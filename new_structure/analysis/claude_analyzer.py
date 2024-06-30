import json
import os
import pandas as pd
import base64
import matplotlib.pyplot as plt
from io import BytesIO
from anthropic import Anthropic
from utils.logger import get_logger
from db.database import save_analysis_result, get_last_analysis_result
from datetime import datetime, timedelta

logger = get_logger()

ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
if not ANTHROPIC_API_KEY:
    logger.error("ANTHROPIC_API_KEY not found in environment variables")
    raise ValueError("ANTHROPIC_API_KEY is not set")

client = Anthropic(api_key=ANTHROPIC_API_KEY)

def get_instructions():
    try:
        with open("enhanced_instructions_claude.md", "r", encoding='utf-8') as file:
            return file.read()
    except FileNotFoundError:
        logger.error("enhanced_instructions_claude.md file not found")
        raise
    except Exception as e:
        logger.error(f"Error reading instructions file: {e}")
        raise

def json_serial(obj):
    if isinstance(obj, (datetime, pd.Timestamp)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")

def serialize_data(data):
    def serialize_item(item):
        if isinstance(item, pd.DataFrame):
            return item.to_dict(orient='records')
        elif isinstance(item, pd.Series):
            return item.to_dict()
        elif isinstance(item, (int, float, str, bool)):
            return item
        elif isinstance(item, (datetime, pd.Timestamp)):
            return item.isoformat()
        else:
            return str(item)
    
    return {key: serialize_item(value) for key, value in data.items()}

def create_chart_image(df):
    try:
        # DataFrame의 열 이름을 소문자로 변경
        df.columns = df.columns.str.lower()

        # 'timestamp' 열이 없으면 인덱스를 사용
        if 'timestamp' not in df.columns:
            df['timestamp'] = df.index

        # 'timestamp' 열을 datetime 형식으로 변환
        df['timestamp'] = pd.to_datetime(df['timestamp'])

        plt.figure(figsize=(10, 6))
        plt.plot(df['timestamp'], df['close'], label='Close Price')
        plt.title('Bitcoin Price Chart')
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.legend()
        
        buffer = BytesIO()
        plt.savefig(buffer, format='png')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        logger.info("Chart image created successfully")
        return image_base64
    except Exception as e:
        logger.error(f"Error creating chart image: {e}")
        return None

def analyze_data(processed_data):
    try:
        instructions = get_instructions()
        logger.info("Instructions loaded successfully")
        
        serialized_data = serialize_data(processed_data)
        serializable_data = json.dumps(serialized_data, default=json_serial)
        logger.info("Data serialized successfully")
        
        # Create chart image
        chart_data = processed_data.get('ohlcv', {}).get('hourly', processed_data.get('chart_data'))
        if isinstance(chart_data, list):
            chart_data = pd.DataFrame(chart_data)
        
        if chart_data is not None and not chart_data.empty:
            chart_image = create_chart_image(chart_data)
            if chart_image:
                logger.info("Chart image created successfully")
            else:
                logger.warning("Failed to create chart image")
        else:
            logger.warning("No valid chart data found")
            chart_image = None
        
        system_message = instructions
        user_message = f"Processed market data: {serializable_data}\n"
        if chart_image:
            user_message += f"Chart image (base64 encoded): {chart_image}\n"
        user_message += "Based on the provided market data and chart image, analyze the situation and provide a trading recommendation."
        
        logger.info("Sending request to Anthropic API using Claude 3.5 Sonnet")
        response = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=1000,
            system=system_message,
            messages=[
                {"role": "user", "content": user_message}
            ]
        )
        logger.info("Received response from Anthropic API")
        
        assistant_message = response.content[0].text
        logger.info(f"Claude's analysis: {assistant_message}")
        
        analysis_result = extract_json_from_text(assistant_message)
        if analysis_result and validate_analysis_result(analysis_result):
            logger.info("Analysis completed successfully")
            logger.info(f"Decision: {analysis_result['decision']}")
            logger.info(f"Reason: {analysis_result['reason']}")
            logger.info(f"Confidence: {analysis_result['confidence']}")
            logger.info(f"Suggested position size: {analysis_result['suggested_position_size']}")
            save_analysis_result(analysis_result)
            return analysis_result
        else:
            logger.warning("Invalid analysis result structure")
            return handle_error("invalid_result")

    except Exception as e:
        logger.error(f"Error in analyze_data: {e}", exc_info=True)
        return handle_error("unknown_error")

def extract_json_from_text(text):
    try:
        start = text.find('{')
        end = text.rfind('}') + 1
        if start != -1 and end != -1:
            json_str = text[start:end]
            json_obj = json.loads(json_str)
            return json_obj
    except json.JSONDecodeError:
        logger.error("Invalid JSON found in the response")
    return None

def validate_analysis_result(result):
    required_keys = ['decision', 'reason', 'confidence', 'suggested_position_size']
    return all(key in result for key in required_keys)

def handle_error(error_type):
    logger.warning(f"Handling error: {error_type}")
    
    last_result = get_last_analysis_result()
    if last_result and (datetime.now() - last_result['timestamp']) < timedelta(hours=1):
        logger.info("Using last valid analysis result")
        return last_result['result']
    
    default_strategy = get_default_strategy(error_type)
    logger.info(f"Using default strategy: {default_strategy}")
    return default_strategy

def get_default_strategy(error_type):
    strategies = {
        "api_error": {"decision": "hold", "reason": "API error, using cautious approach", "confidence": 30, "suggested_position_size": 0},
        "rate_limit": {"decision": "hold", "reason": "Rate limit exceeded, waiting for next cycle", "confidence": 20, "suggested_position_size": 0},
        "network_error": {"decision": "hold", "reason": "Network issues, unable to fetch data", "confidence": 10, "suggested_position_size": 0},
        "unknown_error": {"decision": "hold", "reason": "Unknown error occurred, using safe strategy", "confidence": 5, "suggested_position_size": 0}
    }
    return strategies.get(error_type, strategies["unknown_error"])

if __name__ == "__main__":
    dummy_data = {
        "chart_data": pd.DataFrame({
            "timestamp": [pd.Timestamp("2024-06-30 00:00:00"), pd.Timestamp("2024-06-30 01:00:00")],
            "open": [85000000, 85500000],
            "high": [86000000, 87000000],
            "low": [84000000, 85000000],
            "close": [85500000, 86500000],
            "volume": [100, 120]
        })
    }
    
    result = analyze_data(dummy_data)
    print(json.dumps(result, indent=2))
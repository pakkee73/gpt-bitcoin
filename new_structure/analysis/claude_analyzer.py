import json
import os
import re 
from anthropic import Anthropic
import pandas as pd
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

def serialize_data(data):
    def serialize_item(item):
        if isinstance(item, pd.DataFrame):
            return item.to_dict(orient='records')
        elif isinstance(item, pd.Series):
            return item.to_dict()
        elif isinstance(item, (int, float, str, bool)):
            return item
        else:
            return str(item)
    
    return {key: serialize_item(value) for key, value in data.items()}

def get_default_strategy(error_type):
    strategies = {
        "api_error": {"decision": "hold", "reason": "API error, using cautious approach", "confidence": 30, "suggested_position_size": 0},
        "rate_limit": {"decision": "hold", "reason": "Rate limit exceeded, waiting for next cycle", "confidence": 20, "suggested_position_size": 0},
        "network_error": {"decision": "hold", "reason": "Network issues, unable to fetch data", "confidence": 10, "suggested_position_size": 0},
        "unknown_error": {"decision": "hold", "reason": "Unknown error occurred, using safe strategy", "confidence": 5, "suggested_position_size": 0}
    }
    return strategies.get(error_type, strategies["unknown_error"])

def analyze_data(processed_data, chart_image=None):
    logger.info("Starting data analysis")
    try:
        instructions = get_instructions()
        logger.info("Instructions loaded successfully")
        
        serializable_data = serialize_data(processed_data)
        logger.info("Data serialized successfully")
        
        messages = [
            {
                "role": "user",
                "content": f"{instructions}\nProcessed market data: {json.dumps(serializable_data)}"
            }
        ]
        
        if chart_image:
            messages[0]["content"] += f"\nChart image: {chart_image}"
        
        messages[0]["content"] += "\n\nBased on the provided market data and instructions, analyze the situation and provide a trading recommendation."
        
        logger.info("Sending request to Anthropic API")

        response = client.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=4000,
            messages=messages
        )
        logger.info("Received response from Anthropic API")
        
        # 응답 내용 로깅
        logger.debug(f"Raw API response: {response.content}")
        
        json_str = extract_json_from_text(response.content[0].text)
        if json_str:
            analysis_result = json.loads(json_str)
            logger.info("Analysis completed successfully")
            save_analysis_result(analysis_result)
            return analysis_result
        else:
            logger.warning("No valid JSON found in the response")
            return handle_error("api_error")
        
    except Exception as e:
        logger.error(f"Error in analyze_data: {e}", exc_info=True)
        return handle_error("unknown_error")

def extract_json_from_text(text):
    try:
        # JSON 객체의 시작과 끝을 찾습니다.
        start = text.find('{')
        end = text.rfind('}') + 1
        if start != -1 and end != -1:
            json_str = text[start:end]
            # JSON 문자열을 파싱하여 유효성을 검사합니다.
            json_obj = json.loads(json_str)
            return json.dumps(json_obj)  # 다시 문자열로 변환하여 반환
    except json.JSONDecodeError:
        logger.error("Invalid JSON found in the response")
    return None

def handle_error(error_type):
    logger.warning(f"Handling error: {error_type}")
    
    # 최근 유효한 분석 결과 가져오기
    last_result = get_last_analysis_result()
    if last_result and (datetime.now() - last_result['timestamp']) < timedelta(hours=1):
        logger.info("Using last valid analysis result")
        return last_result['result']
    
    # 기본 전략 사용
    default_strategy = get_default_strategy(error_type)
    logger.info(f"Using default strategy: {default_strategy}")
    return default_strategy

# 추가: 시장 상황에 따른 동적 기본 전략
def get_dynamic_default_strategy(market_data):
    current_price = market_data.get('current_price', 0)
    prev_price = market_data.get('previous_price', 0)
    
    if current_price > prev_price * 1.05:  # 5% 이상 급등
        return {"decision": "sell", "reason": "Significant price increase, potential profit-taking", "confidence": 60, "suggested_position_size": 30}
    elif current_price < prev_price * 0.95:  # 5% 이상 급락
        return {"decision": "buy", "reason": "Significant price decrease, potential buying opportunity", "confidence": 60, "suggested_position_size": 20}
    else:
        return {"decision": "hold", "reason": "No significant price movement", "confidence": 40, "suggested_position_size": 0}


if __name__ == "__main__":
    # 테스트 목적의 더미 데이터
    dummy_data = {
        "price": pd.DataFrame({'close': [100, 101, 102]}),
        "volume": pd.Series([1000, 1100, 1200]),
        "indicator": 0.5
    }
    
    result = analyze_data(dummy_data)
    print(json.dumps(result, indent=2))

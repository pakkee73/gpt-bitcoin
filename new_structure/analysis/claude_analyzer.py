import json
import os
import re 
from anthropic import Anthropic
import pandas as pd
from utils.logger import get_logger
from db.database import save_analysis_result, get_last_analysis_result
from datetime import datetime, timedelta
from tenacity import retry, stop_after_attempt, wait_fixed
from anthropic import Anthropic, HUMAN_PROMPT, AI_PROMPT

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

@retry(stop=stop_after_attempt(3), wait=wait_fixed(2))
def api_request(client, model, messages):
    response = client.messages.create(model=model, max_tokens=4000, messages=messages)
    return response

def validate_analysis_result(result):
    required_keys = ['decision', 'reason', 'confidence', 'suggested_position_size']
    return all(key in result for key in required_keys)

def analyze_data(processed_data, chart_image=None):
    try:
        instructions = get_instructions()
        logger.info("Instructions loaded successfully")
        
        serializable_data = serialize_data(processed_data)
        logger.info("Data serialized successfully")
        
        prompt = f"{HUMAN_PROMPT} {instructions}\nProcessed market data: {json.dumps(serializable_data)}"
        if chart_image:
            prompt += f"\nChart image: {chart_image}"
        prompt += "\n\nBased on the provided market data and instructions, analyze the situation and provide a trading recommendation."
        prompt += f"{AI_PROMPT}"
        
        logger.info("Sending request to Anthropic API")
        response = client.completions.create(
            model="claude-3-sonnet-20240229",
            max_tokens=4000,
            prompt=prompt
        )
        logger.info("Received response from Anthropic API")
        
        logger.debug(f"Raw API response: {response.content}")
        
        json_str = extract_json_from_text(response.content[0].text)
        if json_str:
            analysis_result = json.loads(json_str)
            if validate_analysis_result(analysis_result):
                logger.info("Analysis completed successfully")
                save_analysis_result(analysis_result)
                return analysis_result
            else:
                logger.warning("Invalid analysis result structure")
                return handle_error("invalid_result")
        else:
            logger.warning("No valid JSON found in the response")
            return handle_error("api_error")
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
            return json.dumps(json_obj)
    except json.JSONDecodeError:
        logger.error("Invalid JSON found in the response")
    return None

def handle_error(error_type):
    logger.warning(f"Handling error: {error_type}")
    
    last_result = get_last_analysis_result()
    if last_result and (datetime.now() - last_result['timestamp']) < timedelta(hours=1):
        logger.info("Using last valid analysis result")
        return last_result['result']
    
    default_strategy = get_default_strategy(error_type)
    logger.info(f"Using default strategy: {default_strategy}")
    return default_strategy

def get_dynamic_default_strategy(market_data):
    current_price = market_data.get('current_price', 0)
    prev_price = market_data.get('previous_price', 0)
    
    if current_price > prev_price * 1.05:
        return {"decision": "sell", "reason": "Significant price increase, potential profit-taking", "confidence": 60, "suggested_position_size": 30}
    elif current_price < prev_price * 0.95:
        return {"decision": "buy", "reason": "Significant price decrease, potential buying opportunity", "confidence": 60, "suggested_position_size": 20}
    else:
        return {"decision": "hold", "reason": "No significant price movement", "confidence": 40, "suggested_position_size": 0}

if __name__ == "__main__":
    dummy_data = {
        "price": pd.DataFrame({'close': [100, 101, 102]}),
        "volume": pd.Series([1000, 1100, 1200]),
        "indicator": 0.5
    }
    
    result = analyze_data(dummy_data)
    print(json.dumps(result, indent=2))
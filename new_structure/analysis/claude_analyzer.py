import json
import os
from anthropic import Anthropic
import pandas as pd
from utils.logger import setup_logger

logger = setup_logger()

# 환경 변수에서 API 키를 로드
ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY')
if not ANTHROPIC_API_KEY:
    logger.error("ANTHROPIC_API_KEY not found in environment variables")
    raise ValueError("ANTHROPIC_API_KEY is not set")

anthropic = Anthropic(api_key=ANTHROPIC_API_KEY)

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

    return "Analyze the following processed market data and provide trading recommendations."

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

def analyze_data(processed_data, chart_image=None):
    logger.info("Starting data analysis")
    try:
        instructions = get_instructions()
        logger.info("Instructions loaded successfully")
        
        serializable_data = serialize_data(processed_data)
        logger.info("Data serialized successfully")
        
        prompt = f"\n\nHuman: {instructions}\nProcessed market data: {json.dumps(serializable_data)}"
        if chart_image:
            prompt += f"\nChart image: {chart_image}"
            logger.info("Chart image added to the analysis request")
        
        logger.info("Sending request to Anthropic API")
        response = anthropic.completions.create(
            model="claude-3",
            max_tokens_to_sample=4000,
            prompt=prompt
        )
        logger.info("Received response from Anthropic API")
        
        analysis_result = json.loads(response['completion'])
        logger.info("Analysis completed successfully")

        return analysis_result
    
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding JSON response: {e}")
        return {"decision": "hold", "reason": "Error in parsing analysis result", "confidence": 0, "suggested_position_size": 0}
    except Exception as e:
        logger.error(f"Error in analyze_data: {e}", exc_info=True)
        return {"decision": "hold", "reason": f"Error in analysis: {str(e)}", "confidence": 0, "suggested_position_size": 0}

if __name__ == "__main__":
    # 테스트 목적의 더미 데이터
    dummy_data = {
        "price": pd.DataFrame({'close': [100, 101, 102]}),
        "volume": pd.Series([1000, 1100, 1200]),
        "indicator": 0.5
    }
    
    result = analyze_data(dummy_data)
    print(json.dumps(result, indent=2))

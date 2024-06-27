from anthropic import Anthropic
from config import ANTHROPIC_API_KEY
import json

anthropic = Anthropic(api_key=ANTHROPIC_API_KEY)

def get_instructions():
    with open("enhanced_instructions_claude.md", "r") as file:
        return file.read()

def analyze_data(processed_data):
    instructions = get_instructions()
    
    try:
        response = anthropic.messages.create(
            model="claude-3-sonnet-20240229",
            max_tokens=4000,
            system=instructions,
            messages=[
                {"role": "user", "content": f"Processed market data: {json.dumps(processed_data)}"}
            ]
        )
        return response.content
    except Exception as e:
        print(f"Error in analyze_data: {e}")
        return None
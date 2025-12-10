import os
import json
import time
from groq import Groq
from dotenv import load_dotenv

load_dotenv()


class LLMClient:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY not found in environment variables")
        
        self.client = Groq(api_key=api_key)
        # Groq's fastest and most capable model
        self.model = "llama-3.3-70b-versatile"
        print(f"Using model: {self.model}")
    
    def generate(self, system_prompt: str, user_prompt: str, max_tokens: int = 2000, max_retries: int = 3) -> str:
        """Generate content using Groq with retry logic"""
        
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    max_tokens=max_tokens,
                    temperature=0.7
                )
                return response.choices[0].message.content
            except Exception as e:
                error_str = str(e)
                if "rate" in error_str.lower() or "limit" in error_str.lower() or "429" in error_str:
                    wait_time = (attempt + 1) * 10  # 10s, 20s, 30s
                    print(f"Rate limit hit. Waiting {wait_time}s before retry {attempt + 1}/{max_retries}...")
                    time.sleep(wait_time)
                else:
                    print(f"Error generating content: {e}")
                    raise
        
        raise Exception("Max retries exceeded for rate limiting")
    
    def generate_json(self, system_prompt: str, user_prompt: str, max_tokens: int = 2000, max_retries: int = 3) -> dict:
        """Generate JSON output using Groq with retry logic for JSON parsing"""
        import re
        
        # Add stronger JSON instruction to system prompt
        json_system_prompt = f"""{system_prompt}

CRITICAL INSTRUCTIONS:
1. Respond with ONLY valid JSON
2. Do NOT include any text before or after the JSON
3. Do NOT use markdown code blocks
4. Start your response with [ or {{ and end with ] or }}
5. Use double quotes for all strings
6. Do NOT include newlines within string values"""
        
        for attempt in range(max_retries):
            response = self.generate(json_system_prompt, user_prompt, max_tokens)
            
            # Clean up markdown code blocks if present
            response = response.replace("```json", "").replace("```", "").strip()
            
            # Try to extract JSON from response using regex
            # Look for array [...] or object {...}
            json_match = re.search(r'(\[[\s\S]*\]|\{[\s\S]*\})', response)
            if json_match:
                response = json_match.group(1)
            
            # Clean up common JSON issues
            # Remove control characters except newlines and tabs
            response = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', response)
            
            # Fix unescaped newlines within strings (common LLM issue)
            # This replaces actual newlines between quotes with escaped \n
            def fix_string_newlines(match):
                return match.group(0).replace('\n', '\\n').replace('\r', '\\r')
            
            # Match strings and fix internal newlines
            response = re.sub(r'"[^"]*"', fix_string_newlines, response)
            
            try:
                return json.loads(response)
            except json.JSONDecodeError as e:
                if attempt < max_retries - 1:
                    print(f"JSON parse error (attempt {attempt + 1}/{max_retries}): {e}")
                    print(f"Retrying with fresh LLM call...")
                    time.sleep(2)  # Brief delay before retry
                else:
                    print(f"Failed to parse JSON response after {max_retries} attempts: {response[:500]}...")
                    raise ValueError(f"Invalid JSON from LLM: {e}")


# Singleton instance
llm_client = LLMClient()




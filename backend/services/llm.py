import os
from google import genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Set default model
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

class LLMService:
    def __init__(self):
        # The Client will automatically look for GEMINI_API_KEY in environment
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            print("WARNING: GEMINI_API_KEY not found in environment. Please set it in your .env file.")
        self.client = genai.Client(api_key=self.api_key) if self.api_key else None

    def generate(self, prompt: str, system_instruction: str = None) -> str:
        """
        Generate content using the Gemini model.
        """
        if not self.client:
            # Simple mock response if API key is missing
            return f"[MOCK GENERATION] (Set GEMINI_API_KEY to see actual output)\nPrompt: {prompt[:100]}..."

        try:
            config = {}
            if system_instruction:
                config["system_instruction"] = system_instruction
            
            response = self.client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config=config
            )
            return response.text
        except Exception as e:
            print(f"Error calling Gemini API: {e}")
            return f"Error: Failed to generate content due to API error: {str(e)}"

# Singleton instance
llm_service = LLMService()

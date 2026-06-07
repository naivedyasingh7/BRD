import os

# Set default model placeholder
MODEL_NAME = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

class LLMService:
    """
    LLMService skeleton for other developers to integrate the real AI LLM calls.
    Currently returns mock data.
    """
    def __init__(self):
        # TODO: Initialize Gemini or other LLM Client here
        # Example: self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
        pass

    def generate(self, prompt: str, system_instruction: str = None) -> str:
        """
        Generate content using the LLM model.
        TODO: Implement real LLM API call.
        """
        print(f"[LLMService] Mocking generation for prompt. System instruction: {system_instruction}")
        
        # Simple mock response returned for testing flow
        return f"[MOCK GENERATED BRD CONTENT]\nPrompt snippet: {prompt[:100]}..."

# Singleton instance
llm_service = LLMService()

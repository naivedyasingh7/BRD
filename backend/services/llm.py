import os
import logging
from langchain_groq import ChatGroq

logger = logging.getLogger(__name__)

# Get API key
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

class LLMService:
    """
    Provides a shared LLM instance for all CrewAI agents.
    """
    def __init__(self):
        if not GROQ_API_KEY or GROQ_API_KEY == "your_groq_api_key_here":
            logger.error("GROQ_API_KEY is not set.")
            raise ValueError("GROQ_API_KEY is missing. You must provide a valid Groq API key to use the reasoning engine.")
            
        try:
            self.llm = ChatGroq(
                api_key=GROQ_API_KEY,
                model_name="llama3-70b-8192", 
                temperature=0.2
            )
            logger.info("ChatGroq shared instance initialized successfully.")
        except Exception as e:
            logger.error(f"Failed to initialize ChatGroq: {e}")
            raise RuntimeError(f"Could not initialize the Groq reasoning engine: {str(e)}")

# Singleton — lazy: only raises at call time if key is missing
try:
    llm_service = LLMService()
    shared_groq_llm = llm_service.llm
except ValueError:
    llm_service = None
    shared_groq_llm = None

import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "groq/llama3-70b-8192"


def _make_llm():
    if not GROQ_API_KEY or GROQ_API_KEY == "your_groq_api_key_here":
        logger.error("GROQ_API_KEY is not set.")
        raise ValueError("GROQ_API_KEY is missing. Set it in your .env file.")
    try:
        from crewai import LLM
        llm = LLM(model=GROQ_MODEL, api_key=GROQ_API_KEY, temperature=0.2)
        logger.info("CrewAI LLM instance initialized successfully.")
        return llm
    except Exception as e:
        logger.error(f"Failed to initialize LLM: {e}")
        raise RuntimeError(f"Could not initialize LLM: {str(e)}")


try:
    shared_groq_llm = _make_llm()
except (ValueError, RuntimeError):
    shared_groq_llm = None

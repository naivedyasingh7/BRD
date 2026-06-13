import logging
from backend.services.config import GROQ_API_KEY, is_groq_configured

logger = logging.getLogger(__name__)

GROQ_MODEL = "groq/llama3-70b-8192"


def _make_llm():
    if not is_groq_configured():
        logger.warning("GROQ_API_KEY is not configured. LLM-based services will be unavailable.")
        return None
    try:
        from crewai import LLM
        llm = LLM(model=GROQ_MODEL, api_key=GROQ_API_KEY, temperature=0.2)
        logger.info("CrewAI LLM instance initialized successfully.")
        return llm
    except Exception as e:
        logger.error(f"Failed to initialize LLM: {e}")
        return None


shared_groq_llm = _make_llm()


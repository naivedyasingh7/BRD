import os
import logging
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

# Check if placeholders are used
if GROQ_API_KEY == "your_groq_api_key_here":
    GROQ_API_KEY = None
if SARVAM_API_KEY == "your_sarvam_api_key_here":
    SARVAM_API_KEY = None


def is_groq_configured() -> bool:
    return bool(GROQ_API_KEY)


def is_sarvam_configured() -> bool:
    return bool(SARVAM_API_KEY)


def validate_groq_config():
    if not is_groq_configured():
        logger.error("GROQ_API_KEY is not configured or is a placeholder.")
        raise ValueError("GROQ_API_KEY is missing. Please set it in your .env file.")


def validate_sarvam_config():
    if not is_sarvam_configured():
        logger.error("SARVAM_API_KEY is not configured or is a placeholder.")
        raise ValueError("SARVAM_API_KEY is missing. Please set it in your .env file.")

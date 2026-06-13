import logging
import requests
from typing import Dict
from backend.services.config import SARVAM_API_KEY, is_sarvam_configured

logger = logging.getLogger(__name__)


class TranslationError(Exception):
    pass


class TranslationTimeoutError(TranslationError):
    pass


def map_language_code(lang_name: str) -> str:
    lang_map: Dict[str, str] = {
        "english": "en-IN",
        "hindi": "hi-IN",
        "bengali": "bn-IN",
        "tamil": "ta-IN",
        "telugu": "te-IN",
        "marathi": "mr-IN",
        "gujarati": "gu-IN",
        "kannada": "kn-IN",
        "malayalam": "ml-IN",
        "punjabi": "pa-IN",
        "odia": "or-IN"
    }
    return lang_map.get(lang_name.lower(), "en-IN")


def _translate_chunk(text: str, source_lang: str, target_lang: str) -> str:
    """
    Translates a single text chunk using Sarvam AI Mayura Translation API.
    """
    url = "https://api.sarvam.ai/translate"
    payload = {
        "input": [text],
        "source_language_code": map_language_code(source_lang),
        "target_language_code": map_language_code(target_lang),
        "speaker_gender": "Male",
        "mode": "formal",
        "model": "mayura:v1"
    }
    headers = {
        "api-subscription-key": SARVAM_API_KEY,
        "Content-Type": "application/json"
    }
    
    try:
        logger.info(f"Translating chunk ({len(text)} chars) from {source_lang} to {target_lang}...")
        response = requests.post(url, headers=headers, json=payload, timeout=60)
        
        if response.status_code == 200:
            result = response.json()
            translated_texts = result.get("translated_text", [])
            if translated_texts:
                return translated_texts[0]
            raise TranslationError("Translation API returned an empty response.")
        else:
            logger.error(f"Sarvam translation API returned status code {response.status_code}: {response.text}")
            raise TranslationError(f"Translation failed with status code {response.status_code}.")
            
    except requests.exceptions.Timeout:
        logger.error("Sarvam translate API request timed out.")
        raise TranslationTimeoutError("Translation request timed out.")
    except Exception as e:
        if not isinstance(e, TranslationError):
            logger.error(f"Unexpected translation exception: {type(e).__name__} - {str(e)}")
            raise TranslationError(f"Unexpected error during translation: {str(e)}")
        raise


def translate_text(text: str, source_lang: str, target_lang: str) -> str:
    """
    Translates text. Splits larger texts into chunks under 900 characters
    to prevent API limit bottlenecks.
    """
    if source_lang.lower() == target_lang.lower():
        return text
        
    if not text.strip():
        return text

    if not is_sarvam_configured():
        logger.warning("Sarvam API key is not configured. Returning original text as translation fallback.")
        return text

    # Chunk translation to handle API size limitations
    CHUNK_SIZE = 900
    if len(text) > CHUNK_SIZE:
        chunks = [text[i:i + CHUNK_SIZE] for i in range(0, len(text), CHUNK_SIZE)]
        translated_chunks = []
        for i, chunk in enumerate(chunks):
            try:
                translated_chunks.append(_translate_chunk(chunk, source_lang, target_lang))
            except Exception as e:
                logger.error(f"Failed to translate chunk {i}: {str(e)}")
                translated_chunks.append(f"\n[Translation error on block {i+1}: {str(e)}]\n{chunk}")
        return "".join(translated_chunks)
        
    return _translate_chunk(text, source_lang, target_lang)

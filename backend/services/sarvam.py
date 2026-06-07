import os
import requests
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")

class SarvamService:
    """
    SarvamService handles interactions with Sarvam AI APIs for STT and Translation.
    """
    def __init__(self):
        self.api_key = SARVAM_API_KEY
        if not self.api_key or self.api_key == "your_sarvam_api_key_here":
            logger.error("SARVAM_API_KEY is missing or invalid.")
            raise ValueError("SARVAM_API_KEY is not configured in the environment.")
            
        self.headers = {
            "api-subscription-key": self.api_key
        }

    def speech_to_text_translate(self, audio_file_path: str) -> str:
        """
        Transcribes regional speech from an audio file and translates it to English in one step.
        Uses Sarvam's speech-to-text API.
        """
        url = "https://api.sarvam.ai/speech-to-text-translate"
        try:
            with open(audio_file_path, "rb") as audio_file:
                files = {"file": (os.path.basename(audio_file_path), audio_file, "audio/wav")}
                data = {
                    "prompt": "",
                    "model": "saaras:v1"
                }
                logger.info(f"Sending audio file {os.path.basename(audio_file_path)} to Sarvam STT.")
                response = requests.post(url, headers=self.headers, files=files, data=data, timeout=120)
                
            if response.status_code == 200:
                result = response.json()
                transcript = result.get("transcript", result.get("text", ""))
                if not transcript:
                    logger.warning("Sarvam STT returned empty transcript.")
                    raise ValueError("Speech-to-Text resulted in an empty transcript. Please provide clearer audio.")
                return transcript
            else:
                logger.error(f"Sarvam API Error STT: {response.status_code} - {response.text}")
                raise ConnectionError(f"Sarvam STT API returned error code {response.status_code}")
        except requests.exceptions.Timeout:
            logger.error("Sarvam STT API request timed out.")
            raise TimeoutError("Speech-to-Text processing timed out.")
        except Exception as e:
            logger.error(f"Sarvam STT Exception: {e}")
            raise RuntimeError(f"Error processing audio file: {str(e)}")

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """
        Translates text between English and regional languages using Sarvam API.
        """
        if target_lang.lower() == "english" and source_lang.lower() == "english":
            return text
            
        url = "https://api.sarvam.ai/translate"
        payload = {
            "input": [text],
            "source_language_code": self._map_lang_code(source_lang),
            "target_language_code": self._map_lang_code(target_lang),
            "speaker_gender": "Male",
            "mode": "formal",
            "model": "mayura:v1"
        }
        headers = {
            "api-subscription-key": self.api_key,
            "Content-Type": "application/json"
        }
        try:
            logger.info(f"Sending translation request from {source_lang} to {target_lang}.")
            response = requests.post(url, headers=headers, json=payload, timeout=60)
            if response.status_code == 200:
                result = response.json()
                translated_texts = result.get("translated_text", [])
                if translated_texts:
                    return translated_texts[0]
                raise ValueError("Translation API returned empty list.")
            else:
                logger.error(f"Sarvam API Error Translate: {response.status_code} - {response.text}")
                raise ConnectionError(f"Sarvam Translate API returned error code {response.status_code}")
        except requests.exceptions.Timeout:
            logger.error("Sarvam Translate API request timed out.")
            raise TimeoutError("Translation processing timed out.")
        except Exception as e:
            logger.error(f"Sarvam Translate Exception: {e}")
            raise RuntimeError(f"Error translating text: {str(e)}")

    def _map_lang_code(self, lang_name: str) -> str:
        lang = lang_name.lower()
        lang_map = {
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
        return lang_map.get(lang, "en-IN")

# Singleton — lazy: only raises at call time if key is missing
try:
    sarvam_service = SarvamService()
except ValueError:
    sarvam_service = None

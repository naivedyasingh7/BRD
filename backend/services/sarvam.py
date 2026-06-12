import os
import logging
import requests
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
ALLOWED_AUDIO_EXTENSIONS = {".wav", ".mp3", ".m4a", ".ogg", ".webm"}


class SarvamService:
    def __init__(self):
        self.api_key = SARVAM_API_KEY
        if not self.api_key or self.api_key == "your_sarvam_api_key_here":
            logger.error("SARVAM_API_KEY is missing or invalid.")
            raise ValueError("SARVAM_API_KEY is not configured in the environment.")
        self.headers = {"api-subscription-key": self.api_key}

    def speech_to_text_translate(self, audio_file_path: str) -> str:
        safe_path = os.path.realpath(audio_file_path)
        allowed_base = os.path.realpath(
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "temp_audio")
        )
        if not safe_path.startswith(allowed_base):
            raise ValueError("Invalid audio file path.")

        ext = os.path.splitext(safe_path)[1].lower()
        if ext not in ALLOWED_AUDIO_EXTENSIONS:
            raise ValueError(f"Unsupported audio format: {ext}")

        url = "https://api.sarvam.ai/speech-to-text-translate"
        try:
            with open(safe_path, "rb") as audio_file:
                files = {"file": (os.path.basename(safe_path), audio_file, "audio/wav")}
                data = {"prompt": "", "model": "saaras:v1"}
                logger.info(f"Sending audio file {os.path.basename(safe_path)} to Sarvam STT.")
                response = requests.post(url, headers=self.headers, files=files, data=data, timeout=120)

            if response.status_code == 200:
                result = response.json()
                transcript = result.get("transcript", result.get("text", ""))
                if not transcript:
                    logger.warning("Sarvam STT returned empty transcript.")
                    raise ValueError("Speech-to-Text resulted in an empty transcript. Please provide clearer audio.")
                return transcript
            else:
                logger.error(f"Sarvam API Error STT: {response.status_code}")
                raise ConnectionError(f"Sarvam STT API returned error code {response.status_code}")
        except requests.exceptions.Timeout:
            logger.error("Sarvam STT API request timed out.")
            raise TimeoutError("Speech-to-Text processing timed out.")
        except (ValueError, ConnectionError, TimeoutError):
            raise
        except Exception as e:
            logger.error(f"Sarvam STT Exception: {type(e).__name__}")
            raise RuntimeError(f"Error processing audio file: {type(e).__name__}")

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
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
                logger.error(f"Sarvam API Error Translate: {response.status_code}")
                raise ConnectionError(f"Sarvam Translate API returned error code {response.status_code}")
        except requests.exceptions.Timeout:
            logger.error("Sarvam Translate API request timed out.")
            raise TimeoutError("Translation processing timed out.")
        except (ValueError, ConnectionError, TimeoutError):
            raise
        except Exception as e:
            logger.error(f"Sarvam Translate Exception: {type(e).__name__}")
            raise RuntimeError(f"Error translating text: {type(e).__name__}")

    def _map_lang_code(self, lang_name: str) -> str:
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
        return lang_map.get(lang_name.lower(), "en-IN")


try:
    sarvam_service = SarvamService()
except ValueError:
    sarvam_service = None

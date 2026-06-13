import os
import logging
import requests
from backend.services.config import GROQ_API_KEY, is_groq_configured, is_sarvam_configured

logger = logging.getLogger(__name__)

ALLOWED_AUDIO_EXTENSIONS = {".wav", ".mp3", ".m4a", ".ogg", ".webm", ".flac"}

class AudioProcessingError(Exception):
    pass

class AudioTimeoutError(AudioProcessingError):
    pass

class EmptyTranscriptError(AudioProcessingError):
    pass

def transcribe_audio(file_path: str) -> str:
    
    safe_path = os.path.realpath(file_path)
    ext = os.path.splitext(safe_path)[1].lower()
    if ext not in ALLOWED_AUDIO_EXTENSIONS:
        raise AudioProcessingError(f"Unsupported audio format '{ext}'. Allowed: {', '.join(ALLOWED_AUDIO_EXTENSIONS)}")

    if not os.path.exists(safe_path):
        raise AudioProcessingError("Audio file does not exist on disk.")
    if is_sarvam_configured():
        from backend.services.config import SARVAM_API_KEY
        url = "https://api.sarvam.ai/speech-to-text-translate"
        headers = {"api-subscription-key": SARVAM_API_KEY}
        try:
            with open(safe_path, "rb") as audio_file:
                files = {"file": (os.path.basename(safe_path), audio_file, "audio/wav")}
                data = {"prompt": "", "model": "saaras:v1"}
                logger.info(f"Uploading {os.path.basename(safe_path)} to Sarvam STT API (Indic Support)...")
                
                response = requests.post(url, headers=headers, files=files, data=data, timeout=120)

            if response.status_code == 200:
                result = response.json()
                transcript = result.get("transcript", result.get("text", ""))
                if not transcript:
                    logger.warning("Sarvam STT returned an empty transcript.")
                    raise EmptyTranscriptError("The audio file contains no audible speech.")
                logger.info("Sarvam STT transcription successful.")
                return transcript
            else:
                logger.error(f"Sarvam STT API returned status code {response.status_code}: {response.text}")
                logger.info("Falling back to Groq Whisper...")
        except requests.exceptions.Timeout:
            logger.error("Sarvam STT request timed out. Falling back to Groq Whisper...")
        except Exception as e:
            logger.error(f"Sarvam STT failed: {e}. Falling back to Groq Whisper...")
    if not is_groq_configured():
        raise AudioProcessingError("Neither Sarvam nor Groq services are configured. Please set an API key.")

    url = "https://api.groq.com/openai/v1/audio/transcriptions"
    headers = {"Authorization": f"Bearer {GROQ_API_KEY}"}
    
    try:
        with open(safe_path, "rb") as audio_file:
            files = {"file": (os.path.basename(safe_path), audio_file)}
            data = {"model": "whisper-large-v3", "response_format": "json"}
            logger.info(f"Uploading {os.path.basename(safe_path)} to Groq Whisper STT API...")
            
            response = requests.post(url, headers=headers, files=files, data=data, timeout=120)

        if response.status_code == 200:
            result = response.json()
            transcript = result.get("text", "")
            if not transcript:
                logger.warning("Groq Whisper returned an empty transcript.")
                raise EmptyTranscriptError("The audio file contains no audible speech or transcribable text.")
            logger.info("Groq Whisper transcription successful.")
            return transcript
        else:
            logger.error(f"Groq Whisper API returned status code {response.status_code}: {response.text}")
            raise AudioProcessingError(f"Groq Whisper failed with status code {response.status_code}.")

    except requests.exceptions.Timeout:
        logger.error("Groq STT request timed out.")
        raise AudioTimeoutError("Groq STT request timed out. The audio file might be too large or network is slow.")
    except (AudioProcessingError, EmptyTranscriptError):
        raise
    except Exception as e:
        logger.error(f"Unexpected exception during STT translation: {type(e).__name__} - {str(e)}")
        raise AudioProcessingError(f"Unexpected error processing audio: {str(e)}")

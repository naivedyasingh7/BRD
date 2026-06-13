import logging
from backend.services.config import is_sarvam_configured
from backend.services.audio import transcribe_audio
from backend.services.translation import translate_text

logger = logging.getLogger(__name__)


class SarvamServiceFacade:
    """
    Facade maintaining compatibility with the legacy SarvamService structure.
    Delegates to the modularized services.
    """
    def speech_to_text_translate(self, audio_file_path: str) -> str:
        return transcribe_audio(audio_file_path)

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        return translate_text(text, source_lang=source_lang, target_lang=target_lang)


try:
    if is_sarvam_configured():
        sarvam_service = SarvamServiceFacade()
    else:
        sarvam_service = None
except Exception:
    sarvam_service = None

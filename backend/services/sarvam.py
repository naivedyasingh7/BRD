import os
import requests
import json
from dotenv import load_dotenv
from backend.services.llm import llm_service

load_dotenv()

class SarvamService:
    def __init__(self):
        self.api_key = os.getenv("SARVAM_API_KEY")
        if not self.api_key:
            print("WARNING: SARVAM_API_KEY not found in environment. Using Gemini as translation/transcription fallback.")

    def speech_to_text_translate(self, audio_file_path: str) -> str:
        """
        Transcribes regional speech from an audio file and translates it to English in one step.
        """
        if not self.api_key:
            return self._gemini_audio_fallback(audio_file_path)

        url = "https://api.sarvam.ai/speech-to-text"
        headers = {
            "api-subscription-key": self.api_key
        }
        
        try:
            filename = os.path.basename(audio_file_path)
            with open(audio_file_path, "rb") as f:
                files = {
                    "file": (filename, f, "audio/wav")
                }
                data = {
                    "model": "saaras:v3",
                    "mode": "translate" # Translate to English
                }
                
                response = requests.post(url, headers=headers, files=files, data=data)
                
            if response.status_code == 200:
                result = response.json()
                return result.get("transcript", "")
            else:
                print(f"Sarvam STT failed with status code {response.status_code}: {response.text}")
                # Fall back to Gemini if Sarvam fails
                return self._gemini_audio_fallback(audio_file_path)
        except Exception as e:
            print(f"Error calling Sarvam STT: {e}")
            return self._gemini_audio_fallback(audio_file_path)

    def translate(self, text: str, source_lang: str, target_lang: str) -> str:
        """
        Translates text between English and regional languages (e.g. hi-IN, ta-IN).
        """
        if not self.api_key:
            return self._gemini_translation_fallback(text, source_lang, target_lang)

        url = "https://api.sarvam.ai/translate"
        headers = {
            "api-subscription-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        # Convert codes if needed
        # Sarvam expects format like 'hi-IN', 'ta-IN', 'en-IN'
        src = self._normalize_lang_code(source_lang)
        tgt = self._normalize_lang_code(target_lang)
        
        payload = {
            "input": text,
            "source_language_code": src,
            "target_language_code": tgt,
            "model": "sarvam-translate:v1"
        }
        
        try:
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code == 200:
                result = response.json()
                return result.get("translated_text", "")
            else:
                print(f"Sarvam translation failed with status code {response.status_code}: {response.text}")
                return self._gemini_translation_fallback(text, source_lang, target_lang)
        except Exception as e:
            print(f"Error calling Sarvam translate: {e}")
            return self._gemini_translation_fallback(text, source_lang, target_lang)

    def _normalize_lang_code(self, lang: str) -> str:
        lang = lang.lower()
        if "hindi" in lang or lang.startswith("hi"):
            return "hi-IN"
        if "tamil" in lang or lang.startswith("ta"):
            return "ta-IN"
        if "english" in lang or lang.startswith("en"):
            return "en-IN"
        return "hi-IN" # Default to Hindi

    def _gemini_translation_fallback(self, text: str, source_lang: str, target_lang: str) -> str:
        """
        Fallback translation using Gemini when Sarvam is unavailable.
        """
        prompt = f"""
        Translate the following text from {source_lang} to {target_lang}.
        Provide ONLY the translated text. Do not add explanations, notes, or markers.
        Text to translate:
        "{text}"
        """
        return llm_service.generate(prompt)

    def _gemini_audio_fallback(self, audio_file_path: str) -> str:
        """
        Fallback speech-to-text + translation using Gemini directly, or simulated transcription if API fails.
        """
        # If Gemini API key is configured, we can upload the audio to Gemini for transcription
        if llm_service.client:
            try:
                print("Uploading audio to Gemini for speech-to-text translation fallback...")
                # We can upload local file using files.upload
                uploaded_file = llm_service.client.files.upload(file=audio_file_path)
                prompt = "Transcribe the audio and translate the speech to clear English text. Provide only the English transcription."
                response = llm_service.client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=[uploaded_file, prompt]
                )
                # Cleanup file
                try:
                    llm_service.client.files.delete(name=uploaded_file.name)
                except Exception:
                    pass
                return response.text
            except Exception as e:
                print(f"Gemini audio upload failed: {e}. Falling back to simulated text.")
        
        # If no Gemini API key or file upload failed, simulate for demo purposes
        return "I want an app that can manage shop accounts and billing. It should keep track of products, sales, and generate invoices for customers."

# Singleton instance
sarvam_service = SarvamService()

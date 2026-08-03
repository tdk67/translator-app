from gtts import gTTS
import os
import uuid
import logging
import io

logger = logging.getLogger(__name__)

class TTSAPIError(RuntimeError):
    """Raised when the TTS external API fails."""
    pass

class TTSEngine:
    def __init__(self):
        pass

    def generate_audio(self, text: str, lang: str = 'en', engine: str = 'gTTS') -> bytes:
        """
        Generates audio from text using the specified engine.
        Returns the raw audio bytes.
        """
        if not text:
            raise ValueError("Text cannot be empty for TTS generation.")

        if engine == 'gTTS':
            try:
                tts = gTTS(text=text, lang=lang, slow=False)
                fp = io.BytesIO()
                tts.write_to_fp(fp)
                return fp.getvalue()
            except Exception as e:
                logger.error(f"gTTS API connection failed: {e}")
                raise TTSAPIError(f"Failed to connect to TTS API: {str(e)}") from e
        elif engine == 'Google':
            logger.warning("Google TTS placeholder invoked. Falling back to gTTS for now.")
            return self.generate_audio(text, lang, engine='gTTS')
        else:
            raise ValueError(f"Unsupported TTS engine: {engine}")

    def cleanup(self, filepath: str):
        """
        Deprecated. Cleanup is no longer necessary as audio is kept in memory.
        """
        pass

import io
import logging
import markdown
from bs4 import BeautifulSoup
from gtts import gTTS

logger = logging.getLogger(__name__)


class TTSAPIError(RuntimeError):
    """Raised when the TTS external API fails."""
    pass


class TTSEngine:
    """Text-to-Speech Engine using gTTS with in-memory streaming and text sanitization."""

    def __init__(self):
        pass

    @staticmethod
    def strip_markdown(text: str) -> str:
        """Strips Markdown syntax and HTML tags to prevent speech synthesis reading markdown symbols."""
        if not text:
            return ""
        try:
            html = markdown.markdown(text)
            clean_text = "".join(BeautifulSoup(html, "html.parser").find_all(string=True))
            return clean_text.strip() if clean_text.strip() else text.strip()
        except Exception as e:
            logger.warning(f"Failed to strip markdown: {e}. Falling back to raw text.")
            return text.strip()

    def generate_audio(self, text: str, lang: str = 'en', engine: str = 'gTTS') -> bytes:
        """
        Generates audio from text using the specified engine.
        Returns the raw audio bytes (MP3 format) directly from memory.
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty for TTS generation.")

        # Sanitize text so markdown tags (headers, bullet points, asterisks) are not vocalized
        clean_text = self.strip_markdown(text)
        if not clean_text:
            raise ValueError("Text contains no readable content after sanitization.")

        if engine == 'gTTS':
            try:
                tts = gTTS(text=clean_text, lang=lang, slow=False)
                fp = io.BytesIO()
                tts.write_to_fp(fp)
                return fp.getvalue()
            except Exception as e:
                logger.error(f"gTTS API connection failed: {e}")
                raise TTSAPIError(f"Failed to connect to TTS API: {str(e)}") from e
        else:
            raise ValueError(f"Unsupported TTS engine: {engine}")

from gtts import gTTS
import os
import uuid
import logging

logger = logging.getLogger(__name__)

class TTSEngine:
    def __init__(self, output_dir="temp_audio"):
        self.output_dir = output_dir
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

    def generate_audio(self, text: str, lang: str = 'en', engine: str = 'gTTS') -> str:
        """
        Generates audio from text using the specified engine.
        Returns the path to the generated audio file.
        """
        if not text:
            raise ValueError("Text cannot be empty for TTS generation.")

        filename = f"{uuid.uuid4()}.mp3"
        filepath = os.path.join(self.output_dir, filename)

        if engine == 'gTTS':
            try:
                tts = gTTS(text=text, lang=lang, slow=False)
                tts.save(filepath)
                return filepath
            except Exception as e:
                logger.error(f"gTTS generation failed: {e}")
                raise e
        elif engine == 'Google':
            logger.warning("Google TTS placeholder invoked. Falling back to gTTS for now.")
            return self.generate_audio(text, lang, engine='gTTS')
        else:
            raise ValueError(f"Unsupported TTS engine: {engine}")

    def cleanup(self, filepath: str):
        """
        Utility to clean up generated audio files.
        """
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
            except Exception as e:
                logger.error(f"Failed to remove {filepath}: {e}")

from google import genai
from google.genai import types
import json
import logging
import io

logger = logging.getLogger(__name__)

class GeminiClient:
    def __init__(self, api_key: str = None, model_name: str = 'gemini-3.5-flash'):
        if api_key:
            self.client = genai.Client(api_key=api_key)
        else:
            self.client = None
        self.model_name = model_name

    def translate_text(self, text: str, target_language: str) -> dict:
        """
        Translates text to the target language and detects the source language.
        Implements guardrails to prevent malicious prompts.
        """
        if self._is_malicious(text):
            return {
                "detected_language": "Unknown",
                "translation": "Error: Input flagged for malicious content or prompt injection."
            }

        prompt = f"""
        You are a highly capable translation assistant. 
        Detect the language of the following text and translate it into {target_language}.
        Return ONLY a JSON object with two keys: "detected_language" and "translation".
        Do not include markdown blocks or any other text.
        
        Text to translate:
        {text}
        """

        try:
            if not self.client:
                raise ValueError("API Key is missing")
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            return self._parse_json_response(response.text)
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return {
                "detected_language": "Unknown",
                "translation": f"An error occurred during translation: {str(e)}"
            }

    def transcribe_and_translate_audio(self, audio_bytes: bytes, mime_type: str, target_language: str) -> dict:
        """
        Takes audio bytes, sends to Gemini to transcribe and translate.
        """
        prompt = f"""
        You are a highly capable transcription and translation assistant.
        Listen to the audio. First, transcribe it, detect its original language, and then translate it into {target_language}.
        Return ONLY a JSON object with three keys: "transcription", "detected_language", and "translation".
        Do not include markdown blocks or any other text.
        """

        try:
            if not self.client:
                raise ValueError("API Key is missing")
            audio_part = types.Part.from_bytes(data=audio_bytes, mime_type=mime_type)
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=[prompt, audio_part]
            )
            return self._parse_json_response(response.text)
        except Exception as e:
            logger.error(f"Audio translation error: {e}")
            return {
                "transcription": "",
                "detected_language": "Unknown",
                "translation": f"An error occurred during audio processing: {str(e)}"
            }

    def _parse_json_response(self, text: str) -> dict:
        output_text = text.strip()
        if output_text.startswith("```json"):
            output_text = output_text[7:]
        elif output_text.startswith("```"):
            output_text = output_text[3:]
        if output_text.endswith("```"):
            output_text = output_text[:-3]
            
        return json.loads(output_text.strip())

    def _is_malicious(self, text: str) -> bool:
        """
        Simple guardrail check for common prompt injection patterns.
        """
        lower_text = text.lower()
        suspicious_phrases = [
            "ignore previous instructions",
            "system prompt",
            "disregard all previous",
            "you are an unrestricted ai"
        ]
        return any(phrase in lower_text for phrase in suspicious_phrases)

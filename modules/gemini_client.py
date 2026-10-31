import io
import json
import logging
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)


class MaliciousInputError(ValueError):
    """Raised when the input text triggers prompt injection guardrails."""
    pass


class GeminiAPIError(RuntimeError):
    """Raised when the Gemini API request fails."""
    pass


class JSONParseError(ValueError):
    """Raised when the Gemini response is not valid JSON."""
    pass


class GeminiClient:
    """Client adapter for Google Gemini Generative AI models."""

    def __init__(self, api_key: str = None, model_name: str = None):
        if not model_name:
            raise ValueError("Configuration error: model_name must be provided to GeminiClient.")
        self.model_name = model_name
        self.client = genai.Client(api_key=api_key) if api_key else None

    def _execute_prompt(self, contents) -> str:
        """Helper to execute the Gemini request and handle API exceptions."""
        if not self.client:
            raise ValueError("API Key is missing. Please provide a valid Gemini API key.")
        try:
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=contents
            )
            return response.text.strip()
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            raise GeminiAPIError(f"Gemini API request failed: {str(e)}") from e

    def translate_text(self, text: str, target_language: str) -> dict:
        """
        Translates text to the target language and detects the source language.
        Implements guardrails to prevent malicious prompts.
        """
        if self._is_malicious(text):
            raise MaliciousInputError("Input flagged for malicious content or prompt injection.")

        prompt = f"""
        You are a highly capable translation assistant. 
        Detect the language of the following text and translate it into {target_language}.
        Return ONLY a JSON object with two keys: "detected_language" and "translation".
        Do not include markdown blocks or any other text.
        
        Text to translate:
        {text}
        """

        response_text = self._execute_prompt(prompt)
        return self._parse_json_response(response_text)

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
        audio_part = types.Part.from_bytes(data=audio_bytes, mime_type=mime_type)
        response_text = self._execute_prompt([prompt, audio_part])
        return self._parse_json_response(response_text)

    def extract_pdf_markdown(self, pdf_bytes: bytes) -> str:
        """
        Takes PDF bytes and extracts text as Markdown preserving formatting.
        """
        prompt = """
        Extract all text from this document and output it as Markdown, preserving the original formatting (headers, lists, bold text, tables, etc.) exactly. 
        Do not add any extra conversational text. If the document has a specific visual structure, represent it as best as you can in Markdown.
        """
        pdf_part = types.Part.from_bytes(data=pdf_bytes, mime_type="application/pdf")
        return self._execute_prompt([prompt, pdf_part])

    def _parse_json_response(self, text: str) -> dict:
        output_text = text.strip()
        if output_text.startswith("```json"):
            output_text = output_text[7:]
        elif output_text.startswith("```"):
            output_text = output_text[3:]
        if output_text.endswith("```"):
            output_text = output_text[:-3]

        try:
            return json.loads(output_text.strip())
        except json.JSONDecodeError as e:
            logger.error(f"JSON Decode Error: {e} | Text: {text}")
            raise JSONParseError(f"Failed to parse JSON response from LLM: {str(e)}") from e

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

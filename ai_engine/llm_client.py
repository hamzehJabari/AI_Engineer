"""
LLM Client for IntelliWheels - uses Google Gemini (new google-genai SDK).
"""
import os
import logging
from typing import List, Dict
from django.conf import settings

logger = logging.getLogger(__name__)


class GeminiClient:
    """Client for Google Gemini API using the new google-genai SDK."""

    def __init__(self, model=None, vision_model=None):
        self.api_key = getattr(settings, 'GEMINI_API_KEY', '') or os.getenv('GEMINI_API_KEY', '')
        # Model switch logic
        model_switch = getattr(settings, 'GEMINI_MODEL_SWITCH', None) or os.getenv('GEMINI_MODEL_SWITCH', '2.0')
        if model_switch == '2.5':
            self.model_name = model or 'gemini-2.5-flash'
            self.vision_model_name = vision_model or 'gemini-2.5-flash'
        else:
            self.model_name = model or 'gemini-2.0-flash'
            self.vision_model_name = vision_model or 'gemini-2.0-flash'
        self._client = None

        if self.api_key:
            try:
                from google import genai
                self._client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.error(f"Failed to configure Gemini: {e}")
        else:
            logger.warning("GEMINI_API_KEY not configured - using mock responses")

    def chat(self, messages: List[Dict[str, str]], system_prompt: str = None) -> Dict:
        """
        Send a chat request to Gemini.

        Args:
            messages: list of {"role": "user"/"assistant", "content": "..."}
            system_prompt: optional system instruction

        Returns:
            dict with "response" and "model_used"
        """
        if not self._client:
            return self._mock_response(messages)

        try:
            from google.genai import types

            # Build config with system instruction and disable thinking for speed
            config = None
            if system_prompt:
                config = types.GenerateContentConfig(
                    system_instruction=system_prompt,
                    thinking_config=types.ThinkingConfig(thinking_budget=0),
                )
            else:
                config = types.GenerateContentConfig(
                    thinking_config=types.ThinkingConfig(thinking_budget=0),
                )

            # Build contents list for multi-turn conversation
            contents = []
            for msg in messages:
                role = "user" if msg["role"] == "user" else "model"
                contents.append(types.Content(
                    role=role,
                    parts=[types.Part.from_text(text=msg["content"])],
                ))

            response = self._client.models.generate_content(
                model=self.model_name,
                contents=contents,
                config=config,
            )

            return {
                "response": response.text,
                "model_used": self.model_name,
            }

        except Exception as e:
            logger.error(f"Gemini chat error: {e}")
            error_msg = str(e)
            if "429" in error_msg or "RESOURCE_EXHAUSTED" in error_msg:
                return {
                    "response": "I'm currently rate-limited. Please wait a moment and try again.",
                    "model_used": "rate_limited",
                }
            return {
                "response": f"I encountered an error: {error_msg}",
                "model_used": "error",
            }

    def analyze_image(self, image_bytes: bytes, prompt: str) -> Dict:
        """
        Analyze an image with Gemini Vision.

        Args:
            image_bytes: raw image bytes
            prompt: the analysis prompt

        Returns:
            dict with "response" and "model_used"
        """
        if not self._client:
            return self._mock_vision_response()

        try:
            from google.genai import types

            image_part = types.Part.from_bytes(
                data=image_bytes,
                mime_type="image/jpeg",
            )
            text_part = types.Part.from_text(text=prompt)

            response = self._client.models.generate_content(
                model=self.vision_model_name,
                contents=[text_part, image_part],
            )

            return {
                "response": response.text,
                "model_used": self.vision_model_name,
            }

        except Exception as e:
            logger.error(f"Gemini vision error: {e}")
            return {
                "response": f"Vision analysis error: {str(e)}",
                "model_used": "error",
            }

    def _mock_response(self, messages: List[Dict]) -> Dict:
        last = messages[-1]["content"] if messages else ""
        return {
            "response": (
                "I am IntelliWheels AI (running in mock mode).\n\n"
                f"You asked: \"{last[:120]}...\"\n\n"
                "To get real AI responses, set GEMINI_API_KEY in your .env file and restart the server."
            ),
            "model_used": "mock",
        }

    def _mock_vision_response(self) -> Dict:
        return {
            "response": '{"make": "Unknown", "model": "Unknown", "year": "Unknown", '
                        '"condition": "Vision analysis requires a valid GEMINI_API_KEY."}',
            "model_used": "mock",
        }


# Singleton
_gemini_client = None


def get_gemini_client() -> GeminiClient:
    global _gemini_client
    if _gemini_client is None:
        _gemini_client = GeminiClient()
    return _gemini_client

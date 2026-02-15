"""
Vision Helper — uses Gemini Vision to analyze car images.

Given an uploaded image, the AI identifies:
  - Make
  - Model
  - Approximate year
  - Brief condition / status description
"""
import json
import logging
from ai_engine.llm_client import get_gemini_client

logger = logging.getLogger(__name__)

VISION_PROMPT = """You are an expert automotive analyst. 
Analyze this car image and provide the following information in EXACTLY this JSON format:
{
    "make": "the car manufacturer",
    "model": "the specific model name",
    "year": "approximate year or year range",
    "condition": "a brief 2-3 sentence description of the car's visible condition, color, body style, and any notable features or damage you can see"
}

If you cannot determine a field, use "Unknown" as the value.
Return ONLY the JSON object, no extra text."""


def analyze_car_image(image_bytes: bytes) -> dict:
    """
    Analyze a car image using Gemini Vision.

    Args:
        image_bytes: Raw bytes of the uploaded image.

    Returns:
        dict with keys: make, model, year, condition, raw_response
    """
    client = get_gemini_client()

    result = client.analyze_image(image_bytes, VISION_PROMPT)
    raw = result.get("response", "")

    # Try to parse structured JSON from the response
    parsed = _parse_vision_response(raw)
    parsed["raw_response"] = raw
    return parsed


def _parse_vision_response(text: str) -> dict:
    """Attempt to extract structured data from the Gemini response."""
    defaults = {
        "make": "Unknown",
        "model": "Unknown",
        "year": "Unknown",
        "condition": text,  # fallback: use the whole response text
    }

    # Try parsing as JSON
    try:
        # Strip markdown code fences if present
        cleaned = text.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("\n", 1)[-1]
            cleaned = cleaned.rsplit("```", 1)[0]
        data = json.loads(cleaned)
        return {
            "make": data.get("make", "Unknown"),
            "model": data.get("model", "Unknown"),
            "year": str(data.get("year", "Unknown")),
            "condition": data.get("condition", "No condition info"),
        }
    except (json.JSONDecodeError, AttributeError):
        logger.warning("Could not parse vision response as JSON, using raw text")
        return defaults

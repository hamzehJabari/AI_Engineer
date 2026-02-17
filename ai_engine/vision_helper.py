"""
Vision Helper — uses Gemini Vision to analyze car images.

This module provides both:
1. analyze_car_image() (original) — direct Gemini Vision SDK for fast analysis
2. analyze_car_image_crew() — CrewAI-based multi-agent vision analysis

Given an uploaded image, the AI identifies:
  - Make
  - Model
  - Approximate year
  - Brief condition / status description
"""
import json
import logging
from ai_engine.llm_client import get_gemini_client
from ai_engine.prompts import load_prompt

logger = logging.getLogger(__name__)

# Load prompt from external .md file (separated prompt engineering)
VISION_PROMPT = load_prompt('vision_analysis.md')


def analyze_car_image(image_bytes: bytes) -> dict:
    """
    Analyze a car image using direct Gemini Vision SDK (fast path).

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


def analyze_car_image_crew(image_bytes: bytes) -> dict:
    """
    Analyze a car image using CrewAI Vision Agent (multi-agent path).

    First gets a raw description from Gemini Vision, then passes it
    through the VisionAnalysisCrew agent for structured extraction.

    Args:
        image_bytes: Raw bytes of the uploaded image.

    Returns:
        dict with keys: make, model, year, condition, raw_response
    """
    from ai_engine.crews import VisionAnalysisCrew

    try:
        # Step 1: Get raw image description from Gemini Vision
        client = get_gemini_client()
        vision_result = client.analyze_image(
            image_bytes,
            "Describe this car image in detail: make, model, year, color, "
            "condition, body style, and any notable features or damage."
        )
        raw_description = vision_result.get("response", "")

        # Step 2: Pass through CrewAI Vision Agent for structured extraction
        result = (
            VisionAnalysisCrew()
            .crew()
            .kickoff(inputs={
                "image_description": raw_description,
            })
        )

        parsed = _parse_vision_response(result.raw)
        parsed["raw_response"] = raw_description
        return parsed

    except Exception as e:
        logger.error(f"CrewAI vision error: {e}, falling back to direct analysis")
        return analyze_car_image(image_bytes)


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

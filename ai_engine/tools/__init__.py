"""
LLM configuration for IntelliWheels — central model definitions.

Following the course pattern (core/tools/main_llm.py in agents_htu),
this file defines the shared LLM instances used by all crews and agents.
"""
from django.conf import settings
from crewai import LLM

# Primary LLM for chat agents (Gemini via litellm)
gemini_llm = LLM(
    model=f"gemini/{settings.GEMINI_MODEL}",
    api_key=settings.GEMINI_API_KEY,
    temperature=0.7,
)

# Vision-capable LLM for image analysis agents
gemini_vision_llm = LLM(
    model=f"gemini/{settings.GEMINI_VISION_MODEL}",
    api_key=settings.GEMINI_API_KEY,
    temperature=0.3,
)

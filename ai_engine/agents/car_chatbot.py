"""
Car Chatbot Agent — the main conversational AI for IntelliWheels.

This module provides both:
1. CarChatbotAgent (original) — direct Gemini SDK calls for fast responses
2. CrewAI integration — via CarChatCrew for multi-agent orchestration

The view layer uses CarChatbotAgent for low-latency chat, while the
CrewAI crews are available for more complex multi-agent workflows.
"""
import logging
from ai_engine.llm_client import get_gemini_client
from ai_engine.prompts import load_prompt

logger = logging.getLogger(__name__)

# Load system prompt from external .md file (separated prompt engineering)
SYSTEM_PROMPT = load_prompt('car_chatbot_system.md')


class CarChatbotAgent:
    """Conversational agent for car-related queries (direct Gemini SDK)."""

    def __init__(self):
        self.client = get_gemini_client()

    def chat(self, message: str, history: list = None) -> dict:
        """
        Process a user message and return an AI response.

        Args:
            message:  The user's latest message.
            history:  List of prior {"role": ..., "content": ...} dicts.

        Returns:
            dict with "response" and "model_used" keys.
        """
        messages = []
        if history:
            messages.extend(history)
        messages.append({"role": "user", "content": message})

        result = self.client.chat(messages, system_prompt=SYSTEM_PROMPT)
        return result


class CarChatbotCrewAgent:
    """Conversational agent using CrewAI multi-agent orchestration."""

    def chat(self, message: str, history: list = None) -> dict:
        """
        Process a user message via the CarChatCrew (CrewAI).

        Args:
            message:  The user's latest message.
            history:  List of prior {"role": ..., "content": ...} dicts.

        Returns:
            dict with "response" and "model_used" keys.
        """
        from ai_engine.crews import CarChatCrew

        # Format history as readable text for the crew
        history_text = ""
        if history:
            for msg in history:
                role = msg.get("role", "user").capitalize()
                content = msg.get("content", "")
                history_text += f"{role}: {content}\n"

        try:
            result = (
                CarChatCrew()
                .crew()
                .kickoff(inputs={
                    "user_message": message,
                    "conversation_history": history_text or "No previous conversation.",
                })
            )
            return {
                "response": result.raw,
                "model_used": "crewai-car-advisor",
            }
        except Exception as e:
            logger.error(f"CrewAI chat error: {e}")
            # Fallback to direct Gemini
            logger.info("Falling back to direct Gemini SDK")
            direct_agent = CarChatbotAgent()
            return direct_agent.chat(message, history)


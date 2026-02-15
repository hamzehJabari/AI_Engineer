"""
Car Chatbot Agent — the main conversational AI for IntelliWheels.
Uses Gemini to answer questions about cars, the Jordanian market, etc.
"""
import logging
from ai_engine.llm_client import get_gemini_client

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are IntelliWheels AI, a friendly and knowledgeable car marketplace assistant
specializing in the Jordanian car market.

Your capabilities:
1. Answer questions about cars — specs, comparisons, recommendations.
2. Help users find the right car for their budget and needs in Jordan.
3. Explain car categories (Luxury, Premium, Economic) in the Jordanian context.
4. Give general price guidance (but remind users to use the Price Estimator for accurate numbers).
5. Advise on common car issues, maintenance tips, and import considerations in Jordan.

Guidelines:
- Be concise and helpful. Use bullet points when listing info.
- Prices should be in JOD (Jordanian Dinar).
- If asked about something outside the car domain, politely redirect.
- Be friendly and use a conversational tone.
"""


class CarChatbotAgent:
    """Conversational agent for car-related queries."""

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

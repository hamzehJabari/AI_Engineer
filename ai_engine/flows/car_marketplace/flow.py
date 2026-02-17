"""
Car Marketplace Flow — orchestrates the car chat and vision agents.

Following the course pattern (agents_htu flows), this flow uses:
- @start() to classify the request type
- @router() to decide which crew(s) to invoke
- @listen() to run the appropriate crew
- or_() to merge results from different paths

This demonstrates multi-agent orchestration: the chat agent and vision agent
can work independently or together depending on the user's request.
"""
import json
import logging

from crewai.flow import Flow, listen, start, router, or_

from ai_engine.crews import CarChatCrew, VisionAnalysisCrew
from .schema import CarMarketplaceState

logger = logging.getLogger(__name__)


class CarMarketplaceFlow(Flow[CarMarketplaceState]):
    """
    Orchestration flow for IntelliWheels.

    Routes requests to the appropriate AI agent crew:
    - chat → CarChatCrew (car advisor agent)
    - vision → VisionAnalysisCrew (vision analyst agent)
    """

    @start()
    def classify_request(self):
        """Determine which agent(s) to invoke based on available inputs."""
        has_message = bool(self.state.user_message.strip())
        has_image = self.state.image_bytes is not None

        if has_message and has_image:
            self.state.request_type = "chat_and_vision"
        elif has_image:
            self.state.request_type = "vision"
        else:
            self.state.request_type = "chat"

        logger.info(f"Flow classified request as: {self.state.request_type}")
        return self.state.request_type

    @router(classify_request)
    def route_to_crew(self):
        """Route to the appropriate crew based on request type."""
        return self.state.request_type

    @listen("chat")
    def run_chat_crew(self):
        """Run the car advisor agent for text-based queries."""
        try:
            result = (
                CarChatCrew()
                .crew()
                .kickoff(inputs={
                    "user_message": self.state.user_message,
                    "conversation_history": self.state.conversation_history,
                })
            )
            self.state.chat_output = {
                "response": result.raw,
                "model_used": "crewai-car-advisor",
            }
        except Exception as e:
            logger.error(f"Chat crew error: {e}")
            self.state.chat_output = {
                "response": f"Sorry, I encountered an error: {str(e)}",
                "model_used": "error",
            }

    @listen("vision")
    def run_vision_crew(self):
        """Run the vision analyst agent for image analysis."""
        try:
            # For CrewAI, we pass the image context as text description
            # The actual image analysis is done by the Gemini Vision LLM
            from ai_engine.llm_client import get_gemini_client

            client = get_gemini_client()
            vision_result = client.analyze_image(
                self.state.image_bytes,
                "Describe this car image in detail: make, model, year, color, condition, body style, and any notable features or damage."
            )

            # Now let the vision crew agent refine and structure the output
            result = (
                VisionAnalysisCrew()
                .crew()
                .kickoff(inputs={
                    "image_description": vision_result.get("response", "No description available"),
                })
            )

            # Parse the structured JSON from the crew output
            parsed = self._parse_vision_json(result.raw)
            parsed["raw_response"] = vision_result.get("response", "")
            self.state.vision_output = parsed

        except Exception as e:
            logger.error(f"Vision crew error: {e}")
            self.state.vision_output = {
                "make": "Unknown",
                "model": "Unknown",
                "year": "Unknown",
                "condition": f"Analysis failed: {str(e)}",
                "raw_response": "",
            }

    @listen("chat_and_vision")
    def run_both_crews(self):
        """Run both chat and vision crews when user sends message + image."""
        self.run_vision_crew()
        self.run_chat_crew()

    @listen(or_(run_chat_crew, run_vision_crew, run_both_crews))
    def assemble_final_output(self):
        """Merge outputs from all crews into the final result."""
        final = {}

        if self.state.chat_output:
            final["chat"] = self.state.chat_output

        if self.state.vision_output:
            final["vision"] = self.state.vision_output

        self.state.final_output = final
        return final

    @staticmethod
    def _parse_vision_json(text: str) -> dict:
        """Parse structured JSON from the vision crew output."""
        defaults = {
            "make": "Unknown",
            "model": "Unknown",
            "year": "Unknown",
            "condition": text,
        }
        try:
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
            logger.warning("Could not parse vision crew output as JSON")
            return defaults

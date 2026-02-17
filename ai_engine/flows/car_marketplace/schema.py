"""
Pydantic state schema for the Car Marketplace flow.
"""
from pydantic import BaseModel
from typing import Dict, Optional


class CarMarketplaceState(BaseModel):
    """State shared across all steps in the car marketplace flow."""
    # Input
    user_message: str = ""
    conversation_history: str = ""
    image_bytes: Optional[bytes] = None

    # Routing
    request_type: str = ""  # "chat", "vision", or "chat_and_vision"

    # Outputs
    chat_output: Optional[Dict] = None
    vision_output: Optional[Dict] = None
    final_output: Dict = {}

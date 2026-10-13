from pydantic import BaseModel
from typing import Any, Optional

from session_phases import SessionPhase
from message_types import MessageType

class MessageModel(BaseModel):
    phase: SessionPhase
    round_idx: int
    msg_type: MessageType
    payload: dict = {}
    error: Optional[str] = None
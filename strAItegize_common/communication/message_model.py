from pydantic import BaseModel
from typing import Optional

from message_types import MessageType

class MessageModel(BaseModel):
    phase: int
    round_idx: int
    msg_type: MessageType
    payload: dict = {}
    error: Optional[str] = None
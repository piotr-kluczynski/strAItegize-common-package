from typing import Callable, Dict, Any
from pydantic import ValidationError

class CommandDispatcher:
    def __init__(self):
        self._handlers: Dict[str, Callable] = {}

    def register(self, message_type: str):
        def decorator(func: Callable):
            self._handlers[message_type] = func
            return func

        return decorator

    def dispatch(self, message: dict, sim_context: Any) -> dict:
        message_type = message.get("type")
        payload = message.get("payload", {})

        handler = self._handlers.get(message_type)
        if not handler:
            return {
                "type": "ERROR",
                "payload": {"desc": f"UNKNOWN_MESSAGE_TYPE: {message_type}"}
            }

        try:
            response_payload = handler(payload, sim_context)

            return {
                "type": "RESPONSE",
                "payload": response_payload
            }
        except ValidationError as e:
            return {
                "type": "ERROR",
                "payload": { 
                    "desc": "INVALID_INPUT_SCHEMA", 
                    "details": e.errors()
                }
            }
        except Exception as e:
            return {
                "type": "ERROR",
                "payload": {
                    "desc": f"INTERNAL_ERROR: {str(e)}"
                }
            }
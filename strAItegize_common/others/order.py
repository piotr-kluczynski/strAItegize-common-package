from pydantic import BaseModel, Field
from typing import Literal, Optional

class Order(BaseModel):
    """
    Data class defining an order given to unit identified by given unit_id.
    """
    order_type: Literal["move", "hold", "attack", "support"] = Field(
        description="The category of the order given to the unit."
    )

    unit_id: str = Field(
        description="Identifier of the unit the order is assigned to."
    )

    target_id: Optional[str] = Field(
        description="Identifier of the unit targeted by the order (applicable only in case of attack, or support order).",
        default=None
    )

    move_q: Optional[int] = Field(
        description="The movement vector of q axis in cubic coordinate system (applicable only in case of movement order).",
        default=None
    )
    move_r: Optional[int] = Field(
        description="The movement vector of r axis in cubic coordinate system (applicable only in case of movement order).",
        default=None
    )
    move_s: Optional[int] = Field(
        description="The movement vector of s axis in cubic coordinate system (applicable only in case of movement order).",
        default=None
    )

def describe_order(order: Order) -> str:
    if order.order_type == "move":
        return (
            f"move "
            f"(unit_id: {order.unit_id}; "
            f"move_vector: {order.move_q}, {order.move_r}, {order.move_s})"
        )

    elif order.order_type == "attack":
        return (
            f"attack "
            f"(unit_id: {order.unit_id}; "
            f"target_unit: {order.target_id})"
        )

    elif order.order_type == "support":
        return (
            f"support "
            f"(unit_id: {order.unit_id}; "
            f"target_unit: {order.target_id})"
        )

    elif order.order_type == "hold":
        return f"hold (unit_id: {order.unit_id})"

    else:
        raise ValueError(f"Unknown order type: {order.order_type}")
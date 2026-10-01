from pydantic import BaseModel, Field
from typing import Literal, Optional

class Order(BaseModel):
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
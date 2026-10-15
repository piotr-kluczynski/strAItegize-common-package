from pydantic import BaseModel, Field
from typing import Literal

class RecruitmentChoice(BaseModel):
    """
    Data class, specifying information that needs to be provided in order for the simulation
    to recruit new units for a player.
    """
    unit_type: Literal["light_infantry", "heavy_infantry", "cavalry"] = Field(
        description="Type of unit to recruit in the chosen region."
    )
    region: str = Field(
        description="The name of the region where recruitment will proceed."
    )

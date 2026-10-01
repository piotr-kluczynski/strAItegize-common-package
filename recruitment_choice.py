from pydantic import BaseModel
from typing import Literal
from pydantic import Field

class RecruitmentChoice(BaseModel):
    unit_type: Literal["light_infantry", "heavy_infantry", "cavalry"] = Field(
        description="Type of unit to recruit in the chosen region."
    )
    region: str = Field(
        description="The name of the region where recruitment will proceed."
    )
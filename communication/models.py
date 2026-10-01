from pydantic import BaseModel, Field
from typing import Dict, List, Any

from others.order import Order

# Observation Model
class TileObservation(BaseModel):
    rel_coord: str
    distance: int
    unit: str
    owner: str
    region: str
    is_command_center: bool


# Base Message Wrapper
class NetworkMessage(BaseModel):
    message_type: str
    payload: Dict[str, Any] = Field(default_factory=dict)

# Requests
class ObserveUnitRequest(BaseModel):
    unit_id: str

class ObserveRegionRequest(BaseModel):
    region_id: str

class GetUnitsRequest(BaseModel):
    pass

class GetRegionsRequest(BaseModel):
    pass

class GetPlayersRequest(BaseModel):
    pass

class GetUnitDetailsRequest(BaseModel):
    unit_id: str

class GetRegionDetailsRequest(BaseModel):
    region_id: str

class IssueOrdersReuqest(BaseModel):
    orders: List[Order]

class MessagePlayerRequest(BaseModel):
    pass

class GetPlayerConversationRequest(BaseModel):
    pass

# Responses
class ObserveUnitResponse(BaseModel):
    observations: Dict[str, TileObservation]

class ObserveRegionResponse(BaseModel):
    observations: Dict[str, TileObservation]

class GetUnitsResponse(BaseModel):
    units_list: List[str]

class GetRegionsResponse(BaseModel):
    regions_list: List[str]

class GetUnitDetailsResponse(BaseModel):
    unit_id: str
    owner: str
    coord: str
    movement: int
    upkeep: int
    strength: int

class GetRegionDetailsResponse(BaseModel):
    region_id: str
    owner: str
    command_center_coord: str
    region_upkeep: int
    size: int
    neighbour_regions: List[str]

class GetPlayersResponse(BaseModel):
    players_list: List[str]

class IssueOrdersResponse(BaseModel):
    pass

class MessagePlayerResponse(BaseModel):
    pass

class GetPlayerConversationResponse(BaseModel):
    pass

class ErrorResponse(BaseModel):
    desc: str
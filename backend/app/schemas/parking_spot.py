from pydantic import BaseModel, ConfigDict
from typing import Optional, List


class ParkingSpotBase(BaseModel):
    spot_number: Optional[str] = None
    x: Optional[int] = None
    y: Optional[int] = None
    width: Optional[int] = None
    height: Optional[int] = None
    polygon: Optional[List[List[float]]] = None


class ParkingSpotCreate(ParkingSpotBase):
    pass


class ParkingSpotRead(ParkingSpotBase):
    id: int

    model_config = ConfigDict(from_attributes=True)

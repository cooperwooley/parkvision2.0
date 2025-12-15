from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class ParkingLotBase(BaseModel):
    name: str
    address: Optional[str] = None
    total_spaces: int
    description: Optional[str] = None
    init_frame_path: Optional[str] = None
    video_path: Optional[str] = None
    video_start_time: Optional[float] = None

class ParkingLotCreate(ParkingLotBase):
    pass

class ParkingLotUpdate(BaseModel):
    name: Optional[str] = None
    address: Optional[str] = None
    total_spaces: Optional[int] = None
    description: Optional[str] = None
    init_frame_path: Optional[str] = None
    video_path: Optional[str] = None
    video_start_time: Optional[float] = None

class ParkingLotRead(ParkingLotBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


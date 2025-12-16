from pydantic import BaseModel, ConfigDict
from typing import Optional, List
from datetime import datetime


class ParkingSpotBase(BaseModel):
	parking_lot_id: int
	spot_number: str
	x: Optional[int] = None
	y: Optional[int] = None
	width: Optional[int] = None
	height: Optional[int] = None
	polygon: Optional[List[List[int]]] = None


class ParkingSpotCreate(ParkingSpotBase):
	pass


class ParkingSpotRead(ParkingSpotBase):
	id: int
	created_at: Optional[datetime] = None
	current_status: Optional[str] = None

	model_config = ConfigDict(from_attributes=True)



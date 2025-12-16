from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime


class SpotStatusBase(BaseModel):
	parking_spot_id: int
	status: str
	detected_at: Optional[datetime] = None
	detection_method: Optional[str] = None
	meta: Optional[dict] = None


class SpotStatusCreate(SpotStatusBase):
	pass


class SpotStatusRead(SpotStatusBase):
	id: int

	model_config = ConfigDict(from_attributes=True)



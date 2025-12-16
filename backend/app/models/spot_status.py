# backend/app/models/spot_status.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text
from datetime import datetime, timezone
from app.utils.db import Base
from sqlalchemy.orm import relationship

class SpotStatus(Base):
    __tablename__ = "spot_status"

    id = Column(Integer, primary_key=True, index=True)
    parking_spot_id = Column(Integer, ForeignKey("parking_spots.id"))
    status = Column(String(20), nullable=False)
    detected_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    detection_method = Column(String(50))
    meta = Column(Text, nullable=True)

    parking_spot = relationship("ParkingSpot", back_populates="statuses")
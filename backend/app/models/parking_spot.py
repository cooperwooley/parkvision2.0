# backend/app/models/parking_spot.py
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from datetime import datetime, timezone
from app.utils.db import Base
from sqlalchemy.orm import relationship

class ParkingSpot(Base):
    __tablename__ = "parking_spots"

    id = Column(Integer, primary_key=True, index=True)
    parking_lot_id = Column(Integer, ForeignKey("parking_lots.id"))
    spot_number = Column(String(20), nullable=False)
    x = Column(Integer, nullable=True)
    y = Column(Integer, nullable=True)
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    polygon = Column(JSON, nullable=True)
    annotation_id = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    parking_lot = relationship("ParkingLot", back_populates="parking_spots")
    statuses = relationship("SpotStatus", back_populates="parking_spot")
    vehicle = relationship("Vehicle", back_populates="parking_spot", uselist=False)
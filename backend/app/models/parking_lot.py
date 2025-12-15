# backend/app/models/parking_lot.py
from sqlalchemy import Column, Integer, String, Text, Float, DateTime
from datetime import datetime, timezone
from app.utils.db import Base
from sqlalchemy.orm import relationship

class ParkingLot(Base):
    __tablename__ = "parking_lots"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    address = Column(Text)
    total_spaces = Column(Integer, nullable=False)
    description = Column(Text)
    init_frame_path = Column(Text)
    video_path = Column(Text)
    video_start_time = Column(Float)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    parking_spots = relationship("ParkingSpot", back_populates="parking_lot")
    analytics = relationship("ParkingAnalytics", back_populates="parking_lot")
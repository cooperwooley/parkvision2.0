# backend/app/models/parking_analytics.py
from sqlalchemy import Column, Integer, Float, Boolean, DateTime, ForeignKey
from datetime import datetime, timezone
from app.utils.db import Base
from sqlalchemy.orm import relationship

class ParkingAnalytics(Base):
    __tablename__ = "parking_analytics"

    id = Column(Integer, primary_key=True, index=True)
    parking_lot_id = Column(Integer, ForeignKey("parking_lots.id"))
    time_stamp = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    total_spaces = Column(Integer, nullable=False)
    occupied_spaces = Column(Integer, nullable=False)
    occupancy_rate = Column(Float)
    peak_hour = Column(Boolean, default=False)

    parking_lot = relationship("ParkingLot", back_populates="analytics")
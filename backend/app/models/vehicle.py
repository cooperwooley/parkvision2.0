# backend/app/models/vehicle.py
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from datetime import datetime, timezone
from app.utils.db import Base
from sqlalchemy.orm import relationship

class Vehicle(Base):
    __tablename__ = "vehicles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    parking_spot_id = Column(Integer, ForeignKey("parking_spots.id"), nullable=True)
    license_plate = Column(String(20), unique=True, nullable=False)
    vehicle_type = Column(String(30), nullable=False)
    make = Column(String(50))
    model = Column(String(50))
    color = Column(String(30))
    entry_time = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    exit_time = Column(DateTime, nullable=True)
    is_parked = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    user = relationship("User", back_populates="vehicles")
    parking_spot = relationship("ParkingSpot", back_populates="vehicle")
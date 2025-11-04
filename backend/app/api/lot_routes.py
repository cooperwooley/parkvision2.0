# backend/app/api/lot_routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.utils.db import SessionLocal
from app.models.parking_lot import ParkingLot
from app.schemas.parking_lot import ParkingLotCreate, ParkingLotUpdate, ParkingLotRead
from typing import List

router = APIRouter(prefix="/lots", tags=["Parking Lots"])

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Create a new parking lot
@router.post("/", response_model=ParkingLotRead, status_code=status.HTTP_201_CREATED)
def create_parking_lot(lot: ParkingLotCreate, db: Session = Depends(get_db)):
    """Create a new parking lot."""
    new_lot = ParkingLot(**lot.model_dump())
    db.add(new_lot)
    db.commit()
    db.refresh(new_lot)
    return new_lot

# Get all parking lots
@router.get("/", response_model=List[ParkingLotRead])
def get_all_parking_lots(db: Session = Depends(get_db)):
    """Return all parking lots."""
    lots = db.query(ParkingLot).all()
    return lots

# Get parking lot by ID
@router.get("/{lot_id}", response_model=ParkingLotRead)
def get_parking_lot(lot_id: int, db: Session = Depends(get_db)):
    """Get one parking lot by ID."""
    lot = db.query(ParkingLot).filter(ParkingLot.id == lot_id).first()
    if not lot:
        raise HTTPException(status_code=404, detail="Parking lot not found")
    return lot

# Update parking lot by ID
@router.put("/{lot_id}", response_model=ParkingLotRead)
def update_parking_lot(lot_id: int, updates: ParkingLotUpdate, db: Session = Depends(get_db)):
    """Update an existing parking lot."""
    lot = db.query(ParkingLot).filter(ParkingLot.id == lot_id).first()
    if not lot:
        raise HTTPException(status_code=404, detail="Parking lot not found")

    for key, value in updates.model_dump(exclude_unset=True).items():
        setattr(lot, key, value)

    db.commit()
    db.refresh(lot)
    return lot

# Delete parking lot by ID
@router.delete("/{lot_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_parking_lot(lot_id: int, db: Session = Depends(get_db)):
    lot = db.query(ParkingLot).filter(ParkingLot.id == lot_id).first()
    if not lot:
        raise HTTPException(status_code=404, detail="Parking lot not found")

    db.delete(lot)
    db.commit()
    return

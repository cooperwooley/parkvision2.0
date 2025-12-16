# backend/app/api/lot_routes.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.utils.db import SessionLocal
from app.models.parking_lot import ParkingLot
from app.schemas.parking_lot import ParkingLotCreate, ParkingLotUpdate, ParkingLotRead
from typing import List
import json
from app.models.parking_spot import ParkingSpot
from app.models.spot_status import SpotStatus
from app.schemas.parking_spot import ParkingSpotRead

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
    new_lot = ParkingLot(**lot.model_dump())
    db.add(new_lot)
    db.commit()
    db.refresh(new_lot)
    return new_lot

# Get all parking lots
@router.get("/", response_model=List[ParkingLotRead])
def get_all_parking_lots(db: Session = Depends(get_db)):
    lots = db.query(ParkingLot).all()
    return lots

# Get parking lot by ID
@router.get("/{lot_id}", response_model=ParkingLotRead)
def get_parking_lot(lot_id: int, db: Session = Depends(get_db)):
    lot = db.query(ParkingLot).filter(ParkingLot.id == lot_id).first()
    if not lot:
        raise HTTPException(status_code=404, detail="Parking lot not found")
    # convert stored polygon JSON to lists for response validation
    for spot in getattr(lot, "parking_spots", []):
        try:
            if spot.polygon:
                spot.polygon = json.loads(spot.polygon)
        except Exception:
            spot.polygon = None
    return lot

# Update parking lot by ID
@router.put("/{lot_id}", response_model=ParkingLotRead)
def update_parking_lot(lot_id: int, updates: ParkingLotUpdate, db: Session = Depends(get_db)):
    lot = db.query(ParkingLot).filter(ParkingLot.id == lot_id).first()
    if not lot:
        raise HTTPException(status_code=404, detail="Parking lot not found")

    for key, value in updates.model_dump(exclude_unset=True).items():
        setattr(lot, key, value)

    db.commit()
    db.refresh(lot)
    for spot in getattr(lot, "parking_spots", []):
        try:
            if spot.polygon:
                spot.polygon = json.loads(spot.polygon)
        except Exception:
            spot.polygon = None
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


# Initialize parking spots from AI annotations (list of {points: [[x,y], ...], spot_number?: str})
@router.post("/{lot_id}/init", response_model=ParkingLotRead)
def init_lot_from_annotations(lot_id: int, payload: dict, db: Session = Depends(get_db)):
    lot = db.query(ParkingLot).filter(ParkingLot.id == lot_id).first()
    if not lot:
        raise HTTPException(status_code=404, detail="Parking lot not found")

    annotations = payload.get("annotations") or payload.get("spots")
    if not annotations or not isinstance(annotations, list):
        raise HTTPException(status_code=400, detail="'annotations' list required")

    created = []
    for idx, ann in enumerate(annotations):
        pts = ann.get("points") or ann.get("bbox")
        if not pts:
            continue
        spot_number = ann.get("spot_number") or str(idx + 1)

        new_spot = ParkingSpot(
            parking_lot_id=lot.id,
            spot_number=spot_number,
            polygon=pts,
            annotation_id=ann.get("id") or (idx + 1)
        )
        db.add(new_spot)
        db.flush()
        created.append(new_spot)

    # update total_spaces
    lot.total_spaces = max(lot.total_spaces or 0, len(lot.parking_spots) + len(created))
    db.commit()
    db.refresh(lot)
    # polygon stored as JSON, no parsing required
    return lot


# Update a single spot's occupancy/status. payload: {"status": "occupied"/"vacant", "meta": {...}}
@router.post("/{lot_id}/spots/{spot_id}/update")
def update_spot(lot_id: int, spot_id: int, payload: dict, db: Session = Depends(get_db)):
    lot = db.query(ParkingLot).filter(ParkingLot.id == lot_id).first()
    if not lot:
        raise HTTPException(status_code=404, detail="Parking lot not found")

    spot = db.query(ParkingSpot).filter(ParkingSpot.id == spot_id, ParkingSpot.parking_lot_id == lot_id).first()
    if not spot:
        raise HTTPException(status_code=404, detail="Parking spot not found")

    status_val = payload.get("status")
    if not status_val:
        raise HTTPException(status_code=400, detail="'status' is required")

    meta = payload.get("meta")
    ss = SpotStatus(parking_spot_id=spot.id, status=status_val, detection_method="ai_cv", meta=json.dumps(meta) if meta is not None else None)
    db.add(ss)
    # update current_status on the spot
    spot.current_status = status_val
    db.add(spot)
    db.commit()
    return {"spot_id": spot.id, "status": status_val, "current_status": spot.current_status}


# Bulk update multiple spot statuses in one request
@router.post("/{lot_id}/bulk_update")
def bulk_update_spots(lot_id: int, payload: dict, db: Session = Depends(get_db)):
    lot = db.query(ParkingLot).filter(ParkingLot.id == lot_id).first()
    if not lot:
        raise HTTPException(status_code=404, detail="Parking lot not found")

    updates = payload.get("updates")
    if not updates or not isinstance(updates, list):
        raise HTTPException(status_code=400, detail="'updates' list required")

    results = []
    for u in updates:
        spot_id = u.get("spot_id")
        status = u.get("status")
        meta = u.get("meta")

        spot = db.query(ParkingSpot).filter(ParkingSpot.id == spot_id, ParkingSpot.parking_lot_id == lot_id).first()
        if not spot:
            results.append({"spot_id": spot_id, "status": "not_found"})
            continue

        ss = SpotStatus(parking_spot_id=spot.id, status=status, detection_method="ai_cv", meta=json.dumps(meta) if meta is not None else None)
        db.add(ss)
        # set denormalized current status for quick reads
        spot.current_status = status
        db.add(spot)
        results.append({"spot_id": spot.id, "status": status})

    db.commit()
    return {"updated": results}


# Return list of spots for a lot including latest status
@router.get("/{lot_id}/spots")
def list_spots_with_status(lot_id: int, db: Session = Depends(get_db)):
    lot = db.query(ParkingLot).filter(ParkingLot.id == lot_id).first()
    if not lot:
        raise HTTPException(status_code=404, detail="Parking lot not found")

    spots = []
    for spot in lot.parking_spots:
        # parse polygon if present
        try:
            if spot.polygon:
                poly = json.loads(spot.polygon)
            else:
                poly = None
        except Exception:
            poly = None

        latest = db.query(SpotStatus).filter(SpotStatus.parking_spot_id == spot.id).order_by(SpotStatus.detected_at.desc()).first()
        latest_status = None
        latest_meta = None
        latest_detected_at = None
        if latest:
            latest_status = latest.status
            latest_detected_at = latest.detected_at.isoformat()
            try:
                latest_meta = json.loads(latest.meta) if latest.meta else None
            except Exception:
                latest_meta = latest.meta

        spots.append({
            "id": spot.id,
            "spot_number": spot.spot_number,
            "polygon": poly,
            "last_status": latest_status,
            "last_detected_at": latest_detected_at,
            "last_meta": latest_meta,
            "current_status": getattr(spot, "current_status", None)
        })

    return {"lot_id": lot.id, "spots": spots}


# Return latest status summary for a lot (spot_id -> status)
@router.get("/{lot_id}/status")
def lot_status_summary(lot_id: int, db: Session = Depends(get_db)):
    lot = db.query(ParkingLot).filter(ParkingLot.id == lot_id).first()
    if not lot:
        raise HTTPException(status_code=404, detail="Parking lot not found")

    summary = {}
    for spot in lot.parking_spots:
        # prefer denormalized current_status for fast reads
        summary[spot.id] = getattr(spot, "current_status", None)

    return {"lot_id": lot.id, "summary": summary}


# Return latest status for a single spot
@router.get("/{lot_id}/spots/{spot_id}/status")
def spot_latest_status(lot_id: int, spot_id: int, db: Session = Depends(get_db)):
    spot = db.query(ParkingSpot).filter(ParkingSpot.id == spot_id, ParkingSpot.parking_lot_id == lot_id).first()
    if not spot:
        raise HTTPException(status_code=404, detail="Parking spot not found")
    # Return the denormalized current status; include latest event metadata if available
    latest = db.query(SpotStatus).filter(SpotStatus.parking_spot_id == spot.id).order_by(SpotStatus.detected_at.desc()).first()
    try:
        meta = json.loads(latest.meta) if latest and latest.meta else None
    except Exception:
        meta = latest.meta if latest else None

    return {
        "spot_id": spot.id,
        "status": getattr(spot, "current_status", None),
        "detected_at": latest.detected_at.isoformat() if latest else None,
        "meta": meta
    }

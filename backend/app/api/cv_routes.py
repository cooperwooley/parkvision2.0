from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from app.utils.db import SessionLocal
from app.models.parking_spot import ParkingSpot
from app.models.spot_status import SpotStatus
from app.models.parking_lot import ParkingLot
from app.services.cv_integration import process_image_with_cv, detect_parking_spots
import json
from datetime import datetime, timezone

router = APIRouter(prefix="/cv", tags=["CV Integration"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _point_in_poly(x: float, y: float, poly: list) -> bool:
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        intersect = ((yi > y) != (yj > y)) and (x < (xj - xi) * (y - yi) / (yj - yi + 1e-9) + xi)
        if intersect:
            inside = not inside
        j = i
    return inside


@router.post("/spot_status/", status_code=status.HTTP_201_CREATED)
def post_spot_status(payload: dict, db: Session = Depends(get_db)):
    spot_id = payload.get("parking_spot_id")
    status_text = payload.get("status")
    if not spot_id or not status_text:
        raise HTTPException(status_code=400, detail="parking_spot_id and status required")

    spot = db.query(ParkingSpot).filter(ParkingSpot.id == spot_id).first()
    if not spot:
        raise HTTPException(status_code=404, detail="Parking spot not found")

    ss = SpotStatus(parking_spot_id=spot.id, status=status_text, detection_method=payload.get("detection_method"), meta=json.dumps(payload.get("meta")) if payload.get("meta") else None)
    db.add(ss)
    spot.current_status = status_text
    db.add(spot)
    db.commit()
    db.refresh(ss)
    return {"parking_spot_id": spot.id, "status": status_text, "detected_at": ss.detected_at.isoformat()}


@router.post("/spot_status_by_bbox/", status_code=status.HTTP_201_CREATED)
def post_spot_status_by_bbox(payload: dict, db: Session = Depends(get_db)):
    lot_id = payload.get("parking_lot_id")
    bbox = payload.get("bbox")
    status_text = payload.get("status")

    if not lot_id or not bbox or not status_text:
        raise HTTPException(status_code=400, detail="parking_lot_id, bbox and status are required")

    # compute center point
    xs = [p[0] for p in bbox]
    ys = [p[1] for p in bbox]
    cx = sum(xs) / len(xs)
    cy = sum(ys) / len(ys)

    spots = db.query(ParkingSpot).filter(ParkingSpot.parking_lot_id == lot_id).all()
    matched = None
    for s in spots:
        if s.polygon:
            try:
                spoly = s.polygon
                if _point_in_poly(cx, cy, spoly):
                    matched = s
                    break
            except Exception:
                pass
        else:
            try:
                sx1, sy1 = s.x, s.y
                sx2, sy2 = s.x + s.width, s.y + s.height
                if sx1 <= cx <= sx2 and sy1 <= cy <= sy2:
                    matched = s
                    break
            except Exception:
                continue

    if not matched:
        raise HTTPException(status_code=404, detail="No matching parking spot found for provided bbox")

    ss = SpotStatus(parking_spot_id=matched.id, status=status_text, detection_method=payload.get("detection_method"), meta=json.dumps(payload.get("meta")) if payload.get("meta") else None)
    db.add(ss)
    matched.current_status = status_text
    db.add(matched)
    db.commit()
    db.refresh(ss)

    return {"parking_spot_id": matched.id, "status": status_text, "detected_at": ss.detected_at.isoformat()}


@router.post("/process_image/{lot_id}", status_code=status.HTTP_200_OK)
async def process_image(
    lot_id: int,
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Process an uploaded image using ai_cv and update parking spot statuses.
    
    Returns the bulk update results.
    """
    # Verify lot exists
    lot = db.query(ParkingLot).filter(ParkingLot.id == lot_id).first()
    if not lot:
        raise HTTPException(status_code=404, detail="Parking lot not found")
    
    # Get all parking spots for this lot
    spots = db.query(ParkingSpot).filter(ParkingSpot.parking_lot_id == lot_id).all()
    if not spots:
        raise HTTPException(status_code=400, detail="No parking spots defined for this lot. Initialize spots first.")
    
    # Convert spots to dict format for processing
    spots_data = []
    for spot in spots:
        spot_dict = {
            "id": spot.id,
            "polygon": spot.polygon  # Already JSON or list
        }
        spots_data.append(spot_dict)
    
    # Read image data
    try:
        image_data = await image.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read image: {str(e)}")
    
    # Process image with CV
    try:
        updates = process_image_with_cv(image_data, spots_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CV processing failed: {str(e)}")
    
    if not updates:
        return {"updated": [], "message": "No updates generated"}
    
    # Apply updates via bulk_update logic
    results = []
    for u in updates:
        spot_id = u.get("spot_id")
        status_val = u.get("status")
        meta = u.get("meta")
        
        spot = db.query(ParkingSpot).filter(ParkingSpot.id == spot_id, ParkingSpot.parking_lot_id == lot_id).first()
        if not spot:
            results.append({"spot_id": spot_id, "status": "not_found"})
            continue
        
        ss = SpotStatus(
            parking_spot_id=spot.id,
            status=status_val,
            detection_method="ai_cv",
            meta=json.dumps(meta) if meta else None
        )
        db.add(ss)
        spot.current_status = status_val
        db.add(spot)
        results.append({"spot_id": spot.id, "status": status_val})
    
    db.commit()
    return {"updated": results, "lot_id": lot_id}


@router.post("/detect_spots/", status_code=status.HTTP_200_OK)
async def detect_spots(
    image: UploadFile = File(...)
):
    """
    Quick and dirty parking spot detection from an uploaded image.
    Returns detected parking spots as polygons.
    
    This is a simple heuristic-based approach for demo purposes.
    """
    # Read image data
    try:
        image_data = await image.read()
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read image: {str(e)}")
    
    # Detect spots
    try:
        spots = detect_parking_spots(image_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Spot detection failed: {str(e)}")
    
    return {
        "detected_spots": spots,
        "count": len(spots)
    }
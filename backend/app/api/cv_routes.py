from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.utils.db import SessionLocal
from app.models.parking_spot import ParkingSpot
from app.models.spot_status import SpotStatus
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

# backend/app/services/cv_integration.py
import sys
import os
from pathlib import Path

# Add ai_cv to Python path
backend_dir = Path(__file__).parent.parent.parent
project_root = backend_dir.parent
ai_cv_path = project_root / "ai_cv"
if str(ai_cv_path) not in sys.path:
    sys.path.insert(0, str(ai_cv_path))

import cv2 as cv
import numpy as np
from typing import List, Dict, Tuple, Optional
import json

try:
    from detection.lot_detector import LotDetector
except ImportError:
    LotDetector = None


def process_image_with_cv(
    image_data: bytes,
    parking_spots: List[Dict],
    lot_detector: Optional[LotDetector] = None
) -> List[Dict]:
    """
    Process an image using ai_cv LotDetector and match results to parking spots.
    
    Args:
        image_data: Image bytes (e.g., from uploaded file)
        parking_spots: List of parking spot dicts with 'id', 'polygon' (JSON string or list)
        lot_detector: Optional pre-initialized LotDetector instance
        
    Returns:
        List of updates in format: [{"spot_id": int, "status": "occupied"|"vacant", "meta": {...}}, ...]
    """
    if LotDetector is None:
        raise RuntimeError("ai_cv LotDetector not available. Ensure ai_cv module is installed.")
    
    # Decode image
    nparr = np.frombuffer(image_data, np.uint8)
    frame = cv.imdecode(nparr, cv.IMREAD_COLOR)
    if frame is None:
        raise ValueError("Failed to decode image")
    
    # Initialize detector if not provided
    if lot_detector is None:
        lot_detector = LotDetector()
    
    # Extract lot polygons from parking spots
    lot_polygons = []
    spot_id_to_polygon = {}
    
    for spot in parking_spots:
        spot_id = spot["id"]
        polygon = spot.get("polygon")
        
        # Parse polygon if it's a JSON string
        if isinstance(polygon, str):
            try:
                polygon = json.loads(polygon)
            except (json.JSONDecodeError, TypeError):
                continue
        
        if polygon and isinstance(polygon, list) and len(polygon) > 0:
            lot_polygons.append({
                "points": polygon,
                "spot_id": spot_id
            })
            spot_id_to_polygon[spot_id] = polygon
    
    if not lot_polygons:
        # No polygons to process
        return []
    
    # Create temporary JSON file for LotDetector
    # Track the mapping from polygon index to spot_id
    import tempfile
    polygon_index_to_spot_id = {}
    json_lots = []
    for idx, lp in enumerate(lot_polygons):
        json_lots.append({"points": lp["points"]})
        polygon_index_to_spot_id[idx] = lp["spot_id"]
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        temp_json_path = f.name
        json.dump(json_lots, f)
    
    try:
        # Detect occupied/unoccupied lots
        occupied, unoccupied, detections = lot_detector.detect(frame, temp_json_path)
        
        # Build updates: track which spot indices are occupied
        occupied_indices = set()
        updates = []
        
        # Match occupied lots back to original polygon indices
        # The occupied list contains bboxes (polygon points) from the original natural_poly
        for occ in occupied:
            occ_bbox = occ.get("bbox", [])
            if not occ_bbox:
                continue
            
            # Find which polygon index this occupied bbox matches
            # by comparing with original polygons (bbox is the polygon points)
            for idx, lp in enumerate(lot_polygons):
                if idx in occupied_indices:
                    continue
                # Compare polygon points - handle both list of lists and flat lists
                if _polygons_match(occ_bbox, lp["points"]):
                    spot_id = polygon_index_to_spot_id[idx]
                    occupied_indices.add(idx)
                    updates.append({
                        "spot_id": spot_id,
                        "status": "occupied",
                        "meta": {
                            "conf": occ.get("conf", 0),
                            "name": occ.get("name", "vehicle"),
                            "cls": occ.get("cls", 0),
                            "track_id": occ.get("track_id")
                        }
                    })
                    break
        
        # Mark all unoccupied spots as vacant
        for idx, lp in enumerate(lot_polygons):
            if idx not in occupied_indices:
                spot_id = polygon_index_to_spot_id[idx]
                updates.append({
                    "spot_id": spot_id,
                    "status": "vacant",
                    "meta": {}
                })
        
        return updates
        
    finally:
        # Clean up temp file
        try:
            os.unlink(temp_json_path)
        except Exception:
            pass


def _polygons_match(poly1: List, poly2: List, tolerance: float = 5.0) -> bool:
    """Check if two polygons match by comparing points (within tolerance)."""
    if len(poly1) != len(poly2):
        return False
    
    # Normalize point order (start from min x,y)
    def normalize_poly(poly):
        if not poly:
            return poly
        # Find starting point (min x, then min y)
        start_idx = 0
        min_x, min_y = poly[0][0], poly[0][1]
        for i, (x, y) in enumerate(poly):
            if x < min_x or (x == min_x and y < min_y):
                min_x, min_y = x, y
                start_idx = i
        # Rotate to start from this point
        return poly[start_idx:] + poly[:start_idx]
    
    norm1 = normalize_poly(poly1)
    norm2 = normalize_poly(poly2)
    
    # Check if all points match within tolerance
    for (x1, y1), (x2, y2) in zip(norm1, norm2):
        if abs(x1 - x2) > tolerance or abs(y1 - y2) > tolerance:
            return False
    
    return True

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


def detect_parking_spots(image_data: bytes) -> List[Dict]:
    """
    Quick and dirty parking spot detection from an image.
    Uses edge detection and contour finding to detect rectangular parking spots.
    
    Args:
        image_data: Image bytes (e.g., from uploaded file)
        
    Returns:
        List of detected spots in format: [{"polygon": [[x1,y1], [x2,y2], ...], "confidence": float}, ...]
    """
    # Decode image
    nparr = np.frombuffer(image_data, np.uint8)
    frame = cv.imdecode(nparr, cv.IMREAD_COLOR)
    if frame is None:
        raise ValueError("Failed to decode image")
    
    h, w = frame.shape[:2]
    img_area = h * w
    
    # Convert to grayscale
    gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    
    # Apply Gaussian blur to reduce noise
    blurred = cv.GaussianBlur(gray, (5, 5), 0)
    
    # Edge detection
    edges = cv.Canny(blurred, 50, 150)
    
    # Dilate edges to connect nearby lines
    kernel = np.ones((3, 3), np.uint8)
    dilated = cv.dilate(edges, kernel, iterations=2)
    
    # Find contours
    contours, _ = cv.findContours(dilated, cv.RETR_EXTERNAL, cv.CHAIN_APPROX_SIMPLE)
    
    detected_spots = []
    
    for contour in contours:
        # Filter by area (parking spots should be reasonably sized)
        area = cv.contourArea(contour)
        min_area = img_area * 0.001  # At least 0.1% of image
        max_area = img_area * 0.15   # At most 15% of image
        
        if area < min_area or area > max_area:
            continue
        
        # Approximate contour to polygon
        epsilon = 0.02 * cv.arcLength(contour, True)
        approx = cv.approxPolyDP(contour, epsilon, True)
        
        # Filter for roughly rectangular shapes (3-6 vertices)
        if len(approx) < 3 or len(approx) > 6:
            continue
        
        # Get bounding rectangle to check aspect ratio
        x, y, w_rect, h_rect = cv.boundingRect(approx)
        aspect_ratio = w_rect / h_rect if h_rect > 0 else 0
        
        # Parking spots are typically rectangular (aspect ratio between 0.3 and 3.0)
        if aspect_ratio < 0.3 or aspect_ratio > 3.0:
            continue
        
        # Convert to list of points
        polygon = [[int(point[0][0]), int(point[0][1])] for point in approx]
        
        # Calculate confidence based on how rectangular it is
        rect_area = w_rect * h_rect
        extent = area / rect_area if rect_area > 0 else 0
        
        detected_spots.append({
            "polygon": polygon,
            "confidence": float(extent),  # Higher extent = more rectangular = higher confidence
            "area": float(area)
        })
    
    # Sort by confidence (most rectangular first)
    detected_spots.sort(key=lambda x: x["confidence"], reverse=True)
    
    # Limit to top 50 spots to avoid too many false positives
    return detected_spots[:50]

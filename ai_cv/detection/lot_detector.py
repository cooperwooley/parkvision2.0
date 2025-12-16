# ai_cv/detection/lot_detect.py
from ast import UnaryOp
import enum
import cv2 as cv
import numpy as np
from ultralytics import solutions
import json
from detection.detect import VehicleDetector
from recognition.tracker import VehicleTracker

class LotDetector:
    def __init__(self, model_path = "best.pt", iou_thresh=.01, conf_thresh = 0.05):
        self.model_path = model_path
        self.detected = None
        
        self.vehicledetector = VehicleDetector(model_path, conf_thresh = conf_thresh, iou_thresh = iou_thresh)
        
        self.vehicletracker = VehicleTracker()


    def detect(self, frame, json_path):
        #using https://arxiv.org/html/2505.17364v1 as refrence regarding detection in borders declared by json

        #get detections
        self.detected = self.vehicledetector.detect(frame)
        
        #imort json data
        with open(json_path, 'r') as file:
            data = json.load(file)
            
        #Read json file and turn into bbox
        natural_poly = []
        for lot in data:
            pts = lot['points']  # e.g., [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
            # Ensure poloygon is closed
            if len(pts) > 0:
                # Ensure points are in correct format
                if isinstance(pts[0], (int, float)):
                    # If it's flat, reshape
                    pts = [[pts[i], pts[i+1]] for i in range(0, len(pts, 2))]
                natural_poly.append({
                    "bbox": pts,
                    "conf": 0,
                })
        
        # Use improved matching logic
        occupied, unoccupied = self._match_detections_to_lots(self.detected, natural_poly)
        
        print(f"Unoccupied lots: {len(unoccupied)}")
        return occupied, unoccupied, self.detected


    """
    Match vehicle detections to parking lots using best-match strategy.
    """
    def _match_detections_to_lots(self, detections, natural_poly):
        occupied = []
        matched_lot_indices = set()

        # Find best matching lot for each detection
        for det in detections:
            best_iou = 0
            best_lot_idx = None

            for idx, lot_box in enumerate(natural_poly):
                if idx in matched_lot_indices:
                    continue

                iou = self._poly_rect_iou(lot_box["bbox"], det["xyxy"])
                if iou > 0.3 and iou > best_iou: # IOU thres
                    best_iou = iou
                    best_lot_idx = idx

            if best_lot_idx is not None:
                matched_lot_indices.add(best_lot_idx)
                lot_box = natural_poly[best_lot_idx]
                occupied.append({
                    "bbox": lot_box["bbox"],
                    "conf": best_iou,
                    "cls": det["cls"],
                    "name": det["name"]
                })

        # Find unoccupied lots
        unoccupied = []
        for idx, box in enumerate(natural_poly):
            if idx not in matched_lot_indices:
                unoccupied.append(box)

        return occupied, unoccupied


    """
    Calculate IoU between a polygon and a rectangle.
    Uses a more robust method for polygon-rectangle intersection.
    """
    @staticmethod
    def _poly_rect_iou(polygon_points, rect_xyxy):
        poly = np.array(polygon_points, dtype=np.float32)
        
        # Ensure polygon is closed
        if len(poly) > 0 and not np.array_equal(poly[0], poly[-1]):
            poly = np.vstack([poly, poly[0:1]])

        # Ensure polygon has at least 3 points
        if len(poly) < 3:
            return 0.0

        x_min, y_min, x_max, y_max = rect_xyxy
        rect = np.array([
            [x_min, y_min],
            [x_max, y_min],
            [x_max, y_max],
            [x_min, y_max],
            [x_min, y_min] # Close the rectangle
        ], dtype=np.float32)

        # Compute polygon area
        poly_area = cv.contourArea(poly)
        if poly_area <= 0:
            return 0.0

        # Compute rectangle area
        rect_area = (x_max - x_min) * (y_max - y_min)
        if rect_area <= 0:
            return 0.0
        
        # Compute intersection using fillPoly
        h, w = int(max(poly[:, 1].max(), y_max)) + 1, int(max(poly[:, 0].max(), x_max)) + 1
        mask_poly = np.zeros((h, w), dtype=np.uint8)
        mask_rect = np.zeros((h, w), dtype=np.uint8)

        cv.fillPoly(mask_poly, [poly.astype(np.int32)], 255)
        cv.fillPoly(mask_rect, [rect.astype(np.int32)], 255)

        intersection = cv.bitwise_and(mask_poly, mask_rect)
        inter_area = np.sum(intersection > 0)

        # Compute union
        union_area = poly_area + rect_area - inter_area
        if union_area <= 0:
            return 0.0

        return float(inter_area / union_area)


    """
    Process video stream with vehicle tracking and lot detection.
    
    Args:
        video_path: Path to video file or camera index (0 for webcam)
        json_path: Path to JSON file containing lot annotations
        callback_fn: Optional callback function(frame, occupied, unoccupied, tracks)
    """
    def detect_from_video(self, video_path, json_path, callback_fn=None): 
        cap = cv.VideoCapture(video_path)

        # Load lot annotations
        with open(json_path, 'r') as file:
            data = json.load(file)

        natural_poly = []
        for lot in data:
            pts = lot['points']
            natural_poly.append({
                "bbox": pts,
                "conf": 0,
            })

        while True:
            ret, frame = cap.read()
            if not ret:
                break

            detections = self.vehicledetector.detect(frame)

            tracks = self.vehicletracker.update(detections, frame=frame)

            occupied, unoccupied = self._match_tracks_to_lots(tracks, natural_poly)

            if callback_fn:
                callback_fn(frame, occupied, unoccupied, tracks)

        cap.release()
        return occupied, unoccupied

    
    """
    Match tracked vehicles to parking lots.
    
    Args:
        tracks: List of tracked vehicles
        natural_poly: List of parking lot polygons
        
    Returns:
        occupied: List of occupied lots
        unoccupied: List of unoccupied lots
    """
    def _match_tracks_to_lots(self, tracks, natural_poly):
        occupied = []
        matched_lot_indices = set()

        # Find best matching lot for each track
        for track in tracks:
            best_iou = 0
            best_lot_idx = None

        for idx, lot_box in enumerate(natural_poly):
            if idx in matched_lot_indices:
                continue

            iou = self._poly_rect_iou(lot_box["bbox"], track["bbox"])
            if iou > 0.3 and iou > best_iou: # IOU thresh
                best_iou = iou
                best_lot_idx = idx

        if best_lot_idx is not None:
            matched_lot_indices.add(best_lot_idx)
            lot_box = natural_poly[best_lot_idx]
            occupied.append({
                "bbox": lot_box["bbox"],
                "conf": best_iou,
                "cls": track.get("cls", 0)
                "name": track.get("name", "vehicle"),
                "track_id": track.get("track_id")
            })

        # Find unoccupied lots
        unoccupied = []
        for idx, box in enumerate(natural_poly):
            if idx not in matched_lot_indices:
                unoccupied.append(box)

        return occupied, unoccupied
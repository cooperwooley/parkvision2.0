# ai_cv/detection/lot_detect.py
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
        json_bbox = []
        natrual_poly = []
        for lot in data:
            pts = lot['points']  # e.g., [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
            natrual_poly.append({
                "bbox": pts,
                "conf": 0,
            })
        
        occupied = []
        a_boxes = []
        unoc = []
        for det in self.detected:
            for lot_box in natrual_poly:
                iou = self._poly_rect_iou(lot_box["bbox"], det['xyxy'])
                if iou > .3: # IOU threshold
                    a_boxes.append(lot_box["bbox"])
                    occupied.append({
                        "bbox": lot_box["bbox"],
                        "conf": iou,
                        "cls": det["cls"],
                        "name": det["name"]
                    })
                    
        for box in natrual_poly:
            if box["bbox"] not in a_boxes:
                unoc.append(box)
        
        print(len(unoc))
        return occupied, unoc, self.detected
    
    
    @staticmethod
    def _poly_rect_iou(polygon_points, rect_xyxy):
        poly = np.array(polygon_points, dtype=np.float32)
        
        x_min, y_min, x_max, y_max = rect_xyxy
        rect = np.array([
            [x_min, y_min],
            [x_max, y_min],
            [x_max, y_max],
            [x_min, y_max]
        ], dtype=np.float32)
        
        
        # Compute intersection (returns area and polygon)
        inter_area, _ = cv.intersectConvexConvex(poly, rect)
        if inter_area <= 0:
            return 0.0

        # Compute individual areas
        poly_area = cv.contourArea(poly)
        rect_area = cv.contourArea(rect)

        # Compute union
        union_area = poly_area + rect_area - inter_area
        if union_area <= 0:
            return 0.0

        return float(inter_area / union_area)
        
        
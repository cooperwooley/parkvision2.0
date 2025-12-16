# ai_cv/detection/detect.py

from ultralytics import YOLO
import cv2 as cv

class VehicleDetector:
    def __init__(self, model_path = "yolov8n.pt", conf_thresh = 0.4, iou_thresh = 0.5):
        self.model = YOLO(model_path)
        self.conf_thresh = conf_thresh
        self.iou_thresh = iou_thresh

    def detect(self, frame):
        # run inference
        results = self.model.predict(frame, conf=self.conf_thresh, iou=self.iou_thresh)
        res = results[0]

        detections = []
        for box in res.boxes:
            x1, y1, x2, y2 = box.xyxy[0].tolist()
            conf = float(box.conf[0])
            cls = int(box.cls[0])
            name = res.names[cls]
            detections.append({
                "xyxy": [x1, y1, x2, y2],
                "conf": conf,
                "cls": cls,
                "name": name
            })

        return detections
    
    def detect_from_video(self, video_path, callback_fn=None):
        cap = cv.VideoCapture(video_path)
        while True:
            ret, frame = cap.read()
            if not ret:
                break
            dets = self.detect(frame)
            if callback_fn:
                callback_fn(frame, dets)
        cap.release()
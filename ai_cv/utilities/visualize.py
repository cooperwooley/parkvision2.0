# ai_cv/utilities.visualize.py

import cv2 as cv

def annotate_detections(image, detections, color=(0, 255, 0)):
    annotated = image.copy()
    for d in detections:
        x1, y1, x2, y2 = map(int, d["xyxy"])
        label = f"{d['name']} {d['conf']:.2f}"
        cv.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
        cv.putText(annotated, label, (x1, y1 - 5), cv.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
    return annotated

def annotate_tracks(image, tracks, color=(255, 0, 0)):
    annotated = image.copy()
    for t in tracks:
        x1, y1, x2, y2 = map(int, t["bbox"])
        label = f"ID {t['track_id']} ({t['name']})"
        cv.rectangle(annotated, (x1, y1), (x2, y2), color, 2)
        cv.putText(annotated, label, (x1, y1 - 5), cv.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
    return annotated


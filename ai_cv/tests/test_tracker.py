# ai_cv/tests/test_tracker.py

import sys, os
from pathlib import Path

# Add the parent folder (ai_cv) to the module search path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import cv2 as cv
import numpy as np
from recognition.tracker import VehicleTracker
from utilities.visualize import annotate_tracks


def test_tracking_consistency():
    tr = VehicleTracker(min_hits=1, use_embeddings=False)

    # Simulate two frames
    frame1 = np.zeros((300, 400, 3), dtype=np.uint8)
    frame2 = np.zeros((300, 400, 3), dtype=np.uint8)

    # Manually simulate detections
    # Suppose object bounding box appears at x=100 in frame1, then x=105 in frame2
    dets1 = [ {"xyxy": [100,100,150,150], "conf": 0.9, "cls": 2, "name": "car"} ]
    tracks1 = tr.update(dets1, frame=frame1)
    assert len(tracks1) == 1
    tid = tracks1[0]["track_id"]

    dets2 = [ {"xyxy": [105,100,155,150], "conf": 0.88, "cls": 2, "name": "car"} ]
    tracks2 = tr.update(dets2, frame=frame2)
    assert len(tracks2) == 1
    assert tracks2[0]["track_id"] == tid

def test_visual_tracking_sequence():
    tr = VehicleTracker(min_hits=1, use_embeddings=False)

    # Create synthetic test images
    frames = []
    for i in range(3):
        frame = np.zeros((300, 400, 3), dtype=np.uint8)
        # Draw rectangle moving slightly to right in each frame
        x1, y1, x2, y2 = 100 + i * 10, 120, 160 + i * 10, 180
        cv.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), -1)
        frames.append(frame)

    # Output directory
    out_dir = os.path.join(os.path.dirname(__file__), "outputs")
    os.makedirs(out_dir, exist_ok=True)

    track_id = None
    for idx, frame in enumerate(frames):
        # Create fake detections
        dets = [{"xyxy": [100 + idx * 10, 120, 160 + idx * 10, 180],
                 "conf": 0.95, "cls": 2, "name": "car"}]
        
        tracks = tr.update(dets, frame=frame)

        if idx == 0:
            assert len(tracks) == 1
            track_id = tracks[0]["track_id"]
        else:
            assert tracks[0]["track_id"] == track_id

        annotated = annotate_tracks(frame, tracks)
        out_path = os.path.join(out_dir, f"tracked_frame_{idx}.jpg")
        cv.imwrite(out_path, annotated)
        print(f"Save {out_path}")

def test_tracking_loss():
    pass
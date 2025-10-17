# ai_cv/tests/test_tracker.py

import sys
from pathlib import Path

# Add the parent folder (ai_cv) to the module search path
sys.path.append(str(Path(__file__).resolve().parents[1]))

from detection.detect import VehicleDetector
from recognition.tracker import VehicleTracker
import numpy as np


def test_tracking_consistency():
    tr = VehicleTracker()

    # Manually simulate detections
    # Suppose object bounding box appears at x=100 in frame1, then x=105 in frame2
    dets1 = [ {"xyxy": [100,100,150,150], "conf": 0.9, "cls": 2, "name": "car"} ]
    tracks1 = tr.update(dets1)
    assert len(tracks1) == 1
    tid = tracks1[0]["track_id"]

    dets2 = [ {"xyxy": [105,100,155,150], "conf": 0.88, "cls": 2, "name": "car"} ]
    tracks2 = tr.update(dets2)
    assert len(tracks2) == 1
    assert tracks2[0]["track_id"] == tid

def test_tracking_loss():
    pass
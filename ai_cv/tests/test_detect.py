# ai_cv/tests/test_detect.py

import sys
from pathlib import Path

# Add the parent folder (ai_cv) to the module search path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import cv2 as cv
import os
import numpy as np
from detection.detect import VehicleDetector

def test_detect_on_blank():
    # Create a blank image with no vehicles
    blank = np.zeros((480, 640, 3), dtype=np.uint8)
    det = VehicleDetector()
    results = det.detect(blank)
    assert isinstance(results, list)
    assert len(results) == 0

def test_detect_on_sample_image():
    # Use a sample image
    img_path = os.path.join(os.path.dirname(__file__), "test_data/images", "parking_lot_day.jpg")
    img = cv.imread(img_path)
    det = VehicleDetector()
    results = det.detect(img)
    # Expect at least one detection
    assert len(results) >= 1
    for r in results:
        assert "xyxy" in r and "conf" in r and "name" in r
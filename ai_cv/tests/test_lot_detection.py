# ai_cv/tests/test_lot_detection.py

import sys
from pathlib import Path

# Add the parent folder (ai_cv) to the module search path
sys.path.append(str(Path(__file__).resolve().parents[1]))

import cv2 as cv
import os
import numpy as np
import pandas as pd
from detection.lot_detector import LotDetector
from ultralytics import solutions
from utilities.visualize import annotate_detections
import xml.etree.ElementTree as ET
import json

'''
def test_detect_on_blank():
    # Create a blank image with no vehicles
    blank = np.zeros((480, 640, 3), dtype=np.uint8)
    det = LotDetector(model_path="best.pt")
    results = det.detect(blank)
    assert isinstance(results, list)
    assert len(results) == 0
'''

def extract_points_from_cvat(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()

    annotations = {}  # { "images/0.png": [ [points], [points], ... ], ... }

    for image in root.findall("image"):
        image_name = image.attrib.get("id")
        polygons = []

        for polygon in image.findall("polygon"):
            points_str = polygon.attrib.get("points", "")
            if not points_str:
                continue

            points = []
            for p in points_str.split(";"):
                if "," in p:
                    x, y = map(float, p.split(","))
                    points.append([x, y])
            polygons.append(points)

        annotations[image_name] = polygons

    return annotations

def convert_to_json(polygons, out_path):
    data = [{"points": pts} for pts in polygons]
    with open(out_path, "w") as f:
        json.dump(data, f, indent=4)
    return out_path

def test_detect_on_sample_image(json_path, image_path):
    # Use a sample image
    if os.path.isabs(image_path):
        img_path = image_path
    else:
        img_path = os.path.join(os.path.dirname(__file__), image_path)
    img = cv.imread(img_path)
    if img is None:
        raise FileNotFoundError(f"❌ Could not load image from: {img_path}")
    det = LotDetector(model_path="best.pt", iou_thresh = .001, conf_thresh = .001)

    occupied, blocked, unoccupied, detections = det.detect(img, json_path)

    blocked_det = []
    oc_det = []
    uc_det = []

    for box in blocked:
        # Ensure bbox is flat
        bbox = box['bbox']
        if isinstance(bbox[0], (list, tuple)):
            bbox = bbox[0] + bbox[2]

        blocked_det.append({
            "xyxy": bbox,
            "conf": box.get('conf', 1.0),
            "cls": 0,
            "name": "BLOCKED"
        })

    for box in occupied:
        # Ensure bbox is flat
        bbox = box['bbox']
        if isinstance(bbox[0], (list, tuple)):
            bbox = bbox[0] + bbox[2]

        oc_det.append({
            "xyxy": bbox,
            "conf": box.get('conf', 1.0),
            "cls": 0,
            "name": "TAKEN"
        })

    for box in unoccupied:
        if box not in occupied:
            bbox = box['bbox']
            if isinstance(bbox[0], (list, tuple)):
                bbox = bbox[0] + bbox[2]

            uc_det.append({
                "xyxy": bbox,
                "conf": 0,
                "cls": 0,
                "name": 'OPEN'
            })

    detects = annotate_detections(img, detections, (0,0,255))
    tannotated = annotate_detections(img, oc_det, (0,255,0))
    ttan = annotate_detections(tannotated, blocked_det, (0,255,255))
    annotated = annotate_detections(ttan, uc_det, (255,0,0))

    out_dir = os.path.join(os.path.dirname(__file__), "outputs")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, f"detected_lot_{os.path.basename(image_path)}")
    cv.imwrite(out_path, detects)

    print(f"Annotated detection saved to: {out_path}")


    # Print results, stored as


def test_multiple_img(folder_path):
    # In some /dir there has to be equal number of images and .json files
    # Also needs to be specifically .png and .json
    json_files = [pos_json for pos_json in os.listdir(folder_path) if pos_json.endswith('.json')]
    img_files = [pos_json for pos_json in os.listdir(folder_path) if pos_json.endswith('.png')]

    for timg, json in zip(img_files, json_files):
        img_path = os.path.join(os.path.dirname(folder_path, timg))
        json_path = os.path.join(os.path.dirname(folder_path, json))
        img = cv.imread(img_path)

        if img is None:
            raise FileNotFoundError(f"❌ Could not load image from: {img_path}")

        det = LotDetector(model_path="best.pt", json_path=json_path)
        results = det.detect(img)





if __name__ == "__main__":#
    if len(sys.argv) >1:
        xml_path = sys.argv[1]
    else:
        print("Please use with <command> <filepath to image>")

    annotations = extract_points_from_cvat(xml_path)

    for id, polygons in annotations.items():
        jid = id + ".json"
        json_path = os.path.join("lot_test_data/images/archive", jid)
        convert_to_json(polygons, json_path)

        iid = id + ".png"
        image_path = os.path.join("lot_test_data/images/archive/images", iid)

        test_detect_on_sample_image(json_path, image_path)


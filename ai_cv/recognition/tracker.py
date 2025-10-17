# ai_cv/recognition/tracker.py

from deep_sort_realtime.deepsort_tracker import DeepSort
import numpy as np

class VehicleTracker:
    def __init__(self, max_age = 30, min_hits = 3, nms_max_ol=1.0, iou_thresh=0.3):
        self.sort = DeepSort(max_age=max_age, n_init=min_hits, nms_max_overlap=nms_max_ol, max_cosine_distance=iou_thresh)

    def update(self, detections):
        # Convert detections to array [x1, y1, x2, y2, score] for the tracker
        det_array = np.array([d["xyxy"] + [d["conf"]] for d in detections])
        tracks = self.sort.update_tracks(det_array) # array with [x1, y1, x2, y2, track_id] per row

        out = []
        for t in tracks:
            x1, y1, x2, y2, tid = t.tolist()
            # find detection with highest overlap
            best = None
            best_iou = 0.0
            for d in detections:
                # compute IoU
                dx1 = max(x1, d["xyxy"][0])
                dy1 = max(y1, d["xyxy"][0])
                dx2 = max(x2, d["xyxy"][0])
                dy2 = max(y2, d["xyxy"][0])
                w = max(0, dx2 - dx1)
                h = max(0, dy2 - dy1)
                inter = w * h
                area1 = (x2 - x1) * (y2 - y1)
                area2 = (d["xyxy"][2] - d["xyxy"][0]) * (d["xyxy"][3] - d["xyxy"][1])
                union = area1 + area2 - inter
                iou = inter / union if union > 0 else 0
                if iou > best_iou:
                    best_iou = iou
                    best = d
            if best is not None:
                out.append({
                    "track_id": int(id),
                    "bbox": [x1, y1, x2, y2],
                    "conf": best["conf"],
                    "cls": best["cls"],
                    "name": best["name"]
                })
        return out

# ai_cv/recognition/tracker.py

from deep_sort_realtime.deepsort_tracker import DeepSort
import numpy as np

class VehicleTracker:
    def __init__(self, max_age = 30, min_hits = 3, nms_max_ol=1.0, iou_thresh=0.3, use_embeddings=True):
        self.use_embeddings = use_embeddings
        self.sort = DeepSort(max_age=max_age, n_init=min_hits, nms_max_overlap=nms_max_ol, max_cosine_distance=iou_thresh)
        self._simple_tracks = {}

    def update(self, detections, frame=None):
        if not detections:
            return []
        
        # Convert detections to array [x1, y1, x2, y2, score] for the tracker
        det_list = []
        for d in detections:
            x1, y1, x2, y2 = d["xyxy"]
            w, h = x2 - x1, y2 - y1
            det_list.append(([x1, y1, w, h], d["conf"], d["name"]))

        # If not using embeddings, feed dummy 128D vectors
        embeds = None
        if not self.use_embeddings:
            embeds = [np.random.rand(128).astype(np.float32) for _ in det_list]

        try:
            tracks = self.sort.update_tracks(det_list, 
                                             embeds=embeds, 
                                             frame=frame if self.use_embeddings else None,
                                             )
        except Exception:
            tracks = []

        out = []
        for t in tracks:
            if hasattr(t, "to_ltrb"):
                x1, y1, x2, y2 = t.to_ltrb()
                out.append({
                    "track_id": int(t.track_id),
                    "bbox": [x1, y1, x2, y2],
                    "conf": float(getattr(t, "det_conf", 1.0)),
                    "cls": detections[0]["cls"],
                    "name": detections[0]["name"],
                })

        if not out:
            new_out = []
            next_id = len(self._simple_tracks) + 1
            for d in detections:
                bbox = d["xyxy"]
                matched_id = None
                for tid, prev_bbox in self._simple_tracks.items():
                    iou = self._iou(bbox, prev_bbox)
                    if iou > 0.3:
                        matched_id = tid
                        break
                if matched_id is None:
                    matched_id = next_id
                    next_id += 1
                self._simple_tracks[matched_id] = bbox
                new_out.append({
                    "track_id": matched_id,
                    "bbox": bbox,
                    "conf": d["conf"],
                    "cls": d["cls"],
                    "name": d["name"],
                })
            out = new_out
        return out

    @staticmethod
    def _iou(b1, b2):
        x1 = max(b1[0], b2[0])
        y1 = max(b1[1], b2[1])
        x2 = min(b1[2], b2[2])
        y2 = min(b1[3], b2[3])
        inter = max(0, x2 - x1) * max(0, y2 - y1)
        area1 = (b1[2] - b1[0]) * (b1[3] - b1[1])
        area2 = (b2[2] - b2[0]) * (b2[3] - b2[1])
        union = area1 + area2 - inter
        return inter / union if union else 0.0
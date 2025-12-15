# ai_cv/run_pipeline.py

import cv2 as cv
import time
from detection.detect import VehicleDetector
from recognition.tracker import VehicleTracker
from recognition.session_logic import SessionManager

def draw(frame, tracks):
    for t in tracks:
        x1, y1, x2, y2 = map(int, t["bbox"])
        tid = t["track_id"]
        name = t["name"]
        conf = t["conf"]
        cv.rectangle(frame, (x1, y1), (x2, y2), (0,255,0), 2)
        cv.putText(frame, f"{name}-{tid}:{conf:.2f}", (x1, y1-10), cv.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)

def main(video_path):
    detector = VehicleDetector()
    tracker = VehicleTracker()
    sess_mgr = SessionManager()

    cap = cv.VideoCapture(video_path)
    while True:
        ret, frame = cap.read()
        if not ret:
            break

        start = time.time()
        dets = detector.detect(frame)
        stop = time.time()
        print(f"Detection duration: {stop-start}s")

        start = time.time()
        tracks = tracker.update(dets)
        stop = time.time()
        print(f"Tracking duration: {stop-start}s")

        start = time.time()
        completed = sess_mgr.update(tracks, timestamp=time.time())
        stop = time.time()
        print(f"Session logic duration: {stop-start}s")

        for c in completed:
            print("Vehicle left:", c)

        draw(frame, tracks)
        cv.imshow("Frame", frame)
        if cv.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv.destroyAllWindows()

if __name__ == "__main__":
    import sys
    video_path = sys.argv[1] if len(sys.argv) > 1 else 0
    main(video_path)
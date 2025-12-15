# ai_cv/recognition/session_logic.py

import time

class SessionManager:
    def __init__(self):
        self.sessions = {}

        self.disappearance_timeout = 5.0 # how many seconds to consider a vehicle is gone

    def update(self, tracks, timestamp=None):
        if timestamp is None:
            timestamp = time.time()

        active_ids = set()
        completed = []

        # update or create sessions for current tracks
        for t in tracks:
            tid = t["track_id"]
            active_ids.add(tid)
            if tid not in self.sessions:
                # new session
                self.sessions[tid] = {
                    "start_time": timestamp,
                    "last_seen": timestamp,
                    "bbox": t["bbox"],
                    "cls": t["cls"],
                    "name": t["name"]
                }
            else:
                # existing session gets updated
                sess = self.sessions[tid]
                sess["last_seen"] = timestamp
                sess["bbox"] = t["bbox"]
                sess["cls"] = t["cls"]
                sess["name"] = t["name"]

        # find sessions that have disappeared and remove them
        for tid, sess in list(self.sessions.items()):
            if tid not in active_ids:
                if timestamp - sess["last_seen"] > self.disappearance_timeout:
                    completed.append({
                        "track_id": tid,
                        "start_time": sess["start_time"],
                        "end_time": sess["last_seen"],
                        "duration": sess["last_seen"] - sess["start_time"],
                        "bbox": sess["bbox"],
                        "cls": sess["cls"],
                        "name": sess["name"]
                    })
                    del self.sessions[tid]

        return completed
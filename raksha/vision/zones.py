"""Zone counting + dwell. Zones are polygons in normalized coords [(x,y)...]."""
import time
import cv2
import numpy as np


class ZoneCounter:
    def __init__(self, zones):
        self.zones = zones  # {name: [(x,y)...]}
        self.enter = {}  # (zone, track_id) -> timestamp

    def count(self, dets, shape):
        h, w = shape[:2]
        out = {}
        now = time.time()
        for name, poly in self.zones.items():
            pts = (np.array(poly) * [w, h]).astype(int)
            ids = []
            for d in dets:
                if d["id"] is None:
                    continue
                x1, y1, x2, y2 = d["xyxy"]
                cx, cy = (x1 + x2) / 2, y2  # feet point
                if cv2.pointPolygonTest(pts, (cx, cy), False) >= 0:
                    ids.append(d["id"])
                    self.enter.setdefault((name, d["id"]), now)
            dwell = {i: now - self.enter[(name, i)] for i in ids}
            out[name] = {"count": len(ids), "ids": ids, "dwell_s": dwell}
        return out

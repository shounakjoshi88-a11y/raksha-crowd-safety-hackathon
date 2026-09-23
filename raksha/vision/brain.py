"""Crowd brain: density + Farneback flow (stillness, counterflow, entropy) -> stampede risk + alerts."""
import time
import cv2
import numpy as np


class CrowdBrain:
    def __init__(self, area_m2=50.0):
        self.prev = None
        self.alerts = []
        self.area = area_m2

    def update(self, frame, count):
        small = cv2.resize(frame, (320, 180))
        gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
        density = count / self.area
        still, cf, ent = 1.0, 0.0, 0.0
        if self.prev is not None:
            flow = cv2.calcOpticalFlowFarneback(self.prev, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)
            mag, ang = cv2.cartToPolar(flow[..., 0], flow[..., 1])
            still = float(np.clip(1 - mag.mean() / 2.0, 0, 1))
            hist, _ = np.histogram(ang, bins=8, range=(0, 2 * np.pi))
            tot = hist.sum() + 1e-9
            p = hist / tot
            ent = float(-(p[p > 0] * np.log(p[p > 0] + 1e-9)).sum() / np.log(8))
            i1 = int(np.argmax(hist))
            cf = float(min(hist[i1], hist[(i1 + 4) % 8]) / tot * 2)
        self.prev = gray
        rho = float(np.clip(density / 5.0, 0, 1.5))
        risk = float(np.clip(rho * still * (1 + cf), 0, 1.5))
        level = "red" if risk > 0.6 else "yellow" if risk > 0.4 else "green"
        if level != "green":
            self.alerts.append({"level": level, "risk": round(risk, 2),
                                "density": round(density, 2), "time": time.time()})
            self.alerts = self.alerts[-50:]
        return {"density": round(density, 2), "risk": round(risk, 2), "level": level,
                "stillness": round(still, 2), "counterflow": round(cf, 2), "entropy": round(ent, 2)}

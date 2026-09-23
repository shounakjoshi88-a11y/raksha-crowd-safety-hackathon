"""Per-track attributes, Chinese-VMS style: top/bottom clothing color, direction, speed.

Color lessons from our own research notes (Dahua-style top/bottom split):
central-region sampling only (full-width bands catch sky/arms), achromatic
check before hue, mean over median for washed daylight cloth.
"""
import cv2
import numpy as np


def _classify(hsv):
    mh, ms, mv = [float(np.mean(hsv[:, :, i])) for i in range(3)]
    if mv < 60:
        return "black"
    if ms < 45:
        return "white" if mv > 140 else "gray"
    if mh < 10 or mh > 160:
        return "red"
    if mh < 25:
        return "orange"
    if mh < 38:
        return "yellow"
    if mh < 78:
        return "green"
    if mh < 100:
        return "cyan"
    if mh < 132:
        return "blue"
    return "purple"


def _band(frame, xyxy, y0, y1):
    x1, y1_, x2, y2 = [int(v) for v in xyxy]
    h, w = frame.shape[:2]
    x1, y1_ = max(0, x1), max(0, y1_)
    x2, y2 = min(w, x2), min(h, y2)
    bh = y2 - y1_
    if bh < 20 or x2 - x1 < 10:
        return None
    cx0 = x1 + int((x2 - x1) * 0.25)
    cx1 = x2 - int((x2 - x1) * 0.25)
    crop = frame[y1_ + int(bh * y0):y1_ + int(bh * y1), cx0:cx1]
    if crop.size == 0:
        return None
    return cv2.cvtColor(crop, cv2.COLOR_BGR2HSV)


def top_color(frame, xyxy):
    hsv = _band(frame, xyxy, 0.25, 0.55)
    return _classify(hsv) if hsv is not None else "unknown"


def bottom_color(frame, xyxy):
    hsv = _band(frame, xyxy, 0.60, 0.92)
    return _classify(hsv) if hsv is not None else "unknown"


def direction(trail, fps=15.0):
    """Compass direction + px/s from trail deque of (x, y)."""
    if len(trail) < 5:
        return "still", 0.0
    x0, y0 = trail[0]
    x1, y1 = trail[-1]
    dx, dy = x1 - x0, y1 - y0
    dist = float(np.hypot(dx, dy))
    if dist < 5:
        return "still", 0.0
    ang = float(np.degrees(np.arctan2(-dy, dx)))  # y down, so flip; 0=E, 90=N
    dirs = ["E", "NE", "N", "NW", "W", "SW", "S", "SE"]
    label = dirs[int(((ang + 360) % 360 + 22.5) // 45) % 8]
    speed = dist / max(len(trail) / fps, 1e-3)
    return label, round(speed, 1)

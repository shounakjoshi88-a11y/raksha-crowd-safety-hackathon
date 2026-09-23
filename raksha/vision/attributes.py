"""Per-track attributes, Chinese-VMS style: top clothing color, direction, speed."""
import cv2
import numpy as np


def top_color(frame, xyxy):
    """Dominant torso color name from HSV. Torso = upper-middle band of box."""
    x1, y1, x2, y2 = [int(v) for v in xyxy]
    h, w = frame.shape[:2]
    x1, y1 = max(0, x1), max(0, y1)
    x2, y2 = min(w, x2), min(h, y2)
    bh = y2 - y1
    if bh < 20 or x2 - x1 < 10:
        return "unknown"
    torso = frame[y1 + int(bh * 0.2):y1 + int(bh * 0.55), x1:x2]
    if torso.size == 0:
        return "unknown"
    hsv = cv2.cvtColor(torso, cv2.COLOR_BGR2HSV)
    mh, ms, mv = [float(np.median(hsv[:, :, i])) for i in range(3)]
    if mv < 50:
        return "black"
    if ms < 40:
        return "white" if mv > 180 else "gray"
    if mh < 10 or mh > 165:
        return "red"
    if mh < 25:
        return "orange"
    if mh < 35:
        return "yellow"
    if mh < 80:
        return "green"
    if mh < 100:
        return "cyan"
    if mh < 130:
        return "blue"
    return "purple"


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

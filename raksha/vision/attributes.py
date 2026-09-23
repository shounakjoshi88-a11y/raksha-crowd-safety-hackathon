"""Part-based body attributes, real measured color (no hardcoded guesses).

Research grounding: rigid head/torso/legs split is the efficient classic
(Zhu 15-patch, Feris body parsing); dominant color via k-means on small
central crops (algolia/color-extractor pipeline: downscale, center crop,
cluster, largest wins). Colors recomputed at most every 15 frames per
track and cached, because clothing does not change frame to frame.
"""
import cv2
import numpy as np

PARTS = (("head", 0.00, 0.20), ("torso", 0.20, 0.58), ("legs", 0.58, 1.00))


def part_boxes(xyxy):
    """Split person box into head/torso/legs (x1, y1, x2, y2) dict."""
    x1, y1, x2, y2 = [int(v) for v in xyxy]
    h = y2 - y1
    if h <= 0:
        return {}
    return {name: (x1, y1 + int(h * a), x2, y1 + int(h * b)) for name, a, b in PARTS}


def dominant_bgr(crop):
    """Largest k-means cluster (k=2) on a small central crop. Returns (B, G, R)."""
    h, w = crop.shape[:2]
    cx0, cx1 = int(w * 0.25), int(w * 0.75)
    cy0, cy1 = int(h * 0.25), int(h * 0.75)
    small = cv2.resize(crop[cy0:cy1, cx0:cx1], (40, 40), interpolation=cv2.INTER_AREA)
    data = small.reshape(-1, 3).astype(np.float32)
    _, _, centers = cv2.kmeans(data, 2, None,
                               (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 8, 1.0),
                               2, cv2.KMEANS_PP_CENTERS)
    # largest cluster wins
    d = ((data[:, None, :] - centers[None, :, :]) ** 2).sum(axis=2).argmin(axis=1)
    best = int(np.bincount(d).argmax())
    return tuple(int(v) for v in centers[best][::-1])  # BGR ints


def name_of_bgr(bgr):
    """Nearest of 11 basic colors in HSV space (fast, no tables)."""
    arr = np.uint8([[list(bgr)]])
    h, s, v = [float(x) for x in cv2.cvtColor(arr, cv2.COLOR_BGR2HSV)[0][0]]
    if v < 60:
        return "black"
    if s < 45:
        return "white" if v > 140 else "gray"
    if h < 10 or h > 160:
        return "red"
    if h < 25:
        return "orange"
    if h < 38:
        return "yellow"
    if h < 78:
        return "green"
    if h < 100:
        return "cyan"
    if h < 132:
        return "blue"
    return "purple"


def hex_of_bgr(bgr):
    r, g, b = int(bgr[2]), int(bgr[1]), int(bgr[0])
    return "#%02X%02X%02X" % (r, g, b)


def part_colors(frame, xyxy):
    """Measured color per body part: {part: (bgr, name, hex)}. Safe on tiny boxes."""
    H, W = frame.shape[:2]
    out = {}
    for name, (x1, y1, x2, y2) in part_boxes(xyxy).items():
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(W, x2), min(H, y2)
        if x2 - x1 < 8 or y2 - y1 < 8:
            continue
        bgr = dominant_bgr(frame[y1:y2, x1:x2])
        out[name] = (bgr, name_of_bgr(bgr), hex_of_bgr(bgr))
    return out


def parts_info(frame, xyxy):
    """Merged per-part record for overlay: {part: {box, bgr, name, hex}}."""
    boxes = part_boxes(xyxy)
    cols = part_colors(frame, xyxy)
    out = {}
    for name, box in boxes.items():
        if name in cols:
            bgr, nm, hx = cols[name]
            out[name] = {"box": box, "bgr": bgr, "name": nm, "hex": hx}
    return out


def top_color(frame, xyxy):
    pc = part_colors(frame, xyxy)
    return pc["torso"][1] if "torso" in pc else "unknown"


def bottom_color(frame, xyxy):
    pc = part_colors(frame, xyxy)
    return pc["legs"][1] if "legs" in pc else "unknown"


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

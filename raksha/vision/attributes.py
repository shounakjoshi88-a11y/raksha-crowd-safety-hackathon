"""Part-based body attributes with properly researched color science.

Deep-dive findings (papers + repos: DeepMAR/RAP part taxonomy, algolia
color-extractor, uniform_color_detect, Yang&Yu clothing segmentation):
1. k=3 (shirt + trouser + background), NOT k=2. k=2 merges background into
   clothing and the largest cluster is often the wall behind the person.
2. Reject background: clusters near the crop border color are scenery.
3. Reject skin: HSV skin mask, else arms/face pollute torso color.
4. IQR-clean the surviving pixels, take the median (outlier-proof).
5. Name in CIELAB with Delta-E against 11 basic colors, monochrome gated
   on chroma first (algolia hard_monochrome pattern).
6. Temporal: per-track cache every 15 frames + running average over last 3
   measurements, because cloth color must not flicker frame to frame.

Part taxonomy follows RAP: head-shoulder / upper-body / lower-body.
"""
import cv2
import numpy as np

PARTS = (("head", 0.00, 0.20), ("torso", 0.20, 0.58), ("legs", 0.58, 1.00))


def name_of_bgr(bgr):
    """Basic color name from measured BGR. HSV sectors on the *measured*
    (background/skin-cleaned) color; pink/brown/maroon split by S/V."""
    arr = np.uint8([[[int(bgr[0]), int(bgr[1]), int(bgr[2])]]])
    h, s, v = [float(x) for x in cv2.cvtColor(arr, cv2.COLOR_BGR2HSV)[0][0]]
    if v < 70:
        return "black"
    if s < 40:
        if v > 180:
            return "white"
        return "gray"
    is_red = h < 8 or h > 155
    if is_red:
        if v > 150 and s < 130:
            return "pink"
        if v < 110:
            return "maroon"
        return "red"
    if h < 20:
        return "brown" if v < 130 else "orange"
    if h < 32:
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


def _skin_mask(bgr_crop):
    hsv = cv2.cvtColor(bgr_crop, cv2.COLOR_BGR2HSV)
    return cv2.inRange(hsv, np.array([0, 30, 60]), np.array([20, 255, 255])) > 0


def measure_color(bgr_crop):
    """Dominant clothing color of a part crop. Returns (bgr, name, hex) or None."""
    h, w = bgr_crop.shape[:2]
    if h < 8 or w < 8:
        return None
    cx0, cx1 = int(w * 0.35), int(w * 0.65)
    cy0, cy1 = int(h * 0.25), int(h * 0.75)
    roi = cv2.resize(bgr_crop[cy0:cy1, cx0:cx1], (40, 40), interpolation=cv2.INTER_AREA)
    lab = cv2.cvtColor(roi, cv2.COLOR_BGR2LAB).reshape(-1, 3).astype(np.float32)
    _, _, centers = cv2.kmeans(lab, 3, None,
                               (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 8, 1.0),
                               2, cv2.KMEANS_PP_CENTERS)
    d = ((lab[:, None, :] - centers[None, :, :]) ** 2).sum(axis=2).argmin(axis=1)
    counts = np.bincount(d, minlength=3)
    # background prototype = border ring mean in Lab
    ring = np.concatenate([lab[:40 * 3], lab[-40 * 3:], lab[::40][:40], lab[39::40][:40]])
    bg = ring.mean(axis=0)
    # skin fraction per cluster (computed in BGR space)
    bgr_flat = roi.reshape(-1, 3)
    skin = _skin_mask(roi).reshape(-1)
    best, best_n = None, -1
    best_frac = 0.0
    for k in range(3):
        m = d == k
        n = int(m.sum())
        if n < 40:
            continue
        clab = centers[k]
        if float(((clab - bg) ** 2).sum()) < 12.0 ** 2:
            continue  # scenery, not clothing
        if n > 0 and float(skin[m].mean()) > 0.5:
            continue  # arm/face skin, not clothing
        if n > best_n:
            best, best_n = k, n
            best_frac = n / max(len(d), 1)
    if best is None:  # fallback: largest non-background cluster
        order = sorted(range(3), key=lambda k: -int((d == k).sum()))
        for k in order:
            if float(((centers[k] - bg) ** 2).sum()) >= 12.0 ** 2:
                best = k
                best_frac = int((d == k).sum()) / max(len(d), 1)
                break
        if best is None:
            return None
    if best_frac < 0.45:
        return None  # no dominant clothing color; honest unknown beats wrong guess
    sel = lab[d == best]
    # IQR-clean per channel, then median (outlier-proof representative)
    clean = []
    for c in range(3):
        v = sel[:, c]
        q1, q3 = np.percentile(v, 25), np.percentile(v, 75)
        iqr = q3 - q1
        keep = v[(v >= q1 - 1.5 * iqr) & (v <= q3 + 1.5 * iqr)]
        clean.append(float(np.median(keep)) if keep.size else float(np.median(v)))
    lab_med = np.array([[[int(round(v)) for v in clean]]], dtype=np.uint8)
    bgr_med = cv2.cvtColor(lab_med, cv2.COLOR_LAB2BGR)[0][0]
    bgr = (int(bgr_med[0]), int(bgr_med[1]), int(bgr_med[2]))
    return bgr, name_of_bgr(bgr), hex_of_bgr(bgr)


def part_boxes(xyxy):
    """Split person box into head/torso/legs (x1, y1, x2, y2) dict."""
    x1, y1, x2, y2 = [int(v) for v in xyxy]
    h = y2 - y1
    if h <= 0:
        return {}
    return {name: (x1, y1 + int(h * a), x2, y1 + int(h * b)) for name, a, b in PARTS}


def parts_info(frame, xyxy):
    """Measured color per body part: {part: {box, bgr, name, hex}}."""
    H, W = frame.shape[:2]
    out = {}
    for name, (x1, y1, x2, y2) in part_boxes(xyxy).items():
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(W, x2), min(H, y2)
        if x2 - x1 < 8 or y2 - y1 < 8:
            continue
        m = measure_color(frame[y1:y2, x1:x2])
        if m is None:
            continue
        bgr, nm, hx = m
        out[name] = {"box": (x1, y1, x2, y2), "bgr": bgr, "name": nm, "hex": hx}
    return out


def top_color(frame, xyxy):
    pc = parts_info(frame, xyxy)
    return pc["torso"]["name"] if "torso" in pc else "unknown"


def bottom_color(frame, xyxy):
    pc = parts_info(frame, xyxy)
    return pc["legs"]["name"] if "legs" in pc else "unknown"


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

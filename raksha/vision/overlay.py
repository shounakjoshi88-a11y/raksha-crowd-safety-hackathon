"""Chinese-VMS style overlay: box plus attached multi-line attribute panel."""
import cv2

BOX = (0, 229, 204)
BOX_VEH = (255, 150, 0)
TRAIL = (255, 59, 92)
PANEL_BG = (10, 10, 10)
PANEL_FG = (240, 240, 240)
FONT = cv2.FONT_HERSHEY_SIMPLEX


def draw_panel(frame, x, y, lines, scale=0.45, side="right"):
    """Dark label stack at (x, y). Returns bottom y."""
    fs, th, pad, lh = scale, 1, 5, 15
    widths = [cv2.getTextSize(t, FONT, fs, th)[0][0] for t in lines]
    bw, bh = max(widths) + pad * 2, len(lines) * lh + pad * 2
    H, W = frame.shape[:2]
    if side == "left":
        x = x - bw - 8
    if x + bw > W:
        x = max(0, x - bw - 8)
    if x < 0:
        x = 0
    y = max(0, min(y, H - bh))
    cv2.rectangle(frame, (x, y), (x + bw, y + bh), PANEL_BG, -1)
    for i, t in enumerate(lines):
        cv2.putText(frame, t, (x + pad, y + pad + (i + 1) * lh - 4), FONT, fs, PANEL_FG, th, cv2.LINE_AA)
    return y + bh


def draw_track(frame, det, trail, extra_lines=None, box_color=None, full_panel_h=90, compact=False):
    x1, y1, x2, y2 = [int(v) for v in det["xyxy"]]
    color = box_color or (BOX_VEH if det.get("cls", 0) != 0 else BOX)
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
    for i in range(1, len(trail)):
        cv2.line(frame, trail[i - 1], trail[i], TRAIL, 2)
    if y2 - y1 < full_panel_h or det["id"] is None:
        cv2.putText(frame, str(det["id"]), (x1, max(0, y1 - 6)),
                    FONT, 0.55, color, 2, cv2.LINE_AA)
        return
    lines = [f"{det.get('label', 'ID')} {det['id']}"]
    if extra_lines:
        lines += extra_lines[:1] if compact else extra_lines
    fs, th, pad, lh = 0.45, 1, 5, 15
    widths = [cv2.getTextSize(t, FONT, fs, th)[0][0] for t in lines]
    bw, bh = max(widths) + pad * 2, len(lines) * lh + pad * 2
    H, W = frame.shape[:2]
    # anchor above the box so bodies stay visible; fall back to a free side
    px, py = x1, y1 - bh - 6
    if py < 0:
        try:
            side = "left" if int(det["id"]) % 2 else "right"
        except (TypeError, ValueError):
            side = "right"
        px = x1 - bw - 8 if side == "left" else x2 + 6
        py = y1
    if px + bw > W:
        px = max(0, W - bw)
    if px < 0:
        px = 0
    py = max(0, min(py, H - bh))
    cv2.rectangle(frame, (px, py), (px + bw, py + bh), PANEL_BG, -1)
    for i, t in enumerate(lines):
        cv2.putText(frame, t, (px + pad, py + pad + (i + 1) * lh - 4), FONT, fs, PANEL_FG, th, cv2.LINE_AA)

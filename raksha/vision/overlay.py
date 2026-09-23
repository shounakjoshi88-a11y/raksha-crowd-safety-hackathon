"""Chinese-VMS style overlay: box plus attached multi-line attribute panel."""
import cv2

BOX = (0, 229, 204)
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


def draw_track(frame, det, trail, extra_lines=None):
    x1, y1, x2, y2 = [int(v) for v in det["xyxy"]]
    cv2.rectangle(frame, (x1, y1), (x2, y2), BOX, 2)
    for i in range(1, len(trail)):
        cv2.line(frame, trail[i - 1], trail[i], TRAIL, 2)
    lines = [f"ID {det['id']}"]
    if extra_lines:
        lines += extra_lines
    try:
        side = "left" if int(det["id"]) % 2 else "right"
    except (TypeError, ValueError):
        side = "right"
    if side == "left":
        draw_panel(frame, x1, y1, lines, side="left")
    else:
        draw_panel(frame, x2 + 6, y1, lines)

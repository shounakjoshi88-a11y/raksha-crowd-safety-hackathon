"""Chinese-VMS style overlay: part boxes plus measured-color panels.

Panels anchor above the box so bodies stay visible. Swatch squares show the
measured color, hex plus name beside it. Crowded frames fall back to compact
panels automatically.
"""
import cv2

BOX = (0, 229, 204)
BOX_VEH = (255, 150, 0)
PART_COLORS = {"head": (0, 255, 255), "torso": (0, 229, 204), "legs": (255, 102, 178)}
PANEL_BG = (10, 10, 10)
PANEL_FG = (240, 240, 240)
FONT = cv2.FONT_HERSHEY_SIMPLEX
FS, TH, PAD, LH = 0.45, 1, 5, 15
SW = 12  # swatch square size


def _text_row(frame, px, py, text, xoff=0):
    cv2.putText(frame, text, (px + PAD + xoff, py), FONT, FS, PANEL_FG, TH, cv2.LINE_AA)


def draw_person(frame, det, trail, parts, zone_line, compact=False):
    """parts: {name: {'box': (x1,y1,x2,y2), 'bgr': (b,g,r), 'name': str, 'hex': str}}."""
    x1, y1, x2, y2 = [int(v) for v in det["xyxy"]]
    cv2.rectangle(frame, (x1, y1), (x2, y2), BOX, 2)
    for i in range(1, len(trail)):
        cv2.line(frame, trail[i - 1], trail[i], (255, 59, 92), 2)
    if y2 - y1 < (130 if compact else 60) or det["id"] is None:
        cv2.putText(frame, str(det["id"]), (x1, max(0, y1 - 6)),
                    FONT, 0.55, BOX, 2, cv2.LINE_AA)
        return
    H, W = frame.shape[:2]
    for pname, p in parts.items():
        bx1, by1, bx2, by2 = [int(v) for v in p["box"]]
        bx1, by1 = max(0, bx1), max(0, by1)
        bx2, by2 = min(W, bx2), min(H, by2)
        pc = PART_COLORS.get(pname, BOX)
        cv2.rectangle(frame, (bx1, by1), (bx2, by2), pc, 2)
        cv2.putText(frame, pname.upper(), (bx1, max(0, by1 - 4)),
                    FONT, 0.4, pc, 1, cv2.LINE_AA)
    rows = [("t", f"ID {det['id']}")]
    if "torso" in parts:
        t = parts["torso"]
        rows.append(("s", f"TORSO {t['hex']} {t['name']}", t["bgr"]))
    if not compact and "legs" in parts:
        lg = parts["legs"]
        rows.append(("s", f"LEGS {lg['hex']} {lg['name']}", lg["bgr"]))
    if not compact:
        rows.append(("t", zone_line))
    widths = []
    for kind, text, *rest in rows:
        w = cv2.getTextSize(text, FONT, FS, TH)[0][0]
        widths.append(w + (SW + 6 if kind == "s" else 0))
    bw, bh = max(widths) + PAD * 2, len(rows) * LH + PAD * 2
    px, py = x1, y1 - bh - 6
    if py < 0:
        px = x2 + 6 if int(det["id"] or 0) % 2 == 0 else x1 - bw - 8
        py = y1
    px = max(0, min(px, W - bw))
    py = max(0, min(py, H - bh))
    cv2.rectangle(frame, (px, py), (px + bw, py + bh), PANEL_BG, -1)
    for i, (kind, text, *rest) in enumerate(rows):
        ty = py + PAD + (i + 1) * LH - 4
        if kind == "s":
            cv2.rectangle(frame, (px + PAD, ty - SW + 3), (px + PAD + SW, ty + 3), rest[0], -1)
            _text_row(frame, px, ty, text, SW + 6)
        else:
            _text_row(frame, px, ty, text)


def draw_panel(frame, x, y, lines, scale=0.45, side="right"):
    """Legacy simple panel (vehicles)."""
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
    """Vehicle/simple path: colored box plus small dark panel.
    In compact (crowded) mode, boxes under 130px get an ID tag only."""
    x1, y1, x2, y2 = [int(v) for v in det["xyxy"]]
    color = box_color or (BOX_VEH if det.get("cls", 0) != 0 else BOX)
    cv2.rectangle(frame, (x1, y1), (x2, y2), color, 2)
    for i in range(1, len(trail)):
        cv2.line(frame, trail[i - 1], trail[i], (255, 59, 92), 2)
    if y2 - y1 < (130 if compact else full_panel_h) or det["id"] is None:
        cv2.putText(frame, str(det["id"]), (x1, max(0, y1 - 6)),
                    FONT, 0.55, color, 2, cv2.LINE_AA)
        return
    lines = [f"{det.get('label', 'ID')} {det['id']}"]
    if extra_lines:
        lines += extra_lines[:1] if compact else extra_lines
    try:
        side = "left" if int(det["id"]) % 2 else "right"
    except (TypeError, ValueError):
        side = "right"
    if side == "left":
        draw_panel(frame, x1, y1, lines, side="left")
    else:
        draw_panel(frame, x2 + 6, y1, lines)

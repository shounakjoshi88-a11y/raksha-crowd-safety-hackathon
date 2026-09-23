"""Video sources for Raksha: webcam index, file path, or RTSP URL. Yields BGR frames at capped width."""
import cv2


def open_source(src, width=1280):
    cap = cv2.VideoCapture(src)
    if not cap.isOpened():
        raise RuntimeError(f"cannot open source: {src}")
    return cap


def read_frame(cap, width=1280):
    ok, frame = cap.read()
    if not ok:
        return None
    h, w = frame.shape[:2]
    if w > width:
        scale = width / w
        frame = cv2.resize(frame, (width, int(h * scale)), interpolation=cv2.INTER_LINEAR)
    return frame

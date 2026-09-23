"""Privacy helpers: blur faces in stored frames. Raw faces never hit disk unblurred."""
import cv2


def blur_faces(frame, faces, k=(51, 51)):
    out = frame.copy()
    for fc in faces:
        x1, y1, x2, y2 = fc["bbox"]
        roi = out[y1:y2, x1:x2]
        if roi.size:
            out[y1:y2, x1:x2] = cv2.GaussianBlur(roi, k, 0)
    return out

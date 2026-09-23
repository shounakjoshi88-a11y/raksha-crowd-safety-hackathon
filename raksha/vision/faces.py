"""Face engine: buffalo_s detect + 512-D ArcFace + age/gender + quality gate."""
import cv2
import numpy as np
from insightface.app import FaceAnalysis


class FaceEngine:
    def __init__(self, pack="buffalo_s", ctx_id=0, det_size=(640, 640), det_thresh=0.5):
        self.app = FaceAnalysis(name=pack, providers=["CUDAExecutionProvider", "CPUExecutionProvider"])
        self.app.prepare(ctx_id=ctx_id, det_size=det_size, det_thresh=det_thresh)

    @staticmethod
    def blur_score(crop):
        g = cv2.cvtColor(crop, cv2.COLOR_BGR2GRAY)
        return float(cv2.Laplacian(g, cv2.CV_64F).var())

    def get_faces(self, frame, min_size=60, min_blur=40.0):
        """Returns list of dicts: bbox, det_score, embedding(512,), age, gender, blur."""
        out = []
        h, w = frame.shape[:2]
        for f in self.app.get(frame):
            x1, y1, x2, y2 = [int(v) for v in f.bbox]
            x1, y1 = max(0, x1), max(0, y1)
            x2, y2 = min(w, x2), min(h, y2)
            if min(x2 - x1, y2 - y1) < min_size:
                continue
            blur = self.blur_score(frame[y1:y2, x1:x2])
            if blur < min_blur:
                continue
            out.append({"bbox": (x1, y1, x2, y2), "det_score": float(f.det_score),
                        "embedding": np.asarray(f.normed_embedding, dtype=np.float32),
                        "age": int(f.age), "gender": "M" if f.sex == 1 else "F", "blur": blur})
        return out

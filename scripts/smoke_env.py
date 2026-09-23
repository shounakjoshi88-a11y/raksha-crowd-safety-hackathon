"""Phase 0 acceptance: GPU + YOLO detect + InsightFace embed. Run: python scripts/smoke_env.py"""
import time, cv2, numpy as np, torch
print("torch", torch.__version__, "cuda:", torch.cuda.is_available(), torch.cuda.get_device_name(0))

from ultralytics import YOLO
m = YOLO("yolov8s.pt")
cap = cv2.VideoCapture(0)
ok, frame = cap.read()
cap.release()
assert ok, "webcam read failed"
t = time.time()
r = m.predict(frame, device=0, verbose=False)[0]
dt = time.time() - t
n = len([c for c in r.boxes.cls.tolist() if int(c) == 0]) if r.boxes is not None else 0
print(f"YOLOv8s GPU: {dt*1000:.0f}ms persons={n}")

from insightface.app import FaceAnalysis
app = FaceAnalysis(name="buffalo_s", providers=["CUDAExecutionProvider", "CPUExecutionProvider"])
app.prepare(ctx_id=0, det_size=(640, 640))
t = time.time()
faces = app.get(frame)
dt = time.time() - t
print(f"buffalo_s: {dt*1000:.0f}ms faces={len(faces)}", end="")
if faces:
    print(f" emb={faces[0].normed_embedding.shape} age={faces[0].age} gender={'M' if faces[0].sex==1 else 'F'}")
else:
    print(" (no face in webcam frame, show your face and rerun)")
print("SMOKE OK")

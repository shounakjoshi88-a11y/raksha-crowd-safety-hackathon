"""Enroll: python scripts/enroll.py <Name> [shots]. Captures quality faces from webcam into gallery/gallery.*"""
import os, sys
import cv2
sys.path.insert(0, "D:/Q_project")
from raksha.vision.ingest import open_source, read_frame
from raksha.vision.faces import FaceEngine
from raksha.vision.gallery import Gallery

name = sys.argv[1] if len(sys.argv) > 1 else "Person01"
shots = int(sys.argv[2]) if len(sys.argv) > 2 else 5
os.makedirs("D:/Q_project/gallery", exist_ok=True)
prefix = "D:/Q_project/gallery/gallery"

try:
    gal = Gallery.load(prefix)
except Exception:
    gal = Gallery()
eng = FaceEngine()
cap = open_source(0)
got, n = 0, 0
while got < shots and n < 300:
    f = read_frame(cap)
    n += 1
    if f is None or n % 5:
        continue
    faces = eng.get_faces(f)
    if not faces:
        continue
    best = max(faces, key=lambda x: x["blur"])
    gal.add(name, best["embedding"], {"age": best["age"], "gender": best["gender"]})
    got += 1
    print(f"shot {got}/{shots} blur={best['blur']:.0f} age={best['age']}")
cap.release()
gal.save(prefix)
print(f"enrolled {name}, gallery size={gal.index.ntotal}")

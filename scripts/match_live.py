"""Live match: python scripts/match_live.py [--frames N] [--no-show]. 3-frame vote smoothing."""
import sys, argparse
from collections import deque
import cv2
sys.path.insert(0, "D:/Q_project")
from raksha.vision.ingest import open_source, read_frame
from raksha.vision.faces import FaceEngine
from raksha.vision.gallery import Gallery
from raksha.vision.dossier import Dossier

ap = argparse.ArgumentParser()
ap.add_argument("--frames", type=int, default=0)
ap.add_argument("--no-show", action="store_true")
a = ap.parse_args()

gal = Gallery.load("D:/Q_project/gallery/gallery")
eng = FaceEngine()
cap = open_source(0)
votes, dossiers, n = deque(maxlen=3), {}, 0
while True:
    f = read_frame(cap)
    if f is None:
        break
    n += 1
    if n % 3 == 0:
        for fc in eng.get_faces(f):
            nm, sim, meta = gal.search(fc["embedding"])
            votes.append(nm)
            label = nm if nm and list(votes).count(nm) >= 2 else f"unknown?{sim:.2f}"
            gid = nm or "stranger"
            d = dossiers.setdefault(gid, Dossier(gid, nm))
            d.touch(snapshot=None)
            x1, y1, x2, y2 = fc["bbox"]
            cv2.rectangle(f, (x1, y1), (x2, y2), (0, 229, 204), 2)
            cv2.putText(f, f"{label} {sim:.2f} {fc['age']}{fc['gender']}",
                        (x1, y1 - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 229, 204), 2)
    if not a.no_show:
        cv2.imshow("Raksha Match (q to quit)", f)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    if a.frames and n >= a.frames:
        break
cap.release()
cv2.destroyAllWindows()
print("dossiers:", {k: v.card() for k, v in dossiers.items()})
print("done")

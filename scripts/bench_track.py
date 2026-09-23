"""Warm FPS benchmark: python scripts/bench_track.py [source] [frames]. Default webcam 0, 120 frames."""
import sys, time
sys.path.insert(0, "D:/Q_project")
from raksha.vision.ingest import open_source, read_frame
from raksha.vision.tracker import PersonTracker

src = sys.argv[1] if len(sys.argv) > 1 else 0
try:
    src = int(src)
except ValueError:
    pass
n = int(sys.argv[2]) if len(sys.argv) > 2 else 120

cap = open_source(src)
trk = PersonTracker()
# warmup
for _ in range(5):
    f = read_frame(cap)
    if f is None:
        break
    trk.update(f)
ids, persons, t0 = set(), 0, time.time()
done = 0
for _ in range(n):
    f = read_frame(cap)
    if f is None:
        break
    for d in trk.update(f):
        persons += 1
        if d["id"] is not None:
            ids.add(d["id"])
    done += 1
dt = time.time() - t0
cap.release()
print(f"frames={done} fps={done/dt:.1f} unique_ids={len(ids)} person_dets={persons}")

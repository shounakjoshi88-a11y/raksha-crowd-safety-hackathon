"""Live wall: python scripts/live.py [source] [--save out.mp4] [--no-show].
Overlays IDs, trails, zone counts, dwell, FPS. Zones default to left/right halves."""
import sys, time, argparse
from collections import deque
import cv2
sys.path.insert(0, "D:/Q_project")
from raksha.vision.ingest import open_source, read_frame
from raksha.vision.tracker import PersonTracker
from raksha.vision.zones import ZoneCounter

ap = argparse.ArgumentParser()
ap.add_argument("source", nargs="?", default="0")
ap.add_argument("--save", default=None)
ap.add_argument("--no-show", action="store_true")
ap.add_argument("--frames", type=int, default=0)
a = ap.parse_args()
try:
    src = int(a.source)
except ValueError:
    src = a.source

cap = open_source(src)
trk = PersonTracker()
zones = ZoneCounter({"Gate": [(0, 0), (0.5, 0), (0.5, 1), (0, 1)],
                     "Stage": [(0.5, 0), (1, 0), (1, 1), (0.5, 1)]})
trails, writer = {}, None
t0, frames = time.time(), 0
fps = 0.0

while True:
    f = read_frame(cap, width=1280)
    if f is None:
        break
    dets = trk.update(f)
    zc = zones.count(dets, f.shape)
    H, W = f.shape[:2]
    for d in dets:
        if d["id"] is None:
            continue
        x1, y1, x2, y2 = map(int, d["xyxy"])
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        tr = trails.setdefault(d["id"], deque(maxlen=30))
        tr.append((cx, cy))
        cv2.rectangle(f, (x1, y1), (x2, y2), (0, 229, 204), 2)
        cv2.putText(f, f"ID {d['id']}", (x1, y1 - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 229, 204), 2)
        for i in range(1, len(tr)):
            cv2.line(f, tr[i - 1], tr[i], (255, 59, 92), 2)
    # zone divider + panel
    cv2.line(f, (W // 2, 0), (W // 2, H), (120, 120, 120), 1)
    y = 30
    for name, z in zc.items():
        cv2.putText(f, f"{name}: {z['count']}  max-dwell {max(z['dwell_s'].values(), default=0):.0f}s",
                    (10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)
        y += 32
    frames += 1
    if frames % 10 == 0:
        fps = frames / (time.time() - t0)
    cv2.putText(f, f"{fps:.1f} FPS", (W - 160, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    if writer is None and a.save:
        writer = cv2.VideoWriter(a.save, cv2.VideoWriter_fourcc(*"mp4v"), 20, (W, H))
    if writer:
        writer.write(f)
    if not a.no_show:
        cv2.imshow("Raksha Wall (q to quit)", f)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
    if a.frames and frames >= a.frames:
        break
cap.release()
if writer:
    writer.release()
cv2.destroyAllWindows()
print(f"done frames={frames} avg_fps={frames/(time.time()-t0):.1f}")

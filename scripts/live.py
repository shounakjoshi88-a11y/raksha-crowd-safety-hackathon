"""Live wall: python scripts/live.py [source] [--save out.mp4] [--no-show].
Overlays IDs, trails, zone counts, dwell, FPS. Zones default to left/right halves."""
import sys, time, argparse
from collections import deque
import cv2
sys.path.insert(0, "D:/Q_project")
from raksha.vision.ingest import open_source, read_frame
from raksha.vision.tracker import PersonTracker
from raksha.vision.zones import ZoneCounter
from raksha.vision.attributes import top_color, direction
from raksha.vision.overlay import draw_track

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
    persons = [d for d in dets if d["cls"] == 0]
    vehicles = [d for d in dets if d["cls"] != 0]
    zc = zones.count(persons, f.shape)
    H, W = f.shape[:2]
    zone_of, dwell_of = {}, {}
    for zname, z in zc.items():
        for tid in z["ids"]:
            zone_of[tid] = zname
            dwell_of[tid] = z["dwell_s"].get(tid, 0)
    for d in persons:
        if d["id"] is None:
            continue
        x1, y1, x2, y2 = map(int, d["xyxy"])
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        tr = trails.setdefault(d["id"], deque(maxlen=30))
        tr.append((cx, cy))
        dlbl, spd = direction(tr)
        extra = [f"top {top_color(f, d['xyxy'])}",
                 f"{zone_of.get(d['id'], '-')} {dwell_of.get(d['id'], 0):.0f}s {dlbl}"]
        draw_track(f, d, tr, extra, compact=len(dets) > 12)
    for d in vehicles:
        if d["id"] is None:
            continue
        x1, y1, x2, y2 = map(int, d["xyxy"])
        tr = trails.setdefault(("v", d["id"]), deque(maxlen=30))
        tr.append(((x1 + x2) // 2, (y1 + y2) // 2))
        dlbl, spd = direction(tr)
        draw_track(f, d, tr, [f"{dlbl} {spd}px/s"], compact=len(dets) > 12)
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

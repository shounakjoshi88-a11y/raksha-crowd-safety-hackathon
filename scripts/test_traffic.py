"""Traffic clip vehicle test + annotated frame."""
import sys, time
from collections import deque, Counter
import cv2
sys.path.insert(0, "D:/Q_project")
from raksha.vision.tracker import PersonTracker
from raksha.vision.overlay import draw_track, draw_person
from raksha.vision.attributes import direction, top_color, parts_info

cap = cv2.VideoCapture("D:/Q_project/assets/clips/traffic.mp4")
trk = PersonTracker()
pids, vids, kinds, n, t0, peak = set(), set(), Counter(), 0, time.time(), 0
trails = {}
while True:
    ok, f = cap.read()
    if not ok:
        break
    dets = trk.update(f)
    ps = [d for d in dets if d["cls"] == 0 and d["id"] is not None]
    vs = [d for d in dets if d["cls"] != 0 and d["id"] is not None]
    pids.update(d["id"] for d in ps)
    vids.update(d["id"] for d in vs)
    kinds.update(d["label"] for d in vs)
    peak = max(peak, len(ps) + len(vs))
    n += 1
    if n == 200:
        cmpct = len(dets) > 12
        for d in dets:
            if d["id"] is None:
                continue
            x1, y1, x2, y2 = map(int, d["xyxy"])
            tr = trails.setdefault((d["cls"], d["id"]), deque(maxlen=30))
            tr.append(((x1 + x2) // 2, (y1 + y2) // 2))
            if d["cls"] == 0:
                dl, _ = direction(tr)
                draw_person(f, d, tr, parts_info(f, d["xyxy"]), dl, compact=cmpct)
            else:
                dl, sp = direction(tr)
                draw_track(f, d, tr, [dl + " " + str(sp) + "px/s"], compact=cmpct)
        cv2.imwrite("D:/Q_project/assets/shots/traffic_0.jpg", f)
cap.release()
print("frames=%d fps=%.1f person_ids=%d vehicle_ids=%d peak=%d kinds=%s"
      % (n, n / (time.time() - t0), len(pids), len(vids), peak, dict(kinds)))

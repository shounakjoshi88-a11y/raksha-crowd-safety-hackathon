"""Indian CCTV clip test + annotated frames."""
import sys, time
from collections import deque
import cv2
sys.path.insert(0, "D:/Q_project")
from raksha.vision.tracker import PersonTracker
from raksha.vision.overlay import draw_person
from raksha.vision.attributes import direction, parts_info

for name, fr in (("india_station.mp4", 400), ("india_temple.mp4", 300)):
    cap = cv2.VideoCapture("D:/Q_project/assets/clips/" + name)
    trk = PersonTracker()
    ids, peak, n, t0 = set(), 0, 0, time.time()
    trails = {}
    while True:
        ok, f = cap.read()
        if not ok:
            break
        dets = trk.update(f)
        ps = [d for d in dets if d["cls"] == 0 and d["id"] is not None]
        ids.update(d["id"] for d in ps)
        peak = max(peak, len(ps))
        n += 1
        if n == fr:
            cmpct = len(dets) > 12
            for d in dets:
                if d["id"] is None:
                    continue
                x1, y1, x2, y2 = map(int, d["xyxy"])
                if d["cls"] != 0:
                    continue
                tr = trails.setdefault(d["id"], deque(maxlen=30))
                tr.append(((x1 + x2) // 2, (y1 + y2) // 2))
                dl, _ = direction(tr)
                draw_person(f, d, tr, parts_info(f, d["xyxy"]), dl, compact=cmpct)
            cv2.imwrite("D:/Q_project/assets/shots/" + name.split(".")[0] + ".jpg", f)
    cap.release()
    print("%s: frames=%d fps=%.1f unique_ids=%d peak=%d" % (name, n, n / (time.time() - t0), len(ids), peak))
print("shots saved")

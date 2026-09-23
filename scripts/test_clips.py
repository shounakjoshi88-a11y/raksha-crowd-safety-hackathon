"""Crowd clip test: python scripts/test_clips.py. Full pass per clip: IDs, peak, FPS + annotated frames."""
import os, sys, time
import cv2
sys.path.insert(0, "D:/Q_project")
from raksha.vision.tracker import PersonTracker

CLIPS = ["grand_central.mp4", "station_rush.mp4", "street_walk.ogv"]
os.makedirs("D:/Q_project/assets/shots", exist_ok=True)
trk = PersonTracker()
for name in CLIPS:
    path = f"D:/Q_project/assets/clips/{name}"
    cap = cv2.VideoCapture(path)
    ids, peak, n, t0, saved = set(), 0, 0, time.time(), 0
    boxes_drawn = 0
    while True:
        ok, f = cap.read()
        if not ok:
            break
        dets = trk.update(f)
        persons = [d for d in dets if d["id"] is not None]
        ids.update(d["id"] for d in persons)
        peak = max(peak, len(persons))
        n += 1
        if persons and saved < 2 and n > 30:
            for d in persons:
                x1, y1, x2, y2 = map(int, d["xyxy"])
                cv2.rectangle(f, (x1, y1), (x2, y2), (0, 229, 204), 2)
                cv2.putText(f, f"ID {d['id']}", (x1, y1 - 6), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 229, 204), 2)
                boxes_drawn += 1
            cv2.imwrite(f"D:/Q_project/assets/shots/{name}_{saved}.jpg", f)
            saved += 1
    cap.release()
    dt = time.time() - t0
    print(f"{name}: frames={n} fps={n/dt:.1f} unique_ids={len(ids)} peak_simultaneous={peak} boxes_drawn={boxes_drawn}")
print("shots saved")

"""FPS vs crowd load: per-frame person count bins across the three clips.
python scripts/bench_density.py [frames_per_clip]
Prints bucketed FPS + per-clip summary. Same PersonTracker pipeline as production.
"""
import sys, time, json
from collections import defaultdict

sys.path.insert(0, "D:/Q_project")
from raksha.vision.tracker import PersonTracker

import cv2

CLIPS = ["station_concourse.webm", "shibuya_crossing.webm", "india_temple.mp4"]
N = int(sys.argv[1]) if len(sys.argv) > 1 else 400
# person-count buckets (proxy for crowd load in frame)
BUCKETS = [(0, 5), (5, 9), (9, 13), (13, 10_000)]
LABELS = ["0-4", "5-8", "9-12", "13+"]

trk = PersonTracker()
# warmup on a black frame so first-compile cost is excluded
import numpy as np
trk.update(np.zeros((720, 1280, 3), np.uint8))

bin_frames = defaultdict(int)
bin_secs = defaultdict(float)
per_clip = {}

for name in CLIPS:
    path = f"D:/Q_project/assets/clips/{name}"
    cap = cv2.VideoCapture(path)
    n = dt_person = 0
    peak = 0
    t_clip = time.time()
    while n < N:
        ok, f = cap.read()
        if not ok:
            cap.release()
            # loop once for short clips to reach N
            cap = cv2.VideoCapture(path)
            ok, f = cap.read()
            if not ok:
                break
        t0 = time.time()
        dets = trk.update(f)
        dt = time.time() - t0
        persons = sum(1 for d in dets if d["cls"] == 0)
        peak = max(peak, persons)
        n += 1
        dt_person += dt
        # bin by instantaneous person count
        for lo, hi in BUCKETS:
            if lo <= persons < hi:
                bin_frames[(lo, hi)] += 1
                bin_secs[(lo, hi)] += dt
                break
    cap.release()
    clip_dt = time.time() - t_clip
    per_clip[name] = {"frames": n, "fps": round(n / clip_dt, 1),
                      "infer_fps": round(n / dt_person, 1) if dt_person else 0,
                      "peak_persons": peak}
    print(name, per_clip[name])

print("\nFPS by people-in-frame bucket (pooled, inference only):")
out = []
for (lo, hi), lab in zip(BUCKETS, LABELS):
    f, s = bin_frames[(lo, hi)], bin_secs[(lo, hi)]
    fps = round(f / s, 1) if s > 0 else None
    out.append({"bucket": lab, "frames": f, "fps": fps})
    print(f"  {lab:>7} persons: frames={f:4d} fps={fps}")

json.dump({"per_clip": per_clip, "buckets": out},
          open("D:/Q_project/gallery/bench_density.json", "w"), indent=2)
print("saved gallery/bench_density.json")

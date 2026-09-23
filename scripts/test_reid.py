"""ReID re-entry test: python scripts/test_reid.py. 30 live frames, 60 black (occlusion), 30 live. PASS if ID set after == before."""
import sys
import numpy as np
sys.path.insert(0, "D:/Q_project")
from raksha.vision.ingest import open_source, read_frame
from raksha.vision.tracker import PersonTracker

cap = open_source(0)
trk = PersonTracker(tracker="D:/Q_project/raksha/vision/botsort_reid.yaml", conf=0.35)
seen = []
for phase, n in (("live1", 30), ("dark", 60), ("live2", 30)):
    ids = set()
    for _ in range(n):
        f = read_frame(cap)
        if phase == "dark":
            f = np.zeros_like(f)
        for d in trk.update(f):
            if d["id"] is not None:
                ids.add(d["id"])
    seen.append(ids)
    print(phase, sorted(ids))
cap.release()
before, after = seen[0], seen[2]
print("PASS: ID persisted" if before and before == after else f"CHECK: before={sorted(before)} after={sorted(after)}")

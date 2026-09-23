"""One person, one file. Global ID keyed by gallery name or unknown track."""
import time
from collections import deque


class Dossier:
    def __init__(self, gid, name=None):
        self.gid = gid
        self.name = name or gid
        self.first_seen = time.time()
        self.last_seen = self.first_seen
        self.track_ids = set()
        self.snapshots = []  # file paths of best crops
        self.trail = deque(maxlen=200)  # (cam, x, y, t)
        self.flags = []

    def touch(self, track_id=None, pos=None, snapshot=None):
        self.last_seen = time.time()
        if track_id is not None:
            self.track_ids.add(track_id)
        if pos is not None:
            self.trail.append((*pos, self.last_seen))
        if snapshot is not None and len(self.snapshots) < 3:
            self.snapshots.append(snapshot)

    @property
    def dwell_s(self):
        return self.last_seen - self.first_seen

    def card(self):
        import os as _os
        return {"gid": self.gid, "name": self.name, "dwell_s": round(self.dwell_s, 1),
                "tracks": sorted(self.track_ids), "snaps": len(self.snapshots),
                "snap_urls": ["/snaps/" + _os.path.basename(s) for s in self.snapshots],
                "trail_pts": len(self.trail), "flags": self.flags}

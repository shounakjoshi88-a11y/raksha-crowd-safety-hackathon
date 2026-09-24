"""Continuous recording: rotating mp4 segments of the annotated wall feed."""
import os
import time
import cv2


class SegmentWriter:
    def __init__(self, outdir, seconds=60, fps=15):
        self.outdir = outdir
        self.seconds = seconds
        self.fps = fps
        os.makedirs(outdir, exist_ok=True)
        self.w = None
        self.path = None
        self.started = 0
        self.size = None

    def write(self, frame):
        now = time.time()
        done = None
        if self.w is None or now - self.started >= self.seconds:
            done = self.rollover(frame, now)
        self.w.write(frame)
        return done

    def rollover(self, frame, now):
        old = self.close()
        h, w = frame.shape[:2]
        self.size = (w, h)
        self.path = os.path.join(self.outdir, time.strftime("wall_%Y%m%d_%H%M%S.mp4", time.localtime(now)))
        self.w = cv2.VideoWriter(self.path, cv2.VideoWriter_fourcc(*"mp4v"), self.fps, self.size)
        self.started = now
        return old

    def close(self):
        if self.w is not None:
            self.w.release()
            done = (self.path, self.started, time.time())
            self.w = None
            return done
        return None

"""Raksha real backend: vision loop thread + FastAPI (MJPEG wall + JSON state).
Run: python raksha/backend/app.py [--source 0] [--port 8000]
Open: http://localhost:8000/wall.html
"""
import argparse, os, sys, threading, time
from collections import deque
import cv2
sys.path.insert(0, "D:/Q_project")
from fastapi import FastAPI
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
import uvicorn

from raksha.vision.ingest import open_source, read_frame
from raksha.vision.tracker import PersonTracker
from raksha.vision.zones import ZoneCounter
from raksha.vision.faces import FaceEngine
from raksha.vision.gallery import Gallery
from raksha.vision.dossier import Dossier
from raksha.vision.brain import CrowdBrain

SNAP_DIR = "D:/Q_project/gallery/snaps"
os.makedirs(SNAP_DIR, exist_ok=True)

state = {"jpg": None, "dets": [], "zones": {}, "dossiers": {},
         "brain": {}, "alerts": [], "fps": 0.0, "face_on": False}
lock = threading.Lock()


def vision_loop(src):
    cap = open_source(src)
    trk = PersonTracker()
    zones = ZoneCounter({"Gate": [(0, 0), (0.5, 0), (0.5, 1), (0, 1)],
                         "Stage": [(0.5, 0), (1, 0), (1, 1), (0.5, 1)]})
    try:
        gal = Gallery.load("D:/Q_project/gallery/gallery")
        face_on = gal.index.ntotal > 0
    except Exception:
        gal, face_on = Gallery(), False
    eng = FaceEngine() if face_on else None
    brain = CrowdBrain()
    trails, votes, dossiers = {}, deque(maxlen=3), {}
    t0, n = time.time(), 0
    fps = 0.0
    while True:
        f = read_frame(cap, width=1280)
        if f is None:
            time.sleep(0.2)
            continue
        dets = trk.update(f)
        zc = zones.count(dets, f.shape)
        br = brain.update(f, sum(z["count"] for z in zc.values()))
        H, W = f.shape[:2]
        for d in dets:
            if d["id"] is None:
                continue
            x1, y1, x2, y2 = map(int, d["xyxy"])
            tr = trails.setdefault(d["id"], deque(maxlen=30))
            tr.append(((x1 + x2) // 2, (y1 + y2) // 2))
            cv2.rectangle(f, (x1, y1), (x2, y2), (0, 229, 204), 2)
            cv2.putText(f, f"ID {d['id']}", (x1, y1 - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 229, 204), 2)
            for i in range(1, len(tr)):
                cv2.line(f, tr[i - 1], tr[i], (255, 59, 92), 2)
        if eng and n % 6 == 0:
            for fc in eng.get_faces(f):
                nm, sim, meta = gal.search(fc["embedding"])
                votes.append(nm)
                label = nm if nm and list(votes).count(nm) >= 2 else "stranger"
                gid = nm or "stranger"
                ds = dossiers.setdefault(gid, Dossier(gid, nm))
                x1, y1, x2, y2 = fc["bbox"]
                snap = None
                if len(ds.snapshots) < 3:
                    snap = os.path.join(SNAP_DIR, f"{gid}_{len(ds.snapshots)}.jpg")
                    cv2.imwrite(snap, f[y1:y2, x1:x2])
                ds.touch(snapshot=snap)
                cv2.rectangle(f, (x1, y1), (x2, y2), (255, 200, 0), 2)
                cv2.putText(f, f"{label} {sim:.2f}", (x1, y2 + 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 200, 0), 2)
        n += 1
        if n % 10 == 0:
            fps = n / (time.time() - t0)
        ok, buf = cv2.imencode(".jpg", f, [cv2.IMWRITE_JPEG_QUALITY, 80])
        with lock:
            state.update({"jpg": buf.tobytes() if ok else None, "dets": dets, "zones": zc,
                          "brain": br, "alerts": brain.alerts[-10:], "fps": round(fps, 1),
                          "face_on": face_on,
                          "dossiers": {k: v.card() for k, v in dossiers.items()}})


app = FastAPI(title="Raksha Command API")


@app.get("/api/health")
def health():
    return {"ok": True}


@app.get("/api/state")
def api_state():
    with lock:
        return JSONResponse({k: v for k, v in state.items() if k != "jpg"})


@app.get("/stream.mjpeg")
def stream():
    def gen():
        while True:
            with lock:
                jpg = state["jpg"]
            if jpg:
                yield b"--frame\r\nContent-Type: image/jpeg\r\n\r\n" + jpg + b"\r\n"
            time.sleep(0.05)
    return StreamingResponse(gen(), media_type="multipart/x-mixed-replace; boundary=frame")


app.mount("/", StaticFiles(directory="D:/Q_project/raksha/frontend", html=True), name="static")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default="0")
    ap.add_argument("--port", type=int, default=8000)
    a = ap.parse_args()
    try:
        src = int(a.source)
    except ValueError:
        src = a.source
    threading.Thread(target=vision_loop, args=(src,), daemon=True).start()
    uvicorn.run(app, host="127.0.0.1", port=a.port)

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
from raksha.vision.attributes import top_color, direction
from raksha.vision.overlay import draw_track

SNAP_DIR = "D:/Q_project/gallery/snaps"
os.makedirs(SNAP_DIR, exist_ok=True)

state = {"jpg": None, "dets": [], "zones": {}, "dossiers": {}, "captures": [],
         "brain": {}, "risk_hist": [], "alerts": [], "fps": 0.0, "face_on": False,
         "gal_size": 0}
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
    risk_hist, captures = deque(maxlen=60), deque(maxlen=20)
    t0, n = time.time(), 0
    fps = 0.0
    while True:
        f = read_frame(cap, width=1280)
        if f is None:
            time.sleep(0.2)
            continue
        dets = trk.update(f)
        persons = [d for d in dets if d["cls"] == 0]
        vehicles = [d for d in dets if d["cls"] != 0]
        zc = zones.count(persons, f.shape)
        br = brain.update(f, sum(z["count"] for z in zc.values()))
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
            tr = trails.setdefault(d["id"], deque(maxlen=30))
            tr.append(((x1 + x2) // 2, (y1 + y2) // 2))
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
        if eng and n % 12 == 0:
            for fc in eng.get_faces(f):
                nm, sim, meta = gal.search(fc["embedding"])
                votes.append(nm)
                label = nm if nm and list(votes).count(nm) >= 2 else "stranger"
                gid = nm or "stranger"
                ds = dossiers.setdefault(gid, Dossier(gid, nm))
                if meta:
                    ds.attrs = {"age": meta.get("age"), "gender": meta.get("gender"), "sim": round(sim, 2)}
                x1, y1, x2, y2 = fc["bbox"]
                snap = None
                if len(ds.snapshots) < 3:
                    snap = os.path.join(SNAP_DIR, f"{gid}_{len(ds.snapshots)}.jpg")
                    cv2.imwrite(snap, f[y1:y2, x1:x2])
                    captures.appendleft({"url": "/snaps/" + os.path.basename(snap),
                                         "name": label, "sim": round(sim, 2), "time": time.time()})
                ds.touch(snapshot=snap)
                cv2.rectangle(f, (x1, y1), (x2, y2), (255, 200, 0), 2)
                cv2.putText(f, f"{label} {sim:.2f}", (x1, y2 + 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 200, 0), 2)
        n += 1
        if n % 10 == 0:
            fps = n / (time.time() - t0)
        ok, buf = cv2.imencode(".jpg", f, [cv2.IMWRITE_JPEG_QUALITY, 80])
        risk_hist.append(br["risk"])
        with lock:
            state.update({"jpg": buf.tobytes() if ok else None, "dets": dets, "zones": zc,
                          "brain": br, "risk_hist": list(risk_hist),
                          "captures": list(captures),
                          "alerts": brain.alerts[-10:], "fps": round(fps, 1),
                          "face_on": face_on, "gal_size": gal.index.ntotal,
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


app.mount("/snaps", StaticFiles(directory=SNAP_DIR), name="snaps")
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

"""Local evidence store: SQLite + files, no cloud. Biometrics never leave this machine.

Tables: persons (dossiers), tracks, snapshots (paths), alerts, video_segments,
audit (append-only, hash-chained so tampering shows).
Blobs (video, JPEGs, Faiss) stay as files; the DB holds paths + metadata.
Purge deletes rows AND files older than N days.
"""
import hashlib
import json
import os
import sqlite3
import threading
import time

_LOCK = threading.RLock()  # reentrant: purge/add_alert call _audit inside


def _locked(fn):
    import functools

    @functools.wraps(fn)
    def w(*a, **k):
        with _LOCK:
            return fn(*a, **k)
    return w

SCHEMA = """
CREATE TABLE IF NOT EXISTS persons(
  gid TEXT PRIMARY KEY, name TEXT, age INTEGER, gender TEXT,
  first_seen REAL, last_seen REAL);
CREATE TABLE IF NOT EXISTS tracks(
  id INTEGER PRIMARY KEY AUTOINCREMENT, gid TEXT, track_id INTEGER,
  camera TEXT, started REAL, ended REAL);
CREATE TABLE IF NOT EXISTS snapshots(
  id INTEGER PRIMARY KEY AUTOINCREMENT, gid TEXT, path TEXT,
  taken REAL, blur REAL);
CREATE TABLE IF NOT EXISTS alerts(
  id INTEGER PRIMARY KEY AUTOINCREMENT, level TEXT, risk REAL,
  density REAL, zone TEXT, time REAL, snapshot_path TEXT);
CREATE TABLE IF NOT EXISTS video_segments(
  id INTEGER PRIMARY KEY AUTOINCREMENT, path TEXT,
  started REAL, ended REAL, bytes INTEGER);
CREATE TABLE IF NOT EXISTS audit(
  id INTEGER PRIMARY KEY AUTOINCREMENT, ts REAL, actor TEXT,
  action TEXT, details TEXT, prev_hash TEXT, hash TEXT);
CREATE TABLE IF NOT EXISTS config(
  key TEXT PRIMARY KEY, value TEXT);
CREATE TABLE IF NOT EXISTS cameras(
  id TEXT PRIMARY KEY, name TEXT, zone TEXT, source TEXT,
  enabled INTEGER DEFAULT 1, poly TEXT);
"""


def connect(path):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    db = sqlite3.connect(path, check_same_thread=False)
    db.executescript(SCHEMA)
    for col, typ in (("status", "TEXT DEFAULT 'open'"), ("ack_by", "TEXT"),
                     ("ack_time", "REAL"), ("note", "TEXT")):
        try:
            db.execute(f"ALTER TABLE alerts ADD COLUMN {col} {typ}")
        except sqlite3.OperationalError:
            pass
    defaults = {"data_dir": "D:/Q_project/gallery", "retention_days": "7",
                "warn_level": "0.4", "critical_level": "0.6",
                "record_mode": "full", "density_full": "5.0"}
    for k, v in defaults.items():
        db.execute("INSERT OR IGNORE INTO config(key, value) VALUES(?,?)", (k, v))
    db.commit()
    return db


@_locked
def get_config(db):
    return {k: v for k, v in db.execute("SELECT key, value FROM config").fetchall()}


@_locked
def set_config(db, mapping):
    for k, v in mapping.items():
        db.execute("INSERT INTO config(key, value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                   (k, str(v)))
    _audit(db, "config", json.dumps(mapping))
    db.commit()


@_locked
def ack_alert(db, alert_id, status, by="operator", note=""):
    assert status in ("acknowledged", "false_alarm", "escalated")
    db.execute("UPDATE alerts SET status=?, ack_by=?, ack_time=?, note=? WHERE id=?",
               (status, by, time.time(), note, alert_id))
    _audit(db, "alert_" + status, json.dumps({"id": alert_id, "by": by}))
    db.commit()


@_locked
def export_range(db, data_dir, day, out_path):
    """Zip one day (YYYY-MM-DD) of alerts + snapshots + segments for handoff."""
    import zipfile
    start = time.mktime(time.strptime(day, "%Y-%m-%d"))
    rows = db.execute("SELECT id, level, risk, density, zone, time, status FROM alerts WHERE time>=? AND time<?",
                      (start, start + 86400)).fetchall()
    snaps = db.execute("SELECT path FROM snapshots WHERE taken>=? AND taken<?",
                       (start, start + 86400)).fetchall()
    segs = db.execute("SELECT path FROM video_segments WHERE started>=? AND started<?",
                      (start, start + 86400)).fetchall()
    with zipfile.ZipFile(out_path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("alerts.json", json.dumps(
            [dict(zip(("id", "level", "risk", "density", "zone", "time", "status"), r)) for r in rows], indent=1))
        for (p,) in snaps + segs:
            if p and os.path.isfile(p):
                z.write(p, os.path.relpath(p, data_dir))
    _audit(db, "export", json.dumps({"day": day, "out": out_path}))
    db.commit()
    return out_path


@_locked
def _audit(db, action, details="", actor="system"):
    prev = db.execute("SELECT hash FROM audit ORDER BY id DESC LIMIT 1").fetchone()
    prev_hash = prev[0] if prev else "GENESIS"
    ts = time.time()
    h = hashlib.sha256(f"{ts}{actor}{action}{details}{prev_hash}".encode()).hexdigest()
    db.execute("INSERT INTO audit(ts, actor, action, details, prev_hash, hash) VALUES(?,?,?,?,?,?)",
               (ts, actor, action, details, prev_hash, h))
    db.commit()


@_locked
def upsert_person(db, gid, name=None, age=None, gender=None):
    now = time.time()
    row = db.execute("SELECT gid FROM persons WHERE gid=?", (gid,)).fetchone()
    if row:
        db.execute("UPDATE persons SET last_seen=?, name=COALESCE(?,name), age=COALESCE(?,age), gender=COALESCE(?,gender) WHERE gid=?",
                   (now, name, age, gender, gid))
    else:
        db.execute("INSERT INTO persons(gid, name, age, gender, first_seen, last_seen) VALUES(?,?,?,?,?,?)",
                   (gid, name or gid, age, gender, now, now))
    db.commit()


@_locked
def add_track(db, gid, track_id, camera="cam0"):
    now = time.time()
    row = db.execute("SELECT id FROM tracks WHERE gid=? AND track_id=? AND camera=? AND ended IS NULL",
                     (gid, track_id, camera)).fetchone()
    if row is None:
        db.execute("INSERT INTO tracks(gid, track_id, camera, started) VALUES(?,?,?,?)",
                   (gid, track_id, camera, now))
        db.commit()


@_locked
def close_track(db, gid, track_id, camera="cam0"):
    db.execute("UPDATE tracks SET ended=? WHERE gid=? AND track_id=? AND camera=? AND ended IS NULL",
               (time.time(), gid, track_id, camera))
    db.commit()


@_locked
def add_snapshot(db, gid, path, blur=0.0):
    db.execute("INSERT INTO snapshots(gid, path, taken, blur) VALUES(?,?,?,?)",
               (gid, path, time.time(), blur))
    db.commit()


@_locked
def add_alert(db, level, risk, density, zone="", snapshot_path=""):
    db.execute("INSERT INTO alerts(level, risk, density, zone, time, snapshot_path) VALUES(?,?,?,?,?,?)",
               (level, risk, density, zone, time.time(), snapshot_path))
    _audit(db, "alert", json.dumps({"level": level, "risk": risk, "zone": zone}))
    db.commit()


@_locked
def add_segment(db, path, started, ended):
    try:
        size = os.path.getsize(path)
    except OSError:
        size = 0
    db.execute("INSERT INTO video_segments(path, started, ended, bytes) VALUES(?,?,?,?)",
               (path, started, ended, size))
    db.commit()


@_locked
def purge(db, days=7):
    """Delete records AND files older than N days. Returns counts."""
    cutoff = time.time() - days * 86400
    counts = {}
    for table, tcol, pcol in (("snapshots", "taken", "path"), ("alerts", "time", "snapshot_path"),
                               ("video_segments", "started", "path")):
        paths = [r[0] for r in db.execute(f"SELECT {pcol} FROM {table} WHERE {tcol}<?", (cutoff,)).fetchall() if r[0]]
        for p in paths:
            try:
                os.remove(p)
            except OSError:
                pass
        cur = db.execute(f"DELETE FROM {table} WHERE {tcol}<?", (cutoff,))
        counts[table] = cur.rowcount
    _audit(db, "purge", json.dumps({"days": days, "counts": counts}))
    db.commit()
    return counts


@_locked
def stats(db):
    out = {}
    for t in ("persons", "tracks", "snapshots", "alerts", "video_segments", "audit"):
        out[t] = db.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
    return out


@_locked
def verify_chain(db):
    """Returns True if audit hash chain is intact."""
    rows = db.execute("SELECT ts, actor, action, details, prev_hash, hash FROM audit ORDER BY id").fetchall()
    prev = "GENESIS"
    for ts, actor, action, details, ph, h in rows:
        if ph != prev:
            return False
        if hashlib.sha256(f"{ts}{actor}{action}{details}{ph}".encode()).hexdigest() != h:
            return False
        prev = h
    return True

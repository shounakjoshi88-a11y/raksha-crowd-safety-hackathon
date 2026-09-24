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
import time

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
"""


def connect(path):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    db = sqlite3.connect(path)
    db.executescript(SCHEMA)
    db.commit()
    return db


def _audit(db, action, details="", actor="system"):
    prev = db.execute("SELECT hash FROM audit ORDER BY id DESC LIMIT 1").fetchone()
    prev_hash = prev[0] if prev else "GENESIS"
    ts = time.time()
    h = hashlib.sha256(f"{ts}{actor}{action}{details}{prev_hash}".encode()).hexdigest()
    db.execute("INSERT INTO audit(ts, actor, action, details, prev_hash, hash) VALUES(?,?,?,?,?,?)",
               (ts, actor, action, details, prev_hash, h))
    db.commit()


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


def add_track(db, gid, track_id, camera="cam0"):
    now = time.time()
    row = db.execute("SELECT id FROM tracks WHERE gid=? AND track_id=? AND camera=? AND ended IS NULL",
                     (gid, track_id, camera)).fetchone()
    if row is None:
        db.execute("INSERT INTO tracks(gid, track_id, camera, started) VALUES(?,?,?,?)",
                   (gid, track_id, camera, now))
        db.commit()


def close_track(db, gid, track_id, camera="cam0"):
    db.execute("UPDATE tracks SET ended=? WHERE gid=? AND track_id=? AND camera=? AND ended IS NULL",
               (time.time(), gid, track_id, camera))
    db.commit()


def add_snapshot(db, gid, path, blur=0.0):
    db.execute("INSERT INTO snapshots(gid, path, taken, blur) VALUES(?,?,?,?)",
               (gid, path, time.time(), blur))
    db.commit()


def add_alert(db, level, risk, density, zone="", snapshot_path=""):
    db.execute("INSERT INTO alerts(level, risk, density, zone, time, snapshot_path) VALUES(?,?,?,?,?,?)",
               (level, risk, density, zone, time.time(), snapshot_path))
    _audit(db, "alert", json.dumps({"level": level, "risk": risk, "zone": zone}))
    db.commit()


def add_segment(db, path, started, ended):
    try:
        size = os.path.getsize(path)
    except OSError:
        size = 0
    db.execute("INSERT INTO video_segments(path, started, ended, bytes) VALUES(?,?,?,?)",
               (path, started, ended, size))
    db.commit()


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


def stats(db):
    out = {}
    for t in ("persons", "tracks", "snapshots", "alerts", "video_segments", "audit"):
        out[t] = db.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
    return out


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

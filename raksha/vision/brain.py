"""Crowd brain: density + Farneback flow -> stampede risk, per-zone bottleneck, ETA forecast, alerts.

Bottleneck = a zone that is packed (high density), stopped (local stillness ~1),
and standing long (median dwell up). Scored independently of the global meter so
a local crush shows up even when the whole frame still looks calm.

Proactive: a least-squares fit over the last ~40s of risk gives seconds-to-warn
and seconds-to-critical while the trend is rising, so guards act before the
threshold is crossed, not after.
"""
import time
import json
from collections import deque
import cv2
import numpy as np


def _poly_frac(poly):
    pts = np.asarray(poly, dtype=float)
    x, y = pts[:, 0], pts[:, 1]
    return float(0.5 * abs(np.dot(x, np.roll(y, 1)) - np.dot(y, np.roll(x, 1))))


def _dir_split(ang_flat):
    hist, _ = np.histogram(ang_flat, bins=8, range=(0, 2 * np.pi))
    tot = hist.sum() + 1e-9
    p = hist / tot
    ent = float(-(p[p > 0] * np.log(p[p > 0] + 1e-9)).sum() / np.log(8))
    i1 = int(np.argmax(hist))
    cf = float(min(hist[i1], hist[(i1 + 4) % 8]) / tot * 2)
    return cf, ent


class CrowdBrain:
    def __init__(self, area_m2=50.0):
        self.prev = None
        self.alerts = []
        self.area = float(area_m2)
        self.hist = deque(maxlen=120)  # (t, risk) raw-rate samples for the trend fit
        self._frac = {}

    def _forecast(self, warn, critical):
        """(eta_warn_s, eta_crit_s, slope, trend) from recent risk history."""
        if len(self.hist) < 15:
            return None, None, 0.0, "steady"
        pts = list(self.hist)[-40:]
        ts = np.array([p[0] for p in pts], dtype=float)
        rs = np.array([p[1] for p in pts], dtype=float)
        ts -= ts[0]
        if ts[-1] < 5:
            return None, None, 0.0, "steady"
        slope = float(np.polyfit(ts, rs, 1)[0])
        cur = float(rs[-1])
        if slope > 0.002:
            trend = "rising"
        elif slope < -0.002:
            trend = "easing"
        else:
            trend = "steady"

        def eta(level):
            if cur >= level:
                return 0.0
            if slope <= 1e-6:
                return None
            return round((level - cur) / slope, 1)

        return (eta(warn) if trend == "rising" else None,
                eta(critical) if trend == "rising" else None,
                slope, trend)

    def update(self, frame, count, warn=0.4, critical=0.6, full=5.0,
               zones=None, zone_polys=None):
        now = time.time()
        small = cv2.resize(frame, (320, 180))
        gray = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
        H, W = gray.shape
        density = count / max(self.area, 1.0)
        still, cf, ent = 1.0, 0.0, 0.0
        mag = ang = None
        if self.prev is not None:
            flow = cv2.calcOpticalFlowFarneback(
                self.prev, gray, None, 0.5, 3, 15, 3, 5, 1.2, 0)
            mag, ang = cv2.cartToPolar(flow[..., 0], flow[..., 1])
            still = float(np.clip(1 - mag.mean() / 2.0, 0, 1))
            cf, ent = _dir_split(ang.ravel())
        self.prev = gray
        self.hist.append((now, float(np.clip(
            float(np.clip(density / full, 0, 1.5)) * still * (1 + cf), 0, 1.5))))

        rho = float(np.clip(density / full, 0, 1.5))
        risk = float(np.clip(rho * still * (1 + cf), 0, 1.5))
        level = "red" if risk > critical else "yellow" if risk > warn else "green"
        eta_w, eta_c, slope, trend = self._forecast(warn, critical)

        # ---- per-zone: local density x local stillness x standing time ----
        zone_risk, bottleneck = {}, None
        if zones:
            for name, z in zones.items():
                poly = (zone_polys or {}).get(name)
                frac = self._frac.get(name)
                if frac is None and poly is not None:
                    frac = max(_poly_frac(poly), 1e-3)
                    self._frac[name] = frac
                zarea = max((frac or 0.5) * self.area, 1.0)
                zd = z["count"] / zarea
                z_still, z_cf = still, cf
                if mag is not None and ang is not None and poly is not None:
                    mask = np.zeros((H, W), np.uint8)
                    cv2.fillPoly(mask, [(np.asarray(poly, float) * [W, H]).astype(np.int32)], 1)
                    sel = mask > 0
                    if sel.any():
                        z_still = float(np.clip(1 - mag[sel].mean() / 2.0, 0, 1))
                        z_cf, _ = _dir_split(ang[sel].ravel())
                dw = z.get("dwell_s") or {}
                dwell_med = float(np.median(list(dw.values()))) if dw else 0.0
                stand = float(np.clip(dwell_med / 20.0, 0, 1))
                z_rho = float(np.clip(zd / full, 0, 1.5))
                z_risk = float(np.clip(z_rho * z_still * (1 + z_cf), 0, 1.5))
                # bottleneck score: packed AND stopped AND standing (the crush signature)
                bn = float(np.clip(z_rho * z_still * (0.4 + 0.6 * stand), 0, 1.5))
                sev = "red" if bn > critical else "yellow" if bn > warn else "green"
                zone_risk[name] = {"density": round(zd, 2), "risk": round(z_risk, 2),
                                   "bn": round(bn, 2), "sev": sev,
                                   "still": round(z_still, 2),
                                   "dwell_med": round(dwell_med, 1),
                                   "count": z["count"]}
                if sev != "green" and (bottleneck is None or bn > bottleneck["score"]):
                    bottleneck = {"zone": name, "score": round(bn, 2),
                                  "density": round(zd, 2), "sev": sev,
                                  "still": round(z_still, 2),
                                  "dwell_med": round(dwell_med, 1),
                                  "count": z["count"]}

        if level != "green":
            al = {"level": level, "risk": round(risk, 2),
                  "density": round(density, 2), "time": now}
            if bottleneck:
                al["bottleneck"] = bottleneck["zone"]
            self.alerts.append(al)
            self.alerts = self.alerts[-50:]
            with open("D:/Q_project/gallery/alerts.jsonl", "a") as f:
                f.write(json.dumps(al) + "\n")

        return {"density": round(density, 2), "risk": round(risk, 2), "level": level,
                "stillness": round(still, 2), "counterflow": round(cf, 2),
                "entropy": round(ent, 2),
                "zone_risk": zone_risk, "bottleneck": bottleneck,
                "eta_warn_s": eta_w, "eta_crit_s": eta_c,
                "slope": round(slope, 4), "trend": trend}

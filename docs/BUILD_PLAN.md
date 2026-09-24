# RAKSHA Build Plan — bringing the crowd-physics core to life

> Stage: IDEA PPT (Stage 1). No app code is being written now. This doc is the
> engineering roadmap that makes the idea credible — every step names runnable
> starting points verified Sept 2026 (repos fetched, not remembered).
> Ground rules: (1) dual-track — CORE = density-flow-pressure (new), SIDE =
> per-person labeling (existing YOLO+ByteTrack, already OK, kept);
> (2) NO laptop-bound scores anywhere in the idea deck — published benchmark MAE
> and deployment-scale numbers only. Companion: `docs/RESEARCH_V2.md` (the why).

## 1. Target architecture (one picture in words)

Per fixed camera, one edge node runs the CORE:
`frame → perspective-weighted density heatmap → DIS optical-flow field →
pressure p = ρ·Var(V) + continuity accumulation → zone JSON (density, flow,
pressure per zone) → venue fusion (multi-camera graph) → wall + actuation API
(open overflow gate / hold entries, human confirms)`.
Raw video never leaves the node: each edge box keeps a 10-minute rolling buffer
and only a confirmed Red alert exports its clip, cryptographically signed, to the
evidence pack. Escalation has teeth: Yellow auto-pages the zone guard with an ack
timer; Red auto-pages command with a diversion proposal; unanswered reds climb the
chain automatically; every red has an owner, a timer, and a log. The pilot publishes
its false-alarm rate. Hardware envelope: one Jetson-class box (about $250, 15 watts)
per 1 to 4 cameras, reusing existing CCTV; no cloud video. The SIDE track runs alongside: YOLOv8+ByteTrack
tracklets active only under ~2/m² (low-density cross-check + person dossier
inputs); above that it yields to the density core. Face stays Phase-2, opt-in,
B2G plug-in — untouched.

## 2. Component build order (each row = verified starting point)

| # | Component | Start from (verified) | First runnable | Notes / traps |
|---|---|---|---|---|
| 1 | Density baseline | `cvlab-stonybrook/DM-Count` — 245★, MIT, GDrive weights (SHA/SHB/QNRF/NWPU), `test.py` + Gradio `demo.py` | Day 1: `demo.py` on our station/temple clips | Best runnable base. Benchmarks to quote: SHA 59.7, SHB 7.4, QNRF 85.6 MAE |
| 2 | Density reference arch | `leeyeehoo/CSRNet-pytorch` — 735★, Drive weights (SHA 66.4/SHB 10.6) | Port `model.py` to modern torch + own infer loop | Stale (torch 0.4/py2.7), NO license, NO infer script — reference only |
| 3 | Lightweight edge net | `ChenyuGAO-CS/MobileCount` — 27★, has `test-time.py`/`test-flops.py` | Needs inference wrapper + weight hunt | Candidate only. LCDnet / ShuffleCount / PGCNet runnable code NOT found — never promise them |
| 4 | Flow field | `cv2.DISOpticalFlow_create(PRESET_MEDIUM)` — official OpenCV sample `dis_opt_flow.py` | Drop-in per camera; 300–600 Hz @0.45MP on one CPU core (literature) | Fastest preset for edge; NVOF later on NVIDIA hardware |
| 5 | Perspective weighting | `wlixin/PACNN-PerspectiveAware-CrowdCounting` — 16★, MIT-academic, GT perspective maps for ShanghaiTech | Reuse GT maps + pixel-weighting idea, reimplement in torch (repo is MATLAB/Caffe) | Zero-code alternative that always works: geometry-adaptive kernels σ = 0.3 × k-NN head distance (MCNN formula, no repo needed) |
| 6 | Homography calibration | `JuanIsernGhosn/homography-calibrator` (BSD-3, click points → saves H) or `ElSangour/camera-calibration-system` (MIT, exports homography JSON + reprojection error) | Calibrate ONE fixed view (gate/stairwell) with 4+ ground points | Only for fixed chokepoints surveyed once — never promise per-camera survey at event scale |
| 7 | Edge deployment | DeepStream custom-model docs (`onnx-file=` nvinfer → TensorRT) + `marcoslucianops/DeepStream-Yolo` as config template | Export density net ONNX→TRT as regressor (no bbox parser) | No public density-in-DeepStream example exists — flag as integration work, not reuse |
| 8 | Alert-threshold pattern | `niki600/CrowdCount` (zone.json + capacity thresholds) / `bhavanavempali/Crowd-count-using-video-analytics` (MIT, zone occupancy alerts) | Crude `if pressure > X → alert` reference | Swap their box-counter for density sum; pattern only |
| 9 | Side track (kept) | Existing YOLOv8n + ByteTrack wall (already built, already OK) | No work now | Gate: active <2/m², yields above; feeds dossier inputs |

## 3. Data plan
Train/eval: ShanghaiTech A/B (dense/sparse), UCF-QNRF subset (extreme density),
JHU-CROWD++ (weather/occlusion). Ours: Wikimedia clips (station, crossing, temple)
+ self-annotated precursor segments (stop-and-go waves, counterflow) — because
UMN/UCSD/ShanghaiTech-Campus label overt anomalies, never pre-stop turbulence.
Calibration: 4+ measured ground points per fixed chokepoint view, surveyed once.

## 4. Milestones (exit criteria, no dates — idea stage)
- **M1 density**: DM-Count demo runs on our 3 clips; zone sums look sane vs headcount. Exit: SHA MAE reproduced ±2.
- **M2 flow+pressure**: DIS field over density; plot ρ, mean speed, Var(V), p = ρ·Var(V) on station clip. Exit: stop-and-go precursor visible before the densest segment.
- **M3 geometry**: PACNN-style weighting + one homography-calibrated view. Exit: persons/m² vs uncalibrated on same frame, error direction correct (far field no longer undercounted).
- **M4 fusion+actuation**: multi-zone JSON → venue graph → wall mock with WATCH/RED + upstream-diversion rule (e.g. Gate B pressure → open Gate A overflow). Exit: end-to-end on recorded clips with HITL confirm step.
- **M5 edge**: ONNX→TRT export, per-camera node budget (density + DIS) measured on Jetson-class hardware — real numbers replace estimates only then.

## 5. Deployment realities (Q&A answers, ready)
- Connectivity at outdoor mela grounds: edge boxes link to the venue server over
  site LAN (Kumbh 2025 laid fibre to its servers) with 4G/5G failover; boxes buffer
  locally and sync on reconnect, so a network drop delays the wall, never the edge.
- Venue-server redundancy: hot-standby pair per venue; edge boxes keep alerting
  locally on last-known thresholds if the server is unreachable.
- "City control" escalation tier is a target integration (protocol TBD in pilot),
  not an assumed existing capability.

## 6. Risks (say them before a judge does)- No runnable LCDnet/ShuffleCount/PGCNet code found — lightweight path is MobileCount-port or custom pruning, not a download.
- No density-in-DeepStream precedent — integration risk, prototype on plain TensorRT first.
- Self-calibration errors hit 16% height / 50% distance far-field — metric alarms only on surveyed views.
- Precursor labels don't exist publicly — we annotate our own; small-data risk.
- Kumbh lesson binds: actuation + HITL is the product, the heatmap is just the sensor.

## 6. What this means for the deck rebuild (cut list)
CUT (laptop-bound, meaningless at deployment scale): S4 FPS-by-bucket chart +
"same laptop" caption; S4 "Tested on three real crowds" FPS chips; S2 stat cards
"18 tracked at once / <1s guard warned / 15 video checks every second"; any
"our laptop runs a venue" line. KEEP (not laptop-bound): benchmark MAE table
(SHA/SHB/QNRF from papers); Kumbh deployment numbers (2,751 cameras, >3/m² alarm,
3-month surveys); Jetson PeopleNet FPS clearly labeled as detection baseline;
pressure/threshold physics with paper citations. Side track appears once as
"per-person labeling below 2/m² + dossier inputs — built, kept" and never again.

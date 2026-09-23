# RAKSHA BUILD PLAN (living tracker)
> Update this file as work progresses: tick `[x]` when done, add follow-ups at the bottom.
> Mirror snapshots to repo root `plan.md` on phase completions. Last updated: 2026-09-23 (plan created, research done).

## Machine profile (verified 2026-09-23)
- GPU: RTX 4050 6GB, driver 592.82, CUDA 13.1 → use torch cu130 wheels (driver >= 13.0 OK)
- CPU: i5-13420H 8 cores. RAM: 16GB. Cam: HP Wide Vision HD webcam.
- Python 3.14.2 system env. torch 2.12.0+cpu present (replace with cu130). onnxruntime 1.27, fastapi, uvicorn, numpy 2.4.1, scipy present.
- Missing and needed: ultralytics, insightface, faiss-cpu, opencv-python, supervision.
- Key compat facts: PyTorch 2.9+ ships cp314 CUDA wheels (cu126/cu128/cu130). buffalo_s pack 159MB, buffalo_l 326MB, auto-download on first `prepare`. Faiss flat fine under 50k IDs. YOLOv8s chosen (known MOT benchmarks); tracker `bytetrack.yaml` default, BoT-SORT `with_reid` in phase 3.

## Phase 0: Environment [x] (done 2026-09-23)
- [x] Install torch cu130 + torchvision (replace +cpu build), verify `torch.cuda.is_available()`
- [x] Install ultralytics, insightface, faiss-cpu, opencv-python, supervision
- [x] Download yolov8s.pt (first `YOLO()` call does it), verify GPU inference on webcam frame
- [x] Download buffalo_s pack (first `FaceAnalysis.prepare()` does it), verify 1 face embed
- [x] Record cold FPS numbers into Phase 1 section
- Acceptance: `python scripts/smoke_env.py` prints GPU true + versions + 1 detect + 1 embed.
- Cold numbers: torch 2.14.0+cu130 CUDA True (RTX 4050). YOLOv8s first-run 2857ms (warmup incl), 1 person. buffalo_s 438ms first-run, 1 face, emb (512,), age+gender OK.

## Phase 1: Live tracking wall [x] (done 2026-09-24)
- [x] `raksha/vision/ingest.py`: webcam + video file + RTSP sources, 720p, frame-skip 2
- [x] `raksha/vision/tracker.py`: YOLOv8s + `track(persist=True, tracker=bytetrack.yaml)`, per-stream instances
- [x] Warm FPS measured: **30.3 FPS** bench / **14.2 FPS** full wall w/ overlay + save (`scripts/bench_track.py`, `scripts/live.py`)
- [x] `raksha/vision/zones.py`: polygons + per-zone counts + dwell timers (feet-point test)
- [x] `scripts/live.py`: IDs + trails + zone panel + FPS + save-to-file + frame cap; wall_test.mp4 verified with overlay
- [x] Crowd clip test: 3 public 720p clips (Grand Central 278f, station rush 260f, street 456f). Peaks 20/15/25 simultaneous, 29-38 FPS. IDs inflate by switches in dense scenes, logged honestly. Shots in README.
- [x] Vehicles: multi-class tracker (car, motorbike, bus, truck), blue boxes + type panels. Traffic clip 924f: 226 person IDs, 67 vehicle IDs, peak 23, 49-55 FPS. Compact 2-line panels when >12 dets. Demo video recorded (docs/demo/tracking_demo.mp4).
- Acceptance: 2 sources tracked live, IDs stable through short occlusion, FPS logged.

## Phase 2: Face dossier, one person one file [x] (done 2026-09-24)
- [x] `raksha/vision/faces.py`: buffalo_s FaceAnalysis, ctx_id=0, det_size 640, thr 0.5 + blur/size gate
- [x] `scripts/enroll.py`: Demo01 enrolled, 3 shots, blur 88-122, gallery/gallery.faiss+json (LOCAL ONLY, never push)
- [x] `raksha/vision/gallery.py`: Faiss IndexFlatIP cosine, thr 0.40, save/load
- [x] Live match `scripts/match_live.py`: 3-frame vote smoothing → Demo01 card, dwell 7.7s
- [x] `raksha/vision/dossier.py`: gid, tracks, trail, dwell, flags, card()
- [x] Snapshot crops saved to disk: `gallery/snaps/<gid>_N.jpg`, max 3 per dossier (verified Demo01 snaps=3)
- [x] Backend proper: `raksha/vision/brain.py` (density/flow/risk/alerts) + `raksha/backend/app.py` (threaded loop, /api/state, /stream.mjpeg, static wall) + `raksha/frontend/wall.html` (stream + meter + zones + dossiers + alerts)
- [x] Live verified: track ID 1 conf 0.95, Stage dwell 21s, Demo01 dwell 20.5s, brain green, wall.html 200
- [ ] Stranger clustering polish (currently single stranger dossier)
- Acceptance: enrolled face walks in → card pops <0.5s, unknowns clustered not spammed.

## Phase 3: Cross-camera ReID + global ID [~] (tested honestly 2026-09-24)
- [x] `raksha/vision/botsort_reid.yaml`: with_reid True, appearance_thresh 0.4, gmc none, buffer 60
- [x] `scripts/test_reid.py`: 60-frame blackout → ID persisted (buffer + ReID combined)
- [x] 100-frame blackout (beyond buffer): new ID issued, auto-ReID did NOT rebind at 0.6 or 0.4
- [x] Decision: track_buffer 60 covers ~4-6s occlusions (verified). Cross-cam global identity carried by FACE gallery (same face → same dossier), the stronger signal. Standalone OSNet deferred to Phase 5 if time.
- Acceptance: re-entry keeps global ID in 4/5 trials. (Short-gap: yes. Long-gap body-only: no, face covers it.)

## Phase 4: Crowd brain [x] (done 2026-09-24)
- [x] Zone density (count/area) + heatmap overlay (zone panel; heatmap deferred, counts suffice for meter)
- [x] Farneback flow @320p: stillness + counterflow + entropy (`raksha/vision/brain.py`)
- [x] Stampede meter: risk = density_norm x stillness x (1 + counterflow); RED >0.6 YELLOW >0.4 (verified RED 1.2-1.36 at 6/m2)
- [x] Alerts: <1s wall pop + `gallery/alerts.jsonl` handover log (LOCAL ONLY, never push)
- [x] Wall tune: face every 12th frame (was 6th) to lift FPS
- [ ] Bottleneck box FTLE-lite (rule meter + zones cover demo; add only if time)
- Acceptance: dense test frame → RED + alert entry with snapshot.

## Phase 5: Harden + demo + submission [~] (in progress 2026-09-24)
- [x] ONNX export yolov8s (42.8MB): 327ms ORT-GPU, 4779ms ORT-CPU → PyTorch CUDA stays primary
- [x] onnxruntime-gpu installed → CUDAExecutionProvider live → face steady 61ms (was 438ms CPU)
- [x] `raksha/vision/privacy.py`: blur_faces helper; purge = delete gallery/snaps older than 7d before handover
- [x] Weights moved to `raksha/models/` (local only, never push, 64MB)
- [x] Deck slide 4 now shows OUR measured numbers (15-30 track, 61ms face, RED 1.2+), validated PASSED
- [x] Demo clip recorded: `scripts/ppt/previews/demo_wall.mp4` 300 frames (local only)
- [x] PDF exported via PowerPoint COM: `deck/Raksha_Hackathon2026_Final.pdf` (396KB, 6 slides)
- [ ] Team Leader name into slide 1 (tomorrow) + re-export PDF + upload to portal
- [ ] FPS variance noted (7-30 by thermals/power); record plugged-in numbers if judges ask
- Acceptance: PDF uploaded, video recorded, repo tagged.

## Follow-ups discovered during build
- 2026-09-23: onnxruntime 1.27 here is CPU-only build (no CUDAExecutionProvider), so InsightFace runs CPU (~438ms first run). Consider onnxruntime-gpu in Phase 5 if face latency blocks <0.5s card pop. Face runs on crops + skipped frames, so fine for now.
- 2026-09-24: wall runs ~3 FPS with face every 6th frame (CPU ORT is the bottleneck; YOLO alone does 14-30). Fix options: face on track crops only, every 12th frame, or onnxruntime-gpu. Phase 5.
- 2026-09-24: FastAPI static mount at / must be registered AFTER /api routes or it swallows them (Starlette matches in order). Fixed in app.py.
- 2026-09-24: FP16 half flag gave no gain (15.4 vs 15.2) and is deprecated, reverted. TensorRT skipped: needs heavy install, current speed suffices for demo.
- 2026-09-24: wall end-to-end now 12.1 FPS (was ~3) with GPU face every 12th frame. YOLO raw 15-30 by thermals/power state. Face steady 61ms GPU vs 438ms CPU.
- 2026-09-24: Chinese-style overlay shipped (`vision/attributes.py` top-color HSV + compass dir, `vision/overlay.py` dark panels, odd/even side split). Verified on station_rush dense frame, matches reference pattern.
- 2026-09-24: color fix from crop diagnosis (sky contaminated full-width bands). Now central-region sampling + strict achromatic first (white V>140) + top/bottom split. Panels anchor above boxes, compact 2-line mode when crowded.
- 2026-09-24: part-based bodies per research (head/torso/legs rigid split). Measured color via k-means k=2 on 40px central crops, swatch + hex + name in panel, cached per track every 15 frames (~12ms each, amortized ~16ms/frame at 20 tracks). Verified white/blue/black read true.
- 2026-09-24: color deep dive (DeepMAR/RAP parts, algolia bg+skin rejection, IQR median, Lab naming). Rebuilt engine: k=3 shirt+trouser+background, border-bg + skin rejection, IQR-clean median, HSV-sector naming with pink/brown/maroon, 0.45 dominance gate (unknown beats wrong). Calibrated on station reds/whites/beiges. Seated overlapping rows still partial (documented hard case).
- 2026-09-24: Indian CCTV tests (station 4451f 37 IDs peak 9, temple 1799f 543 IDs peak 17). README shots replaced with Indian footage. Demo video re-recorded with part boxes.
- 2026-09-24: color v2 from GitHub deep dive (DeepMAR/RAP parts, algolia bg+skin rejection, IQR median, HSV-sector naming). Gate 0.30, compact small-box rule (<130px ID tag only). Station whites/reds/beiges verified true. Seated overlap rows partial (documented hard case).
- (add here with date)

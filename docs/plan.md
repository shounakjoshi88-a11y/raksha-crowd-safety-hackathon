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
- [ ] Crowd clip test (multi-person): pending, needs dense test video
- Acceptance: 2 sources tracked live, IDs stable through short occlusion, FPS logged.

## Phase 2: Face dossier, one person one file [~] (engine + enroll + match + card done 2026-09-24)
- [x] `raksha/vision/faces.py`: buffalo_s FaceAnalysis, ctx_id=0, det_size 640, thr 0.5 + blur/size gate
- [x] `scripts/enroll.py`: Demo01 enrolled, 3 shots, blur 88-122, gallery/gallery.faiss+json (LOCAL ONLY, never push)
- [x] `raksha/vision/gallery.py`: Faiss IndexFlatIP cosine, thr 0.40, save/load
- [x] Live match `scripts/match_live.py`: 3-frame vote smoothing → Demo01 card, dwell 7.7s
- [x] `raksha/vision/dossier.py`: gid, tracks, trail, dwell, flags, card()
- [ ] Save best snapshot crops to disk per dossier (currently counted, not written)
- [ ] Stranger clustering polish (currently single stranger dossier)
- Acceptance: enrolled face walks in → card pops <0.5s, unknowns clustered not spammed.

## Phase 3: Cross-camera ReID + global ID [ ]
- [ ] botsort.yaml copy with `with_reid: True`, appearance_thresh 0.6, proximity 0.5
- [ ] Split-clip test: same person two views → one global ID (Hungarian on demand)
- [ ] Mini-map trajectory across cam A → cam B
- Acceptance: re-entry keeps global ID in 4/5 trials.

## Phase 4: Crowd brain [ ]
- [ ] Zone density (count/area) + heatmap overlay
- [ ] Farneback flow @320p: stillness + counterflow + entropy features
- [ ] Stampede meter: risk = density_norm x stillness x (1 + counterflow); RED >0.6, YELLOW >0.4
- [ ] Bottleneck box: FTLE-lite or contour-defect on flow segments, 1 Hz
- [ ] Alerts pipeline: <1s wall pop + guard push mock + audit log + clip export hook
- Acceptance: dense test frame → RED + bottleneck box + alert entry with snapshot.

## Phase 5: Harden + demo + submission [ ]
- [ ] ONNX export YOLOv8s, auto frame-skip by FPS, face-blur stored video, 7-day purge flag
- [ ] Demo video: dense → RED → diversion → face search → export (2 min script in `raksha/demo-script.md`)
- [ ] Measured numbers back into deck slide 4 + `docs/RESEARCH.md`
- [ ] Team Leader name into slide 1, export PDF, upload to portal
- Acceptance: PDF uploaded, video recorded, repo tagged.

## Follow-ups discovered during build
- 2026-09-23: onnxruntime 1.27 here is CPU-only build (no CUDAExecutionProvider), so InsightFace runs CPU (~438ms first run). Consider onnxruntime-gpu in Phase 5 if face latency blocks <0.5s card pop. Face runs on crops + skipped frames, so fine for now.
- (add here with date)

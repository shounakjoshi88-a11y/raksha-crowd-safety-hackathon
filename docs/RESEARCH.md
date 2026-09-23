# RAKSHA Deep Research — Real Deal (not toy)

> Solo but good laptop + space. Goal: China-grade live dossier + stampede guard, privacy-first.
> Cloned into `research/` + skills into `.agents/skills/`. This file is the build bible.

## 0. Verdict: will it work? YES
- YOLOv8n+ByteTrack 8-12 FPS i5 1080p, 20 FPS ONNX, assoc <1ms. IoU fallback 64 FPS CPU-only.
- SCRFD + ArcFace buffalo_s 99.5% LFW, 15ms/face, <200ms end-to-end. Faiss 10M top-5 3.8ms. Cosine thr 0.40.
- AURORA hybrid 94.3% acc, 13.8s early warning, 14.8 FPS. Rule shortcut works: density x stillness x counterflow.
- Limits: >45deg profile/mask 89%, >4x1080p streams needs GPU, night needs IR. Mitigate with clothing-ReID + zone logic.

## 1. Official backbones (install these, not toys)
- `ultralytics/ultralytics` 61.9k stars — YOLOv8/v11 + `.track(persist=True)` ByteTrack/BoT-SORT built-in. Docs: tracking, ONNX export.
  https://github.com/ultralytics/ultralytics
- `deepinsight/insightface` 29.6k — SCRFD detect + ArcFace 512-D + buffalo_s/m/l packs. Use `buffalo_s` CPU, `buffalo_l` server.
  https://github.com/deepinsight/insightface
- `facebookresearch/faiss` 40.9k — IndexFlatIP cosine search. <50k IDs flat is fine. 10M needs INT8 + GPU.
  https://github.com/facebookresearch/faiss
- `ifzhang/ByteTrack` — two-stage low-conf assoc, the occlusion fix. Ultralytics bundles it, read paper for high/low thr 0.5/0.1.
  https://github.com/ifzhang/ByteTrack
- `KaiyangZhou/deep-person-reid` — OSNet ReID for cross-cam global ID + Hungarian. Torchreid zoo.
  https://github.com/KaiyangZhou/deep-person-reid
- `leejaymin/CSRNet-pytorch` / `neuro-ml` CSRNet — density maps. Baseline MAE 68.2/115.0 Part A. CBAM variant 61.1/90.9.
- CountingMOT `s ompt22/CountingMOT` — joint counting+tracking for crowds. MOT17 78.0 MOTA, MOT20 70.2 MOTA.

## 2. Ranked GitHub builds (what to steal)
Downloaded to `research/`:
1. `vectornguyen76/face-recognition` 204s — SCRFD + ArcFace + ByteTrack + similarity. **Closest to dossier.** Steal: track-based smoothing, unknown handling, multithread capture.
   `research/face-recognition-SCRFD-ArcFace-ByteTrack`
2. `Abdirayimov/multi-camera-person-tracking` 4s — YOLO + ByteTrack/IoU + OSNet + Hungarian global ID. **Cross-cam blueprint.** Steal: ReidGallery rolling, zone-transition gate, <0.5ms match.
   `research/multi-camera-OSNet-Hungarian`
3. `Felix-au/JanGinti-Counting-the-Pulse-of-the-Crowd` 21s — CSRNet + ShanghaiTech + Indian set + FastAPI+Vite. **Density + India angle.** Steal: density heatmap overlay, zone counts.
   `research/JanGinti-CSRNet-Indian`

Next to clone if time:
- `Zaid-Al-ayoubi/realtime-person-tracking` — YOLOv8+ByteTrack + face verify + FastAPI + Streamlit. Full stack ref.
- `Yousef-7ossam/ByteTrack-Plus-Plus-Person-Tracker` — CPU-only YOLOv8-ONNX + ByteTrack + Kalman + HSV ReID. Best CPU tuning.
- `saadkhan2003/CCTV_Video_Anomaly_Detection` — YOLOv8+OpenVINO crowd/weapon/loitering + glass UI. Anomaly head start.
- `tajwarchy/crowd-anomaly-panic-detection` — ConvLSTM optical-flow + density, 30 FPS M1, auto alert clips. Panic model.
- `NikhilGupta777/CrowdLens` — YOLOv11m + SORT + FastAPI + React 19. Modern wall ref.
- `Kanishk3813/Real_Time_Crowd_Surveillance_System_using_Machine_Learning` — Prayagraj Mahakumbh 2025 finalist. Head count + anomaly + fire. Pitch angle.
- `SthPhoenix/InsightFace-REST` 632s — TensorRT FastAPI face server. Prod face API pattern.
- `jingh-ai/ultralytics-YOLO-DeepSort-ByteTrack-PyQt-GUI` 460s — PyQt wall with pose + tracking. Desktop wall alt.

## 3. Papers (cite in PPT slide 6)
- CSRNet, CVPR18 — dilated CNN density maps. Baseline to beat.
- ArcFace, CVPR19 — additive angular margin, 99.83% LFW. Thr 0.30-0.55, use 0.40.
- ByteTrack, ECCV22 — high+low assoc, IDS 3 with ReID, 62 FPS.
- CountingMOT — count-constrained tracking, MOT20 70.2 MOTA, 12.6 FPS.
- AURORA 2026 — CSRNet + RAFT-lite + Transformer + rules. 94.3% acc, 13.875s lead, 74ms/frame, FAR 0.041.
- Bottleneck FTLE, AVSS19 Simon et al. — Lagrangian flow ridges detect narrowings. Use for Exit logic.
- Stampede Farneback+LSTM — entropy + TOV + KDE vectors, 99% UMN/PETS, 95% GBA, 91% GSMADC.
- STAR-Crowd — ViT-CNN + LSTM-GNN + Meta-RL. 96.3% density, 1.8s early, -22% false alarms, Delhi -37% response. Kumbh 10k set.
- Panic multimodal — CDNet + LSTM + speech, 91.7% Itaewon, 40 FPS GPU.
- JHU-CROWD++ — 4372 imgs, 1.51M ann, weather + distractors. Train diverse.

## 4. Datasets + benchmarks (download order)
1. ShanghaiTech A/B — 1198 imgs, 330k ann. Start here. Part A MAE 87.85 / Part B 21.12 (from-scratch M1 ref).
2. MOT17 / MOT20 — 8 seqs, up to 246 ppl/frame, 1.65M boxes. Tracking must-pass. Test YOLOv8n+ByteTrack vs BoT-SORT.
3. CrowdHuman + MIX (Caltech, CityPersons, CUHK-SYSU, PRW, ETHZ) — train detector for crowds.
4. UCF-QNRF — 1535 imgs, 1.25M ann, 12865 max. High-density test.
5. JHU-CROWD++ — 4372 imgs, 1.51M, weather + occlusion levels + size. Robustness test.
6. NWPU-Crowd — 5k imgs, largest. Scale test.
7. UMN + PETS2009 + GBA-Stampedes + GSMADC (43k frames) — stampede classifier.
8. Custom Indian 20-face gallery + 2 CCTV clips — your demo set. Enroll frontal, test profile/mask.

Metrics: MAE/MSE counting, MOTA/HOTA/IDF1/IDS tracking, TAR@FAR face, FPIR/FNIR 1:N, lead-time seconds + FAR stampede.

## 5. Thresholds that work (copy these)
- YOLO conf 0.25-0.4, IoU NMS 0.45, imgsz 640 CPU / 1280 GPU, 720p + skip 2.
- ByteTrack high 0.5 low 0.1 buffer 30 match 0.8. OSNet cosine 0.6 for global merge, Hungarian.
- Face SIM 0.40 (0.30 loose, 0.55 strict). Buffalo_s CPU, buffalo_l server. Align 112x112.
- Stampede rule: density >4-5/m2 + speed <0.5m/s + counterflow entropy high for >5s = RED. AURORA lead 13.8s target.
- Zones: A Gate, B Food, C Stage, D Exit. Dwell >10min loiter, fall = aspect flip + stillness.

## 6. Skill files (project-local, read before code)
- `.agents/skills/pptx/` — decks only via pptxgenjs + validate --original
- `.agents/skills/frontend-design/` + `ui-ux-pro-max/` + `web-design-guidelines/` — ops-dark wall, no AI slop
- `.agents/skills/brainstorming/` + `systematic-debugging/` — feature then fix loop
- `.agents/skills/computer-vision-opencv/` 3.6k — OpenCV capture, threading, NMS, optical flow
- `.agents/skills/senior-computer-vision/` 1.1k — detection/tracking/ReID review checklist
- Global only: axiom-vision failed Windows long-path, skip. Official `ultralytics/skills@yolo` 114 installs, low trust, use docs directly.
- Registry https://skills.sh — verify >1k installs + audits before new install.

## 7. Real build order (good laptop, GPU if you have it)
1. `research/*` run demos as-is. Record FPS on your machine. Pick ByteTrack++ CPU path or Ultralytics GPU path.
2. Pipeline v1: ingest (webcam/file/RTSP) -> YOLOv8n track -> zone counts + trails + heatmap. Ship wall first.
3. Face v1: buffalo_s enroll 20 -> SCRFD detect -> ArcFace -> Faiss flat -> card pop + unknown cluster. Tune 0.40 on your light.
4. ReID v1: OSNet embeddings per track -> Hungarian cross-cam. Test split-clip same person.
5. Risk v1: Farneback flow + density -> stampede meter + bottleneck box + guard push (PWA/SMS mock). Log audit.
6. Harden: ONNX export, frame-skip auto, blur stored faces, 7-day purge, clip export. Film dense->RED->divert video.
7. Docs: update AGENTS.md + PPT references with your numbers.

## 8. Commands
```powershell
# research runs
# face dossier demo
# multi-cam demo
# density demo
Get-ChildItem D:\Q_project\research
# skills
npx skills find "tracking reid anomaly"
# backend (after build)
# pip install ultralytics insightface onnxruntime faiss-cpu opencv-python fastapi uvicorn
```

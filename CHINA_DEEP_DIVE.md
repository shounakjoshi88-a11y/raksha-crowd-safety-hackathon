# CHINA DEEP DIVE — How Chinese Crowd Surveillance Works Behind the Scenes
> Real-deal blueprint for Raksha. Synthesized from 4 parallel deep tracks (vendors, standards, algorithms, hardware) + GitHub + papers. No timer, full depth.
> Sources: vendor datasheets, GB/GA standards, MOT/CrowdHuman/WIDER benchmarks, deployment histories. See RESEARCH.md for repo links.

## Mega-prompt used (copy to re-run deeper)
```
You are a senior surveillance-systems researcher with unlimited wifi, tools and subagents, no time limit.
Investigate CHINESE crowd-surveillance behind the scenes at maximum depth:
1) Vendors: Hikvision DeepinView/HikCentral, Dahua WizMind/DSS Pro, SenseTime SenseCrowd/Foundry, Megvii Pangu/Face++, Yitu Dragonfly, CloudWalk VisionCloud, Huawei HoloSens IVS1800/3800. For each: camera models, onboard TOPS, faces/frame, DB sizes, channels, latency claims, APIs.
2) Standards: GB/T 28181-2022 video networking, GB/T 25724 SVAC, GA/T 1400.1-4 view-library (Face/Person/Vehicle/Thing/Scene XSD fields), GB 35114 security, GB/T 35678 face quality, Decree 799 retention. List every person-record field.
3) Deployments: Skynet/Tianwang, Sharp Eyes/Xueliang, Safe City, Bund 2014 lesson, Tiananmen, Chunyun rail, Jacky Cheung concerts. Ops playbook for bottleneck/stampede.
4) Algorithms: detection (YOLO-GSD/DPDN/RT-DETR/DEYO), tracking (ByteTrack/BoT-SORT/OC-SORT/FairMOT/CountingMOT MOT20 numbers), face (SCRFD+ArcFace/AdaFace), ReID (OSNet/TransReID + Hungarian), counting (CSRNet/DM-Count/APGCC), flow/stampede (Farneback/RAFT + FTLE + LSTM + AURORA/STAR), search (Faiss/Milvus INT8/RABITQ/HNSW latencies).
5) Hardware: HiSilicon Hi3519AV200 8.1 TOPS, Hi3559A, BM1684/X 17-32 TOPS, Ascend 310 16 TOPS, Cambricon MLU220/270, Horizon J2-J6, DeepinMind NVR 64ch/400Mbps/24ch-face/500k pics, IVS1800/3800 sizing, SSD math for 8-cam 7-day.
Return product names + numbers + URLs + thresholds. Exhaustive. This feeds a real build.
```

## 1. End-to-end in 30 seconds (what feels like magic)
```
Smart IPC (detect/track/capture/grade on-camera, 1-5 TOPS)
 -> best snapshot + 512-D face + body attrs + quality (only 1-10 pics/sec uplink, not video)
 -> Edge NVR/IVS (16-128ch aggregate, dedup per trackID, buffer/store-and-forward)
 -> Dual uplink: GB/T 28181 video (SIP/RTP, 512k/2M/2.5M, <=2s) + GA/T 1400 VIID objects (Face/Person JSON + crops)
 -> Center: parse-center (GPU 10x CPU) -> MQ (Kafka) -> HBase/MySQL meta + Solr/ES text + Faiss/Milvus vectors + MinIO/Ceph objects
 -> Apps: capture wall + one-person-one-file + trajectory + blacklist alarm (<0.5-1s LAN, 2B/sec search, 18M in 2s)
 -> Ops: one-way loops, wave gates, PA/SMS diversion, grid teams, 30d video / 90d key / years metadata / 6mo logs
```
Why it scales: idle cams send kbps keepalive + counts. 15k cams at 4Mbps would be 60Gbps if raw. Structuring cuts WAN 10-100x. Video fetched on alarm via cascade.

## 2. Vendors (steal this)
- **Hikvision:** iDS-2CD7586G0/7186G2 DeepinView 8MP — 120 faces/frame, 40 pics/frame, 10/s upload, yaw +-60 pitch +-30, 7-8 face + 13 body + vehicle attrs. DeepinMind NVR 64ch 400Mbps, 24ch face/struct, 500k pics. HikCentral Pro 1M faces/64 groups, 3000 cams/group, 1000 events/s, ISAPI + Artemis OpenAPI (`pictureRecognitionModel`, `captureSearch`, `body`). Fusion server 256ch, 384 pics/s, 3M libs, 18M search 2s.
- **Dahua:** WizMind X IPC-HFW7842H-Z 8MP — dual-intel, 200k faces on-cam, 6 face + 8 expressions + 14 body + crowd map/count/heatmap/AcuPick. IVSS7108 128ch 512Mbps, 40ch face IPC, 500k pics. DSS Pro V8.5 distributed 20k ch/4PB, 5k face ch, 20M records, 50 captures/s. AcuPick 2.0 = one-pick ReID across cams (copy this UI).
- **SenseTime:** SenseFace/SenseTotem + SenseCrowd + SenseFoundry + SenseCore 40k PFlops. 21/106/240 keypoints ms-level, 1:1 >99%, age +-5y 99%, attr 97%. City portrait clustering + trajectory.
- **Megvii:** MegEye-D cams + MegCube-B4H 16ch 28.8T 300k faces + Hongtu 256ch + Pangu 2000 devices 1M dynamic. Face++ cloud fields: face_token + rect + 83/106 landmarks + gender/age/smile/pose/blur/emotion/beauty/quality + body skeleton/attrs. Compare 500ms. `CrowdDetection` CVPR20 code + MegEngine open.
- **Yitu:** Dragonfly Eye — one-person-one-file originator. 2B DB seconds, 1.8B photos, billion <3s, 20 provinces 300 cities, Metro 567 in 3mo. FRPC/FRVT #1 x3.
- **CloudWalk:** Dig edge + VisionCloud. Cross-mirror ReID mAP 91.14 Market1501, NIST boarding leader. Face+body fusion for occlusion.
- **Huawei:** SDC 5MP 1T crowd-flow cams + IVS1800 (16ch/160M/4T, 128ch/512M, 20T 48ch image) + IVS3800 (3024ch/2048M, 384T 288ch face, 2B match/s, 1TB→3TB 90d). Hot <3s cold <10s. Cleanest hierarchy to copy.

All on US Entity List — copy tech, not procurement.

## 3. Standards (the real schema)
- **GB/T 28181-2022:** SIP/RFC3261 + RTP/RTCP + PS, 20-digit DeviceID, 25fps Class I/II, 512k front-center / 2M key / 2.5M center-center, E2E <=2s, H.265/AAC, precise PTZ. = video联网.
- **GA/T 1400.1-4 (2017):** view-library. `.1`采集前端/平台/视图库/分析/应用/共享. `.2` search + trajectory + 以图搜图 + auth + 6mo logs. `.3` DB objects. `.4` REST `VIID/Faces|Persons|MotorVehicles...` XML/JSON + register/keepalive/NTP + cascade + 布控/告警/订阅/通知.
- **FaceObject fields (req):** FaceID, InfoKind, SourceID, DeviceID, bbox LeftTopX/Y RightBtmX/Y, LocationMarkTime, Appear/DisAppearTime (YYYYMMDDHHMMSS), IDType/Number, Name, GenderCode, Age limits, Ethic/Nationality/Native/Residence, Skin/Hair/Face/Facial/Physical, Respirator/Cap/Glass, IsDriver/Foreigner/Terrorist/Criminal/Detainee/Victim/Suspicious (0/1/2), Similaritydegree 0-1, Eyebrow/Nose/Mustache/Lip/Wrinkle/Acne/Freckle/Scar/Other, SubImageList (Type 11 face crop + 14 panorama + base64/URI), RelatedList 01→PersonID.
- **PersonObject adds:** Height limits, BodyType, Gesture/Posture/Status, Behavior + desc, Appendant, Umbrella/Scarf/Bag/Coat/Trousers/Shoes style+color, plus all IsXXX.
- **SubImage:** ImageID, EventSort (9 person 10 face), DeviceID, StoragePath, Type, Jpeg, ShotTime, W/H, Data. Typical push 50-150KB (JSON 1-3KB + 512-D 2KB / INT8 0.5KB + face 5-20KB + panorama 30-100KB).
- **No Embedding field in XSD** — vectors live in analysis engine (GA/T 1399) + `FeatureValue` sidecar + `Similaritydegree`. Quality via GB/T 35678 (pose/illum/completeness) + vendor gates.
- **Motor/NonMotor/Thing/Scene:** plates, speed, direction, colors, parts + Scene.PopulationDensity/DenseDegree + weather. = density hook.
- **GB 35114-2017 + GA/T 1788.1-2021:** encrypted transport, certs/keys, gateway isolation, role/IP/multi-login, audit.
- **Decree 799 (2025-04-01):** video >=30d, delete when done, file cam count/duration in 30d. Anti-terror key >=90d, crime/burst >=2y. Logs >=6mo, PIPIA >=3y. Face in-device, minimum necessary, >10k filing, visible signs, banned in rooms/baths. No face-only gate if alt works.

## 4. Algorithms (numbers to build to)
- **Detect:** YOLOv8n CrowdHuman mAP50 80.5 / 50:0.95 49.5, 3M 8.2G 60 FPS 3060 / 15 CPU ONNX. GSD +P2/Ghost/DySample/SEAM/WIoU 86.5 (+2.2) 6.2M 106 FPS. DPDN 85.6/55.1 5.2M. Dense-M 92.7 AP 82G. RT-DETR-R50 53.1 AP 108 FPS T4 NMS-free (control-room GPU). DEYO 92.3 AP50 97.3 R (recall king). P2 stride-4 for <16px heads (+2-4% small, +30-50% FLOPs). Raksha CPU: YOLOv8n/11n+P2 720p skip-2 ONNX INT8. GPU room: RT-DETR/DEYO.
- **Track MOT20 (200+):** FairMOT 61.8/67.3 (fails dense 103k FP). ByteTrack 77.8/75.2 1223 IDS 17.5 FPS (default, 700 FPS assoc). OC-SORT 75.5/75.9 913 IDS. BoT-SORT-ReID 77.8/77.5 1257 IDS (prod default). Deep OC 75.6/79.2 63.9 HOTA 779 IDS. CountingMOT 70.2/72.4 cuts FP 103k→33k (+density head almost free). v2 YOLOX 78.9/78.6 best MOTA. Recipe: YOLO conf 0.5/0.1 + ByteTrack buf-30 match-0.8, no live ReID. CMC only for PTZ/drone. OSNet-0.25x on demand + Hungarian.
- **Face:** SCRFD-0.5G 68.5 Hard 0.57M 3.6ms / 2.5G 77.9 0.67M (~25ms CPU, sweet spot) / 10G 83.1 / 34G 85.3. Align 112x112 1-2ms. ArcFace R100 LFW 99.83 IJB-C 96.03 15ms GPU / 80ms CPU. AdaFace R100 IJB-C 96.89 + low-quality S-to-S 65.3 vs 57.3 (use for blur). Buffalo_s ~10ms 512-D compatible. Cosine thr 0.40. Best-snapshot: score=0.35 size+0.25 sharp(Laplacian)+0.20 frontal+0.10 illum+0.10 norm; reject blur<40 occ>40 yaw>45 eye<25px; keep top-3/track, enroll on +0.05 gain (10x QPS save).
- **ReID:** OSNet 2.2M Market 94.8/84.9 MSMT 78.7/52.9 ~10ms GPU / 30ms CPU (edge default). TransReID ViT 96.7/93.2 MSMT 89.6/75.0 86M 50ms GPU (server ceiling). Cloth-change: CAL/CCVID/FIRe2; <12h same-clothes OSNet fine, multi-day fuse face+height+gait. Hungarian cost=0.5 body+0.4 face+0.1 dt+topology inf, Faiss top-20 prefilter 0.5-2ms + Hungarian 100x100 1-3ms.
- **Count:** MCNN 110/173 A 26/41 B. CSRNet 68/115 A 10/16 B 16M 26 FPS GPU / 5 CPU. BL 62/101 A 7/12 B. DM-Count 59/95 A 7/11 B 85/148 QNRF 88/388 NWPU (stable, tradeoff king). SASNet 53/88 A. P2PNet 52/85 A 6/9 B. APGCC 48/76 A 5/8 B 71/284 NWPU 18M 0.07s (fastest point, localizes → feeds tracker). SAANet 66/298 NWPU No.1. Raksha: CountingMOT P4 head or DM-Count/APGCC every 10th frame @320p (~200ms CPU ok for meter).
- **Flow/stampede:** Farneback 54 FPS UMN 320p / 22 PETS 768p CPU, 20ms worst (default). RAFT 1.43 EPE +8% pushing vs Farneback, 10 FPS GPU / 2 CPU (forensic). Risk=ρ_norm×stillness×(1+counterflow): ρ>4 risky >6 critical, still <0.5px/frame 5s, counter>0.4. Entropy+TOV+KDE→LSTM 99% UMN/PETS 95% GBA 91% GSMADC <6ms GPU / 20ms CPU (live king). CNN-LSTM 99.75 4-level. FTLE ridges persist 10s + ρ rise = bottleneck (50-100ms CPU 80x45 grid 1Hz). Honest leads: 0.5s detect + 10s ConvLSTM forecast + 60s FTLE watch. Vendor 30s-5min claims need gate+phone fusion, not vision alone.
- **Search 512-D:** 1M=2GB FP32. Faiss IVF_FLAT 236 QPS 4ms. Milvus SQ8 0.5KB (-75%) ~500 QPS 2x (-1-2% recall, Raksha default). RABITQ 32x 864 QPS ~FLAT recall (billion-scale). PQ 8-32B 0.03-0.5ms (10M-1B RAM<32G). HNSW 7-20k QPS 98%+ (live <5M). Raksha: 10k Flat 0.2ms / 100k HNSW/SQ8 0.5-1ms / 1M SQ8 1-3ms. Pipeline 4+1+10+1=16ms GPU / 50ms CPU → <0.5s pop easy.

## 5. Hardware sizing (good laptop + optional edge)
- **SoCs:** Hi3519AV200 8.1T (2.5 open) 4.9W 4K30 / Hi3519A 2.0T / Hi3559A 4T board / Hi3559V200 0.4T 1.1W. BM1684 17.6/35.2T 32x1080p25 18W. BM1684X 32 INT8/16 FP16 32ch. Ascend 310 16 INT8/8 FP16 16ch 8W (HoloSens). 310B 20T. MLU220 M.2 8T 8.25W / SOM 16T 15W 16ch. MLU270 128T 150W server. Horizon J2 4T/2W J3 5T/2.5W J5 96-128T/20W J6 80-128T/15W. Rule: 1-2.5T=1x4K/2x1080p full analytics 25-30fps. 5T=flagship 120 faces+vehicle+body.
- **Cams (buy 2):** Hik ColorVu DS-2CD2347G2 4MP F1.0 ~$150 (night faces) + Dahua HDW5442T 4MP Starlight varifocal ~$175 (choke FoV ≤2.5m@2MP ≤4.2m@6MP, horiz <10°, vert 10±3°, h 2.5-3.5m). Showpiece: DeepinView iDS-2CD7 4MP ~$500 5T 120 faces 150k lib (camera already structured). Borrow 6x ONVIF + 2x USB enroll + 4x file loops via ZLMediaKit RTSP.
- **Edge:** DeepinMind 64ch 400M 24ch-face/struct 500k pics 160TB RAID. IVS1800-C08 16ch/160M/4T 5M feats <3s / D16 128ch/512M / E16 20T 48ch image. IVS3800C 384T 288ch-face 2712 img/s / R 2B/s 8M blacklist / AS34C 1TB→3TB 450ch-90d. Jetson Orin Nano 8G 20D/40S/$249 11x1080p30 7-15W (4-8ch YOLO+ArcFace) vs laptop 4060 120-240T 6-10x Nano (8ch + Milvus + train same box). Ideal both: Nano pole → laptop mini-3800.
- **Net:** GbE PoE 60-120W (TL-SG108PE 64W $60 / GS308PP 83W $110). 7x6W+12W=54W ok. Cat5e 15-30m x8.
- **SSD 8-cam 7d:** TB=Mbps×cams×86400×days/8/1e6 +20%. 1080p H.265 15fps 1.35M →117G/d →0.82T/7d →buy 2T. 4MP 15fps 2M →173G/d →1.21T →2T tight →4T. 4MP 25fps 4M →346G/d →2.42T →4T. Snaps tiny: 10k/d×100K=1G/d, feats 20M/d. Buy 2T NVMe +1T SATA / 4T Purple, or 1x4T NVMe $220-280. NVR BW 32M << GbE.

## 6. Deployments (ops, not just AI)
- **Bund 2014-12-31:** 300k Chen Yi Sq, 23:35 counterflow stairs →36 dead 49 inj. Police 6k→700, light cancel, coupons post-crush (video proof), 11 punished. Fix: reservation+slots, one-way+wave+cordons, caps, metro skip, ambulance lanes. CCTV as evidence standard.
- **Tiananmen/Beijing:** HD+thermal+panoramic, face gates + real-name reserve, grid policing, PGIS patrol. Subway AI triage normal/enhanced. Fudan 500MP stadium-wide face cam.
- **Chunyun rail:** LLVision glasses 7+26 in days, ticket-gate face+ID, 5k pairs retimed. WaPo Face++ gender/clothes/tracking demo.
- **Concerts:** Nanchang 60k Ao caught in seat 2018, Jiaxing 20k Yu on exit, beer fest 25. Pattern: entrance gates + ticket-ID + VIID布控 → plainclothes inside/exit (avoid crush). Hik alarm 503 gathering crowds.
- **Ops stack:** permit+risk → sensing (count/heat/flow) → control (one-way/pens/waves/PA/SMS/screens/metro) → response (grid+lane) → review (VIID trajectory accountability).

## 7. Legal/ethics (cite as differentiator)
CSL17 + DSL21 + PIPL21 + Decree799 (2025-04-01: ≥30d, filing 30d) + Face Measures Order19 (2025-06-01: non-mandatory, in-device, minimum, >10k filing 30d, signs, ban rooms/baths, PIPIA 3y) + SPC21 (face=PI, no forced mall/station). Sensitive PI needs separate consent+PIPIA. Video+VIID city-scale = important/core data → assessments + cross-border approval. Raksha: opt-in + alt gate, no Aadhaar join, blur store, 7d purge demo (stricter than 30d floor), signage + filing mock, role/IP audit 6mo+, GB35114 crypto.

## 8. Raksha blueprint (copy order)
1. Run `research/*` demos, record your FPS. Pick ByteTrack++ CPU or Ultralytics GPU path.
2. Wall v1: ingest 720p skip-2 → YOLOv8n-P2 ONNX → ByteTrack → zones/trails/heatmap.
3. Dossier v1: buffalo_s enroll 20 → SCRFD-KPS → ArcFace → Faiss SQ8 → card + unknown cluster @0.40 + smoothing.
4. ReID: OSNet-0.25x on demand → Hungarian + zone gate → global ID split-clip test.
5. Risk: Farneback 320p entropy/TOV/KDE + density → meter + FTLE 1Hz box + PWA/SMS mock + audit.
6. Harden: TensorRT/ONNX, auto skip, blur store, 7d purge, clip export. Film dense→RED→divert.
7. Docs: numbers into AGENTS.md + PPT refs.

Files: `RESEARCH.md` repos/papers/datasets, `.agents/skills/*` 8 skills, `research/*` 3 clones, this file = why/how China does it.

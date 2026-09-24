# RAKSHA Research V2 — Crowd-Physics Rebuild (replaces RESEARCH.md claims)

> Status: evidence-backed. Every number below was quoted from a source by one of five
> parallel research sweeps (density models, geometry, physics, flow anomaly, deployments),
> Sept 2026. Confidence tags: High / Medium / Low. Anything Low is NOT deck-safe.
> Supersedes: `docs/RESEARCH.md` sections on AURORA / STAR-Crowd / FTLE / Farneback+LSTM
> (verdict: UNSOURCED — see §8, do not cite).

## 1. Verdict in one page

Bounding-box tracking (YOLO + ByteTrack) undercounts under severe occlusion — verified:
Faster R-CNN localization F1 **0.068** vs point-based P2PNet **0.712**; on NWPU-Crowd,
hybrid detector Reg+Det MAE **264.9** (worst of 10 methods) vs CSRNet **121.3** vs
Bayesian Loss **105.4**. DM-Count states density maps beat detection-then-counting
because they are "less sensitive to occlusion and do not commit to binarized
decisions at an early stage." The rebuild pivots to: **perspective-aware density
heatmaps + optical-flow velocity field + pressure/accumulation risk**, with YOLO kept
only as a low-density (<2/m²) cross-check, never the primary counter.

Three honest bounds the old deck violated (all verified):
1. **No 10–15 min automated prediction claim.** No published system demonstrates it
   (High-confidence negative). Kumbh 2025 ran AI density + threshold alerts and the
   Jan 29 crush still killed 30 officially. Claim "tens of seconds to minutes" only,
   measured on our own bench.
2. **No metric persons/m² from uncalibrated cameras.** Perspective distortion is real
   (2.4× foreground/background size ratio, Chan et al.), but per-camera homography
   needs surveyed ground points or months of prep (Kumbh: 3-month camera surveys +
   per-camera ground-area teaching for 85–95% count accuracy). Calibrate fixed choke
   points once; use relative indices + self-calibration elsewhere.
3. **"Crush Index = ρ × (∇·v)" as a named formula is unsupported.** No paper validates
   that exact product. The validated metric is Johansson's **crowd pressure
   p = ρ · Var(V)** (density × velocity variance), plus divergence as an inflow–
   outflow accumulation signal (Nakayama BMVC 2025). Frame the engine as
   pressure + continuity-forecast, not a named index.

## 2. Validated component stack

### 2a. Density: heatmaps, not boxes
| Model | Paper | SHA MAE | SHB MAE | QNRF MAE | Repo / note |
|---|---|---|---|---|---|
| CSRNet | CVPR 2018 (Li, Zhang, Chen). VGG-16 front + dilated back-end, density-map regression. https://arxiv.org/abs/1802.10062 | 68.2 | 10.6 | — (predates) | leeyeehoo/CSRNet-pytorch, 735★, **no declared license** |
| Bayesian Loss | ICCV 2019 Oral (Ma et al.). Point supervision without Gaussian maps. https://arxiv.org/abs/1908.03684 | 62.8 | 7.7 | 88.7 | zhiheng-ma/Bayesian-Crowd-Counting, 343★, **no declared license** |
| DM-Count | NeurIPS 2020 Spotlight (Wang et al.). Optimal Transport + TV loss. https://proceedings.neurips.cc/paper/2020/.../118bd558033a1016fcc82560c65cca5f-Paper.pdf | 59.7 | 7.4 | 85.6 | cvlab-stonybrook/DM-Count, 245★, MIT |
| P2PNet | ICCV 2021 Oral (Song et al.). Point proposals + Hungarian matching, joint count+localize | 52.7 | 6.3 | 85.3 | TencentYoutuResearch/CrowdCounting-P2PNet |
| STEERER / APGCC | ICCV 2023 / ECCV 2024. Current SOTA class (APGCC SHA 48.8, SHB 5.6, QNRF 80.1; STEERER NWPU-test 63.7) | 48.8 | 5.6 | 80.1 | apgcc.github.io ; taohan10200/STEERER |

Speed (measured, quoted): CSRNet **26.1 FPS** / BL **34.7 FPS** at only 576×768 on
unspecified GPU (NWPU paper Table IV — Medium confidence, small res, unknown card).
**No measured CSRNet-class FPS at 720p on Jetson Orin Nano or RTX 4050 exists in
literature — do not claim it.** Lightweight options with measurements: LCDnet
(0.05M params, 20× lower delay than CSRNet, tested Jetson Xavier NX + Nano);
Zhao 2025 micro-net (0.15MB, 71.9 FPS on Jetson TX1 @576×768). Our deck must cite
**our own bench** for the ≥25 FPS claim (see §9).

### 2b. Geometry: perspective first, homography where it pays
- Chan, Liang & Vasconcelos, CVPR 2008: weight pixels by perspective map
  (foreground objects ~2.4× background). http://www.svcl.ucsd.edu/publications/conference/2008/cvpr08/cvpr08_peoplecnt.pdf
- WorldExpo'10 perspective maps: M(x) = pixels per meter; sets Gaussian σ.
- Shi et al., PACNN, CVPR 2019: network predicts perspective map from image
  (mean height 1.75 m assumption).
- Zhang & Chan, CVPR 2019: project densities via homography to ground plane,
  multi-view fusion (PETS2009, DukeMTMC, CityStreet).
- Self-calibration (heads+feet → vanishing point, assume 1.8 m): <4% height /
  <10% distance error near field, up to 16%/50% far field — usable for relative
  indices, not alarms.
- Vendor reality: BriefCam docs state per-camera calibration is necessary for
  people counting. Kumbh 2025: ~2,751 CCTVs, 3-month site surveys, per-camera
  ground-area teaching, 85–95% accuracy, alarm at **>3 persons/m²**.
- Rule: full homography for fixed choke points (gates, stairwells — surveyed once);
  geometry-adaptive kernels (σ = 0.3 × k-NN head distance, MCNN-style) or PACNN
  perspective maps everywhere else; line-crossing counts at entries.

### 2c. Flow: velocity field at 720p30
Measured speeds: DIS optical flow **300–600 Hz single CPU core** @1024×436;
NVIDIA hardware flow (NVOFA) **up to 150 FPS @4K / hundreds of FPS @1080p**;
FastFlowNet 90 FPS on GTX 1080Ti but only 5.7 FPS on Jetson TX2; RAFT 10 FPS on
1080Ti (too heavy for edge). Choice: **DIS on CPU or NVOF on NVIDIA GPUs** for the
streakline front-end; learned flow only as fallback. (No 720p Farneback number is
citable — our old "optical-flow stall meter" line survives only if we bench it.)
Theory: Mehran, Oyama & Shah, CVPR 2009 (social-force abnormality); Mehran, Moore
& Shah, ECCV 2010 (streakline representation); Ali & Shah, CVPR 2007 (Lagrangian
particle dynamics). Note: no maintained streakline-anomaly repo exists; datasets
(UMN, UCSD, CUHK Avenue, ShanghaiTech Campus) label overt anomalies, **not**
pre-stop turbulence — so our precursor labels must come from our own annotated
clips + Helbing pressure thresholds.

### 2d. Risk: pressure + accumulation, honestly framed
- Helbing & Molnár, Phys. Rev. E 51:4282 (1995). DOI:10.1103/PhysRevE.51.4282 —
  pedestrians as particles under social forces; reproduces lane formation,
  oscillations. (Justification, not runtime code: full SFM needs trajectories.)
- Helbing, Johansson & Al-Abideen, PRE 75:046109 (2007, Hajj/Jamarat video,
  https://arxiv.org/abs/0708.3339): laminar → stop-and-go → turbulent; mean 6/m²
  with local peaks 9/m²; speed ~18 m/min at 6/m²; control lost ≥7/m².
- Johansson et al. 2008 (https://ar5iv.labs.arxiv.org/html/0810.4590): **crowd
  pressure p = ρ·Var(V)**; "density, speed, flow alone are NOT good criticality
  indicators." Turbulence onset ≈ 0.02/s² (Medium).
- Fruin: crowd ~fluid mass at **7/m²** (shockwaves throw people 3 m+); serious
  crush risk **>4/m²**; flow peaks then drops at **2–3/m²**.
  https://www.gkstill.com/Support/crowd-flow/fruin/Fruin1.html
- LWR (Lighthill–Whitham 1955, Richards 1956) + Hughes 2002 continuum: jams
  propagate as shockwaves; inflow-minus-outflow forecasts the jam — the honest
  ancestor of any "divergence" signal.
- Nakayama & Onishi, BMVC 2025: divergence-based Crowd Risk Score from head
  tracking, validated on real event footage (Medium — conference paper).
- Harding, Gwynne & Amos, PLoS ONE 2011 (https://arxiv.org/abs/1008.2160):
  mutual-information crush detector, **simulation only**, video real-time as future
  work. Closest to "early warning method" — and it proves the gap, not the claim.
- Operational rule (ours, stated as engineering thresholds, not physics law):
  **WATCH** at ρ ≥ 2.5/m² rising; **RED** at p = ρ·Var(V) crossing calibrated
  threshold OR continuity forecast showing ρ → 4/m² within horizon. Lead time:
  "tens of seconds to a few minutes," measured per site — never "10–15 minutes."

## 3. Why dashboards alone fail (the Kumbh lesson — cite it)
Maha Kumbh 2025: 2,751 CCTVs (hundreds AI-enabled), 4 ICCCs, density-map + head-count
models trained on 2024 footage, entry/exit line-crossing, per-m² density with flow
alerts — and the Jan 29 Mauni Amavasya crush still killed 30 officially (~40 per
Reuters morgue sources, up to 82 disputed). Trigger: barricade-jump + 90–100M
attendees that day. Lesson for slide 5: **detection without actuation kills.**
Our impact story must be upstream diversion (overflow gates, held entries) with a
human confirming — not a prettier dashboard.
Itaewon 2022: 159 dead / 196 injured in a 3.2 m × 40 m alley; 11 emergency calls
from 18:34 ignored; no automated trigger. Lesson: the signal existed for ~4 hours
in human eyes; automation must page a human, loudly, early.

## 4. Edge + privacy (feasibility, honestly)
- Pattern (not one paper): process on the edge node, send JSON metadata
  (density, flow, pressure per zone), discard raw video. Ancestor: GigaSight
  (Satyanarayanan et al.). Context numbers: PeopleNet-ResNet34 INT8 ≈172 FPS on
  Xavier NX (detection baseline — NOT a density-map number, label it as such);
  real-world Orin Nano 3-stream ≈20 FPS/stream (field report).
- Privacy by architecture: density maps cannot identify individuals. Cite Chan et
  al. CVPR 2008 — literally titled **"Privacy Preserving Crowd Monitoring:
  Counting People without People Models or Tracking."** Plus Marzani et al.,
  ARES 2025 (density maps + low-res preserve privacy). Face modules stay out of
  the core entirely (Phase-2, opt-in, B2G plug-in — unchanged from pass 3).
- No mature OSS end-to-end stack (density + alerting + dashboard) exists — state
  "compose CSRNet-class + DIS/NVOF + custom wall," never "reuse existing."

## 5. Disaster reference table (slide 2/5 ammo, Reuters/AP/BBC only)
| Event | Toll | Precursor worth naming |
|---|---|---|
| Itaewon, Seoul, 29 Oct 2022 | 159 dead, 196 injured | 3.2 m × 40 m sloped alley, bidirectional flow, 5–9/m² estimates, 11 ignored calls |
| Love Parade, Duisburg, 24 Jul 2010 | 21 dead, 500+ injured | single tunnel+ramp in/out, bidirectional surge; turbulence/quake, not "panic" |
| Maha Kumbh, Sangam, 29 Jan 2025 | 30 official (disputed to ~82) | barricade-jump, 90–100M that day, AI alerts present but no prevention |
| Hathras satsang, 2 Jul 2024 | 121 dead | permit 80k vs ~250k actual, exit rush, blocked narrow exits |
| Astroworld, Houston, 5 Nov 2021 | 10 dead, compression asphyxia | 50k, quadrant enclosed on 3 sides |
| Shanghai Bund, 31 Dec 2014 | 36 dead | ~300k, stair up/down conflict, scaled-down show, thin policing |

## 6. Slide-6 citation pack (all verified, paste-ready)
1. Li, Zhang & Chen, **CSRNet**, CVPR 2018. https://arxiv.org/abs/1802.10062
2. Ma et al., **Bayesian Loss for Crowd Count Estimation**, ICCV 2019 Oral. https://arxiv.org/abs/1908.03684
3. Wang et al., **DM-Count**, NeurIPS 2020 Spotlight. https://proceedings.neurips.cc/paper/2020/file/118bd558033a1016fcc82560c65cca5f-Paper.pdf
4. Chan, Liang & Vasconcelos, **Privacy Preserving Crowd Monitoring**, CVPR 2008. http://www.svcl.ucsd.edu/publications/conference/2008/cvpr08/cvpr08_peoplecnt.pdf
5. Zhang & Chan, **Wide-Area Crowd Counting via Ground-Plane Density Maps**, CVPR 2019. https://openaccess.thecvf.com/content_CVPR_2019/html/Zhang_Wide-Area_Crowd_Counting_via_Ground-Plane_Density_Maps_and_Multi-View_Fusion_CVPR_2019_paper.html
6. Helbing & Molnár, **Social force model for pedestrian dynamics**, PRE 51:4282, 1995. DOI:10.1103/PhysRevE.51.4282
7. Helbing, Johansson & Al-Abideen, **Dynamics of Crowd Disasters**, PRE 75:046109, 2007. https://arxiv.org/abs/0708.3339
8. Johansson et al., **From Crowd Dynamics to Crowd Safety: A Video-Based Analysis**, Adv. Complex Syst. 2008. https://ar5iv.labs.arxiv.org/html/0810.4590
9. Mehran, Oyama & Shah, **Abnormal Crowd Behavior Detection Using Social Force Model**, CVPR 2009. https://vision.eecs.ucf.edu/papers/cvpr2009/CVPR09_Mehran.pdf
10. Mehran, Moore & Shah, **Streakline Representation of Flow in Crowded Scenes**, ECCV 2010. https://www.crcv.ucf.edu/projects/streakline_eccv
11. Hughes, **Continuum theory for the flow of pedestrians**, Transp. Res. B, 2002. DOI:10.1016/S0191-2615(01)00015-7
12. Nakayama & Onishi, **Quantifying Risk Using Divergence from Head-Tracking Flows**, BMVC 2025. https://bmvc2025.bmva.org/proceedings/1024 (Medium — newest, least battle-tested)
13. Fruin via Still, crowd density/flow thresholds. https://www.gkstill.com/Support/crowd-flow/fruin/Fruin1.html
14. Test footage: Wikimedia Commons public footage (station, crossing, temple) — unchanged.

## 7. Rebuilt 6-slide flow (maps to this file)
1. **Title** (template): Raksha — Predictive Crowd Physics & Bottleneck Prevention.
2. **Problem**: reactive 2D CCTV; stillness = too late (pressure already transferred);
   Kumbh-2025 lesson (alerts existed, 30 dead — §3); Itaewon (11 ignored calls).
   True problem = invisible pressure + no actuation.
3. **Pipeline** (replaces Watch→Warn chevrons): **Calibrate** (homography at choke
   points, perspective maps elsewhere — §2b) → **Map density** (CSRNet-class
   heatmaps, benchmark table §2a) → **Track flow** (DIS/NVOF velocity field — §2c)
   → **Forecast pressure** (p = ρ·Var(V) + continuity accumulation — §2d).
4. **Feasibility**: OUR bench (lightweight density FPS + DIS FPS on RTX 4050 — §9)
   + edge JSON-only pattern + calibration honesty + privacy by architecture (§4).
5. **Impact**: upstream actuation (overflow gates, held entries, HITL confirm),
   target venues (railway concourses, Kumbh holding areas, stadium chokepoints).
6. **References**: §6 pack (drop AURORA/STAR-Crowd/FTLE/37% — §8).

## 8. Dropped claims (never cite again)
- "AURORA warning model / 94.3% / 13.8s lead" — no paper, venue, URL, or repo found
  anywhere; RESEARCH.md numbers are unsourced. DROP.
- "STAR-Crowd / Delhi −37% response" — same; DROP. (Kumbh-2025 lesson replaces it
  and is stronger: real deployment, real failure, real lesson.)
- "Bottleneck FTLE (AVSS19 Simon)" — unsourced; DROP (already out of deck).
- "Stampede Farneback+LSTM 99% / Panic CDNet 91.7% Itaewon" — unsourced; DROP.
- "Predicts 10–15 min ahead" — High-confidence negative; DROP.
- "CSRNet ≥25 FPS @720p on Jetson/laptop" — unverified; replace with own bench.
- YOLOv8+ByteTrack as primary counter — demoted to low-density cross-check only.

## 9. Measurements to run before rebuilding the deck (next step)
1. `bench_physics.py`: CSRNet-pytorch (or LCDnet-style light net) inference FPS @720p
   and @576p on RTX 4050, FP32 vs FP16; DIS flow FPS @720p on CPU; NVOF if SDK present.
2. Perspective demo: one concourse clip, geometry-adaptive density vs flat — show the
   2.4×-class correction visually for slide 3.
3. Pressure/divergence trace on station clip: plot ρ, mean speed, Var(V), and
   p = ρ·Var(V) over time; confirm stop-and-go precursor shape for slide 4.
4. Homography: calibrate one fixed view with 4 ground points; report persons/m² vs
   uncalibrated for the same frame (slide-3 honesty footnote).

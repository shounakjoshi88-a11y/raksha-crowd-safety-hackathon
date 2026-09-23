# AGENTS — Raksha Crowd Safety (full-fledged, not toy demo)

> Solo hackathon, <24h. Problem #2: Improving Safety at Large Public Events.
> Goal: China-grade live tracking + instant person dossier, ethical & privacy-first.
> This file is the agent's reference. Follow skills below for every task.

## Project source of truth (repo layout)
- Problem statements: `docs/Hackathon Problem Statement .md`
- Submission deck: `deck/Raksha_Hackathon2026_Final.pptx` (6 slides, exact college template)
- Template: `deck/HACKATHON 2026.pptx`
- Research: `docs/RESEARCH.md` (build bible) + `docs/CHINA_DEEP_DIVE.md` (Chinese stack blueprint)
- Living build tracker: `docs/plan.md`
- Prototype: `raksha/backend/main.py`, `raksha/frontend/index.html`, live vision `raksha/vision/`
- Dev helpers: `scripts/smoke_env.py`, `scripts/bench_track.py`

## Installed skills (project-local copy + global)
Project-local (use these first):
- `.agents/skills/pptx/SKILL.md` — ANY .pptx work. Mandatory.
- `.agents/skills/frontend-design/SKILL.md` — dashboard / control-room UI distinctiveness
- `.agents/skills/ui-ux-pro-max/SKILL.md` — UI structure, palettes, UX rules, charts
- `.agents/skills/web-design-guidelines/SKILL.md` — spacing, typography, a11y
- `.agents/skills/brainstorming/SKILL.md` — ideation before code
- `.agents/skills/systematic-debugging/SKILL.md` — debugging live vision pipeline
- `.agents/skills/computer-vision-opencv/SKILL.md` — OpenCV capture, threading, NMS, optical flow
- `.agents/skills/senior-computer-vision/SKILL.md` — detection/tracking/ReID review checklist

Global fallback: `~/.agents/skills/<same-name>/SKILL.md`
Install more via: `npx skills add <owner/repo> --skill <name> -g -y`
Registry: https://skills.sh

## When to use which skill
1. User mentions deck/slides/pptx → READ `.agents/skills/pptx/SKILL.md` first. No exceptions.
   - Edit template: fill via python-pptx `run.text` (never `text_frame.text`), match template fonts/sizes, validate with `scripts/office/validate.py --original template.pptx`.
   - New deck: Node `pptxgenjs` (pres.layout first, hex without #, fresh options objects).
   - Read: markitdown + PowerPoint COM export JPGs for visual QA (thumbnail.py is Unix-only).
2. Building control-room frontend → READ `frontend-design` + `ui-ux-pro-max` + `web-design-guidelines`.
3. New feature / stuck bug in tracking → use `brainstorming` then `systematic-debugging`.
4. Vision pipeline work → READ `computer-vision-opencv` + `senior-computer-vision`.

## Raksha build rules (robust)
- Live pipeline: ingest (RTSP/webcam/file) → YOLOv8 + ByteTrack persist → best-snapshot scoring (blur/pose/occlusion) → ArcFace 512-D + attributes → Faiss gallery → analytics (density/heatmap/flow/stampede = density×stillness×counterflow) → alerts <1s.
- Person dossier: globalID, trackIDs, best snapshots, trajectory, dwell, flags. Face hit <0.5s pops card.
- CPU-first: YOLOv8n, buffalo_s, downscale 720p, frame-skip. Mock embeddings allowed only behind interface.
- Ethics: opt-in enrollment, auto face-blur stored video, 7-day purge, audit log, no Aadhaar linkage in hackathon.
- Never: toy counter only, central ID linkage, storing raw faces without consent.

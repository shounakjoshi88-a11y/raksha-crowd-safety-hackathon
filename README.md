# Raksha — Predictive Crowd Safety (Hackathon 2026, Problem #2)

Team Raksha · Problem Statement No. 2: *Improving Safety at Large Public Events* ·
Team Leader: Shounak Joshi

## The idea in one minute

Today, control rooms watch dozens of CCTV screens by hand. A guard only notices
danger when a crowd has already stopped moving — but by then, crushing pressure
is already passing body to body. Reactive watching kills.

Raksha flips it: cameras measure how dense each zone is and how fast it moves,
then warn guards **before** the crush builds, so staff can open overflow gates
or hold entries upstream. Think weather forecast, but for crowds.

## How it works (two tracks, don't mix them up)

**CORE track — crowd physics (this is the main idea):**
1. **Calibrate** — map camera pixels to real ground (a fixed gate is measured once;
   other views use relative congestion levels).
2. **Map density** — a density heatmap counts the crowd even when people overlap
   (bounding boxes fail there; heatmaps read the texture of the crowd instead).
3. **Track flow** — optical flow measures which way the crowd mass is moving and
   how fast, like watching currents in water.
4. **Forecast pressure** — density × movement-unevenness gives crowd pressure.
   Rising pressure plus inflow faster than outflow = warn now, not after it stops.

**SIDE track — per-person labeling (already built, kept as is):**
Camera boxes with stable IDs, walking trails, zone counts, stay timers, plus an
opt-in face file (photo card pops on match). It runs below ~2 people per m² and
hands over to the density core above that. Nobody touches this track right now —
it works, leave it alone.

Privacy is built into the core: heatmaps cannot recognize faces, raw video never
leaves the camera box (only small JSON numbers travel up), stored footage is
face-blurred and auto-deleted after 7 days. No ID-card linkage, ever.

## Stage right now: idea PPT, not a finished product

This is a Stage-1 idea submission. The 6-slide deck in `deck/` is the deliverable
judges see. There is a working side-track demo on one laptop, but **laptop speed
scores mean nothing at deployment scale** — so the deck never mentions them.
Published benchmark numbers and real-deployment figures only.

## Where everything lives

| File or folder | What it is | Who should open it |
|---|---|---|
| `deck/Raksha_Hackathon2026_Simplified.pptx` | The live 6-slide submission deck | Everyone — this is what judges see |
| `deck/Raksha_Hackathon2026_Simplified.pdf` | Same deck as PDF, for portal upload | Everyone |
| `deck/HACKATHON 2026.pptx` | Blank official college template, reference only | Anyone editing slides |
| `docs/RESEARCH_V2.md` | The science bible: why boxes fail, pressure math, verified papers with links | Anyone writing or defending the idea |
| `docs/BUILD_PLAN.md` | How to actually build it later: runnable repos, milestones, risks | Builders, when build stage starts |
| `docs/RESEARCH.md` + `docs/CHINA_DEEP_DIVE.md` | Older notes (side-track era). History only — **do not cite AURORA, STAR-Crowd, FTLE, or any "Delhi 37%" claim from these; they are unsourced** | Nobody for new work |
| `docs/Hackathon Problem Statement .md` | All problem statements in text | Everyone |
| `docs/plan.md` | Living checklist of what is done and what is next | Everyone |
| `raksha/` | Side-track code: vision, backend API, wall UI | Builders only |
| `scripts/` | Dev helpers (benchmarks, enroll, clip tests) + `scripts/ppt/` (deck patch scripts, one per fix round) | Builders only |
| `.agents/skills/` | AI assistant skills (slides, UI, vision, debugging). Copy updates in here so the whole team stays in sync | Everyone |

## Reading order for new teammates

1. This README (you are here).
2. `deck/Raksha_Hackathon2026_Simplified.pdf` — the 6 slides, 5 minutes.
3. `docs/RESEARCH_V2.md` sections 1–2 — why the core works, with proof.
4. `docs/BUILD_PLAN.md` — how we build it when the time comes.
5. Only then: side-track code in `raksha/`.

## Editing the deck (rules, no exceptions)

- Deck edits go through Python scripts in `scripts/ppt/` (newest script is current).
  Never hand-edit the `.pptx` in PowerPoint and re-save — it breaks validation.
- After any edit: run the validator
  `python .agents/skills/pptx/scripts/office/validate.py deck/Raksha_Hackathon2026_Simplified.pptx --original "deck/HACKATHON 2026.pptx"`,
  re-export the PDF, and check every slide as an image before committing.
- Full procedure lives in `.agents/skills/pptx/SKILL.md` — read it before any slide work.
- Never put laptop FPS, laptop accuracy, or "tested on our machine" numbers on slides.
- Never cite AURORA, STAR-Crowd, FTLE, or the Delhi 37% figure. Ever.

## Running the side-track demo (optional, builders only)

```powershell
python raksha/backend/app.py        # start backend
http://localhost:8000/wall.html     # open the wall in a browser
python scripts/enroll.py YourName 5 # enroll a face with the webcam
```

First run downloads models automatically. Needs an NVIDIA GPU for full speed,
works slower on CPU. This demo is for our own testing — it is not deck material.

## How to contribute

1. Clone, then make a branch named after you or your task (example: `ananya/deck-flow-rebuild`).
2. Never commit: model weights, face galleries, real face photos, `node_modules`,
   thumbnails, or scratch files. Biometric data stays on your own machine only.
3. Skill updates go in `.agents/skills/<name>/` and get committed like normal code,
   so every teammate's AI assistant stays in sync.
4. Open a pull request with a one-line summary. Small PRs merge fast.

## Team

- Team name: Team Raksha
- Problem statement: No. 2 — Improving Safety at Large Public Events
- Team Leader: Shounak Joshi
- Members: (add names here)

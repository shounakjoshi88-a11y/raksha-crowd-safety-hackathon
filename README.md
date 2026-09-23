# Raksha Command Center: Crowd Safety (Hackathon 2026, Problem #2)

## What we are building
A smart crowd safety system for large public events (concerts, festivals, stations, stadiums).

Today, control rooms watch dozens of CCTV screens by hand. People get missed, crushes get spotted too late. Raksha changes that:

1. **Live tracking.** Every person gets a stable ID that stays with them across cameras, even in dense crowds.
2. **Instant person file.** The moment a face is seen clearly, a card pops up: photo, clothing, where they entered, where they have been, how long they stayed.
3. **Stampede meter.** The system watches density, stillness, and opposite flows. When risk turns red, guards get an alert in under 1 second with the exact zone and what to do.

Same idea as advanced camera systems used abroad, but built privacy first: opt in enrollment, blurred stored video, auto deletion, no ID card linkage, full audit log.

## Problem statement (short version)
Problem #2: Improving Safety at Large Public Events. Build a platform that monitors crowd density and movement, finds bottlenecks and dangerous congestion, and helps security move from reactive watching to proactive action. Full text is in `Hackathon Problem Statement .md`.

## What is inside this repo
| File or folder | What it is | Who should read it |
|---|---|---|
| `deck/Raksha_Hackathon2026_Final.pptx` | Our 6 slide submission deck, filled in the official college template | Everyone, this is what judges see |
| `deck/HACKATHON 2026.pptx` | The blank official template, keep as reference | Anyone editing slides |
| `docs/Hackathon Problem Statement .md` | All 6 problem statements in text form | Everyone |
| `AGENTS.md` | Playbook for our AI coding assistant: which skill to use, build rules, checklists | Anyone working with the AI agent |
| `docs/RESEARCH.md` | Build bible: best GitHub repos to copy from, papers, datasets, settings that work, build order | Builders (vision + backend) |
| `docs/CHINA_DEEP_DIVE.md` | Deep notes on how large scale camera systems work behind the scenes: vendors, standards, algorithms, hardware, real deployments | Builders who want full context |
| `docs/plan.md` | Living build tracker with checkboxes, updated as phases complete | Everyone, check this to see what is done and what is left |
| `scripts/` | Dev helpers: `smoke_env.py` (GPU + detect + embed check), `bench_track.py` (tracking FPS benchmark) | Builders |
| `.agents/skills/` | 8 installed AI skills with all their files: slide making, UI design, computer vision, debugging, brainstorming | Everyone, these make the AI agent much better |
| `raksha/` | Working prototype code: live vision (`vision/`), early mock API + dashboard (`backend/`, `frontend/`), run notes, demo script | Builders |

## Skills folder, simple explanation
The `.agents/skills/` folder teaches our AI assistant how to do expert work:

- `pptx`: making and fixing PowerPoint decks the correct way, with checks.
- `frontend-design`, `ui-ux-pro-max`, `web-design-guidelines`: making the control room dashboard look clean and professional, not generic.
- `computer-vision-opencv`, `senior-computer-vision`: building the camera AI (detection, tracking, face matching, speed tricks).
- `brainstorming`: thinking through ideas before coding.
- `systematic-debugging`: fixing bugs by finding the root cause first.

Rule for the team: when anyone installs or updates a skill, copy the fresh `.agents/skills/<name>` folder into this repo and commit it, so everyone stays in sync. Restore everything on a new machine with the commands in the Skills section below.

## How we will build it (plain steps)
1. **Camera input.** Webcam, video file, or CCTV stream. Start with 720p to keep it fast.
2. **Find and follow people.** YOLOv8 finds people, ByteTrack keeps the same ID on each person frame after frame.
3. **Face plus details.** Best clear face shot is picked automatically, turned into a compact code (ArcFace), matched against our small gallery. Clothing color, age group, and path get attached.
4. **One file per person.** Each person gets a single record: IDs, photos, path on map, dwell time, flags.
5. **Crowd brain.** Count per zone, heatmap, flow direction, stampede score (density times stillness times opposite flow). Red zone means act now.
6. **Alert and handover.** Guard app push plus one click clip export with audit trail.

Key numbers we design for: face match under 0.5 seconds, any alert under 1 second, bottleneck warning at least 60 seconds before a human would spot it.

## Submission checklist
- [ ] Deck: 6 slides max in the official template (done, see final pptx)
- [ ] Team details on slide 1 (Team Leader name: add tomorrow)
- [ ] Export deck as PDF from PowerPoint (portal takes PDF only)
- [ ] Demo video: dense frame goes red, guard diverts, missing person found
- [ ] Short cleanup pass for fonts and spacing before export

## Skills: install and update commands
```powershell
npx -y skills add https://github.com/anthropics/skills --skill pptx -g -y
npx -y skills add https://github.com/anthropics/skills --skill frontend-design -g -y
npx -y skills add https://github.com/nextlevelbuilder/ui-ux-pro-max-skill --skill ui-ux-pro-max -g -y
npx -y skills add https://github.com/vercel-labs/agent-skills --skill web-design-guidelines -g -y
npx -y skills add https://github.com/obra/superpowers --skill brainstorming -g -y
npx -y skills add https://github.com/obra/superpowers --skill systematic-debugging -g -y
npx -y skills add mindrally/skills@computer-vision-opencv -g -y
npx -y skills add alirezarezvani/claude-skills@senior-computer-vision -g -y
```

## How to contribute
1. Clone the repo, make a branch with your name or task (example: `ananya/heatmap-ui`).
2. Keep it clean: never commit `*.py` scratch files, `node_modules`, thumbnails, PDFs, or research clones. `.gitignore` already blocks them.
3. Skill updates go in `.agents/skills/<name>` and get committed like normal code.
4. Open a pull request with a one line summary of what changed. Small PRs get merged fast.

## Team
- Team name: Team Raksha
- Problem statement: No. 2, Improving Safety at Large Public Events
- Team Leader: (adding tomorrow)
- Members: (add names here)

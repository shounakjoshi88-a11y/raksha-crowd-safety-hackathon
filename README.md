# Raksha Command Center — Crowd Safety (Hackathon 2026, Problem #2)

China-grade live tracking + instant person dossier, privacy-first. From reactive CCTV to proactive intervention.

## Contents
- `Hackathon Problem Statement .md` — all 6 problem statements (we build #2)
- `Raksha_Hackathon2026_Final.pptx` — submission deck (6 slides, exact college template)
- `HACKATHON 2026.pptx` — official blank template
- `AGENTS.md` — agent playbook (skills routing, build rules, PPT checklist)
- `RESEARCH.md` — repos, papers, datasets, thresholds, build order
- `CHINA_DEEP_DIVE.md` — how Chinese crowd surveillance works behind the scenes
- `.agents/skills/` — full vendored skills (pptx, frontend-design, ui-ux-pro-max, web-design-guidelines, brainstorming, systematic-debugging, computer-vision-opencv, senior-computer-vision). Excludes `__pycache__`.

## Deck PDFs
The portal accepts PDF only. Open the final PPTX in PowerPoint → Save as PDF → upload.

## Skills: update / restore
Skills are vendored here so the whole team shares them. When someone installs/updates a skill, copy `.agents/skills/<name>` into this repo and commit. Fresh machine restore:
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

## Kept out (local only)
`*.py` builders, `node_modules/`, `raksha/` prototype, `research/` clones, thumbnails — all local. See `.gitignore`.

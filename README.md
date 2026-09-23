# Raksha Command Center — Crowd Safety (Hackathon 2026, Problem #2)

China-grade live tracking + instant person dossier, privacy-first. From reactive CCTV to proactive intervention.

## Contents
- `Hackathon Problem Statement .md` — all 6 problem statements (we build #2)
- `Raksha_Hackathon2026_Final.pptx` — submission deck (6 slides, exact college template) ← upload via web (see below)
- `HACKATHON 2026.pptx` — official blank template ← upload via web (see below)
- `AGENTS.md` — agent playbook (skills routing, build rules, PPT checklist)
- `RESEARCH.md` — repos, papers, datasets, thresholds, build order
- `CHINA_DEEP_DIVE.md` — how Chinese crowd surveillance works behind the scenes
- `.agents/skills/*/SKILL.md` — agent guidance files (pptx, frontend, vision, debugging)

## Deck PDFs
The portal accepts PDF only. Open the final PPTX in PowerPoint → Save as PDF → upload.

## Skills restore (full scripts/schemas)
SKILL.md files are the guidance; full tooling reinstalls with:
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

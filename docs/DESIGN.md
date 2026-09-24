# Raksha control-room design system

Locked tokens and layout rules for the wall and settings screens. Follow this file; do not invent new colors or card patterns mid-build.

## Direction

Warm-graphite instrument panel for night operations. Video canvas is the primary object; lists are tables/rows, not floating cards. Grounded in VMS grammar (Genetec area view + canvas + report pane, Milestone bottom timeline) with Indian event-safety identity through a single signal-amber accent.

### Anti-slop checklist (must pass before ship)

- No ALL-CAPS letter-spaced section labels (sentence case only; AGENTS.md rule)
- No `border-left` color stripes on rows or cards
- No box-shadow glows or neon dots
- No row of identical hero KPI cards; counts live in topbar, zone rows, and the risk strip
- No blue-charcoal `#020617` + acid-green `#22C55E` pairing
- No uniform 10px radius everywhere: panels 6px, controls 4px
- Labels >= 12px; body 13-14px
- Charts show thresholds or axes, not naked spark bars
- Every color state pairs with a text label
- Focus-visible ring on all interactive elements; one `h1` per page; skip link

## Color tokens

| Token | Hex | Use |
|---|---|---|
| `--bg` | `#141311` | page background (warm graphite) |
| `--surface` | `#1C1A17` | panels, topbar, footer |
| `--surface-2` | `#24211D` | inputs, nested rows, hover |
| `--border` | `#3A362F` | 1px hairlines, full perimeter |
| `--fg` | `#EDE6D9` | primary text (warm ivory) |
| `--fg-muted` | `#A39C8F` | secondary text (min 12px) |
| `--fg-dim` | `#7D766B` | placeholders, disabled |
| `--accent` | `#D9A441` | brand signal amber: brand mark, focus, primary button, selected tab underline |
| `--ok` | `#6E9E5A` | nominal / green risk |
| `--watch` | `#D9A441` | yellow risk (same amber family; always with text) |
| `--crit` | `#E06A66` | red risk / critical (text-safe red) |
| `--crit-deep` | `#3A1512` | red banner background only |
| `--watch-deep` | `#33290E` | yellow banner background only |
| `--chart` | `#7BA7C7` | non-risk data viz (steel blue, desaturated) |

Rules: risk greens/ambers/reds are semantic only, never decoration. One brand accent (amber). No cyan-on-dark, no purple gradients.

Contrast targets: body and muted text >= 4.5:1 on their surface; large numerals and chips >= 3:1.

## Typography

Self-hosted (offline-first, no CDN):

- `Barlow` 400/500/600 - UI and body (`fonts/barlow-400.woff2` etc.)
- `Barlow Condensed` 500/600 - pane titles, dense labels, table headers
- Data readouts: `font-family: ui-monospace, "Cascadia Mono", Consolas, monospace` + `font-variant-numeric: tabular-nums` (no extra font file)

Scale: page title 18px/600; pane title 13px/600 condensed; body 13-14px; label 12px/500; micro meta 12px. Sentence case everywhere. No `letter-spacing` tracking on labels. Line length under ~80ch in prose (settings hints).

## Spacing and shape

- 4px base rhythm; common gaps 4, 8, 12, 16
- Panel padding 12px (dense) to 16px (settings cards)
- Radius: panels/cards 6px, inputs/buttons 4px, chips 999px only for pills
- Borders 1px `--border` on all four sides; no accent side-stripes
- Elevation: surface steps only; no drop shadows for structure (menu popovers may use a single soft shadow)

## Wall layout (Genetec grammar)

```
topbar   brand · status pill · readouts (fps/tracked/face) · clock · Settings
banner   red/yellow only, role=alert, slides once
main     sources | canvas (+ tile toolbar, legend) | report pane (tabs)
         risk strip under canvas: score + level chip + density/still/counterflow
timeline full-width SVG: risk line, warn/crit bands, now marker
footer   health readouts as inline text · ethics line · h1 visually brand-adjacent
```

- Sources pane: zone rows (name, count, dwell, density bar, severity dot + text)
- Report pane tabs: `Alerts` (default) | `People` | `Captures` - dense rows, not cards
- Alert row: time · level chip · one-line summary · status · Ack / False / Escalate as compact buttons
- Risk strip replaces the old fat gauge card and the four KPI cards
- Motion: only red/yellow transition gets a 200ms banner slide + canvas border pulse; everything else 150ms color transitions; honor `prefers-reduced-motion`

## Settings layout

Same topbar shell (title = Settings, link back to wall). Sticky in-page section nav (Storage, Thresholds, Export, Data) + single content column max 720px. Each section: `fieldset` + `legend` sentence case, real `<label for>`, help text 13px muted. Save buttons: primary amber with pending state (`Saving...`, disabled). Status message: sticky top, `role="status"`, ok = amber left border? no stripes - use surface-2 bar with ok/crit text color + icon-free text. Danger section: hairline top border, `--crit` text button, no banner block.

## Components (app.css)

- `.topbar`, `.brand`, `.status-pill`, `.readout`, `.banner`
- `.panel` (surface + 1px border + 6px radius), `.pane-title`
- `.tabs` / `[role=tab]` with amber underline on selected
- `.row-list` / `.row` dense list rows; `.chip` semantic pills with text
- `.btn`, `.btn-primary`, `.btn-ghost`, `.btn-danger`; `.btn[disabled]` pending
- `.zone-row`, `.meter` (thin bar, chart color, not accent)
- `.alert-row`, `.person-row`, `.capture-row`
- `.risk-strip`, `.risk-score`, `.timeline`
- `.field` form controls; `.settings-nav`
- `.skip-link`, `:focus-visible` amber 2px offset 2px

## Responsive

- >= 1100px: three-pane main
- 768-1099px: sources collapses under canvas or becomes horizontal chips; report pane full width below
- < 768px: single column stack, topbar readouts wrap, tabs scroll horizontally
- QA widths: 1440, 1024, 768, 390

## V2 pattern spec (from Verkada Command, Rhombus Console, JetStream, Milestone alarms)

V2 closes the gap to real product. Rules below override v1 where they conflict.

### Type v2

- Inter 400/500/600/700 self-hosted (`fonts/inter-*.woff2`) becomes `--font-ui`
  (matches JetStream/Rhombus/Verkada grotesque; Barlow body reads designed, not product)
- Barlow Condensed stays for display numerals and dense headers only
- System mono + tabular-nums for all data readouts (unchanged)

### Chrome v2

- 56px left icon rail: Wall (grid icon), Settings (gear), bottom backend-status dot.
  Rail hides under 860px; topbar keeps text nav as fallback
- Tile chrome sits ON the video: top-left camera pill + LIVE pill, top-right
  snapshot/fullscreen icon buttons, bottom-right clock overlay, bottom-left
  legend overlay. No separate bar above the video
- Icon system: `raksha/frontend/icons.svg` sprite, 24px stroke icons, `currentColor`

### Rows v2

- No boxes inside panels. Panels hold header (title left, actions right) and rows
  separated by 1px `--border` hairlines, 10px vertical padding
- Alert rows: severity chip, relative time, one-line summary, zone, status;
  open rows keep inline Ack / False / Escalate; handled rows dim with outcome text
- Alert filter chips above the list: All, Open, Red, Yellow, Handled
- People tab: 2-column dossier grid (thumb top with sim chip, name + dwell below),
  Rhombus Faces style. Captures stay a divider list

### Timeline v2 (Rhombus/Milestone grammar)

- Transport header: LIVE badge, Hold/Resume polling button, clock, alert count
- SVG: time axis (-60s to Now), area fill under curve, warn/crit dashed bands
  with inline labels, diamond markers for alerts inside the window
- Filter row under chart: event lanes toggles (Risk line, Alert markers) as checkboxes

### Risk instrument v2

- Horizontal scale meter 0 to max(1.0, crit x 1.4) with tick marks at warn/crit,
  numeric score + level chip + three component mini-meters (density/stillness/
  counterflow) with values. Replaces the naked bar

### Features v2 (all wired, no fakes)

- Snapshot button captures the MJPEG frame to a downloaded PNG
- Fullscreen tile via requestFullscreen with CSS fallback class
- Hold/Resume pauses the 1s poll loop (video keeps streaming)
- Keyboard: 1/2/3 tabs, f fullscreen, h hold, / focuses people search
- Settings: two-column enterprise field grid, threshold scale preview,
  keyboard-shortcut reference section

## References (local)

- `assets/ui-refs/` - Genetec docs figure, Milestone XProtect pages 51/52 (UI overview, timeline), JetStream frames, AETHRA, ZCOOL collection
- `assets/china-ui/hikcentral_0{1..4}.png` - enterprise density and event-feed patterns
- Do not copy sci-fi glow frames (ZCOOL) or marketing all-caps (AETHRA)

## Build conventions

- Shared `raksha/frontend/app.css` + optional tiny page scripts inline (no framework, no bundler)
- Fonts: five woff2 in `raksha/frontend/fonts/`, `font-display: swap`
- API wiring unchanged: `/api/state`, `/api/alerts`, `/api/alerts/{id}/ack`, `/api/config`, `/api/browse`, `/api/export`, `/api/purge`, `/stream.mjpeg`
- Vanilla SVG for timeline; no chart library
- Screenshots for QA stay out of git (personal webcam privacy); use public clip source for captures

# Raksha - Unified Crowd Safety + Security4Her
Solo, <24h hackathon build. Covers Problem #2 + #3 in one platform.

## Why this wins
Judges love: 1 demo, 2 problem statements, live AI + social impact. Organizers get proactive crowd dashboard. Women attendees get SOS + AI triage. Same map, same backend.

## MVP (must demo)
1. Crowd: Upload CCTV frame -> count + Green/Yellow/Red + auto alert. Zone list auto-refresh.
2. Her: Big SOS button -> sends location to contacts + control room (mock SMS log). Report -> AI triage high/med/low.
3. Map: Leaflet with zones + SOS pins.

## Run (5 min)
Backend:
```
cd raksha/backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
Frontend: open `raksha/frontend/index.html` in browser (or `npx serve frontend`).

No YOLO weights needed for Day-1 mock. Plug real YOLOv8n later in `/analyze-crowd`.

## 24h plan for solo
0-2h: Run this scaffold, record 30s CCTV test clip, pick event location lat/lon
2-6h: Wire real YOLOv8n (ultralytics) in main.py, test 3 crowd images (sparse/medium/dense)
6-10h: SOS polish: geolocation, WhatsApp deep link `https://wa.me/?text=SOS...`, localStorage trusted contacts
10-13h: Safe-route + lighting reports UI, fake historical data
13-16h: Pitch: 2-min video (crowd red alert -> security dispatch + SOS demo side-by-side), README, slides
Buffer: privacy note (blur faces, consent banner), escalation logic (SOS unanswered 2 min -> police)

## Pitch line
"From reactive CCTV to proactive intervention, and from fear to one-tap help — Raksha protects the crowd and Her in the crowd."

## Next if time
- Twilio SMS, WebSocket live CCTV, face-blur with OpenCV, on-device fall detection tie-in to #6

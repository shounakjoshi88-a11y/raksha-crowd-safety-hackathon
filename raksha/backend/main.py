from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from datetime import datetime
import random

app = FastAPI(title="Raksha - Crowd + Her Safety API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory stores for hackathon demo (swap with SQLite/Firebase later)
alerts_db = []
sos_db = []
reports_db = []

class SOSRequest(BaseModel):
    user_id: str
    lat: float
    lon: float
    message: str = "SOS! I need help"

class ReportRequest(BaseModel):
    user_id: str
    lat: float
    lon: float
    category: str  # harassment, stalking, unsafe_area, lighting, other
    description: str

@app.get("/health")
def health():
    return {"status": "ok", "service": "raksha"}

@app.get("/zones")
def get_zones():
    """Zone-wise crowd risk. Frontend polls this for map."""
    # TODO: replace random with real YOLO counts per camera zone
    zones = []
    for zid, name in [("A", "Main Gate"), ("B", "Food Court"), ("C", "Stage Front"), ("D", "Exit 2")]:
        density = random.randint(20, 180)
        risk = "green" if density < 70 else "yellow" if density < 130 else "red"
        zones.append({"id": zid, "name": name, "density": density, "risk": risk, "updated": datetime.now().isoformat()})
    return {"zones": zones}

@app.post("/analyze-crowd")
async def analyze_crowd(file: UploadFile = File(...)):
    """
    MVP: Accepts CCTV frame / upload.
    Day-1: return mock density. Day-2: plug YOLOv8n person count.
    To enable real: uncomment YOLO code below.
    """
    # from ultralytics import YOLO
    # model = YOLO("yolov8n.pt")
    # ... count = len(model.predict(...))
    mock_count = random.randint(30, 170)
    risk = "green" if mock_count < 70 else "yellow" if mock_count < 130 else "red"
    alert = None
    if risk == "red":
        alert = {"type": "congestion", "msg": f"Dangerous congestion: {mock_count} in frame", "time": datetime.now().isoformat()}
        alerts_db.append(alert)
    return {"count": mock_count, "risk": risk, "alert": alert}

@app.post("/sos")
def sos(req: SOSRequest):
    record = {**req.dict(), "time": datetime.now().isoformat(), "status": "active"}
    sos_db.append(record)
    # TODO: integrate Twilio / WhatsApp / SMS to trusted contacts + control room
    print(f"!!! SOS from {req.user_id} at {req.lat},{req.lon}")
    return {"ok": True, "id": len(sos_db)-1, "msg": "Alert sent to 2 contacts + control room (mock)"}

@app.post("/report")
def report(req: ReportRequest):
    # Simple AI triage: keyword risk score (replace with LLM classifier if time)
    high_risk_words = ["follow", "stalk", "threat", "attack", "knife", "grab"]
    score = sum(1 for w in high_risk_words if w in req.description.lower()) / 2.0
    level = "high" if score >= 1 else "medium" if score >= 0.5 else "low"
    rec = {**req.dict(), "risk": level, "time": datetime.now().isoformat()}
    reports_db.append(rec)
    return {"ok": True, "triage": level}

@app.get("/alerts")
def alerts():
    return {"alerts": alerts_db[-20:], "sos": sos_db[-20:]}

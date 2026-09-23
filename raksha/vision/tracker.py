"""Person detection + tracking. One instance per video stream (tracker state must not mix)."""
from ultralytics import YOLO


VEHICLE_CLASSES = {2: "car", 3: "motorbike", 5: "bus", 7: "truck"}


class PersonTracker:
    def __init__(self, weights="D:/Q_project/raksha/models/yolov8s.pt", device=0, tracker="bytetrack.yaml", conf=0.35, imgsz=640, classes=(0, 2, 3, 5, 7)):
        self.model = YOLO(weights)
        self.device = device
        self.tracker = tracker
        self.conf = conf
        self.imgsz = imgsz
        self.classes = classes

    def update(self, frame):
        """Returns list of dicts: id, cls, label, xyxy, conf. id None until track confirms."""
        res = self.model.track(frame, persist=True, tracker=self.tracker,
                               conf=self.conf, imgsz=self.imgsz, classes=list(self.classes),
                               device=self.device, verbose=False)[0]
        out = []
        if res.boxes is None:
            return out
        ids = res.boxes.id
        for i, box in enumerate(res.boxes):
            cls = int(box.cls)
            tid = int(ids[i]) if ids is not None else None
            label = "person" if cls == 0 else VEHICLE_CLASSES.get(cls, f"cls{cls}")
            out.append({"id": tid, "cls": cls, "label": label,
                        "xyxy": box.xyxy[0].tolist(), "conf": float(box.conf)})
        return out

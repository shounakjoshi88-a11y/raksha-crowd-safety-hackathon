"""Person detection + tracking. One instance per video stream (tracker state must not mix)."""
from ultralytics import YOLO


class PersonTracker:
    def __init__(self, weights="D:/Q_project/raksha/models/yolov8s.pt", device=0, tracker="bytetrack.yaml", conf=0.35, imgsz=640):
        self.model = YOLO(weights)
        self.device = device
        self.tracker = tracker
        self.conf = conf
        self.imgsz = imgsz

    def update(self, frame):
        """Returns list of dicts: id, cls, xyxy, conf. id is None until track confirms."""
        res = self.model.track(frame, persist=True, tracker=self.tracker,
                               conf=self.conf, imgsz=self.imgsz,
                               device=self.device, verbose=False)[0]
        out = []
        if res.boxes is None:
            return out
        ids = res.boxes.id
        for i, box in enumerate(res.boxes):
            if int(box.cls) != 0:  # person only
                continue
            tid = int(ids[i]) if ids is not None else None
            out.append({"id": tid, "xyxy": box.xyxy[0].tolist(), "conf": float(box.conf)})
        return out

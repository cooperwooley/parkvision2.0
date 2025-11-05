import ultralytics
from ultralytics import YOLO


model = YOLO("yolov8n.pt")

model.train(
    data = "VD_Dataset/data.yaml", #change to train dataset
    epochs=300,
    device=0, # THIS PART MIGHT NOT WORK ON YOUR SYSTEM -- ENABLES GPU USAGE FOR TRAINING 
    batch=4,             # ↓ reduce from 16 or auto to 4 or 2
    workers=2,           # ↓ fewer dataloader threads
    cache=False,
)

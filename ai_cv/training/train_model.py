from ultralytics import YOLO
import os
import gc

def train_over_dataset(weights, datapath, epochs=200, lr0=0.001, lrf=0.01, batch=8):
    gc.collect() # clean up memory
    model = YOLO(weights)
    res = model.train(
        data=datapath, #change to train dataset
        epochs=epochs,
        device=0, # THIS PART MIGHT NOT WORK ON YOUR SYSTEM -- ENABLES GPU USAGE FOR TRAINING 
        batch=16,             # ↓ reduce from 16 or auto to 4 or 2
        workers=2,           # ↓ fewer dataloader threads
        cache=False,
        patience=30,
        optimizer="AdamW",
        lr0=lr0,
        lrf=lrf,
        plots=True,
        resume=True,
    )
    
    last_pt = os.path.join(res.save_dir, "weights", "best.pt") # e.g. runs/detect/train3/weights/last.pt

    return last_pt
    


if __name__ == "__main__":

    VDalk_path = os.path.join(os.getcwd(), "datasets", "VDalk")
    yolovd_path = os.path.join(os.getcwd(), "datasets", "yoloVD")
    yaml_path = os.path.join(os.getcwd(), "yaml")

    VDalkdict = {
        "dataset": 'alkanerturan/vehicledetection', # https://www.kaggle.com/datasets/alkanerturan/vehicledetection
        "filepath": VDalk_path,
        "yamlpath": os.path.join(VDalk_path, 'VehiclesDetectionDataset', 'dataset.yaml')
    }

    yoloVDdict = {
        "dataset": 'nadinpethiyagoda/vehicle-dataset-for-yolo', # https://www.kaggle.com/datasets/nadinpethiyagoda/vehicle-dataset-for-yolo
        "filepath": yolovd_path,
        "yamlpath": os.path.join(yaml_path, 'yoloVD.yaml')
    }


    PKVD_path = os.path.join(os.getcwd(), "datasets", "PKVD")
    PKVDdict = {
        "dataset": 'pkdarabi/vehicle-detection-image-dataset', # https://www.kaggle.com/datasets/pkdarabi/vehicle-detection-image-dataset
        "filepath": PKVD_path,
        "yamlpath": os.path.join(PKVD_path,'No_Apply_Grayscale', 'No_Apply_Grayscale', 'Vehicles_Detection.v8i.yolov9', 'data.yaml')
    }

    TVVD_path = os.path.join(os.getcwd(), "datasets", "TVVD")
    TVVDdict = {
        "dataset": 'farzadnekouei/top-view-vehicle-detection-image-dataset', # https://www.kaggle.com/datasets/farzadnekouei/top-view-vehicle-detection-image-dataset
        "filepath": TVVD_path,
        "yamlpath": os.path.join(TVVD_path, 'Vehicle_Detection_Image_Dataset', 'data.yaml')
    }


    TVDCVD_path = os.path.join(os.getcwd(), "datasets", "TVDCVD", "dataset")
    TVDCVDdict = {
        "dataset": 'glebkuzntesov/top-view-drone-car-detection-dataset-12000-images', # https://www.kaggle.com/datasets/glebkuzntesov/top-view-drone-car-detection-dataset-12000-images
        "filepath": TVDCVD_path,
        "yamlpath": os.path.join(TVDCVD_path, 'dataset.yaml')
    }


    AVCD_path = os.path.join(os.getcwd(), "datasets", "AVCD")
    AVCDdict = {
        "dataset": 'braunge/aerial-view-car-detection-for-yolov5', # https://www.kaggle.com/datasets/braunge/aerial-view-car-detection-for-yolov5
        "filepath": AVCD_path,
        "yamlpath": os.path.join(AVCD_path, 'mydata128.yaml')
    }
    w5 = os.path.join("runs", "detect", "train7", 'weights', "last.pt" )  # starting weights using yolov5n pretrained weights
    weights = 'yolo11n.pt'  # starting weights using yolov5n pretrained weights
    # Training over datasets sequentially to continuously train on the same model
    # Adjust epochs as necessary accdoriing to dataset size and complexity
    # Trained from smalles to largest dataset to gradually improve model performance
    # Current traning pipeline introduces a high DGL_loss which could be due to catastrophic forgetting - needs investigation
    w1 = train_over_dataset(weights, VDalkdict["yamlpath"], epochs=200, lr0=0.001, lrf=0.01) # May need more epochs here
    w2 = train_over_dataset(w1, PKVDdict["yamlpath"], epochs=200, lr0=0.001, lrf=0.01) # Good as is
    w3 = train_over_dataset(w2, TVVDdict["yamlpath"], epochs=100, lr0=0.0005, lrf=0.01, batch=8) #Change lr0 to 0.0003?
    w4 = train_over_dataset(w3, AVCDdict["yamlpath"], epochs=150, lr0=0.0005, lrf=0.01, batch=8) # Good as is
    w5 = train_over_dataset(w4, yoloVDdict["yamlpath"], epochs=230, lr0=0.0003, lrf=0.01) # Good as is
    train_over_dataset(w5, TVDCVDdict["yamlpath"], epochs=300, lr0=0.0003, lrf=0.01) # Dataset is of size 12,000 images may need more epoch. Addtionally images in dataset are relitivly small thus a scale factor might be benifiical to reduce DFL loss


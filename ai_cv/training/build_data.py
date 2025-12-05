from kaggle import api
import os
from train_model import train_over_dataset

def download_datasets():

    paths = []

    VDalk_path = os.path.join(os.getcwd(), "datasets", "VDalk")
    if not os.path.exists(VDalk_path):
        os.makedirs(VDalk_path)

    yolovd_path = os.path.join(os.getcwd(), "datasets", "yoloVD")
    if not os.path.exists(yolovd_path):
        os.makedirs(yolovd_path)

    yaml_path = os.path.join(os.getcwd(), "yaml")
    if not os.path.exists(yaml_path):
        os.makedirs(yaml_path)

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

    paths.append(VDalkdict)
    paths.append(yoloVDdict)


    PKVD_path = os.path.join(os.getcwd(), "datasets", "PKVD")
    if not os.path.exists(PKVD_path):
        os.makedirs(PKVD_path)

    PKVDdict = {
        "dataset": 'pkdarabi/vehicle-detection-image-dataset', # https://www.kaggle.com/datasets/pkdarabi/vehicle-detection-image-dataset
        "filepath": PKVD_path,
        "yamlpath": os.path.join(PKVD_path,'No_Apply_Grayscale', 'No_Apply_Grayscale', 'Vehicles_Detection.v8i.yolov9', 'data.yaml')
    }

    paths.append(PKVDdict)


    TVVD_path = os.path.join(os.getcwd(), "datasets", "TVVD")
    if not os.path.exists(TVVD_path):
        os.makedirs(TVVD_path)

    TVVDdict = {
        "dataset": 'farzadnekouei/top-view-vehicle-detection-image-dataset', # https://www.kaggle.com/datasets/farzadnekouei/top-view-vehicle-detection-image-dataset
        "filepath": TVVD_path,
        "yamlpath": os.path.join(TVVD_path, 'Vehicle_Detection_Image_Dataset', 'data.yaml')
    }

    paths.append(TVVDdict)



    TVDCVD_path = os.path.join(os.getcwd(), "datasets", "TVDCVD")
    if not os.path.exists(TVDCVD_path):
        os.makedirs(TVDCVD_path)

    TVDCVDdict = {
        "dataset": 'glebkuzntesov/top-view-drone-car-detection-dataset-12000-images', # https://www.kaggle.com/datasets/glebkuzntesov/top-view-drone-car-detection-dataset-12000-images
        "filepath": TVDCVD_path,
        "yamlpath": os.path.join(TVDCVD_path, 'dataset', 'dataset.yaml')
    }

    paths.append(TVDCVDdict)


    AVCD_path = os.path.join(os.getcwd(), "datasets", "AVCD")
    if not os.path.exists(AVCD_path):
        os.makedirs(AVCD_path)

    AVCDdict = {
        "dataset": 'braunge/aerial-view-car-detection-for-yolov5', # https://www.kaggle.com/datasets/braunge/aerial-view-car-detection-for-yolov5
        "filepath": AVCD_path,
        "yamlpath": os.path.join(AVCD_path, 'mydata128.yaml')
    }

    paths.append(AVCDdict)

    for dataset in paths:
        if not os.listdir(dataset["filepath"]):
            api.dataset_download_files(dataset["dataset"], path=dataset["filepath"], unzip=True)
            
    return paths

if __name__ == "__main__":
    download_datasets()
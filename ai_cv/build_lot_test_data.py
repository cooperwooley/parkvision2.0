from kaggle import api
import os


lot_test_path = os.path.join(os.getcwd(), "tests", "lot_test_data")
if not os.path.exists(lot_test_path):
    os.makedirs(lot_test_path)

lot_test = {
    "dataset": 'trainingdatapro/parking-space-detection-dataset', # https://www.kaggle.com/datasets/alkanerturan/vehicledetection
    "filepath": lot_test_path,
}



api.dataset_download_files(lot_test["dataset"], path=lot_test["filepath"], unzip=True)

import os
import json

#Kaggle token gen
api_token = {"username":"YOURUSERNAME","key":"YOURKEY"}

kaggle_dir = os.path.expanduser('~\.kaggle')
if not os.path.exists(kaggle_dir):
    os.makedirs(kaggle_dir)

kaggle_json_path = os.path.join(kaggle_dir, 'kaggle.json')
with open(kaggle_json_path, 'w') as f:
    json.dump(api_token, f)

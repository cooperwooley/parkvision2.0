# How To Run Tests

From within the `ai_cv/` directory:
1. First, run `pip install -r requirements.txt`
2. To obtain the pretrained YOLO model, run `python3 run_pipeline.py`
3. To install the test dataset, `python3 build_test_data.py`
4. Run tests: `python3 tests/<test_file>.py`
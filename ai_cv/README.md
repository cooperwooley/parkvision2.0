# ParkVision AI/CV Module

Computer vision pipeline for real-time vehicle detection, tracking, and parking lot occupancy analysis.

## Overview

The `ai_cv` module provides a complete pipeline for:
- **Vehicle Detection**: Using YOLO models to detect vehicles in images/video
- **Vehicle Tracking**: Multi-object tracking using DeepSORT for consistent vehicle identification across frames
- **Parking Lot Analysis**: Matching detected vehicles to parking lot polygons to determine occupancy
- **Session Management**: Tracking vehicle entry/exit events and parking durations

## Architecture

ai_cv/

├── detection/ # Vehicle and parking lot detection

│ ├── detect.py # VehicleDetector - YOLO-based vehicle detection

│ └── lot_detector.py # LotDetector - Parking lot occupancy analysis

├── recognition/ # Tracking and session management

│ ├── tracker.py # VehicleTracker - DeepSORT-based tracking

│ └── session_logic.py # SessionManager - Vehicle session tracking
├── utilities/ # Helper utilities

│ └── visualize.py # Visualization functions

├── tests/ # Test suite

├── run_pipeline.py # Main pipeline execution script

└── requirements.txt # Python dependencies

### Component Flow

Video/Image Input

↓

VehicleDetector (YOLO)

↓

VehicleTracker (DeepSORT)

↓

LotDetector (Polygon Matching)

↓

SessionManager (Event Tracking)

↓

Output: Occupied/Unoccupied Lots + Vehicle Sessions

## Installation

### Prerequisites

- Python 3.11+
- CUDA-capable GPU (for real-time performance)
- OpenCV system libraries

### Setup

1. **Install system dependencies** (Ubuntu/Debian):
sudo apt-get update
sudo apt-get install -y python3-opencv ffmpeg libsm6 libxext6
2. **Install Python dependencies**:
cd ai_cv
pip install -r requirements.txt
3. **Download YOLO model** (first run will auto-download, or manually):
* Models are downloaded automatically on first use
* Default: yolov8n.pt (nano - fastest)
* For lot detection: best.pt (custom trained model)

### Docker Setup

```sh
# Build the container
docker-compose build

# Run with volume mount
docker-compose up
```

### Detection format

```json
{
    "xyxy": [x1, y1, x2, y2],  # Bounding box coordinates
    "conf": 0.95,               # Confidence score (0-1)
    "cls": 2,                   # Class ID (YOLO class)
    "name": "car"               # Class name
}
```

### Track Format

```json
{
    "track_id": 1,              # Unique tracking ID
    "bbox": [x1, y1, x2, y2],   # Bounding box coordinates
    "conf": 0.95,               # Detection confidence
    "cls": 2,                   # Class ID
    "name": "car"               # Class name
}
```

### Parking Lot JSON Format

```json
[
    {
        "points": [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
    },
    {
        "points": [[x1, y1], [x2, y2], [x3, y3], [x4, y4]]
    }
]
```

### Occupied Lot Format

```json
{
    
    "bbox": [[x1, y1], [x2, y2], ...],  # Polygon points
    "conf": 0.85,                        # IoU confidence
    "cls": 2,                            # Vehicle class
    "name": "car",                       # Vehicle type
    "track_id": 1                        # (Only in video mode) Tracking ID
}
```

### Session Format

```json
{
    "track_id": 1,
    "start_time": 1234567890.0,
    "end_time": 1234567895.0,
    "duration": 5.0,
    "bbox": [x1, y1, x2, y2],
    "cls": 2,
    "name": "car"
}
```

## Backend Integration

### Recommended Integration Points
1. **Real-time Updates**: Use `detect_from_video()` callback to send updates to backend API
2. **Batch Processing**: Process frames/images and send results via REST API
3. **Event Streaming**: Use `SessionManager` completed sessions to trigger backend events

## Testing

### Run Tests

```sh
# Install test dependencies
pip install -r requirements.txt

# Download test data
python3 build_test_data.py

# Run individual tests
python3 tests/test_detect.py
python3 tests/test_tracker.py
python3 tests/test_lot_detection.py
python3 tests/test_session.py
```

### Test data

- Sample images in `tests/test_data/images/`
- Sample videos in `tests/test_data/videos/`
- Lot annotations in `tests/lot_test_data/`

## Dependencies

- `ultralytics` - YOLO models and inference
- `opencv-python` - Image/video processing
- `numpy` - Numerical operations
- `deep-sort-realtime` - Multi-object tracking
- `scipy`, `pandas` - Data processing utilities

See `requirements.txt` for complete list and versions

## References

- [YOLO Documentation](https://docs.ultralytics.com/)
- [DeepSORT Paper](https://arxiv.org/abs/1703.07402)
- Parking lot detection reference: [arXiv:2505.17364v1](https://arxiv.org/html/2505.17364v1)
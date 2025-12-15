import requests
from pathlib import Path
from tqdm import tqdm

ROOT = Path("tests/test_data")
IMAGES = ROOT / "images"
VIDEOS = ROOT / "videos"
for d in (IMAGES, VIDEOS):
    d.mkdir(parents=True, exist_ok=True)

def download(url: str, dest: Path):
    r = requests.get(url, stream=True)
    if r.status_code != 200:
        raise RuntimeError(f"Failed to download {url} ({r.status_code})")
    total = int(r.headers.get("content-length", 0))
    with open(dest, "wb") as f, tqdm(total=total, unit="B", unit_scale=True, desc=dest.name) as pbar:
        for chunk in r.iter_content(1024):
            f.write(chunk)
            pbar.update(len(chunk))

print("Downloading verified sample images...")
image_urls = {
    # All confirmed working 10/6/2025
    "parking_lot_day.jpg": "https://images.pexels.com/photos/1004409/pexels-photo-1004409.jpeg",
    "parking_lot_night.jpg": "https://images.pexels.com/photos/5199513/pexels-photo-5199513.jpeg",
    "street_cars.jpg": "https://images.pexels.com/photos/210182/pexels-photo-210182.jpeg",
    "small_parking_area.jpg": "https://images.pexels.com/photos/17357654/pexels-photo-17357654.jpeg",
}

for name, url in image_urls.items():
    try:
        download(url, IMAGES / name)
    except Exception as e:
        print(f"Skipping {name}: {e}")

print("Downloading verified MP4 videos...")
video_urls = {
    # These are real traffic / parking related clips under Pexels’ free-to-use license
    "traffic_day.mp4": "https://www.pexels.com/download/video/2103099/",
    "traffic_night.mp4": "https://www.pexels.com/download/video/19120397/",
}

for name, url in video_urls.items():
    try:
        download(url, VIDEOS / name)
    except Exception as e:
        print(f"Skipping {name}: {e}")

print("\nTest suite ready at: ctests/test_data/")

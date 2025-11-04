import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.utils.db import Base, engine, SessionLocal
from app.models.parking_lot import ParkingLot

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture()
def db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Test data for parking lot
test_lot_data = {
    "name": "Lot C",
    "address": "W 9th Street, Rolla, MO",
    "total_spaces": 50,
    "description": "Rolla Parking Lot",
    "init_frame_path": "/frames/lot_c.jpg",
    "video_path": "/videos/lot_c.mp4",
    "video_start_time": 0.0
}

# Tests for parking lot routes
def test_create_parking_lot():
    response = client.post("/lots/", json=test_lot_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == test_lot_data["name"]
    assert "id" in data

def test_get_all_parking_lots():
    response = client.get("/lots/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

def test_get_parking_lot_by_id():
    create_resp = client.post("/lots/", json=test_lot_data)
    lot_id = create_resp.json()["id"]

    response = client.get(f"/lots/{lot_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == lot_id

def test_update_parking_lot():
    create_resp = client.post("/lots/", json=test_lot_data)
    lot_id = create_resp.json()["id"]

    updates = {"description": "Updated description", "total_spaces": 60}
    response = client.put(f"/lots/{lot_id}", json=updates)
    assert response.status_code == 200
    data = response.json()
    assert data["description"] == "Updated description"
    assert data["total_spaces"] == 60

def test_delete_parking_lot():
    create_resp = client.post("/lots/", json=test_lot_data)
    lot_id = create_resp.json()["id"]

    response = client.delete(f"/lots/{lot_id}")
    assert response.status_code == 204

    get_resp = client.get(f"/lots/{lot_id}")
    assert get_resp.status_code == 404

import pytest
from fastapi.testclient import TestClient
from app.main import app

# Create client - will use test database via dependency override
client = TestClient(app)

@pytest.fixture(autouse=True)
def use_test_db(override_get_db):
    pass

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

# Test that creating a parking lot works
def test_create_parking_lot():
    response = client.post("/lots/", json=test_lot_data)
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == test_lot_data["name"]
    assert "id" in data

# Test that getting parking lots works
def test_get_all_parking_lots():
    # Create a parking lot first
    create_resp = client.post("/lots/", json=test_lot_data)
    assert create_resp.status_code == 201
    
    response = client.get("/lots/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

# Test that getting a parking lot by ID works
def test_get_parking_lot_by_id():
    create_resp = client.post("/lots/", json=test_lot_data)
    lot_id = create_resp.json()["id"]

    response = client.get(f"/lots/{lot_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == lot_id

# Test that updating a parking lot works
def test_update_parking_lot():
    create_resp = client.post("/lots/", json=test_lot_data)
    lot_id = create_resp.json()["id"]

    updates = {"description": "Updated description", "total_spaces": 60}
    response = client.put(f"/lots/{lot_id}", json=updates)
    assert response.status_code == 200
    data = response.json()
    assert data["description"] == "Updated description"
    assert data["total_spaces"] == 60

# Test that deleting a parking lot works
def test_delete_parking_lot():
    create_resp = client.post("/lots/", json=test_lot_data)
    lot_id = create_resp.json()["id"]

    response = client.delete(f"/lots/{lot_id}")
    assert response.status_code == 204

    get_resp = client.get(f"/lots/{lot_id}")
    assert get_resp.status_code == 404

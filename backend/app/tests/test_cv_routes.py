from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_spot_status_by_bbox(override_get_db):
    # create lot
    lot_payload = {"name": "Demo CV Lot", "total_spaces": 1}
    r = client.post("/lots/", json=lot_payload)
    assert r.status_code == 201
    lot_id = r.json()["id"]

    # init with one polygon
    annotations = [{"points": [[10,10],[20,10],[20,20],[10,20]]}]
    init = client.post(f"/lots/{lot_id}/init", json={"annotations": annotations})
    assert init.status_code == 200
    got = init.json()
    spot_id = got["parking_spots"][0]["id"]

    # post bbox inside polygon
    bbox = [[12,12],[18,12],[18,18],[12,18]]
    resp = client.post("/cv/spot_status_by_bbox/", json={"parking_lot_id": lot_id, "bbox": bbox, "status": "occupied"})
    assert resp.status_code == 201
    data = resp.json()
    assert data["parking_spot_id"] == spot_id

    # check that current_status updated
    list_resp = client.get(f"/lots/{lot_id}/spots")
    assert list_resp.status_code == 200
    spots = list_resp.json()["spots"]
    s = next(s for s in spots if s["id"] == spot_id)
    assert s["current_status"] == "occupied"

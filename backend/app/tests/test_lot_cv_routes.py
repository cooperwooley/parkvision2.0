import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture(autouse=True)
def use_test_db(override_get_db):
    pass


def test_init_and_update_spot():
    # create lot
    lot_payload = {"name": "Demo Lot", "address": "Addr", "total_spaces": 0, "description": "d"}
    r = client.post("/lots/", json=lot_payload)
    assert r.status_code == 201
    lot = r.json()
    lot_id = lot["id"]

    annotations = [
        {"points": [[0,0],[10,0],[10,10],[0,10]]},
        {"points": [[20,0],[30,0],[30,10],[20,10]]}
    ]
    init_resp = client.post(f"/lots/{lot_id}/init", json={"annotations": annotations})
    assert init_resp.status_code == 200
    got = init_resp.json()
    assert "parking_spots" in got
    assert len(got["parking_spots"]) >= 2

    spot_id = got["parking_spots"][0]["id"]
    upd = client.post(f"/lots/{lot_id}/spots/{spot_id}/update", json={"status": "occupied", "meta": {"track_id": 1}})
    assert upd.status_code == 200
    data = upd.json()
    assert data["spot_id"] == spot_id
    assert data["status"] == "occupied"

    # list spots and check status
    list_resp = client.get(f"/lots/{lot_id}/spots")
    assert list_resp.status_code == 200
    ldata = list_resp.json()
    assert "spots" in ldata
    found = [s for s in ldata["spots"] if s["id"] == spot_id]
    assert found and found[0]["last_status"] == "occupied"

    # summary
    sum_resp = client.get(f"/lots/{lot_id}/status")
    assert sum_resp.status_code == 200
    sdata = sum_resp.json()
    assert str(spot_id) in map(str, sdata["summary"].keys()) or spot_id in sdata["summary"]
    # single spot status
    single_resp = client.get(f"/lots/{lot_id}/spots/{spot_id}/status")
    assert single_resp.status_code == 200
    single = single_resp.json()
    assert single["status"] == "occupied"

    # Bulk update: mark both spots vacant, then one occupied
    all_spots = got["parking_spots"]
    updates = [{"spot_id": s["id"], "status": "vacant"} for s in all_spots]
    bulk_resp = client.post(f"/lots/{lot_id}/bulk_update", json={"updates": updates})
    assert bulk_resp.status_code == 200
    # now mark first spot occupied
    first_id = all_spots[0]["id"]
    bulk2 = client.post(f"/lots/{lot_id}/bulk_update", json={"updates": [{"spot_id": first_id, "status": "occupied", "meta": {"frame": 1}}]})
    assert bulk2.status_code == 200
    # check summary
    s2 = client.get(f"/lots/{lot_id}/status").json()
    assert s2["summary"][str(first_id)] == "occupied" or s2["summary"][first_id] == "occupied"

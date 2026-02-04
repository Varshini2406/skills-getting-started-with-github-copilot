import sys
from pathlib import Path

# Ensure `src` is importable
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from fastapi.testclient import TestClient
from app import app, activities


client = TestClient(app)


def test_get_activities():
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_signup_success_and_cleanup():
    email = "testuser@example.com"
    # ensure not already present
    if email in activities["Chess Club"]["participants"]:
        activities["Chess Club"]["participants"].remove(email)

    resp = client.post(f"/activities/Chess Club/signup", params={"email": email})
    assert resp.status_code == 200
    body = resp.json()
    assert "Signed up" in body.get("message", "")

    # Verify the in-memory activities store was updated
    assert email in activities["Chess Club"]["participants"]

    # Cleanup: remove test email
    activities["Chess Club"]["participants"].remove(email)


def test_signup_already_registered():
    existing = activities["Chess Club"]["participants"][0]
    resp = client.post(f"/activities/Chess Club/signup", params={"email": existing})
    assert resp.status_code == 400


def test_signup_activity_not_found():
    resp = client.post(f"/activities/NotAnActivity/signup", params={"email": "a@b.com"})
    assert resp.status_code == 404

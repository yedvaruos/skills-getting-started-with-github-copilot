import copy
import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset the in-memory activities dict between tests."""
    original = copy.deepcopy(activities)
    yield
    activities.clear()
    activities.update(original)


def test_get_activities():
    client = TestClient(app)
    resp = client.get("/activities")
    assert resp.status_code == 200
    data = resp.json()
    assert "Chess Club" in data
    assert isinstance(data["Chess Club"]["participants"], list)


def test_signup_and_remove_participant():
    client = TestClient(app)
    email = "test.user@example.com"

    # Sign up
    resp = client.post(f"/activities/Chess%20Club/signup?email={email}")
    assert resp.status_code == 200
    assert "Signed up" in resp.json()["message"]

    # Ensure participant shows up
    resp = client.get("/activities")
    assert email in resp.json()["Chess Club"]["participants"]

    # Remove participant
    resp = client.delete(f"/activities/Chess%20Club/participants?email={email}")
    assert resp.status_code == 200
    assert "Unregistered" in resp.json()["message"]

    resp = client.get("/activities")
    assert email not in resp.json()["Chess Club"]["participants"]


def test_duplicate_signup_returns_400():
    client = TestClient(app)
    existing = "michael@mergington.edu"
    resp = client.post(f"/activities/Chess%20Club/signup?email={existing}")
    assert resp.status_code == 400


def test_remove_nonexistent_participant_returns_404():
    client = TestClient(app)
    resp = client.delete("/activities/Chess%20Club/participants?email=notfound@example.com")
    assert resp.status_code == 404

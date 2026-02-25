import copy
import pytest
from fastapi.testclient import TestClient

from src.app import app, activities

# snapshot of original data for resetting
ORIGINAL_ACTIVITIES = copy.deepcopy(activities)

@pytest.fixture(autouse=True)
def reset_activities():
    # Arrange: restore the in-memory state before each test
    activities.clear()
    activities.update(copy.deepcopy(ORIGINAL_ACTIVITIES))


def test_get_activities_returns_data():
    # Arrange
    client = TestClient(app)
    # Act
    resp = client.get("/activities")
    # Assert
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data


def test_successful_signup_adds_participant():
    client = TestClient(app)
    email = "new@mergington.edu"
    # Act
    resp = client.post(f"/activities/Chess%20Club/signup?email={email}")
    # Assert
    assert resp.status_code == 200
    assert "Signed up" in resp.json()["message"]
    assert email in activities["Chess Club"]["participants"]


def test_signup_duplicate_returns_400():
    client = TestClient(app)
    email = ORIGINAL_ACTIVITIES["Chess Club"]["participants"][0]
    resp = client.post(f"/activities/Chess%20Club/signup?email={email}")
    assert resp.status_code == 400


def test_signup_nonexistent_activity():
    client = TestClient(app)
    resp = client.post("/activities/NoSuch/signup?email=x")
    assert resp.status_code == 404


def test_delete_participant_removes_entry():
    client = TestClient(app)
    email = ORIGINAL_ACTIVITIES["Chess Club"]["participants"][0]
    resp = client.delete(f"/activities/Chess%20Club/signup?email={email}")
    assert resp.status_code == 200
    assert email not in activities["Chess Club"]["participants"]


def test_delete_nonexistent_activity():
    client = TestClient(app)
    resp = client.delete("/activities/NoSuch/signup?email=x")
    assert resp.status_code == 404


def test_delete_unregistered_email():
    client = TestClient(app)
    resp = client.delete("/activities/Chess%20Club/signup?email=absent@x")
    assert resp.status_code == 404


def test_root_redirects_to_static():
    client = TestClient(app)
    resp = client.get("/", follow_redirects=False)
    assert resp.status_code in (301, 302, 307)
    assert "/static/index.html" in resp.headers["location"]

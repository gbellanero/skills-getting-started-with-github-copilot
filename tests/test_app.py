from copy import deepcopy

import pytest
from fastapi.testclient import TestClient

from src.app import app, activities


@pytest.fixture()
def client():
    original = deepcopy(activities)
    try:
        yield TestClient(app)
    finally:
        activities.clear()
        activities.update(original)


def test_get_activities_returns_data(client):
    response = client.get("/activities")

    assert response.status_code == 200
    data = response.json()

    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Gym Class" in data


def test_signup_adds_participant(client):
    activity = "Programming Class"
    email = "newstudent@mergington.edu"

    assert email not in activities[activity]["participants"]

    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    assert response.status_code == 200
    assert email in activities[activity]["participants"]


def test_signup_duplicate_rejected(client):
    activity = "Gym Class"
    email = activities[activity]["participants"][0]

    response = client.post(f"/activities/{activity}/signup", params={"email": email})

    assert response.status_code == 400


def test_signup_unknown_activity_rejected(client):
    response = client.post("/activities/Unknown%20Club/signup", params={"email": "test@mergington.edu"})

    assert response.status_code == 404


def test_unregister_removes_participant(client):
    activity = "Chess Club"
    email = activities[activity]["participants"][0]

    response = client.delete(f"/activities/{activity}/unregister", params={"email": email})

    assert response.status_code == 200
    assert email not in activities[activity]["participants"]


def test_unregister_missing_participant_rejected(client):
    activity = "Chess Club"
    email = "missing@mergington.edu"

    response = client.delete(f"/activities/{activity}/unregister", params={"email": email})

    assert response.status_code == 400

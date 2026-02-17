"""Tests for the FastAPI application"""
import pytest


def test_get_activities(client):
    """Test getting the list of activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert "Chess Club" in data
    assert "Programming Class" in data
    assert "Basketball Team" in data


def test_get_activities_structure(client):
    """Test that activities have the correct structure"""
    response = client.get("/activities")
    data = response.json()
    activity = data["Chess Club"]
    
    assert "description" in activity
    assert "schedule" in activity
    assert "max_participants" in activity
    assert "participants" in activity
    assert isinstance(activity["participants"], list)


def test_signup_for_activity(client):
    """Test successful signup for an activity"""
    response = client.post(
        "/activities/Chess Club/signup?email=newstudent@mergington.edu"
    )
    assert response.status_code == 200
    data = response.json()
    assert "Signed up" in data["message"]
    assert "newstudent@mergington.edu" in data["message"]


def test_signup_persists_participant(client):
    """Test that signup adds the participant to the activity"""
    # Signup
    client.post("/activities/Chess Club/signup?email=newstudent@mergington.edu")
    
    # Check that participant was added
    response = client.get("/activities")
    activities = response.json()
    assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]


def test_signup_activity_not_found(client):
    """Test signup returns 404 when activity doesn't exist"""
    response = client.post(
        "/activities/Nonexistent Activity/signup?email=student@mergington.edu"
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_already_registered(client):
    """Test signup returns 400 when student is already registered"""
    response = client.post(
        "/activities/Chess Club/signup?email=michael@mergington.edu"
    )
    assert response.status_code == 400
    assert "already signed up" in response.json()["detail"]


def test_unregister_from_activity(client):
    """Test successful unregistration from an activity"""
    response = client.delete(
        "/activities/Chess Club/unregister?email=michael@mergington.edu"
    )
    assert response.status_code == 200
    data = response.json()
    assert "Unregistered" in data["message"]


def test_unregister_removes_participant(client):
    """Test that unregister removes the participant from the activity"""
    # Unregister
    client.delete(
        "/activities/Chess Club/unregister?email=michael@mergington.edu"
    )
    
    # Check that participant was removed
    response = client.get("/activities")
    activities = response.json()
    assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]
    assert "daniel@mergington.edu" in activities["Chess Club"]["participants"]


def test_unregister_activity_not_found(client):
    """Test unregister returns 404 when activity doesn't exist"""
    response = client.delete(
        "/activities/Nonexistent Activity/unregister?email=student@mergington.edu"
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_not_registered(client):
    """Test unregister returns 400 when student is not registered"""
    response = client.delete(
        "/activities/Chess Club/unregister?email=notregistered@mergington.edu"
    )
    assert response.status_code == 400
    assert "not registered" in response.json()["detail"]


def test_signup_and_unregister_flow(client):
    """Test complete flow: signup then unregister"""
    email = "testflow@mergington.edu"
    activity = "Programming Class"
    
    # Initial check - not registered
    response = client.get("/activities")
    assert email not in response.json()[activity]["participants"]
    
    # Sign up
    response = client.post(f"/activities/{activity}/signup?email={email}")
    assert response.status_code == 200
    
    # Check signed up
    response = client.get("/activities")
    assert email in response.json()[activity]["participants"]
    
    # Unregister
    response = client.delete(f"/activities/{activity}/unregister?email={email}")
    assert response.status_code == 200
    
    # Check unregistered
    response = client.get("/activities")
    assert email not in response.json()[activity]["participants"]

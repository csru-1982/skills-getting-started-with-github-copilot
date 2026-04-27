"""
Integration tests for FastAPI endpoints using AAA pattern.
Tests all HTTP endpoints with success and error cases.
"""

import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_all_activities(self, client):
        # Arrange: No setup needed, data is pre-populated in the app
        
        # Act: Make GET request
        response = client.get("/activities")
        
        # Assert: Verify response
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0
        assert "Chess Club" in data
        assert "Programming Class" in data

    def test_get_activities_returns_correct_structure(self, client):
        # Arrange: No setup needed
        
        # Act: Make GET request
        response = client.get("/activities")
        
        # Assert: Verify response structure
        assert response.status_code == 200
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)

    def test_get_activities_participants_are_emails(self, client):
        # Arrange: No setup needed
        
        # Act: Make GET request
        response = client.get("/activities")
        
        # Assert: Verify participants are email addresses
        assert response.status_code == 200
        activities = response.json()
        
        for activity_data in activities.values():
            for participant in activity_data["participants"]:
                assert "@" in participant
                assert isinstance(participant, str)


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_happy_path(self, client):
        # Arrange: Prepare test data
        activity_name = "Chess Club"
        email = "newstudent@mergington.edu"
        
        # Act: Make POST request to signup
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert: Verify successful signup
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        assert email in response.json()["message"]
        
        # Verify participant was added
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities[activity_name]["participants"]

    def test_signup_activity_not_found(self, client):
        # Arrange: Prepare test data with non-existent activity
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"
        
        # Act: Make POST request to signup for non-existent activity
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert: Verify 404 error
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_signup_duplicate_email(self, client):
        # Arrange: Prepare test data and ensure email is already in participants
        activity_name = "Chess Club"
        email = "michael@mergington.edu"  # Already in Chess Club
        
        # Act: Try to signup with duplicate email
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert: Verify 400 error for duplicate signup
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"].lower()

    def test_signup_missing_email_parameter(self, client):
        # Arrange: Prepare activity name without email parameter
        activity_name = "Chess Club"
        
        # Act: Make POST request without email parameter
        response = client.post(f"/activities/{activity_name}/signup")
        
        # Assert: Verify validation error
        assert response.status_code == 422  # Unprocessable Entity

    def test_signup_increases_participant_count(self, client):
        # Arrange: Get initial participant count
        activity_name = "Tennis Club"
        email = "participant_test@mergington.edu"
        
        initial_response = client.get("/activities")
        initial_count = len(initial_response.json()[activity_name]["participants"])
        
        # Act: Signup new participant
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert: Verify participant count increased
        assert response.status_code == 200
        updated_response = client.get("/activities")
        updated_count = len(updated_response.json()[activity_name]["participants"])
        assert updated_count == initial_count + 1


class TestUnregisterFromActivity:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_happy_path(self, client):
        # Arrange: Prepare test data with existing participant
        activity_name = "Chess Club"
        email = "daniel@mergington.edu"  # Existing participant
        
        # Act: Make DELETE request to unregister
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        
        # Assert: Verify successful unregister
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email not in activities[activity_name]["participants"]

    def test_unregister_activity_not_found(self, client):
        # Arrange: Prepare test data with non-existent activity
        activity_name = "Nonexistent Activity"
        email = "student@mergington.edu"
        
        # Act: Make DELETE request for non-existent activity
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        
        # Assert: Verify 404 error
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_unregister_email_not_registered(self, client):
        # Arrange: Prepare test data with email not in activity
        activity_name = "Drama Club"
        email = "notregistered@mergington.edu"  # Not in Drama Club
        
        # Act: Try to unregister email that's not registered
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        
        # Assert: Verify 400 error
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"].lower()

    def test_unregister_missing_email_parameter(self, client):
        # Arrange: Prepare activity name without email parameter
        activity_name = "Chess Club"
        
        # Act: Make DELETE request without email parameter
        response = client.delete(f"/activities/{activity_name}/unregister")
        
        # Assert: Verify validation error
        assert response.status_code == 422  # Unprocessable Entity

    def test_unregister_decreases_participant_count(self, client):
        # Arrange: Get initial participant count and signup a test participant
        activity_name = "Art Gallery"
        email = "test_unregister@mergington.edu"
        
        # First, signup the participant
        client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        before_response = client.get("/activities")
        before_count = len(before_response.json()[activity_name]["participants"])
        
        # Act: Unregister the participant
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        
        # Assert: Verify participant count decreased
        assert response.status_code == 200
        after_response = client.get("/activities")
        after_count = len(after_response.json()[activity_name]["participants"])
        assert after_count == before_count - 1

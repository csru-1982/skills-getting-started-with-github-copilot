"""
Unit tests for business logic and validation using AAA pattern.
"""

import pytest


class TestDuplicateSignupPrevention:
    """Tests for duplicate signup prevention"""

    def test_cannot_signup_same_email_twice(self, client):
        # Arrange: Prepare test data
        activity_name = "Robotics Club"
        email = "duplicate_test@mergington.edu"
        
        # Act: First signup
        first_response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert: First signup succeeds
        assert first_response.status_code == 200
        
        # Act: Try to signup again with same email
        second_response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert: Second signup fails
        assert second_response.status_code == 400
        assert "already signed up" in second_response.json()["detail"].lower()

    def test_first_signup_actually_added(self, client):
        # Arrange: Prepare test data
        activity_name = "Science Olympiad"
        email = "first_signup@mergington.edu"
        
        # Act: Signup participant
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert: Verify email is in participants
        assert response.status_code == 200
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities[activity_name]["participants"]


class TestUnregisterValidation:
    """Tests for unregister validation logic"""

    def test_cannot_unregister_unregistered_email(self, client):
        # Arrange: Prepare test data with email not in any activity
        activity_name = "Basketball Team"
        email = "never_registered@mergington.edu"
        
        # Act: Try to unregister email that was never registered
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        
        # Assert: Verify 400 error
        assert response.status_code == 400
        assert "not registered" in response.json()["detail"].lower()

    def test_unregister_actually_removes_participant(self, client):
        # Arrange: Signup participant first
        activity_name = "Drama Club"
        email = "remove_me@mergington.edu"
        
        client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Verify email is in participants
        before_response = client.get("/activities")
        assert email in before_response.json()[activity_name]["participants"]
        
        # Act: Unregister the participant
        response = client.delete(
            f"/activities/{activity_name}/unregister?email={email}"
        )
        
        # Assert: Verify email is no longer in participants
        assert response.status_code == 200
        after_response = client.get("/activities")
        assert email not in after_response.json()[activity_name]["participants"]


class TestErrorMessages:
    """Tests for descriptive error messages"""

    def test_duplicate_signup_error_message_is_descriptive(self, client):
        # Arrange: Prepare test data
        activity_name = "Programming Class"
        email = "emma@mergington.edu"  # Already registered
        
        # Act: Try to signup with duplicate email
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert: Error message is descriptive
        assert response.status_code == 400
        error_detail = response.json()["detail"]
        assert "already signed up" in error_detail.lower()
        assert email not in error_detail or "activity" in error_detail.lower()

    def test_activity_not_found_error_message_is_descriptive(self, client):
        # Arrange: Prepare test data with invalid activity
        activity_name = "Invalid Activity XYZ"
        email = "test@mergington.edu"
        
        # Act: Try to signup for nonexistent activity
        response = client.post(
            f"/activities/{activity_name}/signup?email={email}"
        )
        
        # Assert: Error message is descriptive
        assert response.status_code == 404
        error_detail = response.json()["detail"]
        assert "not found" in error_detail.lower()

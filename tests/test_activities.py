"""
Unit tests for the activities endpoints.
"""
import pytest


class TestGetActivities:
    """Tests for the GET /activities endpoint."""

    def test_get_activities_returns_200(self, client):
        """Test that GET /activities returns a 200 status code."""
        response = client.get("/activities")
        assert response.status_code == 200

    def test_get_activities_returns_dict(self, client):
        """Test that GET /activities returns a dictionary."""
        response = client.get("/activities")
        assert isinstance(response.json(), dict)

    def test_get_activities_contains_expected_activities(self, client):
        """Test that the activities list contains expected activities."""
        response = client.get("/activities")
        activities = response.json()
        
        expected_activities = [
            "Chess Club",
            "Programming Class",
            "Gym Class",
            "Basketball Team",
            "Tennis Club",
            "Art Studio",
            "Drama Club",
            "Debate Team",
            "Science Club"
        ]
        
        for activity in expected_activities:
            assert activity in activities

    def test_activity_has_required_fields(self, client):
        """Test that each activity has required fields."""
        response = client.get("/activities")
        activities = response.json()
        
        required_fields = ["description", "schedule", "max_participants", "participants"]
        
        for activity_name, activity_data in activities.items():
            for field in required_fields:
                assert field in activity_data, f"Activity {activity_name} missing field {field}"

    def test_participants_is_list(self, client):
        """Test that participants field is a list."""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data["participants"], list), \
                f"Activity {activity_name} participants is not a list"

    def test_max_participants_is_positive_number(self, client):
        """Test that max_participants is a positive number."""
        response = client.get("/activities")
        activities = response.json()
        
        for activity_name, activity_data in activities.items():
            assert isinstance(activity_data["max_participants"], int), \
                f"Activity {activity_name} max_participants is not an integer"
            assert activity_data["max_participants"] > 0, \
                f"Activity {activity_name} max_participants is not positive"


class TestSignupForActivity:
    """Tests for the POST /activities/{activity_name}/signup endpoint."""

    def test_signup_returns_200_on_success(self, client, sample_activity, sample_email):
        """Test that signup returns a 200 status code on success."""
        response = client.post(
            f"/activities/{sample_activity}/signup",
            params={"email": sample_email}
        )
        assert response.status_code == 200

    def test_signup_returns_success_message(self, client, sample_activity, sample_email):
        """Test that signup returns a success message."""
        response = client.post(
            f"/activities/{sample_activity}/signup",
            params={"email": sample_email}
        )
        result = response.json()
        assert "message" in result
        assert sample_email in result["message"]
        assert sample_activity in result["message"]

    def test_signup_adds_participant_to_activity(self, client, sample_activity):
        """Test that signup adds the participant to the activity."""
        email = "newstudent@mergington.edu"
        
        # Get initial participant list
        initial_response = client.get("/activities")
        initial_participants = initial_response.json()[sample_activity]["participants"]
        initial_count = len(initial_participants)
        
        # Signup
        client.post(
            f"/activities/{sample_activity}/signup",
            params={"email": email}
        )
        
        # Check updated participant list
        updated_response = client.get("/activities")
        updated_participants = updated_response.json()[sample_activity]["participants"]
        updated_count = len(updated_participants)
        
        assert updated_count == initial_count + 1
        assert email in updated_participants

    def test_signup_fails_with_nonexistent_activity(self, client, sample_email):
        """Test that signup fails with a nonexistent activity."""
        response = client.post(
            "/activities/Nonexistent Club/signup",
            params={"email": sample_email}
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_signup_fails_on_duplicate_registration(self, client, sample_activity):
        """Test that signup fails when registering the same email twice."""
        email = "duplicate@mergington.edu"
        
        # First signup should succeed
        response1 = client.post(
            f"/activities/{sample_activity}/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Second signup should fail
        response2 = client.post(
            f"/activities/{sample_activity}/signup",
            params={"email": email}
        )
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"].lower()

    def test_signup_with_special_characters_in_activity_name(self, client):
        """Test that signup works with special characters in activity names (URL encoding)."""
        email = "test@mergington.edu"
        activity = "Basketball Team"
        
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        
        assert response.status_code == 200


class TestUnregisterFromActivity:
    """Tests for the DELETE /activities/{activity_name}/unregister endpoint."""

    def test_unregister_returns_200_on_success(self, client, sample_activity):
        """Test that unregister returns a 200 status code on success."""
        email = "unregister_test@mergington.edu"
        
        # First, sign up
        client.post(
            f"/activities/{sample_activity}/signup",
            params={"email": email}
        )
        
        # Then, unregister
        response = client.delete(
            f"/activities/{sample_activity}/unregister",
            params={"email": email}
        )
        assert response.status_code == 200

    def test_unregister_returns_success_message(self, client, sample_activity):
        """Test that unregister returns a success message."""
        email = "unregister_msg_test@mergington.edu"
        
        # Sign up first
        client.post(
            f"/activities/{sample_activity}/signup",
            params={"email": email}
        )
        
        # Unregister
        response = client.delete(
            f"/activities/{sample_activity}/unregister",
            params={"email": email}
        )
        result = response.json()
        assert "message" in result
        assert "unregister" in result["message"].lower()

    def test_unregister_removes_participant(self, client, sample_activity):
        """Test that unregister removes the participant from the activity."""
        email = "remove_participant@mergington.edu"
        
        # Sign up
        client.post(
            f"/activities/{sample_activity}/signup",
            params={"email": email}
        )
        
        # Verify signup worked
        response = client.get("/activities")
        assert email in response.json()[sample_activity]["participants"]
        
        # Unregister
        client.delete(
            f"/activities/{sample_activity}/unregister",
            params={"email": email}
        )
        
        # Verify unregister worked
        response = client.get("/activities")
        assert email not in response.json()[sample_activity]["participants"]

    def test_unregister_fails_with_nonexistent_activity(self, client, sample_email):
        """Test that unregister fails with a nonexistent activity."""
        response = client.delete(
            "/activities/Nonexistent Club/unregister",
            params={"email": sample_email}
        )
        assert response.status_code == 404

    def test_unregister_fails_when_not_signed_up(self, client, sample_activity):
        """Test that unregister fails when the student is not signed up."""
        email = "not_signed_up@mergington.edu"
        
        response = client.delete(
            f"/activities/{sample_activity}/unregister",
            params={"email": email}
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"].lower()

    def test_unregister_twice_fails(self, client, sample_activity):
        """Test that unregistering twice fails."""
        email = "double_unregister@mergington.edu"
        
        # Sign up
        client.post(
            f"/activities/{sample_activity}/signup",
            params={"email": email}
        )
        
        # First unregister should succeed
        response1 = client.delete(
            f"/activities/{sample_activity}/unregister",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Second unregister should fail
        response2 = client.delete(
            f"/activities/{sample_activity}/unregister",
            params={"email": email}
        )
        assert response2.status_code == 400


class TestRootEndpoint:
    """Tests for the GET / endpoint."""

    def test_root_redirects_to_static(self, client):
        """Test that the root endpoint redirects to static HTML."""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307  # Temporary redirect
        assert "/static/index.html" in response.headers["location"]

    def test_root_redirect_follows_to_html(self, client):
        """Test that following the redirect from root returns HTML."""
        response = client.get("/", follow_redirects=True)
        assert response.status_code == 200

"""
Integration tests for the FastAPI activities management application
"""
import pytest


class TestActivitiesEndpoint:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_list(self, client):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        
        activities = response.json()
        assert isinstance(activities, dict)
        assert len(activities) > 0
        
    def test_get_activities_contains_expected_fields(self, client):
        """Test that each activity has all required fields"""
        response = client.get("/activities")
        activities = response.json()
        
        # Check at least one activity
        first_activity = next(iter(activities.values()))
        assert "description" in first_activity
        assert "schedule" in first_activity
        assert "max_participants" in first_activity
        assert "participants" in first_activity
        
    def test_get_activities_contains_chess_club(self, client):
        """Test that Chess Club activity exists with initial participants"""
        response = client.get("/activities")
        activities = response.json()
        
        assert "Chess Club" in activities
        activity = activities["Chess Club"]
        assert activity["description"] == "Learn strategies and compete in chess tournaments"
        assert isinstance(activity["participants"], list)


class TestRootEndpoint:
    """Tests for GET / endpoint"""

    def test_root_redirects_to_static(self, client):
        """Test that GET / redirects to /static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]


class TestSignupEndpoint:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_success(self, client, sample_activity, sample_email):
        """Test successful signup for an activity"""
        # Get initial participant count
        activities_before = client.get("/activities").json()
        initial_count = len(activities_before[sample_activity]["participants"])
        
        # Signup
        response = client.post(
            f"/activities/{sample_activity}/signup",
            params={"email": sample_email}
        )
        
        assert response.status_code == 200
        assert "Signed up" in response.json()["message"]
        assert sample_email in response.json()["message"]
        
        # Verify participant was added
        activities_after = client.get("/activities").json()
        assert len(activities_after[sample_activity]["participants"]) == initial_count + 1
        assert sample_email in activities_after[sample_activity]["participants"]

    def test_signup_duplicate_fails(self, client, sample_activity, sample_email):
        """Test that signing up twice with same email fails"""
        # First signup
        response1 = client.post(
            f"/activities/{sample_activity}/signup",
            params={"email": sample_email}
        )
        assert response1.status_code == 200
        
        # Second signup with same email
        response2 = client.post(
            f"/activities/{sample_activity}/signup",
            params={"email": sample_email}
        )
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"].lower()

    def test_signup_invalid_activity(self, client, sample_email, invalid_activity):
        """Test that signing up for non-existent activity fails"""
        response = client.post(
            f"/activities/{invalid_activity}/signup",
            params={"email": sample_email}
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_signup_with_special_characters_in_email(self, client, sample_activity):
        """Test signup with valid email containing special characters"""
        special_email = "test.user+tag@mergington.edu"
        response = client.post(
            f"/activities/{sample_activity}/signup",
            params={"email": special_email}
        )
        
        assert response.status_code == 200
        
        # Verify it was added
        activities = client.get("/activities").json()
        assert special_email in activities[sample_activity]["participants"]

    def test_signup_with_url_encoded_activity_name(self, client):
        """Test signup with activity name that needs URL encoding"""
        response = client.post(
            "/activities/Programming%20Class/signup",
            params={"email": "test@mergington.edu"}
        )
        
        assert response.status_code == 200
        activities = client.get("/activities").json()
        assert "test@mergington.edu" in activities["Programming Class"]["participants"]


class TestUnregisterEndpoint:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_success(self, client, sample_activity, sample_email):
        """Test successful unregister from an activity"""
        # First signup
        client.post(
            f"/activities/{sample_activity}/signup",
            params={"email": sample_email}
        )
        
        # Verify signup
        activities = client.get("/activities").json()
        assert sample_email in activities[sample_activity]["participants"]
        initial_count = len(activities[sample_activity]["participants"])
        
        # Unregister
        response = client.delete(
            f"/activities/{sample_activity}/unregister",
            params={"email": sample_email}
        )
        
        assert response.status_code == 200
        assert "Unregistered" in response.json()["message"]
        
        # Verify participant was removed
        activities_after = client.get("/activities").json()
        assert sample_email not in activities_after[sample_activity]["participants"]
        assert len(activities_after[sample_activity]["participants"]) == initial_count - 1

    def test_unregister_not_registered(self, client, sample_activity, sample_email):
        """Test that unregistering someone not registered fails"""
        response = client.delete(
            f"/activities/{sample_activity}/unregister",
            params={"email": sample_email}
        )
        
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"].lower()

    def test_unregister_invalid_activity(self, client, sample_email, invalid_activity):
        """Test that unregistering from non-existent activity fails"""
        response = client.delete(
            f"/activities/{invalid_activity}/unregister",
            params={"email": sample_email}
        )
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_unregister_twice_fails(self, client, sample_activity, sample_email):
        """Test that unregistering twice fails on second attempt"""
        # First signup
        client.post(
            f"/activities/{sample_activity}/signup",
            params={"email": sample_email}
        )
        
        # First unregister
        response1 = client.delete(
            f"/activities/{sample_activity}/unregister",
            params={"email": sample_email}
        )
        assert response1.status_code == 200
        
        # Second unregister
        response2 = client.delete(
            f"/activities/{sample_activity}/unregister",
            params={"email": sample_email}
        )
        assert response2.status_code == 400
        assert "not signed up" in response2.json()["detail"].lower()


class TestSignupUnregisterFlow:
    """Tests for combined signup and unregister workflows"""

    def test_signup_unregister_cycle(self, client, sample_activity, sample_email):
        """Test a full signup and unregister cycle"""
        # Get initial state
        activities_initial = client.get("/activities").json()
        initial_participants = activities_initial[sample_activity]["participants"].copy()
        
        # Signup
        response_signup = client.post(
            f"/activities/{sample_activity}/signup",
            params={"email": sample_email}
        )
        assert response_signup.status_code == 200
        
        # Verify signup
        activities_after_signup = client.get("/activities").json()
        assert sample_email in activities_after_signup[sample_activity]["participants"]
        
        # Unregister
        response_unregister = client.delete(
            f"/activities/{sample_activity}/unregister",
            params={"email": sample_email}
        )
        assert response_unregister.status_code == 200
        
        # Verify return to initial state
        activities_final = client.get("/activities").json()
        assert activities_final[sample_activity]["participants"] == initial_participants

    def test_multiple_participants_signup_and_unregister(self, client, sample_activity):
        """Test multiple participants signing up and unregistering"""
        emails = ["alice@mergington.edu", "bob@mergington.edu", "charlie@mergington.edu"]
        
        # All signup
        for email in emails:
            response = client.post(
                f"/activities/{sample_activity}/signup",
                params={"email": email}
            )
            assert response.status_code == 200
        
        # Verify all signed up
        activities = client.get("/activities").json()
        for email in emails:
            assert email in activities[sample_activity]["participants"]
        
        # One person unregisters
        response = client.delete(
            f"/activities/{sample_activity}/unregister",
            params={"email": "bob@mergington.edu"}
        )
        assert response.status_code == 200
        
        # Verify correct person unregistered
        activities = client.get("/activities").json()
        assert "alice@mergington.edu" in activities[sample_activity]["participants"]
        assert "bob@mergington.edu" not in activities[sample_activity]["participants"]
        assert "charlie@mergington.edu" in activities[sample_activity]["participants"]

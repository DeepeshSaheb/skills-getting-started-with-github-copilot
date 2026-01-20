import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app

client = TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to initial state before each test"""
    from app import activities
    # Store original state
    original = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Competitive basketball team for intramural and varsity play",
            "schedule": "Mondays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu"]
        },
        "Tennis Club": {
            "description": "Learn tennis skills and compete in matches",
            "schedule": "Wednesdays and Saturdays, 3:00 PM - 4:30 PM",
            "max_participants": 16,
            "participants": ["alex@mergington.edu", "maya@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore painting, drawing, and other visual arts",
            "schedule": "Tuesdays and Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["lucas@mergington.edu"]
        },
        "Music Ensemble": {
            "description": "Play instruments and perform in concerts",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:00 PM",
            "max_participants": 25,
            "participants": ["sarah@mergington.edu", "noah@mergington.edu"]
        },
        "Debate Club": {
            "description": "Develop argumentation and public speaking skills",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["grace@mergington.edu"]
        },
        "Science Olympiad": {
            "description": "Compete in science competitions and experiments",
            "schedule": "Tuesdays and Thursdays, 4:30 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["ethan@mergington.edu", "avery@mergington.edu"]
        }
    }
    yield
    # Restore original state after test
    activities.clear()
    activities.update(original)


class TestActivitiesEndpoint:
    """Tests for GET /activities endpoint"""

    def test_get_activities_returns_200(self, reset_activities):
        """Test that GET /activities returns status 200"""
        response = client.get("/activities")
        assert response.status_code == 200

    def test_get_activities_returns_all_activities(self, reset_activities):
        """Test that GET /activities returns all activities"""
        response = client.get("/activities")
        data = response.json()
        assert len(data) == 9
        assert "Chess Club" in data
        assert "Programming Class" in data

    def test_get_activities_contains_required_fields(self, reset_activities):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        data = response.json()
        
        for activity_name, activity_data in data.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data


class TestSignupEndpoint:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_new_participant_returns_200(self, reset_activities):
        """Test successful signup returns 200"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=newstudent@mergington.edu",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 200

    def test_signup_new_participant_adds_to_list(self, reset_activities):
        """Test that new participant is added to activity"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "newstudent@mergington.edu" in activities_data["Chess Club"]["participants"]

    def test_signup_duplicate_participant_returns_400(self, reset_activities):
        """Test that duplicate signup returns 400 error"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_nonexistent_activity_returns_404(self, reset_activities):
        """Test that signup to nonexistent activity returns 404"""
        response = client.post(
            "/activities/Nonexistent%20Activity/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_signup_returns_success_message(self, reset_activities):
        """Test that successful signup returns proper message"""
        response = client.post(
            "/activities/Chess%20Club/signup?email=newstudent@mergington.edu"
        )
        data = response.json()
        assert "message" in data
        assert "Signed up" in data["message"]
        assert "newstudent@mergington.edu" in data["message"]


class TestUnregisterEndpoint:
    """Tests for DELETE /activities/{activity_name}/unregister endpoint"""

    def test_unregister_existing_participant_returns_200(self, reset_activities):
        """Test successful unregister returns 200"""
        response = client.delete(
            "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200

    def test_unregister_removes_participant(self, reset_activities):
        """Test that participant is removed from activity"""
        response = client.delete(
            "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        
        activities_response = client.get("/activities")
        activities_data = activities_response.json()
        assert "michael@mergington.edu" not in activities_data["Chess Club"]["participants"]

    def test_unregister_nonexistent_participant_returns_400(self, reset_activities):
        """Test that unregistering nonexistent participant returns 400"""
        response = client.delete(
            "/activities/Chess%20Club/unregister?email=nonexistent@mergington.edu"
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"].lower()

    def test_unregister_from_nonexistent_activity_returns_404(self, reset_activities):
        """Test that unregister from nonexistent activity returns 404"""
        response = client.delete(
            "/activities/Nonexistent%20Activity/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert "not found" in response.json()["detail"].lower()

    def test_unregister_returns_success_message(self, reset_activities):
        """Test that successful unregister returns proper message"""
        response = client.delete(
            "/activities/Chess%20Club/unregister?email=michael@mergington.edu"
        )
        data = response.json()
        assert "message" in data
        assert "Unregistered" in data["message"]
        assert "michael@mergington.edu" in data["message"]

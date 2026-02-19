"""
Pytest configuration and fixtures for FastAPI tests
"""
import pytest
import sys
from pathlib import Path
from copy import deepcopy

# Add src directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from fastapi.testclient import TestClient
import app as app_module


# Store the original activities state
ORIGINAL_ACTIVITIES = {
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
        "description": "Competitive basketball team for varsity and JV players",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 15,
        "participants": ["james@mergington.edu"]
    },
    "Tennis Club": {
        "description": "Learn tennis skills and participate in friendly matches",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:00 PM",
        "max_participants": 16,
        "participants": ["lucas@mergington.edu", "isabella@mergington.edu"]
    },
    "Art Studio": {
        "description": "Painting, drawing, and visual arts exploration",
        "schedule": "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 18,
        "participants": ["grace@mergington.edu"]
    },
    "Music Ensemble": {
        "description": "Perform instrumental and vocal music with other students",
        "schedule": "Tuesdays, 4:00 PM - 5:30 PM",
        "max_participants": 25,
        "participants": ["noah@mergington.edu", "ava@mergington.edu"]
    },
    "Robotics Club": {
        "description": "Build and program robots for competitions and projects",
        "schedule": "Thursdays, 4:00 PM - 6:00 PM",
        "max_participants": 14,
        "participants": ["liam@mergington.edu"]
    },
    "Debate Team": {
        "description": "Develop critical thinking and public speaking skills",
        "schedule": "Mondays and Thursdays, 3:45 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["mason@mergington.edu", "charlotte@mergington.edu"]
    }
}


@pytest.fixture(autouse=True)
def reset_activities():
    """
    Automatically reset activities to original state before each test.
    This ensures tests don't affect each other.
    """
    # Reset to a deep copy of original activities
    app_module.activities.clear()
    app_module.activities.update(deepcopy(ORIGINAL_ACTIVITIES))
    yield


@pytest.fixture
def client():
    """
    Provides a TestClient instance for testing the FastAPI application.
    Each test gets a fresh client with the current app state.
    """
    return TestClient(app_module.app)


@pytest.fixture
def sample_email():
    """Provides a test email address"""
    return "test@mergington.edu"


@pytest.fixture
def sample_activity():
    """Provides a sample activity name that exists in the app"""
    return "Chess Club"


@pytest.fixture
def invalid_activity():
    """Provides an activity name that doesn't exist"""
    return "NonExistent Activity"

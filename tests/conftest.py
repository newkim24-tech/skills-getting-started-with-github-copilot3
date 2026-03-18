"""
Pytest configuration and fixtures for the test suite.
"""
import sys
from pathlib import Path
import uuid

import pytest
from fastapi.testclient import TestClient

# Add src directory to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app


@pytest.fixture
def client():
    """Provide a TestClient instance for testing the API."""
    return TestClient(app)


@pytest.fixture
def sample_email():
    """Provide a unique sample email for each test."""
    unique_id = str(uuid.uuid4())[:8]
    return f"test_{unique_id}@mergington.edu"


@pytest.fixture
def sample_activity():
    """Provide a sample activity name for testing."""
    return "Chess Club"

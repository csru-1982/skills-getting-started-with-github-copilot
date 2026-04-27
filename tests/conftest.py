"""
Pytest configuration and shared fixtures for FastAPI app tests.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app


@pytest.fixture
def client():
    """
    Fixture providing a TestClient connected to the app.
    This fixture is available to all tests in the suite.
    """
    return TestClient(app)

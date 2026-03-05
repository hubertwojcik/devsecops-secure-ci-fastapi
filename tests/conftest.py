"""Pytest configuration and fixtures."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.store import notes_store


@pytest.fixture(autouse=True)
def clear_store():
    """Clear the notes store before each test."""
    notes_store.clear()
    yield
    notes_store.clear()


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)

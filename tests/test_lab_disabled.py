"""Tests to verify lab endpoints are disabled by default."""

import os
from fastapi.testclient import TestClient


def test_lab_mode_disabled_by_default():
    """Test that LAB_MODE is disabled by default."""
    lab_mode = os.getenv("LAB_MODE", "0")
    assert lab_mode == "0", "LAB_MODE should be disabled (0) by default"


def test_unsafe_redirect_disabled(client: TestClient):
    """Test that unsafe redirect endpoint is disabled when LAB_MODE=0."""
    response = client.get("/lab/unsafe-redirect?next=/notes")
    assert response.status_code == 403
    assert "disabled" in response.json()["detail"].lower()


def test_unsafe_echo_disabled(client: TestClient):
    """Test that unsafe echo endpoint is disabled when LAB_MODE=0."""
    response = client.get("/lab/echo?data=test")
    assert response.status_code == 403
    assert "disabled" in response.json()["detail"].lower()


def test_unsafe_render_disabled(client: TestClient):
    """Test that unsafe render endpoint is disabled when LAB_MODE=0."""
    response = client.get("/lab/render?template=test")
    assert response.status_code == 403
    assert "disabled" in response.json()["detail"].lower()


def test_lab_endpoints_return_consistent_error(client: TestClient):
    """Test that all lab endpoints return consistent 403 error."""
    endpoints = [
        "/lab/unsafe-redirect",
        "/lab/echo",
        "/lab/render"
    ]
    
    for endpoint in endpoints:
        response = client.get(endpoint)
        assert response.status_code == 403, f"Endpoint {endpoint} should return 403"
        data = response.json()
        assert "detail" in data
        assert "disabled" in data["detail"].lower() or "lab" in data["detail"].lower()


def test_lab_mode_message_is_clear(client: TestClient):
    """Test that lab mode disabled message is clear and informative."""
    response = client.get("/lab/echo")
    assert response.status_code == 403
    
    detail = response.json()["detail"]
    # Should mention that lab endpoints are disabled
    assert "lab" in detail.lower() or "disabled" in detail.lower()

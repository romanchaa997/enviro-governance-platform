"""Tests module for enviro governance platform."""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Fixture for FastAPI test client."""
    from backend.app.main import app
    return TestClient(app)


def test_health_check(client):
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_remediation_plan_creation(client):
    """Test remediation plan endpoint."""
    payload = {
        "ecosystem_area_id": 1,
        "contamination_description": "Heavy metal contamination",
        "severity": "high",
    }
    response = client.post("/api/v1/remediation/plan", json=payload)
    assert response.status_code == 201

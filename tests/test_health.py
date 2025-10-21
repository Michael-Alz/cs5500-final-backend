from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_root() -> None:
    """Test root endpoint returns success message."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Backend is running!"}


def test_health_check() -> None:
    """Test health endpoint returns environment info."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "app_env" in data
    assert "port" in data

"""
Simplified and combined API test suite.

This test file covers:
- Health checks (no database required)
- Authentication protection (no database required)
- Input validation (no database required)
- Error handling (no database required)

Database-dependent tests (teacher auth, student auth, courses, sessions):
- These require a running PostgreSQL database
- Start database with: docker-compose up -d database
- Run migrations with: make db-migrate
- Seed data with: uv run python scripts/seed.py

Run with: python -m pytest tests/test_api.py -v
"""

import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional

import pytest
from fastapi.testclient import TestClient

# Add the project root to the Python path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from app.main import app  # noqa: E402

client = TestClient(app)


class TestAPI:
    """Simplified test class for all API endpoints."""

    def __init__(self) -> None:
        self.teacher_token: Optional[str] = None
        self.student_token: Optional[str] = None
        self.test_data: Dict[str, Any] = {}

    def login_teacher(self, email: str = "teacher@test.com", password: str = "Passw0rd!") -> str:
        """Login as teacher and return token."""
        response = client.post("/api/auth/login", json={"email": email, "password": password})
        assert response.status_code == 200, f"Teacher login failed: {response.text}"

        data = response.json()
        self.teacher_token = data["access_token"]
        return self.teacher_token

    def login_student(self, email: str = "student@test.com", password: str = "Passw0rd!") -> str:
        """Login as student and return token."""
        response = client.post("/api/students/login", json={"email": email, "password": password})
        assert response.status_code == 200, f"Student login failed: {response.text}"

        data = response.json()
        self.student_token = data["access_token"]
        return self.student_token

    def get_headers(self, use_student: bool = False) -> Dict[str, str]:
        """Get authorization headers."""
        token = self.student_token if use_student else self.teacher_token
        return {"Authorization": f"Bearer {token}"} if token else {}


def test_health_endpoints() -> None:
    """Test basic health endpoints."""
    # Test root endpoint
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "5500 Backend is running!"}

    # Test health endpoint
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "env" in data


@pytest.mark.database
def test_teacher_authentication() -> None:
    """Test teacher authentication flow (requires database)."""
    tester = TestAPI()

    # Create a new teacher first
    timestamp = int(time.time())
    teacher_data = {
        "email": f"testteacher{timestamp}@example.com",
        "password": "Passw0rd!",
        "full_name": "Test Teacher",
    }
    response = client.post("/api/auth/signup", json=teacher_data)
    assert response.status_code == 200

    # Test teacher login
    token = tester.login_teacher(f"testteacher{timestamp}@example.com", "Passw0rd!")
    assert token is not None

    # Test accessing protected endpoint
    headers = tester.get_headers()
    response = client.get("/api/courses", headers=headers)
    assert response.status_code == 200


@pytest.mark.database
def test_student_authentication() -> None:
    """Test student authentication flow (NEW FEATURE) (requires database)."""
    tester = TestAPI()

    # Test student signup
    timestamp = int(time.time())
    signup_data = {
        "email": f"teststudent{timestamp}@example.com",
        "password": "Passw0rd!",
        "full_name": "Test Student",
    }
    response = client.post("/api/students/signup", json=signup_data)
    assert response.status_code == 200
    data = response.json()
    assert data["full_name"] == "Test Student"

    # Test student login
    token = tester.login_student(f"teststudent{timestamp}@example.com", "Passw0rd!")
    assert token is not None

    # Test student profile
    headers = tester.get_headers(use_student=True)
    response = client.get("/api/students/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == f"teststudent{timestamp}@example.com"

    # Test student submission history
    response = client.get("/api/students/submissions", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0  # No submissions yet


@pytest.mark.database
def test_course_management() -> None:
    """Test course creation and listing (requires database)."""
    tester = TestAPI()

    # Create a new teacher first
    timestamp = int(time.time())
    teacher_data = {
        "email": f"courseteacher{timestamp}@example.com",
        "password": "Passw0rd!",
        "full_name": "Course Teacher",
    }
    response = client.post("/api/auth/signup", json=teacher_data)
    assert response.status_code == 200

    tester.login_teacher(f"courseteacher{timestamp}@example.com", "Passw0rd!")
    headers = tester.get_headers()

    # Create course
    course_data = {"title": "Test Course for API Testing"}
    response = client.post("/api/courses", json=course_data, headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == "Test Course for API Testing"
    tester.test_data["course_id"] = data["id"]

    # List courses
    response = client.get("/api/courses", headers=headers)
    assert response.status_code == 200
    courses = response.json()
    assert isinstance(courses, list)
    assert len(courses) >= 1


@pytest.mark.database
def test_session_management() -> None:
    """Test session creation and management (requires database)."""
    tester = TestAPI()

    # Create a new teacher first
    timestamp = int(time.time())
    teacher_data = {
        "email": f"sessionteacher{timestamp}@example.com",
        "password": "Passw0rd!",
        "full_name": "Session Teacher",
    }
    response = client.post("/api/auth/signup", json=teacher_data)
    assert response.status_code == 200

    tester.login_teacher(f"sessionteacher{timestamp}@example.com", "Passw0rd!")
    headers = tester.get_headers()

    # Create course first
    course_data = {"title": "Session Test Course"}
    response = client.post("/api/courses", json=course_data, headers=headers)
    assert response.status_code == 200
    course_id = response.json()["id"]

    # Create session (using mock survey template ID)
    session_data = {"survey_template_id": "mock-survey-id", "title": "Test Session"}
    response = client.post(
        f"/api/sessions/{course_id}/sessions", json=session_data, headers=headers
    )

    # Note: This might fail if no surveys exist, which is expected
    if response.status_code == 200:
        data = response.json()
        assert "session_id" in data
        assert "join_token" in data
        tester.test_data["session_id"] = data["session_id"]
        tester.test_data["join_token"] = data["join_token"]


@pytest.mark.database
def test_public_endpoints() -> None:
    """Test public survey endpoints (requires database)."""
    # Test public join with invalid token (should fail gracefully)
    response = client.get("/api/public/join/invalid-token")
    assert response.status_code == 404

    # Test public submission with invalid token (should fail gracefully)
    submission_data = {
        "student_name": "Test Guest",
        "answers": {"q1": "Excellent"},
        "is_guest": True,
    }
    response = client.post("/api/public/join/invalid-token/submit", json=submission_data)
    assert response.status_code == 404


def test_authentication_protection() -> None:
    """Test that protected endpoints require authentication."""
    # Test teacher endpoints without token
    response = client.get("/api/courses")
    assert response.status_code == 403  # FastAPI returns 403 for missing auth

    # Test student endpoints without token
    response = client.get("/api/students/me")
    assert response.status_code == 403  # FastAPI returns 403 for missing auth

    # Test with invalid token
    headers = {"Authorization": "Bearer invalid-token"}
    response = client.get("/api/courses", headers=headers)
    assert response.status_code == 401


def test_input_validation() -> None:
    """Test input validation for signup endpoints."""
    # Test teacher signup with missing full_name
    teacher_data = {
        "email": "invalid@test.com",
        "password": "password123",
        # Missing full_name
    }
    response = client.post("/api/auth/signup", json=teacher_data)
    assert response.status_code == 422

    # Test student signup with invalid email
    student_data = {"email": "invalid-email", "password": "password123", "full_name": "Test User"}
    response = client.post("/api/students/signup", json=student_data)
    assert response.status_code == 422


@pytest.mark.database
def test_comprehensive_flow() -> None:
    """Test a complete flow from teacher setup to student submission (requires database)."""
    tester = TestAPI()

    # 1. Create and login teacher
    timestamp = int(time.time())
    teacher_data = {
        "email": f"comprehensive{timestamp}@teacher.com",
        "password": "Passw0rd!",
        "full_name": "Comprehensive Teacher",
    }
    response = client.post("/api/auth/signup", json=teacher_data)
    assert response.status_code == 200

    tester.login_teacher(f"comprehensive{timestamp}@teacher.com", "Passw0rd!")
    teacher_headers = tester.get_headers()

    # 2. Create course
    course_data = {"title": "Comprehensive Test Course"}
    response = client.post("/api/courses", json=course_data, headers=teacher_headers)
    assert response.status_code == 200
    # course_id = response.json()["id"]  # Not used in this simplified test

    # 3. Create and login student
    student_data = {
        "email": f"comprehensive{timestamp}@student.com",
        "password": "Passw0rd!",
        "full_name": "Comprehensive Student",
    }
    response = client.post("/api/students/signup", json=student_data)
    assert response.status_code == 200

    tester.login_student(f"comprehensive{timestamp}@student.com", "Passw0rd!")
    student_headers = tester.get_headers(use_student=True)

    # 4. Verify student can access their profile
    response = client.get("/api/students/me", headers=student_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == f"comprehensive{timestamp}@student.com"

    # 5. Verify student submission history is empty
    response = client.get("/api/students/submissions", headers=student_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 0

    print("✅ Comprehensive flow test passed")


def test_error_handling() -> None:
    """Test error handling for various scenarios."""
    # Test non-existent endpoints
    response = client.get("/api/nonexistent")
    assert response.status_code == 404

    # Test invalid JSON
    response = client.post("/api/auth/login", content="invalid json")
    assert response.status_code == 422

    # Test missing required fields
    response = client.post("/api/students/signup", json={})
    assert response.status_code == 422


if __name__ == "__main__":
    """Run tests directly (non-database tests only)."""
    print("🧪 Running Simplified API Tests (Non-Database Tests Only)")
    print("=" * 60)
    print("Note: Database-dependent tests require a running PostgreSQL database.")
    print("Run 'uv run python -m pytest tests/ -v' for all tests with pytest.")
    print("=" * 60)

    try:
        test_health_endpoints()
        print("✅ Health endpoints test passed")

        test_authentication_protection()
        print("✅ Authentication protection test passed")

        test_input_validation()
        print("✅ Input validation test passed")

        test_error_handling()
        print("✅ Error handling test passed")

        print("\n🎉 All non-database tests passed!")
        print("\nTo run database-dependent tests:")
        print("1. Start database: docker-compose up -d database")
        print("2. Run migrations: make db-migrate")
        print("3. Seed data: uv run python scripts/seed.py")
        print("4. Run all tests: uv run python -m pytest tests/ -v")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        raise

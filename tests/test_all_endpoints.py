"""
Comprehensive test suite for all API endpoints.

This test file covers:
- Authentication endpoints
- Course management
- Survey creation and listing
- Session management
- Public survey submission
- Data cleanup

Run with: python -m pytest tests/test_all_endpoints.py -v
"""

from typing import Any, Dict, Optional

import pytest
import requests


class APITester:
    """Test client for all API endpoints."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.token: Optional[str] = None
        self.test_data: Dict[str, Any] = {}

    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make HTTP request with proper headers."""
        url = f"{self.base_url}{endpoint}"
        headers = kwargs.get("headers", {})

        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        kwargs["headers"] = headers
        return requests.request(method, url, **kwargs)

    def login(self, email: str = "teacher1@example.com", password: str = "Passw0rd!") -> str:
        """Login and store token."""
        response = self._make_request(
            "POST", "/api/auth/login", json={"email": email, "password": password}
        )
        assert response.status_code == 200, f"Login failed: {response.text}"

        data = response.json()
        self.token = data["access_token"]
        return self.token

    def test_health_check(self):
        """Test health endpoint."""
        response = self._make_request("GET", "/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        print("✅ Health check passed")

    def test_authentication(self):
        """Test authentication endpoints."""
        # Test login
        response = self._make_request(
            "POST",
            "/api/auth/login",
            json={"email": "teacher1@example.com", "password": "Passw0rd!"},
        )
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

        # Store token for other tests
        self.token = data["access_token"]
        print("✅ Authentication test passed")

    def test_courses(self):
        """Test course endpoints."""
        # List courses
        response = self._make_request("GET", "/api/courses")
        assert response.status_code == 200
        courses = response.json()
        assert isinstance(courses, list)

        # Store first course for session tests
        if courses:
            self.test_data["course_id"] = courses[0]["id"]
            print(f"✅ Found course: {courses[0]['title']}")

        print("✅ Course listing test passed")

    def test_surveys(self):
        """Test survey endpoints."""
        # List surveys
        response = self._make_request("GET", "/api/surveys/")
        assert response.status_code == 200
        surveys = response.json()
        assert isinstance(surveys, list)
        assert len(surveys) >= 2, "Should have at least 2 seed surveys"

        # Store first survey for session tests
        if surveys:
            self.test_data["survey_id"] = surveys[0]["id"]
            print(f"✅ Found survey: {surveys[0]['title']}")

        print("✅ Survey listing test passed")

    def test_create_survey(self):
        """Test survey creation."""
        import random
        import time

        survey_data = {
            "title": f"Test Survey for API Testing {int(time.time())}_{random.randint(1000, 9999)}",
            "questions": [
                {
                    "id": "q1",
                    "text": "How do you prefer to learn?",
                    "options": [
                        {
                            "label": "By reading",
                            "scores": {"Visual": 5, "Auditory": 0, "Kinesthetic": 0},
                        },
                        {
                            "label": "By listening",
                            "scores": {"Visual": 0, "Auditory": 5, "Kinesthetic": 0},
                        },
                        {
                            "label": "By doing",
                            "scores": {"Visual": 0, "Auditory": 0, "Kinesthetic": 5},
                        },
                    ],
                },
                {
                    "id": "q2",
                    "text": "What motivates you most?",
                    "options": [
                        {
                            "label": "Achievement",
                            "scores": {"Visual": 3, "Auditory": 0, "Kinesthetic": 0},
                        },
                        {
                            "label": "Recognition",
                            "scores": {"Visual": 0, "Auditory": 3, "Kinesthetic": 0},
                        },
                        {
                            "label": "Experience",
                            "scores": {"Visual": 0, "Auditory": 0, "Kinesthetic": 3},
                        },
                    ],
                },
                {
                    "id": "q3",
                    "text": "How do you process information?",
                    "options": [
                        {
                            "label": "Visually",
                            "scores": {"Visual": 4, "Auditory": 0, "Kinesthetic": 0},
                        },
                        {
                            "label": "Through sound",
                            "scores": {"Visual": 0, "Auditory": 4, "Kinesthetic": 0},
                        },
                        {
                            "label": "Through movement",
                            "scores": {"Visual": 0, "Auditory": 0, "Kinesthetic": 4},
                        },
                    ],
                },
                {
                    "id": "q4",
                    "text": "What helps you remember?",
                    "options": [
                        {
                            "label": "Pictures",
                            "scores": {"Visual": 3, "Auditory": 0, "Kinesthetic": 0},
                        },
                        {
                            "label": "Music",
                            "scores": {"Visual": 0, "Auditory": 3, "Kinesthetic": 0},
                        },
                        {
                            "label": "Physical activity",
                            "scores": {"Visual": 0, "Auditory": 0, "Kinesthetic": 3},
                        },
                    ],
                },
                {
                    "id": "q5",
                    "text": "How do you solve problems?",
                    "options": [
                        {
                            "label": "Draw diagrams",
                            "scores": {"Visual": 2, "Auditory": 0, "Kinesthetic": 0},
                        },
                        {
                            "label": "Talk it through",
                            "scores": {"Visual": 0, "Auditory": 2, "Kinesthetic": 0},
                        },
                        {
                            "label": "Try it out",
                            "scores": {"Visual": 0, "Auditory": 0, "Kinesthetic": 2},
                        },
                    ],
                },
                {
                    "id": "q6",
                    "text": "What's your study preference?",
                    "options": [
                        {
                            "label": "Quiet reading",
                            "scores": {"Visual": 4, "Auditory": 0, "Kinesthetic": 0},
                        },
                        {
                            "label": "Group discussion",
                            "scores": {"Visual": 0, "Auditory": 4, "Kinesthetic": 0},
                        },
                        {
                            "label": "Hands-on practice",
                            "scores": {"Visual": 0, "Auditory": 0, "Kinesthetic": 4},
                        },
                    ],
                },
                {
                    "id": "q7",
                    "text": "How do you prefer feedback?",
                    "options": [
                        {
                            "label": "Written comments",
                            "scores": {"Visual": 3, "Auditory": 0, "Kinesthetic": 0},
                        },
                        {
                            "label": "Verbal feedback",
                            "scores": {"Visual": 0, "Auditory": 3, "Kinesthetic": 0},
                        },
                        {
                            "label": "Demonstration",
                            "scores": {"Visual": 0, "Auditory": 0, "Kinesthetic": 3},
                        },
                    ],
                },
                {
                    "id": "q8",
                    "text": "What's your ideal learning environment?",
                    "options": [
                        {
                            "label": "Library with books",
                            "scores": {"Visual": 5, "Auditory": 0, "Kinesthetic": 0},
                        },
                        {
                            "label": "Audio recordings",
                            "scores": {"Visual": 0, "Auditory": 5, "Kinesthetic": 0},
                        },
                        {
                            "label": "Workshop space",
                            "scores": {"Visual": 0, "Auditory": 0, "Kinesthetic": 5},
                        },
                    ],
                },
            ],
        }

        response = self._make_request("POST", "/api/surveys/", json=survey_data)
        if response.status_code != 200:
            print(f"Survey creation failed: {response.status_code} - {response.text}")
        assert response.status_code == 200
        data = response.json()
        assert data["title"] == survey_data["title"]
        assert data["creator_name"] == "teacher1@example.com"

        # Store for cleanup
        self.test_data["created_survey_id"] = data["id"]
        print("✅ Survey creation test passed")

    def test_sessions(self):
        """Test session endpoints."""
        if not self.test_data.get("course_id") or not self.test_data.get("survey_id"):
            pytest.skip("No course or survey available for session test")

        # Create session
        response = self._make_request(
            "POST",
            f'/api/sessions/{self.test_data["course_id"]}/sessions',
            json={"survey_template_id": self.test_data["survey_id"]},
        )
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert "join_token" in data
        assert "qr_url" in data

        # Store for other tests
        self.test_data["session_id"] = data["session_id"]
        self.test_data["join_token"] = data["join_token"]
        print(f"✅ Session created: {data['session_id']}")

    def test_public_join(self):
        """Test public join endpoint."""
        if not self.test_data.get("join_token"):
            pytest.skip("No join token available")

        response = self._make_request("GET", f'/api/public/join/{self.test_data["join_token"]}')
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert "course_title" in data
        assert data["status"] == "OPEN"
        print("✅ Public join test passed")

    def test_survey_submission(self):
        """Test survey submission."""
        if not self.test_data.get("join_token"):
            pytest.skip("No join token available")

        submission_data = {
            "student_name": "Test Student API",
            "answers": {"q1": "By reading", "q2": "Achievement"},
        }

        response = self._make_request(
            "POST", f'/api/public/join/{self.test_data["join_token"]}/submit', json=submission_data
        )
        assert response.status_code == 200
        data = response.json()
        assert data["ok"] is True
        assert "submission_id" in data

        # Store for cleanup
        self.test_data["submission_id"] = data["submission_id"]
        print("✅ Survey submission test passed")

    def test_get_submissions(self):
        """Test getting session submissions."""
        if not self.test_data.get("session_id"):
            pytest.skip("No session available")

        response = self._make_request(
            "GET", f'/api/sessions/{self.test_data["session_id"]}/submissions'
        )
        assert response.status_code == 200
        data = response.json()
        assert "session_id" in data
        assert "count" in data
        assert "items" in data
        assert data["count"] >= 1

        # Check if submission has total_scores
        if data["items"]:
            item = data["items"][0]
            assert "student_name" in item
            assert "total_scores" in item
            assert isinstance(item["total_scores"], dict)
            print(f"✅ Found submission with scores: {item['total_scores']}")

        print("✅ Get submissions test passed")

    def cleanup_test_data(self):
        """Clean up all test data."""
        print("🧹 Cleaning up test data...")

        # Clean up submissions
        if self.test_data.get("session_id"):
            try:
                # Get all submissions for the session
                response = self._make_request(
                    "GET", f'/api/sessions/{self.test_data["session_id"]}/submissions'
                )
                if response.status_code == 200:
                    data = response.json()
                    for item in data.get("items", []):
                        if item["student_name"].startswith("Test Student"):
                            print(f"  - Found test submission: {item['student_name']}")
            except Exception as e:
                print(f"  - Error checking submissions: {e}")

        # Clean up sessions (this will cascade to submissions)
        if self.test_data.get("session_id"):
            try:
                # Close the session first
                response = self._make_request(
                    "POST", f'/api/sessions/{self.test_data["session_id"]}/close'
                )
                if response.status_code == 200:
                    print(f"  - Closed session: {self.test_data['session_id']}")
            except Exception as e:
                print(f"  - Error closing session: {e}")

        # Clean up created survey
        if self.test_data.get("created_survey_id"):
            try:
                # Note: We can't delete surveys via API, but we can identify them
                print(
                    f"  - Created survey (manual cleanup needed): "
                    f"{self.test_data['created_survey_id']}"
                )
            except Exception as e:
                print(f"  - Error with survey cleanup: {e}")

        print("✅ Test data cleanup completed")


def test_all_endpoints():
    """Run comprehensive test of all endpoints."""
    tester = APITester()

    try:
        # Test all endpoints
        tester.test_health_check()
        tester.test_authentication()
        tester.test_courses()
        tester.test_surveys()
        tester.test_create_survey()
        tester.test_sessions()
        tester.test_public_join()
        tester.test_survey_submission()
        tester.test_get_submissions()

        print("\n🎉 All endpoint tests passed!")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        raise

    finally:
        # Always cleanup
        tester.cleanup_test_data()


def test_individual_endpoints():
    """Test individual endpoint categories."""
    tester = APITester()

    try:
        # Test authentication
        tester.test_authentication()

        # Test courses
        tester.test_courses()

        # Test surveys
        tester.test_surveys()

        # Test survey creation
        tester.test_create_survey()

        # Test sessions
        tester.test_sessions()

        # Test public endpoints
        tester.test_public_join()
        tester.test_survey_submission()

        # Test submissions
        tester.test_get_submissions()

        print("\n🎉 All individual endpoint tests passed!")

    except Exception as e:
        print(f"\n❌ Individual test failed: {e}")
        raise

    finally:
        # Cleanup
        tester.cleanup_test_data()


if __name__ == "__main__":
    # Run tests directly
    test_all_endpoints()

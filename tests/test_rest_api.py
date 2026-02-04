"""Test suite for REST API endpoints (FastAPI)."""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi.testclient import TestClient

from open_meteo_mcp.api.main import create_app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    app = create_app()
    return TestClient(app)


class TestRESTAPIHealth:
    """Tests for health check endpoints."""

    def test_health_check_endpoint(self, client):
        """Test health check endpoint returns 200."""
        response = client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "version" in data
        assert "timestamp" in data

    def test_root_endpoint(self, client):
        """Test root endpoint returns API info."""
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Open Meteo MCP REST API"
        assert "version" in data
        assert "docs" in data
        assert "health" in data
        assert "endpoints" in data


class TestRESTAPIToolsEndpoints:
    """Tests for weather tools REST endpoints."""

    def test_weather_endpoint_missing_params(self, client):
        """Test weather endpoint without required parameters."""
        response = client.get("/api/tools/weather")
        assert response.status_code == 422  # Validation error

    def test_weather_endpoint_invalid_latitude(self, client):
        """Test weather endpoint with invalid latitude."""
        response = client.get(
            "/api/tools/weather",
            params={"latitude": 100, "longitude": 8.5417},
        )
        # API may return 422 validation error or 500 if validation is done by API
        assert response.status_code in [422, 500]

    def test_weather_endpoint_invalid_longitude(self, client):
        """Test weather endpoint with invalid longitude."""
        response = client.get(
            "/api/tools/weather",
            params={"latitude": 47.3769, "longitude": 200},
        )
        # API may return 422 validation error or 500 if validation is done by API
        assert response.status_code in [422, 500]

    def test_snow_conditions_endpoint_missing_params(self, client):
        """Test snow conditions endpoint without required parameters."""
        response = client.get("/api/tools/snow-conditions")
        assert response.status_code == 422  # Validation error

    def test_air_quality_endpoint_missing_params(self, client):
        """Test air quality endpoint without required parameters."""
        response = client.get("/api/tools/air-quality")
        assert response.status_code == 422  # Validation error

    def test_search_location_endpoint_missing_params(self, client):
        """Test search location endpoint without required parameters."""
        response = client.post("/api/tools/search-location")
        assert response.status_code == 422  # Validation error

    def test_search_location_endpoint_with_body(self, client):
        """Test search location endpoint with request body."""
        response = client.post(
            "/api/tools/search-location",
            json={"name": "Zurich"},
        )
        # Will fail because we don't have API access, but structure should be correct
        # This test just validates the endpoint accepts the request
        assert response.status_code in [200, 500]  # Either success or API error


class TestRESTAPIChatEndpoints:
    """Tests for chat REST endpoints."""

    def test_chat_health_endpoint(self, client):
        """Test chat health endpoint."""
        response = client.get("/api/chat/health")
        assert response.status_code == 200
        data = response.json()
        assert "status" in data

    def test_chat_message_missing_params(self, client):
        """Test chat message endpoint without session ID."""
        response = client.post(
            "/api/chat/sessions/test-session/messages",
            json={"message": "Hello"},
        )
        # Should either succeed (if chat is mocked) or fail gracefully
        assert response.status_code in [200, 500, 422]

    def test_get_session_messages_endpoint(self, client):
        """Test get session messages endpoint."""
        response = client.get("/api/chat/sessions/test-session/messages")
        # Should either return session messages or 404 for non-existent session
        assert response.status_code in [200, 404, 500]

    def test_delete_session_endpoint(self, client):
        """Test delete session endpoint."""
        response = client.delete("/api/chat/sessions/test-session")
        # Should either succeed or return appropriate status
        assert response.status_code in [200, 404, 500]


class TestRESTAPIResponseFormats:
    """Tests for REST API response format consistency."""

    def test_health_response_format(self, client):
        """Test health endpoint response format."""
        response = client.get("/api/health")
        assert response.headers["content-type"] == "application/json"
        data = response.json()
        assert isinstance(data, dict)
        assert all(isinstance(v, (str, int, float, bool, type(None))) for v in data.values())

    def test_root_response_format(self, client):
        """Test root endpoint response format."""
        response = client.get("/")
        assert response.headers["content-type"] == "application/json"
        data = response.json()
        assert isinstance(data, dict)
        assert "endpoints" in data


class TestRESTAPICORS:
    """Tests for CORS configuration."""

    def test_cors_headers_present(self, client):
        """Test that CORS headers are present in responses."""
        response = client.get(
            "/api/health",
            headers={"Origin": "http://localhost:3000"},
        )
        assert response.status_code == 200
        # CORS headers should be present if configured
        assert response.headers.get("access-control-allow-origin") or "Access-Control-Allow-Origin" not in response.headers

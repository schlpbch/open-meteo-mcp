"""Integration tests for core functionality and message flows."""

import asyncio
from unittest.mock import AsyncMock, MagicMock

import pytest

from open_meteo_mcp.chat.handler import ChatHandler
from open_meteo_mcp.chat.sessions import ConversationSession, SessionManager
from open_meteo_mcp.client import OpenMeteoClient
from open_meteo_mcp.services import AirQualityService, LocationService, WeatherService


class TestChatSessions:
    """Tests for chat session management."""

    def test_session_manager_create_session(self):
        """Test creating a new session."""
        manager = SessionManager()
        session_id = manager.create_session()
        assert session_id is not None
        assert manager.session_exists(session_id)

    def test_session_manager_create_with_custom_id(self):
        """Test creating session with custom ID."""
        manager = SessionManager()
        custom_id = "my-custom-session"
        session_id = manager.create_session(custom_id)
        assert session_id == custom_id
        assert manager.session_exists(custom_id)

    def test_session_manager_delete_session(self):
        """Test deleting a session."""
        manager = SessionManager()
        session_id = manager.create_session()
        assert manager.session_exists(session_id)
        result = manager.delete_session(session_id)
        assert result is True
        assert not manager.session_exists(session_id)

    def test_session_manager_delete_nonexistent(self):
        """Test deleting non-existent session."""
        manager = SessionManager()
        result = manager.delete_session("nonexistent")
        assert result is False

    def test_conversation_session_add_message(self):
        """Test adding messages to conversation."""
        session = ConversationSession("test-id")
        session.add_message("user", "Hello")
        messages = session.get_messages()
        assert len(messages) > 0
        assert any(m.get("role") == "user" for m in messages)

    def test_conversation_session_get_info(self):
        """Test getting session info."""
        manager = SessionManager()
        session_id = manager.create_session()
        info = manager.get_session_info(session_id)
        assert info is not None
        assert "created_at" in info or "id" in info


class TestServiceEnrichment:
    """Tests for service layer enrichment functionality."""

    @pytest.mark.asyncio
    async def test_weather_service_enrichment_returns_dict(self):
        """Test that weather service returns enriched dict."""
        mock_client = AsyncMock(spec=OpenMeteoClient)
        mock_response = MagicMock()
        mock_response.model_dump.return_value = {
            "current_weather": {"temperature": 15.0},
            "daily": {"temperature_2m_max": [20.0]},
        }
        mock_client.get_weather.return_value = mock_response

        service = WeatherService(mock_client)
        result = await service.get_weather_enriched(47.0, 8.0)

        assert isinstance(result, dict)
        assert result is not None

    @pytest.mark.asyncio
    async def test_location_service_enrichment_adds_features(self):
        """Test that location service adds enrichment fields."""
        mock_client = AsyncMock(spec=OpenMeteoClient)
        mock_response = MagicMock()
        mock_response.model_dump.return_value = {
            "results": [{"name": "Zurich", "elevation": 408, "feature_code": "PPLA"}]
        }
        mock_client.search_location.return_value = mock_response

        service = LocationService(mock_client)
        result = await service.search_location_enriched("Zurich")

        assert result is not None
        assert "results" in result

    @pytest.mark.asyncio
    async def test_air_quality_service_enrichment(self):
        """Test air quality enrichment."""
        mock_client = AsyncMock(spec=OpenMeteoClient)
        mock_response = MagicMock()
        mock_response.model_dump.return_value = {
            "current": {"european_aqi": 35},
            "latitude": 47.0,
            "longitude": 8.0,
            "timezone": "Europe/Zurich",
        }
        mock_client.get_air_quality.return_value = mock_response

        service = AirQualityService(mock_client)
        result = await service.get_air_quality_enriched(47.0, 8.0)

        assert result is not None


class TestChatHandlerBasics:
    """Tests for ChatHandler basic functionality."""

    @pytest.mark.asyncio
    async def test_chat_handler_initialization(self):
        """Test ChatHandler initializes with required attributes."""
        handler = ChatHandler()
        assert handler.client is not None
        assert handler.session_manager is not None
        assert handler.model is not None

    @pytest.mark.asyncio
    async def test_chat_handler_create_session(self):
        """Test that ChatHandler can create sessions."""
        handler = ChatHandler()
        session_id = handler.create_session("test-123")
        assert session_id == "test-123"
        assert handler.get_session_info("test-123") is not None

    def test_chat_handler_delete_session(self):
        """Test that ChatHandler can delete sessions."""
        handler = ChatHandler()
        session_id = handler.create_session()
        result = handler.delete_session(session_id)
        assert result is True

    def test_chat_handler_get_nonexistent_session_info(self):
        """Test getting info for non-existent session."""
        handler = ChatHandler()
        info = handler.get_session_info("nonexistent")
        assert info is None


class TestParallelProcessing:
    """Tests for parallel processing capabilities."""

    @pytest.mark.asyncio
    async def test_multiple_services_parallel(self):
        """Test that services can run in parallel."""
        mock_client = AsyncMock(spec=OpenMeteoClient)

        # Setup mocks
        weather_response = MagicMock()
        weather_response.model_dump.return_value = {"current_weather": {}}
        mock_client.get_weather.return_value = weather_response

        aq_response = MagicMock()
        aq_response.model_dump.return_value = {"current": {}}
        mock_client.get_air_quality.return_value = aq_response

        location_response = MagicMock()
        location_response.model_dump.return_value = {"results": []}
        mock_client.search_location.return_value = location_response

        services = [
            WeatherService(mock_client),
            AirQualityService(mock_client),
            LocationService(mock_client),
        ]

        # Execute all in parallel
        tasks = [
            services[0].get_weather_enriched(47.0, 8.0),
            services[1].get_air_quality_enriched(47.0, 8.0),
            services[2].search_location_enriched("Zurich"),
        ]

        results = await asyncio.gather(*tasks)

        assert len(results) == 3
        assert all(r is not None for r in results)
        assert mock_client.get_weather.called
        assert mock_client.get_air_quality.called
        assert mock_client.search_location.called


class TestSessionManagementIntegration:
    """Tests for session management integration."""

    def test_session_manager_multiple_sessions(self):
        """Test managing multiple sessions."""
        manager = SessionManager()

        # Create multiple sessions
        ids = [manager.create_session() for _ in range(3)]
        assert len(ids) == 3
        assert all(manager.session_exists(id) for id in ids)

        # Delete one
        manager.delete_session(ids[0])
        assert not manager.session_exists(ids[0])
        assert manager.session_exists(ids[1])
        assert manager.session_exists(ids[2])

    def test_conversation_session_message_history(self):
        """Test conversation maintains message history."""
        session = ConversationSession("test")

        # Add multiple messages
        session.add_message("user", "First message")
        session.add_message("assistant", "First response")
        session.add_message("user", "Second message")

        messages = session.get_messages()
        assert len(messages) >= 3
        roles = [m.get("role") for m in messages]
        assert "user" in roles
        assert "assistant" in roles


class TestErrorHandlingPaths:
    """Tests for error handling in key paths."""

    @pytest.mark.asyncio
    async def test_weather_service_handles_client_error(self):
        """Test weather service propagates client errors."""
        mock_client = AsyncMock(spec=OpenMeteoClient)
        mock_client.get_weather.side_effect = Exception("API error")

        service = WeatherService(mock_client)
        with pytest.raises(Exception):  # noqa: B017
            await service.get_weather_enriched(47.0, 8.0)

    @pytest.mark.asyncio
    async def test_location_service_handles_client_error(self):
        """Test location service propagates client errors."""
        mock_client = AsyncMock(spec=OpenMeteoClient)
        mock_client.search_location.side_effect = ValueError("Invalid input")

        service = LocationService(mock_client)
        with pytest.raises(ValueError):
            await service.search_location_enriched("test")

    def test_session_manager_handles_missing_sessions(self):
        """Test session manager handles missing sessions gracefully."""
        manager = SessionManager()
        info = manager.get_session_info("nonexistent")
        assert info is None

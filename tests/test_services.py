"""Test suite for service layer (WeatherService, AirQualityService, LocationService)."""

import asyncio
import pytest
from unittest.mock import AsyncMock, MagicMock

from open_meteo_mcp.services import (
    WeatherService,
    AirQualityService,
    LocationService,
)
from open_meteo_mcp.client import OpenMeteoClient


class TestWeatherServiceEnrichment:
    """Tests for WeatherService enrichment logic."""

    @pytest.mark.asyncio
    async def test_weather_service_initialization(self):
        """Test WeatherService initialization."""
        mock_client = AsyncMock(spec=OpenMeteoClient)
        service = WeatherService(mock_client)
        assert service.client == mock_client

    @pytest.mark.asyncio
    async def test_weather_service_calls_client(self):
        """Test that service calls client with correct parameters."""
        mock_client = AsyncMock(spec=OpenMeteoClient)
        service = WeatherService(mock_client)

        # Mock return value with model_dump method
        mock_response = MagicMock()
        mock_response.model_dump.return_value = {"current_weather": {}}
        mock_client.get_weather.return_value = mock_response

        await service.get_weather_enriched(
            latitude=47.0,
            longitude=8.0,
            forecast_days=7,
            include_hourly=True,
            timezone="Europe/Zurich",
        )

        # Verify client was called with correct parameters
        mock_client.get_weather.assert_called_once_with(
            latitude=47.0,
            longitude=8.0,
            forecast_days=7,
            include_hourly=True,
            timezone="Europe/Zurich",
        )

    @pytest.mark.asyncio
    async def test_snow_conditions_enrichment(self):
        """Test snow conditions enrichment."""
        mock_client = AsyncMock(spec=OpenMeteoClient)
        service = WeatherService(mock_client)

        # Mock get_snow_conditions response
        mock_snow_response = MagicMock()
        mock_snow_response.model_dump.return_value = {"current": {}}
        mock_client.get_snow_conditions.return_value = mock_snow_response

        # Mock get_weather response
        mock_weather_response = MagicMock()
        mock_weather_response.model_dump.return_value = {"current_weather": {}}
        mock_client.get_weather.return_value = mock_weather_response

        await service.get_snow_conditions_enriched(
            latitude=46.0,
            longitude=8.5,
            forecast_days=7,
        )

        # Verify both client methods were called
        mock_client.get_snow_conditions.assert_called_once()
        mock_client.get_weather.assert_called_once()


class TestAirQualityServiceEnrichment:
    """Tests for AirQualityService enrichment logic."""

    @pytest.mark.asyncio
    async def test_air_quality_service_initialization(self):
        """Test AirQualityService initialization."""
        mock_client = AsyncMock(spec=OpenMeteoClient)
        service = AirQualityService(mock_client)
        assert service.client == mock_client

    @pytest.mark.asyncio
    async def test_air_quality_service_calls_client(self):
        """Test that service calls client with correct parameters."""
        mock_client = AsyncMock(spec=OpenMeteoClient)
        service = AirQualityService(mock_client)

        # Mock return value with model_dump method
        mock_response = MagicMock()
        mock_response.model_dump.return_value = {"current": {}}
        mock_client.get_air_quality.return_value = mock_response

        await service.get_air_quality_enriched(
            latitude=47.0,
            longitude=8.0,
            forecast_days=5,
            include_pollen=True,
            timezone="auto",
        )

        # Verify client was called
        mock_client.get_air_quality.assert_called_once()


class TestLocationServiceEnrichment:
    """Tests for LocationService enrichment logic."""

    @pytest.mark.asyncio
    async def test_location_service_initialization(self):
        """Test LocationService initialization."""
        mock_client = AsyncMock(spec=OpenMeteoClient)
        service = LocationService(mock_client)
        assert service.client == mock_client

    @pytest.mark.asyncio
    async def test_location_service_calls_client(self):
        """Test that service calls client with correct parameters."""
        mock_client = AsyncMock(spec=OpenMeteoClient)
        service = LocationService(mock_client)

        # Mock return value with proper structure and model_dump method
        mock_response = MagicMock()
        mock_response.model_dump.return_value = {"results": []}
        mock_client.search_location.return_value = mock_response

        await service.search_location_enriched(
            name="Zurich",
            count=10,
            language="en",
        )

        # Verify client was called
        mock_client.search_location.assert_called_once()

    @pytest.mark.asyncio
    async def test_swiss_location_filtering(self):
        """Test Swiss location filtering."""
        mock_client = AsyncMock(spec=OpenMeteoClient)
        service = LocationService(mock_client)

        # Mock return value with proper structure and model_dump method
        mock_response = MagicMock()
        mock_response.model_dump.return_value = {"results": []}
        mock_client.search_location.return_value = mock_response

        await service.search_location_swiss_enriched(
            name="Zurich",
            include_features=False,
            language="en",
            count=10,
        )

        # Verify client was called
        mock_client.search_location.assert_called_once()


class TestServiceErrorHandling:
    """Tests for service error handling."""

    @pytest.mark.asyncio
    async def test_weather_service_error_propagation(self):
        """Test that weather service propagates client errors."""
        mock_client = AsyncMock(spec=OpenMeteoClient)
        mock_client.get_weather.side_effect = Exception("API error")
        service = WeatherService(mock_client)

        with pytest.raises(Exception, match="API error"):
            await service.get_weather_enriched(latitude=47.0, longitude=8.0)

    @pytest.mark.asyncio
    async def test_air_quality_service_error_propagation(self):
        """Test that air quality service propagates client errors."""
        mock_client = AsyncMock(spec=OpenMeteoClient)
        mock_client.get_air_quality.side_effect = Exception("API error")
        service = AirQualityService(mock_client)

        with pytest.raises(Exception, match="API error"):
            await service.get_air_quality_enriched(latitude=47.0, longitude=8.0)

    @pytest.mark.asyncio
    async def test_location_service_error_propagation(self):
        """Test that location service propagates client errors."""
        mock_client = AsyncMock(spec=OpenMeteoClient)
        mock_client.search_location.side_effect = Exception("API error")
        service = LocationService(mock_client)

        with pytest.raises(Exception, match="API error"):
            await service.search_location_enriched(name="Zurich")


class TestServiceIntegration:
    """Integration tests for services working together."""

    @pytest.mark.asyncio
    async def test_services_parallel_execution(self):
        """Test that services can be executed in parallel."""
        mock_client = AsyncMock(spec=OpenMeteoClient)

        # Setup mocks with model_dump methods
        weather_response = MagicMock()
        weather_response.model_dump.return_value = {"current_weather": {}}
        mock_client.get_weather.return_value = weather_response

        aq_response = MagicMock()
        aq_response.model_dump.return_value = {"current": {}}
        mock_client.get_air_quality.return_value = aq_response

        location_response = MagicMock()
        location_response.model_dump.return_value = {"results": []}
        mock_client.search_location.return_value = location_response

        # Create services
        weather_service = WeatherService(mock_client)
        air_quality_service = AirQualityService(mock_client)
        location_service = LocationService(mock_client)

        # Execute parallel calls
        results = await asyncio.gather(
            weather_service.get_weather_enriched(47.0, 8.0),
            air_quality_service.get_air_quality_enriched(47.0, 8.0),
            location_service.search_location_enriched("Zurich"),
        )

        assert len(results) == 3
        mock_client.get_weather.assert_called_once()
        mock_client.get_air_quality.assert_called_once()
        mock_client.search_location.assert_called_once()

    @pytest.mark.asyncio
    async def test_services_with_custom_parameters(self):
        """Test services accept custom parameters."""
        mock_client = AsyncMock(spec=OpenMeteoClient)

        # Mock return value with model_dump method
        mock_response = MagicMock()
        mock_response.model_dump.return_value = {"current_weather": {}}
        mock_client.get_weather.return_value = mock_response

        service = WeatherService(mock_client)
        await service.get_weather_enriched(
            latitude=46.0,
            longitude=7.5,
            forecast_days=14,
            include_hourly=False,
            timezone="America/New_York",
        )

        # Verify custom parameters were passed
        call_kwargs = mock_client.get_weather.call_args[1]
        assert call_kwargs["latitude"] == 46.0
        assert call_kwargs["longitude"] == 7.5
        assert call_kwargs["forecast_days"] == 14
        assert call_kwargs["include_hourly"] is False
        assert call_kwargs["timezone"] == "America/New_York"

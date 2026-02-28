"""Shared pytest fixtures for test suite."""

from typing import Any
from unittest.mock import AsyncMock

import pytest

from open_meteo_mcp.client import OpenMeteoClient
from open_meteo_mcp.services import (
    AirQualityService,
    LocationService,
    WeatherService,
)

# ==================== Client Fixtures ====================


@pytest.fixture
def mock_client() -> AsyncMock:
    """Create a mock OpenMeteoClient for testing."""
    return AsyncMock(spec=OpenMeteoClient)


# ==================== Service Fixtures ====================


@pytest.fixture
def weather_service(mock_client: AsyncMock) -> WeatherService:
    """Create a WeatherService with mock client."""
    return WeatherService(mock_client)


@pytest.fixture
def air_quality_service(mock_client: AsyncMock) -> AirQualityService:
    """Create an AirQualityService with mock client."""
    return AirQualityService(mock_client)


@pytest.fixture
def location_service(mock_client: AsyncMock) -> LocationService:
    """Create a LocationService with mock client."""
    return LocationService(mock_client)


# ==================== Response Fixtures ====================


@pytest.fixture
def base_weather_response() -> dict[str, Any]:
    """Create a base weather API response structure."""
    return {
        "latitude": 46.9479,
        "longitude": 7.4474,
        "timezone": "Europe/Zurich",
        "current_weather": {
            "temperature": 15.0,
            "wind_speed": 10.0,
            "wind_direction": 270,
            "weather_code": 0,
        },
        "daily": {
            "time": ["2025-01-01"],
            "weather_code": [1],
            "temperature_2m_max": [20.0],
            "temperature_2m_min": [10.0],
            "precipitation_sum": [0.0],
        },
        "hourly": {
            "time": ["2025-01-01T00:00"],
            "temperature_2m": [15.0],
            "relative_humidity_2m": [80],
            "precipitation": [0.0],
            "weather_code": [0],
        },
    }


@pytest.fixture
def base_snow_response() -> dict[str, Any]:
    """Create a base snow conditions API response structure."""
    return {
        "latitude": 46.0,
        "longitude": 8.0,
        "timezone": "Europe/Zurich",
        "daily": {
            "time": ["2025-01-01"],
            "snowfall_sum": [10.0],
            "snow_depth_max": [50.0],
        },
        "hourly": {
            "time": ["2025-01-01T00:00"],
            "snowfall": [0.5],
            "snow_depth": [50.0],
        },
    }


@pytest.fixture
def base_air_quality_response() -> dict[str, Any]:
    """Create a base air quality API response structure."""
    return {
        "latitude": 46.9479,
        "longitude": 7.4474,
        "timezone": "Europe/Zurich",
        "hourly": {
            "time": ["2025-01-01T00:00"],
            "european_aqi": [25],
            "us_aqi": [30],
            "pm10": [15.0],
            "pm2_5": [8.0],
            "o3": [50.0],
            "no2": [15.0],
        },
    }


@pytest.fixture
def base_location_response() -> dict[str, Any]:
    """Create a base location search API response structure."""
    return {
        "results": [
            {
                "id": 2661604,
                "name": "Bern",
                "latitude": 46.9479,
                "longitude": 7.4474,
                "elevation": 540,
                "feature_code": "PPLA",
                "country_code": "CH",
                "timezone": "Europe/Zurich",
            }
        ]
    }

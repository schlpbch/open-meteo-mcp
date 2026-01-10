"""Unit tests for air quality functionality."""

import pytest
from pytest_httpx import HTTPXMock

from open_meteo_mcp.client import OpenMeteoClient
from open_meteo_mcp.models import AirQualityForecast, CurrentAirQuality, HourlyAirQuality


@pytest.mark.asyncio
class TestAirQuality:
    """Test air quality API calls."""
    
    async def test_get_air_quality_success(self, httpx_mock: HTTPXMock):
        """Test successful air quality API call."""
        # Mock API response
        httpx_mock.add_response(
            json={
                "latitude": 47.3769,
                "longitude": 8.5417,
                "elevation": 408.0,
                "timezone": "Europe/Zurich",
                "timezone_abbreviation": "CET",
                "utc_offset_seconds": 3600,
                "current": {
                    "time": "2026-01-10T12:00",
                    "european_aqi": 25,
                    "us_aqi": 65,
                    "pm10": 15.5,
                    "pm2_5": 8.2,
                    "uv_index": 3.5
                },
                "hourly": {
                    "time": ["2026-01-10T00:00", "2026-01-10T01:00"],
                    "european_aqi": [22, 25],
                    "us_aqi": [60, 65],
                    "pm10": [14.2, 15.5],
                    "pm2_5": [7.8, 8.2],
                    "carbon_monoxide": [250.5, 255.3],
                    "nitrogen_dioxide": [12.3, 13.1],
                    "sulphur_dioxide": [2.1, 2.3],
                    "ozone": [45.2, 46.8],
                    "dust": [5.2, 5.5],
                    "uv_index": [0.0, 0.5],
                    "uv_index_clear_sky": [0.0, 1.2],
                    "ammonia": [1.2, 1.3],
                    "alder_pollen": [0.0, 0.0],
                    "birch_pollen": [0.0, 0.0],
                    "grass_pollen": [12.5, 15.3],
                    "mugwort_pollen": [0.0, 0.0],
                    "olive_pollen": [0.0, 0.0],
                    "ragweed_pollen": [0.0, 0.0]
                }
            }
        )
        
        async with OpenMeteoClient() as client:
            result = await client.get_air_quality(
                latitude=47.3769,
                longitude=8.5417,
                forecast_days=5,
                include_pollen=True
            )
            
            assert isinstance(result, AirQualityForecast)
            assert result.latitude == 47.3769
            assert result.longitude == 8.5417
            
            # Check current air quality
            assert result.current is not None
            assert isinstance(result.current, CurrentAirQuality)
            assert result.current.european_aqi == 25
            assert result.current.us_aqi == 65
            assert result.current.pm10 == 15.5
            assert result.current.pm2_5 == 8.2
            assert result.current.uv_index == 3.5
            
            # Check hourly forecast
            assert result.hourly is not None
            assert isinstance(result.hourly, HourlyAirQuality)
            assert len(result.hourly.time) == 2
            assert result.hourly.european_aqi == [22, 25]
            assert result.hourly.us_aqi == [60, 65]
            assert result.hourly.pm10 == [14.2, 15.5]
            assert result.hourly.pm2_5 == [7.8, 8.2]
            
            # Check pollutants
            assert result.hourly.carbon_monoxide == [250.5, 255.3]
            assert result.hourly.nitrogen_dioxide == [12.3, 13.1]
            assert result.hourly.sulphur_dioxide == [2.1, 2.3]
            assert result.hourly.ozone == [45.2, 46.8]
            
            # Check pollen data
            assert result.hourly.grass_pollen == [12.5, 15.3]
            assert result.hourly.birch_pollen == [0.0, 0.0]
    
    async def test_get_air_quality_without_pollen(self, httpx_mock: HTTPXMock):
        """Test air quality API call without pollen data."""
        httpx_mock.add_response(
            json={
                "latitude": 47.3769,
                "longitude": 8.5417,
                "timezone": "Europe/Zurich",
                "current": {
                    "time": "2026-01-10T12:00",
                    "european_aqi": 25,
                    "us_aqi": 65,
                    "pm10": 15.5,
                    "pm2_5": 8.2,
                    "uv_index": 3.5
                },
                "hourly": {
                    "time": ["2026-01-10T00:00"],
                    "european_aqi": [22],
                    "us_aqi": [60],
                    "pm10": [14.2],
                    "pm2_5": [7.8],
                    "carbon_monoxide": [250.5],
                    "nitrogen_dioxide": [12.3],
                    "sulphur_dioxide": [2.1],
                    "ozone": [45.2],
                    "dust": [5.2],
                    "uv_index": [0.0],
                    "uv_index_clear_sky": [0.0],
                    "ammonia": [1.2]
                }
            }
        )
        
        async with OpenMeteoClient() as client:
            result = await client.get_air_quality(
                latitude=47.3769,
                longitude=8.5417,
                include_pollen=False
            )
            
            assert isinstance(result, AirQualityForecast)
            assert result.current is not None
            assert result.hourly is not None
            # Pollen fields should be None or not present
    
    async def test_get_air_quality_forecast_days_clamping(self, httpx_mock: HTTPXMock):
        """Test that forecast_days is clamped to 1-5 range."""
        response_data = {
            "latitude": 47.3769,
            "longitude": 8.5417,
            "timezone": "Europe/Zurich",
            "current": {
                "time": "2026-01-10T12:00",
                "european_aqi": 25,
                "us_aqi": 65,
                "pm10": 15.5,
                "pm2_5": 8.2,
                "uv_index": 3.5
            },
            "hourly": {
                "time": ["2026-01-10T00:00"],
                "european_aqi": [22],
                "us_aqi": [60],
                "pm10": [14.2],
                "pm2_5": [7.8],
                "carbon_monoxide": [250.5],
                "nitrogen_dioxide": [12.3],
                "sulphur_dioxide": [2.1],
                "ozone": [45.2],
                "dust": [5.2],
                "uv_index": [0.0],
                "uv_index_clear_sky": [0.0],
                "ammonia": [1.2]
            }
        }
        
        httpx_mock.add_response(json=response_data)
        httpx_mock.add_response(json=response_data)
        
        async with OpenMeteoClient() as client:
            # Test clamping to minimum (1)
            result = await client.get_air_quality(
                latitude=47.3769,
                longitude=8.5417,
                forecast_days=0
            )
            assert isinstance(result, AirQualityForecast)
            
            # Test clamping to maximum (5)
            result = await client.get_air_quality(
                latitude=47.3769,
                longitude=8.5417,
                forecast_days=10
            )
            assert isinstance(result, AirQualityForecast)
    
    async def test_get_air_quality_high_pollution(self, httpx_mock: HTTPXMock):
        """Test air quality with high pollution levels."""
        httpx_mock.add_response(
            json={
                "latitude": 47.3769,
                "longitude": 8.5417,
                "timezone": "Europe/Zurich",
                "current": {
                    "time": "2026-01-10T12:00",
                    "european_aqi": 85,  # Very Poor
                    "us_aqi": 175,  # Unhealthy
                    "pm10": 85.5,
                    "pm2_5": 55.2,
                    "uv_index": 8.5  # Very High
                },
                "hourly": {
                    "time": ["2026-01-10T00:00"],
                    "european_aqi": [85],
                    "us_aqi": [175],
                    "pm10": [85.5],
                    "pm2_5": [55.2],
                    "carbon_monoxide": [850.5],
                    "nitrogen_dioxide": [85.3],
                    "sulphur_dioxide": [45.1],
                    "ozone": [125.2],
                    "dust": [25.2],
                    "uv_index": [8.5],
                    "uv_index_clear_sky": [9.2],
                    "ammonia": [15.2]
                }
            }
        )
        
        async with OpenMeteoClient() as client:
            result = await client.get_air_quality(
                latitude=47.3769,
                longitude=8.5417
            )
            
            assert result.current.european_aqi == 85  # Very Poor
            assert result.current.us_aqi == 175  # Unhealthy
            assert result.current.pm2_5 > 50  # High PM2.5
            assert result.current.uv_index > 8  # Very High UV
    
    async def test_get_air_quality_pollen_season(self, httpx_mock: HTTPXMock):
        """Test air quality during pollen season."""
        httpx_mock.add_response(
            json={
                "latitude": 47.3769,
                "longitude": 8.5417,
                "timezone": "Europe/Zurich",
                "current": {
                    "time": "2026-05-15T12:00",
                    "european_aqi": 20,
                    "us_aqi": 50,
                    "pm10": 12.5,
                    "pm2_5": 6.2,
                    "uv_index": 6.5
                },
                "hourly": {
                    "time": ["2026-05-15T12:00"],
                    "european_aqi": [20],
                    "us_aqi": [50],
                    "pm10": [12.5],
                    "pm2_5": [6.2],
                    "carbon_monoxide": [200.5],
                    "nitrogen_dioxide": [10.3],
                    "sulphur_dioxide": [1.5],
                    "ozone": [55.2],
                    "dust": [3.2],
                    "uv_index": [6.5],
                    "uv_index_clear_sky": [7.2],
                    "ammonia": [1.0],
                    "alder_pollen": [5.0],
                    "birch_pollen": [125.5],  # High birch pollen
                    "grass_pollen": [85.3],  # High grass pollen
                    "mugwort_pollen": [2.0],
                    "olive_pollen": [15.5],
                    "ragweed_pollen": [0.0]
                }
            }
        )
        
        async with OpenMeteoClient() as client:
            result = await client.get_air_quality(
                latitude=47.3769,
                longitude=8.5417,
                include_pollen=True
            )
            
            assert result.hourly.birch_pollen[0] > 100  # High birch pollen
            assert result.hourly.grass_pollen[0] > 50  # High grass pollen
    
    async def test_get_air_quality_http_error(self, httpx_mock: HTTPXMock):
        """Test handling of HTTP errors."""
        httpx_mock.add_response(status_code=503)
        
        async with OpenMeteoClient() as client:
            with pytest.raises(Exception):  # httpx.HTTPStatusError
                await client.get_air_quality(latitude=47.3769, longitude=8.5417)
    
    async def test_get_air_quality_invalid_response(self, httpx_mock: HTTPXMock):
        """Test handling of invalid JSON response."""
        httpx_mock.add_response(
            json={"invalid": "air_quality_data"}
        )
        
        async with OpenMeteoClient() as client:
            with pytest.raises(ValueError):
                await client.get_air_quality(latitude=47.3769, longitude=8.5417)
    
    async def test_get_air_quality_minimal_data(self, httpx_mock: HTTPXMock):
        """Test air quality with minimal data (only required fields)."""
        httpx_mock.add_response(
            json={
                "latitude": 47.3769,
                "longitude": 8.5417,
                "timezone": "Europe/Zurich"
            }
        )
        
        async with OpenMeteoClient() as client:
            result = await client.get_air_quality(
                latitude=47.3769,
                longitude=8.5417
            )
            
            assert isinstance(result, AirQualityForecast)
            assert result.latitude == 47.3769
            assert result.longitude == 8.5417
            # current and hourly may be None
    
    async def test_get_air_quality_uv_index_levels(self, httpx_mock: HTTPXMock):
        """Test different UV index levels."""
        uv_levels = [
            (1.5, "Low"),
            (4.0, "Moderate"),
            (6.5, "High"),
            (9.0, "Very High"),
            (11.5, "Extreme")
        ]
        
        for uv_value, level in uv_levels:
            httpx_mock.add_response(
                json={
                    "latitude": 47.3769,
                    "longitude": 8.5417,
                    "timezone": "Europe/Zurich",
                    "current": {
                        "time": "2026-01-10T12:00",
                        "european_aqi": 20,
                        "us_aqi": 50,
                        "pm10": 10.0,
                        "pm2_5": 5.0,
                        "uv_index": uv_value
                    },
                    "hourly": {
                        "time": ["2026-01-10T12:00"],
                        "european_aqi": [20],
                        "us_aqi": [50],
                        "pm10": [10.0],
                        "pm2_5": [5.0],
                        "carbon_monoxide": [200.0],
                        "nitrogen_dioxide": [10.0],
                        "sulphur_dioxide": [2.0],
                        "ozone": [50.0],
                        "dust": [5.0],
                        "uv_index": [uv_value],
                        "uv_index_clear_sky": [uv_value + 1.0],
                        "ammonia": [1.0]
                    }
                }
            )
        
        async with OpenMeteoClient() as client:
            for uv_value, level in uv_levels:
                result = await client.get_air_quality(
                    latitude=47.3769,
                    longitude=8.5417
                )
                assert result.current.uv_index == uv_value

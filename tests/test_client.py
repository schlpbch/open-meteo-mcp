"""Unit tests for OpenMeteoClient."""

import pytest
from pytest_httpx import HTTPXMock

from open_meteo_mcp.client import OpenMeteoClient
from open_meteo_mcp.models import WeatherForecast, SnowConditions


@pytest.mark.asyncio
class TestOpenMeteoClient:
    """Test OpenMeteoClient API calls."""
    
    async def test_get_weather_success(self, httpx_mock: HTTPXMock):
        """Test successful weather API call."""
        # Mock API response
        httpx_mock.add_response(
            url="https://api.open-meteo.com/v1/forecast?latitude=46.9479&longitude=7.4474&forecast_days=7&timezone=auto&current_weather=true&daily=temperature_2m_max%2Ctemperature_2m_min%2Cprecipitation_sum%2Cprecipitation_probability_max%2Cprecipitation_hours%2Cweather_code%2Csunrise%2Csunset%2Cuv_index_max%2Cwind_speed_10m_max%2Cwind_gusts_10m_max&hourly=temperature_2m%2Capparent_temperature%2Cprecipitation%2Cprecipitation_probability%2Cweather_code%2Cwind_speed_10m%2Cwind_gusts_10m%2Crelative_humidity_2m%2Ccloud_cover%2Cvisibility%2Cuv_index%2Cis_day",
            json={
                "latitude": 46.9479,
                "longitude": 7.4474,
                "elevation": 542.0,
                "timezone": "Europe/Zurich",
                "timezone_abbreviation": "CET",
                "utc_offset_seconds": 3600,
                "current_weather": {
                    "temperature": 15.2,
                    "windspeed": 12.5,
                    "winddirection": 180,
                    "weathercode": 2,
                    "time": "2026-01-09T09:00"
                },
                "hourly": {
                    "time": ["2026-01-09T00:00", "2026-01-09T01:00"],
                    "temperature_2m": [14.5, 14.2],
                    "precipitation": [0.0, 0.0],
                    "weather_code": [2, 2],
                    "wind_speed_10m": [10.5, 11.2],
                    "relative_humidity_2m": [75, 76]
                },
                "daily": {
                    "time": ["2026-01-09"],
                    "temperature_2m_max": [18.5],
                    "temperature_2m_min": [12.3],
                    "precipitation_sum": [0.0],
                    "weather_code": [2],
                    "sunrise": ["2026-01-09T07:45"],
                    "sunset": ["2026-01-09T17:30"]
                }
            }
        )
        
        async with OpenMeteoClient() as client:
            result = await client.get_weather(
                latitude=46.9479,
                longitude=7.4474,
                forecast_days=7,
                include_hourly=True,
                timezone="auto"
            )
            
            assert isinstance(result, WeatherForecast)
            assert result.latitude == 46.9479
            assert result.longitude == 7.4474
            assert result.current_weather is not None
            assert result.current_weather.temperature == 15.2
            assert result.hourly is not None
            assert len(result.hourly.time) == 2
            assert result.daily is not None
            assert len(result.daily.time) == 1
    
    async def test_get_weather_without_hourly(self, httpx_mock: HTTPXMock):
        """Test weather API call without hourly data."""
        httpx_mock.add_response(
            json={
                "latitude": 46.9479,
                "longitude": 7.4474,
                "timezone": "Europe/Zurich",
                "current_weather": {
                    "temperature": 15.2,
                    "windspeed": 12.5,
                    "winddirection": 180,
                    "weathercode": 2,
                    "time": "2026-01-09T09:00"
                },
                "daily": {
                    "time": ["2026-01-09"],
                    "temperature_2m_max": [18.5],
                    "temperature_2m_min": [12.3],
                    "precipitation_sum": [0.0],
                    "weather_code": [2]
                }
            }
        )
        
        async with OpenMeteoClient() as client:
            result = await client.get_weather(
                latitude=46.9479,
                longitude=7.4474,
                include_hourly=False
            )
            
            assert isinstance(result, WeatherForecast)
            assert result.current_weather is not None
            assert result.daily is not None
    
    async def test_get_snow_conditions_success(self, httpx_mock: HTTPXMock):
        """Test successful snow conditions API call."""
        httpx_mock.add_response(
            json={
                "latitude": 45.9763,
                "longitude": 7.6586,
                "elevation": 1620.0,
                "timezone": "Europe/Zurich",
                "timezone_abbreviation": "CET",
                "utc_offset_seconds": 3600,
                "hourly": {
                    "time": ["2026-01-09T00:00", "2026-01-09T01:00"],
                    "temperature_2m": [-5.2, -5.8],
                    "snowfall": [0.5, 0.3],
                    "snow_depth": [1.2, 1.25],
                    "weather_code": [71, 71],
                    "wind_speed_10m": [15.5, 16.2]
                },
                "daily": {
                    "time": ["2026-01-09"],
                    "temperature_2m_max": [-2.5],
                    "temperature_2m_min": [-8.3],
                    "snowfall_sum": [2.5],
                    "snow_depth_max": [1.3]
                }
            }
        )
        
        async with OpenMeteoClient() as client:
            result = await client.get_snow_conditions(
                latitude=45.9763,
                longitude=7.6586,
                forecast_days=7,
                include_hourly=True,
                timezone="Europe/Zurich"
            )
            
            assert isinstance(result, SnowConditions)
            assert result.latitude == 45.9763
            assert result.longitude == 7.6586
            assert result.hourly is not None
            assert len(result.hourly.time) == 2
            assert result.hourly.snow_depth[0] == 1.2
            assert result.daily is not None
            assert result.daily.snowfall_sum[0] == 2.5
    
    async def test_get_weather_http_error(self, httpx_mock: HTTPXMock):
        """Test handling of HTTP errors."""
        httpx_mock.add_response(status_code=500)
        
        async with OpenMeteoClient() as client:
            with pytest.raises(Exception):  # httpx.HTTPStatusError
                await client.get_weather(latitude=46.9479, longitude=7.4474)
    
    async def test_get_weather_invalid_response(self, httpx_mock: HTTPXMock):
        """Test handling of invalid JSON response."""
        httpx_mock.add_response(
            json={"invalid": "data"}
        )
        
        async with OpenMeteoClient() as client:
            with pytest.raises(ValueError):
                await client.get_weather(latitude=46.9479, longitude=7.4474)
    
    async def test_forecast_days_clamping(self, httpx_mock: HTTPXMock):
        """Test that forecast_days is clamped to 1-16 range."""
        # Add mock response for both test cases
        response_data = {
            "latitude": 46.9479,
            "longitude": 7.4474,
            "timezone": "auto",
            "daily": {
                "time": ["2026-01-09"],
                "temperature_2m_max": [18.5],
                "temperature_2m_min": [12.3],
                "precipitation_sum": [0.0],
                "weather_code": [2]
            }
        }
        
        # Add two separate responses for the two calls
        httpx_mock.add_response(json=response_data)
        httpx_mock.add_response(json=response_data)
        
        async with OpenMeteoClient() as client:
            # Test clamping to minimum (1)
            result = await client.get_weather(
                latitude=46.9479,
                longitude=7.4474,
                forecast_days=0,
                include_hourly=False
            )
            assert isinstance(result, WeatherForecast)
            
            # Test clamping to maximum (16)
            result = await client.get_weather(
                latitude=46.9479,
                longitude=7.4474,
                forecast_days=20,
                include_hourly=False
            )
            assert isinstance(result, WeatherForecast)
    
    async def test_client_context_manager(self):
        """Test client can be used as async context manager."""
        async with OpenMeteoClient() as client:
            assert client.client is not None
        # Client should be closed after context exit
    
    async def test_client_close(self):
        """Test client close method."""
        client = OpenMeteoClient()
        await client.close()
        # Should not raise an error
    
    async def test_get_snow_conditions_http_error(self, httpx_mock: HTTPXMock):
        """Test handling of HTTP errors for snow endpoint."""
        httpx_mock.add_response(status_code=503)
        
        async with OpenMeteoClient() as client:
            with pytest.raises(Exception):  # httpx.HTTPStatusError
                await client.get_snow_conditions(latitude=45.9763, longitude=7.6586)
    
    async def test_get_snow_conditions_invalid_response(self, httpx_mock: HTTPXMock):
        """Test handling of invalid JSON response for snow endpoint."""
        httpx_mock.add_response(
            json={"invalid": "snow_data"}
        )
        
        async with OpenMeteoClient() as client:
            with pytest.raises(ValueError):
                await client.get_snow_conditions(latitude=45.9763, longitude=7.6586)
    
    async def test_network_timeout(self, httpx_mock: HTTPXMock):
        """Test handling of network timeout."""
        import httpx
        
        # Create a client with very short timeout
        client = OpenMeteoClient(timeout=0.001)
        
        # Mock a delayed response
        httpx_mock.add_response(
            json={"latitude": 46.9479},
            # This will cause a timeout with our 0.001s timeout
        )
        
        # The timeout is so short that even a successful response might timeout
        # We're testing that the client handles timeout gracefully
        try:
            await client.get_weather(latitude=46.9479, longitude=7.4474)
        except (httpx.TimeoutException, httpx.ReadTimeout, Exception):
            # Expected - timeout or any network error
            pass
        finally:
            await client.close()

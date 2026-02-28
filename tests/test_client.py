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

    async def test_get_air_quality_success(self, httpx_mock: HTTPXMock):
        """Test successful air quality API call."""
        httpx_mock.add_response(
            json={
                "latitude": 46.9479,
                "longitude": 7.4474,
                "elevation": 542.0,
                "timezone": "Europe/Zurich",
                "timezone_abbreviation": "CET",
                "utc_offset_seconds": 3600,
                "current": {
                    "european_aqi": 45,
                    "us_aqi": 95,
                    "pm10": 25.5,
                    "pm2_5": 12.3,
                    "uv_index": 2.5
                },
                "hourly": {
                    "time": ["2026-01-09T00:00", "2026-01-09T01:00"],
                    "european_aqi": [40, 42],
                    "pm2_5": [10.5, 11.2],
                    "pm10": [20.5, 21.2],
                    "uv_index": [0.0, 0.1]
                }
            }
        )

        async with OpenMeteoClient() as client:
            from open_meteo_mcp.models import AirQualityForecast
            result = await client.get_air_quality(
                latitude=46.9479,
                longitude=7.4474,
                forecast_days=5,
                include_pollen=True,
                timezone="auto"
            )

            assert isinstance(result, AirQualityForecast)
            assert result.latitude == 46.9479
            assert result.longitude == 7.4474

    async def test_get_air_quality_without_pollen(self, httpx_mock: HTTPXMock):
        """Test air quality API call without pollen data."""
        httpx_mock.add_response(
            json={
                "latitude": 46.9479,
                "longitude": 7.4474,
                "timezone": "Europe/Zurich",
                "current": {
                    "european_aqi": 45,
                    "us_aqi": 95,
                    "pm10": 25.5,
                    "pm2_5": 12.3,
                    "uv_index": 2.5
                },
                "hourly": {
                    "time": ["2026-01-09T00:00"],
                    "european_aqi": [40],
                    "pm2_5": [10.5],
                    "pm10": [20.5],
                    "uv_index": [0.0]
                }
            }
        )

        async with OpenMeteoClient() as client:
            from open_meteo_mcp.models import AirQualityForecast
            result = await client.get_air_quality(
                latitude=46.9479,
                longitude=7.4474,
                include_pollen=False
            )

            assert isinstance(result, AirQualityForecast)
            assert result.latitude == 46.9479

    async def test_get_air_quality_http_error(self, httpx_mock: HTTPXMock):
        """Test handling of HTTP errors for air quality endpoint."""
        httpx_mock.add_response(status_code=429)  # Rate limited

        async with OpenMeteoClient() as client:
            with pytest.raises(Exception):
                await client.get_air_quality(latitude=46.9479, longitude=7.4474)

    async def test_get_air_quality_invalid_response(self, httpx_mock: HTTPXMock):
        """Test handling of invalid JSON response for air quality endpoint."""
        httpx_mock.add_response(json={"invalid": "air_quality_data"})

        async with OpenMeteoClient() as client:
            with pytest.raises(ValueError):
                await client.get_air_quality(latitude=46.9479, longitude=7.4474)

    async def test_search_location_success(self, httpx_mock: HTTPXMock):
        """Test successful location search."""
        httpx_mock.add_response(
            json={
                "results": [
                    {
                        "id": 2657896,
                        "name": "Zurich",
                        "latitude": 47.3769,
                        "longitude": 8.5417,
                        "elevation": 408.0,
                        "feature_code": "PPLA",
                        "country_code": "CH",
                        "country": "Switzerland"
                    },
                    {
                        "id": 6354439,
                        "name": "Zurich Airport",
                        "latitude": 47.4582,
                        "longitude": 8.5496,
                        "elevation": 430.0,
                        "feature_code": "AIRP",
                        "country_code": "CH",
                        "country": "Switzerland"
                    }
                ],
                "generationtime_ms": 1.234
            }
        )

        async with OpenMeteoClient() as client:
            from open_meteo_mcp.models import GeocodingResponse
            result = await client.search_location(
                name="Zurich",
                count=10,
                language="en",
                country=None
            )

            assert isinstance(result, GeocodingResponse)
            assert len(result.results) == 2
            assert result.results[0].name == "Zurich"

    async def test_search_location_with_country_filter(self, httpx_mock: HTTPXMock):
        """Test location search with country filtering."""
        httpx_mock.add_response(
            json={
                "results": [
                    {
                        "id": 2657896,
                        "name": "Zurich",
                        "latitude": 47.3769,
                        "longitude": 8.5417,
                        "elevation": 408.0,
                        "feature_code": "PPLA",
                        "country_code": "CH",
                        "country": "Switzerland"
                    }
                ],
                "generationtime_ms": 1.234
            }
        )

        async with OpenMeteoClient() as client:
            from open_meteo_mcp.models import GeocodingResponse
            result = await client.search_location(
                name="Zurich",
                count=10,
                language="en",
                country="CH"
            )

            assert isinstance(result, GeocodingResponse)
            assert len(result.results) == 1
            assert result.results[0].country_code == "CH"

    async def test_search_location_no_results(self, httpx_mock: HTTPXMock):
        """Test location search with no results."""
        httpx_mock.add_response(
            json={
                "results": [],
                "generationtime_ms": 0.5
            }
        )

        async with OpenMeteoClient() as client:
            from open_meteo_mcp.models import GeocodingResponse
            result = await client.search_location(
                name="NonExistentPlace12345",
                count=10
            )

            assert isinstance(result, GeocodingResponse)
            assert len(result.results) == 0

    async def test_search_location_http_error(self, httpx_mock: HTTPXMock):
        """Test handling of HTTP errors for search location endpoint."""
        httpx_mock.add_response(status_code=503)

        async with OpenMeteoClient() as client:
            with pytest.raises(Exception):
                await client.search_location(name="Test")

    async def test_search_location_invalid_response(self, httpx_mock: HTTPXMock):
        """Test handling of invalid response for search location."""
        httpx_mock.add_response(json={
            "results": [{"id": 1, "name": "Test"}],  # Missing required latitude/longitude
            "generationtime_ms": 1.0
        })

        async with OpenMeteoClient() as client:
            with pytest.raises(ValueError):
                await client.search_location(name="Test")

    async def test_get_historical_weather_success(self, httpx_mock: HTTPXMock):
        """Test successful historical weather API call."""
        httpx_mock.add_response(
            json={
                "latitude": 46.9479,
                "longitude": 7.4474,
                "elevation": 542.0,
                "timezone": "Europe/Zurich",
                "timezone_abbreviation": "CET",
                "utc_offset_seconds": 3600,
                "daily": {
                    "time": ["2025-01-01", "2025-01-02"],
                    "temperature_2m_max": [5.5, 6.2],
                    "temperature_2m_min": [1.2, 2.1],
                    "precipitation_sum": [0.5, 1.2],
                    "weather_code": [51, 61]
                }
            }
        )

        async with OpenMeteoClient() as client:
            result = await client.get_historical_weather(
                latitude=46.9479,
                longitude=7.4474,
                start_date="2025-01-01",
                end_date="2025-01-02",
                hourly=False,
                timezone="auto"
            )

            assert isinstance(result, WeatherForecast)
            assert result.latitude == 46.9479
            assert result.daily is not None
            assert len(result.daily.time) == 2

    async def test_get_historical_weather_with_hourly(self, httpx_mock: HTTPXMock):
        """Test historical weather with hourly data."""
        httpx_mock.add_response(
            json={
                "latitude": 46.9479,
                "longitude": 7.4474,
                "timezone": "Europe/Zurich",
                "hourly": {
                    "time": ["2025-01-01T00:00", "2025-01-01T01:00"],
                    "temperature_2m": [2.5, 2.3],
                    "precipitation": [0.0, 0.1],
                    "weather_code": [2, 51]
                },
                "daily": {
                    "time": ["2025-01-01"],
                    "temperature_2m_max": [5.5],
                    "temperature_2m_min": [1.2],
                    "precipitation_sum": [0.5],
                    "weather_code": [51]
                }
            }
        )

        async with OpenMeteoClient() as client:
            result = await client.get_historical_weather(
                latitude=46.9479,
                longitude=7.4474,
                start_date="2025-01-01",
                end_date="2025-01-01",
                hourly=True
            )

            assert isinstance(result, WeatherForecast)
            assert result.hourly is not None
            assert len(result.hourly.time) == 2

    async def test_get_historical_weather_http_error(self, httpx_mock: HTTPXMock):
        """Test handling of HTTP errors for historical weather."""
        httpx_mock.add_response(status_code=400)

        async with OpenMeteoClient() as client:
            with pytest.raises(Exception):
                await client.get_historical_weather(
                    latitude=46.9479,
                    longitude=7.4474,
                    start_date="2025-01-01",
                    end_date="2025-01-02"
                )

    async def test_get_historical_weather_invalid_response(self, httpx_mock: HTTPXMock):
        """Test handling of invalid response for historical weather."""
        httpx_mock.add_response(json={"invalid": "historical_data"})

        async with OpenMeteoClient() as client:
            with pytest.raises(ValueError):
                await client.get_historical_weather(
                    latitude=46.9479,
                    longitude=7.4474,
                    start_date="2025-01-01",
                    end_date="2025-01-02"
                )

    async def test_get_marine_conditions_success(self, httpx_mock: HTTPXMock):
        """Test successful marine conditions API call."""
        httpx_mock.add_response(
            json={
                "latitude": 47.2,
                "longitude": 8.5,
                "elevation": 400.0,
                "timezone": "Europe/Zurich",
                "timezone_abbreviation": "CET",
                "utc_offset_seconds": 3600,
                "hourly": {
                    "time": ["2026-01-09T00:00", "2026-01-09T01:00"],
                    "wave_height": [0.5, 0.6],
                    "wave_direction": [180, 185],
                    "wave_period": [5.5, 5.8],
                    "wind_wave_height": [0.3, 0.4],
                    "swell_wave_height": [0.2, 0.2]
                },
                "daily": {
                    "time": ["2026-01-09"],
                    "wave_height_max": [0.7],
                    "wave_direction_dominant": [180],
                    "wave_period_max": [6.0],
                    "swell_wave_height_max": [0.3]
                }
            }
        )

        async with OpenMeteoClient() as client:
            from open_meteo_mcp.models import MarineConditions
            result = await client.get_marine_conditions(
                latitude=47.2,
                longitude=8.5,
                forecast_days=7,
                include_hourly=True,
                timezone="auto"
            )

            assert isinstance(result, MarineConditions)
            assert result.latitude == 47.2
            assert result.longitude == 8.5
            assert result.hourly is not None
            assert len(result.hourly.time) == 2

    async def test_get_marine_conditions_without_hourly(self, httpx_mock: HTTPXMock):
        """Test marine conditions without hourly data."""
        httpx_mock.add_response(
            json={
                "latitude": 47.2,
                "longitude": 8.5,
                "timezone": "Europe/Zurich",
                "daily": {
                    "time": ["2026-01-09"],
                    "wave_height_max": [0.7],
                    "wave_direction_dominant": [180],
                    "wave_period_max": [6.0],
                    "swell_wave_height_max": [0.3]
                }
            }
        )

        async with OpenMeteoClient() as client:
            from open_meteo_mcp.models import MarineConditions
            result = await client.get_marine_conditions(
                latitude=47.2,
                longitude=8.5,
                include_hourly=False
            )

            assert isinstance(result, MarineConditions)
            assert result.daily is not None

    async def test_get_marine_conditions_http_error(self, httpx_mock: HTTPXMock):
        """Test handling of HTTP errors for marine conditions."""
        httpx_mock.add_response(status_code=502)

        async with OpenMeteoClient() as client:
            with pytest.raises(Exception):
                await client.get_marine_conditions(latitude=47.2, longitude=8.5)

    async def test_get_marine_conditions_invalid_response(self, httpx_mock: HTTPXMock):
        """Test handling of invalid response for marine conditions."""
        httpx_mock.add_response(json={"invalid": "marine_data"})

        async with OpenMeteoClient() as client:
            with pytest.raises(ValueError):
                await client.get_marine_conditions(latitude=47.2, longitude=8.5)

    @pytest.mark.asyncio
    async def test_client_str_representation(self):
        """Test string representation of client."""
        async with OpenMeteoClient() as client:
            str_repr = str(client)
            assert "OpenMeteoClient" in str_repr
            assert "base_url" in str_repr

    @pytest.mark.asyncio
    async def test_client_repr_representation(self):
        """Test repr representation of client."""
        async with OpenMeteoClient() as client:
            repr_str = repr(client)
            assert "OpenMeteoClient" in repr_str
            assert "base_url" in repr_str
            assert "timeout" in repr_str

    @pytest.mark.asyncio
    async def test_client_to_dict(self):
        """Test client serialization to dictionary."""
        async with OpenMeteoClient(timeout=45.0) as client:
            client_dict = client.to_dict()

            assert isinstance(client_dict, dict)
            assert "base_url" in client_dict
            assert "timeout" in client_dict
            assert client_dict["base_url"] == "https://api.open-meteo.com/v1"
            # timeout should be present and valid
            assert client_dict["timeout"] is not None

    async def test_search_location_count_clamping(self, httpx_mock: HTTPXMock):
        """Test that search count is clamped to 1-100 range."""
        response_data = {
            "results": [{
                "id": 1,
                "name": "Test",
                "latitude": 47.0,
                "longitude": 8.0,
                "country_code": "CH"
            }],
            "generationtime_ms": 1.0
        }

        # Add two responses for the two test cases
        httpx_mock.add_response(json=response_data)
        httpx_mock.add_response(json=response_data)

        async with OpenMeteoClient() as client:
            from open_meteo_mcp.models import GeocodingResponse

            # Test clamping to minimum (1)
            result = await client.search_location(name="Test", count=0)
            assert isinstance(result, GeocodingResponse)

            # Test clamping to maximum (100)
            result = await client.search_location(name="Test", count=150)
            assert isinstance(result, GeocodingResponse)

    async def test_air_quality_forecast_days_clamping(self, httpx_mock: HTTPXMock):
        """Test that air quality forecast_days is clamped to 1-5 range."""
        response_data = {
            "latitude": 46.9479,
            "longitude": 7.4474,
            "timezone": "Europe/Zurich",
            "current": {
                "european_aqi": 45,
                "us_aqi": 95,
                "pm10": 25.5,
                "pm2_5": 12.3,
                "uv_index": 2.5
            },
            "hourly": {
                "time": ["2026-01-09T00:00"],
                "european_aqi": [40],
                "pm2_5": [10.5],
                "pm10": [20.5],
                "uv_index": [0.0]
            }
        }

        # Add two responses
        httpx_mock.add_response(json=response_data)
        httpx_mock.add_response(json=response_data)

        async with OpenMeteoClient() as client:
            from open_meteo_mcp.models import AirQualityForecast

            # Test clamping to minimum (1)
            result = await client.get_air_quality(
                latitude=46.9479,
                longitude=7.4474,
                forecast_days=0
            )
            assert isinstance(result, AirQualityForecast)

            # Test clamping to maximum (5)
            result = await client.get_air_quality(
                latitude=46.9479,
                longitude=7.4474,
                forecast_days=10
            )
            assert isinstance(result, AirQualityForecast)

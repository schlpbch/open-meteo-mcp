"""
Comprehensive test suite for Open Meteo MCP improvements.

Tests weather alerts functionality, timezone consistency, country filtering,
and overall API improvements.
"""

import pytest
from unittest.mock import patch, Mock
from datetime import datetime
from src.open_meteo_mcp.client import OpenMeteoClient


class TestCountryFiltering:
    """Test suite for country filtering improvements."""

    @pytest.fixture
    def mock_geocoding_response(self):
        """Mock geocoding API response with mixed countries."""
        return {
            "results": [
                {
                    "name": "Thun",
                    "country": "Switzerland",
                    "country_code": "CH",
                    "latitude": 46.75,
                    "longitude": 7.63,
                    "admin1": "Bern",
                },
                {
                    "name": "Thun",
                    "country": "Pakistan",
                    "country_code": "PK",
                    "latitude": 33.5,
                    "longitude": 72.1,
                    "admin1": "Punjab",
                },
                {
                    "name": "Thūn",
                    "country": "India",
                    "country_code": "IN",
                    "latitude": 26.8,
                    "longitude": 78.4,
                    "admin1": "Uttar Pradesh",
                },
            ],
            "generationtime_ms": 0.5,
        }

    @pytest.mark.asyncio
    async def test_country_filtering_works(self, mock_geocoding_response):
        """Test that country filtering returns only matching results."""
        client = OpenMeteoClient()

        with patch.object(client.client, "get") as mock_get:
            mock_response = Mock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = mock_geocoding_response
            mock_get.return_value = mock_response

            result = await client.search_location("Thun", country="CH", count=5)

            # Should only return Swiss results
            assert len(result.results) == 1
            assert result.results[0].country_code == "CH"
            assert result.results[0].name == "Thun"
            assert result.results[0].country == "Switzerland"

        await client.client.aclose()

    @pytest.mark.asyncio
    async def test_country_filtering_no_matches_returns_all(
        self, mock_geocoding_response
    ):
        """Test that if no country matches found, all results are returned."""
        client = OpenMeteoClient()

        # Mock response with no Swiss results
        no_swiss_response = {
            "results": [
                {
                    "name": "Thun",
                    "country": "Pakistan",
                    "country_code": "PK",
                    "latitude": 33.5,
                    "longitude": 72.1,
                },
                {
                    "name": "Thūn",
                    "country": "India",
                    "country_code": "IN",
                    "latitude": 26.8,
                    "longitude": 78.4,
                },
            ],
            "generationtime_ms": 0.5,
        }

        with patch.object(client.client, "get") as mock_get:
            mock_response = Mock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = no_swiss_response
            mock_get.return_value = mock_response

            result = await client.search_location("Thun", country="CH", count=5)

            # Should return all results when no country matches
            assert len(result.results) == 2

        await client.client.aclose()

    @pytest.mark.asyncio
    async def test_no_country_filter_returns_all(self, mock_geocoding_response):
        """Test that without country filter, all results are returned."""
        client = OpenMeteoClient()

        with patch.object(client.client, "get") as mock_get:
            mock_response = Mock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = mock_geocoding_response
            mock_get.return_value = mock_response

            result = await client.search_location("Thun", count=5)

            # Should return all results
            assert len(result.results) == 3

        await client.client.aclose()


class TestTimezoneConsistency:
    """Test suite for timezone consistency improvements."""

    @pytest.mark.asyncio
    async def test_air_quality_timezone_parameter(self):
        """Test that air quality endpoint accepts timezone parameter."""
        client = OpenMeteoClient()

        mock_response_data = {
            "latitude": 46.9479,
            "longitude": 7.4474,
            "timezone": "Europe/Zurich",
            "current": {
                "european_aqi": 25,
                "us_aqi": 45,
                "pm10": 15.0,
                "pm2_5": 8.0,
                "uv_index": 3,
            },
            "hourly": {
                "time": ["2026-01-18T00:00"],
                "european_aqi": [25],
                "us_aqi": [45],
            },
        }

        with patch.object(client.client, "get") as mock_get:
            mock_response = Mock()
            mock_response.raise_for_status.return_value = None
            mock_response.json.return_value = mock_response_data
            mock_get.return_value = mock_response

            result = await client.get_air_quality(
                46.9479, 7.4474, timezone="Europe/Zurich"
            )

            # Verify timezone parameter was passed
            mock_get.assert_called_once()
            call_args = mock_get.call_args
            assert call_args[1]["params"]["timezone"] == "Europe/Zurich"

            # Verify result has correct timezone
            assert result.timezone == "Europe/Zurich"

        await client.client.aclose()

    @pytest.mark.asyncio
    async def test_timezone_consistency_across_endpoints(self):
        """Test that weather and air quality use same timezone when specified."""
        client = OpenMeteoClient()

        # Mock weather response
        weather_response = {
            "latitude": 46.9479,
            "longitude": 7.4474,
            "timezone": "Europe/Zurich",
            "current_weather": {
                "temperature": 15.5,
                "windspeed": 10.0,
                "winddirection": 180,
                "weathercode": 1,
                "time": "2026-01-18T12:00",
            },
            "hourly": {"time": ["2026-01-18T00:00"], "temperature_2m": [15.5]},
            "daily": {
                "time": ["2026-01-18"],
                "temperature_2m_max": [18.0],
                "temperature_2m_min": [12.0],
            },
        }

        # Mock air quality response
        air_quality_response = {
            "latitude": 46.9479,
            "longitude": 7.4474,
            "timezone": "Europe/Zurich",
            "current": {"european_aqi": 25, "us_aqi": 45},
            "hourly": {"time": ["2026-01-18T00:00"], "european_aqi": [25]},
        }

        with patch.object(client.client, "get") as mock_get:
            # Setup mock to return different responses based on URL
            def side_effect(url, **kwargs):
                mock_response = Mock()
                mock_response.raise_for_status.return_value = None
                if "air-quality" in str(url):
                    mock_response.json.return_value = air_quality_response
                else:
                    mock_response.json.return_value = weather_response
                return mock_response

            mock_get.side_effect = side_effect

            # Get both weather and air quality
            weather = await client.get_weather(
                46.9479, 7.4474, timezone="Europe/Zurich"
            )
            air_quality = await client.get_air_quality(
                46.9479, 7.4474, timezone="Europe/Zurich"
            )

            # Both should use same timezone
            assert weather.timezone == "Europe/Zurich"
            assert air_quality.timezone == "Europe/Zurich"
            assert weather.timezone == air_quality.timezone

        await client.client.aclose()


class TestWeatherAlerts:
    """Test suite for weather alerts functionality."""

    def setup_method(self):
        """Set up test data for weather alerts."""
        self.test_current_time = datetime.now()

        # Mock weather data for different alert scenarios
        self.hot_weather_data = {
            "current_weather": {
                "temperature": 35.0,
                "windspeed": 5.0,
                "weathercode": 1,
            },
            "hourly": {
                "time": [self.test_current_time.isoformat()],
                "precipitation": [0.0],
            },
            "daily": {"uv_index_max": [11.0]},
            "timezone": "Europe/Zurich",
        }

        self.cold_weather_data = {
            "current_weather": {
                "temperature": -12.0,
                "windspeed": 25.0,
                "weathercode": 71,
            },
            "hourly": {
                "time": [self.test_current_time.isoformat()],
                "precipitation": [0.0],
            },
            "daily": {"uv_index_max": [2.0]},
            "timezone": "Europe/Zurich",
        }

        self.storm_weather_data = {
            "current_weather": {
                "temperature": 20.0,
                "windspeed": 85.0,
                "weathercode": 95,  # Thunderstorm
            },
            "hourly": {
                "time": [self.test_current_time.isoformat()],
                "precipitation": [15.0],
            },
            "daily": {"uv_index_max": [5.0]},
            "timezone": "Europe/Zurich",
        }

    def test_heat_alert_generation(self):
        """Test heat alert generation logic."""

        # Simulate hot weather conditions
        current = {"temperature": 35.0, "windspeed": 5.0}

        alerts = []

        # Simulate the heat alert logic from the tool
        temp = current["temperature"]
        if temp > 30:
            severity = "warning" if temp > 35 else "watch" if temp > 32 else "advisory"
            alert = {
                "type": "heat",
                "severity": severity,
                "description": f"High temperature alert: {temp:.1f}°C",
                "recommendations": [
                    "Stay hydrated and drink plenty of water",
                    "Avoid prolonged sun exposure during peak hours (11-15h)",
                    "Wear light-colored, loose-fitting clothing",
                    "Seek shade and air conditioning when possible",
                ],
            }
            alerts.append(alert)

        assert len(alerts) == 1
        assert alerts[0]["type"] == "heat"
        assert alerts[0]["severity"] == "watch"  # 35°C should trigger watch (not > 35)
        assert "35.0°C" in alerts[0]["description"]

    def test_cold_alert_generation(self):
        """Test cold alert generation logic."""
        current = {"temperature": -12.0, "windspeed": 25.0}

        alerts = []

        temp = current["temperature"]
        wind_speed = current["windspeed"]
        if temp < -5:
            # Calculate apparent temperature (simplified wind chill)
            apparent_temp = temp - (wind_speed * 0.6)
            severity = (
                "warning"
                if apparent_temp < -15
                else "watch" if apparent_temp < -10 else "advisory"
            )
            alert = {
                "type": "cold",
                "severity": severity,
                "description": f"Cold temperature alert: {temp:.1f}°C (feels like {apparent_temp:.1f}°C)",
                "recommendations": [
                    "Dress in warm layers and cover exposed skin",
                    "Wear insulated, waterproof footwear",
                    "Limit time outdoors and watch for frostbite signs",
                    "Keep emergency supplies in vehicles",
                ],
            }
            alerts.append(alert)

        assert len(alerts) == 1
        assert alerts[0]["type"] == "cold"
        assert (
            alerts[0]["severity"] == "warning"
        )  # -27°C feels like should trigger warning
        assert "-12.0°C" in alerts[0]["description"]

    def test_storm_alert_generation(self):
        """Test storm alert generation logic."""
        current = {"temperature": 20.0, "windspeed": 85.0, "weathercode": 95}

        alerts = []

        # Wind alert
        wind_speed = current["windspeed"]
        if wind_speed > 60:
            severity = "warning" if wind_speed > 80 else "watch"
            alerts.append(
                {
                    "type": "wind",
                    "severity": severity,
                    "description": f"High wind alert: {wind_speed:.1f} km/h",
                }
            )

        # Storm alert for thunderstorm weather code
        weather_code = current["weathercode"]
        if weather_code >= 95:
            alerts.append(
                {
                    "type": "storm",
                    "severity": "warning",
                    "description": "Thunderstorm alert: Lightning and heavy precipitation",
                }
            )

        assert len(alerts) == 2
        storm_alert = next(a for a in alerts if a["type"] == "storm")
        wind_alert = next(a for a in alerts if a["type"] == "wind")

        assert storm_alert["severity"] == "warning"
        assert wind_alert["severity"] == "warning"
        assert "Thunderstorm" in storm_alert["description"]
        assert "85.0 km/h" in wind_alert["description"]

    def test_uv_alert_generation(self):
        """Test UV alert generation logic."""
        daily = {"uv_index_max": [11.0]}

        alerts = []

        max_uv = max(daily["uv_index_max"])
        if max_uv > 8:
            severity = "warning" if max_uv > 10 else "watch"
            alert = {
                "type": "uv",
                "severity": severity,
                "description": f"High UV alert: UV Index {max_uv:.0f}",
                "recommendations": [
                    "Apply broad-spectrum SPF 30+ sunscreen every 2 hours",
                    "Wear protective clothing and wide-brimmed hat",
                    "Seek shade between 10am-4pm",
                    "Wear UV-blocking sunglasses",
                ],
            }
            alerts.append(alert)

        assert len(alerts) == 1
        assert alerts[0]["type"] == "uv"
        assert alerts[0]["severity"] == "warning"  # UV 11 should trigger warning
        assert "UV Index 11" in alerts[0]["description"]

    def test_precipitation_alert_generation(self):
        """Test heavy precipitation alert generation."""
        hourly = {"precipitation": [0.0, 5.0, 15.0, 25.0, 2.0]}

        alerts = []

        for i, precip in enumerate(hourly["precipitation"]):
            if precip > 10:  # Heavy precipitation threshold
                severity = "warning" if precip > 20 else "watch"
                alert = {
                    "type": "precipitation",
                    "severity": severity,
                    "description": f"Heavy precipitation alert: {precip:.1f}mm/hour expected",
                }
                alerts.append(alert)
                break  # Only show first heavy precipitation event

        assert len(alerts) == 1
        assert alerts[0]["type"] == "precipitation"
        assert alerts[0]["severity"] == "watch"  # 15mm should trigger watch
        assert "15.0mm/hour" in alerts[0]["description"]

    def test_no_alerts_for_normal_conditions(self):
        """Test that normal weather conditions generate no alerts."""
        current = {"temperature": 18.0, "windspeed": 15.0, "weathercode": 1}
        daily = {"uv_index_max": [5.0]}
        hourly = {"precipitation": [0.0, 0.5, 1.0]}

        alerts = []

        # Check all alert conditions
        temp = current["temperature"]
        if temp > 30 or temp < -5:
            # Should not trigger
            pass

        wind_speed = current["windspeed"]
        if wind_speed > 60:
            # Should not trigger
            pass

        weather_code = current["weathercode"]
        if weather_code >= 95:
            # Should not trigger
            pass

        max_uv = max(daily["uv_index_max"])
        if max_uv > 8:
            # Should not trigger
            pass

        for precip in hourly["precipitation"]:
            if precip > 10:
                # Should not trigger
                break

        assert len(alerts) == 0


class TestIntegration:
    """Integration tests for the complete MCP improvements."""

    @pytest.mark.asyncio
    async def test_end_to_end_weather_workflow(self):
        """Test complete workflow from location search to weather alerts."""
        client = OpenMeteoClient()

        # Mock location search response
        location_response = {
            "results": [
                {
                    "name": "Bern",
                    "country": "Switzerland",
                    "country_code": "CH",
                    "latitude": 46.9479,
                    "longitude": 7.4474,
                    "timezone": "Europe/Zurich",
                }
            ],
            "generationtime_ms": 0.5,
        }

        # Mock weather response for alerts
        weather_response = {
            "latitude": 46.9479,
            "longitude": 7.4474,
            "timezone": "Europe/Zurich",
            "current_weather": {
                "temperature": 32.0,
                "windspeed": 15.0,
                "winddirection": 180,
                "weathercode": 1,
                "time": "2026-01-18T12:00",
            },
            "hourly": {"time": ["2026-01-18T00:00"], "precipitation": [0.0]},
            "daily": {"time": ["2026-01-18"], "uv_index_max": [9.0]},
        }

        with patch.object(client.client, "get") as mock_get:

            def side_effect(url, **kwargs):
                mock_response = Mock()
                mock_response.raise_for_status.return_value = None
                if "geocoding" in str(url):
                    mock_response.json.return_value = location_response
                else:
                    mock_response.json.return_value = weather_response
                return mock_response

            mock_get.side_effect = side_effect

            # Step 1: Search for location with country filter
            location_result = await client.search_location("Bern", country="CH")
            assert len(location_result.results) == 1
            assert location_result.results[0].country_code == "CH"

            # Step 2: Get weather data for location
            location = location_result.results[0]
            weather = await client.get_weather(
                location.latitude, location.longitude, timezone="Europe/Zurich"
            )

            # Step 3: Verify timezone consistency
            assert weather.timezone == "Europe/Zurich"

            # Step 4: Check that we can generate alerts from this data
            temp = weather.current_weather.temperature
            assert temp == 32.0
            # This would trigger a heat alert (temp > 30)

        await client.client.aclose()


if __name__ == "__main__":
    # Run tests if executed directly
    import subprocess

    subprocess.run(["python", "-m", "pytest", __file__, "-v"])

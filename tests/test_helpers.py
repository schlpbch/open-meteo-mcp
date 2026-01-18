"""Unit tests for helper functions."""

import pytest

from open_meteo_mcp.helpers import (
    interpret_weather_code,
    get_weather_category,
    get_travel_impact,
    assess_ski_conditions,
    format_temperature,
    calculate_wind_chill,
    get_seasonal_advice,
    format_precipitation,
    generate_weather_alerts,
    calculate_comfort_index,
    calculate_astronomy_data,
    normalize_timezone,
    normalize_air_quality_timezone,
)


class TestInterpretWeatherCode:
    """Test weather code interpretation."""
    
    def test_clear_sky(self):
        """Test interpretation of clear sky code."""
        result = interpret_weather_code(0)
        assert result["description"] == "Clear sky"
        assert result["category"] == "Clear"
        assert result["severity"] == "none"
    
    def test_partly_cloudy(self):
        """Test interpretation of partly cloudy code."""
        result = interpret_weather_code(2)
        assert result["description"] == "Partly cloudy"
        assert result["category"] == "Cloudy"
        assert result["severity"] == "low"
    
    def test_moderate_rain(self):
        """Test interpretation of moderate rain code."""
        result = interpret_weather_code(63)
        assert result["description"] == "Moderate rain"
        assert result["category"] == "Rain"
        assert result["severity"] == "medium"
    
    def test_heavy_snow(self):
        """Test interpretation of heavy snow code."""
        result = interpret_weather_code(75)
        assert result["description"] == "Heavy snow"
        assert result["category"] == "Snow"
        assert result["severity"] == "high"
    
    def test_thunderstorm(self):
        """Test interpretation of thunderstorm code."""
        result = interpret_weather_code(95)
        assert result["description"] == "Thunderstorm"
        assert result["category"] == "Thunderstorm"
        assert result["severity"] == "high"
    
    def test_unknown_code(self):
        """Test interpretation of unknown weather code."""
        result = interpret_weather_code(999)
        assert "Unknown" in result["description"]
        assert result["category"] == "Unknown"
        assert result["severity"] == "unknown"


class TestGetWeatherCategory:
    """Test weather category extraction."""
    
    def test_clear_category(self):
        """Test getting Clear category."""
        assert get_weather_category(0) == "Clear"
        assert get_weather_category(1) == "Clear"
    
    def test_rain_category(self):
        """Test getting Rain category."""
        assert get_weather_category(61) == "Rain"
        assert get_weather_category(63) == "Rain"
    
    def test_snow_category(self):
        """Test getting Snow category."""
        assert get_weather_category(71) == "Snow"
        assert get_weather_category(75) == "Snow"


class TestGetTravelImpact:
    """Test travel impact assessment."""
    
    def test_no_impact(self):
        """Test no travel impact for clear weather."""
        assert get_travel_impact(0) == "none"
        assert get_travel_impact(1) == "none"
    
    def test_minor_impact(self):
        """Test minor impact for light rain."""
        assert get_travel_impact(51) == "minor"
        assert get_travel_impact(61) == "minor"
    
    def test_moderate_impact(self):
        """Test moderate impact for moderate rain."""
        assert get_travel_impact(63) == "moderate"
        assert get_travel_impact(45) == "moderate"
    
    def test_significant_impact(self):
        """Test significant impact for heavy conditions."""
        assert get_travel_impact(65) == "significant"
        assert get_travel_impact(95) == "significant"
    
    def test_severe_impact(self):
        """Test severe impact for extreme conditions."""
        assert get_travel_impact(99) == "severe"


class TestAssessSkiConditions:
    """Test ski condition assessment."""
    
    def test_excellent_conditions(self):
        """Test assessment of excellent ski conditions."""
        snow_data = {"snow_depth": 1.2, "recent_snowfall": 15}
        weather_data = {"temperature": -10, "weather_code": 0}
        result = assess_ski_conditions(snow_data, weather_data)
        assert result == "Excellent"
    
    def test_good_conditions(self):
        """Test assessment of good ski conditions."""
        snow_data = {"snow_depth": 0.8, "recent_snowfall": 2}
        weather_data = {"temperature": -5, "weather_code": 2}
        result = assess_ski_conditions(snow_data, weather_data)
        assert result == "Good"
    
    def test_fair_conditions(self):
        """Test assessment of fair ski conditions."""
        snow_data = {"snow_depth": 0.3, "recent_snowfall": 0}
        weather_data = {"temperature": 2, "weather_code": 3}
        result = assess_ski_conditions(snow_data, weather_data)
        assert result == "Fair"
    
    def test_poor_conditions(self):
        """Test assessment of poor ski conditions."""
        snow_data = {"snow_depth": 0.1, "recent_snowfall": 0}
        weather_data = {"temperature": 8, "weather_code": 61}
        result = assess_ski_conditions(snow_data, weather_data)
        assert result == "Poor"


class TestFormatTemperature:
    """Test temperature formatting."""
    
    def test_positive_temperature(self):
        """Test formatting positive temperature."""
        assert format_temperature(15.2) == "15.2°C"
    
    def test_negative_temperature(self):
        """Test formatting negative temperature."""
        assert format_temperature(-5.8) == "-5.8°C"
    
    def test_zero_temperature(self):
        """Test formatting zero temperature."""
        assert format_temperature(0.0) == "0.0°C"
    
    def test_rounding(self):
        """Test temperature rounding to 1 decimal."""
        assert format_temperature(15.234) == "15.2°C"
        assert format_temperature(15.289) == "15.3°C"


class TestCalculateWindChill:
    """Test wind chill calculation."""
    
    def test_low_wind_no_chill(self):
        """Test no wind chill with low wind speed."""
        result = calculate_wind_chill(temp=5, wind=3)
        assert result == 5  # No wind chill below 4.8 km/h
    
    def test_moderate_wind_chill(self):
        """Test wind chill with moderate wind."""
        result = calculate_wind_chill(temp=0, wind=20)
        assert result < 0  # Should feel colder
        assert isinstance(result, float)
    
    def test_high_wind_chill(self):
        """Test wind chill with high wind."""
        result = calculate_wind_chill(temp=-10, wind=40)
        assert result < -10  # Should feel much colder
    
    def test_positive_temp_wind_chill(self):
        """Test wind chill with positive temperature."""
        result = calculate_wind_chill(temp=10, wind=30)
        assert result < 10


class TestGetSeasonalAdvice:
    """Test seasonal advice."""
    
    def test_winter_advice(self):
        """Test winter seasonal advice."""
        advice = get_seasonal_advice(12)
        assert "Winter" in advice
        assert "skiing" in advice.lower() or "snow" in advice.lower()
    
    def test_spring_advice(self):
        """Test spring seasonal advice."""
        advice = get_seasonal_advice(4)
        assert "Spring" in advice
    
    def test_summer_advice(self):
        """Test summer seasonal advice."""
        advice = get_seasonal_advice(7)
        assert "Summer" in advice
        assert "hiking" in advice.lower() or "outdoor" in advice.lower()
    
    def test_autumn_advice(self):
        """Test autumn seasonal advice."""
        advice = get_seasonal_advice(10)
        assert "Autumn" in advice


class TestFormatPrecipitation:
    """Test precipitation formatting."""
    
    def test_no_precipitation(self):
        """Test formatting no precipitation."""
        assert format_precipitation(0.0) == "No precipitation"
    
    def test_light_precipitation(self):
        """Test formatting light precipitation."""
        result = format_precipitation(0.5)
        assert "0.5mm" in result
        assert "light" in result.lower()
    
    def test_moderate_precipitation(self):
        """Test formatting moderate precipitation."""
        result = format_precipitation(3.0)
        assert "3.0mm" in result
        assert "moderate" in result.lower()
    
    def test_heavy_precipitation(self):
        """Test formatting heavy precipitation."""
        result = format_precipitation(7.5)
        assert "7.5mm" in result
        assert "heavy" in result.lower()
    
    def test_very_heavy_precipitation(self):
        """Test formatting very heavy precipitation."""
        result = format_precipitation(15.0)
        assert "15.0mm" in result
        assert "very heavy" in result.lower()


class TestGenerateWeatherAlerts:
    """Test weather alert generation."""

    def test_heat_alert_generation(self):
        """Test heat alert is generated for high temperatures."""
        current = {"temperature": 32, "windspeed": 10, "weathercode": 0}
        hourly = {
            "temperature_2m": [32, 33, 34, 35, 35, 34, 33, 32] + [20] * 16,
            "wind_gusts_10m": [10] * 24,
            "uv_index": [3] * 24,
            "time": [f"2024-01-18T{h:02d}:00" for h in range(24)]
        }
        daily = {
            "temperature_2m_max": [35],
            "temperature_2m_min": [30],
            "precipitation_sum": [0],
            "weather_code": [0],
            "time": ["2024-01-18"]
        }
        alerts = generate_weather_alerts(current, hourly, daily, "Europe/Zurich")
        assert len(alerts) > 0
        heat_alerts = [a for a in alerts if a["type"] == "heat"]
        assert len(heat_alerts) > 0

    def test_cold_alert_generation(self):
        """Test cold alert is generated for low temperatures."""
        current = {"temperature": -15, "windspeed": 10, "weathercode": 0}
        hourly = {
            "temperature_2m": [-15, -16, -17] + [10] * 21,
            "wind_gusts_10m": [10] * 24,
            "uv_index": [1] * 24,
            "time": [f"2024-01-18T{h:02d}:00" for h in range(24)]
        }
        daily = {
            "temperature_2m_max": [-10],
            "temperature_2m_min": [-20],
            "precipitation_sum": [0],
            "weather_code": [0],
            "time": ["2024-01-18"]
        }
        alerts = generate_weather_alerts(current, hourly, daily, "Europe/Zurich")
        cold_alerts = [a for a in alerts if a["type"] == "cold"]
        assert len(cold_alerts) > 0

    def test_no_alerts_for_normal_conditions(self):
        """Test no alerts for normal weather."""
        current = {"temperature": 15, "windspeed": 10, "weathercode": 2}
        hourly = {
            "temperature_2m": [15] * 24,
            "wind_gusts_10m": [15] * 24,
            "uv_index": [3] * 24,
            "time": [f"2024-01-18T{h:02d}:00" for h in range(24)]
        }
        daily = {
            "temperature_2m_max": [18],
            "temperature_2m_min": [12],
            "precipitation_sum": [0],
            "weather_code": [2],
            "time": ["2024-01-18"]
        }
        alerts = generate_weather_alerts(current, hourly, daily, "Europe/Zurich")
        # May have some alerts, but not severe ones
        severe_alerts = [a for a in alerts if a["severity"] == "warning"]
        assert len(severe_alerts) == 0


class TestCalculateComfortIndex:
    """Test comfort index calculation."""

    def test_perfect_comfort(self):
        """Test comfort index for perfect conditions."""
        weather = {
            "temperature": 20,
            "relative_humidity_2m": 50,
            "wind_speed_10m": 5,
            "uv_index": 2,
            "precipitation_probability": 0,
            "weather_code": 0
        }
        air_quality = {"european_aqi": 20}
        result = calculate_comfort_index(weather, air_quality)
        assert result["overall"] >= 80
        assert result["recommendation"] == "Perfect for outdoor activities"

    def test_poor_comfort(self):
        """Test comfort index for poor conditions."""
        weather = {
            "temperature": -20,
            "relative_humidity_2m": 80,
            "wind_speed_10m": 40,
            "uv_index": 0,
            "precipitation_probability": 100,
            "weather_code": 99
        }
        air_quality = {"european_aqi": 150}
        result = calculate_comfort_index(weather, air_quality)
        assert result["overall"] < 40
        assert "Poor" in result["recommendation"] or "Very poor" in result["recommendation"]

    def test_all_factors_present(self):
        """Test that all comfort factors are calculated."""
        weather = {
            "temperature": 15,
            "relative_humidity_2m": 60,
            "wind_speed_10m": 15,
            "uv_index": 4,
            "precipitation_probability": 30,
            "weather_code": 2
        }
        result = calculate_comfort_index(weather)
        assert "overall" in result
        assert "factors" in result
        assert "thermal_comfort" in result["factors"]
        assert "air_quality" in result["factors"]
        assert "precipitation_risk" in result["factors"]
        assert "uv_safety" in result["factors"]
        assert "weather_condition" in result["factors"]


class TestCalculateAstronomyData:
    """Test astronomy data calculation."""

    def test_astronomy_data_contains_times(self):
        """Test astronomy data returns sunrise/sunset times."""
        result = calculate_astronomy_data(47.3769, 8.5417, "Europe/Zurich")
        assert "sunrise" in result
        assert "sunset" in result
        assert "day_length_hours" in result

    def test_astronomy_data_contains_golden_hour(self):
        """Test astronomy data includes golden hour."""
        result = calculate_astronomy_data(47.3769, 8.5417, "Europe/Zurich")
        assert "golden_hour" in result
        assert "start" in result["golden_hour"]
        assert "end" in result["golden_hour"]

    def test_astronomy_data_contains_blue_hour(self):
        """Test astronomy data includes blue hour."""
        result = calculate_astronomy_data(47.3769, 8.5417, "Europe/Zurich")
        assert "blue_hour" in result
        assert "start" in result["blue_hour"]
        assert "end" in result["blue_hour"]


class TestNormalizeTimezone:
    """Test timezone normalization."""

    def test_normalize_timezone_updates_field(self):
        """Test timezone field is updated."""
        response_data = {
            "timezone": "Europe/Zurich",
            "hourly": {"time": []},
            "daily": {"time": []}
        }
        result = normalize_timezone(response_data, "UTC")
        assert result["timezone"] == "UTC"

    def test_normalize_handles_invalid_data(self):
        """Test normalization handles invalid input gracefully."""
        response_data = None
        result = normalize_timezone(response_data or {})
        assert isinstance(result, dict)


class TestNormalizeAirQualityTimezone:
    """Test air quality timezone normalization."""

    def test_normalize_air_quality_updates_timezone(self):
        """Test air quality timezone is updated."""
        air_quality_data = {
            "timezone": "GMT",
            "hourly": {"time": []},
            "current": {}
        }
        result = normalize_air_quality_timezone(air_quality_data, "Europe/Zurich")
        assert result["timezone"] == "Europe/Zurich"

    def test_normalize_air_quality_preserves_data(self):
        """Test normalization preserves other data."""
        air_quality_data = {
            "timezone": "GMT",
            "hourly": {"time": [], "pm2_5": [10, 15]},
            "latitude": 47.3
        }
        result = normalize_air_quality_timezone(air_quality_data)
        assert result["latitude"] == 47.3
        assert result["hourly"]["pm2_5"] == [10, 15]

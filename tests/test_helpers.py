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

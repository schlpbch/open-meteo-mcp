"""Unit tests for Pydantic models."""

import pytest
from pydantic import ValidationError

from open_meteo_mcp.models import (
    WeatherInput,
    SnowInput,
    CurrentWeather,
    HourlyWeather,
    DailyWeather,
    WeatherForecast,
    HourlySnow,
    DailySnow,
    SnowConditions,
)


class TestWeatherInput:
    """Test WeatherInput model validation."""
    
    def test_valid_weather_input(self):
        """Test creating valid WeatherInput."""
        input_data = WeatherInput(
            latitude=46.9479,
            longitude=7.4474,
            forecast_days=7,
            include_hourly=True,
            timezone="Europe/Zurich"
        )
        assert input_data.latitude == 46.9479
        assert input_data.longitude == 7.4474
        assert input_data.forecast_days == 7
        assert input_data.include_hourly is True
        assert input_data.timezone == "Europe/Zurich"
    
    def test_default_values(self):
        """Test default values for optional fields."""
        input_data = WeatherInput(latitude=46.9479, longitude=7.4474)
        assert input_data.forecast_days == 7
        assert input_data.include_hourly is True
        assert input_data.timezone == "auto"
    
    def test_invalid_latitude_too_high(self):
        """Test validation fails for latitude > 90."""
        with pytest.raises(ValidationError) as exc_info:
            WeatherInput(latitude=100, longitude=7.4474)
        assert "latitude" in str(exc_info.value).lower()
    
    def test_invalid_latitude_too_low(self):
        """Test validation fails for latitude < -90."""
        with pytest.raises(ValidationError) as exc_info:
            WeatherInput(latitude=-100, longitude=7.4474)
        assert "latitude" in str(exc_info.value).lower()
    
    def test_invalid_longitude_too_high(self):
        """Test validation fails for longitude > 180."""
        with pytest.raises(ValidationError) as exc_info:
            WeatherInput(latitude=46.9479, longitude=200)
        assert "longitude" in str(exc_info.value).lower()
    
    def test_invalid_longitude_too_low(self):
        """Test validation fails for longitude < -180."""
        with pytest.raises(ValidationError) as exc_info:
            WeatherInput(latitude=46.9479, longitude=-200)
        assert "longitude" in str(exc_info.value).lower()
    
    def test_invalid_forecast_days_too_low(self):
        """Test validation fails for forecast_days < 1."""
        with pytest.raises(ValidationError) as exc_info:
            WeatherInput(latitude=46.9479, longitude=7.4474, forecast_days=0)
        assert "forecast_days" in str(exc_info.value).lower()
    
    def test_invalid_forecast_days_too_high(self):
        """Test validation fails for forecast_days > 16."""
        with pytest.raises(ValidationError) as exc_info:
            WeatherInput(latitude=46.9479, longitude=7.4474, forecast_days=20)
        assert "forecast_days" in str(exc_info.value).lower()
    
    def test_empty_timezone(self):
        """Test validation fails for empty timezone."""
        with pytest.raises(ValidationError) as exc_info:
            WeatherInput(latitude=46.9479, longitude=7.4474, timezone="")
        assert "timezone" in str(exc_info.value).lower()


class TestSnowInput:
    """Test SnowInput model validation."""
    
    def test_valid_snow_input(self):
        """Test creating valid SnowInput."""
        input_data = SnowInput(
            latitude=45.9763,
            longitude=7.6586,
            forecast_days=7,
            include_hourly=True,
            timezone="Europe/Zurich"
        )
        assert input_data.latitude == 45.9763
        assert input_data.longitude == 7.6586
        assert input_data.forecast_days == 7
        assert input_data.timezone == "Europe/Zurich"
    
    def test_default_timezone(self):
        """Test default timezone is Europe/Zurich."""
        input_data = SnowInput(latitude=45.9763, longitude=7.6586)
        assert input_data.timezone == "Europe/Zurich"
    
    def test_coordinate_validation(self):
        """Test coordinate validation works for SnowInput."""
        with pytest.raises(ValidationError):
            SnowInput(latitude=100, longitude=7.6586)


class TestCurrentWeather:
    """Test CurrentWeather model."""
    
    def test_valid_current_weather(self):
        """Test creating valid CurrentWeather."""
        weather = CurrentWeather(
            temperature=15.2,
            windspeed=12.5,
            winddirection=180,
            weathercode=2,
            time="2026-01-09T09:00"
        )
        assert weather.temperature == 15.2
        assert weather.windspeed == 12.5
        assert weather.winddirection == 180
        assert weather.weathercode == 2
        assert weather.time == "2026-01-09T09:00"


class TestWeatherForecast:
    """Test WeatherForecast model."""
    
    def test_valid_weather_forecast(self):
        """Test creating valid WeatherForecast."""
        forecast = WeatherForecast(
            latitude=46.9479,
            longitude=7.4474,
            elevation=542.0,
            timezone="Europe/Zurich",
            timezone_abbreviation="CET",
            utc_offset_seconds=3600,
            current_weather=CurrentWeather(
                temperature=15.2,
                windspeed=12.5,
                winddirection=180,
                weathercode=2,
                time="2026-01-09T09:00"
            ),
            hourly=HourlyWeather(
                time=["2026-01-09T00:00", "2026-01-09T01:00"],
                temperature_2m=[14.5, 14.2],
                precipitation=[0.0, 0.0],
                weather_code=[2, 2],
                wind_speed_10m=[10.5, 11.2]
            ),
            daily=DailyWeather(
                time=["2026-01-09"],
                temperature_2m_max=[18.5],
                temperature_2m_min=[12.3],
                precipitation_sum=[0.0],
                weather_code=[2]
            )
        )
        assert forecast.latitude == 46.9479
        assert forecast.current_weather is not None
        assert forecast.current_weather.temperature == 15.2
        assert forecast.hourly is not None
        assert len(forecast.hourly.time) == 2
        assert forecast.daily is not None
        assert len(forecast.daily.time) == 1
    
    def test_minimal_weather_forecast(self):
        """Test WeatherForecast with only required fields."""
        forecast = WeatherForecast(
            latitude=46.9479,
            longitude=7.4474,
            timezone="Europe/Zurich"
        )
        assert forecast.latitude == 46.9479
        assert forecast.current_weather is None
        assert forecast.hourly is None
        assert forecast.daily is None


class TestSnowConditions:
    """Test SnowConditions model."""
    
    def test_valid_snow_conditions(self):
        """Test creating valid SnowConditions."""
        conditions = SnowConditions(
            latitude=45.9763,
            longitude=7.6586,
            elevation=1620.0,
            timezone="Europe/Zurich",
            hourly=HourlySnow(
                time=["2026-01-09T00:00", "2026-01-09T01:00"],
                temperature_2m=[-5.2, -5.8],
                snowfall=[0.5, 0.3],
                snow_depth=[1.2, 1.25],
                weather_code=[71, 71]
            ),
            daily=DailySnow(
                time=["2026-01-09"],
                temperature_2m_max=[-2.5],
                temperature_2m_min=[-8.3],
                snowfall_sum=[2.5]
            )
        )
        assert conditions.latitude == 45.9763
        assert conditions.hourly is not None
        assert len(conditions.hourly.time) == 2
        assert conditions.daily is not None
        assert conditions.daily.snowfall_sum[0] == 2.5


class TestModelSerialization:
    """Test model serialization and deserialization."""
    
    def test_weather_input_serialization(self):
        """Test WeatherInput can be serialized to dict."""
        input_data = WeatherInput(latitude=46.9479, longitude=7.4474)
        data_dict = input_data.model_dump()
        assert data_dict["latitude"] == 46.9479
        assert data_dict["longitude"] == 7.4474
        assert data_dict["forecast_days"] == 7
    
    def test_weather_forecast_from_dict(self):
        """Test WeatherForecast can be created from dict."""
        data = {
            "latitude": 46.9479,
            "longitude": 7.4474,
            "timezone": "Europe/Zurich",
            "current_weather": {
                "temperature": 15.2,
                "windspeed": 12.5,
                "winddirection": 180,
                "weathercode": 2,
                "time": "2026-01-09T09:00"
            }
        }
        forecast = WeatherForecast(**data)
        assert forecast.latitude == 46.9479
        assert forecast.current_weather.temperature == 15.2

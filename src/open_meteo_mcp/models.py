"""Pydantic models for Open-Meteo API requests and responses."""

from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from datetime import datetime


# Input Models
class WeatherInput(BaseModel):
    """Input parameters for weather forecast requests."""
    
    latitude: float = Field(..., ge=-90, le=90, description="Latitude in decimal degrees")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude in decimal degrees")
    forecast_days: int = Field(7, ge=1, le=16, description="Number of forecast days (1-16)")
    include_hourly: bool = Field(True, description="Include hourly forecast data")
    timezone: str = Field("auto", description="Timezone for timestamps (e.g., 'Europe/Zurich', 'auto')")
    
    @field_validator('timezone')
    @classmethod
    def validate_timezone(cls, v: str) -> str:
        """Validate timezone is not empty."""
        if not v or not v.strip():
            raise ValueError("Timezone cannot be empty")
        return v


class SnowInput(BaseModel):
    """Input parameters for snow conditions requests."""
    
    latitude: float = Field(..., ge=-90, le=90, description="Latitude in decimal degrees")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude in decimal degrees")
    forecast_days: int = Field(7, ge=1, le=16, description="Number of forecast days (1-16)")
    include_hourly: bool = Field(True, description="Include hourly data")
    timezone: str = Field("Europe/Zurich", description="Timezone for timestamps")
    
    @field_validator('timezone')
    @classmethod
    def validate_timezone(cls, v: str) -> str:
        """Validate timezone is not empty."""
        if not v or not v.strip():
            raise ValueError("Timezone cannot be empty")
        return v


# Response Models - Current Weather
class CurrentWeather(BaseModel):
    """Current weather conditions."""
    
    temperature: float = Field(..., description="Temperature in °C")
    windspeed: float = Field(..., description="Wind speed in km/h")
    winddirection: int = Field(..., description="Wind direction in degrees")
    weathercode: int = Field(..., description="WMO weather code")
    time: str = Field(..., description="Timestamp of observation")
    
    class Config:
        populate_by_name = True


# Response Models - Hourly Weather
class HourlyWeather(BaseModel):
    """Hourly weather forecast data."""
    
    time: List[str] = Field(default_factory=list, description="Timestamps for each hour")
    temperature_2m: List[float] = Field(default_factory=list, description="Temperature at 2m height (°C)")
    precipitation: List[float] = Field(default_factory=list, description="Precipitation (mm)")
    weather_code: List[int] = Field(default_factory=list, description="WMO weather codes")
    wind_speed_10m: List[float] = Field(default_factory=list, description="Wind speed at 10m (km/h)")
    relative_humidity_2m: Optional[List[int]] = Field(None, description="Relative humidity (%)")
    
    class Config:
        populate_by_name = True


# Response Models - Daily Weather
class DailyWeather(BaseModel):
    """Daily weather forecast data."""
    
    time: List[str] = Field(default_factory=list, description="Dates for each day")
    temperature_2m_max: List[float] = Field(default_factory=list, description="Maximum temperature (°C)")
    temperature_2m_min: List[float] = Field(default_factory=list, description="Minimum temperature (°C)")
    precipitation_sum: List[float] = Field(default_factory=list, description="Total precipitation (mm)")
    weather_code: List[int] = Field(default_factory=list, description="WMO weather codes")
    sunrise: Optional[List[str]] = Field(None, description="Sunrise times")
    sunset: Optional[List[str]] = Field(None, description="Sunset times")
    
    class Config:
        populate_by_name = True


# Response Models - Weather Forecast
class WeatherForecast(BaseModel):
    """Complete weather forecast response from Open-Meteo API."""
    
    latitude: float = Field(..., description="Latitude of the location")
    longitude: float = Field(..., description="Longitude of the location")
    elevation: Optional[float] = Field(None, description="Elevation in meters")
    timezone: str = Field(..., description="Timezone name")
    timezone_abbreviation: Optional[str] = Field(None, description="Timezone abbreviation")
    utc_offset_seconds: Optional[int] = Field(None, description="UTC offset in seconds")
    current_weather: Optional[CurrentWeather] = Field(None, description="Current weather conditions")
    hourly: Optional[HourlyWeather] = Field(None, description="Hourly forecast data")
    daily: Optional[DailyWeather] = Field(None, description="Daily forecast data")
    
    class Config:
        populate_by_name = True


# Response Models - Hourly Snow
class HourlySnow(BaseModel):
    """Hourly snow conditions data."""
    
    time: List[str] = Field(default_factory=list, description="Timestamps for each hour")
    temperature_2m: List[float] = Field(default_factory=list, description="Temperature at 2m (°C)")
    snowfall: List[float] = Field(default_factory=list, description="Snowfall amount (cm)")
    snow_depth: List[float] = Field(default_factory=list, description="Snow depth (m)")
    weather_code: List[int] = Field(default_factory=list, description="WMO weather codes")
    wind_speed_10m: Optional[List[float]] = Field(None, description="Wind speed at 10m (km/h)")
    
    class Config:
        populate_by_name = True


# Response Models - Daily Snow
class DailySnow(BaseModel):
    """Daily snow conditions data."""
    
    time: List[str] = Field(default_factory=list, description="Dates for each day")
    temperature_2m_max: List[float] = Field(default_factory=list, description="Maximum temperature (°C)")
    temperature_2m_min: List[float] = Field(default_factory=list, description="Minimum temperature (°C)")
    snowfall_sum: List[float] = Field(default_factory=list, description="Total snowfall (cm)")
    snow_depth_max: Optional[List[float]] = Field(None, description="Maximum snow depth (m)")
    
    class Config:
        populate_by_name = True


# Response Models - Snow Conditions
class SnowConditions(BaseModel):
    """Complete snow conditions response from Open-Meteo API."""
    
    latitude: float = Field(..., description="Latitude of the location")
    longitude: float = Field(..., description="Longitude of the location")
    elevation: Optional[float] = Field(None, description="Elevation in meters")
    timezone: str = Field(..., description="Timezone name")
    timezone_abbreviation: Optional[str] = Field(None, description="Timezone abbreviation")
    utc_offset_seconds: Optional[int] = Field(None, description="UTC offset in seconds")
    hourly: Optional[HourlySnow] = Field(None, description="Hourly snow data")
    daily: Optional[DailySnow] = Field(None, description="Daily snow data")
    
    class Config:
        populate_by_name = True

"""Pydantic models for Open-Meteo API requests and responses."""

from typing import Optional, List
from pydantic import BaseModel, Field, field_validator
from datetime import datetime


# Location Model
class Location(BaseModel):
    """Simple location with latitude and longitude."""

    latitude: float = Field(
        ..., ge=-90, le=90, description="Latitude in decimal degrees"
    )
    longitude: float = Field(
        ..., ge=-180, le=180, description="Longitude in decimal degrees"
    )


# Input Models
class WeatherInput(BaseModel):
    """Input parameters for weather forecast requests."""

    latitude: float = Field(
        ..., ge=-90, le=90, description="Latitude in decimal degrees"
    )
    longitude: float = Field(
        ..., ge=-180, le=180, description="Longitude in decimal degrees"
    )
    forecast_days: int = Field(
        7, ge=1, le=16, description="Number of forecast days (1-16)"
    )
    include_hourly: bool = Field(True, description="Include hourly forecast data")
    timezone: str = Field(
        "auto", description="Timezone for timestamps (e.g., 'Europe/Zurich', 'auto')"
    )

    @field_validator("timezone")
    @classmethod
    def validate_timezone(cls, v: str) -> str:
        """Validate timezone is not empty."""
        if not v or not v.strip():
            raise ValueError("Timezone cannot be empty")
        return v


class SnowInput(BaseModel):
    """Input parameters for snow conditions requests."""

    latitude: float = Field(
        ..., ge=-90, le=90, description="Latitude in decimal degrees"
    )
    longitude: float = Field(
        ..., ge=-180, le=180, description="Longitude in decimal degrees"
    )
    forecast_days: int = Field(
        7, ge=1, le=16, description="Number of forecast days (1-16)"
    )
    include_hourly: bool = Field(True, description="Include hourly data")
    timezone: str = Field("Europe/Zurich", description="Timezone for timestamps")

    @field_validator("timezone")
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

    time: List[str] = Field(
        default_factory=list, description="Timestamps for each hour"
    )
    temperature_2m: List[float] = Field(
        default_factory=list, description="Temperature at 2m height (°C)"
    )
    apparent_temperature: Optional[List[float]] = Field(
        None, description="Apparent temperature / feels like (°C)"
    )
    precipitation: List[float] = Field(
        default_factory=list, description="Precipitation (mm)"
    )
    precipitation_probability: Optional[List[int]] = Field(
        None, description="Precipitation probability (%)"
    )
    weather_code: List[int] = Field(
        default_factory=list, description="WMO weather codes"
    )
    wind_speed_10m: List[float] = Field(
        default_factory=list, description="Wind speed at 10m (km/h)"
    )
    wind_gusts_10m: Optional[List[float]] = Field(
        None, description="Wind gusts at 10m (km/h)"
    )
    relative_humidity_2m: Optional[List[int]] = Field(
        None, description="Relative humidity (%)"
    )
    cloud_cover: Optional[List[int]] = Field(None, description="Cloud cover (%)")
    visibility: Optional[List[float]] = Field(None, description="Visibility (m)")
    uv_index: Optional[List[float]] = Field(None, description="UV index")
    is_day: Optional[List[int]] = Field(None, description="Day (1) or night (0)")

    class Config:
        populate_by_name = True


# Response Models - Daily Weather
class DailyWeather(BaseModel):
    """Daily weather forecast data."""

    time: List[str] = Field(default_factory=list, description="Dates for each day")
    temperature_2m_max: List[float] = Field(
        default_factory=list, description="Maximum temperature (°C)"
    )
    temperature_2m_min: List[float] = Field(
        default_factory=list, description="Minimum temperature (°C)"
    )
    precipitation_sum: List[float] = Field(
        default_factory=list, description="Total precipitation (mm)"
    )
    precipitation_probability_max: Optional[List[int]] = Field(
        None, description="Maximum precipitation probability (%)"
    )
    precipitation_hours: Optional[List[float]] = Field(
        None, description="Hours with precipitation"
    )
    weather_code: List[int] = Field(
        default_factory=list, description="WMO weather codes"
    )
    sunrise: Optional[List[str]] = Field(None, description="Sunrise times")
    sunset: Optional[List[str]] = Field(None, description="Sunset times")
    uv_index_max: Optional[List[float]] = Field(None, description="Maximum UV index")
    wind_speed_10m_max: Optional[List[float]] = Field(
        None, description="Maximum wind speed (km/h)"
    )
    wind_gusts_10m_max: Optional[List[float]] = Field(
        None, description="Maximum wind gusts (km/h)"
    )

    class Config:
        populate_by_name = True


# Response Models - Weather Forecast
class WeatherForecast(BaseModel):
    """Complete weather forecast response from Open-Meteo API."""

    latitude: float = Field(..., description="Latitude of the location")
    longitude: float = Field(..., description="Longitude of the location")
    elevation: Optional[float] = Field(None, description="Elevation in meters")
    timezone: str = Field(..., description="Timezone name")
    timezone_abbreviation: Optional[str] = Field(
        None, description="Timezone abbreviation"
    )
    utc_offset_seconds: Optional[int] = Field(None, description="UTC offset in seconds")
    current_weather: Optional[CurrentWeather] = Field(
        None, description="Current weather conditions"
    )
    hourly: Optional[HourlyWeather] = Field(None, description="Hourly forecast data")
    daily: Optional[DailyWeather] = Field(None, description="Daily forecast data")

    class Config:
        populate_by_name = True


# Response Models - Hourly Snow
class HourlySnow(BaseModel):
    """Hourly snow conditions data."""

    time: List[str] = Field(
        default_factory=list, description="Timestamps for each hour"
    )
    temperature_2m: List[float] = Field(
        default_factory=list, description="Temperature at 2m (°C)"
    )
    apparent_temperature: Optional[List[float]] = Field(
        None, description="Apparent temperature / wind chill (°C)"
    )
    snowfall: List[float] = Field(
        default_factory=list, description="Snowfall amount (cm)"
    )
    snow_depth: List[float] = Field(default_factory=list, description="Snow depth (m)")
    weather_code: List[int] = Field(
        default_factory=list, description="WMO weather codes"
    )
    wind_speed_10m: Optional[List[float]] = Field(
        None, description="Wind speed at 10m (km/h)"
    )
    wind_gusts_10m: Optional[List[float]] = Field(
        None, description="Wind gusts at 10m (km/h)"
    )
    cloud_cover: Optional[List[int]] = Field(None, description="Cloud cover (%)")
    precipitation_probability: Optional[List[int]] = Field(
        None, description="Precipitation probability (%)"
    )

    class Config:
        populate_by_name = True


# Response Models - Daily Snow
class DailySnow(BaseModel):
    """Daily snow conditions data."""

    time: List[str] = Field(default_factory=list, description="Dates for each day")
    temperature_2m_max: List[float] = Field(
        default_factory=list, description="Maximum temperature (°C)"
    )
    temperature_2m_min: List[float] = Field(
        default_factory=list, description="Minimum temperature (°C)"
    )
    snowfall_sum: List[float] = Field(
        default_factory=list, description="Total snowfall (cm)"
    )
    snow_depth_max: Optional[List[float]] = Field(
        None, description="Maximum snow depth (m)"
    )
    precipitation_probability_max: Optional[List[int]] = Field(
        None, description="Maximum precipitation probability (%)"
    )
    wind_gusts_10m_max: Optional[List[float]] = Field(
        None, description="Maximum wind gusts (km/h)"
    )

    class Config:
        populate_by_name = True


# Response Models - Snow Conditions
# Response Models - Geocoding
class GeocodingResult(BaseModel):
    """Single geocoding search result."""

    id: Optional[int] = Field(None, description="Location ID")
    name: str = Field(..., description="Location name")
    latitude: float = Field(..., description="Latitude in decimal degrees")
    longitude: float = Field(..., description="Longitude in decimal degrees")
    elevation: Optional[float] = Field(None, description="Elevation in meters")
    feature_code: Optional[str] = Field(None, description="GeoNames feature code")
    country_code: Optional[str] = Field(
        None, description="ISO 3166-1 alpha-2 country code"
    )
    country: Optional[str] = Field(None, description="Country name")
    country_id: Optional[int] = Field(None, description="Country ID")
    timezone: Optional[str] = Field(None, description="Timezone name")
    population: Optional[int] = Field(None, description="Population")
    admin1: Optional[str] = Field(
        None, description="First-level administrative division"
    )
    admin2: Optional[str] = Field(
        None, description="Second-level administrative division"
    )
    admin3: Optional[str] = Field(
        None, description="Third-level administrative division"
    )
    admin4: Optional[str] = Field(
        None, description="Fourth-level administrative division"
    )
    admin1_id: Optional[int] = Field(None, description="Admin1 ID")
    admin2_id: Optional[int] = Field(None, description="Admin2 ID")
    admin3_id: Optional[int] = Field(None, description="Admin3 ID")
    admin4_id: Optional[int] = Field(None, description="Admin4 ID")

    class Config:
        populate_by_name = True


class GeocodingResponse(BaseModel):
    """Response from geocoding search API."""

    results: Optional[List[GeocodingResult]] = Field(
        None, description="List of matching locations"
    )
    generationtime_ms: Optional[float] = Field(
        None, description="API generation time in milliseconds"
    )

    class Config:
        populate_by_name = True


# Response Models - Air Quality
class CurrentAirQuality(BaseModel):
    """Current air quality conditions."""

    time: Optional[str] = Field(None, description="Timestamp of observation")
    european_aqi: Optional[int] = Field(
        None, description="European Air Quality Index (0-100+)"
    )
    us_aqi: Optional[int] = Field(
        None, description="United States Air Quality Index (0-500)"
    )
    pm10: Optional[float] = Field(None, description="Particulate matter PM10 (μg/m³)")
    pm2_5: Optional[float] = Field(None, description="Particulate matter PM2.5 (μg/m³)")
    uv_index: Optional[float] = Field(None, description="UV index")

    class Config:
        populate_by_name = True


class HourlyAirQuality(BaseModel):
    """Hourly air quality forecast data."""

    time: List[str] = Field(
        default_factory=list, description="Timestamps for each hour"
    )
    european_aqi: Optional[List[int]] = Field(
        None, description="European Air Quality Index"
    )
    us_aqi: Optional[List[int]] = Field(
        None, description="United States Air Quality Index"
    )
    pm10: Optional[List[float]] = Field(
        None, description="Particulate matter PM10 (μg/m³)"
    )
    pm2_5: Optional[List[float]] = Field(
        None, description="Particulate matter PM2.5 (μg/m³)"
    )
    carbon_monoxide: Optional[List[float]] = Field(
        None, description="Carbon monoxide (μg/m³)"
    )
    nitrogen_dioxide: Optional[List[float]] = Field(
        None, description="Nitrogen dioxide (μg/m³)"
    )
    sulphur_dioxide: Optional[List[float]] = Field(
        None, description="Sulphur dioxide (μg/m³)"
    )
    ozone: Optional[List[float]] = Field(None, description="Ozone (μg/m³)")
    dust: Optional[List[float]] = Field(None, description="Dust (μg/m³)")
    uv_index: Optional[List[float]] = Field(None, description="UV index")
    uv_index_clear_sky: Optional[List[float]] = Field(
        None, description="UV index under clear sky"
    )
    ammonia: Optional[List[float]] = Field(None, description="Ammonia (μg/m³)")
    alder_pollen: Optional[List[float]] = Field(
        None, description="Alder pollen (grains/m³)"
    )
    birch_pollen: Optional[List[float]] = Field(
        None, description="Birch pollen (grains/m³)"
    )
    grass_pollen: Optional[List[float]] = Field(
        None, description="Grass pollen (grains/m³)"
    )
    mugwort_pollen: Optional[List[float]] = Field(
        None, description="Mugwort pollen (grains/m³)"
    )
    olive_pollen: Optional[List[float]] = Field(
        None, description="Olive pollen (grains/m³)"
    )
    ragweed_pollen: Optional[List[float]] = Field(
        None, description="Ragweed pollen (grains/m³)"
    )

    class Config:
        populate_by_name = True


class AirQualityForecast(BaseModel):
    """Complete air quality forecast response from Open-Meteo API."""

    latitude: float = Field(..., description="Latitude of the location")
    longitude: float = Field(..., description="Longitude of the location")
    elevation: Optional[float] = Field(None, description="Elevation in meters")
    timezone: str = Field(..., description="Timezone name")
    timezone_abbreviation: Optional[str] = Field(
        None, description="Timezone abbreviation"
    )
    utc_offset_seconds: Optional[int] = Field(None, description="UTC offset in seconds")
    current: Optional[CurrentAirQuality] = Field(
        None, description="Current air quality"
    )
    hourly: Optional[HourlyAirQuality] = Field(
        None, description="Hourly air quality forecast"
    )

    class Config:
        populate_by_name = True


# Response Models - Snow Conditions
class SnowConditions(BaseModel):
    """Complete snow conditions response from Open-Meteo API."""

    latitude: float = Field(..., description="Latitude of the location")
    longitude: float = Field(..., description="Longitude of the location")
    elevation: Optional[float] = Field(None, description="Elevation in meters")
    timezone: str = Field(..., description="Timezone name")
    timezone_abbreviation: Optional[str] = Field(
        None, description="Timezone abbreviation"
    )
    utc_offset_seconds: Optional[int] = Field(None, description="UTC offset in seconds")
    hourly: Optional[HourlySnow] = Field(None, description="Hourly snow data")
    daily: Optional[DailySnow] = Field(None, description="Daily snow data")

    class Config:
        populate_by_name = True


# Response Models - Marine Conditions
class HourlyMarine(BaseModel):
    """Hourly marine conditions data."""

    time: List[str] = Field(
        default_factory=list, description="Timestamps for each hour"
    )
    wave_height: Optional[List[float]] = Field(None, description="Wave height (m)")
    wave_direction: Optional[List[int]] = Field(
        None, description="Wave direction (degrees)"
    )
    wave_period: Optional[List[float]] = Field(
        None, description="Wave period (seconds)"
    )
    wind_wave_height: Optional[List[float]] = Field(
        None, description="Wind wave height (m)"
    )
    wind_wave_direction: Optional[List[int]] = Field(
        None, description="Wind wave direction (degrees)"
    )
    wind_wave_period: Optional[List[float]] = Field(
        None, description="Wind wave period (seconds)"
    )
    swell_wave_height: Optional[List[float]] = Field(
        None, description="Swell wave height (m)"
    )
    swell_wave_direction: Optional[List[int]] = Field(
        None, description="Swell wave direction (degrees)"
    )
    swell_wave_period: Optional[List[float]] = Field(
        None, description="Swell wave period (seconds)"
    )

    class Config:
        populate_by_name = True


class DailyMarine(BaseModel):
    """Daily marine conditions data."""

    time: List[str] = Field(default_factory=list, description="Dates for each day")
    wave_height_max: Optional[List[float]] = Field(
        None, description="Maximum wave height (m)"
    )
    wave_direction_dominant: Optional[List[int]] = Field(
        None, description="Dominant wave direction (degrees)"
    )
    wave_period_max: Optional[List[float]] = Field(
        None, description="Maximum wave period (seconds)"
    )
    swell_wave_height_max: Optional[List[float]] = Field(
        None, description="Maximum swell wave height (m)"
    )
    swell_wave_direction_dominant: Optional[List[int]] = Field(
        None, description="Dominant swell wave direction (degrees)"
    )
    swell_wave_period_max: Optional[List[float]] = Field(
        None, description="Maximum swell wave period (seconds)"
    )

    class Config:
        populate_by_name = True


class MarineConditions(BaseModel):
    """Complete marine conditions response from Open-Meteo Marine API."""

    latitude: float = Field(..., description="Latitude of the location")
    longitude: float = Field(..., description="Longitude of the location")
    elevation: Optional[float] = Field(None, description="Elevation in meters")
    timezone: str = Field(..., description="Timezone name")
    timezone_abbreviation: Optional[str] = Field(
        None, description="Timezone abbreviation"
    )
    utc_offset_seconds: Optional[int] = Field(None, description="UTC offset in seconds")
    hourly: Optional[HourlyMarine] = Field(None, description="Hourly marine data")
    daily: Optional[DailyMarine] = Field(None, description="Daily marine data")

    class Config:
        populate_by_name = True


# Response Models - Weather Alerts
class WeatherAlert(BaseModel):
    """Weather alert/warning data."""

    type: str = Field(
        ..., description="Alert type: storm, heat, cold, uv, wind, air_quality"
    )
    severity: str = Field(..., description="Alert severity: advisory, watch, warning")
    start: str = Field(..., description="Alert start time (ISO format)")
    end: str = Field(..., description="Alert end time (ISO format)")
    description: str = Field(..., description="Alert description")
    recommendations: List[str] = Field(
        default_factory=list, description="Safety recommendations"
    )


class WeatherAlertsResponse(BaseModel):
    """Response containing weather alerts for a location."""

    latitude: float = Field(..., description="Latitude of the location")
    longitude: float = Field(..., description="Longitude of the location")
    timezone: str = Field(..., description="Timezone name")
    alerts: List[WeatherAlert] = Field(
        default_factory=list, description="List of active alerts"
    )

    class Config:
        populate_by_name = True

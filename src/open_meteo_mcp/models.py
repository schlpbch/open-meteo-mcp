"""Pydantic models for Open-Meteo API requests and responses."""

from pydantic import BaseModel, ConfigDict, Field, field_validator


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

    model_config = ConfigDict(populate_by_name=True)

    temperature: float = Field(..., description="Temperature in °C")
    windspeed: float = Field(..., description="Wind speed in km/h")
    winddirection: int = Field(..., description="Wind direction in degrees")
    weathercode: int = Field(..., description="WMO weather code")
    time: str = Field(..., description="Timestamp of observation")


# Response Models - Hourly Weather
class HourlyWeather(BaseModel):
    """Hourly weather forecast data."""

    model_config = ConfigDict(populate_by_name=True)

    time: list[str] = Field(
        default_factory=list, description="Timestamps for each hour"
    )
    temperature_2m: list[float] = Field(
        default_factory=list, description="Temperature at 2m height (°C)"
    )
    apparent_temperature: list[float] | None = Field(
        None, description="Apparent temperature / feels like (°C)"
    )
    precipitation: list[float] = Field(
        default_factory=list, description="Precipitation (mm)"
    )
    precipitation_probability: list[int] | None = Field(
        None, description="Precipitation probability (%)"
    )
    weather_code: list[int] = Field(
        default_factory=list, description="WMO weather codes"
    )
    wind_speed_10m: list[float] = Field(
        default_factory=list, description="Wind speed at 10m (km/h)"
    )
    wind_gusts_10m: list[float] | None = Field(
        None, description="Wind gusts at 10m (km/h)"
    )
    relative_humidity_2m: list[int] | None = Field(
        None, description="Relative humidity (%)"
    )
    cloud_cover: list[int] | None = Field(None, description="Cloud cover (%)")
    visibility: list[float] | None = Field(None, description="Visibility (m)")
    uv_index: list[float] | None = Field(None, description="UV index")
    is_day: list[int] | None = Field(None, description="Day (1) or night (0)")


# Response Models - Daily Weather
class DailyWeather(BaseModel):
    """Daily weather forecast data."""

    model_config = ConfigDict(populate_by_name=True)

    time: list[str] = Field(default_factory=list, description="Dates for each day")
    temperature_2m_max: list[float] = Field(
        default_factory=list, description="Maximum temperature (°C)"
    )
    temperature_2m_min: list[float] = Field(
        default_factory=list, description="Minimum temperature (°C)"
    )
    precipitation_sum: list[float] = Field(
        default_factory=list, description="Total precipitation (mm)"
    )
    precipitation_probability_max: list[int] | None = Field(
        None, description="Maximum precipitation probability (%)"
    )
    precipitation_hours: list[float] | None = Field(
        None, description="Hours with precipitation"
    )
    weather_code: list[int] = Field(
        default_factory=list, description="WMO weather codes"
    )
    sunrise: list[str] | None = Field(None, description="Sunrise times")
    sunset: list[str] | None = Field(None, description="Sunset times")
    uv_index_max: list[float] | None = Field(None, description="Maximum UV index")
    wind_speed_10m_max: list[float] | None = Field(
        None, description="Maximum wind speed (km/h)"
    )
    wind_gusts_10m_max: list[float] | None = Field(
        None, description="Maximum wind gusts (km/h)"
    )


# Response Models - Weather Forecast
class WeatherForecast(BaseModel):
    """Complete weather forecast response from Open-Meteo API."""

    model_config = ConfigDict(populate_by_name=True)

    latitude: float = Field(..., description="Latitude of the location")
    longitude: float = Field(..., description="Longitude of the location")
    elevation: float | None = Field(None, description="Elevation in meters")
    timezone: str = Field(..., description="Timezone name")
    timezone_abbreviation: str | None = Field(None, description="Timezone abbreviation")
    utc_offset_seconds: int | None = Field(None, description="UTC offset in seconds")
    current_weather: CurrentWeather | None = Field(
        None, description="Current weather conditions"
    )
    hourly: HourlyWeather | None = Field(None, description="Hourly forecast data")
    daily: DailyWeather | None = Field(None, description="Daily forecast data")


# Response Models - Hourly Snow
class HourlySnow(BaseModel):
    """Hourly snow conditions data."""

    model_config = ConfigDict(populate_by_name=True)

    time: list[str] = Field(
        default_factory=list, description="Timestamps for each hour"
    )
    temperature_2m: list[float] = Field(
        default_factory=list, description="Temperature at 2m (°C)"
    )
    apparent_temperature: list[float] | None = Field(
        None, description="Apparent temperature / wind chill (°C)"
    )
    snowfall: list[float] = Field(
        default_factory=list, description="Snowfall amount (cm)"
    )
    snow_depth: list[float] = Field(default_factory=list, description="Snow depth (m)")
    weather_code: list[int] = Field(
        default_factory=list, description="WMO weather codes"
    )
    wind_speed_10m: list[float] | None = Field(
        None, description="Wind speed at 10m (km/h)"
    )
    wind_gusts_10m: list[float] | None = Field(
        None, description="Wind gusts at 10m (km/h)"
    )
    cloud_cover: list[int] | None = Field(None, description="Cloud cover (%)")
    precipitation_probability: list[int] | None = Field(
        None, description="Precipitation probability (%)"
    )


# Response Models - Daily Snow
class DailySnow(BaseModel):
    """Daily snow conditions data."""

    model_config = ConfigDict(populate_by_name=True)

    time: list[str] = Field(default_factory=list, description="Dates for each day")
    temperature_2m_max: list[float] = Field(
        default_factory=list, description="Maximum temperature (°C)"
    )
    temperature_2m_min: list[float] = Field(
        default_factory=list, description="Minimum temperature (°C)"
    )
    snowfall_sum: list[float] = Field(
        default_factory=list, description="Total snowfall (cm)"
    )
    snow_depth_max: list[float] | None = Field(
        None, description="Maximum snow depth (m)"
    )
    precipitation_probability_max: list[int] | None = Field(
        None, description="Maximum precipitation probability (%)"
    )
    wind_gusts_10m_max: list[float] | None = Field(
        None, description="Maximum wind gusts (km/h)"
    )


# Response Models - Snow Conditions
# Response Models - Geocoding
class GeocodingResult(BaseModel):
    """Single geocoding search result."""

    model_config = ConfigDict(populate_by_name=True)

    id: int | None = Field(None, description="Location ID")
    name: str = Field(..., description="Location name")
    latitude: float = Field(..., description="Latitude in decimal degrees")
    longitude: float = Field(..., description="Longitude in decimal degrees")
    elevation: float | None = Field(None, description="Elevation in meters")
    feature_code: str | None = Field(None, description="GeoNames feature code")
    country_code: str | None = Field(
        None, description="ISO 3166-1 alpha-2 country code"
    )
    country: str | None = Field(None, description="Country name")
    country_id: int | None = Field(None, description="Country ID")
    timezone: str | None = Field(None, description="Timezone name")
    population: int | None = Field(None, description="Population")
    admin1: str | None = Field(None, description="First-level administrative division")
    admin2: str | None = Field(None, description="Second-level administrative division")
    admin3: str | None = Field(None, description="Third-level administrative division")
    admin4: str | None = Field(None, description="Fourth-level administrative division")
    admin1_id: int | None = Field(None, description="Admin1 ID")
    admin2_id: int | None = Field(None, description="Admin2 ID")
    admin3_id: int | None = Field(None, description="Admin3 ID")
    admin4_id: int | None = Field(None, description="Admin4 ID")


class GeocodingResponse(BaseModel):
    """Response from geocoding search API."""

    model_config = ConfigDict(populate_by_name=True)

    results: list[GeocodingResult] | None = Field(
        None, description="List of matching locations"
    )
    generationtime_ms: float | None = Field(
        None, description="API generation time in milliseconds"
    )


# Response Models - Air Quality
class CurrentAirQuality(BaseModel):
    """Current air quality conditions."""

    model_config = ConfigDict(populate_by_name=True)

    time: str | None = Field(None, description="Timestamp of observation")
    european_aqi: int | None = Field(
        None, description="European Air Quality Index (0-100+)"
    )
    us_aqi: int | None = Field(
        None, description="United States Air Quality Index (0-500)"
    )
    pm10: float | None = Field(None, description="Particulate matter PM10 (μg/m³)")
    pm2_5: float | None = Field(None, description="Particulate matter PM2.5 (μg/m³)")
    uv_index: float | None = Field(None, description="UV index")


class HourlyAirQuality(BaseModel):
    """Hourly air quality forecast data."""

    model_config = ConfigDict(populate_by_name=True)

    time: list[str] = Field(
        default_factory=list, description="Timestamps for each hour"
    )
    european_aqi: list[int] | None = Field(
        None, description="European Air Quality Index"
    )
    us_aqi: list[int] | None = Field(
        None, description="United States Air Quality Index"
    )
    pm10: list[float] | None = Field(
        None, description="Particulate matter PM10 (μg/m³)"
    )
    pm2_5: list[float] | None = Field(
        None, description="Particulate matter PM2.5 (μg/m³)"
    )
    carbon_monoxide: list[float] | None = Field(
        None, description="Carbon monoxide (μg/m³)"
    )
    nitrogen_dioxide: list[float] | None = Field(
        None, description="Nitrogen dioxide (μg/m³)"
    )
    sulphur_dioxide: list[float] | None = Field(
        None, description="Sulphur dioxide (μg/m³)"
    )
    ozone: list[float] | None = Field(None, description="Ozone (μg/m³)")
    dust: list[float] | None = Field(None, description="Dust (μg/m³)")
    uv_index: list[float] | None = Field(None, description="UV index")
    uv_index_clear_sky: list[float] | None = Field(
        None, description="UV index under clear sky"
    )
    ammonia: list[float] | None = Field(None, description="Ammonia (μg/m³)")
    alder_pollen: list[float] | None = Field(
        None, description="Alder pollen (grains/m³)"
    )
    birch_pollen: list[float] | None = Field(
        None, description="Birch pollen (grains/m³)"
    )
    grass_pollen: list[float] | None = Field(
        None, description="Grass pollen (grains/m³)"
    )
    mugwort_pollen: list[float] | None = Field(
        None, description="Mugwort pollen (grains/m³)"
    )
    olive_pollen: list[float] | None = Field(
        None, description="Olive pollen (grains/m³)"
    )
    ragweed_pollen: list[float] | None = Field(
        None, description="Ragweed pollen (grains/m³)"
    )


class AirQualityForecast(BaseModel):
    """Complete air quality forecast response from Open-Meteo API."""

    model_config = ConfigDict(populate_by_name=True)

    latitude: float = Field(..., description="Latitude of the location")
    longitude: float = Field(..., description="Longitude of the location")
    elevation: float | None = Field(None, description="Elevation in meters")
    timezone: str = Field(..., description="Timezone name")
    timezone_abbreviation: str | None = Field(None, description="Timezone abbreviation")
    utc_offset_seconds: int | None = Field(None, description="UTC offset in seconds")
    current: CurrentAirQuality | None = Field(None, description="Current air quality")
    hourly: HourlyAirQuality | None = Field(
        None, description="Hourly air quality forecast"
    )


# Response Models - Snow Conditions
class SnowConditions(BaseModel):
    """Complete snow conditions response from Open-Meteo API."""

    model_config = ConfigDict(populate_by_name=True)

    latitude: float = Field(..., description="Latitude of the location")
    longitude: float = Field(..., description="Longitude of the location")
    elevation: float | None = Field(None, description="Elevation in meters")
    timezone: str = Field(..., description="Timezone name")
    timezone_abbreviation: str | None = Field(None, description="Timezone abbreviation")
    utc_offset_seconds: int | None = Field(None, description="UTC offset in seconds")
    hourly: HourlySnow | None = Field(None, description="Hourly snow data")
    daily: DailySnow | None = Field(None, description="Daily snow data")


# Response Models - Marine Conditions
class HourlyMarine(BaseModel):
    """Hourly marine conditions data."""

    model_config = ConfigDict(populate_by_name=True)

    time: list[str] = Field(
        default_factory=list, description="Timestamps for each hour"
    )
    wave_height: list[float] | None = Field(None, description="Wave height (m)")
    wave_direction: list[int] | None = Field(
        None, description="Wave direction (degrees)"
    )
    wave_period: list[float] | None = Field(None, description="Wave period (seconds)")
    wind_wave_height: list[float] | None = Field(
        None, description="Wind wave height (m)"
    )
    wind_wave_direction: list[int] | None = Field(
        None, description="Wind wave direction (degrees)"
    )
    wind_wave_period: list[float] | None = Field(
        None, description="Wind wave period (seconds)"
    )
    swell_wave_height: list[float] | None = Field(
        None, description="Swell wave height (m)"
    )
    swell_wave_direction: list[int] | None = Field(
        None, description="Swell wave direction (degrees)"
    )
    swell_wave_period: list[float] | None = Field(
        None, description="Swell wave period (seconds)"
    )


class DailyMarine(BaseModel):
    """Daily marine conditions data."""

    model_config = ConfigDict(populate_by_name=True)

    time: list[str] = Field(default_factory=list, description="Dates for each day")
    wave_height_max: list[float] | None = Field(
        None, description="Maximum wave height (m)"
    )
    wave_direction_dominant: list[int] | None = Field(
        None, description="Dominant wave direction (degrees)"
    )
    wave_period_max: list[float] | None = Field(
        None, description="Maximum wave period (seconds)"
    )
    swell_wave_height_max: list[float] | None = Field(
        None, description="Maximum swell wave height (m)"
    )
    swell_wave_direction_dominant: list[int] | None = Field(
        None, description="Dominant swell wave direction (degrees)"
    )
    swell_wave_period_max: list[float] | None = Field(
        None, description="Maximum swell wave period (seconds)"
    )


class MarineConditions(BaseModel):
    """Complete marine conditions response from Open-Meteo Marine API."""

    model_config = ConfigDict(populate_by_name=True)

    latitude: float = Field(..., description="Latitude of the location")
    longitude: float = Field(..., description="Longitude of the location")
    elevation: float | None = Field(None, description="Elevation in meters")
    timezone: str = Field(..., description="Timezone name")
    timezone_abbreviation: str | None = Field(None, description="Timezone abbreviation")
    utc_offset_seconds: int | None = Field(None, description="UTC offset in seconds")
    hourly: HourlyMarine | None = Field(None, description="Hourly marine data")
    daily: DailyMarine | None = Field(None, description="Daily marine data")


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
    recommendations: list[str] = Field(
        default_factory=list, description="Safety recommendations"
    )


class WeatherAlertsResponse(BaseModel):
    """Response containing weather alerts for a location."""

    model_config = ConfigDict(populate_by_name=True)

    latitude: float = Field(..., description="Latitude of the location")
    longitude: float = Field(..., description="Longitude of the location")
    timezone: str = Field(..., description="Timezone name")
    alerts: list[WeatherAlert] = Field(
        default_factory=list, description="List of active alerts"
    )

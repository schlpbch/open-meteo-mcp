"""Async HTTP client for Open-Meteo Weather API."""

import httpx
import structlog
from typing import Optional
from .models import WeatherForecast, SnowConditions

logger = structlog.get_logger()


class OpenMeteoClient:
    """
    Client for the Open-Meteo Weather API.
    
    Open-Meteo is a free, open-source weather API that provides:
    - Current weather conditions
    - Hourly forecasts (up to 16 days)
    - Daily forecasts
    - Historical weather data
    
    API Documentation: https://open-meteo.com/en/docs
    No API key required. Free for non-commercial use.
    """
    
    BASE_URL = "https://api.open-meteo.com/v1"
    
    def __init__(self, timeout: float = 30.0):
        """
        Initialize the Open-Meteo API client.
        
        Args:
            timeout: Request timeout in seconds (default: 30.0)
        """
        self.client = httpx.AsyncClient(
            base_url=self.BASE_URL,
            timeout=timeout,
            follow_redirects=True,
            headers={"User-Agent": "open-meteo-mcp/2.0.0"}
        )
        self.logger = logger.bind(component="OpenMeteoClient")
    
    async def get_weather(
        self,
        latitude: float,
        longitude: float,
        forecast_days: int = 7,
        include_hourly: bool = True,
        timezone: str = "auto"
    ) -> WeatherForecast:
        """
        Get current weather and forecast for a location.
        
        Args:
            latitude: Latitude in decimal degrees (e.g., 46.9479 for Bern)
            longitude: Longitude in decimal degrees (e.g., 7.4474 for Bern)
            forecast_days: Number of forecast days (1-16, default: 7)
            include_hourly: Include hourly forecast data (default: True)
            timezone: Timezone for timestamps (e.g., 'Europe/Zurich', default: 'auto')
        
        Returns:
            WeatherForecast object with current conditions and forecast data
        
        Raises:
            httpx.HTTPError: If the API request fails
            ValueError: If the response cannot be parsed
        """
        self.logger.debug(
            "fetching_weather",
            latitude=latitude,
            longitude=longitude,
            forecast_days=forecast_days
        )
        
        # Build query parameters
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "forecast_days": min(max(forecast_days, 1), 16),  # Clamp to 1-16
            "timezone": timezone,
            "current_weather": True,
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,precipitation_probability_max,precipitation_hours,weather_code,sunrise,sunset,uv_index_max,wind_speed_10m_max,wind_gusts_10m_max"
        }
        
        if include_hourly:
            params["hourly"] = "temperature_2m,apparent_temperature,precipitation,precipitation_probability,weather_code,wind_speed_10m,wind_gusts_10m,relative_humidity_2m,cloud_cover,visibility,uv_index,is_day"
        
        try:
            response = await self.client.get("/forecast", params=params)
            response.raise_for_status()
            
            data = response.json()
            self.logger.debug("weather_fetched_successfully", latitude=latitude, longitude=longitude)
            
            return WeatherForecast(**data)
            
        except httpx.HTTPStatusError as e:
            self.logger.error(
                "weather_api_http_error",
                status_code=e.response.status_code,
                error=str(e)
            )
            raise
        except httpx.HTTPError as e:
            self.logger.error("weather_api_request_error", error=str(e))
            raise
        except Exception as e:
            self.logger.error("weather_api_unexpected_error", error=str(e))
            raise ValueError(f"Failed to parse weather data: {e}") from e
    
    async def get_snow_conditions(
        self,
        latitude: float,
        longitude: float,
        forecast_days: int = 7,
        include_hourly: bool = True,
        timezone: str = "Europe/Zurich"
    ) -> SnowConditions:
        """
        Get snow conditions and forecasts for mountain locations.
        
        Args:
            latitude: Latitude in decimal degrees (e.g., 45.9763 for Zermatt)
            longitude: Longitude in decimal degrees (e.g., 7.6586 for Zermatt)
            forecast_days: Number of forecast days (1-16, default: 7)
            include_hourly: Include hourly data (default: True)
            timezone: Timezone for timestamps (default: 'Europe/Zurich')
        
        Returns:
            SnowConditions object with snow depth, snowfall, and forecast data
        
        Raises:
            httpx.HTTPError: If the API request fails
            ValueError: If the response cannot be parsed
        """
        self.logger.debug(
            "fetching_snow_conditions",
            latitude=latitude,
            longitude=longitude,
            forecast_days=forecast_days
        )
        
        # Build query parameters
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "forecast_days": min(max(forecast_days, 1), 16),  # Clamp to 1-16
            "timezone": timezone,
            "daily": "snowfall_sum,snow_depth_max,temperature_2m_max,temperature_2m_min,precipitation_probability_max,wind_gusts_10m_max"
        }
        
        if include_hourly:
            params["hourly"] = "snowfall,snow_depth,temperature_2m,apparent_temperature,weather_code,wind_speed_10m,wind_gusts_10m,cloud_cover,precipitation_probability"
        
        try:
            response = await self.client.get("/forecast", params=params)
            response.raise_for_status()
            
            data = response.json()
            self.logger.debug("snow_conditions_fetched_successfully", latitude=latitude, longitude=longitude)
            
            return SnowConditions(**data)
            
        except httpx.HTTPStatusError as e:
            self.logger.error(
                "snow_api_http_error",
                status_code=e.response.status_code,
                error=str(e)
            )
            raise
        except httpx.HTTPError as e:
            self.logger.error("snow_api_request_error", error=str(e))
            raise
        except Exception as e:
            self.logger.error("snow_api_unexpected_error", error=str(e))
            raise ValueError(f"Failed to parse snow data: {e}") from e
    
    async def get_air_quality(
        self,
        latitude: float,
        longitude: float,
        forecast_days: int = 5,
        include_pollen: bool = True
    ) -> "AirQualityForecast":
        """
        Get air quality forecast for a location.
        
        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            forecast_days: Number of forecast days (1-5, default: 5)
            include_pollen: Include pollen data (Europe only, default: True)
        
        Returns:
            AirQualityForecast with AQI, pollutants, UV index, and pollen data
        
        Raises:
            httpx.HTTPError: If the API request fails
            ValueError: If the response cannot be parsed
        """
        from .models import AirQualityForecast
        
        self.logger.debug(
            "fetching_air_quality",
            latitude=latitude,
            longitude=longitude,
            forecast_days=forecast_days
        )
        
        # Build hourly parameters
        hourly_params = [
            "european_aqi", "us_aqi",
            "pm10", "pm2_5",
            "carbon_monoxide", "nitrogen_dioxide", "sulphur_dioxide", "ozone",
            "dust", "uv_index", "uv_index_clear_sky", "ammonia"
        ]
        
        # Add pollen data if requested (Europe only)
        if include_pollen:
            hourly_params.extend([
                "alder_pollen", "birch_pollen", "grass_pollen",
                "mugwort_pollen", "olive_pollen", "ragweed_pollen"
            ])
        
        # Build query parameters
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "forecast_days": min(max(forecast_days, 1), 5),  # Clamp to 1-5
            "current": "european_aqi,us_aqi,pm10,pm2_5,uv_index",
            "hourly": ",".join(hourly_params)
        }
        
        try:
            # Use air quality API base URL
            air_quality_url = "https://air-quality-api.open-meteo.com/v1/air-quality"
            response = await self.client.get(air_quality_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            self.logger.debug("air_quality_fetched_successfully", latitude=latitude, longitude=longitude)
            
            return AirQualityForecast(**data)
            
        except httpx.HTTPStatusError as e:
            self.logger.error(
                "air_quality_api_http_error",
                status_code=e.response.status_code,
                error=str(e)
            )
            raise
        except httpx.HTTPError as e:
            self.logger.error("air_quality_api_request_error", error=str(e))
            raise
        except Exception as e:
            self.logger.error("air_quality_api_unexpected_error", error=str(e))
            raise ValueError(f"Failed to parse air quality data: {e}") from e
    
    async def search_location(
        self,
        name: str,
        count: int = 10,
        language: str = "en",
        country: Optional[str] = None
    ) -> "GeocodingResponse":
        """
        Search for locations by name using geocoding API.
        
        Args:
            name: Location name to search (e.g., "Zurich", "Bern", "Zermatt")
            count: Number of results to return (1-100, default: 10)
            language: Language for results (default: "en")
            country: Optional ISO 3166-1 alpha-2 country code filter (e.g., "CH" for Switzerland)
        
        Returns:
            GeocodingResponse with list of matching locations
        
        Raises:
            httpx.HTTPError: If the API request fails
            ValueError: If the response cannot be parsed
        """
        from .models import GeocodingResponse
        
        self.logger.debug(
            "searching_location",
            name=name,
            count=count,
            language=language,
            country=country
        )
        
        # Build query parameters
        params = {
            "name": name,
            "count": min(max(count, 1), 100),  # Clamp to 1-100
            "language": language,
            "format": "json"
        }
        
        if country:
            params["country"] = country
        
        try:
            # Use geocoding API base URL
            geocoding_url = "https://geocoding-api.open-meteo.com/v1/search"
            response = await self.client.get(geocoding_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            results = data.get("results", [])
            self.logger.debug(
                "location_search_completed",
                name=name,
                results_count=len(results) if results is not None else 0
            )
            
            return GeocodingResponse(**data)
            
        except httpx.HTTPStatusError as e:
            self.logger.error(
                "geocoding_api_http_error",
                status_code=e.response.status_code,
                error=str(e)
            )
            raise
        except httpx.HTTPError as e:
            self.logger.error("geocoding_api_request_error", error=str(e))
            raise
        except Exception as e:
            self.logger.error("geocoding_api_unexpected_error", error=str(e))
            raise ValueError(f"Failed to parse geocoding data: {e}") from e
    
    async def close(self):
        """Close the HTTP client and release resources."""
        await self.client.aclose()
        self.logger.debug("client_closed")
    
    async def __aenter__(self):
        """Async context manager entry."""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()

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
            "daily": "temperature_2m_max,temperature_2m_min,precipitation_sum,weather_code,sunrise,sunset"
        }
        
        if include_hourly:
            params["hourly"] = "temperature_2m,precipitation,weather_code,wind_speed_10m,relative_humidity_2m"
        
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
            "daily": "snowfall_sum,snow_depth_max,temperature_2m_max,temperature_2m_min"
        }
        
        if include_hourly:
            params["hourly"] = "snowfall,snow_depth,temperature_2m,weather_code,wind_speed_10m"
        
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

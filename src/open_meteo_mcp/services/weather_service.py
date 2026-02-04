"""Weather service with auto-enrichment."""

from typing import Any
from ..client import OpenMeteoClient
from ..helpers import (
    interpret_weather_code,
    format_temperature,
    calculate_wind_chill,
    assess_ski_conditions,
)


class WeatherService:
    """Service for weather data with automatic enrichment."""

    def __init__(self, client: OpenMeteoClient):
        """Initialize weather service with client.

        Args:
            client: OpenMeteoClient instance
        """
        self.client = client

    async def get_weather_enriched(
        self,
        latitude: float,
        longitude: float,
        forecast_days: int = 7,
        include_hourly: bool = True,
        timezone: str = "auto",
    ) -> dict[str, Any]:
        """Get weather forecast with automatic enrichment.

        Fetches weather data and applies enrichment through helpers:
        - Weather code interpretation
        - Temperature formatting
        - Wind chill calculation

        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            forecast_days: Number of forecast days (1-16, default: 7)
            include_hourly: Include hourly forecasts (default: True)
            timezone: Timezone for timestamps (default: 'auto')

        Returns:
            Dictionary with enriched weather data including interpretation layer
        """
        # Fetch raw data from client
        forecast = await self.client.get_weather(
            latitude=latitude,
            longitude=longitude,
            forecast_days=forecast_days,
            include_hourly=include_hourly,
            timezone=timezone,
        )

        # Convert to dict
        result = forecast.model_dump()

        # Enrich current weather if available
        if result.get("current_weather"):
            current = result["current_weather"]

            # Add weather interpretation
            if "weather_code" in current:
                current["weather_interpretation"] = interpret_weather_code(
                    current["weather_code"]
                )

            # Add formatted temperature
            if "temperature" in current:
                current["temperature_formatted"] = format_temperature(
                    current["temperature"]
                )

            # Add wind chill if temperature and wind are available
            if "temperature" in current and "windspeed" in current:
                current["wind_chill"] = calculate_wind_chill(
                    current["temperature"],
                    current["windspeed"],
                )

        # Enrich daily forecast
        if result.get("daily"):
            daily = result["daily"]

            # Add weather interpretations to daily forecasts
            if "weather_code" in daily and daily["weather_code"]:
                daily["weather_interpretation"] = [
                    interpret_weather_code(code) for code in daily["weather_code"]
                ]

            # Format temperature ranges
            if "temperature_2m_max" in daily and daily["temperature_2m_max"]:
                daily["temperature_max_formatted"] = [
                    format_temperature(t) for t in daily["temperature_2m_max"]
                ]

            if "temperature_2m_min" in daily and daily["temperature_2m_min"]:
                daily["temperature_min_formatted"] = [
                    format_temperature(t) for t in daily["temperature_2m_min"]
                ]

        return result

    async def get_snow_conditions_enriched(
        self,
        latitude: float,
        longitude: float,
        forecast_days: int = 7,
        include_hourly: bool = True,
        timezone: str = "Europe/Zurich",
    ) -> dict[str, Any]:
        """Get snow conditions with ski assessment enrichment.

        Fetches snow conditions and applies enrichment:
        - Ski condition assessment
        - Temperature formatting
        - Weather interpretation

        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            forecast_days: Number of forecast days (1-16, default: 7)
            include_hourly: Include hourly data (default: True)
            timezone: Timezone for timestamps (default: 'Europe/Zurich')

        Returns:
            Dictionary with enriched snow conditions including ski assessment
        """
        # Fetch raw data from client
        conditions = await self.client.get_snow_conditions(
            latitude=latitude,
            longitude=longitude,
            forecast_days=forecast_days,
            include_hourly=include_hourly,
            timezone=timezone,
        )

        # Convert to dict
        result = conditions.model_dump()

        # Get weather data for enrichment
        weather = await self.client.get_weather(
            latitude=latitude,
            longitude=longitude,
            forecast_days=forecast_days,
            include_hourly=False,
            timezone=timezone,
        )
        weather_data = weather.model_dump()

        # Enrich current conditions with ski assessment
        if result.get("current") and weather_data.get("current_weather"):
            current = result["current"]
            weather_current = weather_data["current_weather"]

            # Add ski condition assessment
            current["ski_assessment"] = assess_ski_conditions(
                current, weather_current
            )

            # Format temperature
            if "temperature_2m" in weather_current:
                current["temperature_formatted"] = format_temperature(
                    weather_current["temperature_2m"]
                )

        # Enrich daily snow forecast
        if result.get("daily") and weather_data.get("daily"):
            daily_snow = result["daily"]
            daily_weather = weather_data["daily"]

            # Add weather interpretations
            if "weather_code" in daily_weather and daily_weather["weather_code"]:
                daily_snow["weather_interpretation"] = [
                    interpret_weather_code(code)
                    for code in daily_weather["weather_code"]
                ]

        return result

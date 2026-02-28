"""Weather service with auto-enrichment."""

from typing import Any

from ..helpers import (
    assess_ski_conditions,
    calculate_wind_chill,
    format_temperature,
    interpret_weather_code,
)
from .base import BaseService


class WeatherService(BaseService):
    """Service for weather data with automatic enrichment."""

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
        result: dict[str, Any] = forecast.model_dump()

        # Enrich current weather if available
        def enrich_current(current: dict[str, Any]) -> None:
            self._enrich_if_exists(
                current,
                "weather_code",
                interpret_weather_code,
                "weather_interpretation",
            )
            self._enrich_if_exists(
                current,
                "temperature",
                format_temperature,
                "temperature_formatted",
            )
            if "temperature" in current and "windspeed" in current:
                current["wind_chill"] = calculate_wind_chill(
                    current["temperature"],
                    current["windspeed"],
                )

        self._enrich_section(result, "current_weather", enrich_current)

        # Enrich daily forecast
        def enrich_daily(daily: dict[str, Any]) -> None:
            self._enrich_list_if_exists(
                daily,
                "weather_code",
                interpret_weather_code,
                "weather_interpretation",
            )
            self._enrich_list_if_exists(
                daily,
                "temperature_2m_max",
                format_temperature,
                "temperature_max_formatted",
            )
            self._enrich_list_if_exists(
                daily,
                "temperature_2m_min",
                format_temperature,
                "temperature_min_formatted",
            )

        self._enrich_section(result, "daily", enrich_daily)

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
        result: dict[str, Any] = conditions.model_dump()

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
            current["ski_assessment"] = assess_ski_conditions(current, weather_current)

            # Format temperature
            self._enrich_if_exists(
                weather_current,
                "temperature_2m",
                format_temperature,
                "temperature_formatted",
            )
            if "temperature_formatted" in weather_current:
                current["temperature_formatted"] = weather_current[
                    "temperature_formatted"
                ]

        # Enrich daily snow forecast
        if result.get("daily") and weather_data.get("daily"):
            daily_snow = result["daily"]
            daily_weather = weather_data["daily"]

            # Add weather interpretations
            self._enrich_list_if_exists(
                daily_weather,
                "weather_code",
                interpret_weather_code,
                "weather_interpretation",
            )
            if "weather_interpretation" in daily_weather:
                daily_snow["weather_interpretation"] = daily_weather[
                    "weather_interpretation"
                ]

        return result

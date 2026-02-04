"""Air quality service with enrichment."""

from typing import Any
from ..client import OpenMeteoClient


class AirQualityService:
    """Service for air quality data with automatic enrichment."""

    def __init__(self, client: OpenMeteoClient):
        """Initialize air quality service with client.

        Args:
            client: OpenMeteoClient instance
        """
        self.client = client

    def _get_aqi_interpretation(self, aqi: int) -> dict[str, Any]:
        """Interpret European AQI value.

        Args:
            aqi: European AQI value (0-100+)

        Returns:
            Dictionary with interpretation, category, and recommendations
        """
        if aqi <= 20:
            return {
                "category": "Good",
                "description": "Air quality is good",
                "health_advice": "Air quality is satisfactory; enjoy outdoor activities",
                "sensitive_groups_advice": "No restrictions",
            }
        elif aqi <= 40:
            return {
                "category": "Fair",
                "description": "Air quality is fair",
                "health_advice": "Air quality is acceptable; some pollutants may be concerning",
                "sensitive_groups_advice": "Sensitive groups may experience minor symptoms",
            }
        elif aqi <= 60:
            return {
                "category": "Moderate",
                "description": "Air quality is moderate",
                "health_advice": "Reduce prolonged outdoor exertion",
                "sensitive_groups_advice": "Limit outdoor activities",
            }
        elif aqi <= 80:
            return {
                "category": "Poor",
                "description": "Air quality is poor",
                "health_advice": "Avoid outdoor activities",
                "sensitive_groups_advice": "Stay indoors; use air purifiers",
            }
        else:
            return {
                "category": "Very Poor",
                "description": "Air quality is extremely poor",
                "health_advice": "Minimize outdoor exposure",
                "sensitive_groups_advice": "Remain indoors with air filtration",
            }

    def _get_us_aqi_interpretation(self, aqi: int) -> dict[str, Any]:
        """Interpret US AQI value.

        Args:
            aqi: US AQI value (0-500)

        Returns:
            Dictionary with interpretation and health advice
        """
        if aqi <= 50:
            return {
                "category": "Good",
                "description": "Air quality is satisfactory",
                "health_advice": "No health impacts expected",
            }
        elif aqi <= 100:
            return {
                "category": "Moderate",
                "description": "Air quality is acceptable",
                "health_advice": "Unusually sensitive people should consider limiting prolonged outdoor activities",
            }
        elif aqi <= 150:
            return {
                "category": "Unhealthy for Sensitive Groups",
                "description": "Members of sensitive groups may experience health effects",
                "health_advice": "Sensitive groups should limit outdoor activities",
            }
        elif aqi <= 200:
            return {
                "category": "Unhealthy",
                "description": "Everyone may begin to experience health effects",
                "health_advice": "Reduce outdoor activities and limit exposure",
            }
        elif aqi <= 300:
            return {
                "category": "Very Unhealthy",
                "description": "Health alert: The risk of health effects is increased for everyone",
                "health_advice": "Avoid outdoor activities; stay indoors with air filtration",
            }
        else:
            return {
                "category": "Hazardous",
                "description": "Health warning: The entire population is more likely to be affected",
                "health_advice": "Everyone should remain indoors; use air purifiers",
            }

    async def get_air_quality_enriched(
        self,
        latitude: float,
        longitude: float,
        forecast_days: int = 5,
        include_pollen: bool = True,
        timezone: str = "auto",
    ) -> dict[str, Any]:
        """Get air quality forecast with automatic enrichment.

        Fetches air quality data and applies enrichment:
        - AQI interpretation with health advice
        - Pollutant descriptions

        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            forecast_days: Number of forecast days (1-5, default: 5)
            include_pollen: Include pollen data (default: True)
            timezone: Timezone for timestamps (default: 'auto')

        Returns:
            Dictionary with enriched air quality data
        """
        # Fetch raw data from client
        forecast = await self.client.get_air_quality(
            latitude=latitude,
            longitude=longitude,
            forecast_days=forecast_days,
            include_pollen=include_pollen,
            timezone=timezone,
        )

        # Convert to dict
        result = forecast.model_dump()

        # Enrich current air quality
        if result.get("current"):
            current = result["current"]

            # Add European AQI interpretation
            if "european_aqi" in current:
                current["european_aqi_interpretation"] = (
                    self._get_aqi_interpretation(current["european_aqi"])
                )

            # Add US AQI interpretation
            if "us_aqi" in current:
                current["us_aqi_interpretation"] = self._get_us_aqi_interpretation(
                    current["us_aqi"]
                )

        # Enrich hourly air quality
        if result.get("hourly"):
            hourly = result["hourly"]

            # Add hourly AQI interpretations
            if "european_aqi" in hourly and hourly["european_aqi"]:
                hourly["european_aqi_interpretation"] = [
                    self._get_aqi_interpretation(aqi) for aqi in hourly["european_aqi"]
                ]

            if "us_aqi" in hourly and hourly["us_aqi"]:
                hourly["us_aqi_interpretation"] = [
                    self._get_us_aqi_interpretation(aqi) for aqi in hourly["us_aqi"]
                ]

        return result

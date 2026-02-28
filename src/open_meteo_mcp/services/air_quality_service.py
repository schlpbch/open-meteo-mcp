"""Air quality service with enrichment."""

from typing import Any
from .base import BaseService
from ..client import OpenMeteoClient

# AQI interpretation threshold maps
EUROPEAN_AQI_THRESHOLDS = [
    (20, {
        "category": "Good",
        "description": "Air quality is good",
        "health_advice": "Air quality is satisfactory; enjoy outdoor activities",
        "sensitive_groups_advice": "No restrictions",
    }),
    (40, {
        "category": "Fair",
        "description": "Air quality is fair",
        "health_advice": "Air quality is acceptable; some pollutants may be concerning",
        "sensitive_groups_advice": "Sensitive groups may experience minor symptoms",
    }),
    (60, {
        "category": "Moderate",
        "description": "Air quality is moderate",
        "health_advice": "Reduce prolonged outdoor exertion",
        "sensitive_groups_advice": "Limit outdoor activities",
    }),
    (80, {
        "category": "Poor",
        "description": "Air quality is poor",
        "health_advice": "Avoid outdoor activities",
        "sensitive_groups_advice": "Stay indoors; use air purifiers",
    }),
    (float('inf'), {
        "category": "Very Poor",
        "description": "Air quality is extremely poor",
        "health_advice": "Minimize outdoor exposure",
        "sensitive_groups_advice": "Remain indoors with air filtration",
    }),
]

US_AQI_THRESHOLDS = [
    (50, {
        "category": "Good",
        "description": "Air quality is satisfactory",
        "health_advice": "No health impacts expected",
    }),
    (100, {
        "category": "Moderate",
        "description": "Air quality is acceptable",
        "health_advice": "Unusually sensitive people should consider limiting prolonged outdoor activities",
    }),
    (150, {
        "category": "Unhealthy for Sensitive Groups",
        "description": "Members of sensitive groups may experience health effects",
        "health_advice": "Sensitive groups should limit outdoor activities",
    }),
    (200, {
        "category": "Unhealthy",
        "description": "Everyone may begin to experience health effects",
        "health_advice": "Reduce outdoor activities and limit exposure",
    }),
    (300, {
        "category": "Very Unhealthy",
        "description": "Health alert: The risk of health effects is increased for everyone",
        "health_advice": "Avoid outdoor activities; stay indoors with air filtration",
    }),
    (float('inf'), {
        "category": "Hazardous",
        "description": "Health warning: The entire population is more likely to be affected",
        "health_advice": "Everyone should remain indoors; use air purifiers",
    }),
]


class AirQualityService(BaseService):
    """Service for air quality data with automatic enrichment."""

    def _interpret_aqi(self, aqi: int, thresholds: list[tuple[int, dict[str, Any]]]) -> dict[str, Any]:
        """Interpret AQI value using threshold mapping.

        Args:
            aqi: AQI value to interpret
            thresholds: List of (threshold, interpretation) tuples, ordered ascending

        Returns:
            Dictionary with interpretation, category, and recommendations
        """
        for threshold, interpretation in thresholds:
            if aqi <= threshold:
                return interpretation.copy()
        # Fallback (should not reach due to float('inf') in threshold lists)
        return thresholds[-1][1].copy()

    def _get_aqi_interpretation(self, aqi: int) -> dict[str, Any]:
        """Interpret European AQI value.

        Args:
            aqi: European AQI value (0-100+)

        Returns:
            Dictionary with interpretation, category, and recommendations
        """
        return self._interpret_aqi(aqi, EUROPEAN_AQI_THRESHOLDS)

    def _get_us_aqi_interpretation(self, aqi: int) -> dict[str, Any]:
        """Interpret US AQI value.

        Args:
            aqi: US AQI value (0-500)

        Returns:
            Dictionary with interpretation and health advice
        """
        return self._interpret_aqi(aqi, US_AQI_THRESHOLDS)

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

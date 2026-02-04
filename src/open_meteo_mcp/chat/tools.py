"""Tool definitions for Anthropic Claude integration."""

from typing import Any


def get_weather_tool_schema() -> dict[str, Any]:
    """Get schema for weather tool."""
    return {
        "name": "meteo__get_weather",
        "description": "Get weather forecast for a location with temperature, precipitation, and wind conditions",
        "input_schema": {
            "type": "object",
            "properties": {
                "latitude": {
                    "type": "number",
                    "description": "Latitude in decimal degrees (e.g., 47.3769 for Zurich)",
                },
                "longitude": {
                    "type": "number",
                    "description": "Longitude in decimal degrees (e.g., 8.5417 for Zurich)",
                },
                "forecast_days": {
                    "type": "integer",
                    "description": "Number of forecast days (1-16, default: 7)",
                    "default": 7,
                },
                "include_hourly": {
                    "type": "boolean",
                    "description": "Include hourly forecasts (default: true)",
                    "default": True,
                },
                "timezone": {
                    "type": "string",
                    "description": "Timezone for timestamps (default: auto)",
                    "default": "auto",
                },
            },
            "required": ["latitude", "longitude"],
        },
    }


def get_snow_conditions_tool_schema() -> dict[str, Any]:
    """Get schema for snow conditions tool."""
    return {
        "name": "meteo__get_snow_conditions",
        "description": "Get snow conditions and forecasts for mountain locations with ski condition assessment",
        "input_schema": {
            "type": "object",
            "properties": {
                "latitude": {
                    "type": "number",
                    "description": "Latitude in decimal degrees (e.g., 45.9763 for Zermatt)",
                },
                "longitude": {
                    "type": "number",
                    "description": "Longitude in decimal degrees (e.g., 7.6586 for Zermatt)",
                },
                "forecast_days": {
                    "type": "integer",
                    "description": "Number of forecast days (1-16, default: 7)",
                    "default": 7,
                },
                "include_hourly": {
                    "type": "boolean",
                    "description": "Include hourly data (default: true)",
                    "default": True,
                },
                "timezone": {
                    "type": "string",
                    "description": "Timezone for timestamps (default: Europe/Zurich)",
                    "default": "Europe/Zurich",
                },
            },
            "required": ["latitude", "longitude"],
        },
    }


def get_air_quality_tool_schema() -> dict[str, Any]:
    """Get schema for air quality tool."""
    return {
        "name": "meteo__get_air_quality",
        "description": "Get air quality forecast including AQI, pollutants, UV index, and pollen with health interpretations",
        "input_schema": {
            "type": "object",
            "properties": {
                "latitude": {
                    "type": "number",
                    "description": "Latitude in decimal degrees",
                },
                "longitude": {
                    "type": "number",
                    "description": "Longitude in decimal degrees",
                },
                "forecast_days": {
                    "type": "integer",
                    "description": "Number of forecast days (1-5, default: 5)",
                    "default": 5,
                },
                "include_pollen": {
                    "type": "boolean",
                    "description": "Include pollen data (default: true)",
                    "default": True,
                },
                "timezone": {
                    "type": "string",
                    "description": "Timezone for timestamps (default: auto)",
                    "default": "auto",
                },
            },
            "required": ["latitude", "longitude"],
        },
    }


def search_location_tool_schema() -> dict[str, Any]:
    """Get schema for location search tool."""
    return {
        "name": "meteo__search_location",
        "description": "Search for locations by name to get coordinates for weather queries",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {
                    "type": "string",
                    "description": "Location name to search (e.g., 'Zurich', 'Eiger', 'Lake Lucerne')",
                },
                "count": {
                    "type": "integer",
                    "description": "Number of results to return (1-100, default: 10)",
                    "default": 10,
                },
                "language": {
                    "type": "string",
                    "description": "Language for results (default: 'en')",
                    "default": "en",
                },
                "country": {
                    "type": "string",
                    "description": "Optional country code filter (e.g., 'CH' for Switzerland)",
                },
            },
            "required": ["name"],
        },
    }


def get_all_tool_schemas() -> list[dict[str, Any]]:
    """Get all tool schemas for Claude.

    Returns:
        List of tool schemas for the weather tools
    """
    return [
        get_weather_tool_schema(),
        get_snow_conditions_tool_schema(),
        get_air_quality_tool_schema(),
        search_location_tool_schema(),
    ]

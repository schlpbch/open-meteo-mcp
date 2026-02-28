"""REST API routes for Open Meteo tools."""

from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from ...client import OpenMeteoClient
from ...services import AirQualityService, LocationService, WeatherService

# Initialize router
router = APIRouter()

# Initialize client and services
client = OpenMeteoClient()
weather_service = WeatherService(client)
air_quality_service = AirQualityService(client)
location_service = LocationService(client)


# Request models
class LocationSearchRequest(BaseModel):
    """Request model for location search."""

    name: str = Field(..., description="Location name to search")
    count: int = Field(10, description="Number of results (1-100)", ge=1, le=100)
    language: str = Field("en", description="Language for results")
    country: str | None = Field(None, description="Optional country code filter")


# Endpoint: GET /api/tools/weather
@router.get("/weather", response_model=dict[str, Any])
async def get_weather(
    latitude: float = Query(..., description="Latitude in decimal degrees"),
    longitude: float = Query(..., description="Longitude in decimal degrees"),
    forecast_days: int = Query(
        7, description="Number of forecast days (1-16)", ge=1, le=16
    ),
    include_hourly: bool = Query(True, description="Include hourly forecasts"),
    timezone: str = Query("auto", description="Timezone for timestamps"),
) -> dict[str, Any]:
    """Get weather forecast for a location.

    Returns current weather conditions and forecast data with enrichment.
    """
    try:
        return await weather_service.get_weather_enriched(
            latitude=latitude,
            longitude=longitude,
            forecast_days=forecast_days,
            include_hourly=include_hourly,
            timezone=timezone,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Weather service error: {str(e)}"
        ) from e


# Endpoint: GET /api/tools/snow-conditions
@router.get("/snow-conditions", response_model=dict[str, Any])
async def get_snow_conditions(
    latitude: float = Query(..., description="Latitude in decimal degrees"),
    longitude: float = Query(..., description="Longitude in decimal degrees"),
    forecast_days: int = Query(
        7, description="Number of forecast days (1-16)", ge=1, le=16
    ),
    include_hourly: bool = Query(True, description="Include hourly data"),
    timezone: str = Query("Europe/Zurich", description="Timezone for timestamps"),
) -> dict[str, Any]:
    """Get snow conditions and forecasts for mountain locations.

    Returns snow depth, snowfall, and ski condition assessments.
    """
    try:
        return await weather_service.get_snow_conditions_enriched(
            latitude=latitude,
            longitude=longitude,
            forecast_days=forecast_days,
            include_hourly=include_hourly,
            timezone=timezone,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Snow conditions service error: {str(e)}"
        ) from e


# Endpoint: GET /api/tools/air-quality
@router.get("/air-quality", response_model=dict[str, Any])
async def get_air_quality(
    latitude: float = Query(..., description="Latitude in decimal degrees"),
    longitude: float = Query(..., description="Longitude in decimal degrees"),
    forecast_days: int = Query(
        5, description="Number of forecast days (1-5)", ge=1, le=5
    ),
    include_pollen: bool = Query(True, description="Include pollen data"),
    timezone: str = Query("auto", description="Timezone for timestamps"),
) -> dict[str, Any]:
    """Get air quality forecast including AQI, pollutants, and pollen.

    Returns air quality data with health interpretations.
    """
    try:
        return await air_quality_service.get_air_quality_enriched(
            latitude=latitude,
            longitude=longitude,
            forecast_days=forecast_days,
            include_pollen=include_pollen,
            timezone=timezone,
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Air quality service error: {str(e)}"
        ) from e


# Endpoint: POST /api/tools/search-location
@router.post("/search-location", response_model=dict[str, Any])
async def search_location(request: LocationSearchRequest) -> dict[str, Any]:
    """Search for locations by name.

    Returns matching locations with coordinates for weather queries.
    """
    try:
        return await location_service.search_location_enriched(
            name=request.name,
            count=request.count,
            language=request.language,
            country=request.country or "",
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Location search error: {str(e)}"
        ) from e

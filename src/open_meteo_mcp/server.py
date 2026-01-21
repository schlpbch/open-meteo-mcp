"""FastMCP server for Open Meteo weather and snow conditions."""

from fastmcp import FastMCP
from pathlib import Path
from datetime import datetime
from .client import OpenMeteoClient

# Initialize FastMCP server
mcp = FastMCP("open_meteo")

# Initialize API client
client = OpenMeteoClient()


# ============================================================================
# TOOLS
# ============================================================================


@mcp.tool(name="meteo__get_weather")
async def get_weather(
    latitude: float,
    longitude: float,
    forecast_days: int = 7,
    include_hourly: bool = True,
    timezone: str = "auto",
) -> dict:
    """
    Retrieves weather forecast for a location (temperature, rain, sunshine).

    Get current weather conditions for any location in Switzerland (or worldwide).

    **Examples**:
    - "What's the weather in Zürich?" → latitude: 47.3769, longitude: 8.5417
    - "Weather at destination" → Use coordinates from journey endpoint
    - "Is it raining in Bern?" → Check precipitation field

    **Provides**:
    - Current temperature (°C)
    - Weather condition (clear, cloudy, rain, snow)
    - Precipitation amount (mm)
    - Wind speed (km/h)
    - Humidity (%)
    - Hourly and daily forecasts

    **Data Source**: Open-Meteo API (free, no API key required)

    **Performance**: < 200ms

    **Use this tool when**:
    - User asks about weather conditions
    - Planning outdoor activities
    - Checking if weather affects travel
    - Combined with journey planning

    Args:
        latitude: Latitude in decimal degrees (e.g., 46.9479 for Bern)
        longitude: Longitude in decimal degrees (e.g., 7.4474 for Bern)
        forecast_days: Number of forecast days (1-16, default: 7)
        include_hourly: Include hourly forecasts (default: true)
        timezone: Timezone for timestamps (e.g., 'Europe/Zurich', default: 'auto')

    Returns:
        Dictionary containing:
        - current (dict): Current weather with temperature, weather_code, wind_speed, humidity
        - hourly (list[dict] | None): Hourly forecasts if include_hourly=True
        - daily (list[dict]): Daily forecasts with min/max temps, precipitation, weather codes
        - location (dict): Location metadata with coordinates and timezone
    """
    forecast = await client.get_weather(
        latitude=latitude,
        longitude=longitude,
        forecast_days=forecast_days,
        include_hourly=include_hourly,
        timezone=timezone,
    )
    return forecast.model_dump()


@mcp.tool(name="meteo__get_snow_conditions")
async def get_snow_conditions(
    latitude: float,
    longitude: float,
    forecast_days: int = 7,
    include_hourly: bool = True,
    timezone: str = "Europe/Zurich",
) -> dict:
    """
    Retrieves snow conditions and forecasts for mountain locations.

    **Parameters**:
    - latitude (required): Latitude in decimal degrees
    - longitude (required): Longitude in decimal degrees
    - forecast_days (optional): Number of forecast days (1-16, default: 7)
    - include_hourly (optional): Include hourly data (default: true)
    - timezone (optional): Timezone for timestamps (default: "Europe/Zurich")

    **Returns**:
    - Current snow depth (meters)
    - Recent snowfall (cm)
    - Forecast snowfall
    - Temperature trends
    - Hourly and daily snow data

    **Use this tool for**:
    - Ski trip planning
    - Checking snow conditions at resorts
    - Mountain weather forecasts
    - Avalanche risk assessment (via snow depth trends)

    Args:
        latitude: Latitude in decimal degrees (e.g., 45.9763 for Zermatt)
        longitude: Longitude in decimal degrees (e.g., 7.6586 for Zermatt)
        forecast_days: Number of forecast days (1-16, default: 7)
        include_hourly: Include hourly data (default: true)
        timezone: Timezone for timestamps (default: 'Europe/Zurich')

    Returns:
        Dictionary containing:
        - current (dict): Current snow depth and recent snowfall
        - hourly (list[dict] | None): Hourly snow data if include_hourly=True
        - daily (list[dict]): Daily snow forecasts with accumulation and temperature
        - location (dict): Mountain location metadata
    """
    conditions = await client.get_snow_conditions(
        latitude=latitude,
        longitude=longitude,
        forecast_days=forecast_days,
        include_hourly=include_hourly,
        timezone=timezone,
    )
    return conditions.model_dump()


@mcp.tool(name="meteo__search_location")
async def search_location(
    name: str, count: int = 10, language: str = "en", country: str = ""
) -> dict:
    """
    Searches for locations by name to get coordinates for weather queries.

    Convert location names to coordinates using fuzzy search. Essential for
    natural language weather queries like "weather in Zurich" instead of
    requiring latitude/longitude coordinates.

    **Examples**:
    - "Zurich" → Returns Zurich, Switzerland with coordinates
    - "Bern" → Returns multiple matches (Bern CH, Bern US, etc.)
    - "Zermatt" → Returns ski resort with elevation data
    - "Lake Geneva" → Returns lake coordinates

    **Features**:
    - Fuzzy matching (handles typos)
    - Multi-language support
    - Country filtering (e.g., country="CH" for Switzerland only)
    - Returns population, timezone, elevation

    **Workflow**:
    1. Search for location by name
    2. Select result (usually first is best match)
    3. Use latitude/longitude for get_weather or get_snow_conditions

    **Use this tool when**:
    - User provides location name instead of coordinates
    - Need to find coordinates for a city, mountain, or landmark
    - Want to discover locations in a specific country

    Args:
        name: Location name to search (e.g., 'Zurich', 'Eiger', 'Lake Lucerne')
        count: Number of results to return (1-100, default: 10)
        language: Language for results (default: 'en', options: 'de', 'fr', 'it', etc.)
        country: Optional country code filter (e.g., 'CH' for Switzerland, 'DE' for Germany)

    Returns:
        Dictionary containing:
        - results (list[dict]): List of matching locations, each with:
          - name (str): Location name
          - latitude (float): Latitude coordinate
          - longitude (float): Longitude coordinate
          - elevation (float | None): Elevation in meters
          - country (str): Country code
          - timezone (str): Timezone identifier
          - population (int | None): Population if applicable
    """
    response = await client.search_location(
        name=name, count=count, language=language, country=country if country else None
    )
    return response.model_dump()


@mcp.tool(name="meteo__get_air_quality")
async def get_air_quality(
    latitude: float,
    longitude: float,
    forecast_days: int = 5,
    include_pollen: bool = True,
    timezone: str = "auto",
) -> dict:
    """
    Retrieves air quality forecast including AQI, pollutants, UV index, and pollen data.

    Monitor air quality for health-aware outdoor planning, allergy management,
    and UV exposure assessment. Provides both European and US Air Quality Indices
    along with detailed pollutant measurements.

    **Examples**:
    - "What's the air quality in Zurich?" → AQI, PM2.5, PM10, ozone levels
    - "Pollen forecast for Bern?" → Grass, birch, alder pollen counts
    - "UV index for tomorrow?" → UV radiation forecast

    **Provides**:
    - European AQI (0-100+) and US AQI (0-500)
    - Particulate matter (PM10, PM2.5)
    - Gases (O3, NO2, SO2, CO, NH3)
    - UV index (current and clear sky)
    - Pollen data (Europe only): alder, birch, grass, mugwort, olive, ragweed

    **Health Guidelines**:
    - European AQI: 0-20 (Good), 20-40 (Fair), 40-60 (Moderate), 60-80 (Poor), 80-100 (Very Poor), 100+ (Extremely Poor)
    - US AQI: 0-50 (Good), 51-100 (Moderate), 101-150 (Unhealthy for Sensitive), 151-200 (Unhealthy), 201-300 (Very Unhealthy), 301-500 (Hazardous)
    - UV Index: 0-2 (Low), 3-5 (Moderate), 6-7 (High), 8-10 (Very High), 11+ (Extreme)

    **Use this tool when**:
    - Planning outdoor activities for people with asthma/allergies
    - Assessing air quality for exercise or sports
    - Checking pollen levels during allergy season
    - Monitoring UV exposure for sun safety

    Args:
        latitude: Latitude in decimal degrees
        longitude: Longitude in decimal degrees
        forecast_days: Number of forecast days (1-5, default: 5)
        include_pollen: Include pollen data (default: true, Europe only)
        timezone: Timezone for timestamps (default: 'auto')

    Returns:
        Dictionary containing:
        - current (dict): Current AQI, pollutants (PM10, PM2.5, O3, NO2, SO2, CO), UV index
        - hourly (list[dict]): Hourly air quality forecasts
        - pollen (dict | None): Pollen data if include_pollen=True and location is in Europe
        - location (dict): Location metadata
    """
    forecast = await client.get_air_quality(
        latitude=latitude,
        longitude=longitude,
        forecast_days=forecast_days,
        include_pollen=include_pollen,
        timezone=timezone,
    )
    return forecast.model_dump()


@mcp.tool(name="meteo__get_weather_alerts")
async def get_weather_alerts(
    latitude: float, longitude: float, forecast_hours: int = 24, timezone: str = "auto"
) -> dict:
    """
    Generate weather alerts based on thresholds and current forecast.

    Automatically identifies severe weather conditions and generates actionable alerts.

    **Alert Types**:
    - Heat warnings (temperature > 30°C for 3+ hours)
    - Cold warnings (temperature < -10°C)
    - Storm warnings (wind gusts > 80 km/h or thunderstorms)
    - UV warnings (UV index > 8)
    - Wind advisories (gusts 50-80 km/h)

    **Severity Levels**:
    - Advisory: Precautionary, plan accordingly
    - Watch: Conditions favorable for alert type
    - Warning: Conditions expected, take precautions

    **Examples**:
    - Check for heat waves during summer
    - Monitor for storms before outdoor events
    - Plan sun protection based on UV alerts

    Args:
        latitude: Latitude in decimal degrees
        longitude: Longitude in decimal degrees
        forecast_hours: Hours to check for alerts (1-168, default: 24)
        timezone: Timezone for timestamps (default: 'auto')

    Returns:
        Dictionary containing:
        - latitude, longitude: Location coordinates
        - timezone: Timezone name
        - alerts (list): List of active alerts with type, severity, timing, and recommendations
    """
    from .helpers import generate_weather_alerts

    # Get weather forecast
    forecast = await client.get_weather(
        latitude=latitude,
        longitude=longitude,
        forecast_days=min(max(forecast_hours // 24 + 1, 1), 16),
        include_hourly=True,
        timezone=timezone,
    )

    # Generate alerts
    current = forecast.current_weather.model_dump() if forecast.current_weather else {}
    hourly = forecast.hourly.model_dump() if forecast.hourly else {}
    daily = forecast.daily.model_dump() if forecast.daily else {}

    alerts = generate_weather_alerts(current, hourly, daily, forecast.timezone)

    return {
        "latitude": latitude,
        "longitude": longitude,
        "timezone": forecast.timezone,
        "alerts": alerts,
    }


@mcp.tool(name="meteo__get_historical_weather")
async def get_historical_weather(
    latitude: float,
    longitude: float,
    start_date: str,
    end_date: str,
    include_hourly: bool = False,
    timezone: str = "auto",
) -> dict:
    """
    Retrieves historical weather data for trend analysis and research.

    Access 80+ years of historical weather data from Open-Meteo archives.

    **Use cases**:
    - Compare weather patterns year-over-year
    - Climate trend analysis
    - Event planning based on historical patterns
    - Research and academic studies

    **Examples**:
    - "How was the weather in Zurich on this date last year?"
    - "Get average temperatures for July over the past 10 years"
    - "Compare winter snow patterns"

    Args:
        latitude: Latitude in decimal degrees
        longitude: Longitude in decimal degrees
        start_date: Start date in ISO format (YYYY-MM-DD)
        end_date: End date in ISO format (YYYY-MM-DD)
        include_hourly: Include hourly historical data (default: false)
        timezone: Timezone for timestamps (default: 'auto')

    Returns:
        Dictionary containing:
        - historical weather data with temperature, precipitation, wind, etc.
        - daily summaries (temperature min/max, precipitation, weather codes)
        - optional hourly data if requested
    """
    historical = await client.get_historical_weather(
        latitude=latitude,
        longitude=longitude,
        start_date=start_date,
        end_date=end_date,
        hourly=include_hourly,
        timezone=timezone,
    )
    return historical.model_dump()


@mcp.tool(name="meteo__get_marine_conditions")
async def get_marine_conditions(
    latitude: float,
    longitude: float,
    forecast_days: int = 7,
    include_hourly: bool = True,
    timezone: str = "auto",
) -> dict:
    """
    Retrieves marine conditions for lakes and coastal areas.

    Get wave height, swell, period, and wind-driven sea states for water activities.

    **Examples**:
    - Check Lake Geneva conditions for sailing
    - Monitor Zurich Lake for water sports
    - Plan boating activities based on wave forecast

    **Provides**:
    - Wave height (m)
    - Wave direction and period (seconds)
    - Swell characteristics
    - Wind-wave parameters
    - Hourly and daily forecasts

    **Use this tool when**:
    - Planning water sports (sailing, windsurfing, kayaking)
    - Boating safety assessment
    - Recreation planning on Swiss lakes

    Args:
        latitude: Latitude in decimal degrees
        longitude: Longitude in decimal degrees
        forecast_days: Number of forecast days (1-16, default: 7)
        include_hourly: Include hourly data (default: true)
        timezone: Timezone for timestamps (default: 'auto')

    Returns:
        Dictionary containing:
        - wave_height, wave_direction, wave_period
        - swell wave data
        - wind-wave parameters
        - hourly and daily forecasts
    """
    conditions = await client.get_marine_conditions(
        latitude=latitude,
        longitude=longitude,
        forecast_days=forecast_days,
        include_hourly=include_hourly,
        timezone=timezone,
    )
    return conditions.model_dump()


@mcp.tool(name="meteo__get_comfort_index")
async def get_comfort_index(
    latitude: float, longitude: float, timezone: str = "auto"
) -> dict:
    """
    Calculates outdoor activity comfort index (0-100). Takes latitude, longitude, and timezone parameters.

    Combines weather, air quality, UV, and precipitation factors into a single
    comfort score for planning outdoor activities.

    **Score Interpretation**:
    - 80-100: Perfect for outdoor activities
    - 60-79: Good conditions
    - 40-59: Fair conditions, plan accordingly
    - 20-39: Poor conditions, seek indoor alternatives
    - 0-19: Very poor conditions

    **Factors Included**:
    - Thermal comfort (temperature, humidity, wind chill)
    - Air quality (PM2.5, PM10, AQI)
    - Precipitation risk
    - UV safety (skin protection needs)
    - Weather conditions (storms, visibility)

    **Examples**:
    - "Is it good weather for hiking?"
    - "What's the outdoor comfort level?"
    - "Can I do outdoor sports today?"

    Args:
        latitude: Latitude in decimal degrees
        longitude: Longitude in decimal degrees
        timezone: Timezone for timestamps (default: 'auto')

    Returns:
        Dictionary containing:
        - overall: Comfort index (0-100)
        - factors: Breakdown of individual factors
        - recommendation: Text recommendation for activities
    """
    from .helpers import calculate_comfort_index

    # Get current weather and air quality
    weather_forecast = await client.get_weather(
        latitude=latitude,
        longitude=longitude,
        forecast_days=1,
        include_hourly=False,
        timezone=timezone,
    )

    air_quality_forecast = await client.get_air_quality(
        latitude=latitude, longitude=longitude, forecast_days=1, include_pollen=False
    )

    # Extract current conditions
    weather = (
        weather_forecast.current_weather.model_dump()
        if weather_forecast.current_weather
        else {}
    )
    current_aqi = (
        air_quality_forecast.current.model_dump()
        if air_quality_forecast.current
        else {}
    )

    # Calculate comfort index
    comfort = calculate_comfort_index(weather, current_aqi)

    return {
        "latitude": latitude,
        "longitude": longitude,
        "timezone": weather_forecast.timezone,
        "comfort_index": comfort,
    }


@mcp.tool(name="meteo__get_astronomy")
async def get_astronomy(
    latitude: float, longitude: float, timezone: str = "auto"
) -> dict:
    """
    Provides astronomical data for a location (sunrise, sunset, golden hour).

    Useful for photography, event planning, and outdoor activity scheduling.

    **Data Provided**:
    - Sunrise and sunset times
    - Day length
    - Golden hour (best lighting for photography)
    - Blue hour (evening twilight)
    - Moon phase information
    - Best photography windows

    **Use cases**:
    - Photography location scouting
    - Outdoor event planning
    - Sunrise/sunset viewing trips
    - Time-lapse and video production planning

    **Examples**:
    - "When is sunset in Zurich?"
    - "Best time for golden hour photography?"
    - "What's the sunrise time for hiking?"

    Args:
        latitude: Latitude in decimal degrees
        longitude: Longitude in decimal degrees
        timezone: Timezone for timestamps (default: 'auto' tries to auto-detect)

    Returns:
        Dictionary containing:
        - sunrise: Sunrise time (ISO format)
        - sunset: Sunset time (ISO format)
        - day_length_hours: Total daylight hours
        - golden_hour: Start and end times for optimal lighting
        - blue_hour: Twilight window for photography
        - moon_phase: Current lunar phase
        - best_photography_windows: Recommended times for photos
    """
    from .helpers import calculate_astronomy_data

    # Resolve timezone
    if timezone == "auto":
        # Get weather to determine local timezone
        weather = await client.get_weather(
            latitude=latitude,
            longitude=longitude,
            forecast_days=1,
            include_hourly=False,
            timezone="auto",
        )
        timezone = weather.timezone

    astronomy = calculate_astronomy_data(latitude, longitude, timezone)

    return {
        "latitude": latitude,
        "longitude": longitude,
        "timezone": timezone,
        "astronomy": astronomy,
    }


@mcp.tool(name="meteo__search_location_swiss")
async def search_location_swiss(
    name: str, include_features: bool = False, language: str = "en", count: int = 10
) -> dict:
    """
    Search for locations in Switzerland with optional geographic features.

    Specialized search for Swiss locations including cities, mountains, lakes, and passes.

    **Feature Types Supported**:
    - PPL: Populated places (cities, towns, villages)
    - MT: Mountains and peaks
    - LK: Lakes and water bodies
    - PS: Mountain passes
    - STM: Streams and rivers

    **Examples**:
    - "Find Zurich" → Zurich city
    - "Search for Matterhorn" → Mountain peak
    - "Find Lake Geneva" → Lake location
    - "Find Gotthard Pass" → Mountain pass

    **Use this tool when**:
    - Searching specifically within Switzerland
    - Looking for mountains, lakes, or geographic features
    - Need precise coordinates for Swiss locations
    - Want to filter by location type

    Args:
        name: Location name to search
        include_features: Include geographic features like mountains, lakes (default: false)
        language: Language for results (de, fr, it, en; default: en)
        count: Number of results (1-50, default: 10)

    Returns:
        Dictionary containing:
        - results: List of matching Swiss locations with coordinates
        - total: Number of results found
        - search_type: Type of search performed
    """
    # Get all results
    response = await client.search_location(
        name=name,
        count=count * 2,  # Get extra results for post-processing
        language=language,
        country="CH",
    )

    results = response.results if response.results else []

    # If include_features is True, keep all; otherwise filter to populated places
    if not include_features:
        # Filter to primarily populated places
        results = [
            r for r in results if not r.feature_code or r.feature_code.startswith("PPL")
        ]

    # Sort by population if available
    results.sort(key=lambda x: x.population or 0, reverse=True)

    # Limit to requested count
    results = results[:count]

    return {
        "query": name,
        "results": [r.model_dump() if hasattr(r, "model_dump") else r for r in results],
        "total": len(results),
        "country": "CH",
        "include_features": include_features,
        "language": language,
    }


@mcp.tool(name="meteo__compare_locations")
async def compare_locations(
    locations: list, criteria: str = "best_overall", forecast_days: int = 1
) -> dict:
    """
    Compare weather conditions across multiple locations.

    Rank locations by specified weather criteria to find the best destination.

    **Comparison Criteria**:
    - best_overall: Overall comfort and conditions
    - warmest: Highest temperature
    - driest: Lowest precipitation probability
    - sunniest: Best weather codes and visibility
    - best_air_quality: Lowest AQI
    - calmest: Lowest wind speeds

    **Examples**:
    - Compare weekend weather between Zurich, Bern, and Geneva
    - Find the warmest location for outdoor activities
    - Identify the driest location for hiking
    - Compare air quality across multiple cities

    **Use this tool when**:
    - Choosing between multiple destination options
    - Planning group activities
    - Finding optimal conditions for specific activities

    Args:
        locations: List of location dicts with 'name', 'latitude', 'longitude'
        criteria: Comparison criteria (default: 'best_overall')
        forecast_days: Days to forecast (1-16, default: 1)

    Returns:
        Dictionary containing:
        - criteria: The comparison criteria used
        - locations: Ranked list of locations with scores
        - winner: Best location based on criteria
        - details: Key weather metrics for each location
    """
    from .helpers import calculate_comfort_index

    results = []

    # Fetch data for each location
    for loc in locations:
        try:
            name = loc.get("name", "Unknown")
            lat = loc.get("latitude", 46.95)
            lon = loc.get("longitude", 7.45)

            # Get weather
            weather = await client.get_weather(
                latitude=lat,
                longitude=lon,
                forecast_days=forecast_days,
                include_hourly=False,
                timezone="auto",
            )

            # Get air quality
            air_quality = await client.get_air_quality(
                latitude=lat, longitude=lon, forecast_days=1, include_pollen=False
            )

            current_weather = (
                weather.current_weather.model_dump() if weather.current_weather else {}
            )
            current_aqi = (
                air_quality.current.model_dump() if air_quality.current else {}
            )

            # Calculate comfort
            comfort = calculate_comfort_index(current_weather, current_aqi)

            results.append(
                {
                    "name": name,
                    "latitude": lat,
                    "longitude": lon,
                    "temperature": current_weather.get("temperature", 0),
                    "wind_speed": current_weather.get("windspeed", 0),
                    "weather_code": current_weather.get("weathercode", 0),
                    "comfort_index": comfort["overall"],
                    "aqi": current_aqi.get("european_aqi", 0),
                    "recommendation": comfort["recommendation"],
                }
            )

        except Exception as e:
            results.append({"name": loc.get("name", "Unknown"), "error": str(e)})

    # Sort by criteria
    if criteria == "warmest":
        results.sort(key=lambda x: x.get("temperature", 0), reverse=True)
    elif criteria == "driest":
        results.sort(key=lambda x: x.get("wind_speed", 999))
    elif criteria == "sunniest":
        results.sort(key=lambda x: x.get("weather_code", 99))
    elif criteria == "best_air_quality":
        results.sort(key=lambda x: x.get("aqi", 999))
    elif criteria == "calmest":
        results.sort(key=lambda x: x.get("wind_speed", 999))
    else:  # best_overall
        results.sort(key=lambda x: x.get("comfort_index", 0), reverse=True)

    return {
        "criteria": criteria,
        "locations": results,
        "winner": results[0] if results else None,
        "comparison_timestamp": datetime.now().isoformat(),
    }


@mcp.tool(name="meteo__get_weather_alerts")
async def get_weather_alerts(
    latitude: float, longitude: float, forecast_hours: int = 24, timezone: str = "auto"
) -> dict:
    """
    Generate weather alerts and warnings based on forecast data analysis.

    Transforms raw weather data into actionable warnings for various conditions
    like storms, extreme temperatures, high UV, and poor air quality.

    **Alert Types**:
    - Storm: High wind gusts (>80 km/h), severe weather codes
    - Heat: High temperature (>30°C) with recommendations
    - Cold: Low temperature (<-5°C) with wind chill warnings
    - UV: High UV index (>8) with skin protection advice
    - Air Quality: Poor AQI (European AQI >80) with health guidance
    - Wind: Strong sustained winds (>60 km/h) affecting activities
    - Precipitation: Heavy rain/snow (>20mm/hour) travel warnings

    **Severity Levels**:
    - Advisory: Be aware, minimal impact on activities
    - Watch: Conditions developing, plan accordingly
    - Warning: Take action, significant impact expected

    **Use Cases**:
    - Pre-trip safety assessment
    - Outdoor activity planning
    - Travel preparation
    - Health condition management
    - Event planning

    Args:
        latitude: Latitude in decimal degrees
        longitude: Longitude in decimal degrees
        forecast_hours: Hours to analyze for alerts (1-168, default: 24)
        timezone: Timezone for timestamps (default: auto)

    Returns:
        Dictionary containing:
        - alerts (list): Active alerts with type, severity, timing, recommendations
        - summary (dict): Overview of alert counts by type and severity
        - conditions (dict): Current values for key metrics
        - recommendations (list): Prioritized action items
    """
    from datetime import datetime, timedelta

    # Get weather data
    forecast_days = max(1, (forecast_hours + 23) // 24)  # Convert to days, rounded up
    weather = await client.get_weather(
        latitude=latitude,
        longitude=longitude,
        forecast_days=forecast_days,
        include_hourly=True,
        timezone=timezone,
    )

    # Get air quality data
    try:
        air_quality = await client.get_air_quality(
            latitude=latitude,
            longitude=longitude,
            forecast_days=min(forecast_days, 5),  # Air quality limited to 5 days
            include_hourly=True,
        )
    except:
        air_quality = None

    alerts = []
    current_time = datetime.now()

    # Analyze current conditions
    current = weather.current_weather if hasattr(weather, "current_weather") else None

    # Temperature alerts
    if current and hasattr(current, "temperature"):
        temp = current.temperature
        if temp > 30:
            alerts.append(
                {
                    "type": "heat",
                    "severity": (
                        "warning" if temp > 35 else "watch" if temp > 32 else "advisory"
                    ),
                    "start": current_time.isoformat(),
                    "end": (current_time + timedelta(hours=6)).isoformat(),
                    "description": f"High temperature alert: {temp:.1f}°C",
                    "recommendations": [
                        "Stay hydrated and drink plenty of water",
                        "Avoid prolonged sun exposure during peak hours (11-15h)",
                        "Wear light-colored, loose-fitting clothing",
                        "Seek shade and air conditioning when possible",
                    ],
                }
            )
        elif temp < -5:
            # Check for wind chill
            wind_speed = getattr(current, "windspeed", 0)
            apparent_temp = temp - (wind_speed * 0.6)  # Simplified wind chill
            # Determine cold alert severity based on apparent temperature
            if apparent_temp < -15:
                severity = "warning"
            elif apparent_temp < -10:
                severity = "watch"
            else:
                severity = "advisory"

            alerts.append(
                {
                    "type": "cold",
                    "severity": severity,
                    "start": current_time.isoformat(),
                    "end": (current_time + timedelta(hours=6)).isoformat(),
                    "description": f"Cold temperature alert: {temp:.1f}°C (feels like {apparent_temp:.1f}°C)",
                    "recommendations": [
                        "Dress in warm layers and cover exposed skin",
                        "Wear insulated, waterproof footwear",
                        "Limit time outdoors and watch for frostbite signs",
                        "Keep emergency supplies in vehicles",
                    ],
                }
            )

    # Wind alerts
    if current and hasattr(current, "windspeed"):
        wind_speed = current.windspeed
        if wind_speed > 60:
            alerts.append(
                {
                    "type": "wind",
                    "severity": "warning" if wind_speed > 80 else "watch",
                    "start": current_time.isoformat(),
                    "end": (current_time + timedelta(hours=6)).isoformat(),
                    "description": f"High wind alert: {wind_speed:.1f} km/h",
                    "recommendations": [
                        "Secure loose outdoor objects and furniture",
                        "Avoid driving high-profile vehicles",
                        "Stay away from trees and power lines",
                        "Consider postponing outdoor activities",
                    ],
                }
            )

    # Weather code alerts (storms, severe weather)
    if current and hasattr(current, "weathercode"):
        weather_code = current.weathercode
        # Thunderstorm codes: 95-99
        if weather_code >= 95:
            alerts.append(
                {
                    "type": "storm",
                    "severity": "warning",
                    "start": current_time.isoformat(),
                    "end": (current_time + timedelta(hours=3)).isoformat(),
                    "description": "Thunderstorm alert: Lightning and heavy precipitation",
                    "recommendations": [
                        "Seek indoor shelter immediately",
                        "Avoid using electrical equipment",
                        "Stay away from windows and doors",
                        "Do not take shelter under trees",
                    ],
                }
            )

    # UV alerts from daily data
    if (
        hasattr(weather, "daily")
        and weather.daily
        and hasattr(weather.daily, "uv_index_max")
    ):
        max_uv = max(weather.daily.uv_index_max[:1])  # Today's max UV
        if max_uv > 8:
            alerts.append(
                {
                    "type": "uv",
                    "severity": "warning" if max_uv > 10 else "watch",
                    "start": (current_time.replace(hour=10, minute=0)).isoformat(),
                    "end": (current_time.replace(hour=16, minute=0)).isoformat(),
                    "description": f"High UV alert: UV Index {max_uv:.0f}",
                    "recommendations": [
                        "Apply broad-spectrum SPF 30+ sunscreen every 2 hours",
                        "Wear protective clothing and wide-brimmed hat",
                        "Seek shade between 10am-4pm",
                        "Wear UV-blocking sunglasses",
                    ],
                }
            )

    # Air quality alerts
    if air_quality and hasattr(air_quality, "current"):
        aqi = getattr(air_quality.current, "european_aqi", None)
        if aqi and aqi > 80:
            alerts.append(
                {
                    "type": "air_quality",
                    "severity": "warning" if aqi > 120 else "watch",
                    "start": current_time.isoformat(),
                    "end": (current_time + timedelta(hours=12)).isoformat(),
                    "description": f"Poor air quality alert: European AQI {aqi:.0f}",
                    "recommendations": [
                        "Limit outdoor activities, especially strenuous exercise",
                        "Keep windows closed and use air purifiers if available",
                        "Sensitive groups should stay indoors",
                        "Wear N95 masks when outdoors if needed",
                    ],
                }
            )

    # Analyze hourly forecast for precipitation alerts
    if hasattr(weather, "hourly") and weather.hourly:
        hourly_data = weather.hourly
        hours_to_check = min(
            forecast_hours,
            len(hourly_data.time) if hasattr(hourly_data, "time") else 24,
        )

        for i in range(hours_to_check):
            if hasattr(hourly_data, "precipitation") and i < len(
                hourly_data.precipitation
            ):
                precip = hourly_data.precipitation[i]
                if precip > 10:  # Heavy precipitation threshold
                    hour_time = current_time + timedelta(hours=i)
                    alerts.append(
                        {
                            "type": "precipitation",
                            "severity": "warning" if precip > 20 else "watch",
                            "start": hour_time.isoformat(),
                            "end": (hour_time + timedelta(hours=1)).isoformat(),
                            "description": f"Heavy precipitation alert: {precip:.1f}mm/hour expected",
                            "recommendations": [
                                "Allow extra travel time due to possible delays",
                                "Drive carefully and reduce speed",
                                "Avoid flood-prone areas and underpasses",
                                "Carry umbrella and waterproof gear",
                            ],
                        }
                    )
                    break  # Only show first heavy precipitation event

    # Generate summary
    alert_counts = {
        "storm": len([a for a in alerts if a["type"] == "storm"]),
        "heat": len([a for a in alerts if a["type"] == "heat"]),
        "cold": len([a for a in alerts if a["type"] == "cold"]),
        "uv": len([a for a in alerts if a["type"] == "uv"]),
        "wind": len([a for a in alerts if a["type"] == "wind"]),
        "air_quality": len([a for a in alerts if a["type"] == "air_quality"]),
        "precipitation": len([a for a in alerts if a["type"] == "precipitation"]),
    }

    severity_counts = {
        "warning": len([a for a in alerts if a["severity"] == "warning"]),
        "watch": len([a for a in alerts if a["severity"] == "watch"]),
        "advisory": len([a for a in alerts if a["severity"] == "advisory"]),
    }

    # Current conditions summary
    conditions = {}
    if current:
        conditions = {
            "temperature": getattr(current, "temperature", None),
            "wind_speed": getattr(current, "windspeed", None),
            "weather_code": getattr(current, "weathercode", None),
        }

    if air_quality and hasattr(air_quality, "current"):
        conditions["air_quality_aqi"] = getattr(
            air_quality.current, "european_aqi", None
        )

    # Prioritized recommendations
    priority_recommendations = []
    warning_alerts = [a for a in alerts if a["severity"] == "warning"]
    if warning_alerts:
        priority_recommendations.append(
            "WARNING conditions present - review all active alerts"
        )

    watch_alerts = [a for a in alerts if a["severity"] == "watch"]
    if watch_alerts:
        priority_recommendations.append(
            "WATCH conditions developing - monitor forecast updates"
        )

    if not alerts:
        priority_recommendations.append(
            "No weather alerts - conditions are within normal ranges"
        )

    return {
        "alerts": alerts,
        "summary": {
            "total_alerts": len(alerts),
            "by_type": alert_counts,
            "by_severity": severity_counts,
            "analysis_period_hours": forecast_hours,
            "timestamp": current_time.isoformat(),
        },
        "conditions": conditions,
        "recommendations": priority_recommendations,
    }


# ============================================================================
# RESOURCES
# ============================================================================


@mcp.resource("weather://codes")
async def weather_codes() -> str:
    """
    Provides WMO weather code reference with descriptions, categories, and travel impact.

    Use this to interpret weather_code values returned by weather tools.
    Contains 28 weather codes with:
    - Description (e.g., "Clear sky", "Moderate rain")
    - Category (Clear, Cloudy, Rain, Snow, Fog, Thunderstorm)
    - Icon suggestions
    - Travel impact assessments

    Returns:
        JSON string with complete weather code reference data including
        descriptions, categories, and impact assessments for all 28 WMO codes.
    """
    data_path = Path(__file__).parent / "data" / "weather-codes.json"
    return data_path.read_text(encoding="utf-8")


@mcp.resource("weather://parameters")
async def weather_parameters() -> str:
    """
    Provides available weather and snow parameters from Open-Meteo API.

    Documents all available parameters for:
    - Hourly weather data
    - Daily weather data
    - Snow conditions
    - Units and descriptions

    Use this to understand what data is available from the API.

    Returns:
        JSON string documenting all available weather and snow parameters,
        their units, and descriptions for API queries.
    """
    data_path = Path(__file__).parent / "data" / "weather-parameters.json"
    return data_path.read_text(encoding="utf-8")


@mcp.resource("weather://swiss-locations")
async def swiss_locations() -> str:
    """
    Provides popular Swiss locations with coordinates (cities, mountains, passes, lakes).

    Quick reference for common Swiss destinations including:
    - Major cities: Zurich, Geneva, Bern, Basel, Lausanne, Lucerne, etc.
    - Mountains: Matterhorn, Eiger, Jungfrau, Pilatus, Rigi
    - Mountain passes: Gotthard, Simplon, Furka, Grimsel
    - Lakes: Geneva, Zurich, Lucerne, Constance, Maggiore

    Each location includes coordinates, elevation, and description.
    Use this for quick lookups or combine with search_location tool for more options.

    Returns:
        JSON string with Swiss location data including coordinates, elevations,
        and descriptions for cities, mountains, passes, and lakes.
    """
    data_path = Path(__file__).parent / "data" / "swiss-locations.json"
    return data_path.read_text(encoding="utf-8")


@mcp.resource("weather://aqi-reference")
async def aqi_reference() -> str:
    """
    Provides Air Quality Index (AQI) interpretation guide and health recommendations.

    Comprehensive reference for understanding air quality measurements:
    - European AQI scale (0-100+) with 6 levels from Good to Extremely Poor
    - US AQI scale (0-500) with 6 levels from Good to Hazardous
    - UV Index scale (0-11+) with protection recommendations
    - Pollen concentration levels (Europe only)

    Each level includes:
    - Numeric range
    - Color coding
    - Health implications
    - Cautionary statements for sensitive groups
    - Recommended actions

    Use this to interpret air quality data from get_air_quality tool.

    Returns:
        JSON string with complete AQI reference including European AQI, US AQI,
        UV Index scales, and health recommendations for each level.
    """
    data_path = Path(__file__).parent / "data" / "aqi-reference.json"
    return data_path.read_text(encoding="utf-8")


# ============================================================================
# PROMPTS
# ============================================================================


@mcp.prompt(name="meteo__ski-trip-weather")
async def ski_trip_weather(resort: str = "", dates: str = "") -> str:
    """
    Generates a guide for checking snow conditions and weather for ski trips to Swiss resorts.

    Args:
        resort: Name of the Swiss ski resort (e.g., 'Zermatt', 'Verbier', 'St. Moritz')
        dates: Specific dates or time period (e.g., 'this weekend', 'next week', 'January 10-15')

    Returns:
        Prompt template string instructing the LLM to check snow conditions,
        assess ski suitability, and provide recommendations for the specified
        resort and dates.
    """
    template = f"""You are helping plan a ski trip to Swiss Alps resorts. Follow this workflow:

**Step 1: Identify the Resort**
- If the user mentions a resort name{f" (they mentioned: {resort})" if resort else ""}, use the `swiss-ski-resorts` resource to get accurate coordinates
- The resource contains 16 major Swiss ski resorts including Zermatt, Verbier, St. Moritz, Davos, etc.
- Extract the latitude and longitude from the resource data

**Step 2: Check Snow Conditions**
- Use `get_snow_conditions` tool with the resort coordinates
- Key metrics to report:
  * Current snow depth (meters)
  * Recent snowfall (last 24-48 hours)
  * Forecast snowfall for next 7 days
  * Temperature trends (affects snow quality)

**Step 3: Check General Weather**
- Use `get_weather` tool for the same coordinates
- Focus on:
  * Temperature (for comfort and snow quality)
  * Weather codes (use `weather-codes` resource to interpret)
  * Wind conditions (important for lift operations)
  * Visibility (fog can close lifts)

**Step 4: Provide Ski Condition Assessment**
- Combine snow and weather data to assess conditions:
  * **Excellent**: Fresh snow (>10cm), cold temps (-5°C to -15°C), clear skies
  * **Good**: Adequate snow depth (>50cm), stable temps, partly cloudy
  * **Fair**: Limited snow, warmer temps (risk of icy conditions), variable weather
  * **Poor**: No recent snow, very warm temps, heavy fog/storms

**Step 5: Recommendations**
- Suggest best days within the forecast period{f" (focusing on: {dates})" if dates else ""}
- Warn about potential issues (warm temps, storms, fog)
- Recommend appropriate gear based on conditions

**Related Resources**:
- `swiss-ski-resorts`: Resort coordinates and metadata
- `weather-codes`: Interpret weather condition codes
- `weather-parameters`: Understanding snow depth, snowfall metrics

**Related Tools**:
- `get_snow_conditions`: Snow depth, snowfall, mountain weather
- `get_weather`: Temperature, precipitation, wind, visibility
"""
    return template


@mcp.prompt(name="meteo__plan-outdoor-activity")
async def plan_outdoor_activity(
    activity: str = "", location: str = "", timeframe: str = ""
) -> str:
    """
    Generates a weather-aware outdoor activity planning workflow for hiking, cycling, and other outdoor pursuits.

    Args:
        activity: Type of outdoor activity (e.g., 'hiking', 'cycling', 'climbing', 'camping')
        location: Location for the activity (city, mountain, trail name)
        timeframe: When planning to do the activity (e.g., 'this weekend', 'next week', specific dates)

    Returns:
        Prompt template string instructing the LLM to assess weather suitability,
        identify optimal activity windows, and provide safety recommendations based
        on the activity type and conditions.
    """
    template = f"""You are helping plan outdoor activities with weather awareness. Follow this workflow:

**Step 1: Understand the Activity**
{f"Activity mentioned: {activity}" if activity else "Determine the activity type first"}

Weather sensitivity levels:
- **High Sensitivity** (avoid rain, storms, high winds): Rock climbing, Via ferrata, High-altitude hiking, Mountaineering, Paragliding
- **Medium Sensitivity** (manageable in light rain): Day hiking, Mountain biking, Road cycling, Trail running, Camping
- **Low Sensitivity** (possible in most conditions): Walking, Urban sightseeing, Photography, Picnicking

**Step 2: Get Location Coordinates**
{f"Location: {location}" if location else "Identify the location from the user's query"}
- For Swiss locations, reference common destinations
- Ensure latitude and longitude are available

**Step 3: Check Weather Forecast**
- Use `get_weather` tool with appropriate forecast days (typically 3-7 days)
{f"Timeframe: {timeframe}" if timeframe else ""}
- Key metrics for outdoor activities:
  * **Precipitation**: Rain/snow amounts (mm)
  * **Weather codes**: Use `weather-codes` resource
  * **Temperature**: Comfort and safety
  * **Wind**: Important for exposed areas
  * **Visibility**: Critical for mountain activities

**Step 4: Assess Suitability**
- **Ideal Conditions**: Clear or partly cloudy (codes 0-2), no precipitation (<1mm), moderate temps (10-25°C), light winds (<20 km/h)
- **Acceptable Conditions**: Overcast but dry (code 3), light drizzle (<2mm), appropriate temp range, moderate winds (20-30 km/h)
- **Poor Conditions**: Heavy rain (codes 61-65, >5mm), thunderstorms (codes 95-99), extreme temps, high winds (>30 km/h)

**Step 5: Provide Recommendations**
- Identify best days within forecast period
- Suggest alternative dates if conditions are poor
- Recommend weather-appropriate gear
- Provide safety warnings for severe weather

**Activity-Specific Guidelines**:
- **Hiking**: Avoid thunderstorms (lightning risk), check snow for high-altitude trails, consider visibility
- **Cycling**: Avoid heavy rain (slippery roads) and strong headwinds
- **Climbing/Via Ferrata**: Requires dry conditions, avoid any rain or recent rain (<24h)
- **Camping**: Avoid heavy rain/storms, check overnight temps, wind for tent stability

**Related Resources**:
- `weather-codes`: Interpret weather conditions
- `weather-parameters`: Understanding precipitation, wind metrics
"""
    return template


@mcp.prompt(name="meteo__weather-aware-travel")
async def weather_aware_travel(
    destination: str = "", travel_dates: str = "", trip_type: str = ""
) -> str:
    """
    Generates an integration pattern for combining weather forecasts with journey planning.

    Args:
        destination: Travel destination (city, resort, or location name)
        travel_dates: When traveling (e.g., 'tomorrow', 'this weekend', 'January 10-15')
        trip_type: Type of trip (e.g., 'day trip', 'weekend getaway', 'ski trip', 'business travel')

    Returns:
        Prompt template string instructing the LLM to integrate weather data with
        travel planning, provide packing recommendations, and assess weather impact
        on the journey.
    """
    template = f"""You are helping with weather-aware travel planning. Follow this workflow:

**Step 1: Extract Destination Information**
{f"Destination: {destination}" if destination else "Identify travel destination from user's query"}
- If coordinates available from journey planning tools, use those
- Otherwise, use known coordinates for major Swiss cities/destinations

**Step 2: Determine Travel Timeframe**
{f"Travel dates: {travel_dates}" if travel_dates else "Extract travel dates from query"}
{f"Trip type: {trip_type}" if trip_type else ""}
- For trip planning, focus on arrival and stay period
- For day trips, check weather for entire day
- Default to 3-7 day forecast if dates unclear

**Step 3: Check Destination Weather**
- Use `get_weather` tool with destination coordinates
- For mountain destinations, also use `get_snow_conditions` if relevant
- Focus on:
  * Overall conditions (clear, rainy, snowy)
  * Temperature range
  * Precipitation amounts
  * Any severe weather warnings

**Step 4: Provide Weather-Aware Travel Advice**

**Packing Recommendations**:
- Clear/Sunny (codes 0-1): Sunglasses, sunscreen, light clothing
- Partly Cloudy (codes 2-3): Layers, light jacket
- Rainy (codes 51-82): Waterproof jacket, umbrella, water-resistant shoes
- Snowy (codes 71-86): Winter coat, warm layers, winter boots, gloves
- Stormy (codes 95-99): Postpone if possible, or prepare for indoor activities

**Temperature-Based Advice**:
- Cold (<5°C): Warm coat, gloves, hat, thermal layers
- Cool (5-15°C): Jacket, long sleeves, layers
- Mild (15-25°C): Light jacket, comfortable clothing
- Warm (>25°C): Light clothing, sun protection, hydration

**Travel Impact Assessment**:
- No Impact: Clear to partly cloudy, normal temps → Normal travel, no special prep
- Minor Impact: Light rain, cold temps → Bring umbrella, dress warm
- Moderate Impact: Heavy rain, snow → Delays possible, slower travel
- Significant Impact: Storms, extreme weather → Consider rescheduling

**Step 5: Activity Suggestions**
Based on weather, suggest appropriate activities:
- **Good Weather**: Outdoor sightseeing, hiking, lake activities, outdoor dining, photography
- **Mixed Weather**: Flexible plans (indoor/outdoor mix), covered markets, short outdoor excursions
- **Poor Weather**: Museums and galleries, indoor attractions, covered shopping, restaurants, spa

**Integration with Journey Planning**:
When used alongside journey planning tools:
1. Get destination coordinates from journey/station data
2. Check weather for arrival time and duration of stay
3. Warn about weather-related travel delays (snow, storms)
4. Suggest weather-appropriate activities at destination

**Related Resources**:
- `weather-codes`: Interpret weather conditions
- `swiss-ski-resorts`: Mountain destination coordinates
- `weather-parameters`: Understanding weather metrics
"""
    return template


# ============================================================================
# SERVER ENTRY POINT
# ============================================================================

if __name__ == "__main__":
    # Run the server
    mcp.run()

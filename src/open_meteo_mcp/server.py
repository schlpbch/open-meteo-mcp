"""FastMCP server for Open Meteo weather and snow conditions."""

from fastmcp import FastMCP
from pathlib import Path
import json
from typing import Optional

from .client import OpenMeteoClient
from .helpers import interpret_weather_code, assess_ski_conditions

# Initialize FastMCP server
mcp = FastMCP("open-meteo")

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
    timezone: str = "auto"
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
        timezone=timezone
    )
    return forecast.model_dump()


@mcp.tool(name="meteo__get_snow_conditions")
async def get_snow_conditions(
    latitude: float,
    longitude: float,
    forecast_days: int = 7,
    include_hourly: bool = True,
    timezone: str = "Europe/Zurich"
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
        timezone=timezone
    )
    return conditions.model_dump()


@mcp.tool(name="meteo__search_location")
async def search_location(
    name: str,
    count: int = 10,
    language: str = "en",
    country: str = ""
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
        name=name,
        count=count,
        language=language,
        country=country if country else None
    )
    return response.model_dump()


@mcp.tool(name="meteo__get_air_quality")
async def get_air_quality(
    latitude: float,
    longitude: float,
    forecast_days: int = 5,
    include_pollen: bool = True
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
        include_pollen=include_pollen
    )
    return forecast.model_dump()


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


@mcp.resource("weather://swiss-ski-resorts")
async def swiss_ski_resorts() -> str:
    """
    Provides popular Swiss ski resort coordinates and metadata.
    
    Contains 16 major Swiss ski resorts including:
    - Zermatt, Verbier, St. Moritz, Davos, Grindelwald
    - Coordinates (latitude, longitude)
    - Elevation
    - Ski area names
    
    Use this resource to get accurate coordinates for ski resorts.
    
    Returns:
        JSON string with ski resort data including names, coordinates,
        elevations, and ski area information for 16 major Swiss resorts.
    """
    data_path = Path(__file__).parent / "data" / "swiss-ski-resorts.json"
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
    activity: str = "",
    location: str = "",
    timeframe: str = ""
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
    destination: str = "",
    travel_dates: str = "",
    trip_type: str = ""
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

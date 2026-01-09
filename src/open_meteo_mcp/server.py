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

@mcp.tool()
async def get_weather(
    latitude: float,
    longitude: float,
    forecast_days: int = 7,
    include_hourly: bool = True,
    timezone: str = "auto"
) -> dict:
    """
    Get weather forecast for a location (temperature, rain, sunshine).
    
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
        Weather forecast data with current conditions, hourly and daily forecasts
    """
    forecast = await client.get_weather(
        latitude=latitude,
        longitude=longitude,
        forecast_days=forecast_days,
        include_hourly=include_hourly,
        timezone=timezone
    )
    return forecast.model_dump()


@mcp.tool()
async def get_snow_conditions(
    latitude: float,
    longitude: float,
    forecast_days: int = 7,
    include_hourly: bool = True,
    timezone: str = "Europe/Zurich"
) -> dict:
    """
    Get snow conditions and forecasts for mountain locations.
    
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
        Snow conditions with depth, snowfall, and temperature data
    """
    conditions = await client.get_snow_conditions(
        latitude=latitude,
        longitude=longitude,
        forecast_days=forecast_days,
        include_hourly=include_hourly,
        timezone=timezone
    )
    return conditions.model_dump()


# ============================================================================
# RESOURCES
# ============================================================================

@mcp.resource("weather://codes")
async def weather_codes() -> str:
    """
    WMO weather code reference with descriptions, categories, and travel impact.
    
    Use this to interpret weather_code values returned by weather tools.
    Contains 28 weather codes with:
    - Description (e.g., "Clear sky", "Moderate rain")
    - Category (Clear, Cloudy, Rain, Snow, Fog, Thunderstorm)
    - Icon suggestions
    - Travel impact assessments
    """
    data_path = Path(__file__).parent / "data" / "weather-codes.json"
    return data_path.read_text(encoding="utf-8")


@mcp.resource("weather://swiss-ski-resorts")
async def swiss_ski_resorts() -> str:
    """
    Popular Swiss ski resort coordinates and metadata.
    
    Contains 16 major Swiss ski resorts including:
    - Zermatt, Verbier, St. Moritz, Davos, Grindelwald
    - Coordinates (latitude, longitude)
    - Elevation
    - Ski area names
    
    Use this resource to get accurate coordinates for ski resorts.
    """
    data_path = Path(__file__).parent / "data" / "swiss-ski-resorts.json"
    return data_path.read_text(encoding="utf-8")


@mcp.resource("weather://parameters")
async def weather_parameters() -> str:
    """
    Available weather and snow parameters from Open-Meteo API.
    
    Documents all available parameters for:
    - Hourly weather data
    - Daily weather data
    - Snow conditions
    - Units and descriptions
    
    Use this to understand what data is available from the API.
    """
    data_path = Path(__file__).parent / "data" / "weather-parameters.json"
    return data_path.read_text(encoding="utf-8")


# ============================================================================
# PROMPTS
# ============================================================================

@mcp.prompt()
async def ski_trip_weather(resort: str = "", dates: str = "") -> str:
    """
    Guide for checking snow conditions and weather for ski trips to Swiss resorts.
    
    Args:
        resort: Name of the Swiss ski resort (e.g., 'Zermatt', 'Verbier', 'St. Moritz')
        dates: Specific dates or time period (e.g., 'this weekend', 'next week', 'January 10-15')
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


@mcp.prompt()
async def plan_outdoor_activity(
    activity: str = "",
    location: str = "",
    timeframe: str = ""
) -> str:
    """
    Weather-aware outdoor activity planning workflow for hiking, cycling, and other outdoor pursuits.
    
    Args:
        activity: Type of outdoor activity (e.g., 'hiking', 'cycling', 'climbing', 'camping')
        location: Location for the activity (city, mountain, trail name)
        timeframe: When planning to do the activity (e.g., 'this weekend', 'next week', specific dates)
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


@mcp.prompt()
async def weather_aware_travel(
    destination: str = "",
    travel_dates: str = "",
    trip_type: str = ""
) -> str:
    """
    Integration pattern for combining weather forecasts with journey planning.
    
    Args:
        destination: Travel destination (city, resort, or location name)
        travel_dates: When traveling (e.g., 'tomorrow', 'this weekend', 'January 10-15')
        trip_type: Type of trip (e.g., 'day trip', 'weekend getaway', 'ski trip', 'business travel')
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

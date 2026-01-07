# MCP Prompts Documentation

This document provides comprehensive documentation for all MCP Prompts in the open-meteo-mcp server.

## Overview

MCP Prompts are workflow guides that teach LLMs how to effectively use weather tools and resources. They provide structured, step-by-step instructions for common weather-related tasks, ensuring consistent and high-quality responses.

---

## Prompt 1: Ski Trip Weather

### Metadata

- **Prompt Name**: `ski-trip-weather`
- **Description**: Guide for checking snow conditions and weather for ski trips to Swiss resorts
- **Implementation**: `SkiTripWeatherPrompt.java`
- **Provider**: `McpPromptProvider`

### Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| resort | string | No | Name of the Swiss ski resort (e.g., 'Zermatt', 'Verbier', 'St. Moritz') |
| dates | string | No | Specific dates or time period (e.g., 'this weekend', 'next week', 'January 10-15') |

### Purpose

Guides LLMs through a comprehensive ski trip planning workflow that combines resort lookup, snow conditions, weather forecasts, and condition assessment to provide actionable ski trip recommendations.

### Workflow Steps

#### Step 1: Identify the Resort

- Use `swiss-ski-resorts` resource to get accurate coordinates
- Extract latitude and longitude from resource data
- Verify resort name matches (handles variations like "St Moritz" vs "St. Moritz")

#### Step 2: Check Snow Conditions

- Call `getSnowConditions` tool with resort coordinates
- Key metrics to report:
  - Current snow depth (meters)
  - Recent snowfall (last 24-48 hours)
  - Forecast snowfall for next 7 days
  - Temperature trends (affects snow quality)

#### Step 3: Check General Weather

- Call `getWeather` tool for same coordinates
- Focus on:
  - Temperature (for comfort and snow quality)
  - Weather codes (use `weather-codes` resource to interpret)
  - Wind conditions (important for lift operations)
  - Visibility (fog can close lifts)

#### Step 4: Provide Ski Condition Assessment

**Excellent Conditions**:

- Fresh snow (>10cm in last 24-48h)
- Cold temperatures (-5°C to -15°C)
- Clear skies (codes 0-1)
- Light winds (<20 km/h)

**Good Conditions**:

- Adequate snow depth (>50cm base)
- Stable temperatures (-10°C to 0°C)
- Partly cloudy (codes 2-3)
- Moderate winds (20-30 km/h)

**Fair Conditions**:

- Limited recent snow
- Warmer temperatures (risk of icy conditions)
- Variable weather (codes 51-65)
- Higher winds (30-40 km/h)

**Poor Conditions**:

- No recent snow
- Very warm temperatures (>5°C, wet snow)
- Heavy fog (codes 45-48) or storms (codes 95-99)
- Extreme winds (>40 km/h, lift closures likely)

#### Step 5: Recommendations

- Suggest best days within forecast period
- Warn about potential issues (warm temps, storms, fog)
- Recommend appropriate gear based on conditions
- Mention crowd expectations (fresh powder = busy)

### Example Interaction

**User Query**: "What are the ski conditions in Zermatt this weekend?"

**LLM Response Flow**:

1. **Resort Lookup**:

   ```
   Reading swiss-ski-resorts resource...
   Found: Zermatt (45.9763°N, 7.6586°E)
   Elevation: 1620m
   Ski Area: Matterhorn Glacier Paradise
   ```

2. **Snow Conditions Check**:

   ```
   Calling getSnowConditions(45.9763, 7.6586)...
   Current snow depth: 1.2m (excellent base)
   Fresh snow (24h): 15cm
   Forecast: 5-10cm Sunday
   ```

3. **Weather Check**:

   ```
   Calling getWeather(45.9763, 7.6586)...
   Saturday: Partly cloudy, -6°C, code 2
   Sunday: Light snow, -10°C, code 71
   Wind: 12 km/h (lifts operating)
   ```

4. **Assessment**:

   ```
   Conditions: EXCELLENT
   - Fresh powder from recent snowfall
   - Cold temps preserving snow quality
   - Clear to partly cloudy weather
   - Sunday: More fresh snow expected
   ```

5. **Recommendations**:

   ```
   Best day: Sunday (fresh powder)
   Bring: Powder skis, warm layers (-10°C)
   Note: Expect crowds due to excellent conditions
   ```

### Related Resources

- **swiss-ski-resorts**: Resort coordinates and metadata
- **weather-codes**: Interpret weather condition codes
- **weather-parameters**: Understanding snow depth, snowfall metrics

### Related Tools

- **getSnowConditions**: Snow depth, snowfall, mountain weather
- **getWeather**: Temperature, precipitation, wind, visibility

### Use Cases

1. **Weekend Ski Trip Planning**: "Where should I ski this weekend?"
2. **Multi-Resort Comparison**: "Compare conditions at Verbier, Zermatt, and St. Moritz"
3. **Week-Long Trip**: "Best resort for skiing next week?"
4. **Specific Date Planning**: "Snow conditions in Davos on January 15th?"

---

## Prompt 2: Plan Outdoor Activity

### Metadata

- **Prompt Name**: `plan-outdoor-activity`
- **Description**: Weather-aware outdoor activity planning workflow for hiking, cycling, and other outdoor pursuits
- **Implementation**: `OutdoorActivityPrompt.java`
- **Provider**: `McpPromptProvider`

### Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| activity | string | No | Type of outdoor activity (e.g., 'hiking', 'cycling', 'climbing', 'camping') |
| location | string | No | Location for the activity (city, mountain, trail name) |
| timeframe | string | No | When planning to do the activity (e.g., 'this weekend', 'next week', specific dates) |

### Purpose

Guides LLMs through weather-aware outdoor activity planning, helping users choose suitable dates and prepare for weather conditions based on activity-specific requirements.

### Workflow Steps

#### Step 1: Understand the Activity

Determine weather sensitivity:

**High Sensitivity** (avoid rain, storms, high winds):

- Rock climbing
- Via ferrata
- High-altitude hiking
- Mountaineering
- Paragliding

**Medium Sensitivity** (manageable in light rain, avoid storms):

- Day hiking
- Mountain biking
- Road cycling
- Trail running
- Camping

**Low Sensitivity** (possible in most conditions except severe weather):

- Walking
- Urban sightseeing
- Photography
- Picnicking

#### Step 2: Get Location Coordinates

- If user provides specific location, use those coordinates
- For Swiss locations, reference common destinations
- Ensure latitude and longitude are available

#### Step 3: Check Weather Forecast

- Call `getWeather` tool with appropriate forecast days (typically 3-7 days)
- Key metrics for outdoor activities:
  - **Precipitation**: Rain/snow amounts (mm)
  - **Weather codes**: Use `weather-codes` resource
  - **Temperature**: Comfort and safety
  - **Wind**: Important for exposed areas
  - **Visibility**: Critical for mountain activities

#### Step 4: Assess Suitability

**Ideal Conditions**:

- Clear or partly cloudy (codes 0-2)
- No precipitation or minimal (<1mm)
- Moderate temperatures (10-25°C for summer activities)
- Light winds (<20 km/h for exposed areas)

**Acceptable Conditions**:

- Overcast but dry (code 3)
- Light drizzle (<2mm, codes 51-53)
- Appropriate temperature range for activity
- Moderate winds (20-30 km/h)

**Poor Conditions**:

- Heavy rain (codes 61-65, >5mm)
- Thunderstorms (codes 95-99)
- Extreme temperatures
- High winds (>30 km/h for exposed activities)
- Fog (codes 45-48) for mountain activities

#### Step 5: Provide Recommendations

- Identify best days within forecast period
- Suggest alternative dates if conditions are poor
- Recommend weather-appropriate gear
- Provide safety warnings for severe weather

### Activity-Specific Guidelines

#### Hiking

- **Avoid**: Thunderstorms (lightning risk on ridges/peaks)
- **Check**: Snow conditions for high-altitude trails
- **Consider**: Visibility for mountain routes
- **Temperature**: 5-25°C ideal
- **Rain tolerance**: Light rain acceptable with proper gear

#### Cycling

- **Avoid**: Heavy rain (slippery roads), strong headwinds
- **Check**: Wind conditions for exposed routes
- **Temperature**: 10-28°C comfortable
- **Rain tolerance**: Light rain acceptable, avoid >5mm/h

#### Climbing/Via Ferrata

- **Requires**: Dry conditions (wet rock is dangerous)
- **Avoid**: Any rain or recent rain (<24h)
- **Check**: Afternoon thunderstorms in summer
- **Temperature**: 10-20°C ideal
- **Rain tolerance**: Zero - must be completely dry

#### Camping

- **Avoid**: Heavy rain and storms
- **Check**: Overnight temperatures
- **Wind**: Important for tent stability (<30 km/h)
- **Temperature**: >5°C for comfort
- **Rain tolerance**: Light rain manageable with good tent

### Example Interaction

**User Query**: "I want to hike the Eiger Trail next week. What's the weather looking like?"

**LLM Response Flow**:

1. **Activity Assessment**:

   ```
   Activity: Hiking (Eiger Trail - exposed mountain route)
   Sensitivity: Medium-High (exposed sections)
   Location: Grindelwald region (46.6244°N, 8.0411°E)
   ```

2. **Weather Forecast**:

   ```
   Calling getWeather for 7-day forecast...
   
   Mon-Tue: Partly cloudy, 15-18°C, 0mm - IDEAL
   Wed: Overcast, 14°C, light drizzle 2mm - ACCEPTABLE
   Thu-Fri: Rain showers, 12°C, 8-12mm - NOT RECOMMENDED
   Sat-Sun: Clearing, 16-19°C, 0mm - IDEAL
   ```

3. **Suitability Assessment**:

   ```
   Best days: Monday, Tuesday, Saturday, Sunday
   Acceptable: Wednesday (bring rain gear)
   Avoid: Thursday-Friday (significant rain, slippery trail)
   ```

4. **Recommendations**:

   ```
   RECOMMENDED DAYS: Mon, Tue, Sat, Sun
   - Clear to partly cloudy
   - No precipitation
   - Perfect temps (15-19°C)
   
   WHAT TO BRING:
   - Layers (temps vary 15-19°C)
   - Sun protection (clear days)
   - Light rain jacket (just in case)
   - Sturdy hiking boots
   
   SAFETY NOTE:
   Eiger Trail has exposed sections. Check local conditions
   before starting, especially after rain. Trail can be
   slippery when wet.
   ```

### Related Resources

- **weather-codes**: Interpret weather conditions
- **weather-parameters**: Understanding precipitation, wind metrics

### Related Tools

- **getWeather**: Comprehensive weather forecast
- **getSnowConditions**: For high-altitude activities in winter

### Use Cases

1. **Hiking Trip Planning**: "Best day to hike this week?"
2. **Cycling Route Planning**: "Good weather for cycling around Lake Geneva?"
3. **Climbing Conditions**: "Can I climb outdoors this weekend?"
4. **Multi-Day Camping**: "Weather for camping next week?"

---

## Prompt 3: Weather-Aware Travel

### Metadata

- **Prompt Name**: `weather-aware-travel`
- **Description**: Integration pattern for combining weather forecasts with journey planning
- **Implementation**: `WeatherAwareTravelPrompt.java`
- **Provider**: `McpPromptProvider`

### Arguments

| Argument | Type | Required | Description |
|----------|------|----------|-------------|
| destination | string | No | Travel destination (city, resort, or location name) |
| travel_dates | string | No | When traveling (e.g., 'tomorrow', 'this weekend', 'January 10-15') |
| trip_type | string | No | Type of trip (e.g., 'day trip', 'weekend getaway', 'ski trip', 'business travel') |

### Purpose

Guides LLMs on integrating weather information with journey planning, helping users prepare for weather conditions at their destination and make weather-appropriate travel decisions.

### Workflow Steps

#### Step 1: Extract Destination Information

- Identify travel destination from user's query
- If coordinates available from journey planning tools, use those
- Otherwise, use known coordinates for major Swiss cities/destinations

#### Step 2: Determine Travel Timeframe

- Extract travel dates from query
- For trip planning, focus on arrival and stay period
- For day trips, check weather for entire day
- Default to 3-7 day forecast if dates unclear

#### Step 3: Check Destination Weather

- Call `getWeather` tool with destination coordinates
- For mountain destinations, also call `getSnowConditions` if relevant
- Focus on:
  - Overall conditions (clear, rainy, snowy)
  - Temperature range
  - Precipitation amounts
  - Any severe weather warnings

#### Step 4: Provide Weather-Aware Travel Advice

**Packing Recommendations**:

| Conditions | What to Pack |
|------------|--------------|
| Clear/Sunny (codes 0-1) | Sunglasses, sunscreen, light clothing |
| Partly Cloudy (codes 2-3) | Layers, light jacket |
| Rainy (codes 51-82) | Waterproof jacket, umbrella, water-resistant shoes |
| Snowy (codes 71-86) | Winter coat, warm layers, winter boots, gloves |
| Stormy (codes 95-99) | Postpone if possible, or prepare for indoor activities |

**Temperature-Based Advice**:

| Temperature | Clothing Recommendations |
|-------------|-------------------------|
| Cold (<5°C) | Warm coat, gloves, hat, thermal layers |
| Cool (5-15°C) | Jacket, long sleeves, layers |
| Mild (15-25°C) | Light jacket, comfortable clothing |
| Warm (>25°C) | Light clothing, sun protection, hydration |

**Travel Impact Assessment**:

| Impact Level | Conditions | Advice |
|--------------|------------|--------|
| No Impact | Clear to partly cloudy, normal temps | Normal travel, no special prep |
| Minor Impact | Light rain, cold temps | Bring umbrella, dress warm |
| Moderate Impact | Heavy rain, snow | Delays possible, slower travel |
| Significant Impact | Storms, extreme weather | Consider rescheduling |

#### Step 5: Activity Suggestions

Based on weather, suggest appropriate activities:

**Good Weather**:

- Outdoor sightseeing
- Hiking and nature walks
- Lake activities
- Outdoor dining
- Photography

**Mixed Weather**:

- Flexible plans (indoor/outdoor mix)
- Covered markets
- Short outdoor excursions
- Museums with outdoor components

**Poor Weather**:

- Museums and galleries
- Indoor attractions
- Covered shopping areas
- Restaurants and cafes
- Spa and wellness

### Integration with Journey Planning

When used alongside journey planning tools:

1. Get destination coordinates from journey/station data
2. Check weather for arrival time and duration of stay
3. Warn about weather-related travel delays (snow, storms)
4. Suggest weather-appropriate activities at destination

### Example Interaction

**User Query**: "I'm traveling to Lucerne tomorrow. What should I pack?"

**LLM Response Flow**:

1. **Destination Identification**:

   ```
   Destination: Lucerne
   Coordinates: 47.0502°N, 8.3093°E
   Timeframe: Tomorrow (Jan 7, 2026)
   ```

2. **Weather Check**:

   ```
   Calling getWeather(47.0502, 8.3093)...
   
   Tomorrow's Weather:
   - Condition: Partly cloudy (code 2)
   - Temperature: 8-14°C
   - Precipitation: 0mm (dry day)
   - Wind: 15 km/h (light breeze)
   ```

3. **Packing Recommendations**:

   ```
   WHAT TO PACK:
   - Light jacket or sweater (temps 8-14°C)
   - Comfortable walking shoes (dry conditions)
   - Sunglasses (partly cloudy, some sun)
   - Layers (temperature varies throughout day)
   
   OPTIONAL:
   - Light umbrella (just in case)
   - Camera (good visibility for photos)
   ```

4. **Travel Impact**:

   ```
   TRAVEL IMPACT: None expected
   - Good conditions for sightseeing
   - No delays anticipated
   - Normal travel times
   ```

5. **Activity Suggestions**:

   ```
   RECOMMENDED ACTIVITIES:
   - Chapel Bridge and old town walking tour
   - Lake Lucerne boat tours (pleasant weather)
   - Mt. Pilatus or Rigi excursions
     (check mountain weather separately)
   - Outdoor dining at lakeside restaurants
   
   NOTE: Morning will be cooler (8°C), warming to
   14°C by afternoon. Start with layers and remove
   as it warms up.
   ```

### Special Cases

#### Mountain Destinations

- Always check `getSnowConditions` in addition to weather
- Warn about altitude-related weather changes
- Check for avalanche risk in winter (mention in severe weather)
- Temperature drops ~6°C per 1000m elevation gain

#### Multi-Day Trips

- Provide day-by-day weather summary
- Suggest best days for outdoor vs. indoor activities
- Recommend packing for variable conditions
- Highlight any severe weather days

#### International Travel

- Weather tools work worldwide, not just Switzerland
- Adjust temperature/condition expectations for destination climate
- Consider seasonal differences
- Mention time zone for weather timing

### Example Integrated Workflow

**User Query**: "Plan a trip from Zurich to Zermatt this weekend"

**Integrated Response Flow**:

1. **Journey Planning** (from journey-service-mcp):

   ```
   Route: Zurich HB → Zermatt
   Duration: 3h 12min
   Departure: Saturday 08:37
   ```

2. **Destination Weather** (from open-meteo-mcp):

   ```
   Zermatt Weekend Weather:
   Sat: Partly cloudy, -4°C, no snow
   Sun: Light snow, -8°C, 5cm expected
   ```

3. **Snow Conditions** (from open-meteo-mcp):

   ```
   Current: 1.1m base, excellent conditions
   Fresh snow: 12cm in last 24h
   Forecast: Additional 5cm Sunday
   ```

4. **Combined Recommendations**:

   ```
   TRAVEL PLAN:
   - Take 08:37 train Saturday (3h 12min)
   - Arrive Zermatt 11:49
   - Weekend ski conditions: EXCELLENT
   
   PACKING LIST:
   - Ski gear (powder skis recommended)
   - Warm layers (-8°C Sunday)
   - Winter coat, gloves, hat
   - Goggles (fresh snow expected)
   
   ACTIVITY PLAN:
   - Saturday: Ski all day (partly cloudy, good visibility)
   - Sunday: BEST DAY (fresh powder, 5cm new snow)
   
   TRAVEL NOTES:
   - No weather delays expected
   - Zermatt is car-free (walk or electric taxi from station)
   - Book ski rental in advance (busy weekend)
   ```

### Related Resources

- **weather-codes**: Interpret weather conditions
- **swiss-ski-resorts**: Mountain destination coordinates
- **weather-parameters**: Understanding weather metrics

### Related Tools

- **getWeather**: Destination weather forecast
- **getSnowConditions**: Mountain/ski destination conditions
- **Journey planning tools** (from other MCP servers): Get destination coordinates

### Use Cases

1. **Day Trip Packing**: "What should I bring to Bern tomorrow?"
2. **Weekend Getaway**: "Weather for a weekend in Lugano?"
3. **Ski Trip Planning**: "Traveling to Verbier next week, what to expect?"
4. **Business Travel**: "Weather in Geneva for my conference?"
5. **Multi-City Tour**: "Weather for Zurich, Lucerne, Interlaken next week?"

---

## Prompt Discovery

All prompts are automatically discovered and registered via the MCP protocol:

### List Prompts

**MCP Method**: `prompts/list`

**Response**:

```json
{
  "prompts": [
    {
      "name": "ski-trip-weather",
      "description": "Guide for checking snow conditions and weather for ski trips",
      "arguments": [
        {
          "name": "resort",
          "description": "Name of the Swiss ski resort",
          "required": false
        },
        {
          "name": "dates",
          "description": "Specific dates or time period",
          "required": false
        }
      ]
    },
    {
      "name": "plan-outdoor-activity",
      "description": "Weather-aware outdoor activity planning workflow",
      "arguments": [...]
    },
    {
      "name": "weather-aware-travel",
      "description": "Integration pattern for combining weather with journey planning",
      "arguments": [...]
    }
  ]
}
```

### Get Prompt

**MCP Method**: `prompts/get`

**Request**:

```json
{
  "name": "ski-trip-weather",
  "arguments": {
    "resort": "Zermatt",
    "dates": "this weekend"
  }
}
```

**Response**: Full prompt template with interpolated arguments

---

## Technical Implementation

### Architecture

All prompts follow the same pattern:

1. **Interface**: Implement `McpPromptProvider` from `sbb-mcp-commons`
2. **Component**: Annotated with `@Component` for Spring auto-discovery
3. **Return Type**: `List<McpPrompt>` (allows multiple prompts per provider)
4. **Prompt Structure**: Name, description, arguments, template

### Required Methods

```java
public interface McpPromptProvider {
    List<McpPrompt> getPrompts();  // Returns list of prompts
}
```

### Prompt Record Structure

```java
public record McpPrompt(
    String name,                          // Unique prompt name
    String description,                   // Human-readable description
    List<McpPromptArgument> arguments,   // Optional arguments
    String template                       // Full workflow template
) {}

public record McpPromptArgument(
    String name,          // Argument name
    String description,   // Argument description
    boolean required      // Whether argument is required
) {}
```

### Configuration

Prompts are registered in `McpConfig.java`:

```java
@Bean
public List<McpPromptProvider> mcpPrompts(
        SkiTripWeatherPrompt skiTripWeatherPrompt,
        OutdoorActivityPrompt outdoorActivityPrompt,
        WeatherAwareTravelPrompt weatherAwareTravelPrompt) {
    return List.of(skiTripWeatherPrompt, outdoorActivityPrompt, weatherAwareTravelPrompt);
}
```

---

## Best Practices for LLMs

### When to Use Prompts

1. **Ski Trip Planning**: Use `ski-trip-weather` for any ski-related queries
2. **Outdoor Activities**: Use `plan-outdoor-activity` for hiking, cycling, climbing, etc.
3. **Travel Planning**: Use `weather-aware-travel` when combining weather with journeys
4. **Follow Workflows**: Adhere to the step-by-step workflows in templates
5. **Cite Prompts**: Mention that you're following a structured workflow

### Prompt Usage Patterns

**Pattern 1: Direct Prompt Invocation**

```
User asks about ski conditions
→ Invoke ski-trip-weather prompt
→ Follow workflow steps
→ Provide structured response
```

**Pattern 2: Prompt Chaining**

```
User asks about weekend trip to ski resort
→ Use weather-aware-travel for packing
→ Use ski-trip-weather for conditions
→ Combine recommendations
```

**Pattern 3: Adaptive Prompts**

```
User asks general outdoor question
→ Determine activity type
→ Select appropriate prompt
→ Follow relevant workflow
```

### Customization

While prompts provide structured workflows, LLMs should:

- **Adapt** language to user's tone and expertise level
- **Abbreviate** steps for simple queries
- **Expand** details for complex planning
- **Combine** multiple prompts when appropriate
- **Personalize** recommendations based on user context

---

## Maintenance

### Updating Prompt Templates

1. Edit Java class in `src/main/java/com/openmeteo/prompts/`
2. Modify `TEMPLATE` constant
3. Update `DESCRIPTION` if workflow changes
4. Add/remove arguments if needed
5. Rebuild project: `mvn clean compile`
6. Restart server

### Adding New Prompts

1. Create Java class implementing `McpPromptProvider`
2. Add `@Component` annotation
3. Define prompt metadata (name, description)
4. Create argument list
5. Write comprehensive template
6. Implement `getPrompts()` method
7. Register in `McpConfig.java`
8. Update documentation

---

## Related Documentation

- [MCP Resources Documentation](RESOURCES.md)
- [Open-Meteo API Documentation](https://open-meteo.com/en/docs)
- [sbb-mcp-commons Library](https://github.com/schlpbch/sbb-mcp-commons)
- [MCP Protocol Specification](https://modelcontextprotocol.io/)

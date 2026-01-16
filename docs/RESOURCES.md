# MCP Resources Documentation

This document provides comprehensive documentation for all MCP Resources in the open-meteo-mcp server.

## Overview

MCP Resources are discoverable reference data that LLMs can access to improve accuracy and reduce hallucination. The open-meteo-mcp server provides three resources related to weather interpretation and Swiss ski destinations.

---

## Resource 1: Weather Codes

### Metadata

- **Resource Name**: `weather-codes`
- **Resource URI**: `weather://codes`
- **Resource Endpoint**: `/mcp/weather-codes`
- **Data Model**: `application/json`
- **Implementation**: `WeatherCodesResource.java`
- **Data File**: `src/main/resources/data/weather-codes.json`

### Purpose

Provides authoritative reference data for interpreting WMO (World Meteorological Organization) weather codes returned by the Open-Meteo API. This prevents LLMs from hallucinating or misinterpreting weather condition codes.

### Data Structure

```json
{
  "codes": [
    {
      "code": 0,
      "description": "Clear sky",
      "category": "Clear",
      "icon": "☀️",
      "travelImpact": "Ideal conditions"
    },
    ...
  ],
  "categories": {
    "Clear": {
      "codes": [0, 1],
      "characteristics": "Good visibility, minimal precipitation",
      "travelImpact": "Ideal conditions"
    },
    ...
  },
  "source": "WMO standard as implemented by Open-Meteo API",
  "reference": "https://open-meteo.com/en/docs"
}
```

### Content Summary

- **28 Weather Codes**: Complete WMO code set (0-99)
- **6 Categories**: Clear, Cloudy, Fog, Rain, Snow, Thunderstorms
- **Attributes per Code**:
  - Numeric code (0-99)
  - Human-readable description
  - Category classification
  - Emoji icon suggestion
  - Travel impact assessment

### Use Cases

1. **Weather Code Interpretation**: When `getWeather` or `getSnowConditions` returns a `weather_code` value, LLMs can reference this resource to provide accurate descriptions
2. **Travel Planning**: Assess travel impact based on weather conditions
3. **Activity Recommendations**: Determine suitability for outdoor activities based on weather categories
4. **User Communication**: Translate numeric codes into user-friendly descriptions

### Example Usage

```
LLM receives: weather_code = 61

LLM reads resource → Finds code 61:
- Description: "Rain: Slight intensity"
- Category: "Rain"
- Icon: "🌧️"
- Travel Impact: "Possible delays, wet surfaces"

LLM responds: "Light rain expected (3mm). Bring an umbrella and expect possible minor delays."
```

### Implementation Details

- **Caching**: Data is cached in memory after first load for performance
- **Loading**: JSON file loaded from classpath on first access
- **Error Handling**: Returns error JSON if data file cannot be loaded
- **Availability**: Always available (no dynamic dependencies)

---

...existing code...

```json
{
  "resorts": [
    {
      "name": "Zermatt",
      "region": "Valais",
      "latitude": 45.9763,
      "longitude": 7.6586,
      "elevation": 1620,
      "description": "Car-free alpine resort at the foot of the Matterhorn",
      "skiArea": "Matterhorn Glacier Paradise"
    },
    ...
  ],
  "metadata": {
    "totalResorts": 16,
    "regions": ["Valais", "Graubünden", "Bern", "Obwalden", "Uri"],
    "source": "Swiss Tourism and ski area data",
    "lastUpdated": "2026-01-06"
  }
}
```

### Content Summary

- **16 Major Resorts**: Top Swiss ski destinations
- **5 Regions**: Valais, Graubünden, Bern, Obwalden, Uri
- **Attributes per Resort**:
  - Resort name (canonical)
  - Canton/region
  - Precise GPS coordinates (latitude, longitude)
  - Base elevation (meters)
  - Description
  - Ski area name

### Featured Resorts

| Resort | Region | Elevation | Notable Feature |
|--------|--------|-----------|----------------|
| Zermatt | Valais | 1620m | Matterhorn, car-free |
| Verbier | Valais | 1500m | Four Valleys ski area |
| St. Moritz | Graubünden | 1856m | Luxury resort, Olympics host |
| Davos | Graubünden | 1560m | Largest Swiss resort |
| Grindelwald | Bern | 1034m | Eiger North Face |
| Saas-Fee | Valais | 1800m | Year-round glacier skiing |
| Laax | Graubünden | 1100m | Freestyle paradise |
| Engelberg | Obwalden | 1050m | Titlis glacier |
| Andermatt | Uri | 1444m | Modern ski area |
| Wengen | Bern | 1274m | Lauberhorn race |
| Arosa | Graubünden | 1775m | Family-friendly |
| Crans-Montana | Valais | 1500m | Sunny plateau |
| Klosters | Graubünden | 1191m | Traditional village |
| Lenzerheide | Graubünden | 1476m | Connected to Arosa |
| Adelboden | Bern | 1350m | Bernese Oberland |
| Gstaad | Bern | 1050m | Exclusive luxury |

### Use Cases

1. **Coordinate Lookup**: Get accurate coordinates for snow condition queries
2. **Resort Comparison**: Compare multiple resorts for trip planning
3. **Regional Planning**: Find resorts in specific cantons
4. **Elevation Context**: Understand altitude for snow reliability
5. **Ski Area Information**: Learn about connected ski areas

### Example Usage

```
User: "What are the snow conditions in Zermatt?"

...existing code...
```

### Implementation Details

- **Caching**: Data is cached in memory after first load
- **Loading**: JSON file loaded from classpath on first access
- **Error Handling**: Returns error JSON if data file cannot be loaded
- **Availability**: Always available
- **Coordinate Precision**: 4 decimal places (~11m accuracy)

---

## Resource 3: Weather Parameters

### Metadata

- **Resource Name**: `weather-parameters`
- **Resource URI**: `weather://parameters`
- **Resource Endpoint**: `/mcp/weather-parameters`
- **Data Model**: `application/json`
- **Implementation**: `WeatherParametersResource.java`
- **Data File**: `src/main/resources/data/weather-parameters.json`

### Purpose

Documents all available weather and snow parameters from the Open-Meteo API, helping LLMs understand what data is available and how to interpret measurements.

### Data Structure

```json
{
  "weatherParameters": {
    "hourly": [
      {
        "name": "temperature_2m",
        "description": "Air temperature at 2 meters above ground",
        "unit": "°C",
        "category": "Temperature"
      },
      ...
    ],
    "daily": [...]
  },
  "categories": {
    "Temperature": "Air temperature measurements",
    ...
  },
  "usage": {
    "weather": {
      "hourly": ["temperature_2m", "relative_humidity_2m", ...],
      "daily": ["temperature_2m_max", "temperature_2m_min", ...]
    },
    "snow": {
      "hourly": ["snowfall", "snow_depth", "temperature_2m"],
      "daily": ["snowfall_sum", "snow_depth_max", ...]
    }
  }
}
```

### Content Summary

#### Hourly Parameters (12 parameters)

| Parameter | Description | Unit | Category |
|-----------|-------------|------|----------|
| temperature_2m | Air temperature at 2m | °C | Temperature |
| relative_humidity_2m | Relative humidity at 2m | % | Humidity |
| precipitation | Total precipitation | mm | Precipitation |
| rain | Rain from weather systems | mm | Precipitation |
| weather_code | WMO weather code | code | Conditions |
| cloud_cover | Total cloud cover | % | Clouds |
| wind_speed_10m | Wind speed at 10m | km/h | Wind |
| wind_direction_10m | Wind direction at 10m | ° | Wind |
| wind_gusts_10m | Wind gusts at 10m | km/h | Wind |
| visibility | Viewing distance | meters | Visibility |
| snowfall | Snowfall amount | cm | Snow |
| snow_depth | Snow depth on ground | meters | Snow |

#### Daily Parameters (10 parameters)

| Parameter | Description | Unit | Category |
|-----------|-------------|------|----------|
| temperature_2m_max | Maximum daily temperature | °C | Temperature |
| temperature_2m_min | Minimum daily temperature | °C | Temperature |
| precipitation_sum | Sum of daily precipitation | mm | Precipitation |
| rain_sum | Sum of daily rain | mm | Precipitation |
| sunshine_duration | Seconds of sunshine | seconds | Sun |
| weather_code | Most severe daily code | code | Conditions |
| snowfall_sum | Sum of daily snowfall | cm | Snow |
| snow_depth_max | Maximum daily snow depth | meters | Snow |
| wind_speed_10m_max | Maximum daily wind speed | km/h | Wind |
| wind_gusts_10m_max | Maximum daily wind gusts | km/h | Wind |

#### Categories (9 categories)

- **Temperature**: Air temperature measurements
- **Humidity**: Moisture content in the air
- **Precipitation**: Rain, snow, and other forms of water
- **Conditions**: Overall weather conditions and codes
- **Clouds**: Cloud coverage and types
- **Wind**: Wind speed, direction, and gusts
- **Visibility**: How far you can see
- **Snow**: Snow-related measurements
- **Sun**: Sunshine and solar radiation

### Use Cases

1. **Parameter Understanding**: Learn what each parameter measures
2. **Unit Conversion**: Understand units for proper interpretation
3. **Tool Usage Guidance**: Know which parameters are available for queries
4. **Data Interpretation**: Understand the meaning of returned values
5. **Query Optimization**: Select appropriate parameters for specific use cases

### Example Usage

```
User: "What does snow_depth mean?"

LLM reads weather-parameters resource → Finds snow_depth:
- Description: "Snow depth on the ground"
- Unit: "meters"
- Category: "Snow"
- Available in: hourly and daily (as snow_depth_max)

LLM responds: "Snow depth measures the total depth of snow on the ground in meters. For example, 1.2m means there's 1.2 meters (120cm) of snow accumulated."
```

### Implementation Details

- **Caching**: Data is cached in memory after first load
- **Loading**: JSON file loaded from classpath on first access
- **Error Handling**: Returns error JSON if data file cannot be loaded
- **Availability**: Always available
- **Reference**: Based on Open-Meteo API documentation

---

## Resource Discovery

All resources are automatically discovered and registered via the MCP protocol:

### List Resources

**MCP Method**: `resources/list`

**Response**:

```json
{
  "resources": [
    {
      "name": "weather-codes",
      "uri": "weather://codes",
      "description": "WMO weather code reference...",
      "mimeType": "application/json"
    },
    {
    ...existing code...
    },
    {
      "name": "weather-parameters",
      "uri": "weather://parameters",
      "description": "Available weather and snow parameters...",
      "mimeType": "application/json"
    }
  ]
}
```

### Read Resource

**MCP Method**: `resources/read`

**Request**:

```json
{
  "uri": "weather://codes"
}
```

**Response**: Full JSON data from the resource

---

## Technical Implementation

### Architecture

All resources follow the same pattern:

1. **Interface**: Implement `McpResource` from `sbb-mcp-commons`
2. **Component**: Annotated with `@Component` for Spring auto-discovery
3. **Data Loading**: JSON files in `src/main/resources/data/`
4. **Caching**: In-memory caching for performance
5. **Error Handling**: Graceful degradation with error JSON

### Required Methods

```java
public interface McpResource {
    String getResourceName();           // Unique name
    String getResourceDescription();    // Human-readable description
    String getResourceEndpoint();       // REST endpoint path
    String getResourceDataModel();      // MIME type
    Mono<Object> readResource();        // Reactive data retrieval
    default boolean isAvailable();      // Availability check
    default String getResourceUri();    // URI scheme
}
```

### Configuration

Resources are registered in `McpConfig.java`:

```java
@Bean
public List<McpResource> mcpResources(
        WeatherCodesResource weatherCodesResource,
        SwissSkiResortsResource swissSkiResortsResource,
        WeatherParametersResource weatherParametersResource) {
    return List.of(weatherCodesResource, swissSkiResortsResource, weatherParametersResource);
}
```

### Data File Location

```
src/main/resources/data/
├── weather-codes.json
...existing code...
└── weather-parameters.json
```

---

## Best Practices for LLMs

### When to Use Resources

1. **Always** reference `weather-codes` when interpreting weather_code values
...existing code...
3. **Reference** `weather-parameters` when users ask about specific measurements
4. **Cite** resources in responses to build user trust

### Resource Usage Patterns

**Pattern 1: Code Interpretation**

```
1. Receive weather_code from tool
2. Read weather-codes resource
3. Find matching code
4. Use description + travel impact in response
```

**Pattern 2: Ski Resort Lookup**

```
1. User mentions resort name
...existing code...
3. Find matching resort
4. Extract coordinates
5. Call getSnowConditions with coordinates
```

**Pattern 3: Parameter Explanation**

```
1. User asks about a parameter
2. Read weather-parameters resource
3. Find parameter definition
4. Explain with unit and category context
```

### Error Handling

If a resource cannot be loaded:

- Resource returns `{"error": "Failed to load ... data"}`
- LLM should gracefully degrade
- Inform user that reference data is temporarily unavailable
- Proceed with tool calls using best-effort interpretation

---

## Maintenance

### Updating Resource Data

1. Edit JSON file in `src/main/resources/data/`
2. Validate JSON syntax
3. Rebuild project: `mvn clean compile`
4. Restart server
5. Cache will automatically refresh

### Adding New Resources

1. Create JSON data file in `src/main/resources/data/`
2. Create Java class implementing `McpResource`
3. Add `@Component` annotation
4. Implement all required methods
5. Register in `McpConfig.java`
6. Update documentation

---

## Related Documentation

- [MCP Prompts Documentation](PROMPTS.md)
- [Open-Meteo API Documentation](https://open-meteo.com/en/docs)
- [WMO Weather Codes](../docs/WEATHER_CODES.md)
- [sbb-mcp-commons Library](https://github.com/schlpbch/sbb-mcp-commons)

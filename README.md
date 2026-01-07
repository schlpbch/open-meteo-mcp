# Open Meteo MCP Server

A Model Context Protocol (MCP) server providing weather and snow condition tools via the [Open-Meteo API](https://open-meteo.com/).

## Features

- **Weather Forecasts**: Get current weather and multi-day forecasts for any location
- **Snow Conditions**: Get snow depth, snowfall, and mountain weather data
- **MCP Resources**: Weather codes, ski resort coordinates, API parameters reference
- **MCP Prompts**: Guided workflows for ski trips, outdoor activities, and travel planning
- **Free API**: No API key required - powered by Open-Meteo's free weather API
- **MCP Integration**: Seamlessly integrates with MCP-compatible clients like Claude Desktop

## Tools

### `getWeather`

Get weather forecast for a location with temperature, precipitation, humidity, and more.

**Parameters:**

- `latitude` (required): Latitude in decimal degrees
- `longitude` (required): Longitude in decimal degrees
- `forecastDays` (optional): Number of forecast days (1-16, default: 7)
- `includeHourly` (optional): Include hourly forecasts (default: true)
- `timezone` (optional): Timezone for timestamps (default: "auto")

### `getSnowConditions`

Get snow conditions and forecasts for mountain locations.

**Parameters:**

- `latitude` (required): Latitude in decimal degrees
- `longitude` (required): Longitude in decimal degrees
- `forecastDays` (optional): Number of forecast days (1-16, default: 7)
- `includeHourly` (optional): Include hourly data (default: true)
- `timezone` (optional): Timezone for timestamps (default: "Europe/Zurich")

## Resources

The server provides MCP resources for reference data:

### `weather-codes`

WMO weather code reference with descriptions, categories, and travel impact.

- **URI**: `weather://codes`
- **Format**: JSON
- **Content**: 28 weather codes with interpretations

### `swiss-ski-resorts`

Popular Swiss ski resort coordinates and metadata.

- **URI**: `weather://swiss-ski-resorts`
- **Format**: JSON
- **Content**: 16 major resorts (Zermatt, Verbier, St. Moritz, etc.)

### `weather-parameters`

Available weather and snow parameters from Open-Meteo API.

- **URI**: `weather://parameters`
- **Format**: JSON
- **Content**: Hourly/daily parameters with units and categories

## Prompts

The server provides MCP prompts to guide LLM workflows:

### `ski-trip-weather`

Guide for checking snow conditions and weather for ski trips.

- **Arguments**: resort, dates
- **Workflow**: Resort lookup → Snow conditions → Weather → Assessment

### `plan-outdoor-activity`

Weather-aware outdoor activity planning workflow.

- **Arguments**: activity, location, timeframe
- **Workflow**: Activity sensitivity → Weather check → Suitability assessment

### `weather-aware-travel`

Integration pattern for combining weather with journey planning.

- **Arguments**: destination, travel_dates, trip_type
- **Workflow**: Destination weather → Packing advice → Activity suggestions

## Technology Stack

- **Java 21** (LTS)
- **Spring Boot 3.4.1**
- **Spring WebFlux** (Reactive)
- **SBB MCP Commons 1.8.0**
- **Maven**

## Prerequisites

- Java 21 or higher
- Maven 3.6+

## Building

```bash
mvn clean install
```

## Running Locally

```bash
mvn spring-boot:run
```

The server will start on `http://localhost:8080`.

## Docker

Build the container:

```bash
mvn compile jib:dockerBuild
```

Run the container:

```bash
docker run -p 8080:8080 gcr.io/PROJECT_ID/open-meteo-mcp
```

## MCP Integration

### Claude Desktop Configuration

Add to your Claude Desktop configuration file:

**macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "open-meteo": {
      "command": "java",
      "args": [
        "-jar",
        "/path/to/open-meteo-mcp-1.0.0.jar"
      ]
    }
  }
}
```

## API Documentation

The server exposes standard MCP endpoints:

- `POST /mcp` - Main MCP endpoint for tool execution
- `GET /health` - Health check endpoint

## Example Usage

Once connected via MCP, you can ask:

**Weather Queries**:

- "What's the weather in Bern, Switzerland?"
- "Show me the 7-day forecast for Zurich"

**Snow Conditions**:

- "What are the snow conditions in Zermatt?"
- "Will it snow in the Alps this week?"

**Ski Trip Planning** (uses prompts + resources):

- "Plan a ski trip to Verbier this weekend"
- "Compare snow conditions across St. Moritz, Davos, and Zermatt"

**Outdoor Activities** (uses prompts):

- "I want to hike the Eiger Trail next week, what's the weather?"
- "Best days for cycling around Lake Geneva this week?"

## Weather Codes

The API returns WMO weather codes. See [docs/WEATHER_CODES.md](docs/WEATHER_CODES.md) for the complete reference.

## License

MIT License

## Credits

Weather data provided by [Open-Meteo](https://open-meteo.com/) - Free Open-Source Weather API.

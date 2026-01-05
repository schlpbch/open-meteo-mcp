# Open Meteo MCP Server

A Model Context Protocol (MCP) server providing weather and snow condition tools via the [Open-Meteo API](https://open-meteo.com/).

## Features

- **Weather Forecasts**: Get current weather and multi-day forecasts for any location
- **Snow Conditions**: Get snow depth, snowfall, and mountain weather data
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

- "What's the weather in Bern, Switzerland?"
- "Show me the 7-day forecast for Zurich"
- "What are the snow conditions in Zermatt?"
- "Will it snow in the Alps this week?"

## Weather Codes

The API returns WMO weather codes. See [docs/WEATHER_CODES.md](docs/WEATHER_CODES.md) for the complete reference.

## License

MIT License

## Credits

Weather data provided by [Open-Meteo](https://open-meteo.com/) - Free Open-Source Weather API.

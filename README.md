# Open Meteo MCP Server

A Model Context Protocol (MCP) server providing weather and snow condition tools via the [Open-Meteo API](https://open-meteo.com/).

**Version 2.0** - Now powered by Python and FastMCP!

## Features

- **Weather Forecasts**: Get current weather and multi-day forecasts for any location
- **Snow Conditions**: Get snow depth, snowfall, and mountain weather data
- **MCP Resources**: Weather codes, ski resort coordinates, API parameters reference
- **MCP Prompts**: Guided workflows for ski trips, outdoor activities, and travel planning
- **Free API**: No API key required - powered by Open-Meteo's free weather API
- **MCP Integration**: Seamlessly integrates with MCP-compatible clients like Claude Desktop

## Tools

### `get_weather`

Get weather forecast for a location with temperature, precipitation, humidity, and more.

**Parameters:**

- `latitude` (required): Latitude in decimal degrees
- `longitude` (required): Longitude in decimal degrees
- `forecast_days` (optional): Number of forecast days (1-16, default: 7)
- `include_hourly` (optional): Include hourly forecasts (default: true)
- `timezone` (optional): Timezone for timestamps (default: "auto")

### `get_snow_conditions`

Get snow conditions and forecasts for mountain locations.

**Parameters:**

- `latitude` (required): Latitude in decimal degrees
- `longitude` (required): Longitude in decimal degrees
- `forecast_days` (optional): Number of forecast days (1-16, default: 7)
- `include_hourly` (optional): Include hourly data (default: true)
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

- **Python 3.11+**
- **FastMCP** - MCP server framework
- **httpx** - Async HTTP client
- **Pydantic** - Data validation
- **structlog** - Structured logging
- **uv** - Fast Python package manager

## Prerequisites

- Python 3.11 or higher
- uv package manager

## Installation

### Install uv (if not already installed)

**Windows (PowerShell):**

```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**macOS/Linux:**

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Install Dependencies

```bash
uv sync
```

This will install all required dependencies including FastMCP, httpx, pydantic, and testing tools.

## Running Locally

### Stdio Mode (for Claude Desktop)

```bash
uv run python -m open_meteo_mcp.server
```

### Testing with MCP Inspector

```bash
npx @modelcontextprotocol/inspector uv run python -m open_meteo_mcp.server
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
      "command": "uv",
      "args": [
        "--directory",
        "C:\\Users\\YourUsername\\path\\to\\open-meteo-mcp",
        "run",
        "python",
        "-m",
        "open_meteo_mcp.server"
      ]
    }
  }
}
```

**Note**: Update the `--directory` path to match your local installation.

## Development

### Running Tests

```bash
# Run all tests
uv run pytest tests/ -v

# Run with coverage
uv run pytest tests/ --cov=open_meteo_mcp --cov-report=html

# Run specific test file
uv run pytest tests/test_models.py -v
```

### Project Structure

```
open-meteo-mcp/
├── src/
│   └── open_meteo_mcp/
│       ├── __init__.py
│       ├── server.py          # FastMCP server with tools, resources, prompts
│       ├── client.py           # Open-Meteo API client
│       ├── models.py           # Pydantic models
│       ├── helpers.py          # Utility functions
│       └── data/               # JSON resource files
│           ├── weather-codes.json
│           ├── swiss-ski-resorts.json
│           └── weather-parameters.json
├── tests/
│   ├── test_models.py
│   ├── test_client.py
│   └── test_helpers.py
├── pyproject.toml              # Project configuration
└── .fastmcp/
    └── config.yaml             # FastMCP Cloud deployment config
```

## Deployment

### FastMCP Cloud

Deploy to FastMCP Cloud for remote access:

```bash
# Login to FastMCP Cloud
fastmcp login

# Deploy the server
fastmcp deploy

# Check deployment status
fastmcp status open-meteo-mcp
```

The server will be available at `https://open-meteo-mcp.fastmcp.cloud`

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

## Migration from Java

This is version 2.0 of the Open Meteo MCP server, migrated from Java/Spring Boot to Python/FastMCP for:

- Faster development and iteration
- Easier deployment with FastMCP Cloud
- Better integration with the MCP ecosystem
- Simpler codebase and dependencies

The Java version (v1.x) is archived in the `java-v1` branch.

## License

MIT License

## Credits

Weather data provided by [Open-Meteo](https://open-meteo.com/) - Free Open-Source Weather API.

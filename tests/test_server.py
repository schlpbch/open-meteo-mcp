"""Integration tests for FastMCP server tools, resources, and prompts."""

import pytest
import json
from fastmcp.client import Client

from open_meteo_mcp.server import mcp


@pytest.mark.asyncio
class TestServerTools:
    """Test FastMCP tool registration and invocation."""
    
    async def test_get_weather_tool_registered(self):
        """Test that get_weather tool is registered."""
        async with Client(mcp) as client:
            tools = await client.list_tools()
            tool_names = [tool.name for tool in tools]
            assert "meteo__get_weather" in tool_names

    async def test_get_snow_conditions_tool_registered(self):
        """Test that get_snow_conditions tool is registered."""
        async with Client(mcp) as client:
            tools = await client.list_tools()
            tool_names = [tool.name for tool in tools]
            assert "meteo__get_snow_conditions" in tool_names

    async def test_get_weather_alerts_tool_registered(self):
        """Test that get_weather_alerts tool is registered."""
        async with Client(mcp) as client:
            tools = await client.list_tools()
            tool_names = [tool.name for tool in tools]
            assert "meteo__get_weather_alerts" in tool_names

    async def test_get_historical_weather_tool_registered(self):
        """Test that get_historical_weather tool is registered."""
        async with Client(mcp) as client:
            tools = await client.list_tools()
            tool_names = [tool.name for tool in tools]
            assert "meteo__get_historical_weather" in tool_names

    async def test_get_marine_conditions_tool_registered(self):
        """Test that get_marine_conditions tool is registered."""
        async with Client(mcp) as client:
            tools = await client.list_tools()
            tool_names = [tool.name for tool in tools]
            assert "meteo__get_marine_conditions" in tool_names

    async def test_get_comfort_index_tool_registered(self):
        """Test that get_comfort_index tool is registered."""
        async with Client(mcp) as client:
            tools = await client.list_tools()
            tool_names = [tool.name for tool in tools]
            assert "meteo__get_comfort_index" in tool_names

    async def test_get_astronomy_tool_registered(self):
        """Test that get_astronomy tool is registered."""
        async with Client(mcp) as client:
            tools = await client.list_tools()
            tool_names = [tool.name for tool in tools]
            assert "meteo__get_astronomy" in tool_names

    async def test_search_location_swiss_tool_registered(self):
        """Test that search_location_swiss tool is registered."""
        async with Client(mcp) as client:
            tools = await client.list_tools()
            tool_names = [tool.name for tool in tools]
            assert "meteo__search_location_swiss" in tool_names

    async def test_compare_locations_tool_registered(self):
        """Test that compare_locations tool is registered."""
        async with Client(mcp) as client:
            tools = await client.list_tools()
            tool_names = [tool.name for tool in tools]
            assert "meteo__compare_locations" in tool_names

    async def test_tool_count(self):
        """Test that 11 tools are registered."""
        async with Client(mcp) as client:
            tools = await client.list_tools()
            assert len(tools) == 11


@pytest.mark.asyncio
class TestServerResources:
    """Test FastMCP resource registration and content."""
    
    async def test_weather_codes_resource_registered(self):
        """Test that weather codes resource is registered."""
        async with Client(mcp) as client:
            resources = await client.list_resources()
            resource_uris = [str(resource.uri) for resource in resources]
            assert "weather://codes" in resource_uris

    async def test_weather_parameters_resource_registered(self):
        """Test that weather parameters resource is registered."""
        async with Client(mcp) as client:
            resources = await client.list_resources()
            resource_uris = [str(resource.uri) for resource in resources]
            assert "weather://parameters" in resource_uris
    
    async def test_resource_count(self):
        """Test that 4 resources are registered."""
        async with Client(mcp) as client:
            resources = await client.list_resources()
            assert len(resources) == 4
    
    async def test_weather_codes_content(self):
        """Test that weather codes resource returns valid JSON."""
        async with Client(mcp) as client:
            content = await client.read_resource("weather://codes")
            # Should be valid JSON
            data = json.loads(content[0].text)
            assert isinstance(data, dict)
            # Should contain weather codes
            assert len(data) > 0
    

    
    async def test_weather_parameters_content(self):
        """Test that weather parameters resource returns valid JSON."""
        async with Client(mcp) as client:
            content = await client.read_resource("weather://parameters")
            # Should be valid JSON
            data = json.loads(content[0].text)
            assert isinstance(data, dict)
            # Should contain parameter categories
            assert len(data) > 0


@pytest.mark.asyncio
class TestServerPrompts:
    """Test FastMCP prompt registration and template generation."""
    
    async def test_ski_trip_weather_prompt_registered(self):
        """Test that ski trip weather prompt is registered."""
        async with Client(mcp) as client:
            prompts = await client.list_prompts()
            prompt_names = [prompt.name for prompt in prompts]
            assert "meteo__ski-trip-weather" in prompt_names

    async def test_plan_outdoor_activity_prompt_registered(self):
        """Test that outdoor activity prompt is registered."""
        async with Client(mcp) as client:
            prompts = await client.list_prompts()
            prompt_names = [prompt.name for prompt in prompts]
            assert "meteo__plan-outdoor-activity" in prompt_names

    async def test_weather_aware_travel_prompt_registered(self):
        """Test that weather aware travel prompt is registered."""
        async with Client(mcp) as client:
            prompts = await client.list_prompts()
            prompt_names = [prompt.name for prompt in prompts]
            assert "meteo__weather-aware-travel" in prompt_names
    
    async def test_prompt_count(self):
        """Test that 3 prompts are registered."""
        async with Client(mcp) as client:
            prompts = await client.list_prompts()
            assert len(prompts) == 3
    
    async def test_ski_trip_weather_prompt_content(self):
        """Test ski trip weather prompt generates valid template."""
        async with Client(mcp) as client:
            result = await client.get_prompt(
                "meteo__ski-trip-weather",
                arguments={"resort": "Zermatt", "dates": "this weekend"}
            )
            # Should return a message with content
            assert len(result.messages) > 0
            content = result.messages[0].content.text
            assert isinstance(content, str)
            assert len(content) > 0
            # Should mention the resort
            assert "Zermatt" in content
            # Should mention the dates
            assert "this weekend" in content
    
    async def test_plan_outdoor_activity_prompt_content(self):
        """Test outdoor activity prompt generates valid template."""
        async with Client(mcp) as client:
            result = await client.get_prompt(
                "meteo__plan-outdoor-activity",
                arguments={"activity": "hiking", "location": "Bern", "timeframe": "tomorrow"}
            )
            # Should return a message with content
            assert len(result.messages) > 0
            content = result.messages[0].content.text
            assert isinstance(content, str)
            assert len(content) > 0
            # Should mention the activity
            assert "hiking" in content
    
    async def test_weather_aware_travel_prompt_content(self):
        """Test weather aware travel prompt generates valid template."""
        async with Client(mcp) as client:
            result = await client.get_prompt(
                "meteo__weather-aware-travel",
                arguments={"destination": "Zürich", "travel_dates": "next week", "trip_type": "business"}
            )
            # Should return a message with content
            assert len(result.messages) > 0
            content = result.messages[0].content.text
            assert isinstance(content, str)
            assert len(content) > 0
            # Should mention the destination
            assert "Zürich" in content


@pytest.mark.asyncio
class TestServerToolExecution:
    """Test actual execution of server tools with mocked clients."""

    async def test_get_weather_execution(self, monkeypatch):
        """Test get_weather tool executes and returns data."""
        from unittest.mock import AsyncMock, MagicMock
        from open_meteo_mcp import server

        mock_result = MagicMock()
        mock_result.model_dump.return_value = {
            "current_weather": {"temperature": 15},
            "daily": [],
            "hourly": {},
        }
        monkeypatch.setattr(
            server.weather_service,
            "get_weather_enriched",
            AsyncMock(return_value=mock_result.model_dump.return_value),
        )

        result = await server.get_weather(
            latitude=46.95, longitude=7.45, forecast_days=7, include_hourly=True
        )
        assert isinstance(result, dict)
        assert "current_weather" in result

    async def test_get_snow_conditions_execution(self, monkeypatch):
        """Test get_snow_conditions tool executes and returns data."""
        from unittest.mock import AsyncMock, MagicMock
        from open_meteo_mcp import server

        mock_result = MagicMock()
        mock_result.model_dump.return_value = {"current": {"snow_depth": 100}, "daily": []}
        monkeypatch.setattr(
            server.weather_service,
            "get_snow_conditions_enriched",
            AsyncMock(return_value=mock_result.model_dump.return_value),
        )

        result = await server.get_snow_conditions(
            latitude=46.95, longitude=7.45, forecast_days=7, include_hourly=True
        )
        assert isinstance(result, dict)

    async def test_search_location_execution(self, monkeypatch):
        """Test search_location tool executes and returns locations."""
        from unittest.mock import AsyncMock
        from open_meteo_mcp import server

        mock_result = {"results": [{"name": "Bern", "latitude": 46.95}]}
        monkeypatch.setattr(
            server.location_service,
            "search_location_enriched",
            AsyncMock(return_value=mock_result),
        )

        result = await server.search_location(name="Bern")
        assert result == mock_result

    async def test_get_air_quality_execution(self, monkeypatch):
        """Test get_air_quality tool executes and returns data."""
        from unittest.mock import AsyncMock
        from open_meteo_mcp import server

        mock_result = {"current": {"european_aqi": 25}, "hourly": []}
        monkeypatch.setattr(
            server.air_quality_service,
            "get_air_quality_enriched",
            AsyncMock(return_value=mock_result),
        )

        result = await server.get_air_quality(latitude=46.95, longitude=7.45)
        assert result == mock_result

    async def test_get_weather_alerts_execution(self, monkeypatch):
        """Test get_weather_alerts tool executes and returns alerts."""
        from unittest.mock import AsyncMock, MagicMock
        from open_meteo_mcp import server

        # Mock the client weather call
        mock_weather = MagicMock()
        mock_weather.current_weather = MagicMock()
        mock_weather.current_weather.model_dump.return_value = {}
        mock_weather.hourly = MagicMock()
        mock_weather.hourly.model_dump.return_value = {}
        mock_weather.daily = MagicMock()
        mock_weather.daily.model_dump.return_value = {}
        mock_weather.timezone = "UTC"

        monkeypatch.setattr(
            server.client, "get_weather", AsyncMock(return_value=mock_weather)
        )

        result = await server.get_weather_alerts(latitude=46.95, longitude=7.45)
        assert "alerts" in result
        assert "latitude" in result
        assert "longitude" in result

    async def test_get_historical_weather_execution(self, monkeypatch):
        """Test get_historical_weather tool executes and returns data."""
        from unittest.mock import AsyncMock, MagicMock
        from open_meteo_mcp import server

        mock_result = MagicMock()
        mock_result.model_dump.return_value = {"daily": [], "timezone": "Europe/Zurich"}
        monkeypatch.setattr(
            server.client,
            "get_historical_weather",
            AsyncMock(return_value=mock_result),
        )

        result = await server.get_historical_weather(
            latitude=46.95,
            longitude=7.45,
            start_date="2024-01-01",
            end_date="2024-01-31",
        )
        assert isinstance(result, dict)

    async def test_get_marine_conditions_execution(self, monkeypatch):
        """Test get_marine_conditions tool executes and returns data."""
        from unittest.mock import AsyncMock, MagicMock
        from open_meteo_mcp import server

        mock_result = MagicMock()
        mock_result.model_dump.return_value = {"wave_height": {"daily": [1.5, 2.0]}}
        monkeypatch.setattr(
            server.client, "get_marine_conditions", AsyncMock(return_value=mock_result)
        )

        result = await server.get_marine_conditions(latitude=46.95, longitude=7.45)
        assert isinstance(result, dict)

    async def test_get_comfort_index_execution(self, monkeypatch):
        """Test get_comfort_index tool executes and returns index."""
        from unittest.mock import AsyncMock, MagicMock
        from open_meteo_mcp import server

        # Mock weather and air quality calls
        mock_weather = MagicMock()
        mock_weather.current_weather = MagicMock()
        mock_weather.current_weather.model_dump.return_value = {}
        mock_weather.timezone = "UTC"

        mock_aqi = MagicMock()
        mock_aqi.current = MagicMock()
        mock_aqi.current.model_dump.return_value = {}

        monkeypatch.setattr(
            server.client, "get_weather", AsyncMock(return_value=mock_weather)
        )
        monkeypatch.setattr(
            server.client, "get_air_quality", AsyncMock(return_value=mock_aqi)
        )

        result = await server.get_comfort_index(latitude=46.95, longitude=7.45)
        assert "comfort_index" in result
        assert "latitude" in result

    async def test_get_astronomy_execution(self, monkeypatch):
        """Test get_astronomy tool executes and returns data."""
        from unittest.mock import AsyncMock, MagicMock
        from open_meteo_mcp import server

        # Mock the weather call and astronomy calculation
        mock_weather = MagicMock()
        mock_weather.timezone = "Europe/Zurich"

        mock_astronomy = {
            "sunrise": "2024-01-01T07:30:00",
            "sunset": "2024-01-01T17:30:00",
            "day_length_hours": 10.0,
        }

        monkeypatch.setattr(
            server.client, "get_weather", AsyncMock(return_value=mock_weather)
        )
        monkeypatch.setattr(
            "open_meteo_mcp.helpers.calculate_astronomy_data",
            lambda lat, lon, tz: mock_astronomy,
        )

        result = await server.get_astronomy(latitude=46.95, longitude=7.45)
        assert "astronomy" in result
        assert "latitude" in result

    async def test_search_location_swiss_execution(self, monkeypatch):
        """Test search_location_swiss tool executes and returns locations."""
        from unittest.mock import AsyncMock
        from open_meteo_mcp import server

        mock_result = {
            "query": "Bern",
            "results": [{"name": "Bern", "latitude": 46.95}],
            "country": "CH",
        }
        monkeypatch.setattr(
            server.location_service,
            "search_location_swiss_enriched",
            AsyncMock(return_value=mock_result),
        )

        result = await server.search_location_swiss(name="Bern")
        assert result == mock_result

    async def test_compare_locations_execution(self, monkeypatch):
        """Test compare_locations tool executes and returns comparison."""
        from unittest.mock import AsyncMock, MagicMock
        from open_meteo_mcp import server

        # Mock weather and air quality calls for comparison
        mock_weather = MagicMock()
        mock_weather.current_weather = MagicMock()
        mock_weather.current_weather.model_dump.return_value = {}
        mock_weather.timezone = "UTC"

        mock_aqi = MagicMock()
        mock_aqi.current = MagicMock()
        mock_aqi.current.model_dump.return_value = {}

        monkeypatch.setattr(
            server.client, "get_weather", AsyncMock(return_value=mock_weather)
        )
        monkeypatch.setattr(
            server.client, "get_air_quality", AsyncMock(return_value=mock_aqi)
        )

        result = await server.compare_locations(
            locations=[
                {"name": "Bern", "latitude": 46.95, "longitude": 7.45},
                {"name": "Zurich", "latitude": 47.37, "longitude": 8.54},
            ]
        )
        assert isinstance(result, dict)

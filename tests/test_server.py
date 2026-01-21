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

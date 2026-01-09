"""Integration tests for FastMCP server tools, resources, and prompts."""

import pytest
import json
from pathlib import Path
from fastmcp import FastMCP
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
            assert "get_weather" in tool_names
    
    async def test_get_snow_conditions_tool_registered(self):
        """Test that get_snow_conditions tool is registered."""
        async with Client(mcp) as client:
            tools = await client.list_tools()
            tool_names = [tool.name for tool in tools]
            assert "get_snow_conditions" in tool_names
    
    async def test_tool_count(self):
        """Test that exactly 2 tools are registered."""
        async with Client(mcp) as client:
            tools = await client.list_tools()
            assert len(tools) == 2


@pytest.mark.asyncio
class TestServerResources:
    """Test FastMCP resource registration and content."""
    
    async def test_weather_codes_resource_registered(self):
        """Test that weather codes resource is registered."""
        async with Client(mcp) as client:
            resources = await client.list_resources()
            resource_uris = [resource.uri for resource in resources]
            assert "weather://codes" in resource_uris
    
    async def test_swiss_ski_resorts_resource_registered(self):
        """Test that Swiss ski resorts resource is registered."""
        async with Client(mcp) as client:
            resources = await client.list_resources()
            resource_uris = [resource.uri for resource in resources]
            assert "weather://swiss-ski-resorts" in resource_uris
    
    async def test_weather_parameters_resource_registered(self):
        """Test that weather parameters resource is registered."""
        async with Client(mcp) as client:
            resources = await client.list_resources()
            resource_uris = [resource.uri for resource in resources]
            assert "weather://parameters" in resource_uris
    
    async def test_resource_count(self):
        """Test that exactly 3 resources are registered."""
        async with Client(mcp) as client:
            resources = await client.list_resources()
            assert len(resources) == 3
    
    async def test_weather_codes_content(self):
        """Test that weather codes resource returns valid JSON."""
        async with Client(mcp) as client:
            content = await client.read_resource("weather://codes")
            # Should be valid JSON
            data = json.loads(content[0].text)
            assert isinstance(data, dict)
            # Should contain weather codes
            assert len(data) > 0
    
    async def test_swiss_ski_resorts_content(self):
        """Test that ski resorts resource returns valid JSON."""
        async with Client(mcp) as client:
            content = await client.read_resource("weather://swiss-ski-resorts")
            # Should be valid JSON
            data = json.loads(content[0].text)
            assert isinstance(data, list)
            # Should contain resort data
            assert len(data) > 0
            # Verify structure of first resort
            if len(data) > 0:
                resort = data[0]
                assert "name" in resort
                assert "latitude" in resort
                assert "longitude" in resort
    
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
            assert "ski_trip_weather" in prompt_names
    
    async def test_plan_outdoor_activity_prompt_registered(self):
        """Test that outdoor activity prompt is registered."""
        async with Client(mcp) as client:
            prompts = await client.list_prompts()
            prompt_names = [prompt.name for prompt in prompts]
            assert "plan_outdoor_activity" in prompt_names
    
    async def test_weather_aware_travel_prompt_registered(self):
        """Test that weather aware travel prompt is registered."""
        async with Client(mcp) as client:
            prompts = await client.list_prompts()
            prompt_names = [prompt.name for prompt in prompts]
            assert "weather_aware_travel" in prompt_names
    
    async def test_prompt_count(self):
        """Test that exactly 3 prompts are registered."""
        async with Client(mcp) as client:
            prompts = await client.list_prompts()
            assert len(prompts) == 3
    
    async def test_ski_trip_weather_prompt_content(self):
        """Test ski trip weather prompt generates valid template."""
        async with Client(mcp) as client:
            result = await client.get_prompt(
                "ski_trip_weather",
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
                "plan_outdoor_activity",
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
                "weather_aware_travel",
                arguments={"destination": "Zürich", "travel_dates": "next week", "trip_type": "business"}
            )
            # Should return a message with content
            assert len(result.messages) > 0
            content = result.messages[0].content.text
            assert isinstance(content, str)
            assert len(content) > 0
            # Should mention the destination
            assert "Zürich" in content

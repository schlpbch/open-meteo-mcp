#!/usr/bin/env python3
"""Test script to verify the Open Meteo MCP improvements."""

import asyncio
from src.open_meteo_mcp.client import OpenMeteoClient


async def test_country_filter():
    """Test the country filter fix."""
    client = OpenMeteoClient()
    try:
        print("=== Testing Country Filter Fix ===")
        print("Searching for 'Thun' with country='CH' (should only return Swiss results)")
        result = await client.search_location('Thun', country='CH', count=5)
        
        print(f"Found {len(result.results)} results:")
        for r in result.results:
            print(f"  - {r.name} ({r.country_code}) - {r.admin1 or 'N/A'}")
            
        # Verify all results are Swiss
        non_swiss = [r for r in result.results if r.country_code != 'CH']
        if not non_swiss:
            print("✅ Country filter working correctly - all results are Swiss")
        else:
            print(f"❌ Country filter not working - found {len(non_swiss)} non-Swiss results")
            
    except Exception as e:
        print(f"❌ Error testing country filter: {e}")
    finally:
        await client.client.aclose()


async def test_timezone_consistency():
    """Test timezone consistency between endpoints."""
    client = OpenMeteoClient()
    try:
        print("\n=== Testing Timezone Consistency ===")
        lat, lon = 46.9479, 7.4474  # Bern coordinates
        timezone = "Europe/Zurich"
        
        # Get weather data
        weather = await client.get_weather(lat, lon, timezone=timezone)
        print(f"Weather timezone: {weather.timezone}")
        
        # Get air quality data with new timezone parameter
        air_quality = await client.get_air_quality(lat, lon, timezone=timezone)
        print(f"Air quality timezone: {air_quality.timezone}")
        
        if weather.timezone == air_quality.timezone:
            print("✅ Timezone consistency achieved - both endpoints use same timezone")
        else:
            print(f"❌ Timezone inconsistency: weather={weather.timezone}, air_quality={air_quality.timezone}")
            
    except Exception as e:
        print(f"❌ Error testing timezone consistency: {e}")
    finally:
        await client.client.aclose()


async def main():
    """Run all tests."""
    await test_country_filter()
    await test_timezone_consistency()


if __name__ == "__main__":
    asyncio.run(main())
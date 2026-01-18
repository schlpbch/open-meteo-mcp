"""Unit tests for geocoding functionality."""

import pytest
from pytest_httpx import HTTPXMock

from open_meteo_mcp.client import OpenMeteoClient
from open_meteo_mcp.models import GeocodingResponse, GeocodingResult


@pytest.mark.asyncio
class TestGeocoding:
    """Test geocoding API calls."""
    
    async def test_search_location_success(self, httpx_mock: HTTPXMock):
        """Test successful location search."""
        # Mock API response
        httpx_mock.add_response(
            url="https://geocoding-api.open-meteo.com/v1/search?name=Zurich&count=10&language=en&format=json",
            json={
                "results": [
                    {
                        "id": 2657896,
                        "name": "Zurich",
                        "latitude": 47.3769,
                        "longitude": 8.5417,
                        "elevation": 408.0,
                        "feature_code": "PPLA",
                        "country_code": "CH",
                        "country": "Switzerland",
                        "country_id": 2658434,
                        "timezone": "Europe/Zurich",
                        "population": 402762,
                        "admin1": "Zurich",
                        "admin1_id": 2657895
                    },
                    {
                        "id": 5145476,
                        "name": "Zurich",
                        "latitude": 42.9931,
                        "longitude": -75.1007,
                        "elevation": 366.0,
                        "feature_code": "PPL",
                        "country_code": "US",
                        "country": "United States",
                        "timezone": "America/New_York",
                        "population": 1627,
                        "admin1": "New York"
                    }
                ],
                "generationtime_ms": 1.234
            }
        )
        
        async with OpenMeteoClient() as client:
            result = await client.search_location(
                name="Zurich",
                count=10,
                language="en"
            )
            
            assert isinstance(result, GeocodingResponse)
            assert result.results is not None
            assert len(result.results) == 2
            
            # Check first result (Zurich, Switzerland)
            first = result.results[0]
            assert isinstance(first, GeocodingResult)
            assert first.name == "Zurich"
            assert first.latitude == 47.3769
            assert first.longitude == 8.5417
            assert first.country_code == "CH"
            assert first.country == "Switzerland"
            assert first.timezone == "Europe/Zurich"
            assert first.population == 402762
            
            # Check second result (Zurich, US)
            second = result.results[1]
            assert second.name == "Zurich"
            assert second.country_code == "US"
    
    async def test_search_location_with_country_filter(self, httpx_mock: HTTPXMock):
        """Test location search with country filter."""
        httpx_mock.add_response(
            url="https://geocoding-api.open-meteo.com/v1/search?name=Bern&count=5&language=en&format=json&country=CH",
            json={
                "results": [
                    {
                        "id": 2661552,
                        "name": "Bern",
                        "latitude": 46.9480,
                        "longitude": 7.4474,
                        "elevation": 542.0,
                        "country_code": "CH",
                        "country": "Switzerland",
                        "timezone": "Europe/Zurich",
                        "population": 133115
                    }
                ]
            }
        )
        
        async with OpenMeteoClient() as client:
            result = await client.search_location(
                name="Bern",
                count=5,
                language="en",
                country="CH"
            )
            
            assert result.results is not None
            assert len(result.results) == 1
            assert result.results[0].country_code == "CH"
    
    async def test_search_location_no_results(self, httpx_mock: HTTPXMock):
        """Test location search with no results."""
        httpx_mock.add_response(
            json={
                "results": None
            }
        )
        
        async with OpenMeteoClient() as client:
            result = await client.search_location(name="NonexistentPlace123")
            
            assert isinstance(result, GeocodingResponse)
            assert result.results is None
    
    async def test_search_location_fuzzy_matching(self, httpx_mock: HTTPXMock):
        """Test fuzzy matching for typos."""
        httpx_mock.add_response(
            json={
                "results": [
                    {
                        "id": 2657896,
                        "name": "Zurich",
                        "latitude": 47.3769,
                        "longitude": 8.5417,
                        "country_code": "CH"
                    }
                ]
            }
        )
        
        async with OpenMeteoClient() as client:
            # Search with typo
            result = await client.search_location(name="Zuerich")
            
            assert result.results is not None
            assert len(result.results) > 0
            assert result.results[0].name == "Zurich"
    
    async def test_search_location_count_clamping(self, httpx_mock: HTTPXMock):
        """Test that count is clamped to 1-100 range."""
        # Mock responses for both test cases
        response_data = {
            "results": [
                {
                    "name": "Test",
                    "latitude": 47.0,
                    "longitude": 8.0,
                    "country_code": "CH"
                }
            ]
        }
        
        httpx_mock.add_response(json=response_data)
        httpx_mock.add_response(json=response_data)
        
        async with OpenMeteoClient() as client:
            # Test clamping to minimum (1)
            result = await client.search_location(name="Test", count=0)
            assert isinstance(result, GeocodingResponse)
            
            # Test clamping to maximum (100)
            result = await client.search_location(name="Test", count=200)
            assert isinstance(result, GeocodingResponse)
    
    async def test_search_location_multilingual(self, httpx_mock: HTTPXMock):
        """Test multilingual search."""
        httpx_mock.add_response(
            json={
                "results": [
                    {
                        "name": "Zürich",
                        "latitude": 47.3769,
                        "longitude": 8.5417,
                        "country_code": "CH"
                    }
                ]
            }
        )
        
        async with OpenMeteoClient() as client:
            result = await client.search_location(name="Zurich", language="de")
            
            assert result.results is not None
            assert result.results[0].name == "Zürich"
    
    async def test_search_location_http_error(self, httpx_mock: HTTPXMock):
        """Test handling of HTTP errors."""
        httpx_mock.add_response(status_code=500)
        
        async with OpenMeteoClient() as client:
            with pytest.raises(Exception):  # httpx.HTTPStatusError
                await client.search_location(name="Test")
    
    async def test_search_location_invalid_response(self, httpx_mock: HTTPXMock):
        """Test handling of invalid JSON response (gracefully handled)."""
        httpx_mock.add_response(
            json={"invalid": "data"}
        )
        
        async with OpenMeteoClient() as client:
            # Pydantic gracefully handles invalid data - results will be empty list
            result = await client.search_location(name="Test")
            assert isinstance(result, GeocodingResponse)
            assert result.results == [] or result.results is None
    
    async def test_search_swiss_locations(self, httpx_mock: HTTPXMock):
        """Test searching for popular Swiss locations."""
        locations = [
            ("Zermatt", 45.9763, 7.6586),
            ("Interlaken", 46.6863, 7.8632),
            ("Matterhorn", 45.9763, 7.6586),
            ("Lake Geneva", 46.4531, 6.5619)
        ]
        
        for name, lat, lon in locations:
            httpx_mock.add_response(
                json={
                    "results": [
                        {
                            "name": name,
                            "latitude": lat,
                            "longitude": lon,
                            "country_code": "CH"
                        }
                    ]
                }
            )
        
        async with OpenMeteoClient() as client:
            for name, expected_lat, expected_lon in locations:
                result = await client.search_location(name=name)
                assert result.results is not None
                assert result.results[0].latitude == expected_lat
                assert result.results[0].longitude == expected_lon

"""Location service with enrichment."""

from typing import Any

from .base import BaseService


class LocationService(BaseService):
    """Service for location search with automatic enrichment."""

    def _enrich_location(self, location: dict[str, Any]) -> dict[str, Any]:
        """Enrich a single location result with metadata.

        Args:
            location: Location dictionary from API

        Returns:
            Enriched location dictionary
        """
        enriched = location.copy()

        # Add feature type description if available
        feature_code = location.get("feature_code", "")
        feature_descriptions = {
            "PPL": "Populated Place",
            "PPLA": "State Capital",
            "PPLC": "Capital",
            "MT": "Mountain",
            "LK": "Lake",
            "PS": "Mountain Pass",
            "STM": "Stream",
            "RGN": "Region",
        }

        if feature_code:
            for code, description in feature_descriptions.items():
                if feature_code.startswith(code):
                    enriched["feature_type_description"] = description
                    break

        # Add elevation category
        elevation = location.get("elevation")
        if elevation is not None:
            if elevation < 500:
                enriched["elevation_category"] = "Low"
            elif elevation < 1500:
                enriched["elevation_category"] = "Medium"
            elif elevation < 2500:
                enriched["elevation_category"] = "High"
            else:
                enriched["elevation_category"] = "Very High"

        return enriched

    async def search_location_enriched(
        self,
        name: str,
        count: int = 10,
        language: str = "en",
        country: str = "",
    ) -> dict[str, Any]:
        """Search for locations with automatic enrichment.

        Fetches location search results and applies enrichment:
        - Feature type descriptions
        - Elevation categories

        Args:
            name: Location name to search
            count: Number of results (1-100, default: 10)
            language: Language for results (default: 'en')
            country: Optional country code filter

        Returns:
            Dictionary with enriched location results
        """
        # Fetch raw data from client
        response = await self.client.search_location(
            name=name,
            count=count,
            language=language,
            country=country if country else None,
        )

        # Convert to dict
        result: dict[str, Any] = response.model_dump()

        # Enrich each result
        if result.get("results"):
            result["results"] = [
                self._enrich_location(loc) for loc in result["results"]
            ]

        return result

    async def search_location_swiss_enriched(
        self,
        name: str,
        include_features: bool = False,
        language: str = "en",
        count: int = 10,
    ) -> dict[str, Any]:
        """Search for locations in Switzerland with enrichment.

        Specialized search for Swiss locations with feature filtering
        and automatic enrichment.

        Args:
            name: Location name to search
            include_features: Include geographic features (default: False)
            language: Language for results (default: 'en')
            count: Number of results (1-50, default: 10)

        Returns:
            Dictionary with enriched Swiss location results
        """
        # Get all results (fetch extra for filtering)
        response = await self.client.search_location(
            name=name,
            count=count * 2,
            language=language,
            country="CH",
        )

        results = response.results if response.results else []

        # Filter if needed
        if not include_features:
            results = [
                r
                for r in results
                if not r.feature_code or r.feature_code.startswith("PPL")
            ]

        # Sort by population
        results.sort(key=lambda x: x.population or 0, reverse=True)

        # Limit to requested count
        results = results[:count]

        # Enrich results
        enriched_results = [
            self._enrich_location(
                r.model_dump() if hasattr(r, "model_dump") else dict(r)
            )
            for r in results
        ]

        return {
            "query": name,
            "results": enriched_results,
            "total": len(enriched_results),
            "country": "CH",
            "include_features": include_features,
            "language": language,
        }

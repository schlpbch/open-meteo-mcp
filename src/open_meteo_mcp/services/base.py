"""Base service class with common enrichment patterns."""

from abc import ABC, abstractmethod
from typing import Any, Callable, TypeVar

from ..client import OpenMeteoClient

T = TypeVar("T")


class BaseService(ABC):
    """Abstract base service providing common initialization and enrichment patterns.

    Provides:
    - Standardized client initialization
    - Template method pattern for enrichment workflows
    - Safe navigation and conditional enrichment utilities
    """

    def __init__(self, client: OpenMeteoClient) -> None:
        """Initialize base service with client.

        Args:
            client: OpenMeteoClient instance
        """
        self.client = client

    @staticmethod
    def _enrich_if_exists(
        data: dict[str, Any],
        key: str,
        enricher: Callable[[Any], Any],
        output_key: str | None = None,
    ) -> None:
        """Enrich a dictionary value if key exists.

        Applies an enrichment function to a value if the key exists in the
        dictionary, storing the result with the output key (or original key
        with suffix if not specified).

        Args:
            data: Dictionary to enrich
            key: Key to check and enrich from
            enricher: Function to apply to the value
            output_key: Key to store enriched value (default: key + "_enriched")
        """
        if key in data and data[key] is not None:
            output = output_key or f"{key}_enriched"
            data[output] = enricher(data[key])

    @staticmethod
    def _enrich_list_if_exists(
        data: dict[str, Any],
        key: str,
        enricher: Callable[[Any], Any],
        output_key: str | None = None,
    ) -> None:
        """Enrich a list of values if key exists.

        Applies an enrichment function to each element if the key exists and
        contains a list, storing results with the output key.

        Args:
            data: Dictionary to enrich
            key: Key containing list to enrich
            enricher: Function to apply to each element
            output_key: Key to store enriched list (default: key + "_enriched")
        """
        if key in data and data[key]:
            output = output_key or f"{key}_enriched"
            data[output] = [enricher(item) for item in data[key]]

    @staticmethod
    def _enrich_section(
        data: dict[str, Any],
        section_key: str,
        enricher: Callable[[dict[str, Any]], None],
    ) -> None:
        """Apply enrichment function to a nested section.

        Safely applies an enrichment function to a nested dictionary section
        if it exists.

        Args:
            data: Dictionary containing the section
            section_key: Key of the section to enrich
            enricher: Function to apply to the section (modifies in-place)
        """
        if section_key in data and data[section_key]:
            enricher(data[section_key])

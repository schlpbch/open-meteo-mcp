"""Chat handler for Anthropic Claude integration."""

from typing import Any

from anthropic import Anthropic

from ..services import AirQualityService, LocationService, WeatherService
from ..client import OpenMeteoClient
from .sessions import ConversationSession, SessionManager
from .tools import get_all_tool_schemas


class ChatHandler:
    """Handles conversations with Anthropic Claude with tool calling."""

    def __init__(self) -> None:
        """Initialize the chat handler."""
        self.client = Anthropic()
        self.session_manager = SessionManager()
        self.model = "claude-3-5-sonnet-20241022"

        # Initialize services for tool execution
        api_client = OpenMeteoClient()
        self.weather_service = WeatherService(api_client)
        self.air_quality_service = AirQualityService(api_client)
        self.location_service = LocationService(api_client)

    async def process_message(
        self, session_id: str, user_message: str
    ) -> dict[str, Any]:
        """Process a user message and return assistant response.

        Handles multi-turn conversations with automatic tool calling.

        Args:
            session_id: Session identifier
            user_message: User's message text

        Returns:
            Dictionary with assistant response and tool results
        """
        # Get or create session
        if not self.session_manager.session_exists(session_id):
            self.session_manager.create_session(session_id)

        session = self.session_manager.get_session(session_id)
        assert session is not None

        # Add user message to conversation
        session.add_message("user", user_message)

        # Main conversation loop
        response_text = ""
        tool_results: list[dict[str, Any]] = []

        while True:
            # Call Claude with tools
            messages = session.get_messages()
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                tools=get_all_tool_schemas(),  # type: ignore[arg-type]
                messages=messages,  # type: ignore[arg-type]
            )

            # Check if we should stop
            if response.stop_reason == "end_turn":
                # Extract text response
                for block in response.content:
                    if hasattr(block, "text"):
                        response_text = block.text
                        session.add_message("assistant", response_text)
                break

            # Handle tool use
            if response.stop_reason == "tool_use":
                tool_uses = [block for block in response.content if block.type == "tool_use"]

                # Add assistant response to session (includes tool use blocks)
                assistant_message = {
                    "role": "assistant",
                    "content": response.content,
                }
                session.messages.append(assistant_message)

                # Execute tools and collect results
                for tool_use in tool_uses:
                    tool_name = tool_use.name
                    tool_input = tool_use.input
                    tool_use_id = tool_use.id

                    try:
                        result = await self._execute_tool(tool_name, tool_input)
                        tool_results.append(
                            {
                                "tool": tool_name,
                                "input": tool_input,
                                "result": result,
                            }
                        )
                        session.add_tool_result(tool_use_id, tool_name, result)
                    except Exception as e:
                        error_result = {
                            "tool": tool_name,
                            "input": tool_input,
                            "error": str(e),
                        }
                        tool_results.append(error_result)
                        session.add_tool_result(tool_use_id, tool_name, f"Error: {str(e)}")
            else:
                # Unexpected stop reason
                break

        return {
            "session_id": session_id,
            "response": response_text,
            "tool_results": tool_results,
            "message_count": len(session.get_messages()),
        }

    async def _execute_tool(self, tool_name: str, tool_input: dict[str, Any]) -> Any:
        """Execute a tool and return the result.

        Args:
            tool_name: Name of the tool to execute
            tool_input: Input parameters for the tool

        Returns:
            Tool result

        Raises:
            ValueError: If tool is not recognized
        """
        if tool_name == "meteo__get_weather":
            return await self.weather_service.get_weather_enriched(
                latitude=tool_input["latitude"],
                longitude=tool_input["longitude"],
                forecast_days=tool_input.get("forecast_days", 7),
                include_hourly=tool_input.get("include_hourly", True),
                timezone=tool_input.get("timezone", "auto"),
            )

        elif tool_name == "meteo__get_snow_conditions":
            return await self.weather_service.get_snow_conditions_enriched(
                latitude=tool_input["latitude"],
                longitude=tool_input["longitude"],
                forecast_days=tool_input.get("forecast_days", 7),
                include_hourly=tool_input.get("include_hourly", True),
                timezone=tool_input.get("timezone", "Europe/Zurich"),
            )

        elif tool_name == "meteo__get_air_quality":
            return await self.air_quality_service.get_air_quality_enriched(
                latitude=tool_input["latitude"],
                longitude=tool_input["longitude"],
                forecast_days=tool_input.get("forecast_days", 5),
                include_pollen=tool_input.get("include_pollen", True),
                timezone=tool_input.get("timezone", "auto"),
            )

        elif tool_name == "meteo__search_location":
            return await self.location_service.search_location_enriched(
                name=tool_input["name"],
                count=tool_input.get("count", 10),
                language=tool_input.get("language", "en"),
                country=tool_input.get("country", ""),
            )

        else:
            raise ValueError(f"Unknown tool: {tool_name}")

    def get_session_info(self, session_id: str) -> dict[str, Any] | None:
        """Get information about a session.

        Args:
            session_id: Session identifier

        Returns:
            Session info or None if not found
        """
        return self.session_manager.get_session_info(session_id)

    def delete_session(self, session_id: str) -> bool:
        """Delete a session.

        Args:
            session_id: Session identifier

        Returns:
            True if deleted, False if not found
        """
        return self.session_manager.delete_session(session_id)

    def create_session(self, session_id: str | None = None) -> str:
        """Create a new session.

        Args:
            session_id: Optional custom session ID

        Returns:
            The created session ID
        """
        return self.session_manager.create_session(session_id)

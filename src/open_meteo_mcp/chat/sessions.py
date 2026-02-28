"""In-memory session storage for chat conversations."""

import uuid
from datetime import datetime
from typing import Any


class ConversationSession:
    """Represents a single conversation session."""

    def __init__(self, session_id: str) -> None:
        """Initialize a conversation session.

        Args:
            session_id: Unique session identifier
        """
        self.session_id = session_id
        self.messages: list[dict[str, Any]] = []
        self.created_at = datetime.now().isoformat()
        self.last_updated = datetime.now().isoformat()

    def add_message(self, role: str, content: str) -> None:
        """Add a message to the conversation.

        Args:
            role: Message role ('user', 'assistant', 'tool')
            content: Message content
        """
        self.messages.append({"role": role, "content": content})
        self.last_updated = datetime.now().isoformat()

    def add_tool_result(self, tool_use_id: str, tool_name: str, result: Any) -> None:
        """Add a tool result to the conversation.

        Args:
            tool_use_id: ID of the tool use block
            tool_name: Name of the tool that was called
            result: Result from the tool execution
        """
        self.messages.append(
            {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_use_id,
                        "content": str(result),
                    }
                ],
            }
        )
        self.last_updated = datetime.now().isoformat()

    def get_messages(self) -> list[dict[str, Any]]:
        """Get all messages in the conversation.

        Returns:
            List of messages in conversation format
        """
        return self.messages

    def to_dict(self) -> dict[str, Any]:
        """Convert session to dictionary.

        Returns:
            Dictionary representation of session
        """
        return {
            "session_id": self.session_id,
            "messages": self.messages,
            "created_at": self.created_at,
            "last_updated": self.last_updated,
            "message_count": len(self.messages),
        }


class SessionManager:
    """Manages in-memory conversation sessions."""

    def __init__(self) -> None:
        """Initialize the session manager."""
        self.sessions: dict[str, ConversationSession] = {}

    def create_session(self, session_id: str | None = None) -> str:
        """Create a new conversation session.

        Args:
            session_id: Optional custom session ID (generated if not provided)

        Returns:
            The session ID
        """
        if session_id is None:
            session_id = str(uuid.uuid4())

        self.sessions[session_id] = ConversationSession(session_id)
        return session_id

    def get_session(self, session_id: str) -> ConversationSession | None:
        """Get a conversation session.

        Args:
            session_id: Session identifier

        Returns:
            The session or None if not found
        """
        return self.sessions.get(session_id)

    def session_exists(self, session_id: str) -> bool:
        """Check if a session exists.

        Args:
            session_id: Session identifier

        Returns:
            True if session exists, False otherwise
        """
        return session_id in self.sessions

    def delete_session(self, session_id: str) -> bool:
        """Delete a conversation session.

        Args:
            session_id: Session identifier

        Returns:
            True if deleted, False if session didn't exist
        """
        if session_id in self.sessions:
            del self.sessions[session_id]
            return True
        return False

    def list_sessions(self) -> list[str]:
        """List all active session IDs.

        Returns:
            List of session IDs
        """
        return list(self.sessions.keys())

    def get_session_info(self, session_id: str) -> dict[str, Any] | None:
        """Get information about a session.

        Args:
            session_id: Session identifier

        Returns:
            Session info dictionary or None if not found
        """
        session = self.sessions.get(session_id)
        return session.to_dict() if session else None

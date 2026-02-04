"""Chat API routes for conversational weather interface."""

from typing import Any, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from ...chat import ChatHandler

# Initialize router and handler
router = APIRouter()
chat_handler = ChatHandler()


# Request/Response models
class MessageRequest(BaseModel):
    """Request model for chat message."""

    message: str = Field(..., description="User message")


class MessageResponse(BaseModel):
    """Response model for chat message."""

    session_id: str = Field(..., description="Session identifier")
    response: str = Field(..., description="Assistant response")
    tool_results: list[dict[str, Any]] = Field(
        default_factory=list, description="Results from tool calls"
    )
    message_count: int = Field(..., description="Total messages in session")


class SessionInfo(BaseModel):
    """Session information response."""

    session_id: str
    message_count: int
    created_at: str
    last_updated: str


# Endpoint: POST /api/chat/sessions/{sessionId}/messages
@router.post("/sessions/{session_id}/messages", response_model=MessageResponse)
async def send_message(
    session_id: str,
    request: MessageRequest,
) -> MessageResponse:
    """Send a message to the chat handler.

    Processes the user message, calls Claude with available tools,
    and returns the response with any tool results.
    """
    try:
        result = await chat_handler.process_message(session_id, request.message)
        return MessageResponse(
            session_id=result["session_id"],
            response=result["response"],
            tool_results=result["tool_results"],
            message_count=result["message_count"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat error: {str(e)}")


# Endpoint: GET /api/chat/sessions/{sessionId}/messages
@router.get("/sessions/{session_id}/messages", response_model=dict[str, Any])
async def get_session_messages(session_id: str) -> dict[str, Any]:
    """Get all messages in a session.

    Returns the conversation history for a given session.
    """
    try:
        info = chat_handler.get_session_info(session_id)
        if info is None:
            raise HTTPException(status_code=404, detail="Session not found")
        return info
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving session: {str(e)}")


# Endpoint: DELETE /api/chat/sessions/{sessionId}
@router.delete("/sessions/{session_id}")
async def delete_session(session_id: str) -> dict[str, Any]:
    """Delete a conversation session.

    Removes all conversation history for the session.
    """
    try:
        deleted = chat_handler.delete_session(session_id)
        if not deleted:
            raise HTTPException(status_code=404, detail="Session not found")
        return {"message": f"Session {session_id} deleted", "session_id": session_id}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting session: {str(e)}")


# Endpoint: GET /api/chat/health
@router.get("/health")
async def chat_health() -> dict[str, Any]:
    """Health check for chat service.

    Returns status and capabilities of the chat service.
    """
    return {
        "status": "healthy",
        "service": "chat",
        "capabilities": [
            "meteo__get_weather",
            "meteo__get_snow_conditions",
            "meteo__get_air_quality",
            "meteo__search_location",
        ],
        "model": "claude-3-5-sonnet-20241022",
    }

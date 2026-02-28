"""Decorators for tool error handling and logging."""

from collections.abc import Callable, Coroutine
from functools import wraps
from typing import Any, TypeVar

import structlog

logger = structlog.get_logger(__name__)

T = TypeVar("T")


def tool_error_handler(
    tool_name: str, error_class: type[Exception] | None = None
) -> Callable[
    [Callable[..., Coroutine[Any, Any, dict[str, Any]]]],
    Callable[..., Coroutine[Any, Any, dict[str, Any]]],
]:
    """Decorator for consistent MCP tool error handling.

    Args:
        tool_name: Name of the tool for logging
        error_class: Optional specific exception class to catch (defaults to all)

    Returns:
        Decorated async function with unified error handling
    """

    def decorator(
        func: Callable[..., Coroutine[Any, Any, dict[str, Any]]],
    ) -> Callable[..., Coroutine[Any, Any, dict[str, Any]]]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> dict[str, Any]:
            try:
                return await func(*args, **kwargs)
            except (ValueError, KeyError) as e:
                logger.error(f"{tool_name}.validation_error", error=str(e))
                return {"error": str(e)}
            except Exception as e:
                logger.error(f"{tool_name}.unexpected_error", error=str(e))
                return {"error": f"{tool_name} failed: {str(e)}"}

        return wrapper

    return decorator

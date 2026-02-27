# src/servicenow_mcp_server/tool_utils.py

"""Decorator that converts ServiceNowError into ToolError."""

import functools
from typing import Any, Callable

from fastmcp.exceptions import ToolError

from servicenow_mcp_server.exceptions import ServiceNowError


def snow_tool(fn: Callable[..., Any]) -> Callable[..., Any]:
    """Wrap an async tool function so ServiceNowError becomes ToolError."""

    @functools.wraps(fn)
    async def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return await fn(*args, **kwargs)
        except ServiceNowError as e:
            detail = e.message
            if e.details:
                detail += f" — {e.details}"
            raise ToolError(detail) from e

    return wrapper

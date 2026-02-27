# src/servicenow_mcp_server/models.py

"""Shared Pydantic models and helpers used across all tool modules."""

import contextvars

from pydantic import BaseModel, Field

from servicenow_mcp_server.config_loader import load_config
from servicenow_mcp_server.exceptions import ServiceNowConnectionError
from servicenow_mcp_server.utils import ServiceNowClient


class BaseToolParams(BaseModel):
    """Base model for tool parameters. Credentials are handled at the server level."""
    pass


# ---------------------------------------------------------------------------
# Shared HTTP client (set once during lifespan, reused by every tool call)
# ---------------------------------------------------------------------------

_shared_client: contextvars.ContextVar[ServiceNowClient | None] = contextvars.ContextVar(
    "_shared_client", default=None
)


def set_shared_client(client: ServiceNowClient | None) -> None:
    """Store (or clear) the lifespan-managed ServiceNowClient."""
    _shared_client.set(client)


class _NoOpContextManager:
    """Wrap an already-open client so ``async with get_client() as c:`` still works."""

    def __init__(self, client: ServiceNowClient):
        self._client = client

    async def __aenter__(self):
        return self._client

    async def __aexit__(self, *args):
        pass  # Don't close the shared client


def get_client() -> ServiceNowClient | _NoOpContextManager:
    """Return the shared ServiceNowClient (preferred) or create a fresh one.

    The MCP server reads SERVICENOW_INSTANCE, SERVICENOW_USERNAME, and
    SERVICENOW_PASSWORD from the environment (set via the MCP config's ``env`` block).
    Individual tool calls no longer need to supply credentials.
    """
    shared = _shared_client.get()
    if shared is not None:
        return _NoOpContextManager(shared)

    # Fallback: create a new client (backwards-compatible for tests / scripts)
    config = load_config()
    if config is None:
        raise ServiceNowConnectionError(
            "ServiceNow credentials not configured. "
            "Set SERVICENOW_INSTANCE, SERVICENOW_USERNAME, and "
            "SERVICENOW_PASSWORD environment variables in your MCP server config."
        )
    return ServiceNowClient(
        instance_url=config["instance"],
        username=config["username"],
        password=config["password"],
    )

# src/servicenow_mcp_server/models.py

"""Shared Pydantic models used across all tool modules."""

from pydantic import BaseModel, Field


class BaseToolParams(BaseModel):
    """Base model containing the required ServiceNow credentials for any tool call."""

    instance_url: str = Field(
        ...,
        description="The full URL of the ServiceNow instance (e.g., https://my-instance.service-now.com).",
    )
    username: str = Field(..., description="The username for authentication.")
    password: str = Field(
        ...,
        description="The password for authentication.",
        json_schema_extra={"sensitive": True},
    )

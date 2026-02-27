# src/servicenow_mcp_server/agile_management/epic_tools.py
"""
This module defines tools for interacting with Epics in ServiceNow's
Agile Development 2.0 application.
"""

from typing import Dict, Any, Optional
from pydantic import Field
from fastmcp import FastMCP
from servicenow_mcp_server.models import BaseToolParams, get_client
from servicenow_mcp_server.tool_annotations import READ, WRITE
from servicenow_mcp_server.tool_utils import snow_tool

def register_tools(mcp: FastMCP):
    """Adds all tools defined in this file to the main server's MCP instance."""
    _tags = {"agile"}

    mcp.tool(create_epic, tags=_tags | {"write"}, annotations=WRITE)
    mcp.tool(update_epic, tags=_tags | {"write"}, annotations=WRITE)
    mcp.tool(list_epics, tags=_tags | {"read"}, annotations=READ)

# ==============================================================================
#  Pydantic Models
# ==============================================================================

class CreateEpicParams(BaseToolParams):
    short_description: str = Field(..., description="A brief, one-line summary of the epic.")
    description: Optional[str] = Field(None, description="A detailed description of the epic.")
    parent: Optional[str] = Field(None, description="The sys_id of a parent epic, if this is a sub-epic.")
    theme: Optional[str] = Field(None, description="The sys_id of the theme this epic belongs to.")

class UpdateEpicParams(BaseToolParams):
    epic_id: str = Field(..., description="The sys_id of the epic to update.")
    short_description: Optional[str] = Field(None, description="A brief, one-line summary of the epic.")
    description: Optional[str] = Field(None, description="A detailed description of the epic.")
    parent: Optional[str] = Field(None, description="The sys_id of a parent epic, if this is a sub-epic.")
    theme: Optional[str] = Field(None, description="The sys_id of the theme this epic belongs to.")

class ListEpicsParams(BaseToolParams):
    limit: int = Field(10, description="Maximum number of epics to return.")
    offset: int = Field(0, description="Number of records to skip for pagination.")
    short_description: Optional[str] = Field(None, description="Filter by short description (LIKE search).")
    assigned_to: Optional[str] = Field(None, description="Filter by the sys_id of the assigned user.")
    state: Optional[str] = Field(None, description="Filter by state (e.g., 'New', 'In Progress', 'Done').")
    theme: Optional[str] = Field(None, description="Filter by the sys_id of the theme.")

# ==============================================================================
#  Tool Functions
# ==============================================================================

@snow_tool
async def create_epic(params: CreateEpicParams) -> Dict[str, Any]:
    """
    Creates a new epic in the Agile Development 2.0 module.
    """
    async with get_client() as client:
        payload = params.model_dump(
            exclude=set(),
            exclude_unset=True
        )

        return await client.send_request("POST", "/api/now/table/rm_epic", data=payload)

@snow_tool
async def update_epic(params: UpdateEpicParams) -> Dict[str, Any]:
    """
    Updates an existing epic in the Agile Development 2.0 module.
    """
    async with get_client() as client:
        payload = params.model_dump(
            exclude={"epic_id"},
            exclude_unset=True
        )

        return await client.send_request("PATCH", f"/api/now/table/rm_epic/{params.epic_id}", data=payload)

@snow_tool
async def list_epics(params: ListEpicsParams) -> Dict[str, Any]:
    """
    Lists epics from ServiceNow with filtering options.
    """
    async with get_client() as client:
        query_parts = []

        if params.short_description:
            query_parts.append(f"short_descriptionLIKE{params.short_description}")
        if params.assigned_to:
            query_parts.append(f"assigned_to={params.assigned_to}")
        if params.state:
            query_parts.append(f"state={params.state}")
        if params.theme:
            query_parts.append(f"theme={params.theme}")

        query = "^".join(query_parts) if query_parts else None

        params_dict = {
            "sysparm_limit": params.limit,
            "sysparm_offset": params.offset,
        }

        if query:
            params_dict["sysparm_query"] = query

        return await client.send_request("GET", "/api/now/table/rm_epic", params=params_dict)

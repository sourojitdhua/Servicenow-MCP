# src/servicenow_mcp_server/update_set_management/update_set_tools.py

"""
This module defines tools for interacting with ServiceNow Update Sets.
"""

from typing import Dict, Any, Optional
from pydantic import Field
from fastmcp import FastMCP
from servicenow_mcp_server.models import BaseToolParams, get_client
from servicenow_mcp_server.tool_annotations import READ, WRITE
from servicenow_mcp_server.tool_utils import snow_tool

def register_tools(mcp: FastMCP):
    """Adds all tools defined in this file to the main server's MCP instance."""
    _tags = {"update_set"}

    mcp.tool(list_update_sets, tags=_tags | {"read"}, annotations=READ)
    mcp.tool(get_update_set_details, tags=_tags | {"read"}, annotations=READ)
    mcp.tool(create_update_set, tags=_tags | {"write"}, annotations=WRITE)
    mcp.tool(update_update_set, tags=_tags | {"write"}, annotations=WRITE)
    mcp.tool(commit_update_set, tags=_tags | {"write"}, annotations=WRITE)
    mcp.tool(publish_update_set, tags=_tags | {"write"}, annotations=WRITE)
    mcp.tool(add_file_to_update_set, tags=_tags | {"write"}, annotations=WRITE)

# ==============================================================================
#  Pydantic Models
# ==============================================================================

class ListUpdateSetsParams(BaseToolParams):
    state_filter: Optional[str] = Field("in progress", description="Filter by state (e.g., 'in progress', 'complete').")
    name_filter: Optional[str] = Field(None, description="A search term to filter update sets by name.")
    created_by_filter: Optional[str] = Field(None, description="Filter by the username of the creator.")
    limit: int = Field(20, description="The maximum number of records to return.")

class GetUpdateSetDetailsParams(BaseToolParams):
    sys_id: str = Field(..., description="The sys_id of the update set to retrieve.")

class CreateUpdateSetParams(BaseToolParams):
    name: str = Field(..., description="The name of the new update set.")
    description: Optional[str] = Field(None, description="Description of the update set.")

class UpdateUpdateSetParams(BaseToolParams):
    sys_id: str = Field(..., description="The sys_id of the update set to update.")
    name: Optional[str] = Field(None, description="New name for the update set.")
    description: Optional[str] = Field(None, description="Updated description.")

class CommitUpdateSetParams(BaseToolParams):
    sys_id: str = Field(..., description="The sys_id of the update set to commit.")

class PublishUpdateSetParams(BaseToolParams):
    sys_id: str = Field(..., description="The sys_id of the update set to publish.")

class AddFileToUpdateSetParams(BaseToolParams):
    update_set_sys_id: str = Field(..., description="The sys_id of the update set.")
    file_type: str = Field(..., description="Type of configuration file (e.g., 'sys_script', 'sys_script_include').")
    file_sys_id: str = Field(..., description="The sys_id of the record to add to the update set.")

# ==============================================================================
#  Tool Functions
# ==============================================================================

@snow_tool
async def list_update_sets(params: ListUpdateSetsParams) -> Dict[str, Any]:
    """
    List ServiceNow Update Sets from the sys_update_set table. Returns all update sets with optional filtering by state, name, or creator. Use this tool when the user asks about update sets or sys_update_set records.
    """
    async with get_client() as client:
        query_parts = []

        if params.state_filter:
            query_parts.append(f"state={params.state_filter}")
        if params.name_filter:
            query_parts.append(f"nameLIKE{params.name_filter}")
        if params.created_by_filter:
            query_parts.append(f"sys_created_by={params.created_by_filter}")

        final_query = "^".join(query_parts)

        query_params = {
            "sysparm_query": final_query,
            "sysparm_limit": params.limit,
            "sysparm_fields": "name,state,sys_id,sys_created_by,description"
        }

        return await client.send_request("GET", "/api/now/table/sys_update_set", params=query_params)


@snow_tool
async def get_update_set_details(params: GetUpdateSetDetailsParams) -> Dict[str, Any]:
    """
    Retrieve full details for a single ServiceNow Update Set by its sys_id. Queries the sys_update_set table.
    """
    async with get_client() as client:
        return await client.send_request(
            "GET",
            f"/api/now/table/sys_update_set/{params.sys_id}"
        )

@snow_tool
async def create_update_set(params: CreateUpdateSetParams) -> Dict[str, Any]:
    """
    Create a new ServiceNow Update Set in the sys_update_set table. Defaults to 'in progress' state.
    """
    async with get_client() as client:
        payload = params.model_dump(
            exclude=set(),
            exclude_unset=True
        )
        payload.setdefault("state", "in progress")
        return await client.send_request(
            "POST",
            "/api/now/table/sys_update_set",
            data=payload
        )

@snow_tool
async def update_update_set(params: UpdateUpdateSetParams) -> Dict[str, Any]:
    """
    Update an existing ServiceNow Update Set's name or description.
    """
    async with get_client() as client:
        payload = params.model_dump(
            exclude={"sys_id"},
            exclude_unset=True
        )
        return await client.send_request(
            "PATCH",
            f"/api/now/table/sys_update_set/{params.sys_id}",
            data=payload
        )

@snow_tool
async def commit_update_set(params: CommitUpdateSetParams) -> Dict[str, Any]:
    """
    Mark a ServiceNow Update Set as complete (state = 'complete').
    """
    async with get_client() as client:
        payload = {"state": "complete"}
        return await client.send_request(
            "PATCH",
            f"/api/now/table/sys_update_set/{params.sys_id}",
            data=payload
        )

@snow_tool
async def publish_update_set(params: PublishUpdateSetParams) -> Dict[str, Any]:
    """
    Publish a completed ServiceNow Update Set so it can be retrieved from a remote instance.
    """
    async with get_client() as client:
        return await client.send_request(
            "POST",
            f"/api/now/publish/update_set/{params.sys_id}"
        )

@snow_tool
async def add_file_to_update_set(params: AddFileToUpdateSetParams) -> Dict[str, Any]:
    """
    Add (track) a configuration record inside the specified ServiceNow Update Set.
    """
    async with get_client() as client:
        payload = {
            "update_set": params.update_set_sys_id,
            "type": params.file_type,
            "target_sys_id": params.file_sys_id
        }
        return await client.send_request(
            "POST",
            "/api/now/table/sys_update_xml",
            data=payload
        )

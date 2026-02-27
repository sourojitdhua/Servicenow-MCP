# src/servicenow_mcp_server/agile_management/story_tools.py
"""
This module defines tools for interacting with ServiceNow's Agile Development 2.0 application.
This includes stories, epics, and other agile artifacts.
"""

from typing import Dict, Any, Optional
from pydantic import Field
from fastmcp import FastMCP
from servicenow_mcp_server.models import BaseToolParams, get_client
from servicenow_mcp_server.tool_annotations import READ, WRITE, DELETE
from servicenow_mcp_server.tool_utils import snow_tool

def register_tools(main_mcp: FastMCP):
    """Adds all tools defined in this file to the main server's MCP instance."""
    _tags = {"agile"}

    main_mcp.tool(create_story, tags=_tags | {"write"}, annotations=WRITE)
    main_mcp.tool(update_story, tags=_tags | {"write"}, annotations=WRITE)
    main_mcp.tool(list_stories, tags=_tags | {"read"}, annotations=READ)
    main_mcp.tool(create_story_dependency, tags=_tags | {"write"}, annotations=WRITE)
    main_mcp.tool(delete_story_dependency, tags=_tags | {"delete"}, annotations=DELETE)

# ==============================================================================
#  Pydantic Models
# ==============================================================================

class CreateStoryParams(BaseToolParams):
    short_description: str = Field(..., description="A brief, one-line summary of the user story (e.g., 'As a user, I want to...').")
    description: Optional[str] = Field(None, description="A detailed description of the story and its acceptance criteria.")
    assignment_group: Optional[str] = Field(None, description="The sys_id of the group to assign the story to.")
    story_points: Optional[int] = Field(None, description="The estimated effort for the story in points.")
    epic: Optional[str] = Field(None, description="The sys_id of the parent epic this story belongs to.")

class UpdateStoryParams(BaseToolParams):
    story_sys_id: str = Field(..., description="The sys_id of the story to update.")
    short_description: Optional[str] = Field(None, description="A brief, one-line summary of the user story.")
    description: Optional[str] = Field(None, description="A detailed description of the story and its acceptance criteria.")
    assignment_group: Optional[str] = Field(None, description="The sys_id of the group to assign the story to.")
    story_points: Optional[int] = Field(None, description="The estimated effort for the story in points.")
    epic: Optional[str] = Field(None, description="The sys_id of the parent epic this story belongs to.")
    state: Optional[str] = Field(None, description="The sys_id of the story state (e.g., 'Draft', 'Ready').")

class ListStoriesParams(BaseToolParams):
    limit: int = Field(10, description="Maximum number of stories to return.")
    offset: int = Field(0, description="Number of records to skip.")
    assignment_group: Optional[str] = Field(None, description="Filter by assignment group sys_id.")
    epic: Optional[str] = Field(None, description="Filter by parent epic sys_id.")
    state: Optional[str] = Field(None, description="Filter by story state sys_id.")
    assigned_to: Optional[str] = Field(None, description="Filter by assigned user sys_id.")

class CreateStoryDependencyParams(BaseToolParams):
    predecessor_story_sys_id: str = Field(..., description="The sys_id of the story that must be completed first (predecessor).")
    successor_story_sys_id: str = Field(..., description="The sys_id of the story that depends on the predecessor (successor).")
    dependency_type: str = Field("Finish to Start", description="The type of dependency. Default is 'Finish to Start'.")

class DeleteStoryDependencyParams(BaseToolParams):
    dependency_sys_id: str = Field(..., description="The sys_id of the dependency relationship to delete.")

# ==============================================================================
#  Tool Functions
# ==============================================================================

@snow_tool
async def create_story(params: CreateStoryParams) -> Dict[str, Any]:
    """Creates a new user story in the Agile Development 2.0 module."""
    async with get_client() as client:
        payload = params.model_dump(exclude_unset=True)
        return await client.send_request("POST", "/api/now/table/rm_story", data=payload)

@snow_tool
async def update_story(params: UpdateStoryParams) -> Dict[str, Any]:
    """Updates an existing user story in the Agile Development 2.0 module."""
    async with get_client() as client:
        payload = params.model_dump(exclude={"story_sys_id"}, exclude_unset=True)
        return await client.send_request("PATCH", f"/api/now/table/rm_story/{params.story_sys_id}", data=payload)

@snow_tool
async def list_stories(params: ListStoriesParams) -> Dict[str, Any]:
    """Lists user stories with optional filtering and pagination."""
    async with get_client() as client:
        query_params = {"sysparm_limit": params.limit, "sysparm_offset": params.offset}
        filters = []
        if params.assignment_group:
            filters.append(f"assignment_group={params.assignment_group}")
        if params.epic:
            filters.append(f"epic={params.epic}")
        if params.state:
            filters.append(f"state={params.state}")
        if params.assigned_to:
            filters.append(f"assigned_to={params.assigned_to}")

        if filters:
            query_params["sysparm_query"] = "^".join(filters)

        return await client.send_request("GET", "/api/now/table/rm_story", params=query_params)

@snow_tool
async def create_story_dependency(params: CreateStoryDependencyParams) -> Dict[str, Any]:
    """Creates a dependency relationship between two user stories."""
    async with get_client() as client:
        payload = {
            "predecessor": params.predecessor_story_sys_id,
            "successor": params.successor_story_sys_id,
            "type": params.dependency_type
        }
        return await client.send_request("POST", "/api/now/table/rm_story_dependency", data=payload)

@snow_tool
async def delete_story_dependency(params: DeleteStoryDependencyParams) -> Dict[str, Any]:
    """Deletes an existing dependency relationship between user stories."""
    async with get_client() as client:
        return await client.send_request("DELETE", f"/api/now/table/rm_story_dependency/{params.dependency_sys_id}")

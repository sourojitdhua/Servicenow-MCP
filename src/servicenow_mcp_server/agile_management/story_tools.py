# src/servicenow_mcp_server/agile_management/story_tools.py
"""
This module defines tools for interacting with ServiceNow's Agile Development 2.0 application.
This includes stories, epics, and other agile artifacts.
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from fastmcp import FastMCP
from servicenow_mcp_server.utils import ServiceNowClient
from servicenow_mcp_server.models import BaseToolParams
from servicenow_mcp_server.exceptions import ServiceNowError

def register_tools(main_mcp: FastMCP):
    """Adds all tools defined in this file to the main server's MCP instance."""
    main_mcp.add_tool(create_story)
    main_mcp.add_tool(update_story)
    main_mcp.add_tool(list_stories)
    main_mcp.add_tool(create_story_dependency)
    main_mcp.add_tool(delete_story_dependency)

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
    story_sys_id: str = Field(..., description="The sys_id of the story to update.") # Corrected field name
    short_description: Optional[str] = Field(None, description="A brief, one-line summary of the user story.")
    description: Optional[str] = Field(None, description="A detailed description of the story and its acceptance criteria.")
    assignment_group: Optional[str] = Field(None, description="The sys_id of the group to assign the story to.")
    story_points: Optional[int] = Field(None, description="The estimated effort for the story in points.")
    epic: Optional[str] = Field(None, description="The sys_id of the parent epic this story belongs to.")
    state: Optional[str] = Field(None, description="The sys_id of the story state (e.g., 'Draft', 'Ready').")

class ListStoriesParams(BaseToolParams):
    limit: int = Field(10, description="Maximum number of stories to return.") # Made non-optional for clarity
    offset: int = Field(0, description="Number of records to skip.") # Made non-optional for clarity
    assignment_group: Optional[str] = Field(None, description="Filter by assignment group sys_id.")
    epic: Optional[str] = Field(None, description="Filter by parent epic sys_id.")
    state: Optional[str] = Field(None, description="Filter by story state sys_id.")
    assigned_to: Optional[str] = Field(None, description="Filter by assigned user sys_id.")

class CreateStoryDependencyParams(BaseToolParams):
    predecessor_story_sys_id: str = Field(..., description="The sys_id of the story that must be completed first (predecessor).")
    successor_story_sys_id: str = Field(..., description="The sys_id of the story that depends on the predecessor (successor).")
    dependency_type: str = Field("Finish to Start", description="The type of dependency. Default is 'Finish to Start'.") # Made non-optional

class DeleteStoryDependencyParams(BaseToolParams):
    dependency_sys_id: str = Field(..., description="The sys_id of the dependency relationship to delete.") # Corrected field name

# ==============================================================================
#  Tool Functions
# ==============================================================================

async def create_story(params: CreateStoryParams) -> Dict[str, Any]:
    """Creates a new user story in the Agile Development 2.0 module."""
    try:
        async with ServiceNowClient(instance_url=params.instance_url, username=params.username, password=params.password) as client:
            payload = params.model_dump(exclude={"instance_url", "username", "password"}, exclude_unset=True)
            # CORRECTED TABLE NAME for Agile 2.0
            return await client.send_request("POST", "/api/now/table/rm_story", data=payload)
    except ServiceNowError as e:
        return {"error": type(e).__name__, "message": e.message, "details": e.details}

async def update_story(params: UpdateStoryParams) -> Dict[str, Any]:
    """Updates an existing user story in the Agile Development 2.0 module."""
    try:
        async with ServiceNowClient(instance_url=params.instance_url, username=params.username, password=params.password) as client:
            payload = params.model_dump(exclude={"instance_url", "username", "password", "story_sys_id"}, exclude_unset=True)
            # CORRECTED TABLE NAME and using PATCH for partial update
            return await client.send_request("PATCH", f"/api/now/table/rm_story/{params.story_sys_id}", data=payload)
    except ServiceNowError as e:
        return {"error": type(e).__name__, "message": e.message, "details": e.details}

async def list_stories(params: ListStoriesParams) -> Dict[str, Any]:
    """Lists user stories with optional filtering and pagination."""
    try:
        async with ServiceNowClient(instance_url=params.instance_url, username=params.username, password=params.password) as client:
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

            # CORRECTED TABLE NAME
            return await client.send_request("GET", "/api/now/table/rm_story", params=query_params)
    except ServiceNowError as e:
        return {"error": type(e).__name__, "message": e.message, "details": e.details}

async def create_story_dependency(params: CreateStoryDependencyParams) -> Dict[str, Any]:
    """Creates a dependency relationship between two user stories."""
    try:
        async with ServiceNowClient(instance_url=params.instance_url, username=params.username, password=params.password) as client:
            payload = {
                "predecessor": params.predecessor_story_sys_id,
                "successor": params.successor_story_sys_id,
                "type": params.dependency_type
            }
            # CORRECTED TABLE NAME for Agile 2.0 story dependencies
            return await client.send_request("POST", "/api/now/table/rm_story_dependency", data=payload)
    except ServiceNowError as e:
        return {"error": type(e).__name__, "message": e.message, "details": e.details}

async def delete_story_dependency(params: DeleteStoryDependencyParams) -> Dict[str, Any]:
    """Deletes an existing dependency relationship between user stories."""
    try:
        async with ServiceNowClient(instance_url=params.instance_url, username=params.username, password=params.password) as client:
            # CORRECTED TABLE NAME
            return await client.send_request("DELETE", f"/api/now/table/rm_story_dependency/{params.dependency_sys_id}")
    except ServiceNowError as e:
        return {"error": type(e).__name__, "message": e.message, "details": e.details}

# src/servicenow_mcp_server/project_management/project_tools.py

"""
This module defines tools for interacting with the ServiceNow Project Management application.
"""

from typing import Dict, Any, Optional
from pydantic import Field
from fastmcp import FastMCP
from servicenow_mcp_server.models import BaseToolParams, get_client
from servicenow_mcp_server.tool_annotations import READ, WRITE
from servicenow_mcp_server.tool_utils import snow_tool

def register_tools(mcp: FastMCP):
    """Adds all tools defined in this file to the main server's MCP instance."""
    _tags = {"project"}

    mcp.tool(create_project, tags=_tags | {"write"}, annotations=WRITE)
    mcp.tool(update_project, tags=_tags | {"write"}, annotations=WRITE)
    mcp.tool(list_projects, tags=_tags | {"read"}, annotations=READ)

# ==============================================================================
#  Pydantic Models
# ==============================================================================

class CreateProjectParams(BaseToolParams):
    short_description: str = Field(..., description="A brief, one-line summary or name for the project.")
    description: Optional[str] = Field(None, description="A detailed description of the project's goals and scope.")
    project_manager: Optional[str] = Field(None, description="The sys_id of the user who will be the project manager.")
    start_date: Optional[str] = Field(None, description="The planned start date in 'YYYY-MM-DD' format.")
    end_date: Optional[str] = Field(None, description="The planned end date in 'YYYY-MM-DD' format.")

class UpdateProjectParams(BaseToolParams):
    sys_id: str = Field(..., description="The sys_id of the project to update.")
    short_description: Optional[str] = Field(None, description="A brief summary or name for the project.")
    description: Optional[str] = Field(None, description="A detailed description of the project's goals and scope.")
    project_manager: Optional[str] = Field(None, description="The sys_id of the user who will be the project manager.")
    start_date: Optional[str] = Field(None, description="The planned start date in 'YYYY-MM-DD' format.")
    end_date: Optional[str] = Field(None, description="The planned end date in 'YYYY-MM-DD' format.")
    state: Optional[str] = Field(None, description="Desired project state (e.g., 'Draft', 'Planning', 'Work in Progress', 'Completed', 'Cancelled').")

class ListProjectsParams(BaseToolParams):
    project_manager: Optional[str] = Field(None, description="Return only projects managed by this user.")
    state: Optional[str] = Field(None, description="Return only projects in this state.")
    limit: int = Field(10, description="Maximum number of projects to return (max 100).")
    offset: int = Field(0, description="Number of records to skip for pagination.")

# ==============================================================================
#  Tool Functions
# ==============================================================================

@snow_tool
async def create_project(params: CreateProjectParams) -> Dict[str, Any]:
    """
    Creates a new project.
    """
    async with get_client() as client:
        payload = params.model_dump(
            exclude=set(),
            exclude_unset=True
        )

        return await client.send_request("POST", "/api/now/table/pm_project", data=payload)


@snow_tool
async def update_project(params: UpdateProjectParams) -> Dict[str, Any]:
    """
    Updates an existing project in ServiceNow.
    """
    async with get_client() as client:
        payload = params.model_dump(
            exclude={"sys_id"},
            exclude_unset=True
        )
        return await client.send_request(
            "PATCH",
            f"/api/now/table/pm_project/{params.sys_id}",
            data=payload
        )

@snow_tool
async def list_projects(params: ListProjectsParams) -> Dict[str, Any]:
    """
    Lists projects from ServiceNow with optional filters.
    """
    async with get_client() as client:
        query_parts = []
        if params.project_manager:
            query_parts.append(f"project_manager={params.project_manager}")
        if params.state:
            query_parts.append(f"state={params.state}")

        query = "^".join(query_parts)
        params_dict = {
            "sysparm_limit": min(max(params.limit, 1), 100),
            "sysparm_offset": max(params.offset, 0)
        }
        if query:
            params_dict["sysparm_query"] = query

        return await client.send_request(
            "GET",
            "/api/now/table/pm_project",
            params=params_dict
        )

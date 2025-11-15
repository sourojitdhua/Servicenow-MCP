# src/servicenow_mcp_server/problem_management/problem_tools.py

"""
Tools for interacting with the ServiceNow Problem Management process.
"""

from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
from fastmcp import FastMCP

from servicenow_mcp_server.models import BaseToolParams
from servicenow_mcp_server.utils import ServiceNowClient
from servicenow_mcp_server.exceptions import ServiceNowError


# ==============================================================================
#  Tool Registration
# ==============================================================================

def register_tools(mcp: FastMCP):
    """Registers all problem management tools with the main MCP server instance."""
    mcp.add_tool(create_problem)
    mcp.add_tool(update_problem)
    mcp.add_tool(list_problems)
    mcp.add_tool(get_problem)
    mcp.add_tool(create_known_error)


# ==============================================================================
#  Pydantic Models
# ==============================================================================

class CreateProblemParams(BaseToolParams):
    short_description: str = Field(..., description="A brief, one-line summary of the problem.")
    description: Optional[str] = Field(None, description="A detailed description of the problem.")
    impact: str = Field("3", description="Impact of the problem (1-High, 2-Medium, 3-Low).")
    urgency: str = Field("3", description="Urgency of the problem (1-High, 2-Medium, 3-Low).")
    assignment_group: Optional[str] = Field(None, description="The sys_id of the group to assign the problem to.")
    assigned_to: Optional[str] = Field(None, description="The sys_id of the user to assign the problem to.")


class UpdateProblemParams(BaseToolParams):
    sys_id: str = Field(..., description="The sys_id of the problem to update.")
    short_description: Optional[str] = Field(None, description="Updated summary.")
    description: Optional[str] = Field(None, description="Updated detailed description.")
    impact: Optional[str] = Field(None, description="Updated impact (1-High, 2-Medium, 3-Low).")
    urgency: Optional[str] = Field(None, description="Updated urgency (1-High, 2-Medium, 3-Low).")
    assignment_group: Optional[str] = Field(None, description="Updated assignment group sys_id.")
    assigned_to: Optional[str] = Field(None, description="Updated assigned user sys_id.")
    state: Optional[str] = Field(None, description="New problem state (e.g., '1' New, '2' Assess, '3' Root Cause Analysis, '4' Fix in Progress, '6' Resolved, '7' Closed).")


class ListProblemsParams(BaseToolParams):
    query: Optional[str] = Field(None, description="ServiceNow-encoded query string to filter problems.")
    limit: int = Field(10, description="Maximum number of problems to return.")
    offset: int = Field(0, description="Record offset for pagination.")


class GetProblemParams(BaseToolParams):
    sys_id: str = Field(..., description="The sys_id of the problem to retrieve.")


class CreateKnownErrorParams(BaseToolParams):
    sys_id: str = Field(..., description="The sys_id of the problem to mark as a Known Error.")
    workaround: str = Field(..., description="The workaround description for the known error.")


# ==============================================================================
#  Tool Functions
# ==============================================================================

async def create_problem(params: CreateProblemParams) -> Dict[str, Any]:
    """
    Creates a new problem record in ServiceNow.
    """
    try:
        async with ServiceNowClient(
            instance_url=params.instance_url,
            username=params.username,
            password=params.password,
        ) as client:
            payload = params.model_dump(
                exclude={"instance_url", "username", "password"},
                exclude_unset=True,
            )
            return await client.send_request("POST", "/api/now/table/problem", data=payload)
    except ServiceNowError as e:
        return {"error": type(e).__name__, "message": e.message, "details": e.details}


async def update_problem(params: UpdateProblemParams) -> Dict[str, Any]:
    """
    Updates one or more fields on an existing problem record.
    """
    try:
        async with ServiceNowClient(
            instance_url=params.instance_url,
            username=params.username,
            password=params.password,
        ) as client:
            update_data = params.model_dump(
                exclude={"sys_id", "instance_url", "username", "password"},
                exclude_unset=True,
            )
            if not update_data:
                return {"error": "No update data provided.", "message": "You must provide at least one field to update."}

            endpoint = f"/api/now/table/problem/{params.sys_id}"
            return await client.send_request("PATCH", endpoint, data=update_data)
    except ServiceNowError as e:
        return {"error": type(e).__name__, "message": e.message, "details": e.details}


async def list_problems(params: ListProblemsParams) -> Dict[str, Any]:
    """
    Lists problem records with optional filtering and pagination.
    """
    try:
        async with ServiceNowClient(
            instance_url=params.instance_url,
            username=params.username,
            password=params.password,
        ) as client:
            query_params = {
                "sysparm_limit": params.limit,
                "sysparm_offset": params.offset,
            }
            if params.query:
                query_params["sysparm_query"] = params.query

            return await client.send_request("GET", "/api/now/table/problem", params=query_params)
    except ServiceNowError as e:
        return {"error": type(e).__name__, "message": e.message, "details": e.details}


async def get_problem(params: GetProblemParams) -> Dict[str, Any]:
    """
    Retrieves the full details of a single problem record by its sys_id.
    """
    try:
        async with ServiceNowClient(
            instance_url=params.instance_url,
            username=params.username,
            password=params.password,
        ) as client:
            return await client.send_request("GET", f"/api/now/table/problem/{params.sys_id}")
    except ServiceNowError as e:
        return {"error": type(e).__name__, "message": e.message, "details": e.details}


async def create_known_error(params: CreateKnownErrorParams) -> Dict[str, Any]:
    """
    Marks an existing problem as a Known Error and sets the workaround.
    """
    try:
        async with ServiceNowClient(
            instance_url=params.instance_url,
            username=params.username,
            password=params.password,
        ) as client:
            payload = {
                "known_error": "true",
                "work_around": params.workaround,
            }
            endpoint = f"/api/now/table/problem/{params.sys_id}"
            return await client.send_request("PATCH", endpoint, data=payload)
    except ServiceNowError as e:
        return {"error": type(e).__name__, "message": e.message, "details": e.details}

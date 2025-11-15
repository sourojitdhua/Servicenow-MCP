# src/servicenow_mcp_server/script_include_management/script_include_tools.py

"""
This module defines tools for interacting with ServiceNow Script Includes.
"""

from typing import Dict, Any, Optional
from pydantic import Field
from fastmcp import FastMCP
from servicenow_mcp_server.utils import ServiceNowClient
from servicenow_mcp_server.models import BaseToolParams
from servicenow_mcp_server.exceptions import ServiceNowError

def register_tools(mcp: FastMCP):
    """Adds all tools defined in this file to the main server's MCP instance."""
    mcp.add_tool(list_script_includes)
    mcp.add_tool(get_script_include)
    mcp.add_tool(create_script_include)
    mcp.add_tool(update_script_include)
    mcp.add_tool(delete_script_include)

# ==============================================================================
#  Pydantic Models
# ==============================================================================

class ListScriptIncludesParams(BaseToolParams):
    name_filter: Optional[str] = Field(None, description="A search term to filter Script Includes by name.")
    api_name_filter: Optional[str] = Field(None, description="Filter by the specific API name (e.g., 'global.MyUtils').")
    limit: int = Field(20, description="The maximum number of records to return.")

class GetScriptIncludeParams(BaseToolParams):
    sys_id: str = Field(..., description="The sys_id of the Script Include to retrieve.")

class CreateScriptIncludeParams(BaseToolParams):
    name: str = Field(..., description="The name of the new Script Include.")
    api_name: str = Field(..., description="The fully-qualified API name (e.g., 'global.MyUtils').")
    script: str = Field(..., description="The JavaScript code of the Script Include.")
    client_callable: bool = Field(False, description="Whether the Script Include can be called from the client.")
    description: Optional[str] = Field(None, description="Description of the Script Include.")
    active: bool = Field(True, description="Whether the Script Include is active.")

class UpdateScriptIncludeParams(BaseToolParams):
    sys_id: str = Field(..., description="The sys_id of the Script Include to update.")
    name: Optional[str] = Field(None, description="New name of the Script Include.")
    api_name: Optional[str] = Field(None, description="New fully-qualified API name.")
    script: Optional[str] = Field(None, description="Updated JavaScript code.")
    client_callable: Optional[bool] = Field(None, description="Toggle client-callable flag.")
    description: Optional[str] = Field(None, description="Updated description.")
    active: Optional[bool] = Field(None, description="Toggle active flag.")

class DeleteScriptIncludeParams(BaseToolParams):
    sys_id: str = Field(..., description="The sys_id of the Script Include to delete.")

# ==============================================================================
#  Tool Functions
# ==============================================================================

async def list_script_includes(params: ListScriptIncludesParams) -> Dict[str, Any]:
    """
    Lists Script Includes, with options to filter by name or API name.
    """
    try:
        async with ServiceNowClient(instance_url=params.instance_url, username=params.username, password=params.password) as client:
            # The table for Script Includes is 'sys_script_include'.
            query_parts = ["active=true"]

            if params.name_filter:
                query_parts.append(f"nameLIKE{params.name_filter}")
            if params.api_name_filter:
                query_parts.append(f"api_name={params.api_name_filter}")

            final_query = "^".join(query_parts)

            query_params = {
                "sysparm_query": final_query,
                "sysparm_limit": params.limit,
                "sysparm_fields": "name,api_name,sys_id,active,description"
            }

            return await client.send_request("GET", "/api/now/table/sys_script_include", params=query_params)
    except ServiceNowError as e:
        return {"error": type(e).__name__, "message": e.message, "details": e.details}


async def get_script_include(params: GetScriptIncludeParams) -> Dict[str, Any]:
    """
    Retrieve a single Script Include by sys_id.
    """
    try:
        async with ServiceNowClient(instance_url=params.instance_url, username=params.username, password=params.password) as client:
            return await client.send_request(
                "GET",
                f"/api/now/table/sys_script_include/{params.sys_id}"
            )
    except ServiceNowError as e:
        return {"error": type(e).__name__, "message": e.message, "details": e.details}

async def create_script_include(params: CreateScriptIncludeParams) -> Dict[str, Any]:
    """
    Create a new Script Include in ServiceNow.
    """
    try:
        async with ServiceNowClient(instance_url=params.instance_url, username=params.username, password=params.password) as client:
            payload = params.model_dump(
                exclude={"instance_url", "username", "password"},
                exclude_unset=True
            )
            return await client.send_request(
                "POST",
                "/api/now/table/sys_script_include",
                data=payload
            )
    except ServiceNowError as e:
        return {"error": type(e).__name__, "message": e.message, "details": e.details}

async def update_script_include(params: UpdateScriptIncludeParams) -> Dict[str, Any]:
    """
    Update an existing Script Include in ServiceNow.
    """
    try:
        async with ServiceNowClient(instance_url=params.instance_url, username=params.username, password=params.password) as client:
            payload = params.model_dump(
                exclude={"instance_url", "username", "password", "sys_id"},
                exclude_unset=True
            )
            return await client.send_request(
                "PATCH",
                f"/api/now/table/sys_script_include/{params.sys_id}",
                data=payload
            )
    except ServiceNowError as e:
        return {"error": type(e).__name__, "message": e.message, "details": e.details}

async def delete_script_include(params: DeleteScriptIncludeParams) -> Dict[str, Any]:
    """
    Delete a Script Include from ServiceNow.
    """
    try:
        async with ServiceNowClient(instance_url=params.instance_url, username=params.username, password=params.password) as client:
            return await client.send_request(
                "DELETE",
                f"/api/now/table/sys_script_include/{params.sys_id}"
            )
    except ServiceNowError as e:
        return {"error": type(e).__name__, "message": e.message, "details": e.details}

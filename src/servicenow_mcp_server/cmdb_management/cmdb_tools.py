# src/servicenow_mcp_server/cmdb_management/cmdb_tools.py

"""
Tools for interacting with the ServiceNow Configuration Management Database (CMDB).
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
    """Registers all CMDB management tools with the main MCP server instance."""
    mcp.add_tool(list_ci_classes)
    mcp.add_tool(get_ci)
    mcp.add_tool(list_cis)
    mcp.add_tool(create_ci)
    mcp.add_tool(update_ci)
    mcp.add_tool(get_ci_relationships)


# ==============================================================================
#  Pydantic Models
# ==============================================================================

class ListCIClassesParams(BaseToolParams):
    filter: Optional[str] = Field(None, description="A search term to filter CI class names (e.g., 'server', 'network').")
    limit: int = Field(50, description="Maximum number of CI classes to return.")


class GetCIParams(BaseToolParams):
    sys_id: str = Field(..., description="The sys_id of the Configuration Item to retrieve.")
    ci_class: str = Field("cmdb_ci", description="The CMDB class table name (e.g., 'cmdb_ci_server', 'cmdb_ci_computer'). Defaults to the base 'cmdb_ci'.")


class ListCIsParams(BaseToolParams):
    ci_class: str = Field("cmdb_ci", description="The CMDB class table name (e.g., 'cmdb_ci_server'). Defaults to 'cmdb_ci'.")
    query: Optional[str] = Field(None, description="ServiceNow-encoded query string to filter CIs.")
    limit: int = Field(10, description="Maximum number of CIs to return.")
    offset: int = Field(0, description="Record offset for pagination.")


class CreateCIParams(BaseToolParams):
    ci_class: str = Field("cmdb_ci", description="The CMDB class table to create the CI in (e.g., 'cmdb_ci_server').")
    name: str = Field(..., description="The name of the Configuration Item.")
    data: Optional[Dict[str, Any]] = Field(None, description="Additional fields to set on the CI record.")


class UpdateCIParams(BaseToolParams):
    ci_class: str = Field("cmdb_ci", description="The CMDB class table containing the CI.")
    sys_id: str = Field(..., description="The sys_id of the CI to update.")
    data: Dict[str, Any] = Field(..., description="A dictionary of fields and values to update.")


class GetCIRelationshipsParams(BaseToolParams):
    sys_id: str = Field(..., description="The sys_id of the CI whose relationships you want to find.")
    limit: int = Field(20, description="Maximum number of relationship records to return.")


# ==============================================================================
#  Tool Functions
# ==============================================================================

async def list_ci_classes(params: ListCIClassesParams) -> Dict[str, Any]:
    """
    Lists CMDB CI classes by querying the sys_db_object table filtered for CMDB tables.
    """
    try:
        async with ServiceNowClient(
            instance_url=params.instance_url,
            username=params.username,
            password=params.password,
        ) as client:
            query_parts = ["nameSTARTSWITHcmdb_ci"]
            if params.filter:
                query_parts.append(f"nameLIKE{params.filter}^ORlabelLIKE{params.filter}")

            final_query = "^".join(query_parts)
            query_params = {
                "sysparm_query": final_query,
                "sysparm_fields": "name,label,super_class",
                "sysparm_limit": params.limit,
            }
            return await client.send_request("GET", "/api/now/table/sys_db_object", params=query_params)
    except ServiceNowError as e:
        return {"error": type(e).__name__, "message": e.message, "details": e.details}


async def get_ci(params: GetCIParams) -> Dict[str, Any]:
    """
    Retrieves the full details of a single Configuration Item by its sys_id.
    """
    try:
        async with ServiceNowClient(
            instance_url=params.instance_url,
            username=params.username,
            password=params.password,
        ) as client:
            endpoint = f"/api/now/table/{params.ci_class}/{params.sys_id}"
            return await client.send_request("GET", endpoint)
    except ServiceNowError as e:
        return {"error": type(e).__name__, "message": e.message, "details": e.details}


async def list_cis(params: ListCIsParams) -> Dict[str, Any]:
    """
    Lists Configuration Items from a CMDB class table with query and pagination support.
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

            endpoint = f"/api/now/table/{params.ci_class}"
            return await client.send_request("GET", endpoint, params=query_params)
    except ServiceNowError as e:
        return {"error": type(e).__name__, "message": e.message, "details": e.details}


async def create_ci(params: CreateCIParams) -> Dict[str, Any]:
    """
    Creates a new Configuration Item in the specified CMDB class table.
    """
    try:
        async with ServiceNowClient(
            instance_url=params.instance_url,
            username=params.username,
            password=params.password,
        ) as client:
            payload: Dict[str, Any] = {"name": params.name}
            if params.data:
                payload.update(params.data)

            endpoint = f"/api/now/table/{params.ci_class}"
            return await client.send_request("POST", endpoint, data=payload)
    except ServiceNowError as e:
        return {"error": type(e).__name__, "message": e.message, "details": e.details}


async def update_ci(params: UpdateCIParams) -> Dict[str, Any]:
    """
    Updates an existing Configuration Item in the specified CMDB class table.
    """
    try:
        async with ServiceNowClient(
            instance_url=params.instance_url,
            username=params.username,
            password=params.password,
        ) as client:
            endpoint = f"/api/now/table/{params.ci_class}/{params.sys_id}"
            return await client.send_request("PATCH", endpoint, data=params.data)
    except ServiceNowError as e:
        return {"error": type(e).__name__, "message": e.message, "details": e.details}


async def get_ci_relationships(params: GetCIRelationshipsParams) -> Dict[str, Any]:
    """
    Retrieves all relationships for a Configuration Item (both parent and child).
    Queries the cmdb_rel_ci table.
    """
    try:
        async with ServiceNowClient(
            instance_url=params.instance_url,
            username=params.username,
            password=params.password,
        ) as client:
            query = f"parent={params.sys_id}^ORchild={params.sys_id}"
            query_params = {
                "sysparm_query": query,
                "sysparm_limit": params.limit,
            }
            return await client.send_request("GET", "/api/now/table/cmdb_rel_ci", params=query_params)
    except ServiceNowError as e:
        return {"error": type(e).__name__, "message": e.message, "details": e.details}

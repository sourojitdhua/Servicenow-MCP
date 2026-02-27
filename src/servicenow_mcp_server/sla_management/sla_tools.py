# src/servicenow_mcp_server/sla_management/sla_tools.py

"""
Tools for interacting with ServiceNow SLA definitions and task SLAs.
"""

from typing import Dict, Any, Optional
from pydantic import Field
from fastmcp import FastMCP

from servicenow_mcp_server.models import BaseToolParams, get_client
from servicenow_mcp_server.tool_annotations import READ
from servicenow_mcp_server.tool_utils import snow_tool


# ==============================================================================
#  Tool Registration
# ==============================================================================

def register_tools(mcp: FastMCP):
    """Registers all SLA management tools with the main MCP server instance."""
    _tags = {"sla"}

    mcp.tool(list_sla_definitions, tags=_tags | {"read"}, annotations=READ)
    mcp.tool(get_task_sla, tags=_tags | {"read"}, annotations=READ)
    mcp.tool(list_breached_slas, tags=_tags | {"read"}, annotations=READ)


# ==============================================================================
#  Pydantic Models
# ==============================================================================

class ListSLADefinitionsParams(BaseToolParams):
    query: Optional[str] = Field(None, description="ServiceNow-encoded query string to filter SLA definitions.")
    limit: int = Field(20, description="Maximum number of SLA definitions to return.")


class GetTaskSLAParams(BaseToolParams):
    task_sys_id: str = Field(..., description="The sys_id of the task whose SLAs you want to retrieve.")
    limit: int = Field(10, description="Maximum number of task SLA records to return.")


class ListBreachedSLAsParams(BaseToolParams):
    query: Optional[str] = Field(None, description="Additional query to filter breached SLAs (e.g., by assignment group).")
    limit: int = Field(20, description="Maximum number of breached SLA records to return.")
    offset: int = Field(0, description="Record offset for pagination.")


# ==============================================================================
#  Tool Functions
# ==============================================================================

@snow_tool
async def list_sla_definitions(params: ListSLADefinitionsParams) -> Dict[str, Any]:
    """
    Lists SLA definitions from the contract_sla table.
    """
    async with get_client() as client:
        query_params = {"sysparm_limit": params.limit}
        if params.query:
            query_params["sysparm_query"] = params.query

        return await client.send_request("GET", "/api/now/table/contract_sla", params=query_params)


@snow_tool
async def get_task_sla(params: GetTaskSLAParams) -> Dict[str, Any]:
    """
    Retrieves SLA records attached to a specific task.
    """
    async with get_client() as client:
        query_params = {
            "sysparm_query": f"task={params.task_sys_id}",
            "sysparm_limit": params.limit,
        }
        return await client.send_request("GET", "/api/now/table/task_sla", params=query_params)


@snow_tool
async def list_breached_slas(params: ListBreachedSLAsParams) -> Dict[str, Any]:
    """
    Lists task SLA records that have been breached (has_breached=true).
    """
    async with get_client() as client:
        query_parts = ["has_breached=true"]
        if params.query:
            query_parts.append(params.query)

        query_params = {
            "sysparm_query": "^".join(query_parts),
            "sysparm_limit": params.limit,
            "sysparm_offset": params.offset,
        }
        return await client.send_request("GET", "/api/now/table/task_sla", params=query_params)

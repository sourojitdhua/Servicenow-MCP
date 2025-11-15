# src/servicenow_mcp_server/workflow_management/workflow_tools.py

"""
This module defines tools for interacting with ServiceNow Workflow definitions.
"""

from typing import Dict, Any, Optional
from pydantic import Field
from fastmcp import FastMCP
from servicenow_mcp_server.utils import ServiceNowClient
from servicenow_mcp_server.models import BaseToolParams
from servicenow_mcp_server.exceptions import ServiceNowError

def register_tools(mcp: FastMCP):
    """Adds all tools defined in this file to the main server's MCP instance."""
    mcp.add_tool(list_workflows)
    mcp.add_tool(get_workflow)
    mcp.add_tool(create_workflow)
    mcp.add_tool(update_workflow)
    mcp.add_tool(delete_workflow)

# ==============================================================================
#  Pydantic Models
# ==============================================================================

class ListWorkflowsParams(BaseToolParams):
    name_filter: Optional[str] = Field(None, description="A search term to filter workflows by name.")
    table_filter: Optional[str] = Field(None, description="Return only workflows that run on this specific table (e.g., 'sc_req_item').")
    limit: int = Field(20, description="The maximum number of workflows to return.")

class GetWorkflowParams(BaseToolParams):
    sys_id: str = Field(..., description="The sys_id of the workflow to retrieve.")

class CreateWorkflowParams(BaseToolParams):
    name: str = Field(..., description="The name of the new workflow.")
    table: str = Field(..., description="The table on which the workflow runs (e.g., 'sc_req_item').")
    description: Optional[str] = Field(None, description="Description of the workflow.")
    published: bool = Field(False, description="Whether to publish the workflow immediately.")

class UpdateWorkflowParams(BaseToolParams):
    sys_id: str = Field(..., description="The sys_id of the workflow to update.")
    name: Optional[str] = Field(None, description="New name for the workflow.")
    description: Optional[str] = Field(None, description="New description.")
    published: Optional[bool] = Field(None, description="Whether to publish / unpublish the workflow.")

class DeleteWorkflowParams(BaseToolParams):
    sys_id: str = Field(..., description="The sys_id of the workflow to delete.")

# ==============================================================================
#  Tool Functions
# ==============================================================================

async def list_workflows(params: ListWorkflowsParams) -> Dict[str, Any]:
    """
    Lists workflow definitions, with options to filter by name or associated table.
    """
    try:
        async with ServiceNowClient(instance_url=params.instance_url, username=params.username, password=params.password) as client:
            # The table for workflow definitions is 'wf_workflow'.
            query_parts = ["published=true"] # Typically only want to see active, published workflows

            if params.name_filter:
                query_parts.append(f"nameLIKE{params.name_filter}")
            if params.table_filter:
                query_parts.append(f"table={params.table_filter}")

            final_query = "^".join(query_parts)

            query_params = {
                "sysparm_query": final_query,
                "sysparm_limit": params.limit,
                "sysparm_fields": "name,table,sys_id,published,description"
            }

            return await client.send_request("GET", "/api/now/table/wf_workflow", params=query_params)
    except ServiceNowError as e:
        return {"error": type(e).__name__, "message": e.message, "details": e.details}


async def get_workflow(params: GetWorkflowParams) -> Dict[str, Any]:
    """
    Retrieve a single workflow definition by sys_id.
    """
    try:
        async with ServiceNowClient(instance_url=params.instance_url, username=params.username, password=params.password) as client:
            return await client.send_request(
                "GET",
                f"/api/now/table/wf_workflow/{params.sys_id}"
            )
    except ServiceNowError as e:
        return {"error": type(e).__name__, "message": e.message, "details": e.details}

async def create_workflow(params: CreateWorkflowParams) -> Dict[str, Any]:
    """
    Create a new workflow definition.
    """
    try:
        async with ServiceNowClient(instance_url=params.instance_url, username=params.username, password=params.password) as client:
            payload = params.model_dump(
                exclude={"instance_url", "username", "password"},
                exclude_unset=True
            )
            return await client.send_request(
                "POST",
                "/api/now/table/wf_workflow",
                data=payload
            )
    except ServiceNowError as e:
        return {"error": type(e).__name__, "message": e.message, "details": e.details}

async def update_workflow(params: UpdateWorkflowParams) -> Dict[str, Any]:
    """
    Update an existing workflow definition.
    """
    try:
        async with ServiceNowClient(instance_url=params.instance_url, username=params.username, password=params.password) as client:
            payload = params.model_dump(
                exclude={"instance_url", "username", "password", "sys_id"},
                exclude_unset=True
            )
            return await client.send_request(
                "PATCH",
                f"/api/now/table/wf_workflow/{params.sys_id}",
                data=payload
            )
    except ServiceNowError as e:
        return {"error": type(e).__name__, "message": e.message, "details": e.details}

async def delete_workflow(params: DeleteWorkflowParams) -> Dict[str, Any]:
    """
    Delete a workflow definition from ServiceNow.
    """
    try:
        async with ServiceNowClient(instance_url=params.instance_url, username=params.username, password=params.password) as client:
            return await client.send_request(
                "DELETE",
                f"/api/now/table/wf_workflow/{params.sys_id}"
            )
    except ServiceNowError as e:
        return {"error": type(e).__name__, "message": e.message, "details": e.details}

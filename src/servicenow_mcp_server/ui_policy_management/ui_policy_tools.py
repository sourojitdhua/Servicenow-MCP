# src/servicenow_mcp_server/ui_policy_management/ui_policy_tools.py

"""
This module defines tools for managing UI Policies in ServiceNow.
"""

from typing import Dict, Any, Optional
from pydantic import Field
from fastmcp import FastMCP
from servicenow_mcp_server.models import BaseToolParams, get_client
from servicenow_mcp_server.tool_annotations import WRITE
from servicenow_mcp_server.tool_utils import snow_tool

def register_tools(mcp: FastMCP):
    """Adds all tools defined in this file to the main server's MCP instance."""
    _tags = {"ui_policy"}

    mcp.tool(create_ui_policy, tags=_tags | {"write"}, annotations=WRITE)
    mcp.tool(create_ui_policy_action, tags=_tags | {"write"}, annotations=WRITE)

# ==============================================================================
#  Pydantic Models
# ==============================================================================

class CreateUIPolicyParams(BaseToolParams):
    table: str = Field(..., description="The table the UI policy applies to (e.g., 'sc_cat_item').")
    short_description: str = Field(..., description="A short, clear description of what the policy does.")
    conditions: str = Field(..., description="The encoded query string for the conditions (e.g., 'variable_name=value').")
    catalog_item: Optional[str] = Field(None, description="The sys_id of the catalog item this policy applies to (if applicable).")
    reverse_if_false: bool = Field(True, description="If true, the policy actions are reversed when the conditions are not met.")

class CreateUIPolicyActionParams(BaseToolParams):
    ui_policy_sys_id: str = Field(..., description="sys_id of the parent UI Policy.")
    catalog_item_sys_id: str = Field(..., description="sys_id of the Catalog Item this policy belongs to.")
    variable_name: str = Field(..., description="Name of the catalog variable the action affects (e.g., 'business_justification_mcp').")
    mandatory: Optional[str] = Field(None, description="Set field mandatory status. Options: 'true', 'false', 'leave'.")
    visible: Optional[str] = Field(None, description="Set field visibility. Options: 'true', 'false', 'leave'.")
    read_only: Optional[str] = Field(None, description="Set field read-only status. Options: 'true', 'false', 'leave'.")


# ==============================================================================
#  Tool Functions
# ==============================================================================

@snow_tool
async def create_ui_policy(params: CreateUIPolicyParams) -> Dict[str, Any]:
    """
    Creates a new UI Policy.
    """
    async with get_client() as client:
        payload = params.model_dump(
            exclude=set(),
            exclude_unset=True
        )

        if params.table == 'sc_cat_item' and params.catalog_item:
            payload['catalog_ui_policy'] = params.catalog_item

        return await client.send_request("POST", "/api/now/table/sys_ui_policy", data=payload)


@snow_tool
async def create_ui_policy_action(params: CreateUIPolicyActionParams) -> Dict[str, Any]:
    """
    Creates a UI Policy Action that controls the state of a catalog variable.
    """
    async with get_client() as client:
        # Step 1: Find the variable by name within the provided catalog item.
        variable_query = f"cat_item={params.catalog_item_sys_id}^name={params.variable_name}"
        variable_response = await client.send_request("GET", "/api/now/table/item_option_new", params={"sysparm_query": variable_query, "sysparm_limit": 1})

        if not variable_response.get('result'):
            return {"error": "Variable not found.", "message": f"Could not find a variable named '{params.variable_name}' on the catalog item '{params.catalog_item_sys_id}'."}

        variable_sys_id = variable_response['result'][0]['sys_id']

        # Step 2: Create the action record with the correct references.
        payload = {
            "ui_policy": params.ui_policy_sys_id,
            "catalog_variable": f"IO:{variable_sys_id}",
            "mandatory": params.mandatory,
            "visible": params.visible,
            "read_only": params.read_only,
        }
        final_payload = {k: v for k, v in payload.items() if v is not None}

        return await client.send_request("POST", "/api/now/table/catalog_ui_policy_action", data=final_payload)

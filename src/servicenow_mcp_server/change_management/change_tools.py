# src/servicenow_mcp_server/change_management/change_tools.py

"""
This module defines tools for interacting with the ServiceNow Change Management process.
"""

from typing import Dict, Any, Optional
from pydantic import Field
from fastmcp import FastMCP
from servicenow_mcp_server.utils import ServiceNowClient
from servicenow_mcp_server.models import BaseToolParams
from servicenow_mcp_server.constants import ChangeState
from servicenow_mcp_server.exceptions import ServiceNowError

def register_tools(mcp: FastMCP):
    """Adds all tools defined in this file to the main server's MCP instance."""
    mcp.add_tool(create_change_request)
    mcp.add_tool(update_change_request)
    mcp.add_tool(list_change_requests)
    mcp.add_tool(get_change_request_details)
    mcp.add_tool(add_change_task)
    mcp.add_tool(submit_change_for_approval)
    mcp.add_tool(approve_change)
    mcp.add_tool(reject_change)


# ==============================================================================
#  Pydantic Models
# ==============================================================================

class CreateChangeRequestParams(BaseToolParams):
    short_description: str = Field(..., description="A brief, one-line summary of the change.")
    description: str = Field(..., description="A detailed description of the purpose and plan for the change.")
    type: str = Field("Normal", description="The type of change. Options: 'Normal', 'Standard', 'Emergency'.")
    impact: str = Field("3", description="The impact of the change (1-High, 2-Medium, 3-Low).")
    urgency: str = Field("3", description="The urgency of the change (1-High, 2-Medium, 3-Low).")
    assignment_group: Optional[str] = Field(None, description="The sys_id of the group to assign the change to.")
    justification: Optional[str] = Field(None, description="The business justification for the change.")
    start_date: Optional[str] = Field(None, description="The planned start date in 'YYYY-MM-DD HH:MM:SS' format.")
    end_date: Optional[str] = Field(None, description="The planned end date in 'YYYY-MM-DD HH:MM:SS' format.")

class UpdateChangeRequestParams(BaseToolParams):
    sys_id: str = Field(..., description="The sys_id of the change request to update.")
    short_description: Optional[str] = Field(None, description="A new one-line summary for the change.")
    description: Optional[str] = Field(None, description="A new detailed description for the change.")
    impact: Optional[str] = Field(None, description="A new impact value (1-High, 2-Medium, 3-Low).")
    urgency: Optional[str] = Field(None, description="A new urgency value (1-High, 2-Medium, 3-Low).")
    justification: Optional[str] = Field(None, description="An updated business justification for the change.")
    start_date: Optional[str] = Field(None, description="An updated planned start date in 'YYYY-MM-DD HH:MM:SS' format.")
    end_date: Optional[str] = Field(None, description="An updated planned end date in 'YYYY-MM-DD HH:MM:SS' format.")

class ListChangeRequestsParams(BaseToolParams):
    limit: int = Field(10, description="The maximum number of change requests to return.")
    offset: int = Field(0, description="The record number to start from for pagination.")
    query: Optional[str] = Field(None, description="ServiceNow-encoded query string (e.g., 'active=true^type=Normal').")

class GetChangeRequestDetailsParams(BaseToolParams):
    sys_id: Optional[str] = Field(None, description="The sys_id of the change request to retrieve.")
    number: Optional[str] = Field(None, description="The number of the change request to retrieve (e.g., 'CHG0000014').")

class AddChangeTaskParams(BaseToolParams):
    change_request_sys_id: str = Field(..., description="The sys_id of the parent change request.")
    short_description: str = Field(..., description="A brief summary of the task to be performed.")

class SubmitChangeForApprovalParams(BaseToolParams):
    sys_id: str = Field(..., description="The sys_id of the change request to submit for approval.")

class ApproveChangeParams(BaseToolParams):
    sys_id: str = Field(..., description="The sys_id of the change request to approve.")
    approval_notes: Optional[str] = Field(None, description="Optional notes to include with the approval.")

class RejectChangeParams(BaseToolParams):
    sys_id: str = Field(..., description="The sys_id of the change request to reject.")
    rejection_comments: str = Field(..., description="Mandatory comments explaining the reason for the rejection.")
# ==============================================================================
#  Tool Functions
# ==============================================================================

async def create_change_request(params: CreateChangeRequestParams) -> Dict[str, Any]:
    """
    Creates a new Normal, Standard, or Emergency change request.
    """
    try:
        async with ServiceNowClient(instance_url=params.instance_url, username=params.username, password=params.password) as client:
            # Create the payload from the Pydantic model
            payload = params.model_dump(
                exclude={"instance_url", "username", "password"},
                exclude_unset=True
            )

            # We POST to the 'change_request' table.
            return await client.send_request("POST", "/api/now/table/change_request", data=payload)
    except ServiceNowError as e:
        return {"error": type(e).__name__, "message": e.message, "details": e.details}

async def update_change_request(params: UpdateChangeRequestParams) -> Dict[str, Any]:
    """
    Updates one or more fields on an existing change request.
    """
    try:
        async with ServiceNowClient(instance_url=params.instance_url, username=params.username, password=params.password) as client:
            update_data = params.model_dump(
                exclude={"sys_id", "instance_url", "username", "password"},
                exclude_unset=True
            )
            if not update_data:
                return {"error": "No update data provided.", "message": "You must provide at least one field to update."}

            endpoint = f"/api/now/table/change_request/{params.sys_id}"
            return await client.send_request("PATCH", endpoint, data=update_data)
    except ServiceNowError as e:
        return {"error": type(e).__name__, "message": e.message, "details": e.details}

async def list_change_requests(params: ListChangeRequestsParams) -> Dict[str, Any]:
    """
    Lists change requests with optional filtering and pagination.
    """
    try:
        async with ServiceNowClient(instance_url=params.instance_url, username=params.username, password=params.password) as client:
            query_params = {
                "sysparm_limit": params.limit,
                "sysparm_offset": params.offset
            }
            if params.query:
                query_params["sysparm_query"] = params.query

            return await client.send_request("GET", "/api/now/table/change_request", params=query_params)
    except ServiceNowError as e:
        return {"error": type(e).__name__, "message": e.message, "details": e.details}

async def get_change_request_details(params: GetChangeRequestDetailsParams) -> Dict[str, Any]:
    """
    Retrieves the full details of a single change request by its sys_id or number.
    Provide either 'sys_id' or 'number', but not both.
    """
    try:
        async with ServiceNowClient(instance_url=params.instance_url, username=params.username, password=params.password) as client:
            if not params.sys_id and not params.number:
                return {"error": "Missing identifier", "message": "You must provide either a 'sys_id' or a 'number'."}
            if params.sys_id and params.number:
                return {"error": "Ambiguous identifier", "message": "Please provide either 'sys_id' or 'number', not both."}

            if params.sys_id:
                endpoint = f"/api/now/table/change_request/{params.sys_id}"
                return await client.send_request("GET", endpoint)

            if params.number:
                query_params = {"sysparm_query": f"number={params.number}", "sysparm_limit": 1}
                response = await client.send_request("GET", "/api/now/table/change_request", params=query_params)

                if response and response.get('result'):
                    return {"result": response['result'][0]}
                else:
                    return {"error": "Not Found", "message": f"Change request with number '{params.number}' was not found."}
    except ServiceNowError as e:
        return {"error": type(e).__name__, "message": e.message, "details": e.details}

async def add_change_task(params: AddChangeTaskParams) -> Dict[str, Any]:
    """
    Adds a new task to an existing change request.
    """
    try:
        # THE FIX: Indent the following lines to be inside the function.
        async with ServiceNowClient(instance_url=params.instance_url, username=params.username, password=params.password) as client:
            payload = {
                "change_request": params.change_request_sys_id,
                "short_description": params.short_description
            }
            # Change tasks are stored in the 'change_task' table.
            return await client.send_request("POST", "/api/now/table/change_task", data=payload)
    except ServiceNowError as e:
        return {"error": type(e).__name__, "message": e.message, "details": e.details}

async def submit_change_for_approval(params: SubmitChangeForApprovalParams) -> Dict[str, Any]:
    """
    Submits a change request for approval by setting its state to 'Assess'.
    This typically triggers the approval workflow in ServiceNow.
    """
    try:
        # THE FIX: Indent the following lines.
        async with ServiceNowClient(instance_url=params.instance_url, username=params.username, password=params.password) as client:
            # The 'state' for 'Assess' in a Normal change is typically -4.
            # This action moves the change from 'New' to the next step in the workflow.
            update_data = {"state": ChangeState.ASSESS}
            endpoint = f"/api/now/table/change_request/{params.sys_id}"
            return await client.send_request("PATCH", endpoint, data=update_data)
    except ServiceNowError as e:
        return {"error": type(e).__name__, "message": e.message, "details": e.details}

async def approve_change(params: ApproveChangeParams) -> Dict[str, Any]:
    """
    Approves a change request. This finds the current user's approval record
    for the change and sets its state to 'approved'.
    """
    try:
        # THE FIX: Indent the following lines.
        async with ServiceNowClient(instance_url=params.instance_url, username=params.username, password=params.password) as client:
            # Step 1: Find the approval record for the current user and the specified change.
            query = f"sysapproval={params.sys_id}^state=requested"
            query_params = {"sysparm_query": query, "sysparm_limit": 1}

            approval_response = await client.send_request("GET", "/api/now/table/sysapproval_approver", params=query_params)

            if not approval_response.get('result'):
                return {"error": "Approval Not Found", "message": "Could not find a pending approval record for this change. It may not be in the correct state or you may not be an approver."}

            approval_record_sys_id = approval_response['result'][0]['sys_id']

            # Step 2: Update that approval record to 'approved'.
            update_data = {
                "state": "approved",
                "comments": params.approval_notes
            }
            endpoint = f"/api/now/table/sysapproval_approver/{approval_record_sys_id}"
            return await client.send_request("PATCH", endpoint, data=update_data)
    except ServiceNowError as e:
        return {"error": type(e).__name__, "message": e.message, "details": e.details}

async def reject_change(params: RejectChangeParams) -> Dict[str, Any]:
    """
    Rejects a change request. This finds the current user's approval record
    for the change and sets its state to 'rejected'.

    """
    try:
        async with ServiceNowClient(instance_url=params.instance_url, username=params.username, password=params.password) as client:
            # Step 1: Find the pending approval record for the specified change.
            query = f"sysapproval={params.sys_id}^state=requested"
            query_params = {"sysparm_query": query, "sysparm_limit": 1}

            approval_response = await client.send_request("GET", "/api/now/table/sysapproval_approver", params=query_params)

            if not approval_response.get('result'):
                return {"error": "Approval Not Found", "message": "Could not find a pending approval record for this change to reject."}

            approval_record_sys_id = approval_response['result'][0]['sys_id']

            # Step 2: Update that approval record's state to 'rejected'.
            update_data = {
                "state": "rejected",
                "comments": params.rejection_comments
            }
            endpoint = f"/api/now/table/sysapproval_approver/{approval_record_sys_id}"
            return await client.send_request("PATCH", endpoint, data=update_data)
    except ServiceNowError as e:
        return {"error": type(e).__name__, "message": e.message, "details": e.details}

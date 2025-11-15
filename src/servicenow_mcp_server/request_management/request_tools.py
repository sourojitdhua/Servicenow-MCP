# src/servicenow_mcp_server/request_management/request_tools.py

"""
This module defines tools for managing generic Service Requests (sc_request table),
including their associated Requested Items (RITMs) and attachments.
"""

import base64
from typing import Dict, Any, Optional, List
from pydantic import Field
from fastmcp import FastMCP
from servicenow_mcp_server.utils import ServiceNowClient
from servicenow_mcp_server.models import BaseToolParams
from servicenow_mcp_server.exceptions import ServiceNowError

def register_tools(main_mcp: FastMCP):
    """Adds all tools defined in this file to the main server's MCP instance."""
    main_mcp.add_tool(create_request_ticket)
    main_mcp.add_tool(get_request_ticket)
    main_mcp.add_tool(list_request_tickets)
    main_mcp.add_tool(add_comment_to_request)
    main_mcp.add_tool(attach_file_to_record) # This one is generic and stays the same

# ==============================================================================
#  Pydantic Models
# ==============================================================================

class CreateRequestTicketParams(BaseToolParams):
    short_description: str = Field(..., description="A brief, one-line summary of the request.")
    description: Optional[str] = Field(None, description="A detailed description of the request.")
    requested_for: Optional[str] = Field(None, description="The sys_id of the user this request is for. Defaults to the API user if not provided.")

class GetRequestTicketParams(BaseToolParams):
    sys_id: Optional[str] = Field(None, description="The sys_id of the Request (REQ).")
    number: Optional[str] = Field(None, description="The number of the Request (e.g., 'REQ0010001').")

class ListRequestTicketsParams(BaseToolParams):
    active: bool = Field(True, description="Return only active requests.")
    limit: int = Field(10, description="The maximum number of records to return.")
    offset: int = Field(0, description="The record number to start from for pagination.")

class AddCommentToRequestParams(BaseToolParams):
    sys_id: str = Field(..., description="The sys_id of the Request (REQ) to comment on.")
    comment: str = Field(..., description="The customer-visible comment to add.")

class AttachFileToRecordParams(BaseToolParams):
    table_name: str = Field(..., description="The name of the table the record belongs to (e.g., 'sc_request', 'incident').")
    record_sys_id: str = Field(..., description="The sys_id of the record to attach the file to.")
    file_name: str = Field(..., description="The name of the file (e.g., 'details.pdf').")
    file_content_base64: str = Field(..., description="The content of the file, encoded in Base64.")

# ==============================================================================
#  Tool Functions
# ==============================================================================

async def create_request_ticket(params: CreateRequestTicketParams) -> Dict[str, Any]:
    """
    Creates a new, simple service request ticket (sc_request).
    Note: This creates a generic request, not one from a specific catalog item.
    """
    try:
        async with ServiceNowClient(instance_url=params.instance_url, username=params.username, password=params.password) as client:
            payload = params.model_dump(
                exclude={"instance_url", "username", "password"},
                exclude_unset=True
            )
            return await client.send_request("POST", "/api/now/table/sc_request", data=payload)
    except ServiceNowError as e:
        return {"error": type(e).__name__, "message": e.message, "details": e.details}

async def get_request_ticket(params: GetRequestTicketParams) -> Dict[str, Any]:
    """
    Retrieves the details of a specific request ticket (REQ) by its sys_id or number.
    """
    try:
        async with ServiceNowClient(instance_url=params.instance_url, username=params.username, password=params.password) as client:
            if not params.sys_id and not params.number:
                return {"error": "Missing identifier", "message": "Provide either 'sys_id' or 'number'."}

            query = f"sys_id={params.sys_id}" if params.sys_id else f"number={params.number}"
            query_params = {"sysparm_query": query, "sysparm_limit": 1}
            response = await client.send_request("GET", "/api/now/table/sc_request", params=query_params)

            if response and response.get('result'):
                return {"result": response['result'][0]}
            else:
                return {"error": "Not Found", "message": "Request ticket not found."}
    except ServiceNowError as e:
        return {"error": type(e).__name__, "message": e.message, "details": e.details}

async def list_request_tickets(params: ListRequestTicketsParams) -> Dict[str, Any]:
    """Lists request tickets (sc_request) with optional filters."""
    try:
        async with ServiceNowClient(instance_url=params.instance_url, username=params.username, password=params.password) as client:
            query_params = {
                "sysparm_query": f"active={str(params.active).lower()}",
                "sysparm_limit": params.limit,
                "sysparm_offset": params.offset
            }
            return await client.send_request("GET", "/api/now/table/sc_request", params=query_params)
    except ServiceNowError as e:
        return {"error": type(e).__name__, "message": e.message, "details": e.details}

async def add_comment_to_request(params: AddCommentToRequestParams) -> Dict[str, Any]:
    """Adds a customer-visible comment to a request ticket (REQ)."""
    try:
        async with ServiceNowClient(instance_url=params.instance_url, username=params.username, password=params.password) as client:
            payload = {"comments": params.comment}
            endpoint = f"/api/now/table/sc_request/{params.sys_id}"
            return await client.send_request("PATCH", endpoint, data=payload)
    except ServiceNowError as e:
        return {"error": type(e).__name__, "message": e.message, "details": e.details}

async def attach_file_to_record(params: AttachFileToRecordParams) -> Dict[str, Any]:
    """Attaches a file to any record in ServiceNow. The file content must be Base64 encoded."""
    try:
        async with ServiceNowClient(instance_url=params.instance_url, username=params.username, password=params.password) as client:
            endpoint = "/api/now/attachment/file"
            query_params = { "table_name": params.table_name, "table_sys_id": params.record_sys_id, "file_name": params.file_name }
            try:
                file_bytes = base64.b64decode(params.file_content_base64)
            except Exception as e:
                return {"error": "Base64 Decode Error", "details": str(e)}

            return await client.send_raw_request("POST", endpoint, params=query_params, data=file_bytes, headers={"Content-Type": "application/octet-stream"})
    except ServiceNowError as e:
        return {"error": type(e).__name__, "message": e.message, "details": e.details}

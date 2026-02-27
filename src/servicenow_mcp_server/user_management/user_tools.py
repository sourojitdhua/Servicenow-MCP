# src/servicenow_mcp_server/user_management/user_tools.py

"""
This module defines tools for managing users and groups in ServiceNow.
"""

import secrets
from typing import Dict, Any, Optional
from pydantic import Field
from fastmcp import FastMCP, Context
from servicenow_mcp_server.models import BaseToolParams, get_client
from servicenow_mcp_server.tool_annotations import READ, WRITE, DELETE
from servicenow_mcp_server.tool_utils import snow_tool

def register_tools(mcp: FastMCP):
    """Adds all tools defined in this file to the main server's MCP instance."""
    _tags = {"user"}

    mcp.tool(create_user, tags=_tags | {"write"}, annotations=WRITE)
    mcp.tool(update_user, tags=_tags | {"write"}, annotations=WRITE)
    mcp.tool(get_user, tags=_tags | {"read"}, annotations=READ)
    mcp.tool(list_users, tags=_tags | {"read"}, annotations=READ)
    mcp.tool(create_group, tags=_tags | {"write"}, annotations=WRITE)
    mcp.tool(update_group, tags=_tags | {"write"}, annotations=WRITE)
    mcp.tool(add_group_members, tags=_tags | {"write"}, annotations=WRITE)
    mcp.tool(remove_group_members, tags=_tags | {"delete"}, annotations=DELETE)
    mcp.tool(list_groups, tags=_tags | {"read"}, annotations=READ)


# ==============================================================================
#  Pydantic Models
# ==============================================================================

class CreateUserParams(BaseToolParams):
    first_name: str = Field(..., description="The user's first name.")
    last_name: str = Field(..., description="The user's last name.")
    user_name: str = Field(..., description="The user's login ID (user_name).")
    email: str = Field(..., description="The user's email address.")
    password_needs_reset: bool = Field(True, description="If true, the user must reset their password on first login.")
    active: bool = Field(True, description="Set to false to disable the user account.")
    department: Optional[str] = Field(None, description="The sys_id of the user's department.")
    title: Optional[str] = Field(None, description="The user's job title.")
    user_password: Optional[str] = Field(None, description="The password for the new user account. If not provided, a secure random password is generated.")

class UpdateUserParams(BaseToolParams):
    sys_id: str = Field(..., description="The sys_id of the user to update.")
    first_name: Optional[str] = Field(None, description="First name.")
    last_name: Optional[str] = Field(None, description="Last name.")
    email: Optional[str] = Field(None, description="Email address.")
    active: Optional[bool] = Field(None, description="Enable or disable the account.")
    department: Optional[str] = Field(None, description="Department sys_id.")
    title: Optional[str] = Field(None, description="Job title.")

class GetUserParams(BaseToolParams):
    user_id: Optional[str] = Field(None, description="sys_id of the user.")
    user_name: Optional[str] = Field(None, description="Login ID (user_name).")
    email: Optional[str] = Field(None, description="Email address.")

class ListUsersParams(BaseToolParams):
    active_only: bool = Field(True, description="Return only active users.")
    department: Optional[str] = Field(None, description="Filter by department sys_id.")
    name: Optional[str] = Field(None, description="Filter by a search term in the user's name.")
    email: Optional[str] = Field(None, description="Filter by a search term in the user's email.")
    limit: int = Field(20, description="Maximum number of users to return.")
    offset: int = Field(0, description="Records to skip for pagination.")

class CreateGroupParams(BaseToolParams):
    name: str = Field(..., description="The name of the new group.")
    description: Optional[str] = Field(None, description="Group description.")
    active: bool = Field(True, description="Whether the group is active.")

class UpdateGroupParams(BaseToolParams):
    sys_id: str = Field(..., description="The sys_id of the group to update.")
    name: Optional[str] = Field(None, description="New group name.")
    description: Optional[str] = Field(None, description="New description.")
    active: Optional[bool] = Field(None, description="Enable or disable the group.")

class AddGroupMembersParams(BaseToolParams):
    group_sys_id: str = Field(..., description="The sys_id of the group.")
    user_sys_ids: list[str] = Field(..., description="List of user sys_ids to add.")

class RemoveGroupMembersParams(BaseToolParams):
    group_sys_id: str = Field(..., description="The sys_id of the group.")
    user_sys_ids: list[str] = Field(..., description="List of user sys_ids to remove.")

class ListGroupsParams(BaseToolParams):
    active_only: bool = Field(False, description="Return only active groups.")
    limit: int = Field(20, description="Maximum number of groups to return.")
    offset: int = Field(0, description="Records to skip for pagination.")

# ==============================================================================
#  Tool Functions
# ==============================================================================

@snow_tool
async def create_user(params: CreateUserParams) -> Dict[str, Any]:
    """
    Creates a new user record.
    """
    async with get_client() as client:
        payload = params.model_dump(
            exclude=set(),
            exclude_unset=True
        )

        payload.setdefault("user_password", secrets.token_urlsafe(16))

        return await client.send_request("POST", "/api/now/table/sys_user", data=payload)


@snow_tool
async def update_user(params: UpdateUserParams) -> Dict[str, Any]:
    """Update an existing user record."""
    async with get_client() as client:
        payload = params.model_dump(
            exclude={"sys_id"},
            exclude_unset=True
        )
        return await client.send_request(
            "PATCH",
            f"/api/now/table/sys_user/{params.sys_id}",
            data=payload
        )

@snow_tool
async def get_user(params: GetUserParams) -> Dict[str, Any]:
    """Retrieve a single user by sys_id, user_name, or email."""
    async with get_client() as client:
        if params.user_id:
            query = f"sys_id={params.user_id}"
        elif params.user_name:
            query = f"user_name={params.user_name}"
        elif params.email:
            query = f"email={params.email}"
        else:
            return {"error": "ValidationError", "message": "One of user_id, user_name, or email must be provided.", "details": None}

        qp = {"sysparm_query": query, "sysparm_limit": 1}
        return await client.send_request("GET", "/api/now/table/sys_user", params=qp)

@snow_tool
async def list_users(params: ListUsersParams) -> Dict[str, Any]:
    """List users with optional filters."""
    async with get_client() as client:
        query_parts = []
        if params.active_only:
            query_parts.append("active=true")
        if params.department:
            query_parts.append(f"department={params.department}")
        if params.name:
            query_parts.append(f"nameLIKE{params.name}")
        if params.email:
            query_parts.append(f"emailLIKE{params.email}")

        query = "^".join(query_parts)
        qp = {"sysparm_limit": params.limit, "sysparm_offset": params.offset}
        if query:
            qp["sysparm_query"] = query

        return await client.send_request("GET", "/api/now/table/sys_user", params=qp)

@snow_tool
async def create_group(params: CreateGroupParams) -> Dict[str, Any]:
    """Create a new group."""
    async with get_client() as client:
        payload = params.model_dump(
            exclude=set(),
            exclude_unset=True
        )
        return await client.send_request(
            "POST",
            "/api/now/table/sys_user_group",
            data=payload
        )

@snow_tool
async def update_group(params: UpdateGroupParams) -> Dict[str, Any]:
    """Update an existing group."""
    async with get_client() as client:
        payload = params.model_dump(
            exclude={"sys_id"},
            exclude_unset=True
        )
        return await client.send_request(
            "PATCH",
            f"/api/now/table/sys_user_group/{params.sys_id}",
            data=payload
        )

async def add_group_members(params: AddGroupMembersParams, ctx: Context) -> Dict[str, Any]:
    """Add multiple users to a group."""
    from servicenow_mcp_server.exceptions import ServiceNowError

    async with get_client() as client:
        successes = []
        failures = []
        total = len(params.user_sys_ids)
        for i, uid in enumerate(params.user_sys_ids):
            try:
                payload = {"group": params.group_sys_id, "user": uid}
                r = await client.send_request(
                    "POST",
                    "/api/now/table/sys_user_grmember",
                    data=payload
                )
                successes.append(r)
            except ServiceNowError as e:
                failures.append({"user": uid, "error": e.message})
            await ctx.report_progress(i + 1, total, f"Added {i + 1}/{total} members")
        return {"added": successes, "failed": failures}

async def remove_group_members(params: RemoveGroupMembersParams, ctx: Context) -> Dict[str, Any]:
    """Remove multiple users from a group."""
    from servicenow_mcp_server.exceptions import ServiceNowError

    async with get_client() as client:
        query_parts = [f"group={params.group_sys_id}"]
        ids_filter = "^OR".join([f"user={uid}" for uid in params.user_sys_ids])
        query_parts.append(ids_filter)
        query = "^".join(query_parts)

        await ctx.info("Searching for group membership records...")

        # Retrieve membership sys_ids
        qp = {"sysparm_query": query, "sysparm_fields": "sys_id"}
        memberships = await client.send_request("GET", "/api/now/table/sys_user_grmember", params=qp)

        # Delete each membership record
        deleted = []
        failures = []
        records = memberships.get("result", [])
        total = len(records)
        for i, m in enumerate(records):
            try:
                r = await client.send_request(
                    "DELETE",
                    f"/api/now/table/sys_user_grmember/{m['sys_id']}"
                )
                deleted.append(r)
            except ServiceNowError as e:
                failures.append({"sys_id": m["sys_id"], "error": e.message})
            await ctx.report_progress(i + 1, total, f"Removed {i + 1}/{total} members")
        return {"removed": deleted, "failed": failures}

@snow_tool
async def list_groups(params: ListGroupsParams) -> Dict[str, Any]:
    """List groups with optional filters."""
    async with get_client() as client:
        query_parts = []
        if params.active_only:
            query_parts.append("active=true")

        query = "^".join(query_parts)
        qp = {"sysparm_limit": params.limit, "sysparm_offset": params.offset}
        if query:
            qp["sysparm_query"] = query

        return await client.send_request("GET", "/api/now/table/sys_user_group", params=qp)

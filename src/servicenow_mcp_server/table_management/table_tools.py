# src/servicenow_mcp_server/table_management/table_tools.py

"""
This module defines generic tools for interacting with any ServiceNow table.
"""

from typing import Dict, Any, List, Optional
from pydantic import Field
from fastmcp import FastMCP, Context

from servicenow_mcp_server.models import BaseToolParams, get_client
from servicenow_mcp_server.tool_annotations import READ, WRITE, DELETE
from servicenow_mcp_server.tool_utils import snow_tool


def register_tools(mcp: FastMCP):
    """Adds all tools defined in this file to the main server's MCP instance."""
    _tags = {"table"}

    mcp.tool(list_available_tables, tags=_tags | {"read"}, annotations=READ)
    mcp.tool(get_records_from_table, tags=_tags | {"read"}, annotations=READ)
    mcp.tool(get_table_schema, tags=_tags | {"read"}, annotations=READ)
    mcp.tool(search_records_by_text, tags=_tags | {"read"}, annotations=READ)
    mcp.tool(create_record, tags=_tags | {"write"}, annotations=WRITE)
    mcp.tool(update_record, tags=_tags | {"write"}, annotations=WRITE)
    mcp.tool(delete_record, tags=_tags | {"delete"}, annotations=DELETE)
    mcp.tool(batch_update_records, tags=_tags | {"write"}, annotations=WRITE)


# ==============================================================================
#  Pydantic Models
# ==============================================================================

class ListTablesParams(BaseToolParams):
    filter: Optional[str] = Field(None, description="A search term to filter table names (e.g., 'incident', 'cmdb_ci').")


class GetTableSchemaParams(BaseToolParams):
    table_name: str = Field(..., description="The name of the table to get the schema for (e.g., 'incident').")

class GetRecordsParams(BaseToolParams):
    table_name: str = Field(..., description="The name of the table to query (e.g., 'incident', 'cmdb_ci').")
    query: Optional[str] = Field(None, description="ServiceNow-encoded query string (e.g., 'active=true^priority=1').")
    limit: int = Field(10, description="The maximum number of records to return.")
    offset: int = Field(0, description="The record number to start from for pagination.")
    sort_by: Optional[str] = Field(None, description="Field to sort by (e.g., 'sys_created_on').")
    sort_dir: str = Field("DESC", description="Sort direction. 'ASC' for ascending, 'DESC' for descending.")
    fields: Optional[List[str]] = Field(None, description="Specific fields to return to limit the payload size (e.g., ['number', 'short_description']).")

class SearchRecordsParams(BaseToolParams):
    table_name: str = Field(..., description="The name of the table to search within (e.g., 'incident').")
    search_term: str = Field(..., description="The text or keyword to search for across all indexed fields.")
    limit: int = Field(10, description="The maximum number of matching records to return.")

class CreateRecordParams(BaseToolParams):
    table_name: str = Field(..., description="The name of the table to create a record in (e.g., 'incident').")
    data: Dict[str, Any] = Field(..., description="A dictionary of field names and values for the new record.")

class UpdateRecordParams(BaseToolParams):
    table_name: str = Field(..., description="The name of the table containing the record.")
    sys_id: str = Field(..., description="The sys_id of the record to update.")
    data: Dict[str, Any] = Field(..., description="A dictionary of field names and values to update.")

class DeleteRecordParams(BaseToolParams):
    table_name: str = Field(..., description="The name of the table containing the record.")
    sys_id: str = Field(..., description="The sys_id of the record to delete.")

class BatchUpdateRecordsParams(BaseToolParams):
    table_name: str = Field(..., description="The name of the table containing the records.")
    sys_ids: List[str] = Field(..., description="A list of sys_ids of the records to update.")
    data: Dict[str, Any] = Field(..., description="A dictionary of field names and values to apply to all records.")


# ==============================================================================
#  Tool Functions
# ==============================================================================

@snow_tool
async def list_available_tables(params: ListTablesParams) -> Dict[str, Any]:
    """
    Lists tables in the instance by querying the system's metadata table (sys_db_object).
    """
    async with get_client() as client:
        fields_to_get = "name,label,super_class"

        query_parts = ["is_extendable=true", "labelISNOTEMPTY"]

        if params.filter:
            filter_term = params.filter
            query_parts.append(f"nameLIKE{filter_term}^ORlabelLIKE{filter_term}")

        final_query = "^".join(query_parts)

        query_params = {
            "sysparm_fields": fields_to_get,
            "sysparm_query": final_query,
            "sysparm_limit": 200
        }

        return await client.send_request("GET", "/api/now/table/sys_db_object", params=query_params)


@snow_tool
async def get_records_from_table(params: GetRecordsParams) -> Dict[str, Any]:
    """
    Retrieves records from any specified table with advanced filtering, sorting, and pagination.
    """
    async with get_client() as client:
        query_params = {
            "sysparm_limit": params.limit,
            "sysparm_offset": params.offset
        }

        if params.query:
            query_params["sysparm_query"] = params.query

        if params.fields:
            query_params["sysparm_fields"] = ",".join(params.fields)

        if params.sort_by:
            # ServiceNow syntax: ORDERBY<field> for ASC, ORDERBYDESC<field> for DESC
            sort_prefix = "ORDERBYDESC" if params.sort_dir.upper() == "DESC" else "ORDERBY"
            existing_query = query_params.get("sysparm_query", "")
            if existing_query:
                query_params["sysparm_query"] = f"{existing_query}^{sort_prefix}{params.sort_by}"
            else:
                query_params["sysparm_query"] = f"{sort_prefix}{params.sort_by}"

        endpoint = f"/api/now/table/{params.table_name}"

        return await client.send_request("GET", endpoint, params=query_params)


@snow_tool
async def get_table_schema(params: GetTableSchemaParams) -> Dict[str, Any]:
    """
    Retrieves the schema (column names, types, etc.) for a specific table
    by querying the system's data dictionary (sys_dictionary).
    """
    async with get_client() as client:
        schema_query_params = {
            "sysparm_query": f"name={params.table_name}^internal_typeISNOTEMPTY",
            "sysparm_fields": "element,internal_type,max_length,mandatory,display,reference"
        }

        return await client.send_request("GET", "/api/now/table/sys_dictionary", params=schema_query_params)


@snow_tool
async def search_records_by_text(params: SearchRecordsParams) -> Dict[str, Any]:
    """
    Searches for a term in the common text fields of a table using a LIKE query.
    This provides a reliable, real-time search without relying on text indexing.
    Common fields searched: 'short_description', 'description', 'number', 'comments', 'work_notes'.
    """
    async with get_client() as client:
        term = params.search_term

        query_parts = [
            f"short_descriptionLIKE{term}",
            f"descriptionLIKE{term}",
            f"numberLIKE{term}",
            f"commentsLIKE{term}",
            f"work_notesLIKE{term}"
        ]
        query = "^OR".join(query_parts)

        query_params = {
            "sysparm_query": query,
            "sysparm_limit": params.limit
        }

        endpoint = f"/api/now/table/{params.table_name}"

        return await client.send_request("GET", endpoint, params=query_params)


# ==============================================================================
#  New Generic CRUD Tools
# ==============================================================================

@snow_tool
async def create_record(params: CreateRecordParams) -> Dict[str, Any]:
    """
    Creates a new record in any specified ServiceNow table with arbitrary field data.
    """
    async with get_client() as client:
        endpoint = f"/api/now/table/{params.table_name}"
        return await client.send_request("POST", endpoint, data=params.data)


@snow_tool
async def update_record(params: UpdateRecordParams) -> Dict[str, Any]:
    """
    Updates an existing record in any specified ServiceNow table.
    """
    async with get_client() as client:
        endpoint = f"/api/now/table/{params.table_name}/{params.sys_id}"
        return await client.send_request("PATCH", endpoint, data=params.data)


@snow_tool
async def delete_record(params: DeleteRecordParams) -> Dict[str, Any]:
    """
    Deletes a record from any specified ServiceNow table.
    """
    async with get_client() as client:
        endpoint = f"/api/now/table/{params.table_name}/{params.sys_id}"
        return await client.send_request("DELETE", endpoint)


async def batch_update_records(params: BatchUpdateRecordsParams, ctx: Context) -> Dict[str, Any]:
    """
    Updates multiple records in a table with the same data.
    Returns a summary of successes and failures.
    """
    from servicenow_mcp_server.exceptions import ServiceNowError

    async with get_client() as client:
        successes = []
        failures = []
        total = len(params.sys_ids)

        for i, sys_id in enumerate(params.sys_ids):
            try:
                endpoint = f"/api/now/table/{params.table_name}/{sys_id}"
                await client.send_request("PATCH", endpoint, data=params.data)
                successes.append(sys_id)
            except ServiceNowError as e:
                failures.append({
                    "sys_id": sys_id,
                    "error": type(e).__name__,
                    "message": e.message,
                })
            await ctx.report_progress(i + 1, total, f"Updated {i + 1}/{total} records")

        return {
            "status": "Completed",
            "updated_count": len(successes),
            "failed_count": len(failures),
            "successful_updates": successes,
            "failed_updates": failures,
        }

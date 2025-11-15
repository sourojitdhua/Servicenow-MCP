# src/servicenow_mcp_server/table_management/table_tools.py

"""
This module defines generic tools for interacting with any ServiceNow table.
"""

from typing import Dict, Any, List, Optional
from pydantic import Field
from fastmcp import FastMCP

from servicenow_mcp_server.models import BaseToolParams
from servicenow_mcp_server.utils import ServiceNowClient
from servicenow_mcp_server.exceptions import ServiceNowError


def register_tools(mcp: FastMCP):
    """Adds all tools defined in this file to the main server's MCP instance."""
    mcp.add_tool(list_available_tables)
    mcp.add_tool(get_records_from_table)
    mcp.add_tool(get_table_schema)
    mcp.add_tool(search_records_by_text)
    mcp.add_tool(create_record)
    mcp.add_tool(update_record)
    mcp.add_tool(delete_record)
    mcp.add_tool(batch_update_records)


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

async def list_available_tables(params: ListTablesParams) -> Dict[str, Any]:
    """
    Lists tables in the instance by querying the system's metadata table (sys_db_object).
    """
    try:
        async with ServiceNowClient(instance_url=params.instance_url, username=params.username, password=params.password) as client:
            # Define the specific fields we want to make the response efficient.
            fields_to_get = "name,label,super_class"

            # Build a robust query.
            # We start by filtering for tables that are extendable and have a label,
            # which removes a lot of internal system noise.
            query_parts = ["is_extendable=true", "labelISNOTEMPTY"]

            # If the user provides a filter, add it to the query.
            # This will search in both the table 'name' (e.g., cmdb_ci) and its 'label' (e.g., Configuration Item).
            if params.filter:
                filter_term = params.filter
                query_parts.append(f"nameLIKE{filter_term}^ORlabelLIKE{filter_term}")

            # Join the query parts with '^' which is ServiceNow's 'AND' operator.
            final_query = "^".join(query_parts)

            query_params = {
                "sysparm_fields": fields_to_get,
                "sysparm_query": final_query,
                "sysparm_limit": 200  # Limit the results to avoid overly large responses
            }

            # We now query the standard 'sys_db_object' table which is guaranteed to exist.
            return await client.send_request("GET", "/api/now/table/sys_db_object", params=query_params)
    except ServiceNowError as e:
        return {"error": type(e).__name__, "message": e.message, "details": e.details}


async def get_records_from_table(params: GetRecordsParams) -> Dict[str, Any]:
    """
    Retrieves records from any specified table with advanced filtering, sorting, and pagination.
    """
    try:
        async with ServiceNowClient(instance_url=params.instance_url, username=params.username, password=params.password) as client:
            # Start building the dictionary of query parameters
            query_params = {
                "sysparm_limit": params.limit,
                "sysparm_offset": params.offset
            }

            # Add optional parameters if they were provided
            if params.query:
                query_params["sysparm_query"] = params.query

            if params.fields:
                query_params["sysparm_fields"] = ",".join(params.fields)

            if params.sort_by:
                # For sorting, the field name and direction are combined in the query
                sort_direction = "DESC" if params.sort_dir.upper() == "DESC" else "ASC"
                # If a query already exists, append the ORDERBY. Otherwise, create it.
                existing_query = query_params.get("sysparm_query", "")
                if existing_query:
                    query_params["sysparm_query"] = f"{existing_query}^ORDERBY{sort_direction}{params.sort_by}"
                else:
                    query_params["sysparm_query"] = f"ORDERBY{sort_direction}{params.sort_by}"

            # The table name is part of the URL path, not the query parameters
            endpoint = f"/api/now/table/{params.table_name}"

            return await client.send_request("GET", endpoint, params=query_params)
    except ServiceNowError as e:
        return {"error": type(e).__name__, "message": e.message, "details": e.details}


async def get_table_schema(params: GetTableSchemaParams) -> Dict[str, Any]:
    """
    Retrieves the schema (column names, types, etc.) for a specific table
    by querying the system's data dictionary (sys_dictionary).
    """
    try:
        async with ServiceNowClient(instance_url=params.instance_url, username=params.username, password=params.password) as client:

            # This is the correct, robust way to get a table's schema.
            schema_query_params = {
                # Query for dictionary entries where the table name matches
                # and it has an internal type (to filter out non-column entries).
                "sysparm_query": f"name={params.table_name}^internal_typeISNOTEMPTY",

                # Request the specific schema-related fields we care about.
                "sysparm_fields": "element,internal_type,max_length,mandatory,display,reference"
            }

            # Make a standard API call to the 'sys_dictionary' table.
            # This uses the existing, working 'send_request' method.
            return await client.send_request("GET", "/api/now/table/sys_dictionary", params=schema_query_params)
    except ServiceNowError as e:
        return {"error": type(e).__name__, "message": e.message, "details": e.details}



async def search_records_by_text(params: SearchRecordsParams) -> Dict[str, Any]:
    """
    Searches for a term in the common text fields of a table using a LIKE query.
    This provides a reliable, real-time search without relying on text indexing.
    Common fields searched: 'short_description', 'description', 'number', 'comments', 'work_notes'.
    """
    try:
        async with ServiceNowClient(instance_url=params.instance_url, username=params.username, password=params.password) as client:
            term = params.search_term

            # This is a more direct and reliable query method than text indexing.
            # It checks if the search term is contained within several common fields.
            # The '^OR' acts as an "OR" between each condition.
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
    except ServiceNowError as e:
        return {"error": type(e).__name__, "message": e.message, "details": e.details}


# ==============================================================================
#  New Generic CRUD Tools
# ==============================================================================

async def create_record(params: CreateRecordParams) -> Dict[str, Any]:
    """
    Creates a new record in any specified ServiceNow table with arbitrary field data.
    """
    try:
        async with ServiceNowClient(
            instance_url=params.instance_url,
            username=params.username,
            password=params.password,
        ) as client:
            endpoint = f"/api/now/table/{params.table_name}"
            return await client.send_request("POST", endpoint, data=params.data)
    except ServiceNowError as e:
        return {"error": type(e).__name__, "message": e.message, "details": e.details}


async def update_record(params: UpdateRecordParams) -> Dict[str, Any]:
    """
    Updates an existing record in any specified ServiceNow table.
    """
    try:
        async with ServiceNowClient(
            instance_url=params.instance_url,
            username=params.username,
            password=params.password,
        ) as client:
            endpoint = f"/api/now/table/{params.table_name}/{params.sys_id}"
            return await client.send_request("PATCH", endpoint, data=params.data)
    except ServiceNowError as e:
        return {"error": type(e).__name__, "message": e.message, "details": e.details}


async def delete_record(params: DeleteRecordParams) -> Dict[str, Any]:
    """
    Deletes a record from any specified ServiceNow table.
    """
    try:
        async with ServiceNowClient(
            instance_url=params.instance_url,
            username=params.username,
            password=params.password,
        ) as client:
            endpoint = f"/api/now/table/{params.table_name}/{params.sys_id}"
            return await client.send_request("DELETE", endpoint)
    except ServiceNowError as e:
        return {"error": type(e).__name__, "message": e.message, "details": e.details}


async def batch_update_records(params: BatchUpdateRecordsParams) -> Dict[str, Any]:
    """
    Updates multiple records in a table with the same data.
    Returns a summary of successes and failures.
    """
    try:
        async with ServiceNowClient(
            instance_url=params.instance_url,
            username=params.username,
            password=params.password,
        ) as client:
            successes = []
            failures = []

            for sys_id in params.sys_ids:
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

            return {
                "status": "Completed",
                "updated_count": len(successes),
                "failed_count": len(failures),
                "successful_updates": successes,
                "failed_updates": failures,
            }
    except ServiceNowError as e:
        return {"error": type(e).__name__, "message": e.message, "details": e.details}

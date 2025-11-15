# src/servicenow_mcp_server/service_catalog/catalog_tools.py

"""
This module defines tools for interacting with the ServiceNow Service Catalog.
"""

from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from fastmcp import FastMCP
from servicenow_mcp_server.utils import ServiceNowClient
from servicenow_mcp_server.models import BaseToolParams
from servicenow_mcp_server.exceptions import ServiceNowError


def register_tools(mcp: FastMCP):
    """Adds all tools defined in this file to the main server's MCP instance."""
    mcp.add_tool(create_catalog)
    mcp.add_tool(list_catalog_items)
    mcp.add_tool(get_catalog_item)
    mcp.add_tool(list_catalog_categories)
    mcp.add_tool(create_catalog_category)
    mcp.add_tool(update_catalog_category)
    mcp.add_tool(move_catalog_items)
    mcp.add_tool(create_catalog_item_variable)
    mcp.add_tool(list_catalog_item_variables)
    mcp.add_tool(update_catalog_item_variable)
    mcp.add_tool(list_catalogs)


# ==============================================================================
#  Pydantic Models
# ==============================================================================

class ListCatalogItemsParams(BaseToolParams):
    limit: int = Field(20, description="The maximum number of items to return.")
    filter_text: Optional[str] = Field(None, description="A search term to filter items by name or description.")

# Add this class to catalog_tools.py
class GetCatalogItemParams(BaseToolParams):
    sys_id: str = Field(..., description="The unique sys_id of the service catalog item to retrieve.")

# Add this class to catalog_tools.py
class ListCatalogCategoriesParams(BaseToolParams):
    limit: int = Field(20, description="The maximum number of categories to return.")
    filter_text: Optional[str] = Field(None, description="A search term to filter categories by title or description.")
    catalog_sys_id: Optional[str] = Field(None, description="The sys_id of a specific catalog to limit the search to.")


class CreateCatalogCategoryParams(BaseToolParams):
    title: str = Field(..., description="The title for the new category.")
    catalog_sys_id: str = Field(..., description="The sys_id of the parent catalog this category will belong to.")
    description: Optional[str] = Field(None, description="An optional description for the new category.")

# Add this class to catalog_tools.py
class UpdateCatalogCategoryParams(BaseToolParams):
    sys_id: str = Field(..., description="The sys_id of the category to update.")
    title: Optional[str] = Field(None, description="The new title for the category.")
    description: Optional[str] = Field(None, description="The new description for the category.")


class MoveCatalogItemsParams(BaseToolParams):
    destination_category_sys_id: str = Field(..., description="The sys_id of the category to move the items INTO.")
    item_sys_ids: List[str] = Field(..., description="A list of sys_ids for the catalog items to be moved.")


class CreateItemVariableParams(BaseToolParams):
    item_sys_id: str = Field(..., description="The sys_id of the catalog item this variable belongs to.")
    name: str = Field(..., description="The internal system name for the variable (e.g., 'justification').")
    question_text: str = Field(..., description="The user-facing label for the variable's question (e.g., 'Please provide a business justification').")
    type: str = Field(..., description="The variable type. Common types: 1 (Yes/No), 6 (Single Line Text), 8 (Reference), 5 (Select Box).")
    order: int = Field(100, description="The order in which this variable appears on the form (lower numbers appear first).")
    mandatory: bool = Field(False, description="Whether this variable is mandatory.")


class ListItemVariablesParams(BaseToolParams):
    item_sys_id: str = Field(..., description="The sys_id of the catalog item whose variables you want to list.")

class UpdateItemVariableParams(BaseToolParams):
    variable_sys_id: str = Field(..., description="The sys_id of the variable (question) to update.")
    question_text: Optional[str] = Field(None, description="The new user-facing label for the variable.")
    order: Optional[int] = Field(None, description="The new order for the variable on the form.")
    mandatory: Optional[bool] = Field(None, description="The new mandatory status for the variable.")

class ListCatalogsParams(BaseToolParams):
    limit: int = Field(10, description="The maximum number of catalogs to return.")
    filter_text: Optional[str] = Field(None, description="A search term to filter catalogs by title.")

class CreateCatalogParams(BaseToolParams):
    title: str = Field(..., description="The title for the new service catalog.")
    description: Optional[str] = Field(None, description="A description for the new catalog.")
# ==============================================================================
#  Tool Functions
# ==============================================================================


async def create_catalog(params: CreateCatalogParams) -> Dict[str, Any]:
    """
    Creates a new, top-level service catalog.
    """
    try:
        async with ServiceNowClient(instance_url=params.instance_url, username=params.username, password=params.password) as client:
            payload = {
                "title": params.title,
                "description": params.description
            }

            return await client.send_request("POST", "/api/now/table/sc_catalog", data=payload)
    except ServiceNowError as e:
        return {"error": type(e).__name__, "message": e.message, "details": e.details}

async def list_catalog_items(params: ListCatalogItemsParams) -> Dict[str, Any]:
    """
    Lists available items from the Service Catalog.
    These are the end-user facing items that can be requested.
    """
    try:
        async with ServiceNowClient(instance_url=params.instance_url, username=params.username, password=params.password) as client:
            # The table for catalog items is 'sc_cat_item'.

            query_parts = ["active=true"] # Only show active items.

            if params.filter_text:
                # Search in the name, short description, and description fields.
                term = params.filter_text
                query_parts.append(f"nameLIKE{term}^ORshort_descriptionLIKE{term}^ORdescriptionLIKE{term}")

            final_query = "^".join(query_parts)

            query_params = {
                "sysparm_query": final_query,
                "sysparm_limit": params.limit,
                "sysparm_fields": "name,short_description,price,sys_id,category"
            }

            return await client.send_request("GET", "/api/now/table/sc_cat_item", params=query_params)
    except ServiceNowError as e:
        return {"error": type(e).__name__, "message": e.message, "details": e.details}


async def get_catalog_item(params: GetCatalogItemParams) -> Dict[str, Any]:
    """
    Retrieves the full details for a specific service catalog item using its sys_id.
    """
    try:
        async with ServiceNowClient(instance_url=params.instance_url, username=params.username, password=params.password) as client:
            # The endpoint for a specific record is the table name followed by the sys_id.
            endpoint = f"/api/now/table/sc_cat_item/{params.sys_id}"

            return await client.send_request("GET", endpoint)
    except ServiceNowError as e:
        return {"error": type(e).__name__, "message": e.message, "details": e.details}


async def list_catalog_categories(params: ListCatalogCategoriesParams) -> Dict[str, Any]:
    """
    Lists categories within the Service Catalog.
    Categories are used to organize catalog items.
    """
    try:
        async with ServiceNowClient(instance_url=params.instance_url, username=params.username, password=params.password) as client:
            # The table for catalog categories is 'sc_category'.

            query_parts = ["active=true"] # Only show active categories.

            # Add optional filters if they are provided
            if params.catalog_sys_id:
                query_parts.append(f"sc_catalog={params.catalog_sys_id}")

            if params.filter_text:
                # The name field for a category is 'title'.
                term = params.filter_text
                query_parts.append(f"titleLIKE{term}^ORdescriptionLIKE{term}")

            final_query = "^".join(query_parts)

            query_params = {
                "sysparm_query": final_query,
                "sysparm_limit": params.limit,
                "sysparm_fields": "title,description,sys_id,sc_catalog"
            }

            return await client.send_request("GET", "/api/now/table/sc_category", params=query_params)
    except ServiceNowError as e:
        return {"error": type(e).__name__, "message": e.message, "details": e.details}


async def create_catalog_category(params: CreateCatalogCategoryParams) -> Dict[str, Any]:
    """
    Creates a new category within a specified Service Catalog.
    """
    try:
        async with ServiceNowClient(instance_url=params.instance_url, username=params.username, password=params.password) as client:
            # The payload for the new record. 'sc_catalog' is the field for the parent.
            payload = {
                "title": params.title,
                "sc_catalog": params.catalog_sys_id,
                "description": params.description
            }

            # We POST to the 'sc_category' table to create a new record.
            return await client.send_request("POST", "/api/now/table/sc_category", data=payload)
    except ServiceNowError as e:
        return {"error": type(e).__name__, "message": e.message, "details": e.details}

async def update_catalog_category(params: UpdateCatalogCategoryParams) -> Dict[str, Any]:
    """
    Updates an existing service catalog category's title or description.
    """
    try:
        async with ServiceNowClient(instance_url=params.instance_url, username=params.username, password=params.password) as client:
            # Build the update payload with only the fields the user provided.
            update_data = params.model_dump(
                exclude={"sys_id", "instance_url", "username", "password"},
                exclude_unset=True
            )

            if not update_data:
                return {"error": "No update data provided.", "message": "You must provide a 'title' or 'description' to update."}

            endpoint = f"/api/now/table/sc_category/{params.sys_id}"

            return await client.send_request("PATCH", endpoint, data=update_data)
    except ServiceNowError as e:
        return {"error": type(e).__name__, "message": e.message, "details": e.details}

async def move_catalog_items(params: MoveCatalogItemsParams) -> Dict[str, Any]:
    """
    Moves one or more service catalog items to a new category.
    """
    try:
        async with ServiceNowClient(instance_url=params.instance_url, username=params.username, password=params.password) as client:
            successes = []
            failures = []

            # The payload is the same for every item we update.
            update_data = {"category": params.destination_category_sys_id}

            for item_id in params.item_sys_ids:
                endpoint = f"/api/now/table/sc_cat_item/{item_id}"
                response = await client.send_request("PATCH", endpoint, data=update_data)

                if 'error' in response:
                    failures.append({"sys_id": item_id, "error": response.get('error')})
                else:
                    successes.append(item_id)

            # Return a summary of the batch operation.
            return {
                "status": "Completed",
                "moved_count": len(successes),
                "failed_count": len(failures),
                "successful_moves": successes,
                "failed_moves": failures
            }
    except ServiceNowError as e:
        return {"error": type(e).__name__, "message": e.message, "details": e.details}

async def create_catalog_item_variable(params: CreateItemVariableParams) -> Dict[str, Any]:
    """
    Creates a new variable (question/field) on a service catalog item's form.
    """
    try:
        async with ServiceNowClient(instance_url=params.instance_url, username=params.username, password=params.password) as client:
            # The payload for the new record. 'cat_item' is the reference to the parent item.
            payload = {
                "cat_item": params.item_sys_id,
                "name": params.name,
                "question_text": params.question_text,
                "type": params.type,
                "order": str(params.order), # Order is often a string in the API
                "mandatory": str(params.mandatory).lower() # Booleans are strings 'true'/'false'
            }

            # We POST to the 'item_option_new' table.
            return await client.send_request("POST", "/api/now/table/item_option_new", data=payload)
    except ServiceNowError as e:
        return {"error": type(e).__name__, "message": e.message, "details": e.details}

async def list_catalog_item_variables(params: ListItemVariablesParams) -> Dict[str, Any]:
    """
    Lists all the variables (questions/fields) for a specific service catalog item.
    """
    try:
        async with ServiceNowClient(instance_url=params.instance_url, username=params.username, password=params.password) as client:
            # We query the variable table for all records where 'cat_item' matches the provided sys_id.
            query = f"cat_item={params.item_sys_id}"

            query_params = {
                "sysparm_query": query,
                "sysparm_fields": "name,question_text,type,order,mandatory",
                # Order the results by the 'order' field so they appear as they would on the form.
                "sysparm_query_orderby": "order"
            }

            return await client.send_request("GET", "/api/now/table/item_option_new", params=query_params)
    except ServiceNowError as e:
        return {"error": type(e).__name__, "message": e.message, "details": e.details}

async def update_catalog_item_variable(params: UpdateItemVariableParams) -> Dict[str, Any]:
    """
    Updates an existing variable on a service catalog item's form.
    """
    try:
        async with ServiceNowClient(instance_url=params.instance_url, username=params.username, password=params.password) as client:
            # Build the update payload dynamically with only the provided fields.
            update_data = params.model_dump(
                exclude={"variable_sys_id", "instance_url", "username", "password"},
                exclude_unset=True
            )

            # Convert special fields to the string format ServiceNow expects
            if 'order' in update_data:
                update_data['order'] = str(update_data['order'])
            if 'mandatory' in update_data:
                update_data['mandatory'] = str(update_data['mandatory']).lower()

            if not update_data:
                return {"error": "No update data provided.", "message": "You must provide at least one field to update."}

            endpoint = f"/api/now/table/item_option_new/{params.variable_sys_id}"

            return await client.send_request("PATCH", endpoint, data=update_data)
    except ServiceNowError as e:
        return {"error": type(e).__name__, "message": e.message, "details": e.details}

async def list_catalogs(params: ListCatalogsParams) -> Dict[str, Any]:
    """
    Lists the available service catalogs in the instance.
    """
    try:
        async with ServiceNowClient(instance_url=params.instance_url, username=params.username, password=params.password) as client:
            query_parts = ["active=true"]

            if params.filter_text:
                query_parts.append(f"titleLIKE{params.filter_text}")

            final_query = "^".join(query_parts)

            query_params = {
                "sysparm_query": final_query,
                "sysparm_limit": params.limit,
                "sysparm_fields": "title,description,sys_id"
            }

            return await client.send_request("GET", "/api/now/table/sc_catalog", params=query_params)
    except ServiceNowError as e:
        return {"error": type(e).__name__, "message": e.message, "details": e.details}

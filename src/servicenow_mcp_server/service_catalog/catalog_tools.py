# src/servicenow_mcp_server/service_catalog/catalog_tools.py

"""
This module defines tools for interacting with the ServiceNow Service Catalog.
"""

from typing import Dict, Any, List, Optional
from pydantic import Field
from fastmcp import FastMCP, Context
from servicenow_mcp_server.models import BaseToolParams, get_client
from servicenow_mcp_server.tool_annotations import READ, WRITE
from servicenow_mcp_server.tool_utils import snow_tool


def register_tools(mcp: FastMCP):
    """Adds all tools defined in this file to the main server's MCP instance."""
    _tags = {"catalog"}

    mcp.tool(create_catalog, tags=_tags | {"write"}, annotations=WRITE)
    mcp.tool(list_catalog_items, tags=_tags | {"read"}, annotations=READ)
    mcp.tool(get_catalog_item, tags=_tags | {"read"}, annotations=READ)
    mcp.tool(list_catalog_categories, tags=_tags | {"read"}, annotations=READ)
    mcp.tool(create_catalog_category, tags=_tags | {"write"}, annotations=WRITE)
    mcp.tool(update_catalog_category, tags=_tags | {"write"}, annotations=WRITE)
    mcp.tool(move_catalog_items, tags=_tags | {"write"}, annotations=WRITE)
    mcp.tool(create_catalog_item_variable, tags=_tags | {"write"}, annotations=WRITE)
    mcp.tool(list_catalog_item_variables, tags=_tags | {"read"}, annotations=READ)
    mcp.tool(update_catalog_item_variable, tags=_tags | {"write"}, annotations=WRITE)
    mcp.tool(list_catalogs, tags=_tags | {"read"}, annotations=READ)


# ==============================================================================
#  Pydantic Models
# ==============================================================================

class ListCatalogItemsParams(BaseToolParams):
    limit: int = Field(20, description="The maximum number of items to return.")
    filter_text: Optional[str] = Field(None, description="A search term to filter items by name or description.")

class GetCatalogItemParams(BaseToolParams):
    sys_id: str = Field(..., description="The unique sys_id of the service catalog item to retrieve.")

class ListCatalogCategoriesParams(BaseToolParams):
    limit: int = Field(20, description="The maximum number of categories to return.")
    filter_text: Optional[str] = Field(None, description="A search term to filter categories by title or description.")
    catalog_sys_id: Optional[str] = Field(None, description="The sys_id of a specific catalog to limit the search to.")


class CreateCatalogCategoryParams(BaseToolParams):
    title: str = Field(..., description="The title for the new category.")
    catalog_sys_id: str = Field(..., description="The sys_id of the parent catalog this category will belong to.")
    description: Optional[str] = Field(None, description="An optional description for the new category.")

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


@snow_tool
async def create_catalog(params: CreateCatalogParams) -> Dict[str, Any]:
    """
    Creates a new, top-level service catalog.
    """
    async with get_client() as client:
        payload = {
            "title": params.title,
            "description": params.description
        }

        return await client.send_request("POST", "/api/now/table/sc_catalog", data=payload)

@snow_tool
async def list_catalog_items(params: ListCatalogItemsParams) -> Dict[str, Any]:
    """
    Lists available items from the Service Catalog.
    These are the end-user facing items that can be requested.
    """
    async with get_client() as client:
        query_parts = ["active=true"]

        if params.filter_text:
            term = params.filter_text
            query_parts.append(f"nameLIKE{term}^ORshort_descriptionLIKE{term}^ORdescriptionLIKE{term}")

        final_query = "^".join(query_parts)

        query_params = {
            "sysparm_query": final_query,
            "sysparm_limit": params.limit,
            "sysparm_fields": "name,short_description,price,sys_id,category"
        }

        return await client.send_request("GET", "/api/now/table/sc_cat_item", params=query_params)


@snow_tool
async def get_catalog_item(params: GetCatalogItemParams) -> Dict[str, Any]:
    """
    Retrieves the full details for a specific service catalog item using its sys_id.
    """
    async with get_client() as client:
        endpoint = f"/api/now/table/sc_cat_item/{params.sys_id}"
        return await client.send_request("GET", endpoint)


@snow_tool
async def list_catalog_categories(params: ListCatalogCategoriesParams) -> Dict[str, Any]:
    """
    Lists categories within the Service Catalog.
    Categories are used to organize catalog items.
    """
    async with get_client() as client:
        query_parts = ["active=true"]

        if params.catalog_sys_id:
            query_parts.append(f"sc_catalog={params.catalog_sys_id}")

        if params.filter_text:
            term = params.filter_text
            query_parts.append(f"titleLIKE{term}^ORdescriptionLIKE{term}")

        final_query = "^".join(query_parts)

        query_params = {
            "sysparm_query": final_query,
            "sysparm_limit": params.limit,
            "sysparm_fields": "title,description,sys_id,sc_catalog"
        }

        return await client.send_request("GET", "/api/now/table/sc_category", params=query_params)


@snow_tool
async def create_catalog_category(params: CreateCatalogCategoryParams) -> Dict[str, Any]:
    """
    Creates a new category within a specified Service Catalog.
    """
    async with get_client() as client:
        payload = {
            "title": params.title,
            "sc_catalog": params.catalog_sys_id,
            "description": params.description
        }

        return await client.send_request("POST", "/api/now/table/sc_category", data=payload)

@snow_tool
async def update_catalog_category(params: UpdateCatalogCategoryParams) -> Dict[str, Any]:
    """
    Updates an existing service catalog category's title or description.
    """
    async with get_client() as client:
        update_data = params.model_dump(
            exclude={"sys_id"},
            exclude_unset=True
        )

        if not update_data:
            return {"error": "No update data provided.", "message": "You must provide a 'title' or 'description' to update."}

        endpoint = f"/api/now/table/sc_category/{params.sys_id}"

        return await client.send_request("PATCH", endpoint, data=update_data)

async def move_catalog_items(params: MoveCatalogItemsParams, ctx: Context) -> Dict[str, Any]:
    """
    Moves one or more service catalog items to a new category.
    """
    from servicenow_mcp_server.exceptions import ServiceNowError

    async with get_client() as client:
        successes = []
        failures = []
        total = len(params.item_sys_ids)

        update_data = {"category": params.destination_category_sys_id}

        for i, item_id in enumerate(params.item_sys_ids):
            try:
                endpoint = f"/api/now/table/sc_cat_item/{item_id}"
                response = await client.send_request("PATCH", endpoint, data=update_data)

                if 'error' in response:
                    failures.append({"sys_id": item_id, "error": response.get('error')})
                else:
                    successes.append(item_id)
            except ServiceNowError as e:
                failures.append({"sys_id": item_id, "error": e.message})
            await ctx.report_progress(i + 1, total, f"Moved {i + 1}/{total} items")

        return {
            "status": "Completed",
            "moved_count": len(successes),
            "failed_count": len(failures),
            "successful_moves": successes,
            "failed_moves": failures
        }

@snow_tool
async def create_catalog_item_variable(params: CreateItemVariableParams) -> Dict[str, Any]:
    """
    Creates a new variable (question/field) on a service catalog item's form.
    """
    async with get_client() as client:
        payload = {
            "cat_item": params.item_sys_id,
            "name": params.name,
            "question_text": params.question_text,
            "type": params.type,
            "order": str(params.order),
            "mandatory": str(params.mandatory).lower()
        }

        return await client.send_request("POST", "/api/now/table/item_option_new", data=payload)

@snow_tool
async def list_catalog_item_variables(params: ListItemVariablesParams) -> Dict[str, Any]:
    """
    Lists all the variables (questions/fields) for a specific service catalog item.
    """
    async with get_client() as client:
        query = f"cat_item={params.item_sys_id}"

        query_params = {
            "sysparm_query": query,
            "sysparm_fields": "name,question_text,type,order,mandatory",
            "sysparm_query_orderby": "order"
        }

        return await client.send_request("GET", "/api/now/table/item_option_new", params=query_params)

@snow_tool
async def update_catalog_item_variable(params: UpdateItemVariableParams) -> Dict[str, Any]:
    """
    Updates an existing variable on a service catalog item's form.
    """
    async with get_client() as client:
        update_data = params.model_dump(
            exclude={"variable_sys_id"},
            exclude_unset=True
        )

        if 'order' in update_data:
            update_data['order'] = str(update_data['order'])
        if 'mandatory' in update_data:
            update_data['mandatory'] = str(update_data['mandatory']).lower()

        if not update_data:
            return {"error": "No update data provided.", "message": "You must provide at least one field to update."}

        endpoint = f"/api/now/table/item_option_new/{params.variable_sys_id}"

        return await client.send_request("PATCH", endpoint, data=update_data)

@snow_tool
async def list_catalogs(params: ListCatalogsParams) -> Dict[str, Any]:
    """
    Lists the available service catalogs in the instance.
    """
    async with get_client() as client:
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

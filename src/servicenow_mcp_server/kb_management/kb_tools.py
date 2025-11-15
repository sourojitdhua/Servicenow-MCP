# src/servicenow_mcp_server/kb_management/kb_tools.py

"""
This module defines tools for interacting with the ServiceNow Knowledge Base.
"""

from typing import Dict, Any, Optional
from pydantic import Field
from fastmcp import FastMCP
from servicenow_mcp_server.utils import ServiceNowClient
from servicenow_mcp_server.models import BaseToolParams
from servicenow_mcp_server.exceptions import ServiceNowError

def register_tools(mcp: FastMCP):
    """Adds all tools defined in this file to the main server's MCP instance."""
    mcp.add_tool(create_knowledge_base)
    mcp.add_tool(list_knowledge_bases)
    mcp.add_tool(create_category)
    mcp.add_tool(create_article)
    mcp.add_tool(update_article)
    mcp.add_tool(publish_article)
    mcp.add_tool(list_articles)
    mcp.add_tool(get_article)

# ==============================================================================
#  Pydantic Models
# ==============================================================================

class CreateKnowledgeBaseParams(BaseToolParams):
    title: str = Field(..., description="The title of the new Knowledge Base.")
    description: Optional[str] = Field(None, description="A short description of the Knowledge Base's purpose.")

class ListKnowledgeBasesParams(BaseToolParams):
    title_filter: Optional[str] = Field(None, description="Filter knowledge-bases by title.")
    limit: int = Field(20, description="Maximum number of knowledge bases to return.")

class CreateCategoryParams(BaseToolParams):
    knowledge_base_sys_id: str = Field(..., description="The sys_id of the parent Knowledge Base.")
    name: str = Field(..., description="The name of the new category.")
    description: Optional[str] = Field(None, description="Optional description.")

class CreateArticleParams(BaseToolParams):
    knowledge_base_sys_id: str = Field(..., description="The sys_id of the Knowledge Base.")
    title: str = Field(..., description="Title of the article.")
    content: str = Field(..., description="Article body (HTML or plain text).")
    category_sys_id: Optional[str] = Field(None, description="Optional sys_id of a category within the KB.")
    short_description: Optional[str] = Field(None, description="Short description / summary.")
    published: bool = Field(False, description="Whether to publish immediately.")

class UpdateArticleParams(BaseToolParams):
    sys_id: str = Field(..., description="The sys_id of the article to update.")
    title: Optional[str] = Field(None, description="New title.")
    content: Optional[str] = Field(None, description="Updated article body.")
    short_description: Optional[str] = Field(None, description="Updated short description.")
    category_sys_id: Optional[str] = Field(None, description="Re-categorize the article.")

class PublishArticleParams(BaseToolParams):
    sys_id: str = Field(..., description="The sys_id of the article to publish.")

class ListArticlesParams(BaseToolParams):
    knowledge_base_sys_id: Optional[str] = Field(None, description="Filter articles by knowledge base.")
    category_sys_id: Optional[str] = Field(None, description="Filter articles by category.")
    published_only: bool = Field(False, description="Return only published articles.")
    limit: int = Field(20, description="Maximum number of articles to return.")

class GetArticleParams(BaseToolParams):
    sys_id: str = Field(..., description="The sys_id of the article to retrieve.")

# ==============================================================================
#  Tool Functions
# ==============================================================================

async def create_knowledge_base(params: CreateKnowledgeBaseParams) -> Dict[str, Any]:
    """
    Creates a new Knowledge Base.
    """
    try:
        async with ServiceNowClient(instance_url=params.instance_url, username=params.username, password=params.password) as client:
            # The table for Knowledge Bases is 'kb_knowledge_base'.
            payload = params.model_dump(
                exclude={"instance_url", "username", "password"},
                exclude_unset=True
            )

            return await client.send_request("POST", "/api/now/table/kb_knowledge_base", data=payload)
    except ServiceNowError as e:
        return {"error": type(e).__name__, "message": e.message, "details": e.details}

async def list_knowledge_bases(params: ListKnowledgeBasesParams) -> Dict[str, Any]:
    """List knowledge bases with optional title filter."""
    try:
        async with ServiceNowClient(instance_url=params.instance_url, username=params.username, password=params.password) as client:
            query_parts = []
            if params.title_filter:
                query_parts.append(f"titleLIKE{params.title_filter}")

            query = "^".join(query_parts)
            qp = {"sysparm_limit": params.limit}
            if query:
                qp["sysparm_query"] = query

            return await client.send_request("GET", "/api/now/table/kb_knowledge_base", params=qp)
    except ServiceNowError as e:
        return {"error": type(e).__name__, "message": e.message, "details": e.details}

async def create_category(params: CreateCategoryParams) -> Dict[str, Any]:
    """Create a new category inside a Knowledge Base."""
    try:
        async with ServiceNowClient(instance_url=params.instance_url, username=params.username, password=params.password) as client:
            payload = {
                "label": params.name,
                "value": params.name.lower().replace(" ", "_"),
                "parent_id": params.knowledge_base_sys_id,
                "parent_table": "kb_knowledge_base"
            }
            return await client.send_request("POST", "/api/now/table/kb_category", data=payload)
    except ServiceNowError as e:
        return {"error": type(e).__name__, "message": e.message, "details": e.details}

async def create_article(params: CreateArticleParams) -> Dict[str, Any]:
    """Create a new knowledge article."""
    try:
        async with ServiceNowClient(instance_url=params.instance_url, username=params.username, password=params.password) as client:
            payload = {
                "kb_knowledge_base": params.knowledge_base_sys_id,
                "short_description": params.title, # short_description IS the title field
                "article_body": params.content, # The HTML field is article_body
                "kb_category": params.category_sys_id,
                "workflow_state": "published" if params.published else "draft"
            }
            payload = {k: v for k, v in payload.items() if v is not None}
            return await client.send_request("POST", "/api/now/table/kb_knowledge", data=payload)
    except ServiceNowError as e:
        return {"error": type(e).__name__, "message": e.message, "details": e.details}

async def update_article(params: UpdateArticleParams) -> Dict[str, Any]:
    """Update an existing knowledge article."""
    try:
        async with ServiceNowClient(instance_url=params.instance_url, username=params.username, password=params.password) as client:
            payload = params.model_dump(
                exclude={"instance_url", "username", "password", "sys_id"},
                exclude_unset=True
            )
            return await client.send_request(
                "PATCH",
                f"/api/now/table/kb_knowledge/{params.sys_id}",
                data=payload
            )
    except ServiceNowError as e:
        return {"error": type(e).__name__, "message": e.message, "details": e.details}

async def publish_article(params: PublishArticleParams) -> Dict[str, Any]:
    """Publish a knowledge article (sets workflow_state to 'published')."""
    try:
        async with ServiceNowClient(instance_url=params.instance_url, username=params.username, password=params.password) as client:
            payload = {"workflow_state": "published"}
            return await client.send_request(
                "PATCH",
                f"/api/now/table/kb_knowledge/{params.sys_id}",
                data=payload
            )
    except ServiceNowError as e:
        return {"error": type(e).__name__, "message": e.message, "details": e.details}

async def list_articles(params: ListArticlesParams) -> Dict[str, Any]:
    """List knowledge articles with optional filters."""
    try:
        async with ServiceNowClient(instance_url=params.instance_url, username=params.username, password=params.password) as client:
            query_parts = []
            if params.knowledge_base_sys_id:
                query_parts.append(f"kb_knowledge_base={params.knowledge_base_sys_id}")
            if params.category_sys_id:
                query_parts.append(f"category={params.category_sys_id}")
            if params.published_only:
                query_parts.append("workflow_state=published")

            query = "^".join(query_parts)
            qp = {"sysparm_limit": params.limit}
            if query:
                qp["sysparm_query"] = query

            return await client.send_request("GET", "/api/now/table/kb_knowledge", params=qp)
    except ServiceNowError as e:
        return {"error": type(e).__name__, "message": e.message, "details": e.details}

async def get_article(params: GetArticleParams) -> Dict[str, Any]:
    """Retrieve a single knowledge article by sys_id."""
    try:
        async with ServiceNowClient(instance_url=params.instance_url, username=params.username, password=params.password) as client:
            return await client.send_request(
                "GET",
                f"/api/now/table/kb_knowledge/{params.sys_id}"
            )
    except ServiceNowError as e:
        return {"error": type(e).__name__, "message": e.message, "details": e.details}

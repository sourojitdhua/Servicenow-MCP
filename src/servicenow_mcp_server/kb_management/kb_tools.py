# src/servicenow_mcp_server/kb_management/kb_tools.py

"""
This module defines tools for interacting with the ServiceNow Knowledge Base.
"""

from typing import Dict, Any, Optional
from pydantic import Field
from fastmcp import FastMCP
from servicenow_mcp_server.models import BaseToolParams, get_client
from servicenow_mcp_server.tool_annotations import READ, WRITE
from servicenow_mcp_server.tool_utils import snow_tool

def register_tools(mcp: FastMCP):
    """Adds all tools defined in this file to the main server's MCP instance."""
    _tags = {"kb"}

    mcp.tool(create_knowledge_base, tags=_tags | {"write"}, annotations=WRITE)
    mcp.tool(list_knowledge_bases, tags=_tags | {"read"}, annotations=READ)
    mcp.tool(create_kb_category, tags=_tags | {"write"}, annotations=WRITE)
    mcp.tool(create_kb_article, tags=_tags | {"write"}, annotations=WRITE)
    mcp.tool(update_kb_article, tags=_tags | {"write"}, annotations=WRITE)
    mcp.tool(publish_kb_article, tags=_tags | {"write"}, annotations=WRITE)
    mcp.tool(list_kb_articles, tags=_tags | {"read"}, annotations=READ)
    mcp.tool(get_kb_article, tags=_tags | {"read"}, annotations=READ)

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

@snow_tool
async def create_knowledge_base(params: CreateKnowledgeBaseParams) -> Dict[str, Any]:
    """
    Creates a new Knowledge Base.
    """
    async with get_client() as client:
        payload = params.model_dump(exclude_unset=True)
        return await client.send_request("POST", "/api/now/table/kb_knowledge_base", data=payload)

@snow_tool
async def list_knowledge_bases(params: ListKnowledgeBasesParams) -> Dict[str, Any]:
    """List knowledge bases with optional title filter."""
    async with get_client() as client:
        query_parts = []
        if params.title_filter:
            query_parts.append(f"titleLIKE{params.title_filter}")

        query = "^".join(query_parts)
        qp = {"sysparm_limit": params.limit}
        if query:
            qp["sysparm_query"] = query

        return await client.send_request("GET", "/api/now/table/kb_knowledge_base", params=qp)

@snow_tool
async def create_kb_category(params: CreateCategoryParams) -> Dict[str, Any]:
    """Create a new category inside a ServiceNow Knowledge Base (kb_category table)."""
    async with get_client() as client:
        payload = {
            "label": params.name,
            "value": params.name.lower().replace(" ", "_"),
            "parent_id": params.knowledge_base_sys_id,
            "parent_table": "kb_knowledge_base"
        }
        return await client.send_request("POST", "/api/now/table/kb_category", data=payload)

@snow_tool
async def create_kb_article(params: CreateArticleParams) -> Dict[str, Any]:
    """Create a new Knowledge Base article in the kb_knowledge table."""
    async with get_client() as client:
        payload = {
            "kb_knowledge_base": params.knowledge_base_sys_id,
            "short_description": params.title,
            "article_body": params.content,
            "kb_category": params.category_sys_id,
            "workflow_state": "published" if params.published else "draft"
        }
        payload = {k: v for k, v in payload.items() if v is not None}
        return await client.send_request("POST", "/api/now/table/kb_knowledge", data=payload)

@snow_tool
async def update_kb_article(params: UpdateArticleParams) -> Dict[str, Any]:
    """Update an existing Knowledge Base article in the kb_knowledge table."""
    async with get_client() as client:
        payload = params.model_dump(
            exclude={"sys_id"},
            exclude_unset=True
        )
        return await client.send_request(
            "PATCH",
            f"/api/now/table/kb_knowledge/{params.sys_id}",
            data=payload
        )

@snow_tool
async def publish_kb_article(params: PublishArticleParams) -> Dict[str, Any]:
    """Publish a Knowledge Base article (sets workflow_state to 'published')."""
    async with get_client() as client:
        payload = {"workflow_state": "published"}
        return await client.send_request(
            "PATCH",
            f"/api/now/table/kb_knowledge/{params.sys_id}",
            data=payload
        )

@snow_tool
async def list_kb_articles(params: ListArticlesParams) -> Dict[str, Any]:
    """List Knowledge Base articles from the kb_knowledge table with optional filters."""
    async with get_client() as client:
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

@snow_tool
async def get_kb_article(params: GetArticleParams) -> Dict[str, Any]:
    """Retrieve a single Knowledge Base article by sys_id from the kb_knowledge table."""
    async with get_client() as client:
        return await client.send_request(
            "GET",
            f"/api/now/table/kb_knowledge/{params.sys_id}"
        )

# src/servicenow_mcp_server/server.py

import json
import logging
import os
import argparse
import sys
import asyncio
from contextlib import asynccontextmanager

from fastmcp import FastMCP, Client
from fastmcp.tools import Tool
from fastmcp.server.middleware.logging import LoggingMiddleware
from fastmcp.server.middleware.timing import TimingMiddleware
from fastmcp.server.middleware.error_handling import ErrorHandlingMiddleware

from servicenow_mcp_server import __version__
from servicenow_mcp_server.config_loader import load_config
from servicenow_mcp_server.models import get_client, set_shared_client
from servicenow_mcp_server.utils import ServiceNowClient

# Import all tool registration modules
from servicenow_mcp_server.incident_management import incident_tools
from servicenow_mcp_server.table_management import table_tools
from servicenow_mcp_server.service_catalog import catalog_tools
from servicenow_mcp_server.change_management import change_tools
from servicenow_mcp_server.agile_management import story_tools, epic_tools, scrum_tools
from servicenow_mcp_server.project_management import project_tools
from servicenow_mcp_server.workflow_management import workflow_tools
from servicenow_mcp_server.script_include_management import script_include_tools
from servicenow_mcp_server.update_set_management import update_set_tools
from servicenow_mcp_server.kb_management import kb_tools
from servicenow_mcp_server.user_management import user_tools
from servicenow_mcp_server.ui_policy_management import ui_policy_tools
from servicenow_mcp_server.request_management import request_tools
from servicenow_mcp_server.analytics import analytics_tools
# New modules
from servicenow_mcp_server.cmdb_management import cmdb_tools
from servicenow_mcp_server.problem_management import problem_tools
from servicenow_mcp_server.sla_management import sla_tools
from servicenow_mcp_server.prompts import register_prompts

# Configure structured logging from LOG_LEVEL env var
log_level = os.getenv("LOG_LEVEL", "WARNING").upper()
logging.basicConfig(
    level=getattr(logging, log_level, logging.WARNING),
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger("servicenow_mcp_server")

# Suppress MCP server JSON parsing errors when running interactively
# These occur when the server receives empty input (newlines) from terminal
# Cover both the low-level parser and the exception handler loggers
logging.getLogger("mcp.server").setLevel(logging.CRITICAL)


# ---------------------------------------------------------------------------
# Lifespan: open a shared HTTP client once, reuse across all tool calls
# ---------------------------------------------------------------------------

@asynccontextmanager
async def _servicenow_lifespan(server: FastMCP):
    """Create a single ServiceNowClient for the entire server lifetime."""
    config = load_config()
    if config:
        client = ServiceNowClient(
            instance_url=config["instance"],
            username=config["username"],
            password=config["password"],
        )
        async with client:
            set_shared_client(client)
            logger.info("Shared ServiceNow HTTP client opened.")
            try:
                yield {"servicenow_client": client}
            finally:
                set_shared_client(None)
                logger.info("Shared ServiceNow HTTP client closed.")
    else:
        logger.warning("No ServiceNow credentials configured; shared client not created.")
        yield {}


_INSTRUCTIONS = (
    "You are connected to a ServiceNow instance via the ServiceNow MCP Server. "
    "Use the available tools to query, create, and update ServiceNow records. "
    "Tools are tagged by module (e.g. incident, change, cmdb) and operation type "
    "(read, write, delete). Prefer read-only tools when gathering information."
)


def _register_resources(mcp: FastMCP):
    """Register MCP resources on the server instance."""

    @mcp.resource("mcp://servicenow")
    def server_info() -> str:
        """ServiceNow MCP Server — capabilities overview."""
        return json.dumps({
            "name": "ServiceNow MCP Server",
            "version": __version__,
            "description": "MCP server for ServiceNow ITSM automation",
            "modules": [
                "incident_management", "change_management", "kb_management",
                "cmdb_management", "service_catalog", "user_management",
                "problem_management", "sla_management", "request_management",
                "agile_management", "project_management", "workflow_management",
                "script_include_management", "update_set_management",
                "table_management", "analytics", "ui_policy_management",
            ],
        })

    @mcp.resource("servicenow://incident/{sys_id}")
    async def get_incident(sys_id: str) -> str:
        """Get a ServiceNow incident by sys_id."""
        async with get_client() as client:
            result = await client.send_request("GET", f"/api/now/table/incident/{sys_id}")
            return json.dumps(result)

    @mcp.resource("servicenow://incident/number/{number}")
    async def get_incident_by_number(number: str) -> str:
        """Get a ServiceNow incident by number (e.g. INC0010107)."""
        async with get_client() as client:
            result = await client.send_request(
                "GET", "/api/now/table/incident",
                params={"sysparm_query": f"number={number}", "sysparm_limit": 1}
            )
            return json.dumps(result)

    @mcp.resource("servicenow://kb/{sys_id}")
    async def get_kb_article(sys_id: str) -> str:
        """Get a ServiceNow KB article by sys_id."""
        async with get_client() as client:
            result = await client.send_request("GET", f"/api/now/table/kb_knowledge/{sys_id}")
            return json.dumps(result)

    @mcp.resource("servicenow://change/{sys_id}")
    async def get_change_request(sys_id: str) -> str:
        """Get a ServiceNow change request by sys_id."""
        async with get_client() as client:
            result = await client.send_request("GET", f"/api/now/table/change_request/{sys_id}")
            return json.dumps(result)

    @mcp.resource("servicenow://user/{sys_id}")
    async def get_user(sys_id: str) -> str:
        """Get a ServiceNow user by sys_id."""
        async with get_client() as client:
            result = await client.send_request("GET", f"/api/now/table/sys_user/{sys_id}")
            return json.dumps(result)

    @mcp.resource("servicenow://cmdb/{sys_id}")
    async def get_cmdb_ci(sys_id: str) -> str:
        """Get a ServiceNow CMDB configuration item by sys_id."""
        async with get_client() as client:
            result = await client.send_request("GET", f"/api/now/table/cmdb_ci/{sys_id}")
            return json.dumps(result)


def create_mcp_instance() -> FastMCP:
    """Creates and populates the MCP instance with all tools for the server process."""
    mcp = FastMCP(
        name="ServiceNow MCP Server",
        instructions=_INSTRUCTIONS,
        lifespan=_servicenow_lifespan,
        middleware=[
            LoggingMiddleware(methods=["tools/call"]),
            TimingMiddleware(),
            ErrorHandlingMiddleware(include_traceback=False),
        ],
    )

    # Register tools from all modules
    incident_tools.register_tools(mcp)
    table_tools.register_tools(mcp)
    catalog_tools.register_tools(mcp)
    change_tools.register_tools(mcp)
    story_tools.register_tools(mcp)
    epic_tools.register_tools(mcp)
    scrum_tools.register_tools(mcp)
    project_tools.register_tools(mcp)
    workflow_tools.register_tools(mcp)
    script_include_tools.register_tools(mcp)
    update_set_tools.register_tools(mcp)
    kb_tools.register_tools(mcp)
    user_tools.register_tools(mcp)
    ui_policy_tools.register_tools(mcp)
    request_tools.register_tools(mcp)
    analytics_tools.register_tools(mcp)
    # New modules
    cmdb_tools.register_tools(mcp)
    problem_tools.register_tools(mcp)
    sla_tools.register_tools(mcp)

    # Register MCP resources (server metadata + entity lookups)
    _register_resources(mcp)

    # Register prompt templates
    register_prompts(mcp)

    return mcp

def print_welcome_banner():
    """Prints a custom welcome banner with gradient colors."""
    # ANSI color codes for gradient effect (cyan -> blue -> magenta)
    print("\033[96m    ███████╗███╗   ██╗ ██████╗ ██╗    ██╗\033[94m      ███╗   ███╗ ██████╗██████╗\033[0m")
    print("\033[96m    ██╔════╝████╗  ██║██╔═══██╗██║    ██║\033[94m      ████╗ ████║██╔════╝██╔══██╗\033[0m")
    print("\033[96m    ███████╗██╔██╗ ██║██║   ██║██║ █╗ ██║\033[95m█████╗\033[94m██╔████╔██║██║     ██████╔╝\033[0m")
    print("\033[94m    ╚════██║██║╚██╗██║██║   ██║██║███╗██║\033[95m╚════╝\033[94m██║╚██╔╝██║██║     ██╔═══╝\033[0m")
    print("\033[94m    ███████║██║ ╚████║╚██████╔╝╚███╔███╔╝\033[95m      ██║ ╚═╝ ██║╚██████╗██║\033[0m")
    print("\033[95m    ╚══════╝╚═╝  ╚═══╝ ╚═════╝  ╚══╝╚══╝       ╚═╝     ╚═╝ ╚═════╝╚═╝\033[0m")
    print()
    print("\033[1;96m                🔧 ServiceNow Model Control Protocol 🔧\033[0m")
    print("\033[36m           ITSM Automation • Process Control • Data Management\033[0m")
    print()
    print("\033[2;37m                [Connecting to ServiceNow Instance...]\033[0m")

def print_tool_list(all_tools: list[Tool]):
    """Prints a formatted list of all available tools."""
    print("Available Tools:")
    print("-" * 70)

    for tool in sorted(all_tools, key=lambda t: t.name):
        desc = (tool.description or "No description.").strip().split('\n')[0]
        print(f"  - {tool.name:<35} {desc}")

    print("-" * 70)
    print("For detailed parameters, please refer to the project documentation or source code.")

async def run_cli_lister():
    """
    This function acts as a temporary client to list the server's tools.
    """
    client = Client({"mcpServers": {"servicenow": {"command": "snow-mcp", "args": ["--server-mode"]}}})

    async with client:
        await client.ping()
        all_tools = await client.list_tools()
        print_tool_list(all_tools)

def main():
    """Main entry point for the snow-mcp command-line application."""
    parser = argparse.ArgumentParser(
        description="ServiceNow MCP Server CLI. By default, it starts the server for client connections.",
        formatter_class=argparse.RawTextHelpFormatter
    )
    # The only CLI argument is to list tools.
    parser.add_argument('--list-tools', action='store_true', help='List all available tools and their descriptions, then exit.')
    parser.add_argument('--sse', action='store_true', help='Start the server in SSE (HTTP) mode instead of stdio.\nUseful for Windsurf and other clients that connect via URL.')
    parser.add_argument('--host', default='127.0.0.1', help='Host to bind to in SSE mode (default: 127.0.0.1)')
    parser.add_argument('--port', type=int, default=8005, help='Port to bind to in SSE mode (default: 8005)')
    # This hidden argument prevents an infinite loop.
    parser.add_argument('--server-mode', action='store_true', help=argparse.SUPPRESS)

    args = parser.parse_args()

    # Early credential validation (warn if missing, don't crash)
    load_config()
    logger.info("ServiceNow MCP Server v%s starting up.", __version__)

    if args.server_mode:
        mcp_instance = create_mcp_instance()
        mcp_instance.run(transport="stdio")
        sys.exit(0)

    if args.list_tools:
        print_welcome_banner()
        try:
            asyncio.run(run_cli_lister())
        except Exception as e:
            print(f"\nAn error occurred while inspecting the server: {e}")
        sys.exit(0)

    if args.sse:
        print_welcome_banner()
        print(f"Starting ServiceNow MCP Server in SSE mode on http://{args.host}:{args.port}")
        print("Press Ctrl+C to stop.\n")
        mcp_instance = create_mcp_instance()
        mcp_instance.run(transport="sse", host=args.host, port=args.port)
        sys.exit(0)

    # --- Default behavior: A human is running 'snow-mcp' interactively, or a client is connecting ---
    if sys.stdin.isatty():
        print_welcome_banner()
        print("Starting ServiceNow MCP Server...")
        print("Waiting for a client connection over stdio.")
        print("Use '--list-tools' for a list of available tools.")
        print("Use '--sse' to start in HTTP/SSE mode for Windsurf.")
        print("Press Ctrl+C to exit.")

    mcp_instance = create_mcp_instance()
    mcp_instance.run(transport="stdio")

if __name__ == "__main__":
    main()

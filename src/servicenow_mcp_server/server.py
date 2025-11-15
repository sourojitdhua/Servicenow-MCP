# src/servicenow_mcp_server/server.py

import logging
import os
import argparse
import sys
import asyncio
from fastmcp import FastMCP, Client
from fastmcp.tools import Tool

from servicenow_mcp_server import __version__
from servicenow_mcp_server.config_loader import load_config

# Import all tool registration modules
from servicenow_mcp_server.incident_management import incident_tools
from servicenow_mcp_server.table_management import table_tools
from servicenow_mcp_server.service_catalog import catalog_tools
from servicenow_mcp_server.change_management import change_tools
from servicenow_mcp_server.agile_management import story_tools, epic_tools, scrum_tools
from servicenow_mcp_server.project_management import project_tools
from servicenow_mcp_server.workflow_management import workflow_tools
from servicenow_mcp_server.script_include_management import script_include_tools
from servicenow_mcp_server.changeset_management import changeset_tools
from servicenow_mcp_server.kb_management import kb_tools
from servicenow_mcp_server.user_management import user_tools
from servicenow_mcp_server.ui_policy_management import ui_policy_tools
from servicenow_mcp_server.request_management import request_tools
from servicenow_mcp_server.analytics import analytics_tools
# New modules
from servicenow_mcp_server.cmdb_management import cmdb_tools
from servicenow_mcp_server.problem_management import problem_tools
from servicenow_mcp_server.sla_management import sla_tools

# Configure structured logging from LOG_LEVEL env var
log_level = os.getenv("LOG_LEVEL", "WARNING").upper()
logging.basicConfig(
    level=getattr(logging, log_level, logging.WARNING),
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger("servicenow_mcp_server")


def create_mcp_instance() -> FastMCP:
    """Creates and populates the MCP instance with all tools for the server process."""
    mcp = FastMCP(name="ServiceNow MCP Server")

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
    changeset_tools.register_tools(mcp)
    kb_tools.register_tools(mcp)
    user_tools.register_tools(mcp)
    ui_policy_tools.register_tools(mcp)
    request_tools.register_tools(mcp)
    analytics_tools.register_tools(mcp)
    # New modules
    cmdb_tools.register_tools(mcp)
    problem_tools.register_tools(mcp)
    sla_tools.register_tools(mcp)

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

    # --- Default behavior: A human is running 'snow-mcp' interactively, or a client is connecting ---
    if sys.stdin.isatty():
        print_welcome_banner()
        print("Starting ServiceNow MCP Server...")
        print("Waiting for a client connection over stdio.")
        print("Use '--list-tools' for a list of available tools.")
        print("Press Ctrl+C to exit.")

    mcp_instance = create_mcp_instance()
    mcp_instance.run(transport="stdio")

if __name__ == "__main__":
    main()

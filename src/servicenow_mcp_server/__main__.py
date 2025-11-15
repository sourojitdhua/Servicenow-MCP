"""
Entry point for running the ServiceNow MCP server as:
    python -m servicenow_mcp_server
"""

from . import server

if __name__ == "__main__":
    server.main()

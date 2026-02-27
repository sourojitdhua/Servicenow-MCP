#!/usr/bin/env python3
"""
Example script to list ServiceNow Update Sets using the MCP server.

Credentials are read from environment variables by the MCP server:
  SERVICENOW_INSTANCE, SERVICENOW_USERNAME, SERVICENOW_PASSWORD
"""

import asyncio
import json
import os
from dotenv import load_dotenv
from fastmcp import Client

# Load environment variables from .env file
load_dotenv()

async def list_update_sets():
    """List update sets from ServiceNow using the MCP server."""

    instance_url = os.getenv("SERVICENOW_INSTANCE")
    username = os.getenv("SERVICENOW_USERNAME")
    password = os.getenv("SERVICENOW_PASSWORD")

    if not all([instance_url, username, password]):
        print("Error: Missing ServiceNow credentials in .env file")
        print("Required: SERVICENOW_INSTANCE, SERVICENOW_USERNAME, SERVICENOW_PASSWORD")
        return

    # Create a client connection to the snow-mcp server
    client = Client({
        "mcpServers": {
            "servicenow": {
                "command": "snow-mcp",
                "args": ["--server-mode"]
            }
        }
    })

    async with client:
        # Ping to ensure connection
        await client.ping()
        print("Connected to ServiceNow MCP Server\n")

        # List all available update sets
        print("=" * 70)
        print("LISTING UPDATE SETS")
        print("=" * 70)

        # Call the list_update_sets tool (credentials handled by server)
        result = await client.call_tool(
            "list_update_sets",
            arguments={
                "state_filter": "in progress",
                "limit": 10
            }
        )

        print("\nUpdate Sets (In Progress):")
        print("-" * 70)

        if result:
            data = json.loads(result[0].text)

            if "result" in data and data["result"]:
                for idx, update_set in enumerate(data["result"], 1):
                    print(f"\n{idx}. {update_set.get('name', 'N/A')}")
                    print(f"   Sys ID: {update_set.get('sys_id', 'N/A')}")
                    print(f"   State: {update_set.get('state', 'N/A')}")
                    print(f"   Created By: {update_set.get('sys_created_by', 'N/A')}")
                    if update_set.get('description'):
                        print(f"   Description: {update_set.get('description')}")
            else:
                print("No update sets found with the specified filter.")

        print("\n" + "=" * 70)

        # List all update sets (any state)
        print("\nAll Update Sets (Any State):")
        print("-" * 70)

        result_all = await client.call_tool(
            "list_update_sets",
            arguments={
                "state_filter": "",
                "limit": 5
            }
        )

        if result_all:
            data = json.loads(result_all[0].text)

            if "result" in data and data["result"]:
                for idx, update_set in enumerate(data["result"], 1):
                    print(f"\n{idx}. {update_set.get('name', 'N/A')}")
                    print(f"   State: {update_set.get('state', 'N/A')}")
                    print(f"   Sys ID: {update_set.get('sys_id', 'N/A')}")
            else:
                print("No update sets found.")

        print("\n" + "=" * 70)
        print("Complete!")

if __name__ == "__main__":
    asyncio.run(list_update_sets())

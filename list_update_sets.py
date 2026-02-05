#!/usr/bin/env python3
"""
Example script to list ServiceNow Update Sets (Changesets) using the MCP server.
"""

import asyncio
import os
from dotenv import load_dotenv
from fastmcp import Client

# Load environment variables from .env file
load_dotenv()

async def list_update_sets():
    """List update sets from ServiceNow using the MCP server."""
    
    # Get ServiceNow credentials from environment variables
    instance_url = os.getenv("SERVICENOW_INSTANCE")
    username = os.getenv("SERVICENOW_USERNAME")
    password = os.getenv("SERVICENOW_PASSWORD")
    
    if not all([instance_url, username, password]):
        print("❌ Error: Missing ServiceNow credentials in .env file")
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
        print("✓ Connected to ServiceNow MCP Server\n")
        
        # List all available changesets (update sets)
        print("=" * 70)
        print("LISTING UPDATE SETS (CHANGESETS)")
        print("=" * 70)
        
        # Call the list_changesets tool with credentials
        result = await client.call_tool(
            "list_changesets",
            arguments={
                "instance_url": instance_url,
                "username": username,
                "password": password,
                "state_filter": "in progress",  # Filter by state
                "limit": 10  # Limit to 10 results
            }
        )
        
        print("\n📦 Update Sets (In Progress):")
        print("-" * 70)
        
        if result and "result" in result[0].content[0].text:
            import json
            data = json.loads(result[0].content[0].text)
            
            if "result" in data and data["result"]:
                for idx, changeset in enumerate(data["result"], 1):
                    print(f"\n{idx}. {changeset.get('name', 'N/A')}")
                    print(f"   Sys ID: {changeset.get('sys_id', 'N/A')}")
                    print(f"   State: {changeset.get('state', 'N/A')}")
                    print(f"   Created By: {changeset.get('sys_created_by', 'N/A')}")
                    if changeset.get('description'):
                        print(f"   Description: {changeset.get('description')}")
            else:
                print("No update sets found with the specified filter.")
        else:
            print("Error retrieving update sets.")
            print(result)
        
        print("\n" + "=" * 70)
        
        # You can also list all update sets (any state)
        print("\n📦 All Update Sets (Any State):")
        print("-" * 70)
        
        result_all = await client.call_tool(
            "list_changesets",
            arguments={
                "instance_url": instance_url,
                "username": username,
                "password": password,
                "state_filter": "",  # No state filter
                "limit": 5
            }
        )
        
        if result_all and "result" in result_all[0].content[0].text:
            import json
            data = json.loads(result_all[0].content[0].text)
            
            if "result" in data and data["result"]:
                for idx, changeset in enumerate(data["result"], 1):
                    print(f"\n{idx}. {changeset.get('name', 'N/A')}")
                    print(f"   State: {changeset.get('state', 'N/A')}")
                    print(f"   Sys ID: {changeset.get('sys_id', 'N/A')}")
            else:
                print("No update sets found.")
        
        print("\n" + "=" * 70)
        print("✓ Complete!")

if __name__ == "__main__":
    asyncio.run(list_update_sets())

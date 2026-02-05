#!/usr/bin/env python3
"""
Quick ServiceNow operations using MCP tools directly.
No need to run the MCP server - just run this script!
"""

import asyncio
import os
from dotenv import load_dotenv

# Import the tools you need
from servicenow_mcp_server.changeset_management.changeset_tools import (
    list_changesets, ListChangesetsParams
)
from servicenow_mcp_server.incident_management.incident_tools import (
    list_incidents, ListIncidentsParams
)

load_dotenv()

async def main():
    """Quick ServiceNow operations."""
    
    instance_url = os.getenv("SERVICENOW_INSTANCE")
    username = os.getenv("SERVICENOW_USERNAME")
    password = os.getenv("SERVICENOW_PASSWORD")
    
    if not all([instance_url, username, password]):
        print("❌ Missing credentials in .env file")
        return
    
    print("🚀 ServiceNow Quick Operations\n")
    
    # Example 1: List Update Sets
    print("📦 Update Sets (In Progress):")
    print("-" * 60)
    params = ListChangesetsParams(
        instance_url=instance_url,
        username=username,
        password=password,
        state_filter="in progress",
        limit=5
    )
    result = await list_changesets(params)
    if "result" in result:
        for cs in result["result"]:
            print(f"  • {cs.get('name')} - {cs.get('sys_id')[:20]}...")
    
    # Example 2: List Recent Incidents
    print("\n\n🎫 Recent Incidents:")
    print("-" * 60)
    incident_params = ListIncidentsParams(
        instance_url=instance_url,
        username=username,
        password=password,
        query="",
        limit=5
    )
    incidents = await list_incidents(incident_params)
    if "result" in incidents:
        for inc in incidents["result"]:
            print(f"  • {inc.get('number')} - {inc.get('short_description', 'N/A')[:50]}")
    
    print("\n✅ Done!")

if __name__ == "__main__":
    asyncio.run(main())

#!/usr/bin/env python3
"""
Direct script to list ServiceNow Update Sets using the changeset_tools module.
"""

import asyncio
import os
from dotenv import load_dotenv
from servicenow_mcp_server.changeset_management.changeset_tools import list_changesets, ListChangesetsParams

# Load environment variables
load_dotenv()

async def main():
    """List update sets from ServiceNow."""
    
    # Get credentials from environment
    instance_url = os.getenv("SERVICENOW_INSTANCE")
    username = os.getenv("SERVICENOW_USERNAME")
    password = os.getenv("SERVICENOW_PASSWORD")
    
    if not all([instance_url, username, password]):
        print("❌ Error: Missing ServiceNow credentials in .env file")
        print("Required: SERVICENOW_INSTANCE, SERVICENOW_USERNAME, SERVICENOW_PASSWORD")
        return
    
    print("=" * 80)
    print("LISTING SERVICENOW UPDATE SETS (CHANGESETS)")
    print("=" * 80)
    print(f"\n🔗 Instance: {instance_url}")
    print(f"👤 User: {username}\n")
    
    # List update sets in progress
    print("\n📦 Update Sets - IN PROGRESS")
    print("-" * 80)
    
    params = ListChangesetsParams(
        instance_url=instance_url,
        username=username,
        password=password,
        state_filter="in progress",
        limit=10
    )
    
    result = await list_changesets(params)
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
        print(f"   Message: {result['message']}")
        if "details" in result:
            print(f"   Details: {result['details']}")
    elif "result" in result:
        changesets = result["result"]
        if changesets:
            for idx, cs in enumerate(changesets, 1):
                print(f"\n{idx}. {cs.get('name', 'N/A')}")
                print(f"   📋 Sys ID: {cs.get('sys_id', 'N/A')}")
                print(f"   📊 State: {cs.get('state', 'N/A')}")
                print(f"   👤 Created By: {cs.get('sys_created_by', 'N/A')}")
                if cs.get('description'):
                    print(f"   📝 Description: {cs.get('description')}")
        else:
            print("No update sets found with state 'in progress'")
    
    # List all update sets (any state)
    print("\n\n📦 Update Sets - ALL STATES (Last 5)")
    print("-" * 80)
    
    params_all = ListChangesetsParams(
        instance_url=instance_url,
        username=username,
        password=password,
        state_filter="",  # No filter
        limit=5
    )
    
    result_all = await list_changesets(params_all)
    
    if "error" in result_all:
        print(f"❌ Error: {result_all['error']}")
    elif "result" in result_all:
        changesets = result_all["result"]
        if changesets:
            for idx, cs in enumerate(changesets, 1):
                print(f"\n{idx}. {cs.get('name', 'N/A')}")
                print(f"   📊 State: {cs.get('state', 'N/A')}")
                print(f"   📋 Sys ID: {cs.get('sys_id', 'N/A')}")
        else:
            print("No update sets found")
    
    # List update sets by a specific user (optional)
    print("\n\n📦 Update Sets - BY CURRENT USER")
    print("-" * 80)
    
    params_user = ListChangesetsParams(
        instance_url=instance_url,
        username=username,
        password=password,
        state_filter="",
        created_by_filter=username,
        limit=5
    )
    
    result_user = await list_changesets(params_user)
    
    if "error" in result_user:
        print(f"❌ Error: {result_user['error']}")
    elif "result" in result_user:
        changesets = result_user["result"]
        if changesets:
            for idx, cs in enumerate(changesets, 1):
                print(f"\n{idx}. {cs.get('name', 'N/A')}")
                print(f"   📊 State: {cs.get('state', 'N/A')}")
                print(f"   📋 Sys ID: {cs.get('sys_id', 'N/A')}")
        else:
            print(f"No update sets found created by '{username}'")
    
    print("\n" + "=" * 80)
    print("✅ Complete!")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())

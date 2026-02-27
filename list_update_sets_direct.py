#!/usr/bin/env python3
"""
Direct script to list ServiceNow Update Sets using the update_set_tools module.
"""

import asyncio
import os
from dotenv import load_dotenv
from servicenow_mcp_server.update_set_management.update_set_tools import list_update_sets, ListUpdateSetsParams

# Load environment variables (credentials are read by the server automatically)
load_dotenv()

async def main():
    """List update sets from ServiceNow."""
    
    print("=" * 80)
    print("LISTING SERVICENOW UPDATE SETS")
    print("=" * 80)
    print(f"\n🔗 Instance: {os.getenv('SERVICENOW_INSTANCE')}")
    print(f"👤 User: {os.getenv('SERVICENOW_USERNAME')}\n")
    
    # List update sets in progress
    print("\n📦 Update Sets - IN PROGRESS")
    print("-" * 80)
    
    params = ListUpdateSetsParams(
        state_filter="in progress",
        limit=10
    )
    
    result = await list_update_sets(params)
    
    if "error" in result:
        print(f"❌ Error: {result['error']}")
        print(f"   Message: {result['message']}")
        if "details" in result:
            print(f"   Details: {result['details']}")
    elif "result" in result:
        update_sets = result["result"]
        if update_sets:
            for idx, cs in enumerate(update_sets, 1):
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
    
    params_all = ListUpdateSetsParams(
        state_filter="",  # No filter
        limit=5
    )
    
    result_all = await list_update_sets(params_all)
    
    if "error" in result_all:
        print(f"❌ Error: {result_all['error']}")
    elif "result" in result_all:
        update_sets = result_all["result"]
        if update_sets:
            for idx, cs in enumerate(update_sets, 1):
                print(f"\n{idx}. {cs.get('name', 'N/A')}")
                print(f"   📊 State: {cs.get('state', 'N/A')}")
                print(f"   📋 Sys ID: {cs.get('sys_id', 'N/A')}")
        else:
            print("No update sets found")
    
    # List update sets by a specific user (optional)
    print("\n\n📦 Update Sets - BY CURRENT USER")
    print("-" * 80)
    
    params_user = ListUpdateSetsParams(
        state_filter="",
        created_by_filter=os.getenv("SERVICENOW_USERNAME", "admin"),
        limit=5
    )
    
    result_user = await list_update_sets(params_user)
    
    if "error" in result_user:
        print(f"❌ Error: {result_user['error']}")
    elif "result" in result_user:
        update_sets = result_user["result"]
        if update_sets:
            for idx, cs in enumerate(update_sets, 1):
                print(f"\n{idx}. {cs.get('name', 'N/A')}")
                print(f"   📊 State: {cs.get('state', 'N/A')}")
                print(f"   📋 Sys ID: {cs.get('sys_id', 'N/A')}")
        else:
            print(f"No update sets found created by '{os.getenv('SERVICENOW_USERNAME', 'admin')}'")
    
    print("\n" + "=" * 80)
    print("✅ Complete!")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(main())

# for testing change management tools in servicenow-mcp-server
# This script will create a change request, list it, get its details, update it, 
# and verify the update.
import asyncio
from fastmcp import Client

client = Client({
    "mcpServers": {
        "servicenow": {
            "command": "snow-mcp",
            "args": [],
            "transport": "stdio"
        }
    }
})

SERVICENOW_CREDS = {
    "instance_url": "",
    "username": "admin",
    "password": ""
}

# New main function for test_client.py
async def main():
    async with client:
        await client.ping()
        print("✅ Server is reachable.")

        # --- Phase 1: Create a change request to work with ---
        print("\n[Phase 1] Creating a new change request...")
        
        # THE FIX: Add the mandatory 'description' field.
        create_payload = {
            "params": {
                **SERVICENOW_CREDS,
                "short_description": "MCP Test - Deploy new web server",
                "description": "Initial deployment of the new public-facing web server.", # <-- ADDED
                "type": "Normal"
            }
        }
        create_result = await client.call_tool("create_change_request", create_payload)
        
        # Check for creation error before proceeding
        if 'error' in create_result.data:
            print(f"❌ Failed to create change request: {create_result.data}")
            return
            
        new_change = create_result.data.get('result', {})
        change_sys_id = new_change.get('sys_id')
        change_number = new_change.get('number')
        print(f"✅ Created change request {change_number} ({change_sys_id})")

        # --- Phase 2: Test list_change_requests ---
        print(f"\n[Phase 2] Testing 'list_change_requests' to find {change_number}...")
        list_payload = { "params": { **SERVICENOW_CREDS, "query": f"number={change_number}" } }
        list_result = await client.call_tool("list_change_requests", list_payload)
        if list_result.data.get('result'):
            print(f"✅ Successfully found {change_number} in the list.")
        else:
            print(f"❌ Failed to find {change_number} via list_change_requests.")

        # --- Phase 3: Test get_change_request_details ---
        print(f"\n[Phase 3] Testing 'get_change_request_details' for {change_number}...")
        get_payload = { "params": { **SERVICENOW_CREDS, "number": change_number } }
        get_result = await client.call_tool("get_change_request_details", get_payload)
        if get_result.data.get('result', {}).get('number') == change_number:
            print(f"✅ Successfully retrieved details for {change_number}.")
        else:
            print(f"❌ Failed to get details for {change_number}.")

        # --- Phase 4: Test update_change_request ---
        print(f"\n[Phase 4] Testing 'update_change_request' for {change_number}...")
        new_desc = "UPDATED - MCP Test - Deploy new web server with latest patches"
        update_payload = { "params": { **SERVICENOW_CREDS, "sys_id": change_sys_id, "short_description": new_desc } }
        update_result = await client.call_tool("update_change_request", update_payload)
        if 'error' in update_result.data:
            print(f"❌ Update failed: {update_result.data}")
            return
        print(f"✅ Successfully called update tool for {change_number}.")

        # --- Phase 5: Verification ---
        print(f"\n[Phase 5] Verifying the update for {change_number}...")
        verify_payload = { "params": { **SERVICENOW_CREDS, "sys_id": change_sys_id } }
        verify_result = await client.call_tool("get_change_request_details", verify_payload)
        updated_desc = verify_result.data.get('result', {}).get('short_description')
        
        print(f"  - Retrieved Description: '{updated_desc}'")
        print(f"  - Expected Description:  '{new_desc}'")
        
        if updated_desc == new_desc:
            print("✅ Verification successful: The change request was updated correctly.")
        else:
            print("❌ Verification failed: The change request was not updated.")

if __name__ == "__main__":
    asyncio.run(main())
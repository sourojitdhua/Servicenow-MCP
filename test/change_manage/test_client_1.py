# test/change_manage/test_client_1.py
# This script tests the `create_change_request` tool of the ServiceNow MCP server.
# It creates a new change request and verifies it was created successfully.
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
    "instance_url": "https://your-instance.service-now.com",
    "username": "admin",
    "password": "REDACTED_PASSWORD"
}

async def main():
    async with client:
        await client.ping()
        print("✅ Server is reachable.")

        # --- Phase 1: Create a new Normal Change Request ---
        print("\n[Phase 1] Testing 'create_change_request'...")
        short_desc = "MCP Test - Upgrade core network switch"
        
        create_payload = {
            "params": {
                **SERVICENOW_CREDS,
                "short_description": short_desc,
                "description": "This change involves upgrading the firmware on the primary core network switch in the DC.",
                "type": "Normal",
                "impact": "1", # High
                "urgency": "2", # Medium
                "justification": "The new firmware includes critical security patches."
            }
        }
        
        create_result = await client.call_tool("create_change_request", create_payload)
        
        if 'error' in create_result.data:
            print("❌ Test Failed during creation:", create_result.data)
            return
        
        new_change = create_result.data.get('result', {})
        new_change_sys_id = new_change.get('sys_id')
        new_change_number = new_change.get('number')
        print(f"✅ Success! Created new change request '{new_change_number}' with sys_id: {new_change_sys_id}")

        # --- Phase 2: Verify the change was created ---
        print("\n[Phase 2] Verifying the new change request exists...")
        verify_payload = {
            "params": {
                **SERVICENOW_CREDS,
                "table_name": "change_request",
                "query": f"sys_id={new_change_sys_id}",
                "limit": 1
            }
        }
        verify_result = await client.call_tool("get_records_from_table", verify_payload)

        if 'error' in verify_result.data or not verify_result.data.get('result'):
            print("❌ Verification failed: Could not find the newly created change request.")
        else:
            found_desc = verify_result.data['result'][0].get('short_description')
            print(f"  - Found change with description: '{found_desc}'")
            if found_desc == short_desc:
                print("✅ Verification successful: The new change request was found.")
            else:
                print("❌ Verification failed: The found change's description does not match.")


if __name__ == "__main__":
    asyncio.run(main())
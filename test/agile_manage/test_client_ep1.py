# for testing the create_epic tool in the ServiceNow MCP server
# This script creates a new epic, verifies its creation, and checks the description.
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

        # --- Phase 1: Create a new epic ---
        print("\n[Phase 1] Testing 'create_epic'...")
        short_desc = "Implement Self-Service Password Reset Portal"
        
        create_payload = {
            "params": {
                **SERVICENOW_CREDS,
                "short_description": short_desc,
                "description": "This epic covers all stories related to building and launching the new self-service password reset functionality for end users.",
            }
        }
        
        create_result = await client.call_tool("create_epic", create_payload)
        
        if 'error' in create_result.data:
            print("❌ Test Failed during creation:", create_result.data)
            return
        
        new_epic = create_result.data.get('result', {})
        new_epic_sys_id = new_epic.get('sys_id')
        new_epic_number = new_epic.get('number')
        print(f"✅ Success! Created new epic '{new_epic_number}' with sys_id: {new_epic_sys_id}")

        # --- Phase 2: Verify the epic was created ---
        print("\n[Phase 2] Verifying the new epic exists...")
        verify_payload = {
            "params": {
                **SERVICENOW_CREDS,
                "table_name": "rm_epic",
                "query": f"sys_id={new_epic_sys_id}",
                "limit": 1
            }
        }
        verify_result = await client.call_tool("get_records_from_table", verify_payload)

        if 'error' in verify_result.data or not verify_result.data.get('result'):
            print("❌ Verification failed: Could not find the newly created epic.")
        else:
            found_desc = verify_result.data['result'][0].get('short_description')
            print(f"  - Found epic with description: '{found_desc}'")
            if found_desc == short_desc:
                print("✅ Verification successful: The new epic was found.")
            else:
                print("❌ Verification failed: The found epic's description does not match.")


if __name__ == "__main__":
    asyncio.run(main())
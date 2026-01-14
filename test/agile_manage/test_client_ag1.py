# for testing the create_story tool in the ServiceNow MCP server
# This script creates a new user story, verifies its creation, and checks the description.
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

async def main():
    async with client:
        await client.ping()
        print("✅ Server is reachable.")

        # --- Phase 1: Create a new user story ---
        print("\n[Phase 1] Testing 'create_story'...")
        short_desc = "As a user, I can reset my password via a self-service portal"
        
        create_payload = {
            "params": {
                **SERVICENOW_CREDS,
                "short_description": short_desc,
                "description": "The self-service portal should have a 'Forgot Password' link that initiates an email-based reset workflow.",
                "story_points": 8
            }
        }
        
        create_result = await client.call_tool("create_story", create_payload)
        
        if 'error' in create_result.data:
            print("❌ Test Failed during creation:", create_result.data)
            return
        
        new_story = create_result.data.get('result', {})
        new_story_sys_id = new_story.get('sys_id')
        new_story_number = new_story.get('number')
        print(f"✅ Success! Created new story '{new_story_number}' with sys_id: {new_story_sys_id}")

        # --- Phase 2: Verify the story was created ---
        print("\n[Phase 2] Verifying the new story exists...")
        verify_payload = {
            "params": {
                **SERVICENOW_CREDS,
                "table_name": "rm_story",
                "query": f"sys_id={new_story_sys_id}",
                "limit": 1
            }
        }
        verify_result = await client.call_tool("get_records_from_table", verify_payload)

        if 'error' in verify_result.data or not verify_result.data.get('result'):
            print("❌ Verification failed: Could not find the newly created story.")
        else:
            found_desc = verify_result.data['result'][0].get('short_description')
            print(f"  - Found story with description: '{found_desc}'")
            if found_desc == short_desc:
                print("✅ Verification successful: The new story was found.")
            else:
                print("❌ Verification failed: The found story's description does not match.")


if __name__ == "__main__":
    asyncio.run(main())
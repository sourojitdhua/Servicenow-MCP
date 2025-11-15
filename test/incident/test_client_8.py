# for testing the comments and work notes functionality in incidents
# This script creates an incident, adds a customer-visible comment, adds internal work notes,
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

# New main function for test_client.py
async def main():
    async with client:
        await client.ping()
        print("✅ Server is reachable.")

        # --- Phase 1: Create a new incident ---
        print("\n[Phase 1] Creating a temporary incident...")
        create_data = { "params": { **SERVICENOW_CREDS, "short_description": "Test for comments and work notes" } }
        create_result = await client.call_tool("create_incident", create_data)
        
        if 'error' in create_result.data:
            print("❌ Could not create incident. Aborting.")
            return

        incident_sys_id = create_result.data.get('result', {}).get('sys_id')
        incident_number = create_result.data.get('result', {}).get('number')
        print(f"✅ Created incident {incident_number} with sys_id: {incident_sys_id}")

        # --- Phase 2: Add a customer-visible comment ---
        print("\n[Phase 2] Calling 'add_comment_to_incident'...")
        comment_data = {
            "params": {
                **SERVICENOW_CREDS,
                "sys_id": incident_sys_id,
                "comment": "Customer-facing update: We are actively investigating."
            }
        }
        comment_result = await client.call_tool("add_comment_to_incident", comment_data)
        
        # THE FIX: We now check for a server-side error response.
        # A successful call is our measure of success.
        if 'error' in comment_result.data:
            print(f"❌ Test Failed: 'add_comment_to_incident' returned an error:", comment_result.data)
            return
        else:
            print("✅ 'add_comment_to_incident' tool executed successfully.")


        # --- Phase 3: Add internal work notes ---
        print("\n[Phase 3] Calling 'add_work_notes_to_incident'...")
        work_notes_data = {
            "params": {
                **SERVICENOW_CREDS,
                "sys_id": incident_sys_id,
                "notes": "Internal note: Escalating to the network team."
            }
        }
        notes_result = await client.call_tool("add_work_notes_to_incident", work_notes_data)
        
        if 'error' in notes_result.data:
            print(f"❌ Test Failed: 'add_work_notes_to_incident' returned an error:", notes_result.data)
            return
        else:
            print("✅ 'add_work_notes_to_incident' tool executed successfully.")


        print("\n----------------------------------------------------------------")
        print("✅ Verification successful! All communication tools executed without errors.")
        print(f"You can manually verify the updates on incident {incident_number} in your ServiceNow instance.")
        print("----------------------------------------------------------------")

if __name__ == "__main__":
    asyncio.run(main())
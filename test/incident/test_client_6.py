# for fetch the incident details, create and update the incident
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

        # --- Step 1: Create a new incident to test with ---
        print("\n[Phase 1] Creating a temporary incident...")
        create_data = { "params": { **SERVICENOW_CREDS, "short_description": "Test incident for update", "urgency": "3", "impact": "3" } }
        create_result = await client.call_tool("create_incident", create_data)
        
        if 'error' in create_result.data:
            print("❌ Could not create incident to test with. Aborting.")
            return

        incident_sys_id = create_result.data.get('result', {}).get('sys_id')
        incident_number = create_result.data.get('result', {}).get('number')
        print(f"✅ Created incident {incident_number} with sys_id: {incident_sys_id}")

        # --- Step 2: Update the incident ---
        print(f"\n[Phase 2] Updating incident {incident_number}...")
        
        # THE FIX: Instead of setting 'priority', we set the fields that CALCULATE the priority.
        update_data = {
            "params": {
                **SERVICENOW_CREDS,
                "sys_id": incident_sys_id,
                "urgency": "2",  # Change urgency to Moderate
                "impact": "2",   # Change impact to Medium
                "short_description": "UPDATED - Test incident for update"
            }
        }
        update_result = await client.call_tool("update_incident", update_data)
        
        if 'error' in update_result.data:
            print(f"❌ Failed to update incident {incident_number}:", update_result.data)
            return
        
        print(f"✅ Successfully called update tool for {incident_number}.")

        # --- Step 3: Retrieve the incident again to verify changes ---
        print(f"\n[Phase 3] Verifying changes for {incident_number}...")
        verify_data = { "params": { **SERVICENOW_CREDS, "number": incident_number } }
        verify_result = await client.call_tool("get_incident_by_number", verify_data)

        if 'error' in verify_result.data:
             print(f"❌ Failed to retrieve updated incident {incident_number}:", verify_result.data)
             return

        updated_incident = verify_result.data.get('result', {})
        new_priority = updated_incident.get('priority')
        new_desc = updated_incident.get('short_description')

        # We now expect the priority to be '3' as a result of our impact/urgency change.
        expected_priority = '3'
        print(f"  - New Priority: {new_priority} (Expected: {expected_priority})")
        print(f"  - New Description: {new_desc}")

        if new_priority == expected_priority and "UPDATED" in new_desc:
            print("\n✅ Verification successful! All changes were applied correctly.")
        else:
            print("\n❌ Verification failed! The business rule likely overrode the changes.")

if __name__ == "__main__":
    asyncio.run(main())
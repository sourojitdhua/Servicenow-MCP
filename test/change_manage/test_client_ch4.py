# This code is part of a test suite for the ServiceNow MCP server.
# It tests the `reject_change` tool, which allows users to reject change requests.
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
import datetime # Make sure this is at the top

async def main():
    async with client:
        await client.ping()
        print("✅ Server is reachable.")

        # --- Phase 1: Setup - Create and submit a change for rejection ---
        print("\n[Phase 1] Setting up a change request to be rejected...")
        # Find the 'CAB Approval' group
        find_group_payload = {"params": {**SERVICENOW_CREDS, "table_name": "sys_user_group", "query": "name=CAB Approval", "limit": 1}}
        group_result = await client.call_tool("get_records_from_table", find_group_payload)
        cab_group_sys_id = group_result.data['result'][0]['sys_id']

        # Create a change with all required fields
        start_time = datetime.datetime.now() + datetime.timedelta(days=1)
        end_time = start_time + datetime.timedelta(hours=1)
        create_payload = {"params": {**SERVICENOW_CREDS, "short_description": "MCP Test - Reject This Change", "description": "This change will be rejected by an MCP tool.", "type": "Normal", "assignment_group": cab_group_sys_id, "start_date": start_time.strftime("%Y-%m-%d %H:%M:%S"), "end_date": end_time.strftime("%Y-%m-%d %H:%M:%S"), "risk": "3"}}
        create_result = await client.call_tool("create_change_request", create_payload)
        change_sys_id = create_result.data['result']['sys_id']
        change_number = create_result.data['result']['number']
        print(f"✅ Created change request {change_number} ({change_sys_id})")

        # Submit it for approval
        submit_payload = {"params": {**SERVICENOW_CREDS, "sys_id": change_sys_id}}
        await client.call_tool("submit_change_for_approval", submit_payload)
        print(f"✅ Submitted {change_number} for approval. Waiting for workflow...")
        await asyncio.sleep(5)

        # --- Phase 2: Reject the change ---
        print(f"\n[Phase 2] Testing 'reject_change' for {change_number}...")
        reject_payload = {
            "params": {
                **SERVICENOW_CREDS,
                "sys_id": change_sys_id,
                "rejection_comments": "Rejected via MCP test: More information is required."
            }
        }
        reject_result = await client.call_tool("reject_change", reject_payload)
        
        if 'error' in reject_result.data:
            print(f"❌ Failed to reject the change: {reject_result.data}")
            print("   (NOTE: This test requires the API user to be an approver for the change.)")
            return
        print("✅ Successfully rejected the change request.")

        # --- Phase 3: Final Verification ---
        print(f"\n[Phase 3] Verifying the final state of {change_number}...")
        verify_payload = {"params": {**SERVICENOW_CREDS, "sys_id": change_sys_id}}
        verify_result = await client.call_tool("get_change_request_details", verify_payload)
        final_approval = verify_result.data['result'].get('approval')
        
        print(f"  - Final Approval Status: '{final_approval}' (Expected: 'rejected')")
        
        if final_approval == 'rejected':
            print("✅ Verification successful! The change is now rejected.")
        else:
            print("❌ Verification failed! The change is not in a rejected state.")

if __name__ == "__main__":
    asyncio.run(main())
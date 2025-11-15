# test/change_manage/test_client_ch3.py
# This script tests the `create_change_request` tool of the ServiceNow MCP server.
# It creates a new change request, adds a task, submits it for approval, and approves it.

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


import datetime # Make sure this is at the top

async def main():
    async with client:
        await client.ping()
        print("✅ Server is reachable.")

        # --- Phase 1: Find the 'CAB Approval' group ---
        print("\n[Phase 1] Finding the 'CAB Approval' group...")
        find_group_payload = {"params": {**SERVICENOW_CREDS, "table_name": "sys_user_group", "query": "name=CAB Approval", "limit": 1}}
        group_result = await client.call_tool("get_records_from_table", find_group_payload)
        if not group_result.data.get('result'):
            print("❌ Could not find 'CAB Approval' group. Test requires this group to exist. Aborting.")
            return
        cab_group_sys_id = group_result.data['result'][0]['sys_id']
        print(f"✅ Found 'CAB Approval' group with sys_id: {cab_group_sys_id}")
        
        # --- Phase 2: Create a new change request with all required fields ---
        print("\n[Phase 2] Creating a new change request...")

        start_time = datetime.datetime.now() + datetime.timedelta(days=1)
        end_time = start_time + datetime.timedelta(hours=2)

        create_payload = {
            "params": {
                **SERVICENOW_CREDS,
                "short_description": "MCP Lifecycle Test with Risk and Dates",
                "description": "Test for add_task, submit, and approve with all required fields.",
                "type": "Normal",
                "assignment_group": cab_group_sys_id,
                "start_date": start_time.strftime("%Y-%m-%d %H:%M:%S"),
                "end_date": end_time.strftime("%Y-%m-%d %H:%M:%S"),
                "risk": "3" # THE FIX: Add a risk value. 3 = Low.
            }
        }
        create_result = await client.call_tool("create_change_request", create_payload)
        
        if 'error' in create_result.data:
            print(f"❌ Failed to create change request: {create_result.data}")
            return
            
        change_sys_id = create_result.data['result']['sys_id']
        change_number = create_result.data['result']['number']
        print(f"✅ Created change request {change_number} ({change_sys_id})")

        # --- The rest of the test remains the same ---
        
        # --- Phase 3: Add a task to the change ---
        print(f"\n[Phase 3] Testing 'add_change_task' for {change_number}...")
        task_payload = {"params": {**SERVICENOW_CREDS, "change_request_sys_id": change_sys_id, "short_description": "MCP - Deploy to production"}}
        task_result = await client.call_tool("add_change_task", task_payload)
        if 'error' in task_result.data:
            print(f"❌ Failed to add task: {task_result.data}")
            return
        print("✅ Successfully added a task to the change request.")

        # --- Phase 4: Submit the change for approval ---
        print(f"\n[Phase 4] Testing 'submit_change_for_approval' for {change_number}...")
        submit_payload = {"params": {**SERVICENOW_CREDS, "sys_id": change_sys_id}}
        submit_result = await client.call_tool("submit_change_for_approval", submit_payload)
        if 'error' in submit_result.data:
            print(f"❌ Failed to submit for approval: {submit_result.data}")
            return
        print("✅ Successfully submitted the change for approval.")
        print("Waiting a moment for the approval workflow to generate records...")
        await asyncio.sleep(5) 

        # --- Phase 5: Approve the change ---
        print(f"\n[Phase 5] Testing 'approve_change' for {change_number}...")
        approve_payload = {"params": {**SERVICENOW_CREDS, "sys_id": change_sys_id, "approval_notes": "Approved via MCP."}}
        approve_result = await client.call_tool("approve_change", approve_payload)
        if 'error' in approve_result.data:
            print(f"❌ Failed to approve the change: {approve_result.data}")
            print("   (NOTE: This test requires the API user to be an approver for the change.)")
            return
        print("✅ Successfully approved the change request.")

        # --- Phase 6: Final Verification ---
        print(f"\n[Phase 6] Verifying the final state of {change_number}...")
        verify_payload = {"params": {**SERVICENOW_CREDS, "sys_id": change_sys_id}}
        verify_result = await client.call_tool("get_change_request_details", verify_payload)
        final_state = verify_result.data['result'].get('state')
        final_approval = verify_result.data['result'].get('approval')
        print(f"  - Final State: {final_state}")
        print(f"  - Final Approval: {final_approval}")
        if final_approval == 'approved':
            print("✅ Verification successful! The change is now approved.")
        else:
            print("❌ Verification failed! The change is not in an approved state.")

if __name__ == "__main__":
    asyncio.run(main())
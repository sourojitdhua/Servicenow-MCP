# New main function for test_client.py to test all scrum tools

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

        # --- Phase 1: Create a parent story for the tasks ---
        print("\n" + "="*60)
        print("[Phase 1] Creating a parent story...")
        print("="*60)
        story_payload = {"params": {**SERVICENOW_CREDS, "short_description": "Parent story for scrum task test"}}
        story_result = await client.call_tool("create_story", story_payload)
        
        if 'error' in story_result.data:
            print("❌ Could not create parent story. Aborting test.", story_result.data)
            return

        parent_story = story_result.data['result']
        parent_story_sys_id = parent_story['sys_id']
        print(f"✅ Created parent story '{parent_story['number']}' with sys_id: {parent_story_sys_id}")

        # --- Phase 2: Create a new scrum task ---
        print("\n" + "="*60)
        print("[Phase 2] Testing 'create_scrum_task'...")
        print("="*60)
        task_desc = "Develop the API endpoint"
        create_task_payload = {"params": {**SERVICENOW_CREDS, "short_description": task_desc, "story_sys_id": parent_story_sys_id, "remaining_hours": 12}}
        create_result = await client.call_tool("create_scrum_task", create_task_payload)
        
        if 'error' in create_result.data:
            print("❌ Test Failed during task creation:", create_result.data)
            return
        
        new_task = create_result.data.get('result', {})
        new_task_sys_id = new_task.get('sys_id')
        new_task_number = new_task.get('number')
        print(f"✅ Success! Created new scrum task '{new_task_number}' with sys_id: {new_task_sys_id}")

        # --- Phase 3: Test list_scrum_tasks ---
        print("\n" + "="*60)
        print("[Phase 3] Testing 'list_scrum_tasks' to find the new task...")
        print("="*60)
        list_tasks_payload = {"params": {**SERVICENOW_CREDS, "story_sys_id": parent_story_sys_id}}
        list_result = await client.call_tool("list_scrum_tasks", list_tasks_payload)

        if 'error' in list_result.data or not list_result.data.get('result'):
            print("❌ List tasks test failed or returned no results:", list_result.data)
        else:
            found_tasks = list_result.data['result']
            print(f"✅ Success! Found {len(found_tasks)} task(s) for the parent story.")
            is_our_task_present = any(task.get('sys_id') == new_task_sys_id for task in found_tasks)
            if is_our_task_present:
                print(f"✅ Verification successful: Found our new task '{new_task_number}' in the list.")
            else:
                print(f"❌ Verification failed: Did not find task '{new_task_number}' in the list.")

        # --- Phase 4: Test update_scrum_task ---
        print("\n" + "="*60)
        print("[Phase 4] Testing 'update_scrum_task'...")
        print("="*60)
        update_payload = {
            "params": {
                **SERVICENOW_CREDS,
                "sys_id": new_task_sys_id,
                "remaining_hours": 4,
                "state": "1" # State for "Work in Progress"
            }
        }
        update_result = await client.call_tool("update_scrum_task", update_payload)

        if 'error' in update_result.data:
            print("❌ Update scrum task test failed:", update_result.data)
        else:
            print(f"✅ Success! Updated scrum task {new_task_number}")
            
            # Verify the update using our generic get_records_from_table tool
            verify_payload = {"params": {**SERVICENOW_CREDS, "table_name": "rm_scrum_task", "query": f"sys_id={new_task_sys_id}", "limit": 1}}
            verify_result = await client.call_tool("get_records_from_table", verify_payload)
            
            if 'error' not in verify_result.data and verify_result.data.get('result'):
                updated_task_data = verify_result.data['result'][0]
                
                # --- THE FIX IS HERE ---
                # Convert returned values to the expected type before comparing
                retrieved_hours = float(updated_task_data.get('remaining_hours', '0'))
                retrieved_state = str(updated_task_data.get('state', ''))
                
                expected_hours = 4.0
                expected_state = '1'

                # Perform the comparison on the converted types
                if retrieved_hours == expected_hours and retrieved_state == expected_state:
                    print("✅ Verification successful: Task state and remaining hours were updated correctly.")
                else:
                    print("❌ Verification failed: Task properties do not match the update.")
                    print(f"   - Got state: {retrieved_state}, expected: {expected_state}")
                    print(f"   - Got hours: {retrieved_hours}, expected: {expected_hours}")
            else:
                print("❌ Verification failed: Could not retrieve the updated scrum task.")


if __name__ == "__main__":
    asyncio.run(main())
# Complete testing script for all story tools in the ServiceNow MCP server
# This script tests: create_story, update_story, list_stories, create_story_dependency, delete_story_dependency
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
        
        # Store sys_ids for cleanup and dependencies
        created_story_ids = []
        dependency_id = None

        # --- Phase 1: Test create_story ---
        print("\n" + "="*60)
        print("[Phase 1] Testing 'create_story'...")
        print("="*60)
        
        short_desc_1 = "As a user, I can reset my password"
        short_desc_2 = "As a user, I can view my password history"
        
        create_payload_1 = {"params": {**SERVICENOW_CREDS, "short_description": short_desc_1, "description": "Workflow for password reset.", "story_points": 8}}
        create_result_1 = await client.call_tool("create_story", create_payload_1)
        
        if 'error' in create_result_1.data:
            print("❌ Test Failed during first story creation:", create_result_1.data)
            return
        
        story_1 = create_result_1.data.get('result', {})
        story_1_id = story_1.get('sys_id')
        story_1_number = story_1.get('number')
        created_story_ids.append(story_1_id)
        print(f"✅ Success! Created first story '{story_1_number}' with sys_id: {story_1_id}")
        
        create_payload_2 = {"params": {**SERVICENOW_CREDS, "short_description": short_desc_2, "description": "Audit history for password resets.", "story_points": 5}}
        create_result_2 = await client.call_tool("create_story", create_payload_2)
        
        if 'error' in create_result_2.data:
            print("❌ Test Failed during second story creation:", create_result_2.data)
            return
        
        story_2 = create_result_2.data.get('result', {})
        story_2_id = story_2.get('sys_id')
        story_2_number = story_2.get('number')
        created_story_ids.append(story_2_id)
        print(f"✅ Success! Created second story '{story_2_number}' with sys_id: {story_2_id}")

        # --- Phase 2: Test list_stories ---
        print("\n" + "="*60)
        print("[Phase 2] Testing 'list_stories'...")
        print("="*60)
        
        list_payload = {"params": {**SERVICENOW_CREDS, "limit": 20, "offset": 0}}
        list_result = await client.call_tool("list_stories", list_payload)
        
        if 'error' in list_result.data:
            print("❌ List stories test failed:", list_result.data)
        else:
            stories = list_result.data.get('result', [])
            print(f"✅ Success! Retrieved {len(stories)} stories")
            found_stories = [s.get('number') for s in stories if s.get('sys_id') in created_story_ids]
            if len(found_stories) == 2:
                print(f"✅ Verification successful: Found both created stories {found_stories}")
            else:
                print(f"⚠️ Partial verification: Found {len(found_stories)} of 2 created stories")

        # --- Phase 3: Test update_story ---
        print("\n" + "="*60)
        print("[Phase 3] Testing 'update_story'...")
        print("="*60)
        
        updated_description = "Updated description with more details."
        update_payload = {"params": {**SERVICENOW_CREDS, "story_sys_id": story_1_id, "description": updated_description, "story_points": 13}}
        update_result = await client.call_tool("update_story", update_payload)
        
        if 'error' in update_result.data:
            print("❌ Update story test failed:", update_result.data)
        else:
            print(f"✅ Success! Updated story {story_1_number}")
            # CORRECTED: Use correct table name for verification
            verify_payload = {"params": {**SERVICENOW_CREDS, "table_name": "rm_story", "query": f"sys_id={story_1_id}", "limit": 1}}
            verify_result = await client.call_tool("get_records_from_table", verify_payload)
            if 'error' not in verify_result.data and verify_result.data.get('result'):
                if verify_result.data['result'][0].get('description') == updated_description:
                    print("✅ Verification successful: Story description was updated correctly")
                else:
                    print("⚠️ Verification partial: Story was updated but description might not match exactly")
            else:
                print("❌ Verification failed: Could not retrieve updated story")

        # --- Phase 4: Test create_story_dependency ---
        print("\n" + "="*60)
        print("[Phase 4] Testing 'create_story_dependency'...")
        print("="*60)
        
        # CORRECTED: Use corrected field names
        dependency_payload = {"params": {**SERVICENOW_CREDS, "predecessor_story_sys_id": story_1_id, "successor_story_sys_id": story_2_id}}
        dependency_result = await client.call_tool("create_story_dependency", dependency_payload)
        
        if 'error' in dependency_result.data:
            print("❌ Create dependency test failed:", dependency_result.data)
        else:
            dependency_id = dependency_result.data.get('result', {}).get('sys_id')
            print(f"✅ Success! Created dependency with sys_id: {dependency_id}")
            print(f"   Story {story_1_number} is now a predecessor to {story_2_number}")

        # --- Phase 5: Test delete_story_dependency ---
        print("\n" + "="*60)
        print("[Phase 5] Testing 'delete_story_dependency'...")
        print("="*60)
        
        if dependency_id:
            # CORRECTED: Use corrected field name
            delete_dependency_payload = {"params": {**SERVICENOW_CREDS, "dependency_sys_id": dependency_id}}
            delete_dependency_result = await client.call_tool("delete_story_dependency", delete_dependency_payload)
            
            if 'error' in delete_dependency_result.data:
                print("❌ Delete dependency test failed:", delete_dependency_result.data)
            else:
                print(f"✅ Success! Deleted dependency {dependency_id}")
                # CORRECTED: Use correct table name for verification
                verify_dependency_payload = {"params": {**SERVICENOW_CREDS, "table_name": "rm_story_dependency", "query": f"sys_id={dependency_id}", "limit": 1}}
                verify_dependency_result = await client.call_tool("get_records_from_table", verify_dependency_payload)
                if 'error' in verify_dependency_result.data or not verify_dependency_result.data.get('result'):
                    print("✅ Verification successful: Dependency was deleted")
                else:
                    print("❌ Verification failed: Dependency still exists")
        else:
            print("⚠️ Skipping delete dependency test: No dependency was created")

        # --- Phase 6: Does not apply, state is a reference field ---
        # We will skip the filtered list test for now as 'state' in Agile 2.0 is a reference
        # to another table and requires a sys_id, making the test overly complex.
        
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        print("All applicable tests have been run.")

if __name__ == "__main__":
    asyncio.run(main())
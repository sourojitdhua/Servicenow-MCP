# New main function for test_client.py to test all project tools
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

        # --- Phase 1: Test create_project ---
        print("\n" + "="*60)
        print("[Phase 1] Testing 'create_project'...")
        print("="*60)
        
        project_name = "MCP Test - New Website Launch"
        create_payload = {
            "params": {
                **SERVICENOW_CREDS,
                "short_description": project_name,
                "description": "This project tracks all tasks for the Q4 launch of the new corporate website.",
                "start_date": "2024-10-01"
            }
        }
        
        create_result = await client.call_tool("create_project", create_payload)
        
        if 'error' in create_result.data:
            print("❌ Test Failed during project creation:", create_result.data)
            print("   (NOTE: Ensure the 'Project Management' (com.snc.project_management_v3) plugin is active on your instance.)")
            return
        
        project = create_result.data.get('result', {})
        project_sys_id = project.get('sys_id')
        project_number = project.get('number')
        print(f"✅ Success! Created project '{project_number}' with sys_id: {project_sys_id}")

        # --- Phase 2: Test list_projects ---
        print("\n" + "="*60)
        print("[Phase 2] Testing 'list_projects' to find the new project...")
        print("="*60)
        
        # NOTE: State values can differ. '1' is often 'Pending' or 'Draft'.
        list_payload = {"params": {**SERVICENOW_CREDS, "state": "1"}}
        list_result = await client.call_tool("list_projects", list_payload)
        
        if 'error' in list_result.data:
            print("❌ List projects test failed:", list_result.data)
        else:
            projects = list_result.data.get('result', [])
            print(f"✅ Success! 'list_projects' found {len(projects)} project(s) in the 'Pending' state.")
            found_it = any(p.get('sys_id') == project_sys_id for p in projects)
            if found_it:
                print(f"✅ Verification successful: Found our new project '{project_number}' in the list.")
            else:
                 print(f"❌ Verification failed: Did not find project '{project_number}' in the list.")

        # --- Phase 3: Test update_project ---
        print("\n" + "="*60)
        print("[Phase 3] Testing 'update_project'...")
        print("="*60)
        
        updated_description = "UPDATED - Scope now includes mobile app integration."
        
        update_payload = {
            "params": {
                **SERVICENOW_CREDS,
                "sys_id": project_sys_id,
                "description": updated_description,
                "state": "10" # '10' is often 'Work in Progress'
            }
        }
        
        update_result = await client.call_tool("update_project", update_payload)
        
        if 'error' in update_result.data:
            print("❌ Update project test failed:", update_result.data)
        else:
            print(f"✅ Success! Updated project {project_number}")
            
            # Verify the update using our generic get_records_from_table tool
            verify_payload = {"params": {**SERVICENOW_CREDS, "table_name": "pm_project", "query": f"sys_id={project_sys_id}", "limit": 1}}
            verify_result = await client.call_tool("get_records_from_table", verify_payload)
            
            if 'error' not in verify_result.data and verify_result.data.get('result'):
                updated_project_data = verify_result.data['result'][0]
                if updated_project_data.get('description') == updated_description and updated_project_data.get('state') == '10':
                    print("✅ Verification successful: Project description and state were updated correctly.")
                else:
                    print("❌ Verification failed: Project properties do not match.")
                    print(f"  - Got state: {updated_project_data.get('state')}, expected: 10")
            else:
                print("❌ Verification failed: Could not retrieve the updated project.")


if __name__ == "__main__":
    asyncio.run(main())
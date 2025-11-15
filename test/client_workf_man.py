# for testing the workflow management tools in the servicenow-mcp-server
# This script tests the `create_workflow`, `list_workflows`, `get_workflow`,
# `update_workflow`, and `delete_workflow` tools of the ServiceNow MCP server.

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

        workflow_sys_id = None
        workflow_name = "MCP Test Workflow - Temporary"

        try:
            # --- Phase 1: Test create_workflow ---
            print("\n" + "="*60)
            print("[Phase 1] Testing 'create_workflow'...")
            print("="*60)
            
            create_payload = {
                "params": {
                    **SERVICENOW_CREDS,
                    "name": workflow_name,
                    "table": "sc_request", # A common table for workflows
                    "description": "A temporary workflow created for MCP testing."
                }
            }
            
            create_result = await client.call_tool("create_workflow", create_payload)
            
            if 'error' in create_result.data:
                print("❌ Test Failed during workflow creation:", create_result.data)
                return
            
            workflow = create_result.data.get('result', {})
            workflow_sys_id = workflow.get('sys_id')
            print(f"✅ Success! Created workflow '{workflow.get('name')}' with sys_id: {workflow_sys_id}")

            # --- Phase 2: Test list_workflows ---
            print("\n" + "="*60)
            print("[Phase 2] Testing 'list_workflows' to find the new workflow...")
            print("="*60)
            
            list_payload = {"params": {**SERVICENOW_CREDS, "name_filter": workflow_name, "table_filter": "sc_request"}}
            list_result = await client.call_tool("list_workflows", list_payload)
            
            if 'error' in list_result.data or not list_result.data.get('result'):
                print("❌ List workflows test failed or returned no results:", list_result.data)
            else:
                workflows = list_result.data['result']
                print(f"✅ Success! 'list_workflows' found {len(workflows)} matching workflow(s).")
                found_it = any(w.get('sys_id') == workflow_sys_id for w in workflows)
                if found_it:
                    print(f"✅ Verification successful: Found our new workflow in the list.")
                else:
                    print(f"❌ Verification failed: Did not find the new workflow in the list.")

            # --- Phase 3: Test get_workflow ---
            print("\n" + "="*60)
            print("[Phase 3] Testing 'get_workflow'...")
            print("="*60)

            get_payload = {"params": {**SERVICENOW_CREDS, "sys_id": workflow_sys_id}}
            get_result = await client.call_tool("get_workflow", get_payload)
            if 'error' in get_result.data:
                print("❌ Get workflow test failed:", get_result.data)
            else:
                retrieved_name = get_result.data.get('result', {}).get('name')
                print(f"✅ Success! Retrieved workflow with name: '{retrieved_name}'")

            # --- Phase 4: Test update_workflow ---
            print("\n" + "="*60)
            print("[Phase 4] Testing 'update_workflow'...")
            print("="*60)
            
            updated_description = "UPDATED - This workflow is now ready for deletion."
            update_payload = {"params": {**SERVICENOW_CREDS, "sys_id": workflow_sys_id, "description": updated_description}}
            update_result = await client.call_tool("update_workflow", update_payload)
            
            if 'error' in update_result.data:
                print("❌ Update workflow test failed:", update_result.data)
            else:
                print(f"✅ Success! Updated workflow {workflow_sys_id}")
                retrieved_desc = update_result.data.get('result', {}).get('description')
                if retrieved_desc == updated_description:
                    print("✅ Verification successful: Description was updated correctly.")
                else:
                    print("❌ Verification failed: Description does not match.")

        finally:
            # --- Phase 5: Test delete_workflow (Cleanup) ---
            if workflow_sys_id:
                print("\n" + "="*60)
                print("[Phase 5] Testing 'delete_workflow' (Cleanup)...")
                print("="*60)
                
                delete_payload = {"params": {**SERVICENOW_CREDS, "sys_id": workflow_sys_id}}
                delete_result = await client.call_tool("delete_workflow", delete_payload)
                
                # DELETE returns a 204 No Content on success, so the data will be empty.
                if 'error' in delete_result.data:
                    print("❌ Delete workflow test failed:", delete_result.data)
                else:
                    print(f"✅ Success! Deleted workflow {workflow_sys_id}")
                    
                    # Verify it's gone
                    verify_result = await client.call_tool("get_workflow", delete_payload)
                    if 'error' in verify_result.data and verify_result.data.get('status_code') == 404:
                         print("✅ Verification successful: Workflow was deleted.")
                    else:
                        print("❌ Verification failed: Workflow still exists.")
            else:
                print("\nSkipping delete test as no workflow was created.")


if __name__ == "__main__":
    asyncio.run(main())
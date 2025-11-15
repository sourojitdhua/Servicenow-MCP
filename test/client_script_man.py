# for testing script_include_tools.py in the servicenow-mcp-server
# This script tests the `create_script_include`, `list_script_includes`, `get_script_include`,
# `update_script_include`, and `delete_script_include` tools of the ServiceNow MCP server.
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

        script_include_sys_id = None
        script_name = "MCPTestUtils"
        api_name = f"global.{script_name}"

        try:
            # --- Phase 1: Test create_script_include ---
            print("\n" + "="*60)
            print(f"[Phase 1] Testing 'create_script_include' for '{script_name}'...")
            print("="*60)
            
            initial_script_content = f"var {script_name} = Class.create();\n{script_name}.prototype = {{\n    initialize: function() {{\n    }},\n\n    sayHello: function() {{\n        return 'Hello, World!';\n    }},\n\n    type: '{script_name}'\n}};"
            
            create_payload = {
                "params": {
                    **SERVICENOW_CREDS,
                    "name": script_name,
                    "api_name": api_name,
                    "script": initial_script_content,
                    "description": "A temporary utility script created by the MCP server for testing."
                }
            }
            
            create_result = await client.call_tool("create_script_include", create_payload)
            
            if 'error' in create_result.data:
                print("❌ Test Failed during script include creation:", create_result.data)
                return
            
            script_include = create_result.data.get('result', {})
            script_include_sys_id = script_include.get('sys_id')
            print(f"✅ Success! Created Script Include '{script_name}' with sys_id: {script_include_sys_id}")

            # --- Phase 2: Test list_script_includes ---
            print("\n" + "="*60)
            print(f"[Phase 2] Testing 'list_script_includes' to find '{script_name}'...")
            print("="*60)
            
            list_payload = {"params": {**SERVICENOW_CREDS, "api_name_filter": api_name}}
            list_result = await client.call_tool("list_script_includes", list_payload)
            
            if 'error' in list_result.data or not list_result.data.get('result'):
                print("❌ List script includes test failed or returned no results:", list_result.data)
            else:
                found_it = any(s.get('sys_id') == script_include_sys_id for s in list_result.data['result'])
                if found_it:
                    print(f"✅ Verification successful: Found our new script include in the list.")
                else:
                    print(f"❌ Verification failed: Did not find the new script include in the list.")

            # --- Phase 3: Test get_script_include ---
            print("\n" + "="*60)
            print(f"[Phase 3] Testing 'get_script_include' to fetch '{script_name}'...")
            print("="*60)

            get_payload = {"params": {**SERVICENOW_CREDS, "sys_id": script_include_sys_id}}
            get_result = await client.call_tool("get_script_include", get_payload)
            if 'error' in get_result.data:
                print("❌ Get script include test failed:", get_result.data)
            else:
                retrieved_api_name = get_result.data.get('result', {}).get('api_name')
                print(f"✅ Success! Retrieved script with API name: '{retrieved_api_name}'")

            # --- Phase 4: Test update_script_include ---
            print("\n" + "="*60)
            print(f"[Phase 4] Testing 'update_script_include' on '{script_name}'...")
            print("="*60)
            
            updated_script_content = initial_script_content.replace("'Hello, World!'", "'Hello, MCP!' // UPDATED")
            update_payload = {"params": {**SERVICENOW_CREDS, "sys_id": script_include_sys_id, "script": updated_script_content}}
            update_result = await client.call_tool("update_script_include", update_payload)
            
            if 'error' in update_result.data:
                print("❌ Update script include test failed:", update_result.data)
            else:
                print(f"✅ Success! Updated script include {script_include_sys_id}")
                retrieved_script = update_result.data.get('result', {}).get('script')
                if "// UPDATED" in retrieved_script:
                    print("✅ Verification successful: Script content was updated correctly.")
                else:
                    print("❌ Verification failed: Script content does not match update.")

        finally:
            # --- Phase 5: Test delete_script_include (Cleanup) ---
            if script_include_sys_id:
                print("\n" + "="*60)
                print(f"[Phase 5] Testing 'delete_script_include' for '{script_name}' (Cleanup)...")
                print("="*60)
                
                delete_payload = {"params": {**SERVICENOW_CREDS, "sys_id": script_include_sys_id}}
                delete_result = await client.call_tool("delete_script_include", delete_payload)
                
                if 'error' in delete_result.data:
                    print("❌ Delete script include test failed:", delete_result.data)
                else:
                    print(f"✅ Success! Deleted script include {script_include_sys_id}")
                    
                    # Verify it's gone
                    verify_result = await client.call_tool("get_script_include", delete_payload)
                    if 'error' in verify_result.data and verify_result.data.get('status_code') == 404:
                         print("✅ Verification successful: Script include was deleted.")
                    else:
                        print("❌ Verification failed: Script include still exists.")
            else:
                print("\nSkipping delete test as no script include was created.")

if __name__ == "__main__":
    asyncio.run(main())
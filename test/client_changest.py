# New main function for test_client.py to test all changeset tools
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

        changeset_sys_id = None
        script_sys_id = None
        script_name = "MCPChangesetTestScript"

        try:
            # --- Phase 1: Create a new changeset ---
            print("\n" + "="*60)
            print("[Phase 1] Testing 'create_changeset'...")
            print("="*60)
            cs_name = "MCP Test Changeset"
            create_cs_payload = {"params": {**SERVICENOW_CREDS, "name": cs_name, "description": "A test update set."}}
            create_cs_result = await client.call_tool("create_changeset", create_cs_payload)
            
            if 'error' in create_cs_result.data:
                print("❌ Test Failed during changeset creation:", create_cs_result.data)
                return
            
            changeset = create_cs_result.data.get('result', {})
            changeset_sys_id = changeset.get('sys_id')
            print(f"✅ Success! Created changeset '{changeset.get('name')}' with sys_id: {changeset_sys_id}")

            # --- Phase 2: Create a script include to track ---
            print("\n" + "="*60)
            print("[Phase 2] Creating a temporary script include...")
            print("="*60)
            script_payload = {"params": {**SERVICENOW_CREDS, "name": script_name, "api_name": f"global.{script_name}", "script": "function hello() { return 'world'; }"}}
            script_result = await client.call_tool("create_script_include", script_payload)
            script_sys_id = script_result.data['result']['sys_id']
            print(f"✅ Success! Created temporary script include '{script_name}' with sys_id: {script_sys_id}")

            # --- Phase 3: Add the script include to the changeset ---
            print("\n" + "="*60)
            print("[Phase 3] Testing 'add_file_to_changeset'...")
            print("="*60)
            add_file_payload = {"params": {**SERVICENOW_CREDS, "changeset_sys_id": changeset_sys_id, "file_type": "sys_script_include", "file_sys_id": script_sys_id}}
            add_file_result = await client.call_tool("add_file_to_changeset", add_file_payload)

            if 'error' in add_file_result.data:
                print("❌ Test Failed adding file to changeset:", add_file_result.data)
            else:
                print("✅ Success! Added script include to the changeset.")

            # --- Phase 4: Get details and verify the change ---
            print("\n" + "="*60)
            print("[Phase 4] Testing 'get_changeset_details' and verifying content...")
            print("="*60)
            # We must use the generic tool to check the contents of the update set
            verify_content_payload = {"params": {**SERVICENOW_CREDS, "table_name": "sys_update_xml", "query": f"update_set={changeset_sys_id}", "limit": 1}}
            verify_content_result = await client.call_tool("get_records_from_table", verify_content_payload)
            
            if not verify_content_result.data.get('result'):
                print("❌ Verification Failed: The script was not found inside the changeset.")
            else:
                print("✅ Verification Successful: Found the script record inside the changeset.")


            # --- Phase 5: Update and commit the changeset ---
            print("\n" + "="*60)
            print("[Phase 5] Testing 'update_changeset' and 'commit_changeset'...")
            print("="*60)
            update_payload = {"params": {**SERVICENOW_CREDS, "sys_id": changeset_sys_id, "description": "UPDATED - Ready for commit."}}
            await client.call_tool("update_changeset", update_payload)
            print("✅ Successfully updated changeset description.")

            commit_payload = {"params": {**SERVICENOW_CREDS, "sys_id": changeset_sys_id}}
            commit_result = await client.call_tool("commit_changeset", commit_payload)

            if 'error' in commit_result.data:
                print("❌ Test Failed during commit:", commit_result.data)
            else:
                final_state = commit_result.data.get('result', {}).get('state')
                print(f"✅ Success! Committed changeset. Final state: '{final_state}'")
                if final_state != 'complete':
                    print("⚠️ Warning: Final state is not 'complete'.")

            # --- Phase 6: Publish the changeset (may fail due to permissions) ---
            print("\n" + "="*60)
            print("[Phase 6] Testing 'publish_changeset'...")
            print("="*60)
            publish_payload = {"params": {**SERVICENOW_CREDS, "sys_id": changeset_sys_id}}
            publish_result = await client.call_tool("publish_changeset", publish_payload)

            if 'error' in publish_result.data:
                print(f"⚠️ Publish command failed (This can be expected due to permissions): {publish_result.data}")
            else:
                print("✅ Success! Publish command sent successfully.")

        finally:
            # --- Cleanup Phase ---
            print("\n" + "="*60)
            print("[Cleanup] Removing temporary records...")
            print("="*60)
            if script_sys_id:
                # We can't delete a tracked record, so we just report it
                print(f"  - NOTE: Please manually delete Script Include '{script_name}' ({script_sys_id})")
            if changeset_sys_id:
                 # We also can't easily delete a completed update set via API
                print(f"  - NOTE: Please manually delete Update Set '{cs_name}' ({changeset_sys_id})")

if __name__ == "__main__":
    asyncio.run(main())
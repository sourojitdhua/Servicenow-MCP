# Test script for Update Set Management tools
# Credentials are managed by the MCP server via environment variables.
import asyncio
from fastmcp import Client

client = Client({
    "mcpServers": {
        "servicenow": {
            "command": "snow-mcp",
            "args": ["--server-mode"],
            "transport": "stdio"
        }
    }
})


async def main():
    async with client:
        await client.ping()
        print("Server is reachable.")

        update_set_sys_id = None
        script_sys_id = None
        script_name = "MCPUpdateSetTestScript"

        try:
            # --- Phase 1: Create a new update set ---
            print("\n" + "="*60)
            print("[Phase 1] Testing 'create_update_set'...")
            print("="*60)
            us_name = "MCP Test Update Set"
            result = await client.call_tool("create_update_set", {
                "params": {"name": us_name, "description": "A test update set."}
            })
            data = result.data

            if 'error' in data:
                print("FAIL - update set creation:", data)
                return

            update_set = data.get('result', {})
            update_set_sys_id = update_set.get('sys_id')
            print(f"OK - Created update set '{update_set.get('name')}' with sys_id: {update_set_sys_id}")

            # --- Phase 2: Create a script include to track ---
            print("\n" + "="*60)
            print("[Phase 2] Creating a temporary script include...")
            print("="*60)
            result = await client.call_tool("create_script_include", {
                "params": {
                    "name": script_name,
                    "api_name": f"global.{script_name}",
                    "script": "function hello() { return 'world'; }"
                }
            })
            script_sys_id = result.data['result']['sys_id']
            print(f"OK - Created temporary script include '{script_name}' with sys_id: {script_sys_id}")

            # --- Phase 3: Add the script include to the update set ---
            print("\n" + "="*60)
            print("[Phase 3] Testing 'add_file_to_update_set'...")
            print("="*60)
            result = await client.call_tool("add_file_to_update_set", {
                "params": {
                    "update_set_sys_id": update_set_sys_id,
                    "file_type": "sys_script_include",
                    "file_sys_id": script_sys_id
                }
            })
            data = result.data

            if 'error' in data:
                print("FAIL - adding file to update set:", data)
            else:
                print("OK - Added script include to the update set.")

            # --- Phase 4: Get details and verify the change ---
            print("\n" + "="*60)
            print("[Phase 4] Testing 'get_update_set_details' and verifying content...")
            print("="*60)
            result = await client.call_tool("get_records_from_table", {
                "params": {
                    "table_name": "sys_update_xml",
                    "query": f"update_set={update_set_sys_id}",
                    "limit": 1
                }
            })
            data = result.data

            if not data.get('result'):
                print("FAIL - script was not found inside the update set.")
            else:
                print("OK - Found the script record inside the update set.")

            # --- Phase 5: Update and commit the update set ---
            print("\n" + "="*60)
            print("[Phase 5] Testing 'update_update_set' and 'commit_update_set'...")
            print("="*60)
            await client.call_tool("update_update_set", {
                "params": {"sys_id": update_set_sys_id, "description": "UPDATED - Ready for commit."}
            })
            print("OK - Updated update set description.")

            result = await client.call_tool("commit_update_set", {
                "params": {"sys_id": update_set_sys_id}
            })
            data = result.data

            if result.is_error:
                print("FAIL - during commit:", data)
            else:
                final_state = data.get('result', {}).get('state')
                print(f"OK - Committed update set. Final state: '{final_state}'")
                if final_state != 'complete':
                    print("WARNING: Final state is not 'complete'.")

            # --- Phase 6: Publish the update set (may fail due to permissions) ---
            print("\n" + "="*60)
            print("[Phase 6] Testing 'publish_update_set'...")
            print("="*60)
            result = await client.call_tool("publish_update_set", {
                "params": {"sys_id": update_set_sys_id}
            })

            if result.is_error:
                print(f"WARNING - Publish failed (can be expected due to permissions)")
            else:
                print("OK - Publish command sent successfully.")

        finally:
            # --- Cleanup Phase ---
            print("\n" + "="*60)
            print("[Cleanup] Removing temporary records...")
            print("="*60)
            if script_sys_id:
                print(f"  - NOTE: Please manually delete Script Include '{script_name}' ({script_sys_id})")
            if update_set_sys_id:
                print(f"  - NOTE: Please manually delete Update Set '{us_name}' ({update_set_sys_id})")

if __name__ == "__main__":
    asyncio.run(main())

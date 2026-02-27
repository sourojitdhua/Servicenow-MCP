# Test script for list_update_sets and get_update_set_details tools
# Credentials are managed by the MCP server via environment variables.
import asyncio
import json
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


def parse_result(result):
    """Parse tool call result into a dict."""
    if result and hasattr(result[0], 'text'):
        return json.loads(result[0].text)
    return {}


async def main():
    async with client:
        await client.ping()
        print("Server is reachable.")

        update_set_sys_id = None

        try:
            # --- Phase 1: Create an update set so we have a known record ---
            print("\n" + "="*60)
            print("[Phase 1] Creating a test update set...")
            print("="*60)

            create_result = await client.call_tool("create_update_set", {
                "name": "MCP Test Update Set (list & details)",
                "description": "Created by MCP test suite for list_update_sets and get_update_set_details coverage."
            })
            data = parse_result(create_result)

            if 'error' in data:
                print("FAIL - create update set:", data)
                return

            update_set = data.get('result', {})
            update_set_sys_id = update_set.get('sys_id')
            update_set_name = update_set.get('name', 'N/A')
            print(f"OK - Created update set '{update_set_name}' (sys_id: {update_set_sys_id})")

            # --- Phase 2: Test list_update_sets (no filters) ---
            print("\n" + "="*60)
            print("[Phase 2] Testing 'list_update_sets' (default, in progress)...")
            print("="*60)

            list_result = await client.call_tool("list_update_sets", {"limit": 10})
            list_data = parse_result(list_result)

            if 'error' in list_data:
                print("FAIL:", list_data)
            else:
                update_sets = list_data.get('result', [])
                print(f"OK - list_update_sets returned {len(update_sets)} update set(s) in 'in progress' state.")
                for us in update_sets[:5]:
                    print(f"   - {us.get('name', 'N/A')} (state: {us.get('state', 'N/A')}, sys_id: {us.get('sys_id', 'N/A')})")

                found = any(us.get('sys_id') == update_set_sys_id for us in update_sets)
                if found:
                    print("OK - Our test update set is in the list.")
                else:
                    print("WARNING - Our test update set was not found (may exceed limit).")

            # --- Phase 3: Test list_update_sets (with name filter) ---
            print("\n" + "="*60)
            print("[Phase 3] Testing 'list_update_sets' (with name_filter)...")
            print("="*60)

            filtered_result = await client.call_tool("list_update_sets", {
                "name_filter": "MCP Test Update Set",
                "limit": 10
            })
            filtered_data = parse_result(filtered_result)

            if 'error' in filtered_data:
                print("FAIL:", filtered_data)
            else:
                filtered = filtered_data.get('result', [])
                print(f"OK - Filtered list returned {len(filtered)} update set(s) matching 'MCP Test Update Set'.")
                found = any(us.get('sys_id') == update_set_sys_id for us in filtered)
                if found:
                    print("OK - Name filter correctly includes our update set.")
                else:
                    print("WARNING - Our update set was not found with name_filter.")

            # --- Phase 4: Test list_update_sets (with created_by filter) ---
            print("\n" + "="*60)
            print("[Phase 4] Testing 'list_update_sets' (with created_by_filter)...")
            print("="*60)

            creator_result = await client.call_tool("list_update_sets", {
                "created_by_filter": "admin",
                "limit": 5
            })
            creator_data = parse_result(creator_result)

            if 'error' in creator_data:
                print("FAIL:", creator_data)
            else:
                by_creator = creator_data.get('result', [])
                print(f"OK - Created-by filter returned {len(by_creator)} update set(s) by 'admin'.")

            # --- Phase 5: Test get_update_set_details ---
            print("\n" + "="*60)
            print("[Phase 5] Testing 'get_update_set_details'...")
            print("="*60)

            details_result = await client.call_tool("get_update_set_details", {
                "sys_id": update_set_sys_id
            })
            details_data = parse_result(details_result)

            if 'error' in details_data:
                print("FAIL:", details_data)
            else:
                details = details_data.get('result', {})
                print(f"OK - Retrieved update set details:")
                print(f"   Name: {details.get('name', 'N/A')}")
                print(f"   State: {details.get('state', 'N/A')}")
                print(f"   Description: {details.get('description', 'N/A')[:80]}")
                print(f"   Created by: {details.get('sys_created_by', 'N/A')}")

                if details.get('sys_id') == update_set_sys_id:
                    print("OK - sys_id matches our test update set.")
                else:
                    print("FAIL - sys_id mismatch.")

        finally:
            # --- Cleanup ---
            print("\n" + "="*60)
            print("[Cleanup] Removing test update set...")
            print("="*60)

            if update_set_sys_id:
                r = await client.call_tool("delete_record", {
                    "table_name": "sys_update_set",
                    "sys_id": update_set_sys_id
                })
                r_data = parse_result(r)
                if 'error' in r_data:
                    print(f"FAIL - clean up update set {update_set_sys_id}")
                    print(f"   (This may be expected -- update sets sometimes can't be deleted via API)")
                else:
                    print(f"OK - Cleaned up update set {update_set_sys_id}")

        print("\n" + "="*60)
        print("All list_update_sets & get_update_set_details tests completed!")
        print("="*60)

if __name__ == "__main__":
    asyncio.run(main())

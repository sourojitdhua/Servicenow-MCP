# Test script for the 2 previously untested Changeset Management tools:
#   list_changesets, get_changeset_details
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

        changeset_sys_id = None

        try:
            # --- Phase 1: Create a changeset so we have a known record ---
            print("\n" + "="*60)
            print("[Phase 1] Creating a test changeset...")
            print("="*60)

            create_payload = {
                "params": {
                    **SERVICENOW_CREDS,
                    "name": "MCP Test Changeset (list & details)",
                    "description": "Created by MCP test suite for list_changesets and get_changeset_details coverage."
                }
            }
            create_result = await client.call_tool("create_changeset", create_payload)

            if 'error' in create_result.data:
                print("❌ Failed to create changeset:", create_result.data)
                return

            changeset = create_result.data.get('result', {})
            changeset_sys_id = changeset.get('sys_id')
            changeset_name = changeset.get('name', 'N/A')
            print(f"✅ Created changeset '{changeset_name}' (sys_id: {changeset_sys_id})")

            # --- Phase 2: Test list_changesets (no filters) ---
            print("\n" + "="*60)
            print("[Phase 2] Testing 'list_changesets' (default, in progress)...")
            print("="*60)

            list_payload = {
                "params": {
                    **SERVICENOW_CREDS,
                    "limit": 10
                }
            }
            list_result = await client.call_tool("list_changesets", list_payload)

            if 'error' in list_result.data:
                print("❌ Test Failed:", list_result.data)
            else:
                changesets = list_result.data.get('result', [])
                print(f"✅ list_changesets returned {len(changesets)} changeset(s) in 'in progress' state.")
                for cs in changesets[:5]:
                    print(f"   - {cs.get('name', 'N/A')} (state: {cs.get('state', 'N/A')}, sys_id: {cs.get('sys_id', 'N/A')})")

                # Verify our test changeset is in the list
                found = any(cs.get('sys_id') == changeset_sys_id for cs in changesets)
                if found:
                    print("✅ Verification: Our test changeset is in the list.")
                else:
                    print("⚠️  Our test changeset was not found (may exceed limit).")

            # --- Phase 3: Test list_changesets (with name filter) ---
            print("\n" + "="*60)
            print("[Phase 3] Testing 'list_changesets' (with name_filter)...")
            print("="*60)

            filtered_payload = {
                "params": {
                    **SERVICENOW_CREDS,
                    "name_filter": "MCP Test Changeset",
                    "limit": 10
                }
            }
            filtered_result = await client.call_tool("list_changesets", filtered_payload)

            if 'error' in filtered_result.data:
                print("❌ Test Failed:", filtered_result.data)
            else:
                filtered = filtered_result.data.get('result', [])
                print(f"✅ Filtered list returned {len(filtered)} changeset(s) matching 'MCP Test Changeset'.")
                found = any(cs.get('sys_id') == changeset_sys_id for cs in filtered)
                if found:
                    print("✅ Verification: Name filter correctly includes our changeset.")
                else:
                    print("⚠️  Our changeset was not found with name_filter.")

            # --- Phase 4: Test list_changesets (with created_by filter) ---
            print("\n" + "="*60)
            print("[Phase 4] Testing 'list_changesets' (with created_by_filter)...")
            print("="*60)

            creator_payload = {
                "params": {
                    **SERVICENOW_CREDS,
                    "created_by_filter": "admin",
                    "limit": 5
                }
            }
            creator_result = await client.call_tool("list_changesets", creator_payload)

            if 'error' in creator_result.data:
                print("❌ Test Failed:", creator_result.data)
            else:
                by_creator = creator_result.data.get('result', [])
                print(f"✅ Created-by filter returned {len(by_creator)} changeset(s) by 'admin'.")

            # --- Phase 5: Test get_changeset_details ---
            print("\n" + "="*60)
            print("[Phase 5] Testing 'get_changeset_details'...")
            print("="*60)

            details_payload = {
                "params": {
                    **SERVICENOW_CREDS,
                    "sys_id": changeset_sys_id
                }
            }
            details_result = await client.call_tool("get_changeset_details", details_payload)

            if 'error' in details_result.data:
                print("❌ Test Failed:", details_result.data)
            else:
                details = details_result.data.get('result', {})
                print(f"✅ Retrieved changeset details:")
                print(f"   Name: {details.get('name', 'N/A')}")
                print(f"   State: {details.get('state', 'N/A')}")
                print(f"   Description: {details.get('description', 'N/A')[:80]}")
                print(f"   Created by: {details.get('sys_created_by', 'N/A')}")

                # Verify it's our changeset
                if details.get('sys_id') == changeset_sys_id:
                    print("✅ Verification: sys_id matches our test changeset.")
                else:
                    print("❌ Verification failed: sys_id mismatch.")

        finally:
            # --- Cleanup ---
            print("\n" + "="*60)
            print("[Cleanup] Removing test changeset...")
            print("="*60)

            if changeset_sys_id:
                cleanup_payload = {
                    "params": {
                        **SERVICENOW_CREDS,
                        "table_name": "sys_update_set",
                        "sys_id": changeset_sys_id
                    }
                }
                r = await client.call_tool("delete_record", cleanup_payload)
                if 'error' in r.data:
                    print(f"❌ Failed to clean up changeset {changeset_sys_id}")
                    print(f"   (This may be expected — update sets sometimes can't be deleted via API)")
                else:
                    print(f"✅ Cleaned up changeset {changeset_sys_id}")

        print("\n" + "="*60)
        print("All list_changesets & get_changeset_details tests completed!")
        print("="*60)

if __name__ == "__main__":
    asyncio.run(main())

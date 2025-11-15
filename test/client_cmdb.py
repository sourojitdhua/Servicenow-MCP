# Test script for cmdb_management/cmdb_tools.py
# Tests: list_ci_classes, create_ci, get_ci, list_cis, update_ci, get_ci_relationships
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

        ci_sys_id = None

        try:
            # --- Phase 1: Test list_ci_classes ---
            print("\n" + "="*60)
            print("[Phase 1] Testing 'list_ci_classes'...")
            print("="*60)

            list_classes_payload = {
                "params": {
                    **SERVICENOW_CREDS,
                    "filter": "server",
                    "limit": 10
                }
            }
            list_classes_result = await client.call_tool("list_ci_classes", list_classes_payload)

            if 'error' in list_classes_result.data:
                print("❌ Test Failed:", list_classes_result.data)
            else:
                classes = list_classes_result.data.get('result', [])
                print(f"✅ Found {len(classes)} CI classes matching 'server'.")
                for c in classes[:5]:
                    print(f"   - {c.get('name', 'N/A')} ({c.get('label', 'N/A')})")

            # --- Phase 2: Test create_ci ---
            print("\n" + "="*60)
            print("[Phase 2] Testing 'create_ci'...")
            print("="*60)

            create_payload = {
                "params": {
                    **SERVICENOW_CREDS,
                    "ci_class": "cmdb_ci_computer",
                    "name": "MCP-Test-Server-001",
                    "data": {
                        "short_description": "Test CI created by MCP test script",
                        "asset_tag": "MCP-AUTO-001",
                        "serial_number": "SN-MCP-TEST-001"
                    }
                }
            }
            create_result = await client.call_tool("create_ci", create_payload)

            if 'error' in create_result.data:
                print("❌ Test Failed:", create_result.data)
                return
            else:
                ci = create_result.data.get('result', {})
                ci_sys_id = ci.get('sys_id')
                print(f"✅ Created CI 'MCP-Test-Server-001' with sys_id: {ci_sys_id}")

            # --- Phase 3: Test get_ci ---
            print("\n" + "="*60)
            print("[Phase 3] Testing 'get_ci'...")
            print("="*60)

            get_payload = {
                "params": {
                    **SERVICENOW_CREDS,
                    "ci_class": "cmdb_ci_computer",
                    "sys_id": ci_sys_id
                }
            }
            get_result = await client.call_tool("get_ci", get_payload)

            if 'error' in get_result.data:
                print("❌ Test Failed:", get_result.data)
            else:
                retrieved = get_result.data.get('result', {})
                print(f"✅ Retrieved CI: {retrieved.get('name', 'N/A')}")

            # --- Phase 4: Test list_cis ---
            print("\n" + "="*60)
            print("[Phase 4] Testing 'list_cis'...")
            print("="*60)

            list_payload = {
                "params": {
                    **SERVICENOW_CREDS,
                    "ci_class": "cmdb_ci_computer",
                    "query": f"sys_id={ci_sys_id}",
                    "limit": 5
                }
            }
            list_result = await client.call_tool("list_cis", list_payload)

            if 'error' in list_result.data:
                print("❌ Test Failed:", list_result.data)
            else:
                cis = list_result.data.get('result', [])
                print(f"✅ Found {len(cis)} CI(s) in query.")

            # --- Phase 5: Test update_ci ---
            print("\n" + "="*60)
            print("[Phase 5] Testing 'update_ci'...")
            print("="*60)

            update_payload = {
                "params": {
                    **SERVICENOW_CREDS,
                    "ci_class": "cmdb_ci_computer",
                    "sys_id": ci_sys_id,
                    "data": {
                        "short_description": "Updated by MCP test script"
                    }
                }
            }
            update_result = await client.call_tool("update_ci", update_payload)

            if 'error' in update_result.data:
                print("❌ Test Failed:", update_result.data)
            else:
                updated = update_result.data.get('result', {})
                print(f"✅ Updated CI description to: {updated.get('short_description', 'N/A')}")

            # --- Phase 6: Test get_ci_relationships ---
            print("\n" + "="*60)
            print("[Phase 6] Testing 'get_ci_relationships'...")
            print("="*60)

            rel_payload = {
                "params": {
                    **SERVICENOW_CREDS,
                    "sys_id": ci_sys_id,
                    "limit": 10
                }
            }
            rel_result = await client.call_tool("get_ci_relationships", rel_payload)

            if 'error' in rel_result.data:
                print("❌ Test Failed:", rel_result.data)
            else:
                rels = rel_result.data.get('result', [])
                print(f"✅ Found {len(rels)} relationship(s) for this CI.")

        finally:
            # Cleanup: delete the CI we created
            if ci_sys_id:
                print("\n" + "="*60)
                print("[Cleanup] Deleting test CI...")
                print("="*60)
                delete_payload = {
                    "params": {
                        **SERVICENOW_CREDS,
                        "table_name": "cmdb_ci_computer",
                        "sys_id": ci_sys_id
                    }
                }
                delete_result = await client.call_tool("delete_record", delete_payload)
                if 'error' in delete_result.data:
                    print("❌ Cleanup failed:", delete_result.data)
                else:
                    print(f"✅ Cleaned up test CI {ci_sys_id}")

if __name__ == "__main__":
    asyncio.run(main())

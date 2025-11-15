# Test script for the 2 previously untested Incident Management tools:
#   list_incidents, resolve_incident
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

        incident_sys_id = None

        try:
            # --- Phase 1: Create a test incident to work with ---
            print("\n" + "="*60)
            print("[Phase 1] Creating a test incident...")
            print("="*60)

            create_payload = {
                "params": {
                    **SERVICENOW_CREDS,
                    "short_description": "MCP Test - Incident for list & resolve coverage",
                    "description": "Created by the MCP test suite to verify list_incidents and resolve_incident.",
                    "urgency": "3",
                    "impact": "3"
                }
            }
            create_result = await client.call_tool("create_incident", create_payload)

            if 'error' in create_result.data:
                print("❌ Failed to create incident:", create_result.data)
                return

            incident = create_result.data.get('result', {})
            incident_sys_id = incident.get('sys_id')
            incident_number = incident.get('number', 'N/A')
            print(f"✅ Created {incident_number} (sys_id: {incident_sys_id})")

            # --- Phase 2: Test list_incidents (basic) ---
            print("\n" + "="*60)
            print("[Phase 2] Testing 'list_incidents' (basic, no query)...")
            print("="*60)

            list_payload = {
                "params": {
                    **SERVICENOW_CREDS,
                    "limit": 5,
                    "offset": 0
                }
            }
            list_result = await client.call_tool("list_incidents", list_payload)

            if 'error' in list_result.data:
                print("❌ Test Failed:", list_result.data)
            else:
                incidents = list_result.data.get('result', [])
                print(f"✅ list_incidents returned {len(incidents)} incident(s).")
                for inc in incidents[:3]:
                    print(f"   - {inc.get('number', 'N/A')}: {inc.get('short_description', 'N/A')}")

            # --- Phase 3: Test list_incidents (with query and fields) ---
            print("\n" + "="*60)
            print("[Phase 3] Testing 'list_incidents' (with query + field selection)...")
            print("="*60)

            query_payload = {
                "params": {
                    **SERVICENOW_CREDS,
                    "query": f"sys_id={incident_sys_id}",
                    "limit": 5,
                    "fields": ["number", "short_description", "state", "sys_id"]
                }
            }
            query_result = await client.call_tool("list_incidents", query_payload)

            if 'error' in query_result.data:
                print("❌ Test Failed:", query_result.data)
            else:
                results = query_result.data.get('result', [])
                print(f"✅ Filtered query returned {len(results)} incident(s).")
                if results:
                    rec = results[0]
                    print(f"   number: {rec.get('number', 'N/A')}")
                    print(f"   short_description: {rec.get('short_description', 'N/A')}")
                    print(f"   state: {rec.get('state', 'N/A')}")
                    # Verify field selection: 'description' should NOT be present
                    if 'description' not in rec:
                        print("✅ Verification: field selection is working (description excluded).")
                    else:
                        print("⚠️  field selection may not be filtering correctly.")
                else:
                    print("❌ Our test incident was not found in the query results.")

            # --- Phase 4: Test list_incidents (with pagination) ---
            print("\n" + "="*60)
            print("[Phase 4] Testing 'list_incidents' (pagination with offset)...")
            print("="*60)

            page_payload = {
                "params": {
                    **SERVICENOW_CREDS,
                    "limit": 2,
                    "offset": 0
                }
            }
            page1_result = await client.call_tool("list_incidents", page_payload)

            page_payload2 = {
                "params": {
                    **SERVICENOW_CREDS,
                    "limit": 2,
                    "offset": 2
                }
            }
            page2_result = await client.call_tool("list_incidents", page_payload2)

            if 'error' not in page1_result.data and 'error' not in page2_result.data:
                page1 = page1_result.data.get('result', [])
                page2 = page2_result.data.get('result', [])
                page1_ids = {r.get('sys_id') for r in page1}
                page2_ids = {r.get('sys_id') for r in page2}
                overlap = page1_ids & page2_ids
                print(f"✅ Page 1: {len(page1)} records, Page 2: {len(page2)} records.")
                if not overlap:
                    print("✅ Verification: No overlap between pages — pagination is working.")
                else:
                    print(f"⚠️  Found {len(overlap)} overlapping record(s) between pages.")
            else:
                print("❌ Pagination test failed.")

            # --- Phase 5: Test resolve_incident ---
            print("\n" + "="*60)
            print("[Phase 5] Testing 'resolve_incident'...")
            print("="*60)

            resolve_payload = {
                "params": {
                    **SERVICENOW_CREDS,
                    "sys_id": incident_sys_id,
                    "close_notes": "Resolved by MCP test suite — verifying resolve_incident tool.",
                    "close_code": "Solution provided"
                }
            }
            resolve_result = await client.call_tool("resolve_incident", resolve_payload)

            if 'error' in resolve_result.data:
                print("❌ Test Failed:", resolve_result.data)
            else:
                resolved = resolve_result.data.get('result', {})
                state = resolved.get('state', 'N/A')
                incident_state = resolved.get('incident_state', 'N/A')
                close_notes = resolved.get('close_notes', 'N/A')
                print(f"✅ Resolved incident {incident_number}.")
                print(f"   state: {state}, incident_state: {incident_state}")
                print(f"   close_notes: {close_notes[:80]}...")
                # State 6 = Resolved in ServiceNow
                if str(state) == "6" or str(incident_state) == "6":
                    print("✅ Verification: Incident state is 'Resolved' (6).")
                else:
                    print(f"⚠️  Expected state=6, got state={state}, incident_state={incident_state}")

        finally:
            # --- Cleanup ---
            print("\n" + "="*60)
            print("[Cleanup] Deleting test incident...")
            print("="*60)

            if incident_sys_id:
                cleanup_payload = {
                    "params": {
                        **SERVICENOW_CREDS,
                        "table_name": "incident",
                        "sys_id": incident_sys_id
                    }
                }
                r = await client.call_tool("delete_record", cleanup_payload)
                if 'error' in r.data:
                    print(f"❌ Failed to clean up {incident_sys_id}")
                else:
                    print(f"✅ Cleaned up incident {incident_sys_id}")

        print("\n" + "="*60)
        print("All list_incidents & resolve_incident tests completed!")
        print("="*60)

if __name__ == "__main__":
    asyncio.run(main())

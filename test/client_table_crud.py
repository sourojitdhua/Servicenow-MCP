# Test script for the new generic table CRUD tools in table_management/table_tools.py
# Tests: create_record, update_record, delete_record, batch_update_records
import asyncio
import random
import string
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

def random_suffix(length=6):
    return ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))

async def main():
    async with client:
        await client.ping()
        print("✅ Server is reachable.")

        created_sys_ids = []
        suffix = random_suffix()

        try:
            # --- Phase 1: Test create_record ---
            print("\n" + "="*60)
            print("[Phase 1] Testing 'create_record' (creating 3 incidents)...")
            print("="*60)

            for i in range(3):
                create_payload = {
                    "params": {
                        **SERVICENOW_CREDS,
                        "table_name": "incident",
                        "data": {
                            "short_description": f"MCP CRUD Test {suffix} - Record {i+1}",
                            "description": f"Test record {i+1} created by generic create_record tool.",
                            "urgency": "3",
                            "impact": "3"
                        }
                    }
                }
                create_result = await client.call_tool("create_record", create_payload)

                if 'error' in create_result.data:
                    print(f"❌ Failed to create record {i+1}:", create_result.data)
                else:
                    record = create_result.data.get('result', {})
                    sys_id = record.get('sys_id')
                    number = record.get('number', 'N/A')
                    created_sys_ids.append(sys_id)
                    print(f"✅ Created {number} (sys_id: {sys_id})")

            if len(created_sys_ids) < 2:
                print("❌ Not enough records created. Aborting remaining tests.")
                return

            # --- Phase 2: Test update_record ---
            print("\n" + "="*60)
            print("[Phase 2] Testing 'update_record'...")
            print("="*60)

            target_id = created_sys_ids[0]
            update_payload = {
                "params": {
                    **SERVICENOW_CREDS,
                    "table_name": "incident",
                    "sys_id": target_id,
                    "data": {
                        "short_description": f"MCP CRUD Test {suffix} - UPDATED via update_record"
                    }
                }
            }
            update_result = await client.call_tool("update_record", update_payload)

            if 'error' in update_result.data:
                print("❌ Test Failed:", update_result.data)
            else:
                updated = update_result.data.get('result', {})
                print(f"✅ Updated record. New description: {updated.get('short_description', 'N/A')}")

            # --- Phase 3: Test batch_update_records ---
            print("\n" + "="*60)
            print(f"[Phase 3] Testing 'batch_update_records' on {len(created_sys_ids)} records...")
            print("="*60)

            batch_payload = {
                "params": {
                    **SERVICENOW_CREDS,
                    "table_name": "incident",
                    "sys_ids": created_sys_ids,
                    "data": {
                        "urgency": "2",
                        "work_notes": f"Batch-updated by MCP test script [{suffix}]"
                    }
                }
            }
            batch_result = await client.call_tool("batch_update_records", batch_payload)

            if 'error' in batch_result.data:
                print("❌ Test Failed:", batch_result.data)
            else:
                result = batch_result.data
                print(f"✅ Batch update completed:")
                print(f"   Updated: {result.get('updated_count', 0)}")
                print(f"   Failed:  {result.get('failed_count', 0)}")

            # --- Phase 4: Test delete_record ---
            print("\n" + "="*60)
            print("[Phase 4] Testing 'delete_record'...")
            print("="*60)

            delete_id = created_sys_ids.pop()  # Remove last from tracking so cleanup skips it
            delete_payload = {
                "params": {
                    **SERVICENOW_CREDS,
                    "table_name": "incident",
                    "sys_id": delete_id
                }
            }
            delete_result = await client.call_tool("delete_record", delete_payload)

            if 'error' in delete_result.data:
                print("❌ Test Failed:", delete_result.data)
            else:
                print(f"✅ Deleted record {delete_id}")

                # Verify deletion
                verify_payload = {
                    "params": {
                        **SERVICENOW_CREDS,
                        "table_name": "incident",
                        "query": f"sys_id={delete_id}",
                        "limit": 1
                    }
                }
                verify_result = await client.call_tool("get_records_from_table", verify_payload)
                records = verify_result.data.get('result', [])
                if len(records) == 0:
                    print("✅ Verification: Record confirmed deleted.")
                else:
                    print("❌ Verification: Record still exists.")

        finally:
            # Cleanup remaining records
            if created_sys_ids:
                print("\n" + "="*60)
                print(f"[Cleanup] Deleting {len(created_sys_ids)} remaining test records...")
                print("="*60)
                for sid in created_sys_ids:
                    cleanup_payload = {
                        "params": {
                            **SERVICENOW_CREDS,
                            "table_name": "incident",
                            "sys_id": sid
                        }
                    }
                    r = await client.call_tool("delete_record", cleanup_payload)
                    if 'error' in r.data:
                        print(f"❌ Failed to clean up {sid}")
                    else:
                        print(f"✅ Cleaned up {sid}")

        print("\n" + "="*60)
        print("All generic table CRUD tests completed!")
        print("="*60)

if __name__ == "__main__":
    asyncio.run(main())

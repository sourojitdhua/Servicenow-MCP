# New main function for test_client.py to test all UI Policy tools
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
# New main function for test_client.py
async def main():
    async with client:
        await client.ping()
        print("✅ Server is reachable.")

        ui_policy_sys_id = None
        action_sys_id = None

        try:
            # --- Phase 1: Find a catalog item ---
            print("\n[Phase 1] Finding the 'Apple iPad 3' catalog item...")
            find_item_payload = { "params": { **SERVICENOW_CREDS, "table_name": "sc_cat_item", "query": "name=Apple iPad 3", "limit": 1 } }
            item_result = await client.call_tool("get_records_from_table", find_item_payload)
            if not item_result.data.get('result'):
                print("❌ Could not find 'Apple iPad 3' to test with. Aborting."); return
            item_sys_id = item_result.data['result'][0]['sys_id']
            print(f"✅ Found item 'Apple iPad 3' with sys_id: {item_sys_id}")
            
            # --- Phase 2: Create a new UI Policy ---
            print("\n[Phase 2] Testing 'create_ui_policy'...")
            policy_desc = "MCP Test - Make Justification Mandatory"
            create_policy_payload = {"params": {**SERVICENOW_CREDS, "table": "sc_cat_item", "short_description": policy_desc, "conditions": "true=true", "catalog_item": item_sys_id}}
            create_policy_result = await client.call_tool("create_ui_policy", create_policy_payload)
            if 'error' in create_policy_result.data:
                print("❌ UI Policy creation failed:", create_policy_result.data); return
            
            ui_policy_sys_id = create_policy_result.data['result']['sys_id']
            print(f"✅ Created UI Policy '{policy_desc}' with sys_id: {ui_policy_sys_id}")

            # --- Phase 3: Create a new UI Policy Action ---
            print("\n[Phase 3] Testing 'create_ui_policy_action'...")
            
            # THE FIX: Add the 'catalog_item_sys_id' to the payload.
            action_payload = {
                "params": {
                    **SERVICENOW_CREDS,
                    "ui_policy_sys_id": ui_policy_sys_id,
                    "catalog_item_sys_id": item_sys_id, # <-- Pass the ID we already have
                    "variable_name": "business_justification_mcp",
                    "mandatory": "true",
                    "visible": "true"
                }
            }
            create_action_result = await client.call_tool("create_ui_policy_action", action_payload)
            
            if 'error' in create_action_result.data:
                print("❌ UI Policy Action creation failed:", create_action_result.data); return
            
            action_sys_id = create_action_result.data['result']['sys_id']
            print(f"✅ Success! Created new UI Policy Action with sys_id: {action_sys_id}")

            # --- Phase 4: Verification ---
            print("\n[Phase 4] Verifying the new UI Policy Action exists...")
            verify_payload = {"params": {**SERVICENOW_CREDS, "table_name": "catalog_ui_policy_action", "query": f"sys_id={action_sys_id}", "limit": 1}}
            verify_result = await client.call_tool("get_records_from_table", verify_payload)

            if not verify_result.data.get('result'):
                print("❌ Verification failed: Could not find the newly created UI Policy Action.")
            else:
                action_record = verify_result.data['result'][0]
                if action_record.get('mandatory') == 'true':
                    print("✅ Verification successful: The new UI Policy Action was found and is set to mandatory.")
                else:
                    print("❌ Verification failed: Action was found, but 'mandatory' is not true.")

        finally:
            # --- Cleanup Phase ---
            print("\n[Cleanup] NOTE: Manual cleanup of UI Policy and Action may be needed.")
            print(f"  - UI Policy Sys ID: {ui_policy_sys_id}")
            print(f"  - UI Policy Action Sys ID: {action_sys_id}")

if __name__ == "__main__":
    asyncio.run(main())
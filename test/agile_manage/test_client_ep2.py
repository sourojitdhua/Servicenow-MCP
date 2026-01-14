# test_epic_tools.py
# End-to-end test of the new ServiceNow epic tools
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

# New main function for test_client.py to test all epic tools

async def main():
    async with client:
        await client.ping()
        print("✅ Server is reachable.")

        # --- Phase 1: Test create_epic ---
        print("\n" + "="*60)
        print("[Phase 1] Testing 'create_epic'...")
        print("="*60)
        
        epic_desc = "Implement new SSO authentication provider"
        create_payload = {
            "params": {
                **SERVICENOW_CREDS,
                "short_description": epic_desc,
                "description": "This epic covers all work required to integrate a new SSO provider, including backend and frontend changes."
            }
        }
        
        create_result = await client.call_tool("create_epic", create_payload)
        
        if 'error' in create_result.data:
            print("❌ Test Failed during epic creation:", create_result.data)
            return
        
        epic = create_result.data.get('result', {})
        epic_sys_id = epic.get('sys_id')
        epic_number = epic.get('number')
        print(f"✅ Success! Created epic '{epic_number}' with sys_id: {epic_sys_id}")

        # --- Phase 2: Test list_epics ---
        print("\n" + "="*60)
        print("[Phase 2] Testing 'list_epics' to find the new epic...")
        print("="*60)
        
        list_payload = {
            "params": {
                **SERVICENOW_CREDS,
                "short_description": "SSO authentication" # Use a partial search
            }
        }
        
        list_result = await client.call_tool("list_epics", list_payload)
        
        if 'error' in list_result.data:
            print("❌ List epics test failed:", list_result.data)
        else:
            epics = list_result.data.get('result', [])
            print(f"✅ Success! 'list_epics' found {len(epics)} matching epic(s).")
            # Verify our specific epic is in the results
            found_it = any(e.get('sys_id') == epic_sys_id for e in epics)
            if found_it:
                print(f"✅ Verification successful: Found our new epic '{epic_number}' in the list.")
            else:
                 print(f"❌ Verification failed: Did not find epic '{epic_number}' in the list.")

        # --- Phase 3: Test update_epic ---
        print("\n" + "="*60)
        print("[Phase 3] Testing 'update_epic'...")
        print("="*60)
        
        updated_description = "UPDATED - This epic now also covers multi-factor authentication (MFA)."
        
        update_payload = {
            "params": {
                **SERVICENOW_CREDS,
                "epic_id": epic_sys_id,
                "description": updated_description
            }
        }
        
        update_result = await client.call_tool("update_epic", update_payload)
        
        if 'error' in update_result.data:
            print("❌ Update epic test failed:", update_result.data)
        else:
            print(f"✅ Success! Updated epic {epic_number}")
            
            # Verify the update using our generic get_records_from_table tool
            verify_payload = {
                "params": {
                    **SERVICENOW_CREDS,
                    "table_name": "rm_epic",
                    "query": f"sys_id={epic_sys_id}",
                    "limit": 1
                }
            }
            verify_result = await client.call_tool("get_records_from_table", verify_payload)
            
            if 'error' not in verify_result.data and verify_result.data.get('result'):
                updated_epic_data = verify_result.data['result'][0]
                if updated_epic_data.get('description') == updated_description:
                    print("✅ Verification successful: Epic description was updated correctly.")
                else:
                    print("❌ Verification failed: Epic description does not match.")
            else:
                print("❌ Verification failed: Could not retrieve the updated epic.")


if __name__ == "__main__":
    asyncio.run(main())
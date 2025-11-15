# New main function for test_client.py to test all user and group tools
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

def generate_random_string(length=8):
    """Helper to generate a random string for unique names."""
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))

async def main():
    async with client:
        await client.ping()
        print("✅ Server is reachable.")

        user_sys_id = None
        group_sys_id = None
        random_id = generate_random_string()
        user_name = f"mcp.test.{random_id}"
        group_name = f"MCP Test Group {random_id}"

        try:
            print("\n" + "="*60)
            print("[Phase 1] Testing 'create_user' and 'get_user'...")
            print("="*60)
            # THE FIX: Explicitly set active=True
            create_user_payload = {"params": {**SERVICENOW_CREDS, "first_name": "MCP", "last_name": f"TestUser_{random_id}", "user_name": user_name, "email": f"{user_name}@example.com", "active": True}}
            create_user_result = await client.call_tool("create_user", create_user_payload)
            if 'error' in create_user_result.data: print(f"❌ User creation failed: {create_user_result.data}"); return
            
            user_sys_id = create_user_result.data['result']['sys_id']
            print(f"✅ Created user '{user_name}' with sys_id: {user_sys_id}")

            get_user_payload = {"params": {**SERVICENOW_CREDS, "user_name": user_name}}
            get_user_result = await client.call_tool("get_user", get_user_payload)
            retrieved_id = get_user_result.data.get('result', [{}])[0].get('sys_id')
            print("✅ 'get_user' successful." if retrieved_id == user_sys_id else f"❌ 'get_user' verification failed. Got {retrieved_id}")

            # --- Phase 2: Test User Update & List ---
            print("\n" + "="*60)
            print("[Phase 2] Testing 'update_user' and 'list_users'...")
            print("="*60)
            update_user_payload = {"params": {**SERVICENOW_CREDS, "sys_id": user_sys_id, "title": "MCP Test Lead"}}
            await client.call_tool("update_user", update_user_payload)
            print("✅ 'update_user' call successful.")
            
            # THE FIX: Use the new 'name' filter to find our specific user
            list_users_payload = {"params": {**SERVICENOW_CREDS, "active_only": True, "name": f"TestUser_{random_id}"}}
            list_users_result = await client.call_tool("list_users", list_users_payload)
            found_user = any(u.get('sys_id') == user_sys_id for u in list_users_result.data.get('result', []))
            print("✅ 'list_users' verification successful." if found_user else "❌ 'list_users' verification failed.")
            # --- Phase 3: Test Group Creation & List ---
            print("\n" + "="*60)
            print("[Phase 3] Testing 'create_group', 'update_group' and 'list_groups'...")
            print("="*60)
            create_group_payload = {"params": {**SERVICENOW_CREDS, "name": group_name, "description": "A test group."}}
            create_group_result = await client.call_tool("create_group", create_group_payload)
            if 'error' in create_group_result.data: print(f"❌ Group creation failed: {create_group_result.data}"); return
            
            group_sys_id = create_group_result.data['result']['sys_id']
            print(f"✅ Created group '{group_name}' with sys_id: {group_sys_id}")

            update_group_payload = {"params": {**SERVICENOW_CREDS, "sys_id": group_sys_id, "description": "UPDATED - A test group."}}
            await client.call_tool("update_group", update_group_payload)
            print("✅ 'update_group' call successful.")

            list_groups_payload = {"params": {**SERVICENOW_CREDS, "active_only": True}}
            list_groups_result = await client.call_tool("list_groups", list_groups_payload)
            found_group = any(g.get('sys_id') == group_sys_id for g in list_groups_result.data.get('result', []))
            print("✅ 'list_groups' verification successful." if found_group else "❌ 'list_groups' verification failed.")

            # --- Phase 4: Test Add & Remove Group Members ---
            print("\n" + "="*60)
            print("[Phase 4] Testing 'add_group_members' and 'remove_group_members'...")
            print("="*60)
            add_members_payload = {"params": {**SERVICENOW_CREDS, "group_sys_id": group_sys_id, "user_sys_ids": [user_sys_id]}}
            add_members_result = await client.call_tool("add_group_members", add_members_payload)
            print("✅ 'add_group_members' call successful.")

            # Verify addition
            verify_add_payload = {"params": {**SERVICENOW_CREDS, "table_name": "sys_user_grmember", "query": f"group={group_sys_id}^user={user_sys_id}", "limit": 1}}
            verify_add_result = await client.call_tool("get_records_from_table", verify_add_payload)
            if verify_add_result.data.get('result'):
                print("✅ Verification successful: User was added to group.")
            else:
                print("❌ Verification failed: User was not found in group.")

            remove_members_payload = {"params": {**SERVICENOW_CREDS, "group_sys_id": group_sys_id, "user_sys_ids": [user_sys_id]}}
            remove_members_result = await client.call_tool("remove_group_members", remove_members_payload)
            print("✅ 'remove_group_members' call successful.")

            # Verify removal
            verify_remove_result = await client.call_tool("get_records_from_table", verify_add_payload)
            if not verify_remove_result.data.get('result'):
                print("✅ Verification successful: User was removed from group.")
            else:
                print("❌ Verification failed: User is still in group.")

        finally:
            # --- Cleanup Phase ---
            print("\n" + "="*60)
            print("[Cleanup] NOTE: Manual cleanup of user and group may be needed if script failed.")
            print(f"  - User Sys ID: {user_sys_id}, Username: {user_name}")
            print(f"  - Group Sys ID: {group_sys_id}, Group Name: {group_name}")
            print("="*60)


if __name__ == "__main__":
    asyncio.run(main())
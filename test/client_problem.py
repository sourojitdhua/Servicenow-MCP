# Test script for problem_management/problem_tools.py
# Tests: create_problem, get_problem, list_problems, update_problem, create_known_error
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

        problem_sys_id = None

        try:
            # --- Phase 1: Test create_problem ---
            print("\n" + "="*60)
            print("[Phase 1] Testing 'create_problem'...")
            print("="*60)

            create_payload = {
                "params": {
                    **SERVICENOW_CREDS,
                    "short_description": "MCP Test - Recurring network timeouts",
                    "description": "Multiple incidents reported about intermittent network timeouts in Building A. Created by MCP test script.",
                    "impact": "2",
                    "urgency": "2"
                }
            }
            create_result = await client.call_tool("create_problem", create_payload)

            if 'error' in create_result.data:
                print("❌ Test Failed:", create_result.data)
                return

            problem = create_result.data.get('result', {})
            problem_sys_id = problem.get('sys_id')
            problem_number = problem.get('number', 'N/A')
            print(f"✅ Created problem {problem_number} with sys_id: {problem_sys_id}")

            # --- Phase 2: Test get_problem ---
            print("\n" + "="*60)
            print("[Phase 2] Testing 'get_problem'...")
            print("="*60)

            get_payload = {
                "params": {
                    **SERVICENOW_CREDS,
                    "sys_id": problem_sys_id
                }
            }
            get_result = await client.call_tool("get_problem", get_payload)

            if 'error' in get_result.data:
                print("❌ Test Failed:", get_result.data)
            else:
                retrieved = get_result.data.get('result', {})
                print(f"✅ Retrieved problem: {retrieved.get('number', 'N/A')} - {retrieved.get('short_description', 'N/A')}")

            # --- Phase 3: Test list_problems ---
            print("\n" + "="*60)
            print("[Phase 3] Testing 'list_problems'...")
            print("="*60)

            list_payload = {
                "params": {
                    **SERVICENOW_CREDS,
                    "query": f"sys_id={problem_sys_id}",
                    "limit": 5
                }
            }
            list_result = await client.call_tool("list_problems", list_payload)

            if 'error' in list_result.data:
                print("❌ Test Failed:", list_result.data)
            else:
                problems = list_result.data.get('result', [])
                print(f"✅ Found {len(problems)} problem(s) in query.")

            # --- Phase 4: Test update_problem ---
            print("\n" + "="*60)
            print("[Phase 4] Testing 'update_problem'...")
            print("="*60)

            update_payload = {
                "params": {
                    **SERVICENOW_CREDS,
                    "sys_id": problem_sys_id,
                    "short_description": "MCP Test - Recurring network timeouts (UPDATED)",
                    "state": "2"  # Assess
                }
            }
            update_result = await client.call_tool("update_problem", update_payload)

            if 'error' in update_result.data:
                print("❌ Test Failed:", update_result.data)
            else:
                updated = update_result.data.get('result', {})
                print(f"✅ Updated problem description to: {updated.get('short_description', 'N/A')}")

            # --- Phase 5: Test create_known_error ---
            print("\n" + "="*60)
            print("[Phase 5] Testing 'create_known_error'...")
            print("="*60)

            ke_payload = {
                "params": {
                    **SERVICENOW_CREDS,
                    "sys_id": problem_sys_id,
                    "workaround": "Restart the network switch in Building A, Room 102. This provides a temporary fix for approximately 24 hours."
                }
            }
            ke_result = await client.call_tool("create_known_error", ke_payload)

            if 'error' in ke_result.data:
                print("❌ Test Failed:", ke_result.data)
            else:
                ke = ke_result.data.get('result', {})
                known_error_flag = ke.get('known_error', 'N/A')
                print(f"✅ Marked as Known Error. known_error={known_error_flag}")
                if str(known_error_flag).lower() == 'true':
                    print("✅ Verification successful: known_error flag is true.")
                else:
                    print("⚠️  known_error flag value:", known_error_flag)

        finally:
            # Cleanup: delete the problem we created
            if problem_sys_id:
                print("\n" + "="*60)
                print("[Cleanup] Deleting test problem...")
                print("="*60)
                delete_payload = {
                    "params": {
                        **SERVICENOW_CREDS,
                        "table_name": "problem",
                        "sys_id": problem_sys_id
                    }
                }
                delete_result = await client.call_tool("delete_record", delete_payload)
                if 'error' in delete_result.data:
                    print("❌ Cleanup failed:", delete_result.data)
                else:
                    print(f"✅ Cleaned up test problem {problem_sys_id}")

if __name__ == "__main__":
    asyncio.run(main())

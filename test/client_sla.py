# Test script for sla_management/sla_tools.py
# Tests: list_sla_definitions, get_task_sla, list_breached_slas
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

        # --- Phase 1: Test list_sla_definitions ---
        print("\n" + "="*60)
        print("[Phase 1] Testing 'list_sla_definitions'...")
        print("="*60)

        list_defs_payload = {
            "params": {
                **SERVICENOW_CREDS,
                "limit": 10
            }
        }
        list_defs_result = await client.call_tool("list_sla_definitions", list_defs_payload)

        if 'error' in list_defs_result.data:
            print("❌ Test Failed:", list_defs_result.data)
        else:
            defs = list_defs_result.data.get('result', [])
            print(f"✅ Found {len(defs)} SLA definition(s).")
            for d in defs[:5]:
                print(f"   - {d.get('name', 'N/A')} (sys_id: {d.get('sys_id', 'N/A')})")

        # --- Phase 2: Test get_task_sla ---
        # We need a task sys_id. Let's find a recent incident to use.
        print("\n" + "="*60)
        print("[Phase 2] Testing 'get_task_sla'...")
        print("="*60)

        # First, find a recent incident to check for SLAs
        find_task_payload = {
            "params": {
                **SERVICENOW_CREDS,
                "limit": 1
            }
        }
        recent_result = await client.call_tool("list_recent_incidents", find_task_payload)

        task_sys_id = None
        if 'error' not in recent_result.data:
            incidents = recent_result.data.get('result', [])
            if incidents:
                task_sys_id = incidents[0].get('sys_id')

        if task_sys_id:
            task_sla_payload = {
                "params": {
                    **SERVICENOW_CREDS,
                    "task_sys_id": task_sys_id,
                    "limit": 10
                }
            }
            task_sla_result = await client.call_tool("get_task_sla", task_sla_payload)

            if 'error' in task_sla_result.data:
                print("❌ Test Failed:", task_sla_result.data)
            else:
                slas = task_sla_result.data.get('result', [])
                print(f"✅ Found {len(slas)} task SLA(s) for incident {task_sys_id}.")
                for s in slas[:3]:
                    print(f"   - SLA: {s.get('sla', {}).get('display_value', s.get('sla', 'N/A'))} | Breached: {s.get('has_breached', 'N/A')}")
        else:
            print("⚠️  No incidents found to test get_task_sla. Skipping.")

        # --- Phase 3: Test list_breached_slas ---
        print("\n" + "="*60)
        print("[Phase 3] Testing 'list_breached_slas'...")
        print("="*60)

        breached_payload = {
            "params": {
                **SERVICENOW_CREDS,
                "limit": 10,
                "offset": 0
            }
        }
        breached_result = await client.call_tool("list_breached_slas", breached_payload)

        if 'error' in breached_result.data:
            print("❌ Test Failed:", breached_result.data)
        else:
            breached = breached_result.data.get('result', [])
            print(f"✅ Found {len(breached)} breached SLA(s).")
            for b in breached[:5]:
                task_display = b.get('task', {})
                if isinstance(task_display, dict):
                    task_display = task_display.get('display_value', 'N/A')
                print(f"   - Task: {task_display} | SLA: {b.get('sla', {}).get('display_value', b.get('sla', 'N/A'))}")

        print("\n" + "="*60)
        print("All SLA management tests completed!")
        print("="*60)

if __name__ == "__main__":
    asyncio.run(main())

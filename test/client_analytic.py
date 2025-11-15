# New main function for test_client.py
import json
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
# New main function for test_client.py
import json

# New main function for test_client.py
import json

async def main():
    async with client:
        await client.ping()
        print("✅ Server is reachable.")

        print("\n" + "="*60)
        print("Testing: get_aggregate_data to count active incidents by priority...")
        print("="*60)
        
        payload = {
            "params": {
                **SERVICENOW_CREDS,
                "table_name": "incident",
                "aggregation_function": "COUNT",
                "group_by_fields": ["priority"],
                "query": "active=true"
            }
        }
        
        result = await client.call_tool("get_aggregate_data", payload)

        if isinstance(result.data, dict) and 'error' in result.data:
            print("❌ Test Failed:", result.data)
        else:
            # result.data = {'result': [...]}  (exactly what you pasted)
            stats_list = result.data.get('result', [])
            print("✅ Success! Aggregation query completed.")
            print("\n--- Active Incidents by Priority ---")
            total = 0

            priority_map = {
                '1': '1 - Critical',
                '2': '2 - High',
                '3': '3 - Moderate',
                '4': '4 - Low',
                '5': '5 - Planning'
            }

            for group in stats_list:
                priority = group.get('groupby_fields', [{}])[0].get('value', 'N/A')
                count = int(group.get('stats', {}).get('count', 0))
                total += count
                label = priority_map.get(priority, f"Unknown ({priority})")
                print(f"  - Priority {label}: {count} incidents")

            print("------------------------------------")
            print(f"  Total Active Incidents: {total}")

if __name__ == "__main__":
    asyncio.run(main())
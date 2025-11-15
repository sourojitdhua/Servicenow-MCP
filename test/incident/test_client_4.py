# for fetching the 5 most recently created, active change requests
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

        print("\nTesting: get_records_from_table...")

        # Let's get the 5 most recently created, active change requests
        payload = {
            "params": {
                **SERVICENOW_CREDS,
                "table_name": "change_request",
                "query": "active=true",
                "limit": 5,
                "sort_by": "sys_created_on",
                "sort_dir": "DESC",
                "fields": ["number", "short_description", "state", "assigned_to"]
            }
        }
        
        result = await client.call_tool("get_records_from_table", payload)
        
        if 'error' in result.data:
            print("❌ Test Failed:", result.data)
        else:
            records = result.data.get('result', [])
            print(f"✅ Success! Found {len(records)} active change requests:")
            for record in records:
                # The assigned_to field is a link/value pair, so we handle it nicely
                assignee = record.get('assigned_to', {}).get('display_value', 'Unassigned')
                print(
                    f"  - {record['number']}: {record['short_description']} "
                    f"(State: {record['state']}, Assigned to: {assignee})"
                )

if __name__ == "__main__":
    asyncio.run(main())
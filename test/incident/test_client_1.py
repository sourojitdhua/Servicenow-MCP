# New main function for test_client.py
# for fetch recent incidents
# This script tests the `list_recent_incidents` tool of the ServiceNow MCP server.
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

        print("\nTesting: list_recent_incidents...")
        
        # 1. Define the inner data payload
        test_data = {
            **SERVICENOW_CREDS,
            "limit": 5  # Ask for the 5 most recent incidents
        }
        
        # 2. Wrap it in the 'params' key
        final_payload = {
            "params": test_data
        }

        # 3. Call the tool
        result = await client.call_tool("list_recent_incidents", final_payload)
        
        # 4. Display the results nicely
        if 'error' in result.data:
            print("Error:", result.data)
        else:
            print("✅ Success! Recent Incidents:")
            for incident in result.data.get('result', []):
                print(
                    f"  - {incident['number']}: {incident['short_description']} "
                    f"(Priority: {incident['priority']}, State: {incident['state']})"
                )

if __name__ == "__main__":
    asyncio.run(main())
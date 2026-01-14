# get all tables related to 'change' in ServiceNow
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

async def main():
    async with client:
        await client.ping()
        print("✅ Server is reachable.")

        print("\nTesting: list_available_tables (with filter)...")

        # Create the payload to find tables related to 'change'
        payload = {
            "params": {
                **SERVICENOW_CREDS,
                "filter": "change" 
            }
        }
        
        result = await client.call_tool("list_available_tables", payload)
        
        if 'error' in result.data:
            print("❌ Test Failed:", result.data)
        else:
            tables = result.data.get('result', [])
            print(f"✅ Success! Found {len(tables)} tables matching 'change':")
            # Print the first 10 results
            for table in tables[:10]:
                print(f"  - Name: {table.get('name')}, Label: {table.get('label')}")

if __name__ == "__main__":
    asyncio.run(main())
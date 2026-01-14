#  it should return a list of service catalog items from your instance that contain the word "access", 
# such as "Salesforce Access" or "Developer Access
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

        print("\nTesting: list_catalog_items...")
        
        payload = {
            "params": {
                **SERVICENOW_CREDS,
                "limit": 10,
                # Let's search for items related to 'access'
                "filter_text": "access"
            }
        }
        
        result = await client.call_tool("list_catalog_items", payload)
        
        if 'error' in result.data:
            print("❌ Test Failed:", result.data)
        else:
            items = result.data.get('result', [])
            print(f"✅ Success! Found {len(items)} catalog items matching 'access':")
            for item in items:
                # Category is a link/value pair, so we get the display_value
                category_name = item.get('category', {}).get('display_value', 'No Category')
                print(
                    f"  - {item.get('name')} (Price: {item.get('price', 'N/A')}, "
                    f"Category: {category_name})"
                )

if __name__ == "__main__":
    asyncio.run(main())
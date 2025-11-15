# New main function for test_client.py
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
    "username": "",
    "password": "REDACTED_PASSWORD"
}


# New main function for test_client.py
async def main():
    async with client:
        await client.ping()
        print("✅ Server is reachable.")

        print("\nTesting: list_catalog_categories...")
        
        payload = {
            "params": {
                **SERVICENOW_CREDS,
                "limit": 10,
                "filter_text": "services"
            }
        }
        
        result = await client.call_tool("list_catalog_categories", payload)
        
        if 'error' in result.data:
            print("❌ Test Failed:", result.data)
        else:
            categories = result.data.get('result', [])
            print(f"✅ Success! Found {len(categories)} categories matching 'services':")
            for category in categories:
                # --- THE FIX IS HERE ---
                catalog_info = category.get('sc_catalog')
                catalog_name = 'N/A' # Default value
                
                # Check if the catalog_info is a dictionary and has the key we want
                if isinstance(catalog_info, dict) and 'display_value' in catalog_info:
                    catalog_name = catalog_info.get('display_value', 'N/A')
                # If it's just a string (the sys_id), we can still print it
                elif isinstance(catalog_info, str) and catalog_info:
                    catalog_name = f"(sys_id: {catalog_info})"
                
                print(
                    f"  - {category.get('title')} (Catalog: {catalog_name})"
                )

if __name__ == "__main__":
    asyncio.run(main())
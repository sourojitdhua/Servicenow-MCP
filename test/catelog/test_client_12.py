# for testing the create_catalog_category tool in ServiceNow MCP server
# This script will create a new category in the ServiceNow Service Catalog
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

        # --- Phase 1: Find the main "Service Catalog" to use as a parent ---
        print("\n[Phase 1] Finding the 'Service Catalog' sys_id...")
        
        # We need a tool to find the catalog's sys_id. Let's use our generic 'get_records_from_table' tool.
        find_catalog_payload = {
            "params": {
                **SERVICENOW_CREDS,
                "table_name": "sc_catalog",
                "query": "title=Service Catalog",
                "limit": 1,
                "fields": ["sys_id", "title"]
            }
        }
        catalog_result = await client.call_tool("get_records_from_table", find_catalog_payload)
        
        if 'error' in catalog_result.data or not catalog_result.data.get('result'):
            print("❌ Could not find the main 'Service Catalog'. Aborting test.")
            return

        service_catalog = catalog_result.data['result'][0]
        service_catalog_sys_id = service_catalog['sys_id']
        print(f"✅ Found '{service_catalog['title']}' with sys_id: {service_catalog_sys_id}")

        # --- Phase 2: Create a new category inside the Service Catalog ---
        print("\n[Phase 2] Testing 'create_catalog_category'...")
        category_title = "MCP Test - Corporate Services"
        create_payload = {
            "params": {
                **SERVICENOW_CREDS,
                "title": category_title,
                "catalog_sys_id": service_catalog_sys_id,
                "description": "A new category created by the MCP server."
            }
        }
        
        create_result = await client.call_tool("create_catalog_category", create_payload)

        if 'error' in create_result.data:
            print("❌ Test Failed:", create_result.data)
        else:
            new_category = create_result.data.get('result', {})
            print(f"✅ Success! Created new category '{new_category.get('title')}'.")
            
            # --- Phase 3: Verification ---
            retrieved_catalog_info = new_category.get('sc_catalog', {})
            retrieved_catalog_id = retrieved_catalog_info.get('value')
            
            print(f"  - New Category Sys ID: {new_category.get('sys_id')}")
            print(f"  - Parent Catalog Sys ID: {retrieved_catalog_id}")
            
            if retrieved_catalog_id == service_catalog_sys_id:
                print("✅ Verification successful: The new category is correctly assigned to the Service Catalog.")
            else:
                print("❌ Verification failed: The new category was not assigned to the correct parent catalog.")


if __name__ == "__main__":
    asyncio.run(main())
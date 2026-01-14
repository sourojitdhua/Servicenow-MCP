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
    "instance_url": "",
    "username": "admin",
    "password": ""
}


async def main():
    async with client:
        await client.ping()
        print("✅ Server is reachable.")

        # --- Phase 1: Get a list of items to find a valid sys_id ---
        print("\n[Phase 1] Finding a catalog item to test with...")
        list_payload = { "params": { **SERVICENOW_CREDS, "limit": 1 } }
        list_result = await client.call_tool("list_catalog_items", list_payload)

        if 'error' in list_result.data or not list_result.data.get('result'):
            print("❌ Could not find any catalog items to test with. Aborting.")
            return

        first_item = list_result.data['result'][0]
        item_sys_id = first_item.get('sys_id')
        item_name = first_item.get('name')
        print(f"✅ Found item '{item_name}' with sys_id: {item_sys_id}")

        # --- Phase 2: Use the new tool to get the full details ---
        print(f"\n[Phase 2] Testing 'get_catalog_item' with sys_id {item_sys_id}...")
        get_payload = {
            "params": {
                **SERVICENOW_CREDS,
                "sys_id": item_sys_id
            }
        }
        get_result = await client.call_tool("get_catalog_item", get_payload)

        if 'error' in get_result.data:
            print("❌ Test Failed:", get_result.data)
        else:
            item_details = get_result.data.get('result', {})
            retrieved_name = item_details.get('name')
            print(f"✅ Success! Retrieved details for '{retrieved_name}'.")
            
            # Verification
            if retrieved_name == item_name:
                print("✅ Verification successful: The retrieved item name matches the original.")
                print(f"   - Description: {item_details.get('short_description', 'N/A')}")
                print(f"   - Price: {item_details.get('price', 'N/A')}")
            else:
                print("❌ Verification failed: The retrieved item name does not match.")


if __name__ == "__main__":
    asyncio.run(main())
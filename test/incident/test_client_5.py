# for fetch the table schema and print it in a readable format
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

        print("\nTesting: get_table_schema for 'incident' table...")

        payload = {
            "params": {
                **SERVICENOW_CREDS,
                "table_name": "incident",
            }
        }
        
        result = await client.call_tool("get_table_schema", payload)
        
        if 'error' in result.data:
            print("❌ Test Failed:", result.data)
        else:
            fields = result.data.get('result', [])
            print(f"✅ Success! Found {len(fields)} fields in 'incident' table:")
            print("--- Sample of Schema ---")
            # Print a sample of 15 fields from the schema
            for field in fields[:15]:
                # THE FIX: Convert every value to a string using str() before formatting.
                # This handles cases where a value might be a dict or None.
                element_name = str(field.get('element', 'N/A'))
                internal_type = str(field.get('internal_type', 'N/A'))
                reference = str(field.get('reference', '')) # Get reference field, default to empty string

                field_info = f"- Field: {element_name:<25} | Type: {internal_type:<15}"
                
                # Only add the 'References' part if the reference field is not empty
                if reference and reference != "None":
                        field_info += f"| References: {reference}"
                print(field_info)
            print("------------------------")


if __name__ == "__main__":
    asyncio.run(main())
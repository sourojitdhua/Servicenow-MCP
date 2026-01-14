# For featch the ticket details by incident number
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

        # --- Test Case 1: Successful Find ---
        print("\nTesting: get_incident_by_number (Success Case)...")
        incident_to_find = 'INC0010109'  # <-- CHANGE THIS TO A REAL INCIDENT NUMBER

        success_payload = {
            "params": {
                **SERVICENOW_CREDS,
                "number": incident_to_find
            }
        }
        
        success_result = await client.call_tool("get_incident_by_number", success_payload)
        
        if 'error' in success_result.data:
            print("❌ Test Failed:", success_result.data)
        else:
            print(f"✅ Success! Found Incident {incident_to_find}:")
            # We access result.result because our tool nests the response
            incident_details = success_result.data.get('result', {})
            print(f"  - Number: {incident_details.get('number')}")
            print(f"  - Description: {incident_details.get('short_description')}")
            print(f"  - Sys ID: {incident_details.get('sys_id')}")

        # --- Test Case 2: Not Found ---
        print("\nTesting: get_incident_by_number (Not Found Case)...")
        not_found_payload = {
            "params": {
                **SERVICENOW_CREDS,
                "number": "INC9999999" # A number that does not exist
            }
        }

        not_found_result = await client.call_tool("get_incident_by_number", not_found_payload)
        if 'error' in not_found_result.data and not_found_result.data['error'] == 'Not Found':
            print("✅ Success! Correctly handled non-existent incident.")
            print(f"  - Response: {not_found_result.data}")
        else:
            print("❌ Test Failed: Did not correctly handle the 'not found' case.")
            print(f"  - Response: {not_found_result.data}")


if __name__ == "__main__":
    asyncio.run(main())
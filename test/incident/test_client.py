# For create incidents
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

        tools = await client.list_tools()
        print("\nAvailable tools:")
        for tool in tools:
            print(f"- {tool.name}")

        # --- Test Create Incident ---
        print("\nCreating incident...")
        
        # 1. This is the inner data payload, which matches the Pydantic model
        incident_data = {
            **SERVICENOW_CREDS,
            "short_description": "Network outage in Building F (Final Corrected Payload)",
            "urgency": "1",
            "impact": "1"
        }
        
        # 2. THE FIX: Wrap the inner data in a dictionary where the key
        #    matches the server function's argument name ('params').
        final_payload = {
            "params": incident_data
        }

        # 3. Pass this final, correctly structured payload to the tool call.
        create_result = await client.call_tool("create_incident", final_payload)
        print("Create incident result:", create_result.data)
        
        incident_sys_id = create_result.data.get("result", {}).get("sys_id")

        if incident_sys_id:
            # --- Test Get Incident ---
            print(f"\nGetting incident {incident_sys_id}...")

            # Apply the same pattern here
            get_incident_data = {
                **SERVICENOW_CREDS,
                "sys_id": incident_sys_id
            }
            get_final_payload = {
                "params": get_incident_data
            }

            get_result = await client.call_tool("get_incident", get_final_payload)
            print("Get incident result:", get_result.data)

if __name__ == "__main__":
    asyncio.run(main())
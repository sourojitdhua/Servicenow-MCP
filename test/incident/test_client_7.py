# for fetching incidents by a unique keyword
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

        # --- Phase 1: Create a searchable incident ---
        print("\n[Phase 1] Creating an incident with a unique keyword...")
        unique_keyword = "Project Phoenix"
        create_data = {
            "params": {
                **SERVICENOW_CREDS,
                "short_description": f"Critical issue with {unique_keyword} server.",
                "description": "The primary application server for Phoenix is unresponsive."
            }
        }
        create_result = await client.call_tool("create_incident", create_data)
        
        if 'error' in create_result.data:
            print("❌ Could not create incident to test with. Aborting.")
            print(create_result.data)
            return
        
        incident_number = create_result.data.get('result', {}).get('number')
        print(f"✅ Created incident {incident_number} containing the keyword '{unique_keyword}'.")
        print("Waiting a moment for ServiceNow to index the new record...")
        await asyncio.sleep(5) # Give ServiceNow a few seconds to index the new text

        # --- Phase 2: Search for the incident using the new tool ---
        print(f"\n[Phase 2] Searching for '{unique_keyword}' in the incident table...")
        search_data = {
            "params": {
                **SERVICENOW_CREDS,
                "table_name": "incident",
                "search_term": unique_keyword
            }
        }
        search_result = await client.call_tool("search_records_by_text", search_data)

        if 'error' in search_result.data:
            print(f"❌ Search failed:", search_result.data)
            return

        found_records = search_result.data.get('result', [])
        
        print(f"✅ Search tool returned {len(found_records)} record(s).")

        if not found_records:
            print("\n❌ Verification failed! The search did not find the newly created incident.")
            print("   (Note: Text indexing on dev instances can sometimes be slow or disabled.)")
        else:
            # Check if our specific incident is in the results
            found_it = any(rec.get('number') == incident_number for rec in found_records)
            if found_it:
                print(f"\n✅ Verification successful! Found incident {incident_number} in search results.")
            else:
                print(f"\n❌ Verification failed! The search results did not contain incident {incident_number}.")


if __name__ == "__main__":
    asyncio.run(main())
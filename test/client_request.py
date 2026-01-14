# New main function for test_client.py to test all request management tools
import asyncio
import base64
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


# New main function for test_client.py to test all request ticket tools
import asyncio
import base64

async def main():
    async with client:
        await client.ping()
        print("✅ Server is reachable.")

        request_sys_id = None
        request_number = None

        try:
            # --- Phase 1: Test create_request_ticket ---
            print("\n" + "="*60)
            print("[Phase 1] Testing 'create_request_ticket'...")
            print("="*60)
            req_desc = "MCP Test - New Monitor Request"
            
            create_payload = {
                "params": {
                    **SERVICENOW_CREDS,
                    "short_description": req_desc,
                    "description": "User requests a new 27-inch monitor for their workstation."
                }
            }
            create_result = await client.call_tool("create_request_ticket", create_payload)
            if 'error' in create_result.data: print(f"❌ Request creation failed: {create_result.data}"); return
            
            request = create_result.data.get('result', {})
            request_sys_id = request.get('sys_id')
            request_number = request.get('number')
            print(f"✅ Success! Created request '{request_number}' with sys_id: {request_sys_id}")

            # --- Phase 2: Test get_request_ticket and list_request_tickets ---
            print("\n" + "="*60)
            print("[Phase 2] Testing 'get_request_ticket' and 'list_request_tickets'...")
            print("="*60)
            
            get_req_payload = {"params": {**SERVICENOW_CREDS, "number": request_number}}
            get_req_result = await client.call_tool("get_request_ticket", get_req_payload)
            if 'error' in get_req_result.data: print(f"❌ Get Request failed: {get_req_result.data}"); return
            print(f"✅ Successfully retrieved Request {request_number} by number.")
            
            list_req_payload = {"params": {**SERVICENOW_CREDS, "active": True, "limit": 10}}
            list_req_result = await client.call_tool("list_request_tickets", list_req_payload)
            found_it = any(r.get('sys_id') == request_sys_id for r in list_req_result.data.get('result', []))
            print(f"✅ Verification successful: Found request {request_number} in the active list." if found_it else f"❌ Verification failed: Did not find {request_number} in the list.")

            # --- Phase 3: Test add_comment_to_request ---
            print("\n" + "="*60)
            print("[Phase 3] Testing 'add_comment_to_request'...")
            print("="*60)
            comment_payload = {"params": {**SERVICENOW_CREDS, "sys_id": request_sys_id, "comment": "MCP Test: Adding a comment to the request."}}
            comment_result = await client.call_tool("add_comment_to_request", comment_payload)
            if 'error' in comment_result.data: print(f"❌ Add comment failed: {comment_result.data}"); return
            print("✅ Successfully added comment to request.")
            
            # --- Phase 4: Test attach_file_to_record ---
            print("\n" + "="*60)
            print("[Phase 4] Testing 'attach_file_to_record'...")
            print("="*60)
            file_content = "This is a dummy quote for the monitor request."
            file_content_b64 = base64.b64encode(file_content.encode('utf-8')).decode('utf-8')
            
            attach_payload = {
                "params": {
                    **SERVICENOW_CREDS,
                    "table_name": "sc_request", # Attaching to the request table
                    "record_sys_id": request_sys_id,
                    "file_name": "monitor_quote.txt",
                    "file_content_base64": file_content_b64
                }
            }
            attach_result = await client.call_tool("attach_file_to_record", attach_payload)
            if 'error' in attach_result.data: print(f"❌ Attachment failed: {attach_result.data}"); return
            
            attachment_sys_id = attach_result.data.get('result', {}).get('sys_id')
            print(f"✅ Success! Attached file with attachment sys_id: {attachment_sys_id}")

            # Verify attachment exists
            verify_attach_payload = {"params": {**SERVICENOW_CREDS, "table_name": "sys_attachment", "query": f"sys_id={attachment_sys_id}", "limit": 1}}
            verify_attach_result = await client.call_tool("get_records_from_table", verify_attach_payload)
            if verify_attach_result.data.get('result'):
                print("✅ Verification successful: Attachment record was found.")
            else:
                print("❌ Verification failed: Attachment record not found.")

        finally:
            print("\n" + "="*60)
            print("[Cleanup] NOTE: Manual cleanup of Request may be needed.")
            print(f"  - Request Sys ID: {request_sys_id}, Number: {request_number}")
            print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
# Test script for the 7 previously untested Service Catalog tools:
#   create_catalog, list_catalogs, create_catalog_item_variable,
#   list_catalog_item_variables, update_catalog_item_variable,
#   update_catalog_category, move_catalog_items
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

        catalog_sys_id = None
        category_sys_id = None
        category2_sys_id = None
        item_sys_id = None
        variable_sys_id = None

        try:
            # --- Phase 1: Test create_catalog ---
            print("\n" + "="*60)
            print("[Phase 1] Testing 'create_catalog'...")
            print("="*60)

            create_catalog_payload = {
                "params": {
                    **SERVICENOW_CREDS,
                    "title": "MCP Test Catalog",
                    "description": "A test catalog created by the MCP test suite."
                }
            }
            create_catalog_result = await client.call_tool("create_catalog", create_catalog_payload)

            if 'error' in create_catalog_result.data:
                print("❌ Test Failed:", create_catalog_result.data)
                return
            catalog = create_catalog_result.data.get('result', {})
            catalog_sys_id = catalog.get('sys_id')
            print(f"✅ Created catalog '{catalog.get('title', 'N/A')}' (sys_id: {catalog_sys_id})")

            # --- Phase 2: Test list_catalogs ---
            print("\n" + "="*60)
            print("[Phase 2] Testing 'list_catalogs'...")
            print("="*60)

            list_catalogs_payload = {
                "params": {
                    **SERVICENOW_CREDS,
                    "limit": 20,
                    "filter_text": "MCP Test Catalog"
                }
            }
            list_catalogs_result = await client.call_tool("list_catalogs", list_catalogs_payload)

            if 'error' in list_catalogs_result.data:
                print("❌ Test Failed:", list_catalogs_result.data)
            else:
                catalogs = list_catalogs_result.data.get('result', [])
                print(f"✅ Found {len(catalogs)} catalog(s) matching 'MCP Test Catalog'.")
                found = any(c.get('sys_id') == catalog_sys_id for c in catalogs)
                if found:
                    print("✅ Verification: Our newly created catalog is in the list.")
                else:
                    print("⚠️  Our test catalog was not found in the filtered list.")

            # --- Phase 3: Create two categories for move_catalog_items test ---
            print("\n" + "="*60)
            print("[Phase 3] Creating two categories for later tests...")
            print("="*60)

            for idx, cat_title in enumerate(["MCP Test Category A", "MCP Test Category B"], 1):
                cat_payload = {
                    "params": {
                        **SERVICENOW_CREDS,
                        "title": cat_title,
                        "catalog_sys_id": catalog_sys_id,
                        "description": f"Test category {idx} for MCP test suite."
                    }
                }
                cat_result = await client.call_tool("create_catalog_category", cat_payload)
                if 'error' in cat_result.data:
                    print(f"❌ Failed to create category {idx}:", cat_result.data)
                else:
                    cat = cat_result.data.get('result', {})
                    sid = cat.get('sys_id')
                    if idx == 1:
                        category_sys_id = sid
                    else:
                        category2_sys_id = sid
                    print(f"✅ Created category '{cat_title}' (sys_id: {sid})")

            # --- Phase 4: Test update_catalog_category ---
            print("\n" + "="*60)
            print("[Phase 4] Testing 'update_catalog_category'...")
            print("="*60)

            if category_sys_id:
                update_cat_payload = {
                    "params": {
                        **SERVICENOW_CREDS,
                        "sys_id": category_sys_id,
                        "title": "MCP Test Category A (Updated)",
                        "description": "Updated description by MCP test suite."
                    }
                }
                update_cat_result = await client.call_tool("update_catalog_category", update_cat_payload)

                if 'error' in update_cat_result.data:
                    print("❌ Test Failed:", update_cat_result.data)
                else:
                    updated_cat = update_cat_result.data.get('result', {})
                    print(f"✅ Updated category title to: '{updated_cat.get('title', 'N/A')}'")
            else:
                print("⚠️  No category created. Skipping update_catalog_category test.")

            # --- Phase 5: Create a catalog item for variable tests ---
            # We need an existing catalog item. Create one via generic create_record.
            print("\n" + "="*60)
            print("[Phase 5] Creating a catalog item for variable tests...")
            print("="*60)

            create_item_payload = {
                "params": {
                    **SERVICENOW_CREDS,
                    "table_name": "sc_cat_item",
                    "data": {
                        "name": "MCP Test Catalog Item",
                        "short_description": "A test item for variable testing.",
                        "category": category_sys_id or "",
                        "sc_catalogs": catalog_sys_id or ""
                    }
                }
            }
            create_item_result = await client.call_tool("create_record", create_item_payload)

            if 'error' in create_item_result.data:
                print("❌ Failed to create catalog item:", create_item_result.data)
            else:
                item = create_item_result.data.get('result', {})
                item_sys_id = item.get('sys_id')
                print(f"✅ Created catalog item (sys_id: {item_sys_id})")

            # --- Phase 6: Test create_catalog_item_variable ---
            print("\n" + "="*60)
            print("[Phase 6] Testing 'create_catalog_item_variable'...")
            print("="*60)

            if item_sys_id:
                create_var_payload = {
                    "params": {
                        **SERVICENOW_CREDS,
                        "item_sys_id": item_sys_id,
                        "name": "mcp_test_justification",
                        "question_text": "Please provide a business justification",
                        "type": "6",
                        "order": 100,
                        "mandatory": True
                    }
                }
                create_var_result = await client.call_tool("create_catalog_item_variable", create_var_payload)

                if 'error' in create_var_result.data:
                    print("❌ Test Failed:", create_var_result.data)
                else:
                    var = create_var_result.data.get('result', {})
                    variable_sys_id = var.get('sys_id')
                    print(f"✅ Created variable '{var.get('name', 'N/A')}' (sys_id: {variable_sys_id})")
            else:
                print("⚠️  No catalog item created. Skipping variable tests.")

            # --- Phase 7: Test list_catalog_item_variables ---
            print("\n" + "="*60)
            print("[Phase 7] Testing 'list_catalog_item_variables'...")
            print("="*60)

            if item_sys_id:
                list_vars_payload = {
                    "params": {
                        **SERVICENOW_CREDS,
                        "item_sys_id": item_sys_id
                    }
                }
                list_vars_result = await client.call_tool("list_catalog_item_variables", list_vars_payload)

                if 'error' in list_vars_result.data:
                    print("❌ Test Failed:", list_vars_result.data)
                else:
                    variables = list_vars_result.data.get('result', [])
                    print(f"✅ Found {len(variables)} variable(s) for the catalog item.")
                    for v in variables:
                        print(f"   - {v.get('name', 'N/A')} (type: {v.get('type', 'N/A')}, mandatory: {v.get('mandatory', 'N/A')})")
            else:
                print("⚠️  No catalog item. Skipping list_catalog_item_variables test.")

            # --- Phase 8: Test update_catalog_item_variable ---
            print("\n" + "="*60)
            print("[Phase 8] Testing 'update_catalog_item_variable'...")
            print("="*60)

            if variable_sys_id:
                update_var_payload = {
                    "params": {
                        **SERVICENOW_CREDS,
                        "variable_sys_id": variable_sys_id,
                        "question_text": "Business justification (UPDATED by MCP test)",
                        "order": 50,
                        "mandatory": False
                    }
                }
                update_var_result = await client.call_tool("update_catalog_item_variable", update_var_payload)

                if 'error' in update_var_result.data:
                    print("❌ Test Failed:", update_var_result.data)
                else:
                    updated_var = update_var_result.data.get('result', {})
                    print(f"✅ Updated variable question_text to: '{updated_var.get('question_text', 'N/A')}'")
                    print(f"   order: {updated_var.get('order', 'N/A')}, mandatory: {updated_var.get('mandatory', 'N/A')}")
            else:
                print("⚠️  No variable created. Skipping update_catalog_item_variable test.")

            # --- Phase 9: Test move_catalog_items ---
            print("\n" + "="*60)
            print("[Phase 9] Testing 'move_catalog_items'...")
            print("="*60)

            if item_sys_id and category2_sys_id:
                move_payload = {
                    "params": {
                        **SERVICENOW_CREDS,
                        "destination_category_sys_id": category2_sys_id,
                        "item_sys_ids": [item_sys_id]
                    }
                }
                move_result = await client.call_tool("move_catalog_items", move_payload)

                if 'error' in move_result.data:
                    print("❌ Test Failed:", move_result.data)
                else:
                    print(f"✅ Moved catalog item to category B (sys_id: {category2_sys_id})")
            else:
                print("⚠️  Missing item or second category. Skipping move_catalog_items test.")

        finally:
            # --- Cleanup ---
            print("\n" + "="*60)
            print("[Cleanup] Removing test records...")
            print("="*60)

            # Delete variable
            if variable_sys_id:
                r = await client.call_tool("delete_record", {"params": {**SERVICENOW_CREDS, "table_name": "item_option_new", "sys_id": variable_sys_id}})
                if 'error' in r.data:
                    print(f"❌ Failed to clean up variable {variable_sys_id}")
                else:
                    print(f"✅ Cleaned up variable {variable_sys_id}")

            # Delete catalog item
            if item_sys_id:
                r = await client.call_tool("delete_record", {"params": {**SERVICENOW_CREDS, "table_name": "sc_cat_item", "sys_id": item_sys_id}})
                if 'error' in r.data:
                    print(f"❌ Failed to clean up catalog item {item_sys_id}")
                else:
                    print(f"✅ Cleaned up catalog item {item_sys_id}")

            # Delete categories
            for sid in [category_sys_id, category2_sys_id]:
                if sid:
                    r = await client.call_tool("delete_record", {"params": {**SERVICENOW_CREDS, "table_name": "sc_category", "sys_id": sid}})
                    if 'error' in r.data:
                        print(f"❌ Failed to clean up category {sid}")
                    else:
                        print(f"✅ Cleaned up category {sid}")

            # Delete catalog
            if catalog_sys_id:
                r = await client.call_tool("delete_record", {"params": {**SERVICENOW_CREDS, "table_name": "sc_catalog", "sys_id": catalog_sys_id}})
                if 'error' in r.data:
                    print(f"❌ Failed to clean up catalog {catalog_sys_id}")
                else:
                    print(f"✅ Cleaned up catalog {catalog_sys_id}")

        print("\n" + "="*60)
        print("All Service Catalog tests completed!")
        print("="*60)

if __name__ == "__main__":
    asyncio.run(main())

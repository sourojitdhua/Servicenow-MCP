# New main function for test_client.py to test all knowledge base tools
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

        kb_sys_id = None
        category_sys_id = None
        article_sys_id = None

        try:
            # --- Phase 1: Test create_knowledge_base & list_knowledge_bases ---
            print("\n" + "="*60)
            print("[Phase 1] Testing 'create_knowledge_base' and 'list_knowledge_bases'...")
            print("="*60)
            kb_title = "MCP Test KB 2 - HR Policies"
            create_kb_payload = {"params": {**SERVICENOW_CREDS, "title": kb_title}}
            create_kb_result = await client.call_tool("create_knowledge_base", create_kb_payload)
            if 'error' in create_kb_result.data:
                print("❌ KB creation failed:", create_kb_result.data); return
            
            kb_sys_id = create_kb_result.data['result']['sys_id']
            print(f"✅ Created KB '{kb_title}' with sys_id: {kb_sys_id}")

            list_kb_payload = {"params": {**SERVICENOW_CREDS, "title_filter": "MCP Test KB"}}
            list_kb_result = await client.call_tool("list_knowledge_bases", list_kb_payload)
            found_it = any(kb.get('sys_id') == kb_sys_id for kb in list_kb_result.data.get('result', []))
            print("✅ 'list_knowledge_bases' test successful." if found_it else "❌ 'list_knowledge_bases' verification failed.")

            # --- Phase 2: Test create_category ---
            print("\n" + "="*60)
            print("[Phase 2] Testing 'create_category'...")
            print("="*60)
            category_name = "Expense Reports"
            create_cat_payload = {"params": {**SERVICENOW_CREDS, "knowledge_base_sys_id": kb_sys_id, "name": category_name}}
            create_cat_result = await client.call_tool("create_category", create_cat_payload)
            if 'error' in create_cat_result.data:
                print("❌ Category creation failed:", create_cat_result.data); return
            
            category_sys_id = create_cat_result.data['result']['sys_id']
            print(f"✅ Created category '{category_name}' with sys_id: {category_sys_id}")

            # --- Phase 3: Test create_article & get_article ---
            print("\n" + "="*60)
            print("[Phase 3] Testing 'create_article' and 'get_article'...")
            print("="*60)
            article_title = "How to submit an expense report"
            article_content = "<p>All expense reports must be submitted via the portal.</p>"
            create_article_payload = {"params": {**SERVICENOW_CREDS, "knowledge_base_sys_id": kb_sys_id, "category_sys_id": category_sys_id, "title": article_title, "content": article_content}}
            create_article_result = await client.call_tool("create_article", create_article_payload)
            if 'error' in create_article_result.data:
                print("❌ Article creation failed:", create_article_result.data); return
                
            article_sys_id = create_article_result.data['result']['sys_id']
            print(f"✅ Created article '{article_title}' with sys_id: {article_sys_id}")

            get_article_payload = {"params": {**SERVICENOW_CREDS, "sys_id": article_sys_id}}
            get_article_result = await client.call_tool("get_article", get_article_payload)
            retrieved_title = get_article_result.data.get('result', {}).get('short_description')
            print(f"✅ 'get_article' successful. Retrieved title: '{retrieved_title}'")

            # --- Phase 4: Test update_article, publish_article, and list_articles ---
            print("\n" + "="*60)
            print("[Phase 4] Testing 'update_article', 'publish_article', and 'list_articles'...")
            print("="*60)
            updated_content = "<p>UPDATED - All expense reports must be submitted via the online portal with manager approval.</p>"
            update_payload = {"params": {**SERVICENOW_CREDS, "sys_id": article_sys_id, "content": updated_content}}
            await client.call_tool("update_article", update_payload)
            print("✅ 'update_article' call successful.")

            publish_payload = {"params": {**SERVICENOW_CREDS, "sys_id": article_sys_id}}
            await client.call_tool("publish_article", publish_payload)
            print("✅ 'publish_article' call successful.")

            # THE FIX: Wait a few seconds for the background publishing workflow to complete.
            print("   Waiting for publishing workflow to run...")
            await asyncio.sleep(5)

            list_articles_payload = {"params": {**SERVICENOW_CREDS, "knowledge_base_sys_id": kb_sys_id, "published_only": True}}
            list_articles_result = await client.call_tool("list_articles", list_articles_payload)
            found_published = any(a.get('sys_id') == article_sys_id for a in list_articles_result.data.get('result', []))
            
            if found_published:
                print("✅ 'list_articles' (published only) successful. Found the published article.")
            else:
                print("❌ 'list_articles' (published only) failed. The article was not found after the delay.")

        finally:
            # --- Cleanup Phase ---
            print("\n" + "="*60)
            print("[Cleanup] NOTE: Manual cleanup of KB, category, and article may be needed.")
            print(f"  - KB Sys ID: {kb_sys_id}")
            print(f"  - Category Sys ID: {category_sys_id}")
            print(f"  - Article Sys ID: {article_sys_id}")
            print("="*60)

if __name__ == "__main__":
    asyncio.run(main())
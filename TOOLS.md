# ServiceNow MCP Server — Tool Reference

**106 tools** across 19 modules. Version 0.2.0.

---

## Incident Management (9 tools)

| # | Tool | Description |
|---|------|-------------|
| 1 | `create_incident` | Creates a new incident. |
| 2 | `get_incident` | Retrieves the full details of a single incident by its unique sys_id. |
| 3 | `list_incidents` | Lists incidents based on a query, with support for pagination and field selection. |
| 4 | `update_incident` | Updates one or more fields on an existing incident record. |
| 5 | `add_comment_to_incident` | Adds a customer-visible comment to an existing incident. |
| 6 | `add_work_notes_to_incident` | Adds internal work notes to an existing incident. |
| 7 | `resolve_incident` | Resolves an incident by setting its state to 'Resolved' and adding resolution notes. |
| 8 | `list_recent_incidents` | Fetches a list of the most recently created incidents. |
| 9 | `get_incident_by_number` | Finds and retrieves a single incident by its number (e.g., 'INC0010107'). |

## Change Management (8 tools)

| # | Tool | Description |
|---|------|-------------|
| 10 | `create_change_request` | Creates a new Normal, Standard, or Emergency change request. |
| 11 | `update_change_request` | Updates one or more fields on an existing change request. |
| 12 | `list_change_requests` | Lists change requests with optional filtering and pagination. |
| 13 | `get_change_request_details` | Retrieves the full details of a single change request by its sys_id or number. |
| 14 | `add_change_task` | Adds a new task to an existing change request. |
| 15 | `submit_change_for_approval` | Submits a change request for approval by setting its state to 'Assess'. |
| 16 | `approve_change` | Approves a change request by finding and updating the approval record. |
| 17 | `reject_change` | Rejects a change request by finding and updating the approval record. |

## Problem Management (5 tools)

| # | Tool | Description |
|---|------|-------------|
| 18 | `create_problem` | Creates a new problem record in ServiceNow. |
| 19 | `update_problem` | Updates one or more fields on an existing problem record. |
| 20 | `list_problems` | Lists problem records with optional filtering and pagination. |
| 21 | `get_problem` | Retrieves the full details of a single problem record by its sys_id. |
| 22 | `create_known_error` | Marks an existing problem as a Known Error and sets the workaround. |

## Service Catalog (11 tools)

| # | Tool | Description |
|---|------|-------------|
| 23 | `create_catalog` | Creates a new, top-level service catalog. |
| 24 | `list_catalogs` | Lists the available service catalogs in the instance. |
| 25 | `list_catalog_items` | Lists available items from the Service Catalog. |
| 26 | `get_catalog_item` | Retrieves the full details for a specific service catalog item. |
| 27 | `list_catalog_categories` | Lists categories within the Service Catalog. |
| 28 | `create_catalog_category` | Creates a new category within a specified Service Catalog. |
| 29 | `update_catalog_category` | Updates an existing service catalog category's title or description. |
| 30 | `move_catalog_items` | Moves one or more service catalog items to a new category. |
| 31 | `create_catalog_item_variable` | Creates a new variable (question/field) on a catalog item's form. |
| 32 | `list_catalog_item_variables` | Lists all the variables for a specific service catalog item. |
| 33 | `update_catalog_item_variable` | Updates an existing variable on a service catalog item's form. |

## Request Management (5 tools)

| # | Tool | Description |
|---|------|-------------|
| 34 | `create_request_ticket` | Creates a new, simple service request ticket (sc_request). |
| 35 | `get_request_ticket` | Retrieves the details of a specific request ticket by sys_id or number. |
| 36 | `list_request_tickets` | Lists request tickets with optional filters. |
| 37 | `add_comment_to_request` | Adds a customer-visible comment to a request ticket. |
| 38 | `attach_file_to_record` | Attaches a Base64-encoded file to any record in ServiceNow. |

## CMDB Management (6 tools)

| # | Tool | Description |
|---|------|-------------|
| 39 | `list_ci_classes` | Lists CMDB CI classes by querying sys_db_object filtered for CMDB tables. |
| 40 | `get_ci` | Retrieves the full details of a single Configuration Item by its sys_id. |
| 41 | `list_cis` | Lists Configuration Items from a CMDB class table with query and pagination. |
| 42 | `create_ci` | Creates a new Configuration Item in the specified CMDB class table. |
| 43 | `update_ci` | Updates an existing Configuration Item in the specified CMDB class table. |
| 44 | `get_ci_relationships` | Retrieves all relationships for a CI (both parent and child). |

## SLA Management (3 tools)

| # | Tool | Description |
|---|------|-------------|
| 45 | `list_sla_definitions` | Lists SLA definitions from the contract_sla table. |
| 46 | `get_task_sla` | Retrieves SLA records attached to a specific task. |
| 47 | `list_breached_slas` | Lists task SLA records that have been breached. |

## User Management (9 tools)

| # | Tool | Description |
|---|------|-------------|
| 48 | `create_user` | Creates a new user record. |
| 49 | `update_user` | Updates an existing user record. |
| 50 | `get_user` | Retrieves a single user by sys_id, user_name, or email. |
| 51 | `list_users` | Lists users with optional filters. |
| 52 | `create_group` | Creates a new group. |
| 53 | `update_group` | Updates an existing group. |
| 54 | `add_group_members` | Adds multiple users to a group. |
| 55 | `remove_group_members` | Removes multiple users from a group. |
| 56 | `list_groups` | Lists groups with optional filters. |

## Knowledge Base Management (8 tools)

| # | Tool | Description |
|---|------|-------------|
| 57 | `create_knowledge_base` | Creates a new Knowledge Base. |
| 58 | `list_knowledge_bases` | Lists knowledge bases with optional title filter. |
| 59 | `create_category` | Creates a new category inside a Knowledge Base. |
| 60 | `create_article` | Creates a new knowledge article. |
| 61 | `update_article` | Updates an existing knowledge article. |
| 62 | `publish_article` | Publishes a knowledge article (sets workflow_state to 'published'). |
| 63 | `list_articles` | Lists knowledge articles with optional filters. |
| 64 | `get_article` | Retrieves a single knowledge article by sys_id. |

## Agile — Stories (5 tools)

| # | Tool | Description |
|---|------|-------------|
| 65 | `create_story` | Creates a new user story in the Agile Development 2.0 module. |
| 66 | `update_story` | Updates an existing user story. |
| 67 | `list_stories` | Lists user stories with optional filtering and pagination. |
| 68 | `create_story_dependency` | Creates a dependency relationship between two user stories. |
| 69 | `delete_story_dependency` | Deletes an existing dependency relationship between user stories. |

## Agile — Epics (3 tools)

| # | Tool | Description |
|---|------|-------------|
| 70 | `create_epic` | Creates a new epic in the Agile Development 2.0 module. |
| 71 | `update_epic` | Updates an existing epic. |
| 72 | `list_epics` | Lists epics from ServiceNow with filtering options. |

## Agile — Scrum Tasks (3 tools)

| # | Tool | Description |
|---|------|-------------|
| 73 | `create_scrum_task` | Creates a new scrum task and associates it with a parent story. |
| 74 | `update_scrum_task` | Updates an existing scrum task. |
| 75 | `list_scrum_tasks` | Lists scrum tasks with optional filters. |

## Project Management (3 tools)

| # | Tool | Description |
|---|------|-------------|
| 76 | `create_project` | Creates a new project. |
| 77 | `update_project` | Updates an existing project. |
| 78 | `list_projects` | Lists projects with optional filters. |

## Workflow Management (5 tools)

| # | Tool | Description |
|---|------|-------------|
| 79 | `list_workflows` | Lists workflow definitions, with options to filter by name or table. |
| 80 | `get_workflow` | Retrieves a single workflow definition by sys_id. |
| 81 | `create_workflow` | Creates a new workflow definition. |
| 82 | `update_workflow` | Updates an existing workflow definition. |
| 83 | `delete_workflow` | Deletes a workflow definition from ServiceNow. |

## Script Include Management (5 tools)

| # | Tool | Description |
|---|------|-------------|
| 84 | `list_script_includes` | Lists Script Includes, with options to filter by name or API name. |
| 85 | `get_script_include` | Retrieves a single Script Include by sys_id. |
| 86 | `create_script_include` | Creates a new Script Include in ServiceNow. |
| 87 | `update_script_include` | Updates an existing Script Include. |
| 88 | `delete_script_include` | Deletes a Script Include from ServiceNow. |

## Update Set / Changeset Management (7 tools)

| # | Tool | Description |
|---|------|-------------|
| 89 | `list_changesets` | Lists local Update Sets (Changesets), with options to filter. |
| 90 | `get_changeset_details` | Retrieves full details for a single changeset. |
| 91 | `create_changeset` | Creates a new local Update Set (changeset). |
| 92 | `update_changeset` | Updates an existing changeset (name or description). |
| 93 | `commit_changeset` | Marks a changeset as complete. |
| 94 | `publish_changeset` | Publishes a completed changeset for retrieval by remote instances. |
| 95 | `add_file_to_changeset` | Adds (tracks) a configuration record inside the specified changeset. |

## UI Policy Management (2 tools)

| # | Tool | Description |
|---|------|-------------|
| 96 | `create_ui_policy` | Creates a new UI Policy. |
| 97 | `create_ui_policy_action` | Creates a UI Policy Action that controls the state of a catalog variable. |

## Table Management & Generic CRUD (8 tools)

| # | Tool | Description |
|---|------|-------------|
| 98 | `list_available_tables` | Lists tables in the instance by querying sys_db_object. |
| 99 | `get_records_from_table` | Retrieves records from any table with filtering, sorting, and pagination. |
| 100 | `get_table_schema` | Retrieves the schema (columns, types) for a specific table. |
| 101 | `search_records_by_text` | Searches common text fields of a table using a LIKE query. |
| 102 | `create_record` | Creates a new record in any specified ServiceNow table. |
| 103 | `update_record` | Updates an existing record in any specified ServiceNow table. |
| 104 | `delete_record` | Deletes a record from any specified ServiceNow table. |
| 105 | `batch_update_records` | Updates multiple records in a table with the same data. |

## Analytics (1 tool)

| # | Tool | Description |
|---|------|-------------|
| 106 | `get_aggregate_data` | Performs an aggregation (COUNT, AVG, SUM, etc.) on a table, with optional grouping. |

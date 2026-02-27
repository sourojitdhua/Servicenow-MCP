# Changelog

All notable changes to the ServiceNow MCP Server will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2026-02-27

### Added
- **Lifespan management**: Shared `ServiceNowClient` HTTP connection opened once at startup, reused across all tool calls (eliminates per-call TCP overhead)
- **Tool tags**: Every tool tagged by module (`incident`, `change`, `cmdb`, `catalog`, `kb`, `user`, `problem`, `sla`, `request`, `agile`, `project`, `workflow`, `script_include`, `update_set`, `table`, `analytics`, `ui_policy`) and operation type (`read`, `write`, `delete`)
- **Tool annotations**: `ToolAnnotations` on all tools (`readOnlyHint`, `destructiveHint`, `idempotentHint`) so MCP clients can distinguish safe vs. destructive operations
- **`@snow_tool` decorator**: Centralized error handling — catches `ServiceNowError` and raises `ToolError` with `isError=true` in MCP responses
- **Middleware**: `LoggingMiddleware`, `TimingMiddleware`, `ErrorHandlingMiddleware` for cross-cutting observability
- **Prompt templates**: 5 workflow prompts — `triage_incident`, `create_change_workflow`, `investigate_ci_impact`, `onboard_user`, `weekly_incident_report`
- **Context injection**: Progress reporting via `ctx.report_progress()` in batch tools (`batch_update_records`, `add_group_members`, `remove_group_members`, `move_catalog_items`)
- **MCP resources**: Server info resource (`mcp://servicenow`) and entity lookup resources for incidents, KB articles, changes, users, and CMDB CIs
- **Server instructions**: LLM-facing instructions for tool usage guidance
- New `tool_annotations.py`, `tool_utils.py`, and `prompts.py` modules

### Changed
- `fastmcp` dependency bumped from `>=2.1.0` to `>=3.0.0`
- `BaseToolParams` no longer accepts credential fields — credentials managed at server lifespan level
- All 106 tool functions simplified: removed ~320 lines of duplicated `try/except ServiceNowError` boilerplate
- `get_client()` now returns shared lifespan client or falls back to per-call client creation

### Fixed
- Resource endpoint paths missing leading `/` (e.g., `api/now/table/...` → `/api/now/table/...`)
- `get_incident_by_number` resource used wrong query parameter (`number=X` → `sysparm_query=number=X`)
- `ORDERBYASC` sort syntax in `get_records_from_table` (invalid ServiceNow syntax → correct `ORDERBY`/`ORDERBYDESC`)
- `add_group_members`/`remove_group_members` — single failure no longer aborts entire batch
- `attach_file_to_record` base64 error now raises `ToolError` instead of returning error dict
- `send_request`/`send_raw_request` — added `JSONDecodeError` handling for non-JSON responses
- Removed unused imports across 9+ tool modules

## [0.2.1] - 2026-02-03

### Added
- Workflow Management module (5 tools): `list_workflows`, `get_workflow`, `create_workflow`, `update_workflow`, `delete_workflow`
- Script Include Management module (5 tools): `list_script_includes`, `get_script_include`, `create_script_include`, `update_script_include`, `delete_script_include`
- Update Set Management module (7 tools): `list_update_sets`, `get_update_set_details`, `create_update_set`, `update_update_set`, `commit_update_set`, `publish_update_set`, `add_file_to_update_set`
- UI Policy Management module (2 tools): `create_ui_policy`, `create_ui_policy_action`
- Analytics module (1 tool): `get_aggregate_data` with COUNT, AVG, SUM, MIN, MAX and group-by support
- Generic table tools: `create_record`, `update_record`, `delete_record`, `batch_update_records`, `search_records_by_text`
- Additional incident tools: `add_comment_to_incident`, `add_work_notes_to_incident`, `list_recent_incidents`, `get_incident_by_number`
- Additional change tools: `add_change_task`, `submit_change_for_approval`, `approve_change`, `reject_change`
- Additional user tools: `update_user`, `create_group`, `update_group`, `add_group_members`, `remove_group_members`
- Additional catalog tools: `create_catalog`, `create_catalog_category`, `update_catalog_category`, `move_catalog_items`, `create_catalog_item_variable`, `list_catalog_item_variables`, `update_catalog_item_variable`
- `attach_file_to_record` for file uploads to any ServiceNow record
- Example scripts for direct MCP tool usage

### Changed
- Tool count expanded from 72 to 106 with full coverage of platform capabilities
- Improved query building for ServiceNow encoded queries across all list tools

### Fixed
- `update_epic` HTTP method changed from PUT to PATCH for partial update consistency
- `submit_change_for_approval` uses `ChangeState.ASSESS` instead of magic string "-4"
- `resolve_incident` uses `IncidentState.RESOLVED` instead of magic string "6"

## [0.2.0] - 2026-01-14

### Added
- CMDB Management module (6 tools): `list_ci_classes`, `get_ci`, `list_cis`, `create_ci`, `update_ci`, `get_ci_relationships`
- Problem Management module (5 tools): `create_problem`, `update_problem`, `list_problems`, `get_problem`, `create_known_error`
- SLA Management module (3 tools): `list_sla_definitions`, `get_task_sla`, `list_breached_slas`
- Service Catalog module (4 tools): `list_catalogs`, `list_catalog_items`, `get_catalog_item`, `list_catalog_categories`
- Request Management module (3 tools): `create_request_ticket`, `get_request_ticket`, `list_request_tickets`
- Knowledge Base module (8 tools): `create_knowledge_base`, `list_knowledge_bases`, `create_kb_category`, `create_kb_article`, `update_kb_article`, `publish_kb_article`, `list_kb_articles`, `get_kb_article`
- Agile — Stories (5 tools): `create_story`, `update_story`, `list_stories`, `create_story_dependency`, `delete_story_dependency`
- Agile — Epics (3 tools): `create_epic`, `update_epic`, `list_epics`
- Agile — Scrum Tasks (3 tools): `create_scrum_task`, `update_scrum_task`, `list_scrum_tasks`
- Project Management module (3 tools): `create_project`, `update_project`, `list_projects`
- Custom exception hierarchy (`ServiceNowError`, `ServiceNowAPIError`, `ServiceNowAuthError`, `ServiceNowNotFoundError`, `ServiceNowRateLimitError`, `ServiceNowTimeoutError`, `ServiceNowConnectionError`)
- Constants module with enums (`IncidentState`, `ChangeState`, `ChangeType`, `Priority`, `Urgency`, `Impact`)
- Shared `BaseToolParams` model (eliminates duplicate credential handling)
- Exponential-backoff retry logic with configurable `MAX_RETRIES` env var
- Rate-limit handling (HTTP 429 with `Retry-After` header support)
- Configurable request timeout via `API_TIMEOUT` env var
- SSL verification enabled by default, configurable via `SERVICENOW_VERIFY_SSL` env var
- Structured logging via `LOG_LEVEL` env var
- Test scripts for all new modules

### Changed
- Tool count expanded from 15 to 72
- `ServiceNowClient` now raises typed exceptions instead of returning error dicts
- All tool modules wrapped with `try/except ServiceNowError` error handling
- `config_loader` warns on missing credentials instead of crashing

### Fixed
- SSL verification was disabled by default (`verify=False`) — now defaults to `True`
- Duplicate `UpdateIncidentParams` class definition removed
- `setup.cfg` listed `requests` as dependency (project uses `httpx`)
- `setup.cfg` listed `fastmcp>=0.1.0` (now `fastmcp>=2.1.0`)
- Version synced across `pyproject.toml`, `setup.cfg`, and `__init__.py`

### Security
- Removed hardcoded temporary password from user creation — now uses `secrets.token_urlsafe`
- SSL certificate verification enabled by default

## [0.1.1] - 2025-12-08

### Added
- Comprehensive Quickstart guide with visual roadmap
- Environment configuration examples (`.env.example`)
- Contributing guidelines

### Changed
- Improved error messages for authentication failures
- Better connection timeout handling
- Updated documentation structure

### Fixed
- Authentication timeout on slow instances
- Rate limiting edge cases with concurrent requests
- Connection drops on long-running operations

## [0.1.0] - 2025-11-15

### Added
- Initial release with 15 core ServiceNow tools
- Incident Management (5 tools): `create_incident`, `get_incident`, `list_incidents`, `update_incident`, `resolve_incident`
- Change Management (4 tools): `create_change_request`, `update_change_request`, `list_change_requests`, `get_change_request_details`
- User Management (3 tools): `create_user`, `get_user`, `list_users`
- Table Management (3 tools): `list_available_tables`, `get_records_from_table`, `get_table_schema`
- Basic authentication via environment variables
- Claude Desktop integration
- FastMCP 2.x client support
- `snow-mcp` CLI entry point with `--server-mode` and `--list-tools` flags

### Security
- Basic authentication support via `SERVICENOW_INSTANCE`, `SERVICENOW_USERNAME`, `SERVICENOW_PASSWORD` env vars
- Environment variable configuration (no hardcoded credentials)

---

**Maintainer:** Sourojit Dhua
**Repository:** https://github.com/sourojitdhua/Servicenow-MCP

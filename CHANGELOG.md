# Changelog

All notable changes to the ServiceNow MCP Server will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.3.0] - 2026-02-27

### Added
- **Lifespan management**: Shared `ServiceNowClient` HTTP connection opened once at startup, reused across all 106 tool calls (eliminates per-call TCP overhead)
- **Tool tags**: All tools tagged by module (`incident`, `change`, `cmdb`, `catalog`, `kb`, `user`, `problem`, `sla`, `request`, `agile`, `project`, `workflow`, `script_include`, `update_set`, `table`, `analytics`, `ui_policy`) and operation type (`read`, `write`, `delete`)
- **Tool annotations**: All tools annotated with `ToolAnnotations` (`readOnlyHint`, `destructiveHint`, `idempotentHint`) so MCP clients can distinguish safe vs. destructive operations
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
- `move_catalog_items`/`batch_update_records` — added missing `ServiceNowError` import for error handling
- `attach_file_to_record` base64 error now raises `ToolError` instead of returning error dict
- `send_request`/`send_raw_request` — added `JSONDecodeError` handling for non-JSON responses
- `Optional[int]` for `limit`/`offset` in `ListEpicsParams` changed to `int` (None would break API calls)
- Removed unused imports (`BaseModel`, `List`, `ServiceNowError`) across 9+ tool modules
- `setup.cfg` version synced to 0.3.0, `fastmcp` dependency to `>=3.0.0`, description updated
- Retroactive annotation removed from v0.1.0 changelog entry

## [0.2.0] - 2026-02-26

### Added
- CMDB Management module (6 tools): `list_ci_classes`, `get_ci`, `list_cis`, `create_ci`, `update_ci`, `get_ci_relationships`
- Problem Management module (5 tools): `create_problem`, `update_problem`, `list_problems`, `get_problem`, `create_known_error`
- SLA Management module (3 tools): `list_sla_definitions`, `get_task_sla`, `list_breached_slas`
- Generic Table CRUD tools (4 tools): `create_record`, `update_record`, `delete_record`, `batch_update_records`
- Custom exception hierarchy (`ServiceNowError`, `ServiceNowAPIError`, `ServiceNowAuthError`, `ServiceNowNotFoundError`, `ServiceNowRateLimitError`, `ServiceNowTimeoutError`, `ServiceNowConnectionError`)
- Constants module with enums (`IncidentState`, `ChangeState`, `ChangeType`, `Priority`, `Urgency`, `Impact`)
- Shared `BaseToolParams` model (eliminates 16 duplicate definitions)
- Exponential-backoff retry logic with configurable `MAX_RETRIES` env var
- Configurable request timeout via `API_TIMEOUT` env var
- Rate-limit handling (HTTP 429 with `Retry-After` header support)
- SSL verification enabled by default, configurable via `SERVICENOW_VERIFY_SSL` env var
- Structured logging from `LOG_LEVEL` env var
- Test scripts for CMDB, Problem, SLA, and generic table CRUD modules

### Changed
- Tool count increased from 60+ to 106
- `ServiceNowClient` now raises typed exceptions instead of returning error dicts
- All 16 tool modules wrapped with `try/except ServiceNowError` error handling
- `update_epic` HTTP method changed from PUT to PATCH for consistency
- `submit_change_for_approval` uses `ChangeState.ASSESS` instead of magic string "-4"
- `resolve_incident` uses `IncidentState.RESOLVED` instead of magic string "6"
- `create_user` generates secure random password via `secrets.token_urlsafe` instead of hardcoded "TempPassword123!"
- `config_loader` warns on missing credentials instead of crashing (per-call credentials still work)

### Fixed
- SSL verification disabled by default (was `verify=False`) — now defaults to `True`
- Duplicate `UpdateIncidentParams` class definition removed
- Duplicate `update_incident` function definition removed
- `setup.cfg` listed `requests` as dependency (project uses `httpx`)
- `setup.cfg` listed `fastmcp>=0.1.0` (now `fastmcp>=2.1.0`)
- Version synced across `pyproject.toml`, `setup.cfg`, and `__init__.py`

### Security
- Removed hardcoded temporary password from user creation
- SSL certificate verification enabled by default

## [0.1.1] - 2024-12-26

### Added
- Enhanced MCP protocol implementation
- Comprehensive Quickstart guide with visual roadmap
- Project documentation improvements
- Contributing guidelines
- Environment configuration examples

### Changed
- Improved error handling and retry logic
- Updated documentation structure
- Enhanced tool discovery mechanism

### Fixed
- Authentication timeout issues
- Rate limiting edge cases
- Connection stability improvements

## [0.1.0] - 2024-12-01

### Added
- Initial release with 60+ ServiceNow tools
- Support for ITSM operations (Incidents, Changes, Requests)
- Service Catalog management tools
- User and Group management
- Agile development tools (Stories, Epics, Tasks)
- Project management capabilities
- Knowledge base operations
- Workflow management
- Script Include management
- Update Set management
- UI Policy management
- Reporting and analytics tools
- Claude Desktop integration
- FastMCP client support
- Comprehensive documentation
- Example scripts and use cases

### Security
- Basic authentication support
- Environment variable configuration
- Secure credential management

---

## Release Notes

### Version 0.1.1
This release focuses on improving developer experience with better documentation, enhanced error handling, and more robust connection management.

### Version 0.1.0
First public release of the ServiceNow MCP Server. Provides comprehensive coverage of ServiceNow operations through the Model Context Protocol, enabling AI agents and automation tools to interact with ServiceNow seamlessly.

---

**Maintainer:** Sourojit Dhua  
**Repository:** https://github.com/sourojitdhua/Servicenow-MCP

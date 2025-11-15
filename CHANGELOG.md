# Changelog

All notable changes to the ServiceNow MCP Server will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
- Initial release with 60+ ServiceNow tools (now 106 in v0.2.0)
- Support for ITSM operations (Incidents, Changes, Requests)
- Service Catalog management tools
- User and Group management
- Agile development tools (Stories, Epics, Tasks)
- Project management capabilities
- Knowledge base operations
- Workflow management
- Script Include management
- Update Set (Changeset) management
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
**Repository:** https://github.com/yourusername/ServicenowMCP

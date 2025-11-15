# src/servicenow_mcp_server/constants.py

"""Enums, defaults, and API path templates for the ServiceNow MCP server."""

from enum import Enum


# ---------------------------------------------------------------------------
#  ITSM State Enums
# ---------------------------------------------------------------------------

class IncidentState(str, Enum):
    NEW = "1"
    IN_PROGRESS = "2"
    ON_HOLD = "3"
    RESOLVED = "6"
    CLOSED = "7"
    CANCELED = "8"


class ChangeState(str, Enum):
    NEW = "-5"
    ASSESS = "-4"
    AUTHORIZE = "-3"
    SCHEDULED = "-2"
    IMPLEMENT = "-1"
    REVIEW = "0"
    CLOSED = "3"


class ChangeType(str, Enum):
    NORMAL = "Normal"
    STANDARD = "Standard"
    EMERGENCY = "Emergency"


class Priority(str, Enum):
    CRITICAL = "1"
    HIGH = "2"
    MODERATE = "3"
    LOW = "4"
    PLANNING = "5"


class Urgency(str, Enum):
    HIGH = "1"
    MEDIUM = "2"
    LOW = "3"


class Impact(str, Enum):
    HIGH = "1"
    MEDIUM = "2"
    LOW = "3"


# ---------------------------------------------------------------------------
#  Client Defaults
# ---------------------------------------------------------------------------

DEFAULT_TIMEOUT_SECONDS: int = 30
DEFAULT_MAX_RETRIES: int = 3
DEFAULT_RETRY_BACKOFF_BASE: float = 1.0

# ---------------------------------------------------------------------------
#  API Path Templates
# ---------------------------------------------------------------------------

TABLE_API = "/api/now/table/{table_name}"
TABLE_RECORD_API = "/api/now/table/{table_name}/{sys_id}"
STATS_API = "/api/now/stats/{table_name}"
ATTACHMENT_API = "/api/now/attachment/file"

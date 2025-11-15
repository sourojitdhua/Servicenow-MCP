# src/servicenow_mcp_server/exceptions.py

"""Custom exception hierarchy for the ServiceNow MCP server."""


class ServiceNowError(Exception):
    """Base exception for all ServiceNow MCP server errors."""

    def __init__(self, message: str, details: str | None = None):
        self.message = message
        self.details = details
        super().__init__(message)


class ServiceNowAPIError(ServiceNowError):
    """Raised when the ServiceNow API returns an HTTP error."""

    def __init__(
        self,
        message: str,
        status_code: int,
        response_body: str = "",
        details: str | None = None,
    ):
        self.status_code = status_code
        self.response_body = response_body
        super().__init__(message, details=details or response_body)


class ServiceNowAuthError(ServiceNowAPIError):
    """Raised on 401 Unauthorized or 403 Forbidden responses."""


class ServiceNowNotFoundError(ServiceNowAPIError):
    """Raised on 404 Not Found responses."""


class ServiceNowRateLimitError(ServiceNowAPIError):
    """Raised on 429 Too Many Requests responses."""

    def __init__(
        self,
        message: str,
        status_code: int = 429,
        response_body: str = "",
        retry_after: float | None = None,
    ):
        self.retry_after = retry_after
        super().__init__(message, status_code=status_code, response_body=response_body)


class ServiceNowValidationError(ServiceNowError):
    """Raised when input validation fails before making an API call."""


class ServiceNowConnectionError(ServiceNowError):
    """Raised when a network-level connection failure occurs."""


class ServiceNowTimeoutError(ServiceNowError):
    """Raised when a request to ServiceNow times out."""

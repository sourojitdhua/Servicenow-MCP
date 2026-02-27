# src/servicenow_mcp_server/utils.py

"""ServiceNow HTTP client with retry, timeout, rate-limit handling, and typed exceptions."""

import asyncio
import logging
import os
from typing import Dict, Any, Optional

import httpx

from servicenow_mcp_server.constants import (
    DEFAULT_MAX_RETRIES,
    DEFAULT_RETRY_BACKOFF_BASE,
    DEFAULT_TIMEOUT_SECONDS,
)
from servicenow_mcp_server.exceptions import (
    ServiceNowAPIError,
    ServiceNowAuthError,
    ServiceNowConnectionError,
    ServiceNowNotFoundError,
    ServiceNowRateLimitError,
    ServiceNowTimeoutError,
)

logger = logging.getLogger("servicenow_mcp_server.client")

# Status codes that should NOT be retried (raise immediately).
_NON_RETRYABLE_STATUS = {401, 403, 404}


class ServiceNowClient:
    """An async client for making authenticated requests to the ServiceNow API."""

    def __init__(self, instance_url: str, username: str, password: str):
        if not instance_url.endswith("/"):
            instance_url += "/"

        self.base_url = instance_url
        self._auth = (username, password)
        self._client: Optional[httpx.AsyncClient] = None

        # Read configuration from environment (or fall back to defaults).
        self.verify_ssl: bool = os.getenv("SERVICENOW_VERIFY_SSL", "true").lower() not in (
            "false",
            "0",
            "no",
        )
        self.timeout: float = float(
            os.getenv("API_TIMEOUT", str(DEFAULT_TIMEOUT_SECONDS))
        )
        self.max_retries: int = int(
            os.getenv("MAX_RETRIES", str(DEFAULT_MAX_RETRIES))
        )
        self.backoff_base: float = DEFAULT_RETRY_BACKOFF_BASE

    async def __aenter__(self):
        """Initialise the httpx client when entering an ``async with`` block."""
        self._client = httpx.AsyncClient(
            auth=self._auth,
            base_url=self.base_url,
            verify=self.verify_ssl,
            timeout=httpx.Timeout(self.timeout),
        )
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Close the httpx client when exiting the ``async with`` block."""
        if self._client:
            await self._client.aclose()

    # ------------------------------------------------------------------
    #  Internal: request with retry + backoff
    # ------------------------------------------------------------------

    async def _request_with_retry(
        self,
        method: str,
        url: str,
        *,
        headers: Dict[str, str],
        json: Optional[Dict[str, Any]] = None,
        content: Optional[bytes] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> httpx.Response:
        """Execute an HTTP request with exponential back-off and retry logic.

        Non-retryable errors (401, 403, 404) are raised immediately.
        Retryable errors (timeout, connection error, 429, 5xx) are retried up to
        ``self.max_retries`` times.
        """
        if not self._client:
            raise RuntimeError("Client not initialised. Use 'async with ServiceNowClient(...)'")

        last_exc: BaseException | None = None

        for attempt in range(self.max_retries + 1):
            try:
                logger.debug(
                    "Request %s %s (attempt %d/%d)",
                    method,
                    url,
                    attempt + 1,
                    self.max_retries + 1,
                )
                response = await self._client.request(
                    method=method,
                    url=url,
                    json=json,
                    content=content,
                    params=params,
                    headers=headers,
                )

                # --- Non-retryable HTTP errors ---
                if response.status_code in _NON_RETRYABLE_STATUS:
                    self._raise_for_status(response)

                # --- Rate limit (429) ---
                if response.status_code == 429:
                    retry_after = self._parse_retry_after(response)
                    if attempt < self.max_retries:
                        wait = retry_after if retry_after else self._backoff(attempt)
                        logger.warning(
                            "Rate limited (429). Retrying in %.1fs ...", wait
                        )
                        await asyncio.sleep(wait)
                        continue
                    raise ServiceNowRateLimitError(
                        message="Rate limited by ServiceNow API",
                        retry_after=retry_after,
                        response_body=response.text,
                    )

                # --- Server errors (5xx) ---
                if response.status_code >= 500:
                    if attempt < self.max_retries:
                        wait = self._backoff(attempt)
                        logger.warning(
                            "Server error %d. Retrying in %.1fs ...",
                            response.status_code,
                            wait,
                        )
                        await asyncio.sleep(wait)
                        continue
                    self._raise_for_status(response)

                # --- Any other non-success code (4xx besides handled ones) ---
                if response.status_code >= 400:
                    self._raise_for_status(response)

                return response

            except httpx.TimeoutException as exc:
                last_exc = exc
                if attempt < self.max_retries:
                    wait = self._backoff(attempt)
                    logger.warning("Timeout. Retrying in %.1fs ...", wait)
                    await asyncio.sleep(wait)
                    continue
                raise ServiceNowTimeoutError(
                    message="Request to ServiceNow timed out",
                    details=str(exc),
                ) from exc

            except httpx.ConnectError as exc:
                last_exc = exc
                if attempt < self.max_retries:
                    wait = self._backoff(attempt)
                    logger.warning("Connection error. Retrying in %.1fs ...", wait)
                    await asyncio.sleep(wait)
                    continue
                raise ServiceNowConnectionError(
                    message="Failed to connect to ServiceNow",
                    details=str(exc),
                ) from exc

        # Should not be reached, but just in case:
        raise ServiceNowConnectionError(
            message="Request failed after all retries",
            details=str(last_exc),
        )

    # ------------------------------------------------------------------
    #  Public helpers
    # ------------------------------------------------------------------

    async def send_request(
        self,
        method: str,
        endpoint: str,
        data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Send a JSON API request to a ServiceNow endpoint."""
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        response = await self._request_with_retry(
            method, endpoint, headers=headers, json=data, params=params
        )

        if response.status_code == 204:
            return {
                "result": {
                    "status": "success",
                    "message": "Operation completed successfully with no content returned.",
                }
            }
        try:
            return response.json()
        except ValueError:
            raise ServiceNowAPIError(
                message=f"Invalid JSON in response ({response.status_code})",
                status_code=response.status_code,
                response_body=response.text[:500],
            )

    async def send_raw_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[bytes] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Send a request with raw data (e.g. file uploads)."""
        final_headers = {"Accept": "application/json"}
        if headers:
            final_headers.update(headers)

        response = await self._request_with_retry(
            method, endpoint, headers=final_headers, content=data, params=params
        )
        try:
            return response.json()
        except ValueError:
            raise ServiceNowAPIError(
                message=f"Invalid JSON in response ({response.status_code})",
                status_code=response.status_code,
                response_body=response.text[:500],
            )

    # ------------------------------------------------------------------
    #  Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _raise_for_status(response: httpx.Response) -> None:
        """Map an HTTP error response to the appropriate typed exception."""
        status = response.status_code
        body = response.text

        if status in (401, 403):
            raise ServiceNowAuthError(
                message=f"Authentication failed ({status})",
                status_code=status,
                response_body=body,
            )
        if status == 404:
            raise ServiceNowNotFoundError(
                message="Resource not found (404)",
                status_code=status,
                response_body=body,
            )
        if status == 429:
            raise ServiceNowRateLimitError(
                message="Rate limited (429)",
                status_code=status,
                response_body=body,
            )
        raise ServiceNowAPIError(
            message=f"ServiceNow API error ({status})",
            status_code=status,
            response_body=body,
        )

    def _backoff(self, attempt: int) -> float:
        """Compute exponential back-off delay for a given attempt number."""
        return self.backoff_base * (2 ** attempt)

    @staticmethod
    def _parse_retry_after(response: httpx.Response) -> float | None:
        """Try to parse a ``Retry-After`` header (seconds)."""
        value = response.headers.get("Retry-After")
        if value is None:
            return None
        try:
            return float(value)
        except (ValueError, TypeError):
            return None

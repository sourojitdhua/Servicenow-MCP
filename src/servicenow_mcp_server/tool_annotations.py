# src/servicenow_mcp_server/tool_annotations.py

"""Shared ToolAnnotations constants for classifying tool safety."""

from mcp.types import ToolAnnotations

READ = ToolAnnotations(readOnlyHint=True, destructiveHint=False)
WRITE = ToolAnnotations(readOnlyHint=False, destructiveHint=False)
DELETE = ToolAnnotations(readOnlyHint=False, destructiveHint=True)
ADMIN = ToolAnnotations(readOnlyHint=False, idempotentHint=False)

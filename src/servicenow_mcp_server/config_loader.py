import logging
import os
import json
from dotenv import load_dotenv

logger = logging.getLogger("servicenow_mcp_server.config")


def load_config() -> dict | None:
    """
    Loads ServiceNow configuration with the following priority:
    1. Environment variables (e.g., SERVICENOW_INSTANCE).
    2. A .env file in the current working directory.
    3. A JSON file specified by the SERVICENOW_CONFIG_JSON env var.

    Returns the config dict on success, or None if no credentials are found
    (logs a warning instead of crashing so per-call credentials still work).
    """
    # Load .env file contents into environment variables
    load_dotenv()

    # Priority 1: Check for explicit environment variables
    env_vars = ["SERVICENOW_INSTANCE", "SERVICENOW_USERNAME", "SERVICENOW_PASSWORD"]
    if all(os.getenv(v) for v in env_vars):
        logger.info("Loaded ServiceNow credentials from environment variables.")
        return {k.replace("SERVICENOW_", "").lower(): os.getenv(k) for k in env_vars}

    # Priority 2: Check for JSON file path
    json_path = os.getenv("SERVICENOW_CONFIG_JSON")
    if json_path and os.path.exists(json_path):
        with open(json_path, "r") as f:
            logger.info("Loaded ServiceNow credentials from JSON config: %s", json_path)
            return json.load(f)

    # If neither is found, warn but don't crash — tools can still receive per-call creds.
    logger.warning(
        "ServiceNow credentials not found in environment or config file. "
        "Tools will require credentials to be passed per-call."
    )
    return None

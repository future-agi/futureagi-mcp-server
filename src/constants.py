"""Constants and Settings used throughout the FutureAGI MCP Server."""

import os

# Base directory for the project
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Logging configuration
LOGS_DIR = os.path.join(BASE_DIR, "logs")
LOG_LEVEL = os.getenv("LOG_LEVEL", "ERROR")
LOG_FILE = os.path.join(LOGS_DIR, "futureagi-mcp.log")


# Server configuration
SERVER_HOST = "0.0.0.0"
SERVER_PORT = 8001
SERVER_NAME = "futureagi"

# Model Hub configuration
MODEL_HUB_DEVELOP_ID = "2063cf96-40fc-4840-b5cd-ce48f06c24ea"

# Default values
DEFAULT_PROTECT_ACTION = "Response cannot be generated as the input fails the checks"
DEFAULT_PROTECT_TIMEOUT = 30000

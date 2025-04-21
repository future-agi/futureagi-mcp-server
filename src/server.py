import argparse
import os
import sys

from mcp.server.fastmcp import FastMCP

from src.constants import SERVER_HOST, SERVER_NAME, SERVER_PORT
from src.logger import get_logger, setup_logging
from src.tools.datasets import add_evaluation_to_dataset, upload_dataset

# Import tools from their respective modules
from src.tools.evals import (
    all_evaluators,
    create_eval,
    evaluate,
    get_eval_structure,
    get_evals_list_for_create_eval,
)
from src.tools.protect import protect
from src.utils import setup_environment

# Setup logging at module level
setup_logging()
logger = get_logger()

mcp = FastMCP(name=SERVER_NAME, host=SERVER_HOST, port=SERVER_PORT)
mcp.tool()(get_eval_structure)
mcp.tool()(get_evals_list_for_create_eval)
mcp.tool()(create_eval)
mcp.tool()(evaluate)
mcp.tool()(all_evaluators)
mcp.tool()(upload_dataset)
mcp.tool()(add_evaluation_to_dataset)
mcp.tool()(protect)


def start_server():
    """Start the FutureAGI MCP server."""
    mcp.run(transport="stdio")


def main():
    """Main entry point for the FutureAGI MCP server.

    Sets up command line argument parsing for API keys and base URL,
    configures the environment, and starts the MCP server with stdio transport.

    Note: API keys and Base URL are now primarily controlled via environment
    variables (FI_API_KEY, FI_SECRET_KEY, FI_BASE_URL) and validated by Pydantic Settings.
    Command-line arguments are removed as settings handle this.

    Environment variables used:
        FI_API_KEY: FutureAGI API key (Required)
        FI_SECRET_KEY: FutureAGI secret key (Required)
        FI_BASE_URL: FutureAGI base URL (Required)
    """
    parser = argparse.ArgumentParser(description="FutureAGI MCP Server")
    parser.add_argument(
        "--api_key", type=str, required=False, default=os.getenv("FI_API_KEY")
    )
    parser.add_argument(
        "--secret_key", type=str, required=False, default=os.getenv("FI_SECRET_KEY")
    )
    parser.add_argument(
        "--base_url", type=str, required=False, default=os.getenv("FI_BASE_URL")
    )

    try:
        args = parser.parse_args()

        setup_environment(args.api_key, args.secret_key, args.base_url)

        start_server()
    except ValueError as e:
        logger.error(f"Environment variable validation failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

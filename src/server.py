import os
import argparse
import json
from mcp.server.fastmcp import FastMCP

# Import tools from their respective modules
from tools.evals import (
    get_eval_structure,
    get_evals_list_for_create_eval,
    create_eval,
    evaluate,
    all_evaluators,
)
from tools.datasets import upload_dataset
from tools.protect import protect
from utils import setup_environment

# Create an MCP server
mcp = FastMCP("futureagi", host="0.0.0.0", port=8001)

# Register tools with MCP
mcp.tool()(get_eval_structure)
mcp.tool()(get_evals_list_for_create_eval)
mcp.tool()(create_eval)
mcp.tool()(evaluate)
mcp.tool()(all_evaluators)
mcp.tool()(upload_dataset)
mcp.tool()(protect)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--api_key", type=str, required=False)
    parser.add_argument("--secret_key", type=str, required=False)
    parser.add_argument("--base_url", type=str, required=False)

    try:
        args = parser.parse_args()

        # Setup environment variables using the imported function
        setup_environment(
            api_key=args.api_key or os.getenv("FI_API_KEY", ""),
            secret_key=args.secret_key or os.getenv("FI_SECRET_KEY", ""),
            base_url=args.base_url or os.getenv("FI_BASE_URL", ""),
        )

        print("Starting MCP server with stdio transport")
        mcp.run(transport="stdio")
    except Exception as e:
        error_json = json.dumps({"error": str(e)})
        print(error_json)

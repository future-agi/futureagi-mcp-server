import json

import mcp.types as types
from mcp.server import Server

from src.constants import SERVER_NAME
from src.logger import get_logger

# Import tool descriptions
from src.tools.datasets import (
    ADD_EVALUATION_TO_DATASET_DESCRIPTION,
    UPLOAD_DATASET_DESCRIPTION,
    add_evaluation_to_dataset,
    upload_dataset,
)

# Import tools from their respective modules
from src.tools.evals import (
    ALL_EVALUATORS_DESCRIPTION,
    CREATE_EVAL_DESCRIPTION,
    EVALUATE_DESCRIPTION,
    GET_EVAL_STRUCTURE_DESCRIPTION,
    GET_EVALS_LIST_FOR_CREATE_EVAL_DESCRIPTION,
    all_evaluators,
    create_eval,
    evaluate,
    get_eval_structure,
    get_evals_list_for_create_eval,
)
from src.tools.protect import PROTECT_DESCRIPTION, protect
from src.utils import setup_environment

logger = get_logger()


def get_server(
    api_key: str,
    secret_key: str,
    base_url: str,
):
    """Serve the FutureAGI MCP server."""
    setup_environment(api_key, secret_key, base_url)

    # Instantiate the server with its name
    server = Server(SERVER_NAME)

    @server.list_tools()
    async def handle_list_tools() -> list[types.Tool]:
        """Return the list of tools that the server provides."""
        return [
            types.Tool(
                name="get_eval_structure",
                description=GET_EVAL_STRUCTURE_DESCRIPTION,
                inputSchema={
                    "type": "object",
                    "properties": {
                        "template_id": {
                            "type": "string",
                            "description": "UUID of the evaluation template",
                        },
                    },
                    "required": ["template_id"],
                },
            ),
            types.Tool(
                name="get_evals_list_for_create_eval",
                description=GET_EVALS_LIST_FOR_CREATE_EVAL_DESCRIPTION,
                inputSchema={
                    "type": "object",
                    "properties": {
                        "eval_type": {
                            "type": "string",
                            "description": "Type of evaluation templates to retrieve ('preset' or 'user')",
                        },
                    },
                    "required": ["eval_type"],
                },
            ),
            types.Tool(
                name="create_eval",
                description=CREATE_EVAL_DESCRIPTION,
                inputSchema={
                    "type": "object",
                    "properties": {
                        "eval_name": {
                            "type": "string",
                            "description": "Name for the new evaluation template",
                        },
                        "template_id": {
                            "type": "string",
                            "description": "UUID of the base evaluation template to use",
                        },
                        "config": {
                            "type": "object",
                            "description": "Configuration for the new template",
                        },
                    },
                    "required": ["eval_name", "template_id", "config"],
                },
            ),
            types.Tool(
                name="evaluate",
                description=EVALUATE_DESCRIPTION,
                inputSchema={
                    "type": "object",
                    "properties": {
                        "eval_templates": {
                            "type": "array",
                            "description": "List of evaluation templates to use",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "eval_id": {"type": "string"},
                                    "config": {"type": "object"},
                                },
                                "required": ["eval_id"],
                            },
                        },
                        "inputs": {
                            "type": "array",
                            "description": "List of test cases to evaluate",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "text": {"type": "string"},
                                    "output": {"type": "string"},
                                    "prompt": {"type": "string"},
                                    "criteria": {"type": "string"},
                                },
                            },
                        },
                    },
                    "required": ["eval_templates", "inputs"],
                },
            ),
            types.Tool(
                name="all_evaluators",
                description=ALL_EVALUATORS_DESCRIPTION,
                inputSchema={
                    "type": "object",
                    "properties": {},
                    "required": [],
                },
            ),
            types.Tool(
                name="upload_dataset",
                description=UPLOAD_DATASET_DESCRIPTION,
                inputSchema={
                    "type": "object",
                    "properties": {
                        "dataset_name": {
                            "type": "string",
                            "description": "Name of the dataset to create",
                        },
                        "model_type": {
                            "type": "string",
                            "description": "Type of model (e.g., 'GenerativeLLM', 'GenerativeImage')",
                        },
                        "source": {
                            "type": "string",
                            "description": "Source file path for the dataset",
                        },
                    },
                    "required": ["dataset_name", "model_type", "source"],
                },
            ),
            types.Tool(
                name="add_evaluation_to_dataset",
                description=ADD_EVALUATION_TO_DATASET_DESCRIPTION,
                inputSchema={
                    "type": "object",
                    "properties": {
                        "dataset_name": {
                            "type": "string",
                            "description": "Name of the target dataset",
                        },
                        "name": {
                            "type": "string",
                            "description": "Name for the new evaluation column",
                        },
                        "eval_id": {
                            "type": "string",
                            "description": "ID of the evaluation template to use",
                        },
                        "input_column_name": {
                            "type": "string",
                            "description": "Name of the input data column",
                        },
                        "output_column_name": {
                            "type": "string",
                            "description": "Name of the output data column",
                        },
                        "context_column_name": {
                            "type": "string",
                            "description": "Name of the context data column",
                        },
                        "expected_column_name": {
                            "type": "string",
                            "description": "Name of the expected response column",
                        },
                        "save_as_template": {
                            "type": "boolean",
                            "description": "Whether to save as a template",
                        },
                        "reason_column": {
                            "type": "boolean",
                            "description": "Whether to add a reason column",
                        },
                        "config": {
                            "type": "object",
                            "description": "Additional configuration parameters",
                        },
                    },
                    "required": ["dataset_name", "name", "eval_id"],
                },
            ),
            types.Tool(
                name="protect",
                description=PROTECT_DESCRIPTION,
                inputSchema={
                    "type": "object",
                    "properties": {
                        "inputs": {
                            "type": "string",
                            "description": "Input string to evaluate",
                        },
                        "protect_rules": {
                            "type": "array",
                            "description": "List of protection rules",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "metric": {
                                        "type": "string",
                                        "enum": [
                                            "Toxicity",
                                            "Tone",
                                            "Sexism",
                                            "Prompt Injection",
                                            "Data Privacy",
                                        ],
                                    },
                                    "contains": {
                                        "type": "array",
                                        "items": {
                                            "type": "string",
                                            "enum": [
                                                "neutral",
                                                "joy",
                                                "love",
                                                "fear",
                                                "surprise",
                                                "sadness",
                                                "anger",
                                                "annoyance",
                                                "confusion",
                                            ],
                                        },
                                    },
                                    "type": {
                                        "type": "string",
                                        "enum": ["any", "all"],
                                    },
                                },
                                "required": ["metric"],
                            },
                        },
                        "action": {
                            "type": "string",
                            "description": "Default action message when rules fail",
                        },
                        "reason": {
                            "type": "boolean",
                            "description": "Whether to include failure reason",
                        },
                        "timeout": {
                            "type": "integer",
                            "description": "Timeout for evaluations in milliseconds",
                        },
                    },
                    "required": ["inputs", "protect_rules"],
                },
            ),
        ]

    @server.call_tool()
    async def handle_tool_call(
        name: str, arguments: dict | None
    ) -> list[types.TextContent | types.ImageContent]:
        """Handle incoming tool calls and dispatch them to the correct function."""
        if arguments is None:
            arguments = {}
        logger.info(f"Received tool call: {name} with arguments: {arguments}")
        try:
            # Dispatch the call to the correct tool implementation
            # based on the tool name
            if name == "get_eval_structure":
                result = await get_eval_structure(**arguments)
            elif name == "get_evals_list_for_create_eval":
                result = await get_evals_list_for_create_eval(**arguments)
            elif name == "create_eval":
                result = await create_eval(**arguments)
            elif name == "evaluate":
                result = await evaluate(**arguments)
            elif name == "all_evaluators":
                result = await all_evaluators()
            elif name == "upload_dataset":
                logger.info(f"Uploading dataset {arguments}")
                result = await upload_dataset(**arguments)
            elif name == "add_evaluation_to_dataset":
                result = await add_evaluation_to_dataset(**arguments)
            elif name == "protect":
                result = await protect(**arguments)
            else:
                logger.warning(f"Unknown tool name received: {name}")
                return [
                    types.TextContent(text=f"Unknown tool name: {name}", type="text")
                ]

            # Process and return the result
            if isinstance(result, dict):
                result_str = json.dumps(result, indent=2)
            elif isinstance(result, list):
                result_str = json.dumps(result, indent=2)
            else:
                result_str = str(result)

            logger.info(f"Tool {name} executed successfully. Result: {result_str}")
            return [types.TextContent(text=result_str, type="text")]
        except Exception as e:
            logger.error(
                f"Error executing tool {name} with args {arguments}: {str(e)}",
                exc_info=True,
            )
            return [
                types.TextContent(
                    text=f"Error executing tool {name}: {str(e)}", type="text"
                )
            ]

    return server

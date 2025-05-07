import json

import mcp.types as types
from mcp.server import Server

from .constants import SERVER_NAME
from .logger import get_logger

# Import tool descriptions
from .tools.datasets import (
    ADD_EVALUATION_TO_DATASET_DESCRIPTION,
    DATASET_EVALUATION_INSIGHTS_DESCRIPTION,
    DOWNLOAD_DATASET_DESCRIPTION,
    UPLOAD_DATASET_DESCRIPTION,
    add_evaluation_to_dataset,
    download_dataset,
    get_evaluation_insights,
    upload_dataset,
)

# Import tools from their respective modules
from .tools.evals import (
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
from .tools.protect import PROTECT_DESCRIPTION, protect
from .tools.syntheticdatagen import (
    GENERATE_SYNTHETIC_DATA_DESCRIPTION,
    generate_synthetic_data,
)
from .utils import setup_environment

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
                                    "config": {
                                        "type": "object",
                                        "description": "Additional configuration parameters",
                                        "properties": {
                                            "criteria": {"type": "string"},
                                            "model": {"type": "string"},
                                        },
                                        "required": [],
                                    },
                                },
                                "required": ["eval_id", "config"],
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
                            "enum": [
                                "GenerativeLLM",
                                "GenerativeImage",
                            ],
                        },
                        "source": {
                            "type": "string",
                            "description": "Source file path for the dataset (local file path or URL) if not provided, the empty dataset will be created in the FutureAGI platform",
                        },
                    },
                    "required": ["dataset_name", "model_type"],
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
                            "description": "eval_id for the evaluation template, example: '1', '9', '11'",
                        },
                        "required_keys_to_column_names": {
                            "type": "object",
                            "description": "A dictionary mapping required keys of the eval template to column names in the dataset",
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
                            "description": "Additional configuration parameters, use the config['config'] dictionary in the eval template structure",
                        },
                    },
                    "required": [
                        "dataset_name",
                        "name",
                        "eval_id",
                        "required_keys_to_column_names",
                        "config",
                    ],
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
            types.Tool(
                name="download_dataset",
                description=DOWNLOAD_DATASET_DESCRIPTION,
                inputSchema={
                    "type": "object",
                    "properties": {
                        "dataset_name": {
                            "type": "string",
                            "description": "Name of the dataset to download",
                        },
                        "file_path": {
                            "type": "string",
                            "description": "Path to save the downloaded dataset",
                        },
                    },
                    "required": ["dataset_name", "file_path"],
                },
            ),
            types.Tool(
                name="get_evaluation_insights",
                description=DATASET_EVALUATION_INSIGHTS_DESCRIPTION,
                inputSchema={
                    "type": "object",
                    "properties": {
                        "dataset_name": {
                            "type": "string",
                            "description": "Name of the dataset to get insights",
                        },
                    },
                    "required": ["dataset_name"],
                },
            ),
            types.Tool(
                name="generate_synthetic_data",
                description=GENERATE_SYNTHETIC_DATA_DESCRIPTION,
                inputSchema={
                    "type": "object",
                    "properties": {
                        "dataset": {
                            "type": "object",
                            "description": "Metadata describing the dataset to be generated.",
                            "properties": {
                                "name": {
                                    "type": "string",
                                    "description": "A clear, descriptive title for your dataset. Example: 'Customer Support Logs'",
                                },
                                "description": {
                                    "type": "string",
                                    "description": "A detailed explanation of the dataset's contents, purpose, and context.",
                                },
                                "objective": {
                                    "type": "string",
                                    "description": "The main goal or intended use case for the dataset. Example: 'To fine-tune a language model for customer support scenarios.'",
                                },
                                "patterns": {
                                    "type": "string",
                                    "description": "Specific instructions or stylistic patterns to follow when generating data. Example: 'Follow a conversational pattern with alternating customer and agent messages.'",
                                },
                            },
                            "required": [
                                "name",
                                "description",
                                "objective",
                                "patterns",
                            ],
                        },
                        "num_rows": {
                            "type": "integer",
                            "description": "The total number of rows (examples) to generate in the dataset. Example: 1000.",
                        },
                        "columns": {
                            "type": "array",
                            "description": "The schema definition for each column in the dataset. Each object describes one column.",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "name": {
                                        "type": "string",
                                        "description": "The column's name. Should be unique and descriptive. Example: 'customer_id'",
                                    },
                                    "description": {
                                        "type": "string",
                                        "description": "A detailed description of what this column represents. Example: 'The unique identifier for each customer.'",
                                    },
                                    "data_type": {
                                        "type": "string",
                                        "description": "The type of data stored in this column. Supported types: 'text', 'float', 'integer', 'boolean', 'array', 'json', 'datetime'. Example: 'integer'",
                                    },
                                    "property": {
                                        "type": "object",
                                        "description": "Additional constraints or characteristics for the column. For numeric columns: specify 'min', 'max', etc. For text columns: specify 'min_length', 'max_length', 'pattern', etc. For categorical columns: specify 'values' (list of allowed values). For all columns: add any other relevant constraints or metadata.",
                                    },
                                },
                                "required": [
                                    "name",
                                    "description",
                                    "data_type",
                                    "property",
                                ],
                            },
                        },
                    },
                    "required": ["dataset", "num_rows", "columns"],
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
            elif name == "download_dataset":
                result = await download_dataset(**arguments)
            elif name == "get_evaluation_insights":
                result = await get_evaluation_insights(**arguments)
            elif name == "generate_synthetic_data":
                result = await generate_synthetic_data(**arguments)
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

            output = [types.TextContent(text=result_str, type="text")]

            if name == "evaluate":
                output.insert(
                    0,
                    types.TextContent(
                        text="""
Convert the output to MARKDOWN.md code block format (this is mandatory).
Do not use plain text, lists, or any other format.
""",
                        type="text",
                    ),
                )

            return output
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

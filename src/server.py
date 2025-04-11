import os
import argparse
import json
from fi.evals import EvalClient, ProtectClient
from fi.evals.templates import EvalTemplate
from mcp.server.fastmcp import FastMCP
from models import EvalTemplateInput
from fi.testcases import TestCase
from typing import List, Optional, Union, Dict
from fi.datasets import DatasetClient
from fi.datasets.types import DatasetConfig, HuggingfaceDatasetConfig

# Create an MCP server
mcp = FastMCP("futureagi", host="0.0.0.0", port=8001)


@mcp.tool()
def evaluate(eval_templates: List[EvalTemplateInput], inputs: List[TestCase]):
    """
    First Fetch the all the evaluators using the all_evaluators tool.
    Then find the eval_id from the all_evaluators list.
    Then evaluate the inputs against the eval templates.

    The inputs are a list of test cases that has to be evaluated.
    Inputs should contain the required fields for respective eval template.
    Example:
    inputs = [
        {
            "text": "You are a helpful assistant",
            "output": "You are a helpful assistant",
            "prompt": "You are a helpful assistant",
            "criteria": "You are a helpful assistant"
        }
    ]

    The eval_templates are a list of evaluation that are used to evaluate the inputs.
    Eval id should be a string of integer of the eval template.
    You can get the eval_id from the all_evaluators list.

    Example:
    eval_templates = [
        {
            "eval_id": "1",
            "config": Optional[EvalConfig] = {
                "criteria": str,
                "model": str
            } # can be empty
        }
    ]

    Args:
        eval_templates: List[
            {
                "eval_id": str,
                "config": Optional = {
                    "criteria": str,
                    "model": str
                }
            }
        ]
        inputs: List[
            {
                "text": Optional[str] = None,
                "document": Optional[str] = None,
                "input": Optional[str] = None,
                "output": Optional[str] = None,
                "prompt": Optional[str] = None,
                "criteria": Optional[str] = None,
                "actual_json": Optional[dict] = None,
                "expected_json": Optional[dict] = None,
                "expected_text": Optional[str] = None,
                "query": Optional[str] = None,
                "response": Optional[str] = None,
                "context": Union[List[str], str] = None
            }
        ]

    Returns:
        List[BatchRunResult]
    """
    eval_client = EvalClient()
    constructed_eval_templates = []
    for templateinput in eval_templates:
        current_eval_template = EvalTemplate(config=templateinput.config)
        current_eval_template.eval_id = templateinput.eval_id
        constructed_eval_templates.append(current_eval_template)
    eval_results = eval_client.evaluate(constructed_eval_templates, inputs)
    return eval_results

@mcp.tool()
def get_eval_config(eval_templates: List[EvalTemplateInput]):
    """Get the evaluation configuration for the given evaluation templates

    The eval_templates are a list of evaluation templates that are used to evaluate the model.
    The eval_templates should contain the eval_id and the config.
    The returned config will have the configuration and required fields for the input to the evaluate.

    Args:
        eval_templates: List[
            {
                "eval_id": "1",
                "config": Optional[EvalConfig] = {
                    "criteria": "criteria",
                    "config": {},
                    "model": "gpt-4o"
                }
            }
        ]

        EvalTemplateInput:
            eval_id: str
            config: Optional[EvalConfig] = {
                "criteria": str,
                "config": dict,
                "model": str
            }

        EvalConfig:
            criteria: Optional[str] = ""
            config: Optional[dict] = {}
            model: Optional[str] = ""

    Returns:
        List[EvalTemplate]
    """
    eval_client = EvalClient()
    eval_infos = []
    for templateinput in eval_templates:
        eval_info = eval_client._get_eval_info(templateinput.eval_id)
        eval_infos.append(eval_info)
    return eval_infos


@mcp.tool()
def all_evaluators():
    """Get all evaluators and their configurations

    When called will return all the evaluators, their functions and their configurations.

    Returns:
        List[Evaluator]
    """
    eval_client = EvalClient()
    return json.dumps(eval_client.list_evaluations())


@mcp.tool()
def create_eval(eval_name: str, eval_id: str, config: dict):
    """Create an evaluation

    Args:
        eval_id: str
        config: dict
    """
    eval_client = EvalClient()
    eval_client.create_evaluation(eval_name, eval_id, config)
    return json


@mcp.tool()
def upload_dataset(
    dataset_name: str,
    model_type: str,
    source: str
) -> dict:
    """Upload a dataset to FutureAGI

    Args:
        dataset_name: Name of the dataset to create
        model_type: Type of model (e.g., "GenerativeLLM", "GenerativeImage")
        source: Optional source for the dataset. Can be:
            - A file path (str) for local files

        Example:
        dataset_name = "my_dataset"
        model_type = "GenerativeLLM"
        source = "/Users/name/Downloads/test.csv"

    Returns:
        dict: Dataset configuration including ID and name
    """

    # Create dataset config
    config = DatasetConfig(name=dataset_name, model_type=model_type)

    # Create dataset client
    client = DatasetClient(
        dataset_config=config,
        fi_api_key=os.getenv("FI_API_KEY"),
        fi_secret_key=os.getenv("FI_SECRET_KEY"),
        fi_base_url=os.getenv("FI_BASE_URL"),
    )

    # Handle source if provided
    if source:
        if isinstance(source, str):
            # Local file upload
            client.create(source=source)
    else:
        # Create empty dataset
        client.create()

    return {
        "id": client.dataset_config.id,
        "name": client.dataset_config.name,
        "model_type": client.dataset_config.model_type,
    }


@mcp.tool()
def protect(
    inputs: str,
    protect_rules: List[Dict],
    action: str = "Response cannot be generated as the input fails the checks",
    reason: bool = False,
    timeout: int = 30000,
) -> Dict:
    """
    Evaluate input strings against protection rules.

    Args:
        inputs: Single string to evaluate. Can be text, image file path/URL, or audio file path/URL
        protect_rules: List of protection rule dictionaries. Each rule must contain:
            - metric: str, name of the metric to evaluate ('Toxicity', 'Tone', 'Sexism', 'Prompt Injection', 'Data Privacy')
            - contains: List[str], required for Tone metric only. Possible values: neutral, joy, love, fear, surprise, 
                       sadness, anger, annoyance, confusion
            - type: str, required for Tone metric only. Either 'any' (default) or 'all'
        action: Default action message when rules fail. Defaults to "Response cannot be generated as the input fails the checks"
        reason: Whether to include failure reason in output. Defaults to False
        timeout: Timeout for evaluations in milliseconds. Defaults to 30000

    Returns:
        Dict with protection results containing:
            - status: 'passed' or 'failed'
            - messages: Action message if failed, original input if passed
            - completed_rules: List of rules that were evaluated
            - uncompleted_rules: List of rules not evaluated due to failure/timeout
            - failed_rule: Name of failed rule, or None if passed
            - reason: Explanation for failure if reason=True
            - time_taken: Total evaluation duration
    """
    eval_client = EvalClient()
    protect_client = ProtectClient(evaluator=eval_client)
    
    result = protect_client.protect(
        inputs=inputs,
        protect_rules=protect_rules,
        action=action,
        reason=reason,
        timeout=timeout
    )
    
    return result


def setup_environment(api_key: str, secret_key: str, base_url: str):
    """Setup environment variables for the application"""
    os.environ["FI_API_KEY"] = api_key
    os.environ["FI_SECRET_KEY"] = secret_key
    os.environ["FI_BASE_URL"] = base_url


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--api_key", type=str, required=False)
    parser.add_argument("--secret_key", type=str, required=False)
    parser.add_argument("--base_url", type=str, required=False)

    try:
        args = parser.parse_args()

        # Setup environment variables
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

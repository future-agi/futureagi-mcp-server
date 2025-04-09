import os
import argparse
import json
from fi.evals import EvalClient
from fi.evals.templates import EvalTemplate
from mcp.server.fastmcp import FastMCP
from models import EvalTemplateInput
from fi.testcases import TestCase
from typing import List

# Create an MCP server
mcp = FastMCP("futureagi", host="0.0.0.0", port=8001)


@mcp.tool()
def evaluate(eval_templates: List[EvalTemplateInput], inputs: List[TestCase]):
    """Evaluate the given request using eval templates and inputs

    The inputs are a list of test cases that are used to evaluate the model.
    The eval_templates are a list of evaluation templates that are used to evaluate the model.

    Evaluation configs can be fetched using the get_eval_config tool.
    Inputs should contain the required fields depending on the eval template.
    
    Args:
        eval_templates: List[
            {
                "eval_id": str,
                "config": Optional = {
                    "criteria": str,
                    "config": dict,
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
    eval_results = eval_client.evaluate(
        constructed_eval_templates, inputs
    )
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
                "eval_id": str,
                "config": Optional[EvalConfig] = {
                    "criteria": str,
                    "config": dict,
                    "model": str
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
    constructed_eval_templates = []
    for templateinput in eval_templates:
        current_eval_template = EvalTemplate(config=templateinput.config)
        current_eval_template.eval_id = templateinput.eval_id
        constructed_eval_templates.append(current_eval_template)
    return eval_client._get_eval_configs(constructed_eval_templates)

@mcp.tool()
def all_evaluators():
    """Get all evaluators and their configurations

    When called will return all the evaluators, their functions and their configurations.
    
    Returns:
        List[Evaluator]
    """
    eval_client = EvalClient()
    return eval_client.list_evaluations()

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
            base_url=args.base_url or os.getenv("FI_BASE_URL", "")
        )

        print("Starting MCP server with stdio transport")
        mcp.run(transport="sse")
    except Exception as e:
        error_json = json.dumps({"error": str(e)})
        print(error_json)

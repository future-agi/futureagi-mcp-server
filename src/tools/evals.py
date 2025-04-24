import json
import os
from typing import List

from fi.api.auth import APIKeyAuth
from fi.api.types import HttpMethod, RequestConfig
from fi.evals import EvalClient
from fi.evals.templates import EvalTemplate
from fi.testcases import TestCase

from src.logger import get_logger
from src.tools.routes import Routes

logger = get_logger()

GET_EVAL_STRUCTURE_DESCRIPTION = """
    Get the structure of an evaluation using the template_id.

    Args:
        template_id: UUID of the evaluation template

    Returns:
        dict: A dictionary containing the evaluation structure with fields like:
            - id: UUID of the evaluation
            - name: Name of the evaluation (e.g. "Toxicity")
            - description: Description of what the evaluation does
            - evalTags: List of tags categorizing the evaluation
            - requiredKeys: List of required input keys
            - optionalKeys: List of optional input keys
            - output: Expected output format (e.g. "Pass/Fail")
            - config: Configuration parameters
    """

GET_EVALS_LIST_FOR_CREATE_EVAL_DESCRIPTION = """
    Get a list of available evaluation templates for creating new evaluations.

    This function retrieves the list of evaluation templates that can be used as a base for creating
    new custom evaluations. It should not be used when adding existing evaluations to datasets.

    Args:
        eval_type (str): Type of evaluation templates to retrieve:
            - 'preset': Built-in evaluation templates provided by the system
            - 'user': Custom evaluation templates created by users

    Returns:
        dict: Dictionary containing evaluation templates and their configurations. Each template includes:
            - id: Template ID
            - name: Template name
            - description: Template description
            - config: Template configuration parameters
    """

CREATE_EVAL_DESCRIPTION = """Create a new evaluation template based on an existing template.

    Before calling this tool, you should:
    1. Get available templates using get_evals_list_for_create_eval()
    2. Get the template structure using get_eval_structure()
    3. Construct the config dict using the template structure

    Args:
        eval_name (str): Name for the new evaluation template
        template_id (str): UUID of the base evaluation template to use
        config (dict): Configuration for the new template containing:
            mapping (dict): Mapping containing the required fields for the evaluation structure and the example values
            config (dict): Additional configuration parameters specific to this template. Refer to config['config'] in the get_eval_structure output
            model (str): Name of the model to use (e.g. "gpt-4", "claude-3-sonnet")

    Returns:
        dict: Response from the evaluation creation API containing the new template details
            or error information if the creation failed
    """

EVALUATE_DESCRIPTION = """
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

ALL_EVALUATORS_DESCRIPTION = """Get all evaluators and their configurations, always print the evaluators in the order of CUSTOM, then FUTURE_EVALS, then the rest

    Returns a list of all available evaluators with their complete configurations including:
    - id: Unique UUID identifier for the evaluator
    - name: Display name of the evaluator
    - description: description of the evaluator
    - organization: Optional organization that owns the evaluator
    - owner: System level ownership designation
    - eval_tags: Content types supported by evaluator
    - config.config.input: Rule string type input with default empty array
    - config.config.choices: Choices type with default empty array
    - config.config.rule_prompt: Rule prompt type with default empty string
    - config.config.multi_choice: Boolean flag defaulting to false
    - config.output: Output format specified as choices
    - config.eval_type_id: Evaluator implementation type identifier
    - config.required_keys: Required configuration keys (empty)
    - config.config_params_desc: Descriptions for all config parameters
    - eval_id: Numeric identifier for the evaluator
    - criteria: Optional evaluation criteria
    - choices: Optional list of valid choices
    - multi_choice: Flag for multiple choice support

    Returns:
        dict: Dictionary containing all evaluator configurations
    """


async def get_eval_structure(template_id: str):
    """
    Get the structure of an evaluation using the template_id.

    Args:
        template_id: UUID of the evaluation template

    Returns:
        dict: A dictionary containing the evaluation structure with fields like:
            - id: UUID of the evaluation
            - name: Name of the evaluation (e.g. "Toxicity")
            - description: Description of what the evaluation does
            - evalTags: List of tags categorizing the evaluation
            - requiredKeys: List of required input keys
            - optionalKeys: List of optional input keys
            - output: Expected output format (e.g. "Pass/Fail")
            - config: Configuration parameters
    """
    request_handler = APIKeyAuth(
        os.getenv("FI_API_KEY"), os.getenv("FI_SECRET_KEY"), os.getenv("FI_BASE_URL")
    )
    url = Routes.eval_structure(template_id)
    config = RequestConfig(
        method=HttpMethod.POST, url=url, json={"eval_type": "preset"}
    )

    try:
        response = request_handler.request(config)
        return response.json()
    except Exception as e:
        logger.error(f"Failed to get evaluation structure: {str(e)}", exc_info=True)
        return json.dumps({"error": str(e)})


async def get_evals_list_for_create_eval(eval_type: str) -> dict:
    """
    Get a list of available evaluation templates for creating new evaluations.

    This function retrieves the list of evaluation templates that can be used as a base for creating
    new custom evaluations. It should not be used when adding existing evaluations to datasets.

    Args:
        eval_type (str): Type of evaluation templates to retrieve:
            - 'preset': Built-in evaluation templates provided by the system
            - 'user': Custom evaluation templates created by users

    Returns:
        dict: Dictionary containing evaluation templates and their configurations. Each template includes:
            - id: Template ID
            - name: Template name
            - description: Template description
            - config: Template configuration parameters
    """
    request_handler = APIKeyAuth(
        os.getenv("FI_API_KEY"), os.getenv("FI_SECRET_KEY"), os.getenv("FI_BASE_URL")
    )
    url = Routes.EVALS_LIST.value
    json_data = {"eval_type": eval_type, "search_text": ""}
    config = RequestConfig(method=HttpMethod.POST, url=url, json=json_data)
    try:
        response = request_handler.request(config)
        return response.json()
    except Exception as e:
        logger.error(f"Failed to get evaluations list: {str(e)}", exc_info=True)
        return json.dumps({"error": str(e)})


async def create_eval(eval_name: str, template_id: str, config: dict) -> dict:
    """Create a new evaluation template based on an existing template.

    Before calling this tool, you should:
    1. Get available templates using get_evals_list_for_create_eval()
    2. Get the template structure using get_eval_structure()
    3. Construct the config dict using the template structure

    Args:
        eval_name (str): Name for the new evaluation template
        template_id (str): UUID of the base evaluation template to use
        config (dict): Configuration for the new template containing:
            mapping (dict): Mapping containing the required fields for the evaluation structure and the example values
            config (dict): Additional configuration parameters specific to this template. Refer to config['config'] in the get_eval_structure output
            model (str): Name of the model to use (e.g. "gpt-4", "claude-3-sonnet")

    Returns:
        dict: Response from the evaluation creation API containing the new template details
            or error information if the creation failed
    """
    request_handler = APIKeyAuth(
        os.getenv("FI_API_KEY"), os.getenv("FI_SECRET_KEY"), os.getenv("FI_BASE_URL")
    )
    config_dict = config if isinstance(config, dict) else json.loads(config)

    # Make request to run evaluation
    url = Routes.RUN_EVAL.value
    payload = {
        "template_id": template_id,
        "is_run": False,
        "saveAsTemplate": True,
        "log_ids": [],
        "name": eval_name,
        "config": config_dict,  # Pass the dict
    }
    config = RequestConfig(method=HttpMethod.POST, url=url, json=payload)

    try:
        response = request_handler.request(config)
        return response.json()
    except Exception as e:
        logger.error(f"Failed to create evaluation: {str(e)}", exc_info=True)
        return json.dumps({"error": str(e)})


async def evaluate(eval_templates: List[dict], inputs: List[dict]) -> dict:
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
    try:
        eval_client = EvalClient()
        constructed_eval_templates = []

        for template_input in eval_templates:
            current_eval_template = EvalTemplate(
                config=template_input["config"].get("config", {})
            )
            current_eval_template.eval_id = template_input["eval_id"]
            constructed_eval_templates.append(current_eval_template)

        constructed_inputs = []
        for input_item in inputs:
            current_input = TestCase(**input_item)
            constructed_inputs.append(current_input)

        eval_results = eval_client.evaluate(
            constructed_eval_templates, constructed_inputs
        )
        return eval_results.model_dump()
    except Exception as e:
        logger.error(f"Error during evaluation: {str(e)}", exc_info=True)
        return json.dumps({"error": str(e)})


async def all_evaluators() -> dict:
    """Get all evaluators and their configurations, always print the evaluators in the order of CUSTOM, then FUTURE_EVALS, then the rest

    Returns a list of all available evaluators with their complete configurations including:
    - id: Unique UUID identifier for the evaluator
    - name: Display name of the evaluator
    - description: description of the evaluator
    - organization: Optional organization that owns the evaluator
    - owner: System level ownership designation
    - eval_tags: Content types supported by evaluator
    - config.config.input: Rule string type input with default empty array
    - config.config.choices: Choices type with default empty array
    - config.config.rule_prompt: Rule prompt type with default empty string
    - config.config.multi_choice: Boolean flag defaulting to false
    - config.output: Output format specified as choices
    - config.eval_type_id: Evaluator implementation type identifier
    - config.required_keys: Required configuration keys (empty)
    - config.config_params_desc: Descriptions for all config parameters
    - eval_id: Numeric identifier for the evaluator
    - criteria: Optional evaluation criteria
    - choices: Optional list of valid choices
    - multi_choice: Flag for multiple choice support

    Returns:
        dict: Dictionary containing all evaluator configurations
    """
    try:
        logger.info("Fetching evaluators")
        eval_client = EvalClient()
        evaluators = eval_client.list_evaluations()
        evaluators.sort(
            key=lambda x: x["eval_tags"] and "CUSTOM" in x["eval_tags"], reverse=True
        )
        logger.info(f"Evaluators: {evaluators}")
        return json.dumps(evaluators)
    except Exception as e:
        logger.error(f"Failed to fetch evaluators: {str(e)}", exc_info=True)
        return json.dumps({"error": str(e)})

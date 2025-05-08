import json
import os
from typing import List, Optional

from fi.api.auth import APIKeyAuth
from fi.api.types import HttpMethod, RequestConfig
from fi.evals import EvalClient
from fi.evals.templates import EvalTemplate
from fi.testcases import MLLMTestCase
from pydantic import ConfigDict

from ..logger import get_logger
from .routes import Routes

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
    Use this tool to evaluate single and batch of inputs against specified evaluation templates.

    Before using this tool, you MUST:
    1. Call the all_evaluators tool to retrieve the current list of evaluators.
    2. Search for the evaluator by name (e.g., "Toxicity") in the returned list.
    3. Use the eval_id from the all_evaluators output for the evaluation.
    4. Do NOT use hardcoded or previously known eval_ids, as these may change.
    5. Only after these steps, call the evaluate tool with the correct eval_id and your input.


    DETERMINISTIC EVALS (Only for Deterministic Evals eval_id = '3')

    Steps to create a deterministic evaluation:
    1. Define placeholders that map to your data fields
       - Choose meaningful placeholder names that reflect the data being compared
       - Map each placeholder to the corresponding input field key
       Example: "placeholder1" -> 'response'
               "placeholder2" -> 'context'

    2. Write a clear rule prompt using the placeholders
       - Use double curly braces {{placeholder}} syntax
       - Make the evaluation criteria explicit
       Example: "Is the {{placeholder1}} factually supported by the {{placeholder2}}?"

    3. Specify the valid evaluation choices
       - Define an array of possible outcomes
       - Keep choices clear and unambiguous
       Example: ["Yes", "No"] or ["Correct", "Incorrect"] or ["Positive", "Negative", "Neutral"]

    4. Provide input data matching the placeholder mapping
       - Input field keys must match the values of the corresponding placeholder
       - Include all required fields for evaluation
       - Also ensure when providing the url for the image, it is a valid url and input field key is image_url and url should be absolute path
       - Also ensure when providing the url for the audio, it is a valid url and input field key is input_audio and url should be absolute path

    Example payload:
    {
        "eval_templates": [
            {
                "eval_id": "3",
                "config": {
                    "input": {
                        "placeholder1": "input_key1",
                        "placeholder2": "input_key2"
                    },
                    "rule_prompt": "can you please check if the {{placeholder1}} is grounded in {{placeholder2}}",
                    "choices": [
                        "Yes",
                        "No"
                    ],
                    "multi_choice": False
                }
            }
        ],
        "inputs": [
            {
                "input_key1": "value1",
                "input_key2": "value2"
            }
        ]
    }
    """

EVALUATE_CONFIG_DESCRIPTION = """
    Config for the evaluation. The config object may contain the following parameters depending on the evaluator type:

    For Deterministic Evals:
    - input: Input data or parameters for the evaluation rule
    - choices: Set of possible choices for multiple-choice outputs
    - rule_prompt: Specific prompt or rule to evaluate against Use the variable {input} in the prompt
    - multi_choice: Boolean flag for multiple-choice output format

    For Similarity & Text Analysis:
    - comparator: Algorithm for text comparison (e.g. CosineSimilarity)
    - failure_threshold: Numerical threshold for similarity comparison
    - substring: Characters to check at text start/end
    - case_sensitive: Boolean for case-sensitive text matching
    - keywords: List of words/phrases to check for
    - max_length/min_length: Character length constraints
    - pattern: Regex pattern for text matching

    For AI/Model Based:
    - model: Language model to use (e.g. gpt-4, claude-3)
    - check_internet: Boolean to allow internet access
    - eval_prompt: Prompt template for AI evaluation
    - system_prompt: System context for AI agent

    For API/External:
    - url: API endpoint URL
    - headers: HTTP request headers
    - payload: Request body data

    For Custom:
    - code: Custom Python code string
    - validations: JSON validation rules
    - criteria: Natural language evaluation criteria
    """

ALL_EVALUATORS_DESCRIPTION = """
    Get all evaluators and their configurations, sorted in a specific order:
    1. CUSTOM evaluators first - These are user-defined custom evaluations
    2. FUTURE_EVALS evaluators second - FutureAGI's proprietary evaluators
    3. All remaining evaluators last - Standard/default evaluators

    The returned evaluators will include their complete configurations and metadata.

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
        return {"error": str(e)}


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
        return {"error": str(e)}


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
        return {"error": str(e)}


async def evaluate(eval_templates: List[dict], inputs: List[dict]) -> dict:
    """
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
            current_eval_template = EvalTemplate(config=template_input["config"])
            current_eval_template.eval_id = template_input["eval_id"]
            constructed_eval_templates.append(current_eval_template)

        constructed_inputs = []
        for input_item in inputs:
            # Dynamically create a class inheriting from TestCase with input fields
            input_fields = {k: Optional[type(v)] for k, v in input_item.items()}
            DynamicTestCase = type(
                "DynamicTestCase",
                (MLLMTestCase,),
                {
                    "__annotations__": input_fields,
                    "model_config": ConfigDict(extra="allow"),
                },
            )

            # Initialize the dynamic class with input values
            current_input = DynamicTestCase(**input_item)
            constructed_inputs.append(current_input)

        eval_results = eval_client.evaluate(
            constructed_eval_templates, constructed_inputs
        )
        return eval_results.model_dump()
    except Exception as e:
        logger.error(f"Error during evaluation: {str(e)}", exc_info=True)
        return {"error": str(e)}


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
        return evaluators
    except Exception as e:
        logger.error(f"Failed to fetch evaluators: {str(e)}", exc_info=True)
        return {"error": str(e)}

import os
import json
from typing import List

from fi.evals import EvalClient
from fi.evals.templates import EvalTemplate
from fi.api.auth import APIKeyAuth
from fi.api.types import RequestConfig, HttpMethod
from src.models import Evaluation
from fi.testcases import TestCase
from src.logger import get_logger
from src.tools.routes import Routes

logger = get_logger()


def get_eval_structure(template_id: str):
    """Get the structure of an evaluation using the template_id.

    Args:
        template_id: ID of the evaluation template
    """
    request_handler = APIKeyAuth(
        os.getenv("FI_API_KEY"), os.getenv("FI_SECRET_KEY"), os.getenv("FI_BASE_URL")
    )
    url = Routes.eval_structure(template_id)
    config = RequestConfig(method=HttpMethod.POST, url=url, json={"eval_type": "preset"})

    try:
        response = request_handler.request(config)
        return response.json()
    except Exception as e:
        logger.error(f"Failed to get evaluation structure: {str(e)}", exc_info=True)
        return json.dumps({"error": str(e)})


def get_evals_list_for_create_eval(eval_type: str) -> dict:
    """Get list of evaluations. Need to call this only when creating an evaluation.
    for this you have first fetch all the evaluators using the all_evaluators and then use the get_eval_structure tool to get the structure of the evaluation.
    eval_type can be preset, user
    Returns:
        List[str]: List of evaluation templates and their configurations
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


def create_eval(eval_name: str, template_id: str, config: dict) -> dict:
    """Create an evaluation template input object.
    Before creating an evaluation fetch evals list using the get_evals_list_for_create_eval tool.
    The template_id is the id of the evaluation template.
    eval_name is the name of the evaluation you are creating.
    Construct the config using the output of the get_evals_list_for_create_eval tool and the get_eval_structure tool.

    Args:
        eval_name: Name of the evaluation
        template_id:  string uuid of the evaluation template
        config: Configuration object adhering to CreateEvalConfig model
            mapping: Mapping dictionary containing key as a required fields for the evaluation structure and value as the example value
            config: Configuration dictionary containing the config['config'] for the evaluation structure
            model: model name like gpt-4o, claude-3-5-sonnet, etc.
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


def evaluate(eval_templates: List[Evaluation], inputs: List[TestCase]) -> dict:
    """
    First Fetch the all the evaluators using the all_evaluators tool.
    Then find the eval_id from the all_evaluators list.
    Then evaluate the inputs against the eval templates.

    Args:
        eval_templates: List of evaluation template inputs
        inputs: List of test cases to evaluate
    """

    try:
        eval_client = EvalClient()
        constructed_eval_templates = []

        for template_input in eval_templates:
            current_eval_template = EvalTemplate(config=template_input.config.model_dump())
            current_eval_template.eval_id = template_input.eval_id
            constructed_eval_templates.append(current_eval_template)

        eval_results = eval_client.evaluate(constructed_eval_templates, inputs)
        return eval_results
    except Exception as e:
        logger.error(f"Error during evaluation: {str(e)}", exc_info=True)
        return json.dumps({"error": str(e)})


def all_evaluators() -> dict:
    """Get all evaluators and their configurations

    When called will return all the evaluators, their functions and their configurations.

    Returns:
        List[Evaluator]
    """
    try:
        eval_client = EvalClient()
        evaluators = eval_client.list_evaluations()
        return json.dumps(evaluators)
    except Exception as e:
        logger.error(f"Failed to fetch evaluators: {str(e)}", exc_info=True)
        return json.dumps({"error": str(e)})

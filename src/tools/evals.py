import os
import json
import requests
from typing import List

from fi.evals import EvalClient
from fi.evals.templates import EvalTemplate
from models import EvalTemplateInput
from fi.testcases import TestCase



def get_eval_structure(template_id: str):
    """Get the structure of an evaluation using the template_id.

    Args:
        template_id: ID of the evaluation template
    """
    url = (
        os.getenv("FI_BASE_URL")
        + f"/model-hub/develops/2063cf96-40fc-4840-b5cd-ce48f06c24ea/get_eval_structure/{template_id}/"
    )
    headers = {
        "Accept": "application/json",
        "X-Api-Key": os.getenv("FI_API_KEY"),
        "X-Secret-Key": os.getenv("FI_SECRET_KEY"),
    }
    json_data = {"eval_type": "preset"}

    try:
        response = requests.post(url, headers=headers, json=json_data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


def get_evals_list_for_create_eval(eval_type: str):
    """Get list of evaluations. Need to call this only when creating an evaluation.
    for this you have first fetch all the evaluators using the all_evaluators and then use the get_eval_structure tool to get the structure of the evaluation.
    eval_type can be preset, user
    Returns:
        List[str]: List of evaluation templates and their configurations
    """
    url = (
        os.getenv("FI_BASE_URL")
        + "/model-hub/develops/2063cf96-40fc-4840-b5cd-ce48f06c24ea/get_evals_list/"
    )
    headers = {
        "Accept": "application/json",
        "X-Api-Key": os.getenv("FI_API_KEY"),
        "X-Secret-Key": os.getenv("FI_SECRET_KEY"),
    }
    json_data = {"eval_type": eval_type, "search_text": ""}

    try:
        response = requests.post(url, headers=headers, json=json_data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


def create_eval(eval_name: str, template_id: str, config: dict):
    """Create an evaluation template input object.
    Before creating an evaluation fetch evals list using the get_evals_list_for_create_eval tool.
    The template_id is the id of the evaluation template.
    eval_name is the name of the evaluation you are creating.
    Construct the config using the output of the get_evals_list_for_create_eval tool and the get_eval_structure tool.


    Args:
        eval_name: Name of the evaluation
        template_id:  string uuid of the evaluation template
        config: Configuration dictionary containing mapping, config and other settings
            mapping: Mapping dictionary containing key as a required fields for the evaluation structure and value as the example value
            config: Configuration dictionary containing the config['config'] for the evaluation structure
            model: model name like gpt-4o, claude-3-5-sonnet, etc.


    example:
    create_eval(
        eval_name="my_eval",
        template_id="da0ed35d-bc41-40dd-876a-6bea05998dcd",
        config={
            "mapping": {"text": "This is a test"},
            "config": {},
            "model": "gpt-4o"
        }
    )
    """

    # Make request to run evaluation
    url = os.getenv("FI_BASE_URL") + "/model-hub/run-eval"
    payload = {
        "template_id": template_id,
        "is_run": False,
        "saveAsTemplate": True,
        "log_ids": [],
        "name": eval_name,
        "config": config,
    }
    headers = {
        "Accept": "application/json",
        "X-Api-Key": os.getenv("FI_API_KEY"),
        "X-Secret-Key": os.getenv("FI_SECRET_KEY"),
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error making request to evaluation endpoint: {str(e)}")
        return {"error": str(e)}


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


def all_evaluators():
    """Get all evaluators and their configurations

    When called will return all the evaluators, their functions and their configurations.

    Returns:
        List[Evaluator]
    """
    eval_client = EvalClient()
    return json.dumps(eval_client.list_evaluations())

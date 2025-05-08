import asyncio
import time

import pytest

# Import tool functions directly
from futureagi_mcp_server.tools.evals import (
    all_evaluators,
    create_eval,
    evaluate,
    get_eval_structure,
    get_evals_list_for_create_eval,
)

path_to_image = "./tests/testimage.png"


@pytest.fixture
def eval_request():
    evals = asyncio.run(all_evaluators())
    template_id = None
    for eval_item in evals:
        if eval_item["eval_id"] == 5:
            template_id = eval_item["id"]
            break
    return {
        "eval_name": f"test_evaluation_{str(time.time())}",
        "template_id": template_id,
        "config": {
            "mapping": {
                "context": "This is a test input",
                "output": "This is the expected output",
            },
            "config": {},
            "model": "gpt-4o",
        },
    }


@pytest.fixture
def batch_eval_request():
    return {
        "eval_templates": [
            {
                "eval_id": "1",
                "config": {"criteria": "Test criteria", "model": "gpt-4o"},
            }
        ],
        "inputs": [
            {
                "text": "Test input 1",
                "output": "Test output 1",
                "criteria": "Test criteria",
            },
            {
                "text": "Test input 2",
                "output": "Test output 2",
                "criteria": "Test criteria",
            },
        ],
    }


@pytest.fixture
def batch_eval_request_with_config():
    return {
        "eval_templates": [{"eval_id": "9", "config": {"check_internet": False}}],
        "inputs": [
            {
                "input": "What is the capital of France?",
                "context": "Paris is the capital and largest city of France. Located on the Seine River in the northern part of the country, it is a major European city and a global center for art, fashion, gastronomy and culture.",
            }
        ],
    }


@pytest.mark.asyncio
async def test_get_evals_list():
    """Test getting list of available evaluations"""
    # Call function directly
    response_data = await get_evals_list_for_create_eval(eval_type="preset")

    # Assert directly on the returned dict
    assert "status" in response_data
    assert isinstance(response_data.get("result"), dict)
    assert isinstance(response_data.get("result").get("evals"), list)


@pytest.mark.asyncio
async def test_get_eval_structure():
    """Test getting evaluation structure"""
    evals = await all_evaluators()
    template_id = evals[0]["id"]
    # Call function directly
    response_data = await get_eval_structure(template_id=template_id)

    # Assert directly on the returned dict
    assert "status" in response_data


@pytest.mark.asyncio
async def test_create_eval(eval_request):
    """Test creating an evaluation"""
    # Call function directly, unpacking the fixture dict
    response_data = await create_eval(**eval_request)

    # Assert directly on the returned dict
    assert "status" in response_data


@pytest.mark.asyncio
async def test_evaluate(batch_eval_request):
    """Test batch evaluation"""
    # Call function directly, unpacking the fixture dict
    response_data = await evaluate(**batch_eval_request)

    assert "eval_results" in response_data


@pytest.mark.asyncio
async def test_batch_eval_with_config(batch_eval_request_with_config):
    """Test batch evaluation with config"""
    # Call function directly, unpacking the fixture dict
    response_data = await evaluate(**batch_eval_request_with_config)

    # Assert directly on the returned list/dict
    # Assuming evaluate returns a dict with 'eval_results'
    assert "eval_results" in response_data


@pytest.fixture
def deterministic_eval_payload():
    return {
        "eval_templates": [
            {
                "eval_id": "3",
                "config": {
                    "input": {"input1": "response", "input2": "context"},
                    "choices": ["Yes", "No"],
                    "rule_prompt": "Is the {{input1}} grounded in {{input2}}?",
                    "multi_choice": False,
                },
            }
        ],
        "inputs": [
            {
                "response": "The sky is blue.",
                "context": "The sky is blue because of the way sunlight interacts with Earth's atmosphere.",
            },
            {
                "response": "Grass is green.",
                "context": "Grass appears green due to the presence of chlorophyll.",
            },
        ],
    }


@pytest.mark.asyncio
async def test_deterministic_eval(deterministic_eval_payload):
    """Test deterministic evaluation"""
    response_data = await evaluate(**deterministic_eval_payload)
    assert "eval_results" in response_data
    assert isinstance(response_data["eval_results"], list)
    # Optionally print or check the results
    print("Deterministic Eval Results:", response_data["eval_results"])


@pytest.mark.asyncio
async def test_mllm_deterministic_eval():
    """Test MLLM evaluation"""
    mllm_eval_payload = {
        "eval_templates": [
            {
                "eval_id": "3",
                "config": {
                    "input": {"input1": "input", "input2": "image_url"},
                    "choices": ["Yes", "No"],
                    "rule_prompt": "Does the {{input1}} accurately describe what is shown in {{input2}}?",
                    "multi_choice": False,
                },
            }
        ],
        "inputs": [
            {
                "input": "An Asian man playing badminton with Indian",
                "image_url": path_to_image,
            }
        ],
    }

    response_data = await evaluate(**mllm_eval_payload)
    assert "eval_results" in response_data
    assert isinstance(response_data["eval_results"], list)

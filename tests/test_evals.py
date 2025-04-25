import time

import pytest

# Import tool functions directly
from src.tools.evals import (
    create_eval,
    evaluate,
    get_eval_structure,
    get_evals_list_for_create_eval,
)


@pytest.fixture
def eval_request():
    return {
        "eval_name": f"test_evaluation_{str(time.time())}",
        "template_id": "fbb17917-54af-4b73-ba42-7ec183e74b48",
        "config": {
            "mapping": {
                "text": "This is a test input",
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
        "eval_templates": [
            {"eval_id": "9", "config": {"config": {"check_internet": False}}}
        ],
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
    template_id = "fbb17917-54af-4b73-ba42-7ec183e74b48"
    # Call function directly
    response_data = await get_eval_structure(template_id=template_id)

    # Assert directly on the returned dict
    print("*" * 100)
    print(response_data)
    print("*" * 100)
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

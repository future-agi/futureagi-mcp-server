import pytest
import json
from src.server import mcp
import asyncio
import time


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


@pytest.mark.asyncio
async def test_get_evals_list():
    """Test getting list of available evaluations"""
    response = await mcp.call_tool(
        "get_evals_list_for_create_eval", {"eval_type": "preset"}
    )
    result = response[0]

    if isinstance(result, str):
        error_data = json.loads(result)
        assert "error" in error_data
    else:
        response_data = json.loads(result.text)
        assert "status" in response_data
        assert isinstance(response_data.get("result"), dict)
        assert isinstance(response_data.get("result").get("evals"), list)


@pytest.mark.asyncio
async def test_get_eval_structure():
    """Test getting evaluation structure"""
    template_id = "fbb17917-54af-4b73-ba42-7ec183e74b48"
    response = await mcp.call_tool("get_eval_structure", {"template_id": template_id})
    result = response[0]
    if isinstance(result, str):
        error_data = json.loads(result)
        assert "error" in error_data
    else:
        response_data = json.loads(result.text)
        print("*" * 100)
        print(response_data)
        print("*" * 100)
        assert "status" in response_data


@pytest.mark.asyncio
async def test_create_eval(eval_request):
    """Test creating an evaluation"""
    response = await mcp.call_tool("create_eval", eval_request)
    result = response[0]

    if isinstance(result, str):
        error_data = json.loads(result)
        assert "error" in error_data
    else:
        response_data = json.loads(result.text)
        assert "status" in response_data


@pytest.mark.asyncio
async def test_evaluate(batch_eval_request):
    """Test batch evaluation"""
    response = await mcp.call_tool("evaluate", batch_eval_request)
    result = response[0]

    if isinstance(result, str):
        error_data = json.loads(result)
        assert "error" in error_data
    else:
        response_data = json.loads(result.text)
        assert "eval_results" in response_data


import uuid

import pytest

from futureagi_mcp_server.tools.syntheticdatagen import generate_synthetic_data


@pytest.fixture
def sample_synthetic_config():
    return {
        "dataset": {
            "name": "Test Synthetic Dataset " + str(uuid.uuid4()),
            "description": "A synthetic dataset for testing purposes.",
            "objective": "To test synthetic data generation.",
            "patterns": "Keep the tone formal.",
        },
        "num_rows": 10,
        "columns": [
            {
                "name": "user_id",
                "description": "A unique identifier for the user.",
                "data_type": "integer",
                "property": {"min": 1, "max": 1000},
            },
            {
                "name": "message",
                "description": "A message sent by the user.",
                "data_type": "text",
                "property": {"max_length": "50", "min_length": "5"},
            },
            {
                "name": "is_active",
                "description": "Whether the user is active.",
                "data_type": "boolean",
                "property": {},
            },
        ],
    }


@pytest.mark.asyncio
async def test_generate_synthetic_data(sample_synthetic_config):
    config = sample_synthetic_config
    result = await generate_synthetic_data(
        dataset=config["dataset"],
        num_rows=config["num_rows"],
        columns=config["columns"],
    )
    assert isinstance(result, dict)
    assert (
        "error" not in result
    ), f"Synthetic data generation failed: {result.get('error')}"
    assert "status" in result, "Response missing status field"
    assert result["status"] is True, "Status should be true"
    assert "result" in result, "Response missing result field"
    assert isinstance(result["result"], dict), "Result should be a dictionary"
    assert "message" in result["result"], "Result missing message field"
    assert "data" in result["result"], "Result missing data field"
    assert isinstance(result["result"]["data"], dict), "Data should be a dictionary"
    assert "id" in result["result"]["data"], "Data missing id field"
    assert "name" in result["result"]["data"], "Data missing name field"
    assert (
        result["result"]["data"]["name"] == config["dataset"]["name"]
    ), "Dataset name mismatch"

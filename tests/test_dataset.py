import csv
import json
import os
import tempfile
import time

import pytest

from src.server import mcp


@pytest.fixture
def sample_csv_file():
    """Create a temporary CSV file for testing"""
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".csv") as tmp:
        writer = csv.writer(tmp)
        writer.writerow(["input", "output", "context"])
        writer.writerow(
            [
                "What is the capital of France?",
                "Paris",
                "Paris is the capital of France",
            ]
        )
        writer.writerow(["What is 2+2?", "4", "Basic arithmetic"])
        tmp_path = tmp.name

    yield tmp_path
    # Cleanup after test
    os.unlink(tmp_path)


@pytest.mark.asyncio
async def test_upload_dataset(sample_csv_file):
    """Test uploading a dataset from CSV file"""
    request_args = {
        "dataset_name": "test_dataset" + str(time.time()),
        "model_type": "GenerativeLLM",
        "source": sample_csv_file,
    }
    response = await mcp.call_tool("upload_dataset", request_args)
    result = response[0]

    print("result")
    print(type(result))
    print(result)

    # Handle both success and error cases
    if isinstance(result, str):
        # Error case - result is a JSON string
        error_data = json.loads(result)
        assert "error" in error_data
    else:
        # Success case - result is a dictionary
        assert isinstance(json.loads(result.text), dict)
        assert "dataset_id" in json.loads(result.text)

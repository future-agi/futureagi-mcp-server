import csv
import os
import tempfile
import uuid

import pytest

from src.tools.datasets import add_evaluation_to_dataset, upload_dataset


@pytest.fixture
def sample_csv_file():
    """Create a temporary CSV file for testing"""
    # Need os imported for unlink
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
    try:
        os.unlink(tmp_path)  # os.unlink needs os imported
    except FileNotFoundError:
        pass


@pytest.mark.asyncio
async def test_upload_dataset(sample_csv_file):
    """Test uploading a dataset from CSV file"""
    dataset_name = f"test_dataset_{uuid.uuid4()}"
    request_args = {
        "dataset_name": dataset_name,
        "model_type": "GenerativeLLM",
        "source": sample_csv_file,
    }
    response_data = await upload_dataset(**request_args)

    assert isinstance(response_data, dict)
    if response_data.get("error"):
        pytest.fail(f"Upload failed: {response_data.get('error')}")

    assert "dataset_id" in response_data


@pytest.mark.asyncio
async def test_add_evaluation_to_dataset(sample_csv_file):
    """Test adding an evaluation to a dataset"""

    dataset_name = f"test_ds_for_eval_{uuid.uuid4()}"
    upload_args = {
        "dataset_name": dataset_name,
        "model_type": "GenerativeLLM",
        "source": sample_csv_file,
    }
    upload_response = await upload_dataset(**upload_args)
    assert isinstance(upload_response, dict)
    assert (
        upload_response.get("status") == "success"
    ), f"Prerequisite dataset upload failed: {upload_response.get('error')}"

    request_args = {
        "eval_id": "5",
        "dataset_name": dataset_name,
        "output_column_name": "output",
        "context_column_name": "context",
        "name": "adherence_eval_test",
    }

    response_data = await add_evaluation_to_dataset(**request_args)

    assert isinstance(response_data, dict)
    if response_data.get("error"):
        pytest.fail(f"Add evaluation failed: {response_data.get('error')}")

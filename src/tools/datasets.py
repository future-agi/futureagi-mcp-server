import json
import os

from fi.datasets import DatasetClient
from fi.datasets.types import DatasetConfig

from src.logger import get_logger

logger = get_logger()


def upload_dataset(dataset_name: str, model_type: str, source: str) -> dict:
    """Upload a dataset to FutureAGI

    Args:
        dataset_name: Name of the dataset to create
        model_type: Type of model (e.g., "GenerativeLLM", "GenerativeImage")
        source: Optional source for the dataset. Can be:
            - A file path (str) for local files

        Example:
        dataset_name = "my_dataset"
        model_type = "GenerativeLLM"
        source = "/Users/name/Downloads/test.csv"

    Returns:
        dict: Dataset configuration including ID and name
    """

    try:
        dataset_config = DatasetConfig(name=dataset_name, model_type=model_type)

        dataset_client = DatasetClient(
            dataset_config=dataset_config,
            fi_api_key=os.getenv("FI_API_KEY"),
            fi_secret_key=os.getenv("FI_SECRET_KEY"),
            fi_base_url=os.getenv("FI_BASE_URL"),
        )

        result = None
        if source and os.path.exists(source):
            result = dataset_client.create(source=source)
        else:
            result = dataset_client.create()

        if result.dataset_config.id:
            return json.dumps(
                {"status": "success", "dataset_id": str(result.dataset_config.id)}
            )
        else:
            return json.dumps({"error": "Dataset creation/upload failed unexpectedly."})

    except Exception as e:
        logger.error(f"Dataset operation failed: {e}", exc_info=True)
        return json.dumps({"error": str(e)})

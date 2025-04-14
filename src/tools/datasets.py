import os
from fi.datasets import DatasetClient
from fi.datasets.types import DatasetConfig


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

    # Create dataset config
    config = DatasetConfig(name=dataset_name, model_type=model_type)

    # Create dataset client
    client = DatasetClient(
        dataset_config=config,
        fi_api_key=os.getenv("FI_API_KEY"),
        fi_secret_key=os.getenv("FI_SECRET_KEY"),
        fi_base_url=os.getenv("FI_BASE_URL"),
    )

    # Handle source if provided
    if source:
        if isinstance(source, str):
            # Local file upload
            client.create(source=source)
    else:
        # Create empty dataset
        client.create()

    return {
        "id": client.dataset_config.id,
        "name": client.dataset_config.name,
        "model_type": client.dataset_config.model_type,
    } 
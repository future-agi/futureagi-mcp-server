import json
import os
from typing import Any, Dict

from fi.datasets import DatasetClient
from fi.datasets.types import DatasetConfig, ModelTypes
from fi.evals.templates import EvalTemplate

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

        if result and result.dataset_config and result.dataset_config.id:
            return json.dumps(
                {
                    "status": "success",
                    "dataset_id": str(result.dataset_config.id),
                    "dataset_name": result.dataset_config.name,
                }
            )
        else:
            logger.error(
                "Dataset creation/retrieval seemed successful but failed to get ID."
            )
            return json.dumps(
                {
                    "error": "Dataset creation/upload failed unexpectedly or dataset ID missing."
                }
            )

    except Exception as e:
        logger.error(
            f"Dataset operation failed with unexpected error: {e}", exc_info=True
        )
        return json.dumps({"error": f"An unexpected error occurred: {str(e)}"})


def add_evaluation_to_dataset(
    dataset_name: str,
    name: str,
    eval_id: str,
    input_column_name: str = "",
    output_column_name: str = "",
    context_column_name: str = "",
    expected_column_name: str = "",
    save_as_template: bool = False,
    reason_column: bool = False,
    config: Dict[str, Any] = {},
) -> dict:
    """Adds an evaluation column to a specified dataset and runs the evaluation.
    Fetch the eval structure from the eval_id and use it to add the evaluation to the dataset.

    Use the required keys and column names of the dataset to deduce the input_column_name, output_column_name, context_column_name, expected_column_name.

    Args:
        dataset_name (str): Name of the target dataset to which the evaluation will be added.
        name (str): Name for the new evaluation column that will be created in the dataset.
        eval_id (str): eval_id of the evaluation template to use (e.g., '1', '9', '11', etc.).
        input_column_name (Optional[str]): Name of the column in the dataset containing input data, if required by the chosen eval template.
        output_column_name (Optional[str]): Name of the column in the dataset containing output/response data, if required by the chosen eval template.
        context_column_name (Optional[str]): Name of the column in the dataset containing context data, if required by the chosen eval template.
        expected_column_name (Optional[str]): Name of the column in the dataset containing expected response data, if required by the chosen eval template.
        save_as_template (bool): If True, saves this evaluation configuration as a new template for future use.
        reason_column (bool): If True, adds an additional column to explain the evaluation reason or score.
        config (Optional[Dict[str, Any]]): Additional configuration parameters specific to the chosen evaluation template.

    Returns:
        dict: A dictionary indicating the success or failure of the operation, with relevant status messages.
    """
    try:
        logger.info(
            f"Adding evaluation '{name}' using template '{eval_id}' to dataset '{dataset_name}'"
        )
        template_classes = {
            cls.eval_id: cls.__name__ for cls in EvalTemplate.__subclasses__()
        }
        eval_template = template_classes[eval_id]
        dataset_client = DatasetClient(
            dataset_config=DatasetConfig(
                name=dataset_name, model_type=ModelTypes.GENERATIVE_LLM
            ),
            fi_api_key=os.getenv("FI_API_KEY"),
            fi_secret_key=os.getenv("FI_SECRET_KEY"),
            fi_base_url=os.getenv("FI_BASE_URL"),
        )
        dataset_client.add_evaluation(
            name=name,
            eval_template=eval_template,
            input_column_name=input_column_name,
            output_column_name=output_column_name,
            context_column_name=context_column_name,
            expected_column_name=expected_column_name,
            save_as_template=save_as_template,
            run=True,
            reason_column=reason_column,
            config=config,
        )

        logger.info(
            f"Successfully added and triggered evaluation {name} on dataset {dataset_name}"
        )
        return {
            "status": "success",
            "message": f"Evaluation {name} added and triggered for dataset {dataset_name}.",
        }

    except Exception as e:
        logger.error(
            f"An unexpected error occurred while adding evaluation to dataset {dataset_name}: {e}",
            exc_info=True,
        )
        return {"status": "error", "message": f"An unexpected error occurred: {str(e)}"}

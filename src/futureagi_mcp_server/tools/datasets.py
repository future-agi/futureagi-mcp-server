import os
from typing import Any, Dict

from fi.datasets import DatasetClient
from fi.datasets.types import DatasetConfig, ModelTypes
from fi.evals.templates import EvalTemplate

from ..logger import get_logger

logger = get_logger()


UPLOAD_DATASET_DESCRIPTION = """
    This function should be used to upload a dataset to FutureAGI by either:

    Please follow these steps strictly before calling this function:
    1. Validate source file path:
       - Check if provided path is absolute using file system tools
       - If relative path, resolve against current working directory
       - Verify file exists and is readable
       - Return error if file not found or inaccessible
    2. File format validation:
       - Ensure file has supported extension (.csv, .json, etc.)
       - Validate file structure and contents
    3. Dataset creation:
       - If source file provided, use it to create dataset
       - If no source, initialize empty dataset structure
       - Apply any specified dataset configurations

    If the error says "Dataset already exists" then return the following retry with a different dataset name

    Args:
        dataset_name: Name of the dataset to create
        model_type: Type of model (e.g., "GenerativeLLM", "GenerativeImage")
        source: Optional source for the dataset. Can be:
            - A file path (str) for local files
            - This should be the absolute path to the file
            - If the user has not provided the absolute path, try finding the file in the current working directory
            - If the file is not found, return an error

    Example:
        dataset_name = "my_dataset"
        model_type = "GenerativeLLM"
        source = "/Users/name/Downloads/test.csv"

    Returns:
        dict: Dataset configuration including ID and name
    """

ADD_EVALUATION_TO_DATASET_DESCRIPTION = """

    Adds an evaluation column to a specified dataset and runs the evaluation.

    Please follow these steps strictly before calling this function:
    1. Validate eval_id format:
       - Ensure eval_id is an integer string (e.g. '1', '9', '11')
       - Do NOT use UUID format
       - Verify eval_id exists in all_evaluators output
    2. Fetch evaluation structure:
       - Get eval template structure using template_id which is the UUID of the eval template
       - Extract required keys from the eval template
       - Read the dataset columns either from the local file or download the dataset and read the columns
       - construct the required_keys_to_column_names dictionary
    3. For config generation, use the following steps:
       - Find the config['config'] dictionary in the eval template structure
       - You MUST add the keys present the config['config'] dictionary to the config dictionary


    WHEN ADDINGDETERMINISTIC EVALS (Only for Deterministic Evals eval_id = '3')

    You MUST follow these steps to add a deterministic evaluation:
    Add these to the config dictionary:
    1. Define placeholders that map to your column names
       Example: "placeholder1" -> column_name1
               "placeholder2" -> column_name2

    2. Write a clear rule prompt using the placeholders
       - Use double curly braces {{placeholder}} syntax
       - Make the evaluation criteria explicit
       Example: "Is the {{placeholder1}} factually supported by the {{placeholder2}}?"

    3. Specify the valid evaluation choices
       - Define an array of possible outcomes
       - Keep choices clear and unambiguous
       Example: ["Yes", "No"] or ["Correct", "Incorrect"] or ["Positive", "Negative", "Neutral"]
    4. No requirement for input_column_name, output_column_name, context_column_name, expected_column_name

    EXAMPLE PAYLOAD FOR DETERMINISTIC EVALS:
    {
        "name": "deterministic_evaluation",
        "eval_id": "3",
        "config": {
            "input": {
                "placeholder1": "column_name1",
                "placeholder2": "column_name2"
            },
            "rule_prompt": "can you please check if the {{placeholder1}} is grounded in {{placeholder2}}",
            "choices": ["Yes", "No"],
            "multi_choice": False
        },
        "required_keys_to_column_names": {
        }
    }
    """

DOWNLOAD_DATASET_DESCRIPTION = """
    This function is used to download a dataset from FutureAGI.
    It will return a dictionary with the dataset name, the file path, and the insights.

    Please follow these steps strictly before calling this function:
    1. Validate dataset_name format:
       - Ensure dataset_name is a string
       - Verify dataset_name exists in FutureAGI
    2. Validate file_path format:
       - Ensure file_path is a string
       - Verify file_path is a valid path
       - If the Obsolute path is not provided, add the current working directory to the file_path
"""

DATASET_EVALUATION_INSIGHTS_DESCRIPTION = """
    This function is used to get the insights of the evaluation dataset.
    It will return a dictionary with the evaluation insights.
    Please follow these steps strictly before calling this function:
    1. Validate dataset_name format:
       - Ensure dataset_name is a string
       - Verify dataset_name exists in FutureAGI

    The function returns evaluation insights including:
    - Overall statistics:
        - totalRows: Total number of rows evaluated
        - passRate: Overall pass rate percentage

    - Per metric results containing:
        - metricName: Name of the evaluation metric
        - id: Unique identifier for the metric
        - totalRows: Number of rows evaluated for this metric
        - averageScore: Average score across all rows (0-100)
        - successRate: Success rate percentage
        - outputType: Type of output (e.g. "numeric")
        - percentile scores: p5 through p100 showing score distribution
"""


async def upload_dataset(dataset_name: str, model_type: str, source: str) -> dict:
    """
    This function is used to upload a dataset to FutureAGI.
    If a source is provided, check if it is a valid absolute path.
    If not, try finding the file in the current working directory.
    If the file is not found, return an error.
    If a source is not provided, create a new dataset.

    Args:
        dataset_name: Name of the dataset to create
        model_type: Type of model (e.g., "GenerativeLLM", "GenerativeImage")
        source: Optional source for the dataset. Can be:
            - A file path (str) for local files
            - This should be the absolute path to the file
            - If the user has not provided the absolute path, try finding the file in the current working directory
            - If the file is not found, return an error

        Example:
        dataset_name = "my_dataset"
        model_type = "GenerativeLLM"
        source = "/Users/name/Downloads/test.csv"

    Returns:
        dict: Dataset configuration including ID and name
    """

    try:
        try:
            dataset_config = DatasetConfig(
                name=dataset_name, model_type=ModelTypes(model_type)
            )
        except ValueError:
            return {
                "error": f"Invalid model_type: '{model_type}'. Valid types are: {', '.join([t.value for t in ModelTypes])}"
            }

        dataset_client = DatasetClient(
            dataset_config=dataset_config,
            fi_api_key=os.getenv("FI_API_KEY"),
            fi_secret_key=os.getenv("FI_SECRET_KEY"),
            fi_base_url=os.getenv("FI_BASE_URL"),
        )

        result = None
        if source and os.path.exists(source):
            result = dataset_client.create(source=source)
        elif not source:
            result = dataset_client.create()
        elif source and not os.path.exists(source):
            return {"error": f"File not found: {source}"}

        if result and result.dataset_config and result.dataset_config.id:
            return {
                "status": "success",
                "dataset_id": str(result.dataset_config.id),
                "dataset_name": result.dataset_config.name,
            }
        else:
            logger.error(
                "Dataset creation/retrieval seemed successful but failed to get ID."
            )
            return {
                "error": "Dataset creation/upload failed unexpectedly or dataset ID missing."
            }

    except Exception as e:
        logger.error(
            f"Dataset operation failed with unexpected error: {e}", exc_info=True
        )
        return {"error": str(e)}


async def add_evaluation_to_dataset(
    dataset_name: str,
    name: str,
    eval_id: str,
    required_keys_to_column_names: Dict[str, str],
    save_as_template: bool = False,
    reason_column: bool = False,
    config: Dict[str, Any] = None,
) -> dict:
    """
    Adds an evaluation column to a specified dataset and runs the evaluation.
    Fetch the eval structure from the eval_id NOT the UUID this is important.
    Eval id is the integer string of the eval template. Can find it in the output of the all_evaluators tool.

    Use the required keys and column names of the dataset to deduce the input_column_name, output_column_name, context_column_name, expected_column_name.

    Args:
        dataset_name (str): Name of the target dataset to which the evaluation will be added.
        name (str): Name for the new evaluation column that will be created in the dataset.
        eval_id (str): eval_id of the evaluation template to use (e.g., '1', '9', '11', etc.).
        required_keys_to_column_names (Dict[str, str]): A dictionary mapping required keys of the eval template to column names in the dataset.
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

        if config and "input" in config:
            new_input = []
            count = 1
            for key, column_name in config["input"].items():
                column_id = dataset_client.get_column_id(column_name)
                if column_id:
                    new_input.append(column_id)
                variable_name = f"variable_{count}"
                config["rule_prompt"] = config["rule_prompt"].replace(
                    key, variable_name
                )
                count += 1
            config["input"] = new_input

        dataset_client.add_evaluation(
            name=name,
            eval_template=eval_template,
            required_keys_to_column_names=required_keys_to_column_names,
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
        return {"error": str(e)}


async def download_dataset(dataset_name: str, file_path: str) -> dict:
    """
    Downloads a dataset from FutureAGI and saves it to a local file.
    """
    try:
        dataset_client = DatasetClient(
            dataset_config=DatasetConfig(
                name=dataset_name, model_type=ModelTypes.GENERATIVE_LLM
            ),
        )
        dataset_client.download(file_path=file_path)
        return {
            "status": "success",
            "message": f"Dataset {dataset_name} downloaded to {file_path}",
        }
    except Exception as e:
        logger.error(
            f"An unexpected error occurred while downloading dataset {dataset_name}: {e}",
            exc_info=True,
        )
        return {"error": str(e)}


async def get_evaluation_insights(dataset_name: str) -> dict:
    """
    Get the insights of the evaluation dataset.
    """
    try:
        dataset_client = DatasetClient(
            dataset_config=DatasetConfig(
                name=dataset_name, model_type=ModelTypes.GENERATIVE_LLM
            ),
        )
        insights = dataset_client.get_eval_stats()
        return insights
    except Exception as e:
        logger.error(
            f"An unexpected error occurred while getting evaluation insights for dataset {dataset_name}: {e}",
            exc_info=True,
        )
        return {"error": str(e)}

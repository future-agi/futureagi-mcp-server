from fi.api.auth import APIKeyAuth
from fi.api.types import HttpMethod, RequestConfig

from ..logger import get_logger
from .routes import Routes

logger = get_logger()


GENERATE_SYNTHETIC_DATA_DESCRIPTION = """
Generate a synthetic dataset by specifying the following:

1. Basic Metadata

- **Name (required):**
  Provide a clear, descriptive title for your dataset.

- **Description (required):**
  Describe the dataset you want to generate, including its purpose, the type of data it will contain, and the intended use case.

- **Use Case:**
  Specify the primary use case for your dataset (e.g., "Simulated customer support logs for LLM fine-tuning", "Classification dataset with evenly distributed labels").

- **Pattern (optional):**
  Define the structure or style of the data, such as "Follow a conversational pattern", "Keep the tone formal", or any other relevant instructions.

2. Define the Schema

- For every column, specify:
  - **Name:** (e.g., message, label, timestamp, transcript)
  - **Type:** Choose from: text, float, integer, boolean, array, json, datetime
  - **Properties:**
    - Add constraints (e.g., min/max, string patterns) to ensure realistic value ranges.
    - For categorical columns, specify allowed values or let the generator decide dynamically.
    - You can add more properties as needed, providing a name and description for each.

**Example Schema:**

- Column 1:
  Name: review_text
  Type: text
  Properties: None (freeform)

- Column 2:
  Name: rating
  Type: integer
  Properties: min: 1, max: 5

- Column 3:
  Name: sentiment
  Type: text
  Properties: Value: positive, negative, neutral

3. Set Row Count

- Specify the number of rows you want the dataset to contain.

4. Define Column Descriptions

- For each column, provide a detailed description to help the generator create rich, realistic data.

By following these steps, you can generate high-quality synthetic datasets tailored to your specific needs.

EXAMPLE CONFIG:
{
    "dataset": {
        "name": "Customer Support Logs",
        "description": "A dataset of customer support logs",
        "objective": "To simulate customer support logs for LLM fine-tuning",
        "patterns": "Follow a conversational pattern"
    },
    "num_rows": 50,
    "columns": [
        {
            "name": "customer_id",
            "description": "The ID of the customer",
            "data_type": "integer",
            "property": {}
        },
        {
            "name": "customer_name",
            "description": "The name of the customer",
            "data_type": "text",
            "property": {
                "max_length": "20",
                "value": "dynamic",
                "min_length": "17"
            }
        }
    ]
}
"""


async def generate_synthetic_data(dataset: dict, num_rows: int, columns: list[dict]):
    """
    Generate synthetic data based on the dataset configuration
    """
    try:
        request_handler = APIKeyAuth()

        data = {
            "dataset": {
                "name": dataset["name"],
                "description": dataset["description"],
                "objective": dataset["objective"],
                "patterns": dataset["patterns"],
            },
            "num_rows": num_rows,
            "columns": [
                {
                    "name": col["name"],
                    "description": col["description"],
                    "data_type": col["data_type"],
                    "property": col["property"],
                }
                for col in columns
            ],
        }

        request_config = RequestConfig(
            method=HttpMethod.POST,
            url=Routes.SYNTHETIC_DATA_GEN.value,
            json=data,
        )

        response = request_handler.request(request_config)

        if response.status_code == 200:
            return response.json()
        else:
            response_json = response.json()
            logger.error(f"Failed to generate synthetic data: {str(response_json)}")
            return {"error": "Failed to generate synthetic data " + str(response_json)}
    except Exception as e:
        logger.error(f"Error generating synthetic data: {e}")
        return {"error": str(e)}

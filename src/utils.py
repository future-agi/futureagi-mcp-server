import os

from src.logger import get_logger

logger = get_logger()


def setup_environment(api_key: str, secret_key: str, base_url: str):
    """Setup environment variables for the application"""
    os.environ["FI_API_KEY"] = api_key
    os.environ["FI_SECRET_KEY"] = secret_key
    os.environ["FI_BASE_URL"] = base_url

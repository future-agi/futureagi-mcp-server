import os

from .logger import get_logger

logger = get_logger()


def setup_environment(api_key: str, secret_key: str, base_url: str):
    """Setup environment variables for the application"""
    if not os.environ.get("FI_API_KEY") or not os.environ.get("FI_SECRET_KEY"):
        os.environ["FI_API_KEY"] = api_key
        os.environ["FI_SECRET_KEY"] = secret_key
    else:
        logger.info("Environment variables already set")
    if not os.environ.get("FI_BASE_URL"):
        os.environ["FI_BASE_URL"] = base_url
    else:
        logger.info("Base URL already set")

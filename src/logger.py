import os
import logging
from src.constants import LOGS_DIR, LOG_FILE, LOG_LEVEL

# Create logs directory if it doesn't exist
os.makedirs(LOGS_DIR, exist_ok=True)

MCP_LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "{levelname} {asctime} {module} {filename}:{funcName}:{lineno:d} {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "submodule_file": {
            "level": LOG_LEVEL,
            "class": "logging.handlers.RotatingFileHandler",
            "filename": LOG_FILE,
            "maxBytes": 1024 * 1024 * 5,  # 5MB
            "backupCount": 7,
            "formatter": "verbose",
        },
        "console": {
            "level": LOG_LEVEL,
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
    },
    "loggers": {
        "mcp": {
            "handlers": ["submodule_file", "console"],
            "level": LOG_LEVEL,
            "propagate": True,
        },
    },
}


def setup_logging(config=None):
    """Configure logging for the application.

    Args:
        config: Optional logging configuration dictionary. If not provided,
               uses the default MCP_LOGGING configuration.
    """
    if config:
        logging.config.dictConfig(config)
    else:
        logging.config.dictConfig(MCP_LOGGING)


# Global logger setup for the submodule
submodule_logger = logging.getLogger("futureagi-mcp")


def get_logger():
    """Get the configured logger instance.

    Returns:
        logging.Logger: The configured logger instance
    """
    return submodule_logger


# Example usage:
if __name__ == "__main__":
    setup_logging()
    logger = get_logger()
    logger.error("This is an error message")

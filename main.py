import asyncio

import click
import mcp
from mcp.server import NotificationOptions
from mcp.server.models import InitializationOptions

from src.constants import SERVER_NAME, SERVER_VERSION
from src.logger import get_logger, setup_logging
from src.server import get_server

setup_logging()
logger = get_logger()


@click.command()
@click.option(
    "--api-key",
    envvar="FI_API_KEY",
    required=True,
    help="FutureAGI API key",
)
@click.option(
    "--secret-key",
    envvar="FI_SECRET_KEY",
    required=True,
    help="FutureAGI secret key",
)
@click.option(
    "--base-url",
    envvar="FI_BASE_URL",
    default="https://api.futureagi.com",
    help="FutureAGI API base URL",
)
def main(
    api_key: str,
    secret_key: str,
    base_url: str,
):
    """Start the FutureAGI MCP server using stdio."""

    async def _run():
        logger.debug("Starting server via stdio...")

        # Use stdio_server context manager
        async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
            # Get the server instance from serve()
            server = get_server(
                api_key=api_key,
                secret_key=secret_key,
                base_url=base_url,
            )

            # Define initialization options
            init_options = InitializationOptions(
                server_name=SERVER_NAME,
                server_version=SERVER_VERSION,
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            )

            # Run the server
            await server.run(
                read_stream,
                write_stream,
                init_options,
            )

    logger.info("Running server...", flush=True)
    # Run the async function
    asyncio.run(_run())


if __name__ == "__main__":
    logger.info("Running main...", flush=True)
    main()

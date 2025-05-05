# Future AGI MCP Server

A powerful server implementation that integrates with the Future AGI SDK through the Model Context Protocol (MCP). This server provides tools which can be used to interact with Future AGI features.

## Features

🚀 Natural Language Evaluations—At Scale
Why write scripts when you can just ask? Whether it’s a single response or thousands, Future AGI MCP lets you run advanced evaluations like hallucination detection, sentiment analysis, or factuality scoring through a simple chat prompt. It auto-selects evaluators, runs them in the background, and delivers results—zero setup, maximum speed.

📂 Upload Datasets and Add Evaluations Instantly
Drop in a dataset and say the word. MCP handles file uploads, picks the right evaluators, and kicks off evaluations—all in the background, all from a single prompt. No GUIs, no manual tagging, just fast, intelligent data processing that works right inside your dev tools.

## Installation

1. Clone the repository:

```bash
git clone https://github.com/future-agi/futureagi-mcp-server.git
cd futureagi-mcp-server
```

2. Install uv

```bash
brew install uv
```

3. Install dependencies:

```bash
uv sync   # this will create a virtual environment if not present and installs necessary dependencies
```

## Configuring the Server to MCP Clients

To run the server:

```bash
python main.py
```

To Configure with MCP Clients like VS Code and Claude using local forked repository

```
{
  "mcpServers": {
    "FutureAGI-MCP": {
      "command": "uv",
      "args": [
        "--directory",
        "/path/to/futureagi-mcp-server",
        "run",
        "main.py"
      ],
      "env": {
        "FI_SECRET_KEY": "your_api_key",
        "FI_API_KEY": "your_secret_key",
        "FI_BASE_URL": "https://api.futureagi.com",
        "PYTHONPATH": "/path/to/futureagi-mcp-server"
      }
    }
  }
}
```

A simple Configuration using uvx and published package

```
{
  "mcpServers": {
    "FutureAGI-MCP": {
      "command": "uvx",
      "args": [
        "futureagi-mcp-server
      ],
      "env": {
        "FI_SECRET_KEY": "your_api_key",
        "FI_API_KEY": "your_secret_key",
      }
    }
  }
}
```

## Project Structure

```
futureagi-mcp-server/
├── src/                          # Source code directory
│   ├── server.py                 # Main server implementation
│   ├── utils.py                  # Utility functions
│   ├── constants.py              # Constants and configuration
│   ├── logger.py                 # Logging configuration
│   └── tools/                    # Tools directory
│       ├── evals.py              # Evaluation tools
│       ├── datasets.py           # Dataset tools
│       ├── protect.py            # Protection tools
│       └── routes.py             # Route management
├── tests/                        # Test directory
│   ├── test_dataset.py           # Dataset tests
│   ├── test_protect.py           # Protection tests
│   └── test_evals.py             # Evaluation tests
├── .pre-commit-conifg.yaml       # pre-commit hooks that run before every commit
├── pyproject.toml                # Project configuration and dependencies
├── uv.lock                       # Dependency lock file
├── .gitignore                    # Git ignore rules
└── README.md                     # This file

```

## Contribution are Welcome!

### Guidelines for contributing

* Clone the repository either using https or ssh
* Create the venv using `uv pip install ".[dev]"`
* This will create and install all the required dependencies in a virtual environment
* Ensure to activate the environment
* Make necessary changes and run git commit. It will run the pre-commit hooks. Solve any of the failed checks.

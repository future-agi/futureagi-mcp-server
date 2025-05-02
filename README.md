# Future AGI MCP Server

A powerful server implementation that integrates with the Future AGI SDK through the Model Context Protocol (MCP). This server provides tools which can be used to interact with Future AGI features.

## Features

🚀 Natural Language Evaluations—At Scale
Why write scripts when you can just ask? Whether it’s a single response or thousands, Futurea AGI MCP lets you run advanced evaluations like hallucination detection, sentiment analysis, or factuality scoring through a simple chat prompt. It auto-selects evaluators, runs them in the background, and delivers results—zero setup, maximum speed.

📂 Upload Datasets and Launch Evaluations Instantly
Drop in a dataset and say the word. MCP handles file uploads, picks the right evaluators, and kicks off evaluations—all in the background, all from a single prompt. No GUIs, no manual tagging, just fast, intelligent data processing that works right inside your dev tools.

## Requirements

- Python >= 3.10
- FutureAGI >= 0.5.10
- HTTPX >= 0.28.1
- MCP CLI >= 1.6.0
- Pydantic >= 2.11.2

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
uv sync   # this will create a virtual environment if not present
```

## Usage

To run the server:

```bash
python main.py
```

To Configure with MCP Clients like VS Code and Claude using local fork
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
├── pyproject.toml                # Project configuration and dependencies
├── uv.lock                       # Dependency lock file
├── .gitignore                    # Git ignore rules
└── README.md                     # This file

```

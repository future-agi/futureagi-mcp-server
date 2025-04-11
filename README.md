# Future AGI MCP Server

A powerful server implementation that integrates with the Future AGI SDK through the Model Context Protocol (MCP). This server provides a standardized and efficient interface for conducting advanced LLM operations, including system optimizations, performance evaluations, and experimental research.

## Description

This project serves as a bridge between your applications and Future AGI's capabilities through the Model Context Protocol (MCP). It enables standardized communication and interaction with Future AGI's powerful features, making it easier to implement and manage complex LLM-based operations.

## Features

- Evaluations
- Experimentation

## Requirements

- Python >= 3.13.1
- FutureAGI >= 0.5.7
- HTTPX >= 0.28.1
- MCP CLI >= 1.6.0
- Pydantic >= 2.11.2

## Installation

1. Clone the repository:

```bash
git clone https://github.com/yourusername/futureagi-mcp-server.git
cd futureagi-mcp-server
```

2. Create and activate a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate  # On Windows, use `.venv\Scripts\activate`
```

3. Install dependencies:

```bash
pip install -e .
```

## Usage

To run the server:

```bash
python main.py
```

## Project Structure

```
futureagi-mcp-server/
├── src/                          # Source code directory
│   ├── server.py                 # Main server implementation
│   ├── models.py                 # Data models and schemas
│   ├── templates.py              # Template definitions
│   └── utils.py                  # Utility functions
├── main.py                       # Main entry point
├── pyproject.toml                # Project configuration and dependencies
├── uv.lock                       # Dependency lock file
├── .gitignore                    # Git ignore rules
└── README.md                     # This file

```

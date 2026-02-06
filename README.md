# Issues-FS__CLI

[![pypi package](https://badge.fury.io/py/issues-fs-cli.svg)](https://pypi.org/project/issues-fs-cli/)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![License: Apache 2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://www.apache.org/licenses/LICENSE-2.0)

**Git-native graph-based issue tracking from the command line.**

Issues-FS CLI is a command-line interface for the Issues-FS ecosystem. It provides a Git-like experience for creating, managing, and querying issues stored as files in your repository.

## Installation

```bash
pip install issues-fs-cli
```

Or with Poetry:

```bash
poetry add issues-fs-cli
```

## Quick Start

```bash
# Initialize a new Issues-FS repository
issues-fs init

# Create your first bug
issues-fs create bug "Login button not responding"

# Create a task
issues-fs create task "Implement rate limiting" --priority P1

# List all issues
issues-fs list

# Show issue details
issues-fs show Bug-1

# Update issue status
issues-fs update Bug-1 --status confirmed

# Link issues
issues-fs link Bug-1 blocks Task-1

# Add a comment
issues-fs comment Bug-1 "Investigating the root cause"

# View comments
issues-fs comments Bug-1
```

## Commands Reference

### Core Commands

| Command | Description |
|---------|-------------|
| `issues-fs init` | Initialize a new `.issues/` repository |
| `issues-fs create <type> <title>` | Create a new issue |
| `issues-fs show <label>` | Display issue details |
| `issues-fs list` | List all issues |
| `issues-fs update <label>` | Update an issue |
| `issues-fs delete <label>` | Delete an issue |

### Link Commands

| Command | Description |
|---------|-------------|
| `issues-fs link <source> <verb> <target>` | Create link between issues |
| `issues-fs unlink <source> <target>` | Remove link |
| `issues-fs links <label>` | List links for an issue |

### Comment Commands

| Command | Description |
|---------|-------------|
| `issues-fs comment <label> <text>` | Add comment to issue |
| `issues-fs comments <label>` | List comments on issue |

### Type Management

| Command | Description |
|---------|-------------|
| `issues-fs types list` | List node types |
| `issues-fs types init` | Initialize default types |
| `issues-fs link-types list` | List link types |

## Output Formats

All commands support multiple output formats:

```bash
# Human-readable table (default)
issues-fs list

# JSON for scripts and agents
issues-fs list --output json

# Markdown for documentation
issues-fs show Bug-1 --output markdown

# Agent-optimized JSON with full details
issues-fs show Bug-1 --for-agent
```

## Development

### Setup

```bash
# Clone the repository
git clone https://github.com/owasp-sbot/Issues-FS__CLI.git
cd Issues-FS__CLI

# Install dependencies with Poetry
poetry install

# Run the CLI
poetry run issues-fs --help
```

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=issues_fs_cli --cov-report=html

# Run specific test file
poetry run pytest tests/unit/cli/test_CLI__Context.py
```

### Project Structure

```
issues_fs_cli/
├── cli/
│   ├── __init__.py
│   ├── CLI__Context.py       # Repository discovery and service init
│   ├── CLI__Label_Parser.py  # Label parsing utilities
│   ├── CLI__Output.py        # Output formatters
│   ├── cli__main.py          # Entry point and command registration
│   ├── cli__create.py        # Create command
│   ├── cli__show.py          # Show command
│   ├── cli__list.py          # List command
│   ├── cli__update.py        # Update command
│   ├── cli__delete.py        # Delete command
│   ├── cli__link.py          # Link commands
│   ├── cli__comment.py       # Comment commands
│   ├── cli__types.py         # Type management commands
│   └── cli__init.py          # Init command
└── utils/
    └── Version.py
```

## Architecture

The CLI follows a clean architecture with three layers:

1. **Command Layer** (`cli__*.py`) - Parses arguments, validates input, calls services
2. **Service Layer** - Business logic from `issues-fs` package
3. **Repository Layer** - File-based storage in `.issues/` directory

See [Architecture Documentation](docs/architecture.md) for detailed information.

## Integration with Issues-FS Ecosystem

Issues-FS CLI works with the broader Issues-FS ecosystem:

- **Issues-FS** - Core library with graph data model
- **Issues-FS__Service** - REST API for issue management
- **Issues-FS__Service__UI** - Web interface

## License

Apache 2.0 - See [LICENSE](LICENSE) for details.

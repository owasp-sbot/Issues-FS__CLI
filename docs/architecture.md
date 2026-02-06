# Issues-FS CLI Architecture

**Version:** v1.0
**Date:** 2026-02-06

## Overview

The Issues-FS CLI provides a command-line interface for the Issues-FS graph-based issue tracking system. It follows a layered architecture that separates concerns between command parsing, business logic, and storage.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                         User / Agent                         │
└─────────────────────────────┬───────────────────────────────┘
                              │ CLI commands
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Issues-FS CLI                           │
│  ┌─────────────────────────────────────────────────────────┐│
│  │  Command Layer (cli__*.py)                              ││
│  │  - Argument parsing (Typer)                             ││
│  │  - Input validation                                     ││
│  │  - Output formatting                                    ││
│  └─────────────────────────────────────────────────────────┘│
│                              │                               │
│  ┌─────────────────────────────────────────────────────────┐│
│  │  Context Layer (CLI__Context)                           ││
│  │  - Repository discovery                                 ││
│  │  - Service instantiation                                ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Issues-FS Core Library                    │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │  Node__Service  │  │  Link__Service  │  │ Type__Service│ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
│  ┌─────────────────────────────────────────────────────────┐│
│  │  Graph__Repository                                      ││
│  │  - Storage abstraction                                  ││
│  │  - Memory-FS backend                                    ││
│  └─────────────────────────────────────────────────────────┘│
└─────────────────────────────┬───────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    .issues/ Directory                        │
│  .graph/                                                     │
│  ├── types.json           # Node type definitions            │
│  ├── link-types.json      # Link type definitions            │
│  ├── global-index.json    # Global statistics                │
│  └── <node-type>/                                            │
│      ├── index.json       # Per-type index                   │
│      └── <Label>/                                            │
│          └── issue.json   # Node data                        │
└─────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. CLI__Context

The `CLI__Context` class is responsible for:

- **Repository Discovery**: Walks up from the current directory to find `.issues/`
- **Service Instantiation**: Creates all required services with the discovered repository

```python
class CLI__Context(Type_Safe):
    repository       : Graph__Repository  = None
    node_service     : Node__Service      = None
    link_service     : Link__Service      = None
    comments_service : Comments__Service  = None
    type_service     : Type__Service      = None
```

### 2. CLI__Label_Parser

Parses user-provided labels into (type, label) tuples:

- Input: `"Bug-27"`, `"Task-123"`, `"Feature-5"`
- Output: `(Safe_Str__Node_Type("bug"), Safe_Str__Node_Label("Bug-27"))`

### 3. CLI__Output

Handles output formatting for different audiences:

- **Table**: Human-readable tabular format (default)
- **JSON**: Machine-readable for scripts and agents
- **Markdown**: Documentation-friendly format
- **Agent Mode**: Full JSON with all fields and metadata

### 4. Command Modules

Each command is implemented in its own module:

| Module | Commands |
|--------|----------|
| `cli__main.py` | Entry point, Typer app registration |
| `cli__init.py` | `issues-fs init` |
| `cli__create.py` | `issues-fs create` |
| `cli__show.py` | `issues-fs show` |
| `cli__list.py` | `issues-fs list` |
| `cli__update.py` | `issues-fs update` |
| `cli__delete.py` | `issues-fs delete` |
| `cli__link.py` | `issues-fs link`, `unlink`, `links` |
| `cli__comment.py` | `issues-fs comment`, `comments` |
| `cli__types.py` | `issues-fs types`, `link-types` |

## Command Flow

### Example: Creating a Bug

```
User runs: issues-fs create bug "Login fails"
                          │
                          ▼
┌─────────────────────────────────────────┐
│ cli__create.py                          │
│ 1. Parse arguments (type="bug",         │
│    title="Login fails")                 │
│ 2. Create CLI__Context                  │
│ 3. Build Schema__Node__Create__Request  │
│ 4. Call node_service.create_node()      │
│ 5. Format response with CLI__Output     │
└─────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────┐
│ Node__Service.create_node()             │
│ 1. Validate request                     │
│ 2. Generate node_id and label           │
│ 3. Create Schema__Node                  │
│ 4. Save via repository.node_save()      │
│ 5. Update indexes                       │
│ 6. Return response                      │
└─────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────┐
│ Graph__Repository.node_save()           │
│ 1. Serialize node to JSON               │
│ 2. Write to .issues/.graph/bug/Bug-1/   │
│    issue.json                           │
└─────────────────────────────────────────┘
```

## Design Decisions

### 1. Typer Framework

We use [Typer](https://typer.tiangolo.com/) for CLI parsing because:

- Automatic help generation
- Tab completion support
- Type validation on arguments
- Clean subcommand structure
- Native Python type hints

### 2. Service Layer Reuse

The CLI reuses the service layer from `issues-fs` core rather than implementing its own business logic:

- **Consistency**: Same behavior as API and UI
- **Maintenance**: One place to fix bugs
- **Testing**: Services are already tested

### 3. Label-Based Interface

Users interact with labels (`Bug-27`) not node IDs:

- **Human-friendly**: Easy to remember and type
- **Git-like**: Similar to branch names
- **Type-embedded**: Label prefix indicates node type

### 4. Repository Discovery

The CLI walks up from the current directory to find `.issues/`:

- **Git-like**: Same as `git` finding `.git/`
- **Workspace-aware**: Works from any subdirectory
- **Clear error**: Explains how to create repository

## Output Modes

### Table (Default)

```
Label           Type         Status          Title
──────────────────────────────────────────────────
Bug-1           bug          confirmed       Login button not working
Task-1          task         backlog         Fix the login page

Total: 2
```

### JSON

```json
{
  "success": true,
  "nodes": [
    {"label": "Bug-1", "node_type": "bug", ...}
  ],
  "total": 2
}
```

### Agent Mode

Includes additional metadata for automated workflows:

- Full node data with all fields
- State machine information (valid transitions)
- Link details with node IDs
- Timestamps and audit fields

## Error Handling

### Error Response Pattern

All commands follow a consistent error handling pattern:

```python
response = context.node_service.create_node(request)

if response.success is False:
    CLI__Output.error(response.message, for_agent)
    raise typer.Exit(code=1)
```

### Exit Codes

- `0` - Success
- `1` - Error (service error, validation error, not found)

### Agent Mode Errors

In agent mode, errors are returned as JSON:

```json
{"success": false, "error": "Node not found: Bug-999"}
```

## Extension Points

### Adding New Commands

1. Create `cli__<command>.py` with command function
2. Import and register in `cli__main.py`
3. Add to README command reference

### Adding Output Formats

1. Add format handler in `CLI__Output`
2. Add format option to command signatures
3. Document in README

### Adding Node Types

1. Use `issues-fs types list` to see available types
2. Types are configured in `.issues/.graph/types.json`
3. CLI reads types from repository, no CLI code changes needed

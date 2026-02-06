# Issues-FS CLI: The Graph Interface

**Document:** issues-fs__cli-architecture  
**Version:** v1.0  
**Date:** 2026-02-05  
**Status:** Draft  
**Depends On:** issues-fs__thinking-in-graphs v1.0, issues-fs__lexicon-architecture v2.0  

---

## Executive Summary

This document defines the architecture of the Issues-FS command-line interface (CLI). The CLI is not just a convenience layer — it is the **primary interface to the graph** for both humans and agents. Every CLI command is a graph operation: creating nodes, adding edges, traversing relationships, or serializing subgraphs. The CLI abstracts the graph complexity while preserving full access to its power.

The CLI is designed with three audiences in mind: developers who want Git-like simplicity, agents who need structured output for automated workflows, and power users who want direct graph operations.

---

## Why: The Interface Problem

### Graphs Are Powerful but Not Directly Usable

The Issues-FS graph model is expressive: nodes, edges, fractal scopes, anchor links, pattern matching, confidence analysis. But no one interacts with a graph directly. They interact through interfaces that translate intent into graph operations.

Without a well-designed CLI:
- Developers must write Python code for every interaction
- Agents must parse unstructured output or use complex APIs
- Simple operations (update a status, list tasks) require disproportionate effort
- The graph's power is locked behind implementation complexity

### The CLI as Graph Interpreter

The CLI translates human-readable commands into graph operations:

| Command | Graph Operation |
|---------|-----------------|
| `issues-fs create task "Fix login bug"` | Create a node with type edge to Task anchor |
| `issues-fs update Task-23 --status completed` | Modify status edge, validate against state machine |
| `issues-fs link Task-23 --blocks Task-24` | Create edge between two nodes |
| `issues-fs show Task-23` | Traverse and serialize node's subgraph |
| `issues-fs list --type bug --status open` | Query: find nodes matching edge criteria |
| `issues-fs analyse Task-23 --connectivity` | Run Lexicon analysis tools on node |

The user doesn't need to know about edges, anchors, or traversal. They issue commands; the CLI handles the graph.

### Agents as First-Class Users

A critical insight from the voice memo: agents will use this CLI. When an agent is assigned a task, it needs to:

1. Read the task details (`issues-fs show Task-23`)
2. Understand what's required (parse the output)
3. Do the work (external to Issues-FS)
4. Update the status (`issues-fs update Task-23 --status completed`)
5. Report outcomes (`issues-fs comment Task-23 "Implemented rate limiting"`)

The CLI must produce output that agents can parse reliably. This means structured formats, consistent schemas, and explicit rather than implicit information.

---

## Design Principles

### 1. Git-Like Command Structure

Developers already know Git. The CLI should feel familiar:

```bash
# Git                          # Issues-FS
git status                     issues-fs status
git log                        issues-fs log
git add file.py                issues-fs create task "..."
git commit -m "message"        issues-fs update Task-23 --status completed
git branch feature-x           issues-fs scope create sprint-4
git checkout feature-x         issues-fs scope switch sprint-4
git diff                       issues-fs diff --from backup-1 --to backup-2
```

Commands are verb-first: `create`, `update`, `show`, `list`, `link`, `analyse`, `scope`, `scratch`.

### 2. Progressive Disclosure

Simple commands for simple operations. Power when you need it.

```bash
# Simple: create a task
issues-fs create task "Implement rate limiting"

# More detail: with fields
issues-fs create task "Implement rate limiting" \
    --priority P1 \
    --assigned-to dev-role \
    --parent Epic-5

# Power user: with explicit graph edges
issues-fs node create \
    --type task \
    --edge "title:Implement rate limiting" \
    --edge "priority:P1" \
    --edge "assigned_to:@dev-role" \
    --edge "parent:Epic-5" \
    --link-anchor "Lexicon:anchor__task"
```

Most users never see the third form. But it's there for those who need it.

### 3. Output Formats for Every Audience

The `--output` flag controls serialization:

```bash
# Human-readable table (default for terminals)
issues-fs list --type task
# ┌─────────┬──────────────────────┬────────────┬──────────┐
# │ ID      │ Title                │ Status     │ Priority │
# ├─────────┼──────────────────────┼────────────┼──────────┤
# │ Task-23 │ Implement rate limit │ in_progress│ P1       │
# │ Task-24 │ Add unit tests       │ open       │ P2       │
# └─────────┴──────────────────────┴────────────┴──────────┘

# JSON for agents and scripts
issues-fs list --type task --output json
# [{"id": "Task-23", "title": "Implement rate limiting", ...}]

# YAML for config-style readability
issues-fs list --type task --output yaml

# Markdown for documentation
issues-fs list --type task --output markdown

# Graph-native for full fidelity
issues-fs list --type task --output graph
# Outputs node IDs, edge types, anchor links — full graph structure
```

### 4. Agent-Optimized Mode

The `--for-agent` flag adjusts output for machine consumption:

```bash
issues-fs show Task-23 --for-agent
```

This mode:
- Always outputs JSON (unless overridden)
- Includes node IDs and edge types explicitly
- Includes state machine information (valid next statuses)
- Includes confidence assessment from Lexicon analysis
- Omits decorative formatting

Example agent-optimized output:

```json
{
  "node_id": "Task-23",
  "type": "task",
  "type_anchor": "Lexicon:anchor__task",
  "fields": {
    "title": "Implement rate limiting",
    "status": "in_progress",
    "priority": "P1",
    "assigned_to": "dev-role"
  },
  "edges": [
    {"type": "parent", "target": "Epic-5"},
    {"type": "blocks", "target": "Task-24"}
  ],
  "state_machine": {
    "current": "in_progress",
    "valid_transitions": ["completed", "blocked", "cancelled"]
  },
  "confidence": {
    "level": "high",
    "anchor_linked": true,
    "pattern_coverage": "5/7 fields match anchor__task"
  }
}
```

An agent receiving this knows exactly what it can do next (valid transitions), how the node relates to the broader system (anchor link, confidence), and what edges exist.

---

## Command Reference

### Core Commands

**`issues-fs create <type> <title>`** — Create a new issue node.

```bash
issues-fs create task "Implement rate limiting"
issues-fs create bug "Login fails on mobile"
issues-fs create decision "Use WebSocket vs polling"
issues-fs create handoff "Ready for QA review" --from dev --to qa
```

Options:
- `--priority <P0-P3>` — Set priority
- `--assigned-to <role>` — Assign to a role
- `--parent <id>` — Set parent node
- `--field <name>:<value>` — Set arbitrary field
- `--link-anchor <anchor>` — Explicitly link to Lexicon anchor

**`issues-fs update <id> [--field value]`** — Update an existing node.

```bash
issues-fs update Task-23 --status completed
issues-fs update Task-23 --priority P0 --assigned-to qa-role
issues-fs update Task-23 --field "estimated_hours:4"
```

The CLI validates status transitions against the state machine (if linked to a Lexicon anchor with a state machine pattern). Invalid transitions produce a warning:

```bash
issues-fs update Task-23 --status completed
# Warning: Task-23 is currently 'open'. 
# Valid transitions from 'open': ['in_progress', 'blocked', 'cancelled']
# 'completed' is not a valid transition. Use --force to override.
```

**`issues-fs show <id>`** — Display a node and its subgraph.

```bash
issues-fs show Task-23
issues-fs show Task-23 --depth 2          # Include 2 levels of connected nodes
issues-fs show Task-23 --edges-only       # Just show edges, not full nodes
issues-fs show Task-23 --output json      # JSON format
issues-fs show Task-23 --for-agent        # Agent-optimized output
```

**`issues-fs list [--filters]`** — Query nodes.

```bash
issues-fs list                                    # All issues in current scope
issues-fs list --type task                        # Only tasks
issues-fs list --type task --status open          # Open tasks
issues-fs list --assigned-to dev-role             # Assigned to dev
issues-fs list --parent Epic-5                    # Children of Epic-5
issues-fs list --has-edge "blocks"                # Nodes that block something
issues-fs list --no-anchor-link                   # Nodes not linked to Lexicon anchors
```

**`issues-fs link <source> --<type> <target>`** — Create an edge between nodes.

```bash
issues-fs link Task-23 --blocks Task-24
issues-fs link Task-23 --depends-on Decision-7
issues-fs link Task-23 --parent Epic-5
issues-fs link Task-23 --related-to Task-25
```

**`issues-fs unlink <source> --<type> <target>`** — Remove an edge.

```bash
issues-fs unlink Task-23 --blocks Task-24
```

### Analysis Commands

**`issues-fs analyse <id> <analysis-type>`** — Run Lexicon analysis tools.

```bash
issues-fs analyse Task-23 --connectivity
# Connectivity Analysis for Task-23
# ─────────────────────────────────
# Direct edges: 7
# Edges to typed definitions: 3
# Edges to anchor nodes: 1 (Lexicon:anchor__task)
# Confidence: high
# 
# Assessment: Task-23 links to project-level Task definition
# which links to Lexicon anchor. Port field has full type chain.
# Status field links to state machine.

issues-fs analyse Task-23 --pattern review_process
# Pattern Coverage: review_process
# ────────────────────────────────
# examine:  ✓ (has 'review_code' step)
# judge:    ✓ (has 'approve_or_reject' step)
# document: ✗ (no documentation step found)
# action:   ✗ (no follow-up action step found)
# 
# Coverage: 2/4 elements
# Assessment: This review process lacks documentation and action steps.

issues-fs analyse --scope Project-6 --gaps
# Gap Analysis for Project-6
# ──────────────────────────
# Total type definitions: 8
# Linked to anchors: 5 (62%)
# Local-only: 3
# 
# High-value gaps:
# - Sprint_Goal: No anchor exists. Closest match: anchor__task (32% overlap)
# - Retrospective: Matches review_process 3/4. Missing: action step.
```

**`issues-fs compare <id1> <id2>`** — Compare two nodes.

```bash
issues-fs compare Project-6:Review Project-7:Review
# Compatibility Analysis
# ──────────────────────
# Shared anchor: Lexicon:anchor__review_request
# Overlap edges: 2
# Divergent (Project-6 only): 3
# Divergent (Project-7 only): 2
# 
# Pattern coverage (review_process):
#   Project-6: examine ✓, judge ✓, document ✓, action ✗
#   Project-7: examine ✓, judge ✓, document ✗, action ✗
# 
# Assessment: Compatible for "was something reviewed".
# Divergent on documentation practices.
```

### Scope Commands

**`issues-fs scope`** — Manage fractal scopes.

```bash
issues-fs scope list                      # List available scopes
issues-fs scope current                   # Show current scope
issues-fs scope switch Project-6          # Switch to a scope
issues-fs scope create Sprint-5 --parent Project-6
issues-fs scope info Project-6            # Show scope's vocabulary, anchor links
```

Scopes affect which nodes are visible and how type resolution works. When you're in `Sprint-5` scope, `issues-fs list` shows only nodes in that scope (and optionally ancestors).

**`issues-fs scope resolve <type>`** — Show how a type resolves in current scope.

```bash
issues-fs scope resolve Task
# Type Resolution: Task
# ─────────────────────
# Current scope: Sprint-5
# Resolution chain:
#   1. Sprint-5: not found
#   2. Project-6: found → Project-6:Task
#      └── links to: Lexicon:anchor__task
# 
# Resolved definition: Project-6:Task
# Confidence: high (anchor linked)
```

### Scratch Graph Commands

**`issues-fs scratch`** — Manage ephemeral in-memory graphs.

```bash
# Create a scratch graph
issues-fs scratch create my-analysis

# Load data into it
issues-fs scratch load my-analysis --source github:owasp-sbot/Issues-FS
issues-fs scratch load my-analysis --source ./local-backup/
issues-fs scratch load my-analysis --source jira:PROJECT-KEY

# Switch to it (commands now operate on scratch graph)
issues-fs scratch switch my-analysis

# Do analysis
issues-fs list --type bug
issues-fs analyse --scope . --gaps

# Persist if needed
issues-fs scratch persist my-analysis --to ./exports/analysis-2026-02-05/

# Or discard
issues-fs scratch delete my-analysis

# List active scratch graphs
issues-fs scratch list
```

Scratch graphs are perfect for:
- Loading external issues (GitHub, Jira) without committing to local storage
- Running analysis on a subset of data
- Comparing issues across different sources
- Experimentation without affecting the main graph

### Import/Export Commands

**`issues-fs import`** — Import issues from external sources.

```bash
issues-fs import github owasp-sbot/Issues-FS
issues-fs import github owasp-sbot/Issues-FS --labels bug,enhancement
issues-fs import jira PROJECT-KEY --status "In Progress"
issues-fs import file ./backup-2026-01-15.json
```

Options:
- `--to-scratch <name>` — Import to a scratch graph instead of main storage
- `--map-types` — Attempt to map external types to Lexicon anchors
- `--dry-run` — Show what would be imported without doing it

**`issues-fs export`** — Export issues to various formats.

```bash
issues-fs export --output ./backup.json
issues-fs export --scope Project-6 --output ./project-6-backup.json
issues-fs export --type decision --output ./decisions.md --format markdown
issues-fs export --query "status:open AND priority:P0" --output ./urgent.json
```

---

## State Machine Enforcement

### How It Works

When a node links (directly or through scope resolution) to a Lexicon anchor that has a `pattern__state_machine`, the CLI enforces valid transitions.

```
Task-23
    └── type ──→ Project-6:Task
                    └── links_to ──→ Lexicon:anchor__task
                                        └── has_pattern ──→ pattern__state_machine
                                                              └── transitions:
                                                                  open → [in_progress, blocked, cancelled]
                                                                  in_progress → [completed, blocked]
                                                                  blocked → [in_progress, cancelled]
                                                                  completed → []  (terminal)
                                                                  cancelled → []  (terminal)
```

When you run `issues-fs update Task-23 --status completed`:

1. CLI resolves Task-23's type through scope chain
2. Finds anchor link with state machine pattern
3. Checks: is `in_progress → completed` valid? Yes.
4. Updates the status edge

If you tried `issues-fs update Task-23 --status completed` when status is `open`:

```bash
issues-fs update Task-23 --status completed
# Error: Invalid transition
# Current status: open
# Requested status: completed
# Valid transitions from 'open': in_progress, blocked, cancelled
# 
# Use --force to override (not recommended).
# Use --via to specify intermediate states:
#   issues-fs update Task-23 --status completed --via in_progress
```

### Nodes Without State Machines

If a node doesn't link to an anchor with a state machine, transitions are unrestricted but flagged:

```bash
issues-fs update Widget-7 --status done
# Warning: No state machine found for Widget-7's type.
# Transition allowed but not validated.
# 
# To add validation, link Widget-7's type to a Lexicon anchor:
#   issues-fs link Widget-7 --type-anchor Lexicon:anchor__task
```

This is honest uncertainty in action: the CLI reports what it can and can't validate.

---

## Configuration

### Config File

`~/.issues-fs/config.yaml`:

```yaml
# Default scope
default_scope: Project-6

# Default output format
output:
  format: table           # table, json, yaml, markdown, graph
  for_agent: false        # Set true to default to agent-optimized output
  color: auto             # auto, always, never

# State machine enforcement
state_machine:
  enforce: true           # Validate transitions
  warn_only: false        # Warn instead of error on invalid transitions

# Scratch graphs
scratch:
  default_location: memory    # memory, /tmp, custom path
  auto_cleanup: true          # Delete scratch graphs on exit

# Remote connections
remotes:
  github:
    token_env: GITHUB_TOKEN
  jira:
    url: https://company.atlassian.net
    token_env: JIRA_TOKEN
```

### Environment Variables

```bash
ISSUES_FS_SCOPE=Project-6          # Override default scope
ISSUES_FS_OUTPUT=json              # Override output format
ISSUES_FS_FOR_AGENT=1              # Enable agent mode
ISSUES_FS_STATE_MACHINE=warn       # warn, enforce, disable
```

---

## Implementation Notes

### Built on Typer

The CLI uses [Typer](https://typer.tiangolo.com/) for command structure, which provides:
- Automatic help generation
- Tab completion
- Type validation on arguments
- Clean subcommand structure

### Imports Issues-FS Core

The CLI imports `issues-fs` (core library) and `issues-fs-lexicon` directly:

```python
from issues_fs            import Graph__Repository, Node__Issue
from issues_fs_lexicon    import anchor__task, analyse_connectivity
from issues_fs_lexicon    import pattern__state_machine, analyse_coverage
```

This means the CLI can operate locally without a server. For remote operations, it calls the `Issues-FS__Service` API.

### Graph Operations Under the Hood

Every command translates to graph operations:

```python
# issues-fs create task "Fix login bug" --priority P1

# Becomes:
node = graph.create_node()
graph.add_edge(node, "type", resolve_type("task", current_scope))
graph.add_edge(node, "title", "Fix login bug")
graph.add_edge(node, "priority", "P1")
graph.add_edge(node, "status", get_initial_status("task"))
# ... etc
```

The CLI is syntactic sugar over graph operations. Advanced users can drop down to `issues-fs node` and `issues-fs edge` commands for direct graph manipulation.

---

## Agent Integration Patterns

### Pattern 1: Agent Reads Task, Does Work, Updates Status

```bash
# Agent receives task assignment
TASK_ID="Task-23"

# Agent reads task details
TASK=$(issues-fs show $TASK_ID --for-agent)

# Agent extracts what it needs (using jq or similar)
TITLE=$(echo $TASK | jq -r '.fields.title')
STATUS=$(echo $TASK | jq -r '.fields.status')
VALID_TRANSITIONS=$(echo $TASK | jq -r '.state_machine.valid_transitions[]')

# Agent does its work...
# ...

# Agent updates status
issues-fs update $TASK_ID --status completed

# Agent adds a comment
issues-fs comment $TASK_ID "Implemented rate limiting. Added 100 req/min default."
```

### Pattern 2: Agent Creates Handoff

```bash
# Dev agent completing work, handing to QA
issues-fs create handoff "Rate limiting ready for QA" \
    --from dev-role \
    --to qa-role \
    --deliverables "PR-123, unit tests passing" \
    --linked-to Task-23

# QA agent picks up handoff
HANDOFFS=$(issues-fs list --type handoff --to qa-role --status pending --for-agent)
# ... process handoffs
```

### Pattern 3: Agent Analyses Before Acting

```bash
# Agent checks confidence before proceeding
ANALYSIS=$(issues-fs analyse Task-23 --connectivity --output json)
CONFIDENCE=$(echo $ANALYSIS | jq -r '.confidence.level')

if [ "$CONFIDENCE" != "high" ]; then
    echo "Low confidence on Task-23, requesting human review"
    issues-fs update Task-23 --status blocked \
        --field "blocked_reason:Low graph confidence, needs human review"
    exit 1
fi

# Proceed with high confidence
# ...
```

---

## Relationship to Other Components

```
┌─────────────────────────────────────────────────────────────┐
│                         User / Agent                         │
└─────────────────────────────┬───────────────────────────────┘
                              │ CLI commands
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                      Issues-FS CLI                           │
│  (issues-fs create, update, show, list, analyse, scope...)  │
└─────────────────────────────┬───────────────────────────────┘
                              │ graph operations
              ┌───────────────┴───────────────┐
              ▼                               ▼
┌─────────────────────────┐     ┌─────────────────────────────┐
│    Issues-FS Core       │     │    Issues-FS Lexicon        │
│   (Graph__Repository,   │     │   (anchor nodes, patterns,  │
│    Node__Issue, etc.)   │     │    analysis tools)          │
└─────────────────────────┘     └─────────────────────────────┘
              │                               │
              └───────────────┬───────────────┘
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Storage Backend                           │
│        (Memory-FS: memory, disk, S3, SQLite, ZIP)           │
└─────────────────────────────────────────────────────────────┘
```

The CLI sits above the core library and Lexicon, translating user intent into graph operations. It can operate entirely locally (using Memory-FS backends) or connect to a remote `Issues-FS__Service` for shared/hosted scenarios.

---

## Decisions Log

| # | Decision | Rationale |
|---|----------|-----------|
| C1 | **Git-like command structure** | Developers know Git. Familiar patterns reduce learning curve. Verb-first commands are intuitive. |
| C2 | **Multiple output formats with `--output`** | Different audiences need different serializations. Tables for humans, JSON for agents, markdown for docs. |
| C3 | **`--for-agent` mode** | Agents are first-class users. They need structured, explicit, parseable output with state machine info and confidence levels. |
| C4 | **State machine enforcement by default** | The graph knows valid transitions. The CLI should use that knowledge to prevent invalid operations. Override with `--force` for edge cases. |
| C5 | **Scratch graphs for ephemeral work** | Not everything needs to persist. Analysis, comparison, experimentation should be possible without affecting the main graph. |
| C6 | **Built on Typer** | Typer provides excellent CLI ergonomics: auto-help, completion, type validation. No need to reinvent. |
| C7 | **Every command is a graph operation** | The CLI is not a separate system — it's a human/agent interface to the graph. This keeps the mental model consistent. |
| C8 | **Progressive disclosure** | Simple commands for simple tasks, power commands for advanced users. Most users never need `issues-fs node create --edge`. |

---

## References

- [Thinking in Graphs: Meaning Through Connectivity](./v0_4_0__issues-fs__thinking-in-graphs.md) — Foundational philosophy
- [Issues-FS Lexicon Architecture](./v0_4_0__issues-fs__lexicon-architecture-v2.md) — Anchor nodes and analysis tools
- [Issues-FS Architecture Overview](./v0_4_0__issues-fs__architecture-overview.md) — Ecosystem architecture
- [Typer](https://typer.tiangolo.com/) — CLI framework

---

*Issues-FS CLI Architecture v1.0*  
*Date: 2026-02-05*

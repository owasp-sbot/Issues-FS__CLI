# ═══════════════════════════════════════════════════════════════════════════════
# CLI Init Command - Initialize a new .issues/ repository
# ═══════════════════════════════════════════════════════════════════════════════

import os
import typer

from issues_fs_cli.cli.CLI__Output                                              import CLI__Output
from issues_fs.issues.graph_services.Graph__Repository__Factory                 import Graph__Repository__Factory
from issues_fs.issues.graph_services.Type__Service                              import Type__Service


def init(path      : str  = typer.Option(".", "--path", "-p", help="Path to create .issues/ in")       ,
         for_agent : bool = typer.Option(False, "--for-agent", help="Agent-optimized output")
    ) -> None:                                                                   # Initialize new .issues/ repository
    issues_path = os.path.join(os.path.abspath(path), '.issues')

    if os.path.exists(issues_path):
        CLI__Output.error(f".issues/ directory already exists at {issues_path}", for_agent)
        raise typer.Exit(code=1)

    # Create the .issues directory
    os.makedirs(issues_path, exist_ok=True)

    # Create repository and initialize default types
    repository   = Graph__Repository__Factory.create_local_disk(root_path = issues_path)
    type_service = Type__Service(repository = repository)
    type_service.initialize_default_types()

    if for_agent:
        import json
        print(json.dumps({"success"    : True                   ,
                          "message"    : "Repository initialized",
                          "issues_path": issues_path            }))
    else:
        CLI__Output.success(f"Initialized Issues-FS repository at {issues_path}")

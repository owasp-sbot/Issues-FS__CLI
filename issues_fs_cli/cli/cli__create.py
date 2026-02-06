# ═══════════════════════════════════════════════════════════════════════════════
# CLI Create Command - Create new issue nodes
# ═══════════════════════════════════════════════════════════════════════════════

import typer

from typing                                                                     import Optional

from issues_fs_cli.cli.CLI__Context                                             import CLI__Context
from issues_fs_cli.cli.CLI__Output                                              import CLI__Output
from issues_fs.schemas.graph.Schema__Node__Create__Request                      import Schema__Node__Create__Request
from issues_fs.schemas.graph.Safe_Str__Graph_Types                              import Safe_Str__Node_Type


def create(node_type   : str            = typer.Argument(..., help="Node type (bug, task, feature, etc.)"),
           title       : str            = typer.Argument(..., help="Issue title")                         ,
           description : str            = typer.Option("", "--description", "-d", help="Description")     ,
           status      : Optional[str]  = typer.Option(None, "--status", "-s", help="Initial status")     ,
           priority    : Optional[str]  = typer.Option(None, "--priority", "-p", help="Priority level")   ,
           tags        : Optional[str]  = typer.Option(None, "--tags", "-t", help="Comma-separated tags") ,
           output      : str            = typer.Option("table", "--output", "-o", help="Output format")   ,
           for_agent   : bool           = typer.Option(False, "--for-agent", help="Agent-optimized output")
      ) -> None:                                                                 # Create a new issue node
    try:
        context    = CLI__Context()
    except FileNotFoundError as e:
        CLI__Output.error(str(e), for_agent)
        raise typer.Exit(code=1)

    properties = {}
    if priority:
        properties['priority'] = priority

    tag_list = [t.strip() for t in tags.split(',')] if tags else []

    try:
        safe_node_type = Safe_Str__Node_Type(node_type.lower())
    except Exception as e:
        CLI__Output.error(f"Invalid node type: {node_type}", for_agent)
        raise typer.Exit(code=1)

    request = Schema__Node__Create__Request(node_type   = safe_node_type ,
                                            title       = title          ,
                                            description = description    ,
                                            status      = status or ''   ,
                                            tags        = tag_list       ,
                                            properties  = properties     )

    response = context.node_service.create_node(request)

    if response.success is False:
        CLI__Output.error(response.message, for_agent)
        raise typer.Exit(code=1)

    CLI__Output.render_create_response(response                ,
                                       format    = output      ,
                                       for_agent = for_agent   )

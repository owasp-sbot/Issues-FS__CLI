# ═══════════════════════════════════════════════════════════════════════════════
# CLI Update Command - Update an existing node
# ═══════════════════════════════════════════════════════════════════════════════

import typer

from typing                                                                     import Optional

from issues_fs_cli.cli.CLI__Context                                             import CLI__Context
from issues_fs_cli.cli.CLI__Output                                              import CLI__Output
from issues_fs_cli.cli.CLI__Label_Parser                                        import CLI__Label_Parser
from issues_fs.schemas.graph.Schema__Node__Update__Request                      import Schema__Node__Update__Request


def update(label       : str           = typer.Argument(..., help="Node label (e.g. Task-23)")             ,
           title       : Optional[str] = typer.Option(None, "--title", "-T", help="New title")             ,
           description : Optional[str] = typer.Option(None, "--description", "-d", help="New description") ,
           status      : Optional[str] = typer.Option(None, "--status", "-s", help="New status")           ,
           priority    : Optional[str] = typer.Option(None, "--priority", "-p", help="New priority")       ,
           tags        : Optional[str] = typer.Option(None, "--tags", "-t", help="Comma-separated tags")   ,
           output      : str           = typer.Option("table", "--output", "-o", help="Output format")     ,
           for_agent   : bool          = typer.Option(False, "--for-agent", help="Agent-optimized output")
      ) -> None:                                                                 # Update an existing node
    try:
        context = CLI__Context()
    except FileNotFoundError as e:
        CLI__Output.error(str(e), for_agent)
        raise typer.Exit(code=1)

    node_type, node_label = CLI__Label_Parser.parse(label)

    if node_type is None:
        CLI__Output.error(f"Invalid label format: {label}. Expected format: Type-123", for_agent)
        raise typer.Exit(code=1)

    properties = {}
    if priority:
        properties['priority'] = priority

    tag_list = [t.strip() for t in tags.split(',')] if tags else None

    request = Schema__Node__Update__Request(title       = title                  ,
                                            description = description            ,
                                            status      = status                 ,
                                            tags        = tag_list               ,
                                            properties  = properties if properties else None)

    response = context.node_service.update_node(node_type = node_type  ,
                                                label     = node_label ,
                                                request   = request    )

    if response.success is False:
        CLI__Output.error(response.message, for_agent)
        raise typer.Exit(code=1)

    CLI__Output.render_update_response(response                ,
                                       format    = output      ,
                                       for_agent = for_agent   )

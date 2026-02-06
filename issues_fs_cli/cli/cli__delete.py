# ═══════════════════════════════════════════════════════════════════════════════
# CLI Delete Command - Delete a node
# ═══════════════════════════════════════════════════════════════════════════════

import typer

from issues_fs_cli.cli.CLI__Context                                             import CLI__Context
from issues_fs_cli.cli.CLI__Output                                              import CLI__Output
from issues_fs_cli.cli.CLI__Label_Parser                                        import CLI__Label_Parser


def delete(label     : str  = typer.Argument(..., help="Node label (e.g. Task-23)")                     ,
           force     : bool = typer.Option(False, "--force", "-f", help="Skip confirmation")            ,
           output    : str  = typer.Option("table", "--output", "-o", help="Output format")             ,
           for_agent : bool = typer.Option(False, "--for-agent", help="Agent-optimized output")
      ) -> None:                                                                 # Delete a node
    try:
        context = CLI__Context()
    except FileNotFoundError as e:
        CLI__Output.error(str(e), for_agent)
        raise typer.Exit(code=1)

    node_type, node_label = CLI__Label_Parser.parse(label)

    if node_type is None:
        CLI__Output.error(f"Invalid label format: {label}. Expected format: Type-123", for_agent)
        raise typer.Exit(code=1)

    # Confirm deletion unless --force
    if not force and not for_agent:
        confirm = typer.confirm(f"Are you sure you want to delete {label}?")
        if not confirm:
            raise typer.Abort()

    response = context.node_service.delete_node(node_type = node_type  ,
                                                label     = node_label )

    if response.success is False:
        CLI__Output.error(response.message, for_agent)
        raise typer.Exit(code=1)

    CLI__Output.render_delete_response(response                ,
                                       format    = output      ,
                                       for_agent = for_agent   )

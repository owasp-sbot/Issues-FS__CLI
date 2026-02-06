# ═══════════════════════════════════════════════════════════════════════════════
# CLI Show Command - Display a node and its subgraph
# ═══════════════════════════════════════════════════════════════════════════════

import typer

from issues_fs_cli.cli.CLI__Context                                             import CLI__Context
from issues_fs_cli.cli.CLI__Output                                              import CLI__Output
from issues_fs_cli.cli.CLI__Label_Parser                                        import CLI__Label_Parser


def show(label     : str  = typer.Argument(..., help="Node label (e.g. Task-23)")                      ,
         depth     : int  = typer.Option(0, "--depth", "-D", help="Traversal depth for graph view")    ,
         output    : str  = typer.Option("table", "--output", "-o", help="Output format")              ,
         for_agent : bool = typer.Option(False, "--for-agent", help="Agent-optimized output")
    ) -> None:                                                                   # Display node details
    try:
        context = CLI__Context()
    except FileNotFoundError as e:
        CLI__Output.error(str(e), for_agent)
        raise typer.Exit(code=1)

    node_type, node_label = CLI__Label_Parser.parse(label)

    if node_type is None:
        CLI__Output.error(f"Invalid label format: {label}. Expected format: Type-123", for_agent)
        raise typer.Exit(code=1)

    if depth > 0:
        response = context.node_service.get_node_graph(node_type = node_type  ,
                                                       label     = node_label ,
                                                       depth     = depth      )
        if response.success is False:
            CLI__Output.error(response.message, for_agent)
            raise typer.Exit(code=1)

        CLI__Output.render_graph(response                  ,
                                 format    = output        ,
                                 for_agent = for_agent     )
    else:
        node = context.node_service.get_node(node_type = node_type  ,
                                             label     = node_label )
        if node is None:
            CLI__Output.error(f"Node not found: {label}", for_agent)
            raise typer.Exit(code=1)

        CLI__Output.render_node(node                       ,
                                format    = output         ,
                                for_agent = for_agent      )

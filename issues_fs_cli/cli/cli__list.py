# ═══════════════════════════════════════════════════════════════════════════════
# CLI List Command - Query and list nodes
# ═══════════════════════════════════════════════════════════════════════════════

import typer

from typing                                                                     import Optional

from issues_fs_cli.cli.CLI__Context                                             import CLI__Context
from issues_fs_cli.cli.CLI__Output                                              import CLI__Output
from issues_fs.schemas.graph.Safe_Str__Graph_Types                              import Safe_Str__Node_Type


def list_issues(node_type : Optional[str] = typer.Option(None, "--type", "-t", help="Filter by node type") ,
                status    : Optional[str] = typer.Option(None, "--status", "-s", help="Filter by status")  ,
                output    : str           = typer.Option("table", "--output", "-o", help="Output format")  ,
                for_agent : bool          = typer.Option(False, "--for-agent", help="Agent-optimized output")
           ) -> None:                                                            # List all issues
    try:
        context = CLI__Context()
    except FileNotFoundError as e:
        CLI__Output.error(str(e), for_agent)
        raise typer.Exit(code=1)

    safe_node_type = None
    if node_type:
        try:
            safe_node_type = Safe_Str__Node_Type(node_type.lower())
        except Exception:
            CLI__Output.error(f"Invalid node type: {node_type}", for_agent)
            raise typer.Exit(code=1)

    response = context.node_service.list_nodes(node_type = safe_node_type)

    if response.success is False:
        CLI__Output.error(response.message, for_agent)
        raise typer.Exit(code=1)

    # Filter by status if specified
    if status and response.nodes:
        filtered_nodes = [n for n in response.nodes if str(n.status) == status]
        response.nodes = filtered_nodes
        response.total = len(filtered_nodes)

    CLI__Output.render_list(response                ,
                            format    = output      ,
                            for_agent = for_agent   )

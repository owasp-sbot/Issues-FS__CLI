# ═══════════════════════════════════════════════════════════════════════════════
# CLI Comment Commands - Create and list comments on nodes
# ═══════════════════════════════════════════════════════════════════════════════

import typer

from typing                                                                     import Optional

from issues_fs_cli.cli.CLI__Context                                             import CLI__Context
from issues_fs_cli.cli.CLI__Output                                              import CLI__Output
from issues_fs_cli.cli.CLI__Label_Parser                                        import CLI__Label_Parser
from issues_fs.schemas.issues.Schema__Comment                                   import Schema__Comment__Create__Request


def comment(label     : str           = typer.Argument(..., help="Node label (e.g. Task-23)")            ,
            text      : str           = typer.Argument(..., help="Comment text")                         ,
            author    : Optional[str] = typer.Option("cli-user", "--author", "-a", help="Comment author"),
            output    : str           = typer.Option("table", "--output", "-o", help="Output format")    ,
            for_agent : bool          = typer.Option(False, "--for-agent", help="Agent-optimized output")
       ) -> None:                                                                # Add a comment to a node
    try:
        context = CLI__Context()
    except FileNotFoundError as e:
        CLI__Output.error(str(e), for_agent)
        raise typer.Exit(code=1)

    node_type, node_label = CLI__Label_Parser.parse(label)

    if node_type is None:
        CLI__Output.error(f"Invalid label format: {label}. Expected format: Type-123", for_agent)
        raise typer.Exit(code=1)

    request = Schema__Comment__Create__Request(author = author ,
                                               text   = text   )

    response = context.comments_service.create_comment(node_type = node_type  ,
                                                       label     = node_label ,
                                                       request   = request    )

    if response.success is False:
        CLI__Output.error(response.message, for_agent)
        raise typer.Exit(code=1)

    CLI__Output.render_comment_response(response                ,
                                        format    = output      ,
                                        for_agent = for_agent   )


def comments(label     : str  = typer.Argument(..., help="Node label (e.g. Task-23)")                   ,
             output    : str  = typer.Option("table", "--output", "-o", help="Output format")           ,
             for_agent : bool = typer.Option(False, "--for-agent", help="Agent-optimized output")
        ) -> None:                                                               # List all comments on a node
    try:
        context = CLI__Context()
    except FileNotFoundError as e:
        CLI__Output.error(str(e), for_agent)
        raise typer.Exit(code=1)

    node_type, node_label = CLI__Label_Parser.parse(label)

    if node_type is None:
        CLI__Output.error(f"Invalid label format: {label}. Expected format: Type-123", for_agent)
        raise typer.Exit(code=1)

    response = context.comments_service.list_comments(node_type = node_type  ,
                                                      label     = node_label )

    if response.success is False:
        CLI__Output.error(response.message, for_agent)
        raise typer.Exit(code=1)

    CLI__Output.render_comments_list(response                ,
                                     format    = output      ,
                                     for_agent = for_agent   )

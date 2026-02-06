# ═══════════════════════════════════════════════════════════════════════════════
# CLI Types Commands - Manage node and link types
# ═══════════════════════════════════════════════════════════════════════════════

import typer

from issues_fs_cli.cli.CLI__Context                                             import CLI__Context
from issues_fs_cli.cli.CLI__Output                                              import CLI__Output


types_app = typer.Typer(name         = "types"                                  ,
                        help         = "Manage node and link types"             ,
                        no_args_is_help = True                                  )


@types_app.command("list")
def types_list(output    : str  = typer.Option("table", "--output", "-o", help="Output format")        ,
               for_agent : bool = typer.Option(False, "--for-agent", help="Agent-optimized output")
          ) -> None:                                                             # List all node types
    try:
        context = CLI__Context()
    except FileNotFoundError as e:
        CLI__Output.error(str(e), for_agent)
        raise typer.Exit(code=1)

    types = context.type_service.list_node_types()

    CLI__Output.render_node_types(types                     ,
                                  format    = output        ,
                                  for_agent = for_agent     )


@types_app.command("init")
def types_init(for_agent : bool = typer.Option(False, "--for-agent", help="Agent-optimized output")
          ) -> None:                                                             # Initialize default types
    try:
        context = CLI__Context()
    except FileNotFoundError as e:
        CLI__Output.error(str(e), for_agent)
        raise typer.Exit(code=1)

    context.type_service.initialize_default_types()

    if for_agent:
        import json
        print(json.dumps({"success": True, "message": "Default types initialized"}))
    else:
        CLI__Output.success("Default types initialized successfully")


# ═══════════════════════════════════════════════════════════════════════════════
# Link Types Subcommand
# ═══════════════════════════════════════════════════════════════════════════════

link_types_app = typer.Typer(name         = "link-types"                        ,
                             help         = "Manage link types"                 ,
                             no_args_is_help = True                             )


@link_types_app.command("list")
def link_types_list(output    : str  = typer.Option("table", "--output", "-o", help="Output format")   ,
                    for_agent : bool = typer.Option(False, "--for-agent", help="Agent-optimized output")
               ) -> None:                                                        # List all link types
    try:
        context = CLI__Context()
    except FileNotFoundError as e:
        CLI__Output.error(str(e), for_agent)
        raise typer.Exit(code=1)

    types = context.type_service.list_link_types()

    CLI__Output.render_link_types(types                     ,
                                  format    = output        ,
                                  for_agent = for_agent     )

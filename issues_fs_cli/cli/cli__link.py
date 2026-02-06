# ═══════════════════════════════════════════════════════════════════════════════
# CLI Link Command - Create and remove edges between nodes
# ═══════════════════════════════════════════════════════════════════════════════

import typer

from issues_fs_cli.cli.CLI__Context                                             import CLI__Context
from issues_fs_cli.cli.CLI__Output                                              import CLI__Output
from issues_fs_cli.cli.CLI__Label_Parser                                        import CLI__Label_Parser
from issues_fs.schemas.graph.Schema__Link__Create__Request                      import Schema__Link__Create__Request
from issues_fs.schemas.graph.Safe_Str__Graph_Types                              import Safe_Str__Link_Verb
from issues_fs.schemas.graph.Safe_Str__Graph_Types                              import Safe_Str__Node_Label


def link(source    : str  = typer.Argument(..., help="Source label (e.g. Task-23)")                    ,
         verb      : str  = typer.Argument(..., help="Link verb (blocks, depends-on, etc.)")           ,
         target    : str  = typer.Argument(..., help="Target label (e.g. Bug-1)")                      ,
         output    : str  = typer.Option("table", "--output", "-o", help="Output format")              ,
         for_agent : bool = typer.Option(False, "--for-agent", help="Agent-optimized output")
    ) -> None:                                                                   # Create link between nodes
    try:
        context = CLI__Context()
    except FileNotFoundError as e:
        CLI__Output.error(str(e), for_agent)
        raise typer.Exit(code=1)

    source_type, source_label = CLI__Label_Parser.parse(source)

    if source_type is None:
        CLI__Output.error(f"Invalid source label: {source}. Expected format: Type-123", for_agent)
        raise typer.Exit(code=1)

    try:
        safe_verb = Safe_Str__Link_Verb(verb.lower())
    except Exception:
        CLI__Output.error(f"Invalid link verb: {verb}", for_agent)
        raise typer.Exit(code=1)

    try:
        safe_target = Safe_Str__Node_Label(target)
    except Exception:
        CLI__Output.error(f"Invalid target label: {target}", for_agent)
        raise typer.Exit(code=1)

    request = Schema__Link__Create__Request(verb         = safe_verb   ,
                                            target_label = safe_target )

    response = context.link_service.create_link(source_type  = source_type  ,
                                                source_label = source_label ,
                                                request      = request      )

    if response.success is False:
        CLI__Output.error(response.message, for_agent)
        raise typer.Exit(code=1)

    CLI__Output.render_link_response(response                ,
                                     format    = output      ,
                                     for_agent = for_agent   )


def unlink(source    : str  = typer.Argument(..., help="Source label (e.g. Task-23)")                  ,
           target    : str  = typer.Argument(..., help="Target label (e.g. Bug-1)")                    ,
           output    : str  = typer.Option("table", "--output", "-o", help="Output format")            ,
           for_agent : bool = typer.Option(False, "--for-agent", help="Agent-optimized output")
      ) -> None:                                                                 # Remove link between nodes
    try:
        context = CLI__Context()
    except FileNotFoundError as e:
        CLI__Output.error(str(e), for_agent)
        raise typer.Exit(code=1)

    source_type, source_label = CLI__Label_Parser.parse(source)

    if source_type is None:
        CLI__Output.error(f"Invalid source label: {source}. Expected format: Type-123", for_agent)
        raise typer.Exit(code=1)

    try:
        safe_target = Safe_Str__Node_Label(target)
    except Exception:
        CLI__Output.error(f"Invalid target label: {target}", for_agent)
        raise typer.Exit(code=1)

    response = context.link_service.delete_link(source_type  = source_type  ,
                                                source_label = source_label ,
                                                target_label = safe_target  )

    if response.success is False:
        CLI__Output.error(response.message, for_agent)
        raise typer.Exit(code=1)

    CLI__Output.render_unlink_response(response                ,
                                       format    = output      ,
                                       for_agent = for_agent   )


def links(label     : str  = typer.Argument(..., help="Node label (e.g. Task-23)")                     ,
          output    : str  = typer.Option("table", "--output", "-o", help="Output format")             ,
          for_agent : bool = typer.Option(False, "--for-agent", help="Agent-optimized output")
     ) -> None:                                                                  # List links for a node
    try:
        context = CLI__Context()
    except FileNotFoundError as e:
        CLI__Output.error(str(e), for_agent)
        raise typer.Exit(code=1)

    node_type, node_label = CLI__Label_Parser.parse(label)

    if node_type is None:
        CLI__Output.error(f"Invalid label format: {label}. Expected format: Type-123", for_agent)
        raise typer.Exit(code=1)

    response = context.link_service.list_links(node_type = node_type  ,
                                               label     = node_label )

    if response.success is False:
        CLI__Output.error(response.message, for_agent)
        raise typer.Exit(code=1)

    CLI__Output.render_links_list(response                ,
                                  format    = output      ,
                                  for_agent = for_agent   )

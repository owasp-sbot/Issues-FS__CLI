# ═══════════════════════════════════════════════════════════════════════════════
# CLI Main - Typer app definition and command registration
# ═══════════════════════════════════════════════════════════════════════════════

import typer

from issues_fs_cli.cli.cli__create                                              import create
from issues_fs_cli.cli.cli__show                                                import show
from issues_fs_cli.cli.cli__list                                                import list_issues
from issues_fs_cli.cli.cli__update                                              import update
from issues_fs_cli.cli.cli__delete                                              import delete
from issues_fs_cli.cli.cli__link                                                import link, unlink, links
from issues_fs_cli.cli.cli__comment                                             import comment, comments
from issues_fs_cli.cli.cli__types                                               import types_app, link_types_app
from issues_fs_cli.cli.cli__init                                                import init


app = typer.Typer(name            = "issues-fs"                                 ,
                  help            = "Git-native graph-based issue tracking"     ,
                  no_args_is_help = True                                        )


# ═══════════════════════════════════════════════════════════════════════════════
# Core Node Commands
# ═══════════════════════════════════════════════════════════════════════════════

app.command("init"    )(init       )
app.command("create"  )(create     )
app.command("show"    )(show       )
app.command("list"    )(list_issues)
app.command("update"  )(update     )
app.command("delete"  )(delete     )


# ═══════════════════════════════════════════════════════════════════════════════
# Link Commands
# ═══════════════════════════════════════════════════════════════════════════════

app.command("link"    )(link       )
app.command("unlink"  )(unlink     )
app.command("links"   )(links      )


# ═══════════════════════════════════════════════════════════════════════════════
# Comment Commands
# ═══════════════════════════════════════════════════════════════════════════════

app.command("comment" )(comment    )
app.command("comments")(comments   )


# ═══════════════════════════════════════════════════════════════════════════════
# Type Management Subcommands
# ═══════════════════════════════════════════════════════════════════════════════

app.add_typer(types_app     , name = "types"     )
app.add_typer(link_types_app, name = "link-types")


# ═══════════════════════════════════════════════════════════════════════════════
# Entry Point
# ═══════════════════════════════════════════════════════════════════════════════

def main():                                                                      # CLI entry point
    app()


if __name__ == "__main__":
    main()

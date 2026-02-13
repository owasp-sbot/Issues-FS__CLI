# ═══════════════════════════════════════════════════════════════════════════════
# CLI Check Command - Validate .issues files
# ═══════════════════════════════════════════════════════════════════════════════

import os
import typer

from issues_fs.issues.issues_file.Issues_File__Check__Service               import Issues_File__Check__Service
from issues_fs_cli.cli.CLI__Output                                          import CLI__Output


def check(file      : str  = typer.Argument(None                           , help="Specific .issues file to check"     ),
          for_agent : bool = typer.Option   (False, "--for-agent"          , help="Agent-optimized output"              )
     ) -> None:                                                             # Validate .issues files
    issues_dir = find_issues_dir()
    if issues_dir is None:
        CLI__Output.error("No .issues/ directory found. "
                          "Run 'issues-fs init' to create one.", for_agent)
        raise typer.Exit(code=1)

    if file:
        file_path = os.path.join(issues_dir, file) if not os.path.isabs(file) else file
        if not os.path.exists(file_path):
            CLI__Output.error(f"File not found: {file_path}", for_agent)
            raise typer.Exit(code=1)
        files = [file_path]
    else:
        files = discover_issues_files(issues_dir)

    if not files:
        CLI__Output.success("No .issues files found.")
        raise typer.Exit(code=0)

    checker      = Issues_File__Check__Service()
    files_data   = []

    for path in files:
        with open(path, 'r') as f:
            content = f.read()
        filename = os.path.basename(path)
        files_data.append((content, filename))

    if len(files_data) == 1:
        summary = checker.check_content(files_data[0][0], files_data[0][1])
    else:
        summary = checker.check_multiple(files_data)

    report = checker.format_report(summary)
    print(report)

    if summary.is_valid is False:
        raise typer.Exit(code=1)


def find_issues_dir() -> str:                                               # Walk up from cwd to find .issues/
    current = os.getcwd()
    while True:
        candidate = os.path.join(current, '.issues')
        if os.path.isdir(candidate):
            return candidate
        parent = os.path.dirname(current)
        if parent == current:
            return None
        current = parent


def discover_issues_files(issues_dir: str) -> list:                         # Find all *.issues files in directory
    result = []
    for entry in os.listdir(issues_dir):
        if entry.endswith('.issues'):
            result.append(os.path.join(issues_dir, entry))
    return sorted(result)

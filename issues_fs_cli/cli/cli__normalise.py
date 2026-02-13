# ═══════════════════════════════════════════════════════════════════════════════
# CLI Normalise Command - Export .issues files to JSON issue structure
# ═══════════════════════════════════════════════════════════════════════════════

import json
import os
import typer

from issues_fs.issues.issues_file.Issues_File__Normalise__Service           import Issues_File__Normalise__Service
from issues_fs_cli.cli.CLI__Output                                          import CLI__Output


def normalise(file      : str  = typer.Argument(None                       , help="Specific .issues file to normalise" ),
              dry_run   : bool = typer.Option   (False, "--dry-run"        , help="Show what would be written"          ),
              for_agent : bool = typer.Option   (False, "--for-agent"      , help="Agent-optimized output"              )
         ) -> None:                                                         # Export .issues to JSON
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

    normaliser = Issues_File__Normalise__Service()
    files_data = []

    for path in files:
        with open(path, 'r') as f:
            content = f.read()
        filename = os.path.basename(path)
        files_data.append((content, filename))

    if len(files_data) == 1:
        file_map, errors = normaliser.normalise_to_dict(files_data[0][0], files_data[0][1])
    else:
        file_map, errors = normaliser.normalise_multiple(files_data)

    if dry_run:
        print(f"Would write {len(file_map)} files:")
        for path in sorted(file_map.keys()):
            print(f"  {path}")
        if errors:
            print(f"\nErrors ({len(errors)}):")
            for error in errors:
                print(f"  {error}")
        return

    written = 0
    for rel_path, content in file_map.items():
        abs_path = os.path.join(issues_dir, rel_path)
        os.makedirs(os.path.dirname(abs_path), exist_ok=True)
        with open(abs_path, 'w') as f:
            f.write(content)
        written += 1

    print(f"Normalised: {written} issue files written to {issues_dir}/")

    if errors:
        print(f"Errors ({len(errors)}):")
        for error in errors:
            print(f"  {error}")
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

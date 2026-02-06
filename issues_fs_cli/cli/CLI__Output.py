# ═══════════════════════════════════════════════════════════════════════════════
# CLI__Output - Render service responses for terminal or agent consumption
# ═══════════════════════════════════════════════════════════════════════════════

import json
import sys

from typing                                                                     import List

from issues_fs.schemas.graph.Schema__Node                                       import Schema__Node
from issues_fs.schemas.graph.Schema__Node__Create__Response                     import Schema__Node__Create__Response
from issues_fs.schemas.graph.Schema__Node__Update__Response                     import Schema__Node__Update__Response
from issues_fs.schemas.graph.Schema__Node__Delete__Response                     import Schema__Node__Delete__Response
from issues_fs.schemas.graph.Schema__Node__List__Response                       import Schema__Node__List__Response
from issues_fs.schemas.graph.Schema__Graph__Response                            import Schema__Graph__Response
from issues_fs.schemas.graph.Schema__Link__Create__Response                     import Schema__Link__Create__Response
from issues_fs.schemas.graph.Schema__Link__Delete__Response                     import Schema__Link__Delete__Response
from issues_fs.schemas.graph.Schema__Link__List__Response                       import Schema__Link__List__Response
from issues_fs.schemas.issues.Schema__Comment                                   import Schema__Comment__Response
from issues_fs.schemas.issues.Schema__Comment                                   import Schema__Comment__List__Response
from issues_fs.schemas.issues.Schema__Comment                                   import Schema__Comment__Delete__Response
from issues_fs.schemas.graph.Schema__Node__Type                                 import Schema__Node__Type
from issues_fs.schemas.graph.Schema__Link__Type                                 import Schema__Link__Type


class CLI__Output:                                                               # Output formatting utilities

    # ═══════════════════════════════════════════════════════════════════════════════
    # Error and Success Messages
    # ═══════════════════════════════════════════════════════════════════════════════

    @staticmethod
    def error(message: str, for_agent: bool = False) -> None:                    # Print error to stderr
        if for_agent:
            print(json.dumps({"success": False, "error": message}))
        else:
            sys.stderr.write(f"Error: {message}\n")

    @staticmethod
    def success(message: str) -> None:                                           # Print success message
        sys.stdout.write(f"{message}\n")

    # ═══════════════════════════════════════════════════════════════════════════════
    # Node Rendering
    # ═══════════════════════════════════════════════════════════════════════════════

    @staticmethod
    def render_node(node      : Schema__Node ,                                   # Render single node
                    format    : str = "table" ,
                    for_agent : bool = False  ) -> None:
        if for_agent or format == "json":
            print(json.dumps(node.json(), indent=2))
            return

        if format == "table":
            CLI__Output.render_node_table(node)
            return

        if format == "markdown":
            CLI__Output.render_node_markdown(node)
            return

    @staticmethod
    def render_node_table(node: Schema__Node) -> None:                           # Render node as table
        print(f"{'Label':<15} {node.label}")
        print(f"{'Type':<15} {node.node_type}")
        print(f"{'Title':<15} {node.title}")
        print(f"{'Status':<15} {node.status}")

        if node.tags:
            print(f"{'Tags':<15} {', '.join(str(t) for t in node.tags)}")

        if node.description and str(node.description).strip():
            print(f"{'Description':<15} {node.description}")

        if node.links:
            print(f"\n{'Links':}")
            for link in node.links:
                print(f"  {link.verb} → {link.target_label}")

    @staticmethod
    def render_node_markdown(node: Schema__Node) -> None:                        # Render node as markdown
        print(f"# {node.label}: {node.title}\n")
        print(f"**Type:** {node.node_type}  ")
        print(f"**Status:** {node.status}  ")

        if node.tags:
            print(f"**Tags:** {', '.join(str(t) for t in node.tags)}  ")

        if node.description and str(node.description).strip():
            print(f"\n{node.description}")

        if node.links:
            print(f"\n## Links\n")
            for link in node.links:
                print(f"- **{link.verb}** → {link.target_label}")

    # ═══════════════════════════════════════════════════════════════════════════════
    # List Rendering
    # ═══════════════════════════════════════════════════════════════════════════════

    @staticmethod
    def render_list(response  : Schema__Node__List__Response ,                   # Render node list
                    format    : str  = "table"               ,
                    for_agent : bool = False                  ) -> None:
        if for_agent or format == "json":
            print(json.dumps(response.json(), indent=2))
            return

        if format == "table":
            CLI__Output.render_list_table(response)
            return

    @staticmethod
    def render_list_table(response: Schema__Node__List__Response) -> None:       # Render list as table
        if response.total == 0:
            print("No issues found.")
            return

        header = f"{'Label':<15} {'Type':<12} {'Status':<15} {'Title'}"
        print(header)
        print("─" * len(header))

        for node in response.nodes:
            title = str(node.title)[:50] if node.title else ""
            print(f"{str(node.label):<15} {str(node.node_type):<12} {str(node.status):<15} {title}")

        print(f"\nTotal: {response.total}")

    # ═══════════════════════════════════════════════════════════════════════════════
    # Create Response Rendering
    # ═══════════════════════════════════════════════════════════════════════════════

    @staticmethod
    def render_create_response(response  : Schema__Node__Create__Response ,      # Render create result
                               format    : str  = "table"                 ,
                               for_agent : bool = False                   ) -> None:
        if for_agent or format == "json":
            print(json.dumps(response.json(), indent=2))
            return

        if response.success and response.node:
            print(f"Created {response.node.label}: {response.node.title}")

    # ═══════════════════════════════════════════════════════════════════════════════
    # Update Response Rendering
    # ═══════════════════════════════════════════════════════════════════════════════

    @staticmethod
    def render_update_response(response  : Schema__Node__Update__Response ,      # Render update result
                               format    : str  = "table"                 ,
                               for_agent : bool = False                   ) -> None:
        if for_agent or format == "json":
            print(json.dumps(response.json(), indent=2))
            return

        if response.success and response.node:
            print(f"Updated {response.node.label}: {response.node.title}")

    # ═══════════════════════════════════════════════════════════════════════════════
    # Delete Response Rendering
    # ═══════════════════════════════════════════════════════════════════════════════

    @staticmethod
    def render_delete_response(response  : Schema__Node__Delete__Response ,      # Render delete result
                               format    : str  = "table"                 ,
                               for_agent : bool = False                   ) -> None:
        if for_agent or format == "json":
            print(json.dumps(response.json(), indent=2))
            return

        if response.success:
            print(f"Deleted {response.label}")
        else:
            print(f"Failed to delete: {response.message}")

    # ═══════════════════════════════════════════════════════════════════════════════
    # Graph Rendering
    # ═══════════════════════════════════════════════════════════════════════════════

    @staticmethod
    def render_graph(response  : Schema__Graph__Response ,                       # Render graph traversal
                     format    : str  = "table"          ,
                     for_agent : bool = False            ) -> None:
        if for_agent or format == "json":
            print(json.dumps(response.json(), indent=2))
            return

        if format == "table":
            print(f"Graph from {response.root} (depth={response.depth})\n")

            print(f"{'Label':<15} {'Type':<12} {'Status':<15} {'Title'}")
            print("─" * 60)
            for node in response.nodes:
                title = str(node.title)[:50] if node.title else ""
                print(f"{str(node.label):<15} {str(node.node_type):<12} {str(node.status):<15} {title}")

            if response.links:
                print(f"\nEdges:")
                for link in response.links:
                    print(f"  {link.source} ──{link.link_type}──▶ {link.target}")

    # ═══════════════════════════════════════════════════════════════════════════════
    # Link Rendering
    # ═══════════════════════════════════════════════════════════════════════════════

    @staticmethod
    def render_link_response(response  : Schema__Link__Create__Response ,        # Render link create result
                             format    : str  = "table"                 ,
                             for_agent : bool = False                   ) -> None:
        if for_agent or format == "json":
            print(json.dumps(response.json(), indent=2))
            return

        if response.success and response.source_link:
            link = response.source_link
            print(f"Linked: {link.verb} → {link.target_label}")

    @staticmethod
    def render_unlink_response(response  : Schema__Link__Delete__Response ,      # Render link delete result
                               format    : str  = "table"                 ,
                               for_agent : bool = False                   ) -> None:
        if for_agent or format == "json":
            print(json.dumps(response.json(), indent=2))
            return

        if response.success:
            print(f"Unlinked: {response.source_label} → {response.target_label}")

    @staticmethod
    def render_links_list(response  : Schema__Link__List__Response ,             # Render links list
                          format    : str  = "table"               ,
                          for_agent : bool = False                 ) -> None:
        if for_agent or format == "json":
            print(json.dumps(response.json(), indent=2))
            return

        if not response.links:
            print("No links found.")
            return

        print(f"{'Verb':<20} {'Target'}")
        print("─" * 40)
        for link in response.links:
            print(f"{str(link.verb):<20} {link.target_label}")

    # ═══════════════════════════════════════════════════════════════════════════════
    # Comment Rendering
    # ═══════════════════════════════════════════════════════════════════════════════

    @staticmethod
    def render_comment_response(response  : Schema__Comment__Response ,          # Render comment result
                                format    : str  = "table"            ,
                                for_agent : bool = False              ) -> None:
        if for_agent or format == "json":
            print(json.dumps(response.json(), indent=2))
            return

        if response.success and response.comment:
            comment = response.comment
            print(f"Comment {comment.id} by {comment.author}:")
            print(f"  {comment.text}")

    @staticmethod
    def render_comments_list(response  : Schema__Comment__List__Response ,       # Render comments list
                             format    : str  = "table"                  ,
                             for_agent : bool = False                    ) -> None:
        if for_agent or format == "json":
            print(json.dumps(response.json(), indent=2))
            return

        if response.total == 0:
            print("No comments found.")
            return

        for comment in response.comments:
            print(f"[{comment.id}] {comment.author} at {comment.created_at}:")
            print(f"  {comment.text}")
            print()

    @staticmethod
    def render_comment_delete(response  : Schema__Comment__Delete__Response ,    # Render comment delete
                              format    : str  = "table"                    ,
                              for_agent : bool = False                      ) -> None:
        if for_agent or format == "json":
            print(json.dumps(response.json(), indent=2))
            return

        if response.success:
            print(f"Deleted comment {response.comment_id}")

    # ═══════════════════════════════════════════════════════════════════════════════
    # Type Rendering
    # ═══════════════════════════════════════════════════════════════════════════════

    @staticmethod
    def render_node_types(types     : List[Schema__Node__Type] ,                 # Render node types list
                          format    : str  = "table"           ,
                          for_agent : bool = False             ) -> None:
        if for_agent or format == "json":
            print(json.dumps([t.json() for t in types], indent=2))
            return

        if not types:
            print("No node types defined.")
            return

        print(f"{'Name':<15} {'Display':<15} {'Color':<10} {'Statuses'}")
        print("─" * 60)
        for t in types:
            statuses = ', '.join(str(s) for s in t.statuses) if t.statuses else ''
            print(f"{str(t.name):<15} {str(t.display_name):<15} {str(t.color):<10} {statuses}")

    @staticmethod
    def render_link_types(types     : List[Schema__Link__Type] ,                 # Render link types list
                          format    : str  = "table"           ,
                          for_agent : bool = False             ) -> None:
        if for_agent or format == "json":
            print(json.dumps([t.json() for t in types], indent=2))
            return

        if not types:
            print("No link types defined.")
            return

        print(f"{'Verb':<20} {'Inverse':<20} {'Description'}")
        print("─" * 60)
        for t in types:
            desc = str(t.description)[:30] if t.description else ''
            print(f"{str(t.verb):<20} {str(t.inverse_verb):<20} {desc}")

# ═══════════════════════════════════════════════════════════════════════════════
# CLI__Context - Discovers .issues/ directory and initialises services
# ═══════════════════════════════════════════════════════════════════════════════

import os

from osbot_utils.type_safe.Type_Safe                                            import Type_Safe
from issues_fs.issues.graph_services.Graph__Repository__Factory                 import Graph__Repository__Factory
from issues_fs.issues.graph_services.Graph__Repository                          import Graph__Repository
from issues_fs.issues.graph_services.Node__Service                              import Node__Service
from issues_fs.issues.graph_services.Link__Service                              import Link__Service
from issues_fs.issues.graph_services.Comments__Service                          import Comments__Service
from issues_fs.issues.graph_services.Type__Service                              import Type__Service


class CLI__Context(Type_Safe):                                                   # CLI runtime context
    repository       : Graph__Repository  = None                                 # Storage layer
    node_service     : Node__Service      = None                                 # Node operations
    link_service     : Link__Service      = None                                 # Link operations
    comments_service : Comments__Service  = None                                 # Comment operations
    type_service     : Type__Service      = None                                 # Type operations
    root_path        : str                = None                                 # Discovered .issues/ path

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.repository is None:
            self.root_path  = self.discover_issues_root()
            self.repository = Graph__Repository__Factory.create_local_disk(root_path = self.root_path)

        self.node_service     = Node__Service    (repository = self.repository)
        self.link_service     = Link__Service    (repository = self.repository)
        self.comments_service = Comments__Service(repository = self.repository)
        self.type_service     = Type__Service    (repository = self.repository)

    def discover_issues_root(self) -> str:                                       # Walk up from cwd to find .issues/
        current = os.getcwd()

        while True:
            candidate = os.path.join(current, '.issues')
            if os.path.isdir(candidate):
                return candidate

            parent = os.path.dirname(current)
            if parent == current:                                                # Reached filesystem root
                raise FileNotFoundError(
                    "No .issues/ directory found. "
                    "Run 'issues-fs init' to create one, "
                    "or run this command from within an Issues-FS repository."
                )
            current = parent

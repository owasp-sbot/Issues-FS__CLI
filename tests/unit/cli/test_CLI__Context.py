# ═══════════════════════════════════════════════════════════════════════════════
# Test CLI__Context - Repository discovery and service initialization
# ═══════════════════════════════════════════════════════════════════════════════

import os
import tempfile
import shutil

from unittest                                                                   import TestCase

from issues_fs_cli.cli.CLI__Context                                             import CLI__Context
from issues_fs.issues.graph_services.Graph__Repository                          import Graph__Repository
from issues_fs.issues.graph_services.Graph__Repository__Factory                 import Graph__Repository__Factory
from issues_fs.issues.graph_services.Node__Service                              import Node__Service
from issues_fs.issues.graph_services.Link__Service                              import Link__Service
from issues_fs.issues.graph_services.Comments__Service                          import Comments__Service
from issues_fs.issues.graph_services.Type__Service                              import Type__Service


class test_CLI__Context(TestCase):

    @classmethod
    def setUpClass(cls):                                                         # Create temp directory with .issues/
        cls.temp_dir    = tempfile.mkdtemp()
        cls.issues_dir  = os.path.join(cls.temp_dir, '.issues')
        os.makedirs(cls.issues_dir)

        # Initialize with types
        repo         = Graph__Repository__Factory.create_local_disk(root_path = cls.issues_dir)
        type_service = Type__Service(repository = repo)
        type_service.initialize_default_types()

        cls.original_cwd = os.getcwd()

    @classmethod
    def tearDownClass(cls):                                                      # Cleanup temp directory
        os.chdir(cls.original_cwd)
        shutil.rmtree(cls.temp_dir)

    def setUp(self):                                                             # Change to temp directory
        os.chdir(self.temp_dir)

    def tearDown(self):                                                          # Restore original cwd
        os.chdir(self.original_cwd)

    # ═══════════════════════════════════════════════════════════════════════════════
    # Tests for __init__
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__init__(self):                                                      # Test context initialization
        with CLI__Context() as ctx:
            assert ctx is not None
            assert ctx.repository       is not None
            assert ctx.node_service     is not None
            assert ctx.link_service     is not None
            assert ctx.comments_service is not None
            assert ctx.type_service     is not None

    def test__init____service_types(self):                                       # Test service types
        with CLI__Context() as ctx:
            assert type(ctx.repository)       is Graph__Repository
            assert type(ctx.node_service)     is Node__Service
            assert type(ctx.link_service)     is Link__Service
            assert type(ctx.comments_service) is Comments__Service
            assert type(ctx.type_service)     is Type__Service

    def test__init____with_injected_repository(self):                            # Test context with injected repo
        repo = Graph__Repository__Factory.create_memory()
        with CLI__Context(repository = repo) as ctx:
            assert ctx.repository is repo

    # ═══════════════════════════════════════════════════════════════════════════════
    # Tests for discover_issues_root
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_discover_issues_root__from_root(self):                              # Test discovery from root
        with CLI__Context() as ctx:
            assert os.path.realpath(ctx.root_path) == os.path.realpath(self.issues_dir)

    def test_discover_issues_root__from_subdirectory(self):                      # Test discovery from subdir
        subdir = os.path.join(self.temp_dir, 'src', 'deep', 'nested')
        os.makedirs(subdir)
        os.chdir(subdir)

        with CLI__Context() as ctx:
            assert os.path.realpath(ctx.root_path) == os.path.realpath(self.issues_dir)

    def test_discover_issues_root__not_found(self):                              # Test error when not found
        empty_dir = tempfile.mkdtemp()
        os.chdir(empty_dir)

        try:
            with self.assertRaises(FileNotFoundError) as context:
                CLI__Context()

            assert "No .issues/ directory found" in str(context.exception)
        finally:
            os.chdir(self.original_cwd)
            shutil.rmtree(empty_dir)

    # ═══════════════════════════════════════════════════════════════════════════════
    # Tests for service operations
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_node_service__create_and_get(self):                                 # Test node service works
        with CLI__Context() as ctx:
            from issues_fs.schemas.graph.Schema__Node__Create__Request          import Schema__Node__Create__Request
            from issues_fs.schemas.graph.Safe_Str__Graph_Types                  import Safe_Str__Node_Type

            request  = Schema__Node__Create__Request(node_type = Safe_Str__Node_Type("bug") ,
                                                     title     = "Test bug"                 )
            response = ctx.node_service.create_node(request)

            assert response.success is True
            assert response.node is not None
            assert str(response.node.title) == "Test bug"

    def test_type_service__list_types(self):                                     # Test type service works
        with CLI__Context() as ctx:
            types = ctx.type_service.list_node_types()

            assert types is not None
            assert len(types) > 0

            type_names = [str(t.name) for t in types]
            assert "bug"  in type_names
            assert "task" in type_names

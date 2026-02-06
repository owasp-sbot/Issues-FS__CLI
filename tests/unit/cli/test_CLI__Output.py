# ═══════════════════════════════════════════════════════════════════════════════
# Test CLI__Output - Output formatting utilities
# ═══════════════════════════════════════════════════════════════════════════════

import io
import sys
import json

from unittest                                                                   import TestCase

from issues_fs_cli.cli.CLI__Output                                              import CLI__Output
from issues_fs.schemas.graph.Schema__Node                                       import Schema__Node
from issues_fs.schemas.graph.Schema__Node__Summary                              import Schema__Node__Summary
from issues_fs.schemas.graph.Schema__Node__Create__Response                     import Schema__Node__Create__Response
from issues_fs.schemas.graph.Schema__Node__List__Response                       import Schema__Node__List__Response
from issues_fs.schemas.graph.Schema__Node__Delete__Response                     import Schema__Node__Delete__Response
from issues_fs.schemas.graph.Safe_Str__Graph_Types                              import Safe_Str__Node_Type
from issues_fs.schemas.graph.Safe_Str__Graph_Types                              import Safe_Str__Node_Label
from issues_fs.schemas.graph.Safe_Str__Graph_Types                              import Safe_Str__Status


class test_CLI__Output(TestCase):

    def setUp(self):                                                             # Capture stdout/stderr
        self.held_stdout = sys.stdout
        self.held_stderr = sys.stderr
        sys.stdout = io.StringIO()
        sys.stderr = io.StringIO()

    def tearDown(self):                                                          # Restore stdout/stderr
        sys.stdout = self.held_stdout
        sys.stderr = self.held_stderr

    def get_stdout(self):                                                        # Get captured stdout
        sys.stdout.seek(0)
        return sys.stdout.read()

    def get_stderr(self):                                                        # Get captured stderr
        sys.stderr.seek(0)
        return sys.stderr.read()

    # ═══════════════════════════════════════════════════════════════════════════════
    # Tests for error
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_error__text_mode(self):                                             # Test error in text mode
        CLI__Output.error("Something went wrong")
        output = self.get_stderr()
        assert "Error: Something went wrong" in output

    def test_error__agent_mode(self):                                            # Test error in agent mode
        CLI__Output.error("Something went wrong", for_agent=True)
        output = self.get_stdout()
        data   = json.loads(output)
        assert data["success"] is False
        assert data["error"]   == "Something went wrong"

    # ═══════════════════════════════════════════════════════════════════════════════
    # Tests for success
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_success(self):                                                      # Test success message
        CLI__Output.success("Operation completed")
        output = self.get_stdout()
        assert "Operation completed" in output

    # ═══════════════════════════════════════════════════════════════════════════════
    # Tests for render_node
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_render_node__table(self):                                           # Test node table rendering
        node = Schema__Node(node_type = Safe_Str__Node_Type("bug")   ,
                            label     = Safe_Str__Node_Label("Bug-1"),
                            title     = "Test bug"                   ,
                            status    = Safe_Str__Status("backlog")  )

        CLI__Output.render_node(node, format="table")
        output = self.get_stdout()

        assert "Bug-1"   in output
        assert "bug"     in output
        assert "Test bug" in output
        assert "backlog" in output

    def test_render_node__json(self):                                            # Test node JSON rendering
        node = Schema__Node(node_type = Safe_Str__Node_Type("bug")   ,
                            label     = Safe_Str__Node_Label("Bug-1"),
                            title     = "Test bug"                   ,
                            status    = Safe_Str__Status("backlog")  )

        CLI__Output.render_node(node, format="json")
        output = self.get_stdout()
        data   = json.loads(output)

        assert data["label"]     == "Bug-1"
        assert data["node_type"] == "bug"
        assert data["title"]     == "Test bug"

    def test_render_node__for_agent(self):                                       # Test node agent mode
        node = Schema__Node(node_type = Safe_Str__Node_Type("bug")   ,
                            label     = Safe_Str__Node_Label("Bug-1"),
                            title     = "Test bug"                   ,
                            status    = Safe_Str__Status("backlog")  )

        CLI__Output.render_node(node, for_agent=True)
        output = self.get_stdout()
        data   = json.loads(output)

        assert "node_id" in data                                                 # Agent mode includes all fields

    def test_render_node__markdown(self):                                        # Test node markdown rendering
        node = Schema__Node(node_type = Safe_Str__Node_Type("bug")   ,
                            label     = Safe_Str__Node_Label("Bug-1"),
                            title     = "Test bug"                   ,
                            status    = Safe_Str__Status("backlog")  )

        CLI__Output.render_node(node, format="markdown")
        output = self.get_stdout()

        assert "# Bug-1: Test bug" in output
        assert "**Type:**"         in output
        assert "**Status:**"       in output

    # ═══════════════════════════════════════════════════════════════════════════════
    # Tests for render_list
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_render_list__empty(self):                                           # Test empty list
        response = Schema__Node__List__Response(success = True ,
                                                nodes   = []   ,
                                                total   = 0    )

        CLI__Output.render_list(response)
        output = self.get_stdout()

        assert "No issues found" in output

    def test_render_list__with_nodes(self):                                      # Test list with nodes
        node1 = Schema__Node__Summary(node_type = Safe_Str__Node_Type("bug")   ,
                                      label     = Safe_Str__Node_Label("Bug-1"),
                                      title     = "First bug"                  ,
                                      status    = Safe_Str__Status("backlog")  )
        node2 = Schema__Node__Summary(node_type = Safe_Str__Node_Type("task")   ,
                                      label     = Safe_Str__Node_Label("Task-1"),
                                      title     = "First task"                  ,
                                      status    = Safe_Str__Status("todo")      )

        response = Schema__Node__List__Response(success = True           ,
                                                nodes   = [node1, node2] ,
                                                total   = 2              )

        CLI__Output.render_list(response)
        output = self.get_stdout()

        assert "Bug-1"      in output
        assert "Task-1"     in output
        assert "First bug"  in output
        assert "First task" in output
        assert "Total: 2"   in output

    def test_render_list__json(self):                                            # Test list JSON rendering
        node = Schema__Node__Summary(node_type = Safe_Str__Node_Type("bug")   ,
                                     label     = Safe_Str__Node_Label("Bug-1"),
                                     title     = "Test bug"                   ,
                                     status    = Safe_Str__Status("backlog")  )

        response = Schema__Node__List__Response(success = True   ,
                                                nodes   = [node] ,
                                                total   = 1      )

        CLI__Output.render_list(response, format="json")
        output = self.get_stdout()
        data   = json.loads(output)

        assert data["success"] is True
        assert data["total"]   == 1
        assert len(data["nodes"]) == 1

    # ═══════════════════════════════════════════════════════════════════════════════
    # Tests for render_create_response
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_render_create_response__success(self):                              # Test successful create
        node = Schema__Node(node_type = Safe_Str__Node_Type("bug")   ,
                            label     = Safe_Str__Node_Label("Bug-1"),
                            title     = "New bug"                    ,
                            status    = Safe_Str__Status("backlog")  )

        response = Schema__Node__Create__Response(success = True ,
                                                  node    = node )

        CLI__Output.render_create_response(response)
        output = self.get_stdout()

        assert "Created Bug-1: New bug" in output

    # ═══════════════════════════════════════════════════════════════════════════════
    # Tests for render_delete_response
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_render_delete_response__success(self):                              # Test successful delete
        response = Schema__Node__Delete__Response(success = True    ,
                                                  deleted = True    ,
                                                  label   = "Bug-1" )

        CLI__Output.render_delete_response(response)
        output = self.get_stdout()

        assert "Deleted Bug-1" in output

    def test_render_delete_response__failure(self):                              # Test failed delete
        response = Schema__Node__Delete__Response(success = False          ,
                                                  deleted = False          ,
                                                  label   = "Bug-99"       ,
                                                  message = "Node not found")

        CLI__Output.render_delete_response(response)
        output = self.get_stdout()

        assert "Failed to delete: Node not found" in output

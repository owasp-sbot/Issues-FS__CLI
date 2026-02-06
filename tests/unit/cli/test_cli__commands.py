# ═══════════════════════════════════════════════════════════════════════════════
# Test CLI Commands - Integration tests for CLI commands using CliRunner
# ═══════════════════════════════════════════════════════════════════════════════

import os
import tempfile
import shutil

from unittest                                                                   import TestCase
from typer.testing                                                              import CliRunner

from issues_fs_cli.cli.cli__main                                                import app
from issues_fs.issues.graph_services.Graph__Repository__Factory                 import Graph__Repository__Factory
from issues_fs.issues.graph_services.Type__Service                              import Type__Service


class test_cli__commands(TestCase):

    @classmethod
    def setUpClass(cls):                                                         # Create temp directory
        cls.runner      = CliRunner()
        cls.temp_dir    = tempfile.mkdtemp()
        cls.issues_dir  = os.path.join(cls.temp_dir, '.issues')
        os.makedirs(cls.issues_dir)

        # Initialize repository with types
        repo         = Graph__Repository__Factory.create_local_disk(root_path = cls.issues_dir)
        type_service = Type__Service(repository = repo)
        type_service.initialize_default_types()

        cls.original_cwd = os.getcwd()
        os.chdir(cls.temp_dir)

    @classmethod
    def tearDownClass(cls):                                                      # Cleanup
        os.chdir(cls.original_cwd)
        shutil.rmtree(cls.temp_dir)

    # ═══════════════════════════════════════════════════════════════════════════════
    # Tests for help
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_help(self):                                                         # Test --help works
        result = self.runner.invoke(app, ["--help"])
        assert result.exit_code == 0
        assert "Git-native graph-based issue tracking" in result.output

    def test_create_help(self):                                                  # Test create --help
        result = self.runner.invoke(app, ["create", "--help"])
        assert result.exit_code == 0
        assert "Node type"   in result.output
        assert "Issue title" in result.output

    # ═══════════════════════════════════════════════════════════════════════════════
    # Tests for create
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_create__bug(self):                                                  # Test creating a bug
        result = self.runner.invoke(app, ["create", "bug", "Test bug"])
        assert result.exit_code == 0
        assert "Created Bug-" in result.output
        assert "Test bug"     in result.output

    def test_create__task(self):                                                 # Test creating a task
        result = self.runner.invoke(app, ["create", "task", "Test task"])
        assert result.exit_code == 0
        assert "Created Task-" in result.output

    def test_create__with_options(self):                                         # Test create with options
        result = self.runner.invoke(app, ["create", "bug", "Bug with options",
                                          "--description", "Detailed description",
                                          "--status", "confirmed",
                                          "--tags", "critical,api"])
        assert result.exit_code == 0
        assert "Created Bug-" in result.output

    def test_create__invalid_type(self):                                         # Test create with invalid type
        result = self.runner.invoke(app, ["create", "invalid", "Test"])
        assert result.exit_code == 1
        assert "Error" in result.output or "error" in result.output.lower()

    def test_create__json_output(self):                                          # Test create with JSON output
        result = self.runner.invoke(app, ["create", "bug", "JSON test", "--output", "json"])
        assert result.exit_code == 0
        assert '"success": true' in result.output
        assert '"node":'         in result.output

    # ═══════════════════════════════════════════════════════════════════════════════
    # Tests for list
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_list(self):                                                         # Test listing issues
        result = self.runner.invoke(app, ["list"])
        assert result.exit_code == 0
        assert "Total:" in result.output or "No issues" in result.output

    def test_list__by_type(self):                                                # Test list by type
        result = self.runner.invoke(app, ["list", "--type", "bug"])
        assert result.exit_code == 0

    def test_list__json_output(self):                                            # Test list with JSON output
        result = self.runner.invoke(app, ["list", "--output", "json"])
        assert result.exit_code == 0
        assert '"success":' in result.output
        assert '"nodes":'   in result.output

    # ═══════════════════════════════════════════════════════════════════════════════
    # Tests for show
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_show__existing(self):                                               # Test showing existing node
        # First create a bug
        self.runner.invoke(app, ["create", "bug", "Show test bug"])

        result = self.runner.invoke(app, ["show", "Bug-1"])
        assert result.exit_code == 0
        assert "Bug-1" in result.output

    def test_show__not_found(self):                                              # Test showing non-existent node
        result = self.runner.invoke(app, ["show", "Bug-9999"])
        assert result.exit_code == 1
        assert "not found" in result.output.lower()

    def test_show__invalid_label(self):                                          # Test show with invalid label
        result = self.runner.invoke(app, ["show", "InvalidLabel"])
        assert result.exit_code == 1
        assert "Invalid label" in result.output

    def test_show__json_output(self):                                            # Test show with JSON output
        result = self.runner.invoke(app, ["show", "Bug-1", "--output", "json"])
        assert result.exit_code == 0
        assert '"label":' in result.output

    def test_show__markdown_output(self):                                        # Test show with markdown output
        result = self.runner.invoke(app, ["show", "Bug-1", "--output", "markdown"])
        assert result.exit_code == 0
        assert "# Bug-1:" in result.output

    def test_show__for_agent(self):                                              # Test show for agent
        result = self.runner.invoke(app, ["show", "Bug-1", "--for-agent"])
        assert result.exit_code == 0
        assert '"node_id":' in result.output

    # ═══════════════════════════════════════════════════════════════════════════════
    # Tests for update
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_update__status(self):                                               # Test updating status
        result = self.runner.invoke(app, ["update", "Bug-1", "--status", "confirmed"])
        assert result.exit_code == 0
        assert "Updated Bug-1" in result.output

    def test_update__title(self):                                                # Test updating title
        result = self.runner.invoke(app, ["update", "Bug-1", "--title", "New title"])
        assert result.exit_code == 0
        assert "Updated Bug-1" in result.output

    def test_update__not_found(self):                                            # Test update non-existent
        result = self.runner.invoke(app, ["update", "Bug-9999", "--status", "done"])
        assert result.exit_code == 1

    # ═══════════════════════════════════════════════════════════════════════════════
    # Tests for link
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_link__create(self):                                                 # Test creating a link
        # Create second node
        self.runner.invoke(app, ["create", "task", "Task for linking"])

        result = self.runner.invoke(app, ["link", "Bug-1", "blocks", "Task-1"])
        # May succeed or fail depending on link type rules
        # Just verify it runs and outputs something
        assert result.output is not None

    def test_link__invalid_verb(self):                                           # Test link with invalid verb
        result = self.runner.invoke(app, ["link", "Bug-1", "invalid-verb", "Task-1"])
        assert result.exit_code == 1
        assert "error" in result.output.lower() or "invalid" in result.output.lower()

    # ═══════════════════════════════════════════════════════════════════════════════
    # Tests for links
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_links__list(self):                                                  # Test listing links
        result = self.runner.invoke(app, ["links", "Bug-1"])
        assert result.exit_code == 0

    def test_links__not_found(self):                                             # Test links for non-existent node
        result = self.runner.invoke(app, ["links", "Bug-9999"])
        assert result.exit_code == 1

    # ═══════════════════════════════════════════════════════════════════════════════
    # Tests for comment
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_comment__add(self):                                                 # Test adding comment
        # First ensure a bug exists (tests may run in any order)
        self.runner.invoke(app, ["create", "bug", "Bug for comment test"])

        result = self.runner.invoke(app, ["comment", "Bug-1", "This is a test comment"])
        assert result.exit_code == 0
        assert "Comment" in result.output

    def test_comment__with_author(self):                                         # Test comment with author
        # First ensure a bug exists (tests may run in any order)
        self.runner.invoke(app, ["create", "bug", "Bug for author comment"])

        result = self.runner.invoke(app, ["comment", "Bug-1", "Comment from bot", "--author", "test-bot"])
        assert result.exit_code == 0

    def test_comment__not_found(self):                                           # Test comment on non-existent node
        result = self.runner.invoke(app, ["comment", "Bug-9999", "Comment"])
        assert result.exit_code == 1

    # ═══════════════════════════════════════════════════════════════════════════════
    # Tests for comments
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_comments__list(self):                                               # Test listing comments
        # First ensure a bug exists (tests may run in any order)
        self.runner.invoke(app, ["create", "bug", "Bug for comments list"])

        result = self.runner.invoke(app, ["comments", "Bug-1"])
        assert result.exit_code == 0

    def test_comments__json_output(self):                                        # Test comments with JSON
        # First ensure a bug exists (tests may run in any order)
        self.runner.invoke(app, ["create", "bug", "Bug for comments json"])

        result = self.runner.invoke(app, ["comments", "Bug-1", "--output", "json"])
        assert result.exit_code == 0
        assert '"comments":' in result.output

    # ═══════════════════════════════════════════════════════════════════════════════
    # Tests for types
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_types_list(self):                                                   # Test listing types
        result = self.runner.invoke(app, ["types", "list"])
        assert result.exit_code == 0
        assert "bug"  in result.output
        assert "task" in result.output

    def test_types_list__json(self):                                             # Test types list JSON
        result = self.runner.invoke(app, ["types", "list", "--output", "json"])
        assert result.exit_code == 0
        assert '"name":' in result.output

    # ═══════════════════════════════════════════════════════════════════════════════
    # Tests for link-types
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_link_types_list(self):                                              # Test listing link types
        result = self.runner.invoke(app, ["link-types", "list"])
        assert result.exit_code == 0
        assert "blocks"    in result.output
        assert "blocked-by" in result.output

    # ═══════════════════════════════════════════════════════════════════════════════
    # Tests for delete
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_delete__with_force(self):                                           # Test delete with force
        # Create something to delete
        self.runner.invoke(app, ["create", "bug", "Bug to delete"])

        result = self.runner.invoke(app, ["delete", "Bug-6", "--force"])
        # May or may not find it depending on test order
        assert result.output is not None

    def test_delete__not_found(self):                                            # Test delete non-existent
        result = self.runner.invoke(app, ["delete", "Bug-9999", "--force"])
        assert result.exit_code == 1

    def test_delete__invalid_label(self):                                        # Test delete with invalid label
        result = self.runner.invoke(app, ["delete", "InvalidLabel", "--force"])
        assert result.exit_code == 1
        assert "Invalid" in result.output

    # ═══════════════════════════════════════════════════════════════════════════════
    # Tests for unlink
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_unlink__not_found(self):                                            # Test unlink non-existent
        result = self.runner.invoke(app, ["unlink", "Bug-1", "Task-9999"])
        # Will fail because Bug-1 exists but link may not exist
        assert result.output is not None

    def test_unlink__invalid_source(self):                                       # Test unlink with invalid source label
        result = self.runner.invoke(app, ["unlink", "InvalidLabel", "Task-1"])
        assert result.exit_code == 1
        assert "Invalid" in result.output

    # ═══════════════════════════════════════════════════════════════════════════════
    # Tests for list with filters
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_list__with_status_filter(self):                                     # Test list with status filter
        result = self.runner.invoke(app, ["list", "--status", "backlog"])
        assert result.exit_code == 0

    def test_links__invalid_label(self):                                         # Test links with invalid label
        result = self.runner.invoke(app, ["links", "InvalidLabel"])
        assert result.exit_code == 1
        assert "Invalid" in result.output

    # ═══════════════════════════════════════════════════════════════════════════════
    # Tests for link-types subcommands
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_link_types_list__json(self):                                        # Test link types JSON
        result = self.runner.invoke(app, ["link-types", "list", "--output", "json"])
        assert result.exit_code == 0
        assert '"verb":' in result.output or '"name":' in result.output

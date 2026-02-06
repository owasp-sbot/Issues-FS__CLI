# ═══════════════════════════════════════════════════════════════════════════════
# Test CLI Init Command - Repository initialization
# ═══════════════════════════════════════════════════════════════════════════════

import os
import tempfile
import shutil

from unittest                                                                   import TestCase
from typer.testing                                                              import CliRunner

from issues_fs_cli.cli.cli__main                                                import app


class test_cli__init(TestCase):

    @classmethod
    def setUpClass(cls):                                                         # Setup test runner
        cls.runner       = CliRunner()
        cls.original_cwd = os.getcwd()

    # todo: we should be using the Temp_Folder() class and this folder creation and deletion should be happing on setUpClass and tearDownClass
    def setUp(self):                                                             # Create fresh temp dir for each test

        self.temp_dir = tempfile.mkdtemp()
        os.chdir(self.temp_dir)

    def tearDown(self):                                                          # Cleanup
        os.chdir(self.original_cwd)
        shutil.rmtree(self.temp_dir)

    # ═══════════════════════════════════════════════════════════════════════════════
    # Tests for init command
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_init__creates_issues_directory(self):                               # Test init creates .issues/
        result = self.runner.invoke(app, ["init"])

        assert result.exit_code == 0
        issues_path = os.path.join(os.path.realpath(self.temp_dir), '.issues')
        assert os.path.isdir(issues_path)
        assert "Initialized" in result.output

    def test_init__creates_types(self):                                          # Test init creates node-types.json
        self.runner.invoke(app, ["init"])

        # Files are stored in .issues/.issues/config/ directory
        types_path = os.path.join(os.path.realpath(self.temp_dir), '.issues', '.issues', 'config', 'node-types.json')
        assert os.path.isfile(types_path)

    def test_init__creates_link_types(self):                                     # Test init creates link-types.json
        self.runner.invoke(app, ["init"])

        # Files are stored in .issues/.issues/config/ directory
        link_types_path = os.path.join(os.path.realpath(self.temp_dir), '.issues', '.issues', 'config', 'link-types.json')
        assert os.path.isfile(link_types_path)

    def test_init__already_exists(self):                                         # Test init when already exists
        self.runner.invoke(app, ["init"])                                        # First init

        result = self.runner.invoke(app, ["init"])                               # Second init
        assert result.exit_code == 1
        assert "already exists" in result.output

    def test_init__custom_path(self):                                            # Test init with custom path
        subdir = os.path.join(os.path.realpath(self.temp_dir), 'custom')
        os.makedirs(subdir)

        result = self.runner.invoke(app, ["init", "--path", subdir])

        assert result.exit_code == 0
        assert os.path.isdir(os.path.join(subdir, '.issues'))

    def test_init__for_agent(self):                                              # Test init with agent output
        result = self.runner.invoke(app, ["init", "--for-agent"])

        assert result.exit_code == 0
        assert '"success": true' in result.output
        assert '"issues_path":'  in result.output

    def test_init__then_list_works(self):                                        # Test init enables list command
        self.runner.invoke(app, ["init"])

        result = self.runner.invoke(app, ["list"])
        assert result.exit_code == 0
        assert "No issues found" in result.output

    def test_init__then_create_works(self):                                      # Test init enables create command
        self.runner.invoke(app, ["init"])

        result = self.runner.invoke(app, ["create", "bug", "First bug"])
        assert result.exit_code == 0
        assert "Created Bug-1" in result.output

    def test_init__types_list_after_init(self):                                  # Test types are available after init
        self.runner.invoke(app, ["init"])

        result = self.runner.invoke(app, ["types", "list"])
        assert result.exit_code == 0
        assert "bug"     in result.output
        assert "task"    in result.output
        assert "feature" in result.output
        assert "person"  in result.output

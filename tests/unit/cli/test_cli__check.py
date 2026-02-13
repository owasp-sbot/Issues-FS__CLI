# ═══════════════════════════════════════════════════════════════════════════════
# test_cli__check - Tests for the check CLI command
# ═══════════════════════════════════════════════════════════════════════════════

import os
import tempfile
import shutil

from unittest                                                                   import TestCase
from typer.testing                                                              import CliRunner

from issues_fs_cli.cli.cli__main                                                import app


class test_cli__check(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.runner       = CliRunner()
        cls.temp_dir     = tempfile.mkdtemp()
        cls.issues_dir   = os.path.join(cls.temp_dir, '.issues')
        os.makedirs(cls.issues_dir)
        cls.original_cwd = os.getcwd()
        os.chdir(cls.temp_dir)

    @classmethod
    def tearDownClass(cls):
        os.chdir(cls.original_cwd)
        shutil.rmtree(cls.temp_dir)

    def setUp(self):
        for f in os.listdir(self.issues_dir):
            if f.endswith('.issues'):
                os.remove(os.path.join(self.issues_dir, f))

    # ═══════════════════════════════════════════════════════════════════════════
    # Basic Check
    # ═══════════════════════════════════════════════════════════════════════════

    def test__check__no_files(self):
        result = self.runner.invoke(app, ["check"])
        assert result.exit_code == 0
        assert "No .issues files" in result.output

    def test__check__valid_file(self):
        path = os.path.join(self.issues_dir, 'tasks.issues')
        with open(path, 'w') as f:
            f.write('Task-1 | todo | First task\nTask-2 | done | Second task')

        result = self.runner.invoke(app, ["check"])
        assert result.exit_code == 0
        assert 'PASS' in result.output
        assert 'Issues: 2' in result.output

    def test__check__invalid_file(self):
        path = os.path.join(self.issues_dir, 'bad.issues')
        with open(path, 'w') as f:
            f.write('Task-1 | todo | Good\nbad line\nalso bad')

        result = self.runner.invoke(app, ["check"])
        assert result.exit_code == 1
        assert 'FAIL' in result.output

    # ═══════════════════════════════════════════════════════════════════════════
    # Specific File
    # ═══════════════════════════════════════════════════════════════════════════

    def test__check__specific_file(self):
        path = os.path.join(self.issues_dir, 'specific.issues')
        with open(path, 'w') as f:
            f.write('Bug-1 | confirmed | A bug')

        result = self.runner.invoke(app, ["check", "specific.issues"])
        assert result.exit_code == 0
        assert 'PASS' in result.output

    def test__check__missing_file(self):
        result = self.runner.invoke(app, ["check", "ghost.issues"])
        assert result.exit_code == 1
        assert 'not found' in result.output.lower()

    # ═══════════════════════════════════════════════════════════════════════════
    # Validation Errors
    # ═══════════════════════════════════════════════════════════════════════════

    def test__check__duplicate_labels(self):
        path = os.path.join(self.issues_dir, 'dups.issues')
        with open(path, 'w') as f:
            f.write('Task-1 | todo | First\nTask-1 | done | Duplicate')

        result = self.runner.invoke(app, ["check"])
        assert result.exit_code == 1
        assert 'Duplicate' in result.output
        assert 'Task-1'    in result.output

    def test__check__broken_refs(self):
        path = os.path.join(self.issues_dir, 'refs.issues')
        with open(path, 'w') as f:
            f.write('Task-1 | todo | Needs -> Ghost-1')

        result = self.runner.invoke(app, ["check"])
        assert result.exit_code == 1
        assert 'Broken'   in result.output
        assert 'Ghost-1'  in result.output

    # ═══════════════════════════════════════════════════════════════════════════
    # Multiple Files
    # ═══════════════════════════════════════════════════════════════════════════

    def test__check__multiple_files(self):
        with open(os.path.join(self.issues_dir, 'a.issues'), 'w') as f:
            f.write('Task-1 | todo | First')
        with open(os.path.join(self.issues_dir, 'b.issues'), 'w') as f:
            f.write('Bug-1 | confirmed | A bug')

        result = self.runner.invoke(app, ["check"])
        assert result.exit_code == 0
        assert 'PASS'       in result.output
        assert 'Issues: 2'  in result.output

# ═══════════════════════════════════════════════════════════════════════════════
# test_cli__normalise - Tests for the normalise CLI command
# ═══════════════════════════════════════════════════════════════════════════════

import json
import os
import tempfile
import shutil

from unittest                                                                   import TestCase
from typer.testing                                                              import CliRunner

from issues_fs_cli.cli.cli__main                                                import app


class test_cli__normalise(TestCase):

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
        data_dir = os.path.join(self.issues_dir, 'data')
        if os.path.exists(data_dir):
            shutil.rmtree(data_dir)

    # ═══════════════════════════════════════════════════════════════════════════
    # No Files
    # ═══════════════════════════════════════════════════════════════════════════

    def test__normalise__no_files(self):
        result = self.runner.invoke(app, ["normalise"])
        assert result.exit_code == 0
        assert "No .issues files" in result.output

    # ═══════════════════════════════════════════════════════════════════════════
    # Dry Run
    # ═══════════════════════════════════════════════════════════════════════════

    def test__normalise__dry_run(self):
        path = os.path.join(self.issues_dir, 'tasks.issues')
        with open(path, 'w') as f:
            f.write('Task-1 | todo | First task\nBug-1 | confirmed | A bug')

        result = self.runner.invoke(app, ["normalise", "--dry-run"])
        assert result.exit_code == 0
        assert 'Would write 2 files' in result.output
        assert 'data/task/Task-1/issue.json' in result.output
        assert 'data/bug/Bug-1/issue.json'   in result.output

        assert not os.path.exists(os.path.join(self.issues_dir, 'data'))

    # ═══════════════════════════════════════════════════════════════════════════
    # Write Files
    # ═══════════════════════════════════════════════════════════════════════════

    def test__normalise__writes_files(self):
        path = os.path.join(self.issues_dir, 'tasks.issues')
        with open(path, 'w') as f:
            f.write('Task-1 | todo | Enable logs')

        result = self.runner.invoke(app, ["normalise"])
        assert result.exit_code == 0
        assert 'Normalised: 1' in result.output

        json_path = os.path.join(self.issues_dir, 'data', 'task', 'Task-1', 'issue.json')
        assert os.path.exists(json_path) is True

        with open(json_path) as f:
            data = json.load(f)
        assert data['label']     == 'Task-1'
        assert data['node_type'] == 'task'
        assert data['status']    == 'todo'
        assert data['title']     == 'Enable logs'

    # ═══════════════════════════════════════════════════════════════════════════
    # Specific File
    # ═══════════════════════════════════════════════════════════════════════════

    def test__normalise__specific_file(self):
        with open(os.path.join(self.issues_dir, 'a.issues'), 'w') as f:
            f.write('Task-1 | todo | From A')
        with open(os.path.join(self.issues_dir, 'b.issues'), 'w') as f:
            f.write('Bug-1 | confirmed | From B')

        result = self.runner.invoke(app, ["normalise", "a.issues", "--dry-run"])
        assert result.exit_code == 0
        assert 'Would write 1 files' in result.output
        assert 'Task-1' in result.output
        assert 'Bug-1'  not in result.output

    def test__normalise__missing_file(self):
        result = self.runner.invoke(app, ["normalise", "ghost.issues"])
        assert result.exit_code == 1
        assert 'not found' in result.output.lower()

    # ═══════════════════════════════════════════════════════════════════════════
    # With Errors
    # ═══════════════════════════════════════════════════════════════════════════

    def test__normalise__with_errors(self):
        path = os.path.join(self.issues_dir, 'mixed.issues')
        with open(path, 'w') as f:
            f.write('Task-1 | todo | Good\nbad line\nTask-2 | done | Also good')

        result = self.runner.invoke(app, ["normalise"])
        assert result.exit_code == 1
        assert 'Normalised: 2'  in result.output
        assert 'Errors (1)'     in result.output

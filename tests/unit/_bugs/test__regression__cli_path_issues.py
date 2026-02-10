import os
from unittest                                                   import TestCase
from osbot_utils.testing.Temp_Folder                            import Temp_Folder
from osbot_utils.utils.Files                                    import path_combine, folder_create, folder_exists
from issues_fs.issues.graph_services.Graph__Repository__Factory import Graph__Repository__Factory
from issues_fs_cli.cli.CLI__Context                             import CLI__Context


class test__regression__cli_path_issues(TestCase):

    @classmethod
    def setUpClass(cls):
        cls.temp_folder   = Temp_Folder().__enter__()                                   # creates temp folder on start
        cls.repo_folder   = cls.temp_folder.full_path
        cls.issues_folder = path_combine(cls.repo_folder,'.issues')
        cls.original_cwd  = os.getcwd()                                                 # save the current path
        os.chdir(cls.temp_folder.full_path)                                             # set the path to cls.repo_folder
        folder_create(cls.issues_folder)

        assert folder_exists(cls.repo_folder  ) is True
        assert folder_exists(cls.issues_folder) is True

    @classmethod
    def tearDownClass(cls):
        cls.temp_folder.__exit__(None, None, None)                                      # deletes temp folder on start
        os.chdir(cls.original_cwd)                                                      # restore original path

        assert folder_exists(cls.repo_folder  ) is False                                # confirm folders have been deleted
        assert folder_exists(cls.issues_folder) is False
    # ═══════════════════════════════════════════════════════════════════════════════
    # Angle 6: CLI context discovery + factory = the full bug chain
    # ═══════════════════════════════════════════════════════════════════════════════

    def test__cli_discovery_returns_dot_issues_path(self):                              # CLI returns .issues/ as root

        ctx = CLI__Context.__new__(CLI__Context)                                    # Create without __init__
        root = ctx.discover_issues_root()                                           # call discover_issues_root()
        assert root.endswith('.issues') is True                                     # Returns path ending in .issues
        assert self.issues_folder       in root                                     # OK: we get the issues folder, note we use 'in' in this test because on osx, the self.issues_folder started with /private



    def test__regression__cli_discovery_path_fed_to_factory_creates_double_path(self):     # Full chain: discover → factory → doubled

        ctx = CLI__Context.__new__(CLI__Context)
        discovered_root = ctx.discover_issues_root()

        repo = Graph__Repository__Factory.create_local_disk(root_path=discovered_root)      # This is what CLI__Context.__init__ does

        assert discovered_root.endswith('.issues')                                          # Storage is rooted at .issues/

        assert repo.path_handler.base_path == '.issues'                                     # Path handler still prepends .issues/

        config_path = repo.path_handler.path_for_node_types()                               # So effective paths are doubled
        #assert config_path == '.issues/config/node-types.json'                              # BUG: effective = .issues/.issues/...
        assert config_path == 'config/node-types.json'                                      # FIXED

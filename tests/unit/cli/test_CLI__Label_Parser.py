# ═══════════════════════════════════════════════════════════════════════════════
# Test CLI__Label_Parser - Label parsing utilities
# ═══════════════════════════════════════════════════════════════════════════════

from unittest                                                                   import TestCase

from issues_fs_cli.cli.CLI__Label_Parser                                        import CLI__Label_Parser
from issues_fs.schemas.graph.Safe_Str__Graph_Types                              import Safe_Str__Node_Type
from issues_fs.schemas.graph.Safe_Str__Graph_Types                              import Safe_Str__Node_Label


class test_CLI__Label_Parser(TestCase):

    def test__init__(self):                                                      # Test class exists and is importable
        assert CLI__Label_Parser is not None

    # ═══════════════════════════════════════════════════════════════════════════════
    # Tests for parse_type
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_parse_type__valid_bug(self):                                        # Test parsing Bug-1
        result = CLI__Label_Parser.parse_type("Bug-1")
        assert result is not None
        assert type(result) is Safe_Str__Node_Type
        assert str(result) == "bug"

    def test_parse_type__valid_task(self):                                       # Test parsing Task-123
        result = CLI__Label_Parser.parse_type("Task-123")
        assert result is not None
        assert str(result) == "task"

    def test_parse_type__valid_feature(self):                                    # Test parsing Feature-5
        result = CLI__Label_Parser.parse_type("Feature-5")
        assert result is not None
        assert str(result) == "feature"

    def test_parse_type__valid_person(self):                                     # Test parsing Person-2
        result = CLI__Label_Parser.parse_type("Person-2")
        assert result is not None
        assert str(result) == "person"

    def test_parse_type__mixed_case(self):                                       # Test parsing with mixed case
        result = CLI__Label_Parser.parse_type("BUG-1")
        assert result is not None
        assert str(result) == "bug"                                              # Lowercase conversion

    def test_parse_type__no_hyphen(self):                                        # Test parsing without hyphen
        result = CLI__Label_Parser.parse_type("Bug1")
        assert result is None

    def test_parse_type__empty_string(self):                                     # Test parsing empty string
        result = CLI__Label_Parser.parse_type("")
        assert result is None

    def test_parse_type__only_hyphen(self):                                      # Test parsing just a hyphen
        result = CLI__Label_Parser.parse_type("-")
        assert result is None

    def test_parse_type__hyphen_at_start(self):                                  # Test hyphen at start
        result = CLI__Label_Parser.parse_type("-123")
        assert result is None                                                    # Empty type portion

    # ═══════════════════════════════════════════════════════════════════════════════
    # Tests for parse_label
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_parse_label__valid_bug(self):                                       # Test parsing Bug-1 label
        result = CLI__Label_Parser.parse_label("Bug-1")
        assert result is not None
        assert type(result) is Safe_Str__Node_Label
        assert str(result) == "Bug-1"

    def test_parse_label__valid_task(self):                                      # Test parsing Task-123
        result = CLI__Label_Parser.parse_label("Task-123")
        assert result is not None
        assert str(result) == "Task-123"

    def test_parse_label__valid_multi_digit(self):                               # Test multi-digit number
        result = CLI__Label_Parser.parse_label("Feature-12345")
        assert result is not None
        assert str(result) == "Feature-12345"

    def test_parse_label__no_hyphen(self):                                       # Test without hyphen
        result = CLI__Label_Parser.parse_label("Bug1")
        assert result is None

    def test_parse_label__empty_string(self):                                    # Test empty string
        result = CLI__Label_Parser.parse_label("")
        assert result is None

    # ═══════════════════════════════════════════════════════════════════════════════
    # Tests for parse (combined)
    # ═══════════════════════════════════════════════════════════════════════════════

    def test_parse__valid_bug(self):                                             # Test combined parse Bug-1
        node_type, node_label = CLI__Label_Parser.parse("Bug-1")
        assert node_type  is not None
        assert node_label is not None
        assert str(node_type)  == "bug"
        assert str(node_label) == "Bug-1"

    def test_parse__valid_task(self):                                            # Test combined parse Task-123
        node_type, node_label = CLI__Label_Parser.parse("Task-123")
        assert str(node_type)  == "task"
        assert str(node_label) == "Task-123"

    def test_parse__invalid_no_hyphen(self):                                     # Test combined parse without hyphen
        node_type, node_label = CLI__Label_Parser.parse("Bug1")
        assert node_type  is None
        assert node_label is None

    def test_parse__invalid_empty(self):                                         # Test combined parse empty
        node_type, node_label = CLI__Label_Parser.parse("")
        assert node_type  is None
        assert node_label is None

    def test_parse__hyphen_only(self):                                           # Test combined parse hyphen only
        node_type, node_label = CLI__Label_Parser.parse("-")
        assert node_type  is None
        assert node_label is None

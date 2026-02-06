# ═══════════════════════════════════════════════════════════════════════════════
# CLI__Label_Parser - Parse user-provided labels into (type, label) pairs
# Mirrors Link__Service.parse_label() logic
# ═══════════════════════════════════════════════════════════════════════════════

from typing                                                                     import Optional, Tuple

from issues_fs.schemas.graph.Safe_Str__Graph_Types                              import Safe_Str__Node_Type
from issues_fs.schemas.graph.Safe_Str__Graph_Types                              import Safe_Str__Node_Label


class CLI__Label_Parser:                                                         # Label parsing utilities

    @staticmethod
    def parse_type(label: str) -> Optional[Safe_Str__Node_Type]:                 # Extract type from label
        if '-' not in label:                                                     # "Bug-27" → "bug"
            return None
        parts = label.split('-', 1)
        if len(parts) != 2:
            return None
        try:
            return Safe_Str__Node_Type(parts[0].lower())
        except Exception:
            return None

    @staticmethod
    def parse_label(label: str) -> Optional[Safe_Str__Node_Label]:               # Validate and wrap label
        if '-' not in label:
            return None
        try:
            return Safe_Str__Node_Label(label)
        except Exception:
            return None

    @staticmethod
    def parse(label: str) -> Tuple[Optional[Safe_Str__Node_Type],                # Parse both type and label
                                   Optional[Safe_Str__Node_Label]]:
        node_type  = CLI__Label_Parser.parse_type(label)
        node_label = CLI__Label_Parser.parse_label(label)
        return (node_type, node_label)

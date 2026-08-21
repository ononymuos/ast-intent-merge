import gc
import libcst as cst
from typing import Dict, Any, Optional

class SemanticBlockExtractor(cst.CSTVisitor):
    """
    Visits a CST and extracts distinct semantic blocks:
    classes, functions, module-level variables, imports, and docstrings.
    """
    def __init__(self):
        super().__init__()
        self.blocks = {
            "classes": {},
            "functions": {},
            "imports": [],
            "module_vars": {},
            "docstrings": []
        }
        self.current_context = []

    def visit_ClassDef(self, node: cst.ClassDef) -> Optional[bool]:
        name = node.name.value
        context = ".".join(self.current_context + [name])
        self.blocks["classes"][context] = node
        self.current_context.append(name)
        return True

    def leave_ClassDef(self, original_node: cst.ClassDef) -> None:
        self.current_context.pop()

    def visit_FunctionDef(self, node: cst.FunctionDef) -> Optional[bool]:
        name = node.name.value
        context = ".".join(self.current_context + [name])
        self.blocks["functions"][context] = node
        # Optional: could append to context and recurse to get nested functions,
        # but for semantic merge drivers, top-level/class-level is typically enough.
        return False

    def visit_Import(self, node: cst.Import) -> Optional[bool]:
        self.blocks["imports"].append(node)
        return False

    def visit_ImportFrom(self, node: cst.ImportFrom) -> Optional[bool]:
        self.blocks["imports"].append(node)
        return False

    def visit_Assign(self, node: cst.Assign) -> Optional[bool]:
        if not self.current_context:  # Module-level variable
            for target in node.targets:
                if isinstance(target.target, cst.Name):
                    self.blocks["module_vars"][target.target.value] = node
        return False

    def visit_Expr(self, node: cst.Expr) -> Optional[bool]:
        # Naive docstring extraction: string expressions
        if isinstance(node.value, cst.SimpleString):
            self.blocks["docstrings"].append(node)
        return False


def parse_and_extract(source_code: str) -> Dict[str, Any]:
    """
    Parses a Python source file into a libcst syntax tree, preserving formatting.
    Extracts and identifies distinct semantic blocks.
    Runs explicit garbage collection after parsing.
    """
    try:
        module = cst.parse_module(source_code)
        extractor = SemanticBlockExtractor()
        module.visit(extractor)
        
        return {
            "module": module,
            "blocks": extractor.blocks
        }
    finally:
        # CRITICAL CONSTRAINT: Explicitly collect garbage to comply with RAM limits
        gc.collect()


def compare_nodes(node_a: cst.CSTNode, node_b: cst.CSTNode) -> bool:
    """
    Provide a way to compare nodes to detect if changes overlap structurally.
    Returns True if both nodes are structurally identical.
    """
    return node_a.deep_equals(node_b)

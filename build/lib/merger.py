import gc
import libcst as cst
from parser import compare_nodes

class SemanticMerger(cst.CSTTransformer):
    """
    Traverses the ancestor CST and intelligently replaces nodes that were modified
    in either 'ours' or 'theirs'. Detects logical collisions if both modified the same node differently.
    """
    def __init__(self, anc_blocks, our_blocks, thr_blocks):
        self.anc_blocks = anc_blocks
        self.our_blocks = our_blocks
        self.thr_blocks = thr_blocks
        self.current_context = []
        self.conflict_detected = False

    def handle_node(self, node, btype, context):
        if self.conflict_detected:
            return node
            
        anc_node = self.anc_blocks.get(btype, {}).get(context)
        our_node = self.our_blocks.get(btype, {}).get(context)
        thr_node = self.thr_blocks.get(btype, {}).get(context)

        def changed(n1, n2):
            if n1 is None and n2 is None: return False
            if n1 is None or n2 is None: return True
            return not compare_nodes(n1, n2)

        our_changed = changed(anc_node, our_node)
        thr_changed = changed(anc_node, thr_node)

        # If both changed the block relative to ancestor, check if they match
        if our_changed and thr_changed:
            if changed(our_node, thr_node):
                self.conflict_detected = True
                return node

        if our_changed:
            return our_node if our_node is not None else cst.RemoveFromParent()
        if thr_changed:
            return thr_node if thr_node is not None else cst.RemoveFromParent()
        return node

    def visit_ClassDef(self, node: cst.ClassDef):
        self.current_context.append(node.name.value)
        return True

    def leave_ClassDef(self, original_node: cst.ClassDef, updated_node: cst.ClassDef):
        context = ".".join(self.current_context)
        res = self.handle_node(updated_node, "classes", context)
        self.current_context.pop()
        return res

    def visit_FunctionDef(self, node: cst.FunctionDef):
        self.current_context.append(node.name.value)
        return False

    def leave_FunctionDef(self, original_node: cst.FunctionDef, updated_node: cst.FunctionDef):
        context = ".".join(self.current_context)
        res = self.handle_node(updated_node, "functions", context)
        self.current_context.pop()
        return res
        
    def leave_Assign(self, original_node: cst.Assign, updated_node: cst.Assign):
        if not self.current_context: # Module level variable
            for target in original_node.targets:
                if isinstance(target.target, cst.Name):
                    return self.handle_node(updated_node, "module_vars", target.target.value)
        return updated_node

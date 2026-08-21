import gc
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ast_intent_merge.parser import parse_and_extract
from ast_intent_merge.merger import SemanticMerger

def test_semantic_merger_no_conflict():
    anc_code = "def a():\n    pass\ndef b():\n    pass\n"
    our_code = "def a():\n    return 1\ndef b():\n    pass\n"
    thr_code = "def a():\n    pass\ndef b():\n    return 2\n"
    
    anc = parse_and_extract(anc_code)
    ours = parse_and_extract(our_code)
    theirs = parse_and_extract(thr_code)
    
    merger = SemanticMerger(anc["blocks"], ours["blocks"], theirs["blocks"])
    merged = anc["module"].visit(merger)
    
    assert not merger.conflict_detected
    assert "return 1" in merged.code
    assert "return 2" in merged.code
    gc.collect()

def test_semantic_merger_conflict():
    anc_code = "def a():\n    pass\n"
    our_code = "def a():\n    return 1\n"
    thr_code = "def a():\n    return 2\n"
    
    anc = parse_and_extract(anc_code)
    ours = parse_and_extract(our_code)
    theirs = parse_and_extract(thr_code)
    
    merger = SemanticMerger(anc["blocks"], ours["blocks"], theirs["blocks"])
    merged = anc["module"].visit(merger)
    
    assert merger.conflict_detected
    gc.collect()

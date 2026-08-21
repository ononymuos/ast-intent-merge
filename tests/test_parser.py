import sys
import os
import gc
import pytest

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from ast_intent_merge.parser import parse_and_extract, compare_nodes

def test_parse_and_extract_classes():
    code = "class MyClass:\n    pass\n"
    result = parse_and_extract(code)
    assert "MyClass" in result["blocks"]["classes"]
    gc.collect()

def test_parse_and_extract_functions():
    code = "def my_func():\n    return 1\n"
    result = parse_and_extract(code)
    assert "my_func" in result["blocks"]["functions"]
    gc.collect()

def test_compare_nodes_identical():
    code = "def my_func():\n    return 1\n"
    result1 = parse_and_extract(code)
    result2 = parse_and_extract(code)
    assert compare_nodes(result1["blocks"]["functions"]["my_func"], result2["blocks"]["functions"]["my_func"])
    gc.collect()

def test_compare_nodes_different():
    code1 = "def my_func():\n    return 1\n"
    code2 = "def my_func():\n    return 2\n"
    result1 = parse_and_extract(code1)
    result2 = parse_and_extract(code2)
    assert not compare_nodes(result1["blocks"]["functions"]["my_func"], result2["blocks"]["functions"]["my_func"])
    gc.collect()

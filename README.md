# AST Intent Merge 🧠 🔀

[![CI](https://github.com/ononymuos/ast-intent-merge/actions/workflows/ci.yml/badge.svg)](https://github.com/ononymuos/ast-intent-merge/actions)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A custom, zero-config Git merge driver specifically for Python that understands **semantic intent**.

Standard `git merge` relies on line-based diffing. If two developers modify adjacent lines with logically compatible intents (e.g., adding a decorator vs. changing a docstring), Git throws a conflict. `ast-intent-merge` eliminates these bottlenecks by analyzing the Concrete Syntax Tree (CST) and surgically merging the code.

## Features ✨
- **True Semantic Understanding**: Merges changes at the function, class, and variable level instead of raw text.
- **Formatting Preserved**: Uses `libcst` to retain exact original code formatting.
- **Zero-Exhaustion Architecture**: Designed for lightweight execution with strict `gc.collect()` memory management (sub-2GB RAM limits guaranteed).
- **Graceful Fallback**: Instantly falls back to standard `git merge` if it detects a true logical collision.

## Installation 🚀

### 1. Install the tool
```bash
pip install .
```

### 2. Configure Git Hooks
Run the built-in CLI to register the semantic driver in your local Git configuration:
```bash
ast-intent-merge install
```
This seamlessly updates your `.git/config` and `.gitattributes` to route all `*.py` files through the AST merger. Use `--global` to install it across all your repositories.

## How it Works ⚙️
1. Git passes the Ancestor, Ours, and Theirs file versions to the driver.
2. The driver parses all three versions into syntax trees.
3. Distinct semantic blocks are isolated and compared.
4. If modifications are non-overlapping, the trees are cleanly spliced and merged.
5. The merged output is dynamically written, bypassing the manual conflict resolution screen entirely!

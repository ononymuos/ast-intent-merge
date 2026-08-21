#!/usr/bin/env bash

# Configure custom merge driver named ast-intent
git config merge.ast-intent.name "AST Semantic Merge"
git config merge.ast-intent.driver "/home/ubuntu/ast-intent-merge/venv/bin/python src/merge_driver.py %O %A %B"

# Route Python files to this driver
echo "*.py merge=ast-intent" >> .gitattributes

# Secure setup script
chmod +x setup_driver.sh src/merge_driver.py

#!/usr/bin/env bash
set -e

echo "=== Setting up realistic standard Git conflict scenario ==="
mkdir -p /tmp/demo_project
cd /tmp/demo_project
rm -rf .git
git init -q

# Ensure we have our tool installed in a local environment
python3 -m venv venv
source venv/bin/activate
pip install --quiet /home/ubuntu/ast-intent-merge

# Enable our merge driver!
ast-intent-merge install

# Create a Python file where classes are strictly adjacent.
# Standard Git line-based merge WILL conflict here if both are edited.
cat << 'EOF' > math_utils.py
class Add:
    def run(self, a, b):
        return a + b
class Sub:
    def run(self, a, b):
        return a - b
EOF
git add math_utils.py .gitattributes
git commit -q -m "Initial commit"

# Feature Branch 1: Modify Add class
git checkout -q -b feature-add
cat << 'EOF' > math_utils.py
class Add:
    """Handles Addition"""
    def run(self, a, b):
        return a + b
class Sub:
    def run(self, a, b):
        return a - b
EOF
git commit -q -am "docs: added docstring to Add class"

# Feature Branch 2: Modify Sub class
git checkout -q master
git checkout -q -b feature-sub
cat << 'EOF' > math_utils.py
class Add:
    def run(self, a, b):
        return a + b
class Sub:
    """Handles Subtraction"""
    def run(self, a, b):
        return a - b
EOF
git commit -q -am "docs: added docstring to Sub class"

echo ""
echo "=== Triggering Merge (Feature Add into Feature Sub) ==="
# Now we merge. Standard git would cry about adjacent lines. Ours will parse the CST.
git merge feature-add

echo ""
echo "=== Resulting math_utils.py ==="
cat math_utils.py

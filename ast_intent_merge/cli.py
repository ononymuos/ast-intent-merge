import argparse
import sys
import subprocess
from pathlib import Path
import os
import gc

# Add src to path

from ast_intent_merge.parser import parse_and_extract
from ast_intent_merge.merger import SemanticMerger

def install_driver(global_install=False):
    scope = "--global" if global_install else "--local"
    try:
        subprocess.run(["git", "config", scope, "merge.ast-intent.name", "AST Semantic Merge"], check=True)
        subprocess.run(["git", "config", scope, "merge.ast-intent.driver", "ast-intent-merge merge %O %A %B"], check=True)
        print(f"Successfully installed git config ({scope}).")
        
        if not global_install:
            attr_path = Path(".gitattributes")
            mode = "a" if attr_path.exists() else "w"
            with open(attr_path, mode) as f:
                f.write("\n*.py merge=ast-intent\n")
            print("Successfully updated .gitattributes in the local repository.")
            
    except subprocess.CalledProcessError as e:
        print(f"Failed to configure git: {e}")
        sys.exit(1)

def run_merge(ancestor_path, ours_path, theirs_path):
    with open(ancestor_path, 'r') as f: anc_code = f.read()
    with open(ours_path, 'r') as f: ours_code = f.read()
    with open(theirs_path, 'r') as f: theirs_code = f.read()
    
    try:
        anc = parse_and_extract(anc_code)
        ours = parse_and_extract(ours_code)
        theirs = parse_and_extract(theirs_code)
    except Exception as e:
        print(f"AST Parsing failed: {e}")
        gc.collect()
        sys.exit(1) # fallback to normal git merge
        
    merger = SemanticMerger(anc["blocks"], ours["blocks"], theirs["blocks"])
    merged_module = anc["module"].visit(merger)
    
    if merger.conflict_detected:
        print("Semantic conflict detected! Falling back to standard git merge.")
        gc.collect()
        sys.exit(1)
        
    with open(ours_path, 'w') as f:
        f.write(merged_module.code)
        
    print("AST Intent Merge successful! Seamlessly combined distinct semantic blocks.")
    gc.collect()
    sys.exit(0)

def main():
    parser = argparse.ArgumentParser(description="AST-Intent-Merge: Semantic Git Merge Driver for Python")
    subparsers = parser.add_subparsers(dest="command", required=True)
    
    install_parser = subparsers.add_parser("install", help="Install the merge driver in git config")
    install_parser.add_argument("--global", action="store_true", dest="is_global", help="Install globally")
    
    merge_parser = subparsers.add_parser("merge", help="Execute the merge logic (used by git)")
    merge_parser.add_argument("ancestor", help="Ancestor file path")
    merge_parser.add_argument("ours", help="Ours file path")
    merge_parser.add_argument("theirs", help="Theirs file path")
    
    args = parser.parse_args()
    
    if args.command == "install":
        install_driver(args.is_global)
    elif args.command == "merge":
        run_merge(args.ancestor, args.ours, args.theirs)

if __name__ == "__main__":
    main()

import sys
import os
import gc
import libcst as cst

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parser import parse_and_extract
from merger import SemanticMerger

def main():
    if len(sys.argv) < 4:
        print("Usage: merge_driver.py <ancestor> <ours> <theirs>")
        sys.exit(1)
        
    ancestor_path = sys.argv[1]
    ours_path = sys.argv[2]
    theirs_path = sys.argv[3]
    
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
        sys.exit(1)
        
    merger = SemanticMerger(anc["blocks"], ours["blocks"], theirs["blocks"])
    merged_module = anc["module"].visit(merger)
    
    if merger.conflict_detected:
        print("Semantic conflict detected! Falling back to standard git merge.")
        gc.collect()
        sys.exit(1)
        
    # Write merged code to 'ours' path which Git uses for the resolution
    with open(ours_path, 'w') as f:
        f.write(merged_module.code)
        
    print("AST Intent Merge successful! Seamlessly combined distinct semantic blocks.")
    gc.collect()
    sys.exit(0)

if __name__ == "__main__":
    main()

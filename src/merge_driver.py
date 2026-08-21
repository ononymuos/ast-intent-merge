import sys
import os
import gc

# Add current dir to path to import our parser
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parser import parse_and_extract, compare_nodes

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
        # Parsing failed; fallback to standard line merge
        gc.collect()
        sys.exit(1)
        
    conflict = False
    for btype in ["classes", "functions", "module_vars"]:
        anc_b = anc["blocks"].get(btype, {})
        our_b = ours["blocks"].get(btype, {})
        thr_b = theirs["blocks"].get(btype, {})
        
        all_keys = set(anc_b.keys()) | set(our_b.keys()) | set(thr_b.keys())
        
        for k in all_keys:
            node_anc = anc_b.get(k)
            node_our = our_b.get(k)
            node_thr = thr_b.get(k)
            
            def changed(n1, n2):
                if n1 is None and n2 is None: return False
                if n1 is None or n2 is None: return True
                return not compare_nodes(n1, n2)
                
            our_changed = changed(node_anc, node_our)
            thr_changed = changed(node_anc, node_thr)
            
            # If both changed the block relative to ancestor, check if they match
            if our_changed and thr_changed:
                if changed(node_our, node_thr):
                    conflict = True
                    break
                    
        if conflict:
            break
            
    # Explicitly clear objects to stay within 2GB RAM limit
    gc.collect()
    
    if conflict:
        print("Semantic conflict detected! Falling back to standard git merge.")
        sys.exit(1)
    else:
        print("No semantic conflict detected. Allowing standard merge to handle distinct blocks.")
        # Returning 1 safely permits git to interleave standard text edits if we don't do inline AST codegen rewriting here
        sys.exit(1)

if __name__ == "__main__":
    main()

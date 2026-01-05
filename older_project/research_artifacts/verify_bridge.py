#!/usr/bin/env python3
"""Sovereign Bridge: Verification Harness"""
import kuzu

DB_PATH = 'kuzu_db'

def run_verification():
    print("="*60)
    print("SOVEREIGN BRIDGE VERIFICATION HARNESS")
    print("="*60)
    
    db = kuzu.Database(DB_PATH)
    conn = kuzu.Connection(db)
    
    checks = []
    
    # --- Layer 2: Data Integrity ---
    print("\n[LAYER 2: DATA INTEGRITY]")
    
    # Concept Count
    res = conn.execute('MATCH (c:Concept) RETURN count(c) AS cnt')
    concept_cnt = res.get_next()[0] if res.has_next() else 0
    print(f"  Concept Nodes: {concept_cnt}")
    checks.append(('Concept Count > 100', concept_cnt > 100))
    
    # Symbol Count
    res = conn.execute('MATCH (s:Symbol) RETURN count(s) AS cnt')
    symbol_cnt = res.get_next()[0] if res.has_next() else 0
    print(f"  Symbol Nodes: {symbol_cnt}")
    checks.append(('Symbol Count > 0', symbol_cnt > 0))
    
    # Edge Count
    res = conn.execute('MATCH ()-[r:IMPLEMENTS]->() RETURN count(r) AS cnt')
    edge_cnt = res.get_next()[0] if res.has_next() else 0
    print(f"  IMPLEMENTS Edges: {edge_cnt}")
    checks.append(('IMPLEMENTS Edges >= 2', edge_cnt >= 2))
    
    # --- Layer 3: Functional Logic ---
    print("\n[LAYER 3: FUNCTIONAL LOGIC]")
    
    # Specific Link Test
    res = conn.execute("MATCH (c:Concept)-[:IMPLEMENTS]->(s:Symbol) WHERE c.name = 'Context Window Limit Recovery' RETURN s.name, s.file_path")
    if res.has_next():
        row = res.get_next()
        print(f"  Query 'Context Window...' -> Symbol: {row[0]}, File: {row[1]}")
        checks.append(('Context Window Link Exists', True))
    else:
        print(f"  Query 'Context Window...' -> NOT FOUND")
        checks.append(('Context Window Link Exists', False))

    # Sample Concepts (for sanity)
    print("\n[SAMPLE DATA: Top 5 Concepts]")
    res = conn.execute('MATCH (c:Concept) RETURN c.name LIMIT 5')
    while res.has_next():
        print(f"    - {res.get_next()[0]}")
        
    # Sample Symbols (for sanity)
    print("\n[SAMPLE DATA: Top 5 Symbols]")
    res = conn.execute('MATCH (s:Symbol) RETURN s.name, s.file_path LIMIT 5')
    while res.has_next():
        row = res.get_next()
        print(f"    - {row[0]} @ {row[1]}")

    # --- Summary ---
    print("\n" + "="*60)
    print("VERIFICATION SUMMARY")
    print("="*60)
    passed = sum(1 for _, v in checks if v)
    failed = len(checks) - passed
    for name, status in checks:
        mark = "✅ PASS" if status else "❌ FAIL"
        print(f"  [{mark}] {name}")
    
    print(f"\nTotal: {passed}/{len(checks)} Passed, {failed} Failed.")
    
    if failed == 0:
        print("\n🎉 ALL CHECKS PASSED. SYSTEM IS ROBUST.")
    else:
        print("\n⚠️  SOME CHECKS FAILED. REVIEW REQUIRED.")
    
    return failed == 0

if __name__ == '__main__':
    run_verification()

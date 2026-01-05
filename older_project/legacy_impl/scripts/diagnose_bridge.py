#!/usr/bin/env python3
"""
Sovereign Bridge: Diagnostic Gap Analysis
Identifies weak spots, orphan concepts, and potential false positives.
"""
import kuzu
import os

DB_PATH = os.path.expanduser('~/sovereign_platform/data/kuzu_db')

def run_diagnostics():
    print("="*60)
    print("SOVEREIGN BRIDGE: DIAGNOSTIC REPORT")
    print("="*60)
    
    db = kuzu.Database(DB_PATH)
    conn = kuzu.Connection(db)
    
    # 1. ORPHAN CONCEPTS (Docs with no Code)
    # These represent "Hallucinated Hallucinations" - docs checking writing prompts that code hasn't filled, 
    # or simple naming mismatches.
    res = conn.execute('''
        MATCH (c:Concept)
        WHERE NOT (c)-[:IMPLEMENTS]->(:Symbol)
        RETURN count(c)
    ''')
    orphan_concepts = res.get_next()[0]
    
    print(f"\n[?] ORPHAN CONCEPTS (Doc -> X -> Code): {orphan_concepts}")
    if orphan_concepts > 0:
        print("    Sample of Unlinked Concepts:")
        res = conn.execute('''
            MATCH (c:Concept)
            WHERE NOT (c)-[:IMPLEMENTS]->(:Symbol)
            RETURN c.name
            LIMIT 10
        ''')
        while res.has_next():
            print(f"    - {res.get_next()[0]}")

    # 2. ORPHAN SYMBOLS (Code with no Docs)
    # This represents "Dark Code" - undocumented logic.
    res = conn.execute('''
        MATCH (s:Symbol)
        WHERE NOT (:Concept)-[:IMPLEMENTS]->(s)
        RETURN count(s)
    ''')
    orphan_symbols = res.get_next()[0]
    
    print(f"\n[?] DARK CODE (Code -> X -> Doc): {orphan_symbols}")
    
    # 3. LINK DENSITY
    # Are we linking 1:1 or 1:Many? 
    # High fan-out might indicate generic concepts like "Error" linking to every error class.
    res = conn.execute('''
        MATCH (c:Concept)-[:IMPLEMENTS]->(s:Symbol)
        RETURN c.name, count(s) as fanout
        ORDER BY fanout DESC
        LIMIT 5
    ''')
    print("\n[?] HIGH FAN-OUT CONCEPTS (Potential False Positives):")
    while res.has_next():
        row = res.get_next()
        print(f"    - '{row[0]}' links to {row[1]} symbols")

    # 4. NAME COLLISION RISK
    # Check for short acronyms that usually cause false links (e.g., 'ID', 'Log')
    risky_terms = ['ID', 'LOG', 'USER', 'AUTH']
    print("\n[?] RISKY TERM CHECK:")
    for term in risky_terms:
        res = conn.execute(f'''
            MATCH (c:Concept)-[:IMPLEMENTS]->(s:Symbol)
            WHERE c.name = '{term}' OR c.name = '{term.title()}'
            RETURN count(s)
        ''')
        cnt = res.get_next()[0]
        print(f"    - '{term}': {cnt} links")

if __name__ == '__main__':
    run_diagnostics()

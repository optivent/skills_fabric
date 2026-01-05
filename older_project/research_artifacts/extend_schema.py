#!/usr/bin/env python3
"""
Extend KuzuDB Schema for Sovereign Platform Integration
Adds Skill nodes and relationships for ULTRATHINK Factory integration.
"""
import kuzu
import os

DB_PATH = os.path.expanduser('~/sovereign_platform/data/kuzu_db')

def extend_schema():
    print("="*60)
    print("SOVEREIGN PLATFORM: SCHEMA EXTENSION")
    print("="*60)
    
    db = kuzu.Database(DB_PATH)
    conn = kuzu.Connection(db)
    
    # Add Skill node table
    try:
        conn.execute('''
            CREATE NODE TABLE Skill(
                id STRING,
                question STRING,
                code STRING,
                source_url STRING,
                library STRING,
                verified BOOLEAN,
                PRIMARY KEY (id)
            )
        ''')
        print("[+] Created Skill node table")
    except RuntimeError as e:
        if "already exists" in str(e):
            print("[.] Skill table already exists")
        else:
            print(f"[!] Error creating Skill table: {e}")
    
    # Add TestResult node table
    try:
        conn.execute('''
            CREATE NODE TABLE TestResult(
                id STRING,
                exit_code INT64,
                stdout STRING,
                timestamp STRING,
                PRIMARY KEY (id)
            )
        ''')
        print("[+] Created TestResult node table")
    except RuntimeError as e:
        if "already exists" in str(e):
            print("[.] TestResult table already exists")
        else:
            print(f"[!] Error creating TestResult table: {e}")
    
    # Add TEACHES relationship (Skill -> Concept)
    try:
        conn.execute('CREATE REL TABLE TEACHES(FROM Skill TO Concept)')
        print("[+] Created TEACHES relationship")
    except RuntimeError as e:
        if "already exists" in str(e):
            print("[.] TEACHES relationship already exists")
        else:
            print(f"[!] Error creating TEACHES: {e}")
    
    # Add USES relationship (Skill -> Symbol)
    try:
        conn.execute('CREATE REL TABLE USES(FROM Skill TO Symbol)')
        print("[+] Created USES relationship")
    except RuntimeError as e:
        if "already exists" in str(e):
            print("[.] USES relationship already exists")
        else:
            print(f"[!] Error creating USES: {e}")
    
    # Add VERIFIED_BY relationship (Skill -> TestResult)
    try:
        conn.execute('CREATE REL TABLE VERIFIED_BY(FROM Skill TO TestResult)')
        print("[+] Created VERIFIED_BY relationship")
    except RuntimeError as e:
        if "already exists" in str(e):
            print("[.] VERIFIED_BY relationship already exists")
        else:
            print(f"[!] Error creating VERIFIED_BY: {e}")
    
    # Verify schema
    print("\n" + "="*60)
    print("SCHEMA VERIFICATION")
    print("="*60)
    
    tables = ['Concept', 'Symbol', 'Skill', 'TestResult']
    for table in tables:
        try:
            res = conn.execute(f'MATCH (n:{table}) RETURN count(n)')
            count = res.get_next()[0] if res.has_next() else 0
            print(f"  {table}: {count} nodes")
        except Exception as e:
            print(f"  {table}: ERROR - {e}")
    
    print("\n✅ Schema extension complete!")

if __name__ == '__main__':
    extend_schema()

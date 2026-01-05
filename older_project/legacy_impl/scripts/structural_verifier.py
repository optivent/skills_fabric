#!/usr/bin/env python3
"""
Sovereign Verification Protocol - Phase 1: Structural Proof (FIXED)
Extracts GitHub file paths from docs and verifies they exist in the repo.
Creates PROVEN links with 100% accuracy.
"""
import kuzu
import os
import re
import glob

DB_PATH = os.path.expanduser('~/sovereign_platform/data/kuzu_db')
DOCS_DIR = os.path.expanduser('~/sovereign_platform/data/codewiki')
REPO_DIR = os.path.expanduser('~/sovereign_platform/data/oh-my-opencode')

# Pattern to extract file paths from GitHub URLs (handles ?plain=1 and #L123)
GITHUB_PATH_PATTERN = re.compile(
    r'https://github\.com/[^/]+/[^/]+/blob/[^/]+/([^\s\)#?\]]+)'
)

class StructuralVerifierV2:
    def __init__(self):
        self.db = kuzu.Database(DB_PATH)
        self.conn = kuzu.Connection(self.db)
        
    def extract_file_paths(self, doc_text: str) -> set[str]:
        """Extract unique file paths from GitHub URLs in doc."""
        matches = GITHUB_PATH_PATTERN.findall(doc_text)
        # Clean paths - remove any trailing garbage
        cleaned = set()
        for m in matches:
            # Remove common suffixes that aren't part of path
            path = m.split('?')[0].split('#')[0]
            if path and not path.endswith('/'):
                cleaned.add(path)
        return cleaned
    
    def verify_and_link(self):
        """Main verification loop."""
        print("="*60)
        print("SOVEREIGN VERIFICATION PROTOCOL V2")
        print("="*60)
        
        # Get all doc files
        doc_files = glob.glob(os.path.join(DOCS_DIR, '*.md'))
        print(f"\n[+] Processing {len(doc_files)} documents")
        
        # Track unique file-to-concept mappings
        verified_files = {}  # file_path -> [doc_names]
        
        for doc_path in doc_files:
            with open(doc_path, 'r', encoding='utf-8') as f:
                doc_text = f.read()
            
            doc_name = os.path.basename(doc_path).replace('.md', '')
            
            # Extract file paths
            paths = self.extract_file_paths(doc_text)
            
            for file_path in paths:
                # Verify file exists in repo
                local_path = os.path.join(REPO_DIR, file_path)
                if os.path.exists(local_path):
                    if file_path not in verified_files:
                        verified_files[file_path] = []
                    verified_files[file_path].append(doc_name)
        
        print(f"[+] Found {len(verified_files)} unique verified files")
        
        # Now create nodes and links
        symbols_created = 0
        links_created = 0
        
        for file_path, doc_names in verified_files.items():
            # Create Symbol node for this file
            symbol_name = os.path.basename(file_path)
            try:
                self.conn.execute('''
                    MERGE (s:Symbol {name: $name, file_path: $path, line: 0, kind: 'verified_file'})
                ''', {'name': symbol_name, 'path': file_path})
                symbols_created += 1
            except Exception as e:
                pass  # Symbol may already exist
            
            # Create PROVEN link from each doc that references this file
            for doc_name in doc_names:
                # Ensure concept exists
                try:
                    self.conn.execute('''
                        MERGE (c:Concept {name: $name, content: 'Documentation section'})
                    ''', {'name': doc_name})
                except: pass
                
                # Create PROVEN link
                try:
                    self.conn.execute('''
                        MATCH (c:Concept {name: $cname}), (s:Symbol {file_path: $path})
                        MERGE (c)-[:PROVEN {proof_type: 'FILE_EXISTS'}]->(s)
                    ''', {'cname': doc_name, 'path': file_path})
                    links_created += 1
                except Exception as e:
                    pass
        
        print(f"[+] Created {symbols_created} Symbol nodes")
        print(f"[+] Created {links_created} PROVEN links")
        
        # Verify counts in graph
        res = self.conn.execute('MATCH (s:Symbol) RETURN count(s)')
        print(f"\n[GRAPH STATE]")
        print(f"  Total Symbols: {res.get_next()[0]}")
        
        res = self.conn.execute('MATCH ()-[r:PROVEN]->() RETURN count(r)')
        print(f"  Total PROVEN links: {res.get_next()[0]}")
        
        res = self.conn.execute('MATCH (c:Concept)-[:PROVEN]->() RETURN count(DISTINCT c)')
        print(f"  Concepts with PROVEN links: {res.get_next()[0]}")

if __name__ == '__main__':
    verifier = StructuralVerifierV2()
    verifier.verify_and_link()

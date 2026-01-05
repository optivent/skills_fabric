
import os
import glob
import kuzu
import re

# GLiNER Import
try:
    from gliner import GLiNER
    HAS_GLINER = True
except ImportError:
    HAS_GLINER = False
    print("[!] GLiNER not found. Semantic extraction disabled.")

# SCIP Protobuf Import
try:
    import scip_pb2
    HAS_SCIP = True
except ImportError:
    HAS_SCIP = False
    print("[!] scip_pb2 not found. Code Compass disabled.")

# Configuration
DB_PATH = 'kuzu_db'
DOCS_DIR = 'ingest_output'
SCIP_INDEX = 'oh-my-opencode/index.scip'

class SovereignBridge:
    def __init__(self):
        self.db = kuzu.Database(DB_PATH)
        self.conn = kuzu.Connection(self.db)
        self._init_schema()

        if HAS_GLINER:
            print("[+] Loading GLiNER model (urchade/gliner_small-v2.1)...")
            self.ner_model = GLiNER.from_pretrained("urchade/gliner_small-v2.1")
        
    def _init_schema(self):
        try:
            self.conn.execute('CREATE NODE TABLE Concept(name STRING, content STRING, PRIMARY KEY (name))')
            self.conn.execute('CREATE NODE TABLE Symbol(name STRING, file_path STRING, line INT64, kind STRING, PRIMARY KEY (name))')
            self.conn.execute('CREATE REL TABLE IMPLEMENTS(FROM Concept TO Symbol)')
            print('[+] Schema Initialized.')
        except RuntimeError:
            print('[.] Schema already exists.')

    def ingest_concepts(self):
        print(f'[+] Ingesting Docs from {DOCS_DIR}...')
        files = glob.glob(os.path.join(DOCS_DIR, '*.md'))
        print(f'    Found {len(files)} files.')
        
        for fpath in files:
            with open(fpath, 'r', encoding='utf-8') as f:
                text = f.read()
            fname = os.path.basename(fpath).replace('.md', '')

            # 1. Ingest Document Title
            try:
                self.conn.execute('MERGE (c:Concept {name: $name, content: $content})', 
                                  {'name': fname, 'content': text[:200]})
            except: pass

            # 2. GLiNER Extraction
            if HAS_GLINER:
                labels = ["Software Concept", "System Component", "Algorithm", "Limit", "Hook", "Class", "Function"]
                entities = self.ner_model.predict_entities(text[:2000], labels)
                
                for ent in entities:
                    ent_text = ent["text"].strip()
                    if len(ent_text) > 3:
                        try:
                            self.conn.execute('MERGE (c:Concept {name: $name, content: $content})',
                                              {'name': ent_text, 'content': f"Extracted from {fname}"})
                        except: pass

    def ingest_symbols_scip(self):
        if not HAS_SCIP:
            print("[!] Skipping SCIP Ingestion (Missing Protobuf Bindings)")
            return

        print(f'[+] Ingesting Real SCIP Index from {SCIP_INDEX}...')
        index = scip_pb2.Index()
        
        try:
            with open(SCIP_INDEX, "rb") as f:
                index.ParseFromString(f.read())
        except Exception as e:
            print(f"[!] Failed to parse SCIP index: {e}")
            return

        print(f"    Index Metadata: {index.metadata.tool_info.name} {index.metadata.tool_info.version}")
        print(f"    Documents: {len(index.documents)}")
        
        cnt = 0
        for doc in index.documents:
            file_path = doc.relative_path
            
            # Simple heuristic: Only ingest "Definitions" (Symbol Roles)
            # Not strictly checking roles bitmask for speed, relying on occurence context if available
            # Or better: Extract symbols from 'symbols' table if present, or occurrences
            
            # Strategy: Iterate distinct symbols defined in this document
            # SCIP 0.2+ usually lists symbols in doc.symbols
            
            for symbol_info in doc.symbols:
                sym_name = symbol_info.symbol
                # Clean name (SCIP names are long: 'scip-python npm name ...')
                # We need a robust heuristic to get the "Short Name"
                # e.g. '.../MyClass#' -> MyClass
                
                short_name = self._parse_scip_name(sym_name)
                if not short_name: continue
                
                # Find definition line from occurrences (optional, perf hit)
                # For PoC, we just node it up
                
                try:
                    self.conn.execute('MERGE (s:Symbol {name: $name, file_path: $path, line: $line, kind: $kind})',
                                      {'name': short_name, 
                                       'path': file_path, 
                                       'line': 0, # Placeholder
                                       'kind': 'scip_symbol'})
                    cnt += 1
                except: pass
                
        print(f"[+] Ingested {cnt} Symbols from SCIP Index.")

    def _parse_scip_name(self, scip_name):
        # SCIP symbol format: scheme manager package version descriptor
        # e.g. rogram-name package-name version descriptor
        # descriptor: `name` or `name.` or `name#` or `name()`
        
        # Heuristic: Take the last segment
        parts = scip_name.split('/')
        if not parts: return None
        last = parts[-1]
        
        # Strip suffix sigils
        last = last.replace('#', '').replace('.', '').replace('()', '').replace(':', '')
        # If it contains backticks (method names), strip them
        last = last.replace('`', '')
        
        if len(last) > 2:
            return last
        return None

    def build_bridge(self):
        print('[+] Building Semantic Bridge (Python Fuzzy Logic)...')
        
        res = self.conn.execute('MATCH (c:Concept) RETURN c.name')
        concepts = []
        while res.has_next():
            concepts.append(res.get_next()[0])

        res = self.conn.execute('MATCH (s:Symbol) RETURN s.name')
        symbols = {}
        while res.has_next():
            name = res.get_next()[0]
            symbols[name.upper()] = name

        cnt = 0
        for c_name in concepts:
            c_norm = c_name.upper().replace(' ', '').replace('-', '').replace('_', '')
            if c_norm in symbols:
                target_sym = symbols[c_norm]
                try:
                    self.conn.execute('MATCH (c:Concept), (s:Symbol) WHERE c.name = $c_name AND s.name = $s_name MERGE (c)-[:IMPLEMENTS]->(s)',
                                      {'c_name': c_name, 's_name': target_sym})
                    print(f'    [LINK] Concept("{c_name}") -> Symbol("{target_sym}")')
                    cnt += 1
                except: pass
                
        print(f'[+] Bridge Built. {cnt} links created.')

    def query_test(self):
        # Specific regression test for the user's focus
        print('[?] Querying Bridge...')
        res = self.conn.execute('MATCH (c:Concept)-[:IMPLEMENTS]->(s:Symbol) RETURN c.name, s.name, s.file_path')
        found = False
        while res.has_next():
            found = True
            row = res.get_next()
            # print(f'    [VERIFIED LINK] {row[0]} -> {row[1]} :: {row[2]}') # Verbose
            pass
        
        if found:
            print(f"    [SUCCESS] Verification passed. Links exist.")
        else:
            print('    [!] No links found.')

if __name__ == '__main__':
    bridge = SovereignBridge()
    bridge.ingest_concepts()
    bridge.ingest_symbols_scip()
    bridge.build_bridge()
    bridge.query_test()

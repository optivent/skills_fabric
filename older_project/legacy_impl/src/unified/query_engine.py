#!/usr/bin/env python3
"""
Sovereign Platform: Unified Query Engine
Natural Language -> Graph Query -> Grounded Response
"""
import kuzu
import os
import re

# GLiNER for concept extraction
try:
    from gliner import GLiNER
    HAS_GLINER = True
except ImportError:
    HAS_GLINER = False

DB_PATH = os.path.expanduser('~/sovereign_platform/data/kuzu_db')

class SovereignQueryEngine:
    """Query the unified Sovereign Platform graph with natural language."""
    
    def __init__(self):
        self.db = kuzu.Database(DB_PATH)
        self.conn = kuzu.Connection(self.db)
        
        if HAS_GLINER:
            print("[+] Loading GLiNER model...")
            self.ner = GLiNER.from_pretrained("urchade/gliner_small-v2.1")
        else:
            self.ner = None
            print("[!] GLiNER not available, using keyword extraction")
    
    def extract_concepts(self, query: str) -> list[str]:
        """Extract concepts from natural language query."""
        if self.ner:
            labels = ["Software Concept", "Library", "Function", "Class", "Feature"]
            entities = self.ner.predict_entities(query, labels)
            return [e["text"] for e in entities]
        else:
            # Fallback: simple keyword extraction
            words = re.findall(r'\b[A-Z][a-zA-Z]+\b', query)
            return words
    
    def query(self, question: str) -> dict:
        """
        Query the graph with natural language.
        Returns grounded response with sources.
        """
        print(f"\n[?] Query: {question}")
        
        # Step 1: Extract concepts
        concepts = self.extract_concepts(question)
        print(f"    Extracted concepts: {concepts}")
        
        if not concepts:
            # Try normalized search
            normalized = question.upper().replace(' ', '').replace('-', '').replace('_', '')
            concepts = [question]
        
        # Step 2: Find matching concepts in graph
        results = {
            'query': question,
            'concepts_found': [],
            'symbols_linked': [],
            'skills_available': [],
            'grounded': False
        }
        
        for concept in concepts:
            # Fuzzy search for concept
            c_norm = concept.upper().replace(' ', '').replace('-', '').replace('_', '')
            
            # Search concepts
            res = self.conn.execute('''
                MATCH (c:Concept) 
                RETURN c.name, c.content
            ''')
            
            while res.has_next():
                row = res.get_next()
                c_name = row[0]
                c_name_norm = c_name.upper().replace(' ', '').replace('-', '').replace('_', '')
                
                if c_norm in c_name_norm or c_name_norm in c_norm:
                    results['concepts_found'].append({
                        'name': c_name,
                        'preview': row[1][:100] if row[1] else ''
                    })
                    
                    # Find linked symbols
                    sym_res = self.conn.execute('''
                        MATCH (c:Concept)-[:IMPLEMENTS]->(s:Symbol)
                        WHERE c.name = $name
                        RETURN s.name, s.file_path
                    ''', {'name': c_name})
                    
                    while sym_res.has_next():
                        sym_row = sym_res.get_next()
                        results['symbols_linked'].append({
                            'symbol': sym_row[0],
                            'file': sym_row[1]
                        })
                        results['grounded'] = True
                    
                    # Find related skills
                    skill_res = self.conn.execute('''
                        MATCH (sk:Skill)-[:TEACHES]->(c:Concept)
                        WHERE c.name = $name
                        RETURN sk.question, sk.code, sk.verified
                    ''', {'name': c_name})
                    
                    while skill_res.has_next():
                        skill_row = skill_res.get_next()
                        results['skills_available'].append({
                            'question': skill_row[0],
                            'code': skill_row[1][:200] if skill_row[1] else '',
                            'verified': skill_row[2]
                        })
        
        return results
    
    def format_response(self, results: dict) -> str:
        """Format query results as human-readable response."""
        output = []
        output.append(f"\n{'='*60}")
        output.append(f"SOVEREIGN QUERY RESULT")
        output.append(f"{'='*60}")
        output.append(f"Query: {results['query']}")
        output.append(f"Grounded: {'✅ Yes' if results['grounded'] else '❌ No'}")
        
        if results['concepts_found']:
            output.append(f"\n📚 Concepts Found ({len(results['concepts_found'])}):")
            for c in results['concepts_found'][:5]:  # Limit to 5
                output.append(f"   - {c['name']}")
        
        if results['symbols_linked']:
            output.append(f"\n🔗 Code Symbols:")
            for s in results['symbols_linked']:
                output.append(f"   - {s['symbol']} @ {s['file']}")
        
        if results['skills_available']:
            output.append(f"\n💡 Verified Skills:")
            for sk in results['skills_available'][:3]:  # Limit to 3
                output.append(f"   Q: {sk['question']}")
                output.append(f"   Verified: {'✅' if sk['verified'] else '❌'}")
        
        if not results['grounded']:
            output.append("\n⚠️  No direct code linkage found for this query.")
        
        return '\n'.join(output)

def main():
    engine = SovereignQueryEngine()
    
    # Test queries
    test_queries = [
        "What is Context Window Limit Recovery?",
        "How do I use executeCompact?",
        "Tell me about ChatWindowManager"
    ]
    
    for q in test_queries:
        results = engine.query(q)
        print(engine.format_response(results))
        print()

if __name__ == '__main__':
    main()

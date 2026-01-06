#!/usr/bin/env python3
"""Test full supervisor pipeline on Docling with zero-hallucination verification."""
import sys
from pathlib import Path

src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

import importlib.util

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

# Load required modules directly
ddr_module = load_module("ddr", src_path / "skills_fabric" / "verify" / "ddr.py")
DirectDependencyRetriever = ddr_module.DirectDependencyRetriever
SourceRef = ddr_module.SourceRef


def test_mining_stage():
    """Test Stage 1: Mining symbols from repo."""
    print("\n" + "=" * 60)
    print("STAGE 1: MINING")
    print("=" * 60)

    repo_path = Path("/home/user/skills_fabric/crawl_output/docling_repo/docling")

    # Find Python files
    py_files = list(repo_path.rglob("*.py"))
    py_files = [f for f in py_files if '__pycache__' not in str(f)]

    print(f"Python files found: {len(py_files)}")

    # Extract symbols using simple AST parsing
    import ast

    symbols = []
    for py_file in py_files[:50]:  # Limit for speed
        try:
            content = py_file.read_text(encoding='utf-8', errors='ignore')
            tree = ast.parse(content)

            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    symbols.append({
                        "name": node.name,
                        "type": "class",
                        "file": str(py_file.relative_to(repo_path)),
                        "line": node.lineno
                    })
                elif isinstance(node, ast.FunctionDef):
                    symbols.append({
                        "name": node.name,
                        "type": "function",
                        "file": str(py_file.relative_to(repo_path)),
                        "line": node.lineno
                    })
        except Exception as e:
            continue

    print(f"Symbols extracted: {len(symbols)}")
    print(f"Classes: {sum(1 for s in symbols if s['type'] == 'class')}")
    print(f"Functions: {sum(1 for s in symbols if s['type'] == 'function')}")

    # Sample output
    print("\nSample symbols:")
    for s in symbols[:5]:
        print(f"  {s['name']} ({s['type']}) at {s['file']}:{s['line']}")

    return symbols


def test_linking_stage(symbols: list):
    """Test Stage 2: Linking symbols to CodeWiki concepts."""
    print("\n" + "=" * 60)
    print("STAGE 2: LINKING")
    print("=" * 60)

    codewiki_path = Path("/home/user/skills_fabric/crawl_output/docling")
    ddr = DirectDependencyRetriever(codewiki_path=codewiki_path)
    ddr.load_symbol_catalog(codewiki_path / "symbol_catalog.md")

    # Link mined symbols to DDR-validated entries
    linked = []
    for sym in symbols[:30]:  # Limit for speed
        result = ddr.retrieve(sym['name'], max_results=1)
        if result.validated_count > 0:
            ddr_ref = result.elements[0].source_ref
            linked.append({
                "mined": sym,
                "ddr_match": {
                    "symbol": ddr_ref.symbol_name,
                    "file": ddr_ref.file_path,
                    "line": ddr_ref.line_number,
                    "validated": ddr_ref.validated
                }
            })

    print(f"Symbols linked: {len(linked)}/{len(symbols[:30])}")

    # Show linking results
    print("\nLinked symbols:")
    for l in linked[:5]:
        mined = l['mined']
        ddr = l['ddr_match']
        match = "✓" if ddr['validated'] else "✗"
        print(f"  {match} {mined['name']} -> {ddr['symbol']} at {ddr['file']}:{ddr['line']}")

    return linked


def test_writing_stage(linked: list):
    """Test Stage 3: Writing skill content."""
    print("\n" + "=" * 60)
    print("STAGE 3: WRITING")
    print("=" * 60)

    skills = []
    for item in linked[:10]:  # Write skills for top 10 linked symbols
        sym = item['mined']
        ddr = item['ddr_match']

        # Generate skill content
        skill = {
            "name": sym['name'],
            "type": sym['type'],
            "content": f"""# {sym['name']}

## Summary
The `{sym['name']}` {sym['type']} is part of Docling's document processing pipeline.

## Source Reference
- File: `{ddr['file']}`
- Line: {ddr['line']}

## Usage
```python
from docling import {sym['name']}
```

## Related
- Located in `{sym['file']}`
""",
            "source_ref": SourceRef(
                symbol_name=ddr['symbol'],
                file_path=ddr['file'],
                line_number=ddr['line'],
                symbol_type=sym['type'],
                validated=ddr['validated']
            )
        }
        skills.append(skill)

    print(f"Skills generated: {len(skills)}")
    print("\nSample skill:")
    if skills:
        print(skills[0]['content'][:300] + "...")

    return skills


def test_auditing_stage(skills: list):
    """Test Stage 4: Auditing for zero-hallucination."""
    print("\n" + "=" * 60)
    print("STAGE 4: AUDITING (Zero-Hallucination)")
    print("=" * 60)

    import re
    codewiki_path = Path("/home/user/skills_fabric/crawl_output/docling")
    ddr = DirectDependencyRetriever(codewiki_path=codewiki_path)
    ddr.load_symbol_catalog(codewiki_path / "symbol_catalog.md")

    audited = []
    total_claims = 0
    verified_claims = 0

    for skill in skills:
        content = skill['content']

        # Extract claims (code references in backticks)
        claims = re.findall(r'`([A-Za-z_][A-Za-z0-9_]*)`', content)
        claims = list(set(claims))  # Dedupe

        skill_verified = 0
        skill_total = len(claims)

        for claim in claims:
            result = ddr.retrieve(claim, max_results=1)
            if result.validated_count > 0:
                skill_verified += 1

        total_claims += skill_total
        verified_claims += skill_verified

        if skill_total == 0 or (skill_verified / skill_total) >= 0.98:
            audited.append(skill)

    hall_rate = 1 - (verified_claims / total_claims) if total_claims > 0 else 0

    print(f"Total claims: {total_claims}")
    print(f"Verified claims: {verified_claims}")
    print(f"Hallucination rate: {hall_rate:.4f}")
    print(f"Target (<0.02): {'PASS' if hall_rate < 0.02 else 'FAIL'}")
    print(f"Skills passing audit: {len(audited)}/{len(skills)}")

    return audited, hall_rate


def test_verification_stage(audited: list):
    """Test Stage 5: Trust verification."""
    print("\n" + "=" * 60)
    print("STAGE 5: VERIFICATION")
    print("=" * 60)

    verified = []
    for skill in audited:
        ref = skill.get('source_ref')
        if ref and ref.validated:
            skill['verified'] = True
            verified.append(skill)
        else:
            skill['verified'] = False

    print(f"Skills verified: {len(verified)}/{len(audited)}")

    return verified


def test_storing_stage(verified: list):
    """Test Stage 6: Store verified skills."""
    print("\n" + "=" * 60)
    print("STAGE 6: STORING")
    print("=" * 60)

    # Simulate storing (just output summary)
    output_path = Path("/home/user/skills_fabric/output/docling_skills")
    output_path.mkdir(parents=True, exist_ok=True)

    stored = 0
    for skill in verified:
        skill_file = output_path / f"{skill['name']}.md"
        skill_file.write_text(skill['content'])
        stored += 1

    print(f"Skills stored: {stored}")
    print(f"Output directory: {output_path}")

    return stored


def main():
    print("=" * 70)
    print("FULL PIPELINE TEST - DOCLING")
    print("=" * 70)

    # Stage 1: Mining
    symbols = test_mining_stage()
    if not symbols:
        print("FAIL: No symbols mined")
        return False

    # Stage 2: Linking
    linked = test_linking_stage(symbols)
    if not linked:
        print("FAIL: No symbols linked")
        return False

    # Stage 3: Writing
    skills = test_writing_stage(linked)
    if not skills:
        print("FAIL: No skills written")
        return False

    # Stage 4: Auditing
    audited, hall_rate = test_auditing_stage(skills)
    if hall_rate >= 0.02:
        print(f"WARNING: Hallucination rate {hall_rate:.4f} exceeds target 0.02")

    # Stage 5: Verification
    verified = test_verification_stage(audited)
    if not verified:
        print("FAIL: No skills verified")
        return False

    # Stage 6: Storing
    stored = test_storing_stage(verified)

    # Final summary
    print("\n" + "=" * 70)
    print("PIPELINE SUMMARY")
    print("=" * 70)
    print(f"  Symbols mined: {len(symbols)}")
    print(f"  Symbols linked: {len(linked)}")
    print(f"  Skills written: {len(skills)}")
    print(f"  Skills audited: {len(audited)}")
    print(f"  Skills verified: {len(verified)}")
    print(f"  Skills stored: {stored}")
    print(f"  Hallucination rate: {hall_rate:.4f}")
    print(f"  Target met: {'YES' if hall_rate < 0.02 else 'NO'}")

    success = hall_rate < 0.02 and stored > 0
    print(f"\nFINAL RESULT: {'PASS' if success else 'FAIL'}")

    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

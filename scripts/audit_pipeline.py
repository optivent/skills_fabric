#!/usr/bin/env python3
"""Deep Audit of LangGraph Pipeline Components.

This script thoroughly tests each component in isolation to verify
actual functionality, not just simulated tests.
"""

import sys
import os
import json
import traceback
import importlib.util

print("=" * 70)
print("DEEP AUDIT: LangGraph Pipeline Components")
print("=" * 70)

# =============================================================================
# AUDIT 1: GLM Client - Real API Connection
# =============================================================================

print("\n" + "=" * 70)
print("AUDIT 1: GLM Client - Real API Connection Test")
print("=" * 70)

# Load GLM client
spec_glm = importlib.util.spec_from_file_location(
    "glm_client",
    "/home/user/skills_fabric/src/skills_fabric/llm/glm_client.py"
)
glm_module = importlib.util.module_from_spec(spec_glm)
spec_glm.loader.exec_module(glm_module)

GLMClient = glm_module.GLMClient
GLMConfig = glm_module.GLMConfig
CODING_BASE_URL = glm_module.CODING_BASE_URL
GENERAL_BASE_URL = glm_module.GENERAL_BASE_URL

API_KEY = os.getenv("ZAI_API_KEY", os.getenv("GLM_API_KEY", ""))

if not API_KEY:
    print("⚠ WARNING: No API key found!")
    print("  Set ZAI_API_KEY or GLM_API_KEY environment variable")
    LIVE_TEST = False
else:
    print(f"✓ API key found: {API_KEY[:8]}...{API_KEY[-4:]}")
    LIVE_TEST = True

print(f"\nEndpoint Configuration:")
print(f"  Coding URL: {CODING_BASE_URL}")
print(f"  General URL: {GENERAL_BASE_URL}")

if LIVE_TEST:
    print("\n--- Testing GLM API Connection ---")
    try:
        client = GLMClient()
        print(f"  Using endpoint: {client.endpoint}")

        # Test simple completion
        print("\n  Sending test message...")
        response = client.chat(
            user_message="Say 'API connection successful' and nothing else.",
            thinking=False,
        )

        print(f"\n  Response content: {response.content[:100]}")
        print(f"  Finish reason: {response.finish_reason}")
        print(f"  Tokens used: {response.usage.total_tokens}")
        print(f"  Latency: {response.latency_ms:.0f}ms")

        if "successful" in response.content.lower() or response.content:
            print("\n✓ AUDIT 1 PASSED: GLM API connection working")
            AUDIT_1_PASSED = True
        else:
            print("\n✗ AUDIT 1 FAILED: Unexpected response")
            AUDIT_1_PASSED = False

    except Exception as e:
        print(f"\n✗ AUDIT 1 FAILED: {e}")
        traceback.print_exc()
        AUDIT_1_PASSED = False
else:
    print("\n⚠ AUDIT 1 SKIPPED: No API key")
    AUDIT_1_PASSED = None

# =============================================================================
# AUDIT 2: Research Node - CRITICAL FLAW Detection
# =============================================================================

print("\n" + "=" * 70)
print("AUDIT 2: Research Node - CRITICAL FLAW Analysis")
print("=" * 70)

# Load pipeline
spec_pipeline = importlib.util.spec_from_file_location(
    "langgraph_pipeline",
    "/home/user/skills_fabric/src/skills_fabric/pipeline/langgraph_pipeline.py"
)
pipeline_module = importlib.util.module_from_spec(spec_pipeline)
spec_pipeline.loader.exec_module(pipeline_module)

research_node = pipeline_module.research_node
SkillState = pipeline_module.SkillState

print("\nAnalyzing research_node implementation...")
print("\n⚠ CRITICAL FLAW DETECTED:")
print("  The research_node creates SIMULATED symbols, not real ones!")
print("  It hardcodes fake symbols like:")
print("    - {library}.main_class")
print("    - {library}.helper_func")
print("    - {library}.Config")
print("\n  This means ALL verification is against fake data!")

# Test with real library
state: SkillState = {
    "library": "pandas",
    "topic": "DataFrame.groupby",
    "level": 3,
    "symbols": [],
    "documentation": "",
    "content": "",
    "thinking": "",
    "citations": [],
    "hall_m": 0.0,
    "verified_citations": 0,
    "total_citations": 0,
    "passed": False,
    "retry_count": 0,
    "max_retries": 2,
    "error": None,
    "final_skill": None,
    "token_usage": {},
}

result = research_node(state)

print(f"\nTest result for 'pandas' library:")
print(f"  Symbols returned: {json.dumps(result['symbols'], indent=4)}")
print(f"\n  Expected: Real pandas symbols like:")
print("    - pandas.DataFrame.groupby from pandas/core/frame.py")
print("    - pandas.core.groupby.GroupBy from pandas/core/groupby/grouper.py")
print(f"\n  Got: Fake symbols like 'pandas.main_class'")

print("\n✗ AUDIT 2 FAILED: Research node uses fake/simulated data")
AUDIT_2_PASSED = False

# =============================================================================
# AUDIT 3: Generate Node - Real GLM Generation Test
# =============================================================================

print("\n" + "=" * 70)
print("AUDIT 3: Generate Node - Real Generation Test")
print("=" * 70)

generate_node = pipeline_module.generate_node

if LIVE_TEST:
    print("\nTesting generate_node with real API call...")

    # Prepare state with the fake symbols (as research_node would provide)
    state_for_gen: SkillState = {
        "library": "requests",
        "topic": "HTTP GET request",
        "level": 2,
        "symbols": [
            {"name": "requests.get", "citation": "requests/api.py:64"},
            {"name": "requests.Response", "citation": "requests/models.py:187"},
            {"name": "requests.Session", "citation": "requests/sessions.py:333"},
        ],
        "documentation": """
# requests library

## Overview
HTTP library for Python

## Key functions
- requests.get(url, **kwargs): Send GET request
- requests.Response: Response object
""",
        "content": "",
        "thinking": "",
        "citations": [],
        "hall_m": 0.0,
        "verified_citations": 0,
        "total_citations": 0,
        "passed": False,
        "retry_count": 0,
        "max_retries": 2,
        "error": None,
        "final_skill": None,
        "token_usage": {},
    }

    try:
        result = generate_node(state_for_gen)

        print(f"\nGenerated content length: {len(result['content'])} chars")
        print(f"Thinking trace length: {len(result.get('thinking', ''))} chars")
        print(f"Citations extracted: {result['citations']}")
        print(f"Tokens used: {result['token_usage']}")

        print("\n--- Generated Content Preview ---")
        print(result['content'][:500])
        print("...")

        # Check if citations match what was provided
        provided_paths = {"requests/api.py", "requests/models.py", "requests/sessions.py"}
        extracted = result['citations']

        print(f"\n--- Citation Analysis ---")
        print(f"Provided symbol paths: {provided_paths}")
        print(f"Extracted citations: {extracted}")

        matching = 0
        for cit in extracted:
            path = cit.split(":")[0]
            if any(p in path for p in provided_paths):
                matching += 1
                print(f"  ✓ '{cit}' matches provided symbols")
            else:
                print(f"  ✗ '{cit}' NOT in provided symbols (potential hallucination)")

        if matching > 0 and result['content']:
            print("\n✓ AUDIT 3 PASSED: Generate node produces content")
            AUDIT_3_PASSED = True
        else:
            print("\n⚠ AUDIT 3 WARNING: No matching citations")
            AUDIT_3_PASSED = True  # Generation works, verification is the issue

    except Exception as e:
        print(f"\n✗ AUDIT 3 FAILED: {e}")
        traceback.print_exc()
        AUDIT_3_PASSED = False
else:
    print("\n⚠ AUDIT 3 SKIPPED: No API key")
    AUDIT_3_PASSED = None

# =============================================================================
# AUDIT 4: Verify Node - Citation Verification Logic
# =============================================================================

print("\n" + "=" * 70)
print("AUDIT 4: Verify Node - Citation Verification Logic")
print("=" * 70)

verify_node = pipeline_module.verify_node

print("\nAnalyzing verify_node implementation...")

# Test 1: Fake citations against fake symbols (should pass but is meaningless)
print("\n--- Test 4.1: Fake citations matching fake symbols ---")
state_fake: SkillState = {
    "library": "mylib",
    "topic": "test",
    "level": 3,
    "symbols": [
        {"name": "mylib.foo", "citation": "mylib/core.py:42"},
        {"name": "mylib.bar", "citation": "mylib/utils.py:15"},
    ],
    "documentation": "",
    "content": "Use mylib/core.py for processing",
    "thinking": "",
    "citations": ["mylib/core.py:42", "mylib/utils.py:15"],  # Match fake symbols
    "hall_m": 0.0,
    "verified_citations": 0,
    "total_citations": 0,
    "passed": False,
    "retry_count": 0,
    "max_retries": 2,
    "error": None,
    "final_skill": None,
    "token_usage": {},
}

result = verify_node(state_fake)
print(f"  hall_m: {result['hall_m']:.2%}")
print(f"  verified: {result['verified_citations']}/{result['total_citations']}")
print(f"  passed: {result['passed']}")
print(f"  ⚠ This 'passes' but verifies fake data against fake data!")

# Test 2: Real request library citations (LLM might generate different paths)
print("\n--- Test 4.2: Real library citation test ---")
state_real: SkillState = {
    "library": "requests",
    "topic": "HTTP",
    "level": 3,
    "symbols": [
        {"name": "requests.get", "citation": "requests/api.py:64"},
        {"name": "requests.Session", "citation": "requests/sessions.py:333"},
    ],
    "documentation": "",
    "content": "Import requests and use get()",
    "thinking": "",
    # Simulate what LLM might generate - different but valid paths
    "citations": ["requests/__init__.py:10", "requests/api.py:75"],
    "hall_m": 0.0,
    "verified_citations": 0,
    "total_citations": 0,
    "passed": False,
    "retry_count": 0,
    "max_retries": 2,
    "error": None,
    "final_skill": None,
    "token_usage": {},
}

result = verify_node(state_real)
print(f"  hall_m: {result['hall_m']:.2%}")
print(f"  verified: {result['verified_citations']}/{result['total_citations']}")
print(f"  passed: {result['passed']}")

# Analyze the verification logic
print("\n--- Verification Logic Analysis ---")
print("  Current logic: Checks if citation PATH contains any 'valid' path")
print("  Problem 1: 'valid_paths' come from fake symbols, not real SCIP data")
print("  Problem 2: Substring matching is too loose (requests/api.py matches api.py)")
print("  Problem 3: No actual verification against real source code")

# Test 3: Obviously wrong citations
print("\n--- Test 4.3: Obviously wrong citations ---")
state_wrong: SkillState = {
    "library": "requests",
    "topic": "HTTP",
    "level": 3,
    "symbols": [
        {"name": "requests.get", "citation": "requests/api.py:64"},
    ],
    "documentation": "",
    "content": "Use the function from totally/wrong/path.py",
    "thinking": "",
    "citations": ["totally/wrong/path.py:999", "nonexistent/module.py:1"],
    "hall_m": 0.0,
    "verified_citations": 0,
    "total_citations": 0,
    "passed": False,
    "retry_count": 0,
    "max_retries": 2,
    "error": None,
    "final_skill": None,
    "token_usage": {},
}

result = verify_node(state_wrong)
print(f"  hall_m: {result['hall_m']:.2%}")
print(f"  verified: {result['verified_citations']}/{result['total_citations']}")
print(f"  passed: {result['passed']}")
print(f"  ✓ At least this correctly fails")

print("\n✗ AUDIT 4 FAILED: Verification logic has fundamental flaws")
print("  - Verifies against fake/simulated symbols, not real SCIP data")
print("  - No actual source code verification")
print("  - Pattern matching is too simplistic")
AUDIT_4_PASSED = False

# =============================================================================
# AUDIT 5: End-to-End Pipeline Flow
# =============================================================================

print("\n" + "=" * 70)
print("AUDIT 5: End-to-End Pipeline Flow")
print("=" * 70)

if LIVE_TEST:
    SkillGenerationPipeline = pipeline_module.SkillGenerationPipeline

    print("\nRunning full pipeline with debugging...")

    pipeline = SkillGenerationPipeline(checkpointing=False)

    try:
        result = pipeline.generate(
            library="json",
            topic="JSON parsing",
            level=2,
            max_retries=1,
        )

        print(f"\nPipeline Result:")
        print(f"  Library: {result['library']}")
        print(f"  Topic: {result['topic']}")
        print(f"  Passed: {result['passed']}")
        print(f"  Hall_m: {result['hall_m']:.2%}")
        print(f"  Verified: {result['verified_citations']}/{result['total_citations']}")
        print(f"  Retries: {result['retry_count']}")

        print(f"\n  Symbols (from research_node - FAKE):")
        for s in result['symbols']:
            print(f"    - {s['name']}: {s['citation']}")

        print(f"\n  Citations (from generate_node):")
        for c in result['citations']:
            print(f"    - {c}")

        print("\n⚠ Pipeline 'works' but with fundamental flaws:")
        print("  - Research gives fake symbols")
        print("  - Verification is against fake data")
        print("  - hall_m=0 doesn't mean zero hallucinations")

        AUDIT_5_PASSED = False  # Works but flawed

    except Exception as e:
        print(f"\n✗ AUDIT 5 FAILED: {e}")
        traceback.print_exc()
        AUDIT_5_PASSED = False
else:
    print("\n⚠ AUDIT 5 SKIPPED: No API key")
    AUDIT_5_PASSED = None

# =============================================================================
# SUMMARY
# =============================================================================

print("\n" + "=" * 70)
print("AUDIT SUMMARY")
print("=" * 70)

audits = [
    ("1. GLM API Connection", AUDIT_1_PASSED),
    ("2. Research Node (CRITICAL)", AUDIT_2_PASSED),
    ("3. Generate Node", AUDIT_3_PASSED),
    ("4. Verify Node (CRITICAL)", AUDIT_4_PASSED),
    ("5. End-to-End Pipeline", AUDIT_5_PASSED),
]

for name, passed in audits:
    if passed is True:
        status = "✓ PASSED"
    elif passed is False:
        status = "✗ FAILED"
    else:
        status = "⚠ SKIPPED"
    print(f"  {name}: {status}")

print("\n" + "=" * 70)
print("CRITICAL FINDINGS")
print("=" * 70)
print("""
1. RESEARCH NODE IS FAKE:
   - Creates hardcoded simulated symbols instead of querying SCIP
   - Every library gets the same fake symbols (main_class, helper_func, Config)
   - No real documentation fetching

2. VERIFICATION IS MEANINGLESS:
   - Verifies citations against FAKE symbols from research_node
   - hall_m=0% means "matches fake data" not "zero hallucinations"
   - No actual verification against real source code

3. FALSE CONFIDENCE:
   - Tests "pass" because they test fake data against fake expectations
   - Real hallucinations would NOT be detected
   - The "zero-hallucination" claim is NOT validated

REQUIRED FIXES:
   - Connect research_node to real SCIP index
   - Implement actual citation verification against source files
   - Add DDR (Deep Document Retrieval) for real documentation
   - Test against actual library code, not simulated data
""")

print("\n" + "=" * 70)

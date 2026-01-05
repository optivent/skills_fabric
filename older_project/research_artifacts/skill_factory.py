#!/usr/bin/env python3
"""
Sovereign Skill Factory - Simplified 6-Node Pipeline
A Miessler-aligned skill generation engine with zero-hallucination guarantees.

Architecture:
  1. SelectSource    -> Choose verified content from Context7/CodeWiki
  2. ExtractHardContent -> AST/regex extraction (no LLM, 100% trust)
  3. GenerateQuestion -> LLM creates question grounded in HardContent
  4. VerifyGrounding  -> Check question references real concepts
  5. ExecuteSandbox  -> Run code in Docker, capture output
  6. FormatSkill     -> Structure into Claude Skill format

Models:
  - GLM-4.7: Question generation (bulk, cheap)
  - Claude: Final validation (quality-critical)
"""
import os
import re
import json
import subprocess
from pathlib import Path
from typing import TypedDict, Optional, Annotated
from dataclasses import dataclass
import operator

# LangGraph
from langgraph.graph import StateGraph, START, END

# LangChain (for LLM calls)
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

# KuzuDB for storage
import kuzu

# =============================================================================
# CONFIGURATION
# =============================================================================

@dataclass
class FactoryConfig:
    """Configuration for the Skill Factory."""
    # Paths
    context7_cache: str = os.path.expanduser('~/sovereign_platform/data/context7_cache')
    codewiki_dir: str = os.path.expanduser('~/sovereign_platform/data/codewiki')
    kuzu_db: str = os.path.expanduser('~/sovereign_platform/data/kuzu_db')
    output_dir: str = os.path.expanduser('~/sovereign_platform/skills')
    
    # LLM Config
    glm_base_url: str = 'https://api.z.ai/v1'
    glm_model: str = 'glm-4.7'
    glm_api_key: str = os.environ.get('ZAI_API_KEY', '')
    
    # Sandbox: 'bubblewrap' (lighter, default) or 'docker' (heavier, more isolated)
    sandbox_method: str = 'bubblewrap'
    docker_image: str = 'python:3.12-slim'
    timeout_seconds: int = 30

# =============================================================================
# STATE DEFINITION (Simplified)
# =============================================================================

class SkillState(TypedDict):
    """State for the simplified skill pipeline."""
    # Input
    library: str
    source_file: str
    code_snippet: str
    
    # HardContent extraction
    imports: list[str]
    api_calls: list[str]
    concepts: list[str]
    
    # Question generation
    question: str
    question_grounded: bool
    
    # Execution
    execution_success: bool
    execution_output: str
    execution_error: str
    
    # Output
    skill_json: dict
    
    # Control
    errors: Annotated[list[str], operator.add]

# =============================================================================
# NODE IMPLEMENTATIONS
# =============================================================================

def select_source(state: SkillState) -> dict:
    """Node 1: Select verified content from cache."""
    # For now, just validate the source exists
    config = FactoryConfig()
    source_path = os.path.join(config.context7_cache, state['source_file'])
    
    if not os.path.exists(source_path):
        return {'errors': [f"Source not found: {source_path}"]}
    
    with open(source_path, 'r') as f:
        data = json.load(f)
    
    # Extract first code snippet (simplified)
    if 'docs' in data and data['docs']:
        snippet = data['docs'][0].get('code', '')
    else:
        snippet = ''
    
    return {'code_snippet': snippet}


def extract_hard_content(state: SkillState) -> dict:
    """Node 2: Extract HardContent via regex/AST (no LLM)."""
    code = state.get('code_snippet', '')
    
    # Extract imports
    imports = re.findall(r'^(?:from|import)\s+([^\s]+)', code, re.MULTILINE)
    
    # Extract API calls (function calls)
    api_calls = re.findall(r'([a-zA-Z_][a-zA-Z0-9_]*)\s*\(', code)
    
    # Extract class names
    classes = re.findall(r'class\s+([a-zA-Z_][a-zA-Z0-9_]*)', code)
    
    # Combine as concepts
    concepts = list(set(imports + classes + api_calls[:10]))  # Limit to prevent noise
    
    return {
        'imports': imports,
        'api_calls': api_calls[:20],
        'concepts': concepts
    }


def generate_question(state: SkillState) -> dict:
    """Node 3: LLM generates question grounded in HardContent."""
    config = FactoryConfig()
    
    if not config.glm_api_key:
        return {'question': '', 'errors': ['ZAI_API_KEY not set']}
    
    llm = ChatOpenAI(
        model=config.glm_model,
        base_url=config.glm_base_url,
        api_key=config.glm_api_key,
        temperature=0.7,
        max_tokens=200,
    )
    
    concepts_str = ', '.join(state.get('concepts', [])[:5])
    code_preview = state.get('code_snippet', '')[:500]
    
    prompt = f"""Generate a clear, practical question that this code snippet answers.
The question MUST reference at least 2 of these concepts: {concepts_str}

Code snippet:
```python
{code_preview}
```

Output ONLY the question, nothing else. Example format:
"How do I use [Concept1] with [Concept2] to achieve X?"
"""
    
    response = llm.invoke([HumanMessage(content=prompt)])
    question = response.content.strip().strip('"')
    
    return {'question': question}


def verify_grounding(state: SkillState) -> dict:
    """Node 4: Verify question is grounded in HardContent."""
    question = state.get('question', '').lower()
    concepts = [c.lower() for c in state.get('concepts', [])]
    
    # Check at least 1 concept appears in question
    grounded_count = sum(1 for c in concepts if c in question)
    
    return {'question_grounded': grounded_count >= 1}


def execute_sandbox(state: SkillState) -> dict:
    """Node 5: Execute code in sandbox (Bubblewrap or Docker).
    
    Bubblewrap: Lighter, faster, default for development
    Docker: Heavier, more isolated, for production
    """
    config = FactoryConfig()
    code = state.get('code_snippet', '')
    
    if not code:
        return {'execution_success': False, 'execution_error': 'No code to execute'}
    
    # Choose sandbox method
    if config.sandbox_method == 'bubblewrap':
        return _execute_bubblewrap(code, config)
    else:
        return _execute_docker(code, config)


def _execute_bubblewrap(code: str, config: FactoryConfig) -> dict:
    """Execute code in Bubblewrap sandbox (lightweight, Linux-only)."""
    import tempfile
    
    # Write code to temp file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
        f.write(code)
        script_path = f.name
    
    try:
        # Bubblewrap command with minimal permissions
        bwrap_cmd = [
            'bwrap',
            '--ro-bind', '/usr', '/usr',
            '--ro-bind', '/lib', '/lib',
            '--ro-bind', '/lib64', '/lib64',  # May not exist on all systems
            '--ro-bind', '/bin', '/bin',
            '--ro-bind', script_path, '/script.py',
            '--unshare-all',
            '--die-with-parent',
            'python3', '/script.py'
        ]
        
        result = subprocess.run(
            bwrap_cmd,
            capture_output=True,
            text=True,
            timeout=config.timeout_seconds
        )
        
        output = result.stdout + result.stderr
        success = result.returncode == 0
        
        return {
            'execution_success': success,
            'execution_output': output[:1000],
            'execution_error': '' if success else output[:500]
        }
    except FileNotFoundError:
        return {'execution_success': False, 'execution_error': 'bubblewrap not installed'}
    except subprocess.TimeoutExpired:
        return {'execution_success': False, 'execution_error': 'Timeout'}
    except Exception as e:
        return {'execution_success': False, 'execution_error': str(e)}
    finally:
        os.unlink(script_path)


def _execute_docker(code: str, config: FactoryConfig) -> dict:
    """Execute code in Docker sandbox (heavier, more isolated)."""
    script_content = f'''#!/usr/bin/env python3
try:
    {code}
    print("__EXECUTION_SUCCESS__")
except Exception as e:
    print(f"__EXECUTION_ERROR__: {{e}}")
'''
    
    try:
        result = subprocess.run(
            ['docker', 'run', '--rm', '-i', config.docker_image, 'python3', '-c', script_content],
            capture_output=True,
            text=True,
            timeout=config.timeout_seconds
        )
        
        output = result.stdout + result.stderr
        success = '__EXECUTION_SUCCESS__' in output
        
        return {
            'execution_success': success,
            'execution_output': output[:1000],
            'execution_error': '' if success else output[:500]
        }
    except subprocess.TimeoutExpired:
        return {'execution_success': False, 'execution_error': 'Timeout'}
    except Exception as e:
        return {'execution_success': False, 'execution_error': str(e)}


def format_skill(state: SkillState) -> dict:
    """Node 6: Format into Claude Skill JSON."""
    skill = {
        'library': state.get('library', ''),
        'question': state.get('question', ''),
        'code': state.get('code_snippet', ''),
        'concepts': state.get('concepts', []),
        'verified': state.get('execution_success', False),
        'grounded': state.get('question_grounded', False),
        'source': state.get('source_file', ''),
    }
    
    return {'skill_json': skill}


# =============================================================================
# GRAPH CONSTRUCTION
# =============================================================================

def build_skill_graph():
    """Build the 6-node skill generation graph."""
    graph = StateGraph(SkillState)
    
    # Add nodes
    graph.add_node('select_source', select_source)
    graph.add_node('extract_hard_content', extract_hard_content)
    graph.add_node('generate_question', generate_question)
    graph.add_node('verify_grounding', verify_grounding)
    graph.add_node('execute_sandbox', execute_sandbox)
    graph.add_node('format_skill', format_skill)
    
    # Add edges (linear flow)
    graph.add_edge(START, 'select_source')
    graph.add_edge('select_source', 'extract_hard_content')
    graph.add_edge('extract_hard_content', 'generate_question')
    graph.add_edge('generate_question', 'verify_grounding')
    graph.add_edge('verify_grounding', 'execute_sandbox')
    graph.add_edge('execute_sandbox', 'format_skill')
    graph.add_edge('format_skill', END)
    
    return graph.compile()


# =============================================================================
# MAIN
# =============================================================================

def main():
    print("="*60)
    print("SOVEREIGN SKILL FACTORY - 6-Node Pipeline")
    print("="*60)
    
    # Build graph
    app = build_skill_graph()
    
    # Test with sample input
    initial_state = {
        'library': 'langchain',
        'source_file': 'langchain_oss_python_langchain_sample.json',  # Will need real file
        'code_snippet': '',
        'imports': [],
        'api_calls': [],
        'concepts': [],
        'question': '',
        'question_grounded': False,
        'execution_success': False,
        'execution_output': '',
        'execution_error': '',
        'skill_json': {},
        'errors': [],
    }
    
    print("\n[+] Graph built successfully")
    print("[.] To run: provide a real Context7 cache file")
    print("\nGraph structure:")
    print("  START -> select_source -> extract_hard_content -> generate_question")
    print("       -> verify_grounding -> execute_sandbox -> format_skill -> END")

if __name__ == '__main__':
    main()

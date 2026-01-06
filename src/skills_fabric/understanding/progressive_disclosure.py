#!/usr/bin/env python3
"""
Progressive Disclosure Understanding System

A hierarchical approach to code understanding with 6 levels of depth:
- Level 0: Executive Summary (what is this?)
- Level 1: Concept Map (major components)
- Level 2: Detailed Sections (how things work)
- Level 3: Source References (actual code)
- Level 4: Semantic Analysis (LSP + AST)
- Level 5: Execution Proofs (verified behavior)

Each level can be expanded on-demand, providing just-in-time understanding.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Set
from enum import IntEnum
from pathlib import Path
import json
import re
from datetime import datetime


class DepthLevel(IntEnum):
    """Understanding depth levels."""
    EXECUTIVE_SUMMARY = 0  # 1 paragraph overview
    CONCEPT_MAP = 1        # H2 sections - major components
    DETAILED_SECTIONS = 2  # H3 sections - how things work
    SOURCE_REFERENCES = 3  # GitHub links - actual code
    SEMANTIC_ANALYSIS = 4  # LSP + AST - deep understanding
    EXECUTION_PROOFS = 5   # Tests + assertions - verified behavior


@dataclass
class SourceRef:
    """A reference to source code with verification."""
    file_path: str
    line: int
    commit: str
    repo: str
    symbol_name: str
    symbol_kind: str  # class, function, method
    verified: bool = False  # True if validated against clone

    @property
    def github_url(self) -> str:
        return f"https://github.com/{self.repo}/blob/{self.commit}/{self.file_path}#L{self.line}"

    @property
    def local_path(self) -> str:
        return f"{self.file_path}:{self.line}"


@dataclass
class SemanticInfo:
    """Deep semantic analysis from LSP/AST."""
    type_signature: Optional[str] = None
    parameters: List[Dict[str, str]] = field(default_factory=list)
    return_type: Optional[str] = None
    docstring: str = ""
    calls: List[str] = field(default_factory=list)  # Functions this calls
    called_by: List[str] = field(default_factory=list)  # Functions that call this
    imports: List[str] = field(default_factory=list)
    complexity: Optional[int] = None  # Cyclomatic complexity
    data_flow: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionProof:
    """Verified behavior through execution."""
    assertion: str
    result: bool
    evidence: str  # Actual output/trace
    timestamp: datetime = field(default_factory=datetime.now)


@dataclass
class UnderstandingNode:
    """A node in the progressive understanding tree."""
    id: str
    title: str
    level: DepthLevel
    content: str  # The understanding at this level

    # Hierarchy
    parent_id: Optional[str] = None
    children_ids: List[str] = field(default_factory=list)

    # Progressive data (populated on-demand)
    source_refs: List[SourceRef] = field(default_factory=list)
    semantic_info: Optional[SemanticInfo] = None
    execution_proofs: List[ExecutionProof] = field(default_factory=list)

    # Metadata
    keywords: Set[str] = field(default_factory=set)
    related_ids: List[str] = field(default_factory=list)

    @property
    def is_expanded(self) -> bool:
        """Check if deeper levels have been populated."""
        if self.level == DepthLevel.SOURCE_REFERENCES:
            return len(self.source_refs) > 0
        elif self.level == DepthLevel.SEMANTIC_ANALYSIS:
            return self.semantic_info is not None
        elif self.level == DepthLevel.EXECUTION_PROOFS:
            return len(self.execution_proofs) > 0
        return len(self.children_ids) > 0


@dataclass
class ProgressiveUnderstanding:
    """
    Complete progressive understanding of a codebase.

    Organized as a tree with 6 depth levels:
    - Root: Executive summary
    - Level 1: Major concepts
    - Level 2: Detailed sections
    - Level 3+: On-demand expansion
    """
    name: str
    repo: str
    commit: str
    nodes: Dict[str, UnderstandingNode] = field(default_factory=dict)
    root_id: Optional[str] = None

    # Index for fast lookup
    _by_level: Dict[DepthLevel, List[str]] = field(default_factory=dict)
    _by_keyword: Dict[str, List[str]] = field(default_factory=dict)

    def add_node(self, node: UnderstandingNode) -> None:
        """Add a node to the understanding tree."""
        self.nodes[node.id] = node

        # Index by level
        if node.level not in self._by_level:
            self._by_level[node.level] = []
        self._by_level[node.level].append(node.id)

        # Index by keywords
        for kw in node.keywords:
            if kw not in self._by_keyword:
                self._by_keyword[kw] = []
            self._by_keyword[kw].append(node.id)

    def get_at_level(self, level: DepthLevel) -> List[UnderstandingNode]:
        """Get all nodes at a specific depth level."""
        ids = self._by_level.get(level, [])
        return [self.nodes[id] for id in ids]

    def search(self, query: str) -> List[UnderstandingNode]:
        """Search for nodes matching a query."""
        query_lower = query.lower()
        results = []

        # First check keywords
        for kw, ids in self._by_keyword.items():
            if query_lower in kw.lower():
                for id in ids:
                    if self.nodes[id] not in results:
                        results.append(self.nodes[id])

        # Then check content
        for node in self.nodes.values():
            if query_lower in node.title.lower() or query_lower in node.content.lower():
                if node not in results:
                    results.append(node)

        # Sort by level (shallower first)
        results.sort(key=lambda n: n.level)
        return results

    def expand(self, node_id: str, to_level: DepthLevel) -> UnderstandingNode:
        """
        Expand a node to a deeper level of understanding.
        This is where the magic happens - on-demand deep analysis.
        """
        node = self.nodes.get(node_id)
        if not node:
            raise ValueError(f"Node {node_id} not found")

        if to_level <= node.level:
            return node  # Already at or beyond this level

        # Progressive expansion based on target level
        if to_level >= DepthLevel.SOURCE_REFERENCES and not node.source_refs:
            node.source_refs = self._find_source_refs(node)

        if to_level >= DepthLevel.SEMANTIC_ANALYSIS and not node.semantic_info:
            node.semantic_info = self._analyze_semantics(node)

        if to_level >= DepthLevel.EXECUTION_PROOFS and not node.execution_proofs:
            node.execution_proofs = self._generate_proofs(node)

        return node

    def _find_source_refs(self, node: UnderstandingNode) -> List[SourceRef]:
        """Find source code references for a node. Override in subclass."""
        return []

    def _analyze_semantics(self, node: UnderstandingNode) -> Optional[SemanticInfo]:
        """Perform LSP/AST analysis. Override in subclass."""
        return None

    def _generate_proofs(self, node: UnderstandingNode) -> List[ExecutionProof]:
        """Generate execution proofs. Override in subclass."""
        return []

    def get_summary(self, max_level: DepthLevel = DepthLevel.CONCEPT_MAP) -> str:
        """Get a summary up to the specified level."""
        lines = []

        # Level 0: Executive summary
        if self.root_id and max_level >= DepthLevel.EXECUTIVE_SUMMARY:
            root = self.nodes[self.root_id]
            lines.append(f"# {root.title}")
            lines.append("")
            lines.append(root.content)
            lines.append("")

        # Level 1: Concept map
        if max_level >= DepthLevel.CONCEPT_MAP:
            concepts = self.get_at_level(DepthLevel.CONCEPT_MAP)
            if concepts:
                lines.append("## Key Concepts")
                lines.append("")
                for concept in concepts:
                    lines.append(f"- **{concept.title}**: {concept.content[:100]}...")
                lines.append("")

        # Level 2: Detailed sections
        if max_level >= DepthLevel.DETAILED_SECTIONS:
            sections = self.get_at_level(DepthLevel.DETAILED_SECTIONS)
            if sections:
                lines.append("## Details")
                lines.append("")
                for section in sections[:10]:  # Limit for summary
                    lines.append(f"### {section.title}")
                    lines.append(section.content[:200] + "...")
                    lines.append("")

        return "\n".join(lines)

    def to_dict(self) -> Dict:
        """Serialize to dictionary."""
        return {
            "name": self.name,
            "repo": self.repo,
            "commit": self.commit,
            "root_id": self.root_id,
            "nodes": {
                id: {
                    "id": n.id,
                    "title": n.title,
                    "level": n.level,
                    "content": n.content,
                    "parent_id": n.parent_id,
                    "children_ids": n.children_ids,
                    "keywords": list(n.keywords),
                    "source_refs": [
                        {"file_path": r.file_path, "line": r.line, "commit": r.commit,
                         "repo": r.repo, "symbol_name": r.symbol_name, "symbol_kind": r.symbol_kind}
                        for r in n.source_refs
                    ]
                }
                for id, n in self.nodes.items()
            }
        }

    def save(self, path: Path) -> None:
        """Save to JSON file."""
        path.write_text(json.dumps(self.to_dict(), indent=2))

    @classmethod
    def load(cls, path: Path) -> 'ProgressiveUnderstanding':
        """Load from JSON file."""
        data = json.loads(path.read_text())
        pu = cls(name=data["name"], repo=data["repo"], commit=data["commit"])
        pu.root_id = data.get("root_id")

        for id, nd in data.get("nodes", {}).items():
            node = UnderstandingNode(
                id=nd["id"],
                title=nd["title"],
                level=DepthLevel(nd["level"]),
                content=nd["content"],
                parent_id=nd.get("parent_id"),
                children_ids=nd.get("children_ids", []),
                keywords=set(nd.get("keywords", []))
            )
            for ref in nd.get("source_refs", []):
                node.source_refs.append(SourceRef(**ref))
            pu.add_node(node)

        return pu


class ProgressiveUnderstandingBuilder:
    """
    Builds a ProgressiveUnderstanding from CodeWiki output.

    This is the main entry point for creating understanding trees.
    """

    def __init__(self, repo_name: str, repo_path: Path, codewiki_path: Path):
        self.repo_name = repo_name
        self.repo_path = repo_path
        self.codewiki_path = codewiki_path
        self.commit = self._get_commit()

        # Load symbols for Level 3+
        self.symbols: Dict[str, SourceRef] = {}
        self._load_symbols()

        # Pre-load sections for efficient processing
        self._sections_cache: Dict[str, str] = {}
        self._preload_sections()

    def _get_commit(self) -> str:
        """Get commit hash from repo."""
        git_head = self.repo_path / ".git" / "HEAD"
        if git_head.exists():
            ref = git_head.read_text().strip()
            if ref.startswith("ref: "):
                ref_path = self.repo_path / ".git" / ref[5:]
                if ref_path.exists():
                    return ref_path.read_text().strip()[:12]
            return ref[:12]
        return "main"

    def _load_symbols(self) -> None:
        """Load symbol catalog for source references."""
        catalog_path = self.codewiki_path / "symbol_catalog.md"
        if not catalog_path.exists():
            return

        content = catalog_path.read_text()
        # Parse GitHub links from catalog
        pattern = r"\[`([^`]+)`\]\(https://github\.com/([^/]+/[^/]+)/blob/([^/]+)/([^#]+)#L(\d+)\)"

        for match in re.finditer(pattern, content):
            name, repo, commit, file_path, line = match.groups()
            self.symbols[name] = SourceRef(
                file_path=file_path,
                line=int(line),
                commit=commit,
                repo=repo,
                symbol_name=name,
                symbol_kind="unknown",
                verified=True
            )

    def _preload_sections(self) -> None:
        """Pre-load all section files into memory for fast processing."""
        sections_dir = self.codewiki_path / "sections"
        if not sections_dir.exists():
            return

        for section_file in sorted(sections_dir.iterdir()):
            if section_file.name.endswith('.md'):
                try:
                    self._sections_cache[section_file.name] = section_file.read_text()
                except:
                    pass

    def build(self) -> ProgressiveUnderstanding:
        """Build the complete progressive understanding tree."""
        pu = ProgressiveUnderstanding(
            name=self.repo_name,
            repo=f"langchain-ai/{self.repo_name}" if "langgraph" in self.repo_name.lower() else self.repo_name,
            commit=self.commit
        )

        # Level 0: Executive Summary
        root = self._build_executive_summary()
        pu.add_node(root)
        pu.root_id = root.id

        # Level 1: Concept Map (from H2 sections)
        concepts = self._build_concept_map(root.id)
        for concept in concepts:
            pu.add_node(concept)
            root.children_ids.append(concept.id)

        # Level 2: Detailed Sections (from H3 sections)
        for concept in concepts:
            sections = self._build_detailed_sections(concept)
            for section in sections:
                pu.add_node(section)
                concept.children_ids.append(section.id)

        return pu

    def _build_executive_summary(self) -> UnderstandingNode:
        """Build Level 0: Executive Summary."""
        # Try to find README or index
        readme_path = self.repo_path / "README.md"
        content = ""

        if readme_path.exists():
            readme = readme_path.read_text()
            lines = readme.split('\n')

            # Look for substantive paragraphs (not badges, HTML, code blocks)
            in_code_block = False
            for line in lines:
                stripped = line.strip()

                # Skip code blocks
                if stripped.startswith('```'):
                    in_code_block = not in_code_block
                    continue
                if in_code_block:
                    continue

                # Skip HTML, badges, empty lines
                if stripped.startswith('<') or stripped.startswith('[![') or not stripped:
                    continue
                if stripped.startswith('#'):
                    continue

                # Found a substantive paragraph
                if len(stripped) > 50 and not stripped.startswith('|'):
                    content = stripped
                    break

        if not content:
            content = f"A Python library for {self.repo_name}."

        return UnderstandingNode(
            id="root",
            title=self.repo_name,
            level=DepthLevel.EXECUTIVE_SUMMARY,
            content=content,
            keywords=self._extract_keywords(content)
        )

    def _build_concept_map(self, parent_id: str) -> List[UnderstandingNode]:
        """Build Level 1: Concept Map - group sections by major topics."""
        # Define major topic categories
        topic_categories = {
            "Agents": ["agent", "react", "prebuilt", "tools", "tool_calling"],
            "State & Memory": ["state", "memory", "checkpoint", "persistence", "store"],
            "Graphs & Workflow": ["graph", "stategraph", "node", "edge", "workflow", "compile"],
            "Human-in-the-Loop": ["human", "interrupt", "approval", "hitl"],
            "Streaming": ["stream", "streaming", "token", "events"],
            "Deployment": ["deploy", "cloud", "server", "platform", "docker"],
            "Multi-Agent": ["multi_agent", "supervisor", "swarm", "handoff"],
            "Configuration": ["config", "configuration", "settings"],
            "Debugging": ["debug", "tracing", "langsmith", "observability"],
            "Examples": ["example", "tutorial", "quickstart", "how_to"],
        }

        concepts = []

        for topic, keywords in topic_categories.items():
            # Find sections matching this topic
            matching_sections = []

            for filename, content in self._sections_cache.items():
                filename_lower = filename.lower()
                content_lower = content.lower()[:500]

                if any(kw in filename_lower or kw in content_lower for kw in keywords):
                    # Extract the H2 title from content
                    for line in content.split('\n'):
                        if line.startswith('## '):
                            title = line[3:].strip()
                            if title.lower() not in ['source references']:
                                matching_sections.append({
                                    'filename': filename,
                                    'title': title,
                                    'content': content
                                })
                            break

            if matching_sections:
                # Create concept node for this topic
                preview = f"Contains {len(matching_sections)} sections about {topic.lower()}."
                if matching_sections:
                    titles = [s['title'] for s in matching_sections[:3]]
                    preview += f" Key topics: {', '.join(titles)}"

                concept = UnderstandingNode(
                    id=f"concept_{len(concepts)}",
                    title=topic,
                    level=DepthLevel.CONCEPT_MAP,
                    content=preview[:300],
                    parent_id=parent_id,
                    keywords=set(keywords + [topic.lower()])
                )
                concept._matching_sections = matching_sections  # Store for Level 2
                concepts.append(concept)

        return concepts

    def _build_detailed_sections(self, concept: UnderstandingNode) -> List[UnderstandingNode]:
        """Build Level 2: Detailed sections under a concept."""
        sections = []

        # Use pre-matched sections from concept building
        matching_sections = getattr(concept, '_matching_sections', [])

        for match in matching_sections[:15]:  # Limit to 15 per concept
            content = match['content']

            # Get content after the H2 title (skip the title line)
            lines = content.split('\n')
            content_lines = []
            started = False
            for line in lines:
                if line.startswith('## '):
                    started = True
                    continue
                if started:
                    if line.startswith('### Source References'):
                        break
                    content_lines.append(line)

            section_content = '\n'.join(content_lines).strip()[:600]

            # Extract source refs from full content
            source_refs = self._extract_source_refs(content)

            sections.append(UnderstandingNode(
                id=f"{concept.id}_section_{len(sections)}",
                title=match['title'],
                level=DepthLevel.DETAILED_SECTIONS,
                content=section_content,
                parent_id=concept.id,
                source_refs=source_refs,
                keywords=self._extract_keywords(f"{match['title']} {section_content[:200]}")
            ))

        return sections

    def _extract_source_refs(self, content: str) -> List[SourceRef]:
        """Extract source references from content."""
        refs = []
        pattern = r"\[`([^`]+)`\]\(https://github\.com/([^/]+/[^/]+)/blob/([^/]+)/([^#]+)#L(\d+)\)"

        for match in re.finditer(pattern, content):
            name, repo, commit, file_path, line = match.groups()
            refs.append(SourceRef(
                file_path=file_path,
                line=int(line),
                commit=commit,
                repo=repo,
                symbol_name=name,
                symbol_kind="unknown",
                verified=True
            ))

        return refs

    def _extract_keywords(self, text: str) -> Set[str]:
        """Extract keywords from text."""
        # Simple keyword extraction
        words = re.findall(r'\b[A-Z][a-z]+[A-Z][a-zA-Z]*\b', text)  # CamelCase
        words += re.findall(r'\b[a-z]+_[a-z_]+\b', text)  # snake_case
        words += re.findall(r'\b[A-Z]{2,}\b', text)  # ACRONYMS

        # Also add significant words
        for word in text.split():
            word = word.strip('`[]().,;:')
            if len(word) > 5 and word[0].isupper():
                words.append(word)

        return set(w for w in words if len(w) > 2)


def build_progressive_understanding(
    repo_name: str,
    repo_path: Path,
    codewiki_path: Path,
    output_path: Optional[Path] = None
) -> ProgressiveUnderstanding:
    """
    Main entry point: Build progressive understanding from a CodeWiki.

    Args:
        repo_name: Name of the repository
        repo_path: Path to cloned repository
        codewiki_path: Path to CodeWiki output directory
        output_path: Optional path to save the result

    Returns:
        ProgressiveUnderstanding tree
    """
    builder = ProgressiveUnderstandingBuilder(repo_name, repo_path, codewiki_path)
    pu = builder.build()

    if output_path:
        pu.save(output_path)

    return pu


if __name__ == "__main__":
    # Test with LangGraph
    from pathlib import Path

    repo_path = Path("/home/user/skills_fabric/langgraph_repo")
    codewiki_path = Path("/home/user/skills_fabric/crawl_output/langgraph")
    output_path = Path("/home/user/skills_fabric/crawl_output/langgraph/progressive_understanding.json")

    if repo_path.exists() and codewiki_path.exists():
        pu = build_progressive_understanding("langgraph", repo_path, codewiki_path, output_path)

        print(f"Built progressive understanding for {pu.name}")
        print(f"  Commit: {pu.commit}")
        print(f"  Total nodes: {len(pu.nodes)}")
        print(f"  Levels: {dict(sorted([(l.name, len(ids)) for l, ids in pu._by_level.items()]))}")
        print()
        print("=== EXECUTIVE SUMMARY ===")
        print(pu.get_summary(DepthLevel.CONCEPT_MAP))

#!/usr/bin/env python3
"""
Skill Development Framework

Integrates:
1. Progressive Disclosure (Levels 0-5) - Context Provider
2. Claude Hierarchy (Opus/Sonnet/Haiku) - Intelligence Routing
3. Git Worktrees - Parallel Execution

The goal: Perfect proficiency with any library through
machine-verified understanding and tiered intelligence.
"""

import subprocess
import json
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from pathlib import Path
from datetime import datetime
from enum import Enum


class SkillPhase(Enum):
    """Phases of skill development."""
    CRAWL = "crawl"           # Get CodeWiki/documentation
    UNDERSTAND = "understand"  # Build progressive disclosure
    DEVELOP = "develop"        # Generate skill code
    VERIFY = "verify"          # Test and validate
    REFINE = "refine"          # Iterate improvements


@dataclass
class WorktreeConfig:
    """Configuration for a git worktree agent."""
    name: str
    branch: str
    path: Path
    purpose: str  # "research", "coding", "verification"
    active: bool = False


@dataclass
class SkillDevelopmentSession:
    """A complete skill development session."""
    library_name: str
    repo_url: str
    started_at: datetime = field(default_factory=datetime.now)

    # Paths
    base_path: Path = field(default_factory=lambda: Path.cwd())
    repo_path: Optional[Path] = None
    codewiki_path: Optional[Path] = None

    # Worktrees for parallel agents
    worktrees: Dict[str, WorktreeConfig] = field(default_factory=dict)

    # Phase tracking
    current_phase: SkillPhase = SkillPhase.CRAWL
    phase_history: List[Dict[str, Any]] = field(default_factory=list)

    # Results
    understanding_nodes: int = 0
    skills_generated: int = 0
    verification_passed: bool = False


class GitWorktreeManager:
    """
    Manages git worktrees for parallel agent execution.

    Each worktree is an isolated working directory that shares
    the git history. This allows multiple agents to work on
    different branches simultaneously.
    """

    def __init__(self, repo_path: Path):
        self.repo_path = repo_path
        self.worktrees_dir = repo_path.parent / "worktrees"
        self.active_worktrees: Dict[str, WorktreeConfig] = {}

    def create_worktree(self, name: str, branch: str, purpose: str) -> WorktreeConfig:
        """Create a new worktree for an agent."""
        worktree_path = self.worktrees_dir / name

        # Ensure worktrees directory exists
        self.worktrees_dir.mkdir(exist_ok=True)

        # Create branch if it doesn't exist
        try:
            subprocess.run(
                ["git", "branch", branch],
                cwd=self.repo_path,
                capture_output=True,
                check=False  # Branch might already exist
            )
        except:
            pass

        # Create worktree
        if not worktree_path.exists():
            result = subprocess.run(
                ["git", "worktree", "add", str(worktree_path), branch],
                cwd=self.repo_path,
                capture_output=True,
                text=True
            )
            if result.returncode != 0:
                # Try with -B to force create branch
                subprocess.run(
                    ["git", "worktree", "add", "-B", branch, str(worktree_path)],
                    cwd=self.repo_path,
                    capture_output=True
                )

        config = WorktreeConfig(
            name=name,
            branch=branch,
            path=worktree_path,
            purpose=purpose,
            active=True
        )
        self.active_worktrees[name] = config
        return config

    def remove_worktree(self, name: str) -> bool:
        """Remove a worktree."""
        config = self.active_worktrees.get(name)
        if not config:
            return False

        subprocess.run(
            ["git", "worktree", "remove", str(config.path)],
            cwd=self.repo_path,
            capture_output=True
        )
        del self.active_worktrees[name]
        return True

    def list_worktrees(self) -> List[Dict[str, str]]:
        """List all worktrees."""
        result = subprocess.run(
            ["git", "worktree", "list", "--porcelain"],
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )

        worktrees = []
        current = {}
        for line in result.stdout.split('\n'):
            if line.startswith('worktree '):
                if current:
                    worktrees.append(current)
                current = {'path': line[9:]}
            elif line.startswith('HEAD '):
                current['head'] = line[5:]
            elif line.startswith('branch '):
                current['branch'] = line[7:]

        if current:
            worktrees.append(current)

        return worktrees


class SkillDeveloper:
    """
    Main orchestrator for skill development.

    Coordinates:
    - Progressive Disclosure for understanding
    - Claude Hierarchy for intelligence routing
    - Git Worktrees for parallel work
    """

    def __init__(self, base_path: Path = None):
        self.base_path = base_path or Path.cwd()
        self.sessions: Dict[str, SkillDevelopmentSession] = {}

    def start_session(self, library_name: str, repo_url: str) -> SkillDevelopmentSession:
        """Start a new skill development session."""
        session = SkillDevelopmentSession(
            library_name=library_name,
            repo_url=repo_url,
            base_path=self.base_path,
        )
        self.sessions[library_name] = session
        return session

    def phase_crawl(self, session: SkillDevelopmentSession) -> Dict[str, Any]:
        """
        Phase 1: Crawl - Get documentation

        Uses: Brightdata for CodeWiki (if JS) or direct clone
        Output: Raw documentation in crawl_output/
        """
        session.current_phase = SkillPhase.CRAWL

        result = {
            "phase": "crawl",
            "status": "pending",
            "actions": []
        }

        # Clone repository
        repo_path = self.base_path / f"{session.library_name}_repo"
        if not repo_path.exists():
            result["actions"].append(f"git clone {session.repo_url} {repo_path}")

        session.repo_path = repo_path

        # Set up CodeWiki output path
        codewiki_path = self.base_path / "crawl_output" / session.library_name
        codewiki_path.mkdir(parents=True, exist_ok=True)
        session.codewiki_path = codewiki_path

        result["status"] = "ready"
        result["repo_path"] = str(repo_path)
        result["codewiki_path"] = str(codewiki_path)

        session.phase_history.append(result)
        return result

    def phase_understand(self, session: SkillDevelopmentSession) -> Dict[str, Any]:
        """
        Phase 2: Understand - Build progressive disclosure

        Uses: ProgressiveUnderstandingBuilder
        Output: 6-level understanding tree
        """
        session.current_phase = SkillPhase.UNDERSTAND

        result = {
            "phase": "understand",
            "status": "pending",
            "levels": {}
        }

        # This would use our progressive disclosure builder
        # For now, indicate the process
        result["actions"] = [
            "Build Level 0: Executive Summary from README",
            "Build Level 1: Concept Map (topic categories)",
            "Build Level 2: Detailed Sections with source refs",
            "Build Level 3: Validate source references",
            "Build Level 4: Extract semantic info (AST/LSP)",
            "Build Level 5: Generate execution proofs",
        ]

        result["status"] = "ready"
        session.phase_history.append(result)
        return result

    def phase_develop(self, session: SkillDevelopmentSession) -> Dict[str, Any]:
        """
        Phase 3: Develop - Generate skill code

        Uses: Claude Hierarchy
        - Opus: Design skill architecture (if complex)
        - Sonnet: Prepare context from progressive disclosure
        - Haiku: Generate actual skill code

        Output: Skill files in skills/
        """
        session.current_phase = SkillPhase.DEVELOP

        result = {
            "phase": "develop",
            "status": "pending",
            "agents": []
        }

        # Set up worktrees for parallel agents
        if session.repo_path and session.repo_path.exists():
            wt_manager = GitWorktreeManager(session.repo_path)

            # Create worktrees for each agent type
            session.worktrees["researcher"] = wt_manager.create_worktree(
                name="agent_researcher",
                branch="research/skill-development",
                purpose="research"
            )
            result["agents"].append({
                "name": "researcher",
                "tier": "SONNET",
                "purpose": "Search and prepare context"
            })

            session.worktrees["coder"] = wt_manager.create_worktree(
                name="agent_coder",
                branch="develop/skill-implementation",
                purpose="coding"
            )
            result["agents"].append({
                "name": "coder",
                "tier": "HAIKU",
                "purpose": "Generate skill code"
            })

            session.worktrees["verifier"] = wt_manager.create_worktree(
                name="agent_verifier",
                branch="verify/skill-testing",
                purpose="verification"
            )
            result["agents"].append({
                "name": "verifier",
                "tier": "SONNET",
                "purpose": "Verify and test skills"
            })

        result["status"] = "ready"
        session.phase_history.append(result)
        return result

    def phase_verify(self, session: SkillDevelopmentSession) -> Dict[str, Any]:
        """
        Phase 4: Verify - Test generated skills

        Uses:
        - Level 5 execution proofs
        - Type checking
        - Unit tests
        - Integration tests

        Output: Verification report
        """
        session.current_phase = SkillPhase.VERIFY

        result = {
            "phase": "verify",
            "status": "pending",
            "checks": []
        }

        result["checks"] = [
            {"name": "Type checking", "command": "mypy skills/"},
            {"name": "Unit tests", "command": "pytest tests/unit/"},
            {"name": "Level 5 proofs", "command": "python -m verify_proofs"},
            {"name": "Integration tests", "command": "pytest tests/integration/"},
        ]

        result["status"] = "ready"
        session.phase_history.append(result)
        return result

    def phase_refine(self, session: SkillDevelopmentSession, issues: List[str]) -> Dict[str, Any]:
        """
        Phase 5: Refine - Fix issues found in verification

        This is the Ralph loop - iterate until success.
        """
        session.current_phase = SkillPhase.REFINE

        result = {
            "phase": "refine",
            "status": "pending",
            "issues_to_fix": issues,
            "approach": []
        }

        # Route issues to appropriate tier
        for issue in issues:
            issue_lower = issue.lower()

            if "architecture" in issue_lower or "design" in issue_lower:
                result["approach"].append({
                    "issue": issue,
                    "tier": "OPUS",
                    "action": "Redesign component"
                })
            elif "type" in issue_lower or "test" in issue_lower:
                result["approach"].append({
                    "issue": issue,
                    "tier": "SONNET",
                    "action": "Analyze and fix"
                })
            else:
                result["approach"].append({
                    "issue": issue,
                    "tier": "HAIKU",
                    "action": "Quick fix"
                })

        result["status"] = "ready"
        session.phase_history.append(result)
        return result

    def run_full_pipeline(
        self,
        library_name: str,
        repo_url: str,
        max_refinements: int = 5
    ) -> Dict[str, Any]:
        """
        Run the complete skill development pipeline.

        Returns comprehensive results.
        """
        pipeline_result = {
            "library": library_name,
            "started": datetime.now().isoformat(),
            "phases": [],
            "success": False
        }

        # Start session
        session = self.start_session(library_name, repo_url)

        # Phase 1: Crawl
        pipeline_result["phases"].append(self.phase_crawl(session))

        # Phase 2: Understand
        pipeline_result["phases"].append(self.phase_understand(session))

        # Phase 3: Develop
        pipeline_result["phases"].append(self.phase_develop(session))

        # Phase 4: Verify
        verify_result = self.phase_verify(session)
        pipeline_result["phases"].append(verify_result)

        # Phase 5: Refine (Ralph loop)
        refinement_count = 0
        issues = []  # Would come from verification

        while issues and refinement_count < max_refinements:
            refine_result = self.phase_refine(session, issues)
            pipeline_result["phases"].append(refine_result)

            # Re-verify
            verify_result = self.phase_verify(session)
            pipeline_result["phases"].append(verify_result)

            refinement_count += 1
            # In real implementation, check if issues are resolved
            issues = []  # Clear for demo

        pipeline_result["refinements"] = refinement_count
        pipeline_result["success"] = True
        pipeline_result["completed"] = datetime.now().isoformat()

        return pipeline_result


def demonstrate_pipeline():
    """Demonstrate the skill development pipeline."""
    print("=" * 70)
    print("Skill Development Framework")
    print("Tiered Intelligence + Progressive Disclosure + Git Worktrees")
    print("=" * 70)

    developer = SkillDeveloper(Path("/home/user/skills_fabric"))

    # Demonstrate with LangGraph
    print("\n" + "-" * 70)
    print("Starting skill development for: LangGraph")
    print("-" * 70)

    result = developer.run_full_pipeline(
        library_name="langgraph",
        repo_url="https://github.com/langchain-ai/langgraph.git"
    )

    print(f"\nPipeline completed: {result['success']}")
    print(f"Phases executed: {len(result['phases'])}")

    for phase in result['phases']:
        print(f"\n  Phase: {phase['phase'].upper()}")
        print(f"  Status: {phase['status']}")

        if 'agents' in phase:
            for agent in phase['agents']:
                print(f"    Agent: {agent['name']} ({agent['tier']}) - {agent['purpose']}")

        if 'levels' in phase:
            print(f"    Understanding levels: 0-5")

        if 'checks' in phase:
            for check in phase['checks'][:3]:
                print(f"    Check: {check['name']}")


if __name__ == "__main__":
    demonstrate_pipeline()

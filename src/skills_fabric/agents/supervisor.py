"""Supervisor Agent - Orchestrates multi-agent workflow.

The Supervisor coordinates all specialized agents:
- Miner: Source code search
- Linker: PROVEN relationship creation
- Verifier: Trust hierarchy verification
- Writer: Skill output generation

Oh My OpenCode Inspiration:
Like a conductor orchestrating different model agents,
each with their specific strengths and roles.

LangGraph Integration:
Uses StateGraph for structured workflow management.

Model: Sonnet (orchestration and routing)
"""
from dataclasses import dataclass, field
from typing import Any, Optional, Callable
from enum import Enum
from datetime import datetime

from .base import (
    BaseAgent, AgentRole, AgentResult, AgentStatus,
    AgentMessage, AgentConfig
)
from .miner import MinerAgent, MiningTask
from .linker import LinkerAgent, LinkingTask
from .verifier import VerifierAgent, VerificationTask
from .writer import WriterAgent, WritingTask


class WorkflowStage(Enum):
    """Stages in the multi-agent workflow."""
    INIT = "init"
    MINING = "mining"
    LINKING = "linking"
    WRITING = "writing"
    VERIFYING = "verifying"
    STORING = "storing"
    COMPLETE = "complete"
    FAILED = "failed"


@dataclass
class WorkflowState:
    """State passed through the workflow."""
    stage: WorkflowStage = WorkflowStage.INIT
    library_name: str = ""
    repo_path: str = ""

    # Agent outputs
    mined_symbols: list[dict] = field(default_factory=list)
    mined_snippets: list[dict] = field(default_factory=list)
    proven_links: list[dict] = field(default_factory=list)
    skills: list[Any] = field(default_factory=list)
    verified_skills: list[Any] = field(default_factory=list)

    # Metrics
    skills_created: int = 0
    skills_verified: int = 0
    skills_rejected: int = 0

    # Messages
    messages: list[AgentMessage] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class SupervisorResult:
    """Result from supervisor orchestration."""
    success: bool
    final_state: WorkflowState
    agent_results: dict[AgentRole, AgentResult]
    total_duration_ms: float


class SupervisorAgent(BaseAgent[SupervisorResult]):
    """Orchestrates multi-agent skill generation workflow.

    Workflow:
    1. MINING: Miner searches for relevant code
    2. LINKING: Linker creates PROVEN relationships
    3. WRITING: Writer generates skill content
    4. VERIFYING: Verifier checks trust hierarchy
    5. STORING: Store verified skills

    Coordination Pattern:
    - Sequential execution with state passing
    - Message routing between agents
    - Failure escalation and recovery
    - Progress tracking and reporting
    """

    def __init__(self):
        super().__init__(AgentRole.SUPERVISOR)

        # Initialize sub-agents
        self.miner = MinerAgent()
        self.linker = LinkerAgent()
        self.verifier = VerifierAgent()
        self.writer = WriterAgent()

        # Agent configs
        self.configs = {
            AgentRole.MINER: AgentConfig.for_role(AgentRole.MINER),
            AgentRole.LINKER: AgentConfig.for_role(AgentRole.LINKER),
            AgentRole.VERIFIER: AgentConfig.for_role(AgentRole.VERIFIER),
            AgentRole.WRITER: AgentConfig.for_role(AgentRole.WRITER),
        }

    def execute(
        self,
        task: dict,
        context: dict = None
    ) -> AgentResult:
        """Execute the full multi-agent workflow.

        Args:
            task: Dict with 'library_name' and 'repo_path'
            context: Optional shared context

        Returns:
            AgentResult with SupervisorResult
        """
        start = self._start_execution()

        try:
            # Initialize state
            state = WorkflowState(
                library_name=task.get('library_name', ''),
                repo_path=task.get('repo_path', '')
            )

            agent_results = {}

            # Stage 1: Mining
            print(f"[Supervisor] Stage 1: Mining {state.library_name}...")
            state, mining_result = self._run_mining(state)
            agent_results[AgentRole.MINER] = mining_result

            if not mining_result.success:
                state.stage = WorkflowStage.FAILED
                state.errors.append(f"Mining failed: {mining_result.error}")
            else:
                self._collect_messages(mining_result)

            # Stage 2: Linking
            if state.stage != WorkflowStage.FAILED:
                print(f"[Supervisor] Stage 2: Linking concepts to symbols...")
                state, linking_result = self._run_linking(state)
                agent_results[AgentRole.LINKER] = linking_result

                if not linking_result.success:
                    state.errors.append(f"Linking warning: {linking_result.error}")
                else:
                    self._collect_messages(linking_result)

            # Stage 3: Writing
            if state.stage != WorkflowStage.FAILED:
                print(f"[Supervisor] Stage 3: Writing skills...")
                state, writing_result = self._run_writing(state)
                agent_results[AgentRole.WRITER] = writing_result

                if not writing_result.success:
                    state.errors.append(f"Writing warning: {writing_result.error}")
                else:
                    self._collect_messages(writing_result)

            # Stage 4: Verifying
            if state.stage != WorkflowStage.FAILED and state.skills:
                print(f"[Supervisor] Stage 4: Verifying {len(state.skills)} skills...")
                state, verify_result = self._run_verification(state)
                agent_results[AgentRole.VERIFIER] = verify_result

                if verify_result.success:
                    self._collect_messages(verify_result)

            # Stage 5: Storing
            if state.verified_skills:
                print(f"[Supervisor] Stage 5: Storing {len(state.verified_skills)} verified skills...")
                state = self._run_storing(state)

            # Final state
            state.stage = WorkflowStage.COMPLETE if state.skills_created > 0 else WorkflowStage.FAILED

            duration = (datetime.now() - start).total_seconds() * 1000

            result = SupervisorResult(
                success=state.stage == WorkflowStage.COMPLETE,
                final_state=state,
                agent_results=agent_results,
                total_duration_ms=duration
            )

            return self._end_execution(start, output=result)

        except Exception as e:
            return self._end_execution(start, error=str(e))

    def _run_mining(
        self,
        state: WorkflowState
    ) -> tuple[WorkflowState, AgentResult]:
        """Run mining stage."""
        state.stage = WorkflowStage.MINING

        task = MiningTask(
            query=state.library_name,
            repo_path=state.repo_path,
            max_results=100
        )

        result = self.miner.execute(task)

        if result.success:
            state.mined_symbols = result.output.symbols
            state.mined_snippets = result.output.code_snippets
            print(f"  Found {len(state.mined_symbols)} symbols, {len(state.mined_snippets)} snippets")

        return state, result

    def _run_linking(
        self,
        state: WorkflowState
    ) -> tuple[WorkflowState, AgentResult]:
        """Run linking stage."""
        state.stage = WorkflowStage.LINKING

        # Get concepts from database
        from ..core.database import db
        try:
            res = db.execute("MATCH (c:Concept) RETURN c.name, c.content LIMIT 100")
            concepts = []
            while res.has_next():
                row = res.get_next()
                concepts.append({'name': row[0], 'content': row[1] or ''})
        except Exception:
            concepts = []

        if not concepts:
            # Create concepts from mined symbols
            concepts = [
                {'name': s['name'], 'content': s.get('signature', '')}
                for s in state.mined_symbols[:50]
            ]

        task = LinkingTask(
            concepts=concepts,
            symbols=state.mined_symbols,
            min_confidence=0.5
        )

        result = self.linker.execute(task)

        if result.success:
            state.proven_links = result.output.links
            print(f"  Created {len(state.proven_links)} PROVEN links")

        return state, result

    def _run_writing(
        self,
        state: WorkflowState
    ) -> tuple[WorkflowState, AgentResult]:
        """Run writing stage."""
        state.stage = WorkflowStage.WRITING

        # Generate skills from proven links and snippets
        skills = []

        for link in state.proven_links[:20]:
            # Find matching snippet
            symbol_name = link.get('symbol_name', '')
            file_path = link.get('file_path', '')

            snippet = next(
                (s for s in state.mined_snippets if symbol_name in s.get('snippet', '')),
                None
            )

            source_code = snippet['snippet'] if snippet else ""

            task = WritingTask(
                concept_name=link.get('concept_name', ''),
                symbol_name=symbol_name,
                source_code=source_code,
                file_path=file_path,
                library=state.library_name
            )

            result = self.writer.execute(task)

            if result.success:
                skills.append(result.output.skill)

        state.skills = skills
        print(f"  Generated {len(skills)} skills")

        # Return last result (or create summary)
        return state, AgentResult(
            agent=AgentRole.WRITER,
            status=AgentStatus.SUCCESS,
            output={'skills_count': len(skills)}
        )

    def _run_verification(
        self,
        state: WorkflowState
    ) -> tuple[WorkflowState, AgentResult]:
        """Run verification stage."""
        state.stage = WorkflowStage.VERIFYING

        verified = []
        rejected = 0

        for skill in state.skills:
            task = VerificationTask(skill=skill)
            result = self.verifier.execute(task)

            if result.success and result.output.passed:
                skill.verified = True
                verified.append(skill)
            else:
                rejected += 1

        state.verified_skills = verified
        state.skills_verified = len(verified)
        state.skills_rejected = rejected

        print(f"  Verified: {len(verified)}, Rejected: {rejected}")

        return state, AgentResult(
            agent=AgentRole.VERIFIER,
            status=AgentStatus.SUCCESS,
            output={'verified': len(verified), 'rejected': rejected}
        )

    def _run_storing(self, state: WorkflowState) -> WorkflowState:
        """Store verified skills."""
        state.stage = WorkflowStage.STORING

        from ..store.kuzu_store import KuzuSkillStore

        store = KuzuSkillStore()
        stored = 0

        for skill in state.verified_skills:
            try:
                store.create_skill(skill)
                stored += 1
            except Exception:
                pass

        state.skills_created = stored
        print(f"  Stored: {stored} skills")

        return state

    def _collect_messages(self, result: AgentResult):
        """Collect messages from agent result."""
        for msg in result.messages:
            self._messages.append(msg)

    def run_workflow(
        self,
        library_name: str,
        repo_path: str
    ) -> SupervisorResult:
        """Convenience method to run full workflow.

        Args:
            library_name: Name of the library
            repo_path: Path to the repository

        Returns:
            SupervisorResult with workflow outcome
        """
        result = self.execute({
            'library_name': library_name,
            'repo_path': repo_path
        })

        if result.success:
            return result.output
        else:
            # Create failed result
            return SupervisorResult(
                success=False,
                final_state=WorkflowState(
                    stage=WorkflowStage.FAILED,
                    errors=[result.error]
                ),
                agent_results={},
                total_duration_ms=result.duration_ms
            )

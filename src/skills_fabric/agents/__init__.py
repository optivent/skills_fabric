"""Multi-Agent Orchestration for Skills Fabric.

Inspired by Oh My OpenCode's multi-model agent coordination:
- Different agents handle different tasks
- Supervisor orchestrates workflow
- Model recommendations per agent type
- Message passing between agents

Agents:
- Supervisor: Orchestrates workflow (Sonnet)
- Miner: Source code search (Haiku)
- Linker: PROVEN relationships (Sonnet)
- Verifier: Trust verification (Opus)
- Writer: Skill generation (Sonnet)

Workflow:
    MINING → LINKING → WRITING → VERIFYING → STORING

Usage:
    from skills_fabric.agents import SupervisorAgent

    supervisor = SupervisorAgent()
    result = supervisor.run_workflow("langgraph", "/path/to/repo")

    if result.success:
        print(f"Created {result.final_state.skills_created} skills")
"""
from .base import (
    AgentRole,
    AgentStatus,
    AgentMessage,
    AgentResult,
    AgentConfig,
    BaseAgent,
)
from .miner import MinerAgent, MiningTask, MiningResult
from .linker import LinkerAgent, LinkingTask, LinkingResult
from .verifier import VerifierAgent, VerificationTask, VerificationResult
from .writer import WriterAgent, WritingTask, WritingResult
from .supervisor import (
    SupervisorAgent,
    SupervisorResult,
    WorkflowState,
    WorkflowStage,
)

__all__ = [
    # Base
    "AgentRole",
    "AgentStatus",
    "AgentMessage",
    "AgentResult",
    "AgentConfig",
    "BaseAgent",
    # Miner
    "MinerAgent",
    "MiningTask",
    "MiningResult",
    # Linker
    "LinkerAgent",
    "LinkingTask",
    "LinkingResult",
    # Verifier
    "VerifierAgent",
    "VerificationTask",
    "VerificationResult",
    # Writer
    "WriterAgent",
    "WritingTask",
    "WritingResult",
    # Supervisor
    "SupervisorAgent",
    "SupervisorResult",
    "WorkflowState",
    "WorkflowStage",
]

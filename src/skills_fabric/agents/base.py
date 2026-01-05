"""Base Agent - Foundation for all specialized agents.

Inspired by Oh My OpenCode multi-agent coordination where different
agents handle different tasks based on their specialization.

Agent Philosophy:
- Each agent has a specific role and expertise
- Agents communicate through structured messages
- Supervisor coordinates agent execution
- Failures are escalated, not hidden
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional, TypeVar, Generic
from enum import Enum
from datetime import datetime
import uuid


class AgentRole(Enum):
    """Roles for specialized agents."""
    SUPERVISOR = "supervisor"   # Orchestrates other agents
    MINER = "miner"            # Searches source code
    LINKER = "linker"          # Creates PROVEN relationships
    VERIFIER = "verifier"      # Verifies trust hierarchy
    WRITER = "writer"          # Generates skill output
    RESEARCHER = "researcher"   # Fetches documentation


class AgentStatus(Enum):
    """Status of an agent execution."""
    IDLE = "idle"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass
class AgentMessage:
    """Message passed between agents."""
    id: str = field(default_factory=lambda: uuid.uuid4().hex[:8])
    sender: AgentRole = AgentRole.SUPERVISOR
    recipient: AgentRole = AgentRole.SUPERVISOR
    content: Any = None
    metadata: dict = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

    def reply(self, content: Any, **metadata) -> "AgentMessage":
        """Create a reply message."""
        return AgentMessage(
            sender=self.recipient,
            recipient=self.sender,
            content=content,
            metadata={**self.metadata, **metadata, "reply_to": self.id}
        )


@dataclass
class AgentResult:
    """Result of an agent execution."""
    agent: AgentRole
    status: AgentStatus
    output: Any = None
    error: Optional[str] = None
    duration_ms: float = 0.0
    messages: list[AgentMessage] = field(default_factory=list)

    @property
    def success(self) -> bool:
        return self.status == AgentStatus.SUCCESS


T = TypeVar('T')


class BaseAgent(ABC, Generic[T]):
    """Base class for all agents.

    Each agent:
    1. Has a specific role
    2. Processes messages
    3. Returns structured results
    4. Can communicate with other agents through supervisor
    """

    def __init__(self, role: AgentRole):
        self.role = role
        self.status = AgentStatus.IDLE
        self._messages: list[AgentMessage] = []

    @abstractmethod
    def execute(self, task: Any, context: dict = None) -> AgentResult:
        """Execute the agent's primary task.

        Args:
            task: The task to execute
            context: Shared context from supervisor

        Returns:
            AgentResult with output or error
        """
        pass

    def send_message(self, recipient: AgentRole, content: Any, **metadata) -> AgentMessage:
        """Create a message to send to another agent."""
        msg = AgentMessage(
            sender=self.role,
            recipient=recipient,
            content=content,
            metadata=metadata
        )
        self._messages.append(msg)
        return msg

    def receive_message(self, message: AgentMessage) -> Optional[AgentMessage]:
        """Process a received message and optionally reply.

        Override this method to handle incoming messages.
        """
        return None

    def get_pending_messages(self) -> list[AgentMessage]:
        """Get and clear pending outgoing messages."""
        messages = self._messages
        self._messages = []
        return messages

    def _start_execution(self) -> datetime:
        """Mark execution start."""
        self.status = AgentStatus.RUNNING
        return datetime.now()

    def _end_execution(
        self,
        start_time: datetime,
        output: Any = None,
        error: str = None
    ) -> AgentResult:
        """Mark execution end and create result."""
        duration = (datetime.now() - start_time).total_seconds() * 1000

        if error:
            self.status = AgentStatus.FAILED
            return AgentResult(
                agent=self.role,
                status=AgentStatus.FAILED,
                error=error,
                duration_ms=duration,
                messages=self.get_pending_messages()
            )

        self.status = AgentStatus.SUCCESS
        return AgentResult(
            agent=self.role,
            status=AgentStatus.SUCCESS,
            output=output,
            duration_ms=duration,
            messages=self.get_pending_messages()
        )


@dataclass
class AgentConfig:
    """Configuration for an agent."""
    role: AgentRole
    model: str = "default"  # Model to use (for LLM-backed agents)
    timeout: int = 60       # Timeout in seconds
    max_retries: int = 3    # Max retry attempts
    priority: int = 1       # Execution priority (lower = higher priority)

    # Model recommendations (Oh My OpenCode style)
    MODEL_RECOMMENDATIONS = {
        AgentRole.MINER: "haiku",      # Fast search
        AgentRole.LINKER: "sonnet",    # Reasoning
        AgentRole.VERIFIER: "opus",    # Complex judgment
        AgentRole.WRITER: "sonnet",    # Structured output
        AgentRole.RESEARCHER: "haiku", # Quick fetches
        AgentRole.SUPERVISOR: "sonnet", # Orchestration
    }

    @classmethod
    def for_role(cls, role: AgentRole) -> "AgentConfig":
        """Create config with recommended model for role."""
        return cls(
            role=role,
            model=cls.MODEL_RECOMMENDATIONS.get(role, "sonnet")
        )

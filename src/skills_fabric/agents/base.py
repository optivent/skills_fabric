"""Base Agent - Foundation for all specialized agents.

Inspired by Oh My OpenCode multi-agent coordination where different
agents handle different tasks based on their specialization.

Agent Philosophy:
- Each agent has a specific role and expertise
- Agents communicate through structured messages
- Supervisor coordinates agent execution
- Failures are escalated, not hidden

Observability:
- OpenTelemetry tracing for all agent executions
- Spans include agent role, duration, and result status
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Optional, TypeVar, Generic
from enum import Enum
from datetime import datetime
import uuid

# Import tracing (optional dependency)
try:
    from ..telemetry.tracing import get_tracer, trace_span
    TRACING_AVAILABLE = True
except ImportError:
    TRACING_AVAILABLE = False
    get_tracer = lambda: None
    trace_span = None


class AgentRole(Enum):
    """Roles for specialized agents."""
    SUPERVISOR = "supervisor"   # Orchestrates other agents
    MINER = "miner"            # Searches source code
    LINKER = "linker"          # Creates PROVEN relationships
    VERIFIER = "verifier"      # Verifies trust hierarchy
    WRITER = "writer"          # Generates skill output
    RESEARCHER = "researcher"   # Fetches documentation
    AUDITOR = "auditor"        # Verifies content against source (zero-hallucination)


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
    5. Has OpenTelemetry tracing for observability
    """

    def __init__(self, role: AgentRole):
        self.role = role
        self.status = AgentStatus.IDLE
        self._messages: list[AgentMessage] = []
        self._tracer = get_tracer() if TRACING_AVAILABLE else None
        self._current_span = None

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
        """Mark execution start and begin trace span."""
        self.status = AgentStatus.RUNNING

        # Start tracing span
        if self._tracer:
            self._current_span = self._tracer.start_span(
                f"agent.{self.role.value}.execute"
            )
            self._current_span.set_attribute("agent.role", self.role.value)
            self._current_span.set_attribute("agent.class", self.__class__.__name__)

        return datetime.now()

    def _end_execution(
        self,
        start_time: datetime,
        output: Any = None,
        error: str = None
    ) -> AgentResult:
        """Mark execution end, close trace span, and create result."""
        duration = (datetime.now() - start_time).total_seconds() * 1000

        # Update trace span
        if self._current_span:
            self._current_span.set_attribute("duration_ms", duration)

            if error:
                from opentelemetry.trace import Status, StatusCode
                self._current_span.set_status(Status(StatusCode.ERROR, error))
                self._current_span.set_attribute("error", True)
            else:
                from opentelemetry.trace import Status, StatusCode
                self._current_span.set_status(Status(StatusCode.OK))
                self._current_span.set_attribute("error", False)

                # Add output attributes if available
                if hasattr(output, 'passed'):
                    self._current_span.set_attribute("result.passed", output.passed)
                if hasattr(output, 'hallucination_rate'):
                    self._current_span.set_attribute("result.hall_m", output.hallucination_rate)

            self._current_span.end()
            self._current_span = None

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
        AgentRole.AUDITOR: "opus",     # Critical verification (zero-hallucination)
    }

    @classmethod
    def for_role(cls, role: AgentRole) -> "AgentConfig":
        """Create config with recommended model for role."""
        return cls(
            role=role,
            model=cls.MODEL_RECOMMENDATIONS.get(role, "sonnet")
        )

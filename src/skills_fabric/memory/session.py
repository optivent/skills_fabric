"""Session Memory - Track learning across sessions.

Supermemory-inspired features:
- Persist learnings across CLI sessions
- Track failures and successful patterns
- Resume context from previous sessions
- Session-specific strategy adjustments
"""
from dataclasses import dataclass, field
from typing import Optional, Any
from datetime import datetime
import json
from pathlib import Path
import uuid


@dataclass
class SessionRecord:
    """Record of a generation session."""
    session_id: str
    started_at: datetime
    ended_at: Optional[datetime] = None
    library: str = ""
    skills_created: int = 0
    skills_verified: int = 0
    skills_rejected: int = 0
    iterations: int = 0
    strategy_adjustments: list[dict] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    notes: str = ""

    def to_dict(self) -> dict:
        return {
            "session_id": self.session_id,
            "started_at": self.started_at.isoformat(),
            "ended_at": self.ended_at.isoformat() if self.ended_at else None,
            "library": self.library,
            "skills_created": self.skills_created,
            "skills_verified": self.skills_verified,
            "skills_rejected": self.skills_rejected,
            "iterations": self.iterations,
            "strategy_adjustments": self.strategy_adjustments,
            "errors": self.errors,
            "notes": self.notes
        }

    @classmethod
    def from_dict(cls, data: dict) -> "SessionRecord":
        return cls(
            session_id=data["session_id"],
            started_at=datetime.fromisoformat(data["started_at"]),
            ended_at=datetime.fromisoformat(data["ended_at"]) if data.get("ended_at") else None,
            library=data.get("library", ""),
            skills_created=data.get("skills_created", 0),
            skills_verified=data.get("skills_verified", 0),
            skills_rejected=data.get("skills_rejected", 0),
            iterations=data.get("iterations", 0),
            strategy_adjustments=data.get("strategy_adjustments", []),
            errors=data.get("errors", []),
            notes=data.get("notes", "")
        )


class SessionMemory:
    """Manages session history and cross-session learning.

    Features:
    - Persist session records to JSON file
    - Track patterns across sessions
    - Resume from previous session context
    - Learn optimal strategies over time

    Usage:
        memory = SessionMemory()

        # Start new session
        session = memory.start_session("langgraph")

        # During session
        memory.record_skill_created(session.session_id)
        memory.record_failure(session.session_id, "Source not found")

        # End session
        memory.end_session(session.session_id)

        # Later: get insights
        best_strategy = memory.get_best_strategy("langgraph")
    """

    def __init__(self, storage_path: Path = None):
        self.storage_path = storage_path or Path.home() / ".skills_fabric" / "sessions.json"
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        self._sessions: dict[str, SessionRecord] = {}
        self._load()

    def _load(self) -> None:
        """Load sessions from storage."""
        if self.storage_path.exists():
            try:
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    for session_data in data.get("sessions", []):
                        session = SessionRecord.from_dict(session_data)
                        self._sessions[session.session_id] = session
            except Exception:
                self._sessions = {}

    def _save(self) -> None:
        """Save sessions to storage."""
        try:
            data = {
                "sessions": [s.to_dict() for s in self._sessions.values()]
            }
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception:
            pass

    def start_session(self, library: str = "") -> SessionRecord:
        """Start a new generation session."""
        session = SessionRecord(
            session_id=f"session-{uuid.uuid4().hex[:8]}",
            started_at=datetime.now(),
            library=library
        )
        self._sessions[session.session_id] = session
        self._save()
        return session

    def end_session(self, session_id: str) -> Optional[SessionRecord]:
        """End a session and save final state."""
        if session_id in self._sessions:
            session = self._sessions[session_id]
            session.ended_at = datetime.now()
            self._save()
            return session
        return None

    def get_session(self, session_id: str) -> Optional[SessionRecord]:
        """Get a session by ID."""
        return self._sessions.get(session_id)

    def record_skill_created(self, session_id: str) -> None:
        """Record a skill was created in this session."""
        if session_id in self._sessions:
            self._sessions[session_id].skills_created += 1
            self._save()

    def record_skill_verified(self, session_id: str) -> None:
        """Record a skill was verified in this session."""
        if session_id in self._sessions:
            self._sessions[session_id].skills_verified += 1
            self._save()

    def record_skill_rejected(self, session_id: str) -> None:
        """Record a skill was rejected in this session."""
        if session_id in self._sessions:
            self._sessions[session_id].skills_rejected += 1
            self._save()

    def record_failure(self, session_id: str, error: str) -> None:
        """Record a failure in this session."""
        if session_id in self._sessions:
            self._sessions[session_id].errors.append(error)
            self._save()

    def record_iteration(self, session_id: str) -> None:
        """Record an iteration in this session."""
        if session_id in self._sessions:
            self._sessions[session_id].iterations += 1
            self._save()

    def record_strategy_adjustment(
        self,
        session_id: str,
        adjustment: dict
    ) -> None:
        """Record a strategy adjustment made during session."""
        if session_id in self._sessions:
            self._sessions[session_id].strategy_adjustments.append({
                "timestamp": datetime.now().isoformat(),
                **adjustment
            })
            self._save()

    def get_recent_sessions(
        self,
        library: str = None,
        limit: int = 10
    ) -> list[SessionRecord]:
        """Get recent sessions, optionally filtered by library."""
        sessions = list(self._sessions.values())

        if library:
            sessions = [s for s in sessions if s.library == library]

        sessions.sort(key=lambda s: s.started_at, reverse=True)
        return sessions[:limit]

    def get_best_strategy(self, library: str) -> dict:
        """Get the best strategy based on successful sessions.

        Analyzes past sessions for the library to find
        patterns that led to successful skill generation.
        """
        sessions = self.get_recent_sessions(library=library, limit=20)

        if not sessions:
            return {"search_depth": 1, "min_confidence": 0.7}

        # Find sessions with best success rate
        successful = [s for s in sessions if s.skills_verified > 0]

        if not successful:
            return {"search_depth": 2, "min_confidence": 0.6}

        # Aggregate successful strategy adjustments
        strategy = {
            "search_depth": 1,
            "min_confidence": 0.7,
            "require_exact_match": False
        }

        for session in successful:
            for adj in session.strategy_adjustments:
                if adj.get("search_depth"):
                    strategy["search_depth"] = max(
                        strategy["search_depth"],
                        adj["search_depth"]
                    )
                if adj.get("min_confidence"):
                    strategy["min_confidence"] = min(
                        strategy["min_confidence"],
                        adj["min_confidence"]
                    )

        return strategy

    def get_failure_patterns(self, library: str = None) -> dict[str, int]:
        """Get common failure patterns across sessions."""
        sessions = self.get_recent_sessions(library=library, limit=50)

        patterns = {}
        for session in sessions:
            for error in session.errors:
                # Normalize error messages
                key = error.lower()[:50]
                patterns[key] = patterns.get(key, 0) + 1

        # Sort by frequency
        return dict(sorted(patterns.items(), key=lambda x: x[1], reverse=True)[:10])

    def get_statistics(self, library: str = None) -> dict:
        """Get aggregate statistics across sessions."""
        sessions = self.get_recent_sessions(library=library, limit=100)

        if not sessions:
            return {
                "total_sessions": 0,
                "total_skills": 0,
                "total_verified": 0,
                "total_rejected": 0,
                "avg_iterations": 0,
                "success_rate": 0
            }

        total_skills = sum(s.skills_created for s in sessions)
        total_verified = sum(s.skills_verified for s in sessions)
        total_rejected = sum(s.skills_rejected for s in sessions)
        total_iterations = sum(s.iterations for s in sessions)
        successful_sessions = sum(1 for s in sessions if s.skills_verified > 0)

        return {
            "total_sessions": len(sessions),
            "total_skills": total_skills,
            "total_verified": total_verified,
            "total_rejected": total_rejected,
            "avg_iterations": total_iterations / len(sessions) if sessions else 0,
            "success_rate": successful_sessions / len(sessions) if sessions else 0
        }

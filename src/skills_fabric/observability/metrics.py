"""Metrics - Production metrics for Skills Fabric.

Tracks key performance indicators:
- Skill generation duration
- Verification pass rate
- Trust level distribution
- Ralph Wiggum iterations
- Failure type counts

Supports multiple backends:
- In-memory (default)
- Prometheus (optional)
- StatsD (optional)
"""
from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime
from enum import Enum
from collections import defaultdict
import threading


class MetricType(Enum):
    """Types of metrics."""
    COUNTER = "counter"      # Monotonically increasing
    GAUGE = "gauge"          # Point-in-time value
    HISTOGRAM = "histogram"  # Distribution of values
    TIMER = "timer"          # Duration measurements


@dataclass
class MetricValue:
    """A metric measurement."""
    name: str
    type: MetricType
    value: float
    labels: dict = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)


class MetricsRegistry:
    """Thread-safe metrics registry.

    Usage:
        metrics = MetricsRegistry()

        # Counter
        metrics.increment("skills_created", labels={"library": "langgraph"})

        # Gauge
        metrics.gauge("active_sessions", 5)

        # Timer
        with metrics.timer("skill_generation_duration"):
            generate_skill()

        # Histogram
        metrics.histogram("iterations_to_success", 3)
    """

    def __init__(self):
        self._lock = threading.Lock()
        self._counters: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
        self._gauges: dict[str, dict[str, float]] = defaultdict(lambda: defaultdict(float))
        self._histograms: dict[str, dict[str, list]] = defaultdict(lambda: defaultdict(list))
        self._timers: dict[str, dict[str, list]] = defaultdict(lambda: defaultdict(list))

    def _labels_key(self, labels: dict) -> str:
        """Convert labels dict to string key."""
        if not labels:
            return ""
        return ",".join(f"{k}={v}" for k, v in sorted(labels.items()))

    def increment(
        self,
        name: str,
        value: float = 1.0,
        labels: dict = None
    ) -> None:
        """Increment a counter."""
        labels = labels or {}
        key = self._labels_key(labels)
        with self._lock:
            self._counters[name][key] += value

    def gauge(
        self,
        name: str,
        value: float,
        labels: dict = None
    ) -> None:
        """Set a gauge value."""
        labels = labels or {}
        key = self._labels_key(labels)
        with self._lock:
            self._gauges[name][key] = value

    def histogram(
        self,
        name: str,
        value: float,
        labels: dict = None
    ) -> None:
        """Record a value in a histogram."""
        labels = labels or {}
        key = self._labels_key(labels)
        with self._lock:
            self._histograms[name][key].append(value)

    def timer(self, name: str, labels: dict = None) -> "TimerContext":
        """Create a timer context manager."""
        return TimerContext(self, name, labels or {})

    def record_duration(
        self,
        name: str,
        duration_ms: float,
        labels: dict = None
    ) -> None:
        """Record a duration in milliseconds."""
        labels = labels or {}
        key = self._labels_key(labels)
        with self._lock:
            self._timers[name][key].append(duration_ms)

    def get_counter(self, name: str, labels: dict = None) -> float:
        """Get counter value."""
        key = self._labels_key(labels or {})
        with self._lock:
            return self._counters[name][key]

    def get_gauge(self, name: str, labels: dict = None) -> float:
        """Get gauge value."""
        key = self._labels_key(labels or {})
        with self._lock:
            return self._gauges[name][key]

    def get_histogram_stats(self, name: str, labels: dict = None) -> dict:
        """Get histogram statistics."""
        key = self._labels_key(labels or {})
        with self._lock:
            values = self._histograms[name][key]
            if not values:
                return {"count": 0}
            return {
                "count": len(values),
                "sum": sum(values),
                "min": min(values),
                "max": max(values),
                "avg": sum(values) / len(values),
                "p50": sorted(values)[len(values) // 2],
                "p95": sorted(values)[int(len(values) * 0.95)] if len(values) >= 20 else max(values),
            }

    def get_all_metrics(self) -> dict:
        """Get all metrics as a dictionary."""
        with self._lock:
            return {
                "counters": dict(self._counters),
                "gauges": dict(self._gauges),
                "histograms": {
                    name: {k: self._compute_stats(v) for k, v in labels.items()}
                    for name, labels in self._histograms.items()
                },
                "timers": {
                    name: {k: self._compute_stats(v) for k, v in labels.items()}
                    for name, labels in self._timers.items()
                }
            }

    def _compute_stats(self, values: list) -> dict:
        """Compute statistics for a list of values."""
        if not values:
            return {"count": 0}
        sorted_values = sorted(values)
        return {
            "count": len(values),
            "sum": sum(values),
            "min": min(values),
            "max": max(values),
            "avg": sum(values) / len(values),
            "p50": sorted_values[len(values) // 2],
        }

    def reset(self) -> None:
        """Reset all metrics."""
        with self._lock:
            self._counters.clear()
            self._gauges.clear()
            self._histograms.clear()
            self._timers.clear()


class TimerContext:
    """Context manager for timing operations."""

    def __init__(self, registry: MetricsRegistry, name: str, labels: dict):
        self.registry = registry
        self.name = name
        self.labels = labels
        self.start_time: Optional[datetime] = None

    def __enter__(self):
        self.start_time = datetime.now()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            duration_ms = (datetime.now() - self.start_time).total_seconds() * 1000
            self.registry.record_duration(self.name, duration_ms, self.labels)
        return False


# Global metrics instance
_metrics = MetricsRegistry()


def get_metrics() -> MetricsRegistry:
    """Get the global metrics registry."""
    return _metrics


# =============================================================================
# Predefined Metrics for Skills Fabric
# =============================================================================

class SkillsMetrics:
    """Predefined metrics for Skills Fabric.

    Standard metrics:
    - skills_generated_total: Total skills generated
    - skills_verified_total: Total skills that passed verification
    - skills_rejected_total: Total skills rejected (Trust Level 3)
    - skill_generation_duration_ms: Time to generate a skill
    - verification_duration_ms: Time to verify a skill
    - ralph_wiggum_iterations: Iterations until success
    - trust_level_distribution: Distribution across trust levels
    """

    def __init__(self, registry: MetricsRegistry = None):
        self.registry = registry or get_metrics()

    def skill_generated(self, library: str = ""):
        """Record a skill was generated."""
        self.registry.increment("skills_generated_total", labels={"library": library})

    def skill_verified(self, library: str = "", trust_level: int = 2):
        """Record a skill passed verification."""
        self.registry.increment("skills_verified_total", labels={
            "library": library,
            "trust_level": str(trust_level)
        })

    def skill_rejected(self, library: str = "", reason: str = ""):
        """Record a skill was rejected."""
        self.registry.increment("skills_rejected_total", labels={
            "library": library,
            "reason": reason[:50]
        })

    def generation_duration(self, library: str = "") -> TimerContext:
        """Time skill generation."""
        return self.registry.timer("skill_generation_duration_ms", {"library": library})

    def verification_duration(self) -> TimerContext:
        """Time skill verification."""
        return self.registry.timer("verification_duration_ms")

    def record_iterations(self, iterations: int, library: str = ""):
        """Record Ralph Wiggum iterations to success."""
        self.registry.histogram("ralph_wiggum_iterations", iterations, {"library": library})

    def record_trust_level(self, trust_level: int):
        """Record trust level for distribution tracking."""
        self.registry.increment("trust_level_distribution", labels={"level": str(trust_level)})

    def active_sessions(self, count: int):
        """Set number of active sessions."""
        self.registry.gauge("active_sessions", count)

    def get_summary(self) -> dict:
        """Get metrics summary."""
        return {
            "skills_generated": self.registry.get_counter("skills_generated_total"),
            "skills_verified": self.registry.get_counter("skills_verified_total"),
            "skills_rejected": self.registry.get_counter("skills_rejected_total"),
            "generation_stats": self.registry.get_histogram_stats("skill_generation_duration_ms"),
            "iteration_stats": self.registry.get_histogram_stats("ralph_wiggum_iterations"),
        }

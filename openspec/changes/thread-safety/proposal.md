# Proposal: Fix HallMetric Thread Safety

> OpenSpec Change Proposal
> ID: TASK-003 | Priority: P0 (Critical) | BMAD Track: Quick Flow

## Problem Statement

The `HallMetric` class uses global state that is not thread-safe. In concurrent scenarios (parallel batch processing), this can lead to incorrect hallucination rate calculations.

## Current State

```python
# src/skills_fabric/verify/ddr/__init__.py
# Global instance - NOT thread-safe
hall_metric = HallMetric(threshold=0.02)

class DirectDependencyRetriever:
    def retrieve(self, query):
        # Uses global hall_metric
        hall_metric.record(validated=..., rejected=...)
```

## Problem Scenario

```python
# Thread 1: Processing batch A
hall_metric.record(validated=10, rejected=0)  # Hall_m = 0.0

# Thread 2: Processing batch B (concurrent)
hall_metric.record(validated=5, rejected=5)   # Hall_m = 0.33

# Result: Metrics are mixed, neither thread has accurate data
```

## Proposed Solution

Use `contextvars` for thread-local metric tracking:

```python
import contextvars

_hall_metric_var: contextvars.ContextVar[HallMetric] = contextvars.ContextVar(
    'hall_metric',
    default=None
)

def get_hall_metric() -> HallMetric:
    """Get thread-local HallMetric instance."""
    metric = _hall_metric_var.get()
    if metric is None:
        metric = HallMetric(threshold=0.02)
        _hall_metric_var.set(metric)
    return metric

def reset_hall_metric() -> None:
    """Reset thread-local HallMetric (useful for tests)."""
    _hall_metric_var.set(None)
```

## Alternative: Instance-Scoped

```python
class DirectDependencyRetriever:
    def __init__(self, ...):
        self.hall_metric = HallMetric(threshold=0.02)  # Instance, not global
```

## Acceptance Criteria

- [ ] HallMetric is thread-safe
- [ ] Concurrent batch processing gives correct per-thread metrics
- [ ] Existing single-threaded behavior unchanged
- [ ] Thread safety tests added
- [ ] No performance regression

## Files to Modify

```
src/skills_fabric/verify/ddr/__init__.py  # Add contextvars
tests/test_ddr.py                          # Add concurrency tests
```

## Test Cases

```python
@pytest.mark.asyncio
async def test_concurrent_hall_metric():
    """Verify thread-local metrics don't interfere."""
    async def process_batch(batch_id, validated, rejected):
        metric = get_hall_metric()
        metric.record(validated=validated, rejected=rejected)
        return metric.current_hall_m

    # Run concurrently
    results = await asyncio.gather(
        process_batch("A", 10, 0),   # Should be 0.0
        process_batch("B", 5, 5),    # Should be 0.5
    )

    assert results[0] == 0.0   # Thread A isolated
    assert results[1] == 0.5   # Thread B isolated
```

## Estimated Effort

3 story points (~4-6 hours)

## BMAD Agent

Developer Agent perspective - code correctness.

---

*Proposal created from BMAD analysis. See `docs/bmad/agent-analysis.md` for details.*

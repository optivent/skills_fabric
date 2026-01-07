# Tasks: Fix HallMetric Thread Safety

> OpenSpec Task Breakdown
> Proposal: thread-safety | Status: Ready

## Task List

### Implementation

- [ ] Add `contextvars` import to `ddr/__init__.py`
- [ ] Create `_hall_metric_var` context variable
- [ ] Implement `get_hall_metric()` function
- [ ] Implement `reset_hall_metric()` function
- [ ] Update `DirectDependencyRetriever` to use `get_hall_metric()`
- [ ] Update any other code using global `hall_metric`

### Testing

- [ ] Add `test_hall_metric_thread_isolation` test
- [ ] Add `test_concurrent_batch_processing` test
- [ ] Add `test_reset_hall_metric` test
- [ ] Verify existing tests still pass

### Documentation

- [ ] Update docstrings with thread-safety guarantees
- [ ] Add usage example for concurrent scenarios

## Code Changes

### Step 1: Add contextvars

```python
# At top of src/skills_fabric/verify/ddr/__init__.py
import contextvars

_hall_metric_var: contextvars.ContextVar[Optional[HallMetric]] = contextvars.ContextVar(
    'hall_metric',
    default=None
)
```

### Step 2: Add accessor functions

```python
def get_hall_metric(threshold: float = 0.02) -> HallMetric:
    """Get thread-local HallMetric instance.

    Creates a new instance if none exists in current context.
    Thread-safe for concurrent operations.
    """
    metric = _hall_metric_var.get()
    if metric is None:
        metric = HallMetric(threshold=threshold)
        _hall_metric_var.set(metric)
    return metric

def reset_hall_metric() -> None:
    """Reset thread-local HallMetric.

    Useful for tests and starting fresh calculations.
    """
    _hall_metric_var.set(None)
```

### Step 3: Update DDR usage

```python
class DirectDependencyRetriever:
    def __init__(self, ...):
        # Remove: self.hall_metric = hall_metric (global)
        # Use get_hall_metric() in methods instead

    @property
    def hall_metric(self) -> HallMetric:
        return get_hall_metric(threshold=self._threshold)
```

## Verification

```bash
# Run all DDR tests
pytest tests/test_ddr.py -v

# Run with concurrency
pytest tests/test_ddr.py -v -k "concurrent or thread"
```

## Definition of Done

- [ ] contextvars implementation complete
- [ ] All existing tests pass
- [ ] Concurrency tests added and passing
- [ ] No performance regression
- [ ] Code reviewed

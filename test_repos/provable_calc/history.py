"""History tracking with provable properties."""
from dataclasses import dataclass, field
from typing import List, Tuple
from datetime import datetime


@dataclass
class Operation:
    """A recorded operation.

    Provable Properties:
    - Has exactly 3 fields: name, args, timestamp
    - timestamp is auto-set if not provided
    """
    name: str
    args: Tuple
    timestamp: datetime = field(default_factory=datetime.now)


class History:
    """Tracks operation history.

    Provable Properties:
    - P1: __init__ creates empty history (len == 0)
    - P2: record(op) increases len by exactly 1
    - P3: record preserves order (FIFO)
    - P4: clear() sets len to 0
    - P5: get_all() returns copy, not reference
    """

    def __init__(self) -> None:
        """Initialize empty history."""
        self._operations: List[Operation] = []

    def record(self, name: str, *args) -> None:
        """Record an operation.

        Property: len(history) increases by 1
        Property: new operation is at end of list
        """
        self._operations.append(Operation(name=name, args=args))

    def get_all(self) -> List[Operation]:
        """Get all operations (copy).

        Property: returns new list, not internal reference
        Property: modifications to returned list don't affect history
        """
        return list(self._operations)

    def clear(self) -> None:
        """Clear all history.

        Property: after clear(), len == 0
        """
        self._operations = []

    def __len__(self) -> int:
        """Return number of operations."""
        return len(self._operations)

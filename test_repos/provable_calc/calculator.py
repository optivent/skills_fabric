"""Calculator with provable properties.

Every method in this class has properties that can be
formally verified through execution and static analysis.
"""
from typing import Union

Number = Union[int, float]


class Calculator:
    """A calculator with history tracking.

    Provable Properties:
    - P1: __init__ sets value to 0
    - P2: add(x) increases value by exactly x
    - P3: subtract(x) decreases value by exactly x
    - P4: multiply(x) multiplies value by exactly x
    - P5: divide(0) raises ValueError
    - P6: divide(x) where x != 0 divides value by x
    - P7: reset() sets value to exactly 0
    """

    def __init__(self) -> None:
        """Initialize calculator with value 0."""
        self.value: Number = 0

    def add(self, x: Number) -> Number:
        """Add x to current value.

        Property: result == old_value + x
        """
        self.value = self.value + x
        return self.value

    def subtract(self, x: Number) -> Number:
        """Subtract x from current value.

        Property: result == old_value - x
        """
        self.value = self.value - x
        return self.value

    def multiply(self, x: Number) -> Number:
        """Multiply current value by x.

        Property: result == old_value * x
        """
        self.value = self.value * x
        return self.value

    def divide(self, x: Number) -> Number:
        """Divide current value by x.

        Property: x == 0 raises ValueError
        Property: x != 0 implies result == old_value / x
        """
        if x == 0:
            raise ValueError("Cannot divide by zero")
        self.value = self.value / x
        return self.value

    def reset(self) -> None:
        """Reset value to 0.

        Property: after reset(), value == 0
        """
        self.value = 0

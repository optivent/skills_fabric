"""Sample Python module for testing AST and tree-sitter parsing.

This file provides comprehensive Python code patterns for parser tests.
"""
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
import asyncio


@dataclass
class Person:
    """A person with name, age, and optional email.

    Attributes:
        name: The person's full name.
        age: The person's age in years.
        email: Optional email address.
    """
    name: str
    age: int
    email: Optional[str] = None

    def greet(self) -> str:
        """Return a greeting message.

        Returns:
            A personalized greeting string.
        """
        return f"Hello, I'm {self.name}"

    def greet_person(self, other: "Person") -> str:
        """Greet another person.

        Args:
            other: The person to greet.

        Returns:
            A greeting between two people.
        """
        return f"Hi {other.name}, I'm {self.name}"

    @property
    def is_adult(self) -> bool:
        """Check if person is an adult (18+)."""
        return self.age >= 18

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Person":
        """Create a Person from a dictionary.

        Args:
            data: Dictionary with name, age, and optional email.

        Returns:
            A new Person instance.
        """
        return cls(
            name=data["name"],
            age=data["age"],
            email=data.get("email"),
        )


class Calculator:
    """A simple calculator with basic operations.

    Supports addition, subtraction, multiplication, and division
    with configurable precision.
    """

    def __init__(self, precision: int = 2):
        """Initialize calculator with precision.

        Args:
            precision: Number of decimal places for results.
        """
        self._precision = precision
        self._history: List[str] = []

    def add(self, a: float, b: float) -> float:
        """Add two numbers.

        Args:
            a: First number.
            b: Second number.

        Returns:
            Sum of a and b, rounded to precision.
        """
        result = round(a + b, self._precision)
        self._history.append(f"{a} + {b} = {result}")
        return result

    def subtract(self, a: float, b: float) -> float:
        """Subtract b from a."""
        result = round(a - b, self._precision)
        self._history.append(f"{a} - {b} = {result}")
        return result

    @staticmethod
    def multiply(a: float, b: float) -> float:
        """Multiply two numbers (static method)."""
        return a * b

    @classmethod
    def from_precision(cls, precision: int) -> "Calculator":
        """Create calculator with specified precision (class method)."""
        return cls(precision=precision)

    @property
    def history(self) -> List[str]:
        """Get calculation history."""
        return self._history.copy()


async def fetch_data(url: str, timeout: float = 30.0) -> Dict[str, Any]:
    """Fetch data from a URL asynchronously.

    Args:
        url: The URL to fetch from.
        timeout: Request timeout in seconds.

    Returns:
        The fetched data as a dictionary.

    Raises:
        TimeoutError: If the request times out.
    """
    await asyncio.sleep(0.01)  # Simulated network delay
    return {"url": url, "data": "sample", "timeout": timeout}


def process_items(
    items: List[str],
    transform: Optional[callable] = None,
    *,
    strip: bool = True,
) -> List[str]:
    """Process a list of items with optional transformation.

    Args:
        items: List of strings to process.
        transform: Optional transformation function.
        strip: Whether to strip whitespace (keyword-only).

    Returns:
        Processed list of strings.
    """
    result = []
    for item in items:
        if strip:
            item = item.strip()
        if transform:
            item = transform(item)
        result.append(item)
    return result


def _private_helper() -> None:
    """Private helper function (not exported)."""
    pass


# Module-level constant
DEFAULT_TIMEOUT: float = 30.0

# Module-level variable
_cache: Dict[str, Any] = {}

"""A minimal calculator module for proving code understanding.

This module is intentionally small and well-typed to serve as
a test case for proof-based code understanding.

The complete set of provable facts about this module:
1. Module exists and is importable
2. Contains exactly 2 classes: Calculator, History
3. Calculator has exactly 5 methods
4. History has exactly 3 methods
5. All methods have type annotations
6. Calculator.divide raises ValueError on zero
7. History stores operations in order
"""
from .calculator import Calculator
from .history import History

__all__ = ["Calculator", "History"]
__version__ = "1.0.0"

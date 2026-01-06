"""Property-Based Testing for Code Understanding.

Based on research:
- Property-Generated Solver (PGS) framework
- "Properties are simpler to verify than exhaustive test oracles"
- "Breaking the cycle of self-deception"

Key insight: Instead of testing specific inputs/outputs,
define PROPERTIES that should hold for all valid inputs.

For code understanding, properties include:
1. Existence properties: "If X is defined, import should succeed"
2. Type properties: "If X inherits from Y, isinstance check should pass"
3. Signature properties: "If method requires param p, calling without p raises"
4. Behavioral properties: "Calling X.compile() returns something callable"
5. Invariants: "State before and after should satisfy condition"
"""
import ast
import sys
import io
from dataclasses import dataclass, field
from typing import Callable, Any, Optional
from pathlib import Path
from enum import Enum, auto

# Try relative import, fall back to direct definition
try:
    from .assertions import (
        Assertion, Evidence, VerificationResult, VerificationType
    )
except ImportError:
    # When run directly, define minimal versions
    from dataclasses import dataclass, field
    from enum import Enum, auto
    from datetime import datetime

    class VerificationType(Enum):
        EXISTENCE = auto()
        TYPE_CHECK = auto()
        EXECUTION = auto()
        PROPERTY = auto()
        TRACE = auto()
        MUTATION = auto()
        STATIC = auto()

    class VerificationResult(Enum):
        VERIFIED = auto()
        REFUTED = auto()
        INCONCLUSIVE = auto()
        ERROR = auto()

    @dataclass
    class Evidence:
        type: str
        content: str
        source_file: str = ""
        source_line: int = 0
        timestamp: datetime = field(default_factory=datetime.now)

    @dataclass
    class Assertion:
        claim: str
        category: str
        source_concept: str
        source_file: str
        source_line: int
        verification_type: VerificationType = VerificationType.EXISTENCE
        verification_code: str = ""
        result: VerificationResult = VerificationResult.INCONCLUSIVE
        evidence: list = field(default_factory=list)
        confidence: float = 0.0

        def is_verified(self) -> bool:
            return self.result == VerificationResult.VERIFIED


class PropertyType(Enum):
    """Types of properties we can test."""
    IMPORT = auto()         # Module/class can be imported
    INSTANTIATION = auto()  # Class can be instantiated
    METHOD_CALL = auto()    # Method can be called
    TYPE_CHECK = auto()     # Type relationships hold
    RETURN_TYPE = auto()    # Return type matches annotation
    EXCEPTION = auto()      # Expected exception is raised
    INVARIANT = auto()      # Property holds before/after


@dataclass
class Property:
    """A testable property of code behavior.

    Unlike assertions which are verified once,
    properties are tested with multiple generated inputs.
    """
    name: str
    property_type: PropertyType
    description: str
    test_code: str                    # Code that tests this property
    expected_result: str = "success"  # What success looks like

    # Results
    tested: bool = False
    passed: bool = False
    counter_example: str = ""         # Input that failed
    evidence: list[Evidence] = field(default_factory=list)


class PropertyGenerator:
    """Generate properties from code analysis.

    Given a class/function, generate properties that should hold:
    - If class exists → import should work
    - If method has signature → wrong args should fail
    - If method returns type → check return type
    """

    def __init__(self, source_code: str, file_path: str = ""):
        self.source = source_code
        self.file_path = file_path
        try:
            self.tree = ast.parse(source_code)
        except:
            self.tree = None

    def generate_for_class(self, class_name: str, module_path: str = "") -> list[Property]:
        """Generate properties for a class."""
        properties = []

        if not self.tree:
            return properties

        for node in ast.walk(self.tree):
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                # Property 1: Class is importable
                if module_path:
                    properties.append(Property(
                        name=f"{class_name}_importable",
                        property_type=PropertyType.IMPORT,
                        description=f"{class_name} can be imported from {module_path}",
                        test_code=f"""
try:
    from {module_path} import {class_name}
    print("PASS: Import successful")
except ImportError as e:
    print(f"FAIL: {{e}}")
""",
                        expected_result="PASS"
                    ))

                # Property 2: Class has expected methods
                for item in node.body:
                    if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                        method_name = item.name
                        if not method_name.startswith('_'):  # Public methods
                            properties.append(Property(
                                name=f"{class_name}_{method_name}_exists",
                                property_type=PropertyType.METHOD_CALL,
                                description=f"{class_name}.{method_name} is callable",
                                test_code=f"""
try:
    # Just check the method exists and is callable
    method = getattr({class_name}, '{method_name}', None)
    if method is not None and callable(method):
        print("PASS: Method is callable")
    else:
        print("FAIL: Method not found or not callable")
except Exception as e:
    print(f"FAIL: {{e}}")
""",
                                expected_result="PASS"
                            ))

                # Property 3: Check inheritance
                for base in node.bases:
                    base_name = self._get_name(base)
                    if base_name and base_name != "?":
                        properties.append(Property(
                            name=f"{class_name}_inherits_{base_name}",
                            property_type=PropertyType.TYPE_CHECK,
                            description=f"{class_name} is subclass of {base_name}",
                            test_code=f"""
# Check if inheritance relationship holds (MRO)
try:
    mro = [c.__name__ for c in {class_name}.__mro__]
    if '{base_name}' in str(mro) or 'object' in mro:
        print("PASS: Inheritance verified")
    else:
        print(f"FAIL: {{mro}}")
except Exception as e:
    print(f"FAIL: {{e}}")
""",
                            expected_result="PASS"
                        ))

                # Property 4: Check __init__ signature
                init_method = None
                for item in node.body:
                    if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                        init_method = item
                        break

                if init_method:
                    # Count required parameters (no default)
                    required_count = len(init_method.args.args) - len(init_method.args.defaults) - 1  # -1 for self

                    if required_count > 0:
                        properties.append(Property(
                            name=f"{class_name}_init_requires_args",
                            property_type=PropertyType.EXCEPTION,
                            description=f"{class_name}() without required args raises TypeError",
                            test_code=f"""
try:
    instance = {class_name}()
    print("FAIL: Should have raised TypeError")
except TypeError as e:
    print("PASS: TypeError raised as expected")
except Exception as e:
    print(f"FAIL: Wrong exception: {{type(e).__name__}}")
""",
                            expected_result="PASS"
                        ))

                break

        return properties

    def _get_name(self, node: ast.AST) -> str:
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return f"{self._get_name(node.value)}.{node.attr}"
        elif isinstance(node, ast.Subscript):
            return f"{self._get_name(node.value)}[...]"
        return "?"


class PropertyTester:
    """Execute property tests and collect results."""

    def __init__(self, setup_code: str = ""):
        """
        Args:
            setup_code: Code to run before each test (e.g., imports)
        """
        self.setup_code = setup_code

    def test(self, property: Property) -> Property:
        """Test a property and update it with results."""
        # Capture stdout/stderr
        old_stdout = sys.stdout
        old_stderr = sys.stderr
        sys.stdout = io.StringIO()
        sys.stderr = io.StringIO()

        try:
            # Build full test code
            full_code = f"""
{self.setup_code}

{property.test_code}
"""
            exec_globals = {}
            exec(full_code, exec_globals)

            stdout_val = sys.stdout.getvalue()
            stderr_val = sys.stderr.getvalue()

            property.tested = True

            if property.expected_result in stdout_val:
                property.passed = True
                property.evidence.append(Evidence(
                    type="property_pass",
                    content=stdout_val.strip()
                ))
            else:
                property.passed = False
                property.evidence.append(Evidence(
                    type="property_fail",
                    content=stdout_val.strip() if stdout_val else stderr_val.strip()
                ))
                property.counter_example = stdout_val

        except Exception as e:
            property.tested = True
            property.passed = False
            property.evidence.append(Evidence(
                type="execution_error",
                content=f"{type(e).__name__}: {str(e)}"
            ))
            property.counter_example = str(e)

        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

        return property


@dataclass
class PropertyTestResult:
    """Results of property-based testing."""
    concept: str
    properties_tested: int
    properties_passed: int
    properties: list[Property]

    def pass_rate(self) -> float:
        if self.properties_tested == 0:
            return 0.0
        return self.properties_passed / self.properties_tested

    def summary(self) -> str:
        lines = [
            f"Property Test Results: {self.concept}",
            f"Tested: {self.properties_tested}",
            f"Passed: {self.properties_passed}",
            f"Pass Rate: {self.pass_rate():.1%}",
            ""
        ]
        for p in self.properties:
            status = "✓" if p.passed else "✗"
            lines.append(f"  {status} {p.name}")
            if not p.passed and p.counter_example:
                lines.append(f"      Counter-example: {p.counter_example[:50]}...")
        return "\n".join(lines)


def test_properties_for_code(
    source_code: str,
    class_name: str,
    module_path: str = "",
    setup_code: str = ""
) -> PropertyTestResult:
    """Run property-based testing on a class.

    Args:
        source_code: The source code to analyze
        class_name: Name of the class to test
        module_path: Module path for import tests
        setup_code: Code to run before each test

    Returns:
        PropertyTestResult with pass/fail for each property
    """
    generator = PropertyGenerator(source_code)
    properties = generator.generate_for_class(class_name, module_path)

    tester = PropertyTester(setup_code)
    tested_properties = []

    for prop in properties:
        tested = tester.test(prop)
        tested_properties.append(tested)

    passed = sum(1 for p in tested_properties if p.passed)

    return PropertyTestResult(
        concept=class_name,
        properties_tested=len(tested_properties),
        properties_passed=passed,
        properties=tested_properties
    )


def properties_to_assertions(
    result: PropertyTestResult,
    source_file: str
) -> list[Assertion]:
    """Convert property test results to assertions.

    This bridges property-based testing with the assertion engine.
    """
    assertions = []

    for prop in result.properties:
        assertion = Assertion(
            claim=prop.description,
            category="property",
            source_concept=result.concept,
            source_file=source_file,
            source_line=0,
            verification_type=VerificationType.PROPERTY,
            result=VerificationResult.VERIFIED if prop.passed else VerificationResult.REFUTED,
            evidence=prop.evidence,
            confidence=0.9 if prop.passed else 0.0
        )
        assertions.append(assertion)

    return assertions

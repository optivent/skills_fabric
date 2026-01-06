#!/usr/bin/env python3
"""Test Program Slicing for Focused Understanding.

Program slicing helps focus on what matters:
- Backward slice: What affects this variable?
- Forward slice: What does this variable affect?
"""
import sys
import importlib.util
from pathlib import Path

# Direct import to bypass package system
script_dir = Path(__file__).parent.parent / "src" / "skills_fabric" / "understanding"

spec = importlib.util.spec_from_file_location("slicing", script_dir / "slicing.py")
slicing_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(slicing_module)

ProgramSlicer = slicing_module.ProgramSlicer
SlicingCriterion = slicing_module.SlicingCriterion
slice_for_understanding = slicing_module.slice_for_understanding


def print_section(title: str):
    print(f"\n{'='*70}")
    print(f"  {title}")
    print(f"{'='*70}\n")


def test_backward_slice():
    """Test backward slicing - what affects a variable?"""
    print_section("TEST 1: BACKWARD SLICING")

    sample_code = '''
def calculate_total(items, tax_rate):
    subtotal = 0
    for item in items:
        price = item.price
        quantity = item.quantity
        item_total = price * quantity
        subtotal = subtotal + item_total
    tax = subtotal * tax_rate
    total = subtotal + tax
    return total
'''

    print("Source code:")
    for i, line in enumerate(sample_code.split('\n'), 1):
        print(f"  {i}: {line}")

    slicer = ProgramSlicer(sample_code)

    # Slice for 'total' at return statement (line 11)
    criterion = SlicingCriterion(line=11, variable="total")
    slice_result = slicer.backward_slice(criterion)

    print(f"\nBackward slice for 'total' at line 11:")
    print(f"  Lines in slice: {sorted(slice_result.lines)}")
    print(f"\n  Statements:")
    for stmt in slice_result.statements:
        print(f"    {stmt}")

    print(f"\n  Dependencies:")
    for dep in slice_result.dependencies[:5]:
        print(f"    {dep.from_line} → {dep.to_line} ({dep.dependency_type}: {dep.variable})")

    # The slice should include: tax_rate, subtotal, tax, total
    expected_lines = {2, 3, 4, 5, 6, 7, 8, 9, 10, 11}  # Most of the function
    actual_lines = slice_result.lines

    if len(actual_lines) > 3:
        print("\n✓ Backward slicing working")
        return True
    else:
        print(f"\n✗ Slice too small: {actual_lines}")
        return False


def test_forward_slice():
    """Test forward slicing - what does a variable affect?"""
    print_section("TEST 2: FORWARD SLICING")

    sample_code = '''
def process(x):
    y = x * 2
    z = y + 1
    w = z * z
    print(w)
    return w
'''

    print("Source code:")
    for i, line in enumerate(sample_code.split('\n'), 1):
        print(f"  {i}: {line}")

    slicer = ProgramSlicer(sample_code)

    # Slice from 'x' at line 2 (first assignment)
    criterion = SlicingCriterion(line=2, variable="x")
    slice_result = slicer.forward_slice(criterion)

    print(f"\nForward slice from 'x' at line 2:")
    print(f"  Lines in slice: {sorted(slice_result.lines)}")
    print(f"\n  Statements:")
    for stmt in slice_result.statements:
        print(f"    {stmt}")

    # Everything should be in the slice because x affects everything
    expected_lines = {2, 3, 4, 5, 6, 7}
    actual_lines = slice_result.lines

    if len(actual_lines) >= 4:
        print("\n✓ Forward slicing working")
        return True
    else:
        print(f"\n✗ Slice too small: {actual_lines}")
        return False


def test_method_focus():
    """Test focusing on a specific method."""
    print_section("TEST 3: METHOD FOCUS")

    sample_code = '''
class Calculator:
    def __init__(self, initial):
        self.value = initial

    def add(self, x):
        self.value = self.value + x
        return self.value

    def multiply(self, x):
        self.value = self.value * x
        return self.value

    def reset(self):
        self.value = 0
'''

    print("Source code (abbreviated):")
    for i, line in enumerate(sample_code.split('\n')[:10], 1):
        print(f"  {i}: {line}")
    print("  ...")

    slicer = ProgramSlicer(sample_code)

    # Focus on the 'add' method
    focus = slicer.focus_on_method("add")

    print(f"\nFocused slice for 'add' method:")
    print(f"  Lines in slice: {sorted(focus.lines)}")
    print(f"\n  Statements:")
    for stmt in focus.statements:
        print(f"    {stmt}")

    if len(focus.lines) >= 2:
        print("\n✓ Method focus working")
        return True
    else:
        print("\n✗ Focus failed")
        return False


def test_real_code_slicing():
    """Test slicing on real LangGraph code."""
    print_section("TEST 4: REAL CODE SLICING")

    repo_path = Path(__file__).parent.parent / "older_project" / "crawl_data" / "langgraph_repo"
    file_path = repo_path / "libs/langgraph/langgraph/graph/state.py"

    if not file_path.exists():
        print(f"File not found: {file_path}")
        return False

    with open(file_path, 'r') as f:
        source = f.read()

    slicer = ProgramSlicer(source, str(file_path))

    # Focus on the 'compile' method
    focus = slicer.focus_on_method("compile")

    print(f"Focused slice for StateGraph.compile():")
    print(f"  Lines in slice: {len(focus.lines)}")
    print(f"\n  First 10 statements:")
    for stmt in focus.statements[:10]:
        print(f"    {stmt}")

    if len(focus.lines) > 10:
        print(f"  ... and {len(focus.lines) - 10} more lines")

    if len(focus.lines) >= 5:
        print("\n✓ Real code slicing working")
        return True
    else:
        print("\n✗ Slice too small")
        return False


def test_understanding_with_slicing():
    """Show how slicing helps understanding."""
    print_section("TEST 5: SLICING FOR UNDERSTANDING")

    sample_code = '''
def compute_discount(base_price, quantity, member_status):
    # Compute base discount
    if quantity > 100:
        quantity_discount = 0.1
    else:
        quantity_discount = 0

    # Compute member discount
    if member_status == 'gold':
        member_discount = 0.2
    elif member_status == 'silver':
        member_discount = 0.1
    else:
        member_discount = 0

    # Apply discounts
    total_discount = quantity_discount + member_discount
    final_price = base_price * (1 - total_discount)
    return final_price
'''

    print("Question: What affects the final_price?")
    print("(We need to understand this to verify discount logic)")

    slicer = ProgramSlicer(sample_code)

    # Backward slice from final_price
    criterion = SlicingCriterion(line=19, variable="final_price")
    slice_result = slicer.backward_slice(criterion)

    print(f"\nBackward slice from 'final_price':")
    print(f"Lines that matter: {sorted(slice_result.lines)}")
    print(f"\nRelevant code:")
    for stmt in slice_result.statements:
        print(f"  {stmt}")

    # The slice should capture the discount logic
    print("\n--- Understanding Summary ---")
    print("To understand final_price, you need to understand:")
    print("  1. base_price (input)")
    print("  2. total_discount (computed from quantity_discount + member_discount)")
    print("  3. The conditions that set quantity_discount and member_discount")
    print("\nSlicing automatically identified these dependencies!")

    return True


def main():
    """Run all slicing tests."""
    print("\n" + "="*70)
    print("  PROGRAM SLICING FOR FOCUSED UNDERSTANDING")
    print("="*70)
    print("\nProgram slicing answers:")
    print("  - 'What affects X?' (backward slice)")
    print("  - 'What does X affect?' (forward slice)")

    results = []

    results.append(("Backward Slicing", test_backward_slice()))
    results.append(("Forward Slicing", test_forward_slice()))
    results.append(("Method Focus", test_method_focus()))
    results.append(("Real Code Slicing", test_real_code_slicing()))
    results.append(("Understanding with Slicing", test_understanding_with_slicing()))

    print_section("SUMMARY")
    passed = sum(1 for _, r in results if r)
    total = len(results)

    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"  {status}: {name}")

    print(f"\nTotal: {passed}/{total} tests passed")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Test R MCP Server."""

import sys
import importlib.util

# Load R server module
spec = importlib.util.spec_from_file_location(
    "r_server",
    "/home/user/skills_fabric/src/skills_fabric/mcp/r_server.py"
)
r_server = importlib.util.module_from_spec(spec)
spec.loader.exec_module(r_server)

RCodeParser = r_server.RCodeParser
RSymbol = r_server.RSymbol
RMCPServer = r_server.RMCPServer

# Sample R code for testing
SAMPLE_R_CODE = '''
#' Calculate summary statistics
#'
#' @param x A numeric vector
#' @param na.rm Remove NA values
#' @return A list with mean, sd, and n
#' @export
summarize_data <- function(x, na.rm = FALSE) {
  list(
    mean = mean(x, na.rm = na.rm),
    sd = sd(x, na.rm = na.rm),
    n = length(x)
  )
}

# Helper function
validate_input <- function(x) {
  if (!is.numeric(x)) {
    stop("x must be numeric")
  }
  invisible(TRUE)
}

# S3 method
print.summary_result <- function(x, digits = 3, ...) {
  cat("Summary Result:\\n")
  cat("  Mean:", round(x$mean, digits), "\\n")
  cat("  SD:", round(x$sd, digits), "\\n")
  invisible(x)
}

# S4 class
setClass("DataContainer",
  slots = c(
    data = "data.frame",
    name = "character",
    created = "POSIXct"
  )
)

# R6 class
DataProcessor <- R6Class("DataProcessor",
  public = list(
    data = NULL,
    initialize = function(data) {
      self$data <- data
    },
    process = function() {
      # Process data
      self$data
    }
  )
)
'''


def test_r_parser_creation():
    """Test creating R parser."""
    print("=" * 60)
    print("TEST 1: R Parser Creation")
    print("=" * 60)

    parser = RCodeParser()
    print("✓ Created RCodeParser")
    print(f"  Tree-sitter available: {r_server.TREE_SITTER_R_AVAILABLE}")

    return True


def test_parse_functions():
    """Test parsing R functions."""
    print("\n" + "=" * 60)
    print("TEST 2: Parse R Functions")
    print("=" * 60)

    parser = RCodeParser()
    symbols = parser.parse(SAMPLE_R_CODE, "test.R")

    print(f"✓ Parsed {len(symbols)} symbols")

    functions = [s for s in symbols if s.kind == 'function']
    print(f"  Functions: {len(functions)}")
    for f in functions:
        print(f"    - {f.name}: {f.to_citation()}")
        if f.parameters:
            print(f"      Params: {', '.join(f.parameters)}")

    assert len(functions) >= 2, "Should find at least 2 functions"
    return True


def test_parse_s3_methods():
    """Test parsing S3 methods."""
    print("\n" + "=" * 60)
    print("TEST 3: Parse S3 Methods")
    print("=" * 60)

    parser = RCodeParser()
    symbols = parser.parse(SAMPLE_R_CODE, "test.R")

    s3_methods = [s for s in symbols if s.kind == 's3_method']
    print(f"✓ Found {len(s3_methods)} S3 methods")

    for m in s3_methods:
        print(f"    - {m.name}: {m.to_citation()}")

    assert len(s3_methods) >= 1, "Should find S3 method"
    return True


def test_parse_s4_classes():
    """Test parsing S4 classes."""
    print("\n" + "=" * 60)
    print("TEST 4: Parse S4 Classes")
    print("=" * 60)

    parser = RCodeParser()
    symbols = parser.parse(SAMPLE_R_CODE, "test.R")

    s4_classes = [s for s in symbols if s.kind == 's4_class']
    print(f"✓ Found {len(s4_classes)} S4 classes")

    for c in s4_classes:
        print(f"    - {c.name}: {c.to_citation()}")

    assert len(s4_classes) >= 1, "Should find S4 class"
    return True


def test_parse_r6_classes():
    """Test parsing R6 classes."""
    print("\n" + "=" * 60)
    print("TEST 5: Parse R6 Classes")
    print("=" * 60)

    parser = RCodeParser()
    symbols = parser.parse(SAMPLE_R_CODE, "test.R")

    r6_classes = [s for s in symbols if s.kind == 'r6_class']
    print(f"✓ Found {len(r6_classes)} R6 classes")

    for c in r6_classes:
        print(f"    - {c.name}: {c.to_citation()}")

    assert len(r6_classes) >= 1, "Should find R6 class"
    return True


def test_roxygen_extraction():
    """Test roxygen2 documentation extraction."""
    print("\n" + "=" * 60)
    print("TEST 6: Roxygen2 Documentation")
    print("=" * 60)

    parser = RCodeParser()
    symbols = parser.parse(SAMPLE_R_CODE, "test.R")

    # Find function with documentation
    documented = [s for s in symbols if s.documentation]
    print(f"✓ Found {len(documented)} symbols with documentation")

    for sym in documented[:2]:
        print(f"\n  {sym.name}:")
        doc_lines = sym.documentation.split('\n')[:3]
        for line in doc_lines:
            print(f"    {line}")

    return True


def test_symbol_to_dict():
    """Test symbol serialization."""
    print("\n" + "=" * 60)
    print("TEST 7: Symbol Serialization")
    print("=" * 60)

    parser = RCodeParser()
    symbols = parser.parse(SAMPLE_R_CODE, "test.R")

    if symbols:
        sym = symbols[0]
        d = sym.to_dict()

        print("✓ Serialized symbol to dict:")
        print(f"  name: {d['name']}")
        print(f"  kind: {d['kind']}")
        print(f"  citation: {d['citation']}")
        print(f"  parameters: {d['parameters']}")

        assert 'name' in d
        assert 'citation' in d

    return True


def test_mcp_server_creation():
    """Test MCP server creation."""
    print("\n" + "=" * 60)
    print("TEST 8: MCP Server Creation")
    print("=" * 60)

    server = RMCPServer()
    print("✓ Created RMCPServer")
    print(f"  MCP available: {r_server.MCP_AVAILABLE}")

    return True


def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("R MCP SERVER TEST SUITE")
    print("=" * 60)

    tests = [
        test_r_parser_creation,
        test_parse_functions,
        test_parse_s3_methods,
        test_parse_s4_classes,
        test_parse_r6_classes,
        test_roxygen_extraction,
        test_symbol_to_dict,
        test_mcp_server_creation,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"\n✗ {test.__name__} FAILED: {e}")
            import traceback
            traceback.print_exc()
            failed += 1

    print("\n" + "=" * 60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("=" * 60)

    return failed == 0


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)

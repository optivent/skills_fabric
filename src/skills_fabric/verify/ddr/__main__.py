"""CLI interface for DDR (Direct Dependency Retriever) verification.

Usage:
    python -m skills_fabric.verify.ddr --query "StateGraph"
    python -m skills_fabric.verify.ddr --query "StateGraph" --codewiki ./codewiki
    python -m skills_fabric.verify.ddr --query "StateGraph" --json
    python -m skills_fabric.verify.ddr --validate "StateGraph" --file "src/graph.py" --line 50

Examples:
    # Basic query for a symbol
    python -m skills_fabric.verify.ddr --query StateGraph

    # Query with CodeWiki path for symbol catalog lookup
    python -m skills_fabric.verify.ddr --query StateGraph --codewiki ./codewiki_output

    # Query with repository path for source validation
    python -m skills_fabric.verify.ddr --query StateGraph --repo ./langgraph

    # Output as JSON for programmatic use
    python -m skills_fabric.verify.ddr --query StateGraph --json

    # Validate a specific symbol at a location
    python -m skills_fabric.verify.ddr --validate StateGraph --file src/state.py --line 50

    # Batch query multiple symbols
    python -m skills_fabric.verify.ddr --batch "StateGraph,CompiledGraph,NodeSpec"

    # Show Hall_m metrics summary
    python -m skills_fabric.verify.ddr --query StateGraph --show-metrics

    # Strict mode - fail if Hall_m >= 0.02
    python -m skills_fabric.verify.ddr --query StateGraph --strict
"""

import argparse
import json
import sys
from pathlib import Path

from skills_fabric.verify.ddr import (
    DirectDependencyRetriever,
    SourceRef,
    CodeElement,
    DDRResult,
    BatchProgress,
    BatchResult,
    MultiSourceValidator,
    ValidationSource,
    ValidationResult,
    validate_symbol,
    HallMetric,
    HallMetricSnapshot,
    HallMetricExceededException,
    get_hall_metric,
    reset_hall_metric,
)


def format_source_ref(ref: SourceRef) -> str:
    """Format a SourceRef for text output.

    Args:
        ref: The SourceRef to format.

    Returns:
        Formatted string representation.
    """
    validated_marker = "[VALID]" if ref.validated else "[UNVERIFIED]"
    return f"  {validated_marker} {ref.symbol_name} ({ref.symbol_type}) -> {ref.citation}"


def format_code_element(element: CodeElement, verbose: bool = False) -> str:
    """Format a CodeElement for text output.

    Args:
        element: The CodeElement to format.
        verbose: Include full content.

    Returns:
        Formatted string representation.
    """
    lines = []
    ref = element.source_ref
    validated_marker = "[VALID]" if ref.validated else "[UNVERIFIED]"

    lines.append(f"  {validated_marker} {ref.symbol_name}")
    lines.append(f"      Type: {ref.symbol_type}")
    lines.append(f"      Location: {ref.citation}")

    if ref.signature:
        lines.append(f"      Signature: {ref.signature}")

    if verbose and element.content:
        content_preview = element.content[:200].replace("\n", "\n      ")
        lines.append(f"      Content: {content_preview}...")

    return "\n".join(lines)


def format_ddr_result_text(result: DDRResult, verbose: bool = False) -> str:
    """Format DDR result as readable text.

    Args:
        result: The DDRResult to format.
        verbose: Include detailed information.

    Returns:
        Formatted text output.
    """
    lines = []

    # Header
    lines.append(f"Query: {result.query}")
    lines.append("-" * 60)

    # Metrics
    status = "PASS" if result.hallucination_rate < 0.02 else "FAIL"
    lines.append(f"Hall_m: {result.hallucination_rate:.4f} [{status}]")
    lines.append(f"Validated: {result.validated_count}")
    lines.append(f"Rejected: {result.rejected_count}")
    lines.append("-" * 60)

    # Elements
    if result.elements:
        lines.append(f"\nValidated Elements ({len(result.elements)}):\n")
        for element in result.elements:
            lines.append(format_code_element(element, verbose))
            lines.append("")
    else:
        lines.append("\nNo validated elements found.")

    return "\n".join(lines)


def format_ddr_result_json(result: DDRResult) -> dict:
    """Convert DDR result to JSON-serializable dictionary.

    Args:
        result: The DDRResult to convert.

    Returns:
        Dictionary suitable for JSON serialization.
    """
    return {
        "query": result.query,
        "validated_count": result.validated_count,
        "rejected_count": result.rejected_count,
        "hallucination_rate": result.hallucination_rate,
        "success": result.success,
        "elements": [
            {
                "symbol_name": e.source_ref.symbol_name,
                "symbol_type": e.source_ref.symbol_type,
                "file_path": e.source_ref.file_path,
                "line_number": e.source_ref.line_number,
                "citation": e.source_ref.citation,
                "signature": e.source_ref.signature,
                "validated": e.source_ref.validated,
                "content": e.content[:500] if e.content else None,
            }
            for e in result.elements
        ],
    }


def format_validation_result_text(result: ValidationResult) -> str:
    """Format validation result as readable text.

    Args:
        result: The ValidationResult to format.

    Returns:
        Formatted text output.
    """
    lines = []

    status = "VALID" if result.is_valid else "INVALID"
    confidence = f"{result.confidence:.0%}"

    lines.append(f"Symbol: {result.symbol_name}")
    lines.append(f"Status: {status}")
    lines.append(f"Confidence: {confidence}")
    lines.append(f"Line: {result.line_number}" + (f" (actual: {result.actual_line})" if result.actual_line and result.actual_line != result.line_number else ""))

    if result.symbol_kind:
        lines.append(f"Kind: {result.symbol_kind}")
    if result.signature:
        lines.append(f"Signature: {result.signature}")

    lines.append(f"\nSources checked: {', '.join(s.value for s in result.sources_checked)}")
    lines.append(f"Sources confirmed: {', '.join(s.value for s in result.sources_confirmed)}")

    if result.discrepancies:
        lines.append(f"\nDiscrepancies:")
        for d in result.discrepancies:
            lines.append(f"  - {d}")

    return "\n".join(lines)


def format_validation_result_json(result: ValidationResult) -> dict:
    """Convert validation result to JSON-serializable dictionary.

    Args:
        result: The ValidationResult to convert.

    Returns:
        Dictionary suitable for JSON serialization.
    """
    return result.to_dict()


def format_batch_result_text(result: BatchResult) -> str:
    """Format batch result as readable text.

    Args:
        result: The BatchResult to format.

    Returns:
        Formatted text output.
    """
    lines = []

    status = "PASS" if result.success else "FAIL"
    lines.append(f"Batch Query Result [{status}]")
    lines.append("=" * 60)
    lines.append(f"Queries processed: {result.queries_processed}")
    lines.append(f"Total validated: {result.total_validated}")
    lines.append(f"Total rejected: {result.total_rejected}")
    lines.append(f"Overall Hall_m: {result.overall_hallucination_rate:.4f}")
    lines.append(f"Duration: {result.duration_seconds:.2f}s")
    lines.append("-" * 60)

    # Summary of each query
    for ddr_result in result.results:
        if ddr_result.elements:
            lines.append(f"\n{ddr_result.query}: {ddr_result.validated_count} validated")
            for element in ddr_result.elements[:3]:  # Show first 3
                lines.append(f"  - {element.source_ref.citation}")
            if len(ddr_result.elements) > 3:
                lines.append(f"  ... and {len(ddr_result.elements) - 3} more")

    return "\n".join(lines)


def format_hall_m_metrics_text(metric: HallMetric) -> str:
    """Format Hall_m metrics as readable text.

    Args:
        metric: The HallMetric tracker.

    Returns:
        Formatted text output.
    """
    summary = metric.get_summary()

    lines = []
    status = "PASS" if summary.get("is_within_threshold", True) else "FAIL"

    lines.append(f"\nHall_m Metrics Summary [{status}]")
    lines.append("=" * 60)
    lines.append(f"Session start: {summary['session_start']}")
    lines.append(f"Observations: {summary['observations']}")
    lines.append(f"Threshold: {summary['threshold']:.4f}")
    lines.append(f"Cumulative Hall_m: {summary['cumulative_hall_m']:.4f}")

    if summary['observations'] > 0:
        lines.append(f"Total validated: {summary['total_validated']}")
        lines.append(f"Total rejected: {summary['total_rejected']}")
        lines.append(f"Min Hall_m: {summary['min_hall_m']:.4f}")
        lines.append(f"Max Hall_m: {summary['max_hall_m']:.4f}")
        lines.append(f"Avg Hall_m: {summary['avg_hall_m']:.4f}")

        if summary.get("by_operation"):
            lines.append("\nBy operation:")
            for op_name, op_stats in summary["by_operation"].items():
                lines.append(f"  {op_name}: Hall_m={op_stats['hall_m']:.4f} (v={op_stats['validated']}, r={op_stats['rejected']})")

    return "\n".join(lines)


def main() -> int:
    """Main entry point for DDR CLI.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    parser = argparse.ArgumentParser(
        prog="python -m skills_fabric.verify.ddr",
        description="DDR (Direct Dependency Retriever) - Zero-hallucination code verification",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Basic query for a symbol
  %(prog)s --query StateGraph

  # Query with CodeWiki path
  %(prog)s --query StateGraph --codewiki ./codewiki_output

  # Validate a specific symbol location
  %(prog)s --validate StateGraph --file src/state.py --line 50 --repo ./repo

  # Batch query multiple symbols
  %(prog)s --batch "StateGraph,CompiledGraph,NodeSpec"

  # Output as JSON
  %(prog)s --query StateGraph --json

Hall_m Target:
  The target hallucination rate is < 0.02 (2%).
  Use --strict to fail if Hall_m exceeds threshold.
        """
    )

    # Query mode arguments
    query_group = parser.add_argument_group("Query Mode")
    query_group.add_argument(
        "--query", "-q",
        type=str,
        help="Symbol or concept to search for"
    )
    query_group.add_argument(
        "--batch", "-b",
        type=str,
        help="Comma-separated list of symbols to query in batch"
    )

    # Validation mode arguments
    validate_group = parser.add_argument_group("Validation Mode")
    validate_group.add_argument(
        "--validate", "-v",
        type=str,
        help="Symbol name to validate at specific location"
    )
    validate_group.add_argument(
        "--file", "-f",
        type=str,
        help="File path for validation (relative to repo)"
    )
    validate_group.add_argument(
        "--line", "-l",
        type=int,
        help="Line number for validation (1-indexed)"
    )
    validate_group.add_argument(
        "--type", "-t",
        type=str,
        choices=["class", "function", "method", "variable"],
        help="Expected symbol type"
    )

    # Path arguments
    path_group = parser.add_argument_group("Paths")
    path_group.add_argument(
        "--codewiki", "-c",
        type=Path,
        help="Path to CodeWiki output directory (contains symbol_catalog.md)"
    )
    path_group.add_argument(
        "--repo", "-r",
        type=Path,
        help="Path to repository root for source validation"
    )

    # Output arguments
    output_group = parser.add_argument_group("Output")
    output_group.add_argument(
        "--json", "-j",
        action="store_true",
        help="Output as JSON"
    )
    output_group.add_argument(
        "--verbose",
        action="store_true",
        help="Include detailed information (content, context)"
    )
    output_group.add_argument(
        "--show-metrics",
        action="store_true",
        help="Show Hall_m metrics summary"
    )

    # Behavior arguments
    behavior_group = parser.add_argument_group("Behavior")
    behavior_group.add_argument(
        "--max-results", "-n",
        type=int,
        default=20,
        help="Maximum results per query (default: 20)"
    )
    behavior_group.add_argument(
        "--strict",
        action="store_true",
        help="Fail with exit code 1 if Hall_m >= 0.02"
    )
    behavior_group.add_argument(
        "--multi-source",
        action="store_true",
        default=True,
        help="Enable multi-source validation (AST + tree-sitter)"
    )
    behavior_group.add_argument(
        "--no-multi-source",
        action="store_true",
        help="Disable multi-source validation"
    )
    behavior_group.add_argument(
        "--use-lsp",
        action="store_true",
        help="Enable LSP validation (slower but richer type info)"
    )
    behavior_group.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress informational messages"
    )

    args = parser.parse_args()

    # Determine multi-source setting
    use_multi_source = args.multi_source and not args.no_multi_source

    # Validate arguments
    if args.validate:
        if not args.repo:
            print("Error: --repo is required for validation mode", file=sys.stderr)
            return 1
        if not args.file:
            print("Error: --file is required for validation mode", file=sys.stderr)
            return 1
        if not args.line:
            print("Error: --line is required for validation mode", file=sys.stderr)
            return 1
    elif not args.query and not args.batch:
        parser.error("One of --query, --batch, or --validate is required")

    try:
        # Validation mode
        if args.validate:
            repo_path = args.repo.resolve() if args.repo else None

            if not args.quiet and not args.json:
                print(f"Validating symbol: {args.validate}", file=sys.stderr)
                print(f"  File: {args.file}", file=sys.stderr)
                print(f"  Line: {args.line}", file=sys.stderr)

            result = validate_symbol(
                symbol_name=args.validate,
                file_path=args.file,
                line_number=args.line,
                repo_path=repo_path,
                expected_type=args.type,
                use_lsp=args.use_lsp,
            )

            if args.json:
                print(json.dumps(format_validation_result_json(result), indent=2))
            else:
                print(format_validation_result_text(result))

            # Exit code based on validation
            if args.strict and not result.is_valid:
                return 1
            return 0

        # Initialize DDR retriever
        codewiki_path = args.codewiki.resolve() if args.codewiki else None
        repo_path = args.repo.resolve() if args.repo else None

        ddr = DirectDependencyRetriever(
            codewiki_path=codewiki_path,
            repo_path=repo_path,
            use_multi_source=use_multi_source,
            use_lsp=args.use_lsp,
            fail_on_hall_m_exceed=args.strict,
        )

        try:
            # Batch mode
            if args.batch:
                queries = [q.strip() for q in args.batch.split(",") if q.strip()]

                if not args.quiet and not args.json:
                    print(f"Processing batch of {len(queries)} queries...", file=sys.stderr)

                def on_progress(progress: BatchProgress) -> None:
                    if not args.quiet and not args.json:
                        print(
                            f"  Progress: {progress.percent_complete:.1f}% "
                            f"({progress.processed}/{progress.total}) "
                            f"Hall_m: {progress.hallucination_rate:.4f}",
                            file=sys.stderr
                        )

                result = ddr.retrieve_batch(
                    queries=queries,
                    max_results_per_query=args.max_results,
                    on_progress=on_progress if not args.quiet else None,
                )

                if args.json:
                    output = {
                        "queries_processed": result.queries_processed,
                        "total_validated": result.total_validated,
                        "total_rejected": result.total_rejected,
                        "overall_hallucination_rate": result.overall_hallucination_rate,
                        "success": result.success,
                        "duration_seconds": result.duration_seconds,
                        "results": [format_ddr_result_json(r) for r in result.results],
                    }
                    print(json.dumps(output, indent=2))
                else:
                    print(format_batch_result_text(result))

                # Show metrics if requested
                if args.show_metrics and not args.json:
                    print(format_hall_m_metrics_text(ddr.hall_metric))

                # Exit code based on Hall_m
                if args.strict and not result.success:
                    return 1
                return 0

            # Single query mode
            if not args.quiet and not args.json:
                print(f"Querying: {args.query}", file=sys.stderr)

            result = ddr.retrieve(args.query, args.max_results)

            if args.json:
                print(json.dumps(format_ddr_result_json(result), indent=2))
            else:
                print(format_ddr_result_text(result, args.verbose))

            # Show metrics if requested
            if args.show_metrics and not args.json:
                print(format_hall_m_metrics_text(ddr.hall_metric))

            # Exit code based on Hall_m
            if args.strict and not result.success:
                return 1
            return 0

        finally:
            ddr.close()

    except HallMetricExceededException as e:
        if args.json:
            print(json.dumps({
                "error": "HallMetricExceeded",
                "hall_m": e.hall_m,
                "threshold": e.threshold,
                "validated": e.validated,
                "rejected": e.rejected,
                "context": e.context,
            }, indent=2))
        else:
            print(f"\nError: Hallucination rate exceeded threshold!", file=sys.stderr)
            print(f"  Hall_m: {e.hall_m:.4f}", file=sys.stderr)
            print(f"  Threshold: {e.threshold:.4f}", file=sys.stderr)
            print(f"  Validated: {e.validated}", file=sys.stderr)
            print(f"  Rejected: {e.rejected}", file=sys.stderr)
        return 1

    except FileNotFoundError as e:
        print(f"Error: File not found: {e}", file=sys.stderr)
        return 1

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())

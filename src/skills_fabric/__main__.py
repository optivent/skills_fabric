"""Skills Fabric CLI - Zero-Hallucination Claude Skill Generation.

Main entry point for the skills_fabric command-line interface.

Usage:
    python -m skills_fabric generate <library> --depth <level>
    python -m skills_fabric verify <query>
    python -m skills_fabric analyze <file>

Commands:
    generate  - Generate progressive understanding for a library
    verify    - Verify symbols using DDR (Direct Dependency Retriever)
    analyze   - Analyze source files using AST/Tree-sitter
    research  - Research a topic using Perplexity
    search    - Search documentation using Brave

Examples:
    # Generate understanding for langgraph at depth 2
    python -m skills_fabric generate langgraph --depth 2

    # Verify a symbol exists in source
    python -m skills_fabric verify StateGraph --codewiki ./codewiki

    # Analyze a Python file
    python -m skills_fabric analyze src/example.py

    # Analyze a directory
    python -m skills_fabric analyze src/ --directory

    # Research a topic
    python -m skills_fabric research "LangGraph state management"

    # Search documentation
    python -m skills_fabric search "LangGraph tutorial" --technical
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional


def cmd_generate(args: argparse.Namespace) -> int:
    """Execute the generate command.

    Generates progressive understanding for a library using the
    ProgressiveUnderstandingBuilder or SkillFactory system.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    from skills_fabric.understanding.progressive_disclosure import (
        DepthLevel,
        ProgressiveUnderstanding,
        ProgressiveUnderstandingBuilder,
        build_progressive_understanding,
    )
    from skills_fabric.observability.logging import get_logger

    logger = get_logger(__name__)

    library = args.library
    depth = args.depth
    output_format = "json" if args.json else "text"

    if not args.quiet:
        print(f"Generating understanding for: {library}", file=sys.stderr)
        print(f"Target depth: {depth} ({DepthLevel(depth).name})", file=sys.stderr)

    try:
        # Check if using factory mode
        if args.factory:
            from skills_fabric.generate.skill_factory import SkillFactory

            if not args.quiet:
                print("Using SkillFactory pipeline...", file=sys.stderr)

            factory = SkillFactory()
            result = factory.run(library)

            if output_format == "json":
                output = {
                    "library": library,
                    "mode": "factory",
                    "skills_created": result.get("skills_created", 0),
                    "symbols_count": len(result.get("symbols", [])),
                    "proven_links_count": len(result.get("proven_links", [])),
                    "errors": result.get("errors", []),
                    "status": "complete" if not result.get("errors") else "completed_with_errors",
                }
                print(json.dumps(output, indent=2))
            else:
                print(f"\n{'=' * 60}")
                print(f"Skill Generation Complete: {library}")
                print(f"{'=' * 60}")
                print(f"Skills created: {result.get('skills_created', 0)}")
                print(f"Symbols extracted: {len(result.get('symbols', []))}")
                print(f"PROVEN links: {len(result.get('proven_links', []))}")
                if result.get("errors"):
                    print(f"Errors: {len(result['errors'])}")
                    for err in result["errors"][:5]:
                        print(f"  - {err}")

            return 0 if not result.get("errors") else 1

        # Use progressive understanding builder
        repo_path = Path(args.repo_path) if args.repo_path else None
        codewiki_path = Path(args.codewiki_path) if args.codewiki_path else None

        # Try to infer paths if not provided
        if not repo_path:
            possible_paths = [
                Path.home() / "skills_fabric" / f"{library}_repo",
                Path.home() / library,
                Path(f"./{library}"),
                Path(f"./repos/{library}"),
            ]
            for p in possible_paths:
                if p.exists():
                    repo_path = p
                    if not args.quiet:
                        print(f"Found repository at: {repo_path}", file=sys.stderr)
                    break

        if not codewiki_path:
            possible_paths = [
                Path.home() / "skills_fabric" / "crawl_output" / library,
                Path(f"./codewiki_output/{library}"),
                Path(f"./output/{library}"),
            ]
            for p in possible_paths:
                if p.exists():
                    codewiki_path = p
                    if not args.quiet:
                        print(f"Found CodeWiki at: {codewiki_path}", file=sys.stderr)
                    break

        if not repo_path or not codewiki_path:
            if not args.quiet:
                print(
                    "Warning: Repository or CodeWiki path not found. "
                    "Use --repo-path and --codewiki-path to specify locations.",
                    file=sys.stderr
                )
            # Create minimal understanding without codewiki
            pu = ProgressiveUnderstanding(
                name=library,
                repo=library,
                commit="unknown"
            )
        else:
            if not args.quiet:
                print(f"Repository: {repo_path}", file=sys.stderr)
                print(f"CodeWiki: {codewiki_path}", file=sys.stderr)

            output_path = Path(args.save) if args.save else None
            pu = build_progressive_understanding(
                repo_name=library,
                repo_path=repo_path,
                codewiki_path=codewiki_path,
                output_path=output_path
            )

        # Get summary at requested depth
        target_depth = DepthLevel(min(depth, DepthLevel.DETAILED_SECTIONS))
        summary = pu.get_summary(target_depth)

        if output_format == "json":
            output = {
                "library": library,
                "mode": "progressive_disclosure",
                "name": pu.name,
                "repo": pu.repo,
                "commit": pu.commit,
                "depth_requested": depth,
                "depth_name": DepthLevel(depth).name,
                "node_count": len(pu.nodes),
                "levels": {
                    level.name: len(ids)
                    for level, ids in pu._by_level.items()
                },
                "summary": summary,
            }
            if pu.root_id and pu.root_id in pu.nodes:
                root = pu.nodes[pu.root_id]
                output["root"] = {
                    "id": root.id,
                    "title": root.title,
                    "content_preview": root.content[:500] if root.content else None,
                    "children_count": len(root.children_ids),
                    "source_refs_count": len(root.source_refs),
                }
            print(json.dumps(output, indent=2, default=str))
        else:
            print(summary)
            print()
            print(f"Total nodes: {len(pu.nodes)}")
            for level, ids in sorted(pu._by_level.items()):
                print(f"  {level.name}: {len(ids)}")

        if args.save:
            output_path = Path(args.save)
            pu.save(output_path)
            if not args.quiet:
                print(f"\nSaved to: {output_path}", file=sys.stderr)

        return 0

    except ImportError as e:
        logger.error(f"Import error: {e}")
        print(f"Error: Missing dependency - {e}", file=sys.stderr)
        return 1
    except Exception as e:
        logger.error(f"Generation error: {e}")
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def cmd_verify(args: argparse.Namespace) -> int:
    """Execute the verify command.

    Verifies symbols using the DDR (Direct Dependency Retriever).

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    from skills_fabric.verify.ddr import (
        DirectDependencyRetriever,
        HallMetricExceededException,
    )

    query = args.query
    output_format = "json" if args.json else "text"

    if not args.quiet:
        print(f"Verifying symbol: {query}", file=sys.stderr)

    try:
        # Initialize DDR
        codewiki_path = Path(args.codewiki).resolve() if args.codewiki else None
        repo_path = Path(args.repo).resolve() if args.repo else None

        ddr = DirectDependencyRetriever(
            codewiki_path=codewiki_path,
            repo_path=repo_path,
            use_multi_source=not args.no_multi_source,
            use_lsp=args.use_lsp,
            fail_on_hall_m_exceed=args.strict,
        )

        try:
            result = ddr.retrieve(query, args.max_results)

            if output_format == "json":
                output = {
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
                        }
                        for e in result.elements
                    ],
                }
                print(json.dumps(output, indent=2))
            else:
                # Text output
                status = "PASS" if result.hallucination_rate < 0.02 else "FAIL"
                print(f"\nQuery: {result.query}")
                print("-" * 60)
                print(f"Hall_m: {result.hallucination_rate:.4f} [{status}]")
                print(f"Validated: {result.validated_count}")
                print(f"Rejected: {result.rejected_count}")
                print("-" * 60)

                if result.elements:
                    print(f"\nValidated Elements ({len(result.elements)}):\n")
                    for element in result.elements:
                        ref = element.source_ref
                        marker = "[VALID]" if ref.validated else "[UNVERIFIED]"
                        print(f"  {marker} {ref.symbol_name}")
                        print(f"      Type: {ref.symbol_type}")
                        print(f"      Location: {ref.citation}")
                        if ref.signature:
                            print(f"      Signature: {ref.signature}")
                        print()
                else:
                    print("\nNo validated elements found.")

            # Show metrics if requested
            if args.show_metrics:
                summary = ddr.hall_metric.get_summary()
                print(f"\nHall_m Metrics:")
                print(f"  Observations: {summary['observations']}")
                print(f"  Cumulative Hall_m: {summary['cumulative_hall_m']:.4f}")
                print(f"  Threshold: {summary['threshold']:.4f}")

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
            }))
        else:
            print(f"\nError: Hallucination rate exceeded threshold!", file=sys.stderr)
            print(f"  Hall_m: {e.hall_m:.4f}", file=sys.stderr)
            print(f"  Threshold: {e.threshold:.4f}", file=sys.stderr)
        return 1
    except Exception as e:
        if args.json:
            print(json.dumps({"error": str(e), "query": query}))
        else:
            print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def cmd_analyze(args: argparse.Namespace) -> int:
    """Execute the analyze command.

    Analyzes source files using AST or Tree-sitter.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    from skills_fabric.analyze import (
        ASTParser,
        TreeSitterParser,
        CodeAnalyzer,
        AnalysisMode,
    )

    path = Path(args.file).resolve()
    output_format = "json" if args.json else "text"
    analyzer_mode = args.analyzer

    if not path.exists():
        print(f"Error: Path not found: {path}", file=sys.stderr)
        return 1

    is_directory = args.directory or path.is_dir()

    if is_directory and not path.is_dir():
        print(f"Error: Path is not a directory: {path}", file=sys.stderr)
        return 1

    if not is_directory and not path.is_file():
        print(f"Error: Path is not a file: {path}", file=sys.stderr)
        return 1

    if not args.quiet:
        mode_str = "directory" if is_directory else "file"
        print(f"Analyzing {mode_str}: {path}", file=sys.stderr)
        print(f"Mode: {analyzer_mode}", file=sys.stderr)

    try:
        symbols = []
        analysis_mode = analyzer_mode
        warning_msg = None

        if analyzer_mode == "auto":
            # Use unified CodeAnalyzer with fallback
            project_path = path if is_directory else path.parent
            with CodeAnalyzer(project_path=project_path, try_lsp=not args.no_lsp) as analyzer:
                if is_directory:
                    result = analyzer.analyze_directory(path)
                else:
                    result = analyzer.analyze_file(path)
                symbols = result.symbols
                analysis_mode = result.mode.value
                warning_msg = result.warning

                if not args.quiet and analyzer.is_degraded:
                    print(
                        f"Note: Running in {analysis_mode} mode (LSP unavailable)",
                        file=sys.stderr
                    )

        elif analyzer_mode == "ast":
            # AST-only (Python files only)
            if not is_directory and path.suffix != ".py":
                print(
                    f"Error: AST analyzer only supports Python files (.py)",
                    file=sys.stderr
                )
                return 1
            parser = ASTParser()
            if is_directory:
                symbols = parser.parse_directory(path)
            else:
                symbols = parser.parse_file_enhanced(path)

        elif analyzer_mode == "tree-sitter":
            # Tree-sitter (multi-language)
            parser = TreeSitterParser()
            if is_directory:
                ts_symbols = parser.parse_directory(path)
            else:
                if not parser.is_supported(path):
                    print(
                        f"Error: Unsupported file type for tree-sitter: {path.suffix}",
                        file=sys.stderr
                    )
                    return 1
                ts_symbols = parser.parse_file(path)
            # Convert to enhanced symbols for consistent output
            symbols = [s.to_enhanced() for s in ts_symbols]

        # Filter by kind if requested
        if args.kind:
            symbols = [s for s in symbols if s.kind == args.kind]

        # Output the results
        if output_format == "json":
            output = {
                "path": str(path),
                "is_directory": is_directory,
                "analyzer": analysis_mode,
                "count": len(symbols),
                "warning": warning_msg,
                "symbols": [
                    {
                        "name": s.name,
                        "kind": s.kind,
                        "file_path": s.file_path,
                        "line": s.line,
                        "end_line": getattr(s, "end_line", None),
                        "signature": getattr(s, "signature", None),
                        "docstring": getattr(s, "docstring", "")[:200] if getattr(s, "docstring", None) else None,
                        "decorators": getattr(s, "decorators", []),
                        "is_async": getattr(s, "is_async", False),
                    }
                    for s in symbols
                ],
            }
            print(json.dumps(output, indent=2))
        else:
            # Text output
            print(f"\nSymbols in {path}:")
            print(f"Analysis mode: {analysis_mode}")
            if warning_msg:
                print(f"Warning: {warning_msg}")
            print()

            print(f"{'Kind':12} {'Name':40} Location")
            print("-" * 80)

            for symbol in symbols:
                name = getattr(symbol, 'qualified_name', symbol.name) if hasattr(symbol, 'qualified_name') else symbol.name
                if len(name) > 38:
                    name = name[:35] + "..."
                loc = f"{symbol.file_path}:{symbol.line}"
                print(f"{symbol.kind:12} {name:40} {loc}")

            print("-" * 80)
            print(f"Total: {len(symbols)} symbol(s)")

            # Show additional info if verbose
            if args.verbose and symbols:
                print(f"\nDetailed info for first symbol:")
                s = symbols[0]
                print(f"  Name: {s.name}")
                print(f"  Kind: {s.kind}")
                print(f"  Line: {s.line}")
                if hasattr(s, "signature") and s.signature:
                    print(f"  Signature: {s.signature}")
                if hasattr(s, "docstring") and s.docstring:
                    doc_preview = s.docstring[:100].replace("\n", " ")
                    print(f"  Docstring: {doc_preview}...")
                if hasattr(s, "decorators") and s.decorators:
                    print(f"  Decorators: {', '.join(s.decorators)}")

        return 0

    except Exception as e:
        if args.json:
            print(json.dumps({"error": str(e), "path": str(path)}))
        else:
            print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def cmd_research(args: argparse.Namespace) -> int:
    """Execute the research command.

    Research a topic using Perplexity.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    import asyncio

    query = args.query
    output_format = "json" if args.json else "text"

    if not args.quiet:
        print(f"Researching: {query}", file=sys.stderr)

    try:
        from skills_fabric.retrievals.perplexity_client import (
            PerplexityClient,
            PerplexityConfig,
        )

        config = PerplexityConfig.from_env()
        client = PerplexityClient(config)

        async def run_research():
            if args.iterative:
                return await client.iterative_research(
                    initial_query=query,
                    max_depth=args.depth,
                )
            else:
                return await client.research(query)

        result = asyncio.run(run_research())

        if output_format == "json":
            if args.iterative:
                findings = result if isinstance(result, list) else [result]
                output = {
                    "query": query,
                    "mode": "iterative",
                    "depth": args.depth,
                    "findings_count": len(findings),
                    "findings": [
                        {
                            "query": getattr(f, 'query', query),
                            "answer": getattr(f, 'answer', str(f)),
                            "citations": [
                                {"url": c.url, "title": c.title}
                                for c in getattr(f, 'citations', [])
                            ],
                        }
                        for f in findings
                    ],
                }
            else:
                output = {
                    "query": query,
                    "mode": "single",
                    "answer": getattr(result, 'answer', str(result)),
                    "citations": [
                        {"url": c.url, "title": c.title}
                        for c in getattr(result, 'citations', [])
                    ],
                }
            print(json.dumps(output, indent=2))
        else:
            if args.iterative:
                findings = result if isinstance(result, list) else [result]
                print(f"\nResearch Results: {query}")
                print("=" * 60)
                for i, finding in enumerate(findings, 1):
                    print(f"\n--- Finding {i} ---")
                    answer = getattr(finding, 'answer', str(finding))
                    print(answer[:500] + "..." if len(answer) > 500 else answer)
                    citations = getattr(finding, 'citations', [])
                    if citations:
                        print("\nCitations:")
                        for c in citations[:5]:
                            print(f"  - {c.title}: {c.url}")
            else:
                print(f"\nResearch: {query}")
                print("=" * 60)
                answer = getattr(result, 'answer', str(result))
                print(answer)
                citations = getattr(result, 'citations', [])
                if citations:
                    print("\nCitations:")
                    for c in citations:
                        print(f"  - {c.title}: {c.url}")

        return 0

    except Exception as e:
        if args.json:
            print(json.dumps({"error": str(e), "query": query}))
        else:
            print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def cmd_search(args: argparse.Namespace) -> int:
    """Execute the search command.

    Search documentation using Brave.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    import asyncio

    query = args.query
    output_format = "json" if args.json else "text"

    if not args.quiet:
        print(f"Searching: {query}", file=sys.stderr)

    try:
        from skills_fabric.retrievals.brave_search_client import (
            BraveSearchClient,
            BraveConfig,
            Freshness,
        )

        config = BraveConfig.from_env()
        client = BraveSearchClient(config)

        async def run_search():
            freshness = None
            if args.freshness:
                freshness_map = {
                    "day": Freshness.DAY,
                    "week": Freshness.WEEK,
                    "month": Freshness.MONTH,
                    "year": Freshness.YEAR,
                }
                freshness = freshness_map.get(args.freshness)

            if args.technical:
                return await client.search_technical(
                    query,
                    count=args.count,
                    freshness=freshness
                )
            elif args.academic:
                return await client.search_academic(
                    query,
                    count=args.count
                )
            else:
                return await client.search(
                    query,
                    count=args.count,
                    freshness=freshness
                )

        response = asyncio.run(run_search())

        if output_format == "json":
            output = {
                "query": query,
                "result_count": len(response.results),
                "results": [
                    {
                        "title": r.title,
                        "url": r.url,
                        "description": r.description,
                        "domain": getattr(r, 'domain', None),
                        "relevance_score": getattr(r, 'relevance_score', None),
                    }
                    for r in response.results
                ],
            }
            print(json.dumps(output, indent=2))
        else:
            print(f"\nSearch Results: {query}")
            print("=" * 60)
            print(f"Found: {len(response.results)} results\n")

            for i, result in enumerate(response.results, 1):
                print(f"{i}. {result.title}")
                print(f"   {result.url}")
                if result.description:
                    desc = result.description[:150] + "..." if len(result.description) > 150 else result.description
                    print(f"   {desc}")
                score = getattr(result, 'relevance_score', None)
                if score:
                    print(f"   Score: {score:.2f}")
                print()

        return 0

    except Exception as e:
        if args.json:
            print(json.dumps({"error": str(e), "query": query}))
        else:
            print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


def cmd_version(args: argparse.Namespace) -> int:
    """Show version information.

    Args:
        args: Parsed command-line arguments.

    Returns:
        Exit code (0 for success).
    """
    try:
        from skills_fabric import __version__
        version = __version__
    except ImportError:
        version = "0.1.0"

    if args.json:
        print(json.dumps({"name": "skills_fabric", "version": version}))
    else:
        print(f"skills-fabric version {version}")
    return 0


def main() -> int:
    """Main entry point for the skills_fabric CLI.

    Returns:
        Exit code (0 for success, 1 for error).
    """
    parser = argparse.ArgumentParser(
        prog="python -m skills_fabric",
        description="Skills Fabric - Zero-Hallucination Claude Skill Generation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
  generate    Generate progressive understanding for a library
  verify      Verify symbols using DDR (zero-hallucination)
  analyze     Analyze source files with AST/Tree-sitter
  research    Research a topic using Perplexity
  search      Search documentation using Brave
  version     Show version information

Examples:
  %(prog)s generate langgraph --depth 2
  %(prog)s verify StateGraph --codewiki ./codewiki
  %(prog)s analyze src/example.py --json
  %(prog)s analyze src/ --directory
  %(prog)s research "LangGraph state management"
  %(prog)s search "LangGraph tutorial" --technical

For more help on a specific command:
  %(prog)s <command> --help
        """
    )

    # Global options
    parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress informational messages"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show verbose output and stack traces"
    )
    parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="Output as JSON"
    )

    # Subcommands
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # === generate command ===
    gen_parser = subparsers.add_parser(
        "generate",
        help="Generate progressive understanding for a library",
        description="Generate progressive understanding using ProgressiveDisclosure",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m skills_fabric generate langgraph --depth 2
  python -m skills_fabric generate langgraph --depth 3 --save ./output.json
  python -m skills_fabric generate langgraph --factory
        """
    )
    gen_parser.add_argument(
        "library",
        type=str,
        help="Library name (e.g., langgraph, langchain)"
    )
    gen_parser.add_argument(
        "--depth", "-d",
        type=int,
        choices=[0, 1, 2, 3, 4, 5],
        default=2,
        help="Understanding depth (0=summary, 5=execution proofs)"
    )
    gen_parser.add_argument(
        "--save", "-s",
        type=str,
        help="Save understanding to JSON file"
    )
    gen_parser.add_argument(
        "--repo-path",
        type=str,
        help="Path to cloned repository"
    )
    gen_parser.add_argument(
        "--codewiki-path",
        type=str,
        help="Path to CodeWiki output directory"
    )
    gen_parser.add_argument(
        "--factory",
        action="store_true",
        help="Use full SkillFactory pipeline (requires database)"
    )
    gen_parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="Output as JSON"
    )
    gen_parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress informational messages"
    )
    gen_parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show verbose output"
    )
    gen_parser.set_defaults(func=cmd_generate)

    # === verify command ===
    verify_parser = subparsers.add_parser(
        "verify",
        help="Verify symbols using DDR",
        description="Verify symbols exist in source using DDR (Direct Dependency Retriever)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m skills_fabric verify StateGraph
  python -m skills_fabric verify StateGraph --codewiki ./codewiki
  python -m skills_fabric verify StateGraph --strict --json
        """
    )
    verify_parser.add_argument(
        "query",
        type=str,
        help="Symbol or concept to verify"
    )
    verify_parser.add_argument(
        "--codewiki", "-c",
        type=str,
        help="Path to CodeWiki output directory"
    )
    verify_parser.add_argument(
        "--repo", "-r",
        type=str,
        help="Path to repository root"
    )
    verify_parser.add_argument(
        "--max-results", "-n",
        type=int,
        default=20,
        help="Maximum results (default: 20)"
    )
    verify_parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="Output as JSON"
    )
    verify_parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail if Hall_m >= 0.02"
    )
    verify_parser.add_argument(
        "--no-multi-source",
        action="store_true",
        help="Disable multi-source validation"
    )
    verify_parser.add_argument(
        "--use-lsp",
        action="store_true",
        help="Enable LSP validation (richer but slower)"
    )
    verify_parser.add_argument(
        "--show-metrics",
        action="store_true",
        help="Show Hall_m metrics summary"
    )
    verify_parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress informational messages"
    )
    verify_parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show verbose output"
    )
    verify_parser.set_defaults(func=cmd_verify)

    # === analyze command ===
    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Analyze source files with AST/Tree-sitter",
        description="Analyze source files to extract symbols and metadata",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m skills_fabric analyze src/example.py
  python -m skills_fabric analyze src/ --directory
  python -m skills_fabric analyze example.ts --analyzer tree-sitter
  python -m skills_fabric analyze src/example.py --json
        """
    )
    analyze_parser.add_argument(
        "file",
        type=str,
        help="Path to source file or directory to analyze"
    )
    analyze_parser.add_argument(
        "--directory",
        action="store_true",
        help="Analyze entire directory recursively"
    )
    analyze_parser.add_argument(
        "--analyzer", "-a",
        choices=["auto", "ast", "tree-sitter"],
        default="auto",
        help="Analyzer to use (default: auto with fallback)"
    )
    analyze_parser.add_argument(
        "--kind", "-k",
        choices=["class", "function", "method"],
        help="Filter symbols by kind"
    )
    analyze_parser.add_argument(
        "--no-lsp",
        action="store_true",
        help="Skip LSP, use AST-only analysis"
    )
    analyze_parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="Output as JSON"
    )
    analyze_parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress informational messages"
    )
    analyze_parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show verbose output"
    )
    analyze_parser.set_defaults(func=cmd_analyze)

    # === research command ===
    research_parser = subparsers.add_parser(
        "research",
        help="Research a topic using Perplexity",
        description="Research a topic using Perplexity AI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m skills_fabric research "LangGraph state management"
  python -m skills_fabric research "LangGraph patterns" --iterative --depth 3
  python -m skills_fabric research "Python async best practices" --json
        """
    )
    research_parser.add_argument(
        "query",
        type=str,
        help="Research query"
    )
    research_parser.add_argument(
        "--iterative",
        action="store_true",
        help="Use iterative research loop for deeper exploration"
    )
    research_parser.add_argument(
        "--depth",
        type=int,
        default=2,
        help="Research depth for iterative mode (default: 2)"
    )
    research_parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="Output as JSON"
    )
    research_parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress informational messages"
    )
    research_parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show verbose output"
    )
    research_parser.set_defaults(func=cmd_research)

    # === search command ===
    search_parser = subparsers.add_parser(
        "search",
        help="Search documentation using Brave",
        description="Search documentation using Brave Search API",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m skills_fabric search "LangGraph tutorial"
  python -m skills_fabric search "LangGraph API" --technical
  python -m skills_fabric search "LangGraph paper" --academic
  python -m skills_fabric search "LangGraph" --freshness week
        """
    )
    search_parser.add_argument(
        "query",
        type=str,
        help="Search query"
    )
    search_parser.add_argument(
        "--count", "-n",
        type=int,
        default=10,
        help="Number of results (default: 10, max: 20)"
    )
    search_parser.add_argument(
        "--technical",
        action="store_true",
        help="Search technical/documentation sites"
    )
    search_parser.add_argument(
        "--academic",
        action="store_true",
        help="Search academic sources"
    )
    search_parser.add_argument(
        "--freshness",
        choices=["day", "week", "month", "year"],
        help="Filter by content freshness"
    )
    search_parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="Output as JSON"
    )
    search_parser.add_argument(
        "--quiet", "-q",
        action="store_true",
        help="Suppress informational messages"
    )
    search_parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show verbose output"
    )
    search_parser.set_defaults(func=cmd_search)

    # === version command ===
    version_parser = subparsers.add_parser(
        "version",
        help="Show version information"
    )
    version_parser.add_argument(
        "--json", "-j",
        action="store_true",
        help="Output as JSON"
    )
    version_parser.set_defaults(func=cmd_version)

    # Parse arguments
    args = parser.parse_args()

    # If no command given, show help
    if not args.command:
        parser.print_help()
        return 0

    # Execute the command
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())

#!/bin/bash
# =============================================================================
# Autonomous Skill Generation Script
#
# Ralph Wiggum enhanced skill generation with completion promises.
#
# Usage:
#   ./autonomous_skill_gen.sh <library_name> [max_iterations] [min_skills]
#
# Examples:
#   ./autonomous_skill_gen.sh langgraph
#   ./autonomous_skill_gen.sh langgraph 20 5
#   ./autonomous_skill_gen.sh fastapi 10 3
#
# Batch mode:
#   ./autonomous_skill_gen.sh --batch libraries.txt
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Defaults
MAX_ITERATIONS=${2:-10}
MIN_SKILLS=${3:-1}

print_header() {
    echo "═══════════════════════════════════════════════════════════════"
    echo " AUTONOMOUS SKILL GENERATION"
    echo " Ralph Wiggum + Trust Hierarchy + BMAD C.O.R.E."
    echo "═══════════════════════════════════════════════════════════════"
    echo ""
}

print_config() {
    echo "Configuration:"
    echo "  Library: $1"
    echo "  Max Iterations: $MAX_ITERATIONS"
    echo "  Min Skills: $MIN_SKILLS"
    echo ""
}

run_single() {
    local library=$1

    print_header
    print_config "$library"

    echo "Starting autonomous generation..."
    echo ""

    python -m skills_fabric.orchestration.autonomous_factory \
        "$library" \
        --max-iterations "$MAX_ITERATIONS" \
        --min-skills "$MIN_SKILLS"

    local exit_code=$?

    echo ""
    if [ $exit_code -eq 0 ]; then
        echo -e "${GREEN}✓ Generation successful${NC}"
    else
        echo -e "${RED}✗ Generation failed${NC}"
    fi

    return $exit_code
}

run_batch() {
    local file=$1

    if [ ! -f "$file" ]; then
        echo -e "${RED}Error: File not found: $file${NC}"
        exit 1
    fi

    print_header
    echo "Batch Mode: Processing libraries from $file"
    echo ""

    local total=0
    local success=0
    local failed=0

    while IFS= read -r library || [[ -n "$library" ]]; do
        # Skip empty lines and comments
        [[ -z "$library" || "$library" =~ ^# ]] && continue

        total=$((total + 1))
        echo "─────────────────────────────────────────────────────────────────"
        echo "[$total] Processing: $library"
        echo "─────────────────────────────────────────────────────────────────"

        if python -m skills_fabric.orchestration.autonomous_factory \
            "$library" \
            --max-iterations "$MAX_ITERATIONS" \
            --min-skills "$MIN_SKILLS"; then
            success=$((success + 1))
            echo -e "${GREEN}✓ $library: Success${NC}"
        else
            failed=$((failed + 1))
            echo -e "${RED}✗ $library: Failed${NC}"
        fi

        echo ""
    done < "$file"

    # Summary
    echo "═══════════════════════════════════════════════════════════════"
    echo " BATCH SUMMARY"
    echo "═══════════════════════════════════════════════════════════════"
    echo "  Total: $total"
    echo -e "  ${GREEN}Success: $success${NC}"
    echo -e "  ${RED}Failed: $failed${NC}"
    echo "═══════════════════════════════════════════════════════════════"
}

# Main
if [ "$1" == "--batch" ]; then
    if [ -z "$2" ]; then
        echo "Usage: $0 --batch <libraries_file>"
        exit 1
    fi
    run_batch "$2"
elif [ "$1" == "--help" ] || [ "$1" == "-h" ]; then
    echo "Usage: $0 <library_name> [max_iterations] [min_skills]"
    echo "       $0 --batch <libraries_file>"
    echo ""
    echo "Arguments:"
    echo "  library_name     Name of library to generate skills for"
    echo "  max_iterations   Maximum iterations (default: 10)"
    echo "  min_skills       Minimum skills required (default: 1)"
    echo ""
    echo "Batch mode:"
    echo "  --batch <file>   Process libraries listed in file (one per line)"
    echo ""
    echo "Examples:"
    echo "  $0 langgraph"
    echo "  $0 langgraph 20 5"
    echo "  $0 --batch libraries.txt"
elif [ -z "$1" ]; then
    echo "Error: Library name required"
    echo "Usage: $0 <library_name> [max_iterations] [min_skills]"
    exit 1
else
    run_single "$1"
fi

#!/usr/bin/env bash
#
# Entry point for the Bloom's Taxonomy classifier.
#
# Usage:
#   export OPENAI_API_KEY=sk-...
#   ./run_classify.sh --input questions.csv --output results.csv
#
# Any arguments are passed through directly to src/classify.py.
# Run './run_classify.sh --help' to see all available options.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ -z "${OPENAI_API_KEY:-}" ]; then
    echo "ERROR: OPENAI_API_KEY is not set." >&2
    echo "Set it first, e.g.:" >&2
    echo "  export OPENAI_API_KEY=sk-..." >&2
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "ERROR: python3 not found on PATH." >&2
    exit 1
fi

if ! python3 -c "import pandas, openai, tqdm" &> /dev/null; then
    echo "NOTE: required Python packages not detected; installing from requirements.txt..."
    pip install -r "${SCRIPT_DIR}/requirements.txt"
fi

python3 "${SCRIPT_DIR}/src/classify.py" "$@"

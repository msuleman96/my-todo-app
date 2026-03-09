#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

if ! command -v python >/dev/null 2>&1; then
  echo "Error: python is not installed or not in PATH."
  exit 1
fi

if ! command -v streamlit >/dev/null 2>&1; then
  echo "Installing dependencies from requirements.txt..."
  python -m pip install -r requirements.txt
fi

echo "Starting AI Trading Agent on http://localhost:8501"
exec streamlit run web.py

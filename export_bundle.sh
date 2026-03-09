#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

OUT_NAME="ai-trading-agent-bundle.zip"
rm -f "$OUT_NAME"

zip -r "$OUT_NAME" \
  web.py \
  trading_agent.py \
  run.sh \
  requirements.txt \
  README.md \
  .streamlit/config.toml \
  functions.py \
  todos.txt \
  >/dev/null

echo "Created: $SCRIPT_DIR/$OUT_NAME"

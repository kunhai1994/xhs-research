#!/usr/bin/env bash
# xhs-research: Quick health check on session start (<2s)

XHS_DIR="$HOME/.local/share/xhs-research"

missing=()
[ ! -d "$XHS_DIR/bin" ] && missing+=("xiaohongshu-mcp binary")
[ ! -f "$XHS_DIR/last30days/scripts/last30days.py" ] && missing+=("last30days engine")

if [ ${#missing[@]} -gt 0 ]; then
  echo "/xhs-research: Missing: ${missing[*]}. First-run setup needed — the skill will handle it automatically."
fi

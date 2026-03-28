#!/usr/bin/env python3
"""xhs-research: Quick health check on session start (<2s)."""

import os
import sys

XHS_DIR = os.path.join(os.path.expanduser("~"), ".local", "share", "xhs-research")

missing = []
if not os.path.isdir(os.path.join(XHS_DIR, "bin")):
    missing.append("xiaohongshu-mcp binary")

if missing:
    print(f"/xhs-research: Missing: {', '.join(missing)}. First-run setup needed — the skill will handle it automatically.")

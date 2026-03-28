#!/usr/bin/env python3
"""Start xiaohongshu-mcp server if not already running."""

import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import (
    BIN_DIR, COOKIES_PATH, MCP_PORT,
    find_binary, check_mcp_health, ok, fail, info, warn,
)


def main() -> None:
    print("\n🚀 Starting xiaohongshu-mcp server\n")

    if check_mcp_health():
        ok(f"MCP server already running on port {MCP_PORT}")
        return

    mcp_bin = find_binary("xiaohongshu-mcp")
    if not mcp_bin:
        fail("xiaohongshu-mcp binary not found. Run setup.py first.")
        sys.exit(1)

    if not os.path.isfile(COOKIES_PATH):
        warn(f"No cookies found at {COOKIES_PATH}")
        warn("Server will start but you need to login first (run login.py)")

    info(f"Starting {os.path.basename(mcp_bin)} on port {MCP_PORT}...")

    env = os.environ.copy()
    env["COOKIES_PATH"] = COOKIES_PATH

    try:
        log_path = os.path.join(BIN_DIR, "mcp-server.log")
        log_file = open(log_path, "a")
        subprocess.Popen(
            [mcp_bin, "-port", f":{MCP_PORT}", "-headless"],
            env=env, stdout=log_file, stderr=log_file,
            start_new_session=True,
        )
        log_file.close()  # Child inherits FD; parent can safely close
    except Exception as e:
        fail(f"Failed to start MCP server: {e}")
        sys.exit(1)

    info("Waiting for server to start...")
    for i in range(6):
        time.sleep(1)
        if check_mcp_health():
            ok(f"MCP server running on port {MCP_PORT}")
            info(f"Log file: {log_path}")
            return

    fail(f"Server did not respond within 6 seconds. Check log: {log_path}")
    sys.exit(1)


if __name__ == "__main__":
    main()

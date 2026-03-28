#!/usr/bin/env python3
"""Run xiaohongshu QR code login and verify session."""

import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import (
    XHS_DIR, COOKIES_PATH,
    find_binary, check_mcp_health, check_mcp_login,
    ok, fail, info, warn,
)


def main() -> None:
    print("\n🔑 Xiaohongshu login\n")

    login_bin = find_binary("xiaohongshu-login")
    if not login_bin:
        fail("xiaohongshu-login binary not found. Run setup.py first.")
        sys.exit(1)

    os.makedirs(XHS_DIR, exist_ok=True)

    info("Launching Chrome for QR code login...")
    info("Please scan the QR code with your Xiaohongshu app.")
    print()

    try:
        result = subprocess.run([login_bin], cwd=XHS_DIR)
        if result.returncode != 0:
            fail(f"Login process exited with code {result.returncode}")
            sys.exit(1)
    except FileNotFoundError:
        fail(f"Cannot execute {login_bin}. Check file permissions.")
        sys.exit(1)
    except KeyboardInterrupt:
        warn("Login cancelled by user.")
        sys.exit(1)

    if not os.path.isfile(COOKIES_PATH):
        fail(f"Cookies not found at {COOKIES_PATH}")
        info("Login may have failed. Please try again.")
        sys.exit(1)

    ok("Cookies saved successfully")

    info("Starting MCP server to verify login...")
    from start import main as start_main
    start_main()

    print()
    if check_mcp_login():
        ok("Login verified! You can now use /xhs-research to search Xiaohongshu.")
    else:
        warn("MCP server is running but login status could not be verified.")
        warn("This may happen if the server is still loading. Try again in a few seconds.")


if __name__ == "__main__":
    main()

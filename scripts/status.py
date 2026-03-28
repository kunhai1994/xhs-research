#!/usr/bin/env python3
"""Check status of all xhs-research components."""

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import (
    BIN_DIR, COOKIES_PATH, MCP_PORT,
    detect_platform, find_binary,
    check_mcp_health, check_mcp_login,
    ok, fail, info,
)


def main() -> None:
    emit_json = "--json" in sys.argv

    os_name, arch = detect_platform()
    results = {
        "platform": f"{os_name}-{arch}",
        "mcp_binary_installed": find_binary("xiaohongshu-mcp") is not None,
        "login_binary_installed": find_binary("xiaohongshu-login") is not None,
        "cookies_exist": os.path.isfile(COOKIES_PATH),
        "mcp_running": False,
        "xhs_logged_in": False,
    }

    if results["mcp_binary_installed"]:
        results["mcp_running"] = check_mcp_health()
        if results["mcp_running"]:
            results["xhs_logged_in"] = check_mcp_login()

    results["all_ready"] = all([
        results["mcp_binary_installed"],
        results["mcp_running"],
        results["xhs_logged_in"],
    ])

    if emit_json:
        print(json.dumps(results, indent=2))
        sys.exit(0 if results["all_ready"] else 1)

    print(f"\n📊 xhs-research status ({os_name}-{arch})\n")

    def check(label: str, value: bool, hint: str = "") -> None:
        if value:
            ok(label)
        else:
            fail(f"{label}{f' — {hint}' if hint else ''}")

    check("xiaohongshu-mcp binary", results["mcp_binary_installed"], "run setup.py")
    check("MCP server (port {})".format(MCP_PORT), results["mcp_running"], "run start.py")
    check("Xiaohongshu login", results["xhs_logged_in"],
          "run login.py" if not results["mcp_running"] else "cookies expired, run login.py")

    print()
    if results["all_ready"]:
        ok("All systems ready! Use /xhs-research to start researching.")
    else:
        info("Run the suggested commands above to fix issues.")

    sys.exit(0 if results["all_ready"] else 1)


if __name__ == "__main__":
    main()

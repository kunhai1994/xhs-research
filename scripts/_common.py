"""Shared constants and helpers for xhs-research scripts."""

import os
import platform
import sys
import urllib.request
import urllib.error
import json

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
XHS_DIR = os.path.join(os.path.expanduser("~"), ".local", "share", "xhs-research")
BIN_DIR = os.path.join(XHS_DIR, "bin")
COOKIES_PATH = os.path.join(XHS_DIR, "cookies.json")

MCP_PORT = 18060
MCP_BASE_URL = f"http://localhost:{MCP_PORT}"
MCP_REPO = "xpzouying/xiaohongshu-mcp"

# Multi-platform skill root discovery
SEARCH_DIRS = [
    os.environ.get("CLAUDE_PLUGIN_ROOT", ""),
    os.environ.get("OPENCLAW_SKILL_ROOT", ""),
    os.environ.get("GEMINI_EXTENSION_DIR", ""),
    os.path.expanduser("~/.claude/skills/xhs-research"),
    os.path.expanduser("~/.agents/skills/xhs-research"),
    os.path.expanduser("~/.codex/skills/xhs-research"),
    os.path.expanduser("~/.gemini/extensions/xhs-research"),
]


def find_skill_root() -> str | None:
    """Find the xhs-research skill installation directory."""
    for d in SEARCH_DIRS:
        if d and os.path.isfile(os.path.join(d, "scripts", "xhs_research.py")):
            return d
    return None


# ---------------------------------------------------------------------------
# Platform detection
# ---------------------------------------------------------------------------
def detect_platform() -> tuple[str, str]:
    """Return (os_name, arch) matching xiaohongshu-mcp release naming."""
    system = platform.system().lower()
    machine = platform.machine().lower()

    arch_map = {
        "arm64": "arm64",
        "aarch64": "arm64",
        "x86_64": "amd64",
        "amd64": "amd64",
    }
    arch = arch_map.get(machine)
    if arch is None:
        print(f"[error] Unsupported architecture: {machine}", file=sys.stderr)
        sys.exit(1)

    return system, arch


def get_binary_name(prefix: str) -> str:
    """Return the expected binary filename."""
    os_name, arch = detect_platform()
    return f"{prefix}-{os_name}-{arch}"


def find_binary(prefix: str) -> str | None:
    """Find installed binary in BIN_DIR. Returns full path or None."""
    name = get_binary_name(prefix)
    path = os.path.join(BIN_DIR, name)
    return path if os.path.isfile(path) else None


# ---------------------------------------------------------------------------
# HTTP helpers (stdlib only)
# ---------------------------------------------------------------------------
def http_get_json(url: str, timeout: int = 5) -> dict | None:
    """GET a URL and parse JSON. Returns None on any error."""
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "xhs-research/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read())
    except Exception:
        return None


def check_mcp_health() -> bool:
    """Return True if xiaohongshu-mcp is running and healthy."""
    data = http_get_json(f"{MCP_BASE_URL}/health", timeout=2)
    return isinstance(data, dict) and data.get("success") is True


def check_mcp_login() -> bool:
    """Return True if xiaohongshu-mcp reports logged in."""
    data = http_get_json(f"{MCP_BASE_URL}/api/v1/login/status", timeout=8)
    if not isinstance(data, dict):
        return False
    return data.get("data", {}).get("is_logged_in") is True


# ---------------------------------------------------------------------------
# Pretty output
# ---------------------------------------------------------------------------
def ok(msg: str) -> None:
    print(f"  \033[32m✅ {msg}\033[0m")

def fail(msg: str) -> None:
    print(f"  \033[31m❌ {msg}\033[0m")

def info(msg: str) -> None:
    print(f"  \033[36mℹ️  {msg}\033[0m")

def warn(msg: str) -> None:
    print(f"  \033[33m⚠️  {msg}\033[0m")

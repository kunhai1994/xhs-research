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
LAST30DAYS_DIR = os.path.join(XHS_DIR, "last30days")
LAST30DAYS_SCRIPT = os.path.join(LAST30DAYS_DIR, "scripts", "last30days.py")
COOKIES_PATH = os.path.join(XHS_DIR, "cookies.json")
ENV_FILE = os.path.join(os.path.expanduser("~"), ".config", "last30days", ".env")

MCP_PORT = 18060
MCP_BASE_URL = f"http://localhost:{MCP_PORT}"
MCP_REPO = "xpzouying/xiaohongshu-mcp"
LAST30DAYS_REPO = "https://github.com/mvanhorn/last30days-skill.git"


# ---------------------------------------------------------------------------
# Platform detection
# ---------------------------------------------------------------------------
def detect_platform() -> tuple[str, str]:
    """Return (os_name, arch) matching xiaohongshu-mcp release naming.

    Examples: ("darwin", "arm64"), ("linux", "amd64"), ("windows", "amd64")
    """
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
    """Return the expected binary filename, e.g. 'xiaohongshu-mcp-darwin-arm64'."""
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
# Config helpers
# ---------------------------------------------------------------------------
def ensure_env_key(key: str, value: str) -> bool:
    """Append key=value to ENV_FILE if not already present. Returns True if written."""
    os.makedirs(os.path.dirname(ENV_FILE), exist_ok=True)

    existing = ""
    if os.path.isfile(ENV_FILE):
        with open(ENV_FILE, "r") as f:
            existing = f.read()

    for line in existing.splitlines():
        stripped = line.strip()
        if stripped.startswith(f"{key}=") or stripped.startswith(f"export {key}="):
            return False

    with open(ENV_FILE, "a") as f:
        if existing and not existing.endswith("\n"):
            f.write("\n")
        f.write(f"{key}={value}\n")

    return True


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

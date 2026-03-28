#!/usr/bin/env python3
"""xhs-research setup: download xiaohongshu-mcp binary."""

import json
import os
import stat
import sys
import tarfile
import tempfile
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _common import (
    XHS_DIR, BIN_DIR, MCP_REPO,
    detect_platform, find_binary,
    ok, fail, info,
)

GITHUB_API = f"https://api.github.com/repos/{MCP_REPO}/releases/latest"


def download_mcp_binaries() -> bool:
    """Download xiaohongshu-mcp + xiaohongshu-login from latest GitHub release."""
    os.makedirs(BIN_DIR, exist_ok=True)
    os_name, arch = detect_platform()

    if find_binary("xiaohongshu-mcp") and find_binary("xiaohongshu-login"):
        ok(f"xiaohongshu-mcp binaries already installed ({os_name}-{arch})")
        return True

    info(f"Fetching latest release for {os_name}-{arch}...")
    try:
        req = urllib.request.Request(GITHUB_API, headers={"User-Agent": "xhs-research/1.0"})
        with urllib.request.urlopen(req, timeout=15) as resp:
            release = json.loads(resp.read())
    except Exception as e:
        fail(f"Failed to fetch release info: {e}")
        return False

    target_name = f"xiaohongshu-mcp-{os_name}-{arch}.tar.gz"
    asset_url = None
    for asset in release.get("assets", []):
        if asset["name"] == target_name:
            asset_url = asset["browser_download_url"]
            break

    if not asset_url:
        fail(f"No release asset found for {target_name}")
        available = [a["name"] for a in release.get("assets", [])]
        info(f"Available assets: {', '.join(available)}")
        return False

    info(f"Downloading {target_name} (~19MB)...")
    tmp_path = None
    try:
        with tempfile.NamedTemporaryFile(suffix=".tar.gz", delete=False) as tmp:
            tmp_path = tmp.name
            urllib.request.urlretrieve(asset_url, tmp_path)

        info("Extracting...")
        with tarfile.open(tmp_path, "r:gz") as tar:
            for member in tar.getmembers():
                if member.name.startswith(("xiaohongshu-mcp-", "xiaohongshu-login-")):
                    member.name = os.path.basename(member.name)
                    tar.extract(member, BIN_DIR)

        for name in os.listdir(BIN_DIR):
            path = os.path.join(BIN_DIR, name)
            if os.path.isfile(path):
                os.chmod(path, os.stat(path).st_mode | stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH)

        ok(f"Binaries installed to {BIN_DIR}")
        return True

    except Exception as e:
        fail(f"Download/extract failed: {e}")
        return False
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)


def main() -> None:
    print("\n🔧 xhs-research setup\n")

    os_name, arch = detect_platform()
    info(f"Platform: {os_name}-{arch}")

    success = download_mcp_binaries()

    print()
    if success:
        ok("Setup complete!")
        print()
        info("Next step: run login to scan QR code:")
        info(f"  python3 {os.path.dirname(os.path.abspath(__file__))}/login.py")
    else:
        fail("Setup incomplete. Please fix the errors above and retry.")
        sys.exit(1)


if __name__ == "__main__":
    main()

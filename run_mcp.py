#!/usr/bin/env python3
"""
Entry point for the Robot Framework MCP Server (pip / UV installs).

    robotframework-mcp                       # SeleniumLibrary backend (default)
    robotframework-mcp --library=browser     # Playwright / Browser library backend
    robotframework-mcp --library=browser --setup   # one-time: rfbrowser init

The Browser backend's dependencies come from the optional extra
(pip install "robotframework-mcp[browser]"). If they are missing,
--library=browser installs them into the current environment automatically.

stdout is the MCP JSON-RPC channel, so everything this script prints goes to stderr.
"""

import importlib
import importlib.util
import os
import subprocess
import sys

SUPPORTED_LIBRARIES = ("selenium", "browser")


def _err(msg: str) -> None:
    print(msg, file=sys.stderr)


def _selected_library(argv: list[str]) -> str:
    for arg in argv:
        if arg.startswith("--library="):
            return arg.split("=", 1)[1].strip().lower()
    return os.environ.get("ROBOTFRAMEWORK_MCP_LIBRARY", "selenium").strip().lower()


# Same requirements as the [browser] extra in pyproject.toml.
BROWSER_REQUIREMENTS = ["robotframework>=7.0", "robotframework-browser>=19.0.0"]


def _run_quietly(cmd: list[str]) -> int:
    """Run a setup command with all of its output on stderr, so it can never
    corrupt an MCP stdio stream."""
    return subprocess.call(cmd, stdin=subprocess.DEVNULL, stdout=sys.stderr, stderr=sys.stderr)


def _browser_installed() -> bool:
    importlib.invalidate_caches()
    return importlib.util.find_spec("Browser") is not None


def _browser_initialized() -> bool:
    """`rfbrowser init` installs the Node side-car (incl. playwright-core)
    next to the Browser package; its presence means init has completed."""
    spec = importlib.util.find_spec("Browser")
    if spec is None or not spec.origin:
        return False
    pkg_dir = os.path.dirname(spec.origin)
    return os.path.isdir(os.path.join(pkg_dir, "wrapper", "node_modules", "playwright-core"))


def _ensure_browser_backend() -> int:
    """Install robotframework-browser if missing (same as the [browser]
    extra), then run `rfbrowser init` if it has not run yet. Returns 0 when
    the backend is ready."""
    if not _browser_installed():
        _err("📦 Installing the Browser library backend (robotframework-browser)...")
        if _run_quietly([sys.executable, "-m", "pip", "install", *BROWSER_REQUIREMENTS]) != 0:
            _err('❌ Install failed. Try manually: pip install "robotframework-mcp[browser]"')
            return 1
        if not _browser_installed():
            _err("❌ robotframework-browser still not importable after install.")
            return 1
    if not _browser_initialized():
        _err("📦 Running `rfbrowser init` (downloads Playwright browsers, a few minutes)...")
        if _run_quietly([sys.executable, "-m", "Browser.entry", "init"]) != 0:
            _err("❌ `rfbrowser init` failed. Try manually: rfbrowser init")
            return 1
    _err("✅ Browser-library backend ready")
    return 0


def _run_browser() -> None:
    if not (_browser_installed() and _browser_initialized()):
        _err("⚠️ Browser-library backend is not set up yet; setting it up now (can take a few minutes).")
        _err("   If your MCP client times out, run this once in a terminal and restart the client:")
        _err("     robotframework-mcp --library=browser --setup")
        if _ensure_browser_backend() != 0:
            sys.exit(1)
    from rf_browser_mcp.server import main as browser_main
    browser_main()


def _run_selenium() -> None:
    # Make the sibling mcp_server module importable when run from a checkout.
    current_dir = os.path.dirname(os.path.abspath(__file__))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)
    from mcp_server import main as mcp_main
    mcp_main()


def main():
    """Main entry point for pip / UV execution"""
    library = _selected_library(sys.argv[1:])
    if library not in SUPPORTED_LIBRARIES:
        _err(f'❌ Unknown --library="{library}". Supported values: {", ".join(SUPPORTED_LIBRARIES)}')
        sys.exit(1)

    if "--setup" in sys.argv[1:]:
        sys.exit(_ensure_browser_backend() if library == "browser" else 0)

    try:
        if library == "browser":
            _run_browser()
        else:
            _run_selenium()
    except ImportError as e:
        _err(f"Import error: {e}")
        sys.exit(1)
    except Exception as e:
        _err(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()

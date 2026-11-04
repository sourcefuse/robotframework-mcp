"""MCP server exposing Robot Framework's Browser library as tools.

Each tool below is a thin wrapper that calls a real Browser-library
keyword against a single, persistent RF execution context (see
``bridge.py``). Arguments are passed the same way they would be written
in a .robot file: required values positionally, optional values as
``name=value`` strings (Robot Framework's own argument-resolution and
type-conversion machinery handles the rest, including enums like
``SupportedBrowsers`` and time strings like ``500 ms``).
"""

from __future__ import annotations

from typing import Any

from mcp.server.mcpserver import MCPServer
from mcp.server.mcpserver.exceptions import ToolError
from robot.utils import escape as robot_escape

from .bridge import KeywordError, KeywordTimeout, RobotBridge

mcp = MCPServer("rf-browser-mcp")
_bridge = RobotBridge()

# Default time to wait for one keyword's reply from the RF thread.
_DEFAULT_CALL_TIMEOUT_S = 60.0


class _Raw(str):
    """An argument passed to Robot Framework verbatim (not escaped), for
    the few places we deliberately want RF syntax such as ``${None}``."""


_NONE = _Raw("${None}")


def _escape(value: Any) -> str:
    """Escape a value so Robot Framework treats it as a literal string.

    ``BuiltIn.run_keyword`` re-parses its arguments exactly like a line in
    a .robot file: ``${var}`` / ``%{ENV}`` are expanded, backslashes are
    consumed, ``name=value`` is treated as a named argument and words like
    ``AND`` / ``ELSE`` are special. User-provided text (passwords, JS
    code, selectors) must never be interpreted that way."""
    if isinstance(value, _Raw):
        return str(value)
    return robot_escape(str(value))


def _args(*positional: Any, **named: Any) -> list[str]:
    """Build an RF-style argument list: required positionals first (as
    escaped strings, skipping None), then optional ``name=value`` strings
    for any keyword arguments that were actually supplied (skipping None
    so RF's own defaults apply)."""
    out = [_escape(p) for p in positional if p is not None]
    out += [f"{k}={_escape(v)}" for k, v in named.items() if v is not None]
    return out


# Short timeout for the quick state probes run after a failure.
_PROBE_TIMEOUT_S = 5.0


def _try(keyword: str, *positional: Any) -> tuple[bool, Any]:
    """Run a keyword for inspection only: never raises, returns (ok, value)."""
    try:
        return True, _bridge.call_keyword(
            f"Browser.{keyword}", _args(*positional), timeout=_PROBE_TIMEOUT_S
        )
    except KeywordError as exc:
        return False, str(exc)


def _page_state() -> dict[str, Any]:
    """Best-effort snapshot of where the session actually is right now."""
    ok, page_ids = _try("Get Page Ids")
    if not ok or not page_ids:
        return {"browser_open": False, "open_pages": 0, "url": None, "title": None}
    _, url = _try("Get Url")
    _, title = _try("Get Title")
    return {
        "browser_open": True,
        "open_pages": len(page_ids),
        "url": url,
        "title": title,
    }


def _format_state(state: dict[str, Any]) -> str:
    if not state["browser_open"]:
        return "- no browser/page is open (call open_browser to start one)"
    return (
        f"- url: {state['url']}\n"
        f"- title: {state['title']}\n"
        f"- open pages: {state['open_pages']}"
    )


def _call(keyword: str, *positional: Any, _timeout: float | None = None, **named: Any) -> Any:
    """Run a Browser keyword. On failure, raise ToolError (so the MCP result
    is flagged isError) with Browser's real message plus a snapshot of the
    page state *after* the failure, so the model re-plans from the actual
    state instead of assuming the step succeeded or nothing changed."""
    try:
        return _bridge.call_keyword(
            f"Browser.{keyword}",
            _args(*positional, **named),
            timeout=_timeout or _DEFAULT_CALL_TIMEOUT_S,
        )
    except KeywordTimeout as exc:
        # The RF thread is still busy with this keyword, so probing the page
        # now would just queue behind it -- report the state as unknown.
        raise ToolError(
            f"'{keyword}' failed: {exc}\n\n"
            "Page state: UNKNOWN -- the keyword may still be running in the "
            "browser. Call session_status before continuing, or reset_session "
            "to start from a clean browser."
        ) from exc
    except KeywordError as exc:
        raise ToolError(
            f"'{keyword}' failed: {exc}\n\n"
            "Page state after the failure (the page may be partially loaded "
            "or unchanged -- verify before continuing):\n"
            f"{_format_state(_page_state())}"
        ) from exc


# --- Browser / context / page lifecycle -----------------------------------


@mcp.tool()
def open_browser(url: str | None = None, browser: str = "chromium", headless: bool = True) -> Any:
    """Launch a browser and open a new page, optionally navigating to a URL.

    browser: one of "chromium", "firefox", "webkit".
    """
    _call("New Browser", browser=browser, headless=headless)
    return _call("New Page", url)


@mcp.tool()
def session_status() -> Any:
    """Report the real current state of the browser session: whether a
    browser is open, how many pages, and the active page's URL and title.
    Call this after any failed step before continuing."""
    return _page_state()


@mcp.tool()
def reset_session(url: str | None = None, browser: str = "chromium", headless: bool = True) -> Any:
    """Close every browser, context, and page, then (if url is given) start
    a fresh browser on that URL. Use this to recover when the page state is
    unreliable after a failure."""
    _try("Close Browser", "ALL")
    if url is None:
        return _page_state()
    open_browser(url=url, browser=browser, headless=headless)
    return _page_state()


@mcp.tool()
def new_page(url: str | None = None) -> Any:
    """Open a new page (tab). Auto-launches a default headless Chromium
    browser first if none is open yet."""
    return _call("New Page", url)


@mcp.tool()
def close_page() -> Any:
    """Close the current active page."""
    return _call("Close Page")


@mcp.tool()
def close_browser() -> Any:
    """Close all open browsers, contexts, and pages."""
    return _call("Close Browser", "ALL")


# --- Navigation -------------------------------------------------------------


@mcp.tool()
def go_to(url: str, timeout_s: float | None = None) -> Any:
    """Navigate the current page to the given URL. Optional timeout_s
    overrides the Browser library's default navigation timeout."""
    timeout = f"{timeout_s} s" if timeout_s is not None else None
    bridge_timeout = max(_DEFAULT_CALL_TIMEOUT_S, (timeout_s or 0) + 30)
    return _call("Go To", url, timeout=timeout, _timeout=bridge_timeout)


@mcp.tool()
def get_url() -> Any:
    """Return the current page URL."""
    return _call("Get Url")


@mcp.tool()
def get_title() -> Any:
    """Return the current page title."""
    return _call("Get Title")


# --- Interaction -------------------------------------------------------------


@mcp.tool()
def click(selector: str) -> Any:
    """Click the element found by the given selector."""
    return _call("Click", selector)


@mcp.tool()
def fill_text(selector: str, text: str) -> Any:
    """Clear the field found by the given selector and fill in the given text
    in one action (fast, no per-character events)."""
    return _call("Fill Text", selector, text)


@mcp.tool()
def type_text(selector: str, text: str, delay_ms: int | None = None) -> Any:
    """Type text into the field found by the given selector one character at
    a time (fires real keydown/keyup events, useful for JS-driven inputs).
    Optional delay_ms adds a delay between keystrokes."""
    delay = f"{delay_ms} ms" if delay_ms is not None else None
    return _call("Type Text", selector, text, delay=delay)


@mcp.tool()
def clear_text(selector: str) -> Any:
    """Clear the text field found by the given selector."""
    return _call("Clear Text", selector)


@mcp.tool()
def press_keys(selector: str, keys: list[str]) -> Any:
    """Press one or more keys (e.g. "Enter", "Control+A") on the element
    found by the given selector, in order."""
    return _call("Press Keys", selector, *keys)


@mcp.tool()
def check_checkbox(selector: str) -> Any:
    """Check the checkbox found by the given selector."""
    return _call("Check Checkbox", selector)


@mcp.tool()
def uncheck_checkbox(selector: str) -> Any:
    """Uncheck the checkbox found by the given selector."""
    return _call("Uncheck Checkbox", selector)


@mcp.tool()
def select_options_by(selector: str, values: list[str], attribute: str = "value") -> Any:
    """Select one or more options in a <select> element found by the given
    selector. attribute is one of "value", "label", "text", "index"."""
    return _call("Select Options By", selector, attribute, *values)


# --- Reading page content -----------------------------------------------------


@mcp.tool()
def get_text(selector: str) -> Any:
    """Return the text content of the element found by the given selector."""
    return _call("Get Text", selector)


@mcp.tool()
def get_attribute(selector: str, attribute: str) -> Any:
    """Return the value of the given HTML attribute of the element found by
    the given selector."""
    return _call("Get Attribute", selector, attribute)


@mcp.tool()
def get_element_count(selector: str) -> Any:
    """Return the number of elements matching the given selector."""
    return _call("Get Element Count", selector)


# --- Waiting -------------------------------------------------------------------


@mcp.tool()
def wait_for_elements_state(selector: str, state: str = "visible", timeout_s: float | None = None) -> Any:
    """Wait for the element found by the given selector to reach the given
    state: "attached", "detached", "visible", "hidden", "enabled",
    "disabled", "editable", "readonly", "selected", "deselected",
    "focused", or "stable"."""
    timeout = f"{timeout_s} s" if timeout_s is not None else None
    # Give the bridge longer than the keyword's own timeout, so a slow but
    # legitimate wait reports Browser's real error instead of a bridge timeout.
    bridge_timeout = max(_DEFAULT_CALL_TIMEOUT_S, (timeout_s or 0) + 30)
    return _call("Wait For Elements State", selector, state, timeout=timeout, _timeout=bridge_timeout)


# --- Screenshots & JS ------------------------------------------------------------


@mcp.tool()
def take_screenshot(filename: str | None = None, selector: str | None = None, full_page: bool = False) -> Any:
    """Take a screenshot of the page (or of one element if selector is
    given) and save it to disk. Returns the saved file path."""
    return _call("Take Screenshot", filename=filename, selector=selector, fullPage=full_page)


@mcp.tool()
def evaluate_javascript(function: str, selector: str | None = None) -> Any:
    """Evaluate arbitrary JavaScript in the page context. If selector is
    given, the matched element is passed into the function as its
    argument, e.g. function="(elem) => elem.textContent"."""
    # selector is the keyword's first positional argument; it must be passed
    # explicitly as ${None} when absent, otherwise the JS code would land in
    # the selector slot.
    return _call("Evaluate JavaScript", selector if selector is not None else _NONE, function)


# --- Escape hatch -----------------------------------------------------------------


@mcp.tool()
def run_keyword(name: str, args: list[str] | None = None) -> Any:
    """Run any Robot Framework Browser-library keyword by name, for
    anything not covered by a dedicated tool above. name is the keyword
    name (e.g. "New Context", "Get Viewport Size"), args is a list of
    strings passed positionally, using "key=value" for optional/named
    arguments -- exactly as you would write them in a .robot file."""
    bare = name.split(".", 1)[1] if name.strip().lower().startswith("browser.") else name
    # Keep "key=value" working as a named argument, but escape the values
    # so ${...} / %{...} / backslashes are taken literally.
    rf_args: list[str] = []
    for arg in args or []:
        key, sep, value = str(arg).partition("=")
        if sep and key.isidentifier():
            rf_args.append(_Raw(f"{key}={_escape(value)}"))
        else:
            rf_args.append(arg)
    return _call(bare, *rf_args)


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()

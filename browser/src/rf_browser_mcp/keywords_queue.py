"""Internal Robot Framework library used by rf_browser_mcp.

An MCP tool call happens on the asyncio/main thread. Robot Framework's
Browser library, however, needs a real, fully-initialized RF execution
context (for timeouts, logging, output files, etc.) that stays alive for
the whole browser session -- not just for one keyword call.

The trick: we start exactly one Robot Framework suite/test in a dedicated
background thread. Its one and only top-level keyword is
``Run Session Queue`` (this library's ``run_session_queue`` method), which
blocks in a loop pulling ``(keyword_name, args)`` jobs off a thread-safe
queue, executes each one via ``BuiltIn().run_keyword`` (so it runs exactly
as if it were a normal step in a .robot test), and pushes the result (or
error) onto a reply queue. The MCP server pushes jobs and blocks on the
reply queue, giving synchronous, one-keyword-at-a-time control over a
Browser-library session that stays open across many separate MCP tool
calls.
"""

from __future__ import annotations

import queue as _queue
from typing import Any

from robot.libraries.BuiltIn import BuiltIn

# session_id -> (in_queue, out_queue). Populated by bridge.py before the
# background RF thread starts, looked up by QueueRunner.__init__ when RF
# imports this library into the running suite.
_SESSIONS: dict[str, tuple["_queue.Queue", "_queue.Queue"]] = {}


def register_session(session_id: str, in_q: "_queue.Queue", out_q: "_queue.Queue") -> None:
    _SESSIONS[session_id] = (in_q, out_q)


def unregister_session(session_id: str) -> None:
    _SESSIONS.pop(session_id, None)


class QueueRunner:
    """Robot Framework test library: executes keywords handed to it over
    a queue until told to stop. Not meant to be used from a .robot file
    directly -- rf_browser_mcp wires it up programmatically."""

    ROBOT_LIBRARY_SCOPE = "GLOBAL"

    def __init__(self, session_id: str):
        self._in_q, self._out_q = _SESSIONS[session_id]

    def run_session_queue(self) -> None:
        bi = BuiltIn()
        while True:
            job = self._in_q.get()
            if job is None:  # sentinel: stop the session
                break
            # job_id is echoed back so the caller can discard a late reply
            # for a call it already gave up on (see RobotBridge.call_keyword).
            job_id, name, args = job
            try:
                result: Any = bi.run_keyword(name, *args)
                self._out_q.put((job_id, "ok", result))
            except Exception as exc:  # keyword failed -- report, keep looping
                self._out_q.put((job_id, "error", str(exc)))
        # Best-effort cleanup so we don't leak browser/node processes.
        try:
            bi.run_keyword("Browser.Close Browser", "ALL")
        except Exception:
            pass

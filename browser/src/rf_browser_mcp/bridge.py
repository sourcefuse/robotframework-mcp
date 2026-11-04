"""Owns the single, persistent Robot Framework execution context that
backs the MCP server, and exposes a synchronous ``call_keyword`` API to
run Browser-library keywords against it."""

from __future__ import annotations

import itertools
import queue
import threading
import time
import uuid
from typing import Any

from robot.running import TestSuite

from . import keywords_queue as kq


class KeywordError(Exception):
    """Raised when a Browser-library keyword call fails or times out."""


class KeywordTimeout(KeywordError):
    """Raised when the bridge stops waiting for a keyword. The keyword may
    still be running on the RF thread, so the page state is unknown."""


class _ReadyListener:
    """RF listener (v3 API) used only to detect the moment our one test
    actually starts running -- i.e. after all suite-level library imports
    (Browser included, which starts its Node side-car process) have
    finished successfully. Signaling readiness right after *building* the
    suite object would be wrong: the imports haven't happened yet at that
    point, they happen inside ``suite.run()``."""

    ROBOT_LISTENER_API_VERSION = 3

    def __init__(self, ready_event: threading.Event):
        self._ready_event = ready_event

    def start_test(self, data, result) -> None:
        self._ready_event.set()


class RobotBridge:
    def __init__(self, outputdir: str = "rf_browser_mcp_output"):
        self._session_id = uuid.uuid4().hex
        self._in_q: "queue.Queue" = queue.Queue()
        self._out_q: "queue.Queue" = queue.Queue()
        self._outputdir = outputdir
        self._thread: threading.Thread | None = None
        self._call_lock = threading.Lock()
        self._job_ids = itertools.count(1)
        self._started = False
        self._start_error: str | None = None
        self._start_event = threading.Event()

    def start(self) -> None:
        if self._started:
            return
        kq.register_session(self._session_id, self._in_q, self._out_q)

        def _run() -> None:
            try:
                suite = TestSuite("MCP Browser Session")
                suite.resource.imports.library("Browser")
                suite.resource.imports.library(
                    "rf_browser_mcp.keywords_queue.QueueRunner",
                    args=(self._session_id,),
                )
                test = suite.tests.create("Session")
                test.body.create_keyword(name="Run Session Queue")
                result = suite.run(
                    outputdir=self._outputdir,
                    console="NONE",
                    listener=_ReadyListener(self._start_event),
                )
                # If the suite failed before our test ever started (e.g. a
                # library import error), the listener's start_test never
                # fired -- make sure start() doesn't hang forever.
                if not self._start_event.is_set():
                    self._start_error = (
                        f"Robot Framework session ended before it started "
                        f"(return code {result.return_code})"
                    )
                    self._start_event.set()
            except Exception as exc:  # suite build / library import failure
                self._start_error = str(exc)
                self._start_event.set()

        self._thread = threading.Thread(
            target=_run, name="rf-browser-mcp-session", daemon=True
        )
        self._thread.start()

        if not self._start_event.wait(timeout=60):
            raise KeywordError("Timed out starting Robot Framework session")
        if self._start_error:
            raise KeywordError(
                f"Failed to start Robot Framework session: {self._start_error}"
            )
        self._started = True

    def call_keyword(self, name: str, args: list[str] | None = None, timeout: float = 60.0) -> Any:
        if not self._started:
            self.start()
        with self._call_lock:
            job_id = next(self._job_ids)
            self._in_q.put((job_id, name, list(args or [])))
            deadline = time.monotonic() + timeout
            while True:
                remaining = deadline - time.monotonic()
                try:
                    if remaining <= 0:
                        raise queue.Empty
                    reply_id, status, payload = self._out_q.get(timeout=remaining)
                except queue.Empty as exc:
                    raise KeywordTimeout(
                        f"Timed out after {timeout}s waiting for keyword '{name}' "
                        f"(it may still be running; its result will be discarded)"
                    ) from exc
                if reply_id == job_id:
                    break
                # Late reply from an earlier call that already timed out --
                # drop it so it is never returned as this call's result.
        if status == "error":
            raise KeywordError(payload)
        return payload

    def stop(self, timeout: float = 30.0) -> None:
        if not self._started:
            return
        self._in_q.put(None)
        if self._thread is not None:
            self._thread.join(timeout=timeout)
        kq.unregister_session(self._session_id)
        self._started = False

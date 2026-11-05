"""Records the Browser-library keywords that actually ran (and passed) in
the live session, and renders them as a reviewable .robot test.

Steps are captured in the server's ``_call`` only after the keyword
returns successfully, using the exact argument strings that were handed to
``BuiltIn.run_keyword``. Since run_keyword parses its arguments like a
line in a .robot file, the exported file replays the same calls. Only
whitespace and empty values need extra encoding, because in a file they
would otherwise split or drop cells.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
import tempfile
import threading
from dataclasses import dataclass
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Any

_SEP = "    "
# A value the assistant read is shown as a commented assertion; long values
# are cut so the file stays readable.
_MAX_OBSERVED_LEN = 200


@dataclass(frozen=True)
class Step:
    keyword: str
    args: tuple[str, ...]
    # For read-only calls: the value that was observed. Rendered as a
    # commented-out "Keyword  args  ==  value" assertion.
    observed: Any = None
    is_observation: bool = False


def _space_run(match: re.Match) -> str:
    run = match.group(0)
    text = match.string
    at_edge = match.start() == 0 or match.end() == len(text)
    if len(run) >= 2 or at_edge:
        return "${SPACE}" * len(run)
    return run


def _normalize(name: str) -> str:
    name = name.strip()
    if name.lower().startswith("browser."):
        name = name.split(".", 1)[1]
    return name.lower().replace(" ", "").replace("_", "")


@lru_cache(maxsize=1)
def _browser_keyword_args() -> dict[str, tuple[set[str], bool]]:
    """{normalized keyword name: (parameter names, accepts **kwargs)} for
    the Browser library. Browser is a dynamic library, so the arguments come
    from libdoc. It runs in a subprocess to stay clear of the live RF run."""
    with tempfile.TemporaryDirectory() as tmp:
        spec = Path(tmp) / "browser.json"
        subprocess.run(
            [sys.executable, "-m", "robot.libdoc", "--format", "JSON", "Browser", str(spec)],
            check=True,
            capture_output=True,
            timeout=120,
        )
        data = json.loads(spec.read_text(encoding="utf-8"))
    out: dict[str, tuple[set[str], bool]] = {}
    for kw in data.get("keywords", []):
        args = kw.get("args", [])
        names = {a["name"] for a in args if a.get("kind") != "VAR_NAMED"}
        var_kw = any(a.get("kind") == "VAR_NAMED" for a in args)
        out[_normalize(kw["name"])] = (names, var_kw)
    return out


def _named_params(keyword: str) -> tuple[set[str], bool] | None:
    """(parameter names, accepts **kwargs) for a Browser keyword, or None
    if it can't be looked up (then escapes are kept, which is always safe)."""
    try:
        return _browser_keyword_args().get(_normalize(keyword))
    except Exception:
        return None


# "\=" that is a real escape, i.e. not preceded by another escaped backslash.
_ESCAPED_EQ = re.compile(r"(?<!\\)((?:\\\\)*)\\=")


def readable(keyword: str, value: str) -> str:
    """Drop "\\=" escapes that RF doesn't need in this cell, so selectors read
    as ``id=user`` instead of ``id\\=user``. An "=" only needs escaping when
    the text before it would be taken as a named argument of this keyword."""
    if "\\=" not in value:
        return value
    params = _named_params(keyword)
    if params is None:
        return value
    names, var_kw = params
    plain = _ESCAPED_EQ.sub(lambda m: m.group(1) + "=", value)
    prefix = plain.split("=", 1)[0]
    if prefix in names or (var_kw and prefix.isidentifier()):
        # Keep the first "=" escaped so it stays a positional value.
        return prefix + "\\=" + plain[len(prefix) + 1:]
    return plain


def format_cell(value: str) -> str:
    """Make an (already RF-escaped) argument safe to place in one cell of
    a space-separated .robot file."""
    if value == "":
        return "${EMPTY}"
    value = value.replace("\r", "\\r").replace("\n", "\\n").replace("\t", "\\t")
    value = re.sub(r" +", _space_run, value)
    if value.startswith("#"):
        value = "\\" + value
    return value


def _format_test_name(name: str) -> str:
    name = " ".join(str(name).split())
    return name or "Recorded Session"


def _observed_cell(value: Any) -> str:
    from robot.utils import escape as robot_escape

    text = str(value)
    if len(text) > _MAX_OBSERVED_LEN:
        text = text[:_MAX_OBSERVED_LEN] + "..."
    return format_cell(robot_escape(text))


class SessionRecorder:
    def __init__(self) -> None:
        self._steps: list[Step] = []
        self._lock = threading.Lock()

    def record(self, keyword: str, args: list[str]) -> None:
        with self._lock:
            self._steps.append(Step(keyword, tuple(args)))

    def observe(self, keyword: str, args: list[str], value: Any) -> None:
        with self._lock:
            self._steps.append(Step(keyword, tuple(args), value, is_observation=True))

    def clear(self) -> None:
        with self._lock:
            self._steps.clear()

    @property
    def action_count(self) -> int:
        with self._lock:
            return sum(1 for s in self._steps if not s.is_observation)

    def render(self, test_name: str = "Recorded Session") -> str:
        with self._lock:
            steps = list(self._steps)
        lines = [
            "*** Settings ***",
            f"Documentation{_SEP}Recorded by rf-browser-mcp on "
            f"{datetime.now().strftime('%Y-%m-%d %H:%M')}. Review before committing.",
            f"...{_SEP}Only steps that passed are included. Commented \"==\" lines are",
            f"...{_SEP}values the assistant read: uncomment them to turn them into assertions.",
            f"...{_SEP}Typed values are recorded as-is, so replace any secrets with variables.",
            f"Library{_SEP}Browser",
            "",
            "*** Test Cases ***",
            _format_test_name(test_name),
        ]
        if not steps:
            lines.append(f"{_SEP}No Operation{_SEP}# nothing was recorded")
        for step in steps:
            cells = [step.keyword, *(format_cell(readable(step.keyword, a)) for a in step.args)]
            if step.is_observation:
                cells += ["==", _observed_cell(step.observed)]
                lines.append(f"{_SEP}# " + _SEP.join(cells))
            else:
                lines.append(_SEP + _SEP.join(cells))
        return "\n".join(lines) + "\n"

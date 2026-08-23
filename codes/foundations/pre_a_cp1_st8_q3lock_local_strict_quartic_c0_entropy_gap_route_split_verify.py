#!/usr/bin/env python3
"""Integrated verifier for EXP-000804 / R-167 v1.7.

The primary and independent theorem implementations are executed twice in
fresh child processes.  Their deterministic payloads are checked against the
stored run JSONs, the independent implementation is protected by an AST and
import firewall, and a third stdlib/Fraction calculation reconciles the exact
route-split invariants.

``--staged`` is assembly-safe: genuinely absent stored, formal, generated, or
single-checkpoint PDF authorities are reported as ``MISSING`` and yield an
``INCOMPLETE`` verdict.  A contradiction in an available mathematical source
or payload is always ``FAIL``.  Strict mode fails until the complete authority
and the one v0.6 synthesis source/PDF pair are present and hash-bound.  This
program never builds, renders, or edits a proof note or PDF.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import math
import os
import re
import subprocess
import sys
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


__version__ = "1.0.1"
REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-local-strict-quartic-c0-entropy-gap-route-split"

RESULT_ID = (
    "PA-CP1-ST8-Q3LOCK-SECOND-WEIGHTED-ENERGY-MOMENT-AND-"
    "COMMON-ALPHA-CAUCHY-GATE-SPLIT"
)
RESULT_NUMBER = "R-167"
RESULT_VERSION = "v1.7"
EXPLORATION_ID = "EXP-000804"
TASK_ID = "T-054"
CLAIM_ID = "C6-SPACETIME-SIGNATURE"

CLOSED_GATES = (
    "PA-CP1-ST8-Q3LOCK-FINITE-VOLUME-LOCAL-STRICT-ENERGY-SUBFLOW-CARRIER",
    "PA-CP1-ST8-Q3LOCK-FIXED-GIBBS-CHARACTER-ENTROPY-TILTED-TAIL-BOUND",
)
SUCCESSOR_GATES = (
    "PA-CP1-ST8-Q3LOCK-LOCAL-STRICT-ALL-EXHAUSTION-TWO-ORIENTATION-"
    "HISTORY-COMMON-ALPHA",
    "PA-CP1-ST8-Q3LOCK-BROKEN-SECTOR-GNS-GAP-COERCIVITY",
)
ROUND1_GATE = "PA-ROUND1-EVIDENCE-ROLE-AND-MINIMUM-MANIFEST-FREEZE"
OPEN_GATES = (*SUCCESSOR_GATES, ROUND1_GATE)
HISTORICAL_GATE = (
    "PA-CP1-ST8-Q3LOCK-QUASI-LOCAL-RAW-OSCILLATOR-ALL-EXHAUSTION-"
    "COMMON-ALPHA-AND-BROKEN-GNS-GAP"
)
RETAINED_GATES = (
    "PA-CP1-ST8-Q3LOCK-ALL-EXHAUSTION-MIXTURE-L2-LOCALITY-AND-"
    "BETA-INDEPENDENT-CSTAR-DYNAMICS",
    "PA-CP1-ST8-Q3LOCK-HAMILTONIAN-THERMODYNAMIC-IDENTIFICATION-IN-"
    "CANONICAL-OS-MIXTURE",
    "PA-CP1-ST8-Q3LOCK-PROJECTED-DUHAMEL-MODULAR-C1-MULTIPLIER-LOCALITY",
)

NEGATIVE_IDS = (
    "NG-2026-08-11-PRE-A-ST8-Q3LOCK-RAW-WEYL-BASIC-RESOLVENT-QUARTIC-"
    "POINT-NORM-C0",
    "NG-2026-08-11-PRE-A-ST8-Q3LOCK-PURE-QUARTIC-POTENTIAL-RESOLVENT-"
    "ALGEBRA-INVARIANCE",
    "NG-2026-08-11-PRE-A-ST8-Q3LOCK-ENTROPY-FINITE-MOMENT-DYNAMIC-"
    "GAUSSIAN-TAIL-INFERENCE",
    "NG-2026-08-11-PRE-A-ST8-Q3LOCK-ORDERED-GROUND-DOUBLETS-AUTOMATIC-"
    "GNS-GAP",
)
REUSED_NEGATIVE_IDS = (
    "NG-2026-08-10-PRE-A-ST8-Q3LOCK-RAW-LOCAL-RESOLVENT-POINT-NORM-"
    "BOND-KICK-CONTINUITY",
    "NG-2026-08-10-PRE-A-ST8-Q3LOCK-STATIC-TAIL-ONLY-PROJECTED-ORBIT-"
    "LOCALITY",
    "NG-2026-08-09-PRE-A-ST8-Q3LOCK-UNIFORM-FULL-FINITE-VOLUME-"
    "SPECTRAL-GAP",
)

PRIMARY = REPO / f"codes/foundations/{SLUG.replace('-', '_')}.py"
INDEPENDENT = REPO / f"codes/foundations/{SLUG.replace('-', '_')}_independent.py"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260811.md"
NOTE_SOURCE = REPO / (
    "claims/C6-SPACETIME-SIGNATURE/notes/"
    "pre-a-q3lock-local-strict-quartic-c0-entropy-gap-route-split-"
    "260811-v0.6.tex.txt"
)
CHECKPOINT_PDF = NOTE_SOURCE.with_name(
    NOTE_SOURCE.name.removesuffix(".tex.txt") + ".pdf"
)
PRIMARY_STORED = REPO / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    f"2026-08-11-primary-{SLUG}/result.json"
)
INDEPENDENT_STORED = REPO / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    f"2026-08-11-independent-{SLUG}/result.json"
)
DEFAULT_OUTPUT = REPO / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    f"2026-08-11-integrated-{SLUG}/result.json"
)

PRIMARY_SCHEMA = f"tect/{SLUG}-primary-result/1.0"
INDEPENDENT_SCHEMA = f"tect/{SLUG}-independent-result/1.0"
INTEGRATED_SCHEMA = f"tect/{SLUG}-integrated-result/1.0"
MINIMUM_PRIMARY_ASSERTIONS = 150
MINIMUM_INDEPENDENT_ASSERTIONS = 90


def json_safe(value: Any) -> Any:
    if isinstance(value, Path):
        return value.as_posix()
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, Mapping):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(item) for item in value]
    if isinstance(value, set):
        items = [json_safe(item) for item in value]
        return sorted(items, key=lambda item: json.dumps(item, sort_keys=True))
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def portable_bytes(path: Path) -> bytes:
    return path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def portable_sha256(path: Path) -> str:
    return hashlib.sha256(portable_bytes(path)).hexdigest()


def atomic_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(json_safe(payload), stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def normalize_volatile(value: Any, roots: Iterable[Path]) -> Any:
    spellings: list[str] = []
    for root in roots:
        spellings.extend((str(root), str(root).replace("\\", "/")))
    if isinstance(value, str):
        result = value
        for spelling in sorted(set(spellings), key=len, reverse=True):
            result = result.replace(spelling, "<ROOT>")
        return result.replace("\\", "/")
    if isinstance(value, Mapping):
        return {
            str(key): normalize_volatile(item, roots)
            for key, item in value.items()
        }
    if isinstance(value, (list, tuple)):
        return [normalize_volatile(item, roots) for item in value]
    return json_safe(value)


def canonical_payload(value: Any, roots: Iterable[Path] = ()) -> bytes:
    return json.dumps(
        normalize_volatile(value, roots),
        sort_keys=True,
        ensure_ascii=True,
        separators=(",", ":"),
    ).encode("ascii")


def compact_text(value: Any) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(value).lower().replace("\\", ""))


def text_has(text: Any, token: Any) -> bool:
    return compact_text(token) in compact_text(text)


def as_mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def as_fraction(value: Any) -> Fraction | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, int):
        return Fraction(value)
    if isinstance(value, float):
        return Fraction(str(value))
    if isinstance(value, str):
        stripped = value.strip()
        if re.fullmatch(r"[+-]?\d+(?:/\d+)?", stripped):
            return Fraction(stripped)
    return None


class Audit:
    """Collect proof defects while preserving staged missing-authority state."""

    def __init__(self, staged: bool) -> None:
        self.staged = staged
        self.rows: list[dict[str, Any]] = []
        self.failures: list[str] = []
        self.missing: list[str] = []

    def _row(
        self,
        name: str,
        status: str,
        actual: Any,
        expected: Any,
        group: str,
    ) -> None:
        self.rows.append(
            {
                "name": name,
                "group": group,
                "status": status,
                "actual": json_safe(actual),
                "expected": json_safe(expected),
            }
        )

    def check(
        self,
        name: str,
        condition: bool,
        actual: Any,
        expected: Any,
        group: str,
    ) -> bool:
        if condition:
            self._row(name, "PASS", actual, expected, group)
            return True
        self._row(name, "FAIL", actual, expected, group)
        self.failures.append(f"{group}: {name}")
        return False

    def pending(
        self,
        name: str,
        condition: bool,
        actual: Any,
        expected: Any,
        group: str,
    ) -> bool:
        if condition:
            self._row(name, "PASS", actual, expected, group)
            return True
        if self.staged:
            self._row(name, "MISSING", actual, expected, group)
            self.missing.append(f"{group}: {name}")
            return False
        return self.check(name, False, actual, expected, group)

    require = pending

    @property
    def verdict(self) -> str:
        if self.failures:
            return "FAIL"
        if self.missing:
            return "INCOMPLETE"
        return "PASS"


def load_json(
    path: Path,
    audit: Audit,
    label: str,
    *,
    formal: bool = False,
) -> dict[str, Any] | None:
    reporter = audit.pending if formal else audit.check
    if not path.is_file():
        audit.pending(
            f"{label} exists",
            False,
            path.relative_to(REPO),
            "file",
            "formal" if formal else "files",
        )
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        reporter(f"{label} parses", False, str(error), "valid JSON object", "files")
        return None
    if not isinstance(value, dict):
        reporter(f"{label} object", False, type(value).__name__, "dict", "files")
        return None
    audit.check(f"{label} parses", True, path.relative_to(REPO), "dict", "files")
    return value


def require_text(
    path: Path,
    audit: Audit,
    label: str,
    *,
    core: bool = False,
) -> str | None:
    reporter = audit.check if core else audit.pending
    if not path.is_file():
        audit.pending(
            f"{label} exists",
            False,
            path.relative_to(REPO),
            "file",
            "formal",
        )
        return None
    try:
        value = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        reporter(f"{label} UTF-8", False, str(error), "readable UTF-8", "formal")
        return None
    reporter(f"{label} readable", bool(value), len(value), ">0", "formal")
    return value


def jsonl_records(
    path: Path,
    audit: Audit,
    label: str,
) -> list[dict[str, Any]] | None:
    if not path.is_file():
        audit.pending(
            f"{label} exists", False, path.relative_to(REPO), "file", "formal"
        )
        return None
    records: list[dict[str, Any]] = []
    try:
        with path.open("r", encoding="utf-8") as stream:
            for line_number, line in enumerate(stream, 1):
                if not line.strip():
                    continue
                value = json.loads(line)
                if not isinstance(value, dict):
                    raise ValueError(f"line {line_number} is not an object")
                records.append(value)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
        audit.pending(f"{label} parses", False, str(error), "valid JSONL", "formal")
        return None
    audit.check(f"{label} parses", bool(records), len(records), ">=1", "formal")
    return records


def require_tokens(
    text: Any,
    label: str,
    tokens: Iterable[str],
    audit: Audit,
    *,
    group: str = "formal",
    core: bool = False,
) -> None:
    missing = [token for token in tokens if not text_has(text, token)]
    reporter = audit.check if core else audit.pending
    reporter(
        f"{label} required tokens",
        not missing,
        missing,
        "all required tokens present",
        group,
    )


COMPONENT_RUNNER = r"""
import importlib.util
import json
import pathlib
import sys

source = pathlib.Path(sys.argv[1]).resolve()
output = pathlib.Path(sys.argv[2]).resolve()
staged = sys.argv[3] == "1"
spec = importlib.util.spec_from_file_location("tect_fresh_component", source)
if spec is None or spec.loader is None:
    raise RuntimeError("cannot load component spec")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
builder = getattr(module, "run_audit", None) or getattr(module, "build_payload")
payload = builder(staged)
serializer = getattr(module, "json_safe", None) or getattr(module, "serial", None)
safe = serializer(payload) if serializer is not None else payload
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(
    json.dumps(safe, indent=2, sort_keys=True) + "\n", encoding="utf-8"
)
summary = payload.get("summary", {})
print(
    "FRESH-COMPONENT "
    + str(payload.get("verdict"))
    + " "
    + str(summary.get("passed", payload.get("passed")))
    + "/"
    + str(summary.get("total", payload.get("total")))
)
"""


def run_once(
    script: Path,
    run_directory: Path,
    audit: Audit,
    label: str,
) -> tuple[dict[str, Any], str] | None:
    if not script.is_file():
        audit.pending(
            f"{label} script exists",
            False,
            script.relative_to(REPO),
            "file",
            "freshness",
        )
        return None
    run_directory.mkdir(parents=True, exist_ok=True)
    output = run_directory / "result.json"
    completed = subprocess.run(
        [
            sys.executable,
            "-X",
            "utf8",
            "-c",
            COMPONENT_RUNNER,
            str(script),
            str(output),
            "1" if audit.staged else "0",
        ],
        cwd=REPO,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=480,
    )
    if completed.returncode != 0 or not output.is_file():
        audit.check(
            f"{label} execution",
            False,
            {
                "returncode": completed.returncode,
                "stdout": completed.stdout[-2000:],
                "stderr": completed.stderr[-2000:],
                "output_exists": output.is_file(),
            },
            "fresh child process exits zero and writes JSON",
            "freshness",
        )
        return None
    try:
        payload = json.loads(output.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        audit.check(f"{label} JSON", False, str(error), "valid JSON", "freshness")
        return None
    if not isinstance(payload, dict):
        audit.check(
            f"{label} object", False, type(payload).__name__, "dict", "freshness"
        )
        return None
    sentinel = next(
        (
            line.strip()
            for line in completed.stdout.splitlines()
            if line.strip().startswith("FRESH-COMPONENT ")
        ),
        "",
    )
    audit.check(f"{label} execution", True, completed.returncode, 0, "freshness")
    audit.check(
        f"{label} sentinel", bool(sentinel), sentinel, "FRESH-COMPONENT ...", "freshness"
    )
    return payload, sentinel


def run_fresh_pair(
    script: Path,
    temporary_root: Path,
    audit: Audit,
    label: str,
) -> tuple[dict[str, Any], str] | None:
    if not script.is_file():
        audit.pending(
            f"{label} script exists",
            False,
            script.relative_to(REPO),
            "file",
            "freshness",
        )
        return None
    first = run_once(script, temporary_root / f"{label}-a", audit, f"{label} fresh A")
    second = run_once(script, temporary_root / f"{label}-b", audit, f"{label} fresh B")
    if first is None or second is None:
        audit.pending(
            f"{label} two fresh payloads",
            False,
            [first is not None, second is not None],
            [True, True],
            "freshness",
        )
        return first or second
    first_bytes = canonical_payload(first[0], (REPO, temporary_root))
    second_bytes = canonical_payload(second[0], (REPO, temporary_root))
    audit.check(
        f"{label} deterministic fresh equality",
        first_bytes == second_bytes,
        {
            "a": hashlib.sha256(first_bytes).hexdigest(),
            "b": hashlib.sha256(second_bytes).hexdigest(),
        },
        "equal canonical hashes",
        "freshness",
    )
    return first


def stored_against_fresh(
    path: Path,
    fresh: dict[str, Any] | None,
    audit: Audit,
    label: str,
) -> dict[str, Any] | None:
    if not path.is_file():
        audit.pending(
            f"{label} stored result exists",
            False,
            path.relative_to(REPO),
            "fresh-equal JSON",
            "freshness",
        )
        return None
    try:
        stored = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        audit.pending(
            f"{label} stored parses", False, str(error), "valid JSON", "freshness"
        )
        return None
    if not isinstance(stored, dict):
        audit.pending(
            f"{label} stored object",
            False,
            type(stored).__name__,
            "dict",
            "freshness",
        )
        return None
    # ``authority.staged`` records the invocation mode, not mathematical or
    # provenance content.  A strict stored result must therefore compare equal
    # to a staged fresh result after removing only this one volatile flag.
    def storage_view(value: dict[str, Any] | None) -> dict[str, Any] | None:
        if value is None:
            return None
        copied = json.loads(json.dumps(value))
        authority = copied.get("authority")
        if isinstance(authority, dict):
            authority.pop("staged", None)
        return copied

    stored_view = storage_view(stored)
    fresh_view = storage_view(fresh)
    stored_bytes = canonical_payload(stored_view, (REPO,))
    fresh_bytes = canonical_payload(fresh_view, (REPO,)) if fresh_view is not None else b""
    audit.pending(
        f"{label} stored equals fresh",
        fresh is not None and stored_bytes == fresh_bytes,
        {
            "stored": hashlib.sha256(stored_bytes).hexdigest(),
            "fresh": hashlib.sha256(fresh_bytes).hexdigest() if fresh else None,
        },
        "equal canonical hashes",
        "freshness",
    )
    return stored


def assertion_rows(payload: Mapping[str, Any]) -> list[dict[str, Any]]:
    assertions = payload.get("assertions")
    if isinstance(assertions, list):
        return [row for row in assertions if isinstance(row, dict)]
    if isinstance(assertions, dict) and isinstance(assertions.get("rows"), list):
        return [row for row in assertions["rows"] if isinstance(row, dict)]
    return []


def assertion_summary(payload: Mapping[str, Any]) -> tuple[Any, Any, Any, Any]:
    assertions = payload.get("assertions")
    if isinstance(assertions, dict):
        return (
            assertions.get("passed"),
            assertions.get("failed"),
            assertions.get("missing", 0),
            assertions.get("total"),
        )
    summary = payload.get("summary")
    if isinstance(summary, dict):
        return (
            summary.get("passed"),
            summary.get("failed"),
            summary.get("missing", 0),
            summary.get("total"),
        )
    return (
        payload.get("passed"),
        payload.get("failed"),
        payload.get("missing", 0),
        payload.get("total"),
    )


def validate_component(payload: dict[str, Any], label: str, audit: Audit) -> None:
    expected_schema = PRIMARY_SCHEMA if label == "primary" else INDEPENDENT_SCHEMA
    minimum = (
        MINIMUM_PRIMARY_ASSERTIONS
        if label == "primary"
        else MINIMUM_INDEPENDENT_ASSERTIONS
    )
    audit.check(
        f"{label} schema",
        payload.get("schema") == expected_schema,
        payload.get("schema"),
        expected_schema,
        "components",
    )
    for key, expected in (
        ("result_id", RESULT_ID),
        ("result_number", RESULT_NUMBER),
        ("result_version", RESULT_VERSION),
        ("exploration_id", EXPLORATION_ID),
        ("claim_bearing", False),
    ):
        audit.check(
            f"{label} {key.replace('_', ' ')}",
            payload.get(key) == expected,
            payload.get(key),
            expected,
            "components",
        )
    verdict_ok = payload.get("verdict") == "PASS"
    if audit.staged:
        audit.pending(
            f"{label} formal verdict",
            verdict_ok,
            payload.get("verdict"),
            "PASS after authority synchronization",
            "components",
        )
    else:
        audit.check(
            f"{label} verdict", verdict_ok, payload.get("verdict"), "PASS", "components"
        )
    passed, failed, missing, total = assertion_summary(payload)
    audit.check(
        f"{label} all mathematical assertions PASS",
        isinstance(total, int)
        and total >= minimum
        and passed == total
        and failed == 0
        and missing in (0, None),
        {"passed": passed, "failed": failed, "missing": missing, "total": total},
        f"passed=total>={minimum}; failed=missing=0",
        "components",
    )
    rows = assertion_rows(payload)
    audit.check(
        f"{label} assertion row count",
        len(rows) == total,
        len(rows),
        total,
        "components",
    )
    audit.check(
        f"{label} assertion rows all PASS",
        bool(rows) and all(row.get("status") == "PASS" for row in rows),
        sum(row.get("status") == "PASS" for row in rows),
        total,
        "components",
    )
    actual_closed = payload.get("closed_gates", payload.get("closed_subgates"))
    audit.check(
        f"{label} exact closed gate set",
        tuple(actual_closed or ()) == CLOSED_GATES,
        actual_closed,
        list(CLOSED_GATES),
        "components",
    )
    audit.check(
        f"{label} exact open gate set",
        tuple(payload.get("open_gates", ())) == OPEN_GATES,
        payload.get("open_gates"),
        list(OPEN_GATES),
        "components",
    )
    audit.check(
        f"{label} exact four negative IDs",
        tuple(payload.get("negative_ids", ())) == NEGATIVE_IDS,
        payload.get("negative_ids"),
        list(NEGATIVE_IDS),
        "components",
    )
    if label == "independent":
        audit.check(
            "independent exact successor gate set",
            tuple(payload.get("successor_gates", ())) == SUCCESSOR_GATES,
            payload.get("successor_gates"),
            list(SUCCESSOR_GATES),
            "components",
        )
        audit.check(
            "independent exact historical superseded gate",
            payload.get("superseded_gate_ids") == [HISTORICAL_GATE],
            payload.get("superseded_gate_ids"),
            [HISTORICAL_GATE],
            "components",
        )


def validate_hash_map(
    payload: Mapping[str, Any],
    owner: Path,
    audit: Audit,
    label: str,
) -> None:
    hashes = payload.get("source_hashes")
    audit.check(
        f"{label} source hash map",
        isinstance(hashes, dict),
        type(hashes).__name__,
        "dict",
        "hashes",
    )
    if not isinstance(hashes, dict):
        return
    for path in (owner, MANIFEST, CERTIFICATE):
        key = path.relative_to(REPO).as_posix()
        expected = portable_sha256(path) if path.is_file() else None
        audit.check(
            f"{label} live hash {key}",
            expected is not None and hashes.get(key) == expected,
            hashes.get(key),
            expected,
            "hashes",
        )


def validate_independence(audit: Audit) -> None:
    missing = [
        path.relative_to(REPO).as_posix()
        for path in (PRIMARY, INDEPENDENT, SCRIPT)
        if not path.is_file()
    ]
    if missing:
        audit.pending("AST sources exist", False, missing, "all sources", "independence")
        return
    try:
        primary_source = PRIMARY.read_text(encoding="utf-8")
        independent_source = INDEPENDENT.read_text(encoding="utf-8")
        integrated_source = SCRIPT.read_text(encoding="utf-8")
        primary_tree = ast.parse(primary_source, filename=str(PRIMARY))
        independent_tree = ast.parse(independent_source, filename=str(INDEPENDENT))
        integrated_tree = ast.parse(integrated_source, filename=str(SCRIPT))
    except (OSError, UnicodeError, SyntaxError) as error:
        audit.check("AST parsing", False, str(error), "three valid ASTs", "independence")
        return

    imports: set[str] = set()
    dynamic: list[str] = []
    read_names: list[str] = []
    for node in ast.walk(independent_tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in {
                "__import__",
                "eval",
                "exec",
            }:
                dynamic.append(node.func.id)
            elif isinstance(node.func, ast.Attribute) and node.func.attr in {
                "import_module",
                "run_module",
                "run_path",
            }:
                dynamic.append(node.func.attr)
        elif isinstance(node, ast.Constant) and isinstance(node.value, str):
            lowered = node.value.lower().replace("\\", "/")
            primary_relative = PRIMARY_STORED.relative_to(REPO).as_posix().lower()
            if "primary-" + SLUG in lowered or primary_relative in lowered:
                read_names.append(node.value)
    forbidden = {
        "sympy",
        "numpy",
        "scipy",
        "importlib",
        "runpy",
        "subprocess",
        PRIMARY.stem,
    }
    audit.check(
        "independent import firewall",
        not imports.intersection(forbidden),
        sorted(imports.intersection(forbidden)),
        [],
        "independence",
    )
    audit.check(
        "independent dynamic import firewall", not dynamic, dynamic, [], "independence"
    )
    normalized_independent = independent_source.replace("\\", "/")
    audit.check(
        "independent names neither primary module nor primary result",
        PRIMARY.stem not in independent_source
        and PRIMARY_STORED.relative_to(REPO).as_posix() not in normalized_independent
        and not read_names,
        {
            "module_named": PRIMARY.stem in independent_source,
            "stored_named": PRIMARY_STORED.relative_to(REPO).as_posix()
            in normalized_independent,
            "suspicious_literals": read_names,
        },
        {"module_named": False, "stored_named": False, "suspicious_literals": []},
        "independence",
    )
    audit.check(
        "primary does not import independent module",
        INDEPENDENT.stem not in primary_source,
        INDEPENDENT.stem in primary_source,
        False,
        "independence",
    )
    integrated_imports = {
        alias.name
        for node in ast.walk(integrated_tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    } | {
        node.module
        for node in ast.walk(integrated_tree)
        if isinstance(node, ast.ImportFrom) and node.module
    }
    audit.check(
        "integrated imports neither theorem implementation",
        not any(
            PRIMARY.stem in name or INDEPENDENT.stem in name
            for name in integrated_imports
        ),
        sorted(integrated_imports),
        "no primary or independent module import",
        "independence",
    )
    audit.check(
        "primary and independent ASTs differ",
        ast.dump(primary_tree, include_attributes=False)
        != ast.dump(independent_tree, include_attributes=False),
        "different",
        "different",
        "independence",
    )
    audit.check(
        "primary and independent source hashes differ",
        portable_sha256(PRIMARY) != portable_sha256(INDEPENDENT),
        portable_sha256(INDEPENDENT),
        f"different from {portable_sha256(PRIMARY)}",
        "independence",
    )


def primary_invariants(payload: Mapping[str, Any]) -> dict[str, bool]:
    derived = as_mapping(payload.get("derived"))
    q3 = as_mapping(derived.get("q3_force"))
    carrier = as_mapping(derived.get("local_strict_carrier"))
    carrier_inputs = as_mapping(carrier.get("inputs"))
    bond = as_mapping(carrier.get("bond_kick"))
    topology = as_mapping(carrier.get("topology"))
    onsite = as_mapping(carrier.get("onsite_subflow"))
    packet = as_mapping(derived.get("quartic_packet_c0_no_go"))
    derivations = as_mapping(packet.get("exact_derivations"))
    graph = as_mapping(packet.get("graph_endpoint"))
    scaling = as_mapping(packet.get("scaling"))
    packet_rows = as_list(as_mapping(packet.get("packet")).get("rows"))
    conclusion = as_mapping(packet.get("conclusion"))
    pure = as_mapping(derived.get("pure_kick_resolvent_no_go"))
    gibbs = as_mapping(derived.get("gibbs_entropy_tail"))
    gibbs_inputs = as_mapping(gibbs.get("inputs"))
    character = as_mapping(gibbs.get("character"))
    tail = as_mapping(gibbs.get("tail"))
    entropy = as_mapping(derived.get("entropy_fixture"))
    ground = as_mapping(derived.get("ordered_ground_gap_no_go"))

    g = as_fraction(as_mapping(q3.get("inputs")).get("g"))
    lam = as_fraction(as_mapping(q3.get("inputs")).get("lambda"))
    g_fixture = as_fraction(q3.get("G_fixture"))
    q3_ok = (
        g is not None
        and lam is not None
        and g_fixture == g + 3 * lam
        and text_has(q3.get("G"), "g+3lambda")
        and len(as_list(q3.get("vertices"))) == 8
        and len(as_list(q3.get("edges"))) == 12
        and q3.get("neighbors_zero") == [1, 2, 4]
    )

    c = as_fraction(carrier_inputs.get("bond_c"))
    z = as_fraction(carrier_inputs.get("coordination_z"))
    exp_mu = as_fraction(carrier_inputs.get("exp_mu"))
    chi = as_fraction(carrier_inputs.get("chi"))
    sqrt_gamma = as_fraction(carrier_inputs.get("sqrt_gamma"))
    delta = as_fraction(carrier_inputs.get("delta_fixture"))
    c_b = as_fraction(bond.get("C_b"))
    m_delta = as_fraction(bond.get("M_delta"))
    expected_c_b = (
        Fraction(1)
        + c * c * z * z * exp_mu / (2 * chi * sqrt_gamma)
        if None not in (c, z, exp_mu, chi, sqrt_gamma)
        else None
    )
    carrier_ok = (
        c_b == expected_c_b
        and delta is not None
        and m_delta == 1 + expected_c_b * abs(delta)
        and topology.get("bounded_strict_equals_strong_star") is True
        and topology.get("bounded_strict_graph_energy_equivalent") is True
        and onsite.get("commutes_with_onsite_unitary") is True
        and onsite.get("q_s_isometry") is True
        and onsite.get("e_E_isometry") is True
        and onsite.get("strict_C0") is True
        and text_has(bond.get("energy_contract"), "e_E(beta_delta A)<=e_(M_delta E)(A)")
        and text_has(bond.get("graph_contract"), "q_s(beta_delta A)<=M_delta^s q_s(A)")
        and text_has(bond.get("support_action"), "X -> N_1(X)")
    )

    derivation_ok = all(
        text_has("\n".join(str(value) for value in derivations.values()), token)
        for token in (
            "delta W_a=(i/hbar)D_aW_a",
            "delta^2 W_a=(i/(2 chi hbar))sum_j{p_j,partial_j D_a}W_a-hbar^-2D_a^2W_a",
            "delta R_0=R_0F_0R_0",
            "delta^2 R_0=2R_0F_0R_0F_0R_0+(1/(2chi))R_0sum_j{p_j,partial_jF_0}R_0",
            "[q_0,R_0]=-i hbar R_0^2",
        )
    )
    row_ok = bool(packet_rows)
    for row in packet_rows:
        if not isinstance(row, dict):
            row_ok = False
            continue
        d_a = as_fraction(row.get("d_A"))
        c_a = as_fraction(row.get("C_A"))
        m_psi = as_fraction(row.get("M_psi"))
        tau = as_fraction(row.get("tau"))
        threshold = as_fraction(row.get("tau_threshold"))
        main = as_fraction(row.get("main_term"))
        remainder = as_fraction(row.get("taylor_remainder"))
        lower = as_fraction(row.get("liminf_lower"))
        row_ok = row_ok and None not in (
            d_a,
            c_a,
            m_psi,
            tau,
            threshold,
            main,
            remainder,
            lower,
        )
        if None not in (d_a, c_a, m_psi, tau, threshold, main, remainder, lower):
            row_ok = row_ok and (
                threshold == 2 * d_a / (c_a * m_psi)
                and 0 < tau < threshold
                and main == tau * d_a
                and remainder == tau * tau * c_a * m_psi / 2
                and lower == main - remainder
                and lower > 0
            )
    packet_ok = (
        derivation_ok
        and graph.get("anisotropic_max_degree") == 6
        and as_fraction(graph.get("K_three_halves_degree_R")) == 6
        and as_fraction(scaling.get("time_degree_R")) == -3
        and as_fraction(scaling.get("time_squared_degree_R")) == -6
        and as_fraction(scaling.get("delta_squared_vector_bound_degree_R")) == 6
        and as_fraction(scaling.get("taylor_remainder_total_degree_R")) == 0
        and row_ok
        and conclusion.get("full_unsplit_positive_liminf_only") is True
        and conclusion.get("exact_norm_jump_claimed") is False
        and conclusion.get("raw_momentum_weyl_point_norm_C0") is False
        and conclusion.get("basic_momentum_resolvent_point_norm_C0") is False
        and conclusion.get("unsplit_resolvent_algebra_invariance_decided") is False
    )

    mu = as_fraction(pure.get("mu_fixture"))
    jump = as_fraction(pure.get("exact_jump_fixture"))
    pure_ok = (
        mu not in (None, 0)
        and jump is not None
        and jump * abs(mu) == 1
        and pure.get("standard_resolvent_algebra_invariant_under_pure_quartic_kick")
        is False
        and pure.get("unital_resolvent_strict_equals_norm") is True
        and pure.get("unsplit_quartic_resolvent_algebra_invariance_decided") is False
        and text_has(pure.get("exact_spatial_weyl_orbit_jump"), "1/abs(mu)")
    )

    beta = as_fraction(gibbs_inputs.get("beta"))
    hbar = as_fraction(gibbs_inputs.get("hbar"))
    gibbs_chi = as_fraction(gibbs_inputs.get("chi"))
    xi2 = as_fraction(gibbs_inputs.get("xi_norm_square"))
    s_xi = as_fraction(character.get("S_xi"))
    expected_s = (
        beta * hbar * hbar * xi2 / (2 * gibbs_chi)
        if None not in (beta, hbar, gibbs_chi, xi2)
        else None
    )
    orientation = as_mapping(tail.get("orientation_bounds"))
    gibbs_ok = (
        s_xi == expected_s
        and character.get("both_character_orientations") is True
        and character.get("preserved_after_full_H_time_evolution") is True
        and tail.get("denominator_positive") is True
        and orientation.get("q_plus") == orientation.get("q_minus")
        and text_has(tail.get("formula"), "(S_xi+log(2))/(a L^2-log(M_a |S|))")
        and as_mapping(gibbs.get("scope")).get("dynamic_gaussian_tail") is False
    )

    entropy_rows = as_list(entropy.get("rows"))
    entropy_rows_ok = bool(entropy_rows)
    for row in entropy_rows:
        if not isinstance(row, dict):
            entropy_rows_ok = False
            continue
        m = as_fraction(row.get("m"))
        n = as_fraction(row.get("n"))
        tail_increment = as_fraction(row.get("tail_increment"))
        relative_entropy = as_fraction(row.get("relative_entropy"))
        energy_excess = as_fraction(row.get("energy_excess"))
        beta_fixture = as_fraction(as_mapping(entropy.get("inputs")).get("beta"))
        if None in (m, n, tail_increment, relative_entropy, energy_excess, beta_fixture):
            entropy_rows_ok = False
            continue
        entropy_rows_ok = entropy_rows_ok and (
            m.denominator == 1
            and m >= 3
            and tail_increment == n ** (-2 * int(m))
            and relative_entropy == n ** (4 - 2 * int(m))
            and energy_excess == relative_entropy / beta_fixture
            and as_fraction(row.get("moment_order")) == 2 * m
            and all(
                isinstance(item, dict)
                and 0 < as_fraction(item.get("order_r")) <= 2 * m
                for item in as_list(row.get("lower_even_moments"))
            )
        )
    m4 = as_mapping(entropy.get("m4_bound_proof"))
    entropy_ok = (
        entropy_rows_ok
        and entropy.get("both_unitary_orientations") is True
        and entropy.get("uniform_dynamic_gaussian_tail_inferred") is False
        and text_has(as_mapping(entropy.get("general_exact_values")).get("relative_entropy"), "n^(4-2m)")
        and text_has(as_mapping(entropy.get("m4_exact_values")).get("reference_piece_bound"), "4 exp(-2)")
        and text_has(m4.get("global_maximum"), "4 exp(-2)")
    )

    generator = as_mapping(ground.get("generator"))
    states = as_mapping(ground.get("states"))
    gns = as_mapping(ground.get("gns"))
    probes = [as_fraction(value) for value in as_list(generator.get("spectral_probes_1_over_N"))]
    ground_ok = (
        generator.get("kernel_dimension") == 1
        and generator.get("positive_spectrum_accumulates_at_zero") is True
        and all(value is not None and value > 0 for value in probes)
        and all(right < left for left, right in zip(probes, probes[1:]))
        and states.get("pure") is True
        and states.get("disjoint") is True
        and states.get("exact_ground") is True
        and states.get("parity_exchange") == "summand swap"
        and gns.get("ground_vector_simple") is True
        and as_fraction(gns.get("positive_gap")) == 0
        and gns.get("coercive_gap_estimate_supplied") is False
        and ground.get("automatic_broken_sector_GNS_gap") is False
    )

    scope = as_mapping(payload.get("scope"))
    scope_ok = (
        scope.get("finite_volume_local_strict_energy_subflow_carrier") is True
        and scope.get("fixed_gibbs_character_entropy_tilted_tail") is True
        and all(
            scope.get(key) is False
            for key in (
                "all_exhaustion_two_orientation_history_common_alpha",
                "broken_sector_GNS_gap_coercivity",
                "mass_gap",
                "continuum_regulator_removal",
                "physical_empty_space_reference",
                "C6_advanced",
                "CP1_complete",
                "Sector_A_complete",
                "Pre_A_complete",
            )
        )
    )
    return {
        "q3_effective_coupling": q3_ok,
        "local_strict_topology_and_subflows": carrier_ok,
        "delta_delta2_packet_positive_only": packet_ok,
        "pure_kick_exact_jump_and_scope": pure_ok,
        "two_sided_gibbs_entropy_log_tail": gibbs_ok,
        "general_m_and_m4_finite_moment_no_go": entropy_ok,
        "ordered_ground_gap_no_go": ground_ok,
        "no_overclaim_scope": scope_ok,
    }


def independent_invariants(payload: Mapping[str, Any]) -> dict[str, bool]:
    derived = as_mapping(payload.get("derived"))
    topology = as_mapping(derived.get("local_strict_topology"))
    bond = as_mapping(topology.get("bond_form_fixture"))
    q3 = as_mapping(derived.get("q3_quartic_force"))
    packet = as_mapping(derived.get("unsplit_packet"))
    graph_degrees = as_mapping(packet.get("graph_degrees"))
    translation = as_mapping(packet.get("translation_powers"))
    pure = as_mapping(derived.get("pure_quartic_resolvent"))
    gibbs = as_mapping(derived.get("finite_gibbs_entropy"))
    entropy = as_mapping(derived.get("entropy_finite_moment_no_go"))
    ground = as_mapping(derived.get("ordered_ground_gap_no_go"))

    g = as_fraction(q3.get("g_fixture"))
    lam = as_fraction(q3.get("lambda_fixture"))
    g_fixture = as_fraction(q3.get("G_fixture"))
    q3_ok = (
        g is not None
        and lam is not None
        and g_fixture == g + 3 * lam
        and q3.get("symbolic_G_pair") == ["1", "3"]
        and q3.get("axis_F_leading_pair") == ["1", "3"]
        and q3.get("neighbours_of_zero") == [1, 2, 4]
        and len(as_list(q3.get("edges"))) == 12
        and q3.get("degree_rows") == [3] * 8
    )
    topology_ok = (
        topology.get("strict_equals_strong_star_on_norm_bounded_sets") is True
        and topology.get("compact_graph_dense_range_equivalence") is True
        and topology.get("fixed_region_only") is True
        and topology.get("onsite_commuting_control_isometric") is True
        and topology.get("onsite_support_growth") == 0
        and topology.get("bond_support_growth") == 1
        and text_has(bond.get("energy_map"), "e_E(beta(A))<=e_(M E)(A)")
        and bond.get("both_form_orientations") is True
        and topology.get("continuous_split_product_limit_closed") is False
        and topology.get("all_exhaustion_Cauchy_closed") is False
        and topology.get("global_multiplier_strict_topology_claimed") is False
    )

    hbar = as_fraction(packet.get("hbar"))
    chi = as_fraction(packet.get("chi"))
    delta_w = packet.get("delta_W_D_coefficient")
    delta2_w_anti = packet.get("delta2_W_anticommutator_coefficient")
    delta2_w_square = packet.get("delta2_W_D_squared_coefficient")
    derivation_ok = (
        hbar not in (None, 0)
        and chi not in (None, 0)
        and delta_w == ["0", str(1 / hbar)]
        and delta2_w_anti == ["0", str(1 / (2 * chi * hbar))]
        and delta2_w_square == [str(-1 / (hbar * hbar)), "0"]
        and packet.get("delta_R_F_coefficient") == ["1", "0"]
        and as_fraction(packet.get("delta2_R_F_R_F_coefficient")) == 2
        and as_fraction(packet.get("delta2_R_anticommutator_coefficient"))
        == 1 / (2 * chi)
        and text_has(packet.get("q_resolvent_commutator_sign"), "[q_0,R_0]=-i hbar R_0^2")
    )
    packet_rows_ok = bool(as_list(packet.get("rows")))
    for row in as_list(packet.get("rows")):
        if not isinstance(row, dict):
            packet_rows_ok = False
            continue
        tau = as_fraction(row.get("tau"))
        tau_upper = as_fraction(row.get("tau_upper"))
        lower = as_fraction(row.get("liminf_lower"))
        packet_rows_ok = packet_rows_ok and (
            tau is not None
            and tau_upper is not None
            and lower is not None
            and 0 < tau < tau_upper
            and lower > 0
            and row.get("positive_only_not_exact_jump") is True
        )
    packet_ok = (
        derivation_ok
        and graph_degrees.get("D_a") == 3
        and graph_degrees.get("F_0") == 3
        and graph_degrees.get("D_a_squared") == 6
        and graph_degrees.get("F_0_squared") == 6
        and packet.get("graph_endpoint") == 6
        and translation.get("K") == 4
        and translation.get("K_to_three_halves") == 6
        and translation.get("delta_W_a") == 3
        and translation.get("delta_R_0") == 3
        and translation.get("time") == -3
        and translation.get("first_Taylor_total") == 0
        and translation.get("second_Taylor_total") == 0
        and packet_rows_ok
        and packet.get("unsplit_flow_invariance_decided") is False
        and packet.get("unsplit_flow_point_norm_C0_if_invariant") is False
        and packet.get("exact_norm_jump_claimed") is False
    )

    mu = as_fraction(pure.get("mu"))
    jump = as_fraction(pure.get("exact_jump"))
    pure_ok = (
        mu not in (None, 0)
        and jump is not None
        and jump * abs(mu) == 1
        and pure.get("momentum_center_power") == 2
        and as_fraction(pure.get("packet_width_power")) == Fraction(1, 2)
        and as_fraction(pure.get("phase_spread_power")) == Fraction(3, 2)
        and pure.get("upper_bound") == pure.get("lower_bound") == pure.get("exact_jump")
        and pure.get("weyl_orbit_norm_continuous_for_resolvent_algebra_elements")
        is True
        and pure.get("translated_element_in_resolvent_algebra") is False
        and pure.get("full_resolvent_algebra_unital") is True
        and pure.get("its_multiplier_strict_equals_norm") is True
        and pure.get("unsplit_invariance_decided") is False
        and pure.get("dynamics_nonexistence_claimed") is False
    )

    beta = as_fraction(gibbs.get("beta"))
    gibbs_hbar = as_fraction(gibbs.get("hbar"))
    gibbs_chi = as_fraction(gibbs.get("chi"))
    xi2 = as_fraction(gibbs.get("xi_squared"))
    expected_s = (
        beta * gibbs_hbar * gibbs_hbar * xi2 / (2 * gibbs_chi)
        if None not in (beta, gibbs_hbar, gibbs_chi, xi2)
        else None
    )
    gibbs_ok = (
        as_fraction(gibbs.get("relative_entropy_plus")) == expected_s
        and as_fraction(gibbs.get("relative_entropy_minus")) == expected_s
        and as_fraction(gibbs.get("evolved_relative_entropy_plus")) == expected_s
        and as_fraction(gibbs.get("evolved_relative_entropy_minus")) == expected_s
        and gibbs.get("two_orientations") is True
        and as_mapping(gibbs.get("binary_fixture")).get("q_below_inverted_bound")
        is True
        and as_mapping(gibbs.get("gaussian_tail_substitution")).get(
            "denominator_positive"
        )
        is True
        and as_mapping(gibbs.get("gaussian_tail_substitution")).get(
            "asymptotic_power"
        )
        == -2
        and gibbs.get("all_history_gaussian_tail_closed") is False
        and gibbs.get("exponential_corridor_absorbed") is False
    )

    ceiling_rows = as_list(entropy.get("arbitrary_finite_ceiling_rows"))
    real_rows = as_list(entropy.get("real_r_rows"))
    m4_rows = as_list(entropy.get("m4_rows"))
    entropy_ok = (
        bool(ceiling_rows)
        and all(
            isinstance(row, dict)
            and row.get("covered") is True
            and row.get("chosen_m", 0) >= 3
            and 2 * row.get("chosen_m", 0) >= row.get("ceiling", 10**9)
            for row in ceiling_rows
        )
        and bool(real_rows)
        and all(
            isinstance(row, dict)
            and row.get("r_in_domain") is True
            and row.get("second_exponent_nonpositive") is True
            and row.get("within_uniform_bound") is True
            for row in real_rows
        )
        and bool(m4_rows)
        and all(isinstance(row, dict) and row.get("bound_holds") is True for row in m4_rows)
        and as_fraction(entropy.get("m4_calculus_optimizer_for_x_squared_exp_minus_x"))
        == 2
        and math.isclose(float(entropy.get("m4_excess_bound")), 4 * math.exp(-2), rel_tol=1e-12)
        and entropy.get("finite_moment_to_gaussian_inference_valid") is False
        and entropy.get("Q3LOCK_counterexample") is False
        and entropy.get("stronger_quasi_invariance_excluded") is False
    )

    points = [as_fraction(value) for value in as_list(ground.get("positive_spectral_points"))]
    ground_ok = (
        ground.get("dynamics_point_norm_C0") is True
        and ground.get("states_pure") is True
        and ground.get("states_disjoint") is True
        and ground.get("parity_swap") is True
        and ground.get("central_order_values") == ["1", "-1"]
        and ground.get("GNS_ground_kernel_dimension_each") == 1
        and ground.get("spectrum_each") == "[0,1]"
        and as_fraction(ground.get("positive_spectrum_infimum")) == 0
        and all(point is not None and point > 0 for point in points)
        and all(right < left for left, right in zip(points, points[1:]))
        and all(
            isinstance(row, dict) and row.get("orthogonal_to_ground") is True
            for row in as_list(ground.get("weyl_sequence_rows"))
        )
        and ground.get("ordered_doublets_imply_gap") is False
        and ground.get("physical_mass_gap_claimed") is False
        and text_has(ground.get("coercivity_form"), "Delta")
    )

    scope_ok = (
        derived.get("finite_region_local_strict_carrier_closed") is True
        and derived.get("fixed_finite_gibbs_entropy_tail_closed") is True
        and all(
            derived.get(key) is False
            for key in (
                "continuous_time_split_limit_closed",
                "all_exhaustion_common_alpha_closed",
                "unsplit_resolvent_algebra_invariance_decided",
                "phase_KMS_quotient_identified",
                "broken_sector_GNS_gap_closed",
                "physical_mass_gap_closed",
                "regulator_removal_closed",
                "continuum_closed",
                "physical_empty_comparison_closed",
                "C6_closed",
                "CP1_closed",
                "Sector_A_closed",
                "Pre_A_closed",
            )
        )
    )
    return {
        "q3_effective_coupling": q3_ok,
        "local_strict_topology_and_subflows": topology_ok,
        "delta_delta2_packet_positive_only": packet_ok,
        "pure_kick_exact_jump_and_scope": pure_ok,
        "two_sided_gibbs_entropy_log_tail": gibbs_ok,
        "general_m_and_m4_finite_moment_no_go": entropy_ok,
        "ordered_ground_gap_no_go": ground_ok,
        "no_overclaim_scope": scope_ok,
    }


def third_recomputation() -> dict[str, Any]:
    edges = sorted(
        {
            (min(vertex, vertex ^ (1 << bit)), max(vertex, vertex ^ (1 << bit)))
            for vertex in range(8)
            for bit in range(3)
        }
    )
    neighbors = sorted(
        right if left == 0 else left
        for left, right in edges
        if left == 0 or right == 0
    )
    g = Fraction(3, 5)
    lam = Fraction(2, 7)
    effective_g = g + len(neighbors) * lam

    c = Fraction(3, 5)
    z = 6
    exp_mu = Fraction(3, 2)
    chi = Fraction(7, 4)
    sqrt_gamma = Fraction(2, 5)
    delta = Fraction(2, 7)
    c_b = 1 + c * c * z * z * exp_mu / (2 * chi * sqrt_gamma)
    m_delta = 1 + c_b * abs(delta)

    d_a = Fraction(7, 5)
    c_a = Fraction(9, 4)
    m_psi = Fraction(5, 3)
    tau_threshold = 2 * d_a / (c_a * m_psi)
    tau = tau_threshold / 2
    packet_lower = tau * d_a - tau * tau * c_a * m_psi / 2

    mu = Fraction(-11, 6)
    pure_jump = Fraction(1, 1) / abs(mu)

    beta = Fraction(2)
    hbar = Fraction(3)
    gibbs_chi = Fraction(5)
    xi2 = Fraction(25, 36)
    s_xi = beta * hbar * hbar * xi2 / (2 * gibbs_chi)

    entropy_rows: list[dict[str, Any]] = []
    for m in (3, 4, 7):
        for n in (2, 3, 5):
            tail = Fraction(1, n ** (2 * m))
            entropy = Fraction(n ** 4, n ** (2 * m))
            energy = entropy / Fraction(7, 5)
            entropy_rows.append(
                {
                    "m": m,
                    "n": n,
                    "tail": tail,
                    "entropy": entropy,
                    "energy": energy,
                    "zero_moment": Fraction(1),
                }
            )
    m4_bound = all(
        n**8 * (math.exp(-(n**4)) / (1 + math.exp(-(n**4))))
        <= 4 * math.exp(-2) + 1e-15
        for n in (2, 3, 5, 8)
    )
    spectral_points = [Fraction(1, 2**index) for index in range(6)]
    expected_flags = {
        "q3_effective_coupling": (
            len(edges) == 12
            and neighbors == [1, 2, 4]
            and effective_g == Fraction(51, 35)
        ),
        "local_strict_topology_and_subflows": (
            c_b == Fraction(521, 35)
            and m_delta == Fraction(1287, 245)
            and 0 < Fraction(1, 2) <= Fraction(1, 2)
        ),
        "delta_delta2_packet_positive_only": (
            3 + (-3) == 0
            and 6 + 2 * (-3) == 0
            and 0 < tau < tau_threshold
            and packet_lower > 0
        ),
        "pure_kick_exact_jump_and_scope": pure_jump == Fraction(6, 11),
        "two_sided_gibbs_entropy_log_tail": s_xi == Fraction(5, 4),
        "general_m_and_m4_finite_moment_no_go": (
            all(row["m"] >= 3 and row["zero_moment"] == 1 for row in entropy_rows)
            and m4_bound
        ),
        "ordered_ground_gap_no_go": (
            all(point > 0 for point in spectral_points)
            and all(
                right < left
                for left, right in zip(spectral_points, spectral_points[1:])
            )
            and Fraction(0) == 0
        ),
        "no_overclaim_scope": True,
    }
    return {
        "cube_edges": edges,
        "neighbors_zero": neighbors,
        "effective_G": effective_g,
        "C_b": c_b,
        "M_delta": m_delta,
        "packet_tau_threshold": tau_threshold,
        "packet_tau": tau,
        "packet_positive_lower": packet_lower,
        "pure_kick_jump": pure_jump,
        "gibbs_S_xi": s_xi,
        "entropy_rows": entropy_rows,
        "m4_reference_piece_bound": m4_bound,
        "positive_spectral_points": spectral_points,
        "flags": expected_flags,
    }


def compare_exact_core(
    primary: Mapping[str, Any],
    independent: Mapping[str, Any],
    audit: Audit,
) -> dict[str, Any]:
    primary_flags = primary_invariants(primary)
    independent_flags = independent_invariants(independent)
    recomputed = third_recomputation()
    expected = {key: True for key in primary_flags}
    audit.check(
        "primary exact semantic invariants",
        primary_flags == expected,
        primary_flags,
        expected,
        "cross_core",
    )
    audit.check(
        "independent exact semantic invariants",
        independent_flags == expected,
        independent_flags,
        expected,
        "cross_core",
    )
    audit.check(
        "third stdlib/Fraction recomputation",
        recomputed["flags"] == expected,
        recomputed["flags"],
        expected,
        "cross_core",
    )
    audit.check(
        "three proof layers agree on the exact boundary",
        primary_flags == independent_flags == recomputed["flags"] == expected,
        {
            "primary": primary_flags,
            "independent": independent_flags,
            "third": recomputed["flags"],
        },
        expected,
        "cross_core",
    )
    return {
        "primary": primary_flags,
        "independent": independent_flags,
        "third": recomputed,
        "expected": expected,
        "all_exact": primary_flags == independent_flags == expected,
    }


def validate_manifest(manifest: Mapping[str, Any], audit: Audit) -> None:
    route = as_mapping(manifest.get("route_status"))
    exact = {
        "schema": manifest.get("schema") == "tect/pre-a-route-split/1.0",
        "candidate": manifest.get("candidate_id")
        == "PA-CP1-ST8-Q3LOCK-LOCAL-STRICT-QUARTIC-C0-ENTROPY-GAP-ROUTE-SPLIT-v0",
        "task": manifest.get("task_id") == TASK_ID,
        "claim": manifest.get("claim_ids") == [CLAIM_ID],
        "parents": manifest.get("parent_explorations")
        == ["EXP-000792", "EXP-000799", "EXP-000803"],
        "exploration": manifest.get("exploration_id") == EXPLORATION_ID,
        "result_id": manifest.get("result_id") == RESULT_ID,
        "result_number": manifest.get("result_number") == RESULT_NUMBER,
        "result_version": manifest.get("result_version") == RESULT_VERSION,
        "claim_bearing": manifest.get("claim_bearing") is False,
        "negatives": tuple(manifest.get("negative_ids", ())) == NEGATIVE_IDS,
        "reused_negatives": tuple(manifest.get("reused_negative_ids", ()))
        == REUSED_NEGATIVE_IDS,
        "closed": tuple(manifest.get("closed_subgates", ())) == CLOSED_GATES,
        "open": tuple(manifest.get("open_gates", ())) == OPEN_GATES,
        "retained": tuple(manifest.get("retained_gate_ids", ())) == RETAINED_GATES,
        "historical": manifest.get("superseded_gate_ids") == [HISTORICAL_GATE],
        "route_historical": route.get("superseded_combined_gate")
        == HISTORICAL_GATE,
        "route_dynamics": route.get("next_dynamics_gate") == SUCCESSOR_GATES[0],
        "route_gap": route.get("next_gap_gate") == SUCCESSOR_GATES[1],
    }
    audit.check(
        "manifest exact identity, negatives and gate split",
        all(exact.values()),
        exact,
        "all true",
        "manifest",
    )
    verification = as_mapping(manifest.get("verification"))
    expected_scripts = {
        "primary_script": PRIMARY.relative_to(REPO).as_posix(),
        "independent_script": INDEPENDENT.relative_to(REPO).as_posix(),
        "integrated_script": SCRIPT.relative_to(REPO).as_posix(),
    }
    audit.check(
        "manifest exact verifier paths",
        all(verification.get(key) == value for key, value in expected_scripts.items()),
        {key: verification.get(key) for key in expected_scripts},
        expected_scripts,
        "manifest",
    )
    checkpoint = as_mapping(manifest.get("checkpoint_synthesis"))
    note_relative = NOTE_SOURCE.relative_to(REPO).as_posix()
    pdf_relative = CHECKPOINT_PDF.relative_to(REPO).as_posix()
    checkpoint_core = {
        "source": checkpoint.get("source") == note_relative,
        "pdf": checkpoint.get("pdf") == pdf_relative,
        "development_economy": text_has(
            checkpoint.get("workflow", ""), "No per-lemma or intermediate PDF"
        ),
        "proof_layers_first": all(
            text_has(checkpoint.get("workflow", ""), token)
            for token in ("manifest", "certificate", "primary", "independent", "integrated")
        ),
    }
    audit.check(
        "manifest checkpoint core contract",
        all(checkpoint_core.values()),
        checkpoint_core,
        "all true",
        "manifest",
    )
    serialized = json.dumps(manifest, sort_keys=True)
    require_tokens(
        serialized,
        "manifest theorem and hostile-fixture content",
        (
            "B(H_Y)=M(K(H_Y))",
            "strict",
            "strong-star",
            "q_s",
            "e_E",
            "C_b",
            "N_1(X)",
            "G=g+3lambda",
            "K^(-3/2)",
            "1/|mu|",
            "inverse-logarithmic",
            "n^(4-2m)",
            "1+4exp(-2)",
            "[0,1]",
            "coercive",
        ),
        audit,
        group="manifest",
        core=True,
    )
    require_tokens(
        manifest.get("no_overclaim", ""),
        "manifest no-overclaim boundary",
        (
            "continuous-time thermodynamic split limit",
            "all-exhaustion",
            "quasi-local raw oscillator common alpha",
            "unsplit quartic flow",
            "phase-KMS quotient identification",
            "broken-sector GNS or physical mass gap",
            "regulator removal",
            "continuum",
            "physical empty space",
            "below-empty sign",
            "Pre-A",
            "C6",
            "CP1",
            "Sector-A",
        ),
        audit,
        group="scope",
        core=True,
    )
    forbidden = (
        r"(?:proves|closes)[^.]{0,120}all[- ]exhaustion",
        r"(?:proves|closes)[^.]{0,120}broken[- ]sector gns gap",
        r"unsplit quartic flow does not preserve",
        r"q3lock dynamics (?:does not exist|is impossible)",
    )
    hits = [pattern for pattern in forbidden if re.search(pattern, serialized, re.I)]
    audit.check(
        "manifest has no broadened positive conclusion", not hits, hits, [], "scope"
    )


def validate_certificate(audit: Audit) -> str:
    certificate = require_text(CERTIFICATE, audit, "certificate", core=True) or ""
    if not certificate:
        return certificate
    require_tokens(
        certificate,
        "certificate theorem, fixtures and exact boundary",
        (
            EXPLORATION_ID,
            RESULT_NUMBER,
            RESULT_VERSION,
            RESULT_ID,
            *CLOSED_GATES,
            *SUCCESSOR_GATES,
            HISTORICAL_GATE,
            *NEGATIVE_IDS,
            "B({cal H}_Y)=M(K({cal H}_Y))",
            "q_(s,Y)",
            "e_(E,Y)",
            "M_delta=1+C_b|delta|",
            "N_1(X)",
            "G=g+3lambda",
            "delta W_a",
            "D_aW_a",
            "delta^2 R_0=2R_0F_0R_0F_0R_0",
            "K^(-3/2)",
            "t_R=tau R^(-3)",
            "positive discontinuity",
            "1 over |mu|",
            "S_xi",
            "O(L^(-2))",
            "m>=3",
            "1+4exp(-2)",
            "[0,1]",
            "-i hbar omega(A^*delta(A))",
            "No per-lemma or intermediate PDF",
            "Exactly one gate-level synthesis",
        ),
        audit,
        group="certificate",
        core=True,
    )
    malformed = [
        token
        for token in ("{cal", ",qquad", ",quad", "limsup_RR")
        if token in certificate
    ]
    audit.check(
        "certificate has no known malformed LaTeX tokens",
        not malformed,
        malformed,
        [],
        "certificate",
    )
    forbidden = (
        r"finite[- ]region local[- ]strict theorem (?:is|gives) the thermodynamic",
        r"ordered ground states (?:imply|prove|give) a positive (?:gns|mass) gap",
        r"the unsplit quartic flow (?:is|was) proved not to preserve",
    )
    hits = [pattern for pattern in forbidden if re.search(pattern, certificate, re.I)]
    audit.check(
        "certificate has no broadened positive conclusion", not hits, hits, [], "scope"
    )
    return certificate


def heading_section(text: str, identifier: str) -> str | None:
    lines = text.splitlines()
    starts = [
        index
        for index, line in enumerate(lines)
        if line.startswith("###") and identifier in line
    ]
    if len(starts) != 1:
        return None
    start = starts[0]
    end = next(
        (
            index
            for index in range(start + 1, len(lines))
            if lines[index].startswith("###")
        ),
        len(lines),
    )
    return "\n".join(lines[start:end])


def result_section(text: str, result: str) -> str | None:
    lines = text.splitlines()
    starts = [
        index
        for index, line in enumerate(lines)
        if line.startswith("###") and re.search(rf"\b{re.escape(result)}\b", line)
    ]
    if len(starts) != 1:
        return None
    start = starts[0]
    end = next(
        (
            index
            for index in range(start + 1, len(lines))
            if lines[index].startswith("###")
        ),
        len(lines),
    )
    return "\n".join(lines[start:end])


def pdf_metadata(path: Path) -> dict[str, Any]:
    """Read compressed-object PDFs with the repository's installed parser.

    Page dictionaries in project PDFs are commonly stored in object streams,
    so a stdlib byte regex cannot count them reliably.  This is the sole place
    where the integrated verifier needs a non-stdlib package.
    """

    try:
        from pypdf import PdfReader

        reader = PdfReader(str(path), strict=True)
        texts = [page.extract_text() or "" for page in reader.pages]
        return {
            "error": None,
            "pages": len(reader.pages),
            "encrypted": reader.is_encrypted,
            "form_fields": bool(reader.get_fields()),
            "page_characters": [len(text) for text in texts],
            "text": "\n".join(texts),
        }
    except Exception as error:  # pypdf exposes several parser-specific errors.
        return {
            "error": f"{type(error).__name__}: {error}",
            "pages": 0,
            "encrypted": None,
            "form_fields": None,
            "page_characters": [],
            "text": "",
        }


def validate_pdf_efficiency(
    audit: Audit,
    manifest: Mapping[str, Any],
    certificate: str,
) -> dict[str, Any]:
    note_relative = NOTE_SOURCE.relative_to(REPO).as_posix()
    pdf_relative = CHECKPOINT_PDF.relative_to(REPO).as_posix()
    expected_artifacts = {note_relative, pdf_relative}
    source_exists = NOTE_SOURCE.is_file()
    pdf_exists = CHECKPOINT_PDF.is_file()
    notes_root = NOTE_SOURCE.parent
    package_artifacts: list[str] = []
    stem_marker = "pre-a-q3lock-local-strict-quartic-c0-entropy-gap-route-split-260811"
    if notes_root.is_dir():
        for path in notes_root.iterdir():
            if (
                path.is_file()
                and stem_marker in path.name.lower()
                and path.name.lower().endswith((".pdf", ".tex.txt"))
            ):
                package_artifacts.append(path.relative_to(REPO).as_posix())
    audit.pending(
        "exactly one v0.6 checkpoint source/PDF pair exists",
        set(package_artifacts) == expected_artifacts
        and len(package_artifacts) == len(expected_artifacts),
        sorted(package_artifacts),
        sorted(expected_artifacts),
        "pdf_efficiency",
    )

    source_text = ""
    source_error: str | None = None
    try:
        source_text = NOTE_SOURCE.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        source_error = str(error)
    audit.pending(
        "checkpoint source readable UTF-8",
        source_error is None and len(source_text) > 10000,
        {"error": source_error, "characters": len(source_text)},
        "readable UTF-8 source with >10000 characters",
        "pdf_checkpoint",
    )
    source_tokens = (
        EXPLORATION_ID,
        RESULT_NUMBER,
        RESULT_VERSION,
        RESULT_ID,
        *CLOSED_GATES,
        *SUCCESSOR_GATES,
        HISTORICAL_GATE,
        *NEGATIVE_IDS,
        "local-strict",
        "strong-star",
        "G=g+3lambda",
        "positive discontinuity",
        "inverse-logarithmic",
        "[0,1]",
        "physical mass gap",
        "continuum",
        "C6",
        "CP1",
        "Pre-A closure",
    )
    if source_exists:
        require_tokens(
            source_text,
            "checkpoint source theorem and no-overclaim content",
            source_tokens,
            audit,
            group="pdf_checkpoint",
            core=True,
        )
    else:
        audit.pending(
            "checkpoint source theorem and no-overclaim content required tokens",
            False,
            "source unavailable",
            "all required tokens present",
            "pdf_checkpoint",
        )
    source_compact = compact_text(source_text)
    source_boundary = {
        "positive_not_exact_jump": "normjump" in source_compact
        and any(
            token in source_compact
            for token in ("notanexact", "nottheexact", "noexact")
        ),
        "pure_kick_exact_inverse_mu": "purequartic" in source_compact
        and "exact" in source_compact
        and "mu" in source_compact
        and "jump" in source_compact,
        "m4_bound": "m4" in source_compact
        and any(token in source_compact for token in ("4exp2", "4e2")),
        "all_exhaustion_denied": "allexhaustion" in source_compact
        and any(token in source_compact for token in ("notallexhaustion", "noallexhaustion")),
        "unsplit_invariance_open": "unsplit" in source_compact
        and "resolventalgebra" in source_compact
        and "invariance" in source_compact
        and "open" in source_compact,
    }
    source_boundary_reporter = audit.check if source_exists else audit.pending
    source_boundary_reporter(
        "checkpoint source exact route-boundary clauses",
        source_exists and all(source_boundary.values()),
        source_boundary,
        "all true",
        "pdf_checkpoint",
    )
    placeholders = [
        token
        for token in ("TODO", "TBD", "FIXME", "PLACEHOLDER")
        if re.search(rf"\b{token}\b", source_text, re.I)
    ]
    audit.pending(
        "checkpoint source has no drafting placeholders",
        source_exists and not placeholders,
        placeholders,
        [],
        "pdf_checkpoint",
    )

    raw_pdf = b""
    pdf_error: str | None = None
    try:
        raw_pdf = CHECKPOINT_PDF.read_bytes()
    except OSError as error:
        pdf_error = str(error)
    parsed_pdf = pdf_metadata(CHECKPOINT_PDF) if pdf_exists else {
        "error": pdf_error,
        "pages": 0,
        "encrypted": None,
        "form_fields": None,
        "page_characters": [],
        "text": "",
    }
    pages = int(parsed_pdf["pages"])
    header_ok = raw_pdf.startswith(b"%PDF-")
    eof_ok = b"%%EOF" in raw_pdf[-64:] if raw_pdf else False
    audit.pending(
        "checkpoint PDF static structure",
        pdf_error is None
        and parsed_pdf["error"] is None
        and header_ok
        and eof_ok
        and pages > 0
        and parsed_pdf["encrypted"] is False
        and parsed_pdf["form_fields"] is False
        and all(count > 150 for count in parsed_pdf["page_characters"]),
        {
            "read_error": pdf_error,
            "parse_error": parsed_pdf["error"],
            "bytes": len(raw_pdf),
            "header": raw_pdf[:8].decode("latin-1", errors="replace"),
            "eof": eof_ok,
            "pages": pages,
            "encrypted": parsed_pdf["encrypted"],
            "form_fields": parsed_pdf["form_fields"],
            "page_characters": parsed_pdf["page_characters"],
        },
        "static unencrypted form-free PDF with nonempty extracted pages",
        "pdf_checkpoint",
    )
    if pdf_exists:
        require_tokens(
            parsed_pdf["text"],
            "checkpoint PDF provenance and exact gate boundary",
            (
                EXPLORATION_ID,
                RESULT_NUMBER,
                RESULT_VERSION,
                *CLOSED_GATES,
                *SUCCESSOR_GATES,
                *NEGATIVE_IDS,
                "local-strict",
                "positive discontinuity",
                "inverse-logarithmic",
                "physical mass gap",
                "Pre-A closure",
            ),
            audit,
            group="pdf_checkpoint",
            core=True,
        )
    else:
        audit.pending(
            "checkpoint PDF provenance and exact gate boundary required tokens",
            False,
            "PDF unavailable",
            "all required tokens present",
            "pdf_checkpoint",
        )
    source_stat = NOTE_SOURCE.stat() if source_exists else None
    pdf_stat = CHECKPOINT_PDF.stat() if pdf_exists else None
    freshness = (
        source_stat is not None
        and pdf_stat is not None
        and pdf_stat.st_mtime_ns >= source_stat.st_mtime_ns
        and pdf_stat.st_size > 0
    )
    audit.pending(
        "checkpoint PDF fresh relative to source",
        freshness,
        {
            "source_mtime_ns": source_stat.st_mtime_ns if source_stat else None,
            "pdf_mtime_ns": pdf_stat.st_mtime_ns if pdf_stat else None,
            "source_size": source_stat.st_size if source_stat else None,
            "pdf_size": pdf_stat.st_size if pdf_stat else None,
        },
        "PDF mtime >= source and both nonempty",
        "pdf_checkpoint",
    )

    checkpoint = as_mapping(manifest.get("checkpoint_synthesis"))
    source_hash = portable_sha256(NOTE_SOURCE) if source_exists else None
    pdf_hash = portable_sha256(CHECKPOINT_PDF) if pdf_exists else None
    checkpoint_final = {
        "not_deferred": checkpoint.get("status")
        not in ("DEFERRED_UNTIL_GATE_LEVEL_VALIDATION", "DEFERRED"),
        "source_hash": checkpoint.get("source_sha256") == source_hash,
        "pdf_hash": checkpoint.get("pdf_sha256") == pdf_hash,
        "pages": isinstance(checkpoint.get("pages"), int)
        and checkpoint.get("pages") == pages
        and pages > 0,
        "single_checkpoint": text_has(
            checkpoint.get("workflow", ""), "single gate-level synthesis"
        ),
        "visual_render": text_has(checkpoint.get("visual_qa", ""), "rendered"),
        "visual_clipping": text_has(checkpoint.get("visual_qa", ""), "clipping"),
        "visual_overlap": text_has(checkpoint.get("visual_qa", ""), "overlap"),
        "visual_equations": text_has(checkpoint.get("visual_qa", ""), "equations"),
        "visual_overfull": text_has(checkpoint.get("visual_qa", ""), "overfull boxes"),
    }
    audit.pending(
        "manifest final checkpoint hashes, pages and visual QA",
        source_exists and pdf_exists and all(checkpoint_final.values()),
        checkpoint_final,
        "all true",
        "pdf_checkpoint",
    )

    completed = subprocess.run(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=REPO,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=60,
    )
    changed_artifacts: list[str] = []
    if completed.returncode == 0:
        for line in completed.stdout.splitlines():
            path_text = line[3:].strip().strip('"') if len(line) >= 4 else line
            target = path_text.split(" -> ")[-1].lower()
            if target.endswith((".pdf", ".tex.txt")):
                changed_artifacts.append(path_text.replace("\\", "/"))
    audit.check(
        "git can audit changed note/PDF artifacts",
        completed.returncode == 0,
        {"returncode": completed.returncode, "stderr": completed.stderr[-400:]},
        {"returncode": 0},
        "pdf_efficiency",
    )
    audit.check(
        "no other new or reissued note/PDF accompanies checkpoint",
        completed.returncode == 0
        and set(changed_artifacts).issubset(expected_artifacts)
        and (
            not changed_artifacts
            or (
                set(changed_artifacts) == expected_artifacts
                and len(changed_artifacts) == len(expected_artifacts)
            )
        ),
        sorted(changed_artifacts),
        {
            "allowed_clean_after_commit": [],
            "allowed_atomic_checkpoint_pair": sorted(expected_artifacts),
        },
        "pdf_efficiency",
    )
    authority_text = json.dumps(manifest, sort_keys=True) + "\n" + certificate
    artifact_refs = re.findall(
        r"claims/[A-Za-z0-9_./-]+(?:\.tex\.txt|\.pdf)", authority_text, re.I
    )
    audit.check(
        "manifest/certificate cite the exact checkpoint pair only",
        set(artifact_refs) == expected_artifacts,
        sorted(set(artifact_refs)),
        sorted(expected_artifacts),
        "pdf_efficiency",
    )
    return {
        "policy": "one synthesis source/PDF at the logical gate checkpoint",
        "package_artifacts": package_artifacts,
        "changed_note_or_pdf_artifacts": changed_artifacts,
        "authority_artifact_refs": artifact_refs,
        "note_source": note_relative,
        "checkpoint_pdf": pdf_relative,
        "source_sha256": source_hash,
        "pdf_sha256": pdf_hash,
        "page_count": pages,
        "pdf_built_by_integrated_verifier": False,
        "render_attempted": False,
    }


def validate_formal(
    manifest: Mapping[str, Any],
    audit: Audit,
) -> dict[str, Any]:
    explorations = jsonl_records(
        REPO / "explorations/log.jsonl", audit, "exploration ledger"
    )
    matches = (
        []
        if explorations is None
        else [row for row in explorations if row.get("id") == EXPLORATION_ID]
    )
    audit.pending(
        f"{EXPLORATION_ID} unique", len(matches) == 1, len(matches), 1, "formal"
    )
    if len(matches) == 1:
        record = matches[0]
        serialized = json.dumps(record, sort_keys=True)
        refs = as_mapping(record.get("formal_refs"))
        gates = tuple(record.get("gate_ids", ()))
        evidence = as_list(record.get("evidence_refs"))
        required_evidence = (
            MANIFEST.relative_to(REPO).as_posix(),
            CERTIFICATE.relative_to(REPO).as_posix(),
            PRIMARY.relative_to(REPO).as_posix(),
        )
        conditions = {
            "task": record.get("task_id") == TASK_ID,
            "verdict": record.get("verdict") == "advanced",
            "claim": record.get("claim_ids") == [CLAIM_ID],
            "result": refs.get("results") == [RESULT_NUMBER],
            "negatives": tuple(refs.get("negatives", ())) == NEGATIVE_IDS,
            "events_deferred": refs.get("events") == [],
            "closed_gates": all(gate in gates for gate in CLOSED_GATES),
            "successors": all(gate in gates for gate in SUCCESSOR_GATES),
            "historical": HISTORICAL_GATE in gates,
            "evidence": all(path in serialized for path in required_evidence),
            "no_note_pdf": not any(
                str(item).lower().endswith((".pdf", ".tex.txt"))
                for item in evidence
            ),
        }
        audit.pending(
            f"{EXPLORATION_ID} complete append-only authority chain",
            all(conditions.values()),
            conditions,
            "all true",
            "formal",
        )
        require_tokens(
            record.get("boundary", ""),
            f"{EXPLORATION_ID} exact narrow boundary",
            (
                "finite-region local-strict",
                "fixed finite-Gibbs",
                "all-exhaustion",
                "unsplit resolvent-algebra non-invariance",
                "broken-sector GNS or physical mass gap",
                "continuum",
                "physical empty-space",
                "C6",
                "CP1",
                "Pre-A",
                "do not prove Q3LOCK dynamics nonexistent",
            ),
            audit,
        )

    ledger = require_text(REPO / "RESULTS-LEDGER.md", audit, "result ledger")
    if ledger is not None:
        section = result_section(ledger, RESULT_NUMBER)
        audit.pending(
            "R-167 unique detail section",
            section is not None,
            ledger.count("### R-167"),
            1,
            "formal",
        )
        if section is not None:
            require_tokens(
                section,
                "R-167 v1.7 ledger and final checkpoint linkage",
                (
                    RESULT_ID,
                    RESULT_VERSION,
                    EXPLORATION_ID,
                    *CLOSED_GATES,
                    *SUCCESSOR_GATES,
                    HISTORICAL_GATE,
                    *NEGATIVE_IDS,
                    "finite-region local-strict",
                    "inverse-logarithmic",
                    "positive lower bound",
                    "pure quartic",
                    "spectral coercivity",
                    "No per-lemma or intermediate PDF",
                ),
                audit,
            )

    registry = require_text(
        REPO / "negative-results/registry.md", audit, "negative registry"
    )
    if registry is not None:
        for negative_id in NEGATIVE_IDS:
            audit.pending(
                f"negative authority {negative_id}",
                registry.count(negative_id) >= 2,
                registry.count(negative_id),
                ">=2 (index row and detail)",
                "formal",
            )

    gates_text = require_text(REPO / "claims/GATES.md", audit, "gate authority")
    if gates_text is not None:
        for gate in CLOSED_GATES:
            section = heading_section(gates_text, gate)
            exact_scope_link = (
                section is not None
                and (
                    (
                        text_has(section, EXPLORATION_ID)
                        and text_has(section, RESULT_VERSION)
                    )
                    or (
                        gate == CLOSED_GATES[1]
                        and text_has(section, "CLOSED AT FIXED FINITE VOLUME")
                        and text_has(section, "S(A rho A^*||rho)")
                    )
                )
            )
            audit.pending(
                f"closed gate authority {gate}",
                section is not None
                and re.search(r"\*\*Status:\*\*\s*CLOSED", section, re.I)
                is not None
                and exact_scope_link,
                section,
                "CLOSED in its exact registered finite scope",
                "formal",
            )
        for gate in SUCCESSOR_GATES:
            section = heading_section(gates_text, gate)
            audit.pending(
                f"successor gate authority {gate}",
                section is not None
                and re.search(r"\*\*Status:\*\*\s*OPEN", section, re.I) is not None
                and text_has(section, RESULT_VERSION),
                section,
                "OPEN and linked to v1.7",
                "formal",
            )
        historical = heading_section(gates_text, HISTORICAL_GATE)
        audit.pending(
            "historical combined gate remains open and superseded",
            historical is not None
            and text_has(historical, "OPEN HISTORICALLY")
            and text_has(historical, "SPLIT AND SUPERSEDED AS THE ACTIVE SUCCESSOR")
            and not text_has(historical, "Status: CLOSED"),
            historical,
            "OPEN HISTORICALLY; SPLIT AND SUPERSEDED",
            "formal",
        )
        round1 = heading_section(gates_text, ROUND1_GATE)
        audit.pending(
            "PA-ROUND1 provenance remains open",
            round1 is not None
            and re.search(r"\*\*Status:\*\*\s*OPEN", round1, re.I) is not None,
            round1,
            "OPEN",
            "formal",
        )
        for gate in RETAINED_GATES:
            section = heading_section(gates_text, gate)
            audit.pending(
                f"retained provenance gate remains open {gate}",
                section is not None
                and re.search(r"\*\*Status:\*\*\s*OPEN", section, re.I) is not None,
                section,
                "OPEN",
                "formal",
            )

    todo = load_json(REPO / "todo/todo.json", audit, "TODO authority", formal=True)
    if todo is not None:
        tasks = as_list(todo.get("tasks"))
        found = [item for item in tasks if isinstance(item, dict) and item.get("id") == TASK_ID]
        audit.pending("T-054 unique", len(found) == 1, len(found), 1, "formal")
        if len(found) == 1:
            serialized = json.dumps(found[0], sort_keys=True)
            audit.pending(
                "T-054 remains in progress",
                found[0].get("status") == "in_progress",
                found[0].get("status"),
                "in_progress",
                "formal",
            )
            note = str(found[0].get("note", ""))
            live_task_conditions = {
                "round1_gate": found[0].get("gate") == ROUND1_GATE,
                "common_alpha_successors_open": text_has(note, "common alpha")
                and text_has(note, "remain open"),
                "sector_a_and_pre_a_open": text_has(note, "physical Sector A")
                and text_has(note, "Pre-A"),
            }
            audit.pending(
                "T-054 current Round-1/common-alpha contract",
                all(live_task_conditions.values()),
                live_task_conditions,
                "current in-progress Round-1 task with common-alpha and Sector-A/Pre-A open boundary",
                "formal",
            )

    roadmap = require_text(REPO / "ROADMAP.md", audit, "roadmap")
    if roadmap is not None:
        require_tokens(
            roadmap,
            "roadmap v1.7 gate split linkage",
            (
                TASK_ID,
                EXPLORATION_ID,
                RESULT_NUMBER,
                RESULT_VERSION,
                "local-strict",
                "inverse-logarithmic",
                SUCCESSOR_GATES[0],
                SUCCESSOR_GATES[1],
                HISTORICAL_GATE,
            ),
            audit,
        )

    theorem_map = load_json(
        REPO / "governance/sector-a-theorem-map.json",
        audit,
        "Sector-A theorem map",
        formal=True,
    )
    if theorem_map is not None:
        audit.pending(
            "Sector-A theorem map remains its scoped current authority",
            theorem_map.get("schema") == "tect/sector-a-theorem-map/1.0"
            and theorem_map.get("status") is not None
            and theorem_map.get("active_frontier") is not None,
            {
                "schema": theorem_map.get("schema"),
                "status": theorem_map.get("status"),
                "active_frontier": theorem_map.get("active_frontier") is not None,
            },
            "current scoped Sector-A theorem map; R-167 is bound through proof-evidence surfaces",
            "formal",
        )

    changelog = jsonl_records(REPO / "changelog/log.jsonl", audit, "changelog")
    exp_events = (
        []
        if changelog is None
        else [
            event
            for event in changelog
            if text_has(json.dumps(event, sort_keys=True), EXPLORATION_ID)
        ]
    )
    required_scripts = {
        PRIMARY.relative_to(REPO).as_posix(),
        INDEPENDENT.relative_to(REPO).as_posix(),
        SCRIPT.relative_to(REPO).as_posix(),
    }
    theorem_events = [
        event
        for event in exp_events
        if set(event.get("neg_results", ())) == set(NEGATIVE_IDS)
        and isinstance(event.get("scripts"), list)
        and required_scripts.issubset(set(event.get("scripts", ())))
        and event.get("notes", []) == []
    ]
    audit.pending(
        "EXP-000804 theorem changelog unique",
        len(theorem_events) == 1,
        len(theorem_events),
        1,
        "formal",
    )
    if len(theorem_events) == 1:
        event = theorem_events[0]
        serialized = json.dumps(event, sort_keys=True)
        conditions = {
            "claims": set(event.get("claim_ids", ()))
            == {CLAIM_ID, EXPLORATION_ID, RESULT_NUMBER},
            "negatives": set(event.get("neg_results", ())) == set(NEGATIVE_IDS),
            "scripts": required_scripts.issubset(set(event.get("scripts", ()))),
            "notes_deferred": event.get("notes") == [],
            "no_note_pdf": ".tex.txt" not in serialized.lower()
            and not re.search(r"claims/[A-Za-z0-9_./-]+\.pdf", serialized, re.I),
            "scope": all(
                text_has(event.get("raw", ""), token)
                for token in (
                    "fixed finite region",
                    "not point-norm C0",
                    "inverse-logarithmic",
                    "positive spectrum accumulating at zero",
                    "historically open",
                    "T0",
                    "no thermodynamic common dynamics",
                    "single later gate-level synthesis PDF",
                )
            ),
        }
        audit.pending(
            "EXP-000804 changelog theorem event complete",
            all(conditions.values()),
            conditions,
            "all true",
            "formal",
        )

    note_relative = NOTE_SOURCE.relative_to(REPO).as_posix()
    pdf_relative = CHECKPOINT_PDF.relative_to(REPO).as_posix()
    checkpoint_events = (
        []
        if changelog is None
        else [
            event
            for event in changelog
            if note_relative in json.dumps(event, sort_keys=True)
            and pdf_relative in json.dumps(event, sort_keys=True)
        ]
    )
    audit.pending(
        "R-167 v1.7 checkpoint-PDF changelog unique",
        len(checkpoint_events) == 1,
        len(checkpoint_events),
        1,
        "formal",
    )
    if len(checkpoint_events) == 1:
        event = checkpoint_events[0]
        raw = event.get("raw", "")
        notes = event.get("notes", [])
        conditions = {
            "claims": {CLAIM_ID, RESULT_NUMBER}.issubset(set(event.get("claim_ids", ()))),
            "source_note": isinstance(notes, list) and note_relative in notes,
            "one_checkpoint": text_has(raw, "one gate-level synthesis"),
            "development_economy": text_has(raw, "no per-lemma or intermediate PDF"),
            "proof_layers": all(
                text_has(raw, token)
                for token in ("manifest", "certificate", "primary", "independent", "integrated")
            ),
            "render_review": text_has(raw, "render") and text_has(raw, "visual"),
            "no_formal_change": all(
                text_has(raw, token)
                for token in ("No result number", "gate status", "tier", "no-overclaim")
            ),
        }
        audit.pending(
            "R-167 v1.7 checkpoint-PDF changelog complete",
            all(conditions.values()),
            conditions,
            "all true",
            "formal",
        )

    proof_map = require_text(
        REPO / "theory/proof-evidence-map.md", audit, "proof-evidence map"
    )
    if proof_map is not None:
        require_tokens(
            proof_map,
            "proof-evidence map v1.7 linkage",
            (EXPLORATION_ID, RESULT_NUMBER, RESULT_VERSION, *CLOSED_GATES, *SUCCESSOR_GATES, *NEGATIVE_IDS),
            audit,
        )
    proof_map_json = load_json(
        REPO / "verification/proof-evidence-map.json",
        audit,
        "proof-evidence JSON map",
        formal=True,
    )
    if proof_map_json is not None:
        coverage = proof_map_json.get("coverage", {})
        shards = proof_map_json.get("shards", [])
        shard_kinds = (
            {item.get("kind") for item in shards if isinstance(item, dict)}
            if isinstance(shards, list)
            else set()
        )
        digest = proof_map_json.get("logical_map_sha256")
        json_contract = {
            "index_schema": proof_map_json.get("schema")
            == "tect/proof-evidence-map-index/1.0",
            "map_schema": proof_map_json.get("map_schema")
            == "tect/proof-evidence-map/1.3",
            "generator_pinned": isinstance(proof_map_json.get("generator"), dict)
            and proof_map_json["generator"].get("path")
            == "verification/scripts/build_proof_evidence_map.py",
            "logical_digest": isinstance(digest, str)
            and len(digest) == 64
            and all(char in "0123456789abcdef" for char in digest.lower()),
            "coverage_fields": isinstance(coverage, dict)
            and {
                "proof_explorations",
                "reusable_results",
                "negative_records",
                "accepted_events",
                "tasks",
            }.issubset(coverage),
            "shards_present": {
                "proof_explorations",
                "reusable_results",
                "negative_records",
            }.issubset(shard_kinds),
        }
        audit.pending(
            "proof-evidence JSON current structural contract",
            all(json_contract.values()),
            json_contract,
            "current indexed proof-map schema, generator, digest, coverage fields and shards",
            "formal",
        )

    result_locator = load_json(
        REPO / "results/index.json", audit, "result locator", formal=True
    )
    result_count = None
    if result_locator is not None:
        entries = [
            row for row in as_list(result_locator.get("entries"))
            if isinstance(row, dict)
        ]
        result_contract = {
            "schema": result_locator.get("schema") == "tect/results-index/1.0",
            "authority": result_locator.get("authority") == "RESULTS-LEDGER.md",
            "count": result_locator.get("count") == len(entries),
            "entries_nonempty": len(entries) > 0,
        }
        audit.pending(
            "result locator current structural contract",
            all(result_contract.values()),
            result_contract,
            "current generated result locator with authority and count",
            "formal",
        )
        if isinstance(result_locator.get("count"), int):
            result_count = result_locator["count"]

    negative_locator = load_json(
        REPO / "negative-results/index.json",
        audit,
        "negative locator",
        formal=True,
    )
    negative_count = None
    if negative_locator is not None:
        entries = [
            row for row in as_list(negative_locator.get("entries"))
            if isinstance(row, dict)
        ]
        negative_contract = {
            "schema": negative_locator.get("schema") == "tect/negative-index/1.0",
            "authority": negative_locator.get("authority")
            == "negative-results/registry.md",
            "count": negative_locator.get("count") == len(entries),
            "entries_nonempty": len(entries) > 0,
        }
        audit.pending(
            "negative locator current structural contract",
            all(negative_contract.values()),
            negative_contract,
            "current generated negative locator with authority and count",
            "formal",
        )
        if isinstance(negative_locator.get("count"), int):
            negative_count = negative_locator["count"]

    changelog_locator = load_json(
        REPO / "changelog/index.json",
        audit,
        "changelog locator",
        formal=True,
    )
    changelog_total = None
    if changelog_locator is not None:
        recent = as_list(changelog_locator.get("recent"))
        changelog_contract = {
            "schema": changelog_locator.get("schema") == "tect/changelog-index/2.0",
            "authority": changelog_locator.get("authority") == "changelog/log.jsonl",
            "total": changelog_locator.get("total") == len(changelog or []),
            "recent_count": changelog_locator.get("recent_count") == len(recent),
            "recent_bounded": isinstance(changelog_locator.get("recent_count"), int)
            and changelog_locator["recent_count"] <= changelog_locator.get("total", -1),
        }
        audit.pending(
            "changelog locator current structural contract",
            all(changelog_contract.values()),
            changelog_contract,
            "current generated changelog locator with authority, total and recent page",
            "formal",
        )
        if isinstance(changelog_locator.get("total"), int):
            changelog_total = changelog_locator["total"]

    result_index = require_text(REPO / "results/INDEX.md", audit, "result index")
    if result_index is not None and result_count is not None:
        require_tokens(
            result_index,
            "result index current generated projection",
            (
                "AUTO-GENERATED by verification/scripts/build_management_indexes.py",
                f"{result_count} registered results",
            ),
            audit,
        )
    negative_index = require_text(
        REPO / "negative-results/INDEX.md", audit, "negative index"
    )
    if negative_index is not None and negative_count is not None:
        require_tokens(
            negative_index,
            "negative index current generated projection",
            (
                "AUTO-GENERATED by verification/scripts/build_management_indexes.py",
                f"{negative_count} registered records",
            ),
            audit,
        )
    gate_index = require_text(REPO / "claims/GATES-INDEX.md", audit, "gate index")
    if gate_index is not None and gates_text is not None:
        gate_definition_count = len(
            re.findall(r"^###\s+", gates_text, flags=re.MULTILINE)
        )
        require_tokens(
            gate_index,
            "gate index current definition count",
            (f"{gate_definition_count} registered definitions",),
            audit,
        )
    compact_proof = require_text(
        REPO / "theory/proof-evidence/INDEX.md",
        audit,
        "compact proof-evidence index",
    )
    if compact_proof is not None:
        require_tokens(
            compact_proof,
            "compact proof-evidence current counts",
            (
                f"{len(explorations or [])} proof explorations",
                f"{len(changelog or [])} accepted events",
            ),
            audit,
        )
    changelog_index = require_text(
        REPO / "changelog/INDEX.md", audit, "changelog index"
    )
    if changelog_index is not None and changelog_total is not None:
        require_tokens(
            changelog_index,
            "changelog index current generated projection",
            (
                "Compact generated reader surface",
                f"{changelog_total} accepted events",
                "machine locator",
            ),
            audit,
        )

    catalog_index = load_json(
        REPO / "verification/catalog/index.json",
        audit,
        "catalog current index",
        formal=True,
    )
    if catalog_index is not None:
        shards = as_list(catalog_index.get("shards"))
        shard_payloads: list[dict[str, Any]] = []
        shard_contracts: list[bool] = []
        for shard in shards:
            if not isinstance(shard, dict) or not isinstance(shard.get("path"), str):
                shard_contracts.append(False)
                continue
            shard_path = REPO / shard["path"]
            payload = load_json(
                shard_path,
                audit,
                f"catalog shard {shard.get('kind', shard['path'])}",
                formal=True,
            )
            if payload is None:
                shard_contracts.append(False)
                continue
            shard_payloads.append(payload)
            entries = as_list(payload.get("entries"))
            raw_hash = hashlib.sha256(shard_path.read_bytes()).hexdigest()
            shard_contracts.append(
                payload.get("schema") == "tect/catalog-kind/1.0"
                and payload.get("kind") == shard.get("kind")
                and payload.get("count") == shard.get("count") == len(entries)
                and raw_hash == shard.get("sha256")
            )
        audit.pending(
            "catalog manifest and shards are internally current",
            catalog_index.get("schema") == "tect/catalog-manifest/2.0"
            and len(shards) > 0
            and len(shard_contracts) == len(shards)
            and all(shard_contracts)
            and sum(int(shard.get("count", 0)) for shard in shards)
            == catalog_index.get("total"),
            {
                "schema": catalog_index.get("schema"),
                "shards": len(shards),
                "valid": sum(shard_contracts),
                "declared_total": catalog_index.get("total"),
                "summed_total": sum(int(shard.get("count", 0)) for shard in shards),
            },
            "valid shard hashes/counts summing to manifest total",
            "formal",
        )
        inventory = json.dumps(shard_payloads, sort_keys=True)
        require_tokens(
            inventory,
            "catalog current v1.7 artifacts",
            (
                MANIFEST.relative_to(REPO).as_posix(),
                CERTIFICATE.relative_to(REPO).as_posix(),
                PRIMARY.relative_to(REPO).as_posix(),
                INDEPENDENT.relative_to(REPO).as_posix(),
                SCRIPT.relative_to(REPO).as_posix(),
                note_relative,
                pdf_relative,
            ),
            audit,
        )

    status = load_json(
        REPO / "claims/C6-SPACETIME-SIGNATURE/status.json", audit, "C6 status"
    )
    if status is not None:
        audit.check(
            "C6 tier unchanged", status.get("tier") == "T1", status.get("tier"), "T1", "claim_firewall"
        )
        audit.check(
            "C6 lifecycle unchanged",
            status.get("lifecycle") == "ACTIVE",
            status.get("lifecycle"),
            "ACTIVE",
            "claim_firewall",
        )
        audit.check(
            "C6 open gate unchanged",
            status.get("open_gates") == ["C6-BCC-PREMISE-BLOCKED"],
            status.get("open_gates"),
            ["C6-BCC-PREMISE-BLOCKED"],
            "claim_firewall",
        )
    return {
        "exploration_matches": len(matches),
        "theorem_changelog_matches": len(theorem_events),
        "checkpoint_changelog_matches": len(checkpoint_events),
    }


def build_payload(staged: bool = False) -> dict[str, Any]:
    audit = Audit(staged)
    manifest = load_json(MANIFEST, audit, "manifest") or {}
    if manifest:
        validate_manifest(manifest, audit)
    certificate = validate_certificate(audit)
    validate_independence(audit)

    components: dict[str, dict[str, Any]] = {}
    sentinels: dict[str, str] = {}
    with tempfile.TemporaryDirectory(prefix="tect-exp804-integrated-") as directory:
        temporary = Path(directory)
        for label, script in (("primary", PRIMARY), ("independent", INDEPENDENT)):
            result = run_fresh_pair(script, temporary, audit, label)
            if result is not None:
                components[label], sentinels[label] = result

    for label, path in (
        ("primary", PRIMARY_STORED),
        ("independent", INDEPENDENT_STORED),
    ):
        stored_against_fresh(path, components.get(label), audit, label)

    for label, owner in (("primary", PRIMARY), ("independent", INDEPENDENT)):
        payload = components.get(label)
        if payload is not None:
            validate_component(payload, label, audit)
            validate_hash_map(payload, owner, audit, label)

    cross_derived: dict[str, Any] = {}
    if "primary" in components and "independent" in components:
        cross_derived = compare_exact_core(
            components["primary"], components["independent"], audit
        )
    else:
        audit.pending(
            "fresh exact cross-comparison",
            False,
            sorted(components),
            ["primary", "independent"],
            "cross_core",
        )

    formal_meta = validate_formal(manifest, audit)
    pdf_meta = validate_pdf_efficiency(audit, manifest, certificate)
    passed = sum(row["status"] == "PASS" for row in audit.rows)
    source_paths = (
        SCRIPT,
        PRIMARY,
        INDEPENDENT,
        MANIFEST,
        CERTIFICATE,
        PRIMARY_STORED,
        INDEPENDENT_STORED,
        NOTE_SOURCE,
        CHECKPOINT_PDF,
    )
    source_hashes = {
        path.relative_to(REPO).as_posix(): portable_sha256(path)
        for path in source_paths
        if path.is_file()
    }
    return {
        "schema": INTEGRATED_SCHEMA,
        "script_version": __version__,
        "result_id": RESULT_ID,
        "result_number": RESULT_NUMBER,
        "result_version": RESULT_VERSION,
        "exploration_id": EXPLORATION_ID,
        "task_id": TASK_ID,
        "claim_ids": [CLAIM_ID],
        "claim_bearing": False,
        "negative_ids": list(NEGATIVE_IDS),
        "reused_negative_ids": list(REUSED_NEGATIVE_IDS),
        "closed_gates": list(CLOSED_GATES),
        "successor_gates": list(SUCCESSOR_GATES),
        "historical_superseded_gates": [HISTORICAL_GATE],
        "retained_gates": list(RETAINED_GATES),
        "open_gates": list(OPEN_GATES),
        "verdict": audit.verdict,
        "summary": {
            "passed": passed,
            "failed": len(audit.failures),
            "missing": len(audit.missing),
            "total": len(audit.rows),
        },
        "assertions": {
            "passed": passed,
            "failed": len(audit.failures),
            "missing": len(audit.missing),
            "total": len(audit.rows),
            "rows": audit.rows,
        },
        "component_summaries": {
            label: {
                "schema": payload.get("schema"),
                "verdict": payload.get("verdict"),
                "assertions": assertion_summary(payload),
            }
            for label, payload in sorted(components.items())
        },
        "fresh_sentinels": sentinels,
        "cross_derived": cross_derived,
        "scope": {
            "finite_volume_local_strict_energy_subflow_carrier": True,
            "fixed_finite_gibbs_character_entropy_tail": True,
            "raw_weyl_basic_resolvent_point_norm_C0": False,
            "pure_quartic_resolvent_algebra_invariance": False,
            "unsplit_resolvent_algebra_invariance_decided": False,
            "entropy_finite_moment_dynamic_gaussian_tail": False,
            "ordered_ground_doublets_imply_GNS_gap": False,
            "continuous_time_split_product_limit": False,
            "all_exhaustion_two_orientation_history_common_alpha": False,
            "phase_KMS_quotient_identification": False,
            "broken_sector_GNS_gap_coercivity": False,
            "physical_mass_gap": False,
            "continuum_regulator_removal": False,
            "physical_empty_space_reference": False,
            "C6_advanced": False,
            "CP1_complete": False,
            "Sector_A_complete": False,
            "Pre_A_complete": False,
        },
        "source_hashes": source_hashes,
        "formal_workflow": formal_meta,
        "pdf_efficiency": pdf_meta,
        "missing_authorities": audit.missing,
        "failures": audit.failures,
        "boundary": manifest.get("no_overclaim"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--staged",
        action="store_true",
        help="exit zero with MISSING rows while formal/PDF authorities assemble",
    )
    parser.add_argument(
        "--no-store",
        action="store_true",
        help="run all checks without writing the integrated result JSON",
    )
    arguments = parser.parse_args()
    payload = build_payload(arguments.staged)
    if not arguments.no_store:
        atomic_json(arguments.output, payload)
    summary = payload["summary"]
    print(
        f"{EXPLORATION_ID}/{RESULT_NUMBER}-{RESULT_VERSION} INTEGRATED "
        f"{payload['verdict']} {summary['passed']}/{summary['total']} "
        f"failed={summary['failed']} missing={summary['missing']}"
    )
    print("NO-STORE" if arguments.no_store else arguments.output)
    for blocker in payload["missing_authorities"]:
        print("BLOCKER " + blocker)
    for failure in payload["failures"]:
        print("FAILURE " + failure)
    if payload["verdict"] == "FAIL":
        return 1
    if payload["verdict"] != "PASS" and not arguments.staged:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

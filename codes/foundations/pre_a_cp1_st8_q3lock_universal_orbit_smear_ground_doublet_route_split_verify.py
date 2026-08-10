#!/usr/bin/env python3
"""Integrated verifier for EXP-000803 / R-167 v1.6.

The primary and independent theorem implementations are executed twice in
fresh child processes.  Their deterministic payloads are checked against the
stored run JSONs, the independent implementation is protected by an AST/import
firewall, and the exact cross-invariants of the route split are reconciled.

``--staged`` is assembly-safe.  A missing implementation, run JSON, exploration
record, or generated authority is recorded as ``MISSING`` and yields an
``INCOMPLETE`` verdict.  A contradiction in an available mathematical payload
is always ``FAIL``.  This verifier never builds or renders the checkpoint PDF;
it reads the issued source/PDF pair, checks both text extractors, and binds the
pair to the formal checkpoint authorities.
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

import pdfplumber
from pypdf import PdfReader


__version__ = "1.1.0"
REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-universal-orbit-smear-ground-doublet-route-split"

RESULT_ID = (
    "PA-CP1-ST8-Q3LOCK-SECOND-WEIGHTED-ENERGY-MOMENT-AND-"
    "COMMON-ALPHA-CAUCHY-GATE-SPLIT"
)
RESULT_NUMBER = "R-167"
RESULT_VERSION = "v1.6"
EXPLORATION_ID = "EXP-000803"
TASK_ID = "T-054"
CLAIM_ID = "C6-SPACETIME-SIGNATURE"

CLOSED_GATES = (
    "PA-CP1-ST8-Q3LOCK-SELECTED-TANGENT-RAW-FINITE-ORBIT-WORD-"
    "MOMENT-COMPLETION",
    "PA-CP1-ST8-Q3LOCK-ZERO-SOURCE-FINITE-HAMILTONIAN-L1-ORBIT-"
    "SMEAR-CSTAR-CARRIER",
    "PA-CP1-ST8-Q3LOCK-UNIVERSAL-ORBIT-SMEAR-DISTINCT-ALGEBRAIC-"
    "GROUND-DOUBLETS",
)
RETAINED_GATES = (
    "PA-CP1-ST8-Q3LOCK-ALL-EXHAUSTION-MIXTURE-L2-LOCALITY-AND-"
    "BETA-INDEPENDENT-CSTAR-DYNAMICS",
    "PA-CP1-ST8-Q3LOCK-HAMILTONIAN-THERMODYNAMIC-IDENTIFICATION-"
    "IN-CANONICAL-OS-MIXTURE",
    "PA-CP1-ST8-Q3LOCK-PROJECTED-DUHAMEL-MODULAR-C1-MULTIPLIER-"
    "LOCALITY",
)
SUCCESSOR_GATE = (
    "PA-CP1-ST8-Q3LOCK-QUASI-LOCAL-RAW-OSCILLATOR-ALL-EXHAUSTION-"
    "COMMON-ALPHA-AND-BROKEN-GNS-GAP"
)
ROUND1_GATE = "PA-ROUND1-EVIDENCE-ROLE-AND-MINIMUM-MANIFEST-FREEZE"
OPEN_GATES = (SUCCESSOR_GATE, ROUND1_GATE)

NEW_NEGATIVE_IDS = (
    "NG-2026-08-10-PRE-A-ST8-Q3LOCK-STATIC-TAIL-ONLY-PROJECTED-"
    "ORBIT-LOCALITY",
)
REUSED_NEGATIVE_IDS = (
    "NG-2026-08-09-PRE-A-ST8-Q3LOCK-POSTHOC-DIRECT-SUM-COMMON-"
    "DYNAMICS",
    "NG-2026-08-10-PRE-A-ST8-Q3LOCK-FIXED-BETA-ENVELOPE-"
    "AUTOMATIC-CROSS-BETA-GLUING",
)
ALL_NEGATIVE_IDS = (*NEW_NEGATIVE_IDS, *REUSED_NEGATIVE_IDS)

PRIMARY = REPO / f"codes/foundations/{SLUG.replace('-', '_')}.py"
INDEPENDENT = REPO / f"codes/foundations/{SLUG.replace('-', '_')}_independent.py"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260810.md"
NOTE_SOURCE = REPO / (
    "claims/C6-SPACETIME-SIGNATURE/notes/"
    "pre-a-q3lock-universal-orbit-smear-ground-doublet-route-split-"
    "260810-v0.5.tex.txt"
)
CHECKPOINT_PDF = NOTE_SOURCE.with_name(
    NOTE_SOURCE.name.removesuffix(".tex.txt") + ".pdf"
)
PRIMARY_STORED = REPO / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    f"2026-08-10-primary-{SLUG}/result.json"
)
INDEPENDENT_STORED = REPO / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    f"2026-08-10-independent-{SLUG}/result.json"
)
DEFAULT_OUTPUT = REPO / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    f"2026-08-10-integrated-{SLUG}/result.json"
)

PRIMARY_SCHEMA = f"tect/{SLUG}-primary-result/1.0"
INDEPENDENT_SCHEMA = f"tect/{SLUG}-independent-result/1.0"
MINIMUM_PRIMARY_ASSERTIONS = 50
MINIMUM_INDEPENDENT_ASSERTIONS = 45


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


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
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
    text = (
        str(value)
        .lower()
        .translate(
            str.maketrans(
                {
                    "ﬁ": "fi",
                    "ﬂ": "fl",
                    "ﬀ": "ff",
                    "ﬃ": "ffi",
                    "ﬄ": "ffl",
                }
            )
        )
        .replace("\\", "")
    )
    return re.sub(r"[^a-z0-9]+", "", text)


def text_has(text: Any, token: Any) -> bool:
    return compact_text(token) in compact_text(text)


class Audit:
    """Collect defects without hiding staged missing-authority state."""

    def __init__(self, staged: bool) -> None:
        self.staged = staged
        self.rows: list[dict[str, Any]] = []
        self.failures: list[str] = []
        self.missing: list[str] = []

    def _row(
        self, name: str, status: str, actual: Any, expected: Any, group: str
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
        self, name: str, condition: bool, actual: Any, expected: Any, group: str
    ) -> bool:
        if condition:
            self._row(name, "PASS", actual, expected, group)
            return True
        self._row(name, "FAIL", actual, expected, group)
        self.failures.append(f"{group}: {name}")
        return False

    def pending(
        self, name: str, condition: bool, actual: Any, expected: Any, group: str
    ) -> bool:
        if condition:
            self._row(name, "PASS", actual, expected, group)
            return True
        if self.staged:
            self._row(name, "MISSING", actual, expected, group)
            self.missing.append(f"{group}: {name}")
            return False
        return self.check(name, False, actual, expected, group)

    def require(
        self, name: str, condition: bool, actual: Any, expected: Any, group: str
    ) -> bool:
        if condition:
            self._row(name, "PASS", actual, expected, group)
            return True
        self._row(name, "MISSING", actual, expected, group)
        self.missing.append(f"{group}: {name}")
        return False

    @property
    def verdict(self) -> str:
        if self.failures:
            return "FAIL"
        if self.missing:
            return "INCOMPLETE"
        return "PASS"


def load_json(
    path: Path, audit: Audit, label: str, *, formal: bool = False
) -> dict[str, Any] | None:
    if not path.is_file():
        audit.require(
            f"{label} exists", False, path.relative_to(REPO), "file", "files"
        )
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        reporter = audit.pending if formal else audit.check
        reporter(f"{label} parses", False, error, "valid JSON object", "files")
        return None
    if not isinstance(value, dict):
        reporter = audit.pending if formal else audit.check
        reporter(f"{label} object", False, type(value).__name__, "dict", "files")
        return None
    audit.check(f"{label} parses", True, path.relative_to(REPO), "dict", "files")
    return value


def require_text(path: Path, audit: Audit, label: str) -> str | None:
    if not path.is_file():
        audit.require(
            f"{label} exists", False, path.relative_to(REPO), "file", "formal"
        )
        return None
    try:
        value = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        audit.pending(f"{label} UTF-8", False, error, "readable UTF-8", "formal")
        return None
    audit.pending(f"{label} readable", bool(value), len(value), ">0", "formal")
    return value


def jsonl_records(
    path: Path, audit: Audit, label: str
) -> list[dict[str, Any]] | None:
    if not path.is_file():
        audit.require(
            f"{label} exists", False, path.relative_to(REPO), "file", "formal"
        )
        return None
    rows: list[dict[str, Any]] = []
    try:
        with path.open("r", encoding="utf-8") as stream:
            for line_number, line in enumerate(stream, 1):
                if not line.strip():
                    continue
                value = json.loads(line)
                if not isinstance(value, dict):
                    raise ValueError(f"line {line_number} is not an object")
                rows.append(value)
    except (OSError, UnicodeError, json.JSONDecodeError, ValueError) as error:
        audit.pending(f"{label} parses", False, error, "valid JSONL", "formal")
        return None
    audit.check(f"{label} parses", bool(rows), len(rows), ">=1", "formal")
    return rows


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
    + str(summary.get("passed"))
    + "/"
    + str(summary.get("total"))
)
"""


def run_once(
    script: Path, run_directory: Path, audit: Audit, label: str
) -> tuple[dict[str, Any], str] | None:
    if not script.is_file():
        audit.require(
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
            "fresh child-process derivation exits 0 and writes JSON",
            "freshness",
        )
        return None
    try:
        payload = json.loads(output.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        audit.check(f"{label} JSON", False, error, "valid JSON", "freshness")
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
        f"{label} fresh sentinel",
        bool(sentinel),
        sentinel,
        "FRESH-COMPONENT ...",
        "freshness",
    )
    return payload, sentinel


def run_fresh_pair(
    script: Path, temporary_root: Path, audit: Audit, label: str
) -> tuple[dict[str, Any], str] | None:
    if not script.is_file():
        audit.require(
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
        audit.require(
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
        audit.require(
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
            f"{label} stored parses", False, error, "valid JSON", "freshness"
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
    stored_bytes = canonical_payload(stored, (REPO,))
    fresh_bytes = canonical_payload(fresh, (REPO,)) if fresh is not None else b""
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


def assertion_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    assertions = payload.get("assertions", [])
    if isinstance(assertions, list):
        return [row for row in assertions if isinstance(row, dict)]
    if isinstance(assertions, dict) and isinstance(assertions.get("rows"), list):
        return [row for row in assertions["rows"] if isinstance(row, dict)]
    return []


def assertion_summary(payload: dict[str, Any]) -> tuple[Any, Any, Any, Any]:
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
    return None, None, None, None


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
            "PASS after authority synchronisation",
            "components",
        )
    else:
        audit.check(
            f"{label} verdict",
            verdict_ok,
            payload.get("verdict"),
            "PASS",
            "components",
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
        f"passed=total>={minimum}, failed=missing=0",
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

    actual_new = payload.get("negative_ids")
    actual_reused = payload.get("reused_negative_ids")
    audit.check(
        f"{label} exact new negative set",
        tuple(actual_new or ()) == NEW_NEGATIVE_IDS,
        actual_new,
        list(NEW_NEGATIVE_IDS),
        "components",
    )
    audit.check(
        f"{label} exact reused negative set",
        tuple(actual_reused or ()) == REUSED_NEGATIVE_IDS,
        actual_reused,
        list(REUSED_NEGATIVE_IDS),
        "components",
    )
    actual_closed = payload.get("closed_gates", payload.get("closed_subgates"))
    audit.check(
        f"{label} exact closed gates",
        tuple(actual_closed or ()) == CLOSED_GATES,
        actual_closed,
        list(CLOSED_GATES),
        "components",
    )
    audit.check(
        f"{label} exact open gates",
        tuple(payload.get("open_gates", ())) == OPEN_GATES,
        payload.get("open_gates"),
        list(OPEN_GATES),
        "components",
    )


def validate_independence(audit: Audit) -> None:
    missing = [
        path.relative_to(REPO).as_posix()
        for path in (PRIMARY, INDEPENDENT, SCRIPT)
        if not path.is_file()
    ]
    if missing:
        audit.require("AST sources exist", False, missing, "all sources", "independence")
        return
    try:
        primary_source = PRIMARY.read_text(encoding="utf-8")
        independent_source = INDEPENDENT.read_text(encoding="utf-8")
        integrated_source = SCRIPT.read_text(encoding="utf-8")
        primary_tree = ast.parse(primary_source, filename=str(PRIMARY))
        independent_tree = ast.parse(independent_source, filename=str(INDEPENDENT))
        integrated_tree = ast.parse(integrated_source, filename=str(SCRIPT))
    except (OSError, UnicodeError, SyntaxError) as error:
        audit.check("AST parsing", False, error, "three valid ASTs", "independence")
        return

    imports: set[str] = set()
    dynamic: list[str] = []
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
        "independent dynamic import firewall",
        not dynamic,
        dynamic,
        [],
        "independence",
    )
    normalized_independent = independent_source.replace("\\", "/")
    audit.check(
        "independent does not name primary module or stored result",
        PRIMARY.stem not in independent_source
        and PRIMARY_STORED.relative_to(REPO).as_posix() not in normalized_independent,
        {
            "module_named": PRIMARY.stem in independent_source,
            "stored_named": PRIMARY_STORED.relative_to(REPO).as_posix()
            in normalized_independent,
        },
        {"module_named": False, "stored_named": False},
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
        "no primary/independent module import",
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


def validate_hash_map(
    payload: dict[str, Any], owner: Path, audit: Audit, label: str
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


def as_mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def iter_mappings(value: Any) -> Iterable[dict[str, Any]]:
    if isinstance(value, dict):
        yield value
        for item in value.values():
            yield from iter_mappings(item)
    elif isinstance(value, (list, tuple)):
        for item in value:
            yield from iter_mappings(item)


def first_value(value: Any, names: Iterable[str]) -> Any:
    wanted = {name.lower() for name in names}
    for mapping in iter_mappings(value):
        for key, item in mapping.items():
            if str(key).lower() in wanted:
                return item
    return None


def first_list(value: Any, names: Iterable[str]) -> list[Any] | None:
    found = first_value(value, names)
    return found if isinstance(found, list) else None


def find_group(
    derived: Mapping[str, Any], names: Iterable[str], key_tokens: Iterable[str]
) -> dict[str, Any]:
    for name in names:
        candidate = derived.get(name)
        if isinstance(candidate, dict):
            return candidate
    tokens = tuple(compact_text(token) for token in key_tokens)
    for key, candidate in derived.items():
        if isinstance(candidate, dict):
            compact = compact_text(key)
            if all(token in compact for token in tokens):
                return candidate
    return {}


def _safe_numeric_node(node: ast.AST) -> float:
    if isinstance(node, ast.Expression):
        return _safe_numeric_node(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return float(node.value)
    if isinstance(node, ast.UnaryOp) and isinstance(node.op, (ast.UAdd, ast.USub)):
        value = _safe_numeric_node(node.operand)
        return value if isinstance(node.op, ast.UAdd) else -value
    if isinstance(node, ast.BinOp):
        left = _safe_numeric_node(node.left)
        right = _safe_numeric_node(node.right)
        if isinstance(node.op, ast.Add):
            return left + right
        if isinstance(node.op, ast.Sub):
            return left - right
        if isinstance(node.op, ast.Mult):
            return left * right
        if isinstance(node.op, ast.Div):
            return left / right
        if isinstance(node.op, ast.Pow):
            return left**right
    if isinstance(node, ast.Name) and node.id == "pi":
        return math.pi
    if (
        isinstance(node, ast.Call)
        and isinstance(node.func, ast.Name)
        and len(node.args) == 1
        and not node.keywords
    ):
        argument = _safe_numeric_node(node.args[0])
        if node.func.id == "sqrt":
            return math.sqrt(argument)
        if node.func.id == "exp":
            return math.exp(argument)
        if node.func.id == "log":
            return math.log(argument)
    raise ValueError("unsupported numeric expression")


def as_float(value: Any) -> float | None:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, (int, float)):
        result = float(value)
        return result if math.isfinite(result) else None
    if isinstance(value, str):
        text = value.strip().replace("^", "**")
        if len(text) > 240:
            return None
        try:
            result = _safe_numeric_node(ast.parse(text, mode="eval"))
        except (SyntaxError, ValueError, ZeroDivisionError, OverflowError):
            return None
        return result if math.isfinite(result) else None
    return None


def numeric_matrix(value: Any) -> list[list[float]] | None:
    """Parse JSON matrices or the restricted ``Matrix([[...]])`` form."""

    if isinstance(value, str):
        try:
            node = ast.parse(value.strip(), mode="eval").body
        except SyntaxError:
            return None
        if (
            isinstance(node, ast.Call)
            and isinstance(node.func, ast.Name)
            and node.func.id == "Matrix"
            and len(node.args) == 1
            and not node.keywords
        ):
            node = node.args[0]
        if not isinstance(node, (ast.List, ast.Tuple)):
            return None
        rows: list[list[float]] = []
        try:
            for row_node in node.elts:
                if not isinstance(row_node, (ast.List, ast.Tuple)):
                    return None
                rows.append([_safe_numeric_node(entry) for entry in row_node.elts])
        except (ValueError, ZeroDivisionError, OverflowError):
            return None
        return rows if rows and all(len(row) == len(rows[0]) for row in rows) else None
    if not isinstance(value, (list, tuple)) or not value:
        return None
    rows = []
    for raw_row in value:
        if not isinstance(raw_row, (list, tuple)):
            return None
        row = [as_float(entry) for entry in raw_row]
        if any(entry is None for entry in row):
            return None
        rows.append([entry for entry in row if entry is not None])
    return rows if rows and all(len(row) == len(rows[0]) for row in rows) else None


def matrices_close(left: Any, right: Any, tolerance: float = 1.0e-11) -> bool:
    left_matrix, right_matrix = numeric_matrix(left), numeric_matrix(right)
    return (
        left_matrix is not None
        and right_matrix is not None
        and len(left_matrix) == len(right_matrix)
        and all(len(left_row) == len(right_row) for left_row, right_row in zip(left_matrix, right_matrix))
        and all(
            math.isclose(left_entry, right_entry, rel_tol=tolerance, abs_tol=tolerance)
            for left_row, right_row in zip(left_matrix, right_matrix)
            for left_entry, right_entry in zip(left_row, right_row)
        )
    )


def matrix_sign_pattern(value: Any, tolerance: float = 1.0e-12) -> list[list[int]] | None:
    matrix = numeric_matrix(value)
    if matrix is None:
        return None
    return [
        [0 if abs(entry) <= tolerance else (1 if entry > 0 else -1) for entry in row]
        for row in matrix
    ]


def close(left: Any, right: Any, tolerance: float = 1.0e-11) -> bool:
    left_value, right_value = as_float(left), as_float(right)
    if left_value is None or right_value is None:
        return False
    return math.isclose(left_value, right_value, rel_tol=tolerance, abs_tol=tolerance)


def positive(value: Any) -> bool:
    number = as_float(value)
    return number is not None and number > 0


def negative(value: Any) -> bool:
    number = as_float(value)
    return number is not None and number < 0


def decreasing(values: Sequence[Any]) -> bool:
    parsed = [as_float(item) for item in values]
    return bool(parsed) and all(item is not None for item in parsed) and all(
        parsed[index + 1] < parsed[index]  # type: ignore[operator]
        for index in range(len(parsed) - 1)
    )


def semantic_cross_invariants(
    payload: dict[str, Any], label: str, audit: Audit
) -> dict[str, Any]:
    derived = as_mapping(payload.get("derived"))

    recursive = find_group(
        derived,
        (
            "sequential_fejer_raw_word_recovery",
            "recursive_raw_word_recovery",
            "right_context_recursive_word_recovery",
            "right_context_recursive_smoothing",
        ),
        ("word", "recover"),
    )
    serialized_recursive = json.dumps(recursive, sort_keys=True)
    order = first_value(
        recursive, ("replacement_order", "smoothing_order", "recursive_order")
    )
    fixed_only = first_value(
        recursive,
        ("fixed_finite_word_only", "fixed_word_only", "finite_word_only"),
    )
    uniform_length = first_value(
        recursive,
        ("uniform_in_word_length", "word_length_uniform", "uniform_word_length"),
    )
    rows = first_list(recursive, ("rows", "recursion_rows", "cutoff_rows")) or []
    target = first_value(
        recursive, ("target_error", "total_error_target", "target")
    )
    exact_total = first_value(
        recursive, ("exact_total_error", "total_contextual_error", "total_error")
    )
    payload_boundary = str(payload.get("boundary", ""))
    if fixed_only is None:
        fixed_only = (
            text_has(payload_boundary, "fixed finite")
            or derived.get("selected_tangent_raw_finite_words_closed") is True
        )
    if uniform_length is None:
        uniform_length = (
            False
            if fixed_only
            and (
                text_has(payload_boundary, "all-exhaustion")
                or derived.get("all_exhaustion_spatial_cauchy_closed") is False
            )
            else None
        )
    recursive_ok = (
        bool(recursive)
        and text_has(order or serialized_recursive, "right to left")
        and fixed_only is True
        and uniform_length is False
        and bool(rows)
        and as_float(target) is not None
        and as_float(exact_total) is not None
        and as_float(exact_total) < as_float(target)  # type: ignore[operator]
        and text_has(serialized_recursive, "right")
        and text_has(serialized_recursive, "bandwidth")
    )
    audit.check(
        f"{label} exact right-context recursive word recovery",
        recursive_ok,
        {
            "order": order,
            "fixed_only": fixed_only,
            "uniform_length": uniform_length,
            "rows": len(rows),
            "exact_total": exact_total,
            "target": target,
        },
        "right-to-left, fixed finite word, exact total below target",
        "cross_core",
    )

    modular = as_mapping(derived.get("modular_right_context"))
    standard_form = as_mapping(recursive.get("standard_form_matrix_fixture"))
    if standard_form:
        standard_residual = standard_form.get("sigma_i_half_residual")
        wrong_residual = standard_form.get("wrong_orientation_residual")
        orientation_ok = (
            standard_form.get("sigma_i_half_orientation_exact") is True
            and standard_form.get("sigma_minus_i_half_orientation_fails") is True
            and matrices_close(standard_residual, [[0, 0], [0, 0]])
            and matrices_close(wrong_residual, [[6, -3], [9, 3]])
            and matrices_close(
                standard_form.get("YC_rho_half"),
                standard_form.get("Y_rho_half_sigma_i_half_C"),
            )
            and not matrices_close(
                standard_form.get("YC_rho_half"),
                standard_form.get("Y_rho_half_sigma_minus_i_half_C"),
            )
            and text_has(
                standard_form.get("modular_convention", ""),
                "sigma_s=alpha_(-beta hbar s)",
            )
            and text_has(recursive.get("right_multiplier_norm", ""), "sigma_(i/2)(C)")
            and text_has(
                recursive.get("right_multiplier_identity", ""),
                "J sigma_(-i/2)(C*) J",
            )
        )
        orientation_actual = {
            "sigma_i_half_residual": standard_residual,
            "wrong_orientation_residual": wrong_residual,
            "convention": standard_form.get("modular_convention"),
        }
    else:
        rho = numeric_matrix(modular.get("rho"))
        context = numeric_matrix(modular.get("context"))
        sigma_i_half = numeric_matrix(modular.get("sigma_plus_half"))
        expected_entry = None
        wrong_entry = None
        if (
            rho is not None
            and context is not None
            and len(rho) == len(context) == 2
            and rho[0][0] > 0
            and rho[1][1] > 0
        ):
            expected_entry = context[0][1] * math.sqrt(rho[1][1] / rho[0][0])
            wrong_entry = context[0][1] * math.sqrt(rho[0][0] / rho[1][1])
        orientation_ok = (
            sigma_i_half is not None
            and expected_entry is not None
            and wrong_entry is not None
            and math.isclose(
                sigma_i_half[0][1], expected_entry, rel_tol=1.0e-11, abs_tol=1.0e-11
            )
            and not math.isclose(
                sigma_i_half[0][1], wrong_entry, rel_tol=1.0e-11, abs_tol=1.0e-11
            )
            and matrices_close(
                modular.get("sigma_plus_half"), modular.get("commutant_multiplier")
            )
            and matrices_close(modular.get("lhs"), modular.get("rhs"))
            and text_has(
                modular.get("identity", ""), "J sigma_{-i/2}(C*) J"
            )
            and text_has(modular.get("general_bound", ""), "sigma_{i/2}(C)")
            and text_has(
                modular.get("identity", ""), "sigma_s=alpha_{-beta*hbar*s}"
            )
        )
        orientation_actual = {
            "sigma_i_half_01": sigma_i_half[0][1] if sigma_i_half else None,
            "expected_01": expected_entry,
            "wrong_01": wrong_entry,
            "identity": modular.get("identity"),
        }
    audit.check(
        f"{label} exact standard-form imaginary-half orientation",
        orientation_ok,
        orientation_actual,
        {
            "right_multiplier": "sigma_(i/2)(C)",
            "adjoint_identity": "J sigma_(-i/2)(C*) J",
            "opposite_orientation_rejected": True,
        },
        "cross_core",
    )

    carrier = find_group(
        derived,
        (
            "universal_zero_source_orbit_smear_carrier",
            "universal_orbit_smear_carrier",
            "orbit_smear_cstar",
            "triangular_l1_c0",
        ),
        ("orbit", "smear"),
    )
    translation_candidate = first_value(
        carrier, ("translation", "l1_translation", "c0_shift")
    )
    translation = (
        as_mapping(translation_candidate)
        if isinstance(translation_candidate, dict)
        else carrier
    )
    l1_distance = first_value(
        translation, ("exact_l1_distance", "l1_distance", "translation_l1")
    )
    l1_formula = first_value(
        translation, ("exact_l1_formula", "l1_formula", "translation_formula")
    )
    c0_flag = first_value(
        translation,
        (
            "point_norm_C0_on_completion",
            "point_norm_c0",
            "point_norm_continuous",
        ),
    )
    isometry = first_value(
        translation, ("universal_isometry", "isometric", "shift_isometric")
    )
    translation_rows = first_list(
        translation, ("translation_rows", "rows", "l1_rows")
    ) or []
    row_formula_ok = False
    if translation_rows:
        horizon = first_value(translation, ("horizon", "triangle_width", "width"))
        horizon_value = as_float(horizon)
        row_formula_ok = horizon_value is not None and all(
            isinstance(row, dict)
            and as_float(first_value(row, ("shift", "translation"))) is not None
            and close(
                first_value(
                    row,
                    ("l1_translation_distance", "exact_l1_distance", "l1_distance"),
                ),
                2 * abs(as_float(first_value(row, ("shift", "translation")))) / horizon_value
                - as_float(first_value(row, ("shift", "translation"))) ** 2
                / (2 * horizon_value * horizon_value),
            )
            for row in translation_rows
        )
    if isometry is None:
        isometry = bool(
            first_value(
                translation,
                ("orbit_smear_uniform_bound", "isometry_formula", "uniform_bound"),
            )
        )
    formula_ok = close(l1_distance, l1_formula) or row_formula_ok
    l1_ok = (
        bool(carrier)
        and bool(translation)
        and formula_ok
        and c0_flag is True
        and isometry is True
    )
    audit.check(
        f"{label} exact L1 C0 shift",
        l1_ok,
        {
            "distance": l1_distance,
            "formula": l1_formula,
            "translation_rows": len(translation_rows),
            "row_formula_ok": row_formula_ok,
            "point_norm_C0": c0_flag,
            "isometric": isometry,
        },
        "exact L1 translation formula and isometric point-norm C0 shift",
        "cross_core",
    )

    doublet = find_group(
        derived,
        (
            "exp789_rational_sine_ground_doublets",
            "ground_doublet",
            "ground_doublets",
            "rational_sine_near_ground",
        ),
        ("doublet",),
    )
    triangle = as_mapping(
        first_value(doublet, ("triangle", "triangular_kernel", "fixed_smear"))
    )
    triangle_source = triangle or (
        carrier if text_has(json.dumps(carrier, sort_keys=True), "half_moment") else {}
    )
    triangle_width = first_value(
        triangle_source,
        ("triangle_width_T", "triangle_width", "width", "T", "horizon"),
    )
    if triangle_width is None:
        inputs = as_mapping(doublet.get("inputs"))
        triangle_width = first_value(
            inputs, ("triangle_width_T", "triangle_width", "width", "T")
        )
    half_moment = first_value(
        triangle_source,
        ("half_moment", "sqrt_time_moment", "square_root_moment"),
    )
    normalization = first_value(triangle_source, ("normalization", "integral"))
    triangle_ratio = None
    if as_float(half_moment) is not None and positive(triangle_width):
        triangle_ratio = as_float(half_moment) / math.sqrt(as_float(triangle_width))  # type: ignore[arg-type]
    triangle_ok = (
        bool(doublet)
        and close(normalization, 1)
        and triangle_ratio is not None
        and math.isclose(triangle_ratio, 8 / 15, rel_tol=1.0e-11, abs_tol=1.0e-11)
    )
    audit.check(
        f"{label} triangular kernel exact 8/15 half moment",
        triangle_ok,
        {
            "normalization": normalization,
            "width": triangle_width,
            "half_moment": half_moment,
            "ratio": triangle_ratio,
        },
        {"normalization": 1, "half_moment_over_sqrt_T": "8/15"},
        "cross_core",
    )

    sine_margin = first_value(
        doublet,
        (
            "sine_margin",
            "witness_margin",
            "positive_sine_margin",
            "declared_margin_squared",
        ),
    )
    sine_lower = first_value(doublet, ("sine_lower", "sine_lower_bound"))
    separation_d = first_value(
        doublet, ("separation_d", "d", "order_gap", "declared_margin_squared")
    )
    xi = first_value(doublet, ("xi", "rational_label"))
    label_eight = isinstance(xi, (list, tuple)) and len(xi) == 8
    squared_fixture = (
        positive(first_value(doublet, ("declared_margin_squared",)))
        and as_float(first_value(doublet, ("small_frequency_left_squared",)))
        is not None
        and as_float(first_value(doublet, ("small_frequency_right_squared",)))
        is not None
        and as_float(first_value(doublet, ("small_frequency_left_squared",)))
        <= as_float(first_value(doublet, ("small_frequency_right_squared",)))
        and text_has(first_value(doublet, ("sine_remainder_inequality",)), "6")
    )
    direct_sine_fixture = (
        positive(sine_margin)
        and positive(separation_d)
        and as_float(sine_lower) is not None
        and as_float(sine_lower) >= as_float(separation_d)  # type: ignore[operator]
    )
    sine_ok = label_eight and (direct_sine_fixture or squared_fixture)
    audit.check(
        f"{label} rational sine witness positive margin",
        sine_ok,
        {
            "margin": sine_margin,
            "lower": sine_lower,
            "d": separation_d,
            "label_length": len(xi) if isinstance(xi, (list, tuple)) else None,
        },
        "positive margin above d with eight-entry rational label",
        "cross_core",
    )

    volume_rows = first_list(
        doublet,
        ("volume_rows", "smear_rows", "finite_volume_rows", "rows"),
    ) or []
    smear_values: list[Any] = []
    smear_equalities: list[bool] = []
    smear_signs: list[bool] = []
    for row in volume_rows:
        if not isinstance(row, dict):
            continue
        error = first_value(
            row,
            (
                "smear_error_formula",
                "smear_error",
                "error_bound",
                "smear_error_squared",
            ),
        )
        direct = first_value(
            row,
            (
                "smear_error_from_half_moment",
                "integrated_smear_error",
                "direct_error",
            ),
        )
        plus = first_value(row, ("plus_smeared_lower", "plus_lower"))
        minus = first_value(row, ("minus_smeared_upper", "minus_upper"))
        smear_values.append(error)
        if direct is not None:
            smear_equalities.append(close(error, direct))
        else:
            epsilon = first_value(
                row, ("energy_excess_bound", "energy_excess_upper", "epsilon")
            )
            half = first_value(doublet, ("half_moment",))
            hbar_value = first_value(doublet, ("hbar",))
            recomputed = None
            if all(as_float(item) is not None for item in (epsilon, half, hbar_value)):
                recomputed = (
                    8
                    * as_float(epsilon)
                    * as_float(half) ** 2
                    / as_float(hbar_value)
                )
            smear_equalities.append(recomputed is not None and close(error, recomputed))
        if plus is not None or minus is not None:
            smear_signs.append(positive(plus) and negative(minus))
        else:
            smear_signs.append(
                first_value(row, ("below_half_declared_margin",)) is True
            )
    smear_formula_text = first_value(
        doublet, ("smear_error_formula", "smear_bound_formula")
    )
    formula_serialized = smear_formula_text or json.dumps(doublet, sort_keys=True)
    coefficient_present = text_has(formula_serialized, "16 15") or (
        triangle_ok and all(smear_equalities)
    )
    smear_ok = (
        len(smear_values) >= 2
        and all(smear_equalities)
        and all(smear_signs)
        and decreasing(smear_values)
        and coefficient_present
        and text_has(formula_serialized, "hbar")
    )
    audit.check(
        f"{label} exact fixed-smear error and sign separation",
        smear_ok,
        {
            "errors": smear_values,
            "direct_equal": smear_equalities,
            "signs": smear_signs,
            "formula": smear_formula_text,
        },
        "16/15 formula, exact direct equality, V-decay, opposite signs",
        "cross_core",
    )

    arveson = find_group(
        derived,
        (
            "negative_arveson_near_ground",
            "negative_arveson_ground",
            "arveson_ground_criterion",
            "negative_arveson",
        ),
        ("arveson",),
    )
    arveson_inputs = as_mapping(arveson.get("inputs")) or arveson
    hbar = first_value(arveson_inputs, ("hbar",))
    nu = first_value(
        arveson_inputs, ("nu", "frequency_cutoff", "nu_inverse_time")
    )
    energy = first_value(arveson, ("energy_excess", "epsilon"))
    norm_square = first_value(
        arveson,
        (
            "operator_norm_square",
            "norm_square",
            "universal_norm_square",
            "abstract_norm_bound",
        ),
    )
    bound = first_value(
        arveson, ("bound", "near_ground_bound", "ground_expectation_bound")
    )
    frequency = first_value(
        arveson,
        ("arveson_frequency", "physical_frequency", "frequency"),
    )
    if first_value(arveson, ("abstract_norm_bound",)) is not None:
        norm_value = as_float(norm_square)
        norm_square = norm_value * norm_value if norm_value is not None else None
    if frequency is None and text_has(first_value(arveson, ("negative_support",)), "-nu"):
        frequency = -as_float(nu) if as_float(nu) is not None else None
    expected_bound = None
    if all(as_float(item) is not None for item in (energy, norm_square, hbar, nu)):
        expected_bound = (
            as_float(norm_square) * as_float(energy) / (as_float(hbar) * as_float(nu))  # type: ignore[operator]
        )
    arveson_ok = (
        bool(arveson)
        and positive(hbar)
        and positive(nu)
        and expected_bound is not None
        and close(bound, expected_bound)
        and as_float(frequency) is not None
        and close(frequency, -as_float(nu))
        and (
            text_has(json.dumps(arveson, sort_keys=True), "hbar nu")
            or close(first_value(arveson, ("hbar_nu_energy",)), as_float(hbar) * as_float(nu))
        )
    )
    audit.check(
        f"{label} negative-Arveson hbar-nu denominator and sign",
        arveson_ok,
        {
            "hbar": hbar,
            "nu": nu,
            "frequency": frequency,
            "bound": bound,
            "recomputed": expected_bound,
        },
        "frequency=-nu and bound=norm^2 epsilon/(hbar nu)",
        "cross_core",
    )

    projected_corridor = as_mapping(derived.get("projected_corridor"))
    projected_static_tail = as_mapping(projected_corridor.get("static_tail"))
    tail = projected_static_tail or find_group(
        derived,
        (
            "projected_static_tail_4x4",
            "static_tail_4x4",
            "projected_corridor_static_tail",
            "four_dimensional_static_tail",
            "static_tail_four_by_four_no_go",
        ),
        ("tail",),
    )
    tail_serialized = json.dumps(tail, sort_keys=True)
    tail_limit = first_value(
        tail,
        (
            "static_tail_limit",
            "tail_duhamel_square_limit",
            "tail_norm_square_limit",
            "tail_duhamel_square",
            "static_tail_duhamel_square",
        ),
    )
    commutator_limit = first_value(
        tail,
        (
            "commutator_limit",
            "commutator_duhamel_square_limit",
            "commutator_norm_square_limit",
            "commutator_duhamel_square",
            "evolved_commutator_duhamel_square",
        ),
    )
    orbit_limit = first_value(
        tail,
        (
            "orbit_distance_limit",
            "full_cutoff_distance_limit",
            "two_sided_distance_limit",
            "full_vs_cutoff_averaged_sharp_square_limit",
            "full_vs_cutoff_averaged_sharp_square",
        ),
    )
    q3_counterexample = first_value(
        tail,
        ("q3lock_counterexample", "is_q3lock_counterexample"),
    )
    gibbs_invariant = first_value(
        tail, ("gibbs_invariant", "state_gibbs_invariant")
    )
    tail_rows = first_list(tail, ("rows", "limit_rows", "asymptotic_rows")) or []
    if tail_limit is None and tail_rows:
        static_values = [
            first_value(row, ("static_D_squared", "static_tail_squared"))
            for row in tail_rows
            if isinstance(row, dict)
        ]
        commutator_values = [
            first_value(row, ("commutator_D_squared", "commutator_squared"))
            for row in tail_rows
            if isinstance(row, dict)
        ]
        lower_values = [
            first_value(row, ("full_H_vs_K_hash_lower", "orbit_lower"))
            for row in tail_rows
            if isinstance(row, dict)
        ]
        upper_values = [
            first_value(row, ("full_H_vs_K_hash_upper", "orbit_upper"))
            for row in tail_rows
            if isinstance(row, dict)
        ]
        static_numbers = [as_float(value) for value in static_values]
        commutator_numbers = [as_float(value) for value in commutator_values]
        tail_sequence_ok = (
            len(static_numbers) >= 3
            and all(value is not None for value in static_numbers)
            and all(
                right <= left
                for left, right in zip(static_numbers, static_numbers[1:])
            )
            and static_numbers[0] > static_numbers[-1]
            and static_numbers[-1] < 1.0e-20
        )
        commutator_sequence_ok = (
            len(commutator_numbers) >= 3
            and all(value is not None for value in commutator_numbers)
            and all(
                right >= left
                for left, right in zip(
                    commutator_numbers, commutator_numbers[1:]
                )
            )
            and str(commutator_values[0]).strip() != "2"
            and close(commutator_numbers[-1], 2.0, tolerance=1.0e-12)
        )
        full_return_values = [
            first_value(
                row,
                ("full_H_orbit_to_raw_operator_bound", "full_orbit_operator_bound"),
            )
            for row in tail_rows
            if isinstance(row, dict)
        ]
        orbit_sequence_ok = (
            len(lower_values) >= 3
            and len(upper_values) >= 3
            and len(full_return_values) >= 3
            and decreasing(full_return_values)
            and as_float(lower_values[-1]) is not None
            and as_float(upper_values[-1]) is not None
            and as_float(lower_values[-1]) > 1.98
            and as_float(upper_values[-1]) - as_float(lower_values[-1]) < 0.04
        )
        if tail_sequence_ok:
            tail_limit = 0
        if commutator_sequence_ok:
            commutator_limit = 2
        if orbit_sequence_ok:
            orbit_limit = 2
    if q3_counterexample is None and first_value(
        tail, ("q_only_static_fixture_not_Q3LOCK_counterexample",)
    ) is True:
        q3_counterexample = False
    if gibbs_invariant is None:
        gibbs_invariant = first_value(
            tail, ("rho_is_KMS_for_displayed_K_or_H",)
        )
    if gibbs_invariant is None and tail_rows:
        invariant_flags = [
            (
                first_value(row, ("state_invariant_under_H",)),
                first_value(row, ("state_invariant_under_K",)),
            )
            for row in tail_rows
            if isinstance(row, dict)
        ]
        if invariant_flags and all(pair == (False, False) for pair in invariant_flags):
            gibbs_invariant = False
    matrix_fixture = text_has(tail_serialized, "4x4") or text_has(
        tail_serialized, "four dimensional"
    ) or (
        isinstance(first_value(tail, ("identity",)), list)
        and len(first_value(tail, ("identity",))) == 4
    ) or (len(tail_rows) >= 3 and q3_counterexample is False)
    tail_ok = (
        bool(tail)
        and matrix_fixture
        and close(tail_limit, 0)
        and close(commutator_limit, 2)
        and close(orbit_limit, 2)
        and q3_counterexample is False
        and gibbs_invariant is False
    )
    audit.check(
        f"{label} exact 4x4 static-tail hostile limits",
        tail_ok,
        {
            "tail": tail_limit,
            "commutator": commutator_limit,
            "orbit": orbit_limit,
            "q3lock_counterexample": q3_counterexample,
            "gibbs_invariant": gibbs_invariant,
        },
        {"limits": [0, 2, 2], "q3lock_counterexample": False, "gibbs": False},
        "cross_core",
    )

    fixture_rows: list[dict[str, Any]] = []
    if "cutoff_orbit_00_11_block" in tail:
        fixture_rows.append(tail)
    fixture_rows.extend(
        row
        for row in tail_rows
        if isinstance(row, dict) and "cutoff_orbit_00_11_block" in row
    )
    expected_cutoff_sign = [[0, -1], [-1, 0]]
    expected_commutator_sign = [
        [0, 0, 0, 1],
        [0, 0, 0, 0],
        [0, 0, 0, 0],
        [-1, 0, 0, 0],
    ]
    sign_rows: list[dict[str, Any]] = []
    for row in fixture_rows:
        cutoff = row.get("cutoff_orbit_00_11_block")
        expected_cutoff = row.get("expected_cutoff_block")
        commutator = first_value(
            row,
            ("commutator_C", "commutator_C_over_r_squared", "normalized_commutator"),
        )
        expected_commutator = first_value(
            row, ("expected_commutator_C", "expected_normalized_commutator")
        )
        cutoff_pattern = matrix_sign_pattern(cutoff)
        commutator_pattern = matrix_sign_pattern(commutator)
        sign_rows.append(
            {
                "cutoff": cutoff_pattern,
                "commutator": commutator_pattern,
                "cutoff_matches_expected": matrices_close(cutoff, expected_cutoff),
                "commutator_matches_expected": matrices_close(
                    commutator, expected_commutator
                ),
            }
        )
    static_sign_ok = bool(sign_rows) and all(
        row["cutoff"] == expected_cutoff_sign
        and row["commutator"] == expected_commutator_sign
        and row["cutoff_matches_expected"] is True
        and row["commutator_matches_expected"] is True
        for row in sign_rows
    )
    if label == "independent":
        sign_alias = as_mapping(tail.get("commutator_C_sign_alias"))
        static_sign_ok = (
            static_sign_ok
            and close(sign_alias.get("00_11"), 1)
            and close(sign_alias.get("11_00"), -1)
        )
    audit.check(
        f"{label} exact 4x4 cutoff and commutator signs",
        static_sign_ok,
        sign_rows,
        {
            "cutoff_B_00_11": expected_cutoff_sign,
            "commutator_C_sign": expected_commutator_sign,
        },
        "cross_core",
    )

    categorical = find_group(
        derived,
        (
            "categorical_M2_boundary",
            "categorical_m2_boundary",
            "m2_categorical_boundary",
        ),
        ("categorical",),
    )
    frequencies = first_value(categorical, ("frequencies", "orbit_frequencies"))
    rank = first_value(
        categorical, ("direct_sum_basis_rank", "generated_algebra_rank")
    )
    dimension = first_value(
        categorical,
        (
            "direct_sum_dimension",
            "generated_algebra_dimension",
            "direct_sum_complex_dimension",
        ),
    )
    common_shift = first_value(
        categorical,
        (
            "common_direct_sum_shift_exists",
            "common_shift_exists",
            "common_c0_shift_categorical_only",
        ),
    )
    single_generator = first_value(
        categorical,
        ("single_labelled_M2_generator_exists", "single_labelled_generator_exists"),
    )
    quasi_local = first_value(
        categorical,
        (
            "categorical_envelope_implies_quasi_local_limit",
            "implies_quasi_local",
            "quasi_local_thermodynamic_identification",
        ),
    )
    exhaustion_unique = first_value(
        categorical,
        (
            "categorical_envelope_implies_exhaustion_uniqueness",
            "implies_exhaustion_uniqueness",
        ),
    )
    if single_generator is None and first_value(
        categorical, ("generator_difference_nonscalar",)
    ) is True:
        single_generator = False
    if exhaustion_unique is None and text_has(payload_boundary, "not an all-exhaustion"):
        exhaustion_unique = False
    if exhaustion_unique is None and derived.get("all_exhaustion_spatial_cauchy_closed") is False:
        exhaustion_unique = False
    frequency_values = (
        [as_float(item) for item in frequencies]
        if isinstance(frequencies, (list, tuple))
        else []
    )
    categorical_ok = (
        len(frequency_values) == 2
        and close(frequency_values[0], 2)
        and close(frequency_values[1], 4)
        and close(rank, 8)
        and close(dimension, 8)
        and common_shift is True
        and single_generator is False
        and quasi_local is False
        and exhaustion_unique is False
    )
    audit.check(
        f"{label} exact M2 categorical boundary",
        categorical_ok,
        {
            "frequencies": frequencies,
            "rank": rank,
            "dimension": dimension,
            "common_shift": common_shift,
            "single_generator": single_generator,
            "quasi_local": quasi_local,
            "exhaustion_unique": exhaustion_unique,
        },
        {
            "frequencies": [2, 4],
            "rank": 8,
            "common_shift": True,
            "single_generator": False,
            "quasi_local": False,
            "exhaustion_unique": False,
        },
        "cross_core",
    )

    return {
        "right_context_recursive_word_recovery": recursive_ok,
        "right_context_standard_form_orientation": (
            "sigma_(i/2)(C)" if orientation_ok else None
        ),
        "right_context_opposite_orientation_rejected": orientation_ok,
        "L1_point_norm_C0_shift": l1_ok,
        "triangular_half_moment_coefficient": "8/15" if triangle_ok else None,
        "rational_sine_margin_positive": sine_ok,
        "smear_error_coefficient": "16/15" if smear_ok else None,
        "negative_arveson_frequency_sign": -1 if arveson_ok else None,
        "negative_arveson_denominator": "hbar*nu" if arveson_ok else None,
        "static_tail_4x4_limits": [0, 2, 2] if tail_ok else None,
        "static_tail_cutoff_B_00_11": (
            expected_cutoff_sign if static_sign_ok else None
        ),
        "static_tail_commutator_C_sign": (
            expected_commutator_sign if static_sign_ok else None
        ),
        "M2_frequencies": [2, 4] if categorical_ok else None,
        "M2_direct_sum_dimension": 8 if categorical_ok else None,
        "M2_categorical_not_quasi_local": categorical_ok,
    }


def compare_exact_core(
    primary: dict[str, Any], independent: dict[str, Any], audit: Audit
) -> dict[str, Any]:
    primary_invariants = semantic_cross_invariants(primary, "primary", audit)
    independent_invariants = semantic_cross_invariants(
        independent, "independent", audit
    )
    expected = {
        "right_context_recursive_word_recovery": True,
        "right_context_standard_form_orientation": "sigma_(i/2)(C)",
        "right_context_opposite_orientation_rejected": True,
        "L1_point_norm_C0_shift": True,
        "triangular_half_moment_coefficient": "8/15",
        "rational_sine_margin_positive": True,
        "smear_error_coefficient": "16/15",
        "negative_arveson_frequency_sign": -1,
        "negative_arveson_denominator": "hbar*nu",
        "static_tail_4x4_limits": [0, 2, 2],
        "static_tail_cutoff_B_00_11": [[0, -1], [-1, 0]],
        "static_tail_commutator_C_sign": [
            [0, 0, 0, 1],
            [0, 0, 0, 0],
            [0, 0, 0, 0],
            [-1, 0, 0, 0],
        ],
        "M2_frequencies": [2, 4],
        "M2_direct_sum_dimension": 8,
        "M2_categorical_not_quasi_local": True,
    }
    audit.check(
        "primary and independent exact cross-invariants agree",
        primary_invariants == independent_invariants == expected,
        {"primary": primary_invariants, "independent": independent_invariants},
        expected,
        "cross_core",
    )
    return {
        "primary": primary_invariants,
        "independent": independent_invariants,
        "expected": expected,
        "all_exact": primary_invariants == independent_invariants == expected,
    }


def validate_manifest(manifest: dict[str, Any], audit: Audit) -> None:
    route = as_mapping(manifest.get("route_status"))
    exact = {
        "candidate": manifest.get("candidate_id")
        == "PA-CP1-ST8-Q3LOCK-UNIVERSAL-ORBIT-SMEAR-GROUND-DOUBLET-ROUTE-SPLIT-v0",
        "task": manifest.get("task_id") == TASK_ID,
        "claim": manifest.get("claim_ids") == [CLAIM_ID],
        "parents": manifest.get("parent_explorations")
        == ["EXP-000789", "EXP-000801", "EXP-000802"],
        "exploration": manifest.get("exploration_id") == EXPLORATION_ID,
        "result_id": manifest.get("result_id") == RESULT_ID,
        "result_number": manifest.get("result_number") == RESULT_NUMBER,
        "result_version": manifest.get("result_version") == RESULT_VERSION,
        "claim_bearing": manifest.get("claim_bearing") is False,
        "new_negative": tuple(manifest.get("negative_ids", ()))
        == NEW_NEGATIVE_IDS,
        "reused_negatives": tuple(manifest.get("reused_negative_ids", ()))
        == REUSED_NEGATIVE_IDS,
        "closed_gates": tuple(manifest.get("closed_subgates", ()))
        == CLOSED_GATES,
        "retained_gates": tuple(manifest.get("retained_gate_ids", ()))
        == RETAINED_GATES,
        "open_gates": tuple(manifest.get("open_gates", ())) == OPEN_GATES,
        "successor": route.get("next_gate") == SUCCESSOR_GATE,
    }
    audit.check(
        "manifest exact identity, negative and gate contract",
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
    checkpoint_contract = {
        "source": checkpoint.get("source") == note_relative,
        "pdf": checkpoint.get("pdf") == pdf_relative,
        "development_economy": text_has(
            checkpoint.get("workflow", ""), "no per-lemma or intermediate PDF"
        ),
        "one_checkpoint": text_has(
            checkpoint.get("workflow", ""), "single gate-level synthesis PDF"
        ),
        "proof_layers_first": all(
            text_has(checkpoint.get("workflow", ""), token)
            for token in ("manifest", "certificate", "three verifier layers passed")
        ),
        "seven_pages": text_has(checkpoint.get("visual_qa", ""), "seven rendered pages"),
        "visual_qa": all(
            text_has(checkpoint.get("visual_qa", ""), token)
            for token in ("zero clipping", "overlap", "broken equations", "overfull boxes")
        ),
    }
    audit.check(
        "manifest exact gate-level synthesis checkpoint contract",
        all(checkpoint_contract.values()),
        checkpoint_contract,
        "all true",
        "manifest",
    )
    require_tokens(
        json.dumps(manifest, sort_keys=True),
        "manifest positive theorem content",
        (
            "modular right-context",
            "right to left",
            "fixed finite raw configuration-orbit word",
            "L1-orbit-smear C-star",
            "point-norm C0",
            "rational",
            "8sqrt(T)/15",
            "hbar nu",
            "ground states",
            "M_2 direct-sum M_2",
            "static tail",
        ),
        audit,
        group="manifest",
        core=True,
    )
    require_tokens(
        manifest.get("no_overclaim", ""),
        "manifest no-overclaim boundary",
        (
            "selected fixed-beta phase-tangent",
            "quasi-local raw oscillator thermodynamic limit",
            "all-exhaustion",
            "spatially local algebra",
            "zero-source periodic phase mixture",
            "canonical momentum/full Weyl",
            "polynomial local generator",
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
    forbidden_positive = (
        r"(?:proves|closes)[^.]{0,100}quasi[- ]local raw oscillator thermodynamic",
        r"(?:proves|closes)[^.]{0,100}all[- ]exhaustion (?:uniqueness|cauchy)",
    )
    serialized = json.dumps(manifest, sort_keys=True)
    hits = [pattern for pattern in forbidden_positive if re.search(pattern, serialized, re.I)]
    audit.check(
        "manifest has no broadened positive conclusion",
        not hits,
        hits,
        [],
        "scope",
    )


def validate_certificate(audit: Audit) -> str:
    certificate = require_text(CERTIFICATE, audit, "certificate") or ""
    if not certificate:
        return certificate
    require_tokens(
        certificate,
        "certificate theorem, fixtures and boundary",
        (
            EXPLORATION_ID,
            RESULT_NUMBER,
            RESULT_VERSION,
            *CLOSED_GATES,
            SUCCESSOR_GATE,
            *NEW_NEGATIVE_IDS,
            "right to left",
            "right-context",
            "8 over 15",
            "16 over 15",
            "hbar nu",
            "negative-frequency operator lowers energy",
            "M_2 direct-sum M_2",
            "four-dimensional hostile fixture",
            "not a Q3LOCK counterexample",
            "categorical carrier",
            "not the missing quasi-local thermodynamic oscillator algebra",
            "broken-sector GNS gap",
            NOTE_SOURCE.relative_to(REPO).as_posix(),
            CHECKPOINT_PDF.relative_to(REPO).as_posix(),
            "single gate-level synthesis",
            "source-only form check",
            "zero overfull boxes",
            "all seven rendered pages",
            "not a new mathematical result",
        ),
        audit,
        group="scope",
        core=True,
    )
    forbidden = (
        r"the carrier (?:is|gives) the quasi[- ]local",
        r"distinct ground states (?:give|imply|prove) a positive (?:gns|mass) gap",
        r"every exhaustion converges",
    )
    hits = [pattern for pattern in forbidden if re.search(pattern, certificate, re.I)]
    audit.check(
        "certificate has no broadened positive conclusion",
        not hits,
        hits,
        [],
        "scope",
    )
    return certificate


def gate_section(text: str, gate: str) -> str | None:
    lines = text.splitlines()
    starts = [
        index
        for index, line in enumerate(lines)
        if line.startswith("###") and gate in line
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


def validate_pdf_efficiency(
    audit: Audit, manifest: dict[str, Any], certificate: str
) -> dict[str, Any]:
    note_relative = NOTE_SOURCE.relative_to(REPO).as_posix()
    pdf_relative = CHECKPOINT_PDF.relative_to(REPO).as_posix()
    expected_artifacts = {note_relative, pdf_relative}
    source_exists = NOTE_SOURCE.is_file()
    pdf_exists = CHECKPOINT_PDF.is_file()
    notes_root = REPO / "claims/C6-SPACETIME-SIGNATURE/notes"
    package_artifacts: list[str] = []
    if notes_root.is_dir():
        for path in notes_root.rglob("*"):
            if not path.is_file():
                continue
            lower = path.name.lower()
            if not lower.endswith((".pdf", ".tex.txt")):
                continue
            normalized = re.sub(r"[^a-z0-9]+", "-", lower)
            if all(
                token in normalized
                for token in ("universal", "orbit", "smear", "ground", "doublet")
            ):
                package_artifacts.append(path.relative_to(REPO).as_posix())
    pair_reporter = audit.pending if not (source_exists and pdf_exists) else audit.check
    pair_reporter(
        "exactly one EXP-000803 checkpoint source/PDF pair exists",
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
    source_reporter = audit.pending if not source_exists else audit.check
    source_reporter(
        "checkpoint source readable UTF-8",
        source_error is None and len(source_text) > 12000,
        {"error": source_error, "characters": len(source_text)},
        "readable UTF-8 source with >12000 characters",
        "pdf_checkpoint",
    )
    source_tokens = (
        "Q3LOCK Universal Orbit-Smear Carrier and Ground-Doublet Route Split",
        EXPLORATION_ID,
        RESULT_NUMBER,
        RESULT_VERSION,
        RESULT_ID,
        *CLOSED_GATES,
        SUCCESSOR_GATE,
        *ALL_NEGATIVE_IDS,
        "modular right-context",
        "right-to-left Fejer",
        "fixed finite raw configuration-orbit word",
        "universal L1 orbit-smear C-star carrier",
        "two distinct weak-star cluster states",
        "negative-Arveson",
        "categorical and nonlocal",
        "not a quasi-local thermodynamic limit",
        "No all-exhaustion Cauchy",
        "broken-sector GNS gap",
        "physical mass gap",
        "continuum",
        "physical empty-space",
        "C6",
        "CP1",
        "Sector A",
        "Pre-A closure is claimed",
        "not a Q3LOCK counterexample",
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
    source_placeholders = [
        token for token in ("TODO", "TBD", "FIXME", "PLACEHOLDER") if re.search(
            rf"\b{token}\b", source_text, re.I
        )
    ]
    source_reporter(
        "checkpoint source has no drafting placeholders",
        source_exists and not source_placeholders,
        source_placeholders,
        [],
        "pdf_checkpoint",
    )

    pdf_error: str | None = None
    pdf_pages = 0
    pypdf_texts: list[str] = []
    pdfplumber_texts: list[str] = []
    encrypted = True
    form_fields = True
    try:
        reader = PdfReader(str(CHECKPOINT_PDF), strict=True)
        encrypted = reader.is_encrypted
        form_fields = bool(reader.get_fields())
        pdf_pages = len(reader.pages)
        pypdf_texts = [page.extract_text() or "" for page in reader.pages]
        with pdfplumber.open(CHECKPOINT_PDF) as document:
            pdfplumber_texts = [page.extract_text() or "" for page in document.pages]
    except Exception as error:  # PDF parsers expose several library-specific errors.
        pdf_error = f"{type(error).__name__}: {error}"
    pdf_text = "\n".join(pypdf_texts)
    plumber_text = "\n".join(pdfplumber_texts)
    pdf_reporter = audit.pending if not pdf_exists else audit.check
    pdf_reporter(
        "checkpoint PDF readable by two independent parsers",
        pdf_error is None
        and pdf_pages == len(pdfplumber_texts) == 7
        and all(len(text.strip()) > 300 for text in pypdf_texts)
        and all(len(text.strip()) > 300 for text in pdfplumber_texts),
        {
            "error": pdf_error,
            "pypdf_pages": pdf_pages,
            "pdfplumber_pages": len(pdfplumber_texts),
            "pypdf_page_characters": [len(text) for text in pypdf_texts],
            "pdfplumber_page_characters": [len(text) for text in pdfplumber_texts],
        },
        "7 nonempty pages in pypdf and pdfplumber",
        "pdf_checkpoint",
    )
    pdf_reporter(
        "checkpoint PDF is static, unencrypted, and form-free",
        pdf_error is None and encrypted is False and form_fields is False,
        {"encrypted": encrypted, "form_fields": form_fields},
        {"encrypted": False, "form_fields": False},
        "pdf_checkpoint",
    )
    pdf_tokens = (
        "Q3LOCK Universal Orbit-Smear Carrier and Ground-Doublet Route Split",
        EXPLORATION_ID,
        RESULT_NUMBER,
        RESULT_VERSION,
        RESULT_ID,
        *CLOSED_GATES,
        SUCCESSOR_GATE,
        *ALL_NEGATIVE_IDS,
        "modular right-context",
        "right-to-left Fejer",
        "fixed finite raw configuration-orbit word",
        "universal L1 orbit-smear C-star carrier",
        "two distinct weak-star cluster states",
        "negative-Arveson",
        "categorical and nonlocal",
        "not a quasi-local thermodynamic limit",
        "No all-exhaustion Cauchy",
        "broken-sector GNS gap",
        "physical mass gap",
        "continuum",
        "physical empty-space",
        "C6",
        "CP1",
        "Sector A",
        "Pre-A closure is claimed",
        "not a Q3LOCK counterexample",
    )
    if pdf_exists:
        require_tokens(
            pdf_text,
            "checkpoint PDF theorem and no-overclaim text",
            pdf_tokens,
            audit,
            group="pdf_checkpoint",
            core=True,
        )
        require_tokens(
            plumber_text,
            "checkpoint PDF second-extractor provenance and boundary",
            (
                EXPLORATION_ID,
                RESULT_NUMBER,
                RESULT_VERSION,
                *CLOSED_GATES,
                SUCCESSOR_GATE,
                *ALL_NEGATIVE_IDS,
                "not a quasi-local thermodynamic limit",
                "broken-sector GNS gap",
                "physical mass gap",
                "Pre-A closure is claimed",
            ),
            audit,
            group="pdf_checkpoint",
            core=True,
        )
    else:
        audit.pending(
            "checkpoint PDF theorem and no-overclaim text required tokens",
            False,
            "PDF unavailable",
            "all required tokens present",
            "pdf_checkpoint",
        )
        audit.pending(
            "checkpoint PDF second-extractor provenance and boundary required tokens",
            False,
            "PDF unavailable",
            "all required tokens present",
            "pdf_checkpoint",
        )

    source_stat = NOTE_SOURCE.stat() if NOTE_SOURCE.is_file() else None
    pdf_stat = CHECKPOINT_PDF.stat() if CHECKPOINT_PDF.is_file() else None
    header = CHECKPOINT_PDF.read_bytes()[:8] if CHECKPOINT_PDF.is_file() else b""
    trailer = CHECKPOINT_PDF.read_bytes()[-32:] if CHECKPOINT_PDF.is_file() else b""
    freshness = (
        source_stat is not None
        and pdf_stat is not None
        and pdf_stat.st_mtime_ns >= source_stat.st_mtime_ns
        and pdf_stat.st_size > source_stat.st_size > 0
        and header.startswith(b"%PDF-")
        and b"%%EOF" in trailer
    )
    freshness_reporter = (
        audit.pending if not (source_exists and pdf_exists) else audit.check
    )
    freshness_reporter(
        "checkpoint PDF is readable and fresh relative to source",
        freshness,
        {
            "source_mtime_ns": source_stat.st_mtime_ns if source_stat else None,
            "pdf_mtime_ns": pdf_stat.st_mtime_ns if pdf_stat else None,
            "source_size": source_stat.st_size if source_stat else None,
            "pdf_size": pdf_stat.st_size if pdf_stat else None,
            "header": header.decode("latin-1", errors="replace"),
            "has_eof": b"%%EOF" in trailer,
        },
        "PDF mtime >= source, nonempty, %PDF header, %%EOF trailer",
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
                changed_artifacts.append(path_text)
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
    authority_reporter = audit.pending if not (manifest and certificate) else audit.check
    authority_reporter(
        "manifest and certificate cite the exact checkpoint pair only",
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
        "source_sha256": portable_sha256(NOTE_SOURCE) if NOTE_SOURCE.is_file() else None,
        "pdf_sha256": portable_sha256(CHECKPOINT_PDF) if CHECKPOINT_PDF.is_file() else None,
        "page_count": pdf_pages,
        "pypdf_text_characters": len(pdf_text),
        "pdfplumber_text_characters": len(plumber_text),
        "pdf_imported": pdf_error is None,
        "pdf_built_by_integrated_verifier": False,
        "render_attempted": False,
    }


def validate_formal(manifest: dict[str, Any], audit: Audit) -> dict[str, Any]:
    required_paths = (MANIFEST, CERTIFICATE, PRIMARY, INDEPENDENT, SCRIPT)
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
        evidence = record.get("evidence_refs", [])
        conditions = {
            "task": record.get("task_id") == TASK_ID,
            "verdict": record.get("verdict") == "advanced",
            "claim": record.get("claim_ids") == [CLAIM_ID],
            "result": refs.get("results") == [RESULT_NUMBER],
            "negatives": set(refs.get("negatives", ())) == set(ALL_NEGATIVE_IDS),
            "closed_gates": all(gate in gates for gate in CLOSED_GATES),
            "successor_gate": SUCCESSOR_GATE in gates,
            "paths": all(path.relative_to(REPO).as_posix() in serialized for path in required_paths),
            "no_note_pdf": isinstance(evidence, list)
            and not any(str(item).lower().endswith((".pdf", ".tex.txt")) for item in evidence),
        }
        audit.pending(
            f"{EXPLORATION_ID} complete authority chain",
            all(conditions.values()),
            conditions,
            "all true",
            "formal",
        )
        require_tokens(
            record.get("boundary", ""),
            f"{EXPLORATION_ID} exact narrow boundary",
            (
                "selected-tangent finite-word",
                "categorical zero-source orbit-smear",
                "quasi-local raw oscillator",
                "all-exhaustion",
                "momentum",
                "broken-sector GNS or physical mass gap",
                "continuum",
                "Pre-A",
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
                "R-167 v1.6 ledger",
                (
                    RESULT_ID,
                    RESULT_VERSION,
                    EXPLORATION_ID,
                    *CLOSED_GATES,
                    SUCCESSOR_GATE,
                    *NEW_NEGATIVE_IDS,
                    "right-context",
                    "L1-orbit-smear",
                    "distinct",
                    "ground",
                    "categorical rather than quasi-local",
                    "GNS gap",
                    NOTE_SOURCE.relative_to(REPO).as_posix(),
                    CHECKPOINT_PDF.relative_to(REPO).as_posix(),
                    "single gate-level synthesis authority",
                    "No per-lemma or intermediate PDF",
                ),
                audit,
            )

    registry = require_text(
        REPO / "negative-results/registry.md", audit, "negative registry"
    )
    if registry is not None:
        for negative_id in ALL_NEGATIVE_IDS:
            audit.pending(
                f"negative authority {negative_id}",
                registry.count(negative_id) >= 2,
                registry.count(negative_id),
                ">=2",
                "formal",
            )

    gates_text = require_text(REPO / "claims/GATES.md", audit, "gate authority")
    if gates_text is not None:
        for gate in CLOSED_GATES:
            section = gate_section(gates_text, gate)
            audit.pending(
                f"closed gate authority {gate}",
                section is not None
                and re.search(r"\*\*Status:\*\*\s*CLOSED", section, re.I) is not None,
                section,
                "exact gate heading with CLOSED status",
                "formal",
            )
        for gate in OPEN_GATES:
            section = gate_section(gates_text, gate)
            linked = gate == ROUND1_GATE or (
                section is not None
                and (
                    text_has(section, EXPLORATION_ID)
                    or (
                        text_has(section, RESULT_NUMBER)
                        and text_has(section, RESULT_VERSION)
                    )
                )
            )
            audit.pending(
                f"open gate authority {gate}",
                section is not None
                and re.search(r"\*\*Status:\*\*\s*OPEN", section, re.I) is not None
                and linked,
                section,
                "OPEN; successor linked to EXP-000803",
                "formal",
            )
        for gate in RETAINED_GATES:
            section = gate_section(gates_text, gate)
            audit.pending(
                f"retained gate remains open {gate}",
                section is not None
                and re.search(r"\*\*Status:\*\*\s*OPEN", section, re.I) is not None,
                section,
                "OPEN",
                "formal",
            )

    todo = load_json(REPO / "todo/todo.json", audit, "TODO authority", formal=True)
    if todo is not None:
        tasks = todo.get("tasks", [])
        found = (
            [
                item
                for item in tasks
                if isinstance(item, dict) and item.get("id") == TASK_ID
            ]
            if isinstance(tasks, list)
            else []
        )
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
            require_tokens(
                serialized,
                "T-054 v1.6 linkage",
                (
                    EXPLORATION_ID,
                    RESULT_NUMBER,
                    RESULT_VERSION,
                    "modular right-context",
                    "fixed finite raw configuration-orbit word",
                    "zero-source finite Hamiltonians",
                    "universal L1 orbit-smear",
                    "distinct algebraic ground states",
                    "categorical",
                    SUCCESSOR_GATE,
                ),
                audit,
            )

    roadmap = require_text(REPO / "ROADMAP.md", audit, "roadmap")
    if roadmap is not None:
        require_tokens(
            roadmap,
            "roadmap v1.6 linkage",
            (
                TASK_ID,
                EXPLORATION_ID,
                RESULT_NUMBER,
                RESULT_VERSION,
                "modular right-context",
                "fixed finite raw configuration-orbit word",
                "zero-source finite periodic Hamiltonian",
                "universal L1 orbit-smear",
                "two distinct weak-star cluster states",
                "both are ground states",
                "categorical",
                SUCCESSOR_GATE,
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
        require_tokens(
            json.dumps(theorem_map, sort_keys=True),
            "theorem map v1.6 linkage",
            (EXPLORATION_ID, RESULT_NUMBER, RESULT_VERSION, *CLOSED_GATES, SUCCESSOR_GATE),
            audit,
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
        if set(event.get("neg_results", ())) == set(ALL_NEGATIVE_IDS)
        and isinstance(event.get("scripts"), list)
        and required_scripts.issubset(set(event.get("scripts", ())))
        and event.get("notes", []) == []
    ]
    audit.pending(
        "EXP-000803 theorem changelog unique",
        len(theorem_events) == 1,
        len(theorem_events),
        1,
        "formal",
    )
    if len(theorem_events) == 1:
        event = theorem_events[0]
        notes = event.get("notes", [])
        scripts = event.get("scripts", [])
        serialized = json.dumps(event, sort_keys=True)
        conditions = {
            "claim_refs": set(event.get("claim_ids", ()))
            == {CLAIM_ID, EXPLORATION_ID, RESULT_NUMBER},
            "negatives": set(event.get("neg_results", ())) == set(ALL_NEGATIVE_IDS),
            "scripts": required_scripts.issubset(set(scripts))
            if isinstance(scripts, list)
            else False,
            "notes_deferred": notes == [],
            "no_note_pdf_path": ".tex.txt" not in serialized.lower()
            and not re.search(r"claims/[A-Za-z0-9_./-]+\.pdf", serialized, re.I),
            "scope": all(
                text_has(event.get("raw", ""), token)
                for token in (
                    "fixed finite raw",
                    "L1-orbit-smear",
                    "ground",
                    "categorical",
                    "not quasi-local",
                    "GNS gap",
                    "no intermediate note/PDF",
                )
            ),
        }
        audit.pending(
            "EXP-000803 changelog complete",
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
        "R-167 v1.6 checkpoint-PDF changelog unique",
        len(checkpoint_events) == 1,
        len(checkpoint_events),
        1,
        "formal",
    )
    if len(checkpoint_events) == 1:
        checkpoint_event = checkpoint_events[0]
        checkpoint_serialized = json.dumps(checkpoint_event, sort_keys=True)
        checkpoint_raw = checkpoint_event.get("raw", "")
        checkpoint_notes = checkpoint_event.get("notes", [])
        checkpoint_claims = set(checkpoint_event.get("claim_ids", ()))
        checkpoint_conditions = {
            "claim_refs": {CLAIM_ID, RESULT_NUMBER}.issubset(checkpoint_claims),
            "source_structured": isinstance(checkpoint_notes, list)
            and note_relative in checkpoint_notes,
            "exact_source": note_relative in checkpoint_serialized,
            "exact_pdf": pdf_relative in checkpoint_serialized,
            "one_checkpoint": text_has(checkpoint_raw, "one gate-level synthesis"),
            "development_economy": text_has(
                checkpoint_raw, "no per-lemma or intermediate PDF"
            ),
            "proof_layers_first": all(
                text_has(checkpoint_raw, token)
                for token in (
                    "manifest",
                    "certificate",
                    "primary",
                    "independent",
                    "integrated proof layers passed",
                )
            ),
            "seven_page_pdf": text_has(checkpoint_raw, "seven-page PDF"),
            "zero_overfull": text_has(checkpoint_raw, "zero overfull boxes"),
            "visual_review": text_has(
                checkpoint_raw, "complete rendered-page visual review"
            ),
            "no_formal_change": all(
                text_has(checkpoint_raw, token)
                for token in (
                    "No result number",
                    "gate status",
                    "tier",
                    "no-overclaim boundary changes",
                )
            ),
        }
        audit.pending(
            "R-167 v1.6 checkpoint-PDF changelog complete",
            all(checkpoint_conditions.values()),
            checkpoint_conditions,
            "all true",
            "formal",
        )

    proof_map = require_text(
        REPO / "theory/proof-evidence-map.md", audit, "proof-evidence map"
    )
    if proof_map is not None:
        require_tokens(
            proof_map,
            "proof-evidence map v1.6 linkage",
            (EXPLORATION_ID, RESULT_NUMBER, RESULT_VERSION, *CLOSED_GATES, SUCCESSOR_GATE, *ALL_NEGATIVE_IDS),
            audit,
        )
    proof_map_json = load_json(
        REPO / "verification/proof-evidence-map.json",
        audit,
        "proof-evidence JSON map",
        formal=True,
    )
    if proof_map_json is not None:
        require_tokens(
            json.dumps(proof_map_json, sort_keys=True),
            "proof-evidence JSON v1.6 linkage",
            (EXPLORATION_ID, RESULT_NUMBER, RESULT_VERSION, *CLOSED_GATES, SUCCESSOR_GATE, *ALL_NEGATIVE_IDS),
            audit,
        )

    status = load_json(
        REPO / "claims/C6-SPACETIME-SIGNATURE/status.json", audit, "C6 status"
    )
    if status is not None:
        audit.check(
            "C6 tier unchanged",
            status.get("tier") == "T1",
            status.get("tier"),
            "T1",
            "claim_firewall",
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
        "formal_authorities_complete": not audit.missing,
    }


def build_payload(staged: bool) -> dict[str, Any]:
    audit = Audit(staged)
    manifest = load_json(MANIFEST, audit, "manifest") or {}
    if manifest:
        validate_manifest(manifest, audit)
    certificate = validate_certificate(audit)
    validate_independence(audit)

    components: dict[str, dict[str, Any]] = {}
    sentinels: dict[str, str] = {}
    with tempfile.TemporaryDirectory(prefix="tect-exp803-integrated-") as directory:
        temporary = Path(directory)
        for label, script in (("primary", PRIMARY), ("independent", INDEPENDENT)):
            result = run_fresh_pair(script, temporary, audit, label)
            if result is not None:
                components[label], sentinels[label] = result

    for label, stored_path in (
        ("primary", PRIMARY_STORED),
        ("independent", INDEPENDENT_STORED),
    ):
        stored_against_fresh(stored_path, components.get(label), audit, label)

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
        audit.require(
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
        "schema": f"tect/{SLUG}-integrated-result/1.0",
        "script_version": __version__,
        "result_id": RESULT_ID,
        "result_number": RESULT_NUMBER,
        "result_version": RESULT_VERSION,
        "exploration_id": EXPLORATION_ID,
        "task_id": TASK_ID,
        "claim_ids": [CLAIM_ID],
        "claim_bearing": False,
        "negative_ids": list(NEW_NEGATIVE_IDS),
        "reused_negative_ids": list(REUSED_NEGATIVE_IDS),
        "closed_gates": list(CLOSED_GATES),
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
            "selected_tangent_fixed_finite_raw_orbit_word_moments": True,
            "selected_tangent_raw_word_pointed_finite_core_fell_gns": True,
            "zero_source_finite_hamiltonian_L1_orbit_smear_cstar": True,
            "beta_and_state_independent_universal_shift": True,
            "two_distinct_algebraic_ground_states_on_smear_carrier": True,
            "all_exhaustion_thermodynamic_limit": False,
            "quasi_local_raw_oscillator_algebra": False,
            "raw_character_generator_core": False,
            "polynomial_local_derivation_identified": False,
            "finite_volume_to_OS_quotient_identified": False,
            "broken_sector_GNS_gap": False,
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
        help="exit zero with explicit MISSING rows while authorities assemble",
    )
    arguments = parser.parse_args()
    payload = build_payload(arguments.staged)
    atomic_json(arguments.output, payload)
    summary = payload["summary"]
    print(
        f"{EXPLORATION_ID}/{RESULT_NUMBER}-{RESULT_VERSION} INTEGRATED "
        f"{payload['verdict']} {summary['passed']}/{summary['total']} "
        f"failed={summary['failed']} missing={summary['missing']}"
    )
    print(arguments.output)
    if payload["verdict"] == "FAIL":
        return 1
    if payload["verdict"] != "PASS" and not arguments.staged:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

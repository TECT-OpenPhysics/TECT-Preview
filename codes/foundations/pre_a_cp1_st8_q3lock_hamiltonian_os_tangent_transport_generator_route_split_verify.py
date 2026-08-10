#!/usr/bin/env python3
"""Integrated verifier for EXP-000801 / R-167 v1.5.

The primary and independent implementations are loaded only in isolated child
processes.  Each is derived twice in a fresh temporary directory, canonical
payloads are compared for determinism, and the fresh payloads are compared
with the stored run JSONs.  The verifier then reconciles exact theorem
invariants and audits the formal repository authority chain.

The --staged mode is assembly-safe.  Missing or not-yet-synchronised formal
authorities produce explicit MISSING rows and an INCOMPLETE verdict while
mathematical contradictions remain FAIL.  Strict mode succeeds only at PASS.
No PDF builder, renderer, parser, or note-source generator is invoked.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import re
import subprocess
import sys
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = (
    "pre-a-cp1-st8-q3lock-hamiltonian-os-tangent-transport-"
    "generator-route-split"
)
RESULT_ID = (
    "PA-CP1-ST8-Q3LOCK-SECOND-WEIGHTED-ENERGY-MOMENT-AND-"
    "COMMON-ALPHA-CAUCHY-GATE-SPLIT"
)
RESULT_NUMBER = "R-167"
RESULT_VERSION = "v1.5"
EXPLORATION_ID = "EXP-000801"
CORRECTION_ID = "EXP-000802"
TASK_ID = "T-054"
CLAIM_ID = "C6-SPACETIME-SIGNATURE"

CLOSED_GATE = (
    "PA-CP1-ST8-Q3LOCK-FIXED-BETA-TANGENT-NET-BANDLIMITED-"
    "HAMILTONIAN-OS-POINTED-GNS-IDENTIFICATION"
)
SUCCESSOR_GATE = (
    "PA-CP1-ST8-Q3LOCK-ALL-EXHAUSTION-MIXTURE-L2-LOCALITY-"
    "AND-BETA-INDEPENDENT-CSTAR-DYNAMICS"
)
RETAINED_GATES = (
    "PA-CP1-ST8-Q3LOCK-HAMILTONIAN-THERMODYNAMIC-"
    "IDENTIFICATION-IN-CANONICAL-OS-MIXTURE",
    "PA-CP1-ST8-Q3LOCK-PROJECTED-DUHAMEL-MODULAR-C1-"
    "MULTIPLIER-LOCALITY",
)

NEGATIVE_IDS = (
    "NG-2026-08-10-PRE-A-ST8-Q3LOCK-POINTWISE-OS-GRAM-"
    "NAIVE-LABEL-EMBEDDING",
    "NG-2026-08-10-PRE-A-ST8-Q3LOCK-CONFIGURATION-CYLINDER-"
    "CANONICAL-MOMENTUM-GENERATOR",
    "NG-2026-08-10-PRE-A-ST8-Q3LOCK-RAW-CONFIGURATION-"
    "CHARACTER-BOUNDED-GENERATOR-CORE",
    "NG-2026-08-10-PRE-A-ST8-Q3LOCK-ASYMMETRIC-MIXTURE-"
    "ZERO-SOURCE-PERIODIC-LIMIT",
    "NG-2026-08-10-PRE-A-ST8-Q3LOCK-FIXED-BETA-ENVELOPE-"
    "AUTOMATIC-CROSS-BETA-GLUING",
)

PRIMARY = REPO / f"codes/foundations/{SLUG.replace('-', '_')}.py"
INDEPENDENT = REPO / f"codes/foundations/{SLUG.replace('-', '_')}_independent.py"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate.md"
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
MINIMUM_PRIMARY_ASSERTIONS = 100
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
    text = str(value).lower().replace("\\", "")
    return re.sub(r"[^a-z0-9]+", "", text)


def text_has(text: Any, token: Any) -> bool:
    return compact_text(token) in compact_text(text)


class Audit:
    """Accumulate all defects while preserving staged MISSING state."""

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
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        audit.pending(f"{label} UTF-8", False, error, "readable UTF-8", "formal")
        return None
    audit.pending(f"{label} readable", bool(text), len(text), ">0", "formal")
    return text


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
    script: Path,
    run_directory: Path,
    audit: Audit,
    label: str,
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
        timeout=360,
    )
    if completed.returncode != 0 or not output.is_file():
        audit.check(
            f"{label} execution",
            False,
            {
                "returncode": completed.returncode,
                "stdout": completed.stdout[-1600:],
                "stderr": completed.stderr[-1600:],
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


def assertion_summary(payload: dict[str, Any]) -> tuple[Any, Any, Any]:
    assertions = payload.get("assertions")
    if isinstance(assertions, dict):
        return assertions.get("passed"), assertions.get("failed"), assertions.get("total")
    summary = payload.get("summary")
    if isinstance(summary, dict):
        return summary.get("passed"), summary.get("failed"), summary.get("total")
    return None, None, None


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
    passed, failed, total = assertion_summary(payload)
    audit.check(
        f"{label} all mathematical assertions PASS",
        isinstance(total, int)
        and total >= minimum
        and passed == total
        and failed == 0,
        {"passed": passed, "failed": failed, "total": total},
        f"passed=total>={minimum}, failed=0",
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
        f"{label} rows all PASS",
        bool(rows) and all(row.get("status") == "PASS" for row in rows),
        sum(row.get("status") == "PASS" for row in rows),
        total,
        "components",
    )
    audit.check(
        f"{label} exact negative set",
        tuple(payload.get("negative_ids", [])) == NEGATIVE_IDS,
        payload.get("negative_ids"),
        list(NEGATIVE_IDS),
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
    audit.check(
        "independent does not name primary module or stored result",
        PRIMARY.stem not in independent_source
        and PRIMARY_STORED.relative_to(REPO).as_posix() not in independent_source.replace("\\", "/"),
        {
            "module_named": PRIMARY.stem in independent_source,
            "result_named": PRIMARY_STORED.relative_to(REPO).as_posix()
            in independent_source.replace("\\", "/"),
        },
        {"module_named": False, "result_named": False},
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
        not any(PRIMARY.stem in name or INDEPENDENT.stem in name for name in integrated_imports),
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


def as_fraction(value: Any) -> Fraction | None:
    if isinstance(value, bool) or value is None:
        return None
    if isinstance(value, Fraction):
        return value
    if isinstance(value, int):
        return Fraction(value)
    if isinstance(value, float):
        return Fraction(str(value))
    if isinstance(value, str):
        try:
            return Fraction(value.strip())
        except (ValueError, ZeroDivisionError):
            return None
    return None


def fraction_list(value: Any) -> list[Fraction] | None:
    if not isinstance(value, (list, tuple)):
        return None
    parsed = [as_fraction(item) for item in value]
    return None if any(item is None for item in parsed) else [item for item in parsed if item is not None]


def all_zero(value: Any) -> bool:
    if isinstance(value, bool) or value is None:
        return False
    scalar = as_fraction(value)
    if scalar is not None:
        return scalar == 0
    if isinstance(value, (list, tuple)):
        return bool(value) and all(all_zero(item) for item in value)
    if isinstance(value, dict):
        return bool(value) and all(all_zero(item) for item in value.values())
    if isinstance(value, str) and "matrix" in value.lower():
        numbers = re.findall(r"(?<![A-Za-z_])[-+]?\d+(?:/\d+)?", value)
        return bool(numbers) and all(Fraction(number) == 0 for number in numbers)
    return False


def strictly_decreasing(values: Sequence[Any]) -> bool:
    fractions = [as_fraction(value) for value in values]
    return bool(fractions) and all(item is not None for item in fractions) and all(
        fractions[index + 1] < fractions[index]
        for index in range(len(fractions) - 1)
    )


def compare_exact_core(
    primary: dict[str, Any], independent: dict[str, Any], audit: Audit
) -> dict[str, Any]:
    pderived = as_mapping(primary.get("derived"))
    iderived = as_mapping(independent.get("derived"))
    pchar = as_mapping(pderived.get("character_dirichlet_filter"))
    ichar = as_mapping(iderived.get("character_dirichlet_fejer"))
    pin = as_mapping(pchar.get("inputs"))
    pxi = fraction_list(pin.get("xi"))
    ixi = fraction_list(ichar.get("xi"))
    p_beta, p_hbar, p_chi, p_radius = (
        as_fraction(pin.get("beta")),
        as_fraction(pin.get("hbar")),
        as_fraction(pin.get("chi")),
        as_fraction(pin.get("physical_bandwidth")),
    )
    i_beta, i_hbar, i_chi, i_radius = (
        as_fraction(ichar.get("beta")),
        as_fraction(ichar.get("hbar")),
        as_fraction(ichar.get("chi")),
        as_fraction(ichar.get("radius")),
    )
    p_norm = sum((entry * entry for entry in pxi), Fraction(0)) if pxi else None
    i_norm = sum((entry * entry for entry in ixi), Fraction(0)) if ixi else None
    p_kubo = as_fraction(pchar.get("kubo_delta_square"))
    i_kubo = as_fraction(ichar.get("kubo_norm_squared"))
    p_fejer = as_mapping(pchar.get("fejer"))
    p_unaveraged = as_fraction(p_fejer.get("unaveraged_two_sided_square_bound"))
    i_unaveraged = as_fraction(ichar.get("fejer_unaveraged_squared"))
    i_fejer_duhamel = as_fraction(ichar.get("fejer_duhamel_bound"))
    i_fejer_derivative = as_fraction(ichar.get("fejer_derivative_bound"))

    p_character_ok = all(
        item is not None
        for item in (p_norm, p_beta, p_hbar, p_chi, p_radius, p_kubo, p_unaveraged)
    ) and (
        as_fraction(pchar.get("xi_norm_sq")) == p_norm
        and as_fraction(pchar.get("double_commutator"))
        == p_hbar * p_hbar * p_norm / p_chi
        and p_kubo == p_norm / (p_beta * p_chi)
        and p_unaveraged
        == p_kubo * (Fraction(2) / (p_radius * p_radius) + p_beta * p_hbar / p_radius)
    )
    i_character_ok = all(
        item is not None
        for item in (
            i_norm,
            i_beta,
            i_hbar,
            i_chi,
            i_radius,
            i_kubo,
            i_unaveraged,
            i_fejer_duhamel,
            i_fejer_derivative,
        )
    ) and (
        as_fraction(ichar.get("xi_norm_squared")) == i_norm
        and as_fraction(ichar.get("double_commutator"))
        == i_hbar * i_hbar * i_norm / i_chi
        and i_kubo == i_norm / (i_beta * i_chi)
        and i_fejer_duhamel * i_fejer_duhamel
        == i_kubo / (i_radius * i_radius)
        and i_fejer_derivative * i_fejer_derivative == i_kubo
        and i_unaveraged
        == i_kubo * (Fraction(2) / (i_radius * i_radius) + i_beta * i_hbar / i_radius)
    )
    audit.check(
        "exact character, Kubo and Fejer constants cross",
        bool(p_character_ok and i_character_ok),
        {"primary": p_character_ok, "independent": i_character_ok},
        {"primary": True, "independent": True},
        "cross_core",
    )

    pspan = as_mapping(pderived.get("finite_span"))
    pspan_gradient = as_fraction(pspan.get("ell_gradient"))
    pspan_square = as_fraction(pspan.get("delta_bound_square"))
    ispan_coefficients = fraction_list(ichar.get("span_coefficients"))
    ispan_norms = fraction_list(ichar.get("span_label_norms"))
    ispan_bound = as_fraction(ichar.get("span_derivative_bound"))
    independent_span_expected = None
    if ispan_coefficients and ispan_norms and i_beta and i_chi and ispan_bound:
        numerator = sum(
            (abs(coefficient) * norm for coefficient, norm in zip(ispan_coefficients, ispan_norms)),
            Fraction(0),
        )
        expected_square = numerator * numerator / (i_beta * i_chi)
        independent_span_expected = ispan_bound * ispan_bound == expected_square
    span_ok = (
        pspan_gradient is not None
        and pspan_square is not None
        and p_beta is not None
        and p_chi is not None
        and pspan_square == pspan_gradient * pspan_gradient / (p_beta * p_chi)
        and pspan.get("sharp_at_zero") is True
        and independent_span_expected is True
    )
    audit.check(
        "finite-span Duhamel bounds cross",
        span_ok,
        {"primary": pspan_square, "independent": ichar.get("span_derivative_bound")},
        "exact coefficient-weighted character bound",
        "cross_core",
    )

    pgram = as_mapping(pderived.get("gram_polar_transport"))
    igram = as_mapping(iderived.get("finite_block_transport"))
    pfixtures = [row for row in pgram.get("fixtures", []) if isinstance(row, dict)]
    ifixtures = [row for row in igram.get("transport_rows", []) if isinstance(row, dict)]
    p_distances = [row.get("transport_distance_sq") for row in pfixtures]
    i_distances = [row.get("distance_to_identity") for row in ifixtures]
    psingular = as_mapping(pgram.get("singular_support"))
    gram_ok = (
        bool(pfixtures)
        and bool(ifixtures)
        and all(all_zero(row.get("congruence_residual")) for row in pfixtures)
        and all(all_zero(row.get("isometry_residual")) for row in ifixtures)
        and strictly_decreasing(p_distances)
        and strictly_decreasing(i_distances)
        and list(psingular.get("retained_indices", [])) == [0, 2]
        and list(psingular.get("discarded_indices", [])) == [1]
        and list(igram.get("retained_indices", [])) == [0, 2]
        and list(igram.get("discarded_indices", [])) == [1]
        and igram.get("full_inverse_permitted") is False
    )
    audit.check(
        "exact positive-root congruence and singular-pivot cross",
        gram_ok,
        {
            "primary_distances": p_distances,
            "independent_distances": i_distances,
            "primary_retained": psingular.get("retained_indices"),
            "independent_retained": igram.get("retained_indices"),
        },
        "zero residuals, decreasing distance, retained [0,2], no full inverse",
        "cross_core",
    )

    pembedding = as_mapping(pderived.get("embedding_no_gos"))
    iembedding = as_mapping(iderived.get("embedding_counterexamples"))
    pgauge_raw = as_mapping(pderived.get("momentum_gauge_and_raw_character"))
    pgauge = as_mapping(pgauge_raw.get("momentum_gauge"))
    praw = as_mapping(pgauge_raw.get("raw_character"))
    igauge = as_mapping(iderived.get("momentum_gauge"))
    iraw = as_mapping(iderived.get("raw_character_scope"))
    negatives_ok = (
        as_mapping(pembedding.get("rotating_null")).get("naive_label_map_well_defined") is False
        and as_mapping(pembedding.get("dimension_collapse")).get("injective_isometry_possible") is False
        and iembedding.get("null_inclusion_fails") is True
        and iembedding.get("complete_label_embedding_injective") is False
        and all_zero(pgauge.get("cylinder_trace_residual"))
        and pgauge.get("canonical_momentum_selected") is False
        and igauge.get("cylinder_equal") is True
        and igauge.get("canonical_momentum_selected_by_q_cylinders") is False
        and praw.get("bounded_generator_core") is False
        and iraw.get("bounded_wstar_generator_core") is False
    )
    audit.check(
        "embedding, momentum and raw-generator negatives cross",
        negatives_ok,
        negatives_ok,
        True,
        "cross_core",
    )

    pparity_beta = as_mapping(pderived.get("parity_and_cross_beta"))
    pparity = as_mapping(pparity_beta.get("parity"))
    pcross_beta = as_mapping(pparity_beta.get("cross_beta"))
    iparity_beta = as_mapping(iderived.get("parity_cross_beta"))
    psolutions = fraction_list(pparity.get("parity_solutions"))
    parity_beta_ok = (
        psolutions == [Fraction(1, 2)]
        and pparity.get("asymmetric_zero_source_periodic_limit_possible") is False
        and as_fraction(iparity_beta.get("unique_parity_weight")) == Fraction(1, 2)
        and iparity_beta.get("symmetric_limit_still_unproved") is True
        and pcross_beta.get("single_inner_dynamics_possible") is False
        and iparity_beta.get("automatic_cross_beta_gluing") is False
    )
    audit.check(
        "parity and cross-beta negatives cross",
        parity_beta_ok,
        parity_beta_ok,
        True,
        "cross_core",
    )

    pjet_tail = as_mapping(pderived.get("local_jet_and_coordinate_tail"))
    ijet_tail = as_mapping(iderived.get("generator_first_tail"))
    tail_ok = (
        as_mapping(pjet_tail.get("coordinate_tail")).get("all_higher_orbit_rungs_resummed") is False
        and ijet_tail.get("connected_tail_resummation_closed") is False
        and ijet_tail.get("real_time_series_summed") is False
    )
    audit.check(
        "first-tail-only boundary cross",
        tail_ok,
        tail_ok,
        True,
        "cross_core",
    )

    primary_scope = {
        "scalar_kms": pderived.get("kms_scalar_analytic_continuation_from_real_time") is True,
        "no_operator_complex_time": pderived.get("raw_operator_complex_time_alpha_used") is False,
        "fixed_band": pderived.get("fixed_band_finite_word_gram_convergence_scope") is True,
        "finite_core_fell_gns": pderived.get("independent_pivot_pointed_finite_core_fell_gns_scope") is True,
        "no_common_hilbert_strong_star": pderived.get("common_hilbert_operator_strong_star_closed") is False,
        "cyclic_l2_only": pderived.get("raw_character_cyclic_two_sided_l2_filter_removal") is True,
        "no_arbitrary_context": pderived.get("arbitrary_bandlimited_left_right_context_control_closed") is False,
        "no_raw_operator_strong_star": pderived.get("raw_character_operator_strong_star_recovery_closed") is False,
    }
    independent_boundary = str(as_mapping(independent.get("authority")).get("boundary", independent.get("boundary", "")))
    independent_scope = {
        "selected_tangent": iderived.get("selected_tangent_pointed_gns_identification_closed") is True,
        "finite_core_fell_gns": text_has(independent_boundary, "pointed finite-core Fell-GNS"),
        "no_common_hilbert_strong_star": text_has(independent_boundary, "does not prove")
        and text_has(independent_boundary, "globally compatible common-Hilbert operator strong-star convergence"),
        "no_arbitrary_context": text_has(independent_boundary, "raw-character convergence after arbitrary left/right contexts"),
        "no_all_exhaustion": iderived.get("all_exhaustion_mixture_l2_closed") is False,
    }
    audit.check(
        "narrowed topology scope cross",
        all(primary_scope.values()) and all(independent_scope.values()),
        {"primary": primary_scope, "independent": independent_scope},
        "all true",
        "scope",
    )
    return {
        "character_fejer_exact": bool(p_character_ok and i_character_ok),
        "finite_span_exact": span_ok,
        "positive_root_transport_exact": gram_ok,
        "five_negative_fixtures_crossed": bool(negatives_ok and parity_beta_ok),
        "first_tail_only": tail_ok,
        "scope": {
            "pointed_finite_core_fell_gns_only": True,
            "fejer_cyclic_two_sided_l2_only": True,
            "common_hilbert_operator_strong_star_closed": False,
            "arbitrary_context_control_closed": False,
        },
    }


def validate_manifest(manifest: dict[str, Any], audit: Audit) -> None:
    exact = {
        "candidate": manifest.get("candidate_id")
        == "PA-CP1-ST8-Q3LOCK-HAMILTONIAN-OS-TANGENT-TRANSPORT-GENERATOR-ROUTE-SPLIT-v0",
        "task": manifest.get("task_id") == TASK_ID,
        "exploration": manifest.get("exploration_id") == EXPLORATION_ID,
        "result_id": manifest.get("result_id") == RESULT_ID,
        "result_number": manifest.get("result_number") == RESULT_NUMBER,
        "result_version": manifest.get("result_version") == RESULT_VERSION,
        "claim_bearing": manifest.get("claim_bearing") is False,
        "negatives": tuple(manifest.get("negative_ids", [])) == NEGATIVE_IDS,
        "closed_gate": manifest.get("closed_subgates") == [CLOSED_GATE],
        "retained_gates": tuple(manifest.get("retained_gate_ids", [])) == RETAINED_GATES,
        "successor": as_mapping(manifest.get("route_status")).get("next_gate") == SUCCESSOR_GATE
        and SUCCESSOR_GATE in manifest.get("open_gates", []),
    }
    audit.check(
        "manifest exact identity and gate contract",
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

    transport = as_mapping(manifest.get("finite_block_polar_transport"))
    filter_theorem = as_mapping(manifest.get("character_dirichlet_and_filter_theorem"))
    route = as_mapping(manifest.get("route_status"))
    narrowed = {
        "finite_core_positive": text_has(transport.get("operator_transport", ""), "pointed finite-core Fell/GNS"),
        "finite_word_intertwining": text_has(transport.get("operator_transport", ""), "finite-word approximate intertwining"),
        "no_global_extension": text_has(transport.get("operator_transport", ""), "No globally compatible common-Hilbert extension is inferred"),
        "singular_pivots": text_has(transport.get("scope", ""), "Singular limit directions are discarded through retained independent pivots"),
        "cyclic_l2_positive": text_has(filter_theorem.get("fejer_filter", ""), "cyclic two-sided L2 vector"),
        "no_context": text_has(filter_theorem.get("fejer_filter", ""), "does not give arbitrary bandlimited left/right-context multiplier control"),
        "no_raw_operator": text_has(filter_theorem.get("fejer_filter", ""), "raw-core operator strong-star convergence"),
        "route_finite_core": text_has(route.get("closed_scope", ""), "pointed finite-core Fell/GNS"),
        "route_cyclic": text_has(route.get("closed_scope", ""), "cyclic two-sided L2"),
    }
    audit.check(
        "manifest narrowed Fell-GNS and cyclic-L2 scope",
        all(narrowed.values()),
        narrowed,
        "all true",
        "scope",
    )
    serialized = json.dumps(manifest, sort_keys=True, ensure_ascii=True)
    forbidden_positive = (
        r"gives\s+pointed\s+strong[- ]star\s+convergence",
        r"raw\s+characters?\s+(?:are\s+)?recovered[^.]{0,100}operator\s+strong[- ]star",
        r"partial\s+polar\s+transport[^.]{0,100}(?:full|higher)[- ]rank",
    )
    hits = [pattern for pattern in forbidden_positive if re.search(pattern, serialized, re.I)]
    audit.check(
        "manifest has no broadened positive topology claim",
        not hits,
        hits,
        [],
        "scope",
    )
    require_tokens(
        manifest.get("no_overclaim", ""),
        "manifest no-overclaim",
        (
            "selected fixed-beta",
            "pointed finite-core Fell-GNS",
            "exact cyclic character",
            "globally compatible common-Hilbert operator strong-star",
            "arbitrary left/right contexts",
            "all-exhaustion",
            "beta-independent",
            "ground states",
            "GNS",
            "continuum",
            "physical empty space",
            "Pre-A",
            "C6",
        ),
        audit,
        group="scope",
        core=True,
    )


def validate_certificate(audit: Audit) -> str:
    certificate = require_text(CERTIFICATE, audit, "certificate") or ""
    if not certificate:
        return certificate
    require_tokens(
        certificate,
        "certificate theorem and boundary",
        (
            EXPLORATION_ID,
            RESULT_NUMBER,
            RESULT_VERSION,
            TASK_ID,
            CLOSED_GATE,
            SUCCESSOR_GATE,
            *NEGATIVE_IDS,
            "bounded scalar KMS analytic continuation",
            "maximally totally real",
            "L1 translation continuity",
            "countable bandlimited orbit-word list",
            "pointed finite-core Fell/GNS convergence",
            "no common-Hilbert operator strong-star convergence is inferred",
            "retained independent pivots",
            "cyclic two-sided L2 vector",
            "does not control multiplication",
            "does not upgrade the raw characters to operator strong-star convergence",
            "delta(A_f)=-A_(f')",
            "does not issue or render an intermediate note PDF",
        ),
        audit,
        group="scope",
        core=True,
    )
    forbidden = (
        r"gives\s+pointed\s+strong[- ]star\s+convergence",
        r"partial\s+polar\s+transport\s+from\s+the\s+full",
        r"recover(?:s|ed)?\s+raw[^.]{0,120}operator\s+strong[- ]star\s+convergence(?!\s+is\s+not)",
    )
    hits = [pattern for pattern in forbidden if re.search(pattern, certificate, re.I)]
    audit.check(
        "certificate has no broadened positive topology claim",
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


def validate_pdf_efficiency(
    audit: Audit, manifest: dict[str, Any], certificate: str
) -> dict[str, Any]:
    notes_root = REPO / "claims"
    package_artifacts: list[str] = []
    if notes_root.is_dir():
        for path in notes_root.rglob("*"):
            if not path.is_file():
                continue
            lower = path.name.lower()
            if not (lower.endswith(".pdf") or lower.endswith(".tex.txt")):
                continue
            normalized = re.sub(r"[^a-z0-9]+", "-", lower)
            if all(token in normalized for token in ("hamiltonian", "os", "tangent", "transport", "generator")):
                package_artifacts.append(path.relative_to(REPO).as_posix())
    audit.check(
        "no EXP-000801 note source or PDF exists",
        not package_artifacts,
        package_artifacts,
        [],
        "pdf_efficiency",
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
            if target.endswith(".pdf") or target.endswith(".tex.txt"):
                changed_artifacts.append(path_text)
    audit.check(
        "git can audit changed note/PDF artifacts",
        completed.returncode == 0,
        {"returncode": completed.returncode, "stderr": completed.stderr[-400:]},
        {"returncode": 0},
        "pdf_efficiency",
    )
    audit.check(
        "no new or reissued note/PDF in worktree",
        completed.returncode == 0 and not changed_artifacts,
        changed_artifacts,
        [],
        "pdf_efficiency",
    )

    authority_text = json.dumps(manifest, sort_keys=True, ensure_ascii=True) + "\n" + certificate
    artifact_refs = re.findall(
        r"claims/[A-Za-z0-9_./-]+(?:\.tex\.txt|\.pdf)", authority_text, re.I
    )
    audit.check(
        "manifest and certificate cite no intermediate note/PDF path",
        not artifact_refs,
        artifact_refs,
        [],
        "pdf_efficiency",
    )
    return {
        "policy": "development-records-only-until-gate-checkpoint",
        "package_artifacts": package_artifacts,
        "changed_note_or_pdf_artifacts": changed_artifacts,
        "authority_artifact_refs": artifact_refs,
        "pdf_imported": False,
        "render_attempted": False,
    }


def validate_formal(manifest: dict[str, Any], audit: Audit) -> dict[str, Any]:
    exploration_required_paths = (MANIFEST, CERTIFICATE, PRIMARY, INDEPENDENT)
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
    corrections = (
        []
        if explorations is None
        else [row for row in explorations if row.get("id") == CORRECTION_ID]
    )
    audit.pending(
        f"{CORRECTION_ID} correction unique",
        len(corrections) == 1,
        len(corrections),
        1,
        "formal",
    )
    if len(matches) == 1:
        record = matches[0]
        serialized = json.dumps(record, sort_keys=True, ensure_ascii=True)
        refs = as_mapping(record.get("formal_refs"))
        gates = set(record.get("gate_ids", []))
        evidence = record.get("evidence_refs", [])
        conditions = {
            "task": record.get("task_id") == TASK_ID,
            "verdict": record.get("verdict") == "advanced",
            "claim": record.get("claim_ids") == [CLAIM_ID],
            "result": refs.get("results") == [RESULT_NUMBER],
            "negatives": set(refs.get("negatives", [])) == set(NEGATIVE_IDS),
            "closed_gate": CLOSED_GATE in gates,
            "successor_gate": SUCCESSOR_GATE in gates,
            "paths": all(
                path.relative_to(REPO).as_posix() in serialized
                for path in exploration_required_paths
            ),
            "no_note_pdf": isinstance(evidence, list)
            and not any(str(item).lower().endswith((".pdf", ".tex.txt")) for item in evidence),
        }
        audit.pending(
            f"{EXPLORATION_ID} complete chain",
            all(conditions.values()),
            conditions,
            "all true",
            "formal",
        )
        require_tokens(
            record.get("boundary", ""),
            f"{EXPLORATION_ID} base boundary",
            (
                "fixed-beta",
                "finite-core Fell-GNS",
                "common-Hilbert operator strong-star",
                "arbitrary left/right contexts",
                "all-shape exhaustion",
                "beta-independent",
                "ground",
                "GNS",
                "continuum",
                "Pre-A",
            ),
            audit,
        )
    if len(matches) == 1 and len(corrections) == 1:
        record = matches[0]
        correction = corrections[0]
        aggregate = json.dumps(
            [record, correction], sort_keys=True, ensure_ascii=True
        )
        related = correction.get("related", [])
        related_ok = isinstance(related, list) and any(
            isinstance(item, dict)
            and item.get("id") == EXPLORATION_ID
            and item.get("relation") == "corrects"
            for item in related
        )
        correction_refs = as_mapping(correction.get("formal_refs"))
        correction_conditions = {
            "task": correction.get("task_id") == TASK_ID,
            "verdict": correction.get("verdict") == "advanced",
            "claim": correction.get("claim_ids") == [CLAIM_ID],
            "result": correction_refs.get("results") == [RESULT_NUMBER],
            "relation": related_ok,
            "integrated_path": SCRIPT.relative_to(REPO).as_posix() in aggregate,
            "aggregate_paths": all(
                path.relative_to(REPO).as_posix() in aggregate
                for path in (*exploration_required_paths, SCRIPT)
            ),
            "no_note_pdf": ".tex.txt" not in aggregate.lower()
            and not re.search(r"claims/[A-Za-z0-9_./-]+\.pdf", aggregate, re.I),
        }
        audit.pending(
            f"{CORRECTION_ID} append-only correction chain",
            all(correction_conditions.values()),
            correction_conditions,
            "all true",
            "formal",
        )
        require_tokens(
            aggregate,
            f"{EXPLORATION_ID}/{CORRECTION_ID} aggregate narrow scope",
            (
                "cyclic two-sided L2",
                "all-exhaustion",
                "globally compatible common-Hilbert operator strong-star",
                "arbitrary left/right contexts",
                "integrated",
                "no-intermediate-PDF",
            ),
            audit,
        )

    ledger = require_text(REPO / "RESULTS-LEDGER.md", audit, "result ledger")
    if ledger is not None:
        audit.pending(
            "R-167 unique detail",
            ledger.count("### R-167 --") == 1,
            ledger.count("### R-167 --"),
            1,
            "formal",
        )
        require_tokens(
            ledger,
            "R-167 v1.5 ledger",
            (
                RESULT_ID,
                RESULT_NUMBER,
                RESULT_VERSION,
                EXPLORATION_ID,
                CLOSED_GATE,
                SUCCESSOR_GATE,
                *NEGATIVE_IDS,
                "pointed finite-core Fell/GNS",
                "cyclic two-sided L2",
                "not a left/right-context multiplier estimate",
                "no intermediate note/PDF",
            ),
            audit,
        )

    registry = require_text(
        REPO / "negative-results/registry.md", audit, "negative registry"
    )
    if registry is not None:
        for negative in NEGATIVE_IDS:
            audit.pending(
                f"negative authority {negative}",
                registry.count(negative) >= 2,
                registry.count(negative),
                ">=2",
                "formal",
            )

    gates_text = require_text(REPO / "claims/GATES.md", audit, "gate authority")
    if gates_text is not None:
        closed = gate_section(gates_text, CLOSED_GATE)
        audit.pending(
            "closed selected-tangent gate authority",
            closed is not None
            and re.search(r"\*\*Status:\*\*\s*CLOSED", closed, re.I) is not None
            and text_has(closed, EXPLORATION_ID),
            closed,
            "CLOSED and linked to EXP-000801",
            "formal",
        )
        successor = gate_section(gates_text, SUCCESSOR_GATE)
        audit.pending(
            "open successor gate authority",
            successor is not None
            and re.search(r"\*\*Status:\*\*\s*OPEN", successor, re.I) is not None
            and text_has(successor, EXPLORATION_ID),
            successor,
            "OPEN and linked to EXP-000801",
            "formal",
        )

    todo = load_json(REPO / "todo/todo.json", audit, "TODO authority", formal=True)
    if todo is not None:
        tasks = todo.get("tasks", [])
        found = [
            item
            for item in tasks
            if isinstance(item, dict) and item.get("id") == TASK_ID
        ] if isinstance(tasks, list) else []
        audit.pending("T-054 unique", len(found) == 1, len(found), 1, "formal")
        if len(found) == 1:
            serialized = json.dumps(found[0], sort_keys=True, ensure_ascii=True)
            audit.pending(
                "T-054 remains in progress",
                found[0].get("status") == "in_progress",
                found[0].get("status"),
                "in_progress",
                "formal",
            )
            require_tokens(
                serialized,
                "T-054 v1.5 linkage",
                (EXPLORATION_ID, RESULT_NUMBER, RESULT_VERSION, CLOSED_GATE, SUCCESSOR_GATE),
                audit,
            )

    roadmap = require_text(REPO / "ROADMAP.md", audit, "roadmap")
    if roadmap is not None:
        require_tokens(
            roadmap,
            "roadmap v1.5 linkage",
            (TASK_ID, EXPLORATION_ID, RESULT_NUMBER, RESULT_VERSION, CLOSED_GATE, SUCCESSOR_GATE),
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
            json.dumps(theorem_map, sort_keys=True, ensure_ascii=True),
            "theorem map v1.5 linkage",
            (EXPLORATION_ID, RESULT_NUMBER, RESULT_VERSION, CLOSED_GATE, SUCCESSOR_GATE),
            audit,
        )

    changelog = jsonl_records(REPO / "changelog/log.jsonl", audit, "changelog")
    events = (
        []
        if changelog is None
        else [
            event
            for event in changelog
            if text_has(json.dumps(event, sort_keys=True), EXPLORATION_ID)
        ]
    )
    audit.pending(
        "EXP-000801 changelog unique", len(events) == 1, len(events), 1, "formal"
    )
    if len(events) == 1:
        event = events[0]
        notes = event.get("notes", [])
        scripts = event.get("scripts", [])
        serialized = json.dumps(event, sort_keys=True, ensure_ascii=True)
        conditions = {
            "claim_refs": set(event.get("claim_ids", []))
            == {CLAIM_ID, EXPLORATION_ID, RESULT_NUMBER},
            "negatives": set(event.get("neg_results", [])) == set(NEGATIVE_IDS),
            "scripts": {
                PRIMARY.relative_to(REPO).as_posix(),
                INDEPENDENT.relative_to(REPO).as_posix(),
                SCRIPT.relative_to(REPO).as_posix(),
            }.issubset(set(scripts)) if isinstance(scripts, list) else False,
            "notes_deferred": notes == [],
            "no_note_pdf_path": ".tex.txt" not in serialized.lower()
            and not re.search(r"claims/[A-Za-z0-9_./-]+\.pdf", serialized, re.I),
            "scope": all(
                text_has(event.get("raw", ""), token)
                for token in (
                    "pointed finite-core Fell/GNS",
                    "cyclic two-sided L2",
                    "common-Hilbert operator strong-star",
                    "raw-context multiplier",
                    "no intermediate note/PDF",
                )
            ),
        }
        audit.pending(
            "EXP-000801 changelog complete",
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
            "proof-evidence map v1.5 linkage",
            (EXPLORATION_ID, CORRECTION_ID, RESULT_NUMBER, RESULT_VERSION, CLOSED_GATE, SUCCESSOR_GATE, *NEGATIVE_IDS),
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
            json.dumps(proof_map_json, sort_keys=True, ensure_ascii=True),
            "proof-evidence JSON v1.5 linkage",
            (EXPLORATION_ID, CORRECTION_ID, RESULT_NUMBER, RESULT_VERSION, CLOSED_GATE, SUCCESSOR_GATE, *NEGATIVE_IDS),
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
        "correction_matches": len(corrections),
        "changelog_matches": len(events),
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
    with tempfile.TemporaryDirectory(prefix="tect-exp801-integrated-") as directory:
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
        "negative_ids": list(NEGATIVE_IDS),
        "closed_gates": [CLOSED_GATE],
        "open_gates": [SUCCESSOR_GATE, *RETAINED_GATES],
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
            "pointed_finite_core_fell_gns_only": True,
            "fejer_cyclic_two_sided_l2_only": True,
            "common_hilbert_operator_strong_star_closed": False,
            "raw_character_arbitrary_context_control_closed": False,
            "raw_character_operator_strong_star_closed": False,
            "all_exhaustion_mixture_l2_closed": False,
            "beta_independent_cstar_dynamics_closed": False,
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
        help="exit zero with explicit MISSING rows while formal authorities assemble",
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

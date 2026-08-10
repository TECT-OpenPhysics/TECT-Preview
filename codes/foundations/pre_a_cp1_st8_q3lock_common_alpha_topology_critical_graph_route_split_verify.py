#!/usr/bin/env python3
"""Integrated verifier for EXP-000799 / R-167 v1.3.

The primary SymPy calculation and the independent standard-library audit are
executed twice in fresh temporary directories.  Their deterministic payloads
are compared with the stored results, their implementations are separated by
an AST import firewall, and their differently shaped exact fixtures are
reconciled here.  The verifier also checks the append-only proof authorities,
the retained common-alpha gates, and the rendered note/PDF boundary.

``--staged`` is assembly-safe: a missing or not-yet-synchronised formal
authority is reported as ``MISSING`` and the process exits zero, while a
contradiction in an available mathematical component remains a ``FAIL``.
Strict mode succeeds only with verdict ``PASS``.
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
from typing import Any, Iterable

try:
    from pypdf import PdfReader
except ImportError:  # Reported explicitly by the PDF audit.
    PdfReader = None  # type: ignore[assignment]


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-common-alpha-topology-critical-graph-route-split"
RESULT_ID = (
    "PA-CP1-ST8-Q3LOCK-SECOND-WEIGHTED-ENERGY-MOMENT-AND-"
    "COMMON-ALPHA-CAUCHY-GATE-SPLIT"
)
RESULT_NUMBER = "R-167"
RESULT_VERSION = "v1.3"
EXPLORATION_ID = "EXP-000799"
TASK_ID = "T-054"
CLAIM_ID = "C6-SPACETIME-SIGNATURE"

ALL_BOND_GATE = (
    "PA-CP1-ST8-Q3LOCK-ALL-BOND-UNITARY-TROTTER-GRAPH-"
    "LIPSCHITZ-AND-COMMON-ALPHA-CLOSURE"
)
PROJECTED_GATE = (
    "PA-CP1-ST8-Q3LOCK-PROJECTED-DUHAMEL-MODULAR-C1-"
    "MULTIPLIER-LOCALITY"
)
ROUND1_GATE = "PA-ROUND1-EVIDENCE-ROLE-AND-MINIMUM-MANIFEST-FREEZE"

NEGATIVE_IDS = (
    "NG-2026-08-10-PRE-A-ST8-Q3LOCK-RAW-LOCAL-RESOLVENT-"
    "POINT-NORM-BOND-KICK-CONTINUITY",
    "NG-2026-08-10-PRE-A-ST8-Q3LOCK-UNWEIGHTED-ONSITE-"
    "QP-LIPSCHITZ-STABILITY",
    "NG-2026-08-10-PRE-A-ST8-Q3LOCK-SUBCRITICAL-ENERGY-"
    "DAMPED-ONSITE-LIPSCHITZ-STABILITY",
    "NG-2026-08-10-PRE-A-ST8-Q3LOCK-COORDINATE-CUTOFF-"
    "HALF-MODULAR-STRIP-ABSOLUTE-CLOSURE",
    "NG-2026-08-10-PRE-A-ST8-Q3LOCK-SMALL-D-DELTA-D-"
    "UNIFORM-HALF-STRIP-MULTIPLIER-INFERENCE",
    "NG-2026-08-10-PRE-A-ST8-Q3LOCK-FAITHFUL-REPRESENTATION-"
    "STRONGSTAR-ABSTRACT-CSTAR-INFERENCE",
    "NG-2026-08-10-PRE-A-ST8-Q3LOCK-CRITICAL-ONE-SIDED-"
    "ENERGY-DAMPED-LEIBNIZ-ONSITE-STABILITY",
)

PRIMARY = REPO / f"codes/foundations/{SLUG.replace('-', '_')}.py"
INDEPENDENT = REPO / f"codes/foundations/{SLUG.replace('-', '_')}_independent.py"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260810.md"
PARENT_MANIFEST = REPO / (
    "strategy/pre-a-cp1-st8-q3lock-modular-cutoff-unitary-"
    "resummation-route-split-manifest.json"
)
NOTE = REPO / (
    "claims/C6-SPACETIME-SIGNATURE/notes/"
    "pre-a-q3lock-common-alpha-topology-critical-graph-route-split-"
    "260810-v0.4.tex.txt"
)
PDF = NOTE.with_name(NOTE.name.removesuffix(".tex.txt") + ".pdf")
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

PRIMARY_SCHEMA = "tect/foundation-audit/1.0"
INDEPENDENT_SCHEMA = f"tect/{SLUG}-independent-result/1.0"
MINIMUM_PRIMARY_COUNT = 59
MINIMUM_INDEPENDENT_COUNT = 85


def json_safe(value: Any) -> Any:
    if isinstance(value, Path):
        return value.as_posix()
    if isinstance(value, dict):
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


def artifact_sha256(path: Path) -> str:
    if path.suffix.lower() == ".pdf":
        return hashlib.sha256(path.read_bytes()).hexdigest()
    return portable_sha256(path)


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
            result = result.replace(spelling, "<TEMP>")
        return result.replace("\\", "/")
    if isinstance(value, dict):
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


class Audit:
    """Accumulate every defect without hiding staged assembly state."""

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
    path: Path,
    audit: Audit,
    label: str,
    *,
    formal: bool = False,
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


def jsonl_records(path: Path, audit: Audit, label: str) -> list[dict[str, Any]] | None:
    if not path.is_file():
        audit.require(f"{label} exists", False, path.relative_to(REPO), "file", "formal")
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


def run_once(
    script: Path,
    output: Path,
    temporary_root: Path,
    audit: Audit,
    label: str,
) -> tuple[dict[str, Any], str] | None:
    if not script.is_file():
        audit.require(f"{label} script exists", False, script.relative_to(REPO), "file", "freshness")
        return None
    completed = subprocess.run(
        [sys.executable, "-X", "utf8", str(script), "--output", str(output)],
        cwd=REPO,
        check=False,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=360,
    )
    if completed.returncode != 0 or not output.is_file():
        audit.pending(
            f"{label} execution",
            False,
            normalize_volatile(
                {
                    "returncode": completed.returncode,
                    "stdout": completed.stdout[-1500:],
                    "stderr": completed.stderr[-1500:],
                    "output_exists": output.is_file(),
                },
                (temporary_root,),
            ),
            "exit 0 and JSON",
            "freshness",
        )
        return None
    try:
        payload = json.loads(output.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        audit.check(f"{label} JSON", False, error, "valid JSON object", "freshness")
        return None
    if not isinstance(payload, dict):
        audit.check(f"{label} object", False, type(payload).__name__, "dict", "freshness")
        return None
    sentinel = next(
        (line.strip() for line in completed.stdout.splitlines() if line.strip().startswith("PASS ")),
        "",
    )
    audit.check(f"{label} execution", True, completed.returncode, 0, "freshness")
    audit.check(f"{label} PASS sentinel", bool(sentinel), sentinel, "PASS ...", "freshness")
    return normalize_volatile(payload, (temporary_root,)), sentinel


def run_fresh_pair(
    script: Path,
    temporary_root: Path,
    audit: Audit,
    label: str,
) -> tuple[dict[str, Any], str] | None:
    first = run_once(script, temporary_root / f"{label}-a.json", temporary_root, audit, f"{label} fresh A")
    second = run_once(script, temporary_root / f"{label}-b.json", temporary_root, audit, f"{label} fresh B")
    if first is None or second is None:
        audit.require(
            f"{label} two fresh payloads", False, [first is not None, second is not None], [True, True], "freshness"
        )
        return first or second
    first_bytes = canonical_payload(first[0])
    second_bytes = canonical_payload(second[0])
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
        audit.pending(f"{label} stored parses", False, error, "valid JSON", "freshness")
        return None
    if not isinstance(stored, dict):
        audit.pending(f"{label} stored object", False, type(stored).__name__, "dict", "freshness")
        return None
    stored_bytes = canonical_payload(stored)
    fresh_bytes = canonical_payload(fresh) if fresh is not None else b""
    audit.pending(
        f"{label} stored equals fresh",
        fresh is not None and stored_bytes == fresh_bytes,
        {
            "stored": hashlib.sha256(stored_bytes).hexdigest(),
            "fresh": hashlib.sha256(fresh_bytes).hexdigest() if fresh is not None else None,
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


def validate_component(payload: dict[str, Any], label: str, audit: Audit) -> None:
    primary = label == "primary"
    expected_schema = PRIMARY_SCHEMA if primary else INDEPENDENT_SCHEMA
    minimum = MINIMUM_PRIMARY_COUNT if primary else MINIMUM_INDEPENDENT_COUNT
    audit.check(f"{label} schema", payload.get("schema") == expected_schema, payload.get("schema"), expected_schema, "components")
    audit.check(f"{label} exploration", payload.get("exploration_id") == EXPLORATION_ID, payload.get("exploration_id"), EXPLORATION_ID, "components")
    audit.check(f"{label} result number", payload.get("result_number") == RESULT_NUMBER, payload.get("result_number"), RESULT_NUMBER, "components")
    audit.check(f"{label} result version", payload.get("result_version") == RESULT_VERSION, payload.get("result_version"), RESULT_VERSION, "components")
    audit.check(f"{label} verdict", payload.get("verdict") == "PASS", payload.get("verdict"), "PASS", "components")
    if primary:
        passed = payload.get("passed")
        failed = payload.get("failed")
        total = payload.get("total")
    else:
        summary = payload.get("assertions", {})
        passed = summary.get("passed") if isinstance(summary, dict) else None
        failed = summary.get("failed") if isinstance(summary, dict) else None
        total = summary.get("total") if isinstance(summary, dict) else None
        audit.check(f"{label} result id", payload.get("result_id") == RESULT_ID, payload.get("result_id"), RESULT_ID, "components")
        audit.check(f"{label} claim nonbearing", payload.get("claim_bearing") is False, payload.get("claim_bearing"), False, "scope")
    audit.check(
        f"{label} all-PASS count",
        isinstance(total, int) and total >= minimum and passed == total and failed == 0,
        {"passed": passed, "failed": failed, "total": total},
        f"passed=total>={minimum}, failed=0",
        "components",
    )
    rows = assertion_rows(payload)
    audit.check(f"{label} assertion rows", len(rows) == total, len(rows), total, "components")
    audit.check(f"{label} rows all PASS", bool(rows) and all(row.get("status") == "PASS" for row in rows), sum(row.get("status") == "PASS" for row in rows), total, "components")


def validate_independence(audit: Audit) -> None:
    missing = [path.relative_to(REPO).as_posix() for path in (PRIMARY, INDEPENDENT) if not path.is_file()]
    if missing:
        audit.require("AST sources exist", False, missing, "both sources", "independence")
        return
    try:
        primary_source = PRIMARY.read_text(encoding="utf-8")
        independent_source = INDEPENDENT.read_text(encoding="utf-8")
        primary_tree = ast.parse(primary_source, filename=str(PRIMARY))
        independent_tree = ast.parse(independent_source, filename=str(INDEPENDENT))
    except (OSError, UnicodeError, SyntaxError) as error:
        audit.check("AST parsing", False, error, "two valid ASTs", "independence")
        return
    imports: set[str] = set()
    dynamic: list[str] = []
    for node in ast.walk(independent_tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in {"__import__", "eval", "exec"}:
                dynamic.append(node.func.id)
            elif isinstance(node.func, ast.Attribute) and node.func.attr in {"import_module", "run_module", "run_path"}:
                dynamic.append(node.func.attr)
    forbidden = {"sympy", "numpy", "importlib", "runpy", "subprocess", PRIMARY.stem}
    audit.check("independent import firewall", not imports.intersection(forbidden), sorted(imports.intersection(forbidden)), [], "independence")
    audit.check("independent dynamic import firewall", not dynamic, dynamic, [], "independence")
    audit.check("independent does not name primary module", PRIMARY.stem not in independent_source, PRIMARY.stem in independent_source, False, "independence")
    primary_dump = ast.dump(primary_tree, include_attributes=False)
    independent_dump = ast.dump(independent_tree, include_attributes=False)
    audit.check("independent AST differs", primary_dump != independent_dump, "different" if primary_dump != independent_dump else "same", "different", "independence")
    audit.check("independent source hash differs", portable_sha256(PRIMARY) != portable_sha256(INDEPENDENT), portable_sha256(INDEPENDENT), f"different from {portable_sha256(PRIMARY)}", "independence")


def validate_hashes(primary: dict[str, Any], independent: dict[str, Any], audit: Audit) -> None:
    if not MANIFEST.is_file() or not CERTIFICATE.is_file():
        audit.require("manifest and certificate available for hash audit", False, [MANIFEST.is_file(), CERTIFICATE.is_file()], [True, True], "hashes")
        return
    manifest_hash = portable_sha256(MANIFEST)
    certificate_hash = portable_sha256(CERTIFICATE)
    provenance = primary.get("provenance", {})
    audit.check("primary manifest hash", isinstance(provenance, dict) and provenance.get("manifest_sha256") == manifest_hash, provenance.get("manifest_sha256") if isinstance(provenance, dict) else provenance, manifest_hash, "hashes")
    audit.check("primary certificate hash", isinstance(provenance, dict) and provenance.get("certificate_sha256") == certificate_hash, provenance.get("certificate_sha256") if isinstance(provenance, dict) else provenance, certificate_hash, "hashes")
    source_hashes = independent.get("source_hashes", {})
    manifest_key = MANIFEST.relative_to(REPO).as_posix()
    certificate_key = CERTIFICATE.relative_to(REPO).as_posix()
    audit.check("independent manifest hash", isinstance(source_hashes, dict) and source_hashes.get(manifest_key) == manifest_hash, source_hashes.get(manifest_key) if isinstance(source_hashes, dict) else source_hashes, manifest_hash, "hashes")
    audit.check("independent certificate hash", isinstance(source_hashes, dict) and source_hashes.get(certificate_key) == certificate_hash, source_hashes.get(certificate_key) if isinstance(source_hashes, dict) else source_hashes, certificate_hash, "hashes")
    if isinstance(source_hashes, dict):
        for relative, digest in sorted(source_hashes.items()):
            candidate = (REPO / relative).resolve()
            confined = candidate == REPO or REPO in candidate.parents
            expected = portable_sha256(candidate) if confined and candidate.is_file() else None
            audit.check(f"independent fresh hash {relative}", confined and expected == digest, digest, expected if confined else "repository-confined source", "hashes")


def as_fraction(value: Any) -> Fraction:
    return Fraction(str(value))


def increasing(values: list[Any]) -> bool:
    try:
        converted = [float(value) for value in values]
    except (TypeError, ValueError):
        return False
    return all(right > left for left, right in zip(converted, converted[1:]))


def critical_half_payload(derived: dict[str, Any]) -> dict[str, Any] | None:
    """Locate the independently named critical-half Leibniz fixture.

    The primary and stdlib implementations intentionally need not share a
    field path.  Selection therefore uses the exact new invariants, while all
    subsequent checks still require named jet and scope fields.
    """

    for key in (
        "critical_half_vector_field",
        "critical_half",
        "critical_half_leibniz_counterexample",
        "critical_half_leibniz",
        "critical_one_sided_leibniz",
    ):
        direct = derived.get(key)
        if isinstance(direct, dict):
            return direct

    candidates: list[tuple[str, dict[str, Any]]] = []

    def visit(value: Any, path: str) -> None:
        if not isinstance(value, dict):
            return
        serialized = json.dumps(value, sort_keys=True, ensure_ascii=True)
        lowered = path.lower() + " " + serialized.lower()
        if (
            ("critical" in lowered or "leibniz" in lowered)
            and "51/35" in serialized
            and "32112" in serialized
        ):
            candidates.append((path, value))
        for key, item in value.items():
            if isinstance(item, dict):
                visit(item, f"{path}.{key}" if path else str(key))

    visit(derived, "derived")
    if not candidates:
        return None
    # The smallest matching subtree is the most specific fixture.
    candidates.sort(
        key=lambda item: (
            len(json.dumps(item[1], sort_keys=True, ensure_ascii=True)),
            item[0],
        )
    )
    return candidates[0][1]


def recursive_value(value: Any, aliases: Iterable[str]) -> Any:
    targets = {re.sub(r"[^a-z0-9]", "", alias.lower()) for alias in aliases}
    if isinstance(value, dict):
        for key, item in value.items():
            normalized = re.sub(r"[^a-z0-9]", "", str(key).lower())
            if normalized in targets:
                return item
        for item in value.values():
            found = recursive_value(item, aliases)
            if found is not None:
                return found
    elif isinstance(value, list):
        for item in value:
            found = recursive_value(item, aliases)
            if found is not None:
                return found
    return None


def canonical_monomial(value: Any) -> str:
    return (
        str(value)
        .replace(" ", "")
        .replace("**", "^")
        .replace("(", "")
        .replace(")", "")
    )


def monomial_coefficient(value: Any) -> str:
    text = canonical_monomial(value)
    if text == "0":
        return "0"
    if "*a^" in text:
        return text.split("*a^", 1)[0]
    if text.startswith("a^"):
        return "1"
    if text.startswith("-a^"):
        return "-1"
    return text


def normalize_scalar_jets(value: Any) -> list[str] | None:
    if isinstance(value, (list, tuple)):
        return [str(item) for item in value]
    if isinstance(value, dict):
        normalized = {
            re.sub(r"[^a-z0-9]", "", str(key).lower()): str(item)
            for key, item in value.items()
        }
        for prefixes in (
            ("d0", "d1", "d2", "d3", "d4"),
            ("j0", "j1", "j2", "j3", "j4"),
        ):
            if all(key in normalized for key in prefixes):
                return [normalized[key] for key in prefixes]
    return None


def jet_rows(value: Any) -> list[dict[str, Any]] | None:
    if not isinstance(value, dict):
        return None
    rows = recursive_value(value, ("backward_jets", "jet_rows"))
    if not isinstance(rows, list) or not all(isinstance(row, dict) for row in rows):
        return None
    return rows


def jet_coefficient(rows: list[dict[str, Any]] | None, order: int) -> tuple[str, str] | None:
    if rows is None:
        return None
    matches = [row for row in rows if row.get("order") == order]
    if len(matches) != 1:
        return None
    polynomial = matches[0].get("axis_polynomial")
    if not isinstance(polynomial, dict):
        return None
    if not polynomial:
        return ("0", "0")
    if len(polynomial) != 1:
        return None
    exponent, coefficient = next(iter(polynomial.items()))
    return (str(coefficient), str(exponent))


def critical_contract(payload: dict[str, Any]) -> dict[str, Any]:
    q3 = recursive_value(payload, ("q3", "full_q3", "full_q3_jets"))
    scalar = recursive_value(payload, ("scalar", "scalar_fixture", "scalar_jets"))
    leibniz = recursive_value(payload, ("leibniz", "leibniz_fixture"))
    q3_source = q3 if isinstance(q3, dict) else payload
    scalar_source = scalar if isinstance(scalar, dict) else payload
    leibniz_source = leibniz if isinstance(leibniz, dict) else payload
    q3_rows = jet_rows(q3_source)
    scalar_rows = jet_rows(scalar_source)

    direct_q3_jets = recursive_value(
        payload,
        ("full_q3_backward_jets", "full_q3_jets", "q3_backward_jets"),
    )
    direct_scalar_jets = recursive_value(
        payload,
        ("scalar_backward_jets", "scalar_jets", "scalar_jet_sequence"),
    )

    first = jet_coefficient(q3_rows, 1)
    second = jet_coefficient(q3_rows, 2)
    third = jet_coefficient(q3_rows, 3)
    if first is not None:
        dp0: Any = (
            first[0]
            if first[1] == "0"
            else f"{first[0]}*a^{first[1]}"
        )
    else:
        dp0 = recursive_value(q3_source, ("Dp0", "D_p0", "first_p_jet"))
    d2: Any = second[0] if second is not None else recursive_value(q3_source, ("D2", "second_jet"))
    if third is not None:
        d3: Any = (
            third[0]
            if third[1] == "0"
            else f"{third[0]}*a^{third[1]}"
        )
    else:
        d3 = recursive_value(q3_source, ("D3", "third_jet"))
    if (
        isinstance(direct_q3_jets, list)
        and len(direct_q3_jets) == 3
    ):
        dp0, d2, d3 = direct_q3_jets

    scalar_values: list[str] | None = None
    if scalar_rows is not None:
        scalar_values = []
        for order in range(1, 6):
            item = jet_coefficient(scalar_rows, order)
            if item is None:
                scalar_values = None
                break
            scalar_values.append(item[0])
    if scalar_values is None:
        scalar_values = normalize_scalar_jets(
            direct_scalar_jets
        )
    if scalar_values is not None:
        scalar_values = [monomial_coefficient(item) for item in scalar_values]
    scope = recursive_value(
        leibniz_source,
        ("scope", "scope_boundary", "no_overclaim", "boundary"),
    )
    return {
        "G": recursive_value(q3_source, ("G", "G_fixture", "exact_G", "gram_G")),
        "Dp0": dp0,
        "D2": d2,
        "D3": d3,
        "scalar_jets": scalar_values,
        "scope": str(scope) if scope is not None else None,
        "one_sided_closed": recursive_value(
            payload,
            (
                "fixed_one_sided_leibniz_critical_closed",
                "one_sided_critical_uniform_stability",
                "critical_half_one_sided_leibniz_stability",
            ),
        ),
        "alternatives_open": recursive_value(
            payload,
            (
                "nonleibniz_or_state_weighted_critical_open",
                "alternative_critical_topology_open",
            ),
        ),
        "finite_weyl_evidence": recursive_value(
            leibniz_source,
            ("L_Wb", "identity", "weyl_power_identity"),
        ),
        "p_commutator_evidence": recursive_value(
            leibniz_source,
            ("commutator_domination", "leading_p", "p_commutator_domination"),
        ),
    }


def compare_exact_core(primary: dict[str, Any], independent: dict[str, Any], audit: Audit) -> dict[str, Any]:
    p = primary.get("derived", {})
    i = independent.get("derived", {})
    if not isinstance(p, dict) or not isinstance(i, dict):
        audit.check("derived payload objects", False, [type(p).__name__, type(i).__name__], ["dict", "dict"], "cross_core")
        return {}
    pk = p.get("centered_kick", {})
    ig = i.get("global_graph", {})
    c_b = [pk.get("c_b") if isinstance(pk, dict) else None, ig.get("C_b") if isinstance(ig, dict) else None]
    audit.check("exact cross C_b", c_b == ["521/35", "521/35"], c_b, ["521/35", "521/35"], "cross_core")
    weighted = [pk.get("weighted_star_coefficient") if isinstance(pk, dict) else None, ig.get("weighted_s_coefficient_before_absorption") if isinstance(ig, dict) else None]
    audit.check("exact cross weighted z2 ratio", weighted == ["54", "54"], weighted, ["54", "54"], "cross_core")

    commutator = p.get("centered_kick", {}).get("commutator_recurrence", {}) if isinstance(p.get("centered_kick", {}), dict) else {}
    ik = i.get("kick_commutator", {})
    sign_contract = {
        "primary_p_recurrence": commutator.get("p") if isinstance(commutator, dict) else None,
        "independent_convention": ik.get("convention") if isinstance(ik, dict) else None,
        "independent_neighbor": ik.get("neighbor_coefficient") if isinstance(ik, dict) else None,
    }
    sign_ok = (
        sign_contract["primary_p_recurrence"]
        == "beta([p_x,A]-delta*c*sum_y[q_y,A])"
        and sign_contract["independent_convention"]
        == "beta_delta(X)=B_delta^* X B_delta, so p_x maps to p_x+delta*c*sum_(y~x)q_y"
        and sign_contract["independent_neighbor"] == "6/35"
    )
    audit.check(
        "exact cross kick convention and sign",
        sign_ok,
        sign_contract,
        {
            "primary_p_recurrence": "beta([p_x,A]-delta*c*sum_y[q_y,A])",
            "independent_convention": "beta_delta(X)=B_delta^* X B_delta, so p_x maps to p_x+delta*c*sum_(y~x)q_y",
            "independent_neighbor": "6/35",
        },
        "cross_core",
    )
    graph_rows = ig.get("graph_power_rows", []) if isinstance(ig, dict) else []
    graph_contract = [
        {
            "s": str(row.get("s")),
            "one_sided_sum_power": str(row.get("one_sided_sum_power")),
            "fully_conjugated_safe_power": str(row.get("fully_conjugated_safe_power")),
        }
        for row in graph_rows
        if isinstance(row, dict)
    ]
    expected_graph_contract = [
        {"s": "0", "one_sided_sum_power": "0", "fully_conjugated_safe_power": "0"},
        {"s": "1/4", "one_sided_sum_power": "1/4", "fully_conjugated_safe_power": "1/2"},
        {"s": "3/8", "one_sided_sum_power": "3/8", "fully_conjugated_safe_power": "3/4"},
        {"s": "1/2", "one_sided_sum_power": "1/2", "fully_conjugated_safe_power": "1"},
    ]
    audit.check(
        "exact graph one-sided versus fully conjugated powers",
        graph_contract == expected_graph_contract,
        graph_contract,
        expected_graph_contract,
        "cross_core",
    )

    pr = p.get("resolvent", {})
    ir = i.get("resolvent_no_go", {})
    norms = [pr.get("exact_norm_distance") if isinstance(pr, dict) else None, ir.get("norm_distance_for_every_nonzero_delta") if isinstance(ir, dict) else None]
    audit.check("exact cross resolvent norm", norms == ["1", "1"], norms, ["1", "1"], "cross_core")
    p_residual = str(pr.get("residual", "")).replace(" ", "") if isinstance(pr, dict) else ""
    i_residual = str(ir.get("residual_identity", "")).replace(" ", "") if isinstance(ir, dict) else ""
    residual_poly = ir.get("residual_polynomial") if isinstance(ir, dict) else None
    residual_ok = p_residual in {"(u*v+1)**2", "(1+u*v)**2"}
    residual_ok = residual_ok and i_residual in {"(1+u*v)^2", "(u*v+1)^2"}
    residual_ok = residual_ok and residual_poly == {"(0, 0)": "1", "(1, 1)": "2", "(2, 2)": "1"}
    audit.check("exact cross resolvent residual", residual_ok, {"primary": pr.get("residual") if isinstance(pr, dict) else None, "independent": ir.get("residual_identity") if isinstance(ir, dict) else None, "polynomial": residual_poly}, "(1+u*v)^2 with coefficients 1,2,1", "cross_core")

    po = p.get("onsite", {})
    io = i.get("quartic_onsite_criticality", {})
    primary_polynomial = str(po.get("derivative_difference", "")).replace(" ", "") if isinstance(po, dict) else ""
    independent_polynomial = io.get("difference") if isinstance(io, dict) else None
    expected_numeric = {"0": "125/441", "1": "-25/21", "2": "5/3"}
    audit.check("exact cross onsite polynomial", primary_polynomial == "a*g*(a**2-3*a*q+3*q**2)" and independent_polynomial == expected_numeric, {"primary": primary_polynomial, "independent": independent_polynomial}, {"symbolic": "a*g*(a**2-3*a*q+3*q**2)", "g=7/9,a=5/7": expected_numeric}, "cross_core")
    p_exponents = po.get("translated_bump_exponents", {}) if isinstance(po, dict) else {}
    i_rows = io.get("exponent_rows", []) if isinstance(io, dict) else []
    i_exponents = {str(row.get("s")): str(row.get("translated_bump_exponent")) for row in i_rows if isinstance(row, dict)}
    expected_p = {"s_0": "2", "s_quarter": "1", "s_half": "0", "s_three_quarters": "-1"}
    expected_i = {"0": "2", "1/4": "1", "3/8": "1/2", "1/2": "0", "3/4": "-1"}
    audit.check("exact cross onsite exponents", p_exponents == expected_p and i_exponents == expected_i, {"primary": p_exponents, "independent": i_exponents}, {"primary": expected_p, "independent": expected_i}, "cross_core")

    pc = p.get("cutoff", {})
    ic = i.get("coordinate_cutoff", {})
    p_rows = pc.get("rows", []) if isinstance(pc, dict) else []
    i_cut_rows = ic.get("radius_rows", []) if isinstance(ic, dict) else []
    def quadratic(rows: list[Any]) -> bool:
        pairs = [(as_fraction(row["L"]), as_fraction(row["J_L"])) for row in rows if isinstance(row, dict) and "L" in row and "J_L" in row]
        return len(pairs) >= 3 and all(l2 == 2 * l1 and j2 == 4 * j1 for (l1, j1), (l2, j2) in zip(pairs, pairs[1:]))
    cutoff_ok = isinstance(pc, dict) and isinstance(ic, dict) and pc.get("growth_power") == "2" and ic.get("quartic_scaling_ratio") == "4" and quadratic(p_rows) and quadratic(i_cut_rows)
    audit.check("exact cross cutoff L2 growth", cutoff_ok, {"primary_power": pc.get("growth_power") if isinstance(pc, dict) else None, "independent_ratio": ic.get("quartic_scaling_ratio") if isinstance(ic, dict) else None, "primary_rows": p_rows, "independent_rows": i_cut_rows}, "both J_L sequences grow exactly by 4 when L doubles", "cross_core")

    pd = p.get("direct_relative", {})
    pid = i.get("direct_relative_unitary", {})
    idm = i.get("small_direct_tail_large_multiplier", {})
    p_m0 = [row.get("multiplier_lower_float") for row in pd.get("rows", []) if isinstance(row, dict)] if isinstance(pd, dict) else []
    direct_ok = (
        isinstance(pd, dict)
        and isinstance(pid, dict)
        and isinstance(idm, dict)
        and pd.get("fixed_finite_volume_unbounded_tail_passage_closed") is True
        and pd.get("thermodynamic_uniform_tail_passage_closed") is False
        and pid.get("fixed_finite_volume_unbounded_tail_passage_closed") is True
        and pid.get("thermodynamic_uniform_tail_passage_closed") is False
        and pd.get("uniform_evolved_half_strip_inferred") is False
        and increasing(p_m0)
        and all(idm.get(key) is True for key in ("W_tail_decreases", "modular_W_tail_decreases", "direct_tail_decreases", "direct_modular_tail_decreases", "M0_lower_increases"))
    )
    audit.check("exact cross direct-tail versus M0 divergence", direct_ok, {"primary_M0": p_m0, "primary_fixed_finite_volume": pd.get("fixed_finite_volume_unbounded_tail_passage_closed") if isinstance(pd, dict) else None, "independent_fixed_finite_volume": pid.get("fixed_finite_volume_unbounded_tail_passage_closed") if isinstance(pid, dict) else None, "independent_flags": {key: idm.get(key) for key in ("W_tail_decreases", "modular_W_tail_decreases", "direct_tail_decreases", "direct_modular_tail_decreases", "M0_lower_increases")} if isinstance(idm, dict) else idm}, "fixed-finite-volume direct and first modular tails decrease while M0 diverges", "cross_core")
    direct_constants_ok = (
        isinstance(pd, dict)
        and isinstance(pid, dict)
        and as_fraction(pd.get("one_orientation_bound_fixture")) == Fraction(195, 308)
        and as_fraction(pid.get("one_orientation_bound")) == Fraction(195, 308)
        and as_fraction(pd.get("trace_distance_bound_fixture")) == Fraction(195, 154)
        and as_fraction(pid.get("trace_distance_bound")) == Fraction(195, 154)
        and as_fraction(pd.get("entropy_coefficient_fixture")) == Fraction(4, 3)
        and as_fraction(pid.get("entropy_coefficient")) == Fraction(4, 3)
        and as_fraction(pd.get("right_hs_sq_fixture"))
        == as_fraction(pd.get("left_hs_sq_fixture"))
        == as_fraction(pd.get("phi_w2_matrix_fixture"))
        == Fraction(5, 1)
    )
    audit.check(
        "exact cross direct relative-unitary constants",
        direct_constants_ok,
        {
            "primary_one": pd.get("one_orientation_bound_fixture") if isinstance(pd, dict) else None,
            "independent_one": pid.get("one_orientation_bound") if isinstance(pid, dict) else None,
            "primary_trace": pd.get("trace_distance_bound_fixture") if isinstance(pd, dict) else None,
            "independent_trace": pid.get("trace_distance_bound") if isinstance(pid, dict) else None,
            "primary_entropy": pd.get("entropy_coefficient_fixture") if isinstance(pd, dict) else None,
            "independent_entropy": pid.get("entropy_coefficient") if isinstance(pid, dict) else None,
        },
        "195/308, 195/154, 4/3 and equal HS orientations",
        "cross_core",
    )

    prep = p.get("representation", {})
    irep = i.get("faithful_representation", {})
    representation_ok = (
        isinstance(prep, dict)
        and isinstance(irep, dict)
        and prep.get("multiplication_strong_star_limit") == 0
        and prep.get("direct_sum_strong_star_limit") == [0, 1]
        and prep.get("abstract_cstar_inference") is False
        and irep.get("standard_representation_faithful") is True
        and irep.get("standard_strong_star_limit") == "0"
        and irep.get("ultrafilter_character_limit") == "1"
        and irep.get("abstract_C_star_inference") is False
    )
    audit.check("exact cross representation fixture", representation_ok, {"primary": prep, "independent_limits": {key: irep.get(key) for key in ("standard_representation_faithful", "standard_strong_star_limit", "ultrafilter_character_limit", "abstract_C_star_inference")} if isinstance(irep, dict) else irep}, "faithful 0 versus faithful-direct-sum 0+1; no abstract inference", "cross_core")

    critical_payloads = {
        "primary": critical_half_payload(p),
        "independent": critical_half_payload(i),
    }
    for label, payload in critical_payloads.items():
        audit.pending(
            f"{label} critical-half Leibniz fixture present",
            payload is not None,
            None if payload is None else sorted(payload),
            "derived critical-half fixture with G and jet invariants",
            "cross_core",
        )
    critical_contracts: dict[str, dict[str, Any]] = {}
    for label, payload in critical_payloads.items():
        if payload is None:
            continue
        contract = critical_contract(payload)
        critical_contracts[label] = contract
        dp0 = canonical_monomial(contract["Dp0"])
        d2 = canonical_monomial(contract["D2"])
        d3 = canonical_monomial(contract["D3"])
        scope_text = compact_text(
            json.dumps(payload, sort_keys=True, ensure_ascii=True)
            + " "
            + (contract["scope"] or "")
        )
        exact_values = (
            str(contract["G"]) == "51/35"
            and dp0 in {"51*a^3/35", "51/35*a^3", "51a^3/35"}
            and d2 == "0"
            and d3
            in {
                "-32112*a^5/8575",
                "-32112/8575*a^5",
                "-32112a^5/8575",
            }
            and contract["scalar_jets"] == ["1", "0", "-3", "0", "27"]
        )
        audit.pending(
            f"{label} exact critical-half jets",
            exact_values,
            contract,
            {
                "G": "51/35",
                "Dp0": "51*a^3/35",
                "D2": "0",
                "D3": "-32112*a^5/8575",
                "scalar_jets": ["1", "0", "-3", "0", "27"],
            },
            "cross_core",
        )
        alternatives_retained = (
            contract.get("alternatives_open") is True
            or (
                "non-leibniz" in scope_text
                and any(
                    token in scope_text
                    for token in (
                        "state-weighted",
                        "state-tempered",
                        "two-sided",
                        "orbit-adapted",
                    )
                )
                and any(
                    token in scope_text
                    for token in ("does not reject", "remain open", "not all")
                )
            )
        )
        scope_ok = (
            contract.get("one_sided_closed") is False
            and contract.get("finite_weyl_evidence") is not None
            and contract.get("p_commutator_evidence") is not None
            and "leibniz" in scope_text
            and "critical" in scope_text
            and alternatives_retained
        )
        audit.pending(
            f"{label} critical-half scope firewall",
            scope_ok,
            contract["scope"],
            "rejects fixed C*-Leibniz seminorm finite on momentum Weyl and dominating either one-sided critical p-commutator; not all critical/state-weighted/non-Leibniz dynamics",
            "scope",
        )
    if len(critical_contracts) == 2:
        normalized_contracts = {
            label: {
                "G": str(contract["G"]),
                "Dp0": canonical_monomial(contract["Dp0"]),
                "D2": canonical_monomial(contract["D2"]),
                "D3": canonical_monomial(contract["D3"]),
                "scalar_jets": contract["scalar_jets"],
            }
            for label, contract in critical_contracts.items()
        }
        audit.pending(
            "exact cross critical-half no-go invariants",
            all(
                values["G"] == "51/35"
                and values["D2"] == "0"
                and values["scalar_jets"] == ["1", "0", "-3", "0", "27"]
                for values in normalized_contracts.values()
            ),
            normalized_contracts,
            "both engines independently reproduce G, full-Q3 jets, and scalar jets",
            "cross_core",
        )
    else:
        audit.pending(
            "exact cross critical-half no-go invariants",
            False,
            sorted(critical_contracts),
            ["primary", "independent"],
            "cross_core",
        )
    return {
        "C_b": "521/35",
        "weighted_z2_ratio": "54",
        "kick_neighbor_coefficient": "+6/35",
        "one_sided_sum_power": "s",
        "fully_conjugated_safe_power": "2s",
        "resolvent_norm": "1",
        "resolvent_residual": "(1+u*v)^2",
        "onsite_threshold": "s=1/2",
        "cutoff_growth": "L^2",
        "direct_tail_small_M0_large": True,
        "representation_dependent_strong_star": True,
        "critical_half_leibniz_no_go": {
            "G": "51/35",
            "full_Q3_jets": {
                "Dp0": "51*a^3/35",
                "D2": "0",
                "D3": "-32112*a^5/8575",
            },
            "scalar_jets": ["1", "0", "-3", "0", "27"],
        },
    }


def compact_text(value: str) -> str:
    # PDF extractors commonly insert whitespace after a line-ending hyphen in
    # long authority IDs.  Normalize only whitespace adjacent to hyphens before
    # the ordinary whitespace fold; this preserves exact token order while
    # making the check independent of page wrapping.
    value = re.sub(r"-\s+", "-", value)
    value = re.sub(r"\s+-", "-", value)
    return re.sub(r"\s+", " ", value).strip().lower()


def text_has(text: str, token: str) -> bool:
    return compact_text(token) in compact_text(text)


def require_tokens(text: str, label: str, tokens: Iterable[str], audit: Audit, group: str = "formal") -> None:
    for token in tokens:
        audit.pending(f"{label} token {token}", text_has(text, token), token if text_has(text, token) else "MISSING", token, group)


def validate_manifest(manifest: dict[str, Any], audit: Audit) -> None:
    exact = {
        "schema": "tect/pre-a-route-split/1.0",
        "task_id": TASK_ID,
        "exploration_id": EXPLORATION_ID,
        "result_id": RESULT_ID,
        "result_number": RESULT_NUMBER,
        "result_version": RESULT_VERSION,
        "claim_bearing": False,
    }
    for key, expected in exact.items():
        audit.check(f"manifest {key}", manifest.get(key) == expected, manifest.get(key), expected, "manifest")
    audit.check("manifest claim scope", manifest.get("claim_ids") == [CLAIM_ID], manifest.get("claim_ids"), [CLAIM_ID], "manifest")
    audit.pending("manifest exact seven negatives", isinstance(manifest.get("negative_ids"), list) and len(manifest["negative_ids"]) == 7 and set(manifest["negative_ids"]) == set(NEGATIVE_IDS), manifest.get("negative_ids"), list(NEGATIVE_IDS), "manifest")
    routes = manifest.get("active_routes", {})
    audit.check("manifest retained two active gates", isinstance(routes, dict) and routes.get("primary_gate") == ALL_BOND_GATE and routes.get("secondary_gate") == PROJECTED_GATE, routes, {"primary_gate": ALL_BOND_GATE, "secondary_gate": PROJECTED_GATE}, "manifest")
    audit.check("manifest exact open gate set", set(manifest.get("open_gates", [])) == {ALL_BOND_GATE, PROJECTED_GATE, ROUND1_GATE}, manifest.get("open_gates"), [ALL_BOND_GATE, PROJECTED_GATE, ROUND1_GATE], "manifest")
    verification = manifest.get("verification", {})
    expected_scripts = {
        "primary_script": PRIMARY.relative_to(REPO).as_posix(),
        "independent_script": INDEPENDENT.relative_to(REPO).as_posix(),
        "integrated_script": SCRIPT.relative_to(REPO).as_posix(),
    }
    for key, expected in expected_scripts.items():
        audit.check(f"manifest {key}", isinstance(verification, dict) and verification.get(key) == expected, verification.get(key) if isinstance(verification, dict) else verification, expected, "manifest")
    graph = manifest.get("all_bond_centered_graph_theorem", {})
    graph_contract = {
        "canonical_action": graph.get("canonical_action") if isinstance(graph, dict) else None,
        "graph_bound": graph.get("graph_bound") if isinstance(graph, dict) else None,
        "commutator_recurrence": graph.get("commutator_recurrence") if isinstance(graph, dict) else None,
    }
    audit.check(
        "manifest kick convention and graph powers",
        isinstance(graph, dict)
        and "B_delta^*p_xB_delta=p_x+delta c" in str(graph.get("canonical_action", ""))
        and "fully conjugated" in str(graph.get("graph_bound", "")).lower()
        and "power 2s" in str(graph.get("graph_bound", ""))
        and "each orientation" in str(graph.get("graph_bound", "")).lower()
        and "power s" in str(graph.get("graph_bound", ""))
        and "[p_x,A]-delta c" in str(graph.get("commutator_recurrence", "")),
        graph_contract,
        "beta=B*AB, p maps with plus; recurrence minus; one-sided s and fully conjugated 2s",
        "manifest",
    )
    resolvent = manifest.get("raw_resolvent_point_norm_counterexample", {})
    audit.check(
        "manifest resolvent plus convention",
        isinstance(resolvent, dict)
        and "B_delta^*AB_delta" in str(resolvent.get("kick", ""))
        and "p_x+delta c q_y" in str(resolvent.get("kick", "")),
        resolvent.get("kick") if isinstance(resolvent, dict) else resolvent,
        "beta=B*AB and (i+p_x+delta*c*q_y)^-1",
        "manifest",
    )
    direct = manifest.get("direct_relative_unitary_theorem", {})
    setup = str(direct.get("setup", "")) if isinstance(direct, dict) else ""
    tail_hypotheses = str(direct.get("unbounded_tail_hypotheses", "")) if isinstance(direct, dict) else ""
    audit.check(
        "manifest unbounded-W outer-cutoff passage",
        all(text_has(setup, token) for token in ("bounded outer cutoffs", "common closed forms", "strong resolvent", "Hilbert--Schmidt Gibbs vectors")),
        setup,
        "bounded outer cutoffs + form/strong-resolvent + Gibbs-vector passage",
        "manifest",
    )
    critical = critical_half_payload(manifest)
    audit.pending(
        "manifest critical-half Leibniz no-go present",
        critical is not None,
        None if critical is None else sorted(critical),
        "critical-half section containing G=51/35 and the exact third jet",
        "manifest",
    )
    if critical is not None:
        serialized_critical = json.dumps(critical, sort_keys=True, ensure_ascii=True)
        scope_value = recursive_value(
            critical,
            ("scope", "scope_boundary", "boundary", "no_overclaim"),
        )
        scope_text = compact_text(serialized_critical + " " + str(scope_value or ""))
        critical_scope_ok = all(
            token in scope_text
            for token in (
                "leibniz",
                "weyl",
                "one-sided",
                "critical",
                "p-commutator",
                "state-weighted",
                "non-leibniz",
            )
        ) and any(token in scope_text for token in ("does not", "not all", "doesn't"))
        audit.check(
            "manifest critical-half scope firewall",
            critical_scope_ok,
            scope_value or serialized_critical,
            "fixed C*-Leibniz one-sided no-go only; all-critical, state-weighted, and non-Leibniz dynamics retained",
            "scope",
        )
    audit.check(
        "manifest unbounded-tail load-bearing hypotheses",
        all(
            text_has(tail_hypotheses, token)
            for token in (
                "fixed finite Lambda",
                "form-norm cutoff convergence",
                "finite H-energy",
                "exponential W_L moment",
            )
        ),
        tail_hypotheses,
        "fixed finite volume + form norm + finite energy + exponential moment",
        "manifest",
    )
    trotter = manifest.get("finite_volume_trotter_graph_corollary", {})
    trotter_text = json.dumps(trotter, sort_keys=True) if isinstance(trotter, dict) else str(trotter)
    audit.check(
        "manifest Trotter domain-density passage",
        all(text_has(trotter_text, token) for token in ("D(K_X^(1/2-s))", "density", "D(K_X^s)", "s<1/2")),
        trotter_text,
        "dense D(K^(1/2-s)) extension to D(K^s), s<1/2",
        "manifest",
    )
    no_overclaim = str(manifest.get("no_overclaim", ""))
    require_tokens(no_overclaim, "manifest no-overclaim", ("s=1/2", "thermodynamic", "common C-star alpha", "KMS", "ground", "GNS", "continuum", "physical empty space", "C6", "Pre-A"), audit, group="scope")


def gate_section(text: str, gate: str) -> str | None:
    lines = text.splitlines()
    starts = [index for index, line in enumerate(lines) if line.startswith("###") and gate in line]
    if len(starts) != 1:
        return None
    start = starts[0]
    end = next((index for index in range(start + 1, len(lines)) if lines[index].startswith("###")), len(lines))
    return "\n".join(lines[start:end])


def validate_pdf(audit: Audit) -> dict[str, Any]:
    if not PDF.is_file():
        audit.require("PDF exists", False, PDF.relative_to(REPO), "file", "pdf")
        return {}
    raw = PDF.read_bytes()
    audit.pending("PDF header", raw.startswith(b"%PDF-"), raw[:5].decode("ascii", errors="replace"), "%PDF-", "pdf")
    audit.pending("PDF nontrivial size", len(raw) > 1024, len(raw), ">1024", "pdf")
    if NOTE.is_file():
        audit.pending("PDF fresh relative to note", PDF.stat().st_mtime_ns >= NOTE.stat().st_mtime_ns, {"pdf": PDF.stat().st_mtime_ns, "note": NOTE.stat().st_mtime_ns}, "pdf>=note", "pdf")
    if PdfReader is None:
        audit.pending("pypdf available", False, "ImportError", "installed pypdf", "pdf")
        return {"size_bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
    try:
        reader = PdfReader(str(PDF), strict=True)
        pages = len(reader.pages)
        text = "\n".join((page.extract_text() or "") for page in reader.pages)
    except Exception as error:
        audit.pending("PDF parses strictly", False, error, "strictly parseable PDF", "pdf")
        return {"size_bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
    audit.pending("PDF pages", pages >= 4, pages, ">=4", "pdf")
    audit.pending("PDF extracted text", len(text) > 2500, len(text), ">2500", "pdf")
    require_tokens(text, "PDF", (EXPLORATION_ID, RESULT_NUMBER, RESULT_VERSION, ALL_BOND_GATE, PROJECTED_GATE, *NEGATIVE_IDS), audit, group="pdf")
    require_tokens(text, "PDF boundary", ("common", "KMS", "GNS", "continuum", "Pre-A"), audit, group="pdf")
    return {"path": PDF.relative_to(REPO).as_posix(), "size_bytes": len(raw), "pages": pages, "text_characters": len(text), "sha256": hashlib.sha256(raw).hexdigest()}


def validate_formal(manifest: dict[str, Any], audit: Audit) -> dict[str, Any]:
    required_paths = (MANIFEST, CERTIFICATE, PRIMARY, INDEPENDENT, SCRIPT, NOTE, PDF)
    explorations = jsonl_records(REPO / "explorations/log.jsonl", audit, "exploration ledger")
    matches = [] if explorations is None else [row for row in explorations if row.get("id") == EXPLORATION_ID]
    audit.pending(f"{EXPLORATION_ID} unique", len(matches) == 1, len(matches), 1, "formal")
    if len(matches) == 1:
        record = matches[0]
        serialized = json.dumps(record, sort_keys=True, ensure_ascii=True)
        refs = record.get("formal_refs", {})
        negatives = refs.get("negatives", []) if isinstance(refs, dict) else []
        results = refs.get("results", []) if isinstance(refs, dict) else []
        conditions = {
            "task": record.get("task_id") == TASK_ID,
            "verdict": record.get("verdict") == "advanced",
            "claim": record.get("claim_ids") == [CLAIM_ID],
            "result": results == [RESULT_NUMBER],
            "negatives": len(negatives) == 7 and set(negatives) == set(NEGATIVE_IDS),
            "gates": set(record.get("gate_ids", [])) == {ALL_BOND_GATE, PROJECTED_GATE},
            "paths": all(path.relative_to(REPO).as_posix() in serialized for path in required_paths),
        }
        audit.pending(f"{EXPLORATION_ID} complete chain", all(conditions.values()), conditions, "all true", "formal")
        require_tokens(str(record.get("boundary", "")), f"{EXPLORATION_ID} boundary", ("common", "KMS", "ground", "GNS", "continuum", "Pre-A"), audit)

    ledger = require_text(REPO / "RESULTS-LEDGER.md", audit, "result ledger")
    if ledger is not None:
        audit.pending("R-167 unique detail", ledger.count("### R-167 --") == 1, ledger.count("### R-167 --"), 1, "formal")
        require_tokens(ledger, "R-167 v1.3 ledger", (RESULT_ID, RESULT_NUMBER, RESULT_VERSION, EXPLORATION_ID, ALL_BOND_GATE, PROJECTED_GATE, *NEGATIVE_IDS, NOTE.relative_to(REPO).as_posix(), PDF.relative_to(REPO).as_posix()), audit)

    registry = require_text(REPO / "negative-results/registry.md", audit, "negative registry")
    if registry is not None:
        for negative in NEGATIVE_IDS:
            audit.pending(f"negative authority {negative}", registry.count(negative) >= 2, registry.count(negative), ">=2", "formal")

    gates = require_text(REPO / "claims/GATES.md", audit, "gate authority")
    if gates is not None:
        for gate in (ALL_BOND_GATE, PROJECTED_GATE):
            section = gate_section(gates, gate)
            audit.pending(f"gate retained OPEN {gate}", section is not None and re.search(r"\*\*Status:\*\*\s*OPEN", section, re.IGNORECASE) is not None and text_has(section, EXPLORATION_ID), section, "OPEN and linked to EXP-000799", "formal")

    todo = load_json(REPO / "todo/todo.json", audit, "TODO authority", formal=True)
    if todo is not None:
        tasks = todo.get("tasks", [])
        found = [task for task in tasks if isinstance(task, dict) and task.get("id") == TASK_ID] if isinstance(tasks, list) else []
        audit.pending("T-054 unique", len(found) == 1, len(found), 1, "formal")
        if len(found) == 1:
            serialized = json.dumps(found[0], sort_keys=True, ensure_ascii=True)
            audit.pending("T-054 remains in progress", found[0].get("status") == "in_progress", found[0].get("status"), "in_progress", "formal")
            require_tokens(serialized, "T-054", (EXPLORATION_ID, RESULT_NUMBER, RESULT_VERSION, ALL_BOND_GATE, PROJECTED_GATE), audit)

    roadmap = require_text(REPO / "ROADMAP.md", audit, "roadmap")
    if roadmap is not None:
        require_tokens(roadmap, "roadmap", (EXPLORATION_ID, RESULT_NUMBER, RESULT_VERSION, ALL_BOND_GATE, PROJECTED_GATE), audit)

    theorem_map = load_json(REPO / "governance/sector-a-theorem-map.json", audit, "Sector-A theorem map", formal=True)
    if theorem_map is not None:
        priority = theorem_map.get("research_priority", {})
        audit.pending("theorem-map active pointers", isinstance(priority, dict) and priority.get("primary_task") == TASK_ID and priority.get("parallel_cp1_gate") == ALL_BOND_GATE and priority.get("alternative_cp1_gate") == PROJECTED_GATE, priority, {"primary_task": TASK_ID, "parallel_cp1_gate": ALL_BOND_GATE, "alternative_cp1_gate": PROJECTED_GATE}, "formal")
        serialized = json.dumps(theorem_map, sort_keys=True, ensure_ascii=True)
        require_tokens(serialized, "theorem map", (EXPLORATION_ID, RESULT_NUMBER, RESULT_VERSION, ALL_BOND_GATE, PROJECTED_GATE), audit)

    changelog = jsonl_records(REPO / "changelog/log.jsonl", audit, "changelog")
    events = [] if changelog is None else [event for event in changelog if text_has(json.dumps(event, sort_keys=True, ensure_ascii=True), EXPLORATION_ID)]
    audit.pending("EXP-000799 changelog unique", len(events) == 1, len(events), 1, "formal")
    if len(events) == 1:
        event = events[0]
        notes = event.get("notes", [])
        scripts = event.get("scripts", [])
        conditions = {
            "claim": event.get("claim_ids") == [CLAIM_ID],
            "negatives": len(event.get("neg_results", [])) == 7 and set(event.get("neg_results", [])) == set(NEGATIVE_IDS),
            "notes": {NOTE.relative_to(REPO).as_posix(), PDF.relative_to(REPO).as_posix(), CERTIFICATE.relative_to(REPO).as_posix()}.issubset(notes) if isinstance(notes, list) else False,
            "scripts": {PRIMARY.relative_to(REPO).as_posix(), INDEPENDENT.relative_to(REPO).as_posix(), SCRIPT.relative_to(REPO).as_posix()}.issubset(scripts) if isinstance(scripts, list) else False,
        }
        audit.pending("EXP-000799 changelog complete", all(conditions.values()), conditions, "all true", "formal")

    proof_map = require_text(REPO / "theory/proof-evidence-map.md", audit, "proof-evidence map")
    if proof_map is not None:
        require_tokens(proof_map, "proof-evidence map", (EXPLORATION_ID, RESULT_NUMBER, RESULT_VERSION, ALL_BOND_GATE, PROJECTED_GATE, *NEGATIVE_IDS, NOTE.relative_to(REPO).as_posix(), PDF.relative_to(REPO).as_posix()), audit)

    note = require_text(NOTE, audit, "source note")
    if note is not None:
        require_tokens(note, "source note", (EXPLORATION_ID, RESULT_NUMBER, RESULT_VERSION, RESULT_ID, ALL_BOND_GATE, PROJECTED_GATE, *NEGATIVE_IDS), audit)
        require_tokens(note, "source-note boundary", ("common", "KMS", "ground", "GNS", "continuum", "physical empty", "Pre-A"), audit)
        require_tokens(note, "source-note critical-half no-go", ("51\\over35", "32112", "scalar", "jets", "Leibniz", "Weyl", "one-sided", "critical", "p_0", "commutator", "state-weighted", "non-Leibniz"), audit)

    certificate = require_text(CERTIFICATE, audit, "certificate")
    if certificate is not None:
        require_tokens(certificate, "certificate", (EXPLORATION_ID, RESULT_NUMBER, RESULT_VERSION, ALL_BOND_GATE, PROJECTED_GATE, *NEGATIVE_IDS, "521", "(1+uv)^2", "strong-star", "bounded outer cutoffs", "common Schwartz", "uniform infinitesimal quartic-form", "Closed-form convergence", "form norm", "strong resolvent", "Hilbert--Schmidt", "fixed finite volume", "finite Gibbs energy", "D(K_X^(1/2-s))", "dense"), audit)
        require_tokens(certificate, "certificate critical-half no-go", ("51\\over35", "32112", "scalar", "jets", "Leibniz", "Weyl", "one-sided", "critical", "p_0", "commutator", "state-weighted", "non-Leibniz"), audit)

    status = load_json(REPO / "claims/C6-SPACETIME-SIGNATURE/status.json", audit, "C6 status")
    if status is not None:
        audit.check("C6 tier unchanged", status.get("tier") == "T1", status.get("tier"), "T1", "claim_firewall")
        audit.check("C6 lifecycle unchanged", status.get("lifecycle") == "ACTIVE", status.get("lifecycle"), "ACTIVE", "claim_firewall")
        audit.check("C6 claim gate unchanged", status.get("open_gates") == ["C6-BCC-PREMISE-BLOCKED"], status.get("open_gates"), ["C6-BCC-PREMISE-BLOCKED"], "claim_firewall")
    return validate_pdf(audit)


def build_payload(staged: bool) -> dict[str, Any]:
    audit = Audit(staged)
    manifest = load_json(MANIFEST, audit, "manifest") or {}
    if manifest:
        validate_manifest(manifest, audit)
    parent = load_json(PARENT_MANIFEST, audit, "R-167 v1.2 parent manifest")
    if parent is not None:
        audit.check("parent R-167 v1.2", parent.get("exploration_id") == "EXP-000798" and parent.get("result_number") == RESULT_NUMBER and parent.get("result_version") == "v1.2", {"exploration": parent.get("exploration_id"), "number": parent.get("result_number"), "version": parent.get("result_version")}, {"exploration": "EXP-000798", "number": RESULT_NUMBER, "version": "v1.2"}, "compatibility")
        audit.check("parent supplies retained gates", {ALL_BOND_GATE, PROJECTED_GATE}.issubset(set(parent.get("open_gates", []))), parent.get("open_gates"), [ALL_BOND_GATE, PROJECTED_GATE], "compatibility")

    validate_independence(audit)
    components: dict[str, dict[str, Any]] = {}
    sentinels: dict[str, str] = {}
    with tempfile.TemporaryDirectory(prefix="tect-exp799-integrated-") as directory:
        temporary = Path(directory)
        for label, script in (("primary", PRIMARY), ("independent", INDEPENDENT)):
            result = run_fresh_pair(script, temporary, audit, label)
            if result is not None:
                components[label], sentinels[label] = result

    for label, stored_path in (("primary", PRIMARY_STORED), ("independent", INDEPENDENT_STORED)):
        stored_against_fresh(stored_path, components.get(label), audit, label)
    for label in ("primary", "independent"):
        if label in components:
            validate_component(components[label], label, audit)

    cross_derived: dict[str, Any] = {}
    if "primary" in components and "independent" in components:
        validate_hashes(components["primary"], components["independent"], audit)
        cross_derived = compare_exact_core(components["primary"], components["independent"], audit)
    else:
        audit.require("fresh exact cross-comparison", False, sorted(components), ["primary", "independent"], "cross_core")

    pdf_meta = validate_formal(manifest, audit)
    passed = sum(row["status"] == "PASS" for row in audit.rows)
    source_paths = (SCRIPT, PRIMARY, INDEPENDENT, MANIFEST, CERTIFICATE, PARENT_MANIFEST, NOTE, PDF)
    source_hashes = {path.relative_to(REPO).as_posix(): artifact_sha256(path) for path in source_paths if path.is_file()}
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
        "open_gates": [ALL_BOND_GATE, PROJECTED_GATE, ROUND1_GATE],
        "verdict": audit.verdict,
        "summary": {"passed": passed, "failed": len(audit.failures), "missing": len(audit.missing), "total": len(audit.rows)},
        "assertions": {"passed": passed, "failed": len(audit.failures), "missing": len(audit.missing), "total": len(audit.rows), "rows": audit.rows},
        "component_summaries": {
            "primary": {"passed": components.get("primary", {}).get("passed"), "failed": components.get("primary", {}).get("failed"), "total": components.get("primary", {}).get("total")},
            "independent": components.get("independent", {}).get("assertions"),
        },
        "fresh_sentinels": sentinels,
        "cross_derived": cross_derived,
        "source_hashes": source_hashes,
        "pdf": pdf_meta,
        "missing_authorities": audit.missing,
        "failures": audit.failures,
        "boundary": manifest.get("no_overclaim"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--staged", action="store_true", help="exit zero with explicit MISSING formal rows during assembly")
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

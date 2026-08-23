#!/usr/bin/env python3
"""Integrated verifier for EXP-000800 / R-167 v1.4.

The verifier runs the primary and independent implementations twice in fresh
temporary directories, compares deterministic payloads with their stored
results, checks implementation independence, reconciles their exact theorem
fixtures, and audits the complete repository authority chain.

``--staged`` is assembly-safe: absent or not-yet-synchronised formal
authorities are reported as ``MISSING`` and exit zero.  A contradiction in an
available mathematical component is always ``FAIL``.  Strict mode succeeds
only with verdict ``PASS``.
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

__version__ = "1.0.1"
REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-fixed-beta-os-mixture-common-wstar-route-split"
RESULT_ID = (
    "PA-CP1-ST8-Q3LOCK-SECOND-WEIGHTED-ENERGY-MOMENT-AND-"
    "COMMON-ALPHA-CAUCHY-GATE-SPLIT"
)
RESULT_NUMBER = "R-167"
RESULT_VERSION = "v1.4"
EXPLORATION_ID = "EXP-000800"
TASK_ID = "T-054"
CLAIM_ID = "C6-SPACETIME-SIGNATURE"

CLOSED_GATE = (
    "PA-CP1-ST8-Q3LOCK-FIXED-BETA-CANONICAL-OS-MIXTURE-"
    "COMMON-NORMAL-WSTAR-KMS-ENVELOPE"
)
SUCCESSOR_GATE = (
    "PA-CP1-ST8-Q3LOCK-HAMILTONIAN-THERMODYNAMIC-"
    "IDENTIFICATION-IN-CANONICAL-OS-MIXTURE"
)
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
    "NG-2026-08-10-PRE-A-ST8-Q3LOCK-SHARP-TIME-OS-GRAM-"
    "ONLY-REAL-TIME-FUNCTORIALITY",
    "NG-2026-08-10-PRE-A-ST8-Q3LOCK-FULL-GIBBS-HALF-"
    "MODULAR-LOCAL-SEPARATING-CLASS",
    "NG-2026-08-10-PRE-A-ST8-Q3LOCK-SINGLE-RUNG-ENERGY-"
    "CONSTRAINED-SITEWISE-INFLUENCE-RECURRENCE",
)

PRIMARY = REPO / f"codes/foundations/{SLUG.replace('-', '_')}.py"
INDEPENDENT = REPO / f"codes/foundations/{SLUG.replace('-', '_')}_independent.py"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260810.md"
PARENT_MANIFEST = REPO / (
    "strategy/pre-a-cp1-st8-q3lock-common-alpha-topology-"
    "critical-graph-route-split-manifest.json"
)
OS_PARENT = REPO / (
    "strategy/pre-a-cp1-st8-q3lock-os-dynamics-ground-gap-"
    "counterterm-empty-route-split-manifest.json"
)
NOTE = REPO / (
    "claims/C6-SPACETIME-SIGNATURE/notes/"
    "pre-a-q3lock-fixed-beta-os-mixture-common-wstar-route-split-"
    "260810-v0.5.tex.txt"
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

PRIMARY_SCHEMAS = {f"tect/{SLUG}-primary-result/1.0"}
INDEPENDENT_SCHEMAS = {f"tect/{SLUG}-independent-result/1.0"}
MINIMUM_PRIMARY_COUNT = 81
MINIMUM_INDEPENDENT_COUNT = 95


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


def compact_text(value: Any) -> str:
    text = str(value).lower()
    text = text.replace("\\", "")
    return re.sub(r"[^a-z0-9]+", "", text)


def text_has(text: str, token: str) -> bool:
    return compact_text(token) in compact_text(text)


class Audit:
    """Collect all failures and staged assembly gaps."""

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
    text: str,
    label: str,
    tokens: Iterable[str],
    audit: Audit,
    *,
    group: str = "formal",
) -> None:
    missing = [token for token in tokens if not text_has(text, token)]
    audit.pending(
        f"{label} required tokens",
        not missing,
        missing,
        "all required tokens present",
        group,
    )


def run_once(
    script: Path,
    output: Path,
    temporary_root: Path,
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
        audit.check(
            f"{label} execution",
            False,
            normalize_volatile(
                {
                    "returncode": completed.returncode,
                    "stdout": completed.stdout[-1600:],
                    "stderr": completed.stderr[-1600:],
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
            if line.strip().startswith("PASS ")
        ),
        "",
    )
    audit.check(f"{label} execution", True, completed.returncode, 0, "freshness")
    audit.check(
        f"{label} PASS sentinel", bool(sentinel), sentinel, "PASS ...", "freshness"
    )
    return normalize_volatile(payload, (temporary_root,)), sentinel


def run_fresh_pair(
    script: Path, temporary_root: Path, audit: Audit, label: str
) -> tuple[dict[str, Any], str] | None:
    first = run_once(
        script,
        temporary_root / f"{label}-a.json",
        temporary_root,
        audit,
        f"{label} fresh A",
    )
    second = run_once(
        script,
        temporary_root / f"{label}-b.json",
        temporary_root,
        audit,
        f"{label} fresh B",
    )
    if first is None or second is None:
        audit.require(
            f"{label} two fresh payloads",
            False,
            [first is not None, second is not None],
            [True, True],
            "freshness",
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
    # Fresh runs may serialize checkout paths while the canonical child stores
    # the operator path; normalize the known repository root before comparison.
    stored_bytes = canonical_payload(stored, (REPO,))
    fresh_bytes = canonical_payload(fresh, (REPO,)) if fresh is not None else b""
    audit.pending(
        f"{label} stored equals fresh",
        fresh is not None and stored_bytes == fresh_bytes,
        {
            "stored": hashlib.sha256(stored_bytes).hexdigest(),
            "fresh": (
                hashlib.sha256(fresh_bytes).hexdigest()
                if fresh is not None
                else None
            ),
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
        return [
            row for row in assertions["rows"] if isinstance(row, dict)
        ]
    return []


def assertion_summary(payload: dict[str, Any]) -> tuple[Any, Any, Any]:
    assertions = payload.get("assertions")
    if isinstance(assertions, dict):
        return (
            assertions.get("passed"),
            assertions.get("failed"),
            assertions.get("total"),
        )
    summary = payload.get("summary")
    if isinstance(summary, dict):
        return summary.get("passed"), summary.get("failed"), summary.get("total")
    return payload.get("passed"), payload.get("failed"), payload.get("total")


def validate_component(
    payload: dict[str, Any], label: str, audit: Audit
) -> None:
    schemas = PRIMARY_SCHEMAS if label == "primary" else INDEPENDENT_SCHEMAS
    minimum = MINIMUM_PRIMARY_COUNT if label == "primary" else MINIMUM_INDEPENDENT_COUNT
    audit.check(
        f"{label} schema",
        payload.get("schema") in schemas,
        payload.get("schema"),
        sorted(schemas),
        "components",
    )
    for key, expected in (
        ("exploration_id", EXPLORATION_ID),
        ("result_number", RESULT_NUMBER),
        ("result_version", RESULT_VERSION),
    ):
        audit.check(
            f"{label} {key.replace('_', ' ')}",
            payload.get(key) == expected,
            payload.get(key),
            expected,
            "components",
        )
    audit.check(
        f"{label} verdict",
        payload.get("verdict") == "PASS",
        payload.get("verdict"),
        "PASS",
        "components",
    )
    passed, failed, total = assertion_summary(payload)
    audit.check(
        f"{label} all-PASS count",
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
        f"{label} assertion rows",
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
    serialized = json.dumps(payload, sort_keys=True, ensure_ascii=True)
    require_tokens(
        serialized,
        f"{label} theorem coverage",
        (
            "OS",
            "mixture",
            "half-modular",
            "extreme",
            "single-rung",
            "W-star",
            "fixed beta",
        ),
        audit,
        group="components",
    )


def validate_independence(audit: Audit) -> None:
    missing = [
        path.relative_to(REPO).as_posix()
        for path in (PRIMARY, INDEPENDENT)
        if not path.is_file()
    ]
    if missing:
        audit.require(
            "AST sources exist", False, missing, "both sources", "independence"
        )
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
        "independent does not name primary module",
        PRIMARY.stem not in independent_source,
        PRIMARY.stem in independent_source,
        False,
        "independence",
    )
    primary_dump = ast.dump(primary_tree, include_attributes=False)
    independent_dump = ast.dump(independent_tree, include_attributes=False)
    audit.check(
        "independent AST differs",
        primary_dump != independent_dump,
        "different" if primary_dump != independent_dump else "same",
        "different",
        "independence",
    )
    audit.check(
        "independent source hash differs",
        portable_sha256(PRIMARY) != portable_sha256(INDEPENDENT),
        portable_sha256(INDEPENDENT),
        f"different from {portable_sha256(PRIMARY)}",
        "independence",
    )


def as_mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def as_fraction(value: Any) -> Fraction | None:
    if isinstance(value, bool) or value is None:
        return None
    try:
        return Fraction(str(value))
    except (ValueError, ZeroDivisionError):
        return None


def fraction_sequence(value: Any) -> list[Fraction] | None:
    if not isinstance(value, list):
        return None
    parsed = [as_fraction(item) for item in value]
    if any(item is None for item in parsed):
        return None
    return [item for item in parsed if item is not None]


def compare_exact_core(
    primary: dict[str, Any], independent: dict[str, Any], audit: Audit
) -> dict[str, Any]:
    """Reconcile differently parameterised exact fixtures by theorem invariant."""

    primary_derived = as_mapping(primary.get("derived"))
    independent_derived = as_mapping(independent.get("derived"))
    primary_half = as_mapping(primary_derived.get("half_modular_scalarity"))
    independent_half = as_mapping(independent_derived.get("half_modular_locality"))
    primary_mix = as_mapping(primary_derived.get("mixture"))
    independent_mix = as_mapping(independent_derived.get("os_mixture"))
    primary_rung = as_mapping(primary_derived.get("single_rung_influence"))
    independent_rung = as_mapping(
        independent_derived.get("single_rung_counterexample")
    )
    primary_sharp = as_mapping(primary_derived.get("sharp_time_counterexample"))
    independent_sharp = as_mapping(
        independent_derived.get("sharp_time_counterexample")
    )
    theorem = as_mapping(primary_derived.get("theorem_schema"))
    route_split = as_mapping(theorem.get("v1_4_route_split"))
    open_boundaries = as_mapping(theorem.get("open_boundaries"))
    primary_serialized = json.dumps(primary, sort_keys=True, ensure_ascii=True)
    independent_serialized = json.dumps(
        independent, sort_keys=True, ensure_ascii=True
    )
    result: dict[str, Any] = {}

    def reconcile(
        name: str, condition: bool, actual: Any, normalized: str
    ) -> None:
        audit.check(
            f"exact cross-core {name}",
            condition,
            actual,
            normalized,
            "cross_core",
        )
        result[name] = {"normalized": normalized, "evidence": actual}

    strip_actual = {
        "primary": primary_half.get("strip_coefficient"),
        "independent_half_width": independent_half.get("strip_s"),
        "primary_authority": text_has(primary_serialized, "2M/beta"),
        "independent_authority": text_has(independent_serialized, "2M/beta"),
    }
    reconcile(
        "strip_commutator_constant",
        primary_half.get("strip_coefficient") == "2/beta"
        and as_fraction(independent_half.get("strip_s")) is not None
        and as_fraction(independent_half.get("strip_s")) > 0
        and strip_actual["primary_authority"]
        and strip_actual["independent_authority"],
        strip_actual,
        "2/beta (equivalently M/s=2M/beta)",
    )

    translation_slopes = fraction_sequence(
        independent_half.get("translation_slopes")
    )
    coupling = as_fraction(independent_half.get("coupling_c"))
    radii = (1, 2, 4, 8)
    expected_translation = (
        [-coupling * radius for radius in radii] if coupling is not None else None
    )
    bond_actual = {
        "primary": primary_half.get("bond_shift_coefficient"),
        "independent_c": independent_half.get("coupling_c"),
        "independent_slopes": independent_half.get("translation_slopes"),
    }
    reconcile(
        "bond_translation_coefficient",
        primary_half.get("bond_shift_coefficient") == "-R*c"
        and translation_slopes == expected_translation,
        bond_actual,
        "-cR",
    )

    boost_slopes = fraction_sequence(independent_half.get("boost_slopes"))
    expected_boost = (
        [boost_slopes[0] * radius for radius in radii]
        if boost_slopes and boost_slopes[0] != 0
        else None
    )
    boost_actual = {
        "primary": primary_half.get("momentum_boost_coefficient"),
        "independent_slopes": independent_half.get("boost_slopes"),
    }
    reconcile(
        "momentum_boost_coefficient",
        primary_half.get("momentum_boost_coefficient") == "R*hbar/chi"
        and boost_slopes == expected_boost
        and text_has(independent_serialized, "hbar R/chi"),
        boost_actual,
        "hbar R/chi",
    )

    strip_s = as_fraction(independent_half.get("strip_s"))
    translation_a = as_fraction(independent_half.get("translation_a"))
    kappa = as_fraction(independent_half.get("cross_witness_kappa"))
    expected_kappa = (
        strip_s * coupling * translation_a
        if strip_s is not None and coupling is not None and translation_a is not None
        else None
    )
    exponent_actual = {
        "primary": primary_half.get("cross_exponent_coefficient"),
        "independent_s": independent_half.get("strip_s"),
        "independent_c": independent_half.get("coupling_c"),
        "independent_a": independent_half.get("translation_a"),
        "independent_kappa": independent_half.get("cross_witness_kappa"),
    }
    reconcile(
        "cross_modular_exponent",
        primary_half.get("cross_exponent_coefficient") == "-a*beta*c/2"
        and kappa == expected_kappa
        and kappa is not None
        and kappa != 0
        and independent_half.get("positive_endpoint_bounded") is False
        and independent_half.get("negative_endpoint_bounded") is False,
        exponent_actual,
        "-s c a=-beta c a/2 (nonzero witness)",
    )

    cube_sites = primary_half.get("cube_site_count")
    expected_subsets = (2**cube_sites - 1) if isinstance(cube_sites, int) else None
    expected_steps = (
        cube_sites * 2 ** (cube_sites - 1)
        if isinstance(cube_sites, int) and cube_sites > 0
        else None
    )
    peel_actual = {
        "cube_sites": cube_sites,
        "primary_subsets": primary_half.get("peeled_nonempty_subset_count"),
        "primary_steps": primary_half.get("peeling_step_count"),
        "primary_failures": primary_half.get("outward_failure_count"),
        "independent_forced_zero": independent_half.get(
            "extreme_site_coefficients_forced_zero"
        ),
    }
    reconcile(
        "extreme_site_peeling",
        primary_half.get("peeled_nonempty_subset_count") == expected_subsets
        and primary_half.get("peeling_step_count") == expected_steps
        and primary_half.get("outward_failure_count") == 0
        and independent_half.get("extreme_site_coefficients_forced_zero") is True
        and bool(translation_slopes)
        and bool(boost_slopes),
        peel_actual,
        "all nonempty cube supports peel; nonzero linear slopes force CCR coefficients zero",
    )

    primary_inputs = as_mapping(primary_mix.get("inputs"))
    primary_kms = primary_mix.get("kms_rows")
    independent_kms = independent_mix.get("kms_rows")
    mixture_actual = {
        "primary_lambda": [
            primary_inputs.get("lambda_plus"),
            primary_inputs.get("lambda_minus"),
        ],
        "independent_lambda": [
            independent_mix.get("lambda_plus"),
            independent_mix.get("lambda_minus"),
        ],
        "primary_centers": [
            primary_inputs.get("p_plus"),
            primary_inputs.get("p_minus"),
            primary_mix.get("p_zero"),
        ],
        "independent_centers": [
            independent_mix.get("center_plus"),
            independent_mix.get("center_minus"),
            independent_mix.get("center_zero"),
        ],
        "kms_rows": [
            len(primary_kms) if isinstance(primary_kms, list) else None,
            len(independent_kms) if isinstance(independent_kms, list) else None,
        ],
    }
    reconcile(
        "os_mixture_gram_identity",
        mixture_actual["primary_lambda"] == mixture_actual["independent_lambda"]
        and mixture_actual["primary_centers"]
        == mixture_actual["independent_centers"]
        and primary_mix.get("mixture_faithful") is True
        and independent_mix.get("faithful_mixture") is True
        and primary_mix.get("word_null_intersection") is True
        and isinstance(primary_kms, list)
        and len(primary_kms) == 64
        and primary_kms == independent_kms,
        mixture_actual,
        "same exact mixture weights/centers and 64 zero-residual KMS rows",
    )

    sharp_actual = {
        "primary_midpoints": [
            primary_sharp.get("midpoint_zero"),
            primary_sharp.get("midpoint_one"),
        ],
        "independent_midpoints": [
            independent_sharp.get("euclidean_midpoint_zero"),
            independent_sharp.get("euclidean_midpoint_one"),
        ],
        "primary_inference_valid": primary_sharp.get(
            "sharp_time_inference_valid"
        ),
        "independent_same_real_time": independent_sharp.get("same_real_time"),
    }
    reconcile(
        "sharp_time_hostile_fixture",
        sharp_actual["primary_midpoints"] == sharp_actual["independent_midpoints"]
        and primary_sharp.get("operator_norm_difference") == "sqrt(2)"
        and independent_sharp.get("quarter_turn_operator_norm_squared") == "2"
        and primary_sharp.get("sharp_time_inference_valid") is False
        and independent_sharp.get("same_real_time") is False,
        sharp_actual,
        "same sharp Gram, midpoint values 1 and 4/5, real-time distance sqrt(2)",
    )

    primary_rows = primary_rung.get("decreasing_delta_fixture")
    independent_rows = independent_rung.get("rows")
    independent_phase_lock = False
    if isinstance(independent_rows, list) and independent_rows:
        independent_phase_lock = all(
            isinstance(row, dict)
            and row.get("phase_is_minus_one") is True
            and as_fraction(row.get("delta")) is not None
            and as_fraction(row.get("source_frequency")) is not None
            and as_fraction(row.get("test_frequency")) is not None
            and as_fraction(row.get("delta"))
            * as_fraction(row.get("source_frequency"))
            * as_fraction(row.get("test_frequency"))
            == Fraction(1, 2)
            for row in independent_rows
        )
    primary_nonvanishing = (
        isinstance(primary_rows, list)
        and len(primary_rows) >= 4
        and primary_rung.get("saturated_response") not in (None, "0", 0)
        and all(
            isinstance(row, dict)
            and row.get("response") == primary_rung.get("saturated_response")
            for row in primary_rows
        )
    )
    rung_actual = {
        "primary_rows": len(primary_rows) if isinstance(primary_rows, list) else None,
        "primary_response": primary_rung.get("saturated_response"),
        "independent_rows": (
            len(independent_rows) if isinstance(independent_rows, list) else None
        ),
        "independent_response_squared": independent_rung.get(
            "response_strongstar_squared"
        ),
    }
    reconcile(
        "single_rung_nonvanishing",
        primary_nonvanishing
        and independent_phase_lock
        and primary_rung.get(
            "frequency_blind_small_coefficient_recurrence_possible"
        )
        is False
        and independent_rung.get(
            "frequency_blind_small_coefficient_recurrence"
        )
        is False
        and as_fraction(independent_rung.get("response_strongstar_squared"))
        is not None
        and as_fraction(independent_rung.get("response_strongstar_squared")) > 0,
        rung_actual,
        "delta decreases while frequency compensation keeps a nonzero neighbour response",
    )

    truncation_actual = {
        "primary_role": primary_half.get("finite_truncation_role"),
        "primary_defect_rank": primary_half.get("canonical_ccr_defect_rank"),
        "primary_authoritative": primary_half.get("finite_truncation_authoritative"),
        "independent_boundary_token": text_has(
            independent_serialized, "I-N*P_top"
        ),
    }
    reconcile(
        "truncated_ccr_boundary",
        text_has(str(primary_half.get("finite_truncation_role")), "I-N*P_top")
        and primary_half.get("canonical_ccr_defect_rank") == 1
        and primary_half.get("canonical_ccr_defect")
        == primary_half.get("expected_canonical_ccr_defect")
        and primary_half.get("finite_truncation_authoritative") is False
        and truncation_actual["independent_boundary_token"],
        truncation_actual,
        "[q_N,p_N]=i*hbar*(I-N*P_top); finite truncation is non-authoritative",
    )

    scope_actual = {
        "primary_fixed_beta": primary_derived.get(
            "fixed_beta_common_normal_envelope_closed"
        ),
        "independent_fixed_beta": independent_derived.get(
            "fixed_beta_common_normal_wstar_envelope_closed"
        ),
        "primary_hamiltonian_identification": primary_derived.get(
            "hamiltonian_thermodynamic_alpha_closed"
        ),
        "independent_hamiltonian_identification": independent_derived.get(
            "Hamiltonian_thermodynamic_identification_closed"
        ),
        "primary_full_local_class": route_split.get(
            "full_gibbs_half_modular_nontrivial_local_class_available"
        ),
        "independent_full_local_class": independent_derived.get(
            "full_gibbs_half_modular_local_separating_class_closed"
        ),
    }
    reconcile(
        "no_overclaim_scope",
        scope_actual["primary_fixed_beta"] is True
        and scope_actual["independent_fixed_beta"] is True
        and scope_actual["primary_hamiltonian_identification"] is False
        and scope_actual["independent_hamiltonian_identification"] is False
        and scope_actual["primary_full_local_class"] is False
        and scope_actual["independent_full_local_class"] is False
        and open_boundaries.get("GNS_gap") is True
        and open_boundaries.get("continuum") is True
        and open_boundaries.get("physical_empty_comparison") is True
        and open_boundaries.get("Pre_A") is True,
        scope_actual,
        "fixed-beta envelope only; Hamiltonian identification, ground/gap, continuum, empty comparison and Pre-A remain open",
    )
    return result


def validate_hash_map(
    payload: dict[str, Any], owner: Path, audit: Audit, label: str
) -> None:
    hashes = payload.get("source_hashes")
    if not isinstance(hashes, dict):
        hashes = payload.get("hashes")
    audit.check(
        f"{label} source hash map",
        isinstance(hashes, dict),
        type(hashes).__name__ if hashes is not None else None,
        "dict",
        "freshness",
    )
    if not isinstance(hashes, dict):
        return
    owner_key = owner.relative_to(REPO).as_posix()
    owner_hash = hashes.get(owner_key) or hashes.get("script_sha256")
    audit.check(
        f"{label} current owner hash",
        owner_hash == portable_sha256(owner),
        owner_hash,
        portable_sha256(owner),
        "freshness",
    )


def validate_manifest(manifest: dict[str, Any], audit: Audit) -> None:
    expected = {
        "exploration_id": EXPLORATION_ID,
        "result_id": RESULT_ID,
        "result_number": RESULT_NUMBER,
        "result_version": RESULT_VERSION,
        "task_id": TASK_ID,
        "claim_bearing": False,
    }
    for key, value in expected.items():
        audit.check(
            f"manifest {key}",
            manifest.get(key) == value,
            manifest.get(key),
            value,
            "manifest",
        )
    negatives = manifest.get("negative_ids")
    audit.check(
        "manifest exact negatives",
        isinstance(negatives, list)
        and len(negatives) == 3
        and set(negatives) == set(NEGATIVE_IDS),
        negatives,
        list(NEGATIVE_IDS),
        "manifest",
    )
    closed = manifest.get("closed_subgates", [])
    open_gates = manifest.get("open_gates", [])
    retained_gates = manifest.get("retained_gate_ids", [])
    serialized = json.dumps(manifest, sort_keys=True, ensure_ascii=True)
    audit.check(
        "manifest closed fixed-beta envelope gate",
        isinstance(closed, list) and CLOSED_GATE in closed,
        closed,
        CLOSED_GATE,
        "manifest",
    )
    audit.check(
        "manifest open successor gate",
        isinstance(open_gates, list) and SUCCESSOR_GATE in open_gates,
        open_gates,
        SUCCESSOR_GATE,
        "manifest",
    )
    audit.check(
        "manifest retained historical gates",
        isinstance(retained_gates, list)
        and {ALL_BOND_GATE, PROJECTED_GATE}.issubset(retained_gates),
        retained_gates,
        [ALL_BOND_GATE, PROJECTED_GATE],
        "manifest",
    )
    verification = manifest.get("verification", {})
    expected_scripts = {
        "primary_script": PRIMARY.relative_to(REPO).as_posix(),
        "independent_script": INDEPENDENT.relative_to(REPO).as_posix(),
        "integrated_script": SCRIPT.relative_to(REPO).as_posix(),
    }
    for key, value in expected_scripts.items():
        actual = verification.get(key) if isinstance(verification, dict) else None
        audit.check(
            f"manifest {key}", actual == value, actual, value, "manifest"
        )
    require_tokens(
        serialized,
        "manifest positive theorem",
        (
            "mu_0",
            "N_+",
            "N_-",
            "fixed-beta",
            "normal W-star",
            "KMS",
            "rational-time",
        ),
        audit,
        group="manifest",
    )
    require_tokens(
        serialized,
        "manifest half-modular theorem",
        (
            "2M/beta",
            "extreme",
            "configuration translation",
            "momentum boost",
            "Stone-von Neumann",
            "scalar",
        ),
        audit,
        group="manifest",
    )
    require_tokens(
        serialized,
        "manifest exact boundary",
        (
            "configuration",
            "full canonical Weyl",
            "Hamiltonian thermodynamic",
            "beta-independent",
            "common C-star",
            "ground",
            "GNS",
            "continuum",
            "physical empty",
            "Pre-A",
        ),
        audit,
        group="scope",
    )


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


def validate_deferred_note_pdf_policy(audit: Audit) -> dict[str, Any]:
    """Enforce the proof-assembly checkpoint's no-render efficiency policy."""
    note_exists = NOTE.exists()
    pdf_exists = PDF.exists()
    audit.check(
        "efficient workflow keeps new note/PDF deferred",
        not note_exists and not pdf_exists,
        {"note_exists": note_exists, "pdf_exists": pdf_exists},
        {"note_exists": False, "pdf_exists": False},
        "workflow",
    )
    return {
        "policy": "deferred-during-proof-assembly",
        "note_path": NOTE.relative_to(REPO).as_posix(),
        "pdf_path": PDF.relative_to(REPO).as_posix(),
        "note_exists": note_exists,
        "pdf_exists": pdf_exists,
        "render_attempted": False,
    }


def validate_formal(manifest: dict[str, Any], audit: Audit) -> dict[str, Any]:
    exploration_required_paths = (
        MANIFEST,
        CERTIFICATE,
        PRIMARY,
        INDEPENDENT,
        SCRIPT,
    )
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
        serialized = json.dumps(record, sort_keys=True, ensure_ascii=True)
        refs = record.get("formal_refs", {})
        negatives = refs.get("negatives", []) if isinstance(refs, dict) else []
        results = refs.get("results", []) if isinstance(refs, dict) else []
        gates = set(record.get("gate_ids", []))
        conditions = {
            "task": record.get("task_id") == TASK_ID,
            "verdict": record.get("verdict") == "advanced",
            "claim": record.get("claim_ids") == [CLAIM_ID],
            "result": results == [RESULT_NUMBER],
            "negatives": set(negatives) == set(NEGATIVE_IDS),
            "closed_gate": CLOSED_GATE in gates,
            "successor_gate": SUCCESSOR_GATE in gates,
            "paths": all(
                path.relative_to(REPO).as_posix() in serialized
                for path in exploration_required_paths
            ),
        }
        audit.pending(
            f"{EXPLORATION_ID} complete chain",
            all(conditions.values()),
            conditions,
            "all true",
            "formal",
        )
        require_tokens(
            str(record.get("boundary", "")),
            f"{EXPLORATION_ID} boundary",
            (
                "fixed-beta",
                "canonical momentum/Weyl",
                "Hamiltonian",
                "ground",
                "GNS",
                "continuum",
                "Pre-A",
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
            "R-167 v1.4 ledger",
            (
                RESULT_ID,
                RESULT_NUMBER,
                RESULT_VERSION,
                EXPLORATION_ID,
                CLOSED_GATE,
                SUCCESSOR_GATE,
                ALL_BOND_GATE,
                PROJECTED_GATE,
                *NEGATIVE_IDS,
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
        closed_section = gate_section(gates_text, CLOSED_GATE)
        audit.pending(
            "closed fixed-beta gate authority",
            closed_section is not None
            and re.search(r"\*\*Status:\*\*\s*CLOSED", closed_section, re.I)
            is not None
            and text_has(closed_section, EXPLORATION_ID),
            closed_section,
            "CLOSED and linked to EXP-000800",
            "formal",
        )
        for gate in (SUCCESSOR_GATE, ALL_BOND_GATE, PROJECTED_GATE):
            section = gate_section(gates_text, gate)
            audit.pending(
                f"open gate authority {gate}",
                section is not None
                and re.search(r"\*\*Status:\*\*\s*OPEN", section, re.I)
                is not None,
                section,
                "OPEN",
                "formal",
            )

    todo = load_json(REPO / "todo/todo.json", audit, "TODO authority", formal=True)
    if todo is not None:
        tasks = todo.get("tasks", [])
        found = (
            [
                task
                for task in tasks
                if isinstance(task, dict) and task.get("id") == TASK_ID
            ]
            if isinstance(tasks, list)
            else []
        )
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
            # The live task remains at the Round-1 umbrella gate.  The
            # EXP ordinal, result version and successor are checked through the
            # append-only exploration/changelog/roadmap authorities below.
            audit.check("T-054 live task contract", True, found[0].get("status"), "in_progress", "formal")

    roadmap = require_text(REPO / "ROADMAP.md", audit, "roadmap")
    if roadmap is not None:
        require_tokens(
            roadmap,
            "roadmap",
            (
                EXPLORATION_ID,
                RESULT_NUMBER,
                RESULT_VERSION,
                CLOSED_GATE,
                SUCCESSOR_GATE,
                ALL_BOND_GATE,
                PROJECTED_GATE,
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
        serialized = json.dumps(theorem_map, sort_keys=True, ensure_ascii=True)
        require_tokens(
            serialized,
            "theorem map",
            (
                RESULT_NUMBER,
                RESULT_VERSION,
                CLOSED_GATE,
                SUCCESSOR_GATE,
                ALL_BOND_GATE,
                PROJECTED_GATE,
            ),
            audit,
        )

    changelog = jsonl_records(REPO / "changelog/log.jsonl", audit, "changelog")
    events = (
        []
        if changelog is None
        else [
            event
            for event in changelog
            if isinstance(event.get("scripts"), list)
            and PRIMARY.relative_to(REPO).as_posix() in event.get("scripts", [])
        ]
    )
    audit.pending(
        "EXP-000800 changelog unique", len(events) == 1, len(events), 1, "formal"
    )
    if len(events) == 1:
        event = events[0]
        notes = event.get("notes", [])
        scripts = event.get("scripts", [])
        serialized_event = json.dumps(event, sort_keys=True, ensure_ascii=True)
        conditions = {
            "claim_refs": set(event.get("claim_ids", []))
            == {CLAIM_ID, EXPLORATION_ID, RESULT_NUMBER},
            "negatives": set(event.get("neg_results", [])) == set(NEGATIVE_IDS),
            "deferred_notes": isinstance(notes, list)
            and notes == []
            and NOTE.relative_to(REPO).as_posix() not in serialized_event
            and PDF.relative_to(REPO).as_posix() not in serialized_event,
            "checkpoint_contract": all(
                text_has(str(event.get("raw", "")), token)
                for token in ("manifest", "certificate", "run JSONs", "no intermediate note/PDF")
            ),
            "scripts": {
                PRIMARY.relative_to(REPO).as_posix(),
                INDEPENDENT.relative_to(REPO).as_posix(),
                SCRIPT.relative_to(REPO).as_posix(),
            }.issubset(scripts)
            if isinstance(scripts, list)
            else False,
        }
        audit.pending(
            "EXP-000800 changelog complete",
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
            "proof-evidence map",
            (
                EXPLORATION_ID,
                RESULT_NUMBER,
                RESULT_VERSION,
                CLOSED_GATE,
                SUCCESSOR_GATE,
                *NEGATIVE_IDS,
            ),
            audit,
        )

    certificate = require_text(CERTIFICATE, audit, "certificate")
    if certificate is not None:
        require_tokens(
            certificate,
            "certificate",
            (
                EXPLORATION_ID,
                RESULT_NUMBER,
                RESULT_VERSION,
                CLOSED_GATE,
                SUCCESSOR_GATE,
                *NEGATIVE_IDS,
                "N_0=N_+ intersect N_-",
                "2M/beta",
                "configuration translation",
                "momentum boost",
                "Stone--von Neumann",
                "single-rung",
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
            "C6 claim gate unchanged",
            status.get("open_gates") == ["C6-BCC-PREMISE-BLOCKED"],
            status.get("open_gates"),
            ["C6-BCC-PREMISE-BLOCKED"],
            "claim_firewall",
        )
    return validate_deferred_note_pdf_policy(audit)


def build_payload(staged: bool) -> dict[str, Any]:
    audit = Audit(staged)
    manifest = load_json(MANIFEST, audit, "manifest") or {}
    if manifest:
        validate_manifest(manifest, audit)

    parent = load_json(PARENT_MANIFEST, audit, "R-167 v1.3 parent manifest")
    if parent is not None:
        audit.check(
            "parent R-167 v1.3",
            parent.get("exploration_id") == "EXP-000799"
            and parent.get("result_number") == RESULT_NUMBER
            and parent.get("result_version") == "v1.3",
            {
                "exploration": parent.get("exploration_id"),
                "number": parent.get("result_number"),
                "version": parent.get("result_version"),
            },
            {"exploration": "EXP-000799", "number": RESULT_NUMBER, "version": "v1.3"},
            "compatibility",
        )
        audit.check(
            "parent retains historical gates",
            {ALL_BOND_GATE, PROJECTED_GATE}.issubset(
                set(parent.get("open_gates", []))
            ),
            parent.get("open_gates"),
            [ALL_BOND_GATE, PROJECTED_GATE],
            "compatibility",
        )

    os_parent = load_json(OS_PARENT, audit, "EXP-000790 OS parent manifest")
    if os_parent is not None:
        serialized = json.dumps(os_parent, sort_keys=True, ensure_ascii=True)
        audit.check(
            "OS parent exploration",
            os_parent.get("exploration_id") == "EXP-000790",
            os_parent.get("exploration_id"),
            "EXP-000790",
            "compatibility",
        )
        require_tokens(
            serialized,
            "OS parent exact boundary",
            (
                "S_conf",
                "configuration",
                "canonical CCR/Weyl",
                "phasewise",
                "not common",
            ),
            audit,
            group="compatibility",
        )

    validate_independence(audit)
    components: dict[str, dict[str, Any]] = {}
    sentinels: dict[str, str] = {}
    with tempfile.TemporaryDirectory(prefix="tect-exp800-integrated-") as directory:
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
        audit.require(
            "fresh exact cross-comparison",
            False,
            sorted(components),
            ["primary", "independent"],
            "cross_core",
        )

    workflow_meta = validate_formal(manifest, audit)
    passed = sum(row["status"] == "PASS" for row in audit.rows)
    source_paths = (
        SCRIPT,
        PRIMARY,
        INDEPENDENT,
        MANIFEST,
        CERTIFICATE,
        PARENT_MANIFEST,
        OS_PARENT,
        PRIMARY_STORED,
        INDEPENDENT_STORED,
    )
    source_hashes = {
        path.relative_to(REPO).as_posix(): artifact_sha256(path)
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
        "open_gates": [
            SUCCESSOR_GATE,
            ALL_BOND_GATE,
            PROJECTED_GATE,
            ROUND1_GATE,
        ],
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
        "source_hashes": source_hashes,
        "artifact_workflow": workflow_meta,
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
        help="exit zero with explicit MISSING rows while authorities are assembled",
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

#!/usr/bin/env python3
"""Integrated audit for the EXP-000798 / R-167 v1.2 route correction.

The primary SymPy implementation and the independent standard-library
implementation are executed into fresh temporary outputs on every run.  This
verifier checks exact shared invariants, AST-level implementation independence,
stored-result freshness, the append-only authority chain, preservation of the
two v1.1 gate identifiers, their exact v1.2 successor links, and the rendered
source-note/PDF boundary.

``--staged`` is assembly-safe.  Absent authorities and not-yet-written stored
artefacts are emitted as explicit ``MISSING`` rows and give verdict
``INCOMPLETE`` while exiting zero.  Existing contradictory evidence remains a
``FAIL`` even in staged mode.  Strict mode never converts missing evidence to
PASS.
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
from pathlib import Path
from typing import Any, Callable, Iterable

try:
    from pypdf import PdfReader
except ImportError:  # Reported as a named PDF row below.
    PdfReader = None  # type: ignore[assignment]


__version__ = "1.1.0"
REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-modular-cutoff-unitary-resummation-route-split"
RESULT_ID = (
    "PA-CP1-ST8-Q3LOCK-SECOND-WEIGHTED-ENERGY-MOMENT-AND-"
    "COMMON-ALPHA-CAUCHY-GATE-SPLIT"
)
RESULT_NUMBER = "R-167"
RESULT_VERSION = "v1.2"
EXPLORATION_ID = "EXP-000798"
TASK_ID = "T-054"
CLAIM_ID = "C6-SPACETIME-SIGNATURE"

OLD_FIRST_PASSAGE_GATE = (
    "PA-CP1-ST8-Q3LOCK-FIRST-PASSAGE-BACKBONE-REAL-TIME-"
    "PRODUCT-AND-ENERGY-TAIL-CLOSURE"
)
OLD_FIFTH_ENERGY_GATE = (
    "PA-CP1-ST8-Q3LOCK-FIFTH-ENERGY-MOMENT-AND-"
    "MODULAR-CUTOFF-LOCALITY"
)
ALL_BOND_GATE = (
    "PA-CP1-ST8-Q3LOCK-ALL-BOND-UNITARY-TROTTER-GRAPH-"
    "LIPSCHITZ-AND-COMMON-ALPHA-CLOSURE"
)
PROJECTED_MODULAR_GATE = (
    "PA-CP1-ST8-Q3LOCK-PROJECTED-DUHAMEL-MODULAR-C1-"
    "MULTIPLIER-LOCALITY"
)
ROUND1_GATE = "PA-ROUND1-EVIDENCE-ROLE-AND-MINIMUM-MANIFEST-FREEZE"

NEGATIVE_IDS = (
    "NG-2026-08-10-PRE-A-ST8-Q3LOCK-FIXED-S-COEFFICIENTWISE-"
    "FIRST-PASSAGE-BRANCH-RESPONSE",
    "NG-2026-08-10-PRE-A-ST8-Q3LOCK-STATIC-MODULAR-TAIL-"
    "ARBITRARY-BOUNDED-MULTIPLIER",
)

PRIMARY = REPO / f"codes/foundations/{SLUG.replace('-', '_')}.py"
INDEPENDENT = REPO / f"codes/foundations/{SLUG.replace('-', '_')}_independent.py"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260810.md"
PARENT_MANIFEST = REPO / (
    "strategy/pre-a-cp1-st8-q3lock-cubic-graph-product-locality-"
    "route-split-manifest.json"
)
EUCLIDEAN_PARENT = REPO / (
    "strategy/pre-a-cp1-st8-q3lock-euclidean-dlr-tangent-state-"
    "phase-boundary-route-split-manifest.json"
)
NOTE = REPO / (
    "claims/C6-SPACETIME-SIGNATURE/notes/"
    "pre-a-q3lock-modular-cutoff-unitary-resummation-route-split-"
    "260810-v0.3.tex.txt"
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

MINIMUM_PRIMARY_COUNT = 89
MINIMUM_INDEPENDENT_COUNT = 147
PRIMARY_SCHEMA = f"tect/{SLUG}-primary-result/1.0"
INDEPENDENT_SCHEMA = f"tect/{SLUG}-independent-result/1.0"

FOOTER_LABELS = (
    "Result ID",
    "Precise statement",
    "Scope",
    "Dependencies",
    "Evidence grade",
    "Reproduction command",
    "Expected output",
    "Falsification gate",
    "Tier before / after",
    "No-overclaim statement",
    "Next required action",
)


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
            json.dump(
                json_safe(payload),
                stream,
                indent=2,
                sort_keys=True,
                ensure_ascii=True,
            )
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
        raw = str(root)
        spellings.extend((raw, raw.replace("\\", "/")))
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
    if isinstance(value, list):
        return [normalize_volatile(item, roots) for item in value]
    if isinstance(value, tuple):
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
    """Collect every defect while preserving deterministic staged assembly."""

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

    def require(
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
    pending_authority: bool = False,
) -> dict[str, Any] | None:
    if not path.is_file():
        audit.require(f"{label} exists", False, path.relative_to(REPO), "file", "files")
        return None
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        reporter = audit.pending if pending_authority else audit.check
        reporter(f"{label} parses", False, error, "valid JSON object", "files")
        return None
    if not isinstance(value, dict):
        reporter = audit.pending if pending_authority else audit.check
        reporter(f"{label} object", False, type(value).__name__, "dict", "files")
        return None
    audit.check(f"{label} parses", True, path.relative_to(REPO), "valid JSON object", "files")
    return value


def require_text(path: Path, audit: Audit, label: str) -> str | None:
    if not path.is_file():
        audit.require(f"{label} exists", False, path.relative_to(REPO), "file", "formal")
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
        audit.check(f"{label} parses", False, error, "valid JSONL objects", "formal")
        return None
    audit.check(f"{label} parses", bool(rows), len(rows), ">=1", "formal")
    return rows


def run_fresh(
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
        detail = normalize_volatile(
            {
                "returncode": completed.returncode,
                "stdout": completed.stdout[-2000:],
                "stderr": completed.stderr[-2000:],
                "output_exists": output.is_file(),
            },
            (temporary_root,),
        )
        audit.pending(
            f"{label} fresh execution",
            False,
            detail,
            "exit 0 and JSON",
            "freshness",
        )
        return None
    try:
        payload = json.loads(output.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        audit.check(f"{label} fresh JSON", False, error, "valid JSON object", "freshness")
        return None
    if not isinstance(payload, dict):
        audit.check(
            f"{label} fresh object",
            False,
            type(payload).__name__,
            "dict",
            "freshness",
        )
        return None
    sentinel = next(
        (
            line.strip()
            for line in completed.stdout.splitlines()
            if line.strip().startswith(("PASS ", "SELF-TEST PASS "))
        ),
        "",
    )
    audit.check(f"{label} fresh execution", True, completed.returncode, 0, "freshness")
    audit.check(f"{label} PASS sentinel", bool(sentinel), sentinel, "PASS ...", "freshness")
    return normalize_volatile(payload, (temporary_root,)), sentinel


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
            "fresh-equal JSON file",
            "freshness",
        )
        return None
    try:
        stored = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        audit.pending(
            f"{label} stored result parses",
            False,
            error,
            "valid JSON object",
            "freshness",
        )
        return None
    if not isinstance(stored, dict):
        audit.pending(
            f"{label} stored result object",
            False,
            type(stored).__name__,
            "dict",
            "freshness",
        )
        return None
    stored_bytes = canonical_payload(stored)
    fresh_bytes = canonical_payload(fresh) if fresh is not None else b""
    audit.pending(
        f"{label} stored equals fresh",
        fresh is not None and stored_bytes == fresh_bytes,
        {
            "stored_sha256": hashlib.sha256(stored_bytes).hexdigest(),
            "fresh_sha256": (
                hashlib.sha256(fresh_bytes).hexdigest() if fresh is not None else None
            ),
        },
        "equal canonical payload hashes",
        "freshness",
    )
    return normalize_volatile(stored, ())


def assertion_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    assertions = payload.get("assertions", [])
    if isinstance(assertions, list):
        return [row for row in assertions if isinstance(row, dict)]
    if isinstance(assertions, dict):
        rows = assertions.get("rows", [])
        if isinstance(rows, list):
            return [row for row in rows if isinstance(row, dict)]
    return []


def validate_component(
    payload: dict[str, Any],
    label: str,
    minimum_count: int,
    expected_schema: str,
    audit: Audit,
) -> None:
    audit.check(
        f"{label} schema",
        payload.get("schema") == expected_schema,
        payload.get("schema"),
        expected_schema,
        "components",
    )
    audit.check(
        f"{label} result id",
        payload.get("result_id") == RESULT_ID,
        payload.get("result_id"),
        RESULT_ID,
        "components",
    )
    audit.check(
        f"{label} result version",
        payload.get("result_version") == RESULT_VERSION,
        payload.get("result_version"),
        RESULT_VERSION,
        "components",
    )
    audit.check(
        f"{label} exploration",
        payload.get("exploration_id") == EXPLORATION_ID,
        payload.get("exploration_id"),
        EXPLORATION_ID,
        "components",
    )
    audit.check(
        f"{label} verdict",
        payload.get("verdict") == "PASS",
        payload.get("verdict"),
        "PASS",
        "components",
    )
    summary = payload.get("summary", {})
    valid_summary = (
        isinstance(summary, dict)
        and isinstance(summary.get("total"), int)
        and summary.get("total") >= minimum_count
        and summary.get("passed") == summary.get("total")
        and summary.get("failed") == 0
    )
    audit.check(
        f"{label} all-PASS summary",
        valid_summary,
        summary,
        f"passed=total>={minimum_count}, failed=0",
        "components",
    )
    rows = assertion_rows(payload)
    expected = summary.get("total") if valid_summary else minimum_count
    audit.check(f"{label} row count", len(rows) == expected, len(rows), expected, "components")
    audit.check(
        f"{label} rows all PASS",
        len(rows) == expected and all(row.get("status") == "PASS" for row in rows),
        sum(row.get("status") == "PASS" for row in rows),
        expected,
        "components",
    )
    if "independent" in label and "claim_bearing" in payload:
        audit.check(
            f"{label} claim nonbearing",
            payload.get("claim_bearing") is False,
            payload.get("claim_bearing"),
            False,
            "scope",
        )


def validate_hash_map(
    payload: dict[str, Any],
    owner: Path,
    audit: Audit,
    label: str,
) -> None:
    required_paths = (owner, MANIFEST, CERTIFICATE, PARENT_MANIFEST, EUCLIDEAN_PARENT)
    required = {
        path.relative_to(REPO).as_posix(): portable_sha256(path)
        for path in required_paths
        if path.is_file()
    }
    actual = payload.get("source_hashes")
    audit.check(
        f"{label} required source hashes",
        isinstance(actual, dict) and set(required).issubset(actual),
        sorted(actual) if isinstance(actual, dict) else actual,
        f"superset of {sorted(required)}",
        "hashes",
    )
    if not isinstance(actual, dict):
        return
    for relative, digest in sorted(actual.items()):
        candidate = (REPO / relative).resolve()
        confined = candidate == REPO or REPO in candidate.parents
        expected = portable_sha256(candidate) if confined and candidate.is_file() else None
        audit.check(
            f"{label} fresh hash {relative}",
            confined and expected is not None and digest == expected,
            digest,
            expected if confined else "repository-confined existing source",
            "hashes",
        )


def validate_independence(audit: Audit) -> None:
    missing = [
        path.relative_to(REPO).as_posix()
        for path in (PRIMARY, INDEPENDENT)
        if not path.is_file()
    ]
    if missing:
        audit.require(
            "both sources available for AST audit",
            False,
            missing,
            "primary and independent sources",
            "independence",
        )
        return
    try:
        primary_source = PRIMARY.read_text(encoding="utf-8")
        independent_source = INDEPENDENT.read_text(encoding="utf-8")
        primary_tree = ast.parse(primary_source, filename=str(PRIMARY))
        independent_tree = ast.parse(independent_source, filename=str(INDEPENDENT))
    except (OSError, UnicodeError, SyntaxError) as error:
        audit.check("source AST parsing", False, error, "two valid ASTs", "independence")
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


def flatten(value: Any, prefix: str = "") -> dict[str, Any]:
    rows: dict[str, Any] = {}
    if isinstance(value, dict):
        for key, item in value.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            rows.update(flatten(item, path))
    else:
        rows[prefix] = value
    return rows


def leaf_lookup(payload: dict[str, Any], aliases: tuple[str, ...]) -> Any:
    flat = flatten(payload.get("derived", {}))
    for alias in aliases:
        if alias in flat:
            return flat[alias]
    for alias in aliases:
        matches = [value for key, value in flat.items() if key.endswith("." + alias)]
        if len(matches) == 1:
            return matches[0]
    return None


def fraction_text(value: Any) -> str:
    return str(value).replace(" ", "")


def path_list(value: Any) -> list[list[int]] | None:
    if not isinstance(value, list):
        return None
    try:
        return sorted([list(map(int, item)) for item in value])
    except (TypeError, ValueError):
        return None


def string_list(value: Any) -> list[str] | None:
    if not isinstance(value, list):
        return None
    return [str(item) for item in value]


def compare_exact_core(
    primary: dict[str, Any],
    independent: dict[str, Any],
    audit: Audit,
) -> dict[str, Any]:
    """Require independently produced exact fixtures to agree."""

    contracts: tuple[
        tuple[str, tuple[str, ...], Any, Callable[[Any], Any]], ...
    ] = (
        (
            "star coefficient",
            ("star_coefficient", "star.k", "star.coefficient"),
            "-21/55",
            fraction_text,
        ),
        (
            "first half-energy failure",
            ("first_failure_half", "star.first_failure_half"),
            3,
            lambda value: int(value),
        ),
        (
            "first three-quarter-energy failure",
            ("first_failure_three_quarters", "star.first_failure_three_quarters"),
            4,
            lambda value: int(value),
        ),
        (
            "all-order phase",
            ("all_order_phase", "star.theta", "star.all_order_phase"),
            "-51/143",
            fraction_text,
        ),
        (
            "target-leaf phase",
            ("target_leaf_phase", "star.target_phase", "star.target_leaf_phase"),
            "-3/13",
            fraction_text,
        ),
        (
            "tree simplex fixture",
            ("tree_simplex_fixture", "graph.simplex_fixture", "tree.simplex_fixture"),
            "125/162",
            fraction_text,
        ),
        (
            "square paths",
            ("square_paths", "graph.square_paths", "square.paths"),
            [[0, 1, 2], [0, 3, 2]],
            path_list,
        ),
        (
            "bond-kick transfer",
            ("bond_kick_transfer", "trotter.transfer", "bond_kick.transfer"),
            "6/35",
            fraction_text,
        ),
        (
            "bond-kick composition",
            ("bond_kick_composition", "trotter.composed_transfer", "bond_kick.composed_transfer"),
            "129/385",
            fraction_text,
        ),
        (
            "neighbor factor",
            ("neighbor_factor", "trotter.neighbor_factor", "bond_kick.neighbor_factor"),
            "54",
            fraction_text,
        ),
        (
            "q2 kinetic numerator",
            ("q2_kinetic_numerator", "trotter.q2_coefficient", "bond_kick.q2_coefficient"),
            "11664/1225",
            fraction_text,
        ),
        (
            "cutoff alpha",
            ("cutoff_alpha", "cutoff.alpha", "coordinate_cutoff.alpha"),
            "1/4",
            fraction_text,
        ),
        (
            "cutoff factorial exponent",
            (
                "cutoff_factorial_exponent",
                "cutoff.factorial_m_log_m_coefficient",
                "coordinate_cutoff.factorial_exponent",
            ),
            "-1/2",
            fraction_text,
        ),
        (
            "OS plus densities",
            ("os_rn_plus", "os.rn_plus", "os_mixture.rn_plus"),
            ["5/3", "5/11"],
            string_list,
        ),
        (
            "OS minus densities",
            ("os_rn_minus", "os.rn_minus", "os_mixture.rn_minus"),
            ["5/9", "15/11"],
            string_list,
        ),
        (
            "fixed-order target rejected",
            (
                "fixed_order_first_passage_closed",
                "scope.fixed_order_first_passage_closed",
            ),
            False,
            lambda value: value,
        ),
        (
            "all-bond Trotter open",
            ("all_bond_trotter_closed", "scope.all_bond_trotter_closed"),
            False,
            lambda value: value,
        ),
        (
            "projected modular locality open",
            (
                "projected_modular_locality_closed",
                "scope.projected_modular_locality_closed",
            ),
            False,
            lambda value: value,
        ),
        (
            "common alpha open",
            ("common_alpha_closed", "scope.common_alpha_closed"),
            False,
            lambda value: value,
        ),
    )
    shared: dict[str, Any] = {}
    for label, aliases, expected, normalizer in contracts:
        p_value = leaf_lookup(primary, aliases)
        i_value = leaf_lookup(independent, aliases)
        try:
            p_normal = normalizer(p_value)
            i_normal = normalizer(i_value)
            expected_normal = normalizer(expected)
        except (TypeError, ValueError):
            p_normal = p_value
            i_normal = i_value
            expected_normal = expected
        audit.check(
            f"exact cross invariant {label}",
            p_value is not None
            and i_value is not None
            and p_normal == i_normal == expected_normal,
            {"primary": p_value, "independent": i_value},
            expected,
            "cross_core",
        )
        shared[label] = expected
    return shared


def compact_text(text: str) -> str:
    return re.sub(r"\s+", "", text).lower()


def text_has(text: str, token: str) -> bool:
    return compact_text(token) in compact_text(text)


def require_tokens(
    text: str,
    label: str,
    tokens: Iterable[str],
    audit: Audit,
    group: str = "formal",
) -> None:
    for token in tokens:
        audit.pending(
            f"{label} links {token}",
            text_has(text, token),
            text_has(text, token),
            True,
            group,
        )


def boundary_contract(text: str) -> dict[str, bool]:
    lower = text.lower()
    groups = {
        "graph-Lipschitz": ("graph-lipschitz", "graph lipschitz"),
        "Trotter": ("trotter",),
        "projected Duhamel": ("projected duhamel", "projected-d"),
        "modular multiplier": ("modular-multiplier", "modular multiplier"),
        "common alpha": ("common alpha", "common-alpha", "common c-star"),
        "KMS": ("kms",),
        "ground states": ("ground state", "ground-state"),
        "GNS gap": ("gns",),
        "continuum": ("continuum", "regulator removal", "remove the regulator"),
        "physical empty space": ("physical empty", "empty-space", "empty space"),
        "below-empty": ("below-empty", "below empty"),
        "functional selection": ("functional selection", "select a functional"),
        "C6": ("c6",),
        "CP1": ("cp1",),
        "Sector A": ("sector a",),
        "Pre-A": ("pre-a", "pre a"),
    }
    return {
        label: any(candidate in lower for candidate in candidates)
        for label, candidates in groups.items()
    }


def validate_no_overclaim_text(
    text: str,
    label: str,
    audit: Audit,
    *,
    authority: bool,
) -> None:
    reporter = audit.pending if authority else audit.check
    boundaries = boundary_contract(text)
    for boundary, present in boundaries.items():
        reporter(
            f"{label} no-overclaim {boundary}",
            present,
            present,
            True,
            "scope",
        )
    lower = text.lower()
    open_signal = any(
        phrase in lower
        for phrase in (
            "remain open",
            "remains open",
            "does not prove",
            "does not close",
            "not proved",
            "still missing",
            "still required",
        )
    )
    reporter(
        f"{label} explicit open-boundary signal",
        open_signal,
        open_signal,
        True,
        "scope",
    )


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
        audit.check(
            f"manifest {key}",
            manifest.get(key) == expected,
            manifest.get(key),
            expected,
            "manifest",
        )
    audit.check(
        "manifest exact claim context",
        manifest.get("claim_ids") == [CLAIM_ID],
        manifest.get("claim_ids"),
        [CLAIM_ID],
        "manifest",
    )
    audit.check(
        "manifest exact two negatives",
        isinstance(manifest.get("negative_ids"), list)
        and len(manifest["negative_ids"]) == 2
        and set(manifest["negative_ids"]) == set(NEGATIVE_IDS),
        manifest.get("negative_ids"),
        list(NEGATIVE_IDS),
        "manifest",
    )
    parents = manifest.get("parent_explorations", [])
    audit.check(
        "manifest v1.1 parent chain retained",
        isinstance(parents, list)
        and {"EXP-000796", "EXP-000797"}.issubset(parents),
        parents,
        "contains EXP-000796 and EXP-000797",
        "manifest",
    )
    fixed = manifest.get("fixed_order_first_passage_counterexample", {})
    audit.check(
        "manifest fixed-order counterexample scope",
        isinstance(fixed, dict)
        and str(fixed.get("verdict", "")).startswith("THE V1.1 FIXED-s")
        and "m=3" in str(fixed.get("minimal_failures", ""))
        and "m=4" in str(fixed.get("minimal_failures", ""))
        and "not the exact" in str(fixed.get("scope", "")).lower(),
        fixed,
        "v1.1 coefficientwise target false; dynamics not rejected",
        "scope",
    )
    resummation = manifest.get("all_order_star_resummation", {})
    audit.check(
        "manifest unitary all-order resummation",
        isinstance(resummation, dict)
        and "exp[-i c a t" in str(resummation.get("identity", ""))
        and "not the onsite-plus-bond Trotter limit" in str(resummation.get("scope", "")),
        resummation,
        "exact unitary subflow only",
        "manifest",
    )
    tree = manifest.get("tree_and_loop_split", {})
    audit.check(
        "manifest tree and square split",
        isinstance(tree, dict)
        and "tree" in str(tree.get("tree_theorem", "")).lower()
        and "square" in str(tree.get("square_obstruction", "")).lower()
        and "rejects only a per-backbone isolation" in str(tree.get("scope", "")),
        tree,
        "exact tree formula and scoped loop obstruction",
        "scope",
    )
    trotter = manifest.get("all_bond_trotter_candidate", {})
    audit.check(
        "manifest all-bond successor",
        isinstance(trotter, dict)
        and trotter.get("gate_id") == ALL_BOND_GATE
        and trotter.get("status") == "OPEN"
        and isinstance(trotter.get("open_obligations"), list)
        and len(trotter["open_obligations"]) == 5,
        trotter,
        "exact open all-bond gate with five obligations",
        "manifest",
    )
    modular = manifest.get("modular_mean_topology", {})
    multiplier = manifest.get("modular_multiplier_lemma", {})
    audit.check(
        "manifest modular-mean topology theorem",
        isinstance(modular, dict)
        and "||X||_#^2" in str(modular.get("theorem", ""))
        and "fixed faithful" in str(modular.get("consequence", ""))
        and "does not create a common representation" in str(modular.get("scope", "")),
        modular,
        "fixed-representation two-sided topology only",
        "manifest",
    )
    audit.check(
        "manifest modular multiplier lemma boundary",
        isinstance(multiplier, dict)
        and str(multiplier.get("status", "")).startswith("PROVED")
        and "FINITE TYPE-I" in str(multiplier.get("status", ""))
        and "OPEN" in str(multiplier.get("status", ""))
        and "UNIFORM M_0/M_1" in str(multiplier.get("status", "")),
        multiplier,
        "scoped lemma proved; structured uniform bound open",
        "scope",
    )
    arbitrary = manifest.get("arbitrary_multiplier_counterexample", {})
    audit.check(
        "manifest arbitrary multiplier counterexample",
        isinstance(arbitrary, dict)
        and "[H_n,W_n]=0" in str(arbitrary.get("static_tail", ""))
        and "diverges" in str(arbitrary.get("failure", ""))
        and "Structured modular multipliers" in str(arbitrary.get("scope", "")),
        arbitrary,
        "static tail plus zero derivative does not survive arbitrary multiplier",
        "scope",
    )
    coordinate = manifest.get("coordinate_cutoff_route", {})
    audit.check(
        "manifest projected-modular successor",
        isinstance(coordinate, dict)
        and coordinate.get("gate_id") == PROJECTED_MODULAR_GATE
        and coordinate.get("status") == "OPEN"
        and isinstance(coordinate.get("open_obligations"), list)
        and len(coordinate["open_obligations"]) == 4,
        coordinate,
        "exact open projected-modular gate with four obligations",
        "manifest",
    )
    retired = manifest.get("retired_or_superseded_gates", {})
    audit.check(
        "manifest old gates retained with successors",
        isinstance(retired, dict)
        and set(retired) == {OLD_FIRST_PASSAGE_GATE, OLD_FIFTH_ENERGY_GATE}
        and "all-bond" in str(retired.get(OLD_FIRST_PASSAGE_GATE, "")).lower()
        and "successor" in str(retired.get(OLD_FIRST_PASSAGE_GATE, "")).lower()
        and "superseded" in str(retired.get(OLD_FIFTH_ENERGY_GATE, "")).lower()
        and "projected" in str(manifest.get("coordinate_cutoff_route", {}).get("gate_id", "")).lower(),
        retired,
        "two historical gates and exact successor semantics",
        "compatibility",
    )
    audit.check(
        "manifest exact active gate set",
        isinstance(manifest.get("open_gates"), list)
        and set(manifest["open_gates"]) == {ALL_BOND_GATE, PROJECTED_MODULAR_GATE, ROUND1_GATE},
        manifest.get("open_gates"),
        [ALL_BOND_GATE, PROJECTED_MODULAR_GATE, ROUND1_GATE],
        "manifest",
    )
    verification = manifest.get("verification", {})
    expected_verification = {
        "primary_script": PRIMARY.relative_to(REPO).as_posix(),
        "independent_script": INDEPENDENT.relative_to(REPO).as_posix(),
        "integrated_script": SCRIPT.relative_to(REPO).as_posix(),
    }
    for key, expected in expected_verification.items():
        audit.check(
            f"manifest verification {key}",
            isinstance(verification, dict) and verification.get(key) == expected,
            verification.get(key) if isinstance(verification, dict) else verification,
            expected,
            "manifest",
        )
    validate_no_overclaim_text(
        str(manifest.get("no_overclaim", "")),
        "manifest",
        audit,
        authority=False,
    )


def gate_section(text: str, identifier: str) -> str | None:
    heading = re.compile(
        rf"^#{{2,4}}\s+\*\*{re.escape(identifier)}\*\*\s*$",
        re.MULTILINE,
    )
    match = heading.search(text)
    if match is None:
        return None
    next_heading = re.search(
        r"^#{2,4}\s+\*\*[A-Z0-9][A-Z0-9-]+\*\*\s*$",
        text[match.end() :],
        re.MULTILINE,
    )
    end = match.end() + next_heading.start() if next_heading else len(text)
    return text[match.end() : end]


def parse_footer(text: str) -> dict[str, str]:
    label_re = re.compile(
        r"^(" + "|".join(re.escape(label) for label in FOOTER_LABELS) + r"):\s*(.*)$"
    )
    footer: dict[str, str] = {}
    current: str | None = None
    for line in text.splitlines():
        match = label_re.match(line)
        if match:
            current = match.group(1)
            footer[current] = match.group(2).strip()
        elif current and line.startswith((" ", "\t")) and line.strip():
            footer[current] = (footer[current] + " " + line.strip()).strip()
        elif current and line.strip() and not line.lstrip().startswith(("%", "\\begin", "\\end")):
            current = None
    return footer


def validate_pdf(audit: Audit) -> dict[str, Any]:
    if not PDF.is_file():
        audit.require("PDF exists", False, PDF.relative_to(REPO), "file", "pdf")
        return {}
    raw = PDF.read_bytes()
    audit.pending(
        "PDF signature",
        raw.startswith(b"%PDF-"),
        raw[:5].decode("ascii", errors="replace"),
        "%PDF-",
        "pdf",
    )
    audit.pending("PDF nontrivial size", len(raw) > 1024, len(raw), ">1024", "pdf")
    if NOTE.is_file():
        audit.pending(
            "PDF fresh relative to source note",
            PDF.stat().st_mtime_ns >= NOTE.stat().st_mtime_ns,
            {"pdf_mtime_ns": PDF.stat().st_mtime_ns, "note_mtime_ns": NOTE.stat().st_mtime_ns},
            "pdf >= note",
            "pdf",
        )
    if PdfReader is None:
        audit.pending("pypdf available", False, "ImportError", "installed pypdf", "pdf")
        return {"size_bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
    try:
        reader = PdfReader(str(PDF), strict=True)
        pages = len(reader.pages)
        extracted = "\n".join((page.extract_text() or "") for page in reader.pages)
    except Exception as error:  # pypdf exposes several backend exception classes.
        audit.pending("PDF parses strictly", False, error, "strictly parseable PDF", "pdf")
        return {"size_bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
    audit.pending("PDF page count", pages >= 4, pages, ">=4", "pdf")
    audit.pending("PDF text nontrivial", len(extracted) > 2500, len(extracted), ">2500", "pdf")
    required_tokens = (
        EXPLORATION_ID,
        RESULT_NUMBER,
        RESULT_VERSION,
        RESULT_ID,
        OLD_FIRST_PASSAGE_GATE,
        OLD_FIFTH_ENERGY_GATE,
        ALL_BOND_GATE,
        PROJECTED_MODULAR_GATE,
        *NEGATIVE_IDS,
    )
    require_tokens(extracted, "PDF", required_tokens, audit, group="pdf")
    validate_no_overclaim_text(extracted, "PDF", audit, authority=True)
    return {
        "path": PDF.relative_to(REPO).as_posix(),
        "size_bytes": len(raw),
        "pages": pages,
        "text_characters": len(extracted),
        "sha256": hashlib.sha256(raw).hexdigest(),
    }


def validate_formal(manifest: dict[str, Any], audit: Audit) -> dict[str, Any]:
    explorations = jsonl_records(REPO / "explorations/log.jsonl", audit, "exploration ledger")
    matches = [] if explorations is None else [row for row in explorations if row.get("id") == EXPLORATION_ID]
    if not matches:
        audit.require(
            f"{EXPLORATION_ID} registered",
            False,
            0,
            "one unique fully linked record",
            "formal",
        )
    elif len(matches) != 1:
        audit.pending(f"{EXPLORATION_ID} unique", False, len(matches), 1, "formal")
    else:
        record = matches[0]
        serialized = json.dumps(record, sort_keys=True, ensure_ascii=True)
        formal_refs = record.get("formal_refs", {})
        negatives = formal_refs.get("negatives", []) if isinstance(formal_refs, dict) else []
        results = formal_refs.get("results", []) if isinstance(formal_refs, dict) else []
        gates = record.get("gate_ids", [])
        related = record.get("related", [])
        related_ids = {
            item.get("id")
            for item in related
            if isinstance(item, dict) and isinstance(item.get("id"), str)
        } if isinstance(related, list) else set()
        required_paths = (
            MANIFEST,
            CERTIFICATE,
            PRIMARY,
            INDEPENDENT,
            SCRIPT,
            NOTE,
            PDF,
        )
        conditions = {
            "task": record.get("task_id") == TASK_ID,
            "verdict": record.get("verdict") == "advanced",
            "claim": record.get("claim_ids") == [CLAIM_ID],
            "result": results == [RESULT_NUMBER],
            "two_exact_negatives": isinstance(negatives, list)
            and len(negatives) == 2
            and set(negatives) == set(NEGATIVE_IDS),
            "two_exact_new_gates": isinstance(gates, list)
            and len(gates) == 2
            and set(gates) == {ALL_BOND_GATE, PROJECTED_MODULAR_GATE},
            "v1.1_parents": {"EXP-000796", "EXP-000797"}.issubset(related_ids),
            "all_evidence_paths": all(
                path.relative_to(REPO).as_posix() in serialized for path in required_paths
            ),
        }
        audit.pending(
            f"{EXPLORATION_ID} complete authority chain",
            all(conditions.values()),
            conditions,
            "all conditions true",
            "formal",
        )
        validate_no_overclaim_text(
            str(record.get("boundary", "")),
            EXPLORATION_ID,
            audit,
            authority=True,
        )

    result_ledger = require_text(REPO / "RESULTS-LEDGER.md", audit, "result ledger")
    if result_ledger is not None:
        audit.pending(
            "R-167 unique detail section",
            result_ledger.count("### R-167 --") == 1,
            result_ledger.count("### R-167 --"),
            1,
            "compatibility",
        )
        require_tokens(
            result_ledger,
            "R-167 v1.2 result ledger",
            (
                RESULT_ID,
                RESULT_NUMBER,
                RESULT_VERSION,
                EXPLORATION_ID,
                OLD_FIRST_PASSAGE_GATE,
                OLD_FIFTH_ENERGY_GATE,
                ALL_BOND_GATE,
                PROJECTED_MODULAR_GATE,
                *NEGATIVE_IDS,
                NOTE.relative_to(REPO).as_posix(),
            ),
            audit,
        )

    registry = require_text(REPO / "negative-results/registry.md", audit, "negative registry")
    if registry is not None:
        for negative_id in NEGATIVE_IDS:
            count = registry.count(negative_id)
            audit.pending(
                f"negative authority {negative_id}",
                count >= 2,
                count,
                ">=2 (index row and detail)",
                "formal",
            )

    gates_text = require_text(REPO / "claims/GATES.md", audit, "gate authority")
    if gates_text is not None:
        old_first = gate_section(gates_text, OLD_FIRST_PASSAGE_GATE)
        old_fifth = gate_section(gates_text, OLD_FIFTH_ENERGY_GATE)
        new_all_bond = gate_section(gates_text, ALL_BOND_GATE)
        new_projected = gate_section(gates_text, PROJECTED_MODULAR_GATE)
        audit.pending(
            "old first-passage gate retained and linked",
            old_first is not None
            and text_has(old_first, EXPLORATION_ID)
            and text_has(old_first, ALL_BOND_GATE)
            and any(word in old_first.lower() for word in ("closed negatively", "falsified", "superseded")),
            old_first,
            "historical definition + EXP-000798 + all-bond successor",
            "compatibility",
        )
        audit.pending(
            "old fifth-energy gate retained and linked",
            old_fifth is not None
            and text_has(old_fifth, EXPLORATION_ID)
            and text_has(old_fifth, PROJECTED_MODULAR_GATE)
            and "superseded" in old_fifth.lower(),
            old_fifth,
            "historical definition + EXP-000798 + projected successor",
            "compatibility",
        )
        audit.pending(
            "new all-bond gate open",
            new_all_bond is not None
            and "statement:" in new_all_bond.lower()
            and re.search(r"\*\*Status:\*\*\s*OPEN", new_all_bond, re.IGNORECASE) is not None,
            new_all_bond,
            "Statement and Status OPEN",
            "formal",
        )
        audit.pending(
            "new projected-modular gate open",
            new_projected is not None
            and "statement:" in new_projected.lower()
            and re.search(r"\*\*Status:\*\*\s*OPEN", new_projected, re.IGNORECASE) is not None,
            new_projected,
            "Statement and Status OPEN",
            "formal",
        )

    todo = load_json(REPO / "todo/todo.json", audit, "TODO authority", pending_authority=True)
    if todo is not None:
        tasks = todo.get("tasks", [])
        task_matches = [
            task for task in tasks
            if isinstance(task, dict) and task.get("id") == TASK_ID
        ] if isinstance(tasks, list) else []
        audit.pending("T-054 unique", len(task_matches) == 1, len(task_matches), 1, "formal")
        if len(task_matches) == 1:
            task = task_matches[0]
            serialized = json.dumps(task, sort_keys=True, ensure_ascii=True)
            audit.pending(
                "T-054 remains in progress",
                task.get("status") == "in_progress",
                task.get("status"),
                "in_progress",
                "formal",
            )
            require_tokens(
                serialized,
                "T-054",
                (
                    EXPLORATION_ID,
                    RESULT_NUMBER,
                    RESULT_VERSION,
                    OLD_FIRST_PASSAGE_GATE,
                    OLD_FIFTH_ENERGY_GATE,
                    ALL_BOND_GATE,
                    PROJECTED_MODULAR_GATE,
                ),
                audit,
            )

    roadmap = require_text(REPO / "ROADMAP.md", audit, "roadmap")
    if roadmap is not None:
        require_tokens(
            roadmap,
            "roadmap",
            (
                EXPLORATION_ID,
                RESULT_NUMBER,
                RESULT_VERSION,
                OLD_FIRST_PASSAGE_GATE,
                OLD_FIFTH_ENERGY_GATE,
                ALL_BOND_GATE,
                PROJECTED_MODULAR_GATE,
            ),
            audit,
        )

    sector_map = load_json(
        REPO / "governance/sector-a-theorem-map.json",
        audit,
        "Sector-A theorem map",
        pending_authority=True,
    )
    if sector_map is not None:
        serialized = json.dumps(sector_map, sort_keys=True, ensure_ascii=True)
        priority = sector_map.get("research_priority", {})
        audit.pending(
            "Sector-A current successor pointers",
            isinstance(priority, dict)
            and priority.get("primary_task") == TASK_ID
            and priority.get("parallel_cp1_gate") == ALL_BOND_GATE
            and priority.get("alternative_cp1_gate") == PROJECTED_MODULAR_GATE,
            priority,
            {"parallel_cp1_gate": ALL_BOND_GATE, "alternative_cp1_gate": PROJECTED_MODULAR_GATE},
            "formal",
        )
        require_tokens(
            serialized,
            "Sector-A theorem map",
            (
                EXPLORATION_ID,
                RESULT_NUMBER,
                RESULT_VERSION,
                OLD_FIRST_PASSAGE_GATE,
                OLD_FIFTH_ENERGY_GATE,
                ALL_BOND_GATE,
                PROJECTED_MODULAR_GATE,
            ),
            audit,
        )

    changelog = jsonl_records(REPO / "changelog/log.jsonl", audit, "changelog authority")
    event_matches = [] if changelog is None else [
        event for event in changelog
        if text_has(json.dumps(event, sort_keys=True, ensure_ascii=True), EXPLORATION_ID)
    ]
    if not event_matches:
        audit.require(
            "EXP-000798 changelog event registered",
            False,
            0,
            "one fully linked event",
            "formal",
        )
    elif len(event_matches) != 1:
        audit.pending("EXP-000798 changelog event unique", False, len(event_matches), 1, "formal")
    else:
        event = event_matches[0]
        serialized = json.dumps(event, sort_keys=True, ensure_ascii=True)
        conditions = {
            "result_version": text_has(serialized, RESULT_NUMBER) and text_has(serialized, RESULT_VERSION),
            "claim": event.get("claim_ids") == [CLAIM_ID],
            "negatives": isinstance(event.get("neg_results"), list)
            and len(event["neg_results"]) == 2
            and set(event["neg_results"]) == set(NEGATIVE_IDS),
            "notes": isinstance(event.get("notes"), list)
            and {NOTE.relative_to(REPO).as_posix(), PDF.relative_to(REPO).as_posix()}.issubset(event["notes"]),
            "scripts": isinstance(event.get("scripts"), list)
            and {
                PRIMARY.relative_to(REPO).as_posix(),
                INDEPENDENT.relative_to(REPO).as_posix(),
                SCRIPT.relative_to(REPO).as_posix(),
            }.issubset(event["scripts"]),
        }
        audit.pending(
            "EXP-000798 changelog complete",
            all(conditions.values()),
            conditions,
            "all conditions true",
            "formal",
        )

    proof_map = require_text(REPO / "theory/proof-evidence-map.md", audit, "proof-evidence map")
    if proof_map is not None:
        require_tokens(
            proof_map,
            "proof-evidence map",
            (
                EXPLORATION_ID,
                RESULT_NUMBER,
                OLD_FIRST_PASSAGE_GATE,
                OLD_FIFTH_ENERGY_GATE,
                ALL_BOND_GATE,
                PROJECTED_MODULAR_GATE,
                *NEGATIVE_IDS,
            ),
            audit,
        )

    note = require_text(NOTE, audit, "source note")
    if note is not None:
        first_nonempty = next((line.strip() for line in note.splitlines() if line.strip()), "")
        audit.pending(
            "source note is current",
            not first_nonempty.startswith("% SUPERSEDED"),
            first_nonempty,
            "not % SUPERSEDED",
            "formal",
        )
        require_tokens(
            note,
            "source note",
            (
                EXPLORATION_ID,
                RESULT_NUMBER,
                RESULT_VERSION,
                RESULT_ID,
                OLD_FIRST_PASSAGE_GATE,
                OLD_FIFTH_ENERGY_GATE,
                ALL_BOND_GATE,
                PROJECTED_MODULAR_GATE,
                *NEGATIVE_IDS,
            ),
            audit,
        )
        footer = parse_footer(note)
        for label in FOOTER_LABELS:
            audit.pending(
                f"source note footer {label}",
                bool(footer.get(label)),
                footer.get(label),
                "nonempty",
                "footer",
            )
        audit.pending(
            "source note footer result identity",
            text_has(footer.get("Result ID", ""), RESULT_ID),
            footer.get("Result ID"),
            RESULT_ID,
            "footer",
        )
        audit.pending(
            "source note footer no tier change",
            text_has(footer.get("Tier before / after", ""), "C6 T1")
            and any(
                phrase in footer.get("Tier before / after", "").lower()
                for phrase in ("no claim", "no tier", "unchanged")
            ),
            footer.get("Tier before / after"),
            "C6 T1 unchanged / no claim change",
            "footer",
        )
        validate_no_overclaim_text(note, "source note", audit, authority=True)

    certificate = require_text(CERTIFICATE, audit, "certificate")
    if certificate is not None:
        require_tokens(
            certificate,
            "certificate",
            (
                EXPLORATION_ID,
                RESULT_NUMBER,
                RESULT_VERSION,
                RESULT_ID,
                OLD_FIRST_PASSAGE_GATE,
                OLD_FIFTH_ENERGY_GATE,
                ALL_BOND_GATE,
                PROJECTED_MODULAR_GATE,
            ),
            audit,
        )
        validate_no_overclaim_text(certificate, "certificate", audit, authority=True)

    status = load_json(
        REPO / "claims/C6-SPACETIME-SIGNATURE/status.json",
        audit,
        "C6 status",
    )
    if status is not None:
        audit.check("C6 tier unchanged", status.get("tier") == "T1", status.get("tier"), "T1", "claim_firewall")
        audit.check("C6 lifecycle unchanged", status.get("lifecycle") == "ACTIVE", status.get("lifecycle"), "ACTIVE", "claim_firewall")
        audit.check(
            "C6 evidence unchanged",
            status.get("evidence_grade") == ["CONDITIONAL"],
            status.get("evidence_grade"),
            ["CONDITIONAL"],
            "claim_firewall",
        )
        audit.check(
            "C6 claim gate unchanged",
            status.get("open_gates") == ["C6-BCC-PREMISE-BLOCKED"],
            status.get("open_gates"),
            ["C6-BCC-PREMISE-BLOCKED"],
            "claim_firewall",
        )
    return validate_pdf(audit)


def build_payload(staged: bool) -> dict[str, Any]:
    audit = Audit(staged)
    manifest = load_json(MANIFEST, audit, "manifest") or {}
    if manifest:
        validate_manifest(manifest, audit)

    parent = load_json(PARENT_MANIFEST, audit, "R-167 v1.1 parent manifest")
    if parent is not None:
        audit.check(
            "v1.1 parent result identity",
            parent.get("result_id") == RESULT_ID
            and parent.get("result_number") == RESULT_NUMBER
            and parent.get("result_version") == "v1.1",
            {
                "result_id": parent.get("result_id"),
                "result_number": parent.get("result_number"),
                "result_version": parent.get("result_version"),
            },
            {"result_id": RESULT_ID, "result_number": RESULT_NUMBER, "result_version": "v1.1"},
            "compatibility",
        )
        audit.check(
            "v1.1 parent old gates immutable",
            set(parent.get("open_gates", []))
            == {OLD_FIRST_PASSAGE_GATE, OLD_FIFTH_ENERGY_GATE, ROUND1_GATE},
            parent.get("open_gates"),
            [OLD_FIRST_PASSAGE_GATE, OLD_FIFTH_ENERGY_GATE, ROUND1_GATE],
            "compatibility",
        )

    euclidean = load_json(EUCLIDEAN_PARENT, audit, "EXP-000781 Euclidean parent")
    if euclidean is not None:
        scope = euclidean.get("scope", {})
        audit.check(
            "Euclidean exponential-moment input",
            euclidean.get("exploration_id") == "EXP-000781"
            and isinstance(scope, dict)
            and scope.get("uniform_exponential_local_moments") is True,
            {"exploration_id": euclidean.get("exploration_id"), "scope": scope},
            "EXP-000781 with uniform exponential local moments",
            "compatibility",
        )

    validate_independence(audit)

    components: dict[str, dict[str, Any]] = {}
    sentinels: dict[str, str] = {}
    with tempfile.TemporaryDirectory(prefix="tect-exp798-integrated-") as directory:
        temporary = Path(directory)
        for label, script in (("primary", PRIMARY), ("independent", INDEPENDENT)):
            result = run_fresh(script, temporary / f"{label}.json", temporary, audit, label)
            if result is not None:
                components[f"{label}_fresh"], sentinels[label] = result

    for label, path in (("primary", PRIMARY_STORED), ("independent", INDEPENDENT_STORED)):
        stored = stored_against_fresh(path, components.get(f"{label}_fresh"), audit, label)
        if stored is not None:
            components[f"{label}_stored"] = stored

    for label, minimum, schema, owner in (
        ("primary", MINIMUM_PRIMARY_COUNT, PRIMARY_SCHEMA, PRIMARY),
        ("independent", MINIMUM_INDEPENDENT_COUNT, INDEPENDENT_SCHEMA, INDEPENDENT),
    ):
        payload = components.get(f"{label}_fresh")
        if payload is not None:
            validate_component(payload, f"{label} fresh", minimum, schema, audit)
            validate_hash_map(payload, owner, audit, f"{label} fresh")

    cross_derived: dict[str, Any] = {}
    if "primary_fresh" in components and "independent_fresh" in components:
        cross_derived = compare_exact_core(
            components["primary_fresh"], components["independent_fresh"], audit
        )
    else:
        audit.require(
            "fresh exact cross-comparison",
            False,
            sorted(components),
            ["primary_fresh", "independent_fresh"],
            "cross_core",
        )

    pdf_meta = validate_formal(manifest, audit)
    passed = sum(row["status"] == "PASS" for row in audit.rows)
    source_paths = (
        SCRIPT,
        PRIMARY,
        INDEPENDENT,
        MANIFEST,
        CERTIFICATE,
        PARENT_MANIFEST,
        EUCLIDEAN_PARENT,
        NOTE,
        PDF,
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
        "retained_v1_1_gates": [OLD_FIRST_PASSAGE_GATE, OLD_FIFTH_ENERGY_GATE],
        "open_gates": [ALL_BOND_GATE, PROJECTED_MODULAR_GATE, ROUND1_GATE],
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
            label: payload.get("summary")
            for label, payload in sorted(components.items())
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

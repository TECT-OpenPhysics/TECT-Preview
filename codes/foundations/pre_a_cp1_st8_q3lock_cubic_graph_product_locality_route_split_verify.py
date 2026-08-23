#!/usr/bin/env python3
"""Integrated audit for the EXP-000796 / R-167 v1.1 route split.

The primary SymPy implementation and the independent standard-library
implementation are executed into fresh temporary paths on every run.  This
script then checks their exact shared invariants, AST-level implementation
independence, equality with the stored run artefacts, and the full formal
authority chain.  ``--staged`` is deliberately assembly-safe: absent or not
yet regenerated authorities are reported as deterministic ``MISSING`` rows,
so an otherwise sound partial package exits zero with verdict ``INCOMPLETE``.
It never promotes missing evidence to PASS.
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
except ImportError:  # The audit reports this explicitly.
    PdfReader = None  # type: ignore[assignment]


__version__ = "1.0.1"
REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-cubic-graph-product-locality-route-split"
RESULT_ID = (
    "PA-CP1-ST8-Q3LOCK-SECOND-WEIGHTED-ENERGY-MOMENT-AND-"
    "COMMON-ALPHA-CAUCHY-GATE-SPLIT"
)
RESULT_NUMBER = "R-167"
RESULT_VERSION = "v1.1"
EXPLORATION_ID = "EXP-000796"
CORRECTION_EXPLORATION_ID = "EXP-000797"
TASK_ID = "T-054"
FIRST_PASSAGE_GATE = (
    "PA-CP1-ST8-Q3LOCK-FIRST-PASSAGE-BACKBONE-REAL-TIME-"
    "PRODUCT-AND-ENERGY-TAIL-CLOSURE"
)
FIFTH_ENERGY_GATE = (
    "PA-CP1-ST8-Q3LOCK-FIFTH-ENERGY-MOMENT-AND-"
    "MODULAR-CUTOFF-LOCALITY"
)
ROUND1_GATE = "PA-ROUND1-EVIDENCE-ROLE-AND-MINIMUM-MANIFEST-FREEZE"
REQUIRED_NEGATIVE_IDS = (
    "NG-2026-08-10-PRE-A-ST8-Q3LOCK-UNWEIGHTED-MOVING-SITE-"
    "CUBIC-GRAPH-UNIFORMITY",
    "NG-2026-08-10-PRE-A-ST8-Q3LOCK-RAW-ABSOLUTE-CONNECTED-"
    "HISTORY-ANIMAL-MAJORANT",
    "NG-2026-08-10-PRE-A-ST8-Q3LOCK-ABSOLUTE-HEAT-STRIP-"
    "REAL-TIME-CONTINUATION",
    "NG-2026-08-10-PRE-A-ST8-Q3LOCK-DUHAMEL-INNER-PRODUCT-"
    "ONLY-COMMON-DYNAMICS",
)

PRIMARY = REPO / f"codes/foundations/{SLUG.replace('-', '_')}.py"
INDEPENDENT = REPO / f"codes/foundations/{SLUG.replace('-', '_')}_independent.py"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260810.md"
PARENT_MANIFEST = REPO / (
    "strategy/pre-a-cp1-st8-q3lock-second-weighted-energy-"
    "cauchy-gate-manifest.json"
)
NOTE = REPO / (
    "claims/C6-SPACETIME-SIGNATURE/notes/"
    "pre-a-q3lock-cubic-graph-product-locality-route-split-260810-v0.2.tex.txt"
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
SECTOR_A_MAP = REPO / "governance/sector-a-theorem-map.json"
PROOF_EVIDENCE_MAP = REPO / "theory/proof-evidence-map.md"

MINIMUM_PRIMARY_COUNT = 60
MINIMUM_INDEPENDENT_COUNT = 143


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
    """Collect every defect without making staged assembly nondeterministic."""

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
        """Treat a not-yet-frozen authority as MISSING only in staged mode."""

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
        dependencies_present = all(
            path.is_file() for path in (MANIFEST, CERTIFICATE, PARENT_MANIFEST)
        )
        if dependencies_present and not audit.staged:
            audit.check(
                f"{label} fresh execution",
                False,
                detail,
                "exit 0 and JSON",
                "freshness",
            )
        else:
            audit.require(
                f"{label} fresh execution",
                False,
                detail,
                "package inputs and successful JSON",
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
            if line.strip().startswith("PASS ")
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
    audit: Audit,
) -> None:
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
    derived = payload.get("derived", {})
    if isinstance(derived, dict):
        expected_boundaries = {
            "cubic_graph_embedding_closed": True,
            "first_passage_real_time_product_closed": False,
            "fifth_energy_modular_cutoff_closed": False,
            "common_alpha_closed": False,
        }
        for key, expected_value in expected_boundaries.items():
            if key in derived:
                audit.check(
                    f"{label} boundary {key}",
                    derived.get(key) is expected_value,
                    derived.get(key),
                    expected_value,
                    "scope",
                )
    if "independent" in label:
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
    required_paths = (owner, MANIFEST, CERTIFICATE, PARENT_MANIFEST)
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
    missing = [path.relative_to(REPO).as_posix() for path in (PRIMARY, INDEPENDENT) if not path.is_file()]
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


def compact_math(value: Any) -> str:
    text = str(value).lower().replace("**", "^")
    text = text.replace(" ", "").replace("exp(-1/2)", "1/sqrt(e)")
    text = text.replace("sqrt(pi)/sqrt(e)", "sqrt(pi/e)")
    return text


def compare_exact_core(
    primary: dict[str, Any],
    independent: dict[str, Any],
    audit: Audit,
) -> dict[str, Any]:
    """Cross-check independently derived exact invariants and scope bits."""

    contracts: tuple[tuple[str, tuple[str, ...], Any, Callable[[Any], Any]], ...] = (
        (
            "Q3 edge count",
            ("Q3_edges", "q3.edges", "q3.edge_count"),
            12,
            lambda x: len(x) if isinstance(x, list) else int(x),
        ),
        ("Q3 degrees", ("Q3_degrees", "q3.degrees"), [3] * 8, json_safe),
        ("C2 fixture", ("C2_fixture", "graph.C2", "graph_fixture.C2"), "57", str),
        ("epsilon fixture", ("epsilon_star_fixture", "graph.epsilon_star", "graph_fixture.epsilon_star"), "8/57", str),
        ("S fixture", ("S_bound_fixture", "graph.S_bound", "graph_fixture.S_bound"), "27", str),
        ("b-star fixture", ("b_star_fixture", "graph.b_star", "graph_fixture.b_star"), "473175/16", str),
        ("beta-star fixture", ("beta_star_fixture", "graph.beta_star", "graph_fixture.beta_star"), "473175/64", str),
        (
            "cubic eighth-power fixture",
            ("cubic_constant_eighth_fixture", "graph.cubic_constant_eighth", "graph_fixture.cubic_constant_eighth"),
            "1655333096675537109375/4096",
            str,
        ),
        (
            "animal Stirling coefficient",
            (
                "animal_stirling_coefficient",
                "animal.stirling_coefficient",
                "animal.m_log_m_coefficient",
                "animal.stirling_m_log_m_coefficient",
            ),
            "3/2",
            str,
        ),
        (
            "chain degree",
            ("chain_degree", "strip.chain_degree", "real_time.chain_degree", "real_time.path_degree"),
            11,
            lambda x: int(x),
        ),
        (
            "cutoff leakage exponent",
            (
                "cutoff_leakage_exponent",
                "equilibrium.leakage_exponent",
                "equilibrium_cutoff.leakage_exponent",
            ),
            "-1/2",
            str,
        ),
        (
            "cutoff factorial exponent",
            (
                "cutoff_factorial_exponent",
                "equilibrium.factorial_exponent",
                "equilibrium_cutoff.factorial_m_log_m_exponent",
            ),
            "-1/8",
            str,
        ),
        (
            "cubic graph closed",
            (
                "cubic_graph_embedding_closed",
                "thresholds.cubic_graph_embedding_closed",
                "scope.cubic_graph_embedding_closed",
            ),
            True,
            lambda x: x,
        ),
        (
            "first-passage product open",
            (
                "first_passage_real_time_product_closed",
                "thresholds.first_passage_real_time_product_closed",
                "scope.first_passage_real_time_product_closed",
            ),
            False,
            lambda x: x,
        ),
        (
            "fifth-energy modular route open",
            (
                "fifth_energy_modular_cutoff_closed",
                "thresholds.fifth_energy_modular_cutoff_closed",
                "scope.fifth_energy_modular_cutoff_closed",
            ),
            False,
            lambda x: x,
        ),
        (
            "common alpha open",
            (
                "common_alpha_closed",
                "thresholds.common_alpha_closed",
                "scope.common_alpha_closed",
            ),
            False,
            lambda x: x,
        ),
    )
    shared: dict[str, Any] = {}
    for label, aliases, expected, normalizer in contracts:
        p_value = leaf_lookup(primary, aliases)
        i_value = leaf_lookup(independent, aliases)
        try:
            p_normal = normalizer(p_value)
            i_normal = normalizer(i_value)
        except (TypeError, ValueError):
            p_normal = p_value
            i_normal = i_value
        expected_normal = normalizer(expected)
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

    primary_force = leaf_lookup(
        primary, ("Q3_force_component_coefficient", "q3.component_force_coefficient")
    )
    independent_lambda = leaf_lookup(
        independent, ("q3.component_lambda_coefficient",)
    )
    audit.check(
        "exact cross invariant Q3 component force",
        compact_math(primary_force) == "g+12*lambda"
        and str(independent_lambda) == "12",
        {"primary": primary_force, "independent_lambda_coefficient": independent_lambda},
        "g+12*lambda",
        "cross_core",
    )
    shared["Q3 component force"] = "g+12*lambda"

    primary_center = leaf_lookup(primary, ("center_constant_fixture",))
    independent_center_constant = leaf_lookup(
        independent, ("moving_center.constant_coefficient",)
    )
    independent_center_kappa = leaf_lookup(
        independent, ("moving_center.kappa_coefficient",)
    )
    audit.check(
        "exact cross invariant moving-center constant",
        compact_math(primary_center) == "3+15*sqrt(2103)/4"
        and str(independent_center_constant) == "3"
        and str(independent_center_kappa) == "2",
        {
            "primary": primary_center,
            "independent_constant": independent_center_constant,
            "independent_kappa": independent_center_kappa,
        },
        "C_mu=3+2*sqrt(473175/64)=3+15*sqrt(2103)/4",
        "cross_core",
    )
    shared["moving-center constant"] = "3+15*sqrt(2103)/4"

    primary_heat = (
        leaf_lookup(primary, ("heat_n1_dirichlet",)),
        leaf_lookup(primary, ("heat_n2_dirichlet",)),
    )
    independent_heat_rows = leaf_lookup(independent, ("heat_simplex.rows",))
    independent_heat = None
    if isinstance(independent_heat_rows, list) and len(independent_heat_rows) >= 2:
        independent_heat = [
            {
                "rational": independent_heat_rows[index].get("rational"),
                "pi_power": independent_heat_rows[index].get("pi_power"),
                "beta_power": independent_heat_rows[index].get("beta_power"),
            }
            for index in range(2)
            if isinstance(independent_heat_rows[index], dict)
        ]
    audit.check(
        "exact cross invariant first heat-simplex rows",
        tuple(map(compact_math, primary_heat)) == ("2*sqrt(beta)", "pi*beta")
        and independent_heat
        == [
            {"rational": "2", "pi_power": 0, "beta_power": "1/2"},
            {"rational": "1", "pi_power": 1, "beta_power": "1"},
        ],
        {"primary": primary_heat, "independent": independent_heat},
        "n=1: 2 sqrt(beta); n=2: pi beta",
        "cross_core",
    )
    shared["first heat-simplex rows"] = ["2*sqrt(beta)", "pi*beta"]

    primary_bump = leaf_lookup(primary, ("moving_bump_limit",))
    independent_bump = {
        key: leaf_lookup(independent, (f"moving_bump.{key}",))
        for key in ("f", "limit", "expected_limit", "R_degree", "f_exponent", "C1_exponent")
    }
    audit.check(
        "exact cross invariant moving-bump spatial exponent",
        "f^(3/4)" in compact_math(primary_bump)
        and "c1^(3/4)" in compact_math(primary_bump)
        and independent_bump
        == {
            "f": "1/16",
            "limit": "8",
            "expected_limit": "8",
            "R_degree": "0",
            "f_exponent": "-3/4",
            "C1_exponent": "-3/4",
        },
        {"primary": primary_bump, "independent": independent_bump},
        "C1^(-3/4) f^(-3/4) with zero R degree",
        "cross_core",
    )
    shared["moving-bump spatial exponent"] = "C1^(-3/4) f^(-3/4)"

    # Exact six-row Duhamel fixture.  Both engines must expose the same rational
    # values, not merely a common floating approximation.
    p_rows = leaf_lookup(primary, ("duhamel_first_rows", "duhamel.first_rows"))
    i_rows = leaf_lookup(
        independent,
        ("duhamel_first_rows", "duhamel.first_rows", "duhamel_topology.rows"),
    )
    expected_rows = [
        (1, "1/4", "3/8"),
        (2, "3/16", "5/16"),
        (3, "7/48", "9/32"),
        (4, "15/128", "17/64"),
        (5, "31/320", "33/128"),
        (6, "21/256", "65/256"),
    ]

    def row_contract(rows: Any) -> list[tuple[int, str, str]] | None:
        if not isinstance(rows, list) or len(rows) < 6:
            return None
        result: list[tuple[int, str, str]] = []
        for row in rows[:6]:
            if not isinstance(row, dict):
                return None
            result.append(
                (
                    int(row.get("n")),
                    str(
                        row.get(
                            "beta_times_duhamel_squared",
                            row.get("beta_times_duhamel_X_square"),
                        )
                    ),
                    str(
                        row.get(
                            "symmetric_gns_squared",
                            row.get("symmetric_gns_square"),
                        )
                    ),
                )
            )
        return result

    p_contract = row_contract(p_rows)
    i_contract = row_contract(i_rows)
    audit.check(
        "exact cross invariant Duhamel rational rows",
        p_contract == i_contract == expected_rows,
        {"primary": p_contract, "independent": i_contract},
        expected_rows,
        "cross_core",
    )
    shared["Duhamel rational rows"] = expected_rows
    return shared


def compact_text(text: str) -> str:
    return re.sub(r"\s+", "", text).lower()


def text_has(text: str, token: str) -> bool:
    return compact_text(token) in compact_text(text)


def boundary_contract(text: str) -> dict[str, bool]:
    lower = text.lower()
    groups = {
        "first-passage product": ("first-passage", "first passage"),
        "spatial commutator": ("spatial commutator", "lieb--robinson", "lieb-robinson"),
        "fifth onsite energy": ("fifth onsite", "fifth local", "p=5", "p > 4", "p>4"),
        "modular cutoff": ("modular", "dual-state", "dual state", "nontracial cutoff"),
        "common alpha": ("common alpha", "common-alpha", "common c-star", "common $\\alpha$"),
        "KMS": ("kms",),
        "ground states": ("ground state", "ground-state"),
        "GNS": ("gns",),
        "continuum": ("continuum", "regulator removal", "regulator"),
        "physical empty space": ("physical empty", "empty space", "empty-space"),
        "C6": ("c6",),
        "CP1": ("cp1",),
        "Sector A": ("sector a",),
        "Pre-A": ("pre-a", "pre a"),
    }
    return {
        label: any(candidate.lower() in lower for candidate in candidates)
        for label, candidates in groups.items()
    }


def validate_no_overclaim_text(text: str, label: str, audit: Audit, *, authority: bool) -> None:
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
            "does not add",
            "does not close",
            "not prove",
            "not yet proved",
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
    checks = {
        "schema": (manifest.get("schema"), "tect/pre-a-route-split/1.0"),
        "task": (manifest.get("task_id"), TASK_ID),
        "exploration": (manifest.get("exploration_id"), EXPLORATION_ID),
        "result id": (manifest.get("result_id"), RESULT_ID),
        "result number": (manifest.get("result_number"), RESULT_NUMBER),
        "result version": (manifest.get("result_version"), RESULT_VERSION),
    }
    for label, (actual, expected) in checks.items():
        audit.check(f"manifest {label}", actual == expected, actual, expected, "formal")
    negatives = manifest.get("negative_ids")
    audit.check(
        "manifest four exact negative IDs",
        isinstance(negatives, list)
        and len(negatives) == 4
        and tuple(negatives) == REQUIRED_NEGATIVE_IDS,
        negatives,
        list(REQUIRED_NEGATIVE_IDS),
        "formal",
    )
    parents = manifest.get("parent_explorations", [])
    audit.check(
        "manifest parent exploration chain",
        isinstance(parents, list) and all(item in parents for item in ("EXP-000794", "EXP-000795")),
        parents,
        "contains EXP-000794 and EXP-000795",
        "formal",
    )
    cubic = manifest.get("cubic_graph_embedding", {})
    audit.check(
        "manifest centered cubic graph closed",
        isinstance(cubic, dict)
        and cubic.get("closed") is True
        and "||U_f A^-1||<=kappa" in str(cubic.get("operator_bound", ""))
        and "0<=m<=4" in str(cubic.get("all_natural_powers", "")),
        cubic,
        "closed weighted graph theorem with operator and natural-power bounds",
        "formal",
    )
    moving = manifest.get("moving_center_comparison", {})
    audit.check(
        "manifest moving-center comparison",
        isinstance(moving, dict)
        and "C_mu=1+2(exp(mu)-1)(1+kappa)" in str(moving.get("neighbor_bound", ""))
        and "0<=s<=1" in str(moving.get("fractional_bound", "")),
        moving,
        "neighbor and fractional graph comparisons",
        "formal",
    )
    heat = manifest.get("heat_simplex", {})
    audit.check(
        "manifest prescribed-word heat scope",
        isinstance(heat, dict)
        and str(heat.get("status", "")).startswith("PROVED FOR EACH PRESCRIBED WORD")
        and "NOT A CONNECTED-CLUSTER OR REAL-TIME THEOREM" in str(heat.get("status", "")),
        heat.get("status") if isinstance(heat, dict) else heat,
        "prescribed-word only",
        "scope",
    )
    real_time = manifest.get("conditional_real_time_product", {})
    audit.check(
        "manifest first-passage gate open",
        isinstance(real_time, dict)
        and real_time.get("gate_id") == FIRST_PASSAGE_GATE
        and real_time.get("status") == "OPEN"
        and "Gamma(1+n/2)" in str(real_time.get("response_target", "")),
        real_time,
        "open exact first-passage response target",
        "formal",
    )
    equilibrium = manifest.get("equilibrium_cutoff_alternative", {})
    audit.check(
        "manifest fifth-energy modular gate open",
        isinstance(equilibrium, dict)
        and equilibrium.get("gate_id") == FIFTH_ENERGY_GATE
        and equilibrium.get("status") == "OPEN"
        and "p=5" in str(equilibrium.get("moment_target", ""))
        and "alone do not prove" in str(equilibrium.get("topology_requirement", "")),
        equilibrium,
        "open p=5 plus modular/dual-state topology gate",
        "formal",
    )
    duhamel = manifest.get("duhamel_topology_counterexample", {})
    audit.check(
        "manifest squared-Duhamel topology boundary",
        isinstance(duhamel, dict)
        and str(duhamel.get("duhamel", "")).startswith("The squared Duhamel norms")
        and "itself is not rejected" in str(duhamel.get("scope", "")),
        duhamel,
        "squared norms vanish; KMS route not rejected",
        "scope",
    )
    open_gates = manifest.get("open_gates", [])
    audit.check(
        "manifest exact open-gate set",
        isinstance(open_gates, list)
        and set(open_gates) == {FIRST_PASSAGE_GATE, FIFTH_ENERGY_GATE, ROUND1_GATE},
        open_gates,
        [FIRST_PASSAGE_GATE, FIFTH_ENERGY_GATE, ROUND1_GATE],
        "formal",
    )
    expected_verification = {
        "primary_script": PRIMARY.relative_to(REPO).as_posix(),
        "independent_script": INDEPENDENT.relative_to(REPO).as_posix(),
        "integrated_script": SCRIPT.relative_to(REPO).as_posix(),
    }
    verification = manifest.get("verification", {})
    for key, expected in expected_verification.items():
        audit.check(
            f"manifest verification {key}",
            isinstance(verification, dict) and verification.get(key) == expected,
            verification.get(key) if isinstance(verification, dict) else verification,
            expected,
            "formal",
        )
    validate_no_overclaim_text(str(manifest.get("no_overclaim", "")), "manifest", audit, authority=False)


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
    if PdfReader is None:
        audit.pending("pypdf available", False, "ImportError", "installed pypdf", "pdf")
        return {"size_bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
    try:
        reader = PdfReader(str(PDF), strict=True)
        pages = len(reader.pages)
        extracted = "\n".join((page.extract_text() or "") for page in reader.pages)
    except Exception as error:  # pypdf uses several backend exception classes.
        audit.pending("PDF parses strictly", False, error, "strictly parseable PDF", "pdf")
        return {"size_bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
    audit.pending("PDF page count positive", pages > 0, pages, ">0", "pdf")
    audit.pending("PDF text nontrivial", len(extracted) > 300, len(extracted), ">300", "pdf")
    for token in (EXPLORATION_ID, RESULT_NUMBER, RESULT_VERSION, FIRST_PASSAGE_GATE, FIFTH_ENERGY_GATE):
        audit.pending(
            f"PDF links {token}",
            text_has(extracted, token),
            text_has(extracted, token),
            True,
            "pdf",
        )
    for negative_id in REQUIRED_NEGATIVE_IDS:
        audit.pending(
            f"PDF links {negative_id}",
            text_has(extracted, negative_id),
            text_has(extracted, negative_id),
            True,
            "pdf",
        )
    validate_no_overclaim_text(extracted, "PDF", audit, authority=True)
    return {
        "path": PDF.relative_to(REPO).as_posix(),
        "size_bytes": len(raw),
        "pages": pages,
        "sha256": hashlib.sha256(raw).hexdigest(),
    }


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
        audit.pending(
            f"{EXPLORATION_ID} unique",
            False,
            len(matches),
            1,
            "formal",
        )
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
        conditions = {
            "task": record.get("task_id") == TASK_ID,
            "verdict": record.get("verdict") == "advanced",
            "result": RESULT_NUMBER in results,
            "negatives": set(REQUIRED_NEGATIVE_IDS).issubset(negatives),
            "gates": isinstance(gates, list) and {FIRST_PASSAGE_GATE, FIFTH_ENERGY_GATE}.issubset(gates),
            "parents": {"EXP-000794", "EXP-000795"}.issubset(related_ids),
            "manifest": MANIFEST.relative_to(REPO).as_posix() in serialized,
            "certificate": CERTIFICATE.relative_to(REPO).as_posix() in serialized,
            "pdf": PDF.relative_to(REPO).as_posix() in serialized,
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

        # EXP-000796 is immutable and omitted the source-note locator.  The
        # omission must not be silently forgiven by accepting an arbitrary
        # later record; exactly EXP-000797 supplies the append-only repair.
        audit.check(
            f"{EXPLORATION_ID} source-note omission preserved",
            NOTE.relative_to(REPO).as_posix() not in serialized,
            NOTE.relative_to(REPO).as_posix() in serialized,
            False,
            "correction_chain",
        )

    correction_matches = [] if explorations is None else [
        row for row in explorations if row.get("id") == CORRECTION_EXPLORATION_ID
    ]
    if not correction_matches:
        audit.require(
            f"{CORRECTION_EXPLORATION_ID} registered",
            False,
            0,
            "one unique append-only source-note correction",
            "correction_chain",
        )
    elif len(correction_matches) != 1:
        audit.pending(
            f"{CORRECTION_EXPLORATION_ID} unique",
            False,
            len(correction_matches),
            1,
            "correction_chain",
        )
    else:
        correction = correction_matches[0]
        correction_serialized = json.dumps(
            correction, sort_keys=True, ensure_ascii=True
        )
        correction_formal = correction.get("formal_refs", {})
        correction_negatives = (
            correction_formal.get("negatives", [])
            if isinstance(correction_formal, dict)
            else []
        )
        correction_results = (
            correction_formal.get("results", [])
            if isinstance(correction_formal, dict)
            else []
        )
        correction_gates = correction.get("gate_ids", [])
        correction_related = correction.get("related", [])
        relation_exact = (
            isinstance(correction_related, list)
            and sum(
                1
                for item in correction_related
                if isinstance(item, dict)
                and item.get("id") == EXPLORATION_ID
                and item.get("relation") == "corrects"
            )
            == 1
        )
        correction_conditions = {
            "task": correction.get("task_id") == TASK_ID,
            "verdict": correction.get("verdict") == "advanced",
            "corrects_EXP-000796_exactly_once": relation_exact,
            "source_note": NOTE.relative_to(REPO).as_posix()
            in correction_serialized,
            "pdf": PDF.relative_to(REPO).as_posix() in correction_serialized,
            "result": RESULT_NUMBER in correction_results,
            "four_exact_negatives": (
                isinstance(correction_negatives, list)
                and len(correction_negatives) == 4
                and set(correction_negatives) == set(REQUIRED_NEGATIVE_IDS)
            ),
            "both_exact_gates": (
                isinstance(correction_gates, list)
                and len(correction_gates) == 2
                and set(correction_gates)
                == {FIRST_PASSAGE_GATE, FIFTH_ENERGY_GATE}
            ),
        }
        for condition, value in correction_conditions.items():
            audit.pending(
                f"{CORRECTION_EXPLORATION_ID} {condition}",
                value,
                value,
                True,
                "correction_chain",
            )
        audit.pending(
            "append-only note/PDF locator correction chain complete",
            all(correction_conditions.values()),
            correction_conditions,
            "all conditions true",
            "correction_chain",
        )
        validate_no_overclaim_text(
            str(correction.get("boundary", "")),
            CORRECTION_EXPLORATION_ID,
            audit,
            authority=True,
        )

    result_ledger = require_text(REPO / "RESULTS-LEDGER.md", audit, "result ledger")
    if result_ledger is not None:
        require_tokens(
            result_ledger,
            "R-167 v1.1 result ledger",
            (
                "### R-167",
                RESULT_ID,
                RESULT_VERSION,
                EXPLORATION_ID,
                "centered-weight cubic graph",
                "prescribed-word",
                FIRST_PASSAGE_GATE,
                FIFTH_ENERGY_GATE,
            ),
            audit,
        )

    registry = require_text(REPO / "negative-results/registry.md", audit, "negative registry")
    if registry is not None:
        for negative_id in REQUIRED_NEGATIVE_IDS:
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
        require_tokens(
            gates_text,
            "gate authority",
            (EXPLORATION_ID, RESULT_NUMBER, RESULT_VERSION, FIRST_PASSAGE_GATE, FIFTH_ENERGY_GATE),
            audit,
        )

    todo = load_json(REPO / "todo/todo.json", audit, "TODO authority", pending_authority=True)
    if todo is not None:
        tasks = todo.get("tasks", [])
        task_matches = [
            task
            for task in tasks
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
            task_note = str(task.get("note", "")).lower()
            task_contract = {
                "round1_gate": task.get("gate") == ROUND1_GATE,
                "common_alpha_open": "common alpha" in task_note and "remain open" in task_note,
                "current_status": task.get("status") == "in_progress",
            }
            audit.pending(
                "T-054 current live-task contract",
                all(task_contract.values()),
                task_contract,
                "in_progress Round-1 task with common-alpha route explicitly open",
                "formal",
            )

    roadmap = require_text(REPO / "ROADMAP.md", audit, "roadmap")
    if roadmap is not None:
        require_tokens(
            roadmap,
            "roadmap",
            (EXPLORATION_ID, RESULT_NUMBER, RESULT_VERSION, FIRST_PASSAGE_GATE, FIFTH_ENERGY_GATE),
            audit,
        )

    sector_map = load_json(SECTOR_A_MAP, audit, "Sector-A theorem map", pending_authority=True)
    if sector_map is not None:
        serialized = json.dumps(sector_map, sort_keys=True, ensure_ascii=True)
        require_tokens(
            serialized,
            "Sector-A theorem map",
            (RESULT_NUMBER, RESULT_VERSION, FIRST_PASSAGE_GATE, FIFTH_ENERGY_GATE),
            audit,
        )

    proof_map = require_text(PROOF_EVIDENCE_MAP, audit, "proof-evidence map")
    if proof_map is not None:
        require_tokens(
            proof_map,
            "proof-evidence map",
            (
                EXPLORATION_ID,
                CORRECTION_EXPLORATION_ID,
                RESULT_NUMBER,
                FIRST_PASSAGE_GATE,
                FIFTH_ENERGY_GATE,
                *REQUIRED_NEGATIVE_IDS,
            ),
            audit,
        )

    note = require_text(NOTE, audit, "source note")
    if note is not None:
        require_tokens(
            note,
            "source note",
            (
                EXPLORATION_ID,
                RESULT_NUMBER,
                RESULT_VERSION,
                RESULT_ID,
                FIRST_PASSAGE_GATE,
                FIFTH_ENERGY_GATE,
                *REQUIRED_NEGATIVE_IDS,
            ),
            audit,
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
                FIRST_PASSAGE_GATE,
                FIFTH_ENERGY_GATE,
                *REQUIRED_NEGATIVE_IDS,
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
            "C6 gate unchanged",
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
    validate_independence(audit)

    components: dict[str, dict[str, Any]] = {}
    sentinels: dict[str, str] = {}
    with tempfile.TemporaryDirectory(prefix="tect-exp796-integrated-") as directory:
        temporary = Path(directory)
        for label, script in (("primary", PRIMARY), ("independent", INDEPENDENT)):
            result = run_fresh(script, temporary / f"{label}.json", temporary, audit, label)
            if result is not None:
                components[f"{label}_fresh"], sentinels[label] = result

    for label, path in (("primary", PRIMARY_STORED), ("independent", INDEPENDENT_STORED)):
        stored = stored_against_fresh(path, components.get(f"{label}_fresh"), audit, label)
        if stored is not None:
            components[f"{label}_stored"] = stored

    for label, minimum, owner in (
        ("primary", MINIMUM_PRIMARY_COUNT, PRIMARY),
        ("independent", MINIMUM_INDEPENDENT_COUNT, INDEPENDENT),
    ):
        payload = components.get(f"{label}_fresh")
        if payload is not None:
            validate_component(payload, f"{label} fresh", minimum, audit)
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
        "authority_correction_exploration": CORRECTION_EXPLORATION_ID,
        "task_id": TASK_ID,
        "open_gates": [FIRST_PASSAGE_GATE, FIFTH_ENERGY_GATE, ROUND1_GATE],
        "negative_ids": list(REQUIRED_NEGATIVE_IDS),
        "claim_bearing": False,
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
        help="exit zero with deterministic INCOMPLETE while authorities are being assembled",
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

#!/usr/bin/env python3
"""Integrated strict audit for the EXP-000794/795 second-energy/Cauchy split.

The primary and independent implementations are always executed into fresh
temporary paths.  Their volatile caller-selected paths are normalized before
comparison with the stored artifacts.  The default mode is release-strict:
all formal authorities, the source note, the parsed PDF, and the two fresh
stored results must agree.  During package assembly ``--staged`` writes an
explicitly ``INCOMPLETE`` result that lists every missing authority; it never
turns missing evidence into PASS.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Callable, Iterable

try:
    from pypdf import PdfReader
except ImportError:  # Reported by the audit rather than hidden at import time.
    PdfReader = None  # type: ignore[assignment]


__version__ = "1.0.1"
REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-second-weighted-energy-cauchy-gate"
RESULT_ID = (
    "PA-CP1-ST8-Q3LOCK-SECOND-WEIGHTED-ENERGY-MOMENT-AND-"
    "COMMON-ALPHA-CAUCHY-GATE-SPLIT"
)
EXPLORATION_ID = "EXP-000794"
CORRECTION_EXPLORATION_ID = "EXP-000795"
TASK_ID = "T-054"
NEXT_GATE = "PA-CP1-ST8-Q3LOCK-ENERGY-WEIGHTED-COMMUTATOR-GEVREY-LR-CLOSURE"
REQUIRED_NEGATIVE_IDS = (
    "NG-2026-08-10-PRE-A-ST8-Q3LOCK-FIRST-MOMENT-AUTOMATIC-POWER-UPGRADE",
    "NG-2026-08-10-PRE-A-ST8-Q3LOCK-SYMMETRIC-SANDWICH-ONLY-THERMODYNAMIC-CAUCHY",
)

PRIMARY = REPO / f"codes/foundations/{SLUG.replace('-', '_')}.py"
INDEPENDENT = REPO / f"codes/foundations/{SLUG.replace('-', '_')}_independent.py"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260810.md"
PARENT_MANIFEST = REPO / (
    "strategy/pre-a-cp1-st8-q3lock-common-local-derivation-"
    "weighted-energy-route-split-manifest.json"
)
NOTE = REPO / (
    "claims/C6-SPACETIME-SIGNATURE/notes/"
    "pre-a-q3lock-second-weighted-energy-and-cauchy-gate-260810-v0.1.tex.txt"
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

MINIMUM_PRIMARY_COUNT = 43
MINIMUM_INDEPENDENT_COUNT = 104


def json_safe(value: Any) -> Any:
    """Return a deterministic JSON-compatible representation."""

    if isinstance(value, Path):
        return value.as_posix()
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        items = [json_safe(item) for item in value]
        return sorted(items, key=lambda item: json.dumps(item, sort_keys=True)) if isinstance(value, set) else items
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    return str(value)


def portable_bytes(path: Path) -> bytes:
    return path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def portable_sha256(path: Path) -> str:
    return hashlib.sha256(portable_bytes(path)).hexdigest()


def artifact_sha256(path: Path) -> str:
    """Use normalized text hashes, but never mutate binary PDF bytes."""

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
            json.dump(json_safe(payload), stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def normalize_volatile(value: Any, roots: Iterable[Path]) -> Any:
    """Erase caller-selected temporary roots without weakening other checks."""

    root_spellings: list[str] = []
    for root in roots:
        text = str(root)
        root_spellings.extend((text, text.replace("\\", "/")))

    if isinstance(value, str):
        normalized = value
        for spelling in sorted(set(root_spellings), key=len, reverse=True):
            normalized = normalized.replace(spelling, "<TEMP>")
        return normalized.replace("\\", "/")
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
    normalized = normalize_volatile(value, roots)
    return json.dumps(
        normalized,
        sort_keys=True,
        ensure_ascii=True,
        separators=(",", ":"),
    ).encode("ascii")


class Audit:
    """Collect all defects so staged mode reports the complete boundary."""

    def __init__(self) -> None:
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
    missing_is_authority: bool = True,
) -> dict[str, Any] | None:
    if not path.is_file():
        reporter = audit.require if missing_is_authority else audit.check
        reporter(f"{label} exists", False, path, "file", "files")
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        audit.check(f"{label} parses", False, error, "valid JSON object", "files")
        return None
    if not isinstance(payload, dict):
        audit.check(f"{label} object", False, type(payload).__name__, "dict", "files")
        return None
    audit.check(f"{label} parses", True, path.relative_to(REPO), "valid JSON object", "files")
    return payload


def require_text(path: Path, audit: Audit, label: str) -> str | None:
    if not path.is_file():
        audit.require(f"{label} exists", False, path.relative_to(REPO), "file", "formal")
        return None
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        audit.check(f"{label} UTF-8", False, error, "readable UTF-8", "formal")
        return None
    audit.check(f"{label} readable", bool(text), len(text), ">0", "formal")
    return text


def jsonl_records(path: Path, audit: Audit, label: str) -> list[dict[str, Any]] | None:
    if not path.is_file():
        audit.require(f"{label} exists", False, path.relative_to(REPO), "file", "formal")
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
        audit.check(f"{label} parses", False, error, "valid JSONL objects", "formal")
        return None
    audit.check(f"{label} parses", bool(records), len(records), ">=1", "formal")
    return records


def unique_record(
    records: list[dict[str, Any]] | None,
    predicate: Callable[[dict[str, Any]], bool],
    label: str,
    audit: Audit,
) -> dict[str, Any] | None:
    if records is None:
        return None
    matches = [record for record in records if predicate(record)]
    if not matches:
        audit.require(f"{label} registered", False, 0, 1, "formal")
        return None
    if len(matches) != 1:
        audit.check(f"{label} unique", False, len(matches), 1, "formal")
        return None
    audit.check(f"{label} unique", True, 1, 1, "formal")
    return matches[0]


def run_fresh(
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
        detail = normalize_volatile(
            {
                "returncode": completed.returncode,
                "stdout": completed.stdout[-2000:],
                "stderr": completed.stderr[-2000:],
                "output_exists": output.is_file(),
            },
            (temporary_root,),
        )
        audit.check(f"{label} fresh execution", False, detail, "exit 0 and JSON", "freshness")
        return None
    try:
        payload = json.loads(output.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        audit.check(f"{label} fresh JSON", False, error, "valid JSON object", "freshness")
        return None
    if not isinstance(payload, dict):
        audit.check(f"{label} fresh object", False, type(payload).__name__, "dict", "freshness")
        return None
    sentinel = next(
        (line.strip() for line in completed.stdout.splitlines() if line.strip().startswith("PASS ")),
        "",
    )
    audit.check(f"{label} fresh execution", True, completed.returncode, 0, "freshness")
    audit.check(f"{label} PASS sentinel", bool(sentinel), sentinel, "PASS ...", "freshness")
    return normalize_volatile(payload, (temporary_root,)), sentinel


def load_stored_against_fresh(
    path: Path,
    fresh: dict[str, Any] | None,
    audit: Audit,
    label: str,
) -> dict[str, Any] | None:
    """Use one row in both staged and strict modes to keep totals stable."""

    if not path.is_file():
        audit.require(
            f"{label} stored fresh result",
            False,
            path.relative_to(REPO),
            "existing valid JSON exactly equal to fresh execution",
            "freshness",
        )
        return None
    try:
        stored = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        audit.check(
            f"{label} stored fresh result",
            False,
            error,
            "existing valid JSON exactly equal to fresh execution",
            "freshness",
        )
        return None
    if not isinstance(stored, dict):
        audit.check(
            f"{label} stored fresh result",
            False,
            type(stored).__name__,
            "JSON object exactly equal to fresh execution",
            "freshness",
        )
        return None
    stored_canonical = canonical_payload(stored)
    fresh_canonical = canonical_payload(fresh) if fresh is not None else b""
    equal = fresh is not None and stored_canonical == fresh_canonical
    audit.check(
        f"{label} stored fresh result",
        equal,
        {
            "stored_sha256": hashlib.sha256(stored_canonical).hexdigest(),
            "fresh_sha256": hashlib.sha256(fresh_canonical).hexdigest() if fresh is not None else None,
        },
        "equal normalized payload hashes",
        "freshness",
    )
    return normalize_volatile(stored, ())


def assertion_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    assertions = payload.get("assertions", [])
    if isinstance(assertions, list):
        return [row for row in assertions if isinstance(row, dict)]
    if isinstance(assertions, dict):
        rows = assertions.get("rows", [])
        return [row for row in rows if isinstance(row, dict)] if isinstance(rows, list) else []
    return []


def validate_component(
    payload: dict[str, Any],
    label: str,
    minimum_count: int,
    audit: Audit,
) -> None:
    audit.check(f"{label} result id", payload.get("result_id") == RESULT_ID, payload.get("result_id"), RESULT_ID, "components")
    audit.check(f"{label} verdict", payload.get("verdict") == "PASS", payload.get("verdict"), "PASS", "components")
    summary = payload.get("summary", {})
    summary_valid = (
        isinstance(summary, dict)
        and isinstance(summary.get("total"), int)
        and summary.get("total") >= minimum_count
        and summary.get("passed") == summary.get("total")
        and summary.get("failed") == 0
    )
    audit.check(
        f"{label} exact all-PASS summary",
        summary_valid,
        summary,
        f"passed=total>={minimum_count}, failed=0",
        "components",
    )
    expected_count = summary.get("total") if summary_valid else minimum_count
    rows = assertion_rows(payload)
    audit.check(
        f"{label} row count",
        len(rows) == expected_count,
        len(rows),
        expected_count,
        "components",
    )
    audit.check(
        f"{label} rows all PASS",
        len(rows) == expected_count and all(row.get("status") == "PASS" for row in rows),
        sum(row.get("status") == "PASS" for row in rows),
        expected_count,
        "components",
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
    required_paths = {owner, MANIFEST, CERTIFICATE, PARENT_MANIFEST}
    required = {
        path.relative_to(REPO).as_posix(): portable_sha256(path)
        for path in required_paths
        if path.is_file()
    }
    actual = payload.get("source_hashes")
    audit.check(
        f"{label} required source-hash keys",
        isinstance(actual, dict) and set(required).issubset(actual),
        sorted(actual) if isinstance(actual, dict) else actual,
        f"superset of {sorted(required)}",
        "hashes",
    )
    if isinstance(actual, dict):
        for relative, digest in actual.items():
            candidate = (REPO / relative).resolve()
            confined = candidate == REPO or REPO in candidate.parents
            expected_digest = portable_sha256(candidate) if confined and candidate.is_file() else None
            audit.check(
                f"{label} fresh hash {relative}",
                confined and expected_digest is not None and digest == expected_digest,
                digest,
                expected_digest if confined else "repository-confined existing source",
                "hashes",
            )


def validate_independence(audit: Audit) -> None:
    if not (PRIMARY.is_file() and INDEPENDENT.is_file()):
        audit.require("both sources available for AST audit", False, [PRIMARY.is_file(), INDEPENDENT.is_file()], [True, True], "independence")
        return
    try:
        primary_tree = ast.parse(PRIMARY.read_text(encoding="utf-8"), filename=str(PRIMARY))
        independent_source = INDEPENDENT.read_text(encoding="utf-8")
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
            if isinstance(node.func, ast.Name) and node.func.id in {"__import__", "eval", "exec"}:
                dynamic.append(node.func.id)
            elif isinstance(node.func, ast.Attribute) and node.func.attr in {"import_module", "run_module", "run_path"}:
                dynamic.append(node.func.attr)
    forbidden = {"sympy", "numpy", "importlib", PRIMARY.stem}
    audit.check("independent import firewall", not imports.intersection(forbidden), sorted(imports.intersection(forbidden)), [], "independence")
    audit.check("independent dynamic import firewall", not dynamic, dynamic, [], "independence")
    audit.check("independent AST differs", ast.dump(primary_tree) != ast.dump(independent_tree), "different" if ast.dump(primary_tree) != ast.dump(independent_tree) else "same", "different", "independence")
    audit.check("independent source hash differs", portable_sha256(PRIMARY) != portable_sha256(INDEPENDENT), portable_sha256(INDEPENDENT), f"different from {portable_sha256(PRIMARY)}", "independence")


def compare_exact_core(primary: dict[str, Any], independent: dict[str, Any], audit: Audit) -> None:
    p = primary.get("derived", {})
    i = independent.get("derived", {})
    iq3 = i.get("q3", {})
    imoment = i.get("second_moment_fixture", {})
    iorder = i.get("ordering_counterexample", {})
    iword = i.get("free_word_cubic", {})
    iupward = i.get("upward_spectral_transition", {})
    iconvex = i.get("convexity_sign_counterexample", {})
    ithresholds = i.get("thresholds", {})
    pairs = (
        ("Q3 edges", p.get("Q3_edges"), iq3.get("edges")),
        ("Q3 degrees", p.get("Q3_degrees"), iq3.get("degrees")),
        ("C2 fixture", p.get("C2_fixture"), iq3.get("C2_fixture")),
        ("M_mu squared", p.get("M_mu_squared_fixture"), imoment.get("M_mu_squared")),
        ("v_mu squared", p.get("v_mu_squared_fixture"), imoment.get("v_mu_squared")),
        ("first-order determinant", p.get("first_order_det"), iorder.get("first_determinant")),
        ("squared-order determinant", p.get("squared_order_det"), iorder.get("second_determinant")),
        ("cubic free-word residual", p.get("cubic_identity_residual_terms"), iword.get("residual_terms")),
        ("common-alpha closure flag", p.get("common_alpha_closed"), i.get("common_alpha_closed")),
        (
            "cubic multiplier closure flag",
            p.get("cubic_multiplier_closed"),
            ithresholds.get("cubic_multiplier_closed"),
        ),
    )
    for name, primary_value, independent_value in pairs:
        audit.check(
            f"exact cross {name}",
            primary_value == independent_value,
            {"primary": primary_value, "independent": independent_value},
            "exact equality",
            "cross_core",
        )

    independent_rungs = [
        row.get("upward_matrix_element")
        for row in iupward.get("rung_rows", [])[:9]
        if isinstance(row, dict)
    ]
    audit.check(
        "exact cross exponential rung amplitudes",
        p.get("rung_amplitudes") == independent_rungs,
        {"primary": p.get("rung_amplitudes"), "independent": independent_rungs},
        [str(2**index) for index in range(9)],
        "cross_core",
    )
    audit.check(
        "exact cross convex weighted witness",
        p.get("convex_weighted_witness") == iconvex.get("quadratic_form"),
        {"primary": p.get("convex_weighted_witness"), "independent": iconvex.get("quadratic_form")},
        "-1",
        "cross_core",
    )
    audit.check(
        "exact cross convex weighted trace",
        p.get("convex_weighted_trace") == iconvex.get("trace"),
        {"primary": p.get("convex_weighted_trace"), "independent": iconvex.get("trace")},
        "48",
        "cross_core",
    )

    exact_oracles = {
        "Q3 edges": (p.get("Q3_edges"), 12),
        "Q3 degrees": (p.get("Q3_degrees"), [3] * 8),
        "C2 fixture": (p.get("C2_fixture"), "13"),
        "M_mu squared": (p.get("M_mu_squared_fixture"), "700902/125"),
        "v_mu squared": (p.get("v_mu_squared_fixture"), "27/5"),
        "first-order determinant": (p.get("first_order_det"), "7/20"),
        "squared-order determinant": (p.get("squared_order_det"), "-127/16"),
        "cubic residual": (p.get("cubic_identity_residual_terms"), 0),
        "common alpha open": (p.get("common_alpha_closed"), False),
        "cubic multiplier embedding open": (p.get("cubic_multiplier_closed"), False),
        "first nine rung amplitudes": (p.get("rung_amplitudes"), [str(2**index) for index in range(9)]),
        "convex weighted witness": (p.get("convex_weighted_witness"), "-1"),
        "convex weighted trace": (p.get("convex_weighted_trace"), "48"),
    }
    for name, (actual, expected) in exact_oracles.items():
        audit.check(f"exact oracle {name}", actual == expected, actual, expected, "cross_core")

    thresholds = ithresholds
    expected_thresholds = {
        "cubic_power_count_target": "3/4",
        "symmetric_cubic_power_count_target": "3/8",
        "cubic_multiplier_closed": False,
        "minimum_fractional_moment": "3/2",
        "minimum_integer_moment": 2,
        "cauchy_spatial_condition": "rho>mu/4",
    }
    audit.check(
        "independent exact power-count and domain-boundary contracts",
        all(thresholds.get(key) == value for key, value in expected_thresholds.items()),
        {key: thresholds.get(key) for key in expected_thresholds},
        expected_thresholds,
        "cross_core",
    )
    audit.check(
        "independent exponential rung obstruction",
        iupward.get("generic_lower_bound") == "2^(2^n-d(n+1)) along j=2^n",
        iupward.get("generic_lower_bound"),
        "2^(2^n-d(n+1)) along j=2^n",
        "cross_core",
    )


def contains_all_boundaries(text: str) -> dict[str, bool]:
    lower = text.lower()
    alternatives = {
        "common alpha": (
            "common alpha",
            "common $\\alpha$",
            "common \\(\\alpha\\)",
            "common `alpha`",
            "common thermodynamic `alpha`",
            "common-alpha",
            "common α",
        ),
        "KMS": ("kms",),
        "ground states": ("ground state", "ground-state"),
        "GNS": ("gns",),
        "regulator removal": ("regulator removal", "remove the regulator", "continuum removal"),
        "physical empty space": ("physical empty", "empty space", "empty-space"),
        "C6": ("c6",),
        "CP1": ("cp1",),
        "Sector A": ("sector a",),
        "Pre-A": ("pre-a", "pre a"),
    }
    return {
        label: any(candidate.lower() in lower for candidate in candidates)
        for label, candidates in alternatives.items()
    }


def validate_no_overclaim_text(text: str, label: str, audit: Audit) -> None:
    boundaries = contains_all_boundaries(text)
    for boundary, present in boundaries.items():
        audit.check(f"{label} no-overclaim {boundary}", present, present, True, "scope")
    lower = text.lower()
    open_signal = any(phrase in lower for phrase in ("remain open", "remains open", "does not prove", "not prove"))
    audit.check(f"{label} explicit open-boundary signal", open_signal, open_signal, True, "scope")


def validate_cubic_scope_text(text: str, label: str, audit: Audit) -> None:
    """Reject the EXP-000794 graph-embedding overstatement explicitly."""

    lower = text.lower()
    energy_domain = "energy-domain" in lower or "energy domain" in lower
    power_count = (
        "power-count" in lower
        or "power count" in lower
        or "necessary scalar" in lower
        or "necessary target" in lower
    )
    cubic_multiplier = (
        "cubic multiplier" in lower
        or "cubic-multiplier" in lower
        or "q^3" in lower
        or "q3" in lower
    )
    open_signal = any(
        phrase in lower
        for phrase in (
            "remains open",
            "remain open",
            "not proved",
            "not prove",
            "does not prove",
            "no noncommuting operator/domain embedding is proved",
        )
    )
    audit.check(
        f"{label} three-quarter energy-domain scope",
        energy_domain,
        energy_domain,
        True,
        "scope_correction",
    )
    audit.check(
        f"{label} cubic threshold is power-count only",
        power_count,
        power_count,
        True,
        "scope_correction",
    )
    audit.check(
        f"{label} cubic multiplier named open",
        cubic_multiplier and open_signal,
        {"cubic_multiplier": cubic_multiplier, "open_signal": open_signal},
        {"cubic_multiplier": True, "open_signal": True},
        "scope_correction",
    )


def validate_pdf(audit: Audit) -> dict[str, Any]:
    if not PDF.is_file():
        audit.require("PDF exists", False, PDF.relative_to(REPO), "file", "pdf")
        return {}
    raw = PDF.read_bytes()
    audit.check("PDF signature", raw.startswith(b"%PDF-"), raw[:5].decode("ascii", errors="replace"), "%PDF-", "pdf")
    audit.check("PDF nontrivial size", len(raw) > 1024, len(raw), ">1024", "pdf")
    if PdfReader is None:
        audit.check("pypdf available", False, "ImportError", "installed pypdf", "pdf")
        return {"size_bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
    try:
        reader = PdfReader(str(PDF), strict=True)
        page_count = len(reader.pages)
        extracted = "\n".join((page.extract_text() or "") for page in reader.pages)
    except Exception as error:  # pypdf exposes several backend exception types.
        audit.check("PDF parses strictly", False, error, "strictly parseable PDF", "pdf")
        return {"size_bytes": len(raw), "sha256": hashlib.sha256(raw).hexdigest()}
    audit.check("PDF page count positive", page_count > 0, page_count, ">0", "pdf")
    audit.check("PDF extracted text nontrivial", len(extracted) > 200, len(extracted), ">200", "pdf")
    validate_no_overclaim_text(extracted, "PDF", audit)
    validate_cubic_scope_text(extracted, "PDF", audit)
    return {
        "path": PDF.relative_to(REPO).as_posix(),
        "size_bytes": len(raw),
        "pages": page_count,
        "sha256": hashlib.sha256(raw).hexdigest(),
    }


def validate_formal(manifest: dict[str, Any], audit: Audit) -> dict[str, Any]:
    declared_negatives = manifest.get("negative_ids", [])
    if not isinstance(declared_negatives, list):
        declared_negatives = []
    audit.check("manifest result id", manifest.get("result_id") == RESULT_ID, manifest.get("result_id"), RESULT_ID, "formal")
    audit.check("manifest task id", manifest.get("task_id") == TASK_ID, manifest.get("task_id"), TASK_ID, "formal")
    audit.check(
        "manifest required negative IDs",
        len(declared_negatives) == len(set(declared_negatives))
        and all(item in declared_negatives for item in REQUIRED_NEGATIVE_IDS),
        declared_negatives,
        f"unique list containing {list(REQUIRED_NEGATIVE_IDS)}",
        "formal",
    )
    audit.check("manifest next gate", manifest.get("open_commutator_gate", {}).get("gate_id") == NEXT_GATE, manifest.get("open_commutator_gate", {}).get("gate_id"), NEXT_GATE, "formal")
    audit.check("manifest common alpha open", "COMMON ALPHA" in manifest.get("status", "") and "REMAIN OPEN" in manifest.get("status", ""), manifest.get("status"), "COMMON ALPHA ... REMAIN OPEN", "scope")
    audit.check(
        "manifest scope-correction exploration",
        manifest.get("scope_correction_exploration") == CORRECTION_EXPLORATION_ID,
        manifest.get("scope_correction_exploration"),
        CORRECTION_EXPLORATION_ID,
        "scope_correction",
    )
    fractional = manifest.get("fractional_graph_domain", {})
    audit.check(
        "manifest cubic multiplier remains open",
        fractional.get("cubic_multiplier_closed") is False,
        fractional.get("cubic_multiplier_closed"),
        False,
        "scope_correction",
    )
    power_contract = str(fractional.get("sharp_power_count", ""))
    audit.check(
        "manifest three-quarter value is necessary power count only",
        "s>=3/4" in power_contract
        and "necessary" in power_contract.lower()
        and any(
            phrase in power_contract.lower()
            for phrase in ("does not prove", "not prove", "no noncommuting")
        ),
        power_contract,
        "s>=3/4 necessary scalar target; no operator/domain embedding proved",
        "scope_correction",
    )
    open_obligation = str(fractional.get("cubic_multiplier_open_obligation", ""))
    audit.check(
        "manifest cubic multiplier open obligation explicit",
        ("q^3" in open_obligation.lower() or "cubic multiplier" in open_obligation.lower())
        and any(
            phrase in open_obligation.lower()
            for phrase in (
                "remain open",
                "remains open",
                "not proved",
                "not prove",
                "neither follows",
            )
        ),
        open_obligation,
        "explicit open q^3/cubic-multiplier embedding obligation",
        "scope_correction",
    )
    status_text = str(manifest.get("status", ""))
    audit.check(
        "manifest status names energy-domain propagation, not graph closure",
        "ENERGY-DOMAIN" in status_text
        and "SHARP CUBIC GRAPH DOMAIN" not in status_text,
        status_text,
        "ENERGY-DOMAIN ... and no SHARP CUBIC GRAPH DOMAIN",
        "scope_correction",
    )
    validate_no_overclaim_text(str(manifest.get("no_overclaim", "")), "manifest", audit)
    validate_cubic_scope_text(json.dumps(manifest, sort_keys=True), "manifest", audit)

    expected_verification = {
        "primary_script": PRIMARY.relative_to(REPO).as_posix(),
        "independent_script": INDEPENDENT.relative_to(REPO).as_posix(),
        "integrated_script": SCRIPT.relative_to(REPO).as_posix(),
    }
    verification = manifest.get("verification", {})
    for key, expected in expected_verification.items():
        audit.check(f"manifest verification {key}", verification.get(key) == expected, verification.get(key), expected, "formal")

    explorations = jsonl_records(REPO / "explorations/log.jsonl", audit, "exploration ledger")
    matches = [] if explorations is None else [
        record for record in explorations if record.get("id") == EXPLORATION_ID
    ]
    if not matches:
        audit.require(
            f"{EXPLORATION_ID} formal record complete",
            False,
            0,
            "one unique fully linked advanced record",
            "formal",
        )
    elif len(matches) != 1:
        audit.check(
            f"{EXPLORATION_ID} formal record complete",
            False,
            len(matches),
            1,
            "formal",
        )

    else:
        exploration = matches[0]
        serialized = json.dumps(exploration, sort_keys=True, ensure_ascii=True)
        needles = (NEXT_GATE, "EXP-000792", "EXP-000793", *declared_negatives)
        links = {needle: needle in serialized for needle in needles}
        formal_negatives = exploration.get("formal_refs", {}).get("negatives", [])
        formal_results = exploration.get("formal_refs", {}).get("results", [])
        try:
            result_ledger = (REPO / "RESULTS-LEDGER.md").read_text(encoding="utf-8")
        except (OSError, UnicodeError):
            result_ledger = ""
        result_authority_chain = (
            "R-167" in formal_results
            and "### R-167" in result_ledger
            and RESULT_ID in result_ledger
        )
        boundary_text = str(exploration.get("boundary", ""))
        boundary_checks = contains_all_boundaries(boundary_text)
        boundary_lower = boundary_text.lower()
        open_signal = any(
            phrase in boundary_lower
            for phrase in ("remain open", "remains open", "does not prove", "not prove")
        )
        conditions = {
            "unique": True,
            "verdict_advanced": exploration.get("verdict") == "advanced",
            "task_id": exploration.get("task_id") == TASK_ID,
            "links": all(links.values()),
            "formal_negatives": all(item in formal_negatives for item in declared_negatives),
            "result_authority_chain": result_authority_chain,
            "boundary_tokens": all(boundary_checks.values()),
            "boundary_open_signal": open_signal,
        }
        audit.check(
            f"{EXPLORATION_ID} formal record complete",
            all(conditions.values()),
            {
                "conditions": conditions,
                "links": links,
                "boundary_tokens": boundary_checks,
                "formal_negatives": formal_negatives,
                "formal_results": formal_results,
            },
            "all conditions true",
            "formal",
        )

    correction_matches = [] if explorations is None else [
        record for record in explorations if record.get("id") == CORRECTION_EXPLORATION_ID
    ]
    if not correction_matches:
        audit.require(
            f"{CORRECTION_EXPLORATION_ID} correction record complete",
            False,
            0,
            "one unique EXP-000794 scope correction",
            "scope_correction",
        )
    elif len(correction_matches) != 1:
        audit.check(
            f"{CORRECTION_EXPLORATION_ID} correction record complete",
            False,
            len(correction_matches),
            1,
            "scope_correction",
        )
    else:
        correction = correction_matches[0]
        correction_serialized = json.dumps(correction, sort_keys=True, ensure_ascii=True)
        correction_finding = str(correction.get("finding", ""))
        correction_lower = correction_finding.lower()
        correction_scope_lower = (
            correction_finding + "\n" + str(correction.get("boundary", ""))
        ).lower()
        related = correction.get("related", [])
        relation_exact = any(
            isinstance(item, dict)
            and item.get("id") == EXPLORATION_ID
            and item.get("relation") == "corrects"
            for item in related
        ) if isinstance(related, list) else False
        formal_results = correction.get("formal_refs", {}).get("results", [])
        correction_conditions = {
            "task_id": correction.get("task_id") == TASK_ID,
            "verdict_advanced": correction.get("verdict") == "advanced",
            "corrects_exp794": relation_exact,
            "result_link": (
                "R-167" in formal_results
                and "### R-167" in result_ledger
                and RESULT_ID in result_ledger
            ),
            "gate_link": NEXT_GATE in correction_serialized,
            "energy_domain_scope": "energy-domain" in correction_scope_lower or "energy domain" in correction_scope_lower,
            "cubic_multiplier_named": "cubic multiplier" in correction_scope_lower or "q^3" in correction_scope_lower,
            "cubic_multiplier_open": any(
                phrase in correction_scope_lower
                for phrase in ("remains open", "remain open", "not proved", "does not prove")
            ),
        }
        audit.check(
            f"{CORRECTION_EXPLORATION_ID} correction record complete",
            all(correction_conditions.values()),
            correction_conditions,
            "all conditions true",
            "scope_correction",
        )
        validate_cubic_scope_text(
            correction_finding + "\n" + str(correction.get("boundary", "")),
            CORRECTION_EXPLORATION_ID,
            audit,
        )

    registry = require_text(REPO / "negative-results/registry.md", audit, "negative registry")
    if registry is not None:
        for negative_id in declared_negatives:
            count = registry.count(negative_id)
            if count >= 2:
                audit.check(f"negative authority {negative_id}", True, count, ">=2 (index row and detail)", "formal")
            else:
                audit.require(f"negative authority {negative_id}", False, count, ">=2 (index row and detail)", "formal")

    gates = require_text(REPO / "claims/GATES.md", audit, "gate authority")
    if gates is not None:
        for needle in (
            EXPLORATION_ID,
            CORRECTION_EXPLORATION_ID,
            RESULT_ID,
            NEXT_GATE,
            "PARTIALLY RESOLVED",
        ):
            if needle in gates:
                audit.check(f"gate authority links {needle}", True, True, True, "formal")
            else:
                audit.require(f"gate authority links {needle}", False, False, True, "formal")

    todo = load_json(REPO / "todo/todo.json", audit, "TODO authority")
    if todo is not None:
        tasks = todo.get("tasks", [])
        matches = [task for task in tasks if isinstance(task, dict) and task.get("id") == TASK_ID]
        audit.check("T-054 unique", len(matches) == 1, len(matches), 1, "formal")
        if len(matches) == 1:
            task = matches[0]
            serialized = json.dumps(task, sort_keys=True, ensure_ascii=True)
            audit.check("T-054 in progress", task.get("status") == "in_progress", task.get("status"), "in_progress", "formal")
            for needle in (EXPLORATION_ID, CORRECTION_EXPLORATION_ID, RESULT_ID, NEXT_GATE):
                if needle in serialized:
                    audit.check(f"T-054 links {needle}", True, True, True, "formal")
                else:
                    audit.require(f"T-054 links {needle}", False, False, True, "formal")

    note = require_text(NOTE, audit, "source note")
    if note is not None:
        for needle in (
            EXPLORATION_ID,
            CORRECTION_EXPLORATION_ID,
            RESULT_ID,
            NEXT_GATE,
            *declared_negatives,
        ):
            audit.check(f"source note links {needle}", needle in note, needle in note, True, "formal")
        validate_no_overclaim_text(note, "source note", audit)
        validate_cubic_scope_text(note, "source note", audit)

    certificate = require_text(CERTIFICATE, audit, "certificate")
    if certificate is not None:
        for needle in (CORRECTION_EXPLORATION_ID, RESULT_ID, NEXT_GATE):
            audit.check(f"certificate links {needle}", needle in certificate, needle in certificate, True, "formal")
        validate_no_overclaim_text(certificate, "certificate", audit)
        validate_cubic_scope_text(certificate, "certificate", audit)

    status = load_json(
        REPO / "claims/C6-SPACETIME-SIGNATURE/status.json",
        audit,
        "C6 status",
        missing_is_authority=False,
    )
    if status is not None:
        audit.check("C6 tier unchanged", status.get("tier") == "T1", status.get("tier"), "T1", "claim_firewall")
        audit.check("C6 lifecycle unchanged", status.get("lifecycle") == "ACTIVE", status.get("lifecycle"), "ACTIVE", "claim_firewall")
        audit.check("C6 evidence unchanged", status.get("evidence_grade") == ["CONDITIONAL"], status.get("evidence_grade"), ["CONDITIONAL"], "claim_firewall")
        audit.check("C6 gate unchanged", status.get("open_gates") == ["C6-BCC-PREMISE-BLOCKED"], status.get("open_gates"), ["C6-BCC-PREMISE-BLOCKED"], "claim_firewall")

    return validate_pdf(audit)


def build_payload() -> dict[str, Any]:
    audit = Audit()
    manifest = load_json(MANIFEST, audit, "manifest", missing_is_authority=False) or {}
    validate_independence(audit)

    components: dict[str, dict[str, Any]] = {}
    sentinels: dict[str, str] = {}
    with tempfile.TemporaryDirectory(prefix="tect-exp794-integrated-") as directory:
        temporary = Path(directory)
        for label, script in (("primary", PRIMARY), ("independent", INDEPENDENT)):
            result = run_fresh(script, temporary / f"{label}.json", temporary, audit, label)
            if result is not None:
                components[f"{label}_fresh"], sentinels[label] = result

    for label, path in (("primary", PRIMARY_STORED), ("independent", INDEPENDENT_STORED)):
        stored = load_stored_against_fresh(
            path,
            components.get(f"{label}_fresh"),
            audit,
            label,
        )
        if stored is not None:
            components[f"{label}_stored"] = stored

    for label, minimum_count, owner in (
        ("primary", MINIMUM_PRIMARY_COUNT, PRIMARY),
        ("independent", MINIMUM_INDEPENDENT_COUNT, INDEPENDENT),
    ):
        payload = components.get(f"{label}_fresh")
        if payload is not None:
            validate_component(payload, f"{label} fresh", minimum_count, audit)
            validate_hash_map(payload, owner, audit, f"{label} fresh")

    if "primary_fresh" in components and "independent_fresh" in components:
        compare_exact_core(components["primary_fresh"], components["independent_fresh"], audit)
    else:
        audit.require("fresh exact cross-comparison", False, sorted(components), ["primary_fresh", "independent_fresh"], "cross_core")

    pdf_meta = validate_formal(manifest, audit)
    passed = sum(row["status"] == "PASS" for row in audit.rows)
    source_paths = (SCRIPT, PRIMARY, INDEPENDENT, MANIFEST, CERTIFICATE, PARENT_MANIFEST, NOTE, PDF)
    source_hashes = {
        path.relative_to(REPO).as_posix(): artifact_sha256(path)
        for path in source_paths
        if path.is_file()
    }
    component_summaries = {
        label: payload.get("summary")
        for label, payload in sorted(components.items())
    }
    return {
        "schema": f"tect/{SLUG}-integrated-result/1.0",
        "script_version": __version__,
        "result_id": RESULT_ID,
        "exploration_id": EXPLORATION_ID,
        "scope_correction_exploration": CORRECTION_EXPLORATION_ID,
        "task_id": TASK_ID,
        "next_gate": NEXT_GATE,
        "negative_ids": manifest.get("negative_ids", list(REQUIRED_NEGATIVE_IDS)),
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
        "component_summaries": component_summaries,
        "fresh_sentinels": sentinels,
        "derived": {
            "Q3_edges": 12,
            "Q3_degrees": [3] * 8,
            "C2_fixture": "13",
            "M_mu_squared_fixture": "700902/125",
            "v_mu_squared_fixture": "27/5",
            "first_order_det": "7/20",
            "squared_order_det": "-127/16",
            "cubic_identity_residual_terms": 0,
            "cubic_power_count_target": "3/4",
            "symmetric_cubic_power_count_target": "3/8",
            "cubic_multiplier_closed": False,
            "rung_amplitudes": [str(2**index) for index in range(9)],
            "convex_weighted_witness": "-1",
            "convex_weighted_trace": "48",
            "common_alpha_closed": False,
        },
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
        help="write INCOMPLETE output and exit zero when only authorities are missing",
    )
    arguments = parser.parse_args()
    payload = build_payload()
    atomic_json(arguments.output, payload)
    summary = payload["summary"]
    print(
        f"{EXPLORATION_ID}/{CORRECTION_EXPLORATION_ID} INTEGRATED {payload['verdict']} "
        f"{summary['passed']}/{summary['total']} "
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

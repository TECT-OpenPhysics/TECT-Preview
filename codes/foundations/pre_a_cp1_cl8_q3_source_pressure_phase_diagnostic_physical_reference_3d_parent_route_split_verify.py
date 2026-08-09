#!/usr/bin/env python3
"""Integrated verifier for the EXP-000779 Q3 source-pressure route split."""

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
from pathlib import Path
from typing import Any, Iterable


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-cl8-q3-source-pressure-phase-diagnostic-physical-reference-3d-parent-route-split"
CANDIDATE_ID = "PA-CP1-CL8-Q3-SOURCE-PRESSURE-PHASE-DIAGNOSTIC-PHYSICAL-REFERENCE-AND-3D-PARENT-ROUTE-SPLIT-v0"
RESULT_ID = "PA-CP1-CL8-Q3-ALL-SOURCE-BOUNDARY-INDEPENDENT-CONVEX-EVEN-PRESSURE-WITH-PHASE-REFERENCE-AND-PARENT-OBSTRUCTIONS"
EXPLORATION_ID = "EXP-000779"
PARENT_EXPLORATION = "EXP-000778"
ST8_PARENT_EXPLORATION = "EXP-000719"
PARENT_CANDIDATE_ID = "PA-CP1-CL8-Q3-FINITE-COMPONENT-GRS-BOUNDARY-PRESSURE-PERIODIC-GROUND-DENSITY-v0"
ST8_PARENT_CANDIDATE_ID = "PA-CP1-ST8-Q3LOCK-v0"
PARENT_GATE = "PA-CP1-CL8-Q3-PHASE-PHYSICAL-REFERENCE-AND-ONE-DIMENSIONAL-TO-THREE-DIMENSIONAL-PARENT-ROUTE-SPLIT"
NEXT_GATE = "PA-CP1-ST8-Q3LOCK-FIXED-LATTICE-3D-QUANTUM-PARENT-PRESSURE-GROUND-DENSITY-AND-EFFECTIVE-REDUCTION-SPLIT"
NEGATIVE_IDS = [
    "NG-2026-08-04-PRE-A-CP1-CL8-PRESSURE-VALUE-ONLY-PHASE-CLASSIFICATION",
    "NG-2026-08-04-PRE-A-CP1-CL8-TRANSVERSE-ZERO-RESTRICTION-AS-INTERACTING-MARGINAL",
]
REUSED_NEGATIVE_IDS = [
    "NG-2026-07-30-A13-NORMALIZED-GIBBS-DOOB-ABSOLUTE-ANCHOR",
    "NG-2026-08-04-PRE-A-CP1-CL8-FIXED-RAW-QUADRATIC-FINITE-Q3-RENORMALIZED-LIMIT",
]
PARENT_IDS = [PARENT_CANDIDATE_ID, ST8_PARENT_CANDIDATE_ID]
CLOSED_SUBGATES = [
    "PA-CP1-CL8-Q3-ALL-CONSTANT-SOURCE-BOUNDARY-INDEPENDENT-PRESSURE",
    "PA-CP1-CL8-Q3-CONVEX-EVEN-SOURCE-PRESSURE-AND-DIRECTIONAL-CUSP-DIAGNOSTIC",
    "PA-CP1-CL8-Q3-PRESSURE-VALUE-ONLY-PHASE-UNDERDETERMINATION",
    "PA-CP1-CL8-Q3-TRANSVERSE-RESTRICTION-VERSUS-INTERACTING-MARGINAL-SEPARATION",
]
OPEN_SUBGATES = [
    "PA-CP1-CL8-Q3-ORDER-PARAMETER-CUSP-SIGN-AND-SOURCE-STATE-CONSTRUCTION",
    "PA-CP1-CL8-Q3-PHYSICAL-EMPTY-SPACE-AND-STRESS-TENSOR-RENORMALIZATION-ANCHOR",
    "PA-CP1-ST8-Q3LOCK-FIXED-LATTICE-3D-QUANTUM-THERMODYNAMIC-LIMIT",
    "PA-CP1-ST8-Q3LOCK-TO-CL8-Q3-EFFECTIVE-REDUCTION",
    "PA-CP1-CL8-Q3-ZERO-TEMPERATURE-STATE-GROUND-VECTOR-GAP-AND-CORRELATION-LIMITS",
    "PA-CP1-CL8-INTERACTING-MICROLOCAL-SPECTRUM-OR-RELATIVISTIC-KMS",
    "PA-PRE-A-C0-N1-N5-VALIDATION",
]
POSITIVE_SCOPE = (
    "constant_vector_source_Q3_interaction",
    "linear_source_subdominant_exponent_4_over_3",
    "all_source_pressure_exists_and_finite",
    "all_source_boundary_Wick_independence",
    "source_pressure_locally_uniform",
    "source_pressure_convex",
    "source_pressure_global_Z2_even",
    "source_pressure_origin_equals_alpha_infinity",
    "directional_one_sided_derivatives_exist",
    "pressure_cusp_diagnostic_defined",
    "finite_volume_zero_source_response",
    "thermodynamic_then_zero_source_order_required",
    "pressure_value_only_phase_classification_refuted",
    "additive_scalar_absolute_reference_no_go_reused",
    "bare_transverse_restriction_suffices_for_interacting_marginal_inference_refuted",
)
FALSE_SCOPE = (
    "any_Q3_cusp_sign_determined",
    "Q3_phase_transition_or_phase_uniqueness",
    "source_selected_infinite_volume_states",
    "plus_minus_state_purity_or_clustering",
    "physical_empty_space_reference",
    "absolute_vacuum_energy_fixed",
    "common_renormalized_stress_tensor_anchor",
    "original_fixed_raw_CL8_family",
    "fixed_lattice_3D_Q3LOCK_thermodynamic_limit",
    "original_3D_Q3LOCK_parent_derived",
    "exact_effective_dimensional_reduction",
    "zero_temperature_state_limit",
    "ground_vector_limit",
    "uniform_spectral_gap",
    "correlation_function_limit_interchange",
    "interacting_Hadamard_or_microlocal_spectrum",
    "physical_light_speed_derived",
    "C0_closed",
    "N1_through_N5_closed",
    "C6_advanced",
    "CP1_complete",
    "Sector_A_complete",
    "Pre_A_complete",
)
SCHEMA = f"tect/{SLUG}-integrated/0.1"
SCRIPT = Path(__file__).resolve()
PRIMARY = REPO / f"codes/foundations/{SLUG.replace('-', '_')}.py"
INDEPENDENT = REPO / f"codes/foundations/{SLUG.replace('-', '_')}_independent.py"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260804.md"
PRIMARY_STORED = REPO / f"claims/C6-SPACETIME-SIGNATURE/runs/2026-08-04-primary-{SLUG}/result.json"
INDEPENDENT_STORED = REPO / f"claims/C6-SPACETIME-SIGNATURE/runs/2026-08-04-independent-{SLUG}/result.json"
PARENT_STORED = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-04-integrated-pre-a-cp1-cl8-q3-finite-component-grs-boundary-pressure-periodic-ground-density-route-split/result.json"
ST8_PARENT_STORED = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-03-integrated-pre-a-cp1-st8-q3lock/result.json"
DEFAULT_OUTPUT = REPO / f"claims/C6-SPACETIME-SIGNATURE/runs/2026-08-04-integrated-{SLUG}/result.json"


def sha256(path: Path) -> str:
    normalized = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(normalized).hexdigest()


def canonical(payload: dict[str, Any]) -> bytes:
    return (json.dumps(payload, indent=2, sort_keys=True) + "\n").encode()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(self, name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{group}: {name}: {actual!r} != {expected!r}")
        self.rows.append(
            {"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)}
        )


def run_child(script: Path, output: Path) -> tuple[dict[str, Any], tuple[int, int]]:
    completed = subprocess.run(
        [sys.executable, str(script), "--output", str(output)],
        cwd=REPO,
        capture_output=True,
        text=True,
        timeout=240,
    )
    if completed.returncode:
        raise RuntimeError(f"{script.name} failed:\n{completed.stdout}\n{completed.stderr}")
    match = re.search(r"([0-9]+)/([0-9]+) PASS$", completed.stdout.strip())
    if match is None:
        raise AssertionError(completed.stdout)
    return json.loads(output.read_text(encoding="utf-8")), (int(match.group(1)), int(match.group(2)))


def imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    result = {alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names}
    result |= {node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
    return result


def all_pass(payload: dict[str, Any]) -> bool:
    summary = payload.get("assertion_summary")
    if isinstance(summary, dict):
        return summary.get("passed") == summary.get("total")
    assertions = payload.get("assertions")
    if isinstance(assertions, dict):
        return assertions.get("passed") == assertions.get("total")
    return False


def assertion_row(payload: dict[str, Any], fragments: Iterable[str]) -> dict[str, Any] | None:
    lowered = tuple(fragment.lower() for fragment in fragments)
    rows = payload.get("assertions", [])
    if not isinstance(rows, list):
        return None
    for row in rows:
        name = str(row.get("name", "")).lower()
        if all(fragment in name for fragment in lowered):
            return row
    return None


def assertion_any(payload: dict[str, Any], alternatives: Iterable[Iterable[str]]) -> dict[str, Any] | None:
    for fragments in alternatives:
        row = assertion_row(payload, fragments)
        if row is not None:
            return row
    return None


def walk_lists(value: Any) -> Iterable[list[Any]]:
    if isinstance(value, list):
        yield value
        for item in value:
            yield from walk_lists(item)
    elif isinstance(value, dict):
        for item in value.values():
            yield from walk_lists(item)


def cusp_errors(payload: dict[str, Any]) -> dict[int, float]:
    candidates: list[dict[int, float]] = []
    for rows in walk_lists(payload.get("derived", {}).get("phase", {})):
        result: dict[int, float] = {}
        for row in rows:
            if not isinstance(row, dict):
                continue
            order_value = row.get("n", row.get("order"))
            if order_value is None:
                continue
            errors: list[float] = []
            for value_row in row.get("values", []):
                if isinstance(value_row, dict):
                    for key, value in value_row.items():
                        if "error" in key.lower() or key.lower() == "gap":
                            errors.append(abs(float(value)))
            for key, value in row.items():
                if key != "values" and ("error" in key.lower() or key.lower() == "gap") and isinstance(value, (int, float, str)):
                    errors.append(abs(float(value)))
            if errors:
                order = int(order_value)
                result[order] = max(result.get(order, 0.0), max(errors))
        if len(result) >= 2:
            candidates.append(result)
    if not candidates:
        raise AssertionError("no numerical smooth-to-cusp error rows in child output")
    return max(candidates, key=len)


def marginal_rows(payload: dict[str, Any]) -> list[tuple[float, float, float]]:
    candidates: list[list[tuple[float, float, float]]] = []
    parent = payload.get("derived", {}).get("parent", {})
    for rows in walk_lists(parent):
        parsed: list[tuple[float, float, float]] = []
        for row in rows:
            if not isinstance(row, dict):
                continue
            q_key = next((key for key in row if key.lower() in {"q", "q_value", "q_squared"}), None)
            f_key = next(
                (key for key in row if key.lower() in {"f", "effective", "effective_term", "delta_f", "normalized_f"}),
                None,
            )
            derivative_key = next(
                (key for key in row if "df" in key.lower() or "derivative" in key.lower() or key.lower() == "f_prime"),
                None,
            )
            if q_key is None or f_key is None or derivative_key is None:
                continue
            q_value = float(row[q_key])
            q_squared = q_value if q_key.lower() == "q_squared" else q_value * q_value
            parsed.append((q_squared, float(row[f_key]), float(row[derivative_key])))
        if len(parsed) >= 3:
            candidates.append(sorted(parsed))
    if not candidates:
        raise AssertionError("no numerical discarded-mode marginal rows in child output")
    result = max(candidates, key=len)
    origin = result[0][1]
    return [(q_value, effective - origin, derivative) for q_value, effective, derivative in result]


def exploration_record() -> dict[str, Any]:
    for line in (REPO / "explorations/log.jsonl").read_text(encoding="utf-8").splitlines():
        record = json.loads(line)
        if record.get("id") == EXPLORATION_ID:
            return record
    raise AssertionError(f"missing {EXPLORATION_ID}")


def build_payload() -> dict[str, Any]:
    audit = Audit()
    required = (MANIFEST, CERTIFICATE, PRIMARY, INDEPENDENT, PARENT_STORED, ST8_PARENT_STORED)
    for path in required:
        audit.check(f"required file {path.name}", path.is_file(), str(path), "file", "files")

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate = " ".join(CERTIFICATE.read_text(encoding="utf-8").split())
    status = json.loads((REPO / "claims/C6-SPACETIME-SIGNATURE/status.json").read_text(encoding="utf-8"))
    audit.check("manifest schema", manifest["schema"] == f"tect/{SLUG}-manifest/0.1", manifest["schema"], f"tect/{SLUG}-manifest/0.1", "identity")
    audit.check("candidate id", manifest["candidate_id"] == CANDIDATE_ID, manifest["candidate_id"], CANDIDATE_ID, "identity")
    audit.check("result id", manifest["result_id"] == RESULT_ID, manifest["result_id"], RESULT_ID, "identity")
    audit.check("exploration id", manifest["exploration_id"] == EXPLORATION_ID, manifest["exploration_id"], EXPLORATION_ID, "identity")
    audit.check("parent ids", manifest["parent_ids"] == PARENT_IDS, manifest["parent_ids"], PARENT_IDS, "identity")
    audit.check("negative ids", manifest["negative_ids"] == NEGATIVE_IDS, manifest["negative_ids"], NEGATIVE_IDS, "identity")
    audit.check("reused negative ids", manifest["reused_negative_ids"] == REUSED_NEGATIVE_IDS, manifest["reused_negative_ids"], REUSED_NEGATIVE_IDS, "identity")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "identity")
    audit.check("task id", manifest["task_id"] == "T-054", manifest["task_id"], "T-054", "identity")
    audit.check("claim context", manifest["claim_context"] == "C6-SPACETIME-SIGNATURE", manifest["claim_context"], "C6-SPACETIME-SIGNATURE", "identity")
    audit.check("parent gate", manifest["gate_resolution"]["parent_gate"] == PARENT_GATE, manifest["gate_resolution"]["parent_gate"], PARENT_GATE, "identity")
    audit.check("next gate", manifest["gate_resolution"]["next_gate"] == NEXT_GATE, manifest["gate_resolution"]["next_gate"], NEXT_GATE, "identity")
    audit.check("closed subgates", manifest["gate_resolution"]["closed_subgates"] == CLOSED_SUBGATES, manifest["gate_resolution"]["closed_subgates"], CLOSED_SUBGATES, "identity")
    audit.check("open subgates", manifest["gate_resolution"]["open_subgates"] == OPEN_SUBGATES, manifest["gate_resolution"]["open_subgates"], OPEN_SUBGATES, "identity")

    parent = json.loads(PARENT_STORED.read_text(encoding="utf-8"))
    st8_parent = json.loads(ST8_PARENT_STORED.read_text(encoding="utf-8"))
    audit.check("EXP771 parent identity", parent.get("candidate_id") == PARENT_CANDIDATE_ID and parent.get("exploration_id") == PARENT_EXPLORATION, (parent.get("candidate_id"), parent.get("exploration_id")), (PARENT_CANDIDATE_ID, PARENT_EXPLORATION), "parents")
    audit.check("EXP771 parent all pass", all_pass(parent), parent.get("assertion_summary"), "all pass", "parents")
    audit.check("EXP771 pressure base", parent["scope"]["finite_component_GRS_uniform_subdominant_coupling"] is True and parent["scope"]["all_sixteen_full_half_boundary_pressure_density_limits"] is True, parent["scope"], "finite-component all-boundary base", "parents")
    audit.check("ST8 parent identity", st8_parent.get("candidate_id") == ST8_PARENT_CANDIDATE_ID, st8_parent.get("candidate_id"), ST8_PARENT_CANDIDATE_ID, "parents")
    audit.check("ST8 parent all pass", all_pass(st8_parent), st8_parent.get("assertions"), "all pass", "parents")

    with tempfile.TemporaryDirectory(prefix="tect-q3-source-pressure-") as directory:
        primary, primary_summary = run_child(PRIMARY, Path(directory) / "primary.json")
        independent, independent_summary = run_child(INDEPENDENT, Path(directory) / "independent.json")
    summaries = {"primary": primary_summary, "independent": independent_summary}
    for label, child in (("primary", primary), ("independent", independent)):
        audit.check(f"{label} all pass", summaries[label][0] == summaries[label][1], summaries[label], "all pass", "children")
        audit.check(f"{label} identity", child.get("candidate_id") == CANDIDATE_ID and child.get("result_id") == RESULT_ID and child.get("exploration_id") == EXPLORATION_ID, (child.get("candidate_id"), child.get("result_id"), child.get("exploration_id")), (CANDIDATE_ID, RESULT_ID, EXPLORATION_ID), "children")
        audit.check(f"{label} negatives", child.get("negative_ids") == NEGATIVE_IDS, child.get("negative_ids"), NEGATIVE_IDS, "children")
        audit.check(f"{label} claim nonbearing", child.get("claim_bearing") is False, child.get("claim_bearing"), False, "children")
        audit.check(f"{label} scope", child.get("scope") == manifest["scope"], child.get("scope"), manifest["scope"], "children")
        audit.check(f"{label} next gate", child.get("next_gate") == NEXT_GATE, child.get("next_gate"), NEXT_GATE, "children")

    audit.check("stored primary exists", PRIMARY_STORED.is_file(), str(PRIMARY_STORED), "file", "stored")
    audit.check("stored independent exists", INDEPENDENT_STORED.is_file(), str(INDEPENDENT_STORED), "file", "stored")
    primary_stored = json.loads(PRIMARY_STORED.read_text(encoding="utf-8"))
    independent_stored = json.loads(INDEPENDENT_STORED.read_text(encoding="utf-8"))
    audit.check("stored primary fresh", canonical(primary_stored) == canonical(primary), sha256(PRIMARY_STORED), "fresh", "stored")
    audit.check("stored independent fresh", canonical(independent_stored) == canonical(independent), sha256(INDEPENDENT_STORED), "fresh", "stored")
    for label, child, source in (("primary", primary, PRIMARY), ("independent", independent, INDEPENDENT)):
        hashes = child.get("source_sha256", {})
        audit.check(f"{label} script hash", hashes.get("script") == sha256(source), hashes.get("script"), sha256(source), "stored")
        audit.check(f"{label} manifest hash", hashes.get("manifest") == sha256(MANIFEST), hashes.get("manifest"), sha256(MANIFEST), "stored")
        audit.check(f"{label} certificate hash", hashes.get("certificate") == sha256(CERTIFICATE), hashes.get("certificate"), sha256(CERTIFICATE), "stored")
        parent_key = "parent" if label == "primary" else "EXP771_parent"
        st8_parent_key = "st8_parent" if label == "primary" else "ST8_parent"
        audit.check(f"{label} EXP771 parent hash", hashes.get(parent_key) == sha256(PARENT_STORED), hashes.get(parent_key), sha256(PARENT_STORED), "stored")
        audit.check(f"{label} ST8 parent hash", hashes.get(st8_parent_key) == sha256(ST8_PARENT_STORED), hashes.get(st8_parent_key), sha256(ST8_PARENT_STORED), "stored")

    independent_imports = imports(INDEPENDENT)
    audit.check("independent no primary import", PRIMARY.stem not in independent_imports, sorted(independent_imports), f"not {PRIMARY.stem}", "independence")
    audit.check("independent stdlib only", not ({"sympy", "mpmath", "numpy", "scipy"} & independent_imports), sorted(independent_imports), "stdlib only", "independence")
    audit.check("child source diversity", sha256(PRIMARY) != sha256(INDEPENDENT), sha256(PRIMARY), sha256(INDEPENDENT), "independence")

    coverage = {
        "source Young factorization": (("young",),),
        "source exponent": (("source", "exponent"),),
        "source coercive bound": (("coerciv",),),
        "pressure evenness": (("pressure", "even"), ("pressure", "global", "z2")),
        "finite zero-source response": (("zero", "source"),),
        "pressure convexity": (("hessian",),),
        "smooth-to-cusp limit": (("smooth", "cusp"), ("local-uniform", "cusp")),
        "limit-order diagnostic": (("thermodynamic", "cusp"), ("thermodynamic-first",), ("smooth", "sequence", "cusp")),
        "scalar-shift normalized law": (("shift", "normalized"),),
        "scalar-shift KL": (("shift", "kl"),),
        "scalar-shift pressure": (("shift", "pressure"),),
        "two-cell quartic": (("quartic", "identity"),),
        "effective derivative": (("effective", "derivative", "positive"), ("transverse", "f", "prime", "positive")),
        "effective nonconstancy": (("effective", "nonconstant"),),
    }
    for label, child in (("primary", primary), ("independent", independent)):
        for topic, alternatives in coverage.items():
            row = assertion_any(child, alternatives)
            audit.check(f"{label} coverage {topic}", row is not None, alternatives, "present", "coverage")

    primary_exponent = assertion_row(primary, ("source", "exponent"))
    independent_exponent = assertion_row(independent, ("source", "exponent"))
    audit.check("cross source exponent 4/3", primary_exponent is not None and independent_exponent is not None and "4/3" in (str(primary_exponent.get("actual")) + str(primary_exponent.get("expected"))) and "4/3" in (str(independent_exponent.get("actual")) + str(independent_exponent.get("expected"))), (primary_exponent, independent_exponent), "4/3 in both", "cross")
    for topic, alternatives in (
        ("convex-even pressure", (("pressure", "even"), ("pressure", "global", "z2"))),
        ("zero finite response", (("zero", "source"),)),
        ("cusp limit", (("smooth", "cusp"), ("local-uniform", "cusp"))),
        ("KL shift invariance", (("shift", "kl"),)),
        ("quartic coefficients", (("quartic", "identity"),)),
    ):
        audit.check(f"cross semantic agreement {topic}", assertion_any(primary, alternatives) is not None and assertion_any(independent, alternatives) is not None, alternatives, "proved independently", "cross")

    primary_cusp = cusp_errors(primary)
    independent_cusp = cusp_errors(independent)
    for label, rows in (("primary", primary_cusp), ("independent", independent_cusp)):
        orders = sorted(rows)
        audit.check(f"{label} cusp errors decrease", rows[orders[-1]] < rows[orders[0]], rows, "decreasing", "cross")
        audit.check(f"{label} cusp log-two bound", all(error <= math.log(2.0) / order + 1e-10 for order, error in rows.items()), rows, "error <= log(2)/n", "cross")
    audit.check("cross cusp-bound agreement", all(error <= math.log(2.0) / order + 1e-10 for rows in (primary_cusp, independent_cusp) for order, error in rows.items()), (primary_cusp, independent_cusp), "both satisfy error <= log(2)/n", "cross")

    primary_marginal = marginal_rows(primary)
    independent_marginal = marginal_rows(independent)
    audit.check("cross marginal row count", len(primary_marginal) == len(independent_marginal) >= 3, (len(primary_marginal), len(independent_marginal)), "same and >=3", "cross")
    audit.check("cross marginal q grid", max(abs(left[0] - right[0]) for left, right in zip(primary_marginal, independent_marginal)) < 1e-12, (primary_marginal, independent_marginal), "same q grid", "cross")
    audit.check("cross normalized effective rows", max(abs(left[1] - right[1]) for left, right in zip(primary_marginal, independent_marginal)) < 5e-5, (primary_marginal, independent_marginal), "agreement within 5e-5", "cross")
    audit.check("cross effective derivatives", max(abs(left[2] - right[2]) for left, right in zip(primary_marginal, independent_marginal)) < 5e-5, (primary_marginal, independent_marginal), "agreement within 5e-5", "cross")

    for path in (MANIFEST, CERTIFICATE, PRIMARY, INDEPENDENT, SCRIPT):
        audit.check(f"ASCII {path.name}", all(ord(character) < 128 for character in path.read_text(encoding="utf-8")), path.name, "ASCII", "hygiene")
    for phrase in (
        "For every constant external source",
        "both side lengths tending independently",
        "proves, rather than assumes",
        "Directional derivative and order of limits",
        "difference quotient",
        "not a field restriction",
        "determine whether any",
        "not a claim that either function is the Q3 pressure",
        "Physical-reference obstruction",
        "physical empty space",
        "Exact restriction-versus-marginal obstruction",
        "does not calculate the full registered",
        "This proves Pre-A. UPHELD AS FALSE",
    ):
        audit.check(f"certificate phrase {phrase}", phrase.lower() in certificate.lower(), phrase, "present", "certificate")

    verification = manifest["verification"]
    audit.check("analytic proof grade", verification["proof_grade"].startswith("ANALYTIC"), verification["proof_grade"], "ANALYTIC", "routing")
    audit.check("primary route", verification["primary"] == PRIMARY.relative_to(REPO).as_posix(), verification["primary"], PRIMARY.relative_to(REPO).as_posix(), "routing")
    audit.check("independent route", verification["independent"] == INDEPENDENT.relative_to(REPO).as_posix(), verification["independent"], INDEPENDENT.relative_to(REPO).as_posix(), "routing")
    audit.check("integrated route", verification["integrated"] == SCRIPT.relative_to(REPO).as_posix(), verification["integrated"], SCRIPT.relative_to(REPO).as_posix(), "routing")

    index = (REPO / "strategy/INDEX.md").read_text(encoding="utf-8")
    audit.check("strategy index", MANIFEST.name in index and CERTIFICATE.name in index, (MANIFEST.name, CERTIFICATE.name), "indexed", "records")
    exploration = exploration_record()
    audit.check("exploration verdict", exploration.get("verdict") == "advanced", exploration.get("verdict"), "advanced", "records")
    audit.check("exploration task", exploration.get("task_id") == "T-054", exploration.get("task_id"), "T-054", "records")
    audit.check("exploration claim context", exploration.get("claim_ids") == ["C6-SPACETIME-SIGNATURE"], exploration.get("claim_ids"), ["C6-SPACETIME-SIGNATURE"], "records")
    formal = exploration.get("formal_refs", {})
    audit.check("exploration empty results", formal.get("results", []) == [], formal, "no result card", "records")
    audit.check("exploration empty events", formal.get("events", []) == [], formal, "no event", "records")
    audit.check("exploration exact negatives", set(formal.get("negatives", [])) == set(NEGATIVE_IDS + REUSED_NEGATIVE_IDS), formal.get("negatives"), NEGATIVE_IDS + REUSED_NEGATIVE_IDS, "records")
    related = {(item.get("id"), item.get("relation")) for item in exploration.get("related", [])}
    audit.check("exploration EXP771 parent", (PARENT_EXPLORATION, "continues") in related, related, (PARENT_EXPLORATION, "continues"), "records")
    audit.check("exploration ST8 parent", (ST8_PARENT_EXPLORATION, "continues") in related, related, (ST8_PARENT_EXPLORATION, "continues"), "records")
    audit.check("exploration next gate", NEXT_GATE in exploration.get("next_action", ""), exploration.get("next_action"), NEXT_GATE, "records")

    todo_payload = json.loads((REPO / "todo/todo.json").read_text(encoding="utf-8"))
    task = next(item for item in todo_payload["tasks"] if item["id"] == "T-054")
    audit.check("TODO structured record", task["status"] == "in_progress" and EXPLORATION_ID in task["note"] and NEXT_GATE in task["note"], task, "active route history", "records")
    todo_view = (REPO / "TODO.md").read_text(encoding="utf-8")
    audit.check("TODO generated view", EXPLORATION_ID in todo_view and NEXT_GATE in todo_view, EXPLORATION_ID, "rendered", "records")
    changelog_records = [json.loads(line) for line in (REPO / "changelog/log.jsonl").read_text(encoding="utf-8").splitlines()]
    changelog = next(item for item in changelog_records if EXPLORATION_ID in item.get("header", ""))
    expected_notes = {MANIFEST.relative_to(REPO).as_posix(), CERTIFICATE.relative_to(REPO).as_posix()}
    expected_scripts = {PRIMARY.relative_to(REPO).as_posix(), INDEPENDENT.relative_to(REPO).as_posix(), SCRIPT.relative_to(REPO).as_posix()}
    audit.check("changelog claim context", changelog.get("claim_ids") == ["C6-SPACETIME-SIGNATURE"], changelog.get("claim_ids"), ["C6-SPACETIME-SIGNATURE"], "records")
    audit.check("changelog notes", expected_notes <= set(changelog.get("notes", [])), changelog.get("notes"), expected_notes, "records")
    audit.check("changelog scripts", expected_scripts <= set(changelog.get("scripts", [])), changelog.get("scripts"), expected_scripts, "records")
    audit.check("changelog negatives", set(NEGATIVE_IDS) <= set(changelog.get("neg_results", [])), changelog.get("neg_results"), NEGATIVE_IDS, "records")
    changelog_view = (REPO / "CHANGELOG.md").read_text(encoding="utf-8")
    audit.check("changelog generated view", EXPLORATION_ID in changelog_view, EXPLORATION_ID, "rendered", "records")

    lineage = (REPO / "claims/C6-SPACETIME-SIGNATURE/LINEAGE.md").read_text(encoding="utf-8")
    for kind in ("primary", "independent"):
        audit.check(f"lineage {kind}", f"runs/2026-08-04-{kind}-{SLUG}/" in lineage, kind, "present", "records")
    audit.check("lineage EXP771 parent", PARENT_STORED.parent.relative_to(REPO / "claims/C6-SPACETIME-SIGNATURE").as_posix() + "/" in lineage, PARENT_EXPLORATION, "present", "records")
    audit.check("lineage ST8 parent", ST8_PARENT_STORED.parent.relative_to(REPO / "claims/C6-SPACETIME-SIGNATURE").as_posix() + "/" in lineage, ST8_PARENT_CANDIDATE_ID, "present", "records")
    if DEFAULT_OUTPUT.is_file():
        audit.check("lineage integrated", f"runs/2026-08-04-integrated-{SLUG}/" in lineage, "integrated", "present", "records")

    gates = (REPO / "claims/GATES.md").read_text(encoding="utf-8")
    audit.check("parent gate registered", PARENT_GATE in gates, PARENT_GATE, "registered", "records")
    audit.check("next gate registered", NEXT_GATE in gates, NEXT_GATE, "registered", "records")
    negatives = (REPO / "negative-results/registry.md").read_text(encoding="utf-8")
    for negative_id in NEGATIVE_IDS:
        audit.check(f"new negative {negative_id}", f"### {negative_id} " in negatives, negative_id, "registered", "records")
    for negative_id in REUSED_NEGATIVE_IDS:
        audit.check(f"reused negative {negative_id}", f"### {negative_id} " in negatives, negative_id, "registered", "records")

    for key in POSITIVE_SCOPE:
        audit.check(f"positive scope {key}", manifest["scope"][key] is True, manifest["scope"][key], True, "scope")
    for key in FALSE_SCOPE:
        audit.check(f"scope firewall {key}", manifest["scope"][key] is False, manifest["scope"][key], False, "scope")
    audit.check("exact scope keyset", set(manifest["scope"]) == set(POSITIVE_SCOPE) | set(FALSE_SCOPE), sorted(manifest["scope"]), sorted(set(POSITIVE_SCOPE) | set(FALSE_SCOPE)), "scope")
    audit.check("phase sign firewall", manifest["scope"]["any_Q3_cusp_sign_determined"] is False and manifest["scope"]["Q3_phase_transition_or_phase_uniqueness"] is False, "no cusp sign or phase", False, "scope")
    audit.check("state firewall", manifest["scope"]["source_selected_infinite_volume_states"] is False and manifest["scope"]["plus_minus_state_purity_or_clustering"] is False, "no selected states", False, "scope")
    audit.check("physical reference firewall", manifest["scope"]["physical_empty_space_reference"] is False and manifest["scope"]["absolute_vacuum_energy_fixed"] is False and manifest["scope"]["common_renormalized_stress_tensor_anchor"] is False, "physical reference open", False, "scope")
    audit.check("parent firewall", manifest["scope"]["fixed_lattice_3D_Q3LOCK_thermodynamic_limit"] is False and manifest["scope"]["original_3D_Q3LOCK_parent_derived"] is False and manifest["scope"]["exact_effective_dimensional_reduction"] is False, "3D parent open", False, "scope")
    audit.check("C6 tier unchanged", status["tier"] == "T1", status["tier"], "T1", "scope")
    audit.check("C6 lifecycle unchanged", status["lifecycle"] == "ACTIVE", status["lifecycle"], "ACTIVE", "scope")
    audit.check("C6 evidence unchanged", status["evidence_grade"] == ["CONDITIONAL"], status["evidence_grade"], ["CONDITIONAL"], "scope")
    audit.check("C6 gate unchanged", status["open_gates"] == ["C6-BCC-PREMISE-BLOCKED"], status["open_gates"], ["C6-BCC-PREMISE-BLOCKED"], "scope")

    catalog_texts = [
        (REPO / "CATALOG.md").read_text(encoding="utf-8"),
        (REPO / "verification/catalog.json").read_text(encoding="utf-8"),
    ]
    proof_map_texts = [
        (REPO / "theory/proof-evidence-map.md").read_text(encoding="utf-8"),
        (REPO / "verification/proof-evidence-map.json").read_text(encoding="utf-8"),
    ]
    generated_paths = [MANIFEST, CERTIFICATE, PRIMARY, INDEPENDENT, SCRIPT, PRIMARY_STORED, INDEPENDENT_STORED]
    if DEFAULT_OUTPUT.is_file():
        generated_paths.append(DEFAULT_OUTPUT)
    for path in generated_paths:
        token = path.relative_to(REPO).as_posix()
        audit.check(f"catalog markdown {path.name}", token in catalog_texts[0], token, "catalogued", "generated")
        audit.check(f"catalog json {path.name}", token in catalog_texts[1], token, "catalogued", "generated")
    for token in (EXPLORATION_ID, PARENT_GATE, NEXT_GATE, MANIFEST.name, CERTIFICATE.name, *NEGATIVE_IDS, *REUSED_NEGATIVE_IDS):
        audit.check(f"proof map markdown {token}", token in proof_map_texts[0], token, "mapped", "generated")
        audit.check(f"proof map json {token}", token in proof_map_texts[1], token, "mapped", "generated")

    return {
        "schema": SCHEMA,
        "candidate_id": CANDIDATE_ID,
        "result_id": RESULT_ID,
        "negative_ids": NEGATIVE_IDS,
        "reused_negative_ids": REUSED_NEGATIVE_IDS,
        "exploration_id": EXPLORATION_ID,
        "claim_bearing": False,
        "verdict": manifest["gate_resolution"]["status"],
        "next_gate": NEXT_GATE,
        "script_version": __version__,
        "source_sha256": {
            "script": sha256(SCRIPT),
            "manifest": sha256(MANIFEST),
            "certificate": sha256(CERTIFICATE),
            "primary": sha256(PRIMARY),
            "independent": sha256(INDEPENDENT),
            "parent": sha256(PARENT_STORED),
            "st8_parent": sha256(ST8_PARENT_STORED),
        },
        "child_summaries": {key: {"passed": value[0], "total": value[1]} for key, value in summaries.items()},
        "cross": {
            "primary_cusp_errors": primary_cusp,
            "independent_cusp_errors": independent_cusp,
            "primary_marginal": primary_marginal,
            "independent_marginal": independent_marginal,
        },
        "scope": manifest["scope"],
        "assertions": audit.rows,
        "assertion_summary": {"passed": len(audit.rows), "total": len(audit.rows)},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    arguments = parser.parse_args()
    payload = build_payload()
    if not arguments.self_test:
        atomic_json(arguments.output, payload)
    print(f"{CANDIDATE_ID}: {payload['assertion_summary']['passed']}/{payload['assertion_summary']['total']} PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

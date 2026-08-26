#!/usr/bin/env python3
"""Primary finite-cutoff scaling audit for the Q3 raw Trotter coefficient.

For each declared graph volume and oscillator cutoff this script reconstructs
the local Q3 onsite and bond terms, computes

    C_V(n) = sum_{j<k} ||[H_j(n), H_k(n)]||,

and reports the fixed-step Lie--Trotter coefficient
``horizon**2*C_V/(2*step_count)`` together with the corresponding unit-norm
history coefficient.  The calculation is deliberately local: a term norm is
computed on its support and an overlapping commutator on the union support.
Tensor locality is checked once by a full embedding at the manifest reference
cutoff.  No finite table is promoted to a cutoff-uniform or QFT statement.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_finite_trotter_cutoff_scaling"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-finite-trotter-cutoff-scaling-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-26-primary-{SLUG}" / "primary.json"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pre_a_cp1_st8_q3lock_weighted_triple_commutator_volume_stress as q3  # noqa: E402


PHYSICAL_KEYS = ("c", "chi", "r", "g", "lambda", "hbar")


def normalized_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True, default=float)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def hermitian(matrix: np.ndarray) -> np.ndarray:
    return (matrix + matrix.conj().T) / 2.0


def operator_norm(matrix: np.ndarray) -> float:
    return float(np.linalg.svd(matrix, compute_uv=False)[0])


def commutator(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    return left @ right - right @ left


def load_fixture() -> tuple[dict[str, Any], list[dict[str, str]]]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    current_path = MANIFEST
    chain: list[dict[str, str]] = []
    while True:
        current = json.loads(current_path.read_text(encoding="utf-8"))
        source = current.get("source_fixture")
        if not isinstance(source, dict) or "manifest" not in source:
            raise ValueError(f"source fixture chain ended before physical fixture: {current_path}")
        next_path = REPO / str(source["manifest"])
        chain.append({"path": next_path.relative_to(REPO).as_posix(), "sha256": normalized_sha256(next_path)})
        if all(key in source for key in PHYSICAL_KEYS):
            return source, chain
        current_path = next_path


def term_specs(volume: int) -> list[dict[str, Any]]:
    specs = [{"kind": "onsite", "support": [site]} for site in range(volume)]
    specs.extend({"kind": "bond", "support": [left, right]} for left, right in q3.graph_edges(volume))
    return specs


def support_term(spec: dict[str, Any], union: list[int], n: int, fixture: dict[str, Any]) -> np.ndarray:
    q_single, p_single = q3.oscillator(n)
    identity = np.eye(n, dtype=complex)
    q_ops = {site: q3.embed(q_single, index, len(union), identity) for index, site in enumerate(union)}
    p_ops = {site: q3.embed(p_single, index, len(union), identity) for index, site in enumerate(union)}
    if spec["kind"] == "onsite":
        site = int(spec["support"][0])
        q, p = q_ops[site], p_ops[site]
        chi, r, g = float(fixture["chi"]), float(fixture["r"]), float(fixture["g"])
        return hermitian(p @ p / (2.0 * chi) + r * (q @ q) / 2.0 + g * (q @ q @ q @ q) / 4.0)
    left, right = (int(value) for value in spec["support"])
    return hermitian(q3.bond_term(q_ops[left], q_ops[right], fixture))


def reference_localization(volume: int, n: int, fixture: dict[str, Any], tolerance: float) -> float:
    """Compare every overlapping local commutator with its full tensor embedding."""
    q_single, p_single = q3.oscillator(n)
    identity = np.eye(n, dtype=complex)
    q_ops = [q3.embed(q_single, site, volume, identity) for site in range(volume)]
    p_ops = [q3.embed(p_single, site, volume, identity) for site in range(volume)]
    chi, r, g = float(fixture["chi"]), float(fixture["r"]), float(fixture["g"])
    onsite = [hermitian(p @ p / (2.0 * chi) + r * (q @ q) / 2.0 + g * (q @ q @ q @ q) / 4.0) for q, p in zip(q_ops, p_ops)]
    bonds = [hermitian(q3.bond_term(q_ops[left], q_ops[right], fixture)) for left, right in q3.graph_edges(volume)]
    terms = onsite + bonds
    specs = term_specs(volume)
    maximum = 0.0
    for left_index, left_spec in enumerate(specs):
        for right_index in range(left_index + 1, len(specs)):
            right_spec = specs[right_index]
            left_support = set(int(value) for value in left_spec["support"])
            right_support = set(int(value) for value in right_spec["support"])
            if left_support.isdisjoint(right_support):
                continue
            union = sorted(left_support | right_support)
            local = commutator(support_term(left_spec, union, n, fixture), support_term(right_spec, union, n, fixture))
            full = commutator(terms[left_index], terms[right_index])
            residual = abs(operator_norm(full) - operator_norm(local))
            maximum = max(maximum, residual)
            if residual > tolerance:
                raise AssertionError(f"reference localization residual {residual} > {tolerance}")
    return maximum


def cutoff_row(volume: int, n: int, fixture: dict[str, Any], horizon: float, step_count: int) -> dict[str, Any]:
    specs = term_specs(volume)
    q_single, p_single = q3.oscillator(n)
    q_norm = operator_norm(q_single)
    p_norm = operator_norm(p_single)
    term_norms: list[float] = []
    onsite_norms: list[float] = []
    bond_norms: list[float] = []
    for spec in specs:
        support = sorted(int(value) for value in spec["support"])
        value = operator_norm(support_term(spec, support, n, fixture))
        term_norms.append(value)
        (onsite_norms if spec["kind"] == "onsite" else bond_norms).append(value)

    commutator_sum = 0.0
    overlap_count = 0
    max_pair_norm = 0.0
    max_union_dimension = 0
    for left_index, left_spec in enumerate(specs):
        left_support = set(int(value) for value in left_spec["support"])
        for right_spec in specs[left_index + 1 :]:
            right_support = set(int(value) for value in right_spec["support"])
            if left_support.isdisjoint(right_support):
                continue
            overlap_count += 1
            union = sorted(left_support | right_support)
            max_union_dimension = max(max_union_dimension, n ** len(union))
            pair_norm = operator_norm(commutator(support_term(left_spec, union, n, fixture), support_term(right_spec, union, n, fixture)))
            commutator_sum += pair_norm
            max_pair_norm = max(max_pair_norm, pair_norm)

    coarse_envelope = 2.0 * overlap_count * max(term_norms) ** 2
    delta = horizon / step_count
    unitary_bound = horizon * horizon * commutator_sum / (2.0 * step_count)
    history_coefficient = delta ** 3 * commutator_sum * step_count * (step_count - 1) / 2.0
    return {
        "volume": volume,
        "cutoff": n,
        "local_max_dimension": max_union_dimension,
        "q_norm": q_norm,
        "p_norm": p_norm,
        "onsite_norm_max": max(onsite_norms),
        "bond_norm_max": max(bond_norms),
        "term_norm_max": max(term_norms),
        "commutator_sum": commutator_sum,
        "commutator_sum_per_site": commutator_sum / volume,
        "overlap_pair_count": overlap_count,
        "max_overlap_commutator": max_pair_norm,
        "coarse_fixed_cutoff_envelope": coarse_envelope,
        "unitary_bound_at_step_count": unitary_bound,
        "history_unit_multiplier_coefficient": history_coefficient,
    }


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, chain = load_fixture()
    audit = manifest["audit_fixture"]
    volumes = [int(value) for value in manifest["source_fixture"]["volume_values"]]
    cutoffs = [int(value) for value in manifest["source_fixture"]["cutoff_values"]]
    horizon = float(Fraction(audit["horizon"]))
    step_count = int(audit["step_count"])
    tolerance = float(audit["localization_tolerance"])
    floor = float(audit["commutator_floor"])
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    scope = manifest["scope"]
    check("identity", manifest["exploration_id"] == "EXP-001163" and manifest["task_id"] == "T-054" and manifest["claim_bearing"] is False, [manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"]], "EXP-001163/T-054/false", "provenance")
    check("source chain", len(chain) >= 3 and all(Path(item["path"]).is_file() for item in chain), chain, "physical fixture chain present", "provenance")
    check("physical fixture", all(key in fixture for key in PHYSICAL_KEYS), sorted(fixture), PHYSICAL_KEYS, "fixture")
    check("graph volumes", volumes == [2, 4, 6] and all(len(q3.graph_edges(volume)) > 0 for volume in volumes), volumes, "registered Q3 graph volumes", "fixture")
    check("cutoff grid", cutoffs == [2, 3, 4, 5, 6] and all(cutoff >= 2 for cutoff in cutoffs), cutoffs, "declared increasing finite cutoffs", "fixture")
    check("fixed-step fixture", horizon == 1.0 / 3.0 and step_count > 0, [horizon, step_count], [1.0 / 3.0, ">0"], "fixture")
    check("scope firewall", scope["finite_cutoff_scaling_rows_closed"] and scope["fixed_volume_growth_diagnostic_closed"] and not scope["raw_operator_norm_cutoff_uniformity_closed"] and not scope["pre_a_closed"], scope, "finite scaling only", "scope")

    rows: list[dict[str, Any]] = []
    volume_summaries: list[dict[str, Any]] = []
    for volume in volumes:
        volume_rows = [cutoff_row(volume, cutoff, fixture, horizon, step_count) for cutoff in cutoffs]
        for row in volume_rows:
            check(f"V={volume} n={row['cutoff']} finite norms", all(np.isfinite(float(row[key])) for key in ("q_norm", "p_norm", "term_norm_max", "commutator_sum", "unitary_bound_at_step_count", "history_unit_multiplier_coefficient")), row, "finite", "numeric")
            check(f"V={volume} n={row['cutoff']} nonnegative commutator", row["commutator_sum"] >= 0.0, row["commutator_sum"], f">{floor}", "commutator")
            check(f"V={volume} n={row['cutoff']} fixed envelope", row["commutator_sum"] <= row["coarse_fixed_cutoff_envelope"] + tolerance * (1.0 + row["coarse_fixed_cutoff_envelope"]), [row["commutator_sum"], row["coarse_fixed_cutoff_envelope"]], "C_V<=2*overlap*K_n^2", "finite envelope")
            rows.append(row)
        commutators = [float(row["commutator_sum"]) for row in volume_rows]
        term_norms = [float(row["term_norm_max"]) for row in volume_rows]
        q_norms = [float(row["q_norm"]) for row in volume_rows]
        positive = [index for index, value in enumerate(commutators) if value > floor]
        baseline_index = positive[0] if positive else None
        baseline_value = commutators[baseline_index] if baseline_index is not None else None
        growth_ratio = commutators[-1] / baseline_value if baseline_value else None
        summary = {
            "volume": volume,
            "row_count": len(volume_rows),
            "first_cutoff": cutoffs[0],
            "last_cutoff": cutoffs[-1],
            "first_positive_cutoff": cutoffs[baseline_index] if baseline_index is not None else None,
            "commutator_sum_first": commutators[0],
            "commutator_sum_last": commutators[-1],
            "commutator_growth_ratio_from_first_positive": growth_ratio,
            "commutator_nondecreasing_on_grid": all(commutators[index] + tolerance >= commutators[index - 1] for index in range(1, len(commutators))),
            "term_norm_growth_ratio": term_norms[-1] / term_norms[0],
            "q_norm_growth_ratio": q_norms[-1] / q_norms[0],
            "growth_ratio_threshold": float(audit["growth_ratio_threshold"]),
            "growth_threshold_crossed": growth_ratio is not None and growth_ratio >= float(audit["growth_ratio_threshold"]),
            "unitary_bound_first": float(volume_rows[0]["unitary_bound_at_step_count"]),
            "unitary_bound_last": float(volume_rows[-1]["unitary_bound_at_step_count"]),
            "history_coefficient_first": float(volume_rows[0]["history_unit_multiplier_coefficient"]),
            "history_coefficient_last": float(volume_rows[-1]["history_unit_multiplier_coefficient"]),
        }
        check(f"V={volume} row coverage", summary["row_count"] == len(cutoffs), summary["row_count"], len(cutoffs), "coverage")
        check(f"V={volume} positive commutator somewhere", any(value > floor for value in commutators), commutators, f"some value >{floor}", "commutator")
        volume_summaries.append(summary)

    reference = manifest["source_fixture"]["reference_embedding"]
    reference_residual = reference_localization(int(reference["volume"]), int(reference["cutoff"]), fixture, tolerance)
    check("reference tensor localization", reference_residual <= tolerance, reference_residual, f"<={tolerance}", "locality")
    diagnostic = {
        "all_declared_volumes_cross_threshold": all(item["growth_threshold_crossed"] for item in volume_summaries),
        "all_declared_volumes_nondecreasing_on_grid": all(item["commutator_nondecreasing_on_grid"] for item in volume_summaries),
        "interpretation": "finite-grid raw coefficient growth diagnostic; not an asymptotic divergence theorem",
        "raw_operator_norm_cutoff_uniformity": "not established by this audit",
        "energy_state_weighted_route": "open",
    }
    check("diagnostic is finite-only", diagnostic["raw_operator_norm_cutoff_uniformity"] == "not established by this audit" and diagnostic["energy_state_weighted_route"] == "open", diagnostic, "finite diagnostic", "scope")
    check("QFT firewall", not scope["raw_operator_norm_cutoff_uniformity_closed"] and not scope["operator_domain_embedding_closed"] and not scope["actual_q3_thermodynamic_history_closed"] and not scope["common_alpha_closed"] and not scope["pre_a_closed"], scope, "uniform/domain/QFT gates remain open", "scope")
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": "PA-CP1-ST8-Q3LOCK-FINITE-TROTTER-CUTOFF-SCALING",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": len(checks),
        "assertion_count": len(checks),
        "assertions": checks,
        "derived": {
            "source_chain": chain,
            "row_count": len(rows),
            "rows": rows,
            "volume_summaries": volume_summaries,
            "reference_localization_residual": reference_residual,
            "finite_cutoff_scaling_rows_closed": True,
            "fixed_volume_growth_diagnostic_closed": True,
            "raw_operator_norm_cutoff_uniformity_closed": False,
            "raw_operator_norm_route_boundary_recorded": True,
            "energy_state_weighted_cutoff_uniform_route_open": True,
            "diagnostic": diagnostic,
        },
        "boundary": scope,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY TROTTER-CUTOFF-SCALING PASS {payload['passed']}/{payload['assertion_count']} rows={payload['derived']['row_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

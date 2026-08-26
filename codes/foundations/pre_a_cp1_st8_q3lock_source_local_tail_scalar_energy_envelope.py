#!/usr/bin/env python3
"""Primary source-edge scalar tail-envelope audit (EXP-001191).

The scalar part proves a contraction-only polynomial envelope for one source
edge.  The matrix part evaluates the same edge tail in the inherited finite
Q3 fixtures with full and source-local shifted Hamiltonian quotients.  The
scalar envelope is deliberately not promoted to an operator fourth-power
inequality because the kinetic term does not commute with the coordinate
tail.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-st8-q3lock-source-local-tail-scalar-energy-envelope"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-27-primary-{SLUG}" / "primary.json"

sys.path.insert(0, str(Path(__file__).resolve().parent))
import pre_a_cp1_st8_q3lock_weighted_triple_commutator_volume_stress as q3  # noqa: E402


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


def load_fixture(manifest: dict[str, Any]) -> tuple[dict[str, Any], list[str]]:
    current = manifest
    lineage: list[str] = []
    while "finite_fixture" not in current:
        lineage.append(str(current.get("exploration_id", "unknown")))
        current = json.loads((REPO / current["fixture_source"]).read_text(encoding="utf-8"))
    lineage.append(str(current.get("exploration_id", "unknown")))
    return current["finite_fixture"], lineage


def rat(value: Any) -> Fraction:
    return Fraction(str(value))


def bond_scalar(x: Fraction, y: Fraction, c: Fraction, lam: Fraction) -> Fraction:
    difference = x - y
    return c * difference**2 / 2 + lam * difference**2 * (x**2 + y**2) / 4


def onsite_scalar(x: Fraction, r: Fraction, g: Fraction) -> Fraction:
    return r * x**2 / 2 + g * x**4 / 4


def hermitian(matrix: np.ndarray) -> np.ndarray:
    return (matrix + matrix.conj().T) / 2.0


def spectral_inverse_power(matrix: np.ndarray, exponent: float) -> tuple[np.ndarray, float]:
    values, vectors = np.linalg.eigh(hermitian(matrix))
    minimum = float(np.min(values))
    if minimum <= 0.0:
        raise ValueError(f"shifted matrix is not positive: min={minimum}")
    return (vectors * np.power(values, -exponent)) @ vectors.conj().T, minimum


def operator_norm(matrix: np.ndarray) -> float:
    return float(np.linalg.svd(matrix, compute_uv=False)[0])


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, fixture_lineage = load_fixture(manifest)
    finite_test = manifest["finite_test"]
    scope = manifest["scope"]
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001191" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001191/T-054", "provenance")
    check("fixture lineage", fixture_lineage[-1] == "EXP-001188", fixture_lineage, "EXP-001190 -> EXP-001189 -> EXP-001188", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("scope firewall", scope["scalar_contraction_bond_envelope_closed"] and scope["scalar_local_fourth_tail_envelope_closed"] and scope["finite_source_edge_tail_rows_closed"] and scope["finite_local_quotient_rows_closed"] and scope["source_volume_uniform_scalar_constant_closed"] and not scope["operator_fourth_order_envelope_closed"] and not scope["gibbs_local_fourth_moment_uniform_closed"] and not scope["common_alpha_closed"] and not scope["pre_a_closed"], scope, "scalar/finite only; operator and QFT gates open", "scope")

    c, lam, g, r = (rat(fixture[key]) for key in ("c", "lambda", "g", "r"))
    if not (c >= 0 and lam >= 0 and g > 0):
        raise ValueError("inherited Q3 coefficients do not satisfy the scalar hypotheses")
    shift_per_site = r**2 / (4 * g)
    scalar_factor = Fraction(8, 1) / g
    tail_factor = 2 * (c + lam) * scalar_factor
    fourth_constant = tail_factor**4
    residual = 1 + 4 * (r / g) ** 2 - scalar_factor
    check("onsite residual", residual <= 0, residual, "<=0", "scalar coercivity")
    check("tail factor positive", tail_factor > 0, tail_factor, ">0", "scalar envelope")

    scalar_rows: list[dict[str, Any]] = []
    fields = [rat(value) for value in finite_test["field_values"]]
    factors = [rat(value) for value in finite_test["contraction_factors"]]
    for x in fields:
        for y in fields:
            s = 1 + x**4 + y**4
            k_pot = 1 + onsite_scalar(x, r, g) + onsite_scalar(y, r, g) + 2 * shift_per_site
            check(f"x={x} y={y} local potential positive", k_pot >= 1, k_pot, ">=1", "scalar coercivity")
            check(f"x={x} y={y} S envelope", s <= scalar_factor * k_pot, [s, scalar_factor * k_pot], "S <= (8/g) k_pot", "scalar coercivity")
            for left in factors:
                for right in factors:
                    u, v = left * x, right * y
                    b_xy, b_uv = bond_scalar(x, y, c, lam), bond_scalar(u, v, c, lam)
                    check(f"x={x} y={y} a={left} b={right} bond bounds", b_xy <= (c + lam) * s and b_uv <= (c + lam) * s, [b_xy, b_uv, (c + lam) * s], "both bond values <= (c+lambda)S", "scalar envelope")
                    tail_abs = abs(b_xy - b_uv)
                    check(f"x={x} y={y} a={left} b={right} fourth envelope", tail_abs**4 <= fourth_constant * k_pot**4, [tail_abs**4, fourth_constant * k_pot**4], "|T|^4 <= C k_pot^4", "scalar envelope")
                    scalar_rows.append({"x": str(x), "y": str(y), "u": str(u), "v": str(v), "k_pot": str(k_pot), "S": str(s), "tail_abs": str(tail_abs), "tail_factor": str(tail_factor), "fourth_constant": str(fourth_constant)})
    check("scalar row coverage", len(scalar_rows) == len(fields) ** 2 * len(factors) ** 2, len(scalar_rows), len(fields) ** 2 * len(factors) ** 2, "coverage")

    matrix_rows: list[dict[str, Any]] = []
    betas = [float(value) for value in fixture["beta_values"]]
    radii = [float(value) for value in fixture["radius_values"]]
    numerical_tolerance = float(fixture["unitary_tolerance"])
    for scenario in fixture["scenarios"]:
        volume, dimension = int(scenario["volume"]), int(scenario["oscillator_dimension"])
        _, hamiltonian, local_hamiltonian, bonds = q3.build_volume(volume, dimension, fixture)
        identity = np.eye(hamiltonian.shape[0], dtype=complex)
        full_shift = volume * float(r**2 / (4 * g))
        local_shift = 2.0 * float(r**2 / (4 * g))
        full_k = hermitian(hamiltonian + (1.0 + full_shift) * identity)
        local_k = hermitian(local_hamiltonian + (1.0 + local_shift) * identity)
        full_inv2, full_floor = spectral_inverse_power(full_k, 2.0)
        local_inv2, local_floor = spectral_inverse_power(local_k, 2.0)
        full_k4 = full_k @ full_k @ full_k @ full_k
        local_k4 = local_k @ local_k @ local_k @ local_k
        q_single, _ = q3.oscillator(dimension)
        for beta in betas:
            rho = q3.gibbs(hamiltonian, beta)
            rho_half = q3.spectral_power(rho, 0.5)
            full_energy4 = float(np.real(np.trace(rho @ full_k4)))
            local_energy4 = float(np.real(np.trace(rho @ local_k4)))
            for radius in radii:
                q_cut = q3.cut_coordinate(q_single, radius)
                _, _, _, cut_bonds = q3.build_volume_with_bond_coordinate(volume, dimension, fixture, q_cut)
                tail = hermitian(bonds[(0, 1)] - cut_bonds[(0, 1)])
                tail_square = tail @ tail
                tail_fourth = tail_square @ tail_square
                two_slice = float(np.real(np.trace(rho_half @ tail_square @ rho_half @ tail_square)))
                equal_time = float(np.real(np.trace(rho @ tail_fourth)))
                local_q = hermitian(local_inv2 @ tail_fourth @ local_inv2)
                full_q = hermitian(full_inv2 @ tail_fourth @ full_inv2)
                local_c, full_c = operator_norm(local_q), operator_norm(full_q)
                local_bound, full_bound = local_c * local_energy4, full_c * full_energy4
                local_slack, full_slack = local_bound - equal_time, full_bound - equal_time
                q_values = np.linalg.eigvalsh(hermitian(q_single))
                cut_values = np.linalg.eigvalsh(hermitian(q_cut))
                contraction_defect = float(np.max(np.abs(cut_values) - np.abs(q_values)))
                values = {"volume": volume, "oscillator_dimension": dimension, "beta": beta, "radius": radius, "tail_operator_norm": operator_norm(tail), "two_slice": two_slice, "equal_time_fourth_moment": equal_time, "local_shifted_floor": local_floor, "full_shifted_floor": full_floor, "local_quotient_constant": local_c, "full_quotient_constant": full_c, "local_energy_fourth_moment": local_energy4, "full_energy_fourth_moment": full_energy4, "local_trace_bound": local_bound, "full_trace_bound": full_bound, "local_trace_slack": local_slack, "full_trace_slack": full_slack, "cutoff_contraction_defect": contraction_defect}
                check(f"V={volume} beta={beta} L={radius} local finite", all(np.isfinite(value) for value in values.values()), values, "finite", "matrix diagnostic")
                check(f"V={volume} beta={beta} L={radius} two-slice order", two_slice >= -numerical_tolerance and equal_time >= -numerical_tolerance and equal_time - two_slice >= -numerical_tolerance * (1 + equal_time), [two_slice, equal_time], "0<=two_slice<=equal-time fourth", "Euclidean transfer")
                check(f"V={volume} beta={beta} L={radius} cutoff contraction", contraction_defect <= numerical_tolerance, contraction_defect, f"<={numerical_tolerance}", "cutoff")
                check(f"V={volume} beta={beta} L={radius} local quotient order", local_slack >= -numerical_tolerance * (1 + local_bound), [local_slack, local_bound], "finite tolerance", "local quotient")
                check(f"V={volume} beta={beta} L={radius} full quotient order", full_slack >= -numerical_tolerance * (1 + full_bound), [full_slack, full_bound], "finite tolerance", "full quotient")
                matrix_rows.append(values)

    check("matrix row coverage", len(matrix_rows) == len(fixture["scenarios"]) * len(betas) * len(radii), len(matrix_rows), len(fixture["scenarios"]) * len(betas) * len(radii), "coverage")
    summaries: list[dict[str, Any]] = []
    for scenario in fixture["scenarios"]:
        for beta in betas:
            members = [row for row in matrix_rows if row["volume"] == int(scenario["volume"]) and row["beta"] == beta]
            summaries.append({"volume": int(scenario["volume"]), "oscillator_dimension": int(scenario["oscillator_dimension"]), "beta": beta, "max_local_quotient_constant": max(row["local_quotient_constant"] for row in members), "max_full_quotient_constant": max(row["full_quotient_constant"] for row in members), "max_two_slice": max(row["two_slice"] for row in members), "max_equal_time_fourth_moment": max(row["equal_time_fourth_moment"] for row in members), "max_local_trace_bound": max(row["local_trace_bound"] for row in members), "max_full_trace_bound": max(row["full_trace_bound"] for row in members), "min_local_trace_slack": min(row["local_trace_slack"] for row in members), "min_full_trace_slack": min(row["full_trace_slack"] for row in members)})
    check("summary coverage", len(summaries) == len(fixture["scenarios"]) * len(betas), len(summaries), len(fixture["scenarios"]) * len(betas), "coverage")
    check("finite summaries", all(np.isfinite(value) for row in summaries for value in row.values() if isinstance(value, (int, float))), len(summaries), "finite", "matrix diagnostic")

    return {"schema": "tect/foundation-audit/1.0", "run_kind": "primary", "audit_id": "PA-CP1-ST8-Q3LOCK-SOURCE-LOCAL-TAIL-SCALAR-ENERGY-ENVELOPE", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "passed": len(rows), "assertion_count": len(rows), "assertions": rows, "derived": {"scalar_rows": scalar_rows, "matrix_rows": matrix_rows, "summary_rows": summaries, "shift_per_site": str(shift_per_site), "scalar_factor": str(scalar_factor), "tail_factor": str(tail_factor), "fourth_constant": str(fourth_constant), "onsite_residual": str(residual), "scalar_contraction_bond_envelope_closed": True, "scalar_local_fourth_tail_envelope_closed": True, "finite_source_edge_tail_rows_closed": True, "finite_local_quotient_rows_closed": True, "source_volume_uniform_scalar_constant_closed": True, "operator_fourth_order_envelope_closed": False, "gibbs_local_fourth_moment_uniform_closed": False, "unbounded_common_core_closed": False, "common_alpha_closed": False, "qft_promoted": False}, "boundary": scope, "provenance": {"script": str(Path(__file__).resolve().relative_to(REPO)).replace("\\", "/"), "fixture_lineage": fixture_lineage}}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY SOURCE-LOCAL-TAIL-SCALAR-ENERGY-ENVELOPE PASS {payload['passed']}/{payload['assertion_count']} scalar={len(payload['derived']['scalar_rows'])} matrix={len(payload['derived']['matrix_rows'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

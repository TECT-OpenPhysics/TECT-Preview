#!/usr/bin/env python3
"""Primary commuting-configuration order lift audit (EXP-001192)."""

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
SLUG = "pre-a-cp1-st8-q3lock-source-local-tail-configuration-order"
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
    d = x - y
    return c * d**2 / 2 + lam * d**2 * (x**2 + y**2) / 4


def onsite_scalar(x: Fraction, r: Fraction, g: Fraction) -> Fraction:
    return r * x**2 / 2 + g * x**4 / 4


def hermitian(matrix: np.ndarray) -> np.ndarray:
    return (matrix + matrix.conj().T) / 2.0


def operator_norm(matrix: np.ndarray) -> float:
    return float(np.linalg.svd(matrix, compute_uv=False)[0])


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, lineage = load_fixture(manifest)
    finite_test, scope = manifest["finite_test"], manifest["scope"]
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001192" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001192/T-054", "provenance")
    check("fixture lineage", lineage[-1] == "EXP-001188", lineage, "EXP-001191 -> EXP-001190 -> EXP-001189 -> EXP-001188", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("scope firewall", scope["commuting_configuration_order_closed"] and scope["finite_potential_order_rows_closed"] and scope["finite_gibbs_potential_trace_transfer_closed"] and not scope["kinetic_inclusive_operator_order_closed"] and not scope["uniform_gibbs_potential_moment_closed"] and not scope["common_alpha_closed"] and not scope["pre_a_closed"], scope, "configuration order only; kinetic/QFT gates open", "scope")

    c, lam, g, r = (rat(fixture[key]) for key in ("c", "lambda", "g", "r"))
    shift = r**2 / (4 * g)
    energy_factor = Fraction(8, 1) / g
    tail_factor = 2 * (c + lam) * energy_factor
    fourth_constant = tail_factor**4
    residual = 1 + 4 * (r / g) ** 2 - energy_factor
    check("onsite residual", residual <= 0, residual, "<=0", "scalar coercivity")
    check("constant fixture", tail_factor == Fraction(56, 3) and fourth_constant == Fraction(9834496, 81), [tail_factor, fourth_constant], [Fraction(56, 3), Fraction(9834496, 81)], "constant")

    scalar_rows: list[dict[str, Any]] = []
    fields = [rat(value) for value in finite_test["field_values"]]
    factors = [rat(value) for value in finite_test["contraction_factors"]]
    for x in fields:
        for y in fields:
            s = 1 + x**4 + y**4
            kp = 1 + onsite_scalar(x, r, g) + onsite_scalar(y, r, g) + 2 * shift
            for a in factors:
                for b in factors:
                    u, v = a * x, b * y
                    bxy, buv = bond_scalar(x, y, c, lam), bond_scalar(u, v, c, lam)
                    tail = abs(bxy - buv)
                    check(f"x={x} y={y} a={a} b={b} pointwise", kp >= 1 and s <= energy_factor * kp and bxy <= (c + lam) * s and buv <= (c + lam) * s and tail**4 <= fourth_constant * kp**4, [kp, s, bxy, buv, tail**4], "pointwise envelope", "scalar order")
                    scalar_rows.append({"x": str(x), "y": str(y), "u": str(u), "v": str(v), "k_pot": str(kp), "S": str(s), "tail_abs": str(tail)})
    check("scalar coverage", len(scalar_rows) == len(fields) ** 2 * len(factors) ** 2, len(scalar_rows), len(fields) ** 2 * len(factors) ** 2, "coverage")

    matrix_rows: list[dict[str, Any]] = []
    tolerance = float(fixture["unitary_tolerance"])
    for scenario in fixture["scenarios"]:
        volume, dimension = int(scenario["volume"]), int(scenario["oscillator_dimension"])
        q_ops, hamiltonian, _, bonds = q3.build_volume(volume, dimension, fixture)
        identity = np.eye(hamiltonian.shape[0], dtype=complex)
        potential = sum((float(r) * (q @ q) / 2.0 + float(g) * (q @ q @ q @ q) / 4.0 for q in q_ops[:2]), np.zeros_like(hamiltonian))
        k_pot = hermitian(potential + (1.0 + 2.0 * float(shift)) * identity)
        k_pot4 = k_pot @ k_pot @ k_pot @ k_pot
        min_k = float(np.min(np.linalg.eigvalsh(k_pot)))
        check(f"V={volume} potential floor", min_k >= 1.0 - tolerance, min_k, ">=1", "matrix positivity")
        q_single, _ = q3.oscillator(dimension)
        for beta in (float(value) for value in fixture["beta_values"]):
            rho = q3.gibbs(hamiltonian, beta)
            potential_moment = float(np.real(np.trace(rho @ k_pot4)))
            for radius in (float(value) for value in fixture["radius_values"]):
                q_cut = q3.cut_coordinate(q_single, radius)
                _, _, _, cut_bonds = q3.build_volume_with_bond_coordinate(volume, dimension, fixture, q_cut)
                tail = hermitian(bonds[(0, 1)] - cut_bonds[(0, 1)])
                tail_square, tail_fourth = tail @ tail, (tail @ tail) @ (tail @ tail)
                quotient_defect = hermitian(float(fourth_constant) * k_pot4 - tail_fourth)
                order_slack = float(np.min(np.linalg.eigvalsh(quotient_defect)))
                trace_tail = float(np.real(np.trace(rho @ tail_fourth)))
                trace_bound = float(fourth_constant) * potential_moment
                values = {"volume": volume, "oscillator_dimension": dimension, "beta": beta, "radius": radius, "tail_operator_norm": operator_norm(tail), "two_slice": float(np.real(np.trace(q3.spectral_power(rho, 0.5) @ tail_square @ q3.spectral_power(rho, 0.5) @ tail_square))), "tail_fourth_moment": trace_tail, "potential_fourth_moment": potential_moment, "trace_bound": trace_bound, "trace_slack": trace_bound - trace_tail, "order_slack": order_slack, "potential_floor": min_k}
                check(f"V={volume} beta={beta} L={radius} finite order", all(np.isfinite(value) for value in values.values()), values, "finite", "configuration order")
                check(f"V={volume} beta={beta} L={radius} order slack", order_slack >= -tolerance * (1.0 + operator_norm(tail_fourth) + float(fourth_constant) * operator_norm(k_pot4)), order_slack, "finite tolerance", "configuration order")
                check(f"V={volume} beta={beta} L={radius} trace transfer", values["trace_slack"] >= -tolerance * (1 + trace_bound), values["trace_slack"], "finite tolerance", "Gibbs trace")
                matrix_rows.append(values)
    check("matrix coverage", len(matrix_rows) == len(fixture["scenarios"]) * len(fixture["beta_values"]) * len(fixture["radius_values"]), len(matrix_rows), len(fixture["scenarios"]) * len(fixture["beta_values"]) * len(fixture["radius_values"]), "coverage")
    summaries: list[dict[str, Any]] = []
    for scenario in fixture["scenarios"]:
        for beta in (float(value) for value in fixture["beta_values"]):
            members = [row for row in matrix_rows if row["volume"] == int(scenario["volume"]) and row["beta"] == beta]
            summaries.append({"volume": int(scenario["volume"]), "oscillator_dimension": int(scenario["oscillator_dimension"]), "beta": beta, "max_tail_fourth_moment": max(row["tail_fourth_moment"] for row in members), "max_potential_fourth_moment": max(row["potential_fourth_moment"] for row in members), "max_trace_bound": max(row["trace_bound"] for row in members), "min_order_slack": min(row["order_slack"] for row in members), "min_trace_slack": min(row["trace_slack"] for row in members)})
    check("summary coverage", len(summaries) == len(fixture["scenarios"]) * len(fixture["beta_values"]), len(summaries), len(fixture["scenarios"]) * len(fixture["beta_values"]), "coverage")

    return {"schema": "tect/foundation-audit/1.0", "run_kind": "primary", "audit_id": "PA-CP1-ST8-Q3LOCK-SOURCE-LOCAL-TAIL-CONFIGURATION-ORDER", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "passed": len(checks), "assertion_count": len(checks), "assertions": checks, "derived": {"scalar_rows": scalar_rows, "matrix_rows": matrix_rows, "summary_rows": summaries, "shift_per_site": str(shift), "scalar_factor": str(energy_factor), "tail_factor": str(tail_factor), "fourth_constant": str(fourth_constant), "onsite_residual": str(residual), "commuting_configuration_order_closed": True, "finite_potential_order_rows_closed": True, "finite_gibbs_potential_trace_transfer_closed": True, "source_volume_uniform_potential_constant_closed": True, "kinetic_inclusive_operator_order_closed": False, "uniform_gibbs_potential_moment_closed": False, "unbounded_common_core_closed": False, "common_alpha_closed": False, "qft_promoted": False}, "boundary": scope, "provenance": {"script": str(Path(__file__).resolve().relative_to(REPO)).replace("\\", "/"), "fixture_lineage": lineage}}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY SOURCE-LOCAL-TAIL-CONFIGURATION-ORDER PASS {payload['passed']}/{payload['assertion_count']} scalar={len(payload['derived']['scalar_rows'])} matrix={len(payload['derived']['matrix_rows'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

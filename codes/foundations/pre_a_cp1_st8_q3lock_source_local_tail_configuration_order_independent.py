#!/usr/bin/env python3
"""Independent commuting-configuration order lift audit (EXP-001192).

This lane rebuilds the oscillator tensor products, cutoff, Gibbs state and
configuration-order checks without importing the primary audit or its helper.
"""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-st8-q3lock-source-local-tail-configuration-order"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-27-independent-{SLUG}" / "independent.json"


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
    square = difference**2
    return c * square / 2 + lam * square * (x**2 + y**2) / 4


def onsite_scalar(x: Fraction, r: Fraction, g: Fraction) -> Fraction:
    return r * x**2 / 2 + g * x**4 / 4


def oscillator(n: int) -> tuple[np.ndarray, np.ndarray]:
    annihilation = np.zeros((n, n), dtype=complex)
    for index in range(n - 1):
        annihilation[index, index + 1] = np.sqrt(index + 1.0)
    creation = annihilation.conj().T
    return (annihilation + creation) / np.sqrt(2.0), (annihilation - creation) / (1j * np.sqrt(2.0))


def graph_edges(volume: int) -> list[tuple[int, int]]:
    if volume == 2:
        return [(0, 1)]
    if volume == 4:
        return [(0, 1), (0, 2), (1, 3), (2, 3)]
    if volume == 6:
        return [(0, 1), (1, 2), (3, 4), (4, 5), (0, 3), (1, 4), (2, 5)]
    raise ValueError("unexpected finite volume")


def embed(single: np.ndarray, site: int, volume: int, identity: np.ndarray) -> np.ndarray:
    factors = [single if index == site else identity for index in range(volume)]
    result = factors[0]
    for factor in factors[1:]:
        result = np.kron(result, factor)
    return result


def bond_matrix(left: np.ndarray, right: np.ndarray, fixture: dict[str, Any]) -> np.ndarray:
    difference = left - right
    square = difference @ difference
    c, lam = float(fixture["c"]), float(fixture["lambda"])
    return c * square / 2.0 + lam * square @ (left @ left + right @ right) / 4.0


def build_volume(volume: int, dimension: int, fixture: dict[str, Any], coordinate: np.ndarray | None = None) -> tuple[np.ndarray, np.ndarray, dict[tuple[int, int], np.ndarray]]:
    q_single, p_single = oscillator(dimension)
    identity = np.eye(dimension, dtype=complex)
    q_ops = [embed(q_single, site, volume, identity) for site in range(volume)]
    p_ops = [embed(p_single, site, volume, identity) for site in range(volume)]
    bond_single = q_single if coordinate is None else coordinate
    bond_ops = [embed(bond_single, site, volume, identity) for site in range(volume)]
    chi, r, g = float(fixture["chi"]), float(fixture["r"]), float(fixture["g"])
    onsite_terms = [p @ p / (2.0 * chi) + r * (q @ q) / 2.0 + g * (q @ q @ q @ q) / 4.0 for q, p in zip(q_ops, p_ops)]
    bond_terms = {(left, right): bond_matrix(bond_ops[left], bond_ops[right], fixture) for left, right in graph_edges(volume)}
    zero = np.zeros_like(q_ops[0])
    full = sum(onsite_terms, zero) + sum(bond_terms.values(), zero)
    local = onsite_terms[0] + onsite_terms[1] + bond_terms[(0, 1)]
    return (full + full.conj().T) / 2.0, (local + local.conj().T) / 2.0, bond_terms


def cutoff(q: np.ndarray, radius: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((q + q.conj().T) / 2.0)
    scaled = np.abs(values) / radius
    taper = np.where(scaled <= 1.0, 1.0, np.where(scaled < 2.0, 0.5 * (1.0 + np.cos(np.pi * (scaled - 1.0))), 0.0))
    return (vectors * (values * taper)) @ vectors.conj().T


def gibbs(hamiltonian: np.ndarray, beta: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((hamiltonian + hamiltonian.conj().T) / 2.0)
    weights = np.exp(-beta * (values - float(np.min(values))))
    weights /= float(np.sum(weights))
    return (vectors * weights) @ vectors.conj().T


def spectral_power(matrix: np.ndarray, exponent: float) -> np.ndarray:
    hermitian = (matrix + matrix.conj().T) / 2.0
    values, vectors = np.linalg.eigh(hermitian)
    if float(np.min(values)) < -1.0e-9:
        raise ValueError("matrix is not positive")
    values = np.maximum(values, 0.0)
    return (vectors * np.power(values, exponent)) @ vectors.conj().T


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
    check("fixture lineage", lineage[-1] == "EXP-001188", lineage, "ends at EXP-001188", "provenance")
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
            scalar_s = 1 + x**4 + y**4
            potential = 1 + onsite_scalar(x, r, g) + onsite_scalar(y, r, g) + 2 * shift
            check(f"x={x} y={y} potential", potential >= 1 and scalar_s <= energy_factor * potential, [potential, scalar_s], "k_pot>=1 and S envelope", "scalar coercivity")
            for a in factors:
                for b in factors:
                    u, v = a * x, b * y
                    original = bond_scalar(x, y, c, lam)
                    cutoff_bond = bond_scalar(u, v, c, lam)
                    tail = abs(original - cutoff_bond)
                    check(f"x={x} y={y} a={a} b={b} order", original <= (c + lam) * scalar_s and cutoff_bond <= (c + lam) * scalar_s and tail**4 <= fourth_constant * potential**4, [original, cutoff_bond, tail**4], "configuration fourth order", "scalar envelope")
                    scalar_rows.append({"x": str(x), "y": str(y), "u": str(u), "v": str(v), "k_pot": str(potential), "S": str(scalar_s), "tail_abs": str(tail)})
    expected_scalar = len(fields) ** 2 * len(factors) ** 2
    check("scalar coverage", len(scalar_rows) == expected_scalar, len(scalar_rows), expected_scalar, "coverage")

    matrix_rows: list[dict[str, Any]] = []
    tolerance = float(fixture["unitary_tolerance"])
    q_single_cache: dict[int, np.ndarray] = {}
    for scenario in fixture["scenarios"]:
        volume, dimension = int(scenario["volume"]), int(scenario["oscillator_dimension"])
        hamiltonian, _, bonds = build_volume(volume, dimension, fixture)
        identity = np.eye(hamiltonian.shape[0], dtype=complex)
        q_ops = []
        q, _ = oscillator(dimension)
        for site in range(volume):
            q_ops.append(embed(q, site, volume, np.eye(dimension, dtype=complex)))
        potential = sum((float(r) * (op @ op) / 2.0 + float(g) * (op @ op @ op @ op) / 4.0 for op in q_ops[:2]), np.zeros_like(hamiltonian))
        k_pot = hermitian(potential + (1.0 + 2.0 * float(shift)) * identity)
        k_pot4 = k_pot @ k_pot @ k_pot @ k_pot
        minimum = float(np.min(np.linalg.eigvalsh(k_pot)))
        check(f"V={volume} potential floor", minimum >= 1.0 - tolerance, minimum, ">=1", "matrix positivity")
        q_single_cache[dimension] = q
        for beta in (float(value) for value in fixture["beta_values"]):
            rho = gibbs(hamiltonian, beta)
            rho_half = spectral_power(rho, 0.5)
            potential_moment = float(np.real(np.trace(rho @ k_pot4)))
            for radius in (float(value) for value in fixture["radius_values"]):
                q_cut = cutoff(q, radius)
                _, _, cut_bonds = build_volume(volume, dimension, fixture, q_cut)
                tail = hermitian(bonds[(0, 1)] - cut_bonds[(0, 1)])
                square = tail @ tail
                fourth = square @ square
                quotient_defect = hermitian(float(fourth_constant) * k_pot4 - fourth)
                order_slack = float(np.min(np.linalg.eigvalsh(quotient_defect)))
                trace_tail = float(np.real(np.trace(rho @ fourth)))
                trace_bound = float(fourth_constant) * potential_moment
                values = {"volume": volume, "oscillator_dimension": dimension, "beta": beta, "radius": radius, "tail_operator_norm": operator_norm(tail), "two_slice": float(np.real(np.trace(rho_half @ square @ rho_half @ square))), "tail_fourth_moment": trace_tail, "potential_fourth_moment": potential_moment, "trace_bound": trace_bound, "trace_slack": trace_bound - trace_tail, "order_slack": order_slack, "potential_floor": minimum}
                check(f"V={volume} beta={beta} L={radius} finite", all(np.isfinite(value) for value in values.values()), values, "finite", "configuration order")
                scale = tolerance * (1.0 + operator_norm(fourth) + float(fourth_constant) * operator_norm(k_pot4))
                check(f"V={volume} beta={beta} L={radius} order slack", order_slack >= -scale, order_slack, "finite tolerance", "configuration order")
                check(f"V={volume} beta={beta} L={radius} trace transfer", values["trace_slack"] >= -tolerance * (1 + trace_bound), values["trace_slack"], "finite tolerance", "Gibbs trace")
                matrix_rows.append(values)
    expected_matrix = len(fixture["scenarios"]) * len(fixture["beta_values"]) * len(fixture["radius_values"])
    check("matrix coverage", len(matrix_rows) == expected_matrix, len(matrix_rows), expected_matrix, "coverage")
    summaries: list[dict[str, Any]] = []
    for scenario in fixture["scenarios"]:
        for beta in (float(value) for value in fixture["beta_values"]):
            members = [row for row in matrix_rows if row["volume"] == int(scenario["volume"]) and row["beta"] == beta]
            summaries.append({"volume": int(scenario["volume"]), "oscillator_dimension": int(scenario["oscillator_dimension"]), "beta": beta, "max_tail_fourth_moment": max(row["tail_fourth_moment"] for row in members), "max_potential_fourth_moment": max(row["potential_fourth_moment"] for row in members), "max_trace_bound": max(row["trace_bound"] for row in members), "min_order_slack": min(row["order_slack"] for row in members), "min_trace_slack": min(row["trace_slack"] for row in members)})
    check("summary coverage", len(summaries) == len(fixture["scenarios"]) * len(fixture["beta_values"]), len(summaries), len(fixture["scenarios"]) * len(fixture["beta_values"]), "coverage")

    return {"schema": "tect/foundation-audit/1.0", "run_kind": "independent", "audit_id": "PA-CP1-ST8-Q3LOCK-SOURCE-LOCAL-TAIL-CONFIGURATION-ORDER", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "passed": len(checks), "assertion_count": len(checks), "assertions": checks, "derived": {"scalar_rows": scalar_rows, "matrix_rows": matrix_rows, "summary_rows": summaries, "shift_per_site": str(shift), "scalar_factor": str(energy_factor), "tail_factor": str(tail_factor), "fourth_constant": str(fourth_constant), "onsite_residual": str(residual), "commuting_configuration_order_closed": True, "finite_potential_order_rows_closed": True, "finite_gibbs_potential_trace_transfer_closed": True, "source_volume_uniform_potential_constant_closed": True, "kinetic_inclusive_operator_order_closed": False, "uniform_gibbs_potential_moment_closed": False, "unbounded_common_core_closed": False, "common_alpha_closed": False, "qft_promoted": False}, "boundary": scope, "provenance": {"script": str(Path(__file__).resolve().relative_to(REPO)).replace("\\\\", "/"), "fixture_lineage": lineage}}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT SOURCE-LOCAL-TAIL-CONFIGURATION-ORDER PASS {payload['passed']}/{payload['assertion_count']} scalar={len(payload['derived']['scalar_rows'])} matrix={len(payload['derived']['matrix_rows'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
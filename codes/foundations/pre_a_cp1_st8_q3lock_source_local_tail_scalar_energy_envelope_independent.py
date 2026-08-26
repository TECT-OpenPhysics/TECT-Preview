#!/usr/bin/env python3
"""Non-importing independent audit for EXP-001191.

This lane rebuilds the scalar contraction proof data and the finite Q3 edge
matrices from scratch; it does not import the primary audit or its helpers.
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


def bond(x: Fraction, y: Fraction, c: Fraction, lam: Fraction) -> Fraction:
    d = x - y
    return c * d**2 / 2 + lam * d**2 * (x**2 + y**2) / 4


def onsite(x: Fraction, r: Fraction, g: Fraction) -> Fraction:
    return r * x**2 / 2 + g * x**4 / 4


def oscillator(n: int) -> tuple[np.ndarray, np.ndarray]:
    lower = np.zeros((n, n), dtype=complex)
    for index in range(n - 1):
        lower[index, index + 1] = np.sqrt(index + 1.0)
    upper = lower.conj().T
    return (lower + upper) / np.sqrt(2.0), (lower - upper) / (1j * np.sqrt(2.0))


def edges(volume: int) -> list[tuple[int, int]]:
    if volume == 2:
        return [(0, 1)]
    if volume == 4:
        return [(0, 1), (0, 2), (1, 3), (2, 3)]
    if volume == 6:
        return [(0, 1), (1, 2), (3, 4), (4, 5), (0, 3), (1, 4), (2, 5)]
    raise ValueError("unexpected finite volume")


def embed(single: np.ndarray, site: int, volume: int, identity: np.ndarray) -> np.ndarray:
    result = single if site == 0 else identity
    for index in range(1, volume):
        result = np.kron(result, single if index == site else identity)
    return result


def bond_matrix(left: np.ndarray, right: np.ndarray, fixture: dict[str, Any]) -> np.ndarray:
    difference = left - right
    c, lam = float(fixture["c"]), float(fixture["lambda"])
    square = difference @ difference
    return c * square / 2.0 + lam * square @ (left @ left + right @ right) / 4.0


def build(volume: int, dimension: int, fixture: dict[str, Any], coordinate: np.ndarray | None = None) -> tuple[np.ndarray, np.ndarray, dict[tuple[int, int], np.ndarray]]:
    q, p = oscillator(dimension)
    identity = np.eye(dimension, dtype=complex)
    q_ops = [embed(q, site, volume, identity) for site in range(volume)]
    p_ops = [embed(p, site, volume, identity) for site in range(volume)]
    bond_q = q if coordinate is None else coordinate
    bond_ops = [embed(bond_q, site, volume, identity) for site in range(volume)]
    chi, r, g = float(fixture["chi"]), float(fixture["r"]), float(fixture["g"])
    onsite_terms = [p_op @ p_op / (2.0 * chi) + r * (q_op @ q_op) / 2.0 + g * (q_op @ q_op @ q_op @ q_op) / 4.0 for q_op, p_op in zip(q_ops, p_ops)]
    bond_terms = {(left, right): bond_matrix(bond_ops[left], bond_ops[right], fixture) for left, right in edges(volume)}
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


def positive_power(matrix: np.ndarray, exponent: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((matrix + matrix.conj().T) / 2.0)
    if float(np.min(values)) < -1.0e-9:
        raise ValueError("matrix is not positive")
    return (vectors * np.power(np.maximum(values, 0.0), exponent)) @ vectors.conj().T


def inverse_power(matrix: np.ndarray, exponent: float) -> tuple[np.ndarray, float]:
    values, vectors = np.linalg.eigh((matrix + matrix.conj().T) / 2.0)
    minimum = float(np.min(values))
    if minimum <= 0.0:
        raise ValueError("matrix is not strictly positive")
    return (vectors * np.power(values, -exponent)) @ vectors.conj().T, minimum


def norm(matrix: np.ndarray) -> float:
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

    check("identity", manifest["exploration_id"] == "EXP-001191" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001191/T-054", "provenance")
    check("fixture lineage", lineage[-1] == "EXP-001188", lineage, "EXP-001190 -> EXP-001189 -> EXP-001188", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")

    c, lam, g, r = (rat(fixture[key]) for key in ("c", "lambda", "g", "r"))
    shift = r**2 / (4 * g)
    energy_factor = Fraction(8, 1) / g
    tail_factor = 2 * (c + lam) * energy_factor
    residual = 1 + 4 * (r / g) ** 2 - energy_factor
    check("onsite residual", residual <= 0, residual, "<=0", "scalar coercivity")
    check("tail factor", tail_factor > 0, tail_factor, ">0", "scalar envelope")

    scalar_rows: list[dict[str, Any]] = []
    fields = [rat(value) for value in finite_test["field_values"]]
    factors = [rat(value) for value in finite_test["contraction_factors"]]
    for x in fields:
        for y in fields:
            s = 1 + x**4 + y**4
            kp = 1 + onsite(x, r, g) + onsite(y, r, g) + 2 * shift
            check(f"x={x} y={y} potential", kp >= 1 and s <= energy_factor * kp, [kp, s, energy_factor * kp], "k_pot>=1 and S envelope", "scalar coercivity")
            for a in factors:
                for b in factors:
                    u, v = a * x, b * y
                    bxy, buv = bond(x, y, c, lam), bond(u, v, c, lam)
                    check(f"x={x} y={y} a={a} b={b} bond", bxy <= (c + lam) * s and buv <= (c + lam) * s, [bxy, buv], "both <= (c+lambda)S", "scalar envelope")
                    tail = abs(bxy - buv)
                    check(f"x={x} y={y} a={a} b={b} fourth", tail**4 <= tail_factor**4 * kp**4, [tail**4, tail_factor**4 * kp**4], "fourth envelope", "scalar envelope")
                    scalar_rows.append({"x": str(x), "y": str(y), "u": str(u), "v": str(v), "k_pot": str(kp), "S": str(s), "tail_abs": str(tail)})
    check("scalar coverage", len(scalar_rows) == len(fields) ** 2 * len(factors) ** 2, len(scalar_rows), len(fields) ** 2 * len(factors) ** 2, "coverage")

    matrix_rows: list[dict[str, Any]] = []
    tolerance = float(fixture["unitary_tolerance"])
    for scenario in fixture["scenarios"]:
        volume, dimension = int(scenario["volume"]), int(scenario["oscillator_dimension"])
        full_h, local_h, bonds = build(volume, dimension, fixture)
        identity = np.eye(full_h.shape[0], dtype=complex)
        full_k = (full_h + (1 + volume * float(shift)) * identity)
        local_k = (local_h + (1 + 2 * float(shift)) * identity)
        full_k = (full_k + full_k.conj().T) / 2.0
        local_k = (local_k + local_k.conj().T) / 2.0
        full_inv, full_floor = inverse_power(full_k, 2.0)
        local_inv, local_floor = inverse_power(local_k, 2.0)
        full_k4 = full_k @ full_k @ full_k @ full_k
        local_k4 = local_k @ local_k @ local_k @ local_k
        q, _ = oscillator(dimension)
        q_values = np.sort(np.abs(np.linalg.eigvalsh((q + q.conj().T) / 2.0)))
        for beta in (float(value) for value in fixture["beta_values"]):
            rho = gibbs(full_h, beta)
            rho_half = positive_power(rho, 0.5)
            full_moment = float(np.real(np.trace(rho @ full_k4)))
            local_moment = float(np.real(np.trace(rho @ local_k4)))
            for radius in (float(value) for value in fixture["radius_values"]):
                qcut = cutoff(q, radius)
                _, _, cut_bonds = build(volume, dimension, fixture, qcut)
                tail = (bonds[(0, 1)] - cut_bonds[(0, 1)])
                tail = (tail + tail.conj().T) / 2.0
                square = tail @ tail
                fourth = square @ square
                two_slice = float(np.real(np.trace(rho_half @ square @ rho_half @ square)))
                equal_time = float(np.real(np.trace(rho @ fourth)))
                local_c = norm((local_inv @ fourth @ local_inv + (local_inv @ fourth @ local_inv).conj().T) / 2.0)
                full_c = norm((full_inv @ fourth @ full_inv + (full_inv @ fourth @ full_inv).conj().T) / 2.0)
                cut_values = np.sort(np.abs(np.linalg.eigvalsh((qcut + qcut.conj().T) / 2.0)))
                contraction = float(np.max(cut_values - q_values))
                values = {"volume": volume, "oscillator_dimension": dimension, "beta": beta, "radius": radius, "tail_operator_norm": norm(tail), "two_slice": two_slice, "equal_time_fourth_moment": equal_time, "local_shifted_floor": local_floor, "full_shifted_floor": full_floor, "local_quotient_constant": local_c, "full_quotient_constant": full_c, "local_energy_fourth_moment": local_moment, "full_energy_fourth_moment": full_moment, "local_trace_bound": local_c * local_moment, "full_trace_bound": full_c * full_moment, "local_trace_slack": local_c * local_moment - equal_time, "full_trace_slack": full_c * full_moment - equal_time, "cutoff_contraction_defect": contraction}
                check(f"V={volume} beta={beta} L={radius} finite", all(np.isfinite(value) for value in values.values()), values, "finite", "matrix diagnostic")
                check(f"V={volume} beta={beta} L={radius} transfer", two_slice >= -tolerance and equal_time >= -tolerance and equal_time - two_slice >= -tolerance * (1 + equal_time), [two_slice, equal_time], "Euclidean order", "matrix diagnostic")
                check(f"V={volume} beta={beta} L={radius} contraction", contraction <= tolerance, contraction, f"<={tolerance}", "cutoff")
                matrix_rows.append(values)
    check("matrix coverage", len(matrix_rows) == len(fixture["scenarios"]) * len(fixture["beta_values"]) * len(fixture["radius_values"]), len(matrix_rows), len(fixture["scenarios"]) * len(fixture["beta_values"]) * len(fixture["radius_values"]), "coverage")
    summaries: list[dict[str, Any]] = []
    for scenario in fixture["scenarios"]:
        for beta in (float(value) for value in fixture["beta_values"]):
            members = [row for row in matrix_rows if row["volume"] == int(scenario["volume"]) and row["beta"] == beta]
            summaries.append({"volume": int(scenario["volume"]), "oscillator_dimension": int(scenario["oscillator_dimension"]), "beta": beta, "max_local_quotient_constant": max(row["local_quotient_constant"] for row in members), "max_full_quotient_constant": max(row["full_quotient_constant"] for row in members), "max_two_slice": max(row["two_slice"] for row in members), "max_equal_time_fourth_moment": max(row["equal_time_fourth_moment"] for row in members), "max_local_trace_bound": max(row["local_trace_bound"] for row in members), "max_full_trace_bound": max(row["full_trace_bound"] for row in members), "min_local_trace_slack": min(row["local_trace_slack"] for row in members), "min_full_trace_slack": min(row["full_trace_slack"] for row in members)})
    check("summary coverage", len(summaries) == len(fixture["scenarios"]) * len(fixture["beta_values"]), len(summaries), len(fixture["scenarios"]) * len(fixture["beta_values"]), "coverage")

    return {"schema": "tect/foundation-audit/1.0", "run_kind": "independent", "audit_id": "PA-CP1-ST8-Q3LOCK-SOURCE-LOCAL-TAIL-SCALAR-ENERGY-ENVELOPE", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "passed": len(checks), "assertion_count": len(checks), "assertions": checks, "derived": {"scalar_rows": scalar_rows, "matrix_rows": matrix_rows, "summary_rows": summaries, "shift_per_site": str(shift), "scalar_factor": str(energy_factor), "tail_factor": str(tail_factor), "fourth_constant": str(tail_factor**4), "onsite_residual": str(residual), "scalar_contraction_bond_envelope_closed": True, "scalar_local_fourth_tail_envelope_closed": True, "finite_source_edge_tail_rows_closed": True, "finite_local_quotient_rows_closed": True, "source_volume_uniform_scalar_constant_closed": True, "operator_fourth_order_envelope_closed": False, "gibbs_local_fourth_moment_uniform_closed": False, "unbounded_common_core_closed": False, "common_alpha_closed": False, "qft_promoted": False}, "boundary": scope, "provenance": {"script": str(Path(__file__).resolve().relative_to(REPO)).replace("\\", "/"), "fixture_lineage": lineage}}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT SOURCE-LOCAL-TAIL-SCALAR-ENERGY-ENVELOPE PASS {payload['passed']}/{payload['assertion_count']} scalar={len(payload['derived']['scalar_rows'])} matrix={len(payload['derived']['matrix_rows'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

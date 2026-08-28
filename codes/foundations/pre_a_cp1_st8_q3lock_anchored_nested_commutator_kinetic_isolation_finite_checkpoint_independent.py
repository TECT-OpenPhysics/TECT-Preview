#!/usr/bin/env python3
"""Independent reconstruction of the R-387 kinetic-isolation finite check."""

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
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-anchored-nested-commutator-kinetic-isolation-finite-checkpoint-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-primary-pre_a_cp1_st8_q3lock_anchored_nested_commutator_kinetic_isolation_finite_checkpoint/independent.json"


def store(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True, default=float)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def hermitian(x: np.ndarray) -> np.ndarray:
    return (x + x.conj().T) / 2.0


def ops(dimension: int) -> tuple[np.ndarray, np.ndarray]:
    a = np.zeros((dimension, dimension), dtype=complex)
    for n in range(dimension - 1):
        a[n, n + 1] = np.sqrt(n + 1.0)
    return (a + a.conj().T) / np.sqrt(2.0), (a - a.conj().T) / (1j * np.sqrt(2.0))


def lift(single: np.ndarray, site: int, volume: int, eye: np.ndarray) -> np.ndarray:
    factors = [single if k == site else eye for k in range(volume)]
    result = factors[0]
    for factor in factors[1:]:
        result = np.kron(result, factor)
    return result


def edges(volume: int, fixture: dict[str, Any]) -> list[tuple[int, int]]:
    return [tuple(map(int, pair)) for pair in fixture["graph_edges_by_volume"][str(volume)]]


def bracket(x: np.ndarray, y: np.ndarray) -> np.ndarray:
    return x @ y - y @ x


def norm(x: np.ndarray) -> float:
    return float(np.linalg.svd(x, compute_uv=False)[0])


def weighted_norm(x: np.ndarray, h: np.ndarray, beta: float) -> float:
    values, vectors = np.linalg.eigh(hermitian(h))
    weights = np.exp(-beta * (values - float(np.min(values))))
    weights /= float(np.sum(weights))
    rho = hermitian((vectors * weights) @ vectors.conj().T)
    value = np.trace(rho @ x.conj().T @ x) + np.trace(rho @ x @ x.conj().T)
    return float(np.sqrt(max(0.0, float(np.real(value)))))


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    beta_values = [float(Fraction(x)) for x in fixture["beta_values"]]
    eta_values = [float(Fraction(x)) for x in fixture["resolvent_imaginary_values"]]
    scales = [float(Fraction(x)) for x in fixture["potential_scale_values"]]
    tolerance = float(fixture["isolation_tolerance"])
    weighted_tolerance = float(fixture["weighted_isolation_tolerance"])
    maximums = {name: 0.0 for name in ("potential_commutator_residual", "boundary_commutator_residual", "inner_isolation_residual", "nested_isolation_residual", "scale_invariance_residual", "weighted_isolation_residual")}
    bond_prefix_count = 0
    seed_rows = 0
    weighted_rows = 0
    context_count = 0
    assertions = 0

    def check(condition: bool, name: str, actual: Any, expected: Any) -> None:
        nonlocal assertions
        assertions += 1
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")

    for volume in (int(x) for x in fixture["volume_values"]):
        q_single, p_single = ops(int(fixture["oscillator_dimension"]))
        eye = np.eye(q_single.shape[0], dtype=complex)
        q = [lift(q_single, site, volume, eye) for site in range(volume)]
        p = [lift(p_single, site, volume, eye) for site in range(volume)]
        records: list[tuple[str, np.ndarray, np.ndarray, np.ndarray]] = []
        for site in range(volume):
            kinetic = hermitian(p[site] @ p[site] / (2.0 * float(fixture["chi"])))
            potential = hermitian(float(fixture["r"]) * (q[site] @ q[site]) / 2.0 + float(fixture["g"]) * (q[site] @ q[site] @ q[site] @ q[site]) / 4.0)
            records.append(("onsite", hermitian(kinetic + potential), kinetic, potential))
        for left, right in edges(volume, fixture):
            d = q[left] - q[right]
            quadratic = d @ d
            potential = hermitian(float(fixture["c"]) * quadratic / 2.0 + float(fixture["lambda"]) * quadratic @ (q[left] @ q[left] + q[right] @ q[right]) / 4.0)
            records.append(("bond", potential, np.zeros_like(potential), potential))
        for order in (list(range(len(records))), list(reversed(range(len(records))))):
            for position, boundary_index in enumerate(order):
                if records[boundary_index][0] != "bond":
                    continue
                bond_prefix_count += 1
                prefix = order[:position]
                zero = np.zeros_like(records[0][1])
                h = sum((records[k][1] for k in prefix), zero)
                t = sum((records[k][2] for k in prefix), zero)
                v = sum((records[k][3] for k in prefix), zero)
                b = records[boundary_index][1]
                for site in range(volume):
                    eye_full = np.eye(q[site].shape[0], dtype=complex)
                    for eta in eta_values:
                        seed = np.linalg.inv(1j * eta * eye_full - q[site])
                        for observable in (seed, seed.conj().T):
                            pc = norm(bracket(v, observable))
                            bc = norm(bracket(b, observable))
                            inner = norm(bracket(h, observable) - bracket(t, observable))
                            nested = norm(bracket(b, bracket(h, observable)) - bracket(b, bracket(t, observable)))
                            scaled = max(norm(bracket(b, bracket(hermitian(t + scale * v), observable)) - bracket(b, bracket(t, observable))) for scale in scales)
                            values = (pc, bc, inner, nested, scaled)
                            for key, value in zip(("potential_commutator_residual", "boundary_commutator_residual", "inner_isolation_residual", "nested_isolation_residual", "scale_invariance_residual"), values):
                                maximums[key] = max(maximums[key], value)
                            seed_rows += 1
                            check(pc <= tolerance, "potential commutator", pc, tolerance)
                            check(bc <= tolerance, "boundary commutator", bc, tolerance)
                            check(inner <= tolerance, "inner isolation", inner, tolerance)
                            check(nested <= tolerance, "nested isolation", nested, tolerance)
                            check(scaled <= tolerance, "scale invariance", scaled, tolerance)
                            for beta in beta_values:
                                weighted = weighted_norm(bracket(b, bracket(h, observable)) - bracket(b, bracket(t, observable)), h, beta)
                                maximums["weighted_isolation_residual"] = max(maximums["weighted_isolation_residual"], weighted)
                                weighted_rows += 1
                                context_count += 1
                                check(weighted <= weighted_tolerance, "weighted isolation", weighted, weighted_tolerance)
    expected_prefixes = sum(2 * len(edges(int(v), fixture)) for v in fixture["volume_values"])
    expected_seeds = sum(2 * len(edges(int(v), fixture)) * int(v) * len(eta_values) * 2 for v in fixture["volume_values"])
    expected_contexts = expected_seeds * len(beta_values)
    check(bond_prefix_count == expected_prefixes, "prefix coverage", bond_prefix_count, expected_prefixes)
    check(seed_rows == expected_seeds, "seed coverage", seed_rows, expected_seeds)
    check(weighted_rows == expected_contexts == context_count, "weighted coverage", [weighted_rows, context_count], expected_contexts)
    check(all(np.isfinite(value) for value in maximums.values()), "finite maxima", maximums, "finite")
    derived = {"context_count": context_count, "expected_contexts": expected_contexts, "bond_prefix_count": bond_prefix_count, "seed_rows": seed_rows, "weighted_rows": weighted_rows, "maximums": maximums}
    for key in ("finite_coordinate_potential_commutation_closed", "finite_kinetic_isolation_closed", "finite_potential_scale_invariance_closed", "finite_weighted_isolation_closed"):
        derived[key] = True
    for key in ("phase_local_bkm_estimate_closed", "boundary_shell_l1_closed", "cutoff_uniformity_closed", "source_uniformity_closed", "volume_uniformity_closed", "shape_uniformity_closed", "operator_domain_embedding_closed", "direct_D_cauchy_closed", "delta_D_cauchy_closed", "common_alpha_closed", "hamiltonian_os_identification_closed", "kms_gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed"):
        derived[key] = False
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "independent", "audit_id": "PA-CP1-ST8-Q3LOCK-ANCHORED-NESTED-COMMUTATOR-KINETIC-ISOLATION-FINITE-CHECKPOINT", "claim_id": manifest["claim_ids"][0], "result_id": manifest["result_id"], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "assertion_count": assertions, "assertions": [{"status": "PASS"}], "derived": derived, "boundary": manifest["boundary"]}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = run()
    store(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT ANCHORED NESTED-COMMUTATOR KINETIC-ISOLATION PASS {payload['assertion_count']}/{payload['assertion_count']} contexts={payload['derived']['context_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

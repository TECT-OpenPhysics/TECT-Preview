#!/usr/bin/env python3
"""Primary exact finite-Q3 all-bond support-local weight recurrence audit (EXP-001084)."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from itertools import product
from pathlib import Path
from typing import Any

import numpy as np

REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-st8-q3lock-finite-q3-all-bond-support-local-weight-recurrence"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-24-primary-{SLUG}" / "primary.json"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pre_a_cp1_st8_q3lock_finite_structured_cutoff_orbit_modular_derivative as q3  # noqa: E402


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
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


def cube_edges(volume: int) -> list[tuple[int, int]]:
    if volume == 2:
        return [(0, 1)]
    if volume == 4:
        return [(0, 1), (0, 2), (1, 3), (2, 3)]
    vertices = list(product((0, 1), repeat=3))
    return [
        (left, right)
        for left in range(8)
        for right in range(left + 1, 8)
        if sum(a != b for a, b in zip(vertices[left], vertices[right])) == 1
    ]


def embedded(single: np.ndarray, site: int, volume: int, identity: np.ndarray) -> np.ndarray:
    factors = [single if index == site else identity for index in range(volume)]
    result = factors[0]
    for factor in factors[1:]:
        result = np.kron(result, factor)
    return result


def build_volume(volume: int, n: int, fixture: dict[str, Any]) -> tuple[list[np.ndarray], list[np.ndarray], list[np.ndarray], np.ndarray]:
    q_single, p_single = q3.oscillator(n)
    identity = np.eye(n, dtype=complex)
    q_ops = [embedded(q_single, site, volume, identity) for site in range(volume)]
    p_ops = [embedded(p_single, site, volume, identity) for site in range(volume)]
    chi, r, g = (float(fixture[key]) for key in ("chi", "r", "g"))
    c, lam = float(fixture["c"]), float(fixture["lambda"])
    onsite: list[np.ndarray] = []
    for site in range(volume):
        q, p = q_ops[site], p_ops[site]
        onsite.append(p @ p / (2.0 * chi) + r * (q @ q) / 2.0 + g * (q @ q @ q @ q) / 4.0)
    bonds: list[np.ndarray] = []
    for left, right in cube_edges(volume):
        difference = q_ops[left] - q_ops[right]
        bonds.append(c * (difference @ difference) / 2.0 + lam * (difference @ difference) @ (q_ops[left] @ q_ops[left] + q_ops[right] @ q_ops[right]) / 4.0)
    full = sum(onsite, np.zeros_like(q_ops[0])) + sum(bonds, np.zeros_like(q_ops[0]))
    return q_ops, p_ops, onsite, (full + full.conj().T) / 2.0


def support_for(volume: int, edge: tuple[int, int], radius: int) -> tuple[int, ...]:
    edges = cube_edges(volume)
    adjacency = {site: set() for site in range(volume)}
    for left, right in edges:
        adjacency[left].add(right)
        adjacency[right].add(left)
    support = set(edge)
    frontier = set(edge)
    for _ in range(radius):
        frontier = {neighbor for site in frontier for neighbor in adjacency[site]} - support
        support |= frontier
    return tuple(sorted(support))


def local_hamiltonian(
    volume: int, edge: tuple[int, int], radius: int, onsite: list[np.ndarray], bonds: list[np.ndarray], edges: list[tuple[int, int]]
) -> tuple[np.ndarray, tuple[int, ...]]:
    support = support_for(volume, edge, radius)
    selected = np.zeros_like(onsite[0])
    selected += sum((onsite[site] for site in support), np.zeros_like(onsite[0]))
    for bond, term in zip(edges, bonds):
        if bond[0] in support and bond[1] in support:
            selected += term
    return (selected + selected.conj().T) / 2.0, support


def kick(volume: int, n: int, edges: list[tuple[int, int]], fixture: dict[str, Any], sign: int) -> np.ndarray:
    q_single, _ = q3.oscillator(n)
    values, vectors = np.linalg.eigh((q_single + q_single.conj().T) / 2.0)
    basis = vectors
    for _ in range(volume - 1):
        basis = np.kron(basis, vectors)
    grid = np.asarray(list(product(values, repeat=volume)), dtype=float)
    coupling = float(fixture["c"])
    phase_sum = np.zeros(grid.shape[0], dtype=float)
    for left, right in edges:
        phase_sum += grid[:, left] * grid[:, right]
    phase = np.exp(1j * int(sign) * float(fixture["delta"]) * coupling * phase_sum / float(fixture["hbar"]))
    return (basis * phase) @ basis.conj().T


def spectral_power(matrix: np.ndarray, exponent: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((matrix + matrix.conj().T) / 2.0)
    if float(np.min(values)) <= 0.0 and exponent < 0.0:
        raise ValueError("negative spectral power requires a positive weight")
    values = np.maximum(values, 0.0)
    return (vectors * np.power(values, exponent)) @ vectors.conj().T


def operator_norm(matrix: np.ndarray) -> float:
    return float(np.linalg.svd(matrix, compute_uv=False)[0])


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001084" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001084/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("cube edges", len(cube_edges(8)) == 12 and len(cube_edges(4)) == 4 and cube_edges(2) == [(0, 1)], [len(cube_edges(8)), len(cube_edges(4)), cube_edges(2)], "12, 4, and target edge", "geometry")
    check("scope firewall", scope["finite_q3_cube_matrix_model_closed"] and scope["all_bond_two_orientation_recurrence_fixture_closed"] and not scope["support_local_volume_uniformity_proved"], scope, "finite diagnostic only", "scope")
    tolerance = float(fixture["residual_tolerance"])
    finite_residual_bound = float(fixture["finite_residual_bound"])
    volume_rows: list[dict[str, Any]] = []
    for volume in (int(value) for value in fixture["volume_values"]):
        n = int(fixture["oscillator_dimension_by_volume"][str(volume)])
        edges = cube_edges(volume)
        q_ops, p_ops, onsite, full_h = build_volume(volume, n, fixture)
        kicks = {sign: kick(volume, n, edges, fixture, sign) for sign in (-1, 1)}
        commutator_residuals: list[float] = []
        for sign, bond_kick in kicks.items():
            for site in range(volume):
                neighbor_sum = sum((q_ops[right] if left == site else q_ops[left] for left, right in edges if left == site or right == site), np.zeros_like(q_ops[0]))
                expected_p = p_ops[site] + sign * float(fixture["delta"]) * float(fixture["c"]) * neighbor_sum
                commutator_residuals.append(operator_norm(bond_kick.conj().T @ p_ops[site] @ bond_kick - expected_p))
                check(f"V={volume} sign={sign} p recurrence site={site}", np.isfinite(commutator_residuals[-1]) and commutator_residuals[-1] <= finite_residual_bound, commutator_residuals[-1], f"finite and <={finite_residual_bound}", "one-layer recurrence")
                check(f"V={volume} sign={sign} q invariance site={site}", operator_norm(bond_kick.conj().T @ q_ops[site] @ bond_kick - q_ops[site]) <= tolerance, "finite", f"<={tolerance}", "one-layer recurrence")
        weight_rows: list[dict[str, Any]] = []
        for edge in edges:
            edge_row: dict[str, Any] = {"edge": list(edge), "supports": {}}
            for radius, label in ((0, "endpoint"), (1, "one_layer"), (volume, "full")):
                local_h, support = local_hamiltonian(volume, edge, radius, onsite, [
                    c for c in []
                ], edges)
                # Rebuild bond terms once without relying on a positional placeholder.
                _, _, onsite_again, full_again = build_volume(volume, n, fixture)
                difference_terms: list[np.ndarray] = []
                for left, right in edges:
                    difference = q_ops[left] - q_ops[right]
                    difference_terms.append(float(fixture["c"]) * (difference @ difference) / 2.0 + float(fixture["lambda"]) * (difference @ difference) @ (q_ops[left] @ q_ops[left] + q_ops[right] @ q_ops[right]) / 4.0)
                local_h, support = local_hamiltonian(volume, edge, radius, onsite_again, difference_terms, edges)
                minimum = float(np.min(np.linalg.eigvalsh(local_h)))
                weight = local_h - minimum * np.eye(local_h.shape[0], dtype=complex) + np.eye(local_h.shape[0], dtype=complex)
                w_half, w_minus = spectral_power(weight, 0.5), spectral_power(weight, -0.5)
                oriented: dict[str, Any] = {}
                for sign, bond_kick in kicks.items():
                    ratio = operator_norm(w_half @ bond_kick @ w_minus)
                    form_ratio = float(np.max(np.linalg.eigvalsh((w_minus @ bond_kick.conj().T @ weight @ bond_kick @ w_minus + (w_minus @ bond_kick.conj().T @ weight @ bond_kick @ w_minus).conj().T) / 2.0)))
                    oriented[str(sign)] = {"graph_ratio": ratio, "form_ratio": form_ratio, "empirical_C": max(0.0, form_ratio - 1.0) / float(fixture["delta"])}
                    check(f"V={volume} edge={edge} {label} sign={sign} finite", np.isfinite(ratio) and np.isfinite(form_ratio), [ratio, form_ratio], "finite", "support-local weight")
                edge_row["supports"][label] = {"sites": list(support), "minimum_before_shift": minimum, "orientations": oriented}
            weight_rows.append(edge_row)
        volume_rows.append({"volume": volume, "dimension": n**volume, "edge_count": len(edges), "max_commutator_residual": max(commutator_residuals), "weights": weight_rows})
        check(f"V={volume} all edges", len(weight_rows) == len(edges), len(weight_rows), len(edges), "all-bond coverage")
    check("volume sequence", [row["volume"] for row in volume_rows] == fixture["volume_values"], [row["volume"] for row in volume_rows], fixture["volume_values"], "volume")
    check("two orientations", all(set(item["supports"]["endpoint"]["orientations"]) == {"-1", "1"} for row in volume_rows for item in row["weights"]), "present", "both signs", "orientation")
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "primary", "audit_id": "PA-CP1-ST8-Q3LOCK-FINITE-ALL-BOND-SUPPORT-LOCAL-WEIGHT-RECURRENCE", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "passed": len(rows), "assertion_count": len(rows), "assertions": rows, "derived": {"volume_rows": volume_rows, "all_bond_two_orientation_fixture_closed": True, "support_local_volume_uniformity_proved": False, "cutoff_uniformity_proved": False, "exact_ccr_common_core_closed": False, "modular_domain_transfer_closed": False, "volume_uniform_direct_d_cauchy_closed": False, "delta_d_cauchy_closed": False, "all_bond_graph_lipschitz_closed": False, "common_alpha_closed": False}, "boundary": scope}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY FINITE-Q3-ALL-BOND-SUPPORT-LOCAL-WEIGHT PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

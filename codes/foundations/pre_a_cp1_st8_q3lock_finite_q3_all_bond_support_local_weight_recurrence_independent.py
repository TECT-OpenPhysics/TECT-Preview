#!/usr/bin/env python3
"""Independent NumPy reconstruction for EXP-001084 (no primary import)."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from itertools import product
from pathlib import Path
from typing import Any

import numpy as np

REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-st8-q3lock-finite-q3-all-bond-support-local-weight-recurrence"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-24-primary-{SLUG}" / "independent.json"


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True, default=float)
            stream.write("\n"); stream.flush(); os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary): os.unlink(temporary)


def oscillator(n: int) -> tuple[np.ndarray, np.ndarray]:
    annihilation = np.zeros((n, n), dtype=complex)
    for index in range(n - 1):
        annihilation[index, index + 1] = np.sqrt(index + 1.0)
    creation = annihilation.conj().T
    return (annihilation + creation) / np.sqrt(2.0), (annihilation - creation) / (1j * np.sqrt(2.0))


def edges(volume: int) -> list[tuple[int, int]]:
    if volume == 2: return [(0, 1)]
    if volume == 4: return [(0, 1), (0, 2), (1, 3), (2, 3)]
    vertices = list(product((0, 1), repeat=3))
    return [(i, j) for i in range(8) for j in range(i + 1, 8) if sum(a != b for a, b in zip(vertices[i], vertices[j])) == 1]


def embed(single: np.ndarray, site: int, volume: int, identity: np.ndarray) -> np.ndarray:
    factors = [single if index == site else identity for index in range(volume)]
    result = factors[0]
    for factor in factors[1:]: result = np.kron(result, factor)
    return result


def graph_support(volume: int, edge: tuple[int, int], radius: int) -> tuple[int, ...]:
    adjacency = {site: set() for site in range(volume)}
    for left, right in edges(volume): adjacency[left].add(right); adjacency[right].add(left)
    support, frontier = set(edge), set(edge)
    for _ in range(radius):
        frontier = {neighbor for site in frontier for neighbor in adjacency[site]} - support
        support |= frontier
    return tuple(sorted(support))


def matrix_power(matrix: np.ndarray, exponent: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((matrix + matrix.conj().T) / 2.0)
    if exponent < 0 and float(np.min(values)) <= 0: raise ValueError("nonpositive weight")
    return (vectors * np.power(np.maximum(values, 0.0), exponent)) @ vectors.conj().T


def norm(matrix: np.ndarray) -> float:
    return float(np.linalg.svd(matrix, compute_uv=False)[0])


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8")); fixture, scope = manifest["finite_fixture"], manifest["scope"]
    rows: list[dict[str, Any]] = []
    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition: raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})
    check("identity", manifest["exploration_id"] == "EXP-001084" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001084/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("cube edges", len(edges(8)) == 12 and len(edges(4)) == 4 and edges(2) == [(0, 1)], [len(edges(8)), len(edges(4)), edges(2)], "12, 4, and target edge", "geometry")
    tol = float(fixture["residual_tolerance"]); finite_residual_bound = float(fixture["finite_residual_bound"]); all_volumes: list[dict[str, Any]] = []
    for volume in map(int, fixture["volume_values"]):
        n = int(fixture["oscillator_dimension_by_volume"][str(volume)])
        edge_list = edges(volume); q_single, p_single = oscillator(n); identity = np.eye(n, dtype=complex)
        q_ops = [embed(q_single, site, volume, identity) for site in range(volume)]
        p_ops = [embed(p_single, site, volume, identity) for site in range(volume)]
        onsite: list[np.ndarray] = []
        for site in range(volume):
            q, p = q_ops[site], p_ops[site]
            onsite.append(p @ p / (2 * float(fixture["chi"])) + float(fixture["r"]) * (q @ q) / 2 + float(fixture["g"]) * (q @ q @ q @ q) / 4)
        bond_terms: list[np.ndarray] = []
        for left, right in edge_list:
            d = q_ops[left] - q_ops[right]
            bond_terms.append(float(fixture["c"]) * (d @ d) / 2 + float(fixture["lambda"]) * (d @ d) @ (q_ops[left] @ q_ops[left] + q_ops[right] @ q_ops[right]) / 4)
        values, vectors = np.linalg.eigh((q_single + q_single.conj().T) / 2); basis = vectors
        for _ in range(volume - 1): basis = np.kron(basis, vectors)
        grid = np.asarray(list(product(values, repeat=volume)), dtype=float)
        phase_sum = sum((grid[:, left] * grid[:, right] for left, right in edge_list), np.zeros(grid.shape[0]))
        kicks = {sign: (basis * np.exp(1j * sign * float(fixture["delta"]) * float(fixture["c"]) * phase_sum / float(fixture["hbar"]))) @ basis.conj().T for sign in (-1, 1)}
        residuals: list[float] = []
        for sign, bond_kick in kicks.items():
            for site in range(volume):
                neighbor_sum = sum((q_ops[right] if left == site else q_ops[left] for left, right in edge_list if left == site or right == site), np.zeros_like(q_ops[0]))
                residuals.append(norm(bond_kick.conj().T @ p_ops[site] @ bond_kick - p_ops[site] - sign * float(fixture["delta"]) * float(fixture["c"]) * neighbor_sum))
                check(f"V={volume} sign={sign} p recurrence site={site}", np.isfinite(residuals[-1]) and residuals[-1] <= finite_residual_bound, residuals[-1], f"finite and <={finite_residual_bound}", "one-layer recurrence")
                q_residual = norm(bond_kick.conj().T @ q_ops[site] @ bond_kick - q_ops[site])
                check(f"V={volume} sign={sign} q invariance site={site}", q_residual <= tol, q_residual, f"<={tol}", "one-layer recurrence")
        edge_rows: list[dict[str, Any]] = []
        for edge in edge_list:
            row: dict[str, Any] = {"edge": list(edge), "supports": {}}
            for radius, label in ((0, "endpoint"), (1, "one_layer"), (volume, "full")):
                support = graph_support(volume, edge, radius); local = sum((onsite[site] for site in support), np.zeros_like(q_ops[0]))
                for bond, term in zip(edge_list, bond_terms):
                    if bond[0] in support and bond[1] in support: local += term
                local = (local + local.conj().T) / 2; minimum = float(np.min(np.linalg.eigvalsh(local)))
                weight = local - minimum * np.eye(local.shape[0], dtype=complex) + np.eye(local.shape[0], dtype=complex)
                half, inverse = matrix_power(weight, 0.5), matrix_power(weight, -0.5)
                orientations: dict[str, Any] = {}
                for sign, bond_kick in kicks.items():
                    transformed = inverse @ bond_kick.conj().T @ weight @ bond_kick @ inverse
                    transformed = (transformed + transformed.conj().T) / 2
                    form_ratio = float(np.max(np.linalg.eigvalsh(transformed))); graph_ratio = norm(half @ bond_kick @ inverse)
                    orientations[str(sign)] = {"graph_ratio": graph_ratio, "form_ratio": form_ratio, "empirical_C": max(0.0, form_ratio - 1.0) / float(fixture["delta"])}
                    check(f"V={volume} edge={edge} {label} sign={sign} finite", np.isfinite(graph_ratio) and np.isfinite(form_ratio), [graph_ratio, form_ratio], "finite", "support-local weight")
                row["supports"][label] = {"sites": list(support), "minimum_before_shift": minimum, "orientations": orientations}
            edge_rows.append(row)
        all_volumes.append({"volume": volume, "dimension": n**volume, "edge_count": len(edge_list), "max_commutator_residual": max(residuals), "weights": edge_rows})
        check(f"V={volume} all edges", len(edge_rows) == len(edge_list), len(edge_rows), len(edge_list), "all-bond coverage")
    check("volume sequence", [item["volume"] for item in all_volumes] == fixture["volume_values"], [item["volume"] for item in all_volumes], fixture["volume_values"], "volume")
    check("two orientations", all(set(item["supports"]["endpoint"]["orientations"]) == {"-1", "1"} for row in all_volumes for item in row["weights"]), "present", "both signs", "orientation")
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "independent", "audit_id": "PA-CP1-ST8-Q3LOCK-FINITE-ALL-BOND-SUPPORT-LOCAL-WEIGHT-RECURRENCE", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "passed": len(rows), "assertion_count": len(rows), "assertions": rows, "derived": {"volume_rows": all_volumes, "all_bond_two_orientation_fixture_closed": True, "support_local_volume_uniformity_proved": False, "cutoff_uniformity_proved": False, "exact_ccr_common_core_closed": False, "modular_domain_transfer_closed": False, "volume_uniform_direct_d_cauchy_closed": False, "delta_d_cauchy_closed": False, "all_bond_graph_lipschitz_closed": False, "common_alpha_closed": False}, "boundary": scope}


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT); parser.add_argument("--self-test", action="store_true"); args = parser.parse_args(); payload = run()
    if not args.self_test: atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT FINITE-Q3-ALL-BOND-SUPPORT-LOCAL-WEIGHT PASS {payload['passed']}/{payload['assertion_count']}"); return 0


if __name__ == "__main__": raise SystemExit(main())

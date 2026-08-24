#!/usr/bin/env python3
"""Independent tensor-product lane for EXP-001083."""

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
SLUG = "pre-a-cp1-st8-q3lock-finite-q3-cube-local-global-weight-volume-stress"
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


def oscillator(size: int) -> tuple[np.ndarray, np.ndarray]:
    lower = np.zeros((size, size), dtype=complex)
    for index in range(size - 1): lower[index, index + 1] = np.sqrt(index + 1.0)
    upper = lower.conj().T
    return (lower + upper) / np.sqrt(2.0), (lower - upper) / (1j * np.sqrt(2.0))


def gibbs(hamiltonian: np.ndarray, beta: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((hamiltonian + hamiltonian.conj().T) / 2.0)
    weights = np.exp(-beta * (values - np.min(values)))
    return (vectors * weights) @ vectors.conj().T / np.sum(weights)


def edges(volume: int) -> list[tuple[int, int]]:
    if volume == 2: return [(0, 1)]
    vertices = list(product((0, 1), repeat=3))
    return [(i, j) for i in range(8) for j in range(i + 1, 8) if sum(a != b for a, b in zip(vertices[i], vertices[j])) == 1]


def embed(single: np.ndarray, site: int, volume: int, identity: np.ndarray) -> np.ndarray:
    factors = [single if k == site else identity for k in range(volume)]
    result = factors[0]
    for factor in factors[1:]: result = np.kron(result, factor)
    return result


def model(volume: int, n: int, fixture: dict[str, Any]) -> tuple[list[np.ndarray], list[np.ndarray], np.ndarray, np.ndarray, np.ndarray]:
    q, p = oscillator(n); identity = np.eye(n, dtype=complex)
    q_ops = [embed(q, k, volume, identity) for k in range(volume)]
    p_ops = [embed(p, k, volume, identity) for k in range(volume)]
    chi, r, g = float(fixture["chi"]), float(fixture["r"]), float(fixture["g"]); c, lam = float(fixture["c"]), float(fixture["lambda"])
    onsites = [(p_ops[k] @ p_ops[k]) / (2.0 * chi) + r * (q_ops[k] @ q_ops[k]) / 2.0 + g * (q_ops[k] @ q_ops[k] @ q_ops[k] @ q_ops[k]) / 4.0 for k in range(volume)]
    bonds: dict[tuple[int, int], np.ndarray] = {}
    for i, j in edges(volume):
        d = q_ops[i] - q_ops[j]
        bonds[(i, j)] = c * (d @ d) / 2.0 + lam * (d @ d) @ (q_ops[i] @ q_ops[i] + q_ops[j] @ q_ops[j]) / 4.0
    zero = np.zeros_like(q_ops[0]); full = sum(onsites, zero) + sum(bonds.values(), zero); local = onsites[0] + onsites[1] + bonds[(0, 1)]
    return q_ops, p_ops, (full + full.conj().T) / 2.0, (local + local.conj().T) / 2.0, q


def cutoff(values: np.ndarray, radius: float) -> tuple[np.ndarray, np.ndarray]:
    scaled = np.abs(values) / radius
    eta = np.where(scaled <= 1.0, 1.0, np.where(scaled < 2.0, 0.5 * (1.0 + np.cos(np.pi * (scaled - 1.0))), 0.0))
    eta_one = np.where(scaled <= 1.0, 0.0, np.where(scaled < 2.0, -0.5 * np.pi * np.sin(np.pi * (scaled - 1.0)), 0.0))
    return values * eta, eta + scaled * eta_one


def bond(q: np.ndarray, v: np.ndarray, c: float, lam: float) -> np.ndarray:
    d = q - v; return c * d**2 / 2.0 + lam * d**2 * (q**2 + v**2) / 4.0


def force(q: np.ndarray, v: np.ndarray, c: float, lam: float) -> np.ndarray:
    d = q - v; return c * d + lam * d * (2.0 * q**2 - q * v + v**2) / 2.0


def force_prime(q: np.ndarray, v: np.ndarray, c: float, lam: float) -> np.ndarray:
    d = q - v; return c + lam * (q**2 + v**2 + d**2 + 4.0 * q * d) / 2.0


def coordinate(values: np.ndarray, vectors: np.ndarray, volume: int) -> np.ndarray:
    joint = vectors
    for _ in range(volume - 1): joint = np.kron(joint, vectors)
    return joint @ np.diag(values.reshape(-1)) @ joint.conj().T


def power(matrix: np.ndarray, exponent: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((matrix + matrix.conj().T) / 2.0)
    if float(np.min(values)) < -1.0e-10: raise ValueError("nonpositive spectrum")
    values = np.maximum(values, 0.0)
    if exponent < 0.0 and float(np.min(values)) <= 0.0: raise ValueError("negative power needs positivity")
    return (vectors * np.power(values, exponent)) @ vectors.conj().T


def opnorm(matrix: np.ndarray) -> float: return float(np.linalg.svd(matrix, compute_uv=False)[0])
def hsnorm(matrix: np.ndarray) -> float: return float(np.linalg.norm(matrix, ord="fro"))


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8")); fixture, scope = manifest["finite_fixture"], manifest["scope"]
    rows: list[dict[str, Any]] = []
    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition: raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})
    check("identity", manifest["exploration_id"] == "EXP-001083" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001083/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("geometry", len(edges(8)) == 12 and edges(2) == [(0, 1)], [len(edges(8)), edges(2)], "Q3 cube", "geometry")
    check("scope firewall", scope["finite_support_local_weight_defined"] and scope["finite_full_volume_weight_defined"] and not scope["volume_uniform_local_weight_proved"], scope, "finite comparison", "scope")
    tol, factor_tol = float(fixture["bound_tolerance"]), float(fixture["factorization_tolerance"]); c, lam, hbar, beta = float(fixture["c"]), float(fixture["lambda"]), float(fixture["hbar"]), float(fixture["beta"])
    volume_rows: list[dict[str, Any]] = []
    for volume_value in fixture["volume_values"]:
        volume, n = int(volume_value), int(fixture["oscillator_dimension"]); q_ops, p_ops, full_h, local_h, q_single = model(volume, n, fixture); rho = gibbs(full_h, beta); rho_sqrt = power(rho, 0.5); q_values_single, q_vectors = np.linalg.eigh((q_single + q_single.conj().T) / 2.0)
        q_values, v_values = np.meshgrid(q_values_single, q_values_single, indexing="ij"); q_cut, q_prime = cutoff(q_values, float(fixture["radius"])); v_cut, _ = cutoff(v_values, float(fixture["radius"])); tail = bond(q_values, v_values, c, lam) - bond(q_cut, v_cut, c, lam); force_value = force(q_values, v_values, c, lam); fprime = force_prime(q_values, v_values, c, lam); cut_force = force(q_cut, v_cut, c, lam); mixed = tail * force_value; mixed_prime = (force_value - cut_force * q_prime) * force_value + tail * fprime
        shape = (n, n) + (1,) * (volume - 2); multiplier = coordinate(np.broadcast_to(mixed.reshape(shape), (n,) * volume), q_vectors, volume); coordinate_derivative = coordinate(np.broadcast_to(mixed_prime.reshape(shape), (n,) * volume), q_vectors, volume); p0 = p_ops[0]; residual = p0 @ multiplier - multiplier @ p0 + 1j * hbar * coordinate_derivative; right_leg, left_leg = hsnorm(multiplier @ p0 @ rho_sqrt), hsnorm(p0 @ multiplier @ rho_sqrt); actual_root = float(np.sqrt(max(0.0, right_leg**2 + left_leg**2))); weight_rows: dict[str, Any] = {}
        for kind, base in (("local", local_h), ("full", full_h)):
            values = np.linalg.eigvalsh(base); weight = base - float(np.min(values)) * np.eye(base.shape[0], dtype=complex) + np.eye(base.shape[0], dtype=complex); w34, wm34 = power(weight, 0.75), power(weight, -0.75); kplus, kzero = hsnorm(w34 @ p0 @ rho_sqrt), hsnorm(w34 @ rho_sqrt); u, v, rr = opnorm(multiplier @ wm34), opnorm(coordinate_derivative @ wm34), opnorm(residual @ wm34); rb = u * kplus; lb = rb + hbar * v * kzero + rr * kzero; root = float(np.sqrt(max(0.0, rb**2 + lb**2))); check(f"V={volume} {kind} factor", hsnorm(multiplier @ p0 - (multiplier @ wm34) @ (w34 @ p0)) < factor_tol, "finite", f"<{factor_tol}", "factorization"); check(f"V={volume} {kind} bound", actual_root**2 <= rb**2 + lb**2 + tol * (1.0 + root**2), [actual_root, root], "actual<=corrected", "weighted bound"); check(f"V={volume} {kind} finite", all(np.isfinite(x) for x in (u, v, rr, kplus, kzero, root)), "finite", "finite", "diagnostic"); weight_rows[kind] = {"u_energy": u, "v_energy": v, "residual_energy": rr, "k_plus": kplus, "k_zero": kzero, "corrected_bound_root": root}
        volume_rows.append({"volume": volume, "dimension": n**volume, "actual_root": actual_root, "right_leg": right_leg, "left_leg": left_leg, "weights": weight_rows})
    check("weights present", all(set(row["weights"]) == {"local", "full"} for row in volume_rows), volume_rows, "local/full", "scope"); check("volume count", len(volume_rows) == len(fixture["volume_values"]), len(volume_rows), len(fixture["volume_values"]), "volume")
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "independent", "audit_id": "PA-CP1-ST8-Q3LOCK-FINITE-Q3-CUBE-LOCAL-GLOBAL-WEIGHT-VOLUME-STRESS", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "passed": len(rows), "assertion_count": len(rows), "assertions": rows, "derived": {"volume_rows": volume_rows, "finite_support_local_weight_defined": True, "finite_full_volume_weight_defined": True, "finite_corrected_two_sided_bound_closed": True, "local_full_weight_equivalence_proved": False, "volume_uniform_local_weight_proved": False, "cutoff_uniformity_proved": False, "exact_ccr_domain_closed": False, "modular_domain_transfer_closed": False, "volume_uniform_direct_d_cauchy_closed": False, "delta_d_cauchy_closed": False, "all_bond_graph_lipschitz_closed": False, "common_alpha_closed": False}, "boundary": scope}


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT); parser.add_argument("--self-test", action="store_true"); args = parser.parse_args(); payload = run()
    if not args.self_test: atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT FINITE-Q3-CUBE-LOCAL-GLOBAL-WEIGHT PASS {payload['passed']}/{payload['assertion_count']}"); return 0


if __name__ == "__main__": raise SystemExit(main())

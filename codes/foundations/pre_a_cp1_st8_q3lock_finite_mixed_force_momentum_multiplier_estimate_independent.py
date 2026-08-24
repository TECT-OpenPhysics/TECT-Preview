#!/usr/bin/env python3
"""Independent numpy lane for EXP-001081.

This lane reconstructs the oscillator, Q3 Hamiltonian, Gibbs state, cutoff
chain rule and mixed-product estimate without importing the primary audit.
"""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path
from typing import Any

import numpy as np


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-st8-q3lock-finite-mixed-force-momentum-multiplier-estimate"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / (
    f"2026-08-24-primary-{SLUG}/independent.json"
)


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


def oscillator(size: int) -> tuple[np.ndarray, np.ndarray]:
    annihilation = np.zeros((size, size), dtype=complex)
    for index in range(size - 1):
        annihilation[index, index + 1] = np.sqrt(index + 1.0)
    creation = annihilation.conj().T
    return (annihilation + creation) / np.sqrt(2.0), (annihilation - creation) / (1j * np.sqrt(2.0))


def q3_hamiltonian(size: int, fixture: dict[str, Any]) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    q, p = oscillator(size)
    identity = np.eye(size, dtype=complex)
    q_one = np.kron(q, identity)
    q_two = np.kron(identity, q)
    p_one = np.kron(p, identity)
    p_two = np.kron(identity, p)
    chi = float(fixture["chi"])
    r = float(fixture["r"])
    g = float(fixture["g"])
    c = float(fixture["c"])
    lam = float(fixture["lambda"])
    onsite = (p_one @ p_one + p_two @ p_two) / (2.0 * chi) + r * (q_one @ q_one + q_two @ q_two) / 2.0 + g * (q_one @ q_one @ q_one @ q_one + q_two @ q_two @ q_two @ q_two) / 4.0
    difference = q_one - q_two
    bond = c * difference @ difference / 2.0 + lam * (difference @ difference) @ (q_one @ q_one + q_two @ q_two) / 4.0
    return q_one, q_two, p_one, onsite + bond


def gibbs(hamiltonian: np.ndarray, beta: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((hamiltonian + hamiltonian.conj().T) / 2.0)
    shifted = values - np.min(values)
    weights = np.exp(-beta * shifted)
    return (vectors * weights) @ vectors.conj().T / np.sum(weights)


def seminorm(rho: np.ndarray, operator: np.ndarray) -> float:
    right = np.trace(rho @ operator.conj().T @ operator).real
    left = np.trace(rho @ operator @ operator.conj().T).real
    return float(np.sqrt(max(0.0, right + left)))


def cutoff(values: np.ndarray, radius: float) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    scaled = np.abs(values) / radius
    taper = np.where(scaled <= 1.0, 1.0, np.where(scaled < 2.0, 0.5 * (1.0 + np.cos(np.pi * (scaled - 1.0))), 0.0))
    taper_one = np.where(scaled <= 1.0, 0.0, np.where(scaled < 2.0, -0.5 * np.pi * np.sin(np.pi * (scaled - 1.0)), 0.0))
    taper_two = np.where(scaled <= 1.0, 0.0, np.where(scaled < 2.0, -0.5 * np.pi**2 * np.cos(np.pi * (scaled - 1.0)), 0.0))
    cut = values * taper
    first = taper + scaled * taper_one
    second = np.where(np.abs(values) <= np.finfo(float).eps, 0.0, np.sign(values) * (2.0 * taper_one + scaled * taper_two) / radius)
    return cut, first, second


def bond(q_value: np.ndarray, v_value: np.ndarray, c: float, lam: float) -> np.ndarray:
    difference = q_value - v_value
    return c * difference**2 / 2.0 + lam * difference**2 * (q_value**2 + v_value**2) / 4.0


def force(q_value: np.ndarray, v_value: np.ndarray, c: float, lam: float) -> np.ndarray:
    difference = q_value - v_value
    return c * difference + lam * difference * (2.0 * q_value**2 - q_value * v_value + v_value**2) / 2.0


def force_prime(q_value: np.ndarray, v_value: np.ndarray, c: float, lam: float) -> np.ndarray:
    difference = q_value - v_value
    return c + lam * (q_value**2 + v_value**2 + difference**2 + 4.0 * q_value * difference) / 2.0


def coordinate_matrix(values: np.ndarray, vectors: np.ndarray) -> np.ndarray:
    joint = np.kron(vectors, vectors)
    return joint @ np.diag(values.reshape(-1)) @ joint.conj().T


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    scope = manifest["scope"]
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001081" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001081/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("finite parameters", fixture["beta"] > 0 and fixture["chi"] > 0 and fixture["hbar"] > 0 and fixture["g"] > 0, fixture, "positive finite parameters", "model")
    check("scope firewall", scope["finite_two_sided_mixed_multiplier_bound_closed"] and not scope["unweighted_cutoff_uniformity_proved"] and not scope["energy_weighted_mixed_bound_closed"], scope, "finite bound only", "scope")

    tolerance = float(fixture["bound_tolerance"])
    c = float(fixture["c"])
    lam = float(fixture["lambda"])
    hbar = float(fixture["hbar"])
    beta = float(fixture["beta"])
    rows_by_size: list[dict[str, Any]] = []
    fixed_u: list[float] = []

    for n_value in fixture["n_values"]:
        n = int(n_value)
        q_one, q_two, p_one, hamiltonian = q3_hamiltonian(n, fixture)
        rho = gibbs(hamiltonian, beta)
        q_single, _ = oscillator(n)
        eigenvalues, eigenvectors = np.linalg.eigh((q_single + q_single.conj().T) / 2.0)
        kinetic_root = float(np.sqrt(max(0.0, np.trace(rho @ (p_one @ p_one)).real)))
        radius_rows: list[dict[str, Any]] = []
        for radius_value in fixture["radius_values"]:
            radius = float(radius_value)
            q_values, v_values = np.meshgrid(eigenvalues, eigenvalues, indexing="ij")
            q_cut, q_prime, _ = cutoff(q_values, radius)
            v_cut, _, _ = cutoff(v_values, radius)
            tail = bond(q_values, v_values, c, lam) - bond(q_cut, v_cut, c, lam)
            force_value = force(q_values, v_values, c, lam)
            force_prime_value = force_prime(q_values, v_values, c, lam)
            cut_force = force(q_cut, v_cut, c, lam)
            tail_prime = force_value - cut_force * q_prime
            mixed = tail * force_value
            mixed_prime = tail_prime * force_value + tail * force_prime_value
            mixed_matrix = coordinate_matrix(mixed, eigenvectors)
            actual_root = seminorm(rho, mixed_matrix @ p_one)
            multiplier_norm = float(np.max(np.abs(mixed)))
            derivative_norm = float(np.max(np.abs(mixed_prime)))
            bound_squared = (multiplier_norm * kinetic_root) ** 2 + (multiplier_norm * kinetic_root + hbar * derivative_norm) ** 2
            bound_root = float(np.sqrt(max(0.0, bound_squared)))
            check(f"n={n} L={radius} bound", actual_root**2 <= bound_squared + tolerance * (1.0 + bound_squared), [actual_root, bound_root], "actual<=bound", "mixed bound")
            radius_rows.append({"radius": radius, "actual_root": actual_root, "bound_root": bound_root, "multiplier_norm": multiplier_norm, "derivative_norm": derivative_norm, "kinetic_root": kinetic_root, "bound_squared": bound_squared, "bound_margin": bound_root - actual_root})
            if abs(radius - float(fixture["scaling_radius"])) <= tolerance:
                fixed_u.append(multiplier_norm)
        rows_by_size.append({"n": n, "dimension": n * n, "kinetic_root": kinetic_root, "radii": radius_rows})

    check("finite scaling ordering", all(next_value + float(fixture["scaling_tolerance"]) >= current for current, next_value in zip(fixed_u, fixed_u[1:])), fixed_u, "nondecreasing diagnostic", "scaling")
    check("all finite", all(np.isfinite(row["actual_root"]) and np.isfinite(row["bound_root"]) for item in rows_by_size for row in item["radii"]), rows_by_size, "finite", "diagnostic")

    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "audit_id": "PA-CP1-ST8-Q3LOCK-FINITE-MIXED-FORCE-MOMENTUM-MULTIPLIER-ESTIMATE",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": len(rows),
        "assertion_count": len(rows),
        "assertions": rows,
        "derived": {"dimension_rows": rows_by_size, "fixed_radius_multiplier_norms": fixed_u, "finite_two_sided_mixed_multiplier_bound_closed": True, "unweighted_multiplier_scaling_diagnostic_closed": True, "unweighted_cutoff_uniformity_proved": False, "energy_weighted_mixed_bound_closed": False, "volume_uniform_direct_d_cauchy_closed": False, "delta_d_cauchy_closed": False},
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
    print(f"INDEPENDENT FINITE-MIXED-FORCE-MOMENTUM PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

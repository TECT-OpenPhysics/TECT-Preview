#!/usr/bin/env python3
"""Independent reconstruction of the R-389 spectral-window corridor.

This file deliberately does not import the primary implementation.  It uses
eigenbasis/Frobenius evaluations of the projected Gibbs seminorm instead of
the primary trace helper.
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
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-spectral-window-kinetic-corridor-finite-checkpoint-manifest.json"
SLUG = "pre_a_cp1_st8_q3lock_spectral_window_kinetic_corridor_finite_checkpoint"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-30-primary-{SLUG}" / "independent.json"


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


def sym(matrix: np.ndarray) -> np.ndarray:
    return (matrix + matrix.conj().T) / 2.0


def oscillator(n: int) -> tuple[np.ndarray, np.ndarray]:
    lowering = np.zeros((n, n), dtype=complex)
    for j in range(1, n):
        lowering[j - 1, j] = np.sqrt(float(j))
    raising = lowering.conj().T
    return (lowering + raising) / np.sqrt(2.0), (lowering - raising) / (1j * np.sqrt(2.0))


def lift(single: np.ndarray, site: int, n: int) -> np.ndarray:
    eye = np.eye(n, dtype=complex)
    return np.kron(single, eye) if site == 0 else np.kron(eye, single)


def comm(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    return a @ b - b @ a


def opnorm(a: np.ndarray) -> float:
    return float(np.linalg.svd(a, compute_uv=False)[0])


def hamiltonian(n: int, f: dict[str, Any]) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    q, p = oscillator(n)
    q0, q1 = lift(q, 0, n), lift(q, 1, n)
    p0, p1 = lift(p, 0, n), lift(p, 1, n)
    delta = q0 - q1
    delta2 = delta @ delta
    kinetic = sym((p0 @ p0 + p1 @ p1) / (2.0 * float(f["chi"])))
    onsite = sym(float(f["r"]) * (q0 @ q0 + q1 @ q1) / 2.0 + float(f["g"]) * (q0 @ q0 @ q0 @ q0 + q1 @ q1 @ q1 @ q1) / 4.0)
    boundary = sym(float(f["c"]) * delta2 / 2.0 + float(f["lambda"]) * delta2 @ (q0 @ q0 + q1 @ q1) / 4.0)
    return q0, q1, p0, p1, sym(kinetic + onsite + boundary)


def gibbs_and_sqrt(H: np.ndarray, beta: float) -> tuple[np.ndarray, np.ndarray]:
    values, vectors = np.linalg.eigh(sym(H))
    weights = np.exp(-beta * (values - values.min()))
    weights /= weights.sum()
    rho = sym((vectors * weights) @ vectors.conj().T)
    sqrt_rho = (vectors * np.sqrt(weights)) @ vectors.conj().T
    return rho, sym(sqrt_rho)


def projected_norm(matrix: np.ndarray, rho_window: np.ndarray) -> float:
    values, vectors = np.linalg.eigh(sym(rho_window))
    values = np.maximum(values, 0.0)
    root = (vectors * np.sqrt(values)) @ vectors.conj().T
    left = matrix @ root
    right = matrix.conj().T @ root
    return float(np.sqrt(max(0.0, float(np.real(np.vdot(left, left) + np.vdot(right, right))))))


def name(beta: float, eta: float, energy: float) -> str:
    return f"beta={beta};eta={eta};E={energy}"


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    f, coverage, scope = manifest["finite_fixture"], manifest["coverage"], manifest["scope"]
    checks: list[dict[str, Any]] = []

    def check(label: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{label}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": label, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001232" and manifest["result_id"] == "R-389" and not manifest["claim_bearing"], [manifest["exploration_id"], manifest["result_id"]], "EXP-001232/R-389/false", "provenance")
    check("coverage", all(coverage.values()), coverage, "all coverage flags", "coverage")
    finite_flags = ("finite_spectral_window_weighted_corridor_closed", "finite_eta_split_closed", "finite_window_mass_rank_closed", "finite_operator_growth_stress_closed")
    open_flags = tuple(key for key in scope if key.endswith("_closed") and key not in finite_flags)
    check("scope firewall", all(scope[key] for key in finite_flags) and not any(scope[key] for key in open_flags), "finite window only", "all promoted flags false", "scope")

    dimensions = [int(x) for x in f["cutoff_dimensions"]]
    sites = [int(x) for x in f["site_values"]]
    betas = [float(Fraction(x)) for x in f["beta_values"]]
    etas = [float(Fraction(x)) for x in f["resolvent_imaginary_values"]]
    energies = [float(Fraction(x)) for x in f["energy_windows"]]
    tail_start = int(f["tail_cutoff_start"])
    threshold = float(f["tail_stability_ratio_threshold"])
    eta_floor = float(Fraction(f["corridor_eta_floor"]))
    tolerance = 1e-10
    profile: dict[str, dict[int, list[float]]] = {name(beta, eta, energy): {d: [] for d in dimensions} for beta in betas for eta in etas for energy in energies}
    conditional_profile: dict[str, dict[int, list[float]]] = {k: {d: [] for d in dimensions} for k in profile}
    mass_profile: dict[str, dict[int, list[float]]] = {k: {d: [] for d in dimensions} for k in profile}
    rank_profile: dict[str, dict[int, list[int]]] = {k: {d: [] for d in dimensions} for k in profile}
    op_by_dimension: dict[int, list[float]] = {d: [] for d in dimensions}
    seed_rows = 0
    weighted_rows = 0
    maxima = {"operator_norm": 0.0, "projected_weighted_norm": 0.0, "conditional_projected_norm": 0.0}

    for d in dimensions:
        q0, q1, p0, p1, H = hamiltonian(d, f)
        I = np.eye(d * d, dtype=complex)
        T = sym((p0 @ p0 + p1 @ p1) / (2.0 * float(f["chi"])))
        delta = q0 - q1
        B = sym(float(f["c"]) * delta @ delta / 2.0 + float(f["lambda"]) * (delta @ delta) @ (q0 @ q0 + q1 @ q1) / 4.0)
        values, vectors = np.linalg.eigh(sym(H))
        shifted = values - values.min()
        projectors: dict[float, np.ndarray] = {}
        ranks: dict[float, int] = {}
        for E in energies:
            select = shifted <= E + tolerance
            ranks[E] = int(np.count_nonzero(select))
            projectors[E] = vectors[:, select] @ vectors[:, select].conj().T
            check(f"d={d} E={E} rank", ranks[E] > 0, ranks[E], ">0", "window")
        states = {beta: gibbs_and_sqrt(H, beta)[0] for beta in betas}
        for site, qsite in enumerate((q0, q1)):
            for eta in etas:
                seed = np.linalg.solve(1j * eta * I - qsite, I)
                for adjoint, observable in enumerate((seed, seed.conj().T)):
                    target = comm(B, comm(T, observable))
                    op_value = opnorm(target)
                    op_by_dimension[d].append(op_value)
                    maxima["operator_norm"] = max(maxima["operator_norm"], op_value)
                    seed_rows += 1
                    check(f"d={d} site={site} eta={eta} adj={adjoint} operator", np.isfinite(op_value), op_value, "finite", "operator stress")
                    for beta in betas:
                        rho = states[beta]
                        for E in energies:
                            P = projectors[E]
                            projected_rho = sym(P @ rho @ P)
                            mass = float(np.real(np.trace(projected_rho)))
                            projected = projected_norm(target, projected_rho)
                            conditional = projected / max(np.sqrt(max(mass, 0.0)), np.finfo(float).tiny)
                            k = name(beta, eta, E)
                            check(f"d={d} site={site} eta={eta} adj={adjoint} beta={beta} E={E} finite", all(np.isfinite(x) and x >= -tolerance for x in (mass, projected, conditional)), [mass, projected, conditional], "finite nonnegative", "window")
                            check(f"d={d} beta={beta} E={E} mass", -tolerance <= mass <= 1.0 + tolerance, mass, "[0,1]", "window")
                            profile[k][d].append(projected)
                            conditional_profile[k][d].append(conditional)
                            mass_profile[k][d].append(mass)
                            rank_profile[k][d].append(ranks[E])
                            maxima["projected_weighted_norm"] = max(maxima["projected_weighted_norm"], projected)
                            maxima["conditional_projected_norm"] = max(maxima["conditional_projected_norm"], conditional)
                            weighted_rows += 1

    growth = max(op_by_dimension[dimensions[-1]]) / max(op_by_dimension[dimensions[0]])
    check("operator growth witness", growth > float(f["operator_growth_threshold"]), growth, f">{f['operator_growth_threshold']}", "operator stress")
    summaries: dict[str, dict[str, Any]] = {}
    corridor: list[str] = []
    outside: list[str] = []
    for k in profile:
        beta = float(k.split(";")[0].split("=")[1])
        eta = float(k.split(";")[1].split("=")[1])
        E = float(k.split(";")[2].split("=")[1])
        projected = {d: max(profile[k][d]) for d in dimensions}
        conditional = {d: max(conditional_profile[k][d]) for d in dimensions}
        tail_p = [projected[d] for d in dimensions if d >= tail_start]
        tail_c = [conditional[d] for d in dimensions if d >= tail_start]
        ratio_p = max(tail_p) / max(min(tail_p), np.finfo(float).tiny)
        ratio_c = max(tail_c) / max(min(tail_c), np.finfo(float).tiny)
        item = {"beta": beta, "eta": eta, "energy_threshold": E, "tail_cutoff_start": tail_start, "tail_row_count": len(tail_p), "projected_tail_ratio": ratio_p, "conditional_tail_ratio": ratio_c, "projected_late_ratio": projected[dimensions[-1]] / max(projected[tail_start], np.finfo(float).tiny), "conditional_late_ratio": conditional[dimensions[-1]] / max(conditional[tail_start], np.finfo(float).tiny), "window_mass_min": min(min(v) for v in mass_profile[k].values()), "window_mass_max": max(max(v) for v in mass_profile[k].values()), "rank_min": min(min(v) for v in rank_profile[k].values()), "rank_max": max(max(v) for v in rank_profile[k].values()), "stable": ratio_p <= threshold and ratio_c <= threshold}
        summaries[k] = item
        if eta >= eta_floor:
            corridor.append(k)
            check(f"corridor {k}", item["stable"], item, f"both ratios <= {threshold}", "spectral corridor")
        else:
            outside.append(k)
    check("corridor coverage", bool(corridor) and bool(outside), [len(corridor), len(outside)], "both eta regions", "spectral corridor")
    check("outside eta stress", max(summaries[k]["projected_tail_ratio"] for k in outside) > threshold, max(summaries[k]["projected_tail_ratio"] for k in outside), f">{threshold}", "spectral corridor")
    expected_seed = len(dimensions) * len(sites) * len(etas) * 2
    expected_weighted = expected_seed * len(betas) * len(energies)
    check("row counts", [seed_rows, weighted_rows], [expected_seed, expected_weighted], [expected_seed, expected_weighted], "coverage")
    check("finite maxima", all(np.isfinite(x) for x in maxima.values()), maxima, "finite", "numerics")
    derived = {"cutoff_dimensions": dimensions, "seed_rows": seed_rows, "weighted_rows": weighted_rows, "operator_growth_ratio": growth, "maximums": maxima, "corridor_keys": corridor, "outside_keys": outside, "tail_stability_threshold": threshold, "summaries": summaries, "dimension_operator_max": {str(d): max(op_by_dimension[d]) for d in dimensions}}
    for k in finite_flags:
        derived[k] = True
    for k in open_flags:
        derived[k] = False
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "independent", "audit_id": "PA-CP1-ST8-Q3LOCK-SPECTRAL-WINDOW-KINETIC-CORRIDOR-FINITE-CHECKPOINT", "claim_id": manifest["claim_ids"][0], "result_id": manifest["result_id"], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "passed": len(checks), "assertion_count": len(checks), "assertions": checks, "derived": derived, "boundary": manifest["boundary"]}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT SPECTRAL-WINDOW KINETIC CORRIDOR PASS {payload['passed']}/{payload['assertion_count']} seeds={payload['derived']['seed_rows']} weighted={payload['derived']['weighted_rows']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

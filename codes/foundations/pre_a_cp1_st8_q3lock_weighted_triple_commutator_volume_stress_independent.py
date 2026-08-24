#!/usr/bin/env python3
"""Independent finite-Q3 reconstruction for EXP-001088.

This lane deliberately rebuilds the oscillator, graph, cutoff, Gibbs state,
Hamiltonian, nested commutators, and weighted four-leg seminorm without
importing the primary module.
"""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
NAME = "pre_a_cp1_st8_q3lock_weighted_triple_commutator_volume_stress"
MANIFEST = ROOT / f"strategy/{NAME}_manifest.json"
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-25-primary-{NAME}" / "independent.json"


def store(path: Path, payload: dict[str, Any]) -> None:
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


def q_and_p(size: int) -> tuple[np.ndarray, np.ndarray]:
    a = np.zeros((size, size), dtype=np.complex128)
    for row in range(size - 1):
        a[row, row + 1] = np.sqrt(float(row + 1))
    return (a + a.T.conj()) / np.sqrt(2.0), (a - a.T.conj()) / (1j * np.sqrt(2.0))


def edges(size: int) -> tuple[tuple[int, int], ...]:
    lookup = {
        2: ((0, 1),),
        4: ((0, 1), (0, 2), (1, 3), (2, 3)),
        6: ((0, 1), (1, 2), (3, 4), (4, 5), (0, 3), (1, 4), (2, 5)),
    }
    return lookup[size]


def tensor_site(single: np.ndarray, site: int, volume: int, identity: np.ndarray) -> np.ndarray:
    result = np.array([[1.0 + 0.0j]])
    for index in range(volume):
        result = np.kron(result, single if index == site else identity)
    return result


def bond(q_left: np.ndarray, q_right: np.ndarray, data: dict[str, Any]) -> np.ndarray:
    d = q_left - q_right
    c, lam = float(data["c"]), float(data["lambda"])
    return c * (d @ d) / 2.0 + lam * (d @ d) @ (q_left @ q_left + q_right @ q_right) / 4.0


def model(volume: int, size: int, data: dict[str, Any], bond_coordinate: np.ndarray) -> tuple[list[np.ndarray], np.ndarray, np.ndarray, dict[tuple[int, int], np.ndarray]]:
    q0, p0 = q_and_p(size)
    eye = np.eye(size, dtype=np.complex128)
    qs = [tensor_site(q0, site, volume, eye) for site in range(volume)]
    ps = [tensor_site(p0, site, volume, eye) for site in range(volume)]
    cut_qs = [tensor_site(bond_coordinate, site, volume, eye) for site in range(volume)]
    chi, r, g = float(data["chi"]), float(data["r"]), float(data["g"])
    onsite = [p @ p / (2.0 * chi) + r * (q @ q) / 2.0 + g * (q @ q @ q @ q) / 4.0 for q, p in zip(qs, ps)]
    bonds = {(left, right): bond(cut_qs[left], cut_qs[right], data) for left, right in edges(volume)}
    zero = np.zeros_like(qs[0])
    total = sum(onsite, zero) + sum(bonds.values(), zero)
    local = onsite[0] + onsite[1] + bonds[(0, 1)]
    return qs, (total + total.T.conj()) / 2.0, (local + local.T.conj()) / 2.0, bonds


def smooth_cut(q: np.ndarray, radius: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((q + q.T.conj()) / 2.0)
    scaled = np.abs(values) / radius
    taper = np.ones_like(scaled)
    taper[scaled >= 2.0] = 0.0
    band = (scaled > 1.0) & (scaled < 2.0)
    taper[band] = 0.5 * (1.0 + np.cos(np.pi * (scaled[band] - 1.0)))
    return (vectors * (values * taper)) @ vectors.T.conj()


def thermal_state(h: np.ndarray, beta: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((h + h.T.conj()) / 2.0)
    weights = np.exp(-beta * (values - values.min()))
    weights /= weights.sum()
    return (vectors * weights) @ vectors.T.conj()


def power(positive: np.ndarray, exponent: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((positive + positive.T.conj()) / 2.0)
    if values.min() < -1.0e-9:
        raise AssertionError(f"nonpositive matrix: {values.min()}")
    return (vectors * np.power(np.maximum(values, 0.0), exponent)) @ vectors.T.conj()


def shifted(base: np.ndarray) -> np.ndarray:
    hermitian = (base + base.T.conj()) / 2.0
    return hermitian - np.linalg.eigvalsh(hermitian).min() * np.eye(base.shape[0]) + np.eye(base.shape[0])


def exp_character(generator: np.ndarray, amplitude: float, hbar: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((generator + generator.T.conj()) / 2.0)
    return (vectors * np.exp(1j * amplitude * values / hbar)) @ vectors.T.conj()


def bracket(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    return left @ right - right @ left


def frobenius(matrix: np.ndarray) -> float:
    return float(np.linalg.norm(matrix, ord="fro"))


def spectral_norm(matrix: np.ndarray) -> float:
    return float(np.linalg.svd(matrix, compute_uv=False)[0])


def gns(matrix: np.ndarray, rho: np.ndarray) -> float:
    value = np.trace(rho @ matrix.T.conj() @ matrix) + np.trace(rho @ matrix @ matrix.T.conj())
    return float(np.sqrt(max(0.0, float(np.real(value)))))


def four_leg(matrix: np.ndarray, weight_power: np.ndarray, rho_half: np.ndarray) -> float:
    legs = [
        weight_power @ matrix @ rho_half,
        weight_power @ matrix.T.conj() @ rho_half,
        matrix @ weight_power @ rho_half,
        matrix.T.conj() @ weight_power @ rho_half,
    ]
    return float(np.sqrt(sum(frobenius(item) ** 2 for item in legs)))


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    rows: list[dict[str, Any]] = []

    def check(name: str, ok: bool, actual: Any, expected: Any, group: str) -> None:
        if not ok:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001088" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001088/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("geometry", edges(2) == ((0, 1),) and len(edges(4)) == 4 and len(edges(6)) == 7, [edges(2), len(edges(4)), len(edges(6))], "target/square/2x3", "geometry")
    check("scope firewall", scope["finite_triple_commutator_identity_closed"] and scope["finite_weighted_two_sided_rows_closed"] and not scope["candidate_volume_uniform_bound_closed"], scope, "finite weighted diagnostic", "scope")

    beta, amplitude, hbar = float(fixture["beta"]), float(fixture["character_amplitude"]), float(fixture["hbar"])
    tol, tail_tol, exponent = float(fixture["commutator_tolerance"]), float(fixture["tail_tolerance"]), float(fixture["weight_exponent"])
    volume_rows: list[dict[str, Any]] = []
    for volume in [int(value) for value in fixture["volume_values"]]:
        q0, _ = q_and_p(int(fixture["oscillator_dimension"]))
        qs, hamiltonian, local_hamiltonian, uncut_bonds = model(volume, int(fixture["oscillator_dimension"]), fixture, q0)
        rho = thermal_state(hamiltonian, beta)
        rho_half = power(rho, 0.5)
        observable = exp_character(qs[0] + qs[1], amplitude, hbar)
        h_observable = bracket(hamiltonian, observable)
        local_power = power(shifted(local_hamiltonian), exponent)
        full_power = power(shifted(hamiltonian), exponent)
        cut_rows: list[dict[str, Any]] = []
        for radius in [float(value) for value in fixture["radius_values"]]:
            cut_q = smooth_cut(q0, radius)
            _, _, _, cut_bonds = model(volume, int(fixture["oscillator_dimension"]), fixture, cut_q)
            zero = np.zeros_like(hamiltonian)
            tails = {edge: uncut_bonds[edge] - cut_bonds[edge] for edge in edges(volume)}
            tail = sum(tails.values(), zero)
            tail_norm = spectral_norm(tail)
            source_comm = spectral_norm(bracket(tail, observable))
            inner = bracket(tail, h_observable)
            d2 = -inner / (hbar * hbar)
            triple = bracket(hamiltonian, inner)
            modular = -beta * bracket(hamiltonian, d2)
            identity_error = spectral_norm(modular - beta * triple / (hbar * hbar))
            disjoint_tail = sum((tails[edge] for edge in edges(volume) if set(edge).isdisjoint(set(fixture["observable_support"]))), zero)
            disjoint_comm = spectral_norm(bracket(disjoint_tail, observable))
            check(f"V={volume} L={radius} identity", identity_error <= tol, identity_error, f"<={tol}", "triple identity")
            check(f"V={volume} L={radius} source", source_comm <= tol, source_comm, f"<={tol}", "configuration commutation")
            check(f"V={volume} L={radius} disjoint", disjoint_comm <= tol, disjoint_comm, f"<={tol}", "support locality")
            if radius == max(float(value) for value in fixture["radius_values"]):
                check(f"V={volume} zero tail", tail_norm <= tail_tol, tail_norm, f"<={tail_tol}", "cutoff")
            weight_data: dict[str, Any] = {}
            for name, weight in (("local", local_power), ("full", full_power)):
                values = {
                    "D2_gibbs": gns(d2, rho),
                    "modular_D2_gibbs": gns(modular, rho),
                    "D2_weighted": four_leg(d2, weight, rho_half),
                    "modular_weighted": four_leg(modular, weight, rho_half),
                    "tail_operator_norm": tail_norm,
                    "modular_identity_error": identity_error,
                }
                check(f"V={volume} L={radius} {name} finite", all(np.isfinite(value) for value in values.values()), values, "finite", "weighted triple")
                weight_data[name] = values
            cut_rows.append({"radius": radius, "source_commutator_norm": source_comm, "disjoint_tail_commutator_norm": disjoint_comm, "weights": weight_data})
        volume_rows.append({"volume": volume, "dimension": int(fixture["oscillator_dimension"]) ** volume, "radius_rows": cut_rows})

    check("volume sequence", [row["volume"] for row in volume_rows] == fixture["volume_values"], [row["volume"] for row in volume_rows], fixture["volume_values"], "volume")

    def maxima(weight: str, field: str) -> list[float]:
        return [max(item["weights"][weight][field] for item in row["radius_rows"]) for row in volume_rows]

    local_modular, full_modular = maxima("local", "modular_weighted"), maxima("full", "modular_weighted")
    local_d2, full_d2 = maxima("local", "D2_weighted"), maxima("full", "D2_weighted")
    local_growth = local_modular[-1] / max(local_modular[0], np.finfo(float).tiny)
    full_growth = full_modular[-1] / max(full_modular[0], np.finfo(float).tiny)
    check("maxima finite", all(np.isfinite(value) for value in local_modular + full_modular + local_d2 + full_d2), [local_modular, full_modular], "finite", "scaling")
    check("growth captured", local_growth >= float(fixture["growth_threshold"]) and full_growth >= float(fixture["growth_threshold"]), [local_growth, full_growth], f">={fixture['growth_threshold']}", "scaling")
    check("support locality", all(float(row["source_commutator_norm"]) <= tol and float(row["disjoint_tail_commutator_norm"]) <= tol for volume in volume_rows for row in volume["radius_rows"]), "all rows", "tolerance", "support locality")
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "audit_id": "PA-CP1-ST8-Q3LOCK-WEIGHTED-TRIPLE-COMMUTATOR-VOLUME-STRESS",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": len(rows),
        "assertion_count": len(rows),
        "assertions": rows,
        "derived": {
            "volume_rows": volume_rows,
            "weight_exponent": exponent,
            "local_modular_weighted_maxima": local_modular,
            "full_modular_weighted_maxima": full_modular,
            "local_D2_weighted_maxima": local_d2,
            "full_D2_weighted_maxima": full_d2,
            "local_modular_volume_growth": local_growth,
            "full_modular_volume_growth": full_growth,
            "finite_triple_commutator_identity_closed": True,
            "finite_weighted_two_sided_rows_closed": True,
            "candidate_volume_growth_diagnostic_closed": True,
            "candidate_volume_uniform_bound_closed": False,
            "weighted_modular_domain_closed": False,
            "volume_uniform_direct_d_cauchy_closed": False,
            "delta_d_cauchy_closed": False,
            "positive_time_history_closed": False,
            "product_core_density_closed": False,
            "exhaustion_independence_closed": False,
            "group_law_closed": False,
            "common_alpha_closed": False,
        },
        "boundary": scope,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        store(args.output if args.output.is_absolute() else ROOT / args.output, payload)
    print(f"INDEPENDENT WEIGHTED-TRIPLE-COMMUTATOR-VOLUME-STRESS PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

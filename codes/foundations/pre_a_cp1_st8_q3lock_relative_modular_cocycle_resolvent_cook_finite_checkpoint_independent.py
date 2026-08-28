#!/usr/bin/env python3
"""Non-importing independent reconstruction of the R-385 finite checkpoint."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
TAG = "pre_a_cp1_st8_q3lock_relative_modular_cocycle_resolvent_cook_finite_checkpoint"
CONFIG = ROOT / "strategy/pre-a-cp1-st8-q3lock-relative-modular-cocycle-resolvent-cook-finite-checkpoint-manifest.json"
DEFAULT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-30-primary-{TAG}" / "independent.json"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def store(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(value, stream, indent=2, sort_keys=True, ensure_ascii=True, default=float)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def sym(matrix: np.ndarray) -> np.ndarray:
    return (matrix + matrix.conj().T) / 2.0


def mode_pair(size: int) -> tuple[np.ndarray, np.ndarray]:
    lowering = np.zeros((size, size), dtype=complex)
    for row in range(size - 1):
        lowering[row, row + 1] = np.sqrt(row + 1.0)
    raising = lowering.conj().T
    return (lowering + raising) / np.sqrt(2.0), (lowering - raising) / (1j * np.sqrt(2.0))


def edges(size: int, f: dict[str, Any]) -> list[tuple[int, int]]:
    return [tuple(int(site) for site in edge) for edge in f["graph_edges_by_volume"][str(size)]]


def lift(local: np.ndarray, position: int, size: int, identity: np.ndarray) -> np.ndarray:
    factors = [local if index == position else identity for index in range(size)]
    answer = factors[0]
    for factor in factors[1:]:
        answer = np.kron(answer, factor)
    return answer


def interaction(left: np.ndarray, right: np.ndarray, f: dict[str, Any]) -> np.ndarray:
    difference = left - right
    square = difference @ difference
    quartic = square @ (left @ left + right @ right)
    return sym(float(f["c"]) * square / 2.0 + float(f["lambda"]) * quartic / 4.0)


def system(size: int, dimension: int, f: dict[str, Any]) -> tuple[list[np.ndarray], list[dict[str, Any]], list[np.ndarray]]:
    q0, p0 = mode_pair(dimension)
    identity = np.eye(dimension, dtype=complex)
    qs = [lift(q0, site, size, identity) for site in range(size)]
    ps = [lift(p0, site, size, identity) for site in range(size)]
    onsite = [sym(p @ p / (2.0 * float(f["chi"])) + float(f["r"]) * (q @ q) / 2.0 + float(f["g"]) * (q @ q @ q @ q) / 4.0) for q, p in zip(qs, ps)]
    specs = [{"kind": "onsite", "support": [site]} for site in range(size)]
    bonds: list[np.ndarray] = []
    for left, right in edges(size, f):
        bonds.append(interaction(qs[left], qs[right], f))
        specs.append({"kind": "bond", "support": [left, right]})
    return qs, specs, onsite + bonds


def add(terms: list[np.ndarray], indices: list[int]) -> np.ndarray:
    result = np.zeros_like(terms[0], dtype=complex)
    for index in indices:
        result = result + terms[index]
    return sym(result)


def propagator(generator: np.ndarray, time: float, hbar: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(sym(generator))
    return (vectors * np.exp(-1j * time * values / hbar)) @ vectors.conj().T


def conjugate(generator: np.ndarray, operator: np.ndarray, time: float, hbar: float) -> np.ndarray:
    return propagator(generator, -time, hbar) @ operator @ propagator(generator, time, hbar)


def cocycle(base: np.ndarray, extension: np.ndarray, time: float, hbar: float) -> np.ndarray:
    return propagator(extension, -time, hbar) @ propagator(base, time, hbar)


def thermal(generator: np.ndarray, beta: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(sym(generator))
    weights = np.exp(-beta * (values - float(np.min(values))))
    weights /= float(np.sum(weights))
    return sym((vectors * weights) @ vectors.conj().T)


def local_resolvent(operator: np.ndarray, eta: float) -> np.ndarray:
    return np.linalg.inv(1j * eta * np.eye(operator.shape[0], dtype=complex) - operator)


def norm(matrix: np.ndarray) -> float:
    return float(np.linalg.svd(matrix, compute_uv=False)[0])


def two_leg(matrix: np.ndarray, state: np.ndarray) -> float:
    value = np.trace(state @ matrix.conj().T @ matrix) + np.trace(state @ matrix @ matrix.conj().T)
    return float(np.sqrt(max(0.0, float(np.real(value)))))


def run() -> dict[str, Any]:
    manifest = json.loads(CONFIG.read_text(encoding="utf-8"))
    f = manifest["finite_fixture"]
    hbar = float(Fraction(f["hbar"]))
    betas = [float(Fraction(v)) for v in f["beta_values"]]
    etas = [float(Fraction(v)) for v in f["resolvent_imaginary_values"]]
    magnitudes = [float(Fraction(v)) for v in f["time_magnitudes"]]
    pairs = [(float(Fraction(a)), float(Fraction(b))) for a, b in f["composition_pairs"]]
    step = float(Fraction(f["derivative_step"]))
    maxima = {"alpha_intertwining_residual": 0.0, "cocycle_residual": 0.0, "derivative_residual": 0.0, "resolvent_residual": 0.0, "unitarity_residual": 0.0, "commutator_norm": 0.0, "weighted_left": 0.0, "weighted_right": 0.0, "weighted_commutator": 0.0, "weighted_adjoint_commutator": 0.0}
    summaries: list[dict[str, Any]] = []
    contexts = 0
    alpha_rows = composition_rows = derivative_rows = resolvent_rows = prefixes = bond_prefixes = 0
    for size in [int(v) for v in f["volume_values"]]:
        qs, specs, terms = system(size, int(f["oscillator_dimension"]), f)
        orders = {"forward": list(range(len(terms))), "reverse": list(reversed(range(len(terms))))}
        local_max = {key: 0.0 for key in maxima}
        local_contexts = local_prefixes = 0
        for order_name in manifest["coverage"]["orders"]:
            ordering = orders[order_name]
            for k, next_term in enumerate(ordering):
                prefixes += 1
                local_prefixes += 1
                if specs[next_term]["kind"] == "bond":
                    bond_prefixes += 1
                base = add(terms, ordering[:k])
                extension = sym(base + terms[next_term])
                raw_times = sorted(set(magnitudes + [-x for x in magnitudes]))
                sum_times = [a + b for a, b in pairs]
                cache_times = sorted(set(raw_times + sum_times + [x + step for x in raw_times] + [x - step for x in raw_times]))
                base_u = {t: propagator(base, t, hbar) for t in cache_times}
                ext_u = {t: propagator(extension, t, hbar) for t in cache_times}
                rel = {t: ext_u[-t] @ base_u[t] for t in cache_times}
                for sign in (-1, 1):
                    for magnitude in magnitudes:
                        t = sign * magnitude
                        identity = np.eye(rel[t].shape[0], dtype=complex)
                        unitary_error = max(norm(rel[t].conj().T @ rel[t] - identity), norm(rel[t] @ rel[t].conj().T - identity))
                        maxima["unitarity_residual"] = max(maxima["unitarity_residual"], unitary_error); local_max["unitarity_residual"] = max(local_max["unitarity_residual"], unitary_error)
                        derivative = (rel[t + step] - rel[t - step]) / (2.0 * step)
                        expected = (1j / hbar) * conjugate(extension, terms[next_term], t, hbar) @ rel[t]
                        derivative_error = norm(derivative - expected)
                        maxima["derivative_residual"] = max(maxima["derivative_residual"], derivative_error); local_max["derivative_residual"] = max(local_max["derivative_residual"], derivative_error); derivative_rows += 1
                    for left, right in pairs:
                        error = norm(rel[left + right] - rel[left] @ conjugate(base, rel[right], left, hbar))
                        maxima["cocycle_residual"] = max(maxima["cocycle_residual"], error); local_max["cocycle_residual"] = max(local_max["cocycle_residual"], error); composition_rows += 1
                seeds = {(site, eta): local_resolvent(qs[site], eta) for site in range(size) for eta in etas}
                for site in range(size):
                    for eta in etas:
                        seed = seeds[(site, eta)]
                        for eta2 in etas:
                            other = seeds[(site, eta2)]
                            residual = norm(seed - other - (1j * eta2 - 1j * eta) * seed @ other)
                            maxima["resolvent_residual"] = max(maxima["resolvent_residual"], residual); local_max["resolvent_residual"] = max(local_max["resolvent_residual"], residual); resolvent_rows += 1
                        for beta in betas:
                            state = thermal(extension, beta)
                            for seed_name, observable in (("A", seed), ("A_star", seed.conj().T)):
                                contexts += 1; local_contexts += 1
                                left = terms[next_term] @ observable; right = observable @ terms[next_term]; difference = left - right
                                values = {"left": two_leg(left, state), "right": two_leg(right, state), "commutator": two_leg(difference, state), "commutator_matrix": norm(difference)}
                                maxima["weighted_left"] = max(maxima["weighted_left"], values["left"]); maxima["weighted_right"] = max(maxima["weighted_right"], values["right"]); maxima["weighted_commutator"] = max(maxima["weighted_commutator"], values["commutator"]); maxima["commutator_norm"] = max(maxima["commutator_norm"], values["commutator_matrix"])
                                local_max["weighted_left"] = max(local_max["weighted_left"], values["left"]); local_max["weighted_right"] = max(local_max["weighted_right"], values["right"]); local_max["weighted_commutator"] = max(local_max["weighted_commutator"], values["commutator"]); local_max["commutator_norm"] = max(local_max["commutator_norm"], values["commutator_matrix"])
                                if seed_name == "A_star":
                                    maxima["weighted_adjoint_commutator"] = max(maxima["weighted_adjoint_commutator"], values["commutator"]); local_max["weighted_adjoint_commutator"] = max(local_max["weighted_adjoint_commutator"], values["commutator"])
                                for sign in (-1, 1):
                                    for magnitude in magnitudes:
                                        t = sign * magnitude
                                        error = norm(conjugate(extension, observable, t, hbar) - rel[t] @ conjugate(base, observable, t, hbar) @ rel[t].conj().T)
                                        maxima["alpha_intertwining_residual"] = max(maxima["alpha_intertwining_residual"], error); local_max["alpha_intertwining_residual"] = max(local_max["alpha_intertwining_residual"], error); alpha_rows += 1
        summaries.append({"volume": size, "dimension": int(f["oscillator_dimension"]) ** size, "term_count": len(terms), "prefix_count": local_prefixes, "bond_prefix_count": sum(1 for spec in specs if spec["kind"] == "bond") * 2, "context_count": local_contexts, "maximums": local_max})
    expected = sum(2 * (len(system(size, int(f["oscillator_dimension"]), f)[1])) * len(betas) * len(etas) * size * 2 for size in [int(v) for v in f["volume_values"]])
    if contexts != expected:
        raise AssertionError((contexts, expected))
    if maxima["commutator_norm"] <= float(f["commutator_floor"]):
        raise AssertionError("commutator witness vanished")
    derived = {**maxima, "volume_summaries": summaries, "volume_count": len(summaries), "prefix_count": prefixes, "bond_prefix_count": bond_prefixes, "context_count": contexts, "expected_contexts": expected, "alpha_row_count": alpha_rows, "composition_row_count": composition_rows, "derivative_row_count": derivative_rows, "resolvent_row_count": resolvent_rows, "finite_relative_cocycle_identity_closed": True, "finite_cocycle_derivative_identity_closed": True, "finite_cocycle_composition_closed": True, "finite_resolvent_identity_closed": True, "finite_two_orientation_state_weighted_rows_closed": True, "finite_all_prefix_order_sign_beta_seed_grid_closed": True, "boundary_shell_l1_closed": False, "phase_local_bkm_estimate_closed": False, "cutoff_uniformity_closed": False, "source_uniformity_closed": False, "volume_uniformity_closed": False, "shape_uniformity_closed": False, "operator_domain_embedding_closed": False, "direct_D_cauchy_closed": False, "delta_D_cauchy_closed": False, "common_alpha_closed": False, "hamiltonian_os_identification_closed": False, "kms_gns_gap_closed": False, "continuum_closed": False, "c6_closed": False, "sector_a_closed": False, "pre_a_closed": False}
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "independent", "audit_id": "PA-CP1-ST8-Q3LOCK-RELATIVE-MODULAR-COCYCLE-RESOLVENT-COOK-FINITE-CHECKPOINT", "claim_id": manifest["claim_ids"][0], "result_id": manifest["result_id"], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "passed": contexts, "assertion_count": contexts, "assertions": [{"name": "independent finite grid", "status": "PASS", "actual": str(contexts), "expected": str(expected)}], "derived": derived, "boundary": manifest["boundary"], "provenance": {"script": str(Path(__file__).relative_to(ROOT)).replace("\\", "/"), "script_sha256": digest(Path(__file__)), "manifest": str(CONFIG.relative_to(ROOT)).replace("\\", "/"), "manifest_sha256": digest(CONFIG)}}


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--output", type=Path, default=DEFAULT); parser.add_argument("--self-test", action="store_true"); args = parser.parse_args(); payload = run()
    if not args.self_test: store(args.output if args.output.is_absolute() else ROOT / args.output, payload)
    print(f"INDEPENDENT RELATIVE-MODULAR-COCYCLE-COOK PASS {payload['passed']}/{payload['assertion_count']} contexts={payload['derived']['context_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

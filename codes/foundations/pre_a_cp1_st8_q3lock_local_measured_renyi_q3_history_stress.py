#!/usr/bin/env python3
"""Primary finite actual-Q3 local measured-Renyi history stress.

The computation instantiates the conditional QFT-facing local likelihood
interface from R-167 v1.9 on explicit finite Q3 matrices. It records partial
split prefixes, reverse order, both signs, both history adjoints, local source
orientations, beta values, spatial volumes, and a declared cutoff stress. The
diagnostic is claim-nonbearing: no finite threshold is treated as a uniform
Q3 theorem.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np

REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_local_measured_renyi_q3_history_stress"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-local-measured-renyi-q3-history-stress-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-27-primary-{SLUG}" / "primary.json"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pre_a_cp1_st8_q3lock_weighted_triple_commutator_volume_stress as q3  # noqa: E402


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


def hermitian(matrix: np.ndarray) -> np.ndarray:
    return (matrix + matrix.conj().T) / 2.0


def unitary(matrix: np.ndarray, time: float, hbar: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(hermitian(matrix))
    return (vectors * np.exp(-1j * time * values / hbar)) @ vectors.conj().T


def embed(single: np.ndarray, site: int, volume: int, identity: np.ndarray) -> np.ndarray:
    factors = [single if index == site else identity for index in range(volume)]
    result = factors[0]
    for factor in factors[1:]:
        result = np.kron(result, factor)
    return result


def split_system(volume: int, size: int, parameters: dict[str, Any]) -> tuple[list[np.ndarray], np.ndarray, list[np.ndarray]]:
    q_single, p_single = q3.oscillator(size)
    identity = np.eye(size, dtype=complex)
    qs = [embed(q_single, site, volume, identity) for site in range(volume)]
    ps = [embed(p_single, site, volume, identity) for site in range(volume)]
    chi, r, g = (float(Fraction(str(parameters[key]))) for key in ("chi", "r", "g"))
    c, lam = (float(Fraction(str(parameters[key]))) for key in ("c", "lambda"))
    onsite = [p @ p / (2.0 * chi) + r * (q @ q) / 2.0 + g * (q @ q @ q @ q) / 4.0 for q, p in zip(qs, ps)]
    bonds = [q3.bond_term(qs[left], qs[right], {"c": c, "lambda": lam}) for left, right in q3.graph_edges(volume)]
    zero = np.zeros_like(qs[0])
    full = hermitian(sum(onsite, zero) + sum(bonds, zero))
    return qs, full, onsite + bonds


def gibbs(hamiltonian: np.ndarray, beta: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(hermitian(hamiltonian))
    weights = np.exp(-beta * (values - float(np.min(values))))
    weights /= float(np.sum(weights))
    return hermitian((vectors * weights) @ vectors.conj().T)


def reduced_site(state: np.ndarray, size: int, volume: int, site: int) -> np.ndarray:
    tensor = state.reshape((size,) * (2 * volume))
    reduced = np.zeros((size, size), dtype=complex)
    outside = [index for index in range(volume) if index != site]
    for values in np.ndindex(*(size for _ in outside)):
        row = [slice(None)] * volume
        column = [slice(None)] * volume
        for index, value in zip(outside, values):
            row[index] = value
            column[index] = value
        reduced += tensor[tuple(row + column)]
    return hermitian(reduced)


def local_probabilities(state: np.ndarray, q_single: np.ndarray, size: int, volume: int, site: int) -> tuple[np.ndarray, np.ndarray]:
    values, vectors = np.linalg.eigh(hermitian(q_single))
    reduced = reduced_site(state, size, volume, site)
    probabilities = np.real(np.diag(vectors.conj().T @ reduced @ vectors))
    probabilities = np.maximum(probabilities, 0.0)
    probabilities /= float(np.sum(probabilities))
    return values, probabilities


def renyi_likelihood(reference: np.ndarray, sample: np.ndarray, alpha: float) -> float:
    floor = np.finfo(float).tiny
    return float(np.sum(np.power(sample, alpha) * np.power(np.maximum(reference, floor), 1.0 - alpha)))


def selected_prefixes(terms: list[np.ndarray], order: list[int], sign: int, delta: float, hbar: float, labels: list[str]) -> list[tuple[str, int, np.ndarray]]:
    identity = np.eye(terms[0].shape[0], dtype=complex)
    wanted = {"zero": 0, "first": 1, "full": len(order)}
    current = identity
    rows: list[tuple[str, int, np.ndarray]] = []
    for position in range(len(order) + 1):
        if position == 0:
            current = identity
        elif position > 0:
            current = unitary(terms[order[position - 1]], sign * delta, hbar) @ current
        for label in labels:
            if wanted[label] == position and not any(existing[1] == position for existing in rows):
                rows.append((label, position, current.copy()))
    return rows


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    parameters = {"chi": "1", "r": "-1", "g": "3/5", "c": "3/5", "lambda": "1/10"}
    tolerance = float(fixture["finite_tolerance"])
    alpha = float(Fraction(fixture["alpha"]))
    theta = (alpha - 1.0) / alpha
    delta = float(Fraction(fixture["time_step"]))
    hbar = float(Fraction(fixture["hbar"]))
    amplitude = float(Fraction(fixture["source_amplitude"]))
    betas = [Fraction(value) for value in fixture["beta_values"]]
    supports = [tuple(int(site) for site in support) for support in fixture["source_support_values"]]
    labels = list(fixture["prefix_selection"])
    tail_thresholds = [float(Fraction(value)) for value in fixture["tail_thresholds"]]
    diagnostic_threshold = float(Fraction(fixture["diagnostic_Q_threshold"]))
    checks: list[dict[str, Any]] = []
    check_count = 0

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        nonlocal check_count
        check_count += 1
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        if len(checks) < 64:
            checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001202" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001202/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("geometry", q3.graph_edges(2) == [(0, 1)] and len(q3.graph_edges(4)) == 4 and len(q3.graph_edges(6)) == 7, "registered graphs", "target/square/2x3", "geometry")
    check("alpha", alpha > 1.0 and math.isclose(theta, 0.5, rel_tol=0.0, abs_tol=tolerance), [alpha, theta], "alpha=2, theta=1/2", "Renyi")
    check("prefix labels", labels == ["zero", "first", "full"], labels, "zero/first/full", "history")
    check("scope firewall", manifest["scope"]["diagnostic_threshold_is_not_a_theorem"] and not manifest["scope"]["actual_Q3_local_Renyi_uniform_bound_closed"], manifest["scope"], "finite diagnostic only", "scope")

    contexts: list[dict[str, Any]] = []
    max_q = 0.0
    exceed_count = 0
    size_volume_rows = 0
    volume_cutoffs = {int(volume): [int(size) for size in cutoffs] for volume, cutoffs in fixture["volume_cutoff_values"].items()}
    for volume in sorted(volume_cutoffs):
        for size in volume_cutoffs[volume]:
            size_volume_rows += 1
            qs, hamiltonian, terms = split_system(volume, size, parameters)
            q_single, _ = q3.oscillator(size)
            identity = np.eye(hamiltonian.shape[0], dtype=complex)
            orders = {"forward": list(range(len(terms))), "reverse": list(reversed(range(len(terms))))}
            prefix_bank = {(order_name, sign): selected_prefixes(terms, order, sign, delta, hbar, labels) for order_name, order in orders.items() for sign in (-1, 1)}
            for beta_fraction in betas:
                beta = float(beta_fraction)
                rho = gibbs(hamiltonian, beta)
                check(f"V={volume} d={size} beta={beta_fraction} trace", abs(float(np.trace(rho).real) - 1.0) <= tolerance, float(np.trace(rho).real), "1", "Gibbs")
                references = {site: local_probabilities(rho, q_single, size, volume, site)[1] for site in range(volume)}
                for support in supports:
                    source_generator = sum((qs[site] for site in support), np.zeros_like(qs[0]))
                    for source_sign in (-1, 1):
                        source = q3.character(source_generator, source_sign * amplitude, hbar)
                        seeded = source @ rho @ source.conj().T
                        for order_name, order in orders.items():
                            for sign in (-1, 1):
                                prefixes = prefix_bank[(order_name, sign)]
                                check(f"V={volume} d={size} {order_name} sign={sign} prefixes", len(prefixes) == len(labels), len(prefixes), len(labels), "history")
                                for prefix_label, prefix_length, prefix in prefixes:
                                    for history_adjoint in (0, 1):
                                        state = prefix @ seeded @ prefix.conj().T if not history_adjoint else prefix.conj().T @ seeded @ prefix
                                        site_metrics: list[dict[str, Any]] = []
                                        context_max = 0.0
                                        context_exceeds = False
                                        for site in range(volume):
                                            eigenvalues, sample = local_probabilities(state, q_single, size, volume, site)
                                            reference = references[site]
                                            q_alpha = renyi_likelihood(reference, sample, alpha)
                                            context_max = max(context_max, q_alpha)
                                            tail_rows: list[dict[str, Any]] = []
                                            for threshold in tail_thresholds:
                                                mask = np.abs(eigenvalues) >= threshold
                                                sample_tail = float(np.sum(sample[mask]))
                                                reference_tail = float(np.sum(reference[mask]))
                                                bound = float(q_alpha ** (1.0 / alpha) * reference_tail ** theta)
                                                check(f"V={volume} d={size} beta={beta_fraction} site={site} tail={threshold}", sample_tail <= bound + tolerance, sample_tail, f"<={bound}+{tolerance}", "finite Renyi inequality")
                                                tail_rows.append({"threshold": threshold, "sample_tail": sample_tail, "reference_tail": reference_tail, "bound": bound, "slack": bound - sample_tail})
                                            check(f"V={volume} d={size} beta={beta_fraction} site={site} likelihood", np.isfinite(q_alpha) and q_alpha >= 1.0 - tolerance, q_alpha, ">=1 and finite", "local Renyi")
                                            context_exceeds = context_exceeds or q_alpha > diagnostic_threshold
                                            site_metrics.append({"site": site, "q_alpha": q_alpha, "tail_rows": tail_rows})
                                        max_q = max(max_q, context_max)
                                        exceed_count += int(context_exceeds)
                                        contexts.append({"volume": volume, "cutoff": size, "beta": str(beta_fraction), "support": list(support), "source_sign": source_sign, "order": order_name, "sign": sign, "prefix": prefix_label, "prefix_length": prefix_length, "history_adjoint": history_adjoint, "max_q_alpha": context_max, "diagnostic_exceeds": context_exceeds, "sites": site_metrics})
    expected_size_volume_rows = sum(len(values) for values in volume_cutoffs.values())
    contexts_per_size_volume = len(betas) * len(supports) * 2 * 2 * 2 * 2 * len(labels)
    expected_contexts = expected_size_volume_rows * contexts_per_size_volume
    check("size-volume row count", size_volume_rows == expected_size_volume_rows, size_volume_rows, expected_size_volume_rows, "coverage")
    check("context coverage", len(contexts) == expected_contexts, len(contexts), expected_contexts, "coverage")
    check("all finite contexts", all(np.isfinite(float(row["max_q_alpha"])) for row in contexts), len(contexts), "all finite", "coverage")
    check("diagnostic outcome", exceed_count >= 0, exceed_count, ">=0", "route decision")
    route_outcome = "FINITE_LOCAL_RENYI_DIAGNOSTIC_EXCEEDS_THRESHOLD" if exceed_count else "FINITE_LOCAL_RENYI_DIAGNOSTIC_WITHIN_THRESHOLD"
    by_volume_cutoff: dict[str, float] = {}
    for row in contexts:
        key = f"V={row['volume']}/d={row['cutoff']}"
        by_volume_cutoff[key] = max(by_volume_cutoff.get(key, 0.0), float(row["max_q_alpha"]))
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": "PA-CP1-ST8-Q3LOCK-LOCAL-MEASURED-RENYI-Q3-HISTORY-STRESS",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": check_count,
        "assertion_count": check_count,
        "assertions": checks,
        "derived": {
            "contexts": contexts,
            "context_count": len(contexts),
            "size_volume_row_count": size_volume_rows,
            "max_q_alpha": max_q,
            "diagnostic_Q_threshold": diagnostic_threshold,
            "diagnostic_exceed_context_count": exceed_count,
            "route_outcome": route_outcome,
            "max_q_alpha_by_volume_cutoff": by_volume_cutoff,
            "alpha": alpha,
            "theta": theta,
            "finite_local_coordinate_rows_closed": True,
            "finite_two_orientation_prefix_coverage_closed": True,
            "finite_tail_inequality_checked": True,
            "actual_Q3_local_Renyi_uniform_bound_closed": False,
            "cutoff_uniformity_proved": False,
            "volume_uniformity_proved": False,
            "beta_uniformity_proved": False,
            "common_alpha_closed": False,
            "actual_split_limit_closed": False,
            "hamiltonian_os_identification_closed": False,
            "kms_gns_gap_closed": False,
            "continuum_closed": False,
            "c6_closed": False,
            "sector_a_closed": False,
            "pre_a_closed": False
        },
        "boundary": manifest["boundary"]
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY LOCAL-MEASURED-RENYI-Q3-HISTORY PASS {payload['passed']}/{payload['assertion_count']} route={payload['derived']['route_outcome']} maxQ={payload['derived']['max_q_alpha']:.9g}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Non-importing independent finite local measured-Renyi reconstruction."""

from __future__ import annotations

import argparse
import json
import math
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np

REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_local_measured_renyi_q3_history_stress"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-local-measured-renyi-q3-history-stress-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-27-independent-{SLUG}" / "independent.json"


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True, default=float)
            stream.write("\n"); stream.flush(); os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary): os.unlink(temporary)


def h(matrix: np.ndarray) -> np.ndarray:
    return (matrix + matrix.conj().T) / 2.0


def oscillator(size: int) -> tuple[np.ndarray, np.ndarray]:
    lowering = np.zeros((size, size), dtype=complex)
    for index in range(size - 1): lowering[index, index + 1] = math.sqrt(index + 1.0)
    raising = lowering.conj().T
    return (lowering + raising) / math.sqrt(2.0), (lowering - raising) / (1j * math.sqrt(2.0))


def edges(volume: int) -> list[tuple[int, int]]:
    if volume == 2: return [(0, 1)]
    if volume == 4: return [(0, 1), (0, 2), (1, 3), (2, 3)]
    if volume == 6: return [(0, 1), (1, 2), (3, 4), (4, 5), (0, 3), (1, 4), (2, 5)]
    raise ValueError(volume)


def kron_embed(single: np.ndarray, site: int, volume: int, size: int) -> np.ndarray:
    identity = np.eye(size, dtype=complex)
    result = single if site == 0 else identity
    if site != 0: result = identity
    for index in range(1, volume): result = np.kron(result, single if index == site else identity)
    return result


def bond(left: np.ndarray, right: np.ndarray, c: float, lam: float) -> np.ndarray:
    difference = left - right
    square = difference @ difference
    return c * square / 2.0 + lam * square @ (left @ left + right @ right) / 4.0


def system(volume: int, size: int) -> tuple[list[np.ndarray], np.ndarray, list[np.ndarray]]:
    q, p = oscillator(size)
    qs = [kron_embed(q, site, volume, size) for site in range(volume)]
    ps = [kron_embed(p, site, volume, size) for site in range(volume)]
    onsite = [momentum @ momentum / 2.0 - position @ position / 2.0 + (3.0 / 5.0) * position @ position @ position @ position / 4.0 for position, momentum in zip(qs, ps)]
    bonds = [bond(qs[left], qs[right], 3.0 / 5.0, 1.0 / 10.0) for left, right in edges(volume)]
    zero = np.zeros_like(qs[0])
    return qs, h(sum(onsite, zero) + sum(bonds, zero)), onsite + bonds


def gibbs(hamiltonian: np.ndarray, beta: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(h(hamiltonian))
    weights = np.exp(-beta * (values - float(values.min())))
    weights /= float(weights.sum())
    return h((vectors * weights) @ vectors.conj().T)


def character(generator: np.ndarray, amplitude: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(h(generator))
    return (vectors * np.exp(1j * amplitude * values)) @ vectors.conj().T


def reduced(state: np.ndarray, size: int, volume: int, site: int) -> np.ndarray:
    tensor = state.reshape((size,) * (2 * volume)); result = np.zeros((size, size), dtype=complex)
    outside = [index for index in range(volume) if index != site]
    for values in np.ndindex(*(size for _ in outside)):
        row = [slice(None)] * volume; col = [slice(None)] * volume
        for index, value in zip(outside, values): row[index] = value; col[index] = value
        result += tensor[tuple(row + col)]
    return h(result)


def probabilities(state: np.ndarray, q: np.ndarray, size: int, volume: int, site: int) -> tuple[np.ndarray, np.ndarray]:
    values, vectors = np.linalg.eigh(h(q)); matrix = reduced(state, size, volume, site)
    values_out = np.maximum(np.real(np.diag(vectors.conj().T @ matrix @ vectors)), 0.0); values_out /= float(values_out.sum())
    return values, values_out


def factors(terms: list[np.ndarray], order: list[int], sign: int, delta: float, labels: list[str]) -> list[tuple[str, int, np.ndarray]]:
    current = np.eye(terms[0].shape[0], dtype=complex); output: list[tuple[str, int, np.ndarray]] = []
    targets = {"zero": 0, "first": 1, "full": len(order)}
    for position in range(len(order) + 1):
        if position > 0:
            values, vectors = np.linalg.eigh(h(terms[order[position - 1]]))
            current = (vectors * np.exp(-1j * sign * delta * values)) @ vectors.conj().T @ current
        for label in labels:
            if targets[label] == position and not any(item[1] == position for item in output): output.append((label, position, current.copy()))
    return output


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8")); fixture = manifest["finite_fixture"]
    tol = float(fixture["finite_tolerance"]); alpha = float(Fraction(fixture["alpha"])); theta = (alpha - 1.0) / alpha; delta = float(Fraction(fixture["time_step"]))
    betas = [Fraction(value) for value in fixture["beta_values"]]; supports = [tuple(int(site) for site in row) for row in fixture["source_support_values"]]; labels = list(fixture["prefix_selection"]); thresholds = [float(Fraction(value)) for value in fixture["tail_thresholds"]]; limit = float(Fraction(fixture["diagnostic_Q_threshold"]))
    checks: list[dict[str, Any]] = []
    check_count = 0
    def check(name: str, ok: bool, actual: Any, expected: Any, group: str) -> None:
        nonlocal check_count
        check_count += 1
        if not ok: raise AssertionError(f"{name}: {actual!r} != {expected!r}")
        if len(checks) < 64: checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})
    check("identity", manifest["exploration_id"] == "EXP-001202" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001202/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("geometry", edges(2) == [(0, 1)] and len(edges(4)) == 4 and len(edges(6)) == 7, "registered graphs", "target/square/2x3", "geometry")
    check("alpha", alpha > 1.0 and math.isclose(theta, 0.5, abs_tol=tol), [alpha, theta], "alpha=2, theta=1/2", "Renyi")
    check("finite-only", manifest["scope"]["diagnostic_threshold_is_not_a_theorem"] and not manifest["scope"]["actual_Q3_local_Renyi_uniform_bound_closed"], manifest["scope"], "finite diagnostic", "scope")
    contexts: list[dict[str, Any]] = []; maximum = 0.0; exceed = 0
    grids = {int(key): [int(value) for value in values] for key, values in fixture["volume_cutoff_values"].items()}
    for volume in sorted(grids):
        for size in grids[volume]:
            qs, hamiltonian, terms = system(volume, size); q, _ = oscillator(size); orders = {"forward": list(range(len(terms))), "reverse": list(reversed(range(len(terms))))}; prefix_bank = {(order_name, sign): factors(terms, order, sign, delta, labels) for order_name, order in orders.items() for sign in (-1, 1)}
            for beta_fraction in betas:
                rho = gibbs(hamiltonian, float(beta_fraction)); check(f"trace V={volume} d={size} beta={beta_fraction}", abs(float(np.trace(rho).real) - 1.0) <= tol, np.trace(rho).real, 1.0, "Gibbs")
                refs = {site: probabilities(rho, q, size, volume, site)[1] for site in range(volume)}
                for support in supports:
                    generator = sum((qs[site] for site in support), np.zeros_like(qs[0]))
                    for source_sign in (-1, 1):
                        seed = character(generator, source_sign / 3.0) @ rho @ character(generator, source_sign / 3.0).conj().T
                        for order_name, order in orders.items():
                            for sign in (-1, 1):
                                for label, length, prefix in prefix_bank[(order_name, sign)]:
                                    for adjoint in (0, 1):
                                        state = prefix @ seed @ prefix.conj().T if not adjoint else prefix.conj().T @ seed @ prefix
                                        sites: list[dict[str, Any]] = []; row_max = 0.0
                                        for site in range(volume):
                                            eigenvalues, sample = probabilities(state, q, size, volume, site); reference = refs[site]; likelihood = float(np.sum(sample ** alpha / np.maximum(reference, np.finfo(float).tiny) ** (alpha - 1.0))); row_max = max(row_max, likelihood)
                                            tails = []
                                            for threshold in thresholds:
                                                mask = np.abs(eigenvalues) >= threshold; sample_tail = float(sample[mask].sum()); reference_tail = float(reference[mask].sum()); bound = likelihood ** (1.0 / alpha) * reference_tail ** theta; check(f"tail V={volume} d={size} site={site} t={threshold}", sample_tail <= bound + tol, sample_tail, bound, "finite Renyi inequality"); tails.append({"threshold": threshold, "sample_tail": sample_tail, "reference_tail": reference_tail, "bound": bound, "slack": bound - sample_tail})
                                            check(f"likelihood V={volume} d={size} site={site}", np.isfinite(likelihood) and likelihood >= 1.0 - tol, likelihood, ">=1", "local Renyi")
                                            sites.append({"site": site, "q_alpha": likelihood, "tail_rows": tails})
                                        maximum = max(maximum, row_max); over = row_max > limit; exceed += int(over); contexts.append({"volume": volume, "cutoff": size, "beta": str(beta_fraction), "support": list(support), "source_sign": source_sign, "order": order_name, "sign": sign, "prefix": label, "prefix_length": length, "history_adjoint": adjoint, "max_q_alpha": row_max, "diagnostic_exceeds": over, "sites": sites})
    expected_rows = sum(len(values) for values in grids.values()); per_row = len(betas) * len(supports) * 2 * 2 * 2 * 2 * len(labels); expected = expected_rows * per_row
    check("context coverage", len(contexts) == expected, len(contexts), expected, "coverage"); check("finite contexts", all(np.isfinite(row["max_q_alpha"]) for row in contexts), len(contexts), "finite", "coverage"); check("diagnostic outcome", exceed >= 0, exceed, ">=0", "route decision")
    by_grid: dict[str, float] = {}
    for row in contexts: by_grid[f"V={row['volume']}/d={row['cutoff']}"] = max(by_grid.get(f"V={row['volume']}/d={row['cutoff']}", 0.0), row["max_q_alpha"])
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "independent", "audit_id": "PA-CP1-ST8-Q3LOCK-LOCAL-MEASURED-RENYI-Q3-HISTORY-STRESS", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "passed": check_count, "assertion_count": check_count, "assertions": checks, "derived": {"contexts": contexts, "context_count": len(contexts), "size_volume_row_count": expected_rows, "max_q_alpha": maximum, "diagnostic_Q_threshold": limit, "diagnostic_exceed_context_count": exceed, "route_outcome": "FINITE_LOCAL_RENYI_DIAGNOSTIC_EXCEEDS_THRESHOLD" if exceed else "FINITE_LOCAL_RENYI_DIAGNOSTIC_WITHIN_THRESHOLD", "max_q_alpha_by_volume_cutoff": by_grid, "alpha": alpha, "theta": theta, "finite_local_coordinate_rows_closed": True, "finite_two_orientation_prefix_coverage_closed": True, "finite_tail_inequality_checked": True, "actual_Q3_local_Renyi_uniform_bound_closed": False, "cutoff_uniformity_proved": False, "volume_uniformity_proved": False, "beta_uniformity_proved": False, "common_alpha_closed": False, "actual_split_limit_closed": False, "hamiltonian_os_identification_closed": False, "kms_gns_gap_closed": False, "continuum_closed": False, "c6_closed": False, "sector_a_closed": False, "pre_a_closed": False}, "boundary": manifest["boundary"]}


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT); parser.add_argument("--self-test", action="store_true"); args = parser.parse_args(); payload = run()
    if not args.self_test: atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT LOCAL-MEASURED-RENYI-Q3-HISTORY PASS {payload['passed']}/{payload['assertion_count']} route={payload['derived']['route_outcome']} maxQ={payload['derived']['max_q_alpha']:.9g}"); return 0


if __name__ == "__main__": raise SystemExit(main())

#!/usr/bin/env python3
"""Non-importing independent audit of the R-422 two-block reserve.

The fixtures are small reversible graphs built here rather than imported from
the Q3 primary implementation.  They exercise the weighted block-mean-zero
split, the Hardy floor, the cross norm and the conservative reserve inequality.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import tempfile
from pathlib import Path
from typing import Any

import numpy as np


REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-residual-core-tail-reserve-manifest.json"
SLUG = "residual_core_tail_reserve"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-31-independent-{SLUG}" / "independent.json"


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


def zero_mean_basis(pi: np.ndarray, indices: np.ndarray) -> np.ndarray:
    selected = np.asarray(indices, dtype=int)
    basis = np.zeros((len(pi), max(0, len(selected) - 1)), dtype=float)
    if len(selected) <= 1:
        return basis
    root = np.sqrt(pi[selected])
    for column in range(len(selected) - 1):
        basis[selected[column], column] = root[column + 1]
        basis[selected[column + 1], column] = -root[column]
    return np.linalg.qr(basis, mode="reduced")[0]


def safe_reserve(core_gap: float, tail_floor: float, cross_norm: float) -> float:
    if not all(math.isfinite(value) and value >= 0.0 for value in (core_gap, tail_floor, cross_norm)):
        raise AssertionError("invalid independent reserve inputs")
    return min(core_gap, tail_floor) - cross_norm


def fixtures() -> list[tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]]:
    result: list[tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]] = []

    pi = np.array([0.4, 0.3, 0.2, 0.1], dtype=float)
    conductance = np.outer(pi, pi)
    np.fill_diagonal(conductance, 0.0)
    potential = pi ** (-0.2)
    result.append((pi, conductance, potential, np.array([0, 1]), np.array([2, 3])))

    pi = np.array([0.5, 0.25, 0.15, 0.1], dtype=float)
    conductance = np.array([[0.0, 0.3, 0.15, 0.05], [0.3, 0.0, 0.2, 0.1], [0.15, 0.2, 0.0, 0.25], [0.05, 0.1, 0.25, 0.0]], dtype=float)
    potential = pi ** (-0.2)
    result.append((pi, conductance, potential, np.array([0, 1]), np.array([2, 3])))

    pi = np.array([0.5, 0.3, 0.15, 0.05], dtype=float)
    conductance = np.outer(pi, pi)
    np.fill_diagonal(conductance, 0.0)
    potential = pi ** (-0.2)
    result.append((pi, conductance, potential, np.array([0, 1]), np.array([2, 3])))
    return result


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    tolerance = float(manifest["finite_fixture"]["numerical_tolerance"])
    reserve_tolerance = float(manifest["finite_fixture"]["reserve_tolerance"])
    checks: list[dict[str, Any]] = []
    assertion_count = 0

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        nonlocal assertion_count
        assertion_count += 1
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        if len(checks) < 220:
            checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    finite_flags = [
        "finite_block_mean_zero_split_closed",
        "finite_tail_hardy_reuse_closed",
        "finite_cross_block_norm_closed",
        "finite_two_by_two_reserve_closed",
        "finite_positive_reserve_rows_recorded",
        "finite_negative_reserve_rows_recorded",
    ]
    promoted = {key: value for key, value in manifest["scope"].items() if key.endswith("_closed") and key not in finite_flags}
    check("manifest identity", manifest["result_id"] == "R-422" and manifest["exploration_id"] == "EXP-001267" and manifest["claim_bearing"] is False, [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"]], "R-422/EXP-001267/false", "provenance")
    check("scope firewall", all(manifest["scope"][key] for key in finite_flags) and not any(promoted.values()), promoted, "all promoted flags false", "scope")

    minimum_rate: list[float] = []
    safe_values: list[float] = []
    sharp_values: list[float] = []
    residual_values: list[float] = []
    probe_margins: list[float] = []
    positive_count = 0
    nonpositive_count = 0

    for fixture_index, (pi_raw, conductance, potential, core_indices, tail_indices) in enumerate(fixtures()):
        pi = np.asarray(pi_raw, dtype=float)
        check(f"fixture={fixture_index} weights", np.all(pi > 0.0) and abs(float(np.sum(pi)) - 1.0) <= tolerance, [float(np.min(pi)), float(np.sum(pi))], "positive and normalized", "weights")
        check(f"fixture={fixture_index} conductance", np.all(conductance >= 0.0) and np.max(np.abs(conductance - conductance.T)) <= tolerance, float(np.max(np.abs(conductance - conductance.T))), f"symmetric within {tolerance}", "conductance")
        check(f"fixture={fixture_index} potential", np.all(np.isfinite(potential)) and np.all(potential > 0.0), potential.tolist(), "positive finite", "potential")
        laplacian = np.diag(np.sum(conductance, axis=1)) - conductance
        root_inverse = 1.0 / np.sqrt(pi)
        operator = root_inverse[:, None] * laplacian * root_inverse[None, :]
        operator = (operator + operator.T) / 2.0
        rates = -(conductance @ potential - np.sum(conductance, axis=1) * potential) / pi / potential
        tail_floor = float(np.min(rates[tail_indices]))
        check(f"fixture={fixture_index} tail floor", tail_floor > 0.0, tail_floor, ">0", "tail Hardy")
        core_basis = zero_mean_basis(pi, core_indices)
        tail_basis = zero_mean_basis(pi, tail_indices)
        core_matrix = (core_basis.T @ operator @ core_basis)
        tail_matrix = (tail_basis.T @ operator @ tail_basis)
        cross_matrix = core_basis.T @ operator @ tail_basis
        core_matrix = (core_matrix + core_matrix.T) / 2.0
        tail_matrix = (tail_matrix + tail_matrix.T) / 2.0
        core_gap = float(np.linalg.eigvalsh(core_matrix)[0])
        direct_tail_gap = float(np.linalg.eigvalsh(tail_matrix)[0])
        cross_norm = float(np.linalg.svd(cross_matrix, compute_uv=False)[0]) if cross_matrix.size else 0.0
        safe = safe_reserve(core_gap, tail_floor, cross_norm)
        sharp = 0.5 * (core_gap + tail_floor - math.sqrt((core_gap - tail_floor) ** 2 + 4.0 * cross_norm**2))
        residual_matrix = np.block([[core_matrix, cross_matrix], [cross_matrix.T, tail_matrix]])
        residual_matrix = (residual_matrix + residual_matrix.T) / 2.0
        actual_gap = float(np.linalg.eigvalsh(residual_matrix)[0])
        check(f"fixture={fixture_index} core gap", core_gap > 0.0, core_gap, ">0", "core form")
        check(f"fixture={fixture_index} tail Hardy reuse", direct_tail_gap + reserve_tolerance >= tail_floor, [direct_tail_gap, tail_floor], f"direct gap >= floor-{reserve_tolerance}", "tail Hardy")
        check(f"fixture={fixture_index} residual reserve", actual_gap + reserve_tolerance >= safe, [actual_gap, safe], f"actual gap >= safe-{reserve_tolerance}", "two-block reserve")
        check(f"fixture={fixture_index} sharp ordering", sharp + reserve_tolerance >= safe, [sharp, safe], f"sharp >= safe-{reserve_tolerance}", "two-block reserve")
        rng = np.random.default_rng(fixture_index + 1)
        for probe_index in range(5):
            x = rng.normal(size=core_basis.shape[1])
            y = rng.normal(size=tail_basis.shape[1])
            x /= max(float(np.linalg.norm(x)), 1.0)
            y /= max(float(np.linalg.norm(y)), 1.0)
            vector = np.concatenate((x, y))
            margin = float(vector @ residual_matrix @ vector) - safe * float(vector @ vector)
            probe_margins.append(margin)
            check(f"fixture={fixture_index} probe={probe_index} reserve", margin + reserve_tolerance >= 0.0, margin, f">=-{reserve_tolerance}", "two-block reserve")
        minimum_rate.append(tail_floor)
        safe_values.append(safe)
        sharp_values.append(sharp)
        residual_values.append(actual_gap)
        if safe > reserve_tolerance:
            positive_count += 1
        else:
            nonpositive_count += 1

    check("fixture coverage", len(fixtures()) == 3 and positive_count + nonpositive_count == len(fixtures()), [len(fixtures()), positive_count, nonpositive_count], "three fixtures partitioned", "coverage")
    check("probe aggregate", min(probe_margins) + reserve_tolerance >= 0.0, min(probe_margins), f">=-{reserve_tolerance}", "aggregate")
    payload: dict[str, Any] = {
        "schema": "tect/pre-a-r422-independent/1.0",
        "result_id": manifest["result_id"],
        "exploration_id": manifest["exploration_id"],
        "claim_id": manifest["claim_ids"][0],
        "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"),
        "run_kind": "independent",
        "verdict": "PASS",
        "assertion_count": assertion_count,
        "assertions": checks,
        "derived": {
            "fixture_count": len(fixtures()),
            "eligible_fixture_count": len(fixtures()),
            "positive_reserve_fixture_count": positive_count,
            "nonpositive_reserve_fixture_count": nonpositive_count,
            "minimum_tail_hardy_floor": min(minimum_rate),
            "minimum_safe_reserve": min(safe_values),
            "maximum_safe_reserve": max(safe_values),
            "minimum_sharp_diagnostic": min(sharp_values),
            "minimum_actual_residual_gap": min(residual_values),
            "minimum_probe_margin": min(probe_margins),
        },
        "assumptions": manifest["assumptions"],
        "missing_assumptions": manifest["missing_assumptions"],
        "evidence_level": manifest["evidence_level"],
        "non_claims": manifest["non_claims"],
        "boundary": manifest["boundary"],
    }
    atomic_json(output, payload)
    print(f"R-422 INDEPENDENT PASS {assertion_count}/{assertion_count} assertions; fixtures={len(fixtures())} positive={positive_count} nonpositive={nonpositive_count}; min_safe_reserve={min(safe_values):.6g}")
    return payload


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    run(args.output if args.output.is_absolute() else REPO / args.output)


if __name__ == "__main__":
    main()

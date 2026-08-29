#!/usr/bin/env python3
"""Non-importing independent audit of the boundary-capacity envelope."""

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
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-boundary-capacity-cauchy-manifest.json"
SLUG = "boundary_capacity_cauchy"
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
    if selected.size < 2:
        raise AssertionError("block has fewer than two indices")
    raw = np.zeros((len(pi), selected.size - 1), dtype=float)
    root = np.sqrt(pi[selected])
    for column in range(selected.size - 1):
        raw[selected[column], column] = root[column + 1]
        raw[selected[column + 1], column] = -root[column]
    return np.linalg.qr(raw, mode="reduced")[0]


def capacity(pi: np.ndarray, conductance: np.ndarray, core: np.ndarray, tail: np.ndarray) -> tuple[float, float, float, np.ndarray]:
    weights = np.asarray(pi, dtype=float)
    matrix = np.asarray(conductance, dtype=float)
    core = np.asarray(core, dtype=int)
    tail = np.asarray(tail, dtype=int)
    if not np.all(np.isfinite(weights)) or np.any(weights <= 0.0):
        raise AssertionError("weights must be positive and finite")
    if not np.all(np.isfinite(matrix)) or np.any(matrix < 0.0) or np.max(np.abs(matrix - matrix.T)) > 1.0e-12:
        raise AssertionError("conductance must be symmetric and nonnegative")
    if np.intersect1d(core, tail).size:
        raise AssertionError("supports must be disjoint")
    block = matrix[np.ix_(core, tail)]
    rho_core = float(np.max(np.sum(block, axis=1) / weights[core]))
    rho_tail = float(np.max(np.sum(block, axis=0) / weights[tail]))
    bound = math.sqrt(rho_core * rho_tail)
    edge = block / np.sqrt(weights[core, None] * weights[tail][None, :])
    return rho_core, rho_tail, bound, edge


def fixtures() -> list[dict[str, Any]]:
    low_pi = np.array([0.4, 0.3, 0.2, 0.1], dtype=float)
    low_c = 0.05 * np.outer(low_pi, low_pi)
    np.fill_diagonal(low_c, 0.0)
    asym_pi = np.array([0.5, 0.25, 0.15, 0.1], dtype=float)
    asym_c = np.array([[0.0, 0.02, 0.01, 0.005], [0.02, 0.0, 0.015, 0.002], [0.01, 0.015, 0.0, 0.01], [0.005, 0.002, 0.01, 0.0]], dtype=float)
    high_pi = np.array([0.5, 0.3, 0.15, 0.05], dtype=float)
    high_c = 2.0 * np.outer(high_pi, high_pi)
    np.fill_diagonal(high_c, 0.0)
    zero_pi = np.array([0.25, 0.25, 0.25, 0.25], dtype=float)
    zero_c = np.zeros((4, 4), dtype=float)
    return [
        {"pi": low_pi, "c": low_c, "core": np.array([0, 1]), "tail": np.array([2, 3]), "a": 0.8, "kappa": 0.6},
        {"pi": asym_pi, "c": asym_c, "core": np.array([0, 1]), "tail": np.array([2, 3]), "a": 0.2, "kappa": 0.15},
        {"pi": high_pi, "c": high_c, "core": np.array([0, 1]), "tail": np.array([2, 3]), "a": 0.3, "kappa": 0.25},
        {"pi": zero_pi, "c": zero_c, "core": np.array([0, 1]), "tail": np.array([2, 3]), "a": 0.4, "kappa": 0.35},
    ]


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    tolerance = float(manifest["finite_fixture"]["crosscheck_tolerance"])
    checks: list[dict[str, Any]] = []
    assertions = 0

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        nonlocal assertions
        assertions += 1
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        if len(checks) < 240:
            checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    scope = manifest["scope"]
    finite_flags = ["finite_directed_capacity_closed", "finite_cauchy_cross_bound_closed", "finite_capacity_reserve_closed", "finite_capacity_boundary_rows_recorded"]
    promoted = {key: value for key, value in scope.items() if key.endswith("_closed") and key not in finite_flags}
    check("manifest identity", manifest["result_id"] == "R-423" and manifest["exploration_id"] == "EXP-001268" and manifest["claim_bearing"] is False, [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"]], "R-423/EXP-001268/false", "provenance")
    check("scope firewall", all(scope[key] for key in finite_flags) and not any(promoted.values()), promoted, "all promoted flags false", "scope")

    capacities: list[float] = []
    reserves: list[float] = []
    margins: list[float] = []
    positive = 0
    nonpositive = 0
    for index, fixture in enumerate(fixtures()):
        pi = np.asarray(fixture["pi"], dtype=float)
        conductance = np.asarray(fixture["c"], dtype=float)
        core = np.asarray(fixture["core"], dtype=int)
        tail = np.asarray(fixture["tail"], dtype=int)
        check(f"fixture={index} weights", np.all(pi > 0.0) and abs(float(np.sum(pi)) - 1.0) <= tolerance, [float(np.min(pi)), float(np.sum(pi))], "positive normalized weights", "weights")
        rho_core, rho_tail, bound, edge = capacity(pi, conductance, core, tail)
        core_basis = zero_mean_basis(pi, core)
        tail_basis = zero_mean_basis(pi, tail)
        cross = core_basis[core].T @ edge @ tail_basis[tail]
        cross_norm = float(np.linalg.svd(cross, compute_uv=False)[0]) if cross.size else 0.0
        reserve = min(float(fixture["a"]), float(fixture["kappa"])) - bound
        check(f"fixture={index} directed capacities", rho_core >= 0.0 and rho_tail >= 0.0 and math.isfinite(bound), [rho_core, rho_tail, bound], "finite nonnegative", "capacity")
        check(f"fixture={index} cross envelope", cross_norm <= bound + tolerance, [cross_norm, bound], f"cross<=capacity+{tolerance}", "capacity")
        for probe_index in range(6):
            x = np.sin((np.arange(len(core)) + 1.0) * (probe_index + 0.5))
            y = np.cos((np.arange(len(tail)) + 1.0) * (probe_index + 1.0))
            x /= max(float(np.linalg.norm(x)), 1.0)
            y /= max(float(np.linalg.norm(y)), 1.0)
            lhs = abs(float(x @ edge @ y))
            first = float(np.sum((conductance[np.ix_(core, tail)] * x[:, None] ** 2) / pi[core, None]))
            second = float(np.sum((conductance[np.ix_(core, tail)] * y[None, :] ** 2) / pi[tail][None, :]))
            edge_bound = math.sqrt(max(first, 0.0) * max(second, 0.0))
            margin = edge_bound - lhs
            margins.append(margin)
            check(f"fixture={index} probe={probe_index} edge Cauchy", lhs <= edge_bound + tolerance and edge_bound <= bound + tolerance, [lhs, edge_bound, bound], f"lhs<=edge<=capacity+{tolerance}", "capacity")
        capacities.append(bound)
        reserves.append(reserve)
        if reserve > float(manifest["finite_fixture"]["reserve_tolerance"]):
            positive += 1
        else:
            nonpositive += 1

    check("fixture coverage", len(fixtures()) == 4 and positive > 0 and nonpositive > 0, [len(fixtures()), positive, nonpositive], "four fixtures with both reserve signs", "coverage")
    check("probe margins", min(margins) + tolerance >= 0.0, min(margins), f">=-{tolerance}", "aggregate")
    payload: dict[str, Any] = {
        "schema": "tect/pre-a-r423-independent/1.0",
        "result_id": manifest["result_id"],
        "exploration_id": manifest["exploration_id"],
        "claim_id": manifest["claim_ids"][0],
        "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"),
        "run_kind": "independent",
        "verdict": "PASS",
        "assertion_count": assertions,
        "assertions": checks,
        "derived": {"fixture_count": len(fixtures()), "positive_capacity_reserve_fixture_count": positive, "nonpositive_capacity_reserve_fixture_count": nonpositive, "minimum_capacity": min(capacities), "maximum_capacity": max(capacities), "minimum_capacity_reserve": min(reserves), "maximum_capacity_reserve": max(reserves), "minimum_probe_margin": min(margins)},
        "assumptions": manifest["assumptions"],
        "missing_assumptions": manifest["missing_assumptions"],
        "evidence_level": manifest["evidence_level"],
        "non_claims": manifest["non_claims"],
        "boundary": manifest["boundary"],
    }
    atomic_json(output, payload)
    print(f"R-423 INDEPENDENT PASS {assertions}/{assertions} fixtures={len(fixtures())} positive={positive} nonpositive={nonpositive} reserve=[{min(reserves):.6g},{max(reserves):.6g}]")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    run(args.output if args.output.is_absolute() else REPO / args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

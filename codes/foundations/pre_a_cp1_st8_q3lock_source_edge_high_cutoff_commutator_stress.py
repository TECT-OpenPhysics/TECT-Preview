#!/usr/bin/env python3
"""Primary finite Q3 source-edge high-cutoff commutator stress (EXP-001198)."""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

import numpy as np

REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_source_edge_high_cutoff_commutator_stress"
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-source-edge-high-cutoff-commutator-stress-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-29-primary-{SLUG}" / "primary.json"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pre_a_cp1_st8_q3lock_weighted_triple_commutator_volume_stress as q3  # noqa: E402


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True, default=float)
            stream.write("\n")
            stream.flush(); os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary): os.unlink(temporary)


def hermitian(matrix: np.ndarray) -> np.ndarray:
    return (matrix + matrix.conj().T) / 2.0


def shifted(base: np.ndarray) -> tuple[np.ndarray, float]:
    value = hermitian(base)
    minimum = float(np.min(np.linalg.eigvalsh(value)))
    return value + (1.0 - minimum) * np.eye(value.shape[0], dtype=complex), minimum


def spectral_inverse(weight: np.ndarray) -> tuple[np.ndarray, np.ndarray, float]:
    values, vectors = np.linalg.eigh(hermitian(weight))
    floor = float(np.min(values))
    inverse = (vectors * np.reciprocal(values)) @ vectors.conj().T
    inverse_sqrt = (vectors * np.reciprocal(np.sqrt(values))) @ vectors.conj().T
    return inverse, inverse_sqrt, floor


def operator_norm(matrix: np.ndarray) -> float:
    return float(np.linalg.svd(matrix, compute_uv=False)[0])


def vector_norm(vector: np.ndarray) -> float:
    return float(np.linalg.norm(vector))


def basis_vector(dimension: int, index: tuple[int, int]) -> np.ndarray:
    vector = np.zeros(dimension * dimension, dtype=complex)
    vector[index[0] * dimension + index[1]] = 1.0
    return vector


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition: raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001198" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001198/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("scope firewall", scope["finite_high_cutoff_rows_closed"] and scope["explicit_high_core_lower_bound_rows_closed"] and scope["cutoff_growth_diagnostic_closed"] and not scope["uniform_commutator_bound_closed"] and not scope["cutoff_removal_closed"], scope, "finite route stress only", "scope")

    tolerance = float(fixture["tolerance"])
    slope = float(fixture["core_linear_slope_threshold"])
    offset = int(fixture["core_linear_offset"])
    dimensions = [int(value) for value in fixture["oscillator_dimensions"]]
    high_rows: list[dict[str, Any]] = []
    for dimension in dimensions:
        q_ops, hamiltonian, _local_hamiltonian, bonds = q3.build_volume(int(fixture["volume"]), dimension, fixture)
        r_value, g_value = float(fixture["r"]), float(fixture["g"])
        onsite_potential = sum((r_value * (q @ q) / 2.0 + g_value * (q @ q @ q @ q) / 4.0 for q in q_ops), np.zeros_like(hamiltonian))
        source_base = onsite_potential + bonds[(0, 1)]
        full_weight, full_floor = shifted(hamiltonian)
        source_weight, source_floor = shifted(source_base)
        full_inverse, full_inverse_sqrt, full_inverse_floor = spectral_inverse(full_weight)
        commutator = full_weight @ source_weight - source_weight @ full_weight
        commutator_operator = commutator @ full_inverse
        global_commutator = operator_norm(commutator_operator)
        global_graph = operator_norm(source_weight @ full_inverse)
        form_constant = float(np.max(np.linalg.eigvalsh(hermitian(full_inverse_sqrt @ source_weight @ full_inverse_sqrt))))
        check(f"d={dimension} full positive", full_inverse_floor >= 1.0 - tolerance, full_inverse_floor, ">=1", "full")
        check(f"d={dimension} source positive", float(np.min(np.linalg.eigvalsh(source_weight))) >= 1.0 - tolerance, source_floor, ">=1", "source")
        check(f"d={dimension} finite constants", all(np.isfinite(value) and value >= 0.0 for value in (global_graph, form_constant, global_commutator)), [global_graph, form_constant, global_commutator], "finite nonnegative", "constants")
        vector_rows: list[dict[str, Any]] = []
        for label in fixture["high_core_indices"]:
            index = (dimension - 1, dimension - 1) if label == "diagonal_top" else (dimension - 1, 0)
            vector = basis_vector(dimension, index)
            denominator = vector_norm(full_weight @ vector)
            ratio = vector_norm(commutator @ vector) / denominator
            check(f"d={dimension} {label} global domination", ratio <= global_commutator * (1.0 + tolerance) + tolerance, ratio, f"<={global_commutator}", "core")
            check(f"d={dimension} {label} finite", np.isfinite(ratio) and ratio >= 0.0, ratio, "finite nonnegative", "core")
            vector_rows.append({"label": label, "index": list(index), "ratio": ratio, "scaled_ratio": ratio / max(float(dimension - offset), 1.0)})
        diagonal = next(row for row in vector_rows if row["label"] == "diagonal_top")
        lower_bound = slope * float(dimension - offset)
        check(f"d={dimension} diagonal linear lower bound", diagonal["ratio"] + tolerance >= lower_bound, diagonal["ratio"], f">={lower_bound}", "cutoff lower bound")
        high_rows.append({"dimension": dimension, "global_graph_constant": global_graph, "form_constant": form_constant, "global_commutator_constant": global_commutator, "vectors": vector_rows, "diagonal_lower_bound": lower_bound, "full_floor": full_floor, "source_floor": source_floor})

    check("dimension coverage", [row["dimension"] for row in high_rows] == dimensions, [row["dimension"] for row in high_rows], dimensions, "coverage")
    check("vector coverage", all(len(row["vectors"]) == len(fixture["high_core_indices"]) for row in high_rows), [len(row["vectors"]) for row in high_rows], len(fixture["high_core_indices"]), "coverage")
    first = next(row for row in high_rows if row["dimension"] == dimensions[0])
    last = next(row for row in high_rows if row["dimension"] == dimensions[-1])
    first_ratio = next(row["ratio"] for row in first["vectors"] if row["label"] == "diagonal_top")
    last_ratio = next(row["ratio"] for row in last["vectors"] if row["label"] == "diagonal_top")
    growth = last_ratio / max(first_ratio, np.finfo(float).tiny)
    check("high-core growth", growth >= 1.0, growth, ">=1", "cutoff diagnostic")
    return {
        "schema": "tect/foundation-audit/1.0", "run_kind": "primary", "audit_id": "PA-CP1-ST8-Q3LOCK-SOURCE-EDGE-HIGH-CUTOFF-COMMUTATOR-STRESS", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "passed": len(checks), "assertion_count": len(checks), "assertions": checks,
        "derived": {"dimension_count": len(high_rows), "vector_row_count": sum(len(row["vectors"]) for row in high_rows), "high_cutoff_rows": high_rows, "max_global_graph_constant": max(row["global_graph_constant"] for row in high_rows), "max_form_constant": max(row["form_constant"] for row in high_rows), "max_global_commutator_constant": max(row["global_commutator_constant"] for row in high_rows), "diagonal_first_ratio": first_ratio, "diagonal_last_ratio": last_ratio, "diagonal_growth_ratio": growth, "finite_high_cutoff_rows_closed": True, "explicit_high_core_lower_bound_rows_closed": True, "cutoff_growth_diagnostic_closed": True, "uniform_commutator_bound_closed": False, "cutoff_removal_closed": False, "unbounded_common_core_closed": False, "common_alpha_closed": False, "qft_promoted": False}, "boundary": scope,
    }


def main() -> int:
    parser = argparse.ArgumentParser(); parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT); parser.add_argument("--self-test", action="store_true"); args = parser.parse_args(); payload = run()
    if not args.self_test: atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY SOURCE-EDGE-HIGH-CUTOFF-COMMUTATOR PASS {payload['passed']}/{payload['assertion_count']} dimensions={payload['derived']['dimension_count']}")
    return 0


if __name__ == "__main__": raise SystemExit(main())
#!/usr/bin/env python3
"""Primary exact finite-oscillator CCR-boundary audit for EXP-001094."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path
from typing import Any

import numpy as np


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_truncated_ccr_boundary"
MANIFEST = REPO / f"strategy/{SLUG}_manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-25-primary-{SLUG}" / "primary.json"


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True, default=float)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def oscillator(n: int) -> tuple[np.ndarray, np.ndarray]:
    lowering = np.zeros((n, n), dtype=complex)
    for index in range(1, n):
        lowering[index - 1, index] = np.sqrt(float(index))
    raising = lowering.conj().T
    return (lowering + raising) / np.sqrt(2.0), (lowering - raising) / (1j * np.sqrt(2.0))


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    tolerance = float(fixture["tolerance"])
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001094" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001094/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("scope firewall", scope["exact_truncated_ccr_identity_closed"] and scope["operator_norm_defect_closed"] and scope["vector_tail_condition_derived"] and not scope["actual_unbounded_q3_domain_transfer_closed"], scope, "finite exact identity and open transfer", "scope")

    n_values = [int(value) for value in fixture["n_values"]]
    rows_data: list[dict[str, Any]] = []
    for n in n_values:
        q, p = oscillator(n)
        identity = np.eye(n, dtype=complex)
        top = np.zeros((n, n), dtype=complex)
        top[-1, -1] = 1.0
        commutator = q @ p - p @ q
        expected = 1j * (identity - float(n) * top)
        defect = commutator - 1j * identity
        expected_defect = -1j * float(n) * top
        formula_error = float(np.linalg.svd(commutator - expected, compute_uv=False)[0])
        defect_error = float(np.linalg.svd(defect - expected_defect, compute_uv=False)[0])
        defect_norm = float(np.linalg.svd(defect, compute_uv=False)[0])
        top_action = float(np.linalg.norm(defect @ np.eye(n, dtype=complex)[:, -1]))
        ground_action = float(np.linalg.norm(defect @ np.eye(n, dtype=complex)[:, 0]))
        numerical_rank = int(np.linalg.matrix_rank(defect, tol=tolerance))
        check(f"n={n} commutator formula", formula_error <= tolerance, formula_error, f"<={tolerance}", "exact CCR boundary")
        check(f"n={n} defect formula", defect_error <= tolerance, defect_error, f"<={tolerance}", "exact CCR boundary")
        check(f"n={n} defect norm", abs(defect_norm - float(n)) <= tolerance, defect_norm, n, "operator norm")
        check(f"n={n} top action", abs(top_action - float(n)) <= tolerance, top_action, n, "top boundary")
        check(f"n={n} ground action", ground_action <= tolerance, ground_action, f"<={tolerance}", "top boundary")
        check(f"n={n} defect rank", numerical_rank == 1, numerical_rank, 1, "top boundary")
        rows_data.append({"n": n, "formula_error": formula_error, "defect_error": defect_error, "defect_operator_norm": defect_norm, "top_action_norm": top_action, "ground_action_norm": ground_action, "rank": numerical_rank, "exact_defect_coefficient": -n})

    amplitudes = []
    for power in [int(value) for value in fixture["powers"]]:
        values = [{"n": n, "amplitude": float(n ** (-power)), "n_times_amplitude": float(n ** (1 - power))} for n in n_values]
        amplitudes.append({"power": power, "rows": values})
        check(f"power={power} tail arithmetic", all(np.isfinite(item["n_times_amplitude"]) for item in values), values, "finite", "domain condition")
    check("n sequence", [row["n"] for row in rows_data] == n_values, [row["n"] for row in rows_data], n_values, "fixture")

    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": "PA-CP1-ST8-Q3LOCK-TRUNCATED-CCR-BOUNDARY",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": len(rows),
        "assertion_count": len(rows),
        "assertions": rows,
        "derived": {
            "rows": rows_data,
            "tail_amplitude_rows": amplitudes,
            "exact_truncated_ccr_identity_closed": True,
            "operator_norm_defect_closed": True,
            "vector_tail_condition_derived": True,
            "finite_matrix_ccr_uniformity_closed": False,
            "actual_unbounded_q3_domain_transfer_closed": False,
            "source_volume_uniform_modular_history_closed": False,
            "common_alpha_closed": False,
        },
        "boundary": manifest["boundary"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY TRUNCATED-CCR-BOUNDARY PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

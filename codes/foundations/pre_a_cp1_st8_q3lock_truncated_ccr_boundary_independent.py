#!/usr/bin/env python3
"""Independent finite-oscillator CCR-boundary audit for EXP-001094."""

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
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-25-independent-{SLUG}" / "independent.json"


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


def build_qp(n: int) -> tuple[np.ndarray, np.ndarray]:
    creation = np.zeros((n, n), dtype=complex)
    for row in range(1, n):
        creation[row, row - 1] = np.sqrt(float(row))
    annihilation = creation.conj().T
    coordinate = (creation + annihilation) / np.sqrt(2.0)
    momentum = (annihilation - creation) / (1j * np.sqrt(2.0))
    return coordinate, momentum


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    tolerance = float(fixture["tolerance"])
    checks: list[dict[str, Any]] = []

    def require(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    require("independent identity", manifest["exploration_id"] == "EXP-001094" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001094/T-054", "provenance")
    require("independent nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    require("independent scope", scope["exact_truncated_ccr_identity_closed"] and scope["operator_norm_defect_closed"] and not scope["actual_unbounded_q3_domain_transfer_closed"], scope, "exact finite/open transfer", "scope")

    rows: list[dict[str, Any]] = []
    for n in [int(value) for value in fixture["n_values"]]:
        coordinate, momentum = build_qp(n)
        eye = np.eye(n, dtype=complex)
        projector = np.zeros((n, n), dtype=complex)
        projector[n - 1, n - 1] = 1.0
        commutator = coordinate @ momentum - momentum @ coordinate
        residual = commutator - 1j * eye
        expected_residual = -1j * float(n) * projector
        formula_error = float(np.max(np.abs(residual - expected_residual)))
        norm_value = float(np.linalg.norm(residual, ord=2))
        top_vector = np.zeros(n, dtype=complex); top_vector[n - 1] = 1.0
        bottom_vector = np.zeros(n, dtype=complex); bottom_vector[0] = 1.0
        top_action = float(np.linalg.norm(residual @ top_vector))
        bottom_action = float(np.linalg.norm(residual @ bottom_vector))
        rank = int(np.sum(np.linalg.svd(residual, compute_uv=False) > tolerance))
        require(f"n={n} exact residual", formula_error <= tolerance, formula_error, f"<={tolerance}", "exact CCR boundary")
        require(f"n={n} operator norm", abs(norm_value - float(n)) <= tolerance, norm_value, n, "operator norm")
        require(f"n={n} top vector", abs(top_action - float(n)) <= tolerance, top_action, n, "top boundary")
        require(f"n={n} bottom vector", bottom_action <= tolerance, bottom_action, f"<={tolerance}", "top boundary")
        require(f"n={n} rank one", rank == 1, rank, 1, "top boundary")
        rows.append({"n": n, "formula_error": formula_error, "operator_norm": norm_value, "top_action": top_action, "bottom_action": bottom_action, "rank": rank, "exact_defect_coefficient": -n})

    scaled_rows = []
    for power in [int(value) for value in fixture["powers"]]:
        values = []
        for n in [int(value) for value in fixture["n_values"]]:
            amplitude = 1.0 / (float(n) ** power)
            values.append({"n": n, "amplitude": amplitude, "scaled": float(n) * amplitude})
        require(f"power={power} scaled finite", all(np.isfinite(item["scaled"]) for item in values), values, "finite", "domain condition")
        scaled_rows.append({"power": power, "rows": values})

    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "audit_id": "PA-CP1-ST8-Q3LOCK-TRUNCATED-CCR-BOUNDARY",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": len(checks),
        "assertion_count": len(checks),
        "assertions": checks,
        "derived": {
            "rows": rows,
            "tail_amplitude_rows": scaled_rows,
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
    print(f"INDEPENDENT TRUNCATED-CCR-BOUNDARY PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

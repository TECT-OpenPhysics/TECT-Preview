#!/usr/bin/env python3
"""Independent dense-matrix audit for EXP-001105.

The construction intentionally uses a separate ladder implementation and
explicit repeated multiplication rather than importing the primary lane.
"""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from pathlib import Path
from typing import Any

import numpy as np

REPO = Path(__file__).resolve().parents[2]
SLUG = "pre_a_cp1_st8_q3lock_harmonic_compression_boundary_leakage"
MANIFEST = REPO / f"strategy/{SLUG}_manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-25-independent-{SLUG}" / "independent.json"


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


def ladder(dimension: int) -> tuple[np.ndarray, np.ndarray]:
    lower = np.zeros((dimension, dimension), dtype=complex)
    for row in range(1, dimension):
        lower[row - 1, row] = np.sqrt(float(row))
    upper = lower.T.conj()
    return (lower + upper) / np.sqrt(2.0), (lower - upper) / (1j * np.sqrt(2.0))


def repeated_power(matrix: np.ndarray, degree: int) -> np.ndarray:
    result = np.eye(matrix.shape[0], dtype=complex)
    for _ in range(degree):
        result = result @ matrix
    return result


def window(n: int, degree: int) -> np.ndarray:
    result = np.zeros((n, n), dtype=complex)
    first = max(0, n - degree)
    for index in range(first, n):
        result[index, index] = 1.0
    return result


def defect(n: int, degree: int, operator: np.ndarray) -> np.ndarray:
    compressed = operator[:n, :n]
    return repeated_power(operator, degree)[:n, :n] - repeated_power(compressed, degree)


def envelope(ambient_dimension: int, degree: int) -> float:
    return 2.0 * float(ambient_dimension) ** (0.5 * degree)


def onsite(n: int, ambient: int, parameters: dict[str, float]) -> tuple[np.ndarray, float]:
    coordinate, momentum = ladder(ambient)
    q = coordinate[:n, :n]
    p = momentum[:n, :n]
    chi = float(parameters["chi"])
    r = float(parameters["r"])
    g = float(parameters["g"])
    exact = (momentum @ momentum / (2.0 * chi) + r * (coordinate @ coordinate) / 2.0 + g * repeated_power(coordinate, 4) / 4.0)[:n, :n]
    compressed = p @ p / (2.0 * chi) + r * (q @ q) / 2.0 + g * repeated_power(q, 4) / 4.0
    bound = abs(1.0 / (2.0 * chi)) * envelope(ambient, 2) + abs(r) / 2.0 * envelope(ambient, 2) + abs(g) / 4.0 * envelope(ambient, 4)
    return exact - compressed, bound


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    scope = manifest["scope"]
    tolerance = float(fixture["tolerance"])
    moment_cap = float(fixture["moment_cap"])
    max_degree = max(int(value) for value in fixture["degree_values"])
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001105" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001105/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    check("degree set", fixture["degree_values"] == [2, 4], fixture["degree_values"], "[2,4]", "degree")
    check("scope firewall", scope["finite_path_support_closed"] and scope["conditional_state_weighted_boundary_bound_closed"] and not scope["q3_gibbs_weighted_boundary_uniformity_closed"], scope, "finite conditional only", "scope")

    degree_rows: list[dict[str, Any]] = []
    n_rows: list[dict[str, Any]] = []
    for n in [int(value) for value in fixture["n_values"]]:
        ambient = n + max_degree + 1
        coordinate, momentum = ladder(ambient)
        row: dict[str, Any] = {"n": n, "ambient_dimension": ambient, "degrees": []}
        for degree in [int(value) for value in fixture["degree_values"]]:
            cut = window(n, degree)
            defect_rows: dict[str, Any] = {}
            for label, operator in (("q", coordinate), ("p", momentum)):
                difference = defect(n, degree, operator)
                support_residual = float(np.linalg.norm(difference - cut @ difference @ cut, ord=2))
                actual_norm = float(np.linalg.norm(difference, ord=2))
                bound = envelope(ambient, degree)
                check(f"n={n} d={degree} {label} support", support_residual <= tolerance, support_residual, f"<={tolerance}", "path support")
                check(f"n={n} d={degree} {label} norm envelope", actual_norm <= bound * (1.0 + tolerance), actual_norm, f"<={bound * (1.0 + tolerance)}", "norm envelope")
                defect_rows[label] = {"support_residual": support_residual, "norm": actual_norm, "derived_envelope": bound}
            degree_row = {"degree": degree, "defects": defect_rows}
            degree_row["conditional_state_weighted_bound"] = bound * moment_cap / float(n - degree) ** 5
            check(f"n={n} d={degree} conditional denominator", n > degree, n - degree, ">0", "state envelope")
            degree_rows.append({"n": n, **degree_row})
            row["degrees"].append(degree_row)

        onsite_difference, onsite_bound = onsite(n, ambient, fixture["parameters"])
        onsite_cut = window(n, max_degree)
        support_residual = float(np.linalg.norm(onsite_difference - onsite_cut @ onsite_difference @ onsite_cut, ord=2))
        actual_norm = float(np.linalg.norm(onsite_difference, ord=2))
        check(f"n={n} onsite support", support_residual <= tolerance, support_residual, f"<={tolerance}", "onsite path support")
        check(f"n={n} onsite norm envelope", actual_norm <= onsite_bound * (1.0 + tolerance), actual_norm, f"<={onsite_bound * (1.0 + tolerance)}", "onsite norm envelope")
        check(f"n={n} onsite conditional denominator", n > max_degree, n, f">{max_degree}", "state envelope")
        row["onsite"] = {"support_residual": support_residual, "norm": actual_norm, "derived_envelope": onsite_bound, "conditional_state_weighted_bound": onsite_bound * moment_cap / float(n - max_degree) ** 5}
        n_rows.append(row)

    check("cutoff sequence", [row["n"] for row in n_rows] == [int(value) for value in fixture["n_values"]], [row["n"] for row in n_rows], fixture["n_values"], "cutoff")
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "audit_id": "PA-CP1-ST8-Q3LOCK-HARMONIC-COMPRESSION-BOUNDARY-LEAKAGE",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": len(rows),
        "assertion_count": len(rows),
        "assertions": rows,
        "derived": {
            "n_rows": n_rows,
            "degree_rows": degree_rows,
            "finite_path_support_closed": True,
            "finite_norm_envelope_closed": True,
            "conditional_state_weighted_boundary_bound_closed": True,
            "operator_norm_convergence_closed": False,
            "q3_energy_to_number_form_domination_closed": False,
            "q3_gibbs_weighted_boundary_uniformity_closed": False,
            "q3_evolved_history_weighted_boundary_uniformity_closed": False,
            "common_alpha_closed": False,
            "hamiltonian_os_identification_closed": False,
            "kms_gns_gap_closed": False,
            "continuum_closed": False,
            "c6_closed": False,
            "sector_a_closed": False,
            "pre_a_closed": False
        },
        "boundary": scope
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT HARMONIC-COMPRESSION-BOUNDARY-LEAKAGE PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

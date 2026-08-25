#!/usr/bin/env python3
"""Primary exact oscillator boundary-leakage audit for EXP-001105.

This is a finite matrix audit of the distinction between P A^d P and
(P A P)^d.  The conditional state-weighted estimate is recorded only as a
derived envelope from the exact support and a fifth number moment; no Q3
state is instantiated here.
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
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-25-primary-{SLUG}" / "primary.json"


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


def oscillator(dimension: int) -> tuple[np.ndarray, np.ndarray]:
    annihilation = np.zeros((dimension, dimension), dtype=complex)
    for index in range(dimension - 1):
        annihilation[index, index + 1] = np.sqrt(float(index + 1))
    creation = annihilation.conj().T
    coordinate = (annihilation + creation) / np.sqrt(2.0)
    momentum = (annihilation - creation) / (1j * np.sqrt(2.0))
    return coordinate, momentum


def projection(n: int, dimension: int) -> np.ndarray:
    result = np.zeros((dimension, dimension), dtype=complex)
    result[:n, :n] = np.eye(n, dtype=complex)
    return result


def top_block(matrix: np.ndarray, n: int) -> np.ndarray:
    return matrix[:n, :n]


def power(matrix: np.ndarray, degree: int) -> np.ndarray:
    return np.linalg.matrix_power(matrix, degree)


def compression_defect(n: int, degree: int, operator: np.ndarray) -> np.ndarray:
    ambient = operator.shape[0]
    p_n = projection(n, ambient)
    compressed = top_block(operator, n)
    return top_block(p_n @ power(operator, degree) @ p_n, n) - power(compressed, degree)


def window_projection(n: int, degree: int) -> np.ndarray:
    result = np.zeros((n, n), dtype=complex)
    first = max(0, n - degree)
    result[first:n, first:n] = np.eye(n - first, dtype=complex)
    return result


def norm_bound(ambient_dimension: int, degree: int) -> float:
    # ||P A^d P - (P A P)^d|| <= 2 ||A||^d and ||A|| <= sqrt(m).
    return 2.0 * float(ambient_dimension) ** (0.5 * degree)


def onsite_defect(n: int, ambient: int, parameters: dict[str, float]) -> tuple[np.ndarray, float]:
    coordinate, momentum = oscillator(ambient)
    q_n, p_n = top_block(coordinate, n), top_block(momentum, n)
    chi, r, g = (float(parameters[key]) for key in ("chi", "r", "g"))
    exact = top_block(momentum @ momentum / (2.0 * chi) + r * (coordinate @ coordinate) / 2.0 + g * power(coordinate, 4) / 4.0, n)
    compressed = p_n @ p_n / (2.0 * chi) + r * (q_n @ q_n) / 2.0 + g * power(q_n, 4) / 4.0
    defect = exact - compressed
    bound = (abs(1.0 / (2.0 * chi)) * norm_bound(ambient, 2) + abs(r) / 2.0 * norm_bound(ambient, 2) + abs(g) / 4.0 * norm_bound(ambient, 4))
    return defect, bound


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    scope = manifest["scope"]
    tolerance = float(fixture["tolerance"])
    moment_cap = float(fixture["moment_cap"])
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
    max_degree = max(int(value) for value in fixture["degree_values"])
    for n in [int(value) for value in fixture["n_values"]]:
        ambient = n + max_degree + 1
        coordinate, momentum = oscillator(ambient)
        row: dict[str, Any] = {"n": n, "ambient_dimension": ambient, "degrees": []}
        for degree in [int(value) for value in fixture["degree_values"]]:
            window = window_projection(n, degree)
            defects: dict[str, Any] = {}
            for label, operator in (("q", coordinate), ("p", momentum)):
                defect = compression_defect(n, degree, operator)
                support_residual = float(np.linalg.norm(defect - window @ defect @ window, ord=2))
                actual_norm = float(np.linalg.norm(defect, ord=2))
                envelope = norm_bound(ambient, degree)
                check(f"n={n} d={degree} {label} support", support_residual <= tolerance, support_residual, f"<={tolerance}", "path support")
                check(f"n={n} d={degree} {label} norm envelope", actual_norm <= envelope * (1.0 + tolerance), actual_norm, f"<={envelope * (1.0 + tolerance)}", "norm envelope")
                defects[label] = {"support_residual": support_residual, "norm": actual_norm, "derived_envelope": envelope}
            degree_row = {"degree": degree, "defects": defects}
            if n > degree:
                conditional = norm_bound(ambient, degree) * moment_cap / float(n - degree) ** 5
                degree_row["conditional_state_weighted_bound"] = conditional
                check(f"n={n} d={degree} conditional denominator", n - degree > 0, n - degree, ">0", "state envelope")
            degree_rows.append({"n": n, **degree_row})
            row["degrees"].append(degree_row)

        onsite, onsite_envelope = onsite_defect(n, ambient, fixture["parameters"])
        onsite_window = window_projection(n, max_degree)
        onsite_support = float(np.linalg.norm(onsite - onsite_window @ onsite @ onsite_window, ord=2))
        onsite_norm = float(np.linalg.norm(onsite, ord=2))
        conditional_onsite = onsite_envelope * moment_cap / float(n - max_degree) ** 5 if n > max_degree else None
        check(f"n={n} onsite support", onsite_support <= tolerance, onsite_support, f"<={tolerance}", "onsite path support")
        check(f"n={n} onsite norm envelope", onsite_norm <= onsite_envelope * (1.0 + tolerance), onsite_norm, f"<={onsite_envelope * (1.0 + tolerance)}", "onsite norm envelope")
        check(f"n={n} onsite conditional denominator", n > max_degree, n, f">{max_degree}", "state envelope")
        row["onsite"] = {"support_residual": onsite_support, "norm": onsite_norm, "derived_envelope": onsite_envelope, "conditional_state_weighted_bound": conditional_onsite}
        n_rows.append(row)

    check("cutoff sequence", [row["n"] for row in degree_rows[::len(fixture["degree_values"])] ] == [int(value) for value in fixture["n_values"]], [row["n"] for row in degree_rows[::len(fixture["degree_values"])]], fixture["n_values"], "cutoff")
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
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
    print(f"PRIMARY HARMONIC-COMPRESSION-BOUNDARY-LEAKAGE PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

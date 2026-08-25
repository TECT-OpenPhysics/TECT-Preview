#!/usr/bin/env python3
"""Independent reversed-construction lane for EXP-001109."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any

import numpy as np


REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre_a_cp1_st8_q3lock_eight_component_energy_number_form"
MANIFEST = REPO / f"strategy/{SLUG}_manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-25-independent-{SLUG}" / "independent.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def ladder(dimension: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    annihilation = np.zeros((dimension, dimension), dtype=complex)
    for row in range(dimension - 1):
        annihilation[row, row + 1] = np.sqrt(float(row + 1))
    creation = np.conjugate(annihilation.T)
    coordinate = (creation + annihilation) / np.sqrt(2.0)
    momentum = (creation - annihilation) / (1j * np.sqrt(2.0))
    number = creation @ annihilation
    return coordinate, momentum, number


def tensor_factor(single: np.ndarray, component: int, components: int, identity: np.ndarray) -> np.ndarray:
    result = np.array([[1.0 + 0.0j]])
    for index in range(components):
        result = np.kron(result, single if index == component else identity)
    return result


def cube_edges(edges: list[list[int]], components: int) -> list[tuple[int, int]]:
    result = [tuple(int(value) for value in edge) for edge in edges]
    expected = {(left, right) for left in range(components) for right in range(left + 1, components) if (left ^ right).bit_count() == 1}
    if set(result) != expected:
        raise AssertionError("independent Q3 edge-set mismatch")
    return result


def build(manifest: dict[str, Any], r_value: float, lambda_value: float) -> tuple[np.ndarray, np.ndarray]:
    fixture = manifest["finite_fixture"]
    components = int(fixture["component_count"])
    dimension = int(fixture["oscillator_dimensions"][0])
    coordinate, momentum, number = ladder(dimension)
    identity = np.eye(dimension, dtype=complex)
    q_ops = [tensor_factor(coordinate, component, components, identity) for component in range(components)]
    p_ops = [tensor_factor(momentum, component, components, identity) for component in range(components)]
    n_ops = [tensor_factor(number, component, components, identity) for component in range(components)]
    total_identity = np.eye(dimension**components, dtype=complex)
    chi = float(fixture["chi"])
    g = float(fixture["g"])
    result = np.zeros_like(total_identity)
    for component in range(components):
        result += p_ops[component] @ p_ops[component] / (2.0 * chi)
        result += r_value * q_ops[component] @ q_ops[component] / 2.0
        result += g * np.linalg.matrix_power(q_ops[component], 4) / 4.0
    for left, right in cube_edges(fixture["q3_edges"], components):
        difference = q_ops[left] - q_ops[right]
        result += lambda_value * difference @ difference @ (q_ops[left] @ q_ops[left] + q_ops[right] @ q_ops[right]) / 4.0
    result += float(fixture["onsite_shift"]) * total_identity
    result = (result + np.conjugate(result.T)) / 2.0
    total_number = np.zeros_like(total_identity)
    for operator in n_ops:
        total_number += operator
    return result, (total_number + np.conjugate(total_number.T)) / 2.0


def report(hamiltonian: np.ndarray, number: np.ndarray, moment_order: int) -> tuple[float, float, float, float, float]:
    identity = np.eye(hamiltonian.shape[0], dtype=complex)
    energy_power = np.linalg.matrix_power(hamiltonian, moment_order)
    number_power = np.linalg.matrix_power(number, moment_order)
    denominator = identity + energy_power
    values, vectors = np.linalg.eigh((denominator + np.conjugate(denominator.T)) / 2.0)
    inverse_sqrt = (vectors * (1.0 / np.sqrt(values))) @ np.conjugate(vectors.T)
    transformed = inverse_sqrt @ number_power @ inverse_sqrt
    ratio = float(np.max(np.linalg.eigvalsh((transformed + np.conjugate(transformed.T)) / 2.0)))
    residual = ratio * denominator - number_power
    residual_min = float(np.min(np.linalg.eigvalsh((residual + np.conjugate(residual.T)) / 2.0)))
    energy_min = float(np.min(np.linalg.eigvalsh((hamiltonian + np.conjugate(hamiltonian.T)) / 2.0)))
    eigvals, eigvecs = np.linalg.eigh((hamiltonian + np.conjugate(hamiltonian.T)) / 2.0)
    weights = np.exp(-(eigvals - float(np.min(eigvals))))
    rho = (eigvecs * weights) @ np.conjugate(eigvecs.T) / float(np.sum(weights))
    gibbs_ratio = float(np.real(np.trace(rho @ number_power)) / (1.0 + np.real(np.trace(rho @ energy_power))))
    return ratio, residual_min, energy_min, gibbs_ratio, float(np.real(np.trace(rho)))


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    tolerance = float(fixture["matrix_tolerance"])
    moment_order = int(fixture["moment_order"])
    assertions: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        assertions.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001109" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001109/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    rows: list[dict[str, Any]] = []
    for r_value in [float(value) for value in fixture["r_values"]]:
        for lambda_value in [float(value) for value in fixture["lambda_values"]]:
            hamiltonian, number = build(manifest, r_value, lambda_value)
            ratio, residual_min, energy_min, gibbs_ratio, gibbs_trace = report(hamiltonian, number, moment_order)
            check(f"r={r_value} lambda={lambda_value} positive energy", energy_min > float(fixture["positive_floor_tolerance"]), energy_min, ">0", "form")
            check(f"r={r_value} lambda={lambda_value} residual", residual_min >= -tolerance, residual_min, f">=-{tolerance}", "form")
            check(f"r={r_value} lambda={lambda_value} Gibbs trace", abs(gibbs_trace - 1.0) <= tolerance, gibbs_trace, "1", "Gibbs")
            rows.append({"r": r_value, "lambda": lambda_value, "dimension": int(hamiltonian.shape[0]), "energy_min": energy_min, "form_ratio": ratio, "form_residual_min": residual_min, "gibbs_ratio": gibbs_ratio})
    check("parameter grid", len(rows) == len(fixture["r_values"]) * len(fixture["lambda_values"]), len(rows), len(fixture["r_values"]) * len(fixture["lambda_values"]), "fixture")
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "independent", "audit_id": "PA-CP1-ST8-Q3LOCK-EIGHT-COMPONENT-ENERGY-NUMBER-FORM", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "passed": len(assertions), "assertion_count": len(assertions), "assertions": assertions, "derived": {"rows": rows, "max_form_ratio": max(row["form_ratio"] for row in rows), "finite_eight_component_form_ratio_closed": True, "uniform_graph_constant_instantiated": False, "q_p_to_creation_annihilation_domain_closed": False, "energy_to_number_uniform_form_domination_closed": False, "source_volume_orientation_history_uniform_closed": False, "kms_gns_gap_closed": False, "continuum_closed": False, "pre_a_closed": False}, "provenance": {"script": str(SCRIPT.relative_to(REPO)).replace("\\", "/"), "script_sha256": sha256(SCRIPT), "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"), "manifest_sha256": sha256(MANIFEST)}}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT EIGHT-COMPONENT-ENERGY-NUMBER-FORM PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

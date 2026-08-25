#!/usr/bin/env python3
"""Primary finite canonical eight-component Q3 energy/number form audit."""

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
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-25-primary-{SLUG}" / "primary.json"


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


def oscillator(dimension: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    annihilation = np.zeros((dimension, dimension), dtype=complex)
    for index in range(dimension - 1):
        annihilation[index, index + 1] = np.sqrt(index + 1.0)
    creation = annihilation.conj().T
    coordinate = (annihilation + creation) / np.sqrt(2.0)
    momentum = (annihilation - creation) / (1j * np.sqrt(2.0))
    number = creation @ annihilation
    return coordinate, momentum, number


def embed(single: np.ndarray, component: int, components: int, identity: np.ndarray) -> np.ndarray:
    factors = [single if index == component else identity for index in range(components)]
    result = factors[0]
    for factor in factors[1:]:
        result = np.kron(result, factor)
    return result


def q3_edges(manifest_edges: list[list[int]], components: int) -> list[tuple[int, int]]:
    edges = [tuple(int(value) for value in edge) for edge in manifest_edges]
    expected = {(left, right) for left in range(components) for right in range(left + 1, components) if (left ^ right).bit_count() == 1}
    if set(edges) != expected:
        raise AssertionError(f"Q3 edge set mismatch: actual={edges!r}, expected={sorted(expected)!r}")
    return edges


def build_hamiltonian(manifest: dict[str, Any], r_value: float, lambda_value: float) -> tuple[np.ndarray, np.ndarray]:
    fixture = manifest["finite_fixture"]
    components = int(fixture["component_count"])
    dimension = int(fixture["oscillator_dimensions"][0])
    coordinate, momentum, number = oscillator(dimension)
    identity = np.eye(dimension, dtype=complex)
    q_ops = [embed(coordinate, index, components, identity) for index in range(components)]
    p_ops = [embed(momentum, index, components, identity) for index in range(components)]
    n_ops = [embed(number, index, components, identity) for index in range(components)]
    total_dimension = dimension**components
    total_identity = np.eye(total_dimension, dtype=complex)
    chi = float(fixture["chi"])
    g = float(fixture["g"])
    hamiltonian = np.zeros_like(total_identity)
    for q_op, p_op in zip(q_ops, p_ops):
        hamiltonian = hamiltonian + p_op @ p_op / (2.0 * chi) + r_value * (q_op @ q_op) / 2.0 + g * np.linalg.matrix_power(q_op, 4) / 4.0
    for left, right in q3_edges(fixture["q3_edges"], components):
        difference = q_ops[left] - q_ops[right]
        hamiltonian = hamiltonian + lambda_value * (difference @ difference) @ (q_ops[left] @ q_ops[left] + q_ops[right] @ q_ops[right]) / 4.0
    hamiltonian = hamiltonian + float(fixture["onsite_shift"]) * total_identity
    hamiltonian = (hamiltonian + hamiltonian.conj().T) / 2.0
    total_number = sum(n_ops, np.zeros_like(total_identity))
    return hamiltonian, (total_number + total_number.conj().T) / 2.0


def unitary(hamiltonian: np.ndarray, time: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((hamiltonian + hamiltonian.conj().T) / 2.0)
    return (vectors * np.exp(-1j * time * values)) @ vectors.conj().T


def gibbs(hamiltonian: np.ndarray, beta: float) -> np.ndarray:
    values, vectors = np.linalg.eigh((hamiltonian + hamiltonian.conj().T) / 2.0)
    shifted = values - float(np.min(values))
    weights = np.exp(-beta * shifted)
    return (vectors * weights) @ vectors.conj().T / float(np.sum(weights))


def expectation_state(state: np.ndarray, operator: np.ndarray) -> float:
    return float(np.real(np.trace(state @ operator)))


def expectation_vector(vector: np.ndarray, operator: np.ndarray) -> float:
    return float(np.real(np.vdot(vector, operator @ vector)))


def generalized_ratio(hamiltonian: np.ndarray, number: np.ndarray, moment_order: int) -> tuple[float, float, float]:
    identity = np.eye(hamiltonian.shape[0], dtype=complex)
    energy_power = np.linalg.matrix_power(hamiltonian, moment_order)
    number_power = np.linalg.matrix_power(number, moment_order)
    denominator = (identity + energy_power + (identity + energy_power).conj().T) / 2.0
    denominator_values, denominator_vectors = np.linalg.eigh(denominator)
    inverse_sqrt = (denominator_vectors * (1.0 / np.sqrt(denominator_values))) @ denominator_vectors.conj().T
    transformed = inverse_sqrt @ number_power @ inverse_sqrt
    ratio = float(np.max(np.linalg.eigvalsh((transformed + transformed.conj().T) / 2.0)))
    residual = ratio * denominator - number_power
    residual_min = float(np.min(np.linalg.eigvalsh((residual + residual.conj().T) / 2.0)))
    energy_min = float(np.min(np.linalg.eigvalsh((hamiltonian + hamiltonian.conj().T) / 2.0)))
    return ratio, residual_min, energy_min


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = manifest["finite_fixture"]
    scope = manifest["scope"]
    tolerance = float(fixture["matrix_tolerance"])
    agreement_tolerance = float(fixture["agreement_tolerance"])
    floor_tolerance = float(fixture["positive_floor_tolerance"])
    moment_order = int(fixture["moment_order"])
    components = int(fixture["component_count"])
    audit: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        audit.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("identity", manifest["exploration_id"] == "EXP-001109" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001109/T-054", "provenance")
    check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    edge_vertices = {int(endpoint) for edge in fixture["q3_edges"] for endpoint in edge}
    check("component count", components == len(edge_vertices), [components, len(edge_vertices)], "all Q3 vertices", "model")
    check("moment order", moment_order == 5, moment_order, "5", "moment")
    check("Q3 cube edge set", len(q3_edges(fixture["q3_edges"], components)) == 12, fixture["q3_edges"], "12 cube edges", "model")
    check("scope firewall", scope["finite_eight_component_form_ratio_closed"] and not scope["uniform_graph_constant_instantiated"] and not scope["energy_to_number_uniform_form_domination_closed"], scope, "finite/open", "scope")

    rows: list[dict[str, Any]] = []
    for r_value in [float(value) for value in fixture["r_values"]]:
        for lambda_value in [float(value) for value in fixture["lambda_values"]]:
            hamiltonian, number = build_hamiltonian(manifest, r_value, lambda_value)
            ratio, residual_min, energy_min = generalized_ratio(hamiltonian, number, moment_order)
            check(f"r={r_value} lambda={lambda_value} positive energy", energy_min > floor_tolerance, energy_min, ">0", "form")
            check(f"r={r_value} lambda={lambda_value} finite form residual", residual_min >= -tolerance, residual_min, f">=-{tolerance}", "form")
            rho = gibbs(hamiltonian, float(fixture["beta"]))
            number_power = np.linalg.matrix_power(number, moment_order)
            energy_power = np.linalg.matrix_power(hamiltonian, moment_order)
            gibbs_number = expectation_state(rho, number_power)
            gibbs_energy = expectation_state(rho, energy_power)
            check(f"r={r_value} lambda={lambda_value} Gibbs trace", abs(float(np.trace(rho).real) - 1.0) <= tolerance, float(np.trace(rho).real), "1", "Gibbs")
            check(f"r={r_value} lambda={lambda_value} Gibbs form ratio", gibbs_number <= ratio * (1.0 + gibbs_energy) + tolerance, [gibbs_number, gibbs_energy, ratio], "dominated", "Gibbs")
            vacuum = np.zeros(hamiltonian.shape[0], dtype=complex)
            vacuum[0] = 1.0
            history_rows: list[dict[str, Any]] = []
            for time in [float(value) for value in fixture["history_times"]]:
                propagator = unitary(hamiltonian, time)
                vector = propagator @ vacuum
                unitarity = float(np.linalg.norm(propagator.conj().T @ propagator - np.eye(hamiltonian.shape[0]), ord=2))
                history_number = expectation_vector(vector, number_power)
                history_energy = expectation_vector(vector, energy_power)
                check(f"r={r_value} lambda={lambda_value} t={time} unitary", unitarity <= agreement_tolerance, unitarity, f"<={agreement_tolerance}", "history")
                check(f"r={r_value} lambda={lambda_value} t={time} history form ratio", history_number <= ratio * (1.0 + history_energy) + tolerance, [history_number, history_energy, ratio], "dominated", "history")
                history_rows.append({"time": time, "unitarity_residual": unitarity, "number_moment": history_number, "energy_moment": history_energy, "ratio": float(history_number / (1.0 + history_energy))})
            rows.append({"r": r_value, "lambda": lambda_value, "dimension": int(hamiltonian.shape[0]), "energy_min": energy_min, "form_ratio": ratio, "form_residual_min": residual_min, "gibbs_number_moment": gibbs_number, "gibbs_energy_moment": gibbs_energy, "gibbs_ratio": float(gibbs_number / (1.0 + gibbs_energy)), "history": history_rows})
    check("parameter grid", len(rows) == len(fixture["r_values"]) * len(fixture["lambda_values"]), len(rows), len(fixture["r_values"]) * len(fixture["lambda_values"]), "fixture")
    check("finite ratios bounded", all(np.isfinite(row["form_ratio"]) and row["form_ratio"] > 0.0 for row in rows), [row["form_ratio"] for row in rows], "finite positive", "form")
    check("QFT firewall", not any(scope[key] for key in ("uniform_graph_constant_instantiated", "q_p_to_creation_annihilation_domain_closed", "source_volume_orientation_history_uniform_closed", "kms_gns_gap_closed", "continuum_closed", "pre_a_closed")), scope, "successor gates open", "scope")
    passed = len(audit)
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": "PA-CP1-ST8-Q3LOCK-EIGHT-COMPONENT-ENERGY-NUMBER-FORM",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": passed,
        "assertion_count": passed,
        "assertions": audit,
        "derived": {"rows": rows, "max_form_ratio": max(row["form_ratio"] for row in rows), "finite_eight_component_form_ratio_closed": True, "finite_gibbs_number_energy_comparison_closed": True, "finite_history_number_energy_comparison_closed": True, "uniform_graph_constant_instantiated": False, "q_p_to_creation_annihilation_domain_closed": False, "energy_to_number_uniform_form_domination_closed": False, "q3_gibbs_weighted_tail_uniformity_closed": False, "q3_evolved_history_weighted_tail_uniformity_closed": False, "actual_unbounded_q3_domain_transfer_closed": False, "source_volume_orientation_history_uniform_closed": False, "direct_d_delta_d_cauchy_closed": False, "common_alpha_closed": False, "hamiltonian_os_identification_closed": False, "kms_gns_gap_closed": False, "continuum_closed": False, "c6_closed": False, "sector_a_closed": False, "pre_a_closed": False},
        "provenance": {"script": str(SCRIPT.relative_to(REPO)).replace("\\", "/"), "script_sha256": sha256(SCRIPT), "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"), "manifest_sha256": sha256(MANIFEST)},
        "boundary": scope,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY EIGHT-COMPONENT-ENERGY-NUMBER-FORM PASS {payload['passed']}/{payload['assertion_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

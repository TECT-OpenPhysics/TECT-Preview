#!/usr/bin/env python3
"""Primary finite Q3 common-word OS/KMS context comparison for EXP-001174.

The program evaluates the same source-0 half-period transfer words in several
finite Hamiltonian contexts.  It reports adjacent-context deltas; it does not
silently turn those finite diagnostics into an exhaustion or OS theorem.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import tempfile
from pathlib import Path
from fractions import Fraction
from typing import Any

import numpy as np


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-st8-q3lock-finite-common-word-cauchy"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-26-primary-{SLUG}" / "primary.json"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pre_a_cp1_st8_q3lock_finite_split_gibbs_kms_residual as base  # noqa: E402


def periodic_terms(edges: list[tuple[int, int]], volume: int, dimension: int, parameters: dict[str, str]) -> tuple[list[np.ndarray], np.ndarray, np.ndarray]:
    q_single, p_single = base.oscillator(dimension)
    identity = np.eye(dimension, dtype=complex)
    q_ops = [base.embed(q_single, site, volume, identity) for site in range(volume)]
    p_ops = [base.embed(p_single, site, volume, identity) for site in range(volume)]
    chi = float(Fraction(parameters["chi"]))
    r = float(Fraction(parameters["r"]))
    g = float(Fraction(parameters["g"]))
    onsite = [p @ p / (2.0 * chi) + r * (q @ q) / 2.0 + g * (q @ q @ q @ q) / 4.0 for q, p in zip(q_ops, p_ops)]
    bonds = [base.bond_term(q_ops[left], q_ops[right], parameters) for left, right in edges]
    return onsite + bonds, q_single, p_single


def transfer_vector(energies: np.ndarray, seconds: float, hbar: float) -> np.ndarray:
    return np.exp(-seconds * energies / hbar)


def thermal_word(energies: np.ndarray, left: np.ndarray, right: np.ndarray, period: float, seconds: float, z: float, hbar: float) -> complex:
    weights = np.exp(-((period - seconds) * energies[:, None] + seconds * energies[None, :]) / hbar)
    return complex(np.sum(weights * left * right.T) / z)


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


def finite_context(declaration: dict[str, Any], fixture: dict[str, Any], parameters: dict[str, str]) -> dict[str, Any]:
    volume = int(declaration["vertices"])
    edges = [tuple(int(value) for value in edge) for edge in declaration["edges"]]
    sources = [int(value) for value in declaration["source_sites"]]
    canonical = [(min(left, right), max(left, right)) for left, right in edges]
    if any(left == right or left < 0 or right < 0 or left >= volume or right >= volume for left, right in edges):
        raise AssertionError(f"invalid edge set: {edges!r}")
    if len(set(canonical)) != len(canonical):
        raise AssertionError(f"duplicate edge set: {edges!r}")
    if sources != [0]:
        raise AssertionError(f"common source must be [0]: {sources!r}")

    dimension = int(fixture["oscillator_dimension"])
    terms, q_single, p_single = periodic_terms(edges, volume, dimension, parameters)
    hamiltonian = base.hermitian(sum(terms, np.zeros_like(terms[0])))
    energies, vectors = base.eigensystem(hamiltonian)
    shifted = energies - float(np.min(energies))
    noncommutation = base.operator_norm(hamiltonian @ terms[0] - terms[0] @ hamiltonian)
    identity = np.eye(dimension, dtype=complex)
    amplitude = float(fixture["character_amplitude"])
    hbar = float(fixture["hbar"])
    site = 0
    local = {
        "q": base.embed(base.character(q_single, amplitude, hbar), site, volume, identity),
        "p": base.embed(base.character(p_single, amplitude, hbar), site, volume, identity),
    }
    in_basis = {kind: vectors.conj().T @ observable @ vectors for kind, observable in local.items()}
    gram_rows: list[dict[str, Any]] = []
    thermal_rows: list[dict[str, Any]] = []
    reflection_errors: list[float] = []

    for beta_value in fixture["beta_values"]:
        beta = float(beta_value)
        period = beta * hbar
        weights = transfer_vector(shifted, period / hbar, 1.0)
        z = float(np.sum(weights))
        if not np.isfinite(z) or z <= 0.0:
            raise AssertionError(f"invalid partition function {z!r}")
        descriptors: list[dict[str, Any]] = []
        transfer_words: list[np.ndarray] = []
        for fraction in fixture["euclidean_time_fractions"]:
            tau = float(fraction) * period
            if tau < 0.0 or tau > period / 2.0:
                raise AssertionError(f"half-period violation: {tau!r}")
            for kind in ("q", "p"):
                observable = in_basis[kind]
                left = transfer_vector(shifted, period / 2.0 - tau, hbar)
                right = transfer_vector(shifted, tau, hbar)
                transfer_words.append(left[:, None] * observable * right[None, :])
                descriptors.append({"tau_fraction": float(fraction), "kind": kind})
        gram = np.array([[np.vdot(one, two) / z for two in transfer_words] for one in transfer_words], dtype=complex)
        gram = (gram + gram.conj().T) / 2.0
        reflected = np.zeros_like(gram)
        for i, first in enumerate(descriptors):
            for j, second in enumerate(descriptors):
                first_op = in_basis[first["kind"]]
                second_op = in_basis[second["kind"]]
                tau_sum = (float(first["tau_fraction"]) + float(second["tau_fraction"])) * period
                exponent = np.exp(-((period - tau_sum) * shifted[:, None] + tau_sum * shifted[None, :]) / hbar)
                reflected[i, j] = np.sum(exponent * first_op.conj() * second_op) / z
        reflection_error = float(np.max(np.abs(gram - (reflected + reflected.conj().T) / 2.0)))
        eigenvalues = np.linalg.eigvalsh(gram)
        gram_rows.append({
            "graph": declaration["name"],
            "volume": volume,
            "source_site": site,
            "beta": beta,
            "descriptor_order": descriptors,
            "matrix_real": gram.real.tolist(),
            "matrix_imag": gram.imag.tolist(),
            "min_eigenvalue": float(np.min(eigenvalues)),
            "max_eigenvalue": float(np.max(eigenvalues)),
            "diagonal_min": float(np.min(np.real(np.diag(gram)))),
            "reflection_error": reflection_error,
            "partition_function": z,
        })
        reflection_errors.append(reflection_error)

        for fraction in fixture["cyclicity_fractions"]:
            seconds = float(fraction) * period
            forward = thermal_word(shifted, in_basis["q"], in_basis["p"], period, seconds, z, hbar)
            reverse = thermal_word(shifted, in_basis["p"], in_basis["q"], period, period - seconds, z, hbar)
            thermal_rows.append({
                "graph": declaration["name"],
                "volume": volume,
                "source_site": site,
                "beta": beta,
                "fraction": float(fraction),
                "seconds": seconds,
                "forward_real": float(forward.real),
                "forward_imag": float(forward.imag),
                "reverse_real": float(reverse.real),
                "reverse_imag": float(reverse.imag),
                "cyclicity_residual": float(abs(forward - reverse)),
                "witness": float(abs(forward) + abs(reverse)),
            })
    return {
        "name": declaration["name"],
        "volume": volume,
        "edge_count": len(edges),
        "degree_min": min(sum(vertex in edge for edge in edges) for vertex in range(volume)),
        "degree_max": max(sum(vertex in edge for edge in edges) for vertex in range(volume)),
        "source_site": site,
        "noncommutation": float(noncommutation),
        "gram_rows": gram_rows,
        "thermal_rows": thermal_rows,
        "max_reflection_error": max(reflection_errors),
    }


def compare_contexts(contexts: dict[str, dict[str, Any]], nested: list[str], betas: list[float]) -> list[dict[str, Any]]:
    comparisons: list[dict[str, Any]] = []
    for left_name, right_name in zip(nested, nested[1:]):
        left = contexts[left_name]
        right = contexts[right_name]
        for beta in betas:
            left_gram = next(row for row in left["gram_rows"] if row["beta"] == beta)
            right_gram = next(row for row in right["gram_rows"] if row["beta"] == beta)
            left_matrix = np.asarray(left_gram["matrix_real"]) + 1j * np.asarray(left_gram["matrix_imag"])
            right_matrix = np.asarray(right_gram["matrix_real"]) + 1j * np.asarray(right_gram["matrix_imag"])
            gram_difference = np.abs(right_matrix - left_matrix)
            left_thermal = [row for row in left["thermal_rows"] if row["beta"] == beta]
            right_thermal = [row for row in right["thermal_rows"] if row["beta"] == beta]
            thermal_differences: list[float] = []
            for one, two in zip(sorted(left_thermal, key=lambda row: row["fraction"]), sorted(right_thermal, key=lambda row: row["fraction"])):
                forward_delta = abs(complex(two["forward_real"], two["forward_imag"]) - complex(one["forward_real"], one["forward_imag"]))
                reverse_delta = abs(complex(two["reverse_real"], two["reverse_imag"]) - complex(one["reverse_real"], one["reverse_imag"]))
                thermal_differences.extend([float(forward_delta), float(reverse_delta)])
            scale = max(float(np.max(np.abs(left_matrix))), float(np.max(np.abs(right_matrix))), 1e-30)
            thermal_scale = max(
                *(abs(complex(row["forward_real"], row["forward_imag"])) for row in left_thermal + right_thermal),
                1e-30,
            )
            comparisons.append({
                "from_graph": left_name,
                "to_graph": right_name,
                "from_volume": int(left["volume"]),
                "to_volume": int(right["volume"]),
                "beta": beta,
                "gram_max_delta": float(np.max(gram_difference)),
                "gram_frobenius_delta": float(np.linalg.norm(right_matrix - left_matrix)),
                "gram_relative_max_delta": float(np.max(gram_difference) / scale),
                "thermal_max_delta": max(thermal_differences),
                "thermal_relative_max_delta": float(max(thermal_differences) / thermal_scale),
                "max_context_delta": max(float(np.max(gram_difference)), max(thermal_differences)),
            })
    return comparisons


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": actual, "expected": expected})

    check("identity", manifest["exploration_id"] == "EXP-001174" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001174/T-054", "provenance")
    check("claim firewall", manifest["claim_bearing"] is False and not scope["volume_uniform_os_cauchy_closed"], [manifest["claim_bearing"], scope["volume_uniform_os_cauchy_closed"]], "nonbearing/open", "scope")
    check("graph order", list(fixture["graphs"]) == ["path2", "path3", "path4", "path5", "bond2", "square4", "grid2x3"], list(fixture["graphs"]), "registered contexts", "fixture")
    check("nested order", fixture["nested_graphs"] == ["path2", "path3", "path4", "path5"], fixture["nested_graphs"], "path2->path5", "fixture")
    check("dimension", int(fixture["oscillator_dimension"]) == 3, fixture["oscillator_dimension"], 3, "nondegenerate d=3")
    check("common source", all(declaration["source_sites"] == [0] for declaration in fixture["graphs"].values()), fixture["graphs"], "source site 0", "fixture")
    check("scope firewall", scope["finite_q3_transfer_closed"] and scope["finite_os_gram_closed"] and scope["finite_thermal_cyclicity_closed"] and scope["identical_local_word_descriptor_closed"] and scope["finite_context_comparison_closed"] and not scope["source_uniform_common_word_closed"] and not scope["volume_uniform_os_cauchy_closed"] and not scope["common_alpha_closed"] and not scope["pre_a_closed"], scope, "finite comparison only", "scope")

    contexts: dict[str, dict[str, Any]] = {}
    for name, declaration in fixture["graphs"].items():
        declaration = dict(declaration)
        declaration["name"] = name
        context = finite_context(declaration, fixture, manifest["model_parameters"])
        contexts[name] = context
        check(f"{name} noncommutation", context["noncommutation"] >= float(fixture.get("noncommutation_witness_floor", 1e-6)), context["noncommutation"], "positive Q3 witness", "nondegenerate Q3")
        check(f"{name} gram coverage", len(context["gram_rows"]) == len(fixture["beta_values"]), len(context["gram_rows"]), len(fixture["beta_values"]), "coverage")
        check(f"{name} thermal coverage", len(context["thermal_rows"]) == len(fixture["beta_values"]) * len(fixture["cyclicity_fractions"]), len(context["thermal_rows"]), len(fixture["beta_values"]) * len(fixture["cyclicity_fractions"]), "coverage")
        for row in context["gram_rows"]:
            check(f"{name} beta={row['beta']} Gram finite", np.all(np.isfinite(np.asarray(row["matrix_real"]))) and np.all(np.isfinite(np.asarray(row["matrix_imag"]))), row["reflection_error"], "finite", "OS Gram")
            check(f"{name} beta={row['beta']} Gram reflection", row["reflection_error"] <= float(fixture["agreement_tolerance"]), row["reflection_error"], f"<={fixture['agreement_tolerance']}", "OS Gram")
            check(f"{name} beta={row['beta']} Gram positive", row["min_eigenvalue"] >= -float(fixture["positive_tolerance"]), row["min_eigenvalue"], f">={-float(fixture['positive_tolerance'])}", "OS Gram")
            check(f"{name} beta={row['beta']} Gram diagonal", row["diagonal_min"] >= float(fixture["positive_diagonal_floor"]), row["diagonal_min"], f">={fixture['positive_diagonal_floor']}", "OS Gram")
        for row in context["thermal_rows"]:
            check(f"{name} beta={row['beta']} s={row['seconds']} KMS finite", np.isfinite(row["cyclicity_residual"]) and np.isfinite(row["witness"]), [row["cyclicity_residual"], row["witness"]], "finite", "thermal KMS")
            check(f"{name} beta={row['beta']} s={row['seconds']} KMS cyclicity", row["cyclicity_residual"] <= float(fixture["finite_tolerance"]), row["cyclicity_residual"], f"<={fixture['finite_tolerance']}", "thermal KMS")

    betas = [float(value) for value in fixture["beta_values"]]
    comparisons = compare_contexts(contexts, list(fixture["nested_graphs"]), betas)
    check("comparison coverage", len(comparisons) == (len(fixture["nested_graphs"]) - 1) * len(betas), len(comparisons), (len(fixture["nested_graphs"]) - 1) * len(betas), "coverage")
    check("comparison finite", all(np.isfinite(row[key]) for row in comparisons for key in ("gram_max_delta", "gram_frobenius_delta", "gram_relative_max_delta", "thermal_max_delta", "thermal_relative_max_delta", "max_context_delta")), len(comparisons), "finite", "context comparison")
    max_delta = max(row["max_context_delta"] for row in comparisons)
    min_delta = min(row["max_context_delta"] for row in comparisons)
    check("context sensitivity witness", max_delta >= float(fixture["context_witness_floor"]), max_delta, f">={fixture['context_witness_floor']}", "adversarial context")
    path_delta_sequence = [row["max_context_delta"] for row in comparisons if row["beta"] == betas[0]]
    monotone = all(one >= two for one, two in zip(path_delta_sequence, path_delta_sequence[1:]))
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": "PA-CP1-ST8-Q3LOCK-FINITE-COMMON-WORD-CAUCHY",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": len(checks),
        "assertion_count": len(checks),
        "assertions": checks,
        "contexts": [{key: value for key, value in context.items() if key not in ("gram_rows", "thermal_rows")} for context in contexts.values()],
        "gram_rows": [row for context in contexts.values() for row in context["gram_rows"]],
        "thermal_rows": [row for context in contexts.values() for row in context["thermal_rows"]],
        "comparisons": comparisons,
        "derived": {
            "context_count": len(contexts),
            "nested_pair_count": len(fixture["nested_graphs"]) - 1,
            "gram_row_count": sum(len(context["gram_rows"]) for context in contexts.values()),
            "thermal_row_count": sum(len(context["thermal_rows"]) for context in contexts.values()),
            "comparison_count": len(comparisons),
            "min_context_delta": min_delta,
            "max_context_delta": max_delta,
            "path_beta0_delta_sequence": path_delta_sequence,
            "path_beta0_delta_nonincreasing": monotone,
            "finite_q3_transfer_closed": True,
            "finite_os_gram_closed": True,
            "finite_thermal_cyclicity_closed": True,
            "identical_local_word_descriptor_closed": True,
            "finite_context_comparison_closed": True,
            "source_uniform_common_word_closed": False,
            "volume_uniform_direct_d_cauchy_closed": False,
            "volume_uniform_os_cauchy_closed": False,
            "exhaustion_independence_closed": False,
            "common_alpha_closed": False,
            "hamiltonian_os_identification_closed": False,
            "kms_gns_gap_closed": False,
            "continuum_closed": False,
            "c6_closed": False,
            "sector_a_closed": False,
            "pre_a_closed": False,
            "no_new_negative_result": True,
            "no_tier_change": True,
            "no_pdf": True,
        },
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
    print(f"PRIMARY FINITE-COMMON-WORD-CAUCHY PASS {payload['passed']}/{payload['assertion_count']} contexts={payload['derived']['context_count']} comparisons={payload['derived']['comparison_count']} max_delta={payload['derived']['max_context_delta']:.16g}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

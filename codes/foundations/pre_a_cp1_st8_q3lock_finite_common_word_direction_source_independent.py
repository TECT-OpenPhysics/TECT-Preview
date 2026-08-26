#!/usr/bin/env python3
"""Independent reconstruction for EXP-001175 direction/source stress."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-st8-q3lock-finite-common-word-direction-source"
MANIFEST = ROOT / f"strategy/{SLUG}-manifest.json"
DEFAULT_OUTPUT = ROOT / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-26-independent-{SLUG}" / "independent.json"


def save_json(path: Path, payload: dict[str, Any]) -> None:
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


def oscillator(size: int) -> tuple[np.ndarray, np.ndarray]:
    lowering = np.zeros((size, size), dtype=complex)
    for index in range(size - 1):
        lowering[index, index + 1] = np.sqrt(float(index + 1))
    raising = lowering.conj().T
    return (lowering + raising) / np.sqrt(2.0), (lowering - raising) / (1j * np.sqrt(2.0))


def tensor_at(local: np.ndarray, site: int, volume: int, identity: np.ndarray) -> np.ndarray:
    result: np.ndarray | None = None
    for index in range(volume):
        factor = local if index == site else identity
        result = factor if result is None else np.kron(result, factor)
    assert result is not None
    return result


def hermitian(matrix: np.ndarray) -> np.ndarray:
    return (matrix + matrix.conj().T) * 0.5


def spectrum(matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    return np.linalg.eigh(hermitian(matrix))


def bond(left: np.ndarray, right: np.ndarray, parameters: dict[str, str]) -> np.ndarray:
    difference = left - right
    square = difference @ difference
    c = float(Fraction(parameters["c"]))
    lam = float(Fraction(parameters["lambda"]))
    return c * square / 2.0 + lam * square @ (left @ left + right @ right) / 4.0


def hamiltonian_terms(edges: list[tuple[int, int]], volume: int, size: int, parameters: dict[str, str]) -> tuple[list[np.ndarray], np.ndarray, np.ndarray]:
    q_local, p_local = oscillator(size)
    identity = np.eye(size, dtype=complex)
    q_ops = [tensor_at(q_local, site, volume, identity) for site in range(volume)]
    p_ops = [tensor_at(p_local, site, volume, identity) for site in range(volume)]
    chi, r, g = (float(Fraction(parameters[key])) for key in ("chi", "r", "g"))
    onsite = [p @ p / (2.0 * chi) + r * q @ q / 2.0 + g * q @ q @ q @ q / 4.0 for q, p in zip(q_ops, p_ops)]
    return onsite + [bond(q_ops[left], q_ops[right], parameters) for left, right in edges], q_local, p_local


def character(local: np.ndarray, amplitude: float, hbar: float) -> np.ndarray:
    values, vectors = spectrum(local)
    return (vectors * np.exp(1j * amplitude * values / hbar)) @ vectors.conj().T


def transfer(energies: np.ndarray, seconds: float, hbar: float) -> np.ndarray:
    return np.exp(-seconds * energies / hbar)


def thermal_word(energies: np.ndarray, left: np.ndarray, right: np.ndarray, period: float, seconds: float, z: float, hbar: float) -> complex:
    weights = np.exp(-((period - seconds) * energies[:, None] + seconds * energies[None, :]) / hbar)
    return complex(np.sum(weights * left * right.T) / z)


def make_context(name: str, declaration: dict[str, Any], fixture: dict[str, Any], parameters: dict[str, str]) -> dict[str, Any]:
    volume = int(declaration["vertices"])
    edges = [tuple(int(value) for value in edge) for edge in declaration["edges"]]
    sites = [int(value) for value in declaration["source_sites"]]
    roles = [str(value) for value in declaration["source_roles"]]
    if len(sites) != len(roles) or len(set(roles)) != len(roles):
        raise AssertionError(f"invalid role declaration {sites!r} {roles!r}")
    if any(site < 0 or site >= volume for site in sites):
        raise AssertionError(f"invalid source site {sites!r}")
    if any(left == right or min(left, right) < 0 or max(left, right) >= volume for left, right in edges):
        raise AssertionError(f"invalid edge set {edges!r}")
    if len({(min(left, right), max(left, right)) for left, right in edges}) != len(edges):
        raise AssertionError(f"duplicate edge set {edges!r}")
    size = int(fixture["oscillator_dimension"])
    terms, q_local, p_local = hamiltonian_terms(edges, volume, size, parameters)
    hamiltonian = hermitian(sum(terms, np.zeros_like(terms[0])))
    energies, vectors = spectrum(hamiltonian)
    shifted = energies - float(np.min(energies))
    identity = np.eye(size, dtype=complex)
    amplitude = float(fixture["character_amplitude"])
    hbar = float(fixture["hbar"])
    basis: dict[str, dict[str, np.ndarray]] = {}
    for site, role in zip(sites, roles):
        q_operator = tensor_at(character(q_local, amplitude, hbar), site, volume, identity)
        p_operator = tensor_at(character(p_local, amplitude, hbar), site, volume, identity)
        basis[role] = {"q": vectors.conj().T @ q_operator @ vectors, "p": vectors.conj().T @ p_operator @ vectors}
    gram_rows: list[dict[str, Any]] = []
    thermal_rows: list[dict[str, Any]] = []
    for beta_value in fixture["beta_values"]:
        beta = float(beta_value)
        period = beta * hbar
        z = float(np.sum(transfer(shifted, period / hbar, 1.0)))
        if not np.isfinite(z) or z <= 0.0:
            raise AssertionError(f"invalid partition {z!r}")
        for site, role in zip(sites, roles):
            descriptors: list[dict[str, Any]] = []
            words: list[np.ndarray] = []
            for fraction in fixture["euclidean_time_fractions"]:
                tau = float(fraction) * period
                if not 0.0 <= tau <= period / 2.0:
                    raise AssertionError(f"half-period violation {tau!r}")
                for kind in ("q", "p"):
                    words.append(transfer(shifted, period / 2.0 - tau, hbar)[:, None] * basis[role][kind] * transfer(shifted, tau, hbar)[None, :])
                    descriptors.append({"tau_fraction": float(fraction), "kind": kind})
            gram = np.array([[np.vdot(one, two) / z for two in words] for one in words], dtype=complex)
            gram = (gram + gram.conj().T) / 2.0
            reflected = np.zeros_like(gram)
            for i, first in enumerate(descriptors):
                for j, second in enumerate(descriptors):
                    tau_sum = (float(first["tau_fraction"]) + float(second["tau_fraction"])) * period
                    exponent = np.exp(-((period - tau_sum) * shifted[:, None] + tau_sum * shifted[None, :]) / hbar)
                    reflected[i, j] = np.sum(exponent * basis[role][first["kind"]].conj() * basis[role][second["kind"]]) / z
            eigenvalues = np.linalg.eigvalsh(gram)
            gram_rows.append({
                "graph": name,
                "volume": volume,
                "source_role": role,
                "source_site": site,
                "beta": beta,
                "descriptor_order": descriptors,
                "matrix_real": gram.real.tolist(),
                "matrix_imag": gram.imag.tolist(),
                "min_eigenvalue": float(np.min(eigenvalues)),
                "max_eigenvalue": float(np.max(eigenvalues)),
                "diagonal_min": float(np.min(np.real(np.diag(gram)))),
                "reflection_error": float(np.max(np.abs(gram - (reflected + reflected.conj().T) / 2.0))),
                "partition_function": z,
            })
            for fraction in fixture["cyclicity_fractions"]:
                seconds = float(fraction) * period
                forward = thermal_word(shifted, basis[role]["q"], basis[role]["p"], period, seconds, z, hbar)
                reverse = thermal_word(shifted, basis[role]["p"], basis[role]["q"], period, period - seconds, z, hbar)
                thermal_rows.append({
                    "graph": name,
                    "volume": volume,
                    "source_role": role,
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
    degrees = [sum(vertex in edge for edge in edges) for vertex in range(volume)]
    return {"name": name, "volume": volume, "edge_count": len(edges), "degree_min": min(degrees), "degree_max": max(degrees), "source_roles": roles, "source_sites": sites, "noncommutation": float(np.linalg.norm(hamiltonian @ terms[0] - terms[0] @ hamiltonian, ord=2)), "gram_rows": gram_rows, "thermal_rows": thermal_rows}


def compare(contexts: dict[str, dict[str, Any]], nested: list[str], roles: list[str], betas: list[float]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for from_name, to_name in zip(nested, nested[1:]):
        for role in roles:
            for beta in betas:
                left = next(row for row in contexts[from_name]["gram_rows"] if row["source_role"] == role and row["beta"] == beta)
                right = next(row for row in contexts[to_name]["gram_rows"] if row["source_role"] == role and row["beta"] == beta)
                left_matrix = np.asarray(left["matrix_real"]) + 1j * np.asarray(left["matrix_imag"])
                right_matrix = np.asarray(right["matrix_real"]) + 1j * np.asarray(right["matrix_imag"])
                gram_delta = np.abs(right_matrix - left_matrix)
                left_thermal = sorted((row for row in contexts[from_name]["thermal_rows"] if row["source_role"] == role and row["beta"] == beta), key=lambda row: row["fraction"])
                right_thermal = sorted((row for row in contexts[to_name]["thermal_rows"] if row["source_role"] == role and row["beta"] == beta), key=lambda row: row["fraction"])
                thermal_delta: list[float] = []
                for one, two in zip(left_thermal, right_thermal):
                    thermal_delta.extend([float(abs(complex(two["forward_real"], two["forward_imag"]) - complex(one["forward_real"], one["forward_imag"]))), float(abs(complex(two["reverse_real"], two["reverse_imag"]) - complex(one["reverse_real"], one["reverse_imag"])))])
                scale = max(float(np.max(np.abs(left_matrix))), float(np.max(np.abs(right_matrix))), 1e-30)
                thermal_scale = max(*(abs(complex(row["forward_real"], row["forward_imag"])) for row in left_thermal + right_thermal), 1e-30)
                rows.append({"from_graph": from_name, "to_graph": to_name, "source_role": role, "from_site": int(left["source_site"]), "to_site": int(right["source_site"]), "beta": beta, "gram_max_delta": float(np.max(gram_delta)), "gram_frobenius_delta": float(np.linalg.norm(right_matrix - left_matrix)), "gram_relative_max_delta": float(np.max(gram_delta) / scale), "thermal_max_delta": max(thermal_delta), "thermal_relative_max_delta": float(max(thermal_delta) / thermal_scale), "max_context_delta": max(float(np.max(gram_delta)), max(thermal_delta))})
    return rows


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": actual, "expected": expected})

    check("identity", manifest["exploration_id"] == "EXP-001175" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001175/T-054", "provenance")
    check("claim firewall", manifest["claim_bearing"] is False and not scope["volume_uniform_os_cauchy_closed"], [manifest["claim_bearing"], scope["volume_uniform_os_cauchy_closed"]], "nonbearing/open", "scope")
    check("graph order", list(fixture["graphs"]) == ["path4", "path5", "path6"], list(fixture["graphs"]), "path4/path5/path6", "fixture")
    check("source roles", all(declaration["source_roles"] == ["endpoint_left", "center", "endpoint_right"] for declaration in fixture["graphs"].values()), fixture["graphs"], "three physical roles", "fixture")
    check("dimension", int(fixture["oscillator_dimension"]) == 3, fixture["oscillator_dimension"], 3, "nondegenerate d=3")
    check("scope firewall", scope["finite_q3_transfer_closed"] and scope["finite_os_gram_closed"] and scope["finite_thermal_cyclicity_closed"] and scope["source_role_coverage_closed"] and scope["direction_context_comparison_closed"] and not scope["source_uniform_common_word_closed"] and not scope["volume_uniform_os_cauchy_closed"] and not scope["two_orientation_common_alpha_closed"] and not scope["pre_a_closed"], scope, "finite direction/source comparison", "scope")

    contexts: dict[str, dict[str, Any]] = {}
    for name, declaration in fixture["graphs"].items():
        contexts[name] = make_context(name, declaration, fixture, manifest["model_parameters"])
        context = contexts[name]
        check(f"{name} noncommutation", context["noncommutation"] >= float(fixture.get("noncommutation_witness_floor", 1e-6)), context["noncommutation"], "positive Q3 witness", "nondegenerate Q3")
        check(f"{name} role coverage", len(context["gram_rows"]) == len(fixture["beta_values"]) * len(declaration["source_roles"]), len(context["gram_rows"]), len(fixture["beta_values"]) * len(declaration["source_roles"]), "coverage")
        check(f"{name} thermal coverage", len(context["thermal_rows"]) == len(fixture["beta_values"]) * len(declaration["source_roles"]) * len(fixture["cyclicity_fractions"]), len(context["thermal_rows"]), len(fixture["beta_values"]) * len(declaration["source_roles"]) * len(fixture["cyclicity_fractions"]), "coverage")
        for row in context["gram_rows"]:
            check(f"{name} role={row['source_role']} beta={row['beta']} Gram finite", np.all(np.isfinite(row["matrix_real"])) and np.all(np.isfinite(row["matrix_imag"])), row["reflection_error"], "finite", "OS Gram")
            check(f"{name} role={row['source_role']} beta={row['beta']} Gram reflection", row["reflection_error"] <= float(fixture["agreement_tolerance"]), row["reflection_error"], f"<={fixture['agreement_tolerance']}", "OS Gram")
            check(f"{name} role={row['source_role']} beta={row['beta']} Gram positive", row["min_eigenvalue"] >= -float(fixture["positive_tolerance"]), row["min_eigenvalue"], f">={-float(fixture['positive_tolerance'])}", "OS Gram")
            check(f"{name} role={row['source_role']} beta={row['beta']} Gram diagonal", row["diagonal_min"] >= float(fixture["positive_diagonal_floor"]), row["diagonal_min"], f">={fixture['positive_diagonal_floor']}", "OS Gram")
        for row in context["thermal_rows"]:
            check(f"{name} role={row['source_role']} beta={row['beta']} KMS finite", np.isfinite(row["cyclicity_residual"]) and np.isfinite(row["witness"]), [row["cyclicity_residual"], row["witness"]], "finite", "thermal KMS")
            check(f"{name} role={row['source_role']} beta={row['beta']} KMS cyclicity", row["cyclicity_residual"] <= float(fixture["finite_tolerance"]), row["cyclicity_residual"], f"<={fixture['finite_tolerance']}", "thermal KMS")

    roles = ["endpoint_left", "center", "endpoint_right"]
    betas = [float(value) for value in fixture["beta_values"]]
    comparisons = compare(contexts, list(fixture["nested_graphs"]), roles, betas)
    check("comparison coverage", len(comparisons) == (len(fixture["nested_graphs"]) - 1) * len(roles) * len(betas), len(comparisons), (len(fixture["nested_graphs"]) - 1) * len(roles) * len(betas), "coverage")
    check("comparison finite", all(np.isfinite(row[key]) for row in comparisons for key in ("gram_max_delta", "gram_frobenius_delta", "gram_relative_max_delta", "thermal_max_delta", "thermal_relative_max_delta", "max_context_delta")), len(comparisons), "finite", "context comparison")
    maximum = max(row["max_context_delta"] for row in comparisons)
    minimum = min(row["max_context_delta"] for row in comparisons)
    check("context sensitivity witness", maximum >= float(fixture["context_witness_floor"]), maximum, f">={fixture['context_witness_floor']}", "adversarial context")
    sequences = {role: [row["max_context_delta"] for row in comparisons if row["source_role"] == role and row["beta"] == betas[0]] for role in roles}
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "independent", "audit_id": "PA-CP1-ST8-Q3LOCK-FINITE-COMMON-WORD-DIRECTION-SOURCE", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "passed": len(checks), "assertion_count": len(checks), "assertions": checks, "contexts": [{key: value for key, value in context.items() if key not in ("gram_rows", "thermal_rows")} for context in contexts.values()], "gram_rows": [row for context in contexts.values() for row in context["gram_rows"]], "thermal_rows": [row for context in contexts.values() for row in context["thermal_rows"]], "comparisons": comparisons, "derived": {"context_count": len(contexts), "role_count": len(roles), "nested_pair_count": len(fixture["nested_graphs"]) - 1, "gram_row_count": sum(len(context["gram_rows"]) for context in contexts.values()), "thermal_row_count": sum(len(context["thermal_rows"]) for context in contexts.values()), "comparison_count": len(comparisons), "min_context_delta": minimum, "max_context_delta": maximum, "beta0_direction_sequences": sequences, "finite_q3_transfer_closed": True, "finite_os_gram_closed": True, "finite_thermal_cyclicity_closed": True, "source_role_coverage_closed": True, "direction_context_comparison_closed": True, "source_uniform_common_word_closed": False, "volume_uniform_os_cauchy_closed": False, "two_orientation_common_alpha_closed": False, "exhaustion_independence_closed": False, "common_alpha_closed": False, "hamiltonian_os_identification_closed": False, "kms_gns_gap_closed": False, "continuum_closed": False, "c6_closed": False, "sector_a_closed": False, "pre_a_closed": False, "no_new_negative_result": True, "no_tier_change": True, "no_pdf": True}, "boundary": scope}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        save_json(args.output if args.output.is_absolute() else ROOT / args.output, payload)
    print(f"INDEPENDENT FINITE-COMMON-WORD-DIRECTION-SOURCE PASS {payload['passed']}/{payload['assertion_count']} contexts={payload['derived']['context_count']} comparisons={payload['derived']['comparison_count']} max_delta={payload['derived']['max_context_delta']:.16g}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

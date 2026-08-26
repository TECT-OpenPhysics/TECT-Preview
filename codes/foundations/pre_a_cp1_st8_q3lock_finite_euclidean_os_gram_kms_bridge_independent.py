#!/usr/bin/env python3
"""Independent finite Q3 Euclidean transfer/OS Gram and thermal KMS audit.

This lane rebuilds the tensor matrices and energy-basis formulas without
importing the primary script.
"""

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
SLUG = "pre-a-cp1-st8-q3lock-finite-euclidean-os-gram-kms-bridge"
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


def bond(left: np.ndarray, right: np.ndarray, params: dict[str, str]) -> np.ndarray:
    difference = left - right
    square = difference @ difference
    c = float(Fraction(params["c"]))
    lam = float(Fraction(params["lambda"]))
    return c * square / 2.0 + lam * square @ (left @ left + right @ right) / 4.0


def terms(edges: list[tuple[int, int]], volume: int, size: int, params: dict[str, str]) -> tuple[list[np.ndarray], np.ndarray, np.ndarray]:
    q, p = oscillator(size)
    identity = np.eye(size, dtype=complex)
    q_ops = [tensor_at(q, site, volume, identity) for site in range(volume)]
    p_ops = [tensor_at(p, site, volume, identity) for site in range(volume)]
    chi, r, g = (float(Fraction(params[key])) for key in ("chi", "r", "g"))
    onsite = [p_op @ p_op / (2.0 * chi) + r * q_op @ q_op / 2.0 + g * q_op @ q_op @ q_op @ q_op / 4.0 for q_op, p_op in zip(q_ops, p_ops)]
    return onsite + [bond(q_ops[left], q_ops[right], params) for left, right in edges], q, p


def character(local: np.ndarray, amplitude: float, hbar: float) -> np.ndarray:
    values, vectors = spectrum(local)
    return (vectors * np.exp(1j * amplitude * values / hbar)) @ vectors.conj().T


def transfer(energies: np.ndarray, seconds: float, hbar: float) -> np.ndarray:
    return np.exp(-seconds * energies / hbar)


def thermal_word(energies: np.ndarray, left: np.ndarray, right: np.ndarray, period: float, seconds: float, z: float, hbar: float) -> complex:
    weights = np.exp(-((period - seconds) * energies[:, None] + seconds * energies[None, :]) / hbar)
    return complex(np.sum(weights * left * right.T) / z)


def validate(declaration: dict[str, Any], volume: int) -> tuple[list[tuple[int, int]], list[int], int, int, float]:
    edges = [tuple(int(value) for value in edge) for edge in declaration["edges"]]
    sources = [int(value) for value in declaration["source_sites"]]
    canonical = [(min(left, right), max(left, right)) for left, right in edges]
    if any(left == right or left < 0 or right < 0 or left >= volume or right >= volume for left, right in edges):
        raise AssertionError(f"invalid edge set: {edges!r}")
    if len(set(canonical)) != len(canonical):
        raise AssertionError(f"duplicate edge set: {edges!r}")
    if sources != list(range(volume)):
        raise AssertionError(f"source coverage: {sources!r}")
    degrees = [0] * volume
    for left, right in edges:
        degrees[left] += 1
        degrees[right] += 1
    return edges, sources, min(degrees), max(degrees), float(sum(degrees) / volume)


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": actual, "expected": expected})

    check("identity", manifest["exploration_id"] == "EXP-001173" and manifest["task_id"] == "T-054", [manifest["exploration_id"], manifest["task_id"]], "EXP-001173/T-054", "provenance")
    check("claim firewall", manifest["claim_bearing"] is False and scope["common_alpha_closed"] is False, [manifest["claim_bearing"], scope["common_alpha_closed"]], "nonbearing/open", "scope")
    size = int(fixture["oscillator_dimension"])
    check("periodic graph names", list(fixture["graphs"]) == ["bond2", "square4", "grid2x3"], list(fixture["graphs"]), "bond2/square4/grid2x3", "fixture")
    check("dimension", size == 3, size, 3, "nondegenerate d=3")
    check("sources", all(declaration["source_sites"] == list(range(int(declaration["vertices"]))) for declaration in fixture["graphs"].values()), fixture["graphs"], "all finite sites", "fixture")
    betas = [float(value) for value in fixture["beta_values"]]
    time_fractions = [float(value) for value in fixture["euclidean_time_fractions"]]
    cyclicity_fractions = [float(value) for value in fixture["cyclicity_fractions"]]
    amplitude = float(fixture["character_amplitude"])
    hbar = float(fixture["hbar"])
    finite_tolerance = float(fixture["finite_tolerance"])
    positive_tolerance = float(fixture["positive_tolerance"])
    agreement_tolerance = float(fixture["agreement_tolerance"])
    diagonal_floor = float(fixture["positive_diagonal_floor"])
    cyclicity_floor = float(fixture["cyclicity_witness_floor"])
    params = manifest["model_parameters"]
    gram_rows: list[dict[str, Any]] = []
    thermal_rows: list[dict[str, Any]] = []
    shape_summaries: list[dict[str, Any]] = []
    kinds = ["q", "p"]

    for graph, declaration in fixture["graphs"].items():
        volume = int(declaration["vertices"])
        edges, sources, degree_min, degree_max, degree_mean = validate(declaration, volume)
        check(f"{graph} edge validity", len(edges) > 0 and degree_min > 0, {"edges": edges, "degree_min": degree_min, "degree_max": degree_max}, "nonempty control", "graph")
        h_terms, q_local, p_local = terms(edges, volume, size, params)
        hamiltonian = hermitian(sum(h_terms, np.zeros_like(h_terms[0])))
        energies, vectors = spectrum(hamiltonian)
        shifted = energies - float(np.min(energies))
        noncommutation = float(np.linalg.norm(hamiltonian @ h_terms[0] - h_terms[0] @ hamiltonian, ord=2))
        check(f"{graph} noncommutation", noncommutation >= float(fixture.get("noncommutation_witness_floor", 1e-6)), noncommutation, "positive Q3 witness", "nondegenerate Q3")
        identity = np.eye(size, dtype=complex)
        local = {site: {"q": tensor_at(character(q_local, amplitude, hbar), site, volume, identity), "p": tensor_at(character(p_local, amplitude, hbar), site, volume, identity)} for site in sources}
        in_basis = {site: {kind: vectors.conj().T @ local[site][kind] @ vectors for kind in kinds} for site in sources}

        for beta in betas:
            period = beta * hbar
            weights = transfer(shifted, period / hbar, 1.0)
            z = float(np.sum(weights))
            check(f"{graph} beta={beta} partition", np.isfinite(z) and z > 0.0, z, ">0 finite", "Euclidean transfer")
            tau_values = [fraction * period for fraction in time_fractions]
            for site in sources:
                fs: list[np.ndarray] = []
                descriptors: list[dict[str, Any]] = []
                for tau in tau_values:
                    for kind in kinds:
                        op = in_basis[site][kind]
                        fs.append(transfer(shifted, period / 2.0 - tau, hbar)[:, None] * op * transfer(shifted, tau, hbar)[None, :])
                        descriptors.append({"tau": tau, "kind": kind})
                gram = np.array([[np.vdot(one, two) / z for two in fs] for one in fs], dtype=complex)
                gram = (gram + gram.conj().T) / 2.0
                reflected = np.zeros_like(gram)
                for i, first in enumerate(descriptors):
                    for j, second in enumerate(descriptors):
                        first_op = in_basis[site][first["kind"]]
                        second_op = in_basis[site][second["kind"]]
                        exponents = np.exp(-((period - first["tau"] - second["tau"]) * shifted[:, None] + (first["tau"] + second["tau"]) * shifted[None, :]) / hbar)
                        reflected[i, j] = np.sum(exponents * first_op.conj() * second_op) / z
                error = float(np.max(np.abs(gram - (reflected + reflected.conj().T) / 2.0)))
                eigenvalues = np.linalg.eigvalsh(gram)
                minimum = float(np.min(eigenvalues))
                diagonal = float(np.min(np.real(np.diag(gram))))
                check(f"{graph} site={site} beta={beta} Gram finite", np.all(np.isfinite(gram.real)) and np.all(np.isfinite(gram.imag)), error, "finite", "OS Gram")
                check(f"{graph} site={site} beta={beta} Gram reflection", error <= agreement_tolerance, error, f"<={agreement_tolerance}", "OS Gram")
                check(f"{graph} site={site} beta={beta} Gram positive", minimum >= -positive_tolerance, minimum, f">={-positive_tolerance}", "OS Gram")
                check(f"{graph} site={site} beta={beta} Gram diagonal", diagonal >= diagonal_floor, diagonal, f">={diagonal_floor}", "OS Gram")
                gram_rows.append({"graph": graph, "volume": volume, "source_site": int(site), "beta": beta, "vector_count": len(fs), "min_eigenvalue": minimum, "max_eigenvalue": float(np.max(eigenvalues)), "diagonal_min": diagonal, "reflection_error": error})
                for fraction in cyclicity_fractions:
                    seconds = fraction * period
                    a_obs, b_obs = in_basis[site]["q"], in_basis[site]["p"]
                    forward = thermal_word(shifted, a_obs, b_obs, period, seconds, z, hbar)
                    reverse = thermal_word(shifted, b_obs, a_obs, period, period - seconds, z, hbar)
                    residual = abs(forward - reverse)
                    witness = abs(forward) + abs(reverse)
                    check(f"{graph} site={site} beta={beta} s={seconds} cyclic finite", np.isfinite(residual) and np.isfinite(witness), [residual, witness], "finite", "thermal KMS")
                    check(f"{graph} site={site} beta={beta} s={seconds} cyclicity", residual <= finite_tolerance, residual, f"<={finite_tolerance}", "thermal KMS")
                    check(f"{graph} site={site} beta={beta} s={seconds} cyclic witness", witness >= cyclicity_floor, witness, f">={cyclicity_floor}", "thermal KMS")
                    thermal_rows.append({"graph": graph, "volume": volume, "source_site": int(site), "beta": beta, "seconds": seconds, "fraction": fraction, "forward_real": float(forward.real), "forward_imag": float(forward.imag), "reverse_real": float(reverse.real), "reverse_imag": float(reverse.imag), "cyclicity_residual": float(residual), "witness": float(witness)})

        graph_grams = [row for row in gram_rows if row["graph"] == graph]
        graph_thermal = [row for row in thermal_rows if row["graph"] == graph]
        shape_summaries.append({"graph": graph, "volume": volume, "edge_count": len(edges), "degree_min": degree_min, "degree_max": degree_max, "degree_mean": degree_mean, "source_count": len(sources), "min_gram_eigenvalue": min(row["min_eigenvalue"] for row in graph_grams), "max_gram_reflection_error": max(row["reflection_error"] for row in graph_grams), "min_gram_diagonal": min(row["diagonal_min"] for row in graph_grams), "max_cyclicity_residual": max(row["cyclicity_residual"] for row in graph_thermal), "min_cyclicity_witness": min(row["witness"] for row in graph_thermal)})

    source_count = sum(len(declaration["source_sites"]) for declaration in fixture["graphs"].values())
    expected_gram = source_count * len(betas)
    expected_thermal = source_count * len(betas) * len(cyclicity_fractions)
    check("Gram coverage", len(gram_rows) == expected_gram, len(gram_rows), expected_gram, "coverage")
    check("thermal coverage", len(thermal_rows) == expected_thermal, len(thermal_rows), expected_thermal, "coverage")
    check("shape coverage", len(shape_summaries) == len(fixture["graphs"]), len(shape_summaries), len(fixture["graphs"]), "coverage")
    check("all rows finite", all(np.isfinite(row[key]) for row in gram_rows for key in ("min_eigenvalue", "max_eigenvalue", "diagonal_min", "reflection_error")) and all(np.isfinite(row[key]) for row in thermal_rows for key in ("cyclicity_residual", "witness")), len(gram_rows) + len(thermal_rows), "finite", "numerics")
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "independent",
        "audit_id": "PA-CP1-ST8-Q3LOCK-FINITE-EUCLIDEAN-OS-GRAM-KMS-BRIDGE",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": len(checks),
        "assertion_count": len(checks),
        "assertions": checks,
        "gram_rows": gram_rows,
        "thermal_rows": thermal_rows,
        "shape_summaries": shape_summaries,
        "derived": {
            "gram_row_count": len(gram_rows),
            "thermal_row_count": len(thermal_rows),
            "shape_count": len(shape_summaries),
            "finite_q3_euclidean_transfer_closed": True,
            "finite_os_reflection_gram_closed": True,
            "finite_thermal_cyclicity_closed": True,
            "all_source_sites_closed": True,
            "shape_degree_diagnostic_closed": True,
            "min_gram_eigenvalue": min(row["min_eigenvalue"] for row in gram_rows),
            "max_gram_reflection_error": max(row["reflection_error"] for row in gram_rows),
            "max_cyclicity_residual": max(row["cyclicity_residual"] for row in thermal_rows),
            "finite_to_os_intertwiner_closed": False,
            "source_uniform_direct_d_cauchy_closed": False,
            "volume_uniform_direct_d_cauchy_closed": False,
            "beta_uniform_direct_d_cauchy_closed": False,
            "product_core_density_closed": False,
            "exhaustion_independence_closed": False,
            "group_law_closed": False,
            "common_alpha_closed": False,
            "hamiltonian_os_identification_closed": False,
            "kms_gns_gap_closed": False,
            "continuum_closed": False,
            "c6_closed": False,
            "sector_a_closed": False,
            "pre_a_closed": False,
            "no_new_negative_result": True,
            "no_tier_change": True,
            "no_pdf": True
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
        save_json(args.output if args.output.is_absolute() else ROOT / args.output, payload)
    print(f"INDEPENDENT FINITE-EUCLIDEAN-OS-GRAM-KMS-BRIDGE PASS {payload['passed']}/{payload['assertion_count']} gram_rows={payload['derived']['gram_row_count']} thermal_rows={payload['derived']['thermal_row_count']} shapes={payload['derived']['shape_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

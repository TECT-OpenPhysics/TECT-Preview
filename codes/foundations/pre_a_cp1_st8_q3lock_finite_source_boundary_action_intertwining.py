#!/usr/bin/env python3
"""Finite Q3 source-boundary/action-intertwining audit for EXP-001183.

The audit compares exact finite-volume real-time actions on nested path
graphs, verifies the source-separated commutator tangent, and checks the
finite Duhamel variation identity against a direct matrix difference.  It
also records normalized Euclidean source-word mismatches.  Every conclusion
is finite-dimensional and claim-nonbearing.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

import numpy as np


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-st8-q3lock-finite-source-boundary-action-intertwining"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
LEAN = REPO / "verification/lean/Tect/R343.lean"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-26-primary-{SLUG}" / "primary.json"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pre_a_cp1_st8_q3lock_finite_euclidean_os_gram_kms_bridge as model  # noqa: E402
import pre_a_cp1_st8_q3lock_finite_split_gibbs_kms_residual as base  # noqa: E402


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


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


def commutator(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    return left @ right - right @ left


def hermitian(matrix: np.ndarray) -> np.ndarray:
    return (matrix + matrix.conj().T) / 2.0


def finite_state(declaration: dict[str, Any], dimension: int, parameters: dict[str, str]) -> dict[str, Any]:
    volume = int(declaration["vertices"])
    edges = [tuple(int(value) for value in edge) for edge in declaration["edges"]]
    terms, q_single, p_single = model.periodic_terms(edges, volume, dimension, parameters)
    hamiltonian = hermitian(sum(terms, np.zeros_like(terms[0])))
    energies, vectors = base.eigensystem(hamiltonian)
    shifted = energies - float(np.min(energies))
    identity = np.eye(dimension, dtype=complex)
    return {
        "volume": volume,
        "dimension": int(dimension**volume),
        "edges": edges,
        "hamiltonian": hamiltonian,
        "energies": shifted,
        "vectors": vectors,
        "q_single": q_single,
        "p_single": p_single,
        "identity_single": identity,
    }


def observable(state: dict[str, Any], kind: str, amplitude: float, hbar: float) -> np.ndarray:
    generator = state["q_single"] if kind == "q" else state["p_single"]
    single = base.character(generator, amplitude, hbar)
    return base.embed(single, 0, state["volume"], state["identity_single"])


def extension_identity(small: dict[str, Any], large: dict[str, Any]) -> np.ndarray:
    factor = large["dimension"] // small["dimension"]
    if factor <= 0 or large["dimension"] != small["dimension"] * factor:
        raise AssertionError("nested dimensions are not an identity extension")
    return np.eye(factor, dtype=complex)


def embed_extension(operator: np.ndarray, identity_extension: np.ndarray) -> np.ndarray:
    return np.kron(operator, identity_extension)


def heisenberg(eigenvalues: np.ndarray, eigenvectors: np.ndarray, seconds: float, operator: np.ndarray, hbar: float) -> np.ndarray:
    basis = eigenvectors.conj().T @ operator @ eigenvectors
    phase = np.exp(1j * seconds * eigenvalues / hbar)
    evolved_basis = phase[:, None] * basis * phase.conj()[None, :]
    return eigenvectors @ evolved_basis @ eigenvectors.conj().T


def interpolation_spectra(h0: np.ndarray, delta: np.ndarray, order: int) -> list[tuple[float, float, np.ndarray, np.ndarray]]:
    nodes, weights = np.polynomial.legendre.leggauss(order)
    result: list[tuple[float, float, np.ndarray, np.ndarray]] = []
    for node, weight in zip(nodes, weights):
        parameter = (float(node) + 1.0) / 2.0
        values, vectors = np.linalg.eigh(hermitian(h0 + parameter * delta))
        result.append((parameter, float(weight) / 2.0, values, vectors))
    return result


def interval_nodes(upper: float, order: int) -> list[tuple[float, float]]:
    nodes, weights = np.polynomial.legendre.leggauss(order)
    return [((float(node) + 1.0) * upper / 2.0, float(weight) * upper / 2.0) for node, weight in zip(nodes, weights)]


def direct_action_difference(
    small: dict[str, Any],
    large: dict[str, Any],
    identity_extension: np.ndarray,
    operator_small: np.ndarray,
    operator_large: np.ndarray,
    seconds: float,
    hbar: float,
) -> np.ndarray:
    large_action = heisenberg(large["energies"], large["vectors"], seconds, operator_large, hbar)
    small_action = heisenberg(small["energies"], small["vectors"], seconds, operator_small, hbar)
    return large_action - embed_extension(small_action, identity_extension)


def duhamel_action_difference(
    h0: np.ndarray,
    delta: np.ndarray,
    operator_large: np.ndarray,
    seconds: float,
    hbar: float,
    spectra: list[tuple[float, float, np.ndarray, np.ndarray]],
    u_order: int,
) -> np.ndarray:
    if seconds == 0.0:
        return np.zeros_like(operator_large)
    integral = np.zeros_like(operator_large)
    for _parameter, s_weight, values, vectors in spectra:
        inner = np.zeros_like(operator_large)
        for u, u_weight in interval_nodes(seconds, u_order):
            at_t_minus_u = heisenberg(values, vectors, seconds - u, operator_large, hbar)
            boundary_commutator = commutator(delta, at_t_minus_u)
            inner += u_weight * heisenberg(values, vectors, u, boundary_commutator, hbar)
        integral += s_weight * inner
    return 1j * integral / hbar


def euclidean_word(state: dict[str, Any], beta: float, tau_fraction: float, operator: np.ndarray, hbar: float) -> tuple[np.ndarray, float]:
    period = beta * hbar
    tau = tau_fraction * period
    transfer = lambda seconds: (state["vectors"] * np.exp(-seconds * state["energies"] / hbar)) @ state["vectors"].conj().T
    partition = float(np.sum(np.exp(-beta * state["energies"] / hbar)))
    if partition <= 0.0 or not np.isfinite(partition):
        raise AssertionError("invalid finite partition function")
    word = transfer(period / 2.0 - tau) @ operator @ transfer(tau)
    return word / np.sqrt(partition), partition


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": actual, "expected": expected})

    check("identity", (manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"]) == ("EXP-001183", "T-054", False), [manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"]], "EXP-001183/T-054/false", "provenance")
    check("graph fixture", list(fixture["graphs"]) == ["path2", "path3", "path4"], list(fixture["graphs"]), "path2/path3/path4", "fixture")
    check("nested fixture", fixture["nested_pairs"] == [["path2", "path3"], ["path3", "path4"]], fixture["nested_pairs"], "declared nested path pairs", "fixture")
    check("dimension fixture", int(fixture["oscillator_dimension"]) == 3, fixture["oscillator_dimension"], 3, "finite oscillator")
    check("scope firewall", scope["finite_source_boundary_commutator_zero_closed"] and scope["finite_duhamel_action_intertwining_identity_closed"] and scope["finite_euclidean_source_boundary_diagnostic_closed"] and not scope["source_volume_cutoff_beta_uniform_closed"] and not scope["common_alpha_closed"] and not scope["pre_a_closed"], scope, "finite source-boundary diagnostic", "scope")

    dimension = int(fixture["oscillator_dimension"])
    hbar = float(fixture["hbar"])
    amplitude = float(fixture["character_amplitude"])
    parameters = manifest["model_parameters"]
    commutator_tolerance = float(fixture["commutator_zero_tolerance"])
    duhamel_tolerance = float(fixture["duhamel_tolerance"])
    finite_tolerance = float(fixture["finite_tolerance"])
    order_floor = float(fixture["order_witness_floor"])
    states = {name: finite_state(declaration, dimension, parameters) for name, declaration in fixture["graphs"].items()}
    source_boundary_rows: list[dict[str, Any]] = []
    order_rows: list[dict[str, Any]] = []
    action_rows: list[dict[str, Any]] = []
    os_rows: list[dict[str, Any]] = []

    for small_name, large_name in fixture["nested_pairs"]:
        small, large = states[small_name], states[large_name]
        identity_extension = extension_identity(small, large)
        h0 = embed_extension(small["hamiltonian"], identity_extension)
        delta = hermitian(large["hamiltonian"] - h0)
        distance = int(small["volume"] - 1)
        spectra = interpolation_spectra(h0, delta, int(fixture["quadrature_s_order"]))
        check(f"{small_name}->{large_name} nested dimensions", large["dimension"] == small["dimension"] * identity_extension.shape[0], [small["dimension"], large["dimension"], identity_extension.shape[0]], "identity extension", "embedding")
        check(f"{small_name}->{large_name} boundary finite", np.all(np.isfinite(delta.real)) and np.all(np.isfinite(delta.imag)), float(np.linalg.norm(delta, ord="fro")), "finite", "boundary")
        boundary_commutators: list[float] = []
        first_orders: list[int] = []
        for kind in fixture["observable_kinds"]:
            operator_small = observable(small, kind, amplitude, hbar)
            operator_large = observable(large, kind, amplitude, hbar)
            source_commutator = commutator(delta, operator_large)
            source_commutator_norm = float(np.linalg.norm(source_commutator, ord="fro"))
            boundary_commutators.append(source_commutator_norm)
            check(f"{small_name}->{large_name} {kind} source-boundary tangent", source_commutator_norm <= commutator_tolerance, source_commutator_norm, f"<={commutator_tolerance}", "source tangent")
            current_large = operator_large.copy()
            current_small = embed_extension(operator_small, identity_extension)
            commutator_norms: list[float] = []
            for order in range(1, int(fixture["max_commutator_order"]) + 1):
                current_large = commutator(large["hamiltonian"], current_large)
                current_small = commutator(h0, current_small)
                difference_norm = float(np.linalg.norm(current_large - current_small, ord="fro"))
                commutator_norms.append(difference_norm)
                order_rows.append({"small_graph": small_name, "large_graph": large_name, "kind": kind, "order": order, "distance": distance, "difference_frobenius": difference_norm})
            nonzero = [index + 1 for index, value in enumerate(commutator_norms) if value > order_floor]
            first_order = nonzero[0] if nonzero else None
            check(f"{small_name}->{large_name} {kind} first propagation order", first_order is None or first_order >= distance + 1, first_order, f">={distance + 1} when observed within cutoff", "source distance")
            first_orders.append(int(first_order) if first_order is not None else -1)
            for seconds in (float(value) for value in fixture["real_time_values"]):
                direct = direct_action_difference(small, large, identity_extension, operator_small, operator_large, seconds, hbar)
                reconstructed = duhamel_action_difference(h0, delta, operator_large, seconds, hbar, spectra, int(fixture["quadrature_u_order"]))
                direct_norm = float(np.linalg.norm(direct, ord="fro"))
                reconstructed_norm = float(np.linalg.norm(reconstructed, ord="fro"))
                residual = float(np.linalg.norm(direct - reconstructed, ord="fro"))
                action_scale = max(float(np.linalg.norm(operator_large, ord="fro")), float(fixture["positive_partition_floor"]))
                action_rows.append({"small_graph": small_name, "large_graph": large_name, "kind": kind, "seconds": seconds, "direct_defect_frobenius": direct_norm, "direct_defect_relative": direct_norm / action_scale, "duhamel_reconstruction_frobenius": reconstructed_norm, "duhamel_residual_frobenius": residual, "duhamel_residual_relative": residual / action_scale})
                check(f"{small_name}->{large_name} {kind} t={seconds} Duhamel identity", residual <= duhamel_tolerance + finite_tolerance * max(1.0, direct_norm), residual, f"<={duhamel_tolerance}+scaled", "Duhamel")
        source_boundary_rows.append({"small_graph": small_name, "large_graph": large_name, "boundary_distance": distance, "boundary_frobenius": float(np.linalg.norm(delta, ord="fro")), "q_source_commutator": boundary_commutators[0], "p_source_commutator": boundary_commutators[1], "first_nonzero_orders": first_orders})

        for beta in (float(value) for value in fixture["beta_values"]):
            for tau_fraction in (float(value) for value in fixture["euclidean_time_fractions"]):
                for kind in fixture["observable_kinds"]:
                    small_operator = observable(small, kind, amplitude, hbar)
                    large_operator = observable(large, kind, amplitude, hbar)
                    small_word, z_small = euclidean_word(small, beta, tau_fraction, small_operator, hbar)
                    large_word, z_large = euclidean_word(large, beta, tau_fraction, large_operator, hbar)
                    defect = large_word - embed_extension(small_word, identity_extension)
                    defect_norm = float(np.linalg.norm(defect, ord="fro"))
                    scale = max(float(np.linalg.norm(large_word, ord="fro")), float(np.linalg.norm(embed_extension(small_word, identity_extension), ord="fro")), float(fixture["positive_partition_floor"]))
                    os_rows.append({"small_graph": small_name, "large_graph": large_name, "kind": kind, "beta": beta, "tau_fraction": tau_fraction, "partition_small": z_small, "partition_large": z_large, "defect_frobenius": defect_norm, "defect_relative": defect_norm / scale})
                    check(f"{small_name}->{large_name} {kind} beta={beta} tau={tau_fraction} OS finite", np.isfinite(defect_norm) and z_small > float(fixture["positive_partition_floor"]) and z_large > float(fixture["positive_partition_floor"]), [defect_norm, z_small, z_large], "finite and positive", "OS source boundary")

    check("source boundary coverage", len(source_boundary_rows) == len(fixture["nested_pairs"]), len(source_boundary_rows), len(fixture["nested_pairs"]), "coverage")
    check("order coverage", len(order_rows) == len(fixture["nested_pairs"]) * len(fixture["observable_kinds"]) * int(fixture["max_commutator_order"]), len(order_rows), len(fixture["nested_pairs"]) * len(fixture["observable_kinds"]) * int(fixture["max_commutator_order"]), "coverage")
    check("action coverage", len(action_rows) == len(fixture["nested_pairs"]) * len(fixture["observable_kinds"]) * len(fixture["real_time_values"]), len(action_rows), len(fixture["nested_pairs"]) * len(fixture["observable_kinds"]) * len(fixture["real_time_values"]), "coverage")
    check("OS coverage", len(os_rows) == len(fixture["nested_pairs"]) * len(fixture["observable_kinds"]) * len(fixture["beta_values"]) * len(fixture["euclidean_time_fractions"]), len(os_rows), len(fixture["nested_pairs"]) * len(fixture["observable_kinds"]) * len(fixture["beta_values"]) * len(fixture["euclidean_time_fractions"]), "coverage")
    check("nonzero action witness", max(row["direct_defect_relative"] for row in action_rows) > order_floor, max(row["direct_defect_relative"] for row in action_rows), f">{order_floor}", "route diagnostic")
    check("nonzero OS witness", max(row["defect_relative"] for row in os_rows) > order_floor, max(row["defect_relative"] for row in os_rows), f">{order_floor}", "route diagnostic")
    check("all numerical rows finite", all(np.isfinite(float(row[key])) for row in action_rows for key in ("direct_defect_frobenius", "direct_defect_relative", "duhamel_residual_frobenius", "duhamel_residual_relative")) and all(np.isfinite(float(row[key])) for row in os_rows for key in ("defect_frobenius", "defect_relative", "partition_small", "partition_large")), len(action_rows) + len(os_rows), "finite", "numerics")
    downstream = ("source_volume_cutoff_beta_uniform_closed", "word_product_star_action_intertwining_closed", "common_os_hilbert_carrier_closed", "common_word_exhaustion_closed", "direct_d_delta_d_cauchy_closed", "common_alpha_closed", "hamiltonian_os_identification_closed", "kms_gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed")
    check("downstream QFT firewall", all(not scope[field] for field in downstream), {field: scope[field] for field in downstream}, "all downstream QFT gates open", "scope")
    return {
        "schema": "tect/foundation-audit/1.0",
        "run_kind": "primary",
        "audit_id": "PA-CP1-ST8-Q3LOCK-FINITE-SOURCE-BOUNDARY-ACTION-INTERTWINING",
        "claim_id": manifest["claim_ids"][0],
        "task_id": manifest["task_id"],
        "exploration_id": manifest["exploration_id"],
        "verdict": "PASS",
        "passed": len(checks),
        "assertion_count": len(checks),
        "assertions": checks,
        "source_boundary_rows": source_boundary_rows,
        "order_rows": order_rows,
        "action_rows": action_rows,
        "os_rows": os_rows,
        "scope": scope,
        "boundary": manifest["boundary"],
        "derived": {
            "pair_count": len(source_boundary_rows),
            "order_row_count": len(order_rows),
            "action_row_count": len(action_rows),
            "os_row_count": len(os_rows),
            "max_source_commutator": max(max(row["q_source_commutator"], row["p_source_commutator"]) for row in source_boundary_rows),
            "max_action_defect_relative": max(row["direct_defect_relative"] for row in action_rows),
            "max_duhamel_residual_relative": max(row["duhamel_residual_relative"] for row in action_rows),
            "max_os_defect_relative": max(row["defect_relative"] for row in os_rows),
            "first_nonzero_orders": {f"{row['small_graph']}->{row['large_graph']}": row["first_nonzero_orders"] for row in source_boundary_rows},
            "finite_source_boundary_commutator_zero_closed": True,
            "finite_source_distance_order_diagnostic_closed": True,
            "finite_duhamel_action_intertwining_identity_closed": True,
            "finite_euclidean_source_boundary_diagnostic_closed": True,
            "source_volume_cutoff_beta_uniform_closed": False,
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
        "provenance": {"script": str(Path(__file__).resolve().relative_to(REPO)).replace("\\", "/"), "script_sha256": sha256(Path(__file__).resolve()), "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"), "manifest_sha256": sha256(MANIFEST), "lean": str(LEAN.relative_to(REPO)).replace("\\", "/"), "lean_sha256": sha256(LEAN)}
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"PRIMARY FINITE-SOURCE-BOUNDARY-ACTION-INTERTWINING PASS {payload['passed']}/{payload['assertion_count']} pairs={payload['derived']['pair_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Non-importing independent finite Q3 norm-envelope audit for EXP-001184."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np


REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-st8-q3lock-finite-source-boundary-norm-envelope"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
LEAN = REPO / "verification/lean/Tect/R343.lean"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-26-independent-{SLUG}" / "independent.json"


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


def oscillator(dimension: int) -> tuple[np.ndarray, np.ndarray]:
    lowering = np.zeros((dimension, dimension), dtype=complex)
    for index in range(dimension - 1):
        lowering[index, index + 1] = np.sqrt(index + 1.0)
    raising = lowering.conj().T
    return (lowering + raising) / np.sqrt(2.0), (lowering - raising) / (1j * np.sqrt(2.0))


def embed(single: np.ndarray, site: int, volume: int, identity: np.ndarray) -> np.ndarray:
    factors = [single if index == site else identity for index in range(volume)]
    result = factors[0]
    for factor in factors[1:]:
        result = np.kron(result, factor)
    return result


def hermitian(matrix: np.ndarray) -> np.ndarray:
    return (matrix + matrix.conj().T) / 2.0


def eigensystem(matrix: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    return np.linalg.eigh(hermitian(matrix))


def character(generator: np.ndarray, amplitude: float, hbar: float) -> np.ndarray:
    values, vectors = eigensystem(generator)
    return (vectors * np.exp(1j * amplitude * values / hbar)) @ vectors.conj().T


def bond_term(left: np.ndarray, right: np.ndarray, parameters: dict[str, str]) -> np.ndarray:
    difference = left - right
    square = difference @ difference
    return float(Fraction(parameters["c"])) * square / 2.0 + float(Fraction(parameters["lambda"])) * square @ (left @ left + right @ right) / 4.0


def periodic_terms(edges: list[tuple[int, int]], volume: int, dimension: int, parameters: dict[str, str]) -> tuple[list[np.ndarray], np.ndarray, np.ndarray]:
    q_single, p_single = oscillator(dimension)
    identity = np.eye(dimension, dtype=complex)
    q_ops = [embed(q_single, site, volume, identity) for site in range(volume)]
    p_ops = [embed(p_single, site, volume, identity) for site in range(volume)]
    chi = float(Fraction(parameters["chi"]))
    r = float(Fraction(parameters["r"]))
    g = float(Fraction(parameters["g"]))
    onsite = [p @ p / (2.0 * chi) + r * q @ q / 2.0 + g * q @ q @ q @ q / 4.0 for q, p in zip(q_ops, p_ops)]
    return onsite + [bond_term(q_ops[left], q_ops[right], parameters) for left, right in edges], q_single, p_single


def build_state(declaration: dict[str, Any], dimension: int, parameters: dict[str, str]) -> dict[str, Any]:
    volume = int(declaration["vertices"])
    edges = [tuple(int(value) for value in edge) for edge in declaration["edges"]]
    terms, q_single, p_single = periodic_terms(edges, volume, dimension, parameters)
    hamiltonian = hermitian(sum(terms, np.zeros_like(terms[0])))
    energies, vectors = eigensystem(hamiltonian)
    return {"volume": volume, "dimension": int(dimension**volume), "hamiltonian": hamiltonian, "energies": energies - float(np.min(energies)), "vectors": vectors, "q_single": q_single, "p_single": p_single, "identity_single": np.eye(dimension, dtype=complex)}


def observable(state: dict[str, Any], kind: str, amplitude: float, hbar: float) -> np.ndarray:
    return embed(character(state["q_single"] if kind == "q" else state["p_single"], amplitude, hbar), 0, state["volume"], state["identity_single"])


def commutator(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    return left @ right - right @ left


def operator_norm(matrix: np.ndarray) -> float:
    return float(np.max(np.linalg.svd(matrix, compute_uv=False)))


def heisenberg(values: np.ndarray, vectors: np.ndarray, seconds: float, operator: np.ndarray, hbar: float) -> np.ndarray:
    basis = vectors.conj().T @ operator @ vectors
    phase = np.exp(1j * seconds * values / hbar)
    return vectors @ (phase[:, None] * basis * phase.conj()[None, :]) @ vectors.conj().T


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": actual, "expected": expected})

    source_text = Path(__file__).read_text(encoding="utf-8")
    check("independent implementation", not any(line.lstrip().startswith(("import ", "from ")) and "pre_a_cp1_st8_q3lock_finite_source_boundary_norm_envelope" in line for line in source_text.splitlines()), "non-importing", "no primary import", "independence")
    check("identity", (manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"]) == ("EXP-001184", "T-054", False), [manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"]], "EXP-001184/T-054/false", "provenance")
    check("graph fixture", list(fixture["graphs"]) == ["path2", "path3", "path4"], list(fixture["graphs"]), "path2/path3/path4", "fixture")
    check("nested fixture", fixture["nested_pairs"] == [["path2", "path3"], ["path3", "path4"]], fixture["nested_pairs"], "declared nested path pairs", "fixture")
    check("cutoff fixture", [int(value) for value in fixture["oscillator_dimensions"]] == [2, 3], fixture["oscillator_dimensions"], "dimensions 2 and 3", "fixture")
    check("scope firewall", scope["finite_source_boundary_commutator_zero_closed"] and scope["finite_quadratic_action_norm_envelope_closed"] and scope["finite_cutoff_volume_stress_closed"] and not scope["source_volume_cutoff_beta_uniform_closed"] and not scope["common_alpha_closed"] and not scope["pre_a_closed"], scope, "finite envelope only", "scope")

    hbar = float(fixture["hbar"])
    amplitude = float(fixture["character_amplitude"])
    parameters = manifest["model_parameters"]
    commutator_tolerance = float(fixture["commutator_zero_tolerance"])
    bound_tolerance = float(fixture["bound_tolerance"])
    order_floor = float(fixture["order_witness_floor"])
    floor = float(fixture["positive_partition_floor"])
    action_rows: list[dict[str, Any]] = []
    norm_rows: list[dict[str, Any]] = []
    order_rows: list[dict[str, Any]] = []
    for dimension in (int(value) for value in fixture["oscillator_dimensions"]):
        states = {name: build_state(declaration, dimension, parameters) for name, declaration in fixture["graphs"].items()}
        for small_name, large_name in fixture["nested_pairs"]:
            small, large = states[small_name], states[large_name]
            extension = np.eye(large["dimension"] // small["dimension"], dtype=complex)
            h0 = np.kron(small["hamiltonian"], extension)
            delta = hermitian(large["hamiltonian"] - h0)
            h0_norm, delta_norm = operator_norm(h0), operator_norm(delta)
            distance = int(small["volume"] - 1)
            norm_rows.append({"oscillator_dimension": dimension, "small_graph": small_name, "large_graph": large_name, "h0_operator_norm": h0_norm, "delta_operator_norm": delta_norm, "boundary_distance": distance})
            check(f"d={dimension} {small_name}->{large_name} finite boundary", np.isfinite(h0_norm) and np.isfinite(delta_norm), [h0_norm, delta_norm], "finite", "norm envelope")
            first_orders: list[int] = []
            for kind in fixture["observable_kinds"]:
                operator_small = observable(small, kind, amplitude, hbar)
                operator_large = observable(large, kind, amplitude, hbar)
                operator_size = operator_norm(operator_large)
                source_commutator = operator_norm(commutator(delta, operator_large))
                check(f"d={dimension} {small_name}->{large_name} {kind} tangent", source_commutator <= commutator_tolerance, source_commutator, f"<={commutator_tolerance}", "source commutation")
                current_large, current_small = operator_large.copy(), np.kron(operator_small, extension)
                commutator_norms: list[float] = []
                for order in range(1, int(fixture["max_commutator_order"]) + 1):
                    current_large = commutator(large["hamiltonian"], current_large)
                    current_small = commutator(h0, current_small)
                    difference = operator_norm(current_large - current_small)
                    commutator_norms.append(difference)
                    order_rows.append({"oscillator_dimension": dimension, "small_graph": small_name, "large_graph": large_name, "kind": kind, "order": order, "distance": distance, "difference_operator_norm": difference})
                observed = [index + 1 for index, value in enumerate(commutator_norms) if value > order_floor]
                first_order = observed[0] if observed else None
                check(f"d={dimension} {small_name}->{large_name} {kind} distance lower bound", first_order is None or first_order >= distance + 1, first_order, f">={distance + 1} when observed", "source distance")
                first_orders.append(int(first_order) if first_order is not None else -1)
                coefficient = 2.0 * delta_norm * (h0_norm + delta_norm) * operator_size / (hbar * hbar)
                for seconds in (float(value) for value in fixture["real_time_values"]):
                    direct = heisenberg(large["energies"], large["vectors"], seconds, operator_large, hbar) - np.kron(heisenberg(small["energies"], small["vectors"], seconds, operator_small, hbar), extension)
                    defect = operator_norm(direct)
                    cap = 2.0 * operator_size
                    bound = min(cap, coefficient * seconds * seconds)
                    slack = bound_tolerance * max(1.0, bound, defect)
                    check(f"d={dimension} {small_name}->{large_name} {kind} t={seconds} norm envelope", defect <= bound + slack, [defect, bound], "defect<=bound+slack", "norm envelope")
                    action_rows.append({"oscillator_dimension": dimension, "small_graph": small_name, "large_graph": large_name, "kind": kind, "seconds": seconds, "source_distance": distance, "source_commutator_operator_norm": source_commutator, "operator_norm_A": operator_size, "h0_operator_norm": h0_norm, "delta_operator_norm": delta_norm, "quadratic_coefficient": coefficient, "trivial_cap": cap, "bound": bound, "direct_defect_operator_norm": defect, "bound_slack": slack, "bound_ratio": defect / max(bound, floor)})
            norm_rows[-1]["first_nonzero_orders"] = first_orders

    check("norm-row coverage", len(norm_rows) == len(fixture["oscillator_dimensions"]) * len(fixture["nested_pairs"]), len(norm_rows), len(fixture["oscillator_dimensions"]) * len(fixture["nested_pairs"]), "coverage")
    check("order-row coverage", len(order_rows) == len(fixture["oscillator_dimensions"]) * len(fixture["nested_pairs"]) * len(fixture["observable_kinds"]) * int(fixture["max_commutator_order"]), len(order_rows), len(fixture["oscillator_dimensions"]) * len(fixture["nested_pairs"]) * len(fixture["observable_kinds"]) * int(fixture["max_commutator_order"]), "coverage")
    check("action-row coverage", len(action_rows) == len(fixture["oscillator_dimensions"]) * len(fixture["nested_pairs"]) * len(fixture["observable_kinds"]) * len(fixture["real_time_values"]), len(action_rows), len(fixture["oscillator_dimensions"]) * len(fixture["nested_pairs"]) * len(fixture["observable_kinds"]) * len(fixture["real_time_values"]), "coverage")
    check("nonzero action witness", max(row["direct_defect_operator_norm"] for row in action_rows) > order_floor, max(row["direct_defect_operator_norm"] for row in action_rows), f">{order_floor}", "route diagnostic")
    check("all finite rows", all(np.isfinite(float(row[key])) for row in action_rows for key in ("bound", "direct_defect_operator_norm", "bound_ratio", "quadratic_coefficient")) and all(np.isfinite(float(row[key])) for row in norm_rows for key in ("h0_operator_norm", "delta_operator_norm")), len(action_rows) + len(norm_rows), "finite", "numerics")
    downstream = ("source_volume_cutoff_beta_uniform_closed", "word_product_star_action_intertwining_closed", "common_os_hilbert_carrier_closed", "common_word_exhaustion_closed", "direct_d_delta_d_cauchy_closed", "common_alpha_closed", "hamiltonian_os_identification_closed", "kms_gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed")
    check("downstream QFT firewall", all(not scope[field] for field in downstream), {field: scope[field] for field in downstream}, "all downstream QFT gates open", "scope")
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "independent", "audit_id": "PA-CP1-ST8-Q3LOCK-FINITE-SOURCE-BOUNDARY-NORM-ENVELOPE", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "passed": len(checks), "assertion_count": len(checks), "assertions": checks, "norm_rows": norm_rows, "order_rows": order_rows, "action_rows": action_rows, "scope": scope, "boundary": manifest["boundary"], "derived": {"cutoff_count": len(fixture["oscillator_dimensions"]), "pair_count": len(fixture["nested_pairs"]), "norm_row_count": len(norm_rows), "order_row_count": len(order_rows), "action_row_count": len(action_rows), "max_source_commutator": max(float(row["source_commutator_operator_norm"]) for row in action_rows), "max_action_defect_operator_norm": max(row["direct_defect_operator_norm"] for row in action_rows), "max_bound_ratio": max(row["bound_ratio"] for row in action_rows), "max_quadratic_coefficient": max(row["quadratic_coefficient"] for row in action_rows), "min_quadratic_coefficient": min(row["quadratic_coefficient"] for row in action_rows), "cutoff_volume_norm_rows": norm_rows, "finite_source_boundary_commutator_zero_closed": True, "finite_quadratic_action_norm_envelope_closed": True, "finite_cutoff_volume_stress_closed": True, "finite_source_distance_order_diagnostic_closed": True, "source_volume_cutoff_beta_uniform_closed": False, "common_alpha_closed": False, "hamiltonian_os_identification_closed": False, "kms_gns_gap_closed": False, "continuum_closed": False, "c6_closed": False, "sector_a_closed": False, "pre_a_closed": False, "no_new_negative_result": True, "no_tier_change": True, "no_pdf": True}, "provenance": {"script": str(Path(__file__).resolve().relative_to(REPO)).replace("\\", "/"), "script_sha256": sha256(Path(__file__).resolve()), "manifest": str(MANIFEST.relative_to(REPO)).replace("\\", "/"), "manifest_sha256": sha256(MANIFEST), "lean": str(LEAN.relative_to(REPO)).replace("\\", "/"), "lean_sha256": sha256(LEAN)}}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        atomic_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT FINITE-SOURCE-BOUNDARY-NORM-ENVELOPE PASS {payload['passed']}/{payload['assertion_count']} cutoff={payload['derived']['cutoff_count']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

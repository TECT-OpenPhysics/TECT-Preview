#!/usr/bin/env python3
"""Independent finite Q3 cross-volume tensor-carrier stress test for EXP-001180."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np

REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-st8-q3lock-cross-volume-tensor-carrier"
MANIFEST = REPO / "strategy" / f"{SLUG}-manifest.json"
LEAN = REPO / "verification" / "lean" / "Tect" / "R341.lean"
REGISTRY = REPO / "verification" / "lean" / "registry.json"
DEFAULT_OUTPUT = REPO / "claims" / "C6-SPACETIME-SIGNATURE" / "runs" / f"2026-08-26-independent-{SLUG}" / "independent.json"
MARKER = "normalized_product_sum_lift"


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


def normalized_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")).hexdigest()


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


def character(generator: np.ndarray, amplitude: float, hbar: float) -> np.ndarray:
    values, vectors = np.linalg.eigh(hermitian(generator))
    return (vectors * np.exp(1j * amplitude * values / hbar)) @ vectors.conj().T


def bond(left: np.ndarray, right: np.ndarray, parameters: dict[str, str]) -> np.ndarray:
    difference = left - right
    square = difference @ difference
    coupling = float(Fraction(parameters["c"]))
    lam = float(Fraction(parameters["lambda"]))
    return coupling * square / 2.0 + lam * square @ (left @ left + right @ right) / 4.0


def q3_terms(edges: list[tuple[int, int]], volume: int, size: int, parameters: dict[str, str]) -> tuple[list[np.ndarray], np.ndarray, np.ndarray]:
    q_single, p_single = oscillator(size)
    identity = np.eye(size, dtype=complex)
    q_ops = [tensor_at(q_single, site, volume, identity) for site in range(volume)]
    p_ops = [tensor_at(p_single, site, volume, identity) for site in range(volume)]
    chi, r, g = (float(Fraction(parameters[key])) for key in ("chi", "r", "g"))
    onsite = [p_op @ p_op / (2.0 * chi) + r * q_op @ q_op / 2.0 + g * q_op @ q_op @ q_op @ q_op / 4.0 for q_op, p_op in zip(q_ops, p_ops)]
    return onsite + [bond(q_ops[left], q_ops[right], parameters) for left, right in edges], q_single, p_single


def declarations(path: Path) -> list[str]:
    return re.findall(r"(?m)^\s*(?:theorem|lemma|example)\s+([A-Za-z0-9_]+)", path.read_text(encoding="utf-8"))


def finite_state(declaration: dict[str, Any], dimension: int, parameters: dict[str, str], amplitude: float, hbar: float) -> dict[str, Any]:
    volume = int(declaration["vertices"])
    edges = [tuple(int(value) for value in edge) for edge in declaration["edges"]]
    terms, q_single, p_single = q3_terms(edges, volume, dimension, parameters)
    hamiltonian = hermitian(sum(terms, np.zeros_like(terms[0])))
    energies, eigenvectors = np.linalg.eigh(hamiltonian)
    shifted = energies - float(np.min(energies))
    identity = np.eye(dimension, dtype=complex)
    observables = {
        kind: tensor_at(character(q_single if kind == "q" else p_single, amplitude, hbar), 0, volume, identity)
        for kind in ("q", "p")
    }

    def transfer(seconds: float) -> np.ndarray:
        return eigenvectors @ np.diag(np.exp(-seconds * shifted / hbar)) @ eigenvectors.conj().T

    return {"volume": volume, "dimension": int(dimension**volume), "energies": shifted, "eigenvectors": eigenvectors, "observables": observables, "transfer": transfer}


def expectation(state: dict[str, Any], observable: np.ndarray, beta: float, hbar: float) -> complex:
    weights = np.exp(-beta * state["energies"] / hbar)
    partition = float(np.sum(weights))
    diagonal = np.diag(state["eigenvectors"].conj().T @ observable @ state["eigenvectors"])
    return complex(np.sum(weights * diagonal) / partition)


def run() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture, scope = manifest["finite_fixture"], manifest["scope"]
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": actual, "expected": expected})

    check("identity", (manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"]) == ("EXP-001180", "T-054", False), [manifest["exploration_id"], manifest["task_id"], manifest["claim_bearing"]], "EXP-001180/T-054/false", "provenance")
    check("graph fixture", list(fixture["graphs"]) == ["path2", "path3", "path4"], list(fixture["graphs"]), "path2/path3/path4", "fixture")
    check("nested pairs", fixture["nested_pairs"] == [["path2", "path3"], ["path3", "path4"]], fixture["nested_pairs"], "path2->path3 and path3->path4", "fixture")
    check("scope firewall", scope["finite_q3_nested_transfer_closed"] and scope["finite_tracial_lift_identity_closed"] and not scope["common_os_hilbert_carrier_closed"] and not scope["pre_a_closed"], scope, "finite carrier stress only", "scope")
    check("Lean declarations", declarations(LEAN) == [MARKER], declarations(LEAN), [MARKER], "Lean")
    registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
    matches = [item for item in registry["entrypoints"] if item.get("path") == "verification/lean/Tect/R341.lean"]
    check("registry uniqueness", len(matches) == 1, len(matches), 1, "registry")
    check("registry hash", matches[0]["sha256"] == normalized_sha256(LEAN), matches[0]["sha256"], normalized_sha256(LEAN), "registry")

    dimension = int(fixture["oscillator_dimension"])
    beta_values = [float(value) for value in fixture["beta_values"]]
    tau_fractions = [float(value) for value in fixture["tau_fractions"]]
    amplitude = float(fixture["character_amplitude"])
    hbar = float(fixture["hbar"])
    absolute_tolerance = float(fixture["absolute_tolerance"])
    relative_tolerance = float(fixture["relative_tolerance"])
    partition_floor = float(fixture["positive_partition_floor"])
    witness_floor = float(fixture["witness_floor"])
    parameters = manifest["model_parameters"]
    states = {name: finite_state(declaration, dimension, parameters, amplitude, hbar) for name, declaration in fixture["graphs"].items()}
    rows: list[dict[str, Any]] = []
    algebra_rows: list[dict[str, Any]] = []

    for small_name, large_name in fixture["nested_pairs"]:
        small, large = states[small_name], states[large_name]
        identity = np.eye(dimension, dtype=complex)
        small_dim, large_dim = small["dimension"], large["dimension"]
        check(f"{small_name}->{large_name} dimensions", large_dim == small_dim * dimension, [small_dim, large_dim], f"large={small_dim}*{dimension}", "tensor")
        aq, ap = small["observables"]["q"], small["observables"]["p"]
        jq, jp = np.kron(aq, identity), np.kron(ap, identity)
        sq, sp = jq / np.sqrt(dimension), jp / np.sqrt(dimension)
        tracial_inner_residual = abs(np.vdot(jq, jp) / large_dim - np.vdot(aq, ap) / small_dim)
        raw_hs_inner_residual = abs(np.vdot(sq, sp) - np.vdot(aq, ap))
        j_mult_residual = np.linalg.norm(jq @ jp - np.kron(aq @ ap, identity), ord="fro")
        s_mult_defect = np.linalg.norm(sq @ sp - np.kron(aq @ ap, identity) / np.sqrt(dimension), ord="fro")
        s_vs_target_defect = np.linalg.norm(sq @ sp - np.kron(aq @ ap, identity) / dimension, ord="fro")
        j_norm_dilation_residual = abs(np.linalg.norm(jq, ord="fro") / np.linalg.norm(aq, ord="fro") - np.sqrt(dimension))
        s_norm_isometry_residual = abs(np.linalg.norm(sq, ord="fro") - np.linalg.norm(aq, ord="fro"))
        algebra_rows.append({"small_graph": small_name, "large_graph": large_name, "small_dimension": small_dim, "large_dimension": large_dim, "tracial_inner_residual": float(tracial_inner_residual), "raw_hs_inner_residual": float(raw_hs_inner_residual), "j_multiplication_residual": float(j_mult_residual), "s_multiplication_defect": float(s_mult_defect), "s_vs_scaled_product_defect": float(s_vs_target_defect), "j_norm_dilation_residual": float(j_norm_dilation_residual), "s_norm_isometry_residual": float(s_norm_isometry_residual)})

        for beta in beta_values:
            period = beta * hbar
            small_weights = np.exp(-beta * small["energies"] / hbar)
            large_weights = np.exp(-beta * large["energies"] / hbar)
            z_small, z_large = float(np.sum(small_weights)), float(np.sum(large_weights))
            check(f"{small_name}->{large_name} beta={beta} partitions", z_small > partition_floor and z_large > partition_floor, [z_small, z_large], f">{partition_floor}", "normalization")
            for tau_fraction in tau_fractions:
                tau = tau_fraction * period
                small_left, small_right = small["transfer"](period / 2.0 - tau), small["transfer"](tau)
                large_left, large_right = large["transfer"](period / 2.0 - tau), large["transfer"](tau)
                for kind in ("q", "p"):
                    f_small = small_left @ small["observables"][kind] @ small_right
                    f_large = large_left @ large["observables"][kind] @ large_right
                    j_word = np.kron(f_small, identity)
                    s_word = j_word / np.sqrt(dimension)
                    scale = max(np.linalg.norm(f_large, ord="fro"), np.linalg.norm(j_word, ord="fro"), partition_floor)
                    word_j_relative_defect = np.linalg.norm(f_large - j_word, ord="fro") / scale
                    word_s_relative_defect = np.linalg.norm(f_large - s_word, ord="fro") / scale
                    gibbs_functional_defect = abs(expectation(large, np.kron(small["observables"][kind], identity), beta, hbar) - expectation(small, small["observables"][kind], beta, hbar))
                    gibbs_gram_defect = abs(np.vdot(f_large, f_large) / z_large - np.vdot(f_small, f_small) / z_small)
                    rows.append({"small_graph": small_name, "large_graph": large_name, "small_volume": small["volume"], "large_volume": large["volume"], "beta": beta, "tau_fraction": tau_fraction, "tau": tau, "kind": kind, "partition_small": z_small, "partition_large": z_large, "word_j_relative_defect": float(word_j_relative_defect), "word_s_relative_defect": float(word_s_relative_defect), "gibbs_functional_defect": float(gibbs_functional_defect), "gibbs_gram_defect": float(gibbs_gram_defect), "frob_small": float(np.linalg.norm(f_small, ord="fro")), "frob_large": float(np.linalg.norm(f_large, ord="fro")), "j_word_frob": float(np.linalg.norm(j_word, ord="fro")), "s_word_frob": float(np.linalg.norm(s_word, ord="fro"))})

    expected_rows = len(fixture["nested_pairs"]) * len(beta_values) * len(tau_fractions) * 2
    check("row coverage", len(rows) == expected_rows, len(rows), expected_rows, "coverage")
    check("finite row fields", all(np.isfinite(row[key]) for row in rows for key in ("partition_small", "partition_large", "word_j_relative_defect", "word_s_relative_defect", "gibbs_functional_defect", "gibbs_gram_defect")), len(rows), "all numeric fields finite", "numerics")
    algebra_tolerance = absolute_tolerance + relative_tolerance
    check("J normalized-trace isometry", max(row["tracial_inner_residual"] for row in algebra_rows) <= algebra_tolerance, max(row["tracial_inner_residual"] for row in algebra_rows), algebra_tolerance, "tensor identity")
    check("S raw-Frobenius isometry", max(row["raw_hs_inner_residual"] for row in algebra_rows) <= algebra_tolerance, max(row["raw_hs_inner_residual"] for row in algebra_rows), algebra_tolerance, "tensor identity")
    check("J multiplication", max(row["j_multiplication_residual"] for row in algebra_rows) <= algebra_tolerance, max(row["j_multiplication_residual"] for row in algebra_rows), algebra_tolerance, "algebra lift")
    check("S multiplication witness", min(row["s_multiplication_defect"] for row in algebra_rows) >= witness_floor, min(row["s_multiplication_defect"] for row in algebra_rows), f">={witness_floor}", "algebra lift")
    check("J raw norm dilation", max(row["j_norm_dilation_residual"] for row in algebra_rows) <= algebra_tolerance, max(row["j_norm_dilation_residual"] for row in algebra_rows), algebra_tolerance, "tensor identity")
    check("S raw norm isometry", max(row["s_norm_isometry_residual"] for row in algebra_rows) <= algebra_tolerance, max(row["s_norm_isometry_residual"] for row in algebra_rows), algebra_tolerance, "tensor identity")
    check("OS word defect witness", max(row["word_j_relative_defect"] for row in rows) >= witness_floor and max(row["word_s_relative_defect"] for row in rows) >= witness_floor, [max(row["word_j_relative_defect"] for row in rows), max(row["word_s_relative_defect"] for row in rows)], f">={witness_floor}", "Q3 carrier")
    check("Gibbs compatibility witness", max(row["gibbs_functional_defect"] for row in rows) >= witness_floor and max(row["gibbs_gram_defect"] for row in rows) >= witness_floor, [max(row["gibbs_functional_defect"] for row in rows), max(row["gibbs_gram_defect"] for row in rows)], f">={witness_floor}", "Q3 Gibbs")
    downstream = ("common_os_hilbert_carrier_closed", "source_volume_cutoff_beta_uniform_closed", "common_word_exhaustion_closed", "direct_d_delta_d_cauchy_closed", "common_alpha_closed", "hamiltonian_os_identification_closed", "kms_gns_gap_closed", "continuum_closed", "c6_closed", "sector_a_closed", "pre_a_closed")
    check("scope firewall", all(not scope[field] for field in downstream), {field: scope[field] for field in downstream}, "all downstream QFT gates open", "scope")
    return {"schema": "tect/foundation-audit/1.0", "run_kind": "independent", "audit_id": "PA-CP1-ST8-Q3LOCK-CROSS-VOLUME-TENSOR-CARRIER", "claim_id": manifest["claim_ids"][0], "task_id": manifest["task_id"], "exploration_id": manifest["exploration_id"], "verdict": "PASS", "passed": len(checks), "assertion_count": len(checks), "assertions": checks, "rows": rows, "algebra_rows": algebra_rows, "scope": scope, "boundary": manifest["boundary"], "derived": {"row_count": len(rows), "algebra_row_count": len(algebra_rows), "max_word_j_relative_defect": max(row["word_j_relative_defect"] for row in rows), "max_word_s_relative_defect": max(row["word_s_relative_defect"] for row in rows), "max_gibbs_functional_defect": max(row["gibbs_functional_defect"] for row in rows), "max_gibbs_gram_defect": max(row["gibbs_gram_defect"] for row in rows), "min_s_multiplication_defect": min(row["s_multiplication_defect"] for row in algebra_rows), "lean_marker": MARKER}, "provenance": {"script_sha256": normalized_sha256(Path(__file__)), "manifest_sha256": normalized_sha256(MANIFEST), "lean_sha256": normalized_sha256(LEAN), "registry_sha256": normalized_sha256(REGISTRY)}}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run()
    if not args.self_test:
        save_json(args.output if args.output.is_absolute() else REPO / args.output, payload)
    print(f"INDEPENDENT CROSS-VOLUME-TENSOR-CARRIER PASS {payload['passed']}/{payload['assertion_count']} rows={len(payload['rows'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

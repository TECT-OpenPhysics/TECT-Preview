#!/usr/bin/env python3
"""Decimal precision uplift for the fixed R-428 residual row.

The upstream graph is deliberately frozen as the R-428 double-precision
snapshot.  Decimal arithmetic therefore certifies only the downstream
residual eigensolve for that rounded input; it is not an interval proof for
the original Hamiltonian Gibbs state.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import sys
import tempfile
from decimal import Decimal, InvalidOperation, getcontext
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np


REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-residual-precision-uplift-manifest.json"
R428_MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-residual-basis-conditioning-diagnostic-manifest.json"
R426_MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-high-cutoff-schur-stress-manifest.json"
R419_MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-growing-volume-lyapunov-core-tail-stress-manifest.json"
R416_MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-preconditioned-schur-cutoff-stress-manifest.json"
R402_MODULE = "pre_a_cp1_st8_q3lock_hamiltonian_carre_du_champ_comparison"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-primary-residual_precision_uplift/primary.json"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pre_a_cp1_st8_q3lock_growing_volume_lyapunov_core_tail_stress as r419  # noqa: E402
import pre_a_cp1_st8_q3lock_preconditioned_schur_cutoff_stress as r416  # noqa: E402
import pre_a_cp1_st8_q3lock_hamiltonian_carre_du_champ_comparison as r402  # noqa: E402


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


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def D(value: Any) -> Decimal:
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise AssertionError(f"cannot decimalize value: {value!r}") from exc


def zeros(rows: int, columns: int) -> list[list[Decimal]]:
    return [[Decimal(0) for _ in range(columns)] for _ in range(rows)]


def transpose(matrix: list[list[Decimal]]) -> list[list[Decimal]]:
    return [list(column) for column in zip(*matrix)]


def matmul(left: list[list[Decimal]], right: list[list[Decimal]]) -> list[list[Decimal]]:
    if not left or not right or len(left[0]) != len(right):
        raise AssertionError("incompatible Decimal matrix product")
    right_t = transpose(right)
    return [[sum((left[i][k] * right_t[j][k] for k in range(len(right))), Decimal(0)) for j in range(len(right_t))] for i in range(len(left))]


def dot(left: list[Decimal], right: list[Decimal]) -> Decimal:
    if len(left) != len(right):
        raise AssertionError("incompatible Decimal vector product")
    return sum((x * y for x, y in zip(left, right)), Decimal(0))


def max_abs(matrix: list[list[Decimal]]) -> Decimal:
    return max((abs(value) for row in matrix for value in row), default=Decimal(0))


def vector_max_abs(values: list[Decimal]) -> Decimal:
    return max((abs(value) for value in values), default=Decimal(0))


def row_inputs() -> tuple[np.ndarray, np.ndarray, list[np.ndarray]]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    target = manifest["diagnostic_contract"]["fixed_failure_row"]
    fixture = json.loads(R419_MANIFEST.read_text(encoding="utf-8"))["finite_fixture"]
    volume = int(target["volume"])
    dimension = int(target["cutoff_dimension"])
    beta = float(Fraction(str(target["beta"])))
    _, hamiltonian, _ = r419.r399.split_system(volume, dimension, fixture)
    coordinate_basis = r419.r399.coordinate_basis(dimension, volume)
    log_reference, _, _ = r416.log_coordinate_distribution(hamiltonian, coordinate_basis, beta, dimension, volume)
    order = list(range(volume)) if target["orientation"] == "right" else list(reversed(range(volume)))
    selected: tuple[np.ndarray, float] | None = None
    for index, (weights, minimum_log_row) in enumerate(r416.conditional_rows(log_reference, order, dimension, float(fixture["probability_floor"]))):
        if index == int(target["conditional_row_index"]):
            selected = (np.asarray(weights, dtype=float), float(minimum_log_row))
            break
    if selected is None:
        raise AssertionError("fixed conditional row absent")
    weights, _minimum_log_row = selected
    momentum = r402.coordinate_data(dimension)[2]
    graph = r416.projected_graph(weights, momentum, float(Fraction(str(fixture["chi"]))))
    pi = np.asarray(graph["weights"], dtype=float)
    conductance = np.asarray(graph["conductance"], dtype=float)
    phi = float(np.max(np.log(pi))) - np.log(pi)
    tail_threshold = float(Fraction(str(json.loads(R426_MANIFEST.read_text(encoding="utf-8"))["finite_fixture"]["tail_threshold"])))
    tail = phi >= tail_threshold
    blocks = [np.flatnonzero(~tail), np.flatnonzero(tail)]
    return pi, conductance, blocks


def decimal_operator(pi: list[Decimal], conductance: list[list[Decimal]]) -> list[list[Decimal]]:
    n = len(pi)
    if len(conductance) != n or any(len(row) != n for row in conductance):
        raise AssertionError("conductance shape")
    operator = zeros(n, n)
    for i in range(n):
        diagonal = sum(conductance[i], Decimal(0))
        for j in range(n):
            laplacian = diagonal if i == j else -conductance[i][j]
            operator[i][j] = laplacian / (pi[i] * pi[j]).sqrt()
    return operator


def residual_basis(pi: list[Decimal], blocks: list[np.ndarray], reverse: bool) -> list[list[Decimal]]:
    n = len(pi)
    rows: list[list[Decimal]] = []
    block_order = list(reversed(blocks)) if reverse else list(blocks)
    for block_array in block_order:
        block = [int(index) for index in block_array]
        if len(block) < 2:
            raise AssertionError("residual block has fewer than two entries")
        anchor = block[-1] if reverse else block[0]
        others = [index for index in block if index != anchor]
        for index in others:
            vector = [Decimal(0) for _ in range(n)]
            vector[anchor] = pi[index].sqrt()
            vector[index] = -pi[anchor].sqrt()
            rows.append(vector)
    # Modified Gram-Schmidt in Decimal arithmetic.  The rows are converted to
    # columns only after orthonormalization so block supports remain explicit.
    orthonormal: list[list[Decimal]] = []
    for raw in rows:
        vector = list(raw)
        for basis in orthonormal:
            coefficient = dot(basis, vector)
            vector = [value - coefficient * base for value, base in zip(vector, basis)]
        norm_square = dot(vector, vector)
        if norm_square <= Decimal(0):
            raise AssertionError("dependent Decimal residual vector")
        norm = norm_square.sqrt()
        orthonormal.append([value / norm for value in vector])
    # Return an n by (n-2) column matrix.
    return [list(column) for column in zip(*orthonormal)]


def jacobi_eigenvalues(matrix: list[list[Decimal]], tolerance: Decimal, max_sweeps: int) -> tuple[list[Decimal], int, Decimal]:
    n = len(matrix)
    if n == 0 or any(len(row) != n for row in matrix):
        raise AssertionError("Jacobi input must be square")
    value = [list(row) for row in matrix]
    for sweep in range(1, max_sweeps + 1):
        p, q = 0, 1 if n > 1 else 0
        largest = Decimal(0)
        for i in range(n):
            for j in range(i + 1, n):
                candidate = abs(value[i][j])
                if candidate > largest:
                    largest, p, q = candidate, i, j
        if largest <= tolerance:
            return sorted(value[i][i] for i in range(n)), sweep, largest
        app, aqq, apq = value[p][p], value[q][q], value[p][q]
        tau = (aqq - app) / (Decimal(2) * apq)
        sign = Decimal(1) if tau >= Decimal(0) else Decimal(-1)
        t = sign / (abs(tau) + (Decimal(1) + tau * tau).sqrt())
        c = Decimal(1) / (Decimal(1) + t * t).sqrt()
        s = t * c
        for k in range(n):
            if k in (p, q):
                continue
            akp, akq = value[k][p], value[k][q]
            value[k][p] = value[p][k] = c * akp - s * akq
            value[k][q] = value[q][k] = c * akq + s * akp
        value[p][p] = app - t * apq
        value[q][q] = aqq + t * apq
        value[p][q] = value[q][p] = Decimal(0)
    raise AssertionError("Decimal Jacobi did not converge")


def compression(operator: list[list[Decimal]], basis: list[list[Decimal]]) -> list[list[Decimal]]:
    return matmul(transpose(basis), matmul(operator, basis))


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    target = manifest["diagnostic_contract"]["fixed_failure_row"]
    thresholds = manifest["diagnostic_contract"]["thresholds"]
    precision = int(manifest["precision_contract"]["decimal_precision_digits"])
    getcontext().prec = precision
    pi_float, conductance_float, blocks = row_inputs()
    pi = [D(value) for value in pi_float]
    conductance = [[D(value) for value in row] for row in conductance_float]
    operator = decimal_operator(pi, conductance)
    basis_a = residual_basis(pi, blocks, reverse=False)
    basis_b = residual_basis(pi, blocks, reverse=True)
    residual_a = compression(operator, basis_a)
    residual_b = compression(operator, basis_b)
    tolerance = D(thresholds["jacobi_tolerance"])
    eigen_a, sweeps_a, off_a = jacobi_eigenvalues(residual_a, tolerance, int(manifest["precision_contract"]["jacobi_max_sweeps"]))
    eigen_b, sweeps_b, off_b = jacobi_eigenvalues(residual_b, tolerance, int(manifest["precision_contract"]["jacobi_max_sweeps"]))
    gap_a, gap_b = eigen_a[0], eigen_b[0]
    gap_agreement = abs(gap_a - gap_b)
    r422_reference = D(target["r422_residual_gap"])
    direct_reference = D(target["r426_direct_residual_gap"])
    mismatch_r422 = abs(gap_a - r422_reference)
    mismatch_direct = abs(gap_a - direct_reference)
    comparison_tolerance = D(thresholds["comparison_tolerance"])
    checks: list[dict[str, Any]] = []
    assertion_count = 0

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        nonlocal assertion_count
        assertion_count += 1
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("manifest identity", manifest["result_id"] == "R-429" and manifest["exploration_id"] == "EXP-001274" and manifest["claim_bearing"] is False, [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"]], "R-429/EXP-001274/false", "provenance")
    check("parent hashes", sha256(R428_MANIFEST) == manifest["upstream_authority"]["r428_sha256"] and sha256(R426_MANIFEST) == manifest["upstream_authority"]["r426_sha256"], "hash-pinned R428/R426", "declared SHA-256 values", "authority")
    check("fixed row", [target["volume"], target["cutoff_dimension"], target["beta"], target["orientation"], target["conditional_row_index"]] == [2, 16, "8", "right", 7], [target["volume"], target["cutoff_dimension"], target["beta"], target["orientation"], target["conditional_row_index"]], "V2/d16/beta8/right/row7", "fixture")
    check("positive normalized graph", all(value > Decimal(0) for value in pi) and abs(sum(pi, Decimal(0)) - Decimal(1)) <= D(thresholds["reconstruction_tolerance"]) and max_abs(conductance) >= Decimal(0), [str(min(pi)), str(max(pi)), str(sum(pi, Decimal(0)))], "positive normalized Decimal snapshot", "graph")
    check("reversible conductance", all(conductance[i][j] == conductance[j][i] for i in range(len(pi)) for j in range(len(pi))), "symmetric Decimal conductance", "exact decimal symmetry", "graph")
    check("basis dimensions", basis_a and basis_b and len(basis_a) == len(pi) and len(basis_b) == len(pi) and len(basis_a[0]) == len(pi) - len(blocks) and len(basis_b[0]) == len(pi) - len(blocks), [len(basis_a), len(basis_a[0]), len(basis_b[0])], "16x14", "basis")
    for name, basis in (("anchor", basis_a), ("reversed", basis_b)):
        gram = matmul(transpose(basis), basis)
        gram_error = max_abs([[gram[i][j] - (Decimal(1) if i == j else Decimal(0)) for j in range(len(gram))] for i in range(len(gram))])
        check(f"{name} Decimal orthonormality", gram_error <= tolerance, gram_error, f"<={tolerance}", "basis")
    check("Jacobi convergence", off_a <= tolerance and off_b <= tolerance and sweeps_a <= int(manifest["precision_contract"]["jacobi_max_sweeps"]) and sweeps_b <= int(manifest["precision_contract"]["jacobi_max_sweeps"]), [str(off_a), str(off_b), sweeps_a, sweeps_b], f"offdiag<={tolerance}", "precision")
    check("basis-invariant gap agreement", gap_agreement <= D(thresholds["basis_gap_agreement_tolerance"]), gap_agreement, f"<={thresholds['basis_gap_agreement_tolerance']}", "precision")
    check("rounded-input mismatch exceeds fixed tolerance", mismatch_r422 > comparison_tolerance, mismatch_r422, f">{comparison_tolerance}", "reconstruction")
    check("direct reference remains distinct", mismatch_direct > comparison_tolerance, mismatch_direct, f">{comparison_tolerance}", "reconstruction")
    check("R-426 failure preserved", manifest["scope"]["r426_route_failure_preserved"] is True and manifest["scope"]["residual_reuse_closed"] is False, manifest["scope"], "failure preserved and reuse open", "scope")
    classification = "ROUNDED_INPUT_ALGEBRAIC_BOUNDARY" if mismatch_r422 > comparison_tolerance and gap_agreement <= D(thresholds["basis_gap_agreement_tolerance"]) else "ROUNDED_INPUT_UNRESOLVED"
    check("diagnostic classification", classification == "ROUNDED_INPUT_ALGEBRAIC_BOUNDARY", classification, "ROUNDED_INPUT_ALGEBRAIC_BOUNDARY", "verdict")
    derived = {
        "fixed_row": {"volume": target["volume"], "cutoff_dimension": target["cutoff_dimension"], "beta": target["beta"], "orientation": target["orientation"], "conditional_row_index": target["conditional_row_index"], "core_size": len(blocks[0]), "tail_size": len(blocks[1])},
        "decimal_precision_digits": precision,
        "jacobi_tolerance": str(tolerance),
        "jacobi_sweeps": {"anchor": sweeps_a, "reversed": sweeps_b},
        "jacobi_final_offdiagonal": {"anchor": str(off_a), "reversed": str(off_b)},
        "invariant_gap_decimal": str(gap_a),
        "second_basis_gap_decimal": str(gap_b),
        "basis_gap_agreement_decimal": str(gap_agreement),
        "r422_reference_decimal": str(r422_reference),
        "direct_reference_decimal": str(direct_reference),
        "mismatch_r422_decimal": str(mismatch_r422),
        "mismatch_direct_decimal": str(mismatch_direct),
        "classification": classification,
        "upstream_source_precision_certified": False,
        "exact_original_input_certified": False,
        "residual_reuse_closed": False,
        "r426_route_failure_preserved": True,
    }
    payload: dict[str, Any] = {
        "schema": "tect/pre-a-r429-primary/1.0",
        "manifest": MANIFEST.relative_to(REPO).as_posix(),
        "result_id": manifest["result_id"],
        "exploration_id": manifest["exploration_id"],
        "claim_id": manifest["claim_ids"][0],
        "run_kind": "primary",
        "verdict": classification,
        "assertion_count": assertion_count,
        "assertions": checks,
        "derived": derived,
        "source_hashes": {"primary": sha256(Path(__file__)), "manifest": sha256(MANIFEST), "r428_manifest": sha256(R428_MANIFEST), "r426_manifest": sha256(R426_MANIFEST), "r419_manifest": sha256(R419_MANIFEST), "r416_manifest": sha256(R416_MANIFEST)},
        "assumptions": manifest["assumptions"],
        "missing_assumptions": manifest["missing_assumptions"],
        "evidence_level": manifest["evidence_level"],
        "non_claims": manifest["non_claims"],
        "boundary": manifest["boundary"],
    }
    atomic_json(output, payload)
    print(f"R-429 PRIMARY {classification} {assertion_count}/{assertion_count} gap={gap_a} mismatch={mismatch_r422} basis_agreement={gap_agreement} sweeps={sweeps_a}/{sweeps_b}")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run(args.output if args.output.is_absolute() else REPO / args.output)
    if args.self_test:
        assert payload["verdict"] == "ROUNDED_INPUT_ALGEBRAIC_BOUNDARY"
        assert payload["derived"]["residual_reuse_closed"] is False
        print("R-429 PRIMARY SELFTEST: PASS (80-digit Decimal rounded-input invariant residual)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

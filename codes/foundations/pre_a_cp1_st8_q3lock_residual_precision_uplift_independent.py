#!/usr/bin/env python3
"""Independent Decimal reconstruction for R-429.

This lane does not import the R-429 primary module.  It rebuilds the fixed
row from the upstream finite sources, uses reversed block anchors, and runs a
separate Decimal Jacobi implementation before comparing with R-426.
"""

from __future__ import annotations

import argparse
import hashlib
import json
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
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-independent-residual_precision_uplift/independent.json"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import pre_a_cp1_st8_q3lock_growing_volume_lyapunov_core_tail_stress as r419  # noqa: E402
import pre_a_cp1_st8_q3lock_preconditioned_schur_cutoff_stress as r416  # noqa: E402
import pre_a_cp1_st8_q3lock_hamiltonian_carre_du_champ_comparison as r402  # noqa: E402


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dec(value: Any) -> Decimal:
    try:
        return Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise AssertionError(f"not decimalizable: {value!r}") from exc


def transpose(matrix: list[list[Decimal]]) -> list[list[Decimal]]:
    return [list(column) for column in zip(*matrix)]


def multiply(left: list[list[Decimal]], right: list[list[Decimal]]) -> list[list[Decimal]]:
    right_t = transpose(right)
    return [[sum((left[i][k] * right_t[j][k] for k in range(len(right))), Decimal(0)) for j in range(len(right_t))] for i in range(len(left))]


def inner(left: list[Decimal], right: list[Decimal]) -> Decimal:
    return sum((a * b for a, b in zip(left, right)), Decimal(0))


def max_abs(matrix: list[list[Decimal]]) -> Decimal:
    return max((abs(value) for row in matrix for value in row), default=Decimal(0))


def fixed_row() -> tuple[np.ndarray, np.ndarray, list[np.ndarray]]:
    target = json.loads(MANIFEST.read_text(encoding="utf-8"))["diagnostic_contract"]["fixed_failure_row"]
    fixture = json.loads(R419_MANIFEST.read_text(encoding="utf-8"))["finite_fixture"]
    volume, dimension = int(target["volume"]), int(target["cutoff_dimension"])
    beta = float(Fraction(str(target["beta"])))
    _, hamiltonian, _ = r419.r399.split_system(volume, dimension, fixture)
    coordinate_basis = r419.r399.coordinate_basis(dimension, volume)
    log_reference, _, _ = r416.log_coordinate_distribution(hamiltonian, coordinate_basis, beta, dimension, volume)
    order = list(range(volume)) if target["orientation"] == "right" else list(reversed(range(volume)))
    for index, (row, _minimum_log_row) in enumerate(r416.conditional_rows(log_reference, order, dimension, float(fixture["probability_floor"]))):
        if index == int(target["conditional_row_index"]):
            selected = np.asarray(row, dtype=float)
            break
    else:
        raise AssertionError("fixed row missing")
    momentum = r402.coordinate_data(dimension)[2]
    graph = r416.projected_graph(selected, momentum, float(Fraction(str(fixture["chi"]))))
    pi = np.asarray(graph["weights"], dtype=float)
    conductance = np.asarray(graph["conductance"], dtype=float)
    phi = float(np.max(np.log(pi))) - np.log(pi)
    threshold = float(Fraction(str(json.loads(R426_MANIFEST.read_text(encoding="utf-8"))["finite_fixture"]["tail_threshold"])))
    tail = phi >= threshold
    return pi, conductance, [np.flatnonzero(~tail), np.flatnonzero(tail)]


def operator(pi: list[Decimal], conductance: list[list[Decimal]]) -> list[list[Decimal]]:
    n = len(pi)
    output = [[Decimal(0) for _ in range(n)] for _ in range(n)]
    for i in range(n):
        diagonal = sum(conductance[i], Decimal(0))
        for j in range(n):
            laplacian = diagonal if i == j else -conductance[i][j]
            output[i][j] = laplacian / (pi[i] * pi[j]).sqrt()
    return output


def reversed_basis(pi: list[Decimal], blocks: list[np.ndarray]) -> list[list[Decimal]]:
    n = len(pi)
    vectors: list[list[Decimal]] = []
    for block_array in reversed(blocks):
        block = [int(value) for value in block_array]
        anchor = block[-1]
        for index in block[:-1]:
            vector = [Decimal(0) for _ in range(n)]
            vector[anchor] = pi[index].sqrt()
            vector[index] = -pi[anchor].sqrt()
            vectors.append(vector)
    basis: list[list[Decimal]] = []
    for vector in vectors:
        work = list(vector)
        for previous in basis:
            coefficient = inner(previous, work)
            work = [x - coefficient * y for x, y in zip(work, previous)]
        norm = inner(work, work).sqrt()
        if norm <= Decimal(0):
            raise AssertionError("dependent residual vector")
        basis.append([x / norm for x in work])
    return [list(column) for column in zip(*basis)]


def jacobi(matrix: list[list[Decimal]], tol: Decimal, limit: int) -> tuple[list[Decimal], int, Decimal]:
    n = len(matrix)
    value = [list(row) for row in matrix]
    for sweep in range(1, limit + 1):
        p, q, largest = 0, 1, Decimal(0)
        for i in range(n):
            for j in range(i + 1, n):
                candidate = abs(value[i][j])
                if candidate > largest:
                    largest, p, q = candidate, i, j
        if largest <= tol:
            return sorted(value[i][i] for i in range(n)), sweep, largest
        app, aqq, apq = value[p][p], value[q][q], value[p][q]
        tau = (aqq - app) / (Decimal(2) * apq)
        sign = Decimal(1) if tau >= Decimal(0) else Decimal(-1)
        t = sign / (abs(tau) + (Decimal(1) + tau * tau).sqrt())
        c = Decimal(1) / (Decimal(1) + t * t).sqrt()
        s = t * c
        for k in range(n):
            if k == p or k == q:
                continue
            kp, kq = value[k][p], value[k][q]
            value[k][p] = value[p][k] = c * kp - s * kq
            value[k][q] = value[q][k] = c * kq + s * kp
        value[p][p], value[q][q] = app - t * apq, aqq + t * apq
        value[p][q] = value[q][p] = Decimal(0)
    raise AssertionError("independent Decimal Jacobi did not converge")


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    target = manifest["diagnostic_contract"]["fixed_failure_row"]
    thresholds = manifest["diagnostic_contract"]["thresholds"]
    getcontext().prec = int(manifest["precision_contract"]["decimal_precision_digits"])
    pi_float, conductance_float, blocks = fixed_row()
    pi = [dec(value) for value in pi_float]
    conductance = [[dec(value) for value in row] for row in conductance_float]
    basis = reversed_basis(pi, blocks)
    gram = multiply(transpose(basis), basis)
    gram_error = max_abs([[gram[i][j] - (Decimal(1) if i == j else Decimal(0)) for j in range(len(gram))] for i in range(len(gram))])
    residual = multiply(transpose(basis), multiply(operator(pi, conductance), basis))
    gap, sweeps, off_diagonal = jacobi(residual, dec(thresholds["jacobi_tolerance"]), int(manifest["precision_contract"]["jacobi_max_sweeps"]))
    gap_value = gap[0]
    reference = dec(target["r422_residual_gap"])
    comparison = dec(thresholds["comparison_tolerance"])
    mismatch = abs(gap_value - reference)
    checks = [
        {"name": "manifest identity", "status": "PASS" if manifest["result_id"] == "R-429" and manifest["exploration_id"] == "EXP-001274" and manifest["claim_bearing"] is False else "FAIL", "actual": [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"]], "expected": "R-429/EXP-001274/false"},
        {"name": "fixed row", "status": "PASS" if [target["volume"], target["cutoff_dimension"], target["beta"], target["orientation"], target["conditional_row_index"]] == [2, 16, "8", "right", 7] else "FAIL", "actual": [target["volume"], target["cutoff_dimension"], target["beta"], target["orientation"], target["conditional_row_index"]], "expected": "V2/d16/beta8/right/row7"},
        {"name": "positive Decimal graph", "status": "PASS" if all(value > Decimal(0) for value in pi) and abs(sum(pi, Decimal(0)) - Decimal(1)) <= dec(thresholds["reconstruction_tolerance"]) else "FAIL", "actual": [str(min(pi)), str(max(pi)), str(sum(pi, Decimal(0)))], "expected": "positive normalized"},
        {"name": "reversed basis dimension", "status": "PASS" if len(basis) == len(pi) and len(basis[0]) == len(pi) - len(blocks) else "FAIL", "actual": [len(basis), len(basis[0])], "expected": "16x14"},
        {"name": "reversed basis orthonormal", "status": "PASS" if gram_error <= dec(thresholds["jacobi_tolerance"]) else "FAIL", "actual": str(gram_error), "expected": f"<={thresholds['jacobi_tolerance']}"},
        {"name": "Jacobi converged", "status": "PASS" if off_diagonal <= dec(thresholds["jacobi_tolerance"]) else "FAIL", "actual": [str(off_diagonal), sweeps], "expected": "offdiag below tolerance"},
        {"name": "rounded-input mismatch", "status": "PASS" if mismatch > comparison else "FAIL", "actual": str(mismatch), "expected": f">{comparison}"},
    ]
    if not all(item["status"] == "PASS" for item in checks):
        raise AssertionError(checks)
    payload: dict[str, Any] = {
        "schema": "tect/pre-a-r429-independent/1.0",
        "manifest": MANIFEST.relative_to(REPO).as_posix(),
        "result_id": manifest["result_id"],
        "exploration_id": manifest["exploration_id"],
        "claim_id": manifest["claim_ids"][0],
        "run_kind": "independent",
        "verdict": "PASS",
        "assertion_count": len(checks),
        "assertions": checks,
        "derived": {"fixed_row": {"volume": target["volume"], "cutoff_dimension": target["cutoff_dimension"], "beta": target["beta"], "orientation": target["orientation"], "conditional_row_index": target["conditional_row_index"], "core_size": len(blocks[0]), "tail_size": len(blocks[1])}, "invariant_gap_decimal": str(gap_value), "mismatch_r422_decimal": str(mismatch), "basis_gap_agreement_not_tested": True, "jacobi_sweeps": sweeps, "jacobi_final_offdiagonal": str(off_diagonal), "rounded_input_mismatch_reproduced": True, "residual_reuse_closed": False, "r426_route_failure_preserved": True},
        "source_hashes": {"independent": sha256(Path(__file__)), "manifest": sha256(MANIFEST), "r428_manifest": sha256(R428_MANIFEST), "r426_manifest": sha256(R426_MANIFEST), "r419_manifest": sha256(R419_MANIFEST), "r416_manifest": sha256(R416_MANIFEST)},
        "assumptions": manifest["assumptions"],
        "missing_assumptions": manifest["missing_assumptions"],
        "evidence_level": manifest["evidence_level"],
        "non_claims": manifest["non_claims"],
        "boundary": manifest["boundary"],
        "independence_scope": "reversed-anchor Decimal residual basis and independent Jacobi implementation without importing the R-429 primary module",
    }
    atomic_json(output, payload)
    print(f"R-429 INDEPENDENT PASS {len(checks)}/{len(checks)} gap={gap_value} mismatch={mismatch} sweeps={sweeps}")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    run(args.output if args.output.is_absolute() else REPO / args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

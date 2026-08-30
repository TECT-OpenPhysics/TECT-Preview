#!/usr/bin/env python3
"""Recompute the fixed R-426 source row with arbitrary mpmath precision.

This is intentionally a point-precision audit.  It rebuilds the oscillator,
coordinate basis, volume-two Hamiltonian, Gibbs coordinate masses and graph
without using the R-428 graph snapshot, but it does not provide interval
enclosures for the original input data.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np


REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-source-point-precision-audit-manifest.json"
R429_MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-residual-precision-uplift-manifest.json"
R428_MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-residual-basis-conditioning-diagnostic-manifest.json"
R426_MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-high-cutoff-schur-stress-manifest.json"
R419_MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-growing-volume-lyapunov-core-tail-stress-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-primary-source_point_precision_audit/primary.json"


def _load_mpmath():
    try:
        import mpmath as module
        return module
    except ModuleNotFoundError:
        runtime = REPO / ".tmp/verification-runtime"
        if not runtime.is_dir():
            raise
        sys.path.insert(0, str(runtime))
        import mpmath as module
        return module


mp = _load_mpmath()


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


def eye(n: int) -> Any:
    return mp.eye(n)


def kron(left: Any, right: Any) -> Any:
    output = mp.matrix(left.rows * right.rows, left.cols * right.cols)
    for i in range(left.rows):
        for j in range(left.cols):
            for k in range(right.rows):
                for ell in range(right.cols):
                    output[i * right.rows + k, j * right.cols + ell] = left[i, j] * right[k, ell]
    return output


def real_symmetric(matrix: Any) -> Any:
    output = mp.matrix(matrix.rows, matrix.cols)
    for i in range(matrix.rows):
        for j in range(matrix.cols):
            value = (matrix[i, j] + mp.conj(matrix[j, i])) / 2
            output[i, j] = mp.re(value)
    return output


def oscillator(n: int) -> tuple[Any, Any]:
    annihilation = mp.matrix(n)
    for index in range(n - 1):
        annihilation[index, index + 1] = mp.sqrt(index + 1)
    creation = annihilation.transpose_conj()
    root_two = mp.sqrt(2)
    q = (annihilation + creation) / root_two
    p = (annihilation - creation) / (1j * root_two)
    return q, p


def source_system(volume: int, dimension: int, fixture: dict[str, Any]) -> tuple[Any, Any, Any, Any]:
    q_single, p_single = oscillator(dimension)
    identity = eye(dimension)
    q_ops = [kron(q_single, identity), kron(identity, q_single)]
    p_ops = [kron(p_single, identity), kron(identity, p_single)]
    chi = mp.mpf(str(fixture["chi"]))
    r = mp.mpf(str(fixture["r"]))
    g = mp.mpf(str(fixture["g"]))
    c = mp.mpf(str(fixture["c"]))
    lam = mp.mpf(str(fixture["lambda"]))
    onsite = []
    for q, p in zip(q_ops, p_ops):
        q2 = q * q
        onsite.append(p * p / (2 * chi) + r * q2 / 2 + g * q2 * q2 / 4)
    difference = q_ops[0] - q_ops[1]
    difference2 = difference * difference
    bond = c * difference2 / 2 + lam * difference2 * (q_ops[0] * q_ops[0] + q_ops[1] * q_ops[1]) / 4
    hamiltonian = real_symmetric(onsite[0] + onsite[1] + bond)
    levels, coordinate_vectors = mp.eigsy(q_single)
    coordinate_basis = kron(coordinate_vectors, coordinate_vectors)
    momentum_coordinate = coordinate_vectors.transpose_conj() * p_single * coordinate_vectors
    return hamiltonian, coordinate_basis, momentum_coordinate, levels


def logsumexp(values: list[Any]) -> Any:
    finite = [value for value in values if value != mp.ninf]
    if not finite:
        return mp.ninf
    maximum = max(finite)
    return maximum + mp.log(mp.fsum([mp.exp(value - maximum) for value in finite]))


def coordinate_log_masses(hamiltonian: Any, coordinate_basis: Any, beta: Any) -> list[Any]:
    energies, eigenvectors = mp.eigsy(hamiltonian)
    minimum = energies[0]
    transformed = coordinate_basis.transpose_conj() * eigenvectors
    logs: list[Any] = []
    for row in range(coordinate_basis.rows):
        terms: list[Any] = []
        for column in range(eigenvectors.cols):
            coefficient = abs(transformed[row, column])
            terms.append(mp.ninf if coefficient == 0 else -beta * (energies[column] - minimum) + 2 * mp.log(coefficient))
        logs.append(logsumexp(terms))
    total = logsumexp(logs)
    return [value - total for value in logs]


def conditional_row(logs: list[Any], dimension: int, row_index: int) -> list[Any]:
    if len(logs) != dimension * dimension:
        raise AssertionError("unexpected coordinate mass size")
    parent_log = logsumexp(logs[row_index * dimension : (row_index + 1) * dimension])
    weights = [mp.exp(value - parent_log) for value in logs[row_index * dimension : (row_index + 1) * dimension]]
    total = mp.fsum(weights)
    return [value / total for value in weights]


def projected_graph(weights: list[Any], momentum: Any, chi: Any) -> list[list[Any]]:
    n = len(weights)
    graph = [[mp.mpf(0) for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j:
                value = momentum[i, j]
                graph[i][j] = (weights[i] + weights[j]) * abs(value) ** 2 / (2 * chi)
    return graph


def blocks_from_row(weights: list[Any], threshold: Any) -> list[list[int]]:
    maximum = max(mp.log(value) for value in weights)
    phi = [maximum - mp.log(value) for value in weights]
    tail = [index for index, value in enumerate(phi) if value >= threshold]
    core = [index for index in range(len(weights)) if index not in set(tail)]
    return [core, tail]


def residual_basis(weights: list[Any], blocks: list[list[int]]) -> list[list[Any]]:
    n = len(weights)
    vectors: list[list[Any]] = []
    for block in blocks:
        anchor = block[0]
        for index in block[1:]:
            vector = [mp.mpf(0) for _ in range(n)]
            vector[anchor] = mp.sqrt(weights[index])
            vector[index] = -mp.sqrt(weights[anchor])
            vectors.append(vector)
    basis: list[list[Any]] = []
    for vector in vectors:
        work = list(vector)
        for previous in basis:
            coefficient = mp.fsum([a * b for a, b in zip(previous, work)])
            work = [a - coefficient * b for a, b in zip(work, previous)]
        norm = mp.sqrt(mp.fsum([value * value for value in work]))
        if norm <= 0:
            raise AssertionError("dependent residual vector")
        basis.append([value / norm for value in work])
    return [list(column) for column in zip(*basis)]


def residual_operator(weights: list[Any], graph: list[list[Any]]) -> Any:
    n = len(weights)
    operator = mp.matrix(n)
    for i in range(n):
        diagonal = mp.fsum(graph[i])
        for j in range(n):
            laplacian = diagonal if i == j else -graph[i][j]
            operator[i, j] = laplacian / mp.sqrt(weights[i] * weights[j])
    return real_symmetric(operator)


def compressed(operator: Any, basis: list[list[Any]]) -> Any:
    matrix = mp.matrix(basis)
    return real_symmetric(matrix.transpose() * operator * matrix)


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    target = manifest["diagnostic_contract"]["fixed_failure_row"]
    thresholds = manifest["diagnostic_contract"]["thresholds"]
    digits = int(manifest["precision_contract"]["mpmath_decimal_digits"])
    mp.mp.dps = digits
    print(f"R-430 source audit: mpmath dps={digits}; building oscillator/Hamiltonian", flush=True)
    fixture = json.loads(R419_MANIFEST.read_text(encoding="utf-8"))["finite_fixture"]
    hamiltonian, coordinate_basis, momentum_coordinate, coordinate_levels = source_system(int(target["volume"]), int(target["cutoff_dimension"]), fixture)
    print("R-430 source audit: diagonalizing 256-dimensional Hamiltonian", flush=True)
    beta = mp.mpf(str(Fraction(str(target["beta"]))))
    logs = coordinate_log_masses(hamiltonian, coordinate_basis, beta)
    row = conditional_row(logs, int(target["cutoff_dimension"]), 6)
    chi = mp.mpf(str(Fraction(str(fixture["chi"]))))
    graph = projected_graph(row, momentum_coordinate, chi)
    threshold = mp.mpf(str(Fraction(str(json.loads(R426_MANIFEST.read_text(encoding="utf-8"))["finite_fixture"]["tail_threshold"]))))
    blocks = blocks_from_row(row, threshold)
    operator = residual_operator(row, graph)
    basis = residual_basis(row, blocks)
    print("R-430 source audit: diagonalizing 14-dimensional residual compression", flush=True)
    eigenvalues = mp.eigsy(compressed(operator, basis), eigvals_only=True)
    gap = eigenvalues[0]
    reference = mp.mpf(str(target["r422_residual_gap"]))
    direct_reference = mp.mpf(str(target["r426_direct_residual_gap"]))
    mismatch = abs(gap - reference)
    direct_mismatch = abs(gap - direct_reference)
    comparison = mp.mpf(str(thresholds["comparison_tolerance"]))
    checks: list[dict[str, Any]] = []
    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})
    check("manifest identity", manifest["result_id"] == "R-430" and manifest["exploration_id"] == "EXP-001275" and manifest["claim_bearing"] is False, [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"]], "R-430/EXP-001275/false", "provenance")
    check("source dimensions", hamiltonian.rows == 256 and coordinate_basis.rows == 256 and coordinate_basis.cols == 256 and momentum_coordinate.rows == 16, [hamiltonian.rows, coordinate_basis.rows, coordinate_basis.cols, momentum_coordinate.rows], "256/256/256/16", "source")
    check("coordinate levels ordered", all(coordinate_levels[i] < coordinate_levels[i + 1] for i in range(len(coordinate_levels) - 1)), "strictly increasing", "coordinate eigensystem", "source")
    check("log masses finite", all(value != mp.ninf and mp.isfinite(value) for value in logs), [str(min(logs)), str(max(logs))], "finite", "gibbs")
    check("conditional row positive", all(value > 0 for value in row) and abs(mp.fsum(row) - 1) <= mp.mpf(str(thresholds["row_reconstruction_tolerance"])), [str(min(row)), str(max(row)), str(mp.fsum(row))], "positive normalized", "graph")
    graph_symmetry_error = max(abs(graph[i][j] - graph[j][i]) for i in range(len(row)) for j in range(len(row)))
    check("graph reversible", graph_symmetry_error <= mp.mpf("1e-40"), graph_symmetry_error, "<=1e-40", "graph")
    check("block sizes", [len(block) for block in blocks] == [int(target["core_size"]), int(target["tail_size"])], [len(block) for block in blocks], [target["core_size"], target["tail_size"]], "fixture")
    check("residual basis dimension", len(basis) == len(row) and len(basis[0]) == len(row) - len(blocks), [len(basis), len(basis[0])], "16x14", "residual")
    gram = mp.matrix(basis).transpose() * mp.matrix(basis)
    gram_error = max(abs(gram[i, j] - (1 if i == j else 0)) for i in range(gram.rows) for j in range(gram.cols))
    check("residual basis orthonormal", gram_error <= mp.mpf("1e-40"), gram_error, "<=1e-40", "residual")
    check("source residual gap finite", mp.isfinite(gap) and gap > 0, gap, ">0", "residual")
    check("source gap separated from R-422", mismatch > comparison, mismatch, f">{comparison}", "reconstruction")
    check("source gap separated from direct reference", direct_mismatch > comparison, direct_mismatch, f">{comparison}", "reconstruction")
    check("scope firewall", manifest["scope"]["source_interval_certified"] is False and manifest["scope"]["exact_original_input_certified"] is False and manifest["scope"]["residual_reuse_closed"] is False and manifest["scope"]["r426_route_failure_preserved"] is True, manifest["scope"], "point audit only", "scope")
    classification = "SOURCE_POINT_AUDIT_NO_INTERVAL"
    check("classification", classification == manifest["status"], classification, manifest["status"], "verdict")
    derived = {"fixed_row": {"volume": target["volume"], "cutoff_dimension": target["cutoff_dimension"], "beta": target["beta"], "orientation": target["orientation"], "conditional_row_index": target["conditional_row_index"], "core_size": len(blocks[0]), "tail_size": len(blocks[1])}, "mpmath_decimal_digits": digits, "hamiltonian_dimension": hamiltonian.rows, "conditional_row_min_decimal": mp.nstr(min(row), 45), "conditional_row_max_decimal": mp.nstr(max(row), 45), "minimum_log_mass_decimal": mp.nstr(min(logs), 45), "source_residual_gap_decimal": mp.nstr(gap, 45), "r422_reference_decimal": mp.nstr(reference, 45), "direct_reference_decimal": mp.nstr(direct_reference, 45), "mismatch_r422_decimal": mp.nstr(mismatch, 45), "mismatch_direct_decimal": mp.nstr(direct_mismatch, 45), "classification": classification, "source_interval_certified": False, "exact_original_input_certified": False, "residual_reuse_closed": False, "r426_route_failure_preserved": True}
    payload: dict[str, Any] = {"schema": "tect/pre-a-r430-primary/1.0", "manifest": MANIFEST.relative_to(REPO).as_posix(), "result_id": manifest["result_id"], "exploration_id": manifest["exploration_id"], "claim_id": manifest["claim_ids"][0], "run_kind": "primary", "verdict": classification, "assertion_count": len(checks), "assertions": checks, "derived": derived, "source_hashes": {"primary": sha256(Path(__file__)), "manifest": sha256(MANIFEST), "r429_manifest": sha256(R429_MANIFEST), "r428_manifest": sha256(R428_MANIFEST), "r426_manifest": sha256(R426_MANIFEST), "r419_manifest": sha256(R419_MANIFEST)}, "assumptions": manifest["assumptions"], "missing_assumptions": manifest["missing_assumptions"], "evidence_level": manifest["evidence_level"], "non_claims": manifest["non_claims"], "boundary": manifest["boundary"], "runtime": {"package": "mpmath", "version": mp.__version__, "decimal_digits": digits}}
    atomic_json(output, payload)
    print(f"R-430 PRIMARY {classification} {len(checks)}/{len(checks)} gap={mp.nstr(gap, 45)} mismatch={mp.nstr(mismatch, 45)} direct_mismatch={mp.nstr(direct_mismatch, 45)}", flush=True)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run(args.output if args.output.is_absolute() else REPO / args.output)
    if args.self_test:
        assert payload["verdict"] == "SOURCE_POINT_AUDIT_NO_INTERVAL"
        assert payload["derived"]["source_interval_certified"] is False
        print("R-430 PRIMARY SELFTEST: PASS (original-source mpmath point audit)", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

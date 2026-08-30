#!/usr/bin/env python3
"""Non-importing NumPy control for the R-438 d=19 finite row."""

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
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-original-source-interval-d19-manifest.json"
R419_MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-growing-volume-lyapunov-core-tail-stress-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-independent-original_source_interval_d19/independent.json"


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


def rational(value: Any) -> float:
    fraction = Fraction(str(value))
    return float(fraction.numerator / fraction.denominator)


def source_matrices(dimension: int, fixture: dict[str, Any]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    q = np.zeros((dimension, dimension), dtype=np.longdouble)
    skew = np.zeros((dimension, dimension), dtype=np.longdouble)
    for index in range(dimension - 1):
        value = np.sqrt(np.longdouble(index + 1) / np.longdouble(2))
        q[index, index + 1] = value
        q[index + 1, index] = value
        skew[index, index + 1] = value
        skew[index + 1, index] = -value
    identity = np.eye(dimension, dtype=np.longdouble)
    q0 = np.kron(q, identity)
    q1 = np.kron(identity, q)
    s0 = np.kron(skew, identity)
    s1 = np.kron(identity, skew)
    q02 = q0 @ q0
    q12 = q1 @ q1
    sum_q2 = q02 + q12
    difference2 = q02 + q12 - np.longdouble(2) * (q0 @ q1)
    onsite = (-(s0 @ s0) - (s1 @ s1)) / (np.longdouble(2) * rational(fixture["chi"]))
    onsite += rational(fixture["r"]) * sum_q2 / np.longdouble(2)
    onsite += rational(fixture["g"]) * (q02 @ q02 + q12 @ q12) / np.longdouble(4)
    bond = rational(fixture["c"]) * difference2 / np.longdouble(2)
    bond += rational(fixture["lambda"]) * (difference2 @ sum_q2) / np.longdouble(4)
    return q, skew, onsite + bond


def block_dimensions(dimension: int) -> list[int]:
    values: list[int] = []
    for parity in (0, 1):
        for exchange in (1, -1):
            count = 0
            for left in range(dimension):
                for right in range(left, dimension):
                    if (left + right) % 2 != parity:
                        continue
                    if left == right and exchange != 1:
                        continue
                    count += 1
            values.append(count)
    return values


def residual_basis(weights: np.ndarray, core: np.ndarray, tail: np.ndarray) -> np.ndarray:
    vectors: list[np.ndarray] = []
    for block in (core, tail):
        anchor = int(block[0])
        for index in block[1:]:
            vector = np.zeros(weights.size, dtype=np.float64)
            vector[anchor] = np.sqrt(weights[int(index)])
            vector[int(index)] = -np.sqrt(weights[anchor])
            vectors.append(vector)
    basis, _ = np.linalg.qr(np.column_stack(vectors), mode="reduced")
    return basis


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = json.loads(R419_MANIFEST.read_text(encoding="utf-8"))["finite_fixture"]
    source = manifest["source_contract"]
    contract = manifest["interval_contract"]
    n = int(source["cutoff_dimension"])
    size = n * n
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("manifest identity", manifest["result_id"] == "R-438" and manifest["exploration_id"] == "EXP-001283" and not manifest["claim_bearing"], [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"]], "R-438/EXP-001283/false", "provenance")
    check("finite dimension", size == int(contract["expected_hamiltonian_dimension"]), size, contract["expected_hamiltonian_dimension"], "source")
    check("independent block enumeration", block_dimensions(n) == manifest["expected_block_sizes"], block_dimensions(n), manifest["expected_block_sizes"], "symmetry")
    q_single, skew_single, hamiltonian = source_matrices(n, fixture)
    energies, vectors = np.linalg.eigh(np.asarray(hamiltonian, dtype=np.float64))
    check("source self-adjoint", float(np.max(np.abs(hamiltonian - hamiltonian.T))) < 1.0e-10 and np.all(np.isfinite(energies)), float(np.max(np.abs(hamiltonian - hamiltonian.T))), "finite symmetric source", "source")
    check("source ordering", bool(np.all(np.diff(energies) > 0.0)), float(np.min(np.diff(energies))), ">0", "source")
    beta = rational(source["beta"])
    shifted = np.exp(-beta * (energies - energies[0]))
    gibbs = (vectors * shifted) @ vectors.T
    q_values, q_vectors = np.linalg.eigh(np.asarray(q_single, dtype=np.float64))
    coordinate = np.zeros((size, size), dtype=np.float64)
    for left in range(n):
        for right in range(n):
            coordinate[:, left * n + right] = np.kron(q_vectors[:, left], q_vectors[:, right])
    diagonal = np.diag(coordinate.T @ gibbs @ coordinate)
    normalized = diagonal / float(np.sum(diagonal))
    row = np.asarray([float(np.sum(normalized[left * n : (left + 1) * n])) for left in range(n)])
    check("unconditional positivity", bool(np.all(row > 0.0)), float(np.min(row)), ">0", "Gibbs row")
    check("unconditional normalization", abs(float(np.sum(row)) - 1.0) < 1.0e-12, float(np.sum(row)), "1", "Gibbs row")
    maximum = float(np.max(row))
    phi = np.log(maximum) - np.log(row)
    threshold = rational(source["tail_threshold"])
    core = np.flatnonzero(phi < threshold)
    tail = np.flatnonzero(phi >= threshold)
    check("tail split", core.tolist() == source["core_indices"] and tail.tolist() == source["tail_indices"], [core.tolist(), tail.tolist()], [source["core_indices"], source["tail_indices"]], "row")
    projected = q_vectors.T @ np.asarray(skew_single, dtype=np.float64) @ q_vectors
    momentum_squared = projected * projected
    conductance = (row[:, None] + row[None, :]) * momentum_squared / (2.0 * rational(fixture["chi"]))
    np.fill_diagonal(conductance, 0.0)
    laplacian = np.diag(np.sum(conductance, axis=1)) - conductance
    operator = laplacian / np.sqrt(row[:, None] * row[None, :])
    operator = (operator + operator.T) / 2.0
    basis = residual_basis(row, core, tail)
    compressed = (basis.T @ operator @ basis + (basis.T @ operator @ basis).T) / 2.0
    gap = float(np.linalg.eigvalsh(compressed)[0])
    check("residual compression", np.isfinite(gap) and compressed.shape == (n - 2, n - 2), [gap, compressed.shape], f"finite {n - 2}x{n - 2} compression", "residual")
    check("lower probe", gap > rational(contract["lower_probe"]), gap, f">{contract['lower_probe']}", "eigenvalue")
    check("upper probe", gap < rational(contract["upper_probe"]), gap, f"<{contract['upper_probe']}", "eigenvalue")
    check("finite gap margin", gap - rational(contract["lower_probe"]) > 0.0 and rational(contract["upper_probe"]) - gap > 0.0, [gap - rational(contract["lower_probe"]), rational(contract["upper_probe"]) - gap], "positive two-sided margin", "eigenvalue")
    payload = {
        "schema": "tect/pre-a-r438-independent/1.0",
        "manifest": MANIFEST.relative_to(REPO).as_posix(),
        "result_id": "R-438",
        "exploration_id": "EXP-001283",
        "claim_id": manifest["claim_ids"][0],
        "run_kind": "independent",
        "verdict": "INDEPENDENT_FINITE_CONTROL_PASS",
        "assertion_count": len(checks),
        "assertions": checks,
        "derived": {"fixed_row": source, "block_sizes": block_dimensions(n), "conditional_row": row.tolist(), "tail_split": {"core": core.tolist(), "tail": tail.tolist()}, "residual_gap_double": gap, "lower_probe_margin": gap - rational(contract["lower_probe"]), "upper_probe_margin": rational(contract["upper_probe"]) - gap},
        "source_hashes": {"script": sha256(Path(__file__)), "manifest": sha256(MANIFEST), "r419_manifest": sha256(R419_MANIFEST)},
        "assumptions": manifest["assumptions"],
        "missing_assumptions": manifest["missing_assumptions"],
        "evidence_level": "T0 / EXECUTED INDEPENDENT FINITE FLOAT CONTROL; PRIMARY DIRECTED INTERVAL REMAINS AUTHORITATIVE",
        "non_claims": manifest["non_claims"] + ["The independent float reconstruction is not an interval or uniform proof."],
        "boundary": manifest["boundary"],
    }
    atomic_json(output, payload)
    print(f"R-438 INDEPENDENT {payload['verdict']} {len(checks)}/{len(checks)} gap={gap:.15g}", flush=True)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = run(args.output if args.output.is_absolute() else REPO / args.output)
    if args.self_test:
        assert payload["verdict"] == "INDEPENDENT_FINITE_CONTROL_PASS"
        print("R-438 INDEPENDENT SELFTEST: PASS", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

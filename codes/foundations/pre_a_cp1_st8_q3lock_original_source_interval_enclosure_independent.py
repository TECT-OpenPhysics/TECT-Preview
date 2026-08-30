#!/usr/bin/env python3
"""Independent NumPy control for the R-433 finite source row.

This file deliberately does not import the primary mpmath implementation.  It
rebuilds the oscillator source, diagonalizes the full 256 by 256 matrix, and
recomputes the corrected parent-6 conditional row and residual compression in
a separate algebraic order.  Its role is an independent finite control; only
the primary run supplies the directed interval certificate.
"""

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
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-original-source-interval-enclosure-manifest.json"
R419_MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-growing-volume-lyapunov-core-tail-stress-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-independent-original_source_interval_enclosure/independent.json"


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


def scalar(value: Any) -> float:
    fraction = Fraction(str(value))
    return float(fraction.numerator / fraction.denominator)


def source_matrices(dimension: int, fixture: dict[str, Any]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Reconstruct q, skew-q and H from the declared rational fixture."""
    q_single = np.zeros((dimension, dimension), dtype=np.longdouble)
    skew_single = np.zeros((dimension, dimension), dtype=np.longdouble)
    for index in range(dimension - 1):
        value = np.sqrt(np.longdouble(index + 1) / np.longdouble(2))
        q_single[index, index + 1] = value
        q_single[index + 1, index] = value
        skew_single[index, index + 1] = value
        skew_single[index + 1, index] = -value
    identity = np.eye(dimension, dtype=np.longdouble)
    q0 = np.kron(q_single, identity)
    q1 = np.kron(identity, q_single)
    skew0 = np.kron(skew_single, identity)
    skew1 = np.kron(identity, skew_single)
    q02 = q0 @ q0
    q12 = q1 @ q1
    p02 = -(skew0 @ skew0)
    p12 = -(skew1 @ skew1)
    sum_q2 = q02 + q12
    difference2 = q02 + q12 - np.longdouble(2) * (q0 @ q1)
    q04 = q02 @ q02
    q14 = q12 @ q12
    chi = np.longdouble(scalar(fixture["chi"]))
    mass = np.longdouble(scalar(fixture["r"]))
    quartic = np.longdouble(scalar(fixture["g"]))
    coupling = np.longdouble(scalar(fixture["c"]))
    lam = np.longdouble(scalar(fixture["lambda"]))
    onsite = (p02 + p12) / (np.longdouble(2) * chi) + mass * sum_q2 / np.longdouble(2) + quartic * (q04 + q14) / np.longdouble(4)
    bond = coupling * difference2 / np.longdouble(2) + lam * (difference2 @ sum_q2) / np.longdouble(4)
    return q_single, skew_single, onsite + bond


def sector_dimensions(dimension: int) -> list[int]:
    dimensions: list[int] = []
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
            dimensions.append(count)
    return dimensions


def residual_basis(weights: np.ndarray, blocks: list[np.ndarray]) -> np.ndarray:
    vectors: list[np.ndarray] = []
    for block in blocks:
        if len(block) < 2:
            raise AssertionError("residual block has fewer than two entries")
        anchor = int(block[0])
        for index in block[1:]:
            vector = np.zeros(weights.size, dtype=np.longdouble)
            vector[anchor] = np.sqrt(weights[int(index)])
            vector[int(index)] = -np.sqrt(weights[anchor])
            vectors.append(vector)
    matrix = np.column_stack(vectors)
    # NumPy's QR is intentionally used here rather than the primary interval
    # Gram-Schmidt implementation.
    orthonormal, _ = np.linalg.qr(np.asarray(matrix, dtype=np.float64), mode="reduced")
    return np.asarray(orthonormal, dtype=np.longdouble)


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    fixture = json.loads(R419_MANIFEST.read_text(encoding="utf-8"))["finite_fixture"]
    source = manifest["source_contract"]
    dimension = int(source["cutoff_dimension"])
    size = dimension * dimension
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check("manifest identity", manifest["result_id"] == "R-433" and manifest["exploration_id"] == "EXP-001278" and manifest["claim_bearing"] is False, [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"]], "R-433/EXP-001278/false", "provenance")
    check("fixed source row", [source["volume"], dimension, source["beta"], source["orientation"], source["target_emission_ordinal"], source["target_parent_coordinate"]] == [2, 16, "8", "right", 7, 6], [source["volume"], dimension, source["beta"], source["orientation"], source["target_emission_ordinal"], source["target_parent_coordinate"]], "V2/d16/beta8/right/emission7/parent6", "fixture")
    check("sector enumeration", sector_dimensions(dimension) == [72, 56, 64, 64], sector_dimensions(dimension), [72, 56, 64, 64], "symmetry")

    q_single, skew_single, hamiltonian = source_matrices(dimension, fixture)
    energies, h_vectors = np.linalg.eigh(np.asarray(hamiltonian, dtype=np.float64))
    check("full source dimension", hamiltonian.shape == (size, size), hamiltonian.shape, (256, 256), "source")
    check("source finite self-adjoint", np.max(np.abs(hamiltonian - hamiltonian.T)) < 1.0e-10 and np.all(np.isfinite(energies)), float(np.max(np.abs(hamiltonian - hamiltonian.T))), "symmetric and finite", "source")
    check("source ordering", bool(np.all(np.diff(energies) > 0.0)), float(np.min(np.diff(energies))), ">0", "source")

    beta = scalar(source["beta"])
    shifted = np.exp(-beta * (energies - energies[0]))
    gibbs_kernel = (h_vectors * shifted) @ h_vectors.T
    q_values, q_vectors = np.linalg.eigh(np.asarray(q_single, dtype=np.float64))
    coordinate_matrix = np.zeros((size, size), dtype=np.longdouble)
    for left in range(dimension):
        for right in range(dimension):
            coordinate_matrix[:, left * dimension + right] = np.kron(q_vectors[:, left], q_vectors[:, right])
    diagonal = np.diag(np.asarray(coordinate_matrix.T @ np.asarray(gibbs_kernel, dtype=np.longdouble) @ coordinate_matrix, dtype=np.longdouble))
    parent = int(source["target_parent_coordinate"])
    probabilities = diagonal[parent * dimension : (parent + 1) * dimension]
    probabilities = probabilities / np.sum(probabilities)
    check("conditional row positivity", bool(np.all(probabilities > 0.0)), float(np.min(probabilities)), ">0", "Gibbs row")
    check("conditional row normalization", abs(float(np.sum(probabilities)) - 1.0) < 1.0e-12, float(np.sum(probabilities)), "1", "Gibbs row")

    maximum = float(np.max(probabilities))
    phi = np.log(maximum) - np.log(np.asarray(probabilities, dtype=float))
    threshold = scalar(source["tail_threshold"])
    core = np.flatnonzero(phi < threshold)
    tail = np.flatnonzero(phi >= threshold)
    check("tail split", core.tolist() == source["core_indices"] and tail.tolist() == source["tail_indices"], [core.tolist(), tail.tolist()], [source["core_indices"], source["tail_indices"]], "row")

    projected_momentum = q_vectors.T @ np.asarray(skew_single, dtype=np.float64) @ q_vectors
    momentum_squared = projected_momentum * projected_momentum
    conductance = (np.asarray(probabilities, dtype=float)[:, None] + np.asarray(probabilities, dtype=float)[None, :]) * momentum_squared / (2.0 * scalar(fixture["chi"]))
    np.fill_diagonal(conductance, 0.0)
    conductance = (conductance + conductance.T) / 2.0
    laplacian = np.diag(np.sum(conductance, axis=1)) - conductance
    operator = laplacian / np.sqrt(np.asarray(probabilities, dtype=float)[:, None] * np.asarray(probabilities, dtype=float)[None, :])
    operator = (operator + operator.T) / 2.0
    blocks = [core, tail]
    basis = residual_basis(np.asarray(probabilities, dtype=float), blocks)
    compressed = np.asarray(basis.T @ operator @ basis, dtype=float)
    compressed = (compressed + compressed.T) / 2.0
    residual_gap = float(np.linalg.eigvalsh(compressed)[0])
    check("residual compression finite", np.isfinite(residual_gap) and compressed.shape == (14, 14), residual_gap, "finite 14x14 compression", "residual")

    r422_lower = scalar(source["r422_reference"]) + float(source["comparison_tolerance"])
    r426_upper = scalar(source["r426_direct_reference"]) + 5.0e-6
    check("independent R-422 sign separation", residual_gap > r422_lower, residual_gap - scalar(source["r422_reference"]), f">{source['comparison_tolerance']}", "reference")
    check("independent source consistency", abs(residual_gap - 5.3631875357869329) < 5.0e-6 and residual_gap < r426_upper, residual_gap, "finite source control within 5e-6", "reference")

    payload: dict[str, Any] = {
        "schema": "tect/pre-a-r433-independent/1.0",
        "manifest": MANIFEST.relative_to(REPO).as_posix(),
        "result_id": "R-433",
        "exploration_id": "EXP-001278",
        "claim_id": manifest["claim_ids"][0],
        "run_kind": "independent",
        "verdict": "INDEPENDENT_FINITE_CONTROL_PASS",
        "assertion_count": len(checks),
        "assertions": checks,
        "derived": {
            "symmetry_block_sizes": sector_dimensions(dimension),
            "fixed_row": source,
            "hamiltonian_ground_energy_double": float(energies[0]),
            "hamiltonian_top_energy_double": float(energies[-1]),
            "conditional_row": [float(value) for value in probabilities],
            "tail_split": {"core": core.tolist(), "tail": tail.tolist()},
            "residual_gap_double": residual_gap,
            "r422_separation_margin_double": residual_gap - scalar(source["r422_reference"]),
            "role": "independent finite control only; it does not replace the primary directed interval enclosure",
        },
        "scope": {
            "independent_source_reconstruction": True,
            "independent_corrected_row_reconstruction": True,
            "independent_residual_control": True,
            "directed_interval_certificate": False,
            "uniform_or_physical_promotion": False,
        },
        "source_hashes": {"script": sha256(Path(__file__)), "manifest": sha256(MANIFEST), "r419_manifest": sha256(R419_MANIFEST)},
        "assumptions": manifest["assumptions"],
        "missing_assumptions": manifest["missing_assumptions"],
        "evidence_level": "T0 / EXECUTED INDEPENDENT FINITE DOUBLE-PRECISION CONTROL; PRIMARY INTERVAL CERTIFICATE REMAINS AUTHORITATIVE",
        "non_claims": manifest["non_claims"] + ["The independent double-precision control is not itself an interval or uniform proof."],
    }
    atomic_json(output, payload)
    print(f"R-433 INDEPENDENT {payload['verdict']} {len(checks)}/{len(checks)} gap={residual_gap:.15g}", flush=True)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    destination = args.output if args.output.is_absolute() else REPO / args.output
    payload = run(destination)
    if args.self_test:
        assert payload["verdict"] == "INDEPENDENT_FINITE_CONTROL_PASS"
        assert payload["scope"]["directed_interval_certificate"] is False
        print("R-433 INDEPENDENT SELFTEST: PASS", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

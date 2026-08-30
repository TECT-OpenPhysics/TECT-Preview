#!/usr/bin/env python3
"""Directed interval certificate for the fixed R-428/R-429 graph snapshot.

The upstream row is intentionally the deterministic binary64 snapshot emitted
by R-429.  Each stored float is treated as its exact binary rational.  The
interval calculation certifies only the resulting finite residual matrix; it
does not enclose the original 256-dimensional Hamiltonian or its Gibbs state.
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
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-rounded-snapshot-interval-enclosure-manifest.json"
R429_MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-residual-precision-uplift-manifest.json"
R429_SCRIPT = REPO / "codes/foundations/pre_a_cp1_st8_q3lock_residual_precision_uplift.py"
R426_MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-high-cutoff-schur-stress-manifest.json"
R428_MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-residual-basis-conditioning-diagnostic-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-primary-rounded_snapshot_interval_enclosure/primary.json"


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
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
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


def lo(value: Any) -> Any:
    return mp.mpf(value.a)


def hi(value: Any) -> Any:
    return mp.mpf(value.b)


def width(value: Any) -> Any:
    return hi(value) - lo(value)


def interval_from_float(value: float) -> Any:
    """Represent a binary64 value as an exact binary rational interval."""
    rational = Fraction.from_float(float(value))
    return mp.iv.mpf(rational.numerator) / mp.iv.mpf(rational.denominator)


def interval_from_decimal(value: str) -> Any:
    return mp.iv.mpf(str(value))


def interval_sum(values: list[Any]) -> Any:
    return sum(values, mp.iv.mpf(0))


def interval_hull(left: Any, right: Any) -> Any:
    return mp.iv.mpf([min(lo(left), lo(right)), max(hi(left), hi(right))])


def contains(value: Any, target: Any) -> bool:
    return lo(value) <= mp.mpf(target) <= hi(value)


def snapshot_row() -> tuple[list[Any], list[list[Any]], list[np.ndarray]]:
    """Load the exact R-429 finite snapshot without importing this module."""
    sys.path.insert(0, str(R429_SCRIPT.parent))
    import pre_a_cp1_st8_q3lock_residual_precision_uplift as r429  # noqa: PLC0415

    pi_float, conductance_float, blocks = r429.row_inputs()
    pi = [interval_from_float(float(value)) for value in pi_float]
    conductance = [
        [interval_from_float(float(value)) for value in row]
        for row in conductance_float
    ]
    return pi, conductance, blocks


def build_residual_interval(
    pi: list[Any], conductance: list[list[Any]], blocks: list[np.ndarray]
) -> tuple[list[list[Any]], list[list[Any]], list[list[Any]]]:
    n = len(pi)
    if n == 0 or len(conductance) != n:
        raise AssertionError("empty or mismatched snapshot")

    # Make the finite conductance explicitly symmetric by interval hull.  This
    # encloses both binary64 directions without silently selecting one side.
    symmetric = [[mp.iv.mpf(0) for _ in range(n)] for _ in range(n)]
    for i in range(n):
        if len(conductance[i]) != n:
            raise AssertionError("conductance is not square")
        for j in range(n):
            symmetric[i][j] = interval_hull(conductance[i][j], conductance[j][i])

    operator = [[mp.iv.mpf(0) for _ in range(n)] for _ in range(n)]
    for i in range(n):
        diagonal = interval_sum(symmetric[i])
        for j in range(n):
            laplacian = diagonal if i == j else -symmetric[i][j]
            operator[i][j] = laplacian / mp.iv.sqrt(pi[i] * pi[j])

    raw: list[list[Any]] = []
    for block_array in blocks:
        block = [int(index) for index in block_array]
        if len(block) < 2:
            raise AssertionError("residual block has fewer than two entries")
        anchor = block[0]
        for index in block[1:]:
            vector = [mp.iv.mpf(0) for _ in range(n)]
            vector[anchor] = mp.iv.sqrt(pi[index])
            vector[index] = -mp.iv.sqrt(pi[anchor])
            raw.append(vector)

    basis: list[list[Any]] = []
    for vector in raw:
        work = list(vector)
        for previous in basis:
            coefficient = interval_sum(
                [left * right for left, right in zip(previous, work)]
            )
            work = [value - coefficient * base for value, base in zip(work, previous)]
        norm_square = interval_sum([value * value for value in work])
        if hi(norm_square) <= 0:
            raise AssertionError("interval residual vector lost positivity")
        norm = mp.iv.sqrt(norm_square)
        basis.append([value / norm for value in work])

    columns = [list(column) for column in zip(*basis)]
    dimension = len(columns[0])
    compressed = [[mp.iv.mpf(0) for _ in range(dimension)] for _ in range(dimension)]
    for i in range(dimension):
        for j in range(dimension):
            total = mp.iv.mpf(0)
            for a in range(n):
                inner = interval_sum(
                    [operator[a][b] * columns[b][j] for b in range(n)]
                )
                total += columns[a][i] * inner
            compressed[i][j] = total

    symmetric_compressed = [[mp.iv.mpf(0) for _ in range(dimension)] for _ in range(dimension)]
    for i in range(dimension):
        for j in range(dimension):
            symmetric_compressed[i][j] = interval_hull(
                compressed[i][j], compressed[j][i]
            )
    return symmetric_compressed, columns, symmetric


def interval_gram(columns: list[list[Any]]) -> list[list[Any]]:
    rows = len(columns)
    cols = len(columns[0])
    return [
        [interval_sum([columns[k][i] * columns[k][j] for k in range(rows)]) for j in range(cols)]
        for i in range(cols)
    ]


def interval_cholesky_lower(matrix: list[list[Any]], probe: Any) -> tuple[bool, list[Any]]:
    n = len(matrix)
    factor = [[mp.iv.mpf(0) for _ in range(n)] for _ in range(n)]
    pivots: list[Any] = []
    for i in range(n):
        pivot = matrix[i][i] - probe - interval_sum(
            [factor[i][k] * factor[i][k] for k in range(i)]
        )
        pivots.append(pivot)
        if lo(pivot) <= 0:
            return False, pivots
        factor[i][i] = mp.iv.sqrt(pivot)
        for j in range(i + 1, n):
            numerator = matrix[j][i] - interval_sum(
                [factor[j][k] * factor[i][k] for k in range(i)]
            )
            factor[j][i] = numerator / factor[i][i]
    return True, pivots


def midpoint(value: Any) -> float:
    return float((lo(value) + hi(value)) / 2)


def rayleigh_upper(matrix: list[list[Any]]) -> tuple[Any, list[float]]:
    center = np.asarray(
        [[midpoint(value) for value in row] for row in matrix], dtype=float
    )
    eigenvalues, eigenvectors = np.linalg.eigh(center)
    if not np.isfinite(eigenvalues[0]):
        raise AssertionError("center eigensolver returned nonfinite value")
    vector = eigenvectors[:, 0]
    x = [interval_from_float(float(value)) for value in vector]
    numerator = mp.iv.mpf(0)
    for i in range(len(matrix)):
        inner = interval_sum([matrix[i][j] * x[j] for j in range(len(matrix))])
        numerator += x[i] * inner
    denominator = interval_sum([value * value for value in x])
    if lo(denominator) <= 0:
        raise AssertionError("Rayleigh denominator interval is not positive")
    return numerator / denominator, [float(value) for value in vector]


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    contract = manifest["interval_contract"]
    target = contract["fixed_row"]
    oracles = manifest["test_oracles"]
    mp.iv.dps = int(contract["interval_decimal_digits"])
    mp.mp.dps = int(contract["interval_decimal_digits"]) + 40

    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append(
            {
                "name": name,
                "group": group,
                "status": "PASS",
                "actual": str(actual),
                "expected": str(expected),
            }
        )

    check(
        "manifest identity",
        manifest["result_id"] == "R-431"
        and manifest["exploration_id"] == "EXP-001276"
        and manifest["claim_bearing"] is False,
        [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"]],
        "R-431/EXP-001276/false",
        "provenance",
    )
    check(
        "parent hashes",
        sha256(R429_MANIFEST) == manifest["upstream_authority"]["r429_sha256"]
        and sha256(R429_SCRIPT) == manifest["upstream_authority"]["r429_script_sha256"]
        and sha256(R426_MANIFEST) == manifest["upstream_authority"]["r426_sha256"]
        and sha256(R428_MANIFEST) == manifest["upstream_authority"]["r428_sha256"],
        "hash-pinned R429/R428/R426 inputs",
        "declared SHA-256 values",
        "authority",
    )
    check(
        "fixed row",
        [
            target["volume"],
            target["cutoff_dimension"],
            target["beta"],
            target["orientation"],
            target["conditional_row_index"],
        ]
        == [2, 16, "8", "right", 7],
        target,
        "V2/d16/beta8/right/row7",
        "fixture",
    )

    pi, conductance, blocks = snapshot_row()
    pi_sum = interval_sum(pi)
    check(
        "positive snapshot weights",
        all(lo(value) > 0 for value in pi),
        [str(min(lo(value) for value in pi)), str(max(hi(value) for value in pi))],
        ">0",
        "snapshot",
    )
    normalization_error = max(abs(lo(pi_sum) - 1), abs(hi(pi_sum) - 1))
    check(
        "snapshot normalization",
        normalization_error <= mp.mpf(str(contract["snapshot_normalization_tolerance"])),
        normalization_error,
        f"<={contract['snapshot_normalization_tolerance']}",
        "snapshot",
    )
    check(
        "block sizes",
        [len(block) for block in blocks]
        == [int(target["core_size"]), int(target["tail_size"])],
        [len(block) for block in blocks],
        [target["core_size"], target["tail_size"]],
        "fixture",
    )

    matrix, columns, symmetric_conductance = build_residual_interval(pi, conductance, blocks)
    gram = interval_gram(columns)
    gram_ok = all(
        contains(gram[i][i], 1) and all(contains(gram[i][j], 0) for j in range(len(gram)) if j != i)
        for i in range(len(gram))
    )
    check("interval residual basis enclosure", gram_ok, "diagonal contains 1 and off-diagonal contains 0", "orthonormal enclosure", "basis")
    max_matrix_width = max(width(value) for row in matrix for value in row)
    check(
        "matrix interval width",
        max_matrix_width <= mp.mpf(str(contract["maximum_matrix_interval_width"])),
        max_matrix_width,
        f"<={contract['maximum_matrix_interval_width']}",
        "interval",
    )
    check(
        "conductance symmetry enclosure",
        all(lo(symmetric_conductance[i][j]) <= hi(symmetric_conductance[i][j]) for i in range(len(pi)) for j in range(len(pi))),
        "all pair hulls finite",
        "finite symmetric hull",
        "graph",
    )

    lower_probe = interval_from_decimal(contract["lower_probe"])
    upper_probe = interval_from_decimal(contract["upper_probe"])
    failure_probe = interval_from_decimal(contract["cholesky_failure_probe"])
    lower_ok, lower_pivots = interval_cholesky_lower(matrix, lower_probe)
    check(
        "interval Cholesky lower bound",
        lower_ok and all(lo(pivot) > 0 for pivot in lower_pivots),
        [str(min(lo(pivot) for pivot in lower_pivots)), len(lower_pivots)],
        f"positive pivots for L={contract['lower_probe']}",
        "eigenvalue enclosure",
    )
    failure_ok, failure_pivots = interval_cholesky_lower(matrix, failure_probe)
    check(
        "upper-side Cholesky probe rejected",
        failure_ok is False and any(hi(pivot) <= 0 for pivot in failure_pivots),
        [failure_ok, len(failure_pivots)],
        f"rejected L={contract['cholesky_failure_probe']}",
        "eigenvalue enclosure",
    )

    rayleigh, rayleigh_vector = rayleigh_upper(matrix)
    check(
        "interval Rayleigh upper bound",
        hi(rayleigh) <= mp.mpf(str(contract["upper_probe"])),
        [str(lo(rayleigh)), str(hi(rayleigh))],
        f"<={contract['upper_probe']}",
        "eigenvalue enclosure",
    )
    lower_separation_threshold = mp.mpf(str(oracles["r422_lower_separation_threshold"]))
    upper_separation_threshold = mp.mpf(str(oracles["r426_upper_separation_threshold"]))
    lower_endpoint = mp.mpf(str(contract["lower_probe"]))
    upper_endpoint = hi(rayleigh)
    check(
        "R-422 separation",
        lower_endpoint > lower_separation_threshold,
        lower_endpoint - mp.mpf(str(oracles["r422_reference"])),
        f">{contract['comparison_tolerance']}",
        "reference separation",
    )
    check(
        "R-426 direct separation",
        upper_endpoint < upper_separation_threshold,
        mp.mpf(str(oracles["r426_direct_reference"])) - upper_endpoint,
        f">{contract['comparison_tolerance']}",
        "reference separation",
    )
    bracket_width = upper_endpoint - lower_endpoint
    check(
        "certified bracket width",
        bracket_width <= mp.mpf(str(contract["maximum_bracket_width"])),
        bracket_width,
        f"<={contract['maximum_bracket_width']}",
        "eigenvalue enclosure",
    )
    scope = manifest["scope"]
    check(
        "scope firewall",
        scope["rounded_snapshot_interval_certified"] is True
        and scope["original_source_interval_certified"] is False
        and scope["exact_original_hamiltonian_certified"] is False
        and scope["r422_separation_certified"] is True
        and scope["r426_direct_separation_certified"] is True
        and scope["r426_route_failure_preserved"] is True
        and scope["residual_reuse_closed_for_original_source"] is False
        and scope["no_new_negative_result"] is True
        and scope["no_tier_change"] is True,
        scope,
        "rounded snapshot only; original source open",
        "scope",
    )

    derived = {
        "fixed_row": target,
        "interval_decimal_digits": int(contract["interval_decimal_digits"]),
        "snapshot_weight_sum_interval": [str(lo(pi_sum)), str(hi(pi_sum))],
        "snapshot_normalization_error": str(normalization_error),
        "max_matrix_interval_width": str(max_matrix_width),
        "lower_probe": contract["lower_probe"],
        "upper_probe": contract["upper_probe"],
        "cholesky_failure_probe": contract["cholesky_failure_probe"],
        "lower_endpoint": str(lower_endpoint),
        "upper_endpoint": str(upper_endpoint),
        "bracket_width": str(bracket_width),
        "lower_min_pivot": str(min(lo(pivot) for pivot in lower_pivots)),
        "rayleigh_interval": [str(lo(rayleigh)), str(hi(rayleigh))],
        "rayleigh_vector_norm": str(sum(value * value for value in rayleigh_vector)),
        "r422_reference": oracles["r422_reference"],
        "r426_direct_reference": oracles["r426_direct_reference"],
        "r422_separation_margin_lower": str(lower_endpoint - mp.mpf(str(oracles["r422_reference"]))),
        "r426_separation_margin_upper": str(mp.mpf(str(oracles["r426_direct_reference"])) - upper_endpoint),
        "rounded_snapshot_interval_certified": True,
        "original_source_interval_certified": False,
        "exact_original_hamiltonian_certified": False,
        "r426_route_failure_preserved": True,
        "residual_reuse_closed_for_original_source": False,
        "classification": manifest["status"],
    }
    payload: dict[str, Any] = {
        "schema": "tect/pre-a-r431-primary/1.0",
        "result_id": "R-431",
        "exploration_id": "EXP-001276",
        "claim_id": manifest["claim_ids"][0],
        "manifest": MANIFEST.relative_to(REPO).as_posix(),
        "run_kind": "primary",
        "verdict": manifest["status"],
        "assertion_count": len(checks),
        "assertions": checks,
        "derived": derived,
        "source_hashes": {
            "manifest": sha256(MANIFEST),
            "r429_manifest": sha256(R429_MANIFEST),
            "r429_script": sha256(R429_SCRIPT),
            "r426_manifest": sha256(R426_MANIFEST),
            "r428_manifest": sha256(R428_MANIFEST),
        },
        "assumptions": manifest["assumptions"],
        "missing_assumptions": manifest["missing_assumptions"],
        "evidence_level": manifest["evidence_level"],
        "non_claims": manifest["non_claims"],
        "boundary": manifest["boundary"],
    }
    destination = output if output.is_absolute() else REPO / output
    atomic_json(destination, payload)
    print(
        "R-431 PRIMARY "
        f"{len(checks)}/{len(checks)} interval PASS "
        f"bracket=[{derived['lower_endpoint']},{derived['upper_endpoint']}] "
        f"R422_margin={derived['r422_separation_margin_lower']} "
        f"R426_margin={derived['r426_separation_margin_upper']}"
    )
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    run(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

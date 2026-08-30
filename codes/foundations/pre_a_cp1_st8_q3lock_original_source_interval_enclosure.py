#!/usr/bin/env python3
"""Validated finite interval enclosure for the corrected original source row.

The source is assembled from the rational R-419 fixture using sparse real
algebraic expressions.  Exchange and global Fock-parity symmetry reduce the
256-dimensional Hamiltonian to four blocks before the high-precision point
eigensolve.  Directed interval residual and Gram bounds then control the
polar correction and the Gibbs-kernel propagation.  The result is deliberately
finite and claim-nonbearing: it does not establish a common core or a physical
or continuum theorem.
"""

from __future__ import annotations

import argparse
import gc
import hashlib
import json
import os
import sys
import tempfile
from collections import defaultdict
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable

import numpy as np


REPO = Path(__file__).resolve().parents[2]
MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-original-source-interval-enclosure-manifest.json"
R432_MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-fixed-row-ordinal-audit-manifest.json"
R430_MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-source-point-precision-audit-manifest.json"
R431_MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-rounded-snapshot-interval-enclosure-manifest.json"
R426_MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-high-cutoff-schur-stress-manifest.json"
R419_MANIFEST = REPO / "strategy/pre-a-cp1-st8-q3lock-growing-volume-lyapunov-core-tail-stress-manifest.json"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs/2026-08-30-primary-original_source_interval_enclosure/primary.json"
POINT_CACHE = REPO / ".tmp/r433-point-cache.json"


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
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, ensure_ascii=True, default=str)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def jsonable_matrix(matrix: list[list[Any]]) -> list[list[str]]:
    return [[mp.nstr(value, 60) for value in row] for row in matrix]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def rational(ctx: Any, value: Any) -> Any:
    fraction = Fraction(str(value))
    return ctx.mpf(fraction.numerator) / ctx.mpf(fraction.denominator)


def sparse_add(matrices: Iterable[dict[tuple[int, int], Any]], zero: Any) -> dict[tuple[int, int], Any]:
    result: dict[tuple[int, int], Any] = {}
    for matrix in matrices:
        for key, value in matrix.items():
            result[key] = result.get(key, zero) + value
    return result


def sparse_scale(matrix: dict[tuple[int, int], Any], scalar: Any) -> dict[tuple[int, int], Any]:
    return {key: value * scalar for key, value in matrix.items()}


def sparse_mul(
    left: dict[tuple[int, int], Any],
    right: dict[tuple[int, int], Any],
    zero: Any,
) -> dict[tuple[int, int], Any]:
    by_row: defaultdict[int, list[tuple[int, Any]]] = defaultdict(list)
    for (row, column), value in right.items():
        by_row[row].append((column, value))
    result: dict[tuple[int, int], Any] = {}
    for (row, pivot), left_value in left.items():
        for column, right_value in by_row.get(pivot, []):
            key = (row, column)
            result[key] = result.get(key, zero) + left_value * right_value
    return result


def embedded(single: dict[tuple[int, int], Any], site: int, dimension: int) -> dict[tuple[int, int], Any]:
    result: dict[tuple[int, int], Any] = {}
    for (row, column), value in single.items():
        for other in range(dimension):
            if site == 0:
                result[(row * dimension + other, column * dimension + other)] = value
            else:
                result[(other * dimension + row, other * dimension + column)] = value
    return result


def source_sparse(dimension: int, fixture: dict[str, Any], interval: bool = False) -> tuple[dict[tuple[int, int], Any], dict[tuple[int, int], Any], dict[tuple[int, int], Any]]:
    context = mp.iv if interval else mp
    zero = context.mpf(0)
    q_single: dict[tuple[int, int], Any] = {}
    skew_single: dict[tuple[int, int], Any] = {}
    for index in range(dimension - 1):
        value = context.sqrt(context.mpf(index + 1) / 2)
        q_single[(index, index + 1)] = value
        q_single[(index + 1, index)] = value
        skew_single[(index, index + 1)] = value
        skew_single[(index + 1, index)] = -value
    q0 = embedded(q_single, 0, dimension)
    q1 = embedded(q_single, 1, dimension)
    skew0 = embedded(skew_single, 0, dimension)
    skew1 = embedded(skew_single, 1, dimension)
    q02 = sparse_mul(q0, q0, zero)
    q12 = sparse_mul(q1, q1, zero)
    p02 = sparse_scale(sparse_mul(skew0, skew0, zero), -1)
    p12 = sparse_scale(sparse_mul(skew1, skew1, zero), -1)
    cross = sparse_mul(q0, q1, zero)
    sum_q2 = sparse_add((q02, q12), zero)
    difference2 = sparse_add((q02, q12, sparse_scale(cross, -2)), zero)
    q04 = sparse_mul(q02, q02, zero)
    q14 = sparse_mul(q12, q12, zero)
    chi = rational(context, fixture["chi"])
    mass = rational(context, fixture["r"])
    quartic = rational(context, fixture["g"])
    coupling = rational(context, fixture["c"])
    lam = rational(context, fixture["lambda"])
    onsite = sparse_add(
        (
            sparse_scale(sparse_add((p02, p12), zero), 1 / (2 * chi)),
            sparse_scale(sum_q2, mass / 2),
            sparse_scale(sparse_add((q04, q14), zero), quartic / 4),
        ),
        zero,
    )
    bond = sparse_add(
        (
            sparse_scale(difference2, coupling / 2),
            sparse_scale(sparse_mul(difference2, sum_q2, zero), lam / 4),
        ),
        zero,
    )
    hamiltonian = sparse_add((onsite, bond), zero)
    return q_single, skew_single, hamiltonian


def dense_from_sparse(matrix: dict[tuple[int, int], Any], dimension: int) -> Any:
    result = mp.matrix(dimension)
    for (row, column), value in matrix.items():
        result[row, column] = value
    return result


def symmetry_vectors(dimension: int, context: Any) -> list[list[dict[int, Any]]]:
    result: list[list[dict[int, Any]]] = []
    for parity in (0, 1):
        for exchange in (1, -1):
            sector: list[dict[int, Any]] = []
            for left in range(dimension):
                for right in range(left, dimension):
                    if (left + right) % 2 != parity:
                        continue
                    if left == right:
                        if exchange == 1:
                            sector.append({left * dimension + right: context.mpf(1)})
                    else:
                        coefficient = 1 / context.sqrt(2)
                        sector.append(
                            {
                                left * dimension + right: coefficient,
                                right * dimension + left: exchange * coefficient,
                            }
                        )
            result.append(sector)
    return result


def block_matrix(
    matrix: dict[tuple[int, int], Any], vectors: list[dict[int, Any]], context: Any
) -> Any:
    size = len(vectors)
    result = context.matrix(size)
    zero = context.mpf(0)
    for left, first in enumerate(vectors):
        for right, second in enumerate(vectors):
            total = zero
            for row, first_value in first.items():
                for column, second_value in second.items():
                    total += first_value * matrix.get((row, column), zero) * second_value
            result[left, right] = total
    return (result + result.transpose()) / 2


def source_eigenpairs(
    hamiltonian: dict[tuple[int, int], Any], dimension: int, context: Any
) -> tuple[list[Any], list[list[Any]], list[int]]:
    pairs: list[tuple[Any, list[Any]]] = []
    block_sizes: list[int] = []
    for vectors in symmetry_vectors(dimension, context):
        block_sizes.append(len(vectors))
        block = block_matrix(hamiltonian, vectors, context)
        values, columns = context.eigsy(block)
        for index in range(block.rows):
            full = [context.mpf(0)] * (dimension * dimension)
            for basis_index, basis_vector in enumerate(vectors):
                for state, coefficient in basis_vector.items():
                    full[state] += coefficient * columns[basis_index, index]
            pairs.append((values[index], full))
    pairs.sort(key=lambda item: item[0])
    energies = [item[0] for item in pairs]
    columns = [[item[1][row] for item in pairs] for row in range(dimension * dimension)]
    return energies, columns, block_sizes


def interval_from_point(value: Any, digits: int) -> Any:
    # ``nstr`` is a decimal truncation, not an exact enclosure.  Enlarge the
    # interval by one decimal unit at the retained precision so the rounded
    # eigendata are actually covered (including the mpmath display rounding).
    center = mp.mpf(mp.nstr(value, digits))
    radius = mp.mpf(10) ** (-digits)
    return mp.iv.mpf([center - radius, center + radius])


def lower(value: Any) -> Any:
    return mp.mpf(value.a)


def upper(value: Any) -> Any:
    return mp.mpf(value.b)


def interval_sum(values: Iterable[Any]) -> Any:
    return sum(values, mp.iv.mpf(0))


def upper_l2(values: Iterable[Any]) -> Any:
    total = mp.iv.mpf(0)
    for value in values:
        magnitude = max(abs(lower(value)), abs(upper(value)))
        total += mp.iv.mpf(magnitude) * mp.iv.mpf(magnitude)
    return upper(mp.iv.sqrt(total))


def row_abs_upper(matrix: dict[tuple[int, int], Any], dimension: int) -> Any:
    rows: defaultdict[int, list[Any]] = defaultdict(list)
    for (row, _column), value in matrix.items():
        rows[row].append(mp.iv.fabs(value))
    return max(upper(interval_sum(rows.get(row, []))) for row in range(dimension))


def gram_upper_from_enclosure(columns_interval: list[list[Any]], point_digits: int) -> Any:
    """Frobenius enclosure for Q^T Q-I without a 16-million-cell iv loop.

    The midpoint product is evaluated at the point precision.  Each entry's
    interval radius is then propagated with the elementary product bound, and
    the mpmath roundoff term is included via ``mp.eps``.  Taking the Frobenius
    norm of the common entry bound is conservative for the spectral quantity
    used by the polar-correction estimate.
    """
    rows = len(columns_interval)
    columns = len(columns_interval[0])
    midpoint_matrix = mp.matrix(rows, columns)
    radii: list[list[Any]] = []
    max_mid_abs = mp.mpf(0)
    max_radius = mp.mpf(0)
    for row in range(rows):
        row_radii: list[Any] = []
        for column in range(columns):
            value = columns_interval[row][column]
            lo = lower(value)
            hi = upper(value)
            center = (lo + hi) / 2
            radius = (hi - lo) / 2
            midpoint_matrix[row, column] = center
            row_radii.append(radius)
            max_mid_abs = max(max_mid_abs, abs(center))
            max_radius = max(max_radius, radius)
        radii.append(row_radii)
    gram = midpoint_matrix.T * midpoint_matrix
    entry_bound = mp.mpf(0)
    for left in range(columns):
        for right in range(columns):
            rounding = rows * mp.eps * (1 + max_mid_abs + max_radius) ** 2
            bound = rounding
            center_defect = abs(gram[left, right] - (1 if left == right else 0))
            for row in range(rows):
                left_mid = abs(midpoint_matrix[row, left])
                right_mid = abs(midpoint_matrix[row, right])
                left_radius = radii[row][left]
                right_radius = radii[row][right]
                bound += left_mid * right_radius + right_mid * left_radius + left_radius * right_radius
            entry_bound = max(entry_bound, center_defect + bound)
    return entry_bound * mp.sqrt(columns * columns)


def inflate(value: Any, amount: Any) -> Any:
    return mp.iv.mpf([lower(value) - amount, upper(value) + amount])


def source_residual_bounds(
    hamiltonian_interval: dict[tuple[int, int], Any],
    energies: list[Any],
    columns: list[list[Any]],
    dimension: int,
    source_digits: int,
) -> dict[str, Any]:
    size = dimension * dimension
    q_interval = [[interval_from_point(columns[row][column], source_digits) for column in range(size)] for row in range(size)]
    energy_interval = [interval_from_point(value, source_digits) for value in energies]
    rows: defaultdict[int, list[tuple[int, Any]]] = defaultdict(list)
    for (row, column), value in hamiltonian_interval.items():
        rows[row].append((column, value))
    # Propagate midpoint/radius bounds rather than invoking interval objects
    # for every multiply-add.  This is algebraically equivalent to directed
    # intervals here and keeps the 256x256 source check tractable.
    residual_square = mp.mpf(0)
    for column in range(size):
        for row in range(size):
            total = mp.mpf(0)
            radius = mp.mpf(0)
            for pivot, value in rows.get(row, []):
                h_lo, h_hi = lower(value), upper(value)
                h_mid, h_rad = (h_lo + h_hi) / 2, (h_hi - h_lo) / 2
                q_value = q_interval[pivot][column]
                q_lo, q_hi = lower(q_value), upper(q_value)
                q_mid, q_rad = (q_lo + q_hi) / 2, (q_hi - q_lo) / 2
                total += h_mid * q_mid
                radius += abs(h_mid) * q_rad + abs(q_mid) * h_rad + h_rad * q_rad
            q_value = q_interval[row][column]
            q_lo, q_hi = lower(q_value), upper(q_value)
            q_mid, q_rad = (q_lo + q_hi) / 2, (q_hi - q_lo) / 2
            e_value = energy_interval[column]
            e_lo, e_hi = lower(e_value), upper(e_value)
            e_mid, e_rad = (e_lo + e_hi) / 2, (e_hi - e_lo) / 2
            total -= q_mid * e_mid
            radius += abs(q_mid) * e_rad + abs(e_mid) * q_rad + q_rad * e_rad
            # Include a conservative point-arithmetic roundoff allowance.
            radius += (len(rows.get(row, [])) + 2) * mp.eps * (1 + abs(total) + radius)
            residual_square += (abs(total) + radius) ** 2
    residual_upper = mp.sqrt(residual_square)
    gram_upper = gram_upper_from_enclosure(q_interval, source_digits)
    norm_upper = row_abs_upper(hamiltonian_interval, size)
    lambda_upper = max(abs(value) for value in energies)
    delta = 2 * gram_upper
    if delta >= mp.mpf("0.5"):
        raise AssertionError(f"polar correction is not in its small-defect regime: {delta}")
    error = residual_upper + delta * (norm_upper + lambda_upper)
    return {
        "residual_upper": residual_upper,
        "gram_upper": gram_upper,
        "operator_norm_upper": norm_upper,
        "lambda_norm_upper": lambda_upper,
        "polar_delta_upper": delta,
        "spectral_approximation_error_upper": error,
        "columns_interval": q_interval,
        "energies_interval": energy_interval,
    }


def coordinate_residual_bounds(
    q_interval_sparse: dict[tuple[int, int], Any], q_values: list[Any], q_vectors: Any, dimension: int, source_digits: int
) -> dict[str, Any]:
    q_interval = [[q_interval_sparse.get((row, column), mp.iv.mpf(0)) for column in range(dimension)] for row in range(dimension)]
    vectors = [[interval_from_point(q_vectors[row, column], source_digits) for column in range(dimension)] for row in range(dimension)]
    values = [interval_from_point(value, source_digits) for value in q_values]
    residual_square = mp.mpf(0)
    for column in range(dimension):
        for row in range(dimension):
            total = mp.mpf(0)
            radius = mp.mpf(0)
            for pivot in range(dimension):
                q_value = q_interval[row][pivot]
                q_lo, q_hi = lower(q_value), upper(q_value)
                q_mid, q_rad = (q_lo + q_hi) / 2, (q_hi - q_lo) / 2
                v_value = vectors[pivot][column]
                v_lo, v_hi = lower(v_value), upper(v_value)
                v_mid, v_rad = (v_lo + v_hi) / 2, (v_hi - v_lo) / 2
                total += q_mid * v_mid
                radius += abs(q_mid) * v_rad + abs(v_mid) * q_rad + q_rad * v_rad
            v_value = vectors[row][column]
            v_lo, v_hi = lower(v_value), upper(v_value)
            v_mid, v_rad = (v_lo + v_hi) / 2, (v_hi - v_lo) / 2
            e_value = values[column]
            e_lo, e_hi = lower(e_value), upper(e_value)
            e_mid, e_rad = (e_lo + e_hi) / 2, (e_hi - e_lo) / 2
            total -= v_mid * e_mid
            radius += abs(v_mid) * e_rad + abs(e_mid) * v_rad + v_rad * e_rad
            radius += (dimension + 1) * mp.eps * (1 + abs(total) + radius)
            residual_square += (abs(total) + radius) ** 2
    residual_upper = mp.sqrt(residual_square)
    gram_upper = gram_upper_from_enclosure(vectors, source_digits)
    norm_upper = row_abs_upper(q_interval_sparse, dimension)
    lambda_upper = max(abs(value) for value in q_values)
    delta = 2 * gram_upper
    if delta >= mp.mpf("0.5"):
        raise AssertionError(f"coordinate polar correction is not in its small-defect regime: {delta}")
    error = residual_upper + delta * (norm_upper + lambda_upper)
    return {
        "residual_upper": residual_upper,
        "gram_upper": gram_upper,
        "operator_norm_upper": norm_upper,
        "lambda_norm_upper": lambda_upper,
        "polar_delta_upper": delta,
        "spectral_approximation_error_upper": error,
        "vectors_interval": vectors,
        "values_interval": values,
    }


def interval_hull(left: Any, right: Any) -> Any:
    return mp.iv.mpf([min(lower(left), lower(right)), max(upper(left), upper(right))])


def interval_cholesky_lower(matrix: list[list[Any]], probe: Any) -> tuple[bool, list[Any]]:
    size = len(matrix)
    factor = [[mp.iv.mpf(0) for _ in range(size)] for _ in range(size)]
    pivots: list[Any] = []
    for row in range(size):
        pivot = matrix[row][row] - probe - interval_sum(factor[row][index] * factor[row][index] for index in range(row))
        pivots.append(pivot)
        if lower(pivot) <= 0:
            return False, pivots
        factor[row][row] = mp.iv.sqrt(pivot)
        for next_row in range(row + 1, size):
            numerator = matrix[next_row][row] - interval_sum(factor[next_row][index] * factor[row][index] for index in range(row))
            factor[next_row][row] = numerator / factor[row][row]
    return True, pivots


def midpoint(value: Any) -> float:
    return float((lower(value) + upper(value)) / 2)


def interval_rayleigh_upper(matrix: list[list[Any]]) -> tuple[Any, list[float]]:
    center = np.asarray([[midpoint(value) for value in row] for row in matrix], dtype=float)
    values, vectors = np.linalg.eigh((center + center.T) / 2)
    if not np.isfinite(values[0]):
        raise AssertionError("nonfinite midpoint residual eigensolve")
    vector = vectors[:, 0]
    x = [mp.iv.mpf(Fraction.from_float(float(value)).numerator) / mp.iv.mpf(Fraction.from_float(float(value)).denominator) for value in vector]
    numerator = mp.iv.mpf(0)
    for row in range(len(matrix)):
        inner = interval_sum(matrix[row][column] * x[column] for column in range(len(matrix)))
        numerator += x[row] * inner
    denominator = interval_sum(value * value for value in x)
    if lower(denominator) <= 0:
        raise AssertionError("nonpositive Rayleigh denominator")
    return numerator / denominator, [float(value) for value in vector]


def build_residual_interval(
    probabilities: list[Any], momentum_squared: list[list[Any]], blocks: list[list[int]], chi: Any
) -> tuple[list[list[Any]], list[list[Any]], list[list[Any]]]:
    size = len(probabilities)
    conductance = [[mp.iv.mpf(0) for _ in range(size)] for _ in range(size)]
    for row in range(size):
        for column in range(size):
            if row != column:
                conductance[row][column] = (probabilities[row] + probabilities[column]) * momentum_squared[row][column] / (2 * chi)
    symmetric = [[mp.iv.mpf(0) for _ in range(size)] for _ in range(size)]
    for row in range(size):
        for column in range(size):
            symmetric[row][column] = interval_hull(conductance[row][column], conductance[column][row])
    operator = [[mp.iv.mpf(0) for _ in range(size)] for _ in range(size)]
    for row in range(size):
        diagonal = interval_sum(symmetric[row])
        for column in range(size):
            laplacian = diagonal if row == column else -symmetric[row][column]
            operator[row][column] = laplacian / mp.iv.sqrt(probabilities[row] * probabilities[column])
    raw: list[list[Any]] = []
    for block in blocks:
        if len(block) < 2:
            raise AssertionError("residual block has fewer than two entries")
        anchor = block[0]
        for index in block[1:]:
            vector = [mp.iv.mpf(0) for _ in range(size)]
            vector[anchor] = mp.iv.sqrt(probabilities[index])
            vector[index] = -mp.iv.sqrt(probabilities[anchor])
            raw.append(vector)
    basis: list[list[Any]] = []
    for vector in raw:
        work = list(vector)
        for previous in basis:
            coefficient = interval_sum(left * right for left, right in zip(previous, work))
            work = [value - coefficient * base for value, base in zip(work, previous)]
        norm_square = interval_sum(value * value for value in work)
        if upper(norm_square) <= 0:
            raise AssertionError("interval residual basis lost positivity")
        norm = mp.iv.sqrt(norm_square)
        basis.append([value / norm for value in work])
    columns = [list(column) for column in zip(*basis)]
    compressed_size = len(columns[0])
    compressed = [[mp.iv.mpf(0) for _ in range(compressed_size)] for _ in range(compressed_size)]
    for left in range(compressed_size):
        for right in range(compressed_size):
            total = mp.iv.mpf(0)
            for row in range(size):
                inner = interval_sum(operator[row][column] * columns[column][right] for column in range(size))
                total += columns[row][left] * inner
            compressed[left][right] = total
    symmetric_compressed = [[mp.iv.mpf(0) for _ in range(compressed_size)] for _ in range(compressed_size)]
    for left in range(compressed_size):
        for right in range(compressed_size):
            symmetric_compressed[left][right] = interval_hull(compressed[left][right], compressed[right][left])
    return symmetric_compressed, columns, symmetric


def run(output: Path = DEFAULT_OUTPUT) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    source = manifest["source_contract"]
    contract = manifest["interval_contract"]
    fixture = json.loads(R419_MANIFEST.read_text(encoding="utf-8"))["finite_fixture"]
    dimension = int(source["cutoff_dimension"])
    volume = int(source["volume"])
    size = dimension * dimension
    point_digits = int(contract["point_decimal_digits"])
    source_digits = int(contract["source_decimal_digits_in_intervals"])
    mp.mp.dps = point_digits
    mp.iv.dps = int(contract["interval_decimal_digits"])
    checks: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        checks.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})

    check(
        "manifest identity",
        manifest["result_id"] == "R-433" and manifest["exploration_id"] == "EXP-001278" and manifest["claim_bearing"] is False,
        [manifest["result_id"], manifest["exploration_id"], manifest["claim_bearing"]],
        "R-433/EXP-001278/false",
        "provenance",
    )
    expected_hashes = {
        "r432_manifest_sha256": R432_MANIFEST,
        "r430_manifest_sha256": R430_MANIFEST,
        "r431_manifest_sha256": R431_MANIFEST,
        "r426_manifest_sha256": R426_MANIFEST,
        "r419_manifest_sha256": R419_MANIFEST,
    }
    check(
        "parent hashes",
        all(sha256(path) == manifest["upstream_authority"][key] for key, path in expected_hashes.items()),
        {key: sha256(path) for key, path in expected_hashes.items()},
        manifest["upstream_authority"],
        "authority",
    )
    check(
        "fixed source row",
        [volume, dimension, source["beta"], source["orientation"], source["target_emission_ordinal"], source["target_parent_coordinate"]]
        == [2, 16, "8", "right", 7, 6],
        [volume, dimension, source["beta"], source["orientation"], source["target_emission_ordinal"], source["target_parent_coordinate"]],
        "V2/d16/beta8/right/emission7/parent6",
        "fixture",
    )
    check("source dimension", size == 256, size, 256, "source")

    q_point, skew_point, h_point = source_sparse(dimension, fixture, interval=False)
    q_interval, skew_interval, h_interval = source_sparse(dimension, fixture, interval=True)
    cache_key = {
        "point_digits": point_digits,
        "source_digits": source_digits,
        "r432_manifest_sha256": sha256(R432_MANIFEST),
        "r419_manifest_sha256": sha256(R419_MANIFEST),
    }
    cached: dict[str, Any] | None = None
    if POINT_CACHE.is_file():
        try:
            candidate = json.loads(POINT_CACHE.read_text(encoding="utf-8"))
            if candidate.get("cache_key") == cache_key:
                cached = candidate
        except (OSError, ValueError, TypeError):
            cached = None
    if cached is None:
        energies, h_columns, block_sizes = source_eigenpairs(h_point, dimension, mp)
    else:
        energies = [mp.mpf(value) for value in cached["energies"]]
        h_columns = [[mp.mpf(value) for value in row] for row in cached["h_columns"]]
        block_sizes = [int(value) for value in cached["block_sizes"]]
    check("exchange/parity block dimensions", block_sizes == [72, 56, 64, 64], block_sizes, [72, 56, 64, 64], "symmetry")
    check("source eigenvalue ordering", all(energies[index] < energies[index + 1] for index in range(size - 1)), "strictly increasing", "strictly increasing", "source")

    if cached is None:
        h_bounds = source_residual_bounds(h_interval, energies, h_columns, dimension, source_digits)
    else:
        h_bounds = {key: mp.mpf(value) for key, value in cached["h_bounds"].items()}
        h_bounds["columns_interval"] = []
        h_bounds["energies_interval"] = []
    check("Hamiltonian residual enclosure", h_bounds["residual_upper"] < mp.mpf("1e-35"), h_bounds["residual_upper"], "<1e-35", "source interval")
    check("Hamiltonian Gram enclosure", h_bounds["gram_upper"] < mp.mpf("1e-35"), h_bounds["gram_upper"], "<1e-35", "source interval")
    check("Hamiltonian polar regime", h_bounds["polar_delta_upper"] < mp.mpf("0.5"), h_bounds["polar_delta_upper"], "<0.5", "source interval")

    if cached is None:
        q_point_dense = dense_from_sparse(q_point, dimension)
        q_values, q_vectors = mp.eigsy(q_point_dense)
        q_bounds = coordinate_residual_bounds(q_interval, [q_values[index] for index in range(dimension)], q_vectors, dimension, source_digits)
        cache_payload = {
            "cache_key": cache_key,
            "energies": [mp.nstr(value, 60) for value in energies],
            "h_columns": jsonable_matrix(h_columns),
            "block_sizes": block_sizes,
            "h_bounds": {key: mp.nstr(value, 60) for key, value in h_bounds.items() if key not in {"columns_interval", "energies_interval"}},
            "q_values": [mp.nstr(value, 60) for value in q_values],
            "q_vectors": jsonable_matrix([[q_vectors[row, column] for column in range(dimension)] for row in range(dimension)]),
            "q_bounds": {key: mp.nstr(value, 60) for key, value in q_bounds.items() if key not in {"vectors_interval", "values_interval"}},
        }
        atomic_json(POINT_CACHE, cache_payload)
    else:
        q_values = [mp.mpf(value) for value in cached["q_values"]]
        q_vectors = mp.matrix([[mp.mpf(value) for value in row] for row in cached["q_vectors"]])
        q_bounds = {key: mp.mpf(value) for key, value in cached["q_bounds"].items()}
        q_bounds["vectors_interval"] = [[interval_from_point(q_vectors[row, column], source_digits) for column in range(dimension)] for row in range(dimension)]
        q_bounds["values_interval"] = [interval_from_point(value, source_digits) for value in q_values]
    check("coordinate residual enclosure", q_bounds["residual_upper"] < mp.mpf("1e-35"), q_bounds["residual_upper"], "<1e-35", "coordinate interval")
    check("coordinate Gram enclosure", q_bounds["gram_upper"] < mp.mpf("1e-35"), q_bounds["gram_upper"], "<1e-35", "coordinate interval")

    h_error = h_bounds["spectral_approximation_error_upper"]
    q_error = q_bounds["spectral_approximation_error_upper"]
    h_delta = h_bounds["polar_delta_upper"]
    q_delta = q_bounds["polar_delta_upper"]
    lambda_hat = [mp.mpf(mp.nstr(value, source_digits)) for value in energies]
    qvec_hat = [[mp.mpf(mp.nstr(q_vectors[row, column], source_digits)) for column in range(dimension)] for row in range(dimension)]
    hvec_hat = [[mp.mpf(mp.nstr(h_columns[row][column], source_digits)) for column in range(size)] for row in range(size)]
    shift_safety = rational(mp, contract["shift_safety"])
    lower_shift = lambda_hat[0] - h_error - shift_safety
    lower_shift_interval = mp.iv.mpf(mp.nstr(lower_shift, source_digits))
    energy_intervals = [interval_from_point(value, source_digits) for value in lambda_hat]
    d_intervals = [mp.iv.exp(-mp.iv.mpf(str(source["beta"])) * (value - lower_shift_interval)) for value in energy_intervals]
    d_max = max(upper(value) for value in d_intervals)
    h_basis_delta = h_delta * (1 + mp.sqrt(1 + h_bounds["gram_upper"]))
    exponential_error = mp.mpf(str(source["beta"])) * h_error
    kernel_error = exponential_error + h_basis_delta * d_max
    q_basis_delta = q_delta * (1 + mp.sqrt(1 + q_bounds["gram_upper"]))
    coordinate_vector_error = 2 * q_basis_delta + q_basis_delta * q_basis_delta
    total_diagonal_error = kernel_error + coordinate_vector_error
    check("shifted source cone", lower_shift < lambda_hat[0], [lower_shift, lambda_hat[0]], "lower shift below approximate minimum", "Gibbs")
    check("Gibbs kernel error finite", total_diagonal_error < mp.mpf("1e-30"), total_diagonal_error, "<1e-30", "Gibbs")

    # Release the large temporary interval/eigenvector tables before building
    # the midpoint kernel matrices; this keeps the bounded finite run below
    # the Windows worker memory ceiling.
    h_interval = {}
    h_point = {}
    q_point = {}
    h_bounds["columns_interval"] = []
    gc.collect()

    # Form all 256 conditional coordinates as one Kronecker matrix and use
    # high-precision matrix products for the midpoint Gibbs kernel.  A single
    # norm/radius propagation then encloses every diagonal entry; this avoids
    # a prohibitively slow 16-million-cell interval multiply while retaining a
    # directed enclosure for the source rounding and eigensolver residual.
    coordinate_matrix = mp.matrix(size, size)
    for left in range(dimension):
        for right in range(dimension):
            coordinate_index = left * dimension + right
            for x in range(dimension):
                for y in range(dimension):
                    coordinate_matrix[x * dimension + y, coordinate_index] = qvec_hat[x][left] * qvec_hat[y][right]
    h_matrix = mp.matrix(size, size)
    d_mid = []
    d_radius = mp.mpf(0)
    for eigen_index in range(size):
        d_mid_value = (lower(d_intervals[eigen_index]) + upper(d_intervals[eigen_index])) / 2
        d_mid.append(d_mid_value)
        d_radius = max(d_radius, (upper(d_intervals[eigen_index]) - lower(d_intervals[eigen_index])) / 2)
        for state in range(size):
            h_matrix[state, eigen_index] = hvec_hat[state][eigen_index]
    weighted_h = mp.matrix(size, size)
    for state in range(size):
        for eigen_index in range(size):
            weighted_h[state, eigen_index] = h_matrix[state, eigen_index] * d_mid[eigen_index]
    kernel_mid = weighted_h * h_matrix.T
    diagonal_mid = coordinate_matrix.T * kernel_mid * coordinate_matrix

    h_radius = mp.mpf(0)
    h_max = mp.mpf(0)
    for row in range(size):
        for column in range(size):
            value = interval_from_point(h_columns[row][column], source_digits)
            h_radius = max(h_radius, (upper(value) - lower(value)) / 2)
            h_max = max(h_max, abs(h_matrix[row, column]))
    q_radius = mp.mpf(0)
    q_max = mp.mpf(0)
    for row in range(dimension):
        for column in range(dimension):
            value = q_bounds["vectors_interval"][row][column]
            q_radius = max(q_radius, (upper(value) - lower(value)) / 2)
            q_max = max(q_max, abs(qvec_hat[row][column]))
    h_matrix_norm = size * (h_max + h_radius)
    h_rounding_norm = size * h_radius
    d_norm = max(abs(value) for value in d_mid) + d_radius
    delta_kernel_rounding = (2 * h_matrix_norm * h_rounding_norm + h_rounding_norm * h_rounding_norm) * d_norm
    delta_kernel_rounding += (h_matrix_norm + h_rounding_norm) ** 2 * d_radius
    kernel_entry_error = kernel_error + delta_kernel_rounding
    coordinate_norm = mp.sqrt(size) * (q_max + q_radius) ** 2
    coordinate_entry_error = coordinate_vector_error
    kernel_norm = h_matrix_norm * h_matrix_norm * d_norm
    diagonal_radius = (2 * coordinate_norm * coordinate_entry_error + coordinate_entry_error * coordinate_entry_error) * kernel_norm
    diagonal_radius += (coordinate_norm + coordinate_entry_error) ** 2 * kernel_entry_error
    h_diagonal_intervals: list[Any] = [
        mp.iv.mpf([diagonal_mid[index, index] - diagonal_radius, diagonal_mid[index, index] + diagonal_radius])
        for index in range(size)
    ]
    parent = int(source["target_parent_coordinate"])
    row_diagonals = h_diagonal_intervals[parent * dimension : (parent + 1) * dimension]
    row_denominator = interval_sum(row_diagonals)
    probabilities = [value / row_denominator for value in row_diagonals]
    check("conditional row positivity", all(lower(value) > 0 for value in probabilities), [str(min(lower(value) for value in probabilities)), str(max(upper(value) for value in probabilities))], ">0", "Gibbs row")
    check("conditional row normalization", abs(lower(interval_sum(probabilities)) - 1) < mp.mpf("1e-30") and abs(upper(interval_sum(probabilities)) - 1) < mp.mpf("1e-30"), interval_sum(probabilities), "contains 1", "Gibbs row")

    point_probabilities = [mp.mpf((lower(value) + upper(value)) / 2) for value in probabilities]
    maximum = max(point_probabilities)
    phi = [mp.log(maximum) - mp.log(value) for value in point_probabilities]
    core = [index for index, value in enumerate(phi) if value < rational(mp, source["tail_threshold"])]
    tail = [index for index, value in enumerate(phi) if value >= rational(mp, source["tail_threshold"])]
    check("tail split identity", core == source["core_indices"] and tail == source["tail_indices"], [core, tail], [source["core_indices"], source["tail_indices"]], "row")
    max_interval = probabilities[point_probabilities.index(maximum)]
    for index in core:
        phi_interval = mp.iv.log(max_interval) - mp.iv.log(probabilities[index])
        check(f"core threshold {index}", upper(phi_interval) < rational(mp, source["tail_threshold"]), phi_interval, "<4", "row threshold")
    for index in tail:
        phi_interval = mp.iv.log(max_interval) - mp.iv.log(probabilities[index])
        check(f"tail threshold {index}", lower(phi_interval) > rational(mp, source["tail_threshold"]), phi_interval, ">4", "row threshold")

    q_vector_intervals = q_bounds["vectors_interval"]
    p_squared: list[list[Any]] = [[mp.iv.mpf(0) for _ in range(dimension)] for _ in range(dimension)]
    skew_norm = row_abs_upper(skew_interval, dimension)
    p_basis_delta = q_delta * (1 + mp.sqrt(1 + q_bounds["gram_upper"]))
    # For P=Q^T S Q, the two-sided perturbation contributes
    # 2||S||*delta + ||S||*delta^2; retaining only one side would not enclose
    # the projected momentum after polar correction.
    p_error = 2 * skew_norm * p_basis_delta + skew_norm * p_basis_delta * p_basis_delta
    for left in range(dimension):
        for right in range(dimension):
            total = mp.iv.mpf(0)
            for row in range(dimension):
                for column in range(dimension):
                    total += q_vector_intervals[row][left] * skew_interval.get((row, column), mp.iv.mpf(0)) * q_vector_intervals[column][right]
            # First enclose the projected momentum matrix element, then square
            # that enclosure.  Inflating the already-squared value by a linear
            # matrix error would mix units and is not a valid propagation rule.
            projected = inflate(total, p_error)
            p_squared[left][right] = projected * projected
    chi = rational(mp, fixture["chi"])
    compressed, basis, conductance = build_residual_interval(probabilities, p_squared, [core, tail], chi)
    gram = [[mp.iv.mpf(0) for _ in range(len(basis[0]))] for _ in range(len(basis[0]))]
    for left in range(len(gram)):
        for right in range(len(gram)):
            gram[left][right] = interval_sum(basis[row][left] * basis[row][right] for row in range(dimension))
    gram_ok = all(lower(gram[index][index]) <= 1 <= upper(gram[index][index]) and all(lower(gram[index][other]) <= 0 <= upper(gram[index][other]) for other in range(len(gram)) if other != index) for index in range(len(gram)))
    check("residual basis interval orthogonality", gram_ok, "diagonal contains 1 and off-diagonal contains 0", "orthonormal enclosure", "residual")
    maximum_width = max(upper(value) - lower(value) for row in compressed for value in row)
    check("residual matrix interval width", maximum_width < rational(mp, contract["maximum_matrix_interval_width"]), maximum_width, f"<{contract['maximum_matrix_interval_width']}", "residual")
    lower_probe = rational(mp, contract["lower_probe"])
    upper_probe = rational(mp, contract["upper_probe"])
    failure_probe = rational(mp, contract["cholesky_failure_probe"])
    lower_ok, lower_pivots = interval_cholesky_lower(compressed, mp.iv.mpf(mp.nstr(lower_probe, source_digits)))
    check("interval Cholesky lower bound", lower_ok and all(lower(pivot) > 0 for pivot in lower_pivots), min(lower(pivot) for pivot in lower_pivots), f">0 at {lower_probe}", "eigenvalue")
    failure_ok, failure_pivots = interval_cholesky_lower(compressed, mp.iv.mpf(mp.nstr(failure_probe, source_digits)))
    check("upper-side Cholesky probe rejected", failure_ok is False and any(upper(pivot) <= 0 for pivot in failure_pivots), [failure_ok, len(failure_pivots)], f"rejected at {failure_probe}", "eigenvalue")
    rayleigh, _vector = interval_rayleigh_upper(compressed)
    check("interval Rayleigh upper bound", upper(rayleigh) < upper_probe, [lower(rayleigh), upper(rayleigh)], f"<{upper_probe}", "eigenvalue")
    check("R-422 separation", lower_probe > rational(mp, manifest["expected_outcomes"]["target_gap_interval_above_r422_threshold"]), lower_probe - rational(mp, source["r422_reference"]), ">5e-7", "reference")
    check("R-426 direct separation", upper(rayleigh) < rational(mp, manifest["expected_outcomes"]["target_gap_interval_below_r426_threshold"]), rational(mp, source["r426_direct_reference"]) - upper(rayleigh), ">5e-7", "reference")
    bracket_width = upper(rayleigh) - lower_probe
    check("certified bracket width", bracket_width < rational(mp, contract["maximum_bracket_width"]), bracket_width, f"<{contract['maximum_bracket_width']}", "eigenvalue")

    scope = manifest["scope"]
    scope["original_source_interval_certified"] = True
    scope["exact_original_hamiltonian_certified"] = True
    scope["gibbs_kernel_interval_propagated"] = True
    scope["corrected_row_interval_propagated"] = True
    scope["residual_interval_certified"] = True
    scope["r422_separation_certified"] = True
    scope["r426_direct_separation_certified"] = True
    scope["residual_reuse_closed_for_original_source"] = False
    classification = "ORIGINAL_SOURCE_INTERVAL_CERTIFIED"
    derived = {
        "fixed_row": source,
        "symmetry_block_sizes": block_sizes,
        "point_decimal_digits": point_digits,
        "interval_decimal_digits": int(contract["interval_decimal_digits"]),
        "hamiltonian_dimension": size,
        "coordinate_eigenvalue_min": mp.nstr(q_values[0], 45),
        "coordinate_eigenvalue_max": mp.nstr(q_values[dimension - 1], 45),
        "hamiltonian_ground_energy_point": mp.nstr(lambda_hat[0], 45),
        "hamiltonian_top_energy_point": mp.nstr(lambda_hat[-1], 45),
        "hamiltonian_residual_upper": mp.nstr(h_bounds["residual_upper"], 45),
        "hamiltonian_gram_upper": mp.nstr(h_bounds["gram_upper"], 45),
        "hamiltonian_polar_delta_upper": mp.nstr(h_delta, 45),
        "hamiltonian_spectral_error_upper": mp.nstr(h_error, 45),
        "coordinate_residual_upper": mp.nstr(q_bounds["residual_upper"], 45),
        "coordinate_gram_upper": mp.nstr(q_bounds["gram_upper"], 45),
        "coordinate_polar_delta_upper": mp.nstr(q_delta, 45),
        "kernel_error_upper": mp.nstr(kernel_error, 45),
        "coordinate_vector_error_upper": mp.nstr(coordinate_vector_error, 45),
        "total_diagonal_error_upper": mp.nstr(total_diagonal_error, 45),
        "conditional_row_lower": [mp.nstr(lower(value), 45) for value in probabilities],
        "conditional_row_upper": [mp.nstr(upper(value), 45) for value in probabilities],
        "tail_split": {"core": core, "tail": tail},
        "maximum_residual_matrix_interval_width": mp.nstr(maximum_width, 45),
        "lower_probe": mp.nstr(lower_probe, 45),
        "upper_rayleigh_endpoint": mp.nstr(upper(rayleigh), 45),
        "rayleigh_interval": [mp.nstr(lower(rayleigh), 45), mp.nstr(upper(rayleigh), 45)],
        "bracket_width": mp.nstr(bracket_width, 45),
        "r422_separation_margin": mp.nstr(lower_probe - rational(mp, source["r422_reference"]), 45),
        "r426_separation_margin": mp.nstr(rational(mp, source["r426_direct_reference"]) - upper(rayleigh), 45),
        "source_interval_certified": True,
        "exact_original_hamiltonian_certified": True,
        "gibbs_kernel_interval_propagated": True,
        "corrected_row_interval_propagated": True,
        "residual_interval_certified": True,
        "r422_separation_certified": True,
        "r426_direct_separation_certified": True,
        "residual_reuse_closed_for_original_source": False,
        "classification": classification,
    }
    payload: dict[str, Any] = {
        "schema": "tect/pre-a-r433-primary/1.0",
        "manifest": MANIFEST.relative_to(REPO).as_posix(),
        "result_id": manifest["result_id"],
        "exploration_id": manifest["exploration_id"],
        "claim_id": manifest["claim_ids"][0],
        "run_kind": "primary",
        "verdict": classification,
        "assertion_count": len(checks),
        "assertions": checks,
        "derived": derived,
        "scope": scope,
        "source_hashes": {
            "primary": sha256(Path(__file__)),
            "manifest": sha256(MANIFEST),
            "r432_manifest": sha256(R432_MANIFEST),
            "r430_manifest": sha256(R430_MANIFEST),
            "r431_manifest": sha256(R431_MANIFEST),
            "r426_manifest": sha256(R426_MANIFEST),
            "r419_manifest": sha256(R419_MANIFEST),
        },
        "assumptions": manifest["assumptions"],
        "missing_assumptions": manifest["missing_assumptions"],
        "evidence_level": "T0 / EXECUTED VALIDATED FINITE ORIGINAL-SOURCE INTERVAL ENCLOSURE; NO UNIFORM OR PHYSICAL PROMOTION",
        "non_claims": manifest["non_claims"],
        "boundary": "This certificate encloses one finite V=2, d=16, beta=8 source row at corrected emission ordinal 7 (parent coordinate 6). It does not close residual reuse uniformly or identify a physical-empty branch.",
        "runtime": {"mpmath": mp.__version__, "point_decimal_digits": point_digits, "interval_decimal_digits": int(contract["interval_decimal_digits"])},
    }
    atomic_json(output, payload)
    print(f"R-433 PRIMARY {classification} {len(checks)}/{len(checks)} bracket=[{derived['lower_probe']},{derived['upper_rayleigh_endpoint']}]", flush=True)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    destination = args.output if args.output.is_absolute() else REPO / args.output
    payload = run(destination)
    if args.self_test:
        assert payload["verdict"] == "ORIGINAL_SOURCE_INTERVAL_CERTIFIED"
        assert payload["scope"]["original_source_interval_certified"] is True
        assert payload["scope"]["residual_reuse_closed_for_original_source"] is False
        print("R-433 PRIMARY SELFTEST: PASS (validated original-source interval)", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

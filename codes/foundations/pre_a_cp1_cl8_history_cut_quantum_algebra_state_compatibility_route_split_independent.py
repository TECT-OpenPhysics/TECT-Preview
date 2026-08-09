#!/usr/bin/env python3
"""Independent stdlib/Fraction audit for the CL8 history-cut quantum route."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


__version__ = "0.2.0"
REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-cl8-history-cut-quantum-algebra-state-compatibility-route-split"
CANDIDATE_ID = "PA-CP1-CL8-HISTORY-CUT-QUANTUM-ALGEBRA-STATE-COMPATIBILITY-ROUTE-SPLIT-v0"
RESULT_ID = "PA-CP1-CL8-EXACT-HISTORY-CUT-BH-CCR-STATE-TRANSPORT-AND-RAW-LEG-NOGO"
NEGATIVES = ("NG-2026-08-04-PRE-A-CP1-CL8-HISTORY-CUT-RAW-LEG-TENSOR-FACTORIZATION",)
PARENT_IDS = (
    "PA-CP1-CL8-CONTROLLER-FREE-COMMON-PARENT-ROUTE-SPLIT-v0",
    "PA-CP1-CL8-COMMON-FINITE-REGULATOR-CHARACTERISTIC-ROUTE-SPLIT-v0",
    "PA-CP1-CL8-FINITE-QUANTUM-STATE-BOUNDARY-FORK-v0",
    "PA-CP1-CL8-QUANTUM-BOUNDARY-ALGEBRA-INTERTWINER-ROUTE-SPLIT-v0",
    "PA-CP1-CL8-PASSIVE-TWO-ARM-CHARACTERISTIC-CONTROL-ROUTE-SPLIT-v0",
    "PA-CP1-CL8-INTERACTING-TWO-ARM-WORK-ROUTE-SPLIT-v0",
)
PARENTS = (
    REPO / "strategy/pre-a-cp1-cl8-controller-free-common-parent-route-split-manifest.json",
    REPO / "strategy/pre-a-cp1-cl8-common-finite-regulator-characteristic-route-split-manifest.json",
    REPO / "strategy/pre-a-cp1-cl8-finite-quantum-state-boundary-fork-manifest.json",
    REPO / "strategy/pre-a-cp1-cl8-quantum-boundary-algebra-intertwiner-route-split-manifest.json",
    REPO / "strategy/pre-a-cp1-cl8-passive-two-arm-characteristic-control-route-split-manifest.json",
    REPO / "strategy/pre-a-cp1-cl8-interacting-two-arm-work-route-split-manifest.json",
)
EXPECTED_VERDICT = (
    "CLOSE EXACT FINITE OPEN ALL-CUT B(H) UNITARIES AND CUT CCR, PLUS THE "
    "BALANCED-EVEN-M PERIODIC D-K-D AUTOMORPHISM AND NORMAL-STATE-TRANSPORT "
    "INTERTWINER; RETAIN FIXED WEYL-CSTAR INVARIANCE, STATIONARITY/SELECTION, "
    "INTER-REGULATOR, CONTINUUM/HADAMARD, 1D-TO-3D, C6, CP1, AND PRE-A GATES"
)
SCHEMA = f"tect/{SLUG}-independent/0.2"
SCRIPT = Path(__file__).resolve()
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260804.md"
DEFAULT_OUTPUT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / f"2026-08-04-independent-{SLUG}/result.json"
)

Vector = tuple[Fraction, ...]
MatrixF = list[list[Fraction]]


def f(numerator: int, denominator: int = 1) -> Fraction:
    return Fraction(numerator, denominator)


def matmul(left: MatrixF, right: MatrixF) -> MatrixF:
    return [
        [sum((left[row][inner] * right[inner][column] for inner in range(len(right))), f(0)) for column in range(len(right[0]))]
        for row in range(len(left))
    ]


def transpose(matrix: MatrixF) -> MatrixF:
    return [list(row) for row in zip(*matrix)]


def identity(size: int) -> MatrixF:
    return [[f(1) if row == column else f(0) for column in range(size)] for row in range(size)]


def matadd(left: MatrixF, right: MatrixF) -> MatrixF:
    return [[left[row][column] + right[row][column] for column in range(len(left[0]))] for row in range(len(left))]


def matsub(left: MatrixF, right: MatrixF) -> MatrixF:
    return [[left[row][column] - right[row][column] for column in range(len(left[0]))] for row in range(len(left))]


def matscale(coefficient: Fraction, matrix: MatrixF) -> MatrixF:
    return [[coefficient * value for value in row] for row in matrix]


def matrix_power(matrix: MatrixF, exponent: int) -> MatrixF:
    result = identity(len(matrix))
    base = matrix
    power = exponent
    while power:
        if power % 2:
            result = matmul(result, base)
        base = matmul(base, base)
        power //= 2
    return result


def determinant(matrix: MatrixF) -> Fraction:
    work = [list(row) for row in matrix]
    result = f(1)
    for column in range(len(work)):
        pivot = next((row for row in range(column, len(work)) if work[row][column] != 0), None)
        if pivot is None:
            return f(0)
        if pivot != column:
            work[column], work[pivot] = work[pivot], work[column]
            result = -result
        pivot_value = work[column][column]
        result *= pivot_value
        for row in range(column + 1, len(work)):
            multiplier = work[row][column] / pivot_value
            for inner in range(column, len(work)):
                work[row][inner] -= multiplier * work[column][inner]
    return result


def trace(matrix: MatrixF) -> Fraction:
    return sum((matrix[index][index] for index in range(len(matrix))), f(0))


def serial(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value).replace("\\", "/")
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set, frozenset)):
        return [serial(item) for item in value]
    return value


def sha256(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(serial(payload), stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(self, name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{group}: {name}: {actual!r} != {expected!r}")
        self.rows.append(
            {"name": name, "group": group, "status": "PASS", "actual": serial(actual), "expected": serial(expected)}
        )


def zero() -> Vector:
    return (f(0),) * 8


def vadd(left: Vector, right: Vector) -> Vector:
    return tuple(a + b for a, b in zip(left, right))


def vsub(left: Vector, right: Vector) -> Vector:
    return tuple(a - b for a, b in zip(left, right))


def vscale(coefficient: Fraction, value: Vector) -> Vector:
    return tuple(coefficient * item for item in value)


def vsum(values: Any) -> Vector:
    result = zero()
    for value in values:
        result = vadd(result, value)
    return result


def q3_edges() -> tuple[tuple[int, int], ...]:
    return tuple(
        (left, right)
        for left in range(8)
        for right in range(left + 1, 8)
        if (left ^ right) in (1, 2, 4)
    )


def q3_potential(values: Vector, data: dict[str, Any]) -> Fraction:
    total = sum((data["r"] * x * x / 2 + data["g"] * x**4 / 4 for x in values), f(0))
    for left, right in q3_edges():
        x = values[left]
        y = values[right]
        total += data["lambda"] * (x - y) ** 2 * (x * x + y * y) / 4
    return total


def q3_gradient(values: Vector, data: dict[str, Any]) -> Vector:
    result = [data["r"] * x + data["g"] * x**3 for x in values]
    for left, right in q3_edges():
        x = values[left]
        y = values[right]
        difference = x - y
        square_sum = x * x + y * y
        result[left] += data["lambda"] * (difference * square_sum + difference * difference * x) / 2
        result[right] += data["lambda"] * (-difference * square_sum + difference * difference * y) / 2
    return tuple(result)


def five_point_gradient(values: Vector, data: dict[str, Any]) -> Vector:
    result: list[Fraction] = []
    step = f(1)
    for index in range(8):
        samples: dict[int, Fraction] = {}
        for shift in (-2, -1, 1, 2):
            moved = list(values)
            moved[index] += shift * step
            samples[shift] = q3_potential(tuple(moved), data)
        result.append((samples[-2] - 8 * samples[-1] + 8 * samples[1] - samples[2]) / (12 * step))
    return tuple(result)


def fixture(name: str) -> dict[str, Any]:
    if name == "f0":
        data = {
            "name": name,
            "M": 4,
            "L": f(8),
            "chi": f(2),
            "c": f(3, 2),
            "r": f(-1, 2),
            "g": f(2),
            "lambda": f(1),
            "delta": f(1, 2),
            "hbar": f(3, 7),
        }
    elif name == "f1":
        data = {
            "name": name,
            "M": 6,
            "L": f(9),
            "chi": f(4, 3),
            "c": f(7, 9),
            "r": f(1, 5),
            "g": f(9, 7),
            "lambda": f(5, 6),
            "delta": f(-3, 10),
            "hbar": f(7, 8),
        }
    else:
        raise ValueError(name)
    data["a"] = data["L"] / data["M"]
    data["w"] = data["a"] / 8
    data["mu"] = data["chi"] * data["w"]
    data["ell"] = data["mu"] / data["delta"]
    data["kappa"] = data["c"] * data["delta"] ** 2 / (data["chi"] * data["a"] ** 2)
    data["beta"] = data["delta"] ** 2 / data["chi"]
    return data


def vector_fixture(data: dict[str, Any], offset: int) -> list[Vector]:
    result: list[Vector] = []
    for site in range(data["M"]):
        vector = [f(0)] * 8
        vector[(site + offset) % 8] = f((-1) ** (site + offset) * (site + 1), site + offset + 2)
        vector[(2 * site + offset + 3) % 8] += f(site + offset + 2, site + offset + 5)
        result.append(tuple(vector))
    return result


def ring_gradient(values: list[Vector], data: dict[str, Any]) -> list[Vector]:
    spatial = data["w"] * data["c"] / data["a"] ** 2
    result: list[Vector] = []
    for site, value in enumerate(values):
        laplace = vsub(vscale(2, value), vadd(values[(site - 1) % data["M"]], values[(site + 1) % data["M"]]))
        result.append(vadd(vscale(spatial, laplace), vscale(data["w"], q3_gradient(value, data))))
    return result


def history_step(previous: list[Vector], current: list[Vector], data: dict[str, Any]) -> list[Vector]:
    coefficient = data["delta"] ** 2 / data["mu"]
    gradient = ring_gradient(current, data)
    return [vsub(vsub(vscale(2, current[j]), previous[j]), vscale(coefficient, gradient[j])) for j in range(data["M"])]


def dkd_step(positions: list[Vector], momenta: list[Vector], data: dict[str, Any]) -> tuple[list[Vector], list[Vector]]:
    half = data["delta"] / (2 * data["mu"])
    midpoint = [vadd(positions[j], vscale(half, momenta[j])) for j in range(data["M"])]
    gradient = ring_gradient(midpoint, data)
    kicked = [vsub(momenta[j], vscale(data["delta"], gradient[j])) for j in range(data["M"])]
    output = [vadd(midpoint[j], vscale(half, kicked[j])) for j in range(data["M"])]
    return output, kicked


def local_f(value: Vector, data: dict[str, Any]) -> Vector:
    return vsub(vscale(2 * (1 - data["kappa"]), value), vscale(data["beta"], q3_gradient(value, data)))


def balanced_heights(M: int) -> list[tuple[int, ...]]:
    result: list[tuple[int, ...]] = []
    for deltas in itertools.product((-1, 1), repeat=M):
        if sum(deltas) != 0:
            continue
        heights = [0]
        for delta in deltas[:-1]:
            heights.append(heights[-1] + delta)
        if heights[0] - heights[-1] != deltas[-1]:
            raise AssertionError("periodic closure")
        result.append(tuple(heights))
    return result


def lower_neighbours(heights: tuple[int, ...] | list[int], site: int) -> tuple[int, ...]:
    M = len(heights)
    return tuple(k for k in ((site - 1) % M, (site + 1) % M) if heights[k] == heights[site] - 1)


def open_height_paths(down_steps: int, up_steps: int) -> list[tuple[int, ...]]:
    paths: list[tuple[int, ...]] = []
    length = down_steps + up_steps
    for down_positions in itertools.combinations(range(length), down_steps):
        down_set = set(down_positions)
        heights = [0]
        for position in range(length):
            heights.append(heights[-1] + (-1 if position in down_set else 1))
        paths.append(tuple(heights))
    return paths


def open_lower_neighbours(heights: tuple[int, ...] | list[int], site: int) -> tuple[int, ...]:
    return tuple(
        neighbour
        for neighbour in (site - 1, site + 1)
        if 0 <= neighbour < len(heights) and heights[neighbour] == heights[site] - 1
    )


def open_current_form(heights: tuple[int, ...], data: dict[str, Any]) -> dict[tuple[int, int], Fraction]:
    N = len(heights)
    form: dict[tuple[int, int], Fraction] = {}
    for site in range(N):
        wedge_add(form, N + site, site, data["ell"])
    for left in range(N - 1):
        right = left + 1
        high, low = (left, right) if heights[left] > heights[right] else (right, left)
        wedge_add(form, N + low, high, -data["ell"] * data["kappa"])
    return form


def open_darboux_form(heights: tuple[int, ...], data: dict[str, Any]) -> dict[tuple[int, int], Fraction]:
    N = len(heights)
    form: dict[tuple[int, int], Fraction] = {}
    for site in range(N):
        wedge_add(form, N + site, site, data["ell"])
        for lower in open_lower_neighbours(heights, site):
            wedge_add(form, N + lower, site, -data["ell"] * data["kappa"])
    return form


def open_adjacency(heights: tuple[int, ...]) -> MatrixF:
    N = len(heights)
    matrix = [[f(0) for _ in range(N)] for _ in range(N)]
    for high in range(N):
        for lower in open_lower_neighbours(heights, high):
            matrix[high][lower] = f(1)
    return matrix


def open_transform(heights: tuple[int, ...], data: dict[str, Any]) -> MatrixF:
    N = len(heights)
    matrix = [[f(0) for _ in range(2 * N)] for _ in range(2 * N)]
    for site in range(N):
        matrix[site][site] = f(1)
        matrix[N + site][N + site] = data["ell"]
        for lower in open_lower_neighbours(heights, site):
            matrix[N + site][N + lower] = -data["ell"] * data["kappa"]
    return matrix


def open_force(value: Fraction, data: dict[str, Any]) -> Fraction:
    return 2 * (1 - data["kappa"]) * value - data["beta"] * (data["r"] * value + data["g"] * value**3)


def open_cut_darboux(A: list[Fraction], B: list[Fraction], heights: tuple[int, ...] | list[int], data: dict[str, Any]) -> tuple[list[Fraction], list[Fraction]]:
    Q = list(A)
    P = [
        data["ell"] * (B[site] - data["kappa"] * sum((B[lower] for lower in open_lower_neighbours(heights, site)), f(0)))
        for site in range(len(heights))
    ]
    return Q, P


def open_ready_valleys(heights: tuple[int, ...] | list[int]) -> tuple[int, ...]:
    return tuple(
        site
        for site in range(1, len(heights) - 1)
        if heights[site - 1] == heights[site] + 1 and heights[site + 1] == heights[site] + 1
    )


def open_raw_flip(A: list[Fraction], B: list[Fraction], heights: tuple[int, ...] | list[int], site: int, data: dict[str, Any]) -> tuple[list[Fraction], list[Fraction], tuple[int, ...]]:
    if site not in open_ready_valleys(heights):
        raise ValueError("not an open valley")
    left, right = site - 1, site + 1
    A_out = list(A)
    B_out = list(B)
    A_out[site] = data["kappa"] * (A[left] + A[right]) - A[site] + open_force(B[site], data)
    B_out[site] = data["kappa"] * (B[left] + B[right]) - B[site] + open_force(A_out[site], data)
    h_out = list(heights)
    h_out[site] += 2
    return A_out, B_out, tuple(h_out)


def open_staged_flip(Q: list[Fraction], P: list[Fraction], site: int, data: dict[str, Any]) -> tuple[list[Fraction], list[Fraction]]:
    left, right = site - 1, site + 1
    Q_now = list(Q)
    P_now = list(P)
    Q_now[site] -= open_force(P_now[site] / data["ell"], data)
    Q_now[site] = -Q_now[site]
    P_now[site] = -P_now[site]
    Q_now[site] += data["kappa"] * (Q_now[left] + Q_now[right])
    P_now[left] -= data["kappa"] * P_now[site]
    P_now[right] -= data["kappa"] * P_now[site]
    P_now[site] += data["ell"] * open_force(Q_now[site], data)
    return Q_now, P_now


def open_inverse_staged_flip(Q_out: list[Fraction], P_out: list[Fraction], site: int, data: dict[str, Any]) -> tuple[list[Fraction], list[Fraction]]:
    left, right = site - 1, site + 1
    Q_now = list(Q_out)
    P_now = list(P_out)
    P_now[site] -= data["ell"] * open_force(Q_now[site], data)
    Q_now[site] -= data["kappa"] * (Q_now[left] + Q_now[right])
    P_now[left] += data["kappa"] * P_now[site]
    P_now[right] += data["kappa"] * P_now[site]
    Q_now[site] = -Q_now[site]
    P_now[site] = -P_now[site]
    Q_now[site] += open_force(P_now[site] / data["ell"], data)
    return Q_now, P_now


def enumerate_open_sweeps(heights: tuple[int, ...], target: tuple[int, ...]) -> list[tuple[int, ...]]:
    if heights == target:
        return [tuple()]
    sweeps: list[tuple[int, ...]] = []
    for site in open_ready_valleys(heights):
        updated = list(heights)
        updated[site] += 2
        for tail in enumerate_open_sweeps(tuple(updated), target):
            sweeps.append((site,) + tail)
    return sweeps


def apply_open_sweep(A: list[Fraction], B: list[Fraction], heights: tuple[int, ...], sweep: tuple[int, ...], data: dict[str, Any]) -> tuple[list[Fraction], list[Fraction], tuple[int, ...]]:
    A_now, B_now, h_now = list(A), list(B), tuple(heights)
    for site in sweep:
        A_now, B_now, h_now = open_raw_flip(A_now, B_now, h_now, site, data)
    return A_now, B_now, h_now


def wedge_add(form: dict[tuple[int, int], Fraction], left: int, right: int, coefficient: Fraction) -> None:
    if left == right:
        return
    if left < right:
        key, signed = (left, right), coefficient
    else:
        key, signed = (right, left), -coefficient
    form[key] = form.get(key, f(0)) + signed
    if form[key] == 0:
        del form[key]


def current_form(heights: tuple[int, ...], data: dict[str, Any]) -> dict[tuple[int, int], Fraction]:
    M = data["M"]
    form: dict[tuple[int, int], Fraction] = {}
    for site in range(M):
        wedge_add(form, M + site, site, data["ell"])
    for site in range(M):
        other = (site + 1) % M
        high, low = (site, other) if heights[site] > heights[other] else (other, site)
        wedge_add(form, M + low, high, -data["ell"] * data["kappa"])
    return form


def darboux_form(heights: tuple[int, ...], data: dict[str, Any]) -> dict[tuple[int, int], Fraction]:
    M = data["M"]
    form: dict[tuple[int, int], Fraction] = {}
    for site in range(M):
        wedge_add(form, M + site, site, data["ell"])
        for lower in lower_neighbours(heights, site):
            wedge_add(form, M + lower, site, -data["ell"] * data["kappa"])
    return form


def cut_darboux(A: list[Vector], B: list[Vector], heights: tuple[int, ...] | list[int], data: dict[str, Any]) -> tuple[list[Vector], list[Vector]]:
    Q = list(A)
    P = [
        vscale(
            data["ell"],
            vsub(B[site], vscale(data["kappa"], vsum(B[k] for k in lower_neighbours(heights, site)))),
        )
        for site in range(data["M"])
    ]
    return Q, P


def reconstruct_B_coefficients(heights: tuple[int, ...], data: dict[str, Any]) -> list[list[Fraction]]:
    M = data["M"]
    coefficients = [[f(0) for _ in range(M)] for _ in range(M)]
    for site in sorted(range(M), key=lambda j: heights[j]):
        coefficients[site][site] += 1 / data["ell"]
        for lower in lower_neighbours(heights, site):
            for source in range(M):
                coefficients[site][source] += data["kappa"] * coefficients[lower][source]
    return coefficients


def valley_flip_raw(A: list[Vector], B: list[Vector], heights: list[int], site: int, data: dict[str, Any]) -> tuple[list[Vector], list[Vector], list[int]]:
    M = data["M"]
    left, right = (site - 1) % M, (site + 1) % M
    if not (heights[left] == heights[site] + 1 and heights[right] == heights[site] + 1):
        raise ValueError("not a valley")
    A_out = list(A)
    B_out = list(B)
    A_out[site] = vadd(vsub(vscale(data["kappa"], vadd(A[left], A[right])), A[site]), local_f(B[site], data))
    B_out[site] = vadd(vsub(vscale(data["kappa"], vadd(B[left], B[right])), B[site]), local_f(A_out[site], data))
    heights_out = list(heights)
    heights_out[site] += 2
    return A_out, B_out, heights_out


def canonical_valley_flip(Q: list[Vector], P: list[Vector], heights: list[int], site: int, data: dict[str, Any]) -> tuple[list[Vector], list[Vector]]:
    M = data["M"]
    left, right = (site - 1) % M, (site + 1) % M
    Q_out = list(Q)
    P_out = list(P)
    P_out[left] = vadd(P[left], vscale(data["kappa"], P[site]))
    P_out[right] = vadd(P[right], vscale(data["kappa"], P[site]))
    Q_out[site] = vadd(vsub(vscale(data["kappa"], vadd(Q[left], Q[right])), Q[site]), local_f(vscale(1 / data["ell"], P[site]), data))
    P_out[site] = vadd(vscale(-1, P[site]), vscale(data["ell"], local_f(Q_out[site], data)))
    return Q_out, P_out


def factorized_valley_flip(Q: list[Vector], P: list[Vector], site: int, data: dict[str, Any]) -> tuple[list[Vector], list[Vector]]:
    M = len(Q)
    left, right = (site - 1) % M, (site + 1) % M
    Q_now = list(Q)
    P_now = list(P)
    Q_now[site] = vsub(Q_now[site], local_f(vscale(1 / data["ell"], P_now[site]), data))
    Q_now[site] = vscale(-1, Q_now[site])
    P_now[site] = vscale(-1, P_now[site])
    Q_now[site] = vadd(Q_now[site], vscale(data["kappa"], vadd(Q_now[left], Q_now[right])))
    P_now[left] = vsub(P_now[left], vscale(data["kappa"], P_now[site]))
    P_now[right] = vsub(P_now[right], vscale(data["kappa"], P_now[site]))
    P_now[site] = vadd(P_now[site], vscale(data["ell"], local_f(Q_now[site], data)))
    return Q_now, P_now


def swapped_control_parity_valley_flip(Q: list[Vector], P: list[Vector], site: int, data: dict[str, Any]) -> tuple[list[Vector], list[Vector]]:
    M = len(Q)
    left, right = (site - 1) % M, (site + 1) % M
    Q_now = list(Q)
    P_now = list(P)
    Q_now[site] = vsub(Q_now[site], local_f(vscale(1 / data["ell"], P_now[site]), data))
    Q_now[site] = vadd(Q_now[site], vscale(data["kappa"], vadd(Q_now[left], Q_now[right])))
    P_now[left] = vsub(P_now[left], vscale(data["kappa"], P_now[site]))
    P_now[right] = vsub(P_now[right], vscale(data["kappa"], P_now[site]))
    Q_now[site] = vscale(-1, Q_now[site])
    P_now[site] = vscale(-1, P_now[site])
    P_now[site] = vadd(P_now[site], vscale(data["ell"], local_f(Q_now[site], data)))
    return Q_now, P_now


def inverse_factorized(Q_out: list[Vector], P_out: list[Vector], site: int, data: dict[str, Any]) -> tuple[list[Vector], list[Vector]]:
    M = data["M"]
    left, right = (site - 1) % M, (site + 1) % M
    Q_mid = list(Q_out)
    P_mid = list(P_out)
    P_mid[site] = vsub(P_mid[site], vscale(data["ell"], local_f(Q_mid[site], data)))
    Q_mid[site] = vscale(-1, Q_mid[site])
    P_mid[site] = vscale(-1, P_mid[site])
    Q = list(Q_mid)
    P = list(P_mid)
    Q[site] = vadd(vadd(Q_mid[site], vscale(data["kappa"], vadd(Q_mid[left], Q_mid[right]))), local_f(vscale(1 / data["ell"], P_mid[site]), data))
    P[left] = vsub(P_mid[left], vscale(data["kappa"], P_mid[site]))
    P[right] = vsub(P_mid[right], vscale(data["kappa"], P_mid[site]))
    return Q, P


def raw_checkerboard(previous: list[Vector], current: list[Vector], high_parity: int, data: dict[str, Any]) -> tuple[list[Vector], list[Vector], list[int]]:
    following = history_step(previous, current, data)
    A: list[Vector] = []
    B: list[Vector] = []
    heights: list[int] = []
    for site in range(data["M"]):
        if site % 2 == high_parity:
            A.append(current[site])
            B.append(following[site])
            heights.append(1)
        else:
            A.append(previous[site])
            B.append(current[site])
            heights.append(0)
    return A, B, heights


def decode_checkerboard(A: list[Vector], B: list[Vector], heights: list[int], data: dict[str, Any]) -> tuple[list[Vector], list[Vector]]:
    minimum = min(heights)
    current = [B[j] if heights[j] == minimum else A[j] for j in range(data["M"])]
    gradient = ring_gradient(current, data)
    coefficient = data["delta"] ** 2 / data["mu"]
    previous = [
        A[j] if heights[j] == minimum else vsub(vsub(vscale(2, current[j]), B[j]), vscale(coefficient, gradient[j]))
        for j in range(data["M"])
    ]
    return previous, current


def apply_valleys(A: list[Vector], B: list[Vector], heights: list[int], order: tuple[int, ...], data: dict[str, Any]) -> tuple[list[Vector], list[Vector], list[int]]:
    A_now, B_now, h_now = list(A), list(B), list(heights)
    for site in order:
        A_now, B_now, h_now = valley_flip_raw(A_now, B_now, h_now, site, data)
    return A_now, B_now, h_now


def audit_reference_anchor(audit: Audit, data: dict[str, Any]) -> None:
    name = data["name"]
    q_values = vector_fixture(data, 3)
    pi_values = vector_fixture(data, 6)
    gradient = ring_gradient(q_values, data)
    symplectic = [[f(1), -1 / data["ell"]], [data["ell"], f(0)]]
    standard = [[f(0), f(1)], [f(-1), f(0)]]
    audit.check(f"{name} independent reference low metaplectic symplectic matrix", matmul(matmul(transpose(symplectic), standard), symplectic) == standard, matmul(matmul(transpose(symplectic), standard), symplectic), standard, "reference_regularity")
    for high_parity in (0, 1):
        heights = [1 if site % 2 == high_parity else 0 for site in range(data["M"])]
        A: list[Vector] = []
        B: list[Vector] = []
        for site in range(data["M"]):
            if heights[site] == 1:
                A.append(q_values[site])
                B.append(vadd(q_values[site], vscale(1 / data["ell"], vsub(pi_values[site], vscale(data["delta"], gradient[site])))))
            else:
                A.append(vsub(q_values[site], vscale(1 / data["ell"], pi_values[site])))
                B.append(q_values[site])
        Q, P = cut_darboux(A, B, heights, data)
        for site in range(data["M"]):
            if heights[site] == 1:
                expected_Q = q_values[site]
                expected_P = vsub(
                    vadd(pi_values[site], vscale(data["ell"] * (1 - 2 * data["kappa"]), q_values[site])),
                    vscale(data["delta"] * data["w"], q3_gradient(q_values[site], data)),
                )
            else:
                expected_Q = vsub(q_values[site], vscale(1 / data["ell"], pi_values[site]))
                expected_P = vscale(data["ell"], q_values[site])
            audit.check(f"{name} parity {high_parity} independent reference decoder Q site {site}", Q[site] == expected_Q, Q[site], expected_Q, "reference_regularity")
            audit.check(f"{name} parity {high_parity} independent reference decoder P site {site}", P[site] == expected_P, P[site], expected_P, "reference_regularity")
        reconstructed_q = [A[site] if heights[site] == 1 else B[site] for site in range(data["M"])]
        reconstructed_pi = [
            vadd(vscale(data["ell"], vsub(B[site], A[site])), vscale(data["delta"], gradient[site]) if heights[site] == 1 else zero())
            for site in range(data["M"])
        ]
        audit.check(f"{name} parity {high_parity} independent reference q reconstruction", reconstructed_q == q_values, reconstructed_q, q_values, "reference_regularity")
        audit.check(f"{name} parity {high_parity} independent reference pi reconstruction", reconstructed_pi == pi_values, reconstructed_pi, pi_values, "reference_regularity")


def audit_ready_generator_support(audit: Audit) -> None:
    def supports(kind: str, center: int, neighbours: set[int]) -> tuple[set[int], set[int]]:
        if kind == "gp":
            return set(), {center}
        if kind == "gk":
            return set(neighbours), {center}
        return {center}, set()

    for label, left_center, right_center, left_neighbours, right_neighbours in (
        ("independent M4 shared-two-controls", 1, 3, {0, 2}, {0, 2}),
        ("independent M6 shared-one-control", 1, 3, {0, 2}, {2, 4}),
    ):
        audit.check(f"{label} distinct ready centers", left_center not in right_neighbours and right_center not in left_neighbours, [left_center, right_center], "not controls", "diamond_support")
        for left_kind in ("gp", "gk", "gq"):
            for right_kind in ("gp", "gk", "gq"):
                q_left, p_left = supports(left_kind, left_center, left_neighbours)
                q_right, p_right = supports(right_kind, right_center, right_neighbours)
                intersections = (p_left & q_right, q_left & p_right)
                audit.check(f"{label} {left_kind}-{right_kind} strong support commutation", intersections == (set(), set()), [sorted(item) for item in intersections], [[], []], "diamond_support")


def audit_open_rectangles(audit: Audit, data: dict[str, Any]) -> dict[str, Any]:
    fingerprints: dict[str, Any] = {}
    for down_steps, up_steps, expected_cuts, expected_sweeps in ((2, 2, 6, 2), (2, 3, 10, 5)):
        label = f"independent open-{down_steps}x{up_steps}"
        paths = open_height_paths(down_steps, up_steps)
        legs = down_steps + up_steps + 1
        audit.check(f"{label} every boundary path", len(paths) == expected_cuts, len(paths), expected_cuts, "open_all_cut")
        diamond_count = 0
        cover_count = 0
        for index, heights in enumerate(paths):
            current = open_current_form(heights, data)
            darboux = open_darboux_form(heights, data)
            audit.check(f"{label} cut {index} endpoint-aware two-form identity", darboux == current, darboux, current, "open_all_cut")
            transform_det = determinant(open_transform(heights, data))
            audit.check(f"{label} cut {index} one-species determinant", transform_det == data["ell"] ** legs, transform_det, data["ell"] ** legs, "open_all_cut")
            audit.check(f"{label} cut {index} full-eight-species determinant", transform_det**8 == data["ell"] ** (8 * legs), transform_det**8, data["ell"] ** (8 * legs), "open_all_cut")
            adjacency = open_adjacency(heights)
            zero_matrix = [[f(0) for _ in range(legs)] for _ in range(legs)]
            audit.check(f"{label} cut {index} nilpotent adjacency", matrix_power(adjacency, legs) == zero_matrix, matrix_power(adjacency, legs), zero_matrix, "open_all_cut")
            scaled = matscale(data["kappa"], adjacency)
            series = zero_matrix
            for power in range(legs):
                series = matadd(series, matrix_power(scaled, power))
            inverse_product = matmul(matsub(identity(legs), scaled), series)
            audit.check(f"{label} cut {index} finite inverse", inverse_product == identity(legs), inverse_product, identity(legs), "open_all_cut")
            endpoint_keys = ((legs - 1, legs), (0, 2 * legs - 1))
            audit.check(f"{label} cut {index} endpoint seam absent", all(key not in current for key in endpoint_keys), endpoint_keys, "absent", "open_all_cut")

            A = [f((index + 2) * (site + 1), site + 3) for site in range(legs)]
            B = [f((-1) ** (index + site) * (site + 2), index + site + 4) for site in range(legs)]
            ready = open_ready_valleys(heights)
            if len(ready) >= 2:
                diamond_count += 1
                first, second = ready[:2]
                left_route = apply_open_sweep(A, B, heights, (first, second), data)
                right_route = apply_open_sweep(A, B, heights, (second, first), data)
                audit.check(f"{label} cut {index} genuine open diamond", left_route == right_route, left_route, right_route, "open_all_cut")
            for site in ready:
                cover_count += 1
                Q, P = open_cut_darboux(A, B, heights, data)
                A_out, B_out, h_out = open_raw_flip(A, B, heights, site, data)
                Q_raw, P_raw = open_cut_darboux(A_out, B_out, h_out, data)
                Q_stage, P_stage = open_staged_flip(Q, P, site, data)
                audit.check(f"{label} cover {index}:{site} raw/staged Q", Q_raw == Q_stage, Q_raw, Q_stage, "open_cover")
                audit.check(f"{label} cover {index}:{site} raw/staged P", P_raw == P_stage, P_raw, P_stage, "open_cover")
                Q_back, P_back = open_inverse_staged_flip(Q_stage, P_stage, site, data)
                audit.check(f"{label} cover {index}:{site} staged inverse Q", Q_back == Q, Q_back, Q, "open_cover")
                audit.check(f"{label} cover {index}:{site} staged inverse P", P_back == P, P_back, P, "open_cover")

        minimal = tuple([0] + [-(site + 1) for site in range(down_steps)] + [-down_steps + site + 1 for site in range(up_steps)])
        maximal_steps = [1] * up_steps + [-1] * down_steps
        maximal_values = [0]
        for step in maximal_steps:
            maximal_values.append(maximal_values[-1] + step)
        maximal = tuple(maximal_values)
        sweeps = enumerate_open_sweeps(minimal, maximal)
        audit.check(f"{label} every saturated sweep", len(sweeps) == expected_sweeps, len(sweeps), expected_sweeps, "open_sweep")
        A0 = [f(site + 1, site + 2) for site in range(legs)]
        B0 = [f((-1) ** site * (site + 2), site + 3) for site in range(legs)]
        outputs = [apply_open_sweep(A0, B0, minimal, sweep, data) for sweep in sweeps]
        audit.check(f"{label} full sweep order independence", all(item == outputs[0] for item in outputs), len(outputs), expected_sweeps, "open_sweep")
        audit.check(f"{label} has a genuine diamond", diamond_count > 0, diamond_count, "positive", "open_sweep")
        fingerprints[f"open-{down_steps}x{up_steps}"] = {"cuts": len(paths), "legs": legs, "covers": cover_count, "diamonds": diamond_count, "sweeps": len(sweeps)}
    return fingerprints


def audit_fixture(audit: Audit, data: dict[str, Any]) -> dict[str, Any]:
    name = data["name"]
    M = data["M"]
    audit_reference_anchor(audit, data)
    cuts = balanced_heights(M)
    audit.check(f"{name} all balanced cuts enumerated", len(cuts) == math.comb(M, M // 2), len(cuts), math.comb(M, M // 2), "all_cut")
    for index, heights in enumerate(cuts):
        audit.check(f"{name} cut {index} two-form identity", darboux_form(heights, data) == current_form(heights, data), darboux_form(heights, data), current_form(heights, data), "all_cut")
        directed = [(lower, high) for high in range(M) for lower in lower_neighbours(heights, high)]
        audit.check(f"{name} cut {index} directed time increase", all(heights[high] == heights[lower] + 1 for lower, high in directed), directed, "strict increase", "all_cut")

    sample = vector_fixture(data, 2)[0]
    audit.check(f"{name} independent Q3 five-point derivative", five_point_gradient(sample, data) == q3_gradient(sample, data), five_point_gradient(sample, data), q3_gradient(sample, data), "q3")
    wrong_data = dict(data)
    wrong_data["lambda"] *= 2
    audit.check(f"{name} Q3 locking mutant rejected", q3_gradient(sample, wrong_data) != five_point_gradient(sample, data), "different", "potential derivative", "mutant")

    previous = vector_fixture(data, 1)
    current = vector_fixture(data, 4)
    following = history_step(previous, current, data)
    second = history_step(current, following, data)
    pi_current = [vscale(data["ell"], vsub(current[j], previous[j])) for j in range(M)]
    pi_next = [vsub(pi_current[j], vscale(data["delta"], ring_gradient(current, data)[j])) for j in range(M)]
    audit.check(f"{name} discrete Legendre momentum", all(pi_next[j] == vscale(data["ell"], vsub(following[j], current[j])) for j in range(M)), pi_next, "ell difference", "history")
    audit.check(f"{name} history kick-drift", all(following[j] == vadd(current[j], vscale(1 / data["ell"], pi_next[j])) for j in range(M)), following, "kick-drift", "history")

    original_q = [vscale(f(1, 2), vadd(previous[j], current[j])) for j in range(M)]
    original_p = [vscale(data["ell"], vsub(current[j], previous[j])) for j in range(M)]
    dkd_q, dkd_p = dkd_step(original_q, original_p, data)
    half = data["delta"] / (2 * data["mu"])
    decoded_previous = [vsub(dkd_q[j], vscale(half, dkd_p[j])) for j in range(M)]
    decoded_current = [vadd(dkd_q[j], vscale(half, dkd_p[j])) for j in range(M)]
    audit.check(f"{name} independent D-K-D midpoint first", decoded_previous == current, decoded_previous, current, "history")
    audit.check(f"{name} independent D-K-D midpoint second", decoded_current == following, decoded_current, following, "history")

    for high_parity in (0, 1):
        A, B, heights = raw_checkerboard(previous, current, high_parity, data)
        low_sites = tuple(j for j in range(M) if heights[j] == 0)
        Q, P = cut_darboux(A, B, heights, data)
        first = low_sites[0]
        Q_direct, P_direct = canonical_valley_flip(Q, P, heights, first, data)
        Q_factor, P_factor = factorized_valley_flip(Q, P, first, data)
        audit.check(f"{name} parity {high_parity} independent circuit Q", Q_factor == Q_direct, Q_factor, Q_direct, "circuit")
        audit.check(f"{name} parity {high_parity} independent circuit P", P_factor == P_direct, P_factor, P_direct, "circuit")
        if high_parity == 0:
            left, right = (first - 1) % M, (first + 1) % M
            Q_wrong, P_wrong = swapped_control_parity_valley_flip(Q, P, first, data)
            expected_q_difference = vscale(-2 * data["kappa"], vadd(Q[left], Q[right]))
            expected_left_p_difference = vscale(-2 * data["kappa"], P[first])
            audit.check(f"{name} independent staged order mutant central Q difference", vsub(Q_wrong[first], Q_direct[first]) == expected_q_difference, vsub(Q_wrong[first], Q_direct[first]), expected_q_difference, "mutant")
            audit.check(f"{name} independent staged order mutant retained P difference", vsub(P_wrong[left], P_direct[left]) == expected_left_p_difference, vsub(P_wrong[left], P_direct[left]), expected_left_p_difference, "mutant")
            audit.check(f"{name} independent staged order mutant Q witness nonzero", expected_q_difference != zero(), expected_q_difference, "nonzero", "mutant")
            audit.check(f"{name} independent staged order mutant P witness nonzero", expected_left_p_difference != zero(), expected_left_p_difference, "nonzero", "mutant")
        Q_back, P_back = inverse_factorized(Q_factor, P_factor, first, data)
        audit.check(f"{name} parity {high_parity} independent inverse Q", Q_back == Q, Q_back, Q, "circuit")
        audit.check(f"{name} parity {high_parity} independent inverse P", P_back == P, P_back, P, "circuit")
        A_one, B_one, h_one = valley_flip_raw(A, B, heights, first, data)
        Q_raw, P_raw = cut_darboux(A_one, B_one, h_one, data)
        audit.check(f"{name} parity {high_parity} raw/canonical Q", Q_raw == Q_direct, Q_raw, Q_direct, "circuit")
        audit.check(f"{name} parity {high_parity} raw/canonical P", P_raw == P_direct, P_raw, P_direct, "circuit")
        outputs = [apply_valleys(A, B, heights, order, data) for order in itertools.permutations(low_sites)]
        audit.check(f"{name} parity {high_parity} every ready order", all(item == outputs[0] for item in outputs), len(outputs), math.factorial(M // 2), "diamond")
        old, now = decode_checkerboard(A, B, heights, data)
        now_out, next_out = decode_checkerboard(outputs[0][0], outputs[0][1], outputs[0][2], data)
        audit.check(f"{name} parity {high_parity} decoder input", old == previous and now == current, "exact", "previous,current", "diagram")
        audit.check(f"{name} parity {high_parity} decoder output", now_out == current and next_out == following, "exact", "current,following", "diagram")

    checker = tuple(1 if j % 2 == 0 else 0 for j in range(M))
    coefficients = reconstruct_B_coefficients(checker, data)
    tensor_witness = coefficients[0][1]
    audit.check(f"{name} raw cross-leg bracket", tensor_witness == data["kappa"] / data["ell"], tensor_witness, data["kappa"] / data["ell"], "raw_tensor_nogo")
    audit.check(f"{name} raw cross-leg bracket nonzero", tensor_witness != 0, tensor_witness, "nonzero", "raw_tensor_nogo")
    audit.check(f"{name} raw onsite bracket", coefficients[0][0] == 1 / data["ell"], coefficients[0][0], 1 / data["ell"], "raw_ccr")
    audit.check(f"{name} independent-leg mutant rejected", tensor_witness != 0, tensor_witness, 0, "mutant")

    dimension = 8 * M
    mixed = (-data["ell"]) ** dimension
    audit.check(f"{name} FIO mixed Hessian determinant", mixed != 0, mixed, "nonzero", "unitary")
    audit.check(f"{name} normalization exponent", dimension // 2 == 4 * M, dimension // 2, 4 * M, "unitary")
    audit.check(f"{name} nonlinear cubic coefficient", -data["beta"] * data["g"] != 0, -data["beta"] * data["g"], "nonzero", "weyl_boundary")
    return {
        "M": M,
        "ell": data["ell"],
        "kappa": data["kappa"],
        "beta": data["beta"],
        "cut_count": len(cuts),
        "one_species_darboux_determinant": data["ell"] ** M,
        "full_eight_species_darboux_determinant": data["ell"] ** (8 * M),
        "tensor_witness": tensor_witness,
        "kernel_mixed_hessian_determinant": mixed,
        "kernel_normalization_power": dimension // 2,
        "parity_order_count": math.factorial(M // 2),
        "following_site0": following[0],
        "second_following_site0": second[0],
    }


def audit_state_direction(audit: Audit) -> dict[str, Any]:
    M_half = [[f(3, 5), f(-4, 5), f(0)], [f(4, 5), f(3, 5), f(0)], [f(0), f(0), f(1)]]
    U_DKD = [[f(5, 13), f(0), f(-12, 13)], [f(0), f(1), f(0)], [f(12, 13), f(0), f(5, 13)]]
    Lambda_C = identity(3)
    Lambda_D = [[f(0), f(1), f(0)], [f(0), f(0), f(1)], [f(1), f(0), f(0)]]
    audit.check("independent typed anchor noncommuting half-drift fixture", matmul(M_half, U_DKD) != matmul(U_DKD, M_half), matsub(matmul(M_half, U_DKD), matmul(U_DKD, M_half)), "nonzero", "typed_anchor")
    U_hist = matmul(matmul(M_half, U_DKD), transpose(M_half))
    Gamma_C = matmul(transpose(M_half), Lambda_C)
    Gamma_D = matmul(transpose(M_half), Lambda_D)
    audit.check("independent typed Gamma C equals half-drift adjoint Lambda C", Gamma_C == matmul(transpose(M_half), Lambda_C), Gamma_C, "typed", "typed_anchor")
    audit.check("independent typed Gamma D equals half-drift adjoint Lambda D", Gamma_D == matmul(transpose(M_half), Lambda_D), Gamma_D, "typed", "typed_anchor")

    same_time = matmul(transpose(Gamma_D), Gamma_C)
    same_time_history = matmul(transpose(Lambda_D), Lambda_C)
    physical = matmul(matmul(transpose(Gamma_D), U_DKD), Gamma_C)
    physical_history = matmul(matmul(transpose(Lambda_D), U_hist), Lambda_C)
    audit.check("independent typed same-time Gamma and Lambda maps agree", same_time == same_time_history, same_time, same_time_history, "typed_anchor")
    audit.check("independent typed same-time history diagram", matmul(Lambda_D, same_time) == Lambda_C, matmul(Lambda_D, same_time), Lambda_C, "typed_anchor")
    audit.check("independent typed same-time phase diagram", matmul(Gamma_D, same_time) == Gamma_C, matmul(Gamma_D, same_time), Gamma_C, "typed_anchor")
    audit.check("independent typed physical Gamma and Lambda maps agree", physical == physical_history, physical, physical_history, "typed_anchor")
    audit.check("independent typed physical history diagram", matmul(Lambda_D, physical) == matmul(U_hist, Lambda_C), matmul(Lambda_D, physical), matmul(U_hist, Lambda_C), "typed_anchor")
    audit.check("independent typed physical phase diagram", matmul(Gamma_D, physical) == matmul(U_DKD, Gamma_C), matmul(Gamma_D, physical), matmul(U_DKD, Gamma_C), "typed_anchor")

    hamiltonian = [[f(0), f(0), f(0)], [f(0), f(1), f(0)], [f(0), f(0), f(2)]]
    rho = [[f(4, 7), f(0), f(0)], [f(0), f(2, 7), f(0)], [f(0), f(0), f(1, 7)]]
    rho_C = matmul(matmul(transpose(Gamma_C), rho), Gamma_C)
    rho_D_same = matmul(matmul(transpose(Gamma_D), rho), Gamma_D)
    audit.check("independent typed same-time density covariance", matmul(matmul(same_time, rho_C), transpose(same_time)) == rho_D_same, matmul(matmul(same_time, rho_C), transpose(same_time)), rho_D_same, "state")
    rho_1 = matmul(matmul(U_DKD, rho), transpose(U_DKD))
    rho_D_1 = matmul(matmul(transpose(Gamma_D), rho_1), Gamma_D)
    audit.check("independent typed physical density covariance", matmul(matmul(physical, rho_C), transpose(physical)) == rho_D_1, matmul(matmul(physical, rho_C), transpose(physical)), rho_D_1, "state")
    audit.check("independent typed physical density trace", trace(rho_D_1) == 1, trace(rho_D_1), 1, "state")
    observable = [[f(2), f(1), f(0)], [f(1), f(-1), f(1)], [f(0), f(1), f(3)]]
    target_expectation = trace(matmul(rho_D_1, observable))
    source_expectation = trace(matmul(matmul(matmul(rho_C, transpose(physical)), observable), physical))
    audit.check("independent typed expectation direction", target_expectation == source_expectation, target_expectation, source_expectation, "state")

    energy_C = matmul(matmul(transpose(Gamma_C), hamiltonian), Gamma_C)
    energy_D = matmul(matmul(transpose(Gamma_D), hamiltonian), Gamma_D)
    audit.check("independent typed same-time energy ledger", matmul(matmul(transpose(same_time), energy_D), same_time) == energy_C, matmul(matmul(transpose(same_time), energy_D), same_time), energy_C, "energy")
    energy_defect = matsub(matmul(matmul(transpose(physical), energy_D), physical), energy_C)
    reference_defect = matmul(matmul(transpose(Gamma_C), matsub(matmul(matmul(transpose(U_DKD), hamiltonian), U_DKD), hamiltonian)), Gamma_C)
    audit.check("independent typed physical energy defect", energy_defect == reference_defect, energy_defect, reference_defect, "energy")
    shifted = matadd(hamiltonian, matscale(f(5), identity(3)))
    shifted_C = matmul(matmul(transpose(Gamma_C), shifted), Gamma_C)
    shifted_D = matmul(matmul(transpose(Gamma_D), shifted), Gamma_D)
    audit.check("independent typed additive shift cancels", matsub(matmul(matmul(transpose(physical), shifted_D), physical), shifted_C) == energy_defect, matsub(matmul(matmul(transpose(physical), shifted_D), physical), shifted_C), energy_defect, "energy")

    hamiltonian_co_1 = matmul(matmul(U_DKD, hamiltonian), transpose(U_DKD))
    audit.check("independent transported Gibbs commutes with co-moving energy", matsub(matmul(rho_1, hamiltonian_co_1), matmul(hamiltonian_co_1, rho_1)) == [[f(0)] * 3 for _ in range(3)], matsub(matmul(rho_1, hamiltonian_co_1), matmul(hamiltonian_co_1, rho_1)), "zero", "state_boundary")
    audit.check("independent transported Gibbs not fixed-energy stationary", matsub(matmul(rho_1, hamiltonian), matmul(hamiltonian, rho_1)) != [[f(0)] * 3 for _ in range(3)], matsub(matmul(rho_1, hamiltonian), matmul(hamiltonian, rho_1)), "nonzero", "state_boundary")
    ground = [[f(1), f(0), f(0)], [f(0), f(0), f(0)], [f(0), f(0), f(0)]]
    ground_1 = matmul(matmul(U_DKD, ground), transpose(U_DKD))
    audit.check("independent transported ground commutes with co-moving energy", matsub(matmul(ground_1, hamiltonian_co_1), matmul(hamiltonian_co_1, ground_1)) == [[f(0)] * 3 for _ in range(3)], matsub(matmul(ground_1, hamiltonian_co_1), matmul(hamiltonian_co_1, ground_1)), "zero", "state_boundary")
    audit.check("independent transported ground not fixed-energy ground", matsub(matmul(ground_1, hamiltonian), matmul(hamiltonian, ground_1)) != [[f(0)] * 3 for _ in range(3)], matsub(matmul(ground_1, hamiltonian), matmul(hamiltonian, ground_1)), "nonzero", "state_boundary")
    energy_D_co = matmul(matmul(transpose(Gamma_D), hamiltonian_co_1), Gamma_D)
    audit.check("independent cut Gibbs commutes with co-moving cut energy", matsub(matmul(rho_D_1, energy_D_co), matmul(energy_D_co, rho_D_1)) == [[f(0)] * 3 for _ in range(3)], matsub(matmul(rho_D_1, energy_D_co), matmul(energy_D_co, rho_D_1)), "zero", "state_boundary")
    audit.check("independent cut Gibbs not unchanged-energy stationary", matsub(matmul(rho_D_1, energy_D), matmul(energy_D, rho_D_1)) != [[f(0)] * 3 for _ in range(3)], matsub(matmul(rho_D_1, energy_D), matmul(energy_D, rho_D_1)), "nonzero", "state_boundary")

    bad_same_time = matmul(Gamma_D, transpose(Gamma_C))
    bad_physical = matmul(matmul(Gamma_D, U_DKD), transpose(Gamma_C))
    audit.check("independent reversed Gamma same-time mutant rejected", matmul(matmul(bad_same_time, rho_C), transpose(bad_same_time)) != rho_D_same, matmul(matmul(bad_same_time, rho_C), transpose(bad_same_time)), rho_D_same, "mutant")
    audit.check("independent reversed Gamma physical mutant rejected", matmul(matmul(bad_physical, rho_C), transpose(bad_physical)) != rho_D_1, matmul(matmul(bad_physical, rho_C), transpose(bad_physical)), rho_D_1, "mutant")
    audit.check("independent reversed Gamma energy mutant rejected", matsub(matmul(matmul(transpose(bad_physical), energy_D), bad_physical), energy_C) != reference_defect, matsub(matmul(matmul(transpose(bad_physical), energy_D), bad_physical), energy_C), reference_defect, "mutant")
    return {"same_time_map": same_time, "physical_map": physical, "transported_density": rho_D_1, "energy_defect": energy_defect, "fixed_energy_commutator": matsub(matmul(rho_1, hamiltonian), matmul(hamiltonian, rho_1))}


def run(output: Path) -> dict[str, Any]:
    audit = Audit()
    audit.check("independent Q3 graph count", len(q3_edges()) == 12, len(q3_edges()), 12, "q3")
    fingerprints = {name: audit_fixture(audit, fixture(name)) for name in ("f0", "f1")}
    audit_ready_generator_support(audit)
    open_fingerprints = audit_open_rectangles(audit, fixture("f0"))
    state = audit_state_direction(audit)
    for parent, parent_id in zip(PARENTS, PARENT_IDS):
        record = json.loads(parent.read_text(encoding="utf-8"))
        audit.check(f"parent identity {parent_id}", record["candidate_id"] == parent_id, record["candidate_id"], parent_id, "parents")
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    audit.check("manifest candidate identity", manifest["candidate_id"] == CANDIDATE_ID, manifest["candidate_id"], CANDIDATE_ID, "manifest")
    audit.check("manifest result identity", manifest["result_id"] == RESULT_ID, manifest["result_id"], RESULT_ID, "manifest")
    audit.check("manifest parent identities", tuple(manifest["parent_ids"]) == PARENT_IDS, manifest["parent_ids"], list(PARENT_IDS), "manifest")
    audit.check("manifest negative identity", tuple(manifest["negative_ids"]) == NEGATIVES, manifest["negative_ids"], list(NEGATIVES), "manifest")
    audit.check("manifest scoped verdict", manifest["verdict"] == EXPECTED_VERDICT, manifest["verdict"], EXPECTED_VERDICT, "manifest")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "scope")
    payload = {
        "schema": SCHEMA,
        "candidate_id": CANDIDATE_ID,
        "result_id": RESULT_ID,
        "parent_ids": list(PARENT_IDS),
        "negative_ids": list(NEGATIVES),
        "claim_bearing": manifest["claim_bearing"],
        "verdict": manifest["verdict"],
        "status": manifest["status"],
        "script_version": __version__,
        "script_sha256": sha256(SCRIPT),
        "manifest_sha256": sha256(MANIFEST),
        "certificate_sha256": sha256(CERTIFICATE),
        "parent_sha256": {parent_id: sha256(parent) for parent_id, parent in zip(PARENT_IDS, PARENTS)},
        "invariants": {"fixtures": fingerprints, "open_rectangles": open_fingerprints, "state_control": state},
        "scope": manifest["scope"],
        "assertions": audit.rows,
        "assertion_summary": {"passed": len(audit.rows), "total": len(audit.rows)},
        "next_gate": manifest["gate_resolution"]["next_gate"],
        "no_overclaim": manifest["no_overclaim"],
    }
    atomic_json(output, payload)
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = run(args.output)
    summary = payload["assertion_summary"]
    print(f"PASS {summary['passed']}/{summary['total']} -> {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

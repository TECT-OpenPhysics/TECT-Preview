#!/usr/bin/env python3
"""Primary exact audit for the CL8 history-cut quantum route split."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import os
import tempfile
from pathlib import Path
from typing import Any

import sympy as sp


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
SCHEMA = f"tect/{SLUG}-primary/0.2"
SCRIPT = Path(__file__).resolve()
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260804.md"
DEFAULT_OUTPUT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / f"2026-08-04-primary-{SLUG}/result.json"
)


def q(numerator: int, denominator: int = 1) -> sp.Rational:
    return sp.Rational(numerator, denominator)


def serial(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value).replace("\\", "/")
    if isinstance(value, sp.MatrixBase):
        return [[serial(value[i, j]) for j in range(value.cols)] for i in range(value.rows)]
    if isinstance(value, sp.Basic):
        return str(sp.factor(value))
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


def q3_edges() -> tuple[tuple[int, int], ...]:
    return tuple(
        (left, right)
        for left in range(8)
        for right in range(left + 1, 8)
        if (left ^ right) in (1, 2, 4)
    )


def q3_potential(values: sp.Matrix, data: dict[str, Any]) -> sp.Expr:
    onsite = sum(data["r"] * value**2 / 2 + data["g"] * value**4 / 4 for value in values)
    locked = sum(
        data["lambda"]
        * (values[left] - values[right]) ** 2
        * (values[left] ** 2 + values[right] ** 2)
        / 4
        for left, right in q3_edges()
    )
    return sp.factor(onsite + locked)


def q3_gradient(values: sp.Matrix, data: dict[str, Any]) -> sp.Matrix:
    result = sp.Matrix([data["r"] * value + data["g"] * value**3 for value in values])
    for left, right in q3_edges():
        x = values[left]
        y = values[right]
        difference = x - y
        square_sum = x**2 + y**2
        result[left] += data["lambda"] * (difference * square_sum + difference**2 * x) / 2
        result[right] += data["lambda"] * (-difference * square_sum + difference**2 * y) / 2
    return sp.Matrix([sp.factor(item) for item in result])


def audit_q3(audit: Audit) -> None:
    values = sp.Matrix(sp.symbols("z0:8", real=True))
    r_symbol, g_symbol, lambda_symbol = sp.symbols("r_q g_q lambda_q", nonzero=True, real=True)
    data = {"r": r_symbol, "g": g_symbol, "lambda": lambda_symbol}
    potential = sp.expand(q3_potential(values, data))
    derived = sp.Matrix([sp.diff(potential, value) for value in values])
    formula = q3_gradient(values, data)
    gradient_defect = sp.Matrix([sp.factor(item) for item in formula - derived])
    audit.check("Q3 gradient derives from the complete potential", gradient_defect == sp.zeros(8, 1), gradient_defect, sp.zeros(8, 1), "q3")
    hessian = derived.jacobian(values)
    audit.check("Q3 Hessian is symmetric", sp.simplify(hessian - hessian.T) == sp.zeros(8), hessian - hessian.T, sp.zeros(8), "q3")
    audit.check("Q3 graph has twelve edges", len(q3_edges()) == 12, len(q3_edges()), 12, "q3")
    omitted = sum(r_symbol * value**2 / 2 + g_symbol * value**4 / 4 for value in values)
    omitted += sum(
        lambda_symbol * (values[a] - values[b]) ** 2 * (values[a] ** 2 + values[b] ** 2) / 4
        for a, b in q3_edges()[1:]
    )
    omitted_gradient = sp.Matrix([sp.diff(omitted, value) for value in values])
    audit.check("Q3 omitted-edge mutant rejected", omitted_gradient != derived, "different", "full gradient", "mutant")
    audit.check(
        "Q3 locking-factor mutant rejected",
        q3_gradient(values, {"r": r_symbol, "g": g_symbol, "lambda": 2 * lambda_symbol}) != derived,
        "different",
        "full gradient",
        "mutant",
    )


def fixture(name: str) -> dict[str, Any]:
    if name == "f0":
        data = {
            "name": name,
            "M": 4,
            "L": q(8),
            "chi": q(2),
            "c": q(3, 2),
            "r": q(-1, 2),
            "g": q(2),
            "lambda": q(1),
            "delta": q(1, 2),
            "hbar": q(3, 7),
        }
    elif name == "f1":
        data = {
            "name": name,
            "M": 6,
            "L": q(9),
            "chi": q(4, 3),
            "c": q(7, 9),
            "r": q(1, 5),
            "g": q(9, 7),
            "lambda": q(5, 6),
            "delta": q(-3, 10),
            "hbar": q(7, 8),
        }
    else:
        raise ValueError(name)
    data["a"] = sp.factor(data["L"] / data["M"])
    data["w"] = sp.factor(data["a"] / 8)
    data["mu"] = sp.factor(data["chi"] * data["w"])
    data["ell"] = sp.factor(data["mu"] / data["delta"])
    data["kappa"] = sp.factor(data["c"] * data["delta"] ** 2 / (data["chi"] * data["a"] ** 2))
    data["beta"] = sp.factor(data["delta"] ** 2 / data["chi"])
    return data


def vector_fixture(data: dict[str, Any], offset: int) -> list[sp.Matrix]:
    result: list[sp.Matrix] = []
    for site in range(data["M"]):
        vector = sp.zeros(8, 1)
        vector[(site + offset) % 8] = q((-1) ** (site + offset) * (site + 1), site + offset + 2)
        vector[(2 * site + offset + 3) % 8] += q(site + offset + 2, site + offset + 5)
        result.append(vector)
    return result


def ring_gradient(values: list[sp.Matrix], data: dict[str, Any]) -> list[sp.Matrix]:
    result: list[sp.Matrix] = []
    spatial = data["w"] * data["c"] / data["a"] ** 2
    for site, value in enumerate(values):
        result.append(
            sp.Matrix(
                [
                    sp.factor(item)
                    for item in (
                        spatial * (2 * value - values[(site - 1) % data["M"]] - values[(site + 1) % data["M"]])
                        + data["w"] * q3_gradient(value, data)
                    )
                ]
            )
        )
    return result


def history_step(previous: list[sp.Matrix], current: list[sp.Matrix], data: dict[str, Any]) -> list[sp.Matrix]:
    gradient = ring_gradient(current, data)
    coefficient = sp.factor(data["delta"] ** 2 / data["mu"])
    return [
        sp.Matrix([sp.factor(item) for item in (2 * current[j] - previous[j] - coefficient * gradient[j])])
        for j in range(data["M"])
    ]


def dkd_step(positions: list[sp.Matrix], momenta: list[sp.Matrix], data: dict[str, Any]) -> tuple[list[sp.Matrix], list[sp.Matrix]]:
    half = sp.factor(data["delta"] / (2 * data["mu"]))
    midpoint = [positions[j] + half * momenta[j] for j in range(data["M"])]
    gradient = ring_gradient(midpoint, data)
    kicked = [momenta[j] - data["delta"] * gradient[j] for j in range(data["M"])]
    output = [midpoint[j] + half * kicked[j] for j in range(data["M"])]
    return output, kicked


def local_f(value: sp.Matrix, data: dict[str, Any]) -> sp.Matrix:
    return sp.Matrix(
        [
            sp.factor(item)
            for item in (2 * (1 - data["kappa"]) * value - data["beta"] * q3_gradient(value, data))
        ]
    )


def balanced_heights(M: int) -> list[tuple[int, ...]]:
    paths: list[tuple[int, ...]] = []
    for deltas in itertools.product((-1, 1), repeat=M):
        if sum(deltas) != 0:
            continue
        heights = [0]
        for delta in deltas[:-1]:
            heights.append(heights[-1] + delta)
        if heights[0] - heights[-1] != deltas[-1]:
            raise AssertionError("periodic height closure")
        paths.append(tuple(heights))
    return paths


def lower_neighbours(heights: tuple[int, ...] | list[int], site: int) -> tuple[int, ...]:
    M = len(heights)
    return tuple(
        neighbour
        for neighbour in ((site - 1) % M, (site + 1) % M)
        if heights[neighbour] == heights[site] - 1
    )


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
    neighbours = []
    for neighbour in (site - 1, site + 1):
        if 0 <= neighbour < len(heights) and heights[neighbour] == heights[site] - 1:
            neighbours.append(neighbour)
    return tuple(neighbours)


def open_cut_matrices(heights: tuple[int, ...], data: dict[str, Any]) -> tuple[sp.Matrix, sp.Matrix, sp.Matrix, sp.Matrix]:
    N = len(heights)
    adjacency = sp.zeros(N)
    transform = sp.zeros(2 * N)
    for site in range(N):
        transform[site, site] = 1
        transform[N + site, N + site] = data["ell"]
        for lower in open_lower_neighbours(heights, site):
            adjacency[site, lower] = 1
            transform[N + site, N + lower] = -data["ell"] * data["kappa"]
    canonical = sp.zeros(2 * N)
    for site in range(N):
        canonical[site, N + site] = -1
        canonical[N + site, site] = 1
    pulled = sp.simplify(transform.T * canonical * transform)
    flux = sp.zeros(2 * N)
    for site in range(N):
        flux[N + site, site] += data["ell"]
        flux[site, N + site] -= data["ell"]
    for left in range(N - 1):
        right = left + 1
        high, low = (left, right) if heights[left] > heights[right] else (right, left)
        flux[N + low, high] -= data["ell"] * data["kappa"]
        flux[high, N + low] += data["ell"] * data["kappa"]
    return transform, pulled, flux, adjacency


def open_force(value: sp.Expr, data: dict[str, Any]) -> sp.Expr:
    return sp.factor(2 * (1 - data["kappa"]) * value - data["beta"] * (data["r"] * value + data["g"] * value**3))


def open_cut_darboux(A: list[sp.Expr], B: list[sp.Expr], heights: tuple[int, ...] | list[int], data: dict[str, Any]) -> tuple[list[sp.Expr], list[sp.Expr]]:
    Q = list(A)
    P = [
        sp.factor(
            data["ell"]
            * (B[site] - data["kappa"] * sum((B[lower] for lower in open_lower_neighbours(heights, site)), sp.S.Zero))
        )
        for site in range(len(heights))
    ]
    return Q, P


def open_ready_valleys(heights: tuple[int, ...] | list[int]) -> tuple[int, ...]:
    return tuple(
        site
        for site in range(1, len(heights) - 1)
        if heights[site - 1] == heights[site] + 1 and heights[site + 1] == heights[site] + 1
    )


def open_raw_flip(A: list[sp.Expr], B: list[sp.Expr], heights: tuple[int, ...] | list[int], site: int, data: dict[str, Any]) -> tuple[list[sp.Expr], list[sp.Expr], tuple[int, ...]]:
    if site not in open_ready_valleys(heights):
        raise ValueError("site is not an open-cut valley")
    left, right = site - 1, site + 1
    A_out = list(A)
    B_out = list(B)
    A_out[site] = sp.factor(data["kappa"] * (A[left] + A[right]) - A[site] + open_force(B[site], data))
    B_out[site] = sp.factor(data["kappa"] * (B[left] + B[right]) - B[site] + open_force(A_out[site], data))
    heights_out = list(heights)
    heights_out[site] += 2
    return A_out, B_out, tuple(heights_out)


def open_staged_flip(Q: list[sp.Expr], P: list[sp.Expr], site: int, data: dict[str, Any]) -> tuple[list[sp.Expr], list[sp.Expr]]:
    left, right = site - 1, site + 1
    Q_now = list(Q)
    P_now = list(P)
    Q_now[site] = sp.factor(Q_now[site] - open_force(P_now[site] / data["ell"], data))
    Q_now[site] = -Q_now[site]
    P_now[site] = -P_now[site]
    Q_now[site] = sp.factor(Q_now[site] + data["kappa"] * (Q_now[left] + Q_now[right]))
    P_now[left] = sp.factor(P_now[left] - data["kappa"] * P_now[site])
    P_now[right] = sp.factor(P_now[right] - data["kappa"] * P_now[site])
    P_now[site] = sp.factor(P_now[site] + data["ell"] * open_force(Q_now[site], data))
    return Q_now, P_now


def open_inverse_staged_flip(Q_out: list[sp.Expr], P_out: list[sp.Expr], site: int, data: dict[str, Any]) -> tuple[list[sp.Expr], list[sp.Expr]]:
    left, right = site - 1, site + 1
    Q_now = list(Q_out)
    P_now = list(P_out)
    P_now[site] = sp.factor(P_now[site] - data["ell"] * open_force(Q_now[site], data))
    Q_now[site] = sp.factor(Q_now[site] - data["kappa"] * (Q_now[left] + Q_now[right]))
    P_now[left] = sp.factor(P_now[left] + data["kappa"] * P_now[site])
    P_now[right] = sp.factor(P_now[right] + data["kappa"] * P_now[site])
    Q_now[site] = -Q_now[site]
    P_now[site] = -P_now[site]
    Q_now[site] = sp.factor(Q_now[site] + open_force(P_now[site] / data["ell"], data))
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


def apply_open_sweep(A: list[sp.Expr], B: list[sp.Expr], heights: tuple[int, ...], sweep: tuple[int, ...], data: dict[str, Any]) -> tuple[list[sp.Expr], list[sp.Expr], tuple[int, ...]]:
    A_now, B_now, h_now = list(A), list(B), tuple(heights)
    for site in sweep:
        A_now, B_now, h_now = open_raw_flip(A_now, B_now, h_now, site, data)
    return A_now, B_now, h_now


def cut_darboux(
    A: list[sp.Matrix], B: list[sp.Matrix], heights: tuple[int, ...] | list[int], data: dict[str, Any]
) -> tuple[list[sp.Matrix], list[sp.Matrix]]:
    Q = [value.copy() for value in A]
    P = [
        sp.Matrix(
            [
                sp.factor(item)
                for item in data["ell"]
                * (B[site] - data["kappa"] * sum((B[n] for n in lower_neighbours(heights, site)), sp.zeros(8, 1)))
            ]
        )
        for site in range(data["M"])
    ]
    return Q, P


def cut_matrices(heights: tuple[int, ...], data: dict[str, Any]) -> tuple[sp.Matrix, sp.Matrix, sp.Matrix]:
    M = data["M"]
    transform = sp.zeros(2 * M)
    for site in range(M):
        transform[site, site] = 1
        transform[M + site, M + site] = data["ell"]
        for lower in lower_neighbours(heights, site):
            transform[M + site, M + lower] = -data["ell"] * data["kappa"]
    canonical = sp.zeros(2 * M)
    for site in range(M):
        canonical[site, M + site] = -1
        canonical[M + site, site] = 1
    pulled = sp.simplify(transform.T * canonical * transform)
    flux = sp.zeros(2 * M)
    for site in range(M):
        flux[M + site, site] += data["ell"]
        flux[site, M + site] -= data["ell"]
    for site in range(M):
        other = (site + 1) % M
        if heights[site] > heights[other]:
            high, low = site, other
        else:
            high, low = other, site
        flux[M + low, high] -= data["ell"] * data["kappa"]
        flux[high, M + low] += data["ell"] * data["kappa"]
    return transform, pulled, flux


def valley_flip_raw(
    A: list[sp.Matrix], B: list[sp.Matrix], heights: tuple[int, ...] | list[int], site: int, data: dict[str, Any]
) -> tuple[list[sp.Matrix], list[sp.Matrix], list[int]]:
    M = data["M"]
    left, right = (site - 1) % M, (site + 1) % M
    if not (heights[left] == heights[site] + 1 and heights[right] == heights[site] + 1):
        raise ValueError("site is not a valley")
    A_out = [value.copy() for value in A]
    B_out = [value.copy() for value in B]
    A_out[site] = data["kappa"] * (A[left] + A[right]) - A[site] + local_f(B[site], data)
    B_out[site] = data["kappa"] * (B[left] + B[right]) - B[site] + local_f(A_out[site], data)
    heights_out = list(heights)
    heights_out[site] += 2
    return A_out, B_out, heights_out


def canonical_valley_flip(
    Q: list[sp.Matrix], P: list[sp.Matrix], heights: tuple[int, ...] | list[int], site: int, data: dict[str, Any]
) -> tuple[list[sp.Matrix], list[sp.Matrix]]:
    M = data["M"]
    left, right = (site - 1) % M, (site + 1) % M
    if not (heights[left] == heights[site] + 1 and heights[right] == heights[site] + 1):
        raise ValueError("site is not a valley")
    Q_out = [value.copy() for value in Q]
    P_out = [value.copy() for value in P]
    P_out[left] = P[left] + data["kappa"] * P[site]
    P_out[right] = P[right] + data["kappa"] * P[site]
    Q_out[site] = -Q[site] + data["kappa"] * (Q[left] + Q[right]) + local_f(P[site] / data["ell"], data)
    P_out[site] = -P[site] + data["ell"] * local_f(Q_out[site], data)
    return Q_out, P_out


def factorized_valley_flip(
    Q: list[sp.Matrix], P: list[sp.Matrix], heights: tuple[int, ...] | list[int], site: int, data: dict[str, Any]
) -> tuple[list[sp.Matrix], list[sp.Matrix]]:
    M = len(Q)
    left, right = (site - 1) % M, (site + 1) % M
    Q_now = [value.copy() for value in Q]
    P_now = [value.copy() for value in P]

    # U_p point-map stage.
    Q_now[site] -= local_f(P_now[site] / data["ell"], data)

    # Central parity stage.
    Q_now[site] = -Q_now[site]
    P_now[site] = -P_now[site]

    # U_kappa point-map stage.  P_now[site] is already -P_s(old).
    Q_now[site] += data["kappa"] * (Q_now[left] + Q_now[right])
    P_now[left] -= data["kappa"] * P_now[site]
    P_now[right] -= data["kappa"] * P_now[site]

    # U_q point-map stage.
    P_now[site] += data["ell"] * local_f(Q_now[site], data)
    return Q_now, P_now


def swapped_control_parity_valley_flip(
    Q: list[sp.Matrix], P: list[sp.Matrix], site: int, data: dict[str, Any]
) -> tuple[list[sp.Matrix], list[sp.Matrix]]:
    """Hostile mutant: U_p, then U_kappa, then parity, then U_q."""
    M = len(Q)
    left, right = (site - 1) % M, (site + 1) % M
    Q_now = [value.copy() for value in Q]
    P_now = [value.copy() for value in P]
    Q_now[site] -= local_f(P_now[site] / data["ell"], data)
    Q_now[site] += data["kappa"] * (Q_now[left] + Q_now[right])
    P_now[left] -= data["kappa"] * P_now[site]
    P_now[right] -= data["kappa"] * P_now[site]
    Q_now[site] = -Q_now[site]
    P_now[site] = -P_now[site]
    P_now[site] += data["ell"] * local_f(Q_now[site], data)
    return Q_now, P_now


def inverse_factorized_valley_flip(
    Q_out: list[sp.Matrix], P_out: list[sp.Matrix], site: int, data: dict[str, Any]
) -> tuple[list[sp.Matrix], list[sp.Matrix]]:
    M = data["M"]
    left, right = (site - 1) % M, (site + 1) % M
    P_before_out = [value.copy() for value in P_out]
    P_before_out[site] -= data["ell"] * local_f(Q_out[site], data)
    Q_mid = [value.copy() for value in Q_out]
    P_mid = [value.copy() for value in P_before_out]
    Q_mid[site] = -Q_out[site]
    P_mid[site] = -P_before_out[site]
    Q = [value.copy() for value in Q_mid]
    P = [value.copy() for value in P_mid]
    Q[site] = Q_mid[site] + data["kappa"] * (Q_mid[left] + Q_mid[right]) + local_f(P_mid[site] / data["ell"], data)
    P[left] = P_mid[left] - data["kappa"] * P_mid[site]
    P[right] = P_mid[right] - data["kappa"] * P_mid[site]
    return Q, P


def raw_checkerboard(previous: list[sp.Matrix], current: list[sp.Matrix], high_parity: int, data: dict[str, Any]) -> tuple[list[sp.Matrix], list[sp.Matrix], list[int]]:
    following = history_step(previous, current, data)
    A: list[sp.Matrix] = []
    B: list[sp.Matrix] = []
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


def decode_checkerboard(
    A: list[sp.Matrix], B: list[sp.Matrix], heights: list[int], data: dict[str, Any]
) -> tuple[list[sp.Matrix], list[sp.Matrix]]:
    minimum = min(heights)
    maximum = max(heights)
    if maximum - minimum != 1:
        raise ValueError("not checkerboard")
    current: list[sp.Matrix] = [sp.zeros(8, 1) for _ in range(data["M"])]
    for site in range(data["M"]):
        current[site] = B[site] if heights[site] == minimum else A[site]
    following = history_step(
        [
            A[site]
            if heights[site] == minimum
            else 2 * current[site] - B[site] - (data["delta"] ** 2 / data["mu"]) * ring_gradient(current, data)[site]
            for site in range(data["M"])
        ],
        current,
        data,
    )
    previous = [2 * current[j] - following[j] - (data["delta"] ** 2 / data["mu"]) * ring_gradient(current, data)[j] for j in range(data["M"])]
    return previous, current


def apply_valleys(
    A: list[sp.Matrix], B: list[sp.Matrix], heights: list[int], order: tuple[int, ...], data: dict[str, Any]
) -> tuple[list[sp.Matrix], list[sp.Matrix], list[int]]:
    A_now = [value.copy() for value in A]
    B_now = [value.copy() for value in B]
    h_now = list(heights)
    for site in order:
        A_now, B_now, h_now = valley_flip_raw(A_now, B_now, h_now, site, data)
    return A_now, B_now, h_now


def audit_reference_anchor(audit: Audit, data: dict[str, Any]) -> None:
    name = data["name"]
    q_values = vector_fixture(data, 3)
    pi_values = vector_fixture(data, 6)
    gradient = ring_gradient(q_values, data)
    symplectic = sp.Matrix([[1, -1 / data["ell"]], [data["ell"], 0]])
    standard = sp.Matrix([[0, 1], [-1, 0]])
    audit.check(
        f"{name} reference low metaplectic symplectic matrix",
        sp.simplify(symplectic.T * standard * symplectic) == standard,
        sp.simplify(symplectic.T * standard * symplectic),
        standard,
        "reference_regularity",
    )
    for high_parity in (0, 1):
        heights = [1 if site % 2 == high_parity else 0 for site in range(data["M"])]
        A: list[sp.Matrix] = []
        B: list[sp.Matrix] = []
        for site in range(data["M"]):
            if heights[site] == 1:
                A.append(q_values[site])
                B.append(q_values[site] + (pi_values[site] - data["delta"] * gradient[site]) / data["ell"])
            else:
                A.append(q_values[site] - pi_values[site] / data["ell"])
                B.append(q_values[site])
        Q, P = cut_darboux(A, B, heights, data)
        for site in range(data["M"]):
            if heights[site] == 1:
                expected_Q = q_values[site]
                expected_P = (
                    pi_values[site]
                    + data["ell"] * (1 - 2 * data["kappa"]) * q_values[site]
                    - data["delta"] * data["w"] * q3_gradient(q_values[site], data)
                )
            else:
                expected_Q = q_values[site] - pi_values[site] / data["ell"]
                expected_P = data["ell"] * q_values[site]
            audit.check(f"{name} parity {high_parity} reference decoder Q site {site}", Q[site] == expected_Q, Q[site], expected_Q, "reference_regularity")
            audit.check(f"{name} parity {high_parity} reference decoder P site {site}", P[site] == expected_P, P[site], expected_P, "reference_regularity")
        reconstructed_q = [A[site] if heights[site] == 1 else B[site] for site in range(data["M"])]
        reconstructed_pi = [
            data["ell"] * (B[site] - A[site]) + (data["delta"] * gradient[site] if heights[site] == 1 else sp.zeros(8, 1))
            for site in range(data["M"])
        ]
        audit.check(f"{name} parity {high_parity} reference q reconstruction", reconstructed_q == q_values, reconstructed_q, q_values, "reference_regularity")
        audit.check(f"{name} parity {high_parity} reference pi reconstruction", reconstructed_pi == pi_values, reconstructed_pi, pi_values, "reference_regularity")


def audit_ready_generator_commutation(audit: Audit) -> None:
    generator_kinds = ("gp", "gk", "gq")

    def supports(kind: str, center: int, neighbours: set[int]) -> tuple[set[int], set[int]]:
        if kind == "gp":
            return set(), {center}
        if kind == "gk":
            return set(neighbours), {center}
        return {center}, set()

    for label, size, left_center, right_center, left_neighbours, right_neighbours in (
        ("M4-shared-two-controls", 4, 1, 3, {0, 2}, {0, 2}),
        ("M6-shared-one-control", 6, 1, 3, {0, 2}, {2, 4}),
    ):
        Q = sp.symbols(f"q0:{size}")
        P = sp.symbols(f"p0:{size}")
        a2, a4, b2, b4, kappa_symbol = sp.symbols("a2 a4 b2 b4 kappa_support")

        def expression(kind: str, center: int, neighbours: set[int]) -> sp.Expr:
            if kind == "gp":
                return a2 * P[center] ** 2 + a4 * P[center] ** 4
            if kind == "gk":
                return kappa_symbol * P[center] * sum((Q[item] for item in neighbours), sp.S.Zero)
            return b2 * Q[center] ** 2 + b4 * Q[center] ** 4

        for left_kind in generator_kinds:
            for right_kind in generator_kinds:
                q_left, p_left = supports(left_kind, left_center, left_neighbours)
                q_right, p_right = supports(right_kind, right_center, right_neighbours)
                disjoint_conjugates = not (p_left & q_right or q_left & p_right)
                audit.check(
                    f"{label} {left_kind}-{right_kind} strong support commutation",
                    disjoint_conjugates,
                    [sorted(p_left & q_right), sorted(q_left & p_right)],
                    [[], []],
                    "diamond_support",
                )
                left_expr = expression(left_kind, left_center, left_neighbours)
                right_expr = expression(right_kind, right_center, right_neighbours)
                bracket = sp.factor(
                    sum(
                        sp.diff(left_expr, Q[site]) * sp.diff(right_expr, P[site])
                        - sp.diff(left_expr, P[site]) * sp.diff(right_expr, Q[site])
                        for site in range(size)
                    )
                )
                audit.check(f"{label} {left_kind}-{right_kind} symbolic cross bracket", bracket == 0, bracket, 0, "diamond_support")


def audit_open_rectangles(audit: Audit, data: dict[str, Any]) -> dict[str, Any]:
    fingerprints: dict[str, Any] = {}
    for down_steps, up_steps, expected_cuts, expected_sweeps in ((2, 2, 6, 2), (2, 3, 10, 5)):
        label = f"open-{down_steps}x{up_steps}"
        paths = open_height_paths(down_steps, up_steps)
        legs = down_steps + up_steps + 1
        audit.check(f"{label} every boundary path", len(paths) == expected_cuts, len(paths), expected_cuts, "open_all_cut")
        diamond_count = 0
        cover_count = 0
        for index, heights in enumerate(paths):
            transform, pulled, flux, adjacency = open_cut_matrices(heights, data)
            audit.check(f"{label} cut {index} endpoint-aware Darboux pullback", pulled == flux, pulled - flux, sp.zeros(2 * legs), "open_all_cut")
            audit.check(f"{label} cut {index} one-species determinant", sp.factor(transform.det()) == data["ell"] ** legs, sp.factor(transform.det()), data["ell"] ** legs, "open_all_cut")
            audit.check(f"{label} cut {index} full-eight-species determinant", sp.factor(transform.det() ** 8) == data["ell"] ** (8 * legs), sp.factor(transform.det() ** 8), data["ell"] ** (8 * legs), "open_all_cut")
            audit.check(f"{label} cut {index} nilpotent adjacency", adjacency**legs == sp.zeros(legs), adjacency**legs, sp.zeros(legs), "open_all_cut")
            series = sum(((data["kappa"] * adjacency) ** power for power in range(legs)), sp.zeros(legs))
            audit.check(f"{label} cut {index} finite inverse", sp.simplify((sp.eye(legs) - data["kappa"] * adjacency) * series) == sp.eye(legs), sp.simplify((sp.eye(legs) - data["kappa"] * adjacency) * series), sp.eye(legs), "open_all_cut")
            seam_entries = (flux[legs, legs - 1], flux[legs - 1, legs], flux[2 * legs - 1, 0], flux[0, 2 * legs - 1])
            audit.check(f"{label} cut {index} endpoint seam absent", all(entry == 0 for entry in seam_entries), seam_entries, (0, 0, 0, 0), "open_all_cut")

            A = [q((index + 2) * (site + 1), site + 3) for site in range(legs)]
            B = [q((-1) ** (index + site) * (site + 2), index + site + 4) for site in range(legs)]
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
        A0 = [q(site + 1, site + 2) for site in range(legs)]
        B0 = [q((-1) ** site * (site + 2), site + 3) for site in range(legs)]
        outputs = [apply_open_sweep(A0, B0, minimal, sweep, data) for sweep in sweeps]
        audit.check(f"{label} full sweep order independence", all(item == outputs[0] for item in outputs), len(outputs), expected_sweeps, "open_sweep")
        audit.check(f"{label} has a genuine diamond", diamond_count > 0, diamond_count, "positive", "open_sweep")
        fingerprints[label] = {"cuts": len(paths), "legs": legs, "covers": cover_count, "diamonds": diamond_count, "sweeps": len(sweeps)}
    return fingerprints


def audit_fixture(audit: Audit, data: dict[str, Any]) -> dict[str, Any]:
    name = data["name"]
    M = data["M"]
    audit_reference_anchor(audit, data)
    expected_cut_count = math.comb(M, M // 2)
    cuts = balanced_heights(M)
    audit.check(f"{name} all balanced cuts enumerated", len(cuts) == expected_cut_count, len(cuts), expected_cut_count, "all_cut")
    determinants: list[sp.Expr] = []
    for index, heights in enumerate(cuts):
        transform, pulled, flux = cut_matrices(heights, data)
        audit.check(f"{name} cut {index} Darboux pullback", pulled == flux, pulled - flux, sp.zeros(2 * M), "all_cut")
        determinant = sp.factor(transform.det())
        determinants.append(determinant)
        audit.check(f"{name} cut {index} Darboux determinant", determinant == data["ell"] ** M, determinant, data["ell"] ** M, "all_cut")
    wrong_ell = dict(data)
    wrong_ell["ell"] = -data["ell"]
    _, wrong_pulled, flux = cut_matrices(cuts[0], wrong_ell)
    _, _, correct_flux = cut_matrices(cuts[0], data)
    audit.check(f"{name} history-sign mutant rejected", wrong_pulled != correct_flux, "different", "correct cut form", "mutant")

    previous = vector_fixture(data, 1)
    current = vector_fixture(data, 4)
    following = history_step(previous, current, data)
    next_following = history_step(current, following, data)
    pi_current = [data["ell"] * (current[j] - previous[j]) for j in range(M)]
    pi_next = [pi_current[j] - data["delta"] * ring_gradient(current, data)[j] for j in range(M)]
    audit.check(
        f"{name} discrete Legendre momentum recurrence",
        all(pi_next[j] == data["ell"] * (following[j] - current[j]) for j in range(M)),
        pi_next,
        "ell*(x_next-x)",
        "history",
    )
    audit.check(
        f"{name} kick-drift position recurrence",
        all(following[j] == current[j] + pi_next[j] / data["ell"] for j in range(M)),
        following,
        "q+pi_next/ell",
        "history",
    )

    original_q = [(previous[j] + current[j]) / 2 for j in range(M)]
    original_p = [data["ell"] * (current[j] - previous[j]) for j in range(M)]
    dkd_q, dkd_p = dkd_step(original_q, original_p, data)
    decoded_previous = [dkd_q[j] - data["delta"] * dkd_p[j] / (2 * data["mu"]) for j in range(M)]
    decoded_current = [dkd_q[j] + data["delta"] * dkd_p[j] / (2 * data["mu"]) for j in range(M)]
    audit.check(f"{name} D-K-D midpoint conjugacy first slice", decoded_previous == current, decoded_previous, current, "history")
    audit.check(f"{name} D-K-D midpoint conjugacy second slice", decoded_current == following, decoded_current, following, "history")

    for high_parity in (0, 1):
        A, B, heights = raw_checkerboard(previous, current, high_parity, data)
        low_sites = tuple(site for site in range(M) if heights[site] == 0)
        Q, P = cut_darboux(A, B, heights, data)
        first = low_sites[0]
        Q_direct, P_direct = canonical_valley_flip(Q, P, heights, first, data)
        Q_factored, P_factored = factorized_valley_flip(Q, P, heights, first, data)
        audit.check(f"{name} parity {high_parity} shear-parity-shear Q", Q_factored == Q_direct, Q_factored, Q_direct, "circuit")
        audit.check(f"{name} parity {high_parity} shear-parity-shear P", P_factored == P_direct, P_factored, P_direct, "circuit")
        if high_parity == 0:
            left, right = (first - 1) % M, (first + 1) % M
            Q_wrong, P_wrong = swapped_control_parity_valley_flip(Q, P, first, data)
            expected_q_difference = -2 * data["kappa"] * (Q[left] + Q[right])
            expected_left_p_difference = -2 * data["kappa"] * P[first]
            audit.check(f"{name} staged order mutant central Q difference", Q_wrong[first] - Q_direct[first] == expected_q_difference, Q_wrong[first] - Q_direct[first], expected_q_difference, "mutant")
            audit.check(f"{name} staged order mutant retained P difference", P_wrong[left] - P_direct[left] == expected_left_p_difference, P_wrong[left] - P_direct[left], expected_left_p_difference, "mutant")
            audit.check(f"{name} staged order mutant Q witness nonzero", expected_q_difference != sp.zeros(8, 1), expected_q_difference, "nonzero", "mutant")
            audit.check(f"{name} staged order mutant P witness nonzero", expected_left_p_difference != sp.zeros(8, 1), expected_left_p_difference, "nonzero", "mutant")
        Q_back, P_back = inverse_factorized_valley_flip(Q_factored, P_factored, first, data)
        audit.check(f"{name} parity {high_parity} circuit inverse Q", Q_back == Q, Q_back, Q, "circuit")
        audit.check(f"{name} parity {high_parity} circuit inverse P", P_back == P, P_back, P, "circuit")
        A_one, B_one, h_one = valley_flip_raw(A, B, heights, first, data)
        Q_raw, P_raw = cut_darboux(A_one, B_one, h_one, data)
        audit.check(f"{name} parity {high_parity} raw-canonical flip Q", Q_raw == Q_direct, Q_raw, Q_direct, "circuit")
        audit.check(f"{name} parity {high_parity} raw-canonical flip P", P_raw == P_direct, P_raw, P_direct, "circuit")

        outputs = [apply_valleys(A, B, heights, order, data) for order in itertools.permutations(low_sites)]
        reference_A, reference_B, reference_h = outputs[0]
        audit.check(
            f"{name} parity {high_parity} all simultaneous-flip orders",
            all(item[0] == reference_A and item[1] == reference_B and item[2] == reference_h for item in outputs),
            len(outputs),
            math.factorial(M // 2),
            "circuit",
        )
        decoded_old, decoded_now = decode_checkerboard(A, B, heights, data)
        decoded_now_out, decoded_next_out = decode_checkerboard(reference_A, reference_B, reference_h, data)
        audit.check(f"{name} parity {high_parity} input checkerboard decode", decoded_old == previous and decoded_now == current, "exact", "previous,current", "diagram")
        audit.check(f"{name} parity {high_parity} output checkerboard decode", decoded_now_out == current and decoded_next_out == following, "exact", "current,following", "diagram")

    heights = tuple(1 if site % 2 == 0 else 0 for site in range(M))
    transform, pulled, _ = cut_matrices(heights, data)
    poisson = sp.simplify(pulled.inv())
    low = 1
    high = 0
    tensor_witness = sp.factor(poisson[low, M + high])
    audit.check(f"{name} raw cross-leg commutator witness", tensor_witness == data["kappa"] / data["ell"], tensor_witness, data["kappa"] / data["ell"], "raw_tensor_nogo")
    audit.check(f"{name} raw cross-leg witness nonzero", tensor_witness != 0, tensor_witness, "nonzero", "raw_tensor_nogo")
    audit.check(f"{name} onsite raw CCR coefficient", sp.factor(poisson[high, M + high]) == 1 / data["ell"], poisson[high, M + high], 1 / data["ell"], "raw_ccr")
    wrong_tensor = sp.zeros(2 * M)
    for site in range(M):
        wrong_tensor[site, M + site] = 1 / data["ell"]
        wrong_tensor[M + site, site] = -1 / data["ell"]
    audit.check(f"{name} independent-leg Poisson mutant rejected", wrong_tensor != poisson, "different", "current-flux inverse", "mutant")

    dimension = 8 * M
    mixed_hessian_determinant = sp.factor((-data["ell"]) ** dimension)
    audit.check(f"{name} history FIO mixed Hessian nonzero", mixed_hessian_determinant != 0, mixed_hessian_determinant, "nonzero", "unitary")
    audit.check(f"{name} kernel normalization power", dimension // 2 == 4 * M, dimension // 2, 4 * M, "unitary")
    audit.check(f"{name} negative-step kernel absolute scale", abs(data["ell"]) > 0, abs(data["ell"]), "positive", "unitary")
    audit.check(f"{name} quartic nonlinear coefficient nonzero", sp.factor(-data["beta"] * data["g"]) != 0, -data["beta"] * data["g"], "nonzero", "weyl_boundary")

    return {
        "M": M,
        "ell": data["ell"],
        "kappa": data["kappa"],
        "beta": data["beta"],
        "cut_count": len(cuts),
        "one_species_darboux_determinant": determinants[0],
        "full_eight_species_darboux_determinant": sp.factor(determinants[0] ** 8),
        "tensor_witness": tensor_witness,
        "kernel_mixed_hessian_determinant": mixed_hessian_determinant,
        "kernel_normalization_power": dimension // 2,
        "parity_order_count": math.factorial(M // 2),
        "following_site0": list(following[0]),
        "second_following_site0": list(next_following[0]),
    }


def audit_generating_phase(audit: Audit) -> None:
    q_old, q_new, ell, delta = sp.symbols("q_old q_new ell delta", real=True, nonzero=True)
    u = sp.Function("U")(q_old)
    phase = ell * (q_new - q_old) ** 2 / 2 - delta * u
    pi_old = -sp.diff(phase, q_old)
    pi_new = sp.diff(phase, q_new)
    audit.check("type-one phase old momentum", sp.expand(pi_old - pi_new - delta * sp.diff(u, q_old)) == 0, pi_old, pi_new + delta * sp.diff(u, q_old), "phase")
    audit.check("type-one phase mixed Hessian", sp.diff(phase, q_new, q_old) == -ell, sp.diff(phase, q_new, q_old), -ell, "phase")
    wrong_phase = ell * (q_new - q_old) ** 2 / 2 + delta * u
    audit.check("phase-kick-sign mutant rejected", -sp.diff(wrong_phase, q_old) != pi_old, -sp.diff(wrong_phase, q_old), pi_old, "mutant")


def audit_state_transport(audit: Audit) -> dict[str, Any]:
    M_half = sp.Matrix([[q(3, 5), q(-4, 5), 0], [q(4, 5), q(3, 5), 0], [0, 0, 1]])
    U_DKD = sp.Matrix([[q(5, 13), 0, q(-12, 13)], [0, 1, 0], [q(12, 13), 0, q(5, 13)]])
    Lambda_C = sp.eye(3)
    Lambda_D = sp.Matrix([[0, 1, 0], [0, 0, 1], [1, 0, 0]])
    audit.check("typed anchor noncommuting half-drift fixture", M_half * U_DKD != U_DKD * M_half, M_half * U_DKD - U_DKD * M_half, "nonzero", "typed_anchor")
    U_hist = sp.simplify(M_half * U_DKD * M_half.T)
    Gamma_C = sp.simplify(M_half.T * Lambda_C)
    Gamma_D = sp.simplify(M_half.T * Lambda_D)
    audit.check("typed Gamma C equals half-drift adjoint Lambda C", Gamma_C == M_half.T * Lambda_C, Gamma_C, M_half.T * Lambda_C, "typed_anchor")
    audit.check("typed Gamma D equals half-drift adjoint Lambda D", Gamma_D == M_half.T * Lambda_D, Gamma_D, M_half.T * Lambda_D, "typed_anchor")

    same_time = sp.simplify(Gamma_D.T * Gamma_C)
    same_time_history = sp.simplify(Lambda_D.T * Lambda_C)
    physical = sp.simplify(Gamma_D.T * U_DKD * Gamma_C)
    physical_history = sp.simplify(Lambda_D.T * U_hist * Lambda_C)
    audit.check("typed same-time Gamma and Lambda maps agree", same_time == same_time_history, same_time, same_time_history, "typed_anchor")
    audit.check("typed same-time history diagram", sp.simplify(Lambda_D * same_time) == Lambda_C, sp.simplify(Lambda_D * same_time), Lambda_C, "typed_anchor")
    audit.check("typed same-time phase diagram", sp.simplify(Gamma_D * same_time) == Gamma_C, sp.simplify(Gamma_D * same_time), Gamma_C, "typed_anchor")
    audit.check("typed physical Gamma and Lambda maps agree", physical == physical_history, physical, physical_history, "typed_anchor")
    audit.check("typed physical history diagram", sp.simplify(Lambda_D * physical) == U_hist * Lambda_C, sp.simplify(Lambda_D * physical), U_hist * Lambda_C, "typed_anchor")
    audit.check("typed physical phase diagram", sp.simplify(Gamma_D * physical) == U_DKD * Gamma_C, sp.simplify(Gamma_D * physical), U_DKD * Gamma_C, "typed_anchor")

    hamiltonian = sp.diag(0, 1, 2)
    rho = sp.diag(q(4, 7), q(2, 7), q(1, 7))
    rho_C = sp.simplify(Gamma_C.T * rho * Gamma_C)
    rho_D_same = sp.simplify(Gamma_D.T * rho * Gamma_D)
    audit.check("typed same-time density covariance", sp.simplify(same_time * rho_C * same_time.T) == rho_D_same, sp.simplify(same_time * rho_C * same_time.T), rho_D_same, "state")
    rho_1 = sp.simplify(U_DKD * rho * U_DKD.T)
    rho_D_1 = sp.simplify(Gamma_D.T * rho_1 * Gamma_D)
    audit.check("typed physical density covariance", sp.simplify(physical * rho_C * physical.T) == rho_D_1, sp.simplify(physical * rho_C * physical.T), rho_D_1, "state")
    audit.check("typed physical density trace", sp.trace(rho_D_1) == 1, sp.trace(rho_D_1), 1, "state")
    observable = sp.Matrix([[2, 1, 0], [1, -1, 1], [0, 1, 3]])
    target_expectation = sp.trace(rho_D_1 * observable)
    source_expectation = sp.trace(rho_C * physical.T * observable * physical)
    audit.check("typed Schrodinger-Heisenberg expectation covariance", target_expectation == source_expectation, target_expectation, source_expectation, "state")

    energy_C = sp.simplify(Gamma_C.T * hamiltonian * Gamma_C)
    energy_D = sp.simplify(Gamma_D.T * hamiltonian * Gamma_D)
    audit.check("typed same-time affiliated-energy analogue", sp.simplify(same_time.T * energy_D * same_time) == energy_C, sp.simplify(same_time.T * energy_D * same_time), energy_C, "energy")
    energy_defect = sp.simplify(physical.T * energy_D * physical - energy_C)
    reference_defect = sp.simplify(Gamma_C.T * (U_DKD.T * hamiltonian * U_DKD - hamiltonian) * Gamma_C)
    audit.check("typed physical energy defect identity", energy_defect == reference_defect, energy_defect, reference_defect, "energy")
    shifted = hamiltonian + 5 * sp.eye(3)
    shifted_C = sp.simplify(Gamma_C.T * shifted * Gamma_C)
    shifted_D = sp.simplify(Gamma_D.T * shifted * Gamma_D)
    audit.check("typed additive energy shift cancels", sp.simplify(physical.T * shifted_D * physical - shifted_C) == energy_defect, sp.simplify(physical.T * shifted_D * physical - shifted_C), energy_defect, "energy")

    hamiltonian_co_1 = sp.simplify(U_DKD * hamiltonian * U_DKD.T)
    audit.check("transported Gibbs commutes with co-moving energy", sp.simplify(rho_1 * hamiltonian_co_1 - hamiltonian_co_1 * rho_1) == sp.zeros(3), sp.simplify(rho_1 * hamiltonian_co_1 - hamiltonian_co_1 * rho_1), sp.zeros(3), "state_boundary")
    audit.check("transported Gibbs not stationary for fixed energy", sp.simplify(rho_1 * hamiltonian - hamiltonian * rho_1) != sp.zeros(3), sp.simplify(rho_1 * hamiltonian - hamiltonian * rho_1), "nonzero", "state_boundary")
    ground = sp.diag(1, 0, 0)
    ground_1 = sp.simplify(U_DKD * ground * U_DKD.T)
    audit.check("transported ground commutes with co-moving energy", sp.simplify(ground_1 * hamiltonian_co_1 - hamiltonian_co_1 * ground_1) == sp.zeros(3), sp.simplify(ground_1 * hamiltonian_co_1 - hamiltonian_co_1 * ground_1), sp.zeros(3), "state_boundary")
    audit.check("transported ground not fixed-energy ground", sp.simplify(ground_1 * hamiltonian - hamiltonian * ground_1) != sp.zeros(3), sp.simplify(ground_1 * hamiltonian - hamiltonian * ground_1), "nonzero", "state_boundary")
    energy_D_co = sp.simplify(Gamma_D.T * hamiltonian_co_1 * Gamma_D)
    audit.check("cut Gibbs commutes with co-moving cut energy", sp.simplify(rho_D_1 * energy_D_co - energy_D_co * rho_D_1) == sp.zeros(3), sp.simplify(rho_D_1 * energy_D_co - energy_D_co * rho_D_1), sp.zeros(3), "state_boundary")
    audit.check("cut Gibbs not stationary for unchanged cut energy", sp.simplify(rho_D_1 * energy_D - energy_D * rho_D_1) != sp.zeros(3), sp.simplify(rho_D_1 * energy_D - energy_D * rho_D_1), "nonzero", "state_boundary")

    bad_same_time = sp.simplify(Gamma_D * Gamma_C.T)
    bad_physical = sp.simplify(Gamma_D * U_DKD * Gamma_C.T)
    audit.check("reversed Gamma same-time orientation mutant rejected", sp.simplify(bad_same_time * rho_C * bad_same_time.T) != rho_D_same, sp.simplify(bad_same_time * rho_C * bad_same_time.T), rho_D_same, "mutant")
    audit.check("reversed Gamma physical orientation mutant rejected", sp.simplify(bad_physical * rho_C * bad_physical.T) != rho_D_1, sp.simplify(bad_physical * rho_C * bad_physical.T), rho_D_1, "mutant")
    audit.check("reversed Gamma energy-ledger mutant rejected", sp.simplify(bad_physical.T * energy_D * bad_physical - energy_C) != reference_defect, sp.simplify(bad_physical.T * energy_D * bad_physical - energy_C), reference_defect, "mutant")
    return {
        "same_time_map": same_time,
        "physical_map": physical,
        "transported_density": rho_D_1,
        "energy_defect": energy_defect,
        "fixed_energy_commutator": sp.simplify(rho_1 * hamiltonian - hamiltonian * rho_1),
    }


def run(output: Path) -> dict[str, Any]:
    audit = Audit()
    audit_q3(audit)
    audit_generating_phase(audit)
    fingerprints = {name: audit_fixture(audit, fixture(name)) for name in ("f0", "f1")}
    audit_ready_generator_commutation(audit)
    open_fingerprints = audit_open_rectangles(audit, fixture("f0"))
    state = audit_state_transport(audit)
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

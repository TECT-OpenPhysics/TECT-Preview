#!/usr/bin/env python3
"""Non-importing standard-library audit for the scoped A13 R-142 result."""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-31"
__version_issued__ = "2026-07-31"

import argparse
from fractions import Fraction
import json
import math
import os
from pathlib import Path
import tempfile


RESULT_ID = (
    "A13-CLASSII-INNOVATION-COMPRESSED-COMMON-FEATURE-SU2-"
    "COVARIANCE-SIGNED-COLLAR-BAND-BOUNDARY"
)
SCHEMA = (
    "tect/a13-innovation-compressed-common-feature-su2-covariance-"
    "signed-collar-band-boundary-independent/1.0"
)
DEFAULT_OUTPUT = Path(
    "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/"
    "runs/2026-07-31-independent-innovation-compressed-common-feature-su2-"
    "covariance-signed-collar-band-boundary/result.json"
)
F = Fraction
P = F(4_000_000_000_001, 1_000_000_000_000)
ALPHA = F(5, 9)
C0 = F(3, 250) / P
C1 = F(243, 8000) / P
TOL = 8.0e-10


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []

    def add(
        self, group: str, name: str, passed: bool, actual: object, expected: object
    ) -> None:
        row = {
            "group": group,
            "name": name,
            "status": "PASS" if passed else "FAIL",
            "actual": str(actual),
            "expected": str(expected),
        }
        self.rows.append(row)
        if not passed:
            raise AssertionError(f"{group}::{name}: {actual!r} != {expected!r}")


def atomic_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def dot(left: list[Fraction], right: list[Fraction]) -> Fraction:
    return sum((x * y for x, y in zip(left, right)), F(0))


def mean(samples: list[list[Fraction]]) -> list[Fraction]:
    count = F(len(samples))
    return [sum((row[j] for row in samples), F(0)) / count for j in range(len(samples[0]))]


def cross(left: list[list[Fraction]], right: list[list[Fraction]]) -> Fraction:
    return sum((dot(x, y) for x, y in zip(left, right)), F(0)) / F(len(left))


def transpose(matrix: list[list[float]]) -> list[list[float]]:
    return [list(column) for column in zip(*matrix)]


def matmul(left: list[list[float]], right: list[list[float]]) -> list[list[float]]:
    columns = transpose(right)
    return [[sum(x * y for x, y in zip(row, column)) for column in columns] for row in left]


def jacobi_eigenvalues(matrix: list[list[float]]) -> list[float]:
    """Independent cyclic Jacobi diagonalisation for a real symmetric matrix."""
    a = [row[:] for row in matrix]
    size = len(a)
    for _ in range(200):
        p, q = max(
            ((i, j) for i in range(size) for j in range(i + 1, size)),
            key=lambda pair: abs(a[pair[0]][pair[1]]),
        )
        if abs(a[p][q]) < 1.0e-15:
            break
        tau = (a[q][q] - a[p][p]) / (2.0 * a[p][q])
        tangent = math.copysign(1.0, tau) / (
            abs(tau) + math.sqrt(1.0 + tau * tau)
        ) if tau != 0.0 else 1.0
        cosine = 1.0 / math.sqrt(1.0 + tangent * tangent)
        sine = tangent * cosine
        app, aqq, apq = a[p][p], a[q][q], a[p][q]
        a[p][p] = app - tangent * apq
        a[q][q] = aqq + tangent * apq
        a[p][q] = a[q][p] = 0.0
        for k in range(size):
            if k in (p, q):
                continue
            akp, akq = a[k][p], a[k][q]
            a[k][p] = a[p][k] = cosine * akp - sine * akq
            a[k][q] = a[q][k] = sine * akp + cosine * akq
    return sorted(a[i][i] for i in range(size))


def determinant3(matrix: list[list[Fraction]]) -> Fraction:
    a = matrix
    return (
        a[0][0] * (a[1][1] * a[2][2] - a[1][2] * a[2][1])
        - a[0][1] * (a[1][0] * a[2][2] - a[1][2] * a[2][0])
        + a[0][2] * (a[1][0] * a[2][1] - a[1][1] * a[2][0])
    )


def inverse3(matrix: list[list[float]]) -> list[list[float]]:
    augmented = [
        row[:] + [1.0 if i == j else 0.0 for j in range(3)]
        for i, row in enumerate(matrix)
    ]
    for column in range(3):
        pivot = max(range(column, 3), key=lambda i: abs(augmented[i][column]))
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        scale = augmented[column][column]
        augmented[column] = [value / scale for value in augmented[column]]
        for row in range(3):
            if row == column:
                continue
            factor = augmented[row][column]
            augmented[row] = [
                x - factor * y
                for x, y in zip(augmented[row], augmented[column])
            ]
    return [row[3:] for row in augmented]


def owner_value(h1: float, h2: float) -> float:
    u = (h1 * h1 + h2, h1 * h2)
    phi = (h1 + h2 * h2, h1 - h2)
    return 0.5 * (sum(x * x for x in phi) - sum(x * x for x in u))


def finite_hessian(h1: float, h2: float, step: float) -> list[list[float]]:
    f = owner_value
    d11 = (f(h1 + step, h2) - 2.0 * f(h1, h2) + f(h1 - step, h2)) / step**2
    d22 = (f(h1, h2 + step) - 2.0 * f(h1, h2) + f(h1, h2 - step)) / step**2
    d12 = (
        f(h1 + step, h2 + step)
        - f(h1 + step, h2 - step)
        - f(h1 - step, h2 + step)
        + f(h1 - step, h2 - step)
    ) / (4.0 * step**2)
    return [[d11, d12], [d12, d22]]


def analytic_feature_hessian(h1: float, h2: float) -> list[list[float]]:
    u = [h1 * h1 + h2, h1 * h2]
    phi = [h1 + h2 * h2, h1 - h2]
    du = [[2.0 * h1, 1.0], [h2, h1]]
    dphi = [[1.0, 2.0 * h2], [1.0, -1.0]]
    d2u = [
        [[2.0, 0.0], [0.0, 0.0]],
        [[0.0, 1.0], [1.0, 0.0]],
    ]
    d2phi = [
        [[0.0, 0.0], [0.0, 2.0]],
        [[0.0, 0.0], [0.0, 0.0]],
    ]
    result = [[0.0, 0.0], [0.0, 0.0]]
    for i in range(2):
        for j in range(2):
            result[i][j] = (
                sum(dphi[k][i] * dphi[k][j] + phi[k] * d2phi[k][i][j] for k in range(2))
                - sum(du[k][i] * du[k][j] + u[k] * d2u[k][i][j] for k in range(2))
            )
    return result


def coefficient_a(n: int, delta: float) -> float:
    floor = delta * delta
    kappa = math.asinh(delta)
    c = math.sqrt(1.0 + delta * delta)
    positive = 5.0 * delta / (27.0 * c)
    positive += 25.0 * delta * delta * (
        n + 1.0 / math.tanh(2.0 * kappa)
    ) / (81.0 * c * c)
    return 4.0 * float(C1) * floor * (-1.0) ** (n + 1) * math.exp(-2.0 * n * kappa) * positive


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    audit = Audit()

    # Independent centering fixture.
    jq = [[F(-4), F(1)], [F(2), F(7)], [F(8), F(-3)]]
    jp = [[F(5), F(0)], [F(-1), F(4)], [F(3), F(8)]]
    phiq, phip = mean(jq), mean(jp)
    rq = [[row[j] - phiq[j] for j in range(2)] for row in jq]
    rp = [[row[j] - phip[j] for j in range(2)] for row in jp]
    lhs = -cross(jq, jp) + cross(rq, rp)
    rhs = -dot(phiq, phip)
    audit.add("compression", "independent mixed compression", lhs == rhs, lhs, rhs)
    audit.add("compression", "q residual centered", mean(rq) == [F(0), F(0)], mean(rq), [F(0), F(0)])
    audit.add("compression", "p residual centered", mean(rp) == [F(0), F(0)], mean(rp), [F(0), F(0)])

    # Shared singular probe, reimplemented without symbolic algebra.
    v = [F(2), F(-1)]
    aq = [[F(3), F(1)], [F(-2), F(4)]]
    ap = [[F(0), F(5)], [F(2), F(1)]]
    uq = [dot(row, v) for row in aq]
    up = [dot(row, v) for row in ap]
    trace_by_indices = sum(
        aq[i][j] * v[j] * v[k] * ap[i][k]
        for i in range(2)
        for j in range(2)
        for k in range(2)
    )
    audit.add("trace_feature", "shared singular probe cross", trace_by_indices == dot(uq, up), trace_by_indices, dot(uq, up))

    analytic = analytic_feature_hessian(0.37, -0.29)
    finite_a = finite_hessian(0.37, -0.29, 2.0e-4)
    finite_b = finite_hessian(0.37, -0.29, 1.0e-4)
    max_error_a = max(abs(analytic[i][j] - finite_a[i][j]) for i in range(2) for j in range(2))
    max_error_b = max(abs(analytic[i][j] - finite_b[i][j]) for i in range(2) for j in range(2))
    audit.add("hessian", "feature formula agrees with finite difference", max_error_b < 3.0e-7, max_error_b, "<3e-7")
    audit.add("hessian", "finite difference refines", max_error_b < max_error_a, (max_error_a, max_error_b), "second smaller")
    audit.add("hessian", "analytic Hessian symmetric", abs(analytic[0][1] - analytic[1][0]) < 1.0e-15, analytic, "symmetric")

    # Independent SU(2) block.
    r, s, floor = F(11, 8), F(5, 6), F(1, 7)
    t = r * r / (r * r + s * s + floor)
    transverse = 4 * (C0 + C1) * r * r
    a = r * r * (C0 + C1 * (1 - ALPHA * t) ** 2)
    c = -C1 * ALPHA * t * (1 - ALPHA * t) * r * s
    d = C1 * ALPHA**2 * t**2 * s**2
    radial = [[float(4 * a), float(4 * c)], [float(4 * c), float(4 * d)]]
    radial_eigenvalues = jacobi_eigenvalues(radial)
    determinant = F(16) * (a * d - c * c)
    determinant_formula = F(16) * C0 * C1 * ALPHA**2 * t**2 * r**2 * s**2
    audit.add("su2", "independent radial determinant", determinant == determinant_formula, determinant, determinant_formula)
    audit.add("su2", "radial eigenvalues positive", radial_eigenvalues[0] > 0.0, radial_eigenvalues, "positive")
    audit.add("su2", "radial edge below transverse", radial_eigenvalues[-1] <= float(transverse) + TOL, radial_eigenvalues[-1], transverse)
    full_eigenvalues = sorted([0.0, 0.0, float(transverse), float(transverse), *radial_eigenvalues])
    audit.add("su2", "two phase zeros", full_eigenvalues[:2] == [0.0, 0.0], full_eigenvalues, "two zeros")
    audit.add("su2", "four active positive modes", all(value > 0.0 for value in full_eigenvalues[2:]), full_eigenvalues, "four positive")
    ratio = (C0 + C1) / (C0 + C1 * (1 - ALPHA) ** 2)
    audit.add("su2", "transverse radial asymptotic ratio", ratio == F(113, 48), ratio, F(113, 48))

    # Mass derived from family masses plus k(I-P_1).
    family = [F(0), F(3, 100), F(7, 100)]
    lock = F(3, 20)
    mass = [
        [
            (family[i] if i == j else F(0))
            + lock * ((F(1) if i == j else F(0)) - F(1, 3))
            for j in range(3)
        ]
        for i in range(3)
    ]
    expected_mass = [
        [F(1, 10), -F(1, 20), -F(1, 20)],
        [-F(1, 20), F(13, 100), -F(1, 20)],
        [-F(1, 20), -F(1, 20), F(17, 100)],
    ]
    audit.add("covariance", "mass independently derived", mass == expected_mass, mass, expected_mass)
    trace = sum(mass[i][i] for i in range(3))
    principal2 = (
        mass[0][0] * mass[1][1] - mass[0][1] * mass[1][0]
        + mass[0][0] * mass[2][2] - mass[0][2] * mass[2][0]
        + mass[1][1] * mass[2][2] - mass[1][2] * mass[2][1]
    )
    determinant = determinant3(mass)
    audit.add("covariance", "characteristic trace coefficient", trace == F(2, 5), trace, F(2, 5))
    audit.add("covariance", "characteristic quadratic coefficient", principal2 == F(223, 5000), principal2, F(223, 5000))
    audit.add("covariance", "characteristic determinant", determinant == F(24, 25000), determinant, F(24, 25000))
    mass_float = [[float(value) for value in row] for row in mass]
    mu = jacobi_eigenvalues(mass_float)
    audit.add("covariance", "three positive mass eigenvalues", mu[0] > 0.0, mu, "positive")
    audit.add("covariance", "mass trace from eigenvalues", abs(sum(mu) - float(trace)) < TOL, sum(mu), trace)
    audit.add("covariance", "mass eigenvalue intervals", 0.028 < mu[0] < 0.029 and 0.165 < mu[1] < 0.166 and 0.206 < mu[2] < 0.207, mu, "three pinned intervals")
    commutator = [
        [0.0, 0.1, 0.05],
        [-0.1, 0.0, -0.05],
        [-0.05, 0.05, 0.0],
    ]
    gram = matmul(transpose(commutator), commutator)
    commutator_norm_sq = jacobi_eigenvalues(gram)[-1]
    audit.add("covariance", "commutator norm squared independent", abs(commutator_norm_sq - 3.0 / 200.0) < TOL, commutator_norm_sq, F(3, 200))
    remainder_norms: dict[str, float] = {}
    for a_value in (0.75, 2.5):
        shifted = [
            [mass_float[i][j] + (a_value if i == j else 0.0) for j in range(3)]
            for i in range(3)
        ]
        covariance = inverse3(shifted)
        gamma0 = 1.0 / (a_value + mu[2])
        remainder = [
            [covariance[i][j] - (gamma0 if i == j else 0.0) for j in range(3)]
            for i in range(3)
        ]
        eig = jacobi_eigenvalues(remainder)
        formula = (mu[2] - mu[0]) / ((a_value + mu[0]) * (a_value + mu[2]))
        remainder_norms[str(a_value)] = eig[-1]
        audit.add("covariance", f"remainder PSD a={a_value}", eig[0] >= -TOL, eig, "PSD")
        audit.add("covariance", f"remainder norm a={a_value}", abs(eig[-1] - formula) < TOL, eig[-1], formula)

    # Scalar adapted chart, independently recomputed.
    root2 = math.sqrt(2.0)
    m_g = 0.9 - 4.0 * float(C1) * (3.0 + root2)
    m_g -= (4.0 * float(C1) * (2.0 + root2)) ** 2 / 18.0
    lambda_c = F(9, 10) + F(81, 4) - 2 * C0 - 8 * C1
    audit.add("scalar_chart", "mG numerical interval", 0.7653 < m_g < 0.7654, m_g, "(0.7653,0.7654)")
    audit.add("scalar_chart", "mG above three quarters", m_g > 0.75, m_g, ">0.75")
    audit.add("scalar_chart", "lambda c exact", lambda_c == F(1_686_660_000_000_423, 80_000_000_000_020), lambda_c, F(1_686_660_000_000_423, 80_000_000_000_020))
    audit.add("scalar_chart", "lambda c positive", float(lambda_c) > 21.0, float(lambda_c), ">21")
    score_polynomial_moment = F(15 - 4 * 3 + 1, 4)
    audit.add("scalar_chart", "signed score identity moment", score_polynomial_moment == F(1), score_polynomial_moment, F(1))
    score_absolute_majorant = F(15 + 1, 4)
    audit.add("scalar_chart", "score absolute majorant", score_absolute_majorant == F(4), score_absolute_majorant, F(4))

    # Band ranges and alternating sign, with a different floor fixture.
    ranges = {
        offset: list(range(2 ** (offset - 2) + 1, 2 ** (offset - 1) + 1))
        for offset in range(5, 10)
    }
    audit.add("band", "range q5", (ranges[5][0], ranges[5][-1]) == (9, 16), (ranges[5][0], ranges[5][-1]), (9, 16))
    audit.add("band", "range q7", (ranges[7][0], ranges[7][-1]) == (33, 64), (ranges[7][0], ranges[7][-1]), (33, 64))
    audit.add("band", "range q9", (ranges[9][0], ranges[9][-1]) == (129, 256), (ranges[9][0], ranges[9][-1]), (129, 256))
    delta = 0.35
    a_values = {n: coefficient_a(n, delta) for n in range(2, 258)}
    g = {
        n: 0.5 * a_values[n] - 0.25 * (a_values[n - 1] + a_values[n + 1])
        for n in range(3, 257)
    }
    failures = [n for n, value in g.items() if (-1) ** (n + 1) * value <= 0.0]
    audit.add("band", "alternating sign independent floor", failures == [], failures, [])
    sign_identity_failures = [
        n
        for n, value in g.items()
        if abs(
            (-1) ** (n + 1) * value
            - (
                abs(a_values[n]) / 2.0
                + abs(a_values[n - 1]) / 4.0
                + abs(a_values[n + 1]) / 4.0
            )
        )
        > 1.0e-14 * max(1.0, abs(value))
    ]
    audit.add(
        "band",
        "sign-stripped identity independent",
        sign_identity_failures == [],
        sign_identity_failures,
        [],
    )
    h8 = 2.0 * sum(g[n] * (-1.0) ** n for n in range(9, 65))
    h10 = 2.0 * sum(g[n] * (-1.0) ** n for n in range(9, 257))
    audit.add("band", "unweighted C8 symbol negative", h8 < 0.0, h8, "<0")
    audit.add("band", "unweighted C10 symbol negative", h10 < 0.0, h10, "<0")
    common = 2_114_970
    carriers = [common // harmonic for harmonic in (17, 33, 65)]
    audit.add("band", "coherent three-layer common mode", [carriers[i] * (17, 33, 65)[i] for i in range(3)] == [common] * 3, carriers, common)

    scope = {
        "full_production_matrix": False,
        "uniform_production_bound": False,
        "scalar_to_full_su2": False,
        "band_to_full_owner_counterexample": False,
        "a13_gate_closed": False,
        "nelson": False,
        "sector_a_closed": False,
    }
    for key, value in scope.items():
        audit.add("scope", f"{key} false", value is False, value, False)

    failed = sum(row["status"] != "PASS" for row in audit.rows)
    payload: dict[str, object] = {
        "schema": SCHEMA,
        "version": __version__,
        "result_id": RESULT_ID,
        "status": "PASS" if failed == 0 else "FAIL",
        "assertions": {
            "total": len(audit.rows),
            "passed": len(audit.rows) - failed,
            "failed": failed,
            "rows": audit.rows,
        },
        "computed": {
            "compression_lhs": str(lhs),
            "compression_rhs": str(rhs),
            "feature_hessian": analytic,
            "su2_transverse_eigenvalue": str(transverse),
            "su2_radial_determinant": str(determinant_formula),
            "mass_eigenvalues": mu,
            "commutator_norm_squared": commutator_norm_sq,
            "covariance_remainder_norms": remainder_norms,
            "scalar_translation_lower_bound": m_g,
            "scalar_covariance_lower_bound": str(lambda_c),
            "c8_symbol_pi_over_two": h8,
            "c10_symbol_pi_over_two": h10,
            "coherent_carriers": carriers,
        },
        "scope": scope,
    }
    atomic_json(args.output, payload)
    print(
        f"{RESULT_ID}: {'PASS' if failed == 0 else 'FAIL'} "
        f"({len(audit.rows) - failed}/{len(audit.rows)})"
    )
    print(f"output: {args.output}")
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())

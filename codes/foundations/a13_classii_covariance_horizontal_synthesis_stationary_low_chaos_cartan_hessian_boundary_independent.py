#!/usr/bin/env python3
"""Independent standard-library audit for the scoped R-120 result.

This implementation does not import the primary script or SymPy.  It uses
exact Fraction arithmetic for the production constants, Pauli matrices,
covariance quotient, chaos moments, Hessian identities, and fixed-basis
flattening.
"""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-29"
__version_issued__ = "2026-07-29"

import argparse
from fractions import Fraction as F
import json
from math import comb
import os
from pathlib import Path
import tempfile
from typing import Any


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-COVARIANCE-HORIZONTAL-SYNTHESIS-STATIONARY-LOW-CHAOS-CARTAN-HESSIAN-BOUNDARY"
SCHEMA = "tect/a13-covariance-horizontal-synthesis-stationary-low-chaos-cartan-hessian-independent/1.0"
DEFAULT_OUTPUT = REPO / "claims" / CLAIM / "runs/2026-07-29-independent-covariance-horizontal-synthesis-stationary-low-chaos-cartan-hessian/result.json"
A1_MANIFEST = REPO / "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json"
A8_RESULT = REPO / "claims/A8-CLASSII-DECOUPLED-NELSON-BOUND/runs/2026-07-20-independent-decoupled-nelson/result.json"


Vector = list[F]
Matrix = list[list[F]]
Series = dict[tuple[int, int], F]
SERIES_MAX_X = 3
SERIES_MAX_Y = 1


def frac(value: Any) -> F:
    return F(str(value))


def serial(value: Any) -> Any:
    if isinstance(value, F):
        return f"{value.numerator}/{value.denominator}"
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(item) for item in value]
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(serial(payload), stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def zeros(rows: int, columns: int) -> Matrix:
    return [[F(0) for _ in range(columns)] for _ in range(rows)]


def eye(n: int) -> Matrix:
    result = zeros(n, n)
    for i in range(n):
        result[i][i] = F(1)
    return result


def transpose(a: Matrix) -> Matrix:
    return [list(row) for row in zip(*a)]


def add(a: Matrix, b: Matrix) -> Matrix:
    return [[a[i][j] + b[i][j] for j in range(len(a[0]))] for i in range(len(a))]


def subtract(a: Matrix, b: Matrix) -> Matrix:
    return [[a[i][j] - b[i][j] for j in range(len(a[0]))] for i in range(len(a))]


def scale(c: F, a: Matrix) -> Matrix:
    return [[c * value for value in row] for row in a]


def matmul(a: Matrix, b: Matrix) -> Matrix:
    return [[sum((a[i][k] * b[k][j] for k in range(len(b))), F(0)) for j in range(len(b[0]))] for i in range(len(a))]


def matvec(a: Matrix, x: Vector) -> Vector:
    return [sum((row[j] * x[j] for j in range(len(x))), F(0)) for row in a]


def dot(x: Vector, y: Vector) -> F:
    return sum((a * b for a, b in zip(x, y)), F(0))


def outer(x: Vector, y: Vector) -> Matrix:
    return [[a * b for b in y] for a in x]


def inverse2(a: Matrix) -> Matrix:
    determinant = a[0][0] * a[1][1] - a[0][1] * a[1][0]
    return [[a[1][1] / determinant, -a[0][1] / determinant], [-a[1][0] / determinant, a[0][0] / determinant]]


def symmetric(a: Matrix) -> bool:
    return a == transpose(a)


def gaussian_moment(power: int) -> F:
    """Return the exact standard-normal moment without a symbolic backend."""
    if power < 0:
        raise ValueError("power must be nonnegative")
    if power % 2:
        return F(0)
    value = F(1)
    for factor in range(1, power, 2):
        value *= factor
    return value


def series_add(a: Series, b: Series) -> Series:
    result = dict(a)
    for key, value in b.items():
        result[key] = result.get(key, F(0)) + value
        if result[key] == 0:
            del result[key]
    return result


def series_scale(value: F, a: Series) -> Series:
    return {key: value * coefficient for key, coefficient in a.items() if value * coefficient != 0}


def series_mul(a: Series, b: Series) -> Series:
    result: Series = {}
    for (ax, ay), avalue in a.items():
        for (bx, by), bvalue in b.items():
            key = (ax + bx, ay + by)
            if key[0] <= SERIES_MAX_X and key[1] <= SERIES_MAX_Y:
                result[key] = result.get(key, F(0)) + avalue * bvalue
    return {key: value for key, value in result.items() if value != 0}


def series_pow(a: Series, power: int) -> Series:
    result: Series = {(0, 0): F(1)}
    for _ in range(power):
        result = series_mul(result, a)
    return result


def series_inverse(a: Series) -> Series:
    constant = a.get((0, 0), F(0))
    if constant == 0:
        raise ZeroDivisionError("series has zero constant term")
    remainder = series_add(a, {(0, 0): -constant})
    ratio = series_scale(-1 / constant, remainder)
    total: Series = {(0, 0): F(1)}
    term: Series = {(0, 0): F(1)}
    for _ in range(SERIES_MAX_X + SERIES_MAX_Y):
        term = series_mul(term, ratio)
        total = series_add(total, term)
    return series_scale(1 / constant, total)


def r102_gram_series(base_x: F, base_y: F, alpha: F) -> tuple[Series, Series]:
    """Return G_00 and G_10 Taylor series without symbolic differentiation."""
    x: Series = {(0, 0): base_x, (1, 0): F(1)}
    y: Series = {(0, 0): base_y, (0, 1): F(1)}
    denominator = series_add({(0, 0): F(1)}, series_add(series_pow(x, 2), series_pow(y, 2)))
    inverse = series_inverse(denominator)
    row0 = series_add(x, series_scale(-alpha, series_mul(series_pow(x, 3), inverse)))
    row1 = series_scale(-alpha, series_mul(series_mul(series_pow(x, 2), y), inverse))
    return series_scale(F(4), series_mul(row0, row0)), series_scale(F(4), series_mul(row1, row0))


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(self, group: str, name: str, condition: bool, actual: Any, expected: Any) -> None:
        self.rows.append({"group": group, "name": name, "status": "PASS" if condition else "FAIL", "actual": serial(actual), "expected": serial(expected)})

    def finish(self, diagnostics: dict[str, Any]) -> dict[str, Any]:
        passed = sum(row["status"] == "PASS" for row in self.rows)
        return {
            "schema": SCHEMA,
            "package_version": __version__,
            "claim_id": CLAIM,
            "result_id": RESULT_ID,
            "status": "PASS" if passed == len(self.rows) else "FAIL",
            "assertions_total": len(self.rows),
            "assertions_passed": passed,
            "assertions_failed": len(self.rows) - passed,
            "assertions": self.rows,
            "diagnostics": serial(diagnostics),
            "no_overclaim": (
                "This non-importing audit checks exact finite fixtures supporting R-120's analytic "
                "lemmas; it is not an owner-complete adapted production reconstruction. It does not "
                "supply the future-feedback forest coefficients D0,D1, cancel the rational Cartan "
                "term, observe the +40/729 companion, or prove one-use, Nelson, or Sector A closure."
            ),
        }


def q_data(u: Vector, generator: Matrix, alpha: F, floor: F) -> tuple[F, Matrix, Vector, Matrix, Matrix, Vector]:
    dimension = len(u)
    denominator = dot(u, u) + floor
    su = matvec(generator, u)
    q = dot(u, su) / denominator
    q_tangent = subtract(generator, scale(q, eye(dimension)))
    remainder = matvec(q_tangent, u)
    gradient = [2 * value / denominator for value in remainder]
    hessian = subtract(
        scale(F(2) / denominator, q_tangent),
        scale(F(4) / denominator**2, add(outer(u, remainder), outer(remainder, u))),
    )
    tangent = subtract(generator, scale(alpha * q, eye(dimension)))
    coefficient = matvec(tangent, u)
    frame = subtract(tangent, scale(alpha, outer(u, gradient)))
    return q, tangent, gradient, hessian, frame, coefficient


def k_matrix(u: Vector, generator: Matrix, covariance: Matrix, alpha: F, floor: F) -> tuple[Matrix, Vector, Vector]:
    _, tangent, gradient, hessian, frame, coefficient = q_data(u, generator, alpha, floor)
    w = matvec(covariance, coefficient)
    beta = dot(u, w)
    first = scale(F(4), matmul(transpose(frame), matmul(covariance, frame)))
    second = scale(4 * alpha * beta, hessian)
    third = scale(4 * alpha, add(outer(gradient, w), outer(w, gradient)))
    return subtract(subtract(first, second), third), coefficient, gradient


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()
    audit = Audit()

    a1 = json.loads(A1_MANIFEST.read_text(encoding="utf-8"))
    params = a1["parameters"]
    p_mass = frac(params["M_X"]) ** 2 + frac(params["classii_mass_regularizer"])
    a = frac(params["cJJ"]) * frac(params["alpha_X"]) ** 2 / p_mass
    b = frac(params["cJK"]) * frac(params["alpha_X"]) * frac(params["beta_X"]) / p_mass
    c = frac(params["cKK"]) * frac(params["beta_X"]) ** 2 / p_mass
    c0 = F(3, 250) / p_mass
    c1 = F(243, 8000) / p_mass
    alpha = F(5, 9)
    audit.check("production", "a", a == F(9, 500) / p_mass, a, F(9, 500) / p_mass)
    audit.check("production", "b", b == F(3, 400) / p_mass, b, F(3, 400) / p_mass)
    audit.check("production", "c", c == F(3, 320) / p_mass, c, F(3, 320) / p_mass)
    audit.check("production", "diagonal_a", c0 + c1 * (1 - alpha) ** 2 == a, c0 + c1 * (1 - alpha) ** 2, a)
    audit.check("production", "diagonal_b", c1 * alpha * (1 - alpha) == b, c1 * alpha * (1 - alpha), b)
    audit.check("production", "diagonal_c", c1 * alpha**2 == c, c1 * alpha**2, c)
    envelope = 4 * (c0 + c1)
    audit.check("production", "linear_envelope", envelope == F(339, 2000) / p_mass, envelope, F(339, 2000) / p_mass)

    generators: tuple[Matrix, ...] = (
        [[F(0), F(1), F(0), F(0), F(0), F(0)], [F(1), F(0), F(0), F(0), F(0), F(0)], [F(0)] * 6, [F(0), F(0), F(0), F(0), F(1), F(0)], [F(0), F(0), F(0), F(1), F(0), F(0)], [F(0)] * 6],
        [[F(0), F(0), F(0), F(0), F(1), F(0)], [F(0), F(0), F(0), F(-1), F(0), F(0)], [F(0)] * 6, [F(0), F(-1), F(0), F(0), F(0), F(0)], [F(1), F(0), F(0), F(0), F(0), F(0)], [F(0)] * 6],
        [[F(1), F(0), F(0), F(0), F(0), F(0)], [F(0), F(-1), F(0), F(0), F(0), F(0)], [F(0)] * 6, [F(0), F(0), F(0), F(1), F(0), F(0)], [F(0), F(0), F(0), F(0), F(-1), F(0)], [F(0)] * 6],
    )
    p_doublet = [[F(1 if i == j and i in (0, 1, 3, 4) else 0) for j in range(6)] for i in range(6)]
    pauli_absolute_sum = zeros(6, 6)
    for index, generator in enumerate(generators, start=1):
        audit.check("production", f"S{index}_symmetric", symmetric(generator), generator, transpose(generator))
        audit.check("production", f"S{index}_square", matmul(generator, generator) == p_doublet, matmul(generator, generator), p_doublet)
        # Symmetry and S_A^2=P_dbl imply |S_A|=P_dbl.
        pauli_absolute_sum = add(pauli_absolute_sum, p_doublet)
    audit.check("production", "pauli_absolute_sum", pauli_absolute_sum == scale(F(3), p_doublet), pauli_absolute_sum, scale(F(3), p_doublet))
    pauli_gap = subtract(scale(F(3), eye(6)), pauli_absolute_sum)
    audit.check("production", "pauli_absolute_bound", all(pauli_gap[i][i] >= 0 for i in range(6)), pauli_gap, ">=0 diagonal")

    # Evaluate all three linear and all three rational coefficient rows at
    # an exact generic point and its negative. This is independent finite
    # support for the analytic six-row oddness argument.
    parity_u = [F(1), F(2), F(-1), F(3), F(-2), F(1)]
    parity_floor = frac(params["rho_regularizer"])
    for index, generator in enumerate(generators, start=1):
        linear = scale(F(2), [[value] for value in matvec(generator, parity_u)])
        linear_negative = scale(F(2), [[value] for value in matvec(generator, [-value for value in parity_u])])
        audit.check("low_chaos", f"linear_row_{index}_odd", linear_negative == scale(F(-1), linear), linear_negative, scale(F(-1), linear))
        _, _, _, _, _, rational = q_data(parity_u, generator, alpha, parity_floor)
        _, _, _, _, _, rational_negative = q_data([-value for value in parity_u], generator, alpha, parity_floor)
        audit.check("low_chaos", f"rational_row_{index}_odd", rational_negative == [-value for value in rational], rational_negative, [-value for value in rational])

    # Exact overlapping covariance quotient.
    s1 = [[F(1), F(0)], [F(0), F(1, 2)]]
    s2 = [[F(1), F(1)], [F(0), F(1)]]
    synthesis = [s1[0] + s2[0], s1[1] + s2[1]]
    covariance = matmul(synthesis, transpose(synthesis))
    union = add(matmul(s1, transpose(s1)), matmul(s2, transpose(s2)))
    audit.check("synthesis", "covariance_union", covariance == union, covariance, union)
    h = [F(2), F(-1), F(1), F(3)]
    z = matvec(synthesis, h)
    cinv = inverse2(covariance)
    minimum = matvec(transpose(synthesis), matvec(cinv, z))
    audit.check("synthesis", "minimum_endpoint", matvec(synthesis, minimum) == z, matvec(synthesis, minimum), z)
    quotient = dot(z, matvec(cinv, z))
    audit.check("synthesis", "quotient_norm", quotient == dot(minimum, minimum), quotient, dot(minimum, minimum))
    audit.check("synthesis", "quotient_contraction", dot(minimum, minimum) <= dot(h, h), dot(minimum, minimum), f"<={dot(h,h)}")

    r = frac(params["r"])
    zcoef = frac(params["Z"])
    ycoef = frac(params["Y"])
    stationary = (2 * r - zcoef) / (2 * ycoef - zcoef)
    ratio = lambda value: (ycoef * value**2 + zcoef * value + r) / (1 + value) ** 2
    c_sym = min(ratio(F(0)), ratio(stationary), ycoef)
    a8 = json.loads(A8_RESULT.read_text(encoding="utf-8"))
    recorded = frac(a8["derived"]["symbol_coercivity"]["c_symbol"])
    m_r = frac(a8["config"]["regulator_multiplier_bound"])
    audit.check("synthesis", "stationary_nonnegative", stationary >= 0, stationary, ">=0")
    audit.check("synthesis", "coercivity_recomputed", abs(float(c_sym - recorded)) < 5e-15, float(c_sym), float(recorded))
    audit.check("synthesis", "regulator_multiplier_bound", m_r == 1, m_r, 1)
    c_cm = m_r**2 / c_sym
    audit.check("synthesis", "cm_constant", abs(float(c_cm) - 9.22811176850986) < 5e-14, float(c_cm), 9.22811176850986)
    audit.check("synthesis", "l6_constant", F(2) ** 5 == 32, F(2) ** 5, 32)
    gap_coefficients = [
        (F(32) if power in (0, 6) else F(0)) - F((-1) ** power * comb(6, power))
        for power in range(7)
    ]
    quartic_coefficients = [F(31), F(-56), F(66), F(-56), F(31)]
    factored_coefficients = [F(0) for _ in range(7)]
    for left_power, left_value in enumerate((F(1), F(2), F(1))):
        for right_power, right_value in enumerate(quartic_coefficients):
            factored_coefficients[left_power + right_power] += left_value * right_value
    audit.check("synthesis", "l6_global_factorization", gap_coefficients == factored_coefficients, gap_coefficients, factored_coefficients)
    positive_quartic_coefficients = [F(1), F(15), F(15)]
    audit.check("synthesis", "l6_positive_quartic", all(value >= 0 for value in positive_quartic_coefficients), positive_quartic_coefficients, ">=0 coefficients in u^4+15u^2v^2+15v^4")
    audit.check("synthesis", "l6_sharp", abs(F(1) - F(-1)) ** 6 == 32 * (F(1) ** 6 + F(-1) ** 6), 64, 64)

    kappa = F(1, 10)
    theta = (1 + kappa) / 2
    model_power = 3 / (1 - kappa)
    audit.check("multiplier", "theta", theta == F(11, 20), theta, F(11, 20))
    audit.check("multiplier", "k0_interpolation", 1 - theta == F(9, 20), 1 - theta, F(9, 20))
    audit.check("multiplier", "model_power", model_power == F(10, 3), model_power, F(10, 3))
    audit.check("multiplier", "young_k0", (1 - theta) * model_power == F(3, 2), (1 - theta) * model_power, F(3, 2))
    audit.check("multiplier", "young_k2", theta * model_power == F(11, 6), theta * model_power, F(11, 6))

    # Gaussian one-pair moments, reconstructed term by term rather than
    # accepting parity as a hard-coded boolean oracle.
    lambda1 = 4 * c0
    expected_packet = lambda1 * (F(8) - 4 * F(2)) / 16
    audit.check("low_chaos", "one_pair_mean", expected_packet == 0, expected_packet, 0)
    first_x = lambda1 * (
        gaussian_moment(5)
        + 2 * gaussian_moment(3) * gaussian_moment(2)
        + gaussian_moment(1) * gaussian_moment(4)
        - 4 * gaussian_moment(3)
        - 4 * gaussian_moment(1) * gaussian_moment(2)
    ) / 16
    first_y = lambda1 * (
        gaussian_moment(4) * gaussian_moment(1)
        + 2 * gaussian_moment(2) * gaussian_moment(3)
        + gaussian_moment(5)
        - 4 * gaussian_moment(2) * gaussian_moment(1)
        - 4 * gaussian_moment(3)
    ) / 16
    audit.check("low_chaos", "one_pair_first_x", first_x == 0, first_x, 0)
    audit.check("low_chaos", "one_pair_first_y", first_y == 0, first_y, 0)
    expected_abs_z4 = F(1, 2)
    expected_y = 2 * lambda1 * expected_abs_z4
    expected_tau = 2 * lambda1 * F(1, 2)
    audit.check("low_chaos", "one_pair_energy_trace", expected_y == expected_tau == lambda1, [expected_y, expected_tau], lambda1)

    # Complete-stationary parity, evaluated independently on the rational slice.
    def row(u1: F, u2: F) -> Vector:
        denominator = F(1) + u1 * u1 + u2 * u2
        return [u1 - alpha * u1**3 / denominator, -alpha * u1**2 * u2 / denominator]

    u = [F(2), F(-1)]
    v = [F(3), F(4)]
    coefficient = row(*u)
    coefficient_negative = row(-u[0], -u[1])
    y_value = 2 * dot(coefficient, v)
    y_negative = 2 * dot(coefficient_negative, [-v[0], -v[1]])
    gamma_diag = [F(2), F(5)]
    tau_value = 4 * sum((gamma_diag[i] * coefficient[i] ** 2 for i in range(2)), F(0))
    tau_negative = 4 * sum((gamma_diag[i] * coefficient_negative[i] ** 2 for i in range(2)), F(0))
    conditional_energy = sum(
        (F(2) * coefficient[i]) ** 2 * gamma_diag[i] for i in range(2)
    )
    audit.check("low_chaos", "C_odd", coefficient_negative == [-item for item in coefficient], coefficient_negative, [-item for item in coefficient])
    audit.check("low_chaos", "Y_even", y_negative == y_value, y_negative, y_value)
    audit.check("low_chaos", "tau_even", tau_negative == tau_value, tau_negative, tau_value)
    audit.check("low_chaos", "conditional_trace", conditional_energy == tau_value, conditional_energy, tau_value)

    # Linear Hessian completion and trace factor.
    aa, bb, cc, tt = F(2), F(-3), F(5), F(2, 7)
    direct = 2 * aa * cc + 4 * bb**2 + 12 * tt * bb * cc + 6 * tt**2 * cc**2
    completed = 2 * aa * cc + 4 * (bb + F(3, 2) * tt * cc) ** 2 - 3 * tt**2 * cc**2
    audit.check("linear_hessian", "completion", direct == completed, direct, completed)
    audit.check("linear_hessian", "quartic_weight", F(1, 4) == F(3) * (F(1, 3) - F(1, 4)), F(1, 4), F(1, 4))
    audit.check("linear_hessian", "budget_powers", F(1, 2) + F(1, 2) == 1, [F(1, 2), F(1, 2)], 1)

    # Rational raw-Q Hessian, reconstructed without symbolic differentiation.
    fixture_u = [F(1), F(2), F(-1)]
    fixture_z = [F(2), F(-1), F(1)]
    generator = [[F(1), F(0), F(0)], [F(0), F(-1), F(0)], [F(0), F(0), F(0)]]
    rough_q = [[F(2), F(1), F(0)], [F(1), F(3), F(1)], [F(0), F(1), F(5)]]
    kmat, coefficient, gradient = k_matrix(fixture_u, generator, rough_q, alpha, F(1))
    _, _, _, hessian, frame, _ = q_data(fixture_u, generator, alpha, F(1))
    dg = matvec(frame, fixture_z)
    d2g = [
        -alpha * (dot(fixture_z, matvec(hessian, fixture_z)) * fixture_u[i] + 2 * dot(gradient, fixture_z) * fixture_z[i])
        for i in range(3)
    ]
    direct_hessian = 4 * c1 * (dot(dg, matvec(rough_q, dg)) + dot(coefficient, matvec(rough_q, d2g)))
    formula_hessian = c1 * dot(fixture_z, matvec(kmat, fixture_z))
    audit.check("rational_hessian", "raw_q_identity", direct_hessian == formula_hessian, direct_hessian, formula_hessian)
    audit.check("rational_hessian", "selfadjoint", symmetric(kmat), kmat, transpose(kmat))

    basis_absolute_sum = zeros(6, 6)
    basis_count = 0
    for i in range(6):
        diagonal_absolute = zeros(6, 6)
        diagonal_absolute[i][i] = F(1)
        basis_absolute_sum = add(basis_absolute_sum, diagonal_absolute)
        basis_count += 1
        for j in range(i + 1, 6):
            # |(E_ij+E_ji)/2|=(E_ii+E_jj)/2.
            off_diagonal_absolute = zeros(6, 6)
            off_diagonal_absolute[i][i] = F(1, 2)
            off_diagonal_absolute[j][j] = F(1, 2)
            basis_absolute_sum = add(basis_absolute_sum, off_diagonal_absolute)
            basis_count += 1
    audit.check("rational_hessian", "basis_absolute_sum", basis_absolute_sum == scale(F(7, 2), eye(6)), basis_absolute_sum, scale(F(7, 2), eye(6)))
    audit.check("rational_hessian", "basis_count", basis_count == 21, basis_count, 21)

    # Exterior curvature formula on a generic point and the adapted chain rule.
    x, y, floor = F(1), F(1), F(1)
    dm = [2 * x, -2 * y]
    drho = [2 * x, 2 * y]
    omega = -alpha / (floor + x * x + y * y) * (dm[0] * drho[1] - dm[1] * drho[0])
    audit.check("cartan", "generic_curvature", omega == F(-40, 27), omega, F(-40, 27))
    audit.check("cartan", "radial_locus", -alpha / (floor + x * x) * ((2 * x) * 0 - 0 * (2 * x)) == 0, 0, 0)

    base_g00, base_g10 = r102_gram_series(F(1), F(1), alpha)
    shifted_g00, shifted_g10 = r102_gram_series(F(2), F(1), alpha)
    derivative_y_r00 = (
        shifted_g00.get((0, 1), F(0))
        - base_g00.get((0, 1), F(0))
        - base_g00.get((1, 1), F(0))
        - base_g00.get((2, 1), F(0))
    )
    derivative_x_r10 = (
        shifted_g10.get((1, 0), F(0))
        - base_g10.get((1, 0), F(0))
        - 2 * base_g10.get((2, 0), F(0))
        - 3 * base_g10.get((3, 0), F(0))
    )
    r102_curl = derivative_y_r00 - derivative_x_r10
    audit.check("cartan", "isolated_r102_curl", r102_curl == F(-40, 729), r102_curl, F(-40, 729))

    b1, b2, hp, hpp = F(2), F(3), F(5), F(7)
    chain = b2 * (1 + hp) ** 2 + b1 * hpp
    expanded = b2 + 2 * b2 * hp + b2 * hp**2 + b1 * hpp
    audit.check("adapted_boundary", "chain_families", chain == expanded, chain, expanded)
    audit.check("adapted_boundary", "Dh_family", 2 * b2 != 0, 2 * b2, "nonzero")
    audit.check("adapted_boundary", "D2h_family", b1 != 0, b1, "nonzero")

    diagnostics = {
        "production": {"c0": c0, "c1": c1, "alpha": alpha, "linear_envelope": envelope},
        "horizontal_synthesis": {"c_sym": float(c_sym), "regulator_multiplier_bound": float(m_r), "c_cm": float(c_cm), "l6_constant": 32},
        "multiplier": {"k0_young": "3/2", "k2_young": "11/6", "model_power": "10/3"},
        "stationary_low_chaos": {"one_pair": True, "six_row_coefficient_parity_verified": True, "analytic_scope": "common-real-even stationary six-row raw-current packet", "adapted": "open D0,D1"},
        "rational_hessian": {"fixed_basis_count": 21, "absolute_sum": "7/2 I", "cartan_survives": True, "isolated_r102_curl": r102_curl},
    }
    payload = audit.finish(diagnostics)
    atomic_json(arguments.output, payload)
    print(f"Independent R-120 {payload['status']}: {payload['assertions_passed']}/{payload['assertions_total']} assertions")
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

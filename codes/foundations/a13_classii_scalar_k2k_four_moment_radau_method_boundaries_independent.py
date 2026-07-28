#!/usr/bin/env python3
"""Independent stdlib-only exact audit of the R-115 method boundaries.

This scratch certificate intentionally does not import SymPy or any TECT
implementation module.  It constructs the relevant bivariate polynomials from
``fractions.Fraction``, converts every declared rectangle to its tensor
Bernstein basis, reconstructs the power polynomial, and checks a rational
upper bound proving failure of the full Kearns--Saul coefficient immediately
beyond the certified endpoint.
"""

from __future__ import annotations

from fractions import Fraction as F
from hashlib import sha256
from math import comb, factorial as math_factorial
import argparse
import json
import os
from pathlib import Path
import tempfile


Poly = dict[tuple[int, int], F]
VERSION = "1.0.0"
SCHEMA = "tect/a13-scalar-k2k-four-moment-radau-method-boundaries-independent/1.0"
REPO = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = REPO / "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/runs/2026-07-28-independent-scalar-k2k-four-moment-radau-method-boundaries/result.json"


def atomic_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def clean(p: Poly) -> Poly:
    return {key: value for key, value in p.items() if value}


def add(*polynomials: Poly) -> Poly:
    out: Poly = {}
    for polynomial in polynomials:
        for key, value in polynomial.items():
            out[key] = out.get(key, F(0)) + value
    return clean(out)


def scale(polynomial: Poly, factor: F | int) -> Poly:
    factor = F(factor)
    return clean({key: factor * value for key, value in polynomial.items()})


def multiply(left: Poly, right: Poly) -> Poly:
    out: Poly = {}
    for (i, j), a in left.items():
        for (k, ell), value in right.items():
            key = (i + k, j + ell)
            out[key] = out.get(key, F(0)) + a * value
    return clean(out)


def power(polynomial: Poly, exponent: int) -> Poly:
    out: Poly = {(0, 0): F(1)}
    base = polynomial
    while exponent:
        if exponent & 1:
            out = multiply(out, base)
        base = multiply(base, base)
        exponent //= 2
    return out


def monomial(i: int, j: int, coefficient: F | int = 1) -> Poly:
    return {(i, j): F(coefficient)}


def affine_box(polynomial: Poly, b0: F, b1: F, c0: F, c1: F) -> Poly:
    """Substitute b=b0+(b1-b0)u and c=c0+(c1-c0)v."""
    out: Poly = {}
    db, dc = b1 - b0, c1 - c0
    for (ib, ic), coefficient in polynomial.items():
        for m in range(ib + 1):
            b_coefficient = F(comb(ib, m)) * b0 ** (ib - m) * db**m
            for n in range(ic + 1):
                c_coefficient = F(comb(ic, n)) * c0 ** (ic - n) * dc**n
                key = (m, n)
                out[key] = out.get(key, F(0)) + coefficient * b_coefficient * c_coefficient
    return clean(out)


def bernstein(polynomial: Poly) -> tuple[int, int, list[F]]:
    degree_b = max(i for i, _ in polynomial)
    degree_c = max(j for _, j in polynomial)
    coefficients: list[F] = []
    for i in range(degree_b + 1):
        for j in range(degree_c + 1):
            value = F(0)
            for (m, n), coefficient in polynomial.items():
                if m <= i and n <= j:
                    value += (
                        coefficient
                        * F(comb(i, m), comb(degree_b, m))
                        * F(comb(j, n), comb(degree_c, n))
                    )
            coefficients.append(value)
    return degree_b, degree_c, coefficients


def bernstein_to_power(coefficients: list[F], degree_b: int, degree_c: int) -> Poly:
    out: Poly = {}
    cursor = 0
    for i in range(degree_b + 1):
        first: dict[int, F] = {}
        for m in range(i, degree_b + 1):
            first[m] = F(comb(degree_b, i) * comb(degree_b - i, m - i) * (-1) ** (m - i))
        for j in range(degree_c + 1):
            second: dict[int, F] = {}
            for n in range(j, degree_c + 1):
                second[n] = F(comb(degree_c, j) * comb(degree_c - j, n - j) * (-1) ** (n - j))
            coefficient = coefficients[cursor]
            cursor += 1
            for m, first_value in first.items():
                for n, second_value in second.items():
                    key = (m, n)
                    out[key] = out.get(key, F(0)) + coefficient * first_value * second_value
    return clean(out)


def fraction_text(value: F) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def coefficient_hash(coefficients: list[F]) -> str:
    encoded = "\n".join(fraction_text(value) for value in coefficients).encode("ascii")
    return sha256(encoded).hexdigest()


def evaluate(polynomial: Poly, b: F, c: F) -> F:
    return sum(coefficient * b**i * c**j for (i, j), coefficient in polynomial.items())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    k2 = add(monomial(0, 2), scale(monomial(0, 1), -1), monomial(0, 0, F(1, 2)))
    k1 = {
        (0, 3): F(-3, 4),
        (0, 2): F(5, 4),
        (0, 1): F(1, 4),
        (0, 0): F(1, 4),
    }
    k0 = {
        (0, 4): F(153, 64),
        (0, 3): F(-156, 64),
        (0, 2): F(82, 64),
        (0, 1): F(-4, 64),
        (0, 0): F(5, 64),
    }
    covariance = add(multiply(monomial(2, 0), k2), multiply(monomial(1, 0), k1), k0)
    reserve = {
        (0, 4): F(33, 64),
        (0, 3): F(-36, 64),
        (0, 2): F(22, 64),
        (0, 1): F(-4, 64),
        (0, 0): F(1, 64),
    }
    variance = scale(add(covariance, scale(reserve, -1)), F(1, 2))
    beta_square = monomial(2, 0, F(1, 4))
    q_polynomial = add(variance, scale(beta_square, -1))
    plus = add(beta_square, variance)
    minus = add(beta_square, scale(variance, -1))
    fifth_proxy = add(
        scale(multiply(multiply(covariance, beta_square), power(plus, 4)), 30),
        scale(multiply(multiply(multiply(covariance, beta_square), power(minus, 2)), power(plus, 2)), 10),
        scale(multiply(multiply(covariance, beta_square), power(minus, 4)), 6),
        scale(power(plus, 6), -15),
    )

    b0, b1 = F(643, 200), F(103, 32)
    regions = (
        ("Q_LOW", q_polynomial, F(0), F(1, 10), (2, 4), 15),
        ("T4_A", fifth_proxy, F(1, 10), F(37, 160), (12, 24), 325),
        ("T4_B", fifth_proxy, F(37, 160), F(19, 64), (12, 24), 325),
        ("T4_C1", fifth_proxy, F(19, 64), F(211, 640), (12, 24), 325),
        ("T4_C2", fifth_proxy, F(211, 640), F(29, 80), (12, 24), 325),
        ("T4_D", fifth_proxy, F(29, 80), F(5, 8), (12, 24), 325),
        ("Q_HIGH", q_polynomial, F(5, 8), F(1), (2, 4), 15),
    )
    certificates: dict[str, object] = {}
    total = 0
    for label, polynomial, c0, c1, expected_degree, expected_count in regions:
        transported = affine_box(polynomial, b0, b1, c0, c1)
        degree_b, degree_c, coefficients = bernstein(transported)
        assert (degree_b, degree_c) == expected_degree
        assert len(coefficients) == expected_count
        assert all(value > 0 for value in coefficients)
        assert bernstein_to_power(coefficients, degree_b, degree_c) == transported
        total += len(coefficients)
        certificates[label] = {
            "c_interval": [fraction_text(c0), fraction_text(c1)],
            "degree": [degree_b, degree_c],
            "coefficient_count": len(coefficients),
            "minimum": fraction_text(min(coefficients)),
            "sha256": coefficient_hash(coefficients),
            "reconstruction": "PASS",
            "reconstructed_power_terms": len(transported),
        }
    assert total == 1655

    witness_b, witness_c = F(3219, 1000), F(31, 100)
    witness_k = evaluate(covariance, witness_b, witness_c)
    witness_v = evaluate(variance, witness_b, witness_c)
    witness_beta = witness_b / 2
    witness_beta_square = witness_beta**2
    witness_a = witness_beta_square + witness_v
    witness_d = witness_beta_square - witness_v
    witness_y = witness_d / witness_a
    witness_r = witness_a / witness_beta
    witness_q = witness_v - witness_beta_square
    assert 0 < witness_y < 1 and witness_q < 0
    ratio_upper = 1 + witness_y**2 / 3 + witness_y**4 / (5 * (1 - witness_y**2))
    upper_margin = 2 * witness_k * ratio_upper - witness_r**2
    assert upper_margin < 0
    tau_star_upper = 4 * witness_y / (witness_r * (1 - witness_y**2))
    tau_star_gap = F(1, 8) - tau_star_upper
    residual_tau_cap = (32 * witness_b + 20) / (2 * witness_b + 1) ** 2
    residual_cap_gap = residual_tau_cap - 2
    assert tau_star_gap > 0 and residual_cap_gap > 0
    assert witness_b - b1 == F(1, 4000)

    support = (F(-1), F(0), F(2))
    weights = (F(1, 2), F(1, 4), F(1, 4))
    mean = sum((weight * value for weight, value in zip(weights, support)), F(0))
    variance_fixture = sum((weight * (value - mean) ** 2 for weight, value in zip(weights, support)), F(0))
    reserve_k = F(16, 5)
    exp_minus_half_lower = sum((F(-1, 2) ** n / F(math_factorial(n)) for n in range(4)), F(0))
    exp_one_lower = sum((F(1, math_factorial(n)) for n in range(7)), F(0))
    exp_one_fifth_upper = F(61, 50) + F(2, 1425)
    laplace_lower = exp_minus_half_lower / 2 + F(1, 4) + exp_one_lower / 4
    rational_gap = laplace_lower - exp_one_fifth_upper
    assert mean == 0 and variance_fixture == F(3, 2) and reserve_k > 2 * variance_fixture
    assert exp_minus_half_lower == F(29, 48)
    assert exp_one_lower == F(1957, 720)
    assert F(1, 750) / (1 - F(1, 20)) == F(2, 1425)
    assert rational_gap == F(2789, 273600) > 0

    payload = {
        "schema": SCHEMA,
        "version": VERSION,
        "status": "PASS",
        "source": {
            "path": str(Path(__file__).resolve()),
            "sha256": sha256(Path(__file__).resolve().read_bytes()).hexdigest()
        },
        "engine": "stdlib fractions.Fraction sparse bivariate polynomial; no SymPy",
        "scope": {
            "b_interval": [fraction_text(b0), fraction_text(b1)],
            "c_interval": ["0", "1"],
            "classifier": "Q>=0 or fifth-order atanh T4>0",
        },
        "certificates": certificates,
        "total_exact_positive_coefficients": total,
        "identities": {
            "every_Bernstein_power_reconstruction": "PASS",
            "fifth_proxy": "30*K*B*(B+V)^4 + 10*K*B*(B-V)^2*(B+V)^2 + 6*K*B*(B-V)^4 - 15*(B+V)^6",
            "atanh_lower_remainder_derivative": "y^6/(1-y^2)",
        },
        "exact_KS_failure_witness": {
            "b": fraction_text(witness_b),
            "c": fraction_text(witness_c),
            "distance_above_certified_endpoint": fraction_text(witness_b - b1),
            "beta": fraction_text(witness_beta),
            "K": fraction_text(witness_k),
            "V": fraction_text(witness_v),
            "A": fraction_text(witness_a),
            "D": fraction_text(witness_d),
            "Q": fraction_text(witness_q),
            "r": fraction_text(witness_r),
            "y": fraction_text(witness_y),
            "atanh_ratio_upper": fraction_text(ratio_upper),
            "upper_KS_margin": fraction_text(upper_margin),
            "tau_star_rational_upper": fraction_text(tau_star_upper),
            "tau_star_upper_below_one_eighth_gap": fraction_text(tau_star_gap),
            "residual_tau_cap": fraction_text(residual_tau_cap),
            "residual_tau_cap_above_two_gap": fraction_text(residual_cap_gap),
            "atanh_upper_derivation": "atanh(y)/y=sum_{n>=0} y^(2n)/(2n+1) <=1+y^2/3+y^4/[5(1-y^2)] for 0<y<1",
            "sharp_KS_equality_time": "tau_star=4*atanh(y)/r, with 0<tau_star<1/8<R(b)",
            "verdict": "full exact Kearns-Saul coefficient cannot certify this point",
        },
        "generic_four_moment_reserve_counterexample": {
            "support_X": [fraction_text(value) for value in support],
            "weights": [fraction_text(value) for value in weights],
            "lower_support_for_minus_X": "-2",
            "mean": fraction_text(mean),
            "variance": fraction_text(variance_fixture),
            "K": fraction_text(reserve_k),
            "t": "1/2",
            "exp_minus_half_lower": fraction_text(exp_minus_half_lower),
            "exp_one_lower": fraction_text(exp_one_lower),
            "exp_one_fifth_upper": fraction_text(exp_one_fifth_upper),
            "positive_rational_gap": fraction_text(rational_gap),
            "verdict": "support, four moments, and K>2 Var do not imply the target distribution-free"
        },
    }
    output = args.output.resolve()
    atomic_json(output, payload)
    print(f"Fraction R-115 audit PASS: {total}/{total} exact Bernstein signs positive")
    print(f"exact KS upper margin {fraction_text(upper_margin)} < 0")
    print(f"generic reserve-only rational violation {fraction_text(rational_gap)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

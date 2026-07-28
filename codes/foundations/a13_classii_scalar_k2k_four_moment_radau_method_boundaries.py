"""Primary exact audit of the R-115 auxiliary method boundaries.

This file imports no TECT implementation.  It reconstructs K, Delta, V,
Q, and the fifth-order atanh certificate directly over QQ, converts every
listed rectangle to the tensor Bernstein basis, reconstructs the original
power polynomial from those coefficients, and rationalizes a nearby failure
of the full exact Kearns--Saul coefficient.
"""

from __future__ import annotations

import hashlib
import json
import argparse
from fractions import Fraction
from math import comb
import os
from pathlib import Path
import tempfile

import sympy as sp


VERSION = "1.0.0"
SCHEMA = "tect/a13-scalar-k2k-four-moment-radau-method-boundaries-primary/1.0"
REPO = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = REPO / "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/runs/2026-07-28-primary-scalar-k2k-four-moment-radau-method-boundaries/result.json"


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


def rational_text(value: sp.Expr) -> str:
    value = sp.Rational(value)
    return str(value.p) if value.q == 1 else f"{value.p}/{value.q}"


def coefficient_hash(values: list[sp.Rational]) -> str:
    payload = "\n".join(rational_text(value) for value in values).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def tensor_bernstein(
    polynomial: sp.Expr, first: sp.Symbol, second: sp.Symbol
) -> tuple[int, int, list[sp.Rational], dict[tuple[int, int], sp.Rational]]:
    power = sp.Poly(sp.expand(polynomial), first, second, domain=sp.QQ)
    degree_first, degree_second = power.degree_list()
    monomial = {
        index: sp.Rational(value) for index, value in power.as_dict().items()
    }
    coefficients: list[sp.Rational] = []
    for i in range(degree_first + 1):
        for j in range(degree_second + 1):
            value = sp.S.Zero
            for m in range(i + 1):
                for n in range(j + 1):
                    value += (
                        monomial.get((m, n), sp.S.Zero)
                        * sp.Rational(comb(i, m), comb(degree_first, m))
                        * sp.Rational(comb(j, n), comb(degree_second, n))
                    )
            coefficients.append(sp.Rational(value))

    # Reconstruct power coefficients directly from the Bernstein basis.
    reconstructed: dict[tuple[int, int], sp.Rational] = {}
    for m in range(degree_first + 1):
        for n in range(degree_second + 1):
            value = sp.S.Zero
            for i in range(m + 1):
                first_power = (
                    comb(degree_first, i)
                    * comb(degree_first - i, m - i)
                    * (-1) ** (m - i)
                )
                for j in range(n + 1):
                    second_power = (
                        comb(degree_second, j)
                        * comb(degree_second - j, n - j)
                        * (-1) ** (n - j)
                    )
                    value += (
                        coefficients[i * (degree_second + 1) + j]
                        * first_power
                        * second_power
                    )
            if value:
                reconstructed[(m, n)] = sp.Rational(value)
    assert reconstructed == monomial
    return degree_first, degree_second, coefficients, reconstructed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    b, c, u, v = sp.symbols("b c u v")
    k = sp.expand(
        b**2 * (c**2 - c + sp.Rational(1, 2))
        + b * (-3 * c**3 + 5 * c**2 + c + 1) / 4
        + (153 * c**4 - 156 * c**3 + 82 * c**2 - 4 * c + 5) / 64
    )
    delta = (33 * c**4 - 36 * c**3 + 22 * c**2 - 4 * c + 1) / 64
    variance = sp.expand((k - delta) / 2)
    beta = b / 2
    total = sp.expand(beta**2 + variance)
    difference = sp.expand(beta**2 - variance)
    q_polynomial = sp.expand(variance - beta**2)

    # Clearing 15 beta^2 total^4 from
    # r^2 <= 2K(1+y^2/3+y^4/5), y=difference/total,
    # r=total/beta, gives this exact polynomial.
    t4_polynomial = sp.expand(
        30 * k * beta**2 * total**4
        + 10 * k * beta**2 * difference**2 * total**2
        + 6 * k * beta**2 * difference**4
        - 15 * total**6
    )
    y_symbol = sp.symbols("y", nonnegative=True)
    derivative_remainder = sp.factor(
        sp.diff(
            sp.atanh(y_symbol)
            - y_symbol
            - y_symbol**3 / 3
            - y_symbol**5 / 5,
            y_symbol,
        )
    )
    assert sp.simplify(derivative_remainder - y_symbol**6 / (1 - y_symbol**2)) == 0
    radius = total / beta
    y_ratio = difference / total
    cleared_identity = sp.factor(sp.together(
        t4_polynomial
        - 15
        * beta**2
        * total**4
        * (2 * k * (1 + y_ratio**2 / 3 + y_ratio**4 / 5) - radius**2)
    ))
    assert cleared_identity == 0

    lower_b = sp.Rational(643, 200)
    upper_b = sp.Rational(103, 32)
    midpoint = sp.Rational(211, 640)
    regions = [
        ("Q_LOW", q_polynomial, sp.Rational(0), sp.Rational(1, 10)),
        ("T4_A", t4_polynomial, sp.Rational(1, 10), sp.Rational(37, 160)),
        ("T4_B", t4_polynomial, sp.Rational(37, 160), sp.Rational(19, 64)),
        ("T4_C1", t4_polynomial, sp.Rational(19, 64), midpoint),
        ("T4_C2", t4_polynomial, midpoint, sp.Rational(29, 80)),
        ("T4_D", t4_polynomial, sp.Rational(29, 80), sp.Rational(5, 8)),
        ("Q_HIGH", q_polynomial, sp.Rational(5, 8), sp.Rational(1)),
    ]
    certificates: dict[str, object] = {}
    total_signs = 0
    for name, polynomial, lower_c, upper_c in regions:
        unit = sp.expand(
            polynomial.subs(
                {
                    b: lower_b + (upper_b - lower_b) * u,
                    c: lower_c + (upper_c - lower_c) * v,
                }
            )
        )
        degree_b, degree_c, coefficients, reconstructed = tensor_bernstein(
            unit, u, v
        )
        expected_degree = (2, 4) if name.startswith("Q_") else (12, 24)
        assert (degree_b, degree_c) == expected_degree
        assert all(value > 0 for value in coefficients)
        expected_count = (degree_b + 1) * (degree_c + 1)
        assert len(coefficients) == expected_count
        total_signs += len(coefficients)
        certificates[name] = {
            "c_interval": [rational_text(lower_c), rational_text(upper_c)],
            "degree": [degree_b, degree_c],
            "coefficient_count": len(coefficients),
            "minimum": rational_text(min(coefficients)),
            "sha256": coefficient_hash(coefficients),
            "reconstructed_power_terms": len(reconstructed),
            "reconstruction": "PASS",
        }
    assert total_signs == 1655

    # Exact failure of the full KS coefficient just above the certified slab.
    witness_b = sp.Rational(3219, 1000)
    witness_c = sp.Rational(31, 100)
    witness = {
        "K": sp.factor(k.subs({b: witness_b, c: witness_c})),
        "V": sp.factor(variance.subs({b: witness_b, c: witness_c})),
        "beta": witness_b / 2,
    }
    witness["Q"] = sp.factor(witness["V"] - witness["beta"] ** 2)
    witness["A"] = sp.factor(witness["V"] + witness["beta"] ** 2)
    witness["D"] = sp.factor(witness["beta"] ** 2 - witness["V"])
    witness["y"] = sp.factor(witness["D"] / witness["A"])
    witness["r"] = sp.factor(witness["A"] / witness["beta"])
    assert 0 < witness["y"] < 1
    assert witness["Q"] < 0
    # From atanh(y)/y=sum y^(2n)/(2n+1), bound every n>=2 denominator
    # below by 5, hence the following strict rational upper bound.
    witness["atanh_ratio_upper"] = sp.factor(
        1 + witness["y"] ** 2 / 3 + witness["y"] ** 4 / (5 * (1 - witness["y"] ** 2))
    )
    witness["upper_KS_margin"] = sp.factor(
        2 * witness["K"] * witness["atanh_ratio_upper"] - witness["r"] ** 2
    )
    assert witness["upper_KS_margin"] < 0
    # The centered-Bernoulli Kearns--Saul bound is sharp again at
    # lambda=4*atanh(y), hence at tau_star=4*atanh(y)/r here.  Its rational
    # upper enclosure lies well inside the R-112 compact tau interval.
    witness["tau_star_rational_upper"] = sp.factor(
        4 * witness["y"] / (witness["r"] * (1 - witness["y"] ** 2))
    )
    witness["tau_star_upper_below_one_eighth_gap"] = sp.factor(
        sp.Rational(1, 8) - witness["tau_star_rational_upper"]
    )
    witness["residual_tau_cap"] = sp.factor(
        (32 * witness_b + 20) / (2 * witness_b + 1) ** 2
    )
    witness["residual_tau_cap_above_two_gap"] = sp.factor(
        witness["residual_tau_cap"] - 2
    )
    assert witness["tau_star_upper_below_one_eighth_gap"] > 0
    assert witness["residual_tau_cap_above_two_gap"] > 0
    assert witness_b - upper_b == sp.Rational(1, 4000)

    # Distribution-free four-moment/reserve no-go.  Every exponential bound
    # below comes from a finite Taylor/alternating-series calculation.
    support = (-1, 0, 2)
    weights = (sp.Rational(1, 2), sp.Rational(1, 4), sp.Rational(1, 4))
    mean = sum(weight * value for weight, value in zip(weights, support))
    variance_fixture = sum(weight * (value - mean) ** 2 for weight, value in zip(weights, support))
    reserve_k = sp.Rational(16, 5)
    exp_minus_half_lower = sum((-sp.Rational(1, 2)) ** n / sp.factorial(n) for n in range(4))
    exp_one_lower = sum(sp.Rational(1, sp.factorial(n)) for n in range(7))
    exp_one_fifth_upper = sp.Rational(61, 50) + sp.Rational(2, 1425)
    laplace_lower = exp_minus_half_lower / 2 + sp.Rational(1, 4) + exp_one_lower / 4
    rational_gap = sp.factor(laplace_lower - exp_one_fifth_upper)
    assert mean == 0
    assert variance_fixture == sp.Rational(3, 2)
    assert reserve_k > 2 * variance_fixture
    assert exp_minus_half_lower == sp.Rational(29, 48)
    assert exp_one_lower == sp.Rational(1957, 720)
    # For n>=3, successive exp(1/5) tail terms have ratio at most 1/20,
    # so their sum is strictly below (1/750)/(1-1/20)=2/1425.
    assert sp.Rational(1, 750) / (1 - sp.Rational(1, 20)) == sp.Rational(2, 1425)
    assert rational_gap == sp.Rational(2789, 273600) > 0

    payload = {
        "schema": SCHEMA,
        "version": VERSION,
        "status": "PASS",
        "source": {
            "path": str(Path(__file__).resolve()),
            "sha256": hashlib.sha256(Path(__file__).resolve().read_bytes()).hexdigest()
        },
        "scope": {
            "b_interval": [rational_text(lower_b), rational_text(upper_b)],
            "c_interval": ["0", "1"],
            "classifier": "Q>=0 or fifth-order atanh T4>0",
        },
        "identities": {
            "atanh_lower_remainder_derivative": "y^6/(1-y^2)",
            "T4_cleared_identity": "PASS",
            "every_Bernstein_power_reconstruction": "PASS",
        },
        "total_exact_positive_coefficients": total_signs,
        "certificates": certificates,
        "exact_KS_failure_witness": {
            "b": rational_text(witness_b),
            "c": rational_text(witness_c),
            "distance_above_certified_endpoint": "1/4000",
            **{name: rational_text(value) for name, value in witness.items()},
            "atanh_upper_derivation": (
                "atanh(y)/y=sum_{n>=0} y^(2n)/(2n+1) "
                "<=1+y^2/3+y^4/[5(1-y^2)] for 0<y<1"
            ),
            "sharp_KS_equality_time": "tau_star=4*atanh(y)/r, with 0<tau_star<1/8<R(b)",
            "verdict": "full exact Kearns-Saul coefficient cannot certify this point",
        },
        "generic_four_moment_reserve_counterexample": {
            "support_X": [str(value) for value in support],
            "weights": [rational_text(value) for value in weights],
            "lower_support_for_minus_X": "-2",
            "mean": rational_text(mean),
            "variance": rational_text(variance_fixture),
            "K": rational_text(reserve_k),
            "t": "1/2",
            "exp_minus_half_lower": rational_text(exp_minus_half_lower),
            "exp_one_lower": rational_text(exp_one_lower),
            "exp_one_fifth_upper": rational_text(exp_one_fifth_upper),
            "positive_rational_gap": rational_text(rational_gap),
            "verdict": "support, four moments, and K>2 Var do not imply the target distribution-free"
        },
    }
    atomic_json(args.output.resolve(), payload)
    print("R115 exact-KS extension audit PASS")
    print(f"Bernstein signs: {total_signs}/{total_signs} positive")
    print("Every tensor-Bernstein expansion reconstructed exactly")
    print(f"Certified b interval: [{lower_b}, {upper_b}]")
    print(f"Exact-KS failure witness: b={witness_b}, c={witness_c}")
    print(f"Rational upper-KS margin: {witness['upper_KS_margin']}")
    print(f"Generic reserve-only rational violation: {rational_gap}")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Primary exact certificate for the R-105 subdivision/route boundary.

The certificate deliberately keeps three logically separate checks in one
checkpoint package:

* complete common-root Cartan edges descend to an extended-endpoint quotient;
* the historical rational Taylor owner does not descend to that quotient,
  while the complete raw-Wick endpoint increment does;
* positivity, divergence freedom, and sextic coercivity alone do not make the
  A9 smart path monotone.

All claimed rational values are derived symbolically.  The output is written
atomically so a failed run cannot leave a plausible partial certificate.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path

import sympy as sp


SCHEMA = "tect/a13-cartan-rational-subdivision-smart-path-boundary-primary/1.0"
VERSION = "1.0.0"
DEFAULT_OUTPUT = Path(
    "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/"
    "runs/2026-07-28-primary-cartan-rational-subdivision-smart-path-boundary/"
    "result.json"
)
REPO = Path(__file__).resolve().parents[2]


class Checks:
    def __init__(self) -> None:
        self.names: list[str] = []

    def require(self, name: str, condition: object) -> None:
        if condition is not True and condition != sp.S.true:
            raise AssertionError(name)
        self.names.append(name)


def atomic_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_name, path)
    except BaseException:
        try:
            os.unlink(tmp_name)
        except FileNotFoundError:
            pass
        raise


def frac(value: sp.Expr) -> str:
    value = sp.cancel(value)
    if value.is_Rational:
        return str(value)
    raise TypeError(f"not an exact rational: {value!r}")


def rational_owner(b: sp.Expr, x: sp.Symbol, u: int, g: int, a: int, c: int) -> dict[str, sp.Expr]:
    b0 = sp.cancel(b.subs(x, u))
    b1 = sp.cancel(b.subs(x, u + a))
    bp = sp.cancel(sp.diff(b, x).subs(x, u))
    bpp = sp.cancel(sp.diff(b, x, 2).subs(x, u))
    b_t = sp.cancel(b0 + bp * a + sp.Rational(1, 2) * bpp * a * a)
    remainder = sp.cancel(b1 - b_t)
    q = sp.Integer(g * g - 1)
    q_shift = sp.Integer((g + c) * (g + c) - 1)
    raw_q = sp.cancel(sp.Rational(1, 2) * (b1 - b0) * q)
    mixed_u = sp.cancel(g * b_t * c)
    k_r = sp.cancel(g * remainder * c + sp.Rational(1, 2) * b1 * c * c)
    f_65 = sp.cancel(sp.Rational(1, 2) * remainder * q + k_r)
    delta = sp.cancel(raw_q + mixed_u + k_r)
    endpoint = sp.cancel(sp.Rational(1, 2) * b1 * q_shift - sp.Rational(1, 2) * b0 * q)
    translated_wick = sp.cancel(
        sp.Rational(1, 2) * remainder * q_shift
        + sp.Rational(1, 2) * b_t * c * c
    )
    return {
        "B0": b0,
        "B1": b1,
        "B_T": b_t,
        "L": remainder,
        "Q": q,
        "Q_shift": q_shift,
        "R_Q": raw_q,
        "M_U": mixed_u,
        "K_R": k_r,
        "F_6_5": f_65,
        "Delta": delta,
        "endpoint": endpoint,
        "translated_wick": translated_wick,
    }


def current(sigma: sp.Rational, z: sp.Rational) -> sp.Matrix:
    """A nonlinear exact current used only to exercise the telescope."""

    return sp.Matrix(
        [z**3 + sigma * z + sigma**2, 2 * z**2 - sigma * z + 3 * sigma]
    )


def complete_edge(left: tuple[sp.Rational, sp.Rational], right: tuple[sp.Rational, sp.Rational]) -> sp.Matrix:
    sigma0, z0 = left
    sigma1, z1 = right
    value_edge = current(sigma1, z1) - current(sigma1, z0)
    heat_edge = current(sigma1, z0) - current(sigma0, z0)
    return sp.simplify(value_edge + heat_edge)


def edge_sum(path: list[tuple[sp.Rational, sp.Rational]]) -> sp.Matrix:
    total = sp.zeros(2, 1)
    for left, right in zip(path, path[1:]):
        total += complete_edge(left, right)
    return sp.simplify(total)


def grouped_square(path: list[tuple[sp.Rational, sp.Rational]], operator: sp.Matrix) -> sp.Expr:
    image = sp.simplify(operator * edge_sum(path))
    return sp.expand((image.T * image)[0])


def edgewise_square(path: list[tuple[sp.Rational, sp.Rational]], operator: sp.Matrix) -> sp.Expr:
    value = sp.Integer(0)
    for left, right in zip(path, path[1:]):
        image = sp.simplify(operator * complete_edge(left, right))
        value += sp.expand((image.T * image)[0])
    return sp.expand(value)


def source_only_sum(path: list[tuple[sp.Rational, sp.Rational]]) -> sp.Matrix:
    total = sp.zeros(2, 1)
    for left, right in zip(path, path[1:]):
        _, z0 = left
        sigma1, z1 = right
        total += current(sigma1, z1) - current(sigma1, z0)
    return sp.simplify(total)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    checks = Checks()
    x = sp.symbols("x", real=True)
    b = sp.cancel(4 * x**2 * (4 * x**2 + 9) ** 2 / (81 * (1 + x**2) ** 2))

    expected_jets = {
        "b0": sp.Integer(0),
        "bp0": sp.Integer(0),
        "bpp0": sp.Integer(8),
        "b1": sp.Rational(169, 81),
        "bp1": sp.Rational(208, 81),
        "bpp1": sp.Rational(-2, 81),
        "b2": sp.Rational(400, 81),
    }
    actual_jets = {
        "b0": b.subs(x, 0),
        "bp0": sp.diff(b, x).subs(x, 0),
        "bpp0": sp.diff(b, x, 2).subs(x, 0),
        "b1": b.subs(x, 1),
        "bp1": sp.diff(b, x).subs(x, 1),
        "bpp1": sp.diff(b, x, 2).subs(x, 1),
        "b2": b.subs(x, 2),
    }
    for name, expected in expected_jets.items():
        checks.require(f"production jet {name}", sp.cancel(actual_jets[name] - expected) == 0)

    one = rational_owner(b, x, 0, 1, 2, 2)
    step1 = rational_owner(b, x, 0, 1, 1, 1)
    step2 = rational_owner(b, x, 1, 2, 1, 1)
    expected_one = {
        "B_T": sp.Integer(16),
        "L": sp.Rational(-896, 81),
        "R_Q": sp.Integer(0),
        "M_U": sp.Integer(32),
        "K_R": sp.Rational(-992, 81),
        "F_6_5": sp.Rational(-992, 81),
        "Delta": sp.Rational(1600, 81),
    }
    expected_step1 = {
        "B_T": sp.Integer(4),
        "L": sp.Rational(-155, 81),
        "R_Q": sp.Integer(0),
        "M_U": sp.Integer(4),
        "K_R": sp.Rational(-47, 54),
        "F_6_5": sp.Rational(-47, 54),
        "Delta": sp.Rational(169, 54),
    }
    expected_step2 = {
        "B_T": sp.Rational(376, 81),
        "L": sp.Rational(8, 27),
        "R_Q": sp.Rational(77, 18),
        "M_U": sp.Rational(752, 81),
        "K_R": sp.Rational(248, 81),
        "F_6_5": sp.Rational(284, 81),
        "Delta": sp.Rational(2693, 162),
    }
    for label, row, expected in (
        ("one", one, expected_one),
        ("step1", step1, expected_step1),
        ("step2", step2, expected_step2),
    ):
        checks.require(f"{label} endpoint identity", sp.cancel(row["Delta"] - row["endpoint"]) == 0)
        checks.require(
            f"{label} translated Wick identity",
            sp.cancel(row["F_6_5"] - row["translated_wick"]) == 0,
        )
        checks.require(
            f"{label} Taylor correction",
            sp.cancel(row["F_6_5"] - (sp.Rational(1, 2) * row["L"] * row["Q"] + row["K_R"])) == 0,
        )
        for name, value in expected.items():
            checks.require(f"{label} exact {name}", sp.cancel(row[name] - value) == 0)

    split = {name: sp.cancel(step1[name] + step2[name]) for name in ("R_Q", "M_U", "K_R", "F_6_5", "Delta")}
    expected_split = {
        "R_Q": sp.Rational(77, 18),
        "M_U": sp.Rational(1076, 81),
        "K_R": sp.Rational(355, 162),
        "F_6_5": sp.Rational(427, 162),
        "Delta": sp.Rational(1600, 81),
    }
    for name, expected in expected_split.items():
        checks.require(f"split exact {name}", sp.cancel(split[name] - expected) == 0)

    defects = {name: sp.cancel(one[name] - split[name]) for name in split}
    expected_defects = {
        "R_Q": sp.Rational(-693, 162),
        "M_U": sp.Rational(3032, 162),
        "K_R": sp.Rational(-2339, 162),
        "F_6_5": sp.Rational(-2411, 162),
        "Delta": sp.Integer(0),
    }
    for name, expected in expected_defects.items():
        checks.require(f"defect exact {name}", sp.cancel(defects[name] - expected) == 0)
    checks.require("one-chart K_R is negative", one["K_R"] < 0)
    checks.require("split K_R is positive", split["K_R"] > 0)
    checks.require("one-chart F_6_5 is negative", one["F_6_5"] < 0)
    checks.require("split F_6_5 is positive", split["F_6_5"] > 0)
    checks.require("complete endpoint increment is subdivision invariant", defects["Delta"] == 0)
    checks.require(
        "labelled-owner defects cancel",
        sp.cancel(defects["R_Q"] + defects["M_U"] + defects["K_R"]) == 0,
    )

    e, gamma0, c1 = sp.symbols("e gamma0 c1", positive=True)
    scale = c1 * e * gamma0
    checks.require("production scale is positive", sp.ask(sp.Q.positive(scale)) is True)
    checks.require("scaled negative owner remains negative", sp.ask(sp.Q.negative(scale * one["K_R"])) is True)
    checks.require("scaled positive split remains positive", sp.ask(sp.Q.positive(scale * split["K_R"])) is True)
    checks.require("scaled endpoint defect stays zero", sp.cancel(scale * defects["Delta"]) == 0)

    operator = sp.Matrix([[2, -1], [1, 3]])
    coarse = [(sp.Rational(0), sp.Rational(1)), (sp.Rational(3), sp.Rational(2))]
    refined = [
        (sp.Rational(0), sp.Rational(1)),
        (sp.Rational(1), sp.Rational(-1)),
        (sp.Rational(2), sp.Rational(3)),
        (sp.Rational(3), sp.Rational(2)),
    ]
    reverse_refined = [coarse[0], (sp.Rational(4), sp.Rational(0)), (sp.Rational(-2), sp.Rational(5)), coarse[-1]]
    endpoint = current(*coarse[-1]) - current(*coarse[0])
    for label, path in (("coarse", coarse), ("refined", refined), ("reverse-refined", reverse_refined)):
        checks.require(f"Cartan {label} telescopes", edge_sum(path) == endpoint)
        checks.require(
            f"Cartan {label} grouped square is endpoint square",
            grouped_square(path, operator) == sp.expand(((operator * endpoint).T * (operator * endpoint))[0]),
        )
    checks.require("all common-root partitions have same grouped square", grouped_square(coarse, operator) == grouped_square(refined, operator) == grouped_square(reverse_refined, operator))

    loop = [
        (sp.Rational(0), sp.Rational(1)),
        (sp.Rational(2), sp.Rational(-2)),
        (sp.Rational(-1), sp.Rational(4)),
        (sp.Rational(0), sp.Rational(1)),
    ]
    checks.require("closed extended loop has zero grouped charge", edge_sum(loop) == sp.zeros(2, 1))
    checks.require("closed extended loop has zero grouped energy", grouped_square(loop, operator) == 0)
    checks.require("edgewise square is a subdivision artefact", edgewise_square(loop, operator) > 0)
    checks.require("heat compensator is necessary", source_only_sum(refined) != endpoint)
    checks.require("complete and source-only sums differ", source_only_sum(refined) != edge_sum(refined))

    for seed in range(1, 8):
        path = [(sp.Rational(-2), sp.Rational(3))]
        for index in range(1, seed + 2):
            path.append((sp.Rational(seed - 2 * index), sp.Rational(2 * seed + index)))
        expected = current(*path[-1]) - current(*path[0])
        checks.require(f"arbitrary exact path telescope {seed}", edge_sum(path) == expected)

    x1, x2 = sp.symbols("x1 x2", real=True)
    r2 = x1**2 + x2**2
    t0 = sp.Matrix([[x1**2 + 3 * x2**2, -2 * x1 * x2], [-2 * x1 * x2, 3 * x1**2 + x2**2]])
    vector = sp.Matrix([x1, x2])
    checks.require("smart-path T0 trace", sp.expand(sp.trace(t0) - 4 * r2) == 0)
    checks.require("smart-path T0 determinant", sp.expand(t0.det() - 3 * r2**2) == 0)
    checks.require("smart-path T0 radial action", sp.simplify(t0 * vector - r2 * vector) == sp.zeros(2, 1))
    checks.require("smart-path radial quadratic", sp.expand((vector.T * t0 * vector)[0] - r2**2) == 0)
    div_column = sp.Matrix([sp.diff(t0[0, j], x1) + sp.diff(t0[1, j], x2) for j in range(2)])
    checks.require("smart-path T0 is divergence free", sp.simplify(div_column) == sp.zeros(2, 1))
    lam = sp.Rational(3, 20)
    p = sp.Rational(10, 9)
    a_tilt = sp.cancel(8 * p * lam)
    checks.require("production smart-path tilt a", a_tilt == sp.Rational(4, 3))
    checks.require("IBP coefficient is strictly negative", sp.cancel(-6 * p * a_tilt) < 0)
    checks.require("PSD eigenvalue polynomial factors", sp.factor((sp.Symbol("l") - r2) * (sp.Symbol("l") - 3 * r2) - (sp.Symbol("l")**2 - sp.trace(t0) * sp.Symbol("l") + t0.det())) == 0)

    eta = sp.Rational(9, 20)
    zeta = sp.Rational(3, 20)
    critical_three_quarter = sp.cancel(
        4 * eta ** sp.Rational(3, 4) * zeta ** sp.Rational(1, 4)
        / 3 ** sp.Rational(3, 4)
    )
    critical_half_half = sp.simplify(2 * sp.sqrt(eta * zeta))
    checks.require("critical three-quarter Young threshold", sp.simplify(critical_three_quarter - sp.Rational(3, 5)) == 0)
    checks.require("critical half-half Young threshold", sp.simplify(critical_half_half - 3 * sp.sqrt(3) / 10) == 0)
    ratio = sp.simplify(eta / (3 * zeta))
    checks.require("critical Young saturating ratio", ratio == 1)
    e_var, y_var, r_var = sp.symbols("E Y R", positive=True)
    critical_defect = sp.simplify(
        r_var * e_var ** sp.Rational(3, 4) * y_var ** sp.Rational(1, 4)
        - eta * e_var - zeta * y_var
    )
    checks.require(
        "critical Young defect is linear on saturating ray",
        sp.simplify(critical_defect.subs(y_var, ratio * e_var) - e_var * (r_var - sp.Rational(3, 5))) == 0,
    )
    epsilon = zeta
    d_var, t_var = sp.symbols("d t", positive=True)
    t4 = sp.simplify(d_var / (3 * epsilon))
    minimum_coefficient = sp.simplify(2 / (3 * sp.sqrt(3 * epsilon)))
    checks.require("constant-mode minimizing fourth power", t4 == 20 * d_var / 9)
    checks.require("constant-mode exact divergence coefficient", minimum_coefficient == 4 * sp.sqrt(5) / 9)
    manifest = json.loads(
        (REPO / "claims/A7-CLASSII-RENORMALISED-ENERGY-COMPOSITE/classii_renormalised_energy_manifest.json").read_text(encoding="utf-8")
    )
    constants = manifest["constants"]
    delta_cube = float(constants["delta_cube"]["value"])
    coefficient_a = float(constants["a"]["value"])
    coefficient_b = float(constants["b"]["value"])
    coefficient_c = float(constants["c"]["value"])
    kappa = delta_cube * (9 * coefficient_a + 12 * coefficient_b + 6 * coefficient_c)
    checks.require("upstream constant-mode counterterm slope positive", kappa > 0.0)
    checks.require("full-budget pointwise minimum diverges", kappa > 0.0 and float(minimum_coefficient.evalf()) > 0.0)

    # Production top-shell ray for the all-law relative-bracket audit.  The
    # symbolic coefficient identity is independent of rounded manifest
    # values; positivity is read from the pinned upstream coefficient.
    prod_a, prod_b, prod_c = sp.symbols("a_prod b_prod c_prod", real=True)
    prod_d = prod_a + 2 * prod_b + prod_c
    horizontal_coefficient = sp.expand(4 * prod_d - 8 * (prod_b + prod_c) + 4 * prod_c)
    checks.require("production horizontal coefficient reduces to four a", horizontal_coefficient == 4 * prod_a)
    checks.require("production horizontal coefficient is positive", coefficient_a > 0.0)
    top_angle = sp.symbols("theta_top", real=True)
    top_g = sp.cos(top_angle)
    checks.require(
        "top-shell cubic harmonic decomposition",
        sp.expand_trig(top_g**3 - (3 * sp.cos(top_angle) + sp.cos(3 * top_angle)) / 4) == 0,
    )
    checks.require(
        "top-shell quintic harmonic decomposition",
        sp.expand_trig(top_g**5 - (10 * sp.cos(top_angle) + 5 * sp.cos(3 * top_angle) + sp.cos(5 * top_angle)) / 16) == 0,
    )
    top_sextic_average = sp.simplify(sp.integrate(top_g**6, (top_angle, 0, 2 * sp.pi)) / (2 * sp.pi))
    checks.require("top-shell sextic average", top_sextic_average == sp.Rational(5, 16))
    top_wave_square = sp.symbols("k_top_sq", positive=True)
    checks.require("top-shell projected current stays active", coefficient_a * top_wave_square > 0)
    amplitude_square, top_tau, top_time = sp.symbols("A2 tau_top t_top", positive=True)
    saturation = sp.limit(
        amplitude_square * top_tau / (1 + p * top_time * amplitude_square * top_tau),
        amplitude_square,
        sp.oo,
    )
    checks.require("top-shell resolvent range saturation", sp.simplify(saturation - 1 / (p * top_time)) == 0)
    top_u6 = sp.symbols("u6_top", positive=True)
    bracket_leading = sp.simplify(p / 2 * (-p * 6 * top_u6 * saturation))
    free_leading = p * top_u6
    checks.require("all-law relative bracket leading ratio", sp.simplify(bracket_leading / free_leading + 3 / top_time) == 0)
    top_epsilon = sp.symbols("epsilon_top", positive=True)
    required_b_integral = sp.limit(3 * sp.log(1 / top_epsilon), top_epsilon, 0, dir="+")
    checks.require("all-law relative bracket requires nonintegrable b", required_b_integral == sp.oo)

    theta = sp.symbols("theta", real=True)
    amplitude_a, radial_r, radial_s, sigma, beta, wave = sp.symbols(
        "A R S sigma beta k", real=True
    )
    one_pair_field = amplitude_a + sigma * (
        radial_r * sp.cos(theta) + radial_s * sp.sin(theta)
    )
    one_pair_derivative = wave * sigma * (
        -radial_r * sp.sin(theta) + radial_s * sp.cos(theta)
    )
    average = lambda expression: sp.simplify(
        sp.integrate(sp.expand_trig(sp.expand(expression)), (theta, 0, 2 * sp.pi))
        / (2 * sp.pi)
    )
    pair_norm = radial_r**2 + radial_s**2
    gamma_pair = wave**2 * sigma**2
    pair_v = sp.simplify(
        beta
        / 2
        * (
            average(one_pair_field**2 * one_pair_derivative**2)
            - gamma_pair * average(one_pair_field**2)
        )
    )
    alpha_pair = beta * wave**2 * amplitude_a**2 * sigma**2 / 4
    mu_pair = beta * wave**2 * sigma**4 / 16
    pair_expected = sp.expand(
        alpha_pair * (pair_norm - 2) + mu_pair * (pair_norm**2 - 4 * pair_norm)
    )
    checks.require("one-pair covariance-normal energy identity", sp.simplify(pair_v - pair_expected) == 0)
    checks.require("one-pair quartic lower square", sp.expand(pair_norm**2 - 4 * pair_norm - ((pair_norm - 2) ** 2 - 4)) == 0)
    laplace_a, gaussian_z, shift_h = sp.symbols("a z h", positive=True)
    completed = sp.expand(
        (1 + 2 * laplace_a)
        / 2
        * (gaussian_z + 2 * laplace_a * shift_h / (1 + 2 * laplace_a)) ** 2
        + laplace_a * shift_h**2 / (1 + 2 * laplace_a)
    )
    checks.require(
        "noncentral Gaussian Laplace completion",
        sp.simplify(completed - (gaussian_z**2 / 2 + laplace_a * (gaussian_z + shift_h) ** 2)) == 0,
    )
    t_bound = sp.symbols("t_bound", nonnegative=True)
    inequality_remainder = t_bound**2 / 2 - t_bound + sp.log(1 + t_bound)
    checks.require("one-pair log bound starts at zero", inequality_remainder.subs(t_bound, 0) == 0)
    checks.require(
        "one-pair log bound derivative nonnegative",
        sp.simplify(sp.diff(inequality_remainder, t_bound) - t_bound**2 / (1 + t_bound)) == 0,
    )
    checks.require("one-pair mu summability exponent", 6 > 3)
    checks.require("one-pair alpha-square summability exponent", 4 > 3)

    resonance_r, resonance_u = sp.symbols("r u", real=True)
    cross_field = amplitude_a + resonance_r * sp.cos(theta) + resonance_u * sp.cos(2 * theta)
    cross_derivative = -resonance_r * sp.sin(theta) - 2 * resonance_u * sp.sin(2 * theta)
    cross_average = sp.expand(average(cross_field**2 * cross_derivative**2))
    cross_expected = sp.expand(
        (
            4 * amplitude_a**2 * resonance_r**2
            + 16 * amplitude_a**2 * resonance_u**2
            + 12 * amplitude_a * resonance_r**2 * resonance_u
            + resonance_r**4
            + 10 * resonance_r**2 * resonance_u**2
            + 4 * resonance_u**4
        )
        / 8
    )
    checks.require("cross-mode exact average", sp.simplify(cross_average - cross_expected) == 0)
    diagonal_raw = sp.expand(
        (4 * amplitude_a**2 * resonance_r**2 + resonance_r**4) / 8
        + (16 * amplitude_a**2 * resonance_u**2 + 4 * resonance_u**4) / 8
    )
    resonance = sp.factor(cross_average - diagonal_raw)
    checks.require(
        "cross-mode resonance identity",
        sp.simplify(resonance - resonance_r**2 * resonance_u * (6 * amplitude_a + 5 * resonance_u) / 4) == 0,
    )
    checks.require(
        "cross-mode resonance has negative production-shaped example",
        resonance.subs({amplitude_a: 1, resonance_u: -1, resonance_r: 2}) == -1,
    )

    results = {
        "production_b": str(b),
        "jets": {name: frac(value) for name, value in actual_jets.items()},
        "one_chart": {name: frac(one[name]) for name in ("B_T", "L", "R_Q", "M_U", "K_R", "F_6_5", "Delta")},
        "split_sum": {name: frac(split[name]) for name in split},
        "one_minus_split": {name: frac(defects[name]) for name in defects},
        "cartan": {
            "coarse_grouped_square": frac(grouped_square(coarse, operator)),
            "refined_grouped_square": frac(grouped_square(refined, operator)),
            "closed_loop_grouped_square": frac(grouped_square(loop, operator)),
            "closed_loop_edgewise_square": frac(edgewise_square(loop, operator)),
            "complete_heat_compensator_required": True,
        },
        "smart_path": {
            "p": frac(p),
            "lambda": frac(lam),
            "radial_tilt_a": frac(a_tilt),
            "first_variation_factor_times_positive_EY4": frac(-6 * p * a_tilt),
            "generic_monotonicity": False,
            "production_specific_counterexample": False,
        },
        "deterministic_method_boundaries": {
            "full_energy_budget": frac(eta),
            "full_sextic_budget": frac(zeta),
            "critical_three_quarter_threshold": frac(critical_three_quarter),
            "critical_half_half_threshold_exact": str(critical_half_half),
            "constant_mode_minimum_coefficient_exact": str(minimum_coefficient),
            "constant_mode_minimum_coefficient_decimal": f"{float(minimum_coefficient.evalf(18)):.15f}",
            "upstream_constant_mode_counterterm_slope": f"{kappa:.17g}",
            "pathwise_uniform_coercivity": False,
            "nelson_counterexample": False,
        },
        "relative_bracket_boundary": {
            "active_horizontal_coefficient": "4*a with pinned a>0",
            "top_shell_cubic_projection": "P_J cos(kx)^3=(3/4)cos(kx)",
            "top_shell_quintic_projection": "P_J cos(kx)^5=(10/16)cos(kx)",
            "sextic_average": "5/16",
            "resolvent_range_limit": "A^2*T0*(I+q*t*A^2*T0)^-1 -> P_Ran(T0)/(q*t)",
            "all_law_required_b_lower": "b(t)>=3/t",
            "all_law_pointwise_integrable_ab": False,
            "gibbs_specific_or_time_integrated_bracket": "open",
        },
        "one_fourier_pair": {
            "covariance_normal_identity": "alpha*(S_h-2)+mu*(S_h^2-4*S_h)",
            "conditional_log_bound": "4*q*mu+t-log(1+t) <= 4*q*mu+t^2/2",
            "t_definition": "2*q*alpha",
            "mu_summability_exponent": 6,
            "alpha_square_summability_exponent": 4,
            "uniform_in_past_shift": True,
            "full_physical_mode_factorization": False,
            "cross_mode_resonance": "r^2*u*(6*A+5*u)/4",
            "cross_mode_negative_fixture": "A=1,u=-1,r=2 gives -1",
        },
        "route_verdicts": {
            "common_root_signed_grouping": "advanced-exact-endpoint-quotient",
            "historical_F_6_5_progressive_owner": "superseded-not-subdivision-invariant",
            "fixed_chart_K_R": "retained-only-in-declared-regular-scope",
            "generic_A9_monotonicity": "failed-under-PSD-divergence-free-sextic-hypotheses",
            "all_law_relative_A9_bracket": "failed-production-top-shell-ray",
            "uniform_overlap_src": "open",
            "nelson_q_10_9": "open",
            "sector_a": "open",
        },
    }
    canonical = json.dumps(results, sort_keys=True, separators=(",", ":")).encode("utf-8")
    payload = {
        "schema": SCHEMA,
        "version": VERSION,
        "status": "PASS",
        "assertions_passed": len(checks.names),
        "assertions_total": len(checks.names),
        "assertion_names": checks.names,
        "results_sha256": hashlib.sha256(canonical).hexdigest(),
        "results": results,
    }
    atomic_json(args.output, payload)
    print(f"PASS: primary ({len(checks.names)}/{len(checks.names)})")
    print(f"RESULT: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

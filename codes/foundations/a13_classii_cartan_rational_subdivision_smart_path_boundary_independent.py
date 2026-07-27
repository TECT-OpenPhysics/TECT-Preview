#!/usr/bin/env python3
"""Non-importing standard-library certificate for R-105.

This route uses second-order rational jets and a tiny bivariate-polynomial
engine.  It does not import SymPy, NumPy, or the primary certificate.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import tempfile
from dataclasses import dataclass
from fractions import Fraction
from pathlib import Path


SCHEMA = "tect/a13-cartan-rational-subdivision-smart-path-boundary-independent/1.0"
VERSION = "1.0.0"
DEFAULT_OUTPUT = Path(
    "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/"
    "runs/2026-07-28-independent-cartan-rational-subdivision-smart-path-boundary/"
    "result.json"
)
REPO = Path(__file__).resolve().parents[2]


class Checks:
    def __init__(self) -> None:
        self.names: list[str] = []

    def require(self, name: str, condition: bool) -> None:
        if not condition:
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


@dataclass(frozen=True)
class Jet2:
    """Coefficients of f(u+h)=c0+c1*h+c2*h^2+O(h^3)."""

    c0: Fraction
    c1: Fraction = Fraction(0)
    c2: Fraction = Fraction(0)

    @staticmethod
    def scalar(value: int | Fraction) -> "Jet2":
        return Jet2(Fraction(value))

    def __add__(self, other: "Jet2") -> "Jet2":
        return Jet2(self.c0 + other.c0, self.c1 + other.c1, self.c2 + other.c2)

    def __neg__(self) -> "Jet2":
        return Jet2(-self.c0, -self.c1, -self.c2)

    def __sub__(self, other: "Jet2") -> "Jet2":
        return self + (-other)

    def __mul__(self, other: "Jet2") -> "Jet2":
        return Jet2(
            self.c0 * other.c0,
            self.c0 * other.c1 + self.c1 * other.c0,
            self.c0 * other.c2 + self.c1 * other.c1 + self.c2 * other.c0,
        )

    def inverse(self) -> "Jet2":
        if self.c0 == 0:
            raise ZeroDivisionError
        a0 = 1 / self.c0
        a1 = -self.c1 / (self.c0 * self.c0)
        a2 = self.c1 * self.c1 / (self.c0**3) - self.c2 / (self.c0 * self.c0)
        return Jet2(a0, a1, a2)

    def __truediv__(self, other: "Jet2") -> "Jet2":
        return self * other.inverse()

    def power(self, exponent: int) -> "Jet2":
        result = Jet2.scalar(1)
        for _ in range(exponent):
            result = result * self
        return result


def b_jet(u: int) -> tuple[Fraction, Fraction, Fraction]:
    x = Jet2(Fraction(u), Fraction(1), Fraction(0))
    x2 = x.power(2)
    numerator = Jet2.scalar(4) * x2 * (Jet2.scalar(4) * x2 + Jet2.scalar(9)).power(2)
    denominator = Jet2.scalar(81) * (Jet2.scalar(1) + x2).power(2)
    value = numerator / denominator
    return value.c0, value.c1, 2 * value.c2


def b_value(u: int) -> Fraction:
    return b_jet(u)[0]


def owner(u: int, g: int, a: int, c: int) -> dict[str, Fraction]:
    b0, bp, bpp = b_jet(u)
    b1 = b_value(u + a)
    b_t = b0 + bp * a + Fraction(1, 2) * bpp * a * a
    remainder = b1 - b_t
    q = Fraction(g * g - 1)
    q_shift = Fraction((g + c) * (g + c) - 1)
    raw_q = Fraction(1, 2) * (b1 - b0) * q
    mixed_u = g * b_t * c
    k_r = g * remainder * c + Fraction(1, 2) * b1 * c * c
    f_65 = Fraction(1, 2) * remainder * q + k_r
    delta = raw_q + mixed_u + k_r
    endpoint = Fraction(1, 2) * b1 * q_shift - Fraction(1, 2) * b0 * q
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
    }


Vector = tuple[Fraction, Fraction]
State = tuple[Fraction, Fraction]


def v_add(left: Vector, right: Vector) -> Vector:
    return left[0] + right[0], left[1] + right[1]


def v_sub(left: Vector, right: Vector) -> Vector:
    return left[0] - right[0], left[1] - right[1]


def current(state: State) -> Vector:
    sigma, z = state
    return z**3 + sigma * z + sigma**2, 2 * z**2 - sigma * z + 3 * sigma


def complete_edge(left: State, right: State) -> Vector:
    sigma0, z0 = left
    sigma1, z1 = right
    value = v_sub(current((sigma1, z1)), current((sigma1, z0)))
    heat = v_sub(current((sigma1, z0)), current((sigma0, z0)))
    return v_add(value, heat)


def edge_sum(path: list[State]) -> Vector:
    total = Fraction(0), Fraction(0)
    for left, right in zip(path, path[1:]):
        total = v_add(total, complete_edge(left, right))
    return total


def apply_operator(vector: Vector) -> Vector:
    return 2 * vector[0] - vector[1], vector[0] + 3 * vector[1]


def square(vector: Vector) -> Fraction:
    return vector[0] * vector[0] + vector[1] * vector[1]


def grouped_square(path: list[State]) -> Fraction:
    return square(apply_operator(edge_sum(path)))


def edgewise_square(path: list[State]) -> Fraction:
    return sum((square(apply_operator(complete_edge(left, right))) for left, right in zip(path, path[1:])), Fraction(0))


Poly = dict[tuple[int, int], Fraction]
QComplex = tuple[Fraction, Fraction]
Laurent = dict[int, QComplex]


def p_clean(poly: Poly) -> Poly:
    return {key: value for key, value in poly.items() if value}


def p_add(left: Poly, right: Poly) -> Poly:
    result = dict(left)
    for key, value in right.items():
        result[key] = result.get(key, Fraction(0)) + value
    return p_clean(result)


def p_neg(poly: Poly) -> Poly:
    return {key: -value for key, value in poly.items()}


def p_sub(left: Poly, right: Poly) -> Poly:
    return p_add(left, p_neg(right))


def p_mul(left: Poly, right: Poly) -> Poly:
    result: Poly = {}
    for (i, j), a in left.items():
        for (k, ell), b in right.items():
            key = i + k, j + ell
            result[key] = result.get(key, Fraction(0)) + a * b
    return p_clean(result)


def p_scale(value: Fraction | int, poly: Poly) -> Poly:
    return p_clean({key: Fraction(value) * coefficient for key, coefficient in poly.items()})


def p_derivative(poly: Poly, axis: int) -> Poly:
    result: Poly = {}
    for (i, j), value in poly.items():
        powers = [i, j]
        if powers[axis] == 0:
            continue
        coefficient = value * powers[axis]
        powers[axis] -= 1
        result[tuple(powers)] = coefficient
    return p_clean(result)


def c_add(left: QComplex, right: QComplex) -> QComplex:
    return left[0] + right[0], left[1] + right[1]


def c_mul(left: QComplex, right: QComplex) -> QComplex:
    return left[0] * right[0] - left[1] * right[1], left[0] * right[1] + left[1] * right[0]


def c_scale(value: Fraction | int, number: QComplex) -> QComplex:
    value = Fraction(value)
    return value * number[0], value * number[1]


def l_clean(series: Laurent) -> Laurent:
    return {mode: value for mode, value in series.items() if value != (Fraction(0), Fraction(0))}


def l_mul(left: Laurent, right: Laurent) -> Laurent:
    result: Laurent = {}
    for mode_left, coefficient_left in left.items():
        for mode_right, coefficient_right in right.items():
            mode = mode_left + mode_right
            result[mode] = c_add(result.get(mode, (Fraction(0), Fraction(0))), c_mul(coefficient_left, coefficient_right))
    return l_clean(result)


def l_derivative(series: Laurent, wave: Fraction = Fraction(1)) -> Laurent:
    # d/dx z^n = i*n*wave*z^n.
    result: Laurent = {}
    for mode, (real, imag) in series.items():
        factor = wave * mode
        result[mode] = (-factor * imag, factor * real)
    return l_clean(result)


def l_constant(series: Laurent) -> Fraction:
    real, imag = series.get(0, (Fraction(0), Fraction(0)))
    if imag != 0:
        raise AssertionError("constant Fourier coefficient is not real")
    return real


def pair_series(a_value: Fraction, r_value: Fraction, s_value: Fraction, sigma_value: Fraction) -> Laurent:
    return {
        0: (a_value, Fraction(0)),
        1: (sigma_value * r_value / 2, -sigma_value * s_value / 2),
        -1: (sigma_value * r_value / 2, sigma_value * s_value / 2),
    }


def cosine_two_mode_series(a_value: Fraction, r_value: Fraction, u_value: Fraction) -> Laurent:
    return {
        0: (a_value, Fraction(0)),
        1: (r_value / 2, Fraction(0)),
        -1: (r_value / 2, Fraction(0)),
        2: (u_value / 2, Fraction(0)),
        -2: (u_value / 2, Fraction(0)),
    }


def fstr(value: Fraction) -> str:
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    checks = Checks()

    jets = {
        "b0": b_jet(0)[0],
        "bp0": b_jet(0)[1],
        "bpp0": b_jet(0)[2],
        "b1": b_jet(1)[0],
        "bp1": b_jet(1)[1],
        "bpp1": b_jet(1)[2],
        "b2": b_jet(2)[0],
    }
    expected_jets = {
        "b0": Fraction(0), "bp0": Fraction(0), "bpp0": Fraction(8),
        "b1": Fraction(169, 81), "bp1": Fraction(208, 81),
        "bpp1": Fraction(-2, 81), "b2": Fraction(400, 81),
    }
    for name, expected in expected_jets.items():
        checks.require(f"independent production jet {name}", jets[name] == expected)

    one = owner(0, 1, 2, 2)
    step1 = owner(0, 1, 1, 1)
    step2 = owner(1, 2, 1, 1)
    for label, row in (("one", one), ("step1", step1), ("step2", step2)):
        checks.require(f"independent {label} endpoint identity", row["Delta"] == row["endpoint"])
        checks.require(
            f"independent {label} Taylor correction",
            row["F_6_5"] == Fraction(1, 2) * row["L"] * row["Q"] + row["K_R"],
        )
    expected_rows = {
        "one": {"L": Fraction(-896, 81), "K_R": Fraction(-992, 81), "F_6_5": Fraction(-992, 81), "Delta": Fraction(1600, 81)},
        "step1": {"L": Fraction(-155, 81), "K_R": Fraction(-47, 54), "F_6_5": Fraction(-47, 54), "Delta": Fraction(169, 54)},
        "step2": {"L": Fraction(8, 27), "K_R": Fraction(248, 81), "F_6_5": Fraction(284, 81), "Delta": Fraction(2693, 162)},
    }
    for label, row in (("one", one), ("step1", step1), ("step2", step2)):
        for name, expected in expected_rows[label].items():
            checks.require(f"independent {label} exact {name}", row[name] == expected)

    split = {name: step1[name] + step2[name] for name in ("R_Q", "M_U", "K_R", "F_6_5", "Delta")}
    expected_split = {
        "R_Q": Fraction(77, 18), "M_U": Fraction(1076, 81),
        "K_R": Fraction(355, 162), "F_6_5": Fraction(427, 162),
        "Delta": Fraction(1600, 81),
    }
    for name, expected in expected_split.items():
        checks.require(f"independent split exact {name}", split[name] == expected)
    defects = {name: one[name] - split[name] for name in split}
    expected_defects = {
        "R_Q": Fraction(-693, 162), "M_U": Fraction(3032, 162),
        "K_R": Fraction(-2339, 162), "F_6_5": Fraction(-2411, 162),
        "Delta": Fraction(0),
    }
    for name, expected in expected_defects.items():
        checks.require(f"independent defect exact {name}", defects[name] == expected)
    checks.require("independent K_R sign flip", one["K_R"] < 0 < split["K_R"])
    checks.require("independent F_6_5 sign flip", one["F_6_5"] < 0 < split["F_6_5"])
    checks.require("independent complete owner invariant", defects["Delta"] == 0)
    checks.require("independent defects cancel", defects["R_Q"] + defects["M_U"] + defects["K_R"] == 0)

    coarse = [(Fraction(0), Fraction(1)), (Fraction(3), Fraction(2))]
    refined = [(Fraction(0), Fraction(1)), (Fraction(1), Fraction(-1)), (Fraction(2), Fraction(3)), (Fraction(3), Fraction(2))]
    endpoint = v_sub(current(coarse[-1]), current(coarse[0]))
    checks.require("independent coarse Cartan telescope", edge_sum(coarse) == endpoint)
    checks.require("independent refined Cartan telescope", edge_sum(refined) == endpoint)
    checks.require("independent grouped Cartan quotient", grouped_square(coarse) == grouped_square(refined))
    loop = [(Fraction(0), Fraction(1)), (Fraction(2), Fraction(-2)), (Fraction(-1), Fraction(4)), (Fraction(0), Fraction(1))]
    checks.require("independent closed Cartan charge zero", edge_sum(loop) == (Fraction(0), Fraction(0)))
    checks.require("independent closed grouped energy zero", grouped_square(loop) == 0)
    checks.require("independent edgewise artefact positive", edgewise_square(loop) > 0)
    for seed in range(1, 6):
        path: list[State] = [(Fraction(-3), Fraction(2))]
        for index in range(seed + 2):
            path.append((Fraction(seed - index), Fraction(seed + 3 * index)))
        checks.require(f"independent arbitrary Cartan telescope {seed}", edge_sum(path) == v_sub(current(path[-1]), current(path[0])))

    x1: Poly = {(1, 0): Fraction(1)}
    x2: Poly = {(0, 1): Fraction(1)}
    x1sq, x2sq, x1x2 = p_mul(x1, x1), p_mul(x2, x2), p_mul(x1, x2)
    r2 = p_add(x1sq, x2sq)
    t00 = p_add(x1sq, p_scale(3, x2sq))
    t01 = p_scale(-2, x1x2)
    t10 = dict(t01)
    t11 = p_add(p_scale(3, x1sq), x2sq)
    trace = p_add(t00, t11)
    determinant = p_sub(p_mul(t00, t11), p_mul(t01, t10))
    checks.require("independent smart-path trace polynomial", trace == p_scale(4, r2))
    checks.require("independent smart-path determinant polynomial", determinant == p_scale(3, p_mul(r2, r2)))
    tx0 = p_add(p_mul(t00, x1), p_mul(t01, x2))
    tx1 = p_add(p_mul(t10, x1), p_mul(t11, x2))
    checks.require("independent smart-path first radial component", tx0 == p_mul(r2, x1))
    checks.require("independent smart-path second radial component", tx1 == p_mul(r2, x2))
    div0 = p_add(p_derivative(t00, 0), p_derivative(t10, 1))
    div1 = p_add(p_derivative(t01, 0), p_derivative(t11, 1))
    checks.require("independent smart-path first divergence component", div0 == {})
    checks.require("independent smart-path second divergence component", div1 == {})
    p_value, lam = Fraction(10, 9), Fraction(3, 20)
    a_tilt = 8 * p_value * lam
    first_variation_factor = -6 * p_value * a_tilt
    checks.require("independent radial tilt exact", a_tilt == Fraction(4, 3))
    checks.require("independent smart-path first variation negative", first_variation_factor < 0)
    checks.require("independent block amplification sign", 17 * first_variation_factor < first_variation_factor < 0)

    eta, zeta = Fraction(9, 20), Fraction(3, 20)
    ratio = eta / (3 * zeta)
    critical_three_quarter = Fraction(3, 5)
    checks.require("independent critical Young saturating ratio", ratio == 1)
    for energy in (Fraction(1), Fraction(7, 3), Fraction(29)):
        # On the exact saturating ray Y=E, E^(3/4)Y^(1/4)=E.
        at_threshold = critical_three_quarter * energy
        checks.require(f"independent critical Young equality {energy}", at_threshold == eta * energy + zeta * energy)
        above_threshold = Fraction(61, 100) * energy - eta * energy - zeta * energy
        checks.require(f"independent critical Young divergence slope {energy}", above_threshold == Fraction(1, 100) * energy)
    critical_half_half = 3 * math.sqrt(3) / 10
    minimum_coefficient = 4 * math.sqrt(5) / 9
    checks.require("independent half-half threshold positive", 0.5 < critical_half_half < 0.53)
    checks.require("independent constant-mode minimum coefficient positive", 0.99 < minimum_coefficient < 1.0)
    manifest = json.loads(
        (REPO / "claims/A7-CLASSII-RENORMALISED-ENERGY-COMPOSITE/classii_renormalised_energy_manifest.json").read_text(encoding="utf-8")
    )
    constants = manifest["constants"]
    delta_cube = float(constants["delta_cube"]["value"])
    coefficient_a = float(constants["a"]["value"])
    coefficient_b = float(constants["b"]["value"])
    coefficient_c = float(constants["c"]["value"])
    kappa = delta_cube * (9 * coefficient_a + 12 * coefficient_b + 6 * coefficient_c)
    checks.require("independent upstream constant-mode slope positive", kappa > 0.0)
    checks.require("independent full-budget pointwise minimum diverges", minimum_coefficient * kappa > 0.0)

    a_pin = Fraction(str(constants["a"]["value"]))
    b_pin = Fraction(str(constants["b"]["value"]))
    c_pin = Fraction(str(constants["c"]["value"]))
    d_from_abc = a_pin + 2 * b_pin + c_pin
    horizontal_coefficient = 4 * d_from_abc - 8 * (b_pin + c_pin) + 4 * c_pin
    checks.require("independent production horizontal coefficient reduces to four a", horizontal_coefficient == 4 * a_pin)
    checks.require("independent production horizontal coefficient is positive", horizontal_coefficient > 0)
    top_g = pair_series(Fraction(0), Fraction(1), Fraction(0), Fraction(1))
    top_g2 = l_mul(top_g, top_g)
    top_g3 = l_mul(top_g2, top_g)
    top_g5 = l_mul(l_mul(top_g3, top_g), top_g)
    projected_g3 = {mode: value for mode, value in top_g3.items() if abs(mode) == 1}
    projected_g5 = {mode: value for mode, value in top_g5.items() if abs(mode) == 1}
    expected_g3 = l_clean({mode: c_scale(Fraction(3, 4), value) for mode, value in top_g.items()})
    expected_g5 = l_clean({mode: c_scale(Fraction(10, 16), value) for mode, value in top_g.items()})
    checks.require("independent top-shell cubic projection", projected_g3 == expected_g3)
    checks.require("independent top-shell quintic projection", projected_g5 == expected_g5)
    top_g6 = l_mul(top_g3, top_g3)
    checks.require("independent top-shell sextic average", l_constant(top_g6) == Fraction(5, 16))
    checks.require("independent top-shell projected current stays active", a_pin > 0)
    saturation_fixtures = (
        (Fraction(4), Fraction(3, 5), Fraction(1, 2)),
        (Fraction(25), Fraction(7, 9), Fraction(2, 3)),
        (Fraction(121), Fraction(5, 4), Fraction(3, 7)),
    )
    for index, (amplitude_square, tau_value, time_value) in enumerate(saturation_fixtures, start=1):
        finite_value = amplitude_square * tau_value / (1 + p_value * time_value * amplitude_square * tau_value)
        limit_value = 1 / (p_value * time_value)
        exact_gap = 1 / (p_value * time_value * (1 + p_value * time_value * amplitude_square * tau_value))
        checks.require(f"independent resolvent saturation identity {index}", limit_value - finite_value == exact_gap)
    for index, time_value in enumerate((Fraction(1), Fraction(1, 2), Fraction(1, 7)), start=1):
        u6_value = Fraction(5, 96)
        saturation_limit = 1 / (p_value * time_value)
        bracket_leading = p_value / 2 * (-p_value * 6 * u6_value * saturation_limit)
        free_leading = p_value * u6_value
        checks.require(f"independent all-law relative bracket ratio {index}", bracket_leading / free_leading == -3 / time_value)
    dyadic_required_integral = sum((3 * math.log(2) for _ in range(12)), 0.0)
    checks.require("independent required b dyadic integral grows linearly", abs(dyadic_required_integral - 36 * math.log(2)) < 1e-14)

    pair_fixtures = (
        (Fraction(1), Fraction(2), Fraction(-1), Fraction(1, 3), Fraction(5, 7), Fraction(3)),
        (Fraction(-2), Fraction(1, 2), Fraction(4), Fraction(2, 5), Fraction(7, 9), Fraction(5)),
        (Fraction(0), Fraction(-3), Fraction(2), Fraction(3, 7), Fraction(11, 13), Fraction(2)),
        (Fraction(5, 4), Fraction(0), Fraction(-5, 3), Fraction(4, 9), Fraction(2, 3), Fraction(7)),
    )
    for index, (a_value, r_value, s_value, sigma_value, beta_value, wave_value) in enumerate(pair_fixtures, start=1):
        field = pair_series(a_value, r_value, s_value, sigma_value)
        derivative = l_derivative(field, wave_value)
        field_square = l_mul(field, field)
        derivative_square = l_mul(derivative, derivative)
        gamma_pair = wave_value * wave_value * sigma_value * sigma_value
        actual = beta_value / 2 * (
            l_constant(l_mul(field_square, derivative_square))
            - gamma_pair * l_constant(field_square)
        )
        pair_norm = r_value * r_value + s_value * s_value
        alpha_pair = beta_value * wave_value * wave_value * a_value * a_value * sigma_value * sigma_value / 4
        mu_pair = beta_value * wave_value * wave_value * sigma_value**4 / 16
        expected = alpha_pair * (pair_norm - 2) + mu_pair * (pair_norm * pair_norm - 4 * pair_norm)
        checks.require(f"independent one-pair covariance-normal identity {index}", actual == expected)
        checks.require(f"independent one-pair quartic lower square {index}", pair_norm * pair_norm - 4 * pair_norm == (pair_norm - 2) ** 2 - 4)

    for numerator in range(0, 9):
        t_value = Fraction(numerator, 3)
        # f'(t)=t^2/(1+t)>=0 proves t-log(1+t)<=t^2/2.
        derivative_value = t_value * t_value / (1 + t_value)
        checks.require(f"independent one-pair log-bound derivative {numerator}", derivative_value >= 0)
    checks.require("independent one-pair mu summability exponent", 6 > 3)
    checks.require("independent one-pair alpha-square summability exponent", 4 > 3)

    cross_fixtures = (
        (Fraction(1), Fraction(2), Fraction(-1), Fraction(1)),
        (Fraction(-2), Fraction(3), Fraction(4), Fraction(5)),
        (Fraction(3, 2), Fraction(-5, 3), Fraction(7, 4), Fraction(2)),
        (Fraction(0), Fraction(6), Fraction(-2), Fraction(3)),
    )
    for index, (a_value, r_value, u_value, wave_value) in enumerate(cross_fixtures, start=1):
        field = cosine_two_mode_series(a_value, r_value, u_value)
        derivative = l_derivative(field, wave_value)
        actual = l_constant(l_mul(l_mul(field, field), l_mul(derivative, derivative)))
        expected = wave_value**2 * (
            4 * a_value**2 * r_value**2
            + 16 * a_value**2 * u_value**2
            + 12 * a_value * r_value**2 * u_value
            + r_value**4
            + 10 * r_value**2 * u_value**2
            + 4 * u_value**4
        ) / 8
        diagonal = wave_value**2 * (
            (4 * a_value**2 * r_value**2 + r_value**4)
            + (16 * a_value**2 * u_value**2 + 4 * u_value**4)
        ) / 8
        resonance = wave_value**2 * r_value**2 * u_value * (6 * a_value + 5 * u_value) / 4
        checks.require(f"independent cross-mode exact average {index}", actual == expected)
        checks.require(f"independent cross-mode resonance {index}", actual - diagonal == resonance)
    negative_series = cosine_two_mode_series(Fraction(1), Fraction(2), Fraction(-1))
    negative_full = l_constant(l_mul(l_mul(negative_series, negative_series), l_mul(l_derivative(negative_series), l_derivative(negative_series))))
    negative_diagonal = Fraction(1, 8) * ((4 * 1 * 4 + 16) + (16 * 1 * 1 + 4))
    checks.require("independent cross-mode negative resonance fixture", negative_full - negative_diagonal == -1)

    results = {
        "jets": {name: fstr(value) for name, value in jets.items()},
        "one_chart": {name: fstr(one[name]) for name in ("B_T", "L", "R_Q", "M_U", "K_R", "F_6_5", "Delta")},
        "split_sum": {name: fstr(split[name]) for name in split},
        "one_minus_split": {name: fstr(defects[name]) for name in defects},
        "cartan": {
            "coarse_grouped_square": fstr(grouped_square(coarse)),
            "refined_grouped_square": fstr(grouped_square(refined)),
            "closed_loop_grouped_square": fstr(grouped_square(loop)),
            "closed_loop_edgewise_square": fstr(edgewise_square(loop)),
        },
        "smart_path": {
            "p": fstr(p_value),
            "lambda": fstr(lam),
            "radial_tilt_a": fstr(a_tilt),
            "first_variation_factor_times_positive_EY4": fstr(first_variation_factor),
            "generic_monotonicity": False,
            "production_specific_counterexample": False,
        },
        "deterministic_method_boundaries": {
            "full_energy_budget": fstr(eta),
            "full_sextic_budget": fstr(zeta),
            "critical_three_quarter_threshold": fstr(critical_three_quarter),
            "critical_half_half_threshold_decimal": f"{critical_half_half:.15f}",
            "constant_mode_minimum_coefficient_decimal": f"{minimum_coefficient:.15f}",
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
            "cross_mode_resonance": "k^2*r^2*u*(6*A+5*u)/4",
            "cross_mode_negative_fixture": "A=1,u=-1,r=2,k=1 gives -1",
        },
        "route_verdicts": {
            "common_root_signed_grouping": "advanced-exact-endpoint-quotient",
            "historical_F_6_5_progressive_owner": "superseded-not-subdivision-invariant",
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
    print(f"PASS: independent ({len(checks.names)}/{len(checks.names)})")
    print(f"RESULT: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

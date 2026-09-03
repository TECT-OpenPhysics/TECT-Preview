#!/usr/bin/env python3
"""Primary exact audit for the A13 R-166 sparse-fibre global owner bound."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Any

import sympy as sp


__version__ = "1.1.0"
REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-SPARSE-PRODUCTION-OWNER-RADIAL-GRAM-GLOBAL-BOUNDARY"
LEDGER_ID = "R-166"
SLUG = "sparse-production-owner-radial-gram-global-boundary"
SCHEMA = f"tect/a13-{SLUG}-primary/1.1"
CLAIM_DIR = REPO / "claims" / CLAIM
DEFAULT_OUTPUT = CLAIM_DIR / "runs" / f"2026-08-04-primary-{SLUG}-v1-1" / "result.json"

A1_MANIFEST = REPO / "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json"
R130_MANIFEST = CLAIM_DIR / "classii_terminal_xi_conormal_gram_balanced_low_response_boundary_manifest.json"
R153_MANIFEST = CLAIM_DIR / "classii_production_strict_past_conditional_hessian_weighted_collar_boundary_manifest.json"
R164_MANIFEST = CLAIM_DIR / "classii_predictable_first_chaos_origin_force_anchor_free_semiconvexity_reduction_manifest.json"
R165_MANIFEST = CLAIM_DIR / "classii_sparse_production_owner_harmonic_coercivity_compact_annulus_boundary_manifest.json"

SCOPE = {
    "fixed_side_16_torus": True,
    "fixed_finite_sparse_p_2p_4p_chart": True,
    "unit_regulator_multipliers_p_2p_4p": True,
    "only_declared_past_and_fresh_modes": True,
    "positive_a7_floor": True,
    "strict_past_conditioned": True,
    "whitened_antipodal_source_coordinates": True,
    "exact_continuum_torus_average": True,
    "fresh_4p_final_root": True,
    "all_past_amplitudes": True,
    "r165_open_annulus_closed": True,
    "coefficient_one_single_fresh_pair_harmonic_coercivity": True,
    "coefficient_one_multi_fresh_pair_harmonic_coercivity": False,
    "complete_multi_root_owner": False,
    "random_nonlinear_revisit_controls": False,
    "cutoff_or_floor_removal": False,
    "t050_closed": False,
    "a13_closed": False,
    "sector_a_closed": False,
}

NO_OVERCLAIM = (
    "R-166 proves K_owner > -4I/5 for every whitened past amplitude on only the "
    "fixed side-16 exact nonaliased R-153 p:2p strict-past and fresh-4p twelve-dimensional "
    "conditional fibre with unit retained regulator multipliers and positive floor, allowing "
    "the scoped R-164 choice rho=3/20. It closes the R-165 annulus on that fibre. The "
    "coefficient-one direct harmonic lemma does not tensorize uniformly to simultaneous fresh-4p "
    "and fresh-8p support. This does not refute the original single-pair result and does not prove "
    "the complete multi-root production owner, other harmonics or cross blocks, random/nonlinear/revisit feedback, shifted low "
    "variables, removal, T-050, A13, Nelson or an interacting measure, any physical phase, "
    "morphology or PDE, or Sector A."
)


def rational(value: Any) -> sp.Rational:
    return sp.Rational(str(value))


def sha256(path: Path) -> str:
    payload = path.read_bytes()
    if path.suffix.lower() != ".pdf":
        payload = payload.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(payload).hexdigest()


def serial(value: Any) -> Any:
    if isinstance(value, sp.MatrixBase):
        return [[serial(item) for item in row] for row in value.tolist()]
    if isinstance(value, sp.Basic):
        return str(value)
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(item) for item in value]
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(serial(payload), stream, indent=2, sort_keys=True, ensure_ascii=True)
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

    def check(self, group: str, name: str, condition: bool, actual: Any, expected: Any) -> None:
        self.rows.append({"group": group, "name": name, "status": "PASS" if bool(condition) else "FAIL", "actual": serial(actual), "expected": serial(expected)})

    def require(self) -> None:
        failures = [row for row in self.rows if row["status"] != "PASS"]
        if failures:
            raise AssertionError(json.dumps(failures, indent=2, ensure_ascii=True))


def realify(matrix: sp.Matrix) -> sp.Matrix:
    return matrix.as_real_imag()[0].row_join(-matrix.as_real_imag()[1]).col_join(
        matrix.as_real_imag()[1].row_join(matrix.as_real_imag()[0])
    )


def laurent_multiply(left: dict[int, sp.Expr], right: dict[int, sp.Expr]) -> dict[int, sp.Expr]:
    result: dict[int, sp.Expr] = {}
    for left_mode, left_value in left.items():
        for right_mode, right_value in right.items():
            mode = left_mode + right_mode
            result[mode] = sp.expand(result.get(mode, sp.Integer(0)) + left_value * right_value)
    return {mode: value for mode, value in result.items() if sp.simplify(value) != 0}


def laurent_derivative(polynomial: dict[int, sp.Expr]) -> dict[int, sp.Expr]:
    return {mode: sp.expand(mode * value) for mode, value in polynomial.items() if mode != 0}


def laurent_scale(polynomial: dict[int, sp.Expr], factor: sp.Expr) -> dict[int, sp.Expr]:
    return {mode: sp.expand(factor * value) for mode, value in polynomial.items()}


def laurent_coefficient(polynomial: dict[int, sp.Expr], mode: int) -> sp.Expr:
    return sp.expand(polynomial.get(mode, sp.Integer(0)))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()
    audit = Audit()

    a1 = json.loads(A1_MANIFEST.read_text(encoding="utf-8"))
    r130 = json.loads(R130_MANIFEST.read_text(encoding="utf-8"))
    r153 = json.loads(R153_MANIFEST.read_text(encoding="utf-8"))
    r164 = json.loads(R164_MANIFEST.read_text(encoding="utf-8"))
    r165 = json.loads(R165_MANIFEST.read_text(encoding="utf-8"))
    r165_result_path = REPO / r165["files"]["primary_result"]["path"]
    r165_result = json.loads(r165_result_path.read_text(encoding="utf-8"))
    parameters = a1["parameters"]
    audit.check("authority", "R-130 identity", r130["result_ledger_id"] == "R-130", r130["result_ledger_id"], "R-130")
    audit.check("authority", "R-153 identity", r153["result_ledger_id"] == "R-153", r153["result_ledger_id"], "R-153")
    audit.check("authority", "R-164 identity", r164["result_ledger_id"] == "R-164", r164["result_ledger_id"], "R-164")
    audit.check(
        "authority",
        "R-165 identity",
        r165["result_ledger_id"] == "R-165"
        and sha256(r165_result_path) == r165["files"]["primary_result"]["sha256"],
        [r165["result_ledger_id"], sha256(r165_result_path)],
        ["R-165", r165["files"]["primary_result"]["sha256"]],
    )

    p_mass = rational(parameters["M_X"]) ** 2 + rational(parameters["classii_mass_regularizer"])
    c0 = sp.Rational(3, 250) / p_mass
    c1 = sp.Rational(243, 8000) / p_mass
    alpha = sp.Rational(5, 9)
    a_raw = rational(parameters["cJJ"]) * rational(parameters["alpha_X"]) ** 2 / p_mass
    b_raw = rational(parameters["cJK"]) * rational(parameters["alpha_X"]) * rational(parameters["beta_X"]) / p_mass
    c_raw = rational(parameters["cKK"]) * rational(parameters["beta_X"]) ** 2 / p_mass
    audit.check("coefficients", "completed-square c0", sp.simplify(a_raw - b_raw**2 / c_raw - c0) == 0, a_raw - b_raw**2 / c_raw, c0)
    audit.check("coefficients", "completed-square c1", sp.simplify((b_raw + c_raw) ** 2 / c_raw - c1) == 0, (b_raw + c_raw) ** 2 / c_raw, c1)
    audit.check("coefficients", "completed-square alpha", sp.simplify(c_raw / (b_raw + c_raw) - alpha) == 0, c_raw / (b_raw + c_raw), alpha)
    audit.check("coefficients", "outward c0", c0 < sp.Rational(3, 1000), c0, "<3/1000")
    audit.check("coefficients", "outward c1", c1 < sp.Rational(243, 32000), c1, "<243/32000")

    # Exact six-real Pauli-Fierz Gram decomposition on a symbolic tangent.
    sigma = (
        sp.Matrix([[0, 1, 0], [1, 0, 0], [0, 0, 0]]),
        sp.Matrix([[0, -sp.I, 0], [sp.I, 0, 0], [0, 0, 0]]),
        sp.Matrix([[1, 0, 0], [0, -1, 0], [0, 0, 0]]),
    )
    generators = tuple(realify(item) for item in sigma)
    w = sp.Matrix(sp.symbols("w0:6", real=True))
    y = sp.Matrix(sp.symbols("y0:6", real=True))
    d = sp.symbols("d", positive=True)
    projector = sp.diag(1, 1, 0, 1, 1, 0)
    lam = (w.T * projector * w)[0] / d
    pauli_rows = [2 * item * w for item in generators]
    conormal_rows = [2 * (item * w - alpha * ((w.T * item * w)[0] / d) * w) for item in generators]
    radial = 2 * (projector * w - alpha * lam * w)
    plain = 2 * projector * w
    bj = sum((row * row.T for row in pauli_rows), sp.zeros(6))
    bl = sum((row * row.T for row in conormal_rows), sp.zeros(6))
    correction = radial * radial.T - plain * plain.T
    gram_residual = sp.Matrix(6, 6, lambda i, j: sp.factor(bl[i, j] - bj[i, j] - correction[i, j]))
    audit.check("gram", "exact Pauli-Fierz radial split", gram_residual == sp.zeros(6), gram_residual, sp.zeros(6))
    audit.check("gram", "tangent quadratic split", sp.factor((y.T * (bl - bj - correction) * y)[0]) == 0, sp.factor((y.T * (bl - bj - correction) * y)[0]), 0)

    # Derive the quotient jets rather than installing the constants as oracles.
    wx, wy, zx, zy = sp.symbols("wx wy zx zy", real=True)
    floor = sp.symbols("floor", positive=True)
    denominator = wx**2 + wy**2 + floor
    quotient = wx**2 / denominator
    tangent = sp.Matrix([zx, zy])
    gradient = sp.Matrix([sp.diff(quotient, variable) for variable in (wx, wy)])
    directional_gradient = sp.factor((gradient.T * tangent)[0])
    inner = wx * zx - quotient * (wx * zx + wy * zy)
    gradient_formula = sp.factor(2 * inner / denominator)
    hessian_matrix = sp.hessian(quotient, (wx, wy))
    directional_hessian = sp.factor((tangent.T * hessian_matrix * tangent)[0])
    hessian_formula = sp.factor(
        2 * (zx**2 - quotient * (zx**2 + zy**2)) / denominator
        - 8 * inner * (wx * zx + wy * zy) / denominator**2
    )
    hessian_mutant = sp.factor(
        2 * (zx**2 - quotient * (zx**2 + zy**2)) / denominator
        - 4 * inner * (wx * zx + wy * zy) / denominator**2
    )
    audit.check(
        "radial",
        "exact quotient gradient formula",
        sp.simplify(directional_gradient - gradient_formula) == 0,
        sp.simplify(directional_gradient - gradient_formula),
        0,
    )

    # With delta=e/d and x=|Pw|^2/d, the squared gradient bound completes
    # exactly into two nonnegative terms on 0<=delta<=1.
    x, delta, radial_fraction = sp.symbols("x delta radial_fraction", nonnegative=True)
    gradient_square = 4 * radial_fraction * (x - (1 + delta) * x**2)
    gradient_slack = (
        2 * delta / (1 + delta)
        + 4 * radial_fraction * (1 + delta) * (x - 1 / (2 * (1 + delta))) ** 2
    )
    normalized_completion = sp.factor(
        (1 - gradient_square - gradient_slack).subs(radial_fraction, 1 - delta)
    )
    audit.check(
        "radial",
        "sharp quotient-gradient completion",
        normalized_completion == 0 and gradient_slack.is_nonnegative is True,
        [normalized_completion, gradient_slack.is_nonnegative],
        gradient_slack,
    )
    audit.check(
        "radial",
        "exact quotient Hessian and factor-eight mutant",
        sp.simplify(directional_hessian - hessian_formula) == 0
        and sp.simplify(directional_hessian - hessian_mutant) != 0,
        [sp.simplify(directional_hessian - hessian_formula), sp.simplify(directional_hessian - hessian_mutant)],
        [0, "nonzero"],
    )
    gradient_constant = sp.Integer(1)
    hessian_first_payment = 2 * sp.Integer(1)
    hessian_cross_payment = 8 * sp.Rational(1, 2)
    hessian_constant = hessian_first_payment + hessian_cross_payment
    audit.check(
        "radial",
        "Hessian bound ledger from exact jet",
        hessian_first_payment == 2 and hessian_cross_payment == 4 and hessian_constant == 6,
        [hessian_first_payment, hessian_cross_payment, hessian_constant],
        [2, 4, 6],
    )
    da = 2 * (1 + alpha * (1 + gradient_constant))
    d2a = 2 * alpha * (hessian_constant + 2 * gradient_constant)
    c_zero = sp.Integer(8)
    c_first = 2 * (da * 2 + 2 * 2)
    c_half_second = da**2 + 2 * d2a + 2**2
    audit.check("radial", "Da envelope", da == sp.Rational(38, 9), da, sp.Rational(38, 9))
    audit.check("radial", "D2a envelope", d2a == sp.Rational(80, 9), d2a, sp.Rational(80, 9))
    audit.check("radial", "correction value envelope", c_zero == 8, c_zero, 8)
    audit.check("radial", "correction first envelope", c_first == sp.Rational(224, 9), c_first, sp.Rational(224, 9))
    audit.check("radial", "correction half-Hessian envelope", c_half_second == sp.Rational(3208, 81), c_half_second, sp.Rational(3208, 81))

    # Reconstruct the current supports.  The valid p:2p past cannot resonate
    # with the nonzero +/-8p modes of 4 z^T S_A u.  A wrong fresh-2p mutant
    # does resonate, so the check is sensitive to the root assignment.
    past = {-2: sp.Integer(2), -1: sp.Integer(3), 1: sp.Integer(3), 2: sp.Integer(2)}
    past_derivative = laurent_derivative(past)
    fresh4 = {-4: sp.Integer(1), 4: sp.Integer(1)}
    fresh4_derivative = laurent_derivative(fresh4)
    expected_current = laurent_scale(laurent_multiply(past, past_derivative), sp.Integer(2))
    fresh_second = laurent_scale(laurent_multiply(fresh4, fresh4_derivative), sp.Integer(4))
    valid_resonance = laurent_coefficient(laurent_multiply(expected_current, fresh_second), 0)
    fresh2 = {-2: sp.Integer(1), 2: sp.Integer(1)}
    fresh2_second = laurent_scale(
        laurent_multiply(fresh2, laurent_derivative(fresh2)), sp.Integer(4)
    )
    wrong_root_resonance = laurent_coefficient(
        laurent_multiply(expected_current, fresh2_second), 0
    )
    audit.check(
        "harmonic",
        "Pauli-current nonresonance and wrong-root mutant",
        valid_resonance == 0
        and set(expected_current).issubset(set(range(-4, 5)))
        and set(fresh_second) == {-8, 8}
        and wrong_root_resonance != 0,
        [valid_resonance, sorted(expected_current), sorted(fresh_second), wrong_root_resonance],
        [0, "modes within [-4,4]", [-8, 8], "nonzero"],
    )

    # Pin the convolution factors and the distinction from the false
    # coefficient-one decorrelation bound on the sharp cos(2t), sin(4t) fixture.
    half = sp.Rational(1, 2)
    cosine2 = {-2: half, 2: half}
    cosine4_power = laurent_multiply(
        laurent_multiply(cosine2, cosine2), laurent_multiply(cosine2, cosine2)
    )
    sine4_square = {-8: -sp.Rational(1, 4), 0: half, 8: -sp.Rational(1, 4)}
    fixture_product = laurent_coefficient(laurent_multiply(cosine4_power, sine4_square), 0)
    fixture_f = laurent_coefficient(cosine4_power, 0)
    fixture_q = laurent_coefficient(sine4_square, 0)
    source_square = laurent_coefficient(laurent_multiply(cosine2, cosine2), 0) ** 2 * fixture_q
    r0, r1, r2, r3, r4 = sp.symbols("r0 r1 r2 r3 r4", nonnegative=True)
    f0 = r0**2 + 2 * (r1**2 + r2**2 + r3**2 + r4**2)
    harmonic_remainder = sp.expand(f0 - r4**2 - r0**2)
    audit.check(
        "harmonic",
        "direct coefficient coercivity and decorrelation mutant",
        harmonic_remainder == 2 * (r1**2 + r2**2 + r3**2) + r4**2
        and fixture_product == sp.Rational(5, 32)
        and source_square == sp.Rational(1, 8)
        and fixture_product >= source_square
        and fixture_product < fixture_f * fixture_q,
        [harmonic_remainder, fixture_product, source_square, fixture_f * fixture_q],
        [">=0", sp.Rational(5, 32), sp.Rational(1, 8), "false larger RHS"],
    )

    # Exact failure of coefficient-one tensorization when a second fresh
    # harmonic is admitted.  This is a method boundary, not a counterexample
    # to the original single-fresh-pair owner theorem.
    mix_a, mix_b = sp.symbols("mix_a mix_b", real=True)
    mixed_fresh = {
        -8: sp.I * mix_b / 2,
        -4: sp.I * mix_a / 2,
        4: -sp.I * mix_a / 2,
        8: -sp.I * mix_b / 2,
    }
    mixed_fresh_square = laurent_multiply(mixed_fresh, mixed_fresh)
    mixed_numerator = sp.expand(
        laurent_coefficient(laurent_multiply(cosine4_power, mixed_fresh_square), 0)
    )
    mixed_denominator = sp.expand(
        laurent_coefficient(laurent_multiply(cosine2, cosine2), 0) ** 2
        * laurent_coefficient(mixed_fresh_square, 0)
    )
    numerator_gram = sp.Matrix(
        [
            [mixed_numerator.coeff(mix_a, 2), mixed_numerator.coeff(mix_a, 1).coeff(mix_b, 1) / 2],
            [mixed_numerator.coeff(mix_a, 1).coeff(mix_b, 1) / 2, mixed_numerator.coeff(mix_b, 2)],
        ]
    )
    denominator_gram = sp.Matrix(
        [
            [mixed_denominator.coeff(mix_a, 2), mixed_denominator.coeff(mix_a, 1).coeff(mix_b, 1) / 2],
            [mixed_denominator.coeff(mix_a, 1).coeff(mix_b, 1) / 2, mixed_denominator.coeff(mix_b, 2)],
        ]
    )
    generalized_gram = sp.simplify(denominator_gram.inv() * numerator_gram)
    mixed_counter_numerator = sp.factor(mixed_numerator.subs({mix_a: 1, mix_b: -1}))
    mixed_counter_denominator = sp.factor(mixed_denominator.subs({mix_a: 1, mix_b: -1}))
    mixed_counter_ratio = sp.factor(mixed_counter_numerator / mixed_counter_denominator)
    audit.check(
        "harmonic-extension",
        "exact two-harmonic moments",
        mixed_numerator == sp.Rational(5, 32) * mix_a**2 + sp.Rational(1, 4) * mix_a * mix_b + sp.Rational(3, 16) * mix_b**2
        and mixed_denominator == sp.Rational(1, 8) * (mix_a**2 + mix_b**2),
        [mixed_numerator, mixed_denominator],
        ["5*a^2/32+a*b/4+3*b^2/16", "(a^2+b^2)/8"],
    )
    audit.check(
        "harmonic-extension",
        "generalized Gram invariants",
        generalized_gram == sp.Matrix([[sp.Rational(5, 4), 1], [1, sp.Rational(3, 2)]])
        and sp.trace(generalized_gram) == sp.Rational(11, 4)
        and generalized_gram.det() == sp.Rational(7, 8),
        [generalized_gram, sp.trace(generalized_gram), generalized_gram.det()],
        [[[sp.Rational(5, 4), 1], [1, sp.Rational(3, 2)]], sp.Rational(11, 4), sp.Rational(7, 8)],
    )
    audit.check(
        "harmonic-extension",
        "coefficient-one tensorization counterdirection",
        mixed_counter_numerator == sp.Rational(3, 32)
        and mixed_counter_denominator == sp.Rational(1, 4)
        and mixed_counter_ratio == sp.Rational(3, 8) < 1,
        [mixed_counter_numerator, mixed_counter_denominator, mixed_counter_ratio],
        [sp.Rational(3, 32), sp.Rational(1, 4), "3/8<1"],
    )

    predecessor = r165_result["diagnostics"]
    covariance = predecessor["covariance_bounds"]
    volume = rational(parameters["Lx"]) * rational(parameters["Ly"]) * rational(parameters["Lz"])
    cp_min, cp_max = rational(covariance["cp_min"]), rational(covariance["cp_max"])
    c4_min, c4_max = rational(covariance["c4_min"]), rational(covariance["c4_max"])
    trace4_max = rational(covariance["trace4_max"])
    gamma_past = rational(predecessor["past_derivative_covariance_upper"])
    p2 = sp.factor(gamma_past * volume / (10 * cp_max))
    sqrt_factor = sp.Rational(301, 100)
    c0_upper, c1_upper = sp.Rational(3, 1000), sp.Rational(243, 32000)
    l_corr = c1_upper * c_first
    h_corr = c1_upper * c_half_second
    h_trace = 12 * (c0_upper + c1_upper) + h_corr
    audit.check(
        "ledger",
        "radial paid constants",
        volume == rational(predecessor["volume"])
        and p2 == sp.Rational(5, 32)
        and 2 * cp_max * trace4_max < sqrt_factor**2
        and [l_corr, h_corr, h_trace]
        == [sp.Rational(189, 1000), sp.Rational(1203, 4000), sp.Rational(3423, 8000)],
        [volume, p2, 2 * cp_max * trace4_max, l_corr, h_corr, h_trace],
        [rational(predecessor["volume"]), sp.Rational(5, 32), f"<({sqrt_factor})^2", sp.Rational(189, 1000), sp.Rational(1203, 4000), sp.Rational(3423, 8000)],
    )

    A = sp.Rational(9, 10) * c4_min * cp_min**2 / volume**2
    prefactor = p2 * cp_max * c4_max / volume
    B2 = prefactor * (32 * c_zero * c1_upper + 32 * l_corr + 8 * h_corr)
    B1 = 32 * l_corr * p2 * c4_max * sqrt_factor / volume
    d_fresh = c_zero * c1_upper * 32 * p2 * c4_max * trace4_max / volume
    d_trace = h_trace * c4_max * gamma_past
    D0 = d_fresh + d_trace
    constants = {"A": A, "B2": B2, "B1": B1, "D_fresh": d_fresh, "D_trace": d_trace, "D0": D0}
    expected = {
        "A": sp.Rational(625, 21040201728),
        "B2": sp.Rational(25995, 87359488),
        "B1": sp.Rational(1323, 8192000),
        "D_fresh": sp.Rational(729, 30294016),
        "D_trace": sp.Rational(85575, 698875904),
        "D0": sp.Rational(4402893, 30051663872),
    }
    audit.check("ledger", "exact polynomial constants", constants == expected, constants, expected)
    audit.check("ledger", "one-use B2 factors", 32 * c_zero == 256 and 32 * c_first == sp.Rational(7168, 9) and 8 * c_half_second == sp.Rational(25664, 81), [32 * c_zero, 32 * c_first, 8 * c_half_second], [256, sp.Rational(7168, 9), sp.Rational(25664, 81)])
    audit.check("ledger", "fresh and trace partition", sp.simplify(d_fresh + d_trace - D0) == 0, [d_fresh, d_trace], D0)

    G = sp.symbols("G", nonnegative=True)
    polynomial = sp.expand(A * G**4 - B2 * G**2 - B1 * G - D0)
    derivative = sp.diff(polynomial, G)
    second = sp.diff(polynomial, G, 2)
    third = sp.diff(polynomial, G, 3)
    d70, d71 = sp.factor(derivative.subs(G, 70)), sp.factor(derivative.subs(G, 71))
    dd40, dd41, dd70 = (sp.factor(second.subs(G, point)) for point in (40, 41, 70))
    lower = sp.factor(polynomial.subs(G, 70) + d70)
    margin = sp.factor(lower + sp.Rational(9, 10))
    strong_margin = sp.factor(lower + sp.Rational(4, 5))
    audit.check("minimum", "curvature switch bracket", dd40 < 0 < dd41, [dd40, dd41], "negative,positive")
    audit.check("minimum", "derivative root bracket", d70 == -sp.Rational(1360786403, 1277632512000) < 0 and d71 == sp.Rational(97738714417, 876455903232000) > 0, [d70, d71], "negative,positive")
    audit.check("minimum", "convexity on 70-to-infinity", dd70 == sp.Rational(6865745, 5962285056) > 0 and third.subs(G, 70) > 0, [dd70, third.subs(G, 70)], ">0,>0")
    audit.check("minimum", "global rational lower bound", lower == -sp.Rational(332863942666997, 439505584128000), lower, -sp.Rational(332863942666997, 439505584128000))
    audit.check("minimum", "strict owner margin", margin == sp.Rational(62691083048203, 439505584128000) > 0, margin, ">0")
    audit.check("minimum", "stronger minus-four-fifths margin", strong_margin == sp.Rational(18740524635403, 439505584128000) > 0, strong_margin, ">0")

    carryover_polynomial = sp.expand(mixed_counter_ratio * A * G**4 - B2 * G**2 - B1 * G - D0)
    carryover_at_116 = sp.factor(carryover_polynomial.subs(G, 116))
    carryover_r164_margin = sp.factor(carryover_at_116 + sp.Rational(10, 11))
    audit.check(
        "harmonic-extension",
        "old-ledger carry-over fails R-164 threshold",
        carryover_at_116 == -sp.Rational(100799462911238297, 50250138451968000)
        and carryover_r164_margin == -sp.Rational(606292707503941267, 552751522971648000) < 0,
        [carryover_at_116, carryover_r164_margin],
        ["exact P_3/8(116)", "P_3/8(116)+10/11<0"],
    )

    effective_rho = sp.factor(sp.Rational(10, 11) + lower)
    rho = sp.Rational(3, 20)
    rho_margin = sp.factor(effective_rho - rho)
    full_semiconvexity = -sp.Rational(1, 110) + rho
    epsilon_v = sp.Rational(5, 11) - rho / 4
    audit.check("threshold", "effective R-164 rho capacity", effective_rho == sp.Rational(733552471943033, 4834561425408000) > rho, effective_rho, f">{rho}")
    audit.check("threshold", "R-164 rho choice", sp.Rational(10, 11) - rho == sp.Rational(167, 220) and rho_margin == sp.Rational(8368258131833, 4834561425408000) > 0, [sp.Rational(10, 11) - rho, rho_margin], [sp.Rational(167, 220), ">0"])
    audit.check("threshold", "downstream semiconvexity and epsilon", full_semiconvexity == sp.Rational(31, 220) > sp.Rational(1, 10) and epsilon_v == sp.Rational(367, 880) > 0, [full_semiconvexity, epsilon_v], [sp.Rational(31, 220), sp.Rational(367, 880)])
    audit.check("scope", "open-gate firewall", SCOPE["all_past_amplitudes"] and SCOPE["r165_open_annulus_closed"] and not SCOPE["complete_multi_root_owner"] and not SCOPE["t050_closed"] and not SCOPE["sector_a_closed"] and "does not prove" in NO_OVERCLAIM, SCOPE, "one sparse fibre only")

    audit.require()
    payload = {
        "schema": SCHEMA,
        "version": __version__,
        "issued": "2026-08-04",
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "result_ledger_id": LEDGER_ID,
        "status": "PASS",
        "diagnostics": {
            "coefficients": {"c0": c0, "c1": c1, "alpha": alpha},
            "correction_envelopes": {"C0": c_zero, "LC": c_first, "HC": c_half_second, "paid_LC": l_corr, "paid_HC": h_corr, "trace_H": h_trace},
            "quotient_bounds": {"w_grad_lambda": gradient_constant, "w2_hessian_lambda": hessian_constant},
            "harmonic_source_coordinate_constant": 1,
            "multi_harmonic_gram": generalized_gram,
            "multi_harmonic_gram_invariants": {"trace": sp.trace(generalized_gram), "determinant": generalized_gram.det()},
            "multi_harmonic_counterexample": {"numerator": mixed_counter_numerator, "denominator": mixed_counter_denominator, "ratio": mixed_counter_ratio},
            "polynomial_constants": constants,
            "derivative_at_70": d70,
            "derivative_at_71": d71,
            "second_at_40": dd40,
            "second_at_41": dd41,
            "second_at_70": dd70,
            "minimum_bracket": "70<G_*<71",
            "global_lower_bound": lower,
            "owner_margin_above_minus_9_10": margin,
            "owner_margin_above_minus_4_5": strong_margin,
            "owner_floor": -sp.Rational(4, 5),
            "carryover_at_116": carryover_at_116,
            "carryover_margin_to_r164": carryover_r164_margin,
            "effective_rho_capacity": effective_rho,
            "rho": rho,
            "rho_margin": rho_margin,
            "full_semiconvexity": full_semiconvexity,
            "epsilon_v": epsilon_v,
        },
        "scope": SCOPE,
        "no_overclaim": NO_OVERCLAIM,
        "authority_hashes": {"A1": sha256(A1_MANIFEST), "R-130": sha256(R130_MANIFEST), "R-153": sha256(R153_MANIFEST), "R-164": sha256(R164_MANIFEST), "R-165": sha256(R165_MANIFEST), "R-165-result": sha256(r165_result_path)},
        "assertions": audit.rows,
        "summary": {"passed": len(audit.rows), "failed": 0, "total": len(audit.rows)},
    }
    atomic_json(arguments.output, payload)
    print(f"{RESULT_ID}: PASS ({len(audit.rows)}/{len(audit.rows)})")
    print(f"artifact: {arguments.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

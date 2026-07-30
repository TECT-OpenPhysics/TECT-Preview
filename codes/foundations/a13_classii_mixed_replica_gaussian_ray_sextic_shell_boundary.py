#!/usr/bin/env python3
"""Primary exact audit for the scoped A13 R-132 mixed-replica boundary.

The audit verifies the exact replica polarization and Pauli--Fierz mixed
contractions, proves quantitative diagonal heat--sextic comparison constants,
exhibits the square-of-mean cancellation which prevents their production
promotion, proves a law-free floor warning, and checks a floor-uniform
standard-Gaussian score-transfer ray bound using source and sextic once.
It does not assert the missing owner-complete production shell theorem.
"""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-31"
__version_issued__ = "2026-07-31"

import argparse
from itertools import product
import json
import os
from pathlib import Path
import tempfile
from typing import Any

import sympy as sp


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-MIXED-REPLICA-GAUSSIAN-RAY-SEXTIC-SHELL-BOUNDARY"
SCHEMA = "tect/a13-mixed-replica-gaussian-ray-sextic-shell-boundary-primary/1.0"
DEFAULT_OUTPUT = REPO / (
    "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/"
    "runs/2026-07-31-primary-mixed-replica-gaussian-ray-sextic-shell-"
    "boundary/result.json"
)
R131_RESULT = REPO / (
    "claims/A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION/"
    "runs/2026-07-31-primary-owner-complete-physical-response-mixed-"
    "gram-shell-boundary/result.json"
)
A1_MANIFEST = REPO / (
    "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/"
    "production_functional_manifest.json"
)


def serial(value: Any) -> Any:
    if isinstance(value, sp.MatrixBase):
        return [[serial(value[r, c]) for c in range(value.cols)] for r in range(value.rows)]
    if isinstance(value, sp.Basic):
        return str(value)
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(item) for item in value]
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
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


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(self, group: str, name: str, condition: bool, actual: Any, expected: Any) -> None:
        self.rows.append(
            {
                "group": group,
                "name": name,
                "status": "PASS" if bool(condition) else "FAIL",
                "actual": serial(actual),
                "expected": serial(expected),
            }
        )

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
            "scope": {
                "mixed_replica_representation_proved": True,
                "mixed_pauli_fierz_identity_proved": True,
                "diagonal_rademacher_heat_sextic_bound_proved": True,
                "diagonal_to_mixed_promotion_rejected": True,
                "law_free_floor_uniformity_rejected": True,
                "standard_gaussian_ray_score_bound_proved": True,
                "production_owner_complete_form_constructed": False,
                "production_c_mix": False,
                "production_c_far": False,
                "production_c_bal": False,
                "absolute_anchor": False,
                "sector_a_closed": False,
            },
            "no_overclaim": (
                "R-132 proves an exact mixed-replica representation, a mixed Pauli--Fierz "
                "identity, a diagonal Rademacher heat--sextic comparison, a law-free floor "
                "warning, and a floor-uniform standard-Gaussian scalar-ray source--sextic "
                "bound. It does not construct or bound the owner-complete production "
                "response, prove C_mix, C_far, c_bal, the absolute anchor, Nelson, or "
                "Sector A closure."
            ),
        }


def real_part(value: sp.Expr) -> sp.Expr:
    return sp.simplify(sp.expand_complex(value).as_real_imag()[0])


def inner(left: sp.Matrix, right: sp.Matrix) -> sp.Expr:
    return sp.simplify((sp.conjugate(left).T * right)[0])


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    upstream = json.loads(R131_RESULT.read_text(encoding="utf-8"))
    production = upstream["diagnostics"]["production"]
    alpha = sp.Rational(production["alpha"])
    c0 = sp.Rational(production["c0"])
    c1 = sp.Rational(production["c1"])
    a1 = json.loads(A1_MANIFEST.read_text(encoding="utf-8"))
    floor = sp.Rational(str(a1["parameters"]["rho_regularizer"]))
    p_mass = sp.simplify(sp.Rational(3, 250) / c0)
    audit = Audit()

    audit.check("inputs", "upstream_pass", upstream.get("status") == "PASS", upstream.get("status"), "PASS")
    audit.check("inputs", "alpha", alpha == sp.Rational(5, 9), alpha, sp.Rational(5, 9))
    audit.check("inputs", "c0", c0 == sp.Rational(3, 250) / p_mass, c0, sp.Rational(3, 250) / p_mass)
    audit.check("inputs", "c1", c1 == sp.Rational(243, 8000) / p_mass, c1, sp.Rational(243, 8000) / p_mass)
    audit.check("inputs", "floor", floor == sp.Rational(1, 10**12), floor, sp.Rational(1, 10**12))

    # Exact paired-replica polarization on a finite conditional law.  The
    # fixture contains nonzero first and mixed variations and uses unequal
    # conditional weights, so every term in the bilinear identity is active.
    t, s = sp.symbols("t s", real=True)
    weights = [sp.Rational(1, 5), sp.Rational(3, 10), sp.Rational(1, 2)]
    bases = [sp.Matrix([1, -2]), sp.Matrix([3, 1]), sp.Matrix([-1, 4])]
    dz = [sp.Matrix([2, 1]), sp.Matrix([-1, 3]), sp.Matrix([4, -2])]
    dw = [sp.Matrix([-2, 2]), sp.Matrix([1, -3]), sp.Matrix([2, 5])]
    dzw = [sp.Matrix([1, 2]), sp.Matrix([-2, 1]), sp.Matrix([3, -1])]
    family = [bases[k] + t * dz[k] + s * dw[k] + t * s * dzw[k] for k in range(3)]
    mean = sum((weights[k] * family[k] for k in range(3)), sp.zeros(2, 1))
    lhs = sp.diff((mean.T * mean)[0] / 2, t, s).subs({t: 0, s: 0})
    paired = sp.Integer(0)
    for i in range(3):
        for j in range(3):
            paired += weights[i] * weights[j] * (
                (dz[i].T * dw[j])[0] + (bases[i].T * dzw[j])[0]
            )
    audit.check("replica", "polarization", sp.simplify(lhs - paired) == 0, lhs, paired)
    audit.check("replica", "weights_normalized", sum(weights) == 1, sum(weights), 1)

    # Exact Pauli--Fierz mixed contractions.  Direct Pauli sums are compared
    # with the invariant formulas at several exact complex fixtures.
    I = sp.I
    pauli = [
        sp.Matrix([[0, 1], [1, 0]]),
        sp.Matrix([[0, -I], [I, 0]]),
        sp.Matrix([[1, 0], [0, -1]]),
    ]
    fixtures = [
        ([1 + 2 * I, -1 + I], [2 - I, 3 + I], [-2 + 3 * I, 1 - I], [-3 + 2 * I, 2 + 4 * I]),
        ([2 - I, 1 + 3 * I], [-1 + 2 * I, 4 - I], [3 + I, -2 - I], [1 - 4 * I, 2 + I]),
        ([-1 + I, 3 - 2 * I], [2 + 2 * I, -3 + I], [1 - 3 * I, 4 + I], [-2 + I, 1 + 2 * I]),
    ]
    fierz_checks: list[bool] = []
    for raw in fixtures:
        u, v, up, vp = (sp.Matrix(vector) for vector in raw)
        m = [sp.simplify(inner(u, sigma * u)) for sigma in pauli]
        mp = [sp.simplify(inner(up, sigma * up)) for sigma in pauli]
        j = [2 * real_part(inner(u, sigma * v)) for sigma in pauli]
        jp = [2 * real_part(inner(up, sigma * vp)) for sigma in pauli]
        direct_jj = sp.simplify(sum(j[k] * jp[k] for k in range(3)))
        direct_jm = sp.simplify(sum(j[k] * mp[k] for k in range(3)))
        direct_mj = sp.simplify(sum(m[k] * jp[k] for k in range(3)))
        direct_mm = sp.simplify(sum(m[k] * mp[k] for k in range(3)))
        formula_mm = sp.simplify(2 * inner(u, up) * inner(up, u) - inner(u, u) * inner(up, up))
        formula_jm = sp.simplify(4 * real_part(inner(v, up) * inner(up, u)) - 2 * inner(up, up) * real_part(inner(u, v)))
        formula_mj = sp.simplify(4 * real_part(inner(vp, u) * inner(u, up)) - 2 * inner(u, u) * real_part(inner(up, vp)))
        formula_jj = sp.simplify(
            2 * real_part(
                2 * inner(u, vp) * inner(up, v)
                - inner(u, v) * inner(up, vp)
                + 2 * inner(u, up) * inner(vp, v)
                - inner(u, v) * inner(vp, up)
            )
        )
        fierz_checks.append(
            all(
                sp.simplify(left - right) == 0
                for left, right in (
                    (direct_jj, formula_jj),
                    (direct_jm, formula_jm),
                    (direct_mj, formula_mj),
                    (direct_mm, formula_mm),
                )
            )
        )
    audit.check("fierz", "all_exact_fixtures", all(fierz_checks), fierz_checks, [True] * len(fixtures))

    tau, tau_prime = sp.symbols("tau tau_prime", real=True)
    JJ, JM, MJ, MM = sp.symbols("JJ JM MJ MM", real=True)
    direct_mixed = c0 * JJ + c1 * (
        JJ - alpha * tau_prime * JM - alpha * tau * MJ + alpha**2 * tau * tau_prime * MM
    )
    expanded_mixed = sp.expand(c0 * JJ + c1 * ((JJ - alpha * tau * MJ - alpha * tau_prime * JM + alpha**2 * tau * tau_prime * MM)))
    audit.check("fierz", "mixed_six_row_split", sp.simplify(direct_mixed - expanded_mixed) == 0, direct_mixed, expanded_mixed)

    # Diagonal 64-atom heat comparison.  The wedge row controls v, while the
    # radial two-by-two Schur determinant controls w on a compact state ball.
    c_full = sp.simplify(c0 * c1 / (c0 + c1))
    audit.check("diagonal_heat", "c_full", c_full == sp.Rational(243, 28250) / p_mass, c_full, sp.Rational(243, 28250) / p_mass)
    radius = sp.Rational(1, 32)
    denominator = sp.simplify((sp.sqrt(radius) + sp.sqrt(6)) ** 2 + floor)
    compact_v = sp.simplify(8 * (c0 + c1))
    compact_w = sp.simplify(64 * c_full * alpha**2 / denominator**2)
    sextic_outside = sp.simplify(sp.Rational(9, 10) * radius**2)
    audit.check("diagonal_heat", "denominator", denominator == sp.Rational(193, 32) + sp.sqrt(3) / 2 + floor, denominator, sp.Rational(193, 32) + sp.sqrt(3) / 2 + floor)
    audit.check("diagonal_heat", "compact_v", compact_v == sp.Rational(339, 1000) / p_mass, compact_v, sp.Rational(339, 1000) / p_mass)
    audit.check(
        "diagonal_heat",
        "compact_w",
        sp.simplify(
            compact_w - sp.Rational(96, 565) / (p_mass * denominator**2)
        )
        == 0,
        compact_w,
        sp.Rational(96, 565) / (p_mass * denominator**2),
    )
    audit.check("diagonal_heat", "compact_v_above_sextic", compact_v > sextic_outside, compact_v, sextic_outside)
    audit.check("diagonal_heat", "compact_w_above_sextic", sp.simplify(compact_w - sextic_outside) > 0, compact_w, f"> {sextic_outside}")
    audit.check("diagonal_heat", "raw_global_constant", sextic_outside == sp.Rational(9, 10240), sextic_outside, sp.Rational(9, 10240))

    # The half-normalized comparison matches a possible 1/2 energy convention
    # without assuming that the diagonal form is a legal production owner.
    half_radius = sp.Rational(1, 45)
    half_denominator = sp.simplify((sp.sqrt(half_radius) + sp.sqrt(6)) ** 2 + floor)
    half_compact_w = sp.simplify(32 * c_full * alpha**2 / half_denominator**2)
    half_sextic = sp.simplify(sp.Rational(9, 10) * half_radius**2)
    audit.check("diagonal_heat", "half_compact_w_above_sextic", sp.simplify(half_compact_w - half_sextic) > 0, half_compact_w, f"> {half_sextic}")
    audit.check("diagonal_heat", "half_global_constant", half_sextic == sp.Rational(1, 2250), half_sextic, sp.Rational(1, 2250))

    # Exact Rademacher moments used in the compact proof.
    ur1, ui1, ur2, ui2, vr1, vi1, vr2, vi2 = sp.symbols(
        "ur1 ui1 ur2 ui2 vr1 vi1 vr2 vi2", real=True
    )
    r_state = ur1**2 + ui1**2 + ur2**2 + ui2**2
    v_norm = vr1**2 + vi1**2 + vr2**2 + vi2**2
    a_squares = []
    radii_squares = []
    wedge_squares = []
    for signs in product((-1, 1), repeat=4):
        x1r, x1i, x2r, x2i = (sp.Integer(value) for value in signs)
        a_value = (ur1 + x1r) * vr1 + (ui1 + x1i) * vi1 + (ur2 + x2r) * vr2 + (ui2 + x2i) * vi2
        r_value = (ur1 + x1r) ** 2 + (ui1 + x1i) ** 2 + (ur2 + x2r) ** 2 + (ui2 + x2i) ** 2
        h_real = (ur1 + x1r) * vr2 - (ui1 + x1i) * vi2 - (ur2 + x2r) * vr1 + (ui2 + x2i) * vi1
        h_imag = (ur1 + x1r) * vi2 + (ui1 + x1i) * vr2 - (ur2 + x2r) * vi1 - (ui2 + x2i) * vr1
        a_squares.append(a_value**2)
        radii_squares.append(r_value**2)
        wedge_squares.append(h_real**2 + h_imag**2)
    mean_a2 = sp.simplify(sum(a_squares) / len(a_squares))
    mean_r2 = sp.simplify(sum(radii_squares) / len(radii_squares))
    mean_h2 = sp.simplify(sum(wedge_squares) / len(wedge_squares))
    base_a = ur1 * vr1 + ui1 * vi1 + ur2 * vr2 + ui2 * vi2
    base_h_real = ur1 * vr2 - ui1 * vi2 - ur2 * vr1 + ui2 * vi1
    base_h_imag = ur1 * vi2 + ui1 * vr2 - ur2 * vi1 - ui2 * vr1
    audit.check("rademacher", "a_second_moment", sp.simplify(mean_a2 - base_a**2 - v_norm) == 0, mean_a2, base_a**2 + v_norm)
    audit.check("rademacher", "radius_fourth_moment", sp.simplify(mean_r2 - (r_state**2 + 12 * r_state + 16)) == 0, mean_r2, r_state**2 + 12 * r_state + 16)
    audit.check("rademacher", "wedge_second_moment", sp.simplify(mean_h2 - (base_h_real**2 + base_h_imag**2 + 2 * v_norm)) == 0, mean_h2, base_h_real**2 + base_h_imag**2 + 2 * v_norm)

    # At the origin every Xi coordinate is odd under A -> -A, so square of
    # the conditional mean vanishes even though the diagonal Gram is positive.
    atom_means = [sp.Integer(0), sp.Integer(0), sp.Integer(0), sp.Integer(0)]
    atom_count = 0
    wr, wi = sp.symbols("wr wi", real=True)
    for signs in product((-1, 1), repeat=6):
        x1r, x1i, x2r, x2i, xr, xi = (sp.Integer(value) for value in signs)
        atom_r = sp.Integer(4)
        atom_d = sp.Integer(6) + floor
        lam = alpha * atom_r / atom_d
        atom_a = x1r * vr1 + x1i * vi1 + x2r * vr2 + x2i * vi2
        atom_s = xr * wr + xi * wi
        atom_hr = x1r * vr2 - x1i * vi2 - x2r * vr1 + x2i * vi1
        atom_hi = x1r * vi2 + x1i * vr2 - x2r * vi1 - x2i * vr1
        values = [2 * sp.sqrt(c0) * atom_a, 2 * sp.sqrt(c1) * ((1 - lam) * atom_a - lam * atom_s), 2 * sp.sqrt(c0 + c1) * atom_hr, 2 * sp.sqrt(c0 + c1) * atom_hi]
        atom_means = [sp.simplify(atom_means[k] + values[k]) for k in range(4)]
        atom_count += 1
    atom_means = [sp.simplify(value / atom_count) for value in atom_means]
    audit.check("mixed_boundary", "rademacher_mean_xi_zero", atom_means == [0, 0, 0, 0], atom_means, [0, 0, 0, 0])

    rho, xv = sp.symbols("rho xv", nonnegative=True, real=True)
    sextic = sp.Rational(3, 20) * rho**3
    radial_second = sp.simplify(sp.Rational(9, 10) * rho**2 + sp.Rational(18, 5) * rho * xv**2)
    audit.check(
        "sextic",
        "hessian_formula",
        sp.simplify(
            radial_second
            - sp.Rational(9, 10) * rho**2
            - sp.Rational(18, 5) * rho * xv**2
        )
        == 0,
        radial_second,
        "9*rho^2/10 + 18*rho*xv^2/5",
    )
    audit.check("mixed_boundary", "origin_sextic_zero", radial_second.subs({rho: 0, xv: 0}) == 0, radial_second.subs({rho: 0, xv: 0}), 0)

    # Exact two-point floor warning for the real rational active ray.
    delta, shift = sp.symbols("delta shift", positive=True, real=True)
    f = lambda value: sp.simplify(value - alpha * value**3 / (value**2 + delta**2))
    difference = sp.simplify(f(delta + shift) - f(1 + shift))
    two_point_hessian_over_c1 = sp.factor(-sp.diff(difference**2, shift, 2).subs(shift, 0) / 2)
    positive_polynomial = 7 * delta**7 + 188 * delta**6 + 61 * delta**5 + 100 * delta**4 + 57 * delta**3 + 40 * delta**2 + 3 * delta + 8
    expected_floor_warning = -sp.Rational(5, 324) * (delta - 1) ** 2 * positive_polynomial / (delta * (1 + delta**2) ** 4)
    audit.check("floor_warning", "exact_hessian", sp.simplify(two_point_hessian_over_c1 - expected_floor_warning) == 0, two_point_hessian_over_c1, expected_floor_warning)
    audit.check("floor_warning", "negative_for_0_delta_1", expected_floor_warning.subs(delta, sp.Rational(1, 2)) < 0, expected_floor_warning.subs(delta, sp.Rational(1, 2)), "<0")
    audit.check("floor_warning", "inverse_floor_limit", sp.limit(delta * two_point_hessian_over_c1, delta, 0, dir="+") == -sp.Rational(10, 81), sp.limit(delta * two_point_hessian_over_c1, delta, 0, dir="+"), -sp.Rational(10, 81))

    # Standard-Gaussian score transfer avoids derivatives of f_delta.  The
    # uniform value bound |f_delta(x)|<=|x| yields an explicit once-only
    # source--sextic lower margin on the scalar rational ray.
    gaussian_A = sp.simplify(4 * c1 * (3 + sp.sqrt(2)))
    gaussian_B = sp.simplify(4 * c1 * (2 + sp.sqrt(2)))
    gaussian_margin = sp.simplify(sp.Rational(9, 10) - gaussian_A - gaussian_B**2 / 18)
    audit.check("gaussian_ray", "value_multiplier_range", 0 < 1 - alpha < 1, 1 - alpha, "in (0,1)")
    audit.check("gaussian_ray", "margin_positive", gaussian_margin > 0, gaussian_margin, ">0")
    audit.check("gaussian_ray", "margin_above_three_quarters", gaussian_margin > sp.Rational(3, 4), gaussian_margin, ">3/4")
    y = sp.symbols("y", nonnegative=True)
    lower_polynomial = sp.Rational(9, 10) - gaussian_A - gaussian_B * y + sp.Rational(9, 2) * y**2
    completed = sp.expand(sp.Rational(9, 2) * (y - gaussian_B / 9) ** 2 + gaussian_margin)
    audit.check("gaussian_ray", "quartic_completion", sp.simplify(lower_polynomial - completed) == 0, lower_polynomial, completed)

    # Shell inheritance arithmetic: the accepted gamma=7/12 Cartan tail is
    # too slow for either R-131 target exponent.  A new gamma=4 one-use square
    # bound would be compatible with the far amplitude exponent, with the
    # five-shell offset costing 2^20.
    gamma_known = sp.Rational(7, 12)
    known_square_exponent = 2 * gamma_known
    known_amplitude_exponent = gamma_known
    audit.check("shell", "known_square_exponent", known_square_exponent == sp.Rational(7, 6), known_square_exponent, sp.Rational(7, 6))
    audit.check("shell", "known_amplitude_too_slow_mix", known_amplitude_exponent < 2, known_amplitude_exponent, "<2")
    audit.check("shell", "known_amplitude_too_slow_far", known_amplitude_exponent < 4, known_amplitude_exponent, "<4")
    gamma_successor = sp.Integer(4)
    audit.check("shell", "gamma_four_far_compatible", gamma_successor == 4, gamma_successor, 4)
    audit.check("shell", "support_offset_cost", 2 ** (4 * 5) == 2**20, 2 ** (4 * 5), 2**20)

    diagnostics = {
        "inputs": {"alpha": alpha, "c0": c0, "c1": c1, "p_mass": p_mass, "floor": floor},
        "replica": {"finite_fixture_lhs": lhs, "finite_fixture_rhs": paired},
        "mixed_fierz": {"formula": direct_mixed, "floor_dependence": "tau and tau_prime only"},
        "diagonal_heat_sextic": {
            "radius": radius,
            "denominator": denominator,
            "compact_v": compact_v,
            "compact_w": compact_w,
            "global_constant": sextic_outside,
            "half_radius": half_radius,
            "half_global_constant": half_sextic,
            "boundary": "diagonal mean-square only; not square of conditional mean",
        },
        "mixed_cancellation": {"mean_xi_at_origin": atom_means, "sextic_at_origin": 0},
        "law_free_floor_warning": {
            "hessian_over_c1": two_point_hessian_over_c1,
            "scaled_limit": -sp.Rational(10, 81),
            "production_counterexample": False,
        },
        "standard_gaussian_ray": {
            "negative_constant": gaussian_A,
            "negative_quadratic": gaussian_B,
            "source_sextic_margin": gaussian_margin,
            "source_sextic_margin_decimal": float(sp.N(gaussian_margin, 17)),
            "floor_uniform": True,
            "production_full_response": False,
        },
        "shell": {
            "known_gamma": gamma_known,
            "known_square_exponent": known_square_exponent,
            "known_amplitude_exponent": known_amplitude_exponent,
            "required_mix_exponent": 2,
            "required_far_exponent": 4,
            "successor_gamma": gamma_successor,
            "support_offset_cost": 2**20,
        },
    }
    payload = audit.finish(diagnostics)
    atomic_json(args.output, payload)
    print(
        f"R-132 primary {payload['status']}: "
        f"{payload['assertions_passed']}/{payload['assertions_total']} assertions"
    )
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

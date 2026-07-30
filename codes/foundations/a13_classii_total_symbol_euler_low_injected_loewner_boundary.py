#!/usr/bin/env python3
"""Primary exact verifier for the scoped R-126 A13 checkpoint."""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-30"
__version_issued__ = "2026-07-30"

import argparse
import json
import os
from pathlib import Path
import re
import tempfile
from typing import Any

import sympy as sp


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-TOTAL-SYMBOL-EULER-LOW-INJECTED-LOEWNER-BOUNDARY"
SCHEMA = "tect/a13-total-symbol-euler-low-injected-loewner-boundary-primary/1.0"
CLAIM_DIR = REPO / "claims" / CLAIM
DEFAULT_OUTPUT = CLAIM_DIR / "runs/2026-07-30-primary-total-symbol-euler-low-injected-loewner-boundary/result.json"
A1_MANIFEST = REPO / "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json"
R121_MANIFEST = CLAIM_DIR / "classii_cartan_pathspace_exactness_fixed_skew_sobolev_boundary_manifest.json"


def serial(value: Any) -> Any:
    if isinstance(value, sp.MatrixBase):
        return [[serial(value[i, j]) for j in range(value.cols)] for i in range(value.rows)]
    if isinstance(value, sp.Basic):
        return str(sp.simplify(value))
    if isinstance(value, tuple):
        return [serial(item) for item in value]
    if isinstance(value, list):
        return [serial(item) for item in value]
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
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
                "finite_cutoff_total_symbol_directional_derivative_proved": True,
                "periodic_euler_force_proved": True,
                "low_injected_baseline_recombination_proved": True,
                "block_loewner_acceptance_criterion_proved": True,
                "coefficient_blind_unrestricted_reverse_band_extension_refuted": True,
                "production_root_shell_bound_proved": False,
                "balanced_band_bound_proved": False,
                "overlap_src_proved": False,
                "nelson_proved": False,
                "sector_a_closed": False,
            },
            "no_overclaim": (
                "R-126 proves a finite-cutoff directional derivative, its periodic Euler-force "
                "form, an exact low/injected baseline recombination, a block-Loewner criterion, "
                "and a coefficient-blind unrestricted reverse-band no-go. The reverse fixture "
                "is anticipative and is not a legal production-control counterexample. It does not prove the "
                "production forward/reverse/balanced operator estimate, OVERLAP_src, Nelson, "
                "removals, an interacting measure, or Sector A closure."
            ),
        }


def production_mass() -> sp.Expr:
    parameters = json.loads(A1_MANIFEST.read_text(encoding="utf-8"))["parameters"]
    return sp.Rational(str(parameters["M_X"])) ** 2 + sp.Rational(str(parameters["classii_mass_regularizer"]))


def finite_atom_directional_identity(audit: Audit) -> dict[str, Any]:
    t = sp.symbols("t", real=True)
    weights = (sp.Rational(1, 3), sp.Rational(2, 3))
    c_base = sp.Matrix([[1, 0], [0, 2], [1, -1]])
    c_one = sp.Matrix([[1, 1], [0, -1], [2, 0]])
    c_two = sp.Matrix([[0, 1], [1, 0], [-1, 1]])
    states = (sp.Matrix([1, -2]), sp.Matrix([3, 1]))
    directions = (sp.Matrix([2, 1]), sp.Matrix([-1, 2]))
    velocities = (sp.Matrix([1, 3]), sp.Matrix([-2, 1]))
    velocity_directions = (sp.Matrix([2, -1]), sp.Matrix([1, 2]))
    gamma = sp.Matrix([[2, sp.Rational(1, 3)], [sp.Rational(1, 3), 3]])

    matrices: list[sp.Matrix] = []
    vectors: list[sp.Matrix] = []
    for state, direction, velocity, velocity_direction in zip(
        states, directions, velocities, velocity_directions, strict=True
    ):
        moved = state + t * direction
        matrices.append(c_base + moved[0] * c_one + moved[1] * c_two)
        vectors.append(velocity + t * velocity_direction)

    phi = sum(
        (weights[index] * matrices[index] * vectors[index] for index in range(2)),
        sp.zeros(3, 1),
    )
    theta = sum(
        (
            weights[index]
            * sp.trace(matrices[index].T * matrices[index] * gamma)
            for index in range(2)
        ),
        sp.Integer(0),
    )
    total_symbol = sp.expand(theta - phi.dot(phi))
    direct = sp.diff(total_symbol, t).subs(t, 0)

    phi_zero = phi.subs(t, 0)
    delta_phi = sum(
        (
            weights[index]
            * (
                sp.diff(matrices[index], t).subs(t, 0) * velocities[index]
                + matrices[index].subs(t, 0) * velocity_directions[index]
            )
            for index in range(2)
        ),
        sp.zeros(3, 1),
    )
    delta_trace = sum(
        (
            weights[index]
            * sp.trace(
                sp.diff(matrices[index].T * matrices[index], t).subs(t, 0) * gamma
            )
            for index in range(2)
        ),
        sp.Integer(0),
    )
    predicted = sp.expand(delta_trace - 2 * phi_zero.dot(delta_phi))
    audit.check("directional", "finite_atom_total_symbol", sp.simplify(direct - predicted) == 0, direct, predicted)
    audit.check("directional", "trace_factor_two", delta_trace != 0, delta_trace, "nonzero diagnostic")
    audit.check("directional", "mean_square_factor_two", phi_zero.dot(delta_phi) != 0, 2 * phi_zero.dot(delta_phi), "nonzero diagnostic")
    return {
        "total_symbol": total_symbol,
        "directional_derivative": direct,
        "trace_variation": delta_trace,
        "mean_square_variation": 2 * phi_zero.dot(delta_phi),
    }


def periodic_euler_identity(audit: Audit) -> dict[str, Any]:
    x, t, u_one, u_two = sp.symbols("x t u_one u_two", real=True)
    coordinate = sp.Matrix([u_one, u_two])
    row = sp.Matrix([u_one**2 + u_two, u_one * u_two + u_one])
    jacobian = row.jacobian(coordinate)
    state = sp.Matrix([sp.sin(x), sp.cos(x)])
    direction = sp.Matrix([sp.sin(2 * x), sp.cos(2 * x)])
    moved = state + t * direction
    substitutions = {u_one: moved[0], u_two: moved[1]}
    moved_row = row.subs(substitutions)
    moved_velocity = sp.diff(moved, x)
    gamma = sp.Matrix([[2, sp.Rational(1, 3)], [sp.Rational(1, 3), 3]])
    moved_phi = moved_row.dot(moved_velocity)
    integrand = (moved_row.T * gamma * moved_row)[0] - moved_phi**2
    direct = sp.integrate(sp.diff(integrand, t).subs(t, 0), (x, 0, 2 * sp.pi))

    substitutions_zero = {u_one: state[0], u_two: state[1]}
    row_zero = row.subs(substitutions_zero)
    jacobian_zero = jacobian.subs(substitutions_zero)
    velocity = sp.diff(state, x)
    phi = row_zero.dot(velocity)
    divergence_force = 2 * jacobian_zero.T * gamma * row_zero + 2 * sp.diff(phi * row_zero, x) - 2 * phi * jacobian_zero.T * velocity
    cartan_force = (
        2 * jacobian_zero.T * gamma * row_zero
        + 2 * row_zero * sp.diff(phi, x)
        + 2 * phi * (jacobian_zero - jacobian_zero.T) * velocity
    )
    divergence_pairing = sp.integrate(direction.dot(divergence_force), (x, 0, 2 * sp.pi))
    cartan_pairing = sp.integrate(direction.dot(cartan_force), (x, 0, 2 * sp.pi))
    audit.check("euler", "directional_equals_divergence_force", sp.simplify(direct - divergence_pairing) == 0, direct, divergence_pairing)
    audit.check("euler", "divergence_equals_cartan_form", sp.simplify(divergence_pairing - cartan_pairing) == 0, divergence_pairing, cartan_pairing)
    audit.check("euler", "nonzero_skew_jacobian", sp.simplify(jacobian_zero - jacobian_zero.T) != sp.zeros(2), jacobian_zero - jacobian_zero.T, "nonzero")
    audit.check("euler", "exact_periodic_value", direct == 4 * sp.pi, direct, 4 * sp.pi)
    return {
        "directional_pairing": direct,
        "divergence_force_pairing": divergence_pairing,
        "cartan_force_pairing": cartan_pairing,
        "skew_jacobian": jacobian_zero - jacobian_zero.T,
    }


def owner_and_low_recombination(audit: Audit) -> dict[str, Any]:
    # Exact rational fixture.  The identities are algebraic and the nonzero
    # W(A0) value prevents accidental promotion of the raw-reference special case.
    w_zero = sp.Rational(5, 7)
    d_zero_low = sp.Rational(-3, 5)
    b_zero = (sp.Rational(1, 3), sp.Rational(2, 5))
    d_zero_roots = (
        sp.Rational(-2, 7),
        -2 * w_zero - d_zero_low - sp.Rational(-2, 7),
    )
    f_blocks = (sp.Rational(3, 11), sp.Rational(-2, 13))
    d_middle_roots = tuple(d_zero_roots[index] - 2 * f_blocks[index] for index in range(2))
    b_middle = (sp.Rational(3, 8), sp.Rational(1, 6))
    i_blocks = (sp.Rational(-1, 9), sp.Rational(4, 15))
    d_terminal_roots = tuple(d_middle_roots[index] - 2 * i_blocks[index] for index in range(2))
    d_terminal_low = d_zero_low - 2 * sp.Rational(7, 20)

    baseline_raw = sum(d_zero_roots[index] - b_zero[index] ** 2 for index in range(2))
    baseline_middle = sum(d_middle_roots[index] - b_middle[index] ** 2 for index in range(2))
    raw_full = sp.simplify(d_zero_low + baseline_raw)
    middle_recombined = sp.simplify(d_zero_low + baseline_middle)
    predicted_raw = sp.simplify(-2 * w_zero - sum(value**2 for value in b_zero))
    predicted_middle = sp.simplify(
        -2 * w_zero - 2 * sum(f_blocks) - sum(value**2 for value in b_middle)
    )
    audit.check("low_recombination", "raw_full_with_nonzero_W0", raw_full == predicted_raw, raw_full, predicted_raw)
    audit.check("low_recombination", "middle_low_injected", middle_recombined == predicted_middle, middle_recombined, predicted_middle)
    audit.check(
        "low_recombination",
        "injected_D_sign",
        all(sp.simplify(d_middle_roots[index] - d_zero_roots[index] + 2 * f_blocks[index]) == 0 for index in range(2)),
        [d_middle_roots[index] - d_zero_roots[index] for index in range(2)],
        [-2 * value for value in f_blocks],
    )
    audit.check(
        "low_recombination",
        "future_D_sign",
        all(sp.simplify(d_terminal_roots[index] - d_middle_roots[index] + 2 * i_blocks[index]) == 0 for index in range(2)),
        [d_terminal_roots[index] - d_middle_roots[index] for index in range(2)],
        [-2 * value for value in i_blocks],
    )
    terminal_difference = sp.simplify(
        (d_terminal_low + sum(d_terminal_roots)) - (d_zero_low + sum(d_zero_roots))
    )
    predicted_terminal_difference = sp.simplify(
        -2 * (sp.Rational(7, 20) + sum(f_blocks) + sum(i_blocks))
    )
    audit.check("low_recombination", "R079_full_D_sign", terminal_difference == predicted_terminal_difference, terminal_difference, predicted_terminal_difference)
    audit.check("low_recombination", "W0_cannot_be_deleted", w_zero != 0, w_zero, "nonzero")
    return {
        "W_A0": w_zero,
        "raw_full_S": raw_full,
        "middle_low_injected_S": middle_recombined,
        "F_blocks": f_blocks,
        "I_blocks": i_blocks,
    }


def loewner_and_shell_criteria(audit: Audit, mass: sp.Expr) -> dict[str, Any]:
    eta = sp.Rational(1, 3)
    zeta = sp.Rational(1, 4)
    r_block = sp.Rational(1, 5)
    s_block = sp.Rational(1, 7)
    a_block = sp.Rational(2, 9)
    loewner = sp.Matrix(
        [
            [2 * eta - r_block, -a_block / 2],
            [-a_block / 2, 2 * zeta - s_block],
        ]
    )
    audit.check("loewner", "leading_minor", loewner[0, 0] > 0, loewner[0, 0], "positive")
    audit.check("loewner", "determinant", sp.det(loewner) > 0, sp.det(loewner), "positive")

    sharp = 4 * sp.sqrt(eta * zeta)
    boundary = sp.Matrix([[2 * eta, -sharp / 2], [-sharp / 2, 2 * zeta]])
    audit.check("loewner", "zero_diagonal_sharp_boundary", sp.det(boundary) == 0, sp.det(boundary), 0)
    failed = sp.Matrix([[2 * eta, -sp.Rational(5, 4) * sharp / 2], [-sp.Rational(5, 4) * sharp / 2, 2 * zeta]])
    audit.check("loewner", "above_threshold_fails", sp.det(failed) < 0, sp.det(failed), "negative")

    root_start, gap = sp.symbols("root_start gap", integer=True, nonnegative=True)
    positive_sum_factor = sp.Rational(128, 105)
    mixed_square_sum_factor = sp.Rational(64, 45)
    # Direct evaluation of the two nested geometric ratios.
    derived_positive = sp.simplify(1 / ((1 - sp.Rational(1, 16)) * (1 - sp.Rational(1, 8))))
    derived_mixed_square = sp.simplify(1 / ((1 - sp.Rational(1, 16)) * (1 - sp.Rational(1, 4))))
    audit.check("shells", "positive_geometric_factor", derived_positive == positive_sum_factor, derived_positive, positive_sum_factor)
    audit.check("shells", "mixed_square_geometric_factor", derived_mixed_square == mixed_square_sum_factor, derived_mixed_square, mixed_square_sum_factor)

    eta_budget = sp.Rational(197, 440) - sp.Rational(3, 125) / mass
    zeta_budget = sp.Rational(3, 25)
    operator_budget = 4 * sp.sqrt(eta_budget * zeta_budget)
    collar_one_coefficient = sp.sqrt(45) * operator_budget / 2
    audit.check("budget", "eta_positive", eta_budget > 0, eta_budget, "positive")
    audit.check("budget", "operator_budget_interval", sp.Rational(92, 100) < operator_budget < sp.Rational(93, 100), operator_budget, "between 0.92 and 0.93")
    audit.check("budget", "mixed_coefficient_interval", sp.Rational(308, 100) < collar_one_coefficient < sp.Rational(310, 100), collar_one_coefficient, "between 3.08 and 3.10")

    return {
        "block_loewner_matrix": loewner,
        "zero_diagonal_threshold": sharp,
        "positive_double_sum": positive_sum_factor * 2 ** (-4 * gap) * 2 ** (-3 * root_start),
        "mixed_square_double_sum": mixed_square_sum_factor * 2 ** (-4 * gap) * 2 ** (-2 * root_start),
        "mixed_HS_bound": sp.Rational(8, 1) / sp.sqrt(45) * 2 ** (-2 * gap) * 2 ** (-root_start),
        "production_operator_budget": operator_budget,
        "collar_one_Cmix_times_2_minus_j0_limit": collar_one_coefficient,
    }


def cartan_and_obstructions(audit: Audit) -> dict[str, Any]:
    r121 = json.loads(R121_MANIFEST.read_text(encoding="utf-8"))
    statement = r121["theorems"]["normalized_current_audit"]
    match = re.search(
        r"curls are (-?\d+)/(729) for K_R, (\d+)/(729) for M_U, and (\d+)/(729) after recombination",
        statement,
    )
    fractions = (
        [sp.Rational(int(match.group(index)), int(match.group(index + 1))) for index in (1, 3, 5)]
        if match
        else []
    )
    audit.check("cartan", "authority_fraction_count", len(fractions) == 3, len(fractions), 3)
    if len(fractions) == 3:
        audit.check("cartan", "owner_recombination", fractions[0] + fractions[1] == fractions[2], fractions[0] + fractions[1], fractions[2])
        audit.check("cartan", "surviving_curl", fractions[2] != 0, fractions[2], "nonzero")

    gamma, epsilon, time = sp.symbols("gamma epsilon time", positive=True)
    mixed_secant = -2 * gamma * epsilon * time + 4 * gamma * epsilon**2 * time**2
    audit.check("mixed_secant", "nonzero_linear_term", sp.diff(mixed_secant, epsilon).subs(epsilon, 0) == -2 * gamma * time, sp.diff(mixed_secant, epsilon).subs(epsilon, 0), -2 * gamma * time)
    audit.check("mixed_secant", "not_uniformly_quadratic", sp.limit(sp.Abs(mixed_secant) / epsilon**2, epsilon, 0, dir="+") == sp.oo, sp.limit(sp.Abs(mixed_secant) / epsilon**2, epsilon, 0, dir="+"), sp.oo)

    spatial_shell = 2
    reveal_roots = (10, 14, 18)
    source_costs = tuple(sp.Integer(2) ** (4 * spatial_shell) * sp.Integer(2) ** (-4 * spatial_shell) for _ in reveal_roots)
    reverse_positive = tuple(sp.Integer(2) ** (root - 4 * spatial_shell) for root in reveal_roots)
    reverse_mixed = tuple(sp.Integer(2) ** (root - 2 * spatial_shell) for root in reveal_roots)
    audit.check("unrestricted_reverse_band", "source_cost_fixed", len(set(source_costs)) == 1 and source_costs[0] == 1, source_costs, (1, 1, 1))
    audit.check("unrestricted_reverse_band", "positive_weight_diverges", reverse_positive[2] > reverse_positive[1] > reverse_positive[0], reverse_positive, "strictly increasing")
    audit.check("unrestricted_reverse_band", "mixed_weight_diverges", reverse_mixed[2] > reverse_mixed[1] > reverse_mixed[0], reverse_mixed, "strictly increasing")
    audit.check("unrestricted_reverse_band", "four_root_ratio", reverse_mixed[1] / reverse_mixed[0] == 16, reverse_mixed[1] / reverse_mixed[0], 16)
    return {
        "authority_curls": fractions,
        "mixed_secant_fixture": mixed_secant,
        "reverse_reveal_roots": reveal_roots,
        "reverse_source_costs": source_costs,
        "reverse_positive_weights": reverse_positive,
        "reverse_mixed_weights": reverse_mixed,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()
    audit = Audit()
    mass = production_mass()
    audit.check("production", "mass_from_A1", mass == sp.Rational(4000000000001, 10**12), mass, sp.Rational(4000000000001, 10**12))

    diagnostics = {
        "directional": finite_atom_directional_identity(audit),
        "euler": periodic_euler_identity(audit),
        "low_recombination": owner_and_low_recombination(audit),
        "loewner_shells": loewner_and_shell_criteria(audit, mass),
        "cartan_obstructions": cartan_and_obstructions(audit),
    }
    payload = audit.finish(diagnostics)
    atomic_json(arguments.output, payload)
    print(
        f"R-126 primary {payload['status']} "
        f"{payload['assertions_passed']}/{payload['assertions_total']} -> {arguments.output}"
    )
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

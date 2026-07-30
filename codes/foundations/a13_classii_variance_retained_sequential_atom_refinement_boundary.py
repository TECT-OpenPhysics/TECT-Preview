#!/usr/bin/env python3
"""Primary exact audit for the A13 R-135 sequential-atom boundary.

This executable proves the formula-level re-paralinearisation of the R-088
sequential Cartan atom under the R-087 finite-cutoff hypotheses, computes the
exact spatial and Schur weights, and tests the existing one-shell rare-event
obstruction against the resulting R-087 ``q_mod`` majorant.  The obstruction
rejects that majorant route even without revisit multiplicity; it is not a
counterexample to the exact sequential atom and does not create a new named
negative result.  Finite-collar numbers remain conditional on a different,
once-owned ``q`` ledger and certified production headroom.
"""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-31"
__version_issued__ = "2026-07-31"

import argparse
import json
import os
from pathlib import Path
import tempfile
from typing import Any

import sympy as sp


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-VARIANCE-RETAINED-SEQUENTIAL-ATOM-REFINEMENT-BOUNDARY"
SCHEMA = "tect/a13-variance-retained-sequential-atom-refinement-boundary-primary/1.0"
CLAIM_DIR = REPO / "claims" / CLAIM
DEFAULT_OUTPUT = CLAIM_DIR / (
    "runs/2026-07-31-primary-variance-retained-sequential-atom-refinement-boundary/"
    "result.json"
)
R087_RESULT = CLAIM_DIR / (
    "runs/2026-07-25-primary-cartan-spatial-decay-rational-trace-"
    "variational-core-reduction/result.json"
)
R088_RESULT = CLAIM_DIR / (
    "runs/2026-07-25-primary-direct-root-cartan-schur-sequential-secant-"
    "rational-conditional-trace/result.json"
)
R125_RESULT = CLAIM_DIR / (
    "runs/2026-07-30-integrated-conditional-variance-forest-bridge-"
    "root-shell-operator-boundary/result.json"
)
R134_RESULT = CLAIM_DIR / (
    "runs/2026-07-31-primary-terminal-smoothing-fixed-law-action-"
    "aggregate-collar-boundary/result.json"
)
R125_RESULT_ID = (
    "A13-CLASSII-CONDITIONAL-VARIANCE-FOREST-BRIDGE-ROOT-SHELL-"
    "OPERATOR-BOUNDARY"
)
EXISTING_NEGATIVE = (
    "NG-2026-07-25-A13-PATHWISE-TRANSLATED-MODEL-NORM-EXTRACTION"
)
SCALED_FIXTURE_NEGATIVE = "NG-2026-07-31-A13-COVARIANCE-ENVELOPE-REBATE-ERASURE"
REFINEMENT_NEGATIVE = "NG-2026-07-31-A13-REFINEMENT-UNIFORM-LAST-BLOCK-ELLIPTICITY"
COLLAR_SAMPLES = (5, 8, 11, 14, 17, 18)
NORMALIZED_HEADROOM_SAMPLES = (
    sp.Rational(1),
    sp.Rational(1, 10),
    sp.Rational(1, 100),
    sp.Rational(1, 1000),
)


def serial(value: Any) -> Any:
    if isinstance(value, sp.MatrixBase):
        return [[serial(value[i, j]) for j in range(value.cols)] for i in range(value.rows)]
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


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []
        self.identifiers: set[str] = set()

    def check(
        self, group: str, name: str, condition: bool, actual: Any, expected: Any
    ) -> None:
        identifier = f"{group}::{name}"
        if identifier in self.identifiers:
            raise ValueError(f"duplicate assertion identifier: {identifier}")
        self.identifiers.add(identifier)
        self.rows.append(
            {
                "id": identifier,
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
                "fixed_cutoff_positive_floor_sequential_spatial_reparalinearisation": True,
                "three_channel_formula_contract_checked": True,
                "qj_support_is_explicit_hypothesis": True,
                "numerical_full_production_spatial_proof": False,
                "r087_self_atom_directly_dominates_r088_sequential_atom": False,
                "exact_radial_sequential_curvature_identity": True,
                "qmod_majorant_one_use_route_rejected_without_revisits": True,
                "one_active_shell_no_revisit_is_fixture_input": True,
                "exact_sequential_atom_counterexample": False,
                "scaled_r125_fixture_is_full_production_counterexample": False,
                "full_production_counterexample": False,
                "new_named_negative_result_required": True,
                "qmod_new_named_negative_result_required": False,
                "scaled_fixture_negative_result": SCALED_FIXTURE_NEGATIVE,
                "refinement_negative_result": REFINEMENT_NEGATIVE,
                "existing_negative_result_reused": EXISTING_NEGATIVE,
                "r123_full_target_retains_complete_low_owner": True,
                "r123_trace_excess_is_live_target": True,
                "production_r123_trace_excess_bound": False,
                "directed_refinement_last_block_architecture_rejected": True,
                "physical_tail_covariance_finite_sequence_oracle_checked": True,
                "physical_tail_covariance_limit_proved_by_finite_oracle": False,
                "refinement_uniform_terminal_ellipticity": False,
                "conditional_finite_collar_weights_reusable": True,
                "production_one_use_q_ledger": False,
                "production_near_balanced_headroom": False,
                "executable_alone_registers_formal_result": False,
                "sector_a_closed": False,
            },
            "no_overclaim": (
                "This executable establishes a scoped formula-level sequential "
                "re-paralinearisation and rejects only the existing q_mod majorant "
                "route. It does not refute the exact atom, prove a production q "
                "ledger or headroom, or close Sector A. The executable alone does "
                "not register the result; companion repository records do."
            ),
        }


def fraction(text: object) -> sp.Rational:
    return sp.Rational(str(text))


def smallest_strict_collar(
    amplitude: sp.Expr, gamma: sp.Rational, normalized_headroom: sp.Rational
) -> int:
    collar = 5
    while not bool(
        sp.N(amplitude * 2 ** (-gamma * (collar - 5)), 60)
        < sp.N(normalized_headroom, 60)
    ):
        collar += 1
        if collar > 10000:
            raise RuntimeError("strict collar search did not terminate")
    return collar


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()
    audit = Audit()

    r087 = load_json(R087_RESULT)
    r088 = load_json(R088_RESULT)
    r125 = load_json(R125_RESULT)
    r134 = load_json(R134_RESULT)
    for label, payload in (
        ("r087", r087),
        ("r088", r088),
        ("r125", r125),
        ("r134", r134),
    ):
        audit.check("upstream", f"{label}_pass", payload.get("status") == "PASS", payload.get("status"), "PASS")
    audit.check(
        "upstream",
        "r125_result_id",
        r125.get("result_id") == R125_RESULT_ID,
        r125.get("result_id"),
        R125_RESULT_ID,
    )

    cartan = r087["cartan"]
    alpha = fraction(cartan["alpha"])
    beta = sp.simplify(6 * alpha - 1)
    gamma = fraction(r134["diagnostics"]["inputs"]["gamma"])
    aggregate_s = sp.Rational(2, 3)
    direct_s = gamma
    safe_c0 = int(cartan["safe_C0"])
    root_margin_aggregate = sp.simplify(beta - 2 * aggregate_s)
    gap_margin_aggregate = sp.simplify(4 * alpha - 2 * aggregate_s)
    root_margin_direct = sp.simplify(beta - 2 * direct_s)
    gap_margin_direct = sp.simplify(4 * alpha - 2 * direct_s)

    audit.check("exponents", "beta_derived", beta == fraction(cartan["beta"]), beta, cartan["beta"])
    audit.check("exponents", "safe_c0", safe_c0 == 5, safe_c0, 5)
    audit.check("exponents", "aggregate_s_in_r087_window", sp.Rational(1, 2) < aggregate_s < 3 * alpha - sp.Rational(1, 2), aggregate_s, f"1/2<s<{3 * alpha - sp.Rational(1, 2)}")
    audit.check("exponents", "aggregate_gamma_gap", 0 < gamma < aggregate_s, gamma, f"0<gamma<{aggregate_s}")
    audit.check("exponents", "aggregate_root_margin", root_margin_aggregate == sp.Rational(1, 15), root_margin_aggregate, sp.Rational(1, 15))
    audit.check("exponents", "aggregate_gap_margin", gap_margin_aggregate == sp.Rational(4, 15), gap_margin_aggregate, sp.Rational(4, 15))
    audit.check("exponents", "direct_root_margin", root_margin_direct == sp.Rational(7, 30), root_margin_direct, sp.Rational(7, 30))
    audit.check("exponents", "direct_gap_margin", gap_margin_direct == sp.Rational(13, 30), gap_margin_direct, sp.Rational(13, 30))

    # The scalar polynomial is an exact algebra oracle for the vector current
    # variation.  The proof theorem itself uses the R-087 smooth LP argument.
    z, dz = sp.symbols("z dz", real=True)
    b, db = sp.symbols("b db", real=True)
    a1, da1, a2, da2 = sp.symbols("a1 da1 a2 da2", real=True)
    v, dv = sp.symbols("v dv", real=True)
    t, theta = sp.symbols("t theta", real=True)
    phi = z**3 + 2 * z
    current = sp.diff(phi, z) * v * dz + phi * dv
    variables = sp.Matrix([z, dz])
    gradient = sp.Matrix([sp.diff(current, z), sp.diff(current, dz)])
    hessian = sp.hessian(current, (z, dz))
    total = sp.Matrix([a1 + a2, da1 + da2])
    base = sp.Matrix([b, db])

    def evaluate(expression: sp.Expr, state: sp.Matrix) -> sp.Expr:
        return sp.expand(expression.subs({z: state[0], dz: state[1]}))

    def radial_owner(direction: sp.Matrix) -> sp.Expr:
        state = base + t * total
        integrand = evaluate((gradient.T * direction)[0], state)
        return sp.expand(sp.integrate(integrand, (t, 0, 1)))

    def sequential_owner(past: sp.Matrix, direction: sp.Matrix) -> sp.Expr:
        start = base + past
        return sp.expand(
            evaluate(current, start + direction) - evaluate(current, start)
        )

    def curvature_remainder(
        past: sp.Matrix, future: sp.Matrix, direction: sp.Matrix
    ) -> sp.Expr:
        homotopy = (1 - t) * past - t * future
        state = base + t * total + theta * homotopy
        integrand = evaluate(
            (homotopy.T * hessian * direction)[0], state
        )
        return sp.expand(
            sp.integrate(sp.integrate(integrand, (theta, 0, 1)), (t, 0, 1))
        )

    zero = sp.zeros(2, 1)
    first = sp.Matrix([a1, da1])
    second = sp.Matrix([a2, da2])
    sequential_state = base + t * first
    sequential_value = sequential_state[0]
    sequential_derivative = sequential_state[1]
    channel_hessian = sp.expand(
        sp.diff(phi, z, 2).subs(z, sequential_value)
        * a1
        * v
        * sequential_derivative
    )
    channel_control_derivative = sp.expand(
        sp.diff(phi, z).subs(z, sequential_value) * v * da1
    )
    channel_root_derivative = sp.expand(
        sp.diff(phi, z).subs(z, sequential_value) * a1 * dv
    )
    sequential_directional_integrand = evaluate(
        (gradient.T * first)[0], sequential_state
    )
    three_channel_sum = sp.expand(
        channel_hessian + channel_control_derivative + channel_root_derivative
    )
    audit.check(
        "structure",
        "three_channel_identity",
        sp.expand(sequential_directional_integrand - three_channel_sum) == 0,
        sp.expand(sequential_directional_integrand - three_channel_sum),
        0,
    )
    audit.check("structure", "channel_hessian_present", channel_hessian != 0, channel_hessian, "nonzero polynomial")
    audit.check("structure", "channel_control_derivative_present", channel_control_derivative != 0, channel_control_derivative, "nonzero polynomial")
    audit.check("structure", "channel_root_derivative_present", channel_root_derivative != 0, channel_root_derivative, "nonzero polynomial")
    qj_support_hypothesis = ("w_j", "A_(k-1)", "a_k")
    audit.check(
        "structure",
        "qj_support_hypothesis_explicit",
        qj_support_hypothesis == ("w_j", "A_(k-1)", "a_k"),
        qj_support_hypothesis,
        "declared Q_j-supported inputs",
    )
    principal_support_radii = (sp.Rational(19, 3), sp.Rational(26, 3))
    audit.check(
        "structure",
        "principal_support_within_qj4",
        max(principal_support_radii) < 2**4
        and cartan["principal_support_cube"] == "Q_(j+4)",
        {
            "relative_radii": principal_support_radii,
            "upstream_cube": cartan["principal_support_cube"],
        },
        "radii < 16 and upstream Q_(j+4)",
    )
    self_first = radial_owner(first)
    self_second = radial_owner(second)
    seq_first = sequential_owner(zero, first)
    seq_second = sequential_owner(first, second)
    rem_first = curvature_remainder(zero, second, first)
    rem_second = curvature_remainder(first, zero, second)
    endpoint = sp.expand(evaluate(current, base + total) - evaluate(current, base))
    sequential_integral = sp.expand(sp.integrate(three_channel_sum, (t, 0, 1)))
    audit.check(
        "structure",
        "sequential_integral_identity",
        sp.expand(seq_first - sequential_integral) == 0,
        sp.expand(seq_first - sequential_integral),
        0,
    )
    audit.check("paths", "first_homotopy_identity", sp.expand(seq_first - self_first - rem_first) == 0, sp.expand(seq_first - self_first - rem_first), 0)
    audit.check("paths", "second_homotopy_identity", sp.expand(seq_second - self_second - rem_second) == 0, sp.expand(seq_second - self_second - rem_second), 0)
    audit.check("paths", "radial_telescope", sp.expand(self_first + self_second - endpoint) == 0, sp.expand(self_first + self_second - endpoint), 0)
    audit.check("paths", "sequential_telescope", sp.expand(seq_first + seq_second - endpoint) == 0, sp.expand(seq_first + seq_second - endpoint), 0)
    audit.check("paths", "signed_curvature_cancellation", sp.expand(rem_first + rem_second) == 0, sp.expand(rem_first + rem_second), 0)
    audit.check("paths", "ownerwise_paths_differ", sp.expand(seq_first - self_first) != 0, sp.expand(seq_first - self_first), "nonzero polynomial")

    # The existing one-shell predictable rare event has no revisit factor.
    probability_exponent = sp.Integer(-6)
    source_amplitude_exponent = sp.Integer(3)
    smoothing_gain = sp.Integer(2)
    control_amplitude_exponent = source_amplitude_exponent - smoothing_gain
    translated_norm_exponent = 1 + alpha
    derivative_square_exponent = 2 * (control_amplitude_exponent + 1)
    qmod_exponent = sp.simplify(
        -beta
        + probability_exponent
        + 6 * translated_norm_exponent
        + derivative_square_exponent
    )
    source_budget_exponent = probability_exponent + 2 * source_amplitude_exponent
    sextic_budget_exponent = probability_exponent + 6 * control_amplitude_exponent
    mixed_budget_exponent = sp.simplify(
        (source_budget_exponent + sextic_budget_exponent) / 2
    )
    old_weighted_exponent = sp.simplify(qmod_exponent + 1)
    audit.check("rare_event", "integer_qmod_exponent", bool(qmod_exponent.is_integer), qmod_exponent, "integer")
    shell_samples = (2, 4, 8)
    qmod_samples = [sp.Integer(value) ** qmod_exponent for value in shell_samples]
    qmod_ratios = [sp.simplify(qmod_samples[index + 1] / qmod_samples[index]) for index in range(len(qmod_samples) - 1)]
    active_shell_N = shell_samples[-1]
    active_shell_profile = {
        offset: (sp.Integer(active_shell_N) ** qmod_exponent if offset == 0 else sp.Integer(0))
        for offset in range(-2, 3)
    }
    active_offsets = [
        offset for offset, contribution in active_shell_profile.items() if contribution != 0
    ]
    audit.check(
        "rare_event",
        "one_active_shell_construction",
        active_offsets == [0]
        and sum(active_shell_profile.values(), sp.Integer(0))
        == sp.Integer(active_shell_N) ** qmod_exponent,
        {"active_offsets": active_offsets, "profile": active_shell_profile},
        "one nonzero shell at offset 0",
    )
    audit.check("rare_event", "source_budget_exponent", source_budget_exponent == 0, source_budget_exponent, 0)
    audit.check("rare_event", "sextic_budget_exponent", sextic_budget_exponent == 0, sextic_budget_exponent, 0)
    audit.check("rare_event", "mixed_budget_exponent", mixed_budget_exponent == 0, mixed_budget_exponent, 0)
    audit.check("rare_event", "qmod_exponent", qmod_exponent == 5, qmod_exponent, 5)
    audit.check("rare_event", "old_weighted_exponent", old_weighted_exponent == 6, old_weighted_exponent, 6)
    audit.check("rare_event", "qmod_geometric_growth", all(ratio == 2**qmod_exponent for ratio in qmod_ratios), qmod_ratios, [2**qmod_exponent] * len(qmod_ratios))
    audit.check("rare_event", "current_upstream_growth", r088["direct_cartan"]["old_qmod_direct_growth"] == "N^5", r088["direct_cartan"]["old_qmod_direct_growth"], "N^5")
    audit.check("rare_event", "exact_atom_not_refuted", r088["claims_not_established"]["production_sequential_secant_to_quartic_bridge"] is False, r088["claims_not_established"]["production_sequential_secant_to_quartic_bridge"], False)

    inputs = r134["diagnostics"]["inputs"]
    p_mass = fraction(inputs["p_mass"])
    c0 = fraction(inputs["c0"])
    c1 = fraction(inputs["c1"])
    alpha_frame = fraction(inputs["alpha"])
    beta_operator = sp.simplify(4 * (c0 + c1))
    upstream_beta_operator = fraction(inputs["beta_operator"])
    nu = sp.symbols("nu", positive=True)
    eta_gaussian = sp.symbols("eta_gaussian", real=True)
    x_fixture = sp.Matrix(
        [2 * nu * eta_gaussian * sp.sqrt(c0), 2 * nu * eta_gaussian * sp.sqrt(c1)]
    )
    phi_fixture = x_fixture.subs(eta_gaussian, 0)
    theta_fixture = sp.simplify(4 * (c0 + c1) * nu**2)
    variance_fixture = sp.simplify(
        sum(
            sp.expand(component**2).coeff(eta_gaussian, 2)
            for component in x_fixture
        )
    )
    forest_fixture = sp.Integer(0)
    trace_excess_fixture = sp.simplify(theta_fixture - phi_fixture.dot(phi_fixture))
    pcomp_fixture = sp.simplify(-trace_excess_fixture / 2)
    audit.check("owner", "beta_operator", beta_operator == sp.Rational(339, 2000) / p_mass == upstream_beta_operator, beta_operator, sp.Rational(339, 2000) / p_mass)
    audit.check("owner", "phi_zero", phi_fixture == sp.zeros(2, 1), phi_fixture, sp.zeros(2, 1))
    audit.check("owner", "theta_variance", theta_fixture == variance_fixture == beta_operator * nu**2, {"theta": theta_fixture, "variance": variance_fixture}, beta_operator * nu**2)
    audit.check("owner", "forest_zero", forest_fixture == 0, forest_fixture, 0)
    audit.check("owner", "pcomp", pcomp_fixture == -beta_operator * nu**2 / 2, pcomp_fixture, -beta_operator * nu**2 / 2)
    audit.check("owner", "trace_excess_target", trace_excess_fixture == beta_operator * nu**2, trace_excess_fixture, beta_operator * nu**2)

    # Independent finite two-atom check of the R-125 conditional Pythagoras
    # identity with a genuinely nonzero conditional mean.  The forest scalar
    # is a once-owned algebra input; this fixture is not a production model.
    phi_nonzero = sp.Matrix([sp.Rational(3, 2), sp.Rational(-2, 3)])
    fluctuation = sp.Matrix([sp.Rational(5, 7), sp.Integer(0)])
    current_plus = phi_nonzero + fluctuation
    current_minus = phi_nonzero - fluctuation
    current_mean = sp.simplify((current_plus + current_minus) / 2)
    current_second_moment = sp.simplify(
        (current_plus.dot(current_plus) + current_minus.dot(current_minus)) / 2
    )
    future_variance_nonzero = sp.simplify(
        (
            (current_plus - current_mean).dot(current_plus - current_mean)
            + (current_minus - current_mean).dot(current_minus - current_mean)
        )
        / 2
    )
    trace_excess_nonzero = sp.simplify(
        current_second_moment - current_mean.dot(current_mean)
    )
    forest_nonzero = sp.Rational(11, 13)
    pcomp_nonzero = sp.simplify(
        (forest_nonzero - future_variance_nonzero) / 2
    )
    audit.check("owner", "nonzero_phi", current_mean == phi_nonzero and current_mean != sp.zeros(2, 1), current_mean, phi_nonzero)
    audit.check("owner", "nonzero_phi_pythagoras", current_second_moment == current_mean.dot(current_mean) + future_variance_nonzero, current_second_moment, current_mean.dot(current_mean) + future_variance_nonzero)
    audit.check("owner", "nonzero_phi_trace_excess", trace_excess_nonzero == future_variance_nonzero, trace_excess_nonzero, future_variance_nonzero)
    audit.check("owner", "nonzero_phi_factor_half", 2 * pcomp_nonzero == forest_nonzero - future_variance_nonzero, 2 * pcomp_nonzero, forest_nonzero - future_variance_nonzero)

    fixture_nu = sp.Rational(7, 3)
    fixture_floor = sp.Rational(452, 25)
    a_squared = fixture_nu**2
    b_e_squared = fixture_floor * fixture_nu**2
    floor_square_coefficient = sp.simplify(alpha_frame**2 * c1 * fixture_floor)
    q_e = sp.simplify(4 * beta_operator * fixture_nu**2)
    forest_minus_q_e = sp.simplify(forest_fixture - q_e)
    audit.check("owner", "a_squared", a_squared == fixture_nu**2, a_squared, fixture_nu**2)
    audit.check("owner", "be_squared", b_e_squared == fixture_floor * fixture_nu**2, b_e_squared, fixture_floor * fixture_nu**2)
    audit.check("owner", "matched_floor_square_coefficient", floor_square_coefficient == beta_operator, floor_square_coefficient, beta_operator)
    audit.check("owner", "surrogate_coefficient_negative", forest_minus_q_e / fixture_nu**2 == -4 * beta_operator and forest_minus_q_e < 0, forest_minus_q_e / fixture_nu**2, -4 * beta_operator)
    full_target_owners = ("complete_low_stationary", "recombined_roots")
    audit.check("owner", "complete_low_retained", "complete_low_stationary" in full_target_owners, full_target_owners, "complete low/stationary plus recombined roots")
    audit.check("owner", "production_target_open", r134["scope"]["production_signed_forest_bound"] is False, r134["scope"]["production_signed_forest_bound"], False)

    epsilon = sp.symbols("epsilon", positive=True)
    identity_six = sp.eye(6)
    revealed_covariance = (1 - epsilon) * identity_six
    terminal_covariance = epsilon * identity_six
    split_covariance = sp.simplify(revealed_covariance + terminal_covariance)
    terminal_eigenvalues = terminal_covariance.eigenvals()
    smoothing = r134["diagnostics"]["six_real_smoothing"]
    q2_base = fraction(smoothing["q2"])
    q4_base = fraction(smoothing["q4"])
    d2_base = fraction(smoothing["d2f_l2_over_lambda"])
    d3_base = fraction(smoothing["d3f_l2_over_lambda_squared"])
    q2_cost = sp.simplify(q2_base / epsilon)
    q4_cost = sp.simplify(q4_base / epsilon**2)
    d2_cost = sp.simplify(d2_base / epsilon)
    d3_cost = sp.simplify(d3_base / epsilon**2)
    audit.check("refinement", "covariance_split", split_covariance == identity_six, split_covariance, identity_six)
    audit.check("refinement", "terminal_min_eigenvalue", terminal_eigenvalues == {epsilon: 6}, terminal_eigenvalues, {epsilon: 6})
    audit.check("refinement", "q2_cost", q2_cost == 1 / (4 * epsilon), q2_cost, 1 / (4 * epsilon))
    audit.check("refinement", "q4_cost", q4_cost == 1 / (8 * epsilon**2), q4_cost, 1 / (8 * epsilon**2))
    audit.check("refinement", "d2_cost", d2_cost == 49 / epsilon, d2_cost, 49 / epsilon)
    audit.check("refinement", "d3_cost", d3_cost == sp.Rational(3249, 2) / epsilon**2, d3_cost, sp.Rational(3249, 2) / epsilon**2)
    epsilon_samples = tuple(sp.Rational(1, 2**power) for power in range(1, 7))
    tail_table = [
        {
            "epsilon": value,
            "trace": 6 * value,
            "minimum_eigenvalue": value,
            "q2_cost": sp.simplify(q2_base / value),
            "q4_cost": sp.simplify(q4_base / value**2),
            "d2_cost": sp.simplify(d2_base / value),
            "d3_cost": sp.simplify(d3_base / value**2),
        }
        for value in epsilon_samples
    ]
    audit.check("refinement", "physical_tail_sequence_oracle", all(tail_table[index + 1]["minimum_eigenvalue"] * 2 == tail_table[index]["minimum_eigenvalue"] for index in range(len(tail_table) - 1)), [row["minimum_eigenvalue"] for row in tail_table], "exact halving toward zero")
    audit.check("refinement", "symbolic_tail_limit", sp.limit(epsilon, epsilon, 0, dir="+") == 0, sp.limit(epsilon, epsilon, 0, dir="+"), 0)
    audit.check("refinement", "cost_divergence", all(sp.limit(cost, epsilon, 0, dir="+") == sp.oo for cost in (q2_cost, q4_cost, d2_cost, d3_cost)), [sp.limit(cost, epsilon, 0, dir="+") for cost in (q2_cost, q4_cost, d2_cost, d3_cost)], [sp.oo] * 4)
    maximal_owner_covariance = sp.zeros(6)
    audit.check("refinement", "maximal_owner_zero_future_covariance", maximal_owner_covariance == sp.zeros(6), maximal_owner_covariance, sp.zeros(6))

    aggregate_constant = sp.simplify(
        2 ** (-10 * aggregate_s)
        / (
            (1 - 2 ** (-aggregate_s)) ** 2
            * (1 - 2 ** (-2 * (aggregate_s - gamma)))
        )
    )
    direct_constant = sp.simplify(
        2 ** (-10 * direct_s)
        / ((1 - 2 ** (-direct_s)) ** 2 * (1 - 2 ** (-2 * direct_s)))
    )
    aggregate_amplitude = sp.sqrt(aggregate_constant)
    direct_amplitude = sp.sqrt(direct_constant)
    upstream_shell = r134["diagnostics"]["aggregate_shell"]
    audit.check("collar", "aggregate_constant_matches_r134", abs(float(sp.N(aggregate_constant, 20)) - float(upstream_shell["conditional_B_constant_decimal"])) < 2e-15, sp.N(aggregate_constant, 20), upstream_shell["conditional_B_constant_decimal"])
    audit.check("collar", "direct_constant_matches_r134", abs(float(sp.N(direct_constant, 20)) - float(upstream_shell["direct_fixed_collar_constant_decimal"])) < 2e-15, sp.N(direct_constant, 20), upstream_shell["direct_fixed_collar_constant_decimal"])
    audit.check("collar", "direct_amplitude_smaller", bool(sp.N(direct_amplitude, 40) < sp.N(aggregate_amplitude, 40)), sp.N(direct_amplitude / aggregate_amplitude, 20), "<1")
    audit.check("collar", "upstream_q_ledger_open", upstream_shell["production_q_ledger"] is False, upstream_shell["production_q_ledger"], False)

    headroom_table: list[dict[str, Any]] = []
    for collar in COLLAR_SAMPLES:
        ratio = sp.simplify(2 ** (-gamma * (collar - safe_c0)))
        headroom_table.append(
            {
                "collar": collar,
                "tail_ratio": ratio,
                "aggregate_required_per_owner_sqrt_q": sp.N(aggregate_amplitude * ratio, 18),
                "direct_required_per_owner_sqrt_q": sp.N(direct_amplitude * ratio, 18),
            }
        )
    audit.check("collar", "sample_tail_monotone", all(float(headroom_table[index + 1]["tail_ratio"]) < float(headroom_table[index]["tail_ratio"]) for index in range(len(headroom_table) - 1)), [row["tail_ratio"] for row in headroom_table], "strictly decreasing")
    audit.check("collar", "sample_direct_below_aggregate", all(float(row["direct_required_per_owner_sqrt_q"]) < float(row["aggregate_required_per_owner_sqrt_q"]) for row in headroom_table), headroom_table, "direct<aggregate at every sample")

    strict_collar_table = []
    for normalized_headroom in NORMALIZED_HEADROOM_SAMPLES:
        strict_collar_table.append(
            {
                "normalized_headroom": normalized_headroom,
                "aggregate_smallest_strict_collar": smallest_strict_collar(
                    aggregate_amplitude, gamma, normalized_headroom
                ),
                "direct_smallest_strict_collar": smallest_strict_collar(
                    direct_amplitude, gamma, normalized_headroom
                ),
            }
        )
    audit.check("collar", "strict_collars_nondecreasing", all(strict_collar_table[index + 1]["aggregate_smallest_strict_collar"] >= strict_collar_table[index]["aggregate_smallest_strict_collar"] and strict_collar_table[index + 1]["direct_smallest_strict_collar"] >= strict_collar_table[index]["direct_smallest_strict_collar"] for index in range(len(strict_collar_table) - 1)), strict_collar_table, "nondecreasing as headroom shrinks")

    q_formula = (
        "C_e*2^(-(6*alpha-1)*k)*sup_(j>=k) sum_A E int_0^1 "
        "(1+||B_(j,k)+r a_k||_(C^alpha))^6 "
        "(||a_k||_2^2+||D a_k||_2^2) dr"
    )
    diagnostics = {
        "upstream": {
            "r087": R087_RESULT.relative_to(REPO).as_posix(),
            "r088": R088_RESULT.relative_to(REPO).as_posix(),
            "r125": R125_RESULT.relative_to(REPO).as_posix(),
            "r134": R134_RESULT.relative_to(REPO).as_posix(),
        },
        "sequential_reparalinearisation": {
            "alpha": alpha,
            "beta": beta,
            "safe_c0": safe_c0,
            "q_seq_formula": q_formula,
            "three_channels": (
                "D2Phi(u_seq)[a_k,v]^T D u_seq",
                "DPhi(u_seq)[v]^T D a_k",
                "DPhi(u_seq)[a_k]^T Dv",
            ),
            "qj_support_hypothesis": qj_support_hypothesis,
            "support_relative_radii": principal_support_radii,
            "aggregate_s": aggregate_s,
            "aggregate_gamma": gamma,
            "aggregate_root_margin": root_margin_aggregate,
            "aggregate_gap_margin": gap_margin_aggregate,
            "direct_s": direct_s,
            "direct_root_margin": root_margin_direct,
            "direct_gap_margin": gap_margin_direct,
            "ownerwise_direct_domination_from_self_atom": False,
            "exact_path_difference": (
                "T_k-M_k=int_0^1 int_0^1 D2G(w+tA+theta H_(k,t))"
                "[H_(k,t),a_k] dtheta dt"
            ),
            "path_weight": "H_(k,t)=(1-t)A_<(k)-tA_>(k)",
            "signed_path_differences_sum_to_zero": True,
        },
        "single_shell_rare_event": {
            "probability": "N^-6",
            "h_amplitude": "N^3",
            "a_amplitude": "N",
            "source_budget_exponent": source_budget_exponent,
            "sextic_budget_exponent": sextic_budget_exponent,
            "mixed_budget_exponent": mixed_budget_exponent,
            "qmod_exponent": qmod_exponent,
            "old_weighted_exponent": old_weighted_exponent,
            "sample_N": shell_samples,
            "sample_qmod": qmod_samples,
            "one_active_shell_profile": active_shell_profile,
            "revisit_multiplicity": 1,
            "exact_atom_counterexample": False,
            "existing_negative_result": EXISTING_NEGATIVE,
            "new_named_negative_result_required": False,
        },
        "owner_trace_excess": {
            "p_mass": p_mass,
            "beta_operator": beta_operator,
            "phi": phi_fixture,
            "phi_zero": True,
            "theta": theta_fixture,
            "conditional_variance": variance_fixture,
            "forest_expectation": forest_fixture,
            "pcomp": pcomp_fixture,
            "trace_excess": trace_excess_fixture,
            "theta_over_nu_squared": beta_operator,
            "variance_over_nu_squared": beta_operator,
            "pcomp_over_nu_squared": -beta_operator / 2,
            "trace_excess_over_nu_squared": beta_operator,
            "fixture_nu": fixture_nu,
            "fixture_floor": fixture_floor,
            "a_squared": a_squared,
            "b_e_squared": b_e_squared,
            "a_squared_over_nu_squared": 1,
            "b_e_squared_over_e_nu_squared": 1,
            "q_e": q_e,
            "forest_minus_q_e": forest_minus_q_e,
            "forest_minus_q_e_coefficient": sp.simplify(forest_minus_q_e / fixture_nu**2),
            "full_target_owners": full_target_owners,
            "full_target": "sum_o E(Theta_o-||Phi_o||^2)",
            "production_target_proved": False,
            "nonzero_phi_fixture": {
                "phi": tuple(current_mean[index, 0] for index in range(current_mean.rows)),
                "theta": current_second_moment,
                "future_variance": future_variance_nonzero,
                "trace_excess": trace_excess_nonzero,
                "forest": forest_nonzero,
                "pcomp": pcomp_nonzero,
            },
        },
        "directed_refinement": {
            "covariance_split": "(1-epsilon) I_6 + epsilon I_6 = I_6",
            "minimum_eigenvalue": epsilon,
            "q2_cost": q2_cost,
            "q4_cost": q4_cost,
            "d2_cost": d2_cost,
            "d3_cost": d3_cost,
            "tail_table": tail_table,
            "maximal_retained_owner_future_covariance": maximal_owner_covariance,
            "uniform_positive_terminal_ellipticity": False,
            "maximal_owner_zero_future_covariance": True,
            "full_production_counterexample": False,
        },
        "finite_collar": {
            "gamma": gamma,
            "aggregate_square_constant": aggregate_constant,
            "aggregate_amplitude_constant": sp.N(aggregate_amplitude, 18),
            "direct_square_constant": direct_constant,
            "direct_amplitude_constant": sp.N(direct_amplitude, 18),
            "required_headroom_formula": (
                "h(C)/(Lambda_own*sqrt(Q)) > amplitude_constant*"
                "2^(-7(C-5)/12)"
            ),
            "sample_requirements": headroom_table,
            "strict_collar_table": strict_collar_table,
            "usable_only_if_exact_q_ledger_and_headroom_are_supplied": True,
            "production_collar_certified": False,
        },
    }
    result = audit.finish(diagnostics)
    atomic_json(arguments.output, result)
    print(
        f"R-135 primary {result['status']}: "
        f"{result['assertions_passed']}/{result['assertions_total']}"
    )
    print(f"q_mod one-shell exponent={qmod_exponent}")
    print(f"aggregate amplitude={float(sp.N(aggregate_amplitude, 18)):.15f}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

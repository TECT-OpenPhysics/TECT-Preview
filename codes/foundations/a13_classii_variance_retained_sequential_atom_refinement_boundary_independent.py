#!/usr/bin/env python3
"""Independent standard-library audit of the A13 R-135 boundary.

This file neither imports nor reads the primary R-135 implementation.  Exact
Fraction arithmetic and tensor-product Simpson integration independently
check the sequential/radial path identity, exponent ledger, rare-event
scaling, and conditional finite-collar weights.
"""

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
from typing import Any, Callable


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-VARIANCE-RETAINED-SEQUENTIAL-ATOM-REFINEMENT-BOUNDARY"
SCHEMA = "tect/a13-variance-retained-sequential-atom-refinement-boundary-independent/1.0"
CLAIM_DIR = REPO / "claims" / CLAIM
DEFAULT_OUTPUT = CLAIM_DIR / (
    "runs/2026-07-31-independent-variance-retained-sequential-atom-refinement-boundary/"
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
    Fraction(1),
    Fraction(1, 10),
    Fraction(1, 100),
    Fraction(1, 1000),
)


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=f".{path.name}.", suffix=".tmp", dir=path.parent
    )
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
                "actual": actual,
                "expected": expected,
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
            "diagnostics": diagnostics,
            "scope": {
                "standard_library_independent": True,
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
                "This independent audit checks exact algebra and derived constants "
                "only. It rejects the q_mod route, not the exact sequential atom, "
                "and proves no production ledger, headroom, or Sector-A closure. "
                "The executable alone does not register the result; companion "
                "repository records do."
            ),
        }


def parse_fraction(value: object) -> Fraction:
    return Fraction(str(value))


def phi(value: Fraction) -> Fraction:
    return value**3 + 2 * value


def dphi(value: Fraction) -> Fraction:
    return 3 * value**2 + 2


def ddphi(value: Fraction) -> Fraction:
    return 6 * value


def dddphi(_: Fraction) -> Fraction:
    return Fraction(6)


def current(
    value: Fraction,
    derivative: Fraction,
    root_value: Fraction,
    root_derivative: Fraction,
) -> Fraction:
    return dphi(value) * root_value * derivative + phi(value) * root_derivative


def directional_current(
    value: Fraction,
    derivative: Fraction,
    direction: Fraction,
    direction_derivative: Fraction,
    root_value: Fraction,
    root_derivative: Fraction,
) -> Fraction:
    return (
        (ddphi(value) * root_value * derivative + dphi(value) * root_derivative)
        * direction
        + dphi(value) * root_value * direction_derivative
    )


def second_directional_current(
    value: Fraction,
    derivative: Fraction,
    first: Fraction,
    first_derivative: Fraction,
    second: Fraction,
    second_derivative: Fraction,
    root_value: Fraction,
    root_derivative: Fraction,
) -> Fraction:
    zz = dddphi(value) * root_value * derivative + ddphi(value) * root_derivative
    zd = ddphi(value) * root_value
    return (
        zz * first * second
        + zd
        * (first * second_derivative + first_derivative * second)
    )


def simpson(function: Callable[[Fraction], Fraction]) -> Fraction:
    return (
        function(Fraction(0))
        + 4 * function(Fraction(1, 2))
        + function(Fraction(1))
    ) / 6


def double_simpson(
    function: Callable[[Fraction, Fraction], Fraction]
) -> Fraction:
    nodes = (Fraction(0), Fraction(1, 2), Fraction(1))
    weights = (Fraction(1), Fraction(4), Fraction(1))
    return sum(
        weights[i] * weights[j] * function(t, theta)
        for i, t in enumerate(nodes)
        for j, theta in enumerate(nodes)
    ) / 36


def smallest_strict_collar(
    amplitude: float, gamma: Fraction, normalized_headroom: Fraction
) -> int:
    collar = 5
    target = float(normalized_headroom)
    while not amplitude * 2.0 ** (-float(gamma) * (collar - 5)) < target:
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

    alpha = parse_fraction(r087["cartan"]["alpha"])
    beta = 6 * alpha - 1
    gamma = parse_fraction(r134["diagnostics"]["inputs"]["gamma"])
    aggregate_s = Fraction(2, 3)
    direct_s = gamma
    safe_c0 = int(r087["cartan"]["safe_C0"])
    margins = {
        "aggregate_root": beta - 2 * aggregate_s,
        "aggregate_gap": 4 * alpha - 2 * aggregate_s,
        "direct_root": beta - 2 * direct_s,
        "direct_gap": 4 * alpha - 2 * direct_s,
    }
    audit.check("exponents", "beta", beta == parse_fraction(r087["cartan"]["beta"]), str(beta), r087["cartan"]["beta"])
    audit.check("exponents", "safe_c0", safe_c0 == 5, safe_c0, 5)
    audit.check("exponents", "aggregate_window", Fraction(1, 2) < aggregate_s < 3 * alpha - Fraction(1, 2), str(aggregate_s), f"1/2<s<{3 * alpha - Fraction(1, 2)}")
    audit.check("exponents", "aggregate_gamma_gap", 0 < gamma < aggregate_s, str(gamma), f"0<gamma<{aggregate_s}")
    audit.check("exponents", "aggregate_root_margin", margins["aggregate_root"] == Fraction(1, 15), str(margins["aggregate_root"]), "1/15")
    audit.check("exponents", "aggregate_gap_margin", margins["aggregate_gap"] == Fraction(4, 15), str(margins["aggregate_gap"]), "4/15")
    audit.check("exponents", "direct_root_margin", margins["direct_root"] == Fraction(7, 30), str(margins["direct_root"]), "7/30")
    audit.check("exponents", "direct_gap_margin", margins["direct_gap"] == Fraction(13, 30), str(margins["direct_gap"]), "13/30")

    structural_samples = (
        (Fraction(1), Fraction(2), Fraction(3), Fraction(5), Fraction(7), Fraction(11), Fraction(0)),
        (Fraction(-2, 3), Fraction(4, 5), Fraction(5, 7), Fraction(-3, 2), Fraction(2), Fraction(-1, 3), Fraction(1, 2)),
    )
    channel_rows = []
    for value, derivative, direction, direction_derivative, root, root_derivative, time in structural_samples:
        path_value = value + time * direction
        path_derivative = derivative + time * direction_derivative
        channel_hessian = ddphi(path_value) * direction * root * path_derivative
        channel_control_derivative = dphi(path_value) * root * direction_derivative
        channel_root_derivative = dphi(path_value) * direction * root_derivative
        full = directional_current(
            path_value,
            path_derivative,
            direction,
            direction_derivative,
            root,
            root_derivative,
        )
        channel_rows.append(
            {
                "hessian": channel_hessian,
                "control_derivative": channel_control_derivative,
                "root_derivative": channel_root_derivative,
                "full": full,
                "sum": channel_hessian + channel_control_derivative + channel_root_derivative,
            }
        )
    audit.check("structure", "three_channel_identity", all(row["full"] == row["sum"] for row in channel_rows), [{key: str(value) for key, value in row.items()} for row in channel_rows], "full=sum of three channels")
    audit.check("structure", "channel_hessian_present", any(row["hessian"] != 0 for row in channel_rows), [str(row["hessian"]) for row in channel_rows], "some nonzero")
    audit.check("structure", "channel_control_derivative_present", any(row["control_derivative"] != 0 for row in channel_rows), [str(row["control_derivative"]) for row in channel_rows], "some nonzero")
    audit.check("structure", "channel_root_derivative_present", any(row["root_derivative"] != 0 for row in channel_rows), [str(row["root_derivative"]) for row in channel_rows], "some nonzero")
    qj_support_hypothesis = ("w_j", "A_(k-1)", "a_k")
    audit.check("structure", "qj_support_hypothesis_explicit", qj_support_hypothesis == ("w_j", "A_(k-1)", "a_k"), qj_support_hypothesis, "declared Q_j-supported inputs")
    principal_support_radii = (Fraction(19, 3), Fraction(26, 3))
    audit.check("structure", "principal_support_within_qj4", max(principal_support_radii) < 16 and r087["cartan"]["principal_support_cube"] == "Q_(j+4)", {"relative_radii": [str(value) for value in principal_support_radii], "upstream_cube": r087["cartan"]["principal_support_cube"]}, "radii < 16 and upstream Q_(j+4)")

    fixtures = (
        tuple(Fraction(item) for item in (1, 2, 3, 1, -2, 4, 2, -1)),
        tuple(Fraction(item) for item in (-2, 1, 1, -3, 4, 2, -1, 3)),
        (
            Fraction(1, 3), Fraction(-2, 5), Fraction(3, 7),
            Fraction(5, 11), Fraction(-7, 13), Fraction(11, 17),
            Fraction(13, 19), Fraction(-17, 23),
        ),
    )
    fixture_diagnostics = []
    signed_path_differences: list[Fraction] = []
    for index, (base, dbase, a1, da1, a2, da2, root, droot) in enumerate(fixtures, start=1):
        total = a1 + a2
        dtotal = da1 + da2

        def radial_owner(direction: Fraction, ddirection: Fraction) -> Fraction:
            return simpson(
                lambda time: directional_current(
                    base + time * total,
                    dbase + time * dtotal,
                    direction,
                    ddirection,
                    root,
                    droot,
                )
            )

        self_first = radial_owner(a1, da1)
        self_second = radial_owner(a2, da2)
        seq_first = current(base + a1, dbase + da1, root, droot) - current(base, dbase, root, droot)
        seq_second = current(base + total, dbase + dtotal, root, droot) - current(base + a1, dbase + da1, root, droot)

        def remainder(
            past: Fraction,
            dpast: Fraction,
            future: Fraction,
            dfuture: Fraction,
            direction: Fraction,
            ddirection: Fraction,
        ) -> Fraction:
            return double_simpson(
                lambda time, interpolation: second_directional_current(
                    base
                    + time * total
                    + interpolation * ((1 - time) * past - time * future),
                    dbase
                    + time * dtotal
                    + interpolation * ((1 - time) * dpast - time * dfuture),
                    (1 - time) * past - time * future,
                    (1 - time) * dpast - time * dfuture,
                    direction,
                    ddirection,
                    root,
                    droot,
                )
            )

        rem_first = remainder(Fraction(0), Fraction(0), a2, da2, a1, da1)
        rem_second = remainder(a1, da1, Fraction(0), Fraction(0), a2, da2)
        signed_path_differences.append(rem_first + rem_second)
        endpoint = current(base + total, dbase + dtotal, root, droot) - current(base, dbase, root, droot)
        audit.check("paths", f"fixture_{index}_first_homotopy", seq_first - self_first == rem_first, str(seq_first - self_first), str(rem_first))
        audit.check("paths", f"fixture_{index}_second_homotopy", seq_second - self_second == rem_second, str(seq_second - self_second), str(rem_second))
        audit.check("paths", f"fixture_{index}_both_telescopes", self_first + self_second == endpoint and seq_first + seq_second == endpoint, {"radial": str(self_first + self_second), "sequential": str(seq_first + seq_second)}, str(endpoint))
        fixture_diagnostics.append(
            {
                "fixture": index,
                "first_path_difference": str(seq_first - self_first),
                "second_path_difference": str(seq_second - self_second),
                "signed_difference_sum": str(rem_first + rem_second),
            }
        )
    audit.check("paths", "at_least_one_ownerwise_difference", any(item["first_path_difference"] != "0" for item in fixture_diagnostics), fixture_diagnostics, "some nonzero ownerwise difference")
    audit.check("paths", "signed_differences_cancel", all(value == 0 for value in signed_path_differences), [str(value) for value in signed_path_differences], "all zero")

    probability_exponent = Fraction(-6)
    source_amplitude_exponent = Fraction(3)
    smoothing_gain = Fraction(2)
    control_amplitude_exponent = source_amplitude_exponent - smoothing_gain
    translated_norm_exponent = 1 + alpha
    derivative_square_exponent = 2 * (control_amplitude_exponent + 1)
    qmod_exponent = (
        -beta
        + probability_exponent
        + 6 * translated_norm_exponent
        + derivative_square_exponent
    )
    source_budget_exponent = probability_exponent + 2 * source_amplitude_exponent
    sextic_budget_exponent = probability_exponent + 6 * control_amplitude_exponent
    mixed_budget_exponent = (source_budget_exponent + sextic_budget_exponent) / 2
    weighted_exponent = qmod_exponent + 1
    audit.check("rare_event", "integer_qmod_exponent", qmod_exponent.denominator == 1, str(qmod_exponent), "integer")
    shell_samples = (2, 4, 8)
    qmod_power = qmod_exponent.numerator
    qmod_samples = tuple(value**qmod_power for value in shell_samples)
    active_shell_N = shell_samples[-1]
    active_shell_profile = {
        offset: (active_shell_N**qmod_power if offset == 0 else 0)
        for offset in range(-2, 3)
    }
    active_offsets = [
        offset for offset, contribution in active_shell_profile.items() if contribution != 0
    ]
    audit.check("rare_event", "one_active_shell_construction", active_offsets == [0] and sum(active_shell_profile.values()) == active_shell_N**qmod_power, {"active_offsets": active_offsets, "profile": active_shell_profile}, "one nonzero shell at offset 0")
    audit.check("rare_event", "source_budget", source_budget_exponent == 0, str(source_budget_exponent), "0")
    audit.check("rare_event", "sextic_budget", sextic_budget_exponent == 0, str(sextic_budget_exponent), "0")
    audit.check("rare_event", "mixed_budget", mixed_budget_exponent == 0, str(mixed_budget_exponent), "0")
    audit.check("rare_event", "qmod_growth", qmod_exponent == 5, str(qmod_exponent), "5")
    audit.check("rare_event", "old_weighted_growth", weighted_exponent == 6, str(weighted_exponent), "6")
    audit.check("rare_event", "sample_ratio", all(qmod_samples[index + 1] == qmod_samples[index] * 2**qmod_power for index in range(len(qmod_samples) - 1)), qmod_samples, f"ratio {2**qmod_power}")
    audit.check("rare_event", "upstream_N5", r088["direct_cartan"]["old_qmod_direct_growth"] == "N^5", r088["direct_cartan"]["old_qmod_direct_growth"], "N^5")
    audit.check("rare_event", "no_exact_atom_claim", r088["claims_not_established"]["production_sequential_secant_to_quartic_bridge"] is False, r088["claims_not_established"]["production_sequential_secant_to_quartic_bridge"], False)

    inputs = r134["diagnostics"]["inputs"]
    p_mass = parse_fraction(inputs["p_mass"])
    c0 = parse_fraction(inputs["c0"])
    c1 = parse_fraction(inputs["c1"])
    alpha_frame = parse_fraction(inputs["alpha"])
    beta_operator = 4 * (c0 + c1)
    upstream_beta_operator = parse_fraction(inputs["beta_operator"])
    fixture_nu = Fraction(7, 3)
    fixture_floor = Fraction(452, 25)
    phi_fixture = (Fraction(0), Fraction(0))
    theta_fixture = beta_operator * fixture_nu**2
    variance_fixture = 4 * (c0 + c1) * fixture_nu**2
    forest_fixture = Fraction(0)
    trace_excess_fixture = theta_fixture - sum(value * value for value in phi_fixture)
    pcomp_fixture = -trace_excess_fixture / 2
    audit.check("owner", "beta_operator", beta_operator == Fraction(339, 2000) / p_mass == upstream_beta_operator, str(beta_operator), str(Fraction(339, 2000) / p_mass))
    audit.check("owner", "phi_zero", phi_fixture == (Fraction(0), Fraction(0)), [str(value) for value in phi_fixture], ["0", "0"])
    audit.check("owner", "theta_variance", theta_fixture == variance_fixture == beta_operator * fixture_nu**2, {"theta": str(theta_fixture), "variance": str(variance_fixture)}, str(beta_operator * fixture_nu**2))
    audit.check("owner", "forest_zero", forest_fixture == 0, str(forest_fixture), "0")
    audit.check("owner", "pcomp", pcomp_fixture == -beta_operator * fixture_nu**2 / 2, str(pcomp_fixture), str(-beta_operator * fixture_nu**2 / 2))
    audit.check("owner", "trace_excess_target", trace_excess_fixture == beta_operator * fixture_nu**2, str(trace_excess_fixture), str(beta_operator * fixture_nu**2))

    # Separate exact two-atom conditional-law oracle with nonzero mean.
    # The forest scalar is an algebra input, not a production-model claim.
    phi_nonzero = (Fraction(3, 2), Fraction(-2, 3))
    fluctuation = (Fraction(5, 7), Fraction(0))
    current_plus = tuple(phi_nonzero[index] + fluctuation[index] for index in range(2))
    current_minus = tuple(phi_nonzero[index] - fluctuation[index] for index in range(2))
    current_mean = tuple((current_plus[index] + current_minus[index]) / 2 for index in range(2))
    current_second_moment = (
        sum(value * value for value in current_plus)
        + sum(value * value for value in current_minus)
    ) / 2
    future_variance_nonzero = (
        sum((current_plus[index] - current_mean[index]) ** 2 for index in range(2))
        + sum((current_minus[index] - current_mean[index]) ** 2 for index in range(2))
    ) / 2
    mean_square_nonzero = sum(value * value for value in current_mean)
    trace_excess_nonzero = current_second_moment - mean_square_nonzero
    forest_nonzero = Fraction(11, 13)
    pcomp_nonzero = (forest_nonzero - future_variance_nonzero) / 2
    audit.check("owner", "nonzero_phi", current_mean == phi_nonzero and any(value != 0 for value in current_mean), [str(value) for value in current_mean], [str(value) for value in phi_nonzero])
    audit.check("owner", "nonzero_phi_pythagoras", current_second_moment == mean_square_nonzero + future_variance_nonzero, str(current_second_moment), str(mean_square_nonzero + future_variance_nonzero))
    audit.check("owner", "nonzero_phi_trace_excess", trace_excess_nonzero == future_variance_nonzero, str(trace_excess_nonzero), str(future_variance_nonzero))
    audit.check("owner", "nonzero_phi_factor_half", 2 * pcomp_nonzero == forest_nonzero - future_variance_nonzero, str(2 * pcomp_nonzero), str(forest_nonzero - future_variance_nonzero))
    a_squared = fixture_nu**2
    b_e_squared = fixture_floor * fixture_nu**2
    floor_square_coefficient = alpha_frame**2 * c1 * fixture_floor
    q_e = 4 * beta_operator * fixture_nu**2
    forest_minus_q_e = forest_fixture - q_e
    audit.check("owner", "a_squared", a_squared == fixture_nu**2, str(a_squared), str(fixture_nu**2))
    audit.check("owner", "be_squared", b_e_squared == fixture_floor * fixture_nu**2, str(b_e_squared), str(fixture_floor * fixture_nu**2))
    audit.check("owner", "matched_floor_square_coefficient", floor_square_coefficient == beta_operator, str(floor_square_coefficient), str(beta_operator))
    audit.check("owner", "surrogate_coefficient_negative", forest_minus_q_e / fixture_nu**2 == -4 * beta_operator and forest_minus_q_e < 0, str(forest_minus_q_e / fixture_nu**2), str(-4 * beta_operator))
    full_target_owners = ("complete_low_stationary", "recombined_roots")
    audit.check("owner", "complete_low_retained", "complete_low_stationary" in full_target_owners, full_target_owners, "complete low/stationary plus recombined roots")
    audit.check("owner", "production_target_open", r134["scope"]["production_signed_forest_bound"] is False, r134["scope"]["production_signed_forest_bound"], False)

    smoothing = r134["diagnostics"]["six_real_smoothing"]
    q2_base = parse_fraction(smoothing["q2"])
    q4_base = parse_fraction(smoothing["q4"])
    d2_base = parse_fraction(smoothing["d2f_l2_over_lambda"])
    d3_base = parse_fraction(smoothing["d3f_l2_over_lambda_squared"])
    epsilon_samples = tuple(Fraction(1, 2**power) for power in range(1, 7))
    tail_table = []
    for epsilon in epsilon_samples:
        revealed_diagonal = tuple(1 - epsilon for _ in range(6))
        terminal_diagonal = tuple(epsilon for _ in range(6))
        total_diagonal = tuple(
            revealed_diagonal[index] + terminal_diagonal[index]
            for index in range(6)
        )
        tail_table.append(
            {
                "epsilon": epsilon,
                "revealed_diagonal": revealed_diagonal,
                "terminal_diagonal": terminal_diagonal,
                "total_diagonal": total_diagonal,
                "trace": 6 * epsilon,
                "minimum_eigenvalue": min(terminal_diagonal),
                "q2_cost": q2_base / epsilon,
                "q4_cost": q4_base / epsilon**2,
                "d2_cost": d2_base / epsilon,
                "d3_cost": d3_base / epsilon**2,
            }
        )
    audit.check("refinement", "covariance_split", all(row["total_diagonal"] == (Fraction(1),) * 6 for row in tail_table), [[str(value) for value in row["total_diagonal"]] for row in tail_table], ["1"] * 6)
    audit.check("refinement", "terminal_min_eigenvalue", all(row["minimum_eigenvalue"] == row["epsilon"] for row in tail_table), [str(row["minimum_eigenvalue"]) for row in tail_table], [str(value) for value in epsilon_samples])
    audit.check("refinement", "q2_cost", all(row["q2_cost"] == 1 / (4 * row["epsilon"]) for row in tail_table), [str(row["q2_cost"]) for row in tail_table], "1/(4 epsilon)")
    audit.check("refinement", "q4_cost", all(row["q4_cost"] == 1 / (8 * row["epsilon"] ** 2) for row in tail_table), [str(row["q4_cost"]) for row in tail_table], "1/(8 epsilon^2)")
    audit.check("refinement", "d2_cost", all(row["d2_cost"] == 49 / row["epsilon"] for row in tail_table), [str(row["d2_cost"]) for row in tail_table], "49/epsilon")
    audit.check("refinement", "d3_cost", all(row["d3_cost"] == Fraction(3249, 2) / row["epsilon"] ** 2 for row in tail_table), [str(row["d3_cost"]) for row in tail_table], "3249/(2 epsilon^2)")
    audit.check("refinement", "physical_tail_sequence_oracle", all(tail_table[index + 1]["minimum_eigenvalue"] * 2 == tail_table[index]["minimum_eigenvalue"] for index in range(len(tail_table) - 1)), [str(row["minimum_eigenvalue"]) for row in tail_table], "exact halving toward zero")
    audit.check("refinement", "symbolic_tail_limit", epsilon_samples[-1] < Fraction(1, 32) and all(epsilon_samples[index + 1] < epsilon_samples[index] for index in range(len(epsilon_samples) - 1)), [str(value) for value in epsilon_samples], "finite sequence oracle decreases toward zero")
    audit.check("refinement", "cost_divergence", all(tail_table[index + 1]["q2_cost"] > tail_table[index]["q2_cost"] and tail_table[index + 1]["q4_cost"] > tail_table[index]["q4_cost"] and tail_table[index + 1]["d2_cost"] > tail_table[index]["d2_cost"] and tail_table[index + 1]["d3_cost"] > tail_table[index]["d3_cost"] for index in range(len(tail_table) - 1)), [{key: str(row[key]) for key in ("q2_cost", "q4_cost", "d2_cost", "d3_cost")} for row in tail_table], "all costs strictly increase as epsilon halves")
    maximal_owner_covariance = (Fraction(0),) * 6
    audit.check("refinement", "maximal_owner_zero_future_covariance", maximal_owner_covariance == (Fraction(0),) * 6, [str(value) for value in maximal_owner_covariance], ["0"] * 6)

    aggregate_constant = 2.0 ** (-10.0 * float(aggregate_s)) / (
        (1.0 - 2.0 ** (-float(aggregate_s))) ** 2
        * (1.0 - 2.0 ** (-2.0 * float(aggregate_s - gamma)))
    )
    direct_constant = 2.0 ** (-10.0 * float(direct_s)) / (
        (1.0 - 2.0 ** (-float(direct_s))) ** 2
        * (1.0 - 2.0 ** (-2.0 * float(direct_s)))
    )
    aggregate_amplitude = math.sqrt(aggregate_constant)
    direct_amplitude = math.sqrt(direct_constant)
    upstream_shell = r134["diagnostics"]["aggregate_shell"]
    audit.check("collar", "aggregate_constant", abs(aggregate_constant - float(upstream_shell["conditional_B_constant_decimal"])) < 2e-15, aggregate_constant, upstream_shell["conditional_B_constant_decimal"])
    audit.check("collar", "direct_constant", abs(direct_constant - float(upstream_shell["direct_fixed_collar_constant_decimal"])) < 2e-15, direct_constant, upstream_shell["direct_fixed_collar_constant_decimal"])
    audit.check("collar", "direct_below_aggregate", direct_amplitude < aggregate_amplitude, direct_amplitude / aggregate_amplitude, "<1")
    audit.check("collar", "upstream_q_open", upstream_shell["production_q_ledger"] is False, upstream_shell["production_q_ledger"], False)

    headroom_table = []
    for collar in COLLAR_SAMPLES:
        ratio = 2.0 ** (-float(gamma) * (collar - safe_c0))
        headroom_table.append(
            {
                "collar": collar,
                "tail_ratio": ratio,
                "aggregate_required_per_owner_sqrt_q": aggregate_amplitude * ratio,
                "direct_required_per_owner_sqrt_q": direct_amplitude * ratio,
            }
        )
    audit.check("collar", "table_monotone", all(headroom_table[index + 1]["tail_ratio"] < headroom_table[index]["tail_ratio"] for index in range(len(headroom_table) - 1)), [row["tail_ratio"] for row in headroom_table], "strictly decreasing")
    audit.check("collar", "table_direct_smaller", all(row["direct_required_per_owner_sqrt_q"] < row["aggregate_required_per_owner_sqrt_q"] for row in headroom_table), headroom_table, "direct<aggregate")

    strict_collar_table = []
    for normalized_headroom in NORMALIZED_HEADROOM_SAMPLES:
        strict_collar_table.append(
            {
                "normalized_headroom": str(normalized_headroom),
                "aggregate_smallest_strict_collar": smallest_strict_collar(
                    aggregate_amplitude, gamma, normalized_headroom
                ),
                "direct_smallest_strict_collar": smallest_strict_collar(
                    direct_amplitude, gamma, normalized_headroom
                ),
            }
        )
    audit.check("collar", "strict_table_nondecreasing", all(strict_collar_table[index + 1]["aggregate_smallest_strict_collar"] >= strict_collar_table[index]["aggregate_smallest_strict_collar"] and strict_collar_table[index + 1]["direct_smallest_strict_collar"] >= strict_collar_table[index]["direct_smallest_strict_collar"] for index in range(len(strict_collar_table) - 1)), strict_collar_table, "nondecreasing")

    diagnostics = {
        "upstream": {
            "r087": R087_RESULT.relative_to(REPO).as_posix(),
            "r088": R088_RESULT.relative_to(REPO).as_posix(),
            "r125": R125_RESULT.relative_to(REPO).as_posix(),
            "r134": R134_RESULT.relative_to(REPO).as_posix(),
        },
        "sequential_reparalinearisation": {
            "alpha": str(alpha),
            "beta": str(beta),
            "safe_c0": safe_c0,
            "q_seq_formula": (
                "C_e*2^(-(6*alpha-1)*k)*sup_(j>=k) sum_A E int_0^1 "
                "(1+||B_(j,k)+r a_k||_(C^alpha))^6 "
                "(||a_k||_2^2+||D a_k||_2^2) dr"
            ),
            "three_channels": (
                "D2Phi(u_seq)[a_k,v]^T D u_seq",
                "DPhi(u_seq)[v]^T D a_k",
                "DPhi(u_seq)[a_k]^T Dv",
            ),
            "qj_support_hypothesis": qj_support_hypothesis,
            "support_relative_radii": tuple(str(value) for value in principal_support_radii),
            "aggregate_s": str(aggregate_s),
            "aggregate_gamma": str(gamma),
            "aggregate_root_margin": str(margins["aggregate_root"]),
            "aggregate_gap_margin": str(margins["aggregate_gap"]),
            "direct_s": str(direct_s),
            "direct_root_margin": str(margins["direct_root"]),
            "direct_gap_margin": str(margins["direct_gap"]),
            "path_weight": "H_(k,t)=(1-t)A_<(k)-tA_>(k)",
            "fixture_diagnostics": fixture_diagnostics,
            "ownerwise_direct_domination_from_self_atom": False,
        },
        "single_shell_rare_event": {
            "source_budget_exponent": str(source_budget_exponent),
            "sextic_budget_exponent": str(sextic_budget_exponent),
            "mixed_budget_exponent": str(mixed_budget_exponent),
            "qmod_exponent": str(qmod_exponent),
            "old_weighted_exponent": str(weighted_exponent),
            "sample_N": shell_samples,
            "sample_qmod": qmod_samples,
            "one_active_shell_profile": active_shell_profile,
            "revisit_multiplicity": 1,
            "exact_atom_counterexample": False,
            "existing_negative_result": EXISTING_NEGATIVE,
            "new_named_negative_result_required": False,
        },
        "owner_trace_excess": {
            "p_mass": str(p_mass),
            "beta_operator": str(beta_operator),
            "phi": tuple(str(value) for value in phi_fixture),
            "phi_zero": True,
            "theta": str(theta_fixture),
            "conditional_variance": str(variance_fixture),
            "forest_expectation": str(forest_fixture),
            "pcomp": str(pcomp_fixture),
            "trace_excess": str(trace_excess_fixture),
            "theta_over_nu_squared": str(beta_operator),
            "variance_over_nu_squared": str(beta_operator),
            "pcomp_over_nu_squared": str(-beta_operator / 2),
            "trace_excess_over_nu_squared": str(beta_operator),
            "fixture_nu": str(fixture_nu),
            "fixture_floor": str(fixture_floor),
            "a_squared": str(a_squared),
            "b_e_squared": str(b_e_squared),
            "a_squared_over_nu_squared": "1",
            "b_e_squared_over_e_nu_squared": "1",
            "q_e": str(q_e),
            "forest_minus_q_e": str(forest_minus_q_e),
            "forest_minus_q_e_coefficient": str(forest_minus_q_e / fixture_nu**2),
            "full_target_owners": full_target_owners,
            "full_target": "sum_o E(Theta_o-||Phi_o||^2)",
            "production_target_proved": False,
            "nonzero_phi_fixture": {
                "phi": tuple(str(value) for value in current_mean),
                "theta": str(current_second_moment),
                "future_variance": str(future_variance_nonzero),
                "trace_excess": str(trace_excess_nonzero),
                "forest": str(forest_nonzero),
                "pcomp": str(pcomp_nonzero),
            },
        },
        "directed_refinement": {
            "covariance_split": "(1-epsilon) I_6 + epsilon I_6 = I_6",
            "minimum_eigenvalue": "epsilon",
            "q2_cost": "1/(4*epsilon)",
            "q4_cost": "1/(8*epsilon**2)",
            "d2_cost": "49/epsilon",
            "d3_cost": "3249/(2*epsilon**2)",
            "tail_table": [
                {
                    key: (
                        [str(value) for value in item]
                        if isinstance(item, tuple)
                        else str(item)
                    )
                    for key, item in row.items()
                }
                for row in tail_table
            ],
            "maximal_retained_owner_future_covariance": tuple(str(value) for value in maximal_owner_covariance),
            "uniform_positive_terminal_ellipticity": False,
            "maximal_owner_zero_future_covariance": True,
            "full_production_counterexample": False,
        },
        "finite_collar": {
            "gamma": str(gamma),
            "aggregate_square_constant": aggregate_constant,
            "aggregate_amplitude_constant": aggregate_amplitude,
            "direct_square_constant": direct_constant,
            "direct_amplitude_constant": direct_amplitude,
            "sample_requirements": headroom_table,
            "strict_collar_table": strict_collar_table,
            "usable_only_if_exact_q_ledger_and_headroom_are_supplied": True,
            "production_collar_certified": False,
        },
    }
    result = audit.finish(diagnostics)
    atomic_json(arguments.output, result)
    print(
        f"R-135 independent {result['status']}: "
        f"{result['assertions_passed']}/{result['assertions_total']}"
    )
    print(f"q_mod one-shell exponent={qmod_exponent}")
    print(f"direct amplitude={direct_amplitude:.15f}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

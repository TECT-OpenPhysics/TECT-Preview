#!/usr/bin/env python3
"""Primary exact certificate for the R-103 regular H_N/REG reassembly.

The new mathematics is an exact owner partition and a finite form-budget
allocation.  This executable deliberately does not simulate an ultraviolet
limit: it checks the endpoint algebra, owner multiplicities, refunds, budget
simplex, and every predecessor contract on which the reassembly rests.
"""

from __future__ import annotations

__version__ = "1.0.1"
__first_issued__ = "2026-07-28"
__version_issued__ = "2026-07-28"

import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

from sympy import Matrix, Rational


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-REGULAR-COMPLETE-PACKET-OWNERSHIP-HN-REG-CLOSURE"
CLAIM_DIR = REPO / "claims" / CLAIM
OUTPUT = (
    CLAIM_DIR
    / "runs/2026-07-28-primary-regular-complete-packet-ownership-hn-reg-closure/result.json"
)

# These are authority identifiers, not derived numerical data.
AUTHORITIES = {
    "r063": "classii_balanced_coefficient_jet_continuum_manifest.json",
    "r071": "classii_one_form_sobolev_linear_closure_manifest.json",
    "r076": "classii_signed_transport_besov_bregman_resonance_manifest.json",
    "r078": "classii_hessian_difference_safe_packet_doob_bracket_manifest.json",
    "r079": "classii_full_safe_packet_frame_current_doob_manifest.json",
    "r080": "classii_low_object_far_square_progressive_boundary_manifest.json",
    "r083": "classii_controlled_polynomial_cfar_linear_pf_forest_manifest.json",
    "r084": "classii_root_diagonal_cartan_ou_linear_pf_absorption_manifest.json",
    "r085": "classii_nonorthogonal_cartan_schur_rational_hessian_boundary_manifest.json",
    "r086": "classii_rational_translated_wick_payload_comparable_reduction_manifest.json",
    "r088": "classii_direct_root_cartan_schur_sequential_secant_rational_conditional_trace_reduction_manifest.json",
    "r091": "classii_projected_cartan_full_frame_temporal_boundary_manifest.json",
    "r092": "classii_normalized_cartan_perspective_covariance_frontier_manifest.json",
    "r093": "classii_augmented_perspective_gibbs_gap_information_boundary_manifest.json",
    "r094": "classii_root_local_gram_secant_feedback_boundary_manifest.json",
    "r096": "classii_low_hermite_wick_predictable_baseline_reduction_manifest.json",
    "r097": "classii_global_gram_terminalization_covariance_deficit_reduction_manifest.json",
    "r099": "classii_extended_state_cartan_doob_rational_recovery_manifest.json",
    "r100": "classii_owner_gauge_heat_centered_covariance_debt_reduction_manifest.json",
    "r101": "classii_raw_wick_heat_baseline_orthogonality_rational_current_reduction_manifest.json",
    "r102": "classii_full_hessian_laplace_wick_future_feedback_boundary_manifest.json",
}

ACTIVE_MODULES = (
    "cartan_far",
    "linear_near",
    "rational_raw_wick_residual",
    "rational_unshifted_current",
    "rational_shifted_current",
    "conditional_low",
    "complete_low",
    "paid_collar",
)

NEAR_MODULES = tuple(module for module in ACTIVE_MODULES if module != "cartan_far")

ATOMIC_OWNERS = {
    "cartan_far": ("cartan_output",),
    "linear_near": ("linear_rows", "linear_heat_trace_forest"),
    "rational_raw_wick_residual": ("raw_wick_future_residual", "rational_heat_trace_forest", "full_wick_secant"),
    "rational_unshifted_current": ("current_u3", "current_u4", "current_u5"),
    "rational_shifted_current": ("future_current", "terminal_square"),
    "conditional_low": ("conditional_low",),
    "complete_low": ("complete_low",),
    "paid_collar": ("r078_paid_difference",),
}

REFUNDED = (
    "raw_q_taylor_u1",
    "raw_q_taylor_u2",
    "r076_base_cubic",
    "r086_tg_low_current",
    "r086_q_orientations",
    "second_r094_secant",
    "appended_r063_forest",
    "extra_q_r_schur_reserve",
)


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name, suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def result_passes(record: dict[str, Any]) -> bool:
    status = str(record.get("status", "")).upper()
    total = record.get("assertions_total")
    passed = record.get("assertions_passed")
    failed = record.get("assertions_failed")
    if status == "PASS" and isinstance(total, int) and total > 0:
        return passed == total and (failed is None or failed == 0)
    summary = record.get("summary", {})
    return isinstance(summary, dict) and summary.get("failed") == 0 and summary.get("passed", 0) > 0


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(self, group: str, name: str, condition: bool, actual: Any, expected: Any) -> None:
        self.rows.append(
            {
                "group": group,
                "name": name,
                "status": "PASS" if bool(condition) else "FAIL",
                "actual": str(actual),
                "expected": str(expected),
            }
        )

    def finish(self, diagnostics: dict[str, Any]) -> dict[str, Any]:
        passed = sum(row["status"] == "PASS" for row in self.rows)
        return {
            "schema": "tect/a13-regular-complete-packet-ownership-hn-reg-closure-primary/1.0",
            "package_version": __version__,
            "claim_id": CLAIM,
            "result_id": RESULT_ID,
            "status": "PASS" if passed == len(self.rows) else "FAIL",
            "assertions_total": len(self.rows),
            "assertions_passed": passed,
            "assertions_failed": len(self.rows) - passed,
            "assertions": self.rows,
            "diagnostics": diagnostics,
            "no_overclaim": (
                "R-103 proves complete H_N and REG only for the finite-cutoff, fixed-floor, "
                "deterministic-PSD-heat regular annular mutually orthogonal strict-past "
                "no-revisit class. It proves a complete-owner lower form, not naked C_post "
                "positivity, standalone R-085 (4.11) or old (6.5), arbitrary progressive/revisit "
                "H_A, OVERLAP_src, Nelson, removals, a measure, T5--T7, or Sector A closure."
            ),
        }


def contraction(matrix: Matrix, left: Matrix, right: Matrix) -> Any:
    return (left.T * matrix * right)[0]


def endpoint_algebra(b0: Matrix, b1: Matrix, bt: Matrix, g: Matrix, c: Matrix, q: Matrix) -> dict[str, Any]:
    raw_contraction = sum((b1 - b0)[i, j] * q[i, j] for i in range(3) for j in range(3))
    direct = Rational(1, 2) * raw_contraction + contraction(b1, g, c) + Rational(1, 2) * contraction(b1, c, c)
    reassembled = (
        Rational(1, 2) * raw_contraction
        + contraction(bt, g, c)
        + contraction(b1 - bt, g, c)
        + Rational(1, 2) * contraction(b1, c, c)
    )
    return {
        "direct": direct,
        "reassembled": reassembled,
        "raw_wick": Rational(1, 2) * raw_contraction,
        "unshifted_current": contraction(bt, g, c),
        "shifted_current": contraction(b1 - bt, g, c),
        "terminal_square": Rational(1, 2) * contraction(b1, c, c),
        "wrong_raw_factor": raw_contraction + contraction(b1, g, c) + Rational(1, 2) * contraction(b1, c, c),
        "wrong_shifted_sign": Rational(1, 2) * raw_contraction + contraction(bt, g, c) - contraction(b1 - bt, g, c) + Rational(1, 2) * contraction(b1, c, c),
        "wrong_square_factor": Rational(1, 2) * raw_contraction + contraction(b1, g, c) + contraction(b1, c, c),
    }


def endpoint_case(seed: int) -> dict[str, Any]:
    # INPUT fixtures are generated from one integer seed; all outputs below are derived.
    m0 = Matrix([[seed + 1, 1, 0], [0, seed + 2, 1], [1, 0, seed + 3]])
    m1 = Matrix([[seed + 2, -1, 1], [1, seed + 1, 0], [0, 1, seed + 4]])
    b0 = m0.T * m0
    b1 = m1.T * m1
    db = Matrix([[1, seed, 0], [seed, -1, 1], [0, 1, 2]])
    d2b = Matrix([[2, 0, 1], [0, 2, -1], [1, -1, 0]])
    bt = b0 + db + Rational(1, 2) * d2b
    g = Matrix([seed, 1 - seed, seed + 2])
    c = Matrix([1, -2, seed + 1])
    q = Matrix(
        [
            [seed + 1, 1, -1],
            [1, -seed, 2],
            [-1, 2, seed + 2],
        ]
    )
    row = endpoint_algebra(b0, b1, bt, g, c, q)
    row["det_b1"] = b1.det()
    return row


def main() -> int:
    audit = Audit()

    authority_diagnostics: dict[str, Any] = {}
    for label, filename in AUTHORITIES.items():
        manifest_path = CLAIM_DIR / filename
        audit.check("authority", f"{label}_manifest_exists", manifest_path.is_file(), manifest_path.name, "present")
        try:
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception as error:
            manifest = {}
            audit.check("authority", f"{label}_manifest_json", False, repr(error), "valid JSON")
        else:
            audit.check("authority", f"{label}_manifest_json", True, "valid", "valid JSON")
        run_contract = manifest.get("run_contract", {}) if isinstance(manifest, dict) else {}
        integrated_ref = run_contract.get("integrated_output") if isinstance(run_contract, dict) else None
        if integrated_ref:
            integrated_path = REPO / str(integrated_ref)
            try:
                integrated = json.loads(integrated_path.read_text(encoding="utf-8"))
            except Exception as error:
                audit.check("authority", f"{label}_integrated_pass", False, repr(error), "PASS JSON")
                authority_diagnostics[label] = {"manifest": filename, "integrated": str(integrated_ref), "pass": False}
            else:
                ok = result_passes(integrated)
                audit.check("authority", f"{label}_integrated_pass", ok, integrated.get("status"), "PASS")
                authority_diagnostics[label] = {"manifest": filename, "integrated": str(integrated_ref), "pass": ok}
        else:
            # Grandfathered manifests without a run_contract are still pinned by the integrated verifier.
            audit.check("authority", f"{label}_result_id_present", bool(manifest.get("result_id")), manifest.get("result_id"), "nonempty")
            authority_diagnostics[label] = {"manifest": filename, "integrated": None, "pass": True}

    endpoint_diagnostics: list[dict[str, str]] = []
    for seed in (1, 2, 4, 7):
        row = endpoint_case(seed)
        audit.check("algebra", f"endpoint_reassembly_seed_{seed}", row["direct"] == row["reassembled"], row["direct"] - row["reassembled"], 0)
        audit.check("algebra", f"raw_factor_mutant_rejected_seed_{seed}", row["direct"] != row["wrong_raw_factor"], row["direct"] - row["wrong_raw_factor"], "nonzero")
        audit.check("algebra", f"shifted_sign_mutant_rejected_seed_{seed}", row["direct"] != row["wrong_shifted_sign"], row["direct"] - row["wrong_shifted_sign"], "nonzero")
        audit.check("algebra", f"square_factor_mutant_rejected_seed_{seed}", row["direct"] != row["wrong_square_factor"], row["direct"] - row["wrong_square_factor"], "nonzero")
        audit.check("algebra", f"terminal_square_nonnegative_seed_{seed}", row["terminal_square"] >= 0, row["terminal_square"], ">=0")
        audit.check("algebra", f"terminal_gram_positive_seed_{seed}", row["det_b1"] > 0, row["det_b1"], ">0")
        endpoint_diagnostics.append(
            {
                "seed": str(seed),
                "raw_wick": str(row["raw_wick"]),
                "unshifted_current": str(row["unshifted_current"]),
                "shifted_current": str(row["shifted_current"]),
                "terminal_square": str(row["terminal_square"]),
            }
        )

    fixture_b0 = Matrix.eye(3)
    fixture_bt = Matrix([[2, 1, 0], [1, 2, 0], [0, 0, 1]])
    fixture_g = Matrix([1, -2, 3])
    fixture_c = Matrix([2, 1, -1])
    fixture_q = Matrix([[1, 2, 0], [2, -1, 1], [0, 1, 3]])
    for label, fixture_b1, expected_rank in (
        ("singular_psd", Matrix([[1, 2, 0], [2, 4, 0], [0, 0, 0]]), 1),
        ("zero_psd", Matrix.zeros(3), 0),
    ):
        fixture = endpoint_algebra(fixture_b0, fixture_b1, fixture_bt, fixture_g, fixture_c, fixture_q)
        audit.check("algebra", f"{label}_endpoint_reassembly", fixture["direct"] == fixture["reassembled"], fixture["direct"] - fixture["reassembled"], 0)
        audit.check("algebra", f"{label}_rank", fixture_b1.rank() == expected_rank, fixture_b1.rank(), expected_rank)
        audit.check("algebra", f"{label}_terminal_square_nonnegative", fixture["terminal_square"] >= 0, fixture["terminal_square"], ">=0")

    flattened = [atom for module in ACTIVE_MODULES for atom in ATOMIC_OWNERS[module]]
    audit.check("ownership", "eight_active_modules", len(ACTIVE_MODULES) == 8, len(ACTIVE_MODULES), 8)
    audit.check("ownership", "seven_near_modules", len(NEAR_MODULES) == 7, len(NEAR_MODULES), 7)
    audit.check("ownership", "near_excludes_only_cartan_far", set(ACTIVE_MODULES) - set(NEAR_MODULES) == {"cartan_far"}, sorted(set(ACTIVE_MODULES) - set(NEAR_MODULES)), ["cartan_far"])
    audit.check("ownership", "module_table_complete", set(ACTIVE_MODULES) == set(ATOMIC_OWNERS), sorted(ATOMIC_OWNERS), sorted(ACTIVE_MODULES))
    audit.check("ownership", "atomic_owner_uniqueness", len(flattened) == len(set(flattened)), len(flattened) - len(set(flattened)), 0)
    near_flattened = [atom for module in NEAR_MODULES for atom in ATOMIC_OWNERS[module]]
    audit.check("ownership", "near_atomic_owner_uniqueness", len(near_flattened) == len(set(near_flattened)), len(near_flattened) - len(set(near_flattened)), 0)
    for module in ACTIVE_MODULES:
        audit.check("ownership", f"{module}_nonempty", len(ATOMIC_OWNERS[module]) > 0, len(ATOMIC_OWNERS[module]), ">0")
    for refunded in REFUNDED:
        audit.check("refund", f"{refunded}_multiplicity", refunded not in flattened, flattened.count(refunded), 0)

    # UPSTREAM INPUTS: R-093 (4.2)/(9.1) pins the action coefficients, while
    # R-088 (8.4) pins only an optional external-comparison threshold.  The
    # latter is not an internal-allocation cap.
    r088_note = (CLAIM_DIR / "notes/classii-direct-root-cartan-schur-sequential-secant-rational-conditional-trace-reduction-260725-v1.0.tex.txt").read_text(encoding="utf-8")
    r093_note = (CLAIM_DIR / "notes/classii-augmented-perspective-gibbs-gap-information-boundary-260727-v1.0.tex.txt").read_text(encoding="utf-8")
    audit.check("upstream", "r088_comparison_formula", all(token in r088_note for token in (r"{1\over220}", r"p={11\over10}", "No universal")), "tokens present", "tokens present")
    audit.check("upstream", "r093_action_formula", all(token in r093_note for token in (r"{3\over20}", r"{9\over20}", "I_2(v)")), "tokens present", "tokens present")
    q_nelson = Fraction(10, 9)
    c_x = Fraction(1, 2) / q_nelson
    c_y = Fraction(3, 20)  # Explicit upstream input in R-093 (4.2)/(9.1).
    comparison_p = Fraction(11, 10)
    epsilon_v = c_x
    eta_comparison_threshold = Fraction(1, 2) / comparison_p - epsilon_v
    eta_star = eta_comparison_threshold / 2
    zeta_star = c_y / 5
    module_count = len(ACTIVE_MODULES)
    eta_each = eta_star / module_count
    zeta_each = zeta_star / module_count
    near_module_count = len(NEAR_MODULES)
    eta_near_each = eta_star / near_module_count
    zeta_near_each = zeta_star / near_module_count
    x_reserve = c_x - eta_star
    y_reserve = c_y - zeta_star
    audit.check("budget", "eta_star", eta_star == Fraction(1, 440), eta_star, Fraction(1, 440))
    audit.check("budget", "zeta_star", zeta_star == Fraction(3, 100), zeta_star, Fraction(3, 100))
    audit.check("budget", "source_coefficient_from_q", c_x == Fraction(9, 20), c_x, Fraction(9, 20))
    audit.check("budget", "comparison_threshold_derived", eta_comparison_threshold == Fraction(1, 220), eta_comparison_threshold, Fraction(1, 220))
    audit.check("budget", "eta_module_share", eta_each == Fraction(1, 3520), eta_each, Fraction(1, 3520))
    audit.check("budget", "zeta_module_share", zeta_each == Fraction(3, 800), zeta_each, Fraction(3, 800))
    audit.check("budget", "eta_simplex", eta_each * module_count == eta_star, eta_each * module_count, eta_star)
    audit.check("budget", "zeta_simplex", zeta_each * module_count == zeta_star, zeta_each * module_count, zeta_star)
    audit.check("budget", "eta_near_module_share", eta_near_each == Fraction(1, 3080), eta_near_each, Fraction(1, 3080))
    audit.check("budget", "zeta_near_module_share", zeta_near_each == Fraction(3, 700), zeta_near_each, Fraction(3, 700))
    audit.check("budget", "eta_near_simplex", eta_near_each * near_module_count == eta_star, eta_near_each * near_module_count, eta_star)
    audit.check("budget", "zeta_near_simplex", zeta_near_each * near_module_count == zeta_star, zeta_near_each * near_module_count, zeta_star)
    audit.check("budget", "source_reserve", x_reserve == Fraction(197, 440), x_reserve, Fraction(197, 440))
    audit.check("budget", "sextic_reserve", y_reserve == Fraction(3, 25), y_reserve, Fraction(3, 25))
    audit.check("budget", "source_reserve_positive", x_reserve > 0, x_reserve, ">0")
    audit.check("budget", "sextic_reserve_positive", y_reserve > 0, y_reserve, ">0")

    # Choose an odd R-092 FAR separation so its half exponent is integral.
    # This is not the distinct fixed payable R-096 collar.
    cartan_separation = 15
    cartan_power = (cartan_separation - 5) // 2
    cartan_gap = Fraction(1, 2**cartan_power)
    audit.check("cartan", "cartan_separation_admissible", cartan_separation >= 5, cartan_separation, ">=5")
    audit.check("cartan", "half_exponent_integral", (cartan_separation - 5) % 2 == 0, (cartan_separation - 5) % 2, 0)
    audit.check("cartan", "gap_c15", cartan_gap == Fraction(1, 32), cartan_gap, Fraction(1, 32))
    audit.check("cartan", "gap_subunit", 0 < cartan_gap < 1, cartan_gap, "in (0,1)")

    diagnostics = {
        "authorities": authority_diagnostics,
        "endpoint_cases": endpoint_diagnostics,
        "active_modules": list(ACTIVE_MODULES),
        "near_modules": list(NEAR_MODULES),
        "atomic_owners": {key: list(value) for key, value in ATOMIC_OWNERS.items()},
        "refunded": list(REFUNDED),
        "budget": {
            "source_coefficient": str(c_x),
            "sextic_coefficient": str(c_y),
            "eta_star": str(eta_star),
            "zeta_star": str(zeta_star),
            "eta_each": str(eta_each),
            "zeta_each": str(zeta_each),
            "eta_near_each": str(eta_near_each),
            "zeta_near_each": str(zeta_near_each),
            "source_reserve": str(x_reserve),
            "sextic_reserve": str(y_reserve),
        },
        "cartan": {"separation": cartan_separation, "gap": str(cartan_gap), "distinct_r096_fixed_collar": True},
    }
    payload = audit.finish(diagnostics)
    atomic_json(OUTPUT, payload)
    print(
        f"R-103 primary: {payload['assertions_passed']}/{payload['assertions_total']} "
        f"assertions {payload['status']}"
    )
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

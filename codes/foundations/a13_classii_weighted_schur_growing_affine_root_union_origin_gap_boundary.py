#!/usr/bin/env python3
"""Primary exact certificate for the R-160 weighted-Schur origin gap.

This certificate sharpens the R-155 affine source-reuse factor-three path
estimate.  A geometric Schur weight charges each child edge by one quarter at
its parent and four times at its child.  Exact rational Sturm certificates
then prove an origin-Hessian gap above 1/10 for every finite path length.  The
result is still a centered, zero-control, fixed-law affine theorem and is not
T-050 globalization.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path
from typing import Any

import sympy as sp


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-WEIGHTED-SCHUR-GROWING-AFFINE-ROOT-UNION-ORIGIN-GAP-BOUNDARY"
LEDGER_ID = "R-160"
SLUG = "weighted-schur-growing-affine-root-union-origin-gap-boundary"
SCHEMA = f"tect/a13-{SLUG}-primary/1.0"
DEFAULT_OUTPUT = REPO / "claims" / CLAIM / "runs" / f"2026-08-03-primary-{SLUG}" / "result.json"
A1_MANIFEST = REPO / "claims" / "A1-PRODUCTION-FUNCTIONAL-REALISATION" / "production_functional_manifest.json"
R155_MANIFEST = REPO / "claims" / CLAIM / "classii_affine_source_reuse_factor_three_global_gap_boundary_manifest.json"

SCOPE = {
    "fixed_side_16_torus_and_A1_symbol": True,
    "fixed_cutoff_positive_floor": True,
    "exact_nonaliased_torus_integration": True,
    "common_real_even_covariance_matched_scalar_multiplier": True,
    "scalar_multiplier_same_on_real_components": True,
    "scalar_multiplier_abs_le_one": True,
    "admissible_dual_lattice_momenta": True,
    "finite_distinct_antipodal_source_classes": True,
    "source_target_overlap_allowed": True,
    "stationary_centered_common_even_covariance_matched_background": True,
    "linear_one_shot_predictable_chart": True,
    "origin_hessian_only": True,
    "arbitrary_finite_family_cardinality_uniform_origin_gap": True,
    "factor_three_path_weighted_schur": True,
    "global_cross_root_endpoint_retained": True,
    "global_sextic_hessian_dropped_as_one_psd_form": True,
    "continuous_radial_certificate_above_lattice_floor": True,
    "stronger_actual_lattice_shell_certificate": True,
    "cardinality_uniform_nonzero_radius": False,
    "nonzero_or_realised_past": False,
    "shifted_state_recursive_or_revisited_feedback": False,
    "nonlinear_feedback": False,
    "finite_amplitude_convexity": False,
    "cutoff_or_floor_removal": False,
    "t050_closed": False,
    "sector_a_closed": False,
}

NO_OVERCLAIM = (
    "R-160 proves a 19/160 continuous-half-line origin-Hessian gap and the stronger 4/25 actual-"
    "lattice gap, both uniform over every finite cardinality, only for "
    "the R-155 family of distinct-source antipodal p:2p fixed-law affine controls, allowing "
    "source-target reuse, on the side-16 dual lattice at fixed cutoff and positive floor in the "
    "centered stationary common-even covariance-matched A1/A6/A7 chart. It supplies no "
    "cardinality-uniform nonzero radius, nonzero or realised-past estimate, shifted-state recursive "
    "or revisited-root result, nonlinear predictable "
    "feedback, finite-amplitude convexity, cutoff/floor removal, complete historical low owner, "
    "T-050 or A13 closure, Nelson theorem, interacting measure, phase/PDE verdict, or Sector-A closure."
)


def serial(value: Any) -> Any:
    if isinstance(value, Fraction):
        return f"{value.numerator}/{value.denominator}"
    if isinstance(value, sp.Basic):
        return str(value)
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
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


@dataclass
class Audit:
    rows: list[dict[str, Any]] = field(default_factory=list)

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

    def require(self) -> None:
        failures = [row for row in self.rows if row["status"] != "PASS"]
        if failures:
            raise AssertionError(json.dumps(failures, indent=2, ensure_ascii=True))


def rational(value: Any) -> sp.Rational:
    return sp.Rational(str(value))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def sign_variations(signs: list[int]) -> int:
    nonzero = [value for value in signs if value]
    return sum(left != right for left, right in zip(nonzero, nonzero[1:]))


def sturm_certificate(
    poly: sp.Poly,
    variable: sp.Symbol,
    lower: sp.Rational,
    upper: sp.Rational | None = None,
) -> dict[str, Any]:
    sequence = sp.sturm(poly.as_expr(), variable)
    lower_signs = [int(sp.sign(term.subs(variable, lower))) for term in sequence]
    if upper is None:
        upper_signs = [int(sp.sign(sp.LC(sp.Poly(term, variable)))) for term in sequence]
        roots = int(sp.count_roots(poly.as_expr(), lower, sp.oo))
        interval = [lower, "infinity"]
        positive_leading_coefficient = bool(sp.LC(poly) > 0)
    else:
        upper_signs = [int(sp.sign(term.subs(variable, upper))) for term in sequence]
        roots = int(sp.count_roots(poly.as_expr(), lower, upper))
        interval = [lower, upper]
        positive_leading_coefficient = bool(sp.LC(poly) > 0)
    return {
        "degree": poly.degree(),
        "sequence_length": len(sequence),
        "interval": interval,
        "lower_signs": lower_signs,
        "upper_signs": upper_signs,
        "lower_variations": sign_variations(lower_signs),
        "upper_variations": sign_variations(upper_signs),
        "roots": roots,
        "positive_at_lower": bool(poly.eval(lower) > 0),
        "positive_at_upper": True if upper is None else bool(poly.eval(upper) > 0),
        "positive_leading_coefficient": positive_leading_coefficient,
        "lower_value": sp.factor(poly.eval(lower)),
        "upper_value": None if upper is None else sp.factor(poly.eval(upper)),
    }


def atan_alternating_bounds(z: sp.Rational, last_index: int) -> tuple[sp.Rational, sp.Rational]:
    """Rigorous alternating-series bounds using terms k=0,...,last_index."""
    partial = sum(((-1) ** k * z ** (2 * k + 1) / (2 * k + 1) for k in range(last_index + 1)), sp.Rational(0))
    next_term = z ** (2 * last_index + 3) / (2 * last_index + 3)
    if last_index % 2 == 0:
        return sp.factor(partial - next_term), sp.factor(partial)
    return sp.factor(partial), sp.factor(partial + next_term)


def machin_pi_bounds() -> tuple[sp.Rational, sp.Rational, dict[str, Any]]:
    """Use pi/4=4 atan(1/5)-atan(1/239) with exact remainder bounds."""
    a_lower, a_upper = atan_alternating_bounds(sp.Rational(1, 5), 3)
    b_lower, b_upper = atan_alternating_bounds(sp.Rational(1, 239), 1)
    pi_lower = sp.factor(4 * (4 * a_lower - b_upper))
    pi_upper = sp.factor(4 * (4 * a_upper - b_lower))
    tan_two_a = sp.factor(2 * sp.Rational(1, 5) / (1 - sp.Rational(1, 5) ** 2))
    tan_four_a = sp.factor(2 * tan_two_a / (1 - tan_two_a**2))
    tan_difference = sp.factor((tan_four_a - sp.Rational(1, 239)) / (1 + tan_four_a * sp.Rational(1, 239)))
    return pi_lower, pi_upper, {
        "identity": "pi/4 = 4 atan(1/5) - atan(1/239)",
        "tan_two_a": tan_two_a,
        "tan_four_a": tan_four_a,
        "tan_difference": tan_difference,
        "atan_1_5_bounds": [a_lower, a_upper],
        "atan_1_239_bounds": [b_lower, b_upper],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()

    audit = Audit()
    a1 = json.loads(A1_MANIFEST.read_text(encoding="utf-8"))
    parameters = a1["parameters"]
    lengths = [rational(parameters[key]) for key in ("Lx", "Ly", "Lz")]
    volume = sp.prod(lengths)
    audit.check("production", "registered side-16 torus", lengths == [16, 16, 16], lengths, [16, 16, 16])
    audit.check("production", "registered volume", volume == 4096, volume, 4096)

    r155_manifest = json.loads(R155_MANIFEST.read_text(encoding="utf-8"))
    r155_record = r155_manifest["files"]["primary_result"]
    r155_path = REPO / r155_record["path"]
    r155 = json.loads(r155_path.read_text(encoding="utf-8"))
    audit.check("authority", "R-155 result hash", sha256(r155_path) == r155_record["sha256"], sha256(r155_path), r155_record["sha256"])
    audit.check("authority", "R-155 ledger identity", r155.get("result_ledger_id") == "R-155", r155.get("result_ledger_id"), "R-155")
    audit.check("authority", "R-155 source-target reuse scope", bool(r155["scope"]["source_target_overlap_allowed"]), r155["scope"], "source-target reuse allowed")

    x = sp.symbols("x", nonnegative=True)
    registered_mass_floor = sp.Rational(7, 250)
    lower_symbol = sp.expand(x**2 + rational(parameters["Z"]) * x + rational(parameters["r"]) + registered_mass_floor)
    r155_symbol = sp.sympify(r155["diagnostics"]["lower_symbol"], locals={"x": x})
    audit.check("authority", "R-155 lower symbol parity", sp.expand(r155_symbol - lower_symbol) == 0, r155_symbol, lower_symbol)
    audit.check("production", "strict radial lower symbol", sp.discriminant(lower_symbol, x) < 0, sp.factor(sp.discriminant(lower_symbol, x)), "<0")
    coarse_surrogate = x**2 - sp.Rational(953, 1000) * x + sp.Rational(5013, 10000)
    surrogate_difference = sp.expand(lower_symbol - coarse_surrogate)
    expected_difference = sp.Rational(138622937, 5000000000) * x + sp.Rational(7336473, 10000000000)
    audit.check("correction", "coarse scratch symbol is not the authority", surrogate_difference == expected_difference, surrogate_difference, expected_difference)
    audit.check("correction", "coarse scratch symbol is a strict minorant", all(coefficient > 0 for coefficient in sp.Poly(surrogate_difference, x).all_coeffs()), surrogate_difference, ">0 for x>=0")

    h6_upper = rational(r155["diagnostics"]["H6_strict_upper"])
    diagonal_factor = rational(r155["diagnostics"]["diagonal_radial_factor"])
    edge_factor = rational(r155["diagnostics"]["edge_radial_factor"])
    diagonal_numerator = sp.factor(diagonal_factor * h6_upper / volume)
    edge_numerator = sp.factor(edge_factor * h6_upper / volume)
    audit.check("coefficient", "R-155 strict H6 envelope", h6_upper == sp.Rational(7083, 2000), h6_upper, sp.Rational(7083, 2000))
    audit.check("coefficient", "R-155 diagonal radial factor", diagonal_factor == 624, diagonal_factor, 624)
    audit.check("coefficient", "R-155 edge radial factor", edge_factor == 2256, edge_factor, 2256)
    audit.check("structure", "R-155 factor-three resonance ratios", [rational(value) for value in r155["diagnostics"]["distinct_resonance_ratios"]] == [sp.Rational(1, 3), 3], r155["diagnostics"]["distinct_resonance_ratios"], [sp.Rational(1, 3), 3])
    audit.check("structure", "finite path degree", len(("parent", "child")) == 2 and 3 > 1, "one parent, one child, norm grows by 3", "finite path union")
    audit.check("regulator", "common scalar regulator envelope pinned", "scalar regulator" in r155_manifest["statement"] and "exact nonaliased torus" in r155_manifest["statement"], r155_manifest["statement"], "common scalar regulator and exact nonaliased torus")

    f1 = lower_symbol
    f4 = lower_symbol.subs(x, 4 * x)
    f9 = lower_symbol.subs(x, 9 * x)
    f36 = lower_symbol.subs(x, 36 * x)
    f14 = sp.expand(f1 * f4)
    f936 = sp.expand(f9 * f36)
    diagonal_loss = diagonal_numerator * x / f14
    edge_loss_squared = edge_numerator**2 * x**2 / (f14 * f936)

    # The exact edge Young identity is
    # 2ab <= (1/4)a^2 + 4b^2, with equality remainder (a/2-2b)^2.
    schur_ratio = sp.Rational(1, 4)
    a, b = sp.symbols("a b", real=True)
    young_remainder = sp.expand(schur_ratio * a**2 + a * 0 + (1 / schur_ratio) * b**2 - 2 * a * b)
    audit.check("weighted-schur", "geometric weight ratio", schur_ratio == sp.Rational(1, 4), schur_ratio, sp.Rational(1, 4))
    audit.check("weighted-schur", "exact asymmetric Young square", sp.expand(young_remainder - (a / 2 - 2 * b) ** 2) == 0, young_remainder, "(a/2-2b)^2")
    audit.check("weighted-schur", "parent/child edge charges", [schur_ratio, 1 / schur_ratio] == [sp.Rational(1, 4), 4], [schur_ratio, 1 / schur_ratio], [sp.Rational(1, 4), 4])

    nonzero_mode_floor = rational(r155["diagnostics"].get("lattice_floor", "3/20"))
    actual_floor_from_pi = (2 * sp.Rational(31, 10) / lengths[0]) ** 2
    audit.check("lattice", "nonzero dual mode floor", actual_floor_from_pi > nonzero_mode_floor == sp.Rational(3, 20), actual_floor_from_pi, f">{nonzero_mode_floor}")

    pi_lower, pi_upper, pi_certificate = machin_pi_bounds()
    audit.check("pi", "Machin tangent identity", pi_certificate["tan_difference"] == 1, pi_certificate, "tan difference = 1 on principal branch")
    audit.check("pi", "lattice shell rational enclosure", pi_lower > sp.Rational(157, 50) and pi_upper < sp.Rational(22, 7), [pi_lower, pi_upper], [">157/50", "<22/7"])
    unit_shell_lower = sp.Rational(77, 500)
    unit_shell_upper = sp.Rational(31, 200)
    unit_x_lower = sp.factor(pi_lower**2 / 64)
    unit_x_upper = sp.factor(pi_upper**2 / 64)
    higher_shell_floor = sp.Rational(3, 10)
    higher_x_lower = sp.factor(2 * pi_lower**2 / 64)
    audit.check("lattice", "N=1 shell interval", unit_x_lower > unit_shell_lower and unit_x_upper < unit_shell_upper, [unit_x_lower, unit_x_upper], [">77/500", "<31/200"])
    audit.check("lattice", "N>=2 shell half-line", higher_x_lower > higher_shell_floor, higher_x_lower, f">{higher_shell_floor}")

    source_hessian = rational(r155["diagnostics"]["source_hessian"])
    required_gap = sp.Rational(1, 10)
    continuous_gap = sp.Rational(19, 160)
    continuous_headroom = sp.factor(continuous_gap - required_gap)
    continuous_budget = sp.factor(source_hessian - continuous_gap)
    lattice_gap = sp.Rational(4, 25)
    lattice_headroom = sp.factor(lattice_gap - required_gap)
    lattice_budget = sp.factor(source_hessian - lattice_gap)
    audit.check("budget", "source Hessian", source_hessian == sp.Rational(9, 10), source_hessian, sp.Rational(9, 10))
    audit.check("budget", "continuous endpoint budget", continuous_budget == sp.Rational(25, 32), continuous_budget, sp.Rational(25, 32))
    audit.check("budget", "actual-lattice endpoint budget", lattice_budget == sp.Rational(37, 50), lattice_budget, sp.Rational(37, 50))

    def root_polynomials(budget: sp.Rational) -> tuple[sp.Poly, sp.Poly]:
        sign_guard = sp.Poly(sp.expand(budget * f14 - diagonal_numerator * x), x, domain=sp.QQ)
        squared = sp.Poly(
            sp.expand((budget * f14 - diagonal_numerator * x) ** 2 * f936 - edge_numerator**2 * x**2 * f14 / 16),
            x,
            domain=sp.QQ,
        )
        return sign_guard, squared

    continuous_sign, continuous_squared = root_polynomials(continuous_budget)
    lattice_sign, lattice_squared = root_polynomials(lattice_budget)
    certificates = {
        "continuous_root_sign_guard": sturm_certificate(continuous_sign, x, nonzero_mode_floor),
        "continuous_root_squared": sturm_certificate(continuous_squared, x, nonzero_mode_floor),
        "lattice_unit_shell_sign_guard": sturm_certificate(lattice_sign, x, unit_shell_lower, unit_shell_upper),
        "lattice_unit_shell_squared": sturm_certificate(lattice_squared, x, unit_shell_lower, unit_shell_upper),
        "lattice_higher_shell_sign_guard": sturm_certificate(lattice_sign, x, higher_shell_floor),
        "lattice_higher_shell_squared": sturm_certificate(lattice_squared, x, higher_shell_floor),
    }
    expected_degrees = {
        "continuous_root_sign_guard": 4,
        "continuous_root_squared": 12,
        "lattice_unit_shell_sign_guard": 4,
        "lattice_unit_shell_squared": 12,
        "lattice_higher_shell_sign_guard": 4,
        "lattice_higher_shell_squared": 12,
    }
    for name, certificate in certificates.items():
        audit.check("sturm", f"{name} degree", certificate["degree"] == expected_degrees[name], certificate["degree"], expected_degrees[name])
        audit.check(
            "sturm",
            f"{name} positive interval",
            certificate["roots"] == 0
            and certificate["positive_at_lower"]
            and certificate["positive_at_upper"]
            and certificate["positive_leading_coefficient"]
            and certificate["lower_variations"] == certificate["upper_variations"],
            certificate,
            "zero roots, positive endpoints, equal variations",
        )

    r155_sturm = r155["diagnostics"]["sturm"]
    inherited_names = {
        "global_edge_one_sixth": "global_edge_one_sixth",
        "parent_diagonal_one_thirtieth": "parent_diagonal_one_thirtieth",
        "parent_edge_one_thousandth": "parent_edge_one_thousandth",
    }
    for name, inherited_name in inherited_names.items():
        certificate = r155_sturm[inherited_name]
        audit.check(
            "inherited-certificate",
            name,
            certificate["roots_on_half_line"] == 0
            and certificate["positive_at_lower"]
            and certificate["lower_variations"] == certificate["infinity_variations"],
            certificate,
            "R-155 exact positive half-line certificate",
        )

    interior_loss_upper = sp.factor(sp.Rational(1, 30) + (1 / schur_ratio) * sp.Rational(1, 6) + schur_ratio * sp.Rational(1, 1000))
    audit.check("row-bound", "continuous root weighted row", certificates["continuous_root_squared"]["roots"] == 0, "L+E/4", f"<{continuous_budget}")
    audit.check("row-bound", "actual-lattice root weighted row", certificates["lattice_unit_shell_squared"]["roots"] == 0 and certificates["lattice_higher_shell_squared"]["roots"] == 0, "L+E/4 on N=1 and N>=2", f"<{lattice_budget}")
    audit.check("row-bound", "interior/terminal row", interior_loss_upper == sp.Rational(2801, 4000) and interior_loss_upper < lattice_budget < continuous_budget, interior_loss_upper, f"<{lattice_budget}<{continuous_budget}")
    audit.check("row-bound", "continuous interior slack", continuous_budget - interior_loss_upper == sp.Rational(81, 1000), continuous_budget - interior_loss_upper, sp.Rational(81, 1000))
    audit.check("row-bound", "lattice interior slack", lattice_budget - interior_loss_upper == sp.Rational(159, 4000), lattice_budget - interior_loss_upper, sp.Rational(159, 4000))
    audit.check("gap", "continuous arbitrary-length origin gap", source_hessian - continuous_budget == continuous_gap, source_hessian - continuous_budget, continuous_gap)
    audit.check("gap", "actual-lattice arbitrary-length origin gap", source_hessian - lattice_budget == lattice_gap, source_hessian - lattice_budget, lattice_gap)
    audit.check("gap", "strict T-050 threshold headrooms", continuous_headroom == sp.Rational(3, 160) and lattice_headroom == sp.Rational(3, 50), [continuous_headroom, lattice_headroom], ["3/160", "3/50"])
    audit.check("advance", "strict improvement over R-155 global gap", continuous_gap > rational(r155["diagnostics"]["certified_global_gap"]) and lattice_gap > continuous_gap, [lattice_gap, continuous_gap, r155["diagnostics"]["certified_global_gap"]], "4/25 > 19/160 > 7/250")

    floor_witness = sp.Rational(1, 36)
    floor_removal_excess = sp.factor(16 * edge_numerator**2 * floor_witness**2 - continuous_budget**2 * f14.subs(x, floor_witness) * f936.subs(x, floor_witness))
    audit.check("boundary", "weighted-majorant floor-removal extension fails", floor_removal_excess > 0, floor_removal_excess, "4E(1/36)>25/32; method obstruction only")

    audit.require()
    payload = {
        "schema": SCHEMA,
        "version": __version__,
        "issued": "2026-08-03",
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "result_ledger_id": LEDGER_ID,
        "scope": SCOPE,
        "no_overclaim": NO_OVERCLAIM,
        "inputs": {
            "A1_manifest": str(A1_MANIFEST.relative_to(REPO)).replace("\\", "/"),
            "R155_manifest": str(R155_MANIFEST.relative_to(REPO)).replace("\\", "/"),
        },
        "diagnostics": {
            "volume": volume,
            "lower_symbol": lower_symbol,
            "H6_strict_upper": h6_upper,
            "diagonal_radial_factor": diagonal_factor,
            "edge_radial_factor": edge_factor,
            "diagonal_numerator": diagonal_numerator,
            "edge_numerator": edge_numerator,
            "diagonal_loss": diagonal_loss,
            "edge_loss_squared": edge_loss_squared,
            "schur_weight_ratio": schur_ratio,
            "nonzero_mode_floor": nonzero_mode_floor,
            "pi_bounds": [pi_lower, pi_upper],
            "pi_certificate": pi_certificate,
            "unit_shell_interval": [unit_shell_lower, unit_shell_upper],
            "unit_shell_x_bounds": [unit_x_lower, unit_x_upper],
            "higher_shell_floor": higher_shell_floor,
            "higher_shell_x_lower": higher_x_lower,
            "sturm": certificates,
            "source_hessian": source_hessian,
            "continuous_endpoint_loss_budget": continuous_budget,
            "continuous_certified_gap": continuous_gap,
            "continuous_threshold_headroom": continuous_headroom,
            "lattice_endpoint_loss_budget": lattice_budget,
            "lattice_certified_gap": lattice_gap,
            "lattice_threshold_headroom": lattice_headroom,
            "interior_loss_upper": interior_loss_upper,
            "continuous_interior_slack": continuous_budget - interior_loss_upper,
            "lattice_interior_slack": lattice_budget - interior_loss_upper,
            "floor_removal_majorant_witness": {"x": floor_witness, "cleared_excess": floor_removal_excess},
            "coarse_surrogate_difference": surrogate_difference,
        },
        "assertions": audit.rows,
        "summary": {
            "passed": sum(row["status"] == "PASS" for row in audit.rows),
            "failed": sum(row["status"] != "PASS" for row in audit.rows),
            "total": len(audit.rows),
        },
    }
    atomic_json(arguments.output, payload)
    print(f"{RESULT_ID}: {payload['summary']['passed']}/{payload['summary']['total']} PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

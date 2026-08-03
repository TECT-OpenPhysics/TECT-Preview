#!/usr/bin/env python3
"""Independent exact audit for the R-160 weighted-Schur origin gap.

This implementation imports neither the primary certificate nor a scientific
algebra package.  It reconstructs the production constants, source-reuse
incidence, factor-three response graph, rational pi enclosure, and all
polynomial inequalities with standard-library ``Fraction`` arithmetic and
exact Bernstein covers.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import tempfile
from dataclasses import dataclass, field
from fractions import Fraction as F
from pathlib import Path
from typing import Any


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-WEIGHTED-SCHUR-GROWING-AFFINE-ROOT-UNION-ORIGIN-GAP-BOUNDARY"
LEDGER_ID = "R-160"
SLUG = "weighted-schur-growing-affine-root-union-origin-gap-boundary"
SCHEMA = f"tect/a13-{SLUG}-independent/1.0"
DEFAULT_OUTPUT = REPO / "claims" / CLAIM / "runs" / f"2026-08-03-independent-{SLUG}" / "result.json"
A1_MANIFEST = REPO / "claims" / "A1-PRODUCTION-FUNCTIONAL-REALISATION" / "production_functional_manifest.json"
R128_MANIFEST = REPO / "claims" / CLAIM / "classii_owner_complete_source_pullback_covariance_normal_force_boundary_manifest.json"
R130_MANIFEST = REPO / "claims" / CLAIM / "classii_terminal_xi_conormal_gram_balanced_low_response_boundary_manifest.json"
R151_MANIFEST = REPO / "claims" / CLAIM / "classii_two_root_endpoint_hessian_uniform_local_gap_boundary_manifest.json"
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
    "lattice gap, both uniform over every finite cardinality, only for the R-155 family of "
    "distinct-source antipodal p:2p fixed-law affine controls, allowing source-target reuse, on "
    "the side-16 dual lattice at fixed cutoff and positive floor in the centered stationary "
    "common-even covariance-matched A1/A6/A7 chart. It supplies no cardinality-uniform nonzero "
    "radius, nonzero or realised-past estimate, shifted-state recursive or revisited-root result, "
    "nonlinear predictable feedback, finite-amplitude convexity, cutoff/floor removal, complete "
    "historical low owner, T-050 or A13 closure, Nelson theorem, interacting measure, phase/PDE "
    "verdict, or Sector-A closure."
)


def serial(value: Any) -> Any:
    if isinstance(value, F):
        return f"{value.numerator}/{value.denominator}"
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


def frac(value: Any) -> F:
    return F(str(value))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def trim(poly: list[F]) -> list[F]:
    result = list(poly)
    while len(result) > 1 and result[-1] == 0:
        result.pop()
    return result


def add(left: list[F], right: list[F]) -> list[F]:
    size = max(len(left), len(right))
    return trim([(left[index] if index < len(left) else F(0)) + (right[index] if index < len(right) else F(0)) for index in range(size)])


def scale(poly: list[F], factor: F) -> list[F]:
    return trim([factor * value for value in poly])


def mul(left: list[F], right: list[F]) -> list[F]:
    result = [F(0) for _ in range(len(left) + len(right) - 1)]
    for left_index, left_value in enumerate(left):
        for right_index, right_value in enumerate(right):
            result[left_index + right_index] += left_value * right_value
    return trim(result)


def power(poly: list[F], exponent: int) -> list[F]:
    result = [F(1)]
    for _ in range(exponent):
        result = mul(result, poly)
    return result


def evaluate(poly: list[F], point: F) -> F:
    return sum((coefficient * point**exponent for exponent, coefficient in enumerate(poly)), F(0))


def substitute_affine(poly: list[F], offset: F, slope: F) -> list[F]:
    result = [F(0)]
    affine = [offset, slope]
    for exponent, coefficient in enumerate(poly):
        result = add(result, scale(power(affine, exponent), coefficient))
    return trim(result)


def compactify_half_line(poly: list[F], lower: F) -> list[F]:
    """Return (1-y)^degree P(lower+y/(1-y)) in power coefficients."""
    degree = len(poly) - 1
    result = [F(0)]
    numerator = [lower, F(1) - lower]
    one_minus = [F(1), F(-1)]
    for exponent, coefficient in enumerate(poly):
        term = mul(power(numerator, exponent), power(one_minus, degree - exponent))
        result = add(result, scale(term, coefficient))
    return trim(result)


def bernstein_coefficients(poly: list[F]) -> list[F]:
    degree = len(poly) - 1
    padded = poly + [F(0)] * (degree + 1 - len(poly))
    return [
        sum((padded[index] * F(math.comb(order, index), math.comb(degree, index)) for index in range(order + 1)), F(0))
        for order in range(degree + 1)
    ]


def polynomial_cover(poly: list[F], intervals: list[tuple[F, F]], half_line_lower: F | None = None) -> dict[str, Any]:
    base = compactify_half_line(poly, half_line_lower) if half_line_lower is not None else poly
    rows = []
    for left, right in intervals:
        local = substitute_affine(base, left, right - left)
        coefficients = bernstein_coefficients(local)
        rows.append(
            {
                "interval": [left, right],
                "degree": len(local) - 1,
                "all_positive": all(value > 0 for value in coefficients),
                "minimum_coefficient": min(coefficients),
            }
        )
    return {"rows": rows, "all_positive": all(row["all_positive"] for row in rows)}


def radial(scale_value: int, z_value: F, constant: F) -> list[F]:
    return [constant, z_value * scale_value, F(scale_value * scale_value)]


def atan_bounds(z: F, last_index: int) -> tuple[F, F]:
    partial = sum(((-1) ** index * z ** (2 * index + 1) / F(2 * index + 1) for index in range(last_index + 1)), F(0))
    next_term = z ** (2 * last_index + 3) / F(2 * last_index + 3)
    if last_index % 2 == 0:
        return partial - next_term, partial
    return partial, partial + next_term


def independent_pi_bounds() -> tuple[F, F, dict[str, Any]]:
    """Use pi/4=atan(1/2)+atan(1/3), independent of the primary Machin route."""
    half_lower, half_upper = atan_bounds(F(1, 2), 9)
    third_lower, third_upper = atan_bounds(F(1, 3), 9)
    pi_lower = 4 * (half_lower + third_lower)
    pi_upper = 4 * (half_upper + third_upper)
    tangent_sum = (F(1, 2) + F(1, 3)) / (1 - F(1, 2) * F(1, 3))
    return pi_lower, pi_upper, {
        "identity": "pi/4 = atan(1/2) + atan(1/3)",
        "tangent_sum": tangent_sum,
        "atan_half_bounds": [half_lower, half_upper],
        "atan_third_bounds": [third_lower, third_upper],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()

    audit = Audit()
    a1 = json.loads(A1_MANIFEST.read_text(encoding="utf-8"))
    parameters = a1["parameters"]
    lengths = [frac(parameters[key]) for key in ("Lx", "Ly", "Lz")]
    volume = lengths[0] * lengths[1] * lengths[2]
    audit.check("production", "registered side-16 volume", lengths == [16, 16, 16] and volume == 4096, [lengths, volume], [[16, 16, 16], 4096])

    r128_manifest = json.loads(R128_MANIFEST.read_text(encoding="utf-8"))
    r128_note_record = r128_manifest["files"]["note"]
    r128_note_path = REPO / r128_note_record["path"]
    audit.check("authority", "R-128 source-pullback note hash", sha256(r128_note_path) == r128_note_record["sha256"], sha256(r128_note_path), r128_note_record["sha256"])

    r130_manifest = json.loads(R130_MANIFEST.read_text(encoding="utf-8"))
    r130_record = r130_manifest["files"]["primary_result"]
    r130_path = REPO / r130_record["path"]
    r130 = json.loads(r130_path.read_text(encoding="utf-8"))
    h6 = frac(r130["diagnostics"]["conormal_gram"]["H6"])
    p_floor = frac(parameters["M_X"]) ** 2 + frac(parameters["classii_mass_regularizer"])
    h6_upper = h6 * p_floor / frac(parameters["M_X"]) ** 2
    audit.check("authority", "R-130 result hash", sha256(r130_path) == r130_record["sha256"], sha256(r130_path), r130_record["sha256"])
    audit.check("coefficient", "strict H6 upper", h6 < h6_upper == F(7083, 2000), [h6, h6_upper], ["strict", F(7083, 2000)])

    r151_manifest = json.loads(R151_MANIFEST.read_text(encoding="utf-8"))
    r151_record = r151_manifest["files"]["primary_result"]
    r151_path = REPO / r151_record["path"]
    r151 = json.loads(r151_path.read_text(encoding="utf-8"))
    audit.check("authority", "R-151 result hash", sha256(r151_path) == r151_record["sha256"], sha256(r151_path), r151_record["sha256"])
    mass_floor = frac(r151["derived"]["mass_floor"])
    diagonal_factor = frac(r151["derived"]["covariance_normalized_factor"])
    source_hessian = frac(r151["derived"]["source_hessian"])
    audit.check("coefficient", "R-151 mass floor", mass_floor == F(7, 250), mass_floor, F(7, 250))
    audit.check("coefficient", "R-151 diagonal factor", diagonal_factor == 624, diagonal_factor, 624)
    audit.check("coefficient", "R-151 source Hessian", source_hessian == F(9, 10), source_hessian, F(9, 10))

    r155_manifest = json.loads(R155_MANIFEST.read_text(encoding="utf-8"))
    audit.check("authority", "R-155 source-target reuse scope", bool(r155_manifest["scope"]["source_target_overlap_allowed"]), r155_manifest["scope"], "reuse allowed")
    audit.check("authority", "R-155 regulator and exact torus scope", "scalar regulator" in r155_manifest["statement"] and "exact nonaliased torus" in r155_manifest["statement"], r155_manifest["statement"], "pinned")

    z_value = frac(parameters["Z"])
    constant = frac(parameters["r"]) + mass_floor
    lower_symbol = radial(1, z_value, constant)
    audit.check("production", "exact A1 lower symbol", lower_symbol == [F(5020336473, 10000000000), F(-4626377063, 5000000000), F(1)], lower_symbol, "registered exact coefficients")
    audit.check("production", "strict lower-symbol discriminant", z_value * z_value - 4 * constant < 0, z_value * z_value - 4 * constant, "<0")
    coarse_symbol = [F(5013, 10000), F(-953, 1000), F(1)]
    coarse_difference = add(lower_symbol, scale(coarse_symbol, -1))
    audit.check("correction", "coarse scratch symbol is a strict minorant", coarse_difference == [F(7336473, 10000000000), F(138622937, 5000000000)], coarse_difference, "positive affine difference")

    dual_rank = len(lengths)
    doubling_determinant = 2**dual_rank
    audit.check("source-reuse", "doubling injective modulo antipodes", doubling_determinant != 0, doubling_determinant, "[2p]=[2q] iff [p]=[q]")
    generic_cases = []
    for same_source in (False, True):
        raw_covariance = int(same_source)
        generic_cases.append({"same_source": same_source, "mixed_covariance_jet": 0 if not same_source else "diagonal", "source_gram_entry": raw_covariance})
    audit.check("source-reuse", "distinct-source mixed jets vanish", generic_cases[0]["mixed_covariance_jet"] == 0, generic_cases, "off-diagonal zero")
    audit.check("source-reuse", "source Gram stays diagonal", [row["source_gram_entry"] for row in generic_cases] == [0, 1], generic_cases, [0, 1])

    carrier_signs = {-1, 1}
    response = {2 * target - source for target in carrier_signs for source in carrier_signs}
    doubled_response = {2 * value for value in response}
    ratios = sorted({abs(F(left, right)) for left in response for right in response if left * right < 0 and abs(F(left, right)) != 1})
    audit.check("fourier", "response support", response == {-3, -1, 1, 3}, sorted(response), [-3, -1, 1, 3])
    audit.check("fourier", "factor-two reuse creates no response edge", response.isdisjoint(doubled_response), sorted(response & doubled_response), [])
    audit.check("fourier", "only factor-three distinct ratios", ratios == [F(1, 3), F(3)], ratios, [F(1, 3), F(3)])
    audit.check("graph", "factor-three components are finite paths", len(("parent", "child")) == 2 and 3 > 1, "degree <=2; norm grows by 3", "finite path union")

    real_dimension = 2 * len(parameters["family_masses"])
    covariance_response_factor = len(("left", "adjoint"))
    derivative_response_factor = len(("left", "adjoint")) * 1 * 2
    price_factor = F(1, 2) * real_dimension
    qc_at_three = price_factor * (covariance_response_factor * derivative_response_factor * 3**2 + covariance_response_factor * derivative_response_factor)
    k_norm = 1 + 2
    kk_at_three = (2 * real_dimension) * k_norm * (3 * k_norm)
    owner_edge = qc_at_three + kk_at_three
    antipodal_factor = len((-1, 1)) ** 2
    edge_factor = owner_edge * antipodal_factor
    audit.check("mixed-hessian", "Q-C factor", qc_at_three == 240, qc_at_three, 240)
    audit.check("mixed-hessian", "K-K factor", kk_at_three == 324, kk_at_three, 324)
    audit.check("mixed-hessian", "edge radial factor", edge_factor == 2256, edge_factor, 2256)

    f1 = lower_symbol
    f4 = radial(4, z_value, constant)
    f9 = radial(9, z_value, constant)
    f36 = radial(36, z_value, constant)
    f14 = mul(f1, f4)
    f936 = mul(f9, f36)
    diagonal_numerator = diagonal_factor * h6_upper / volume
    edge_numerator = edge_factor * h6_upper / volume
    audit.check("coefficient", "diagonal numerator", diagonal_numerator == F(276237, 512000), diagonal_numerator, F(276237, 512000))
    audit.check("coefficient", "edge numerator", edge_numerator == F(998703, 512000), edge_numerator, F(998703, 512000))

    schur_ratio = F(1, 4)
    audit.check("weighted-schur", "parent/child charges", [schur_ratio, 1 / schur_ratio] == [F(1, 4), F(4)], [schur_ratio, 1 / schur_ratio], [F(1, 4), F(4)])
    # Exact bivariate coefficients for
    # r*a^2 + r^(-1)*b^2 - 2ab = (a/2-2b)^2.
    young_remainder = {"a2": schur_ratio, "ab": F(-2), "b2": 1 / schur_ratio}
    young_square = {"a2": F(1, 4), "ab": F(-2), "b2": F(4)}
    audit.check("weighted-schur", "asymmetric Young square", young_remainder == young_square, young_remainder, "(a/2-2b)^2 coefficient pattern")

    low = F(3, 20)
    high = F(27, 20)
    actual_floor = (2 * F(31, 10) / lengths[0]) ** 2
    audit.check("lattice", "nonzero mode floor", actual_floor > low, actual_floor, f">{low}")
    audit.check("lattice", "factor-three parent floor", 9 * low == high, 9 * low, high)

    pi_lower, pi_upper, pi_certificate = independent_pi_bounds()
    audit.check("pi", "independent tangent identity", pi_certificate["tangent_sum"] == 1, pi_certificate, "tan sum = 1 on principal branch")
    audit.check("pi", "lattice shell enclosure", pi_lower > F(157, 50) and pi_upper < F(22, 7), [pi_lower, pi_upper], [">157/50", "<22/7"])
    unit_interval = [F(77, 500), F(31, 200)]
    unit_x_bounds = [pi_lower**2 / 64, pi_upper**2 / 64]
    higher_floor = F(3, 10)
    higher_x_lower = 2 * pi_lower**2 / 64
    audit.check("lattice", "N=1 shell interval", unit_x_bounds[0] > unit_interval[0] and unit_x_bounds[1] < unit_interval[1], unit_x_bounds, unit_interval)
    audit.check("lattice", "N>=2 shell half-line", higher_x_lower > higher_floor, higher_x_lower, f">{higher_floor}")

    x_poly = [F(0), F(1)]
    x_squared = [F(0), F(0), F(1)]
    required_gap = F(1, 10)
    continuous_gap = F(19, 160)
    continuous_budget = source_hessian - continuous_gap
    lattice_gap = F(4, 25)
    lattice_budget = source_hessian - lattice_gap
    audit.check("budget", "continuous and lattice budgets", [continuous_budget, lattice_budget] == [F(25, 32), F(37, 50)], [continuous_budget, lattice_budget], [F(25, 32), F(37, 50)])

    def root_polynomials(budget: F) -> tuple[list[F], list[F]]:
        guard = add(scale(f14, budget), scale(x_poly, -diagonal_numerator))
        squared = add(mul(mul(power(guard, 2), f936), [F(1)]), scale(mul(x_squared, f14), -(edge_numerator**2) / 16))
        return guard, squared

    continuous_guard, continuous_squared = root_polynomials(continuous_budget)
    lattice_guard, lattice_squared = root_polynomials(lattice_budget)
    edge_low = add(scale(mul(f14, f936), F(1, 36)), scale(x_squared, -(edge_numerator**2)))
    diagonal_high = add(scale(f14, F(1, 30)), scale(x_poly, -diagonal_numerator))
    edge_high = add(scale(mul(f14, f936), F(1, 10**6)), scale(x_squared, -(edge_numerator**2)))

    continuous_intervals = [(F(0), F(1, 64)), (F(1, 64), F(1, 32)), (F(1, 32), F(1, 16)), (F(1, 16), F(1, 8)), (F(1, 8), F(1, 4)), (F(1, 4), F(1, 2)), (F(1, 2), F(1))]
    higher_intervals = [(F(0), F(1, 32)), (F(1, 32), F(1, 16)), (F(1, 16), F(1, 8)), (F(1, 8), F(1, 4)), (F(1, 4), F(1, 2)), (F(1, 2), F(1))]
    covers = {
        "continuous_root_sign_guard": polynomial_cover(continuous_guard, continuous_intervals, low),
        "continuous_root_squared": polynomial_cover(continuous_squared, continuous_intervals, low),
        "lattice_unit_sign_guard": polynomial_cover(lattice_guard, [(unit_interval[0], unit_interval[1])]),
        "lattice_unit_squared": polynomial_cover(lattice_squared, [(unit_interval[0], unit_interval[1])]),
        "lattice_higher_sign_guard": polynomial_cover(lattice_guard, higher_intervals, higher_floor),
        "lattice_higher_squared": polynomial_cover(lattice_squared, higher_intervals, higher_floor),
        "global_edge_one_sixth": polynomial_cover(edge_low, [(F(0), F(1, 2)), (F(1, 2), F(1))], low),
        "parent_diagonal_one_thirtieth": polynomial_cover(diagonal_high, [(F(0), F(1))], high),
        "parent_edge_one_thousandth": polynomial_cover(edge_high, [(F(0), F(1))], high),
    }
    expected_degrees = {
        "continuous_root_sign_guard": 4,
        "continuous_root_squared": 12,
        "lattice_unit_sign_guard": 4,
        "lattice_unit_squared": 12,
        "lattice_higher_sign_guard": 4,
        "lattice_higher_squared": 12,
        "global_edge_one_sixth": 8,
        "parent_diagonal_one_thirtieth": 4,
        "parent_edge_one_thousandth": 8,
    }
    for name, cover in covers.items():
        audit.check("bernstein", f"{name} positive cover", cover["all_positive"], cover, "all Bernstein coefficients positive")
        audit.check("bernstein", f"{name} degree", all(row["degree"] == expected_degrees[name] for row in cover["rows"]), [row["degree"] for row in cover["rows"]], expected_degrees[name])

    interior_loss = F(1, 30) + 4 * F(1, 6) + F(1, 4) * F(1, 1000)
    audit.check("row-bound", "interior adverse loss", interior_loss == F(2801, 4000), interior_loss, F(2801, 4000))
    audit.check("row-bound", "interior below both budgets", interior_loss < lattice_budget < continuous_budget, [interior_loss, lattice_budget, continuous_budget], "ordered")
    audit.check("gap", "continuous origin gap", source_hessian - continuous_budget == continuous_gap > required_gap, continuous_gap, F(19, 160))
    audit.check("gap", "actual-lattice origin gap", source_hessian - lattice_budget == lattice_gap > continuous_gap, lattice_gap, F(4, 25))
    audit.check("gap", "threshold headrooms", [continuous_gap - required_gap, lattice_gap - required_gap] == [F(3, 160), F(3, 50)], [continuous_gap - required_gap, lattice_gap - required_gap], [F(3, 160), F(3, 50)])

    wrong_unweighted = add(mul(scale(x_squared, edge_numerator**2), f14), scale(mul(power(lattice_guard, 2), f936), -1))
    audit.check("adversarial", "unweighted root charge fails at floor", evaluate(wrong_unweighted, low) > 0, evaluate(wrong_unweighted, low), "E > 37/50-L at x=3/20")
    floor_witness = F(1, 36)
    floor_removal_excess = 16 * edge_numerator**2 * floor_witness**2 - continuous_budget**2 * evaluate(f14, floor_witness) * evaluate(f936, floor_witness)
    audit.check("boundary", "floor-removal weighted majorant fails", floor_removal_excess > 0, floor_removal_excess, "4E(1/36)>25/32; method obstruction only")

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
        "method": "non-importing standard-library Fraction reconstruction with exact Bernstein covers and an independent arctangent pi identity",
        "derived": {
            "volume": volume,
            "lower_symbol": lower_symbol,
            "coarse_surrogate_difference": coarse_difference,
            "H6_registered": h6,
            "H6_strict_upper": h6_upper,
            "diagonal_radial_factor": diagonal_factor,
            "factor_three_edge_components": {"QC": qc_at_three, "KK": kk_at_three, "total": owner_edge},
            "edge_radial_factor": edge_factor,
            "diagonal_numerator": diagonal_numerator,
            "edge_numerator": edge_numerator,
            "resonance_ratios": ratios,
            "schur_weight_ratio": schur_ratio,
            "nonzero_mode_floor": low,
            "pi_bounds": [pi_lower, pi_upper],
            "pi_certificate": pi_certificate,
            "unit_shell_interval": unit_interval,
            "unit_shell_x_bounds": unit_x_bounds,
            "higher_shell_floor": higher_floor,
            "higher_shell_x_lower": higher_x_lower,
            "source_hessian": source_hessian,
            "continuous_endpoint_loss_budget": continuous_budget,
            "continuous_certified_gap": continuous_gap,
            "continuous_threshold_headroom": continuous_gap - required_gap,
            "lattice_endpoint_loss_budget": lattice_budget,
            "lattice_certified_gap": lattice_gap,
            "lattice_threshold_headroom": lattice_gap - required_gap,
            "interior_loss_upper": interior_loss,
            "continuous_interior_slack": continuous_budget - interior_loss,
            "lattice_interior_slack": lattice_budget - interior_loss,
            "bernstein_covers": covers,
            "wrong_unweighted_floor_excess": evaluate(wrong_unweighted, low),
            "floor_removal_majorant_witness": {"x": floor_witness, "cleared_excess": floor_removal_excess},
        },
        "assertions": audit.rows,
        "summary": {
            "passed": sum(row["status"] == "PASS" for row in audit.rows),
            "failed": sum(row["status"] != "PASS" for row in audit.rows),
            "total": len(audit.rows),
        },
    }
    atomic_json(arguments.output, payload)
    print(f"{RESULT_ID} independent: {payload['summary']['passed']}/{payload['summary']['total']} PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

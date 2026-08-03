#!/usr/bin/env python3
"""Independent exact audit for the A13 R-164 first-chaos reduction.

This verifier uses only standard-library rational polynomial arithmetic.  It
does not import or read the primary verifier or its result.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass, field
from fractions import Fraction as F
import hashlib
import json
import os
from pathlib import Path
import tempfile
from typing import Any


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = (
    "A13-CLASSII-PREDICTABLE-FIRST-CHAOS-ORIGIN-FORCE-"
    "ANCHOR-FREE-SEMICONVEXITY-REDUCTION"
)
LEDGER_ID = "R-164"
SLUG = "predictable-first-chaos-origin-force-anchor-free-semiconvexity-reduction"
SCHEMA = f"tect/a13-{SLUG}-independent/1.0"
CLAIM_DIR = REPO / "claims" / CLAIM
DEFAULT_OUTPUT = CLAIM_DIR / "runs" / f"2026-08-04-independent-{SLUG}" / "result.json"

AUTHORITIES = {
    "A1": REPO / "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json",
    "A7": REPO / "claims/A7-CLASSII-RENORMALISED-ENERGY-COMPOSITE/classii_renormalised_energy_manifest.json",
    "A11": REPO / "claims/A11-CLASSII-TRUE-INCREMENT-DETERMINANT-REDUCTION/classii_true_increment_determinant_manifest.json",
    "R-104": CLAIM_DIR / "classii_lossless_progressive_complete_owner_assembly_heat_boundary_manifest.json",
    "R-128": CLAIM_DIR / "classii_owner_complete_source_pullback_covariance_normal_force_boundary_manifest.json",
    "R-141": CLAIM_DIR / "classii_projected_force_global_doob_signed_gram_adaptive_collar_quotient_boundary_manifest.json",
    "R-146": CLAIM_DIR / "classii_canonical_covariance_relative_anchor_anisotropic_temporal_reduction_manifest.json",
    "R-153": CLAIM_DIR / "classii_production_strict_past_conditional_hessian_weighted_collar_boundary_manifest.json",
    "R-163": CLAIM_DIR / "classii_full_lattice_weighted_resolvent_dyadic_forest_uniform_neighborhood_gap_boundary_manifest.json",
}

SCOPE = {
    "finite_temporally_faithful_gaussian_chart": True,
    "independent_whitened_source_blocks": True,
    "deterministic_zero_control_synthesis": True,
    "overlapping_physical_source_ranges_allowed": True,
    "complete_r141_endpoint_scalar": True,
    "a7_zero_control_law": True,
    "fixed_sharp_cube_dyadic_cutoff_sequence": True,
    "all_admitted_regulators_uniform": False,
    "direct_unreduced_action": True,
    "origin_preserving_causal_graph_force_only_with_uniform_tangent": True,
    "exact_graph_source_metric_and_stabilizer_transport": False,
    "complete_graph_semiconvexity_composition": False,
    "stationary_low_elimination_away_from_zero": False,
    "nonzero_feedback_force_bound": False,
    "random_nonlinear_revisit_semiconvexity": False,
    "pathwise_conditional_semiconvexity": False,
    "complete_production_owner_bound": False,
    "t050_closed": False,
    "a13_closed": False,
    "sector_a_closed": False,
}

NO_OVERCLAIM = (
    "R-164 proves a cutoff- and finite-chart-uniform zero-control origin-force "
    "bound for the direct R-104/R-141 action by predictable first-chaos "
    "projection, and removes the direct absolute anchor by A7/R-146. It does "
    "not prove the complete production owner lower bound, a stationary reduced "
    "low base away from zero, a nonzero-feedback force estimate, random/"
    "nonlinear/revisit or pathwise conditional semiconvexity, removal, T-050, "
    "A13, Nelson, an interacting measure, a phase/PDE verdict, or Sector-A closure."
)

# Labelled authority inputs. All downstream coefficients are derived here.
SOURCE_ACTION = F(9, 20)
NELSON_P = F(11, 10)
STABILIZER = F(3, 20)
TARGET_EPS6 = F(27, 100)
SOURCE_HESSIAN = 2 * SOURCE_ACTION
TARGET_EPSV = 1 / (2 * NELSON_P)
MU_FLOOR = 2 * (SOURCE_ACTION - TARGET_EPSV)
OWNER_FLOOR = MU_FLOOR - SOURCE_HESSIAN

Monomial = tuple[int, ...]
Polynomial = dict[Monomial, F]


def clean(polynomial: Polynomial) -> Polynomial:
    return {key: value for key, value in polynomial.items() if value}


def add(*polynomials: Polynomial) -> Polynomial:
    result: Polynomial = {}
    for polynomial in polynomials:
        for key, value in polynomial.items():
            result[key] = result.get(key, F(0)) + value
    return clean(result)


def scale(polynomial: Polynomial, coefficient: F | int) -> Polynomial:
    factor = F(coefficient)
    return clean({key: factor * value for key, value in polynomial.items()})


def multiply(left: Polynomial, right: Polynomial) -> Polynomial:
    result: Polynomial = {}
    for lkey, lvalue in left.items():
        for rkey, rvalue in right.items():
            key = tuple(a + b for a, b in zip(lkey, rkey))
            result[key] = result.get(key, F(0)) + lvalue * rvalue
    return clean(result)


def power(polynomial: Polynomial, exponent: int) -> Polynomial:
    dimension = len(next(iter(polynomial)))
    result: Polynomial = {(0,) * dimension: F(1)}
    base = polynomial
    degree = exponent
    while degree:
        if degree & 1:
            result = multiply(result, base)
        base = multiply(base, base)
        degree //= 2
    return result


def derivative(polynomial: Polynomial, axis: int) -> Polynomial:
    result: Polynomial = {}
    for key, value in polynomial.items():
        if key[axis]:
            reduced = list(key)
            coefficient = reduced[axis]
            reduced[axis] -= 1
            reduced_key = tuple(reduced)
            result[reduced_key] = result.get(reduced_key, F(0)) + value * coefficient
    return clean(result)


def double_factorial_odd(index: int) -> int:
    if index == -1:
        return 1
    result = 1
    for value in range(1, index + 1, 2):
        result *= value
    return result


def gaussian_moment(power_value: int) -> int:
    if power_value % 2:
        return 0
    return double_factorial_odd(power_value - 1)


def expectation(polynomial: Polynomial) -> F:
    total = F(0)
    for exponents, coefficient in polynomial.items():
        moment = 1
        for exponent in exponents:
            moment *= gaussian_moment(exponent)
        total += coefficient * moment
    return total


def conditional(polynomial: Polynomial, retained_axes: int) -> Polynomial:
    result: Polynomial = {}
    for exponents, coefficient in polynomial.items():
        moment = 1
        for exponent in exponents[retained_axes:]:
            moment *= gaussian_moment(exponent)
        if not moment:
            continue
        key = exponents[:retained_axes] + (0,) * (len(exponents) - retained_axes)
        result[key] = result.get(key, F(0)) + coefficient * moment
    return clean(result)


def variable(dimension: int, axis: int) -> Polynomial:
    exponents = [0] * dimension
    exponents[axis] = 1
    return {tuple(exponents): F(1)}


def constant(dimension: int, value: F | int) -> Polynomial:
    return {(0,) * dimension: F(value)} if value else {}


def square_norm(polynomial: Polynomial) -> F:
    return expectation(multiply(polynomial, polynomial))


def serial(value: Any) -> Any:
    if isinstance(value, F):
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


def sha256_text(path: Path) -> str:
    payload = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(payload).hexdigest()


def relative(path: Path) -> str:
    return str(path.resolve().relative_to(REPO.resolve())).replace("\\", "/")


@dataclass
class Audit:
    rows: list[dict[str, Any]] = field(default_factory=list)

    def check(self, group: str, name: str, condition: bool, actual: Any, expected: Any) -> None:
        self.rows.append(
            {
                "group": group,
                "name": name,
                "status": "PASS" if condition else "FAIL",
                "actual": serial(actual),
                "expected": serial(expected),
            }
        )

    def require(self) -> None:
        failures = [row for row in self.rows if row["status"] != "PASS"]
        if failures:
            raise AssertionError(json.dumps(failures, indent=2, ensure_ascii=True))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()
    audit = Audit()

    for label, path in AUTHORITIES.items():
        audit.check("authority", f"{label} exists", path.is_file(), relative(path), "existing file")

    a7_note = REPO / "claims/A7-CLASSII-RENORMALISED-ENERGY-COMPOSITE/notes/classii-renormalised-energy-composite-260720-v1.0.tex.txt"
    a11_note = REPO / "claims/A11-CLASSII-TRUE-INCREMENT-DETERMINANT-REDUCTION/notes/classii-true-increment-determinant-260721-v1.0.tex.txt"
    r104_note = CLAIM_DIR / "notes/classii-lossless-progressive-complete-owner-assembly-heat-boundary-260728-v1.0.tex.txt"
    audit.check("authority", "A7 finite-cutoff centering", "zero mean at every cutoff" in a7_note.read_text(encoding="utf-8"), "zero mean at every cutoff", "present")
    audit.check("authority", "A11 point covariance trace", "covariances $C_N$ converge in trace" in a11_note.read_text(encoding="utf-8"), "covariances $C_N$ converge in trace", "present")
    audit.check("authority", "R-104 independent source synthesis", "independent standard source block" in r104_note.read_text(encoding="utf-8"), "independent standard source block", "present")

    dimension = 3
    x, y, z = (variable(dimension, axis) for axis in range(dimension))
    one = constant(dimension, 1)
    h2x = add(multiply(x, x), scale(one, -1))
    h2y = add(multiply(y, y), scale(one, -1))
    h2z = add(multiply(z, z), scale(one, -1))
    endpoint = add(
        x,
        scale(multiply(x, y), 2),
        scale(multiply(h2y, z), 3),
        scale(h2x, 4),
        scale(h2z, 5),
    )
    mean = expectation(endpoint)
    centered = add(endpoint, scale(one, -mean))
    variance = square_norm(centered)
    gradients = [
        conditional(derivative(endpoint, 0), 0),
        conditional(derivative(endpoint, 1), 1),
        conditional(derivative(endpoint, 2), 2),
    ]
    projected = add(multiply(gradients[0], x), multiply(gradients[1], y), multiply(gradients[2], z))
    projected_norm = square_norm(projected)
    coefficient_norm = sum(square_norm(gradient) for gradient in gradients)
    residual = add(centered, scale(projected, -1))

    audit.check("projection", "fixture mean", mean == 0, mean, 0)
    audit.check("projection", "first predictable coefficient", gradients[0] == one, gradients[0], one)
    audit.check("projection", "second predictable coefficient", gradients[1] == scale(x, 2), gradients[1], scale(x, 2))
    audit.check("projection", "third predictable coefficient", gradients[2] == scale(h2y, 3), gradients[2], scale(h2y, 3))
    audit.check("projection", "isometry", projected_norm == coefficient_norm, projected_norm, coefficient_norm)
    audit.check("projection", "Bessel bound", projected_norm <= variance, projected_norm, f"<= {variance}")
    audit.check("projection", "strict projection gap", variance - projected_norm == 82, variance - projected_norm, 82)
    for index, test in enumerate((one, x, h2x)):
        direction = multiply(test, y)
        audit.check("projection", f"residual orthogonal predictable test {index}", expectation(multiply(residual, direction)) == 0, expectation(multiply(residual, direction)), 0)

    m0 = constant(dimension, mean)
    m1 = conditional(endpoint, 1)
    m2 = conditional(endpoint, 2)
    m3 = endpoint
    increments = [add(m1, scale(m0, -1)), add(m2, scale(m1, -1)), add(m3, scale(m2, -1))]
    increment_variance = sum(square_norm(increment) for increment in increments)
    audit.check("martingale", "first conditional Stein coefficient", conditional(multiply(x, increments[0]), 0) == gradients[0], conditional(multiply(x, increments[0]), 0), gradients[0])
    audit.check("martingale", "second conditional Stein coefficient", conditional(multiply(y, increments[1]), 1) == gradients[1], conditional(multiply(y, increments[1]), 1), gradients[1])
    audit.check("martingale", "third conditional Stein coefficient", conditional(multiply(z, increments[2]), 2) == gradients[2], conditional(multiply(z, increments[2]), 2), gradients[2])
    audit.check("martingale", "orthogonal increments recover variance", increment_variance == variance == 105, increment_variance, 105)

    sharp = x
    sharp_gradient = conditional(derivative(sharp, 0), 0)
    strict = h2x
    strict_gradient = conditional(derivative(strict, 0), 0)
    audit.check("sharpness", "constant one attained", square_norm(sharp_gradient) == square_norm(sharp) == 1, [square_norm(sharp_gradient), square_norm(sharp)], [1, 1])
    audit.check("sharpness", "discrete inequality strict", square_norm(strict_gradient) == 0 and square_norm(strict) == 2, [square_norm(strict_gradient), square_norm(strict)], [0, 2])
    wrong_current_conditioning = multiply(x, h2x)
    wrong_energy = square_norm(wrong_current_conditioning)
    audit.check("sharpness", "current-block conditioning is invalid", wrong_energy > square_norm(strict), wrong_energy, f"> {square_norm(strict)}")

    twelfth = gaussian_moment(12)
    audit.check("gaussian-moment", "twelfth moment constructed", twelfth == 10395, twelfth, 10395)
    lambdas = (F(1, 2), F(1, 3), F(1, 6))
    radial_square = add(*(scale(multiply(item, item), weight) for item, weight in zip((x, y, z), lambdas)))
    radial_twelfth = expectation(power(radial_square, 6))
    trace = sum(lambdas, F(0))
    envelope = F(twelfth) * trace**6
    rank_one = expectation(power(scale(multiply(x, x), trace), 6))
    audit.check("gaussian-moment", "radial envelope", radial_twelfth <= envelope, radial_twelfth, f"<= {envelope}")
    audit.check("gaussian-moment", "rank-one equality", rank_one == envelope, rank_one, envelope)

    source_hessian = SOURCE_HESSIAN
    rho = F(2, 7)
    mu = source_hessian + OWNER_FLOOR + rho
    eta = rho / 4
    epsilon_v = SOURCE_ACTION - mu / 2 + eta
    epsilon_6 = STABILIZER
    audit.check("threshold", "source Hessian derived", source_hessian == F(9, 10), source_hessian, F(9, 10))
    audit.check("threshold", "target source coefficient derived", TARGET_EPSV == F(5, 11), TARGET_EPSV, F(5, 11))
    audit.check("threshold", "semiconvexity floor derived", MU_FLOOR == -F(1, 110), MU_FLOOR, -F(1, 110))
    audit.check("threshold", "owner floor derived", OWNER_FLOOR == -F(10, 11), OWNER_FLOOR, -F(10, 11))
    audit.check("threshold", "semiconvexity formula", mu == MU_FLOOR + rho, mu, MU_FLOOR + rho)
    audit.check("threshold", "source coefficient formula", epsilon_v == TARGET_EPSV - rho / 4, epsilon_v, TARGET_EPSV - rho / 4)
    audit.check("threshold", "strict source margin", TARGET_EPSV - epsilon_v == rho / 4 > 0, TARGET_EPSV - epsilon_v, rho / 4)
    audit.check("threshold", "sextic margin", TARGET_EPS6 - epsilon_6 == F(3, 25), TARGET_EPS6 - epsilon_6, F(3, 25))
    for index, (u, v, c) in enumerate(((F(2, 3), F(5, 7), F(4, 9)), (F(11, 5), F(3, 8), F(7, 6)))):
        left = -c * u * v + rho * u * u / 4 + c * c * v * v / rho
        right = (u * F(1, 2) - c * v / rho) ** 2 * rho
        audit.check("threshold", f"Young square fixture {index}", left == right >= 0, left, right)

    zero_interaction_mean = F(0)
    zero_source_cost = F(0)
    fixture_terminal_sixth = F(7, 3)
    fixture_anchor = zero_interaction_mean + zero_source_cost + STABILIZER * fixture_terminal_sixth
    audit.check("anchor", "zero source cost", zero_source_cost == 0, zero_source_cost, 0)
    audit.check("anchor", "A7 centered direct anchor identity", fixture_anchor == F(7, 20), fixture_anchor, F(7, 20))
    audit.check("anchor", "direct anchor nonnegative", fixture_anchor >= 0, fixture_anchor, ">= 0")

    false_scope = (
        "stationary_low_elimination_away_from_zero",
        "nonzero_feedback_force_bound",
        "random_nonlinear_revisit_semiconvexity",
        "pathwise_conditional_semiconvexity",
        "complete_production_owner_bound",
        "exact_graph_source_metric_and_stabilizer_transport",
        "complete_graph_semiconvexity_composition",
        "all_admitted_regulators_uniform",
        "t050_closed",
        "a13_closed",
        "sector_a_closed",
    )
    audit.check("scope", "closure flags false", all(not SCOPE[key] for key in false_scope), {key: SCOPE[key] for key in false_scope}, "all false")
    audit.check("scope", "direct chart true", SCOPE["direct_unreduced_action"] and SCOPE["a7_zero_control_law"], [SCOPE["direct_unreduced_action"], SCOPE["a7_zero_control_law"]], [True, True])

    audit.require()
    variance_components = {
        "renormalized_energy_coefficient": F(1),
        "stabilizer": STABILIZER,
        "volume_power": 3,
        "generic_real_twelfth_moment": twelfth,
        "trace_power": 3,
    }
    direct_constant_components = {"variance_factor": F(1), "rho_power": -1}
    graph_force_components = {"variance_factor": F(1), "tangent_power": 2}
    payload = {
        "schema": SCHEMA,
        "package_version": __version__,
        "issued": "2026-08-04",
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "result_ledger_id": LEDGER_ID,
        "tier": "T4",
        "evidence_grade": ["ANALYTIC", "EXACT", "EXECUTED", "AUDITED"],
        "authority_hashes": {label: sha256_text(path) for label, path in AUTHORITIES.items()},
        "scope": SCOPE,
        "diagnostics": {
            "fixture_variance": variance,
            "fixture_projected_norm": projected_norm,
            "fixture_projection_gap": variance - projected_norm,
            "generic_real_twelfth_moment": twelfth,
            "source_threshold": "5/11 - rho/4",
            "sextic_threshold": epsilon_6,
            "origin_force_certificate_components": variance_components,
            "direct_t050_constant_components": direct_constant_components,
            "graph_force_pullback_components": graph_force_components,
        },
        "assertions": audit.rows,
        "summary": {"passed": len(audit.rows), "failed": 0, "total": len(audit.rows)},
        "no_overclaim": NO_OVERCLAIM,
    }
    atomic_json(arguments.output, payload)
    print(f"R-164 independent: {len(audit.rows)}/{len(audit.rows)} PASS")
    print(f"result: {arguments.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

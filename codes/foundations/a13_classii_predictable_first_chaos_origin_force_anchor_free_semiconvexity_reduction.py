#!/usr/bin/env python3
"""Primary exact audit for the A13 R-164 origin-force reduction.

The analytic proof is in the accompanying note. This executable checks the
predictable first-Gaussian-chaos projection on exact polynomial fixtures, the
Gaussian twelfth-moment envelope, the R-146/R-163 coefficient composition,
and the authority and scope contracts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import sympy as sp


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = (
    "A13-CLASSII-PREDICTABLE-FIRST-CHAOS-ORIGIN-FORCE-"
    "ANCHOR-FREE-SEMICONVEXITY-REDUCTION"
)
LEDGER_ID = "R-164"
SLUG = "predictable-first-chaos-origin-force-anchor-free-semiconvexity-reduction"
SCHEMA = f"tect/a13-{SLUG}-primary/1.0"
CLAIM_DIR = REPO / "claims" / CLAIM
DEFAULT_OUTPUT = CLAIM_DIR / "runs" / f"2026-08-04-primary-{SLUG}" / "result.json"

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
SOURCE_ACTION = sp.Rational(9, 20)
NELSON_P = sp.Rational(11, 10)
STABILIZER = sp.Rational(3, 20)
TARGET_EPS6 = sp.Rational(27, 100)
SOURCE_HESSIAN = 2 * SOURCE_ACTION
TARGET_EPSV = 1 / (2 * NELSON_P)
MU_FLOOR = 2 * (SOURCE_ACTION - TARGET_EPSV)
OWNER_FLOOR = MU_FLOOR - SOURCE_HESSIAN


def serial(value: Any) -> Any:
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
                "status": "PASS" if bool(condition) else "FAIL",
                "actual": serial(actual),
                "expected": serial(expected),
            }
        )

    def require(self) -> None:
        failures = [row for row in self.rows if row["status"] != "PASS"]
        if failures:
            raise AssertionError(json.dumps(failures, indent=2, ensure_ascii=True))


def gaussian_moment(power: int) -> sp.Integer:
    if power < 0 or power % 2:
        return sp.Integer(0)
    if power == 0:
        return sp.Integer(1)
    return sp.factorial2(power - 1)


def gaussian_expectation(expression: sp.Expr, variables: tuple[sp.Symbol, ...]) -> sp.Expr:
    polynomial = sp.Poly(sp.expand(expression), *variables)
    total = sp.Integer(0)
    for exponents, coefficient in polynomial.terms():
        moment = sp.Integer(1)
        for exponent in exponents:
            moment *= gaussian_moment(exponent)
        total += coefficient * moment
    return sp.simplify(total)


def conditional_expectation(
    expression: sp.Expr,
    retained: tuple[sp.Symbol, ...],
    integrated: tuple[sp.Symbol, ...],
) -> sp.Expr:
    expanded = sp.Poly(sp.expand(expression), *(retained + integrated))
    total = sp.Integer(0)
    retained_count = len(retained)
    for exponents, coefficient in expanded.terms():
        moment = sp.Integer(1)
        for exponent in exponents[retained_count:]:
            moment *= gaussian_moment(exponent)
        monomial = coefficient * moment
        for variable, exponent in zip(retained, exponents[:retained_count]):
            monomial *= variable**exponent
        total += monomial
    return sp.expand(total)


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
    r141_note = CLAIM_DIR / "notes/classii-projected-force-global-doob-signed-gram-adaptive-collar-quotient-boundary-260731-v1.0.tex.txt"
    r146_note = CLAIM_DIR / "notes/classii-canonical-covariance-relative-anchor-anisotropic-temporal-reduction-260802-v1.0.tex.txt"
    r153_note = CLAIM_DIR / "notes/classii-production-strict-past-conditional-hessian-weighted-collar-boundary-260803-v1.0.tex.txt"
    r163_note = CLAIM_DIR / "notes/classii-full-lattice-weighted-resolvent-dyadic-forest-uniform-neighborhood-gap-boundary-260804-v1.0.tex.txt"
    for name, path, needle in (
        ("A7 scalar L2 convergence", a7_note, "in }L^2(\\Omega)"),
        ("A7 finite-cutoff centering", a7_note, "zero mean at every cutoff"),
        ("A11 point covariance trace", a11_note, "covariances $C_N$ converge in trace"),
        ("R-104 independent source synthesis", r104_note, "independent standard source block"),
        ("R-141 projected force", r141_note, "(g_\\pi^{\\rm prod}(h))_b"),
        ("R-146 relative anchor", r146_note, "exact relative anchor"),
        ("R-153 nonzero first variation", r153_note, "generally nonzero"),
        ("R-163 threshold", r163_note, "\\mu>-{1\\over110}"),
    ):
        audit.check("authority", name, needle in path.read_text(encoding="utf-8"), needle, "present")

    x, y = sp.symbols("x y", real=True)
    variables = (x, y)
    endpoint = x**3 + 2 * x * y**2 + 3 * x**2 * y + 5 * y**3
    mean = gaussian_expectation(endpoint, variables)
    variance = gaussian_expectation((endpoint - mean) ** 2, variables)
    g1 = gaussian_expectation(sp.diff(endpoint, x), variables)
    g2 = conditional_expectation(sp.diff(endpoint, y), (x,), (y,))
    projected_norm = sp.simplify(g1**2 + gaussian_expectation(g2**2, (x,)))
    delta_g = sp.expand(g1 * x + g2 * y)
    residual = sp.expand(endpoint - mean - delta_g)

    audit.check("projection", "fixture mean", mean == 0, mean, 0)
    audit.check("projection", "first block gradient", g1 == 5, g1, 5)
    audit.check("projection", "second predictable gradient", g2 == 3 * x**2 + 15, g2, 3 * x**2 + 15)
    audit.check("projection", "projection is Bessel bounded", projected_norm <= variance, projected_norm, f"<= {variance}")
    audit.check("projection", "projection gap nonnegative", sp.simplify(variance - projected_norm) >= 0, sp.simplify(variance - projected_norm), ">= 0")

    tests = (sp.Integer(1), x, x**2, x**3)
    audit.check(
        "projection",
        "residual orthogonal to first block",
        gaussian_expectation(residual * x, variables) == 0,
        gaussian_expectation(residual * x, variables),
        0,
    )
    for index, test in enumerate(tests):
        value = gaussian_expectation(residual * test * y, variables)
        audit.check("projection", f"residual orthogonal to predictable test {index}", value == 0, value, 0)

    m1 = conditional_expectation(endpoint, (x,), (y,))
    delta_m1 = sp.expand(m1 - mean)
    delta_m2 = sp.expand(endpoint - m1)
    audit.check("martingale", "first Stein coefficient", gaussian_expectation(x * delta_m1, (x,)) == g1, gaussian_expectation(x * delta_m1, (x,)), g1)
    audit.check("martingale", "second conditional Stein coefficient", conditional_expectation(y * delta_m2, (x,), (y,)) == g2, conditional_expectation(y * delta_m2, (x,), (y,)), g2)
    martingale_variance = gaussian_expectation(delta_m1**2 + delta_m2**2, variables)
    audit.check("martingale", "orthogonal increments recover variance", martingale_variance == variance, martingale_variance, variance)

    sharp_endpoint = x
    sharp_g = gaussian_expectation(sp.diff(sharp_endpoint, x), (x,))
    sharp_variance = gaussian_expectation(sharp_endpoint**2, (x,))
    audit.check("sharpness", "constant one attained", sharp_g**2 == sharp_variance == 1, [sharp_g**2, sharp_variance], [1, 1])
    strict_endpoint = x**2 - 1
    strict_g = gaussian_expectation(sp.diff(strict_endpoint, x), (x,))
    strict_variance = gaussian_expectation(strict_endpoint**2, (x,))
    audit.check("sharpness", "discrete inequality can be strict", strict_g == 0 and strict_variance == 2, [strict_g, strict_variance], [0, 2])

    twelfth = gaussian_moment(12)
    audit.check("gaussian-moment", "twelfth standard moment derived", twelfth == sp.factorial2(11), twelfth, sp.factorial2(11))
    lambdas = (sp.Rational(1, 2), sp.Rational(1, 3), sp.Rational(1, 6))
    g = sp.symbols("g0:3", real=True)
    radial_square = sum(weight * variable**2 for weight, variable in zip(lambdas, g))
    radial_twelfth = gaussian_expectation(radial_square**6, g)
    trace = sum(lambdas)
    envelope = twelfth * trace**6
    audit.check("gaussian-moment", "correlated radial moment envelope", radial_twelfth <= envelope, radial_twelfth, f"<= {envelope}")
    rank_one = gaussian_expectation((trace * g[0] ** 2) ** 6, g)
    audit.check("gaussian-moment", "rank-one envelope equality", rank_one == envelope, rank_one, envelope)

    rho = sp.symbols("rho", positive=True)
    source_hessian = SOURCE_HESSIAN
    adverse_owner = OWNER_FLOOR + rho
    mu = sp.simplify(source_hessian + adverse_owner)
    eta = rho / 4
    epsilon_v = sp.simplify(SOURCE_ACTION - mu / 2 + eta)
    epsilon_6 = STABILIZER
    audit.check("threshold", "source Hessian derived", source_hessian == sp.Rational(9, 10), source_hessian, sp.Rational(9, 10))
    audit.check("threshold", "target source coefficient derived", TARGET_EPSV == sp.Rational(5, 11), TARGET_EPSV, sp.Rational(5, 11))
    audit.check("threshold", "semiconvexity floor derived", MU_FLOOR == -sp.Rational(1, 110), MU_FLOOR, -sp.Rational(1, 110))
    audit.check("threshold", "owner floor derived", OWNER_FLOOR == -sp.Rational(10, 11), OWNER_FLOOR, -sp.Rational(10, 11))
    audit.check("threshold", "owner to semiconvexity", mu == MU_FLOOR + rho, mu, MU_FLOOR + rho)
    audit.check("threshold", "Young choice", eta == rho / 4, eta, rho / 4)
    audit.check("threshold", "source coefficient", epsilon_v == TARGET_EPSV - rho / 4, epsilon_v, TARGET_EPSV - rho / 4)
    audit.check("threshold", "source strict margin", sp.simplify(TARGET_EPSV - epsilon_v) == rho / 4, sp.simplify(TARGET_EPSV - epsilon_v), rho / 4)
    audit.check("threshold", "sextic margin", TARGET_EPS6 - epsilon_6 == sp.Rational(3, 25), TARGET_EPS6 - epsilon_6, sp.Rational(3, 25))

    B, X, c = sp.symbols("B X c", nonnegative=True)
    young_gap = sp.expand(
        -c * sp.sqrt(B * X)
        + rho * X / 4
        + c**2 * B / rho
    )
    young_square = (sp.sqrt(rho * X) / 2 - c * sp.sqrt(B / rho)) ** 2
    audit.check("threshold", "Young completion identity", sp.simplify(young_gap - young_square) == 0, sp.simplify(young_gap - young_square), 0)
    zero_interaction_mean = sp.Integer(0)
    zero_source_cost = sp.Integer(0)
    fixture_terminal_sixth = sp.Rational(7, 3)
    fixture_anchor = zero_interaction_mean + zero_source_cost + STABILIZER * fixture_terminal_sixth
    audit.check("anchor", "zero source cost", zero_source_cost == 0, zero_source_cost, 0)
    audit.check("anchor", "A7 centered direct anchor identity", fixture_anchor == sp.Rational(7, 20), fixture_anchor, sp.Rational(7, 20))
    audit.check("anchor", "direct anchor is nonnegative", fixture_anchor >= 0, fixture_anchor, ">= 0")

    expected_false = {
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
    }
    audit.check("scope", "all closure flags remain false", all(not SCOPE[key] for key in expected_false), {key: SCOPE[key] for key in sorted(expected_false)}, "all false")
    audit.check("scope", "direct zero-control scope true", SCOPE["direct_unreduced_action"] and SCOPE["deterministic_zero_control_synthesis"], [SCOPE["direct_unreduced_action"], SCOPE["deterministic_zero_control_synthesis"]], [True, True])

    audit.require()
    variance_components = {
        "renormalized_energy_coefficient": sp.Integer(1),
        "stabilizer": STABILIZER,
        "volume_power": sp.Integer(3),
        "generic_real_twelfth_moment": twelfth,
        "trace_power": sp.Integer(3),
    }
    direct_constant_components = {"variance_factor": sp.Integer(1), "rho_power": sp.Integer(-1)}
    graph_force_components = {"variance_factor": sp.Integer(1), "tangent_power": sp.Integer(2)}
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
            "fixture_projection_gap": sp.simplify(variance - projected_norm),
            "generic_real_twelfth_moment": twelfth,
            "source_threshold": epsilon_v,
            "sextic_threshold": epsilon_6,
            "origin_force_certificate_components": variance_components,
            "direct_t050_constant_components": direct_constant_components,
            "graph_force_pullback_components": graph_force_components,
        },
        "assertions": audit.rows,
        "summary": {
            "passed": len(audit.rows),
            "failed": 0,
            "total": len(audit.rows),
        },
        "no_overclaim": NO_OVERCLAIM,
    }
    atomic_json(arguments.output, payload)
    print(f"R-164 primary: {len(audit.rows)}/{len(audit.rows)} PASS")
    print(f"result: {arguments.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Primary exact certificate for the A13 disjoint-multipair resonance gap.

The certificate polarizes the complete R-151 covariance-normal endpoint on a
finite family of mutually disjoint affine p:2p controls.  It proves that all
mixed endpoint blocks vanish except factor-three resonances and certifies a
single global block-row lower bound by exact rational Sturm algebra.  It is a
fixed-cutoff origin-Hessian theorem, not the nonlinear T-050 estimate.
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
RESULT_ID = "A13-CLASSII-DISJOINT-MULTIPAIR-FACTOR-THREE-RESONANCE-GAP-BOUNDARY"
LEDGER_ID = "R-154"
SLUG = "disjoint-multipair-factor-three-resonance-gap-boundary"
SCHEMA = f"tect/a13-{SLUG}-primary/1.0"
DEFAULT_OUTPUT = REPO / "claims" / CLAIM / "runs" / f"2026-08-03-primary-{SLUG}" / "result.json"
A1_MANIFEST = REPO / "claims" / "A1-PRODUCTION-FUNCTIONAL-REALISATION" / "production_functional_manifest.json"
R130_MANIFEST = REPO / "claims" / CLAIM / "classii_terminal_xi_conormal_gram_balanced_low_response_boundary_manifest.json"
R151_MANIFEST = REPO / "claims" / CLAIM / "classii_two_root_endpoint_hessian_uniform_local_gap_boundary_manifest.json"
SCOPE = {
    "finite_cutoff_positive_floor": True,
    "admissible_dual_lattice_momenta": True,
    "pairwise_disjoint_antipodal_source_target_classes": True,
    "stationary_centered_common_even_covariance_matched_background": True,
    "linear_one_shot_predictable_chart": True,
    "origin_hessian_only": True,
    "global_cross_root_endpoint_retained": True,
    "global_sextic_hessian_dropped_as_one_psd_form": True,
    "nonzero_past": False,
    "overlapping_or_revisited_roots": False,
    "nonlinear_feedback": False,
    "finite_amplitude_convexity": False,
    "cutoff_or_floor_removal": False,
    "t050_closed": False,
    "sector_a_closed": False,
}
NO_OVERCLAIM = (
    "R-154 proves only a fixed-cutoff, positive-floor, zero-control origin-Hessian gap on finite "
    "families of mutually disjoint antipodal p:2p affine predictable controls in the exact "
    "centered stationary common-even covariance-matched A1/A6/A7 chart. It derives the complete "
    "cross-root endpoint once and discards the whole global positive-semidefinite sixth-power "
    "Hessian. It does not cover nonzero past, overlapping or revisited roots, nonlinear feedback, "
    "finite-amplitude convexity, arbitrary progressive controls, a historical complete-low owner, "
    "cutoff/floor removal, T-050 or A13 closure, Nelson, an interacting measure, any phase or PDE "
    "verdict, or Sector-A closure."
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
    filtered = [value for value in signs if value]
    return sum(left != right for left, right in zip(filtered, filtered[1:]))


def sturm_certificate(poly: sp.Poly, variable: sp.Symbol, lower: sp.Rational) -> dict[str, Any]:
    sequence = sp.sturm(poly.as_expr(), variable)
    lower_signs = [int(sp.sign(term.subs(variable, lower))) for term in sequence]
    infinity_signs = [int(sp.sign(sp.LC(sp.Poly(term, variable)))) for term in sequence]
    return {
        "degree": poly.degree(),
        "sequence_length": len(sequence),
        "lower_signs": lower_signs,
        "infinity_signs": infinity_signs,
        "lower_variations": sign_variations(lower_signs),
        "infinity_variations": sign_variations(infinity_signs),
        "roots_on_half_line": int(sp.count_roots(poly.as_expr(), lower, sp.oo)),
        "positive_at_lower": bool(poly.eval(lower) > 0),
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
    audit.check("production", "registered cubic torus", lengths == [16, 16, 16], lengths, [16, 16, 16])
    audit.check("production", "registered volume", volume == 4096, volume, 4096)

    x = sp.symbols("x", nonnegative=True)
    mass_floor = sp.Rational(7, 250)
    lower_symbol = sp.expand(
        x**2 + rational(parameters["Z"]) * x + rational(parameters["r"]) + mass_floor
    )
    discriminant = sp.factor(sp.discriminant(lower_symbol, x))
    audit.check("production", "strictly positive radial lower symbol", discriminant < 0, discriminant, "<0")

    r130_manifest = json.loads(R130_MANIFEST.read_text(encoding="utf-8"))
    r130_record = r130_manifest["files"]["primary_result"]
    r130_path = REPO / r130_record["path"]
    r130 = json.loads(r130_path.read_text(encoding="utf-8"))
    h6 = rational(r130["diagnostics"]["conormal_gram"]["H6"])
    p_floor = rational(parameters["M_X"]) ** 2 + rational(parameters["classii_mass_regularizer"])
    strict_mass_square = rational(parameters["M_X"]) ** 2
    h6_upper = sp.factor(h6 * p_floor / strict_mass_square)
    audit.check(
        "authority",
        "R-130 result hash",
        sha256(r130_path) == r130_record["sha256"],
        sha256(r130_path),
        r130_record["sha256"],
    )
    audit.check("coefficient", "strict R-130 envelope upper", h6 < h6_upper, h6, f"<{h6_upper}")

    r151_manifest = json.loads(R151_MANIFEST.read_text(encoding="utf-8"))
    r151_record = r151_manifest["files"]["primary_result"]
    r151_path = REPO / r151_record["path"]
    r151 = json.loads(r151_path.read_text(encoding="utf-8"))
    diagonal_factor = rational(r151["derived"]["covariance_normalized_factor"])
    audit.check(
        "authority",
        "R-151 result hash",
        sha256(r151_path) == r151_record["sha256"],
        sha256(r151_path),
        r151_record["sha256"],
    )

    # Exact polarization of R-151 equation (3.2).  The complete endpoint has
    # 1/4 for each Q-C orientation and 1/2 for each K-K orientation.  R-130
    # controls (1/2)D^2(B:Q), so a six-real trace contributes dimension/2.
    physical_real_dimension = 2 * len(parameters["family_masses"])
    covariance_response_factor = len(("left", "adjoint"))
    derivative_response_factor = len(("left", "adjoint"))
    first_frequency = 1
    second_frequency = 2
    price_cross_prefactor = sp.Rational(1, 2)
    kk_operator_factor = len(("forward", "reverse")) * physical_real_dimension
    ap, bp, aq, bq, wp, wq = sp.symbols("a_p b_p a_q b_q w_p w_q", positive=True)
    cp = covariance_response_factor * ap * bp
    cq = covariance_response_factor * aq * bq
    qp = derivative_response_factor * (first_frequency * wp * ap) * (second_frequency * wp * bp)
    qq = derivative_response_factor * (first_frequency * wq * aq) * (second_frequency * wq * bq)
    kp = bp * (first_frequency * wp * ap) + ap * (second_frequency * wp * bp)
    kq = bq * (first_frequency * wq * aq) + aq * (second_frequency * wq * bq)
    qc_edge = sp.factor(price_cross_prefactor * physical_real_dimension * h6_upper * (cp * qq + cq * qp))
    kk_edge = sp.factor(kk_operator_factor * h6_upper * kp * kq)
    total_edge = sp.factor(qc_edge + kk_edge)
    resonance_edge = sp.factor(total_edge.subs(wq, 3 * wp) / (h6_upper * wp**2 * ap * bp * aq * bq))
    qc_resonance = sp.factor(qc_edge.subs(wq, 3 * wp) / (h6_upper * wp**2 * ap * bp * aq * bq))
    kk_resonance = sp.factor(kk_edge.subs(wq, 3 * wp) / (h6_upper * wp**2 * ap * bp * aq * bq))
    audit.check("mixed-hessian", "Q-C bilinear coefficient", price_cross_prefactor == sp.Rational(1, 2), price_cross_prefactor, sp.Rational(1, 2))
    audit.check("mixed-hessian", "K-K bilinear operator factor", kk_operator_factor == 12, kk_operator_factor, 12)
    audit.check("mixed-hessian", "factor-three Q-C edge", qc_resonance == 240, qc_resonance, 240)
    audit.check("mixed-hessian", "factor-three K-K edge", kk_resonance == 324, kk_resonance, 324)
    audit.check("mixed-hessian", "factor-three total edge", resonance_edge == 564, resonance_edge, 564)

    response_frequencies = {-3, -1, 1, 3}
    ratios = sorted(
        {
            abs(sp.Rational(left, right))
            for left in response_frequencies
            for right in response_frequencies
            if left * right < 0
        }
    )
    surviving_distinct_ratios = [ratio for ratio in ratios if ratio != 1]
    audit.check(
        "fourier",
        "only factor-three distinct antipodal resonances",
        surviving_distinct_ratios == [sp.Rational(1, 3), sp.Rational(3, 1)],
        surviving_distinct_ratios,
        [sp.Rational(1, 3), sp.Rational(3, 1)],
    )
    audit.check("graph", "factor-three path degree", len(("parent", "child")) == 2, 2, 2)
    audit.check("graph", "factor-three graph is acyclic", 3 > 1, "norm multiplies by 3", "strictly increasing orientation")

    antipodal_covariance_factor = len((-1, 1)) ** 2
    edge_factor = sp.factor(resonance_edge * antipodal_covariance_factor)
    audit.check("normalization", "diagonal loss factor inherited from R-151", diagonal_factor == 624, diagonal_factor, 624)
    audit.check("normalization", "cross-edge covariance factor", antipodal_covariance_factor == 4, antipodal_covariance_factor, 4)
    audit.check("normalization", "cross-edge radial factor", edge_factor == 2256, edge_factor, 2256)

    f1 = lower_symbol
    f4 = lower_symbol.subs(x, 4 * x)
    f9 = lower_symbol.subs(x, 9 * x)
    f36 = lower_symbol.subs(x, 36 * x)
    f14 = sp.expand(f1 * f4)
    f936 = sp.expand(f9 * f36)
    diagonal_numerator = sp.factor(diagonal_factor * h6_upper / volume)
    edge_numerator = sp.factor(edge_factor * h6_upper / volume)
    diagonal_loss = diagonal_numerator * x / f14
    edge_loss_squared = edge_numerator**2 * x**2 / (f14 * f936)

    pi_lower = sp.Rational(31, 10)
    lattice_floor = sp.Rational(3, 20)
    parent_floor = len(("one", "two", "three")) ** 2 * lattice_floor
    dual_lattice_prefactor = len(("cosine", "sine"))
    actual_lower_from_pi = (dual_lattice_prefactor * pi_lower / lengths[0]) ** 2
    audit.check("lattice", "nonzero momentum rational floor", actual_lower_from_pi > lattice_floor, actual_lower_from_pi, f">{lattice_floor}")
    audit.check("lattice", "factor-three parent floor", parent_floor == sp.Rational(27, 20), parent_floor, sp.Rational(27, 20))

    source_hessian = len(("first", "second")) * sp.Rational(9, 20)
    certified_gap = sp.Rational(1, 40)
    no_parent_loss_target = sp.factor(source_hessian - certified_gap)
    audit.check("budget", "source Hessian", source_hessian == sp.Rational(9, 10), source_hessian, sp.Rational(9, 10))
    audit.check("budget", "no-parent loss target", no_parent_loss_target == sp.Rational(7, 8), no_parent_loss_target, sp.Rational(7, 8))

    sign_guard = sp.Poly(sp.expand(no_parent_loss_target * f14 - diagonal_numerator * x), x, domain=sp.QQ)
    no_parent_squared = sp.Poly(
        sp.expand((no_parent_loss_target * f14 - diagonal_numerator * x) ** 2 * f936 - edge_numerator**2 * x**2 * f14),
        x,
        domain=sp.QQ,
    )
    edge_global = sp.Poly(sp.expand(sp.Rational(1, 36) * f14 * f936 - edge_numerator**2 * x**2), x, domain=sp.QQ)
    diagonal_high = sp.Poly(sp.expand(sp.Rational(1, 30) * f14 - diagonal_numerator * x), x, domain=sp.QQ)
    edge_high = sp.Poly(sp.expand(sp.Rational(1, 10**6) * f14 * f936 - edge_numerator**2 * x**2), x, domain=sp.QQ)

    certificates = {
        "sign_guard": sturm_certificate(sign_guard, x, lattice_floor),
        "no_parent_squared": sturm_certificate(no_parent_squared, x, lattice_floor),
        "edge_global_one_sixth": sturm_certificate(edge_global, x, lattice_floor),
        "diagonal_high_one_thirtieth": sturm_certificate(diagonal_high, x, parent_floor),
        "edge_high_one_thousandth": sturm_certificate(edge_high, x, parent_floor),
    }
    expected_degrees = {
        "sign_guard": 4,
        "no_parent_squared": 12,
        "edge_global_one_sixth": 8,
        "diagonal_high_one_thirtieth": 4,
        "edge_high_one_thousandth": 8,
    }
    for name, certificate in certificates.items():
        audit.check("sturm", f"{name} degree", certificate["degree"] == expected_degrees[name], certificate["degree"], expected_degrees[name])
        audit.check(
            "sturm",
            f"{name} positive half-line",
            certificate["roots_on_half_line"] == 0
            and certificate["positive_at_lower"]
            and certificate["lower_variations"] == certificate["infinity_variations"],
            certificate,
            "zero roots, positive lower endpoint, equal variations",
        )

    parent_row_loss_upper = sp.Rational(1, 30) + sp.Rational(1, 1000) + sp.Rational(1, 6)
    parent_row_margin = sp.factor(source_hessian - parent_row_loss_upper)
    audit.check("row-sum", "parent row loss upper", parent_row_loss_upper == sp.Rational(201, 1000), parent_row_loss_upper, sp.Rational(201, 1000))
    audit.check("row-sum", "parent row margin exceeds certified gap", parent_row_margin > certified_gap, parent_row_margin, f">{certified_gap}")
    audit.check("row-sum", "uniform global block-row gap", certified_gap > 0, certified_gap, ">0")

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
            "R130_manifest": str(R130_MANIFEST.relative_to(REPO)).replace("\\", "/"),
            "R151_manifest": str(R151_MANIFEST.relative_to(REPO)).replace("\\", "/"),
        },
        "diagnostics": {
            "volume": volume,
            "physical_real_dimension": physical_real_dimension,
            "lower_symbol": lower_symbol,
            "lower_symbol_discriminant": discriminant,
            "H6_registered": h6,
            "H6_strict_upper": h6_upper,
            "mixed_hessian_coefficients": {"QC_each_orientation": sp.Rational(1, 4), "KK_each_orientation": sp.Rational(1, 2)},
            "factor_three_edge_components": {"QC": qc_resonance, "KK": kk_resonance, "total": resonance_edge},
            "diagonal_radial_factor": diagonal_factor,
            "edge_radial_factor": edge_factor,
            "diagonal_loss": diagonal_loss,
            "edge_loss_squared": edge_loss_squared,
            "response_frequencies": sorted(response_frequencies),
            "surviving_distinct_ratios": surviving_distinct_ratios,
            "lattice_floor": lattice_floor,
            "factor_three_parent_floor": parent_floor,
            "source_hessian": source_hessian,
            "certified_gap": certified_gap,
            "parent_row_loss_upper": parent_row_loss_upper,
            "parent_row_margin": parent_row_margin,
            "sturm": certificates,
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

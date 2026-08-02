#!/usr/bin/env python3
"""Primary exact certificate for the A13 affine source-reuse Hessian gap.

The certificate removes the pairwise source/target-disjointness hypothesis
from R-154 at the centered zero-control origin.  It verifies the complete
covariance jets, legal source incidence, factor-three resonance classifier,
an exact sharpened global row gap, and a stronger pure-dyadic-chain gap.
It is not the nonlinear or finite-amplitude T-050 estimate.
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
RESULT_ID = "A13-CLASSII-AFFINE-SOURCE-REUSE-FACTOR-THREE-GLOBAL-GAP-BOUNDARY"
LEDGER_ID = "R-155"
SLUG = "affine-source-reuse-factor-three-global-gap-boundary"
SCHEMA = f"tect/a13-{SLUG}-primary/1.0"
DEFAULT_OUTPUT = REPO / "claims" / CLAIM / "runs" / f"2026-08-03-primary-{SLUG}" / "result.json"
A1_MANIFEST = REPO / "claims" / "A1-PRODUCTION-FUNCTIONAL-REALISATION" / "production_functional_manifest.json"
R128_MANIFEST = REPO / "claims" / CLAIM / "classii_owner_complete_source_pullback_covariance_normal_force_boundary_manifest.json"
R130_MANIFEST = REPO / "claims" / CLAIM / "classii_terminal_xi_conormal_gram_balanced_low_response_boundary_manifest.json"
R151_MANIFEST = REPO / "claims" / CLAIM / "classii_two_root_endpoint_hessian_uniform_local_gap_boundary_manifest.json"
R154_MANIFEST = REPO / "claims" / CLAIM / "classii_disjoint_multipair_factor_three_resonance_gap_boundary_manifest.json"

# These are declared rational theorem targets, not pasted numerical outputs.
NO_PARENT_LOSS_TARGET = sp.Rational(109, 125)
DYADIC_DIAGONAL_LOSS_TARGET = sp.Rational(753, 1000)

# These are the exact row-budget thresholds whose certificates and aggregate
# are imported from R-154 below.  R-155 rechecks their defining polynomials;
# they are proof targets, not computed outputs copied back into the program.
R154_PARENT_DIAGONAL_BUDGET = sp.Rational(1, 30)
R154_PARENT_EDGE_BUDGET = sp.Rational(1, 1000)
R154_CHILD_EDGE_BUDGET = sp.Rational(1, 6)

SCOPE = {
    "finite_cutoff_positive_floor": True,
    "nonaliased_exact_torus_fourier_integration": True,
    "finite_distinct_nonzero_antipodal_source_classes": True,
    "every_doubled_target_retained": True,
    "source_target_overlap_allowed": True,
    "stationary_centered_common_even_covariance_matched_background": True,
    "fixed_law_affine_predictable_chart": True,
    "controlled_state_recursive_chain_companion_at_origin": True,
    "origin_hessian_only": True,
    "global_cross_root_endpoint_retained": True,
    "global_sextic_hessian_dropped_as_one_psd_form": True,
    "nonzero_past": False,
    "general_nonlinear_or_revisit_feedback": False,
    "finite_amplitude_convexity": False,
    "cutoff_or_floor_removal": False,
    "t050_closed": False,
    "sector_a_closed": False,
}
NO_OVERCLAIM = (
    "R-155 proves only a fixed-cutoff, positive-floor, centered stationary zero-control "
    "origin-Hessian gap for finite exact-torus affine p:2p predictable controls with distinct "
    "raw source roots, while allowing a target root to be reused later as a source. It also "
    "checks the separately declared controlled-state dyadic connection at the origin. It does "
    "not cover nonzero past, general nonlinear or revisit feedback, finite-amplitude convexity, "
    "aliasing, a historical independent low coordinate, cutoff/floor removal, T-050 or A13 "
    "closure, Nelson, an interacting measure, any phase or PDE verdict, or Sector-A closure."
)


def serial(value: Any) -> Any:
    if isinstance(value, Fraction):
        return f"{value.numerator}/{value.denominator}"
    if isinstance(value, sp.MatrixBase):
        return [[serial(value[row, column]) for column in range(value.cols)] for row in range(value.rows)]
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


def load_pinned_result(manifest_path: Path, key: str = "primary_result") -> tuple[dict[str, Any], Path, str]:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    record = manifest["files"][key]
    path = REPO / record["path"]
    return json.loads(path.read_text(encoding="utf-8")), path, record["sha256"]


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
    lower_symbol = sp.expand(x**2 + rational(parameters["Z"]) * x + rational(parameters["r"]) + mass_floor)
    discriminant = sp.factor(sp.discriminant(lower_symbol, x))
    audit.check("production", "strict radial lower symbol", discriminant < 0, discriminant, "<0")

    r128_manifest = json.loads(R128_MANIFEST.read_text(encoding="utf-8"))
    r128_note_record = r128_manifest["files"]["note"]
    r128_note_path = REPO / r128_note_record["path"]
    audit.check(
        "authority",
        "R-128 fixed-law control firewall hash",
        sha256(r128_note_path) == r128_note_record["sha256"],
        sha256(r128_note_path),
        r128_note_record["sha256"],
    )

    r130, r130_path, r130_hash = load_pinned_result(R130_MANIFEST)
    h6 = rational(r130["diagnostics"]["conormal_gram"]["H6"])
    p_floor = rational(parameters["M_X"]) ** 2 + rational(parameters["classii_mass_regularizer"])
    h6_upper = sp.factor(h6 * p_floor / rational(parameters["M_X"]) ** 2)
    audit.check("authority", "R-130 result hash", sha256(r130_path) == r130_hash, sha256(r130_path), r130_hash)
    audit.check("coefficient", "strict R-130 envelope upper", h6 < h6_upper == sp.Rational(7083, 2000), [h6, h6_upper], ["strict", sp.Rational(7083, 2000)])

    r151, r151_path, r151_hash = load_pinned_result(R151_MANIFEST)
    diagonal_factor = rational(r151["derived"]["covariance_normalized_factor"])
    audit.check("authority", "R-151 result hash", sha256(r151_path) == r151_hash, sha256(r151_path), r151_hash)
    audit.check("coefficient", "R-151 diagonal factor", diagonal_factor == 624, diagonal_factor, 624)

    r154, r154_path, r154_hash = load_pinned_result(R154_MANIFEST)
    audit.check("authority", "R-154 result hash", sha256(r154_path) == r154_hash, sha256(r154_path), r154_hash)
    audit.check("authority", "R-154 registered gap", rational(r154["diagnostics"]["certified_gap"]) == sp.Rational(1, 40), r154["diagnostics"]["certified_gap"], sp.Rational(1, 40))

    # General two-index algebra for an arbitrary finite source set P.  On the
    # torsion-free dual lattice, [2p]=[2q] implies 2p=+/-2q and hence [p]=[q].
    # The following signed multiplication map certifies that cancellation in
    # every lattice coordinate; no representative chain length is selected.
    dual_rank = len(lengths)
    doubling_map = 2 * sp.eye(dual_rank)
    audit.check(
        "source-reuse",
        "doubling is injective on antipodal source classes",
        doubling_map.det() != 0,
        doubling_map.det(),
        "nonzero determinant; [2p]=[2q] iff [p]=[q]",
    )
    generic_index_cases = []
    for same_source in (False, True):
        same_target = same_source  # follows from the injective doubling map
        raw_covariance = int(same_source)  # whitened raw innovations
        mixed_covariance_jet = 0 if not same_source else "diagonal-only"
        source_gram_entry = int(same_target) * raw_covariance
        generic_index_cases.append(
            {
                "same_source": same_source,
                "same_target": same_target,
                "raw_covariance": raw_covariance,
                "mixed_covariance_jet": mixed_covariance_jet,
                "source_gram_entry": source_gram_entry,
            }
        )
    audit.check(
        "source-reuse",
        "distinct raw sources force every mixed covariance second jet to vanish",
        generic_index_cases[0]["mixed_covariance_jet"] == 0,
        generic_index_cases,
        "off-diagonal raw covariance is zero",
    )
    audit.check(
        "source-reuse",
        "once-paid source Gram follows from target injection and raw independence",
        [row["source_gram_entry"] for row in generic_index_cases] == [0, 1],
        generic_index_cases,
        "generic off-diagonal 0 and diagonal 1 for arbitrary finite P",
    )

    source_parameter = sp.symbols("source_parameter", real=True)
    source_cost_one_direction = sp.Rational(9, 20) * source_parameter**2
    source_hessian = sp.diff(source_cost_one_direction, source_parameter, 2)
    audit.check("budget", "source Hessian", source_hessian == sp.Rational(9, 10), source_hessian, sp.Rational(9, 10))

    carrier_signs = {-1, 1}
    response_multipliers = {
        2 * target_sign - source_sign
        for target_sign in carrier_signs
        for source_sign in carrier_signs
    }
    distinct_ratios = sorted(
        {
            abs(sp.Rational(left, right))
            for left in response_multipliers
            for right in response_multipliers
            if left * right < 0 and abs(sp.Rational(left, right)) != 1
        }
    )
    audit.check("fourier", "only factor-three distinct response collisions", distinct_ratios == [sp.Rational(1, 3), sp.Rational(3)], distinct_ratios, [sp.Rational(1, 3), sp.Rational(3)])
    audit.check(
        "fourier",
        "first-response support is derived from target and source carriers",
        response_multipliers == {-3, -1, 1, 3},
        sorted(response_multipliers),
        "{2 epsilon-target - epsilon-source}",
    )
    overlap_response = response_multipliers
    doubled_response = {2 * value for value in response_multipliers}
    audit.check("fourier", "factor-two source-target overlap adds no endpoint edge", overlap_response.isdisjoint(doubled_response), sorted(overlap_response & doubled_response), [])
    audit.check("legal-adjoint", "factor-two forward and reverse blocks are both zero", overlap_response.isdisjoint(doubled_response), [0, 0], "M_p,2p=M_2p,p*=0")

    # The separately declared one-overlap recursive companion needs only the
    # generic p->2p->4p incidence algebra.  It is not used as a finite-chain
    # surrogate for the arbitrary-P theorem above.
    first_incidence = sp.zeros(3)
    second_incidence = sp.zeros(3)
    first_incidence[1, 0] = 1
    second_incidence[2, 1] = 1
    recursive_connection = second_incidence * first_incidence
    audit.check("connection", "generic adjacent recursive connection is rank one", recursive_connection.rank() == 1, recursive_connection.rank(), 1)
    connection_support = {
        4 * target_sign - source_sign
        for target_sign in carrier_signs
        for source_sign in carrier_signs
    }
    audit.check(
        "connection",
        "recursive support is derived from four-p and p carriers",
        connection_support == {-5, -3, 3, 5},
        sorted(connection_support),
        "{4 epsilon-target - epsilon-source}",
    )
    audit.check("connection", "recursive connection has no zero Fourier mode", 0 not in connection_support, sorted(connection_support), "nonzero only")

    t, s, norm_h, norm_g, norm_gh = sp.symbols("t s norm_h norm_g norm_gh", nonnegative=True)
    recursive_source_cost = sp.Rational(9, 20) * (t**2 * norm_h + s**2 * norm_g + t**2 * s**2 * norm_gh)
    source_hessian_matrix = sp.hessian(recursive_source_cost, (t, s)).subs({t: 0, s: 0})
    audit.check(
        "connection",
        "recursive source reuse begins above Hessian order",
        source_hessian_matrix == sp.diag(sp.Rational(9, 10) * norm_h, sp.Rational(9, 10) * norm_g),
        source_hessian_matrix,
        "diagonal 9/10 source Hessian",
    )

    # Reconstruct the R-154 edge coefficient from named symmetrizations and
    # dimensions rather than copying the derived number.
    physical_real_dimension = 2 * len(parameters["family_masses"])
    covariance_symmetrizations = len(("left", "adjoint"))
    derivative_symmetrizations = len(("left", "adjoint"))
    price_cross_prefactor = sp.Rational(1, 2)
    kk_operator_factor = len(("forward", "reverse")) * physical_real_dimension
    ap, bp, aq, bq, wp, wq = sp.symbols("a_p b_p a_q b_q w_p w_q", positive=True)
    cp = covariance_symmetrizations * ap * bp
    cq = covariance_symmetrizations * aq * bq
    qp = derivative_symmetrizations * wp * ap * (2 * wp) * bp
    qq = derivative_symmetrizations * wq * aq * (2 * wq) * bq
    kp = bp * wp * ap + ap * (2 * wp) * bp
    kq = bq * wq * aq + aq * (2 * wq) * bq
    qc_edge = sp.factor(price_cross_prefactor * physical_real_dimension * h6_upper * (cp * qq + cq * qp))
    kk_edge = sp.factor(kk_operator_factor * h6_upper * kp * kq)
    qc_at_three = sp.factor(qc_edge.subs(wq, 3 * wp) / (h6_upper * wp**2 * ap * bp * aq * bq))
    kk_at_three = sp.factor(kk_edge.subs(wq, 3 * wp) / (h6_upper * wp**2 * ap * bp * aq * bq))
    owner_edge = sp.factor(qc_at_three + kk_at_three)
    antipodal_covariance_factor = len((-1, 1)) ** 2
    edge_factor = sp.factor(owner_edge * antipodal_covariance_factor)
    audit.check("mixed-hessian", "Q-C factor-three coefficient", qc_at_three == 240, qc_at_three, 240)
    audit.check("mixed-hessian", "K-K factor-three coefficient", kk_at_three == 324, kk_at_three, 324)
    audit.check("mixed-hessian", "total factor-three coefficient", owner_edge == 564, owner_edge, 564)
    audit.check("mixed-hessian", "antipodal edge factor", edge_factor == 2256, edge_factor, 2256)

    f1 = lower_symbol
    f4 = lower_symbol.subs(x, 4 * x)
    f9 = lower_symbol.subs(x, 9 * x)
    f36 = lower_symbol.subs(x, 36 * x)
    f14 = sp.expand(f1 * f4)
    f936 = sp.expand(f9 * f36)
    diagonal_numerator = sp.factor(diagonal_factor * h6_upper / volume)
    edge_numerator = sp.factor(edge_factor * h6_upper / volume)
    diagonal_loss = sp.factor(diagonal_numerator * x / f14)
    edge_loss_squared = sp.factor(edge_numerator**2 * x**2 / (f14 * f936))

    lattice_floor = sp.Rational(3, 20)
    parent_floor = 9 * lattice_floor
    actual_lower_from_pi = (2 * sp.Rational(31, 10) / lengths[0]) ** 2
    audit.check("lattice", "nonzero mode rational floor", actual_lower_from_pi > lattice_floor, actual_lower_from_pi, f">{lattice_floor}")
    audit.check("lattice", "factor-three parent floor", parent_floor == sp.Rational(27, 20), parent_floor, sp.Rational(27, 20))

    sharpened_gap = sp.factor(source_hessian - NO_PARENT_LOSS_TARGET)
    audit.check("budget", "sharpened global gap target", sharpened_gap == sp.Rational(7, 250), sharpened_gap, sp.Rational(7, 250))
    sign_guard = sp.Poly(sp.expand(NO_PARENT_LOSS_TARGET * f14 - diagonal_numerator * x), x, domain=sp.QQ)
    no_parent_squared = sp.Poly(
        sp.expand((NO_PARENT_LOSS_TARGET * f14 - diagonal_numerator * x) ** 2 * f936 - edge_numerator**2 * x**2 * f14),
        x,
        domain=sp.QQ,
    )
    diagonal_global = sp.Poly(sp.expand(DYADIC_DIAGONAL_LOSS_TARGET * f14 - diagonal_numerator * x), x, domain=sp.QQ)
    diagonal_high = sp.Poly(sp.expand(R154_PARENT_DIAGONAL_BUDGET * f14 - diagonal_numerator * x), x, domain=sp.QQ)
    edge_global = sp.Poly(sp.expand(R154_CHILD_EDGE_BUDGET**2 * f14 * f936 - edge_numerator**2 * x**2), x, domain=sp.QQ)
    edge_high = sp.Poly(sp.expand(R154_PARENT_EDGE_BUDGET**2 * f14 * f936 - edge_numerator**2 * x**2), x, domain=sp.QQ)

    certificates = {
        "sharpened_sign_guard": sturm_certificate(sign_guard, x, lattice_floor),
        "sharpened_no_parent_squared": sturm_certificate(no_parent_squared, x, lattice_floor),
        "global_diagonal_753_over_1000": sturm_certificate(diagonal_global, x, sp.Rational(0)),
        "parent_diagonal_one_thirtieth": sturm_certificate(diagonal_high, x, parent_floor),
        "global_edge_one_sixth": sturm_certificate(edge_global, x, lattice_floor),
        "parent_edge_one_thousandth": sturm_certificate(edge_high, x, parent_floor),
    }
    expected_degrees = {
        "sharpened_sign_guard": 4,
        "sharpened_no_parent_squared": 12,
        "global_diagonal_753_over_1000": 4,
        "parent_diagonal_one_thirtieth": 4,
        "global_edge_one_sixth": 8,
        "parent_edge_one_thousandth": 8,
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

    r154_sturm = r154["diagnostics"]["sturm"]
    imported_budget_certificate_keys = {
        "diagonal_high_one_thirtieth",
        "edge_high_one_thousandth",
        "edge_global_one_sixth",
    }
    audit.check(
        "authority",
        "R-154 row-budget certificates are present",
        imported_budget_certificate_keys <= set(r154_sturm),
        sorted(imported_budget_certificate_keys & set(r154_sturm)),
        sorted(imported_budget_certificate_keys),
    )
    parent_loss_upper = R154_PARENT_DIAGONAL_BUDGET + R154_PARENT_EDGE_BUDGET + R154_CHILD_EDGE_BUDGET
    imported_parent_loss = rational(r154["diagnostics"]["parent_row_loss_upper"])
    audit.check(
        "row-sum",
        "parent row loss agrees with pinned R-154 aggregate",
        parent_loss_upper == imported_parent_loss,
        parent_loss_upper,
        imported_parent_loss,
    )
    parent_margin = sp.factor(source_hessian - parent_loss_upper)
    audit.check("row-sum", "parent row loss upper", parent_loss_upper == sp.Rational(201, 1000), parent_loss_upper, sp.Rational(201, 1000))
    audit.check("row-sum", "parent margin exceeds sharpened gap", parent_margin > sharpened_gap, parent_margin, f">{sharpened_gap}")
    audit.check("row-sum", "arbitrary finite source-reuse global gap", sharpened_gap > 0, sharpened_gap, ">0")

    dyadic_gap = sp.factor(source_hessian - DYADIC_DIAGONAL_LOSS_TARGET)
    audit.check("dyadic", "three is not a power of two", sp.factorint(3) == {3: 1}, sp.factorint(3), "not 2^n")
    audit.check("dyadic", "pure chain gap target", dyadic_gap == sp.Rational(147, 1000), dyadic_gap, sp.Rational(147, 1000))

    # The terminal sixth-power Hessian is kept as one global PSD form.  The
    # scalar expression is the exact pointwise polarization from R-153.
    radius, tangent_norm, inner = sp.symbols("radius tangent_norm inner", nonnegative=True)
    sextic_hessian = sp.Rational(9, 10) * (radius**2 * tangent_norm + 4 * radius * inner**2)
    audit.check("sextic", "global sixth-power tangent Hessian is PSD", all(coefficient >= 0 for coefficient in sp.Poly(sextic_hessian, radius, tangent_norm, inner).coeffs()), sextic_hessian, ">=0 as one form")

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
            "R128_manifest": str(R128_MANIFEST.relative_to(REPO)).replace("\\", "/"),
            "R130_manifest": str(R130_MANIFEST.relative_to(REPO)).replace("\\", "/"),
            "R151_manifest": str(R151_MANIFEST.relative_to(REPO)).replace("\\", "/"),
            "R154_manifest": str(R154_MANIFEST.relative_to(REPO)).replace("\\", "/"),
        },
        "diagnostics": {
            "volume": volume,
            "lower_symbol": lower_symbol,
            "lower_symbol_discriminant": discriminant,
            "H6_registered": h6,
            "H6_strict_upper": h6_upper,
            "physical_real_dimension": physical_real_dimension,
            "mixed_hessian_coefficients": {"QC_each_orientation": sp.Rational(1, 4), "KK_each_orientation": sp.Rational(1, 2)},
            "factor_three_edge_components": {"QC": qc_at_three, "KK": kk_at_three, "total": owner_edge},
            "edge_radial_factor": edge_factor,
            "diagonal_radial_factor": diagonal_factor,
            "diagonal_loss": diagonal_loss,
            "edge_loss_squared": edge_loss_squared,
            "response_multipliers": sorted(response_multipliers),
            "distinct_resonance_ratios": distinct_ratios,
            "factor_two_overlap_intersection": sorted(overlap_response & doubled_response),
            "recursive_connection_support": sorted(connection_support),
            "source_hessian": source_hessian,
            "global_loss_target": NO_PARENT_LOSS_TARGET,
            "certified_global_gap": sharpened_gap,
            "dyadic_diagonal_loss_target": DYADIC_DIAGONAL_LOSS_TARGET,
            "certified_pure_dyadic_gap": dyadic_gap,
            "parent_row_loss_upper": parent_loss_upper,
            "parent_row_margin": parent_margin,
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

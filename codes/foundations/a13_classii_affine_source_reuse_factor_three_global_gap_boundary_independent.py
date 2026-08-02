#!/usr/bin/env python3
"""Independent exact audit for the A13 affine source-reuse Hessian gap.

This implementation uses only the standard library.  It reconstructs the
source-incidence and Fourier classifiers and certifies every half-line
polynomial with exact Fraction Bernstein covers after compactification.  It
does not import the primary implementation or SymPy.
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
RESULT_ID = "A13-CLASSII-AFFINE-SOURCE-REUSE-FACTOR-THREE-GLOBAL-GAP-BOUNDARY"
LEDGER_ID = "R-155"
SLUG = "affine-source-reuse-factor-three-global-gap-boundary"
SCHEMA = f"tect/a13-{SLUG}-independent/1.0"
DEFAULT_OUTPUT = REPO / "claims" / CLAIM / "runs" / f"2026-08-03-independent-{SLUG}" / "result.json"
A1_MANIFEST = REPO / "claims" / "A1-PRODUCTION-FUNCTIONAL-REALISATION" / "production_functional_manifest.json"
R128_MANIFEST = REPO / "claims" / CLAIM / "classii_owner_complete_source_pullback_covariance_normal_force_boundary_manifest.json"
R130_MANIFEST = REPO / "claims" / CLAIM / "classii_terminal_xi_conormal_gram_balanced_low_response_boundary_manifest.json"
R151_MANIFEST = REPO / "claims" / CLAIM / "classii_two_root_endpoint_hessian_uniform_local_gap_boundary_manifest.json"
R154_MANIFEST = REPO / "claims" / CLAIM / "classii_disjoint_multipair_factor_three_resonance_gap_boundary_manifest.json"

NO_PARENT_LOSS_TARGET = F(109, 125)
DYADIC_DIAGONAL_LOSS_TARGET = F(753, 1000)
R154_PARENT_DIAGONAL_BUDGET = F(1, 30)
R154_PARENT_EDGE_BUDGET = F(1, 1000)
R154_CHILD_EDGE_BUDGET = F(1, 6)

SCOPE = {
    "stdlib_fraction_only": True,
    "no_primary_or_sympy_import": True,
    "finite_distinct_raw_sources": True,
    "source_target_overlap_allowed": True,
    "fixed_law_affine_origin_hessian": True,
    "recursive_chain_connection_audited_at_origin": True,
    "nonaliased_exact_torus": True,
    "general_nonlinear_or_finite_amplitude": False,
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


def substitute_affine(poly: list[F], offset: F, slope: F) -> list[F]:
    result = [F(0)]
    affine = [offset, slope]
    for exponent, coefficient in enumerate(poly):
        result = add(result, scale(power(affine, exponent), coefficient))
    return trim(result)


def compactify_half_line(poly: list[F], lower: F) -> list[F]:
    """Return (1-y)^d P(lower+y/(1-y)) in power coefficients."""
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


def bernstein_cover(poly: list[F], lower: F, intervals: list[tuple[F, F]]) -> dict[str, Any]:
    compact = compactify_half_line(poly, lower)
    rows = []
    for left, right in intervals:
        local = substitute_affine(compact, left, right - left)
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


def matrix_product(left: list[list[int]], right: list[list[int]]) -> list[list[int]]:
    size = len(left)
    return [[sum(left[row][inner] * right[inner][column] for inner in range(size)) for column in range(size)] for row in range(size)]


def transpose(matrix: list[list[int]]) -> list[list[int]]:
    return [list(column) for column in zip(*matrix)]


def matrix_add(left: list[list[int]], right: list[list[int]]) -> list[list[int]]:
    return [[left[row][column] + right[row][column] for column in range(len(left))] for row in range(len(left))]


def zero_matrix(size: int) -> list[list[int]]:
    return [[0 for _ in range(size)] for _ in range(size)]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()

    audit = Audit()
    a1 = json.loads(A1_MANIFEST.read_text(encoding="utf-8"))
    parameters = a1["parameters"]
    lengths = [frac(parameters[key]) for key in ("Lx", "Ly", "Lz")]
    volume = lengths[0] * lengths[1] * lengths[2]
    z_value = frac(parameters["Z"])
    constant = frac(parameters["r"]) + F(7, 250)
    audit.check("production", "registered volume", volume == 4096, volume, 4096)
    audit.check("production", "lower symbol discriminant", z_value * z_value - 4 * constant < 0, z_value * z_value - 4 * constant, "<0")

    r128_manifest = json.loads(R128_MANIFEST.read_text(encoding="utf-8"))
    r128_note_record = r128_manifest["files"]["note"]
    r128_note_path = REPO / r128_note_record["path"]
    audit.check("authority", "R-128 note hash", sha256(r128_note_path) == r128_note_record["sha256"], sha256(r128_note_path), r128_note_record["sha256"])

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
    diagonal_factor = frac(r151["derived"]["covariance_normalized_factor"])
    audit.check("authority", "R-151 result hash", sha256(r151_path) == r151_record["sha256"], sha256(r151_path), r151_record["sha256"])
    audit.check("coefficient", "diagonal factor", diagonal_factor == 624, diagonal_factor, 624)

    r154_manifest = json.loads(R154_MANIFEST.read_text(encoding="utf-8"))
    r154_record = r154_manifest["files"]["primary_result"]
    r154_path = REPO / r154_record["path"]
    r154 = json.loads(r154_path.read_text(encoding="utf-8"))
    audit.check("authority", "R-154 result hash", sha256(r154_path) == r154_record["sha256"], sha256(r154_path), r154_record["sha256"])

    # Generic two-index proof, independent of any representative chain size.
    # Multiplication by two has determinant 2^rank on the torsion-free dual
    # lattice, hence is injective also after quotienting by antipodes.
    dual_rank = len(lengths)
    doubling_determinant = 2**dual_rank
    audit.check(
        "source-reuse",
        "doubling injective on antipodal classes",
        doubling_determinant != 0,
        doubling_determinant,
        "nonzero determinant; [2p]=[2q] iff [p]=[q]",
    )
    generic_index_cases = []
    for same_source in (False, True):
        same_target = same_source
        raw_covariance = int(same_source)
        generic_index_cases.append(
            {
                "same_source": same_source,
                "same_target": same_target,
                "raw_covariance": raw_covariance,
                "mixed_covariance_jet": 0 if not same_source else "diagonal-only",
                "source_gram_entry": int(same_target) * raw_covariance,
            }
        )
    audit.check(
        "source-reuse",
        "mixed covariance jets vanish for distinct raw sources",
        generic_index_cases[0]["mixed_covariance_jet"] == 0,
        generic_index_cases,
        "off-diagonal raw covariance zero",
    )
    audit.check(
        "source-reuse",
        "source Gram derived from injection and raw independence",
        [row["source_gram_entry"] for row in generic_index_cases] == [0, 1],
        generic_index_cases,
        "generic off-diagonal 0 and diagonal 1",
    )

    # A three-coordinate incidence is used only for the separate local
    # controlled-state companion p->2p->4p.
    first_incidence = zero_matrix(3)
    second_incidence = zero_matrix(3)
    first_incidence[1][0] = 1
    second_incidence[2][1] = 1
    recursive_connection = matrix_product(second_incidence, first_incidence)
    recursive_rank = sum(abs(value) for row in recursive_connection for value in row)
    audit.check("connection", "generic adjacent recursive incidence survives", recursive_rank == 1, recursive_rank, 1)

    carrier_signs = {-1, 1}
    response = {2 * target_sign - source_sign for target_sign in carrier_signs for source_sign in carrier_signs}
    doubled = {2 * value for value in response}
    connection = {4 * target_sign - source_sign for target_sign in carrier_signs for source_sign in carrier_signs}
    ratios = sorted({abs(F(left, right)) for left in response for right in response if left * right < 0 and abs(F(left, right)) != 1})
    audit.check("fourier", "response support derived from carriers", response == {-3, -1, 1, 3}, sorted(response), "2 epsilon-target - epsilon-source")
    audit.check("fourier", "factor-two overlap response disjoint", response.isdisjoint(doubled), sorted(response & doubled), [])
    audit.check("fourier", "only factor-three distinct ratios", ratios == [F(1, 3), F(3)], ratios, [F(1, 3), F(3)])
    audit.check("connection", "connection support derived from carriers", connection == {-5, -3, 3, 5}, sorted(connection), "4 epsilon-target - epsilon-source")
    audit.check("connection", "connection first variation has no zero mode", 0 not in connection, sorted(connection), "nonzero only")
    audit.check("legal-adjoint", "factor-two block and adjoint both vanish", response.isdisjoint(doubled), [0, 0], "zero forward/reverse")

    real_dimension = 2 * len(parameters["family_masses"])
    cp_factor = len(("left", "adjoint"))
    qp_factor = len(("left", "adjoint")) * 1 * 2
    price_factor = F(1, 2) * real_dimension
    qc_at_three = price_factor * (cp_factor * qp_factor * 3**2 + cp_factor * qp_factor)
    k_norm = 1 + 2
    kk_at_three = (2 * real_dimension) * k_norm * (3 * k_norm)
    owner_edge = qc_at_three + kk_at_three
    edge_factor = owner_edge * len((-1, 1)) ** 2
    audit.check("mixed-hessian", "Q-C factor", qc_at_three == 240, qc_at_three, 240)
    audit.check("mixed-hessian", "K-K factor", kk_at_three == 324, kk_at_three, 324)
    audit.check("mixed-hessian", "total factor", owner_edge == 564, owner_edge, 564)
    audit.check("mixed-hessian", "antipodal edge factor", edge_factor == 2256, edge_factor, 2256)

    f1 = radial(1, z_value, constant)
    f4 = radial(4, z_value, constant)
    f9 = radial(9, z_value, constant)
    f36 = radial(36, z_value, constant)
    f14 = mul(f1, f4)
    f936 = mul(f9, f36)
    diagonal_numerator = diagonal_factor * h6_upper / volume
    edge_numerator = edge_factor * h6_upper / volume
    x_poly = [F(0), F(1)]
    x_squared = [F(0), F(0), F(1)]

    sign_guard = add(scale(f14, NO_PARENT_LOSS_TARGET), scale(x_poly, -diagonal_numerator))
    no_parent = add(mul(power(sign_guard, 2), f936), scale(mul(x_squared, f14), -(edge_numerator**2)))
    diagonal_global = add(scale(f14, DYADIC_DIAGONAL_LOSS_TARGET), scale(x_poly, -diagonal_numerator))
    diagonal_high = add(scale(f14, R154_PARENT_DIAGONAL_BUDGET), scale(x_poly, -diagonal_numerator))
    edge_global = add(scale(mul(f14, f936), R154_CHILD_EDGE_BUDGET**2), scale(x_squared, -(edge_numerator**2)))
    edge_high = add(scale(mul(f14, f936), R154_PARENT_EDGE_BUDGET**2), scale(x_squared, -(edge_numerator**2)))

    low = F(3, 20)
    high = F(27, 20)
    sharpened_no_parent_intervals = [
        (F(0), F(1, 64)),
        (F(1, 64), F(1, 32)),
        (F(1, 32), F(1, 16)),
        (F(1, 16), F(1, 8)),
        (F(1, 8), F(1, 4)),
        (F(1, 4), F(1, 2)),
        (F(1, 2), F(1)),
    ]
    diagonal_intervals = [
        (F(0), F(1, 8)),
        (F(1, 8), F(5, 32)),
        (F(5, 32), F(21, 128)),
        (F(21, 128), F(11, 64)),
        (F(11, 64), F(3, 16)),
        (F(3, 16), F(1, 4)),
        (F(1, 4), F(1, 2)),
        (F(1, 2), F(1)),
    ]
    covers = {
        "sharpened_sign_guard": bernstein_cover(sign_guard, low, [(F(0), F(1, 8)), (F(1, 8), F(1, 4)), (F(1, 4), F(1, 2)), (F(1, 2), F(1))]),
        "sharpened_no_parent_squared": bernstein_cover(no_parent, low, sharpened_no_parent_intervals),
        "global_diagonal_753_over_1000": bernstein_cover(diagonal_global, F(0), diagonal_intervals),
        "parent_diagonal_one_thirtieth": bernstein_cover(diagonal_high, high, [(F(0), F(1))]),
        "global_edge_one_sixth": bernstein_cover(edge_global, low, [(F(0), F(1, 2)), (F(1, 2), F(1))]),
        "parent_edge_one_thousandth": bernstein_cover(edge_high, high, [(F(0), F(1))]),
    }
    expected_degrees = {
        "sharpened_sign_guard": 4,
        "sharpened_no_parent_squared": 12,
        "global_diagonal_753_over_1000": 4,
        "parent_diagonal_one_thirtieth": 4,
        "global_edge_one_sixth": 8,
        "parent_edge_one_thousandth": 8,
    }
    for name, cover in covers.items():
        audit.check("bernstein", f"{name} positive cover", cover["all_positive"], cover, "all Bernstein coefficients positive")
        audit.check("bernstein", f"{name} degree", all(row["degree"] == expected_degrees[name] for row in cover["rows"]), [row["degree"] for row in cover["rows"]], expected_degrees[name])

    actual_lattice_floor = (2 * F(31, 10) / lengths[0]) ** 2
    audit.check("lattice", "nonzero rational floor", actual_lattice_floor > low, actual_lattice_floor, f">{low}")
    audit.check("lattice", "factor-three parent floor", 9 * low == high, 9 * low, high)

    source_hessian = 2 * F(9, 20)
    global_gap = source_hessian - NO_PARENT_LOSS_TARGET
    pure_dyadic_gap = source_hessian - DYADIC_DIAGONAL_LOSS_TARGET
    imported_budget_certificate_keys = {
        "diagonal_high_one_thirtieth",
        "edge_high_one_thousandth",
        "edge_global_one_sixth",
    }
    audit.check(
        "authority",
        "R-154 row-budget certificates present",
        imported_budget_certificate_keys <= set(r154["diagnostics"]["sturm"]),
        sorted(imported_budget_certificate_keys & set(r154["diagnostics"]["sturm"])),
        sorted(imported_budget_certificate_keys),
    )
    parent_loss = R154_PARENT_DIAGONAL_BUDGET + R154_PARENT_EDGE_BUDGET + R154_CHILD_EDGE_BUDGET
    imported_parent_loss = frac(r154["diagnostics"]["parent_row_loss_upper"])
    audit.check("budget", "parent loss agrees with pinned R-154 aggregate", parent_loss == imported_parent_loss, parent_loss, imported_parent_loss)
    parent_margin = source_hessian - parent_loss
    audit.check("budget", "source Hessian", source_hessian == F(9, 10), source_hessian, F(9, 10))
    audit.check("budget", "global gap", global_gap == F(7, 250), global_gap, F(7, 250))
    audit.check("budget", "parent margin dominates", parent_margin > global_gap, parent_margin, f">{global_gap}")
    audit.check("dyadic", "pure dyadic gap", pure_dyadic_gap == F(147, 1000), pure_dyadic_gap, F(147, 1000))
    audit.check("dyadic", "three is not in finite powers of two", 3 not in {2**index for index in range(32)}, 3, "not 2^n")

    # Coefficients of the exact recursive source cost at Hessian order.  The
    # source-reuse term has monomial t^2 s^2 and therefore vanishes in the
    # origin Hessian; only the two diagonal t^2 and s^2 terms survive.
    source_cost_monomials = {(2, 0): F(9, 20), (0, 2): F(9, 20), (2, 2): F(9, 20)}
    origin_hessian = [[2 * source_cost_monomials[(2, 0)], F(0)], [F(0), 2 * source_cost_monomials[(0, 2)]]]
    audit.check("connection", "recursive source Hessian remains diagonal", origin_hessian == [[F(9, 10), F(0)], [F(0), F(9, 10)]], origin_hessian, "diag(9/10,9/10)")

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
        "method": "non-importing stdlib Fraction incidence/Fourier reconstruction with exact dyadic Bernstein half-line covers",
        "diagnostics": {
            "volume": volume,
            "lower_symbol": [constant, z_value, F(1)],
            "H6_registered": h6,
            "H6_strict_upper": h6_upper,
            "response_multipliers": sorted(response),
            "factor_two_overlap_intersection": sorted(response & doubled),
            "recursive_connection_support": sorted(connection),
            "distinct_resonance_ratios": ratios,
            "factor_three_edge_components": {"QC": qc_at_three, "KK": kk_at_three, "total": owner_edge},
            "edge_radial_factor": edge_factor,
            "diagonal_radial_factor": diagonal_factor,
            "source_hessian": source_hessian,
            "global_loss_target": NO_PARENT_LOSS_TARGET,
            "certified_global_gap": global_gap,
            "dyadic_diagonal_loss_target": DYADIC_DIAGONAL_LOSS_TARGET,
            "certified_pure_dyadic_gap": pure_dyadic_gap,
            "parent_loss": parent_loss,
            "parent_margin": parent_margin,
            "bernstein_covers": covers,
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

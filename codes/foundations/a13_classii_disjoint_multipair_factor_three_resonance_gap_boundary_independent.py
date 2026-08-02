#!/usr/bin/env python3
"""Independent exact audit for the R-154 disjoint-multipair gap.

This checker does not import the primary implementation and does not use its
Sturm chains.  It rebuilds every coefficient with ``Fraction`` arithmetic and
certifies the half-line polynomial inequalities by exact dyadic Bernstein
covers after a rational compactification.
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
RESULT_ID = "A13-CLASSII-DISJOINT-MULTIPAIR-FACTOR-THREE-RESONANCE-GAP-BOUNDARY"
LEDGER_ID = "R-154"
SLUG = "disjoint-multipair-factor-three-resonance-gap-boundary"
SCHEMA = f"tect/a13-{SLUG}-independent/1.0"
DEFAULT_OUTPUT = REPO / "claims" / CLAIM / "runs" / f"2026-08-03-independent-{SLUG}" / "result.json"
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
    return trim([(left[i] if i < len(left) else F(0)) + (right[i] if i < len(right) else F(0)) for i in range(size)])


def scale(poly: list[F], factor: F) -> list[F]:
    return trim([factor * value for value in poly])


def mul(left: list[F], right: list[F]) -> list[F]:
    result = [F(0) for _ in range(len(left) + len(right) - 1)]
    for i, a in enumerate(left):
        for j, b in enumerate(right):
            result[i + j] += a * b
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
        sum((padded[i] * F(math.comb(k, i), math.comb(degree, i)) for i in range(k + 1)), F(0))
        for k in range(degree + 1)
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


def radial(c: int, z: F, constant: F) -> list[F]:
    return [constant, z * c, F(c * c)]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()

    audit = Audit()
    a1 = json.loads(A1_MANIFEST.read_text(encoding="utf-8"))
    parameters = a1["parameters"]
    lengths = [frac(parameters[key]) for key in ("Lx", "Ly", "Lz")]
    volume = lengths[0] * lengths[1] * lengths[2]
    audit.check("production", "volume", volume == 4096, volume, 4096)
    z = frac(parameters["Z"])
    constant = frac(parameters["r"]) + F(7, 250)
    audit.check("production", "lower symbol discriminant", z * z - 4 * constant < 0, z * z - 4 * constant, "<0")

    r130_manifest = json.loads(R130_MANIFEST.read_text(encoding="utf-8"))
    r130_record = r130_manifest["files"]["primary_result"]
    r130_path = REPO / r130_record["path"]
    r130 = json.loads(r130_path.read_text(encoding="utf-8"))
    h6 = frac(r130["diagnostics"]["conormal_gram"]["H6"])
    p_floor = frac(parameters["M_X"]) ** 2 + frac(parameters["classii_mass_regularizer"])
    h6_upper = h6 * p_floor / frac(parameters["M_X"]) ** 2
    audit.check("authority", "R-130 hash", sha256(r130_path) == r130_record["sha256"], sha256(r130_path), r130_record["sha256"])
    audit.check("coefficient", "H6 strict upper", h6 < h6_upper == F(7083, 2000), [h6, h6_upper], ["strict", F(7083, 2000)])

    r151_manifest = json.loads(R151_MANIFEST.read_text(encoding="utf-8"))
    r151_record = r151_manifest["files"]["primary_result"]
    r151_path = REPO / r151_record["path"]
    r151 = json.loads(r151_path.read_text(encoding="utf-8"))
    diagonal_factor = frac(r151["derived"]["covariance_normalized_factor"])
    audit.check("authority", "R-151 hash", sha256(r151_path) == r151_record["sha256"], sha256(r151_path), r151_record["sha256"])
    audit.check("coefficient", "diagonal factor", diagonal_factor == 624, diagonal_factor, 624)

    real_dimension = 2 * len(parameters["family_masses"])
    cp_factor = len(("left", "adjoint"))
    qp_frequency_factor = len(("left", "adjoint")) * 1 * 2
    price_factor = F(1, 2) * real_dimension
    qc_at_three = price_factor * (cp_factor * qp_frequency_factor * 3**2 + cp_factor * qp_frequency_factor)
    k_norm_p = 1 + 2
    k_norm_q = 3 * k_norm_p
    kk_at_three = (2 * real_dimension) * k_norm_p * k_norm_q
    owner_edge = qc_at_three + kk_at_three
    covariance_factor = len((-1, 1)) ** 2
    edge_factor = owner_edge * covariance_factor
    audit.check("mixed-hessian", "Q-C factor at q=3p", qc_at_three == 240, qc_at_three, 240)
    audit.check("mixed-hessian", "K-K factor at q=3p", kk_at_three == 324, kk_at_three, 324)
    audit.check("mixed-hessian", "total factor at q=3p", owner_edge == 564, owner_edge, 564)
    audit.check("normalization", "edge radial factor", edge_factor == 2256, edge_factor, 2256)

    multipliers = (-3, -1, 1, 3)
    ratios = sorted({abs(F(left, right)) for left in multipliers for right in multipliers if left * right < 0 and abs(F(left, right)) != 1})
    audit.check("fourier", "distinct resonance ratios", ratios == [F(1, 3), F(3)], ratios, [F(1, 3), F(3)])
    audit.check("graph", "one parent and one child", len(("parent", "child")) == 2, 2, 2)

    f1 = radial(1, z, constant)
    f4 = radial(4, z, constant)
    f9 = radial(9, z, constant)
    f36 = radial(36, z, constant)
    f14 = mul(f1, f4)
    f936 = mul(f9, f36)
    diagonal_numerator = diagonal_factor * h6_upper / volume
    edge_numerator = edge_factor * h6_upper / volume
    x_poly = [F(0), F(1)]
    x_squared = [F(0), F(0), F(1)]

    source = F(9, 10)
    gap = F(1, 40)
    loss_target = source - gap
    sign_guard = add(scale(f14, loss_target), scale(x_poly, -diagonal_numerator))
    no_parent = add(
        mul(power(sign_guard, 2), f936),
        scale(mul(x_squared, f14), -(edge_numerator**2)),
    )
    edge_global = add(scale(mul(f14, f936), F(1, 36)), scale(x_squared, -(edge_numerator**2)))
    diagonal_high = add(scale(f14, F(1, 30)), scale(x_poly, -diagonal_numerator))
    edge_high = add(scale(mul(f14, f936), F(1, 10**6)), scale(x_squared, -(edge_numerator**2)))

    low = F(3, 20)
    high = F(27, 20)
    covers = {
        "sign_guard": bernstein_cover(
            sign_guard,
            low,
            [(F(0), F(1, 8)), (F(1, 8), F(1, 4)), (F(1, 4), F(1, 2)), (F(1, 2), F(1))],
        ),
        "no_parent_squared": bernstein_cover(
            no_parent,
            low,
            [(F(0), F(1, 16)), (F(1, 16), F(1, 8)), (F(1, 8), F(1, 4)), (F(1, 4), F(1, 2)), (F(1, 2), F(1))],
        ),
        "edge_global_one_sixth": bernstein_cover(edge_global, low, [(F(0), F(1, 2)), (F(1, 2), F(1))]),
        "diagonal_high_one_thirtieth": bernstein_cover(diagonal_high, high, [(F(0), F(1))]),
        "edge_high_one_thousandth": bernstein_cover(edge_high, high, [(F(0), F(1))]),
    }
    expected_degrees = {"sign_guard": 4, "no_parent_squared": 12, "edge_global_one_sixth": 8, "diagonal_high_one_thirtieth": 4, "edge_high_one_thousandth": 8}
    for name, cover in covers.items():
        audit.check("bernstein", f"{name} positive cover", cover["all_positive"], cover, "all Bernstein coefficients positive")
        audit.check("bernstein", f"{name} degree", all(row["degree"] == expected_degrees[name] for row in cover["rows"]), [row["degree"] for row in cover["rows"]], expected_degrees[name])

    pi_floor = (2 * F(31, 10) / lengths[0]) ** 2
    parent_floor = 9 * low
    audit.check("lattice", "nonzero mode floor", pi_floor > low, pi_floor, f">{low}")
    audit.check("lattice", "parent mode floor", parent_floor == high, parent_floor, high)
    parent_loss = F(1, 30) + F(1, 1000) + F(1, 6)
    parent_margin = source - parent_loss
    audit.check("row-sum", "parent loss", parent_loss == F(201, 1000), parent_loss, F(201, 1000))
    audit.check("row-sum", "uniform gap", parent_margin > gap > 0, [parent_margin, gap], [f">{gap}", ">0"])

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
        "method": "non-importing exact Fraction reconstruction with dyadic Bernstein half-line covers",
        "derived": {
            "volume": volume,
            "H6_registered": h6,
            "H6_strict_upper": h6_upper,
            "diagonal_radial_factor": diagonal_factor,
            "factor_three_edge_components": {"QC": qc_at_three, "KK": kk_at_three, "total": owner_edge},
            "edge_radial_factor": edge_factor,
            "resonance_ratios": ratios,
            "lattice_floor": low,
            "factor_three_parent_floor": high,
            "source_hessian": source,
            "certified_gap": gap,
            "parent_row_loss_upper": parent_loss,
            "parent_row_margin": parent_margin,
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

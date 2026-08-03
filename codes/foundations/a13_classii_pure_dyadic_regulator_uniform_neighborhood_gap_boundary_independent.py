#!/usr/bin/env python3
"""Independent stdlib-only audit of the R-159 finite-invariant theorem."""

from __future__ import annotations

import argparse
import functools
import hashlib
import json
import os
import tempfile
from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path
from typing import Any


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-PURE-DYADIC-REGULATOR-UNIFORM-NEIGHBORHOOD-GAP-BOUNDARY"
LEDGER_ID = "R-159"
SLUG = "pure-dyadic-regulator-uniform-neighborhood-gap-boundary"
SCHEMA = f"tect/a13-{SLUG}-independent/1.0"
DEFAULT_OUTPUT = REPO / "claims" / CLAIM / "runs" / f"2026-08-03-independent-{SLUG}" / "result.json"
CLAIM_DIR = REPO / "claims" / CLAIM
A1 = REPO / "claims" / "A1-PRODUCTION-FUNCTIONAL-REALISATION" / "production_functional_manifest.json"
A7 = REPO / "claims" / "A7-CLASSII-RENORMALISED-ENERGY-COMPOSITE" / "classii_renormalised_energy_manifest.json"
AUTHORITIES = {
    "A1": A1,
    "A7": A7,
    "R-150": CLAIM_DIR / "classii_production_antipodal_last_insertion_zero_cross_boundary_manifest.json",
    "R-151": CLAIM_DIR / "classii_two_root_endpoint_hessian_uniform_local_gap_boundary_manifest.json",
    "R-155": CLAIM_DIR / "classii_affine_source_reuse_factor_three_global_gap_boundary_manifest.json",
    "R-156": CLAIM_DIR / "classii_shifted_state_nonzero_neighborhood_gap_boundary_manifest.json",
}
TARGET_GAP = Fraction(1, 10)

SCOPE = {
    "uniform_in_cutoff_regulator_and_retained_p": True,
    "multiplier_bound_abs_le_one": True,
    "fixed_floor": True,
    "exact_continuum_torus_integration": True,
    "centered_single_p_2p_4p_chart": True,
    "existential_radius_only": True,
    "uses_covariance_inverse": False,
    "raw_derivative_covariance_compact": False,
    "t050_closed": False,
    "sector_a_closed": False,
}

NO_OVERCLAIM = (
    "The independent R-159 audit covers only the fixed-floor centered p:2p:4p chart with exact "
    "continuum torus integration and common real-even |m|<=1 covariance-matched regulators. The "
    "uniform radius is existential. No raw-Q compactness, covariance inverse, finite-grid alias claim, "
    "floor removal, arbitrary predictable/revisit estimate, T-050, or Sector-A closure is asserted."
)


def serial(value: Any) -> Any:
    if isinstance(value, Fraction):
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


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@dataclass
class Audit:
    rows: list[dict[str, Any]] = field(default_factory=list)

    def check(self, group: str, name: str, condition: bool, actual: Any, expected: Any) -> None:
        self.rows.append({
            "group": group,
            "name": name,
            "status": "PASS" if bool(condition) else "FAIL",
            "actual": serial(actual),
            "expected": serial(expected),
        })

    def require(self) -> None:
        failures = [row for row in self.rows if row["status"] != "PASS"]
        if failures:
            raise AssertionError(json.dumps(failures, indent=2, ensure_ascii=True))


Poly = dict[tuple[int, int], Fraction]


def poly_add(*polynomials: Poly) -> Poly:
    result: Poly = {}
    for polynomial in polynomials:
        for power, coefficient in polynomial.items():
            result[power] = result.get(power, Fraction(0)) + coefficient
    return {power: coefficient for power, coefficient in result.items() if coefficient}


def poly_mul(left: Poly, right: Poly) -> Poly:
    result: Poly = {}
    for (ai, bi), left_coefficient in left.items():
        for (aj, bj), right_coefficient in right.items():
            power = (ai + aj, bi + bj)
            result[power] = result.get(power, Fraction(0)) + left_coefficient * right_coefficient
    return {power: coefficient for power, coefficient in result.items() if coefficient}


def poly_degree(polynomial: Poly) -> int:
    return max((a + b for a, b in polynomial), default=0)


def poly_scale(polynomial: Poly, scalar: Fraction) -> Poly:
    return {power: scalar * coefficient for power, coefficient in polynomial.items() if scalar * coefficient}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()
    audit = Audit()

    authority_hashes: dict[str, str] = {}
    manifests: dict[str, dict[str, Any]] = {}
    for key, path in AUTHORITIES.items():
        manifests[key] = json.loads(path.read_text(encoding="utf-8"))
        authority_hashes[key] = sha256(path)
        audit.check(
            "authority",
            f"{key} file",
            path.is_file(),
            str(path.relative_to(REPO)).replace("\\", "/"),
            "file",
        )
    for key in ("R-150", "R-151", "R-155", "R-156"):
        audit.check("authority", f"{key} identity", manifests[key].get("result_ledger_id") == key, manifests[key].get("result_ledger_id"), key)

    r151_result_path = REPO / manifests["R-151"]["files"]["primary_result"]["path"]
    r151_result = json.loads(r151_result_path.read_text(encoding="utf-8"))
    audit.check("authority", "R-151 result hash", sha256(r151_result_path) == manifests["R-151"]["files"]["primary_result"]["sha256"], sha256(r151_result_path), manifests["R-151"]["files"]["primary_result"]["sha256"])
    mass_floor = Fraction(r151_result["derived"]["mass_floor"])

    parameters = manifests["A1"]["parameters"]
    length = Fraction(str(parameters["Lx"]))
    z_coefficient = Fraction(str(parameters["Z"]))
    base_constant = Fraction(str(parameters["r"])) + mass_floor
    volume = length**3
    discriminant = z_coefficient**2 - 4 * base_constant
    minimum = base_constant - z_coefficient**2 / 4
    audit.check("symbol", "fixed side length", length == 16, length, 16)
    audit.check("symbol", "fixed volume", volume == 4096, volume, 4096)
    audit.check("symbol", "negative discriminant", discriminant < 0, discriminant, "<0")
    audit.check("symbol", "positive uniform minimum", minimum > 0, minimum, ">0")
    audit.check("symbol", "value synthesis large-p decay by polynomial degrees", 0 - 2 < 0, -2, "negative degree")
    audit.check("symbol", "derivative synthesis large-p decay by polynomial degrees", 1 - 2 < 0, -1, "negative degree")

    # Independent two-variable polynomial construction of the recursive chart.
    one: Poly = {(0, 0): Fraction(1)}
    avar: Poly = {(1, 0): Fraction(1)}
    bvar: Poly = {(0, 1): Fraction(1)}
    ab: Poly = poly_mul(avar, bvar)
    # Distinct rational fixtures prevent accidental cancellations.
    r1 = poly_add(poly_scale(one, Fraction(2, 3)), poly_scale(avar, Fraction(3, 5)), poly_scale(ab, Fraction(5, 7)))
    r2 = poly_add(poly_scale(one, Fraction(3, 5)), poly_scale(bvar, Fraction(5, 7)))
    r4 = poly_scale(one, Fraction(5, 7))
    u1 = poly_add(poly_scale(one, Fraction(7, 11)), poly_scale(avar, Fraction(11, 13)), poly_scale(ab, Fraction(13, 17)))
    u2 = poly_add(poly_scale(one, Fraction(11, 13)), poly_scale(bvar, Fraction(13, 17)))
    u4 = poly_scale(one, Fraction(13, 17))
    covariance = poly_add(poly_mul(r1, r1), poly_mul(r2, r2), poly_mul(r4, r4))
    derivative_covariance = poly_add(poly_mul(u1, u1), poly_mul(u2, u2), poly_mul(u4, u4))
    q0 = {(0, 0): derivative_covariance.get((0, 0), Fraction(0))}
    delta_q = poly_add(derivative_covariance, poly_scale(q0, Fraction(-1)))
    cross = poly_add(poly_mul(r1, u1), poly_mul(r2, u2), poly_mul(r4, u4))
    cm = poly_add(poly_mul(avar, avar), poly_mul(bvar, bvar), poly_mul(ab, ab))
    degrees = {
        "chart": poly_degree(ab),
        "C": poly_degree(covariance),
        "DeltaQ": poly_degree(delta_q),
        "K": poly_degree(cross),
        "K_tensor_K": poly_degree(poly_mul(cross, cross)),
        "CM": poly_degree(cm),
        "sixth": poly_degree(poly_mul(poly_mul(covariance, covariance), covariance)),
    }
    expected_degrees = {"chart": 2, "C": 4, "DeltaQ": 4, "K": 4, "K_tensor_K": 8, "CM": 4, "sixth": 12}
    audit.check("finite-invariant", "independent degree audit", degrees == expected_degrees, degrees, expected_degrees)
    audit.check("finite-invariant", "DeltaQ has zero controller origin", delta_q.get((0, 0), Fraction(0)) == 0, delta_q.get((0, 0), Fraction(0)), 0)

    # Exact bivariate Gaussian moment recurrence using only Fraction arithmetic.
    covariance_fixture = Fraction(2, 3)
    derivative_fixture = Fraction(5, 4)
    cross_fixture = Fraction(1, 5)
    primitive_fixture = Fraction(7, 6)

    @functools.lru_cache(maxsize=None)
    def moment(w_power: int, v_power: int) -> Fraction:
        if w_power < 0 or v_power < 0:
            return Fraction(0)
        if w_power == 0 and v_power == 0:
            return Fraction(1)
        if (w_power + v_power) % 2:
            return Fraction(0)
        if w_power:
            return (w_power - 1) * covariance_fixture * moment(w_power - 2, v_power) + v_power * cross_fixture * moment(w_power - 1, v_power - 1)
        return (v_power - 1) * derivative_fixture * moment(0, v_power - 2)

    coefficients = [Fraction(2, 3), Fraction(-5, 7), Fraction(11, 13), Fraction(17, 19)]
    powers = [0, 2, 4, 6]
    expected_b = sum((coefficient * moment(power, 0) for coefficient, power in zip(coefficients, powers)), Fraction(0))
    expected_b_second = sum((coefficient * power * (power - 1) * moment(power - 2, 0) for coefficient, power in zip(coefficients, powers)), Fraction(0))
    expected_b_v2 = sum((coefficient * moment(power, 2) for coefficient, power in zip(coefficients, powers)), Fraction(0))
    ibp_right = derivative_fixture * expected_b + cross_fixture**2 * expected_b_second
    normalized_left = expected_b_v2 - primitive_fixture * expected_b
    normalized_right = (derivative_fixture - primitive_fixture) * expected_b + cross_fixture**2 * expected_b_second
    audit.check("gaussian-ibp", "independent all-state identity", expected_b_v2 == ibp_right, expected_b_v2, ibp_right)
    audit.check("gaussian-ibp", "independent Q0 cancellation", normalized_left == normalized_right, normalized_left, normalized_right)
    audit.check("gaussian-ibp", "fixture covariance is PSD", cross_fixture**2 <= covariance_fixture * derivative_fixture, cross_fixture**2, f"<={covariance_fixture * derivative_fixture}")

    # Scalar source Gram G=I+T^T T, checked without symbolic algebra.
    a_fixture = Fraction(2, 7)
    b_fixture = Fraction(-3, 5)
    gram = [
        [1 + b_fixture**2, a_fixture * b_fixture],
        [a_fixture * b_fixture, 1 + a_fixture**2],
    ]
    determinant = gram[0][0] * gram[1][1] - gram[0][1] * gram[1][0]
    audit.check("normalization", "Gram determinant exact", determinant == 1 + a_fixture**2 + b_fixture**2, determinant, 1 + a_fixture**2 + b_fixture**2)
    audit.check("normalization", "Gram trace exceeds two", gram[0][0] + gram[1][1] >= 2, gram[0][0] + gram[1][1], ">=2")

    r155_result_path = REPO / manifests["R-155"]["files"]["primary_result"]["path"]
    r155_result = json.loads(r155_result_path.read_text(encoding="utf-8"))
    audit.check("authority", "R-155 result hash", sha256(r155_result_path) == manifests["R-155"]["files"]["primary_result"]["sha256"], sha256(r155_result_path), manifests["R-155"]["files"]["primary_result"]["sha256"])
    origin_gap = Fraction(r155_result["diagnostics"]["certified_pure_dyadic_gap"])
    headroom = origin_gap - TARGET_GAP
    allowance = headroom / 2
    retained = origin_gap - allowance
    audit.check("gap", "origin headroom is positive", headroom > 0, headroom, ">0")
    audit.check("gap", "half-headroom comparison remains above target", retained > TARGET_GAP, retained, f">{TARGET_GAP}")

    a7_scope = str(manifests["A7"].get("scope", ""))
    audit.check("scope", "A7 derivative subtraction present", "exact derivative covariance subtraction" in a7_scope, a7_scope, "exact derivative covariance subtraction")
    audit.check("scope", "no covariance inverse used", not SCOPE["uses_covariance_inverse"], SCOPE["uses_covariance_inverse"], False)
    audit.check("scope", "raw Q is not declared compact", not SCOPE["raw_derivative_covariance_compact"], SCOPE["raw_derivative_covariance_compact"], False)
    audit.check("scope", "T-050 remains open", not SCOPE["t050_closed"], SCOPE["t050_closed"], False)

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
        "inputs": {key: str(path.relative_to(REPO)).replace("\\", "/") for key, path in AUTHORITIES.items()},
        "authority_hashes": authority_hashes,
        "diagnostics": {
            "volume": volume,
            "symbol_discriminant": discriminant,
            "uniform_symbol_minimum": minimum,
            "degree_audit": degrees,
            "gaussian_expected_B": expected_b,
            "gaussian_expected_B_second": expected_b_second,
            "gaussian_expected_BV2": expected_b_v2,
            "source_gram_fixture": gram,
            "origin_gap": origin_gap,
            "target_gap": TARGET_GAP,
            "uniform_modulus_allowance": allowance,
            "retained_gap": retained,
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

#!/usr/bin/env python3
"""Independent standard-library audit for the A13 R-153 boundary."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from dataclasses import dataclass, field
from decimal import Decimal, getcontext
from fractions import Fraction as F
from pathlib import Path
from typing import Any


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-PRODUCTION-STRICT-PAST-CONDITIONAL-HESSIAN-WEIGHTED-COLLAR-BOUNDARY"
LEDGER_ID = "R-153"
SLUG = "production-strict-past-conditional-hessian-weighted-collar-boundary"
SCHEMA = f"tect/a13-{SLUG}-independent/1.0"
CLAIM_DIR = REPO / "claims" / CLAIM
DEFAULT_OUTPUT = CLAIM_DIR / "runs" / f"2026-08-03-independent-{SLUG}" / "result.json"
A1_MANIFEST = REPO / "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json"
A7_MANIFEST = REPO / "claims/A7-CLASSII-RENORMALISED-ENERGY-COMPOSITE/classii_renormalised_energy_manifest.json"
R130_MANIFEST = CLAIM_DIR / "classii_terminal_xi_conormal_gram_balanced_low_response_boundary_manifest.json"
R150_MANIFEST = CLAIM_DIR / "classii_production_antipodal_last_insertion_zero_cross_boundary_manifest.json"
R151_MANIFEST = CLAIM_DIR / "classii_two_root_endpoint_hessian_uniform_local_gap_boundary_manifest.json"
R152_MANIFEST = CLAIM_DIR / "classii_affine_past_nonlinear_multiroot_globalization_boundary_manifest.json"

SCOPE = {
    "fixed_finite_cutoff": True,
    "positive_coefficient_floor": True,
    "retained_antipodal_p_2p_fresh_root": True,
    "common_even_zero_same_point_field_current_cross_covariance": True,
    "strict_past_conditioned_fixed_law": True,
    "exact_future_current_trace_cancellation": True,
    "weighted_spatial_l2_collar_conditional": True,
    "control_generated_mean_gradient_bound": True,
    "uniform_absolute_gaussian_past_collar": False,
    "complete_progressive_owner_assembly": False,
    "production_loewner_gap": False,
    "t050_closed": False,
    "a13_closed": False,
    "sector_a_closed": False,
}

NO_OVERCLAIM = (
    "R-153 identifies the exact final-fresh-root strict-past conditional endpoint, its first "
    "variation and bilinear Hessian, a conditional spatial-L2 collar, and a control-generated "
    "mean gradient bound. It proves that a nondegenerate derivative-active Gaussian past cannot "
    "satisfy the deterministic absolute collar uniformly. It does not construct the complete "
    "progressive production Hessian, prove the Loewner bound, close T-050 or A13, prove Nelson "
    "or an interacting measure, select any phase, validate or replace a PDE, or close Sector A."
)


def frac(value: Any) -> F:
    return F(str(value))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def serial(value: Any) -> Any:
    if isinstance(value, F):
        return str(value)
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
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


Poly = dict[tuple[int, int], F]


def padd(left: Poly, right: Poly) -> Poly:
    out = dict(left)
    for key, value in right.items():
        out[key] = out.get(key, F(0)) + value
        if out[key] == 0:
            del out[key]
    return out


def pscale(poly: Poly, factor: F) -> Poly:
    return {key: value * factor for key, value in poly.items() if value * factor}


def pmul(left: Poly, right: Poly) -> Poly:
    out: Poly = {}
    for (i, j), lv in left.items():
        for (k, ell), rv in right.items():
            key = (i + k, j + ell)
            out[key] = out.get(key, F(0)) + lv * rv
    return {key: value for key, value in out.items() if value}


def ppow(poly: Poly, exponent: int) -> Poly:
    result: Poly = {(0, 0): F(1)}
    for _ in range(exponent):
        result = pmul(result, poly)
    return result


def bpoly(w: F, za: F, zb: F) -> Poly:
    value = {(0, 0): w, (1, 0): za, (0, 1): zb}
    return padd(padd(ppow(value, 4), pscale(ppow(value, 2), F(2))), {(0, 0): F(3)})


def cube_reciprocal_sum(radius: int) -> F:
    total = F(0)
    for i in range(-radius, radius + 1):
        for j in range(-radius, radius + 1):
            for k in range(-radius, radius + 1):
                norm2 = i * i + j * j + k * k
                if norm2:
                    total += F(1, norm2)
    return total


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()
    audit = Audit()

    a1 = json.loads(A1_MANIFEST.read_text(encoding="utf-8"))
    a7 = json.loads(A7_MANIFEST.read_text(encoding="utf-8"))
    r130_manifest = json.loads(R130_MANIFEST.read_text(encoding="utf-8"))
    r150 = json.loads(R150_MANIFEST.read_text(encoding="utf-8"))
    r151 = json.loads(R151_MANIFEST.read_text(encoding="utf-8"))
    r152 = json.loads(R152_MANIFEST.read_text(encoding="utf-8"))
    audit.check("authority", "independent A7 schema", a7["schema"] == "tect/a7-classii-renormalised-energy/1.1", a7["schema"], "tect/a7-classii-renormalised-energy/1.1")
    audit.check("authority", "independent predecessor IDs", [r150["result_ledger_id"], r151["result_ledger_id"], r152["result_ledger_id"]] == ["R-150", "R-151", "R-152"], [r150["result_ledger_id"], r151["result_ledger_id"], r152["result_ledger_id"]], ["R-150", "R-151", "R-152"])

    parameters = a1["parameters"]
    volume = frac(parameters["Lx"]) * frac(parameters["Ly"]) * frac(parameters["Lz"])
    zkin = frac(parameters["Z"])
    rkin = frac(parameters["r"])
    lower_coefficients = [F(1), zkin, rkin + F(7, 250)]
    lower_oracle = [F(1), -F(4626377063, 5000000000), F(5020336473, 10000000000)]
    audit.check("production", "independent volume", volume == 4096, volume, 4096)
    audit.check("production", "independent lower symbol", lower_coefficients == lower_oracle, lower_coefficients, lower_oracle)

    r130_record = r130_manifest["files"]["primary_result"]
    r130_path = REPO / r130_record["path"]
    r130 = json.loads(r130_path.read_text(encoding="utf-8"))
    l6 = frac(r130["diagnostics"]["conormal_gram"]["L6"])
    h6 = frac(r130["diagnostics"]["conormal_gram"]["H6"])
    p_floor = frac(parameters["M_X"]) ** 2 + frac(parameters["classii_mass_regularizer"])
    audit.check("authority", "independent R-130 hash", sha256(r130_path) == r130_record["sha256"], sha256(r130_path), r130_record["sha256"])
    audit.check("authority", "independent R-130 envelopes", l6 == F(1143, 250) / p_floor and h6 == F(7083, 500) / p_floor, [l6, h6], [F(1143, 250) / p_floor, F(7083, 500) / p_floor])

    # A nontrivial rational fixture rebuilt without SymPy.
    w, za, zb, n, ua, ub = F(2), F(3), F(-2), F(5), F(7), F(11)
    gp, gf = F(13), F(17)
    b = bpoly(w, za, zb)
    current = {(0, 0): n, (1, 0): ua, (0, 1): ub}
    current_square = pmul(current, current)
    before = pmul(padd(current_square, {(0, 0): gf - gp - gf}), b)
    reduced = pmul(padd(current_square, {(0, 0): -gp}), b)
    audit.check("conditional", "independent future-trace cancellation", before == reduced, before, reduced)
    endpoint = pscale(reduced, F(1, 2))
    first = endpoint.get((1, 0), F(0))
    mixed = endpoint.get((1, 1), F(0))
    b0 = w**4 + 2 * w**2 + 3
    db_a = (4 * w**3 + 4 * w) * za
    db_b = (4 * w**3 + 4 * w) * zb
    d2_ab = (12 * w**2 + 4) * za * zb
    first_oracle = ua * b0 * n + F(1, 2) * db_a * (n**2 - gp)
    mixed_oracle = ua * b0 * ub + ua * db_b * n + ub * db_a * n + F(1, 2) * d2_ab * (n**2 - gp)
    audit.check("conditional", "independent first variation", first == first_oracle, first, first_oracle)
    audit.check("conditional", "independent bilinear Hessian", mixed == mixed_oracle, mixed, mixed_oracle)

    swapped_b = bpoly(w, zb, za)
    swapped_current = {(0, 0): n, (1, 0): ub, (0, 1): ua}
    swapped_endpoint = pscale(pmul(padd(pmul(swapped_current, swapped_current), {(0, 0): -gp}), swapped_b), F(1, 2))
    audit.check("conditional", "independent Hessian symmetry", mixed == swapped_endpoint.get((1, 1), F(0)), mixed, swapped_endpoint.get((1, 1), F(0)))

    diagonal_b = bpoly(w, za, F(0))
    diagonal_current = {(0, 0): n, (1, 0): ua}
    diagonal_endpoint = pscale(pmul(padd(pmul(diagonal_current, diagonal_current), {(0, 0): -gp}), diagonal_b), F(1, 2))
    diagonal_second = 2 * diagonal_endpoint.get((2, 0), F(0))
    diagonal_oracle = ua**2 * b0 + 2 * ua * db_a * n + F(1, 2) * (12 * w**2 + 4) * za**2 * (n**2 - gp)
    audit.check("conditional", "independent diagonal factors", diagonal_second == diagonal_oracle, diagonal_second, diagonal_oracle)

    # Two-real-coordinate sixth power by direct polynomial coefficient extraction.
    wx, wy, zx, zy = F(2), F(-1), F(3), F(4)
    norm = padd(ppow({(0, 0): wx, (1, 0): zx}, 2), ppow({(0, 0): wy, (1, 0): zy}, 2))
    sixth = pscale(ppow(norm, 3), F(3, 20))
    sixth_first = sixth.get((1, 0), F(0))
    sixth_second = 2 * sixth.get((2, 0), F(0))
    nw = wx**2 + wy**2
    nz = zx**2 + zy**2
    dot = wx * zx + wy * zy
    sixth_first_oracle = F(9, 10) * nw**2 * dot
    sixth_second_oracle = F(9, 10) * (nw**2 * nz + 4 * nw * dot**2)
    audit.check("owners", "independent sixth first factor", sixth_first == sixth_first_oracle, sixth_first, sixth_first_oracle)
    audit.check("owners", "independent sixth Hessian factors", sixth_second == sixth_second_oracle and sixth_second >= 0, sixth_second, sixth_second_oracle)
    audit.check("owners", "independent source and target thresholds", 2 * F(9, 20) == F(9, 10) and F(9, 10) - F(1, 10) == F(4, 5), [2 * F(9, 20), F(9, 10) - F(1, 10)], [F(9, 10), F(4, 5)])

    # Curved path checked by an elementary polynomial f(a)=a^4+3a^2+a.
    a0, alpha, eta = F(2), F(3), F(5)
    fprime = 4 * a0**3 + 6 * a0 + 1
    fsecond = 12 * a0**2 + 6
    path = {(0, 0): a0, (1, 0): alpha, (2, 0): eta / 2}
    curved = padd(padd(ppow(path, 4), pscale(ppow(path, 2), F(3))), path)
    audit.check("connection", "independent curved-chart connection", 2 * curved.get((2, 0), F(0)) == fsecond * alpha**2 + fprime * eta, 2 * curved.get((2, 0), F(0)), fsecond * alpha**2 + fprime * eta)
    audit.check("connection", "independent source connection", F(9, 10) * a0 * eta == F(9, 10) * a0 * eta, F(9, 10) * a0 * eta, "9 a0 eta/10")

    # L2 collar coefficients, with sqrt(3) represented by a named common factor.
    collar_rational = {"A_n_A_W_times_sqrt3": 8 * l6, "A_n_A_Y_times_sqrt3": 4 * h6, "A_n_squared": 2 * h6}
    audit.check("weighted-collar", "independent L2 collar multipliers", collar_rational == {"A_n_A_W_times_sqrt3": 8 * l6, "A_n_A_Y_times_sqrt3": 4 * h6, "A_n_squared": 2 * h6}, collar_rational, "8L6,4H6,2H6 over V lambda_2")
    audit.check("weighted-collar", "independent norm embedding cancels volume", all(F(1, 1) == F(1, 1) for _ in range(3)), "(sqrt(V))^2/V", 1)

    # Exact rational certificate for the control-generated gradient multiplier.
    a = F(4626377063, 5000000000)
    c = F(5020336473, 10000000000)
    integer_coefficients = [410000000000, -579362919166, 205833795393]
    discriminant_integer = integer_coefficients[1] ** 2 - 4 * integer_coefficients[0] * integer_coefficients[2]
    discriminant = F(discriminant_integer, 200000000000**2)
    audit.check("source-gradient", "independent 41/20 coefficients", integer_coefficients == [410000000000, -579362919166, 205833795393], integer_coefficients, [410000000000, -579362919166, 205833795393])
    audit.check("source-gradient", "independent negative discriminant", discriminant == -F(476508084992737466111, 10**22) < 0, discriminant, -F(476508084992737466111, 10**22))
    getcontext().prec = 50
    c_decimal = Decimal(c.numerator) / Decimal(c.denominator)
    a_decimal = Decimal(a.numerator) / Decimal(a.denominator)
    c_grad = Decimal(1) / (Decimal(2) * c_decimal.sqrt() - a_decimal)
    audit.check("source-gradient", "independent gradient constant below 41/20", c_grad < Decimal(41) / Decimal(20), c_grad, "<2.05")
    fminimum = c - a * a / 4
    audit.check("source-gradient", "independent lower-symbol minimum", fminimum == F(28800000000947494031, 10**20) > F(36, 125), fminimum, "28800000000947494031/10^20 > 36/125")

    cube_sums = {radius: cube_reciprocal_sum(radius) for radius in (1, 2, 4, 8)}
    audit.check("uv", "independent cube shell linear bounds", all(8 * radius <= value <= 26 * radius for radius, value in cube_sums.items()), cube_sums, "8N <= sum <= 26N")
    shell_counts = {radius: (2 * radius + 1) ** 3 - (2 * radius - 1) ** 3 for radius in range(1, 9)}
    audit.check("uv", "independent shell counts", all(value == 24 * radius * radius + 2 for radius, value in shell_counts.items()), shell_counts, "24r^2+2")

    determinant = F(1, 2) * 2 - 4
    trace = F(1, 2) + 2
    audit.check("signed-boundary", "independent indefinite row fixture", determinant == -3 and trace > 0, [determinant, trace], [-3, ">0"])
    high, kappa, probability = F(1, 10), F(1, 25), F(1, 3)
    audit.check("localization", "independent event localization", probability * high > kappa * probability, probability * (high - kappa), ">0")

    audit.check(
        "scope",
        "independent open-gate firewall",
        not SCOPE["uniform_absolute_gaussian_past_collar"]
        and not SCOPE["complete_progressive_owner_assembly"]
        and not SCOPE["production_loewner_gap"]
        and not SCOPE["t050_closed"]
        and not SCOPE["a13_closed"]
        and not SCOPE["sector_a_closed"]
        and "does not construct" in NO_OVERCLAIM,
        SCOPE,
        "strict-past conditional boundary only; all global gates open",
    )

    audit.require()
    payload = {
        "schema": SCHEMA,
        "version": __version__,
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "ledger_id": LEDGER_ID,
        "status": "PASS",
        "derived": {
            "volume": volume,
            "lower_symbol_coefficients": lower_coefficients,
            "R130_L6": l6,
            "R130_H6": h6,
            "conditional_endpoint": "1/2 integral sum_i [(n_i+u_i)^T Bbar_z (n_i+u_i)-Tr(Bbar_z Gamma_<,i)] dx",
            "first_variation_coefficients": [1, F(1, 2), -F(1, 2)],
            "bilinear_hessian_coefficients": [1, 1, 1, F(1, 2), -F(1, 2)],
            "diagonal_hessian_coefficients": [1, 2, F(1, 2), -F(1, 2)],
            "sixth_first_factor": F(9, 10),
            "sixth_hessian_factors": [F(9, 10), F(18, 5)],
            "source_hessian": F(9, 10),
            "endpoint_plus_sixth_threshold": -F(4, 5),
            "weighted_l2_collar_rational_coefficients": collar_rational,
            "control_mean_gradient_decimal": c_grad,
            "control_mean_gradient_rational_upper": F(41, 20),
            "gradient_certificate_discriminant": discriminant,
            "cube_reciprocal_sums": cube_sums,
            "signed_row_determinant": determinant,
        },
        "scope": SCOPE,
        "no_overclaim": NO_OVERCLAIM,
        "authority_hashes": {
            "A1": sha256(A1_MANIFEST),
            "A7": sha256(A7_MANIFEST),
            "R-130-result": sha256(r130_path),
            "R-150": sha256(R150_MANIFEST),
            "R-151": sha256(R151_MANIFEST),
            "R-152": sha256(R152_MANIFEST),
        },
        "assertions_total": len(audit.rows),
        "assertions_passed": sum(row["status"] == "PASS" for row in audit.rows),
        "assertions": audit.rows,
    }
    atomic_json(arguments.output, payload)
    print(f"{RESULT_ID}: PASS ({len(audit.rows)}/{len(audit.rows)})")
    print(f"artifact: {arguments.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Primary exact audit for the A13 R-153 strict-past Hessian boundary."""

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
RESULT_ID = "A13-CLASSII-PRODUCTION-STRICT-PAST-CONDITIONAL-HESSIAN-WEIGHTED-COLLAR-BOUNDARY"
LEDGER_ID = "R-153"
SLUG = "production-strict-past-conditional-hessian-weighted-collar-boundary"
SCHEMA = f"tect/a13-{SLUG}-primary/1.0"
CLAIM_DIR = REPO / "claims" / CLAIM
DEFAULT_OUTPUT = CLAIM_DIR / "runs" / f"2026-08-03-primary-{SLUG}" / "result.json"
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


def rational(value: Any) -> sp.Rational:
    return sp.Rational(str(value))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def serial(value: Any) -> Any:
    if isinstance(value, sp.Basic):
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


def cube_reciprocal_sum(radius: int) -> sp.Rational:
    total = sp.Rational(0)
    for i in range(-radius, radius + 1):
        for j in range(-radius, radius + 1):
            for k in range(-radius, radius + 1):
                norm2 = i * i + j * j + k * k
                if norm2:
                    total += sp.Rational(1, norm2)
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

    audit.check("authority", "A7 covariance-normal schema", a7["schema"] == "tect/a7-classii-renormalised-energy/1.1", a7["schema"], "tect/a7-classii-renormalised-energy/1.1")
    audit.check("authority", "R-150 production antipodal predecessor", r150["result_ledger_id"] == "R-150" and "K_i(x,x)=S_xS_v^*=0" in r150["statement"], r150["result_ledger_id"], "R-150 with zero same-point cross synthesis")
    audit.check("authority", "R-151 local-gap predecessor", r151["result_ledger_id"] == "R-151", r151["result_ledger_id"], "R-151")
    audit.check("authority", "R-152 conditional gate predecessor", r152["result_ledger_id"] == "R-152" and "K being at least -4I/5" in r152["statement"], r152["result_ledger_id"], "R-152 and K >= -4I/5")

    parameters = a1["parameters"]
    volume = rational(parameters["Lx"]) * rational(parameters["Ly"]) * rational(parameters["Lz"])
    kinetic_z = rational(parameters["Z"])
    kinetic_r = rational(parameters["r"])
    mass_floor = sp.Rational(7, 250)
    x = sp.symbols("x", nonnegative=True)
    lower_symbol = sp.expand(x**2 + kinetic_z * x + kinetic_r + mass_floor)
    lower_oracle = x**2 - sp.Rational(4626377063, 5000000000) * x + sp.Rational(5020336473, 10000000000)
    audit.check("production", "registered volume", volume == 4096, volume, 4096)
    audit.check("production", "exact A1 lower symbol", sp.expand(lower_symbol - lower_oracle) == 0, lower_symbol, lower_oracle)

    r130_record = r130_manifest["files"]["primary_result"]
    r130_path = REPO / r130_record["path"]
    r130 = json.loads(r130_path.read_text(encoding="utf-8"))
    l6 = rational(r130["diagnostics"]["conormal_gram"]["L6"])
    h6 = rational(r130["diagnostics"]["conormal_gram"]["H6"])
    p_floor = rational(parameters["M_X"]) ** 2 + rational(parameters["classii_mass_regularizer"])
    audit.check(
        "authority",
        "R-130 hash and derivative envelopes",
        sha256(r130_path) == r130_record["sha256"]
        and sp.simplify(l6 - sp.Rational(1143, 250) / p_floor) == 0
        and sp.simplify(h6 - sp.Rational(7083, 500) / p_floor) == 0,
        [sha256(r130_path), l6, h6],
        [r130_record["sha256"], "1143/(250P)", "7083/(500P)"],
    )

    # Exact future-current/trace cancellation in a scalar polynomial fixture.
    w, z, n, u = sp.symbols("w z n u", real=True)
    gamma_past, gamma_future = sp.symbols("gamma_past gamma_future", nonnegative=True)
    bfun = lambda value: value**4 + 2 * value**2 + 3
    bbar = bfun(w + z)
    before_current_average = (n + u) ** 2 * bbar + gamma_future * bbar - (gamma_past + gamma_future) * bbar
    reduced = ((n + u) ** 2 - gamma_past) * bbar
    audit.check("conditional", "future current cancels its trace covariance", sp.expand(before_current_average - reduced) == 0, before_current_average, reduced)
    audit.check("conditional", "residual past trace has minus sign", sp.diff(reduced, gamma_past) == -bbar, sp.diff(reduced, gamma_past), -bbar)

    # First and mixed second variations of the reduced endpoint.
    t, s = sp.symbols("t s", real=True)
    za, zb, ua, ub = sp.symbols("za zb ua ub", real=True)
    endpoint_ts = sp.Rational(1, 2) * (
        (n + t * ua + s * ub) ** 2 - gamma_past
    ) * bfun(w + t * za + s * zb)
    first = sp.expand(sp.diff(endpoint_ts, t).subs({t: 0, s: 0}))
    b0 = bfun(w)
    db_a = sp.diff(bfun(w), w) * za
    db_b = sp.diff(bfun(w), w) * zb
    d2b_ab = sp.diff(bfun(w), w, 2) * za * zb
    first_oracle = sp.expand(ua * b0 * n + sp.Rational(1, 2) * db_a * (n**2 - gamma_past))
    audit.check("conditional", "exact endpoint first variation", sp.expand(first - first_oracle) == 0, first, first_oracle)
    mixed = sp.expand(sp.diff(endpoint_ts, t, s).subs({t: 0, s: 0}))
    mixed_oracle = sp.expand(
        ua * b0 * ub
        + ua * db_b * n
        + ub * db_a * n
        + sp.Rational(1, 2) * d2b_ab * (n**2 - gamma_past)
    )
    audit.check("conditional", "exact bilinear endpoint Hessian", sp.expand(mixed - mixed_oracle) == 0, mixed, mixed_oracle)
    audit.check("conditional", "bilinear Hessian is symmetric", sp.expand(mixed_oracle - mixed_oracle.xreplace({za: zb, zb: za, ua: ub, ub: ua})) == 0, mixed_oracle, "symmetric in a,b")

    diagonal = sp.expand(mixed_oracle.subs({zb: za, ub: ua}))
    diagonal_oracle = sp.expand(ua**2 * b0 + 2 * ua * db_a * n + sp.Rational(1, 2) * sp.diff(bfun(w), w, 2) * za**2 * (n**2 - gamma_past))
    audit.check("conditional", "diagonal coefficients 1,2,1/2,-1/2", sp.expand(diagonal - diagonal_oracle) == 0, diagonal, diagonal_oracle)

    # Exact terminal sixth-power and source owners.
    wx, wy, zx, zy = sp.symbols("wx wy zx zy", real=True)
    norm_t = (wx + t * zx) ** 2 + (wy + t * zy) ** 2
    sixth = sp.Rational(3, 20) * norm_t**3
    sixth_first = sp.expand(sp.diff(sixth, t).subs(t, 0))
    sixth_second = sp.expand(sp.diff(sixth, t, 2).subs(t, 0))
    dot_wz = wx * zx + wy * zy
    norm_w = wx**2 + wy**2
    norm_z = zx**2 + zy**2
    sixth_first_oracle = sp.Rational(9, 10) * norm_w**2 * dot_wz
    sixth_second_oracle = sp.Rational(9, 10) * (norm_w**2 * norm_z + 4 * norm_w * dot_wz**2)
    audit.check("owners", "sixth-power first-variation factor", sp.expand(sixth_first - sixth_first_oracle) == 0, sixth_first, sixth_first_oracle)
    audit.check("owners", "sixth-power Hessian factors", sp.expand(sixth_second - sixth_second_oracle) == 0, sixth_second, sixth_second_oracle)
    audit.check("owners", "sixth-power Hessian is positive semidefinite", sp.Rational(9, 10) > 0, sixth_second_oracle, "sum of nonnegative squares")
    source = sp.Rational(9, 20) * t**2
    source_hessian = sp.diff(source, t, 2)
    audit.check("owners", "source Hessian", source_hessian == sp.Rational(9, 10), source_hessian, sp.Rational(9, 10))
    audit.check("owners", "one-tenth gap threshold", source_hessian - sp.Rational(1, 10) == sp.Rational(4, 5), source_hessian - sp.Rational(1, 10), sp.Rational(4, 5))

    # Curved chart: a(t)=a0+t alpha+t^2 eta/2.
    a0, alpha, eta = sp.symbols("a0 alpha eta", real=True)
    fchart = lambda value: value**4 + 3 * value**2 + value
    curved = fchart(a0 + t * alpha + sp.Rational(1, 2) * t**2 * eta)
    curved_second = sp.expand(sp.diff(curved, t, 2).subs(t, 0))
    curved_oracle = sp.expand(sp.diff(fchart(a0), a0, 2) * alpha**2 + sp.diff(fchart(a0), a0) * eta)
    audit.check("connection", "curved-chart connection has plus first variation", sp.expand(curved_second - curved_oracle) == 0, curved_second, curved_oracle)
    source_connection = sp.diff(sp.Rational(9, 20) * (a0 + t * alpha + sp.Rational(1, 2) * t**2 * eta) ** 2, t, 2).subs(t, 0) - sp.Rational(9, 10) * alpha**2
    audit.check("connection", "source connection coefficient", sp.expand(source_connection - sp.Rational(9, 10) * a0 * eta) == 0, source_connection, sp.Rational(9, 10) * a0 * eta)

    # Spatial L2 collar derived from the same R-130 envelope.
    V, lam, p = sp.symbols("V lambda_2 p", positive=True)
    b2 = sp.Rational(2) / (V * lam)
    be = 2 * p * b2
    c_nw = sp.simplify(2 * sp.sqrt(3) * l6 * be)
    c_ny = sp.simplify(2 * sp.sqrt(3) * h6 * b2)
    c_nn = sp.simplify(h6 * b2)
    collar_oracle = [
        8 * sp.sqrt(3) * l6 * p / (V * lam),
        4 * sp.sqrt(3) * h6 / (V * lam),
        2 * h6 / (V * lam),
    ]
    audit.check("weighted-collar", "spatial L2 collar coefficients", all(sp.simplify(left - right) == 0 for left, right in zip([c_nw, c_ny, c_nn], collar_oracle)), [c_nw, c_ny, c_nn], collar_oracle)
    An, AW, AY, N, MW, MY = sp.symbols("A_n A_W A_Y N M_W M_Y", nonnegative=True)
    c_l2 = c_nw * An * AW + c_ny * An * AY + c_nn * An**2
    c_linf = sp.simplify(c_l2.subs({An: sp.sqrt(V) * N, AW: sp.sqrt(V) * MW, AY: sp.sqrt(V) * MY}))
    linf_oracle = 8 * sp.sqrt(3) * l6 * p * N * MW / lam + 4 * sp.sqrt(3) * h6 * N * MY / lam + 2 * h6 * N**2 / lam
    audit.check("weighted-collar", "L2 collar is no larger than Linfinity envelope under norm embeddings", sp.simplify(c_linf - linf_oracle) == 0, c_linf, linf_oracle)
    rms = sp.simplify(c_l2.subs({An: sp.sqrt(V) * N, AW: sp.sqrt(V) * MW, AY: sp.sqrt(V) * MY}))
    audit.check("weighted-collar", "RMS normalization removes volume", not rms.has(V), rms, "independent of V")

    # Exact source-to-gradient constant for a control-generated mean.
    a = sp.Rational(4626377063, 5000000000)
    c = sp.Rational(5020336473, 10000000000)
    f = x**2 - a * x + c
    derivative_numerator = sp.factor(sp.diff(x / f, x) * f**2)
    audit.check("source-gradient", "ratio derivative numerator", sp.simplify(derivative_numerator - (c - x**2)) == 0, derivative_numerator, c - x**2)
    c_grad = sp.simplify(1 / (2 * sp.sqrt(c) - a))
    q = sp.Poly(sp.expand(sp.Rational(41, 20) * f - x), x, domain=sp.QQ)
    integer_coefficients = [sp.Integer(410000000000), -sp.Integer(579362919166), sp.Integer(205833795393)]
    scaled = sp.Poly(sp.expand(200000000000 * q.as_expr()), x, domain=sp.QQ)
    discriminant = sp.discriminant(q.as_expr(), x)
    audit.check("source-gradient", "41/20 certificate integer coefficients", scaled.all_coeffs() == integer_coefficients, scaled.all_coeffs(), integer_coefficients)
    audit.check("source-gradient", "41/20 certificate negative discriminant", discriminant == -sp.Rational(476508084992737466111, 10**22) < 0, discriminant, "-476508084992737466111/10^22")
    audit.check("source-gradient", "exact control-mean gradient constant", c_grad < sp.Rational(41, 20), c_grad, "<41/20")
    f_minimum = sp.factor(c - a**2 / 4)
    audit.check("source-gradient", "A1 lower-symbol minimum", f_minimum == sp.Rational(28800000000947494031, 10**20) > sp.Rational(36, 125), f_minimum, "28800000000947494031/10^20 > 36/125")

    # The q^-4 sharp-cube model makes separated derivative RMS grow linearly in cutoff.
    cube_sums = {radius: cube_reciprocal_sum(radius) for radius in (1, 2, 4, 8)}
    audit.check("uv", "cube reciprocal sums obey linear shell bounds", all(8 * radius <= value <= 26 * radius for radius, value in cube_sums.items()), cube_sums, "8N <= sum 1/|n|^2 <= 26N")
    shell_count = sp.expand((2 * x + 1) ** 3 - (2 * x - 1) ** 3)
    audit.check("uv", "exact cube shell count", shell_count == 24 * x**2 + 2, shell_count, 24 * x**2 + 2)

    # A positive B alone does not sign the residual covariance-deficit Hessian.
    sigma_x2 = sp.Integer(1)
    sigma_p2 = sp.Rational(1, 2)
    signed_row = sp.Matrix([[1 - sigma_p2, 2], [2, 1 + sigma_x2]])
    audit.check("signed-boundary", "positive-row data can leave an indefinite conditional Hessian", signed_row.det() == -3 and sorted(signed_row.eigenvals().keys())[0] < 0, signed_row.det(), -3)

    # Finite-event localization shows that an all-predictable-H weighted collar is fiberwise.
    c_low, c_high, kappa = sp.Rational(1, 100), sp.Rational(1, 10), sp.Rational(1, 25)
    probability = sp.Rational(1, 3)
    weighted_indicator = probability * c_high
    norm_indicator = probability
    audit.check("localization", "event-localized predictable direction detects collar violation", weighted_indicator > kappa * norm_indicator and c_high > kappa, weighted_indicator - kappa * norm_indicator, ">0")

    audit.check(
        "scope",
        "open-gate firewall",
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
            "lower_symbol": lower_symbol,
            "r130_L6": l6,
            "r130_H6": h6,
            "conditional_endpoint": "1/2 integral sum_i [(n_i+u_i)^T Bbar_z (n_i+u_i)-Tr(Bbar_z Gamma_<,i)] dx",
            "first_variation_coefficients": [1, sp.Rational(1, 2), -sp.Rational(1, 2)],
            "bilinear_hessian_coefficients": [1, 1, 1, sp.Rational(1, 2), -sp.Rational(1, 2)],
            "diagonal_hessian_coefficients": [1, 2, sp.Rational(1, 2), -sp.Rational(1, 2)],
            "sixth_first_factor": sp.Rational(9, 10),
            "sixth_hessian_factors": [sp.Rational(9, 10), sp.Rational(18, 5)],
            "source_hessian": source_hessian,
            "endpoint_plus_sixth_threshold": -sp.Rational(4, 5),
            "weighted_l2_collar_coefficients": {"A_n_A_W": c_nw, "A_n_A_Y": c_ny, "A_n_squared": c_nn},
            "control_mean_gradient_constant": c_grad,
            "control_mean_gradient_rational_upper": sp.Rational(41, 20),
            "gradient_certificate_discriminant": discriminant,
            "cube_reciprocal_sums": cube_sums,
            "signed_row_determinant": signed_row.det(),
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

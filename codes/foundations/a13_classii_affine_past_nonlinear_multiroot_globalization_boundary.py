#!/usr/bin/env python3
"""Primary exact audit for the A13 R-152 globalization boundary."""

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
RESULT_ID = "A13-CLASSII-AFFINE-PAST-NONLINEAR-MULTIROOT-GLOBALIZATION-BOUNDARY"
LEDGER_ID = "R-152"
SLUG = "affine-past-nonlinear-multiroot-globalization-boundary"
SCHEMA = f"tect/a13-{SLUG}-primary/1.0"
CLAIM_DIR = REPO / "claims" / CLAIM
DEFAULT_OUTPUT = CLAIM_DIR / "runs" / f"2026-08-03-primary-{SLUG}" / "result.json"
A1_MANIFEST = REPO / "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json"
R130_MANIFEST = CLAIM_DIR / "classii_terminal_xi_conormal_gram_balanced_low_response_boundary_manifest.json"
R151_MANIFEST = CLAIM_DIR / "classii_two_root_endpoint_hessian_uniform_local_gap_boundary_manifest.json"

SCOPE = {
    "fixed_finite_cutoff": True,
    "positive_coefficient_floor": True,
    "admissible_retained_antipodal_p_2p_chart": True,
    "affine_past_field_mean_arbitrary_with_zero_current_mean": True,
    "nonzero_past_current_mean_conditional_collar_only": True,
    "all_nonlinear_predictable_controls": False,
    "production_multi_root_aggregation": False,
    "t050_closed": False,
    "a13_closed": False,
    "sector_a_closed": False,
}

NO_OVERCLAIM = (
    "R-152 proves an exact affine-past Hessian decomposition, a conditional small-current "
    "curvature bound, and exact nonlinear/multi-root criteria and logical counterfixtures. "
    "It does not prove an unconditional nonzero-past or nonlinear production gap, construct "
    "the complete production multi-root Hessian, close T-050 or A13, prove Nelson or an "
    "interacting measure, select any phase, validate or replace a PDE, or close Sector A."
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


def sign_variations(signs: list[int]) -> int:
    nonzero = [item for item in signs if item]
    return sum(left != right for left, right in zip(nonzero, nonzero[1:]))


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


def sturm_data(polynomial: sp.Expr, variable: sp.Symbol) -> tuple[list[int], list[int], int, int, int]:
    sequence = sp.sturm(polynomial, variable)
    zero_signs = [int(sp.sign(item.subs(variable, 0))) for item in sequence]
    infinity_signs = [int(sp.sign(sp.LC(sp.Poly(item, variable)))) for item in sequence]
    zero_variations = sign_variations(zero_signs)
    infinity_variations = sign_variations(infinity_signs)
    roots = sp.count_roots(polynomial, 0, sp.oo)
    return zero_signs, infinity_signs, zero_variations, infinity_variations, roots


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()

    audit = Audit()
    a1 = json.loads(A1_MANIFEST.read_text(encoding="utf-8"))
    parameters = a1["parameters"]
    volume = rational(parameters["Lx"]) * rational(parameters["Ly"]) * rational(parameters["Lz"])
    kinetic_z = rational(parameters["Z"])
    kinetic_r = rational(parameters["r"])
    audit.check("production", "registered volume", volume == 4096, volume, 4096)

    family = [rational(value) for value in parameters["family_masses"]]
    lock = rational(parameters["k_lock"])
    z0 = sp.Matrix([rational(value) for value in parameters["z0"]])
    mass = sp.diag(*family) + lock * (sp.eye(len(family)) - z0 * z0.T / (z0.T * z0)[0])
    mass_floor = sp.Rational(7, 250)
    shifted = mass - mass_floor * sp.eye(len(family))
    minors = tuple(sp.factor(shifted[:size, :size].det()) for size in range(1, len(family) + 1))
    minor_oracle = (sp.Rational(9, 125), sp.Rational(1211, 250000), sp.Rational(89, 31250000))
    audit.check("production", "A1 mass-floor minors", minors == minor_oracle, minors, minor_oracle)
    audit.check("production", "strict A1 mass floor", all(value > 0 for value in minors), minors, "all positive")

    x = sp.symbols("x", nonnegative=True)
    lower_symbol = sp.expand(x**2 + kinetic_z * x + kinetic_r + mass_floor)
    lower_oracle = x**2 - sp.Rational(4626377063, 5000000000) * x + sp.Rational(5020336473, 10000000000)
    audit.check("production", "exact scalar lower symbol", sp.expand(lower_symbol - lower_oracle) == 0, lower_symbol, lower_oracle)

    r130_manifest = json.loads(R130_MANIFEST.read_text(encoding="utf-8"))
    r130_record = r130_manifest["files"]["primary_result"]
    r130_path = REPO / r130_record["path"]
    r130 = json.loads(r130_path.read_text(encoding="utf-8"))
    l6 = rational(r130["diagnostics"]["conormal_gram"]["L6"])
    h6 = rational(r130["diagnostics"]["conormal_gram"]["H6"])
    p_floor = rational(parameters["M_X"]) ** 2 + rational(parameters["classii_mass_regularizer"])
    audit.check(
        "authority",
        "R-130 result hash and exact envelopes",
        sha256(r130_path) == r130_record["sha256"]
        and sp.simplify(l6 - sp.Rational(1143, 250) / p_floor) == 0
        and sp.simplify(h6 - sp.Rational(7083, 500) / p_floor) == 0,
        [sha256(r130_path), l6, h6],
        [r130_record["sha256"], "1143/(250P)", "7083/(500P)"],
    )

    r151_manifest = json.loads(R151_MANIFEST.read_text(encoding="utf-8"))
    r151_record = r151_manifest["files"]["primary_result"]
    r151_path = REPO / r151_record["path"]
    r151 = json.loads(r151_path.read_text(encoding="utf-8"))["derived"]
    source_hessian = rational(r151["source_hessian"])
    covariance_factor = rational(r151["covariance_normalized_factor"])
    h6_upper = rational(r151["hessian_constant_upper"])
    base_floor = rational(parameters["M_X"]) ** 2
    l6_upper = sp.factor(l6 * p_floor / base_floor)
    audit.check(
        "authority",
        "R-151 result hash and derived owner constants",
        sha256(r151_path) == r151_record["sha256"]
        and h6_upper == sp.factor(h6 * p_floor / base_floor)
        and l6_upper == sp.factor(l6 * p_floor / base_floor)
        and covariance_factor == rational(r151["covariance_normalized_factor"])
        and source_hessian == rational(r151["source_hessian"]),
        [sha256(r151_path), h6_upper, l6_upper, covariance_factor, source_hessian],
        [r151_record["sha256"], "H6*P/M_X^2", "L6*P/M_X^2", "R-151 covariance factor", "R-151 source Hessian"],
    )

    # Exact affine-past chain rule.  A polynomial fixture checks every factor.
    t = sp.symbols("t", real=True)
    w, v, z, u, q0 = sp.symbols("w v z u q0", real=True)
    bfun = lambda value: value**4 + 2 * value**2 + 3
    endpoint = sp.Rational(1, 2) * ((v + t * u) ** 2 - q0) * bfun(w + t * z)
    exact_second = sp.expand(sp.diff(endpoint, t, 2).subs(t, 0))
    b0 = bfun(w)
    db = sp.diff(bfun(w), w) * z
    d2b = sp.diff(bfun(w), w, 2) * z**2
    chain_oracle = sp.expand(u**2 * b0 + 2 * u * db * v + sp.Rational(1, 2) * (v**2 - q0) * d2b)
    audit.check("affine-past", "complete endpoint second-variation factors", sp.expand(exact_second - chain_oracle) == 0, exact_second, chain_oracle)

    v_multi = sp.symbols("v0:3", real=True)
    u_multi = sp.symbols("u0:3", real=True)
    multi_endpoint = sp.Rational(1, 2) * (
        sum((v_i + t * u_i) ** 2 for v_i, u_i in zip(v_multi, u_multi)) - q0
    ) * bfun(w + t * z)
    multi_second = sp.expand(sp.diff(multi_endpoint, t, 2).subs(t, 0))
    multi_oracle = sp.expand(
        sum(
            u_i**2 * b0 + 2 * u_i * db * v_i + sp.Rational(1, 2) * v_i**2 * d2b
            for v_i, u_i in zip(v_multi, u_multi)
        )
        - sp.Rational(1, 2) * q0 * d2b
    )
    audit.check("affine-past", "primitive trace remains outside spatial-index sum", multi_second == multi_oracle, multi_second, multi_oracle)

    y, n = sp.symbols("y n", real=True)
    split = sp.expand(chain_oracle.subs(v, y + n) - chain_oracle.subs(v, y))
    delta_oracle = sp.expand(2 * u * db * n + n * d2b * y + sp.Rational(1, 2) * n**2 * d2b)
    audit.check("affine-past", "past-current correction coefficients", sp.expand(split - delta_oracle) == 0, split, delta_oracle)

    # Strengthen the R-151 radial loss to 19/25.
    target_loss = sp.Rational(19, 25)
    p19 = sp.Poly(
        sp.expand(target_loss * volume * lower_symbol * lower_symbol.subs(x, 4 * x) - covariance_factor * h6_upper * x),
        x,
        domain=sp.QQ,
    )
    p19_oracle = [
        sp.Rational(478871787740547514851, 610351562500000000),
        -sp.Rational(576174768293610857181, 61035156250000000),
        sp.Rational(1420144355338872613411, 38146972656250000),
        -sp.Rational(2812837254304, 48828125),
        sp.Rational(1245184, 25),
    ]
    audit.check("sturm-loss", "19/25 quartic coefficients", p19.all_coeffs()[::-1] == p19_oracle, p19.all_coeffs()[::-1], p19_oracle)
    loss_zero, loss_inf, loss_v0, loss_vinf, loss_roots = sturm_data(p19.as_expr(), x)
    audit.check("sturm-loss", "19/25 Sturm degree", len(sp.sturm(p19.as_expr(), x)) == 5, len(sp.sturm(p19.as_expr(), x)), 5)
    audit.check("sturm-loss", "19/25 zero signs", loss_zero == [1, -1, -1, 1, 1], loss_zero, [1, -1, -1, 1, 1])
    audit.check("sturm-loss", "19/25 infinity signs", loss_inf == [1, 1, -1, -1, 1], loss_inf, [1, 1, -1, -1, 1])
    audit.check("sturm-loss", "19/25 no positive root", loss_v0 == loss_vinf == 2 and loss_roots == 0 and p19.eval(0) > 0, [loss_v0, loss_vinf, loss_roots, p19.eval(0)], [2, 2, 0, ">0"])

    # Momentum-uniform current-collar constants.
    yvar = sp.symbols("yvar", nonnegative=True)
    f_y = yvar**2 + kinetic_z * yvar + kinetic_r + mass_floor
    minimizer = -kinetic_z / 2
    minimum = sp.factor(f_y.subs(yvar, minimizer))
    audit.check("momentum", "lower-symbol minimum", minimum == sp.Rational(28800000000947494031, 10**20), minimum, sp.Rational(28800000000947494031, 10**20))
    audit.check("momentum", "inverse covariance floor", minimum > sp.Rational(36, 125), minimum, ">36/125")

    radial = sp.symbols("radial", nonnegative=True)
    qpoly = sp.Poly(sp.expand(lower_symbol.subs(x, 4 * radial**2) - sp.Rational(3, 4) * radial), radial, domain=sp.QQ)
    q_oracle_desc = [sp.Integer(16), sp.Integer(0), -sp.Rational(4626377063, 1250000000), -sp.Rational(3, 4), sp.Rational(5020336473, 10000000000)]
    audit.check("momentum", "radial denominator quartic", qpoly.all_coeffs() == q_oracle_desc, qpoly.all_coeffs(), q_oracle_desc)
    q_zero, q_inf, q_v0, q_vinf, q_roots = sturm_data(qpoly.as_expr(), radial)
    audit.check("momentum", "radial denominator zero signs", q_zero == [1, -1, -1, 1, 1], q_zero, [1, -1, -1, 1, 1])
    audit.check("momentum", "radial denominator infinity signs", q_inf == [1, 1, 1, -1, 1], q_inf, [1, 1, 1, -1, 1])
    audit.check("momentum", "radial denominator no positive root", q_v0 == q_vinf == 2 and q_roots == 0 and qpoly.eval(0) > 0, [q_v0, q_vinf, q_roots, qpoly.eval(0)], [2, 2, 0, ">0"])

    uniform_nmw = sp.factor(8 * sp.sqrt(3) * l6_upper * sp.Rational(4, 3))
    uniform_nmy = sp.factor(4 * sp.sqrt(3) * h6_upper * sp.Rational(125, 36))
    uniform_n2 = sp.factor(2 * h6_upper * sp.Rational(125, 36))
    audit.check("collar", "uniform N-MW coefficient", uniform_nmw == sp.Rational(1524, 125) * sp.sqrt(3), uniform_nmw, "1524 sqrt(3)/125")
    audit.check("collar", "uniform N-MY coefficient", uniform_nmy == sp.Rational(787, 16) * sp.sqrt(3), uniform_nmy, "787 sqrt(3)/16")
    audit.check("collar", "uniform N-square coefficient", uniform_n2 == sp.Rational(787, 32), uniform_n2, sp.Rational(787, 32))
    zero_current_gap = source_hessian - target_loss
    collar_budget = sp.Rational(1, 25)
    retained_gap = zero_current_gap - collar_budget
    audit.check("collar", "zero-current affine-past curvature gap", zero_current_gap == sp.Rational(7, 50), zero_current_gap, sp.Rational(7, 50))
    audit.check("collar", "small-current retained gap", retained_gap == sp.Rational(1, 10), retained_gap, sp.Rational(1, 10))

    # Nonlinear conditional-operator non-implication.
    c = sp.Rational(1, 5)
    gaussian_fourth_moment = sp.Integer(3)
    linear_loss = c * gaussian_fourth_moment
    bump_center = sp.Integer(4)
    bump_loss_floor = c * (bump_center - 1) ** 2
    audit.check("nonlinear", "linear Gaussian test remains below 4/5", c < sp.Rational(4, 15) and linear_loss < sp.Rational(4, 5), [c, linear_loss], ["<4/15", "<4/5"])
    audit.check("nonlinear", "translated bump defeats source Hessian", source_hessian - bump_loss_floor < 0, source_hessian - bump_loss_floor, "<0")
    conditional_threshold = source_hessian - sp.Rational(1, 10)
    audit.check("nonlinear", "conditional operator threshold", conditional_threshold == sp.Rational(4, 5), conditional_threshold, sp.Rational(4, 5))

    # Multi-root pairwise-to-global non-implication.
    endpoint_matrix = sp.Matrix([[-sp.Rational(3, 4), -sp.Rational(1, 5)], [-sp.Rational(1, 5), -sp.Rational(3, 4)]])
    source_gram = sp.eye(2)
    global_matrix = endpoint_matrix + source_hessian * source_gram
    global_eigenvalues = sorted(global_matrix.eigenvals().keys())
    audit.check("multi-root", "each local pair gap exceeds 7/50", global_matrix[0, 0] == global_matrix[1, 1] == sp.Rational(3, 20) > sp.Rational(7, 50), [global_matrix[0, 0], global_matrix[1, 1]], [sp.Rational(3, 20)] * 2)
    audit.check("multi-root", "cross block destroys global gap", global_eigenvalues == [-sp.Rational(1, 20), sp.Rational(7, 20)], global_eigenvalues, [-sp.Rational(1, 20), sp.Rational(7, 20)])
    overlap = sp.symbols("overlap", real=True)
    full_local_source_residual = sp.Matrix([[0, overlap], [overlap, 0]])
    audit.check("multi-root", "full local source allocations require orthogonality", sp.factor(full_local_source_residual.det()) == -overlap**2, sp.factor(full_local_source_residual.det()), "-overlap^2")

    audit.check(
        "scope",
        "open-gate firewall",
        not SCOPE["all_nonlinear_predictable_controls"]
        and not SCOPE["production_multi_root_aggregation"]
        and not SCOPE["t050_closed"]
        and not SCOPE["a13_closed"]
        and not SCOPE["sector_a_closed"]
        and "does not prove" in NO_OVERCLAIM,
        SCOPE,
        "conditional boundary only; all global gates open",
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
            "mass_floor": mass_floor,
            "mass_floor_minors": minors,
            "lower_symbol": lower_symbol,
            "r130_L6": l6,
            "r130_H6": h6,
            "affine_past_delta_coefficients": [2, 1, sp.Rational(1, 2)],
            "endpoint_loss_strict_upper": target_loss,
            "loss_sturm_coefficients_ascending": p19.all_coeffs()[::-1],
            "loss_sturm_zero_signs": loss_zero,
            "loss_sturm_infinity_signs": loss_inf,
            "lower_symbol_minimum": minimum,
            "inverse_lambda2_strict_upper": sp.Rational(125, 36),
            "p_over_lambda2_strict_upper": sp.Rational(4, 3),
            "uniform_past_collar_coefficients": {
                "N_MW": uniform_nmw,
                "N_MY": uniform_nmy,
                "N_squared": uniform_n2,
            },
            "zero_current_affine_past_gap_strict_lower": zero_current_gap,
            "past_collar_budget": collar_budget,
            "source_hessian": source_hessian,
            "retained_gap_strict_lower": retained_gap,
            "nonlinear_fixture_c": c,
            "nonlinear_linear_test_loss": linear_loss,
            "nonlinear_bump_center": bump_center,
            "nonlinear_bump_augmented_upper": source_hessian - bump_loss_floor,
            "conditional_operator_endpoint_threshold": -conditional_threshold,
            "multi_root_endpoint_matrix": endpoint_matrix.tolist(),
            "multi_root_augmented_matrix": global_matrix.tolist(),
            "multi_root_augmented_eigenvalues": global_eigenvalues,
        },
        "scope": SCOPE,
        "no_overclaim": NO_OVERCLAIM,
        "authority_hashes": {
            "A1": sha256(A1_MANIFEST),
            "R-130-result": sha256(r130_path),
            "R-151-result": sha256(r151_path),
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

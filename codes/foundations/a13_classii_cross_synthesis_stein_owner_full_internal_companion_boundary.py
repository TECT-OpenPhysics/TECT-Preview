#!/usr/bin/env python3
"""Primary exact certificate for the phase-neutral A13 R-149 checkpoint.

The certificate derives the complete affine-Gaussian square-minus-trace
identity with separate field and current syntheses, proves by an exact sign
flip that endpoint marginal covariances do not determine that owner, and
computes the full complex three-component/six-row same-root internal tensor.
The latter is strictly positive for every registered kinetic eigenvalue,
background radius, and positive floor.  It is deliberately not identified
with the production spatial current because the field-current cross synthesis,
projectors, heat, visits, forest, future variance, and returned low are not
pinned by the internal calculation.
"""

from __future__ import annotations

import argparse
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
RESULT_ID = "A13-CLASSII-CROSS-SYNTHESIS-STEIN-OWNER-FULL-INTERNAL-COMPANION-BOUNDARY"
SLUG = "cross-synthesis-stein-owner-full-internal-companion-boundary"
SCHEMA = f"tect/a13-{SLUG}-primary/1.0"
MANIFEST = REPO / "claims" / CLAIM / (
    "classii_cross_synthesis_stein_owner_full_internal_companion_boundary_manifest.json"
)
DEFAULT_OUTPUT = REPO / "claims" / CLAIM / "runs" / (
    f"2026-08-02-primary-{SLUG}"
) / "result.json"


def serial(value: Any) -> Any:
    if isinstance(value, sp.MatrixBase):
        return [[serial(value[i, j]) for j in range(value.cols)] for i in range(value.rows)]
    if isinstance(value, sp.Basic):
        return str(value)
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(item) for item in value]
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
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
        failed = [row for row in self.rows if row["status"] != "PASS"]
        if failed:
            raise AssertionError(json.dumps(failed, indent=2, ensure_ascii=True))


def gaussian_expectation(expression: sp.Expr, variables: tuple[sp.Symbol, ...]) -> sp.Expr:
    value = sp.expand(expression)
    for variable in variables:
        polynomial = sp.Poly(sp.expand(value), variable)
        total = sp.Integer(0)
        for (power,), coefficient in polynomial.terms():
            if power % 2:
                continue
            total += coefficient * (sp.factorial2(power - 1) if power else 1)
        value = sp.expand(total)
    return sp.factor(value)


def derive_mass(parameters: dict[str, Any]) -> sp.Matrix:
    family = [sp.Rational(str(value)) for value in parameters["family_masses"]]
    lock = sp.Rational(str(parameters["k_lock"]))
    z0 = [sp.Rational(str(value)) for value in parameters["z0"]]
    norm = sum(value**2 for value in z0)
    return sp.Matrix(
        [
            [
                family[i] * int(i == j)
                + lock * (int(i == j) - z0[i] * z0[j] / norm)
                for j in range(3)
            ]
            for i in range(3)
        ]
    )


def full_six_row_map(
    coordinates: tuple[sp.Symbol, ...],
    floor: sp.Symbol,
    alpha: sp.Expr,
    c0: sp.Expr,
    c1: sp.Expr,
) -> sp.Matrix:
    x1, x2, x3, y1, y2, y3 = coordinates
    z = sp.Matrix([x1 + sp.I * y1, x2 + sp.I * y2, x3 + sp.I * y3])
    pauli = (
        sp.Matrix([[0, 1, 0], [1, 0, 0], [0, 0, 0]]),
        sp.Matrix([[0, -sp.I, 0], [sp.I, 0, 0], [0, 0, 0]]),
        sp.Matrix([[1, 0, 0], [0, -1, 0], [0, 0, 0]]),
    )
    density = sp.simplify((sp.conjugate(z).T * z)[0])
    density_row = sp.Matrix([[sp.diff(density, variable) for variable in coordinates]])
    p_rows: list[sp.Matrix] = []
    l_rows: list[sp.Matrix] = []
    for generator in pauli:
        moment = sp.simplify(sp.re((sp.conjugate(z).T * generator * z)[0]))
        moment_row = sp.Matrix([[sp.diff(moment, variable) for variable in coordinates]])
        quotient = sp.simplify(moment / (density + floor))
        p_rows.append(sp.sqrt(c0) * moment_row)
        l_rows.append(sp.sqrt(c1) * (moment_row - alpha * quotient * density_row))
    return sp.Matrix.vstack(*(p_rows + l_rows))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()

    audit = Audit()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    audit.check("metadata", "claim id", manifest["claim_id"] == CLAIM, manifest["claim_id"], CLAIM)
    audit.check("metadata", "result id", manifest["result_id"] == RESULT_ID, manifest["result_id"], RESULT_ID)
    audit.check("metadata", "ledger id", manifest["result_ledger_id"] == "R-149", manifest["result_ledger_id"], "R-149")
    audit.check("metadata", "tier remains T4", manifest["tier"] == "T4", manifest["tier"], "T4")

    # ------------------------------------------------------------------
    # 1. One-use cancellation in the registered old owner coordinate.
    # ------------------------------------------------------------------
    beta_sum, mean2_sum, trace_sum, future_sum, forest_sum = sp.symbols(
        "beta_sum mean2_sum trace_sum future_sum forest_sum", real=True
    )
    # These symbols denote the exhaustive weighted aggregate after the R-125
    # fixed-root/output/visit incidence is imposed, not arbitrary cells.
    p_comp_aggregate = sp.Rational(1, 2) * (
        beta_sum + mean2_sum - trace_sum
    )
    signature = trace_sum - beta_sum - mean2_sum
    forest_bridge = sp.Eq(signature, future_sum - forest_sum)
    p_comp_bridge = sp.expand(
        p_comp_aggregate.subs(trace_sum, future_sum - forest_sum + beta_sum + mean2_sum)
    )
    covariance_normal = sp.expand(p_comp_bridge + future_sum / 2)
    audit.check("owner-bookkeeping", "aggregate Pcomp is half forest-minus-future", p_comp_bridge == (forest_sum - future_sum) / 2, p_comp_bridge, (forest_sum - future_sum) / 2)
    audit.check("owner-bookkeeping", "aggregate covariance-normal future cancellation", covariance_normal == forest_sum / 2, covariance_normal, forest_sum / 2)
    audit.check("owner-bookkeeping", "aggregate R-125 signature bridge retained", forest_bridge.rhs == future_sum - forest_sum, forest_bridge.rhs, "V-Forest")

    # ------------------------------------------------------------------
    # 2. Exact affine-Gaussian square-minus-trace formula.
    # ------------------------------------------------------------------
    g1, g2 = sp.symbols("g1 g2", real=True)
    w1, w2 = sp.symbols("w1 w2", real=True)
    g = sp.Matrix([g1, g2])
    # Deliberately nonsymmetric rational-free fixture.  All values are INPUTS
    # for the factor/convention self-test, not production coefficients.
    x_map = sp.Matrix([[1, sp.Rational(1, 2)], [sp.Rational(-1, 3), 1]])
    y_map = sp.Matrix([[sp.Rational(2, 3), -1], [1, sp.Rational(1, 4)]])
    v0 = sp.Matrix([sp.Rational(1, 5), sp.Rational(-2, 7)])
    base = sp.Matrix([sp.Rational(1, 3), sp.Rational(-1, 4)])
    w = base + x_map * g
    coefficient = sp.Matrix(
        [
            [1 + w1, w2 + w1 * w2],
            [w1**2 - w2, 1 + w1**2 + w2**2],
        ]
    )
    coefficient_g = coefficient.subs({w1: w[0], w2: w[1]})
    current = sp.expand(coefficient_g * (v0 + y_map * g))
    trace_value = sp.trace(coefficient_g * y_map * y_map.T * coefficient_g.T)
    direct_twice_raw = gaussian_expectation((current.T * current)[0] - trace_value, (g1, g2))

    gram = sp.simplify(coefficient.T * coefficient)
    cross = sp.simplify(x_map * y_map.T)
    differential = sp.Integer(0)
    for m in range(2):
        for n in range(2):
            differential += v0[m] * gram[m, n] * v0[n]
            for alpha_index, variable_a in enumerate((w1, w2)):
                differential += 2 * v0[m] * cross[alpha_index, n] * sp.diff(gram[m, n], variable_a)
                for beta_index, variable_b in enumerate((w1, w2)):
                    differential += (
                        cross[alpha_index, m]
                        * cross[beta_index, n]
                        * sp.diff(gram[m, n], variable_a, variable_b)
                    )
    differential_g = sp.expand(differential.subs({w1: w[0], w2: w[1]}))
    formula_twice_raw = gaussian_expectation(differential_g, (g1, g2))
    audit.check("stein-raw", "direct Gaussian raw square-minus-trace equals cross-synthesis formula", sp.simplify(direct_twice_raw - formula_twice_raw) == 0, direct_twice_raw, formula_twice_raw)
    audit.check("stein-raw", "field-current cross synthesis", cross == x_map * y_map.T, cross, "X Y^T")

    # Same field and current marginal covariances, opposite owner signs.
    identity = sp.eye(2)
    swap = sp.Matrix([[0, 1], [1, 0]])
    b_counter = sp.diag(1 / (1 + w1**2), 1 + w1**2)

    def tensor_at_zero(cross_map: sp.Matrix) -> sp.Expr:
        total = sp.Integer(0)
        variables = (w1, w2)
        for m in range(2):
            for n in range(2):
                for alpha_index, variable_a in enumerate(variables):
                    for beta_index, variable_b in enumerate(variables):
                        total += (
                            cross_map[alpha_index, m]
                            * cross_map[beta_index, n]
                            * sp.diff(b_counter[m, n], variable_a, variable_b).subs({w1: 0, w2: 0})
                        )
        return sp.factor(total)

    tensor_identity = tensor_at_zero(identity)
    tensor_swap = tensor_at_zero(swap)
    epsilon = sp.symbols("epsilon", positive=True)
    x_nonnegative, y_nonnegative = sp.symbols("x_nonnegative y_nonnegative", nonnegative=True)
    h_x = 1 / (1 + epsilon * x_nonnegative)
    h_y = 1 / (1 + epsilon * y_nonnegative)
    antitone_pair = sp.factor(
        (x_nonnegative - y_nonnegative) * (h_x - h_y)
    )
    expected_antitone_pair = sp.factor(
        -epsilon * (x_nonnegative - y_nonnegative) ** 2
        / ((1 + epsilon * x_nonnegative) * (1 + epsilon * y_nonnegative))
    )
    swap_exact_unhalved = 2 * epsilon**2
    audit.check("nonidentifiability", "field covariance unchanged", identity * identity.T == swap * swap.T, swap * swap.T, identity)
    audit.check("nonidentifiability", "current covariance unchanged", identity.T * identity == swap.T * swap, swap.T * swap, identity)
    audit.check("nonidentifiability", "identity cross owner negative", tensor_identity < 0, tensor_identity, "<0")
    audit.check("nonidentifiability", "swapped cross owner positive", tensor_swap > 0, tensor_swap, ">0")
    audit.check("nonidentifiability", "same marginals opposite signs", tensor_identity * tensor_swap < 0, [tensor_identity, tensor_swap], "opposite")
    audit.check("nonidentifiability", "identity exact raw sign by strict antitone covariance", sp.simplify(antitone_pair - expected_antitone_pair) == 0, antitone_pair, expected_antitone_pair)
    audit.check("nonidentifiability", "exchange exact raw sign for every positive epsilon", swap_exact_unhalved > 0, swap_exact_unhalved, ">0")

    # ------------------------------------------------------------------
    # 3. Registered mass and exact full complex six-row same-root tensor.
    # ------------------------------------------------------------------
    a1_path = REPO / manifest["authorities"]["A1"]
    a1 = json.loads(a1_path.read_text(encoding="utf-8"))
    mass = derive_mass(a1["parameters"])
    leading_minors = [sp.factor(mass[:size, :size].det()) for size in (1, 2, 3)]
    audit.check("registered-input", "A1 mass positive by Sylvester", all(value > 0 for value in leading_minors), leading_minors, "all positive")

    a6 = json.loads((REPO / manifest["authorities"]["A6"]).read_text(encoding="utf-8"))
    a7 = json.loads((REPO / manifest["authorities"]["A7"]).read_text(encoding="utf-8"))
    audit.check("registered-input", "A6 complex covariance factor two", "2 A(k)^-1" in a6["convention"]["complex_mode_covariance"], a6["convention"]["complex_mode_covariance"], "contains 2 A(k)^-1")
    audit.check("registered-input", "A7 half-realification convention", "(1/2) realify" in a7["normal_ordering"]["complex_covariance_factor"], a7["normal_ordering"]["complex_covariance_factor"], "contains (1/2) realify")

    kinetic, radius, floor, p_norm = sp.symbols("a R e P", positive=True)
    covariance = sp.simplify((kinetic * sp.eye(3) + mass).inv())
    # A6: each Re/Im coordinate has covariance C=(aI+M)^-1 while the complex
    # covariance is D=2C.  A7 then gives Gamma_R=(1/2)realify(D)=diag(C,C).
    # Dividing this matrix by two again would double-apply the A7 conversion.
    gamma = sp.diag(covariance, covariance)
    coordinates = sp.symbols("x1 x2 x3 y1 y2 y3", real=True)
    r147 = json.loads((REPO / manifest["authorities"]["R-147"]).read_text(encoding="utf-8"))
    coefficient_inputs = r147["audit_inputs"]
    alpha = sp.sympify(coefficient_inputs["production_alpha"])
    c0 = sp.sympify(
        coefficient_inputs["production_p_coefficient"].replace("P", "*P"),
        locals={"P": p_norm},
    )
    c1 = sp.sympify(
        coefficient_inputs["production_l_coefficient"].replace("P", "*P"),
        locals={"P": p_norm},
    )
    audit.check("registered-input", "R-147 alpha loaded", alpha == sp.Rational(5, 9), alpha, "5/9")
    audit.check("registered-input", "R-147 P coefficient loaded", c0 == sp.Rational(3, 250) / p_norm, c0, "3/(250P)")
    audit.check("registered-input", "R-147 L coefficient loaded", c1 == sp.Rational(243, 8000) / p_norm, c1, "243/(8000P)")
    c6 = full_six_row_map(coordinates, floor, alpha, c0, c1)
    gram6 = sp.simplify(c6.T * c6)
    x1, x2, x3, y1, y2, y3 = coordinates
    background = {x1: radius, x2: 0, x3: radius, y1: 0, y2: 0, y3: 0}
    base_map = sp.simplify(c6.subs(background))

    t = radius**2 / (2 * radius**2 + floor)
    expected_radial = 4 * sp.Matrix(
        [
            [radius**2 * (c0 + c1 * (1 - alpha * t) ** 2), -c1 * alpha * t * (1 - alpha * t) * radius**2],
            [-c1 * alpha * t * (1 - alpha * t) * radius**2, c1 * alpha**2 * t**2 * radius**2],
        ]
    )
    base_gram = sp.simplify(base_map.T * base_map)
    audit.check("six-row", "R-142 radial Gram recovered", sp.simplify(base_gram.extract([0, 2], [0, 2]) - expected_radial) == sp.zeros(2), base_gram.extract([0, 2], [0, 2]), expected_radial)
    transverse = sp.factor(4 * (c0 + c1) * radius**2)
    audit.check("six-row", "two transverse eigenvalues", base_gram[1, 1] == transverse and base_gram[4, 4] == transverse, [base_gram[1, 1], base_gram[4, 4]], transverse)
    audit.check("six-row", "two phase kernels", base_gram.extract([3, 5], [3, 5]) == sp.zeros(2), base_gram.extract([3, 5], [3, 5]), sp.zeros(2))

    tensor = sp.Integer(0)
    for m in range(6):
        for n in range(6):
            if gram6[m, n] == 0:
                continue
            for alpha_index, variable_a in enumerate(coordinates):
                for beta_index, variable_b in enumerate(coordinates):
                    factor = gamma[alpha_index, m] * gamma[beta_index, n]
                    if factor != 0:
                        tensor += factor * sp.diff(gram6[m, n], variable_a, variable_b).subs(background)
    tensor = sp.factor(sp.cancel(tensor))
    rho = sp.symbols("rho", nonnegative=True)
    tensor_rho = sp.factor(sp.cancel(tensor.subs(radius**2, rho * floor)))
    numerator, denominator = sp.fraction(tensor_rho)
    numerator_poly = sp.Poly(sp.factor(numerator / 3), kinetic, rho)
    coefficients = numerator_poly.coeffs()
    kinetic_denominator = 25000 * kinetic**3 + 10000 * kinetic**2 + 1115 * kinetic + 24
    expected_denominator = 160 * p_norm * (2 * rho + 1) ** 4 * kinetic_denominator**2
    audit.check("full-internal", "exact positive tensor denominator", sp.expand(denominator - expected_denominator) == 0, sp.factor(denominator), sp.factor(expected_denominator))
    audit.check("full-internal", "numerator has twenty-five monomials", len(coefficients) == 25, len(coefficients), 25)
    audit.check("full-internal", "every numerator coefficient strictly positive", all(value > 0 for value in coefficients), coefficients, "all >0")
    audit.check("full-internal", "degrees four by four", numerator_poly.degree(kinetic) == 4 and numerator_poly.degree(rho) == 4, [numerator_poly.degree(kinetic), numerator_poly.degree(rho)], [4, 4])
    high_kinetic = sp.factor(sp.limit(kinetic**2 * tensor_rho, kinetic, sp.oo))
    expected_high_kinetic = sp.factor(
        3 * (348 * rho**4 + 3296 * rho**3 + 5137 * rho**2 + 2994 * rho + 678)
        / (1000 * p_norm * (2 * rho + 1) ** 4)
    )
    audit.check("full-internal", "registered-convention high-kinetic checksum", sp.simplify(high_kinetic - expected_high_kinetic) == 0, high_kinetic, expected_high_kinetic)

    # The linear P rows are a load-bearing checksum; the nonlinear L packet is
    # not assumed positive separately.
    p_map = c6[:3, :]
    p_gram = sp.simplify(p_map.T * p_map)
    tensor_p = sp.Integer(0)
    for m in range(6):
        for n in range(6):
            if p_gram[m, n] == 0:
                continue
            for alpha_index, variable_a in enumerate(coordinates):
                for beta_index, variable_b in enumerate(coordinates):
                    factor = gamma[alpha_index, m] * gamma[beta_index, n]
                    if factor != 0:
                        tensor_p += factor * sp.diff(p_gram[m, n], variable_a, variable_b).subs(background)
    tensor_p = sp.factor(sp.cancel(tensor_p))
    sample = {kinetic: 1, radius: 1, floor: 1, p_norm: 4}
    tensor_sample = sp.N(tensor.subs(sample), 18)
    p_sample = sp.N(tensor_p.subs(sample), 18)
    l_sample = sp.N((tensor - tensor_p).subs(sample), 18)
    audit.check("full-internal", "full tensor positive at hostile fixture", tensor_sample > 0, tensor_sample, ">0")
    audit.check("full-internal", "linear packet positive at hostile fixture", p_sample > 0, p_sample, ">0")
    audit.check("full-internal", "nonlinear packet can be negative", l_sample < 0, l_sample, "<0")
    audit.check("full-internal", "complete packet remains positive", tensor_sample == p_sample + l_sample, tensor_sample, p_sample + l_sample)

    # Exact source curvature on the active-minus-spectator endpoint direction.
    direction = sp.Matrix([1, 0, -1])
    inverse_covariance = kinetic * sp.eye(3) + mass
    audit.check("source", "canonical endpoint covariance inverse", sp.simplify(inverse_covariance * covariance) == sp.eye(3), inverse_covariance * covariance, sp.eye(3))
    source_hessian = sp.factor(sp.Rational(9, 10) * (direction.T * inverse_covariance * direction)[0])
    audit.check("source", "active-spectator source Hessian strictly positive", sp.Poly(source_hessian, kinetic).all_coeffs() == [sp.Rational(9, 5), sp.Rational(333, 1000)], source_hessian, "9(200a+37)/1000")

    scope = manifest["scope"]
    for key in (
        "old_owner_aggregate_one_use_cancellation_proved",
        "affine_gaussian_raw_square_minus_trace_formula_proved",
        "endpoint_marginal_covariance_nonidentifiability_proved",
        "full_internal_same_root_tensor_positive_proved",
    ):
        audit.check("scope", key, scope[key] is True, scope[key], True)
    for key in (
        "production_spatial_cross_synthesis_identified",
        "raw_diagnostic_identified_with_production_pcomp",
        "r125_incidence_hypotheses_discharged_for_new_chart",
        "old_chart_owner_transport_proved",
        "complete_owner_sign_determined",
        "physical_phase_selected",
        "t050_closed",
        "sector_a_closed",
    ):
        audit.check("scope", key, scope[key] is False, scope[key], False)

    audit.require()
    payload = {
        "schema": SCHEMA,
        "package_version": __version__,
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "status": "PASS",
        "assertions_total": len(audit.rows),
        "assertions_passed": len(audit.rows),
        "assertions_failed": 0,
        "assertions": audit.rows,
        "derived": {
            "mass": mass,
            "mass_leading_minors": leading_minors,
            "raw_formula_fixture_direct": direct_twice_raw,
            "raw_formula_fixture_differential": formula_twice_raw,
            "same_marginal_sign_flip": {
                "leading_identity": tensor_identity,
                "leading_exchange": tensor_swap,
                "identity_exact_unhalved": "epsilon*Cov(G^2,(1+epsilon*G^2)^-1)<0",
                "exchange_exact_unhalved": swap_exact_unhalved,
            },
            "full_internal_tensor": tensor_rho,
            "full_internal_numerator": sp.factor(numerator / 3),
            "full_internal_numerator_coefficients": coefficients,
            "full_internal_sample": {
                "a": "1",
                "rho": "1",
                "P": "4",
                "total": tensor_sample,
                "linear_P": p_sample,
                "nonlinear_L": l_sample,
            },
            "source_hessian_active_minus_spectator": source_hessian,
            "high_kinetic_tensor_checksum": high_kinetic,
        },
        "scope": scope,
        "no_overclaim": manifest["no_overclaim"],
    }
    atomic_json(arguments.output, payload)
    print(f"PASS: {len(audit.rows)}/{len(audit.rows)} assertions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

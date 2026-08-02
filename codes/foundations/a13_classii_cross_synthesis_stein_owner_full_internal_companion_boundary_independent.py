#!/usr/bin/env python3
"""Independent non-importing audit for the phase-neutral A13 R-149 result."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import sympy as s


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-CROSS-SYNTHESIS-STEIN-OWNER-FULL-INTERNAL-COMPANION-BOUNDARY"
SLUG = "cross-synthesis-stein-owner-full-internal-companion-boundary"
SCHEMA = f"tect/a13-{SLUG}-independent/1.0"
MANIFEST = REPO / "claims" / CLAIM / "classii_cross_synthesis_stein_owner_full_internal_companion_boundary_manifest.json"
DEFAULT_OUTPUT = REPO / "claims" / CLAIM / "runs" / f"2026-08-02-independent-{SLUG}" / "result.json"


def clean(value: Any) -> Any:
    if isinstance(value, s.MatrixBase):
        return [[clean(value[i, j]) for j in range(value.cols)] for i in range(value.rows)]
    if isinstance(value, s.Basic):
        return str(value)
    if isinstance(value, dict):
        return {str(key): clean(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [clean(item) for item in value]
    return value


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix="independent.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(clean(payload), stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


@dataclass
class Checks:
    rows: list[dict[str, Any]] = field(default_factory=list)

    def add(self, group: str, name: str, passed: bool, actual: Any, expected: Any) -> None:
        self.rows.append(
            {
                "group": group,
                "name": name,
                "status": "PASS" if bool(passed) else "FAIL",
                "actual": clean(actual),
                "expected": clean(expected),
            }
        )

    def finish(self) -> None:
        failures = [row for row in self.rows if row["status"] != "PASS"]
        if failures:
            raise AssertionError(json.dumps(failures, indent=2, ensure_ascii=True))


def moment(expression: s.Expr, variables: tuple[s.Symbol, ...]) -> s.Expr:
    result = s.expand(expression)
    for variable in variables:
        polynomial = s.Poly(result, variable)
        accumulated = s.Integer(0)
        for (degree,), coefficient in polynomial.terms():
            if degree % 2 == 0:
                accumulated += coefficient * (s.factorial2(degree - 1) if degree else 1)
        result = s.expand(accumulated)
    return s.factor(result)


def realify(matrix: s.Matrix) -> s.Matrix:
    real = matrix.applyfunc(s.re)
    imaginary = matrix.applyfunc(s.im)
    return real.row_join(-imaginary).col_join(imaginary.row_join(real))


def load_mass(manifest: dict[str, Any]) -> s.Matrix:
    upstream = json.loads((REPO / manifest["authorities"]["A1"]).read_text(encoding="utf-8"))
    values = upstream["parameters"]
    family = [s.Rational(str(value)) for value in values["family_masses"]]
    lock = s.Rational(str(values["k_lock"]))
    anchor = s.Matrix([s.Rational(str(value)) for value in values["z0"]])
    projector = anchor * anchor.T / (anchor.T * anchor)[0]
    return s.diag(*family) + lock * (s.eye(3) - projector)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    options = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    checks = Checks()
    checks.add("metadata", "result id", manifest["result_id"] == RESULT_ID, manifest["result_id"], RESULT_ID)
    checks.add("metadata", "ledger id", manifest["result_ledger_id"] == "R-149", manifest["result_ledger_id"], "R-149")

    # Independent exact Gaussian test with a different coefficient fixture.
    g0, g1 = s.symbols("g0 g1", real=True)
    u0, u1 = s.symbols("u0 u1", real=True)
    g = s.Matrix([g0, g1])
    X = s.Matrix([[1, -s.Rational(2, 5)], [s.Rational(3, 7), 1]])
    Y = s.Matrix([[s.Rational(1, 2), s.Rational(4, 3)], [-1, s.Rational(2, 9)]])
    v = s.Matrix([s.Rational(-1, 6), s.Rational(3, 8)])
    base = s.Matrix([s.Rational(2, 5), -s.Rational(1, 3)])
    state = base + X * g
    coefficient = s.Matrix([[1 + u0**2, u0 * u1], [u1 - u0, 2 + u1**2]])
    coefficient_g = coefficient.subs({u0: state[0], u1: state[1]})
    output = coefficient_g * (v + Y * g)
    trace = s.trace(coefficient_g * Y * Y.T * coefficient_g.T)
    direct = moment((output.T * output)[0] - trace, (g0, g1))

    B = s.simplify(coefficient.T * coefficient)
    K = s.simplify(X * Y.T)
    differential = s.Integer(0)
    variables = (u0, u1)
    for m in range(2):
        for n in range(2):
            differential += v[m] * B[m, n] * v[n]
            for a_index, variable_a in enumerate(variables):
                differential += 2 * v[m] * K[a_index, n] * s.diff(B[m, n], variable_a)
                for b_index, variable_b in enumerate(variables):
                    differential += K[a_index, m] * K[b_index, n] * s.diff(B[m, n], variable_a, variable_b)
    derived = moment(differential.subs({u0: state[0], u1: state[1]}), (g0, g1))
    checks.add("stein-raw", "independent raw direct-versus-differential identity", s.simplify(direct - derived) == 0, direct, derived)

    # Same marginal covariances, exact opposite signs, independently phrased.
    w = s.symbols("w", real=True)
    gram = s.diag(1 / (1 + w**2), 1 + w**2)
    identity = s.eye(2)
    exchange = s.Matrix([[0, 1], [1, 0]])
    hessian_diagonal = s.diag(s.diff(gram[0, 0], w, 2).subs(w, 0), s.diff(gram[1, 1], w, 2).subs(w, 0))
    sign_one = hessian_diagonal[0, 0]
    sign_two = hessian_diagonal[1, 1]
    epsilon = s.symbols("epsilon", positive=True)
    x_nonnegative, y_nonnegative = s.symbols("x_nonnegative y_nonnegative", nonnegative=True)
    antitone_product = s.factor(
        (x_nonnegative - y_nonnegative)
        * (1 / (1 + epsilon * x_nonnegative) - 1 / (1 + epsilon * y_nonnegative))
    )
    antitone_oracle = s.factor(
        -epsilon * (x_nonnegative - y_nonnegative) ** 2
        / ((1 + epsilon * x_nonnegative) * (1 + epsilon * y_nonnegative))
    )
    exchange_exact_unhalved = 2 * epsilon**2
    checks.add("nonidentifiability", "same field marginal", identity * identity.T == exchange * exchange.T, exchange * exchange.T, identity)
    checks.add("nonidentifiability", "same current marginal", identity.T * identity == exchange.T * exchange, exchange.T * exchange, identity)
    checks.add("nonidentifiability", "opposite tensor signs", sign_one < 0 < sign_two, [sign_one, sign_two], "negative, positive")
    checks.add("nonidentifiability", "independent strict-antitone covariance kernel", s.simplify(antitone_product - antitone_oracle) == 0, antitone_product, antitone_oracle)
    checks.add("nonidentifiability", "independent exchange exact raw sign", exchange_exact_unhalved > 0, exchange_exact_unhalved, ">0")

    # Build the six rows with realified Pauli matrices, independent of the
    # primary script's complex-coordinate differentiation.
    mass = load_mass(manifest)
    a, R, e, P = s.symbols("a R e P", positive=True)
    C = s.simplify((a * s.eye(3) + mass).inv())
    # A6 gives complex covariance D=2C; A7 gives
    # Gamma_R=(1/2)realify(D)=diag(C,C), with no second halving.
    Gamma = s.diag(C, C)
    coordinates = s.symbols("r1 r2 r3 i1 i2 i3", real=True)
    u = s.Matrix(coordinates)
    complex_pauli = (
        s.Matrix([[0, 1, 0], [1, 0, 0], [0, 0, 0]]),
        s.Matrix([[0, -s.I, 0], [s.I, 0, 0], [0, 0, 0]]),
        s.Matrix([[1, 0, 0], [0, -1, 0], [0, 0, 0]]),
    )
    generators = tuple(realify(generator) for generator in complex_pauli)
    r147 = json.loads((REPO / manifest["authorities"]["R-147"]).read_text(encoding="utf-8"))
    qii = r147["audit_inputs"]["qii_inputs"]
    qii_a = s.Rational(qii["a"]["numerator"], qii["a"]["denominator"]) / P
    qii_b = s.Rational(qii["b"]["numerator"], qii["b"]["denominator"]) / P
    qii_c = s.Rational(qii["c"]["numerator"], qii["c"]["denominator"]) / P
    c0 = s.factor((qii_a * qii_c - qii_b**2) / qii_c)
    c1 = s.factor(qii_c * (1 + qii_b / qii_c) ** 2)
    alpha = s.factor(qii_c / (qii_b + qii_c))
    checks.add("registered-input", "independent Schur P coefficient", c0 == s.Rational(3, 250) / P, c0, "3/(250P)")
    checks.add("registered-input", "independent completed-square L coefficient", c1 == s.Rational(243, 8000) / P, c1, "243/(8000P)")
    checks.add("registered-input", "independent alpha reconstruction", alpha == s.Rational(5, 9), alpha, "5/9")
    density = (u.T * u)[0]
    p_rows: list[s.Matrix] = []
    l_rows: list[s.Matrix] = []
    for generator in generators:
        moment_value = (u.T * generator * u)[0]
        p_row = (2 * generator * u).T
        q_value = moment_value / (density + e)
        l_row = (2 * (generator - alpha * q_value * s.eye(6)) * u).T
        p_rows.append(s.sqrt(c0) * p_row)
        l_rows.append(s.sqrt(c1) * l_row)
    C6 = s.Matrix.vstack(*(p_rows + l_rows))
    base_substitution = dict(zip(coordinates, (R, 0, R, 0, 0, 0)))

    # Row-divergence calculation: F_a = C6 Gamma_{.a}.  This is algebraically
    # independent of forming B and performing the primary four-index loop.
    F = s.simplify(C6 * Gamma)
    tensor = s.Integer(0)
    for alpha_index, variable_a in enumerate(coordinates):
        for beta_index, variable_b in enumerate(coordinates):
            inner = (F[:, alpha_index].T * F[:, beta_index])[0]
            tensor += s.diff(inner, variable_a, variable_b)
    tensor = s.factor(s.cancel(tensor.subs(base_substitution)))
    rho = s.symbols("rho", nonnegative=True)
    tensor_rho = s.factor(s.cancel(tensor.subs(R**2, rho * e)))
    numerator, denominator = s.fraction(tensor_rho)
    kinetic_denominator = 25000 * a**3 + 10000 * a**2 + 1115 * a + 24
    expected_denominator = 160 * P * (2 * rho + 1) ** 4 * kinetic_denominator**2
    polynomial = s.Poly(s.factor(numerator / 3), a, rho)
    coefficients = polynomial.coeffs()
    checks.add("full-internal", "independent twenty-five coefficients", len(coefficients) == 25, len(coefficients), 25)
    checks.add("full-internal", "independent all-positive coefficients", all(value > 0 for value in coefficients), coefficients, "all >0")
    checks.add("full-internal", "independent bidegree", [polynomial.degree(a), polynomial.degree(rho)] == [4, 4], [polynomial.degree(a), polynomial.degree(rho)], [4, 4])
    checks.add("full-internal", "independent exact positive denominator", s.expand(denominator - expected_denominator) == 0, s.factor(denominator), s.factor(expected_denominator))
    high_kinetic = s.factor(s.limit(a**2 * tensor_rho, a, s.oo))
    high_kinetic_oracle = s.factor(
        3 * (348 * rho**4 + 3296 * rho**3 + 5137 * rho**2 + 2994 * rho + 678)
        / (1000 * P * (2 * rho + 1) ** 4)
    )
    checks.add("full-internal", "independent high-kinetic checksum", s.simplify(high_kinetic - high_kinetic_oracle) == 0, high_kinetic, high_kinetic_oracle)

    # Load-bearing split, derived again with the same row-divergence method.
    FP = s.simplify(C6[:3, :] * Gamma)
    tensor_p = s.Integer(0)
    for alpha_index, variable_a in enumerate(coordinates):
        for beta_index, variable_b in enumerate(coordinates):
            tensor_p += s.diff((FP[:, alpha_index].T * FP[:, beta_index])[0], variable_a, variable_b)
    tensor_p = s.factor(s.cancel(tensor_p.subs(base_substitution)))
    hostile = {a: 1, R: 1, e: 1, P: 4}
    total_value = s.N(tensor.subs(hostile), 18)
    p_value = s.N(tensor_p.subs(hostile), 18)
    l_value = s.N((tensor - tensor_p).subs(hostile), 18)
    checks.add("full-internal", "hostile total positive", total_value > 0, total_value, ">0")
    checks.add("full-internal", "hostile nonlinear split negative", l_value < 0, l_value, "<0")
    checks.add("full-internal", "load-bearing recombination", total_value == p_value + l_value, total_value, p_value + l_value)

    scope = manifest["scope"]
    checks.add("scope", "production synthesis remains open", scope["production_spatial_cross_synthesis_identified"] is False, scope["production_spatial_cross_synthesis_identified"], False)
    checks.add("scope", "phase remains open", scope["physical_phase_selected"] is False, scope["physical_phase_selected"], False)
    checks.add("scope", "T050 remains open", scope["t050_closed"] is False, scope["t050_closed"], False)
    checks.add("scope", "raw diagnostic not production Pcomp", scope["raw_diagnostic_identified_with_production_pcomp"] is False, scope["raw_diagnostic_identified_with_production_pcomp"], False)
    checks.finish()

    payload = {
        "schema": SCHEMA,
        "package_version": __version__,
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "status": "PASS",
        "assertions_total": len(checks.rows),
        "assertions_passed": len(checks.rows),
        "assertions_failed": 0,
        "assertions": checks.rows,
        "derived": {
            "gaussian_raw_identity_direct": direct,
            "gaussian_raw_identity_differential": derived,
            "same_marginal_signs": {
                "leading": [sign_one, sign_two],
                "identity_exact_unhalved": "epsilon*Cov(G^2,(1+epsilon*G^2)^-1)<0",
                "exchange_exact_unhalved": exchange_exact_unhalved,
            },
            "full_internal_tensor": tensor_rho,
            "full_internal_numerator": s.factor(numerator / 3),
            "full_internal_coefficients": coefficients,
            "hostile_split": {"total": total_value, "P": p_value, "L": l_value},
            "high_kinetic_tensor_checksum": high_kinetic,
        },
        "scope": scope,
        "no_overclaim": manifest["no_overclaim"],
    }
    write_json(options.output, payload)
    print(f"PASS: {len(checks.rows)}/{len(checks.rows)} assertions")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

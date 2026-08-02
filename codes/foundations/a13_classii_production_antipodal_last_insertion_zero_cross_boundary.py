#!/usr/bin/env python3
"""Primary exact certificate for the A13 R-150 production antipodal boundary.

The certificate installs the first actual A1 Fourier field/current synthesis
requested by R-149.  It proves that one complete antipodal production pair has
zero coincident field-current cross synthesis, while its two-point and Fourier
coefficient cross syntheses are nonzero.  Consequently, for an exhaustive
full-output *last* insertion, the R-149 affine-Gaussian identity makes the
conditional absolute raw/Pcomp endpoint atom nonnegative without spending
source or sextic budget.  Its relative endpoint secant, earlier roots with
future-dependent feedback, and nonlocal output projectors are deliberately
outside the theorem.
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
RESULT_ID = "A13-CLASSII-PRODUCTION-ANTIPODAL-LAST-INSERTION-ZERO-CROSS-BOUNDARY"
LEDGER_ID = "R-150"
SLUG = "production-antipodal-last-insertion-zero-cross-boundary"
SCHEMA = f"tect/a13-{SLUG}-primary/1.0"
MANIFEST = REPO / "claims" / CLAIM / (
    "classii_production_antipodal_last_insertion_zero_cross_boundary_manifest.json"
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
        failures = [row for row in self.rows if row["status"] != "PASS"]
        if failures:
            raise AssertionError(json.dumps(failures, indent=2, ensure_ascii=True))


def gaussian_expectation(expression: sp.Expr, variables: tuple[sp.Symbol, ...]) -> sp.Expr:
    value = sp.expand(expression)
    for variable in variables:
        polynomial = sp.Poly(value, variable)
        total = sp.Integer(0)
        for (power,), coefficient in polynomial.terms():
            if power % 2 == 0:
                total += coefficient * (sp.factorial2(power - 1) if power else 1)
        value = sp.expand(total)
    return sp.factor(value)


def derive_mass(parameters: dict[str, Any]) -> sp.Matrix:
    family = [sp.Rational(str(value)) for value in parameters["family_masses"]]
    lock = sp.Rational(str(parameters["k_lock"]))
    z0 = sp.Matrix([sp.Rational(str(value)) for value in parameters["z0"]])
    projector = z0 * z0.T / (z0.T * z0)[0]
    return sp.diag(*family) + lock * (sp.eye(3) - projector)


def unit_reduce(matrix: sp.Matrix, cosine: sp.Symbol, sine: sp.Symbol) -> sp.Matrix:
    return matrix.applyfunc(
        lambda entry: sp.factor(sp.expand(entry).subs(cosine**2, 1 - sine**2))
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()

    audit = Audit()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    audit.check("metadata", "claim id", manifest["claim_id"] == CLAIM, manifest["claim_id"], CLAIM)
    audit.check("metadata", "result id", manifest["result_id"] == RESULT_ID, manifest["result_id"], RESULT_ID)
    audit.check("metadata", "ledger id", manifest["result_ledger_id"] == LEDGER_ID, manifest["result_ledger_id"], LEDGER_ID)
    audit.check("metadata", "tier remains T4", manifest["tier"] == "T4", manifest["tier"], "T4")

    # Canonical A1 production covariance, without the scalar-slice shortcut.
    a1 = json.loads((REPO / manifest["authorities"]["A1"]).read_text(encoding="utf-8"))
    parameters = a1["parameters"]
    mass = sp.simplify(derive_mass(parameters))
    expected_mass = sp.Matrix(
        [
            [sp.Rational(1, 10), -sp.Rational(1, 20), -sp.Rational(1, 20)],
            [-sp.Rational(1, 20), sp.Rational(13, 100), -sp.Rational(1, 20)],
            [-sp.Rational(1, 20), -sp.Rational(1, 20), sp.Rational(17, 100)],
        ]
    )
    audit.check("production", "exact family-lock mass", mass == expected_mass, mass, expected_mass)
    minors = tuple(sp.factor(mass[:size, :size].det()) for size in (1, 2, 3))
    audit.check("production", "mass Sylvester minors positive", all(value > 0 for value in minors), minors, "all >0")

    kinetic = sp.symbols("a", positive=True)
    covariance = sp.simplify((kinetic * sp.eye(3) + mass).inv())
    audit.check("production", "symbol-covariance inverse identity", sp.simplify((kinetic * sp.eye(3) + mass) * covariance) == sp.eye(3), sp.simplify((kinetic * sp.eye(3) + mass) * covariance), sp.eye(3))
    denominator = sp.factor((kinetic * sp.eye(3) + mass).det())
    denominator_oracle = (25000 * kinetic**3 + 10000 * kinetic**2 + 1115 * kinetic + 24) / 25000
    audit.check("production", "exact covariance denominator", sp.simplify(denominator - denominator_oracle) == 0, denominator, denominator_oracle)

    length = sp.Rational(str(parameters["Lx"]))
    volume = (
        sp.Rational(str(parameters["Lx"]))
        * sp.Rational(str(parameters["Ly"]))
        * sp.Rational(str(parameters["Lz"]))
    )
    wave = 2 * sp.pi / length
    r_value = sp.Rational(str(parameters["r"]))
    z_value = sp.Rational(str(parameters["Z"]))
    y_value = sp.Rational(str(parameters["Y"]))
    a_wave = sp.factor(r_value + z_value * wave**2 + y_value * wave**4)
    a_twice = sp.factor(r_value + z_value * (2 * wave) ** 2 + y_value * (2 * wave) ** 4)
    audit.check("production", "first retained kinetic positive", sp.N(a_wave, 40) > 0, sp.N(a_wave, 18), ">0")
    audit.check("production", "second retained kinetic positive", sp.N(a_twice, 40) > 0, sp.N(a_twice, 18), ">0")
    audit.check("production", "declared first wave is pi/8", sp.simplify(wave - sp.pi / 8) == 0, wave, sp.pi / 8)
    audit.check("production", "declared torus volume", volume == 4096, volume, 4096)

    a6 = json.loads((REPO / manifest["authorities"]["A6"]).read_text(encoding="utf-8"))
    a7 = json.loads((REPO / manifest["authorities"]["A7"]).read_text(encoding="utf-8"))
    audit.check("convention", "A6 complex covariance factor two", "2 A(k)^-1" in a6["convention"]["complex_mode_covariance"], a6["convention"]["complex_mode_covariance"], "contains 2 A(k)^-1")
    audit.check("convention", "A7 half-realification convention", "(1/2) realify" in a7["normal_ordering"]["complex_covariance_factor"], a7["normal_ordering"]["complex_covariance_factor"], "contains (1/2) realify")

    # Generic duplicated six-real covariance and common complex phase.
    c11, c12, c13, c22, c23, c33 = sp.symbols("c11 c12 c13 c22 c23 c33", real=True)
    c3 = sp.Matrix([[c11, c12, c13], [c12, c22, c23], [c13, c23, c33]])
    gamma = sp.diag(c3, c3)
    zero3 = sp.zeros(3)
    identity3 = sp.eye(3)
    complex_structure = sp.Matrix.vstack(
        sp.Matrix.hstack(zero3, -identity3),
        sp.Matrix.hstack(identity3, zero3),
    )
    cosine, sine, kappa = sp.symbols("c s k", real=True)
    identity6 = sp.eye(6)
    phase_plus = cosine * identity6 + sine * complex_structure
    phase_minus = cosine * identity6 - sine * complex_structure
    audit.check("phase", "complex structure skew", complex_structure.T == -complex_structure, complex_structure.T, -complex_structure)
    audit.check("phase", "complex structure squares minus identity", complex_structure**2 == -identity6, complex_structure**2, -identity6)
    audit.check("phase", "production real covariance commutes with common phase", complex_structure * gamma == gamma * complex_structure, complex_structure * gamma - gamma * complex_structure, sp.zeros(6))
    audit.check("phase", "opposite phase is transpose", phase_minus == phase_plus.T, phase_minus, phase_plus.T)

    field_covariance = phase_plus * gamma * phase_plus.T + phase_minus * gamma * phase_minus.T
    current_covariance = (
        kappa**2 * complex_structure * phase_plus * gamma * phase_plus.T * complex_structure.T
        + kappa**2 * complex_structure * phase_minus * gamma * phase_minus.T * complex_structure.T
    )
    cross_same_point = (
        phase_plus * gamma * (kappa * complex_structure * phase_plus).T
        + phase_minus * gamma * (-kappa * complex_structure * phase_minus).T
    )
    audit.check("synthesis", "antipodal field covariance", unit_reduce(field_covariance - 2 * gamma, cosine, sine) == sp.zeros(6), unit_reduce(field_covariance, cosine, sine), 2 * gamma)
    audit.check("synthesis", "antipodal current covariance", unit_reduce(current_covariance - 2 * kappa**2 * gamma, cosine, sine) == sp.zeros(6), unit_reduce(current_covariance, cosine, sine), 2 * kappa**2 * gamma)
    audit.check("synthesis", "coincident field-current cross synthesis vanishes", unit_reduce(cross_same_point, cosine, sine) == sp.zeros(6), unit_reduce(cross_same_point, cosine, sine), sp.zeros(6))

    # The two-point kernel is nonzero.  No unit-circle substitution is needed.
    cx, sx, cy, sy = sp.symbols("cx sx cy sy", real=True)
    rx_plus = cx * identity6 + sx * complex_structure
    rx_minus = cx * identity6 - sx * complex_structure
    ry_plus = cy * identity6 + sy * complex_structure
    ry_minus = cy * identity6 - sy * complex_structure
    cross_two_point = sp.expand(
        rx_plus * gamma * (kappa * complex_structure * ry_plus).T
        + rx_minus * gamma * (-kappa * complex_structure * ry_minus).T
    )
    sine_difference = sx * cy - cx * sy
    expected_two_point = 2 * kappa * sine_difference * gamma
    audit.check("synthesis", "two-point cross kernel exact", sp.simplify(cross_two_point - expected_two_point) == sp.zeros(6), cross_two_point, expected_two_point)
    hostile_two_point = sp.simplify(cross_two_point.subs({cx: 0, sx: 1, cy: 1, sy: 0, kappa: 1}))
    audit.check("synthesis", "two-point kernel is not identically zero", hostile_two_point == 2 * gamma and hostile_two_point != sp.zeros(6), hostile_two_point, 2 * gamma)
    audit.check("synthesis", "two-point kernel is skew under point exchange", sp.simplify(cross_two_point + cross_two_point.subs({cx: cy, sx: sy, cy: cx, sy: sx}, simultaneous=True)) == sp.zeros(6), "K(x,y)+K(y,x)", 0)
    coefficient_cross = kappa * sp.Matrix.vstack(
        sp.Matrix.hstack(sp.zeros(6), -gamma),
        sp.Matrix.hstack(gamma, sp.zeros(6)),
    )
    audit.check("synthesis", "coefficient-space cross is skew", coefficient_cross.T == -coefficient_cross, coefficient_cross.T, -coefficient_cross)
    audit.check("synthesis", "coefficient-space cross is generically nonzero", coefficient_cross != sp.zeros(12), coefficient_cross, "nonzero")

    # Exact scalar Gaussian checksum for the K=0 last-insertion theorem.
    g1, g2 = sp.symbols("g1 g2", real=True)
    past_field, past_current, root_scale = sp.symbols("w v r", real=True)
    fresh_field = past_field + root_scale * (cosine * g1 + sine * g2)
    fresh_current = past_current + kappa * root_scale * (-sine * g1 + cosine * g2)
    gram_scalar = 1 + fresh_field**2 + fresh_field**4
    primitive_trace = kappa**2 * root_scale**2 * gram_scalar
    direct_unhalved = gaussian_expectation(gram_scalar * fresh_current**2 - primitive_trace, (g1, g2))
    predicted_unhalved = gaussian_expectation(past_current**2 * gram_scalar, (g1, g2))
    direct_unit = sp.factor(direct_unhalved.subs(cosine**2, 1 - sine**2))
    predicted_unit = sp.factor(predicted_unhalved.subs(cosine**2, 1 - sine**2))
    audit.check("last-insertion", "direct square-minus-trace equals predictable square", sp.simplify(direct_unit - predicted_unit) == 0, direct_unit, predicted_unit)
    audit.check("last-insertion", "predictable square is nonnegative", predicted_unit.is_nonnegative is True or sp.Poly(predicted_unit, past_current).coeff_monomial(past_current**2) > 0, predicted_unit, ">=0")
    zero_past = sp.factor(direct_unit.subs(past_current, 0))
    audit.check("last-insertion", "zero-past last insertion cancels exactly", zero_past == 0, zero_past, 0)

    # Source norm in normalized root coordinates: two signs, one later visit.
    h11, h12, h21, h22, t = sp.symbols("h11 h12 h21 h22 t", real=True)
    hp1, hp2, hm1, hm2 = sp.symbols("hp1 hp2 hm1 hm2", real=True)
    h_matrix = sp.Matrix([[h11, h12], [h21, h22]])
    gp = sp.Matrix([hp1, hp2])
    gm = sp.Matrix([hm1, hm2])
    source = gaussian_expectation(t**2 * ((h_matrix * gp).dot(h_matrix * gp) + (h_matrix * gm).dot(h_matrix * gm)), (hp1, hp2, hm1, hm2))
    source_oracle = 2 * t**2 * sp.trace(h_matrix * h_matrix.T)
    audit.check("source", "two-sign Cameron-Martin norm", sp.simplify(source - source_oracle) == 0, source, source_oracle)
    audit.check("source", "action source coefficient", sp.Rational(9, 20) * source_oracle == sp.Rational(9, 10) * t**2 * sp.trace(h_matrix * h_matrix.T), sp.Rational(9, 20) * source_oracle, sp.Rational(9, 10) * t**2 * sp.trace(h_matrix * h_matrix.T))

    # Scope gates are load-bearing: this is a last-insertion theorem only.
    scope = manifest["scope"]
    audit.check("scope", "production antipodal synthesis identified", scope["declared_production_antipodal_synthesis_identified"] is True, scope["declared_production_antipodal_synthesis_identified"], True)
    audit.check("scope", "last insertion only", scope["full_two_root_owner_closed"] is False, scope["full_two_root_owner_closed"], False)
    audit.check("scope", "T050 remains open", scope["t050_closed"] is False and scope["sector_a_closed"] is False, [scope["t050_closed"], scope["sector_a_closed"]], [False, False])

    audit.require()
    payload = {
        "schema": SCHEMA,
        "version": __version__,
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "ledger_id": LEDGER_ID,
        "status": "PASS",
        "scope": manifest["scope"],
        "no_overclaim": manifest["no_overclaim"],
        "derived": {
            "mass": mass,
            "mass_leading_minors": minors,
            "covariance_denominator": denominator,
            "wave": wave,
            "kinetic_at_wave": a_wave,
            "kinetic_at_twice_wave": a_twice,
            "volume": volume,
            "same_point_field_covariance": 2 * gamma / volume,
            "same_point_current_covariance": 2 * kappa**2 * gamma / volume,
            "same_point_cross_synthesis": sp.zeros(6),
            "two_point_cross_synthesis": expected_two_point / volume,
            "coefficient_space_cross_synthesis": coefficient_cross,
            "last_insertion_unhalved_owner_checksum": predicted_unit,
            "two_sign_source_norm": source_oracle,
            "absolute_final_atom_budget_allocation": {"eta": 0, "zeta": 0},
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

#!/usr/bin/env python3
"""Independent certificate for the A13 R-150 antipodal last-endpoint theorem.

This implementation uses the cosine/sine Fourier basis rather than the
directed-mode phase matrices of the primary certificate.  It does not import
the primary module or read its result artifact.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import tempfile
from pathlib import Path
from typing import Any

import numpy as np
import sympy as sp


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-PRODUCTION-ANTIPODAL-LAST-INSERTION-ZERO-CROSS-BOUNDARY"
LEDGER_ID = "R-150"
SLUG = "production-antipodal-last-insertion-zero-cross-boundary"
SCHEMA = f"tect/a13-{SLUG}-independent/1.0"
MANIFEST = REPO / "claims" / CLAIM / (
    "classii_production_antipodal_last_insertion_zero_cross_boundary_manifest.json"
)
DEFAULT_OUTPUT = REPO / "claims" / CLAIM / "runs" / (
    f"2026-08-02-independent-{SLUG}"
) / "result.json"


def clean(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, (np.floating, np.integer)):
        return value.item()
    if isinstance(value, sp.Basic):
        return str(value)
    if isinstance(value, dict):
        return {str(key): clean(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [clean(item) for item in value]
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
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


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(self, group: str, name: str, condition: bool, actual: Any, expected: Any) -> None:
        self.rows.append(
            {
                "group": group,
                "name": name,
                "status": "PASS" if bool(condition) else "FAIL",
                "actual": clean(actual),
                "expected": clean(expected),
            }
        )

    def require(self) -> None:
        failed = [row for row in self.rows if row["status"] != "PASS"]
        if failed:
            raise AssertionError(json.dumps(failed, indent=2, ensure_ascii=True))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    options = parser.parse_args()
    audit = Audit()

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    audit.check("metadata", "claim", manifest["claim_id"] == CLAIM, manifest["claim_id"], CLAIM)
    audit.check("metadata", "result", manifest["result_id"] == RESULT_ID, manifest["result_id"], RESULT_ID)
    audit.check("metadata", "ledger", manifest["result_ledger_id"] == LEDGER_ID, manifest["result_ledger_id"], LEDGER_ID)

    a1 = json.loads((REPO / manifest["authorities"]["A1"]).read_text(encoding="utf-8"))
    p = a1["parameters"]
    z0 = np.asarray(p["z0"], dtype=float)
    projector = np.outer(z0, z0) / float(z0 @ z0)
    mass = np.diag(np.asarray(p["family_masses"], dtype=float)) + float(p["k_lock"]) * (np.eye(3) - projector)
    mass_oracle = np.asarray([[0.10, -0.05, -0.05], [-0.05, 0.13, -0.05], [-0.05, -0.05, 0.17]])
    audit.check("production", "mass entries", np.allclose(mass, mass_oracle, rtol=0.0, atol=2.0e-16), mass, mass_oracle)
    audit.check("production", "mass positive", float(np.min(np.linalg.eigvalsh(mass))) > 0.0, np.linalg.eigvalsh(mass), ">0")

    length = float(p["Lx"])
    volume = float(p["Lx"]) * float(p["Ly"]) * float(p["Lz"])
    lower_wave = 2.0 * math.pi / length

    def mode_covariance(wave_number: float) -> np.ndarray:
        scalar = float(p["r"]) + float(p["Z"]) * wave_number**2 + float(p["Y"]) * wave_number**4
        symbol = scalar * np.eye(3) + mass
        return np.linalg.inv(symbol)

    c1 = mode_covariance(lower_wave)
    c2 = mode_covariance(2.0 * lower_wave)
    audit.check("production", "C(k) positive", float(np.min(np.linalg.eigvalsh(c1))) > 0.0, np.linalg.eigvalsh(c1), ">0")
    audit.check("production", "C(2k) positive", float(np.min(np.linalg.eigvalsh(c2))) > 0.0, np.linalg.eigvalsh(c2), ">0")
    gamma2 = np.block([[c2, np.zeros((3, 3))], [np.zeros((3, 3)), c2]])
    eigenvalues, eigenvectors = np.linalg.eigh(gamma2)
    root2 = (eigenvectors * np.sqrt(eigenvalues)) @ eigenvectors.T
    audit.check("production", "six-real square root", np.allclose(root2 @ root2.T, gamma2, rtol=2.0e-14, atol=2.0e-14), root2 @ root2.T, gamma2)

    # Independent cosine/sine coefficient construction for q=2k.
    q = 2.0 * lower_wave
    theta = 0.371
    phi_c = math.sqrt(2.0 / volume) * math.cos(theta)
    phi_s = math.sqrt(2.0 / volume) * math.sin(theta)
    sx = np.block([phi_c * root2, phi_s * root2])
    sv = np.block([-q * phi_s * root2, q * phi_c * root2])
    field_covariance = sx @ sx.T
    current_covariance = sv @ sv.T
    cross = sx @ sv.T
    audit.check("synthesis", "point field covariance", np.allclose(field_covariance, 2.0 * gamma2 / volume, rtol=2.0e-14, atol=2.0e-14), field_covariance, 2.0 * gamma2 / volume)
    audit.check("synthesis", "point current covariance", np.allclose(current_covariance, 2.0 * q**2 * gamma2 / volume, rtol=2.0e-14, atol=2.0e-14), current_covariance, 2.0 * q**2 * gamma2 / volume)
    audit.check("synthesis", "point cross zero", float(np.max(np.abs(cross))) < 2.0e-18, float(np.max(np.abs(cross))), 0.0)

    coefficient_field = np.block([[root2, np.zeros((6, 6))], [np.zeros((6, 6)), root2]])
    coefficient_current = q * np.block([[np.zeros((6, 6)), root2], [-root2, np.zeros((6, 6))]])
    coefficient_cross = coefficient_field @ coefficient_current.T
    coefficient_oracle = q * np.block([[np.zeros((6, 6)), -gamma2], [gamma2, np.zeros((6, 6))]])
    audit.check("synthesis", "coefficient cross exact numerical", np.allclose(coefficient_cross, coefficient_oracle, rtol=2.0e-14, atol=2.0e-14), coefficient_cross, coefficient_oracle)
    audit.check("synthesis", "coefficient cross skew", np.allclose(coefficient_cross.T, -coefficient_cross, rtol=2.0e-14, atol=2.0e-14), coefficient_cross.T + coefficient_cross, 0.0)
    audit.check("synthesis", "coefficient cross nonzero", float(np.linalg.norm(coefficient_cross)) > 0.0, float(np.linalg.norm(coefficient_cross)), ">0")

    theta_x, theta_y = 0.83, -0.29
    sx_xy = np.block([
        math.sqrt(2.0 / volume) * math.cos(theta_x) * root2,
        math.sqrt(2.0 / volume) * math.sin(theta_x) * root2,
    ])
    sv_xy = np.block([
        -q * math.sqrt(2.0 / volume) * math.sin(theta_y) * root2,
        q * math.sqrt(2.0 / volume) * math.cos(theta_y) * root2,
    ])
    kernel_xy = sx_xy @ sv_xy.T
    kernel_oracle = 2.0 * q * math.sin(theta_x - theta_y) * gamma2 / volume
    audit.check("synthesis", "two-point kernel", np.allclose(kernel_xy, kernel_oracle, rtol=3.0e-14, atol=3.0e-14), kernel_xy, kernel_oracle)
    audit.check("synthesis", "final pair prefactor is four lower waves", abs(2.0 * q - 4.0 * lower_wave) < 1.0e-15, 2.0 * q, 4.0 * lower_wave)

    # Direct polynomial Gaussian calculation in an independent rotated basis.
    g, h, w, v, scale, wave_symbol = sp.symbols("g h w v sigma q", real=True)
    angle_c = sp.Rational(3, 5)
    angle_s = sp.Rational(4, 5)
    field = w + scale * (angle_c * g + angle_s * h)
    current = v + wave_symbol * scale * (-angle_s * g + angle_c * h)
    gram = 1 + field**2

    def expectation(expr: sp.Expr) -> sp.Expr:
        result = sp.expand(expr)
        for variable in (g, h):
            poly = sp.Poly(result, variable)
            result = sp.expand(sum(
                coefficient * (sp.factorial2(power - 1) if power and power % 2 == 0 else 1 if power == 0 else 0)
                for (power,), coefficient in poly.terms()
            ))
        return sp.factor(result)

    raw = expectation(gram * current**2 - wave_symbol**2 * scale**2 * gram)
    predictable = expectation(v**2 * gram)
    audit.check("last-endpoint", "independent Stein checksum", sp.simplify(raw - predictable) == 0, raw, predictable)
    coefficient = sp.factor(predictable / v**2)
    audit.check("last-endpoint", "predictable coefficient positive polynomial", all(item > 0 for item in sp.Poly(coefficient, w, scale).coeffs()), coefficient, "positive coefficients")
    audit.check("last-endpoint", "zero predictable current cancels", sp.simplify(raw.subs(v, 0)) == 0, sp.simplify(raw.subs(v, 0)), 0)

    # A nonlocal spatial projection sees the off-diagonal kernel even though
    # the pointwise cross synthesis vanishes.
    angle = sp.symbols("x", real=True)
    aa, bb = sp.symbols("aa bb", real=True)
    field_circle = aa * sp.cos(angle) + bb * sp.sin(angle)
    current_circle = -aa * sp.sin(angle) + bb * sp.cos(angle)
    derivative_basis = (-sp.sin(angle), sp.cos(angle))

    def mean_circle(expr: sp.Expr) -> sp.Expr:
        return sp.simplify(sp.integrate(sp.expand_trig(expr), (angle, 0, 2 * sp.pi)) / (2 * sp.pi))

    def p2_norm(expr: sp.Expr) -> sp.Expr:
        cosine_coefficient = sp.simplify(2 * mean_circle(expr * sp.cos(2 * angle)))
        sine_coefficient = sp.simplify(2 * mean_circle(expr * sp.sin(2 * angle)))
        return sp.factor((cosine_coefficient**2 + sine_coefficient**2) / 2)

    p0_current = mean_circle(field_circle * current_circle) ** 2
    p0_trace = sum(mean_circle(field_circle * basis) ** 2 for basis in derivative_basis)
    d0 = sp.factor(p0_current - p0_trace)
    d2 = sp.factor(
        p2_norm(field_circle * current_circle)
        - sum(p2_norm(field_circle * basis) for basis in derivative_basis)
    )
    def standard_polynomial_expectation(expr: sp.Expr, variables: tuple[sp.Symbol, ...]) -> sp.Expr:
        result = sp.expand(expr)
        for variable in variables:
            polynomial = sp.Poly(result, variable)
            result = sp.expand(sum(
                coefficient * (sp.factorial2(power - 1) if power and power % 2 == 0 else 1 if power == 0 else 0)
                for (power,), coefficient in polynomial.terms()
            ))
        return sp.factor(result)

    d0_expectation = standard_polynomial_expectation(d0, (aa, bb))
    d2_expectation = standard_polynomial_expectation(d2, (aa, bb))
    audit.check("projection-boundary", "zero-output packet exact", sp.simplify(d0 + (aa**2 + bb**2) / 4) == 0, d0, -(aa**2 + bb**2) / 4)
    audit.check("projection-boundary", "two-output packet exact", sp.simplify(d2 - ((aa**2 + bb**2) ** 2 / 8 - (aa**2 + bb**2) / 4)) == 0, d2, (aa**2 + bb**2) ** 2 / 8 - (aa**2 + bb**2) / 4)
    audit.check("projection-boundary", "projected expectations have opposite signs", d0_expectation == -sp.Rational(1, 2) and d2_expectation == sp.Rational(1, 2), [d0_expectation, d2_expectation], [-sp.Rational(1, 2), sp.Rational(1, 2)])

    # Exact earlier-root future-feedback sign fixture.  This is a method
    # boundary, not a full-production action counterexample.
    feedback_amplitude = sp.Integer(1)
    cosine_fixture = sine_fixture = 1 / sp.sqrt(2)
    field_row = sp.Matrix([(1 + feedback_amplitude) * cosine_fixture, sine_fixture])
    current_row = sp.Matrix([-(1 + feedback_amplitude) * sine_fixture, cosine_fixture])
    variance_feedback = sp.simplify((field_row.T * field_row)[0])
    current_variance_feedback = sp.simplify((current_row.T * current_row)[0])
    cross_feedback = sp.simplify((field_row.T * current_row)[0])
    gaussian_weight = sp.Integer(1)
    expected_b_second = sp.simplify(
        -2 * gaussian_weight
        / (1 + 2 * gaussian_weight * variance_feedback) ** sp.Rational(3, 2)
    )
    unhalved_feedback_owner = sp.simplify(cross_feedback**2 * expected_b_second)
    audit.check("future-feedback-boundary", "feedback covariance", variance_feedback == current_variance_feedback == sp.Rational(5, 2) and cross_feedback == -sp.Rational(3, 2), [variance_feedback, current_variance_feedback, cross_feedback], [sp.Rational(5, 2), sp.Rational(5, 2), -sp.Rational(3, 2)])
    audit.check("future-feedback-boundary", "Gaussian B second derivative", expected_b_second == -1 / (3 * sp.sqrt(6)), expected_b_second, -1 / (3 * sp.sqrt(6)))
    audit.check("future-feedback-boundary", "unhalved owner strictly negative", sp.simplify(unhalved_feedback_owner + sp.sqrt(6) / 8) == 0 and unhalved_feedback_owner < 0, unhalved_feedback_owner, -sp.sqrt(6) / 8)

    # Exact scope falsifier: absolute positivity does not sign a relative secant.
    previous_atom = sp.Rational(1, 2) * 2**2
    final_atom = sp.Rational(1, 2) * 1**2
    secant = final_atom - previous_atom
    audit.check("scope", "two positive atoms can have negative secant", previous_atom > 0 and final_atom > 0 and secant < 0, [previous_atom, final_atom, secant], "positive, positive, negative")
    audit.check("scope", "relative secant remains false", manifest["scope"]["relative_final_endpoint_secant_signed"] is False, manifest["scope"]["relative_final_endpoint_secant_signed"], False)
    audit.check("scope", "earlier future feedback remains open", manifest["scope"]["earlier_root_future_feedback_connection_closed"] is False, manifest["scope"]["earlier_root_future_feedback_connection_closed"], False)
    audit.check("scope", "T050 remains open", manifest["scope"]["t050_closed"] is False, manifest["scope"]["t050_closed"], False)

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
            "wave": lower_wave,
            "final_wave": q,
            "C_k_eigenvalues": np.linalg.eigvalsh(c1),
            "C_2k_eigenvalues": np.linalg.eigvalsh(c2),
            "point_cross_max_abs": float(np.max(np.abs(cross))),
            "coefficient_cross_frobenius": float(np.linalg.norm(coefficient_cross)),
            "relative_secant_counterfixture": {
                "previous_atom": previous_atom,
                "final_atom": final_atom,
                "secant": secant,
            },
            "projected_output_expectations": {"zero": d0_expectation, "two": d2_expectation},
            "earlier_future_feedback_unhalved_owner": unhalved_feedback_owner,
        },
        "assertions_total": len(audit.rows),
        "assertions_passed": sum(row["status"] == "PASS" for row in audit.rows),
        "assertions": audit.rows,
    }
    atomic_json(options.output, payload)
    print(f"{RESULT_ID} independent: PASS ({len(audit.rows)}/{len(audit.rows)})")
    print(f"artifact: {options.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

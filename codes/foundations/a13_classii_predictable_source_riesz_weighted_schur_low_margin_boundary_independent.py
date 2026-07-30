#!/usr/bin/env python3
"""Non-importing independent audit for the scoped R-127 A13 checkpoint."""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-30"
__version_issued__ = "2026-07-30"

import argparse
from fractions import Fraction
import json
import math
import os
from pathlib import Path
import re
import tempfile
from typing import Any


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-PREDICTABLE-SOURCE-RIESZ-WEIGHTED-SCHUR-LOW-MARGIN-BOUNDARY"
SCHEMA = "tect/a13-predictable-source-riesz-weighted-schur-low-margin-boundary-independent/1.0"
CLAIM_DIR = REPO / "claims" / CLAIM
DEFAULT_OUTPUT = CLAIM_DIR / "runs/2026-07-30-independent-predictable-source-riesz-weighted-schur-low-margin-boundary/result.json"
R120_OUTPUT = CLAIM_DIR / "runs/2026-07-29-primary-covariance-horizontal-synthesis-stationary-low-chaos-cartan-hessian/result.json"
R093_OUTPUT = CLAIM_DIR / "runs/2026-07-27-primary-augmented-perspective-gibbs-gap-information-boundary/result.json"
R126_OUTPUT = CLAIM_DIR / "runs/2026-07-30-primary-total-symbol-euler-low-injected-loewner-boundary/result.json"


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True, default=str)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(self, group: str, name: str, condition: bool, actual: Any, expected: Any) -> None:
        self.rows.append(
            {
                "group": group,
                "name": name,
                "status": "PASS" if bool(condition) else "FAIL",
                "actual": str(actual) if isinstance(actual, Fraction) else actual,
                "expected": str(expected) if isinstance(expected, Fraction) else expected,
            }
        )

    def finish(self, diagnostics: dict[str, Any]) -> dict[str, Any]:
        passed = sum(row["status"] == "PASS" for row in self.rows)
        return {
            "schema": SCHEMA,
            "package_version": __version__,
            "claim_id": CLAIM,
            "result_id": RESULT_ID,
            "status": "PASS" if passed == len(self.rows) else "FAIL",
            "assertions_total": len(self.rows),
            "assertions_passed": passed,
            "assertions_failed": len(self.rows) - passed,
            "assertions": self.rows,
            "diagnostics": diagnostics,
            "independence": {
                "imports_primary": False,
                "uses_sympy": False,
                "route": "fractions, direct finite-law sums, elementary matrix algebra, and finite differences",
            },
            "scope": {
                "independently_audits_predictable_projection_order": True,
                "independently_audits_weighted_schur_domains_and_constants": True,
                "independently_audits_augmented_low_margin_fixtures": True,
                "independently_audits_gauge_and_curvature_fixtures": True,
                "production_bound_proved": False,
                "sector_a_closed": False,
            },
        }


def source_checks(audit: Audit) -> dict[str, Any]:
    xis = (-1, 1)
    expectation = lambda values: Fraction(sum(values), len(values))
    g1 = expectation(xis)
    legal = tuple(g1 + xi for xi in xis)
    unrestricted = tuple(2 * xi for xi in xis)
    source_norm = g1 * g1 + expectation(tuple(xi * xi for xi in xis))
    covariance_energy = expectation(tuple(xi * (2 * xi) for xi in xis))
    audit.check("source", "past_projection", g1 == 0, g1, 0)
    audit.check("source", "legal_riesz_atoms", legal == xis, legal, xis)
    audit.check("source", "unrestricted_factor_two", unrestricted == tuple(2 * value for value in legal), unrestricted, tuple(2 * value for value in legal))
    audit.check("source", "quotient_norm_squared", source_norm == 1, source_norm, 1)
    audit.check("source", "covariance_upper_bound", source_norm <= covariance_energy, [source_norm, covariance_energy], "ordered")

    r093 = json.loads(R093_OUTPUT.read_text(encoding="utf-8"))
    q_inverse_rows = [row for row in r093["assertions"] if row["name"] == "q_inverse"]
    audit.check("source", "r093_q_inverse_unique", len(q_inverse_rows) == 1, len(q_inverse_rows), 1)
    q_inverse = Fraction(q_inverse_rows[0]["actual"])
    production_q = 1 / q_inverse
    source_cost = 1 / (2 * production_q)
    adverse_cost = 1 / (4 * source_cost)
    audit.check("source", "derived_source_cost", source_cost == Fraction(9, 20), source_cost, Fraction(9, 20))
    audit.check("source", "derived_adverse_cost", adverse_cost == Fraction(5, 9), adverse_cost, Fraction(5, 9))
    for h, g in ((Fraction(2, 3), Fraction(-4, 5)), (Fraction(-7, 9), Fraction(5, 6))):
        left = h * g + source_cost * h * h
        right = source_cost * (h + g / (2 * source_cost)) ** 2 - adverse_cost * g * g
        audit.check("source", f"completion_{h}_{g}", left == right, left, right)

    r120 = json.loads(R120_OUTPUT.read_text(encoding="utf-8"))
    cm_squared = float(r120["diagnostics"]["horizontal_synthesis"]["c_cm"])
    cm_norm = math.sqrt(cm_squared)
    audit.check("source", "upstream_cm_squared", 9.22 < cm_squared < 9.24, cm_squared, "between 9.22 and 9.24")
    audit.check("source", "upstream_cm_norm", 3.03 < cm_norm < 3.04, cm_norm, "between 3.03 and 3.04")
    return {
        "legal_riesz": legal,
        "unrestricted": unrestricted,
        "source_norm_squared": float(source_norm),
        "covariance_energy": float(covariance_energy),
        "r120_cm_norm": cm_norm,
    }


def schur_checks(audit: Audit) -> dict[str, Any]:
    cases = (
        (Fraction(1, 8), Fraction(1, 16)),
        (Fraction(1, 4), Fraction(3, 10)),
        (Fraction(1, 2), Fraction(1, 4)),
    )
    row_maxima = []
    for d, q in cases:
        audit.check("schur", f"domain_d_{d}", 0 < d <= Fraction(1, 2), d, "0 < d <= 1/2")
        audit.check("schur", f"domain_q_{q}", q * q < 1 - d, q * q, f"< {1 - d}")
        rows = [sum((d**j) * ((1 - d) ** (p - j)) for j in range(p + 1)) for p in range(20)]
        row_maxima.append(max(rows))
        audit.check("schur", f"exact_row_bound_d_{d}", max(rows) <= 1, max(rows), "<= 1")
        recurrence_ok = all(rows[p + 1] == (1 - d) ** (p + 1) + d * rows[p] for p in range(len(rows) - 1))
        audit.check("schur", f"exact_row_recurrence_d_{d}", recurrence_ok, recurrence_ok, True)
        t_weight = q / (1 - d)
        beta = 1 / (1 - q * t_weight)
        for j in (0, 1, 5):
            exact_column = d**j / (1 - q * t_weight)
            audit.check("schur", f"exact_column_bound_d_{d}_j_{j}", exact_column <= beta, exact_column, beta)

    mixed_factor = math.sqrt(8.0 / 7.0)
    mixed_coefficient = mixed_factor / 4.0
    mixed_hs = 2.0 / math.sqrt(45.0)
    far_factor = math.sqrt(224.0 / 223.0)
    far_coefficient = far_factor / 16.0
    far_hs = 8.0 / math.sqrt(16065.0)
    audit.check("schur", "mixed_strict_improvement", mixed_coefficient < mixed_hs, mixed_coefficient, mixed_hs)
    audit.check("schur", "far_strict_improvement", far_coefficient < far_hs, far_coefficient, far_hs)

    r126 = json.loads(R126_OUTPUT.read_text(encoding="utf-8"))
    budget_text = r126["diagnostics"]["loewner_shells"]["production_operator_budget"]
    budget_match = re.fullmatch(r"sqrt\((\d+)\)/(\d+)", budget_text)
    if budget_match is None:
        raise ValueError(f"unexpected pinned R-126 operator budget: {budget_text!r}")
    budget = math.sqrt(int(budget_match.group(1))) / int(budget_match.group(2))
    new_threshold = math.sqrt(14.0) * budget
    old_threshold = math.sqrt(45.0) * budget / 2.0
    improvement = 100.0 * (new_threshold / old_threshold - 1.0)
    audit.check("schur", "acceptance_improves", new_threshold > old_threshold, new_threshold, old_threshold)
    audit.check("schur", "improvement_percent", 11.5 < improvement < 11.6, improvement, "between 11.5 and 11.6")
    for j0, j, collar, k in ((0, 0, 1, 0), (3, 2, 1, 4), (5, 7, 3, 2)):
        root = j0 + j
        shell = root + collar + k
        mixed_left = Fraction(2) ** (root - 2 * shell)
        mixed_right = Fraction(2) ** (-j0 - 2 * collar) * Fraction(1, 2) ** j * Fraction(1, 4) ** k
        far_left = Fraction(2) ** (root - 4 * shell)
        far_right = Fraction(2) ** (-3 * j0 - 4 * collar) * Fraction(1, 8) ** j * Fraction(1, 16) ** k
        audit.check("schur", f"mixed_relabel_{j0}_{j}_{collar}_{k}", mixed_left == mixed_right, mixed_left, mixed_right)
        audit.check("schur", f"far_relabel_{j0}_{j}_{collar}_{k}", far_left == far_right, far_left, far_right)
    return {
        "row_maxima": row_maxima,
        "mixed_coefficient": mixed_coefficient,
        "mixed_hs_coefficient": mixed_hs,
        "far_coefficient": far_coefficient,
        "far_hs_coefficient": far_hs,
        "budget": budget,
        "new_threshold": new_threshold,
        "old_threshold": old_threshold,
        "improvement_percent": improvement,
    }


def determinant3(matrix: list[list[float]]) -> float:
    return (
        matrix[0][0] * (matrix[1][1] * matrix[2][2] - matrix[1][2] * matrix[2][1])
        - matrix[0][1] * (matrix[1][0] * matrix[2][2] - matrix[1][2] * matrix[2][0])
        + matrix[0][2] * (matrix[1][0] * matrix[2][1] - matrix[1][1] * matrix[2][0])
    )


def loewner_checks(audit: Audit) -> dict[str, Any]:
    eta, zeta, r, s, a = 2 / 5, 3 / 7, 1 / 9, 1 / 10, 1 / 8
    b, c, d_low = 1 / 11, -1 / 13, 5 / 6
    matrix = [[2 * eta - r, -a / 2, -b], [-a / 2, 2 * zeta - s, -c], [-b, -c, d_low]]
    determinant = determinant3(matrix)
    m00 = matrix[0][0]
    minor2 = matrix[0][0] * matrix[1][1] - matrix[0][1] ** 2
    audit.check("loewner", "positive_augmented_fixture", m00 > 0 and minor2 > 0 and determinant > 0, [m00, minor2, determinant], "all positive")
    audit.check("loewner", "zero_low_noncoupling_failure", -(1 / 3) ** 2 < 0, -(1 / 3) ** 2, "negative")

    eta_s, zeta_s = 4 / 9, 9 / 16
    root_eta, root_zeta = math.sqrt(eta_s), math.sqrt(zeta_s)
    a_sat = 4 * root_eta * root_zeta
    sat_det = 4 * eta_s * zeta_s - a_sat * a_sat / 4
    audit.check("loewner", "saturated_determinant", abs(sat_det) < 1e-15, sat_det, 0)
    b_cancel, c_cancel = root_eta, -root_zeta
    compatibility = b_cancel * root_zeta + c_cancel * root_eta
    audit.check("loewner", "saturated_compatibility", abs(compatibility) < 1e-15, compatibility, 0)
    incompatible_matrix = [[8 / 9, -1.0, -1.0], [-1.0, 9 / 8, 0.0], [-1.0, 0.0, 1.0]]
    incompatible_determinant = determinant3(incompatible_matrix)
    audit.check("loewner", "saturated_generic_incompatibility", abs(incompatible_determinant + 9 / 8) < 1e-15, incompatible_determinant, -9 / 8)

    theta = 1 / 4
    a_strict = (1 - theta) * a_sat
    lambda_min = eta_s + zeta_s - math.sqrt((eta_s - zeta_s) ** 2 + a_strict * a_strict / 4)
    lambda_min_negative = eta_s + zeta_s - math.sqrt(
        (eta_s - zeta_s) ** 2 + (-a_strict) * (-a_strict) / 4
    )
    lower = 2 * eta_s * zeta_s * (2 * theta - theta * theta) / (eta_s + zeta_s)
    audit.check(
        "loewner",
        "strict_margin_and_sign_symmetry",
        lambda_min + 1e-15 >= lower and abs(lambda_min_negative - lambda_min) < 1e-15,
        [lambda_min, lambda_min_negative],
        [f">= {lower}", "equal under a -> -a"],
    )

    eta_a, zeta_a, a_a, bb, cc = 0.7, 0.9, 0.4, -0.3, 0.2
    det = 4 * eta_a * zeta_a - a_a * a_a / 4
    direct = (2 * zeta_a * bb * bb + a_a * bb * cc + 2 * eta_a * cc * cc) / det
    inverse00, inverse01, inverse11 = 2 * zeta_a / det, (a_a / 2) / det, 2 * eta_a / det
    expanded = inverse00 * bb * bb + 2 * inverse01 * bb * cc + inverse11 * cc * cc
    audit.check("loewner", "affine_cost", abs(direct - expanded) < 1e-15, direct, expanded)
    return {
        "augmented_determinant": determinant,
        "saturated_determinant": sat_det,
        "strict_lambda_min": lambda_min,
        "strict_lower_bound": lower,
        "affine_cost": direct,
    }


def logsumexp_pair(values: tuple[float, float]) -> float:
    largest = max(values)
    return largest + math.log((math.exp(values[0] - largest) + math.exp(values[1] - largest)) / 2.0)


def boundary_checks(audit: Audit) -> dict[str, Any]:
    t2 = math.tanh(1.0) ** 2
    reverse_positive = t2 * (0.5 + 0.5**2 / 2)
    reverse_negative = t2 * (-0.5 + (-0.5) ** 2 / 2)
    audit.check("boundary", "reverse_positive", reverse_positive > 0, reverse_positive, "positive")
    audit.check("boundary", "reverse_negative", reverse_negative < 0, reverse_negative, "negative")
    forward = t2 / 2
    audit.check("boundary", "endpoint_checksum_positive", abs(forward + reverse_positive - t2 * (1.5**2) / 2) < 1e-15, forward + reverse_positive, t2 * (1.5**2) / 2)
    audit.check("boundary", "endpoint_checksum_negative", abs(forward + reverse_negative - t2 * (0.5**2) / 2) < 1e-15, forward + reverse_negative, t2 * (0.5**2) / 2)

    q = 10 / 9
    energies = (0.3, -0.8)
    constant = 1.7
    base = -logsumexp_pair(tuple(-q * value for value in energies)) / q
    shifted = -logsumexp_pair(tuple(-q * (value + constant) for value in energies)) / q
    probabilities = [math.exp(-q * value) for value in energies]
    probabilities = [value / sum(probabilities) for value in probabilities]
    shifted_probabilities = [math.exp(-q * (value + constant)) for value in energies]
    shifted_probabilities = [value / sum(shifted_probabilities) for value in shifted_probabilities]
    audit.check("gibbs", "free_energy_shift", abs((shifted - base) - constant) < 1e-14, shifted - base, constant)
    audit.check("gibbs", "normalized_law_invariant", max(abs(a - b) for a, b in zip(probabilities, shifted_probabilities)) < 1e-15, probabilities, shifted_probabilities)

    b0, a0, delta_tau = 2 / 5, 3 / 4, 1 / 7
    xis, residuals = (-1.0, 1.0), (1 / 3, -2 / 5)

    def psi(u: float) -> float:
        potentials = []
        for xi, residual in zip(xis, residuals):
            y = b0 + a0 * xi + u * residual
            tau = a0 * a0 + u * delta_tau
            potentials.append((y * y - tau) / 2)
        return logsumexp_pair(tuple(-q * value for value in potentials))

    base_potentials = [((b0 + a0 * xi) ** 2 - a0 * a0) / 2 for xi in xis]
    raw_weights = [math.exp(-q * value) for value in base_potentials]
    mu = [value / sum(raw_weights) for value in raw_weights]
    pdot = [(b0 + a0 * xi) * residual - delta_tau / 2 for xi, residual in zip(xis, residuals)]
    mean = sum(weight * value for weight, value in zip(mu, pdot))
    variance = sum(weight * (value - mean) ** 2 for weight, value in zip(mu, pdot))
    residual_square = sum(weight * residual * residual for weight, residual in zip(mu, residuals))
    formula = q * q * variance - q * residual_square
    step = 1e-3
    fixture_rows = []
    for center in (-0.3, 0.0, 0.4):
        base_potentials_center = []
        pdot_center = []
        for xi, residual in zip(xis, residuals):
            y = b0 + a0 * xi + center * residual
            tau = a0 * a0 + center * delta_tau
            base_potentials_center.append((y * y - tau) / 2)
            pdot_center.append(y * residual - delta_tau / 2)
        weights_center = [math.exp(-q * value) for value in base_potentials_center]
        mu_center = [value / sum(weights_center) for value in weights_center]
        mean_center = sum(weight * value for weight, value in zip(mu_center, pdot_center))
        variance_center = sum(weight * (value - mean_center) ** 2 for weight, value in zip(mu_center, pdot_center))
        residual_square_center = sum(weight * residual * residual for weight, residual in zip(mu_center, residuals))
        formula_center = q * q * variance_center - q * residual_square_center
        finite_difference = (
            -psi(center + 2 * step)
            + 16 * psi(center + step)
            - 30 * psi(center)
            + 16 * psi(center - step)
            - psi(center - 2 * step)
        ) / (12 * step * step)
        audit.check("interpolation", f"curvature_finite_difference_{center}", abs(finite_difference - formula_center) < 3e-8, finite_difference, formula_center)
        fixture_rows.append({"center": center, "formula": formula_center, "finite_difference": finite_difference})
    linear_anchor = -q * mean
    audit.check("interpolation", "linear_anchor_nonzero", abs(linear_anchor) > 1e-6, linear_anchor, "nonzero")
    return {
        "reverse_positive": reverse_positive,
        "reverse_negative": reverse_negative,
        "free_energy_shift": shifted - base,
        "curvature_at_zero": formula,
        "curvature_fixtures": fixture_rows,
        "linear_anchor": linear_anchor,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()
    audit = Audit()
    diagnostics = {
        "source": source_checks(audit),
        "weighted_schur": schur_checks(audit),
        "augmented_loewner": loewner_checks(audit),
        "boundaries": boundary_checks(audit),
    }
    payload = audit.finish(diagnostics)
    atomic_json(arguments.output, payload)
    print(f"R-127 independent {payload['status']} {payload['assertions_passed']}/{payload['assertions_total']}")
    if payload["status"] != "PASS":
        for row in payload["assertions"]:
            if row["status"] == "FAIL":
                print(f"FAIL {row['group']}::{row['name']} actual={row['actual']!r} expected={row['expected']!r}")
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

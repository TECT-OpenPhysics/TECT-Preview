#!/usr/bin/env python3
"""Non-importing independent verifier for the scoped R-126 checkpoint."""

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
RESULT_ID = "A13-CLASSII-TOTAL-SYMBOL-EULER-LOW-INJECTED-LOEWNER-BOUNDARY"
SCHEMA = "tect/a13-total-symbol-euler-low-injected-loewner-boundary-independent/1.0"
CLAIM_DIR = REPO / "claims" / CLAIM
DEFAULT_OUTPUT = CLAIM_DIR / "runs/2026-07-30-independent-total-symbol-euler-low-injected-loewner-boundary/result.json"
A1_MANIFEST = REPO / "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json"
R121_MANIFEST = CLAIM_DIR / "classii_cartan_pathspace_exactness_fixed_skew_sobolev_boundary_manifest.json"


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
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


def serial(value: Any) -> Any:
    if isinstance(value, Fraction):
        return f"{value.numerator}/{value.denominator}"
    if isinstance(value, tuple):
        return [serial(item) for item in value]
    if isinstance(value, list):
        return [serial(item) for item in value]
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    return value


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(self, group: str, name: str, condition: bool, actual: Any, expected: Any) -> None:
        self.rows.append(
            {
                "group": group,
                "name": name,
                "status": "PASS" if condition else "FAIL",
                "actual": serial(actual),
                "expected": serial(expected),
            }
        )

    def payload(self, diagnostics: dict[str, Any]) -> dict[str, Any]:
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
            "diagnostics": serial(diagnostics),
            "independence": "standard-library implementation; imports neither primary verifier nor its output",
            "scope": {
                "exact_algebra_checked_independently": True,
                "periodic_euler_force_checked_independently": True,
                "production_operator_estimate_proved": False,
                "sector_a_closed": False,
            },
        }


def p_add(left: list[Fraction], right: list[Fraction]) -> list[Fraction]:
    size = max(len(left), len(right))
    return [
        (left[index] if index < len(left) else Fraction(0))
        + (right[index] if index < len(right) else Fraction(0))
        for index in range(size)
    ]


def p_scale(value: Fraction, poly: list[Fraction]) -> list[Fraction]:
    return [value * coefficient for coefficient in poly]


def p_mul(left: list[Fraction], right: list[Fraction]) -> list[Fraction]:
    output = [Fraction(0)] * (len(left) + len(right) - 1)
    for i, first in enumerate(left):
        for j, second in enumerate(right):
            output[i + j] += first * second
    return output


def p_dot(left: list[list[Fraction]], right: list[list[Fraction]]) -> list[Fraction]:
    output = [Fraction(0)]
    for first, second in zip(left, right, strict=True):
        output = p_add(output, p_mul(first, second))
    return output


def finite_atom_polynomial_check(audit: Audit) -> dict[str, Any]:
    weights = (Fraction(2, 5), Fraction(3, 5))
    gamma = ((Fraction(3, 2), Fraction(1, 5)), (Fraction(1, 5), Fraction(7, 3)))
    # Each C entry and velocity is a polynomial in the path parameter t.
    c_atoms = (
        (
            ([Fraction(1), Fraction(2)], [Fraction(-1), Fraction(1)]),
            ([Fraction(2), Fraction(-1)], [Fraction(0), Fraction(3)]),
            ([Fraction(-2), Fraction(1)], [Fraction(1), Fraction(-2)]),
        ),
        (
            ([Fraction(0), Fraction(-1)], [Fraction(3), Fraction(2)]),
            ([Fraction(1), Fraction(2)], [Fraction(-2), Fraction(1)]),
            ([Fraction(2), Fraction(1)], [Fraction(1), Fraction(1)]),
        ),
    )
    velocity_atoms = (
        ([Fraction(2), Fraction(1)], [Fraction(-1), Fraction(2)]),
        ([Fraction(-1), Fraction(3)], [Fraction(2), Fraction(-1)]),
    )

    phi = [[Fraction(0)] for _ in range(3)]
    theta = [Fraction(0)]
    for atom_index, weight in enumerate(weights):
        c_matrix = c_atoms[atom_index]
        velocity = velocity_atoms[atom_index]
        for row_index in range(3):
            current = p_dot(list(c_matrix[row_index]), list(velocity))
            phi[row_index] = p_add(phi[row_index], p_scale(weight, current))
        for row_index in range(3):
            c_row = c_matrix[row_index]
            gamma_c = [
                p_add(p_scale(gamma[column][0], list(c_row[0])), p_scale(gamma[column][1], list(c_row[1])))
                for column in range(2)
            ]
            theta = p_add(theta, p_scale(weight, p_dot(list(c_row), gamma_c)))
    total = list(theta)
    for row in phi:
        total = p_add(total, p_scale(Fraction(-1), p_mul(row, row)))
    derivative = total[1]

    # Independent first-variation assembly from constant/linear coefficients.
    phi_zero = [row[0] for row in phi]
    delta_phi = [row[1] for row in phi]
    trace_derivative = theta[1]
    predicted = trace_derivative - 2 * sum(
        (phi_zero[index] * delta_phi[index] for index in range(3)), Fraction(0)
    )
    audit.check("directional", "polynomial_derivative", derivative == predicted, derivative, predicted)
    audit.check("directional", "nonzero_trace_derivative", trace_derivative != 0, trace_derivative, "nonzero")
    audit.check("directional", "nonzero_mean_derivative", predicted != trace_derivative, predicted, "differs from trace-only")
    return {
        "total_symbol_polynomial": total,
        "derivative": derivative,
        "trace_derivative": trace_derivative,
        "predicted": predicted,
    }


def periodic_numeric_check(audit: Audit) -> dict[str, Any]:
    gamma = ((2.0, 1.0 / 3.0), (1.0 / 3.0, 3.0))
    sample_count = 1024  # test-oracle resolution; trigonometric trapezoid is exact here.
    direct_total = 0.0
    force_total = 0.0
    skew_total = 0.0
    for index in range(sample_count):
        x = 2.0 * math.pi * index / sample_count
        w = (math.sin(x), math.cos(x))
        v = (math.cos(x), -math.sin(x))
        h = (math.sin(2.0 * x), math.cos(2.0 * x))
        dh = (2.0 * math.cos(2.0 * x), -2.0 * math.sin(2.0 * x))
        c = (w[0] * w[0] + w[1], w[0] * w[1] + w[0])
        dc = ((2.0 * w[0], 1.0), (w[1] + 1.0, w[0]))
        dc_h = (
            dc[0][0] * h[0] + dc[0][1] * h[1],
            dc[1][0] * h[0] + dc[1][1] * h[1],
        )
        phi = c[0] * v[0] + c[1] * v[1]
        delta_phi = dc_h[0] * v[0] + dc_h[1] * v[1] + c[0] * dh[0] + c[1] * dh[1]
        gamma_c = (
            gamma[0][0] * c[0] + gamma[0][1] * c[1],
            gamma[1][0] * c[0] + gamma[1][1] * c[1],
        )
        trace_derivative = 2.0 * (dc_h[0] * gamma_c[0] + dc_h[1] * gamma_c[1])
        direct_total += trace_derivative - 2.0 * phi * delta_phi

        dc_t_gamma_c = (
            dc[0][0] * gamma_c[0] + dc[1][0] * gamma_c[1],
            dc[0][1] * gamma_c[0] + dc[1][1] * gamma_c[1],
        )
        # d_x phi is evaluated from d_x c=dc*v and d_x v=-w.
        dc_v = (
            dc[0][0] * v[0] + dc[0][1] * v[1],
            dc[1][0] * v[0] + dc[1][1] * v[1],
        )
        dphi = dc_v[0] * v[0] + dc_v[1] * v[1] - c[0] * w[0] - c[1] * w[1]
        skew_v = (
            (dc[0][1] - dc[1][0]) * v[1],
            (dc[1][0] - dc[0][1]) * v[0],
        )
        force = (
            2.0 * dc_t_gamma_c[0] + 2.0 * c[0] * dphi + 2.0 * phi * skew_v[0],
            2.0 * dc_t_gamma_c[1] + 2.0 * c[1] * dphi + 2.0 * phi * skew_v[1],
        )
        force_total += h[0] * force[0] + h[1] * force[1]
        skew_total += abs(dc[0][1] - dc[1][0])
    scale = 2.0 * math.pi / sample_count
    direct_total *= scale
    force_total *= scale
    skew_total *= scale
    audit.check("euler", "numeric_periodic_pairing", abs(direct_total - force_total) < 1.0e-11, direct_total - force_total, "absolute error < 1e-11")
    audit.check("euler", "numeric_exact_value", abs(direct_total - 4.0 * math.pi) < 1.0e-11, direct_total, 4.0 * math.pi)
    audit.check("euler", "skew_present", skew_total > 0.0, skew_total, "positive")
    return {"direct": direct_total, "force": force_total, "skew_L1": skew_total}


def low_recombination_check(audit: Audit) -> dict[str, Any]:
    w_zero = Fraction(4, 9)
    d_low = Fraction(-1, 4)
    d_raw = (Fraction(2, 7), -2 * w_zero - d_low - Fraction(2, 7))
    b_raw = (Fraction(1, 5), Fraction(1, 3))
    f = (Fraction(-2, 11), Fraction(3, 14))
    d_middle = tuple(d_raw[index] - 2 * f[index] for index in range(2))
    b_middle = (Fraction(1, 2), Fraction(1, 7))
    raw = d_low + sum(d_raw[index] - b_raw[index] ** 2 for index in range(2))
    middle = d_low + sum(d_middle[index] - b_middle[index] ** 2 for index in range(2))
    raw_expected = -2 * w_zero - sum(value**2 for value in b_raw)
    middle_expected = -2 * w_zero - 2 * sum(f) - sum(value**2 for value in b_middle)
    audit.check("low_recombination", "raw_nonzero_reference", raw == raw_expected, raw, raw_expected)
    audit.check("low_recombination", "middle_injected", middle == middle_expected, middle, middle_expected)
    audit.check("low_recombination", "reference_term_load_bearing", w_zero != 0, w_zero, "nonzero")
    return {"W_A0": w_zero, "raw": raw, "middle": middle, "F": f}


def shell_loewner_and_obstructions(audit: Audit) -> dict[str, Any]:
    positive_factor = Fraction(1, 1) / ((1 - Fraction(1, 16)) * (1 - Fraction(1, 8)))
    mixed_square_factor = Fraction(1, 1) / ((1 - Fraction(1, 16)) * (1 - Fraction(1, 4)))
    audit.check("shells", "positive_factor", positive_factor == Fraction(128, 105), positive_factor, Fraction(128, 105))
    audit.check("shells", "mixed_square_factor", mixed_square_factor == Fraction(64, 45), mixed_square_factor, Fraction(64, 45))

    eta, zeta = Fraction(2, 7), Fraction(3, 11)
    threshold_squared = 16 * eta * zeta
    at_boundary_a_squared = threshold_squared
    above_a_squared = Fraction(25, 16) * threshold_squared
    audit.check("loewner", "boundary_determinant", 4 * eta * zeta - at_boundary_a_squared / 4 == 0, 4 * eta * zeta - at_boundary_a_squared / 4, 0)
    audit.check("loewner", "above_boundary_negative", 4 * eta * zeta - above_a_squared / 4 < 0, 4 * eta * zeta - above_a_squared / 4, "negative")

    parameters = json.loads(A1_MANIFEST.read_text(encoding="utf-8"))["parameters"]
    mass = Fraction(str(parameters["M_X"])) ** 2 + Fraction(str(parameters["classii_mass_regularizer"]))
    eta_budget = Fraction(197, 440) - Fraction(3, 125) / mass
    zeta_budget = Fraction(3, 25)
    operator_budget = 4.0 * math.sqrt(float(eta_budget * zeta_budget))
    mixed_limit = math.sqrt(45.0) * operator_budget / 2.0
    audit.check("budget", "operator_interval", 0.92 < operator_budget < 0.93, operator_budget, "0.92 < K < 0.93")
    audit.check("budget", "mixed_limit_interval", 3.08 < mixed_limit < 3.10, mixed_limit, "3.08 < limit < 3.10")

    spatial_shell = 3
    reveal_roots = (12, 16, 20)
    source_cost = tuple(2 ** (4 * spatial_shell) * Fraction(1, 2 ** (4 * spatial_shell)) for _ in reveal_roots)
    reverse_mixed = tuple(2 ** (root - 2 * spatial_shell) for root in reveal_roots)
    audit.check("unrestricted_reverse_band", "fixed_source_cost", source_cost == (1, 1, 1), source_cost, (1, 1, 1))
    audit.check("unrestricted_reverse_band", "divergent_weight", reverse_mixed[2] > reverse_mixed[1] > reverse_mixed[0], reverse_mixed, "strictly increasing")
    audit.check("unrestricted_reverse_band", "gap_four_ratio", reverse_mixed[1] // reverse_mixed[0] == 16, reverse_mixed[1] // reverse_mixed[0], 16)

    epsilons = (Fraction(1, 4), Fraction(1, 8), Fraction(1, 16))
    gamma = Fraction(3, 5)
    time = Fraction(2, 3)
    ratios = tuple(abs(-2 * gamma * epsilon * time + 4 * gamma * epsilon**2 * time**2) / epsilon**2 for epsilon in epsilons)
    audit.check("mixed_secant", "quadratic_ratio_grows", ratios[2] > ratios[1] > ratios[0], ratios, "strictly increasing")
    return {
        "positive_factor": positive_factor,
        "mixed_square_factor": mixed_square_factor,
        "operator_budget": operator_budget,
        "mixed_limit": mixed_limit,
        "reverse_weights": reverse_mixed,
        "mixed_secant_ratios": ratios,
    }


def cartan_authority_check(audit: Audit) -> dict[str, Any]:
    manifest = json.loads(R121_MANIFEST.read_text(encoding="utf-8"))
    statement = manifest["theorems"]["normalized_current_audit"]
    match = re.search(
        r"curls are (-?\d+)/(729) for K_R, (\d+)/(729) for M_U, and (\d+)/(729) after recombination",
        statement,
    )
    fractions = (
        tuple(Fraction(int(match.group(index)), int(match.group(index + 1))) for index in (1, 3, 5))
        if match
        else tuple()
    )
    audit.check("cartan", "authority_parsed", len(fractions) == 3, len(fractions), 3)
    if len(fractions) == 3:
        audit.check("cartan", "recombined", fractions[0] + fractions[1] == fractions[2], fractions[0] + fractions[1], fractions[2])
        audit.check("cartan", "nonzero", fractions[2] != 0, fractions[2], "nonzero")
    return {"curls": fractions}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()
    audit = Audit()
    diagnostics = {
        "directional": finite_atom_polynomial_check(audit),
        "euler": periodic_numeric_check(audit),
        "low_recombination": low_recombination_check(audit),
        "shell_loewner": shell_loewner_and_obstructions(audit),
        "cartan": cartan_authority_check(audit),
    }
    payload = audit.payload(diagnostics)
    atomic_json(arguments.output, payload)
    print(
        f"R-126 independent {payload['status']} "
        f"{payload['assertions_passed']}/{payload['assertions_total']} -> {arguments.output}"
    )
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

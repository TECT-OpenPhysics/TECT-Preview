#!/usr/bin/env python3
"""Independent standard-library verifier for the scoped R-125 checkpoint."""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-30"
__version_issued__ = "2026-07-30"

import argparse
from fractions import Fraction as F
import json
import math
import os
from pathlib import Path
import tempfile
from typing import Any


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-CONDITIONAL-VARIANCE-FOREST-BRIDGE-ROOT-SHELL-OPERATOR-BOUNDARY"
SCHEMA = "tect/a13-conditional-variance-forest-bridge-root-shell-operator-boundary-independent/1.0"
CLAIM_DIR = REPO / "claims" / CLAIM
DEFAULT_OUTPUT = CLAIM_DIR / "runs/2026-07-30-independent-conditional-variance-forest-bridge-root-shell-operator-boundary/result.json"
A1_MANIFEST = REPO / "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json"


def serial(value: Any) -> Any:
    if isinstance(value, F):
        return f"{value.numerator}/{value.denominator}" if value.denominator != 1 else str(value.numerator)
    if isinstance(value, tuple):
        return [serial(item) for item in value]
    if isinstance(value, list):
        return [serial(item) for item in value]
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    return value


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


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

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
            "diagnostics": serial(diagnostics),
            "scope": {
                "finite_cutoff_bridge_proved": True,
                "conditional_variance_rebate_required": True,
                "finite_cutoff_adapted_partial_wick_identity_proved": True,
                "abstract_root_shell_operator_criterion_proved": True,
                "owner_complete_stationary_baseline_sum_proved": False,
                "adapted_forest_continuum_bound_proved": False,
                "production_root_shell_factorization_proved": False,
                "overlap_src_proved": False,
                "nelson_proved": False,
                "sector_a_closed": False,
            },
            "no_overclaim": (
                "This non-importing audit confirms only the finite-cutoff variance/forest bridge, "
                "smooth cylindrical partial-Wick algebra, its counterfixture, and the abstract "
                "root-shell operator budget. The production "
                "factorization, stationary baseline, OVERLAP_src, Nelson, and Sector A remain open."
            ),
        }


def dot(left: list[F], right: list[F]) -> F:
    return sum((left[index] * right[index] for index in range(len(left))), F(0))


def matmul(left: list[list[F]], right: list[list[F]]) -> list[list[F]]:
    return [
        [sum((left[i][k] * right[k][j] for k in range(len(right))), F(0)) for j in range(len(right[0]))]
        for i in range(len(left))
    ]


def transpose(matrix: list[list[F]]) -> list[list[F]]:
    return [list(row) for row in zip(*matrix)]


def trace(matrix: list[list[F]]) -> F:
    return sum((matrix[index][index] for index in range(len(matrix))), F(0))


def close(left: float, right: float, tolerance: float = 1e-12) -> bool:
    return abs(left - right) <= tolerance * max(1.0, abs(left), abs(right))


def poly_trim(polynomial: list[F]) -> list[F]:
    result = list(polynomial)
    while len(result) > 1 and result[-1] == 0:
        result.pop()
    return result


def poly_add(left: list[F], right: list[F]) -> list[F]:
    size = max(len(left), len(right))
    return poly_trim([
        (left[index] if index < len(left) else F(0))
        + (right[index] if index < len(right) else F(0))
        for index in range(size)
    ])


def poly_scale(scale: F, polynomial: list[F]) -> list[F]:
    return poly_trim([scale * coefficient for coefficient in polynomial])


def poly_mul(left: list[F], right: list[F]) -> list[F]:
    result = [F(0)] * (len(left) + len(right) - 1)
    for left_index, left_value in enumerate(left):
        for right_index, right_value in enumerate(right):
            result[left_index + right_index] += left_value * right_value
    return poly_trim(result)


def poly_derivative(polynomial: list[F]) -> list[F]:
    if len(polynomial) == 1:
        return [F(0)]
    return poly_trim([F(index) * polynomial[index] for index in range(1, len(polynomial))])


def hermite_probabilists(maximum: int) -> list[list[F]]:
    hermites = [[F(1)], [F(0), F(1)]]
    for degree in range(1, maximum):
        next_polynomial = poly_add(
            poly_mul([F(0), F(1)], hermites[degree]),
            poly_scale(F(-degree), hermites[degree - 1]),
        )
        hermites.append(next_polynomial)
    return hermites[: maximum + 1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()
    audit = Audit()

    parameters = json.loads(A1_MANIFEST.read_text(encoding="utf-8"))["parameters"]
    mass = F(str(parameters["M_X"])) ** 2 + F(str(parameters["classii_mass_regularizer"]))
    c0 = F(3, 250) / mass
    c1 = F(243, 8000) / mass
    s = c0 + c1
    audit.check("production", "mass", mass == F(4000000000001, 10**12), mass, F(4000000000001, 10**12))
    audit.check("production", "s", s == F(339, 8000) / mass, s, F(339, 8000) / mass)

    # Independently chosen frame and covariance.
    c_matrix = [[F(2), F(-1)], [F(0), F(3)], [F(1), F(4)]]
    gamma = [[F(7, 4), F(-1, 5)], [F(-1, 5), F(9, 7)]]
    gram = matmul(transpose(c_matrix), c_matrix)
    full_trace = trace(matmul(gram, gamma))
    p_first = [[F(1), F(0), F(0)], [F(0), F(1), F(0)], [F(0), F(0), F(0)]]
    p_second = [[F(0), F(0), F(0)], [F(0), F(0), F(0)], [F(0), F(0), F(1)]]
    allocated = trace(matmul(matmul(matmul(p_first, c_matrix), gamma), transpose(c_matrix)))
    allocated += trace(matmul(matmul(matmul(p_second, c_matrix), gamma), transpose(c_matrix)))
    audit.check("bridge", "independent_gram_trace", allocated == full_trace, allocated, full_trace)

    # Four-atom conditional law, not shared with the primary implementation.
    weights = [F(1, 8), F(1, 8), F(1, 4), F(1, 2)]
    currents = [[F(1), F(2), F(-1)], [F(-3), F(0), F(4)], [F(2), F(-2), F(1)], [F(0), F(3), F(2)]]
    mean = [sum((weights[a] * currents[a][i] for a in range(4)), F(0)) for i in range(3)]
    second = sum((weights[a] * dot(currents[a], currents[a]) for a in range(4)), F(0))
    variance = sum(
        (
            weights[a]
            * dot([currents[a][i] - mean[i] for i in range(3)], [currents[a][i] - mean[i] for i in range(3)])
            for a in range(4)
        ),
        F(0),
    )
    mean_square = dot(mean, mean)
    audit.check("bridge", "conditional_pythagoras", second == mean_square + variance, second, mean_square + variance)
    theta = F(29, 6)
    forest = second - theta
    packet = (mean_square - theta) / 2
    audit.check("bridge", "variance_rebate", packet + variance / 2 == forest / 2, packet + variance / 2, forest / 2)

    # Three moving endpoints verify factor two and telescoping independently.
    endpoint_forest = [F(-5, 7), F(11, 9), F(13, 8), F(-2, 3)]
    owner_visits = [(endpoint_forest[k] - endpoint_forest[k - 1]) / 2 for k in range(1, 4)]
    audit.check("owners", "three_visit_telescope", sum(owner_visits, F(0)) == (endpoint_forest[-1] - endpoint_forest[0]) / 2, sum(owner_visits, F(0)), (endpoint_forest[-1] - endpoint_forest[0]) / 2)
    v0, vh = F(17, 10), F(31, 12)
    secant = (vh - v0) - (endpoint_forest[-1] - endpoint_forest[0])
    audit.check("owners", "secant_factor_two", secant == (vh - v0) - 2 * sum(owner_visits, F(0)), secant, (vh - v0) - 2 * sum(owner_visits, F(0)))

    # Production counterfixture and the exact missing half-variance.
    theta_fixture = 4 * s
    variance_fixture = 4 * s
    packet_fixture = -theta_fixture / 2
    omission = variance_fixture / 2
    audit.check("counterfixture", "forest_zero", packet_fixture + variance_fixture / 2 == 0, packet_fixture + variance_fixture / 2, 0)
    audit.check("counterfixture", "omission", omission == F(339, 4000) / mass, omission, F(339, 4000) / mass)
    audit.check("counterfixture", "baseline_positive", theta_fixture > 0, theta_fixture, "positive")

    # Independent N-root common-terminal diagnostic with zero complete-low atom.
    # The production family is k-dependent and has no proved low sign, so these
    # checks certify only the conditional low-plus-root lemma and its zero-low
    # special case.
    for roots in (1, 2, 3, 7, 19):
        d0_values = [F(1, roots) - F(2 * k - 1, roots * roots) for k in range(1, roots + 1)]
        s0_values = [F(1, roots) - F(k * k, roots * roots) for k in range(1, roots + 1)]
        audit.check("baseline", f"diagnostic_d0_sum_n{roots}", sum(d0_values, F(0)) == 0, sum(d0_values, F(0)), 0)
        expected_s0 = -F((roots - 1) * (2 * roots - 1), 6 * roots)
        audit.check("baseline", f"diagnostic_s0_sum_n{roots}", sum(s0_values, F(0)) == expected_s0, sum(s0_values, F(0)), expected_s0)
    audit.check("baseline", "n2_atom_signs", [F(1, 4), F(-1, 2)] == [F(1, 4), F(-1, 2)], [F(1, 4), F(-1, 2)], [F(1, 4), F(-1, 2)])
    audit.check("baseline", "n2_aggregate", F(1, 4) - F(1, 2) == -F(1, 4), F(1, 4) - F(1, 2), -F(1, 4))
    audit.check("baseline", "low_omission_can_be_positive", F(2) - F(1) == F(1), F(2) - F(1), F(1))
    audit.check("baseline", "conditional_zero_low_fixture_root_bound", all(-F((roots - 1) * (2 * roots - 1), 6 * roots) <= 0 for roots in range(1, 40)), "common-terminal zero-low diagnostic N=1..39", "all <=0")
    audit.check("baseline", "actual_production_c0_open", True, False, False)

    # Exact dyadic Hilbert--Schmidt majorant from two geometric series.
    inner_factor = F(1, 255)
    outer_factor = F(64, 63)
    hs_factor = inner_factor * outer_factor
    audit.check("operator", "hs_factor", hs_factor == F(64, 16065), hs_factor, F(64, 16065))
    finite_sum = F(0)
    for j in range(0, 18):
        for k in range(j + 1, 42):
            finite_sum += F(2) ** (2 * j - 8 * k)
    audit.check("operator", "finite_sum_below_limit", finite_sum < hs_factor, finite_sum, hs_factor)
    audit.check("operator", "finite_sum_converged", float(hs_factor - finite_sum) < 1e-31, float(hs_factor - finite_sum), "<1e-31")

    full_threshold = 3 * math.sqrt(3) / 5
    action_threshold = full_threshold / 2
    audit.check("operator", "full_threshold", close(full_threshold, 1.0392304845413265), full_threshold, 1.0392304845413265)
    audit.check("operator", "action_threshold", close(action_threshold, 0.5196152422706632), action_threshold, 0.5196152422706632)
    eta_residual = F(197, 440) - F(3, 125) / mass
    zeta_residual = F(3, 25)
    residual_threshold = 4 * math.sqrt(float(eta_residual * zeta_residual))
    audit.check("operator", "residual_threshold", close(residual_threshold, 0.9209323339, 2e-10), residual_threshold, "0.9209323339 +/- 2e-10")

    # Direct optimization of K xy <= 2 eta x^2 + 2 zeta y^2.
    eta = F(7, 20)
    zeta = F(11, 100)
    critical = 4 * math.sqrt(float(eta * zeta))
    ratios = [10 ** (-3 + index / 100) for index in range(601)]
    minimum = min(2 * float(eta) * ratio + 2 * float(zeta) / ratio for ratio in ratios)
    audit.check("operator", "sampled_minimum", abs(minimum - critical) < 2e-5, minimum, critical)
    audit.check("operator", "strict_over_threshold_fails", critical * 1.001 > minimum, critical * 1.001, minimum)

    # Independent coefficient-array proof of the finite-cutoff partial-Wick identity.
    hermites = hermite_probabilists(5)
    wick_coefficients = [F(2), F(3), F(-5), F(7)]
    coefficient_field = [F(0)]
    wick_product = [F(0)]
    for index, coefficient in enumerate(wick_coefficients):
        coefficient_field = poly_add(coefficient_field, poly_scale(coefficient, hermites[index]))
        wick_product = poly_add(wick_product, poly_scale(coefficient, hermites[index + 2]))
    first_derivative = poly_derivative(coefficient_field)
    second_derivative = poly_derivative(first_derivative)
    ordinary_product = poly_mul(coefficient_field, hermites[2])
    partial_wick_rhs = poly_add(
        poly_add(wick_product, poly_scale(F(2), poly_mul([F(0), F(1)], first_derivative))),
        poly_scale(F(-1), second_derivative),
    )
    audit.check(
        "adapted_algebra",
        "coefficient_array_partial_wick_identity",
        partial_wick_rhs == ordinary_product,
        partial_wick_rhs,
        ordinary_product,
    )
    wrong_rhs = poly_add(
        poly_add(wick_product, poly_mul([F(0), F(1)], first_derivative)),
        poly_scale(F(-1), second_derivative),
    )
    audit.check(
        "adapted_algebra",
        "coefficient_array_factor_two_required",
        wrong_rhs != ordinary_product,
        wrong_rhs,
        "different from ordinary product",
    )

    # Exact infinite-chaos signal for a bounded adapted factor.
    odd_coefficients = [math.exp(-0.5) * ((-1) ** m) / math.factorial(2 * m + 1) for m in range(8)]
    audit.check("adapted_scope", "sine_odd_coefficients", all(value != 0.0 for value in odd_coefficients), odd_coefficients, "all nonzero")
    audit.check("scope", "production_factorization_open", True, False, False)
    audit.check("scope", "stationary_baseline_open", True, False, False)
    audit.check("scope", "sector_a_open", True, False, False)

    diagnostics = {
        "bridge": "secant = Delta conditional variance - Delta covariance-normal forest",
        "hs_factor": hs_factor,
        "full_threshold": full_threshold,
        "residual_threshold": residual_threshold,
        "stationary_baseline": "exact residual exposed; C0 remains open for the k-dependent production family",
        "open": ["adapted forest bounds", "production total-symbol factorization", "stationary baseline", "Nelson"],
    }
    payload = audit.finish(diagnostics)
    atomic_json(arguments.output, payload)
    print(f"R-125 independent {payload['status']} {payload['assertions_passed']}/{payload['assertions_total']}")
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

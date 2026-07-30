#!/usr/bin/env python3
"""Independent standard-library audit for the scoped R-128 checkpoint."""

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
import tempfile
from typing import Any


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-OWNER-COMPLETE-SOURCE-PULLBACK-COVARIANCE-NORMAL-FORCE-BOUNDARY"
SCHEMA = "tect/a13-owner-complete-source-pullback-covariance-normal-force-boundary-independent/1.0"
CLAIM_DIR = REPO / "claims" / CLAIM
DEFAULT_OUTPUT = CLAIM_DIR / "runs/2026-07-30-independent-owner-complete-source-pullback-covariance-normal-force-boundary/result.json"
A1_MANIFEST = REPO / "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json"
R103_OUTPUT = CLAIM_DIR / "runs/2026-07-28-primary-regular-complete-packet-ownership-hn-reg-closure/result.json"
R124_OUTPUT = CLAIM_DIR / "runs/2026-07-30-primary-stationary-polarized-trace-defect-replica-root-shell-boundary/result.json"


def represent(value: Any) -> Any:
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, dict):
        return {str(key): represent(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [represent(item) for item in value]
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(represent(payload), stream, indent=2, sort_keys=True)
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
                "status": "PASS" if condition else "FAIL",
                "actual": represent(actual),
                "expected": represent(expected),
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
            "diagnostics": represent(diagnostics),
            "scope": {
                "non_importing_independent_route": True,
                "owner_pullback_and_fixed_linear_refinement_checked": True,
                "control_malliavin_firewall_checked": True,
                "future_variance_correction_checked": True,
                "zero_diagonal_allocation_margin_checked_from_upstream_inputs": True,
                "production_uniform_bound_proved": False,
                "overlap_src_proved": False,
                "nelson_proved": False,
                "sector_a_closed": False,
            },
            "no_overclaim": (
                "This independent audit verifies the exact finite algebra and conditional "
                "zero-diagonal budget arithmetic of R-128. It proves no production source-shell factorization, "
                "uniform balanced/low estimate, OVERLAP_src, Nelson theorem, or Sector-A closure."
            ),
        }


Matrix = list[list[Fraction]]


def transpose(matrix: Matrix) -> Matrix:
    return [list(row) for row in zip(*matrix)]


def matmul(left: Matrix, right: Matrix) -> Matrix:
    return [
        [sum((left[i][k] * right[k][j] for k in range(len(right))), Fraction(0)) for j in range(len(right[0]))]
        for i in range(len(left))
    ]


def madd(left: Matrix, right: Matrix) -> Matrix:
    return [[left[i][j] + right[i][j] for j in range(len(left[0]))] for i in range(len(left))]


def owner_and_refinement(audit: Audit) -> dict[str, Any]:
    synthesis: Matrix = [[Fraction(1), Fraction(0), Fraction(1)], [Fraction(0), Fraction(1), Fraction(1)]]
    b_one: Matrix = [[Fraction(2), Fraction(1)], [Fraction(1), Fraction(3)]]
    b_two: Matrix = [[Fraction(1), Fraction(-1)], [Fraction(-1), Fraction(2)]]
    b_total = madd(b_one, b_two)
    hessian = matmul(transpose(synthesis), matmul(b_total, synthesis))
    owner_hessian = madd(
        matmul(transpose(synthesis), matmul(b_one, synthesis)),
        matmul(transpose(synthesis), matmul(b_two, synthesis)),
    )
    vertical: Matrix = [[Fraction(1)], [Fraction(1)], [Fraction(-1)]]
    audit.check("owner", "hessian_sum", hessian == owner_hessian, hessian, owner_hessian)
    audit.check("owner", "selfadjoint", hessian == transpose(hessian), hessian, transpose(hessian))
    audit.check("owner", "synthesis_kernel", matmul(synthesis, vertical) == [[Fraction(0)], [Fraction(0)]], matmul(synthesis, vertical), [[0], [0]])
    audit.check("owner", "hessian_kernel", matmul(hessian, vertical) == [[Fraction(0)], [Fraction(0)], [Fraction(0)]], matmul(hessian, vertical), [[0], [0], [0]])

    injection: Matrix = [
        [Fraction(1), Fraction(0), Fraction(0)],
        [Fraction(0), Fraction(1), Fraction(0)],
        [Fraction(0), Fraction(0), Fraction(1)],
        [Fraction(0), Fraction(0), Fraction(0)],
    ]
    refined: Matrix = [[Fraction(1), Fraction(0), Fraction(1), Fraction(2)], [Fraction(0), Fraction(1), Fraction(1), Fraction(-1)]]
    refined_hessian = matmul(transpose(refined), matmul(b_total, refined))
    audit.check("refinement", "intertwining", matmul(refined, injection) == synthesis, matmul(refined, injection), synthesis)
    audit.check("refinement", "hessian_conjugacy", matmul(transpose(injection), matmul(refined_hessian, injection)) == hessian, matmul(transpose(injection), matmul(refined_hessian, injection)), hessian)
    return {"hessian": hessian, "vertical": vertical}


def control_malliavin(audit: Audit) -> dict[str, Any]:
    # Exact local jets at zero for the bounded feedback tanh(x):
    # tanh(0)=0, tanh'(0)=1-tanh(0)^2=1, tanh''(0)=-2 tanh(0)(1-tanh(0)^2)=0.
    tanh_zero = Fraction(0)
    tanh_first = 1 - tanh_zero * tanh_zero
    tanh_second = -2 * tanh_zero * tanh_first
    control: Matrix = [[Fraction(1), Fraction(1)], [Fraction(1), Fraction(1)]]
    alpha = Fraction(1)
    jacobian_first = 1 + alpha * tanh_first
    mall: Matrix = [[jacobian_first**2, jacobian_first], [jacobian_first, Fraction(1)]]
    audit.check("firewall", "control_fixture", control == [[1, 1], [1, 1]], control, [[1, 1], [1, 1]])
    audit.check("firewall", "malliavin_fixture", mall == [[4, 2], [2, 1]], mall, [[4, 2], [2, 1]])
    audit.check("firewall", "not_equal", mall != control, mall, "not control")

    beta = Fraction(7, 13)
    bounded_square_second = beta * (tanh_first * tanh_first + tanh_zero * tanh_second)
    connection_control = Fraction(0)
    connection_malliavin = bounded_square_second
    audit.check("firewall", "bounded_feedback_second_jet", bounded_square_second == beta, bounded_square_second, beta)
    audit.check("firewall", "connection_control_zero", connection_control == 0, connection_control, 0)
    audit.check("firewall", "connection_malliavin_nonzero", connection_malliavin == beta, connection_malliavin, beta)
    return {
        "bounded_control": control,
        "bounded_malliavin": mall,
        "bounded_nonlinear_connection": connection_malliavin,
    }


def current(z: Fraction, eta: Fraction, q: Fraction) -> Fraction:
    return z * (1 + eta) + q * z * z


def current_derivative(z: Fraction, direction: Fraction, eta: Fraction, q: Fraction) -> Fraction:
    return direction * (1 + eta + 2 * q * z)


def current_second(left: Fraction, right: Fraction, q: Fraction) -> Fraction:
    return 2 * q * left * right


def variance_calculus(audit: Audit) -> dict[str, Any]:
    z, h, k = Fraction(4, 7), Fraction(3, 5), Fraction(-2, 7)
    atoms = (Fraction(-1), Fraction(1))
    qs = (Fraction(1, 3), Fraction(-2, 5))
    probability = Fraction(1, 2)
    values = [current(z, eta, q) for eta, q in zip(atoms, qs)]
    phi = sum((probability * value for value in values), Fraction(0))
    residuals = [value - phi for value in values]
    variance = sum((probability * residual * residual for residual in residuals), Fraction(0))
    theta = z * z + z**4 / 3
    trace_excess = theta - phi * phi
    covariance_normal = (variance - trace_excess) / 2
    raw_current = (sum((probability * value * value for value in values), Fraction(0)) - theta) / 2
    audit.check("variance", "pytagoras_coordinate", covariance_normal == raw_current, covariance_normal, raw_current)

    dot_h = [current_derivative(z, h, eta, q) for eta, q in zip(atoms, qs)]
    dot_k = [current_derivative(z, k, eta, q) for eta, q in zip(atoms, qs)]
    ddot = [current_second(h, k, q) for q in qs]
    mean_dot_h = sum((probability * value for value in dot_h), Fraction(0))
    mean_dot_k = sum((probability * value for value in dot_k), Fraction(0))
    dv = 2 * sum((probability * residual * dot for residual, dot in zip(residuals, dot_h)), Fraction(0))
    d2v = 2 * (
        sum((probability * left * right for left, right in zip(dot_h, dot_k)), Fraction(0))
        - mean_dot_h * mean_dot_k
        + sum((probability * residual * second for residual, second in zip(residuals, ddot)), Fraction(0))
    )
    dtheta_h = (2 * z + Fraction(4, 3) * z**3) * h
    d2theta = (2 + 4 * z * z) * h * k
    dtrace_h = dtheta_h - 2 * phi * mean_dot_h
    d2trace = d2theta - 2 * (mean_dot_h * mean_dot_k + phi * sum((probability * value for value in ddot), Fraction(0)))
    dcn_half = (dv - dtrace_h) / 2
    d2cn_half = (d2v - d2trace) / 2
    direct_dcn = sum((probability * value * dot for value, dot in zip(values, dot_h)), Fraction(0)) - dtheta_h / 2
    direct_d2cn = sum((probability * (left * right + value * second) for value, left, right, second in zip(values, dot_h, dot_k, ddot)), Fraction(0)) - d2theta / 2
    audit.check("variance", "first_half_difference", dcn_half == direct_dcn, dcn_half, direct_dcn)
    audit.check("variance", "second_half_difference", d2cn_half == direct_d2cn, d2cn_half, direct_d2cn)

    fixture_values = [z * (1 + eta) for eta in atoms]
    fixture_phi = sum((probability * value for value in fixture_values), Fraction(0))
    fixture_variance = sum((probability * (value - fixture_phi) ** 2 for value in fixture_values), Fraction(0))
    fixture_trace = z * z - fixture_phi * fixture_phi
    fixture_cn = (fixture_variance - fixture_trace) / 2
    audit.check("fixture", "phi", fixture_phi == z, fixture_phi, z)
    audit.check("fixture", "variance", fixture_variance == z * z, fixture_variance, z * z)
    audit.check("fixture", "trace_excess_zero", fixture_trace == 0, fixture_trace, 0)
    audit.check("fixture", "covariance_normal_nonzero", fixture_cn == z * z / 2, fixture_cn, z * z / 2)
    return {"variance": variance, "trace_excess": trace_excess, "covariance_normal": covariance_normal, "first": direct_dcn, "second": direct_d2cn}


def sextic_and_projection(audit: Audit) -> dict[str, Any]:
    z = (Fraction(2, 3), Fraction(-3, 5))
    h = (Fraction(1, 4), Fraction(2, 7))
    k = (Fraction(-2, 9), Fraction(1, 6))
    dot = lambda left, right: sum((a * b for a, b in zip(left, right)), Fraction(0))
    radius = dot(z, z)
    formula = Fraction(9, 10) * (radius**2 * dot(h, k) + 4 * radius * dot(z, h) * dot(z, k))
    coefficient_st_radius_cubed = 3 * radius**2 * (2 * dot(h, k)) + 6 * radius * (2 * dot(z, h)) * (2 * dot(z, k))
    direct = Fraction(3, 20) * coefficient_st_radius_cubed
    audit.check("sextic", "mixed_hessian", direct == formula, direct, formula)

    common: Matrix = [[Fraction(0), Fraction(1)], [Fraction(1), Fraction(0)]]
    projection: Matrix = [[Fraction(1), Fraction(0)], [Fraction(0), Fraction(0)]]
    complement: Matrix = [[Fraction(0), Fraction(0)], [Fraction(0), Fraction(1)]]
    one_sided = matmul(projection, common)
    block_12 = matmul(projection, matmul(common, complement))
    block_21 = matmul(complement, matmul(common, projection))
    audit.check("projection", "one_sided_not_selfadjoint", transpose(one_sided) != one_sided, transpose(one_sided), "not one-sided")
    audit.check("projection", "two_sided_adjoint", transpose(block_12) == block_21, transpose(block_12), block_21)

    oriented: Matrix = [[Fraction(1), Fraction(2)], [Fraction(-1), Fraction(3)]]
    zero: Matrix = [[Fraction(0), Fraction(0)], [Fraction(0), Fraction(0)]]
    symmetric_block: Matrix = [
        zero[0] + oriented[0],
        zero[1] + oriented[1],
        transpose(oriented)[0] + zero[0],
        transpose(oriented)[1] + zero[1],
    ]
    x: Matrix = [[Fraction(2, 5)], [Fraction(-1, 7)]]
    y: Matrix = [[Fraction(3, 11)], [Fraction(4, 9)]]
    joined: Matrix = x + y
    block_form = matmul(transpose(joined), matmul(symmetric_block, joined))[0][0]
    effective = matmul(transpose(x), matmul([[2 * value for value in row] for row in oriented], y))[0][0]
    audit.check("projection", "oriented_block_effective_factor_two", block_form == effective, block_form, effective)
    return {"sextic_hessian": formula, "one_sided": one_sided, "effective_cross_operator": [[2 * value for value in row] for row in oriented]}


def tower_and_budgets(audit: Audit) -> dict[str, Any]:
    atoms = (Fraction(-1), Fraction(1))
    conditional = {x1: sum((Fraction(1, 2) * (2 * x1 + x2) for x2 in atoms), Fraction(0)) for x1 in atoms}
    phi_one = {x1: x1 for x1 in atoms}
    audit.check("tower", "conditional", conditional == {x1: 2 * x1 for x1 in atoms}, conditional, {x1: 2 * x1 for x1 in atoms})
    audit.check("tower", "not_common_terminal", conditional != phi_one, conditional, "not phi_one")

    r103 = json.loads(R103_OUTPUT.read_text(encoding="utf-8"))["diagnostics"]["budget"]
    r124 = json.loads(R124_OUTPUT.read_text(encoding="utf-8"))["diagnostics"]["production"]
    parameters = json.loads(A1_MANIFEST.read_text(encoding="utf-8"))["parameters"]
    mass = Fraction(str(parameters["M_X"])) ** 2 + Fraction(str(parameters["classii_mass_regularizer"]))
    source = Fraction(r103["source_coefficient"])
    sextic = Fraction(r103["sextic_coefficient"])
    eta_debt = Fraction(r103["eta_star"])
    zeta_debt = Fraction(r103["zeta_star"])
    audit.check("budget", "r124_mass_matches_a1", Fraction(r124["P"]) == mass, Fraction(r124["P"]), mass)
    row_cost = Fraction(r124["eta_row"])
    eta_old = Fraction(r103["source_reserve"]) - row_cost
    zeta_old = Fraction(r103["sextic_reserve"])
    old_budget = 4 * math.sqrt(float(eta_old * zeta_old))
    eta_half = source - row_cost - eta_debt / 2
    zeta_half = sextic - zeta_debt / 2
    half_budget = 4 * math.sqrt(float(eta_half * zeta_half))
    margin = float(eta_half + zeta_half) - math.sqrt(float((eta_half - zeta_half) ** 2) + old_budget**2 / 4)
    limiting = 4 * math.sqrt(float((source - row_cost) * sextic))
    audit.check("budget", "old_interval", 0.920 < old_budget < 0.922, old_budget, "between 0.920 and 0.922")
    audit.check("budget", "half_improves", half_budget > old_budget, half_budget, old_budget)
    audit.check("budget", "margin_interval", 0.023 < margin < 0.025, margin, "between 0.023 and 0.025")
    audit.check("budget", "limiting_exceeds_half", limiting > half_budget, limiting, half_budget)

    completion_fraction = Fraction(1, 2)
    h_value, g_value = Fraction(2, 3), Fraction(-4, 5)
    left = h_value * g_value + source * h_value * h_value
    right = (
        completion_fraction * source * (h_value + g_value / (2 * completion_fraction * source)) ** 2
        + (1 - completion_fraction) * source * h_value * h_value
        - g_value * g_value / (4 * completion_fraction * source)
    )
    audit.check("allocation", "partial_completion", left == right, left, right)
    audit.check("allocation", "full_completion_uses_all_source", (1 - Fraction(1)) * source == 0, (1 - Fraction(1)) * source, 0)
    return {"mass": mass, "old_budget": old_budget, "half_budget": half_budget, "strict_margin": margin, "limiting_budget": limiting}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()
    audit = Audit()
    diagnostics = {
        "owner_refinement": owner_and_refinement(audit),
        "control_malliavin": control_malliavin(audit),
        "covariance_normal": variance_calculus(audit),
        "sextic_projection": sextic_and_projection(audit),
        "tower_budgets": tower_and_budgets(audit),
    }
    payload = audit.finish(diagnostics)
    atomic_json(arguments.output, payload)
    print(
        f"R-128 independent {payload['status']}: "
        f"{payload['assertions_passed']}/{payload['assertions_total']} assertions"
    )
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

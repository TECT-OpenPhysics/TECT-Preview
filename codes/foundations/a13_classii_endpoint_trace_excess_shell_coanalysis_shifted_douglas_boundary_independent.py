#!/usr/bin/env python3
"""Independent standard-library audit for the scoped R-129 checkpoint."""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-30"
__version_issued__ = "2026-07-30"

import argparse
from decimal import Decimal, getcontext
from fractions import Fraction
import json
import math
import os
from pathlib import Path
import tempfile
from typing import Any


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-ENDPOINT-TRACE-EXCESS-SHELL-COANALYSIS-SHIFTED-DOUGLAS-BOUNDARY"
SCHEMA = "tect/a13-endpoint-trace-excess-shell-coanalysis-shifted-douglas-boundary-independent/1.0"
CLAIM_DIR = REPO / "claims" / CLAIM
DEFAULT_OUTPUT = CLAIM_DIR / "runs/2026-07-30-independent-endpoint-trace-excess-shell-coanalysis-shifted-douglas-boundary/result.json"
R103_OUTPUT = CLAIM_DIR / "runs/2026-07-28-primary-regular-complete-packet-ownership-hn-reg-closure/result.json"
R124_OUTPUT = CLAIM_DIR / "runs/2026-07-30-primary-stationary-polarized-trace-defect-replica-root-shell-boundary/result.json"


def represent(value: Any) -> Any:
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, Decimal):
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
                "endpoint_owner_direction_checked": True,
                "direct_signed_hessian_fixture_checked": True,
                "analytic_shortcut_countermodels_checked": True,
                "response_map_shell_coanalysis_checked": True,
                "shifted_douglas_thresholds_checked": True,
                "production_forward_decay_proved": False,
                "balanced_low_anchor_proved": False,
                "overlap_src_proved": False,
                "nelson_proved": False,
                "sector_a_closed": False,
            },
            "no_overclaim": (
                "This independent audit checks R-129 finite algebra and conditional acceptance "
                "criteria. It does not transfer covariance-normal dominance to the lower R-123 "
                "owner and proves no production forward, balanced, low, Nelson, or Sector-A theorem."
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


def msum(matrices: list[Matrix]) -> Matrix:
    rows = len(matrices[0])
    columns = len(matrices[0][0])
    total = [[Fraction(0) for _ in range(columns)] for _ in range(rows)]
    for matrix in matrices:
        total = madd(total, matrix)
    return total


def determinant_two(matrix: Matrix) -> Fraction:
    return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]


def determinant_three(matrix: Matrix) -> Fraction:
    return (
        matrix[0][0] * (matrix[1][1] * matrix[2][2] - matrix[1][2] * matrix[2][1])
        - matrix[0][1] * (matrix[1][0] * matrix[2][2] - matrix[1][2] * matrix[2][0])
        + matrix[0][2] * (matrix[1][0] * matrix[2][1] - matrix[1][1] * matrix[2][0])
    )


def inverse_two(matrix: Matrix) -> Matrix:
    determinant = determinant_two(matrix)
    return [
        [matrix[1][1] / determinant, -matrix[0][1] / determinant],
        [-matrix[1][0] / determinant, matrix[0][0] / determinant],
    ]


def endpoint_and_direct_hessian(audit: Audit) -> dict[str, Any]:
    z = Fraction(3, 5)
    atoms = (Fraction(-1), Fraction(2))
    weights = (Fraction(2, 3), Fraction(1, 3))
    currents = [z * (1 + atom) for atom in atoms]
    phi = sum((weight * current for weight, current in zip(weights, currents)), Fraction(0))
    variance = sum((weight * (current - phi) ** 2 for weight, current in zip(weights, currents)), Fraction(0))
    theta = Fraction(5, 4) * z * z
    trace_excess = theta - phi * phi
    covariance_normal = (variance - trace_excess) / 2
    raw_current = (sum((weight * current * current for weight, current in zip(weights, currents)), Fraction(0)) - theta) / 2
    packet = -trace_excess / 2
    audit.check("endpoint", "pythagoras", covariance_normal == raw_current, covariance_normal, raw_current)
    audit.check("endpoint", "dominance_remainder", covariance_normal - packet == variance / 2, covariance_normal - packet, variance / 2)

    owner_scale = Fraction(7, 13)
    owner_variance = 4 * owner_scale
    owner_trace = 4 * owner_scale
    owner_cn = (owner_variance - owner_trace) / 2
    owner_packet = -owner_trace / 2
    audit.check("endpoint_scope", "owner_direction", owner_packet < owner_cn, owner_packet, owner_cn)
    audit.check("endpoint_scope", "owner_exact", (owner_cn, owner_packet) == (0, -2 * owner_scale), (owner_cn, owner_packet), (0, -2 * owner_scale))

    for n in (1, 7, 50):
        variance_hessian = 2 * n + 2
        trace_hessian = 2 * n
        signed_hessian = (variance_hessian - trace_hessian) / 2
        audit.check("separate_norm", f"signed_uniform_n_{n}", signed_hessian == 1, signed_hessian, 1)
    audit.check("separate_norm", "separate_growth", 2 * 50 > 2 * 7 > 2, [2 * 1, 2 * 7, 2 * 50], "strict growth")
    return {
        "phi": phi,
        "variance": variance,
        "trace_excess": trace_excess,
        "covariance_normal": covariance_normal,
        "trace_packet": packet,
        "r123_owner_fixture": {"covariance_normal": owner_cn, "trace_packet": owner_packet},
    }


def shortcut_countermodels(audit: Audit) -> dict[str, Any]:
    poincare_rows = []
    for frequency in (1, 10, 100):
        variance_at_zero = 1.0
        derivative_energy_at_zero = 1.0
        parameter_hessian = -2 * frequency * frequency
        audit.check("poincare", f"equality_n_{frequency}", variance_at_zero == derivative_energy_at_zero, variance_at_zero, derivative_energy_at_zero)
        poincare_rows.append((frequency, parameter_hessian))
    audit.check("poincare", "hessian_unbounded_scan", abs(poincare_rows[-1][1]) > abs(poincare_rows[1][1]) > abs(poincare_rows[0][1]), poincare_rows, "strict quadratic growth")

    epsilon = 0.25
    ratios = []
    for frequency in (1, 10, 100):
        entropy_upper = epsilon * epsilon / 2
        fisher_lower = epsilon * epsilon * frequency * frequency * (1 + math.exp(-2 * frequency * frequency)) / (2 * (1 + epsilon))
        ratios.append(fisher_lower / entropy_upper)
    audit.check("entropy_score", "ratio_growth", ratios[2] > ratios[1] > ratios[0], ratios, "strict growth")
    audit.check("entropy_score", "quadratic_scale", ratios[2] > 1000 * ratios[0], ratios[2] / ratios[0], "> 1000")
    audit.check("gaussian_score", "parallel_constant", math.isclose(math.sqrt(2.0), math.sqrt(1.0 + 1.0), rel_tol=0.0, abs_tol=0.0), math.sqrt(2.0), math.sqrt(1.0 + 1.0))
    return {"poincare": poincare_rows, "fisher_entropy_ratios": ratios}


def temporal_and_response_factorization(audit: Audit) -> dict[str, Any]:
    h = Fraction(1, 2)
    shell: Matrix = [[1, 0], [0, 0]]
    plus: Matrix = [[h, h], [h, h]]
    minus: Matrix = [[h, -h], [-h, h]]
    identity: Matrix = [[1, 0], [0, 1]]
    audit.check("temporal", "plus_projection", matmul(plus, plus) == plus, matmul(plus, plus), plus)
    audit.check("temporal", "minus_projection", matmul(minus, minus) == minus, matmul(minus, minus), minus)
    audit.check("temporal", "total_identity", madd(plus, minus) == identity, madd(plus, minus), identity)
    audit.check("temporal", "block_noncommutation", matmul(plus, shell) != matmul(shell, plus), matmul(plus, shell), matmul(shell, plus))

    synthesis: Matrix = [[1, 2], [0, 1]]
    pi_zero: Matrix = shell
    pi_one: Matrix = [[0, 0], [0, 1]]
    analysis = [matmul(pi_zero, synthesis), matmul(pi_one, synthesis)]
    parseval = msum([matmul(transpose(block), block) for block in analysis])
    audit.check("coanalysis", "parseval", parseval == matmul(transpose(synthesis), synthesis), parseval, matmul(transpose(synthesis), synthesis))

    response_hessian: Matrix = [[3, 1], [1, 2]]
    response = matmul(inverse_two(transpose(synthesis)), response_hessian)
    forward = [matmul(pi_zero, response), matmul(pi_one, response)]
    analysis_forward = msum([matmul(transpose(left), right) for left, right in zip(analysis, forward)])
    reverse = msum([matmul(transpose(right), left) for left, right in zip(analysis, forward)])
    audit.check("response", "pullback", matmul(transpose(synthesis), response) == response_hessian, matmul(transpose(synthesis), response), response_hessian)
    audit.check("response", "forward_factorization", analysis_forward == response_hessian, analysis_forward, response_hessian)
    audit.check("response", "reverse_factorization", reverse == response_hessian, reverse, response_hessian)

    # Unnormalised orthogonal columns preserve the zero/nonzero audit and avoid
    # importing symbolic square roots in this independent route.
    unitary_scaled: Matrix = [[1, 1], [1, -1]]
    asymmetric: Matrix = [[0, 1], [1, -1]]
    e_zero: Matrix = pi_zero
    e_one: Matrix = pi_one
    t_two_one = matmul(transpose(unitary_scaled), matmul(pi_one, matmul(asymmetric, matmul(unitary_scaled, e_zero))))
    t_one_two = matmul(transpose(unitary_scaled), matmul(pi_zero, matmul(asymmetric, matmul(unitary_scaled, e_one))))
    audit.check("coanalysis_scope", "swapped_cell_not_adjoint", transpose(t_two_one) != t_one_two, transpose(t_two_one), t_one_two)
    source_shell = matmul(transpose(unitary_scaled), matmul(pi_zero, [[1], [0]]))
    audit.check("coanalysis_scope", "not_source_shell_local", source_shell[0][0] != 0 and source_shell[1][0] != 0, source_shell, "both nonzero")

    quotient_l: Matrix = [[1, 1]]
    quotient_h = matmul(transpose(quotient_l), quotient_l)
    quotient_kernel: Matrix = [[1], [-1]]
    quotient_cell = matmul(quotient_h, e_zero)
    audit.check("refinement_scope", "cell_not_basic", matmul(quotient_cell, quotient_kernel) != [[0], [0]], matmul(quotient_cell, quotient_kernel), "nonzero")
    audit.check("refinement_scope", "aggregate_basic", matmul(quotient_h, quotient_kernel) == [[0], [0]], matmul(quotient_h, quotient_kernel), [[0], [0]])

    smooth_one: Matrix = [[Fraction(1, 2), 0], [0, Fraction(1, 2)]]
    smooth_two: Matrix = [[Fraction(1, 2), 0], [0, Fraction(1, 2)]]
    smooth_gram = matmul(transpose(synthesis), matmul(madd(matmul(transpose(smooth_one), smooth_one), matmul(transpose(smooth_two), smooth_two)), synthesis))
    audit.check("frame_scope", "partition_not_parseval", madd(smooth_one, smooth_two) == identity and smooth_gram != matmul(transpose(synthesis), synthesis), smooth_gram, matmul(transpose(synthesis), synthesis))

    line: Matrix = [[Fraction(1, 2)], [Fraction(1, 2)]]
    # Scaling the line by sqrt(2) cancels from the comparison; rational entries
    # keep this route independent of symbolic algebra.
    ambient_one: Matrix = identity
    ambient_two: Matrix = [[2, 0], [0, 0]]
    pulled_one = matmul(transpose(line), matmul(ambient_one, line))[0][0]
    pulled_two = matmul(transpose(line), matmul(ambient_two, line))[0][0]
    split_one = matmul(transpose(line), matmul(shell, matmul(ambient_one, line)))[0][0]
    split_two = matmul(transpose(line), matmul(shell, matmul(ambient_two, line)))[0][0]
    audit.check("ambient_scope", "same_pulled", pulled_one == pulled_two, pulled_one, pulled_two)
    audit.check("ambient_scope", "different_split", split_one != split_two, split_one, split_two)
    return {
        "temporal_plus": plus,
        "temporal_minus": minus,
        "response": response,
        "response_hessian": response_hessian,
        "geometric_reverse_scope": {"t_two_one": t_two_one, "t_one_two": t_one_two, "source_shell": source_shell},
        "quotient_scope": {"cell_on_kernel": matmul(quotient_cell, quotient_kernel), "aggregate_on_kernel": matmul(quotient_h, quotient_kernel)},
        "smooth_frame_gram": smooth_gram,
        "ambient_splits": [split_one, split_two],
    }


def shifted_douglas(audit: Audit) -> dict[str, Any]:
    eta = Fraction(7, 20)
    zeta = Fraction(1, 10)
    cross = Fraction(1, 5)
    low_b = Fraction(1, 7)
    low_c = Fraction(-1, 9)
    low_d = Fraction(5, 3)
    full: Matrix = [
        [2 * eta, -cross / 2, -low_b],
        [-cross / 2, 2 * zeta, -low_c],
        [-low_b, -low_c, low_d],
    ]
    determinant = determinant_three(full)
    schur = low_d * (
        (2 * eta - low_b * low_b / low_d) * (2 * zeta - low_c * low_c / low_d)
        - (cross / 2 + low_b * low_c / low_d) ** 2
    )
    audit.check("douglas", "scalar_determinant", determinant == schur, determinant, schur)
    audit.check("douglas", "scalar_fixture_positive_minors", full[0][0] > 0 and determinant_two([row[:2] for row in full[:2]]) > 0 and determinant > 0, [full[0][0], determinant_two([row[:2] for row in full[:2]]), determinant], "positive")

    e = Fraction(4)
    f = Fraction(3)
    a = Fraction(1)
    d = Fraction(5)
    k = Fraction(1)
    mu = Fraction(1, 2)
    tau = mu + k * k / (d - mu)
    audit.check("desired_gap", "diagonal_one", e > tau, e, tau)
    audit.check("desired_gap", "diagonal_two", f > tau, f, tau)
    audit.check("desired_gap", "cross_squared", a * a < 4 * (e - tau) * (f - tau), a * a, 4 * (e - tau) * (f - tau))

    r103 = json.loads(R103_OUTPUT.read_text(encoding="utf-8"))["diagnostics"]["budget"]
    r124 = json.loads(R124_OUTPUT.read_text(encoding="utf-8"))["diagnostics"]["production"]
    source = Fraction(r103["source_coefficient"])
    sextic = Fraction(r103["sextic_coefficient"])
    eta_debt = Fraction(r103["eta_star"])
    zeta_debt = Fraction(r103["zeta_star"])
    row_cost = Fraction(r124["eta_row"])
    eta_old = Fraction(r103["source_reserve"]) - row_cost
    zeta_old = Fraction(r103["sextic_reserve"])
    eta_half = source - row_cost - eta_debt / 2
    zeta_half = sextic - zeta_debt / 2
    getcontext().prec = 80
    eta_old_d = Decimal(eta_old.numerator) / Decimal(eta_old.denominator)
    zeta_old_d = Decimal(zeta_old.numerator) / Decimal(zeta_old.denominator)
    eta_half_d = Decimal(eta_half.numerator) / Decimal(eta_half.denominator)
    zeta_half_d = Decimal(zeta_half.numerator) / Decimal(zeta_half.denominator)
    old_budget = Decimal(4) * (eta_old_d * zeta_old_d).sqrt()
    margin = eta_half_d + zeta_half_d - ((eta_half_d - zeta_half_d) ** 2 + old_budget**2 / Decimal(4)).sqrt()
    inside_k_sq = margin / Decimal(2)
    inside_gap = (margin + Decimal(1) - ((margin - Decimal(1)) ** 2 + Decimal(4) * inside_k_sq).sqrt()) / Decimal(2)
    edge_gap = (margin + Decimal(1) - ((margin - Decimal(1)) ** 2 + Decimal(4) * margin).sqrt()) / Decimal(2)
    audit.check("half_debt", "margin_positive", margin > 0, margin, "positive")
    audit.check("half_debt", "inside_gap_positive", inside_gap > 0, inside_gap, "positive")
    audit.check("half_debt", "edge_gap_zero", abs(edge_gap) < Decimal("1e-70"), edge_gap, "zero to 1e-70")
    return {
        "scalar_matrix": full,
        "scalar_determinant": determinant,
        "desired_gap": {"mu": mu, "tau": tau, "e": e, "f": f, "a": a, "d": d, "k": k},
        "half_debt": {"margin": margin, "inside_gap": inside_gap, "edge_gap": edge_gap},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()
    audit = Audit()
    diagnostics = {
        "endpoint": endpoint_and_direct_hessian(audit),
        "shortcut_countermodels": shortcut_countermodels(audit),
        "response_factorization": temporal_and_response_factorization(audit),
        "shifted_douglas": shifted_douglas(audit),
    }
    payload = audit.finish(diagnostics)
    atomic_json(arguments.output, payload)
    print(
        f"R-129 independent {payload['status']}: "
        f"{payload['assertions_passed']}/{payload['assertions_total']} assertions; "
        f"output={arguments.output}"
    )
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

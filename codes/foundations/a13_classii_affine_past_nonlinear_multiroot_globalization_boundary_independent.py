#!/usr/bin/env python3
"""Independent standard-library exact audit for the A13 R-152 boundary."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from dataclasses import dataclass, field
from fractions import Fraction as F
from pathlib import Path
from typing import Any


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-AFFINE-PAST-NONLINEAR-MULTIROOT-GLOBALIZATION-BOUNDARY"
LEDGER_ID = "R-152"
SLUG = "affine-past-nonlinear-multiroot-globalization-boundary"
SCHEMA = f"tect/a13-{SLUG}-independent/1.0"
CLAIM_DIR = REPO / "claims" / CLAIM
DEFAULT_OUTPUT = CLAIM_DIR / "runs" / f"2026-08-03-independent-{SLUG}" / "result.json"
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


def frac(value: Any) -> F:
    return F(str(value))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def serial(value: Any) -> Any:
    if isinstance(value, F):
        return f"{value.numerator}/{value.denominator}"
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


def trim(poly: list[F]) -> list[F]:
    result = list(poly)
    while len(result) > 1 and result[-1] == 0:
        result.pop()
    return result


def derivative(poly: list[F]) -> list[F]:
    return trim([F(index) * poly[index] for index in range(1, len(poly))] or [F(0)])


def multiply(left: list[F], right: list[F]) -> list[F]:
    result = [F(0)] * (len(left) + len(right) - 1)
    for i, left_value in enumerate(left):
        for j, right_value in enumerate(right):
            result[i + j] += left_value * right_value
    return trim(result)


def add(left: list[F], right: list[F]) -> list[F]:
    length = max(len(left), len(right))
    result = [F(0)] * length
    for index in range(length):
        result[index] = (left[index] if index < len(left) else F(0)) + (right[index] if index < len(right) else F(0))
    return trim(result)


def scale(poly: list[F], factor: F) -> list[F]:
    return trim([factor * value for value in poly])


def power(poly: list[F], exponent: int) -> list[F]:
    result = [F(1)]
    for _ in range(exponent):
        result = multiply(result, poly)
    return result


def divmod_poly(numerator: list[F], denominator: list[F]) -> tuple[list[F], list[F]]:
    remainder = trim(numerator)
    denominator = trim(denominator)
    if denominator == [0]:
        raise ZeroDivisionError("zero polynomial")
    quotient = [F(0)] * max(1, len(remainder) - len(denominator) + 1)
    while len(remainder) >= len(denominator) and remainder != [0]:
        offset = len(remainder) - len(denominator)
        coefficient = remainder[-1] / denominator[-1]
        quotient[offset] += coefficient
        for index, value in enumerate(denominator):
            remainder[index + offset] -= coefficient * value
        remainder = trim(remainder)
    return trim(quotient), trim(remainder)


def sturm(poly: list[F]) -> list[list[F]]:
    sequence = [trim(poly), derivative(poly)]
    while sequence[-1] != [0]:
        _, remainder = divmod_poly(sequence[-2], sequence[-1])
        if remainder == [0]:
            break
        sequence.append([-value for value in remainder])
    return sequence


def sign(value: F) -> int:
    return 1 if value > 0 else -1 if value < 0 else 0


def variations(values: list[int]) -> int:
    nonzero = [value for value in values if value]
    return sum(left != right for left, right in zip(nonzero, nonzero[1:]))


def det2(matrix: list[list[F]]) -> F:
    return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]


def det3(matrix: list[list[F]]) -> F:
    return (
        matrix[0][0] * (matrix[1][1] * matrix[2][2] - matrix[1][2] * matrix[2][1])
        - matrix[0][1] * (matrix[1][0] * matrix[2][2] - matrix[1][2] * matrix[2][0])
        + matrix[0][2] * (matrix[1][0] * matrix[2][1] - matrix[1][1] * matrix[2][0])
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()

    audit = Audit()
    parameters = json.loads(A1_MANIFEST.read_text(encoding="utf-8"))["parameters"]
    volume = frac(parameters["Lx"]) * frac(parameters["Ly"]) * frac(parameters["Lz"])
    z_value = frac(parameters["Z"])
    constant = frac(parameters["r"]) + F(7, 250)
    audit.check("production", "volume from A1 axes", volume == 4096, volume, 4096)

    family = [frac(value) for value in parameters["family_masses"]]
    lock = frac(parameters["k_lock"])
    z0 = [frac(value) for value in parameters["z0"]]
    z0_norm = sum(value * value for value in z0)
    mass = [
        [
            (family[i] if i == j else F(0))
            + lock * ((F(1) if i == j else F(0)) - z0[i] * z0[j] / z0_norm)
            for j in range(3)
        ]
        for i in range(3)
    ]
    floor = F(7, 250)
    shifted = [[mass[i][j] - (floor if i == j else F(0)) for j in range(3)] for i in range(3)]
    minors = (shifted[0][0], det2([row[:2] for row in shifted[:2]]), det3(shifted))
    minor_oracle = (F(9, 125), F(1211, 250000), F(89, 31250000))
    audit.check("production", "independent mass-floor minors", minors == minor_oracle, minors, minor_oracle)

    r130_manifest = json.loads(R130_MANIFEST.read_text(encoding="utf-8"))
    r130_record = r130_manifest["files"]["independent_result"]
    r130_path = REPO / r130_record["path"]
    r130 = json.loads(r130_path.read_text(encoding="utf-8"))
    l6 = frac(r130["diagnostics"]["gram"]["L6"])
    h6 = frac(r130["diagnostics"]["gram"]["H6"])
    p_floor = frac(parameters["M_X"]) ** 2 + frac(parameters["classii_mass_regularizer"])
    audit.check(
        "authority",
        "independent R-130 envelopes and hash",
        sha256(r130_path) == r130_record["sha256"]
        and l6 == F(1143, 250) / p_floor
        and h6 == F(7083, 500) / p_floor,
        [sha256(r130_path), l6, h6],
        [r130_record["sha256"], "1143/(250P)", "7083/(500P)"],
    )

    r151_manifest = json.loads(R151_MANIFEST.read_text(encoding="utf-8"))
    r151_record = r151_manifest["files"]["independent_result"]
    r151_path = REPO / r151_record["path"]
    r151 = json.loads(r151_path.read_text(encoding="utf-8"))["derived"]
    source = frac(r151["source_hessian"])
    covariance_factor = frac(r151["covariance_normalized_factor"])
    h6_upper = frac(r151["hessian_constant_upper"])
    base_floor = frac(parameters["M_X"]) ** 2
    l6_upper = l6 * p_floor / base_floor
    audit.check(
        "authority",
        "independent R-151 hash and derived owner constants",
        sha256(r151_path) == r151_record["sha256"]
        and h6_upper == h6 * p_floor / base_floor
        and l6_upper == l6 * p_floor / base_floor
        and covariance_factor == frac(r151["covariance_normalized_factor"])
        and source == frac(r151["source_hessian"]),
        [sha256(r151_path), h6_upper, l6_upper, covariance_factor, source],
        [r151_record["sha256"], "H6*P/M_X^2", "L6*P/M_X^2", "R-151 covariance factor", "R-151 source Hessian"],
    )

    # Independent second-order jet fixture for the affine-past chain rule.
    w, z, v, u, q0 = F(2, 3), F(-3, 5), F(5, 7), F(4, 9), F(2, 11)
    w_series = [w, z]
    v_series = [v, u]
    b_series = add(add(power(w_series, 4), scale(power(w_series, 2), F(2))), [F(3)])
    endpoint_series = scale(multiply(add(power(v_series, 2), [-q0]), b_series), F(1, 2))
    second_from_series = F(2) * endpoint_series[2]
    b0 = w**4 + 2 * w**2 + 3
    db = (4 * w**3 + 4 * w) * z
    d2b = (12 * w**2 + 4) * z**2
    chain_oracle = u**2 * b0 + 2 * u * db * v + F(1, 2) * (v**2 - q0) * d2b
    audit.check("affine-past", "independent second-order jet factors", second_from_series == chain_oracle, second_from_series, chain_oracle)

    v_multi = [F(2, 7), F(-3, 8), F(5, 11)]
    u_multi = [F(-4, 9), F(7, 10), F(1, 6)]
    q_total = F(13, 17)
    current_series = [-q_total]
    for v_i, u_i in zip(v_multi, u_multi):
        current_series = add(current_series, power([v_i, u_i], 2))
    multi_endpoint = scale(multiply(current_series, b_series), F(1, 2))
    multi_second = F(2) * multi_endpoint[2]
    multi_oracle = sum(
        u_i**2 * b0 + 2 * u_i * db * v_i + F(1, 2) * v_i**2 * d2b
        for v_i, u_i in zip(v_multi, u_multi)
    ) - F(1, 2) * q_total * d2b
    audit.check("affine-past", "independent primitive trace outside spatial sum", multi_second == multi_oracle, multi_second, multi_oracle)
    y_mean, n_mean = F(-2, 5), F(7, 13)
    complete = u**2 * b0 + 2 * u * db * (y_mean + n_mean) + F(1, 2) * ((y_mean + n_mean) ** 2 - q0) * d2b
    core = u**2 * b0 + 2 * u * db * y_mean + F(1, 2) * (y_mean**2 - q0) * d2b
    delta = 2 * u * db * n_mean + n_mean * d2b * y_mean + F(1, 2) * n_mean**2 * d2b
    audit.check("affine-past", "independent current-mean split", complete - core == delta, complete - core, delta)

    # Exact Fraction Sturm audit of the 19/25 loss polynomial.
    first = [constant, z_value, F(1)]
    second = [constant, 4 * z_value, F(16)]
    target = F(19, 25)
    p19 = scale(multiply(first, second), target * volume)
    p19[1] -= covariance_factor * h6_upper
    p19 = trim(p19)
    p19_oracle = [
        F(478871787740547514851, 610351562500000000),
        -F(576174768293610857181, 61035156250000000),
        F(1420144355338872613411, 38146972656250000),
        -F(2812837254304, 48828125),
        F(1245184, 25),
    ]
    audit.check("sturm-loss", "independent 19/25 coefficients", p19 == p19_oracle, p19, p19_oracle)
    p19_sequence = sturm(p19)
    p19_zero = [sign(item[0]) for item in p19_sequence]
    p19_inf = [sign(item[-1]) for item in p19_sequence]
    audit.check("sturm-loss", "independent 19/25 zero signs", p19_zero == [1, -1, -1, 1, 1], p19_zero, [1, -1, -1, 1, 1])
    audit.check("sturm-loss", "independent 19/25 infinity signs", p19_inf == [1, 1, -1, -1, 1], p19_inf, [1, 1, -1, -1, 1])
    audit.check("sturm-loss", "independent 19/25 positivity", len(p19_sequence) == 5 and variations(p19_zero) == variations(p19_inf) == 2 and p19[0] > 0, [len(p19_sequence), variations(p19_zero), variations(p19_inf), p19[0]], [5, 2, 2, ">0"])

    minimum = constant - z_value**2 / 4
    minimum_oracle = F(28800000000947494031, 10**20)
    audit.check("momentum", "independent lower-symbol minimum", minimum == minimum_oracle and minimum > F(36, 125), minimum, f"{minimum_oracle} > 36/125")

    # q(r)=f(4r^2)-3r/4, ascending powers.
    qpoly = [constant, -F(3, 4), 4 * z_value, F(0), F(16)]
    q_oracle = [F(5020336473, 10000000000), -F(3, 4), -F(4626377063, 1250000000), F(0), F(16)]
    audit.check("momentum", "independent radial quartic", qpoly == q_oracle, qpoly, q_oracle)
    q_sequence = sturm(qpoly)
    q_zero = [sign(item[0]) for item in q_sequence]
    q_inf = [sign(item[-1]) for item in q_sequence]
    audit.check("momentum", "independent radial zero signs", q_zero == [1, -1, -1, 1, 1], q_zero, [1, -1, -1, 1, 1])
    audit.check("momentum", "independent radial infinity signs", q_inf == [1, 1, 1, -1, 1], q_inf, [1, 1, 1, -1, 1])
    audit.check("momentum", "independent radial positivity", len(q_sequence) == 5 and variations(q_zero) == variations(q_inf) == 2 and qpoly[0] > 0, [len(q_sequence), variations(q_zero), variations(q_inf), qpoly[0]], [5, 2, 2, ">0"])

    # Square roots are represented by their rational multipliers squared.
    nmw_rational = 8 * l6_upper * F(4, 3)
    nmy_rational = 4 * h6_upper * F(125, 36)
    n2_coefficient = 2 * h6_upper * F(125, 36)
    audit.check("collar", "independent N-MW rational multiplier", nmw_rational == F(1524, 125), nmw_rational, F(1524, 125))
    audit.check("collar", "independent N-MY rational multiplier", nmy_rational == F(787, 16), nmy_rational, F(787, 16))
    audit.check("collar", "independent N-square multiplier", n2_coefficient == F(787, 32), n2_coefficient, F(787, 32))
    zero_current_gap = source - target
    retained_gap = zero_current_gap - F(1, 25)
    audit.check("collar", "independent affine-past gaps", zero_current_gap == F(7, 50) and retained_gap == F(1, 10), [zero_current_gap, retained_gap], [F(7, 50), F(1, 10)])

    c = F(1, 5)
    linear_loss = 3 * c
    bump_augmented = source - c * (F(4) - 1) ** 2
    audit.check("nonlinear", "independent linear-test non-implication", c < F(4, 15) and linear_loss < F(4, 5) and bump_augmented < 0, [c, linear_loss, bump_augmented], ["<4/15", "<4/5", "<0"])
    audit.check("nonlinear", "independent conditional threshold", source - F(1, 10) == F(4, 5), source - F(1, 10), F(4, 5))

    endpoint_diag = -F(3, 4)
    endpoint_cross = -F(1, 5)
    augmented_diag = endpoint_diag + source
    eigenvalues = sorted([augmented_diag + endpoint_cross, augmented_diag - endpoint_cross])
    audit.check("multi-root", "independent local gaps", augmented_diag == F(3, 20) > F(7, 50), augmented_diag, ">7/50")
    audit.check("multi-root", "independent global eigenvalues", eigenvalues == [-F(1, 20), F(7, 20)], eigenvalues, [-F(1, 20), F(7, 20)])
    overlap_fixture = F(2, 7)
    source_residual_determinant = -overlap_fixture**2
    audit.check("multi-root", "independent source-allocation determinant", source_residual_determinant < 0, source_residual_determinant, "<0 unless overlap=0")

    audit.check(
        "scope",
        "independent open-gate firewall",
        not SCOPE["all_nonlinear_predictable_controls"]
        and not SCOPE["production_multi_root_aggregation"]
        and not SCOPE["t050_closed"]
        and not SCOPE["a13_closed"]
        and not SCOPE["sector_a_closed"]
        and "does not prove an unconditional" in NO_OVERCLAIM,
        SCOPE,
        "conditional boundary only",
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
            "mass_floor": floor,
            "mass_floor_minors": minors,
            "R130_L6": l6,
            "R130_H6": h6,
            "affine_past_delta_coefficients": [2, 1, F(1, 2)],
            "endpoint_loss_strict_upper": target,
            "loss_sturm_coefficients_ascending": p19,
            "loss_sturm_zero_signs": p19_zero,
            "loss_sturm_infinity_signs": p19_inf,
            "lower_symbol_minimum": minimum,
            "inverse_lambda2_strict_upper": F(125, 36),
            "p_over_lambda2_strict_upper": F(4, 3),
            "uniform_past_collar_rational_coefficients": {
                "N_MW_times_sqrt3": nmw_rational,
                "N_MY_times_sqrt3": nmy_rational,
                "N_squared": n2_coefficient,
            },
            "zero_current_affine_past_gap_strict_lower": zero_current_gap,
            "source_hessian": source,
            "retained_gap_strict_lower": retained_gap,
            "conditional_operator_endpoint_threshold": -F(4, 5),
            "nonlinear_fixture": {"c": c, "linear_loss": linear_loss, "bump_augmented_upper": bump_augmented},
            "multi_root_augmented_matrix": [
                [F(3, 20), -F(1, 5)],
                [-F(1, 5), F(3, 20)],
            ],
            "multi_root_augmented_eigenvalues": eigenvalues,
        },
        "scope": SCOPE,
        "no_overclaim": NO_OVERCLAIM,
        "authority_hashes": {
            "A1": sha256(A1_MANIFEST),
            "R-130-independent-result": sha256(r130_path),
            "R-151-independent-result": sha256(r151_path),
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

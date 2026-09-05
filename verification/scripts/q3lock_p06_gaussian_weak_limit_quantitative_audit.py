#!/usr/bin/env python3
"""Quantitative fixed-volume Gaussian weak-limit audit for Q3LOCK P-06.

The script checks the explicit covariance error, interpolation, increment,
Fourier-tail, and Young-inequality constants used in the accompanying
analytic audit.  The finite fixtures are regression evidence for the proof
text; they do not replace the analytic proof or external review.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import tempfile
from pathlib import Path
from typing import Any


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = REPO / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-05-q3lock-p06-gaussian-weak-limit-quantitative-audit/result.json"
)


def normalized_sha256(path: Path) -> str:
    return hashlib.sha256(
        path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    ).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
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

    def check(
        self, name: str, condition: bool, actual: Any, expected: Any, group: str
    ) -> None:
        if not condition:
            raise AssertionError(f"{group}: {name}: {actual!r} != {expected!r}")
        self.rows.append(
            {
                "name": name,
                "group": group,
                "status": "PASS",
                "actual": str(actual),
                "expected": str(expected),
            }
        )


def least_representatives(n_sites: int) -> range:
    if n_sites < 4 or n_sites % 2:
        raise ValueError("N must be even and at least four")
    return range(-(n_sites // 2) + 1, n_sites // 2 + 1)


def finite_denominator(
    beta: float, mass: float, rigidity: float, n_sites: int, mode: int
) -> float:
    epsilon = beta / n_sites
    return rigidity + (4.0 * mass / epsilon**2) * math.sin(
        math.pi * mode / n_sites
    ) ** 2


def continuum_denominator(
    beta: float, mass: float, rigidity: float, mode: int
) -> float:
    return rigidity + 4.0 * math.pi**2 * mass * mode**2 / beta**2


def grid_covariance(
    beta: float, mass: float, rigidity: float, n_sites: int, separation: int
) -> float:
    return math.fsum(
        math.cos(2.0 * math.pi * mode * separation / n_sites)
        / finite_denominator(beta, mass, rigidity, n_sites, mode)
        for mode in least_representatives(n_sites)
    ) / beta


def continuum_covariance(
    beta: float, mass: float, rigidity: float, tau: float
) -> float:
    distance = tau % beta
    distance = min(distance, beta - distance)
    frequency = math.sqrt(rigidity / mass)
    return math.cosh(frequency * (beta / 2.0 - distance)) / (
        2.0
        * math.sqrt(rigidity * mass)
        * math.sinh(frequency * beta / 2.0)
    )


def diagonal_bound(beta: float, mass: float, rigidity: float) -> float:
    return 1.0 / (beta * rigidity) + beta / (12.0 * mass)


def grid_covariance_error_bound(beta: float, mass: float, n_sites: int) -> float:
    coefficient = math.pi**2 / 48.0 + 3.0 / (2.0 * math.pi**2)
    return beta * coefficient / (mass * n_sites)


def interpolation_error_bound(
    beta: float, mass: float, rigidity: float, n_sites: int
) -> float:
    epsilon = beta / n_sites
    return grid_covariance_error_bound(beta, mass, n_sites) + math.sqrt(
        2.0 * diagonal_bound(beta, mass, rigidity) * epsilon / mass
    )


def interpolation_weights(beta: float, n_sites: int, tau: float) -> tuple[tuple[int, float], ...]:
    epsilon = beta / n_sites
    reduced = tau % beta
    left = min(int(math.floor(reduced / epsilon)), n_sites - 1)
    theta = (reduced - left * epsilon) / epsilon
    if theta <= 4.0 * math.ulp(1.0):
        return ((left, 1.0),)
    return ((left, 1.0 - theta), ((left + 1) % n_sites, theta))


def interpolated_covariance(
    beta: float,
    mass: float,
    rigidity: float,
    n_sites: int,
    tau: float,
    sigma: float,
) -> float:
    return math.fsum(
        left_weight
        * right_weight
        * grid_covariance(
            beta, mass, rigidity, n_sites, (left_index - right_index) % n_sites
        )
        for left_index, left_weight in interpolation_weights(beta, n_sites, tau)
        for right_index, right_weight in interpolation_weights(beta, n_sites, sigma)
    )


def interpolated_increment_variance(
    beta: float,
    mass: float,
    rigidity: float,
    n_sites: int,
    tau: float,
    sigma: float,
) -> float:
    left = interpolated_covariance(
        beta, mass, rigidity, n_sites, tau, tau
    )
    right = interpolated_covariance(
        beta, mass, rigidity, n_sites, sigma, sigma
    )
    cross = interpolated_covariance(
        beta, mass, rigidity, n_sites, tau, sigma
    )
    return max(0.0, left + right - 2.0 * cross)


def circle_distance(beta: float, tau: float, sigma: float) -> float:
    difference = abs((tau - sigma) % beta)
    return min(difference, beta - difference)


def missing_reciprocal_square_sum(n_sites: int) -> float:
    modes = least_representatives(n_sites)
    retained = math.fsum(1.0 / mode**2 for mode in modes if mode != 0)
    return math.pi**2 / 3.0 - retained


def young_constant(linear_coefficient: float, delta: float) -> float:
    return (
        3.0
        * linear_coefficient ** (4.0 / 3.0)
        / (4.0 * (4.0 * delta) ** (1.0 / 3.0))
    )


def build_payload() -> dict[str, Any]:
    audit = Audit()
    parameter_sets = (
        (2.5, 1.5, 1.75),
        (1.25, 0.8, 2.2),
        (4.0, 2.5, 0.9),
    )
    meshes = (8, 16, 32, 64, 128)
    tolerance = 3.0e-12  # tooling tolerance, not an analytic error bar

    fourier_inequality_rows: list[dict[str, Any]] = []
    for n_sites in meshes:
        for mode in range(1, n_sites // 2 + 1):
            x_value = math.pi * mode / n_sites
            gap = x_value**2 - math.sin(x_value) ** 2
            upper = x_value**4 / 3.0
            audit.check(
                "sine-square fourth-order remainder",
                gap <= upper + tolerance,
                gap,
                f"<={upper}",
                "fourier_inequality",
            )
            audit.check(
                "sine chord lower bound",
                math.sin(x_value) + tolerance >= 2.0 * mode / n_sites,
                math.sin(x_value),
                f">={2.0 * mode / n_sites}",
                "fourier_inequality",
            )
            fourier_inequality_rows.append(
                {"N": n_sites, "mode": mode, "gap": gap, "upper": upper}
            )

    hostile_n = 1024
    hostile_x = math.pi / hostile_n
    hostile_gap = hostile_x**2 - math.sin(hostile_x) ** 2
    hostile_upper = hostile_x**4 / 4.0
    audit.check(
        "hostile one-quarter remainder coefficient is rejected",
        hostile_gap > hostile_upper,
        hostile_gap,
        f">{hostile_upper}",
        "hostile",
    )

    tail_rows: list[dict[str, Any]] = []
    for n_sites in meshes:
        missing = missing_reciprocal_square_sum(n_sites)
        upper = 6.0 / n_sites
        audit.check(
            "missing Fourier reciprocal-square tail",
            missing <= upper + tolerance,
            missing,
            f"<={upper}",
            "fourier_tail",
        )
        tail_rows.append({"N": n_sites, "missing": missing, "upper": upper})

    grid_rows: list[dict[str, Any]] = []
    interpolation_rows: list[dict[str, Any]] = []
    increment_rows: list[dict[str, Any]] = []
    for beta, mass, rigidity in parameter_sets:
        for n_sites in meshes:
            epsilon = beta / n_sites
            grid_bound = grid_covariance_error_bound(beta, mass, n_sites)
            maximum_grid_error = 0.0
            for separation in range(n_sites):
                actual = grid_covariance(
                    beta, mass, rigidity, n_sites, separation
                )
                target = continuum_covariance(
                    beta, mass, rigidity, separation * epsilon
                )
                error = abs(actual - target)
                maximum_grid_error = max(maximum_grid_error, error)
                audit.check(
                    "uniform grid covariance error",
                    error <= grid_bound + tolerance,
                    error,
                    f"<={grid_bound}",
                    "grid_covariance",
                )
            grid_rows.append(
                {
                    "beta": beta,
                    "mass": mass,
                    "rigidity": rigidity,
                    "N": n_sites,
                    "maximum_error": maximum_grid_error,
                    "analytic_bound": grid_bound,
                }
            )

            interpolation_bound = interpolation_error_bound(
                beta, mass, rigidity, n_sites
            )
            probes = tuple(beta * index / 17.0 for index in range(17))
            maximum_interpolation_error = 0.0
            maximum_increment_ratio = 0.0
            for tau in probes:
                for sigma in probes:
                    actual = interpolated_covariance(
                        beta, mass, rigidity, n_sites, tau, sigma
                    )
                    target = continuum_covariance(
                        beta, mass, rigidity, tau - sigma
                    )
                    error = abs(actual - target)
                    maximum_interpolation_error = max(
                        maximum_interpolation_error, error
                    )
                    audit.check(
                        "interpolated covariance error",
                        error <= interpolation_bound + tolerance,
                        error,
                        f"<={interpolation_bound}",
                        "interpolated_covariance",
                    )
                    distance = circle_distance(beta, tau, sigma)
                    if distance > tolerance:
                        variance = interpolated_increment_variance(
                            beta, mass, rigidity, n_sites, tau, sigma
                        )
                        increment_bound = 14.0 * distance / mass
                        maximum_increment_ratio = max(
                            maximum_increment_ratio,
                            variance * mass / distance,
                        )
                        audit.check(
                            "arbitrary-time increment variance",
                            variance <= increment_bound + tolerance,
                            variance,
                            f"<={increment_bound}",
                            "increment_tightness",
                        )
                        scalar_fourth = 3.0 * variance**2
                        fourth_bound = 3.0 * increment_bound**2
                        audit.check(
                            "scalar Gaussian fourth moment",
                            scalar_fourth <= fourth_bound + tolerance,
                            scalar_fourth,
                            f"<={fourth_bound}",
                            "increment_tightness",
                        )
            interpolation_rows.append(
                {
                    "beta": beta,
                    "mass": mass,
                    "rigidity": rigidity,
                    "N": n_sites,
                    "maximum_error": maximum_interpolation_error,
                    "analytic_bound": interpolation_bound,
                }
            )
            increment_rows.append(
                {
                    "beta": beta,
                    "mass": mass,
                    "rigidity": rigidity,
                    "N": n_sites,
                    "maximum_variance_ratio": maximum_increment_ratio,
                    "analytic_ratio_bound": 14.0,
                }
            )

    for parameter_index in range(len(parameter_sets)):
        subset = interpolation_rows[
            parameter_index * len(meshes) : (parameter_index + 1) * len(meshes)
        ]
        audit.check(
            "interpolation covariance refinement improves",
            subset[-1]["maximum_error"] < subset[0]["maximum_error"],
            subset[-1]["maximum_error"],
            f"<{subset[0]['maximum_error']}",
            "convergence_diagnostic",
        )

    young_rows: list[dict[str, Any]] = []
    for linear_coefficient, delta in ((0.7, 0.15), (2.0, 0.4), (5.5, 1.25)):
        optimum = (linear_coefficient / (4.0 * delta)) ** (1.0 / 3.0)
        maximum = linear_coefficient * optimum - delta * optimum**4
        constant = young_constant(linear_coefficient, delta)
        audit.check(
            "quartic Young constant at optimizer",
            math.isclose(maximum, constant, rel_tol=2.0e-14, abs_tol=tolerance),
            maximum,
            constant,
            "young_uniform_integrability",
        )
        audit.check(
            "hostile shrunken Young constant is rejected",
            maximum > 0.99 * constant,
            maximum,
            f">{0.99 * constant}",
            "hostile",
        )
        young_rows.append(
            {
                "linear_coefficient": linear_coefficient,
                "delta": delta,
                "optimizer": optimum,
                "maximum": maximum,
                "constant": constant,
            }
        )

    script_path = Path(__file__).resolve()
    return {
        "schema": "tect/q3lock-p06-gaussian-weak-limit-quantitative-audit/0.1",
        "script_version": __version__,
        "result_id": "R-501",
        "exploration_id": "EXP-001586",
        "authority_chain": ["EXP-000780", "EXP-000781", "EXP-000782"],
        "claim_bearing": False,
        "diagnostic_fixture_not_external_proof": True,
        "assertions": {
            "passed": len(audit.rows),
            "total": len(audit.rows),
            "rows": audit.rows,
        },
        "parameters": {
            "parameter_sets": parameter_sets,
            "meshes": meshes,
            "comparison_tolerance": tolerance,
        },
        "derived": {
            "grid_error_coefficient": math.pi**2 / 48.0
            + 3.0 / (2.0 * math.pi**2),
            "increment_ratio_bound": 14.0,
            "fourier_inequality_rows": fourier_inequality_rows,
            "tail_rows": tail_rows,
            "grid_rows": grid_rows,
            "interpolation_rows": interpolation_rows,
            "increment_rows": increment_rows,
            "young_rows": young_rows,
        },
        "files": {
            "script": str(script_path.relative_to(REPO)).replace("\\", "/"),
            "script_sha256": normalized_sha256(script_path),
        },
        "verdict": "PASS",
        "boundary": (
            "Quantitative fixed-volume Gaussian covariance, interpolation, "
            "tightness and quartic-Young diagnostics only. The accompanying "
            "analytic proof remains subject to independent mathematical review. "
            "No spatial W_t limit, FKG, FSS, pressure, phase, DLR, claim "
            "promotion, manuscript or PDF theorem is certified."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    atomic_json(args.output, payload)
    summary = payload["assertions"]
    print(f"EXP-001586 PASS {summary['passed']}/{summary['total']}")
    print(args.output)


if __name__ == "__main__":
    main()

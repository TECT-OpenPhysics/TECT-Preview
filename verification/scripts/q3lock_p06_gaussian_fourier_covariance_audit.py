#!/usr/bin/env python3
"""Finite Fourier and cyclic-resistance audit for the Q3LOCK P-06 route.

The verifier checks the frozen massive periodic Gaussian convention, the
csc-squared and cyclic-resistance identities, the discrete Fourier
reindexing, the high-mode bound, finite covariance refinement, and the exact
source integral of periodic linear interpolation.  It is diagnostic evidence
at fixed spatial volume; it does not prove a weak loop limit or a
thermodynamic theorem.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT = REPO / (
    "claims/C6-SPACETIME-SIGNATURE/runs/"
    "2026-09-05-q3lock-p06-gaussian-fourier-covariance-audit/result.json"
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


def epsilon(beta: float, n_sites: int) -> float:
    return beta / n_sites


def precision(beta: float, m: float, a: float, n_sites: int, mode: int) -> float:
    step = epsilon(beta, n_sites)
    return (4.0 * m / step) * math.sin(math.pi * mode / n_sites) ** 2 + a * step


def covariance(beta: float, m: float, a: float, n_sites: int, separation: int) -> float:
    return sum(
        math.cos(2.0 * math.pi * mode * separation / n_sites)
        / precision(beta, m, a, n_sites, mode)
        for mode in range(n_sites)
    ) / n_sites


def least_representative_modes(n_sites: int) -> range:
    if n_sites % 2:
        raise ValueError("the audit uses even time meshes")
    return range(-(n_sites // 2) + 1, n_sites // 2 + 1)


def reindexed_covariance(
    beta: float, m: float, a: float, n_sites: int, separation: int
) -> float:
    step = epsilon(beta, n_sites)
    return sum(
        math.cos(2.0 * math.pi * mode * separation / n_sites)
        / (a + (4.0 * m / step**2) * math.sin(math.pi * mode / n_sites) ** 2)
        for mode in least_representative_modes(n_sites)
    ) / beta


def continuum_covariance(beta: float, m: float, a: float, tau: float) -> float:
    distance = tau % beta
    distance = min(distance, beta - distance)
    omega = math.sqrt(a / m)
    return math.cosh(omega * (beta / 2.0 - distance)) / (
        2.0 * math.sqrt(a * m) * math.sinh(omega * beta / 2.0)
    )


def truncated_continuum_fourier(
    beta: float, m: float, a: float, tau: float, cutoff: int
) -> float:
    return sum(
        math.cos(2.0 * math.pi * mode * tau / beta)
        / (a + 4.0 * math.pi**2 * m * mode**2 / beta**2)
        for mode in range(-cutoff, cutoff + 1)
    ) / beta


def interpolated_cell_integral(
    values: tuple[Fraction, ...], beta: Fraction
) -> Fraction:
    step = beta / len(values)
    return sum(
        step * (values[index] + values[(index + 1) % len(values)]) / 2
        for index in range(len(values))
    )


def build_payload() -> dict[str, Any]:
    audit = Audit()
    beta = 2.5
    mass = 1.5
    harmonic_mass = 1.75
    tolerance = 2.0e-10
    tight_tolerance = 1.0e-5  # diagnostic threshold, not an analytic error bound

    csc_rows: list[dict[str, float | int]] = []
    for n_sites in (4, 6, 8, 12, 16, 24, 32):
        lhs = sum(
            1.0 / math.sin(math.pi * mode / n_sites) ** 2
            for mode in range(1, n_sites)
        )
        rhs = (n_sites**2 - 1) / 3.0
        audit.check(
            "csc-squared identity",
            math.isclose(lhs, rhs, rel_tol=tolerance, abs_tol=tolerance),
            lhs,
            rhs,
            "csc_identity",
        )
        csc_rows.append({"N": n_sites, "lhs": lhs, "rhs": rhs})

    diagonal_rows: list[dict[str, float | int]] = []
    diagonal_bound = 1.0 / (beta * harmonic_mass) + beta / (12.0 * mass)
    for n_sites in (4, 8, 16, 32, 64, 128):
        step = epsilon(beta, n_sites)
        zero_mode = (1.0 / n_sites) / (harmonic_mass * step)
        audit.check(
            "zero-mode contribution",
            math.isclose(
                zero_mode,
                1.0 / (beta * harmonic_mass),
                rel_tol=tolerance,
                abs_tol=tolerance,
            ),
            zero_mode,
            1.0 / (beta * harmonic_mass),
            "diagonal_bound",
        )
        diagonal = covariance(beta, mass, harmonic_mass, n_sites, 0)
        audit.check(
            "mesh-uniform diagonal covariance bound",
            diagonal <= diagonal_bound + tolerance,
            diagonal,
            diagonal_bound,
            "diagonal_bound",
        )
        diagonal_rows.append(
            {
                "N": n_sites,
                "zero_mode": zero_mode,
                "diagonal": diagonal,
                "bound": diagonal_bound,
            }
        )

    reindex_rows: list[dict[str, float | int]] = []
    for n_sites in (12, 24, 48, 96):
        for separation in (0, 1, n_sites // 3, n_sites // 2):
            direct = covariance(beta, mass, harmonic_mass, n_sites, separation)
            reindexed = reindexed_covariance(
                beta, mass, harmonic_mass, n_sites, separation
            )
            audit.check(
                "least-representative Fourier reindexing",
                math.isclose(direct, reindexed, rel_tol=tolerance, abs_tol=tolerance),
                direct,
                reindexed,
                "fourier_reindex",
            )
            reindex_rows.append(
                {
                    "N": n_sites,
                    "r": separation,
                    "direct": direct,
                    "reindexed": reindexed,
                }
            )

    tau = beta / 3.0
    continuum_target = continuum_covariance(beta, mass, harmonic_mass, tau)
    refinement_rows: list[dict[str, float | int]] = []
    refinement_errors: list[float] = []
    for n_sites in (12, 24, 48, 96, 192, 384):
        separation = n_sites // 3
        finite_value = covariance(beta, mass, harmonic_mass, n_sites, separation)
        error = abs(finite_value - continuum_target)
        refinement_errors.append(error)
        refinement_rows.append(
            {
                "N": n_sites,
                "r": separation,
                "finite": finite_value,
                "continuum": continuum_target,
                "absolute_error": error,
            }
        )
    audit.check(
        "finite covariance refinement improves",
        refinement_errors[-1] < refinement_errors[0],
        refinement_errors[-1],
        "< initial error",
        "covariance_refinement",
    )
    audit.check(
        "high-resolution covariance is close to closed form",
        refinement_errors[-1] < tight_tolerance,
        refinement_errors[-1],
        f"<{tight_tolerance}",
        "covariance_refinement",
    )

    fourier_rows: list[dict[str, float | int]] = []
    fourier_errors: list[float] = []
    for cutoff in (4, 8, 16, 32, 64, 128):
        finite_sum = truncated_continuum_fourier(
            beta, mass, harmonic_mass, tau, cutoff
        )
        error = abs(finite_sum - continuum_target)
        fourier_errors.append(error)
        fourier_rows.append(
            {
                "cutoff": cutoff,
                "truncated": finite_sum,
                "closed_form": continuum_target,
                "absolute_error": error,
            }
        )
    audit.check(
        "continuous Fourier truncation improves",
        fourier_errors[-1] < fourier_errors[0],
        fourier_errors[-1],
        "< initial error",
        "fourier_tail",
    )
    audit.check(
        "continuous Fourier truncation reaches diagnostic tolerance",
        fourier_errors[-1] < tight_tolerance,
        fourier_errors[-1],
        f"<{tight_tolerance}",
        "fourier_tail",
    )

    high_mode_rows: list[dict[str, float | int]] = []
    for n_sites in (8, 16, 32, 64):
        step = epsilon(beta, n_sites)
        for mode in range(1, n_sites // 2 + 1):
            sine = math.sin(math.pi * mode / n_sites)
            sine_lower = 2.0 * mode / n_sites
            lhs = 1.0 / (harmonic_mass + (4.0 * mass / step**2) * sine**2)
            rhs = beta**2 / (16.0 * mass * mode**2)
            audit.check(
                "sine lower bound for high modes",
                sine + tolerance >= sine_lower,
                sine,
                f">={sine_lower}",
                "high_mode",
            )
            audit.check(
                "n^-2 Fourier majorant",
                lhs <= rhs + tolerance,
                lhs,
                f"<={rhs}",
                "high_mode",
            )
            high_mode_rows.append(
                {
                    "N": n_sites,
                    "n": mode,
                    "sine": sine,
                    "sine_lower": sine_lower,
                    "term": lhs,
                    "majorant": rhs,
                }
            )

    resistance_rows: list[dict[str, float | int]] = []
    for n_sites in (4, 6, 8, 12, 16, 24):
        for separation in range(1, n_sites):
            resistance = sum(
                (1.0 - math.cos(2.0 * math.pi * mode * separation / n_sites))
                / math.sin(math.pi * mode / n_sites) ** 2
                for mode in range(1, n_sites)
            )
            expected = 2.0 * separation * (n_sites - separation)
            audit.check(
                "cyclic resistance identity",
                math.isclose(
                    resistance, expected, rel_tol=tolerance, abs_tol=tolerance
                ),
                resistance,
                expected,
                "resistance",
            )
            resistance_rows.append(
                {"N": n_sites, "r": separation, "lhs": resistance, "rhs": expected}
            )

    increment_rows: list[dict[str, float | int]] = []
    for n_sites in (8, 16, 32, 64):
        step = epsilon(beta, n_sites)
        for separation in (1, n_sites // 3, n_sites // 2):
            variance = (
                2.0
                / n_sites
                * sum(
                    (1.0 - math.cos(2.0 * math.pi * mode * separation / n_sites))
                    / precision(beta, mass, harmonic_mass, n_sites, mode)
                    for mode in range(n_sites)
                )
            )
            exact_bound = (
                step * separation * (n_sites - separation) / (mass * n_sites)
            )
            simple_bound = step * min(separation, n_sites - separation) / mass
            audit.check(
                "increment variance below resistance bound",
                variance <= exact_bound + tolerance,
                variance,
                f"<={exact_bound}",
                "increment",
            )
            audit.check(
                "resistance bound below simple increment bound",
                exact_bound <= simple_bound + tolerance,
                exact_bound,
                f"<={simple_bound}",
                "increment",
            )
            increment_rows.append(
                {
                    "N": n_sites,
                    "r": separation,
                    "variance": variance,
                    "exact_bound": exact_bound,
                    "simple_bound": simple_bound,
                }
            )

    fourth_rows: list[dict[str, float | int]] = []
    for row in diagonal_rows:
        gaussian_fourth = 3.0 * float(row["diagonal"]) ** 2
        fourth_bound = 3.0 * diagonal_bound**2
        audit.check(
            "Gaussian fourth moment envelope",
            gaussian_fourth <= fourth_bound + tolerance,
            gaussian_fourth,
            fourth_bound,
            "gaussian_moment",
        )
        fourth_rows.append(
            {
                "N": int(row["N"]),
                "fourth_moment": gaussian_fourth,
                "bound": fourth_bound,
            }
        )

    rational_beta = Fraction(5, 2)
    rational_values = (
        Fraction(-3),
        Fraction(1, 2),
        Fraction(4),
        Fraction(-2),
        Fraction(3, 2),
        Fraction(0),
    )
    interpolated_integral = interpolated_cell_integral(rational_values, rational_beta)
    vertex_sum = rational_beta / len(rational_values) * sum(rational_values)
    audit.check(
        "periodic interpolation source integral is exact",
        interpolated_integral == vertex_sum,
        interpolated_integral,
        vertex_sum,
        "source_interpolation",
    )
    constant_values = tuple(Fraction(7, 3) for _ in rational_values)
    constant_integral = interpolated_cell_integral(constant_values, rational_beta)
    audit.check(
        "constant interpolation integral",
        constant_integral == rational_beta * constant_values[0],
        constant_integral,
        rational_beta * constant_values[0],
        "source_interpolation",
    )

    script_path = Path(__file__).resolve()
    return {
        "schema": "tect/q3lock-p06-gaussian-fourier-covariance-audit/0.1",
        "script_version": __version__,
        "result_id": "R-500",
        "exploration_id": "EXP-001584",
        "authority_chain": ["EXP-000780", "EXP-000781", "EXP-000782"],
        "claim_bearing": False,
        "diagnostic_fixture_not_proof": True,
        "assertions": {
            "passed": len(audit.rows),
            "total": len(audit.rows),
            "rows": audit.rows,
        },
        "parameters": {
            "beta": beta,
            "mass": mass,
            "harmonic_mass": harmonic_mass,
            "comparison_tolerance": tolerance,
            "tight_tolerance": tight_tolerance,
        },
        "derived": {
            "diagonal_bound": diagonal_bound,
            "csc_rows": csc_rows,
            "diagonal_rows": diagonal_rows,
            "reindex_rows": reindex_rows,
            "continuum_target": continuum_target,
            "refinement_rows": refinement_rows,
            "fourier_rows": fourier_rows,
            "high_mode_rows": high_mode_rows,
            "resistance_rows": resistance_rows,
            "increment_rows": increment_rows,
            "fourth_rows": fourth_rows,
            "source_interpolation": {
                "integral": str(interpolated_integral),
                "vertex_sum": str(vertex_sum),
            },
        },
        "files": {
            "script": str(script_path.relative_to(REPO)).replace("\\", "/"),
            "script_sha256": normalized_sha256(script_path),
        },
        "verdict": "PASS",
        "boundary": (
            "Finite Fourier, cyclic-resistance, covariance-refinement and "
            "interpolation diagnostics only. No analytic Gaussian weak-limit, "
            "weighted loop, pressure, FKG, phase, DLR, claim promotion, "
            "manuscript or PDF theorem is certified."
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    atomic_json(args.output, payload)
    summary = payload["assertions"]
    print(f"EXP-001584 PASS {summary['passed']}/{summary['total']}")
    print(args.output)


if __name__ == "__main__":
    main()

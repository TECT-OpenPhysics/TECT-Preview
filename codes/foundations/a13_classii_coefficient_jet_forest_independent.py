#!/usr/bin/env python3
"""Independent Hermite and parity audit for the A13 jet forest theorem.

This implementation does not import the primary verifier. It recovers the
forest coefficients by Gaussian-Hermite projection and separately checks the
sharp-cube partition and common-even cancellation.
"""

from __future__ import annotations

import argparse
import functools
import hashlib
import itertools
import json
import math
import os
import platform
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

import numpy as np
from numpy.polynomial.hermite_e import hermegauss

__version__ = "1.0.0"
__first_issued__ = "2026-07-22"
__version_issued__ = "2026-07-22"

REPO = Path(__file__).resolve().parents[2]
CLAIM = REPO / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
DEFAULT_MANIFEST = CLAIM / "classii_coefficient_jet_forest_manifest.json"
DEFAULT_OUTPUT = (
    CLAIM
    / "runs"
    / "2026-07-22-independent-coefficient-jet-forest-classification"
    / "result.json"
)
SECTORS = ("LOW_HIGH", "RESONANT", "HIGH_LOW")


def digest(path: Path) -> str:
    value = hashlib.sha256()
    value.update(path.read_bytes())
    return value.hexdigest()


def git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=REPO,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "UNKNOWN"


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name, suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise


def add(
    rows: list[dict[str, Any]],
    name: str,
    passed: bool,
    actual: Any,
    expected: Any,
) -> None:
    rows.append(
        {
            "name": name,
            "status": "PASS" if bool(passed) else "FAIL",
            "actual": actual,
            "expected": expected,
        }
    )


def hermite(degree: int, values: np.ndarray) -> np.ndarray:
    if degree == 0:
        return np.ones_like(values)
    if degree == 1:
        return values.copy()
    lower = np.ones_like(values)
    current = values.copy()
    for index in range(1, degree):
        lower, current = current, values * current - index * lower
    return current


def project_coefficients(
    polynomial: Callable[[np.ndarray], np.ndarray], order: int, maximum_degree: int
) -> dict[int, float]:
    nodes, weights = hermegauss(order)
    normalization = math.sqrt(2.0 * math.pi)
    values = polynomial(nodes)
    return {
        degree: float(
            np.sum(weights * values * hermite(degree, nodes))
            / normalization
            / math.factorial(degree)
        )
        for degree in range(maximum_degree + 1)
    }


def dyadic_level(mode: tuple[int, int, int]) -> int:
    radius = max(map(abs, mode))
    return 0 if radius <= 1 else int(math.ceil(math.log2(radius)))


def sector(left: tuple[int, int, int], right: tuple[int, int, int]) -> str:
    gap = dyadic_level(left) - dyadic_level(right)
    if gap <= -2:
        return "LOW_HIGH"
    if gap >= 2:
        return "HIGH_LOW"
    return "RESONANT"


def mode_cube(cutoff: int) -> list[tuple[int, int, int]]:
    return list(itertools.product(range(-cutoff, cutoff + 1), repeat=3))


def negate(mode: tuple[int, int, int]) -> tuple[int, int, int]:
    return tuple(-value for value in mode)


def covariance_builder(parameters: dict[str, Any]):
    length = float(parameters["Lx"])
    wave_factor = 2.0 * math.pi / length
    mode_measure = length**-3
    z0 = np.asarray(parameters["z0"], dtype=np.float64)
    projector = np.outer(z0, z0) / float(z0 @ z0)
    base_matrix = (
        np.diag(np.asarray(parameters["family_masses"], dtype=np.float64))
        + float(parameters["k_lock"]) * (np.eye(3) - projector)
    )

    @functools.lru_cache(maxsize=None)
    def covariance(mode: tuple[int, int, int]) -> np.ndarray:
        squared = wave_factor**2 * sum(value * value for value in mode)
        scalar = (
            float(parameters["r"])
            + float(parameters["Z"]) * squared
            + float(parameters["Y"]) * squared**2
        )
        complex_covariance = np.linalg.solve(
            scalar * np.eye(3) + base_matrix, np.eye(3)
        )
        zero = np.zeros_like(complex_covariance)
        return 0.5 * mode_measure * np.block(
            [[complex_covariance, zero], [zero, complex_covariance]]
        )

    return covariance, wave_factor


def run(manifest_path: Path, output_path: Path) -> int:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    audit = manifest["independent_audit"]
    tolerance = float(audit["tolerance"])
    rows: list[dict[str, Any]] = []

    a1_path = REPO / manifest["authority"]["a1_manifest"]["path"]
    a1 = json.loads(a1_path.read_text(encoding="utf-8"))
    covariance, wave_factor = covariance_builder(a1["parameters"])

    polynomials: dict[str, tuple[Callable[[np.ndarray], np.ndarray], dict[int, float]]] = {
        "x_h2": (lambda x: x * hermite(2, x), {1: 2.0, 3: 1.0}),
        "h2_h2": (lambda x: hermite(2, x) ** 2, {0: 2.0, 2: 4.0, 4: 1.0}),
        "x2_h2": (lambda x: x**2 * hermite(2, x), {0: 2.0, 2: 5.0, 4: 1.0}),
        "x_h3": (lambda x: x * hermite(3, x), {2: 3.0, 4: 1.0}),
    }
    projections: dict[str, dict[str, float]] = {}
    for name, (polynomial, expected) in polynomials.items():
        coefficients = project_coefficients(
            polynomial, int(audit["hermite_order"]), int(audit["maximum_degree"])
        )
        projections[name] = {str(key): value for key, value in coefficients.items()}
        for degree in range(int(audit["maximum_degree"]) + 1):
            target = expected.get(degree, 0.0)
            add(
                rows,
                f"hermite_{name}_degree_{degree}",
                abs(coefficients[degree] - target) < tolerance,
                coefficients[degree],
                target,
            )

    points = np.asarray(audit["pointwise_points"], dtype=np.float64)
    identities = {
        "first_2_cross": points * hermite(2, points) - hermite(3, points) - 2.0 * hermite(1, points),
        "centered_second_4_plus_2": hermite(2, points) ** 2 - hermite(4, points) - 4.0 * hermite(2, points) - 2.0,
        "raw_second_5_plus_2": points**2 * hermite(2, points) - hermite(4, points) - 5.0 * hermite(2, points) - 2.0,
        "recursive_3_plus_0": points * hermite(3, points) - hermite(4, points) - 3.0 * hermite(2, points),
    }
    for name, error in identities.items():
        maximum = float(np.max(np.abs(error)))
        add(rows, f"pointwise_{name}", maximum < tolerance, maximum, f"<{tolerance}")

    boundary_modes = mode_cube(int(audit["partition_cutoff"]))
    partition_errors = 0
    nested_errors = {"X_PI_X_Q": 0, "PI_XX_Q": 0}
    for left in boundary_modes:
        for right in boundary_modes:
            selected = sector(left, right)
            if selected not in SECTORS:
                partition_errors += 1
            value_sum = tuple(a + b for a, b in zip(left, right, strict=True))
            derivative_sum = negate(value_sum)
            selections = {
                "X_PI_X_Q": (sector(left, negate(left)), sector(right, derivative_sum)),
                "PI_XX_Q": (sector(value_sum, derivative_sum), sector(left, right)),
            }
            for parent, pair in selections.items():
                total = sum(
                    int(pair == (outer, inner))
                    for outer in SECTORS
                    for inner in SECTORS
                )
                if total != 1:
                    nested_errors[parent] += 1
    add(rows, "independent_bony_partition", partition_errors == 0, partition_errors, 0)
    for parent, count in nested_errors.items():
        add(rows, f"independent_nested_partition_{parent.lower()}", count == 0, count, 0)

    parity_modes = mode_cube(int(audit["parity_cutoff"]))
    parity_error = max(
        float(np.max(np.abs(covariance(mode) - covariance(negate(mode)))))
        for mode in parity_modes
    )
    add(rows, "independent_covariance_even", parity_error < tolerance, parity_error, f"<{tolerance}")

    direction = int(audit["direction"])
    paired_gradient = np.zeros((6, 6), dtype=np.float64)
    visited: set[tuple[int, int, int]] = set()
    for mode in parity_modes:
        if mode in visited:
            continue
        partner = negate(mode)
        visited.add(mode)
        visited.add(partner)
        paired_gradient += wave_factor * mode[direction] * covariance(mode)
        if partner != mode:
            paired_gradient += wave_factor * partner[direction] * covariance(partner)
    gradient_norm = float(np.linalg.norm(paired_gradient))
    add(rows, "independent_pairwise_mixed_covariance_zero", gradient_norm < tolerance, gradient_norm, f"<{tolerance}")

    asymmetric = np.sum(
        [
            wave_factor * mode[direction] * covariance(mode)
            for mode in parity_modes
            if mode[direction] >= 0
        ],
        axis=0,
    )
    asymmetric_norm = float(np.linalg.norm(asymmetric))
    add(
        rows,
        "independent_asymmetric_failure_control",
        asymmetric_norm > float(audit["asymmetric_minimum"]),
        asymmetric_norm,
        f">{audit['asymmetric_minimum']}",
    )

    scalar_gradient = float(paired_gradient[0, 0])
    complete_double_cross = -2.0 * scalar_gradient**2
    add(
        rows,
        "independent_complete_double_cross_zero",
        abs(complete_double_cross) < tolerance,
        complete_double_cross,
        f"absolute<{tolerance}",
    )

    failures = [row for row in rows if row["status"] != "PASS"]
    passed = len(rows) - len(failures)
    payload = {
        "schema": "tect/a13-classii-coefficient-jet-forest-independent-result/1.0",
        "claim_id": manifest["claim_id"],
        "result_id": manifest["result_id"],
        "script_version": __version__,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": git_commit(),
        "platform": platform.platform(),
        "manifest": str(manifest_path.relative_to(REPO)).replace("\\", "/"),
        "manifest_sha256": digest(manifest_path),
        "derived": {
            "hermite_projections": projections,
            "pointwise_identity_errors": {
                key: float(np.max(np.abs(value))) for key, value in identities.items()
            },
            "parity_error": parity_error,
            "paired_gradient_norm": gradient_norm,
            "asymmetric_gradient_norm": asymmetric_norm,
            "complete_double_cross": complete_double_cross,
        },
        "assertions": rows,
        "summary": {"passed": passed, "total": len(rows), "failed": len(failures)},
        "verdict": (
            "A13-CLASSII-COEFFICIENT-JET-FOREST-INDEPENDENT-PASS"
            if not failures
            else "FAIL"
        ),
        "honesty_boundary": manifest["honesty_boundary"],
    }
    atomic_json(output_path, payload)
    if failures:
        print(f"FAIL: independent ({len(failures)}/{len(rows)} failed)")
        for failure in failures:
            print(f" - {failure['name']}: {failure['actual']}")
        return 1
    print(f"PASS: independent ({passed}/{len(rows)})")
    print("A13-CLASSII-COEFFICIENT-JET-FOREST-INDEPENDENT-PASS")
    print(f"Evidence: {output_path}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    arguments = parser.parse_args()
    return run(arguments.manifest.resolve(), arguments.output.resolve())


if __name__ == "__main__":
    raise SystemExit(main())

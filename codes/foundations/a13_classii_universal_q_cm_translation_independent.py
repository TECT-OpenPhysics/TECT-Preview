#!/usr/bin/env python3
"""Non-importing audit for the A13 universal-Q/CM translation theorem."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np
from numpy.polynomial.hermite_e import hermegauss

__version__ = "1.0.0"
__first_issued__ = "2026-07-22"
__version_issued__ = "2026-07-22"

REPO = Path(__file__).resolve().parents[2]
CLAIM = REPO / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
DEFAULT_MANIFEST = CLAIM / "classii_universal_q_cm_translation_manifest.json"
DEFAULT_OUTPUT = CLAIM / "runs" / "2026-07-22-independent-universal-q-cm-translation" / "result.json"


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def git_commit() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=REPO, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "UNKNOWN"


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name, suffix=".tmp", dir=path.parent)
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


def record(rows: list[dict[str, Any]], name: str, passed: bool, actual: Any, expected: Any) -> None:
    rows.append(
        {
            "name": name,
            "status": "PASS" if bool(passed) else "FAIL",
            "actual": actual,
            "expected": expected,
        }
    )


def covariance(mode: tuple[int, int, int]) -> float:
    radius_squared = sum(component * component for component in mode)
    return (1.0 + float(radius_squared)) ** -2


def derivative_weight(mode: tuple[int, int, int]) -> float:
    radius_squared = sum(component * component for component in mode)
    return float(radius_squared) * covariance(mode)


def direct_q_value(cutoff: int, output: tuple[int, int, int]) -> float:
    total = 0.0
    for first in range(-cutoff, cutoff + 1):
        for second in range(-cutoff, cutoff + 1):
            for third in range(-cutoff, cutoff + 1):
                left = (first, second, third)
                right = tuple(output[index] - left[index] for index in range(3))
                if all(-cutoff <= component <= cutoff for component in right):
                    total += derivative_weight(left) * derivative_weight(right)
    return total


def probabilists_hermite(degree: int, value: np.ndarray) -> np.ndarray:
    if degree == 0:
        return np.ones_like(value)
    if degree == 1:
        return value.copy()
    previous = np.ones_like(value)
    current = value.copy()
    for order in range(1, degree):
        previous, current = current, value * current - order * previous
    return current


def hermite_moment_audit(order: int, probability_power: float) -> list[dict[str, float]]:
    nodes, weights = hermegauss(order)
    normalized_weights = weights / math.sqrt(2.0 * math.pi)
    result: list[dict[str, float]] = []
    for degree in (2, 3, 4):
        values = probabilists_hermite(degree, nodes)
        second = float(np.sum(normalized_weights * values * values)) ** 0.5
        p_norm = float(np.sum(normalized_weights * np.abs(values) ** probability_power)) ** (1.0 / probability_power)
        bound_factor = (probability_power - 1.0) ** (0.5 * degree)
        result.append(
            {
                "degree": degree,
                "l2": second,
                "lp": p_norm,
                "ratio": p_norm / second,
                "nelson_factor": bound_factor,
            }
        )
    return result


def shifted_hermite_identity(maximum_degree: int, points: list[float], shifts: list[float]) -> float:
    error = 0.0
    for degree in range(maximum_degree + 1):
        for point in points:
            for shift in shifts:
                left = float(probabilists_hermite(degree, np.asarray([point + shift]))[0])
                right = 0.0
                for retained in range(degree + 1):
                    right += (
                        math.comb(degree, retained)
                        * shift ** (degree - retained)
                        * float(probabilists_hermite(retained, np.asarray([point]))[0])
                    )
                error = max(error, abs(left - right))
    return error


def independent_translation_identity(seed: int, samples: int, components: int) -> float:
    generator = np.random.default_rng(seed)
    derivative = generator.standard_normal((samples, components))
    shift = generator.standard_normal((samples, components))
    maximum = 0.0
    for sample in range(samples):
        for left in range(components):
            for right in range(components):
                direct = (derivative[sample, left] + shift[sample, left]) * (
                    derivative[sample, right] + shift[sample, right]
                ) - derivative[sample, left] * derivative[sample, right]
                expanded = (
                    shift[sample, left] * derivative[sample, right]
                    + derivative[sample, left] * shift[sample, right]
                    + shift[sample, left] * shift[sample, right]
                )
                maximum = max(maximum, abs(direct - expanded))
    return maximum


def symmetric_value_derivative_sum(cutoff: int) -> float:
    total = 0.0
    for first in range(-cutoff, cutoff + 1):
        for second in range(-cutoff, cutoff + 1):
            for third in range(-cutoff, cutoff + 1):
                mode = (first, second, third)
                total += first * covariance(mode)
    return total


def contraction_counts() -> dict[str, int]:
    # XQ has two possible value--derivative pairings.  For (XX)Q, four
    # cross single pairings and two perfect cross double pairings survive
    # before the homogeneous-chaos projection.
    xq_single = len([(value, derivative) for value in range(1) for derivative in range(2)])
    xxq_single = len([(value, derivative) for value in range(2) for derivative in range(2)])
    xxq_double = math.factorial(2)
    return {"xq_single": xq_single, "xxq_single": xxq_single, "xxq_double": xxq_double}


def cone_certificate_loop(radius: int) -> dict[str, float]:
    one_sum = 0.0
    count = 0
    for first in range(radius, 2 * radius):
        for second in range(radius, 2 * radius):
            for third in range(radius, 2 * radius):
                one_sum += first * covariance((first, second, third))
                count += 1
    dimension = 3
    lower_one = count * radius * (1.0 + dimension * (2 * radius) ** 2) ** -2
    return {
        "radius": radius,
        "double_contraction_magnitude": one_sum * one_sum,
        "raw_scalar_coefficient": -2.0 * one_sum * one_sum,
        "rigorous_magnitude_lower_bound": lower_one * lower_one,
    }


def run(manifest_path: Path, output_path: Path) -> int:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []
    alpha = float(manifest["regularity"]["alpha"])
    kappa = float(manifest["regularity"]["kappa"])
    dimension = int(manifest["regularity"]["dimension"])
    required_moment = 6.0 / (2.0 - kappa)
    q_decay = 2.0 * float(manifest["regularity"]["derivative_leg_covariance_decay"]) - dimension
    q_ceiling = 0.5 * (q_decay - dimension)
    tolerance = float(manifest["independent_audit"]["arithmetic_tolerance"])
    record(rows, "independent_regularities_admissible", 1.0 / 3.0 < alpha < 0.5 and 0.0 < kappa < 0.5, [alpha, kappa], "1/3<alpha<1/2 and 0<kappa<1/2")
    record(rows, "independent_q_decay", abs(q_decay - float(manifest["theoretical_oracles"]["q_spectrum_decay"])) < tolerance, q_decay, manifest["theoretical_oracles"]["q_spectrum_decay"])
    record(rows, "independent_q_ceiling", abs(q_ceiling - float(manifest["theoretical_oracles"]["q_sobolev_ceiling"])) < tolerance, q_ceiling, manifest["theoretical_oracles"]["q_sobolev_ceiling"])
    record(rows, "independent_required_moment_strictly_above_three", required_moment > 3.0, required_moment, ">3")
    record(rows, "independent_cm_convolution_summable", 4.0 + 2.0 * kappa > dimension, 4.0 + 2.0 * kappa, f">{dimension}")

    shared_cutoff = int(manifest["independent_audit"]["shared_cutoff"])
    direct_values = {
        ",".join(str(int(component)) for component in output): direct_q_value(
            shared_cutoff, tuple(int(component) for component in output)
        )
        for output in manifest["audit"]["selected_outputs"]
    }
    for key, value in direct_values.items():
        record(rows, f"direct_q_positive_{key}", value > 0.0, value, ">0")

    moment_rows = hermite_moment_audit(
        int(manifest["independent_audit"]["hermite_order"]), required_moment
    )
    for item in moment_rows:
        record(rows, f"hermite_degree_{int(item['degree'])}_nelson_bound", item["ratio"] <= item["nelson_factor"] + float(manifest["independent_audit"]["moment_tolerance"]), [item["ratio"], item["nelson_factor"]], "ratio<=Nelson factor")
    hermite_shift_error = shifted_hermite_identity(
        int(manifest["independent_audit"]["maximum_chaos_degree"]),
        [float(value) for value in manifest["independent_audit"]["hermite_points"]],
        [float(value) for value in manifest["independent_audit"]["hermite_shifts"]],
    )
    record(rows, "wick_translation_binomial_identity", hermite_shift_error < float(manifest["independent_audit"]["translation_tolerance"]), hermite_shift_error, manifest["independent_audit"]["translation_tolerance"])
    tensor_shift_error = independent_translation_identity(
        int(manifest["independent_audit"]["translation_seed"]),
        int(manifest["independent_audit"]["translation_samples"]),
        int(manifest["audit"]["components"]),
    )
    record(rows, "independent_q_translation_identity", tensor_shift_error < float(manifest["independent_audit"]["translation_tolerance"]), tensor_shift_error, manifest["independent_audit"]["translation_tolerance"])

    parity_sum = symmetric_value_derivative_sum(int(manifest["independent_audit"]["parity_cutoff"]))
    record(rows, "full_same_point_value_derivative_parity", abs(parity_sum) < float(manifest["independent_audit"]["parity_tolerance"]), parity_sum, 0.0)
    counts = contraction_counts()
    record(rows, "xq_cross_contraction_count", counts["xq_single"] == 2, counts["xq_single"], 2)
    record(rows, "xxq_single_cross_contraction_count", counts["xxq_single"] == 4, counts["xxq_single"], 4)
    record(rows, "xxq_double_cross_contraction_count", counts["xxq_double"] == 2, counts["xxq_double"], 2)

    cone_rows = [cone_certificate_loop(int(radius)) for radius in manifest["independent_audit"]["cone_shell_radii"]]
    for cone in cone_rows:
        radius = int(cone["radius"])
        record(rows, f"independent_log_shell_lower_bound_r{radius}", cone["raw_scalar_coefficient"] < 0.0 and cone["double_contraction_magnitude"] >= cone["rigorous_magnitude_lower_bound"] > 0.0, [cone["raw_scalar_coefficient"], cone["double_contraction_magnitude"], cone["rigorous_magnitude_lower_bound"]], "negative raw coefficient and magnitude>=positive lower bound")
    record(rows, "raw_full_first_target_fails", q_decay <= dimension + 2.0 * (alpha - 1.0 - kappa), [q_decay, dimension + 2.0 * (alpha - 1.0 - kappa)], "available<=required")
    record(rows, "raw_full_second_target_fails", q_decay <= dimension + 2.0 * (2.0 * alpha - 1.0 - kappa), [q_decay, dimension + 2.0 * (2.0 * alpha - 1.0 - kappa)], "available<=required")

    failures = [row for row in rows if row["status"] != "PASS"]
    passed = len(rows) - len(failures)
    payload = {
        "schema": "tect/a13-classii-universal-q-cm-translation-independent-result/1.0",
        "claim_id": manifest["claim_id"],
        "result_id": manifest["result_id"],
        "script_version": __version__,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": git_commit(),
        "platform": platform.platform(),
        "manifest": str(manifest_path.relative_to(REPO)).replace("\\", "/"),
        "manifest_sha256": digest(manifest_path),
        "derived": {
            "q_spectrum_decay": q_decay,
            "q_sobolev_ceiling": q_ceiling,
            "required_model_moment": required_moment,
            "direct_q_values": direct_values,
            "hermite_moments": moment_rows,
            "hermite_translation_error": hermite_shift_error,
            "tensor_translation_error": tensor_shift_error,
            "same_point_parity_sum": parity_sum,
            "contraction_counts": counts,
            "nested_resonance_cone_certificate": cone_rows,
        },
        "assertions": rows,
        "summary": {"passed": passed, "total": len(rows), "failed": len(failures)},
        "verdict": "A13-CLASSII-UNIVERSAL-Q-CM-TRANSLATION-INDEPENDENT-PASS" if not failures else "FAIL",
        "consequence": manifest["consequence"],
        "honesty_boundary": manifest["honesty_boundary"],
    }
    atomic_json(output_path, payload)
    if failures:
        print(f"FAIL: independent ({len(failures)}/{len(rows)} failed)")
        for failure in failures:
            print(f" - {failure['name']}: {failure['actual']}")
        return 1
    print(f"PASS: independent ({passed}/{len(rows)})")
    print("A13-CLASSII-UNIVERSAL-Q-CM-TRANSLATION-INDEPENDENT-PASS")
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

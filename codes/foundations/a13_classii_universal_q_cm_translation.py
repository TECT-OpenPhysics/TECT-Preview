#!/usr/bin/env python3
"""Primary audit for the A13 universal-Q and Cameron--Martin theorem.

The analytic theorem is proved in the paired proof note.  This executable
checks its exponent arithmetic, finite-cutoff tensor identities, scalar
Fourier majorants, and the two raw coefficient-jet counterexamples which
force the next gate to remain open.  Finite fixtures are regression and
falsifier evidence; they are not substituted for the continuum proof.
"""

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

__version__ = "1.0.0"
__first_issued__ = "2026-07-22"
__version_issued__ = "2026-07-22"

REPO = Path(__file__).resolve().parents[2]
CLAIM = REPO / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
DEFAULT_MANIFEST = CLAIM / "classii_universal_q_cm_translation_manifest.json"
DEFAULT_OUTPUT = CLAIM / "runs" / "2026-07-22-primary-universal-q-cm-translation" / "result.json"


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


def add(rows: list[dict[str, Any]], name: str, passed: bool, actual: Any, expected: Any) -> None:
    rows.append(
        {
            "name": name,
            "status": "PASS" if bool(passed) else "FAIL",
            "actual": actual,
            "expected": expected,
        }
    )


def scalar_covariance(coordinates: np.ndarray) -> np.ndarray:
    radius_squared = np.sum(np.asarray(coordinates, dtype=np.float64) ** 2, axis=-1)
    return (1.0 + radius_squared) ** -2


def mode_cube(cutoff: int) -> tuple[np.ndarray, np.ndarray]:
    axis = np.arange(-cutoff, cutoff + 1, dtype=np.int64)
    mesh = np.meshgrid(axis, axis, axis, indexing="ij")
    coordinates = np.stack(mesh, axis=-1)
    return coordinates, scalar_covariance(coordinates)


def linear_convolution(left: np.ndarray, right: np.ndarray) -> np.ndarray:
    shape = tuple(a + b - 1 for a, b in zip(left.shape, right.shape, strict=True))
    transformed = np.fft.fftn(left, shape) * np.fft.fftn(right, shape)
    result = np.fft.ifftn(transformed).real
    scale = max(1.0, float(np.max(np.abs(result))))
    result[np.abs(result) < 5.0e-13 * scale] = 0.0
    return result


def q_majorant_fixture(cutoff: int, kappa: float, outputs: list[list[int]]) -> dict[str, Any]:
    coordinates, covariance = mode_cube(cutoff)
    derivative_weight = np.sum(coordinates.astype(np.float64) ** 2, axis=-1) * covariance
    spectrum = linear_convolution(derivative_weight, derivative_weight)
    support = 2 * cutoff
    axis = np.arange(-support, support + 1, dtype=np.float64)
    mesh = np.meshgrid(axis, axis, axis, indexing="ij")
    radius_squared = sum(item * item for item in mesh)
    sobolev_weight = (1.0 + radius_squared) ** (-1.0 - kappa)
    reflected = spectrum[::-1, ::-1, ::-1]
    selected: dict[str, float] = {}
    for output in outputs:
        index = tuple(int(component) + support for component in output)
        selected[",".join(str(int(component)) for component in output)] = float(spectrum[index])
    return {
        "cutoff": cutoff,
        "minimum": float(np.min(spectrum)),
        "maximum": float(np.max(spectrum)),
        "symmetry_error": float(np.max(np.abs(spectrum - reflected))),
        "weighted_h_minus_1_kappa_sum": float(np.sum(sobolev_weight * spectrum)),
        "selected_outputs": selected,
    }


def translated_q_identity(seed: int, samples: int, components: int) -> dict[str, float]:
    rng = np.random.default_rng(seed)
    derivative = rng.normal(size=(samples, components))
    shift_derivative = rng.normal(size=(samples, components))
    raw = np.einsum("ni,nj->nij", derivative, derivative)
    shifted = np.einsum("ni,nj->nij", derivative + shift_derivative, derivative + shift_derivative)
    cross = (
        np.einsum("ni,nj->nij", shift_derivative, derivative)
        + np.einsum("ni,nj->nij", derivative, shift_derivative)
        + np.einsum("ni,nj->nij", shift_derivative, shift_derivative)
    )
    error = shifted - raw - cross
    return {
        "maximum_error": float(np.max(np.abs(error))),
        "frobenius_error": float(np.linalg.norm(error)),
    }


def cone_shell_certificate(radius: int, dimension: int) -> dict[str, float]:
    if dimension != 3:
        raise ValueError("the production fixture is three-dimensional")
    axis = np.arange(radius, 2 * radius, dtype=np.float64)
    mesh = np.meshgrid(axis, axis, axis, indexing="ij")
    coordinates = np.stack(mesh, axis=-1)
    covariance = scalar_covariance(coordinates)
    one_sum = float(np.sum(coordinates[..., 0] * covariance))
    magnitude = one_sum * one_sum
    raw_scalar_coefficient = -2.0 * magnitude
    cardinality = radius**dimension
    covariance_lower = (1.0 + dimension * (2.0 * radius) ** 2) ** -2
    one_sum_lower = cardinality * radius * covariance_lower
    lower_bound = one_sum_lower * one_sum_lower
    return {
        "radius": radius,
        "one_contraction_sum": one_sum,
        "double_contraction_magnitude": magnitude,
        "raw_scalar_coefficient": raw_scalar_coefficient,
        "rigorous_magnitude_lower_bound": lower_bound,
        "ratio_to_lower_bound": magnitude / lower_bound,
    }


def localized_first_chaos_witness(radius: int) -> float:
    support = 2 * radius + 2
    coordinates, covariance = mode_cube(support)
    norm = np.max(np.abs(coordinates), axis=-1)
    output = np.asarray([1, 0, 0], dtype=np.int64)
    partner = output - coordinates
    partner_norm = np.max(np.abs(partner), axis=-1)
    mask = (
        (norm >= radius)
        & (norm < 2 * radius)
        & (partner_norm >= radius)
        & (partner_norm < 2 * radius)
    )
    return float(np.sum(coordinates[..., 0] * covariance * mask))


def theorem_arithmetic(manifest: dict[str, Any]) -> dict[str, float]:
    dimension = int(manifest["regularity"]["dimension"])
    alpha = float(manifest["regularity"]["alpha"])
    kappa = float(manifest["regularity"]["kappa"])
    derivative_leg_decay = float(manifest["regularity"]["derivative_leg_covariance_decay"])
    q_decay = 2.0 * derivative_leg_decay - dimension
    q_sobolev_ceiling = 0.5 * (q_decay - dimension)
    required_moment = 6.0 / (2.0 - kappa)
    full_first_target = alpha - 1.0 - kappa
    full_second_target = 2.0 * alpha - 1.0 - kappa
    full_first_required_decay = dimension + 2.0 * full_first_target
    full_second_required_decay = dimension + 2.0 * full_second_target
    nested_shell_power = 2.0 * dimension + 2.0 - 8.0
    return {
        "q_spectrum_decay": q_decay,
        "q_sobolev_ceiling": q_sobolev_ceiling,
        "required_model_moment": required_moment,
        "full_product_spectrum_decay": q_decay,
        "first_jet_target": full_first_target,
        "second_jet_target": full_second_target,
        "first_jet_required_spectrum_decay": full_first_required_decay,
        "second_jet_required_spectrum_decay": full_second_required_decay,
        "nested_resonance_shell_power": nested_shell_power,
        "mixed_cm_convolution_power_sum": (2.0 + 2.0 * kappa) + derivative_leg_decay,
    }


def run(manifest_path: Path, output_path: Path) -> int:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []
    for key, authority in manifest["authority"].items():
        actual = digest(REPO / authority["path"])
        add(rows, f"authority_{key}_hash", actual == authority["sha256"], actual, authority["sha256"])

    arithmetic = theorem_arithmetic(manifest)
    regularity = manifest["regularity"]
    alpha = float(regularity["alpha"])
    kappa = float(regularity["kappa"])
    dimension = int(regularity["dimension"])
    oracle = manifest["theoretical_oracles"]
    tolerance = float(manifest["audit"]["arithmetic_tolerance"])
    add(rows, "alpha_above_one_third", alpha > 1.0 / 3.0, alpha, ">1/3")
    add(rows, "alpha_below_one_half", alpha < 0.5, alpha, "<1/2")
    add(rows, "kappa_in_declared_range", 0.0 < kappa < 0.5, kappa, "0<kappa<1/2")
    add(rows, "q_decay_arithmetic", abs(arithmetic["q_spectrum_decay"] - float(oracle["q_spectrum_decay"])) < tolerance, arithmetic["q_spectrum_decay"], oracle["q_spectrum_decay"])
    add(rows, "q_sobolev_ceiling_arithmetic", abs(arithmetic["q_sobolev_ceiling"] - float(oracle["q_sobolev_ceiling"])) < tolerance, arithmetic["q_sobolev_ceiling"], oracle["q_sobolev_ceiling"])
    add(rows, "declared_q_target_below_ceiling", -1.0 - kappa < arithmetic["q_sobolev_ceiling"], -1.0 - kappa, arithmetic["q_sobolev_ceiling"])
    add(rows, "required_moment_exceeds_three", arithmetic["required_model_moment"] > 3.0, arithmetic["required_model_moment"], ">3")
    add(rows, "all_finite_moments_cover_required", math.isfinite(arithmetic["required_model_moment"]), arithmetic["required_model_moment"], "finite")
    add(rows, "cm_mixed_convolution_summable", arithmetic["mixed_cm_convolution_power_sum"] > dimension, arithmetic["mixed_cm_convolution_power_sum"], f">{dimension}")
    add(rows, "full_first_product_decay_insufficient", arithmetic["full_product_spectrum_decay"] <= arithmetic["first_jet_required_spectrum_decay"], [arithmetic["full_product_spectrum_decay"], arithmetic["first_jet_required_spectrum_decay"]], "available<=required")
    add(rows, "full_second_product_decay_insufficient", arithmetic["full_product_spectrum_decay"] <= arithmetic["second_jet_required_spectrum_decay"], [arithmetic["full_product_spectrum_decay"], arithmetic["second_jet_required_spectrum_decay"]], "available<=required")
    add(rows, "nested_resonance_is_logarithmic", abs(arithmetic["nested_resonance_shell_power"]) < tolerance, arithmetic["nested_resonance_shell_power"], 0.0)
    for chaos_degree in (2, 3, 4):
        factor = (arithmetic["required_model_moment"] - 1.0) ** (0.5 * chaos_degree)
        add(rows, f"hypercontractive_factor_degree_{chaos_degree}", factor > 1.0 and math.isfinite(factor), factor, "finite and >1")

    fixtures = [
        q_majorant_fixture(int(cutoff), kappa, manifest["audit"]["selected_outputs"])
        for cutoff in manifest["audit"]["q_cutoffs"]
    ]
    for fixture in fixtures:
        cutoff = int(fixture["cutoff"])
        add(rows, f"q_majorant_nonnegative_N{cutoff}", fixture["minimum"] >= -float(manifest["audit"]["fft_tolerance"]), fixture["minimum"], ">=0")
        add(rows, f"q_majorant_symmetric_N{cutoff}", fixture["symmetry_error"] < float(manifest["audit"]["fft_tolerance"]), fixture["symmetry_error"], manifest["audit"]["fft_tolerance"])
        add(rows, f"q_weighted_sum_finite_N{cutoff}", fixture["weighted_h_minus_1_kappa_sum"] > 0.0 and math.isfinite(fixture["weighted_h_minus_1_kappa_sum"]), fixture["weighted_h_minus_1_kappa_sum"], "finite positive")
    for output in manifest["audit"]["selected_outputs"]:
        key = ",".join(str(int(component)) for component in output)
        values = [float(fixture["selected_outputs"][key]) for fixture in fixtures]
        add(rows, f"q_selected_output_monotone_{key}", all(right + tolerance >= left for left, right in zip(values, values[1:])), values, "nondecreasing with cutoff")

    translation = translated_q_identity(
        int(manifest["audit"]["translation_seed"]),
        int(manifest["audit"]["translation_samples"]),
        int(manifest["audit"]["components"]),
    )
    add(rows, "finite_cutoff_cm_translation_identity", translation["maximum_error"] < float(manifest["audit"]["translation_tolerance"]), translation, manifest["audit"]["translation_tolerance"])

    cone_rows = [
        cone_shell_certificate(int(radius), dimension)
        for radius in manifest["audit"]["cone_shell_radii"]
    ]
    for cone in cone_rows:
        radius = int(cone["radius"])
        add(rows, f"nested_raw_scalar_coefficient_negative_r{radius}", cone["raw_scalar_coefficient"] < 0.0, cone["raw_scalar_coefficient"], "<0")
        add(rows, f"nested_contraction_magnitude_lower_bound_r{radius}", cone["double_contraction_magnitude"] >= cone["rigorous_magnitude_lower_bound"] > 0.0, [cone["double_contraction_magnitude"], cone["rigorous_magnitude_lower_bound"]], "magnitude>=positive rigorous lower bound")
    cumulative = np.cumsum([float(row["double_contraction_magnitude"]) for row in cone_rows])
    add(rows, "nested_contraction_magnitude_cumulative_strict_growth", bool(np.all(np.diff(cumulative) > 0.0)), cumulative.tolist(), "strictly increasing certified magnitude sum")
    first_chaos = localized_first_chaos_witness(int(manifest["audit"]["localized_witness_radius"]))
    add(rows, "localized_first_chaos_not_killed_by_global_evenness", abs(first_chaos) > float(manifest["audit"]["localized_witness_minimum"]), first_chaos, f"absolute>{manifest['audit']['localized_witness_minimum']}")

    failures = [row for row in rows if row["status"] != "PASS"]
    passed = len(rows) - len(failures)
    payload = {
        "schema": "tect/a13-classii-universal-q-cm-translation-primary-result/1.0",
        "claim_id": manifest["claim_id"],
        "result_id": manifest["result_id"],
        "script_version": __version__,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": git_commit(),
        "platform": platform.platform(),
        "manifest": str(manifest_path.relative_to(REPO)).replace("\\", "/"),
        "manifest_sha256": digest(manifest_path),
        "derived": {
            "theorem_arithmetic": arithmetic,
            "q_majorant_fixtures": fixtures,
            "translation_identity": translation,
            "nested_resonance_cone_certificate": cone_rows,
            "nested_resonance_cumulative": cumulative.tolist(),
            "localized_first_chaos_witness": first_chaos,
        },
        "assertions": rows,
        "summary": {"passed": passed, "total": len(rows), "failed": len(failures)},
        "verdict": "A13-CLASSII-UNIVERSAL-Q-CM-TRANSLATION-PRIMARY-PASS" if not failures else "FAIL",
        "consequence": manifest["consequence"],
        "honesty_boundary": manifest["honesty_boundary"],
    }
    atomic_json(output_path, payload)
    if failures:
        print(f"FAIL: primary ({len(failures)}/{len(rows)} failed)")
        for failure in failures:
            print(f" - {failure['name']}: {failure['actual']}")
        return 1
    print(f"PASS: primary ({passed}/{len(rows)})")
    print("A13-CLASSII-UNIVERSAL-Q-CM-TRANSLATION-PRIMARY-PASS")
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

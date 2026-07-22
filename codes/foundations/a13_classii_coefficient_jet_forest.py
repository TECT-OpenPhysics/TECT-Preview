#!/usr/bin/env python3
"""Primary finite-cutoff forest audit for the A13 coefficient jets.

The paired note supplies the analytic Wiener-product proof. This executable
checks the contraction counts, the exact sharp-cube Bony partition, the two
second-jet parenthesisations, common-even cancellation, and an asymmetric
regulator failure control. It does not test or claim continuum convergence.
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
from typing import Any

import numpy as np

__version__ = "1.0.0"
__first_issued__ = "2026-07-22"
__version_issued__ = "2026-07-22"

REPO = Path(__file__).resolve().parents[2]
CLAIM = REPO / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
DEFAULT_MANIFEST = CLAIM / "classii_coefficient_jet_forest_manifest.json"
DEFAULT_OUTPUT = (
    CLAIM
    / "runs"
    / "2026-07-22-primary-coefficient-jet-forest-classification"
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


def mode_scale(mode: tuple[int, int, int]) -> int:
    radius = max(abs(component) for component in mode)
    if radius <= 1:
        return 0
    return (radius - 1).bit_length()


def add_modes(
    left: tuple[int, int, int], right: tuple[int, int, int]
) -> tuple[int, int, int]:
    return tuple(a + b for a, b in zip(left, right, strict=True))


def negate(mode: tuple[int, int, int]) -> tuple[int, int, int]:
    return tuple(-component for component in mode)


def bony_sector(
    left: tuple[int, int, int], right: tuple[int, int, int]
) -> str:
    left_scale = mode_scale(left)
    right_scale = mode_scale(right)
    if left_scale <= right_scale - 2:
        return "LOW_HIGH"
    if right_scale <= left_scale - 2:
        return "HIGH_LOW"
    return "RESONANT"


def bony_weights(
    left: tuple[int, int, int], right: tuple[int, int, int]
) -> dict[str, int]:
    selected = bony_sector(left, right)
    return {sector: int(sector == selected) for sector in SECTORS}


def modes(cutoff: int) -> list[tuple[int, int, int]]:
    axis = range(-cutoff, cutoff + 1)
    return list(itertools.product(axis, repeat=3))


def cross_matching_count(left_legs: int, right_legs: int, pairs: int) -> int:
    if not 0 <= pairs <= min(left_legs, right_legs):
        return 0
    return (
        math.comb(left_legs, pairs)
        * math.comb(right_legs, pairs)
        * math.factorial(pairs)
    )


SparseField = dict[tuple[int, int, int], int]


def add_sparse(*fields: SparseField) -> SparseField:
    output: SparseField = {}
    for field in fields:
        for mode, value in field.items():
            output[mode] = output.get(mode, 0) + value
    return {mode: value for mode, value in output.items() if value != 0}


def convolve_sparse(left: SparseField, right: SparseField) -> SparseField:
    output: SparseField = {}
    for left_mode, left_value in left.items():
        for right_mode, right_value in right.items():
            total_mode = add_modes(left_mode, right_mode)
            output[total_mode] = output.get(total_mode, 0) + left_value * right_value
    return {mode: value for mode, value in output.items() if value != 0}


def bony_sparse(left: SparseField, right: SparseField, selected: str) -> SparseField:
    output: SparseField = {}
    for left_mode, left_value in left.items():
        for right_mode, right_value in right.items():
            if bony_sector(left_mode, right_mode) != selected:
                continue
            total_mode = add_modes(left_mode, right_mode)
            output[total_mode] = output.get(total_mode, 0) + left_value * right_value
    return {mode: value for mode, value in output.items() if value != 0}


def manufactured_sparse_field(seed: int, cutoff: int) -> SparseField:
    rng = np.random.default_rng(seed)
    output = {
        mode: int(value)
        for mode, value in zip(
            modes(cutoff),
            rng.integers(-3, 4, size=(2 * cutoff + 1) ** 3),
            strict=True,
        )
        if int(value) != 0
    }
    if not output:
        raise AssertionError("manufactured field unexpectedly vanished")
    return output


def complete_bony(left: SparseField, right: SparseField) -> SparseField:
    return add_sparse(*(bony_sparse(left, right, selected) for selected in SECTORS))


def complete_nested(
    first: SparseField,
    second: SparseField,
    third: SparseField,
    parenthesisation: str,
) -> tuple[SparseField, dict[str, SparseField]]:
    channels: dict[str, SparseField] = {}
    if parenthesisation == "X_PI_X_Q":
        for outer in SECTORS:
            for inner in SECTORS:
                channels[f"{outer}/{inner}"] = bony_sparse(
                    first, bony_sparse(second, third, inner), outer
                )
    elif parenthesisation == "PI_XX_Q":
        for outer in SECTORS:
            for inner in SECTORS:
                channels[f"{outer}/{inner}"] = bony_sparse(
                    bony_sparse(first, second, inner), third, outer
                )
    else:
        raise ValueError(parenthesisation)
    return add_sparse(*channels.values()), channels


def covariance_builder(parameters: dict[str, Any]):
    length = float(parameters["Lx"])
    if not (
        float(parameters["Ly"]) == length
        and float(parameters["Lz"]) == length
    ):
        raise ValueError("the production fixture requires a cubic torus")
    z0 = np.asarray(parameters["z0"], dtype=np.float64)
    projector = np.outer(z0, z0) / float(z0 @ z0)
    lock = float(parameters["k_lock"]) * (np.eye(3) - projector)
    masses = np.asarray(parameters["family_masses"], dtype=np.float64)
    wave_factor = 2.0 * math.pi / length
    mode_measure = length**-3

    @functools.lru_cache(maxsize=None)
    def covariance(mode: tuple[int, int, int]) -> np.ndarray:
        wave = wave_factor * np.asarray(mode, dtype=np.float64)
        radius_squared = float(wave @ wave)
        scalar = (
            float(parameters["r"])
            + float(parameters["Z"]) * radius_squared
            + float(parameters["Y"]) * radius_squared**2
        )
        symbol = scalar * np.eye(3) + np.diag(masses) + lock
        eigenvalues = np.linalg.eigvalsh(symbol)
        if float(eigenvalues.min()) <= 0.0:
            raise ValueError(f"non-positive production symbol at mode {mode}")
        complex_covariance = np.linalg.inv(symbol)
        zero = np.zeros_like(complex_covariance)
        # A7 eq. (2.5): the six-real covariance is one half of the
        # realification of the complex covariance. The mode measure pins the
        # normalized Fourier convention used by this finite fixture.
        return 0.5 * mode_measure * np.block(
            [[complex_covariance, zero], [zero, complex_covariance]]
        )

    def wave_component(mode: tuple[int, int, int], direction: int) -> float:
        return wave_factor * float(mode[direction])

    return covariance, wave_component


def mixed_gradient_covariance(
    mode_list: list[tuple[int, int, int]], covariance, wave_component, direction: int
) -> np.ndarray:
    terms = [wave_component(mode, direction) * covariance(mode) for mode in mode_list]
    return np.sum(terms, axis=0)


def first_jet_correctors(
    mode_list: list[tuple[int, int, int]],
    covariance,
    wave_component,
    output: tuple[int, int, int],
    direction: int,
) -> dict[str, float]:
    values = {sector: 0.0 for sector in SECTORS}
    output_wave = wave_component(output, direction)
    for mode in mode_list:
        q_mode = add_modes(output, negate(mode))
        sector = bony_sector(mode, q_mode)
        values[sector] += (
            output_wave
            * wave_component(mode, direction)
            * float(covariance(mode)[0, 0])
        )
    values["COMPLETE"] = math.fsum(values[sector] for sector in SECTORS)
    return values


def second_tree_sectors(
    parenthesisation: str,
    p_mode: tuple[int, int, int],
    q_mode: tuple[int, int, int],
) -> tuple[str, str]:
    derivative_sum = negate(add_modes(p_mode, q_mode))
    if parenthesisation == "X_PI_X_Q":
        outer = bony_sector(p_mode, negate(p_mode))
        inner = bony_sector(q_mode, derivative_sum)
    elif parenthesisation == "PI_XX_Q":
        value_sum = add_modes(p_mode, q_mode)
        outer = bony_sector(value_sum, negate(value_sum))
        inner = bony_sector(p_mode, q_mode)
    else:
        raise ValueError(parenthesisation)
    return outer, inner


def second_zero_chaos_forest(
    mode_list: list[tuple[int, int, int]],
    covariance,
    wave_component,
    direction: int,
    cone_radius: int,
) -> dict[str, Any]:
    by_parent: dict[str, dict[str, float]] = {}
    cone_by_parent: dict[str, float] = {}
    for parent in ("X_PI_X_Q", "PI_XX_Q"):
        totals = {f"{outer}/{inner}": 0.0 for outer in SECTORS for inner in SECTORS}
        cone_terms: list[float] = []
        for p_mode in mode_list:
            p_wave = wave_component(p_mode, direction)
            p_cov = float(covariance(p_mode)[0, 0])
            p_cone = all(cone_radius <= component < 2 * cone_radius for component in p_mode)
            for q_mode in mode_list:
                q_wave = wave_component(q_mode, direction)
                q_cov = float(covariance(q_mode)[0, 0])
                coefficient = -2.0 * p_wave * q_wave * p_cov * q_cov
                outer, inner = second_tree_sectors(parent, p_mode, q_mode)
                totals[f"{outer}/{inner}"] += coefficient
                q_cone = all(
                    cone_radius <= component < 2 * cone_radius for component in q_mode
                )
                if p_cone and q_cone:
                    cone_terms.append(coefficient)
        total = math.fsum(totals.values())
        cone = math.fsum(cone_terms)
        by_parent[parent] = totals | {
            "COMPLETE": total,
            "COMPLEMENT_OF_POSITIVE_CONE": total - cone,
        }
        cone_by_parent[parent] = cone
    return {"sector_totals": by_parent, "positive_cone": cone_by_parent}


def value_covariance_rows(
    cutoffs: list[int], covariance
) -> list[dict[str, float]]:
    rows = []
    for cutoff in cutoffs:
        covariance_at_zero = np.sum(
            [covariance(mode) for mode in modes(cutoff)], axis=0
        )
        rows.append(
            {
                "cutoff": cutoff,
                "trace": float(np.trace(covariance_at_zero)),
                "operator_norm": float(np.linalg.norm(covariance_at_zero, ord=2)),
                "minimum_eigenvalue": float(
                    np.linalg.eigvalsh(covariance_at_zero).min()
                ),
            }
        )
    return rows


def run(manifest_path: Path, output_path: Path) -> int:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    rows: list[dict[str, Any]] = []
    for key, authority in manifest["authority"].items():
        actual = digest(REPO / authority["path"])
        add(
            rows,
            f"authority_{key}_hash",
            actual == authority["sha256"],
            actual,
            authority["sha256"],
        )

    a1_manifest = json.loads(
        (REPO / manifest["authority"]["a1_manifest"]["path"]).read_text(
            encoding="utf-8"
        )
    )
    covariance, wave_component = covariance_builder(a1_manifest["parameters"])
    audit = manifest["audit"]
    tolerance = float(audit["tolerance"])
    cutoff = int(audit["classification_cutoff"])
    mode_list = modes(cutoff)

    counts = {
        "first_jet_cross": cross_matching_count(1, 2, 1),
        "wick_xx_q_single_cross": cross_matching_count(2, 2, 1),
        "wick_xx_q_double_cross": cross_matching_count(2, 2, 2),
        "raw_xx_q_second_chaos": cross_matching_count(2, 2, 1) + 1,
        "raw_xx_q_zero_chaos": cross_matching_count(2, 2, 2),
        "recursive_x_times_p3_single_cross": cross_matching_count(1, 3, 1),
        "recursive_x_times_p3_zero_chaos": cross_matching_count(1, 3, 2),
    }
    expected_counts = manifest["oracles"]["contraction_counts"]
    for name, expected in expected_counts.items():
        add(rows, f"contraction_count_{name}", counts[name] == expected, counts[name], expected)

    partition_failures = []
    partition_modes = modes(int(audit["partition_cutoff"]))
    for left in partition_modes:
        for right in partition_modes:
            weights = bony_weights(left, right)
            if sum(weights.values()) != 1 or set(weights.values()) - {0, 1}:
                partition_failures.append([left, right, weights])
    add(
        rows,
        "sharp_cube_bony_partition_exact",
        not partition_failures,
        len(partition_failures),
        0,
    )

    sparse_cutoff = int(audit["sparse_convolution_cutoff"])
    sparse_seed = int(audit["sparse_convolution_seed"])
    sparse_fields = [
        manufactured_sparse_field(sparse_seed + offset, sparse_cutoff)
        for offset in range(3)
    ]
    pair_direct = convolve_sparse(sparse_fields[0], sparse_fields[1])
    pair_bony = complete_bony(sparse_fields[0], sparse_fields[1])
    add(
        rows,
        "exact_sparse_bony_pair_reconstruction",
        pair_bony == pair_direct,
        len(pair_bony),
        len(pair_direct),
    )
    triple_direct = convolve_sparse(pair_direct, sparse_fields[2])
    nested_left, left_channels = complete_nested(
        *sparse_fields, parenthesisation="X_PI_X_Q"
    )
    nested_right, right_channels = complete_nested(
        *sparse_fields, parenthesisation="PI_XX_Q"
    )
    add(
        rows,
        "exact_sparse_left_parenthesisation_reconstruction",
        nested_left == triple_direct,
        len(nested_left),
        len(triple_direct),
    )
    add(
        rows,
        "exact_sparse_right_parenthesisation_reconstruction",
        nested_right == triple_direct,
        len(nested_right),
        len(triple_direct),
    )
    add(
        rows,
        "exact_sparse_parenthesisations_agree_only_after_complete_sum",
        nested_left == nested_right
        and any(left_channels[key] != right_channels[key] for key in left_channels),
        {
            "complete_equal": nested_left == nested_right,
            "different_channel_count": sum(
                left_channels[key] != right_channels[key] for key in left_channels
            ),
        },
        "complete equal and at least one channel differs",
    )
    maximum_output_radius = max(max(map(abs, mode)) for mode in triple_direct)
    add(
        rows,
        "exact_sparse_convolution_not_intermediately_truncated",
        maximum_output_radius > sparse_cutoff,
        maximum_output_radius,
        f">{sparse_cutoff}",
    )

    tree_partition_failures = {"X_PI_X_Q": 0, "PI_XX_Q": 0}
    for p_mode in partition_modes:
        for q_mode in partition_modes:
            for parent in tree_partition_failures:
                outer, inner = second_tree_sectors(parent, p_mode, q_mode)
                weight_sum = math.fsum(
                    int(outer == outer_candidate) * int(inner == inner_candidate)
                    for outer_candidate in SECTORS
                    for inner_candidate in SECTORS
                )
                if weight_sum != 1.0:
                    tree_partition_failures[parent] += 1
    for parent, failures in tree_partition_failures.items():
        add(rows, f"nested_partition_exact_{parent.lower()}", failures == 0, failures, 0)

    direction = int(audit["direction"])
    gradient = mixed_gradient_covariance(
        mode_list, covariance, wave_component, direction
    )
    add(
        rows,
        "common_even_value_derivative_covariance_zero",
        float(np.linalg.norm(gradient)) < tolerance,
        float(np.linalg.norm(gradient)),
        f"<{tolerance}",
    )
    parity_error = max(
        float(np.max(np.abs(covariance(mode) - covariance(negate(mode)))))
        for mode in mode_list
    )
    add(
        rows,
        "production_covariance_real_even",
        parity_error < tolerance,
        parity_error,
        f"<{tolerance}",
    )

    output = tuple(int(value) for value in audit["first_jet_output"])
    first_correctors = first_jet_correctors(
        mode_list, covariance, wave_component, output, direction
    )
    add(
        rows,
        "first_jet_complete_partition_p1_cancels",
        abs(first_correctors["COMPLETE"]) < tolerance,
        first_correctors["COMPLETE"],
        f"absolute<{tolerance}",
    )

    asymmetric_modes = [mode for mode in mode_list if mode[direction] >= 0]
    asymmetric_gradient = mixed_gradient_covariance(
        asymmetric_modes, covariance, wave_component, direction
    )
    asymmetric_norm = float(np.linalg.norm(asymmetric_gradient))
    add(
        rows,
        "asymmetric_regulator_breaks_mixed_covariance_cancellation",
        asymmetric_norm > float(audit["asymmetric_minimum"]),
        asymmetric_norm,
        f">{audit['asymmetric_minimum']}",
    )

    forest = second_zero_chaos_forest(
        mode_list,
        covariance,
        wave_component,
        direction,
        int(audit["cone_radius"]),
    )
    for parent, totals in forest["sector_totals"].items():
        add(
            rows,
            f"second_jet_complete_p0_cancels_{parent.lower()}",
            abs(float(totals["COMPLETE"])) < tolerance,
            totals["COMPLETE"],
            f"absolute<{tolerance}",
        )
        cone = float(forest["positive_cone"][parent])
        complement = float(totals["COMPLEMENT_OF_POSITIVE_CONE"])
        add(
            rows,
            f"positive_cone_coefficient_negative_{parent.lower()}",
            cone < -float(audit["cone_minimum_magnitude"]),
            cone,
            f"<-{audit['cone_minimum_magnitude']}",
        )
        add(
            rows,
            f"cone_cancelled_by_complete_complement_{parent.lower()}",
            abs(cone + complement) < tolerance,
            cone + complement,
            f"absolute<{tolerance}",
        )
    parent_difference = abs(
        float(forest["sector_totals"]["X_PI_X_Q"]["COMPLETE"])
        - float(forest["sector_totals"]["PI_XX_Q"]["COMPLETE"])
    )
    add(
        rows,
        "parenthesisations_agree_after_complete_reconstruction",
        parent_difference < tolerance,
        parent_difference,
        f"<{tolerance}",
    )

    value_rows = value_covariance_rows(
        [int(value) for value in audit["value_covariance_cutoffs"]], covariance
    )
    traces = [row["trace"] for row in value_rows]
    increments = [right - left for left, right in zip(traces, traces[1:])]
    add(rows, "value_covariance_positive", all(value > 0.0 for value in traces), traces, "all positive")
    add(rows, "value_covariance_cutoff_monotone", all(value > 0.0 for value in increments), increments, "all positive")
    add(
        rows,
        "value_covariance_shell_increment_decreases",
        increments[-1] < increments[0],
        increments,
        "last < first",
    )
    add(
        rows,
        "value_covariance_matrices_positive",
        all(row["minimum_eigenvalue"] > 0.0 for row in value_rows),
        [row["minimum_eigenvalue"] for row in value_rows],
        "all positive",
    )

    failures = [row for row in rows if row["status"] != "PASS"]
    passed = len(rows) - len(failures)
    payload = {
        "schema": "tect/a13-classii-coefficient-jet-forest-primary-result/1.0",
        "claim_id": manifest["claim_id"],
        "result_id": manifest["result_id"],
        "script_version": __version__,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": git_commit(),
        "platform": platform.platform(),
        "manifest": str(manifest_path.relative_to(REPO)).replace("\\", "/"),
        "manifest_sha256": digest(manifest_path),
        "derived": {
            "contraction_counts": counts,
            "mixed_gradient_covariance": gradient.tolist(),
            "first_jet_sector_correctors": first_correctors,
            "asymmetric_gradient_norm": asymmetric_norm,
            "second_zero_chaos_forest": forest,
            "value_covariance": value_rows,
        },
        "assertions": rows,
        "summary": {"passed": passed, "total": len(rows), "failed": len(failures)},
        "verdict": (
            "A13-CLASSII-COEFFICIENT-JET-FOREST-PRIMARY-PASS"
            if not failures
            else "FAIL"
        ),
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
    print("A13-CLASSII-COEFFICIENT-JET-FOREST-PRIMARY-PASS")
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

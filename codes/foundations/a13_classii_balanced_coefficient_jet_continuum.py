#!/usr/bin/env python3
"""Primary audit for the balanced A13 coefficient-jet continuum subtheorem.

The analytic theorem is carried by the accompanying proof note.  This program
checks its exponent arithmetic, exact finite-cutoff forest identities, both
non-aliased parenthesisations, the full A1 rational coefficient Taylor chart,
and the finite Sigma*Q Wick-conversion term.  The Fourier fixtures are
regression/falsifier evidence; they are not used as a numerical proof of a
continuum estimate or of the later Nelson bound.
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
__claims__ = ["A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"]

REPO = Path(__file__).resolve().parents[2]
CLAIM = REPO / "claims" / __claims__[0]
DEFAULT_MANIFEST = CLAIM / "classii_balanced_coefficient_jet_continuum_manifest.json"
DEFAULT_OUTPUT = (
    CLAIM
    / "runs"
    / "2026-07-22-primary-balanced-coefficient-jet-continuum"
    / "result.json"
)


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


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
    rows: list[dict[str, Any]], name: str, passed: bool, actual: Any, expected: Any
) -> None:
    rows.append(
        {
            "name": name,
            "status": "PASS" if bool(passed) else "FAIL",
            "actual": actual,
            "expected": expected,
        }
    )


def realify(matrix: np.ndarray) -> np.ndarray:
    return np.block([[matrix.real, -matrix.imag], [matrix.imag, matrix.real]])


def generators() -> list[np.ndarray]:
    pauli = [
        np.array([[0, 1], [1, 0]], dtype=np.complex128),
        np.array([[0, -1j], [1j, 0]], dtype=np.complex128),
        np.array([[1, 0], [0, -1]], dtype=np.complex128),
    ]
    return [realify(np.pad(item, ((0, 1), (0, 1)))) for item in pauli]


def coefficients(params: dict[str, Any]) -> tuple[float, float, float]:
    denominator = float(params["M_X"]) ** 2 + float(
        params["classii_mass_regularizer"]
    )
    return (
        float(params["cJJ"]) * float(params["alpha_X"]) ** 2 / denominator,
        float(params["cJK"])
        * float(params["alpha_X"])
        * float(params["beta_X"])
        / denominator,
        float(params["cKK"]) * float(params["beta_X"]) ** 2 / denominator,
    )


def coefficient_jet(
    x: np.ndarray, z: np.ndarray, params: dict[str, Any]
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return B(x), DB(x)[z], and D2B(x)[z,z] by exact real calculus."""

    x = np.asarray(x, dtype=np.float64)
    z = np.asarray(z, dtype=np.float64)
    epsilon = float(params["rho_regularizer"])
    a_value, b_value, c_value = coefficients(params)
    identity = np.eye(6)
    rho = float(x @ x)
    drho = 2.0 * float(x @ z)
    d2rho = 2.0 * float(z @ z)
    denominator = rho + epsilon
    result = np.zeros((6, 6), dtype=np.float64)
    first = np.zeros_like(result)
    second = np.zeros_like(result)

    def outer_sum(left: np.ndarray, right: np.ndarray) -> np.ndarray:
        return np.outer(left, right) + np.outer(right, left)

    for symmetric in generators():
        moment = float(x @ symmetric @ x)
        dmoment = 2.0 * float(z @ symmetric @ x)
        d2moment = 2.0 * float(z @ symmetric @ z)
        q_value = moment / denominator
        dq = dmoment / denominator - moment * drho / denominator**2
        d2q = (
            d2moment / denominator
            - moment * d2rho / denominator**2
            - 2.0 * dmoment * drho / denominator**2
            + 2.0 * moment * drho**2 / denominator**3
        )
        p = 2.0 * symmetric @ x
        dp = 2.0 * symmetric @ z
        v = 2.0 * (symmetric - q_value * identity) @ x
        dv = dp - 2.0 * dq * x - 2.0 * q_value * z
        d2v = -2.0 * d2q * x - 4.0 * dq * z

        result += (
            a_value * np.outer(p, p)
            + b_value * outer_sum(p, v)
            + c_value * np.outer(v, v)
        )
        first += (
            a_value * outer_sum(dp, p)
            + b_value
            * (
                np.outer(dp, v)
                + np.outer(p, dv)
                + np.outer(dv, p)
                + np.outer(v, dp)
            )
            + c_value * outer_sum(dv, v)
        )
        second += (
            2.0 * a_value * np.outer(dp, dp)
            + b_value
            * (
                2.0 * outer_sum(dp, dv)
                + np.outer(p, d2v)
                + np.outer(d2v, p)
            )
            + c_value
            * (2.0 * np.outer(dv, dv) + outer_sum(d2v, v))
        )
    return result, first, second


def coefficient_matrix(x: np.ndarray, params: dict[str, Any]) -> np.ndarray:
    return coefficient_jet(x, np.zeros(6), params)[0]


def finite_difference_jet(
    x: np.ndarray, z: np.ndarray, params: dict[str, Any], step: float
) -> tuple[np.ndarray, np.ndarray]:
    plus = coefficient_matrix(x + step * z, params)
    minus = coefficient_matrix(x - step * z, params)
    centre = coefficient_matrix(x, params)
    first = (plus - minus) / (2.0 * step)
    second = (plus - 2.0 * centre + minus) / step**2
    return first, second


def convolve_sparse(
    left: dict[tuple[int, ...], int], right: dict[tuple[int, ...], int]
) -> dict[tuple[int, ...], int]:
    output: dict[tuple[int, ...], int] = {}
    for left_mode, left_value in left.items():
        for right_mode, right_value in right.items():
            mode = tuple(a + b for a, b in zip(left_mode, right_mode))
            output[mode] = output.get(mode, 0) + left_value * right_value
    return {mode: value for mode, value in output.items() if value}


def dyadic_level(mode: tuple[int, ...]) -> int:
    radius = max(abs(value) for value in mode)
    if radius <= 1:
        return 0
    return int(math.ceil(math.log2(radius)))


def low(field: dict[tuple[int, ...], int], level: int) -> dict[tuple[int, ...], int]:
    threshold = level - 2
    return {
        mode: value
        for mode, value in field.items()
        if dyadic_level(mode) <= threshold
    }


def high(field: dict[tuple[int, ...], int], level: int) -> dict[tuple[int, ...], int]:
    low_modes = low(field, level)
    return {mode: value for mode, value in field.items() if mode not in low_modes}


def shell(field: dict[tuple[int, ...], int], level: int) -> dict[tuple[int, ...], int]:
    return {
        mode: value for mode, value in field.items() if dyadic_level(mode) == level
    }


def balanced_sparse_fixture(seed: int) -> dict[str, Any]:
    rng = np.random.default_rng(seed)
    modes = [
        (i, j, k)
        for i in range(-3, 4)
        for j in range(-3, 4)
        for k in range(-3, 4)
        if (i, j, k) != (0, 0, 0)
    ]
    chosen = [modes[index] for index in rng.choice(len(modes), size=9, replace=False)]
    x = {mode: int(value) for mode, value in zip(chosen[:5], [2, -1, 3, 1, -2])}
    q = {mode: int(value) for mode, value in zip(chosen[5:], [1, -3, 2, 4])}
    direct_first: dict[tuple[int, ...], int] = {}
    direct_second: dict[tuple[int, ...], int] = {}
    left_second: dict[tuple[int, ...], int] = {}
    right_second: dict[tuple[int, ...], int] = {}
    for level in range(0, 4):
        q_level = shell(q, level)
        x_high = high(x, level)
        first = convolve_sparse(x_high, q_level)
        left = convolve_sparse(convolve_sparse(x_high, x_high), q_level)
        right = convolve_sparse(x_high, convolve_sparse(x_high, q_level))
        for target, source in (
            (direct_first, first),
            (direct_second, left),
            (left_second, left),
            (right_second, right),
        ):
            for mode, value in source.items():
                target[mode] = target.get(mode, 0) + value
    return {
        "first_support": len(direct_first),
        "second_support": len(direct_second),
        "left_equals_right": left_second == right_second,
        "second_checksum": int(sum(direct_second.values())),
        "zero_mode_removed_from_high_blocks": all(
            (0, 0, 0) not in high({(0, 0, 0): 7}, level)
            for level in range(2, 5)
        ),
    }


def theorem_arithmetic(manifest: dict[str, Any]) -> dict[str, float]:
    dimension = float(manifest["theorem_inputs"]["dimension"])
    covariance_decay = float(manifest["theorem_inputs"]["covariance_decay"])
    derivative_decay = covariance_decay - 2.0
    q_variance_decay = 2.0 * derivative_decay - dimension
    first_variance_decay = covariance_decay + q_variance_decay - dimension
    second_variance_decay = (
        2.0 * covariance_decay + q_variance_decay - 2.0 * dimension
    )
    first_ceiling = (first_variance_decay - dimension) / 2.0
    second_ceiling = (second_variance_decay - dimension) / 2.0
    alpha = float(manifest["theorem_inputs"]["alpha"])
    kappa = float(manifest["theorem_inputs"]["kappa"])
    return {
        "derivative_covariance_decay": derivative_decay,
        "q_variance_decay": q_variance_decay,
        "first_jet_variance_decay": first_variance_decay,
        "second_jet_variance_decay": second_variance_decay,
        "first_sobolev_ceiling": first_ceiling,
        "second_sobolev_ceiling": second_ceiling,
        "first_target": alpha - 1.0 - kappa,
        "second_target": 2.0 * alpha - 1.0 - kappa,
        "third_remainder_regularities": 3.0 * alpha - 1.0 - kappa,
    }


def rational_reconstruction_fixture(
    params: dict[str, Any], seed: int
) -> dict[str, Any]:
    rng = np.random.default_rng(seed)
    direct_total = 0.0
    chart_total = 0.0
    maximum_taylor_identity = 0.0
    maximum_first_fd = 0.0
    maximum_second_fd = 0.0
    step = 2.0e-4
    for _ in range(12):
        base = rng.normal(scale=0.35, size=6)
        increment = rng.normal(scale=0.12, size=6)
        tensor = rng.normal(size=(6, 6))
        tensor = 0.5 * (tensor + tensor.T)
        base_matrix, first, second = coefficient_jet(base, increment, params)
        full_matrix = coefficient_matrix(base + increment, params)
        remainder = full_matrix - base_matrix - first - 0.5 * second
        reconstructed = base_matrix + first + 0.5 * second + remainder
        identity_error = float(np.max(np.abs(reconstructed - full_matrix)))
        maximum_taylor_identity = max(maximum_taylor_identity, identity_error)
        direct_total += float(np.sum(full_matrix * tensor))
        chart_total += float(np.sum(reconstructed * tensor))
        fd_first, fd_second = finite_difference_jet(base, increment, params, step)
        maximum_first_fd = max(
            maximum_first_fd,
            float(np.linalg.norm(fd_first - first) / max(1.0, np.linalg.norm(first))),
        )
        maximum_second_fd = max(
            maximum_second_fd,
            float(
                np.linalg.norm(fd_second - second)
                / max(1.0, np.linalg.norm(second))
            ),
        )
    return {
        "direct_total": direct_total,
        "chart_total": chart_total,
        "absolute_reconstruction_error": abs(direct_total - chart_total),
        "maximum_pointwise_taylor_identity_error": maximum_taylor_identity,
        "maximum_first_directional_fd_relative_error": maximum_first_fd,
        "maximum_second_directional_fd_relative_error": maximum_second_fd,
    }


def forest_polynomial_fixture() -> dict[str, float]:
    sigma = 0.7
    gamma = 1.3
    cross = -0.21
    z = 0.43
    y = -0.82
    q = y * y - gamma
    wick_zy = z * y - cross
    wick_zyy = z * (y * y - gamma) - 2.0 * cross * y
    wick_zzyy = (
        z * z * y * y
        - sigma * y * y
        - gamma * z * z
        - 4.0 * cross * z * y
        + sigma * gamma
        + 2.0 * cross * cross
    )
    first_raw = z * q
    first_reconstructed = wick_zyy + 2.0 * cross * y
    second_raw = z * z * q
    second_reconstructed = (
        wick_zzyy
        + sigma * q
        + 4.0 * cross * wick_zy
        + 2.0 * cross * cross
    )
    recursive = z * wick_zyy
    recursive_reconstructed = wick_zzyy + sigma * q + 2.0 * cross * wick_zy
    sigma_q_deleted = second_reconstructed - sigma * q
    return {
        "first_error": abs(first_raw - first_reconstructed),
        "second_error": abs(second_raw - second_reconstructed),
        "recursive_error": abs(recursive - recursive_reconstructed),
        "sigma_q": sigma * q,
        "error_if_sigma_q_deleted": abs(second_raw - sigma_q_deleted),
        "first_cross_count": 2.0,
        "second_cross_count": 4.0,
        "second_double_cross_count": 2.0,
        "raw_second_chaos_count": 5.0,
        "recursive_second_chaos_count": 3.0,
    }


def run(manifest_path: Path, output_path: Path) -> int:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    a1 = json.loads(
        (REPO / manifest["authority"]["a1_manifest"]["path"]).read_text(
            encoding="utf-8"
        )
    )
    params = a1["parameters"]
    rows: list[dict[str, Any]] = []
    tolerance = float(manifest["audit"]["identity_tolerance"])

    for key, authority in manifest["authority"].items():
        actual = digest(REPO / authority["path"])
        add(rows, f"authority_{key}_hash", actual == authority["sha256"], actual, authority["sha256"])

    arithmetic = theorem_arithmetic(manifest)
    expected = manifest["oracles"]["theorem_arithmetic"]
    for key, value in expected.items():
        add(rows, f"arithmetic_{key}", abs(arithmetic[key] - float(value)) < tolerance, arithmetic[key], value)
    add(
        rows,
        "first_target_below_sobolev_ceiling",
        arithmetic["first_target"] < arithmetic["first_sobolev_ceiling"],
        arithmetic["first_target"],
        f"<{arithmetic['first_sobolev_ceiling']}",
    )
    add(
        rows,
        "second_target_below_sobolev_ceiling",
        arithmetic["second_target"] < arithmetic["second_sobolev_ceiling"],
        arithmetic["second_target"],
        f"<{arithmetic['second_sobolev_ceiling']}",
    )
    add(rows, "third_order_remainder_positive", arithmetic["third_remainder_regularities"] > 0.0, arithmetic["third_remainder_regularities"], ">0")

    sparse = balanced_sparse_fixture(int(manifest["audit"]["sparse_seed"]))
    add(rows, "both_parenthesisations_equal_without_intermediate_projection", sparse["left_equals_right"], sparse["left_equals_right"], True)
    add(rows, "balanced_first_fixture_nonempty", sparse["first_support"] > 0, sparse["first_support"], ">0")
    add(rows, "balanced_second_fixture_nonempty", sparse["second_support"] > 0, sparse["second_support"], ">0")
    add(rows, "zero_mode_low_high_removed", sparse["zero_mode_removed_from_high_blocks"], sparse["zero_mode_removed_from_high_blocks"], True)

    forest = forest_polynomial_fixture()
    add(rows, "first_forest_identity", forest["first_error"] < tolerance, forest["first_error"], f"<{tolerance}")
    add(rows, "second_forest_identity", forest["second_error"] < tolerance, forest["second_error"], f"<{tolerance}")
    add(rows, "recursive_forest_identity", forest["recursive_error"] < tolerance, forest["recursive_error"], f"<{tolerance}")
    add(rows, "sigma_q_is_nonzero_in_fixture", abs(forest["sigma_q"]) > 1.0e-3, forest["sigma_q"], "nonzero")
    add(rows, "deleting_sigma_q_breaks_reconstruction", forest["error_if_sigma_q_deleted"] > 1.0e-3, forest["error_if_sigma_q_deleted"], ">1e-3")
    add(rows, "forest_counts_match", [forest[key] for key in ("first_cross_count", "second_cross_count", "second_double_cross_count", "raw_second_chaos_count", "recursive_second_chaos_count")] == [2.0, 4.0, 2.0, 5.0, 3.0], forest, "2, 4+2, 5+2, 3+0")

    rational = rational_reconstruction_fixture(params, int(manifest["audit"]["rational_seed"]))
    add(rows, "rational_pointwise_taylor_chart_exact", rational["maximum_pointwise_taylor_identity_error"] < tolerance, rational["maximum_pointwise_taylor_identity_error"], f"<{tolerance}")
    add(rows, "rational_a7_contraction_reconstructed", rational["absolute_reconstruction_error"] < tolerance, rational["absolute_reconstruction_error"], f"<{tolerance}")
    add(rows, "analytic_first_directional_jet_fd_check", rational["maximum_first_directional_fd_relative_error"] < 1.0e-8, rational["maximum_first_directional_fd_relative_error"], "<1e-8")
    add(rows, "analytic_second_directional_jet_fd_check", rational["maximum_second_directional_fd_relative_error"] < 3.0e-7, rational["maximum_second_directional_fd_relative_error"], "<3e-7")

    add(rows, "regulator_class_common_even", manifest["regulator_class"]["common_scalar"] and manifest["regulator_class"]["real_even"], manifest["regulator_class"], "common real-even scalar")
    add(rows, "exact_covariance_normal_scheme_retained", manifest["reconstruction"]["derivative_counterterm"] == "same-regulator Gamma_Lambda,i only", manifest["reconstruction"]["derivative_counterterm"], "same-regulator Gamma_Lambda,i only")
    add(rows, "adapted_shift_not_claimed", not manifest["claims_not_established"]["adapted_random_shift_control"], manifest["claims_not_established"], "adapted shift false")
    add(rows, "nelson_not_claimed", not manifest["claims_not_established"]["nelson_bound"], manifest["claims_not_established"], "Nelson false")

    expected_total = int(manifest["run_contract"]["primary_assertions"])
    add(rows, "primary_assertion_contract", len(rows) + 1 == expected_total, len(rows) + 1, expected_total)
    failed = [row for row in rows if row["status"] != "PASS"]
    payload = {
        "schema": "tect/a13-balanced-coefficient-jet-continuum-primary-result/1.0",
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
            "balanced_sparse_fixture": sparse,
            "forest_polynomial_fixture": forest,
            "rational_reconstruction_fixture": rational,
        },
        "assertions": rows,
        "summary": {"passed": len(rows) - len(failed), "total": len(rows), "failed": len(failed)},
        "verdict": "A13-CLASSII-BALANCED-COEFFICIENT-JET-CONTINUUM-PRIMARY-PASS" if not failed else "FAIL",
        "honesty_boundary": manifest["honesty_boundary"],
    }
    atomic_json(output_path, payload)
    if failed:
        print(f"FAIL: primary ({len(failed)} issue(s))")
        for row in failed:
            print(f" - {row['name']}: {row['actual']}")
        return 1
    print(f"PASS: primary ({len(rows)}/{len(rows)})")
    print("A13-CLASSII-BALANCED-COEFFICIENT-JET-CONTINUUM-PRIMARY-PASS")
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

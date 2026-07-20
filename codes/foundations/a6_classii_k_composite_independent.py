#!/usr/bin/env python3
"""Non-importing audit of the A6 fixed-floor K-composite package.

This route uses direct mode enumeration rather than radial cube convolution,
an explicit asymmetric-regulator counterexample, and independent quadrature
for the two local concentration proxies.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any

import numpy as np

__version__ = "1.0.0"
__first_issued__ = "2026-07-20"
__version_issued__ = "2026-07-20"
__claims__ = ["A6-CLASSII-K-COMPOSITE-DEFINITION"]

REPO = Path(__file__).resolve().parents[2]
CLAIM = __claims__[0]
CLAIM_DIR = REPO / "claims" / CLAIM
MANIFEST = CLAIM_DIR / "classii_k_composite_manifest.json"
DEFAULT_OUTPUT = CLAIM_DIR / "runs" / "2026-07-20-independent-k-composite" / "result.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_commit() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=REPO, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def add(name: str, condition: bool, actual: Any, expected: Any, rows: list[dict[str, Any]]) -> None:
    rows.append(
        {"name": name, "status": "PASS" if bool(condition) else "FAIL", "actual": actual, "expected": expected}
    )


def production_mass(params: dict[str, Any]) -> np.ndarray:
    anchor = np.asarray(params["z0"], dtype=np.float64)
    return np.diag(np.asarray(params["family_masses"], dtype=np.float64)) + float(params["k_lock"]) * (
        np.eye(3) - np.outer(anchor, anchor) / float(anchor @ anchor)
    )


def direct_component_table(max_squared_index: int, params: dict[str, Any]) -> np.ndarray:
    squared = np.arange(max_squared_index + 1, dtype=np.float64)
    alpha2 = (2.0 * math.pi / float(params["Lx"])) ** 2
    k2 = alpha2 * squared
    scalar = float(params["r"]) + float(params["Z"]) * k2 + float(params["Y"]) * k2 * k2
    matrices = scalar[:, None, None] * np.eye(3)[None, :, :] + production_mass(params)[None, :, :]
    inverses = np.linalg.inv(matrices)
    return inverses[:, 0, 0]


def yz_multiplicities(cutoff: int) -> np.ndarray:
    axis = np.arange(-cutoff, cutoff + 1, dtype=np.int64)
    squared = axis * axis
    return np.bincount((squared[:, None] + squared[None, :]).reshape(-1)).astype(np.int64, copy=False)


def direct_area_variance(
    domain_cutoff: int,
    params: dict[str, Any],
    scheme: str,
    scale: int | None = None,
) -> float:
    scale = domain_cutoff if scale is None else scale
    yz_counts = yz_multiplicities(domain_cutoff)
    component = direct_component_table(3 * domain_cutoff * domain_cutoff, params)
    alpha = 2.0 * math.pi / float(params["Lx"])
    total = 0.0
    radial_yz = np.arange(len(yz_counts), dtype=np.int64)
    for nx in range(-domain_cutoff, domain_cutoff + 1):
        squared = nx * nx + radial_yz
        if scheme == "cube":
            multiplier = np.ones_like(squared, dtype=np.float64)
        elif scheme == "ball":
            multiplier = (squared <= scale * scale).astype(np.float64)
        elif scheme == "smooth":
            multiplier = np.exp(-np.power(np.sqrt(squared) / float(scale), 8.0))
        else:
            raise ValueError(f"unknown scheme {scheme}")
        total += float(np.sum(yz_counts * (alpha * nx) ** 2 * component[squared] ** 2 * multiplier**4))
    volume = float(params["Lx"]) * float(params["Ly"]) * float(params["Lz"])
    return total / volume


def area_audit(params: dict[str, Any], audit: dict[str, Any]) -> dict[str, Any]:
    reference_cutoff = int(audit["independent_area_reference_cutoff"])
    cutoffs = [int(value) for value in audit["independent_area_cutoffs"]]
    reference = direct_area_variance(reference_cutoff, params, "cube")
    rows: list[dict[str, float]] = []
    for cutoff in cutoffs:
        cube_value = direct_area_variance(cutoff, params, "cube")
        ball_value = direct_area_variance(cutoff, params, "ball", cutoff)
        smooth_value = direct_area_variance(reference_cutoff, params, "smooth", cutoff)
        rows.append(
            {
                "cutoff": cutoff,
                "sharp_cube": cube_value,
                "sharp_ball": ball_value,
                "smooth_even": smooth_value,
                "cube_tail": reference - cube_value,
                "ball_tail": reference - ball_value,
                "smooth_tail": reference - smooth_value,
            }
        )
    slopes: dict[str, float] = {}
    for key in ("cube_tail", "ball_tail", "smooth_tail"):
        x = np.log(np.asarray([row["cutoff"] for row in rows[-3:]], dtype=np.float64))
        y = np.log(np.asarray([row[key] for row in rows[-3:]], dtype=np.float64))
        slopes[key] = float(np.polyfit(x, y, 1)[0])
    return {"reference_cutoff": reference_cutoff, "reference_variance": reference, "rows": rows, "tail_slopes": slopes}


def asymmetric_q4_anomaly(cutoff: int, length: float, correlation: float, phase_difference: float) -> float:
    axis = np.arange(-cutoff, cutoff + 1, dtype=np.int64)
    squared_axis = axis * axis
    yz_counts = np.bincount((squared_axis[:, None] + squared_axis[None, :]).reshape(-1)).astype(np.int64, copy=False)
    radial_yz = np.arange(len(yz_counts), dtype=np.float64)
    alpha = 2.0 * math.pi / length
    volume = length**3
    total = 0.0
    for nx in axis:
        squared = float(nx * nx) + radial_yz
        k2 = alpha * alpha * squared
        covariance = 1.0 / (1.0 + k2 * k2)
        total += float(
            np.sum(yz_counts * (alpha * nx) * math.sin(phase_difference * float(nx) / cutoff) * covariance)
        )
    return correlation * total / volume


def coefficients(params: dict[str, Any]) -> tuple[float, float, float]:
    denominator = float(params["M_X"]) ** 2 + float(params["classii_mass_regularizer"])
    return (
        float(params["cJJ"]) * float(params["alpha_X"]) ** 2 / denominator,
        float(params["cJK"]) * float(params["alpha_X"]) * float(params["beta_X"]) / denominator,
        float(params["cKK"]) * float(params["beta_X"]) ** 2 / denominator,
    )


def independent_counterterm(params: dict[str, Any], delta_cube: float) -> dict[str, Any]:
    a_value, b_value, c_value = coefficients(params)
    eigenvalues = np.linalg.eigvalsh(np.asarray([[a_value, b_value], [b_value, c_value]]))
    g_value = a_value + 2.0 * b_value + c_value
    h_value = 9.0 * g_value
    w_infinity = h_value - 6.0 * b_value - 3.0 * c_value
    gamma = float(params["gamma"])
    amplitude = (2.0 * delta_cube * w_infinity / gamma) ** 0.25
    density = amplitude * amplitude
    energy = -(2.0 / 3.0) * delta_cube * w_infinity * density
    eps_remainder_coefficient = 6.0 * b_value + 0.75 * c_value
    return {
        "a": a_value,
        "b": b_value,
        "c": c_value,
        "g": g_value,
        "h": h_value,
        "lambda_min": float(eigenvalues[0]),
        "lower_bound_coefficient": 9.0 * float(eigenvalues[0]),
        "w_infinity": w_infinity,
        "epsilon_remainder_coefficient": eps_remainder_coefficient,
        "amplitude_over_N_quarter_limit": amplitude,
        "rho_over_sqrt_N_limit": density,
        "energy_density_over_N_3_2_limit": energy,
    }


def gauss_legendre_unit(order: int) -> tuple[np.ndarray, np.ndarray]:
    nodes, weights = np.polynomial.legendre.leggauss(order)
    return 0.5 * (nodes + 1.0), 0.5 * weights


def independent_proxy_quadrature(g_value: float, h_value: float, order: int) -> dict[str, Any]:
    laguerre_nodes, laguerre_weights = np.polynomial.laguerre.laggauss(order)
    mean_norm = float(np.sum(laguerre_weights * laguerre_nodes) / h_value**2)
    mean_first = float(np.sum(laguerre_weights * laguerre_nodes**2) / h_value**3)
    mean_second = float(np.sum(laguerre_weights * laguerre_nodes**3) / h_value**4)
    mean_value = mean_first / mean_norm
    mean_variance = mean_second / mean_norm - mean_value**2

    u, weights = gauss_legendre_unit(order)
    exact_integrals: list[float] = []
    for moment in range(3):
        integrand = 2.0 * np.power(u, 4 - 2 * moment) * np.power(1.0 - u * u, moment + 1)
        exact_integrals.append(float(np.sum(weights * integrand) / (2.0 * g_value) ** (moment + 2)))
    exact_mean = exact_integrals[1] / exact_integrals[0]
    exact_variance = exact_integrals[2] / exact_integrals[0] - exact_mean**2
    return {
        "mean_proxy": {"normalization": mean_norm, "mean": mean_value, "variance": mean_variance},
        "derivative_proxy": {
            "normalization": exact_integrals[0],
            "mean": exact_mean,
            "variance": exact_variance,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    production_path = REPO / manifest["authority"]["production_functional_manifest"]["path"]
    production = json.loads(production_path.read_text(encoding="utf-8"))
    params = production["parameters"]
    audit = manifest["audit"]
    assertions: list[dict[str, Any]] = []

    add(
        "production_manifest_hash_matches",
        sha256(production_path) == manifest["authority"]["production_functional_manifest"]["sha256"],
        sha256(production_path),
        manifest["authority"]["production_functional_manifest"]["sha256"],
        assertions,
    )
    area = area_audit(params, audit)
    for name, slope in area["tail_slopes"].items():
        add(f"direct_{name}_has_cubic_variance_tail", -4.0 < slope < -2.0, slope, "between -4 and -2", assertions)
    last = area["rows"][-1]
    spread = max(last[key] for key in ("sharp_cube", "sharp_ball", "smooth_even")) - min(last[key] for key in ("sharp_cube", "sharp_ball", "smooth_even"))
    add("direct_even_schemes_approach_one_limit", spread / area["reference_variance"] < float(audit["independent_scheme_relative_tolerance"]), spread / area["reference_variance"], audit["independent_scheme_relative_tolerance"], assertions)

    anomaly_rows = [
        {
            "cutoff": cutoff,
            "common_phase": asymmetric_q4_anomaly(cutoff, float(params["Lx"]), 0.4, 0.0),
            "split_phase": asymmetric_q4_anomaly(cutoff, float(params["Lx"]), 0.4, 0.7),
        }
        for cutoff in (16, 32, 64, 96)
    ]
    add("common_component_regulator_has_zero_area_drift", max(abs(row["common_phase"]) for row in anomaly_rows) < 1.0e-15, [row["common_phase"] for row in anomaly_rows], "all zero", assertions)
    last_change = abs(anomaly_rows[-1]["split_phase"] - anomaly_rows[-2]["split_phase"]) / abs(anomaly_rows[-1]["split_phase"])
    add("component_split_asymmetric_regulator_has_stable_nonzero_anomaly", abs(anomaly_rows[-1]["split_phase"]) > 1.0e-4 and last_change < 0.08, {"rows": anomaly_rows, "last_relative_change": last_change}, "nonzero and last change <8%", assertions)

    delta_cube = float(manifest["constants"]["delta_cube"])
    counterterm = independent_counterterm(params, delta_cube)
    add("ClassII_coefficient_matrix_is_strictly_positive", counterterm["lambda_min"] > 0.0, counterterm["lambda_min"], ">0", assertions)
    add("W_lower_bound_coefficient_is_positive", counterterm["lower_bound_coefficient"] > 0.0, counterterm["lower_bound_coefficient"], ">0", assertions)
    add("homogeneous_naive_subtraction_coefficient_is_negative", counterterm["energy_density_over_N_3_2_limit"] < 0.0, counterterm["energy_density_over_N_3_2_limit"], "<0", assertions)

    proxy = independent_proxy_quadrature(counterterm["g"], counterterm["h"], int(audit["quadrature_order"]))
    mean_expected = 2.0 / counterterm["h"]
    mean_variance_expected = 2.0 / counterterm["h"] ** 2
    exact_expected = 2.0 / (3.0 * counterterm["g"])
    exact_variance_expected = 14.0 / (9.0 * counterterm["g"] ** 2)
    add("independent_mean_proxy_quadrature_matches_Gamma_law", abs(proxy["mean_proxy"]["mean"] - mean_expected) / mean_expected < 1.0e-10 and abs(proxy["mean_proxy"]["variance"] - mean_variance_expected) / mean_variance_expected < 1.0e-9, proxy["mean_proxy"], {"mean": mean_expected, "variance": mean_variance_expected}, assertions)
    add("independent_derivative_proxy_quadrature_matches_beta_prime_law", abs(proxy["derivative_proxy"]["mean"] - exact_expected) / exact_expected < 1.0e-10 and abs(proxy["derivative_proxy"]["variance"] - exact_variance_expected) / exact_variance_expected < 1.0e-9, proxy["derivative_proxy"], {"mean": exact_expected, "variance": exact_variance_expected}, assertions)
    add("two_local_proxies_are_not_identified", abs(proxy["mean_proxy"]["mean"] - proxy["derivative_proxy"]["mean"]) > 1.0, {"mean_proxy": proxy["mean_proxy"]["mean"], "derivative_proxy": proxy["derivative_proxy"]["mean"]}, "distinct limits", assertions)

    a6_source = (REPO / manifest["authority"]["a6_uv_source"]["path"]).read_text(encoding="utf-8")
    add("A6_W_docstring_has_no_extra_factor_three", "~ delta_cube N W(Psi)" in a6_source and "~ 3 delta_cube N W(Psi)" not in a6_source, "corrected convention text found", "W is already 3*sum", assertions)
    add("arbitrary_regulator_independence_is_explicitly_forbidden", "arbitrary asymmetric regulator independence" in manifest["honesty_boundary"]["excluded"], manifest["honesty_boundary"]["excluded"], "explicit exclusion", assertions)
    add("full_field_bare_concentration_is_explicitly_open", "full-field bare concentration theorem" in manifest["honesty_boundary"]["excluded"], manifest["honesty_boundary"]["excluded"], "explicit exclusion", assertions)

    passed = sum(row["status"] == "PASS" for row in assertions)
    verdict = "A6-CLASSII-K-COMPOSITE-INDEPENDENT-PASS" if passed == len(assertions) else "A6-CLASSII-K-COMPOSITE-INDEPENDENT-FAIL"
    output = {
        "schema": "tect/a6-classii-k-composite-independent-result/1.0",
        "claim_id": CLAIM,
        "script_version": __version__,
        "verdict": verdict,
        "scope": manifest["scope"],
        "derived": {
            "area_lift": area,
            "asymmetric_negative_control": anomaly_rows,
            "counterterm": counterterm,
            "local_proxy_quadrature": proxy,
        },
        "assertions": assertions,
        "assertion_summary": {"passed": passed, "total": len(assertions)},
        "failures": [row["name"] for row in assertions if row["status"] != "PASS"],
        "environment": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "platform": platform.platform(),
            "git_commit": git_commit(),
            "deterministic": True,
        },
        "not_closed_here": manifest["honesty_boundary"]["excluded"],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"{passed}/{len(assertions)} PASS")
    print(verdict)
    print(f"Direct area-tail slopes: {area['tail_slopes']}")
    print(f"Asymmetric anomaly: {anomaly_rows[-1]['split_phase']:.12g}")
    print(f"Evidence: {args.output.resolve()}")
    return 0 if passed == len(assertions) else 1


if __name__ == "__main__":
    raise SystemExit(main())

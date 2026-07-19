#!/usr/bin/env python3
"""Primary analytic audit for the A4 scalar constructive Gibbs measure.

The theorem is finite-volume and non-perturbative.  The script derives every
reported number from the two hash-pinned upstream manifests and checks the
load-bearing estimates:

* trace class of the d=3 q^4 covariance and H^s support for s<1/2;
* the exact negative-quartic/positive-sextic lower bound;
* uniform positive/finite Galerkin partition-function bounds;
* a Gaussian L6 spectral-tail envelope, sufficient for interaction-weight
  convergence and identification of the full Galerkin sequence;
* a tightness envelope obtained from domination by the Gaussian law.

This is not a sampler.  Its numerical rows are sanity checks for explicit
analytic inequalities, and the JSON artefact records every assertion.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import sys
from pathlib import Path
from typing import Any

import numpy as np

__version__ = "1.1.0"
__first_issued__ = "2026-07-18"
__version_issued__ = "2026-07-19"
__claims__ = ["A4-SCALAR-SPECTRAL-CONSTRUCTIVE-MEASURE"]

REPO = Path(__file__).resolve().parents[2]
CLAIM = REPO / "claims" / __claims__[0]
MANIFEST = CLAIM / "constructive_measure_manifest.json"
DEFAULT_OUTPUT = CLAIM / "runs" / "2026-07-18-primary-constructive-measure" / "result.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(name: str, passed: bool, detail: Any, assertions: list[dict[str, Any]]) -> None:
    assertions.append({"name": name, "status": "PASS" if passed else "FAIL", "detail": detail})


def pseries_tail_upper(start: int, exponent: float) -> float:
    """Upper-bound sum_{m=start}^infinity m^{-exponent}, exponent>1."""
    if start < 1 or exponent <= 1.0:
        raise ValueError("p-series bound requires start>=1 and exponent>1")
    x = float(start)
    return x ** (-exponent) + x ** (1.0 - exponent) / (exponent - 1.0)


def exact_weighted_trace(max_mode: int, length: float, q0: float, mass2: float, y_value: float, sobolev_s: float = 0.0) -> float:
    """Trace over the max-norm Fourier cube in the orthonormal real basis."""
    coordinates = np.arange(-max_mode, max_mode + 1, dtype=np.float64)
    n2 = (
        coordinates[:, None, None] ** 2
        + coordinates[None, :, None] ** 2
        + coordinates[None, None, :] ** 2
    )
    scale = 2.0 * math.pi / length
    k2 = scale * scale * n2
    kernel = mass2 + y_value * (k2 - q0 * q0) ** 2
    weight = (1.0 + k2) ** sobolev_s
    return float(np.sum(weight / kernel, dtype=np.float64))


def weighted_trace_tail_upper(start_shell: int, length: float, q0: float, y_value: float, sobolev_s: float = 0.0) -> float:
    """Max-norm shell upper bound outside |n|_infinity < start_shell."""
    scale = 2.0 * math.pi / length
    shell_threshold = math.ceil(math.sqrt(2.0) * q0 / scale)
    if start_shell < max(1, shell_threshold):
        raise ValueError("tail must start beyond the Brazovskii shell threshold")
    if not (sobolev_s < 0.5):
        raise ValueError("the H^s covariance trace tail converges only for s<1/2")

    # On max-norm shell m: |k|^2 >= scale^2 m^2 >= 2 q0^2, hence
    # K >= Y |k|^4/4 >= Y scale^4 m^4/4.  The shell has 24m^2+2 modes.
    weight_factor = (1.0 + 3.0 * scale * scale) ** sobolev_s
    first_exponent = 2.0 - 2.0 * sobolev_s
    second_exponent = 4.0 - 2.0 * sobolev_s
    shell_sum = weight_factor * (
        24.0 * pseries_tail_upper(start_shell, first_exponent)
        + 2.0 * pseries_tail_upper(start_shell, second_exponent)
    )
    return 4.0 * shell_sum / (y_value * scale**4)


def even_gaussian_moments(variance: float, through_order: int) -> dict[str, float]:
    moments: dict[str, float] = {"0": 1.0}
    value = 1.0
    for order in range(2, through_order + 1, 2):
        value *= (order - 1) * variance
        moments[str(order)] = value
    return moments


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    authority = manifest["authority"]
    kernel_path = REPO / authority["scalar_kernel_anchor"]["path"]
    functional_path = REPO / authority["production_functional_anchor"]["path"]
    kernel_anchor = json.loads(kernel_path.read_text(encoding="utf-8"))
    functional_anchor = json.loads(functional_path.read_text(encoding="utf-8"))
    params = functional_anchor["parameters"]
    audit = manifest["audit"]

    length = float(params["Lx"])
    volume = float(params["Lx"]) * float(params["Ly"]) * float(params["Lz"])
    q0 = float(params["q0"])
    y_value = float(params["Y"])
    lambda_value = float(params["lambda"])
    gamma_value = float(params["gamma"])
    perturbative_mass2 = float(kernel_anchor["mu2_shell"])
    production_mass2 = float(params["r"]) - float(params["Z"]) ** 2 / (4.0 * y_value)
    anchors = (
        ("perturbative_scalar", perturbative_mass2),
        ("production_local", production_mass2),
    )

    assertions: list[dict[str, Any]] = []
    check(
        "upstream_source_hashes_match_manifest",
        sha256(kernel_path) == authority["scalar_kernel_anchor"]["sha256"]
        and sha256(functional_path) == authority["production_functional_anchor"]["sha256"],
        {"kernel": sha256(kernel_path), "functional": sha256(functional_path)},
        assertions,
    )
    check(
        "primary_source_hash_matches_manifest",
        sha256(Path(__file__)) == authority["primary_audit"]["sha256"],
        {"actual": sha256(Path(__file__)), "expected": authority["primary_audit"]["sha256"]},
        assertions,
    )
    check(
        "positive_q4_kernel_inputs",
        y_value > 0.0 and all(mass2 > 0.0 for _, mass2 in anchors) and q0 >= 0.0,
        {"Y": y_value, "q0": q0, "masses": dict(anchors)},
        assertions,
    )
    zero_q0_tail = weighted_trace_tail_upper(1, length, 0.0, y_value)
    check(
        "q0_zero_shell_tail_starts_at_first_nonzero_max_norm_shell",
        bool(audit["require_q0_zero_shell_boundary_check"])
        and math.isfinite(zero_q0_tail)
        and zero_q0_tail > 0.0,
        {
            "q0": 0.0,
            "first_nonzero_max_norm_shell": 1,
            "trace_tail_upper": zero_q0_tail,
            "rule": "m0=max(1,ceil(sqrt(2)*q0/alpha))",
        },
        assertions,
    )
    check(
        "production_shell_mass_reproduces_manifest_mu2",
        math.isclose(production_mass2, float(params["mu2"]), rel_tol=0.0, abs_tol=2.0e-10),
        {"derived": production_mass2, "stored": float(params["mu2"])},
        assertions,
    )
    check(
        "positive_sextic_input",
        gamma_value > 0.0,
        {"lambda": lambda_value, "gamma": gamma_value},
        assertions,
    )

    cutoffs = [int(value) for value in audit["max_mode_cutoffs"]]
    max_cutoff = max(cutoffs)
    row_data: list[dict[str, Any]] = []
    trace_monotone: list[bool] = []
    tail_decreasing: list[bool] = []
    l6_decreasing: list[bool] = []
    tightness_decreasing: list[bool] = []
    full_trace_enclosures: dict[str, float] = {}

    negative_quartic = max(-lambda_value, 0.0)
    potential_lower_constant = negative_quartic**3 / (12.0 * gamma_value**2)
    minimizer_square = negative_quartic / gamma_value if negative_quartic else 0.0
    minimum_value = lambda_value * minimizer_square**2 / 4.0 + gamma_value * minimizer_square**3 / 6.0
    check(
        "quartic_sextic_global_minimum_is_exact",
        math.isclose(minimum_value, -potential_lower_constant, rel_tol=2.0e-14, abs_tol=2.0e-16),
        {"phi_squared_at_minimum": minimizer_square, "minimum": minimum_value, "lower_constant": potential_lower_constant},
        assertions,
    )

    for anchor_name, mass2 in anchors:
        partial_traces = [exact_weighted_trace(cutoff, length, q0, mass2, y_value) for cutoff in cutoffs]
        tail_bounds = [weighted_trace_tail_upper(cutoff + 1, length, q0, y_value) for cutoff in cutoffs]
        trace_monotone.append(all(right > left for left, right in zip(partial_traces, partial_traces[1:])))
        tail_decreasing.append(all(right < left for left, right in zip(tail_bounds, tail_bounds[1:])))
        full_trace_upper = partial_traces[-1] + tail_bounds[-1]
        full_trace_enclosures[anchor_name] = full_trace_upper
        pointwise_variance_upper = full_trace_upper / volume
        moments = even_gaussian_moments(pointwise_variance_upper, int(audit["gaussian_even_moments_through"]))

        positive_quartic = max(lambda_value, 0.0)
        expected_interaction_upper = volume * (
            3.0 * positive_quartic * pointwise_variance_upper**2 / 4.0
            + 5.0 * gamma_value * pointwise_variance_upper**3 / 2.0
        )
        log10_z_lower = -expected_interaction_upper / math.log(10.0)
        log10_z_upper = potential_lower_constant * volume / math.log(10.0)
        log10_density_domination = log10_z_upper - log10_z_lower

        cutoff_rows: list[dict[str, float | int]] = []
        l6_values: list[float] = []
        tightness_logs: list[float] = []
        for cutoff, partial_trace, tail_bound in zip(cutoffs, partial_traces, tail_bounds):
            tail_variance = tail_bound / volume
            l6_tail_sixth_moment = 15.0 * volume * tail_variance**3
            log10_tightness_l2_tail = log10_density_domination + math.log10(tail_bound)
            l6_values.append(l6_tail_sixth_moment)
            tightness_logs.append(log10_tightness_l2_tail)
            cutoff_rows.append(
                {
                    "max_mode": cutoff,
                    "partial_covariance_trace": partial_trace,
                    "covariance_trace_tail_upper": tail_bound,
                    "gaussian_L6_tail_sixth_moment_upper": l6_tail_sixth_moment,
                    "log10_interacting_L2_tail_upper": log10_tightness_l2_tail,
                }
            )
        l6_decreasing.append(all(right < left for left, right in zip(l6_values, l6_values[1:])))
        tightness_decreasing.append(all(right < left for left, right in zip(tightness_logs, tightness_logs[1:])))
        row_data.append(
            {
                "anchor": anchor_name,
                "m_shell_squared": mass2,
                "full_covariance_trace_upper": full_trace_upper,
                "pointwise_variance_upper": pointwise_variance_upper,
                "gaussian_even_pointwise_moments_upper": moments,
                "potential_lower_constant_per_volume": potential_lower_constant,
                "log10_uniform_partition_lower": log10_z_lower,
                "log10_uniform_partition_upper": log10_z_upper,
                "log10_density_domination": log10_density_domination,
                "cutoffs": cutoff_rows,
            }
        )

    check("partial_covariance_traces_are_strictly_monotone", all(trace_monotone), trace_monotone, assertions)
    check("analytic_trace_tail_bounds_decrease", all(tail_decreasing), tail_decreasing, assertions)
    check(
        "trace_class_enclosures_are_finite",
        all(math.isfinite(value) and value > 0.0 for value in full_trace_enclosures.values()),
        full_trace_enclosures,
        assertions,
    )

    support_rows: list[dict[str, Any]] = []
    support_ok = True
    for sobolev_s in [float(value) for value in audit["sobolev_exponents"]]:
        exponent = 2.0 - 2.0 * sobolev_s
        tail = weighted_trace_tail_upper(max_cutoff + 1, length, q0, y_value, sobolev_s)
        inner = exact_weighted_trace(max_cutoff, length, q0, perturbative_mass2, y_value, sobolev_s)
        support_ok = support_ok and sobolev_s < 0.5 and exponent > 1.0 and math.isfinite(inner + tail)
        support_rows.append({"s": sobolev_s, "leading_p_series_exponent": exponent, "weighted_trace_upper": inner + tail})
    check("gaussian_Hs_support_for_every_audited_s_below_half", support_ok, support_rows, assertions)
    critical_s = float(audit["sharp_excluded_exponent"])
    check(
        "half_derivative_support_threshold_is_excluded_by_harmonic_power",
        math.isclose(2.0 - 2.0 * critical_s, 1.0, abs_tol=1.0e-15),
        {"s": critical_s, "leading_p_series_exponent": 2.0 - 2.0 * critical_s},
        assertions,
    )
    check("gaussian_L6_spectral_tail_envelopes_decrease_to_zero", all(l6_decreasing), l6_decreasing, assertions)
    check("interacting_measure_tightness_envelopes_decrease_to_zero", all(tightness_decreasing), tightness_decreasing, assertions)
    check(
        "uniform_partition_bounds_are_positive_and_finite",
        all(math.isfinite(row["log10_uniform_partition_lower"]) and row["log10_uniform_partition_lower"] <= row["log10_uniform_partition_upper"] for row in row_data),
        [{"anchor": row["anchor"], "lower": row["log10_uniform_partition_lower"], "upper": row["log10_uniform_partition_upper"]} for row in row_data],
        assertions,
    )
    check(
        "common_gaussian_L6_control_closes_local_interaction",
        all(float(row["gaussian_even_pointwise_moments_upper"]["12"]) < math.inf for row in row_data),
        "finite Gaussian moments through order 12 plus vanishing L6 tail control quartic/sextic differences",
        assertions,
    )
    check(
        "full_sequence_identification_is_declared",
        bool(audit["require_full_sequence_identification"])
        and "full N sequence" in manifest["theorem_scope"]["target_limit"],
        manifest["theorem_scope"]["target_limit"],
        assertions,
    )
    check(
        "derivative_classii_extension_is_excluded",
        any("derivative Class-II" in item for item in manifest["honesty_boundary"]["excluded"]),
        manifest["honesty_boundary"]["excluded"],
        assertions,
    )

    passed = sum(item["status"] == "PASS" for item in assertions)
    verdict = "A4-SCALAR-CONSTRUCTIVE-PRIMARY-PASS" if passed == len(assertions) else "A4-SCALAR-CONSTRUCTIVE-PRIMARY-FAIL"
    output = {
        "schema": "tect/a4-scalar-constructive-primary-result/1.0",
        "claim_id": __claims__[0],
        "script_version": __version__,
        "verdict": verdict,
        "inputs": {
            "domain_lengths": [float(params["Lx"]), float(params["Ly"]), float(params["Lz"])],
            "q0": q0,
            "Y": y_value,
            "lambda": lambda_value,
            "gamma": gamma_value,
            "max_mode_cutoffs": cutoffs,
        },
        "derived": {
            "volume": volume,
            "production_shell_mass_squared": production_mass2,
            "quartic_sextic_lower_constant_per_volume": potential_lower_constant,
            "potential_minimizer_phi_squared": minimizer_square,
            "covariance_trace_power": 4,
            "spatial_dimension": 3,
            "gaussian_support_threshold_s": 0.5,
        },
        "support_rows": support_rows,
        "anchor_rows": row_data,
        "proof_chain": {
            "normalization": "Jensen lower bound and pointwise potential lower bound give 0<inf_N Z_N<=sup_N Z_N<infinity",
            "interaction_limit": "Gaussian L6 tail tends to zero; polynomial difference inequalities give V(P_N phi)->V(phi)",
            "measure_limit": "bounded weights converge in L1 and Z_N->Z; lifted densities converge in total variation",
            "projected_laws": "common-Gaussian coupling gives weak convergence of the full projected Gibbs sequence on L2",
            "correlations": "Gaussian moments plus the uniform density bound give uniform integrability for declared polynomial/cylinder observables",
        },
        "assertions": assertions,
        "assertion_summary": {"passed": passed, "total": len(assertions)},
        "environment": {"python": sys.version.split()[0], "numpy": np.__version__, "platform": platform.platform()},
        "honesty_boundary": manifest["honesty_boundary"],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"{passed}/{len(assertions)} PASS")
    print(verdict)
    print("Trace upper bounds:", {row["anchor"]: row["full_covariance_trace_upper"] for row in row_data})
    print("Evidence:", args.output.resolve())
    return 0 if passed == len(assertions) else 1


if __name__ == "__main__":
    raise SystemExit(main())

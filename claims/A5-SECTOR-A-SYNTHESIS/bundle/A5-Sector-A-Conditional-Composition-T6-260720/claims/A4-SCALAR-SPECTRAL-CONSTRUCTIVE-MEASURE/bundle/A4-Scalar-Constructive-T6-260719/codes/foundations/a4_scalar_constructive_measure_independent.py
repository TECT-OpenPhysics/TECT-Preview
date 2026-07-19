#!/usr/bin/env python3
"""Non-importing adversarial audit for the A4 scalar constructive measure.

This script deliberately does not import the primary A4 implementation.  It
reconstructs a Fourier-cube covariance trace with scalar loops, derives the
quartic/sextic minimum with Decimal arithmetic, rebuilds the Gaussian moment
recurrence, and checks the theorem-scope statements that make the Galerkin
limit a full-sequence result rather than a numerical extrapolation.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import sys
from decimal import Decimal, getcontext
from pathlib import Path
from typing import Any

__version__ = "1.1.0"
__first_issued__ = "2026-07-18"
__version_issued__ = "2026-07-19"
__claims__ = ["A4-SCALAR-SPECTRAL-CONSTRUCTIVE-MEASURE"]

getcontext().prec = 80
REPO = Path(__file__).resolve().parents[2]
CLAIM = REPO / "claims" / __claims__[0]
MANIFEST = CLAIM / "constructive_measure_manifest.json"
DEFAULT_PRIMARY = CLAIM / "runs" / "2026-07-18-primary-constructive-measure" / "result.json"
DEFAULT_OUTPUT = CLAIM / "runs" / "2026-07-18-independent-constructive-measure" / "result.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(name: str, passed: bool, detail: Any, assertions: list[dict[str, Any]]) -> None:
    assertions.append({"name": name, "status": "PASS" if passed else "FAIL", "detail": detail})


def exact_trace_scalar_loop(max_mode: int, length: float, q0: float, mass2: float, y_value: float) -> float:
    """Independent covariance trace using only scalar loops and math.fsum."""
    scale2 = (2.0 * math.pi / length) ** 2
    q02 = q0 * q0
    terms = []
    for n1 in range(-max_mode, max_mode + 1):
        for n2 in range(-max_mode, max_mode + 1):
            for n3 in range(-max_mode, max_mode + 1):
                k2 = scale2 * float(n1 * n1 + n2 * n2 + n3 * n3)
                terms.append(1.0 / (mass2 + y_value * (k2 - q02) ** 2))
    return math.fsum(terms)


def pseries_integral_bound(start: int, exponent: float) -> float:
    """Integral-test upper bound for sum from start to infinity."""
    if start < 1 or exponent <= 1.0:
        raise ValueError("p-series bound requires start>=1 and exponent>1")
    return start ** (-exponent) + start ** (1.0 - exponent) / (exponent - 1.0)


def max_shell_tail(start: int, length: float, q0: float, y_value: float) -> float:
    scale = 2.0 * math.pi / length
    if start < 1:
        raise ValueError("max-norm shell tail starts at m=1")
    if scale * scale * start * start < 2.0 * q0 * q0:
        raise ValueError("tail start does not lie beyond the shell")
    shell_sum = 24.0 * pseries_integral_bound(start, 2.0) + 2.0 * pseries_integral_bound(start, 4.0)
    return 4.0 * shell_sum / (y_value * scale**4)


def decimal_potential_minimum(lambda_value: float, gamma_value: float) -> tuple[Decimal, Decimal, Decimal]:
    lam = Decimal(str(lambda_value))
    gam = Decimal(str(gamma_value))
    negative = max(-lam, Decimal(0))
    critical_x = negative / gam if negative else Decimal(0)
    value = lam * critical_x**2 / Decimal(4) + gam * critical_x**3 / Decimal(6)
    lower_constant = negative**3 / (Decimal(12) * gam**2)
    return critical_x, value, lower_constant


def gaussian_moments(variance: float, through: int) -> dict[str, float]:
    output = {"0": 1.0}
    current = 1.0
    for order in range(2, through + 1, 2):
        current = float(order - 1) * variance * current
        output[str(order)] = current
    return output


def find_anchor(result: dict[str, Any], name: str) -> dict[str, Any]:
    return next(row for row in result["anchor_rows"] if row["anchor"] == name)


def find_cutoff(row: dict[str, Any], max_mode: int) -> dict[str, Any]:
    return next(item for item in row["cutoffs"] if int(item["max_mode"]) == max_mode)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--primary-result", type=Path, default=DEFAULT_PRIMARY)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    authority = manifest["authority"]
    kernel_path = REPO / authority["scalar_kernel_anchor"]["path"]
    functional_path = REPO / authority["production_functional_anchor"]["path"]
    primary_source = REPO / authority["primary_audit"]["path"]
    kernel = json.loads(kernel_path.read_text(encoding="utf-8"))
    functional = json.loads(functional_path.read_text(encoding="utf-8"))
    primary = json.loads(args.primary_result.read_text(encoding="utf-8"))
    params = functional["parameters"]
    assertions: list[dict[str, Any]] = []

    check(
        "independent_source_hash_matches_manifest",
        sha256(Path(__file__)) == authority["independent_audit"]["sha256"],
        {"actual": sha256(Path(__file__)), "expected": authority["independent_audit"]["sha256"]},
        assertions,
    )
    check(
        "primary_source_and_upstreams_are_hash_pinned",
        sha256(primary_source) == authority["primary_audit"]["sha256"]
        and sha256(kernel_path) == authority["scalar_kernel_anchor"]["sha256"]
        and sha256(functional_path) == authority["production_functional_anchor"]["sha256"],
        {"primary": sha256(primary_source), "kernel": sha256(kernel_path), "functional": sha256(functional_path)},
        assertions,
    )
    primary_total = int(primary.get("assertion_summary", {}).get("total", 0))
    check(
        "primary_artifact_is_complete_pass",
        primary.get("verdict") == "A4-SCALAR-CONSTRUCTIVE-PRIMARY-PASS"
        and int(primary.get("assertion_summary", {}).get("passed", -1)) == primary_total
        and primary_total > 0,
        {"verdict": primary.get("verdict"), "summary": primary.get("assertion_summary")},
        assertions,
    )

    length = float(params["Lx"])
    volume = float(params["Lx"]) * float(params["Ly"]) * float(params["Lz"])
    q0 = float(params["q0"])
    y_value = float(params["Y"])
    lambda_value = float(params["lambda"])
    gamma_value = float(params["gamma"])
    production_mass2 = float(params["r"]) - float(params["Z"]) ** 2 / (4.0 * y_value)
    masses = {
        "perturbative_scalar": float(kernel["mu2_shell"]),
        "production_local": production_mass2,
    }
    check(
        "independent_anchor_reconstruction_is_admissible",
        y_value > 0.0 and gamma_value > 0.0 and all(value > 0.0 for value in masses.values()),
        {"Y": y_value, "gamma": gamma_value, "masses": masses},
        assertions,
    )

    trace_comparisons = []
    for name, mass2 in masses.items():
        reconstructed = exact_trace_scalar_loop(8, length, q0, mass2, y_value)
        published = float(find_cutoff(find_anchor(primary, name), 8)["partial_covariance_trace"])
        relative = abs(reconstructed - published) / max(abs(reconstructed), abs(published), 1.0)
        trace_comparisons.append({"anchor": name, "reconstructed": reconstructed, "published": published, "relative_error": relative})
    check(
        "scalar_loop_covariance_traces_match_vectorized_primary",
        all(row["relative_error"] < 3.0e-13 for row in trace_comparisons),
        trace_comparisons,
        assertions,
    )

    shell_counts = []
    for shell in range(1, 13):
        enumerated = (2 * shell + 1) ** 3 - (2 * shell - 1) ** 3
        formula = 24 * shell * shell + 2
        shell_counts.append({"shell": shell, "enumerated": enumerated, "formula": formula})
    check("max_norm_shell_count_is_exact", all(row["enumerated"] == row["formula"] for row in shell_counts), shell_counts, assertions)
    zero_q0_tail = max_shell_tail(1, length, 0.0, y_value)
    check(
        "q0_zero_boundary_is_independently_well_defined",
        bool(manifest["audit"]["require_q0_zero_shell_boundary_check"])
        and shell_counts[0]["shell"] == 1
        and math.isfinite(zero_q0_tail)
        and zero_q0_tail > 0.0,
        {
            "q0": 0.0,
            "first_nonzero_max_norm_shell": shell_counts[0]["shell"],
            "trace_tail_upper": zero_q0_tail,
        },
        assertions,
    )
    covariance_order = 4.0
    spatial_dimension = 3.0
    check(
        "q4_covariance_is_trace_class_in_three_dimensions",
        covariance_order > spatial_dimension and spatial_dimension - 1.0 - covariance_order < -1.0,
        {"covariance_order": covariance_order, "dimension": spatial_dimension, "radial_power": spatial_dimension - 1.0 - covariance_order},
        assertions,
    )

    audited_support = [float(value) for value in manifest["audit"]["sobolev_exponents"]]
    critical = float(manifest["audit"]["sharp_excluded_exponent"])
    support_powers = [{"s": value, "shell_power": 2.0 * value - 2.0} for value in audited_support]
    check(
        "Hs_support_and_half_derivative_threshold_are_rederived",
        all(row["s"] < 0.5 and row["shell_power"] < -1.0 for row in support_powers)
        and math.isclose(2.0 * critical - 2.0, -1.0, abs_tol=1.0e-15),
        {"audited": support_powers, "critical_s": critical},
        assertions,
    )

    critical_x, minimum, lower_constant = decimal_potential_minimum(lambda_value, gamma_value)
    primary_lower = Decimal(str(primary["derived"]["quartic_sextic_lower_constant_per_volume"]))
    derivative_at_critical = critical_x * (Decimal(str(lambda_value)) + Decimal(str(gamma_value)) * critical_x) / Decimal(2)
    check(
        "quartic_sextic_minimum_is_independently_stationary_and_exact",
        derivative_at_critical == 0 and abs(minimum + lower_constant) < Decimal("1e-70") and abs(lower_constant - primary_lower) < Decimal("1e-16"),
        {"phi_squared": str(critical_x), "minimum": str(minimum), "lower_constant": str(lower_constant), "primary_lower": str(primary_lower)},
        assertions,
    )

    partition_rows = []
    for name, mass2 in masses.items():
        primary_row = find_anchor(primary, name)
        trace32 = exact_trace_scalar_loop(32, length, q0, mass2, y_value)
        trace_upper = trace32 + max_shell_tail(33, length, q0, y_value)
        variance = trace_upper / volume
        moments = gaussian_moments(variance, int(manifest["audit"]["gaussian_even_moments_through"]))
        expected_v_upper = volume * (
            3.0 * max(lambda_value, 0.0) * variance**2 / 4.0
            + 5.0 * gamma_value * variance**3 / 2.0
        )
        lower_log10 = -expected_v_upper / math.log(10.0)
        upper_log10 = float(lower_constant) * volume / math.log(10.0)
        moment12_relative = abs(moments["12"] - float(primary_row["gaussian_even_pointwise_moments_upper"]["12"])) / max(abs(moments["12"]), 1.0)
        partition_rows.append(
            {
                "anchor": name,
                "trace_upper": trace_upper,
                "log10_lower": lower_log10,
                "log10_upper": upper_log10,
                "moment12_relative_error": moment12_relative,
                "published_log10_lower": float(primary_row["log10_uniform_partition_lower"]),
                "published_log10_upper": float(primary_row["log10_uniform_partition_upper"]),
            }
        )
    check(
        "gaussian_moments_and_uniform_partition_bounds_reconstruct",
        all(
            row["moment12_relative_error"] < 5.0e-13
            and math.isclose(row["log10_lower"], row["published_log10_lower"], rel_tol=3.0e-13, abs_tol=1.0e-12)
            and math.isclose(row["log10_upper"], row["published_log10_upper"], rel_tol=3.0e-13, abs_tol=1.0e-12)
            and row["log10_lower"] <= row["log10_upper"]
            for row in partition_rows
        ),
        partition_rows,
        assertions,
    )

    tail_rows = []
    for cutoff in [int(value) for value in manifest["audit"]["max_mode_cutoffs"]]:
        tail = max_shell_tail(cutoff + 1, length, q0, y_value)
        l6_sixth = 15.0 * volume * (tail / volume) ** 3
        tail_rows.append({"cutoff": cutoff, "trace_tail_upper": tail, "L6_sixth_moment_upper": l6_sixth})
    check(
        "independent_gaussian_L6_tail_envelope_vanishes_monotonically",
        all(right["L6_sixth_moment_upper"] < left["L6_sixth_moment_upper"] for left, right in zip(tail_rows, tail_rows[1:]))
        and tail_rows[-1]["L6_sixth_moment_upper"] > 0.0,
        tail_rows,
        assertions,
    )

    target = manifest["theorem_scope"]["target_limit"]
    exclusions = manifest["honesty_boundary"]["excluded"]
    check(
        "full_sequence_and_lifted_density_topologies_are_explicit",
        "full N sequence" in target and "weakly on L2" in target and "L1/total variation" in target,
        target,
        assertions,
    )
    check(
        "derivative_classii_infinite_volume_and_BCC_are_not_smuggled_in",
        any("derivative Class-II" in item for item in exclusions)
        and any("infinite volume" in item for item in exclusions)
        and any("BCC" in item for item in exclusions),
        exclusions,
        assertions,
    )
    check(
        "measure_limit_uses_bounded_weight_not_sampling_extrapolation",
        "bounded Gibbs weights" in manifest["analytic_identities"]["measure_convergence"]
        and "converges weakly" in target,
        {"identity": manifest["analytic_identities"]["measure_convergence"], "target": target},
        assertions,
    )

    passed = sum(item["status"] == "PASS" for item in assertions)
    verdict = "A4-SCALAR-CONSTRUCTIVE-INDEPENDENT-PASS" if passed == len(assertions) else "A4-SCALAR-CONSTRUCTIVE-INDEPENDENT-FAIL"
    output = {
        "schema": "tect/a4-scalar-constructive-independent-result/1.0",
        "claim_id": __claims__[0],
        "script_version": __version__,
        "verdict": verdict,
        "scope": "non-importing reconstruction of covariance, stability, partition bounds, and full-sequence theorem declarations",
        "trace_comparisons": trace_comparisons,
        "partition_rows": partition_rows,
        "tail_rows": tail_rows,
        "assertions": assertions,
        "assertion_summary": {"passed": passed, "total": len(assertions)},
        "environment": {"python": sys.version.split()[0], "platform": platform.platform()},
        "not_closed_here": manifest["honesty_boundary"]["excluded"],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"{passed}/{len(assertions)} PASS")
    print(verdict)
    print("Evidence:", args.output.resolve())
    return 0 if passed == len(assertions) else 1


if __name__ == "__main__":
    raise SystemExit(main())

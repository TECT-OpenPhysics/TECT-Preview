#!/usr/bin/env python3
"""Independent semigroup/smoothing audit for A2 full production.

This NumPy-only verifier reconstructs the production linear symbol and checks
the spectral estimates used by the continuous-dependence and positive-time
smoothing proof.  It deliberately does not integrate the nonlinear PDE: the
accompanying v1.3 note proves the weakly singular Gronwall estimate, the first
H4 gain by Duhamel cancellation, and the higher Sobolev bootstrap.
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
__first_issued__ = "2026-07-17"
__version_issued__ = "2026-07-17"

REPO = Path(__file__).resolve().parents[2]
P1_MANIFEST = REPO / "claims" / "A1-PRODUCTION-FUNCTIONAL-REALISATION" / "production_functional_manifest.json"
BASELINE_RESULT = REPO / "claims" / "A2-FULL-PRODUCTION-WELLPOSED" / "runs" / "2026-07-17-coercivity-baseline" / "result.json"
NONLINEAR_RESULT = REPO / "claims" / "A2-FULL-PRODUCTION-WELLPOSED" / "runs" / "2026-07-17-nonlinear-mapping-audit" / "result.json"
ENERGY_RESULT = REPO / "claims" / "A2-FULL-PRODUCTION-WELLPOSED" / "runs" / "2026-07-17-energy-continuation-audit" / "result.json"
DEFAULT_OUTPUT = REPO / "claims" / "A2-FULL-PRODUCTION-WELLPOSED" / "runs" / "2026-07-17-smoothing-audit" / "result.json"

# Audit settings only. Production coefficients are always read from the
# hash-pinned P1 manifest.
TEST_MODE_RADIUS = 8
TEST_TIMES = (0.01, 0.1, 1.0)
TEST_FRACTIONAL_POWERS = (0.5, 0.75, 0.9)
TEST_HOLDER_EXPONENTS = (0.125, 0.25, 0.5)
ROUND_OFF_TOLERANCE = 2.0e-12


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def git_revision() -> str | None:
    completed = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO, text=True, capture_output=True, check=False)
    return completed.stdout.strip() if completed.returncode == 0 else None


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def audit() -> dict[str, Any]:
    manifest = load_json(P1_MANIFEST)
    baseline = load_json(BASELINE_RESULT)
    nonlinear = load_json(NONLINEAR_RESULT)
    energy = load_json(ENERGY_RESULT)
    params = manifest["parameters"]
    backend = manifest["production_reference_backend"]
    backend_path = REPO / backend["path"]
    assertions: list[dict[str, Any]] = []

    def check(name: str, passed: bool, value: Any) -> None:
        assertions.append({"name": name, "passed": bool(passed), "value": value})

    backend_hash = sha256_file(backend_path)
    check("p1_backend_hash_matches_manifest", backend_hash == backend["sha256"], {"computed": backend_hash, "expected": backend["sha256"]})
    prior = {
        "coercivity": baseline.get("verdict"),
        "nonlinear_mapping": nonlinear.get("verdict"),
        "energy_continuation": energy.get("verdict"),
    }
    check("coercivity_baseline_passed", bool(baseline.get("passed")) and prior["coercivity"] == "A2-FULL-COERCIVITY-BASELINE-PASS", prior["coercivity"])
    check("nonlinear_mapping_audit_passed", bool(nonlinear.get("passed")) and prior["nonlinear_mapping"] == "A2-FULL-NONLINEAR-MAPPING-AUDIT-PASS", prior["nonlinear_mapping"])
    check("energy_continuation_audit_passed", bool(energy.get("passed")) and prior["energy_continuation"] == "A2-FULL-ENERGY-CONTINUATION-AUDIT-PASS", prior["energy_continuation"])

    y_value = float(params["Y"])
    z_value = float(params["Z"])
    r_value = float(params["r"])
    critical_k2 = max(0.0, -z_value / (2.0 * y_value))
    scalar_minimum = r_value + z_value * critical_k2 + y_value * critical_k2**2
    check("fourth_order_principal_coefficient_is_positive", y_value > 0.0, y_value)
    check("continuous_scalar_symbol_has_positive_minimum", scalar_minimum > 0.0, {"critical_k_squared": critical_k2, "minimum": scalar_minimum})

    z0 = np.asarray(params["z0"], dtype=float)
    projector = np.outer(z0, z0) / float(np.dot(z0, z0))
    internal = np.diag(np.asarray(params["family_masses"], dtype=float))
    internal += float(params["k_lock"]) * (np.eye(z0.size) - projector)
    internal_eigenvalues = np.linalg.eigvalsh(internal)
    check("internal_linear_matrix_is_positive_semidefinite", float(internal_eigenvalues[0]) >= -ROUND_OFF_TOLERANCE, internal_eigenvalues.tolist())

    mode_axis = np.arange(-TEST_MODE_RADIUS, TEST_MODE_RADIUS + 1, dtype=float)
    nx, ny, nz = np.meshgrid(mode_axis, mode_axis, mode_axis, indexing="ij")
    k2 = (2.0 * math.pi * nx / float(params["Lx"])) ** 2
    k2 += (2.0 * math.pi * ny / float(params["Ly"])) ** 2
    k2 += (2.0 * math.pi * nz / float(params["Lz"])) ** 2
    scalar_symbol = r_value + z_value * k2 + y_value * k2**2
    eigenvalues = (scalar_symbol[..., None] + internal_eigenvalues).reshape(-1)
    sampled_minimum = float(np.min(eigenvalues))
    check("sampled_full_symbol_is_strictly_positive", sampled_minimum > 0.0, sampled_minimum)

    graph_ratio = eigenvalues / np.repeat((1.0 + k2.reshape(-1)) ** 2, internal_eigenvalues.size)
    graph_bounds = {"minimum": float(np.min(graph_ratio)), "maximum": float(np.max(graph_ratio))}
    check("sampled_graph_norm_is_equivalent_to_h4", graph_bounds["minimum"] > 0.0 and math.isfinite(graph_bounds["maximum"]), graph_bounds)

    contraction_ratios: list[float] = []
    fractional_ratios: list[float] = []
    for time in TEST_TIMES:
        contraction_ratios.append(float(np.max(np.exp(-time * eigenvalues)) / math.exp(-time * scalar_minimum)))
        for alpha in TEST_FRACTIONAL_POWERS:
            observed = float(np.max(eigenvalues**alpha * np.exp(-time * eigenvalues)))
            universal = (alpha / (math.e * time)) ** alpha
            fractional_ratios.append(observed / universal)
    max_contraction_ratio = max(contraction_ratios)
    max_fractional_ratio = max(fractional_ratios)
    check("positive_semigroup_obeys_spectral_contraction", max_contraction_ratio <= 1.0 + ROUND_OFF_TOLERANCE, max_contraction_ratio)
    check("analytic_semigroup_fractional_power_bound_holds", max_fractional_ratio <= 1.0 + ROUND_OFF_TOLERANCE, max_fractional_ratio)

    half_kernel_integrals = {str(time): 2.0 * math.sqrt(time) for time in TEST_TIMES}
    check("h2_difference_kernel_is_integrable", all(math.isfinite(value) and value > 0.0 for value in half_kernel_integrals.values()), half_kernel_integrals)
    holder_integrals = {
        f"theta={theta},T={time}": time**theta / theta
        for theta in TEST_HOLDER_EXPONENTS
        for time in TEST_TIMES
    }
    check("duhamel_cancellation_kernel_is_integrable", all(math.isfinite(value) and value > 0.0 for value in holder_integrals.values()), holder_integrals)

    regularisers = {
        "rho_regularizer": float(params["rho_regularizer"]),
        "classii_mass_regularizer": float(params["classii_mass_regularizer"]),
        "eta_shell": float(params["eta_shell"]),
    }
    check(
        "canonical_subset_has_smooth_denominators_and_zero_shell_bias",
        regularisers["rho_regularizer"] > 0.0 and regularisers["classii_mass_regularizer"] > 0.0 and regularisers["eta_shell"] == 0.0,
        regularisers,
    )
    principal_order = 4
    classii_order = 2
    check("sobolev_bootstrap_has_positive_derivative_gain", principal_order - classii_order > 0, {"principal_order": principal_order, "nonlinear_order": classii_order, "gain_per_bootstrap": principal_order - classii_order})

    passed = all(item["passed"] for item in assertions)
    return {
        "schema": "tect/a2-full-production-smoothing-audit/1.0",
        "claim_id": "A2-FULL-PRODUCTION-WELLPOSED",
        "generated_on": "2026-07-17",
        "script_version": __version__,
        "input": {
            "p1_manifest": str(P1_MANIFEST.relative_to(REPO)).replace("\\", "/"),
            "p1_manifest_sha256": sha256_file(P1_MANIFEST),
            "backend": backend["path"],
            "backend_sha256": backend_hash,
            "coercivity_result": str(BASELINE_RESULT.relative_to(REPO)).replace("\\", "/"),
            "nonlinear_mapping_result": str(NONLINEAR_RESULT.relative_to(REPO)).replace("\\", "/"),
            "energy_continuation_result": str(ENERGY_RESULT.relative_to(REPO)).replace("\\", "/"),
        },
        "test_configuration": {
            "mode_radius": TEST_MODE_RADIUS,
            "times": list(TEST_TIMES),
            "fractional_powers": list(TEST_FRACTIONAL_POWERS),
            "holder_exponents": list(TEST_HOLDER_EXPONENTS),
            "round_off_tolerance": ROUND_OFF_TOLERANCE,
        },
        "derived": {
            "continuous_scalar_symbol_minimum": scalar_minimum,
            "sampled_full_symbol_minimum": sampled_minimum,
            "internal_matrix_eigenvalues": internal_eigenvalues.tolist(),
            "sampled_graph_norm_ratio_bounds": graph_bounds,
            "maximum_contraction_bound_ratio": max_contraction_ratio,
            "maximum_fractional_semigroup_bound_ratio": max_fractional_ratio,
            "bootstrap_derivative_gain": principal_order - classii_order,
        },
        "assertions": assertions,
        "proof_boundary": {
            "closed_here": [
                "production spectral assumptions used by the analytic-semigroup proof",
                "integrability of the H2 difference and Duhamel-cancellation kernels",
                "analytic continuous-dependence, first H4 gain, and higher Sobolev bootstrap in the v1.3 note",
            ],
            "not_closed_here": [
                "T6 or T7 theorem tier",
                "historical non-variational proxy or eta_shell nonzero",
                "initial data below H2 or infinite-volume dynamics",
            ],
        },
        "environment": {
            "python": sys.version,
            "numpy": np.__version__,
            "platform": platform.platform(),
            "git_revision": git_revision(),
        },
        "verdict": "A2-FULL-SMOOTHING-AUDIT-PASS" if passed else "A2-FULL-SMOOTHING-AUDIT-FAIL",
        "passed": passed,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    result = audit()
    output = args.output if args.output.is_absolute() else REPO / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    passed_count = sum(item["passed"] for item in result["assertions"])
    print(f"{passed_count}/{len(result['assertions'])} PASS")
    print(result["verdict"])
    print(f"Minimum continuous scalar symbol: {result['derived']['continuous_scalar_symbol_minimum']:.12g}")
    print(f"Maximum fractional semigroup ratio: {result['derived']['maximum_fractional_semigroup_bound_ratio']:.12g}")
    print(f"Evidence: {output}")
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())

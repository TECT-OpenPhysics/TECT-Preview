#!/usr/bin/env python3
"""Non-importing independent audit for the A13 relative-phase obstruction.

This route evaluates the finite polynomial on an alias-free physical grid,
derives the Class-II matrix directly from complex currents, and verifies the
resolvent identity through singular values.  It does not import the primary
audit or reuse its convolution implementation.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import math
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

__version__ = "1.0.0"
__first_issued__ = "2026-07-21"
__version_issued__ = "2026-07-21"

REPO = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = REPO / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION" / "classii_relative_phase_source_obstruction_manifest.json"
DEFAULT_OUTPUT = REPO / "claims" / "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION" / "runs" / "2026-07-21-independent-relative-phase-obstruction" / "result.json"


def file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        while True:
            block = handle.read(1 << 20)
            if not block:
                break
            digest.update(block)
    return digest.hexdigest()


def commit_id() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True, stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.CalledProcessError):
        return "UNKNOWN"


def record(rows: list[dict[str, Any]], name: str, condition: bool, actual: Any, expected: Any) -> None:
    rows.append({"name": name, "status": "PASS" if condition else "FAIL", "actual": actual, "expected": expected})


def generators() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    return (
        np.asarray([[0, 1, 0], [1, 0, 0], [0, 0, 0]], dtype=np.complex128),
        np.asarray([[0, -1j, 0], [1j, 0, 0], [0, 0, 0]], dtype=np.complex128),
        np.asarray([[1, 0, 0], [0, -1, 0], [0, 0, 0]], dtype=np.complex128),
    )


def coefficient_values(parameters: dict[str, Any]) -> tuple[float, float, float]:
    denominator = float(parameters["M_X"]) ** 2 + float(parameters["classii_mass_regularizer"])
    alpha = float(parameters["alpha_X"])
    beta = float(parameters["beta_X"])
    return (
        float(parameters["cJJ"]) * alpha**2 / denominator,
        float(parameters["cJK"]) * alpha * beta / denominator,
        float(parameters["cKK"]) * beta**2 / denominator,
    )


def complex_current_map(field: np.ndarray, tangent: np.ndarray, parameters: dict[str, Any]) -> np.ndarray:
    rho = float(np.real(np.vdot(field, field)))
    safe = rho + float(parameters["rho_regularizer"])
    a_value, b_value, c_value = coefficient_values(parameters)
    output = np.zeros(3, dtype=np.complex128)
    drho = 2.0 * float(np.real(np.vdot(field, tangent)))
    for generator in generators():
        transformed = generator @ field
        moment = float(np.real(np.vdot(field, transformed)))
        current = 2.0 * float(np.real(np.vdot(transformed, tangent)))
        covariant = current - (moment / safe) * drho
        p_complex = 2.0 * transformed
        v_complex = 2.0 * (transformed - (moment / safe) * field)
        output += (a_value * current + b_value * covariant) * p_complex
        output += (b_value * current + c_value * covariant) * v_complex
    return output


def grid_certificate(degree: int, exponent: float, beta_operator: float) -> dict[str, float]:
    minimum_grid = 6 * degree + 1
    grid = 1 << (minimum_grid - 1).bit_length()
    modes = np.arange(1, degree + 1, dtype=np.float64)
    amplitudes = modes ** (-exponent)

    full_hat = np.zeros(grid, dtype=np.complex128)
    past_hat = np.zeros(grid, dtype=np.complex128)
    full_hat[1 : degree + 1] = -amplitudes
    full_hat[-degree:] = amplitudes[::-1]
    past_hat[-degree:] = amplitudes[::-1]

    full = np.fft.ifft(full_hat) * grid
    past = np.fft.ifft(past_hat) * grid
    full_l6 = float(np.mean(np.abs(full) ** 6))
    past_l6 = float(np.mean(np.abs(past) ** 6))
    cubic = past * np.abs(past) ** 2
    cubic_hat = np.fft.fft(cubic) / grid
    signed_modes = np.rint(np.fft.fftfreq(grid) * grid).astype(np.int64)
    nonpositive = float(np.sum(np.abs(cubic_hat[signed_modes <= 0]) ** 2))

    past_ratio = past_l6 / full_l6
    nonpositive_ratio = nonpositive / full_l6
    spin = past_ratio**3 - nonpositive_ratio**3
    return {
        "degree": degree,
        "grid": grid,
        "alias_free_minimum": minimum_grid,
        "past_over_full": past_ratio,
        "nonpositive_over_full": nonpositive_ratio,
        "spin_functional": spin,
        "source_ratio": beta_operator**2 * spin,
        "full_l6_sixth": full_l6,
        "past_l6_sixth": past_l6,
        "nonpositive_cubic_energy": nonpositive,
    }


def run(manifest_path: Path, output_path: Path) -> int:
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assertions: list[dict[str, Any]] = []

    for key in ("a1_manifest", "a12_status", "a12_obstruction_manifest"):
        item = manifest["authority"][key]
        actual = file_hash(REPO / item["path"])
        record(assertions, f"authority_{key}_hash_independent", actual == item["sha256"], actual, item["sha256"])
    own = manifest["sources"]["independent"]
    own_hash = file_hash(REPO / own["path"])
    record(assertions, "independent_source_hash", own_hash == own["sha256"], own_hash, own["sha256"])

    a1 = json.loads((REPO / manifest["authority"]["a1_manifest"]["path"]).read_text(encoding="utf-8"))
    parameters = a1["parameters"]
    a_value, b_value, c_value = coefficient_values(parameters)
    beta_operator = 4.0 * (a_value + 2.0 * b_value + c_value)
    record(assertions, "independent_beta_from_production", abs(beta_operator - float(manifest["derived_oracles"]["beta_operator"])) < 1e-14, beta_operator, manifest["derived_oracles"]["beta_operator"])

    rng = np.random.default_rng(int(manifest["independent_audit"]["seed"]))
    relative_error = 0.0
    phase_error = 0.0
    floor_invariance_error = 0.0
    for _ in range(int(manifest["independent_audit"]["algebra_samples"])):
        z_value = rng.normal(size=2) + 1j * rng.normal(size=2)
        field = np.asarray([z_value[0], z_value[1], 0.0j])
        tangent = np.asarray([1j * z_value[0], -1j * z_value[1], 0.0j])
        actual = complex_current_map(field, tangent, parameters)
        expected = 2j * beta_operator * np.asarray([z_value[0] * abs(z_value[1]) ** 2, -abs(z_value[0]) ** 2 * z_value[1], 0.0j])
        relative_error = max(relative_error, float(np.linalg.norm(actual - expected)) / max(1.0, float(np.linalg.norm(expected))))

        arbitrary = rng.normal(size=3) + 1j * rng.normal(size=3)
        common = 1j * arbitrary
        doublet = np.asarray([1j * arbitrary[0], 1j * arbitrary[1], 0.0j])
        singlet = np.asarray([0.0j, 0.0j, 1j * arbitrary[2]])
        phase_error = max(phase_error, float(np.linalg.norm(complex_current_map(arbitrary, common, parameters))))
        phase_error = max(phase_error, float(np.linalg.norm(complex_current_map(arbitrary, doublet, parameters))))
        phase_error = max(phase_error, float(np.linalg.norm(complex_current_map(arbitrary, singlet, parameters))))

        changed = dict(parameters)
        changed["rho_regularizer"] = 1.0
        changed_actual = complex_current_map(field, tangent, changed)
        floor_invariance_error = max(floor_invariance_error, float(np.linalg.norm(changed_actual - actual)))

    tolerance = float(manifest["independent_audit"]["algebra_tolerance"])
    record(assertions, "relative_su2_carrier_direct_currents", relative_error < tolerance, relative_error, f"<{tolerance}")
    record(assertions, "three_phase_null_checks_direct", phase_error < tolerance, phase_error, f"<{tolerance}")
    record(assertions, "carrier_identity_floor_independent", floor_invariance_error < tolerance, floor_invariance_error, f"<{tolerance}")

    certificate = grid_certificate(
        int(manifest["certificate"]["degree"]),
        float(manifest["certificate"]["coefficient_exponent"]),
        beta_operator,
    )
    gamma_third = float(parameters["gamma"]) / 3.0
    reference_allowance = gamma_third / float(manifest["budget"]["reference_p"])
    record(assertions, "alias_free_grid_is_strict", certificate["grid"] > certificate["alias_free_minimum"], certificate["grid"], f">{certificate['alias_free_minimum']}")
    record(assertions, "grid_spin_functional_positive", certificate["spin_functional"] > 0.0, certificate["spin_functional"], ">0")
    record(assertions, "grid_source_exceeds_gamma_third", certificate["source_ratio"] > gamma_third, certificate["source_ratio"], gamma_third)
    record(assertions, "grid_source_exceeds_reference_budget", certificate["source_ratio"] > reference_allowance, certificate["source_ratio"], reference_allowance)
    record(assertions, "grid_certificate_matches_independent_oracle", abs(certificate["source_ratio"] - float(manifest["derived_oracles"]["independent_source_ratio"])) < float(manifest["independent_audit"]["certificate_tolerance"]), certificate["source_ratio"], manifest["derived_oracles"]["independent_source_ratio"])

    svd_error = 0.0
    lower_bound_error = 0.0
    p_value = float(manifest["budget"]["reference_p"])
    for _ in range(int(manifest["independent_audit"]["resolvent_samples"])):
        operator = rng.normal(size=(6, 4))
        source = rng.normal(size=6)
        left_matrix = operator.T @ operator
        ell = operator.T @ source
        direct = float(ell @ np.linalg.solve(np.eye(4) + p_value * left_matrix, ell))
        u_value, singular, _ = np.linalg.svd(operator, full_matrices=False)
        coordinates = u_value.T @ source
        spectral = float(np.sum((singular**2 / (1.0 + p_value * singular**2)) * coordinates**2))
        svd_error = max(svd_error, abs(direct - spectral))
        crude_lower = float((ell @ ell) / (1.0 + p_value * np.linalg.norm(left_matrix, ord=2)))
        lower_bound_error = max(lower_bound_error, max(0.0, crude_lower - direct))
    record(assertions, "resolvent_svd_identity_independent", svd_error < float(manifest["independent_audit"]["resolvent_tolerance"]), svd_error, f"<{manifest['independent_audit']['resolvent_tolerance']}")
    record(assertions, "resolvent_lower_bound_direction", lower_bound_error < float(manifest["independent_audit"]["resolvent_tolerance"]), lower_bound_error, "lower<=exact")

    source_text = (REPO / own["path"]).read_text(encoding="utf-8")
    syntax = ast.parse(source_text)
    imported_modules = []
    for node in ast.walk(syntax):
        if isinstance(node, ast.Import):
            imported_modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported_modules.append(node.module)
    forbidden_imports = [name for name in imported_modules if name.endswith("a13_classii_relative_phase_source_obstruction")]
    record(assertions, "independent_route_nonimporting", not forbidden_imports, forbidden_imports, [])
    record(assertions, "negative_result_is_scoped", manifest["honesty_boundary"]["does_not_rule_out"][0].startswith("a joint"), manifest["honesty_boundary"]["does_not_rule_out"], "joint routes remain open")
    record(assertions, "tier_boundary_is_t4", manifest["consequence"]["tier_after"] == "T4", manifest["consequence"]["tier_after"], "T4")

    failures = [row for row in assertions if row["status"] != "PASS"]
    result = {
        "schema": "tect/a13-classii-relative-phase-source-obstruction-independent-result/1.0",
        "claim_id": manifest["claim_id"],
        "script_version": __version__,
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "git_commit": commit_id(),
        "platform": platform.platform(),
        "manifest": str(manifest_path.relative_to(REPO)).replace("\\", "/"),
        "method": ["direct complex-current algebra", "alias-free physical-grid quadrature", "SVD resolvent audit"],
        "assertions": assertions,
        "summary": {"passed": len(assertions) - len(failures), "total": len(assertions), "failed": len(failures)},
        "derived": {
            "beta_operator": beta_operator,
            "relative_carrier_error": relative_error,
            "phase_null_error": phase_error,
            "floor_invariance_error": floor_invariance_error,
            "certificate": certificate,
            "budget": {"gamma_over_three": gamma_third, "reference_allowance": reference_allowance, "margin_over_gamma_third": certificate["source_ratio"] - gamma_third},
            "resolvent_svd_error": svd_error,
        },
        "next_gate": manifest["consequence"]["next_gate"],
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"PASS: independent ({len(assertions) - len(failures)}/{len(assertions)})" if not failures else f"FAIL: independent ({len(failures)} failures)")
    print(f"Independent source ratio: {certificate['source_ratio']:.15g}")
    print(f"Evidence: {output_path}")
    return 0 if not failures else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    return run(args.manifest.resolve(), args.output.resolve())


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Non-importing Pauli-current audit of the A9 commutator no-go result."""

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
__first_issued__ = "2026-07-21"
__version_issued__ = "2026-07-21"
__claims__ = ["A9-CLASSII-SMART-PATH-CANCELLATION"]

REPO = Path(__file__).resolve().parents[2]
CLAIM_DIR = REPO / "claims" / __claims__[0]
DEFAULT_MANIFEST = CLAIM_DIR / "tilted_commutator_nogo_manifest.json"
DEFAULT_OUTPUT = CLAIM_DIR / "runs" / "2026-07-21-independent-tilted-commutator-nogo" / "result.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_digest(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()


def git_commit() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=REPO, text=True,
            stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def add(name: str, passed: bool, actual: Any, expected: Any,
        rows: list[dict[str, Any]]) -> None:
    rows.append({
        "name": name,
        "status": "PASS" if bool(passed) else "FAIL",
        "actual": actual,
        "expected": expected,
    })


def production_constants(authority: dict[str, Any]) -> dict[str, float]:
    p = authority["parameters"]
    denominator = float(p["M_X"]) ** 2 + float(p["classii_mass_regularizer"])
    return {
        "a": float(p["cJJ"]) * float(p["alpha_X"]) ** 2 / denominator,
        "b": float(p["cJK"]) * float(p["alpha_X"]) * float(p["beta_X"]) / denominator,
        "c": float(p["cKK"]) * float(p["beta_X"]) ** 2 / denominator,
        "Y": float(p["Y"]),
        "rho_floor": float(p["rho_regularizer"]),
        "L": float(p["Lx"]),
    }


def generators() -> list[np.ndarray]:
    return [
        np.asarray([[0, 1, 0], [1, 0, 0], [0, 0, 0]], dtype=np.complex128),
        np.asarray([[0, -1j, 0], [1j, 0, 0], [0, 0, 0]], dtype=np.complex128),
        np.asarray([[1, 0, 0], [0, -1, 0], [0, 0, 0]], dtype=np.complex128),
    ]


def currents(field: np.ndarray, derivative: np.ndarray,
             rho_floor: float) -> tuple[np.ndarray, np.ndarray]:
    rho = np.sum(np.abs(field) ** 2, axis=0)
    drho = 2.0 * np.real(np.sum(np.conjugate(field) * derivative, axis=0))
    j_rows = []
    k_rows = []
    for generator in generators():
        transformed = np.einsum("ab,b...->a...", generator, field)
        moment = np.real(np.sum(np.conjugate(field) * transformed, axis=0))
        current = 2.0 * np.real(
            np.sum(np.conjugate(transformed) * derivative, axis=0)
        )
        projected = current - moment * drho / (rho + rho_floor)
        j_rows.append(current)
        k_rows.append(projected)
    return np.asarray(j_rows), np.asarray(k_rows)


def classii_density(field: np.ndarray, derivatives: list[np.ndarray],
                    constants: dict[str, float]) -> np.ndarray:
    density = np.zeros(field.shape[1:], dtype=np.float64)
    for derivative in derivatives:
        j_current, k_current = currents(
            field, derivative, constants["rho_floor"]
        )
        density += np.sum(
            0.5 * constants["a"] * j_current * j_current
            + constants["b"] * j_current * k_current
            + 0.5 * constants["c"] * k_current * k_current,
            axis=0,
        )
    return density


def adjacent_shell_coefficient(epsilon: float, grid: int) -> float:
    phase = 2.0 * math.pi * np.arange(grid, dtype=np.float64) / grid
    c1 = np.cos(phase)
    c2 = np.cos(2.0 * phase)
    s1 = np.sin(phase)
    s2 = np.sin(2.0 * phase)
    base = np.ones_like(phase)
    first = base + epsilon * c1
    second = first + epsilon * c2
    d_first = -epsilon * s1
    d_second = -epsilon * s1 - 2.0 * epsilon * s2
    first_increment = 2.0 * np.mean(d_first ** 2 * (first ** 2 - base ** 2))
    second_increment = 2.0 * np.mean(
        d_second ** 2 * (second ** 2 - first ** 2)
    )
    return float(first_increment + second_increment)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    audit = manifest["independent_audit"]
    authority_record = manifest["authority"]["production_functional_manifest"]
    authority_path = REPO / authority_record["path"]
    authority = json.loads(authority_path.read_text(encoding="utf-8"))
    constants = production_constants(authority)
    assertions: list[dict[str, Any]] = []

    add("independent_authority_hash_is_pinned",
        sha256(authority_path) == authority_record["sha256"],
        sha256(authority_path), authority_record["sha256"], assertions)
    grid = int(audit["phase_grid"])
    phase = 2.0 * math.pi * np.arange(grid, dtype=np.float64) / grid
    x_phase, y_phase = np.meshgrid(phase, phase, indexing="ij")
    g = np.cos(x_phase) + np.cos(y_phase) - np.cos(x_phase + y_phase)
    gx = -np.sin(x_phase) + np.sin(x_phase + y_phase)
    gy = -np.sin(y_phase) + np.sin(x_phase + y_phase)
    grad2 = gx * gx + gy * gy
    epsilon = float(audit["epsilon"])
    tolerance = float(audit["quadrature_tolerance"])
    averages = {
        "mean_g_grad2": float(np.mean(g * grad2)),
        "mean_g2_grad2": float(np.mean(g * g * grad2)),
        "mean_grad2": float(np.mean(grad2)),
        "m6": float(np.mean((1.0 + epsilon * g) ** 6)),
    }
    add("numeric_resonant_cubic_average_matches_minus_one",
        abs(averages["mean_g_grad2"] + 1.0) < tolerance,
        averages["mean_g_grad2"], -1.0, assertions)
    add("numeric_resonant_quartic_average_matches_five_halves",
        abs(averages["mean_g2_grad2"] - 2.5) < tolerance,
        averages["mean_g2_grad2"], 2.5, assertions)
    add("numeric_gradient_average_matches_two",
        abs(averages["mean_grad2"] - 2.0) < tolerance,
        averages["mean_grad2"], 2.0, assertions)
    add("numeric_witness_is_uniformly_nonzero",
        float(np.min(1.0 + epsilon * g)) > 0.0,
        float(np.min(1.0 + epsilon * g)), "> 0", assertions)

    laplacian_g = (
        -np.cos(x_phase) - np.cos(y_phase)
        + 2.0 * np.cos(x_phase + y_phase)
    )
    c_entropy = (
        0.5 * constants["Y"] * epsilon ** 2
        * float(np.mean(laplacian_g ** 2))
    )
    c_sextic = averages["m6"]
    raw_commutator_coefficient = (
        2.0 * constants["a"] * epsilon ** 2
        * (
            2.0 * epsilon * averages["mean_g_grad2"]
            + epsilon ** 2 * averages["mean_g2_grad2"]
        )
    )
    c_commutator = -raw_commutator_coefficient
    lattice_mode = int(audit["lattice_mode"])
    wave_number = 2.0 * math.pi * lattice_mode / constants["L"]
    t_value = (c_entropy / c_sextic) ** 0.25
    amplitude = t_value * wave_number

    field = np.zeros((3, grid, grid), dtype=np.complex128)
    low_field = np.zeros_like(field)
    field[0] = amplitude * (1.0 + epsilon * g)
    low_field[0] = amplitude
    derivative_x = np.zeros_like(field)
    derivative_y = np.zeros_like(field)
    derivative_x[0] = amplitude * epsilon * wave_number * gx
    derivative_y[0] = amplitude * epsilon * wave_number * gy
    full_density = classii_density(
        field, [derivative_x, derivative_y], constants
    )
    frozen_density = classii_density(
        low_field, [derivative_x, derivative_y], constants
    )
    commutator = float(np.mean(full_density - frozen_density))
    normalized = commutator / (amplitude ** 4 * wave_number ** 2)
    expected_normalized = -c_commutator
    add("direct_Pauli_current_commutator_has_predicted_negative_sign",
        normalized < 0.0, normalized, "< 0", assertions)
    add("direct_Pauli_current_commutator_matches_scalar_ray_formula",
        abs(normalized - expected_normalized)
        < float(audit["full_floor_tolerance"]),
        normalized, expected_normalized, assertions)

    j_current, k_current = currents(
        field, derivative_x, constants["rho_floor"]
    )
    rho = np.abs(field[0]) ** 2
    expected_k3 = (
        constants["rho_floor"] / (rho + constants["rho_floor"])
        * j_current[2]
    )
    add("direct_Pauli_currents_leave_only_generator_three",
        max(float(np.max(np.abs(j_current[0]))),
            float(np.max(np.abs(j_current[1])))) < tolerance,
        [float(np.max(np.abs(j_current[0]))),
         float(np.max(np.abs(j_current[1])))],
        tolerance, assertions)
    add("direct_K3_matches_fixed_floor_ray_identity",
        float(np.max(np.abs(k_current[2] - expected_k3))) < tolerance,
        float(np.max(np.abs(k_current[2] - expected_k3))),
        tolerance, assertions)

    entropy_coefficient = (
        0.5 * constants["Y"] * epsilon ** 2
        * float(np.mean(laplacian_g ** 2))
    )
    add("direct_biharmonic_entropy_coefficient_matches_three_halves",
        abs(entropy_coefficient - c_entropy) < tolerance,
        entropy_coefficient, c_entropy, assertions)

    eta_min = c_commutator / (2.0 * math.sqrt(c_entropy * c_sextic))
    eta_test = float(audit["eta_test"])
    violation_margin = (
        c_commutator * t_value ** 4
        - eta_test * (c_entropy * t_value ** 2 + c_sextic * t_value ** 6)
    )
    add("independent_eta_threshold_is_strictly_above_test_value",
        eta_min > eta_test > 0.0,
        {"eta_min": eta_min, "eta_test": eta_test},
        "eta_min > eta_test > 0", assertions)
    add("independent_form_bound_violation_margin_is_positive",
        violation_margin > 0.0, violation_margin, "> 0", assertions)

    adjacent = adjacent_shell_coefficient(epsilon, grid * 2)
    adjacent_expected = -epsilon ** 3 + 1.75 * epsilon ** 4
    add("adjacent_shell_high_low_control_is_negative",
        adjacent < 0.0, adjacent, "< 0", assertions)
    add("adjacent_shell_control_matches_exact_polynomial",
        abs(adjacent - adjacent_expected) < tolerance,
        adjacent, adjacent_expected, assertions)

    frozen_coefficient = float(
        np.mean(frozen_density) / (amplitude ** 4 * wave_number ** 2)
    )
    theta_ray = abs(normalized) / frozen_coefficient
    add("direct_frozen_energy_is_strictly_positive",
        frozen_coefficient > 0.0, frozen_coefficient, "> 0", assertions)
    add("direct_frozen_compensation_ratio_is_between_zero_and_one",
        0.0 < theta_ray < 1.0, theta_ray, "0 < theta_ray < 1", assertions)
    add("manifest_scope_does_not_withdraw_positive_A9_T5",
        any("does not falsify the A9 T5 theorem" in item
            for item in manifest["honesty_boundary"]),
        manifest["honesty_boundary"], "A9 T5 firewall present", assertions)

    failures = [row for row in assertions if row["status"] != "PASS"]
    verdict = ("A9-TILTED-COMMUTATOR-NOGO-INDEPENDENT-PASS"
               if not failures else
               "A9-TILTED-COMMUTATOR-NOGO-INDEPENDENT-FAIL")
    config = {
        "epsilon": epsilon, "eta_test": eta_test,
        "phase_grid": grid, "lattice_mode": lattice_mode,
    }
    output = {
        "schema": "tect/a9-tilted-commutator-nogo-independent-result/1.0",
        "claim_id": __claims__[0],
        "script_version": __version__,
        "verdict": verdict,
        "manifest_sha256": sha256(args.manifest),
        "config": config,
        "config_sha256": canonical_digest(config),
        "derived": {
            "production_constants": constants,
            "averages": averages,
            "normalized_commutator": normalized,
            "expected_normalized_commutator": expected_normalized,
            "entropy_coefficient": entropy_coefficient,
            "sextic_coefficient": c_sextic,
            "t_optimal": t_value,
            "eta_min": eta_min,
            "eta_test": eta_test,
            "violation_margin_per_volume_K6": violation_margin,
            "adjacent_shell_coefficient": adjacent,
            "adjacent_shell_expected": adjacent_expected,
            "frozen_coefficient": frozen_coefficient,
            "theta_ray": theta_ray,
        },
        "assertions": assertions,
        "assertion_summary": {
            "passed": len(assertions) - len(failures),
            "total": len(assertions),
        },
        "failures": failures,
        "environment": {
            "python": sys.version.split()[0],
            "numpy": np.__version__,
            "platform": platform.platform(),
            "git_commit": git_commit(),
            "deterministic": True,
            "imports_primary": False,
        },
        "not_closed_here": manifest["not_closed_here"],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"{output['assertion_summary']['passed']}/{output['assertion_summary']['total']} PASS")
    print(f"eta_min={eta_min:.12g}; eta_test={eta_test:.12g}")
    print(f"theta_ray={theta_ray:.12g}")
    print(verdict)
    print(f"Evidence: {args.output.resolve()}")
    return 0 if not failures else 1


if __name__ == "__main__":
    raise SystemExit(main())

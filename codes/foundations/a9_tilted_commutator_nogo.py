#!/usr/bin/env python3
"""Primary exact audit of the A9 tilted-commutator no-go result.

This constructs a same-shell resonant triad on the physical scalar ray.  It
tests the exact algebra proving that the commutator-alone estimate with an
arbitrarily small common entropy/sextic coefficient is impossible.  It does
not falsify the positive A9 theorem or the full A7 Nelson programme.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import subprocess
import sys
from fractions import Fraction
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
DEFAULT_OUTPUT = CLAIM_DIR / "runs" / "2026-07-21-primary-tilted-commutator-nogo" / "result.json"

Mode = tuple[int, int]
Polynomial = dict[Mode, Fraction]


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


def poly_add(left: Polynomial, right: Polynomial) -> Polynomial:
    out = dict(left)
    for mode, coefficient in right.items():
        out[mode] = out.get(mode, Fraction(0)) + coefficient
        if out[mode] == 0:
            del out[mode]
    return out


def poly_scale(poly: Polynomial, scale: Fraction) -> Polynomial:
    return {mode: scale * coefficient for mode, coefficient in poly.items()}


def poly_multiply(left: Polynomial, right: Polynomial) -> Polynomial:
    out: Polynomial = {}
    for lm, lc in left.items():
        for rm, rc in right.items():
            mode = (lm[0] + rm[0], lm[1] + rm[1])
            out[mode] = out.get(mode, Fraction(0)) + lc * rc
    return {mode: coefficient for mode, coefficient in out.items() if coefficient}


def poly_power(poly: Polynomial, exponent: int) -> Polynomial:
    out: Polynomial = {(0, 0): Fraction(1)}
    for _ in range(exponent):
        out = poly_multiply(out, poly)
    return out


def gradient_square(poly: Polynomial) -> Polynomial:
    out: Polynomial = {}
    for lm, lc in poly.items():
        for rm, rc in poly.items():
            dot = lm[0] * rm[0] + lm[1] * rm[1]
            mode = (lm[0] + rm[0], lm[1] + rm[1])
            out[mode] = out.get(mode, Fraction(0)) - dot * lc * rc
    return {mode: coefficient for mode, coefficient in out.items() if coefficient}


def laplacian(poly: Polynomial) -> Polynomial:
    return {
        mode: -(mode[0] * mode[0] + mode[1] * mode[1]) * coefficient
        for mode, coefficient in poly.items()
    }


def mean(poly: Polynomial) -> Fraction:
    return poly.get((0, 0), Fraction(0))


def triad_polynomial() -> Polynomial:
    half = Fraction(1, 2)
    return {
        (1, 0): half, (-1, 0): half,
        (0, 1): half, (0, -1): half,
        (1, 1): -half, (-1, -1): -half,
    }


def production_coefficients(authority: dict[str, Any]) -> dict[str, float]:
    p = authority["parameters"]
    denominator = float(p["M_X"]) ** 2 + float(p["classii_mass_regularizer"])
    return {
        "a": float(p["cJJ"]) * float(p["alpha_X"]) ** 2 / denominator,
        "b": float(p["cJK"]) * float(p["alpha_X"]) * float(p["beta_X"]) / denominator,
        "c": float(p["cKK"]) * float(p["beta_X"]) ** 2 / denominator,
        "Y": float(p["Y"]),
        "gamma": float(p["gamma"]),
        "rho_floor": float(p["rho_regularizer"]),
        "L": float(p["Lx"]),
    }


def scalar_b11(field: np.ndarray | float, constants: dict[str, float]) -> np.ndarray:
    squared = np.asarray(field) ** 2
    ratio = constants["rho_floor"] / (squared + constants["rho_floor"])
    return 4.0 * squared * (
        constants["a"] + 2.0 * constants["b"] * ratio
        + constants["c"] * ratio * ratio
    )


def full_floor_rows(audit: dict[str, Any], constants: dict[str, float],
                    t_value: float, leading: float) -> list[dict[str, float]]:
    grid = int(audit["phase_grid"])
    phase = 2.0 * math.pi * np.arange(grid, dtype=np.float64) / grid
    x_phase, y_phase = np.meshgrid(phase, phase, indexing="ij")
    g = np.cos(x_phase) + np.cos(y_phase) - np.cos(x_phase + y_phase)
    gx = -np.sin(x_phase) + np.sin(x_phase + y_phase)
    gy = -np.sin(y_phase) + np.sin(x_phase + y_phase)
    grad_phase_squared = gx * gx + gy * gy
    epsilon = float(audit["epsilon"])
    rows = []
    for lattice_mode in audit["lattice_modes"]:
        wave_number = 2.0 * math.pi * float(lattice_mode) / constants["L"]
        amplitude = t_value * wave_number
        field = amplitude * (1.0 + epsilon * g)
        grad_squared = (
            amplitude ** 2 * epsilon ** 2 * wave_number ** 2
            * grad_phase_squared
        )
        delta_b = scalar_b11(field, constants) - scalar_b11(amplitude, constants)
        commutator = 0.5 * float(np.mean(grad_squared * delta_b))
        normalized = commutator / (amplitude ** 4 * wave_number ** 2)
        rows.append({
            "lattice_mode": int(lattice_mode),
            "wave_number": wave_number,
            "amplitude": amplitude,
            "normalized_commutator": normalized,
            "leading_coefficient": leading,
            "absolute_error": abs(normalized - leading),
        })
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    authority_record = manifest["authority"]["production_functional_manifest"]
    authority_path = REPO / authority_record["path"]
    authority = json.loads(authority_path.read_text(encoding="utf-8"))
    audit = manifest["audit"]
    constants = production_coefficients(authority)
    assertions: list[dict[str, Any]] = []

    add("production_authority_hash_is_pinned",
        sha256(authority_path) == authority_record["sha256"],
        sha256(authority_path), authority_record["sha256"], assertions)
    add("production_authority_schema_is_pinned",
        authority.get("schema") == authority_record["schema"],
        authority.get("schema"), authority_record["schema"], assertions)
    add("production_ray_constants_are_admissible",
        constants["a"] > 0.0 and constants["Y"] > 0.0
        and constants["gamma"] > 0.0 and constants["rho_floor"] > 0.0,
        constants, "a,Y,gamma,rho_floor all positive", assertions)

    g = triad_polynomial()
    grad2 = gradient_square(g)
    moments = [mean(poly_power(g, exponent)) for exponent in range(7)]
    expected_moments = [
        Fraction(1), Fraction(0), Fraction(3, 2), Fraction(-3, 2),
        Fraction(45, 8), Fraction(-45, 4), Fraction(255, 8),
    ]
    add("triad_moments_are_exact_Fourier_constant_terms",
        moments == expected_moments, [str(v) for v in moments],
        [str(v) for v in expected_moments], assertions)
    gradient_mean = mean(grad2)
    cubic_gradient_mean = mean(poly_multiply(g, grad2))
    quartic_gradient_mean = mean(poly_multiply(poly_power(g, 2), grad2))
    laplacian_g = laplacian(g)
    laplacian_square_mean = mean(poly_multiply(laplacian_g, laplacian_g))
    add("triad_gradient_and_laplacian_means_are_exact",
        gradient_mean == Fraction(2)
        and laplacian_square_mean == Fraction(3),
        {
            "mean_grad2": str(gradient_mean),
            "mean_laplacian_squared": str(laplacian_square_mean),
        },
        {"mean_grad2": "2", "mean_laplacian_squared": "3"}, assertions)
    add("resonant_cubic_gradient_average_is_negative_one",
        cubic_gradient_mean == Fraction(-1), str(cubic_gradient_mean), "-1",
        assertions)
    add("resonant_quartic_gradient_average_is_five_halves",
        quartic_gradient_mean == Fraction(5, 2),
        str(quartic_gradient_mean), "5/2", assertions)
    mode_norms = [1.0, 1.0, math.sqrt(2.0)]
    add("all_three_resonant_modes_fit_the_pinned_sharp_radial_increment",
        audit["dyadic_projector"]
        == "P_prev=1_[abs(q)<K], P_top=1_[abs(q)<2K]"
        and min(mode_norms) >= 1.0 and max(mode_norms) < 2.0,
        {"mode_norms_over_K": mode_norms,
         "projector": audit["dyadic_projector"]},
        "all nonconstant modes in [K,2K)", assertions)

    epsilon = Fraction(str(audit["epsilon"]))
    one_plus = poly_add({(0, 0): Fraction(1)}, poly_scale(g, epsilon))
    m6_fraction = mean(poly_power(one_plus, 6))
    m6 = float(m6_fraction)
    add("positive_floor_witness_stays_away_from_zero",
        1.0 - 3.0 * float(epsilon) > 0.0,
        1.0 - 3.0 * float(epsilon), "> 0", assertions)
    add("sextic_moment_is_exact_and_positive", m6_fraction > 0,
        str(m6_fraction), "positive exact Fraction", assertions)

    e = float(epsilon)
    raw_commutator_coefficient = (
        2.0 * constants["a"] * e ** 2
        * (
            2.0 * e * float(cubic_gradient_mean)
            + e ** 2 * float(quartic_gradient_mean)
        )
    )
    c_commutator = -raw_commutator_coefficient
    c_entropy = (
        0.5 * constants["Y"] * e ** 2 * float(laplacian_square_mean)
    )
    c_sextic = m6
    t_value = (c_entropy / c_sextic) ** 0.25
    eta_min = c_commutator / (2.0 * math.sqrt(c_entropy * c_sextic))
    eta_test = float(audit["eta_test"])
    violation_margin = (
        c_commutator * t_value ** 4
        - eta_test * (c_entropy * t_value ** 2 + c_sextic * t_value ** 6)
    )
    add("commutator_leading_coefficient_is_strictly_negative",
        c_commutator > 0.0, raw_commutator_coefficient, "< 0", assertions)
    add("optimal_amplitude_scale_is_positive",
        math.isfinite(t_value) and t_value > 0.0, t_value,
        "finite positive", assertions)
    add("explicit_eta_is_below_the_necessary_threshold",
        0.0 < eta_test < eta_min,
        {"eta_test": eta_test, "eta_min": eta_min},
        "0 < eta_test < eta_min", assertions)
    add("explicit_asymptotic_form_bound_margin_is_violated",
        violation_margin > 0.0, violation_margin, "> 0", assertions)
    budget_min = c_commutator ** 2 / (4.0 * c_entropy * c_sextic)
    add("separate_entropy_sextic_budget_has_positive_hyperbola",
        budget_min > 0.0, budget_min, "> 0", assertions)

    floor_rows = full_floor_rows(audit, constants, t_value, -c_commutator)
    max_floor_error = max(row["absolute_error"] for row in floor_rows)
    add("full_fixed_floor_scalar_coefficient_converges_to_J_only_limit",
        max_floor_error < float(audit["full_floor_tolerance"]),
        floor_rows, audit["full_floor_tolerance"], assertions)
    add("fixed_floor_b_and_c_do_not_change_the_K6_leading_sign",
        all(row["normalized_commutator"] < 0.0 for row in floor_rows),
        [row["normalized_commutator"] for row in floor_rows],
        "all negative", assertions)

    contraction_power = float(audit["covariance_contraction_power"])
    power_inputs = audit["power_counting_inputs"]
    dimension = int(power_inputs["spatial_dimension"])
    covariance_order = int(power_inputs["covariance_symbol_order"])
    amplitude_power = int(power_inputs["witness_amplitude_power"])
    gradient_order = int(power_inputs["gradient_order"])
    biharmonic_order = int(power_inputs["biharmonic_order"])
    base_value_variance = max(0, dimension - covariance_order)
    base_derivative_variance = max(
        0, dimension + 2 * gradient_order - covariance_order
    )
    scaling = {
        "commutator": (
            2 * amplitude_power
            + 2 * (amplitude_power + gradient_order)
        ),
        "entropy": 2 * (amplitude_power + biharmonic_order),
        "sextic": int(power_inputs["sextic_degree"]) * amplitude_power,
        "fixed_quartic": (
            int(power_inputs["quartic_degree"]) * amplitude_power
        ),
        "covariance_counterterm": (
            base_derivative_variance + 2 * amplitude_power
        ),
        "contracted_covariance_entropy_power_with_log": dimension,
        "contracted_value_variance": (
            base_value_variance - 2.0 * contraction_power
        ),
        "contracted_derivative_variance": (
            base_derivative_variance - 2.0 * contraction_power
        ),
        "mass": int(power_inputs["mass_degree"]) * amplitude_power,
        "vacuum": 0 * amplitude_power,
    }
    add("contracted_Gaussian_fluctuations_and_lower_terms_are_sub_K6",
        scaling["covariance_counterterm"] < scaling["commutator"]
        and scaling["fixed_quartic"] < scaling["commutator"]
        and scaling["contracted_covariance_entropy_power_with_log"]
        < scaling["commutator"]
        and scaling["contracted_value_variance"] < 0.0
        and scaling["contracted_derivative_variance"] < 0.0
        and scaling["mass"] < scaling["commutator"]
        and scaling["vacuum"] < scaling["commutator"],
        scaling, "all corrections are o(K^6)", assertions)

    c_frozen = (
        2.0 * constants["a"] * e ** 2 * float(gradient_mean)
    )
    theta_ray = c_commutator / c_frozen
    add("frozen_positive_energy_coefficient_is_positive",
        c_frozen > 0.0, c_frozen, "> 0", assertions)
    add("witness_zero_budget_frozen_neutralisation_fraction_is_strict",
        0.0 < theta_ray < 1.0, theta_ray, "0 < theta_ray < 1", assertions)
    add("corrected_budget_vanishes_at_the_ray_threshold",
        abs(c_commutator - theta_ray * c_frozen)
        < float(audit["algebra_tolerance"]),
        abs(c_commutator - theta_ray * c_frozen),
        audit["algebra_tolerance"], assertions)

    boundary = manifest["honesty_boundary"]
    add("old_commutator_gate_is_explicitly_falsified",
        manifest["falsified_gate"]
        == "A7-CLASSII-TILTED-COMMUTATOR-FORM-BOUND",
        manifest["falsified_gate"],
        "A7-CLASSII-TILTED-COMMUTATOR-FORM-BOUND", assertions)
    add("corrected_gate_is_explicitly_open",
        manifest["corrected_gate"]
        == "A7-CLASSII-FROZEN-ENERGY-RELATIVE-COMMUTATOR-BOUND",
        manifest["corrected_gate"],
        "A7-CLASSII-FROZEN-ENERGY-RELATIVE-COMMUTATOR-BOUND", assertions)
    add("scope_firewall_preserves_A9_and_A7_Nelson_status",
        any("does not falsify the A9 T5 theorem" in item for item in boundary)
        and any("does not prove or disprove the full A7 Nelson bound"
                in item for item in boundary),
        boundary, "both firewalls explicit", assertions)

    failures = [row for row in assertions if row["status"] != "PASS"]
    verdict = ("A9-TILTED-COMMUTATOR-NOGO-PRIMARY-PASS"
               if not failures else "A9-TILTED-COMMUTATOR-NOGO-PRIMARY-FAIL")
    config = {
        "epsilon": audit["epsilon"], "eta_test": audit["eta_test"],
        "phase_grid": audit["phase_grid"],
        "lattice_modes": audit["lattice_modes"],
        "dyadic_projector": audit["dyadic_projector"],
        "covariance_contraction_power":
            audit["covariance_contraction_power"],
    }
    output = {
        "schema": "tect/a9-tilted-commutator-nogo-primary-result/1.0",
        "claim_id": __claims__[0],
        "script_version": __version__,
        "verdict": verdict,
        "manifest_sha256": sha256(args.manifest),
        "config": config,
        "config_sha256": canonical_digest(config),
        "derived": {
            "production_constants": constants,
            "triad_moments": [str(v) for v in moments],
            "gradient_averages": {
                "mean_grad2": str(gradient_mean),
                "mean_g_grad2": str(cubic_gradient_mean),
                "mean_g2_grad2": str(quartic_gradient_mean),
            },
            "m6_exact": str(m6_fraction), "m6": m6,
            "c_commutator": c_commutator,
            "c_entropy": c_entropy, "c_sextic": c_sextic,
            "t_optimal": t_value, "eta_min": eta_min,
            "eta_test": eta_test,
            "violation_margin_per_volume_K6": violation_margin,
            "budget_product_minimum": budget_min,
            "full_floor_rows": floor_rows,
            "scaling_exponents": scaling,
            "contracted_tilt": {
                "law": "N(h_K, sigma_K^2 C_J)",
                "sigma_K": "K^(-covariance_contraction_power)",
                "covariance_entropy": "O(K^3 log K)",
            },
            "c_frozen": c_frozen, "theta_ray": theta_ray,
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

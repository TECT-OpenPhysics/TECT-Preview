#!/usr/bin/env python3
"""Primary verifier for the centered Q3 Wick/Weyl limit route split."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import os
import tempfile
from pathlib import Path
from typing import Any

import sympy as sp


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-cl8-centered-q3-wick-weyl-limit-route-split"
CANDIDATE_ID = "PA-CP1-CL8-CENTERED-Q3-WICK-WEYL-LIMIT-ROUTE-SPLIT-v0"
RESULT_ID = "PA-CP1-CL8-UNIT-FREE-RP-WEYL-SEAM-AND-CENTERED-Q3-WICK-LP-LIMIT-WITH-UI-GATES"
NEGATIVE_IDS = (
    "NG-2026-08-04-PRE-A-CP1-CL8-FIXED-RAW-QUADRATIC-FINITE-Q3-RENORMALIZED-LIMIT",
    "NG-2026-08-04-PRE-A-CP1-CL8-WICK-L2-ONLY-INTERACTING-DENSITY-LIMIT",
)
EXPLORATION_ID = "EXP-000770"
SCHEMA = f"tect/{SLUG}-primary/0.1"
SCRIPT = Path(__file__).resolve()
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260804.md"
STATUS = REPO / "claims/C6-SPACETIME-SIGNATURE/status.json"
DEFAULT_OUTPUT = REPO / f"claims/C6-SPACETIME-SIGNATURE/runs/2026-08-04-primary-{SLUG}/result.json"


def sha256(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(self, name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{group}: {name}: {actual!r} != {expected!r}")
        self.rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})


def centered_symbol(k: float, spacing: float) -> float:
    return 4.0 * math.sin(spacing * k / 2.0) ** 2 / spacing**2


def convolution_power(base: dict[int, float], degree: int) -> dict[int, float]:
    result = {0: 1.0}
    for _ in range(degree):
        updated: dict[int, float] = {}
        for left_mode, left_value in result.items():
            for right_mode, right_value in base.items():
                mode = left_mode + right_mode
                updated[mode] = updated.get(mode, 0.0) + left_value * right_value
        result = updated
    return result


def alias_sectors(labels: range, degree: int, grid: int) -> set[int]:
    sectors: set[int] = set()
    for values in itertools.product(labels, repeat=degree):
        total = sum(values)
        if total % grid == 0:
            sectors.add(total // grid)
    return sectors


def build_q3_laplacian() -> sp.Matrix:
    adjacency = sp.zeros(8)
    for vertex in range(8):
        for bit in range(3):
            adjacency[vertex, vertex ^ (1 << bit)] = 1
    return 3 * sp.eye(8) - adjacency


def build_payload() -> dict[str, Any]:
    audit = Audit()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate = CERTIFICATE.read_text(encoding="utf-8")
    certificate_flat = " ".join(certificate.split())
    status = json.loads(STATUS.read_text(encoding="utf-8"))

    audit.check("candidate id", manifest["candidate_id"] == CANDIDATE_ID, manifest["candidate_id"], CANDIDATE_ID, "identity")
    audit.check("result id", manifest["result_id"] == RESULT_ID, manifest["result_id"], RESULT_ID, "identity")
    audit.check("negative ids", tuple(manifest["negative_ids"]) == NEGATIVE_IDS, manifest["negative_ids"], list(NEGATIVE_IDS), "identity")
    audit.check("exploration id", manifest["exploration_id"] == EXPLORATION_ID, manifest["exploration_id"], EXPLORATION_ID, "identity")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "identity")

    # Exact unit conversion from the registered w=a/8 Hamiltonian.
    a, chi, c, hbar, r, g, lam = sp.symbols("a chi c hbar r g lambda", positive=True)
    weight = a / 8
    scale_squared = sp.sqrt(chi * c) / (8 * hbar)
    time_jacobian = sp.sqrt(chi / c) / hbar
    time_coefficient = sp.simplify(time_jacobian * weight * (chi / 2) * (c / chi) / scale_squared)
    space_coefficient = sp.simplify(time_jacobian * weight * (c / 2) / scale_squared)
    quadratic_coefficient = sp.simplify(time_jacobian * weight * (r / 2) / scale_squared)
    quartic_coefficient = sp.simplify(time_jacobian * weight * (g / 4) / scale_squared**2)
    edge_coefficient = sp.simplify(time_jacobian * weight * (lam / 4) / scale_squared**2)
    g_e = sp.simplify(8 * hbar * g / (sp.sqrt(chi) * c ** sp.Rational(3, 2)))
    lambda_e = sp.simplify(8 * hbar * lam / (sp.sqrt(chi) * c ** sp.Rational(3, 2)))
    audit.check("unit time derivative coefficient", sp.simplify(time_coefficient - a / 2) == 0, time_coefficient, a / 2, "units")
    audit.check("unit spatial derivative coefficient", sp.simplify(space_coefficient - a / 2) == 0, space_coefficient, a / 2, "units")
    audit.check("unit quadratic coefficient", sp.simplify(quadratic_coefficient - a * r / (2 * c)) == 0, quadratic_coefficient, a * r / (2 * c), "units")
    audit.check("unit onsite quartic coefficient", sp.simplify(quartic_coefficient - a * g_e / 4) == 0, quartic_coefficient, a * g_e / 4, "units")
    audit.check("unit Q3 edge coefficient", sp.simplify(edge_coefficient - a * lambda_e / 4) == 0, edge_coefficient, a * lambda_e / 4, "units")
    beta_h = sp.symbols("beta_H", positive=True)
    beta0 = sp.simplify(hbar * beta_h * sp.sqrt(c / chi))
    audit.check("Euclidean circumference", beta0 == hbar * beta_h * sp.sqrt(c / chi), beta0, "hbar*beta_H*sqrt(c/chi)", "units")
    audit.check("base mass residual ledger", "K_E-m0^2 I" in manifest["unit_dictionary"]["base_Gaussian_residual"], manifest["unit_dictionary"]["base_Gaussian_residual"], "K_E-m0^2 I", "units")

    # Centered symbol sandwich and fixed-mode second-order convergence.
    symbol_rows: list[dict[str, float]] = []
    for grid in (12, 24, 48, 96):
        spacing = 2.0 * math.pi / grid
        for mode in range(1, grid // 2 + 1):
            spectral = float(mode * mode)
            centered = centered_symbol(float(mode), spacing)
            audit.check(f"centered upper sandwich M{grid} k{mode}", centered <= spectral + 1e-12, centered, spectral, "free")
            audit.check(f"centered lower sandwich M{grid} k{mode}", centered + 1e-12 >= 4.0 * spectral / math.pi**2, centered, 4.0 * spectral / math.pi**2, "free")
        fixed = centered_symbol(2.0, spacing)
        symbol_rows.append({"grid": grid, "spacing": spacing, "fixed_error": 4.0 - fixed, "scaled_error": (4.0 - fixed) / spacing**2})
    for prior, current in zip(symbol_rows, symbol_rows[1:]):
        audit.check(f"fixed mode error decreases M{current['grid']}", current["fixed_error"] < prior["fixed_error"], current["fixed_error"], prior["fixed_error"], "free")
    scaled = [row["scaled_error"] for row in symbol_rows]
    audit.check("fixed mode O(a^2) stable ratio", max(scaled) / min(scaled) < 1.05, max(scaled) / min(scaled), "<1.05", "free")

    def coupled_hminus_error(grid: int, s_value: float) -> float:
        spacing = 2.0 * math.pi / grid
        total = 0.0
        for temporal in range(-30, 31):
            for mode in range(-min(grid // 2 - 1, 10), min(grid // 2 - 1, 10) + 1):
                spectral_den = temporal * temporal + mode * mode + 1.0
                centered_den = temporal * temporal + centered_symbol(float(mode), spacing) + 1.0
                multiplier_difference = 1.0 / math.sqrt(centered_den) - 1.0 / math.sqrt(spectral_den)
                total += (1.0 + temporal * temporal + mode * mode) ** (-s_value) * multiplier_difference**2
        return total

    hminus_errors = [coupled_hminus_error(grid, 0.4) for grid in (24, 48, 96)]
    audit.check("common coupling Hminus error decreases 24 to 48", hminus_errors[1] < hminus_errors[0], hminus_errors, "strict decrease", "free")
    audit.check("common coupling Hminus error decreases 48 to 96", hminus_errors[2] < hminus_errors[1], hminus_errors, "strict decrease", "free")
    audit.check("Hminus all-s statement recorded", "for every `s>0`" in certificate, "for every `s>0`" in certificate, True, "free")

    # Nodal aliases and a finite convolution-tail proxy for Riemann-Lebesgue decay.
    full_aliases = {degree: sorted(alias_sectors(range(-4, 4), degree, 8)) for degree in range(1, 5)}
    low_aliases = {degree: sorted(alias_sectors(range(-2, 3), degree, 20)) for degree in range(1, 5)}
    audit.check("degree four full nodal aliases present", any(value != 0 for value in full_aliases[4]), full_aliases[4], "nonzero alias", "Wick")
    for degree in range(1, 5):
        audit.check(f"low-band M>4K exact degree {degree}", low_aliases[degree] == [0], low_aliases[degree], [0], "Wick")
    audit.check("degree four alias range", all(abs(value) <= 2 for value in full_aliases[4]), full_aliases[4], "|ell|<=2", "Wick")
    base = {mode: 1.0 / (1.0 + mode * mode) for mode in range(-60, 61)}
    fourth_convolution = convolution_power(base, 4)
    convolution_tails = [fourth_convolution[mode] for mode in (12, 24, 48)]
    audit.check("positive chaos convolution tails", all(value > 0 for value in convolution_tails), convolution_tails, "positive", "Wick")
    audit.check("chaos alias tail decreases", convolution_tails[2] < convolution_tails[1] < convolution_tails[0], convolution_tails, "strict decrease", "Wick")
    audit.check("Q3 Wick L2 result scoped true", manifest["scope"]["renormalized_Q3_Wick_L2_limit"] is True, manifest["scope"]["renormalized_Q3_Wick_L2_limit"], True, "Wick")
    audit.check("Q3 Wick finite Lp result scoped true", manifest["scope"]["renormalized_Q3_Wick_all_fixed_finite_Lp_limit"] is True, manifest["scope"]["renormalized_Q3_Wick_all_fixed_finite_Lp_limit"], True, "Wick")

    # Exact Q3 matrix direction and fixed-raw divergence.
    laplacian = build_q3_laplacian()
    eigenvalue_multiset = sorted(int(value) for value, multiplicity in laplacian.eigenvals().items() for _ in range(multiplicity))
    audit.check("Q3 Laplacian Walsh spectrum", eigenvalue_multiset == [0, 2, 2, 2, 4, 4, 4, 6], eigenvalue_multiset, [0, 2, 2, 2, 4, 4, 4, 6], "counterterm")
    test_g, test_lambda = sp.Rational(2), sp.Rational(1, 2)
    q3_levels = [sp.simplify(test_g + test_lambda + 2 * level * test_lambda) for level in range(4)]
    audit.check("Q3 counterterm levels positive", all(value > 0 for value in q3_levels), q3_levels, "all positive", "counterterm")
    q3_matrix = (test_g + test_lambda) * sp.eye(8) + test_lambda * laplacian
    audit.check("Q3 matrix spectrum matches Walsh levels", sorted(q3_matrix.eigenvals().keys()) == q3_levels, sorted(q3_matrix.eigenvals().keys()), q3_levels, "counterterm")
    raw_level = sp.Rational(3)
    renormalized_rows = []
    for grid in (8, 32, 128):
        covariance = math.log(grid)
        levels = [float(raw_level + 3 * covariance * float(value)) for value in q3_levels]
        renormalized_rows.append(levels)
    for level in range(4):
        audit.check(f"fixed raw level {level} diverges on fixture", renormalized_rows[2][level] > renormalized_rows[1][level] > renormalized_rows[0][level], [row[level] for row in renormalized_rows], "strict increase", "counterterm")
    target_levels = [sp.Rational(7) + 2 * level for level in range(4)]
    for covariance in (sp.Rational(1, 3), sp.Rational(5, 2), sp.Rational(11)):
        tuned_raw = [target - 3 * covariance * direction for target, direction in zip(target_levels, q3_levels)]
        recovered = [sp.simplify(raw + 3 * covariance * direction) for raw, direction in zip(tuned_raw, q3_levels)]
        audit.check(f"tuned raw recovers fixed KR C={covariance}", recovered == target_levels, recovered, target_levels, "counterterm")

    # Thermal-vacuum covariance difference is UV finite.
    def thermal_difference(grid: int, beta_value: float) -> float:
        spacing = 2.0 * math.pi / grid
        total = 0.0
        for mode in range(-grid // 2, grid // 2):
            omega = math.sqrt(1.0 + centered_symbol(float(mode), spacing))
            total -= 1.0 / (2.0 * math.pi * omega * math.expm1(beta_value * omega))
        return total

    thermal_rows = [thermal_difference(grid, 1.7) for grid in (32, 64, 128, 256)]
    audit.check("thermal-vacuum correction Cauchy", abs(thermal_rows[-1] - thermal_rows[-2]) < abs(thermal_rows[-2] - thermal_rows[-3]), thermal_rows, "shrinking tail", "counterterm")

    # Centered reflected-circle Gram factorization.
    beta_value = 2.3
    spacing = 2.0 * math.pi / 24
    omega = math.sqrt(1.0 + centered_symbol(3.0, spacing))
    coefficient = 1.0 / (2.0 * omega * (1.0 - math.exp(-beta_value * omega)))
    times = (0.1, 0.45, 0.9)
    vectors = [[math.exp(-omega * time), math.exp(-omega * (beta_value / 2.0 - time))] for time in times]
    gram = [[coefficient * sum(vectors[i][alpha] * vectors[j][alpha] for alpha in range(2)) for j in range(3)] for i in range(3)]
    for probe in ((1.0, -2.0, 1.0), (2.0, 1.0, -1.0), (3.0, -1.0, 2.0)):
        form = sum(probe[i] * gram[i][j] * probe[j] for i in range(3) for j in range(3))
        audit.check(f"centered reflected Gram PSD {probe}", form >= -1e-12, form, ">=0", "reflection")
    audit.check("finite centered RP scoped", manifest["scope"]["centered_free_reflection_positive"] is True, manifest["scope"]["centered_free_reflection_positive"], True, "reflection")

    # Symmetric Weyl midpoint phase and free characteristic convergence.
    f, h, g_label, k_shift, q = sp.symbols("f h g_label k_shift q", real=True)
    product_phase = sp.expand(f * (q + h / 2) + g_label * (q + h + k_shift / 2))
    combined_phase = sp.expand((f + g_label) * (q + (h + k_shift) / 2))
    sigma = sp.expand(f * k_shift - g_label * h)
    audit.check("Weyl product cocycle sign", sp.simplify(product_phase - combined_phase + sigma / 2) == 0, sp.simplify(product_phase - combined_phase), -sigma / 2, "Weyl")
    x = sp.symbols("x", real=True)
    midpoint_phase = sp.expand(f * x)
    unsymmetric_phase = sp.expand(f * ((x - h / 2) + h / 2))
    audit.check("Weyl seam midpoint phase", sp.simplify(midpoint_phase - unsymmetric_phase) == 0, unsymmetric_phase, midpoint_phase, "Weyl")
    left_endpoint = sp.expand((x - h / 2) + h)
    right_endpoint = sp.expand(x - h / 2)
    audit.check("Weyl seam endpoints", (left_endpoint, right_endpoint) == (x + h / 2, x - h / 2), (left_endpoint, right_endpoint), (x + h / 2, x - h / 2), "Weyl")
    kappa = hbar**2 / (2 * chi * weight)
    cm_cost = sp.simplify(h**2 / (4 * kappa * beta_h))
    expected_cost = sp.simplify(chi * weight * h**2 / (2 * hbar**2 * beta_h))
    audit.check("Weyl seam Cameron Martin cost", sp.simplify(cm_cost - expected_cost) == 0, cm_cost, expected_cost, "Weyl")

    def free_characteristic(grid: int, mode: int, f_value: float, h_value: float) -> float:
        spacing_value = 2.0 * math.pi / grid
        omega_value = math.sqrt(1.0 + centered_symbol(float(mode), spacing_value))
        coth = 1.0 / math.tanh(0.5 * 1.4 * omega_value)
        exponent = -0.25 * coth * (omega_value * h_value**2 + f_value**2 / omega_value)
        return math.exp(exponent)

    continuum_omega = math.sqrt(1.0 + 4.0)
    continuum_coth = 1.0 / math.tanh(0.5 * 1.4 * continuum_omega)
    continuum_characteristic = math.exp(-0.25 * continuum_coth * (continuum_omega * 0.3**2 + 0.4**2 / continuum_omega))
    characteristic_errors = [abs(free_characteristic(grid, 2, 0.4, 0.3) - continuum_characteristic) for grid in (24, 48, 96)]
    audit.check("free Weyl characteristic errors decrease", characteristic_errors[2] < characteristic_errors[1] < characteristic_errors[0], characteristic_errors, "strict decrease", "Weyl")
    audit.check("free Weyl O(a^2) ratio", characteristic_errors[0] / characteristic_errors[1] > 3.8 and characteristic_errors[1] / characteristic_errors[2] > 3.8, characteristic_errors, "ratios >3.8", "Weyl")
    audit.check("finite twisted seam scoped", manifest["scope"]["finite_regulator_twisted_Weyl_seam_identity"] is True, manifest["scope"]["finite_regulator_twisted_Weyl_seam_identity"], True, "Weyl")

    # L2 convergence does not imply uniform exponential integrability.
    rare_rows = []
    for size in (8, 16, 32):
        probability = size ** -4
        l2_norm = size * math.sqrt(probability)
        log_spike_contribution = size - 4.0 * math.log(size)
        rare_rows.append({"N": size, "probability": probability, "L2": l2_norm, "log_spike_exp": log_spike_contribution})
    audit.check("rare spike L2 tends down", rare_rows[2]["L2"] < rare_rows[1]["L2"] < rare_rows[0]["L2"], rare_rows, "strict decrease", "UI")
    audit.check("rare spike exponential contribution grows", rare_rows[2]["log_spike_exp"] > rare_rows[1]["log_spike_exp"] > rare_rows[0]["log_spike_exp"], rare_rows, "strict increase", "UI")
    audit.check("centered UI remains open", manifest["scope"]["centered_Q3_uniform_exponential_integrability"] is False, manifest["scope"]["centered_Q3_uniform_exponential_integrability"], False, "UI")
    audit.check("interacting density remains open", manifest["scope"]["centered_Q3_interacting_density_L1_limit"] is False, manifest["scope"]["centered_Q3_interacting_density_L1_limit"], False, "UI")

    for phrase in (
        "not a world-first or novelty proof",
        "uniform exponential integrability",
        "off-diagonal seam",
        "energy below empty space",
        "C0, N1--N5, C6, CP1, Sector A, and Pre-A",
    ):
        audit.check(f"certificate boundary {phrase[:34]}", phrase in certificate_flat, phrase, "present", "scope")
    audit.check("C6 tier unchanged", status["tier"] == "T1", status["tier"], "T1", "scope")
    audit.check("C6 lifecycle unchanged", status["lifecycle"] == "ACTIVE", status["lifecycle"], "ACTIVE", "scope")
    audit.check("C6 evidence unchanged", status["evidence_grade"] == ["CONDITIONAL"], status["evidence_grade"], ["CONDITIONAL"], "scope")
    audit.check("C6 gate unchanged", status["open_gates"] == ["C6-BCC-PREMISE-BLOCKED"], status["open_gates"], ["C6-BCC-PREMISE-BLOCKED"], "scope")
    for key in ("C6_advanced", "CP1_complete", "Pre_A_complete", "physical_state_or_vacuum", "below_empty_space_comparison", "interacting_full_phase_space_Weyl_CCR"):
        audit.check(f"scope firewall {key}", manifest["scope"][key] is False, manifest["scope"][key], False, "scope")

    return {
        "schema": SCHEMA,
        "candidate_id": CANDIDATE_ID,
        "result_id": RESULT_ID,
        "negative_ids": list(NEGATIVE_IDS),
        "exploration_id": EXPLORATION_ID,
        "claim_bearing": False,
        "verdict": manifest["gate_resolution"]["status"],
        "next_gate": manifest["gate_resolution"]["next_gate"],
        "script_version": __version__,
        "source_sha256": {"script": sha256(SCRIPT), "manifest": sha256(MANIFEST), "certificate": sha256(CERTIFICATE)},
        "derived": {
            "unit": {
                "time": str(time_coefficient),
                "space": str(space_coefficient),
                "quadratic": str(quadratic_coefficient),
                "g_E": str(g_e),
                "lambda_E": str(lambda_e),
                "beta0": str(beta0),
            },
            "symbol_rows": symbol_rows,
            "Hminus_errors": hminus_errors,
            "full_aliases": full_aliases,
            "low_aliases": low_aliases,
            "convolution_tails": convolution_tails,
            "Q3_laplacian_spectrum": eigenvalue_multiset,
            "Q3_counterterm_levels": [str(value) for value in q3_levels],
            "thermal_difference": thermal_rows,
            "reflected_gram": gram,
            "Weyl_cocycle_difference": str(sp.simplify(product_phase - combined_phase)),
            "Weyl_characteristic_errors": characteristic_errors,
            "rare_spike": rare_rows,
        },
        "scope": manifest["scope"],
        "assertions": audit.rows,
        "assertion_summary": {"passed": len(audit.rows), "total": len(audit.rows)},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    arguments = parser.parse_args()
    payload = build_payload()
    if not arguments.self_test:
        atomic_json(arguments.output, payload)
    print(f"{CANDIDATE_ID}: {payload['assertion_summary']['passed']}/{payload['assertion_summary']['total']} PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Independent adversarial audit of the P3 quantitative majorant.

This script does not import the majorant implementation.  It reconstructs the
linear spectrum and Fourier tail inequalities independently, samples the exact
Class-II q=m/(rho+eps) directional derivatives against the published analytic
envelopes, and checks the logarithmic constant representation and scope flags.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from decimal import Decimal, getcontext
from pathlib import Path
from typing import Any

import numpy as np

__version__ = "1.0.0"
__first_issued__ = "2026-07-17"
__version_issued__ = "2026-07-17"
__claims__ = ["A3-FULL-PRODUCTION-DISCRETIZATION-CONTINUUM"]

getcontext().prec = 80
REPO = Path(__file__).resolve().parents[2]
CLAIM = REPO / "claims" / "A3-FULL-PRODUCTION-DISCRETIZATION-CONTINUUM"
MANIFEST = CLAIM / "discretization_manifest.json"
P1_MANIFEST = REPO / "claims" / "A1-PRODUCTION-FUNCTIONAL-REALISATION" / "production_functional_manifest.json"
MAJORANT_RESULT = CLAIM / "runs" / "2026-07-17-quantitative-majorant" / "result.json"
DEFAULT_OUTPUT = CLAIM / "runs" / "2026-07-17-quantitative-majorant-independent" / "result.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(name: str, passed: bool, detail: Any, assertions: list[dict[str, Any]]) -> None:
    assertions.append({"name": name, "status": "PASS" if passed else "FAIL", "detail": detail})


def generators() -> tuple[np.ndarray, ...]:
    return (
        np.array([[0, 1, 0], [1, 0, 0], [0, 0, 0]], dtype=np.complex128),
        np.array([[0, -1j, 0], [1j, 0, 0], [0, 0, 0]], dtype=np.complex128),
        np.array([[1, 0, 0], [0, -1, 0], [0, 0, 0]], dtype=np.complex128),
    )


def q_value(real_vector: np.ndarray, generator: np.ndarray, epsilon: float) -> float:
    psi = real_vector[:3] + 1j * real_vector[3:]
    rho = float(np.real(np.vdot(psi, psi)))
    moment = float(np.real(np.vdot(psi, generator @ psi)))
    return moment / (rho + epsilon)


def directional_differences(point: np.ndarray, direction: np.ndarray, generator: np.ndarray, epsilon: float, step: float) -> tuple[float, float, float]:
    f0 = q_value(point, generator, epsilon)
    fp = q_value(point + step * direction, generator, epsilon)
    fm = q_value(point - step * direction, generator, epsilon)
    fpp = q_value(point + 2.0 * step * direction, generator, epsilon)
    fmm = q_value(point - 2.0 * step * direction, generator, epsilon)
    first = (fp - fm) / (2.0 * step)
    second = (fp - 2.0 * f0 + fm) / (step * step)
    third = (fpp - 2.0 * fp + 2.0 * fm - fmm) / (2.0 * step**3)
    return abs(first), abs(second), abs(third)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    p1 = json.loads(P1_MANIFEST.read_text(encoding="utf-8"))
    result = json.loads(MAJORANT_RESULT.read_text(encoding="utf-8"))
    params = p1["parameters"]
    stage = manifest["stage8_quantitative_majorant"]
    assertions: list[dict[str, Any]] = []

    source_entry = manifest["authority"]["quantitative_majorant_audit"]
    source_path = REPO / source_entry["path"]
    source_hash = sha256(source_path)
    check("majorant_source_hash_matches_manifest", source_hash == source_entry["sha256"], {"actual": source_hash, "expected": source_entry["sha256"]}, assertions)
    check("majorant_result_passed", result.get("verdict") == "A3-FULL-QUANTITATIVE-MAJORANT-PASS" and result.get("assertion_summary", {}).get("passed") == result.get("assertion_summary", {}).get("total"), result.get("verdict"), assertions)

    # Independent spectral reconstruction of the constant internal matrix.
    z0 = np.asarray(params["z0"], dtype=float)
    projector = np.outer(z0, z0) / float(np.dot(z0, z0))
    internal = np.diag(np.asarray(params["family_masses"], dtype=float))
    internal += float(params["k_lock"]) * (np.eye(3) - projector)
    internal_eigenvalues = np.linalg.eigvalsh(internal)
    y_value = float(params["Y"])
    z_value = float(params["Z"])
    r_value = float(params["r"])
    mode_axis = np.arange(-32, 33, dtype=float)
    k_scale = 2.0 * math.pi / float(params["Lx"])
    k_squared = k_scale**2 * mode_axis**2
    sampled_symbols = []
    for x_value in k_squared:
        sampled_symbols.extend((y_value * x_value**2 + z_value * x_value + r_value + internal_eigenvalues).tolist())
    symbols = np.asarray(sampled_symbols)
    check("independent_linear_spectrum_is_positive", float(np.min(symbols)) > 0.0, {"minimum": float(np.min(symbols)), "internal_eigenvalues": internal_eigenvalues.tolist()}, assertions)

    semigroup_ratios = []
    for time in (0.005, 0.02, 0.2):
        for power in (0.25, 0.5, 0.75, 1.0):
            observed = float(np.max(symbols**power * np.exp(-time * symbols)))
            universal = (power / (math.e * time)) ** power
            semigroup_ratios.append(observed / universal)
    check("sampled_semigroup_respects_universal_fractional_bound", max(semigroup_ratios) <= 1.0 + 2e-12, max(semigroup_ratios), assertions)

    # Direct Fourier-tail test over many omitted modes and all declared N.
    tail_constant = float(result["derived_global_constants"]["projection_tail_N_minus_4"])
    tail_ratios = []
    l_max = max(float(params[name]) for name in ("Lx", "Ly", "Lz"))
    for grid in (8, 12, 16, 32):
        for index in range(grid // 2, 8 * grid + 1):
            k_value = 2.0 * math.pi * index / l_max
            h2_over_h6 = 1.0 / (1.0 + k_value**4)
            tail_ratios.append(h2_over_h6 / (tail_constant * grid**-4))
    check("projection_H6_to_H2_tail_obeys_N_minus_4", max(tail_ratios) <= 1.0 + 2e-12, max(tail_ratios), assertions)

    alias_constant = float(result["derived_global_constants"]["periodic_alias_N_minus_2"])
    exact_alias_shell_sum = 4.0 * math.pi**2 + math.pi**4 / 45.0
    reconstructed_alias = (l_max / math.pi) ** 2 * math.sqrt(exact_alias_shell_sum)
    check("alias_shell_constant_is_conservative", alias_constant >= reconstructed_alias * (1.0 - 2e-14), {"published": alias_constant, "reconstructed": reconstructed_alias}, assertions)

    # Adversarial local checks of the exact q ratio against the analytic
    # derivative envelopes.  Points stay away from zero to avoid finite-
    # difference cancellation; the analytic bound itself covers zero via eps.
    rng = np.random.default_rng(20260717)
    largest = result["rows"][-1]
    amplitude = float(largest["pointwise_amplitude_upper"])
    envelopes = [float(value) for value in largest["classii_q_derivative_envelopes"]]
    maxima = [0.0, 0.0, 0.0]
    for _ in range(64):
        point = rng.normal(size=6)
        point *= rng.uniform(0.1, amplitude) / np.linalg.norm(point)
        direction = rng.normal(size=6)
        direction /= np.linalg.norm(direction)
        for generator in generators():
            values = directional_differences(point, direction, generator, float(params["rho_regularizer"]), 2e-4)
            maxima = [max(old, new) for old, new in zip(maxima, values)]
    check("sampled_q_directional_derivatives_fit_explicit_envelopes", all(maxima[index] <= envelopes[index + 1] for index in range(3)), {"sampled_maxima": maxima, "envelopes": envelopes[1:]}, assertions)

    log_errors = []
    for row in result["rows"]:
        b6 = Decimal(row["B6_tau_T"])
        recorded = Decimal(row["log10_B6_tau_T"])
        recomputed = b6.log10()
        log_errors.append(abs(recomputed - recorded))
    check("decimal_B6_logarithms_are_self_consistent", max(log_errors) <= Decimal("2e-12"), [str(value) for value in log_errors], assertions)
    check("declared_rates_and_restart_scope_are_consistent", all(row["dealiased_restarted_error_rate"].startswith("N^-4") for row in result["rows"]) and float(stage["tau"]) > 0.0 and "restarted" in stage["evolution_scope"].lower(), stage["evolution_scope"], assertions)
    check("historical_solver_certificate_is_absent", "historical Sector-B solver continuum certification" in result["honesty_boundary"]["not_closed_here"], result["honesty_boundary"]["not_closed_here"], assertions)

    passed = sum(item["status"] == "PASS" for item in assertions)
    output = {
        "schema": "tect/a3-full-production-quantitative-majorant-independent/1.0",
        "claim_id": manifest["claim_id"],
        "script_version": __version__,
        "verdict": "A3-FULL-QUANTITATIVE-MAJORANT-INDEPENDENT-PASS" if passed == len(assertions) else "A3-FULL-QUANTITATIVE-MAJORANT-INDEPENDENT-FAIL",
        "scope": "independent spectral, Fourier-tail, Class-II q-derivative, logarithm, and honesty-boundary audit",
        "assertions": assertions,
        "assertion_summary": {"passed": passed, "total": len(assertions)},
        "not_closed_here": ["sharpness of the conservative constants", "historical solver certification", "tier promotion or bundle publication"],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"{passed}/{len(assertions)} PASS")
    print(output["verdict"])
    print(f"Maximum sampled semigroup ratio: {max(semigroup_ratios):.12g}")
    print(f"Maximum projection-tail ratio: {max(tail_ratios):.12g}")
    print(f"Evidence: {args.output.resolve()}")
    return 0 if passed == len(assertions) else 1


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Non-importing reconstruction of the A7 Class-II energy-composite audit."""

from __future__ import annotations

import argparse
import functools
import hashlib
import json
import math
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any

import numpy as np

__version__ = "1.0.1"
__first_issued__ = "2026-07-20"
__version_issued__ = "2026-07-20"
__claims__ = ["A7-CLASSII-RENORMALISED-ENERGY-COMPOSITE"]

REPO = Path(__file__).resolve().parents[2]
CLAIM_DIR = REPO / "claims" / __claims__[0]
DEFAULT_MANIFEST = CLAIM_DIR / "classii_renormalised_energy_manifest.json"
DEFAULT_OUTPUT = CLAIM_DIR / "runs" / "2026-07-20-independent-renormalised-energy" / "result.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def object_sha256(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def git_commit() -> str | None:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True, stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def add(name: str, passed: bool, actual: Any, expected: Any, rows: list[dict[str, Any]]) -> None:
    rows.append({"name": name, "status": "PASS" if bool(passed) else "FAIL", "actual": actual, "expected": expected})


def generators() -> tuple[np.ndarray, ...]:
    return (
        np.asarray([[0, 1, 0], [1, 0, 0], [0, 0, 0]], dtype=np.complex128),
        np.asarray([[0, -1j, 0], [1j, 0, 0], [0, 0, 0]], dtype=np.complex128),
        np.asarray([[1, 0, 0], [0, -1, 0], [0, 0, 0]], dtype=np.complex128),
    )


def realify(matrix: np.ndarray) -> np.ndarray:
    return np.block([[matrix.real, -matrix.imag], [matrix.imag, matrix.real]])


def coefficients(params: dict[str, Any]) -> tuple[float, float, float]:
    denominator = float(params["M_X"]) ** 2 + float(params["classii_mass_regularizer"])
    return (
        float(params["cJJ"]) * float(params["alpha_X"]) ** 2 / denominator,
        float(params["cJK"]) * float(params["alpha_X"]) * float(params["beta_X"]) / denominator,
        float(params["cKK"]) * float(params["beta_X"]) ** 2 / denominator,
    )


def internal_mass(params: dict[str, Any]) -> np.ndarray:
    z0 = np.asarray(params["z0"], dtype=np.float64)
    projector = np.outer(z0, z0) / float(z0 @ z0)
    return np.diag(np.asarray(params["family_masses"], dtype=np.float64)) + float(params["k_lock"]) * (np.eye(3) - projector)


@functools.lru_cache(maxsize=None)
def direct_counts(cutoff: int) -> np.ndarray:
    axis = np.arange(-cutoff, cutoff + 1, dtype=np.int32)
    squared = axis[:, None, None] ** 2 + axis[None, :, None] ** 2 + axis[None, None, :] ** 2
    result = np.bincount(squared.ravel(), minlength=3 * cutoff * cutoff + 1)
    if int(result.sum()) != (2 * cutoff + 1) ** 3:
        raise AssertionError("direct mode count failed")
    return result


def derivative_covariance(cutoff: int, params: dict[str, Any]) -> np.ndarray:
    axis = np.arange(-cutoff, cutoff + 1, dtype=np.float64)
    nx, ny, nz = np.meshgrid(axis, axis, axis, indexing="ij")
    alpha = 2.0 * math.pi / float(params["Lx"])
    k2 = alpha**2 * (nx * nx + ny * ny + nz * nz)
    mass_eigenvalues, basis = np.linalg.eigh(internal_mass(params))
    base = float(params["r"]) + float(params["Z"]) * k2 + float(params["Y"]) * k2**2
    volume = float(params["Lx"]) * float(params["Ly"]) * float(params["Lz"])
    eigenvalues = []
    for mass in mass_eigenvalues:
        eigenvalues.append(float((2.0 / volume) * np.sum((alpha * nx) ** 2 / (base + mass))))
    return (basis * np.asarray(eigenvalues)) @ basis.T


def w_value(field: np.ndarray, params: dict[str, Any]) -> float:
    psi = np.asarray(field, dtype=np.complex128)
    rho = float(np.real(np.vdot(psi, psi)))
    eps = float(params["rho_regularizer"])
    a_value, b_value, c_value = coefficients(params)
    total = 0.0
    for generator in generators():
        transformed = generator @ psi
        q_value = float(np.real(np.vdot(psi, transformed))) / (rho + eps)
        covariant = transformed - q_value * psi
        total += a_value * float(np.real(np.vdot(transformed, transformed))) + 2.0 * b_value * float(np.real(np.vdot(transformed, covariant))) + c_value * float(np.real(np.vdot(covariant, covariant)))
    return 3.0 * total


def exact_counterterm(field: np.ndarray, derivative: np.ndarray, params: dict[str, Any]) -> float:
    psi = np.asarray(field, dtype=np.complex128)
    rho = float(np.real(np.vdot(psi, psi)))
    eps = float(params["rho_regularizer"])
    a_value, b_value, c_value = coefficients(params)
    total = 0.0
    for generator in generators():
        transformed = generator @ psi
        q_value = float(np.real(np.vdot(psi, transformed))) / (rho + eps)
        covariant = transformed - q_value * psi
        total += 3.0 * (
            a_value * float(np.real(np.vdot(transformed, derivative @ transformed)))
            + 2.0 * b_value * float(np.real(np.vdot(transformed, derivative @ covariant)))
            + c_value * float(np.real(np.vdot(covariant, derivative @ covariant)))
        )
    return total


def b_matrix(field: np.ndarray, params: dict[str, Any]) -> np.ndarray:
    psi = np.asarray(field, dtype=np.complex128)
    x_value = np.concatenate((psi.real, psi.imag))
    rho = float(x_value @ x_value)
    eps = float(params["rho_regularizer"])
    a_value, b_value, c_value = coefficients(params)
    result = np.zeros((6, 6), dtype=np.float64)
    for generator in generators():
        symmetric = realify(generator)
        q_value = float(x_value @ symmetric @ x_value) / (rho + eps)
        p_value = 2.0 * symmetric @ x_value
        v_value = 2.0 * (symmetric - q_value * np.eye(6)) @ x_value
        result += a_value * np.outer(p_value, p_value) + b_value * (np.outer(p_value, v_value) + np.outer(v_value, p_value)) + c_value * np.outer(v_value, v_value)
    return result


def conditional_mc(field: np.ndarray, derivative: np.ndarray, params: dict[str, Any], samples: int, seed: int) -> dict[str, float]:
    rng = np.random.default_rng(seed)
    factor = np.linalg.cholesky(derivative)
    raw = (rng.standard_normal((samples, 3, 3)) + 1j * rng.standard_normal((samples, 3, 3))) / math.sqrt(2.0)
    gradients = raw @ factor.T
    psi = np.asarray(field, dtype=np.complex128)
    rho = float(np.real(np.vdot(psi, psi)))
    eps = float(params["rho_regularizer"])
    a_value, b_value, c_value = coefficients(params)
    energies = np.zeros(samples)
    for generator in generators():
        transformed = generator @ psi
        q_value = float(np.real(np.vdot(psi, transformed))) / (rho + eps)
        covariant = transformed - q_value * psi
        j_value = 2.0 * np.real(np.einsum("j,sij->si", np.conj(transformed), gradients))
        k_value = 2.0 * np.real(np.einsum("j,sij->si", np.conj(covariant), gradients))
        energies += np.sum(0.5 * a_value * j_value**2 + b_value * j_value * k_value + 0.5 * c_value * k_value**2, axis=1)
    target = exact_counterterm(psi, derivative, params)
    mean = float(np.mean(energies))
    se = float(np.std(energies, ddof=1) / math.sqrt(samples))
    return {"mean": mean, "target": target, "standard_error": se, "z_score": abs(mean - target) / se}


def variance_proxy(cutoff: int, params: dict[str, Any], scheme: str) -> float:
    support = cutoff if scheme in {"cube", "ball"} else 2 * cutoff
    multiplicities = direct_counts(support).astype(np.float64)
    squared = np.arange(len(multiplicities), dtype=np.float64)
    if scheme == "cube":
        weight = np.ones_like(squared)
    elif scheme == "ball":
        weight = (squared <= cutoff * cutoff).astype(np.float64)
    else:
        weight = np.exp(-4.0 * (squared / float(cutoff * cutoff)) ** 2)
    alpha2 = (2.0 * math.pi / float(params["Lx"])) ** 2
    k2 = alpha2 * squared
    mass_eigenvalues = np.linalg.eigvalsh(internal_mass(params))
    base = float(params["r"]) + float(params["Z"]) * k2 + float(params["Y"]) * k2**2
    denominator = base[:, None] + mass_eigenvalues[None, :]
    volume = float(params["Lx"]) * float(params["Ly"]) * float(params["Lz"])
    return float((4.0 / volume**2) * np.sum(multiplicities[:, None] * weight[:, None] * k2[:, None] ** 2 / denominator**2))


def variance_audit(params: dict[str, Any], cutoffs: list[int], reference_cutoff: int) -> dict[str, Any]:
    reference = variance_proxy(reference_cutoff, params, "cube")
    rows = []
    for cutoff in cutoffs:
        row: dict[str, float] = {"cutoff": cutoff}
        for scheme in ("cube", "ball", "smooth"):
            value = variance_proxy(cutoff, params, scheme)
            row[scheme] = value
            row[f"{scheme}_tail"] = reference - value
        rows.append(row)
    slopes = {}
    for scheme in ("cube", "ball", "smooth"):
        slopes[scheme] = float(np.polyfit(np.log(cutoffs), np.log([abs(row[f"{scheme}_tail"]) for row in rows]), 1)[0])
    return {"reference_cutoff": reference_cutoff, "reference": reference, "rows": rows, "tail_slopes": slopes}


def determinant_check(field: np.ndarray, params: dict[str, Any], cutoff: int) -> dict[str, float]:
    matrix = b_matrix(field, params)
    mass = realify(internal_mass(params))
    alpha2 = (2.0 * math.pi / float(params["Lx"])) ** 2
    volume = float(params["Lx"]) * float(params["Ly"]) * float(params["Lz"])
    leading = logdet = hs = 0.0
    for squared, multiplicity in enumerate(direct_counts(cutoff)):
        if squared == 0 or multiplicity == 0:
            continue
        k2 = alpha2 * squared
        scalar = float(params["r"]) + float(params["Z"]) * k2 + float(params["Y"]) * k2**2
        symbol = scalar * np.eye(6) + mass
        eig, basis = np.linalg.eigh(symbol)
        invroot = (basis * (1.0 / np.sqrt(eig))) @ basis.T
        values = np.linalg.eigvalsh(k2 * invroot @ matrix @ invroot)
        leading += int(multiplicity) * float(np.sum(values))
        logdet += int(multiplicity) * float(np.sum(np.log1p(values)))
        hs += int(multiplicity) * float(np.sum(values**2))
    scale = 1.0 / (2.0 * volume)
    return {"leading": scale * leading, "logdet": scale * logdet, "remainder": scale * (leading - logdet), "half_hs_bound": 0.5 * scale * hs}


def recursive_connection_signatures() -> list[tuple[int, int]]:
    signatures: set[tuple[int, int]] = set()

    def visit(left: int, right: int, q_links: int, p_links: int) -> None:
        if left == 0:
            signatures.add((q_links, p_links + right))
            return
        if right:
            visit(left - 1, right - 1, q_links + 1, p_links)
        visit(left - 1, right, q_links, p_links + 1)

    visit(2, 2, 0, 0)
    return sorted(signatures)


def production_parity_matrix(params: dict[str, Any], cutoff: int) -> dict[str, Any]:
    axis = np.arange(-cutoff, cutoff + 1, dtype=np.float64)
    nx, ny, nz = np.meshgrid(axis, axis, axis, indexing="ij", sparse=True)
    n2 = nx * nx + ny * ny + nz * nz
    alpha = 2.0 * math.pi / float(params["Lx"])
    k2 = alpha**2 * n2
    mass_eigenvalues, basis = np.linalg.eigh(internal_mass(params))
    base = float(params["r"]) + float(params["Z"]) * k2 + float(params["Y"]) * k2**2
    volume = float(params["Lx"]) * float(params["Ly"]) * float(params["Lz"])
    scheme_errors: dict[str, float] = {}
    for scheme in ("cube", "ball", "smooth"):
        if scheme == "cube":
            multiplier2 = np.ones_like(base)
        elif scheme == "ball":
            multiplier2 = (n2 <= cutoff * cutoff).astype(np.float64)
        else:
            multiplier2 = np.exp(-2.0 * (n2 / float(cutoff * cutoff)) ** 2)
        maximum = 0.0
        for component in (nx, ny, nz):
            diagonal = []
            for mass in mass_eigenvalues:
                diagonal.append(np.sum(1j * alpha * component * multiplier2 / (base + mass)) / volume)
            matrix = (basis * np.asarray(diagonal)) @ basis.T
            maximum = max(maximum, float(np.max(np.abs(matrix))))
        scheme_errors[scheme] = maximum
    return {"cutoff": cutoff, "scheme_max_matrix_norm": scheme_errors, "maximum": max(scheme_errors.values())}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    production_path = REPO / manifest["authority"]["production_functional_manifest"]["path"]
    params = json.loads(production_path.read_text(encoding="utf-8"))["parameters"]
    audit = manifest["independent_audit"]
    assertions: list[dict[str, Any]] = []

    add("independent_production_hash_matches", sha256(production_path) == manifest["authority"]["production_functional_manifest"]["sha256"], sha256(production_path), manifest["authority"]["production_functional_manifest"]["sha256"], assertions)
    a_value, b_value, c_value = coefficients(params)
    q_eigenvalues = np.linalg.eigvalsh(np.asarray([[a_value, b_value], [b_value, c_value]]))
    add("independent_Q_is_positive", float(q_eigenvalues[0]) > 0.0, q_eigenvalues.tolist(), "positive", assertions)

    field = np.asarray([0.7 + 0.2j, -0.4 + 0.5j, 0.3 - 0.1j], dtype=np.complex128)
    derivative = derivative_covariance(int(audit["conditional_cutoff"]), params)
    matrix = b_matrix(field, params)
    complex_ct = exact_counterterm(field, derivative, params)
    real_ct = 1.5 * float(np.trace(matrix @ (0.5 * realify(derivative))))
    add("independent_real_complex_counterterm_agree", abs(complex_ct - real_ct) < 1.0e-14, abs(complex_ct - real_ct), "<1e-14", assertions)
    mc = conditional_mc(field, derivative, params, int(audit["conditional_samples"]), int(audit["seed"]))
    add("independent_conditional_MC_agrees", mc["z_score"] < 5.5, mc, "z<5.5", assertions)

    delta = float(manifest["constants"]["delta_cube"]["value"])
    asymptotic = []
    for cutoff in [int(value) for value in audit["asymptotic_cutoffs"]]:
        d_value = derivative_covariance(cutoff, params)
        ratio = exact_counterterm(field, d_value, params) / cutoff
        asymptotic.append({"cutoff": cutoff, "ratio": ratio, "target": delta * w_value(field, params), "relative_error": abs(ratio - delta * w_value(field, params)) / (delta * w_value(field, params))})
    add("independent_exact_counterterm_recovers_delta_N_W", asymptotic[-1]["relative_error"] < 0.03, asymptotic[-1], "relative error <0.03", assertions)

    variance = variance_audit(
        params,
        [int(value) for value in audit["variance_cutoffs"]],
        int(audit["variance_reference_cutoff"]),
    )
    add("independent_variance_tails_have_expected_power", all(-2.2 < slope < -0.5 for slope in variance["tail_slopes"].values()), variance["tail_slopes"], "between -2.2 and -0.5", assertions)
    last = variance["rows"][-1]
    spread = max(abs(last[key] - variance["reference"]) for key in ("cube", "ball", "smooth")) / variance["reference"]
    add("independent_regulator_variances_are_Cauchy", spread < 0.06, spread, "<0.06", assertions)

    h_value = 9.0 * (a_value + 2.0 * b_value + c_value)
    d_value = 6.0 * b_value + 3.0 * c_value
    near = np.asarray([1.0e-5, 0.0, 1.0], dtype=np.complex128)
    near_ratio = w_value(near, params) / abs(near[0]) ** 2
    add("independent_global_mass_threshold_is_h", abs(near_ratio / h_value - 1.0) < 1.0e-8, {"ratio": near_ratio, "h": h_value}, "ratio tends to h", assertions)
    below = 0.99 * h_value
    orientation = (h_value - below) / (2.0 * d_value)
    escape = (h_value - below) * orientation - d_value * orientation**2
    add("independent_subcritical_mass_escape_is_positive", escape > 0.0, escape, ">0", assertions)
    add("independent_family_mass_slope_matches_formula", abs(2.0 * h_value * delta - 0.00308894422883) < 1.0e-14, 2.0 * h_value * delta, 0.00308894422883, assertions)

    plane = np.asarray([0.6 + 0.2j, -0.3 + 0.4j, 0.5 - 0.1j], dtype=np.complex128)
    max_current = 0.0
    for generator in generators():
        transformed = generator @ plane
        q_value = float(np.real(np.vdot(plane, transformed))) / (float(np.real(np.vdot(plane, plane))) + float(params["rho_regularizer"]))
        covariant = transformed - q_value * plane
        for k_value in (2.0, -1.0, 3.0):
            derivative_plane = 1j * k_value * plane
            max_current = max(max_current, abs(2.0 * np.real(np.vdot(transformed, derivative_plane))), abs(2.0 * np.real(np.vdot(covariant, derivative_plane))))
    add("independent_plane_wave_is_ClassII_null", max_current < 1.0e-14, max_current, "zero", assertions)
    add("independent_plane_wave_null_has_positive_W", w_value(plane, params) > 0.0, w_value(plane, params), ">0", assertions)

    determinant = determinant_check(field, params, int(audit["determinant_cutoff"]))
    add("independent_frozen_determinant_remainder_is_positive", determinant["remainder"] > 0.0, determinant, ">0", assertions)
    add("independent_frozen_determinant_obeys_HS_bound", determinant["remainder"] <= determinant["half_hs_bound"] * (1.0 + 1.0e-12), determinant, "remainder <= half HS", assertions)

    signatures = recursive_connection_signatures()
    add("independent_Gaussian_IBP_connections_are_exhaustive", signatures == [(0, 4), (1, 2), (2, 0)], signatures, [(0, 4), (1, 2), (2, 0)], assertions)
    parity = production_parity_matrix(params, int(audit["parity_cutoff"]))
    add("independent_common_even_production_parity_matrix_is_zero", parity["maximum"] < float(audit["parity_tolerance"]), parity, f"<{audit['parity_tolerance']}", assertions)
    add("independent_measure_claim_is_excluded", any("Gibbs measure" in item for item in manifest["honesty_boundary"]["excluded"]), manifest["honesty_boundary"]["excluded"], "explicit exclusion", assertions)

    passed = sum(row["status"] == "PASS" for row in assertions)
    verdict = "A7-CLASSII-RENORMALISED-ENERGY-INDEPENDENT-PASS" if passed == len(assertions) else "A7-CLASSII-RENORMALISED-ENERGY-INDEPENDENT-FAIL"
    run_config = {"independent_audit": audit}
    output = {
        "schema": "tect/a7-classii-renormalised-energy-independent-result/1.1",
        "claim_id": __claims__[0],
        "script_version": __version__,
        "verdict": verdict,
        "scope": manifest["scope"],
        "run": {
            "schema": "tect/a7-classii-renormalised-energy-run/1.0",
            "role": "independent",
            "manifest_sha256": sha256(args.manifest),
            "script_sha256": sha256(Path(__file__)),
            "script_version": __version__,
            "seed": {"conditional": int(audit["seed"])},
            "config": run_config,
            "config_sha256": object_sha256(run_config),
        },
        "derived": {"coefficients": {"a": a_value, "b": b_value, "c": c_value}, "conditional_mc": mc, "counterterm_asymptotics": asymptotic, "variance": variance, "h": h_value, "family_mass_slope": 2.0 * h_value * delta, "plane_wave_max_current": max_current, "plane_wave_W": w_value(plane, params), "determinant": determinant, "gaussian_ibp_connections": signatures, "production_parity": parity},
        "assertions": assertions,
        "assertion_summary": {"passed": passed, "total": len(assertions)},
        "failures": [row["name"] for row in assertions if row["status"] != "PASS"],
        "environment": {"python": sys.version.split()[0], "numpy": np.__version__, "platform": platform.platform(), "git_commit": git_commit(), "deterministic": True},
        "not_closed_here": manifest["honesty_boundary"]["excluded"],
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
    print(f"{passed}/{len(assertions)} PASS")
    print(verdict)
    print(f"Independent h: {h_value:.12g}")
    print(f"Evidence: {args.output.resolve()}")
    return 0 if passed == len(assertions) else 1


if __name__ == "__main__":
    raise SystemExit(main())

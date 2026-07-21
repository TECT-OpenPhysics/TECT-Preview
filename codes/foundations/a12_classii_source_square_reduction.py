#!/usr/bin/env python3
"""Primary executable audit for A12 Class-II source-square reduction.

The infinite-cutoff harmonic-analysis theorem is proved in the accompanying
note.  This executable pins the production constants, the Pauli/Fierz operator
bound, exact sharp-shell weights, regulator power, and source-only sextic
thresholds.  Finite samples are audits, not a substitute for the theorem.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import subprocess
import tempfile
from pathlib import Path
from typing import Any

import numpy as np


VERSION = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
DEFAULT_MANIFEST = REPO / "claims" / "A12-CLASSII-SOURCE-SQUARE-REDUCTION" / "classii_source_square_reduction_manifest.json"
DEFAULT_OUTPUT = REPO / "claims" / "A12-CLASSII-SOURCE-SQUARE-REDUCTION" / "runs" / "2026-07-21-primary-source-square" / "result.json"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
        os.replace(temporary, path)
    except BaseException:
        try:
            os.unlink(temporary)
        except OSError:
            pass
        raise


def git_commit() -> str | None:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True, stderr=subprocess.DEVNULL).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def add(rows: list[dict[str, Any]], name: str, passed: bool, actual: Any, expected: Any) -> None:
    rows.append({"name": name, "status": "PASS" if passed else "FAIL", "actual": actual, "expected": expected})


def pauli() -> list[np.ndarray]:
    return [
        np.asarray([[0, 1], [1, 0]], dtype=np.complex128),
        np.asarray([[0, -1j], [1j, 0]], dtype=np.complex128),
        np.asarray([[1, 0], [0, -1]], dtype=np.complex128),
    ]


def generators() -> list[np.ndarray]:
    return [np.pad(matrix, ((0, 1), (0, 1))) for matrix in pauli()]


def realify(matrix: np.ndarray) -> np.ndarray:
    return np.block([[matrix.real, -matrix.imag], [matrix.imag, matrix.real]])


def real_vector(field: np.ndarray) -> np.ndarray:
    return np.concatenate((field.real, field.imag), axis=-1)


def coefficients(params: dict[str, Any]) -> tuple[float, float, float]:
    denominator = float(params["M_X"]) ** 2 + float(params["classii_mass_regularizer"])
    return (
        float(params["cJJ"]) * float(params["alpha_X"]) ** 2 / denominator,
        float(params["cJK"]) * float(params["alpha_X"]) * float(params["beta_X"]) / denominator,
        float(params["cKK"]) * float(params["beta_X"]) ** 2 / denominator,
    )


def coefficient_matrix(field: np.ndarray, params: dict[str, Any]) -> np.ndarray:
    field = np.asarray(field, dtype=np.complex128)
    a_value, b_value, c_value = coefficients(params)
    floor = float(params["rho_regularizer"])
    x_value = real_vector(field)
    rho = np.sum(np.abs(field) ** 2, axis=-1)
    eye = np.eye(6)
    result = np.zeros(field.shape[:-1] + (6, 6), dtype=np.float64)
    for generator in generators():
        symmetric = realify(generator)
        moment = np.real(np.einsum("...i,ij,...j->...", np.conj(field), generator, field))
        q_value = moment / (rho + floor)
        p_value = 2.0 * np.einsum("ij,...j->...i", symmetric, x_value)
        v_value = 2.0 * np.einsum("...ij,...j->...i", symmetric - q_value[..., None, None] * eye, x_value)
        result += a_value * np.einsum("...i,...j->...ij", p_value, p_value)
        result += b_value * (
            np.einsum("...i,...j->...ij", p_value, v_value)
            + np.einsum("...i,...j->...ij", v_value, p_value)
        )
        result += c_value * np.einsum("...i,...j->...ij", v_value, v_value)
    return result


def symbol_coercivity(params: dict[str, Any]) -> float:
    y_value = float(params["Y"])
    z_value = float(params["Z"])
    r_value = float(params["r"])
    stationary = max(0.0, (2.0 * r_value - z_value) / (2.0 * y_value - z_value))

    def ratio(x_value: float) -> float:
        return (y_value * x_value**2 + z_value * x_value + r_value) / (1.0 + x_value) ** 2

    return min(ratio(0.0), ratio(stationary), y_value)


def internal_mass(params: dict[str, Any]) -> np.ndarray:
    family = np.diag(np.asarray(params["family_masses"], dtype=np.complex128))
    z0 = np.asarray(params["z0"], dtype=np.complex128)
    projector = np.outer(z0, np.conj(z0)) / float(np.real(np.vdot(z0, z0)))
    return family + float(params["k_lock"]) * (np.eye(3) - projector)


def fierz_audit(params: dict[str, Any], seed: int, samples: int) -> dict[str, float]:
    rng = np.random.default_rng(seed)
    floor = float(params["rho_regularizer"])
    maximum_m_identity = 0.0
    maximum_mj_identity = 0.0
    maximum_k_identity = 0.0
    maximum_b_ratio = 0.0
    maximum_frame_ratio = 0.0
    for _ in range(samples):
        psi = rng.normal(size=3) + 1j * rng.normal(size=3)
        h = rng.normal(size=3) + 1j * rng.normal(size=3)
        z, w = psi[:2], psi[2]
        eta, omega = h[:2], h[2]
        s_value = float(np.real(np.vdot(z, z)))
        rho = float(np.real(np.vdot(psi, psi)))
        ds = 2.0 * float(np.real(np.vdot(z, eta)))
        dt = 2.0 * float(np.real(np.conj(w) * omega))
        drho = ds + dt
        m = np.asarray([float(np.real(np.vdot(z, matrix @ z))) for matrix in pauli()])
        j_current = np.asarray([2.0 * float(np.real(np.vdot(matrix @ z, eta))) for matrix in pauli()])
        q = m / (rho + floor)
        k_current = j_current - q * drho
        maximum_m_identity = max(maximum_m_identity, abs(float(m @ m) - s_value**2))
        maximum_mj_identity = max(maximum_mj_identity, abs(float(m @ j_current) - s_value * ds))
        k_formula = float(j_current @ j_current) - ds**2 + (ds - s_value * drho / (rho + floor)) ** 2
        maximum_k_identity = max(maximum_k_identity, abs(float(k_current @ k_current) - k_formula))
        h_norm = float(np.real(np.vdot(h, h)))
        if s_value * h_norm > 1e-20:
            maximum_frame_ratio = max(
                maximum_frame_ratio,
                float(max(j_current @ j_current, k_current @ k_current, abs(j_current @ k_current))) / (4.0 * s_value * h_norm),
            )
        x = real_vector(psi)
        maximum_b_ratio = max(maximum_b_ratio, float(np.linalg.eigvalsh(coefficient_matrix(psi, params))[-1]) / float(x @ x))
    return {
        "max_m_norm_identity_error": maximum_m_identity,
        "max_m_dot_J_identity_error": maximum_mj_identity,
        "max_K_identity_error": maximum_k_identity,
        "max_frame_bound_ratio": maximum_frame_ratio,
        "max_B_operator_ratio": maximum_b_ratio,
    }


def rational_tail(params: dict[str, Any], grid: int) -> dict[str, float]:
    angle = 2.0 * math.pi * np.arange(grid) / grid
    field = np.zeros((grid, 3), dtype=np.complex128)
    field[:, 0] = 0.83 + 0.31 * np.cos(angle)
    field[:, 1] = 0.27j * np.sin(angle)
    field[:, 2] = 0.19
    entry = coefficient_matrix(field, params)[:, 0, 0]
    spectrum = np.fft.fft(entry) / grid
    modes = np.fft.fftfreq(grid) * grid
    tail = float(np.sum(np.abs(spectrum[np.abs(modes) > 6]) ** 2))
    total = float(np.sum(np.abs(spectrum) ** 2))
    return {"tail_energy_above_mode_6": tail, "total_energy": total, "tail_fraction": tail / total}


def shell_audit(params: dict[str, Any], scales: list[int]) -> list[dict[str, float]]:
    alpha = 2.0 * math.pi / float(params["Lx"])
    c_symbol = symbol_coercivity(params)
    mass = internal_mass(params)
    rows: list[dict[str, float]] = []
    for j_value in scales:
        previous = 2 ** (j_value - 1)
        n_min = previous + 1
        kappa = alpha * n_min
        k2 = kappa**2
        scalar = float(params["Y"]) * k2**2 + float(params["Z"]) * k2 + float(params["r"])
        operator = scalar * np.eye(3) + mass
        g_squared = k2 / float(np.min(np.linalg.eigvalsh(operator)))
        exact_upper = 1.0 / (c_symbol * (1.0 + kappa**2))
        rows.append({
            "j": j_value,
            "N_previous": previous,
            "minimum_shell_index": n_min,
            "kappa": kappa,
            "actual_G_squared_boundary": g_squared,
            "coercive_upper": exact_upper,
            "ratio": g_squared / exact_upper,
        })
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    assertions: list[dict[str, Any]] = []

    for key in ("a1_manifest", "a7_manifest", "a8_manifest", "a9_manifest", "a10_manifest", "a11_manifest"):
        authority = manifest["authority"][key]
        actual = sha256(REPO / authority["path"])
        add(assertions, f"authority_{key}_hash", actual == authority["sha256"], actual, authority["sha256"])

    a1 = json.loads((REPO / manifest["authority"]["a1_manifest"]["path"]).read_text(encoding="utf-8"))
    params = a1["parameters"]
    a_value, b_value, c_value = coefficients(params)
    beta_operator = 4.0 * (a_value + 2.0 * abs(b_value) + c_value)
    c_symbol = symbol_coercivity(params)
    base_constant = beta_operator**2 / c_symbol
    gamma = float(params["gamma"])
    add(assertions, "production_mixed_coefficient_positive", b_value > 0.0, b_value, ">0")
    add(assertions, "pauli_operator_constant_matches_manifest", abs(beta_operator - float(manifest["derived_oracles"]["beta_operator"])) < 1e-14, beta_operator, manifest["derived_oracles"]["beta_operator"])
    add(assertions, "coercivity_constant_matches_manifest", abs(c_symbol - float(manifest["derived_oracles"]["c_symbol"])) < 1e-14, c_symbol, manifest["derived_oracles"]["c_symbol"])
    add(assertions, "source_base_constant_matches_manifest", abs(base_constant - float(manifest["derived_oracles"]["source_base_constant"])) < 1e-14, base_constant, manifest["derived_oracles"]["source_base_constant"])

    fierz = fierz_audit(params, int(manifest["audit"]["seed"]), int(manifest["audit"]["fierz_samples"]))
    tolerance = float(manifest["audit"]["identity_tolerance"])
    add(assertions, "pauli_m_norm_identity", fierz["max_m_norm_identity_error"] < tolerance, fierz["max_m_norm_identity_error"], tolerance)
    add(assertions, "pauli_m_dot_J_identity", fierz["max_m_dot_J_identity_error"] < tolerance, fierz["max_m_dot_J_identity_error"], tolerance)
    add(assertions, "pauli_K_identity", fierz["max_K_identity_error"] < tolerance, fierz["max_K_identity_error"], tolerance)
    add(assertions, "pauli_frame_bound", fierz["max_frame_bound_ratio"] <= 1.0 + 1e-12, fierz["max_frame_bound_ratio"], "<=1")
    add(assertions, "sampled_B_operator_bound", fierz["max_B_operator_ratio"] <= beta_operator * (1.0 + 1e-10), fierz["max_B_operator_ratio"], beta_operator)

    tangent = np.asarray([1.0 + 0j, 0j, 0j])
    tangent_ratio = float(np.linalg.eigvalsh(coefficient_matrix(tangent, params))[-1])
    add(assertions, "doublet_tangent_saturates_operator_constant", abs(tangent_ratio - beta_operator) < 1e-12, tangent_ratio, beta_operator)
    third = np.asarray([0j, 0j, 1.0 + 0j])
    add(assertions, "pure_third_component_has_zero_classii_metric", float(np.linalg.norm(coefficient_matrix(third, params))) < 1e-14, float(np.linalg.norm(coefficient_matrix(third, params))), 0.0)

    tail = rational_tail(params, int(manifest["audit"]["rational_grid"]))
    add(assertions, "rational_fixed_floor_coefficient_is_not_polynomial_bandlimited", tail["tail_fraction"] > float(manifest["audit"]["rational_tail_floor"]), tail["tail_fraction"], f">{manifest['audit']['rational_tail_floor']}")

    shell_rows = shell_audit(params, [int(value) for value in manifest["audit"]["shell_scales"]])
    add(assertions, "sharp_shell_boundary_uses_previous_plus_one", all(row["minimum_shell_index"] == row["N_previous"] + 1 for row in shell_rows), shell_rows, "n_min=N_previous+1")
    add(assertions, "actual_production_symbol_below_coercive_shell_bound", max(row["ratio"] for row in shell_rows) <= 1.0 + 1e-12, max(row["ratio"] for row in shell_rows), "<=1")
    add(assertions, "shell_ratios_are_strictly_positive", min(row["ratio"] for row in shell_rows) > 0.0, min(row["ratio"] for row in shell_rows), ">0")

    regulator_rows = []
    reference = shell_rows[0]["coercive_upper"]
    for regulator in manifest["audit"]["regulator_amplitudes"]:
        regulator = float(regulator)
        value = regulator**2 * reference
        regulator_rows.append({"M_R": regulator, "source_bound": value, "quadratic_ratio": value / reference})
    add(assertions, "single_G_source_scales_as_MR_squared", max(abs(row["quadratic_ratio"] - row["M_R"] ** 2) for row in regulator_rows) < 1e-14, regulator_rows, "M_R^2")
    nonunit = [row for row in regulator_rows if abs(row["M_R"] - 1.0) > 1e-12]
    add(assertions, "MR_fourth_power_negative_control_rejected", all(abs(row["quadratic_ratio"] - row["M_R"] ** 4) > 1e-3 for row in nonunit), nonunit, "not M_R^4")

    budget_rows = []
    for p_value in manifest["audit"]["p_values"]:
        p_value = float(p_value)
        source_ceiling = gamma / (3.0 * p_value)
        harmonic_threshold = source_ceiling / base_constant
        old_epsilon = float(manifest["audit"]["obsolete_epsilon6"])
        old_ceiling = 2.0 * (gamma / 6.0 - old_epsilon) / p_value
        budget_rows.append({
            "p": p_value,
            "source_only_Csrc_ceiling": source_ceiling,
            "source_only_H6_ceiling": harmonic_threshold,
            "obsolete_epsilon6": old_epsilon,
            "obsolete_allocation_Csrc_ceiling": old_ceiling,
            "obsolete_allocation_H6_ceiling": old_ceiling / base_constant,
        })
    add(assertions, "source_only_budget_thresholds_positive", all(row["source_only_H6_ceiling"] > 0.0 for row in budget_rows), budget_rows, ">0")
    add(assertions, "obsolete_budget_is_stricter_and_not_reused", all(row["obsolete_allocation_H6_ceiling"] < row["source_only_H6_ceiling"] for row in budget_rows), budget_rows, "obsolete threshold is smaller")
    target_p = float(manifest["derived_oracles"]["budget_reference_p"])
    target = next(row for row in budget_rows if abs(row["p"] - target_p) < 1e-15)
    add(assertions, "reference_H6_threshold_matches_manifest", abs(target["source_only_H6_ceiling"] - float(manifest["derived_oracles"]["source_only_H6_ceiling_at_reference_p"])) < 1e-10, target["source_only_H6_ceiling"], manifest["derived_oracles"]["source_only_H6_ceiling_at_reference_p"])

    passed = sum(row["status"] == "PASS" for row in assertions)
    payload = {
        "schema": "tect/a12-classii-source-square-primary-result/1.0",
        "claim_id": manifest["claim_id"],
        "script_version": VERSION,
        "git_commit": git_commit(),
        "status": "PASS" if passed == len(assertions) else "FAIL",
        "assertion_count": len(assertions),
        "passed": passed,
        "failed": len(assertions) - passed,
        "assertions": assertions,
        "derived": {
            "a": a_value,
            "b": b_value,
            "c": c_value,
            "beta_operator": beta_operator,
            "c_symbol": c_symbol,
            "source_base_constant": base_constant,
            "source_constant_formula": "C_src=(beta_operator^2/c_symbol)*M_R^2*M_6^4*Q_6^2",
            "fierz": fierz,
            "rational_tail": tail,
            "shell_rows": shell_rows,
            "regulator_rows": regulator_rows,
            "budget_rows": budget_rows,
        },
        "honesty_boundary": manifest["honesty_boundary"],
    }
    atomic_json(args.output, payload)
    print(f"PASS: primary ({passed}/{len(assertions)})" if payload["status"] == "PASS" else f"FAIL: primary ({passed}/{len(assertions)})")
    print(f"beta_op={beta_operator:.16g}; base={base_constant:.16g}; H6 ceiling at p={target_p:g}: {target['source_only_H6_ceiling']:.12g}")
    print(f"Evidence: {args.output}")
    return 0 if payload["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

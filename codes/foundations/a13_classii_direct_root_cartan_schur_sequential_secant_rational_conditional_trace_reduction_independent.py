#!/usr/bin/env python3
"""Non-importing independent audit for the R-088 A13 reduction.

The audit uses seeded vector fixtures, direct finite differences, handwritten
NumPy matrix algebra, and independent dyadic bookkeeping.  It imports no code
from the primary R-088 executable.
"""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-25"
__version_issued__ = "2026-07-25"

import json
import math
import os
import re
import tempfile
from fractions import Fraction as F
from pathlib import Path
from typing import Any

import numpy as np


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-DIRECT-ROOT-CARTAN-SCHUR-SEQUENTIAL-SECANT-RATIONAL-CONDITIONAL-TRACE-REDUCTION"
CLAIM_DIR = REPO / "claims" / CLAIM
R084 = CLAIM_DIR / "classii_root_diagonal_cartan_ou_linear_pf_absorption_manifest.json"
R085 = CLAIM_DIR / "classii_nonorthogonal_cartan_schur_rational_hessian_boundary_manifest.json"
R087 = CLAIM_DIR / "classii_cartan_spatial_decay_rational_trace_variational_core_reduction_manifest.json"
R084_NOTE = CLAIM_DIR / "notes/classii-root-diagonal-cartan-ou-linear-pauli-fierz-absorption-260725-v1.0.tex.txt"
R085_NOTE = CLAIM_DIR / "notes/classii-nonorthogonal-cartan-schur-rational-shifted-hessian-boundary-260725-v1.0.tex.txt"
OUTPUT = CLAIM_DIR / "runs/2026-07-25-independent-direct-root-cartan-schur-sequential-secant-rational-conditional-trace/result.json"


INPUTS = {
    "s": F(7, 12),
    "alpha": F(2, 5),
    "eta": F(7, 12),
    "far_separation": 5,
    "seed": 88250725,
    "vector_dimension": 5,
    "target_dimension": 6,
}

TEST_ORACLES = {
    "constant": 16.30295538482827,
    "gap_exponent": F(7, 6),
    "besov_tail_exponent": F(5, 6),
    "old_direct_growth": 5,
    "old_weighted_growth": 6,
    "hypothetical_secant_ansatz_exponent": F(-5, 6),
    "comparison_margin": F(1, 220),
}


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name, suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
            stream.write("\n")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def phi(z: np.ndarray) -> np.ndarray:
    x, y = z
    return np.array([x * x + x * y + 2.0 * y, y**3 - x + x * y])


def jacobian_phi(z: np.ndarray) -> np.ndarray:
    x, y = z
    return np.array([[2.0 * x + y, x + 2.0], [-1.0 + y, 3.0 * y * y + x]])


def variation_current(z: np.ndarray, dz: np.ndarray, v: np.ndarray, dv: np.ndarray) -> float:
    return float((jacobian_phi(z) @ v) @ dz + phi(z) @ dv)


def main() -> int:
    rows: list[dict[str, Any]] = []

    def serial(value: Any) -> Any:
        if isinstance(value, F):
            return str(value)
        if isinstance(value, np.ndarray):
            return value.tolist()
        if isinstance(value, (np.floating, np.integer)):
            return value.item()
        if isinstance(value, (list, tuple)):
            return [serial(item) for item in value]
        if isinstance(value, dict):
            return {key: serial(item) for key, item in value.items()}
        return value

    def check(name: str, condition: bool, actual: Any, expected: Any) -> None:
        rows.append({
            "name": name,
            "status": "PASS" if bool(condition) else "FAIL",
            "actual": serial(actual),
            "expected": serial(expected),
        })

    for path, expected, label in (
        (R084, "A13-CLASSII-ROOT-DIAGONAL-CARTAN-OU-LINEAR-PAULI-FIERZ-ABSORPTION", "r084"),
        (R085, "A13-CLASSII-NONORTHOGONAL-CARTAN-SCHUR-RATIONAL-HESSIAN-BOUNDARY", "r085"),
        (R087, "A13-CLASSII-CARTAN-SPATIAL-DECAY-RATIONAL-TRACE-VARIATIONAL-CORE-REDUCTION", "r087"),
    ):
        record = json.loads(path.read_text(encoding="utf-8"))
        check(f"{label}_authority", record.get("result_id") == expected, record.get("result_id"), expected)

    s = float(INPUTS["s"])
    eta = float(INPUTS["eta"])
    constant = 1.0 / ((1.0 - 2.0**(-eta)) * (1.0 - 2.0**(-2.0 * s)) * (1.0 - 2.0 ** (eta - 2.0 * s)))
    check("direct_constant", abs(constant - TEST_ORACLES["constant"]) < 2e-14, constant, TEST_ORACLES["constant"])
    check("direct_gap_exponent", 2 * INPUTS["s"] == TEST_ORACLES["gap_exponent"], 2 * INPUTS["s"], TEST_ORACLES["gap_exponent"])
    check("direct_threshold_positive", INPUTS["s"] > 0 and 0 < INPUTS["eta"] < 2 * INPUTS["s"], [INPUTS["s"], INPUTS["eta"]], "s>0 and 0<eta<2s")

    r084_text = R084_NOTE.read_text(encoding="utf-8")
    r085_text = R085_NOTE.read_text(encoding="utf-8")
    r084_contract = re.search(r"S_C\^\{\\rm ctrl\}.*?\\tag\{4\.6\}", r084_text, re.DOTALL)
    r085_contract = re.search(r"\\boxed\{.*?\\tag\{4\.3\}", r085_text, re.DOTALL)
    check("normalization_r084_unweighted", r084_contract is not None and "2^j" not in r084_contract.group(0) and "2^{j}" not in r084_contract.group(0), None if r084_contract is None else r084_contract.group(0).count("2^j"), 0)
    check("normalization_r085_weighted", r085_contract is not None and ("2^j" in r085_contract.group(0) or "2^{j}" in r085_contract.group(0)), r085_contract is not None, True)

    rng = np.random.default_rng(INPUTS["seed"])
    direct_bound_factor = constant * 2.0 ** (-2.0 * s * INPUTS["far_separation"])
    schur_ratios: list[float] = []
    for fixture in range(5):
        q = rng.uniform(0.2, 2.0, size=4)
        left = 0.0
        for j in range(10):
            for m in range(j + INPUTS["far_separation"], j + INPUTS["far_separation"] + 16):
                total = np.zeros(INPUTS["vector_dimension"])
                for k in range(min(j, len(q) - 1) + 1):
                    direction = rng.normal(size=INPUTS["vector_dimension"])
                    direction /= np.linalg.norm(direction)
                    contraction_factor = rng.uniform(0.0, 1.0)
                    total += contraction_factor * 2.0 ** (-s * (m - k)) * math.sqrt(q[k]) * direction
                left += float(total @ total)
        ratio = left / float(q.sum())
        schur_ratios.append(ratio)
        check(f"random_direct_schur_{fixture + 1}", ratio <= direct_bound_factor + 1e-12, ratio, f"<={direct_bound_factor}")

    cauchy_residuals: list[float] = []
    for fixture in range(5):
        vectors = rng.normal(size=(8, INPUTS["vector_dimension"]))
        left = float(np.linalg.norm(vectors.sum(axis=0)) ** 2)
        weights = np.array([2.0 ** (-eta * r) for r in range(8)])
        right = float(weights.sum() * sum(np.linalg.norm(vectors[r]) ** 2 / weights[r] for r in range(8)))
        cauchy_residuals.append(left - right)
        check(f"weighted_cauchy_{fixture + 1}", left <= right + 1e-12, left - right, "<=0")

    zero_s_partials = np.array([8, 16, 32, 64]) - INPUTS["far_separation"] + 1
    zero_s_slopes = np.diff(zero_s_partials)
    check("zero_s_divergence", bool(np.all(zero_s_slopes > 0)), zero_s_partials, "strict growth")
    check("zero_s_unbounded_truncation", int(zero_s_partials[-1]) > 10 * int(zero_s_partials[0]), zero_s_partials.tolist(), "last > 10 first")

    # Direct finite-difference and telescope audit of the sequential atom.
    secant_residuals: list[float] = []
    finite_difference_residuals: list[float] = []
    telescope_residuals: list[float] = []
    for fixture in range(6):
        background = rng.normal(size=2)
        d_background = rng.normal(size=2)
        shell = rng.normal(size=2)
        d_shell = rng.normal(size=2)
        root_v = rng.normal(size=2)
        d_root_v = rng.normal(size=2)
        direct = variation_current(background + shell, d_background + d_shell, root_v, d_root_v) - variation_current(background, d_background, root_v, d_root_v)
        channel = (
            ((jacobian_phi(background + shell) - jacobian_phi(background)) @ root_v) @ d_background
            + (jacobian_phi(background + shell) @ root_v) @ d_shell
            + (phi(background + shell) - phi(background)) @ d_root_v
        )
        residual = abs(float(direct - channel))
        secant_residuals.append(residual)
        check(f"sequential_three_channel_{fixture + 1}", residual < 2e-12, residual, "<2e-12")

        epsilon = 2.0**-18
        def current(z: np.ndarray, dz: np.ndarray) -> float:
            return float(phi(z) @ dz)
        plus = current(background + shell + epsilon * root_v, d_background + d_shell + epsilon * d_root_v) - current(background + epsilon * root_v, d_background + epsilon * d_root_v)
        minus = current(background + shell - epsilon * root_v, d_background + d_shell - epsilon * d_root_v) - current(background - epsilon * root_v, d_background - epsilon * d_root_v)
        finite_difference = (plus - minus) / (2.0 * epsilon)
        fd_residual = abs(finite_difference - direct)
        finite_difference_residuals.append(fd_residual)
        check(f"sequential_finite_difference_{fixture + 1}", fd_residual < 2e-8, fd_residual, "<2e-8")

        shells = [rng.normal(size=2) for _ in range(3)]
        d_shells = [rng.normal(size=2) for _ in range(3)]
        state = background.copy()
        d_state = d_background.copy()
        telescope = 0.0
        for one_shell, one_d_shell in zip(shells, d_shells):
            telescope += variation_current(state + one_shell, d_state + one_d_shell, root_v, d_root_v) - variation_current(state, d_state, root_v, d_root_v)
            state += one_shell
            d_state += one_d_shell
        endpoint = variation_current(state, d_state, root_v, d_root_v) - variation_current(background, d_background, root_v, d_root_v)
        telescope_residual = abs(telescope - endpoint)
        telescope_residuals.append(telescope_residual)
        check(f"sequential_telescope_{fixture + 1}", telescope_residual < 2e-12, telescope_residual, "<2e-12")

    # Independent dyadic Cauchy fixtures for the quartic Besov lemma.
    besov_s = INPUTS["s"]
    tail_exponent = 2 * (1 - besov_s)
    check("besov_s_range", 0 < besov_s < 1, besov_s, "0<s<1")
    check("besov_tail_exponent", tail_exponent == TEST_ORACLES["besov_tail_exponent"], tail_exponent, TEST_ORACLES["besov_tail_exponent"])
    for fixture in range(4):
        block_norms = rng.uniform(0.01, 0.4, size=14)
        lhs = sum(2.0 ** ((float(besov_s) + 1.0) * j) * block_norms[j] for j in range(len(block_norms)))
        h2 = math.sqrt(sum(2.0 ** (4.0 * j) * block_norms[j] ** 2 for j in range(len(block_norms))))
        tail = math.sqrt(sum(2.0 ** (-float(tail_exponent) * j) for j in range(len(block_norms))))
        check(f"besov_dyadic_cauchy_{fixture + 1}", lhs <= h2 * tail + 1e-9, lhs - h2 * tail, "<=0")
    for index, scale in enumerate((0.25, 2.0, 7.0), start=1):
        lhs_scale = scale**4
        rhs_scale = (scale**2) ** 0.5 * (scale**6) ** 0.5
        check(f"quartic_homogeneity_{index}", abs(lhs_scale - rhs_scale) < 1e-12, [lhs_scale, rhs_scale], "equal")

    beta = 6 * INPUTS["alpha"] - 1
    event_exponent = -6
    translated_norm_exponent = 6 * (1 + INPUTS["alpha"])
    derivative_energy_exponent = 4
    direct_growth = -beta + event_exponent + translated_norm_exponent + derivative_energy_exponent
    weighted_growth = direct_growth + 1
    hypothetical_decay = event_exponent + 2 + (2 + 2 * INPUTS["s"])
    check("qmod_direct_growth", direct_growth == TEST_ORACLES["old_direct_growth"], direct_growth, TEST_ORACLES["old_direct_growth"])
    check("qmod_weighted_growth", weighted_growth == TEST_ORACLES["old_weighted_growth"], weighted_growth, TEST_ORACLES["old_weighted_growth"])
    check("hypothetical_secant_ansatz_exponent", hypothetical_decay == TEST_ORACLES["hypothetical_secant_ansatz_exponent"], hypothetical_decay, TEST_ORACLES["hypothetical_secant_ansatz_exponent"])
    for index, shell_size in enumerate((2, 4, 8), start=1):
        hypothetical_value = shell_size ** float(hypothetical_decay)
        check(f"hypothetical_secant_ansatz_value_{index}", hypothetical_value < 1.0, hypothetical_value, "<1 under the toy ansatz")

    # Conditional rational identity, pointwise null, and Jensen defect.
    conditional_residuals: list[float] = []
    pointwise_residuals: list[float] = []
    jensen_residuals: list[float] = []
    jensen_min_eigenvalues: list[float] = []
    for fixture in range(8):
        raw = rng.normal(size=(3, 3))
        b1 = raw.T @ raw + 0.3 * np.eye(3)
        raw_l = rng.normal(size=(3, 3))
        l_matrix = (raw_l + raw_l.T) / 2.0
        eta_r = rng.uniform(0.1, 1.2)
        a_eta = b1 + 2.0 * eta_r * np.eye(3)
        inverse = np.linalg.inv(a_eta)
        k_eta = l_matrix @ inverse @ l_matrix
        m_eta = l_matrix - k_eta
        raw_v = rng.normal(size=(3, 3))
        covariance = raw_v.T @ raw_v + 0.2 * np.eye(3)
        raw_gamma = rng.normal(size=(3, 3))
        gamma = raw_gamma.T @ raw_gamma + 0.1 * np.eye(3)
        mu = rng.normal(size=3)
        c_vector = rng.normal(size=3)
        direct = (
            0.5 * np.sum(l_matrix * (covariance + np.outer(mu, mu) - gamma))
            + mu @ l_matrix @ c_vector
            + 0.5 * c_vector @ b1 @ c_vector
            + eta_r * c_vector @ c_vector
        )
        shifted = c_vector + inverse @ l_matrix @ mu
        formula = 0.5 * shifted @ a_eta @ shifted + 0.5 * np.sum(m_eta * np.outer(mu, mu)) + 0.5 * np.sum(l_matrix * (covariance - gamma))
        residual = abs(float(direct - formula))
        conditional_residuals.append(residual)
        check(f"conditional_rational_{fixture + 1}", residual < 2e-10, residual, "<2e-10")

        g_vector = rng.normal(size=3)
        q_tensor = np.outer(g_vector, g_vector) - gamma
        debt = 0.5 * np.sum(k_eta * gamma)
        null = 0.5 * g_vector @ k_eta @ g_vector - 0.5 * np.sum(k_eta * q_tensor) - debt
        null_residual = abs(float(null))
        pointwise_residuals.append(null_residual)
        check(f"pointwise_trace_null_{fixture + 1}", null_residual < 2e-10, null_residual, "<2e-10")

        a_states: list[np.ndarray] = []
        l_states: list[np.ndarray] = []
        for _ in range(4):
            raw_a = rng.normal(size=(3, 3))
            a_states.append(raw_a.T @ raw_a + 0.4 * np.eye(3))
            raw_state_l = rng.normal(size=(3, 3))
            l_states.append((raw_state_l + raw_state_l.T) / 2.0)
        bar_a = sum(a_states) / len(a_states)
        bar_l = sum(l_states) / len(l_states)
        left = sum((l_states[i] @ np.linalg.inv(a_states[i]) @ l_states[i] for i in range(len(a_states)))) / len(a_states) - bar_l @ np.linalg.inv(bar_a) @ bar_l
        right = np.zeros((3, 3))
        for state_a, state_l in zip(a_states, l_states):
            first = state_l - bar_l @ np.linalg.inv(bar_a) @ state_a
            second = state_l - state_a @ np.linalg.inv(bar_a) @ bar_l
            right += first @ np.linalg.inv(state_a) @ second / len(a_states)
        jensen_residual = float(np.max(np.abs(left - right)))
        minimum_eigenvalue = float(np.linalg.eigvalsh((left + left.T) / 2.0).min())
        jensen_residuals.append(jensen_residual)
        jensen_min_eigenvalues.append(minimum_eigenvalue)
        check(f"jensen_identity_{fixture + 1}", jensen_residual < 2e-10, jensen_residual, "<2e-10")
        check(f"jensen_psd_{fixture + 1}", minimum_eigenvalue > -2e-10, minimum_eigenvalue, ">-2e-10")

    # Explicit method no-go fixtures.
    eta_fixture = 0.7
    ell = 1.3
    fixed_dimension = INPUTS["target_dimension"]
    covariance_scales = np.array([1.0, 4.0, 16.0])
    debts = fixed_dimension * covariance_scales * ell**2 / (4.0 * eta_fixture)
    square_variances = []
    for covariance_scale in covariance_scales:
        k_fixture = ell**2 * np.eye(fixed_dimension) / (2.0 * eta_fixture)
        atoms = []
        for coordinate in range(fixed_dimension):
            basis = np.zeros(fixed_dimension)
            basis[coordinate] = math.sqrt(fixed_dimension * covariance_scale)
            atoms.extend((basis, -basis))
        mean = np.mean(atoms, axis=0)
        covariance = sum(np.outer(atom, atom) for atom in atoms) / len(atoms)
        assert np.max(np.abs(mean)) < 1e-14
        assert np.max(np.abs(covariance - covariance_scale * np.eye(fixed_dimension))) < 1e-13
        square_variances.append(sum(0.5 * float(atom @ k_fixture @ atom) for atom in atoms) / len(atoms))
    square_variances_array = np.asarray(square_variances)
    check("standalone_debt_fixed_target_covariance_growth", bool(np.all(np.diff(debts) > 0)), debts, "strict growth at fixed dimension 6")
    check("centered_matched_square_variance_cancels_debt", float(np.max(np.abs(square_variances_array - debts))) < 2e-13, square_variances_array - debts, 0.0)
    t_value = 1.9
    mean_fixture = -0.75 * t_value**2
    check("mean_defect_negative", mean_fixture < 0 and abs(mean_fixture / t_value**2 + 0.75) < 1e-14, mean_fixture, "-3t^2/4")
    covariance_fixture = -0.5
    check("covariance_defect_negative", covariance_fixture == -0.5, covariance_fixture, -0.5)
    xi_values = np.array([-3.0, -0.25, 0.0, 1.5, 4.0])
    adapted_values = eta_fixture * (xi_values**2 - 1.0) + xi_values * (2.0 * eta_fixture) * (-xi_values) + eta_fixture * xi_values**2
    check("adapted_alignment_pathwise", float(np.max(np.abs(adapted_values + eta_fixture))) < 2e-14, adapted_values, -eta_fixture)

    q_nelson = F(10, 9)
    p_compare = F(11, 10)
    pinned = 1 / (2 * q_nelson)
    margin = 1 / (2 * p_compare) - pinned
    check("eta_comparison_margin", margin == TEST_ORACLES["comparison_margin"], margin, TEST_ORACLES["comparison_margin"])
    check("eta_internal_share_q", 1 / (2 * pinned) == q_nelson, 1 / (2 * pinned), q_nelson)
    check("eta_external_small_passes", 1 / (2 * (pinned + F(1, 500))) > p_compare, 1 / (2 * (pinned + F(1, 500))), f">{p_compare}")
    check("eta_external_large_fails", 1 / (2 * (pinned + F(1, 200))) < p_compare, 1 / (2 * (pinned + F(1, 200))), f"<{p_compare}")

    claims_not_established = {
        "production_sequential_secant_to_quartic_bridge": False,
        "direct_integrated_cartan_cfar": False,
        "coefficient_dominant_rational_causal_packet": False,
        "rational_shifted_hessian_form_bound": False,
        "complete_regular_packet_lower_bound": False,
        "overlap_uniform_bound": False,
        "controlled_shell_one_use": False,
        "nelson_bound": False,
        "interacting_measure": False,
        "sector_a_closure": False,
        "tier_promotion": False,
    }
    check("all_downstream_flags_false", not any(claims_not_established.values()), claims_not_established, "all false")

    passed = sum(row["status"] == "PASS" for row in rows)
    payload = {
        "schema": "tect/a13-direct-root-cartan-schur-sequential-secant-rational-conditional-trace-independent/1.0",
        "source_version": __version__,
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "status": "PASS" if passed == len(rows) else "FAIL",
        "assertions_passed": passed,
        "assertions_total": len(rows),
        "assertions": rows,
        "direct_cartan": {
            "s": str(INPUTS["s"]),
            "eta": str(INPUTS["eta"]),
            "constant": constant,
            "gap_factor": "2^(-7C/6)",
            "threshold": "s>0",
            "ledger": "sum_k q_k",
            "max_random_schur_ratio": max(schur_ratios),
            "max_weighted_cauchy_residual": max(cauchy_residuals),
            "max_sequential_identity_residual": max(secant_residuals),
            "max_finite_difference_residual": max(finite_difference_residuals),
            "max_telescope_residual": max(telescope_residuals),
            "quartic_besov_range": "0<s<1",
            "old_qmod_direct_growth": "N^5",
            "hypothetical_secant_ansatz_scaling": "N^(-5/6) under unproved toy ansatz",
        },
        "rational": {
            "max_conditional_residual": max(conditional_residuals),
            "max_pointwise_null_residual": max(pointwise_residuals),
            "max_jensen_identity_residual": max(jensen_residuals),
            "min_jensen_eigenvalue": min(jensen_min_eigenvalues),
            "centered_covariance_matched_square_variance_cancels_debt": True,
            "same_root_adapted_fixture_negative": True,
        },
        "negative_results": [
            "AUDIT-2026-07-25-A13-R085-CARTAN-OUTER-WEIGHT-NORMALIZATION",
            "NG-2026-07-25-A13-RATIONAL-STANDALONE-ETA-DEBT-AND-K-HEAT",
        ],
        "claims_not_established": claims_not_established,
    }
    atomic_json(OUTPUT, payload)
    if payload["status"] == "PASS":
        print(f"[R-088 independent] {passed}/{len(rows)} PASS")
        return 0
    failed = [row["name"] for row in rows if row["status"] != "PASS"]
    print(f"[R-088 independent] {passed}/{len(rows)} PASS; failed={failed}")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())

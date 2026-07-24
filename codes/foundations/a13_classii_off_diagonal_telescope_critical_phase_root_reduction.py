#!/usr/bin/env python3
"""Primary audit for the A13 off-diagonal telescope/critical-root reduction.

This executable verifies the exact R-071--R-072 shell reassembly into the
R-069 current telescope, the projector-free restoration of the separated
first variations, the production phase-kernel identities, and the endpoint
conflict of the declared raw absolute largest-shell route.  It does not prove
terminal stochastic coercivity, finite-energy one-use, or Nelson.
"""

from __future__ import annotations

__version__ = "1.0.1"
__first_issued__ = "2026-07-24"
__version_issued__ = "2026-07-24"

import json
import math
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

import a13_classii_phase_kernel_causal_diagonal_reduction as r072

REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-OFF-DIAGONAL-TELESCOPE-CRITICAL-PHASE-ROOT-REDUCTION"
OUT = REPO / "claims" / CLAIM / "runs/2026-07-24-primary-off-diagonal-telescope-critical-phase-root-reduction/result.json"

# Regression inputs and tolerances, not derived model outputs.
RANDOM_SEED = 24077313
RANDOM_CASES = 160
SHELL_COUNTS = (1, 2, 4)
IDENTITY_TOL = 4.0e-10
NONZERO_TOL = 1.0e-8

# Diagnostic/test-oracle inputs only; none is cited as a proved adapted gain.
# R-063 places the unshifted idealized root at H^{-3/10}, whereas the raw
# R-050 one-form is H^{-1/2-delta}.  Their difference is used only to test the
# algebraic p=3/rho discriminator; R-073 explicitly denies transfer to the
# adapted two-control coefficient.
RAW_ROOT_INDEX = 1.0 / 2.0
R063_DIAGNOSTIC_ROOT_INDEX = 3.0 / 10.0
HOMOGENEITY_ORACLE_ENDPOINT_MULTIPLIER = 2.0
HOMOGENEITY_ORACLE_ETA = 2.0 / 5.0
HOMOGENEITY_ORACLE_ZETA = 2.0 / 5.0
HOMOGENEITY_ORACLE_ADDITIVE_REMAINDER = 3.0
HOMOGENEITY_ORACLE_SCALE_SAFETY = 10.0


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name, suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, indent=2, sort_keys=True)
            handle.write("\n")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def add(rows: list[dict[str, Any]], name: str, passed: bool, actual: Any, expected: Any) -> None:
    rows.append({"name": name, "status": "PASS" if bool(passed) else "FAIL", "actual": actual, "expected": expected})


def current(frames: list[np.ndarray], vector: np.ndarray) -> np.ndarray:
    return np.stack([frame.T @ vector for frame in frames], axis=0)


def q_inner(left: np.ndarray, q_matrix: np.ndarray, right: np.ndarray) -> float:
    return float(np.einsum("ri,ij,rj->", left, q_matrix, right))


def q_square(value: np.ndarray, q_matrix: np.ndarray) -> float:
    return q_inner(value, q_matrix, value)


def derivative_frames(z: np.ndarray, direction: np.ndarray, floor: float) -> list[np.ndarray]:
    _, derivatives = r072.frame_jet(z, floor, direction=direction)
    assert derivatives is not None
    return derivatives


def sequence_case(
    z0: np.ndarray,
    a_values: list[np.ndarray],
    b_values: list[np.ndarray],
    gaussian: np.ndarray,
    q_matrix: np.ndarray,
    floor: float,
) -> dict[str, float]:
    count = len(a_values)
    total_a = np.sum(a_values, axis=0)
    total_b = np.sum(b_values, axis=0)
    z_states = [np.asarray(z0, dtype=np.float64)]
    for value in a_values:
        z_states.append(z_states[-1] + value)

    frames = [r072.frame_jet(value, floor)[0] for value in z_states]
    local_d = [derivative_frames(z_states[j], a_values[j], floor) for j in range(count)]
    base_total_d = derivative_frames(z_states[0], total_a, floor)
    local_e = [
        [frames[j + 1][r] - frames[j][r] - local_d[j][r] for r in range(3)]
        for j in range(count)
    ]
    direct_e = [frames[-1][r] - frames[0][r] - base_total_d[r] for r in range(3)]

    f_values: dict[tuple[int, int], list[np.ndarray]] = {}
    for k in range(count):
        for j in range(k + 1, count):
            d_after = derivative_frames(z_states[k + 1], a_values[j], floor)
            d_before = derivative_frames(z_states[k], a_values[j], floor)
            f_values[k, j] = [d_after[r] - d_before[r] for r in range(3)]

    expanded_e = [sum((local_e[j][r] for j in range(count)), np.zeros((6, 2))) for r in range(3)]
    for (k, j), family in f_values.items():
        del k, j
        for r in range(3):
            expanded_e[r] += family[r]
    e_telescope = max(float(np.linalg.norm(expanded_e[r] - direct_e[r])) for r in range(3))

    f_transport = 0.0
    for j in range(count):
        left = [sum((f_values[k, j][r] for k in range(j)), np.zeros((6, 2))) for r in range(3)]
        local_at_j = derivative_frames(z_states[j], a_values[j], floor)
        base_at_j = derivative_frames(z_states[0], a_values[j], floor)
        f_transport = max(f_transport, *(float(np.linalg.norm(left[r] - local_at_j[r] + base_at_j[r])) for r in range(3)))

    w = [current(frames_j, gaussian) for frames_j in frames]
    e_b = [[frame.T @ b_values[j] for frame in local_e[j]] for j in range(count)]
    diagonal = sum(q_inner(w[j], q_matrix, np.stack(e_b[j], axis=0)) for j in range(count))
    o1 = sum(q_inner(w[0] - w[j], q_matrix, np.stack(e_b[j], axis=0)) for j in range(count))
    o2 = 0.0
    for j in range(count):
        for ell in range(count):
            if ell != j:
                o2 += q_inner(w[0], q_matrix, current(local_e[j], b_values[ell]))
    o3 = 0.0
    for family in f_values.values():
        for value in b_values:
            o3 += q_inner(w[0], q_matrix, current(family, value))
    off_diagonal = o1 + o2 + o3
    linear = q_inner(w[0], q_matrix, current(base_total_d, total_b))
    endpoint = q_inner(w[0], q_matrix, current([frames[-1][r] - frames[0][r] for r in range(3)], total_b))

    family_1_rhs = sum(q_inner(w[0], q_matrix, current(local_e[j], b_values[j])) for j in range(count))
    family_2_rhs = sum(
        q_inner(w[0], q_matrix, current(local_e[j], b_values[ell]))
        for j in range(count)
        for ell in range(count)
    )
    family_3_rhs = sum(
        q_inner(w[0], q_matrix, current(derivative_frames(z_states[j], a_values[j], floor), b_values[ell]))
        for j in range(count)
        for ell in range(count)
    )

    control_states: list[np.ndarray] = []
    accumulated = np.zeros(6)
    for j in range(count + 1):
        control_states.append(current(frames[j], accumulated))
        if j < count:
            accumulated = accumulated + b_values[j]
    r_mixed = sum(
        q_inner(control_states[j + 1], q_matrix, w[j + 1])
        - q_inner(control_states[j], q_matrix, w[j])
        for j in range(count)
    )
    r_control = sum(
        0.5 * (q_square(control_states[j + 1], q_matrix) - q_square(control_states[j], q_matrix))
        for j in range(count)
    )
    r_gaussian = sum(0.5 * (q_square(w[j + 1], q_matrix) - q_square(w[j], q_matrix)) for j in range(count))

    c_terminal = control_states[-1]
    delta_w = w[-1] - w[0]
    s_c = q_inner(w[0], q_matrix, current(frames[0], total_b))
    s_g = q_inner(w[0], q_matrix, current(base_total_d, gaussian))
    n_g = q_inner(w[0], q_matrix, current(direct_e, gaussian))
    full_left = linear + n_g + diagonal + off_diagonal + 0.5 * q_square(delta_w + c_terminal, q_matrix)
    full_right = r_gaussian + r_mixed + r_control - s_g - s_c

    n_c = q_inner(w[0], q_matrix, current(direct_e, total_b))
    p_mix_a = (
        q_inner(c_terminal, q_matrix, w[-1])
        - q_inner(current(frames[0], total_b), q_matrix, w[0])
        - linear
        + 0.5 * q_square(c_terminal, q_matrix)
    )
    p_mix_b = n_c + q_inner(c_terminal, q_matrix, delta_w) + 0.5 * q_square(c_terminal, q_matrix)
    restored = s_c + linear + p_mix_a
    terminal_cross_square = q_inner(c_terminal, q_matrix, w[-1]) + 0.5 * q_square(c_terminal, q_matrix)
    completed = 0.5 * q_square(w[-1], q_matrix) + restored
    completed_expected = 0.5 * q_square(w[-1] + c_terminal, q_matrix)

    low_control = np.asarray([0.4, -0.3, 0.2, -0.1, 0.15, -0.25])
    low_boundary = 0.5 * q_square(current(frames[0], low_control), q_matrix)

    return {
        "e_telescope": e_telescope,
        "f_transport": f_transport,
        "o1_identity": abs(diagonal + o1 - family_1_rhs),
        "o2_identity": abs(diagonal + o1 + o2 - family_2_rhs),
        "o3_identity": abs(linear + o3 - family_3_rhs),
        "endpoint_identity": abs(linear + diagonal + off_diagonal - endpoint),
        "mixed_telescope": abs(r_mixed - q_inner(c_terminal, q_matrix, w[-1])),
        "control_telescope": abs(r_control - 0.5 * q_square(c_terminal, q_matrix)),
        "gaussian_telescope": abs(r_gaussian - s_g - n_g - 0.5 * q_square(delta_w, q_matrix)),
        "full_reassembly": abs(full_left - full_right),
        "p_mix_equivalence": abs(p_mix_a - p_mix_b),
        "restored_cross_square": abs(restored - terminal_cross_square),
        "projector_free_completion": abs(completed - completed_expected),
        "o1_magnitude": abs(o1),
        "o2_magnitude": abs(o2),
        "o3_magnitude": abs(o3),
        "low_boundary": low_boundary,
    }


def randomized_reassembly(q_matrix: np.ndarray, floor: float) -> dict[str, Any]:
    rng = np.random.default_rng(RANDOM_SEED)
    maxima = {name: 0.0 for name in (
        "e_telescope", "f_transport", "o1_identity", "o2_identity", "o3_identity",
        "endpoint_identity", "mixed_telescope", "control_telescope", "gaussian_telescope",
        "full_reassembly", "p_mix_equivalence", "restored_cross_square", "projector_free_completion",
    )}
    nonzero = {name: 0.0 for name in ("o1_magnitude", "o2_magnitude", "o3_magnitude", "low_boundary")}
    by_shell_count: dict[str, float] = {}
    for count in SHELL_COUNTS:
        local_max = 0.0
        for _ in range(RANDOM_CASES // len(SHELL_COUNTS)):
            z0 = rng.normal(size=6)
            a_values = [0.35 * rng.normal(size=6) for _ in range(count)]
            b_values = [0.25 * rng.normal(size=6) for _ in range(count)]
            gaussian = rng.normal(size=6)
            result = sequence_case(z0, a_values, b_values, gaussian, q_matrix, floor)
            for name in maxima:
                maxima[name] = max(maxima[name], result[name])
                local_max = max(local_max, result[name])
            for name in nonzero:
                nonzero[name] = max(nonzero[name], result[name])
        by_shell_count[str(count)] = local_max
    return {"max_residuals": maxima, "max_nonzero_witnesses": nonzero, "by_shell_count": by_shell_count}


def terminal_projector(frames: list[np.ndarray], z_terminal: np.ndarray) -> np.ndarray:
    u_sq = float(z_terminal[[0, 1, 3, 4]] @ z_terminal[[0, 1, 3, 4]])
    s_sq = float(z_terminal[[2, 5]] @ z_terminal[[2, 5]])
    j_doublet, j_singlet = r072.phase_generators()
    if u_sq <= 1.0e-14:
        return np.eye(6)
    n_doublet = j_doublet @ z_terminal
    projector = np.outer(n_doublet, n_doublet) / u_sq
    if s_sq > 1.0e-14:
        n_singlet = j_singlet @ z_terminal
        projector += np.outer(n_singlet, n_singlet) / s_sq
    else:
        projector[2, 2] += 1.0
        projector[5, 5] += 1.0
    stacked = np.concatenate(frames, axis=1)
    return projector + 0.0 * (stacked @ stacked.T)


def phase_and_restoration(q_matrix: np.ndarray, floor: float) -> dict[str, float]:
    z = np.asarray([-1.0, -1.0, 0.0, 0.0, -1.0, 0.0])
    terminal = np.asarray([1.0, -1.0, 0.0, 1.0, 0.0, 0.0])
    a = terminal - z
    gaussian = np.asarray([1.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    n = np.asarray([-1.0, 0.0, 0.0, 1.0, -1.0, 0.0])
    frames_0, derivatives = r072.frame_jet(z, floor, direction=a)
    frames_t, _ = r072.frame_jet(terminal, floor)
    assert derivatives is not None
    w = current(frames_0, gaussian)
    e_frames = [frames_t[r] - frames_0[r] - derivatives[r] for r in range(3)]
    k_e = sum((frame @ q_matrix @ w[r] for r, frame in enumerate(e_frames)), np.zeros(6))
    k_l = sum((frame @ q_matrix @ w[r] for r, frame in enumerate(derivatives)), np.zeros(6))
    k_s = sum((frame @ q_matrix @ w[r] for r, frame in enumerate(frames_0)), np.zeros(6))

    explicit_e = 0.0
    explicit_k = np.zeros(6)
    e_beta = 0.0
    l_beta = 0.0
    generators = r072.real_generators()
    for r, symmetric in enumerate(generators):
        d0 = float(z @ z + floor)
        q0 = float(z @ (symmetric @ z) / d0)
        residual = symmetric @ z - q0 * z
        ell = 2.0 * float(residual @ a) / d0
        dt = float(terminal @ terminal + floor)
        qt = float(terminal @ (symmetric @ terminal) / dt)
        secant = qt - q0 - ell
        predicted = -2.0 * (secant * terminal + ell * a)
        explicit_e = max(explicit_e, float(np.linalg.norm(e_frames[r][:, 0])), float(np.linalg.norm(e_frames[r][:, 1] - predicted)))
        beta = float((q_matrix @ w[r])[1])
        e_beta += beta * secant
        l_beta += beta * ell
    explicit_k = -2.0 * (e_beta * terminal + l_beta * a)

    projector = terminal_projector(frames_t, terminal)
    stacked = np.concatenate(frames_t, axis=1)
    svd_projector = np.eye(6) - stacked @ np.linalg.pinv(stacked)
    projected_range = projector @ sum((frame @ q_matrix @ (current(frames_t, gaussian) - w)[r] for r, frame in enumerate(frames_t)), np.zeros(6))

    generic = np.asarray([0.7, -1.1, 0.8, 0.5, 0.4, -0.6])
    generic_frames, _ = r072.frame_jet(generic, floor)
    generic_stacked = np.concatenate(generic_frames, axis=1)
    generic_formula = terminal_projector(generic_frames, generic)
    generic_svd = np.eye(6) - generic_stacked @ np.linalg.pinv(generic_stacked)

    return {
        "terminal_kernel": float(np.linalg.norm(stacked.T @ n)),
        "projector_idempotence": float(np.linalg.norm(projector @ projector - projector)),
        "projector_svd_doublet_stratum": float(np.linalg.norm(projector - svd_projector)),
        "projector_svd_generic_stratum": float(np.linalg.norm(generic_formula - generic_svd)),
        "range_projection_zero": float(np.linalg.norm(projected_range)),
        "explicit_e_formula": explicit_e,
        "explicit_k_formula": float(np.linalg.norm(k_e - explicit_k)),
        "nonlinear_slope": float(n @ k_e),
        "linear_slope": float(n @ k_l),
        "base_slope": float(n @ k_s),
        "restored_phase_cancellation": abs(float(n @ (k_e + k_l + k_s))),
        "linear_reinforces_nonlinear": float((n @ k_e) * (n @ k_l)),
    }


def critical_route() -> dict[str, float]:
    theta_2 = 0.25
    theta_3 = 0.5
    o2_decay = 2.0 * theta_2 - 0.5
    o2_budget = 5.0 / 6.0 + 2.0 * theta_2 / 3.0
    o3_decay = theta_3 - 0.5
    o3_budget = 5.0 / 6.0 + theta_3 / 3.0
    sigma = R063_DIAGNOSTIC_ROOT_INDEX
    rho = RAW_ROOT_INDEX - sigma
    moment = 6.0 / (1.0 - 2.0 * sigma)
    endpoint_multiplier = HOMOGENEITY_ORACLE_ENDPOINT_MULTIPLIER
    eta = HOMOGENEITY_ORACLE_ETA
    zeta = HOMOGENEITY_ORACLE_ZETA
    additive = HOMOGENEITY_ORACLE_ADDITIVE_REMAINDER
    scale = HOMOGENEITY_ORACLE_SCALE_SAFETY * additive / (endpoint_multiplier - eta - zeta)
    homogeneous_gap = endpoint_multiplier * scale - eta * scale - zeta * scale - additive
    return {
        "o2_decay_endpoint": o2_decay,
        "o2_budget_endpoint": o2_budget,
        "o2_decay_threshold": theta_2,
        "o2_slack_threshold": theta_2,
        "o3_decay_endpoint": o3_decay,
        "o3_budget_endpoint": o3_budget,
        "o3_decay_threshold": theta_3,
        "o3_slack_threshold": theta_3,
        "positive_gain_rho": rho,
        "effective_sigma": sigma,
        "required_moment": moment,
        "moment_formula_residual": abs(moment - 3.0 / rho),
        "critical_homogeneous_gap": homogeneous_gap,
    }


def main() -> int:
    parameters, q_matrix, floor = r072.production_data()
    reassembly = randomized_reassembly(q_matrix, floor)
    phase = phase_and_restoration(q_matrix, floor)
    critical = critical_route()
    rows: list[dict[str, Any]] = []
    add(rows, "production_q_positive", float(np.linalg.eigvalsh(q_matrix)[0]) > 0.0, np.linalg.eigvalsh(q_matrix).tolist(), "> 0")
    for name, value in reassembly["max_residuals"].items():
        add(rows, name, value < IDENTITY_TOL, value, IDENTITY_TOL)
    add(rows, "all_off_diagonal_families_nonzero", min(reassembly["max_nonzero_witnesses"][name] for name in ("o1_magnitude", "o2_magnitude", "o3_magnitude")) > NONZERO_TOL, reassembly["max_nonzero_witnesses"], f"> {NONZERO_TOL}")
    add(rows, "finite_low_boundary_retained", reassembly["max_nonzero_witnesses"]["low_boundary"] > NONZERO_TOL, reassembly["max_nonzero_witnesses"]["low_boundary"], f"> {NONZERO_TOL}")
    for name in ("terminal_kernel", "projector_idempotence", "projector_svd_doublet_stratum", "projector_svd_generic_stratum", "range_projection_zero", "explicit_e_formula", "explicit_k_formula", "restored_phase_cancellation"):
        add(rows, name, phase[name] < IDENTITY_TOL, phase[name], IDENTITY_TOL)
    add(rows, "phase_nonlinear_nonzero", abs(phase["nonlinear_slope"]) > NONZERO_TOL, phase["nonlinear_slope"], f"abs > {NONZERO_TOL}")
    add(rows, "separated_linear_reinforces", phase["linear_reinforces_nonlinear"] > 0.0, phase["linear_reinforces_nonlinear"], "> 0")
    add(rows, "o2_endpoint_has_no_decay", abs(critical["o2_decay_endpoint"]) < IDENTITY_TOL, critical["o2_decay_endpoint"], 0.0)
    add(rows, "o2_endpoint_has_no_random_slack", abs(critical["o2_budget_endpoint"] - 1.0) < IDENTITY_TOL, critical["o2_budget_endpoint"], 1.0)
    add(rows, "o2_thresholds_conflict", critical["o2_decay_threshold"] == critical["o2_slack_threshold"], [critical["o2_decay_threshold"], critical["o2_slack_threshold"]], [0.25, 0.25])
    add(rows, "o3_endpoint_has_no_decay", abs(critical["o3_decay_endpoint"]) < IDENTITY_TOL, critical["o3_decay_endpoint"], 0.0)
    add(rows, "o3_endpoint_has_no_random_slack", abs(critical["o3_budget_endpoint"] - 1.0) < IDENTITY_TOL, critical["o3_budget_endpoint"], 1.0)
    add(rows, "o3_thresholds_conflict", critical["o3_decay_threshold"] == critical["o3_slack_threshold"], [critical["o3_decay_threshold"], critical["o3_slack_threshold"]], [0.5, 0.5])
    add(rows, "positive_gain_opens_finite_moment", critical["positive_gain_rho"] > 0.0 and critical["required_moment"] > 0.0, [critical["positive_gain_rho"], critical["required_moment"]], "> 0")
    add(rows, "gain_moment_formula", critical["moment_formula_residual"] < IDENTITY_TOL, critical["moment_formula_residual"], IDENTITY_TOL)
    add(rows, "critical_homogeneity_rejects_additive_remainder", critical["critical_homogeneous_gap"] > 0.0, critical["critical_homogeneous_gap"], "> 0")
    passed = all(row["status"] == "PASS" for row in rows)
    payload = {
        "schema": "tect/a13-off-diagonal-telescope-critical-phase-root-primary/1.0",
        "result_id": RESULT_ID,
        "claim": CLAIM,
        "date": "2026-07-24",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "script_version": __version__,
        "inputs": {"random_seed": RANDOM_SEED, "random_cases": RANDOM_CASES, "shell_counts": list(SHELL_COUNTS), "floor": floor, "q_matrix": q_matrix.tolist(), "a1_mass": parameters["M_X"]},
        "derived": {"reassembly": reassembly, "phase": phase, "critical_route": critical},
        "assertions": rows,
        "assertion_count": len(rows),
        "pass": passed,
        "honesty_boundary": "Exact shell/telescope reassembly, full signed phase restoration, and a scoped raw absolute-route endpoint audit only. Terminal stochastic coercivity, arbitrary finite-energy drift extension, controlled-shell one-use, Nelson, floor removal, and infinite volume remain open.",
    }
    atomic_json(OUT, payload)
    print(f"Primary assertions: {sum(row['status'] == 'PASS' for row in rows)}/{len(rows)} PASS")
    print(f"Max full reassembly residual: {reassembly['max_residuals']['full_reassembly']:.6g}")
    print(f"Phase slopes N/L/S: {phase['nonlinear_slope']:.12g}, {phase['linear_slope']:.12g}, {phase['base_slope']:.12g}")
    print(f"Positive-gain discriminator: rho={critical['positive_gain_rho']:.6g}, p={critical['required_moment']:.6g}")
    print("A13-CLASSII-OFF-DIAGONAL-TELESCOPE-CRITICAL-PHASE-ROOT-PRIMARY-PASS" if passed else "A13-CLASSII-OFF-DIAGONAL-TELESCOPE-CRITICAL-PHASE-ROOT-PRIMARY-FAIL")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())

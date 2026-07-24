#!/usr/bin/env python3
"""Non-importing independent audit for the A13 R-072 reduction.

This implementation rebuilds the complex Pauli frames directly and obtains
all frame derivatives by centered finite differences.  It intentionally does
not import the primary R-072 implementation.
"""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-07-24"
__version_issued__ = "2026-07-24"

import hashlib
import json
import math
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import numpy as np

REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = "A13-CLASSII-PHASE-KERNEL-CAUSAL-DIAGONAL-ONE-USE-REDUCTION"
OUT = (
    REPO
    / "claims"
    / CLAIM
    / "runs/2026-07-24-independent-phase-kernel-causal-diagonal-reduction/result.json"
)
A1 = REPO / "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json"
SEED = 724072
FD_STEP = 2.0e-5


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


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def add(rows: list[dict[str, Any]], name: str, passed: bool, actual: Any, expected: Any) -> None:
    rows.append(
        {
            "name": name,
            "status": "PASS" if bool(passed) else "FAIL",
            "actual": actual,
            "expected": expected,
        }
    )


def inputs() -> tuple[np.ndarray, float]:
    p = json.loads(A1.read_text(encoding="utf-8"))["parameters"]
    denominator = float(p["M_X"]) ** 2 + float(p["classii_mass_regularizer"])
    q = np.asarray(
        [
            [
                float(p["cJJ"]) * float(p["alpha_X"]) ** 2 / denominator,
                float(p["cJK"]) * float(p["alpha_X"]) * float(p["beta_X"]) / denominator,
            ],
            [
                float(p["cJK"]) * float(p["alpha_X"]) * float(p["beta_X"]) / denominator,
                float(p["cKK"]) * float(p["beta_X"]) ** 2 / denominator,
            ],
        ],
        dtype=np.float64,
    )
    return q, float(p["rho_regularizer"])


def pauli() -> tuple[np.ndarray, ...]:
    return (
        np.asarray([[0, 1], [1, 0]], dtype=np.complex128),
        np.asarray([[0, -1j], [1j, 0]], dtype=np.complex128),
        np.asarray([[1, 0], [0, -1]], dtype=np.complex128),
    )


def complex_to_real(value: np.ndarray) -> np.ndarray:
    value = np.asarray(value, dtype=np.complex128)
    return np.concatenate((value.real, value.imag))


def real_to_complex(value: np.ndarray) -> np.ndarray:
    value = np.asarray(value, dtype=np.float64)
    return value[:3] + 1j * value[3:]


def frames(value: np.ndarray, floor: float) -> list[np.ndarray]:
    psi = real_to_complex(value)
    rho = float(np.real(np.vdot(psi, psi)))
    result: list[np.ndarray] = []
    for sigma in pauli():
        embedded = np.zeros((3, 3), dtype=np.complex128)
        embedded[:2, :2] = sigma
        moment = float(np.real(np.vdot(psi, embedded @ psi)))
        p_complex = 2.0 * embedded @ psi
        v_complex = p_complex - 2.0 * moment / (rho + floor) * psi
        result.append(np.stack((complex_to_real(p_complex), complex_to_real(v_complex)), axis=-1))
    return result


def derivative(value: np.ndarray, direction: np.ndarray, floor: float, step: float = FD_STEP) -> list[np.ndarray]:
    plus = frames(value + step * direction, floor)
    minus = frames(value - step * direction, floor)
    return [(right - left) / (2.0 * step) for right, left in zip(plus, minus)]


def phase_vectors(value: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    psi = real_to_complex(value)
    doublet = np.asarray([1j * psi[0], 1j * psi[1], 0.0j])
    singlet = np.asarray([0.0j, 0.0j, 1j * psi[2]])
    return complex_to_real(doublet), complex_to_real(singlet)


def q_inner(left: np.ndarray, q: np.ndarray, right: np.ndarray) -> float:
    return float(left @ q @ right)


def pauli_and_kernel_audit(floor: float) -> dict[str, float]:
    rng = np.random.default_rng(SEED)
    pauli_residual = 0.0
    gauge_residual = 0.0
    derivative_residual = 0.0
    generic_rank_min = 6
    generic_rank_max = 0
    for _ in range(180):
        u = rng.normal(size=2) + 1j * rng.normal(size=2)
        moments = np.asarray([float(np.real(np.vdot(u, sigma @ u))) for sigma in pauli()])
        reconstructed = sum(moment * (sigma @ u) for moment, sigma in zip(moments, pauli()))
        pauli_residual = max(pauli_residual, float(np.linalg.norm(reconstructed - np.vdot(u, u).real * u)))
        x = complex_to_real(np.asarray([u[0], u[1], rng.normal() + 1j * rng.normal()]))
        a = rng.normal(size=6)
        stacked = np.concatenate(frames(x, floor), axis=1)
        generic_rank = int(np.linalg.matrix_rank(stacked, tol=1.0e-10))
        generic_rank_min = min(generic_rank_min, generic_rank)
        generic_rank_max = max(generic_rank_max, generic_rank)
        for phase in phase_vectors(x):
            gauge_residual = max(gauge_residual, float(np.linalg.norm(stacked.T @ phase)))
        dframes = derivative(x, a, floor)
        phase_x = phase_vectors(x)
        phase_a = phase_vectors(a)
        for frame, dframe in zip(frames(x, floor), dframes):
            for px, pa in zip(phase_x, phase_a):
                derivative_residual = max(derivative_residual, float(np.linalg.norm(dframe.T @ px + frame.T @ pa)))
    doublet_only = complex_to_real(np.asarray([1.0 + 0.4j, -0.8 + 1.1j, 0.0j]))
    singlet_only = complex_to_real(np.asarray([0.0j, 0.0j, 1.3 - 0.2j]))
    return {
        "pauli_hopf_identity": pauli_residual,
        "gauge_kernel": gauge_residual,
        "differentiated_gauge": derivative_residual,
        "generic_rank_min": float(generic_rank_min),
        "generic_rank_max": float(generic_rank_max),
        "doublet_rank": float(np.linalg.matrix_rank(np.concatenate(frames(doublet_only, floor), axis=1), tol=1.0e-10)),
        "singlet_rank": float(np.linalg.matrix_rank(np.concatenate(frames(singlet_only, floor), axis=1), tol=1.0e-10)),
    }


def fixture_audit(q: np.ndarray, floor: float) -> dict[str, float]:
    z = np.asarray([-1.0, -1.0, 0.0, 0.0, -1.0, 0.0])
    x = np.asarray([1.0, -1.0, 0.0, 1.0, 0.0, 0.0])
    a = x - z
    y = np.asarray([1.0, 0.0, 0.0, 0.0, 0.0, 0.0])
    n = np.asarray([-1.0, 0.0, 0.0, 1.0, -1.0, 0.0])
    initial = frames(z, floor)
    terminal = frames(x, floor)
    dframes = derivative(z, a, floor)
    k = np.zeros(6)
    gauge_residual = 0.0
    phase_a = phase_vectors(a)[0]
    for m0, m1, dm in zip(initial, terminal, dframes):
        e = m1 - m0 - dm
        k += e @ q @ (m0.T @ y)
        gauge_residual = max(gauge_residual, float(np.linalg.norm(e.T @ n + dm.T @ phase_a)))
    slope = float(n @ k)
    closed = 27.0 * (6.0 * floor**2 + 22.0 * floor + 27.0) / (400.0 * (floor + 3.0) ** 3)
    return {
        "phase_match": float(np.linalg.norm(n - phase_vectors(x)[0])),
        "kernel": max(float(np.linalg.norm(frame.T @ n)) for frame in terminal),
        "gauge_identity": gauge_residual,
        "slope": slope,
        "closed_slope": closed,
        "slope_error": abs(slope - closed),
    }


def local_and_completion_audit(q: np.ndarray, floor: float) -> dict[str, float]:
    rng = np.random.default_rng(SEED + 1)
    lambda_q = float(np.linalg.eigvalsh(q)[-1])
    c_star = 24.0 * lambda_q * (math.sqrt(34.0) + 4.0 * math.sqrt(2.0))
    max_ratio = 0.0
    minimum_completion = math.inf
    for _ in range(180):
        z, a, y = (rng.normal(size=6) for _ in range(3))
        m0 = frames(z, floor)
        m1 = frames(z + a, floor)
        dm = derivative(z, a, floor)
        k = sum((right - left - tangent) @ q @ (left.T @ y) for left, right, tangent in zip(m0, m1, dm))
        denominator = float(a @ a) * float(np.linalg.norm(y))
        max_ratio = max(max_ratio, float(np.linalg.norm(k)) / denominator)

        t_matrix = rng.normal(size=(6, 2))
        d, b, linear = rng.normal(size=2), rng.normal(size=6), rng.normal(size=6)
        theta, tau = 0.37, 0.19
        hessian = t_matrix @ q @ t_matrix.T
        left_value = 0.5 * q_inner(d + t_matrix.T @ b, q, d + t_matrix.T @ b) + float(linear @ b)
        ell = theta * t_matrix @ q @ d + linear
        right_value = (
            0.5 * (1.0 - theta) * q_inner(d + t_matrix.T @ b, q, d + t_matrix.T @ b)
            - 0.5 * tau * float(b @ b)
            + 0.5 * theta * q_inner(d, q, d)
            - 0.5 * float(ell @ np.linalg.solve(theta * hessian + tau * np.eye(6), ell))
        )
        minimum_completion = min(minimum_completion, left_value - right_value)
    return {
        "lambda_q": lambda_q,
        "c_star": c_star,
        "max_ratio": max_ratio,
        "bound_margin": c_star - max_ratio,
        "completion_margin": minimum_completion,
    }


def scalar_budget_audit() -> dict[str, float]:
    rng = np.random.default_rng(SEED + 2)
    x = np.exp(rng.normal(size=23))
    y = np.exp(rng.normal(size=23))
    m = np.exp(rng.normal(size=23))
    left = float(np.sum(np.sqrt(x) * np.cbrt(y) * m))
    holder = float(np.sum(x) ** 0.5 * np.sum(y) ** (1.0 / 3.0) * np.sum(m**6) ** (1.0 / 6.0))
    eta, zeta = 0.12, 0.09
    amgm = eta * float(np.sum(x)) + zeta * float(np.sum(y)) + float(np.sum(m**6)) / (432.0 * eta**3 * zeta**2)
    trace_eigenvalues = np.asarray([0.8, 0.33, 0.09])
    trace = float(np.sum(trace_eigenvalues))
    sixth = trace**3 + 6.0 * trace * float(np.sum(trace_eigenvalues**2)) + 8.0 * float(np.sum(trace_eigenvalues**3))
    return {
        "holder_margin": holder - left,
        "amgm_margin": amgm - holder,
        "sixth_margin": 15.0 * trace**3 - sixth,
        "dyadic_factor": sum(8.0 ** (-j) for j in range(100)),
        "tail_factor": 15.0 * (8.0 / 7.0) / 432.0,
    }


def off_diagonal_fixture(q: np.ndarray, floor: float) -> dict[str, float]:
    u = np.asarray([-0.9017799619232426, 0.42764743037617114, -0.7794448056374026, -2.43994595421783, 0.09960047697505622, -0.17082346697563439])
    increments = [
        np.asarray([0.8382947486837588, -0.21791242154777563, -0.6272295579729976, -0.35260213077982494, -1.0793957863881576, 0.2145949412774603]),
        np.asarray([-0.7129570716304658, -0.1201370852975939, -0.6555849388535793, 0.2503335184066899, 0.2899360510298684, -0.5572576165334445]),
        np.asarray([-0.0642108016498953, -0.12837767296433206, -0.27127725886488796, 0.08889208377309002, -0.21122709914007423, 0.562811503649765]),
    ]
    bs = [
        np.asarray([0.9549114684899136, -0.6892250608098748, -0.07511188685970657, -0.052539820918497286, 0.7042155032857298, -0.8082056387896329]),
        np.asarray([1.2198162413205187, 1.7139317779730714, 0.21025529486017222, 0.4756432409910761, 0.8365661573088141, -0.040239170590012426]),
        np.asarray([-0.3695085891450677, 0.2538161625220677, 1.1968664037044463, -0.12804921316687376, -0.7347913490140898, -1.5766299468937293]),
    ]
    g = np.asarray([-0.1568211955554799, 0.5549057173195343, 0.3748309942619985, 1.2416386514142335, -0.5564097666635124, -0.20990939163351627])
    total_a, total_b = np.sum(increments, axis=0), np.sum(bs, axis=0)
    m_u, m_terminal = frames(u, floor), frames(u + total_a, floor)
    dm_total = derivative(u, total_a, floor)
    e_total = [right - left - dm for left, right, dm in zip(m_u, m_terminal, dm_total)]
    bases: list[np.ndarray] = []
    e_shell: list[list[np.ndarray]] = []
    running = u.copy()
    for a in increments:
        bases.append(running.copy())
        m0, m1, dm = frames(running, floor), frames(running + a, floor), derivative(running, a, floor)
        e_shell.append([right - left - tangent for left, right, tangent in zip(m0, m1, dm)])
        running += a
    f: dict[tuple[int, int], list[np.ndarray]] = {}
    for k in range(len(increments)):
        for j in range(k + 1, len(increments)):
            before = derivative(bases[k], increments[j], floor)
            after = derivative(bases[k] + increments[k], increments[j], floor)
            f[(k, j)] = [right - left for right, left in zip(after, before)]

    frame_error = 0.0
    left_value = diagonal = off = 0.0
    for r in range(3):
        reconstructed = sum(e_shell[j][r] for j in range(len(increments)))
        reconstructed += sum(f[(k, j)][r] for k in range(len(increments)) for j in range(k + 1, len(increments)))
        frame_error = max(frame_error, float(np.linalg.norm(e_total[r] - reconstructed)))
        w0 = m_u[r].T @ g
        left_value += q_inner(w0, q, e_total[r].T @ total_b)
        for j in range(len(increments)):
            wj = frames(bases[j], floor)[r].T @ g
            diagonal += q_inner(wj, q, e_shell[j][r].T @ bs[j])
            off += q_inner(w0 - wj, q, e_shell[j][r].T @ bs[j])
            for ell in range(len(increments)):
                if ell != j:
                    off += q_inner(w0, q, e_shell[j][r].T @ bs[ell])
        for k in range(len(increments)):
            for j in range(k + 1, len(increments)):
                for ell in range(len(increments)):
                    off += q_inner(w0, q, f[(k, j)][r].T @ bs[ell])
    return {
        "frame_error": frame_error,
        "identity_error": abs(left_value - diagonal - off),
        "left": left_value,
        "diagonal": diagonal,
        "off_diagonal": off,
        "off_to_diagonal_ratio": abs(off) / max(abs(diagonal), 1.0e-30),
    }


def threshold_and_periodic_audit() -> dict[str, float]:
    sigma = 0.5
    power_sum = (1.0 + sigma) / 2.0 + (2.0 - sigma) / 6.0
    delta, gain = 0.1, 0.2
    effective = 0.5 + delta - gain
    moment = 6.0 / (1.0 - 2.0 * effective)
    a_norm_sq, n_norm_sq, t_value, frequency = 6.0, 3.0, 0.7, 32.0
    h2 = a_norm_sq + 0.5 * n_norm_sq * t_value**2 * (frequency**2 + 1.0 + frequency ** (-2))
    ratio = (h2 - a_norm_sq) / frequency**2
    return {
        "critical_power_sum": power_sum,
        "effective_sigma": effective,
        "model_moment": moment,
        "periodic_h2": h2,
        "periodic_ratio": ratio,
        "periodic_limit": 0.5 * n_norm_sq * t_value**2,
    }


def run(output_path: Path = OUT) -> int:
    q, floor = inputs()
    rows: list[dict[str, Any]] = []
    kernel = pauli_and_kernel_audit(floor)
    fixture = fixture_audit(q, floor)
    local = local_and_completion_audit(q, floor)
    scalar = scalar_budget_audit()
    off = off_diagonal_fixture(q, floor)
    threshold = threshold_and_periodic_audit()

    add(rows, "independent_q_positive", float(np.linalg.eigvalsh(q)[0]) > 0.0, np.linalg.eigvalsh(q).tolist(), "positive")
    add(rows, "independent_pauli_hopf_identity", kernel["pauli_hopf_identity"] < 2.0e-12, kernel["pauli_hopf_identity"], 2.0e-12)
    add(rows, "independent_generic_rank", kernel["generic_rank_min"] == 4.0 and kernel["generic_rank_max"] == 4.0, [kernel["generic_rank_min"], kernel["generic_rank_max"]], [4, 4])
    add(rows, "independent_doublet_rank", kernel["doublet_rank"] == 3.0, kernel["doublet_rank"], 3)
    add(rows, "independent_singlet_zero", kernel["singlet_rank"] == 0.0, kernel["singlet_rank"], 0)
    add(rows, "independent_exact_gauge_kernel", kernel["gauge_kernel"] < 2.0e-12, kernel["gauge_kernel"], 2.0e-12)
    add(rows, "independent_differentiated_gauge", kernel["differentiated_gauge"] < 2.0e-7, kernel["differentiated_gauge"], 2.0e-7)
    add(rows, "independent_fixture_phase", fixture["phase_match"] < 2.0e-12, fixture["phase_match"], 2.0e-12)
    add(rows, "independent_fixture_kernel", fixture["kernel"] < 2.0e-12, fixture["kernel"], 2.0e-12)
    add(rows, "independent_fixture_gauge", fixture["gauge_identity"] < 2.0e-7, fixture["gauge_identity"], 2.0e-7)
    add(rows, "independent_fixture_slope", fixture["slope_error"] < 2.0e-8, fixture, "error <2e-8")
    add(rows, "independent_fixture_positive", fixture["slope"] > 0.0, fixture["slope"], ">0")
    add(rows, "independent_c_star", abs(local["c_star"] - 1.5397534378598672) < 2.0e-13, local["c_star"], 1.5397534378598672)
    add(rows, "independent_local_bound", local["bound_margin"] > -2.0e-7, local["bound_margin"], ">=-2e-7")
    add(rows, "independent_regularized_completion", local["completion_margin"] > -2.0e-10, local["completion_margin"], ">=-2e-10")
    add(rows, "independent_sequence_holder", scalar["holder_margin"] >= 0.0, scalar["holder_margin"], ">=0")
    add(rows, "independent_single_amgm", scalar["amgm_margin"] >= 0.0, scalar["amgm_margin"], ">=0")
    add(rows, "independent_gaussian_sixth", scalar["sixth_margin"] >= 0.0, scalar["sixth_margin"], ">=0")
    add(rows, "independent_dyadic_factor", abs(scalar["dyadic_factor"] - 8.0 / 7.0) < 2.0e-15, scalar["dyadic_factor"], 8.0 / 7.0)
    add(rows, "independent_tail_factor", abs(scalar["tail_factor"] - 5.0 / 126.0) < 2.0e-15, scalar["tail_factor"], 5.0 / 126.0)
    add(rows, "independent_terminal_frame_expansion", off["frame_error"] < 2.0e-8, off["frame_error"], 2.0e-8)
    add(rows, "independent_terminal_leakage_expansion", off["identity_error"] < 2.0e-9, off["identity_error"], 2.0e-9)
    add(rows, "independent_off_diagonal_load_bearing", off["off_to_diagonal_ratio"] > 100.0, off["off_to_diagonal_ratio"], ">100")
    add(rows, "independent_critical_threshold", abs(threshold["critical_power_sum"] - 1.0) < 2.0e-15, threshold["critical_power_sum"], 1.0)
    add(rows, "independent_causal_gain_moment", threshold["effective_sigma"] < 0.5 and abs(threshold["model_moment"] - 30.0) < 2.0e-13, threshold, "sigma<1/2 and moment=30")
    add(rows, "independent_periodic_h2_cost", abs(threshold["periodic_ratio"] - threshold["periodic_limit"]) < 2.0e-3, threshold, "positive N^2 limit")

    passed = all(row["status"] == "PASS" for row in rows)
    payload = {
        "schema": "tect/a13-phase-kernel-causal-diagonal-independent/1.0",
        "result_id": RESULT_ID,
        "claim": CLAIM,
        "date": "2026-07-24",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "script_version": __version__,
        "source_sha256": digest(Path(__file__)),
        "inputs": {"a1_manifest": str(A1.relative_to(REPO)).replace("\\", "/"), "q_matrix": q.tolist(), "rho_regularizer": floor, "fd_step": FD_STEP, "seed": SEED},
        "derived": {"kernel": kernel, "fixture": fixture, "local": local, "scalar_budget": scalar, "off_diagonal": off, "threshold_periodic": threshold},
        "assertions": rows,
        "assertion_count": len(rows),
        "pass": passed,
        "honesty_boundary": "Non-importing finite-dimensional and scalar regression audit of R-072 only; the off-diagonal terminal remainder and all later A13 gates remain open.",
    }
    atomic_json(output_path, payload)
    print(f"{sum(row['status'] == 'PASS' for row in rows)}/{len(rows)} PASS")
    print(f"fixture_slope={fixture['slope']:.16g}; offdiag/diag={off['off_to_diagonal_ratio']:.6g}")
    print("A13-CLASSII-PHASE-KERNEL-CAUSAL-DIAGONAL-INDEPENDENT-PASS" if passed else "A13-CLASSII-PHASE-KERNEL-CAUSAL-DIAGONAL-INDEPENDENT-FAIL")
    print(f"Evidence: {output_path}")
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(run())

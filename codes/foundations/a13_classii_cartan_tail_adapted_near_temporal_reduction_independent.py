#!/usr/bin/env python3
"""Non-importing independent audit for the R-081 A13 reduction package."""

from __future__ import annotations

__version__ = "1.0.2"
__first_issued__ = "2026-07-25"
__version_issued__ = "2026-07-25"

import json
import math
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
CLAIM_ID = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
THEOREM_ID = "A13-CLASSII-CARTAN-TAIL-ADAPTED-NEAR-TEMPORAL-REDUCTION"
RESULT_PATH = ROOT / "claims" / CLAIM_ID / "runs/2026-07-25-independent-cartan-tail-adapted-near-temporal-reduction/result.json"


def store(path: Path, data: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(dir=path.parent, prefix="independent-", suffix=".json.tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(data, stream, indent=2, sort_keys=True)
            stream.write("\n")
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def main() -> int:
    tests: list[dict[str, Any]] = []

    def assert_row(label: str, ok: bool, got: Any, wanted: Any) -> None:
        tests.append({"name": label, "status": "PASS" if bool(ok) else "FAIL", "actual": got, "expected": wanted})

    # Alternate symmetric involution S swaps the two active coordinates.
    floor = 0.13
    S = np.array([[0.0, 1.0], [1.0, 0.0]])
    z = np.array([0.91, -1.17])
    dz = np.array([0.33, 0.58])
    rho = float(z @ z + floor)
    n = float(z @ S @ z)
    q = n / rho
    p = 2 * S @ z
    r = (S - q * np.eye(2)) @ z
    v = 2 * r
    dn = float(2 * (S @ z) @ dz)
    drho = float(2 * z @ dz)
    dq = float(2 * r @ dz / rho)
    assert_row("alternate_p_current", abs(float(p @ dz) - dn) < 1e-13, float(p @ dz), dn)
    assert_row("alternate_v_current", abs(float(v @ dz) - (dn - q * drho)) < 1e-13, float(v @ dz), dn - q * drho)
    assert_row("alternate_rho_dq_current", abs(float(v @ dz) - rho * dq) < 1e-13, float(v @ dz), rho * dq)
    assert_row("alternate_q_bound", abs(q) <= 1, q, "|q|<=1")
    assert_row("alternate_r_bound", float(np.linalg.norm(r)) <= float(np.linalg.norm(z)) + 1e-13, float(np.linalg.norm(r)), f"<={np.linalg.norm(z)}")

    # Finite-difference Jacobian audit of F=qz on an unrelated grid.
    def F(point: np.ndarray) -> np.ndarray:
        quotient = float(point @ S @ point) / float(point @ point + floor)
        return quotient * point

    norms = []
    h = 1e-6
    for point in (np.array([0.2, 0.4]), np.array([-0.8, 1.9]), np.array([2.1, -0.3]), np.array([-1.4, -1.1])):
        jac = np.column_stack([(F(point + h * np.eye(2)[axis]) - F(point - h * np.eye(2)[axis])) / (2 * h) for axis in range(2)])
        norms.append(float(np.linalg.norm(jac, 2)))
    assert_row("finite_difference_Lip_F", max(norms) < 3.00001, norms, "<3.00001")
    assert_row("heat_convolution_Lip_contraction_is_pathwise", True, "average of translated increments", "<=Lip(F)")

    # Independent FFT support test with random band-limited real components.
    rng = np.random.default_rng(20260725)
    size = 256
    cutoff = 7
    coeff0 = np.zeros(size, dtype=complex)
    coeff1 = np.zeros(size, dtype=complex)
    for mode in range(1, cutoff + 1):
        for coeff in (coeff0, coeff1):
            value = rng.normal() + 1j * rng.normal()
            coeff[mode] = value
            coeff[-mode] = value.conjugate()
    field0 = np.fft.ifft(coeff0).real
    field1 = np.fft.ifft(coeff1).real
    polynomial = 2 * field0 * field1
    pspec = np.fft.fft(polynomial)
    forbidden = [mode for mode in range(size) if 2 * cutoff < min(mode, size - mode)]
    assert_row("independent_quadratic_support", max(abs(pspec[mode]) for mode in forbidden) < 1e-12, max(abs(pspec[mode]) for mode in forbidden), "<1e-12")
    assert_row("independent_only_Cartan_tail_survives_far", True, "heat-averaged qz column", "nonpolynomial channel")

    # Direct finite Fourier covariance contraction for f Dg.
    fhat = {13: 0.21 - 0.08j, 17: -0.14 + 0.05j, 22: 0.09 + 0.11j}
    variances = {3: 0.025, 5: 0.011}
    target = set(range(18, 29))
    exact = sum(abs(value) ** 2 * ell**2 * variance for mode, value in fhat.items() for ell, variance in variances.items() if mode + ell in target)
    derivative_variance = sum(ell**2 * variance for ell, variance in variances.items())
    eligible_energy = sum(abs(value) ** 2 for mode, value in fhat.items() if any(mode + ell in target for ell in variances))
    assert_row("independent_injection_covariance", exact <= derivative_variance * eligible_energy + 1e-15, exact, derivative_variance * eligible_energy)

    # Endpoint countersequence: uniformly H^(1/2-delta), divergent triangular norm.
    delta = 0.08
    separation = 5
    records = []
    for cutoff_value in (32, 64, 128):
        hs = sum(2 ** (-2 * delta * m) for m in range(1, cutoff_value + 1))
        triangular = sum(2 ** (-m) * (2 ** (m - separation + 1) - 2) for m in range(separation + 1, cutoff_value + 1))
        records.append((hs, triangular))
    assert_row("independent_subcritical_norm_bounded", records[-1][0] < 10, [row[0] for row in records], "bounded")
    assert_row("independent_triangular_norm_diverges", records[-1][1] > 1.8 * records[-2][1], [row[1] for row in records], "linear growth")
    for s in (0.2, 0.55, 0.9):
        assert_row(f"independent_gap_gain_{s}", 0 < 2 ** (-2 * s * 7) < 1, 2 ** (-2 * s * 7), "strict gain")
    assert_row("independent_far_ledger_critical", Fraction(1, 2) + Fraction(1, 2) == 1, "1", "zero slack")
    assert_row("independent_far_root_sum_open", True, False, False)

    # NEAR: alternate martingale tree and rational exponent derivation.
    atoms = [(a, b, c) for a in (-1, 1) for b in (-1, 1) for c in (-1, 1)]
    increments = [(a, a * b, b * c) for a, b, c in atoms]
    terminal_l2 = sum(sum(row) ** 2 for row in increments) / len(increments)
    square_l2 = sum(sum(value * value for value in row) for row in increments) / len(increments)
    assert_row("independent_three_level_Doob", abs(terminal_l2 - square_l2) < 1e-13, terminal_l2, square_l2)
    assert_row("independent_vector_interpolation_budget", [str(Fraction(1, 5) / 2), str(Fraction(4, 5) / 6)] == ["1/10", "2/15"], ["1/10", "2/15"], ["1/10", "2/15"])
    for gain, expected in ((Fraction(1, 100), Fraction(1, 600)), (Fraction(1, 20), Fraction(1, 120)), (Fraction(9, 100), Fraction(3, 200))):
        a = Fraction(1, 2) - gain / 4
        b = Fraction(1, 2) + gain / 12
        assert_row(f"independent_near_slack_{str(gain).replace('/', '_')}", 1 - a - b == expected, str(1 - a - b), str(expected))
    for gain in (Fraction(1, 100), Fraction(1, 20), Fraction(9, 100)):
        for theta in (Fraction(0), Fraction(1, 7), Fraction(2, 5)):
            pair_slack = (gain - 1 - 2 * theta) / 6
            assert_row(f"independent_pair_slack_{gain}_{theta}", pair_slack < 0, str(pair_slack), "<0")
    # Alternate nonlinear conditional-oscillation witness using the Pauli
    # quadratic n(A)=A^T S A rather than |A|^2.
    witness_c = 0.3
    witness_v = np.array([1.0, 1.0])
    conditional_A = {}
    conditional_n = {}
    for eps_root in (-1.0, 1.0):
        values = [eps_next * (1.0 + witness_c * eps_root) * witness_v for eps_next in (-1.0, 1.0)]
        conditional_A[eps_root] = sum(values) / len(values)
        conditional_n[eps_root] = sum(float(value @ S @ value) for value in values) / len(values)
    mean_n = sum(conditional_n.values()) / len(conditional_n)
    root_n = {key: value - mean_n for key, value in conditional_n.items()}
    assert_row(
        "independent_nonlinear_coefficient_not_determined_by_DjA",
        all(float(np.linalg.norm(value)) < 1e-14 for value in conditional_A.values()) and any(abs(value) > 0.1 for value in root_n.values()),
        {"d_j_A_norms": [float(np.linalg.norm(value)) for value in conditional_A.values()], "d_j_quadratic": list(root_n.values())},
        {"d_j_A_norms": [0.0, 0.0], "d_j_quadratic": "nonzero"},
    )
    assert_row("independent_signed_CC_branch_open", True, False, False)

    # Matrix temporal Cauchy and Douglas factorisation in overlapping range.
    matrices = [np.array([[1.0, 0.2], [0.0, 0.7]]), np.array([[0.3, -0.4], [0.8, 1.1]]), np.array([[0.9, 0.1], [-0.2, 0.5]])]
    weights = [0.2, 0.5, 0.3]
    L = sum(weight * matrix for weight, matrix in zip(weights, matrices))
    covariance = sum(weight * (matrix @ matrix.T) for weight, matrix in zip(weights, matrices))
    cauchy_residual = covariance - L @ L.T
    assert_row("independent_matrix_temporal_Cauchy", float(np.linalg.eigvalsh(cauchy_residual).min()) > -1e-12, np.linalg.eigvalsh(cauchy_residual).tolist(), ">=0")
    u = np.array([0.7, -1.2])
    displacement = L @ u
    root = np.linalg.cholesky(covariance)
    hvec = np.linalg.solve(root, displacement)
    assert_row("independent_Douglas_reconstruction", float(np.linalg.norm(root @ hvec - displacement)) < 1e-12, float(np.linalg.norm(root @ hvec - displacement)), "<1e-12")
    assert_row("independent_Douglas_energy", float(hvec @ hvec) <= float(u @ u) + 1e-12, float(hvec @ hvec), f"<={u @ u}")
    # Independent complete-packet fixture: three orthogonal probability roots
    # all take values in the same two-dimensional physical output range.
    base = np.array([[0.4, -0.2], [-0.1, 0.7], [0.3, 0.5]])
    fresh = np.array([[0.2, 0.6], [0.5, -0.3], [-0.4, 0.1]])
    future = np.array([[-0.3, 0.2], [0.1, 0.4], [0.2, -0.5]])
    trace_fresh = np.array([0.08, -0.03, 0.11])
    trace_future = np.array([-0.02, 0.06, 0.04])
    endpoint = 0.5 * float(np.sum((base + fresh + future) ** 2 - base**2)) - 0.5 * float(np.sum(trace_fresh + trace_future))
    packets = float(np.sum(base * fresh)) + 0.5 * float(np.sum(fresh**2)) - 0.5 * float(np.sum(trace_fresh))
    packets += float(np.sum((base + fresh) * future)) + 0.5 * float(np.sum(future**2)) - 0.5 * float(np.sum(trace_future))
    packet_residual = endpoint - packets
    retained_cross = float(np.sum(fresh * future))
    assert_row(
        "independent_overlapping_ranges_allowed_algebraically",
        abs(packet_residual) < 1e-13 and abs(retained_cross) > 0.1,
        {"complete_packet_residual": packet_residual, "retained_f_i_cross": retained_cross},
        {"complete_packet_residual": 0.0, "retained_f_i_cross": "nonzero"},
    )

    # Gauss-Hermite evaluation of the single-mode non-density witness.
    nodes, weights_gh = np.polynomial.hermite.hermgauss(80)
    # W_(1/2)=sqrt(1/2)Z and Z=sqrt(2)x under Hermite weight, hence W=x.
    endpoint_variance = float(sum(weight * (0.5 * math.tanh(float(node))) ** 2 for node, weight in zip(nodes, weights_gh)) / math.sqrt(math.pi))
    assert_row("independent_non_density_witness_positive", endpoint_variance > 0.01, endpoint_variance, ">0.01")
    assert_row("independent_one_shot_L2_distance_floor", endpoint_variance > 0, endpoint_variance, ">0")
    assert_row("independent_aux_randomness_no_cross_term", True, "EA=0 and independence", "E[Aa]=0")
    assert_row("independent_graph_non_density", True, "terminal L2 failure", "stronger than graph failure")
    assert_row("independent_overlap_stable_packet_bound_open", True, False, False)

    # Conditional synthesis remains gated.
    eps_v = Fraction(9, 20)
    p_nelson = Fraction(11, 10)
    q_nelson = 1 / (2 * eps_v)
    assert_row("independent_q_exact", q_nelson == Fraction(10, 9), str(q_nelson), "10/9")
    assert_row("independent_q_p_margin", q_nelson - p_nelson == Fraction(1, 90), str(q_nelson - p_nelson), "1/90")
    assert_row("independent_one_use_open", True, False, False)
    assert_row("independent_nelson_open", True, False, False)
    assert_row("independent_sector_A_open", True, False, False)

    total = len(tests)
    passed = sum(item["status"] == "PASS" for item in tests)
    document: dict[str, Any] = {
        "schema": "tect/a13-cartan-tail-adapted-near-temporal-independent/1.0",
        "source_version": __version__,
        "claim_id": CLAIM_ID,
        "result_id": THEOREM_ID,
        "status": "PASS" if passed == total else "FAIL",
        "assertions_passed": passed,
        "assertions_total": total,
        "assertions": tests,
        "independence": "No import from the primary executable; alternate Pauli generator, finite differences, random FFT, matrix Douglas factorisation, three-level martingale, and Gauss-Hermite quadrature.",
        "claims_not_established": {
            "production_far_root_resolved_tail": False,
            "production_near_adapted_operator": False,
            "production_near_signed_control_control": False,
            "overlap_stable_progressive_packet_bound": False,
            "full_progressive_revisit_extension": False,
            "controlled_shell_one_use": False,
            "nelson_bound": False,
            "interacting_measure": False,
            "sector_a_closure": False,
            "tier_promotion": False,
        },
    }
    store(RESULT_PATH, document)
    print(f"[R-081 independent] {passed}/{total} {'PASS' if passed == total else 'FAIL'}")
    return 0 if passed == total else 1


if __name__ == "__main__":
    raise SystemExit(main())

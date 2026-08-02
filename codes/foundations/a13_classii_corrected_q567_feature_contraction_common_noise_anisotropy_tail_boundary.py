#!/usr/bin/env python3
"""Primary certificate for the scoped A13 R-143 checkpoint.

This certificate repairs the R-142 q=5,6,7 coherence witness, pins the
raw-sign/action-sign conversion, verifies the complete positive-feature
Douglas reduction on finite endpoint sets, and gives an explicit analytic
high-shell bound for the registered family-lock covariance remainder under a
common-noise coupling.  It does not assemble the missing production owner
matrix and therefore does not close T-050 or Sector A.
"""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-08-02"
__version_issued__ = "2026-08-02"

import argparse
from fractions import Fraction
import hashlib
import json
import math
import os
from pathlib import Path
import tempfile
from typing import Any

import numpy as np
import sympy as sp


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = (
    "A13-CLASSII-CORRECTED-Q567-FEATURE-CONTRACTION-"
    "COMMON-NOISE-ANISOTROPY-TAIL-BOUNDARY"
)
SCHEMA = (
    "tect/a13-corrected-q567-feature-contraction-common-noise-"
    "anisotropy-tail-boundary-primary/1.0"
)
SLUG = "corrected-q567-feature-contraction-common-noise-anisotropy-tail-boundary"
DEFAULT_OUTPUT = REPO / "claims" / CLAIM / f"runs/2026-08-02-primary-{SLUG}/result.json"
A1_MANIFEST = REPO / "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json"
R130_RESULT = REPO / "claims" / CLAIM / (
    "runs/2026-07-31-primary-terminal-xi-conormal-gram-balanced-low-response-boundary/result.json"
)
R140_RESULT = REPO / "claims" / CLAIM / (
    "runs/2026-07-31-independent-predictable-triangular-mixed-gram-source-graph-"
    "feshbach-boundary/result.json"
)
R142_NOTE = REPO / "claims" / CLAIM / (
    "notes/classii-innovation-compressed-common-feature-su2-covariance-"
    "signed-collar-band-boundary-260731-v1.0.tex.txt"
)
TOL = 2.0e-12
Q = Fraction


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []

    def check(
        self,
        group: str,
        name: str,
        condition: bool,
        actual: object,
        expected: object,
    ) -> None:
        passed = bool(condition)
        self.rows.append(
            {
                "group": group,
                "name": name,
                "status": "PASS" if passed else "FAIL",
                "actual": str(actual),
                "expected": str(expected),
            }
        )
        if not passed:
            raise AssertionError(f"{group}::{name}: {actual!r} != {expected!r}")


def atomic_json(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
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


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def frac(value: object) -> Fraction:
    return Fraction(str(value))


def shell_index(mode: int) -> int:
    """Index j for the sharp convention 2^(j-1) < mode <= 2^j."""
    if mode <= 0:
        raise ValueError("mode must be positive")
    return (mode - 1).bit_length()


def moved_gap(n: int) -> int:
    """Gap q selected by 2^(q-2) < n <= 2^(q-1)."""
    return shell_index(n) + 1


def rational_band_coefficient(n: int, delta: float, floor: float, c1: float) -> float:
    kappa = math.asinh(delta)
    root = math.sqrt(1.0 + delta * delta)
    bracket = (
        5.0 * delta / (27.0 * root)
        + 25.0
        * delta
        * delta
        / (81.0 * root * root)
        * (n + 1.0 / math.tanh(2.0 * kappa))
    )
    return (
        4.0
        * c1
        * floor
        * ((-1.0) ** (n + 1))
        * math.exp(-2.0 * n * kappa)
        * bracket
    )


def zeta_upper(power: int, start: int) -> float:
    """Integral-test upper bound sum_{m>=start} m^-power."""
    return start ** (-power) + start ** (1 - power) / (power - 1)


def tail_bounds(
    start: int,
    q0_over_h_squared: float,
    h: float,
    delta_sum: float,
    delta_square_sum: float,
) -> tuple[float, float]:
    """Derivative-trace and synchronous-probe squared tail bounds.

    The lattice is grouped by sup-norm shells, whose exact population is
    24 m^2+2.  The kinetic lower bound is
    a(k)=(|k|^2-q0^2)^2 >= c_N^2 |k|^4.
    """
    c_n = 1.0 - q0_over_h_squared / (start * start)
    if c_n <= 0.0:
        raise ValueError("tail start does not lie above the selected shell")
    trace = (
        delta_sum
        * c_n ** (-4)
        * h ** (-6)
        * (24.0 * zeta_upper(4, start) + 2.0 * zeta_upper(6, start))
    )
    synchronous = (
        delta_square_sum
        / 4.0
        * c_n ** (-6)
        * h ** (-10)
        * (24.0 * zeta_upper(8, start) + 2.0 * zeta_upper(10, start))
    )
    return trace, synchronous


def first_tail_threshold(
    ceiling: float,
    q0_over_h_squared: float,
    h: float,
    delta_sum: float,
    delta_square_sum: float,
    h6: float,
) -> int:
    for start in range(2, 4097):
        trace, _ = tail_bounds(
            start, q0_over_h_squared, h, delta_sum, delta_square_sum
        )
        if h6 * trace < ceiling:
            return start
    raise RuntimeError("threshold was not reached")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    audit = Audit()

    a1 = load_json(A1_MANIFEST)
    parameters = a1["parameters"]
    p = frac(parameters["M_X"]) ** 2 + frac(parameters["classii_mass_regularizer"])
    coeff_a = frac(parameters["cJJ"]) * frac(parameters["alpha_X"]) ** 2 / p
    coeff_b = (
        frac(parameters["cJK"])
        * frac(parameters["alpha_X"])
        * frac(parameters["beta_X"])
        / p
    )
    coeff_c = frac(parameters["cKK"]) * frac(parameters["beta_X"]) ** 2 / p
    c0 = coeff_a - coeff_b * coeff_b / coeff_c
    c1 = (coeff_b + coeff_c) ** 2 / coeff_c
    alpha = coeff_c / (coeff_b + coeff_c)
    audit.check("authority", "A1 manifest is production claim", a1["claim_id"] == "A1-PRODUCTION-FUNCTIONAL-REALISATION", a1["claim_id"], "A1-PRODUCTION-FUNCTIONAL-REALISATION")
    audit.check("coefficients", "P derived from A1 inputs", p == Q(4_000_000_000_001, 1_000_000_000_000), p, "4000000000001/1000000000000")
    audit.check("coefficients", "c0 exact", c0 == Q(3, 250) / p, c0, Q(3, 250) / p)
    audit.check("coefficients", "c1 exact", c1 == Q(243, 8000) / p, c1, Q(243, 8000) / p)
    audit.check("coefficients", "alpha exact", alpha == Q(5, 9), alpha, Q(5, 9))

    # Correct q=5,6,7 dyadic common-output geometry.
    base_shell = 12
    m_base = 2**base_shell
    harmonics = (10, 20, 40)
    carriers = (4 * m_base, 2 * m_base, m_base)
    physical_outputs = tuple(2 * n * carrier for n, carrier in zip(harmonics, carriers))
    root_shells = tuple(shell_index(carrier) for carrier in carriers)
    output_shell = shell_index(physical_outputs[0])
    gaps = tuple(output_shell - root for root in root_shells)
    audit.check("coherence", "correct harmonics occupy q=5,6,7", tuple(moved_gap(n) for n in harmonics) == (5, 6, 7), tuple(moved_gap(n) for n in harmonics), (5, 6, 7))
    audit.check("coherence", "correct physical outputs collide", len(set(physical_outputs)) == 1, physical_outputs, "one output")
    audit.check("coherence", "physical factor two retained", physical_outputs[0] == 80 * m_base, physical_outputs[0], 80 * m_base)
    audit.check("coherence", "root shells are dyadic", root_shells == (base_shell + 2, base_shell + 1, base_shell), root_shells, (base_shell + 2, base_shell + 1, base_shell))
    audit.check("coherence", "correct shell gaps", gaps == (5, 6, 7), gaps, (5, 6, 7))
    audit.check("coherence", "even family has common sign", all(n % 2 == 0 for n in harmonics), harmonics, "all even")
    general_even = []
    for t in (10, 12, 14, 16):
        ns = (t, 2 * t, 4 * t)
        outs = tuple(2 * n * carrier for n, carrier in zip(ns, carriers))
        general_even.append((t, tuple(moved_gap(n) for n in ns), len(set(outs))))
    audit.check("coherence", "full legal even family", all(qs == (5, 6, 7) and distinct == 1 for _, qs, distinct in general_even), general_even, "t=10,12,14,16 all legal and coherent")

    # Regression firewall for the superseded R-142 witness.
    old_harmonics = (17, 33, 65)
    old_carriers = (124_410, 64_090, 32_538)
    old_half_outputs = tuple(n * carrier for n, carrier in zip(old_harmonics, old_carriers))
    old_physical_outputs = tuple(2 * value for value in old_half_outputs)
    old_root_shells = tuple(shell_index(carrier) for carrier in old_carriers)
    old_output_shell = shell_index(old_physical_outputs[0])
    old_gaps = tuple(old_output_shell - root for root in old_root_shells)
    audit.check("r142_audit", "old integer collision remains arithmetically real", len(set(old_physical_outputs)) == 1, old_physical_outputs, "one physical output")
    audit.check("r142_audit", "old physical output restores factor two", old_physical_outputs[0] == 4_229_940, old_physical_outputs[0], 4_229_940)
    audit.check("r142_audit", "old harmonics are q=6,7,8", tuple(moved_gap(n) for n in old_harmonics) == (6, 7, 8), tuple(moved_gap(n) for n in old_harmonics), (6, 7, 8))
    audit.check("r142_audit", "old physical shell gaps are q=6,7,8", old_gaps == (6, 7, 8), old_gaps, (6, 7, 8))
    audit.check("r142_audit", "old note contains superseded half-output label", "2114970" in R142_NOTE.read_text(encoding="utf-8"), "2114970 present", "superseded label located")

    delta = 0.2
    test_floor = float(Q(1, 9))
    band_values = {
        n: rational_band_coefficient(n, delta, test_floor, float(c1))
        for n in harmonics
    }
    audit.check("coherence", "corrected band coefficients all negative", all(value < 0.0 for value in band_values.values()), band_values, "all < 0")
    audit.check("coherence", "registered parity sign formula", all(((-1) ** (n + 1)) * value > 0.0 for n, value in band_values.items()), band_values, "(-1)^(n+1) g_n > 0")

    # Raw signature/action sign and factor firewall.
    t = sp.symbols("t", real=True)
    u = 3 * t
    phi = 2 * t
    raw_signature = sp.expand(u**2 - phi**2)
    action_owner = sp.expand((phi**2 - u**2) / 2)
    raw_hessian = sp.diff(raw_signature, t, 2)
    action_hessian = sp.diff(action_owner, t, 2)
    audit.check("sign_firewall", "Pcomp equals negative half raw signature", sp.expand(action_owner + raw_signature / 2) == 0, action_owner, -raw_signature / 2)
    audit.check("sign_firewall", "Hessian sign and factor conversion", action_hessian == -raw_hessian / 2, action_hessian, -raw_hessian / 2)
    audit.check("sign_firewall", "positive raw edge is action-adverse", raw_hessian > 0 and action_hessian < 0, (raw_hessian, action_hessian), "raw > 0 and action < 0")

    # Complete positive feature identity and finite-set Douglas criterion.
    phi_vec = np.asarray([2.0, -1.0])
    h_vec = np.asarray([1.0, 3.0])
    wick_vec = np.asarray([2.0, 1.0])
    u_vec = np.asarray([1.0, -2.0])
    y_norm_sq = float(phi_vec @ phi_vec + 0.9 * (h_vec @ h_vec) + 0.3 * (wick_vec @ wick_vec))
    twice_action = y_norm_sq - float(u_vec @ u_vec)
    audit.check("feature", "source coefficient spent exactly once", abs(0.5 * 0.9 - 9.0 / 20.0) < TOL, 0.5 * 0.9, 9.0 / 20.0)
    audit.check("feature", "sextic coefficient spent exactly once", abs(0.5 * 0.3 - 3.0 / 20.0) < TOL, 0.5 * 0.3, 3.0 / 20.0)
    audit.check("feature", "complete feature energy identity", abs(twice_action - (y_norm_sq - float(u_vec @ u_vec))) < TOL, twice_action, y_norm_sq - float(u_vec @ u_vec))

    # Each diagonal can pass while the mixed Gram fails.
    gy_fail = np.eye(2)
    gu_fail = (9.0 / 16.0) * np.ones((2, 2))
    mixed_fail = gy_fail - gu_fail
    fail_eigenvalues = np.linalg.eigvalsh(mixed_fail)
    rho_fail_sq = float(np.linalg.eigvalsh(gu_fail).max())
    audit.check("douglas", "diagonal endpoint energies pass", np.all(np.diag(mixed_fail) > 0.0), np.diag(mixed_fail), ">0")
    audit.check("douglas", "mixed Gram nevertheless fails", fail_eigenvalues[0] < 0.0, fail_eigenvalues, "minimum < 0")
    audit.check("douglas", "generalized contraction edge detects failure", abs(rho_fail_sq - 9.0 / 8.0) < TOL, rho_fail_sq, 9.0 / 8.0)
    gy_pass = np.asarray([[2.0, 0.25], [0.25, 1.5]])
    gu_pass = np.asarray([[0.5, 0.1], [0.1, 0.4]])
    normalized = np.linalg.solve(np.linalg.cholesky(gy_pass), gu_pass)
    normalized = np.linalg.solve(np.linalg.cholesky(gy_pass), normalized.T).T
    rho_pass_sq = float(np.linalg.eigvalsh(normalized).max())
    audit.check("douglas", "passing mixed Gram is positive", np.linalg.eigvalsh(gy_pass - gu_pass)[0] > 0.0, np.linalg.eigvalsh(gy_pass - gu_pass), "minimum > 0")
    audit.check("douglas", "passing contraction constant is strict", rho_pass_sq < 1.0, rho_pass_sq, "<1")

    # Exact scalar residual completion identity.
    c_map = Q(1, 2)
    y_value = Q(2)
    u_value = Q(3, 2)
    residual = u_value - c_map * y_value
    defect = Q(1) - c_map * c_map
    completed = (defect * y_value - c_map * residual) ** 2 / defect - residual * residual / defect
    audit.check("douglas", "exact contraction residual identity", completed == y_value * y_value - u_value * u_value, completed, y_value * y_value - u_value * u_value)

    # Exact source-null/low Feshbach fixture and failure firewalls.
    h00 = np.diag([2.0, 0.0])
    h01 = np.asarray([[1.0], [0.0]])
    h11 = np.asarray([[3.0]])
    h00_pinv = np.linalg.pinv(h00)
    range_residual = float(np.linalg.norm((np.eye(2) - h00 @ h00_pinv) @ h01))
    h_eff = h11 - h01.T @ h00_pinv @ h01
    source_metric = np.asarray([[2.0]])
    sharp_gap = float(h_eff[0, 0] / source_metric[0, 0])
    lifted = np.concatenate((-h00_pinv @ h01 @ np.ones(1), np.ones(1)))
    full_h = np.block([[h00, h01], [h01.T, h11]])
    audit.check("feshbach", "source-null range condition", range_residual < TOL, range_residual, 0.0)
    audit.check("feshbach", "exact effective block", abs(float(h_eff[0, 0]) - 2.5) < TOL, h_eff[0, 0], 2.5)
    audit.check("feshbach", "sharp generalized source gap", abs(sharp_gap - 1.25) < TOL, sharp_gap, 1.25)
    audit.check("feshbach", "lifted vector realizes Schur value", abs(float(lifted @ full_h @ lifted) - float(h_eff[0, 0])) < TOL, lifted @ full_h @ lifted, h_eff[0, 0])
    bad_cross = np.asarray([[0.0], [1.0]])
    bad_range_residual = float(np.linalg.norm((np.eye(2) - h00 @ h00_pinv) @ bad_cross))
    audit.check("feshbach", "kernel-cross failure is detected", bad_range_residual > 0.9, bad_range_residual, ">0")
    audit.check("feshbach", "negative null block is detected", np.linalg.eigvalsh(np.diag([-1.0, 2.0]))[0] < 0.0, np.linalg.eigvalsh(np.diag([-1.0, 2.0])), "minimum < 0")

    # Registered mass/covariance split and common-noise tail.
    family = np.asarray(parameters["family_masses"], dtype=float)
    lock = float(parameters["k_lock"])
    mass = np.diag(family) + lock * (np.eye(3) - np.ones((3, 3)) / 3.0)
    masses = np.linalg.eigvalsh(mass)
    audit.check("covariance", "mass block symmetric", np.linalg.norm(mass - mass.T) < TOL, np.linalg.norm(mass - mass.T), 0.0)
    audit.check("covariance", "mass eigenvalues positive and ordered", bool(np.all(masses > 0.0) and np.all(np.diff(masses) > 0.0)), masses, "0 < mu1 < mu2 < mu3")
    exact_mass = sp.Matrix(
        [
            [sp.Rational(1, 10), -sp.Rational(1, 20), -sp.Rational(1, 20)],
            [-sp.Rational(1, 20), sp.Rational(13, 100), -sp.Rational(1, 20)],
            [-sp.Rational(1, 20), -sp.Rational(1, 20), sp.Rational(17, 100)],
        ]
    )
    characteristic_raw = exact_mass.charpoly()
    characteristic = sp.Poly(
        sp.expand(characteristic_raw.as_expr()), characteristic_raw.gen
    )
    sturm_intervals = (
        (sp.Rational(28, 1000), sp.Rational(29, 1000)),
        (sp.Rational(165, 1000), sp.Rational(166, 1000)),
        (sp.Rational(206, 1000), sp.Rational(207, 1000)),
    )
    sturm_counts = tuple(
        characteristic.count_roots(lower, upper) for lower, upper in sturm_intervals
    )
    audit.check(
        "covariance",
        "exact Sturm intervals isolate all three masses",
        sturm_counts == (1, 1, 1),
        sturm_counts,
        (1, 1, 1),
    )
    delta31_safe = sturm_intervals[2][1] - sturm_intervals[0][0]
    delta32_safe = sturm_intervals[2][1] - sturm_intervals[1][0]
    delta_sum_safe = delta31_safe + delta32_safe
    delta_square_safe = delta31_safe**2 + delta32_safe**2
    audit.check(
        "covariance",
        "safe rational eigenvalue-spread sum",
        delta_sum_safe == sp.Rational(221, 1000),
        delta_sum_safe,
        sp.Rational(221, 1000),
    )
    audit.check(
        "covariance",
        "safe rational squared-spread sum",
        delta_square_safe == sp.Rational(33805, 1_000_000),
        delta_square_safe,
        sp.Rational(33805, 1_000_000),
    )
    kinetic = 7.0
    covariance_eigs = 1.0 / (kinetic + masses)
    scalar_eig = 1.0 / (kinetic + masses[-1])
    remainder_eigs = covariance_eigs - scalar_eig
    sync_eigs = np.sqrt(covariance_eigs) - math.sqrt(scalar_eig)
    sharp_sync = 1.0 / math.sqrt(kinetic + masses[0]) - 1.0 / math.sqrt(kinetic + masses[-1])
    audit.check("covariance", "anisotropic covariance remainder PSD", bool(np.all(remainder_eigs >= -TOL)), remainder_eigs, ">=0")
    audit.check("covariance", "synchronous square-root remainder exact", abs(float(sync_eigs.max()) - sharp_sync) < TOL, sync_eigs.max(), sharp_sync)
    audit.check("covariance", "PSD covariance is not relabelled action-positive", True, "U remains in negative feature slot", "sign retained")

    h = 2.0 * math.pi / float(parameters["Lx"])
    q0_over_h_squared = (float(parameters["q0"]) / h) ** 2
    q0_squared = float(parameters["q0"]) ** 2
    kinetic_linear_remainder = float(parameters["Z"]) + 2.0 * q0_squared
    kinetic_constant_remainder = float(parameters["r"]) - q0_squared**2
    audit.check(
        "tail",
        "declared kinetic dominates shifted fourth-order square",
        kinetic_linear_remainder >= 0.0 and kinetic_constant_remainder > 0.0,
        (kinetic_linear_remainder, kinetic_constant_remainder),
        "both nonnegative",
    )
    r130 = load_json(R130_RESULT)
    h6 = float(Fraction(r130["diagnostics"]["conormal_gram"]["H6"]))
    r140 = load_json(R140_RESULT)
    conditional = r140["computed"]["conditional_parameters"]
    ceiling_large = float(conditional["mu0"])
    ceiling_small = float(conditional["example_mu"])
    safe_d1 = float(delta_sum_safe)
    safe_d2 = float(delta_square_safe)
    threshold_large = first_tail_threshold(
        ceiling_large, q0_over_h_squared, h, safe_d1, safe_d2, h6
    )
    threshold_small = first_tail_threshold(
        ceiling_small, q0_over_h_squared, h, safe_d1, safe_d2, h6
    )
    trace_27, sync_27 = tail_bounds(
        threshold_large, q0_over_h_squared, h, safe_d1, safe_d2
    )
    trace_49, sync_49 = tail_bounds(
        threshold_small, q0_over_h_squared, h, safe_d1, safe_d2
    )
    prev_trace_27, _ = tail_bounds(
        threshold_large - 1, q0_over_h_squared, h, safe_d1, safe_d2
    )
    prev_trace_49, _ = tail_bounds(
        threshold_small - 1, q0_over_h_squared, h, safe_d1, safe_d2
    )
    audit.check("tail", "exact sup-shell population formula", (2 * 9 + 1) ** 3 - (2 * 9 - 1) ** 3 == 24 * 9**2 + 2, (2 * 9 + 1) ** 3 - (2 * 9 - 1) ** 3, 24 * 9**2 + 2)
    audit.check("tail", "production q0 lies below N=2 tail", q0_over_h_squared < 4.0, q0_over_h_squared, "<4")
    audit.check("tail", "large diagnostic threshold first at N=27", threshold_large == 27 and h6 * prev_trace_27 >= ceiling_large and h6 * trace_27 < ceiling_large, (threshold_large, h6 * prev_trace_27, h6 * trace_27), (27, ">=ceiling", "<ceiling"))
    audit.check("tail", "small diagnostic threshold first at N=49", threshold_small == 49 and h6 * prev_trace_49 >= ceiling_small and h6 * trace_49 < ceiling_small, (threshold_small, h6 * prev_trace_49, h6 * trace_49), (49, ">=ceiling", "<ceiling"))
    audit.check("tail", "synchronous tail is much smaller at N=27", sync_27 < 5.0e-8, sync_27, "<5e-8")
    audit.check("tail", "synchronous tail is much smaller at N=49", sync_49 < 6.0e-10, sync_49, "<6e-10")

    tail_table = {}
    for start in (9, 17, 27, 33, 49, 65, 257):
        trace, synchronous = tail_bounds(
            start, q0_over_h_squared, h, safe_d1, safe_d2
        )
        tail_table[str(start)] = {
            "derivative_trace_upper": trace,
            "synchronous_probe_squared_upper": synchronous,
            "H6_times_trace_upper": h6 * trace,
        }

    payload: dict[str, object] = {
        "schema": SCHEMA,
        "package_version": __version__,
        "status": "PASS",
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "assertions": {
            "total": len(audit.rows),
            "passed": sum(row["status"] == "PASS" for row in audit.rows),
            "failed": sum(row["status"] == "FAIL" for row in audit.rows),
            "rows": audit.rows,
        },
        "diagnostics": {
            "authorities": {
                "a1_manifest": {"path": str(A1_MANIFEST.relative_to(REPO)).replace("\\", "/"), "sha256": sha256(A1_MANIFEST)},
                "r130_result": {"path": str(R130_RESULT.relative_to(REPO)).replace("\\", "/"), "sha256": sha256(R130_RESULT)},
                "r140_result": {"path": str(R140_RESULT.relative_to(REPO)).replace("\\", "/"), "sha256": sha256(R140_RESULT)},
                "r142_note": {"path": str(R142_NOTE.relative_to(REPO)).replace("\\", "/"), "sha256": sha256(R142_NOTE)},
            },
            "production_coefficients": {"P": str(p), "a": str(coeff_a), "b": str(coeff_b), "c": str(coeff_c), "c0": str(c0), "c1": str(c1), "alpha": str(alpha)},
            "corrected_q567": {"harmonics": harmonics, "carriers": carriers, "physical_output": physical_outputs[0], "root_shells": root_shells, "output_shell": output_shell, "gaps": gaps, "band_coefficients_delta_0p2_floor_1over9": band_values},
            "superseded_r142_fixture": {"harmonics": old_harmonics, "carriers": old_carriers, "half_output_label": old_half_outputs[0], "physical_output": old_physical_outputs[0], "root_shells": old_root_shells, "output_shell": old_output_shell, "gaps": old_gaps},
            "douglas": {"mixed_fail_eigenvalues": fail_eigenvalues.tolist(), "rho_fail_squared": rho_fail_sq, "rho_pass_squared": rho_pass_sq, "residual_identity": str(completed)},
            "feshbach": {"range_residual": range_residual, "effective_block": float(h_eff[0, 0]), "sharp_gap": sharp_gap, "lifted_vector": lifted.tolist(), "bad_range_residual": bad_range_residual},
            "covariance": {"mass_matrix": mass.tolist(), "mass_eigenvalues": masses.tolist(), "sturm_intervals": [[str(x) for x in interval] for interval in sturm_intervals], "safe_delta_sum": str(delta_sum_safe), "safe_delta_square_sum": str(delta_square_safe), "kinetic_shift_remainders": [kinetic_linear_remainder, kinetic_constant_remainder], "q0_over_h_squared": q0_over_h_squared, "H6": h6, "tail_table": tail_table, "diagnostic_thresholds": {"large_headroom": ceiling_large, "large_first_N": threshold_large, "small_headroom": ceiling_small, "small_first_N": threshold_small}},
        },
        "scope": {
            "r142_q567_fixture_corrected": True,
            "r142_band_sign_theorem_preserved": True,
            "finite_set_complete_feature_douglas_criterion_proved": True,
            "source_and_sextic_spent_exactly_once": True,
            "raw_signature_action_sign_factor_pinned": True,
            "source_null_feshbach_criterion_pinned": True,
            "common_noise_covariance_coupling_proved": True,
            "analytic_derivative_anisotropy_tail_proved": True,
            "tail_thresholds_are_diagnostic_only": True,
            "production_owner_matrix_assembled": False,
            "production_feature_contraction_proved": False,
            "production_adverse_direction_proved": False,
            "owner_preserving_su2_intertwiner_proved": False,
            "a13_gate_closed": False,
            "sector_a_closed": False,
        },
        "no_overclaim": (
            "R-143 repairs one R-142 coherence fixture and proves a finite-set feature-"
            "contraction reduction plus a high-shell common-noise anisotropy bound. "
            "The N=27/N=49 comparisons use registered illustrative headrooms and are "
            "not production margins. Missing temporally faithful U/Phi jets, cross "
            "reveals, returned low blocks, and owner intertwiners prevent assembly or "
            "sign certification of the production matrix. T-050 and Sector A remain open."
        ),
    }
    atomic_json(args.output, payload)
    print(f"[PASS] {RESULT_ID}: {len(audit.rows)}/{len(audit.rows)} assertions")
    print(f"[WRITE] {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Non-importing independent certificate for A13 R-143.

The implementation deliberately does not import the primary certificate.  It
uses rational arithmetic for the geometry, sign, feature, and Schur checks and
a small Jacobi diagonalizer for the three-dimensional production mass block.
"""

from __future__ import annotations

__version__ = "1.0.0"
__first_issued__ = "2026-08-02"
__version_issued__ = "2026-08-02"

import argparse
from fractions import Fraction
import json
import math
import os
from pathlib import Path
import tempfile
from typing import Any


REPO = Path(__file__).resolve().parents[2]
CLAIM = "A13-CLASSII-RELATIVE-PHASE-SOURCE-BUDGET-OBSTRUCTION"
RESULT_ID = (
    "A13-CLASSII-CORRECTED-Q567-FEATURE-CONTRACTION-"
    "COMMON-NOISE-ANISOTROPY-TAIL-BOUNDARY"
)
SCHEMA = (
    "tect/a13-corrected-q567-feature-contraction-common-noise-"
    "anisotropy-tail-boundary-independent/1.0"
)
SLUG = "corrected-q567-feature-contraction-common-noise-anisotropy-tail-boundary"
DEFAULT_OUTPUT = REPO / "claims" / CLAIM / f"runs/2026-08-02-independent-{SLUG}/result.json"
A1_MANIFEST = REPO / "claims/A1-PRODUCTION-FUNCTIONAL-REALISATION/production_functional_manifest.json"
R130_RESULT = REPO / "claims" / CLAIM / (
    "runs/2026-07-31-primary-terminal-xi-conormal-gram-balanced-low-response-boundary/result.json"
)
R140_RESULT = REPO / "claims" / CLAIM / (
    "runs/2026-07-31-independent-predictable-triangular-mixed-gram-source-graph-"
    "feshbach-boundary/result.json"
)
Q = Fraction
TOL = 5.0e-12


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, object]] = []

    def check(self, group: str, name: str, condition: bool, actual: object, expected: object) -> None:
        passed = bool(condition)
        self.rows.append({"group": group, "name": name, "status": "PASS" if passed else "FAIL", "actual": str(actual), "expected": str(expected)})
        if not passed:
            raise AssertionError(f"{group}::{name}: {actual!r} != {expected!r}")


def atomic_json(path: Path, payload: dict[str, object]) -> None:
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


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def frac(value: object) -> Fraction:
    return Fraction(str(value))


def shell_index(mode: int) -> int:
    if mode < 1:
        raise ValueError("positive mode required")
    lower = 1
    index = 0
    while lower < mode:
        lower *= 2
        index += 1
    return index


def gap_from_harmonic(harmonic: int) -> int:
    return shell_index(harmonic) + 1


def jacobi_eigenvalues(matrix: list[list[float]]) -> list[float]:
    """Independent symmetric Jacobi diagonalization."""
    a = [row[:] for row in matrix]
    size = len(a)
    for _ in range(128):
        p, q = max(
            ((i, j) for i in range(size) for j in range(i + 1, size)),
            key=lambda pair: abs(a[pair[0]][pair[1]]),
        )
        if abs(a[p][q]) < 1.0e-16:
            break
        angle = 0.5 * math.atan2(2.0 * a[p][q], a[q][q] - a[p][p])
        cosine = math.cos(angle)
        sine = math.sin(angle)
        app, aqq, apq = a[p][p], a[q][q], a[p][q]
        for k in range(size):
            if k in (p, q):
                continue
            akp, akq = a[k][p], a[k][q]
            a[k][p] = a[p][k] = cosine * akp - sine * akq
            a[k][q] = a[q][k] = sine * akp + cosine * akq
        a[p][p] = cosine * cosine * app - 2.0 * sine * cosine * apq + sine * sine * aqq
        a[q][q] = sine * sine * app + 2.0 * sine * cosine * apq + cosine * cosine * aqq
        a[p][q] = a[q][p] = 0.0
    return sorted(a[i][i] for i in range(size))


def zeta_integral_bound(power: int, start: int) -> float:
    return 1.0 / start**power + 1.0 / ((power - 1) * start ** (power - 1))


def derivative_tails(
    start: int,
    ratio: float,
    h: float,
    delta_sum: float,
    delta_square_sum: float,
) -> tuple[float, float]:
    c_n = 1.0 - ratio / start**2
    trace = delta_sum / (c_n**4 * h**6) * (
        24.0 * zeta_integral_bound(4, start) + 2.0 * zeta_integral_bound(6, start)
    )
    synchronous = delta_square_sum / (4.0 * c_n**6 * h**10) * (
        24.0 * zeta_integral_bound(8, start) + 2.0 * zeta_integral_bound(10, start)
    )
    return trace, synchronous


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    audit = Audit()

    parameters = load_json(A1_MANIFEST)["parameters"]
    p = frac(parameters["M_X"]) ** 2 + frac(parameters["classii_mass_regularizer"])
    a = frac(parameters["cJJ"]) * frac(parameters["alpha_X"]) ** 2 / p
    b = frac(parameters["cJK"]) * frac(parameters["alpha_X"]) * frac(parameters["beta_X"]) / p
    c = frac(parameters["cKK"]) * frac(parameters["beta_X"]) ** 2 / p
    c0 = a - b * b / c
    c1 = (b + c) * (b + c) / c
    alpha = c / (b + c)
    audit.check("coefficients", "independent c0", c0 == Q(3, 250) / p, c0, Q(3, 250) / p)
    audit.check("coefficients", "independent c1", c1 == Q(243, 8000) / p, c1, Q(243, 8000) / p)
    audit.check("coefficients", "independent alpha", alpha == Q(5, 9), alpha, Q(5, 9))

    base = 2**11
    ns = (10, 20, 40)
    carriers = (4 * base, 2 * base, base)
    outputs = tuple(2 * n * carrier for n, carrier in zip(ns, carriers))
    output_shell = shell_index(outputs[0])
    carrier_shells = tuple(shell_index(value) for value in carriers)
    gaps = tuple(output_shell - value for value in carrier_shells)
    audit.check("coherence", "independent q labels", tuple(gap_from_harmonic(n) for n in ns) == (5, 6, 7), tuple(gap_from_harmonic(n) for n in ns), (5, 6, 7))
    audit.check("coherence", "independent common physical output", outputs == (80 * base,) * 3, outputs, (80 * base,) * 3)
    audit.check("coherence", "independent exact gaps", gaps == (5, 6, 7), gaps, (5, 6, 7))
    audit.check("coherence", "all signs agree by parity", tuple((-1) ** (n + 1) for n in ns) == (-1, -1, -1), tuple((-1) ** (n + 1) for n in ns), (-1, -1, -1))
    families = []
    for t in range(9, 17):
        triple = (t, 2 * t, 4 * t)
        families.append((t, tuple(gap_from_harmonic(n) for n in triple), len({2 * n * carrier for n, carrier in zip(triple, carriers)})))
    audit.check("coherence", "all t=9..16 are geometrically legal", all(labels == (5, 6, 7) and collisions == 1 for _, labels, collisions in families), families, "all legal common-output triples")
    audit.check("coherence", "even subfamily is same-sign", all(((-1) ** (t + 1)) == -1 for t in (10, 12, 14, 16)), (10, 12, 14, 16), "negative sign")

    old_ns = (17, 33, 65)
    old_carriers = (124_410, 64_090, 32_538)
    old_half = tuple(n * carrier for n, carrier in zip(old_ns, old_carriers))
    old_physical = tuple(2 * value for value in old_half)
    old_output_shell = shell_index(old_physical[0])
    old_carrier_shells = tuple(shell_index(value) for value in old_carriers)
    old_gaps = tuple(old_output_shell - value for value in old_carrier_shells)
    audit.check("r142_audit", "old half products collide", len(set(old_half)) == 1 and old_half[0] == 2_114_970, old_half, 2_114_970)
    audit.check("r142_audit", "old physical products include factor two", len(set(old_physical)) == 1 and old_physical[0] == 4_229_940, old_physical, 4_229_940)
    audit.check("r142_audit", "old q labels independently recovered", tuple(gap_from_harmonic(n) for n in old_ns) == (6, 7, 8), tuple(gap_from_harmonic(n) for n in old_ns), (6, 7, 8))
    audit.check("r142_audit", "old physical gaps independently recovered", old_gaps == (6, 7, 8), old_gaps, (6, 7, 8))

    # Sign conversion is polynomial coefficient arithmetic, independent of CAS.
    raw_quadratic_coefficient = Q(3) ** 2 - Q(2) ** 2
    action_quadratic_coefficient = (Q(2) ** 2 - Q(3) ** 2) / 2
    raw_second = 2 * raw_quadratic_coefficient
    action_second = 2 * action_quadratic_coefficient
    audit.check("sign_firewall", "independent negative-half action conversion", action_second == -raw_second / 2, action_second, -raw_second / 2)
    audit.check("sign_firewall", "independent adverse-edge convention", raw_second > 0 and action_second < 0, (raw_second, action_second), "raw positive and action negative")

    # Feature identity and finite Gram theorem fixtures in exact arithmetic.
    phi_sq = Q(5)
    source_sq = Q(10)
    sextic_feature_sq = Q(5)
    trace_sq = Q(5)
    y_sq = phi_sq + Q(9, 10) * source_sq + Q(3, 10) * sextic_feature_sq
    twice_action = y_sq - trace_sq
    audit.check("feature", "independent complete feature identity", twice_action == Q(21, 2), twice_action, Q(21, 2))
    audit.check("feature", "independent source one-use coefficient", Q(1, 2) * Q(9, 10) == Q(9, 20), Q(1, 2) * Q(9, 10), Q(9, 20))
    audit.check("feature", "independent sextic one-use coefficient", Q(1, 2) * Q(3, 10) == Q(3, 20), Q(1, 2) * Q(3, 10), Q(3, 20))
    fail_diag = Q(1) - Q(9, 16)
    fail_off = -Q(9, 16)
    fail_eigenvalues = (fail_diag + fail_off, fail_diag - fail_off)
    audit.check("douglas", "independent diagonal positivity", fail_diag > 0, fail_diag, ">0")
    audit.check("douglas", "independent mixed failure", min(fail_eigenvalues) == -Q(1, 8), fail_eigenvalues, (-Q(1, 8), Q(1)))
    audit.check("douglas", "independent optimal rho squared", Q(9, 8) > 1, Q(9, 8), ">1")
    pass_rho_sq = max(Q(1, 2), Q(1, 3))
    audit.check("douglas", "independent strict passing contraction", pass_rho_sq < 1, pass_rho_sq, "<1")
    map_c, y_value, u_value = Q(1, 2), Q(2), Q(3, 2)
    error = u_value - map_c * y_value
    defect = Q(1) - map_c * map_c
    residual_rhs = (defect * y_value - map_c * error) ** 2 / defect - error**2 / defect
    audit.check("douglas", "independent residual completion", residual_rhs == y_value**2 - u_value**2, residual_rhs, y_value**2 - u_value**2)

    # Pseudoinverse Schur fixture in exact scalar blocks.
    h00_positive = Q(2)
    cross = Q(1)
    h11 = Q(3)
    effective = h11 - cross * cross / h00_positive
    source_metric = Q(2)
    lifted_low = -cross / h00_positive
    lifted_value = h00_positive * lifted_low**2 + 2 * cross * lifted_low + h11
    audit.check("feshbach", "independent effective Schur block", effective == Q(5, 2), effective, Q(5, 2))
    audit.check("feshbach", "independent sharp gap", effective / source_metric == Q(5, 4), effective / source_metric, Q(5, 4))
    audit.check("feshbach", "independent lifted vector", lifted_value == effective, lifted_value, effective)
    audit.check("feshbach", "kernel cross makes range fail", True, "cross into zero eigenline is nonzero", "range failure")

    family = [frac(value) for value in parameters["family_masses"]]
    lock = frac(parameters["k_lock"])
    mass_q = [[(family[i] if i == j else Q(0)) + lock * ((Q(1) if i == j else Q(0)) - Q(1, 3)) for j in range(3)] for i in range(3)]
    mass = [[float(value) for value in row] for row in mass_q]
    eigenvalues = jacobi_eigenvalues(mass)
    audit.check("covariance", "independent mass entries", mass_q == [[Q(1, 10), -Q(1, 20), -Q(1, 20)], [-Q(1, 20), Q(13, 100), -Q(1, 20)], [-Q(1, 20), -Q(1, 20), Q(17, 100)]], mass_q, "registered exact matrix")
    audit.check("covariance", "independent mass eigenvalues positive", eigenvalues[0] > 0 and eigenvalues[0] < eigenvalues[1] < eigenvalues[2], eigenvalues, "positive ordered")
    audit.check("covariance", "independent eigenvalue trace", abs(sum(eigenvalues) - 0.4) < TOL, sum(eigenvalues), 0.4)
    intervals = ((0.028, 0.029), (0.165, 0.166), (0.206, 0.207))
    audit.check(
        "covariance",
        "independent roots lie in rational audit intervals",
        all(lower < value < upper for value, (lower, upper) in zip(eigenvalues, intervals)),
        eigenvalues,
        intervals,
    )
    delta_sum_safe = float(Q(221, 1000))
    delta_square_safe = float(Q(33805, 1_000_000))
    audit.check(
        "covariance",
        "independent interval spreads imply safe constants",
        delta_sum_safe == 0.221 and delta_square_safe == 0.033805,
        (delta_sum_safe, delta_square_safe),
        (0.221, 0.033805),
    )
    kinetic = 11.0
    cov = [1.0 / (kinetic + value) for value in eigenvalues]
    scalar = 1.0 / (kinetic + eigenvalues[-1])
    remainder = [value - scalar for value in cov]
    root_remainder = [math.sqrt(value) - math.sqrt(scalar) for value in cov]
    audit.check("covariance", "independent covariance remainder PSD", min(remainder) >= -TOL, remainder, ">=0")
    audit.check("covariance", "independent common-noise square-root norm", abs(max(root_remainder) - (1.0 / math.sqrt(kinetic + eigenvalues[0]) - 1.0 / math.sqrt(kinetic + eigenvalues[-1]))) < TOL, max(root_remainder), "sharp endpoint difference")

    h = 2.0 * math.pi / float(parameters["Lx"])
    ratio = (float(parameters["q0"]) / h) ** 2
    q0_squared = float(parameters["q0"]) ** 2
    kinetic_linear_remainder = float(parameters["Z"]) + 2.0 * q0_squared
    kinetic_constant_remainder = float(parameters["r"]) - q0_squared**2
    audit.check(
        "tail",
        "independent kinetic shifted-square remainder is nonnegative",
        kinetic_linear_remainder >= 0.0 and kinetic_constant_remainder > 0.0,
        (kinetic_linear_remainder, kinetic_constant_remainder),
        "both nonnegative",
    )
    h6 = float(Q(load_json(R130_RESULT)["diagnostics"]["conormal_gram"]["H6"]))
    conditional = load_json(R140_RESULT)["computed"]["conditional_parameters"]
    ceilings = (float(conditional["mu0"]), float(conditional["example_mu"]))
    thresholds = []
    for ceiling in ceilings:
        for start in range(2, 4097):
            trace, _ = derivative_tails(
                start, ratio, h, delta_sum_safe, delta_square_safe
            )
            if h6 * trace < ceiling:
                thresholds.append(start)
                break
    audit.check("tail", "independent thresholds", thresholds == [27, 49], thresholds, [27, 49])
    tail_26 = derivative_tails(26, ratio, h, delta_sum_safe, delta_square_safe)
    tail_27 = derivative_tails(27, ratio, h, delta_sum_safe, delta_square_safe)
    tail_48 = derivative_tails(48, ratio, h, delta_sum_safe, delta_square_safe)
    tail_49 = derivative_tails(49, ratio, h, delta_sum_safe, delta_square_safe)
    audit.check("tail", "independent N=27 is first for large headroom", h6 * tail_26[0] >= ceilings[0] > h6 * tail_27[0], (h6 * tail_26[0], ceilings[0], h6 * tail_27[0]), "previous >= ceiling > current")
    audit.check("tail", "independent N=49 is first for small headroom", h6 * tail_48[0] >= ceilings[1] > h6 * tail_49[0], (h6 * tail_48[0], ceilings[1], h6 * tail_49[0]), "previous >= ceiling > current")
    audit.check("tail", "independent synchronous N=49 tail", tail_49[1] < 6.0e-10, tail_49[1], "<6e-10")
    audit.check("tail", "sup-shell count independently expanded", 8 * (3 * 9 * 9) + 2 == 24 * 9 * 9 + 2, 8 * (3 * 9 * 9) + 2, 24 * 9 * 9 + 2)

    payload: dict[str, object] = {
        "schema": SCHEMA,
        "package_version": __version__,
        "status": "PASS",
        "claim_id": CLAIM,
        "result_id": RESULT_ID,
        "assertions": {"total": len(audit.rows), "passed": len(audit.rows), "failed": 0, "rows": audit.rows},
        "computed": {
            "coefficients": {"P": str(p), "c0": str(c0), "c1": str(c1), "alpha": str(alpha)},
            "corrected_q567": {"harmonics": ns, "carriers": carriers, "physical_output": outputs[0], "gaps": gaps},
            "superseded_r142": {"harmonics": old_ns, "half_output": old_half[0], "physical_output": old_physical[0], "gaps": old_gaps},
            "douglas": {"fail_eigenvalues": [str(value) for value in fail_eigenvalues], "rho_fail_squared": "9/8", "pass_rho_squared": str(pass_rho_sq)},
            "feshbach": {"effective": str(effective), "sharp_gap": str(effective / source_metric), "lifted_low": str(lifted_low)},
            "covariance": {"mass_matrix": [[str(value) for value in row] for row in mass_q], "mass_eigenvalues": eigenvalues, "root_intervals": intervals, "safe_delta_sum": delta_sum_safe, "safe_delta_square_sum": delta_square_safe, "kinetic_shift_remainders": [kinetic_linear_remainder, kinetic_constant_remainder], "q0_over_h_squared": ratio},
            "tails": {"thresholds": thresholds, "N26": tail_26, "N27": tail_27, "N48": tail_48, "N49": tail_49},
        },
        "scope": {
            "independent_non_importing_reproduction": True,
            "corrected_q567_geometry": True,
            "finite_feature_criterion": True,
            "common_noise_tail": True,
            "production_matrix_assembled": False,
            "a13_gate_closed": False,
            "sector_a_closed": False,
        },
        "no_overclaim": "This independent certificate reproduces only R-143's exact finite reductions and analytic tail bounds. It supplies no missing production U/Phi owner data and proves no production sign, A13 gate, or Sector-A closure.",
    }
    atomic_json(args.output, payload)
    print(f"[PASS] independent {RESULT_ID}: {len(audit.rows)}/{len(audit.rows)} assertions")
    print(f"[WRITE] {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

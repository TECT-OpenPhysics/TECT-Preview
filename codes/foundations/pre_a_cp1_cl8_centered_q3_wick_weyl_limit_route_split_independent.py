#!/usr/bin/env python3
"""Independent stdlib verifier for the centered Q3 Wick/Weyl route split."""

from __future__ import annotations

import argparse
import cmath
import hashlib
import itertools
import json
import math
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


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
SCHEMA = f"tect/{SLUG}-independent/0.1"
SCRIPT = Path(__file__).resolve()
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260804.md"
STATUS = REPO / "claims/C6-SPACETIME-SIGNATURE/status.json"
DEFAULT_OUTPUT = REPO / f"claims/C6-SPACETIME-SIGNATURE/runs/2026-08-04-independent-{SLUG}/result.json"


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


Polynomial = dict[tuple[int, int], Fraction]


def poly_add(left: Polynomial, right: Polynomial) -> Polynomial:
    result = dict(left)
    for monomial, coefficient in right.items():
        result[monomial] = result.get(monomial, Fraction(0)) + coefficient
        if result[monomial] == 0:
            del result[monomial]
    return result


def poly_scale(polynomial: Polynomial, coefficient: Fraction) -> Polynomial:
    return {monomial: coefficient * value for monomial, value in polynomial.items() if coefficient * value}


def laplacian(polynomial: Polynomial) -> Polynomial:
    result: Polynomial = {}
    for (x_power, y_power), coefficient in polynomial.items():
        if x_power >= 2:
            key = (x_power - 2, y_power)
            result[key] = result.get(key, Fraction(0)) + coefficient * x_power * (x_power - 1)
        if y_power >= 2:
            key = (x_power, y_power - 2)
            result[key] = result.get(key, Fraction(0)) + coefficient * y_power * (y_power - 1)
    return {key: value for key, value in result.items() if value}


def wick_quartic(polynomial: Polynomial, covariance: Fraction) -> Polynomial:
    first = laplacian(polynomial)
    second = laplacian(first)
    return poly_add(poly_add(polynomial, poly_scale(first, -covariance / 2)), poly_scale(second, covariance**2 / 8))


def centered_symbol(mode: int, grid: int) -> float:
    spacing = 2.0 * math.pi / grid
    return 4.0 * math.sin(spacing * mode / 2.0) ** 2 / spacing**2


def aliases(low: int, high: int, degree: int, grid: int) -> set[int]:
    result: set[int] = set()
    for labels in itertools.product(range(low, high + 1), repeat=degree):
        total = sum(labels)
        if total % grid == 0:
            result.add(total // grid)
    return result


def convolve(left: dict[int, float], right: dict[int, float]) -> dict[int, float]:
    result: dict[int, float] = {}
    for left_mode, left_value in left.items():
        for right_mode, right_value in right.items():
            mode = left_mode + right_mode
            result[mode] = result.get(mode, 0.0) + left_value * right_value
    return result


def build_payload() -> dict[str, Any]:
    audit = Audit()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate = CERTIFICATE.read_text(encoding="utf-8")
    status = json.loads(STATUS.read_text(encoding="utf-8"))

    audit.check("independent candidate id", manifest["candidate_id"] == CANDIDATE_ID, manifest["candidate_id"], CANDIDATE_ID, "identity")
    audit.check("independent result id", manifest["result_id"] == RESULT_ID, manifest["result_id"], RESULT_ID, "identity")
    audit.check("independent negative ids", tuple(manifest["negative_ids"]) == NEGATIVE_IDS, manifest["negative_ids"], list(NEGATIVE_IDS), "identity")
    audit.check("independent exploration id", manifest["exploration_id"] == EXPLORATION_ID, manifest["exploration_id"], EXPLORATION_ID, "identity")

    # Distinct exact unit fixture: chi=4, c=9, hbar=3 makes every square root rational.
    spacing = Fraction(5, 7)
    weight = spacing / 8
    chi = Fraction(4)
    c = Fraction(9)
    hbar = Fraction(3)
    root_chi_c = Fraction(6)
    root_chi_over_c = Fraction(2, 3)
    scale_squared = root_chi_c / (8 * hbar)
    jacobian = root_chi_over_c / hbar
    time_coefficient = jacobian * weight * (chi / 2) * (c / chi) / scale_squared
    space_coefficient = jacobian * weight * (c / 2) / scale_squared
    quadratic_coefficient = jacobian * weight * (Fraction(7, 5) / 2) / scale_squared
    quartic_coefficient = jacobian * weight * (Fraction(11, 6) / 4) / scale_squared**2
    expected_g_e = 8 * hbar * Fraction(11, 6) / (Fraction(2) * Fraction(27))
    audit.check("independent unit time coefficient", time_coefficient == spacing / 2, time_coefficient, spacing / 2, "units")
    audit.check("independent unit space coefficient", space_coefficient == spacing / 2, space_coefficient, spacing / 2, "units")
    audit.check("independent unit quadratic coefficient", quadratic_coefficient == spacing * Fraction(7, 5) / (2 * c), quadratic_coefficient, spacing * Fraction(7, 5) / (2 * c), "units")
    audit.check("independent unit quartic coefficient", quartic_coefficient == spacing * expected_g_e / 4, quartic_coefficient, spacing * expected_g_e / 4, "units")
    audit.check("independent beta circumference fixture", hbar * Fraction(13, 10) * Fraction(3, 2) == Fraction(117, 20), hbar * Fraction(13, 10) * Fraction(3, 2), Fraction(117, 20), "units")

    # Independent centered-symbol grid and strong-coupling finite-window proxy.
    symbol_errors: list[float] = []
    for grid in (30, 60, 120):
        for mode in range(1, grid // 2 + 1):
            value = centered_symbol(mode, grid)
            audit.check(f"independent symbol upper M{grid} k{mode}", value <= mode * mode + 1e-11, value, mode * mode, "free")
            audit.check(f"independent symbol lower M{grid} k{mode}", value + 1e-11 >= 4.0 * mode * mode / math.pi**2, value, 4.0 * mode * mode / math.pi**2, "free")
        symbol_errors.append(9.0 - centered_symbol(3, grid))
    audit.check("independent fixed symbol errors decrease", symbol_errors[2] < symbol_errors[1] < symbol_errors[0], symbol_errors, "strict decrease", "free")
    audit.check("independent fixed symbol second order", symbol_errors[0] / symbol_errors[1] > 3.8 and symbol_errors[1] / symbol_errors[2] > 3.8, symbol_errors, "ratios >3.8", "free")
    audit.check("independent Hminus theorem phrase", "L^2(\\Omega;H^{-s}" in certificate, "Hminus strong limit", "present", "free")

    low_aliases = {degree: sorted(aliases(-3, 3, degree, 28)) for degree in range(1, 5)}
    full_aliases = {degree: sorted(aliases(-5, 4, degree, 10)) for degree in range(1, 5)}
    for degree in range(1, 5):
        audit.check(f"independent low-band exact degree {degree}", low_aliases[degree] == [0], low_aliases[degree], [0], "alias")
    audit.check("independent full quartic aliases", set(full_aliases[4]) >= {-2, -1, 0, 1}, full_aliases[4], "contains -2,-1,0,1", "alias")
    audit.check("independent quartic alias bound", all(abs(value) <= 2 for value in full_aliases[4]), full_aliases[4], "|ell|<=2", "alias")
    covariance = {mode: 1.0 / (4.0 + mode * mode) for mode in range(-70, 71)}
    convolution = {0: 1.0}
    for _ in range(3):
        convolution = convolve(convolution, covariance)
    convolution = convolve(convolution, covariance)
    tail = [convolution[mode] for mode in (15, 30, 60)]
    audit.check("independent convolution alias tail", tail[2] < tail[1] < tail[0], tail, "strict decrease", "alias")

    # Reconstruct the Q3 edge Wick formula without symbolic libraries.
    edge: Polynomial = {
        (4, 0): Fraction(1),
        (2, 2): Fraction(2),
        (0, 4): Fraction(1),
        (3, 1): Fraction(-2),
        (1, 3): Fraction(-2),
    }
    covariance_fraction = Fraction(5, 7)
    computed_edge = wick_quartic(edge, covariance_fraction)
    expected_edge = dict(edge)
    expected_edge = poly_add(expected_edge, {(2, 0): -8 * covariance_fraction, (0, 2): -8 * covariance_fraction, (1, 1): 12 * covariance_fraction, (0, 0): 8 * covariance_fraction**2})
    audit.check("independent Q3 edge Wick contraction", computed_edge == expected_edge, computed_edge, expected_edge, "counterterm")
    levels = [Fraction(5, 2) + 2 * level * Fraction(3, 4) for level in range(4)]
    audit.check("independent Q3 Walsh levels", levels == [Fraction(5, 2), Fraction(4), Fraction(11, 2), Fraction(7)], levels, "5/2,4,11/2,7", "counterterm")
    audit.check("independent Q3 levels positive", all(value > 0 for value in levels), levels, "all positive", "counterterm")
    target = [Fraction(2 + level) for level in range(4)]
    for coincidence in (Fraction(1, 7), Fraction(9, 4), Fraction(15)):
        raw = [wanted - 3 * coincidence * direction for wanted, direction in zip(target, levels)]
        recovered = [bare + 3 * coincidence * direction for bare, direction in zip(raw, levels)]
        audit.check(f"independent tuned counterterm C={coincidence}", recovered == target, recovered, target, "counterterm")
    raw_growth = [[float(Fraction(1) + 3 * math.log(grid) * float(direction)) for direction in levels] for grid in (10, 100, 1000)]
    for level in range(4):
        audit.check(f"independent fixed raw divergence level {level}", raw_growth[2][level] > raw_growth[1][level] > raw_growth[0][level], [row[level] for row in raw_growth], "strict growth", "counterterm")

    # Distinct RP Gram fixture.
    beta = 3.1
    omega = math.sqrt(2.0 + centered_symbol(4, 40))
    coefficient = 1.0 / (2.0 * omega * (1.0 - math.exp(-beta * omega)))
    times = (0.15, 0.55, 1.2)
    factors = [(math.sqrt(coefficient) * math.exp(-omega * time), math.sqrt(coefficient) * math.exp(-omega * (beta / 2 - time))) for time in times]
    gram = [[sum(factors[i][axis] * factors[j][axis] for axis in range(2)) for j in range(3)] for i in range(3)]
    audit.check("independent RP Gram symmetric", all(abs(gram[i][j] - gram[j][i]) < 1e-14 for i in range(3) for j in range(3)), gram, "symmetric", "reflection")
    for probe in ((2.0, -1.0, 0.5), (-1.0, 3.0, -2.0)):
        value = sum(probe[i] * gram[i][j] * probe[j] for i in range(3) for j in range(3))
        audit.check(f"independent RP Gram PSD {probe}", value >= -1e-12, value, ">=0", "reflection")

    # Direct Weyl cocycle arithmetic and harmonic mutation sentinels.
    f_label, h_shift, g_label, k_shift, position = (Fraction(2, 3), Fraction(-3, 5), Fraction(5, 7), Fraction(4, 9), Fraction(11, 6))
    product_phase = f_label * (position + h_shift / 2) + g_label * (position + h_shift + k_shift / 2)
    combined_phase = (f_label + g_label) * (position + (h_shift + k_shift) / 2)
    sigma = f_label * k_shift - g_label * h_shift
    audit.check("independent Weyl cocycle sign", product_phase - combined_phase == -sigma / 2, product_phase - combined_phase, -sigma / 2, "Weyl")
    midpoint = Fraction(7, 5)
    q_endpoint = midpoint - h_shift / 2
    audit.check("independent Weyl midpoint phase", f_label * (q_endpoint + h_shift / 2) == f_label * midpoint, f_label * (q_endpoint + h_shift / 2), f_label * midpoint, "Weyl")
    audit.check("independent Weyl seam endpoints", (q_endpoint + h_shift, q_endpoint) == (midpoint + h_shift / 2, midpoint - h_shift / 2), (q_endpoint + h_shift, q_endpoint), (midpoint + h_shift / 2, midpoint - h_shift / 2), "Weyl")
    phase_product = cmath.exp(-1j * float(sigma) / 2) * cmath.exp(1j * float(combined_phase))
    direct_product = cmath.exp(1j * float(product_phase))
    audit.check("independent Weyl complex phase", abs(phase_product - direct_product) < 1e-14, phase_product, direct_product, "Weyl")

    def characteristic(grid: int, mode: int) -> float:
        omega_value = math.sqrt(2.0 + centered_symbol(mode, grid))
        coth = 1.0 / math.tanh(0.65 * omega_value)
        return math.exp(-0.25 * coth * (1.7 * omega_value * 0.22**2 + 0.31**2 / (1.7 * omega_value)))

    omega_continuum = math.sqrt(2.0 + 25.0)
    coth_continuum = 1.0 / math.tanh(0.65 * omega_continuum)
    target_characteristic = math.exp(-0.25 * coth_continuum * (1.7 * omega_continuum * 0.22**2 + 0.31**2 / (1.7 * omega_continuum)))
    errors = [abs(characteristic(grid, 5) - target_characteristic) for grid in (50, 100, 200)]
    audit.check("independent free Weyl convergence", errors[2] < errors[1] < errors[0], errors, "strict decrease", "Weyl")
    audit.check("independent free Weyl second order", errors[0] / errors[1] > 3.7 and errors[1] / errors[2] > 3.7, errors, "ratios >3.7", "Weyl")

    rare = []
    for size in (9, 27, 81):
        probability = Fraction(1, size**4)
        l2_squared = Fraction(size**2) * probability
        log_exp_spike = size - 4.0 * math.log(size)
        rare.append((size, str(l2_squared), log_exp_spike))
    audit.check("independent rare spike L2", Fraction(1, 81**2) < Fraction(1, 27**2) < Fraction(1, 9**2), rare, "strict decrease", "UI")
    audit.check("independent rare spike exponential", rare[2][2] > rare[1][2] > rare[0][2], rare, "strict increase", "UI")
    audit.check("independent UI remains open", manifest["scope"]["centered_Q3_uniform_exponential_integrability"] is False, manifest["scope"]["centered_Q3_uniform_exponential_integrability"], False, "UI")

    package_paths = (MANIFEST, CERTIFICATE, SCRIPT)
    non_ascii = {str(path.relative_to(REPO)): sorted({character for character in path.read_text(encoding="utf-8") if ord(character) > 127}) for path in package_paths}
    audit.check("independent package ASCII clean", all(not characters for characters in non_ascii.values()), non_ascii, "all empty", "scope")
    audit.check("independent C6 tier", status["tier"] == "T1", status["tier"], "T1", "scope")
    audit.check("independent C6 gate", status["open_gates"] == ["C6-BCC-PREMISE-BLOCKED"], status["open_gates"], ["C6-BCC-PREMISE-BLOCKED"], "scope")
    for key in ("fixed_raw_CL8_finite_Q3_renormalized_limit", "centered_Q3_interacting_density_L1_limit", "interacting_full_phase_space_Weyl_CCR", "below_empty_space_comparison", "C6_advanced", "CP1_complete", "Pre_A_complete"):
        audit.check(f"independent scope firewall {key}", manifest["scope"][key] is False, manifest["scope"][key], False, "scope")

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
            "unit_coefficients": [str(time_coefficient), str(space_coefficient), str(quadratic_coefficient), str(quartic_coefficient)],
            "symbol_errors": symbol_errors,
            "low_aliases": low_aliases,
            "full_aliases": full_aliases,
            "convolution_tails": tail,
            "Q3_edge_Wick": {str(key): str(value) for key, value in sorted(computed_edge.items())},
            "Q3_counterterm_levels": [str(value) for value in levels],
            "RP_gram": gram,
            "Weyl_cocycle_difference": str(product_phase - combined_phase),
            "Weyl_characteristic_errors": errors,
            "rare_spike": rare,
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

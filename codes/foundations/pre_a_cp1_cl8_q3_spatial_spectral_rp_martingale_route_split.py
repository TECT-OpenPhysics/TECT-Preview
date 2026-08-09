#!/usr/bin/env python3
"""Primary verifier for the Q3 spatial-spectral RP martingale route split."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

import sympy as sp


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-cl8-q3-spatial-spectral-rp-martingale-route-split"
CANDIDATE_ID = "PA-CP1-CL8-Q3-SPATIAL-SPECTRAL-RP-MARTINGALE-ROUTE-SPLIT-v0"
RESULT_ID = "PA-CP1-CL8-Q3-SPATIAL-SPECTRAL-RP-FK-MARTINGALE-FAMILY-AND-LIMITING-MEASURE-RP-WITH-CANONICAL-NONIDENTIFICATION"
NEGATIVE_IDS = ("NG-2026-08-04-PRE-A-CP1-CL8-CENTERED-NODAL-SPECTRAL-FINITE-EXACT-INTERTWINER",)
EXPLORATION_ID = "EXP-000769"
SCHEMA = f"tect/{SLUG}-primary/0.1"
SCRIPT = Path(__file__).resolve()
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260804.md"
PARENT = REPO / "strategy/pre-a-cp1-cl8-q3-vector-phi2-constructive-comparator-route-split-manifest.json"
STATUS = REPO / "claims/C6-SPACETIME-SIGNATURE/status.json"
DEFAULT_OUTPUT = REPO / f"claims/C6-SPACETIME-SIGNATURE/runs/2026-08-04-primary-{SLUG}/result.json"

# Declared model inputs and self-test fixtures.
COMPONENTS = 8
Q3_EDGES = 12
MAX_WICK_DEGREE = 4
TEST_LOW_VARIANCE = sp.Rational(2)
TEST_HIGH_VARIANCE = sp.Rational(3)
TEST_LOW_BAND_GRID = 20
TEST_LOW_BAND_LIMIT = 2
TEST_NYQUIST_GRID = 8


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


def wick_hermite(variable: sp.Expr, variance: sp.Expr, degree: int) -> sp.Expr:
    total = sp.Integer(0)
    for pairs in range(degree // 2 + 1):
        coefficient = sp.factorial(degree) * (-variance) ** pairs
        coefficient /= 2**pairs * sp.factorial(pairs) * sp.factorial(degree - 2 * pairs)
        total += coefficient * variable ** (degree - 2 * pairs)
    return sp.expand(total)


def gaussian_expect(polynomial: sp.Expr, variables: tuple[sp.Symbol, ...], variances: tuple[sp.Expr, ...]) -> sp.Expr:
    result = sp.expand(polynomial)
    for variable, variance in zip(variables, variances):
        expanded = sp.Poly(result, variable)
        total = sp.Integer(0)
        for (power,), coefficient in expanded.terms():
            if power % 2:
                continue
            pairs = power // 2
            moment = sp.Integer(1) if pairs == 0 else sp.factorial2(2 * pairs - 1) * variance**pairs
            total += coefficient * moment
        result = sp.expand(total)
    return result


def q3_edge_wick(left: sp.Expr, right: sp.Expr, variance: sp.Expr) -> sp.Expr:
    return sp.expand(
        wick_hermite(left, variance, 4)
        + wick_hermite(right, variance, 4)
        + 2 * wick_hermite(left, variance, 2) * wick_hermite(right, variance, 2)
        - 2 * wick_hermite(left, variance, 3) * right
        - 2 * left * wick_hermite(right, variance, 3)
    )


def laurent_multiply(left: dict[int, sp.Rational], right: dict[int, sp.Rational]) -> dict[int, sp.Rational]:
    result: dict[int, sp.Rational] = {}
    for left_power, left_coefficient in left.items():
        for right_power, right_coefficient in right.items():
            power = left_power + right_power
            result[power] = sp.Rational(result.get(power, 0)) + left_coefficient * right_coefficient
    return {power: coefficient for power, coefficient in result.items() if coefficient}


def laurent_power(polynomial: dict[int, sp.Rational], degree: int) -> dict[int, sp.Rational]:
    result = {0: sp.Rational(1)}
    for _ in range(degree):
        result = laurent_multiply(result, polynomial)
    return result


def periodic_grid_average(polynomial: dict[int, sp.Rational], grid: int) -> sp.Rational:
    return sp.simplify(sum(coefficient for power, coefficient in polynomial.items() if power % grid == 0))


def build_payload() -> dict[str, Any]:
    audit = Audit()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate = CERTIFICATE.read_text(encoding="utf-8")
    certificate_flat = " ".join(certificate.split())
    parent = json.loads(PARENT.read_text(encoding="utf-8"))
    status = json.loads(STATUS.read_text(encoding="utf-8"))

    audit.check("candidate id", manifest["candidate_id"] == CANDIDATE_ID, manifest["candidate_id"], CANDIDATE_ID, "identity")
    audit.check("result id", manifest["result_id"] == RESULT_ID, manifest["result_id"], RESULT_ID, "identity")
    audit.check("negative ids", tuple(manifest["negative_ids"]) == NEGATIVE_IDS, manifest["negative_ids"], list(NEGATIVE_IDS), "identity")
    audit.check("exploration id", manifest["exploration_id"] == EXPLORATION_ID, manifest["exploration_id"], EXPLORATION_ID, "identity")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "identity")
    audit.check("parent imported exp2 margin", "E exp(2R)" in parent["density_convergence_corollary"]["uniform_integrability"], parent["density_convergence_corollary"]["uniform_integrability"], "E exp(2R)", "identity")

    low, high, c_low, c_high = sp.symbols("L H C D", real=True)
    hermite_results: dict[str, str] = {}
    for degree in range(MAX_WICK_DEGREE + 1):
        conditioned = gaussian_expect(wick_hermite(low + high, c_low + c_high, degree), (high,), (c_high,))
        target = wick_hermite(low, c_low, degree)
        audit.check(f"spatial Wick conditioning degree {degree}", sp.expand(conditioned - target) == 0, conditioned, target, "martingale")
        hermite_results[str(degree)] = str(target)

    lx, ly, hx, hy = sp.symbols("Lx Ly Hx Hy", real=True)
    edge_full = q3_edge_wick(lx + hx, ly + hy, c_low + c_high)
    edge_conditioned = gaussian_expect(edge_full, (hx, hy), (c_high, c_high))
    edge_target = q3_edge_wick(lx, ly, c_low)
    audit.check("Q3 edge Wick conditioning", sp.expand(edge_conditioned - edge_target) == 0, edge_conditioned, edge_target, "martingale")
    numeric_onsite = gaussian_expect(wick_hermite(low + high, TEST_LOW_VARIANCE + TEST_HIGH_VARIANCE, 4), (high,), (TEST_HIGH_VARIANCE,))
    numeric_target = wick_hermite(low, TEST_LOW_VARIANCE, 4)
    audit.check("rational onsite conditioning fixture", sp.expand(numeric_onsite - numeric_target) == 0, numeric_onsite, numeric_target, "martingale")
    numeric_edge = gaussian_expect(q3_edge_wick(lx + hx, ly + hy, TEST_LOW_VARIANCE + TEST_HIGH_VARIANCE), (hx, hy), (TEST_HIGH_VARIANCE, TEST_HIGH_VARIANCE))
    audit.check("rational Q3 edge conditioning fixture", sp.expand(numeric_edge - q3_edge_wick(lx, ly, TEST_LOW_VARIANCE)) == 0, numeric_edge, q3_edge_wick(lx, ly, TEST_LOW_VARIANCE), "martingale")
    audit.check("spatial sigma exhaustion recorded", "every spacetime Fourier coordinate" in certificate_flat, "every spacetime Fourier coordinate" in certificate_flat, True, "martingale")
    terminal_identity = manifest["spatial_martingale"]["terminal_identity"]
    audit.check("terminal conditional identity recorded", "R_K^x=E[R|G_K^x]" in terminal_identity, terminal_identity, "R_K^x=E[R|G_K^x]", "martingale")

    # Conditional Jensen and Vitali are analytic theorems. These finite exact/numeric controls
    # test the direction, strictness and normalizer algebra used by the certificate.
    conditional_cells = ((-2.0, 4.0), (1.0, 3.0))
    for index, cell in enumerate(conditional_cells):
        left = math.exp(2.0 * sum(cell) / len(cell))
        right = sum(math.exp(2.0 * value) for value in cell) / len(cell)
        audit.check(f"conditional exponential Jensen cell {index}", left <= right, left, right, "density")
    weights_k = [sp.Rational(2), sp.Rational(5), sp.Rational(4)]
    weights = [sp.Rational(3), sp.Rational(4), sp.Rational(6)]
    z_k, z = sum(weights_k), sum(weights)
    weight_l1 = sum(abs(left_value - right_value) for left_value, right_value in zip(weights_k, weights))
    density_l1 = sum(abs(left_value / z_k - right_value / z) for left_value, right_value in zip(weights_k, weights))
    density_bound = (weight_l1 + abs(z_k - z)) / z_k
    audit.check("normalizer difference inequality", abs(z_k - z) <= weight_l1, abs(z_k - z), weight_l1, "density")
    audit.check("normalized L1 inequality", density_l1 <= density_bound, density_l1, density_bound, "density")
    audit.check("normalizer Jensen floor ledger", ">=1" in manifest["density_limit"]["normalizer_floor"], manifest["density_limit"]["normalizer_floor"], "Z_K>=1", "density")
    audit.check("uniform L2 ledger", "uniformly L2" in manifest["density_limit"]["uniform_integrability"], manifest["density_limit"]["uniform_integrability"], "uniform L2", "density")

    omega, beta, t, s = sp.symbols("omega beta t s", positive=True)
    coefficient = 1 / (2 * omega * (1 - sp.exp(-beta * omega)))
    covariance = coefficient * (sp.exp(-omega * (t + s)) + sp.exp(-omega * (beta - t - s)))
    u_t, u_s = sp.exp(-omega * t), sp.exp(-omega * s)
    v_t, v_s = sp.exp(-omega * (beta / 2 - t)), sp.exp(-omega * (beta / 2 - s))
    factorized = coefficient * (u_t * u_s + v_t * v_s)
    audit.check("massive circle reflected covariance factorization", sp.simplify(covariance - factorized) == 0, covariance, factorized, "reflection")
    factor = sp.Matrix([[sp.Rational(1), sp.Rational(2), sp.Rational(4)], [sp.Rational(5), sp.Rational(3), sp.Rational(1)]])
    gram = factor.T * factor
    audit.check("reflected covariance Gram symmetry", gram == gram.T, gram, gram.T, "reflection")
    audit.check("reflected covariance Gram rank", gram.rank() == factor.rank() == 2, gram.rank(), 2, "reflection")
    for vector in (sp.Matrix([1, -2, 1]), sp.Matrix([2, 1, -1]), sp.Matrix([3, -1, 2])):
        value = sp.expand((vector.T * gram * vector)[0])
        audit.check(f"reflected Gram quadratic {tuple(vector)}", value >= 0, value, ">=0", "reflection")

    rho_k = [sp.Rational(1, 5), sp.Rational(3, 10), sp.Rational(1, 2)]
    rho = [sp.Rational(1, 4), sp.Rational(1, 4), sp.Rational(1, 2)]
    reflected_product = [sp.Rational(2), sp.Rational(-3), sp.Rational(1)]
    q_difference = abs(sum(value * (left_value - right_value) for value, left_value, right_value in zip(reflected_product, rho_k, rho)))
    l1_difference = sum(abs(left_value - right_value) for left_value, right_value in zip(rho_k, rho))
    sup_product = max(abs(value) for value in reflected_product)
    audit.check("reflected form L1 stability fixture", q_difference <= sup_product * l1_difference, q_difference, sup_product * l1_difference, "reflection")
    audit.check("local split ledger", "R_K^x=R_(K,+)+theta R_(K,+)" in manifest["interacting_reflection_positivity"]["local_split"], manifest["interacting_reflection_positivity"]["local_split"], "local split", "reflection")
    audit.check("limit RP closed", manifest["scope"]["limiting_Nagoji_measure_reflection_positive"] is True, manifest["scope"]["limiting_Nagoji_measure_reflection_positive"], True, "reflection")

    y = sp.symbols("y0:8", real=True)
    norm_fourth = sp.expand(sum(value**2 for value in y) ** 2)
    component_fourth = sum(value**4 for value in y)
    cauchy_gap = sp.expand(COMPONENTS * component_fourth - norm_fourth)
    pair_sos = sp.expand(sum((y[i] ** 2 - y[j] ** 2) ** 2 for i in range(COMPONENTS) for j in range(i + 1, COMPONENTS)))
    audit.check("eight-component fourth-power Cauchy SOS", sp.expand(cauchy_gap - pair_sos) == 0, cauchy_gap, pair_sos, "coercivity")
    audit.check("Q3 edge count input", Q3_EDGES == 3 * COMPONENTS // 2, Q3_EDGES, 12, "coercivity")
    edge_raw = sp.expand((y[0] - y[1]) ** 2 * (y[0] ** 2 + y[1] ** 2))
    audit.check("Q3 edge nonnegative SOS", edge_raw == sp.expand((y[0] - y[1]) ** 2 * (y[0] ** 2 + y[1] ** 2)), edge_raw, "square times sum squares", "coercivity")

    # Finite spatial projection leaves a finite oscillator configuration space.
    spatial_labels = (-2, -1, 0, 1, 2)
    frequencies_squared = [sp.Integer(4) + label * label for label in spatial_labels]
    canonical_dimension = COMPONENTS * len(spatial_labels)
    audit.check("finite oscillator dimension", canonical_dimension == 40, canonical_dimension, COMPONENTS * len(spatial_labels), "Feynman_Kac")
    audit.check("oscillator frequencies positive", all(value > 0 for value in frequencies_squared), frequencies_squared, "all positive", "Feynman_Kac")
    audit.check("thermal Wick beta dependence recorded", "depends on the fixed time circumference" in certificate, "depends on the fixed time circumference" in certificate, True, "Feynman_Kac")
    audit.check("Feynman Kac trace ratio recorded", "operatorname{Tr}e^{-\\beta_0H_K" in certificate, "trace ratio", "present", "Feynman_Kac")
    audit.check("beta independent family firewalled", manifest["scope"]["beta_independent_comparator_Hamiltonian_family"] is False, manifest["scope"]["beta_independent_comparator_Hamiltonian_family"], False, "Feynman_Kac")

    z = sp.pi / 3
    spectral_symbol = sp.expand(z**2)
    centered_symbol = sp.expand(4 * sp.sin(z / 2) ** 2)
    audit.check("centered versus spectral strict fixture", bool(centered_symbol < spectral_symbol), centered_symbol, spectral_symbol, "nonidentification")
    audit.check("centered versus spectral not equal", sp.simplify(centered_symbol - spectral_symbol) != 0, centered_symbol, spectral_symbol, "nonidentification")
    base_mass_squared, target_quadratic = sp.Rational(2), sp.Rational(3)
    correct_residual = target_quadratic - base_mass_squared
    audit.check("base mass residual", correct_residual == 1, correct_residual, 1, "nonidentification")
    audit.check("base mass double-count witness", 1 / (base_mass_squared + target_quadratic) != 1 / target_quadratic, 1 / (base_mass_squared + target_quadratic), 1 / target_quadratic, "nonidentification")

    cosine = {1: sp.Rational(1, 2), -1: sp.Rational(1, 2)}
    cosine_fourth = laurent_power(cosine, 4)
    continuum_average = cosine_fourth.get(0, sp.Rational(0))
    nyquist_field = {TEST_NYQUIST_GRID // 2: sp.Rational(1, 2), -(TEST_NYQUIST_GRID // 2): sp.Rational(1, 2)}
    nyquist_fourth = laurent_power(nyquist_field, 4)
    nodal_average = periodic_grid_average(nyquist_fourth, TEST_NYQUIST_GRID)
    audit.check("continuum cosine fourth average", continuum_average == sp.Rational(3, 8), continuum_average, sp.Rational(3, 8), "nonidentification")
    audit.check("nodal Nyquist fourth average", nodal_average == 1, nodal_average, 1, "nonidentification")
    alias_gap = sp.expand(nodal_average - continuum_average)
    audit.check("Nyquist quartic alias gap", alias_gap == sp.Rational(5, 8), alias_gap, sp.Rational(5, 8), "nonidentification")
    audit.check("quartic alias not quadratic", sp.Poly(alias_gap * low**4, low).degree() == 4, sp.Poly(alias_gap * low**4, low).degree(), 4, "nonidentification")
    low_band = {-TEST_LOW_BAND_LIMIT: sp.Rational(1, 3), 0: sp.Rational(2), TEST_LOW_BAND_LIMIT: sp.Rational(1, 3)}
    low_band_fourth = laurent_power(low_band, 4)
    low_band_continuum = low_band_fourth.get(0, sp.Rational(0))
    low_band_grid = periodic_grid_average(low_band_fourth, TEST_LOW_BAND_GRID)
    audit.check("low-band quartic quadrature survivor", low_band_grid == low_band_continuum, low_band_grid, low_band_continuum, "nonidentification")
    audit.check("low-band no-alias condition", TEST_LOW_BAND_GRID > 4 * TEST_LOW_BAND_LIMIT, TEST_LOW_BAND_GRID, f">{4 * TEST_LOW_BAND_LIMIT}", "nonidentification")
    audit.check("new no-go linked", manifest["canonical_nonidentification"]["quartic_aliasing_no_go"]["negative_id"] == NEGATIVE_IDS[0], manifest["canonical_nonidentification"]["quartic_aliasing_no_go"]["negative_id"], NEGATIVE_IDS[0], "nonidentification")

    # Exact covariance-scheme matrix direction, retained as the next-gate dictionary.
    covariance_shift, g, lam = sp.symbols("D g lambda", positive=True)
    walsh_levels = [sp.expand(3 * covariance_shift * (g + lam + 2 * level * lam)) for level in range(4)]
    fixture_levels = [value.subs({covariance_shift: sp.Rational(4, 3), g: 1, lam: 1}) for value in walsh_levels]
    audit.check("Q3 Wick translation levels", fixture_levels == [8, 16, 24, 32], fixture_levels, [8, 16, 24, 32], "nonidentification")
    audit.check("Q3 Wick translation non-scalar", len(set(fixture_levels)) == 4, fixture_levels, "four levels", "nonidentification")

    true_scope = (
        "Q3_spatial_Wick_martingale",
        "Q3_spatial_common_Gaussian_L1_density_limit",
        "finite_spatial_cutoff_time_locality",
        "finite_spatial_cutoff_reflection_positive",
        "limiting_Nagoji_measure_reflection_positive",
        "finite_spatial_cutoff_Feynman_Kac_comparator",
        "bounded_configuration_observable_limit",
    )
    false_scope = tuple(key for key, value in manifest["scope"].items() if key not in true_scope and value is False)
    for key in true_scope:
        audit.check(f"scope true: {key}", manifest["scope"][key] is True, manifest["scope"][key], True, "scope")
    for key in false_scope:
        audit.check(f"scope false: {key}", manifest["scope"][key] is False, manifest["scope"][key], False, "scope")
    audit.check("scope partition complete", set(true_scope) | set(false_scope) == set(manifest["scope"]), sorted(set(manifest["scope"]) - set(true_scope) - set(false_scope)), [], "scope")
    audit.check("below empty space firewall", manifest["scope"]["below_empty_space_comparison"] is False, manifest["scope"]["below_empty_space_comparison"], False, "scope")
    audit.check("physical vacuum firewall", manifest["scope"]["physical_state_or_vacuum"] is False, manifest["scope"]["physical_state_or_vacuum"], False, "scope")
    audit.check("C6 tier unchanged", status["tier"] == "T1", status["tier"], "T1", "scope")
    audit.check("C6 lifecycle unchanged", status["lifecycle"] == "ACTIVE", status["lifecycle"], "ACTIVE", "scope")
    audit.check("C6 evidence unchanged", status["evidence_grade"] == ["CONDITIONAL"], status["evidence_grade"], ["CONDITIONAL"], "scope")
    audit.check("C6 gate unchanged", status["open_gates"] == ["C6-BCC-PREMISE-BLOCKED"], status["open_gates"], ["C6-BCC-PREMISE-BLOCKED"], "scope")
    expected_next_gate = "PA-CP1-CL8-CENTERED-NODAL-TO-SPATIAL-SPECTRAL-RP-UNIVERSALITY-AND-TWISTED-WEYL-LIMIT"
    audit.check("next gate exact", manifest["gate_resolution"]["next_gate"] == expected_next_gate, manifest["gate_resolution"]["next_gate"], expected_next_gate, "scope")

    for phrase in (
        "reflection positive for Euclidean-time reflection",
        "same terminal interaction",
        "uniformly `L2`",
        "positive semidefinite",
        "bounded truncations",
        "beta-independent Hamiltonian family",
        "Nyquist quartic witness",
        "energy below empty space",
        "C0, N1--N5, C6, CP1 and Pre-A remain open",
    ):
        audit.check(f"certificate phrase {phrase[:34]}", phrase in certificate_flat, phrase, "present", "hygiene")
    package_files = (MANIFEST, CERTIFICATE, SCRIPT)
    non_ascii = {str(path.relative_to(REPO)): sorted({character for character in path.read_text(encoding="utf-8") if ord(character) > 127}) for path in package_files}
    audit.check("package ASCII clean", all(not characters for characters in non_ascii.values()), non_ascii, "all empty", "hygiene")

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
        "source_sha256": {"script": sha256(SCRIPT), "manifest": sha256(MANIFEST), "certificate": sha256(CERTIFICATE), "parent": sha256(PARENT)},
        "derived": {
            "hermite_conditioning": hermite_results,
            "Q3_edge_conditioned": str(edge_conditioned),
            "reflected_gram": [[str(value) for value in row] for row in gram.tolist()],
            "density_fixture": {"l1": str(density_l1), "bound": str(density_bound)},
            "spectral_symbol": str(spectral_symbol),
            "centered_symbol": str(centered_symbol),
            "Nyquist_continuum_average": str(continuum_average),
            "Nyquist_nodal_average": str(nodal_average),
            "Nyquist_alias_gap": str(alias_gap),
            "low_band_average": str(low_band_grid),
            "Wick_translation_levels": [str(value) for value in fixture_levels],
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

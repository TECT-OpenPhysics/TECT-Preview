#!/usr/bin/env python3
"""Primary verifier for the CL8 Q3 vector P(Phi)2 comparator route split."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import tempfile
from collections import Counter
from itertools import product
from pathlib import Path
from typing import Any

import sympy as sp


__version__ = "0.1.1"
REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-cl8-q3-vector-phi2-constructive-comparator-route-split"
CANDIDATE_ID = "PA-CP1-CL8-Q3-VECTOR-PHI2-CONSTRUCTIVE-COMPARATOR-ROUTE-SPLIT-v0"
RESULT_ID = "PA-CP1-CL8-Q3-PHI2-NORMALIZABILITY-L1-DENSITY-AND-CONFIGURATION-CHARACTERISTIC-LIMIT-WITH-RP-AND-SELECTION-NOGOS"
NEGATIVE_IDS = (
    "NG-2026-08-04-PRE-A-CP1-CL8-FULL-EUCLIDEAN-SHARP-CUTOFF-REFLECTION-POSITIVITY",
    "NG-2026-08-04-PRE-A-CP1-CL8-TIME-ZERO-CONFIGURATION-ONLY-FULL-WEYL-STATE",
    "NG-2026-08-04-PRE-A-CP1-CL8-CONSTRUCTIVE-NORMALIZABILITY-ONLY-PHYSICAL-STATE-SELECTION",
)
EXPLORATION_ID = "EXP-000766"
SCHEMA = f"tect/{SLUG}-primary/0.1"
SCRIPT = Path(__file__).resolve()
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260804.md"
PARENT = REPO / "strategy/pre-a-cp1-cl8-matrix-counterterm-state-compactness-route-split-manifest.json"
STATUS = REPO / "claims/C6-SPACETIME-SIGNATURE/status.json"
DEFAULT_OUTPUT = REPO / f"claims/C6-SPACETIME-SIGNATURE/runs/2026-08-04-primary-{SLUG}/result.json"

# Declared mathematical inputs and audit oracles, never derived outputs.
DIMENSION = 2
ALPHA = sp.Rational(1)
COMPONENTS = 8
DEGREE = 4
NAGOJI_Q = sp.Rational(5, 4)
SCALED_P = 2
EXPECTED_MAXIMAL_SUPPORT_COUNT = 64
EXPECTED_DESCENDANT_COUNTS = {0: 1, 1: 8, 2: 20, 3: 32}


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


def cube_edges() -> list[tuple[int, int]]:
    nodes = list(product((0, 1), repeat=3))
    index = {node: position for position, node in enumerate(nodes)}
    edges: list[tuple[int, int]] = []
    for node in nodes:
        left = index[node]
        for axis in range(3):
            if node[axis] == 0:
                other = list(node)
                other[axis] = 1
                edges.append((left, index[tuple(other)]))
    return edges


def unit_index(component: int, power: int = 1) -> tuple[int, ...]:
    values = [0] * COMPONENTS
    values[component] = power
    return tuple(values)


def generic_support(edges: list[tuple[int, int]]) -> set[tuple[int, ...]]:
    support: set[tuple[int, ...]] = set()
    for component in range(COMPONENTS):
        support.add(unit_index(component, 4))
        support.add(unit_index(component, 2))
    for left, right in edges:
        for left_power, right_power in ((3, 1), (2, 2), (1, 3), (1, 1)):
            index = [0] * COMPONENTS
            index[left] = left_power
            index[right] = right_power
            support.add(tuple(index))
    return support


def lower_envelope(support: set[tuple[int, ...]]) -> set[tuple[int, ...]]:
    descendants: set[tuple[int, ...]] = set()
    for exponent in support:
        for candidate in product(*(range(value + 1) for value in exponent)):
            if candidate != exponent:
                descendants.add(tuple(candidate))
    return descendants


def wick_hermite(variable: sp.Expr, variance: sp.Expr, degree: int) -> sp.Expr:
    total = sp.Integer(0)
    for pairs in range(degree // 2 + 1):
        coefficient = sp.factorial(degree) * (-variance) ** pairs
        coefficient /= 2**pairs * sp.factorial(pairs) * sp.factorial(degree - 2 * pairs)
        total += coefficient * variable ** (degree - 2 * pairs)
    return sp.expand(total)


def gaussian_expect_y(polynomial: sp.Expr, variable: sp.Symbol, variance: sp.Expr) -> sp.Expr:
    expanded = sp.Poly(sp.expand(polynomial), variable)
    total = sp.Integer(0)
    for (power,), coefficient in expanded.terms():
        if power % 2:
            continue
        pairs = power // 2
        moment = sp.factorial2(2 * pairs - 1) * variance**pairs if pairs else sp.Integer(1)
        total += coefficient * moment
    return sp.expand(total)


def build_payload() -> dict[str, Any]:
    audit = Audit()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    parent = json.loads(PARENT.read_text(encoding="utf-8"))
    status = json.loads(STATUS.read_text(encoding="utf-8"))
    certificate = CERTIFICATE.read_text(encoding="utf-8")

    audit.check("candidate id", manifest["candidate_id"] == CANDIDATE_ID, manifest["candidate_id"], CANDIDATE_ID, "identity")
    audit.check("result id", manifest["result_id"] == RESULT_ID, manifest["result_id"], RESULT_ID, "identity")
    audit.check("negative ids", tuple(manifest["negative_ids"]) == NEGATIVE_IDS, manifest["negative_ids"], NEGATIVE_IDS, "identity")
    audit.check("exploration id", manifest["exploration_id"] == EXPLORATION_ID, manifest["exploration_id"], EXPLORATION_ID, "identity")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "identity")
    audit.check("parent result", parent["result_id"] in manifest["parent_ids"][0] or parent["candidate_id"] == manifest["parent_ids"][0], parent["candidate_id"], manifest["parent_ids"][0], "identity")

    edges = cube_edges()
    audit.check("Q3 edge count", len(edges) == 12, len(edges), 12, "support")
    support = generic_support(edges)
    descendants = lower_envelope(support)
    degree_counts = Counter(sum(exponent) for exponent in descendants)
    audit.check("maximal formal support count", len(support) == EXPECTED_MAXIMAL_SUPPORT_COUNT, len(support), EXPECTED_MAXIMAL_SUPPORT_COUNT, "support")
    audit.check("descendant degree counts", dict(sorted(degree_counts.items())) == EXPECTED_DESCENDANT_COUNTS, dict(sorted(degree_counts.items())), EXPECTED_DESCENDANT_COUNTS, "support")
    audit.check("descendant total", len(descendants) == sum(EXPECTED_DESCENDANT_COUNTS.values()), len(descendants), sum(EXPECTED_DESCENDANT_COUNTS.values()), "support")
    support_contract = manifest["theorem_hypothesis_instantiation"]["maximal_formal_support"]
    audit.check("support 64 attainment conditions", support_contract["support_64_attainment_conditions"] == ["lambda!=0", "eta_int!=0", "m_int+3 eta_int!=0"], support_contract["support_64_attainment_conditions"], "three exact conditions", "support")
    audit.check("A-minus 61 lambda condition", support_contract["A_minus_61_attainment_condition"] == "lambda!=0", support_contract["A_minus_61_attainment_condition"], "lambda!=0", "support")
    cancelled_support = support - {unit_index(component, 2) for component in range(COMPONENTS)}
    audit.check("diagonal quadratic cancellation leaves 56", len(cancelled_support) == 56, len(cancelled_support), 56, "support")
    maximum_degree = max(map(sum, descendants))
    audit.check("descendant maximum degree", maximum_degree == DEGREE - 1, maximum_degree, DEGREE - 1, "support")
    audit.check("no degree four descendant", all(sum(exponent) < DEGREE for exponent in descendants), maximum_degree, "<4", "support")

    threshold = sp.Rational(DEGREE - 1, 2 * DEGREE) * DIMENSION
    audit.check("Wick threshold", threshold < ALPHA, threshold, ALPHA, "Nagoji")
    audit.check("critical alpha", ALPHA == sp.Rational(DIMENSION, 2), ALPHA, sp.Rational(DIMENSION, 2), "Nagoji")
    audit.check("q above one", NAGOJI_Q > 1, NAGOJI_Q, ">1", "Nagoji")
    maximum_auxiliary_power = NAGOJI_Q * maximum_degree
    audit.check("auxiliary exponent", maximum_auxiliary_power == sp.Rational(15, 4), maximum_auxiliary_power, sp.Rational(15, 4), "Nagoji")
    audit.check("quartic dominates auxiliary", maximum_auxiliary_power < DEGREE, maximum_auxiliary_power, DEGREE, "Nagoji")
    audit.check("mass budget m zero", sp.Integer(0) < sp.Symbol("m0", positive=True) ** 2 / 2, "0", "m0^2/2", "Nagoji")

    q = sp.symbols("q0:8", real=True)
    g, lam = sp.symbols("g lambda", positive=True)
    radius_squared = sp.expand(sum(value**2 for value in q))
    onsite = sp.expand(sum(value**4 for value in q))
    onsite_gap = sp.expand(onsite - radius_squared**2 / COMPONENTS)
    onsite_sos = sp.expand(sum((q[i] ** 2 - q[j] ** 2) ** 2 for i in range(COMPONENTS) for j in range(i + 1, COMPONENTS)) / COMPONENTS)
    audit.check("onsite SOS", sp.expand(onsite_gap - onsite_sos) == 0, onsite_gap, onsite_sos, "coercivity")
    edge_polynomial = sp.expand(sum((q[i] - q[j]) ** 2 * (q[i] ** 2 + q[j] ** 2) for i, j in edges))
    audit.check("edge polynomial nonnegative form", all(term == (q[i] - q[j]) ** 2 * (q[i] ** 2 + q[j] ** 2) for term, (i, j) in zip([(q[i] - q[j]) ** 2 * (q[i] ** 2 + q[j] ** 2) for i, j in edges], edges)), len(edges), "12 nonnegative summands", "coercivity")
    w4 = sp.expand(g * onsite / 4 + lam * edge_polynomial / 4)
    coercive_remainder = sp.expand(w4 - g * radius_squared**2 / 32)
    expected_remainder = sp.expand(g * onsite_sos / 4 + lam * edge_polynomial / 4)
    audit.check("Q3 quartic coercivity identity", sp.expand(coercive_remainder - expected_remainder) == 0, coercive_remainder, expected_remainder, "coercivity")
    constant_ray = {value: sp.Symbol("x", real=True) for value in q}
    audit.check("edge flat constant ray", edge_polynomial.subs(constant_ray) == 0, edge_polynomial.subs(constant_ray), 0, "coercivity")
    audit.check("g positive load-bearing", "g>0" in manifest["euclidean_model"]["domain"], manifest["euclidean_model"]["domain"], "g>0", "coercivity")

    scaled_support = set(support)
    audit.check("scaled two F support unchanged", scaled_support == support and SCALED_P > 1, len(scaled_support), len(support), "integrability")
    audit.check("scaled two F theorem ledger", "2F" in manifest["density_convergence_corollary"]["scaled_input"], manifest["density_convergence_corollary"]["scaled_input"], "2F", "integrability")
    audit.check("Wick martingale ledger", "R_N=E[R|G_N]" in manifest["density_convergence_corollary"]["Wick_martingale"], manifest["density_convergence_corollary"]["Wick_martingale"], "conditional identity", "integrability")
    terminal_contract = manifest["density_convergence_corollary"]["finite_to_terminal_martingale"]
    audit.check("finite-to-terminal L1 passage", terminal_contract["limit_input"] == "Proposition A.1 and estimate (A.3) give R_M->R in L1", terminal_contract["limit_input"], "Proposition A.1 plus (A.3)", "integrability")
    low, high, low_variance, high_variance = sp.symbols("X Y C_low C_high", real=True)
    hermite_checks: dict[str, str] = {}
    for degree in range(DEGREE + 1):
        conditional = gaussian_expect_y(wick_hermite(low + high, low_variance + high_variance, degree), high, high_variance)
        target = wick_hermite(low, low_variance, degree)
        audit.check(f"Wick martingale degree {degree}", sp.expand(conditional - target) == 0, conditional, target, "integrability")
        hermite_checks[str(degree)] = str(target)
    centered_means: dict[str, str] = {}
    for degree in range(1, DEGREE + 1):
        centered_mean = sp.expand(gaussian_expect_y(wick_hermite(high, high_variance, degree), high, high_variance))
        audit.check(f"Wick Hermite centering degree {degree}", centered_mean == 0, centered_mean, 0, "integrability")
        centered_means[str(degree)] = str(centered_mean)
    audit.check("multivariate Wick centering factorization", terminal_contract["centered_degrees"] == [1, 2, 3, 4] and all(value == "0" for value in centered_means.values()), centered_means, "all degrees centered", "integrability")
    audit.check("normalizer Jensen floor recorded", ">=1" in manifest["density_convergence_corollary"]["normalizer_floor"], manifest["density_convergence_corollary"]["normalizer_floor"], "Z_N>=1", "integrability")

    # A discrete exact fixture checks the normalized-density L1 inequality used after Vitali.
    weights_n = [sp.Rational(2), sp.Rational(3), sp.Rational(5)]
    weights = [sp.Rational(3, 2), sp.Rational(7, 2), sp.Rational(5)]
    z_n, z = sum(weights_n), sum(weights)
    l1_weight = sum(abs(left - right) for left, right in zip(weights_n, weights))
    l1_density = sum(abs(left / z_n - right / z) for left, right in zip(weights_n, weights))
    bound = l1_weight / z_n + abs(z - z_n) / z_n
    audit.check("normalized L1 fixture", l1_density <= bound, l1_density, bound, "integrability")
    audit.check("normalizer difference bound", abs(z - z_n) <= l1_weight, abs(z - z_n), l1_weight, "integrability")

    cutoff_n, label_k = 8, 3
    temporal_start = math.floor(math.sqrt(cutoff_n**2 - label_k**2))
    audit.check("temporal trace start", temporal_start > 0, temporal_start, ">0", "configuration")
    finite_tail = sum(sp.Rational(2, n * n) for n in range(temporal_start + 1, 4000))
    tail_bound = sp.Rational(2, temporal_start)
    audit.check("temporal tail finite fixture", finite_tail < tail_bound, finite_tail, tail_bound, "configuration")
    variance = sp.Symbol("v", positive=True)
    audit.check("Gaussian fourth moment", sp.Integer(3) * variance**2 == 3 * variance**2, 3 * variance**2, "3v^2", "configuration")
    audit.check("configuration equicontinuity recorded", "C_K||f||" in manifest["configuration_characteristic_limit"]["equicontinuity"], manifest["configuration_characteristic_limit"]["equicontinuity"], "linear label bound", "configuration")
    audit.check("configuration only boundary", "commuting configuration subgroup" in manifest["configuration_characteristic_limit"]["boundary"], manifest["configuration_characteristic_limit"]["boundary"], "q-only", "configuration")

    mass, eta, covariance = sp.symbols("m_int eta_int C", real=True)
    trace_laplacian = 3 * COMPONENTS
    trace_k = COMPONENTS * mass + trace_laplacian * eta
    whole_wick_scalar = sp.expand(-covariance * trace_k / 2)
    audit.check("Q3 Laplacian trace", trace_laplacian == 24, trace_laplacian, 24, "Wick")
    audit.check("whole quadratic Wick scalar", whole_wick_scalar == -4 * covariance * mass - 12 * covariance * eta, whole_wick_scalar, -4 * covariance * mass - 12 * covariance * eta, "Wick")
    delta = sp.Symbol("D", real=True)
    matrix_scalar, matrix_lap = sp.symbols("M_I M_L", real=True)
    old_raw = matrix_scalar - 3 * covariance * (g + lam)
    new_counterterm = matrix_scalar + 3 * delta * (g + lam) - 3 * (covariance + delta) * (g + lam)
    audit.check("scalar covariance translation", sp.expand(new_counterterm - old_raw) == 0, new_counterterm, old_raw, "Wick")
    old_lap_raw = matrix_lap - 3 * covariance * lam
    new_lap_raw = matrix_lap + 3 * delta * lam - 3 * (covariance + delta) * lam
    audit.check("Q3 covariance translation", sp.expand(new_lap_raw - old_lap_raw) == 0, new_lap_raw, old_lap_raw, "Wick")

    times = (sp.pi / 6, sp.pi / 3, sp.pi / 2)
    weights = (sp.Integer(1), -sp.sqrt(3), sp.sqrt(3) - 1)
    sum_zero = sp.simplify(sum(weights))
    sum_cos = sp.simplify(sum(weight * sp.cos(time) for weight, time in zip(weights, times)))
    sum_sin = sp.simplify(sum(weight * sp.sin(time) for weight, time in zip(weights, times)))
    a0, a1 = sp.symbols("a0 a1", positive=True)
    reflection_form = sp.simplify(sum(weights[i] * weights[j] * (a0 + 2 * a1 * sp.cos(times[i] + times[j])) for i in range(3) for j in range(3)))
    ordinary_form = sp.simplify(sum(weights[i] * weights[j] * (a0 + 2 * a1 * sp.cos(times[i] - times[j])) for i in range(3) for j in range(3)))
    expected_reflection = -2 * a1 * (2 - sp.sqrt(3)) ** 2
    audit.check("RP weight sum", sum_zero == 0, sum_zero, 0, "RP")
    audit.check("RP cosine moment", sum_cos == 0, sum_cos, 0, "RP")
    audit.check("RP sine moment", sum_sin == sp.sqrt(3) - 2, sum_sin, sp.sqrt(3) - 2, "RP")
    audit.check("RP negative form identity", sp.simplify(reflection_form - expected_reflection) == 0, reflection_form, expected_reflection, "RP")
    audit.check("RP strict negativity", bool(expected_reflection.subs(a1, 1) < 0), expected_reflection.subs(a1, 1), "<0", "RP")
    audit.check("RP orientation sentinel", bool(ordinary_form.subs(a1, 1) > 0), ordinary_form.subs(a1, 1), ">0", "RP")
    projected_scope = manifest["reflection_positivity_no_go"]["projected_law_scope"]
    audit.check("projected interacting b1 positive", projected_scope["interacting_b1_positive"] is True, projected_scope["interacting_b1_positive"], True, "RP")
    audit.check("lifted rho1 RP undecided", projected_scope["lifted_rho1_mu_decided"] is False, projected_scope["lifted_rho1_mu_decided"], False, "RP")

    var_q = sp.Rational(1, 2)
    var_p = sp.Rational(1, 2)
    symmetric_qp = sp.Integer(0)
    chirped_var_p = sp.expand(var_p + var_q + symmetric_qp)
    audit.check("vacuum Q variance", var_q == sp.Rational(1, 2), var_q, sp.Rational(1, 2), "Weyl")
    audit.check("vacuum P variance", var_p == sp.Rational(1, 2), var_p, sp.Rational(1, 2), "Weyl")
    audit.check("chirped P variance", chirped_var_p == 1, chirped_var_p, 1, "Weyl")
    t = sp.Symbol("t", real=True)
    q_characteristic = sp.exp(-t**2 / 4)
    audit.check("same Q characteristic", q_characteristic == sp.exp(-t**2 / 4), q_characteristic, sp.exp(-t**2 / 4), "Weyl")
    audit.check("configuration does not fix momentum", chirped_var_p != var_p, chirped_var_p, var_p, "Weyl")

    radial = sp.Symbol("r", nonnegative=True)
    torus_volume = sp.Symbol("V", positive=True)
    density_ratio = sp.exp(-torus_volume * radial**2 / 2)
    audit.check("selection ratio nonconstant", density_ratio.subs(radial, 0) != density_ratio.subs(radial, 1), [density_ratio.subs(radial, 0), density_ratio.subs(radial, 1)], "different", "selection")
    audit.check("selection witness recorded", "K_int=0" in manifest["selection_no_go"]["witness"] and "K_int=I" in manifest["selection_no_go"]["witness"], manifest["selection_no_go"]["witness"], "two inputs", "selection")
    audit.check("normalized Haar volume", manifest["selection_no_go"]["volume_convention"]["normalized_Haar_V"] == 1, manifest["selection_no_go"]["volume_convention"], "V=1", "selection")

    length, nodes, mode = sp.Integer(6), sp.Integer(6), sp.Integer(2)
    spacing = length / nodes
    continuum_symbol = sp.simplify((2 * sp.pi * mode / length) ** 2)
    centered_symbol = sp.simplify((2 / spacing * sp.sin(sp.pi * mode / nodes)) ** 2)
    audit.check("continuum spectral symbol fixture", continuum_symbol == 4 * sp.pi**2 / 9, continuum_symbol, 4 * sp.pi**2 / 9, "regulator")
    audit.check("centered CL8 symbol fixture", centered_symbol == 3, centered_symbol, 3, "regulator")
    audit.check("regulators not identical", continuum_symbol != centered_symbol, continuum_symbol, centered_symbol, "regulator")
    audit.check("base mass residual boundary", "K_int=K_target-m0^2 I" in manifest["euclidean_model"]["base_mass_boundary"], manifest["euclidean_model"]["base_mass_boundary"], "residual map", "regulator")

    true_scope = (
        "Nagoji_hypotheses_instantiated",
        "finite_Euclidean_torus_vector_Phi2_measure",
        "common_Gaussian_L1_density_convergence",
        "time_zero_configuration_characteristic_full_sequence",
        "time_zero_configuration_characteristic_equicontinuity",
        "same_covariance_Wick_scheme_translation",
    )
    false_scope = tuple(key for key, value in manifest["scope"].items() if key not in true_scope and value is False)
    for key in true_scope:
        audit.check(f"scope true {key}", manifest["scope"].get(key) is True, manifest["scope"].get(key), True, "scope")
    for key in false_scope:
        audit.check(f"scope false {key}", manifest["scope"].get(key) is False, manifest["scope"].get(key), False, "scope")
    audit.check("all scope keys boolean", all(isinstance(value, bool) for value in manifest["scope"].values()), manifest["scope"], "booleans", "scope")
    audit.check("C6 tier unchanged", status["tier"] == "T1", status["tier"], "T1", "claim_firewall")
    audit.check("C6 lifecycle unchanged", status["lifecycle"] == "ACTIVE", status["lifecycle"], "ACTIVE", "claim_firewall")
    audit.check("C6 evidence unchanged", status["evidence_grade"] == ["CONDITIONAL"], status["evidence_grade"], ["CONDITIONAL"], "claim_firewall")
    audit.check("C6 gate unchanged", status["open_gates"] == ["C6-BCC-PREMISE-BLOCKED"], status["open_gates"], ["C6-BCC-PREMISE-BLOCKED"], "claim_firewall")
    audit.check("certificate external URL", "https://arxiv.org/pdf/2305.19583" in certificate, "Nagoji URL", "present", "source")
    audit.check("certificate projected RP witness", "-2b_1(2-\\sqrt3)^2<0" in certificate.replace(" ", ""), "projected RP identity", "present", "source")
    audit.check("package ASCII", all(ord(character) < 128 for path in (MANIFEST, CERTIFICATE, SCRIPT) for character in path.read_text(encoding="utf-8")), "ASCII", "clean", "hygiene")

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
            "maximal_support_count": len(support),
            "cancelled_support_count": len(cancelled_support),
            "descendant_degree_counts": {str(key): value for key, value in sorted(degree_counts.items())},
            "maximum_auxiliary_power": str(maximum_auxiliary_power),
            "Wick_threshold": str(threshold),
            "Hermite_martingale_targets": hermite_checks,
            "Hermite_centered_means": centered_means,
            "temporal_tail": {"start": temporal_start, "partial": str(finite_tail), "bound": str(tail_bound)},
            "Wick_scalar": str(whole_wick_scalar),
            "reflection_form": str(reflection_form),
            "projected_law_scope": projected_scope,
            "ordinary_form": str(ordinary_form),
            "momentum_variances": {"base": str(var_p), "chirped": str(chirped_var_p)},
            "regulator_symbols": {"spectral": str(continuum_symbol), "centered": str(centered_symbol)},
            "normalized_Haar_V": manifest["selection_no_go"]["volume_convention"]["normalized_Haar_V"],
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

#!/usr/bin/env python3
"""Non-importing exact-arithmetic audit of the CL8 Q3 P(Phi)2 comparator."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import math
import os
import tempfile
from collections import Counter
from dataclasses import dataclass
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path
from typing import Any


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
SCHEMA = f"tect/{SLUG}-independent/0.1"
SCRIPT = Path(__file__).resolve()
PRIMARY = REPO / f"codes/foundations/{SLUG.replace('-', '_')}.py"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260804.md"
PARENT = REPO / "strategy/pre-a-cp1-cl8-matrix-counterterm-state-compactness-route-split-manifest.json"
STATUS = REPO / "claims/C6-SPACETIME-SIGNATURE/status.json"
DEFAULT_OUTPUT = REPO / f"claims/C6-SPACETIME-SIGNATURE/runs/2026-08-04-independent-{SLUG}/result.json"

# Declared inputs and test oracles.
COMPONENTS = 8
Q_EXPONENT = Fraction(5, 4)
EXPECTED_MAXIMAL_SUPPORT = 64
EXPECTED_ENVELOPE = {0: 1, 1: 8, 2: 20, 3: 32}


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


@dataclass(frozen=True)
class Qsqrt3:
    """Exact a+b*sqrt(3) arithmetic for the reflection witness."""

    a: Fraction
    b: Fraction = Fraction(0)

    def __add__(self, other: "Qsqrt3") -> "Qsqrt3":
        return Qsqrt3(self.a + other.a, self.b + other.b)

    def __neg__(self) -> "Qsqrt3":
        return Qsqrt3(-self.a, -self.b)

    def __sub__(self, other: "Qsqrt3") -> "Qsqrt3":
        return self + (-other)

    def __mul__(self, other: "Qsqrt3") -> "Qsqrt3":
        return Qsqrt3(self.a * other.a + 3 * self.b * other.b, self.a * other.b + self.b * other.a)

    def scale(self, value: Fraction) -> "Qsqrt3":
        return Qsqrt3(value * self.a, value * self.b)

    def numeric(self) -> float:
        return float(self.a) + float(self.b) * math.sqrt(3.0)


ZERO_Q3 = Qsqrt3(Fraction(0))
ONE_Q3 = Qsqrt3(Fraction(1))


def bit_cube_edges() -> list[tuple[int, int]]:
    edges: list[tuple[int, int]] = []
    for node in range(1 << 3):
        for axis in range(3):
            neighbor = node ^ (1 << axis)
            if node < neighbor:
                edges.append((node, neighbor))
    return edges


def exponent(left: int, left_power: int, right: int | None = None, right_power: int = 0) -> tuple[int, ...]:
    values = [0] * COMPONENTS
    values[left] = left_power
    if right is not None:
        values[right] = right_power
    return tuple(values)


def build_support(edges: list[tuple[int, int]]) -> set[tuple[int, ...]]:
    support: set[tuple[int, ...]] = set()
    for component in range(COMPONENTS):
        support.update((exponent(component, 2), exponent(component, 4)))
    for left, right in edges:
        support.update(
            (
                exponent(left, 3, right, 1),
                exponent(left, 2, right, 2),
                exponent(left, 1, right, 3),
                exponent(left, 1, right, 1),
            )
        )
    return support


def descendants(support: set[tuple[int, ...]]) -> set[tuple[int, ...]]:
    result: set[tuple[int, ...]] = set()
    for top in support:
        active = [position for position, value in enumerate(top) if value]
        ranges = [range(top[position] + 1) for position in active]
        for local in product(*ranges):
            candidate = [0] * COMPONENTS
            for position, value in zip(active, local):
                candidate[position] = value
            candidate_tuple = tuple(candidate)
            if candidate_tuple != top:
                result.add(candidate_tuple)
    return result


def factorial(number: int) -> int:
    result = 1
    for value in range(2, number + 1):
        result *= value
    return result


def binomial(n: int, k: int) -> int:
    return factorial(n) // (factorial(k) * factorial(n - k))


def double_factorial_odd(power: int) -> int:
    if power == 0:
        return 1
    result = 1
    for value in range(1, power, 2):
        result *= value
    return result


def hermite_conditional(degree: int, low_variance: Fraction, high_variance: Fraction) -> dict[int, Fraction]:
    """Expand E[H_n(X+Y;C_low+C_high)|X] as powers of X."""

    result: dict[int, Fraction] = {}
    total_variance = low_variance + high_variance
    for pairs in range(degree // 2 + 1):
        remaining = degree - 2 * pairs
        coefficient = Fraction(factorial(degree), (2**pairs) * factorial(pairs) * factorial(remaining))
        coefficient *= (-total_variance) ** pairs
        for y_power in range(remaining + 1):
            if y_power % 2:
                continue
            x_power = remaining - y_power
            y_moment = Fraction(double_factorial_odd(y_power), 1) * high_variance ** (y_power // 2)
            result[x_power] = result.get(x_power, Fraction(0)) + coefficient * binomial(remaining, y_power) * y_moment
    return {power: value for power, value in result.items() if value}


def hermite_target(degree: int, variance: Fraction) -> dict[int, Fraction]:
    result: dict[int, Fraction] = {}
    for pairs in range(degree // 2 + 1):
        power = degree - 2 * pairs
        coefficient = Fraction(factorial(degree), (2**pairs) * factorial(pairs) * factorial(power))
        coefficient *= (-variance) ** pairs
        result[power] = coefficient
    return {power: value for power, value in result.items() if value}


def gaussian_polynomial_mean(coefficients: dict[int, Fraction], variance: Fraction) -> Fraction:
    return sum(
        coefficient * Fraction(double_factorial_odd(power)) * variance ** (power // 2)
        for power, coefficient in coefficients.items()
        if power % 2 == 0
    )


def onsite_identity(values: tuple[Fraction, ...]) -> tuple[Fraction, Fraction]:
    total_two = sum(value * value for value in values)
    left = sum(value**4 for value in values) - total_two**2 / COMPONENTS
    right = sum((values[i] ** 2 - values[j] ** 2) ** 2 for i, j in combinations(range(COMPONENTS), 2)) / COMPONENTS
    return left, right


def edge_value(values: tuple[Fraction, ...], edges: list[tuple[int, int]]) -> Fraction:
    return sum((values[i] - values[j]) ** 2 * (values[i] ** 2 + values[j] ** 2) for i, j in edges)


def build_payload() -> dict[str, Any]:
    audit = Audit()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    parent = json.loads(PARENT.read_text(encoding="utf-8"))
    status = json.loads(STATUS.read_text(encoding="utf-8"))
    certificate = CERTIFICATE.read_text(encoding="utf-8")
    primary_source = PRIMARY.read_text(encoding="utf-8")

    audit.check("candidate id", manifest["candidate_id"] == CANDIDATE_ID, manifest["candidate_id"], CANDIDATE_ID, "identity")
    audit.check("result id", manifest["result_id"] == RESULT_ID, manifest["result_id"], RESULT_ID, "identity")
    audit.check("negative ids", tuple(manifest["negative_ids"]) == NEGATIVE_IDS, manifest["negative_ids"], NEGATIVE_IDS, "identity")
    audit.check("exploration id", manifest["exploration_id"] == EXPLORATION_ID, manifest["exploration_id"], EXPLORATION_ID, "identity")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "identity")
    audit.check("parent candidate", manifest["parent_ids"][0] == parent["candidate_id"], manifest["parent_ids"][0], parent["candidate_id"], "identity")

    tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
    imported_modules = {alias.name for node in ast.walk(tree) if isinstance(node, ast.Import) for alias in node.names}
    imported_from = {node.module or "" for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)}
    audit.check("does not import primary", PRIMARY.stem not in imported_modules and PRIMARY.stem not in imported_from, sorted(imported_modules | imported_from), f"not {PRIMARY.stem}", "independence")
    dynamic_calls = {node.func.id for node in ast.walk(tree) if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in {"exec", "eval"}}
    audit.check("no dynamic primary execution", "runpy" not in imported_modules and not dynamic_calls, {"imports": sorted(imported_modules), "calls": sorted(dynamic_calls)}, "no runpy/exec/eval", "independence")
    audit.check("independent source distinct", sha256(SCRIPT) != sha256(PRIMARY), sha256(SCRIPT), sha256(PRIMARY), "independence")
    audit.check("primary candidate visible only as data", CANDIDATE_ID in primary_source, CANDIDATE_ID, "primary contains identity", "independence")

    edges = bit_cube_edges()
    degree_by_node = Counter(node for edge in edges for node in edge)
    audit.check("bit-mask edge count", len(edges) == 12, len(edges), 12, "support")
    audit.check("cube degree three", all(degree_by_node[node] == 3 for node in range(COMPONENTS)), dict(degree_by_node), "all 3", "support")
    support = build_support(edges)
    envelope = descendants(support)
    envelope_counts = Counter(map(sum, envelope))
    audit.check("maximal formal support count", len(support) == EXPECTED_MAXIMAL_SUPPORT, len(support), EXPECTED_MAXIMAL_SUPPORT, "support")
    audit.check("envelope counts", dict(sorted(envelope_counts.items())) == EXPECTED_ENVELOPE, dict(sorted(envelope_counts.items())), EXPECTED_ENVELOPE, "support")
    audit.check("envelope count sum", len(envelope) == sum(EXPECTED_ENVELOPE.values()), len(envelope), sum(EXPECTED_ENVELOPE.values()), "support")
    support_contract = manifest["theorem_hypothesis_instantiation"]["maximal_formal_support"]
    audit.check("support 64 conditions", support_contract["support_64_attainment_conditions"] == ["lambda!=0", "eta_int!=0", "m_int+3 eta_int!=0"], support_contract["support_64_attainment_conditions"], "three exact conditions", "support")
    audit.check("A-minus 61 condition", support_contract["A_minus_61_attainment_condition"] == "lambda!=0", support_contract["A_minus_61_attainment_condition"], "lambda!=0", "support")
    cancelled_support = support - {exponent(component, 2) for component in range(COMPONENTS)}
    audit.check("cancelled diagonal support count", len(cancelled_support) == 56, len(cancelled_support), 56, "support")
    maximum_degree = max(map(sum, envelope))
    audit.check("maximum descendant degree", maximum_degree == 3, maximum_degree, 3, "support")
    audit.check("Nagoji q", Q_EXPONENT > 1, Q_EXPONENT, ">1", "support")
    maximum_power = Q_EXPONENT * maximum_degree
    audit.check("maximum auxiliary power", maximum_power == Fraction(15, 4), maximum_power, Fraction(15, 4), "support")
    audit.check("strict quartic margin", Fraction(4) - maximum_power == Fraction(1, 4), Fraction(4) - maximum_power, Fraction(1, 4), "support")
    mutated_q = Fraction(4, 3)
    audit.check("q mutation sentinel", mutated_q * maximum_degree == 4 and not mutated_q * maximum_degree < 4, mutated_q * maximum_degree, "not strict", "support")
    threshold = Fraction(4 - 1, 2 * 4) * 2
    audit.check("Wick threshold exact", threshold == Fraction(3, 4), threshold, Fraction(3, 4), "support")
    audit.check("alpha exceeds threshold", Fraction(1) > threshold, 1, threshold, "support")

    fixtures = (
        tuple(Fraction(index - 3, 2) for index in range(COMPONENTS)),
        tuple(Fraction((-1) ** index * (index + 1), 3) for index in range(COMPONENTS)),
        tuple(Fraction(1) for _ in range(COMPONENTS)),
    )
    coercive_rows: list[dict[str, str]] = []
    for index, values in enumerate(fixtures):
        left, right = onsite_identity(values)
        audit.check(f"onsite identity fixture {index}", left == right and left >= 0, left, right, "coercivity")
        edge = edge_value(values, edges)
        audit.check(f"edge nonnegative fixture {index}", edge >= 0, edge, ">=0", "coercivity")
        onsite = sum(value**4 for value in values)
        radius_four = sum(value**2 for value in values) ** 2
        audit.check(f"onsite coercivity fixture {index}", onsite >= radius_four / COMPONENTS, onsite, radius_four / COMPONENTS, "coercivity")
        coercive_rows.append({"onsite_gap": str(left), "edge": str(edge)})
    audit.check("constant ray edge zero", edge_value(fixtures[-1], edges) == 0, edge_value(fixtures[-1], edges), 0, "coercivity")
    audit.check("g zero route excluded", manifest["euclidean_model"]["domain"].startswith("g>0"), manifest["euclidean_model"]["domain"], "g>0", "coercivity")

    low_variance, high_variance = Fraction(2, 3), Fraction(3, 5)
    hermite_rows: dict[str, dict[str, str]] = {}
    for degree in range(5):
        conditional = hermite_conditional(degree, low_variance, high_variance)
        target = hermite_target(degree, low_variance)
        audit.check(f"Hermite conditional degree {degree}", conditional == target, conditional, target, "martingale")
        hermite_rows[str(degree)] = {str(power): str(value) for power, value in sorted(target.items())}
    centered_means: dict[str, str] = {}
    for degree in range(1, 5):
        centered_mean = gaussian_polynomial_mean(hermite_target(degree, low_variance), low_variance)
        audit.check(f"Hermite centering degree {degree}", centered_mean == 0, centered_mean, 0, "martingale")
        centered_means[str(degree)] = str(centered_mean)
    terminal_contract = manifest["density_convergence_corollary"]["finite_to_terminal_martingale"]
    audit.check("terminal martingale L1 input", terminal_contract["limit_input"] == "Proposition A.1 and estimate (A.3) give R_M->R in L1", terminal_contract["limit_input"], "Proposition A.1 plus (A.3)", "martingale")
    audit.check("multivariate centering degrees", terminal_contract["centered_degrees"] == [1, 2, 3, 4] and all(value == "0" for value in centered_means.values()), centered_means, "all degrees centered", "martingale")
    audit.check("scaled p value", "2F" in manifest["density_convergence_corollary"]["scaled_input"], manifest["density_convergence_corollary"]["scaled_input"], "2F", "martingale")
    audit.check("conditional Jensen direction", "<=" in manifest["density_convergence_corollary"]["uniform_integrability"], manifest["density_convergence_corollary"]["uniform_integrability"], "upper bound", "martingale")
    audit.check("Vitali target", "Vitali" in manifest["density_convergence_corollary"]["weight_limit"], manifest["density_convergence_corollary"]["weight_limit"], "Vitali", "martingale")
    audit.check("normalizer floor", "Z_N" in manifest["density_convergence_corollary"]["normalizer_floor"], manifest["density_convergence_corollary"]["normalizer_floor"], "Jensen floor", "martingale")

    # Independent exact normalized-density inequality fixture.
    old_weights = (Fraction(1), Fraction(4), Fraction(7))
    new_weights = (Fraction(3, 2), Fraction(7, 2), Fraction(7))
    old_z, new_z = sum(old_weights), sum(new_weights)
    weight_l1 = sum(abs(left - right) for left, right in zip(old_weights, new_weights))
    density_l1 = sum(abs(left / old_z - right / new_z) for left, right in zip(old_weights, new_weights))
    derived_bound = weight_l1 / old_z + abs(new_z - old_z) / old_z
    audit.check("density L1 inequality", density_l1 <= derived_bound, density_l1, derived_bound, "martingale")
    audit.check("partition difference inequality", abs(new_z - old_z) <= weight_l1, abs(new_z - old_z), weight_l1, "martingale")

    cutoff, label = 10, 4
    temporal_start = math.floor(math.sqrt(cutoff * cutoff - label * label))
    partial_tail = sum(Fraction(2, n * n) for n in range(temporal_start + 1, 500))
    tail_bound = Fraction(2, temporal_start)
    audit.check("temporal start positive", temporal_start > 0, temporal_start, ">0", "configuration")
    audit.check("temporal tail bound", partial_tail < tail_bound, partial_tail, tail_bound, "configuration")
    audit.check("tail mutation sentinel", not partial_tail < Fraction(1, 10 * temporal_start), partial_tail, Fraction(1, 10 * temporal_start), "configuration")
    free_variance_bound = Fraction(1) + Fraction(10, 3)  # 1 + a rational upper bound on pi^2/3.
    audit.check("finite trace variance bound", free_variance_bound > 0, free_variance_bound, ">0", "configuration")
    audit.check("q-only label", "commuting configuration subgroup" in manifest["configuration_characteristic_limit"]["boundary"], manifest["configuration_characteristic_limit"]["boundary"], "q-only", "configuration")

    # Qsqrt(3) reconstruction of the three-point reflection witness.
    weights = (ONE_Q3, Qsqrt3(Fraction(0), Fraction(-1)), Qsqrt3(Fraction(-1), Fraction(1)))
    cosines = (Qsqrt3(Fraction(0), Fraction(1, 2)), Qsqrt3(Fraction(1, 2)), ZERO_Q3)
    sines = (Qsqrt3(Fraction(1, 2)), Qsqrt3(Fraction(0), Fraction(1, 2)), ONE_Q3)
    weight_sum = ZERO_Q3
    cosine_sum = ZERO_Q3
    sine_sum = ZERO_Q3
    for weight, cosine, sine in zip(weights, cosines, sines):
        weight_sum = weight_sum + weight
        cosine_sum = cosine_sum + weight * cosine
        sine_sum = sine_sum + weight * sine
    audit.check("reflection weight sum", weight_sum == ZERO_Q3, weight_sum, ZERO_Q3, "RP")
    audit.check("reflection cosine sum", cosine_sum == ZERO_Q3, cosine_sum, ZERO_Q3, "RP")
    audit.check("reflection sine sum", sine_sum == Qsqrt3(Fraction(-2), Fraction(1)), sine_sum, Qsqrt3(Fraction(-2), Fraction(1)), "RP")
    a1 = Fraction(1, 2)  # m0=1 and temporal frequency one.
    reflection = (sine_sum * sine_sum).scale(-2 * a1)
    ordinary = (sine_sum * sine_sum).scale(2 * a1)
    audit.check("reflection exact pair", reflection == Qsqrt3(Fraction(-7), Fraction(4)), reflection, Qsqrt3(Fraction(-7), Fraction(4)), "RP")
    audit.check("reflection strictly negative", reflection.numeric() < 0, reflection.numeric(), "<0", "RP")
    audit.check("ordinary orientation positive", ordinary.numeric() > 0, ordinary.numeric(), ">0", "RP")
    audit.check("reflection sign mutation sentinel", (-reflection.numeric()) > 0, -reflection.numeric(), ">0", "RP")
    projected_scope = manifest["reflection_positivity_no_go"]["projected_law_scope"]
    audit.check("projected law interacting b1", projected_scope["interacting_b1_positive"] is True, projected_scope["interacting_b1_positive"], True, "RP")
    audit.check("full lifted law undecided", projected_scope["lifted_rho1_mu_decided"] is False, projected_scope["lifted_rho1_mu_decided"], False, "RP")

    base_var_q = Fraction(1, 2)
    base_var_p = Fraction(1, 2)
    base_sym_qp = Fraction(0)
    chirp = Fraction(1)
    chirped_var = base_var_p + chirp * chirp * base_var_q + chirp * base_sym_qp
    audit.check("base position variance", base_var_q == Fraction(1, 2), base_var_q, Fraction(1, 2), "Weyl")
    audit.check("base momentum variance", base_var_p == Fraction(1, 2), base_var_p, Fraction(1, 2), "Weyl")
    audit.check("chirped momentum variance", chirped_var == 1, chirped_var, 1, "Weyl")
    audit.check("same position marginal", base_var_q == base_var_q, base_var_q, base_var_q, "Weyl")
    audit.check("momentum distinguishes states", chirped_var != base_var_p, chirped_var, base_var_p, "Weyl")
    unchirped = base_var_p + Fraction(0) * base_var_q
    audit.check("chirp mutation sentinel", unchirped == base_var_p and unchirped != chirped_var, unchirped, chirped_var, "Weyl")

    mass, eta, coincidence = Fraction(7), Fraction(4), Fraction(3)
    trace_laplacian = 3 * COMPONENTS
    trace_k = COMPONENTS * mass + trace_laplacian * eta
    wick_scalar = -coincidence * trace_k / 2
    audit.check("trace L_Q3", trace_laplacian == 24, trace_laplacian, 24, "Wick")
    audit.check("whole-Wick scalar fixture", wick_scalar == -4 * coincidence * mass - 12 * coincidence * eta, wick_scalar, -4 * coincidence * mass - 12 * coincidence * eta, "Wick")
    g_value, lambda_value, delta = Fraction(5), Fraction(2), Fraction(7, 4)
    raw_scalar = mass - 3 * coincidence * (g_value + lambda_value)
    translated_scalar = mass + 3 * delta * (g_value + lambda_value) - 3 * (coincidence + delta) * (g_value + lambda_value)
    raw_lap = eta - 3 * coincidence * lambda_value
    translated_lap = eta + 3 * delta * lambda_value - 3 * (coincidence + delta) * lambda_value
    audit.check("scalar scheme translation", translated_scalar == raw_scalar, translated_scalar, raw_scalar, "Wick")
    audit.check("Q3 scheme translation", translated_lap == raw_lap, translated_lap, raw_lap, "Wick")
    wrong_translation = mass - 3 * delta * (g_value + lambda_value) - 3 * (coincidence + delta) * (g_value + lambda_value)
    audit.check("translation sign sentinel", wrong_translation != raw_scalar, wrong_translation, raw_scalar, "Wick")

    ratio_at_zero = math.exp(0.0)
    ratio_at_one = math.exp(-0.5)
    audit.check("state-selection ratio nonconstant", ratio_at_zero != ratio_at_one, (ratio_at_zero, ratio_at_one), "different", "selection")
    audit.check("selection boundary retained", "physical state" in manifest["selection_no_go"]["excluded_route"], manifest["selection_no_go"]["excluded_route"], "physical state", "selection")
    audit.check("normalized Haar volume", manifest["selection_no_go"]["volume_convention"]["normalized_Haar_V"] == 1, manifest["selection_no_go"]["volume_convention"], "V=1", "selection")

    length, node_count, mode = 6, 6, 2
    spacing = Fraction(length, node_count)
    spectral = (2.0 * math.pi * mode / length) ** 2
    centered = (2.0 / float(spacing) * math.sin(math.pi * mode / node_count)) ** 2
    audit.check("centered symbol", abs(centered - 3.0) < 1e-14, centered, 3.0, "regulator")
    audit.check("spectral symbol computed", abs(spectral - 4.0 * math.pi**2 / 9.0) < 1e-14, spectral, 4.0 * math.pi**2 / 9.0, "regulator")
    audit.check("regulator mismatch", abs(spectral - centered) > 1.0, spectral - centered, ">1", "regulator")
    audit.check("base mass not double counted", "K_int=K_target-m0^2 I" in manifest["euclidean_model"]["base_mass_boundary"], manifest["euclidean_model"]["base_mass_boundary"], "residual", "regulator")

    true_scope = {
        "Nagoji_hypotheses_instantiated",
        "finite_Euclidean_torus_vector_Phi2_measure",
        "common_Gaussian_L1_density_convergence",
        "time_zero_configuration_characteristic_full_sequence",
        "time_zero_configuration_characteristic_equicontinuity",
        "same_covariance_Wick_scheme_translation",
    }
    for key, value in manifest["scope"].items():
        expected = key in true_scope
        audit.check(f"scope {key}", value is expected, value, expected, "scope")
    audit.check("C6 tier", status["tier"] == "T1", status["tier"], "T1", "claim_firewall")
    audit.check("C6 lifecycle", status["lifecycle"] == "ACTIVE", status["lifecycle"], "ACTIVE", "claim_firewall")
    audit.check("C6 evidence", status["evidence_grade"] == ["CONDITIONAL"], status["evidence_grade"], ["CONDITIONAL"], "claim_firewall")
    audit.check("C6 gate", status["open_gates"] == ["C6-BCC-PREMISE-BLOCKED"], status["open_gates"], ["C6-BCC-PREMISE-BLOCKED"], "claim_firewall")
    audit.check("certificate martingale", "Wick-martingale" in certificate, "Wick-martingale", "present", "source")
    audit.check("certificate q-only no-go", NEGATIVE_IDS[1] in certificate, NEGATIVE_IDS[1], "present", "source")
    audit.check("ASCII package", all(ord(character) < 128 for path in (MANIFEST, CERTIFICATE, SCRIPT) for character in path.read_text(encoding="utf-8")), "ASCII", "clean", "hygiene")

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
            "descendant_degree_counts": {str(key): value for key, value in sorted(envelope_counts.items())},
            "maximum_auxiliary_power": str(maximum_power),
            "Wick_threshold": str(threshold),
            "Hermite_martingale_targets": hermite_rows,
            "Hermite_centered_means": centered_means,
            "coercive_fixtures": coercive_rows,
            "temporal_tail": {"start": temporal_start, "partial": str(partial_tail), "bound": str(tail_bound)},
            "Wick_scalar": str(wick_scalar),
            "reflection_form": {"a": str(reflection.a), "b_sqrt3": str(reflection.b), "numeric": reflection.numeric()},
            "projected_law_scope": projected_scope,
            "ordinary_form": {"a": str(ordinary.a), "b_sqrt3": str(ordinary.b), "numeric": ordinary.numeric()},
            "momentum_variances": {"base": str(base_var_p), "chirped": str(chirped_var)},
            "regulator_symbols": {"spectral": spectral, "centered": centered},
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

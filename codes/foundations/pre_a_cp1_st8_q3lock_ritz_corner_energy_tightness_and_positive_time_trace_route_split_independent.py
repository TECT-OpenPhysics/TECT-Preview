#!/usr/bin/env python3
"""Independent stdlib-only verifier for the R-167 v3.5 package."""

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


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-ritz-corner-energy-tightness-and-positive-time-trace-route-split"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260813.md"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-13-independent-{SLUG}/result.json"
FORMAL_PATHS = (
    REPO / "claims/GATES.md",
    REPO / "RESULTS-LEDGER.md",
    REPO / "negative-results/registry.md",
    REPO / "explorations/log.jsonl",
)

CLOSED = (
    "PA-CP1-ST8-Q3LOCK-RITZ-CORNER-PULLBACK-FIXED-WITNESS-AND-LOCAL-ENERGY-TIGHTNESS-STATE-PASSAGE",
    "PA-CP1-ST8-Q3LOCK-POSITIVE-IMAGINARY-TIME-ENERGY-DRESSED-TRACE-CLASS-RITZ-REMOVAL",
)
NEGATIVES = (
    "NG-2026-08-13-PRE-A-ST8-Q3LOCK-DIMENSION-NORMALIZED-SCHATTEN-SMALLNESS-AUTOMATIC-DFFR-TRANSITION-OR-CONTOUR-SMALLNESS",
    "NG-2026-08-13-PRE-A-ST8-Q3LOCK-FIXED-POSITIVE-TIME-ENERGY-DRESSED-TRACE-CONTROL-AUTOMATIC-DFFR-CONTOUR-ENTRY",
    "NG-2026-08-13-PRE-A-ST8-Q3LOCK-FIXED-WITNESS-SEPARATED-RITZ-PULLBACKS-AUTOMATIC-LOCALLY-NORMAL-LIMITS",
    "NG-2026-08-13-PRE-A-ST8-Q3LOCK-RITZ-CORNER-UCP-AUTOMATIC-ASYMPTOTIC-MULTIPLICATIVITY-AND-DYNAMICS-INTERTWINING",
)

# Independently labelled inputs.
AMBIENT_DIMENSION = 4
CORNER_RANK = 2
TEST_MATRIX = (
    (1, 2, 3, 4),
    (2, 0, 5, 6),
    (3, 5, 7, 8),
    (4, 6, 8, 9),
)
DEFECT_DIMENSION = 4
DEFECT_CORNER_RANK = 3
ENERGY_LEVEL = 4
HIGH_AMPLITUDE = Fraction(1, 4)
ENERGY_CUTOFF = 2
H_LEVELS = (0, 0, 2, 4)
FORM_ALPHA = Fraction(1, 4)
FORM_EPSILON = Fraction(1, 8)
TIME_LOG_BASE = 2
KERNEL_RANK = 2
CONTRACTION_SIGNS = (1, -1, 1, -1)
K_LEVELS = (0, 0, 12)
S_SIGNS = (1, -1, 0)
S_FIXTURE_SCOPE = "actual-compatible selfadjoint-contraction fixture with high-sector zero"
EDGE_J = 1
EDGE_N = 4
EDGE_SHARE = 6
POSITIVE_TIME_FACTOR = 2
EDGE_ALPHA_POWER = 2
EDGE_BETA_POWER = 3
SCHATTEN_N = 4
SCHATTEN_M = 8
SCHATTEN_P = 2
SCHATTEN_PENALTY_POWER = 2
TRANSITION_RANK = 2
TRANSITION_AMPLITUDE = 1
TRACE_M = 8
ESCAPE_MASS = Fraction(1, 4)
ESCAPE_INDEX = 8


def normalized_sha256(path: Path) -> str:
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
        self.rows: list[dict[str, str]] = []

    def check(self, name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        self.rows.append(
            {"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)}
        )


def fraction_text(value: Fraction | int) -> str:
    value = Fraction(value)
    return str(value.numerator) if value.denominator == 1 else f"{value.numerator}/{value.denominator}"


def square_decomposition(value: int) -> tuple[int, int]:
    if value < 1:
        raise ValueError("positive integer required")
    outside = 1
    inside = 1
    remaining = value
    prime = 2
    while prime * prime <= remaining:
        exponent = 0
        while remaining % prime == 0:
            exponent += 1
            remaining //= prime
        outside *= prime ** (exponent // 2)
        if exponent % 2:
            inside *= prime
        prime += 1
    if remaining > 1:
        inside *= remaining
    return outside, inside


def sqrt_fraction_text(value: Fraction) -> str:
    value = Fraction(value)
    numerator_out, numerator_in = square_decomposition(value.numerator)
    denominator_out, denominator_in = square_decomposition(value.denominator)
    coefficient = Fraction(numerator_out, denominator_out * denominator_in)
    radical = numerator_in * denominator_in
    if radical == 1:
        return fraction_text(coefficient)
    radical_text = f"sqrt({radical})"
    if coefficient == 1:
        return radical_text
    if coefficient.numerator == 1:
        return f"{radical_text}/{coefficient.denominator}"
    if coefficient.denominator == 1:
        return f"{coefficient.numerator}*{radical_text}"
    return f"{coefficient.numerator}*{radical_text}/{coefficient.denominator}"


def matrix_multiply(left: list[list[Fraction]], right: list[list[Fraction]]) -> list[list[Fraction]]:
    return [
        [sum((left[i][k] * right[k][j] for k in range(len(right))), Fraction(0)) for j in range(len(right[0]))]
        for i in range(len(left))
    ]


def matrix_subtract(left: list[list[Fraction]], right: list[list[Fraction]]) -> list[list[Fraction]]:
    return [[left[i][j] - right[i][j] for j in range(len(left[0]))] for i in range(len(left))]


def matrix_add(left: list[list[Fraction]], right: list[list[Fraction]]) -> list[list[Fraction]]:
    return [[left[i][j] + right[i][j] for j in range(len(left[0]))] for i in range(len(left))]


def matrix_transpose(matrix: list[list[Fraction]]) -> list[list[Fraction]]:
    return [[matrix[j][i] for j in range(len(matrix))] for i in range(len(matrix[0]))]


def matrix_text(matrix: list[list[Fraction]]) -> list[list[str]]:
    return [[fraction_text(value) for value in row] for row in matrix]


def quad_square(rational: Fraction, radical_coefficient: Fraction) -> tuple[Fraction, Fraction]:
    return rational * rational + 2 * radical_coefficient * radical_coefficient, 2 * rational * radical_coefficient


def quad_text(rational: Fraction, radical_coefficient: Fraction) -> str:
    if radical_coefficient == 0:
        return fraction_text(rational)
    denominator = math.lcm(rational.denominator, radical_coefficient.denominator)
    rational_numerator = rational.numerator * (denominator // rational.denominator)
    radical_numerator = radical_coefficient.numerator * (denominator // radical_coefficient.denominator)
    pieces: list[str] = []
    if radical_numerator:
        if radical_numerator == 1:
            pieces.append("sqrt(2)")
        else:
            pieces.append(f"{radical_numerator}*sqrt(2)")
    if rational_numerator:
        pieces.append(str(rational_numerator))
    numerator = "+".join(pieces)
    return numerator if denominator == 1 else f"({numerator})/{denominator}"


def base_two_heat_quadratic(levels: tuple[int, ...], denominator: int) -> tuple[Fraction, Fraction]:
    if TIME_LOG_BASE != 2:
        raise AssertionError("quadratic heat fixture is derived for labelled base two")
    rational = Fraction(0)
    radical_coefficient = Fraction(0)
    for level in levels:
        exponent = Fraction(level, denominator)
        if exponent.denominator == 1:
            rational += Fraction(1, TIME_LOG_BASE**exponent.numerator)
        elif exponent.denominator == 2:
            integer_part = exponent.numerator // exponent.denominator
            radical_coefficient += Fraction(1, TIME_LOG_BASE ** (integer_part + 1))
        else:
            raise AssertionError("fixture exponent must be integral or half-integral")
    return rational, radical_coefficient


def corner_fixture() -> tuple[dict[str, Any], dict[str, Any]]:
    matrix = [[Fraction(value) for value in row] for row in TEST_MATRIX]
    compressed = [row[:CORNER_RANK] for row in matrix[:CORNER_RANK]]
    squared = matrix_multiply(matrix, matrix)
    compressed_squared = matrix_multiply(compressed, compressed)
    defect = matrix_subtract(
        [row[:CORNER_RANK] for row in squared[:CORNER_RANK]],
        compressed_squared,
    )
    determinant = defect[0][0] * defect[1][1] - defect[0][1] * defect[1][0]
    inputs = {
        "ambient_dimension": str(AMBIENT_DIMENSION),
        "corner_rank": str(CORNER_RANK),
        "test_matrix": matrix_text(matrix),
    }
    derived = {
        "compressed_matrix": matrix_text(compressed),
        "unital": CORNER_RANK <= AMBIENT_DIMENSION,
        "parity_compatible": CORNER_RANK % 2 == 0 and AMBIENT_DIMENSION % 2 == 0,
        "kadison_defect": matrix_text(defect),
        "kadison_defect_determinant": fraction_text(determinant),
    }
    return {"inputs": inputs, "derived": derived}, {"defect": defect, "determinant": determinant}


def energy_tightness_fixture() -> tuple[dict[str, Any], dict[str, Fraction]]:
    tail_probability = HIGH_AMPLITUDE * HIGH_AMPLITUDE
    energy = tail_probability * ENERGY_LEVEL
    markov = energy / ENERGY_CUTOFF
    trace_tail_squared = tail_probability * tail_probability + 4 * tail_probability * (1 - tail_probability)
    gentle_squared = 4 * markov
    inputs = {
        "K_diagonal": [str(0), str(ENERGY_LEVEL)],
        "high_amplitude": fraction_text(HIGH_AMPLITUDE),
        "R": str(ENERGY_CUTOFF),
    }
    derived = {
        "energy": fraction_text(energy),
        "tail_probability": fraction_text(tail_probability),
        "energy_markov_bound": fraction_text(markov),
        "trace_tail_norm": sqrt_fraction_text(trace_tail_squared),
        "gentle_bound": sqrt_fraction_text(gentle_squared),
        "strict_gentle_check": trace_tail_squared < gentle_squared,
    }
    return {"inputs": inputs, "derived": derived}, {
        "tail_probability": tail_probability,
        "markov": markov,
        "trace_tail_squared": trace_tail_squared,
        "gentle_squared": gentle_squared,
    }


def compression_defect_fixture() -> tuple[dict[str, Any], dict[str, Any]]:
    dimension = DEFECT_DIMENSION
    rank = DEFECT_CORNER_RANK
    shift = [[Fraction(0) for _ in range(dimension)] for _ in range(dimension)]
    for index in range(dimension - 1):
        shift[index + 1][index] = Fraction(1)
    shift_star = matrix_transpose(shift)
    identity = [[Fraction(int(i == j)) for j in range(dimension)] for i in range(dimension)]
    projection = [[Fraction(int(i == j and i < rank)) for j in range(dimension)] for i in range(dimension)]
    complement = matrix_subtract(identity, projection)
    product_defect = matrix_subtract(
        matrix_multiply(matrix_multiply(matrix_multiply(projection, shift_star), shift), projection),
        matrix_multiply(
            matrix_multiply(matrix_multiply(matrix_multiply(projection, shift_star), projection), shift),
            projection,
        ),
    )
    hamiltonian = matrix_add(shift, shift_star)
    compressed_hamiltonian = matrix_multiply(matrix_multiply(projection, hamiltonian), projection)
    compressed_observable = matrix_multiply(matrix_multiply(projection, shift), projection)
    full_commutator = matrix_subtract(
        matrix_multiply(hamiltonian, shift), matrix_multiply(shift, hamiltonian)
    )
    corner_commutator = matrix_subtract(
        matrix_multiply(compressed_hamiltonian, compressed_observable),
        matrix_multiply(compressed_observable, compressed_hamiltonian),
    )
    generator_coefficient = matrix_subtract(
        matrix_multiply(matrix_multiply(projection, full_commutator), projection), corner_commutator
    )
    generator_cross_boundary = matrix_subtract(
        matrix_multiply(
            matrix_multiply(matrix_multiply(matrix_multiply(projection, hamiltonian), complement), shift),
            projection,
        ),
        matrix_multiply(
            matrix_multiply(matrix_multiply(matrix_multiply(projection, shift), complement), hamiltonian),
            projection,
        ),
    )
    product_diagonal = [product_defect[index][index] for index in range(rank)]
    generator_diagonal = [generator_coefficient[index][index] for index in range(rank)]
    inputs = {"shift_dimension": str(dimension), "cutoff_rank": str(rank)}
    derived = {
        "product_defect_diagonal": [fraction_text(value) for value in product_diagonal],
        "product_defect_rank": str(sum(value != 0 for value in product_diagonal)),
        "product_defect_operator_norm": fraction_text(max(abs(value) for value in product_diagonal)),
        "generator_defect_diagonal": ["0" if value == 0 else ("I" if value == 1 else f"{fraction_text(value)}*I") for value in generator_diagonal],
        "generator_defect_rank": str(sum(value != 0 for value in generator_diagonal)),
        "generator_defect_operator_norm": fraction_text(max(abs(value) for value in generator_diagonal)),
    }
    return {"inputs": inputs, "derived": derived}, {
        "product_defect": product_defect,
        "generator_coefficient": generator_coefficient,
        "generator_cross_boundary": generator_cross_boundary,
    }


def positive_time_fixture() -> tuple[dict[str, Any], dict[str, Any]]:
    weights = tuple(Fraction(1, TIME_LOG_BASE**level) for level in H_LEVELS)
    z0 = sum(weights, Fraction(0))
    z1 = sum((Fraction(level) * weight for level, weight in zip(H_LEVELS, weights)), Fraction(0))
    envelope = tuple(FORM_ALPHA * level + FORM_EPSILON for level in H_LEVELS)
    perturbation = tuple(sign * value for sign, value in zip(CONTRACTION_SIGNS, envelope))
    dressed = tuple(weight * value for weight, value in zip(weights, perturbation))
    trace_norm = sum((abs(value) for value in dressed), Fraction(0))
    trace_bound = FORM_ALPHA * z1 + FORM_EPSILON * z0
    high_trace = sum(
        (envelope[index] * weights[index] for index in range(KERNEL_RANK, len(H_LEVELS))), Fraction(0)
    )
    inputs = {
        "h_diagonal": [str(value) for value in H_LEVELS],
        "alpha": fraction_text(FORM_ALPHA),
        "epsilon": fraction_text(FORM_EPSILON),
        "t": f"log({TIME_LOG_BASE})",
        "kernel_rank": str(KERNEL_RANK),
    }
    derived = {
        "Z0": fraction_text(z0),
        "Z1": fraction_text(z1),
        "trace_norm": fraction_text(trace_norm),
        "trace_bound": fraction_text(trace_bound),
        "low_operator_bound": fraction_text(FORM_EPSILON),
        "low_HS_bound": sqrt_fraction_text(FORM_EPSILON * FORM_EPSILON * KERNEL_RANK),
        "mixed_HS_bound": sqrt_fraction_text(FORM_EPSILON * high_trace),
        "high_trace_bound": fraction_text(high_trace),
        "last_Ritz_tail": fraction_text(abs(dressed[-1])),
    }
    return {"inputs": inputs, "derived": derived}, {
        "weights": weights,
        "envelope": envelope,
        "dressed": dressed,
        "trace_norm": trace_norm,
        "trace_bound": trace_bound,
        "high_trace": high_trace,
    }


def q3_edge_fixture() -> tuple[dict[str, Any], dict[str, Any]]:
    energies: list[int] = []
    for left_level, left_sign in zip(K_LEVELS, S_SIGNS):
        for right_level, right_sign in zip(K_LEVELS, S_SIGNS):
            numerator = left_level + right_level
            if numerator % EDGE_SHARE:
                raise AssertionError("fixture edge energy must be integral")
            energies.append(numerator // EDGE_SHARE + EDGE_J * (1 - left_sign * right_sign))
    weights = [Fraction(1, TIME_LOG_BASE**energy) for energy in energies]
    edge_z0 = sum(weights, Fraction(0))
    edge_z1 = sum((Fraction(energy) * weight for energy, weight in zip(energies, weights)), Fraction(0))
    zk6_rational, zk6_radical = base_two_heat_quadratic(K_LEVELS, EDGE_SHARE)
    if zk6_radical != 0:
        raise AssertionError("labelled t/EDGE_SHARE fixture should be rational")
    zk6 = zk6_rational
    zk6_squared = zk6 * zk6
    zk12_rational, zk12_radical = base_two_heat_quadratic(
        K_LEVELS, POSITIVE_TIME_FACTOR * EDGE_SHARE
    )
    zk12_squared_rational, zk12_squared_radical = quad_square(zk12_rational, zk12_radical)
    alpha = Fraction(1, EDGE_N**EDGE_ALPHA_POWER)
    beta = Fraction(1, EDGE_N**EDGE_BETA_POWER)
    residual = alpha * edge_z1 + beta * edge_z0
    rational_upper_part = beta * zk6_squared
    thermal_prefactor_rational = POSITIVE_TIME_FACTOR * alpha * zk12_squared_rational
    thermal_prefactor_radical = POSITIVE_TIME_FACTOR * alpha * zk12_squared_radical
    if thermal_prefactor_radical != 0:
        raise AssertionError("labelled actual-compatible heat fixture must have a rational prefactor")
    upper_text = (
        f"{fraction_text(rational_upper_part)}+{thermal_prefactor_rational.numerator}/"
        f"({thermal_prefactor_rational.denominator}*E*log({TIME_LOG_BASE}))"
    )
    upper_float = (
        float(rational_upper_part)
        + POSITIVE_TIME_FACTOR
        * float(alpha)
        * (float(zk12_squared_rational) + float(zk12_squared_radical) * math.sqrt(2))
        / (math.e * math.log(TIME_LOG_BASE))
    )
    inputs = {
        "k_diagonal": [str(value) for value in K_LEVELS],
        "s_diagonal": [str(value) for value in S_SIGNS],
        "fixture_scope": S_FIXTURE_SCOPE,
        "J": str(EDGE_J),
        "N": str(EDGE_N),
        "alpha": f"1/N^{EDGE_ALPHA_POWER}",
        "beta_edge": f"1/N^{EDGE_BETA_POWER}",
        "t": f"log({TIME_LOG_BASE})",
    }
    derived = {
        "edge_Z0": fraction_text(edge_z0),
        "edge_Z1": fraction_text(edge_z1),
        "Zk_t_over_6_squared": fraction_text(zk6_squared),
        "Zk_t_over_12_squared": quad_text(zk12_squared_rational, zk12_squared_radical),
        "residual_trace": fraction_text(residual),
        "residual_upper_bound": upper_text,
        "strict_upper_check": float(residual) < upper_float,
    }
    return {"inputs": inputs, "derived": derived}, {
        "energies": energies,
        "edge_z0": edge_z0,
        "edge_z1": edge_z1,
        "zk6_squared": zk6_squared,
        "zk12_squared_float": float(zk12_squared_rational) + float(zk12_squared_radical) * math.sqrt(2),
        "residual": residual,
        "upper_float": upper_float,
        "s_selfadjoint_contraction": all(abs(value) <= 1 for value in S_SIGNS),
        "k_s_commutator_zero": True,
    }


def normalized_schatten_fixture() -> tuple[dict[str, Any], dict[str, Any]]:
    if SCHATTEN_P != 2:
        raise AssertionError("independent radical fixture is intentionally p=2")
    raw_squared = Fraction(TRANSITION_RANK * TRANSITION_AMPLITUDE**SCHATTEN_P)
    normalized_squared = raw_squared / SCHATTEN_M
    inputs = {"N": str(SCHATTEN_N), "m": str(SCHATTEN_M), "p": str(SCHATTEN_P)}
    derived = {
        "relative_alpha": fraction_text(Fraction(1, SCHATTEN_N**SCHATTEN_PENALTY_POWER)),
        "operator_norm": str(TRANSITION_AMPLITUDE),
        "unnormalized_Sp": sqrt_fraction_text(raw_squared),
        "normalized_Sp": sqrt_fraction_text(normalized_squared),
        "fixed_transition": str(TRANSITION_AMPLITUDE),
        "large_m_limit": str(int(not (SCHATTEN_P > 0 and TRANSITION_RANK < math.inf))),
    }
    return {"inputs": inputs, "derived": derived}, {
        "raw_squared": raw_squared,
        "normalized_squared": normalized_squared,
    }


def fixed_positive_time_fixture() -> tuple[dict[str, Any], dict[str, Any]]:
    dressed_trace = Fraction(TRACE_M, TIME_LOG_BASE**TRACE_M)
    inputs = {"m": str(TRACE_M), "t": f"log({TIME_LOG_BASE})"}
    derived = {
        "dressed_trace": fraction_text(dressed_trace),
        "short_time_supremum": str(TRACE_M),
        "fixed_t_large_m_limit": str(int(not (TIME_LOG_BASE > 1))),
        "raw_HS_norm": sqrt_fraction_text(Fraction(TRACE_M)),
    }
    return {"inputs": inputs, "derived": derived}, {
        "dressed_trace": dressed_trace,
        "fixed_t_decay_samples": [m * math.exp(-math.log(TIME_LOG_BASE) * m) for m in (TRACE_M, 2 * TRACE_M, 4 * TRACE_M)],
    }


def energy_escape_fixture() -> tuple[dict[str, Any], dict[str, Any]]:
    escaped = 1 - ESCAPE_MASS
    plus_support = {"e_plus": ESCAPE_MASS, "f_n_plus": escaped}
    minus_support = {"e_minus": ESCAPE_MASS, "f_n_minus": escaped}
    shared_support = set(plus_support) & set(minus_support)
    if shared_support:
        raise AssertionError("labelled plus/minus fixture must have disjoint orthonormal supports")
    overlap = Fraction(0)
    state_distance_squared = 4 * (1 - overlap * overlap)
    state_distance = sqrt_fraction_text(state_distance_squared)
    plus_witness = plus_support["e_plus"]
    minus_witness = -minus_support["e_minus"]
    energy = plus_support["f_n_plus"] * ESCAPE_INDEX
    inputs = {"m0": fraction_text(ESCAPE_MASS), "n": str(ESCAPE_INDEX)}
    derived = {
        "plus_witness": fraction_text(plus_witness),
        "minus_witness": fraction_text(minus_witness),
        "state_norm_distance": state_distance,
        "compact_mass": fraction_text(ESCAPE_MASS),
        "escaped_mass": fraction_text(escaped),
        "energy": fraction_text(energy),
    }
    return {"inputs": inputs, "derived": derived}, {
        "plus_support": plus_support,
        "minus_support": minus_support,
        "shared_support": shared_support,
        "plus_norm_squared": sum(plus_support.values(), Fraction(0)),
        "minus_norm_squared": sum(minus_support.values(), Fraction(0)),
        "overlap": overlap,
        "state_distance_squared": state_distance_squared,
        "escaped": escaped,
        "energy": energy,
    }


def build_payload(staged: bool) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate = " ".join(CERTIFICATE.read_text(encoding="utf-8").split())
    corner, corner_witness = corner_fixture()
    compression_defects, compression_witness = compression_defect_fixture()
    energy, energy_witness = energy_tightness_fixture()
    positive, positive_witness = positive_time_fixture()
    q3_edge, q3_witness = q3_edge_fixture()
    schatten, schatten_witness = normalized_schatten_fixture()
    fixed_time, fixed_time_witness = fixed_positive_time_fixture()
    escape, escape_witness = energy_escape_fixture()
    derived = {
        "corner_ucp": corner,
        "compression_defects": compression_defects,
        "energy_tightness": energy,
        "positive_time_trace": positive,
        "q3_edge_heat_trace": q3_edge,
        "normalized_schatten": schatten,
        "fixed_positive_time": fixed_time,
        "energy_escape": escape,
    }
    audit = Audit()

    audit.check(
        "manifest exact identity",
        manifest["schema"] == "tect/pre-a-q3lock-ritz-corner-energy-tightness-positive-time-trace/1.0"
        and manifest["package_id"] == SLUG
        and manifest["version"] == "R-167 v3.5"
        and manifest["date"] == "2026-08-13"
        and manifest["exploration_id"] == "EXP-000839"
        and manifest["prior_exploration_id"] == "EXP-000838"
        and manifest["claim_bearing"] is False,
        (manifest["schema"], manifest["version"], manifest["exploration_id"]),
        ("exact schema", "R-167 v3.5", "EXP-000839"),
        "manifest",
    )
    audit.check(
        "manifest exact topology",
        tuple(manifest["closed_gate_ids"]) == CLOSED
        and tuple(manifest["negative_ids"]) == NEGATIVES
        and len(manifest["reused_negative_ids"]) == 3
        and len(manifest["open_parent_gate_ids"]) == 5,
        (manifest["closed_gate_ids"], manifest["negative_ids"], manifest["reused_negative_ids"]),
        (CLOSED, NEGATIVES, "three reused and five parents"),
        "manifest",
    )
    audit.check("independent exact fixture agreement", derived == manifest["exact_fixture"], derived, manifest["exact_fixture"], "oracle")
    audit.check(
        "independent corner positivity",
        corner_witness["determinant"] > 0
        and corner_witness["defect"][0][0] > 0
        and corner["derived"]["parity_compatible"],
        corner_witness,
        "positive sample Kadison defect and parity pair compression",
        "corner",
    )
    audit.check(
        "independent multiplication defect",
        compression_defects["derived"]["product_defect_rank"] == str(1)
        and compression_defects["derived"]["product_defect_operator_norm"] == str(1),
        compression_defects["derived"],
        "rank-one norm-one boundary defect",
        "corner_firewall",
    )
    audit.check(
        "independent generator defect identity",
        compression_witness["generator_coefficient"] == compression_witness["generator_cross_boundary"]
        and compression_defects["derived"]["generator_defect_rank"] == str(1)
        and compression_defects["derived"]["generator_defect_operator_norm"] == str(1),
        compression_defects["derived"],
        "rank-one norm-one cross-boundary coefficient",
        "corner_firewall",
    )
    audit.check(
        "independent energy-tail inequalities",
        energy_witness["tail_probability"] <= energy_witness["markov"]
        and energy_witness["trace_tail_squared"] < energy_witness["gentle_squared"],
        energy_witness,
        "delta<=E/R and compression error below gentle modulus",
        "tightness",
    )
    audit.check(
        "independent trace factorization fixture",
        positive_witness["trace_norm"] == positive_witness["trace_bound"]
        and positive_witness["high_trace"] > 0,
        positive_witness,
        "trace norm saturates envelope bound",
        "trace",
    )
    audit.check(
        "independent Ritz tail",
        all(
            abs(positive_witness["dressed"][index + 1]) <= abs(positive_witness["dressed"][index])
            for index in range(KERNEL_RANK, len(H_LEVELS) - 1)
        ),
        positive_witness["dressed"],
        "decreasing high spectral tail in fixture",
        "trace",
    )
    audit.check(
        "independent Q3 heat partition bound",
        q3_witness["s_selfadjoint_contraction"]
        and q3_witness["k_s_commutator_zero"]
        and q3_witness["edge_z0"] <= q3_witness["zk6_squared"],
        q3_witness["edge_z0"],
        q3_witness["zk6_squared"],
        "q3_heat",
    )
    audit.check(
        "independent Q3 energy and residual bounds",
        float(q3_witness["edge_z1"])
        < POSITIVE_TIME_FACTOR
        * q3_witness["zk12_squared_float"]
        / (math.e * math.log(TIME_LOG_BASE))
        and float(q3_witness["residual"]) < q3_witness["upper_float"],
        (q3_witness["edge_z1"], q3_witness["residual"]),
        "strict derived bounds",
        "q3_heat",
    )
    audit.check(
        "independent normalized Schatten separation",
        schatten_witness["normalized_squared"] < schatten_witness["raw_squared"]
        and schatten["derived"]["operator_norm"] == schatten["derived"]["fixed_transition"],
        schatten["derived"],
        "normalization shrinks while fixed channel is one",
        "negative",
    )
    samples = fixed_time_witness["fixed_t_decay_samples"]
    audit.check(
        "independent fixed-time decay versus short-time supremum",
        samples[0] > samples[1] > samples[2] > 0
        and fixed_time["derived"]["short_time_supremum"] == str(TRACE_M),
        samples,
        "decreasing fixed-time samples and supremum m",
        "negative",
    )
    audit.check(
        "independent energy escape",
        escape_witness["escaped"] > 0
        and not escape_witness["shared_support"]
        and escape_witness["overlap"] == 0
        and escape_witness["state_distance_squared"]
        == 4 * (1 - escape_witness["overlap"] * escape_witness["overlap"])
        and escape_witness["plus_norm_squared"] == 1
        and escape_witness["minus_norm_squared"] == 1
        and escape_witness["energy"] == escape_witness["escaped"] * ESCAPE_INDEX
        and escape["derived"]["compact_mass"] != str(1),
        escape["derived"],
        "positive singular mass and growing energy coefficient",
        "negative",
    )
    theorem_tokens = (
        "Ritz corner maps are UCP and projective",
        "fixed local selfadjoint odd contraction",
        "2 sqrt(E_X/R)",
        "EXP-000781 Section 6 is the prior authority",
        "C_P(AB)-C_P(A)C_P(B)=PA(1-P)BP",
        "does not by itself transfer products, dynamics, KMS",
        "Positive imaginary time makes the form perturbation trace class",
        "Q3 edge heat-trace reduction",
    )
    audit.check(
        "certificate theorem tokens",
        all(token in certificate for token in theorem_tokens),
        [token for token in theorem_tokens if token not in certificate],
        [],
        "certificate",
    )
    boundary_tokens = (
        "Dimension-normalized Schatten smallness",
        "Fixed positive time is not short-time control",
        "Exact asymptotic-multiplicativity and dynamics-intertwining obstruction",
        "No dynamics/KMS/ground/GNS/full-phase claim is made",
        "All five active parent gates remain OPEN",
        "No v3.5 PDF is issued",
    )
    audit.check(
        "certificate boundary tokens",
        all(token in certificate for token in boundary_tokens),
        [token for token in boundary_tokens if token not in certificate],
        [],
        "certificate",
    )
    audit.check(
        "proof-first lifecycle",
        manifest["checkpoint_synthesis"]["pdf_issued"] is False
        and manifest["formal_integration_contract"]["event_id"]
        == "20260813-r-167-v3-5-ritz-corner-state-passage-and-positi"
        and manifest["formal_integration_contract"]["expected_post_formal_counts"]["catalog"] == 3915,
        manifest["formal_integration_contract"],
        "exact event id, catalog target and no PDF",
        "lifecycle",
    )

    if not staged:
        texts = "\n".join(path.read_text(encoding="utf-8") for path in FORMAL_PATHS)
        required = CLOSED + NEGATIVES + ("EXP-000839", "R-167 v3.5")
        audit.check(
            "formal authority aggregate",
            all(token in texts for token in required),
            [token for token in required if token not in texts],
            [],
            "formal",
        )

    return {
        "schema": "tect/verification-run/1.0",
        "script_version": __version__,
        "package_id": SLUG,
        "mode": "staged" if staged else "formal",
        "verdict": "PASS",
        "assertions": audit.rows,
        "summary": {"total": len(audit.rows), "passed": len(audit.rows), "failed": 0, "missing": 0},
        "derived": derived,
        "source_hashes": {
            str(path.relative_to(REPO)).replace("\\", "/"): normalized_sha256(path)
            for path in (SCRIPT, MANIFEST, CERTIFICATE)
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--staged", action="store_true")
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    payload = build_payload(args.staged)
    if not args.no_store:
        atomic_json(args.output, payload)
    total = payload["summary"]["total"]
    print(f"R-167 v3.5 INDEPENDENT PASS {total}/{total}")
    if args.no_store:
        print("NO-STORE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

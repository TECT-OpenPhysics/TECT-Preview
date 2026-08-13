#!/usr/bin/env python3
"""Primary symbolic verifier for the R-167 v3.5 proof-first package."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any

import sympy as sp


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-ritz-corner-energy-tightness-and-positive-time-trace-route-split"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260813.md"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-13-primary-{SLUG}/result.json"
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

# Labelled corner inputs.
AMBIENT_DIMENSION = sp.Integer(4)
CORNER_RANK = sp.Integer(2)
TEST_MATRIX_ROWS = (
    (sp.Integer(1), sp.Integer(2), sp.Integer(3), sp.Integer(4)),
    (sp.Integer(2), sp.Integer(0), sp.Integer(5), sp.Integer(6)),
    (sp.Integer(3), sp.Integer(5), sp.Integer(7), sp.Integer(8)),
    (sp.Integer(4), sp.Integer(6), sp.Integer(8), sp.Integer(9)),
)
DEFECT_DIMENSION = sp.Integer(4)
DEFECT_CORNER_RANK = sp.Integer(3)

# Labelled local-energy inputs.
ENERGY_LEVEL = sp.Integer(4)
HIGH_AMPLITUDE = sp.Rational(1, 4)
ENERGY_CUTOFF = sp.Integer(2)

# Labelled positive-time inputs.
H_LEVELS = (sp.Integer(0), sp.Integer(0), sp.Integer(2), sp.Integer(4))
FORM_ALPHA = sp.Rational(1, 4)
FORM_EPSILON = sp.Rational(1, 8)
TIME_LOG_BASE = sp.Integer(2)
KERNEL_RANK = sp.Integer(2)
CONTRACTION_SIGNS = (sp.Integer(1), sp.Integer(-1), sp.Integer(1), sp.Integer(-1))

# Labelled Q3 edge inputs.
K_LEVELS = (sp.Integer(0), sp.Integer(0), sp.Integer(12))
S_SIGNS = (sp.Integer(1), sp.Integer(-1), sp.Integer(0))
S_FIXTURE_SCOPE = "actual-compatible selfadjoint-contraction fixture with high-sector zero"
EDGE_J = sp.Integer(1)
EDGE_N = sp.Integer(4)
EDGE_SHARE = sp.Integer(6)
POSITIVE_TIME_FACTOR = sp.Integer(2)
EDGE_ALPHA_POWER = sp.Integer(2)
EDGE_BETA_POWER = sp.Integer(3)

# Labelled no-go inputs.
SCHATTEN_N = sp.Integer(4)
SCHATTEN_M = sp.Integer(8)
SCHATTEN_P = sp.Integer(2)
SCHATTEN_PENALTY_POWER = sp.Integer(2)
TRANSITION_RANK = sp.Integer(2)
TRANSITION_AMPLITUDE = sp.Integer(1)
TRACE_M = sp.Integer(8)
ESCAPE_MASS = sp.Rational(1, 4)
ESCAPE_INDEX = sp.Integer(8)


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


def exact_text(value: sp.Expr) -> str:
    return str(sp.factor(value)).replace("**", "^").replace(" ", "")


def matrix_text(matrix: sp.Matrix) -> list[list[str]]:
    return [[exact_text(matrix[i, j]) for j in range(matrix.cols)] for i in range(matrix.rows)]


def corner_fixture() -> tuple[dict[str, Any], dict[str, Any]]:
    matrix = sp.Matrix(TEST_MATRIX_ROWS)
    embedding = sp.zeros(int(AMBIENT_DIMENSION), int(CORNER_RANK))
    for index in range(int(CORNER_RANK)):
        embedding[index, index] = 1
    compressed = embedding.T * matrix * embedding
    defect = sp.simplify(embedding.T * matrix**2 * embedding - compressed**2)
    ambient_parity = sp.zeros(int(AMBIENT_DIMENSION))
    ambient_parity[0, 1] = ambient_parity[1, 0] = 1
    ambient_parity[2, 3] = ambient_parity[3, 2] = 1
    corner_parity = sp.Matrix([[0, 1], [1, 0]])
    derived = {
        "compressed_matrix": matrix_text(compressed),
        "unital": embedding.T * sp.eye(int(AMBIENT_DIMENSION)) * embedding == sp.eye(int(CORNER_RANK)),
        "parity_compatible": ambient_parity * embedding == embedding * corner_parity,
        "kadison_defect": matrix_text(defect),
        "kadison_defect_determinant": exact_text(defect.det()),
    }
    inputs = {
        "ambient_dimension": exact_text(AMBIENT_DIMENSION),
        "corner_rank": exact_text(CORNER_RANK),
        "test_matrix": matrix_text(matrix),
    }
    witness = {
        "embedding_isometry": embedding.T * embedding == sp.eye(int(CORNER_RANK)),
        "defect_trace": sp.trace(defect),
        "defect_determinant": defect.det(),
    }
    return {"inputs": inputs, "derived": derived}, witness


def energy_tightness_fixture() -> tuple[dict[str, Any], dict[str, sp.Expr]]:
    low_amplitude = sp.sqrt(1 - HIGH_AMPLITUDE**2)
    vector = sp.Matrix([low_amplitude, HIGH_AMPLITUDE])
    density = vector * vector.T
    energy_operator = sp.diag(0, ENERGY_LEVEL)
    low_projection = sp.diag(1, 0)
    energy = sp.simplify(sp.trace(density * energy_operator))
    tail_probability = sp.simplify(sp.trace(density * (sp.eye(2) - low_projection)))
    markov = sp.simplify(energy / ENERGY_CUTOFF)
    compression_error = density - low_projection * density * low_projection
    trace_tail = sp.sqrt(
        tail_probability**2 + 4 * tail_probability * (1 - tail_probability)
    )
    gentle = sp.simplify(2 * sp.sqrt(markov))
    inputs = {
        "K_diagonal": [exact_text(sp.Integer(0)), exact_text(ENERGY_LEVEL)],
        "high_amplitude": exact_text(HIGH_AMPLITUDE),
        "R": exact_text(ENERGY_CUTOFF),
    }
    derived = {
        "energy": exact_text(energy),
        "tail_probability": exact_text(tail_probability),
        "energy_markov_bound": exact_text(markov),
        "trace_tail_norm": exact_text(trace_tail),
        "gentle_bound": exact_text(gentle),
        "strict_gentle_check": bool(trace_tail < gentle),
    }
    witness = {
        "density_trace": sp.trace(density),
        "density_determinant": density.det(),
        "compression_error_determinant": compression_error.det(),
        "trace_tail": trace_tail,
        "gentle": gentle,
    }
    return {"inputs": inputs, "derived": derived}, witness


def compression_defect_fixture() -> tuple[dict[str, Any], dict[str, sp.Matrix]]:
    dimension = int(DEFECT_DIMENSION)
    rank = int(DEFECT_CORNER_RANK)
    shift = sp.zeros(dimension)
    for index in range(dimension - 1):
        shift[index + 1, index] = 1
    projection = sp.diag(*([1] * rank + [0] * (dimension - rank)))
    complement = sp.eye(dimension) - projection
    a_product = shift.T
    b_product = shift
    product_defect = sp.simplify(
        projection * a_product * b_product * projection
        - projection * a_product * projection * b_product * projection
    )
    hamiltonian = shift + shift.T
    generator_observable = shift
    compressed_hamiltonian = projection * hamiltonian * projection
    compressed_observable = projection * generator_observable * projection
    full_commutator = hamiltonian * generator_observable - generator_observable * hamiltonian
    corner_commutator = compressed_hamiltonian * compressed_observable - compressed_observable * compressed_hamiltonian
    generator_coefficient = sp.simplify(projection * full_commutator * projection - corner_commutator)
    generator_cross_boundary = sp.simplify(
        projection * hamiltonian * complement * generator_observable * projection
        - projection * generator_observable * complement * hamiltonian * projection
    )
    product_corner = product_defect[:rank, :rank]
    generator_corner = generator_coefficient[:rank, :rank]
    inputs = {"shift_dimension": exact_text(DEFECT_DIMENSION), "cutoff_rank": exact_text(DEFECT_CORNER_RANK)}
    derived = {
        "product_defect_diagonal": [exact_text(product_corner[index, index]) for index in range(rank)],
        "product_defect_rank": exact_text(product_corner.rank()),
        "product_defect_operator_norm": exact_text(max(abs(product_corner[index, index]) for index in range(rank))),
        "generator_defect_diagonal": [
            exact_text(sp.I * generator_corner[index, index]) for index in range(rank)
        ],
        "generator_defect_rank": exact_text(generator_corner.rank()),
        "generator_defect_operator_norm": exact_text(
            max(abs(generator_corner[index, index]) for index in range(rank))
        ),
    }
    return {"inputs": inputs, "derived": derived}, {
        "product_defect": product_defect,
        "generator_coefficient": generator_coefficient,
        "generator_cross_boundary": generator_cross_boundary,
    }


def positive_time_fixture() -> tuple[dict[str, Any], dict[str, Any]]:
    weights = tuple(sp.simplify(TIME_LOG_BASE ** (-level)) for level in H_LEVELS)
    z0 = sp.simplify(sum(weights))
    z1 = sp.simplify(sum(level * weight for level, weight in zip(H_LEVELS, weights)))
    envelope = tuple(sp.simplify(FORM_ALPHA * level + FORM_EPSILON) for level in H_LEVELS)
    perturbation = tuple(sign * value for sign, value in zip(CONTRACTION_SIGNS, envelope))
    dressed = tuple(sp.simplify(weight * value) for weight, value in zip(weights, perturbation))
    trace_norm = sp.simplify(sum(abs(value) for value in dressed))
    trace_bound = sp.simplify(FORM_ALPHA * z1 + FORM_EPSILON * z0)
    high_trace = sp.simplify(sum(envelope[i] * weights[i] for i in range(int(KERNEL_RANK), len(H_LEVELS))))
    low_hs = sp.simplify(FORM_EPSILON * sp.sqrt(KERNEL_RANK))
    mixed_hs = sp.simplify(sp.sqrt(FORM_EPSILON * high_trace))
    last_ritz_tail = abs(dressed[-1])
    inputs = {
        "h_diagonal": [exact_text(value) for value in H_LEVELS],
        "alpha": exact_text(FORM_ALPHA),
        "epsilon": exact_text(FORM_EPSILON),
        "t": f"log({exact_text(TIME_LOG_BASE)})",
        "kernel_rank": exact_text(KERNEL_RANK),
    }
    derived = {
        "Z0": exact_text(z0),
        "Z1": exact_text(z1),
        "trace_norm": exact_text(trace_norm),
        "trace_bound": exact_text(trace_bound),
        "low_operator_bound": exact_text(FORM_EPSILON),
        "low_HS_bound": exact_text(low_hs),
        "mixed_HS_bound": exact_text(mixed_hs),
        "high_trace_bound": exact_text(high_trace),
        "last_Ritz_tail": exact_text(last_ritz_tail),
    }
    witness = {
        "weights": weights,
        "envelope": envelope,
        "perturbation": perturbation,
        "dressed": dressed,
        "trace_norm": trace_norm,
        "trace_bound": trace_bound,
        "high_trace": high_trace,
    }
    return {"inputs": inputs, "derived": derived}, witness


def q3_edge_fixture() -> tuple[dict[str, Any], dict[str, sp.Expr]]:
    edge_energies: list[sp.Expr] = []
    for left_level, left_sign in zip(K_LEVELS, S_SIGNS):
        for right_level, right_sign in zip(K_LEVELS, S_SIGNS):
            edge_energies.append(
                sp.simplify(
                    (left_level + right_level) / EDGE_SHARE + EDGE_J * (1 - left_sign * right_sign)
                )
            )
    edge_weights = [sp.simplify(TIME_LOG_BASE ** (-energy)) for energy in edge_energies]
    edge_z0 = sp.simplify(sum(edge_weights))
    edge_z1 = sp.simplify(sum(energy * weight for energy, weight in zip(edge_energies, edge_weights)))
    zk_t_over_6 = sp.simplify(sum(TIME_LOG_BASE ** (-level / EDGE_SHARE) for level in K_LEVELS))
    zk_t_over_12 = sp.simplify(
        sum(TIME_LOG_BASE ** (-level / (POSITIVE_TIME_FACTOR * EDGE_SHARE)) for level in K_LEVELS)
    )
    zk6_squared = sp.expand(zk_t_over_6**2)
    zk12_squared = sp.expand(zk_t_over_12**2)
    alpha = EDGE_N ** (-EDGE_ALPHA_POWER)
    beta = EDGE_N ** (-EDGE_BETA_POWER)
    residual = sp.simplify(alpha * edge_z1 + beta * edge_z0)
    upper = sp.simplify(
        POSITIVE_TIME_FACTOR * alpha * zk12_squared / (sp.E * sp.log(TIME_LOG_BASE))
        + beta * zk6_squared
    )
    thermal_prefactor = sp.simplify(POSITIVE_TIME_FACTOR * alpha * zk12_squared)
    if not thermal_prefactor.is_Rational:
        raise AssertionError("labelled actual-compatible heat fixture must have a rational prefactor")
    upper_text = (
        f"{exact_text(beta * zk6_squared)}+{thermal_prefactor.p}/"
        f"({thermal_prefactor.q}*E*log({exact_text(TIME_LOG_BASE)}))"
    )
    inputs = {
        "k_diagonal": [exact_text(value) for value in K_LEVELS],
        "s_diagonal": [exact_text(value) for value in S_SIGNS],
        "fixture_scope": S_FIXTURE_SCOPE,
        "J": exact_text(EDGE_J),
        "N": exact_text(EDGE_N),
        "alpha": f"1/N^{exact_text(EDGE_ALPHA_POWER)}",
        "beta_edge": f"1/N^{exact_text(EDGE_BETA_POWER)}",
        "t": f"log({exact_text(TIME_LOG_BASE)})",
    }
    derived = {
        "edge_Z0": exact_text(edge_z0),
        "edge_Z1": exact_text(edge_z1),
        "Zk_t_over_6_squared": exact_text(zk6_squared),
        "Zk_t_over_12_squared": exact_text(zk12_squared),
        "residual_trace": exact_text(residual),
        "residual_upper_bound": upper_text,
        "strict_upper_check": bool(residual < upper),
    }
    witness = {
        "energies": tuple(edge_energies),
        "z0": edge_z0,
        "z1": edge_z1,
        "zk6_squared": zk6_squared,
        "zk12_squared": zk12_squared,
        "residual": residual,
        "upper": upper,
        "s_selfadjoint_contraction": all(abs(value) <= 1 for value in S_SIGNS),
        "k_s_commutator_zero": True,
    }
    return {"inputs": inputs, "derived": derived}, witness


def normalized_schatten_fixture() -> tuple[dict[str, Any], dict[str, sp.Expr]]:
    singular_values = (TRANSITION_AMPLITUDE,) * int(TRANSITION_RANK) + (sp.Integer(0),) * int(
        SCHATTEN_M - TRANSITION_RANK
    )
    raw_sp = sp.simplify(sum(value**SCHATTEN_P for value in singular_values) ** (1 / SCHATTEN_P))
    normalized = sp.simplify(raw_sp / SCHATTEN_M ** (1 / SCHATTEN_P))
    relative_alpha = SCHATTEN_N ** (-SCHATTEN_PENALTY_POWER)
    m = sp.symbols("m", positive=True)
    normalized_symbolic = (
        TRANSITION_RANK * TRANSITION_AMPLITUDE**SCHATTEN_P / m
    ) ** (sp.Integer(1) / SCHATTEN_P)
    inputs = {
        "N": exact_text(SCHATTEN_N),
        "m": exact_text(SCHATTEN_M),
        "p": exact_text(SCHATTEN_P),
    }
    derived = {
        "relative_alpha": exact_text(relative_alpha),
        "operator_norm": exact_text(max(singular_values)),
        "unnormalized_Sp": exact_text(raw_sp),
        "normalized_Sp": exact_text(normalized),
        "fixed_transition": exact_text(TRANSITION_AMPLITUDE),
        "large_m_limit": exact_text(sp.limit(normalized_symbolic, m, sp.oo)),
    }
    return {"inputs": inputs, "derived": derived}, {"normalized_symbolic": normalized_symbolic}


def fixed_positive_time_fixture() -> tuple[dict[str, Any], dict[str, sp.Expr]]:
    dressed_trace = sp.simplify(TRACE_M * TIME_LOG_BASE ** (-TRACE_M))
    raw_hs = sp.sqrt(TRACE_M)
    m, t = sp.symbols("m t", positive=True)
    symbolic = m * sp.exp(-t * m)
    inputs = {"m": exact_text(TRACE_M), "t": f"log({exact_text(TIME_LOG_BASE)})"}
    derived = {
        "dressed_trace": exact_text(dressed_trace),
        "short_time_supremum": exact_text(TRACE_M),
        "fixed_t_large_m_limit": exact_text(sp.limit(symbolic, m, sp.oo)),
        "raw_HS_norm": exact_text(raw_hs),
    }
    return {"inputs": inputs, "derived": derived}, {"symbolic": symbolic, "t": t, "m": m}


def energy_escape_fixture() -> tuple[dict[str, Any], dict[str, Any]]:
    escaped = 1 - ESCAPE_MASS
    low_amplitude = sp.sqrt(ESCAPE_MASS)
    escaping_amplitude = sp.sqrt(escaped)
    plus_vector = sp.Matrix([low_amplitude, 0, escaping_amplitude, 0])
    minus_vector = sp.Matrix([0, low_amplitude, 0, escaping_amplitude])
    plus_density = plus_vector * plus_vector.T
    minus_density = minus_vector * minus_vector.T
    overlap = sp.simplify((plus_vector.T * minus_vector)[0])
    state_distance = sp.simplify(2 * sp.sqrt(1 - sp.Abs(overlap) ** 2))
    witness = sp.diag(1, -1, 0, 0)
    energy_operator = sp.diag(0, 0, ESCAPE_INDEX, ESCAPE_INDEX)
    plus_witness = sp.simplify((plus_vector.T * witness * plus_vector)[0])
    minus_witness = sp.simplify((minus_vector.T * witness * minus_vector)[0])
    energy = sp.simplify((plus_vector.T * energy_operator * plus_vector)[0])
    inputs = {"m0": exact_text(ESCAPE_MASS), "n": exact_text(ESCAPE_INDEX)}
    derived = {
        "plus_witness": exact_text(plus_witness),
        "minus_witness": exact_text(minus_witness),
        "state_norm_distance": exact_text(state_distance),
        "compact_mass": exact_text(ESCAPE_MASS),
        "escaped_mass": exact_text(escaped),
        "energy": exact_text(energy),
    }
    n = sp.symbols("n", positive=True)
    return {"inputs": inputs, "derived": derived}, {
        "plus_vector": plus_vector,
        "minus_vector": minus_vector,
        "plus_density": plus_density,
        "minus_density": minus_density,
        "overlap": overlap,
        "state_distance": state_distance,
        "energy_sequence": escaped * n,
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
        "manifest identity",
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
        "manifest scoped topology",
        tuple(manifest["closed_gate_ids"]) == CLOSED
        and tuple(manifest["negative_ids"]) == NEGATIVES
        and len(manifest["reused_negative_ids"]) == 3
        and len(manifest["open_parent_gate_ids"]) == 5
        and len(manifest["historical_open_gate_ids"]) == 1,
        (
            manifest["closed_gate_ids"],
            manifest["negative_ids"],
            len(manifest["reused_negative_ids"]),
            len(manifest["open_parent_gate_ids"]),
        ),
        (CLOSED, NEGATIVES, 3, 5),
        "manifest",
    )
    audit.check("exact fixture agreement", derived == manifest["exact_fixture"], derived, manifest["exact_fixture"], "oracle")
    audit.check(
        "corner Kraus UCP witness",
        corner_witness["embedding_isometry"]
        and corner["derived"]["unital"]
        and corner["derived"]["parity_compatible"],
        corner_witness,
        "isometric compression and parity intertwining",
        "corner",
    )
    audit.check(
        "corner Kadison defect positive",
        corner_witness["defect_trace"] > 0 and corner_witness["defect_determinant"] > 0,
        (corner_witness["defect_trace"], corner_witness["defect_determinant"]),
        "positive definite sample defect",
        "corner",
    )
    audit.check(
        "exact compression multiplication defect",
        compression_witness["product_defect"]
        == compression_witness["product_defect"].T
        and compression_defects["derived"]["product_defect_rank"] == exact_text(sp.Integer(1))
        and compression_defects["derived"]["product_defect_operator_norm"] == exact_text(sp.Integer(1)),
        compression_defects["derived"],
        "rank-one norm-one shift boundary projection",
        "corner_firewall",
    )
    audit.check(
        "exact compressed-generator defect identity",
        compression_witness["generator_coefficient"] == compression_witness["generator_cross_boundary"]
        and compression_defects["derived"]["generator_defect_rank"] == exact_text(sp.Integer(1))
        and compression_defects["derived"]["generator_defect_operator_norm"] == exact_text(sp.Integer(1)),
        compression_defects["derived"],
        "i(PHQAP-PAQHP) with rank-one norm-one coefficient",
        "corner_firewall",
    )
    audit.check(
        "energy density state",
        energy_witness["density_trace"] == 1 and energy_witness["density_determinant"] == 0,
        energy_witness,
        "rank-one density",
        "tightness",
    )
    audit.check(
        "Markov and gentle modulus",
        sp.Rational(energy["derived"]["tail_probability"])
        <= sp.Rational(energy["derived"]["energy_markov_bound"])
        and energy_witness["trace_tail"] < energy_witness["gentle"],
        energy["derived"],
        "delta<=E/R and strict sample gentle bound",
        "tightness",
    )
    audit.check(
        "positive-time trace equality fixture",
        positive_witness["trace_norm"] == positive_witness["trace_bound"],
        positive_witness["trace_norm"],
        positive_witness["trace_bound"],
        "trace",
    )
    audit.check(
        "positive-time dressed blocks",
        positive_witness["high_trace"] > 0
        and positive["derived"]["low_operator_bound"] == exact_text(FORM_EPSILON)
        and positive["derived"]["last_Ritz_tail"] == exact_text(abs(positive_witness["dressed"][-1])),
        positive["derived"],
        "derived low/high bounds and Ritz tail",
        "trace",
    )
    audit.check(
        "spectral Ritz tail converges",
        sp.limit((FORM_ALPHA * sp.Symbol("x", positive=True) + FORM_EPSILON) * sp.exp(-sp.log(2) * sp.Symbol("x", positive=True)), sp.Symbol("x", positive=True), sp.oo) == 0,
        "energy envelope times heat decay",
        0,
        "trace",
    )
    audit.check(
        "Q3 edge partition bound",
        q3_witness["s_selfadjoint_contraction"]
        and q3_witness["k_s_commutator_zero"]
        and q3_witness["z0"] <= q3_witness["zk6_squared"],
        q3_witness["z0"],
        q3_witness["zk6_squared"],
        "q3_heat",
    )
    audit.check(
        "Q3 edge energy bound",
        q3_witness["z1"] < 2 * q3_witness["zk12_squared"] / (sp.E * sp.log(2)),
        q3_witness["z1"],
        2 * q3_witness["zk12_squared"] / (sp.E * sp.log(2)),
        "q3_heat",
    )
    audit.check(
        "Q3 residual trace bound",
        q3_witness["residual"] < q3_witness["upper"],
        q3_witness["residual"],
        q3_witness["upper"],
        "q3_heat",
    )
    m_symbol = sp.symbols("m", positive=True)
    audit.check(
        "normalized Schatten vanishes but channel persists",
        sp.limit(schatten_witness["normalized_symbolic"], m_symbol, sp.oo) == 0
        and schatten["derived"]["operator_norm"] == schatten["derived"]["fixed_transition"],
        schatten["derived"],
        "normalized limit zero with fixed unit transition",
        "negative",
    )
    audit.check(
        "fixed positive-time versus short-time split",
        fixed_time["derived"]["fixed_t_large_m_limit"] == exact_text(sp.Integer(0))
        and fixed_time["derived"]["short_time_supremum"] == exact_text(TRACE_M),
        fixed_time["derived"],
        "fixed-t limit zero and short-time supremum m",
        "negative",
    )
    n_symbol = sp.symbols("n", positive=True)
    audit.check(
        "energy escape divergence",
        sp.limit(escape_witness["energy_sequence"], n_symbol, sp.oo) == sp.oo
        and escape_witness["overlap"] == 0
        and escape_witness["state_distance"]
        == 2 * sp.sqrt(1 - sp.Abs(escape_witness["overlap"]) ** 2)
        and sp.trace(escape_witness["plus_density"]) == 1
        and sp.trace(escape_witness["minus_density"]) == 1
        and escape["derived"]["compact_mass"] != exact_text(sp.Integer(1)),
        escape["derived"],
        "fixed witness with singular escaped mass and divergent energy",
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
        "trace-ideal approximation theorem",
        "Q3 edge heat-trace reduction",
    )
    audit.check(
        "certificate theorem contract",
        all(token in certificate for token in theorem_tokens),
        [token for token in theorem_tokens if token not in certificate],
        [],
        "certificate",
    )
    obstruction_tokens = (
        "Exact energy-escape obstruction",
        "Dimension-normalized Schatten smallness",
        "Fixed positive time is not short-time control",
        "Exact asymptotic-multiplicativity and dynamics-intertwining obstruction",
        "not automatically have locally normal limits",
        "does not automatically give DFFR contour entry",
    )
    audit.check(
        "certificate four-obstruction contract",
        all(token in certificate for token in obstruction_tokens),
        [token for token in obstruction_tokens if token not in certificate],
        [],
        "certificate",
    )
    boundary_tokens = (
        "No dynamics/KMS/ground/GNS/full-phase claim is made",
        "All five active parent gates remain OPEN",
        "No v3.5 PDF is issued",
        "physical Sector A, or Pre-A closure",
    )
    audit.check(
        "certificate no-overclaim contract",
        all(token in certificate for token in boundary_tokens),
        [token for token in boundary_tokens if token not in certificate],
        [],
        "certificate",
    )
    audit.check(
        "proof-first lifecycle",
        manifest["checkpoint_synthesis"]["pdf_issued"] is False
        and manifest["formal_integration_contract"]["event_ordinal"] == 631
        and manifest["formal_integration_contract"]["theorem_map_version"] == "1.27.0",
        (manifest["checkpoint_synthesis"], manifest["formal_integration_contract"]),
        "no PDF, event 631 and theorem map 1.27.0",
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
    print(f"R-167 v3.5 PRIMARY PASS {total}/{total}")
    if args.no_store:
        print("NO-STORE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

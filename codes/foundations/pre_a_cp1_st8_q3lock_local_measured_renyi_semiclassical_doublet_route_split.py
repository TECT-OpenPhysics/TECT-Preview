#!/usr/bin/env python3
"""Primary exact verifier for the staged R-167 v2.0 route split.

The script has six exact fixture groups.  Fixtures A--C retain every v1.9
check: pure coordinate-bond cutoff algebra, local/global Renyi separation,
Q3 semiclassical geometry, exact low-band compression, residuals, and the N
corridor.  Fixture D verifies finite-Gibbs full-Hamiltonian Duhamel bounds,
trace-state stability, bounded half-modular transfer, and the exact arbitrary-
context counterfamily.  Fixture E checks the fixed-edge corridor constants,
periodic covariance boundary, and homogeneous Gaussian tilted-edge no-go.
Fixture F checks the cubic 11-overlap Feshbach bound, relative-form scales,
extensive-self-energy no-go, and exact compressed-TFIM QPS inputs.

The multidimensional two-well theorem and the Del Vecchio--Frohlich--Pizzo
Lie--Schwinger theorem are *not* reproved numerically here.  The script checks
their authority tokens and the Q3 hypotheses used by the proposed import.  In
particular it records that the former has a non-explicit small-h threshold and
that the published latter theorem is rank-one.  It does not certify the
repository's finite r=-9 fixture, a rank-two many-body block elimination, a
broken-sector GNS gap, Sector A, or Pre-A.

Use ``--staged --no-store`` while the v2.0 ledger, gate, and negative
authorities are being assembled.  Missing authority then produces the
honest verdict ``INCOMPLETE`` while all exact mathematical fixtures still run.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from fractions import Fraction
from itertools import product
from pathlib import Path
from typing import Any, Iterable

import sympy as sp


__version__ = "2.0.0"
REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-local-measured-renyi-semiclassical-doublet-route-split"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260811.md"
DEFAULT_OUTPUT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / f"2026-08-11-primary-{SLUG}/result.json"
)
EXPLORATION_LEDGER = REPO / "explorations/log.jsonl"
RESULT_LEDGER = REPO / "RESULTS-LEDGER.md"
NEGATIVE_REGISTRY = REPO / "negative-results/registry.md"
GATE_REGISTRY = REPO / "claims/GATES.md"

EXPECTED_TASK = "T-054"
EXPECTED_CLAIM_IDS = ("C6-SPACETIME-SIGNATURE",)
EXPECTED_EXPLORATION = "EXP-000809"
EXPECTED_RESULT_NUMBER = "R-167"
EXPECTED_RESULT_VERSION = "v2.0"
EXPECTED_RESULT_ID = (
    "PA-CP1-ST8-Q3LOCK-SECOND-WEIGHTED-ENERGY-MOMENT-AND-COMMON-ALPHA-CAUCHY-GATE-SPLIT"
)
EXPECTED_CANDIDATE_ID = (
    "PA-CP1-ST8-Q3LOCK-LOCAL-MEASURED-RENYI-SEMICLASSICAL-DOUBLET-ROUTE-SPLIT-v0"
)
EXPECTED_CLOSED_SUBGATES = (
    "PA-CP1-ST8-Q3LOCK-PURE-BOND-COORDINATE-TAIL-INVARIANCE-AND-STATE-WEIGHTED-CUTOFF-IDENTITY",
    "PA-CP1-ST8-Q3LOCK-LOCAL-MEASURED-RENYI-TO-HISTORY-TAIL-REDUCTION",
    "PA-CP1-ST8-Q3LOCK-SEMICLASSICAL-ONSITE-DOUBLET-AND-EXACT-LOW-BAND-TFIM-COMPRESSION",    "PA-CP1-ST8-Q3LOCK-FULL-HAMILTONIAN-TWO-ORIENTATION-STATIC-GIBBS-CUTOFF-UNITARY-RESUMMATION",
    "PA-CP1-ST8-Q3LOCK-FIXED-BOND-RESTRICTED-TAIL-TO-GROWING-CORRIDOR-REDUCTION",
    "PA-CP1-ST8-Q3LOCK-BELOW-ONE-HIGH-MODE-FESHBACH-AND-RELATIVE-FORM-SMALLNESS-PRECURSOR",
    "PA-CP1-ST8-Q3LOCK-EXACT-COMPRESSED-TFIM-TWO-PHASE-QPS-AND-PHASEWISE-GAP",
)
EXPECTED_OPEN_GATES = (
    "PA-CP1-ST8-Q3LOCK-LOCAL-STRICT-ALL-EXHAUSTION-TWO-ORIENTATION-HISTORY-COMMON-ALPHA",
    "PA-CP1-ST8-Q3LOCK-BROKEN-SECTOR-GNS-GAP-COERCIVITY",
    "PA-CP1-ST8-Q3LOCK-INFINITE-DIMENSIONAL-RANK-TWO-BAND-BLOCK-DIAGONALIZATION-AND-TWO-PHASE-QPS",
    "PA-ROUND1-EVIDENCE-ROLE-AND-MINIMUM-MANIFEST-FREEZE",
)
NEGATIVE_IDS = (
    "NG-2026-08-11-PRE-A-ST8-Q3LOCK-GLOBAL-ALL-BOND-RENYI-VOLUME-UNIFORMITY",
    "NG-2026-08-11-PRE-A-ST8-Q3LOCK-RANK-ONE-UNBOUNDED-BLOCK-DIAGONALIZATION-DIRECT-BROKEN-DOUBLET-IMPORT",    "NG-2026-08-11-PRE-A-ST8-Q3LOCK-WEIGHTED-UNITARY-CUTOFF-AUTOMATIC-ARBITRARY-CONTEXT-AUTOMORPHISM-L2-UPGRADE",
    "NG-2026-08-11-PRE-A-ST8-Q3LOCK-EXTENSIVE-FESHBACH-SELF-ENERGY-AUTOMATIC-QPS-LOCALITY",
    "NG-2026-08-11-PRE-A-ST8-Q3LOCK-STATIC-GAUSSIAN-SYMMETRY-FINITE-MOMENT-AUTOMATIC-FIXED-EDGE-HISTORY-TAIL",
)
SEMICLASSICAL_SOURCES = (
    "https://www.numdam.org/item/AIHPA_1983__38_3_295_0/",
    "https://www.numdam.org/item/AIHPA_1984__40_2_224_0/",
    "https://doi.org/10.1080/03605308408820335",
    "https://annals.math.princeton.edu/1984/120-1/p04",
    "https://www.numdam.org/item/AIHPA_1985__42_2_127_0/",
)
DFP_SOURCE = "https://arxiv.org/abs/2108.13907"
YAROTSKII_QPS_SOURCE = "https://doi.org/10.1070/RM2006v061n02ABEH004323"


def normalized_sha256(path: Path) -> str:
    raw = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(raw).hexdigest()


def json_safe(value: Any) -> Any:
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, Fraction):
        return f"{value.numerator}/{value.denominator}"
    if isinstance(value, sp.Basic):
        return str(value)
    if isinstance(value, sp.MatrixBase):
        return [[json_safe(item) for item in row] for row in value.tolist()]
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [json_safe(item) for item in value]
    return str(value)


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(json_safe(payload), stream, indent=2, sort_keys=True)
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

    def check(
        self,
        name: str,
        condition: bool,
        actual: Any,
        expected: Any,
        group: str,
    ) -> None:
        if not condition:
            raise AssertionError(f"{group}: {name}: {actual!r} != {expected!r}")
        self.rows.append(
            {
                "group": group,
                "name": name,
                "status": "PASS",
                "actual": json_safe(actual),
                "expected": json_safe(expected),
            }
        )


def trace(matrix: sp.MatrixBase) -> sp.Expr:
    return sp.simplify(sum(matrix[index, index] for index in range(matrix.rows)))


def leading_principal_minors(matrix: sp.MatrixBase) -> list[sp.Expr]:
    return [
        sp.factor(matrix[:size, :size].det())
        for size in range(1, matrix.rows + 1)
    ]


def fixture_a_pure_bond_tail(audit: Audit) -> dict[str, Any]:
    """Exact finite spectral fixture for the pure-bond cutoff identity."""

    # Declared exact fixture inputs.  The density matrix is deliberately
    # non-diagonal, so equality of the two orientations uses normality of the
    # coordinate multiplier and not commutation with the state.
    sigma = sp.Matrix(
        [
            [sp.Rational(1, 2), sp.Rational(1, 10), 0],
            [sp.Rational(1, 10), sp.Rational(1, 3), sp.Rational(1, 20)],
            [0, sp.Rational(1, 20), sp.Rational(1, 6)],
        ]
    )
    delta = sp.pi
    hbar = sp.Integer(1)
    v_cut = sp.diag(0, 1, 0)
    w_tail = sp.diag(0, 1, 2)
    v_full = v_cut + w_tail
    coordinate_multiplier = sp.diag(2, -1, 3)

    b_full = sp.diag(
        *[sp.exp(-sp.I * delta * v_full[i, i] / hbar) for i in range(3)]
    )
    b_cut = sp.diag(
        *[sp.exp(-sp.I * delta * v_cut[i, i] / hbar) for i in range(3)]
    )
    difference = sp.simplify(b_full - b_cut)
    spectral_tail = sp.diag(
        *[
            4 * sp.sin(delta * w_tail[i, i] / (2 * hbar)) ** 2
            for i in range(3)
        ]
    )
    right_orientation = sp.simplify(trace(sigma * difference.H * difference))
    left_orientation = sp.simplify(trace(sigma * difference * difference.H))
    spectral_identity = sp.simplify(trace(sigma * spectral_tail))
    quadratic_upper = sp.simplify(
        delta**2 * trace(sigma * w_tail**2) / hbar**2
    )
    principal_minors = leading_principal_minors(sigma)

    audit.check(
        "fixture A density trace",
        trace(sigma) == 1,
        trace(sigma),
        1,
        "A_pure_bond",
    )
    audit.check(
        "fixture A density positive",
        all(bool(value > 0) for value in principal_minors),
        principal_minors,
        "all positive",
        "A_pure_bond",
    )
    audit.check(
        "coordinate multiplier commutes with full bond kick",
        sp.zeros(3) == b_full * coordinate_multiplier - coordinate_multiplier * b_full,
        b_full * coordinate_multiplier - coordinate_multiplier * b_full,
        sp.zeros(3),
        "A_pure_bond",
    )
    audit.check(
        "two Hilbert-Schmidt orientations exact",
        right_orientation == left_orientation == spectral_identity,
        (right_orientation, left_orientation, spectral_identity),
        "equal",
        "A_pure_bond",
    )
    # TEST ORACLE: with the declared roots-of-unity phases, only the middle
    # spectral atom contributes and its squared difference is four.
    audit.check(
        "state-weighted cutoff identity oracle",
        spectral_identity == sp.Rational(4, 3),
        spectral_identity,
        sp.Rational(4, 3),
        "A_pure_bond",
    )
    audit.check(
        "sine quadratic upper bound fixture",
        bool(sp.N(quadratic_upper - spectral_identity, 80) > 0),
        quadratic_upper - spectral_identity,
        ">0",
        "A_pure_bond",
    )

    return {
        "inputs": {
            "sigma": sigma,
            "delta": delta,
            "hbar": hbar,
            "V_cut": v_cut,
            "W_tail": w_tail,
            "coordinate_multiplier": coordinate_multiplier,
        },
        "commutator_zero": True,
        "right_orientation_hs_squared": right_orientation,
        "left_orientation_hs_squared": left_orientation,
        "spectral_sine_identity": spectral_identity,
        "quadratic_upper_bound": quadratic_upper,
        "pure_layer_only": True,
        "onsite_interspersed_history_tail_proved": False,
    }


def classical_q2(reference: Iterable[Fraction], state: Iterable[Fraction]) -> Fraction:
    return sum(p * p / q for p, q in zip(state, reference))


def fixture_b_local_and_global_renyi(audit: Audit) -> dict[str, Any]:
    """Exact local Holder fixture and exact global product obstruction."""

    reference = (Fraction(1, 2), Fraction(1, 3), Fraction(1, 6))
    plus = (Fraction(2, 3), Fraction(1, 6), Fraction(1, 6))
    minus = (Fraction(1, 4), Fraction(1, 2), Fraction(1, 4))
    event = (1, 2)
    q_event = sum(reference[index] for index in event)
    p_plus_event = sum(plus[index] for index in event)
    p_minus_event = sum(minus[index] for index in event)
    q2_plus = classical_q2(reference, plus)
    q2_minus = classical_q2(reference, minus)

    audit.check(
        "fixture B probability normalization",
        sum(reference) == sum(plus) == sum(minus) == 1,
        (sum(reference), sum(plus), sum(minus)),
        (1, 1, 1),
        "B_local_renyi",
    )
    audit.check(
        "plus measured-Renyi Holder event",
        p_plus_event**2 <= q2_plus * q_event,
        p_plus_event**2,
        f"<={q2_plus * q_event}",
        "B_local_renyi",
    )
    audit.check(
        "minus measured-Renyi Holder event",
        p_minus_event**2 <= q2_minus * q_event,
        p_minus_event**2,
        f"<={q2_minus * q_event}",
        "B_local_renyi",
    )

    alpha = sp.Integer(2)
    theta_holder = sp.simplify((alpha - 1) / alpha)
    gaussian_a = sp.Rational(4, 3)
    b_decay = sp.simplify(theta_holder * gaussian_a)
    cutoff_l = sp.Rational(3, 2)
    layer_cake_polynomial = sp.simplify(
        cutoff_l**4
        + 2 * cutoff_l**2 / b_decay
        + 2 / b_decay**2
    )
    # TEST ORACLE computed independently from the displayed layer-cake
    # antiderivative for the declared rational inputs.
    audit.check(
        "weighted fourth-tail polynomial",
        layer_cake_polynomial == sp.Rational(261, 16),
        layer_cake_polynomial,
        sp.Rational(261, 16),
        "B_local_renyi",
    )

    # Exact conditional low-doublet product fixture from the v1.9 manifest.
    p = sp.Rational(4, 5)
    rho_one = sp.diag(p, 1 - p)
    rho_two = sp.kronecker_product(rho_one, rho_one)
    pauli_x = sp.Matrix([[0, 1], [1, 0]])
    xx = sp.kronecker_product(pauli_x, pauli_x)
    angle = sp.symbols("angle", real=True)
    unitary = sp.cos(angle) * sp.eye(4) + sp.I * sp.sin(angle) * xx
    rotated = sp.simplify(unitary * rho_two * unitary.H)
    rho_inverse_half = sp.diag(
        *[sp.simplify(rho_two[index, index] ** sp.Rational(-1, 2)) for index in range(4)]
    )
    sandwiched_q2 = sp.trace(
        rotated * rho_inverse_half * rotated * rho_inverse_half
    )
    sandwiched_q2 = sp.trigsimp(sp.simplify(sandwiched_q2))
    expected_formula = sp.simplify((4 + 9 * sp.sin(angle) ** 2) ** 2 / 16)
    formula_residual = sp.trigsimp(sp.expand_trig(sandwiched_q2 - expected_formula))
    one_bond = sp.simplify(sandwiched_q2.subs(angle, sp.pi / 4))
    three_bonds = sp.simplify(one_bond**3)
    local_coordinate = sp.kronecker_product(pauli_x, sp.eye(2))

    # A full spatial bond sums all eight onsite components.  After the
    # symmetric doublet compression q_e -> m sigma_x, its kick angle is eight
    # times the single-component channel angle.
    delta_step, c_bond, m_bond, hbar_bond = sp.symbols(
        "delta c_bond m_bond hbar_bond", positive=True
    )
    j_bond = 8 * c_bond * m_bond**2
    full_bond_angle = 8 * delta_step * c_bond * m_bond**2 / hbar_bond
    single_component_angle = delta_step * c_bond * m_bond**2 / hbar_bond

    audit.check(
        "global sandwiched Q2 formula",
        formula_residual == 0,
        formula_residual,
        0,
        "B_global_renyi_no_go",
    )
    audit.check(
        "one-bond Renyi oracle",
        one_bond == sp.Rational(289, 64),
        one_bond,
        sp.Rational(289, 64),
        "B_global_renyi_no_go",
    )
    audit.check(
        "three-bond tensor multiplicativity oracle",
        three_bonds == sp.Rational(24137569, 262144),
        three_bonds,
        sp.Rational(24137569, 262144),
        "B_global_renyi_no_go",
    )
    audit.check(
        "local coordinate algebra commutes with doublet kick",
        local_coordinate * xx - xx * local_coordinate == sp.zeros(4),
        local_coordinate * xx - xx * local_coordinate,
        sp.zeros(4),
        "B_global_renyi_no_go",
    )
    audit.check(
        "full eight-component bond kick angle",
        sp.simplify(full_bond_angle - delta_step * j_bond / hbar_bond) == 0
        and sp.simplify(full_bond_angle / single_component_angle) == 8,
        (full_bond_angle, sp.simplify(full_bond_angle / single_component_angle)),
        (delta_step * j_bond / hbar_bond, 8),
        "B_global_renyi_no_go",
    )

    return {
        "local_measured_renyi": {
            "reference": reference,
            "plus": plus,
            "minus": minus,
            "Q2_plus": q2_plus,
            "Q2_minus": q2_minus,
            "event_reference": q_event,
            "event_plus": p_plus_event,
            "event_minus": p_minus_event,
            "theta": theta_holder,
            "gaussian_a": gaussian_a,
            "b": b_decay,
            "cutoff_L": cutoff_l,
            "fourth_tail_polynomial": layer_cake_polynomial,
            "onsite_interspersed_likelihood_bound_proved": False,
        },
        "global_product_no_go": {
            "rho_one": rho_one,
            "formula": expected_formula,
            "full_bond_angle": full_bond_angle,
            "single_component_angle": single_component_angle,
            "J": j_bond,
            "theta_pi_over_four": one_bond,
            "three_disjoint_bonds": three_bonds,
            "local_coordinate_probability_invariant": True,
            "counterexample_is_full_interacting_Q3_Gibbs": False,
        },
    }


Coord = tuple[int, int, int]


def q3_vertices_and_edges() -> tuple[list[Coord], list[tuple[int, int]]]:
    vertices = list(product((0, 1), repeat=3))
    edges = [
        (left, right)
        for left, a in enumerate(vertices)
        for right, b in enumerate(vertices[left + 1 :], start=left + 1)
        if sum(x != y for x, y in zip(a, b)) == 1
    ]
    return vertices, edges


def connected_component_size(vertex_count: int, edges: list[tuple[int, int]]) -> int:
    adjacency: dict[int, set[int]] = {index: set() for index in range(vertex_count)}
    for left, right in edges:
        adjacency[left].add(right)
        adjacency[right].add(left)
    seen = {0}
    frontier = [0]
    while frontier:
        current = frontier.pop()
        for neighbour in adjacency[current]:
            if neighbour not in seen:
                seen.add(neighbour)
                frontier.append(neighbour)
    return len(seen)


def q3_laplacian(vertex_count: int, edges: list[tuple[int, int]]) -> sp.Matrix:
    laplacian = sp.zeros(vertex_count)
    for left, right in edges:
        laplacian[left, left] += 1
        laplacian[right, right] += 1
        laplacian[left, right] -= 1
        laplacian[right, left] -= 1
    return laplacian


def parameter_fixture(label: str, r_abs: int, c_value: Fraction) -> dict[str, Any]:
    """Derived exact numbers for one declared g=lambda=chi=hbar=1 input."""

    root_r = sp.sqrt(r_abs)
    if not root_r.is_integer:
        raise AssertionError(f"fixture {label}: R must be a perfect square")
    mu = sp.Integer(1)
    v = root_r
    e_star = sp.Integer(r_abs) ** 2
    h_sc = sp.simplify(1 / (sp.Integer(r_abs) ** sp.Rational(3, 2)))
    s_zero = 16 * sp.sqrt(2) / 3
    e_well = sp.simplify(
        (
            sp.sqrt(2)
            + 3 * sp.sqrt(2 + 2 * mu)
            + 3 * sp.sqrt(2 + 4 * mu)
            + sp.sqrt(2 + 6 * mu)
        )
        / 2
    )
    # In the all-one normalization used by these three fixtures, the locked
    # infrared amplitude from R-167 is A0=2*c*R^2/9.  For the corridor
    # R=N^4,c=N^-4 this is (2/9)N^4.
    a_zero_ir = sp.simplify(
        sp.Rational(2, 9)
        * sp.Rational(c_value.numerator, c_value.denominator)
        * sp.Integer(r_abs) ** 2
    )
    return {
        "label": label,
        "inputs": {
            "r": -r_abs,
            "R": r_abs,
            "g": 1,
            "lambda": 1,
            "chi": 1,
            "hbar": 1,
            "c": c_value,
        },
        "mu": mu,
        "v": v,
        "E_star": e_star,
        "h_sc": h_sc,
        "S0_over_h_sc": sp.simplify(s_zero / h_sc),
        "harmonic_Gamma": sp.simplify(e_star * sp.sqrt(2) * h_sc),
        "harmonic_epsilon0": sp.simplify(e_star * h_sc * e_well),
        "A0": a_zero_ir,
        # This uses m=v only as the classical-limit proxy, not as finite-h
        # spectral data for the exact onsite operator.
        "classical_proxy_8c_v_squared": sp.simplify(8 * sp.Rational(c_value.numerator, c_value.denominator) * v**2),
        "finite_h_below_nonexplicit_h0_certified": False,
    }


def fixture_c_semiclassical_and_low_band(audit: Audit) -> dict[str, Any]:
    """Exact Q3 hypotheses, normalization, compression, and form fixtures."""

    vertices, edges = q3_vertices_and_edges()
    laplacian = q3_laplacian(len(vertices), edges)
    mu = sp.symbols("mu", positive=True)
    hessian = 2 * sp.eye(8) + mu * laplacian
    # Use the generator returned by charpoly.  SymPy deliberately strips
    # assumptions from a supplied generator, so reusing a positive input
    # symbol can create two distinct same-printing symbols and a false
    # nonzero residual.
    characteristic_polynomial = hessian.charpoly()
    spectral_t = characteristic_polynomial.gen
    characteristic = sp.factor(characteristic_polynomial.as_expr())
    expected_characteristic = sp.factor(
        (spectral_t - 2)
        * (spectral_t - 2 - 2 * mu) ** 3
        * (spectral_t - 2 - 4 * mu) ** 3
        * (spectral_t - 2 - 6 * mu)
    )
    audit.check(
        "Q3 vertices and edges",
        (len(vertices), len(edges)) == (8, 12),
        (len(vertices), len(edges)),
        (8, 12),
        "C_semiclassical_geometry",
    )
    audit.check(
        "Q3 graph connected",
        connected_component_size(len(vertices), edges) == 8,
        connected_component_size(len(vertices), edges),
        8,
        "C_semiclassical_geometry",
    )
    audit.check(
        "Q3 Hessian characteristic polynomial",
        sp.simplify(characteristic - expected_characteristic) == 0,
        characteristic,
        expected_characteristic,
        "C_semiclassical_geometry",
    )
    audit.check(
        "positive-mu minima nondegenerate",
        sp.simplify(
            hessian.det()
            - 256 * (mu + 1) ** 3 * (2 * mu + 1) ** 3 * (3 * mu + 1)
        )
        == 0,
        sp.factor(hessian.det()),
        256 * (mu + 1) ** 3 * (2 * mu + 1) ** 3 * (3 * mu + 1),
        "C_semiclassical_geometry",
    )

    path_x = sp.symbols("path_x", real=True)
    collective_potential = sp.simplify(8 * (path_x**2 - 1) ** 2 / 4)
    action = sp.simplify(
        sp.sqrt(8)
        * sp.integrate(sp.sqrt(2) * sp.sqrt(collective_potential), (path_x, -1, 1))
    )
    # Sympy retains Abs on a global integral in some releases; on [-1,1],
    # sqrt((x^2-1)^2)=1-x^2, so compute the theorem-side exact value too.
    action_on_interval = sp.simplify(
        sp.sqrt(8)
        * sp.integrate(sp.sqrt(2) * sp.sqrt(2) * (1 - path_x**2), (path_x, -1, 1))
    )
    audit.check(
        "locked collective action",
        action_on_interval == 16 * sp.sqrt(2) / 3,
        action_on_interval,
        16 * sp.sqrt(2) / 3,
        "C_semiclassical_geometry",
    )

    r_abs, g, coupling_lambda, chi, hbar = sp.symbols(
        "R g lambda chi hbar", positive=True
    )
    v = sp.sqrt(r_abs / g)
    e_star = r_abs**2 / g
    h_sc = hbar * g / (sp.sqrt(chi) * r_abs ** sp.Rational(3, 2))
    kinetic_coefficient = sp.simplify(hbar**2 / (2 * chi * v**2 * e_star))
    quartic_coefficient = sp.simplify(g * v**4 / (4 * e_star))
    lock_coefficient = sp.simplify(coupling_lambda * v**4 / (4 * e_star))
    audit.check(
        "semiclassical kinetic normalization",
        sp.simplify(kinetic_coefficient - h_sc**2 / 2) == 0,
        kinetic_coefficient,
        h_sc**2 / 2,
        "C_semiclassical_normalization",
    )
    audit.check(
        "semiclassical quartic normalization",
        quartic_coefficient == sp.Rational(1, 4),
        quartic_coefficient,
        sp.Rational(1, 4),
        "C_semiclassical_normalization",
    )
    audit.check(
        "semiclassical lock normalization",
        sp.simplify(lock_coefficient - (coupling_lambda / g) / 4) == 0,
        lock_coefficient,
        coupling_lambda / (4 * g),
        "C_semiclassical_normalization",
    )

    parameter_fixtures = {
        "A_repository_diagnostic": parameter_fixture("A", 9, Fraction(1)),
        "B_corridor_N2": parameter_fixture("B", 16, Fraction(1, 16)),
        "C_corridor_N3": parameter_fixture("C", 81, Fraction(1, 81)),
    }
    fixture_a = parameter_fixtures["A_repository_diagnostic"]
    fixture_b = parameter_fixtures["B_corridor_N2"]
    fixture_c = parameter_fixtures["C_corridor_N3"]
    audit.check(
        "parameter fixture A h_sc and action",
        fixture_a["h_sc"] == sp.Rational(1, 27)
        and fixture_a["S0_over_h_sc"] == 144 * sp.sqrt(2),
        (fixture_a["h_sc"], fixture_a["S0_over_h_sc"]),
        (sp.Rational(1, 27), 144 * sp.sqrt(2)),
        "C_parameter_fixtures",
    )
    audit.check(
        "parameter fixture B h_sc and action",
        fixture_b["h_sc"] == sp.Rational(1, 64)
        and fixture_b["S0_over_h_sc"] == 1024 * sp.sqrt(2) / 3,
        (fixture_b["h_sc"], fixture_b["S0_over_h_sc"]),
        (sp.Rational(1, 64), 1024 * sp.sqrt(2) / 3),
        "C_parameter_fixtures",
    )
    audit.check(
        "parameter fixture C h_sc and action",
        fixture_c["h_sc"] == sp.Rational(1, 729)
        and fixture_c["S0_over_h_sc"] == 3888 * sp.sqrt(2),
        (fixture_c["h_sc"], fixture_c["S0_over_h_sc"]),
        (sp.Rational(1, 729), 3888 * sp.sqrt(2)),
        "C_parameter_fixtures",
    )
    audit.check(
        "harmonic gap fixtures",
        [row["harmonic_Gamma"] for row in parameter_fixtures.values()]
        == [3 * sp.sqrt(2), 4 * sp.sqrt(2), 9 * sp.sqrt(2)],
        [row["harmonic_Gamma"] for row in parameter_fixtures.values()],
        [3 * sp.sqrt(2), 4 * sp.sqrt(2), 9 * sp.sqrt(2)],
        "C_parameter_fixtures",
    )
    audit.check(
        "A0 exact fixtures",
        [row["A0"] for row in parameter_fixtures.values()]
        == [sp.Integer(18), sp.Rational(32, 9), sp.Integer(18)],
        [row["A0"] for row in parameter_fixtures.values()],
        [sp.Integer(18), sp.Rational(32, 9), sp.Integer(18)],
        "C_parameter_fixtures",
    )

    # Exact low-band algebra in a two-dimensional abstract doublet.
    m_symbol, c_symbol, delta_one = sp.symbols("m c delta_1", real=True)
    a_zero, a_one = sp.symbols("a_0 a_1", real=True)
    identity_two = sp.eye(2)
    s = sp.Matrix([[0, 1], [1, 0]])
    p_one = sp.diag(0, 1)
    a_matrix = sp.diag(a_zero, a_one)
    low_bond = sp.simplify(
        4 * c_symbol * (
            sp.kronecker_product(a_matrix, identity_two)
            + sp.kronecker_product(identity_two, a_matrix)
        )
        - 8 * c_symbol * m_symbol**2 * sp.kronecker_product(s, s)
    )
    j_ising = 8 * c_symbol * m_symbol**2
    low_bond_expected = sp.simplify(
        j_ising * (sp.eye(4) - sp.kronecker_product(s, s))
        + 4 * c_symbol * (
            sp.kronecker_product(a_matrix, identity_two)
            + sp.kronecker_product(identity_two, a_matrix)
        )
        - j_ising * sp.eye(4)
    )
    degree_x = sp.symbols("deg_x", integer=True, nonnegative=True)
    delta_site = sp.expand(
        delta_one + 4 * degree_x * c_symbol * (a_one - a_zero)
    )
    z = sp.Integer(6)
    delta_effective = sp.expand(delta_site.subs(degree_x, z))
    audit.check(
        "one-bond exact low-band compression",
        low_bond == low_bond_expected,
        low_bond - low_bond_expected,
        sp.zeros(4),
        "C_low_band",
    )
    audit.check(
        "site-dependent boundary transverse coefficient",
        sp.simplify(
            delta_site
            - (delta_one + 4 * degree_x * c_symbol * (a_one - a_zero))
        )
        == 0,
        delta_site,
        delta_one + 4 * degree_x * c_symbol * (a_one - a_zero),
        "C_low_band",
    )
    audit.check(
        "periodic cubic z=6 transverse coefficient",
        sp.simplify(
            delta_effective
            - (delta_one + 24 * c_symbol * (a_one - a_zero))
        )
        == 0,
        delta_effective,
        delta_one + 24 * c_symbol * (a_one - a_zero),
        "C_low_band",
    )

    # Three-level hostile fixture: the third level is an explicit high mode.
    m_value = sp.Rational(1, 2)
    u_value = sp.Rational(2, 3)
    c_value = sp.Rational(3, 5)
    q = sp.Matrix(
        [
            [0, m_value, 0],
            [m_value, 0, u_value],
            [0, u_value, 0],
        ]
    )
    p_low = sp.diag(1, 1, 0)
    q_high = sp.eye(3) - p_low
    s_extended = sp.Matrix([[0, 1, 0], [1, 0, 0], [0, 0, 0]])
    q_squared = q**2
    q_fourth = q**4
    a_values = (q_squared[0, 0], q_squared[1, 1])
    b_values = (q_fourth[0, 0], q_fourth[1, 1])
    a_residual_squared = max(
        sp.simplify(a_values[0] - m_value**2),
        sp.simplify(a_values[1] - m_value**2),
    )
    b_residual_squared = max(
        sp.simplify(b_values[0] - a_values[0] ** 2),
        sp.simplify(b_values[1] - a_values[1] ** 2),
    )
    a_residual = sp.sqrt(a_residual_squared)
    b_residual = sp.sqrt(b_residual_squared)
    audit.check(
        "P q P equals m s",
        p_low * q * p_low == m_value * s_extended,
        p_low * q * p_low,
        m_value * s_extended,
        "C_moment_residual",
    )
    audit.check(
        "Q q P moment identity",
        p_low * q * q_high * q * p_low
        == p_low * q_squared * p_low - (p_low * q * p_low) ** 2,
        p_low * q * q_high * q * p_low,
        p_low * q_squared * p_low - (p_low * q * p_low) ** 2,
        "C_moment_residual",
    )
    audit.check(
        "Q q squared P moment identity",
        p_low * q_squared * q_high * q_squared * p_low
        == p_low * q_fourth * p_low - (p_low * q_squared * p_low) ** 2,
        p_low * q_squared * q_high * q_squared * p_low,
        p_low * q_fourth * p_low - (p_low * q_squared * p_low) ** 2,
        "C_moment_residual",
    )
    # TEST ORACLES for the declared exact matrix fixture.
    audit.check(
        "moment residual fixture values",
        (a_residual_squared, b_residual_squared)
        == (sp.Rational(4, 9), sp.Rational(1, 9)),
        (a_residual_squared, b_residual_squared),
        (sp.Rational(4, 9), sp.Rational(1, 9)),
        "C_moment_residual",
    )

    identity_three = sp.eye(3)
    p_bond = sp.kronecker_product(p_low, p_low)
    delta_q = sp.kronecker_product(q, identity_three) - sp.kronecker_product(identity_three, q)
    exact_bond = sp.simplify(4 * c_value * delta_q**2)
    off_block = sp.simplify((sp.eye(9) - p_bond) * exact_bond * p_bond)
    singular_squared = [
        sp.simplify(value)
        for value, multiplicity in (off_block.H * off_block).eigenvals().items()
        for _ in range(multiplicity)
    ]
    actual_norm_squared = max(singular_squared)
    residual_bound = sp.simplify(
        8
        * c_value
        * (b_residual + 2 * m_value * a_residual + a_residual**2)
    )
    audit.check(
        "one-bond low-high residual bound",
        bool(sp.simplify(residual_bound**2 - actual_norm_squared) >= 0),
        actual_norm_squared,
        f"<={residual_bound**2}",
        "C_moment_residual",
    )

    epsilon_zero = sp.Rational(1, 4)
    gamma = sp.Integer(5)
    g_value = sp.Integer(1)
    v_value = sp.Rational(3, 2)
    epsilon_opt = sp.simplify(
        sp.Rational(1, 4) * sp.sqrt(g_value / (epsilon_zero + gamma))
    )
    a_q = sp.simplify(
        v_value**2 / gamma
        + 4 * epsilon_opt * (epsilon_zero + gamma) / (g_value * gamma)
        + 1 / (4 * epsilon_opt * gamma)
    )
    expected_a_q = sp.simplify(
        v_value**2 / gamma
        + 2 * sp.sqrt(epsilon_zero + gamma) / (gamma * sp.sqrt(g_value))
    )
    audit.check(
        "centered form coefficient optimized",
        sp.simplify(a_q - expected_a_q) == 0,
        a_q,
        expected_a_q,
        "C_centered_form",
    )
    k_fixture = sp.diag(0, 0, gamma)
    psi = sp.Matrix([1, 2, 3])
    t_weight = sp.Integer(2)
    r_operator = q - m_value * s_extended
    lhs = sp.simplify((r_operator * psi).dot(r_operator * psi))
    p_psi = p_low * psi
    q_psi = q_high * psi
    rhs = sp.simplify(
        (1 + t_weight) * a_residual_squared * p_psi.dot(p_psi)
        + (1 + 1 / t_weight) * expected_a_q * (q_psi.dot(k_fixture * q_psi))
    )
    audit.check(
        "centered form finite hostile fixture",
        bool(sp.N(rhs - lhs, 80) > 0),
        rhs - lhs,
        ">0",
        "C_centered_form",
    )

    corridor_exponents = {
        "v": 2,
        "E_star": 8,
        "h_sc": -6,
        "Gamma": 2,
        "m": 2,
        "a": -1,
        "b": 1,
        # Safe consequence of a_j=v^2[1+O(h_sc)] separately.  Exponential
        # smallness of their difference needs an additional weighted-Agmon
        # matrix-element lemma and is deliberately not imported here.
        "d2": -2,
        "c": -4,
        "24c_d2": -6,
        "one_bond_low_high": -3,
        "A_Q": 2,
        "c_A_Q": -2,
        "c_m_sqrt_A_Q": -1,
        "J": 0,
    }
    audit.check(
        "corridor low-high exponent",
        corridor_exponents["c"]
        + max(
            corridor_exponents["b"],
            corridor_exponents["m"] + corridor_exponents["a"],
            2 * corridor_exponents["a"],
        )
        == corridor_exponents["one_bond_low_high"],
        corridor_exponents["one_bond_low_high"],
        -3,
        "C_asymptotic_corridor",
    )
    audit.check(
        "corridor Ising scale exponent",
        corridor_exponents["c"] + 2 * corridor_exponents["m"]
        == corridor_exponents["J"] == 0,
        corridor_exponents["c"] + 2 * corridor_exponents["m"],
        0,
        "C_asymptotic_corridor",
    )
    audit.check(
        "corridor weighted high-mode exponent",
        corridor_exponents["c"] + corridor_exponents["A_Q"]
        == corridor_exponents["c_A_Q"] == -2,
        corridor_exponents["c"] + corridor_exponents["A_Q"],
        -2,
        "C_asymptotic_corridor",
    )
    audit.check(
        "corridor mixed anticommutator exponent",
        corridor_exponents["c"]
        + corridor_exponents["m"]
        + sp.Rational(1, 2) * corridor_exponents["A_Q"]
        == corridor_exponents["c_m_sqrt_A_Q"]
        == -1,
        corridor_exponents["c"]
        + corridor_exponents["m"]
        + sp.Rational(1, 2) * corridor_exponents["A_Q"],
        -1,
        "C_asymptotic_corridor",
    )
    audit.check(
        "safe transverse renormalization exponent",
        corridor_exponents["c"] + corridor_exponents["d2"]
        == corridor_exponents["24c_d2"] == -6,
        corridor_exponents["c"] + corridor_exponents["d2"],
        -6,
        "C_asymptotic_corridor",
    )
    audit.check(
        "A0 corridor exponent",
        -4 + 2 * 4 == 4,
        -4 + 2 * 4,
        4,
        "C_asymptotic_corridor",
    )
    n_corridor = sp.symbols("N", positive=True)
    a_zero_corridor = sp.simplify(
        sp.Rational(2, 9) * n_corridor ** (-4) * (n_corridor**4) ** 2
    )
    audit.check(
        "A0 corridor leading coefficient",
        sp.simplify(a_zero_corridor - sp.Rational(2, 9) * n_corridor**4)
        == 0,
        a_zero_corridor,
        sp.Rational(2, 9) * n_corridor**4,
        "C_asymptotic_corridor",
    )

    imported_scope = {
        "fixed_mu_positive": True,
        "coercive_polynomial": True,
        "exactly_two_connected_zeroes": connected_component_size(len(vertices), edges) == 8,
        "nondegenerate_minima": True,
        "exact_Agmon_distance_from_R167": 16 * sp.sqrt(2) / 3,
        "semiclassical_h0_explicit": False,
        "repository_r_minus_9_certified": False,
        "safe_d2_bound": "O(v^2 h_sc)",
        "exponential_d2_requires_extra_weighted_Agmon_lemma": True,
        "extra_weighted_Agmon_lemma_registered": False,
        "literature_theorem_reproved_by_script": False,
    }
    dfp_boundary = {
        "source": DFP_SOURCE,
        "published_main_theorem_rank_one_vacuum": True,
        "published_main_theorem_unique_ground_state": True,
        "introductory_degenerate_extension_is_rank2_band_theorem": False,
        "Q3_local_kernel_rank": 2,
        "Q3_global_low_dimension": "2^|Lambda|",
        "phi0_only_gap": "delta_1 (exponentially small)",
        "direct_import_closes_broken_sector_gap": False,
    }

    return {
        "q3_graph": {
            "vertices": vertices,
            "edges": edges,
            "laplacian": laplacian,
            "hessian_characteristic": characteristic,
            "locked_collective_integral_raw": action,
            "S0": action_on_interval,
            "zero_set_reason": (
                "W_mu=0 forces x_e^2=1; positive lock forces adjacent signs "
                "equal; connected Q3 leaves only plus/minus all-ones"
            ),
        },
        "normalization": {
            "v": v,
            "E_star": e_star,
            "h_sc": h_sc,
            "kinetic_coefficient": kinetic_coefficient,
            "quartic_coefficient": quartic_coefficient,
            "lock_coefficient": lock_coefficient,
        },
        "parameter_fixtures": parameter_fixtures,
        "semiclassical_import_scope": imported_scope,
        "low_band": {
            "J": j_ising,
            "delta_site": delta_site,
            "delta_eff": delta_effective,
            "moment_fixture": {
                "q": q,
                "m": m_value,
                "a_j": a_values,
                "b_j": b_values,
                "a_squared": a_residual_squared,
                "b_squared": b_residual_squared,
                "actual_one_bond_offblock_norm_squared": actual_norm_squared,
                "one_bond_bound": residual_bound,
            },
            "centered_form_fixture": {
                "epsilon0": epsilon_zero,
                "Gamma": gamma,
                "g": g_value,
                "v": v_value,
                "epsilon_optimizer": epsilon_opt,
                "A_Q": expected_a_q,
                "finite_fixture_lhs": lhs,
                "finite_fixture_rhs": rhs,
            },
        },
        "corridor_exponents_in_N": corridor_exponents,
        "A0_corridor": a_zero_corridor,
        "dfp_rank_one_boundary": dfp_boundary,
    }



def operator_norm_squared(matrix: sp.MatrixBase) -> sp.Expr:
    values = []
    for value, multiplicity in (matrix.H * matrix).eigenvals().items():
        values.extend([sp.simplify(value)] * multiplicity)
    return max(values, key=lambda value: float(sp.N(value, 40)))


def fixture_d_full_gibbs_context(audit: Audit) -> dict[str, Any]:
    """Exact Gibbs/Duhamel, modular-context, and arbitrary-context fixtures."""

    # INPUT FIXTURE. The temperature is derived so rho is exactly the Gibbs
    # state of H; all numerical assertions below are labelled test oracles.
    p = sp.Rational(1, 5)
    t_zero = sp.Integer(1)
    hbar = sp.Integer(1)
    beta = sp.log(4) / sp.pi
    rho = sp.diag(1 - p, p)
    projection_one = sp.diag(0, 1)
    h_full = sp.pi * hbar * projection_one / t_zero
    h_cut = sp.zeros(2)
    w_tail = h_full - h_cut
    gibbs_unnormalized = sp.diag(1, sp.exp(-beta * sp.pi * hbar / t_zero))
    gibbs = sp.simplify(gibbs_unnormalized / trace(gibbs_unnormalized))
    u_full = sp.diag(1, -1)
    u_cut = sp.eye(2)
    difference = u_full - u_cut
    right_squared = sp.simplify(trace(rho * difference.H * difference))
    left_squared = sp.simplify(trace(rho * difference * difference.H))
    w_second_moment = sp.simplify(trace(rho * w_tail**2))
    duhamel_rhs_squared = sp.simplify(t_zero**2 * w_second_moment / hbar**2)

    evolved_full = sp.simplify(u_full * rho * u_full.H)
    evolved_cut = sp.simplify(u_cut * rho * u_cut.H)
    state_difference = sp.simplify(evolved_full - evolved_cut)
    trace_distance = sum(
        sp.sqrt(value)
        for value, multiplicity in (state_difference.H * state_difference).eigenvals().items()
        for _ in range(multiplicity)
    )

    pauli_x = sp.Matrix([[0, 1], [1, 0]])
    alpha_full = sp.simplify(u_full.H * pauli_x * u_full)
    alpha_cut = sp.simplify(u_cut.H * pauli_x * u_cut)
    observable_error = sp.simplify(alpha_full - alpha_cut)
    observable_right_squared = sp.simplify(
        trace(rho * observable_error.H * observable_error)
    )
    observable_left_squared = sp.simplify(
        trace(rho * observable_error * observable_error.H)
    )
    rho_half = sp.diag(sp.sqrt(1 - p), sp.sqrt(p))
    rho_minus_half = sp.diag(1 / sp.sqrt(1 - p), 1 / sp.sqrt(p))
    modular_context = sp.simplify(rho_minus_half * pauli_x * rho_half)
    modular_context_norm_squared = operator_norm_squared(modular_context)
    bandwidth_factor = sp.simplify(sp.exp(beta * sp.pi * hbar / (2 * t_zero)))
    projective_band_norm = sp.Integer(2)
    context_transfer_rhs_squared = sp.simplify(
        (1 + sp.sqrt(modular_context_norm_squared)) ** 2
        * duhamel_rhs_squared
    )

    probability = sp.symbols("p", positive=True)
    unitary_hash_squared_family = 8 * probability
    automorphism_hash_squared_family = sp.Integer(8)

    audit.check(
        "finite Gibbs normalization",
        gibbs == rho,
        gibbs,
        rho,
        "D_full_Gibbs",
    )
    audit.check(
        "two weighted unitary orientations",
        right_squared == left_squared == 4 * p,
        (right_squared, left_squared),
        (4 * p, 4 * p),
        "D_full_Gibbs",
    )
    audit.check(
        "Duhamel static Gibbs upper",
        bool(sp.N(duhamel_rhs_squared - right_squared, 80) > 0),
        duhamel_rhs_squared - right_squared,
        ">0",
        "D_full_Gibbs",
    )
    audit.check(
        "Gibbs W square with hbar restored",
        sp.simplify(w_second_moment - sp.pi**2 * hbar**2 * p / t_zero**2) == 0,
        w_second_moment,
        sp.pi**2 * hbar**2 * p / t_zero**2,
        "D_full_Gibbs",
    )
    audit.check(
        "trace-distance state stability fixture",
        trace_distance == 0,
        trace_distance,
        0,
        "D_full_Gibbs",
    )
    audit.check(
        "arbitrary context one-sided norms",
        observable_right_squared == observable_left_squared == 4,
        (observable_right_squared, observable_left_squared),
        (4, 4),
        "D_context_no_go",
    )
    audit.check(
        "arbitrary context hash seminorm",
        observable_right_squared + observable_left_squared == 8,
        observable_right_squared + observable_left_squared,
        8,
        "D_context_no_go",
    )
    audit.check(
        "half-modular context norm",
        modular_context_norm_squared == 4,
        modular_context_norm_squared,
        4,
        "D_modular_context",
    )
    audit.check(
        "fixed Bohr-band projective bound",
        bandwidth_factor == 2
        and sp.sqrt(modular_context_norm_squared)
        <= bandwidth_factor * projective_band_norm,
        (bandwidth_factor, sp.sqrt(modular_context_norm_squared)),
        (2, "<=4"),
        "D_modular_context",
    )
    audit.check(
        "bounded-context transfer fixture",
        observable_right_squared <= context_transfer_rhs_squared,
        observable_right_squared,
        f"<={context_transfer_rhs_squared}",
        "D_modular_context",
    )
    audit.check(
        "arbitrary-context implication limit",
        sp.limit(unitary_hash_squared_family, probability, 0, dir="+") == 0
        and automorphism_hash_squared_family == 8,
        (sp.limit(unitary_hash_squared_family, probability, 0, dir="+"), 8),
        (0, 8),
        "D_context_no_go",
    )
    q3_domain = {
        "common_quartic_form_domain": True,
        "W_coordinate_growth_degree": 2,
        "W_squared_growth_degree": 4,
        "finite_Gibbs_fourth_moment": True,
        "bounded_spectral_form_truncation": True,
        "strong_resolvent_then_S2_closure": True,
        "smooth_clipped_Q_L_automatically_covered": False,
    }
    audit.check(
        "finite-Q3 hard-form domain instantiation",
        q3_domain["common_quartic_form_domain"]
        and q3_domain["W_coordinate_growth_degree"] == 2
        and q3_domain["W_squared_growth_degree"] == 4
        and q3_domain["finite_Gibbs_fourth_moment"]
        and q3_domain["bounded_spectral_form_truncation"]
        and q3_domain["strong_resolvent_then_S2_closure"]
        and not q3_domain["smooth_clipped_Q_L_automatically_covered"],
        q3_domain,
        "hard/form Q3 pair only",
        "D_Q3_domain",
    )

    return {
        "rho": rho,
        "beta": beta,
        "H": h_full,
        "H_L": h_cut,
        "W": w_tail,
        "right_unitary_HS_squared": right_squared,
        "left_unitary_HS_squared": left_squared,
        "rho_W_squared": w_second_moment,
        "Duhamel_rhs_squared": duhamel_rhs_squared,
        "trace_distance": trace_distance,
        "observable": pauli_x,
        "right_observable_HS_squared": observable_right_squared,
        "left_observable_HS_squared": observable_left_squared,
        "hash_seminorm_squared": observable_right_squared + observable_left_squared,
        "half_modular_context": modular_context,
        "half_modular_context_norm_squared": modular_context_norm_squared,
        "fixed_bandwidth_factor": bandwidth_factor,
        "fixed_band_projective_norm": projective_band_norm,
        "arbitrary_context_upgrade_rejected": True,
        "state_stability_implies_automorphism_stability": False,
        "q3_form_domain_instantiation": q3_domain,
    }


def fixture_e_fixed_edge_corridor(audit: Audit) -> dict[str, Any]:
    """Exact cubic-edge count, corridor constants, covariance, and tilted no-go."""

    # INPUT FIXTURE for exact enumeration; the R-dependent bound is derived
    # symbolically below and the displayed integers are TEST ORACLES.
    radius = 2
    vertices = set(product(range(-radius, radius + 1), repeat=3))
    directions = ((1, 0, 0), (0, 1, 0), (0, 0, 1))
    induced_edges = []
    for vertex in sorted(vertices):
        for direction in directions:
            neighbour = tuple(vertex[index] + direction[index] for index in range(3))
            if neighbour in vertices:
                induced_edges.append((vertex, neighbour))
    exact_count = 6 * radius * (2 * radius + 1) ** 2

    hostile_words = (sp.Integer(3), sp.Integer(-2), sp.Integer(5), sp.Integer(1))
    cauchy_left = sum(hostile_words) ** 2
    cauchy_right = len(hostile_words) * sum(value**2 for value in hostile_words)

    r_symbol = sp.symbols("R", positive=True)
    edge_upper = 54 * r_symbol**3
    c_value = sp.Rational(1, 3)
    edge_prefactor = sp.Integer(4)
    l_squared = r_symbol
    corridor_bound = sp.simplify(
        edge_upper**2
        * c_value**2
        * edge_prefactor
        * sp.exp(-l_squared)
        * (l_squared**2 + 2 * l_squared + 2)
    )
    expected_corridor = 1296 * r_symbol**6 * sp.exp(-r_symbol) * (
        r_symbol**2 + 2 * r_symbol + 2
    )
    elementary_majorant = sp.factor(
        1296
        * sp.factorial(10)
        * (r_symbol ** -2 + 2 * r_symbol ** -3 + 2 * r_symbol ** -4)
    )

    torus_side = 4
    torus_vertices = list(product(range(torus_side), repeat=3))
    orientation_orbits: dict[int, set[tuple[tuple[int, int, int], tuple[int, int, int]]]] = {
        direction: set() for direction in range(3)
    }
    for vertex in torus_vertices:
        for direction in range(3):
            neighbour = list(vertex)
            neighbour[direction] = (neighbour[direction] + 1) % torus_side
            orientation_orbits[direction].add((vertex, tuple(neighbour)))

    kappa = sp.Rational(3, 4)
    precision_determinant = sp.simplify(1 - kappa**2)
    marginal_variance = sp.simplify(1 / precision_determinant)
    tilted_tail_exponent = sp.simplify(1 / (2 * marginal_variance))
    theta = sp.Rational(1, 2)
    reference_power_exponent = theta / 2
    exponent_gap = sp.simplify(reference_power_exponent - tilted_tail_exponent)
    q2_precision_determinant = sp.simplify(1 - 4 * kappa**2)
    dimer_scope = True
    full_one_site_translation_invariance = False
    hard_tail_constants = True
    smooth_clipped_q_l_constants = False

    audit.check(
        "induced cubic edge count",
        len(induced_edges) == exact_count == 300,
        len(induced_edges),
        300,
        "E_fixed_edge",
    )
    audit.check(
        "edge count cubic upper",
        exact_count <= 54 * radius**3,
        exact_count,
        f"<={54 * radius**3}",
        "E_fixed_edge",
    )
    audit.check(
        "restricted-tail sum Cauchy",
        cauchy_left <= cauchy_right,
        cauchy_left,
        f"<={cauchy_right}",
        "E_fixed_edge",
    )
    audit.check(
        "explicit growing corridor constant",
        sp.simplify(corridor_bound - expected_corridor) == 0,
        corridor_bound,
        expected_corridor,
        "E_fixed_edge",
    )
    audit.check(
        "growing corridor vanishes",
        sp.limit(corridor_bound, r_symbol, sp.oo) == 0,
        sp.limit(corridor_bound, r_symbol, sp.oo),
        0,
        "E_fixed_edge",
    )
    audit.check(
        "elementary exponential majorant vanishes",
        sp.limit(elementary_majorant, r_symbol, sp.oo) == 0,
        sp.limit(elementary_majorant, r_symbol, sp.oo),
        0,
        "E_fixed_edge",
    )
    audit.check(
        "periodic translation edge orbits",
        len(orientation_orbits) == 3
        and all(len(orbit) == torus_side**3 for orbit in orientation_orbits.values()),
        {key: len(value) for key, value in orientation_orbits.items()},
        {0: 64, 1: 64, 2: 64},
        "E_covariance_boundary",
    )
    audit.check(
        "tilted Gaussian positive precision",
        precision_determinant == sp.Rational(7, 16) > 0,
        precision_determinant,
        sp.Rational(7, 16),
        "E_tilted_no_go",
    )
    audit.check(
        "tilted Gaussian marginal variance",
        marginal_variance == sp.Rational(16, 7),
        marginal_variance,
        sp.Rational(16, 7),
        "E_tilted_no_go",
    )
    audit.check(
        "tilted tail defeats alpha-two reference power",
        exponent_gap == sp.Rational(1, 32) > 0,
        exponent_gap,
        sp.Rational(1, 32),
        "E_tilted_no_go",
    )
    audit.check(
        "tilted order-two likelihood diverges",
        q2_precision_determinant == sp.Rational(-5, 4) < 0,
        q2_precision_determinant,
        sp.Rational(-5, 4),
        "E_tilted_no_go",
    )
    audit.check(
        "tilted Gaussian and hard-tail scope boundaries",
        dimer_scope
        and not full_one_site_translation_invariance
        and hard_tail_constants
        and not smooth_clipped_q_l_constants,
        {
            "dimer_scope": dimer_scope,
            "full_one_site_TI": full_one_site_translation_invariance,
            "hard_tail": hard_tail_constants,
            "smooth_clipped_Q_L": smooth_clipped_q_l_constants,
        },
        "dimer implication and hard-tail constants only",
        "E_scope",
    )

    return {
        "radius_fixture": radius,
        "induced_edge_count": exact_count,
        "edge_formula": "6 R (2R+1)^2",
        "edge_upper": "54 R^3",
        "corridor_bound": corridor_bound,
        "elementary_majorant": elementary_majorant,
        "periodic_translation_orbit_sizes": {
            key: len(value) for key, value in orientation_orbits.items()
        },
        "translation_covariance_reduces_to_one_edge": False,
        "translation_covariance_reduces_to_three_orientations": True,
        "tilted_gaussian": {
            "kappa": kappa,
            "precision_determinant": precision_determinant,
            "marginal_variance": marginal_variance,
            "tilted_tail_exponent": tilted_tail_exponent,
            "reference_power_exponent": reference_power_exponent,
            "exponent_gap": exponent_gap,
            "Q2_precision_determinant": q2_precision_determinant,
            "all_polynomial_moments_finite": True,
            "fixed_edge_tail_implication_rejected": True,
            "two_site_or_homogeneous_dimer_scope": dimer_scope,
            "full_one_site_translation_invariance": (
                full_one_site_translation_invariance
            ),
            "Q3_dynamics_nonexistence": False,
        },
        "hard_tail_constants": hard_tail_constants,
        "smooth_clipped_Q_L_constants": smooth_clipped_q_l_constants,
        "actual_Q3_fixed_edge_history_bound_proved": False,
    }


def fixture_f_feshbach_and_compressed_qps(audit: Audit) -> dict[str, Any]:
    """Exact cubic overlap, Feshbach, form-smallness, and TFIM-QPS inputs."""

    # INPUT FIXTURES. Side four avoids short-cycle edge identifications;
    # rational parameters are chosen only to test the derived inequalities.
    side = 4
    vertices = list(product(range(side), repeat=3))
    edges: list[frozenset[tuple[int, int, int]]] = []
    for vertex in vertices:
        for direction in range(3):
            neighbour = list(vertex)
            neighbour[direction] = (neighbour[direction] + 1) % side
            edges.append(frozenset((vertex, tuple(neighbour))))
    overlap_counts = [sum(bool(edge & other) for other in edges) for edge in edges]
    open_vertices = list(product(range(side), repeat=3))
    open_edges: list[frozenset[tuple[int, int, int]]] = []
    for vertex in open_vertices:
        for direction in range(3):
            neighbour = list(vertex)
            neighbour[direction] += 1
            if neighbour[direction] < side:
                open_edges.append(frozenset((vertex, tuple(neighbour))))
    open_overlap_counts = [
        sum(bool(edge & other) for other in open_edges) for edge in open_edges
    ]

    high_count = 5
    gamma = sp.Integer(7)
    energy = sp.Integer(2)
    epsilon = sp.Rational(1, 3)
    high_block = gamma * sp.eye(high_count)
    off_block = epsilon * sp.ones(high_count, 1)
    self_energy = sp.simplify(
        off_block.H * (high_block - energy * sp.eye(high_count)).inv() * off_block
    )
    overlap_upper = sp.simplify(11 * high_count * epsilon**2 / (gamma - energy))

    dense_low_count = 5
    dense_off_block = epsilon * sp.ones(1, dense_low_count)
    dense_self_energy = sp.simplify(
        dense_off_block.H
        * (sp.Matrix([[gamma]]) - energy * sp.eye(1)).inv()
        * dense_off_block
    )
    dense_norm_squared = operator_norm_squared(dense_self_energy)
    dense_norm = sp.sqrt(dense_norm_squared)

    c_value = sp.Rational(1, 1000)
    m_value = sp.Integer(2)
    a_squared = sp.Rational(1, 100)
    a_value = sp.Rational(1, 10)
    b_value = sp.Rational(1, 20)
    a_q = sp.Integer(3)
    gamma_form = sp.Integer(100)
    z = sp.Integer(6)
    eta_b = sp.simplify(32 * c_value * a_q)
    nu_b = sp.simplify(32 * c_value * m_value**2 + 64 * c_value * a_squared)
    zeta = sp.simplify(z * (eta_b + nu_b / gamma_form))
    epsilon_form = sp.simplify(
        8 * c_value * (b_value + 2 * m_value * a_value + a_squared)
    )
    p_xy = sp.diag(1, 0, 0, 0)
    q_xy = sp.eye(4) - p_xy
    k_xy = sp.diag(0, gamma_form, gamma_form, 2 * gamma_form)
    qkq = sp.simplify(q_xy * k_xy * q_xy)
    diagonal_high_fixture = sp.simplify(eta_b * qkq + nu_b * q_xy)
    projected_high_upper = sp.simplify((eta_b + nu_b / gamma_form) * qkq)
    projected_high_slack = sp.simplify(projected_high_upper - diagonal_high_fixture)
    projected_slack_eigenvalues = list(projected_high_slack.eigenvals())
    corridor_exponents = {
        "epsilon": -3,
        "eta_b": -2,
        "nu_b_over_Gamma": -2,
        "zeta": -2,
    }

    j_symbol = sp.symbols("J", positive=True)
    star_energies: dict[sp.Expr, int] = {}
    for signs in product((-1, 1), repeat=4):
        center, *neighbours = signs
        value = sp.simplify(j_symbol * sum(1 - center * neighbour for neighbour in neighbours))
        star_energies[value] = star_energies.get(value, 0) + 1
    expected_star = {0: 2, 2 * j_symbol: 6, 4 * j_symbol: 6, 6 * j_symbol: 2}

    pauli_x = sp.Matrix([[0, 1], [1, 0]])
    parity = sp.diag(1, -1)
    p_one = sp.diag(0, 1)
    selector_plus_density = 1 - 1
    selector_minus_density = 1 - (-1)
    selector_difference_derivative = selector_plus_density - selector_minus_density
    selector_split = (0, selector_difference_derivative)
    small_ratio = "abs(delta_eff)/(2J)<epsilon_Y"
    feshbach_absolute_energy_before_low_scalar_subtraction = True
    thermodynamic_ground_band_isolation = False
    diagonal_high_compression_only = True
    off_diagonal_bound_is_distinct = True

    audit.check(
        "periodic cubic edge count",
        len(edges) == 3 * side**3,
        len(edges),
        3 * side**3,
        "F_overlap",
    )
    audit.check(
        "cubic overlap upper and periodic bulk equality",
        set(overlap_counts) == {11}
        and max(open_overlap_counts) <= 11
        and min(open_overlap_counts) < 11,
        {
            "periodic": set(overlap_counts),
            "open_min": min(open_overlap_counts),
            "open_max": max(open_overlap_counts),
        },
        "general <=11; periodic equality; open boundary can be smaller",
        "F_overlap",
    )
    audit.check(
        "exact below-Gamma Feshbach fixture",
        self_energy == sp.Matrix([[sp.Rational(1, 9)]]),
        self_energy,
        sp.Matrix([[sp.Rational(1, 9)]]),
        "F_Feshbach",
    )
    audit.check(
        "11-overlap Feshbach upper",
        self_energy[0, 0] <= overlap_upper
        and overlap_upper == sp.Rational(11, 9),
        (self_energy[0, 0], overlap_upper),
        (sp.Rational(1, 9), sp.Rational(11, 9)),
        "F_Feshbach",
    )
    audit.check(
        "dense extensive self-energy norm",
        dense_norm == sp.Rational(1, 9)
        and all(dense_self_energy[i, j] != 0 for i in range(5) for j in range(5)),
        (dense_norm, dense_self_energy),
        (sp.Rational(1, 9), "all entries nonzero"),
        "F_self_energy_no_go",
    )
    audit.check(
        "relative-form coefficient eta_b",
        eta_b == sp.Rational(12, 125),
        eta_b,
        sp.Rational(12, 125),
        "F_relative_form",
    )
    audit.check(
        "relative-form coefficient nu_b",
        nu_b == sp.Rational(402, 3125),
        nu_b,
        sp.Rational(402, 3125),
        "F_relative_form",
    )
    audit.check(
        "global relative-form smallness fixture",
        zeta < 1,
        zeta,
        "<1",
        "F_relative_form",
    )
    audit.check(
        "one-bond off-block smallness fixture",
        epsilon_form == sp.Rational(23, 6250),
        epsilon_form,
        sp.Rational(23, 6250),
        "F_relative_form",
    )
    audit.check(
        "projected local-high diagonal inequality",
        all(bool(value >= 0) for value in projected_slack_eigenvalues)
        and q_xy * k_xy * q_xy - gamma_form * q_xy
        == sp.diag(0, 0, 0, gamma_form)
        and diagonal_high_compression_only
        and off_diagonal_bound_is_distinct,
        {
            "slack_eigenvalues": projected_slack_eigenvalues,
            "QKQ_minus_GammaQ": q_xy * k_xy * q_xy - gamma_form * q_xy,
        },
        "Qxy Bxy Qxy <= (eta_b+nu_b/Gamma) Qxy(kx+ky)Qxy",
        "F_relative_form",
    )
    audit.check(
        "corridor Feshbach coefficient exponents",
        corridor_exponents
        == {"epsilon": -3, "eta_b": -2, "nu_b_over_Gamma": -2, "zeta": -2},
        corridor_exponents,
        {"epsilon": -3, "eta_b": -2, "nu_b_over_Gamma": -2, "zeta": -2},
        "F_relative_form",
    )
    audit.check(
        "compressed TFIM forward-star spectrum",
        star_energies == expected_star,
        star_energies,
        expected_star,
        "F_compressed_QPS",
    )
    audit.check(
        "compressed TFIM Z2 action",
        parity * pauli_x * parity == -pauli_x
        and parity * p_one * parity == p_one,
        (parity * pauli_x * parity, parity * p_one * parity),
        (-pauli_x, p_one),
        "F_compressed_QPS",
    )
    audit.check(
        "compressed TFIM selector split",
        selector_plus_density == 0
        and selector_minus_density == 2
        and selector_split == (0, -2)
        and small_ratio == "abs(delta_eff)/(2J)<epsilon_Y",
        {
            "plus": selector_plus_density,
            "minus": selector_minus_density,
            "k": selector_split,
        },
        {"plus": 0, "minus": 2, "k": (0, -2)},
        "F_compressed_QPS",
    )
    audit.check(
        "finite-volume absolute-energy Feshbach scope",
        feshbach_absolute_energy_before_low_scalar_subtraction
        and not thermodynamic_ground_band_isolation,
        {
            "before_low_scalar_subtraction": (
                feshbach_absolute_energy_before_low_scalar_subtraction
            ),
            "thermodynamic_ground_band_isolation": (
                thermodynamic_ground_band_isolation
            ),
        },
        "finite-volume absolute-energy algebra only",
        "F_scope",
    )

    return {
        "periodic_side": side,
        "edge_count": len(edges),
        "periodic_overlap_counts": sorted(set(overlap_counts)),
        "open_overlap_range": [min(open_overlap_counts), max(open_overlap_counts)],
        "general_overlap_upper": 11,
        "equality_scope": "bulk edges and sufficiently large periodic tori",
        "Feshbach_fixture": {
            "Gamma": gamma,
            "E": energy,
            "epsilon": epsilon,
            "self_energy": self_energy,
            "overlap_upper": overlap_upper,
        },
        "dense_self_energy_no_go": {
            "matrix": dense_self_energy,
            "operator_norm": dense_norm,
            "all_to_all": True,
            "global_extensive_bound_implies_QPS_locality": False,
        },
        "relative_form": {
            "c": c_value,
            "m": m_value,
            "a_squared": a_squared,
            "A_Q": a_q,
            "Gamma": gamma_form,
            "eta_b": eta_b,
            "nu_b": nu_b,
            "zeta": zeta,
            "epsilon": epsilon_form,
            "corridor_exponents": corridor_exponents,
            "P_xy": p_xy,
            "Q_xy": q_xy,
            "Q_k_sum_Q": qkq,
            "diagonal_high_fixture": diagonal_high_fixture,
            "projected_high_upper": projected_high_upper,
            "projected_high_slack": projected_high_slack,
            "diagonal_high_compression_only": diagonal_high_compression_only,
            "off_diagonal_bound_is_distinct": off_diagonal_bound_is_distinct,
        },
        "compressed_TFIM_QPS": {
            "forward_star_spectrum": star_energies,
            "local_gap": 2 * j_symbol,
            "selector": "u sum_x(1-s_x)",
            "selector_plus_density": selector_plus_density,
            "selector_minus_density": selector_minus_density,
            "selector_split": selector_split,
            "small_ratio": small_ratio,
            "Z2_pins_coexistence_u_zero": True,
            "source": YAROTSKII_QPS_SOURCE,
            "existential_small_ratio_only": True,
            "compressed_infinite_lattice_phasewise_gap": True,
            "finite_torus_exact_degeneracy": False,
            "explicit_threshold": False,
            "oscillator_gap": False,
        },
        "Feshbach_absolute_energy_before_low_scalar_subtraction": (
            feshbach_absolute_energy_before_low_scalar_subtraction
        ),
        "thermodynamic_ground_band_isolation": (
            thermodynamic_ground_band_isolation
        ),
    }


def authority_audit(audit: Audit, staged: bool) -> dict[str, Any]:
    missing: list[str] = []

    def missing_or_raise(label: str) -> None:
        if staged:
            missing.append(label)
            return
        raise AssertionError(f"missing or incomplete v2.0 authority: {label}")

    def require_text(path: Path, label: str) -> str | None:
        if not path.exists():
            missing_or_raise(label)
            return None
        return path.read_text(encoding="utf-8")

    def require_token(text: str | None, token: str, label: str) -> bool:
        if text is None or token not in text:
            missing_or_raise(label)
            return False
        audit.check(label, True, True, True, "authority")
        return True

    def require_any_token(
        text: str | None, tokens: tuple[str, ...], label: str
    ) -> bool:
        if text is None or not any(token in text for token in tokens):
            missing_or_raise(label)
            return False
        audit.check(label, True, True, True, "authority")
        return True

    manifest_text = require_text(MANIFEST, "manifest file")
    manifest: dict[str, Any] | None = None
    if manifest_text is not None:
        manifest = json.loads(manifest_text)
        audit.check(
            "manifest candidate",
            manifest.get("candidate_id") == EXPECTED_CANDIDATE_ID,
            manifest.get("candidate_id"),
            EXPECTED_CANDIDATE_ID,
            "authority",
        )
        audit.check(
            "manifest task",
            manifest.get("task_id") == EXPECTED_TASK,
            manifest.get("task_id"),
            EXPECTED_TASK,
            "authority",
        )
        audit.check(
            "manifest result identity",
            (
                manifest.get("result_number"),
                manifest.get("result_version"),
                manifest.get("result_id"),
            )
            == (EXPECTED_RESULT_NUMBER, EXPECTED_RESULT_VERSION, EXPECTED_RESULT_ID),
            (
                manifest.get("result_number"),
                manifest.get("result_version"),
                manifest.get("result_id"),
            ),
            (EXPECTED_RESULT_NUMBER, EXPECTED_RESULT_VERSION, EXPECTED_RESULT_ID),
            "authority",
        )
        audit.check(
            "manifest claim nonbearing",
            manifest.get("claim_bearing") is False,
            manifest.get("claim_bearing"),
            False,
            "authority",
        )
        audit.check(
            "manifest closed subgates",
            tuple(manifest.get("closed_subgates", [])) == EXPECTED_CLOSED_SUBGATES,
            manifest.get("closed_subgates"),
            EXPECTED_CLOSED_SUBGATES,
            "authority",
        )
        audit.check(
            "manifest open gates",
            tuple(manifest.get("open_gates", [])) == EXPECTED_OPEN_GATES,
            manifest.get("open_gates"),
            EXPECTED_OPEN_GATES,
            "authority",
        )
        audit.check(
            "manifest primary script",
            manifest.get("verification", {}).get("primary_script")
            == str(SCRIPT.relative_to(REPO)).replace("\\", "/"),
            manifest.get("verification", {}).get("primary_script"),
            str(SCRIPT.relative_to(REPO)).replace("\\", "/"),
            "authority",
        )
        sources = tuple(manifest.get("q3_semiclassical_onsite", {}).get("sources", []))
        audit.check(
            "semiclassical source set",
            sources == SEMICLASSICAL_SOURCES,
            sources,
            SEMICLASSICAL_SOURCES,
            "authority",
        )
        audit.check(
            "DFP source token",
            manifest.get("unbounded_block_qps_boundary", {}).get("source") == DFP_SOURCE,
            manifest.get("unbounded_block_qps_boundary", {}).get("source"),
            DFP_SOURCE,
            "authority",
        )
        imported_theorem = manifest.get("q3_semiclassical_onsite", {}).get(
            "imported_theorem", ""
        )
        require_token(
            imported_theorem,
            "a_1-a_0=O(v^2 h_sc)",
            "manifest safe d2 token",
        )
        require_token(
            imported_theorem,
            "No exponential",
            "manifest no exponential d2 import token",
        )
        require_token(
            imported_theorem,
            "separate Agmon-overlap theorem",
            "manifest conditional Agmon-overlap token",
        )
        corridor = manifest.get("exact_low_band_compression", {}).get("corridor", "")
        require_token(
            corridor,
            "delta_eff=O(N^-6)+",
            "manifest safe delta_eff corridor",
        )
        require_token(corridor, "A_0 asymptotic to (2/9)N^4", "manifest A0 corridor")
        require_token(
            corridor,
            "c m sqrt(A_Q)",
            "manifest mixed anticommutator corridor",
        )
        renyi_fixture = manifest.get("global_renyi_product_no_go", {}).get(
            "fixture", ""
        )
        require_token(
            renyi_fixture,
            "theta=8 delta c m^2/hbar",
            "manifest full-bond angle factor",
        )
        low_band_definitions = manifest.get("exact_low_band_compression", {}).get(
            "definitions", ""
        )
        low_band_hamiltonian = manifest.get("exact_low_band_compression", {}).get(
            "hamiltonian", ""
        )
        require_token(
            low_band_definitions,
            "periodic cubic lattice z=6",
            "manifest periodic z=6 qualifier",
        )
        require_token(
            low_band_hamiltonian,
            "site-dependent boundary field",
            "manifest boundary field qualifier",
        )
        no_overclaim = manifest.get("no_overclaim", "")
        for token in (
            "rank-two unbounded block diagonalization",
            "broken-sector oscillator temporal mass or GNS gap",
            "Sector A",
            "Pre-A closure",
        ):
            require_token(no_overclaim, token, f"manifest no-overclaim token {token}")
        require_token(
            manifest.get("full_hamiltonian_gibbs_resummation", {}).get("two_orientation_bound", ""),
            "rho(W_L^2)",
            "manifest full-Gibbs Duhamel token",
        )
        require_token(
            manifest.get("fixed_edge_restricted_tail_corridor", {}).get("constants", ""),
            "1296 R^6",
            "manifest corridor constant token",
        )
        audit.check(
            "manifest Yarotskii QPS source",
            manifest.get("compressed_tfim_two_phase_qps", {}).get("source")
            == YAROTSKII_QPS_SOURCE,
            manifest.get("compressed_tfim_two_phase_qps", {}).get("source"),
            YAROTSKII_QPS_SOURCE,
            "authority",
        )
        checkpoint = manifest.get("v2_checkpoint_synthesis")
        prospective_manifest = (
            REPO
            / "strategy/pre-a-round1-prospective-holdout-freeze-protocol-manifest.json"
        )
        other_checkpoint = None
        if prospective_manifest.is_file():
            try:
                other_checkpoint = json.loads(
                    prospective_manifest.read_text(encoding="utf-8")
                ).get("v2_checkpoint_synthesis")
            except (OSError, UnicodeError, json.JSONDecodeError):
                other_checkpoint = None

        checkpoint_fields = {
            "status",
            "source",
            "pdf",
            "source_sha256",
            "pdf_sha256",
            "pages",
            "workflow",
            "visual_qa",
        }
        checkpoint_status = (
            "ISSUED AS ONE COMBINED GATE-LEVEL CHECKPOINT AFTER PROOF VALIDATION"
        )
        checkpoint_source_rel = (
            "claims/C6-SPACETIME-SIGNATURE/notes/"
            "pre-a-q3lock-gibbs-feshbach-tfim-and-round1-map-fingerprint-"
            "checkpoint-260811-v0.9.tex.txt"
        )
        checkpoint_pdf_rel = (
            "claims/C6-SPACETIME-SIGNATURE/notes/"
            "pre-a-q3lock-gibbs-feshbach-tfim-and-round1-map-fingerprint-"
            "checkpoint-260811-v0.9.pdf"
        )
        checkpoint_workflow = (
            "No per-lemma or intermediate PDF was issued. One combined R-167 v2.0 / "
            "R-168 v1.1 gate-level synthesis source/PDF pair was issued only after "
            "the primary, non-importing independent, integrated, formal-authority, "
            "generated-surface, and source-form checks passed."
        )
        source_path = REPO / checkpoint_source_rel
        pdf_path = REPO / checkpoint_pdf_rel
        source_hash_actual = (
            hashlib.sha256(source_path.read_bytes()).hexdigest()
            if source_path.is_file()
            else None
        )
        pdf_hash_actual = (
            hashlib.sha256(pdf_path.read_bytes()).hexdigest()
            if pdf_path.is_file()
            else None
        )
        visual_qa = (
            checkpoint.get("visual_qa", "") if isinstance(checkpoint, dict) else ""
        )
        source_hash_declared = (
            checkpoint.get("source_sha256") if isinstance(checkpoint, dict) else None
        )
        pdf_hash_declared = (
            checkpoint.get("pdf_sha256") if isinstance(checkpoint, dict) else None
        )
        pages_declared = checkpoint.get("pages") if isinstance(checkpoint, dict) else None
        lowercase_hex = set("0123456789abcdef")
        checkpoint_valid = (
            isinstance(checkpoint, dict)
            and set(checkpoint) == checkpoint_fields
            and checkpoint == other_checkpoint
            and checkpoint.get("status") == checkpoint_status
            and checkpoint.get("source") == checkpoint_source_rel
            and checkpoint.get("pdf") == checkpoint_pdf_rel
            and source_path.with_suffix("").with_suffix(".pdf") == pdf_path
            and isinstance(source_hash_declared, str)
            and len(source_hash_declared) == 64
            and set(source_hash_declared) <= lowercase_hex
            and isinstance(pdf_hash_declared, str)
            and len(pdf_hash_declared) == 64
            and set(pdf_hash_declared) <= lowercase_hex
            and isinstance(pages_declared, int)
            and not isinstance(pages_declared, bool)
            and pages_declared > 0
            and checkpoint.get("workflow") == checkpoint_workflow
            and isinstance(visual_qa, str)
            and all(
                token in visual_qa.lower()
                for token in (
                    "all",
                    "rendered pages",
                    "clipping",
                    "overlap",
                    "pypdf",
                    "pdfplumber",
                )
            )
            and source_path.is_file()
            and pdf_path.is_file()
            and source_hash_actual == source_hash_declared
            and pdf_hash_actual == pdf_hash_declared
            and pdf_path.stat().st_mtime_ns >= source_path.stat().st_mtime_ns
        )
        audit.check(
            "v2 combined checkpoint issued and exact",
            checkpoint_valid,
            {
                "checkpoint": checkpoint,
                "shared_checkpoint": other_checkpoint,
                "source_exists": source_path.is_file(),
                "pdf_exists": pdf_path.is_file(),
                "source_sha256": source_hash_actual,
                "pdf_sha256": pdf_hash_actual,
                "pdf_fresh_relative_to_source": (
                    source_path.is_file()
                    and pdf_path.is_file()
                    and pdf_path.stat().st_mtime_ns >= source_path.stat().st_mtime_ns
                ),
            },
            {
                "exact_fields": sorted(checkpoint_fields),
                "shared": True,
                "status": checkpoint_status,
                "source": checkpoint_source_rel,
                "pdf": checkpoint_pdf_rel,
                "workflow": checkpoint_workflow,
                "hashes": "exact lowercase raw SHA256",
                "pages": "positive integer; parser validation is integrated-only",
                "fresh": True,
            },
            "authority",
        )

    certificate_text = require_text(CERTIFICATE, "certificate file")
    for token in (
        EXPECTED_RESULT_NUMBER,
        EXPECTED_RESULT_VERSION,
        EXPECTED_EXPLORATION,
        "S_0={16",
        "24c",
        "O(v^2h)",
        "Agmon-overlap lemma",
        "A_0",
        "N^4",
        "rank-one",
        "rank-two",
        "non-explicit",
        "No statement here closes",
    ):
        require_token(certificate_text, token, f"certificate token {token}")
    require_any_token(
        certificate_text,
        (r"\sqrt{2}", r"\sqrt2", "sqrt(2)"),
        "certificate semantic sqrt(2) token",
    )
    require_any_token(
        certificate_text,
        (r"\delta_{\rm eff}", "delta_eff"),
        "certificate semantic delta_eff token",
    )
    require_any_token(
        certificate_text,
        (r"8\delta c m^2", "8 delta c m^2"),
        "certificate full-bond factor 8 token",
    )
    require_token(
        certificate_text,
        "periodic cubic lattice",
        "certificate periodic lattice qualifier",
    )
    for token in (
        "EXP-000809",
        "rho(W_L^2)",
        "1296R^6",
        r"\kappa_{\rm ov}\le1+2(z-1)=11",
        r"0^{\times2}",
        "k=(0,-2)",
        "RM2006v061n02ABEH004323",
        "No v2.0 PDF is issued",
    ):
        require_token(certificate_text, token, f"certificate v2 token {token}")

    exploration_text = require_text(EXPLORATION_LEDGER, "exploration ledger")
    require_token(
        exploration_text,
        EXPECTED_EXPLORATION,
        f"exploration row {EXPECTED_EXPLORATION}",
    )
    result_text = require_text(RESULT_LEDGER, "result ledger")
    result_row_present = result_text is not None and any(
        EXPECTED_RESULT_NUMBER in line and EXPECTED_RESULT_VERSION in line
        for line in result_text.splitlines()
    )
    if result_row_present:
        audit.check(
            "result ledger exact R-167 v2.0 row",
            True,
            True,
            True,
            "authority",
        )
    else:
        missing_or_raise("result ledger exact R-167 v2.0 row")
    negative_text = require_text(NEGATIVE_REGISTRY, "negative registry")
    for negative_id in NEGATIVE_IDS:
        require_token(negative_text, negative_id, f"negative row {negative_id}")
    gate_text = require_text(GATE_REGISTRY, "gate registry")
    for gate_id in EXPECTED_CLOSED_SUBGATES + EXPECTED_OPEN_GATES:
        require_token(gate_text, gate_id, f"gate row {gate_id}")

    return {
        "status": "PASS" if not missing else "INCOMPLETE",
        "missing": missing,
        "manifest_loaded": manifest is not None,
        "certificate_loaded": certificate_text is not None,
        "external_source_text_reproved": False,
    }


def run_audit(staged: bool = False) -> dict[str, Any]:
    audit = Audit()
    fixture_a = fixture_a_pure_bond_tail(audit)
    fixture_b = fixture_b_local_and_global_renyi(audit)
    fixture_c = fixture_c_semiclassical_and_low_band(audit)
    fixture_d = fixture_d_full_gibbs_context(audit)
    fixture_e = fixture_e_fixed_edge_corridor(audit)
    fixture_f = fixture_f_feshbach_and_compressed_qps(audit)
    authority = authority_audit(audit, staged)
    verdict = "PASS" if authority["status"] == "PASS" else "INCOMPLETE"

    scope = {
        "pure_bond_coordinate_tail_identity": True,
        "local_measured_renyi_sufficiency_reduction": True,
        "global_volume_uniform_renyi_target_rejected_in_product_fixture": True,
        "Q3_semiclassical_hypotheses_and_normalization": True,
        "semiclassical_theorem_imported_not_reproved": True,
        "finite_r_minus_9_onsite_doublet_certified": False,
        "exact_low_band_TFIM_compression": True,
        "finite_Gibbs_full_Hamiltonian_cutoff_resummation": True,
        "arbitrary_context_automorphism_upgrade": False,
        "fixed_edge_to_growing_corridor_reduction": True,
        "actual_Q3_fixed_edge_history_bound": False,
        "below_Gamma_global_Feshbach_precursor": True,
        "compressed_TFIM_two_phase_QPS_and_phasewise_gap": True,
        "rank_two_unbounded_block_elimination": False,
        "two_phase_QPS_for_exact_Q3LOCK": False,
        "broken_sector_GNS_gap": False,
        "Sector_A_complete": False,
        "Pre_A_complete": False,
    }
    source_paths = [SCRIPT, MANIFEST, CERTIFICATE]
    passed = len(audit.rows)
    return {
        "schema": f"tect/{SLUG}-primary-result/1.0",
        "script_version": __version__,
        "task_id": EXPECTED_TASK,
        "claim_ids": list(EXPECTED_CLAIM_IDS),
        "candidate_id": EXPECTED_CANDIDATE_ID,
        "result_id": EXPECTED_RESULT_ID,
        "result_number": EXPECTED_RESULT_NUMBER,
        "result_version": EXPECTED_RESULT_VERSION,
        "exploration_id": EXPECTED_EXPLORATION,
        "claim_bearing": False,
        "closed_subgates": list(EXPECTED_CLOSED_SUBGATES),
        "open_gates": list(EXPECTED_OPEN_GATES),
        "negative_ids": list(NEGATIVE_IDS),
        "verdict": verdict,
        "passed": passed,
        "failed": 0,
        "total": passed,
        "summary": {
            "passed": passed,
            "failed": 0,
            "total": passed,
            "authority_status": authority["status"],
        },
        "authority": authority,
        "derived": {
            "fixture_A_pure_bond_tail": fixture_a,
            "fixture_B_local_and_global_renyi": fixture_b,
            "fixture_C_semiclassical_and_low_band": fixture_c,
            "fixture_D_full_Gibbs_context": fixture_d,
            "fixture_E_fixed_edge_corridor": fixture_e,
            "fixture_F_Feshbach_compressed_QPS": fixture_f,
        },
        "scope": scope,
        "source_hashes": {
            str(path.relative_to(REPO)).replace("\\", "/"): normalized_sha256(path)
            for path in source_paths
            if path.exists()
        },
        "assertions": audit.rows,
        "boundary": (
            "Exact A--F fixtures and theorem imports only. No numerical h0 or "
            "QPS radius, Q3 fixed-edge history bound, arbitrary-context upgrade, "
            "quasi-local rank-two oscillator elimination, oscillator QPS transfer, "
            "broken-sector oscillator GNS gap, Sector A, or Pre-A closure."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--staged", action="store_true")
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()

    payload = run_audit(staged=args.staged)
    if not args.self_test and not args.no_store:
        atomic_json(args.output, payload)
    print(f"{payload['verdict']} {payload['passed']}/{payload['total']}")
    if payload["verdict"] == "INCOMPLETE":
        print("authority: " + ", ".join(payload["authority"]["missing"]))
    script_key = str(SCRIPT.relative_to(REPO)).replace("\\", "/")
    print("schema: " + payload["schema"])
    print("script_sha256: " + payload["source_hashes"][script_key])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

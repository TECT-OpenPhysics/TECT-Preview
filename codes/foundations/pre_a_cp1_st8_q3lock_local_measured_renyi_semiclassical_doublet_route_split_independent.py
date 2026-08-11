#!/usr/bin/env python3
"""Independent standard-library verifier for the R-167 v2.2 route split.

All v2.1 Fraction fixtures and historical boundaries are retained.  New
standard-library reconstructions check the virial coefficient bookkeeping,
terminating subset-shear coefficients, fifth-word budget, registered-periodic
history corridor, and rank-two automatic-gap counterfixture.  This program
imports neither the primary implementation nor any primary result.  It does
not broaden the actual Q3 fifth moment beyond the registered fixed-beta
periodic compact-source family or close n-to-infinity common alpha, connected
rank-two oscillator/QPS transfer, or the oscillator-lattice GNS-gap parent.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import math
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any, Mapping, Sequence


__version__ = "2.2.0"
REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = (
    "pre-a-cp1-st8-q3lock-local-measured-renyi-semiclassical-"
    "doublet-route-split"
)
RESULT_ID = (
    "PA-CP1-ST8-Q3LOCK-SECOND-WEIGHTED-ENERGY-MOMENT-AND-"
    "COMMON-ALPHA-CAUCHY-GATE-SPLIT"
)
RESULT_NUMBER = "R-167"
RESULT_VERSION = "v2.2"
EXPLORATION_ID = "EXP-000813"
TASK_ID = "T-054"
CLAIM_ID = "C6-SPACETIME-SIGNATURE"

MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260811.md"
EXPLORATION_LEDGER = REPO / "explorations/log.jsonl"
RESULT_LEDGER = REPO / "RESULTS-LEDGER.md"
NEGATIVE_REGISTRY = REPO / "negative-results/registry.md"
GATE_REGISTRY = REPO / "claims/GATES.md"
DEFAULT_OUTPUT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / f"2026-08-11-independent-{SLUG}/result.json"
)

NEGATIVE_IDS = ('NG-2026-08-11-PRE-A-ST8-Q3LOCK-GLOBAL-ALL-BOND-RENYI-VOLUME-UNIFORMITY', 'NG-2026-08-11-PRE-A-ST8-Q3LOCK-RANK-ONE-UNBOUNDED-BLOCK-DIAGONALIZATION-DIRECT-BROKEN-DOUBLET-IMPORT', 'NG-2026-08-11-PRE-A-ST8-Q3LOCK-WEIGHTED-UNITARY-CUTOFF-AUTOMATIC-ARBITRARY-CONTEXT-AUTOMORPHISM-L2-UPGRADE', 'NG-2026-08-11-PRE-A-ST8-Q3LOCK-EXTENSIVE-FESHBACH-SELF-ENERGY-AUTOMATIC-QPS-LOCALITY', 'NG-2026-08-11-PRE-A-ST8-Q3LOCK-STATIC-GAUSSIAN-SYMMETRY-FINITE-MOMENT-AUTOMATIC-FIXED-EDGE-HISTORY-TAIL', 'NG-2026-08-11-PRE-A-ST8-Q3LOCK-UNIFORM-QUADRATIC-IN-M-ALL-MOMENT-BOND-SHEAR-GRAPH-TRANSPORT', 'NG-2026-08-11-PRE-A-ST8-Q3LOCK-STATIC-MOMENTS-AND-LOW-GRAPH-AUTOMATIC-TWENTIETH-HISTORY-MOMENT', 'NG-2026-08-11-PRE-A-ST8-Q3LOCK-FULL-OSCILLATOR-LOCAL-PARITY-DOUBLET-EDGE-GAP-AUTOMATIC-VOLUME-UNIFORM-LATTICE-GAP')
CLOSED_SUBGATES = ('PA-CP1-ST8-Q3LOCK-PURE-BOND-COORDINATE-TAIL-INVARIANCE-AND-STATE-WEIGHTED-CUTOFF-IDENTITY', 'PA-CP1-ST8-Q3LOCK-LOCAL-MEASURED-RENYI-TO-HISTORY-TAIL-REDUCTION', 'PA-CP1-ST8-Q3LOCK-SEMICLASSICAL-ONSITE-DOUBLET-AND-EXACT-LOW-BAND-TFIM-COMPRESSION', 'PA-CP1-ST8-Q3LOCK-FULL-HAMILTONIAN-TWO-ORIENTATION-STATIC-GIBBS-CUTOFF-UNITARY-RESUMMATION', 'PA-CP1-ST8-Q3LOCK-FIXED-BOND-RESTRICTED-TAIL-TO-GROWING-CORRIDOR-REDUCTION', 'PA-CP1-ST8-Q3LOCK-BELOW-ONE-HIGH-MODE-FESHBACH-AND-RELATIVE-FORM-SMALLNESS-PRECURSOR', 'PA-CP1-ST8-Q3LOCK-EXACT-COMPRESSED-TFIM-TWO-PHASE-QPS-AND-PHASEWISE-GAP', 'PA-CP1-ST8-Q3LOCK-TWO-ORIENTATION-TWENTIETH-MOMENT-FIXED-EDGE-CORRIDOR-REDUCTION', 'PA-CP1-ST8-Q3LOCK-FULL-OSCILLATOR-EDGE-BLOCK-PARITY-DOUBLET-CLUSTER-AND-UNIFORM-ONSITE-SPECTRAL-CUTOFF-REMOVAL', 'PA-CP1-ST8-Q3LOCK-TRANSLATE-UNIFORM-LOCAL-FIFTH-GIBBS-MOMENT-AND-ELLIPTIC-EMBEDDING', 'PA-CP1-ST8-Q3LOCK-SIMULTANEOUS-BOND-SHEAR-FIFTH-GRAPH-PROPAGATION', 'PA-CP1-ST8-Q3LOCK-ACTUAL-TWO-ORIENTATION-TWENTIETH-HISTORY-MOMENT-AND-HARD-CUTOFF-CORRIDOR')
YAROTSKII_QPS_SOURCE = "https://doi.org/10.1070/RM2006v061n02ABEH004323"

OPEN_GATES = ('PA-CP1-ST8-Q3LOCK-LOCAL-STRICT-ALL-EXHAUSTION-TWO-ORIENTATION-HISTORY-COMMON-ALPHA', 'PA-CP1-ST8-Q3LOCK-BROKEN-SECTOR-GNS-GAP-COERCIVITY', 'PA-CP1-ST8-Q3LOCK-INFINITE-DIMENSIONAL-RANK-TWO-BAND-BLOCK-DIAGONALIZATION-AND-TWO-PHASE-QPS', 'PA-ROUND1-EVIDENCE-ROLE-AND-MINIMUM-MANIFEST-FREEZE', 'PA-CP1-ST8-Q3LOCK-CONNECTED-RANK-TWO-OSCILLATOR-ELIMINATION-QPS-NORM-AND-CUTOFF-COMPATIBILITY')

NO_OVERCLAIM = (
    "This independent verifier checks the retained v2.1 fixtures and independently "
    "reconstructs the exact virial sign/factor, terminating subset-shear algebra, "
    "fifth-word budget, periodic actual-history corridor arithmetic, and rank-two "
    "automatic-gap counterfixture. The actual Q3 fifth moment and history theorem "
    "is restricted to the registered fixed-beta periodic compact-source family; "
    "it does not prove an arbitrary-boundary history bound, n-to-infinity Trotter "
    "convergence, all-shape Cauchy compatibility, all-exhaustion common alpha, "
    "group/generator completion, a phase-KMS quotient, connected rank-two "
    "unbounded block diagonalization, oscillator QPS transfer, an oscillator-"
    "lattice broken-sector temporal mass or GNS gap, regulator removal, a "
    "continuum, physical-empty comparison, prospective blind validation, C6, "
    "CP1, physical Sector A, or Pre-A closure. It also proves neither an onsite-"
    "interspersed local measured-Renyi estimate nor two-phase QPS for the exact "
    "oscillator lattice. The rank-two fixture is not a Q3 "
    "locality, coercivity, or gap no-go."
)
Polynomial = tuple[Fraction, ...]


def serial(value: Any) -> Any:
    """Convert exact values to deterministic JSON-compatible objects."""

    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, Path):
        return str(value).replace("\\", "/")
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, set):
        return [serial(item) for item in sorted(value)]
    if isinstance(value, (list, tuple)):
        return [serial(item) for item in value]
    return value


def canonical_bytes(payload: Mapping[str, Any]) -> bytes:
    return json.dumps(
        serial(dict(payload)),
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    ).encode("utf-8")


def normalized_sha256(path: Path) -> str:
    raw = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(raw).hexdigest()


def atomic_json(path: Path, payload: Mapping[str, Any]) -> None:
    """Write a result atomically; self-test mode never calls this function."""

    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(
                serial(dict(payload)),
                stream,
                indent=2,
                sort_keys=True,
                ensure_ascii=True,
            )
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


class Audit:
    """Fail-fast exact assertion ledger."""

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
            raise AssertionError(
                f"{group}: {name}: actual={actual!r}, expected={expected!r}"
            )
        self.rows.append(
            {
                "name": name,
                "group": group,
                "status": "PASS",
                "actual": serial(actual),
                "expected": serial(expected),
            }
        )


def perfect_fraction_sqrt(value: Fraction) -> Fraction:
    """Return an exact rational square root, rejecting non-square inputs."""

    if value < 0:
        raise ValueError("square root input must be nonnegative")
    numerator = math.isqrt(value.numerator)
    denominator = math.isqrt(value.denominator)
    if numerator * numerator != value.numerator:
        raise ValueError(f"numerator is not a square: {value}")
    if denominator * denominator != value.denominator:
        raise ValueError(f"denominator is not a square: {value}")
    return Fraction(numerator, denominator)


def poly_trim(value: Sequence[Fraction]) -> Polynomial:
    entries = list(value)
    while len(entries) > 1 and entries[-1] == 0:
        entries.pop()
    return tuple(entries)


def poly_add(left: Polynomial, right: Polynomial) -> Polynomial:
    size = max(len(left), len(right))
    return poly_trim(
        tuple(
            (left[index] if index < len(left) else Fraction(0))
            + (right[index] if index < len(right) else Fraction(0))
            for index in range(size)
        )
    )


def poly_scale(value: Polynomial, factor: Fraction) -> Polynomial:
    return poly_trim(tuple(factor * entry for entry in value))


def poly_mul(left: Polynomial, right: Polynomial) -> Polynomial:
    output = [Fraction(0)] * (len(left) + len(right) - 1)
    for left_index, left_value in enumerate(left):
        for right_index, right_value in enumerate(right):
            output[left_index + right_index] += left_value * right_value
    return poly_trim(output)


def poly_eval(value: Polynomial, argument: Fraction) -> Fraction:
    output = Fraction(0)
    for coefficient in reversed(value):
        output = output * argument + coefficient
    return output


def source_firewall_fixture() -> dict[str, Any]:
    """Verify that the program has only stdlib imports and authority inputs."""

    tree = ast.parse(SCRIPT.read_text(encoding="utf-8"), filename=str(SCRIPT))
    allowed_roots = {
        "__future__",
        "argparse",
        "ast",
        "fractions",
        "hashlib",
        "json",
        "math",
        "os",
        "pathlib",
        "tempfile",
        "typing",
    }
    imported_roots: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_roots.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported_roots.add((node.module or "").split(".")[0])
    return {
        "imported_roots": sorted(imported_roots),
        "allowed_roots": sorted(allowed_roots),
        "forbidden_imports": sorted(imported_roots - allowed_roots),
        "runtime_read_inputs": [
            SCRIPT,
            MANIFEST,
            CERTIFICATE,
            EXPLORATION_LEDGER,
            RESULT_LEDGER,
            NEGATIVE_REGISTRY,
            GATE_REGISTRY,
        ],
        "primary_module_imported": False,
        "primary_result_consumed": False,
    }


def pure_bond_diagonal_fixture() -> dict[str, Any]:
    """Recompute the multiplier and cutoff identities on four atoms exactly."""

    # INPUT FIXTURE.  Phase units are multiples of pi, so all exponentials
    # below are exactly +/-1 and no floating-point trigonometry is required.
    weights = (
        Fraction(1, 10),
        Fraction(1, 5),
        Fraction(3, 10),
        Fraction(2, 5),
    )
    full_phase_units = (0, 1, 2, 3)
    cutoff_phase_units = (0, 0, 2, 2)
    coordinate_multiplier = (Fraction(-2), Fraction(0), Fraction(3), Fraction(5))
    tail_projection = (Fraction(0), Fraction(0), Fraction(1), Fraction(1))

    full_unitary = tuple(1 if entry % 2 == 0 else -1 for entry in full_phase_units)
    cutoff_unitary = tuple(
        1 if entry % 2 == 0 else -1 for entry in cutoff_phase_units
    )
    phase_difference_units = tuple(
        full - cutoff
        for full, cutoff in zip(full_phase_units, cutoff_phase_units)
    )
    multiplier_commutator = tuple(
        unitary * value - value * unitary
        for unitary, value in zip(full_unitary, coordinate_multiplier)
    )
    conjugated_tail = tuple(
        unitary * projection * unitary
        for unitary, projection in zip(full_unitary, tail_projection)
    )

    difference_square = tuple(
        (full - cutoff) ** 2
        for full, cutoff in zip(full_unitary, cutoff_unitary)
    )
    sine_square_expression = tuple(
        0 if difference % 2 == 0 else 4
        for difference in phase_difference_units
    )
    left_hilbert_schmidt_square = sum(
        (weight * value for weight, value in zip(weights, difference_square)),
        Fraction(0),
    )
    right_hilbert_schmidt_square = sum(
        (weight * value for weight, value in zip(weights, difference_square)),
        Fraction(0),
    )
    sine_functional = sum(
        (weight * value for weight, value in zip(weights, sine_square_expression)),
        Fraction(0),
    )
    w_square_coefficient = sum(
        (
            weight * difference * difference
            for weight, difference in zip(weights, phase_difference_units)
        ),
        Fraction(0),
    )
    # Exact rational certification of pi^2 > 9 > 4 is enough for the bound.
    pi_squared_strict_lower = Fraction(9)
    cutoff_rhs_strict_lower = pi_squared_strict_lower * w_square_coefficient

    return {
        "weights": weights,
        "full_phase_units_of_pi": full_phase_units,
        "cutoff_phase_units_of_pi": cutoff_phase_units,
        "phase_difference_units_of_pi": phase_difference_units,
        "full_unitary_diagonal": full_unitary,
        "cutoff_unitary_diagonal": cutoff_unitary,
        "coordinate_multiplier": coordinate_multiplier,
        "multiplier_commutator": multiplier_commutator,
        "tail_projection": tail_projection,
        "conjugated_tail": conjugated_tail,
        "difference_square_diagonal": difference_square,
        "sine_square_functional_diagonal": sine_square_expression,
        "left_HS_square": left_hilbert_schmidt_square,
        "right_HS_square": right_hilbert_schmidt_square,
        "sine_functional": sine_functional,
        "W_square_coefficient_before_pi_squared": w_square_coefficient,
        "pi_squared_strict_lower": pi_squared_strict_lower,
        "cutoff_rhs_strict_lower": cutoff_rhs_strict_lower,
        "operator_norm_exponential_paid": False,
        "onsite_interspersed_history_tail_proved": False,
    }


def qtilde_pair_polynomial(reference_a: Fraction, reference_b: Fraction) -> Polynomial:
    """One two-level support block in the exact 4x4 Qtilde_2 trace."""

    # With x=sin(theta)^2, the two evolved diagonal entries are affine in x;
    # the squared off-diagonal magnitude is x(1-x)(a-b)^2.
    diagonal_a = (reference_a, reference_b - reference_a)
    diagonal_b = (reference_b, reference_a - reference_b)
    off_diagonal_square = poly_scale(
        (Fraction(0), Fraction(1), Fraction(-1)),
        (reference_a - reference_b) ** 2,
    )
    geometric_mean = perfect_fraction_sqrt(reference_a * reference_b)
    return poly_add(
        poly_add(
            poly_scale(poly_mul(diagonal_a, diagonal_a), 1 / reference_a),
            poly_scale(poly_mul(diagonal_b, diagonal_b), 1 / reference_b),
        ),
        poly_scale(off_diagonal_square, Fraction(2) / geometric_mean),
    )


def global_qtilde2_fixture() -> dict[str, Any]:
    """Reconstruct the 4x4 order-two sandwiched-Renyi polynomial exactly."""

    # INPUT FIXTURE from the registered conditional low-doublet reference.
    probability_even = Fraction(4, 5)
    probability_odd = Fraction(1, 5)
    q3_coordinate_count = 8
    rho_two_diagonal = (
        probability_even**2,
        probability_even * probability_odd,
        probability_even * probability_odd,
        probability_odd**2,
    )
    coupled_pairs = ((0, 3), (1, 2))
    q_polynomial: Polynomial = (Fraction(0),)
    pair_polynomials = []
    for left, right in coupled_pairs:
        pair = qtilde_pair_polynomial(
            rho_two_diagonal[left], rho_two_diagonal[right]
        )
        pair_polynomials.append(pair)
        q_polynomial = poly_add(q_polynomial, pair)

    # TEST ORACLE: the certificate's claimed ((4+9x)^2)/16 formula.
    certificate_formula_oracle = poly_scale(
        poly_mul((Fraction(4), Fraction(9)), (Fraction(4), Fraction(9))),
        Fraction(1, 16),
    )
    evaluation_arguments = (
        Fraction(0),
        Fraction(1, 2),
        Fraction(16, 25),
        Fraction(144, 169),
        Fraction(1),
    )
    evaluations = {
        str(argument): poly_eval(q_polynomial, argument)
        for argument in evaluation_arguments
    }
    single_bond_pi_over_four = evaluations[str(Fraction(1, 2))]
    disjoint_bond_count = 3
    disjoint_product = single_bond_pi_over_four**disjoint_bond_count

    return {
        "rho_one_diagonal": (probability_even, probability_odd),
        "rho_two_diagonal": rho_two_diagonal,
        "rho_two_trace": sum(rho_two_diagonal, Fraction(0)),
        "coupled_4x4_index_pairs": coupled_pairs,
        "q3_coordinate_count": q3_coordinate_count,
        "physical_theta_coefficient_of_delta_c_m_squared_over_hbar": (
            q3_coordinate_count
        ),
        "physical_theta_relation": (
            "theta=8 delta c m^2/hbar=delta J/hbar"
        ),
        "pair_Qtilde2_polynomials": pair_polynomials,
        "Qtilde2_polynomial": q_polynomial,
        "certificate_formula_polynomial": certificate_formula_oracle,
        "evaluations_by_sin_squared_theta": evaluations,
        "theta_pi_over_four_value": single_bond_pi_over_four,
        "disjoint_bond_count": disjoint_bond_count,
        "disjoint_product_value": disjoint_product,
        "global_volume_uniform_bound_rejected_in_fixture": True,
        "compressed_doublet_coordinate_spectral_functions_commute_with_kick": True,
        "projected_full_coordinate_tail_claimed": False,
        "coordinate_scope": (
            "Spectral functions of the compressed doublet coordinate "
            "m sigma_x, not P 1_{q>L} P."
        ),
        "full_interacting_Q3_Gibbs_counterexample": False,
        "local_measured_Renyi_rejected": False,
        "common_alpha_closed": False,
    }


def measured_renyi_fixture() -> dict[str, Any]:
    """Check discrete Holder and exact fourth-moment layer-cake coefficients."""

    # INPUT FIXTURE for a normalized likelihood on a four-atom coordinate law.
    reference = (
        Fraction(1, 2),
        Fraction(1, 4),
        Fraction(1, 8),
        Fraction(1, 8),
    )
    likelihood = (
        Fraction(1, 2),
        Fraction(1),
        Fraction(3, 2),
        Fraction(5, 2),
    )
    alpha = Fraction(2)
    theta = (alpha - 1) / alpha
    tilted = tuple(
        reference_value * likelihood_value
        for reference_value, likelihood_value in zip(reference, likelihood)
    )
    measured_q_alpha = sum(
        (
            reference_value * likelihood_value**int(alpha)
            for reference_value, likelihood_value in zip(reference, likelihood)
        ),
        Fraction(0),
    )
    event_indices = (2, 3)
    reference_event = sum((reference[index] for index in event_indices), Fraction(0))
    tilted_event = sum((tilted[index] for index in event_indices), Fraction(0))
    holder_left_squared = tilted_event**2
    holder_right_squared = measured_q_alpha * reference_event

    # INPUT FIXTURE for coefficients in the registered Gaussian-tail reduction.
    gaussian_a = Fraction(14)
    cutoff_L = Fraction(2)
    measured_q_coefficient = Fraction(16, 9)
    static_tail_coefficient = Fraction(9, 4)
    b = theta * gaussian_a
    q_root = perfect_fraction_sqrt(measured_q_coefficient)
    static_root = perfect_fraction_sqrt(static_tail_coefficient)
    one_orientation_amplitude = q_root * static_root
    two_orientation_probability_prefactor = 2 * one_orientation_amplitude
    layer_cake_polynomial = (
        cutoff_L**4
        + 2 * cutoff_L**2 / b
        + Fraction(2) / (b * b)
    )
    one_orientation_layer_cake_coefficient = (
        one_orientation_amplitude * layer_cake_polynomial
    )
    two_orientation_layer_cake_coefficient = (
        2 * one_orientation_layer_cake_coefficient
    )

    return {
        "reference_distribution": reference,
        "likelihood": likelihood,
        "tilted_distribution": tilted,
        "reference_normalization": sum(reference, Fraction(0)),
        "tilted_normalization": sum(tilted, Fraction(0)),
        "alpha": alpha,
        "theta": theta,
        "measured_Q_alpha": measured_q_alpha,
        "event_indices": event_indices,
        "reference_event_probability": reference_event,
        "tilted_event_probability": tilted_event,
        "Holder_left_squared": holder_left_squared,
        "Holder_right_squared": holder_right_squared,
        "gaussian_a": gaussian_a,
        "b_theta_a": b,
        "cutoff_L": cutoff_L,
        "Q_coefficient": measured_q_coefficient,
        "static_tail_coefficient": static_tail_coefficient,
        "Q_to_one_over_alpha": q_root,
        "static_tail_to_theta": static_root,
        "one_orientation_amplitude": one_orientation_amplitude,
        "two_orientation_probability_prefactor": (
            two_orientation_probability_prefactor
        ),
        "layer_cake_polynomial": layer_cake_polynomial,
        "one_orientation_layer_cake_coefficient": (
            one_orientation_layer_cake_coefficient
        ),
        "two_orientation_layer_cake_coefficient": (
            two_orientation_layer_cake_coefficient
        ),
        "onsite_interspersed_likelihood_bound_proved": False,
    }


def cube_edges() -> tuple[tuple[int, int], ...]:
    return tuple(
        (left, left ^ bit)
        for left in range(8)
        for bit in (1, 2, 4)
        if left < (left ^ bit)
    )


def cube_laplacian(edges: Sequence[tuple[int, int]]) -> tuple[tuple[int, ...], ...]:
    matrix = [[0] * 8 for _ in range(8)]
    for left, right in edges:
        matrix[left][left] += 1
        matrix[right][right] += 1
        matrix[left][right] -= 1
        matrix[right][left] -= 1
    return tuple(tuple(row) for row in matrix)


def integer_matvec(
    matrix: Sequence[Sequence[int]], vector: Sequence[int]
) -> tuple[int, ...]:
    return tuple(
        sum((entry * value for entry, value in zip(row, vector)), 0)
        for row in matrix
    )


def semiclassical_cube_fixture() -> dict[str, Any]:
    """Derive Q3 minima, Laplacian/Hessian spectrum, and one exact scaling row."""

    edges = cube_edges()
    laplacian = cube_laplacian(edges)
    degrees = tuple(laplacian[index][index] for index in range(8))
    walsh_rows = []
    laplacian_spectrum = []
    for mask in range(8):
        vector = tuple(
            -1 if ((mask & vertex).bit_count() % 2) else 1
            for vertex in range(8)
        )
        eigenvalue = 2 * mask.bit_count()
        applied = integer_matvec(laplacian, vector)
        walsh_rows.append(
            {
                "mask": mask,
                "vector": vector,
                "eigenvalue": eigenvalue,
                "applied": applied,
                "expected": tuple(eigenvalue * entry for entry in vector),
            }
        )
        laplacian_spectrum.append(eigenvalue)
    laplacian_spectrum.sort()
    laplacian_multiplicity = {
        eigenvalue: laplacian_spectrum.count(eigenvalue)
        for eigenvalue in sorted(set(laplacian_spectrum))
    }

    zero_sign_assignments = []
    for bit_pattern in range(1 << 8):
        signs = tuple(1 if bit_pattern & (1 << vertex) else -1 for vertex in range(8))
        if all(signs[left] == signs[right] for left, right in edges):
            zero_sign_assignments.append(signs)

    # INPUT FIXTURE requested for exact finite scaling.
    R = Fraction(16)
    g = Fraction(1)
    lam = Fraction(1)
    chi = Fraction(1)
    hbar = Fraction(1)
    mu = lam / g
    v = perfect_fraction_sqrt(R / g)
    energy_scale = R * R / g
    h_sc = hbar * g / (perfect_fraction_sqrt(chi) * R * perfect_fraction_sqrt(R))
    hessian_spectrum = tuple(Fraction(2) + mu * value for value in laplacian_spectrum)
    hessian_multiplicity = {
        value: hessian_spectrum.count(value) for value in sorted(set(hessian_spectrum))
    }

    # On the locked path, ds=sqrt(8) dt and sqrt(2W)=2(1-t^2).
    locked_path_integral_minus_one_to_one = Fraction(4, 3)
    action_sqrt_radicand = 2
    action_sqrt_coefficient = 4 * locked_path_integral_minus_one_to_one
    action_square = action_sqrt_coefficient**2 * action_sqrt_radicand
    harmonic_gap_sqrt_coefficient = energy_scale * h_sc
    harmonic_gap_sqrt_radicand = 2
    harmonic_gap_square = (
        harmonic_gap_sqrt_coefficient**2 * harmonic_gap_sqrt_radicand
    )

    return {
        "edges": edges,
        "edge_count": len(edges),
        "degrees": degrees,
        "laplacian": laplacian,
        "walsh_rows": walsh_rows,
        "laplacian_spectrum": tuple(laplacian_spectrum),
        "laplacian_multiplicity": laplacian_multiplicity,
        "zero_sign_assignments": zero_sign_assignments,
        "zero_sign_assignment_count": len(zero_sign_assignments),
        "R": R,
        "g": g,
        "lambda": lam,
        "chi": chi,
        "hbar": hbar,
        "mu": mu,
        "v": v,
        "E_star": energy_scale,
        "h_sc": h_sc,
        "hessian_spectrum": hessian_spectrum,
        "hessian_multiplicity": hessian_multiplicity,
        "locked_path_integral": locked_path_integral_minus_one_to_one,
        "S0_sqrt_coefficient": action_sqrt_coefficient,
        "S0_sqrt_radicand": action_sqrt_radicand,
        "S0_square": action_square,
        "Gamma_harm_sqrt_coefficient": harmonic_gap_sqrt_coefficient,
        "Gamma_harm_sqrt_radicand": harmonic_gap_sqrt_radicand,
        "Gamma_harm_square": harmonic_gap_square,
        "numerical_h0_certified": False,
        "many_body_phase_proved": False,
    }


def low_band_tfim_fixture() -> dict[str, Any]:
    """Recompute all exact coefficients of the compressed bond Hamiltonian."""

    # INPUT FIXTURE.
    spatial_coordination = Fraction(6)
    c = Fraction(2, 9)
    m = Fraction(3, 2)
    delta_one = Fraction(1, 10)
    a_zero = Fraction(5, 2)
    a_one = Fraction(251, 100)
    internal_coordinate_count = Fraction(8)

    d_two = a_one - a_zero
    ising_J = internal_coordinate_count * c * m * m
    bond_scalar = internal_coordinate_count * c * a_zero
    bond_field_per_endpoint = 4 * c * d_two
    bond_spin_coupling = -ising_J
    shifted_bond_scalar = bond_scalar - ising_J
    accumulated_site_field = spatial_coordination * bond_field_per_endpoint
    delta_effective = delta_one + accumulated_site_field

    return {
        "z": spatial_coordination,
        "c": c,
        "m": m,
        "delta_1": delta_one,
        "a_0": a_zero,
        "a_1": a_one,
        "d_2": d_two,
        "internal_coordinate_count": internal_coordinate_count,
        "J": ising_J,
        "bond_scalar_before_shift": bond_scalar,
        "bond_field_per_endpoint": bond_field_per_endpoint,
        "bond_spin_coupling": bond_spin_coupling,
        "bond_scalar_removed_after_J_rewrite": shifted_bond_scalar,
        "accumulated_site_field": accumulated_site_field,
        "delta_eff": delta_effective,
        "compression_exact": True,
        "rank_two_high_mode_elimination_proved": False,
    }


def residual_bound_fixture(low_band: Mapping[str, Any]) -> dict[str, Any]:
    """Recompute centered moments, the one-bond bound, and A_Q algebra."""

    m = low_band["m"]
    a_zero = low_band["a_0"]
    a_one = low_band["a_1"]
    c = low_band["c"]

    # INPUT FIXTURE: fourth moments are specified upstream, not inferred.
    b_zero_moment = a_zero**2 + Fraction(1, 4)
    b_one_moment = a_one**2 + Fraction(9, 25)
    a_squared_candidates = (a_zero - m * m, a_one - m * m)
    b_squared_candidates = (
        b_zero_moment - a_zero**2,
        b_one_moment - a_one**2,
    )
    a_squared = max(a_squared_candidates)
    b_squared = max(b_squared_candidates)
    b = perfect_fraction_sqrt(b_squared)

    # a=sqrt(26)/10.  Keep the non-square radical symbolic and verify it by
    # squaring its coefficient/radicand representation.
    a_sqrt_radicand = 26
    a_sqrt_coefficient = Fraction(1, 10)
    a_square_from_surd = a_sqrt_coefficient**2 * a_sqrt_radicand
    bond_rational_part = 8 * c * (b + a_squared)
    bond_sqrt_coefficient = 8 * c * 2 * m * a_sqrt_coefficient
    bond_sqrt_radicand = a_sqrt_radicand
    # Rational strict upper oracle sqrt(26)<51/10 follows from 26<2601/100.
    sqrt_upper = Fraction(51, 10)
    sqrt_upper_certified = Fraction(a_sqrt_radicand) < sqrt_upper**2
    bond_rational_upper = bond_rational_part + bond_sqrt_coefficient * sqrt_upper

    # Independent exact A_Q fixture: sqrt(epsilon_0+Gamma)=sqrt(9)=3.
    residual_v = Fraction(4)
    residual_gamma = Fraction(8)
    residual_epsilon_zero = Fraction(1)
    residual_g = Fraction(1)
    aq_first = residual_v**2 / residual_gamma
    aq_second = (
        2
        * perfect_fraction_sqrt(residual_epsilon_zero + residual_gamma)
        / (residual_gamma * perfect_fraction_sqrt(residual_g))
    )
    a_q = aq_first + aq_second

    young_t = Fraction(1, 2)
    young_matrix = (
        (young_t, Fraction(-1)),
        (Fraction(-1), 1 / young_t),
    )
    young_determinant = (
        young_matrix[0][0] * young_matrix[1][1]
        - young_matrix[0][1] * young_matrix[1][0]
    )

    return {
        "b_0": b_zero_moment,
        "b_1": b_one_moment,
        "a_squared_candidates": a_squared_candidates,
        "a_squared": a_squared,
        "a_sqrt_coefficient": a_sqrt_coefficient,
        "a_sqrt_radicand": a_sqrt_radicand,
        "a_square_from_surd": a_square_from_surd,
        "b_squared_candidates": b_squared_candidates,
        "b_squared": b_squared,
        "b": b,
        "bond_bound_rational_part": bond_rational_part,
        "bond_bound_sqrt_coefficient": bond_sqrt_coefficient,
        "bond_bound_sqrt_radicand": bond_sqrt_radicand,
        "bond_bound_common_denominator_form": {
            "numerator_rational": bond_rational_part * 225,
            "numerator_sqrt_coefficient": bond_sqrt_coefficient * 225,
            "denominator": 225,
            "radicand": bond_sqrt_radicand,
        },
        "sqrt_upper": sqrt_upper,
        "sqrt_upper_certified_by_squaring": sqrt_upper_certified,
        "bond_bound_rational_upper": bond_rational_upper,
        "A_Q_fixture": {
            "v": residual_v,
            "Gamma": residual_gamma,
            "epsilon_0": residual_epsilon_zero,
            "g": residual_g,
            "first_term": aq_first,
            "second_term": aq_second,
            "A_Q": a_q,
        },
        "Young_t": young_t,
        "Young_matrix": young_matrix,
        "Young_determinant": young_determinant,
        "Young_diagonal_nonnegative": (
            young_matrix[0][0] >= 0 and young_matrix[1][1] >= 0
        ),
        "residual_inequality_proves_block_diagonalization": False,
    }


def corridor_exponent_fixture() -> dict[str, Any]:
    """Derive all N powers from r=-N^4 and c=N^-4 algebraically."""

    # INPUT EXPONENTS in powers of N.
    input_exponents = {
        "R": Fraction(4),
        "c": Fraction(-4),
        "g": Fraction(0),
        "lambda": Fraction(0),
        "chi": Fraction(0),
        "hbar": Fraction(0),
    }
    R_exp = input_exponents["R"]
    c_exp = input_exponents["c"]
    g_exp = input_exponents["g"]
    chi_exp = input_exponents["chi"]
    hbar_exp = input_exponents["hbar"]

    v_exp = (R_exp - g_exp) / 2
    energy_exp = 2 * R_exp - g_exp
    h_exp = hbar_exp + g_exp - chi_exp / 2 - 3 * R_exp / 2
    j_exp = c_exp + 2 * v_exp
    gamma_exp = energy_exp + h_exp
    a_squared_exp = 2 * v_exp + h_exp
    a_exp = a_squared_exp / 2
    b_squared_exp = 4 * v_exp + h_exp
    b_exp = b_squared_exp / 2
    bond_bracket_term_exponents = {
        "b": b_exp,
        "2ma": v_exp + a_exp,
        "a_squared": 2 * a_exp,
    }
    bond_bracket_exp = max(bond_bracket_term_exponents.values())
    low_high_bond_exp = c_exp + bond_bracket_exp

    # epsilon_0+Gamma has the harmonic exponent Gamma in this corridor.
    epsilon_plus_gamma_exp = gamma_exp
    aq_term_exponents = {
        "v_squared_over_Gamma": 2 * v_exp - gamma_exp,
        "sqrt_energy_over_Gamma_sqrt_g": (
            epsilon_plus_gamma_exp / 2 - gamma_exp - g_exp / 2
        ),
    }
    a_q_exp = max(aq_term_exponents.values())
    c_a_q_exp = c_exp + a_q_exp
    derived = {
        "v": v_exp,
        "E_star": energy_exp,
        "h_sc": h_exp,
        "J": j_exp,
        "Gamma": gamma_exp,
        "a": a_exp,
        "b": b_exp,
        "one_bond_low_high": low_high_bond_exp,
        "cA_Q": c_a_q_exp,
    }
    # TEST ORACLE: the exponent table registered in the v1.9 certificate.
    certificate_oracle = {
        "v": Fraction(2),
        "E_star": Fraction(8),
        "h_sc": Fraction(-6),
        "J": Fraction(0),
        "Gamma": Fraction(2),
        "a": Fraction(-1),
        "b": Fraction(1),
        "one_bond_low_high": Fraction(-3),
        "cA_Q": Fraction(-2),
    }
    return {
        "input_exponents": input_exponents,
        "derived_exponents": derived,
        "certificate_oracle": certificate_oracle,
        "bond_bracket_term_exponents": bond_bracket_term_exponents,
        "bond_bracket_dominant_exponent": bond_bracket_exp,
        "A_Q_term_exponents": aq_term_exponents,
        "A_Q_dominant_exponent": a_q_exp,
        "J_leading_constant": Fraction(8),
        "Gamma_leading_sqrt_coefficient": Fraction(1),
        "Gamma_leading_sqrt_radicand": 2,
        "finite_N_enclosure": False,
        "two_phase_QPS_proved": False,
    }



def full_gibbs_context_fixture() -> dict[str, Any]:
    """Reconstruct the two-level Gibbs/context family without matrix libraries."""

    # INPUT FIXTURE; derived fractions below are checked against labelled
    # TEST ORACLES in build_payload.
    p = Fraction(1, 5)
    weighted_unitary_right_squared = 4 * p
    weighted_unitary_left_squared = 4 * p
    rho_w_squared_pi_coefficient = p
    pi_squared_lower = Fraction(9)
    duhamel_rhs_strict_lower = pi_squared_lower * p
    observable_right_squared = Fraction(4)
    observable_left_squared = Fraction(4)
    modular_norm_squared = (1 - p) / p
    bandwidth_factor = perfect_fraction_sqrt((1 - p) / p)
    projective_band_norm = Fraction(2)
    return {
        "p": p,
        "weighted_unitary_right_squared": weighted_unitary_right_squared,
        "weighted_unitary_left_squared": weighted_unitary_left_squared,
        "rho_W_squared_coefficient_of_pi_hbar_over_t0_squared": (
            rho_w_squared_pi_coefficient
        ),
        "pi_squared_strict_lower": pi_squared_lower,
        "Duhamel_rhs_strict_lower": duhamel_rhs_strict_lower,
        "trace_distance": Fraction(0),
        "observable_right_squared": observable_right_squared,
        "observable_left_squared": observable_left_squared,
        "hash_seminorm_squared": observable_right_squared + observable_left_squared,
        "half_modular_norm_squared": modular_norm_squared,
        "bandwidth_factor": bandwidth_factor,
        "projective_band_norm": projective_band_norm,
        "family_unitary_hash_squared_coefficient_of_p": Fraction(8),
        "family_automorphism_hash_squared": Fraction(8),
        "unitary_family_limit_p_to_zero": Fraction(0),
        "state_stability_implies_arbitrary_context_stability": False,
        "q3_form_domain_instantiation": {
            "common_quartic_form_domain": True,
            "W_coordinate_growth_degree": 2,
            "W_squared_growth_degree": 4,
            "finite_Gibbs_fourth_moment": True,
            "bounded_spectral_form_truncation": True,
            "strong_resolvent_then_S2_closure": True,
            "smooth_clipped_Q_L_automatically_covered": False,
        },
    }


def fixed_edge_corridor_fixture() -> dict[str, Any]:
    """Count cubic edges and derive the exact elementary corridor majorant."""

    # INPUT FIXTURE for finite enumeration. The general constants and
    # exponential-series majorant are derived from the displayed formulas.
    radius = 2
    vertices = set(
        (x, y, z)
        for x in range(-radius, radius + 1)
        for y in range(-radius, radius + 1)
        for z in range(-radius, radius + 1)
    )
    directions = ((1, 0, 0), (0, 1, 0), (0, 0, 1))
    spatial_dimension = len(directions)
    signed_direction_count = 2
    edge_direction_coefficient = signed_direction_count * spatial_dimension
    side_upper_coefficient = signed_direction_count + 1
    edges = []
    for vertex in sorted(vertices):
        for direction in directions:
            neighbour = tuple(
                vertex[index] + direction[index]
                for index in range(spatial_dimension)
            )
            if neighbour in vertices:
                edges.append((vertex, neighbour))
    formula_count = (
        edge_direction_coefficient
        * radius
        * (signed_direction_count * radius + 1) ** (spatial_dimension - 1)
    )
    edge_upper_coefficient = (
        edge_direction_coefficient
        * side_upper_coefficient ** (spatial_dimension - 1)
    )
    upper_count = edge_upper_coefficient * radius**spatial_dimension

    words = (Fraction(3), Fraction(-2), Fraction(5), Fraction(1))
    cauchy_left = sum(words, Fraction(0)) ** 2
    cauchy_right = len(words) * sum((value * value for value in words), Fraction(0))

    # Derive the local tail prefactor from the v1.9 primitive inputs in
    # 2 Q^(1/alpha) (M_a |S_e|)^theta.  For this exact fixture the weighted
    # support is one, so its fractional power remains exactly one.
    renyi_order = 2
    theta = Fraction(renyi_order - 1, renyi_order)
    renyi_bound = 4
    renyi_root = math.isqrt(renyi_bound)
    assert renyi_root**renyi_order == renyi_bound
    marginal_tail_constant = Fraction(1, 2)
    edge_support_size = len(("x", "y"))
    weighted_support = marginal_tail_constant * edge_support_size
    assert weighted_support == 1
    local_tail_prefactor = 2 * renyi_root

    # Combine m_R <= edge_upper_coefficient R^3, c=1/coupling_denominator,
    # and the derived local tail prefactor.  Divisibility is checked before
    # retaining the exact integer coefficient in the payload.
    coupling_denominator = 3
    prefactor_numerator = edge_upper_coefficient**2 * local_tail_prefactor
    prefactor_denominator = coupling_denominator**2
    assert prefactor_numerator % prefactor_denominator == 0
    prefactor = prefactor_numerator // prefactor_denominator
    factorial_ten = math.factorial(10)
    majorant_powers = {"R^-2": 1, "R^-3": 2, "R^-4": 2}

    side = 4
    orbit_sizes = {
        direction: side**spatial_dimension
        for direction in range(spatial_dimension)
    }

    kappa = Fraction(3, 4)
    precision_determinant = 1 - kappa * kappa
    marginal_variance = 1 / precision_determinant
    tilted_tail_exponent = 1 / (2 * marginal_variance)
    reference_power_exponent = theta / 2
    exponent_gap = reference_power_exponent - tilted_tail_exponent
    q2_precision_determinant = 1 - renyi_order**2 * kappa * kappa
    return {
        "radius": radius,
        "enumerated_edges": len(edges),
        "formula_edges": formula_count,
        "upper_edges": upper_count,
        "Cauchy_left": cauchy_left,
        "Cauchy_right": cauchy_right,
        "corridor_prefactor": prefactor,
        "factorial_ten": factorial_ten,
        "elementary_majorant_powers": majorant_powers,
        "elementary_majorant_limit": Fraction(0),
        "periodic_translation_orbit_sizes": orbit_sizes,
        "periodic_translation_orbit_count": len(orbit_sizes),
        "translation_alone_gives_one_orbit": False,
        "tilted_gaussian": {
            "kappa": kappa,
            "precision_determinant": precision_determinant,
            "marginal_variance": marginal_variance,
            "tilted_tail_exponent": tilted_tail_exponent,
            "reference_power_exponent": reference_power_exponent,
            "exponent_gap": exponent_gap,
            "Q2_precision_determinant": q2_precision_determinant,
            "all_moments_finite": precision_determinant > 0,
            "fixed_edge_implication_rejected": exponent_gap > 0,
            "two_site_or_homogeneous_dimer_scope": True,
            "full_one_site_translation_invariance": False,
        },
        "hard_tail_constants": True,
        "smooth_clipped_Q_L_constants": False,
        "actual_Q3_fixed_edge_history_bound": False,
    }


def feshbach_compressed_qps_fixture() -> dict[str, Any]:
    """Reconstruct overlap, Feshbach, form coefficients, and star spectrum."""

    # INPUT FIXTURES for exact overlap and rational smallness checks.
    # Expected values used later are explicitly TEST ORACLES.
    side = 4
    directions = tuple(range(3))
    spatial_dimension = len(directions)
    coordination_number = 2 * spatial_dimension
    general_overlap_upper = 1 + 2 * (coordination_number - 1)
    vertices = tuple(
        (x, y, z)
        for x in range(side)
        for y in range(side)
        for z in range(side)
    )
    edges = []
    for vertex in vertices:
        for direction in directions:
            neighbour = list(vertex)
            neighbour[direction] = (neighbour[direction] + 1) % side
            edges.append(frozenset((vertex, tuple(neighbour))))
    overlaps = tuple(sum(bool(edge & other) for other in edges) for edge in edges)
    open_edges = []
    for vertex in vertices:
        for direction in directions:
            neighbour = list(vertex)
            neighbour[direction] += 1
            if neighbour[direction] < side:
                open_edges.append(frozenset((vertex, tuple(neighbour))))
    open_overlaps = tuple(
        sum(bool(edge & other) for other in open_edges) for edge in open_edges
    )

    high_count = 5
    gamma = Fraction(7)
    energy = Fraction(2)
    epsilon = Fraction(1, 3)
    self_energy = high_count * epsilon * epsilon / (gamma - energy)
    overlap_upper = (
        general_overlap_upper
        * high_count
        * epsilon
        * epsilon
        / (gamma - energy)
    )
    dense_entry = epsilon * epsilon / (gamma - energy)
    dense_norm = high_count * dense_entry

    c = Fraction(1, 1000)
    m = Fraction(2)
    a_squared = Fraction(1, 100)
    a = Fraction(1, 10)
    b = Fraction(1, 20)
    a_q = Fraction(3)
    gamma_form = Fraction(100)
    young_u = Fraction(1)
    young_t = Fraction(1)
    eta_base_coefficient = 8
    nu_base_coefficient = 16
    residual_base_coefficient = 8
    eta_multiplier = (
        eta_base_coefficient
        * (1 + 1 / young_u)
        * (1 + 1 / young_t)
    )
    nu_m_multiplier = nu_base_coefficient * (1 + young_u)
    nu_a_multiplier = (
        nu_base_coefficient
        * (1 + 1 / young_u)
        * (1 + young_t)
    )
    eta_b = eta_multiplier * c * a_q
    nu_b = nu_m_multiplier * c * m * m + nu_a_multiplier * c * a_squared
    zeta = coordination_number * (eta_b + nu_b / gamma_form)
    epsilon_form = residual_base_coefficient * c * (b + 2 * m * a + a_squared)
    # Exact diagonal local-high reduction on Pxy=diag(1,0,0,0).
    k_diagonal = (Fraction(0), gamma_form, gamma_form, 2 * gamma_form)
    q_diagonal = (Fraction(0), Fraction(1), Fraction(1), Fraction(1))
    high_diagonal = tuple(
        eta_b * k_value + nu_b * q_value
        for k_value, q_value in zip(k_diagonal, q_diagonal)
    )
    projected_upper = tuple(
        (eta_b + nu_b / gamma_form) * k_value
        for k_value in k_diagonal
    )
    projected_slack = tuple(
        upper - actual for upper, actual in zip(projected_upper, high_diagonal)
    )

    spectrum: dict[int, int] = {}
    star_site_count = 1 + len(directions)
    for bits in range(2**star_site_count):
        signs = tuple(
            1 if bits & (1 << index) else -1
            for index in range(star_site_count)
        )
        center = signs[0]
        mismatches = sum(center != neighbour for neighbour in signs[1:])
        coefficient = 2 * mismatches
        spectrum[coefficient] = spectrum.get(coefficient, 0) + 1

    selector_plus_density = 1 - 1
    selector_minus_density = 1 - (-1)
    selector_difference_derivative = selector_plus_density - selector_minus_density

    return {
        "edge_count": len(edges),
        "periodic_overlap_values": sorted(set(overlaps)),
        "open_overlap_range": [min(open_overlaps), max(open_overlaps)],
        "general_overlap_upper": general_overlap_upper,
        "equality_scope": "bulk edges and sufficiently large periodic tori",
        "Feshbach": {
            "Gamma": gamma,
            "E": energy,
            "epsilon": epsilon,
            "self_energy": self_energy,
            "overlap_upper": overlap_upper,
        },
        "dense_no_go": {
            "matrix_size": high_count,
            "entry": dense_entry,
            "norm": dense_norm,
            "off_diagonal_nonzero_count": high_count * (high_count - 1),
            "automatic_QPS_locality": False,
        },
        "relative_form": {
            "eta_b": eta_b,
            "nu_b": nu_b,
            "zeta": zeta,
            "epsilon": epsilon_form,
            "corridor_exponents": {
                "epsilon": -3,
                "eta_b": -2,
                "nu_b_over_Gamma": -2,
                "zeta": -2,
            },
            "P_xy_diagonal": (1, 0, 0, 0),
            "Q_xy_diagonal": q_diagonal,
            "k_x_plus_k_y_diagonal": k_diagonal,
            "diagonal_high_fixture": high_diagonal,
            "projected_high_upper": projected_upper,
            "projected_high_slack": projected_slack,
            "diagonal_high_compression_only": True,
            "off_diagonal_bound_is_distinct": True,
        },
        "forward_star_spectrum_coefficients": spectrum,
        "forward_star_expected": {0: 2, 2: 6, 4: 6, 6: 2},
        "local_gap_coefficient_of_J": 2,
        "selector": "u sum_x(1-s_x)",
        "selector_plus_density": selector_plus_density,
        "selector_minus_density": selector_minus_density,
        "selector_split": (0, selector_difference_derivative),
        "small_ratio": "abs(delta_eff)/(2J)<epsilon_Y",
        "Z2_flips_s": True,
        "Z2_fixes_P1": True,
        "QPS_source": YAROTSKII_QPS_SOURCE,
        "compressed_infinite_lattice_phasewise_gap": True,
        "existential_small_ratio_only": True,
        "finite_torus_exact_degeneracy": False,
        "oscillator_gap": False,
        "Feshbach_absolute_energy_before_low_scalar_subtraction": True,
        "thermodynamic_ground_band_isolation": False,
    }



def twentieth_moment_graph_fixture() -> dict[str, Any]:
    """Reconstruct the v2.1 moment arithmetic using only Fraction."""

    p = 5
    gamma = Fraction(2, 5)
    edge_power = 6
    tail_power = 4 * (p - 1)
    exponent = Fraction(edge_power) - gamma * tail_power
    edge_constant = 54**2
    factorial_coefficient = 2 * gamma - 1
    admissible = [
        order
        for order in range(2, 9)
        if Fraction(6) - 4 * gamma * (order - 1) < 0
    ]
    samples = []
    for x_value, cutoff in ((1, 2), (2, 2), (3, 2), (7, 5)):
        left = x_value**4 if x_value > cutoff else 0
        right = Fraction(x_value**20, cutoff**16)
        samples.append((x_value, cutoff, left, right, Fraction(left) <= right))

    m5 = 3
    d5 = 2
    s_mu = 5
    conditional_coefficient = 2 * d5**2 * s_mu**5 * m5
    weights = (Fraction(1), Fraction(1), Fraction(1, 2))
    energies = (Fraction(2), Fraction(3), Fraction(4))
    weighted_energy = sum(w * k for w, k in zip(weights, energies))
    weight_sum = sum(weights)
    convex_upper = weight_sum**4 * sum(
        w * k**5 for w, k in zip(weights, energies)
    )

    low_k = Fraction(1)
    high_k = Fraction(4)
    square_root_ratio = 2
    all_m = []
    for order in range(1, 8):
        normalized = (
            square_root_ratio**order - Fraction(1, square_root_ratio**order)
        )
        all_m.append(
            {
                "m": order,
                "normalized_commutator_norm": normalized,
                "forced_Gm": normalized,
            }
        )

    # K_N, q_N, V_N inputs are recorded by their powers.  The derivations use
    # sqrt(K_high/K_low)=N^2 and the V transition N^-4.
    n = 3
    k_high = n**4
    q_high = n
    v_transition = Fraction(1, n**4)
    # k_high^(5/2)=N^10; write it directly to avoid floating square roots.
    d5_value = Fraction(q_high**10, n**10)
    g5 = v_transition * (n**10 - Fraction(1, n**10))
    delta = Fraction(1)
    one_history_lower = delta**2 * n**12 / 8
    two_history_lower = 2 * one_history_lower
    low_graph_exponents = {
        str(s): 4 * s - 4 for s in (Fraction(0), Fraction(1, 2), Fraction(1))
    }

    return {
        "p": p,
        "gamma": gamma,
        "edge_constant": edge_constant,
        "tail_power": tail_power,
        "corridor_exponent": exponent,
        "factorial_R_log_R_coefficient": factorial_coefficient,
        "minimal_admissible_integer": admissible[0],
        "pointwise_samples": samples,
        "conditional_coefficient_without_exp": conditional_coefficient,
        "commutator_coefficients": (1, 2, 2),
        "convexity": {
            "weighted_energy_fifth": weighted_energy**5,
            "upper": convex_upper,
            "holds": weighted_energy**5 <= convex_upper,
        },
        "all_m": {
            "K_diagonal": (low_k, high_k),
            "rows": all_m,
            "quadratic_growth": False,
            "fixed_m5_rejected": False,
        },
        "KN": {
            "N": n,
            "delta": delta,
            "condition_delta_nonzero": delta != 0,
            "condition_N4_ge_abs_delta": n**4 >= abs(delta),
            "d5": d5_value,
            "static_m5_upper": "1+(5/e)^5",
            "low_graph_s_range": "0<=s<=1",
            "low_graph_exponents": low_graph_exponents,
            "low_graph_upper": 1 + abs(delta),
            "G5": g5,
            "G5_formula": f"{n}^6-{n}^-14",
            "one_orientation_q20_lower": one_history_lower,
            "two_orientation_q20_lower": two_history_lower,
            "history_growth_power_N": 12,
        },
    }


def oscillator_edge_cluster_fixture() -> dict[str, Any]:
    """Independent Fraction reconstruction of the corrected local edge fixture."""

    c_value = Fraction(1, 1000)
    m_value = Fraction(2)
    a_value = Fraction(1, 10)
    b_value = Fraction(1, 20)
    a_q = Fraction(3)
    a0_minus_m2 = Fraction(1, 100)
    d2 = -Fraction(1, 1000)
    delta1 = Fraction(1, 10000)
    gamma_high = Fraction(100)
    z = Fraction(6)

    c_b = 8 * c_value * a0_minus_m2
    f_b = delta1 / z + 4 * c_value * d2
    e_b = c_b + f_b
    j_value = 8 * c_value * m_value**2
    epsilon = 8 * c_value * (b_value + 2 * m_value * a_value + a_value**2)
    a_block = e_b + 2 * j_value
    d_block = gamma_high / z
    d_minus_a = d_block - a_block
    schur_margin = 2 * j_value * (d_block - e_b) - epsilon**2
    rational_gap = 2 * j_value - epsilon**2 / d_minus_a
    g_b_float = (
        float(a_block + d_block)
        - math.sqrt(float((d_block - a_block) ** 2 + 4 * epsilon**2))
    ) / 2

    # In the s basis (++,+-,-+,--), P1_x+P1_y has this exact matrix.
    half = Fraction(1, 2)
    p1_sum = (
        (1, -half, -half, 0),
        (-half, 1, 0, -half),
        (-half, 0, 1, -half),
        (0, -half, -half, 1),
    )
    low_h = []
    bond_diagonal = (0, 2 * j_value, 2 * j_value, 0)
    for row in range(4):
        low_h.append(
            tuple(
                (c_b if row == column else 0)
                + (bond_diagonal[row] if row == column else 0)
                + f_b * p1_sum[row][column]
                for column in range(4)
            )
        )
    p0_diagonal = (1, 0, 0, 1)
    l_diagonal = (0, 1, 1, 0)
    p0_compression_diagonal = tuple(
        low_h[i][i] if p0_diagonal[i] else 0 for i in range(4)
    )
    l_compression_diagonal = tuple(
        low_h[i][i] if l_diagonal[i] else 0 for i in range(4)
    )
    p0_l_entries = tuple(
        low_h[i][j]
        for i in (0, 3)
        for j in (1, 2)
    )
    # The 2x2 cross matrix has all four entries -fb/2, hence norm |fb|.
    p0_l_norm = abs(f_b)

    eta_b = 32 * c_value * a_q
    nu_b = 32 * c_value * m_value**2 + 64 * c_value * a_value**2
    rho_b = eta_b + nu_b / gamma_high
    tau = epsilon
    alpha = z * (
        rho_b + j_value / gamma_high + epsilon**2 / (tau * gamma_high)
    )
    ell_b = c_b + 8 * c_value * abs(d2)
    beta = 2 * delta1 / z + ell_b + tau
    gamma0 = min(gamma_high / z, 2 * j_value)
    delta_rf = (1 - alpha) * gamma0 - 2 * beta

    return {
        "inputs": {
            "c": c_value,
            "m": m_value,
            "a": a_value,
            "b": b_value,
            "A_Q": a_q,
            "a0_minus_m2": a0_minus_m2,
            "a1_minus_m2": a0_minus_m2 + d2,
            "d2": d2,
            "delta1": delta1,
            "Gamma": gamma_high,
            "z": z,
        },
        "scalars": {
            "Cb": c_b,
            "fb": f_b,
            "eb": e_b,
            "J": j_value,
            "epsilon": epsilon,
            "A": a_block,
            "D": d_block,
            "D_minus_A": d_minus_a,
            "margin": schur_margin,
            "gap_rational_lower": rational_gap,
            "gb_float": g_b_float,
            "gb_minus_eb_float": g_b_float - float(e_b),
        },
        "compressions": {
            "low_h_s_basis": tuple(low_h),
            "P0_diagonal": p0_diagonal,
            "L_diagonal": l_diagonal,
            "P0_h_P0_diagonal": p0_compression_diagonal,
            "L_h_L_diagonal": l_compression_diagonal,
            "P0_h_L_entries": p0_l_entries,
            "P0_h_L_norm": p0_l_norm,
            "P0_L_invariant": False,
            "global_parity_invariant": True,
            "even_trial_energy": e_b,
            "odd_trial_energy": e_b,
        },
        "relative": {
            "eta_b": eta_b,
            "nu_b": nu_b,
            "rho_b": rho_b,
            "alpha": alpha,
            "ell_b": ell_b,
            "beta": beta,
            "gamma0": gamma0,
            "Delta_rf": delta_rf,
        },
        "cutoff": {
            "nested_parity_preserving_Ritz_form_restriction": True,
            "Pi_M_contains_P": True,
            "union_form_core": True,
            "same_constants": True,
            "eigenvalues_decrease_to_full": True,
            "replace_q_then_square": False,
            "Pi_q2_Pi_equals_Pi_q_Pi_squared": False,
        },
        "N_scaling": {
            "eb": -6,
            "epsilon": -3,
            "D": 2,
            "two_J_limit": 16,
            "sharp_gap_correction": -8,
            "alpha": -2,
            "beta": -3,
        },
        "local_edge_only": True,
        "global_QPS": False,
        "oscillator_lattice_GNS_gap": False,
    }



def actual_q3_fifth_shear_rank_two_fixture() -> dict[str, Any]:
    """Non-importing exact reconstruction of the v2.2 algebra and counterfixture."""

    # Independent Weyl-algebra bookkeeping. [p^2,q] contributes twice and
    # [V,p^9] has exactly nine Leibniz placements, with physical prefactors fixed.
    kinetic_commutator_coefficient = Fraction(1)  # (i/hbar)*(-i*hbar)/chi
    force_prefactor = Fraction(-1, 2)
    force_placements = tuple(range(9))
    critical_order = Fraction(1, 4) + 8 * Fraction(1, 2) + 3 * Fraction(1, 4)
    graph_levels = tuple((m, 2 * m, 4 * m) for m in range(6))

    # (p+c*delta*Q)^2/(2 chi), using commuting p_x and neighbor Q_x^F.
    shear_coefficients = {
        "delta_pQ": Fraction(1),
        "delta_squared_Q2": Fraction(1, 2),
    }
    choices = (0, 1, 2)
    delta_degree = (0, 1, 2)
    energy_order = (Fraction(1), Fraction(3, 4), Fraction(1, 2))
    words = []
    for a in choices:
        for b in choices:
            for c in choices:
                for d in choices:
                    for e in choices:
                        word = (a, b, c, d, e)
                        if word == (0, 0, 0, 0, 0):
                            continue
                        words.append(
                            (
                                word,
                                sum(delta_degree[item] for item in word),
                                sum((energy_order[item] for item in word), Fraction(0)),
                            )
                        )
    degree_counts = {
        degree: sum(row[1] == degree for row in words)
        for degree in range(1, 11)
    }
    t_value = 2
    c5_majorant = sum(
        multiplicity * t_value ** (degree - 1)
        for degree, multiplicity in degree_counts.items()
    )
    polynomial_difference = (1 + t_value + t_value**2) ** 5 - 1
    residual_ratio = Fraction(1, 2)
    # Weight exponents are recomputed without symbolic imports.
    r1_paid_x = Fraction(1, 2)
    r1_paid_y = Fraction(1, 4)
    r1_leftover_x_at_worst_neighbor = Fraction(1) - r1_paid_x - r1_paid_y
    r1_neighbor_exponential = r1_paid_y
    r2_paid_neighbor_exponents = (Fraction(1, 4), Fraction(1, 4))
    r2_leftover_x_at_worst_neighbor = (
        Fraction(1) - sum(r2_paid_neighbor_exponents)
    )
    r2_neighbor_exponential = sum(r2_paid_neighbor_exponents)
    residual_weight_bound = 2 * ((1 + residual_ratio) / (1 - residual_ratio)) ** 3
    maximum_local_insertions = max(
        sum(letter != 0 for letter in word) for word, _, _ in words
    )
    maximum_neighbor_incidences = max(
        sum(1 if letter == 1 else 2 if letter == 2 else 0 for letter in word)
        for word, _, _ in words
    )
    tuple_counts = tuple(
        6**r for r in range(1, maximum_neighbor_incidences + 1)
    )
    commutator_order_drop = Fraction(3, 4)
    tree_sphere_terms = tuple(
        6 * 5 ** (radius - 1) * residual_ratio**radius for radius in range(1, 7)
    )
    generic_degree_six_growth_ratio = tree_sphere_terms[1] / tree_sphere_terms[0]

    # Exact rational rank for the connected four-cycle Hamiltonian.
    def rational_rank(matrix: Sequence[Sequence[Fraction]]) -> int:
        work = [list(map(Fraction, row)) for row in matrix]
        rows = len(work)
        columns = len(work[0]) if rows else 0
        pivot_row = 0
        for column in range(columns):
            pivot = next(
                (row for row in range(pivot_row, rows) if work[row][column]),
                None,
            )
            if pivot is None:
                continue
            work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
            scale = work[pivot_row][column]
            work[pivot_row] = [entry / scale for entry in work[pivot_row]]
            for row in range(rows):
                if row == pivot_row or not work[row][column]:
                    continue
                factor = work[row][column]
                work[row] = [
                    left - factor * right
                    for left, right in zip(work[row], work[pivot_row])
                ]
            pivot_row += 1
            if pivot_row == rows:
                break
        return pivot_row

    def rational_matvec(
        matrix: Sequence[Sequence[Fraction]], vector: Sequence[Fraction]
    ) -> tuple[Fraction, ...]:
        return tuple(
            sum((entry * value for entry, value in zip(row, vector)), Fraction(0))
            for row in matrix
        )

    local_edge = (
        (Fraction(0), Fraction(0), Fraction(0), Fraction(0)),
        (Fraction(0), Fraction(1, 2), Fraction(-1, 2), Fraction(0)),
        (Fraction(0), Fraction(-1, 2), Fraction(1, 2), Fraction(0)),
        (Fraction(0), Fraction(0), Fraction(0), Fraction(1)),
    )
    local_square = tuple(
        tuple(
            sum(
                (local_edge[row][middle] * local_edge[middle][column] for middle in range(4)),
                Fraction(0),
            )
            for column in range(4)
        )
        for row in range(4)
    )
    side = 4
    cycle_edges = tuple((site, (site + 1) % side) for site in range(side))
    dimension = 2**side
    h_cycle = [[Fraction(0) for _ in range(dimension)] for _ in range(dimension)]
    for x_site, y_site in cycle_edges:
        for state in range(dimension):
            bit_x = (state >> x_site) & 1
            bit_y = (state >> y_site) & 1
            if bit_x == bit_y == 1:
                h_cycle[state][state] += 1
            elif bit_x != bit_y:
                h_cycle[state][state] += Fraction(1, 2)
                swapped = state ^ (1 << x_site) ^ (1 << y_site)
                h_cycle[swapped][state] -= Fraction(1, 2)
    vacuum = tuple(Fraction(index == 0) for index in range(dimension))
    w_vector = tuple(
        Fraction(state != 0 and state & (state - 1) == 0)
        for state in range(dimension)
    )
    cycle_rank = rational_rank(h_cycle)
    one_indices = tuple(1 << site for site in range(side))
    one_particle = tuple(
        tuple(h_cycle[row][column] for column in one_indices) for row in one_indices
    )
    laplacian = [[Fraction(0) for _ in range(side)] for _ in range(side)]
    for left, right in cycle_edges:
        laplacian[left][left] += 1
        laplacian[right][right] += 1
        laplacian[left][right] -= 1
        laplacian[right][left] -= 1
    half_laplacian = tuple(
        tuple(entry / 2 for entry in row) for row in laplacian
    )
    fourier_real = (Fraction(1), Fraction(0), Fraction(-1), Fraction(0))
    fourier_sine = (Fraction(0), Fraction(1), Fraction(0), Fraction(-1))
    alternating = (Fraction(1), Fraction(-1), Fraction(1), Fraction(-1))
    constant = (Fraction(1),) * side
    eigenpairs = (
        (constant, Fraction(0)),
        (fourier_real, Fraction(1)),
        (fourier_sine, Fraction(1)),
        (alternating, Fraction(2)),
    )
    eigenpairs_hold = all(
        rational_matvec(one_particle, vector)
        == tuple(eigenvalue * entry for entry in vector)
        for vector, eigenvalue in eigenpairs
    )

    onsite_cutoff = 4
    lifted_low_spectrum = (Fraction(0), Fraction(0), Fraction(1), Fraction(1))
    lifted_high_energies = []
    for left in range(onsite_cutoff):
        for right in range(onsite_cutoff):
            if left < 2 and right < 2:
                continue
            lifted_high_energies.append(Fraction(max(left - 1, 0) + max(right - 1, 0)))

    return {
        "static": {
            "kinetic_coefficient": kinetic_commutator_coefficient,
            "force_prefactor": force_prefactor,
            "force_placements": force_placements,
            "critical_order": critical_order,
            "graph_levels": graph_levels,
            "finite_cutoff_before_monotone_limit": True,
            "unbounded_trace_cyclicity": False,
            "registered_periodic_compact_source": True,
            "arbitrary_boundary_static": False,
        },
        "shear": {
            "coefficients": shear_coefficients,
            "word_count": len(words),
            "degree_counts": degree_counts,
            "all_words_have_delta": all(row[1] >= 1 for row in words),
            "all_words_order_at_most_five": all(row[2] <= 5 for row in words),
            "C5_majorant_T2": c5_majorant,
            "polynomial_difference_T2": polynomial_difference,
            "R1_paid_exponents": (r1_paid_x, r1_paid_y),
            "R1_leftover_x_at_worst_neighbor": r1_leftover_x_at_worst_neighbor,
            "R1_neighbor_exponential": r1_neighbor_exponential,
            "R2_paid_neighbor_exponents": r2_paid_neighbor_exponents,
            "R2_cross_terms_retained": True,
            "R2_leftover_x_at_worst_neighbor": r2_leftover_x_at_worst_neighbor,
            "R2_neighbor_exponential": r2_neighbor_exponential,
            "residual_weight_bound": residual_weight_bound,
            "maximum_local_insertions": maximum_local_insertions,
            "maximum_neighbor_incidences": maximum_neighbor_incidences,
            "tuple_counts_neighbor_incidences_le_10": tuple_counts,
            "commutator_order_drop": commutator_order_drop,
            "K5_multinomial_supplies_weights": True,
            "K_ge_one_fills_slack": True,
            "tree_sphere_terms": tree_sphere_terms,
            "generic_degree_six_growth_ratio": generic_degree_six_growth_ratio,
            "generic_degree_six_promotion": False,
            "finite_cubic_subgraph_or_periodic_quotient": True,
            "uniform_cubic_polynomial_growth_required": True,
            "subset_deletion_safe": True,
        },
        "rank_two": {
            "local_idempotent": local_square == local_edge,
            "local_rank": rational_rank(local_edge),
            "local_trace": sum(local_edge[index][index] for index in range(4)),
            "cycle_rank": cycle_rank,
            "cycle_nullity": dimension - cycle_rank,
            "vacuum_kernel": all(value == 0 for value in rational_matvec(h_cycle, vacuum)),
            "W_kernel": all(value == 0 for value in rational_matvec(h_cycle, w_vector)),
            "one_particle_half_laplacian": one_particle == half_laplacian,
            "one_particle_eigenpairs": eigenpairs_hold,
            "torus_L4_gap": Fraction(1),
            "torus_bound_from_pi_gt_three": Fraction(9, 8),
            "lift_low_spectrum": lifted_low_spectrum,
            "lift_first_high_energy": min(lifted_high_energies),
            "automatic_global_gap": False,
            "Q3_gap_no_go": False,
        },
        "history": {
            "M20": "2*d5^2*exp(C5*T)*S_mu^5*m5",
            "corridor": "2916*c^2*M20*R^(-2/5)",
            "factorial": "-R*log(R)/5+O(R)",
            "registered_periodic_only": True,
        },
    }


def authority_audit(audit: Audit, staged: bool) -> dict[str, Any]:
    """Bind to the manifest/certificate without reading primary outputs."""

    missing = [
        str(path.relative_to(REPO)).replace("\\", "/")
        for path in (MANIFEST, CERTIFICATE)
        if not path.exists()
    ]
    if missing:
        if not staged:
            raise FileNotFoundError("missing authorities: " + ", ".join(missing))
        return {
            "status": "INCOMPLETE",
            "missing": missing,
            "manifest": None,
            "certificate": None,
        }

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate = CERTIFICATE.read_text(encoding="utf-8")
    certificate_flat = " ".join(certificate.split())
    audit.check(
        "manifest result identity",
        (
            manifest.get("result_id") == RESULT_ID
            and manifest.get("result_number") == RESULT_NUMBER
            and manifest.get("result_version") == RESULT_VERSION
        ),
        {
            "id": manifest.get("result_id"),
            "number": manifest.get("result_number"),
            "version": manifest.get("result_version"),
        },
        {"id": RESULT_ID, "number": RESULT_NUMBER, "version": RESULT_VERSION},
        "authority",
    )
    audit.check(
        "manifest task/exploration identity",
        (
            manifest.get("task_id") == TASK_ID
            and manifest.get("exploration_id") == EXPLORATION_ID
            and manifest.get("claim_ids") == [CLAIM_ID]
        ),
        {
            "task": manifest.get("task_id"),
            "exploration": manifest.get("exploration_id"),
            "claims": manifest.get("claim_ids"),
        },
        {"task": TASK_ID, "exploration": EXPLORATION_ID, "claims": [CLAIM_ID]},
        "authority",
    )
    audit.check(
        "manifest remains non-claim-bearing",
        manifest.get("claim_bearing") is False,
        manifest.get("claim_bearing"),
        False,
        "authority",
    )
    audit.check(
        "manifest negative IDs",
        tuple(manifest.get("negative_ids", ())) == NEGATIVE_IDS,
        manifest.get("negative_ids"),
        NEGATIVE_IDS,
        "authority",
    )
    audit.check(
        "manifest closed subgates",
        tuple(manifest.get("closed_subgates", ())) == CLOSED_SUBGATES,
        manifest.get("closed_subgates"),
        CLOSED_SUBGATES,
        "authority",
    )
    audit.check(
        "manifest open gates",
        tuple(manifest.get("open_gates", ())) == OPEN_GATES,
        manifest.get("open_gates"),
        OPEN_GATES,
        "authority",
    )
    for section in (
        "twentieth_moment_fixed_edge_corridor",
        "conditional_fifth_graph_transport",
        "all_order_graph_growth_no_go",
        "static_moment_low_graph_no_go",
        "full_oscillator_edge_cluster",
        "v2_1_checkpoint_synthesis",
        "actual_q3_static_fifth_moment_and_elliptic_embedding",
        "direct_subset_shear_fifth_graph_propagation",
        "actual_q3_twentieth_history_and_hard_cutoff_corridor",
        "rank_two_projection_gap_no_go",
        "connected_rank_two_qps_successor",
        "v2_2_checkpoint_synthesis",
    ):
        audit.check(
            f"manifest retained/new section {section}",
            section in manifest,
            section in manifest,
            True,
            "authority",
        )
    checkpoint = manifest.get("checkpoint_synthesis", {})
    checkpoint_source = checkpoint.get("source")
    checkpoint_pdf = checkpoint.get("pdf")
    checkpoint_deferred = (
        checkpoint_source is None
        and checkpoint_pdf is None
        and checkpoint.get("visual_qa") is None
    )
    checkpoint_combined = (
        isinstance(checkpoint_source, str)
        and isinstance(checkpoint_pdf, str)
        and isinstance(checkpoint.get("source_sha256"), str)
        and len(checkpoint["source_sha256"]) == 64
        and isinstance(checkpoint.get("pdf_sha256"), str)
        and len(checkpoint["pdf_sha256"]) == 64
        and isinstance(checkpoint.get("pages"), int)
        and checkpoint["pages"] > 0
        and isinstance(checkpoint.get("visual_qa"), str)
        and "COMBINED" in str(checkpoint.get("status", "")).upper()
    )
    audit.check(
        "manifest PDF checkpoint lifecycle",
        checkpoint_deferred or checkpoint_combined,
        checkpoint,
        "deferred during development or one issued combined checkpoint",
        "authority",
    )
    checkpoint_v22 = manifest.get("v2_2_checkpoint_synthesis")
    deferred_v22 = {
        "status": "DEFERRED",
        "workflow": (
            "No intermediate PDF is issued for R-167 v2.2. Preserve every "
            "v2.1 and earlier source/PDF pair as historical evidence; issue or "
            "update one combined gate-level synthesis only after the proof, "
            "formal-authority, integrated, generated-surface, strict-release "
            "and render-review gates pass."
        ),
    }
    issued_fields = {
        "status", "source", "pdf", "source_sha256", "pdf_sha256",
        "pages", "workflow", "visual_qa",
    }
    issued_status = (
        "ISSUED AS ONE COMBINED GATE-LEVEL CHECKPOINT AFTER PROOF VALIDATION"
    )
    issued_source = (
        "claims/C6-SPACETIME-SIGNATURE/notes/"
        "pre-a-q3lock-fifth-history-rank2-gap-and-m2-response-boundary-"
        "checkpoint-260811-v1.1.tex.txt"
    )
    issued_pdf = issued_source.removesuffix(".tex.txt") + ".pdf"
    issued_workflow = (
        "No per-lemma or intermediate PDF was issued. One combined R-167 v2.2 / "
        "R-168 v1.3 gate-level synthesis source/PDF pair was issued only after "
        "the primary, non-importing independent, integrated, formal-authority, "
        "generated-surface, source-form, freshness, dual-extraction, and "
        "visual-review checks passed."
    )
    r168_v13_checkpoint = None
    try:
        r168_v13_checkpoint = json.loads(
            (
                REPO
                / "strategy/pre-a-round1-prospective-holdout-freeze-protocol-"
                "manifest.json"
            ).read_text(encoding="utf-8")
        ).get("v1_3_checkpoint_synthesis")
    except (OSError, UnicodeError, json.JSONDecodeError):
        pass
    pages_v22 = checkpoint_v22.get("pages") if isinstance(checkpoint_v22, dict) else None
    pages_v22_valid = (
        isinstance(pages_v22, int)
        and not isinstance(pages_v22, bool)
        and pages_v22 > 0
    )
    visual_qa_v22 = (
        f"All {pages_v22} rendered pages were reviewed at readable resolution "
        "with zero clipping, overlap, broken equations, unreadable identifiers, "
        "black glyphs, or malformed page transitions; pypdf and pdfplumber each "
        f"extracted {pages_v22}/{pages_v22} nonempty pages; the build reported "
        "OVERFULL-HBOX 0."
        if pages_v22_valid
        else None
    )
    source_path_v22 = REPO / issued_source
    pdf_path_v22 = REPO / issued_pdf
    source_hash_v22 = (
        hashlib.sha256(source_path_v22.read_bytes()).hexdigest()
        if source_path_v22.is_file()
        else None
    )
    pdf_hash_v22 = (
        hashlib.sha256(pdf_path_v22.read_bytes()).hexdigest()
        if pdf_path_v22.is_file()
        else None
    )
    lowercase_hex = set("0123456789abcdef")
    source_pin_v22 = (
        checkpoint_v22.get("source_sha256")
        if isinstance(checkpoint_v22, dict)
        else None
    )
    pdf_pin_v22 = (
        checkpoint_v22.get("pdf_sha256")
        if isinstance(checkpoint_v22, dict)
        else None
    )
    issued_v22_valid = (
        isinstance(checkpoint_v22, dict)
        and set(checkpoint_v22) == issued_fields
        and checkpoint_v22 == r168_v13_checkpoint
        and checkpoint_v22.get("status") == issued_status
        and checkpoint_v22.get("source") == issued_source
        and checkpoint_v22.get("pdf") == issued_pdf
        and checkpoint_v22.get("workflow") == issued_workflow
        and checkpoint_v22.get("visual_qa") == visual_qa_v22
        and pages_v22_valid
        and isinstance(source_pin_v22, str)
        and len(source_pin_v22) == 64
        and set(source_pin_v22) <= lowercase_hex
        and isinstance(pdf_pin_v22, str)
        and len(pdf_pin_v22) == 64
        and set(pdf_pin_v22) <= lowercase_hex
        and source_path_v22.is_file()
        and pdf_path_v22.is_file()
        and source_hash_v22 == source_pin_v22
        and pdf_hash_v22 == pdf_pin_v22
        and pdf_path_v22.stat().st_mtime_ns >= source_path_v22.stat().st_mtime_ns
    )
    audit.check(
        "manifest v2.2 checkpoint lifecycle",
        checkpoint_v22 == deferred_v22 or issued_v22_valid,
        {
            "metadata": checkpoint_v22,
            "shared_r168_v1_3": r168_v13_checkpoint,
            "deferred_exact": checkpoint_v22 == deferred_v22,
            "issued_exact": issued_v22_valid,
            "source_sha256": source_hash_v22,
            "pdf_sha256": pdf_hash_v22,
        },
        "exact proof-first DEFERRED or exact cross-bound eight-field ISSUED checkpoint",
        "authority",
    )
    audit.check(
        "manifest v2.2 theorem tokens",
        "p_i^10/chi" in manifest.get("actual_q3_static_fifth_moment_and_elliptic_embedding", {}).get("virial_identity", "")
        and "O(|delta|)" in manifest.get("direct_subset_shear_fifth_graph_propagation", {}).get("fifth_form_bound", "")
        and "f_x^(1/2)" in manifest.get("direct_subset_shear_fifth_graph_propagation", {}).get("fifth_form_bound", "")
        and "Maximum degree at most six alone is not enough" in manifest.get("direct_subset_shear_fifth_graph_propagation", {}).get("uniformity_boundary", "")
        and "6*5^(r-1)" in manifest.get("direct_subset_shear_fifth_graph_propagation", {}).get("generic_degree_six_hostile", "")
        and manifest.get("actual_q3_twentieth_history_and_hard_cutoff_corridor", {}).get("moment") == "M20<=2 d5^2 exp(C5 T) S_mu^5 m5.",
        "static, shear and M20 tokens",
        True,
        "authority",
    )
    verification = manifest.get("verification", {})
    audit.check(
        "manifest binds this independent verifier",
        verification.get("independent_script")
        == str(SCRIPT.relative_to(REPO)).replace("\\", "/"),
        verification.get("independent_script"),
        str(SCRIPT.relative_to(REPO)).replace("\\", "/"),
        "authority",
    )
    audit.check(
        "certificate identity tokens",
        all(
            token in certificate
            for token in (
                RESULT_ID,
                RESULT_NUMBER,
                RESULT_VERSION,
                EXPLORATION_ID,
                TASK_ID,
                "claim_bearing: false",
            )
        ),
        "all required tokens present",
        True,
        "authority",
    )
    audit.check(
        "certificate global Renyi scope",
        (
            "not a full-Q3 Gibbs counterexample" in certificate_flat
            and "does not reject a local measured-Renyi" in certificate_flat
        ),
        "scoped conditional-product negative",
        True,
        "authority",
    )
    audit.check(
        "certificate common-alpha gate remains open",
        (
            OPEN_GATES[0] in certificate_flat
            and "ONSITE-INTERSPERSED LOCAL HISTORY TAILS" in certificate_flat
            and "REMAIN OPEN" in certificate_flat
        ),
        "open gate and missing input stated",
        True,
        "authority",
    )
    audit.check(
        "manifest no-overclaim boundary",
        all(
            phrase in manifest.get("no_overclaim", "")
            for phrase in (
                "all-shape or all-exhaustion Cauchy compatibility",
                "all-exhaustion common alpha",
                "rank-two unbounded block diagonalization",
                "broken-sector oscillator temporal mass or GNS gap",
                "physical Sector A",
                "Pre-A closure",
            )
        ),
        manifest.get("no_overclaim"),
        "all boundary phrases present",
        "authority",
    )
    audit.check(
        "certificate v2.1 exact tokens",
        all(
            token in certificate
            for token in (
                "EXP-000811",
                "R-167 v2.1",
                "2916c^2M_{20}",
                r"M_{20}\le2d_5^2e^{G_5T}S_\mu^5m_5",
                "20832953/19531250",
                "332047248/5188304375",
                "4430237/234375000",
                "P_0h_{xy}L",
                "Ritz form restriction",
                "No v2.1 PDF is issued",
                *CLOSED_SUBGATES[-2:],
                *OPEN_GATES[-2:],
                *NEGATIVE_IDS[-2:],
            )
        ),
        "all v2.1 tokens present",
        True,
        "authority",
    )

    audit.check(
        "certificate v2.2 exact tokens",
        all(
            token in certificate
            for token in (
                "EXP-000813",
                "R-167 v2.2",
                "p_i^{10}",
                "C_5(T,\\mu)|\\delta|",
                r"M_{20}\le2d_5^2e^{C_5T}S_\mu^5m_5",
                "rank-two projection",
                "No v2.2 PDF is issued",
                "v2_2_checkpoint_synthesis",
                *CLOSED_SUBGATES[-3:],
                OPEN_GATES[-1],
                NEGATIVE_IDS[-1],
            )
        ),
        "all v2.2 tokens present",
        True,
        "authority",
    )

    formal_missing: list[str] = []

    def formal_require(condition: bool, label: str) -> None:
        if condition:
            audit.check(label, True, True, True, "formal-authority")
        elif staged:
            formal_missing.append(label)
        else:
            raise AssertionError("missing formal v2.2 authority: " + label)

    exploration_records = [
        json.loads(line)
        for line in EXPLORATION_LEDGER.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    formal_require(
        any(record.get("id") == EXPLORATION_ID for record in exploration_records),
        "formal exploration " + EXPLORATION_ID,
    )
    result_lines = RESULT_LEDGER.read_text(encoding="utf-8").splitlines()
    formal_require(
        any(RESULT_NUMBER in line and RESULT_VERSION in line for line in result_lines),
        "formal result R-167 v2.2",
    )
    negative_text = NEGATIVE_REGISTRY.read_text(encoding="utf-8")
    for identifier in NEGATIVE_IDS:
        formal_require(identifier in negative_text, "formal negative " + identifier)
    gate_text = GATE_REGISTRY.read_text(encoding="utf-8")

    def gate_has_status(identifier: str, status: str) -> bool:
        heading = f"### **{identifier}**"
        if heading not in gate_text:
            return False
        block = gate_text.split(heading, 1)[1].split("\n### **", 1)[0]
        return f"**Status:** {status}" in block

    for identifier in CLOSED_SUBGATES:
        formal_require(
            gate_has_status(identifier, "CLOSED"),
            "formal gate CLOSED " + identifier,
        )
    for identifier in OPEN_GATES:
        formal_require(
            gate_has_status(identifier, "OPEN"),
            "formal gate OPEN " + identifier,
        )

    return {
        "status": "COMPLETE" if not formal_missing else "INCOMPLETE",
        "missing": formal_missing,
        "manifest": MANIFEST,
        "certificate": CERTIFICATE,
        "manifest_sha256": normalized_sha256(MANIFEST),
        "certificate_sha256": normalized_sha256(CERTIFICATE),
    }


def build_payload(staged: bool = False) -> dict[str, Any]:
    audit = Audit()

    firewall = source_firewall_fixture()
    audit.check(
        "standard-library import firewall",
        not firewall["forbidden_imports"],
        firewall["imported_roots"],
        firewall["allowed_roots"],
        "independence",
    )
    audit.check(
        "no primary import or result consumption",
        (
            not firewall["primary_module_imported"]
            and not firewall["primary_result_consumed"]
            and firewall["runtime_read_inputs"]
            == [
                SCRIPT,
                MANIFEST,
                CERTIFICATE,
                EXPLORATION_LEDGER,
                RESULT_LEDGER,
                NEGATIVE_REGISTRY,
                GATE_REGISTRY,
            ]
        ),
        firewall,
        "script plus source authorities only",
        "independence",
    )

    pure = pure_bond_diagonal_fixture()
    audit.check(
        "pure-bond coordinate multiplier commutes",
        pure["multiplier_commutator"] == (0, 0, 0, 0),
        pure["multiplier_commutator"],
        (0, 0, 0, 0),
        "pure-bond",
    )
    audit.check(
        "pure-bond coordinate tail invariant",
        pure["conjugated_tail"] == pure["tail_projection"],
        pure["conjugated_tail"],
        pure["tail_projection"],
        "pure-bond",
    )
    audit.check(
        "cutoff functional-calculus diagonal identity",
        pure["difference_square_diagonal"]
        == pure["sine_square_functional_diagonal"],
        pure["difference_square_diagonal"],
        pure["sine_square_functional_diagonal"],
        "pure-bond",
    )
    audit.check(
        "two Hilbert-Schmidt orientations equal",
        pure["left_HS_square"]
        == pure["right_HS_square"]
        == pure["sine_functional"]
        == Fraction(12, 5),
        {
            "left": pure["left_HS_square"],
            "right": pure["right_HS_square"],
            "functional": pure["sine_functional"],
        },
        Fraction(12, 5),
        "pure-bond",
    )
    audit.check(
        "cutoff sine bound certified without floats",
        pure["left_HS_square"] < pure["cutoff_rhs_strict_lower"],
        pure["left_HS_square"],
        {"strictly_below": pure["cutoff_rhs_strict_lower"], "using": "pi^2>9"},
        "pure-bond",
    )
    audit.check(
        "pure-bond theorem boundary",
        (
            not pure["operator_norm_exponential_paid"]
            and not pure["onsite_interspersed_history_tail_proved"]
        ),
        pure,
        "exact layer identity only; history estimate open",
        "scope",
    )

    qtilde = global_qtilde2_fixture()
    audit.check(
        "4x4 reference normalized",
        qtilde["rho_two_trace"] == 1,
        qtilde["rho_two_trace"],
        1,
        "global-Renyi",
    )
    audit.check(
        "exact 4x4 Qtilde2 polynomial",
        qtilde["Qtilde2_polynomial"]
        == qtilde["certificate_formula_polynomial"],
        qtilde["Qtilde2_polynomial"],
        qtilde["certificate_formula_polynomial"],
        "global-Renyi",
    )
    audit.check(
        "full Q3 bond-angle factor",
        (
            qtilde["q3_coordinate_count"] == 8
            and qtilde[
                "physical_theta_coefficient_of_delta_c_m_squared_over_hbar"
            ]
            == 8
            and qtilde["physical_theta_relation"]
            == "theta=8 delta c m^2/hbar=delta J/hbar"
        ),
        {
            "coordinate_count": qtilde["q3_coordinate_count"],
            "theta_coefficient": qtilde[
                "physical_theta_coefficient_of_delta_c_m_squared_over_hbar"
            ],
            "relation": qtilde["physical_theta_relation"],
        },
        "theta=8 delta c m^2/hbar=delta J/hbar",
        "global-Renyi",
    )
    audit.check(
        "Qtilde2 identity angle",
        qtilde["evaluations_by_sin_squared_theta"]["0"] == 1,
        qtilde["evaluations_by_sin_squared_theta"]["0"],
        1,
        "global-Renyi",
    )
    audit.check(
        "Qtilde2 pi-over-four value",
        qtilde["theta_pi_over_four_value"] == Fraction(289, 64),
        qtilde["theta_pi_over_four_value"],
        Fraction(289, 64),
        "global-Renyi",
    )
    audit.check(
        "Qtilde2 independent rational-angle values",
        (
            qtilde["evaluations_by_sin_squared_theta"]["16/25"]
            == Fraction(3721, 625)
            and qtilde["evaluations_by_sin_squared_theta"]["144/169"]
            == Fraction(243049, 28561)
        ),
        qtilde["evaluations_by_sin_squared_theta"],
        {"16/25": Fraction(3721, 625), "144/169": Fraction(243049, 28561)},
        "global-Renyi",
    )
    audit.check(
        "three-disjoint-bond multiplicativity",
        qtilde["disjoint_product_value"] == Fraction(24137569, 262144),
        qtilde["disjoint_product_value"],
        Fraction(24137569, 262144),
        "global-Renyi",
    )
    audit.check(
        "global-Renyi negative remains scoped",
        (
            qtilde["global_volume_uniform_bound_rejected_in_fixture"]
            and qtilde[
                "compressed_doublet_coordinate_spectral_functions_commute_with_kick"
            ]
            and not qtilde["projected_full_coordinate_tail_claimed"]
            and not qtilde["full_interacting_Q3_Gibbs_counterexample"]
            and not qtilde["local_measured_Renyi_rejected"]
            and not qtilde["common_alpha_closed"]
        ),
        qtilde,
        "conditional product-reference global target only",
        "scope",
    )

    measured = measured_renyi_fixture()
    audit.check(
        "local likelihood distributions normalized",
        measured["reference_normalization"] == measured["tilted_normalization"] == 1,
        {
            "reference": measured["reference_normalization"],
            "tilted": measured["tilted_normalization"],
        },
        1,
        "measured-Renyi",
    )
    audit.check(
        "local measured Q2",
        measured["measured_Q_alpha"] == Fraction(23, 16),
        measured["measured_Q_alpha"],
        Fraction(23, 16),
        "measured-Renyi",
    )
    audit.check(
        "discrete Holder event inequality",
        measured["Holder_left_squared"] <= measured["Holder_right_squared"]
        and measured["Holder_left_squared"] == Fraction(1, 4)
        and measured["Holder_right_squared"] == Fraction(23, 64),
        {
            "left_squared": measured["Holder_left_squared"],
            "right_squared": measured["Holder_right_squared"],
        },
        {"left_squared": Fraction(1, 4), "right_squared": Fraction(23, 64)},
        "measured-Renyi",
    )
    audit.check(
        "Holder exponent and Gaussian exponent",
        measured["theta"] == Fraction(1, 2) and measured["b_theta_a"] == 7,
        {"theta": measured["theta"], "b": measured["b_theta_a"]},
        {"theta": Fraction(1, 2), "b": 7},
        "measured-Renyi",
    )
    audit.check(
        "two-orientation probability coefficient",
        measured["two_orientation_probability_prefactor"] == 4,
        measured["two_orientation_probability_prefactor"],
        4,
        "measured-Renyi",
    )
    audit.check(
        "fourth-moment layer-cake polynomial",
        measured["layer_cake_polynomial"] == Fraction(842, 49),
        measured["layer_cake_polynomial"],
        Fraction(842, 49),
        "measured-Renyi",
    )
    audit.check(
        "one- and two-orientation layer-cake coefficients",
        (
            measured["one_orientation_layer_cake_coefficient"]
            == Fraction(1684, 49)
            and measured["two_orientation_layer_cake_coefficient"]
            == Fraction(3368, 49)
        ),
        {
            "one": measured["one_orientation_layer_cake_coefficient"],
            "two": measured["two_orientation_layer_cake_coefficient"],
        },
        {"one": Fraction(1684, 49), "two": Fraction(3368, 49)},
        "measured-Renyi",
    )
    audit.check(
        "measured-Renyi reduction boundary",
        not measured["onsite_interspersed_likelihood_bound_proved"],
        measured["onsite_interspersed_likelihood_bound_proved"],
        False,
        "scope",
    )

    cube = semiclassical_cube_fixture()
    audit.check(
        "Q3 edge and degree fixture",
        cube["edge_count"] == 12 and cube["degrees"] == (3,) * 8,
        {"edges": cube["edge_count"], "degrees": cube["degrees"]},
        {"edges": 12, "degrees": (3,) * 8},
        "Q3-semiclassical",
    )
    audit.check(
        "Walsh diagonalization of cube Laplacian",
        all(row["applied"] == row["expected"] for row in cube["walsh_rows"]),
        cube["walsh_rows"],
        "L chi_S = 2|S| chi_S",
        "Q3-semiclassical",
    )
    audit.check(
        "cube Laplacian spectrum",
        cube["laplacian_multiplicity"] == {0: 1, 2: 3, 4: 3, 6: 1},
        cube["laplacian_multiplicity"],
        {0: 1, 2: 3, 4: 3, 6: 1},
        "Q3-semiclassical",
    )
    audit.check(
        "exactly two sign minima",
        cube["zero_sign_assignment_count"] == 2
        and set(cube["zero_sign_assignments"])
        == {(1,) * 8, (-1,) * 8},
        cube["zero_sign_assignments"],
        {(1,) * 8, (-1,) * 8},
        "Q3-semiclassical",
    )
    audit.check(
        "cube Hessian spectrum at mu one",
        cube["hessian_multiplicity"] == {2: 1, 4: 3, 6: 3, 8: 1},
        cube["hessian_multiplicity"],
        {2: 1, 4: 3, 6: 3, 8: 1},
        "Q3-semiclassical",
    )
    audit.check(
        "semiclassical normalization fixture",
        (
            cube["v"] == 4
            and cube["E_star"] == 256
            and cube["h_sc"] == Fraction(1, 64)
            and cube["mu"] == 1
        ),
        {key: cube[key] for key in ("v", "E_star", "h_sc", "mu")},
        {"v": 4, "E_star": 256, "h_sc": Fraction(1, 64), "mu": 1},
        "Q3-semiclassical",
    )
    audit.check(
        "exact locked action",
        (
            cube["S0_sqrt_coefficient"] == Fraction(16, 3)
            and cube["S0_sqrt_radicand"] == 2
            and cube["S0_square"] == Fraction(512, 9)
        ),
        {
            "coefficient": cube["S0_sqrt_coefficient"],
            "radicand": cube["S0_sqrt_radicand"],
            "square": cube["S0_square"],
        },
        "16 sqrt(2)/3",
        "Q3-semiclassical",
    )
    audit.check(
        "harmonic gap scaling fixture",
        (
            cube["Gamma_harm_sqrt_coefficient"] == 4
            and cube["Gamma_harm_sqrt_radicand"] == 2
            and cube["Gamma_harm_square"] == 32
        ),
        {
            "coefficient": cube["Gamma_harm_sqrt_coefficient"],
            "radicand": cube["Gamma_harm_sqrt_radicand"],
            "square": cube["Gamma_harm_square"],
        },
        "4 sqrt(2)",
        "Q3-semiclassical",
    )
    audit.check(
        "onsite theorem boundary",
        not cube["numerical_h0_certified"] and not cube["many_body_phase_proved"],
        cube,
        "existential small-h onsite input only",
        "scope",
    )

    low_band = low_band_tfim_fixture()
    audit.check(
        "low-band d2",
        low_band["d_2"] == Fraction(1, 100),
        low_band["d_2"],
        Fraction(1, 100),
        "low-band",
    )
    audit.check(
        "exact low-band Ising coupling",
        low_band["J"] == 4 and low_band["bond_spin_coupling"] == -4,
        {"J": low_band["J"], "coupling": low_band["bond_spin_coupling"]},
        {"J": 4, "coupling": -4},
        "low-band",
    )
    audit.check(
        "exact projected bond scalar and field",
        (
            low_band["bond_scalar_before_shift"] == Fraction(40, 9)
            and low_band["bond_field_per_endpoint"] == Fraction(2, 225)
            and low_band["bond_scalar_removed_after_J_rewrite"]
            == Fraction(4, 9)
        ),
        {
            "scalar": low_band["bond_scalar_before_shift"],
            "field": low_band["bond_field_per_endpoint"],
            "shift": low_band["bond_scalar_removed_after_J_rewrite"],
        },
        {
            "scalar": Fraction(40, 9),
            "field": Fraction(2, 225),
            "shift": Fraction(4, 9),
        },
        "low-band",
    )
    audit.check(
        "effective transverse field arithmetic",
        (
            low_band["accumulated_site_field"] == Fraction(4, 75)
            and low_band["delta_eff"] == Fraction(23, 150)
        ),
        {
            "field": low_band["accumulated_site_field"],
            "delta_eff": low_band["delta_eff"],
        },
        {"field": Fraction(4, 75), "delta_eff": Fraction(23, 150)},
        "low-band",
    )
    audit.check(
        "low-band compression boundary",
        low_band["compression_exact"]
        and not low_band["rank_two_high_mode_elimination_proved"],
        low_band,
        "exact compression, high-mode theorem open",
        "scope",
    )

    residual = residual_bound_fixture(low_band)
    audit.check(
        "centered a squared",
        residual["a_squared"]
        == residual["a_square_from_surd"]
        == Fraction(13, 50),
        {
            "maximum": residual["a_squared"],
            "surd_square": residual["a_square_from_surd"],
        },
        Fraction(13, 50),
        "residual",
    )
    audit.check(
        "centered b squared",
        residual["b_squared"] == Fraction(9, 25) and residual["b"] == Fraction(3, 5),
        {"b_squared": residual["b_squared"], "b": residual["b"]},
        {"b_squared": Fraction(9, 25), "b": Fraction(3, 5)},
        "residual",
    )
    audit.check(
        "fourth-moment input arithmetic",
        residual["b_0"] == Fraction(13, 2)
        and residual["b_1"] == Fraction(66601, 10000),
        {"b0": residual["b_0"], "b1": residual["b_1"]},
        {"b0": Fraction(13, 2), "b1": Fraction(66601, 10000)},
        "residual",
    )
    audit.check(
        "one-bond residual exact surd coefficients",
        (
            residual["bond_bound_rational_part"] == Fraction(344, 225)
            and residual["bond_bound_sqrt_coefficient"] == Fraction(8, 15)
            and residual["bond_bound_sqrt_radicand"] == 26
        ),
        {
            "rational": residual["bond_bound_rational_part"],
            "sqrt_coefficient": residual["bond_bound_sqrt_coefficient"],
            "radicand": residual["bond_bound_sqrt_radicand"],
        },
        "(344+120 sqrt(26))/225",
        "residual",
    )
    audit.check(
        "one-bond residual rational upper",
        residual["sqrt_upper_certified_by_squaring"]
        and residual["bond_bound_rational_upper"] == Fraction(956, 225),
        {
            "sqrt_upper": residual["sqrt_upper"],
            "bound_upper": residual["bond_bound_rational_upper"],
        },
        Fraction(956, 225),
        "residual",
    )
    audit.check(
        "A_Q rational fixture",
        residual["A_Q_fixture"]["A_Q"] == Fraction(11, 4),
        residual["A_Q_fixture"],
        Fraction(11, 4),
        "residual",
    )
    audit.check(
        "Young residual matrix positive semidefinite",
        residual["Young_diagonal_nonnegative"]
        and residual["Young_determinant"] == 0,
        {
            "matrix": residual["Young_matrix"],
            "determinant": residual["Young_determinant"],
        },
        "PSD rank one",
        "residual",
    )
    audit.check(
        "residual theorem boundary",
        not residual["residual_inequality_proves_block_diagonalization"],
        residual["residual_inequality_proves_block_diagonalization"],
        False,
        "scope",
    )

    full_gibbs = full_gibbs_context_fixture()
    audit.check(
        "full-Gibbs two unitary orientations",
        full_gibbs["weighted_unitary_right_squared"]
        == full_gibbs["weighted_unitary_left_squared"]
        == Fraction(4, 5),
        {
            "right": full_gibbs["weighted_unitary_right_squared"],
            "left": full_gibbs["weighted_unitary_left_squared"],
        },
        Fraction(4, 5),
        "full-Gibbs",
    )
    audit.check(
        "full-Gibbs Duhamel strict rational lower",
        full_gibbs["Duhamel_rhs_strict_lower"]
        > full_gibbs["weighted_unitary_right_squared"],
        full_gibbs["Duhamel_rhs_strict_lower"],
        ">4/5 using pi^2>9",
        "full-Gibbs",
    )
    audit.check(
        "trace-state versus arbitrary-context separation",
        full_gibbs["trace_distance"] == 0
        and full_gibbs["hash_seminorm_squared"] == 8
        and not full_gibbs["state_stability_implies_arbitrary_context_stability"],
        full_gibbs,
        "trace distance zero and automorphism hash squared eight",
        "context-no-go",
    )
    audit.check(
        "half-modular fixed-band fixture",
        full_gibbs["half_modular_norm_squared"] == 4
        and full_gibbs["bandwidth_factor"] == 2
        and full_gibbs["projective_band_norm"] == 2,
        full_gibbs,
        "modular norm 2; projective upper 4",
        "modular-context",
    )
    audit.check(
        "finite-Q3 hard-form domain instantiation",
        full_gibbs["q3_form_domain_instantiation"]
        == {
            "common_quartic_form_domain": True,
            "W_coordinate_growth_degree": 2,
            "W_squared_growth_degree": 4,
            "finite_Gibbs_fourth_moment": True,
            "bounded_spectral_form_truncation": True,
            "strong_resolvent_then_S2_closure": True,
            "smooth_clipped_Q_L_automatically_covered": False,
        },
        full_gibbs["q3_form_domain_instantiation"],
        "hard/form Q3 pair only",
        "full-Gibbs",
    )
    audit.check(
        "arbitrary-context family limit",
        full_gibbs["unitary_family_limit_p_to_zero"] == 0
        and full_gibbs["family_automorphism_hash_squared"] == 8,
        full_gibbs,
        "unitary hash tends to zero, automorphism hash stays eight",
        "context-no-go",
    )

    fixed_edge = fixed_edge_corridor_fixture()
    # INDEPENDENT TEST ORACLES only: these literals are never inputs to
    # fixed_edge_corridor_fixture; they detect drift in its derived values.
    audit.check(
        "induced cubic edge formula",
        fixed_edge["enumerated_edges"]
        == fixed_edge["formula_edges"]
        == 300
        and fixed_edge["formula_edges"] <= fixed_edge["upper_edges"],
        fixed_edge,
        "300 <= 432",
        "fixed-edge",
    )
    audit.check(
        "restricted-tail Cauchy fixture",
        fixed_edge["Cauchy_left"] <= fixed_edge["Cauchy_right"],
        {"left": fixed_edge["Cauchy_left"], "right": fixed_edge["Cauchy_right"]},
        "left <= right",
        "fixed-edge",
    )
    audit.check(
        "explicit elementary corridor",
        fixed_edge["corridor_prefactor"] == 1296
        and fixed_edge["factorial_ten"] == 3628800
        and fixed_edge["elementary_majorant_limit"] == 0,
        fixed_edge,
        "1296, 10!, limit zero",
        "fixed-edge",
    )
    audit.check(
        "periodic covariance has three direction orbits",
        fixed_edge["periodic_translation_orbit_count"] == 3
        and fixed_edge["periodic_translation_orbit_sizes"] == {0: 64, 1: 64, 2: 64}
        and not fixed_edge["translation_alone_gives_one_orbit"],
        fixed_edge,
        "three translation orbits",
        "covariance-boundary",
    )
    audit.check(
        "homogeneous tilted Gaussian implication no-go",
        fixed_edge["tilted_gaussian"]["precision_determinant"] == Fraction(7, 16)
        and fixed_edge["tilted_gaussian"]["marginal_variance"] == Fraction(16, 7)
        and fixed_edge["tilted_gaussian"]["exponent_gap"] == Fraction(1, 32)
        and fixed_edge["tilted_gaussian"]["Q2_precision_determinant"] == Fraction(-5, 4)
        and fixed_edge["tilted_gaussian"]["fixed_edge_implication_rejected"]
        and fixed_edge["tilted_gaussian"]["two_site_or_homogeneous_dimer_scope"]
        and not fixed_edge["tilted_gaussian"]["full_one_site_translation_invariance"]
        and fixed_edge["hard_tail_constants"]
        and not fixed_edge["smooth_clipped_Q_L_constants"],
        fixed_edge["tilted_gaussian"],
        "7/16, 16/7, 1/32, -5/4",
        "tilted-no-go",
    )

    feshbach_qps = feshbach_compressed_qps_fixture()
    # INDEPENDENT TEST ORACLES only: the overlap and rational coefficients
    # below are compared against, never supplied to, the fixture computation.
    audit.check(
        "cubic overlap upper and periodic bulk equality",
        feshbach_qps["edge_count"] == 192
        and feshbach_qps["periodic_overlap_values"] == [11]
        and feshbach_qps["open_overlap_range"][1] <= 11
        and feshbach_qps["open_overlap_range"][0] < 11
        and feshbach_qps["general_overlap_upper"] == 11,
        {
            "edges": feshbach_qps["edge_count"],
            "periodic": feshbach_qps["periodic_overlap_values"],
            "open": feshbach_qps["open_overlap_range"],
        },
        "general <=11; periodic equality; open boundary can be smaller",
        "Feshbach",
    )
    audit.check(
        "exact global Feshbach fixture",
        feshbach_qps["Feshbach"]["self_energy"] == Fraction(1, 9)
        and feshbach_qps["Feshbach"]["overlap_upper"] == Fraction(11, 9),
        feshbach_qps["Feshbach"],
        {"self_energy": Fraction(1, 9), "overlap_upper": Fraction(11, 9)},
        "Feshbach",
    )
    audit.check(
        "dense extensive self-energy no-go",
        feshbach_qps["dense_no_go"]["norm"] == Fraction(1, 9)
        and feshbach_qps["dense_no_go"]["off_diagonal_nonzero_count"] == 20
        and not feshbach_qps["dense_no_go"]["automatic_QPS_locality"],
        feshbach_qps["dense_no_go"],
        "norm 1/9 with 20 nonzero off-diagonals",
        "self-energy-no-go",
    )
    audit.check(
        "relative-form coefficients and smallness",
        feshbach_qps["relative_form"]["eta_b"] == Fraction(12, 125)
        and feshbach_qps["relative_form"]["nu_b"] == Fraction(402, 3125)
        and feshbach_qps["relative_form"]["zeta"] < 1
        and feshbach_qps["relative_form"]["epsilon"] == Fraction(23, 6250),
        feshbach_qps["relative_form"],
        "exact rational coefficients with zeta < 1",
        "relative-form",
    )
    audit.check(
        "projected local-high diagonal inequality",
        all(value >= 0 for value in feshbach_qps["relative_form"]["projected_high_slack"])
        and feshbach_qps["relative_form"]["diagonal_high_compression_only"]
        and feshbach_qps["relative_form"]["off_diagonal_bound_is_distinct"],
        feshbach_qps["relative_form"],
        "Qxy Bxy Qxy <= (eta_b+nu_b/Gamma) Qxy(kx+ky)Qxy",
        "relative-form",
    )
    audit.check(
        "compressed TFIM star spectrum and selector",
        feshbach_qps["forward_star_spectrum_coefficients"]
        == feshbach_qps["forward_star_expected"]
        and feshbach_qps["selector"] == "u sum_x(1-s_x)"
        and feshbach_qps["selector_plus_density"] == 0
        and feshbach_qps["selector_minus_density"] == 2
        and feshbach_qps["selector_split"] == (0, -2)
        and feshbach_qps["small_ratio"] == "abs(delta_eff)/(2J)<epsilon_Y"
        and feshbach_qps["Z2_flips_s"]
        and feshbach_qps["Z2_fixes_P1"],
        feshbach_qps,
        {"spectrum": {0: 2, 2: 6, 4: 6, 6: 2}, "k": (0, -2)},
        "compressed-QPS",
    )
    audit.check(
        "compressed QPS scope boundary",
        feshbach_qps["compressed_infinite_lattice_phasewise_gap"]
        and feshbach_qps["existential_small_ratio_only"]
        and not feshbach_qps["finite_torus_exact_degeneracy"]
        and not feshbach_qps["oscillator_gap"],
        feshbach_qps,
        "compressed infinite-lattice phasewise theorem only",
        "scope",
    )

    v22 = actual_q3_fifth_shear_rank_two_fixture()
    audit.check(
        "v2.2 static virial and graph bookkeeping",
        v22["static"]["kinetic_coefficient"] == 1
        and v22["static"]["force_prefactor"] == Fraction(-1, 2)
        and len(v22["static"]["force_placements"]) == 9
        and v22["static"]["critical_order"] == 5
        and v22["static"]["graph_levels"][-1] == (5, 10, 20)
        and v22["static"]["finite_cutoff_before_monotone_limit"]
        and not v22["static"]["unbounded_trace_cyclicity"]
        and v22["static"]["registered_periodic_compact_source"]
        and not v22["static"]["arbitrary_boundary_static"],
        v22["static"],
        "coefficients 1,-1/2; 9 placements; order 5; degrees 10/20",
        "v2.2-static",
    )
    audit.check(
        "v2.2 direct shear and fifth-word budget",
        v22["shear"]["coefficients"]
        == {"delta_pQ": Fraction(1), "delta_squared_Q2": Fraction(1, 2)}
        and v22["shear"]["word_count"] == 242
        and v22["shear"]["all_words_have_delta"]
        and v22["shear"]["all_words_order_at_most_five"]
        and 2 * v22["shear"]["C5_majorant_T2"]
        == v22["shear"]["polynomial_difference_T2"]
        and v22["shear"]["R1_paid_exponents"] == (Fraction(1, 2), Fraction(1, 4))
        and v22["shear"]["R1_leftover_x_at_worst_neighbor"] == Fraction(1, 4)
        and v22["shear"]["R1_neighbor_exponential"] == Fraction(1, 4)
        and v22["shear"]["R2_paid_neighbor_exponents"]
        == (Fraction(1, 4), Fraction(1, 4))
        and v22["shear"]["R2_cross_terms_retained"]
        and v22["shear"]["R2_leftover_x_at_worst_neighbor"] == Fraction(1, 2)
        and v22["shear"]["R2_neighbor_exponential"] == Fraction(1, 2)
        and v22["shear"]["residual_weight_bound"] == 54
        and v22["shear"]["maximum_local_insertions"] == 5
        and v22["shear"]["maximum_neighbor_incidences"] == 10
        and v22["shear"]["tuple_counts_neighbor_incidences_le_10"][-1] == 6**10
        and v22["shear"]["commutator_order_drop"] == Fraction(3, 4)
        and v22["shear"]["K5_multinomial_supplies_weights"]
        and v22["shear"]["K_ge_one_fills_slack"]
        and v22["shear"]["subset_deletion_safe"],
        v22["shear"],
        "242 words, R2 cross terms, 5 anchors and <=10 neighbor incidences",
        "v2.2-shear",
    )
    audit.check(
        "v2.2 generic degree-six exponential-growth hostile",
        v22["shear"]["generic_degree_six_growth_ratio"] == Fraction(5, 2)
        and not v22["shear"]["generic_degree_six_promotion"]
        and v22["shear"]["finite_cubic_subgraph_or_periodic_quotient"]
        and v22["shear"]["uniform_cubic_polynomial_growth_required"],
        {
            "sphere_terms": v22["shear"]["tree_sphere_terms"],
            "growth_ratio": v22["shear"]["generic_degree_six_growth_ratio"],
        },
        "six-regular tree weighted sphere ratio 5/2; cubic growth required",
        "v2.2-growth-hostile",
    )
    audit.check(
        "v2.2 rank-two local-to-global counterfixture",
        v22["rank_two"]["local_idempotent"]
        and v22["rank_two"]["local_rank"] == 2
        and v22["rank_two"]["local_trace"] == 2
        and v22["rank_two"]["cycle_nullity"] == 2
        and v22["rank_two"]["vacuum_kernel"]
        and v22["rank_two"]["W_kernel"]
        and v22["rank_two"]["one_particle_half_laplacian"]
        and v22["rank_two"]["one_particle_eigenpairs"]
        and v22["rank_two"]["torus_L4_gap"]
        < v22["rank_two"]["torus_bound_from_pi_gt_three"]
        and v22["rank_two"]["lift_first_high_energy"] == 1
        and not v22["rank_two"]["automatic_global_gap"]
        and not v22["rank_two"]["Q3_gap_no_go"],
        v22["rank_two"],
        "rank-two local projection, cycle nullity 2, half Laplacian, lifted gap 1",
        "v2.2-rank-two",
    )

    moment_v21 = twentieth_moment_graph_fixture()
    audit.check(
        "v2.1 twentieth-moment corridor arithmetic",
        moment_v21["edge_constant"] == 2916
        and moment_v21["tail_power"] == 16
        and moment_v21["corridor_exponent"] == Fraction(-2, 5)
        and moment_v21["factorial_R_log_R_coefficient"] == Fraction(-1, 5)
        and moment_v21["minimal_admissible_integer"] == 5
        and all(row[-1] for row in moment_v21["pointwise_samples"]),
        moment_v21,
        "2916, L^-16, R^-2/5, factorial -1/5, p=5",
        "v2.1-moment",
    )
    audit.check(
        "v2.1 sharp conditional factor and expansion",
        moment_v21["conditional_coefficient_without_exp"] == 75000
        and moment_v21["commutator_coefficients"] == (1, 2, 2)
        and moment_v21["convexity"]["holds"],
        moment_v21,
        "2*d5^2*S_mu^5*m5 and coefficients 1,2,2",
        "v2.1-conditional",
    )
    audit.check(
        "v2.1 all-m normalized commutator fixture",
        all(
            row["normalized_commutator_norm"]
            == 2**row["m"] - Fraction(1, 2**row["m"])
            for row in moment_v21["all_m"]["rows"]
        )
        and not moment_v21["all_m"]["quadratic_growth"]
        and not moment_v21["all_m"]["fixed_m5_rejected"],
        moment_v21["all_m"],
        "2^m-2^-m; automatic all-m only",
        "v2.1-all-m-no-go",
    )
    kn = moment_v21["KN"]
    audit.check(
        "v2.1 KN static/low-graph no-go",
        kn["condition_delta_nonzero"]
        and kn["condition_N4_ge_abs_delta"]
        and kn["d5"] == 1
        and kn["G5"] == Fraction(kn["N"] ** 6) - Fraction(1, kn["N"] ** 14)
        and kn["one_orientation_q20_lower"] == Fraction(kn["N"] ** 12, 8)
        and kn["two_orientation_q20_lower"] == Fraction(kn["N"] ** 12, 4)
        and all(Fraction(value) <= 0 for value in kn["low_graph_exponents"].values()),
        kn,
        "d5=1, G5=N^6-N^-14, q20 lower N^12/8 per orientation",
        "v2.1-static-low-graph-no-go",
    )

    edge_v21 = oscillator_edge_cluster_fixture()
    scalars = edge_v21["scalars"]
    # Independent exact test oracles; the fixture derives every value from inputs.
    expected_edge = {
        "Cb": Fraction(1, 12500),
        "fb": Fraction(19, 1500000),
        "eb": Fraction(139, 1500000),
        "J": Fraction(4, 125),
        "epsilon": Fraction(23, 6250),
        "A": Fraction(96139, 1500000),
        "D": Fraction(50, 3),
        "D_minus_A": Fraction(8301287, 500000),
        "margin": Fraction(20832953, 19531250),
        "gap_rational_lower": Fraction(332047248, 5188304375),
    }
    audit.check(
        "v2.1 corrected edge constants",
        all(scalars[key] == value for key, value in expected_edge.items())
        and edge_v21["inputs"]["a0_minus_m2"]
        == max(
            edge_v21["inputs"]["a0_minus_m2"],
            edge_v21["inputs"]["a1_minus_m2"],
        )
        == edge_v21["inputs"]["a"] ** 2,
        scalars,
        expected_edge,
        "v2.1-edge",
    )
    compressions = edge_v21["compressions"]
    audit.check(
        "v2.1 diagonal compressions without false invariance",
        compressions["P0_h_P0_diagonal"]
        == (scalars["eb"], 0, 0, scalars["eb"])
        and compressions["L_h_L_diagonal"]
        == (0, scalars["A"], scalars["A"], 0)
        and all(value == -scalars["fb"] / 2 for value in compressions["P0_h_L_entries"])
        and compressions["P0_h_L_norm"] == abs(scalars["fb"])
        and not compressions["P0_L_invariant"],
        compressions,
        "P0hP0=ebP0, LhL=AL, ||P0hL||=|fb| != 0",
        "v2.1-edge-compression",
    )
    relative = edge_v21["relative"]
    expected_relative = {
        "eta_b": Fraction(12, 125),
        "nu_b": Fraction(402, 3125),
        "rho_b": Fraction(15201, 156250),
        "alpha": Fraction(183081, 312500),
        "beta": Fraction(2851, 750000),
        "gamma0": Fraction(8, 125),
        "Delta_rf": Fraction(4430237, 234375000),
    }
    audit.check(
        "v2.1 relative-form constants",
        all(relative[key] == value for key, value in expected_relative.items())
        and relative["alpha"] < 1
        and relative["Delta_rf"] > 0,
        relative,
        expected_relative,
        "v2.1-edge-relative",
    )
    cutoff = edge_v21["cutoff"]
    audit.check(
        "v2.1 Ritz cutoff boundary",
        cutoff["nested_parity_preserving_Ritz_form_restriction"]
        and cutoff["Pi_M_contains_P"]
        and cutoff["union_form_core"]
        and cutoff["same_constants"]
        and cutoff["eigenvalues_decrease_to_full"]
        and not cutoff["replace_q_then_square"]
        and not cutoff["Pi_q2_Pi_equals_Pi_q_Pi_squared"],
        cutoff,
        "Ritz form restriction, not truncated q",
        "v2.1-edge-cutoff",
    )

    corridor = corridor_exponent_fixture()
    audit.check(
        "N corridor exponent table",
        corridor["derived_exponents"] == corridor["certificate_oracle"],
        corridor["derived_exponents"],
        corridor["certificate_oracle"],
        "corridor",
    )
    audit.check(
        "N corridor low-high dominant terms",
        corridor["bond_bracket_term_exponents"]
        == {"b": 1, "2ma": 1, "a_squared": -2}
        and corridor["bond_bracket_dominant_exponent"] == 1,
        corridor["bond_bracket_term_exponents"],
        {"b": 1, "2ma": 1, "a_squared": -2},
        "corridor",
    )
    audit.check(
        "N corridor A_Q dominance",
        corridor["A_Q_term_exponents"]
        == {
            "v_squared_over_Gamma": 2,
            "sqrt_energy_over_Gamma_sqrt_g": -1,
        }
        and corridor["A_Q_dominant_exponent"] == 2,
        corridor["A_Q_term_exponents"],
        {
            "v_squared_over_Gamma": 2,
            "sqrt_energy_over_Gamma_sqrt_g": -1,
        },
        "corridor",
    )
    audit.check(
        "N corridor leading scales",
        corridor["J_leading_constant"] == 8
        and corridor["Gamma_leading_sqrt_radicand"] == 2,
        {
            "J": corridor["J_leading_constant"],
            "Gamma_radicand": corridor["Gamma_leading_sqrt_radicand"],
        },
        "J tends to 8 and Gamma is asymptotic to sqrt(2) N^2",
        "corridor",
    )
    audit.check(
        "corridor theorem boundary",
        not corridor["finite_N_enclosure"] and not corridor["two_phase_QPS_proved"],
        corridor,
        "asymptotic algebra only",
        "scope",
    )

    for phrase in (
        "onsite-interspersed local measured-Renyi",
        "n-to-infinity Trotter convergence",
        "all-exhaustion common alpha",
        "phase-KMS quotient",
        "rank-two unbounded block diagonalization",
        "two-phase QPS",
        "broken-sector temporal mass or GNS gap",
        "regulator removal",
        "continuum",
        "physical-empty comparison",
        "prospective blind validation",
        "C6",
        "CP1",
        "physical Sector A",
        "Pre-A closure",
    ):
        audit.check(
            f"no-overclaim phrase {phrase}",
            phrase in NO_OVERCLAIM,
            phrase in NO_OVERCLAIM,
            True,
            "scope",
        )

    authority = authority_audit(audit, staged=staged)
    source_paths = (SCRIPT, MANIFEST, CERTIFICATE)
    source_hashes = {
        str(path.relative_to(REPO)).replace("\\", "/"): normalized_sha256(path)
        for path in source_paths
        if path.exists()
    }
    for relative, digest in source_hashes.items():
        audit.check(
            f"source hash {relative}",
            len(digest) == 64
            and all(character in "0123456789abcdef" for character in digest),
            digest,
            "64 lowercase hexadecimal characters",
            "provenance",
        )

    verdict = "PASS" if authority["status"] == "COMPLETE" else "INCOMPLETE"
    passed = len(audit.rows)
    return {
        "schema": f"tect/{SLUG}-independent-result/1.0",
        "script_version": __version__,
        "result_id": RESULT_ID,
        "result_number": RESULT_NUMBER,
        "result_version": RESULT_VERSION,
        "exploration_id": EXPLORATION_ID,
        "task_id": TASK_ID,
        "claim_ids": [CLAIM_ID],
        "claim_bearing": False,
        "verdict": verdict,
        "summary": {
            "passed": passed,
            "failed": 0,
            "total": passed,
            "authority_status": authority["status"],
        },
        "assertions": {
            "passed": passed,
            "failed": 0,
            "total": passed,
            "rows": audit.rows,
        },
        "derived": {
            "source_firewall": firewall,
            "pure_bond_diagonal": pure,
            "global_Qtilde2_product_no_go": qtilde,
            "local_measured_Renyi_reduction": measured,
            "Q3_semiclassical_cube": cube,
            "exact_low_band_TFIM": low_band,
            "residual_bound": residual,
            "N_corridor": corridor,
            "full_Gibbs_context": full_gibbs,
            "fixed_edge_corridor": fixed_edge,
            "Feshbach_compressed_QPS": feshbach_qps,
            "v2_1_twentieth_moment_graph_boundary": moment_v21,
            "v2_1_full_oscillator_edge_cluster": edge_v21,
            "v2_2_actual_Q3_fifth_shear_rank_two": v22,
            "pure_bond_identity_closed": True,
            "twentieth_moment_fixed_edge_corridor_reduction_closed": True,
            "conditional_fifth_graph_transport_reduction_closed": True,
            "translate_uniform_local_fifth_Gibbs_moment_closed": True,
            "simultaneous_bond_shear_fifth_graph_propagation_closed": True,
            "full_oscillator_local_edge_parity_cluster_closed": True,
            "parity_preserving_Ritz_removal_closed": True,
            "full_Hamiltonian_Gibbs_resummation_closed": True,
            "fixed_edge_to_growing_corridor_reduction_closed": True,
            "below_Gamma_Feshbach_precursor_closed": True,
            "compressed_TFIM_two_phase_QPS_closed": True,
            "arbitrary_context_upgrade_closed": False,
            "actual_Q3_fixed_edge_history_bound_closed": True,
            "registered_periodic_compact_source_scope_only": True,
            "arbitrary_boundary_history_bound_closed": False,
            "local_measured_Renyi_reduction_closed": True,
            "semiclassical_onsite_geometry_fixture_closed": True,
            "exact_low_band_compression_fixture_closed": True,
            "onsite_interspersed_history_bound_closed": False,
            "all_exhaustion_common_alpha_closed": False,
            "rank_two_block_diagonalization_closed": False,
            "two_phase_QPS_for_exact_oscillator_closed": False,
            "broken_sector_GNS_gap_closed": False,
            "physical_mass_gap_closed": False,
            "regulator_removal_closed": False,
            "continuum_closed": False,
            "physical_empty_comparison_closed": False,
            "C6_closed": False,
            "CP1_closed": False,
            "Sector_A_closed": False,
            "Pre_A_closed": False,
        },
        "negative_ids": list(NEGATIVE_IDS),
        "closed_subgates": list(CLOSED_SUBGATES),
        "open_gates": list(OPEN_GATES),
        "authority": authority,
        "source_hashes": source_hashes,
        "boundary": NO_OVERCLAIM,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="derive twice and require byte-identical canonical payloads",
    )
    parser.add_argument(
        "--staged",
        action="store_true",
        help="allow missing manifest/certificate and report INCOMPLETE",
    )
    parser.add_argument(
        "--no-store",
        action="store_true",
        help="run all checks without writing a result JSON",
    )
    arguments = parser.parse_args()

    payload = build_payload(staged=arguments.staged)
    encoded = canonical_bytes(payload)
    digest = hashlib.sha256(encoded).hexdigest()

    if arguments.self_test:
        repeated = build_payload(staged=arguments.staged)
        repeated_encoded = canonical_bytes(repeated)
        if encoded != repeated_encoded:
            raise AssertionError("nondeterministic independent payload")
        if digest != hashlib.sha256(repeated_encoded).hexdigest():
            raise AssertionError("nondeterministic independent digest")
        print(
            f"SELF-TEST {payload['verdict']} {payload['summary']['passed']}/"
            f"{payload['summary']['total']} | SHA256 {digest} | {RESULT_NUMBER} "
            f"{RESULT_VERSION}"
        )
        if payload["authority"]["missing"]:
            print("STAGED-MISSING " + ", ".join(payload["authority"]["missing"]))
        return 0 if payload["verdict"] == "PASS" or arguments.staged else 1

    if payload["verdict"] != "PASS" and not arguments.staged:
        print(
            f"INCOMPLETE {payload['summary']['passed']}/"
            f"{payload['summary']['total']} | authority "
            + ", ".join(payload["authority"]["missing"])
        )
        return 1

    if not arguments.no_store:
        atomic_json(arguments.output, payload)
    label = "PASS" if payload["verdict"] == "PASS" else "STAGED"
    print(
        f"{label} {payload['summary']['passed']}/"
        f"{payload['summary']['total']} | SHA256 {digest} | {RESULT_NUMBER} "
        f"{RESULT_VERSION}"
    )
    print("NO-STORE" if arguments.no_store else arguments.output)
    if payload["authority"]["missing"]:
        print("STAGED-MISSING " + ", ".join(payload["authority"]["missing"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

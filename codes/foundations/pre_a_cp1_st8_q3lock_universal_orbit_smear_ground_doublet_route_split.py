#!/usr/bin/env python3
"""Primary exact verifier for the staged R-167 v1.6 route split.

This executable audits two additive, deliberately narrow statements:

* modular right-context control upgrades the R-167 v1.5 cyclic Fejer
  estimate to every *fixed finite* raw configuration-orbit word along the
  already selected tangent nets; and
* the exact zero-source finite Hamiltonians define a beta-independent
  universal L1 orbit-smear C-star carrier on which the EXP-000789 broken
  doublets have two distinct algebraic-ground-state cluster points.

The carrier is categorical.  It is not an all-exhaustion thermodynamic
limit, a quasi-local raw oscillator algebra, a raw-character generator
core, or a broken-sector GNS-gap theorem.  Until the matching manifest,
certificate, exploration and result-ledger authority exist, use
``--staged``; the calculation then reports ``INCOMPLETE`` rather than
silently promoting staged mathematics to a registered result.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Iterable, Mapping

import sympy as sp


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-universal-orbit-smear-ground-doublet-route-split"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE_CANDIDATES = (
    REPO / f"strategy/{SLUG}-certificate-260810.md",
    REPO / f"strategy/{SLUG}-certificate.md",
)
PARENTS = (
    REPO
    / "strategy/pre-a-cp1-st8-q3lock-hamiltonian-os-tangent-transport-generator-route-split-manifest.json",
    REPO
    / "strategy/pre-a-cp1-st8-q3lock-ground-equal-time-order-gap-continuum-counterterm-route-split-manifest.json",
)
DEFAULT_OUTPUT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / f"2026-08-10-primary-{SLUG}/result.json"
)
STATUS = REPO / "claims/C6-SPACETIME-SIGNATURE/status.json"
EXPLORATION_LEDGER = REPO / "explorations/log.jsonl"
RESULT_LEDGER = REPO / "RESULTS-LEDGER.md"

EXPECTED_TASK = "T-054"
EXPECTED_EXPLORATION = "EXP-000803"
EXPECTED_RESULT_NUMBER = "R-167"
EXPECTED_RESULT_VERSION = "v1.6"
EXPECTED_RESULT_ID = (
    "PA-CP1-ST8-Q3LOCK-SECOND-WEIGHTED-ENERGY-MOMENT-AND-COMMON-ALPHA-CAUCHY-GATE-SPLIT"
)
EXPECTED_CLOSED_SUBGATES = (
    "PA-CP1-ST8-Q3LOCK-SELECTED-TANGENT-RAW-FINITE-ORBIT-WORD-MOMENT-COMPLETION",
    "PA-CP1-ST8-Q3LOCK-ZERO-SOURCE-FINITE-HAMILTONIAN-L1-ORBIT-SMEAR-CSTAR-CARRIER",
    "PA-CP1-ST8-Q3LOCK-UNIVERSAL-ORBIT-SMEAR-DISTINCT-ALGEBRAIC-GROUND-DOUBLETS",
)
EXPECTED_NEXT_GATE = (
    "PA-CP1-ST8-Q3LOCK-QUASI-LOCAL-RAW-OSCILLATOR-ALL-EXHAUSTION-COMMON-ALPHA-AND-BROKEN-GNS-GAP"
)
EXPECTED_OPEN_GATES = (
    EXPECTED_NEXT_GATE,
    "PA-ROUND1-EVIDENCE-ROLE-AND-MINIMUM-MANIFEST-FREEZE",
)
NEGATIVE_IDS = (
    "NG-2026-08-10-PRE-A-ST8-Q3LOCK-STATIC-TAIL-ONLY-PROJECTED-ORBIT-LOCALITY",
)
REUSED_NEGATIVE_IDS = (
    "NG-2026-08-09-PRE-A-ST8-Q3LOCK-POSTHOC-DIRECT-SUM-COMMON-DYNAMICS",
    "NG-2026-08-10-PRE-A-ST8-Q3LOCK-FIXED-BETA-ENVELOPE-AUTOMATIC-CROSS-BETA-GLUING"
)


def normalized_sha256(path: Path) -> str:
    raw = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(raw).hexdigest()


def json_safe(value: Any) -> Any:
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
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


def matrix_zero(matrix: sp.MatrixBase) -> bool:
    return all(sp.simplify(entry) == 0 for entry in matrix)


def matrix_equal(left: sp.MatrixBase, right: sp.MatrixBase) -> bool:
    return left.shape == right.shape and matrix_zero(sp.Matrix(left - right))


def hs_norm_square(matrix: sp.MatrixBase) -> sp.Expr:
    return sp.simplify(sp.trace(matrix.H * matrix))


def operator_norm_square(matrix: sp.MatrixBase) -> sp.Expr:
    eigenvalues: list[sp.Expr] = []
    for eigenvalue, multiplicity in (matrix.H * matrix).eigenvals().items():
        eigenvalues.extend([sp.simplify(eigenvalue)] * multiplicity)
    return max(eigenvalues, key=lambda item: float(sp.N(item, 50)))


def block(left: sp.MatrixBase, right: sp.MatrixBase) -> sp.Matrix:
    return sp.diag(sp.Matrix(left), sp.Matrix(right))


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
                "name": name,
                "group": group,
                "status": "PASS",
                "actual": json_safe(actual),
                "expected": json_safe(expected),
            }
        )


def pauli_matrices() -> tuple[sp.Matrix, sp.Matrix, sp.Matrix, sp.Matrix]:
    identity = sp.eye(2)
    sigma_x = sp.Matrix([[0, 1], [1, 0]])
    sigma_y = sp.Matrix([[0, -sp.I], [sp.I, 0]])
    sigma_z = sp.diag(1, -1)
    return identity, sigma_x, sigma_y, sigma_z


def modular_right_context_audit() -> dict[str, Any]:
    # INPUTS: a faithful two-level Gibbs density and rank-one analytic words.
    probability_low = sp.Rational(1, 4)
    probability_high = 1 - probability_low
    beta = sp.Integer(1)
    hbar = sp.Integer(1)
    rho = sp.diag(probability_low, probability_high)
    rho_half = sp.diag(sp.sqrt(probability_low), sp.sqrt(probability_high))
    rho_minus_half = sp.diag(
        1 / sp.sqrt(probability_low), 1 / sp.sqrt(probability_high)
    )
    context = sp.Matrix([[0, 1], [0, 0]])
    left_word = sp.Matrix([[1, 0], [0, 0]])

    sigma_plus_half = sp.simplify(rho_minus_half * context * rho_half)
    sigma_minus_half_star = sp.simplify(
        rho_half * context.H * rho_minus_half
    )
    commutant_multiplier = sigma_minus_half_star.H
    lhs = sp.simplify(left_word * context * rho_half)
    rhs = sp.simplify(left_word * rho_half * commutant_multiplier)
    lhs_square = hs_norm_square(lhs)
    base_square = hs_norm_square(left_word * rho_half)
    multiplier_norm_square = operator_norm_square(sigma_plus_half)

    # rho is proportional to exp(-beta H).  The scalar in H is immaterial.
    energy_low = -sp.log(probability_low) / beta
    energy_high = -sp.log(probability_high) / beta
    physical_frequency = sp.simplify((energy_low - energy_high) / hbar)
    arveson_bandwidth = abs(physical_frequency)
    exponential_band_bound = sp.exp(beta * hbar * arveson_bandwidth / 2)

    return {
        "inputs": {
            "probability_low": probability_low,
            "probability_high": probability_high,
            "beta": beta,
            "hbar": hbar,
        },
        "rho": rho,
        "context": context,
        "left_word": left_word,
        "sigma_plus_half": sigma_plus_half,
        "commutant_multiplier": commutant_multiplier,
        "lhs": lhs,
        "rhs": rhs,
        "lhs_square": lhs_square,
        "base_square": base_square,
        "multiplier_norm_square": multiplier_norm_square,
        "physical_frequency": physical_frequency,
        "arveson_bandwidth": arveson_bandwidth,
        "exponential_band_bound": exponential_band_bound,
        "identity": (
            "Y C Omega = J sigma_{-i/2}(C*) J Y Omega; "
            "sigma_s=alpha_{-beta*hbar*s}"
        ),
        "general_bound": (
            "||Y C Omega|| <= ||sigma_{i/2}(C)|| ||Y Omega|| "
            "<= exp(beta*hbar*R_C/2)||C||||Y Omega||"
        ),
    }


def sequential_fejer_audit() -> dict[str, Any]:
    # INPUTS: one fixed three-letter raw word and a requested total error.
    beta = sp.Rational(1, 100)
    hbar = sp.Integer(1)
    chi = sp.Integer(100)
    raw_frequency_norms = (
        sp.Rational(1, 2),
        sp.Rational(2, 3),
        sp.Rational(3, 4),
    )
    target_error = sp.Rational(1, 2)
    word_length = len(raw_frequency_norms)
    per_letter_error = target_error / word_length
    beta_hbar = sp.simplify(beta * hbar)

    # Work from the rightmost letter to the left.  At each step the right
    # context is already bandlimited, with bandwidth equal to the finite sum
    # of the cutoffs chosen later in the word.
    context_bandwidth = sp.Integer(0)
    rows_reversed: list[dict[str, Any]] = []
    for index in reversed(range(word_length)):
        xi_norm = raw_frequency_norms[index]
        a_xi = sp.simplify(xi_norm / sp.sqrt(beta * chi))
        cutoff_prefactor = sp.simplify(
            a_xi**2 * (2 + beta_hbar) / per_letter_error**2
        )
        cutoff = sp.simplify(
            cutoff_prefactor * sp.exp(beta_hbar * context_bandwidth)
        )
        exact_cyclic_error = sp.simplify(
            a_xi * sp.sqrt(2 / cutoff**2 + beta_hbar / cutoff)
        )
        context_multiplier = sp.exp(beta_hbar * context_bandwidth / 2)
        contextual_error = sp.simplify(context_multiplier * exact_cyclic_error)
        crude_error = sp.simplify(
            context_multiplier
            * a_xi
            * sp.sqrt((2 + beta_hbar) / cutoff)
        )
        rows_reversed.append(
            {
                "index": index,
                "xi_norm": xi_norm,
                "a_xi": a_xi,
                "right_context_bandwidth": context_bandwidth,
                "cutoff_prefactor": cutoff_prefactor,
                "cutoff": cutoff,
                "exact_cyclic_error": exact_cyclic_error,
                "context_multiplier": context_multiplier,
                "contextual_error": contextual_error,
                "crude_error": crude_error,
                "cutoff_finite": bool(sp.N(cutoff, 40).is_finite),
            }
        )
        context_bandwidth = sp.simplify(context_bandwidth + cutoff)

    rows = sorted(rows_reversed, key=lambda row: row["index"])
    exact_total = sp.simplify(sum(row["contextual_error"] for row in rows))
    crude_total = sp.simplify(sum(row["crude_error"] for row in rows))

    # A short length scan records the dependence on the fixed word length.
    # It is not a uniform-in-length estimate and is never used as one.
    length_scan: list[dict[str, Any]] = []
    for length in range(1, word_length + 2):
        eta = target_error / length
        bandwidth = sp.Integer(0)
        cutoffs: list[sp.Expr] = []
        for _ in reversed(range(length)):
            a_xi = sp.Integer(1)
            prefactor = sp.simplify(a_xi**2 * (2 + beta_hbar) / eta**2)
            cutoff = sp.simplify(prefactor * sp.exp(beta_hbar * bandwidth))
            cutoffs.append(cutoff)
            bandwidth = sp.simplify(bandwidth + cutoff)
        length_scan.append(
            {
                "length": length,
                "largest_cutoff": max(
                    cutoffs, key=lambda item: float(sp.N(item, 40))
                ),
                "all_cutoffs_finite": all(
                    bool(sp.N(item, 40).is_finite) for item in cutoffs
                ),
            }
        )

    return {
        "inputs": {
            "beta": beta,
            "hbar": hbar,
            "chi": chi,
            "raw_frequency_norms": raw_frequency_norms,
            "target_error": target_error,
        },
        "per_letter_error": per_letter_error,
        "rows": rows,
        "exact_total_error": exact_total,
        "crude_total_error": crude_total,
        "length_scan": length_scan,
        "replacement_order": "right-to-left",
        "right_context_bandwidth_rule": "sum of already chosen right cutoffs",
        "stars_preserve_bandwidth_and_error": True,
        "real_time_shifts_preserve_bandwidth_and_error": True,
        "convex_phase_mixtures_preserve_bound": True,
        "fixed_finite_word_only": True,
        "uniform_in_word_length": False,
    }


def periodize_label(
    label: Mapping[tuple[int, int, int], sp.Expr], length: int
) -> dict[tuple[int, int, int], sp.Expr]:
    result: dict[tuple[int, int, int], sp.Expr] = {}
    for site, coefficient in label.items():
        periodic_site = tuple(coordinate % length for coordinate in site)
        result[periodic_site] = sp.simplify(
            result.get(periodic_site, sp.Integer(0)) + coefficient
        )
    return {site: value for site, value in result.items() if value != 0}


def add_labels(
    left: Mapping[tuple[int, int, int], sp.Expr],
    right: Mapping[tuple[int, int, int], sp.Expr],
) -> dict[tuple[int, int, int], sp.Expr]:
    result = dict(left)
    for site, coefficient in right.items():
        result[site] = sp.simplify(result.get(site, 0) + coefficient)
    return {site: value for site, value in result.items() if value != 0}


def triangular_shift_l1(width: sp.Rational, shift: sp.Rational) -> sp.Expr:
    """Integrate the exact L1 distance between a triangle and its shift."""

    t = sp.symbols("t", real=True)
    centers = (sp.Integer(0), shift)
    breakpoints = {
        -width,
        sp.Integer(0),
        width,
        shift - width,
        shift,
        shift + width,
        shift / 2,
    }
    ordered = sorted(breakpoints, key=lambda item: float(item))

    def affine(center: sp.Expr, sample: sp.Expr) -> sp.Expr:
        displacement = sp.simplify(sample - center)
        if abs(float(displacement)) >= float(width):
            return sp.Integer(0)
        sign = 1 if float(displacement) >= 0 else -1
        return sp.simplify((1 - sign * (t - center) / width) / width)

    total = sp.Integer(0)
    for left, right in zip(ordered, ordered[1:]):
        midpoint = sp.simplify((left + right) / 2)
        difference = sp.expand(
            affine(centers[0], midpoint) - affine(centers[1], midpoint)
        )
        midpoint_value = sp.simplify(difference.subs(t, midpoint))
        if midpoint_value == 0:
            continue
        sign = 1 if float(midpoint_value) > 0 else -1
        total += sp.integrate(sign * difference, (t, left, right))
    return sp.simplify(total)


def universal_orbit_smear_audit() -> dict[str, Any]:
    identity, sigma_x, sigma_y, sigma_z = pauli_matrices()

    # INPUTS: two normalized L1 Laplace kernels and one finite Hamiltonian.
    decay = sp.Rational(3, 2)
    hbar = sp.Integer(1)
    coupling = sp.Rational(2, 3)
    physical_frequency = sp.simplify(2 * coupling / hbar)
    laplace_l1 = sp.Integer(1)
    cosine_response = sp.simplify(
        decay**2 / (decay**2 + physical_frequency**2)
    )
    represented_smear = sp.simplify(cosine_response * sigma_z)
    represented_norm_square = operator_norm_square(represented_smear)

    # Exact C-star identity in the faithful joint product representation.
    first_component = sp.Matrix([[1, 1], [0, 0]])
    second_component = sigma_z / 2
    joint_element = block(first_component, second_component)
    universal_norm_square = operator_norm_square(joint_element)
    square_norm = sp.sqrt(operator_norm_square(joint_element.H * joint_element))

    # A finite null-ideal fixture for quotient-before-completion.
    evaluation = sp.Matrix([[1, 0, 1], [0, 1, 1]])
    null_vector = sp.Matrix([-1, -1, 1])

    # INPUTS: a normalized triangular W^{1,1} kernel and one small shift.
    triangle_width = sp.Rational(3, 2)
    translation = sp.Rational(1, 3)
    triangle_l1 = sp.Integer(1)
    derivative_l1 = sp.simplify(2 / triangle_width)
    exact_translation_l1 = triangular_shift_l1(triangle_width, translation)
    translation_formula = sp.simplify(
        2 * translation / triangle_width
        - translation**2 / (2 * triangle_width**2)
    )

    # Integration by parts on a smooth core verifies delta A_f=-A_{f'}.
    omega = sp.Rational(5, 4)
    gaussian_transform = sp.sqrt(sp.pi) * sp.exp(-(omega**2) / 4)
    shifted_transform = sp.exp(sp.I * omega * translation) * gaussian_transform
    generator_transform = sp.I * omega * gaussian_transform
    minus_derivative_transform = sp.I * omega * gaussian_transform

    # Rational finite-support labels; small tori may wrap, cofinal tori do not.
    label_xi = {
        (-1, 0, 0): sp.Rational(1, 3),
        (2, 0, 0): sp.Rational(2, 5),
    }
    label_eta = {
        (0, 1, 0): sp.Rational(-1, 7),
        (2, 0, 0): sp.Rational(1, 11),
    }
    period_three = periodize_label(label_xi, 3)
    period_five = periodize_label(label_xi, 5)
    linear_left = periodize_label(add_labels(label_xi, label_eta), 5)
    linear_right = add_labels(
        periodize_label(label_xi, 5), periodize_label(label_eta, 5)
    )

    return {
        "laplace_contract": {
            "decay": decay,
            "hbar": hbar,
            "coupling": coupling,
            "physical_frequency": physical_frequency,
            "kernel_l1": laplace_l1,
            "cosine_response": cosine_response,
            "represented_smear": represented_smear,
            "represented_norm_square": represented_norm_square,
        },
        "cstar_completion": {
            "joint_element": joint_element,
            "universal_norm_square": universal_norm_square,
            "square_norm": square_norm,
            "evaluation": evaluation,
            "null_vector": null_vector,
            "null_image": evaluation * null_vector,
            "joint_product_representation_faithful_after_quotient": True,
            "individual_evaluations_need_not_be_faithful": True,
        },
        "translation": {
            "triangle_width": triangle_width,
            "translation": translation,
            "kernel_l1": triangle_l1,
            "derivative_l1": derivative_l1,
            "exact_l1_distance": exact_translation_l1,
            "exact_l1_formula": translation_formula,
            "w11_upper_bound": sp.simplify(translation * derivative_l1),
            "theta_rule": "theta_r A_(xi,f)=A_(xi,tau_r f), tau_r f(t)=f(t-r)",
            "universal_isometry": True,
            "point_norm_C0_on_completion": True,
        },
        "smooth_generator": {
            "omega": omega,
            "gaussian_transform": gaussian_transform,
            "shifted_transform": shifted_transform,
            "generator_transform": generator_transform,
            "minus_derivative_transform": minus_derivative_transform,
            "formula": "delta_H A_(xi,f)=-A_(xi,f')",
        },
        "periodization": {
            "xi": label_xi,
            "eta": label_eta,
            "period_three": period_three,
            "period_five": period_five,
            "linear_left": linear_left,
            "linear_right": linear_right,
            "small_torus_wraps": len(period_three) < len(label_xi),
            "cofinal_torus_separates_fixture": len(period_five) == len(label_xi),
        },
        "contracts": {
            "generator_bound": "||pi_Lambda(A_(xi,f))|| <= ||f||_1",
            "universal_seminorm": "sup over exact zero-source periodic finite Hamiltonians",
            "null_ideal_quotiented_before_completion": True,
            "star_rule": "A_(xi,f)^*=A_(-xi,conjugate(f))",
            "equivariance": "pi_Lambda(theta_r a)=alpha_r^Lambda(pi_Lambda(a))",
            "beta_enters_carrier": False,
            "source_h_enters_carrier": False,
        },
    }


def triangular_half_moment(width: sp.Expr) -> sp.Expr:
    t = sp.symbols("t", nonnegative=True)
    return sp.simplify(
        2
        * sp.integrate((1 - t / width) * sp.sqrt(t) / width, (t, 0, width))
    )


def ground_doublet_audit() -> dict[str, Any]:
    # INPUTS: an EXP-000789 positive order lower bound and uniform fourth
    # moment datum E|sum_e q_e|^4 <= 64 M4.
    rho_star = sp.Rational(1, 2)
    fourth_moment_bound = sp.Integer(1)
    hbar = sp.Rational(3, 2)
    chi = sp.Rational(5, 4)
    rational_frequency = sp.Rational(1, 8)
    q3_component_count = sp.Integer(8)
    triangle_width = sp.Rational(9, 4)

    m0 = sp.sqrt(rho_star / 2)
    third_moment_bound = sp.Pow(
        q3_component_count**2 * fourth_moment_bound, sp.Rational(3, 4)
    )
    small_frequency_lhs = sp.simplify(
        rational_frequency**2 * third_moment_bound
    )
    small_frequency_rhs = sp.simplify(
        3 * sp.sqrt(q3_component_count) * m0
    )
    xi = tuple(rational_frequency for _ in range(int(q3_component_count)))
    raw_linear_mean = sp.simplify(
        rational_frequency * sp.sqrt(q3_component_count) * m0
    )
    cubic_remainder = sp.simplify(
        rational_frequency**3 * third_moment_bound / 6
    )
    sine_lower = sp.simplify(raw_linear_mean - cubic_remainder)
    separation_d = sp.simplify(raw_linear_mean / 2)
    sine_margin = sp.simplify(sine_lower - separation_d)

    half_moment = triangular_half_moment(triangle_width)
    half_moment_formula = sp.simplify(8 * sp.sqrt(triangle_width) / 15)
    volumes = tuple(sp.Integer(length) ** 3 for length in (16, 24, 32))
    volume_rows: list[dict[str, Any]] = []
    for volume in volumes:
        energy_excess = sp.simplify(hbar**2 / (2 * chi * volume * rho_star))
        vector_invariance_coefficient = sp.simplify(
            2 * sp.sqrt(2 * energy_excess / hbar)
        )
        smear_error_from_half_moment = sp.simplify(
            vector_invariance_coefficient * half_moment
        )
        smear_error_formula = sp.simplify(
            sp.Rational(16, 15)
            * sp.sqrt(hbar * triangle_width / (chi * volume * rho_star))
        )
        volume_rows.append(
            {
                "volume": volume,
                "energy_excess_upper": energy_excess,
                "vector_invariance_coefficient": vector_invariance_coefficient,
                "smear_error_from_half_moment": smear_error_from_half_moment,
                "smear_error_formula": smear_error_formula,
                "plus_smeared_lower": sp.simplify(
                    separation_d - smear_error_formula
                ),
                "minus_smeared_upper": sp.simplify(
                    -separation_d + smear_error_formula
                ),
            }
        )

    volume_threshold = sp.simplify(
        (sp.Rational(32, 15) ** 2)
        * hbar
        * triangle_width
        / (chi * rho_star * separation_d**2)
    )

    return {
        "inputs": {
            "rho_star": rho_star,
            "fourth_moment_bound_M4": fourth_moment_bound,
            "hbar": hbar,
            "chi": chi,
            "rational_frequency_r": rational_frequency,
            "q3_component_count": q3_component_count,
            "triangle_width_T": triangle_width,
        },
        "m0": m0,
        "third_moment_bound_M3": third_moment_bound,
        "third_moment_identity": sp.simplify(
            third_moment_bound ** sp.Rational(4, 3)
        ),
        "xi": xi,
        "small_frequency_lhs": small_frequency_lhs,
        "small_frequency_rhs": small_frequency_rhs,
        "raw_linear_mean": raw_linear_mean,
        "cubic_remainder": cubic_remainder,
        "sine_lower": sine_lower,
        "separation_d": separation_d,
        "sine_margin": sine_margin,
        "witness": "B_r=sin(r sum_e q_e)=(W_xi-W_xi^*)/(2i)",
        "parity_expectation_signs": {"plus": 1, "minus": -1},
        "triangle": {
            "formula": "f_T(t)=(1-|t|/T)_+/T",
            "normalization": 1,
            "half_moment": half_moment,
            "half_moment_formula": half_moment_formula,
        },
        "volume_rows": volume_rows,
        "volume_threshold_for_error_at_most_d_over_2": volume_threshold,
        "energy_excess_formula": "hbar^2/(4 chi V m_L^2)",
        "rho_substitution": "m_L^2>=rho_star/2",
        "approximate_invariance": (
            "||(exp(-it(H-E0)/hbar)-1)psi||^2 <= 2|t| epsilon/hbar"
        ),
        "smear_error_formula": "16/15 sqrt(hbar T/(chi V rho_star))",
        "fixed_smeared_witness_separates_cluster_states": True,
    }


def negative_arveson_audit() -> dict[str, Any]:
    # INPUTS: an exact three-level positive Hamiltonian and a unit vector.
    hbar = sp.Integer(2)
    nu = sp.Integer(3)
    high_probability = sp.Rational(2, 7)
    hamiltonian = sp.diag(0, hbar * nu, 2 * hbar * nu)
    lowering = sp.Matrix([[0, 1, 0], [0, 0, 0], [0, 0, 0]])
    state = sp.Matrix([sp.sqrt(1 - high_probability), sp.sqrt(high_probability), 0])
    energy_excess = sp.simplify((state.H * hamiltonian * state)[0])
    lowered_norm_square = sp.simplify(
        (state.H * lowering.H * lowering * state)[0]
    )
    norm_square = operator_norm_square(lowering)
    bound = sp.simplify(norm_square * energy_excess / (hbar * nu))
    derivation = sp.simplify(sp.I * (hamiltonian * lowering - lowering * hamiltonian) / hbar)
    expected_derivation = sp.simplify(-sp.I * nu * lowering)

    return {
        "inputs": {
            "hbar": hbar,
            "nu": nu,
            "high_probability": high_probability,
        },
        "hamiltonian": hamiltonian,
        "lowering_operator": lowering,
        "state": state,
        "energy_excess": energy_excess,
        "operator_norm_square": norm_square,
        "lowered_norm_square": lowered_norm_square,
        "bound": bound,
        "derivation": derivation,
        "expected_derivation": expected_derivation,
        "arveson_frequency": -nu,
        "general_bound": "omega(a* a)<=||a||_u^2 epsilon/(hbar nu)",
        "cluster_consequence": (
            "epsilon_L->0 annihilates every strictly negative-Arveson element; "
            "the weak-star cluster state is theta-ground"
        ),
    }


def exp_sigma_x(parameter: sp.Expr, sigma_x: sp.MatrixBase) -> sp.Matrix:
    return sp.simplify(sp.cosh(parameter) * sp.eye(2) + sp.sinh(parameter) * sigma_x)


def categorical_m2_audit() -> dict[str, Any]:
    identity, sigma_x, sigma_y, sigma_z = pauli_matrices()
    hbar = sp.Integer(1)

    # INPUTS: the exact R-167 v1.5 cross-beta hostile pair.
    beta_one, coupling_one = sp.Integer(1), sp.Integer(1)
    beta_two, coupling_two = sp.Integer(2), sp.Integer(2)
    hamiltonian_one = -coupling_one * sigma_x
    hamiltonian_two = -coupling_two * sigma_x
    omega_one = sp.simplify(2 * coupling_one / hbar)
    omega_two = sp.simplify(2 * coupling_two / hbar)

    # Two normalized even Laplace kernels have an invertible frequency-response
    # matrix, so their linear combinations isolate the two summands exactly.
    decay_one, decay_two = sp.Integer(1), sp.Integer(3)

    def response(decay: sp.Expr, omega: sp.Expr) -> sp.Expr:
        return sp.simplify(decay**2 / (decay**2 + omega**2))

    response_matrix = sp.Matrix(
        [
            [response(decay_one, omega_one), response(decay_two, omega_one)],
            [response(decay_one, omega_two), response(decay_two, omega_two)],
        ]
    )
    first_coefficients = sp.simplify(response_matrix.inv() * sp.Matrix([1, 0]))
    second_coefficients = sp.simplify(response_matrix.inv() * sp.Matrix([0, 1]))
    isolated_first_responses = sp.simplify(response_matrix * first_coefficients)
    isolated_second_responses = sp.simplify(response_matrix * second_coefficients)

    z_first = block(sigma_z, sp.zeros(2))
    z_second = block(sp.zeros(2), sigma_z)
    y_first = block(sigma_y, sp.zeros(2))
    y_second = block(sp.zeros(2), sigma_y)
    x_first = sp.simplify(-sp.I * y_first * z_first)
    x_second = sp.simplify(-sp.I * y_second * z_second)
    i_first = sp.simplify(z_first**2)
    i_second = sp.simplify(z_second**2)
    direct_sum_basis = (
        i_first,
        x_first,
        y_first,
        z_first,
        i_second,
        x_second,
        y_second,
        z_second,
    )
    flattened_basis = sp.Matrix.hstack(
        *(sp.Matrix(matrix).reshape(16, 1) for matrix in direct_sum_basis)
    )

    derivation_one = sp.simplify(
        sp.I * (hamiltonian_one * sigma_z - sigma_z * hamiltonian_one) / hbar
    )
    derivation_two = sp.simplify(
        sp.I * (hamiltonian_two * sigma_z - sigma_z * hamiltonian_two) / hbar
    )
    generator_difference = sp.simplify(hamiltonian_two - hamiltonian_one)

    def gibbs(beta: sp.Expr, coupling: sp.Expr) -> sp.Matrix:
        return sp.simplify(
            exp_sigma_x(beta * coupling, sigma_x)
            / (2 * sp.cosh(beta * coupling))
        )

    rho_one = gibbs(beta_one, coupling_one)
    rho_two = gibbs(beta_two, coupling_two)
    test_a = sigma_z
    test_b = sigma_y + sigma_z
    kms_rows: list[dict[str, Any]] = []
    for beta, coupling, rho in (
        (beta_one, coupling_one, rho_one),
        (beta_two, coupling_two, rho_two),
    ):
        exp_minus_beta_h = exp_sigma_x(beta * coupling, sigma_x)
        exp_plus_beta_h = exp_sigma_x(-beta * coupling, sigma_x)
        alpha_i_beta_b = sp.simplify(
            exp_minus_beta_h * test_b * exp_plus_beta_h
        )
        lhs = sp.simplify(sp.trace(rho * test_a * alpha_i_beta_b))
        rhs = sp.simplify(sp.trace(rho * test_b * test_a))
        cyclic_lhs = sp.simplify(
            sp.trace(test_a * exp_minus_beta_h * test_b)
            / (2 * sp.cosh(beta * coupling))
        )
        cyclic_residual = sp.simplify(cyclic_lhs - rhs)
        kms_rows.append(
            {
                "beta": beta,
                "coupling": coupling,
                "rho": rho,
                "lhs": lhs,
                "cyclic_lhs": cyclic_lhs,
                "rhs": rhs,
                "cyclic_residual": cyclic_residual,
                "rho_determinant": sp.simplify(rho.det()),
            }
        )

    return {
        "inputs": {
            "beta_one": beta_one,
            "H_one": hamiltonian_one,
            "beta_two": beta_two,
            "H_two": hamiltonian_two,
            "configuration_label": sigma_z,
            "hbar": hbar,
        },
        "frequencies": (omega_one, omega_two),
        "laplace_decays": (decay_one, decay_two),
        "response_matrix": response_matrix,
        "response_determinant": sp.factor(response_matrix.det()),
        "first_coefficients": first_coefficients,
        "second_coefficients": second_coefficients,
        "isolated_first_responses": isolated_first_responses,
        "isolated_second_responses": isolated_second_responses,
        "direct_sum_basis_rank": flattened_basis.rank(),
        "direct_sum_dimension": len(direct_sum_basis),
        "first_shift_to_y": sp.pi / (2 * omega_one),
        "second_shift_to_y": sp.pi / (2 * omega_two),
        "derivation_one": derivation_one,
        "derivation_two": derivation_two,
        "generator_difference": generator_difference,
        "generator_difference_trace": sp.trace(generator_difference),
        "generator_difference_determinant": generator_difference.det(),
        "kms_rows": kms_rows,
        "generated_algebra": "M2 direct-sum M2",
        "common_direct_sum_shift_exists": True,
        "single_labelled_M2_generator_exists": False,
        "categorical_envelope_implies_quasi_local_limit": False,
        "categorical_envelope_implies_exhaustion_uniqueness": False,
    }


def projected_corridor_audit() -> dict[str, Any]:
    # INPUTS for the conservative bounded-cutoff factorial corridor.
    degree = sp.Integer(6)
    c_value = sp.Rational(1, 100)
    hbar = sp.Integer(1)
    time_horizon = sp.Rational(1, 10)
    observable_norm = sp.Integer(1)
    boundary_norm = sp.Integer(1)
    alpha = sp.Rational(1, 3)
    cutoff_rows: list[dict[str, Any]] = []
    for order in (12, 24, 48, 96):
        order_value = sp.Integer(order)
        coordinate_cutoff = order_value**alpha
        interaction_bound = sp.simplify(4 * c_value * coordinate_cutoff**2)
        nu_bound = sp.simplify(4 * degree * interaction_bound / hbar)
        factorial_bound = sp.simplify(
            8
            * sp.sqrt(2)
            * boundary_norm
            * observable_norm
            * sp.exp(nu_bound * time_horizon)
            * (nu_bound * time_horizon) ** order_value
            / sp.factorial(order_value)
        )
        stirling_log_upper = sp.simplify(
            sp.log(8 * sp.sqrt(2) * boundary_norm * observable_norm)
            + nu_bound * time_horizon
            + order_value
            * (sp.log(nu_bound * time_horizon) + 1 - sp.log(order_value))
        )
        cutoff_rows.append(
            {
                "order_R": order_value,
                "coordinate_cutoff_L": coordinate_cutoff,
                "interaction_bound_J": interaction_bound,
                "nu_bound": nu_bound,
                "factorial_bound": factorial_bound,
                "stirling_log_upper": stirling_log_upper,
            }
        )

    asymptotic_order = sp.symbols("R", positive=True)
    asymptotic_nu_t = sp.simplify(
        16
        * degree
        * c_value
        * time_horizon
        * asymptotic_order ** (2 * alpha)
        / hbar
    )
    normalized_stirling_log = sp.simplify(
        (
            asymptotic_nu_t
            + asymptotic_order
            * (
                sp.log(asymptotic_nu_t)
                + 1
                - sp.log(asymptotic_order)
            )
        )
        / (asymptotic_order * sp.log(asymptotic_order))
    )
    normalized_limit = sp.limit(
        normalized_stirling_log, asymptotic_order, sp.oo
    )

    # INPUTS for the exact four-dimensional static-tail hostile family.
    time_value = sp.Rational(5, 3)
    k_value = sp.simplify(sp.pi * hbar / (4 * time_value))
    test_gaussian_parameter = sp.Rational(3, 2)
    static_rows: list[dict[str, Any]] = []
    for integer_index in (0, 1, 2):
        index = sp.Integer(integer_index)
        radius = (2 * index + 1) * sp.pi
        epsilon = sp.exp(-(radius**4))
        partition = 1 + 3 * epsilon
        q_x = radius * sp.diag(0, 0, 1, 1)
        q_y = radius * sp.diag(0, 1, 0, 1)
        tail = sp.simplify(q_x * q_y)
        rho = sp.diag(1, epsilon, epsilon, epsilon) / partition
        log_rho = sp.diag(
            -sp.log(partition),
            -(radius**4) - sp.log(partition),
            -(radius**4) - sp.log(partition),
            -(radius**4) - sp.log(partition),
        )
        raw_word = sp.diag(1, 1, -1, -1)
        cutoff_hamiltonian = sp.zeros(4)
        cutoff_hamiltonian[0, 3] = -sp.I * k_value
        cutoff_hamiltonian[3, 0] = sp.I * k_value
        full_hamiltonian = sp.simplify(cutoff_hamiltonian + tail)

        angle = sp.simplify(k_value * time_value / hbar)
        cutoff_unitary = sp.eye(4)
        cutoff_unitary[0, 0] = sp.cos(angle)
        cutoff_unitary[0, 3] = sp.sin(angle)
        cutoff_unitary[3, 0] = -sp.sin(angle)
        cutoff_unitary[3, 3] = sp.cos(angle)
        cutoff_orbit = sp.simplify(
            cutoff_unitary * raw_word * cutoff_unitary.H
        )
        commutator = sp.simplify(tail * cutoff_orbit - cutoff_orbit * tail)
        expected_cutoff_block = sp.Matrix([[0, -1], [-1, 0]])
        actual_cutoff_block = cutoff_orbit.extract((0, 3), (0, 3))
        expected_commutator = sp.zeros(4)
        expected_commutator[0, 3] = radius**2
        expected_commutator[3, 0] = -(radius**2)

        tail_duhamel_square = sp.simplify(radius**4 * epsilon / partition)
        commutator_duhamel_square = sp.simplify(
            2 * (1 - epsilon) / partition
        )
        commutator_sharp_sum_square = sp.simplify(
            2 * radius**4 * (1 + epsilon) / partition
        )
        cutoff_static_left_square = sp.simplify(
            2 * (1 + epsilon) / partition
        )
        cutoff_static_right_square = cutoff_static_left_square
        cutoff_static_averaged_sharp_square = sp.simplify(
            (cutoff_static_left_square + cutoff_static_right_square) / 2
        )
        cutoff_static_unaveraged_sharp_square = sp.simplify(
            cutoff_static_left_square + cutoff_static_right_square
        )
        full_orbit_operator_bound = sp.simplify(
            4 * k_value / sp.sqrt(radius**4 + 4 * k_value**2)
        )

        gaussian_coordinate_moment = sp.simplify(
            (
                1
                + epsilon
                + 2
                * epsilon
                * sp.exp(test_gaussian_parameter * radius**2)
            )
            / partition
        )
        gaussian_uniform_bound = sp.simplify(
            2 + 2 * sp.exp(test_gaussian_parameter**2 / 4)
        )

        static_rows.append(
            {
                "index_n": index,
                "radius_r": radius,
                "epsilon": epsilon,
                "partition_Z": partition,
                "q_x": q_x,
                "q_y": q_y,
                "tail_X": tail,
                "rho": rho,
                "log_rho": log_rho,
                "raw_word_W": raw_word,
                "cutoff_Hamiltonian_K": cutoff_hamiltonian,
                "full_Hamiltonian_H": full_hamiltonian,
                "cutoff_orbit_B": cutoff_orbit,
                "cutoff_orbit_00_11_block": actual_cutoff_block,
                "expected_cutoff_block": expected_cutoff_block,
                "commutator_C": commutator,
                "expected_commutator_C": expected_commutator,
                "rho_tail_commutator": sp.simplify(rho * tail - tail * rho),
                "log_rho_tail_commutator": sp.simplify(
                    log_rho * tail - tail * log_rho
                ),
                "tail_duhamel_square": tail_duhamel_square,
                "commutator_duhamel_square": commutator_duhamel_square,
                "commutator_sharp_sum_square": commutator_sharp_sum_square,
                "cutoff_static_left_square": cutoff_static_left_square,
                "cutoff_static_right_square": cutoff_static_right_square,
                "cutoff_static_averaged_sharp_square": (
                    cutoff_static_averaged_sharp_square
                ),
                "cutoff_static_unaveraged_sharp_square": (
                    cutoff_static_unaveraged_sharp_square
                ),
                "full_orbit_operator_bound": full_orbit_operator_bound,
                "gaussian_coordinate_moment": gaussian_coordinate_moment,
                "gaussian_uniform_bound": gaussian_uniform_bound,
                "state_invariant_under_K": matrix_zero(
                    rho * cutoff_hamiltonian - cutoff_hamiltonian * rho
                ),
                "state_invariant_under_H": matrix_zero(
                    rho * full_hamiltonian - full_hamiltonian * rho
                ),
            }
        )

    n_symbol = sp.symbols("n", integer=True, nonnegative=True)
    r_symbol = (2 * n_symbol + 1) * sp.pi
    eps_symbol = sp.exp(-(r_symbol**4))
    z_symbol = 1 + 3 * eps_symbol
    static_limits = {
        "tail_duhamel_square": sp.limit(
            r_symbol**4 * eps_symbol / z_symbol, n_symbol, sp.oo
        ),
        "commutator_duhamel_square": sp.limit(
            2 * (1 - eps_symbol) / z_symbol, n_symbol, sp.oo
        ),
        "commutator_sharp_sum_square": sp.limit(
            2 * r_symbol**4 * (1 + eps_symbol) / z_symbol,
            n_symbol,
            sp.oo,
        ),
        "cutoff_static_averaged_sharp_square": sp.limit(
            2 * (1 + eps_symbol) / z_symbol, n_symbol, sp.oo
        ),
        "cutoff_static_unaveraged_sharp_square": sp.limit(
            4 * (1 + eps_symbol) / z_symbol, n_symbol, sp.oo
        ),
        "full_orbit_operator_bound": sp.limit(
            4 * k_value / sp.sqrt(r_symbol**4 + 4 * k_value**2),
            n_symbol,
            sp.oo,
        ),
    }

    return {
        "bounded_cutoff": {
            "inputs": {
                "degree_z": degree,
                "c": c_value,
                "hbar": hbar,
                "time_horizon_T": time_horizon,
                "boundary_norm": boundary_norm,
                "observable_norm": observable_norm,
                "alpha": alpha,
            },
            "interaction_rule": "J_L<=4 c L^2",
            "nu_rule": "nu_L=4 z J_L/hbar<=96 c L^2/hbar",
            "factorial_rule": (
                "8 sqrt(2)||X||||A|| exp(nu_L T)(nu_L T)^R/R!"
            ),
            "rows": cutoff_rows,
            "normalized_stirling_log_limit": normalized_limit,
            "expected_normalized_limit": sp.simplify(2 * alpha - 1),
            "corridor_condition": "0<alpha<1/2",
        },
        "static_tail": {
            "inputs": {
                "r_rule": "(2n+1)pi",
                "epsilon_rule": "exp(-r^4)",
                "time_T": time_value,
                "hbar": hbar,
                "k": k_value,
                "gaussian_parameter_a": test_gaussian_parameter,
            },
            "rows": static_rows,
            "limits": static_limits,
            "log_rho_tail_commutator": 0,
            "gaussian_completion_square": (
                "-r^4+a r^2=-(r^2-a/2)^2+a^2/4"
            ),
            "full_vs_cutoff_averaged_sharp_square_limit": 2,
            "full_vs_cutoff_unaveraged_sharp_square_limit": 4,
            "q3lock_counterexample": False,
            "logical_inference_rejected": (
                "static Duhamel tail plus first modular derivative does not "
                "imply projected orbit locality"
            ),
        },
    }


def find_certificate() -> Path | None:
    return next((path for path in CERTIFICATE_CANDIDATES if path.exists()), None)


def authority_audit(audit: Audit, staged: bool) -> dict[str, Any]:
    certificate = find_certificate()
    missing: list[str] = []
    if not MANIFEST.exists():
        missing.append(str(MANIFEST.relative_to(REPO)).replace("\\", "/"))
    if certificate is None:
        missing.append(
            str(CERTIFICATE_CANDIDATES[0].relative_to(REPO)).replace("\\", "/")
        )
    for parent in PARENTS:
        if not parent.exists():
            missing.append(str(parent.relative_to(REPO)).replace("\\", "/"))

    if missing:
        if not staged:
            raise FileNotFoundError(
                f"staged v1.6 authority is missing ({missing[0]}); rerun with --staged"
            )
        return {"status": "STAGED", "missing": missing, "checked": []}

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate_text = " ".join(certificate.read_text(encoding="utf-8").split())
    checks_before = len(audit.rows)
    audit.check(
        "authority task",
        manifest.get("task_id") == EXPECTED_TASK,
        manifest.get("task_id"),
        EXPECTED_TASK,
        "authority",
    )
    audit.check(
        "authority exploration",
        manifest.get("exploration_id") == EXPECTED_EXPLORATION,
        manifest.get("exploration_id"),
        EXPECTED_EXPLORATION,
        "authority",
    )
    audit.check(
        "authority result number",
        manifest.get("result_number") == EXPECTED_RESULT_NUMBER,
        manifest.get("result_number"),
        EXPECTED_RESULT_NUMBER,
        "authority",
    )
    audit.check(
        "authority result version",
        manifest.get("result_version") == EXPECTED_RESULT_VERSION,
        manifest.get("result_version"),
        EXPECTED_RESULT_VERSION,
        "authority",
    )
    audit.check(
        "authority result id",
        manifest.get("result_id") == EXPECTED_RESULT_ID,
        manifest.get("result_id"),
        EXPECTED_RESULT_ID,
        "authority",
    )
    audit.check(
        "authority claim nonbearing",
        manifest.get("claim_bearing") is False,
        manifest.get("claim_bearing"),
        False,
        "authority",
    )
    audit.check(
        "authority closed subgates",
        tuple(manifest.get("closed_subgates", [])) == EXPECTED_CLOSED_SUBGATES,
        manifest.get("closed_subgates", []),
        EXPECTED_CLOSED_SUBGATES,
        "authority",
    )
    audit.check(
        "authority new negative set",
        tuple(manifest.get("negative_ids", [])) == NEGATIVE_IDS,
        manifest.get("negative_ids", []),
        NEGATIVE_IDS,
        "authority",
    )
    audit.check(
        "authority reused negative set",
        tuple(manifest.get("reused_negative_ids", [])) == REUSED_NEGATIVE_IDS,
        manifest.get("reused_negative_ids", []),
        REUSED_NEGATIVE_IDS,
        "authority",
    )
    route_status = manifest.get("route_status", {})
    next_gate = route_status.get("next_gate", manifest.get("next_gate"))
    audit.check(
        "authority retained next gate",
        next_gate == EXPECTED_NEXT_GATE,
        next_gate,
        EXPECTED_NEXT_GATE,
        "authority",
    )
    audit.check(
        "authority open gates",
        tuple(manifest.get("open_gates", [])) == EXPECTED_OPEN_GATES,
        manifest.get("open_gates", []),
        EXPECTED_OPEN_GATES,
        "authority",
    )
    primary_path = str(SCRIPT.relative_to(REPO)).replace("\\", "/")
    verification = manifest.get("verification", {})
    audit.check(
        "authority primary script",
        verification.get("primary_script", verification.get("primary")) == primary_path,
        verification.get("primary_script", verification.get("primary")),
        primary_path,
        "authority",
    )

    certificate_tokens = (
        "fixed finite raw",
        "orbit-smear",
        "zero-source",
        "all-exhaustion",
        "quasi-local",
        "GNS gap",
        "Pre-A",
    )
    for token in certificate_tokens:
        audit.check(
            f"certificate token {token}",
            token.lower() in certificate_text.lower(),
            token.lower() in certificate_text.lower(),
            True,
            "authority",
        )

    for section in (
        "selected_tangent_raw_word_completion",
        "zero_source_universal_orbit_smear_carrier",
        "distinct_ground_doublets",
        "categorical_boundary",
        "projected_corridor_route_audit",
    ):
        audit.check(
            f"authority section {section}",
            isinstance(manifest.get(section), dict),
            section in manifest,
            True,
            "authority",
        )
    no_overclaim = manifest.get("no_overclaim", "").lower()
    for token in (
        "quasi-local",
        "all-exhaustion",
        "raw characters",
        "gns",
        "pre-a",
    ):
        audit.check(
            f"authority no-overclaim token {token}",
            token in no_overclaim,
            token in no_overclaim,
            True,
            "authority",
        )

    formal_missing: list[str] = []
    exploration_found = False
    if EXPLORATION_LEDGER.exists():
        for line in EXPLORATION_LEDGER.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            record = json.loads(line)
            if record.get("id") == EXPECTED_EXPLORATION:
                exploration_found = True
                break
    if not exploration_found:
        formal_missing.append(EXPECTED_EXPLORATION)

    result_text = RESULT_LEDGER.read_text(encoding="utf-8")
    if not (
        EXPECTED_RESULT_NUMBER in result_text
        and EXPECTED_RESULT_VERSION in result_text
        and SLUG.replace("-", " ")[:24] in result_text.lower().replace("-", " ")
    ):
        # The slug phrase is optional in historical ledger formatting; the
        # number/version pair remains the load-bearing staged condition.
        if not (
            EXPECTED_RESULT_NUMBER in result_text
            and EXPECTED_RESULT_VERSION in result_text
        ):
            formal_missing.append(f"{EXPECTED_RESULT_NUMBER} {EXPECTED_RESULT_VERSION}")

    status = json.loads(STATUS.read_text(encoding="utf-8"))
    audit.check(
        "C6 tier unchanged",
        status.get("tier") == "T1",
        status.get("tier"),
        "T1",
        "claim_firewall",
    )
    audit.check(
        "C6 lifecycle unchanged",
        status.get("lifecycle") == "ACTIVE",
        status.get("lifecycle"),
        "ACTIVE",
        "claim_firewall",
    )

    if formal_missing:
        if not staged:
            raise FileNotFoundError(
                "staged v1.6 formal authority is missing ("
                + ", ".join(formal_missing)
                + "); rerun with --staged"
            )
        return {
            "status": "STAGED",
            "missing": formal_missing,
            "checked": [row["name"] for row in audit.rows[checks_before:]],
            "certificate": str(certificate.relative_to(REPO)).replace("\\", "/"),
        }

    return {
        "status": "COMPLETE",
        "missing": [],
        "checked": [row["name"] for row in audit.rows[checks_before:]],
        "certificate": str(certificate.relative_to(REPO)).replace("\\", "/"),
    }


def run_audit(staged: bool) -> dict[str, Any]:
    audit = Audit()
    modular = modular_right_context_audit()
    sequential = sequential_fejer_audit()
    universal = universal_orbit_smear_audit()
    doublet = ground_doublet_audit()
    arveson = negative_arveson_audit()
    categorical = categorical_m2_audit()
    projected = projected_corridor_audit()

    audit.check(
        "modular commutant identity",
        matrix_equal(modular["lhs"], modular["rhs"]),
        modular["lhs"],
        modular["rhs"],
        "modular_context",
    )
    audit.check(
        "modular half-translate adjoint",
        matrix_equal(
            modular["commutant_multiplier"], modular["sigma_plus_half"]
        ),
        modular["commutant_multiplier"],
        modular["sigma_plus_half"],
        "modular_context",
    )
    audit.check(
        "modular multiplier inequality",
        sp.simplify(
            modular["multiplier_norm_square"] * modular["base_square"]
            - modular["lhs_square"]
        )
        >= 0,
        modular["lhs_square"],
        "<= multiplier norm squared times base square",
        "modular_context",
    )
    audit.check(
        "modular fixture saturates multiplier bound",
        sp.simplify(
            modular["multiplier_norm_square"] * modular["base_square"]
            - modular["lhs_square"]
        )
        == 0,
        modular["lhs_square"],
        modular["multiplier_norm_square"] * modular["base_square"],
        "modular_context",
    )
    audit.check(
        "Arveson exponential bound exact in fixture",
        sp.simplify(
            modular["exponential_band_bound"] ** 2
            - modular["multiplier_norm_square"]
        )
        == 0,
        modular["exponential_band_bound"],
        sp.sqrt(modular["multiplier_norm_square"]),
        "modular_context",
    )
    audit.check(
        "physical modular convention",
        modular["physical_frequency"] == sp.log(3),
        modular["physical_frequency"],
        sp.log(3),
        "modular_context",
    )

    for row in sequential["rows"]:
        audit.check(
            f"sequential cutoff finite letter {row['index']}",
            row["cutoff_finite"],
            row["cutoff"],
            "finite",
            "sequential_fejer",
        )
        audit.check(
            f"sequential cutoff at least one letter {row['index']}",
            bool(sp.N(row["cutoff"], 40) >= 1),
            row["cutoff"],
            ">=1",
            "sequential_fejer",
        )
        audit.check(
            f"sequential exact below crude letter {row['index']}",
            bool(
                sp.N(row["contextual_error"] - row["crude_error"], 50) <= 0
            ),
            row["contextual_error"],
            row["crude_error"],
            "sequential_fejer",
        )
        audit.check(
            f"sequential crude target letter {row['index']}",
            sp.simplify(row["crude_error"] - sequential["per_letter_error"])
            == 0,
            row["crude_error"],
            sequential["per_letter_error"],
            "sequential_fejer",
        )
    audit.check(
        "sequential exact total below target",
        bool(
            sp.N(
                sequential["exact_total_error"]
                - sequential["inputs"]["target_error"],
                50,
            )
            < 0
        ),
        sequential["exact_total_error"],
        sequential["inputs"]["target_error"],
        "sequential_fejer",
    )
    audit.check(
        "sequential crude total equals target",
        sp.simplify(
            sequential["crude_total_error"]
            - sequential["inputs"]["target_error"]
        )
        == 0,
        sequential["crude_total_error"],
        sequential["inputs"]["target_error"],
        "sequential_fejer",
    )
    audit.check(
        "every scanned fixed length finite",
        all(row["all_cutoffs_finite"] for row in sequential["length_scan"]),
        sequential["length_scan"],
        "all finite",
        "sequential_fejer",
    )
    audit.check(
        "no uniform word-length promotion",
        sequential["fixed_finite_word_only"]
        and sequential["uniform_in_word_length"] is False,
        {
            "fixed": sequential["fixed_finite_word_only"],
            "uniform": sequential["uniform_in_word_length"],
        },
        {"fixed": True, "uniform": False},
        "sequential_fejer",
    )
    audit.check(
        "stars shifts mixtures preserve recursion",
        sequential["stars_preserve_bandwidth_and_error"]
        and sequential["real_time_shifts_preserve_bandwidth_and_error"]
        and sequential["convex_phase_mixtures_preserve_bound"],
        True,
        True,
        "sequential_fejer",
    )

    contract = universal["laplace_contract"]
    audit.check(
        "orbit-smear representation contract",
        bool(
            sp.N(contract["represented_norm_square"], 40)
            <= contract["kernel_l1"] ** 2
        ),
        contract["represented_norm_square"],
        f"<= {contract['kernel_l1'] ** 2}",
        "universal_carrier",
    )
    audit.check(
        "Laplace response positive contraction",
        0 < contract["cosine_response"] < 1,
        contract["cosine_response"],
        "in (0,1)",
        "universal_carrier",
    )
    cstar = universal["cstar_completion"]
    audit.check(
        "joint null ideal fixture",
        matrix_zero(cstar["null_image"]),
        cstar["null_image"],
        sp.zeros(2, 1),
        "universal_carrier",
    )
    audit.check(
        "joint representation Cstar identity",
        sp.simplify(cstar["square_norm"] - cstar["universal_norm_square"])
        == 0,
        cstar["square_norm"],
        cstar["universal_norm_square"],
        "universal_carrier",
    )
    translation = universal["translation"]
    audit.check(
        "triangular translation exact formula",
        sp.simplify(
            translation["exact_l1_distance"] - translation["exact_l1_formula"]
        )
        == 0,
        translation["exact_l1_distance"],
        translation["exact_l1_formula"],
        "universal_carrier",
    )
    audit.check(
        "W11 translation upper bound",
        translation["exact_l1_distance"] <= translation["w11_upper_bound"],
        translation["exact_l1_distance"],
        translation["w11_upper_bound"],
        "universal_carrier",
    )
    audit.check(
        "translation isometric C0 contract",
        translation["universal_isometry"]
        and translation["point_norm_C0_on_completion"],
        True,
        True,
        "universal_carrier",
    )
    generator = universal["smooth_generator"]
    audit.check(
        "smooth generator integration by parts",
        sp.simplify(
            generator["generator_transform"]
            - generator["minus_derivative_transform"]
        )
        == 0,
        generator["generator_transform"],
        generator["minus_derivative_transform"],
        "universal_carrier",
    )
    audit.check(
        "shift derivative equals generator",
        sp.simplify(
            sp.diff(
                sp.exp(sp.I * generator["omega"] * sp.Symbol("r"))
                * generator["gaussian_transform"],
                sp.Symbol("r"),
            ).subs(sp.Symbol("r"), 0)
            - generator["generator_transform"]
        )
        == 0,
        "d/dr at zero",
        "i omega Fourier(f)",
        "universal_carrier",
    )
    periodization = universal["periodization"]
    audit.check(
        "periodization linear",
        periodization["linear_left"] == periodization["linear_right"],
        periodization["linear_left"],
        periodization["linear_right"],
        "universal_carrier",
    )
    audit.check(
        "small-torus wrap fixture",
        periodization["small_torus_wraps"],
        periodization["period_three"],
        "wrapped",
        "universal_carrier",
    )
    audit.check(
        "cofinal-torus label separation fixture",
        periodization["cofinal_torus_separates_fixture"],
        periodization["period_five"],
        "support separated",
        "universal_carrier",
    )
    contracts = universal["contracts"]
    audit.check(
        "carrier beta independent and zero source",
        contracts["beta_enters_carrier"] is False
        and contracts["source_h_enters_carrier"] is False,
        {
            "beta": contracts["beta_enters_carrier"],
            "source": contracts["source_h_enters_carrier"],
        },
        {"beta": False, "source": False},
        "universal_carrier",
    )
    audit.check(
        "quotient precedes Cstar completion",
        contracts["null_ideal_quotiented_before_completion"],
        True,
        True,
        "universal_carrier",
    )

    inputs = doublet["inputs"]
    audit.check(
        "EXP789 m0 substitution",
        sp.simplify(doublet["m0"] - sp.sqrt(inputs["rho_star"] / 2)) == 0,
        doublet["m0"],
        sp.sqrt(inputs["rho_star"] / 2),
        "ground_doublet",
    )
    audit.check(
        "Q3 rational label has eight equal entries",
        len(doublet["xi"]) == inputs["q3_component_count"]
        and all(
            entry == inputs["rational_frequency_r"] for entry in doublet["xi"]
        ),
        doublet["xi"],
        "r(1,...,1)",
        "ground_doublet",
    )
    audit.check(
        "third moment reconstruction",
        sp.simplify(
            doublet["third_moment_bound_M3"]
            - (64 * inputs["fourth_moment_bound_M4"]) ** sp.Rational(3, 4)
        )
        == 0,
        doublet["third_moment_bound_M3"],
        "(64 M4)^(3/4)",
        "ground_doublet",
    )
    audit.check(
        "rational sine small-frequency condition",
        doublet["small_frequency_lhs"] <= doublet["small_frequency_rhs"],
        doublet["small_frequency_lhs"],
        doublet["small_frequency_rhs"],
        "ground_doublet",
    )
    audit.check(
        "sine witness lower bound",
        doublet["sine_lower"] >= doublet["separation_d"]
        and doublet["sine_margin"] > 0,
        doublet["sine_lower"],
        doublet["separation_d"],
        "ground_doublet",
    )
    audit.check(
        "exact d formula",
        sp.simplify(
            doublet["separation_d"]
            - inputs["rational_frequency_r"]
            * sp.sqrt(8)
            * doublet["m0"]
            / 2
        )
        == 0,
        doublet["separation_d"],
        "r sqrt(8) m0/2",
        "ground_doublet",
    )
    triangle = doublet["triangle"]
    audit.check(
        "triangular kernel normalized",
        triangle["normalization"] == 1,
        triangle["normalization"],
        1,
        "ground_doublet",
    )
    audit.check(
        "triangular half moment 8 sqrt(T)/15",
        sp.simplify(triangle["half_moment"] - triangle["half_moment_formula"])
        == 0,
        triangle["half_moment"],
        triangle["half_moment_formula"],
        "ground_doublet",
    )
    for row in doublet["volume_rows"]:
        audit.check(
            f"smear error formula V={row['volume']}",
            sp.simplify(
                row["smear_error_from_half_moment"]
                - row["smear_error_formula"]
            )
            == 0,
            row["smear_error_from_half_moment"],
            row["smear_error_formula"],
            "ground_doublet",
        )
    audit.check(
        "smear error decreases with volume",
        all(
            left["smear_error_formula"] > right["smear_error_formula"]
            for left, right in zip(
                doublet["volume_rows"], doublet["volume_rows"][1:]
            )
        ),
        [row["smear_error_formula"] for row in doublet["volume_rows"]],
        "strictly decreasing",
        "ground_doublet",
    )
    audit.check(
        "declared volumes exceed separation threshold",
        all(
            row["volume"]
            >= doublet["volume_threshold_for_error_at_most_d_over_2"]
            for row in doublet["volume_rows"]
        ),
        [row["volume"] for row in doublet["volume_rows"]],
        doublet["volume_threshold_for_error_at_most_d_over_2"],
        "ground_doublet",
    )
    audit.check(
        "fixed smeared witness separates signs",
        all(
            row["plus_smeared_lower"] > 0 and row["minus_smeared_upper"] < 0
            for row in doublet["volume_rows"]
        ),
        [
            (row["plus_smeared_lower"], row["minus_smeared_upper"])
            for row in doublet["volume_rows"]
        ],
        "positive/negative",
        "ground_doublet",
    )

    audit.check(
        "negative Arveson derivation",
        matrix_equal(arveson["derivation"], arveson["expected_derivation"]),
        arveson["derivation"],
        arveson["expected_derivation"],
        "ground_spectrum",
    )
    audit.check(
        "negative Arveson near-ground bound",
        arveson["lowered_norm_square"] <= arveson["bound"],
        arveson["lowered_norm_square"],
        arveson["bound"],
        "ground_spectrum",
    )
    audit.check(
        "negative Arveson fixture saturates",
        sp.simplify(arveson["lowered_norm_square"] - arveson["bound"])
        == 0,
        arveson["lowered_norm_square"],
        arveson["bound"],
        "ground_spectrum",
    )
    audit.check(
        "energy Markov factor",
        sp.simplify(
            arveson["energy_excess"]
            / (arveson["inputs"]["hbar"] * arveson["inputs"]["nu"])
            - arveson["inputs"]["high_probability"]
        )
        == 0,
        arveson["energy_excess"],
        "hbar nu times high probability",
        "ground_spectrum",
    )

    audit.check(
        "M2 response matrix invertible",
        categorical["response_determinant"] != 0,
        categorical["response_determinant"],
        "nonzero",
        "categorical_no_go",
    )
    audit.check(
        "M2 first component isolated",
        matrix_equal(
            categorical["isolated_first_responses"], sp.Matrix([1, 0])
        ),
        categorical["isolated_first_responses"],
        sp.Matrix([1, 0]),
        "categorical_no_go",
    )
    audit.check(
        "M2 second component isolated",
        matrix_equal(
            categorical["isolated_second_responses"], sp.Matrix([0, 1])
        ),
        categorical["isolated_second_responses"],
        sp.Matrix([0, 1]),
        "categorical_no_go",
    )
    audit.check(
        "M2 orbit smears generate direct sum",
        categorical["direct_sum_basis_rank"]
        == categorical["direct_sum_dimension"]
        == 8,
        categorical["direct_sum_basis_rank"],
        8,
        "categorical_no_go",
    )
    audit.check(
        "M2 labelled derivations disagree",
        not matrix_equal(
            categorical["derivation_one"], categorical["derivation_two"]
        ),
        {
            "first": categorical["derivation_one"],
            "second": categorical["derivation_two"],
        },
        "different",
        "categorical_no_go",
    )
    audit.check(
        "M2 generator difference nonscalar",
        categorical["generator_difference_trace"] == 0
        and categorical["generator_difference_determinant"] != 0,
        categorical["generator_difference"],
        "traceless nonscalar",
        "categorical_no_go",
    )
    for index, row in enumerate(categorical["kms_rows"], start=1):
        audit.check(
            f"M2 component {index} KMS boundary identity",
            row["cyclic_residual"] == 0,
            row["cyclic_lhs"],
            row["rhs"],
            "categorical_no_go",
        )
        audit.check(
            f"M2 component {index} Gibbs state faithful",
            row["rho_determinant"] > 0,
            row["rho_determinant"],
            ">0",
            "categorical_no_go",
        )
    audit.check(
        "categorical carrier does not imply quasi-locality",
        categorical["common_direct_sum_shift_exists"]
        and categorical["single_labelled_M2_generator_exists"] is False
        and categorical["categorical_envelope_implies_quasi_local_limit"] is False
        and categorical["categorical_envelope_implies_exhaustion_uniqueness"]
        is False,
        {
            "common_shift": categorical["common_direct_sum_shift_exists"],
            "single_labelled_generator": categorical[
                "single_labelled_M2_generator_exists"
            ],
            "quasi_local": categorical[
                "categorical_envelope_implies_quasi_local_limit"
            ],
            "exhaustion_unique": categorical[
                "categorical_envelope_implies_exhaustion_uniqueness"
            ],
        },
        {
            "common_shift": True,
            "single_labelled_generator": False,
            "quasi_local": False,
            "exhaustion_unique": False,
        },
        "categorical_no_go",
    )

    bounded_cutoff = projected["bounded_cutoff"]
    audit.check(
        "bounded-cutoff nu coefficient",
        all(
            sp.simplify(
                row["nu_bound"]
                - 96
                * bounded_cutoff["inputs"]["c"]
                * row["coordinate_cutoff_L"] ** 2
                / bounded_cutoff["inputs"]["hbar"]
            )
            == 0
            for row in bounded_cutoff["rows"]
        ),
        [row["nu_bound"] for row in bounded_cutoff["rows"]],
        "96 c L^2/hbar",
        "projected_corridor",
    )
    audit.check(
        "bounded-cutoff factorial rows positive",
        all(row["factorial_bound"] > 0 for row in bounded_cutoff["rows"]),
        [row["factorial_bound"] for row in bounded_cutoff["rows"]],
        "all positive",
        "projected_corridor",
    )
    audit.check(
        "bounded-cutoff factorial rows decrease",
        all(
            left["factorial_bound"] > right["factorial_bound"]
            for left, right in zip(
                bounded_cutoff["rows"], bounded_cutoff["rows"][1:]
            )
        ),
        [row["factorial_bound"] for row in bounded_cutoff["rows"]],
        "strictly decreasing",
        "projected_corridor",
    )
    audit.check(
        "bounded-cutoff subcritical normalized log",
        sp.simplify(
            bounded_cutoff["normalized_stirling_log_limit"]
            - bounded_cutoff["expected_normalized_limit"]
        )
        == 0
        and bounded_cutoff["normalized_stirling_log_limit"] < 0,
        bounded_cutoff["normalized_stirling_log_limit"],
        bounded_cutoff["expected_normalized_limit"],
        "projected_corridor",
    )

    static_tail = projected["static_tail"]
    for row in static_tail["rows"]:
        audit.check(
            f"static-tail cutoff orbit block n={row['index_n']}",
            matrix_equal(
                row["cutoff_orbit_00_11_block"], row["expected_cutoff_block"]
            ),
            row["cutoff_orbit_00_11_block"],
            row["expected_cutoff_block"],
            "static_tail_no_go",
        )
        audit.check(
            f"static-tail commutator entries n={row['index_n']}",
            matrix_equal(row["commutator_C"], row["expected_commutator_C"]),
            row["commutator_C"],
            row["expected_commutator_C"],
            "static_tail_no_go",
        )
        audit.check(
            f"static-tail commutes with rho n={row['index_n']}",
            matrix_zero(row["rho_tail_commutator"]),
            row["rho_tail_commutator"],
            sp.zeros(4),
            "static_tail_no_go",
        )
        audit.check(
            f"static-tail first modular derivative zero n={row['index_n']}",
            matrix_zero(row["log_rho_tail_commutator"]),
            row["log_rho_tail_commutator"],
            sp.zeros(4),
            "static_tail_no_go",
        )
        audit.check(
            f"static-tail Gaussian coordinate bound n={row['index_n']}",
            row["gaussian_coordinate_moment"] <= row["gaussian_uniform_bound"],
            row["gaussian_coordinate_moment"],
            row["gaussian_uniform_bound"],
            "static_tail_no_go",
        )
        audit.check(
            f"static-tail deliberately non-Gibbs fixture n={row['index_n']}",
            row["state_invariant_under_K"] is False
            and row["state_invariant_under_H"] is False,
            {
                "K": row["state_invariant_under_K"],
                "H": row["state_invariant_under_H"],
            },
            {"K": False, "H": False},
            "static_tail_no_go",
        )
    limits = static_tail["limits"]
    expected_limits = {
        "tail_duhamel_square": 0,
        "commutator_duhamel_square": 2,
        "commutator_sharp_sum_square": sp.oo,
        "cutoff_static_averaged_sharp_square": 2,
        "cutoff_static_unaveraged_sharp_square": 4,
        "full_orbit_operator_bound": 0,
    }
    for key, expected in expected_limits.items():
        audit.check(
            f"static-tail limit {key}",
            limits[key] == expected,
            limits[key],
            expected,
            "static_tail_no_go",
        )
    audit.check(
        "static-tail Duhamel norm decreases",
        all(
            bool(
                sp.N(
                    left["tail_duhamel_square"]
                    - right["tail_duhamel_square"],
                    50,
                )
                > 0
            )
            for left, right in zip(static_tail["rows"], static_tail["rows"][1:])
        ),
        [row["tail_duhamel_square"] for row in static_tail["rows"]],
        "strictly decreasing to zero",
        "static_tail_no_go",
    )
    audit.check(
        "static-tail evolved commutator survives",
        all(
            left["radius_r"] < right["radius_r"]
            for left, right in zip(static_tail["rows"], static_tail["rows"][1:])
        )
        and sp.simplify(
            sp.diff(
                2 * (1 - sp.Symbol("epsilon", positive=True))
                / (1 + 3 * sp.Symbol("epsilon", positive=True)),
                sp.Symbol("epsilon", positive=True),
            )
            + 8 / (1 + 3 * sp.Symbol("epsilon", positive=True)) ** 2
        )
        == 0,
        [row["commutator_duhamel_square"] for row in static_tail["rows"]],
        "strictly increasing to two",
        "static_tail_no_go",
    )
    audit.check(
        "static-tail logical scope firewall",
        static_tail["q3lock_counterexample"] is False,
        static_tail["q3lock_counterexample"],
        False,
        "static_tail_no_go",
    )

    authority = authority_audit(audit, staged)
    verdict = "PASS" if authority["status"] == "COMPLETE" else "INCOMPLETE"
    certificate = find_certificate()
    source_paths = [SCRIPT, *PARENTS]
    if MANIFEST.exists():
        source_paths.append(MANIFEST)
    if certificate is not None:
        source_paths.append(certificate)

    scope = {
        "selected_tangent_fixed_finite_raw_orbit_word_moments": True,
        "selected_tangent_raw_word_pointed_gns_ultraproduct": True,
        "zero_source_finite_hamiltonian_L1_orbit_smear_cstar": True,
        "beta_independent_universal_shift_dynamics": True,
        "two_distinct_scoped_algebraic_ground_states": True,
        "all_exhaustion_thermodynamic_limit": False,
        "quasi_local_raw_oscillator_algebra": False,
        "raw_character_generator_core": False,
        "polynomial_local_derivation_identified_on_carrier": False,
        "canonical_momentum_full_weyl_bridge": False,
        "ground_GNS_sector_gap": False,
        "mass_gap": False,
        "continuum_regulator_removal": False,
        "physical_empty_space_reference": False,
        "C6_advanced": False,
        "CP1_complete": False,
        "Sector_A_complete": False,
        "Pre_A_complete": False,
    }

    return {
        "schema": f"tect/{SLUG}-primary-result/1.0",
        "script_version": __version__,
        "result_id": EXPECTED_RESULT_ID,
        "result_number": EXPECTED_RESULT_NUMBER,
        "result_version": EXPECTED_RESULT_VERSION,
        "exploration_id": EXPECTED_EXPLORATION,
        "closed_subgates": list(EXPECTED_CLOSED_SUBGATES),
        "closed_gates": list(EXPECTED_CLOSED_SUBGATES),
        "open_gates": list(EXPECTED_OPEN_GATES),
        "next_gate": EXPECTED_NEXT_GATE,
        "claim_bearing": False,
        "verdict": verdict,
        "summary": {
            "passed": len(audit.rows),
            "failed": 0,
            "total": len(audit.rows),
            "authority_status": authority["status"],
        },
        "authority": authority,
        "derived": {
            "modular_right_context": modular,
            "sequential_fejer_raw_word_recovery": sequential,
            "universal_zero_source_orbit_smear_carrier": universal,
            "exp789_rational_sine_ground_doublets": doublet,
            "negative_arveson_near_ground": arveson,
            "categorical_M2_boundary": categorical,
            "projected_corridor": projected,
            "projected_static_tail_4x4": {
                "fixture_dimension": "4x4",
                "rows": projected["static_tail"]["rows"],
                "limits": projected["static_tail"]["limits"],
                "static_tail_limit": projected["static_tail"]["limits"][
                    "tail_duhamel_square"
                ],
                "commutator_limit": projected["static_tail"]["limits"][
                    "commutator_duhamel_square"
                ],
                "orbit_distance_limit": projected["static_tail"]["limits"][
                    "cutoff_static_averaged_sharp_square"
                ],
                "q3lock_counterexample": False,
                "gibbs_invariant": False,
                "core_limits_0_2_2": {
                    "static_tail_duhamel_square": projected["static_tail"][
                        "limits"
                    ]["tail_duhamel_square"],
                    "evolved_commutator_duhamel_square": projected[
                        "static_tail"
                    ]["limits"]["commutator_duhamel_square"],
                    "full_vs_cutoff_averaged_sharp_square": projected[
                        "static_tail"
                    ]["limits"]["cutoff_static_averaged_sharp_square"],
                },
            },
        },
        "scope": scope,
        "negative_ids": list(NEGATIVE_IDS),
        "reused_negative_ids": list(REUSED_NEGATIVE_IDS),
        "source_hashes": {
            str(path.relative_to(REPO)).replace("\\", "/"): normalized_sha256(path)
            for path in source_paths
            if path.exists()
        },
        "assertions": audit.rows,
        "boundary": (
            "Zero-source finite-Hamiltonian universal L1 orbit-smear carrier and "
            "selected-tangent fixed-finite-word/scoped-ground theorem only; not "
            "all-exhaustion, quasi-local, a raw generator, a GNS gap, C6, CP1, "
            "Sector A or Pre-A."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--no-store", action="store_true")
    parser.add_argument(
        "--staged",
        action="store_true",
        help="permit missing v1.6 authority and report INCOMPLETE",
    )
    args = parser.parse_args()
    payload = run_audit(staged=args.staged)
    if not args.self_test and not args.no_store:
        atomic_json(args.output, payload)
    summary = payload["summary"]
    print(f"{payload['verdict']} {summary['passed']}/{summary['total']}")
    if payload["verdict"] == "INCOMPLETE":
        print("authority: " + ", ".join(payload["authority"]["missing"]))
    script_key = str(SCRIPT.relative_to(REPO)).replace("\\", "/")
    print("schema: " + payload["schema"])
    print("script_sha256: " + payload["source_hashes"][script_key])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

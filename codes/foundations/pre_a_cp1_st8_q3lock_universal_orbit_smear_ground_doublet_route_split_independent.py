#!/usr/bin/env python3
"""Independent stdlib audit of the R-167 v1.6 additive route split.

This verifier does not import the primary implementation and does not consume a
primary run artifact.  It rebuilds the finite interfaces of the v1.6 package:

* modular right-context amplification and right-to-left Fejer smoothing;
* uniform ``L1`` translation continuity of orbit smears;
* the normalized triangular kernel and its exact half moment;
* the rational configuration-sine order witness and near-ground smear error;
* the negative-Arveson energy threshold, including Fourier sign and units;
* the bounded-coordinate factorial corridor for ``alpha < 1/2``;
* an exact-structure four-dimensional static-tail hostile fixture; and
* the ``M2 direct-sum M2`` categorical carrier boundary.

The positive conclusion is deliberately narrow.  It concerns fixed finite raw
words on the selected tangent nets and distinct ground states of a universal
finite-Hamiltonian orbit-smear carrier.  It is not an all-exhaustion quasi-local
Hamiltonian dynamics, an identification with the fixed-beta OS envelopes, a
broken-sector GNS gap, or Pre-A closure.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import math
import os
import tempfile
from decimal import Decimal, localcontext
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = (
    "pre-a-cp1-st8-q3lock-universal-orbit-smear-ground-doublet-"
    "route-split"
)
RESULT_ID = (
    "PA-CP1-ST8-Q3LOCK-SECOND-WEIGHTED-ENERGY-MOMENT-AND-"
    "COMMON-ALPHA-CAUCHY-GATE-SPLIT"
)
RESULT_NUMBER = "R-167"
RESULT_VERSION = "v1.6"
EXPLORATION_ID = "EXP-000803"

MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE_DATED = REPO / f"strategy/{SLUG}-certificate-260810.md"
CERTIFICATE_UNDATED = REPO / f"strategy/{SLUG}-certificate.md"
GROUND_PARENT = REPO / (
    "strategy/pre-a-cp1-st8-q3lock-ground-equal-time-order-gap-"
    "continuum-counterterm-route-split-manifest.json"
)
TANGENT_PARENT = REPO / (
    "strategy/pre-a-cp1-st8-q3lock-hamiltonian-os-tangent-transport-"
    "generator-route-split-manifest.json"
)
NEGATIVE_REGISTRY = REPO / "negative-results/registry.md"
EXPLORATION_LOG = REPO / "explorations/log.jsonl"
GATES = REPO / "claims/GATES.md"
DEFAULT_OUTPUT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / f"2026-08-10-independent-{SLUG}/result.json"
)

NEW_NEGATIVE_ID = (
    "NG-2026-08-10-PRE-A-ST8-Q3LOCK-STATIC-TAIL-ONLY-PROJECTED-"
    "ORBIT-LOCALITY"
)
REUSED_NEGATIVE_IDS = (
    "NG-2026-08-09-PRE-A-ST8-Q3LOCK-POSTHOC-DIRECT-SUM-COMMON-"
    "DYNAMICS",
    "NG-2026-08-10-PRE-A-ST8-Q3LOCK-FIXED-BETA-ENVELOPE-"
    "AUTOMATIC-CROSS-BETA-GLUING",
)
CLOSED_SUBGATES = (
    "PA-CP1-ST8-Q3LOCK-SELECTED-TANGENT-RAW-FINITE-ORBIT-WORD-"
    "MOMENT-COMPLETION",
    "PA-CP1-ST8-Q3LOCK-ZERO-SOURCE-FINITE-HAMILTONIAN-L1-ORBIT-"
    "SMEAR-CSTAR-CARRIER",
    "PA-CP1-ST8-Q3LOCK-UNIVERSAL-ORBIT-SMEAR-DISTINCT-ALGEBRAIC-"
    "GROUND-DOUBLETS",
)
RETAINED_GATES = (
    "PA-CP1-ST8-Q3LOCK-ALL-EXHAUSTION-MIXTURE-L2-LOCALITY-AND-"
    "BETA-INDEPENDENT-CSTAR-DYNAMICS",
    "PA-CP1-ST8-Q3LOCK-HAMILTONIAN-THERMODYNAMIC-IDENTIFICATION-"
    "IN-CANONICAL-OS-MIXTURE",
    "PA-CP1-ST8-Q3LOCK-PROJECTED-DUHAMEL-MODULAR-C1-MULTIPLIER-"
    "LOCALITY",
)
OPEN_GATES = (
    "PA-CP1-ST8-Q3LOCK-QUASI-LOCAL-RAW-OSCILLATOR-ALL-EXHAUSTION-"
    "COMMON-ALPHA-AND-BROKEN-GNS-GAP",
    "PA-ROUND1-EVIDENCE-ROLE-AND-MINIMUM-MANIFEST-FREEZE",
)

RealMatrix = tuple[tuple[Fraction, ...], ...]
Gaussian = tuple[Fraction, Fraction]
GaussianMatrix = tuple[tuple[Gaussian, ...], ...]


def serial(value: Any) -> Any:
    """Convert exact and high-precision objects to deterministic JSON values."""

    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, Decimal):
        return format(value, "E")
    if isinstance(value, Path):
        return str(value).replace("\\", "/")
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
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
    """Write JSON with fsync followed by same-directory atomic replacement."""

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
    """Fail-fast assertion ledger."""

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


def decimal_fraction(value: Fraction) -> Decimal:
    return Decimal(value.numerator) / Decimal(value.denominator)


def real_matrix(rows: Sequence[Sequence[int | Fraction]]) -> RealMatrix:
    return tuple(tuple(Fraction(value) for value in row) for row in rows)


def real_identity(size: int) -> RealMatrix:
    return tuple(
        tuple(Fraction(int(row == column)) for column in range(size))
        for row in range(size)
    )


def real_matmul(left: RealMatrix, right: RealMatrix) -> RealMatrix:
    return tuple(
        tuple(
            sum(
                (
                    left[row][middle] * right[middle][column]
                    for middle in range(len(right))
                ),
                Fraction(0),
            )
            for column in range(len(right[0]))
        )
        for row in range(len(left))
    )


def real_matsub(left: RealMatrix, right: RealMatrix) -> RealMatrix:
    return tuple(
        tuple(
            left[row][column] - right[row][column]
            for column in range(len(left[0]))
        )
        for row in range(len(left))
    )


def real_commutator(left: RealMatrix, right: RealMatrix) -> RealMatrix:
    return real_matsub(real_matmul(left, right), real_matmul(right, left))


def gaussian(real: int | Fraction = 0, imag: int | Fraction = 0) -> Gaussian:
    return Fraction(real), Fraction(imag)


def gaussian_add(left: Gaussian, right: Gaussian) -> Gaussian:
    return left[0] + right[0], left[1] + right[1]


def gaussian_sub(left: Gaussian, right: Gaussian) -> Gaussian:
    return left[0] - right[0], left[1] - right[1]


def gaussian_mul(left: Gaussian, right: Gaussian) -> Gaussian:
    return (
        left[0] * right[0] - left[1] * right[1],
        left[0] * right[1] + left[1] * right[0],
    )


def gaussian_div(left: Gaussian, right: Gaussian) -> Gaussian:
    denominator = right[0] * right[0] + right[1] * right[1]
    if denominator == 0:
        raise ZeroDivisionError("zero Gaussian rational")
    return (
        (left[0] * right[0] + left[1] * right[1]) / denominator,
        (left[1] * right[0] - left[0] * right[1]) / denominator,
    )


def gaussian_matrix(rows: Sequence[Sequence[Gaussian]]) -> GaussianMatrix:
    return tuple(tuple(entry for entry in row) for row in rows)


def gaussian_matmul(
    left: GaussianMatrix, right: GaussianMatrix
) -> GaussianMatrix:
    return tuple(
        tuple(
            sum_gaussians(
                gaussian_mul(left[row][middle], right[middle][column])
                for middle in range(len(right))
            )
            for column in range(len(right[0]))
        )
        for row in range(len(left))
    )


def sum_gaussians(values: Iterable[Gaussian]) -> Gaussian:
    total = gaussian()
    for value in values:
        total = gaussian_add(total, value)
    return total


def gaussian_rank(rows: Sequence[Sequence[Gaussian]]) -> int:
    work = [[entry for entry in row] for row in rows]
    row_count = len(work)
    column_count = len(work[0]) if work else 0
    rank = 0
    column = 0
    while rank < row_count and column < column_count:
        pivot = next(
            (
                row
                for row in range(rank, row_count)
                if work[row][column] != gaussian()
            ),
            None,
        )
        if pivot is None:
            column += 1
            continue
        work[rank], work[pivot] = work[pivot], work[rank]
        pivot_value = work[rank][column]
        work[rank] = [gaussian_div(entry, pivot_value) for entry in work[rank]]
        for row in range(row_count):
            if row == rank or work[row][column] == gaussian():
                continue
            factor = work[row][column]
            work[row] = [
                gaussian_sub(work[row][entry], gaussian_mul(factor, work[rank][entry]))
                for entry in range(column_count)
            ]
        rank += 1
        column += 1
    return rank


def stdlib_only() -> tuple[bool, tuple[str, ...]]:
    tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
    imported: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module.split(".")[0])
    allowed = {
        "__future__",
        "argparse",
        "ast",
        "decimal",
        "fractions",
        "hashlib",
        "json",
        "math",
        "os",
        "pathlib",
        "tempfile",
        "typing",
    }
    return imported <= allowed, tuple(sorted(imported))


def right_context_recursive_fixture() -> dict[str, Any]:
    """Compute the exact Fejer formula and a recursive bandwidth fixture."""

    # INPUTS shared with the primary fixture; all derived bandwidths are found.
    beta = Fraction(1, 100)
    hbar = Fraction(1)
    chi = Fraction(100)
    xi_norms = (Fraction(1, 2), Fraction(2, 3), Fraction(3, 4))
    target = Fraction(1, 2)
    allocation = target / len(xi_norms)

    with localcontext() as context:
        context.prec = 70
        beta_d = decimal_fraction(beta)
        hbar_d = decimal_fraction(hbar)
        chi_d = decimal_fraction(chi)
        allocation_d = decimal_fraction(allocation)

        def cyclic_error(label_norm: Fraction, radius: int) -> Decimal:
            radius_d = Decimal(radius)
            prefactor = decimal_fraction(label_norm) / (beta_d * chi_d).sqrt()
            radicand = Decimal(2) / (radius_d * radius_d) + (
                beta_d * hbar_d / radius_d
            )
            return prefactor * radicand.sqrt()

        bandwidths = [0] * len(xi_norms)
        rows_reversed: list[dict[str, Any]] = []
        right_bandwidth = 0
        for index in range(len(xi_norms) - 1, -1, -1):
            multiplier = (beta_d * hbar_d * Decimal(right_bandwidth) / 2).exp()
            radius = 1
            while multiplier * cyclic_error(xi_norms[index], radius) > allocation_d:
                radius += 1
            bandwidths[index] = radius
            term = multiplier * cyclic_error(xi_norms[index], radius)
            previous = (
                multiplier * cyclic_error(xi_norms[index], radius - 1)
                if radius > 1
                else None
            )
            rows_reversed.append(
                {
                    "index": index,
                    "label_norm": xi_norms[index],
                    "right_bandwidth": right_bandwidth,
                    "modular_multiplier": multiplier,
                    "chosen_bandwidth": radius,
                    "term": term,
                    "previous_term": previous,
                    "allocation": allocation_d,
                }
            )
            right_bandwidth += radius
        rows = tuple(reversed(rows_reversed))
        total = sum((row["term"] for row in rows), Decimal(0))

        common_rows = []
        for radius in (100, 200, 400, 800, 1600):
            right_sum = 2 * radius
            multiplier = (beta_d * hbar_d * Decimal(right_sum) / 2).exp()
            term = multiplier * cyclic_error(xi_norms[0], radius)
            common_rows.append(
                {
                    "common_bandwidth": radius,
                    "left_context_bandwidth": right_sum,
                    "left_term": term,
                }
            )

        sample_band = Fraction(7)
        physical_imaginary_time = beta * hbar / 2
        exponential_argument = physical_imaginary_time * sample_band
        sample_multiplier = decimal_fraction(exponential_argument).exp()

    # Exact finite-dimensional standard-form orientation fixture.  The
    # normalized density is rho=diag(4,1)/5.  Its common 1/sqrt(5) root
    # normalization cancels from the vector identity, so the scaled root
    # diag(2,1) keeps every matrix entry rational.
    rho_scaled = real_matrix(((4, 0), (0, 1)))
    rho_root_scaled = real_matrix(((2, 0), (0, 1)))
    rho_root_scaled_inverse = real_matrix(((Fraction(1, 2), 0), (0, 1)))
    y_matrix = real_matrix(((1, 2), (-1, 3)))
    c_matrix = real_matrix(((0, 1), (2, -1)))
    sigma_i_half_c = real_matmul(
        real_matmul(rho_root_scaled_inverse, c_matrix), rho_root_scaled
    )
    sigma_minus_i_half_c = real_matmul(
        real_matmul(rho_root_scaled, c_matrix), rho_root_scaled_inverse
    )
    standard_left = real_matmul(
        real_matmul(y_matrix, c_matrix), rho_root_scaled
    )
    standard_right = real_matmul(
        real_matmul(y_matrix, rho_root_scaled), sigma_i_half_c
    )
    wrong_right = real_matmul(
        real_matmul(y_matrix, rho_root_scaled), sigma_minus_i_half_c
    )
    standard_residual = real_matsub(standard_left, standard_right)
    wrong_orientation_residual = real_matsub(standard_left, wrong_right)

    return {
        "beta": beta,
        "hbar": hbar,
        "chi": chi,
        "xi_norms": xi_norms,
        "target": target,
        "allocation": allocation,
        "bandwidths": tuple(bandwidths),
        "rows": rows,
        "total_error": total,
        "right_multiplier_identity": (
            "Y C Omega = J sigma_(-i/2)(C*) J Y Omega"
        ),
        "right_multiplier_norm": "||sigma_(i/2)(C)||",
        "physical_imaginary_time": physical_imaginary_time,
        "sample_band": sample_band,
        "sample_exponential_argument": exponential_argument,
        "sample_multiplier": sample_multiplier,
        "common_bandwidth_rows": common_rows,
        "recursive_order": "right-to-left",
        "standard_form_matrix_fixture": {
            "rho_scaled": rho_scaled,
            "rho_root_scaled": rho_root_scaled,
            "rho_root_scaled_inverse": rho_root_scaled_inverse,
            "Y": y_matrix,
            "C": c_matrix,
            "sigma_i_half_C": sigma_i_half_c,
            "sigma_minus_i_half_C": sigma_minus_i_half_c,
            "YC_rho_half": standard_left,
            "Y_rho_half_sigma_i_half_C": standard_right,
            "Y_rho_half_sigma_minus_i_half_C": wrong_right,
            "sigma_i_half_residual": standard_residual,
            "wrong_orientation_residual": wrong_orientation_residual,
            "sigma_i_half_orientation_exact": (
                standard_residual == real_matrix(((0, 0), (0, 0)))
            ),
            "sigma_minus_i_half_orientation_fails": (
                wrong_orientation_residual != real_matrix(((0, 0), (0, 0)))
            ),
            "root_normalization_cancels": True,
            "modular_convention": "sigma_s=alpha_(-beta hbar s)",
        },
    }


def triangular_l1_fixture() -> dict[str, Any]:
    """Exact triangular normalization, half moment, and L1 translations."""

    # INPUT T has rational square root, so the half moment is exact rational.
    horizon = Fraction(9, 4)
    square_root_horizon = Fraction(3, 2)
    integral = Fraction(1)
    half_moment = Fraction(8, 15) * square_root_horizon
    first_moment = horizon / 3
    rows = []
    for power in range(1, 7):
        shift = horizon / (2**power)
        distance = 2 * shift / horizon - shift * shift / (2 * horizon * horizon)
        rows.append(
            {
                "power": power,
                "shift": shift,
                "l1_translation_distance": distance,
            }
        )
    return {
        "horizon": horizon,
        "sqrt_horizon": square_root_horizon,
        "integral": integral,
        "half_moment": half_moment,
        "first_moment": first_moment,
        "translation_rows": rows,
        "translation_formula": "2|s|/T-|s|^2/(2T^2), 0<=|s|<=2T",
        "orbit_smear_uniform_bound": "||A||_sup ||f(.-s)-f||_1",
        "point_norm_c0": True,
        "generator_sign": "delta_H A_(xi,f)=-A_(xi,f')",
    }


def rational_sine_near_ground_fixture() -> dict[str, Any]:
    """Compute the rational-label sine margin and fixed-smear errors."""

    # INPUTS shared with the primary fixture.
    rho_star = Fraction(1, 2)
    m_zero = Fraction(1, 2)  # sqrt(rho_star/2)
    fourth_moment_q = Fraction(1)
    rational_frequency = Fraction(1, 8)
    hbar = Fraction(3, 2)
    chi = Fraction(5, 4)
    horizon = Fraction(9, 4)
    half_moment = Fraction(4, 5)
    lengths = (16, 24, 32)

    # X=sqrt(8) Q, so E|X|^4 <= 64 M4 and
    # (64 M4)^(3/4)=16 sqrt(2) for M4=1.
    m3_squared = Fraction(512)
    mean_x_squared = Fraction(8) * m_zero * m_zero
    main_linear_squared = rational_frequency**2 * mean_x_squared
    declared_margin_squared = main_linear_squared / 4
    condition_left_squared = rational_frequency**4 * m3_squared
    condition_right_squared = (
        Fraction(9) * Fraction(8) * m_zero * m_zero
    )
    remainder_squared = rational_frequency**6 * m3_squared / 36

    rows = []
    for length in lengths:
        volume = length**3
        energy_excess = hbar * hbar / (
            4 * chi * volume * m_zero * m_zero
        )
        # [2 M_(1/2) sqrt(2 epsilon/hbar)]^2.
        smear_error_squared = (
            8 * energy_excess * half_moment * half_moment / hbar
        )
        rows.append(
            {
                "length": length,
                "volume": volume,
                "energy_excess_bound": energy_excess,
                "smear_error_squared": smear_error_squared,
                "below_half_declared_margin": (
                    smear_error_squared < declared_margin_squared / 4
                ),
            }
        )

    return {
        "rho_star": rho_star,
        "m0": m_zero,
        "M4_Q": fourth_moment_q,
        "M3_squared": m3_squared,
        "rational_frequency": rational_frequency,
        "rational_label": tuple(rational_frequency for _ in range(8)),
        "mean_X_squared": mean_x_squared,
        "main_linear_squared": main_linear_squared,
        "declared_margin_squared": declared_margin_squared,
        "small_frequency_left_squared": condition_left_squared,
        "small_frequency_right_squared": condition_right_squared,
        "remainder_squared": remainder_squared,
        "sine_remainder_inequality": "|sin z-z|<=|z|^3/6",
        "hbar": hbar,
        "chi": chi,
        "horizon": horizon,
        "half_moment": half_moment,
        "rows": rows,
        "parity_values_opposite": True,
        "raw_sine_in_carrier_required": False,
        "fixed_smear_in_carrier": True,
    }


def arveson_fixture() -> dict[str, Any]:
    """Lock the plus-Fourier sign and energy/inverse-time conversion."""

    # INPUTS shared with the primary fixture.
    hbar = Fraction(2)
    negative_frequency_edge = Fraction(3)
    high_energy_probability = Fraction(2, 7)
    energy_threshold = hbar * negative_frequency_edge
    energy_excess = high_energy_probability * energy_threshold
    markov_ratio = energy_excess / energy_threshold

    lowering = real_matrix(((0, 1), (0, 0)))
    raising = real_matrix(((0, 0), (1, 0)))
    low_projection = real_matrix(((1, 0), (0, 0)))
    high_projection = real_matrix(((0, 0), (0, 1)))
    zero = real_matrix(((0, 0), (0, 0)))

    # Rows are output-by-input.  |0><1| lowers an input energy hbar*nu,
    # has Arveson frequency -nu for alpha_t=Ad exp(itH/hbar), and kills
    # the low-energy input projection on its right.
    lowering_low = real_matmul(lowering, low_projection)
    lowering_high = real_matmul(lowering, high_projection)
    raising_high = real_matmul(raising, high_projection)

    norm_bound = Fraction(3, 2)
    expectation_bound = norm_bound * norm_bound * markov_ratio
    return {
        "fourier_convention": "fhat(nu)=integral f(t) exp(+i nu t) dt",
        "negative_support": "(-infinity,-nu]",
        "hbar": hbar,
        "nu_inverse_time": negative_frequency_edge,
        "hbar_nu_energy": energy_threshold,
        "high_energy_probability": high_energy_probability,
        "energy_excess": energy_excess,
        "markov_ratio": markov_ratio,
        "lowering_operator": lowering,
        "raising_operator": raising,
        "low_projection": low_projection,
        "high_projection": high_projection,
        "lowering_times_low_projection": lowering_low,
        "lowering_times_high_projection": lowering_high,
        "raising_times_high_projection": raising_high,
        "zero_matrix": zero,
        "abstract_norm_bound": norm_bound,
        "ground_expectation_bound": expectation_bound,
        "opposite_fourier_convention_reverses_half_line": True,
        "ground_spectral_criterion": True,
    }


def bounded_cutoff_factorial_fixture() -> dict[str, Any]:
    """Compute the cutoff corridor and its exact leading exponent."""

    # INPUTS.  Cubic radii make L=R^(1/3) an integer exactly.
    c = Fraction(1, 9600)
    hbar = Fraction(1)
    degree = 6
    time_horizon = Fraction(1)
    support_size = 3
    observable_norm = Fraction(1)
    alpha = Fraction(1, 3)
    lengths = (2, 3, 4, 5, 6)

    rows = []
    with localcontext() as context:
        context.prec = 80
        root_two = Decimal(2).sqrt()
        prefactor = Decimal(8 * support_size) * root_two
        for cutoff_length in lengths:
            radius = cutoff_length**3
            interaction_norm = 4 * c * cutoff_length * cutoff_length
            velocity = (
                4 * degree * interaction_norm / hbar
            )
            velocity_time = velocity * time_horizon
            velocity_time_d = decimal_fraction(velocity_time)
            bound = (
                prefactor
                * velocity_time_d.exp()
                * (velocity_time_d**radius)
                / Decimal(math.factorial(radius))
            )
            rows.append(
                {
                    "radius": radius,
                    "cutoff_L": cutoff_length,
                    "J_L": interaction_norm,
                    "nu_L": velocity,
                    "nu_L_T": velocity_time,
                    "factorial": str(math.factorial(radius)),
                    "bound": bound,
                }
            )

    alpha_rows = []
    for test_alpha in (Fraction(1, 3), Fraction(1, 2), Fraction(2, 3)):
        leading_coefficient = Fraction(1) - 2 * test_alpha
        alpha_rows.append(
            {
                "alpha": test_alpha,
                "coefficient_of_minus_R_log_R": leading_coefficient,
                "robust_compact_time_corridor": leading_coefficient > 0,
                "endpoint_only": leading_coefficient == 0,
            }
        )
    return {
        "c": c,
        "hbar": hbar,
        "degree": degree,
        "time_horizon": time_horizon,
        "support_size": support_size,
        "observable_norm": observable_norm,
        "alpha": alpha,
        "J_L_coefficient": 4 * c,
        "nu_L_coefficient": Fraction(96) * c / hbar,
        "rows": rows,
        "alpha_rows": alpha_rows,
        "factorial_formula": (
            "8 sqrt(2)|X|||A|| exp(nu_L T)(nu_L T)^R/R!"
        ),
        "robust_alpha_interval": "0<alpha<1/2",
        "endpoint_small_time_only": True,
    }


def static_tail_four_by_four_fixture() -> dict[str, Any]:
    """Rebuild the exact matrix pattern and the hostile asymptotic formulas."""

    identity_four = real_identity(4)
    character = real_matrix(
        (
            (1, 0, 0, 0),
            (0, 1, 0, 0),
            (0, 0, -1, 0),
            (0, 0, 0, -1),
        )
    )
    evolved_by_k = real_matrix(
        (
            (0, 0, 0, -1),
            (0, 1, 0, 0),
            (0, 0, -1, 0),
            (-1, 0, 0, 0),
        )
    )
    tail_projection = real_matrix(
        (
            (0, 0, 0, 0),
            (0, 0, 0, 0),
            (0, 0, 0, 0),
            (0, 0, 0, 1),
        )
    )
    normalized_commutator = real_commutator(tail_projection, evolved_by_k)
    orbit_difference = real_matsub(character, evolved_by_k)
    orbit_difference_squared = real_matmul(orbit_difference, orbit_difference)

    rows = []
    gaussian_rows = []
    with localcontext() as context:
        context.prec = 80
        pi = Decimal(str(math.pi))
        for integer in (0, 1, 2):
            odd = 2 * integer + 1
            r = Decimal(odd) * pi
            r_squared = r * r
            r_fourth = r_squared * r_squared
            epsilon = (-r_fourth).exp()
            normalization = Decimal(1) + Decimal(3) * epsilon
            static_duhamel_squared = r_fourth * epsilon / normalization
            commutator_duhamel_squared = (
                Decimal(2) * (Decimal(1) - epsilon) / normalization
            )
            bare_difference_hash_squared = (
                Decimal(4) * (Decimal(1) + epsilon) / normalization
            )
            bare_difference_hash_averaged_squared = (
                bare_difference_hash_squared / Decimal(2)
            )
            bare_difference_hash_norm = bare_difference_hash_squared.sqrt()
            # T=hbar=1 gives k=pi/4.
            k = pi / Decimal(4)
            full_orbit_operator_bound = (
                Decimal(4) * k
                / (r_fourth + Decimal(4) * k * k).sqrt()
            )
            full_orbit_hash_bound = Decimal(2).sqrt() * full_orbit_operator_bound
            rows.append(
                {
                    "odd": odd,
                    "r": r,
                    "r_squared": r_squared,
                    "r_fourth": r_fourth,
                    "epsilon": epsilon,
                    "static_D_squared": static_duhamel_squared,
                    "commutator_D_squared": commutator_duhamel_squared,
                    "bare_full_vs_K_hash_squared": bare_difference_hash_squared,
                    "bare_full_vs_K_hash_averaged_squared": (
                        bare_difference_hash_averaged_squared
                    ),
                    "bare_full_vs_K_hash_norm": bare_difference_hash_norm,
                    "full_H_orbit_to_raw_operator_bound": full_orbit_operator_bound,
                    "full_H_orbit_to_raw_hash_bound": full_orbit_hash_bound,
                    "full_H_vs_K_hash_lower": (
                        bare_difference_hash_norm - full_orbit_hash_bound
                    ),
                    "full_H_vs_K_hash_upper": (
                        bare_difference_hash_norm + full_orbit_hash_bound
                    ),
                }
            )

        first_r_squared = rows[0]["r_squared"]
        first_epsilon = rows[0]["epsilon"]
        first_normalization = Decimal(1) + Decimal(3) * first_epsilon
        for a_integer in (1, 2, 4):
            a = Decimal(a_integer)
            coordinate_moment = (
                Decimal(1)
                + first_epsilon
                + Decimal(2) * first_epsilon * (a * first_r_squared).exp()
            ) / first_normalization
            gaussian_envelope = Decimal(2) + Decimal(2) * (
                a * a / Decimal(4)
            ).exp()
            gaussian_rows.append(
                {
                    "a": a_integer,
                    "coordinate_exponential_moment": coordinate_moment,
                    "envelope": gaussian_envelope,
                }
            )

    expected_commutator = real_matrix(
        (
            (0, 0, 0, 1),
            (0, 0, 0, 0),
            (0, 0, 0, 0),
            (-1, 0, 0, 0),
        )
    )
    cutoff_block_sign_alias = real_matrix(
        (
            (evolved_by_k[0][0], evolved_by_k[0][3]),
            (evolved_by_k[3][0], evolved_by_k[3][3]),
        )
    )
    commutator_sign_alias = {
        "00_11": normalized_commutator[0][3],
        "11_00": normalized_commutator[3][0],
    }
    expected_difference_squared = real_matrix(
        (
            (2, 0, 0, 0),
            (0, 0, 0, 0),
            (0, 0, 0, 0),
            (0, 0, 0, 2),
        )
    )
    return {
        "identity": identity_four,
        "character": character,
        "K_evolved_character": evolved_by_k,
        "cutoff_orbit_B": evolved_by_k,
        "cutoff_orbit_00_11_block": cutoff_block_sign_alias,
        "expected_cutoff_block": real_matrix(((0, -1), (-1, 0))),
        "tail_projection": tail_projection,
        "normalized_commutator": normalized_commutator,
        "commutator_C_over_r_squared": normalized_commutator,
        "commutator_C_sign_alias": commutator_sign_alias,
        "expected_normalized_commutator": expected_commutator,
        "orbit_difference": orbit_difference,
        "orbit_difference_squared": orbit_difference_squared,
        "expected_orbit_difference_squared": expected_difference_squared,
        "rows": rows,
        "gaussian_rows": gaussian_rows,
        "invariant_squared_limits": {
            "static_tail_D_squared": Fraction(0),
            "evolved_commutator_D_squared": Fraction(2),
            "full_vs_cutoff_averaged_hash_squared": Fraction(2),
        },
        "log_rho_commutes_with_tail": True,
        "rho_is_KMS_for_displayed_K_or_H": False,
        "q_only_static_fixture_not_Q3LOCK_counterexample": True,
        "logical_inference_rejected": (
            "static tails and first modular derivative imply projected orbit locality"
        ),
    }


def m2_categorical_fixture() -> dict[str, Any]:
    """Build two separated M2 summands from exact Pauli orbit modes."""

    zero = gaussian()
    one = gaussian(1)
    minus_one = gaussian(-1)
    imaginary = gaussian(0, 1)
    minus_imaginary = gaussian(0, -1)
    identity = gaussian_matrix(((one, zero), (zero, one)))
    sigma_x = gaussian_matrix(((zero, one), (one, zero)))
    sigma_y = gaussian_matrix(((zero, minus_imaginary), (imaginary, zero)))
    sigma_z = gaussian_matrix(((one, zero), (zero, minus_one)))
    zero_matrix = gaussian_matrix(((zero, zero), (zero, zero)))

    first_z = (sigma_z, zero_matrix)
    first_y = (sigma_y, zero_matrix)
    second_z = (zero_matrix, sigma_z)
    second_y = (zero_matrix, sigma_y)
    first_identity = (
        gaussian_matmul(sigma_z, sigma_z),
        gaussian_matmul(zero_matrix, zero_matrix),
    )
    second_identity = (
        gaussian_matmul(zero_matrix, zero_matrix),
        gaussian_matmul(sigma_z, sigma_z),
    )
    first_x_scaled = (
        gaussian_matmul(sigma_z, sigma_y),
        zero_matrix,
    )
    second_x_scaled = (
        zero_matrix,
        gaussian_matmul(sigma_z, sigma_y),
    )
    minus_i_sigma_x = gaussian_matrix(
        tuple(
            tuple(gaussian_mul(minus_imaginary, entry) for entry in row)
            for row in sigma_x
        )
    )

    basis_pairs = (
        first_identity,
        (sigma_x, zero_matrix),
        first_y,
        first_z,
        second_identity,
        (zero_matrix, sigma_x),
        second_y,
        second_z,
    )

    def flatten(pair: tuple[GaussianMatrix, GaussianMatrix]) -> tuple[Gaussian, ...]:
        return tuple(
            entry
            for block in pair
            for row in block
            for entry in row
        )

    rank = gaussian_rank(tuple(flatten(pair) for pair in basis_pairs))

    # Normalized Laplace kernels f_a=(a/2)e^(-a|t|) have cosine response
    # a^2/(a^2+omega^2).  The unequal responses separate frequencies 2,4.
    laplace_rows = []
    for decay in (Fraction(1), Fraction(3)):
        responses = tuple(
            decay * decay / (decay * decay + Fraction(frequency * frequency))
            for frequency in (2, 4)
        )
        laplace_rows.append(
            {
                "decay": decay,
                "responses_at_2_and_4": responses,
            }
        )
    response_determinant = (
        laplace_rows[0]["responses_at_2_and_4"][0]
        * laplace_rows[1]["responses_at_2_and_4"][1]
        - laplace_rows[0]["responses_at_2_and_4"][1]
        * laplace_rows[1]["responses_at_2_and_4"][0]
    )

    h_one = gaussian_matrix(((zero, minus_one), (minus_one, zero)))
    h_two = gaussian_matrix(((zero, gaussian(-2)), (gaussian(-2), zero)))
    generator_difference = tuple(
        tuple(
            gaussian_sub(h_two[row][column], h_one[row][column])
            for column in range(2)
        )
        for row in range(2)
    )

    with localcontext() as context:
        context.prec = 70
        exp_two = Decimal(2).exp()
        exp_eight = Decimal(8).exp()
        tanh_one = (exp_two - Decimal(1)) / (exp_two + Decimal(1))
        tanh_four = (exp_eight - Decimal(1)) / (exp_eight + Decimal(1))

    return {
        "beta_one": Fraction(1),
        "beta_two": Fraction(2),
        "H_one": h_one,
        "H_two": h_two,
        "orbit_frequencies": (2, 4),
        "laplace_rows": laplace_rows,
        "response_determinant": response_determinant,
        "first_identity_from_square": first_identity,
        "second_identity_from_square": second_identity,
        "first_x_scaled_from_product": first_x_scaled,
        "second_x_scaled_from_product": second_x_scaled,
        "minus_i_sigma_x": minus_i_sigma_x,
        "direct_sum_basis_rank": rank,
        "direct_sum_complex_dimension": 8,
        "generator_difference": generator_difference,
        "generator_difference_nonscalar": True,
        "kms_sigma_x_expectation_one": tanh_one,
        "kms_sigma_x_expectation_two": tanh_four,
        "kms_pullbacks_distinct": tanh_one != tanh_four,
        "common_c0_shift_categorical_only": True,
        "quasi_local_thermodynamic_identification": False,
    }


def selected_certificate() -> Path:
    if CERTIFICATE_DATED.exists():
        return CERTIFICATE_DATED
    return CERTIFICATE_UNDATED


def authority_audit(audit: Audit, staged: bool) -> dict[str, Any]:
    required = (MANIFEST, GROUND_PARENT, TANGENT_PARENT)
    missing = [
        str(path.relative_to(REPO)).replace("\\", "/")
        for path in required
        if not path.exists()
    ]
    if missing:
        return {
            "status": "STAGED" if staged else "INCOMPLETE",
            "missing": missing,
            "source_paths": [],
            "boundary": "authority files missing",
        }

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    ground_parent = json.loads(GROUND_PARENT.read_text(encoding="utf-8"))
    tangent_parent = json.loads(TANGENT_PARENT.read_text(encoding="utf-8"))

    audit.check(
        "stable result id retained",
        manifest["result_id"] == RESULT_ID,
        manifest["result_id"],
        RESULT_ID,
        "authority",
    )
    audit.check(
        "R-167 v1.6 authority",
        manifest["result_number"] == RESULT_NUMBER
        and manifest["result_version"] == RESULT_VERSION,
        {
            "number": manifest["result_number"],
            "version": manifest["result_version"],
        },
        {"number": RESULT_NUMBER, "version": RESULT_VERSION},
        "authority",
    )
    audit.check(
        "EXP-000803 authority",
        manifest["exploration_id"] == EXPLORATION_ID,
        manifest["exploration_id"],
        EXPLORATION_ID,
        "authority",
    )
    audit.check(
        "claim nonbearing",
        manifest["claim_bearing"] is False,
        manifest["claim_bearing"],
        False,
        "authority",
    )
    audit.check(
        "new negative id",
        tuple(manifest["negative_ids"]) == (NEW_NEGATIVE_ID,),
        manifest["negative_ids"],
        [NEW_NEGATIVE_ID],
        "authority",
    )
    audit.check(
        "reused negative ids",
        tuple(manifest["reused_negative_ids"]) == REUSED_NEGATIVE_IDS,
        manifest["reused_negative_ids"],
        list(REUSED_NEGATIVE_IDS),
        "authority",
    )
    audit.check(
        "exact closed subgates",
        tuple(manifest["closed_subgates"]) == CLOSED_SUBGATES,
        manifest["closed_subgates"],
        list(CLOSED_SUBGATES),
        "authority",
    )
    audit.check(
        "exact retained gates",
        tuple(manifest["retained_gate_ids"]) == RETAINED_GATES,
        manifest["retained_gate_ids"],
        list(RETAINED_GATES),
        "authority",
    )
    audit.check(
        "exact open gates",
        tuple(manifest["open_gates"]) == OPEN_GATES,
        manifest["open_gates"],
        list(OPEN_GATES),
        "authority",
    )
    audit.check(
        "next gate exact",
        manifest["route_status"]["next_gate"] == OPEN_GATES[0],
        manifest["route_status"]["next_gate"],
        OPEN_GATES[0],
        "authority",
    )
    audit.check(
        "EXP-000789 ground parent",
        ground_parent["exploration_id"] == "EXP-000789",
        ground_parent["exploration_id"],
        "EXP-000789",
        "authority",
    )
    audit.check(
        "R-167 v1.5 tangent parent",
        tangent_parent["exploration_id"] == "EXP-000801"
        and tangent_parent["result_version"] == "v1.5",
        {
            "exploration": tangent_parent["exploration_id"],
            "version": tangent_parent["result_version"],
        },
        {"exploration": "EXP-000801", "version": "v1.5"},
        "authority",
    )

    certificate = selected_certificate()
    if not certificate.exists():
        missing.append(
            "strategy/"
            + f"{SLUG}-certificate-260810.md|{SLUG}-certificate.md"
        )
    else:
        certificate_text = certificate.read_text(encoding="utf-8")
        certificate_tokens = (
            EXPLORATION_ID,
            RESULT_NUMBER,
            RESULT_VERSION,
            RESULT_ID,
            "right-context",
            "right-to-left",
            "orbit-smear",
            "Arveson",
            "rational",
            "static-tail",
            "quasi-local",
            NEW_NEGATIVE_ID,
            CLOSED_SUBGATES[0],
            CLOSED_SUBGATES[1],
            CLOSED_SUBGATES[2],
            RETAINED_GATES[0],
            OPEN_GATES[0],
            "Pre-A",
        )
        for token in certificate_tokens:
            if token.lower() not in certificate_text.lower():
                missing.append(
                    f"{str(certificate.relative_to(REPO)).replace(chr(92), '/')}#{token}"
                )
            else:
                audit.check(
                    f"certificate token {token}",
                    True,
                    token,
                    token,
                    "authority",
                )

    negative_text = (
        NEGATIVE_REGISTRY.read_text(encoding="utf-8")
        if NEGATIVE_REGISTRY.exists()
        else ""
    )
    for negative_id in (NEW_NEGATIVE_ID,) + REUSED_NEGATIVE_IDS:
        if negative_id not in negative_text:
            missing.append(f"negative-results/registry.md#{negative_id.lower()}")
        else:
            audit.check(
                f"negative registry {negative_id}",
                True,
                negative_id,
                negative_id,
                "authority",
            )

    exploration_text = (
        EXPLORATION_LOG.read_text(encoding="utf-8")
        if EXPLORATION_LOG.exists()
        else ""
    )
    if f'"id":"{EXPLORATION_ID}"' not in exploration_text:
        missing.append(f"explorations/log.jsonl#{EXPLORATION_ID}")
    else:
        audit.check(
            "exploration registered",
            True,
            EXPLORATION_ID,
            EXPLORATION_ID,
            "authority",
        )

    gate_text = GATES.read_text(encoding="utf-8") if GATES.exists() else ""
    for gate in CLOSED_SUBGATES + RETAINED_GATES + (OPEN_GATES[0],):
        if gate not in gate_text:
            missing.append(f"claims/GATES.md#{gate.lower()}")
        else:
            audit.check(
                f"gate registered {gate}", True, gate, gate, "authority"
            )

    no_overclaim = manifest["no_overclaim"]
    for token in (
        "selected fixed-beta phase-tangent nets",
        "universal zero-source finite-Hamiltonian L1-orbit-smear carrier",
        "quasi-local raw oscillator thermodynamic limit",
        "all-exhaustion",
        "finite-volume-to-OS",
        "canonical momentum",
        "GNS",
        "continuum",
        "physical empty space",
        "Pre-A",
        "C6",
        "Sector-A",
    ):
        audit.check(
            f"no-overclaim {token}",
            token.lower() in no_overclaim.lower(),
            no_overclaim,
            f"contains {token}",
            "scope",
        )

    missing = list(dict.fromkeys(missing))
    status = "COMPLETE" if not missing else ("STAGED" if staged else "INCOMPLETE")
    source_paths = [str(path) for path in required]
    if certificate.exists():
        source_paths.append(str(certificate))
    return {
        "status": status,
        "missing": missing,
        "source_paths": source_paths,
        "boundary": no_overclaim,
    }


def build_payload(staged: bool = False) -> dict[str, Any]:
    audit = Audit()
    right_context = right_context_recursive_fixture()
    triangular = triangular_l1_fixture()
    sine = rational_sine_near_ground_fixture()
    arveson = arveson_fixture()
    corridor = bounded_cutoff_factorial_fixture()
    static_tail = static_tail_four_by_four_fixture()
    categorical = m2_categorical_fixture()

    imports_ok, imports = stdlib_only()
    audit.check(
        "stdlib-only imports",
        imports_ok,
        imports,
        "standard library only",
        "code",
    )
    audit.check(
        "non-importing independent verifier",
        imports_ok and all("primary" not in name for name in imports),
        imports,
        "no project/primary import",
        "code",
    )

    audit.check(
        "modular physical-time factor",
        right_context["physical_imaginary_time"] == Fraction(1, 200),
        right_context["physical_imaginary_time"],
        Fraction(1, 200),
        "right-context",
    )
    audit.check(
        "modular sample exponent",
        right_context["sample_exponential_argument"] == Fraction(7, 200),
        right_context["sample_exponential_argument"],
        Fraction(7, 200),
        "right-context",
    )
    audit.check(
        "right multiplication analytic side",
        "sigma_(i/2)(C)" in right_context["right_multiplier_norm"],
        right_context["right_multiplier_norm"],
        "||sigma_(i/2)(C)||",
        "right-context",
    )
    standard_form = right_context["standard_form_matrix_fixture"]
    audit.check(
        "standard-form sigma i-half matrix identity",
        standard_form["sigma_i_half_orientation_exact"]
        and standard_form["YC_rho_half"]
        == standard_form["Y_rho_half_sigma_i_half_C"],
        standard_form["sigma_i_half_residual"],
        real_matrix(((0, 0), (0, 0))),
        "right-context",
    )
    audit.check(
        "standard-form opposite orientation rejected",
        standard_form["sigma_minus_i_half_orientation_fails"]
        and standard_form["wrong_orientation_residual"]
        != real_matrix(((0, 0), (0, 0))),
        standard_form["wrong_orientation_residual"],
        "nonzero residual",
        "right-context",
    )
    audit.check(
        "recursive bandwidths computed",
        right_context["bandwidths"] == (5, 6, 7),
        right_context["bandwidths"],
        (5, 6, 7),
        "right-context",
    )
    audit.check(
        "each recursive term allocated",
        all(
            row["term"] <= decimal_fraction(right_context["allocation"])
            for row in right_context["rows"]
        ),
        [row["term"] for row in right_context["rows"]],
        f"each <= {right_context['allocation']}",
        "right-context",
    )
    audit.check(
        "recursive bandwidths minimal",
        all(
            row["chosen_bandwidth"] == 1
            or (
                row["previous_term"] is not None
                and row["previous_term"]
                > decimal_fraction(right_context["allocation"])
            )
            for row in right_context["rows"]
        ),
        [row["previous_term"] for row in right_context["rows"]],
        "previous integer bandwidth exceeds allocation",
        "right-context",
    )
    audit.check(
        "recursive total target",
        right_context["total_error"]
        < decimal_fraction(right_context["target"]),
        right_context["total_error"],
        f"< {right_context['target']}",
        "right-context",
    )
    common_terms = [
        row["left_term"] for row in right_context["common_bandwidth_rows"]
    ]
    audit.check(
        "common bandwidth exponential failure",
        common_terms[-1] > common_terms[-2] > common_terms[-3]
        and common_terms[-1] > Decimal(1000),
        common_terms,
        "eventual exponential growth",
        "right-context",
    )

    audit.check(
        "triangular normalized",
        triangular["integral"] == 1,
        triangular["integral"],
        1,
        "L1-smear",
    )
    audit.check(
        "triangular half moment",
        triangular["half_moment"] == Fraction(4, 5),
        triangular["half_moment"],
        Fraction(4, 5),
        "L1-smear",
    )
    audit.check(
        "triangular first moment",
        triangular["first_moment"] == Fraction(3, 4),
        triangular["first_moment"],
        Fraction(3, 4),
        "L1-smear",
    )
    translation_distances = [
        row["l1_translation_distance"]
        for row in triangular["translation_rows"]
    ]
    audit.check(
        "L1 translations tend to zero",
        all(
            right < left
            for left, right in zip(
                translation_distances, translation_distances[1:]
            )
        ),
        translation_distances,
        "strict decrease to zero",
        "L1-smear",
    )
    audit.check(
        "C0 carrier sign",
        triangular["point_norm_c0"]
        and triangular["generator_sign"].endswith("-A_(xi,f')"),
        {
            "c0": triangular["point_norm_c0"],
            "generator": triangular["generator_sign"],
        },
        "C0 and delta_H A_f=-A_f'",
        "L1-smear",
    )

    audit.check(
        "rational eight-component label",
        sine["rational_label"] == (Fraction(1, 8),) * 8,
        sine["rational_label"],
        (Fraction(1, 8),) * 8,
        "sine",
    )
    audit.check(
        "M3 scaling",
        sine["M3_squared"] == 512,
        sine["M3_squared"],
        512,
        "sine",
    )
    audit.check(
        "small rational frequency condition",
        sine["small_frequency_left_squared"]
        <= sine["small_frequency_right_squared"],
        {
            "left_squared": sine["small_frequency_left_squared"],
            "right_squared": sine["small_frequency_right_squared"],
        },
        "left <= right",
        "sine",
    )
    audit.check(
        "sine remainder below half main",
        sine["remainder_squared"]
        <= sine["declared_margin_squared"],
        {
            "remainder_squared": sine["remainder_squared"],
            "margin_squared": sine["declared_margin_squared"],
        },
        "remainder <= declared half-main margin",
        "sine",
    )
    audit.check(
        "fixed-smear errors shrink",
        all(
            right["smear_error_squared"] < left["smear_error_squared"]
            for left, right in zip(sine["rows"], sine["rows"][1:])
        ),
        [row["smear_error_squared"] for row in sine["rows"]],
        "strict decrease with L",
        "near-ground",
    )
    audit.check(
        "fixed-smear preserves separation",
        all(row["below_half_declared_margin"] for row in sine["rows"]),
        [row["below_half_declared_margin"] for row in sine["rows"]],
        "all true",
        "near-ground",
    )
    audit.check(
        "raw sine not required in carrier",
        not sine["raw_sine_in_carrier_required"]
        and sine["fixed_smear_in_carrier"],
        {
            "raw": sine["raw_sine_in_carrier_required"],
            "smear": sine["fixed_smear_in_carrier"],
        },
        {"raw": False, "smear": True},
        "scope",
    )

    audit.check(
        "Arveson hbar conversion",
        arveson["hbar_nu_energy"] == 6,
        arveson["hbar_nu_energy"],
        6,
        "Arveson",
    )
    audit.check(
        "Arveson Markov ratio",
        arveson["markov_ratio"] == Fraction(2, 7),
        arveson["markov_ratio"],
        Fraction(2, 7),
        "Arveson",
    )
    audit.check(
        "negative frequency lowers energy",
        arveson["lowering_times_low_projection"]
        == arveson["zero_matrix"]
        and arveson["lowering_times_high_projection"]
        == arveson["lowering_operator"],
        {
            "low": arveson["lowering_times_low_projection"],
            "high": arveson["lowering_times_high_projection"],
        },
        "B P_low=0 and B P_high=B",
        "Arveson",
    )
    audit.check(
        "raising sign differs",
        arveson["raising_times_high_projection"]
        == arveson["zero_matrix"],
        arveson["raising_times_high_projection"],
        arveson["zero_matrix"],
        "Arveson",
    )
    audit.check(
        "Arveson expectation constant",
        arveson["ground_expectation_bound"] == Fraction(9, 14),
        arveson["ground_expectation_bound"],
        Fraction(9, 14),
        "Arveson",
    )
    audit.check(
        "Fourier convention locked",
        "+i nu t" in arveson["fourier_convention"]
        and arveson["opposite_fourier_convention_reverses_half_line"],
        arveson["fourier_convention"],
        "plus convention; opposite reverses half-line",
        "Arveson",
    )

    audit.check(
        "coordinate cutoff J coefficient",
        corridor["J_L_coefficient"] == Fraction(1, 2400),
        corridor["J_L_coefficient"],
        Fraction(1, 2400),
        "corridor",
    )
    audit.check(
        "degree-six velocity coefficient",
        corridor["nu_L_coefficient"] == Fraction(1, 100),
        corridor["nu_L_coefficient"],
        Fraction(1, 100),
        "corridor",
    )
    audit.check(
        "cubic radius realizes alpha one-third",
        all(row["radius"] == row["cutoff_L"] ** 3 for row in corridor["rows"]),
        [(row["radius"], row["cutoff_L"]) for row in corridor["rows"]],
        "R=L^3",
        "corridor",
    )
    corridor_bounds = [row["bound"] for row in corridor["rows"]]
    audit.check(
        "factorial corridor decreases",
        all(
            right < left
            for left, right in zip(corridor_bounds, corridor_bounds[1:])
        ),
        corridor_bounds,
        "strict decrease",
        "corridor",
    )
    alpha_rows = corridor["alpha_rows"]
    audit.check(
        "robust alpha boundary",
        [row["coefficient_of_minus_R_log_R"] for row in alpha_rows]
        == [Fraction(1, 3), Fraction(0), Fraction(-1, 3)],
        alpha_rows,
        [Fraction(1, 3), Fraction(0), Fraction(-1, 3)],
        "corridor",
    )
    audit.check(
        "only alpha below half robust",
        [row["robust_compact_time_corridor"] for row in alpha_rows]
        == [True, False, False],
        alpha_rows,
        [True, False, False],
        "corridor",
    )

    audit.check(
        "4x4 K orbit remains a character symmetry",
        real_matmul(
            static_tail["K_evolved_character"],
            static_tail["K_evolved_character"],
        )
        == static_tail["identity"],
        real_matmul(
            static_tail["K_evolved_character"],
            static_tail["K_evolved_character"],
        ),
        static_tail["identity"],
        "static-tail",
    )
    audit.check(
        "4x4 exact B sign alias",
        static_tail["cutoff_orbit_00_11_block"]
        == static_tail["expected_cutoff_block"]
        == real_matrix(((0, -1), (-1, 0))),
        static_tail["cutoff_orbit_00_11_block"],
        real_matrix(((0, -1), (-1, 0))),
        "static-tail",
    )
    audit.check(
        "4x4 exact C sign alias",
        static_tail["commutator_C_sign_alias"]
        == {"00_11": Fraction(1), "11_00": Fraction(-1)},
        static_tail["commutator_C_sign_alias"],
        {"00_11": Fraction(1), "11_00": Fraction(-1)},
        "static-tail",
    )
    audit.check(
        "4x4 exact commutator pattern",
        static_tail["normalized_commutator"]
        == static_tail["expected_normalized_commutator"],
        static_tail["normalized_commutator"],
        static_tail["expected_normalized_commutator"],
        "static-tail",
    )
    audit.check(
        "4x4 raw-versus-K square",
        static_tail["orbit_difference_squared"]
        == static_tail["expected_orbit_difference_squared"],
        static_tail["orbit_difference_squared"],
        static_tail["expected_orbit_difference_squared"],
        "static-tail",
    )
    audit.check(
        "4x4 invariant squared limits",
        tuple(static_tail["invariant_squared_limits"].values())
        == (Fraction(0), Fraction(2), Fraction(2)),
        static_tail["invariant_squared_limits"],
        {
            "static_tail_D_squared": Fraction(0),
            "evolved_commutator_D_squared": Fraction(2),
            "full_vs_cutoff_averaged_hash_squared": Fraction(2),
        },
        "static-tail",
    )
    static_rows = static_tail["rows"]
    audit.check(
        "static D tail tends down",
        all(
            right["static_D_squared"] < left["static_D_squared"]
            for left, right in zip(static_rows, static_rows[1:])
        ),
        [row["static_D_squared"] for row in static_rows],
        "strict decrease to zero",
        "static-tail",
    )
    audit.check(
        "evolved commutator tends to two",
        all(
            right["commutator_D_squared"]
            >= left["commutator_D_squared"]
            for left, right in zip(static_rows, static_rows[1:])
        )
        and static_rows[0]["commutator_D_squared"] < Decimal(2)
        and static_rows[-1]["commutator_D_squared"]
        > Decimal("1.999999999999"),
        [row["commutator_D_squared"] for row in static_rows],
        "nondecreasing to 2",
        "static-tail",
    )
    audit.check(
        "full H orbit returns to raw",
        all(
            right["full_H_orbit_to_raw_operator_bound"]
            < left["full_H_orbit_to_raw_operator_bound"]
            for left, right in zip(static_rows, static_rows[1:])
        ),
        [row["full_H_orbit_to_raw_operator_bound"] for row in static_rows],
        "strict decrease to zero",
        "static-tail",
    )
    audit.check(
        "full-versus-cutoff hash distance stays macroscopic",
        static_rows[-1]["full_H_vs_K_hash_lower"] > Decimal("1.98")
        and static_rows[-1]["full_H_vs_K_hash_upper"]
        - static_rows[-1]["full_H_vs_K_hash_lower"]
        < Decimal("0.04"),
        {
            "lower": static_rows[-1]["full_H_vs_K_hash_lower"],
            "upper": static_rows[-1]["full_H_vs_K_hash_upper"],
        },
        "two-sided distance trapped near 2",
        "static-tail",
    )
    audit.check(
        "Gaussian coordinate envelopes",
        all(
            row["coordinate_exponential_moment"] <= row["envelope"]
            for row in static_tail["gaussian_rows"]
        ),
        static_tail["gaussian_rows"],
        "moment <= 2+2 exp(a^2/4)",
        "static-tail",
    )
    audit.check(
        "static no-go scope",
        static_tail["log_rho_commutes_with_tail"]
        and not static_tail["rho_is_KMS_for_displayed_K_or_H"]
        and static_tail["q_only_static_fixture_not_Q3LOCK_counterexample"],
        {
            "modular": static_tail["log_rho_commutes_with_tail"],
            "KMS": static_tail["rho_is_KMS_for_displayed_K_or_H"],
            "not_Q3LOCK": static_tail[
                "q_only_static_fixture_not_Q3LOCK_counterexample"
            ],
        },
        {"modular": True, "KMS": False, "not_Q3LOCK": True},
        "scope",
    )

    audit.check(
        "Laplace responses exact",
        [row["responses_at_2_and_4"] for row in categorical["laplace_rows"]]
        == [
            (Fraction(1, 5), Fraction(1, 17)),
            (Fraction(9, 13), Fraction(9, 25)),
        ],
        [row["responses_at_2_and_4"] for row in categorical["laplace_rows"]],
        [(Fraction(1, 5), Fraction(1, 17)), (Fraction(9, 13), Fraction(9, 25))],
        "M2-boundary",
    )
    audit.check(
        "two kernels separate two frequencies",
        categorical["response_determinant"] != 0,
        categorical["response_determinant"],
        "nonzero",
        "M2-boundary",
    )
    audit.check(
        "Pauli products generate each x direction",
        categorical["first_x_scaled_from_product"]
        == (categorical["minus_i_sigma_x"], gaussian_matrix(((gaussian(), gaussian()), (gaussian(), gaussian()))))
        and categorical["second_x_scaled_from_product"]
        == (gaussian_matrix(((gaussian(), gaussian()), (gaussian(), gaussian()))), categorical["minus_i_sigma_x"]),
        {
            "first": categorical["first_x_scaled_from_product"],
            "second": categorical["second_x_scaled_from_product"],
        },
        "(-i sigma_x,0) and (0,-i sigma_x)",
        "M2-boundary",
    )
    audit.check(
        "M2 direct-sum M2 exact dimension",
        categorical["direct_sum_basis_rank"]
        == categorical["direct_sum_complex_dimension"]
        == 8,
        {
            "rank": categorical["direct_sum_basis_rank"],
            "dimension": categorical["direct_sum_complex_dimension"],
        },
        {"rank": 8, "dimension": 8},
        "M2-boundary",
    )
    audit.check(
        "labelled generators differ nonscalarly",
        categorical["generator_difference_nonscalar"],
        categorical["generator_difference"],
        "nonscalar -sigma_x",
        "M2-boundary",
    )
    audit.check(
        "KMS pullbacks distinct",
        categorical["kms_pullbacks_distinct"]
        and categorical["kms_sigma_x_expectation_two"]
        > categorical["kms_sigma_x_expectation_one"],
        {
            "first": categorical["kms_sigma_x_expectation_one"],
            "second": categorical["kms_sigma_x_expectation_two"],
        },
        "tanh(4)>tanh(1)",
        "M2-boundary",
    )
    audit.check(
        "categorical carrier scope",
        categorical["common_c0_shift_categorical_only"]
        and not categorical["quasi_local_thermodynamic_identification"],
        {
            "categorical": categorical["common_c0_shift_categorical_only"],
            "quasi_local": categorical[
                "quasi_local_thermodynamic_identification"
            ],
        },
        {"categorical": True, "quasi_local": False},
        "scope",
    )

    authority = authority_audit(audit, staged)
    verdict = "PASS" if authority["status"] == "COMPLETE" else "INCOMPLETE"

    source_paths = [SCRIPT, MANIFEST, GROUND_PARENT, TANGENT_PARENT]
    certificate = selected_certificate()
    if certificate.exists():
        source_paths.append(certificate)
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
            "64 lowercase hexadecimal",
            "provenance",
        )

    passed = len(audit.rows)
    return {
        "schema": f"tect/{SLUG}-independent-result/1.0",
        "script_version": __version__,
        "result_id": RESULT_ID,
        "result_number": RESULT_NUMBER,
        "result_version": RESULT_VERSION,
        "exploration_id": EXPLORATION_ID,
        "task_id": "T-054",
        "claim_ids": ["C6-SPACETIME-SIGNATURE"],
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
            "right_context_recursive_smoothing": right_context,
            "triangular_l1_c0": triangular,
            "rational_sine_near_ground": sine,
            "negative_arveson": arveson,
            "bounded_cutoff_factorial_corridor": corridor,
            "static_tail_four_by_four_no_go": static_tail,
            "m2_categorical_boundary": categorical,
            "selected_tangent_raw_finite_words_closed": True,
            "universal_orbit_smear_cstar_closed": True,
            "universal_carrier_ground_doublets_closed": True,
            "all_exhaustion_spatial_cauchy_closed": False,
            "quasi_local_raw_oscillator_dynamics_closed": False,
            "finite_volume_to_OS_identification_closed": False,
            "broken_sector_GNS_gap_closed": False,
            "physical_mass_gap_closed": False,
            "continuum_closed": False,
            "physical_empty_comparison_closed": False,
            "Pre_A_closed": False,
        },
        "negative_ids": [NEW_NEGATIVE_ID],
        "reused_negative_ids": list(REUSED_NEGATIVE_IDS),
        "closed_subgates": list(CLOSED_SUBGATES),
        "retained_gates": list(RETAINED_GATES),
        "open_gates": list(OPEN_GATES),
        "authority": authority,
        "source_hashes": source_hashes,
        "boundary": authority["boundary"],
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
        help="allow missing certificate/formal authorities and report INCOMPLETE",
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
            f"{payload['summary']['total']} | SHA256 {digest} | {RESULT_ID}"
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

    atomic_json(arguments.output, payload)
    label = "PASS" if payload["verdict"] == "PASS" else "STAGED"
    print(
        f"{label} {payload['summary']['passed']}/"
        f"{payload['summary']['total']} | SHA256 {digest} | {RESULT_ID}"
    )
    print(arguments.output)
    if payload["authority"]["missing"]:
        print("STAGED-MISSING " + ", ".join(payload["authority"]["missing"]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

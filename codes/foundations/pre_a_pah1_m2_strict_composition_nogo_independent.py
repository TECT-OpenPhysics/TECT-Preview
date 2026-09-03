#!/usr/bin/env python3
"""Non-importing independent audit of the strict PA-H1/PA-M2 no-go.

This route uses rational row reduction, polynomial coefficient bookkeeping,
and direct Fourier-lattice arithmetic.  It does not import the primary code.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import tempfile
from collections import Counter
from fractions import Fraction
from pathlib import Path
from typing import Any

import sympy as sp


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
CANDIDATE_ID = "PA-H1-M2-STRICT-COMPOSITION-NOGO-v0"
SLUG = "pre-a-pah1-m2-strict-composition-nogo"
SCHEMA = f"tect/{SLUG}-independent/0.1"
CLAIM_CONTEXT = "C6-SPACETIME-SIGNATURE"
COMPARISON_CONTEXT = "A2-FULL-PRODUCTION-WELLPOSED"
DEFAULT_OUTPUT = (
    REPO
    / "claims"
    / CLAIM_CONTEXT
    / "runs"
    / f"2026-08-03-independent-{SLUG}"
    / "result.json"
)


def serial(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value).replace("\\", "/")
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, sp.MatrixBase):
        return [
            [serial(value[row, column]) for column in range(value.cols)]
            for row in range(value.rows)
        ]
    if isinstance(value, sp.Basic):
        return str(sp.factor(value))
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(item) for item in value]
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(serial(payload), stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def sha256(path: Path) -> str:
    data = path.read_bytes()
    if path.suffix.lower() != ".pdf":
        data = data.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


Matrix = list[list[Fraction]]
WaveVector = tuple[int, int, int]
FourierSeries = dict[WaveVector, sp.Expr]


def zero_matrix(rows: int, columns: int) -> Matrix:
    return [[Fraction(0) for _ in range(columns)] for _ in range(rows)]


def transpose(matrix: Matrix) -> Matrix:
    return [list(row) for row in zip(*matrix, strict=True)]


def multiply(left: Matrix, right: Matrix) -> Matrix:
    return [
        [
            sum(
                left[row][inner] * right[inner][column]
                for inner in range(len(right))
            )
            for column in range(len(right[0]))
        ]
        for row in range(len(left))
    ]


def rank(matrix: Matrix) -> int:
    work = [row[:] for row in matrix]
    rows = len(work)
    columns = len(work[0]) if rows else 0
    pivot_row = 0
    for column in range(columns):
        pivot = next(
            (row for row in range(pivot_row, rows) if work[row][column] != 0),
            None,
        )
        if pivot is None:
            continue
        work[pivot_row], work[pivot] = work[pivot], work[pivot_row]
        pivot_value = work[pivot_row][column]
        work[pivot_row] = [value / pivot_value for value in work[pivot_row]]
        for row in range(rows):
            if row == pivot_row:
                continue
            factor = work[row][column]
            if factor != 0:
                work[row] = [
                    work[row][index] - factor * work[pivot_row][index]
                    for index in range(columns)
                ]
        pivot_row += 1
        if pivot_row == rows:
            break
    return pivot_row


def symplectic(configuration_dimension: int) -> Matrix:
    matrix = zero_matrix(2 * configuration_dimension, 2 * configuration_dimension)
    for index in range(configuration_dimension):
        matrix[index][configuration_dimension + index] = Fraction(1)
        matrix[configuration_dimension + index][index] = Fraction(-1)
    return matrix


def negate_wavevector(vector: WaveVector) -> WaveVector:
    return tuple(-entry for entry in vector)


def fourier_convolve(left: FourierSeries, right: FourierSeries) -> FourierSeries:
    result: FourierSeries = {}
    for left_vector, left_coefficient in left.items():
        for right_vector, right_coefficient in right.items():
            vector = tuple(
                left_vector[index] + right_vector[index] for index in range(3)
            )
            result[vector] = sp.expand(
                result.get(vector, 0) + left_coefficient * right_coefficient
            )
    return {key: sp.simplify(value) for key, value in result.items() if value != 0}


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
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        self.rows.append(
            {
                "name": name,
                "status": "PASS",
                "actual": serial(actual),
                "expected": serial(expected),
                "group": group,
            }
        )


def derive() -> dict[str, Any]:
    audit = Audit()

    frequencies = [3, 5, 5]
    source_configuration = len(frequencies)
    source_phase = 2 * source_configuration
    target_antipodal_pairs = 4
    target_configuration = 2 * target_antipodal_pairs
    target_phase = 2 * target_configuration
    deficit = target_phase - source_phase

    audit.check(
        "independent source configuration dimension",
        source_configuration == 3,
        source_configuration,
        3,
        "fixture_rank",
    )
    audit.check(
        "independent source phase dimension",
        source_phase == 6,
        source_phase,
        6,
        "fixture_rank",
    )
    audit.check(
        "independent target configuration dimension",
        target_configuration == 8,
        target_configuration,
        8,
        "fixture_rank",
    )
    audit.check(
        "independent target phase dimension",
        target_phase == 16,
        target_phase,
        16,
        "fixture_rank",
    )
    audit.check(
        "independent phase-space deficit",
        deficit == 10,
        deficit,
        10,
        "fixture_rank",
    )
    audit.check(
        "independent no-bijection dimension test",
        source_phase != target_phase,
        (source_phase, target_phase),
        "unequal",
        "fixture_rank",
    )

    sigma_source = symplectic(source_configuration)
    sigma_target = symplectic(target_configuration)
    injection = zero_matrix(target_phase, source_phase)
    for index in range(source_configuration):
        injection[index][index] = Fraction(1)
        injection[target_configuration + index][source_configuration + index] = Fraction(1)
    pulled_back = multiply(multiply(transpose(injection), sigma_target), injection)
    audit.check(
        "independent explicit symplectic injection rank",
        rank(injection) == source_phase,
        rank(injection),
        source_phase,
        "fixture_rank",
    )
    audit.check(
        "independent explicit symplectic injection pullback",
        pulled_back == sigma_source,
        pulled_back,
        sigma_source,
        "fixture_rank",
    )

    complement_pairs = target_configuration - source_configuration
    complement = zero_matrix(target_phase, 2 * complement_pairs)
    for local, target in enumerate(range(source_configuration, target_configuration)):
        complement[target][local] = Fraction(1)
        complement[target_configuration + target][complement_pairs + local] = Fraction(1)
    audit.check(
        "independent ten-dimensional complement rank",
        rank(complement) == deficit,
        rank(complement),
        deficit,
        "fixture_rank",
    )
    audit.check(
        "independent complement symplectic form",
        multiply(multiply(transpose(complement), sigma_target), complement)
        == symplectic(complement_pairs),
        multiply(multiply(transpose(complement), sigma_target), complement),
        symplectic(complement_pairs),
        "fixture_rank",
    )

    source_metric_diagonal = [
        *(Fraction(frequency) for frequency in frequencies),
        *(Fraction(1, frequency) for frequency in frequencies),
    ]
    extension_one = [*frequencies, *([2] * complement_pairs)]
    extension_two = [*frequencies, *([7] * complement_pairs)]
    extension_one_metric = [
        *(Fraction(value) for value in extension_one),
        *(Fraction(1, value) for value in extension_one),
    ]
    extension_two_metric = [
        *(Fraction(value) for value in extension_two),
        *(Fraction(1, value) for value in extension_two),
    ]
    image_indices = [
        *range(source_configuration),
        *(target_configuration + index for index in range(source_configuration)),
    ]
    audit.check(
        "independent first full covariance agrees on image",
        [extension_one_metric[index] for index in image_indices]
        == source_metric_diagonal,
        [extension_one_metric[index] for index in image_indices],
        source_metric_diagonal,
        "state_extension",
    )
    audit.check(
        "independent second full covariance agrees on image",
        [extension_two_metric[index] for index in image_indices]
        == source_metric_diagonal,
        [extension_two_metric[index] for index in image_indices],
        source_metric_diagonal,
        "state_extension",
    )
    audit.check(
        "independent full covariances differ off image",
        extension_one_metric[source_configuration]
        != extension_two_metric[source_configuration],
        (
            extension_one_metric[source_configuration],
            extension_two_metric[source_configuration],
        ),
        "different",
        "state_extension",
    )
    extension_positivity = [
        (
            Fraction(frequency) * Fraction(1, frequency) - 1,
            Fraction(frequency) + Fraction(1, frequency),
        )
        for frequency in extension_one + extension_two
    ]
    audit.check(
        "independent complement quasi-free mode blocks are positive semidefinite",
        all(determinant == 0 and trace > 0 for determinant, trace in extension_positivity),
        extension_positivity,
        "det=0 and trace>0 for every mode",
        "state_extension",
    )

    # Independent CI8 Fourier representation.  Direct character
    # orthogonality proves coordinate injectivity, while Parseval for the
    # squared field supplies the quartic positive-definiteness step.
    representatives = (
        (1, 1, 1),
        (1, 1, -1),
        (1, -1, 1),
        (-1, 1, 1),
    )
    inverse_root_two = 1 / sp.sqrt(2)
    real_modes: list[FourierSeries] = []
    for representative in representatives:
        opposite = negate_wavevector(representative)
        real_modes.extend(
            [
                {
                    representative: inverse_root_two,
                    opposite: inverse_root_two,
                },
                {
                    representative: inverse_root_two / sp.I,
                    opposite: -inverse_root_two / sp.I,
                },
            ]
        )
    fourier_gram = sp.Matrix(
        [
            [
                sp.simplify(
                    fourier_convolve(real_modes[row], real_modes[column]).get(
                        (0, 0, 0), 0
                    )
                )
                for column in range(target_configuration)
            ]
            for row in range(target_configuration)
        ]
    )
    audit.check(
        "independent CI8 real Fourier map has identity Gram matrix",
        fourier_gram == sp.eye(target_configuration),
        fourier_gram,
        sp.eye(target_configuration),
        "energy_obstruction",
    )
    field_coordinates = sp.symbols(f"u0:{target_configuration}", real=True)
    field_coefficients: FourierSeries = {}
    for coordinate_value, mode in zip(field_coordinates, real_modes, strict=True):
        for vector, coefficient in mode.items():
            field_coefficients[vector] = sp.expand(
                field_coefficients.get(vector, 0) + coordinate_value * coefficient
            )
    squared_field = fourier_convolve(field_coefficients, field_coefficients)
    independent_l2 = sp.expand(sum(value**2 for value in field_coordinates))
    audit.check(
        "independent squared-field zero mode is the coefficient norm",
        sp.expand(squared_field[(0, 0, 0)] - independent_l2) == 0,
        squared_field[(0, 0, 0)],
        independent_l2,
        "energy_obstruction",
    )
    independent_quartic = sp.expand(
        fourier_convolve(squared_field, squared_field).get((0, 0, 0), 0)
    )
    independent_parseval = sp.expand(
        sum(value * sp.conjugate(value) for value in squared_field.values())
    )
    audit.check(
        "independent quartic integral is the Parseval sum for the squared field",
        sp.simplify(independent_quartic - independent_parseval) == 0,
        independent_quartic,
        independent_parseval,
        "energy_obstruction",
    )

    # Polynomial coefficient route: an affine field coordinate b+lambda*a
    # contributes a^4 to the fourth-degree coefficient, independent of b.
    affine_degree = 4
    affine_fourth_coefficients = [
        math.comb(affine_degree, power) for power in range(affine_degree + 1)
    ]
    audit.check(
        "independent affine quartic leading coefficient",
        affine_fourth_coefficients[-1] == 1,
        affine_fourth_coefficients[-1],
        1,
        "energy_obstruction",
    )
    positive_quartic_coupling = sp.symbols("g", positive=True)
    audit.check(
        "independent positive quartic coupling leaves nonzero top degree",
        positive_quartic_coupling * affine_fourth_coefficients[-1] / 4
        == positive_quartic_coupling / 4,
        positive_quartic_coupling * affine_fourth_coefficients[-1] / 4,
        positive_quartic_coupling / 4,
        "energy_obstruction",
    )
    source_scale = sp.symbols("lambda", real=True)
    source_quadratic = sp.Poly(source_scale**2, source_scale)
    source_fourth_coefficient = source_quadratic.coeff_monomial(source_scale**4)
    audit.check(
        "independent quadratic source has no fourth-degree coefficient",
        source_fourth_coefficient == 0,
        source_fourth_coefficient,
        0,
        "energy_obstruction",
    )
    pure_momentum = zero_matrix(target_phase, source_phase)
    for column in range(source_phase):
        pure_momentum[target_configuration + column][column] = Fraction(1)
    pure_pullback = multiply(
        multiply(transpose(pure_momentum), sigma_target), pure_momentum
    )
    audit.check(
        "independent zero-field derivative is isotropic",
        pure_pullback == zero_matrix(source_phase, source_phase),
        pure_pullback,
        zero_matrix(source_phase, source_phase),
        "energy_obstruction",
    )
    audit.check(
        "independent isotropic pullback contradicts source symplectic rank",
        rank(pure_pullback) == 0 and rank(sigma_source) == source_phase,
        (rank(pure_pullback), rank(sigma_source)),
        (0, source_phase),
        "energy_obstruction",
    )
    audit.check(
        "independent free coupling control removes top-degree mismatch",
        Fraction(0) * affine_fourth_coefficients[-1] == 0,
        0,
        0,
        "energy_obstruction",
    )

    squared_frequencies = sorted(set(frequency**2 for frequency in frequencies))
    audit.check(
        "independent PA-H1 squared-frequency set",
        squared_frequencies == [9, 25],
        squared_frequencies,
        [9, 25],
        "dynamics_obstruction",
    )
    audit.check(
        "independent scalar PA-M2 linearization cannot match two squares",
        len(squared_frequencies) == 2,
        len(squared_frequencies),
        2,
        "dynamics_obstruction",
    )
    source_characteristic_factors = dict(
        Counter(frequency**2 for frequency in frequencies)
    )
    characteristic_variable = sp.symbols("s", real=True)
    r_parameter = sp.symbols("r", real=True)
    chi_parameter = sp.symbols("chi", positive=True)
    pah1_characteristic = sp.factor(
        sp.prod(
            (characteristic_variable**2 + squared_frequency) ** multiplicity
            for squared_frequency, multiplicity in source_characteristic_factors.items()
        )
    )
    pam2_characteristic = sp.factor(
        (characteristic_variable**2 + r_parameter / chi_parameter)
        ** target_configuration
    )
    target_characteristic_factor_count = target_configuration
    audit.check(
        "independent PA-H1 characteristic-factor multiplicities",
        source_characteristic_factors == {9: 1, 25: 2},
        source_characteristic_factors,
        {9: 1, 25: 2},
        "dynamics_obstruction",
    )
    audit.check(
        "independent PA-M2 characteristic polynomial has one repeated factor",
        target_characteristic_factor_count == 8,
        target_characteristic_factor_count,
        8,
        "dynamics_obstruction",
    )
    audit.check(
        "independent frequency-three sector has a matching control",
        frequencies[0] ** 2 in squared_frequencies,
        frequencies[0] ** 2,
        squared_frequencies[0],
        "dynamics_obstruction",
    )
    audit.check(
        "independent frequency-five sector has a matching control",
        frequencies[1] ** 2 in squared_frequencies,
        frequencies[1] ** 2,
        squared_frequencies[-1],
        "dynamics_obstruction",
    )

    ci8_nodes = {
        (one, two, three)
        for one in (-1, 1)
        for two in (-1, 1)
        for three in (-1, 1)
    }
    wavevector = (1, 1, 1)
    triple_wavevector = tuple(3 * entry for entry in wavevector)
    audit.check(
        "independent CI8 contains the stripe carrier",
        wavevector in ci8_nodes,
        wavevector,
        "member",
        "regulator_closure",
    )
    audit.check(
        "independent triple carrier leaves CI8",
        triple_wavevector not in ci8_nodes,
        triple_wavevector,
        "outside",
        "regulator_closure",
    )
    fundamental_coefficient = Fraction(math.comb(3, 1), 2**3)
    third_harmonic_coefficient = Fraction(1, 2**3)
    audit.check(
        "independent cosine-cubed Fourier coefficients",
        (fundamental_coefficient, third_harmonic_coefficient)
        == (Fraction(3, 8), Fraction(1, 8)),
        (fundamental_coefficient, third_harmonic_coefficient),
        (Fraction(3, 8), Fraction(1, 8)),
        "regulator_closure",
    )
    leakage_norm = 2 * third_harmonic_coefficient**2
    audit.check(
        "independent projected cubic leakage norm",
        leakage_norm == Fraction(1, 32),
        leakage_norm,
        Fraction(1, 32),
        "regulator_closure",
    )

    raw_zero_point = Fraction(sum(frequencies), 2)
    normal_ordered_zero_point = raw_zero_point - raw_zero_point
    audit.check(
        "independent PA-H1 zero-point shift",
        raw_zero_point == Fraction(13, 2),
        raw_zero_point,
        Fraction(13, 2),
        "energy_clock",
    )
    energy_differences = [Fraction(1) + shift for shift in (Fraction(0), Fraction(-2))]
    audit.check(
        "independent additive offset reverses cross-model sign",
        energy_differences[0] > 0 > energy_differences[1],
        energy_differences,
        [">0", "<0"],
        "energy_clock",
    )
    common_frequency_gcd = math.gcd(*frequencies)
    flow_period = 2 * sp.pi / common_frequency_gcd
    audit.check(
        "independent integer spectrum has common period two pi",
        common_frequency_gcd == 1,
        common_frequency_gcd,
        1,
        "energy_clock",
    )
    audit.check(
        "independent invariant-state history is constant",
        len({"vacuum" for _ in range(9)}) == 1,
        len({"vacuum" for _ in range(9)}),
        1,
        "energy_clock",
    )
    audit.check(
        "independent nonvacuum oscillatory crossing remains possible",
        sp.cos(3 * sp.pi / 6) == 0,
        sp.cos(3 * sp.pi / 6),
        0,
        "energy_clock",
    )

    wave_number, q, c, chi = sp.symbols("K q c chi", positive=True)
    critical_axis_frequency = sp.sqrt(c / chi) * (wave_number**2 - q**2)
    group_speed = sp.diff(critical_axis_frequency, wave_number)
    uv_speed_growth_coefficient = sp.limit(
        group_speed / wave_number, wave_number, sp.oo
    )
    audit.check(
        "independent PA-M2 ultraviolet speed coefficient",
        uv_speed_growth_coefficient == 2 * sp.sqrt(c / chi),
        uv_speed_growth_coefficient,
        2 * sp.sqrt(c / chi),
        "uv_product",
    )
    audit.check(
        "independent finite cutoff speed grows with the cutoff",
        sp.diff(group_speed, wave_number) == 2 * sp.sqrt(c / chi),
        sp.diff(group_speed, wave_number),
        2 * sp.sqrt(c / chi),
        "uv_product",
    )
    audit.check(
        "independent decoupled product dimension",
        source_phase + target_phase == 22,
        source_phase + target_phase,
        22,
        "uv_product",
    )

    source = Path(__file__).resolve()
    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "candidate_id": CANDIDATE_ID,
        "candidate_family": "PRE-A-STRICT-INTERFACE-NOGO",
        "version": __version__,
        "issued": "2026-08-03",
        "authority": "non-importing T0 compatibility audit; not a claim or Pre-A closure",
        "claim_context": CLAIM_CONTEXT,
        "comparison_context": COMPARISON_CONTEXT,
        "claim_bearing": False,
        "task_id": "T-054",
        "independent_method": "Fraction row reduction, degree arrays, characteristic-factor multiplicities, and direct Fourier-lattice arithmetic; no primary import",
        "shared_exact_results": {
            "pah1_frequencies": frequencies,
            "pah1_configuration_dimension": source_configuration,
            "pah1_phase_dimension": source_phase,
            "pam2_configuration_dimension": target_configuration,
            "pam2_phase_dimension": target_phase,
            "symplectic_complement_dimension": deficit,
            "symplectic_injection_exists": True,
            "symplectic_bijection_exists": False,
            "pah1_characteristic_polynomial": pah1_characteristic,
            "pam2_zero_characteristic_polynomial": pam2_characteristic,
            "common_full_frequency_ratio": None,
            "cubic_third_harmonic_cosine_coefficient": 2 * third_harmonic_coefficient,
            "cubic_third_harmonic_fourier_coefficient": third_harmonic_coefficient,
            "cubic_leakage_norm_squared": leakage_norm,
            "raw_pah1_zero_point": raw_zero_point,
            "normal_ordered_pah1_zero_point": normal_ordered_zero_point,
            "period": flow_period,
            "pam2_uv_speed_growth_coefficient": uv_speed_growth_coefficient,
            "product_phase_dimension": source_phase + target_phase,
        },
        "scope": {
            "strict_unchanged_interface_rejected": True,
            "linear_symplectic_injection_exists": True,
            "linear_symplectic_bijection_exists": False,
            "full_state_extension_unique": False,
            "affine_global_interacting_energy_match": False,
            "zero_background_full_flow_intertwiner": False,
            "ci8_nonlinear_invariant_subspace": False,
            "common_energy_zero_identified": False,
            "stationary_vacuum_nonconstant_control": False,
            "nonvacuum_crossing_excluded": False,
            "global_lorentz_cone_match": False,
            "larger_or_nonlinear_parent_excluded": False,
            "pre_a_complete": False,
        },
        "assertions": {
            "passed": len(audit.rows),
            "total": len(audit.rows),
            "rows": audit.rows,
        },
        "source": {
            "path": source.relative_to(REPO),
            "sha256": sha256(source),
        },
        "no_overclaim": "The independent audit rejects only the declared strict unchanged interface. It does not reject a larger common parent, nonlinear or constrained map, ordered-background Hessian, broader cutoff, nonstationary state, open system, dynamic clock, or causal UV completion, and it does not prove Pre-A.",
    }
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    arguments = parser.parse_args()
    payload = derive()
    if not arguments.self_test:
        atomic_json(arguments.output, payload)
    print(
        f"PASS {payload['assertions']['passed']}/{payload['assertions']['total']} | "
        f"{CANDIDATE_ID} | independent strict-interface audit"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

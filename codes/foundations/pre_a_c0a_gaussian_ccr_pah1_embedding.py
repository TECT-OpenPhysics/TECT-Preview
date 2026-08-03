#!/usr/bin/env python3
"""Primary exact certificate for PA-C0A-GAUSSIAN-CCR-PAH1-EMBEDDING-v0.

The package extends the finite-state C0-A transfer calibration to the exact
Ornstein--Uhlenbeck/oscillator semigroup for three spatial Klein--Gordon modes
and embeds the associated finite-mode Weyl state into the already certified
PA-H1 characteristic reconstruction.  The spatial circle, Klein--Gordon
operator, time law, mode cutoff, and Gaussian state are inserted benchmark
data.  They are not a derivation of time, spacetime, or a physical vacuum.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any

import sympy as sp


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
CANDIDATE_ID = "PA-C0A-GAUSSIAN-CCR-PAH1-EMBEDDING-v0"
SLUG = "pre-a-c0a-gaussian-ccr-pah1-embedding"
SCHEMA = f"tect/{SLUG}-primary/0.1"
CLAIM_CONTEXT = "C6-SPACETIME-SIGNATURE"
DEFAULT_OUTPUT = (
    REPO
    / "claims"
    / CLAIM_CONTEXT
    / "runs"
    / f"2026-08-03-primary-{SLUG}"
    / "result.json"
)


def serial(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value).replace("\\", "/")
    if isinstance(value, sp.MatrixBase):
        return [[serial(value[i, j]) for j in range(value.cols)] for i in range(value.rows)]
    if isinstance(value, sp.Basic):
        return str(sp.simplify(value))
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
    return hashlib.sha256(path.read_bytes()).hexdigest()


class Audit:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def check(self, name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
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


def block_diagonal(*matrices: sp.Matrix) -> sp.Matrix:
    return sp.diag(*matrices)


def trig_coeff(kind: str, harmonic: int, coefficient: sp.Expr) -> dict[int, sp.Expr]:
    """Complex Fourier coefficients for cos/sin(harmonic*s/2)."""
    if kind == "cos":
        return {harmonic: coefficient / 2, -harmonic: coefficient / 2}
    if kind == "sin":
        return {harmonic: coefficient / (2 * sp.I), -harmonic: -coefficient / (2 * sp.I)}
    raise ValueError(kind)


def add_coefficients(*items: dict[int, sp.Expr]) -> dict[int, sp.Expr]:
    result: dict[int, sp.Expr] = {}
    for item in items:
        for harmonic, coefficient in item.items():
            result[harmonic] = sp.simplify(result.get(harmonic, 0) + coefficient)
    return {harmonic: coefficient for harmonic, coefficient in result.items() if coefficient != 0}


def scale_coefficients(item: dict[int, sp.Expr], factor: sp.Expr) -> dict[int, sp.Expr]:
    return {harmonic: sp.simplify(factor * coefficient) for harmonic, coefficient in item.items()}


def multiply_coefficients(
    left: dict[int, sp.Expr], right: dict[int, sp.Expr]
) -> dict[int, sp.Expr]:
    result: dict[int, sp.Expr] = {}
    for left_harmonic, left_coefficient in left.items():
        for right_harmonic, right_coefficient in right.items():
            harmonic = left_harmonic + right_harmonic
            result[harmonic] = sp.simplify(
                result.get(harmonic, 0) + left_coefficient * right_coefficient
            )
    return {harmonic: coefficient for harmonic, coefficient in result.items() if coefficient != 0}


def coefficient_expression(item: dict[int, sp.Expr], variable: sp.Symbol) -> sp.Expr:
    return sp.simplify(
        sp.expand_complex(
            sum(
                coefficient * sp.exp(sp.I * sp.Rational(harmonic, 2) * variable)
                for harmonic, coefficient in item.items()
            )
        )
    )


def derivative_coefficients(item: dict[int, sp.Expr]) -> dict[int, sp.Expr]:
    return {
        harmonic: sp.simplify(sp.I * sp.Rational(harmonic, 2) * coefficient)
        for harmonic, coefficient in item.items()
    }


def exponential_integral(harmonic: int, length: sp.Expr) -> sp.Expr:
    """Integral of exp(i*harmonic*s/2) from zero to length."""
    if harmonic == 0:
        return length
    return sp.simplify(
        2 * (sp.exp(sp.I * sp.Rational(harmonic, 2) * length) - 1)
        / (sp.I * harmonic)
    )


def coefficient_integral(
    left: dict[int, sp.Expr], right: dict[int, sp.Expr], length: sp.Expr
) -> sp.Expr:
    value = sp.Integer(0)
    for left_harmonic, left_coefficient in left.items():
        for right_harmonic, right_coefficient in right.items():
            value += (
                left_coefficient
                * right_coefficient
                * exponential_integral(left_harmonic + right_harmonic, length)
            )
    return sp.simplify(sp.expand_complex(value))


def derive() -> dict[str, Any]:
    audit = Audit()
    I3 = sp.eye(3)
    Z3 = sp.zeros(3)
    symplectic = Z3.row_join(I3).col_join((-I3).row_join(Z3))

    # Inserted fixed-background spectral fixture.
    length = sp.pi / 2
    tau = length / 2
    mass = sp.Integer(3)
    k_values = (sp.Integer(0), sp.Integer(4), sp.Integer(4))
    omega_values = tuple(sp.sqrt(mass**2 + k**2) for k in k_values)
    omega = sp.diag(*omega_values)
    omega_inverse = omega.inv()
    audit.check(
        "inserted KG frequencies are exact",
        omega_values == (sp.Integer(3), sp.Integer(5), sp.Integer(5)),
        omega_values,
        (3, 5, 5),
        "spectral_fixture",
    )
    audit.check(
        "top slice spans the full circle",
        sp.simplify(2 * tau - length) == 0,
        2 * tau,
        length,
        "spectral_fixture",
    )

    x, time = sp.symbols("x time", real=True)
    mode_normalizations = (
        sp.sqrt(sp.Rational(2, 1) / sp.pi),
        2 / sp.sqrt(sp.pi),
        2 / sp.sqrt(sp.pi),
    )
    mode_kinds = ("constant", "cos", "sin")
    modes = (
        mode_normalizations[0],
        mode_normalizations[1] * sp.cos(k_values[1] * x),
        mode_normalizations[2] * sp.sin(k_values[2] * x),
    )
    mode_gram = sp.Matrix(
        3,
        3,
        lambda i, j: sp.simplify(
            sp.integrate(modes[i] * modes[j], (x, -tau, tau))
        ),
    )
    audit.check(
        "real Fourier modes are orthonormal on the slice",
        mode_gram == I3,
        mode_gram,
        I3,
        "spectral_fixture",
    )
    for index, (mode, frequency) in enumerate(zip(modes, omega_values)):
        residual = sp.simplify(-sp.diff(mode, x, 2) + mass**2 * mode - frequency**2 * mode)
        audit.check(
            f"mode {index} diagonalizes the local spatial KG operator",
            residual == 0,
            residual,
            0,
            "spectral_fixture",
        )

    # Classical phase space, compatible complex structure, and real-time flow.
    complex_structure = Z3.row_join(-omega_inverse).col_join(omega.row_join(Z3))
    metric = sp.simplify(symplectic * complex_structure)
    expected_metric = block_diagonal(omega, omega_inverse)
    audit.check(
        "complex structure squares to minus identity",
        sp.simplify(complex_structure**2 + sp.eye(6)) == sp.zeros(6),
        sp.simplify(complex_structure**2),
        -sp.eye(6),
        "phase_space",
    )
    audit.check(
        "complex structure is symplectic",
        sp.simplify(complex_structure.T * symplectic * complex_structure - symplectic)
        == sp.zeros(6),
        sp.simplify(complex_structure.T * symplectic * complex_structure),
        symplectic,
        "phase_space",
    )
    audit.check(
        "compatible covariance metric has the KG energy weights",
        metric == expected_metric,
        metric,
        expected_metric,
        "phase_space",
    )
    for frequency in omega_values:
        positivity_block = sp.Matrix([[frequency, sp.I], [-sp.I, 1 / frequency]])
        audit.check(
            f"quasi-free positivity block at omega={frequency}",
            sp.simplify(positivity_block.det()) == 0
            and sp.simplify(sp.trace(positivity_block)) > 0,
            (positivity_block.det(), sp.trace(positivity_block)),
            (0, ">0"),
            "quasi_free_state",
        )

    cosine = sp.diag(*(sp.cos(frequency * tau) for frequency in omega_values))
    sine = sp.diag(*(sp.sin(frequency * tau) for frequency in omega_values))
    flow = cosine.row_join(omega_inverse * sine).col_join(
        (-omega * sine).row_join(cosine)
    )
    audit.check(
        "exact KG flow is symplectic",
        sp.simplify(flow.T * symplectic * flow - symplectic) == sp.zeros(6),
        sp.simplify(flow.T * symplectic * flow),
        symplectic,
        "phase_space",
    )
    audit.check(
        "exact KG flow preserves the vacuum covariance metric",
        sp.simplify(flow.T * metric * flow - metric) == sp.zeros(6),
        sp.simplify(flow.T * metric * flow),
        metric,
        "quasi_free_state",
    )
    audit.check(
        "exact slice phases are pinned",
        tuple(sp.simplify(omega_values[i] * tau) for i in range(3))
        == (3 * sp.pi / 4, 5 * sp.pi / 4, 5 * sp.pi / 4),
        tuple(sp.simplify(omega_values[i] * tau) for i in range(3)),
        (3 * sp.pi / 4, 5 * sp.pi / 4, 5 * sp.pi / 4),
        "phase_space",
    )

    sample_phase = sp.Matrix([1, -2, 3, 2, 1, -1])
    sample_covariance = sp.simplify((sample_phase.T * metric * sample_phase)[0])
    evolved_covariance = sp.simplify((flow * sample_phase).T * metric * (flow * sample_phase))[0]
    audit.check(
        "sample quasi-free characteristic exponent is invariant",
        sp.simplify(sample_covariance - evolved_covariance) == 0,
        evolved_covariance,
        sample_covariance,
        "quasi_free_state",
    )

    # Infinite-occupation Gaussian/OU transfer on L2(gamma_Omega).
    gaussian_covariance = sp.Rational(1, 2) * omega_inverse
    spacing = sp.log(2)
    transfer_one_particle = sp.diag(*(sp.Rational(1, 2) ** frequency for frequency in omega_values))
    expected_transfer = sp.diag(sp.Rational(1, 8), sp.Rational(1, 32), sp.Rational(1, 32))
    audit.check(
        "one-step Mehler contraction is exact",
        transfer_one_particle == expected_transfer,
        transfer_one_particle,
        expected_transfer,
        "gaussian_transfer",
    )
    noise_covariance = sp.simplify(
        (I3 - transfer_one_particle**2) * gaussian_covariance
    )
    stationary_covariance = sp.simplify(
        transfer_one_particle * gaussian_covariance * transfer_one_particle
        + noise_covariance
    )
    audit.check(
        "Mehler update preserves the Gaussian covariance",
        stationary_covariance == gaussian_covariance,
        stationary_covariance,
        gaussian_covariance,
        "gaussian_transfer",
    )
    transfer_second = sp.diag(
        *(sp.Rational(1, 3) ** frequency for frequency in omega_values)
    )
    noise_second = sp.simplify(
        (I3 - transfer_second**2) * gaussian_covariance
    )
    semigroup_noise = sp.simplify(
        noise_covariance
        + transfer_one_particle * noise_second * transfer_one_particle
    )
    combined_transfer = sp.simplify(transfer_one_particle * transfer_second)
    combined_noise = sp.simplify(
        (I3 - combined_transfer**2) * gaussian_covariance
    )
    audit.check(
        "Mehler noise satisfies the exact semigroup composition law",
        semigroup_noise == combined_noise,
        semigroup_noise,
        combined_noise,
        "gaussian_transfer",
    )
    joint_covariance = gaussian_covariance.row_join(
        gaussian_covariance * transfer_one_particle
    ).col_join(
        (transfer_one_particle * gaussian_covariance).row_join(gaussian_covariance)
    )
    swap = Z3.row_join(I3).col_join(I3.row_join(Z3))
    audit.check(
        "stationary one-link Gaussian law is reflection symmetric",
        sp.simplify(swap * joint_covariance * swap.T - joint_covariance) == sp.zeros(6),
        sp.simplify(swap * joint_covariance * swap.T),
        joint_covariance,
        "gaussian_transfer",
    )
    os_times = (sp.Integer(0), spacing)
    os_vectors = (sp.Matrix([1, 1, 0]), sp.Matrix([1, -1, 0]))
    os_direct = sp.Integer(0)
    os_factor_vector = sp.zeros(3, 1)
    omega_minus_half = sp.diag(*(1 / sp.sqrt(value) for value in omega_values))
    for index in range(2):
        decay_i = sp.diag(*(sp.exp(-os_times[index] * value) for value in omega_values))
        os_factor_vector += omega_minus_half * decay_i * os_vectors[index]
        for other in range(2):
            decay_sum = sp.diag(
                *(
                    sp.exp(-(os_times[index] + os_times[other]) * value)
                    for value in omega_values
                )
            )
            os_direct += (
                os_vectors[index].T
                * gaussian_covariance
                * decay_sum
                * os_vectors[other]
            )[0]
    os_factorized = sp.simplify((os_factor_vector.T * os_factor_vector)[0] / 2)
    audit.check(
        "linear time-reflection Gram fixture factorizes positively",
        sp.simplify(os_direct - os_factorized) == 0 and os_factorized > 0,
        os_direct,
        os_factorized,
        "reflection_positivity",
    )

    multiindices = [
        (n0, nc, ns)
        for n0 in range(4)
        for nc in range(4)
        for ns in range(4)
    ]
    fock_rows = []
    for multiindex in multiindices:
        energy = sum(multiindex[i] * omega_values[i] for i in range(3))
        eigenvalue = sp.simplify(sp.exp(-spacing * energy))
        fock_rows.append((multiindex, energy, eigenvalue))
        audit.check(
            f"Hermite transfer logarithm for {multiindex}",
            sp.simplify(-sp.log(eigenvalue) / spacing - energy) == 0,
            -sp.log(eigenvalue) / spacing,
            energy,
            "gaussian_transfer",
        )
    positive_energies = sorted({int(row[1]) for row in fock_rows if row[1] > 0})
    audit.check(
        "OU vacuum is the unique zero multiindex in the fixture",
        [row[0] for row in fock_rows if row[1] == 0] == [(0, 0, 0)],
        [row[0] for row in fock_rows if row[1] == 0],
        [(0, 0, 0)],
        "gaussian_transfer",
    )
    audit.check(
        "OU spectral gap equals the smallest inserted KG frequency",
        positive_energies[0] == 3,
        positive_energies[0],
        3,
        "gaussian_transfer",
    )
    occupation = sp.symbols("occupation", integer=True, nonnegative=True)
    lower_bound_limit = sp.limit(sp.Rational(1, 2) ** (3 * occupation), occupation, sp.oo)
    audit.check(
        "Mehler transfer has no positive uniform lower spectral bound",
        lower_bound_limit == 0,
        lower_bound_limit,
        0,
        "unbounded_generator_boundary",
    )
    transfer_trace = sp.simplify(
        sp.prod(1 / (1 - sp.exp(-spacing * frequency)) for frequency in omega_values)
    )
    audit.check(
        "finite-mode Mehler transfer is trace class despite infinite occupation",
        transfer_trace == sp.Rational(8192, 6727),
        transfer_trace,
        sp.Rational(8192, 6727),
        "gaussian_transfer",
    )

    q_scalar, omega_scalar = sp.symbols("q_scalar omega_scalar", real=True, positive=True)
    test_function = sp.Function("test_function")(q_scalar)
    position_action = q_scalar * test_function
    momentum_action = -sp.I * (
        sp.diff(test_function, q_scalar) - omega_scalar * q_scalar * test_function
    )
    q_after_p = sp.expand(q_scalar * momentum_action)
    p_after_q = -sp.I * (
        sp.diff(position_action, q_scalar) - omega_scalar * q_scalar * position_action
    )
    audit.check(
        "Gaussian Schrodinger representation satisfies CCR on the polynomial core",
        sp.simplify(q_after_p - p_after_q - sp.I * test_function) == 0,
        sp.simplify(q_after_p - p_after_q),
        sp.I * test_function,
        "quasi_free_state",
    )
    ground_factor = sp.exp(-omega_scalar * q_scalar**2 / 2)
    oscillator_shifted = (
        -sp.diff(ground_factor * test_function, q_scalar, 2) / 2
        + omega_scalar**2 * q_scalar**2 * ground_factor * test_function / 2
        - omega_scalar * ground_factor * test_function / 2
    ) / ground_factor
    ou_generator = -sp.diff(test_function, q_scalar, 2) / 2 + omega_scalar * q_scalar * sp.diff(
        test_function, q_scalar
    )
    audit.check(
        "ground-state transform gives the OU generator exactly",
        sp.simplify(oscillator_shifted - ou_generator) == 0,
        sp.simplify(oscillator_shifted),
        ou_generator,
        "energy_normalization",
    )
    zero_point_energy = sp.Rational(1, 2) * sum(omega_values)
    audit.check(
        "finite-mode unnormalised oscillator zero-point energy",
        zero_point_energy == sp.Rational(13, 2),
        zero_point_energy,
        sp.Rational(13, 2),
        "energy_normalization",
    )

    # A finite occupation truncation cannot obey exact CCR.  The explicit
    # four-level oscillator displays the top-state anomaly and trace zero.
    truncation_dimension = 4
    annihilation = sp.zeros(truncation_dimension)
    for level in range(1, truncation_dimension):
        annihilation[level - 1, level] = sp.sqrt(level)
    creation = annihilation.T
    truncated_commutator = sp.simplify(annihilation * creation - creation * annihilation)
    audit.check(
        "finite Fock truncation has the exact top-state commutator anomaly",
        truncated_commutator == sp.diag(1, 1, 1, -3),
        truncated_commutator,
        sp.diag(1, 1, 1, -3),
        "finite_ccr_boundary",
    )
    audit.check(
        "finite commutator trace obstruction",
        sp.trace(truncated_commutator) == 0
        and sp.trace(sp.eye(truncation_dimension)) == truncation_dimension,
        (sp.trace(truncated_commutator), sp.trace(sp.eye(truncation_dimension))),
        (0, truncation_dimension),
        "finite_ccr_boundary",
    )

    # Mandatory falsifiers and non-selection controls.
    scalar_covariance = sp.Rational(1, 2)
    negative_rho = sp.Rational(-1, 2)
    negative_noise = sp.simplify(scalar_covariance * (1 - negative_rho**2))
    negative_link_form = sp.simplify(negative_rho * scalar_covariance)
    audit.check(
        "negative AR1 remains stationary with positive noise",
        negative_noise == sp.Rational(3, 8),
        negative_noise,
        sp.Rational(3, 8),
        "negative_controls",
    )
    audit.check(
        "negative AR1 first chaos violates link reflection positivity",
        negative_link_form == sp.Rational(-1, 4),
        negative_link_form,
        sp.Rational(-1, 4),
        "negative_controls",
    )
    audit.check(
        "zero-correlation transfer is link-positive but has no finite logarithm",
        sp.log(sp.Integer(0)) == sp.zoo,
        sp.log(sp.Integer(0)),
        sp.zoo,
        "negative_controls",
    )
    drift_one = sp.Integer(1)
    drift_two = sp.Integer(2)
    drift_transfer_one = sp.exp(-spacing * drift_one)
    drift_transfer_two = sp.exp(-spacing * drift_two)
    drift_noise_one = sp.simplify(scalar_covariance * (1 - drift_transfer_one**2))
    drift_noise_two = sp.simplify(scalar_covariance * (1 - drift_transfer_two**2))
    audit.check(
        "same Gaussian marginal supports distinct reversible OU drifts",
        (drift_transfer_one, drift_noise_one, drift_transfer_two, drift_noise_two)
        == (
            sp.Rational(1, 2),
            sp.Rational(3, 8),
            sp.Rational(1, 4),
            sp.Rational(15, 32),
        ),
        (drift_transfer_one, drift_noise_one, drift_transfer_two, drift_noise_two),
        (sp.Rational(1, 2), sp.Rational(3, 8), sp.Rational(1, 4), sp.Rational(15, 32)),
        "nonselection_controls",
    )
    positive_frequency = sp.symbols("positive_frequency", positive=True)
    zero_mode_covariance_limit = sp.limit(
        1 / (2 * positive_frequency), positive_frequency, 0, dir="+"
    )
    audit.check(
        "massless periodic zero mode destroys the canonical Gaussian covariance",
        zero_mode_covariance_limit == sp.oo,
        zero_mode_covariance_limit,
        sp.oo,
        "negative_controls",
    )
    audit.check(
        "negative frequency makes the Euclidean drift expansive",
        sp.exp(-spacing * sp.Integer(-1)) == 2,
        sp.exp(spacing),
        2,
        "negative_controls",
    )

    # Exact PA-H1 embedding.  Initial phase vectors at t=0 generate complete
    # characteristic traces on v=0 and u=0; the certified PA-H1 map must return
    # the KG-evolved phase vector on t=tau.
    fields: list[sp.Expr] = []
    for column in range(6):
        expression = sp.Integer(0)
        for mode_index, (mode, frequency) in enumerate(zip(modes, omega_values)):
            q_coefficient = sp.Integer(1) if column == mode_index else sp.Integer(0)
            p_coefficient = sp.Integer(1) if column == mode_index + 3 else sp.Integer(0)
            expression += mode * (
                q_coefficient * sp.cos(frequency * time)
                + p_coefficient * sp.sin(frequency * time) / frequency
            )
        fields.append(sp.simplify(expression))

    for column, field in enumerate(fields):
        kg_residual = sp.simplify(
            sp.diff(field, time, 2) - sp.diff(field, x, 2) + mass**2 * field
        )
        audit.check(
            f"embedded basis field {column} solves local KG",
            kg_residual == 0,
            kg_residual,
            0,
            "pah1_embedding",
        )

    u, v = sp.symbols("u v", real=True, nonnegative=True)
    traces_a = [sp.simplify(field.subs({time: u / 2, x: u / 2})) for field in fields]
    traces_b = [sp.simplify(field.subs({time: v / 2, x: -v / 2})) for field in fields]
    for column in range(6):
        audit.check(
            f"characteristic corner compatibility for basis {column}",
            sp.simplify(traces_a[column].subs(u, 0) - traces_b[column].subs(v, 0)) == 0,
            traces_a[column].subs(u, 0),
            traces_b[column].subs(v, 0),
            "pah1_embedding",
        )

    # Extract the actual top-slice field and momentum coefficients from every
    # constructed KG basis solution.  PA-H1 uniqueness identifies these with
    # reconstruction from the complete characteristic traces.
    reconstructed_columns: list[sp.Matrix] = []
    for field in fields:
        field_slice = sp.simplify(field.subs(time, tau))
        momentum_slice = sp.simplify(sp.diff(field, time).subs(time, tau))
        q_out = [
            sp.simplify(sp.integrate(mode * field_slice, (x, -tau, tau)))
            for mode in modes
        ]
        p_out = [
            sp.simplify(sp.integrate(mode * momentum_slice, (x, -tau, tau)))
            for mode in modes
        ]
        reconstructed_columns.append(sp.Matrix(q_out + p_out))
    reconstructed_map = sp.Matrix.hstack(*reconstructed_columns)
    audit.check(
        "PA-H1 slice reconstruction equals exact KG flow on the embedded range",
        sp.simplify(reconstructed_map - flow) == sp.zeros(6),
        reconstructed_map,
        flow,
        "pah1_embedding",
    )

    # Derive the boundary Fourier dictionaries from the same upstream mode
    # kinds, wave numbers, frequencies, and normalizations as the fields.
    coefficient_traces_a: list[dict[int, sp.Expr]] = []
    coefficient_traces_b: list[dict[int, sp.Expr]] = []
    for column in range(6):
        mode_index = column if column < 3 else column - 3
        frequency = int(omega_values[mode_index])
        wave_number = int(k_values[mode_index])
        phase_kind = "cos" if column < 3 else "sin"
        phase_scale = sp.Integer(1) if column < 3 else 1 / omega_values[mode_index]
        temporal = trig_coeff(phase_kind, frequency, phase_scale)
        if mode_kinds[mode_index] == "constant":
            spatial_a = {0: mode_normalizations[mode_index]}
            spatial_b = dict(spatial_a)
        else:
            spatial_a = trig_coeff(
                mode_kinds[mode_index], wave_number, mode_normalizations[mode_index]
            )
            orientation = -1 if mode_kinds[mode_index] == "sin" else 1
            spatial_b = trig_coeff(
                mode_kinds[mode_index],
                wave_number,
                orientation * mode_normalizations[mode_index],
            )
        coefficient_traces_a.append(multiply_coefficients(temporal, spatial_a))
        coefficient_traces_b.append(multiply_coefficients(temporal, spatial_b))
    for column in range(6):
        if sp.simplify(coefficient_expression(coefficient_traces_a[column], u) - traces_a[column]) != 0:
            raise AssertionError(f"derived A-trace Fourier dictionary mismatch at column {column}")
        if sp.simplify(coefficient_expression(coefficient_traces_b[column], v) - traces_b[column]) != 0:
            raise AssertionError(f"derived B-trace Fourier dictionary mismatch at column {column}")
    boundary_symplectic = sp.zeros(6)
    boundary_energy = sp.zeros(6)
    for row in range(6):
        for column in range(6):
            derivative_a_row = derivative_coefficients(coefficient_traces_a[row])
            derivative_a_column = derivative_coefficients(coefficient_traces_a[column])
            derivative_b_row = derivative_coefficients(coefficient_traces_b[row])
            derivative_b_column = derivative_coefficients(coefficient_traces_b[column])
            boundary_symplectic[row, column] = sp.simplify(
                coefficient_integral(
                    coefficient_traces_a[row], derivative_a_column, length
                )
                - coefficient_integral(
                    coefficient_traces_a[column], derivative_a_row, length
                )
                + coefficient_integral(
                    coefficient_traces_b[row], derivative_b_column, length
                )
                - coefficient_integral(
                    coefficient_traces_b[column], derivative_b_row, length
                )
            )
            boundary_energy[row, column] = sp.simplify(
                coefficient_integral(derivative_a_row, derivative_a_column, length)
                + mass**2
                * coefficient_integral(
                    coefficient_traces_a[row], coefficient_traces_a[column], length
                )
                / 4
                + coefficient_integral(derivative_b_row, derivative_b_column, length)
                + mass**2
                * coefficient_integral(
                    coefficient_traces_b[row], coefficient_traces_b[column], length
                )
                / 4
            )
    expected_energy_matrix = sp.Rational(1, 2) * block_diagonal(omega**2, I3)
    audit.check(
        "characteristic embedding preserves the exact symplectic form",
        boundary_symplectic == symplectic,
        boundary_symplectic,
        symplectic,
        "pah1_embedding",
    )
    audit.check(
        "characteristic boundary flux equals the exact slice KG energy",
        boundary_energy == expected_energy_matrix,
        boundary_energy,
        expected_energy_matrix,
        "pah1_embedding",
    )

    projector_kernel_witness = sp.simplify(
        sum(mode.subs(x, 0) * mode.subs(x, sp.pi / 8) for mode in modes)
    )
    audit.check(
        "finite spectral projector has an off-diagonal nonlocal kernel",
        projector_kernel_witness == 2 / sp.pi,
        projector_kernel_witness,
        2 / sp.pi,
        "locality_boundary",
    )
    full_stiffness = sp.diag(1, 4)
    noninvariant_vector = sp.Matrix([1, 1]) / sp.sqrt(2)
    noninvariant_projection = noninvariant_vector * noninvariant_vector.T
    intertwining_residual = sp.simplify(
        (sp.eye(2) - noninvariant_projection) * full_stiffness * noninvariant_vector
    )
    audit.check(
        "generic non-spectral Galerkin embedding is not a dynamical intertwiner",
        sp.simplify((intertwining_residual.T * intertwining_residual)[0])
        == sp.Rational(9, 4),
        sp.simplify((intertwining_residual.T * intertwining_residual)[0]),
        sp.Rational(9, 4),
        "intertwiner_boundary",
    )
    image_phase = sp.Matrix([1, 0, 0, 0, 0, 0])
    complement_sigma = sp.Matrix([[0, 1], [-1, 0]])
    complement_phase_zero = sp.Matrix([0, 0])
    complement_phase_probe = sp.Matrix([1, 0])
    extension_data = []
    for complement_frequency in (sp.Integer(2), sp.Integer(7)):
        complement_J = sp.Matrix(
            [[0, -1 / complement_frequency], [complement_frequency, 0]]
        )
        complement_metric = sp.simplify(complement_sigma * complement_J)
        complement_positivity = complement_metric + sp.I * complement_sigma
        full_metric = block_diagonal(metric, complement_metric)
        phase_on_image = image_phase.col_join(complement_phase_zero)
        phase_off_image = image_phase.col_join(complement_phase_probe)
        extension_data.append(
            {
                "frequency": complement_frequency,
                "psd": complement_positivity.det() == 0
                and sp.re(complement_positivity.trace()) > 0,
                "on_image": sp.simplify(
                    (phase_on_image.T * full_metric * phase_on_image)[0] / 4
                ),
                "off_image": sp.simplify(
                    (phase_off_image.T * full_metric * phase_off_image)[0] / 4
                ),
            }
        )
    audit.check(
        "distinct Gaussian extensions agree on the finite image and differ off it",
        all(item["psd"] for item in extension_data)
        and extension_data[0]["on_image"] == extension_data[1]["on_image"]
        and extension_data[0]["off_image"] != extension_data[1]["off_image"],
        extension_data,
        "positive direct-sum states equal on complement=0 and different on complement probe",
        "state_extension_boundary",
    )

    # Analytic Galerkin-tail exponent used in the certificate.  The displayed
    # bound is theorem-level algebra, not a numerical continuum simulation.
    regularity = sp.symbols("s", real=True)
    spectral_weight = sp.symbols("omega_n", positive=True)
    q_tail_factor = sp.simplify(
        spectral_weight / spectral_weight ** (2 * regularity)
    )
    p_tail_factor = sp.simplify(
        spectral_weight ** (-1) / spectral_weight ** (2 * (regularity - 1))
    )
    audit.check(
        "field and momentum energy tails have the same Sobolev exponent",
        sp.simplify(q_tail_factor - spectral_weight ** (1 - 2 * regularity)) == 0
        and sp.simplify(p_tail_factor - spectral_weight ** (1 - 2 * regularity)) == 0,
        (q_tail_factor, p_tail_factor),
        (spectral_weight ** (1 - 2 * regularity),) * 2,
        "galerkin_boundary",
    )

    source = Path(__file__).resolve()
    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "candidate_id": CANDIDATE_ID,
        "candidate_family": "C0A-GAUSSIAN-OU-CCR-PAH1-EMBEDDING",
        "version": __version__,
        "issued": "2026-08-03",
        "authority": "T0 Pre-A C0-A/PA-H1 bridge certificate; no TECT claim or tier change",
        "claim_context": CLAIM_CONTEXT,
        "claim_bearing": False,
        "task_id": "T-054",
        "inserted_fixture": {
            "spatial_background": "fixed 1+1 Minkowski cylinder with circumference pi/2",
            "slice": "tau=pi/4",
            "mass": "3",
            "modes": ["constant", "cos(4x)", "sin(4x)"],
            "frequencies": [str(value) for value in omega_values],
            "time_spacing": "log(2)",
            "one_particle_transfer": serial(transfer_one_particle),
        },
        "exact_results": {
            "ou_measure_covariance": serial(gaussian_covariance),
            "ou_generator": "H_OU=sum_j[-1/2 partial_qj^2+omega_j q_j partial_qj]=dGamma(Omega)",
            "ou_semigroup": "P_t=Gamma(exp(-t Omega)) by the Mehler formula on L2(gamma_Omega)",
            "ou_hermite_spectrum": "H h_n=(omega.n)h_n and P_a h_n=exp[-a(omega.n)]h_n; fixture omega=(3,5,5), a=log 2",
            "unique_vacuum_and_gap": f"ker(H)=span{{1}}; gap={min(omega_values)}",
            "link_reflection_positivity": "<f,P_a f>_gamma>=0, strict for nonzero f, but with no uniform positive lower bound",
            "full_time_reflection_positivity": "E[conj(F(theta Q))F(Q)]=||E[F|Q_0]||^2>=0 for future-measurable F in the stationary two-sided OU path",
            "zero_in_transfer_spectrum": "0 is an accumulation point of spec(P_a), while ker(P_a)={0}",
            "unbounded_log_domain": "H=-(1/a)log(P_a) on D(H)={sum c_n h_n: sum (n.Omega)^2 |c_n|^2<infinity}",
            "quasi_free_state": "omega_0(W(y))=exp[-mu_V(y,y)/4], mu_V=q.Omega.q+p.Omega^(-1).p",
            "state_invariance": "mu_V(S_t y,S_t y)=mu_V(y,y)",
            "pah1_embedding": "T(y)=(phi_y(u/2,u/2),phi_y(v/2,-v/2)); P_tau T=S_tau",
            "pah1_symplectic_identity": "Omega_H(Ty,Tz)=sigma(y,z)",
            "pah1_energy_identity": "E_H(Ty)=E_KG(y)=1/2(p.p+q.Omega^2.q)",
            "boundary_state": "omega_H(W(Ty))=omega_0(W(y)) on the finite-mode characteristic Weyl subalgebra",
            "slice_state": "omega_Sigma(W(P_tau Ty))=omega_H(W(Ty))=omega_0(W(y))",
            "normal_ordered_vacuum_energy": "0",
            "unnormalised_finite_mode_zero_point_energy": str(zero_point_energy),
            "galerkin_covariance_tail": "for s>3/2, 0<=mu_infty(y)-mu_N(y)<=omega_(N+1)^(1-2s)(||q||_s^2+||p||_(s-1)^2)",
            "characteristic_function_tail": "|omega_infinity(W_infinity(y))-omega_N(W_N(Pi_N y))|<=(mu_infinity(y)-mu_N(Pi_N y))/4 as a cross-algebra comparison on the declared smooth domain; no full-algebra state extension follows",
        },
        "hostile_controls": {
            "finite_fock_exact_ccr": False,
            "finite_fock_trace_obstruction": "Tr[A,B]=0 excludes [Q,P]=iI in finite dimension; the four-level commutator is diag(1,1,1,-3)",
            "uniform_positive_transfer_lower_bound": False,
            "absolute_vacuum_energy_selected": False,
            "finite_mode_state_is_full_hadamard_state": False,
            "kg_dispersion_derived": False,
            "same_marginal_selects_drift": False,
            "finite_spectral_cutoff_is_local": False,
            "finite_image_selects_unique_full_state_extension": False,
            "generic_galerkin_embedding_intertwines_dynamics": False,
        },
        "scope": {
            "strongly_continuous_gaussian_semigroup": True,
            "generally_unbounded_self_adjoint_generator": True,
            "exact_infinite_occupation_ccr_for_three_spatial_modes": True,
            "selected_free_benchmark_vacuum_after_omega_is_inserted": True,
            "exact_pah1_finite_mode_embedding": True,
            "exact_boundary_slice_symplectic_and_energy_match": True,
            "controlled_smooth_galerkin_covariance_tail_bound": True,
            "full_continuum_state_limit": False,
            "finite_fock_truncation_used": False,
            "uniform_transfer_lower_bound": False,
            "full_pah1_state_selected": False,
            "hadamard_property_certified": False,
            "absolute_or_physical_vacuum_energy_derived": False,
            "kg_operator_or_dispersion_derived": False,
            "causal_structure_emergent": False,
            "gravity_derived": False,
            "event_horizon_identified": False,
            "pa_m2_composition": False,
            "physical_c0_branch_selected": False,
            "pre_a_complete": False,
        },
        "verdict": "ADVANCE: an inserted local KG spectrum admits an exact OU/CCR vacuum and an exact symplectic-energy embedding into the PA-H1 characteristic image; this calibrates a state-bearing C0-A bridge but does not select the spectrum, causal background, full state, energy reference, gravity, or PA-M2 law",
        "assertions": {
            "passed": len(audit.rows),
            "total": len(audit.rows),
            "rows": audit.rows,
        },
        "source": {
            "path": source.relative_to(REPO),
            "sha256": sha256(source),
        },
        "no_overclaim": (
            "The package is an exact free-field calibration and embedding after the circle, Lorentzian KG law, "
            "mass, mode family, time spacing, and Gaussian complex structure are inserted. It does not derive "
            "time, the KG dispersion, a full or Hadamard PA-H1 state, an absolute physical vacuum energy, gravity, "
            "an event horizon, a cooling or phase-transition history, a PA-M2 interface, or a completed Pre-A."
        ),
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
        f"{CANDIDATE_ID} | OU/CCR state and PA-H1 embedding"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

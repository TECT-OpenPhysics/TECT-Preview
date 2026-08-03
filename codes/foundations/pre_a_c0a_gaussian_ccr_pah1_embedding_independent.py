#!/usr/bin/env python3
"""Non-importing independent audit of the Gaussian/CCR/PA-H1 embedding.

This implementation uses exact rational covariance arithmetic and a
top-slice-centred Fourier trace construction.  It does not import the primary
certificate and deliberately reconstructs the boundary matrices by a distinct
coordinate convention.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

import sympy as sp


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
CANDIDATE_ID = "PA-C0A-GAUSSIAN-CCR-PAH1-EMBEDDING-v0"
SLUG = "pre-a-c0a-gaussian-ccr-pah1-embedding"
SCHEMA = f"tect/{SLUG}-independent/0.1"
CLAIM_CONTEXT = "C6-SPACETIME-SIGNATURE"
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


def diagonal_product(left: list[Fraction], middle: list[Fraction], right: list[Fraction]) -> list[Fraction]:
    return [left[index] * middle[index] * right[index] for index in range(len(left))]


def add_vectors(left: list[Fraction], right: list[Fraction]) -> list[Fraction]:
    return [left[index] + right[index] for index in range(len(left))]


def fourier_add(*items: dict[int, sp.Expr]) -> dict[int, sp.Expr]:
    result: dict[int, sp.Expr] = {}
    for item in items:
        for harmonic, coefficient in item.items():
            result[harmonic] = sp.simplify(result.get(harmonic, 0) + coefficient)
    return {harmonic: coefficient for harmonic, coefficient in result.items() if coefficient != 0}


def fourier_scale(item: dict[int, sp.Expr], factor: sp.Expr) -> dict[int, sp.Expr]:
    return {harmonic: sp.simplify(factor * coefficient) for harmonic, coefficient in item.items()}


def fourier_convolve(left: dict[int, sp.Expr], right: dict[int, sp.Expr]) -> dict[int, sp.Expr]:
    result: dict[int, sp.Expr] = {}
    for left_harmonic, left_coefficient in left.items():
        for right_harmonic, right_coefficient in right.items():
            harmonic = left_harmonic + right_harmonic
            result[harmonic] = sp.simplify(
                result.get(harmonic, 0) + left_coefficient * right_coefficient
            )
    return {harmonic: coefficient for harmonic, coefficient in result.items() if coefficient != 0}


def fourier_derivative(item: dict[int, sp.Expr]) -> dict[int, sp.Expr]:
    return {
        harmonic: sp.simplify(sp.I * sp.Rational(harmonic, 2) * coefficient)
        for harmonic, coefficient in item.items()
    }


def fourier_integral(item: dict[int, sp.Expr], length: sp.Expr) -> sp.Expr:
    value = sp.Integer(0)
    for harmonic, coefficient in item.items():
        if harmonic == 0:
            kernel = length
        else:
            kernel = 2 * (
                sp.exp(sp.I * sp.Rational(harmonic, 2) * length) - 1
            ) / (sp.I * harmonic)
        value += coefficient * kernel
    return sp.simplify(sp.expand_complex(value))


def inner(left: dict[int, sp.Expr], right: dict[int, sp.Expr], length: sp.Expr) -> sp.Expr:
    return fourier_integral(fourier_convolve(left, right), length)


def temporal_trace(frequency: int, kind: str, tau: sp.Expr) -> dict[int, sp.Expr]:
    plus_phase = sp.exp(-sp.I * frequency * tau)
    minus_phase = sp.exp(sp.I * frequency * tau)
    if kind == "q":
        return {frequency: plus_phase / 2, -frequency: minus_phase / 2}
    if kind == "p":
        return {
            frequency: plus_phase / (2 * sp.I * frequency),
            -frequency: -minus_phase / (2 * sp.I * frequency),
        }
    raise ValueError(kind)


def spatial_trace(kind: str, wave_number: int) -> dict[int, sp.Expr]:
    if kind == "constant":
        if wave_number != 0:
            raise ValueError("constant mode must have zero wave number")
        return {0: sp.Integer(1)}
    if kind == "cos":
        return {
            wave_number: sp.Rational(1, 2),
            -wave_number: sp.Rational(1, 2),
        }
    if kind == "sin":
        return {
            wave_number: 1 / (2 * sp.I),
            -wave_number: -1 / (2 * sp.I),
        }
    raise ValueError(kind)


def derive() -> dict[str, Any]:
    audit = Audit()

    # Exact rational OU arithmetic, independent of the primary matrix path.
    # Inserted exact fixture frequencies.  Every derived gap, mass coefficient,
    # and zero-point shift below is computed from this single source.
    frequencies = [3, 5, 5]
    mass = frequencies[0]
    wave_numbers = [
        int(sp.sqrt(frequency**2 - mass**2)) for frequency in frequencies
    ]
    kappa = Fraction(mass**2, 4)
    spectral_gap = min(frequencies)
    zero_point_energy = Fraction(sum(frequencies), 2)
    covariance = [Fraction(1, 2 * frequency) for frequency in frequencies]
    transfer = [Fraction(1, 2**frequency) for frequency in frequencies]
    noise = [
        covariance[index] * (1 - transfer[index] ** 2)
        for index in range(3)
    ]
    stationary = add_vectors(
        diagonal_product(transfer, covariance, transfer), noise
    )
    audit.check(
        "independent stationary Mehler covariance",
        stationary == covariance,
        stationary,
        covariance,
        "gaussian_transfer",
    )
    transfer_three = [Fraction(1, 3**frequency) for frequency in frequencies]
    noise_three = [
        covariance[index] * (1 - transfer_three[index] ** 2)
        for index in range(3)
    ]
    composed_noise = add_vectors(
        noise,
        diagonal_product(transfer, noise_three, transfer),
    )
    composed_transfer = [
        transfer[index] * transfer_three[index] for index in range(3)
    ]
    direct_composed_noise = [
        covariance[index] * (1 - composed_transfer[index] ** 2)
        for index in range(3)
    ]
    audit.check(
        "independent Mehler semigroup covariance law",
        composed_noise == direct_composed_noise,
        composed_noise,
        direct_composed_noise,
        "gaussian_transfer",
    )
    audit.check(
        "independent inserted covariance",
        covariance == [Fraction(1, 6), Fraction(1, 10), Fraction(1, 10)],
        covariance,
        [Fraction(1, 6), Fraction(1, 10), Fraction(1, 10)],
        "gaussian_transfer",
    )
    audit.check(
        "independent one-step transfer",
        transfer == [Fraction(1, 8), Fraction(1, 32), Fraction(1, 32)],
        transfer,
        [Fraction(1, 8), Fraction(1, 32), Fraction(1, 32)],
        "gaussian_transfer",
    )

    energies: dict[tuple[int, int, int], int] = {}
    eigenvalues: dict[tuple[int, int, int], Fraction] = {}
    for n0 in range(6):
        for nc in range(4):
            for ns in range(4):
                multiindex = (n0, nc, ns)
                energy = sum(multiindex[index] * frequencies[index] for index in range(3))
                energies[multiindex] = energy
                eigenvalues[multiindex] = Fraction(1, 2**energy)
    audit.check(
        "independent unique zero occupation",
        [key for key, value in energies.items() if value == 0] == [(0, 0, 0)],
        [key for key, value in energies.items() if value == 0],
        [(0, 0, 0)],
        "fock_spectrum",
    )
    audit.check(
        "independent occupation gap",
        min(value for value in energies.values() if value > 0) == min(frequencies),
        min(value for value in energies.values() if value > 0),
        min(frequencies),
        "fock_spectrum",
    )
    rayleigh_sequence = [Fraction(1, 2 ** (frequencies[0] * level)) for level in range(1, 9)]
    audit.check(
        "independent transfer eigenvalues descend toward zero",
        all(
            rayleigh_sequence[index + 1] < rayleigh_sequence[index]
            for index in range(len(rayleigh_sequence) - 1)
        )
        and rayleigh_sequence[-1] < Fraction(1, 10**6),
        rayleigh_sequence,
        "strictly decreasing with final below 1e-6",
        "unbounded_generator_boundary",
    )
    trace_value = Fraction(1, 1)
    for value in transfer:
        trace_value *= 1 / (1 - value)
    audit.check(
        "independent trace-class partition sum",
        trace_value == Fraction(8192, 6727),
        trace_value,
        Fraction(8192, 6727),
        "fock_spectrum",
    )

    # Independent non-selection and negative controls.
    scalar_covariance = Fraction(1, 2)
    rho_bad = Fraction(-1, 2)
    bad_noise = scalar_covariance * (1 - rho_bad**2)
    bad_form = rho_bad * scalar_covariance
    audit.check(
        "independent negative AR1 noise remains positive",
        bad_noise == Fraction(3, 8),
        bad_noise,
        Fraction(3, 8),
        "negative_controls",
    )
    audit.check(
        "independent negative AR1 reflection form",
        bad_form == Fraction(-1, 4),
        bad_form,
        Fraction(-1, 4),
        "negative_controls",
    )
    distinct_drifts = []
    for drift in (1, 2):
        rho = Fraction(1, 2**drift)
        distinct_drifts.append((rho, scalar_covariance * (1 - rho**2), drift))
    audit.check(
        "independent same-marginal different-drift control",
        distinct_drifts
        == [
            (Fraction(1, 2), Fraction(3, 8), 1),
            (Fraction(1, 4), Fraction(15, 32), 2),
        ],
        distinct_drifts,
        "same covariance with distinct transfers and gaps",
        "nonselection_controls",
    )

    # Quasi-free phase-space algebra by a distinct direct block check.
    omega = sp.diag(*frequencies)
    I3 = sp.eye(3)
    Z3 = sp.zeros(3)
    sigma = Z3.row_join(I3).col_join((-I3).row_join(Z3))
    J = Z3.row_join(-omega.inv()).col_join(omega.row_join(Z3))
    G = sp.simplify(sigma * J)
    audit.check(
        "independent complex structure",
        J**2 == -sp.eye(6),
        J**2,
        -sp.eye(6),
        "quasi_free_state",
    )
    audit.check(
        "independent symplectic compatibility",
        sp.simplify(J.T * sigma * J) == sigma,
        sp.simplify(J.T * sigma * J),
        sigma,
        "quasi_free_state",
    )
    audit.check(
        "independent positive covariance metric",
        G == sp.diag(3, 5, 5, sp.Rational(1, 3), sp.Rational(1, 5), sp.Rational(1, 5)),
        G,
        sp.diag(3, 5, 5, sp.Rational(1, 3), sp.Rational(1, 5), sp.Rational(1, 5)),
        "quasi_free_state",
    )
    for frequency in frequencies:
        positivity_block = sp.Matrix([[frequency, sp.I], [-sp.I, sp.Rational(1, frequency)]])
        audit.check(
            f"independent quasi-free PSD block omega={frequency}",
            positivity_block.det() == 0 and positivity_block.trace() > 0,
            (positivity_block.det(), positivity_block.trace()),
            (0, ">0"),
            "quasi_free_state",
        )

    # Top-slice-centred characteristic trace construction.  Fourier keys m
    # represent exp(i*m*s/2), so every integral is exact.
    length = sp.pi / 2
    tau = length / 2
    root_pi = sp.sqrt(sp.pi)
    temporal_q3 = temporal_trace(frequencies[0], "q", tau)
    temporal_p3 = temporal_trace(frequencies[0], "p", tau)
    temporal_q5 = temporal_trace(frequencies[1], "q", tau)
    temporal_p5 = temporal_trace(frequencies[1], "p", tau)
    constant = spatial_trace("constant", wave_numbers[0])
    cosine = spatial_trace("cos", wave_numbers[1])
    sine = spatial_trace("sin", wave_numbers[2])
    traces_a = [
        fourier_scale(fourier_convolve(temporal_q3, constant), sp.sqrt(2 / sp.pi)),
        fourier_scale(fourier_convolve(temporal_q5, cosine), 2 / root_pi),
        fourier_scale(fourier_convolve(temporal_q5, sine), 2 / root_pi),
        fourier_scale(fourier_convolve(temporal_p3, constant), sp.sqrt(2 / sp.pi)),
        fourier_scale(fourier_convolve(temporal_p5, cosine), 2 / root_pi),
        fourier_scale(fourier_convolve(temporal_p5, sine), 2 / root_pi),
    ]
    traces_b = [
        item if index not in (2, 5) else fourier_scale(item, -1)
        for index, item in enumerate(traces_a)
    ]
    boundary_sigma = sp.zeros(6)
    boundary_energy = sp.zeros(6)
    kappa_sympy = sp.Rational(kappa.numerator, kappa.denominator)
    for row in range(6):
        for column in range(6):
            da_row = fourier_derivative(traces_a[row])
            da_column = fourier_derivative(traces_a[column])
            db_row = fourier_derivative(traces_b[row])
            db_column = fourier_derivative(traces_b[column])
            boundary_sigma[row, column] = sp.simplify(
                inner(traces_a[row], da_column, length)
                - inner(traces_a[column], da_row, length)
                + inner(traces_b[row], db_column, length)
                - inner(traces_b[column], db_row, length)
            )
            boundary_energy[row, column] = sp.simplify(
                inner(da_row, da_column, length)
                + kappa_sympy * inner(traces_a[row], traces_a[column], length)
                + inner(db_row, db_column, length)
                + kappa_sympy * inner(traces_b[row], traces_b[column], length)
            )
    expected_energy = sp.diag(
        *(sp.Rational(frequency**2, 2) for frequency in frequencies),
        *(sp.Rational(1, 2) for _ in frequencies),
    )
    audit.check(
        "independent centred-trace boundary symplectic Gram",
        boundary_sigma == sigma,
        boundary_sigma,
        sigma,
        "pah1_embedding",
    )
    audit.check(
        "independent centred-trace boundary energy Gram",
        boundary_energy == expected_energy,
        boundary_energy,
        expected_energy,
        "pah1_embedding",
    )

    t = sp.symbols("t", real=True)
    q_symbol, p_symbol = sp.symbols("q_symbol p_symbol", real=True)
    for frequency in sorted(set(frequencies)):
        coefficient = q_symbol * sp.cos(frequency * (t - tau)) + p_symbol * sp.sin(
            frequency * (t - tau)
        ) / frequency
        audit.check(
            f"centred KG coefficient returns q at top for omega={frequency}",
            sp.simplify(coefficient.subs(t, tau) - q_symbol) == 0,
            coefficient.subs(t, tau),
            q_symbol,
            "pah1_embedding",
        )
        audit.check(
            f"centred KG coefficient returns p at top for omega={frequency}",
            sp.simplify(sp.diff(coefficient, t).subs(t, tau) - p_symbol) == 0,
            sp.diff(coefficient, t).subs(t, tau),
            p_symbol,
            "pah1_embedding",
        )

    # Finite-rank state/locality and full-extension controls.
    x, y = sp.symbols("x y", real=True)
    mode_normalizations = [
        1 / sp.sqrt(length),
        sp.sqrt(2 / length),
        sp.sqrt(2 / length),
    ]
    modes = [
        mode_normalizations[0],
        mode_normalizations[1] * sp.cos(wave_numbers[1] * x),
        mode_normalizations[2] * sp.sin(wave_numbers[2] * x),
    ]
    modes_y = [
        mode_normalizations[0],
        mode_normalizations[1] * sp.cos(wave_numbers[1] * y),
        mode_normalizations[2] * sp.sin(wave_numbers[2] * y),
    ]
    projector_kernel = sp.simplify(
        sum(modes[index] * modes_y[index] for index in range(3))
    )
    projector_witness = sp.simplify(projector_kernel.subs({x: 0, y: sp.pi / 8}))
    audit.check(
        "independent finite-rank locality counterexample",
        projector_witness == 2 / sp.pi,
        projector_witness,
        2 / sp.pi,
        "locality_boundary",
    )
    wightman_equal_time = sp.simplify(
        sum(
            modes[index] * modes_y[index] / (2 * frequencies[index])
            for index in range(3)
        )
    )
    audit.check(
        "independent finite-mode equal-time covariance witness",
        sp.simplify(wightman_equal_time.subs({x: 0, y: sp.pi / 8}))
        == 1 / (3 * sp.pi),
        sp.simplify(wightman_equal_time.subs({x: 0, y: sp.pi / 8})),
        1 / (3 * sp.pi),
        "state_extension_boundary",
    )
    full_stiffness = sp.diag(1, 4)
    trial = sp.Matrix([1, 1]) / sp.sqrt(2)
    projection = trial * trial.T
    residual = sp.simplify((sp.eye(2) - projection) * full_stiffness * trial)
    residual_squared_oracle = sp.simplify(
        (full_stiffness[1, 1] - full_stiffness[0, 0]) ** 2 / 4
    )
    audit.check(
        "independent noninvariant Galerkin residual",
        sp.simplify((residual.T * residual)[0]) == residual_squared_oracle,
        sp.simplify((residual.T * residual)[0]),
        residual_squared_oracle,
        "intertwiner_boundary",
    )

    source = Path(__file__).resolve()
    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "candidate_id": CANDIDATE_ID,
        "candidate_family": "C0A-GAUSSIAN-OU-CCR-PAH1-EMBEDDING",
        "version": __version__,
        "issued": "2026-08-03",
        "authority": "T0 non-importing independent audit; no TECT claim or tier change",
        "claim_context": CLAIM_CONTEXT,
        "claim_bearing": False,
        "task_id": "T-054",
        "shared_exact_results": {
            "frequencies": frequencies,
            "covariance": covariance,
            "transfer": transfer,
            "unique_vacuum": True,
            "gap": spectral_gap,
            "trace_at_log2": trace_value,
            "transfer_injective_but_not_bounded_below": True,
            "generator_unbounded": True,
            "full_time_reflection_positivity": True,
            "quasi_free_state": True,
            "normal_ordered_vacuum_energy": 0,
            "unnormalised_zero_point_energy": zero_point_energy,
            "pah1_top_slice_reconstruction": "P_tau B_tau=id on the centred finite mode phase space",
            "pah1_boundary_symplectic": True,
            "pah1_boundary_energy": True,
            "finite_fock_exact_ccr": False,
            "finite_image_full_state_selection": False,
            "finite_spectral_cutoff_local": False,
            "generic_galerkin_dynamical_intertwiner": False,
            "hadamard_certified": False,
            "absolute_vacuum_energy_derived": False,
            "pre_a_complete": False,
        },
        "scope": {
            "finite_spatial_mode_infinite_occupation_semigroup": True,
            "exact_quasi_free_ccr_state": True,
            "exact_pah1_finite_image_embedding": True,
            "full_pah1_state": False,
            "hadamard_limit": False,
            "spatial_locality": False,
            "causal_cone": False,
            "absolute_vacuum_energy": False,
            "hbar_origin": False,
            "kg_dispersion_derived": False,
            "physical_c0_selection": False,
            "pa_m2_composition": False,
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
        "no_overclaim": (
            "This independent audit confirms a standard finite-mode Gaussian/Fock reconstruction and an exact "
            "state-bearing embedding into only the PA-H1 finite image. It does not derive the inserted KG spectrum, "
            "time order, hbar normalization, locality, a full/Hadamard state, absolute vacuum energy, gravity, "
            "a PA-M2 composition, or Pre-A."
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
        f"{CANDIDATE_ID} | independent top-slice-centred audit"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

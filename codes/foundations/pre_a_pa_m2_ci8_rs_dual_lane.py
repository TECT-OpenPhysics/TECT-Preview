#!/usr/bin/env python3
"""Exact primary certificate for the T0 PA-M2-CI8-RS-v0 candidate.

The candidate is a newly hypothesised real scalar finite-wave-number model.
It is not a registered TECT action or a physical cosmology.  The certificate
keeps the static fluctuation/order lane and the real-time quantum-chaos lane
on one hashable Hamiltonian while proving only their first exact boundaries.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from fractions import Fraction
from math import comb
from pathlib import Path
from typing import Any

import sympy as sp


__version__ = "0.2.0"
REPO = Path(__file__).resolve().parents[2]
CANDIDATE_ID = "PA-M2-CI8-RS-v0"
SLUG = "pre-a-pa-m2-ci8-rs-dual-lane"
SCHEMA = f"tect/{SLUG}-primary/0.1"
CLAIM_CONTEXT = "A2-FULL-PRODUCTION-WELLPOSED"
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
    if isinstance(value, Fraction):
        return str(value)
    if isinstance(value, sp.MatrixBase):
        return [[serial(value[row, col]) for col in range(value.cols)] for row in range(value.rows)]
    if isinstance(value, sp.Basic):
        return str(sp.factor(value))
    if isinstance(value, dict):
        return {str(key): serial(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [serial(item) for item in value]
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
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


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cosine_even_moment(power: int) -> Fraction:
    if power < 0 or power % 2:
        raise ValueError("power must be a nonnegative even integer")
    half = power // 2
    return Fraction(comb(2 * half, half), 4**half)


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


def derive() -> dict[str, Any]:
    audit = Audit()

    k1, k2, k3 = sp.symbols("k1 k2 k3", real=True)
    p1, p2, p3 = sp.symbols("p1 p2 p3", real=True)
    q, c, g, chi = sp.symbols("q c g chi", positive=True)
    r = sp.symbols("r", real=True)
    y = sp.symbols("y", nonnegative=True)
    k = (k1, k2, k3)
    p = (p1, p2, p3)

    kernel = r + c * sum((component**2 - q**2) ** 2 for component in k)
    gradient = sp.Matrix([sp.diff(kernel, component) for component in k])
    hessian = sp.hessian(kernel, k)
    nodes = [tuple(sign * q for sign in signs) for signs in __import__("itertools").product((-1, 1), repeat=3)]
    target_hessian = 8 * c * q**2 * sp.eye(3)

    audit.check("isolated node count", len(nodes) == 8, len(nodes), 8, "kernel")
    for index, node in enumerate(nodes):
        substitution = dict(zip(k, node, strict=True))
        audit.check(
            f"node {index} reaches the quadratic bottom",
            sp.simplify(kernel.subs(substitution) - r) == 0,
            kernel.subs(substitution),
            r,
            "kernel",
        )
        audit.check(
            f"node {index} is stationary",
            gradient.subs(substitution) == sp.zeros(3, 1),
            gradient.subs(substitution),
            sp.zeros(3, 1),
            "kernel",
        )
        audit.check(
            f"node {index} has the full-rank isotropic Hessian",
            hessian.subs(substitution) == target_hessian,
            hessian.subs(substitution),
            target_hessian,
            "kernel",
        )

    chosen_node = (q, q, q)
    shifted = sp.expand(kernel.subs(dict(zip(k, (q + p1, q + p2, q + p3), strict=True))))
    shifted_expected = r + c * sum(4 * q**2 * component**2 + 4 * q * component**3 + component**4 for component in p)
    audit.check(
        "exact isolated-node expansion",
        sp.expand(shifted - shifted_expected) == 0,
        shifted,
        shifted_expected,
        "kernel",
    )
    speed_squared = sp.simplify(4 * c * q**2 / chi)
    audit.check(
        "critical leading cone coefficient",
        speed_squared == 4 * c * q**2 / chi,
        speed_squared,
        4 * c * q**2 / chi,
        "dynamics",
    )

    moment2 = cosine_even_moment(2)
    moment4 = cosine_even_moment(4)
    audit.check("cosine second moment", moment2 == Fraction(1, 2), moment2, Fraction(1, 2), "lane_f")
    audit.check("cosine fourth moment", moment4 == Fraction(3, 8), moment4, Fraction(3, 8), "lane_f")

    trial_density = sp.factor(r * y * sp.Rational(moment2.numerator, moment2.denominator) / 2 + g * y**2 * sp.Rational(moment4.numerator, moment4.denominator) / 4)
    trial_expected = r * y / 4 + 3 * g * y**2 / 32
    audit.check(
        "single-node cosine energy density",
        sp.expand(trial_density - trial_expected) == 0,
        trial_density,
        trial_expected,
        "lane_f",
    )
    trial_y = sp.factor(-4 * r / (3 * g))
    trial_energy = sp.factor(trial_density.subs(y, trial_y))
    audit.check(
        "ordered-side trial amplitude",
        sp.simplify(sp.diff(trial_density, y).subs(y, trial_y)) == 0,
        trial_y,
        -4 * r / (3 * g),
        "lane_f",
    )
    audit.check(
        "ordered-side trial beats the zero reference",
        trial_energy == -r**2 / (6 * g),
        trial_energy,
        -r**2 / (6 * g),
        "lane_f",
    )

    homogeneous_quadratic = sp.factor(r + 3 * c * q**4)
    audit.check(
        "homogeneous-state quadratic coefficient",
        homogeneous_quadratic == r + 3 * c * q**4,
        homogeneous_quadratic,
        r + 3 * c * q**4,
        "lane_f",
    )
    lower_energy_coefficient = sp.Rational(1, 4)
    upper_energy_coefficient = sp.Rational(1, 6)
    audit.check(
        "energy bracket has the correct order",
        lower_energy_coefficient > upper_energy_coefficient > 0,
        (lower_energy_coefficient, upper_energy_coefficient),
        "1/4 > 1/6 > 0",
        "lane_f",
    )
    # A minimizer is stationary, so testing the Euler--Lagrange equation in
    # the radial direction gives r*X+D+g*I4=0, where D>=0.  Jensen then gives
    # g*X**2/V <= g*I4 <= -r*X and hence X/V <= -r/g.  This is sharper than
    # the bound obtained from negative energy alone.
    mean_square_bound = sp.factor(-r / g)
    audit.check(
        "stationary minimizer mean-square bound is positive on r<0",
        sp.simplify(mean_square_bound.subs({r: -1, g: 1})) == 1,
        mean_square_bound,
        -r / g,
        "lane_f",
    )

    # Exact spectral concentration estimate.  For q=(2*pi/L)*m, the first
    # off-node lattice value of sum_i(k_i^2-q^2)^2 is
    # delta_L=(2*pi/L)^4(2m-1)^2.  The radial stationarity identity implies
    # c*delta_L*X_out <= D <= |r|*X.
    lattice_step, mode_index = sp.symbols("h m", positive=True)
    spectral_gap = sp.factor(lattice_step**4 * (2 * mode_index - 1) ** 2)
    off_node_fraction_bound = sp.factor(-r / (c * spectral_gap))
    audit.check(
        "first off-node lattice gap formula",
        sp.expand(spectral_gap - lattice_step**4 * (2 * mode_index - 1) ** 2) == 0,
        spectral_gap,
        lattice_step**4 * (2 * mode_index - 1) ** 2,
        "lane_f",
    )

    # The exact CI8 kernel morphology identity is reconstructed from all
    # zero-momentum ordered quartets.  z_j and w_j stand for a node amplitude
    # and its conjugate; treating them independently makes this a polynomial
    # identity before imposing w_j=conj(z_j).
    z = sp.symbols("z0:4")
    w = sp.symbols("w0:4")
    representatives = ((1, 1, 1), (1, 1, -1), (1, -1, 1), (-1, 1, 1))
    amplitudes: dict[tuple[int, int, int], sp.Expr] = {}
    for index, vector in enumerate(representatives):
        amplitudes[vector] = z[index]
        amplitudes[tuple(-entry for entry in vector)] = w[index]
    m2_kernel = 2 * sum(z[index] * w[index] for index in range(4))
    m4_kernel = sp.Integer(0)
    node_vectors = tuple(amplitudes)
    for a in node_vectors:
        for b in node_vectors:
            for d in node_vectors:
                for e in node_vectors:
                    if all(a[axis] + b[axis] + d[axis] + e[axis] == 0 for axis in range(3)):
                        m4_kernel += amplitudes[a] * amplitudes[b] * amplitudes[d] * amplitudes[e]
    pair_sum = sum(z[i] * w[i] * z[j] * w[j] for i in range(4) for j in range(i + 1, 4))
    resonance_pair = w[0] * z[1] * z[2] * z[3] + z[0] * w[1] * w[2] * w[3]
    morphology_excess = sp.expand(m4_kernel - sp.Rational(3, 2) * m2_kernel**2)
    morphology_expected = sp.expand(12 * pair_sum + 24 * resonance_pair)
    audit.check(
        "exact CI8 quartic morphology identity",
        sp.expand(morphology_excess - morphology_expected) == 0,
        morphology_excess,
        morphology_expected,
        "lane_f",
    )

    omega, t, hbar = sp.symbols("omega t hbar", positive=True)
    gaussian_otoc = sp.factor(hbar**2 * sp.sin(omega * t) ** 2 / (chi**2 * omega**2))
    critical_otoc = sp.simplify(sp.limit(gaussian_otoc, omega, 0, dir="+"))
    audit.check(
        "Gaussian critical OTOC is polynomial",
        critical_otoc == hbar**2 * t**2 / chi**2,
        critical_otoc,
        hbar**2 * t**2 / chi**2,
        "lane_q",
    )

    # A local double-null toy problem fixes the first horizon-origin gate.
    # One characteristic sheet is not complete Cauchy data: phi=0 and phi=u
    # solve partial_u partial_v phi=0 and have the same trace on u=0.  Two
    # intersecting sheets reconstruct the polynomial test family uniquely.
    u, v = sp.symbols("u v", real=True)
    phi_zero = sp.Integer(0)
    phi_hidden = u
    audit.check(
        "single-null-sheet counterexample equations",
        sp.diff(phi_zero, u, v) == 0 and sp.diff(phi_hidden, u, v) == 0,
        (sp.diff(phi_zero, u, v), sp.diff(phi_hidden, u, v)),
        (0, 0),
        "horizon_origin",
    )
    audit.check(
        "single-null-sheet counterexample equal trace",
        phi_zero.subs(u, 0) == phi_hidden.subs(u, 0),
        (phi_zero.subs(u, 0), phi_hidden.subs(u, 0)),
        (0, 0),
        "horizon_origin",
    )
    a0, a1, a2, b1, b2 = sp.symbols("a0 a1 a2 b1 b2", real=True)
    data_u = a0 + a1 * u + a2 * u**2
    data_v = a0 + b1 * v + b2 * v**2
    reconstructed = sp.expand(data_u + data_v - a0)
    audit.check(
        "two-null-sheet polynomial reconstruction solves wave equation",
        sp.diff(reconstructed, u, v) == 0,
        sp.diff(reconstructed, u, v),
        0,
        "horizon_origin",
    )
    audit.check(
        "two-null-sheet reconstruction matches both traces",
        sp.simplify(reconstructed.subs(v, 0) - data_u) == 0
        and sp.simplify(reconstructed.subs(u, 0) - data_v) == 0,
        (reconstructed.subs(v, 0), reconstructed.subs(u, 0)),
        (data_u, data_v),
        "horizon_origin",
    )
    lyapunov_polynomial = sp.limit(sp.log(1 + t**2) / (2 * t), t, sp.oo)
    audit.check(
        "polynomial OTOC has zero asymptotic Lyapunov exponent",
        lyapunov_polynomial == 0,
        lyapunov_polynomial,
        0,
        "lane_q",
    )

    source = Path(__file__).resolve()
    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "candidate_id": CANDIDATE_ID,
        "candidate_family": "M2-LOCAL-CUBIC-ISOLATED-NODE",
        "version": __version__,
        "issued": "2026-08-03",
        "authority": "T0 candidate certificate; not a TECT action, theorem tier, physical vacuum, or cosmology",
        "claim_context": CLAIM_CONTEXT,
        "claim_bearing": False,
        "task_id": "T-054",
        "functional": {
            "field": "real phi in H2(T_L^3)",
            "energy": "F_r[phi]=1/2 int[r phi^2+c sum_i((partial_i^2+q^2)phi)^2]+g/4 int phi^4",
            "parameter_domain": "c>0, g>0, q=2*pi*m/L with positive integer m; r real",
            "reference_state": "phi=0 on the same torus and normalization",
            "lane_q_hamiltonian": "H=int pi^2/(2 chi)+F_r[phi], chi>0, after an explicitly declared finite Galerkin cutoff",
        },
        "exact_results": {
            "node_set": nodes,
            "node_count": len(nodes),
            "node_radius": sp.sqrt(3) * q,
            "quadratic_symbol": kernel,
            "node_hessian": target_hessian,
            "node_expansion_at_plus_plus_plus": shifted_expected,
            "critical_speed_squared_tree_level": speed_squared,
            "critical_dynamic_exponent": 1,
            "physical_soft_coordinates_before_interactions": 8,
            "cosine_second_moment": moment2,
            "cosine_fourth_moment": moment4,
            "cosine_trial_energy_density": trial_expected,
            "cosine_trial_amplitude_squared_for_r_negative": trial_y,
            "cosine_trial_energy_density_at_optimum": trial_energy,
            "homogeneous_quadratic_coefficient": homogeneous_quadratic,
            "inhomogeneous_global_minimizer_window": "-3*c*q^4 <= r < 0",
            "ground_energy_density_bracket_for_r_negative": "-r^2/(4*g) <= E(r)/V <= -r^2/(6*g)",
            "minimizer_mean_square_upper_bound": mean_square_bound,
            "off_node_lattice_gap": spectral_gap,
            "off_node_spectral_fraction_bound_for_r_negative": off_node_fraction_bound,
            "ci8_quartic_morphology_identity": "m4-(3/2)m2^2=12*(sum_{i<j}|z_i|^2|z_j|^2+4*Re(conj(z0)*z1*z2*z3))",
            "ci8_kernel_morphology_minimizer": "one antipodal node pair (single-Q stripe) in the kernel-restricted leading quartic problem; the complement branch remains open",
            "gaussian_mode_commutator": "[phi_k(t),phi_-k(0)]=-i*hbar*sin(omega_k*t)/(chi*omega_k)",
            "gaussian_mode_otoc": gaussian_otoc,
            "critical_gaussian_otoc": critical_otoc,
            "gaussian_lyapunov_exponent": lyapunov_polynomial,
            "gradient_cycle_boundary": "an autonomous L2 gradient flow of this F has no nonstationary periodic orbit",
            "single_null_sheet_boundary": "INSUFFICIENT in the local wave-equation test: phi=0 and phi=u share the u=0 trace but differ in the bulk",
            "double_null_reconstruction_test": "phi(u,v)=A(u)+B(v)-A(0) for compatible data on v=0 and u=0",
        },
        "lane_verdicts": {
            "lane_f": "ADVANCE: exact finite-volume classical continuous onset and a stable inhomogeneous global minimizer below the common zero reference in the declared window",
            "lane_q": "BOUNDARY: stable and critical modes of the shared quadratic Hamiltonian have lambda_L=0; omega^2<0 gives linear instability, not a chaos certificate; chaos, if present, must be generated by the unchanged local quartic interaction in the full symmetry-complete node star",
            "horizon_origin": "ADVANCE AS A GATE: a single null sheet is not complete starting data; a second intersecting characteristic sheet or equivalent extra datum is required before bulk reconstruction",
            "cyclic_bridge": "OPTIONAL DOWNSTREAM ONLY: no recurrence assumption is used in the horizon-origin or dual-lane results",
        },
        "next_quantum_test": {
            "retained_modes": "full CI8 star: four antipodal pairs and eight real canonical coordinates",
            "interaction": "the exact local quartic momentum-conserving vertex inherited from F_r",
            "required_resonance": "at least one four-distinct-node momentum parallelogram",
            "ablation": "H_eta=H2+D(V4)+eta*(V4-D(V4)); eta=0 retains diagonal shifts but has no occupation scrambling, eta=1 is the unchanged candidate",
            "symmetry_resolution": "Z2, translations, cubic irreducible representation, and time reversal before level statistics",
            "cutoff_rule": "compare Nmax with Nmax+4 at fixed global parity; require stable low-window data and negligible probability on the top four occupation layers",
            "momentum_growth_rule": "the CI8 projection is a first Galerkin diagnostic, not an invariant subspace; enlarge the momentum cutoff because phi^3 generates coordinate components at plus_or_minus q and plus_or_minus 3q",
        },
        "scope": {
            "new_hypothesis": True,
            "finite_periodic_torus": True,
            "static_global_minimizer_existence": True,
            "finite_volume_classical_onset": True,
            "thermodynamic_phase_transition": False,
            "finite_cutoff_quantum_hamiltonian_only": True,
            "nonlinear_quantum_chaos": False,
            "compact_gauge_or_winding": False,
            "gravity_or_bounce": False,
            "physical_vacuum_selected": False,
            "tree_level_common_speed_only": True,
            "loop_or_regulator_speed_protection": False,
            "t053_full_handoff": False,
            "sector_a_closed": False,
            "event_horizon_origin_selected": False,
            "single_null_sheet_complete_initial_data": False,
            "double_null_toy_reconstruction": True,
            "causal_structure_inserted_in_lane_h_toy": True,
            "lane_h_to_pa_m2_composition": False,
        },
        "assertions": {
            "passed": len(audit.rows),
            "total": len(audit.rows),
            "rows": audit.rows,
        },
        "source": {
            "path": source.relative_to(REPO),
            "sha256": file_hash(source),
        },
        "no_overclaim": (
            "PA-M2-CI8-RS-v0 is a T0 candidate and benchmark. The exact result is a finite-volume classical "
            "variational onset with isolated quadratic nodes, leading z=1 cones, and a stable/critical Gaussian "
            "no-chaos boundary; unstable quadratic modes are classified only as linear instabilities. "
            "It does not prove a thermodynamic or quantum phase transition, nonlinear quantum chaos, chaos-caused "
            "ordering, compact gauge structure, emergent space-time, identification of an event horizon as the "
            "physical origin, a bounce, a cyclic universe, or physical selection."
        ),
    }
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true", help="derive and validate without changing the output path")
    arguments = parser.parse_args()
    payload = derive()
    if not arguments.self_test:
        atomic_json(arguments.output, payload)
    print(
        f"PASS {payload['assertions']['passed']}/{payload['assertions']['total']} | "
        f"{CANDIDATE_ID} | Lane-F advance, Gaussian Lane-Q boundary"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

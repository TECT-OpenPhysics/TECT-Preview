#!/usr/bin/env python3
"""Primary exact certificate for PA-C0-DYNAMICAL-COMPLETION-NOGO-v0.

The certificate proves a model-theoretic underdetermination statement: a
static functional, by itself, does not select a unique temporal completion.
It compares dissipative and inertial completions with the same equilibria and
static Hessian, and applies the distinction to the PA-M2 soft node.  This is a
T0 boundary result, not a derivation of time, causality, light, or gravity.
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
CANDIDATE_ID = "PA-C0-DYNAMICAL-COMPLETION-NOGO-v0"
SLUG = "pre-a-c0-dynamical-completion-underdetermination"
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


def derive() -> dict[str, Any]:
    audit = Audit()

    # A nonlinear one-mode fixture makes the common-equilibrium statement
    # explicit without using a quadratic-only special case.
    x = sp.symbols("x", real=True)
    lam = sp.symbols("lambda", positive=True)
    quartic = sp.symbols("g", positive=True)
    gamma = sp.symbols("gamma", positive=True)
    chi = sp.symbols("chi", positive=True)
    potential = lam * x**2 / 2 + quartic * x**4 / 4
    force = sp.diff(potential, x)
    audit.check(
        "nonlinear static force",
        sp.expand(force - (lam * x + quartic * x**3)) == 0,
        force,
        lam * x + quartic * x**3,
        "same_static_data",
    )
    audit.check(
        "positive fixture has one static equilibrium",
        sp.solve(force, x) == [0],
        sp.solve(force, x),
        [0],
        "same_static_data",
    )
    audit.check(
        "gradient and inertial completions use the identical static force",
        sp.simplify((-gamma * force) / (-gamma) - (-force / chi) / (-1 / chi)) == 0,
        ("x_dot=-gamma*dF/dx", "x_ddot=-(dF/dx)/chi"),
        "same dF/dx",
        "same_static_data",
    )

    # Exact energy identities.  The gradient completion uses F as a Lyapunov
    # functional; the inertial completion conserves a newly declared kinetic
    # energy plus F.  The kinetic coefficient is not contained in F.
    f, velocity, acceleration = sp.symbols("f velocity acceleration", real=True)
    gradient_energy_rate = sp.expand(f * (-gamma * f))
    reversed_gradient_energy_rate = sp.expand(f * (gamma * f))
    inertial_energy_rate = sp.expand(velocity * (chi * acceleration + f))
    audit.check(
        "gradient-flow Lyapunov identity",
        gradient_energy_rate == -gamma * f**2,
        gradient_energy_rate,
        -gamma * f**2,
        "dynamics",
    )
    audit.check(
        "reversed finite-mode gradient law has the opposite energy arrow",
        reversed_gradient_energy_rate == gamma * f**2,
        reversed_gradient_energy_rate,
        gamma * f**2,
        "dynamics",
    )
    audit.check(
        "inertial extended-energy identity on shell",
        sp.simplify(inertial_energy_rate.subs(acceleration, -f / chi)) == 0,
        sp.simplify(inertial_energy_rate.subs(acceleration, -f / chi)),
        0,
        "dynamics",
    )

    # For one positive Hessian eigenvalue, the temporal spectra and the number
    # of initial data are inequivalent.  A real time rescaling cannot rotate a
    # negative real exponent into a nonzero imaginary pair.
    eigenvalue = sp.symbols("ell", positive=True)
    spectral = sp.symbols("s")
    gradient_root = sp.solve(spectral + gamma * eigenvalue, spectral)
    inertial_roots = sp.solve(chi * spectral**2 + eigenvalue, spectral)
    audit.check(
        "gradient characteristic root",
        gradient_root == [-eigenvalue * gamma],
        gradient_root,
        [-eigenvalue * gamma],
        "dynamics",
    )
    audit.check(
        "inertial characteristic roots",
        set(inertial_roots)
        == {-sp.I * sp.sqrt(eigenvalue) / sp.sqrt(chi), sp.I * sp.sqrt(eigenvalue) / sp.sqrt(chi)},
        inertial_roots,
        [-sp.I * sp.sqrt(eigenvalue / chi), sp.I * sp.sqrt(eigenvalue / chi)],
        "dynamics",
    )
    audit.check(
        "temporal orders require different initial-data counts",
        (sp.degree(spectral + gamma * eigenvalue, spectral), sp.degree(chi * spectral**2 + eigenvalue, spectral))
        == (1, 2),
        (sp.degree(spectral + gamma * eigenvalue, spectral), sp.degree(chi * spectral**2 + eigenvalue, spectral)),
        (1, 2),
        "dynamics",
    )

    # Same massless spatial functional, different causal classes.  The heat
    # kernel is nonzero at every real x for t>0, while d'Alembert waves solve a
    # finite-speed equation.  Positivity and support are analytic statements
    # proved in the note; the identities are checked symbolically here.
    space = sp.symbols("space", real=True)
    time = sp.symbols("time", positive=True)
    diffusivity = sp.symbols("D", positive=True)
    heat_kernel = sp.exp(-space**2 / (4 * diffusivity * time)) / sp.sqrt(
        4 * sp.pi * diffusivity * time
    )
    heat_residual = sp.simplify(
        sp.diff(heat_kernel, time) - diffusivity * sp.diff(heat_kernel, space, 2)
    )
    audit.check(
        "heat kernel solves the parabolic completion",
        heat_residual == 0,
        heat_residual,
        0,
        "causal_class",
    )
    audit.check(
        "heat kernel is strictly positive for positive time and diffusivity",
        heat_kernel.is_positive is True,
        heat_kernel.is_positive,
        True,
        "causal_class",
    )
    wave_speed = sp.symbols("v", positive=True)
    profile_left = sp.Function("profile_left")
    profile_right = sp.Function("profile_right")
    wave = profile_left(space - wave_speed * time) + profile_right(
        space + wave_speed * time
    )
    wave_residual = sp.simplify(
        sp.diff(wave, time, 2) - wave_speed**2 * sp.diff(wave, space, 2)
    )
    audit.check(
        "dAlembert family solves the hyperbolic completion",
        wave_residual == 0,
        wave_residual,
        0,
        "causal_class",
    )

    # A two-copy static functional exposes dimensionless relative-speed
    # freedom, which cannot be removed by one common change of time units.
    stiffness, chi_one, chi_two = sp.symbols("a chi_1 chi_2", positive=True)
    speed_one_sq = stiffness / chi_one
    speed_two_sq = stiffness / chi_two
    relative_speed_sq = sp.simplify(speed_one_sq / speed_two_sq)
    audit.check(
        "two-copy relative speed remains a free kinetic ratio",
        relative_speed_sq == chi_two / chi_one,
        relative_speed_sq,
        chi_two / chi_one,
        "relative_speed",
    )
    audit.check(
        "relative-speed rational fixture",
        relative_speed_sq.subs({chi_one: 1, chi_two: 4}) == 4,
        relative_speed_sq.subs({chi_one: 1, chi_two: 4}),
        4,
        "relative_speed",
    )

    # Exact PA-M2 soft-node corollary.  Along a coordinate ray from Q=(q,q,q)
    # at r=0, the same static symbol admits z=2 gradient relaxation and z=1
    # inertial oscillation after different temporal laws are supplied.
    epsilon = sp.symbols("epsilon", positive=True)
    c, q = sp.symbols("c q", positive=True)
    node_kernel = sp.expand(c * ((q + epsilon) ** 2 - q**2) ** 2)
    node_expected = sp.expand(c * epsilon**2 * (2 * q + epsilon) ** 2)
    audit.check(
        "PA-M2 exact coordinate-ray node expansion",
        sp.expand(node_kernel - node_expected) == 0,
        node_kernel,
        node_expected,
        "pa_m2_corollary",
    )
    opposite_node_kernel = sp.expand(c * ((q - epsilon) ** 2 - q**2) ** 2)
    symmetric_node_kernel = sp.factor((node_kernel + opposite_node_kernel) / 2)
    audit.check(
        "PA-M2 symmetric node-ray expansion cancels the cubic term",
        symmetric_node_kernel == c * epsilon**2 * (4 * q**2 + epsilon**2),
        symmetric_node_kernel,
        c * epsilon**2 * (4 * q**2 + epsilon**2),
        "pa_m2_corollary",
    )
    gradient_rate = sp.expand(gamma * node_kernel)
    inertial_frequency = sp.sqrt(c / chi) * epsilon * (2 * q + epsilon)
    gradient_leading = sp.limit(gradient_rate / epsilon**2, epsilon, 0, dir="+")
    inertial_leading = sp.limit(inertial_frequency / epsilon, epsilon, 0, dir="+")
    audit.check(
        "PA-M2 gradient completion has nonzero epsilon-squared rate",
        gradient_leading == 4 * c * gamma * q**2,
        gradient_leading,
        4 * c * gamma * q**2,
        "pa_m2_corollary",
    )
    audit.check(
        "PA-M2 inertial completion has nonzero epsilon-linear frequency",
        inertial_leading == 2 * q * sp.sqrt(c / chi),
        inertial_leading,
        2 * q * sp.sqrt(c / chi),
        "pa_m2_corollary",
    )
    target_speed = sp.symbols("c_target", positive=True)
    selected_inertia = sp.factor(4 * c * q**2 / target_speed**2)
    audit.check(
        "any positive node slope can be inserted through the inertia",
        sp.simplify(2 * q * sp.sqrt(c / selected_inertia) - target_speed) == 0,
        sp.simplify(2 * q * sp.sqrt(c / selected_inertia)),
        target_speed,
        "pa_m2_corollary",
    )
    q_zero_kernel = sp.expand(node_expected.subs(q, 0))
    audit.check(
        "q-zero boundary changes the spatial leading power to four",
        q_zero_kernel == c * epsilon**4,
        q_zero_kernel,
        c * epsilon**4,
        "pa_m2_corollary",
    )

    # The full fourth-order PA-M2 spatial operator has omega~k^2 at high
    # momentum, so its node speed is not a global limiting speed.
    momentum = sp.symbols("momentum", positive=True)
    ultraviolet_frequency = sp.sqrt(c / chi) * ((q + momentum) ** 2 - q**2)
    ultraviolet_group_speed = sp.diff(ultraviolet_frequency, momentum)
    audit.check(
        "PA-M2 ultraviolet group speed is unbounded",
        sp.limit(ultraviolet_group_speed, momentum, sp.oo) == sp.oo,
        sp.limit(ultraviolet_group_speed, momentum, sp.oo),
        sp.oo,
        "pa_m2_corollary",
    )

    source = Path(__file__).resolve()
    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "candidate_id": CANDIDATE_ID,
        "candidate_family": "C0-STATIC-TO-DYNAMICS-UNDERDETERMINATION",
        "version": __version__,
        "issued": "2026-08-03",
        "authority": "T0 scoped no-go certificate; not a TECT claim, tier change, derivation of time, or physical causal model",
        "claim_context": CLAIM_CONTEXT,
        "claim_bearing": False,
        "task_id": "T-054",
        "theorem": {
            "static_input": "a differentiable static functional F on a configuration space, with its stationary set and Hessian",
            "completion_one": "gradient flow dphi/dt=-gamma*delta F/delta phi, gamma>0",
            "completion_two": "inertial flow chi*d2phi/dt2+delta F/delta phi=0, chi>0",
            "shared_data": "the same static F, stationary configurations, and static Hessian",
            "inequivalence": "at each positive Hessian eigenvalue ell, the temporal spectra are {-gamma*ell} and {+/-i*sqrt(ell/chi)}, and the evolutions require one versus two initial data",
            "conclusion": "F alone does not decide between an irreversible semigroup and a reversible group, supply a physical arrow, or select the kinetic coefficient, Gaussian dynamical exponent, or spacetime principal-symbol class; those require additional structure",
        },
        "exact_results": {
            "same_static_equilibria_and_hessian": True,
            "gradient_energy_rate": "dF/dt=-gamma*||delta F||^2",
            "reversed_gradient_energy_rate_in_finite_dimension": "dF/dt=+gamma*||delta F||^2",
            "inertial_energy_rate": "d[chi*||phi_t||^2/2+F]/dt=0 on shell",
            "positive_mode_gradient_root": "s=-gamma*ell",
            "positive_mode_inertial_roots": "s=+/-i*sqrt(ell/chi)",
            "temporal_initial_data_counts": {"gradient": 1, "inertial": 2},
            "causal_class_witness": "the same massless gradient static functional admits heat evolution with everywhere-positive kernel and wave evolution with finite dAlembert domain of dependence",
            "two_copy_relative_speed_squared": relative_speed_sq,
            "pa_m2_node_ray_kernel": node_expected,
            "pa_m2_gradient_dynamic_exponent": 2,
            "pa_m2_inertial_dynamic_exponent": 1,
            "pa_m2_inertial_low_energy_speed": 2 * q * sp.sqrt(c / chi),
            "inertia_for_any_declared_positive_node_speed": selected_inertia,
            "q_zero_gaussian_exponents": {"gradient": 4, "inertial": 2},
            "pa_m2_global_limiting_speed": False,
            "pa_m2_ultraviolet_group_speed": ultraviolet_group_speed,
        },
        "required_extra_structure": [
            "a time parameter or relational clock",
            "a kinetic metric, symplectic form, update rule, or quantum Hamiltonian",
            "a rule selecting reversible versus dissipative evolution and a physical arrow, if one is claimed",
            "for a physical limiting speed, a controlled continuum causal structure and cross-sector dimensionless speed comparison",
        ],
        "scope": {
            "exact_scoped_underdetermination": True,
            "static_data_map_noninjective": True,
            "finite_galerkin_nonlinear_witness": True,
            "continuum_heat_wave_causal_class_witness": True,
            "static_functional_selects_kinetic_law": False,
            "pa_m2_static_functional_selects_unique_dynamics": False,
            "pa_m2_gradient_z2_corollary": True,
            "pa_m2_inertial_z1_corollary": True,
            "z_is_gaussian_tree_level_at_r_zero": True,
            "finite_torus_z_requires_commensurate_volume_limit_or_formal_local_momentum": True,
            "z_is_linearized_and_gapless_only": True,
            "finite_torus_z_requires_limit": True,
            "inertial_speed_is_inserted": True,
            "pa_m2_low_energy_node_speed_only": True,
            "pa_m2_cone_is_ir_only": True,
            "pa_m2_global_causal_cone": False,
            "time_orientation_derived": False,
            "time_emergence_derived": False,
            "causal_or_null_structure_derived": False,
            "global_causal_structure_derived": False,
            "physical_light_speed_derived": False,
            "physical_speed_derived": False,
            "physical_time_and_causal_emergence": False,
            "dynamical_exponent_uniquely_derived": False,
            "c0_a_or_c0_b_selected": False,
            "c0_branch_selected": False,
            "pa_m2_invalidated": False,
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
            "This certificate proves only that the declared static data underdetermine their temporal completion, "
            "with exact finite-mode, heat-versus-wave, and PA-M2 soft-node witnesses. It does not prove that time "
            "or causal order cannot emerge from a richer microscopic theory. It does not select C0-A or C0-B, "
            "derive a physical clock or light speed, establish a global PA-M2 causal cone, reconstruct gravity, "
            "identify an event horizon, connect PA-H1 to PA-M2, or complete Pre-A."
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
        f"{CANDIDATE_ID} | static dynamics underdetermined"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

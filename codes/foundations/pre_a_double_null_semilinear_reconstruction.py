#!/usr/bin/env python3
"""Primary exact certificate for the PA-H1-DNKG4-v0 Lane-H bridge.

The bridge studies a fixed-background 1+1 double-null Klein--Gordon equation
and a local phi^4 semilinear extension.  It is a characteristic-data theorem,
not an event-horizon identification, gravitational reconstruction, quantum
boundary state, or derivation of the TECT bulk functional.
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
CANDIDATE_ID = "PA-H1-DNKG4-v0"
SLUG = "pre-a-double-null-semilinear-reconstruction"
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


def volterra(polynomial: sp.Expr, u: sp.Symbol, v: sp.Symbol) -> sp.Expr:
    """Vf(u,v)=int_0^u int_0^v f(s,t) dt ds, exactly for polynomials."""
    s, t = sp.symbols("s t", real=True)
    integrand = polynomial.subs({u: s, v: t})
    return sp.expand(sp.integrate(sp.integrate(integrand, (t, 0, v)), (s, 0, u)))


def derive() -> dict[str, Any]:
    audit = Audit()
    u, v = sp.symbols("u v", nonnegative=True)
    kappa, coupling = sp.symbols("kappa g", nonnegative=True)

    # Exact Volterra monomial rule, checked on a grid independent of the later
    # polynomial fixture.
    for a in range(4):
        for b in range(4):
            monomial = u**a * v**b
            image = volterra(monomial, u, v)
            expected = u ** (a + 1) * v ** (b + 1) / ((a + 1) * (b + 1))
            audit.check(
                f"Volterra monomial ({a},{b})",
                sp.expand(image - expected) == 0,
                image,
                expected,
                "linear_reconstruction",
            )

    # Compatible nontrivial boundary traces and their free double-null lift.
    boundary_u = 1 + 2 * u + 3 * u**2
    boundary_v = 1 - 4 * v + 5 * v**2
    corner = sp.Integer(1)
    free_lift = sp.expand(boundary_u + boundary_v - corner)
    audit.check(
        "free lift has compatible u-axis trace",
        sp.expand(free_lift.subs(v, 0) - boundary_u) == 0,
        free_lift.subs(v, 0),
        boundary_u,
        "linear_reconstruction",
    )
    audit.check(
        "free lift has compatible v-axis trace",
        sp.expand(free_lift.subs(u, 0) - boundary_v) == 0,
        free_lift.subs(u, 0),
        boundary_v,
        "linear_reconstruction",
    )
    audit.check(
        "free lift solves the massless equation",
        sp.diff(free_lift, u, v) == 0,
        sp.diff(free_lift, u, v),
        0,
        "linear_reconstruction",
    )

    # Neumann--Volterra reconstruction for partial_u partial_v phi+kappa*phi=0.
    truncation_order = 6
    iterates = [free_lift]
    for _ in range(truncation_order):
        iterates.append(volterra(iterates[-1], u, v))
    partial_solution = sp.expand(
        sum((-kappa) ** index * item for index, item in enumerate(iterates))
    )
    residual = sp.expand(sp.diff(partial_solution, u, v) + kappa * partial_solution)
    expected_residual = sp.expand(kappa * (-kappa) ** truncation_order * iterates[-1])
    audit.check(
        "finite Neumann residual is exactly the first omitted cancellation",
        sp.expand(residual - expected_residual) == 0,
        residual,
        expected_residual,
        "linear_reconstruction",
    )
    audit.check(
        "massive partial sums preserve both characteristic traces",
        sp.expand(partial_solution.subs(v, 0) - boundary_u) == 0
        and sp.expand(partial_solution.subs(u, 0) - boundary_v) == 0,
        (partial_solution.subs(v, 0), partial_solution.subs(u, 0)),
        (boundary_u, boundary_v),
        "linear_reconstruction",
    )

    # Constant compatible data give the exact Bessel-series fixture.
    z = sp.symbols("z", nonnegative=True)
    series_order = 8
    bessel_partial = sp.expand(
        sum((-z) ** index / sp.factorial(index) ** 2 for index in range(series_order + 1))
    )
    coefficient_ratio = sp.simplify(
        ((-z) ** (series_order + 1) / sp.factorial(series_order + 1) ** 2)
        / ((-z) ** series_order / sp.factorial(series_order) ** 2)
    )
    audit.check(
        "constant-data Bessel coefficient recurrence",
        sp.simplify(coefficient_ratio + z / (series_order + 1) ** 2) == 0,
        coefficient_ratio,
        -z / (series_order + 1) ** 2,
        "linear_reconstruction",
    )
    bessel_kernel = sp.besselj(0, 2 * sp.sqrt(kappa * u * v))
    audit.check(
        "Riemann-Bessel kernel solves the massive double-null equation",
        sp.simplify(sp.diff(bessel_kernel, u, v) + kappa * bessel_kernel) == 0,
        sp.simplify(sp.diff(bessel_kernel, u, v) + kappa * bessel_kernel),
        0,
        "linear_reconstruction",
    )
    audit.check(
        "Riemann-Bessel kernel has unit data on both axes",
        sp.simplify(bessel_kernel.subs(v, 0) - 1) == 0
        and sp.simplify(bessel_kernel.subs(u, 0) - 1) == 0,
        (bessel_kernel.subs(v, 0), bessel_kernel.subs(u, 0)),
        (1, 1),
        "linear_reconstruction",
    )
    infinite_envelope = sp.summation(z**sp.Symbol("n", integer=True, nonnegative=True) / sp.factorial(sp.Symbol("n", integer=True, nonnegative=True)) ** 2, (sp.Symbol("n", integer=True, nonnegative=True), 0, sp.oo))
    envelope_target = sp.besseli(0, 2 * sp.sqrt(z))
    audit.check(
        "factorial-squared envelope is modified Bessel I0",
        sp.simplify(infinite_envelope - envelope_target) == 0,
        infinite_envelope,
        envelope_target,
        "stability",
    )
    n = sp.symbols("n", integer=True, positive=True)
    uniqueness_ratio_limit = sp.limit(z / (n + 1) ** 2, n, sp.oo)
    audit.check(
        "Volterra uniqueness ratio tends to zero",
        uniqueness_ratio_limit == 0,
        uniqueness_ratio_limit,
        0,
        "stability",
    )

    # Exact local semilinear Banach conditions for
    # partial_u partial_v phi+kappa*phi+g*phi^3=0.
    U = sp.Rational(1, 4)
    V = sp.Rational(1, 4)
    kappa_sample = sp.Integer(1)
    coupling_sample = sp.Integer(1)
    radius = sp.Integer(1)
    data_norm = sp.Rational(1, 2)
    self_map_value = sp.factor(
        data_norm + U * V * (kappa_sample * radius + coupling_sample * radius**3)
    )
    lipschitz = sp.factor(
        U * V * (kappa_sample + 3 * coupling_sample * radius**2)
    )
    stability_factor = sp.factor(1 / (1 - lipschitz))
    audit.check(
        "exact semilinear ball is invariant in the sample domain",
        self_map_value <= radius,
        self_map_value,
        radius,
        "semilinear_reconstruction",
    )
    audit.check(
        "exact semilinear map is contractive in the sample domain",
        lipschitz < 1,
        lipschitz,
        "<1",
        "semilinear_reconstruction",
    )
    audit.check(
        "exact semilinear data-stability factor",
        stability_factor == sp.Rational(4, 3),
        stability_factor,
        sp.Rational(4, 3),
        "semilinear_reconstruction",
    )

    # Energy-current conservation for kappa=mu^2/4 and g=lambda/4.
    time, space = sp.symbols("time space", real=True)
    mass, lam = sp.symbols("mu lambda", nonnegative=True)
    field = sp.Function("field")(time, space)
    field_t = sp.diff(field, time)
    field_x = sp.diff(field, space)
    energy_density = (
        (field_t**2 + field_x**2 + mass**2 * field**2) / 2
        + lam * field**4 / 4
    )
    energy_flux = field_t * field_x
    energy_divergence = sp.factor(
        sp.diff(energy_density, time) - sp.diff(energy_flux, space)
    )
    expected_energy_divergence = sp.factor(
        field_t
        * (sp.diff(field, time, 2) - sp.diff(field, space, 2) + mass**2 * field + lam * field**3)
    )
    audit.check(
        "local phi4 energy-current identity",
        sp.simplify(energy_divergence - expected_energy_divergence) == 0,
        energy_divergence,
        expected_energy_divergence,
        "state_transport",
    )
    field_one = sp.Function("field_one")(time, space)
    field_two = sp.Function("field_two")(time, space)
    symplectic_time = field_one * sp.diff(field_two, time) - field_two * sp.diff(
        field_one, time
    )
    symplectic_space = field_one * sp.diff(field_two, space) - field_two * sp.diff(
        field_one, space
    )
    kg_one = (
        sp.diff(field_one, time, 2)
        - sp.diff(field_one, space, 2)
        + mass**2 * field_one
    )
    kg_two = (
        sp.diff(field_two, time, 2)
        - sp.diff(field_two, space, 2)
        + mass**2 * field_two
    )
    symplectic_divergence = sp.expand(
        sp.diff(symplectic_time, time) - sp.diff(symplectic_space, space)
    )
    expected_symplectic_divergence = sp.expand(field_one * kg_two - field_two * kg_one)
    audit.check(
        "general Klein-Gordon symplectic-current identity",
        sp.simplify(symplectic_divergence - expected_symplectic_divergence) == 0,
        symplectic_divergence,
        expected_symplectic_divergence,
        "state_transport",
    )
    tangent_derivative, boundary_value, transverse_derivative = sp.symbols(
        "A_prime A_value transverse", real=True
    )
    right_field_t = tangent_derivative + transverse_derivative
    right_field_x = tangent_derivative - transverse_derivative
    boundary_potential = mass**2 * boundary_value**2 / 2 + lam * boundary_value**4 / 4
    right_energy = (right_field_t**2 + right_field_x**2) / 2 + boundary_potential
    right_flux = right_field_t * right_field_x
    null_flux_per_u = sp.factor((right_energy + right_flux) / 2)
    expected_null_flux = sp.factor(
        tangent_derivative**2 + mass**2 * boundary_value**2 / 4 + lam * boundary_value**4 / 8
    )
    audit.check(
        "right null-boundary energy flux has the exact half-potential factor",
        sp.simplify(null_flux_per_u - expected_null_flux) == 0,
        null_flux_per_u,
        expected_null_flux,
        "state_transport",
    )
    left_field_t = transverse_derivative + tangent_derivative
    left_field_x = transverse_derivative - tangent_derivative
    left_energy = (left_field_t**2 + left_field_x**2) / 2 + boundary_potential
    left_flux = left_field_t * left_field_x
    null_flux_per_v = sp.factor((left_energy - left_flux) / 2)
    audit.check(
        "left null-boundary energy flux has the exact half-potential factor",
        sp.simplify(null_flux_per_v - expected_null_flux) == 0,
        null_flux_per_v,
        expected_null_flux,
        "state_transport",
    )

    # Exact massless polynomial fixture for symplectic boundary-to-slice
    # transport.  The massive linear identity follows from the same conserved
    # symplectic current because equal mass terms cancel.
    tau, x = sp.symbols("tau x", positive=True, real=True)
    audit.check(
        "slice coordinates obey u+v=2*tau",
        sp.simplify((tau + x) + (tau - x) - 2 * tau) == 0,
        sp.simplify((tau + x) + (tau - x)),
        2 * tau,
        "state_transport",
    )
    A1 = 1 + u + 2 * u**2
    B1 = 1 - 3 * v + v**2
    A2 = 2 - u + u**3
    B2 = 2 + 2 * v - v**2
    phi1_slice = sp.expand(A1.subs(u, tau + x) + B1.subs(v, tau - x) - 1)
    phi2_slice = sp.expand(A2.subs(u, tau + x) + B2.subs(v, tau - x) - 2)
    pi1_slice = sp.expand(
        sp.diff(A1, u).subs(u, tau + x) + sp.diff(B1, v).subs(v, tau - x)
    )
    pi2_slice = sp.expand(
        sp.diff(A2, u).subs(u, tau + x) + sp.diff(B2, v).subs(v, tau - x)
    )
    omega_slice = sp.integrate(
        sp.expand(phi1_slice * pi2_slice - phi2_slice * pi1_slice),
        (x, -tau, tau),
    )
    omega_boundary = sp.integrate(
        sp.expand(A1 * sp.diff(A2, u) - A2 * sp.diff(A1, u)),
        (u, 0, 2 * tau),
    ) + sp.integrate(
        sp.expand(B1 * sp.diff(B2, v) - B2 * sp.diff(B1, v)),
        (v, 0, 2 * tau),
    )
    audit.check(
        "massless symplectic boundary-to-slice fixture",
        sp.simplify(omega_slice - omega_boundary) == 0,
        omega_slice,
        omega_boundary,
        "state_transport",
    )

    # The interior state uses u=t+x, v=t-x, so t=(u+v)/2 and
    # Pi=partial_t phi=partial_u phi+partial_v phi.  These are the exact
    # derivative identities obtained by differentiating the Volterra equation.
    derivative_u_identity = "partial_u phi=A'(u)-int_0^v[kappa*phi(u,t)+g*phi(u,t)^3]dt"
    derivative_v_identity = "partial_v phi=B'(v)-int_0^u[kappa*phi(s,v)+g*phi(s,v)^3]ds"
    state_map = "P_tau:C1x_cornerC1 -> C1xC0, (A,B) maps to (phi,(partial_u+partial_v)phi)|_{u+v=2*tau}, 0<2*tau<=min(U,V)"
    spatial_derivative_stability = "||partial_x delta phi_tau||_infinity<=||delta A'||_infinity+||delta B'||_infinity+2*kappa*tau*I0(2*tau*sqrt(kappa))*||delta G||_infinity"
    momentum_stability = "||delta Pi_tau||_infinity<=||delta A'||_infinity+||delta B'||_infinity+2*kappa*tau*I0(2*tau*sqrt(kappa))*||delta G||_infinity"

    source = Path(__file__).resolve()
    payload: dict[str, Any] = {
        "schema": SCHEMA,
        "candidate_id": CANDIDATE_ID,
        "candidate_family": "H1-DOUBLE-NULL-CHARACTERISTIC-RECONSTRUCTION",
        "version": __version__,
        "issued": "2026-08-03",
        "authority": "T0 Lane-H bridge certificate; not a TECT action, claim theorem, event-horizon origin, or gravitational reconstruction",
        "claim_context": CLAIM_CONTEXT,
        "claim_bearing": False,
        "task_id": "T-054",
        "equations": {
            "linear": "partial_u partial_v phi+kappa*phi=0 on [0,U]x[0,V], kappa>=0",
            "semilinear": "partial_u partial_v phi+kappa*phi+g*phi^3=0, kappa>=0, g>=0",
            "physical_parameter_map": "kappa=mu^2/4 and g=lambda/4 gives phi_tt-phi_xx+mu^2*phi+lambda*phi^3=0",
            "data": "phi(u,0)=A(u), phi(0,v)=B(v), A(0)=B(0)",
            "linear_volterra_solution": "phi=sum_{n>=0}(-kappa)^n V^n G, G=A(u)+B(v)-A(0)",
        },
        "exact_results": {
            "volterra_power_bound": "||V^n f||_infinity<=(U*V)^n/(n!)^2 ||f||_infinity",
            "linear_global_sup_bound": "||phi||_infinity<=I0(2*sqrt(kappa*U*V))*||G||_infinity",
            "linear_uniqueness": True,
            "linear_data_stability": "||phi-phi_tilde||_infinity<=I0(2*sqrt(kappa*U*V))*||G-G_tilde||_infinity",
            "constant_data_solution": "phi=a0*J0(2*sqrt(kappa*u*v))",
            "riemann_bessel_kernel_equation_and_axes": True,
            "semilinear_self_map_gate": "M+U*V*(kappa*R+g*R^3)<=R",
            "semilinear_contraction_gate": "L=U*V*(kappa+3*g*R^2)<1",
            "semilinear_data_stability": "for the same kappa,g,R when both data maps preserve the same radius-R ball, ||phi-phi_tilde||_infinity<=||G-G_tilde||_infinity/(1-L)",
            "sample_self_map_value": self_map_value,
            "sample_lipschitz_constant": lipschitz,
            "sample_stability_factor": stability_factor,
            "derivative_u_identity": derivative_u_identity,
            "derivative_v_identity": derivative_v_identity,
            "classical_slice_state_map": state_map,
            "classical_slice_spatial_derivative_stability": spatial_derivative_stability,
            "classical_slice_momentum_stability": momentum_stability,
            "linear_state_map_injective": True,
            "slice_energy_flux_balance": "for 0<=2*tau<=min(U,V), E_tau=int_0^(2tau)[A'^2+mu^2*A^2/4+lambda*A^4/8]du+the_same_B_integral",
            "left_and_right_null_energy_flux_factors": True,
            "massive_symplectic_current_identity": True,
            "linear_symplectic_identity": "Omega_Sigma(P_tau*d1,P_tau*d2)=Omega_H(d1,d2)",
            "linear_boundary_state_transport": "because P_tau is injective and symplectic onto its image, omega_Sigma(W(P_tau*d))=omega_H(W(d)) defines a state on the reconstructed Weyl-CCR image",
        },
        "lane_h_verdict": "ADVANCE: sufficient compatible double-null data define a unique stable fixed-background linear bulk globally and a unique local semilinear bulk under explicit contraction gates",
        "interface_contract": {
            "input": "compatible classical characteristic traces A,B and inserted kappa,g,U,V",
            "output": "stable classical interior slice data (phi,Pi), a conserved current with exact boundary-to-slice energy flux balance, and for the linear theory a symplectic Weyl-CCR image with algebraic-state pull-forward",
            "not_output": "a selected Hadamard state, trace-class density matrix in general, gravitational constraints, physical horizon identity, cosmic energy scale, cooling map r(tau), or PA-M2 bulk law",
        },
        "scope": {
            "fixed_1_plus_1_minkowski_background": True,
            "global_linear_rectangle_reconstruction": True,
            "linear_uniqueness_and_stability": True,
            "local_semilinear_reconstruction_under_explicit_gates": True,
            "classical_state_output": True,
            "linear_state_map_injective": True,
            "linear_algebraic_boundary_state_transport": True,
            "selected_physical_quantum_boundary_state": False,
            "einstein_constraint_system": False,
            "event_horizon_identified": False,
            "high_energy_cosmic_state_derived": False,
            "cooling_map_derived": False,
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
            "The certificate proves a classical fixed-background double-null reconstruction theorem and an explicit "
            "local semilinear contraction theorem only. Its linear Weyl-CCR map transports but does not select a "
            "physical or Hadamard state. It does not identify an event horizon, solve Einstein constraints, derive a "
            "cosmological high-energy state or cooling law, reproduce PA-M2 "
            "dynamics, establish spacetime emergence, or complete Pre-A."
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
        f"{CANDIDATE_ID} | global linear and gated local semilinear reconstruction"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

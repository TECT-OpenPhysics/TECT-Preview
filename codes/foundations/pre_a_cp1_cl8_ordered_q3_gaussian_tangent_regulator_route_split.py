#!/usr/bin/env python3
"""Primary exact audit for the ordered-Q3 Gaussian tangent regulator split."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any

import sympy as sp


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
CANDIDATE_ID = "PA-CP1-CL8-ORDERED-Q3-GAUSSIAN-TANGENT-REGULATOR-ROUTE-SPLIT-v0"
RESULT_ID = "PA-CP1-CL8-SPECTRAL-GAUSSIAN-PROJECTIVE-FAMILY-HADAMARD-COMPARATOR-BARE-CRITICAL-SPEED-CENTERED-PROJECTIVITY-AND-CRITICAL-ZERO-MODE-NOGOS"
NEGATIVE_IDS = (
    "NG-2026-08-04-PRE-A-CP1-CL8-CENTERED-GAUSSIAN-LOW-MODE-EXACT-PROJECTIVITY",
    "NG-2026-08-04-PRE-A-CP1-CL8-CRITICAL-COMPACT-GAUSSIAN-NORMAL-GROUND",
)
PARENT_FILES = (
    "strategy/pre-a-cp1-st8-q3lock-manifest.json",
    "strategy/pre-a-c0a-gaussian-ccr-pah1-embedding-manifest.json",
    "strategy/pre-a-cp1-cl8-semidiscrete-cauchy-oa2-manifest.json",
    "strategy/pre-a-cp1-cl8-finite-quantum-state-boundary-fork-manifest.json",
    "strategy/pre-a-cp1-cl8-quantum-boundary-algebra-intertwiner-route-split-manifest.json",
    "strategy/pre-a-cp1-cl8-history-cut-quantum-algebra-state-compatibility-route-split-manifest.json",
)
SLUG = "pre-a-cp1-cl8-ordered-q3-gaussian-tangent-regulator-route-split"
SCHEMA = f"tect/{SLUG}-primary/0.1"
SCRIPT = Path(__file__).resolve()
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260804.md"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-04-primary-{SLUG}/result.json"


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


def sha256(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(serial(payload), stream, indent=2, sort_keys=True)
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

    def check(self, name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={serial(actual)!r}, expected={serial(expected)!r}")
        self.rows.append({"name": name, "group": group, "status": "PASS", "actual": serial(actual), "expected": serial(expected)})


def cube_laplacian() -> tuple[list[tuple[int, int, int]], sp.Matrix]:
    nodes = [(a, b, c) for a in (0, 1) for b in (0, 1) for c in (0, 1)]
    index = {node: i for i, node in enumerate(nodes)}
    laplacian = sp.zeros(8)
    for node in nodes:
        i = index[node]
        for axis in range(3):
            neighbor = list(node)
            neighbor[axis] ^= 1
            j = index[tuple(neighbor)]
            laplacian[i, i] += 1
            laplacian[i, j] -= 1
    return nodes, laplacian


def walsh(nodes: list[tuple[int, int, int]], alpha: tuple[int, int, int]) -> sp.Matrix:
    return sp.Matrix([(-1) ** sum(a * e for a, e in zip(alpha, node)) for node in nodes])


def khat_squared(k: sp.Expr, a: sp.Expr) -> sp.Expr:
    return sp.factor(4 * sp.sin(k * a / 2) ** 2 / a**2)


def build_payload() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    parents = [json.loads((REPO / path).read_text(encoding="utf-8")) for path in PARENT_FILES]
    audit = Audit()

    audit.check("candidate id", manifest["candidate_id"] == CANDIDATE_ID, manifest["candidate_id"], CANDIDATE_ID, "identity")
    audit.check("result id", manifest["result_id"] == RESULT_ID, manifest["result_id"], RESULT_ID, "identity")
    audit.check("negative ids", tuple(manifest["negative_ids"]) == NEGATIVE_IDS, manifest["negative_ids"], NEGATIVE_IDS, "identity")
    audit.check("parent ids", tuple(parent["candidate_id"] for parent in parents) == tuple(manifest["parent_ids"]), [parent["candidate_id"] for parent in parents], manifest["parent_ids"], "identity")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "identity")
    audit.check("exploration id", manifest["exploration_id"] == "EXP-000762", manifest["exploration_id"], "EXP-000762", "identity")

    nodes, laplacian = cube_laplacian()
    alphas = [(a, b, c) for a in (0, 1) for b in (0, 1) for c in (0, 1)]
    eigen_rows = []
    for alpha in alphas:
        vector = walsh(nodes, alpha)
        level = sum(alpha)
        residual = laplacian * vector - 2 * level * vector
        audit.check(f"Walsh eigenvector {alpha}", residual == sp.zeros(8, 1), residual, sp.zeros(8, 1), "Q3")
        eigen_rows.append((2 * level, level))
    spectrum = Counter(value for value, _ in eigen_rows)
    audit.check("Q3 spectrum", spectrum == Counter({0: 1, 2: 3, 4: 3, 6: 1}), dict(spectrum), {0: 1, 2: 3, 4: 3, 6: 1}, "Q3")
    audit.check("Q3 row sums", all(sum(laplacian[i, j] for j in range(8)) == 0 for i in range(8)), [sum(laplacian[i, j] for j in range(8)) for i in range(8)], [0] * 8, "Q3")

    rho, g = sp.symbols("rho g", positive=True)
    lam = sp.symbols("lambda", nonnegative=True)
    r = -rho
    v2 = rho / g
    ordered_hessian = -2 * r * sp.eye(8) + lam * v2 * laplacian

    # Differentiate the upstream onsite and edge polynomials instead of using
    # the displayed Hessian as an oracle.
    qe, qf, v = sp.symbols("q_e q_f v", real=True)
    onsite_polynomial = r * qe**2 / 2 + g * qe**4 / 4
    edge_polynomial = lam * (qe - qf) ** 2 * (qe**2 + qf**2) / 4
    onsite_hessian_at_well = sp.factor(sp.diff(onsite_polynomial, qe, 2).subs(qe, v).subs(v**2, v2))
    edge_hessian_at_well = sp.Matrix(
        [[sp.diff(edge_polynomial, left, right) for right in (qe, qf)] for left in (qe, qf)]
    ).subs({qe: v, qf: v})
    edge_hessian_at_well = edge_hessian_at_well.applyfunc(sp.factor)
    audit.check("differentiated onsite Hessian", onsite_hessian_at_well == -2 * r, onsite_hessian_at_well, -2 * r, "Hessian")
    expected_edge_hessian = lam * v**2 * sp.Matrix([[1, -1], [-1, 1]])
    audit.check("differentiated lock-edge Hessian", edge_hessian_at_well == expected_edge_hessian, edge_hessian_at_well, expected_edge_hessian, "Hessian")
    assembled_hessian = onsite_hessian_at_well * sp.eye(8)
    for i, left in enumerate(nodes):
        for j, right in enumerate(nodes):
            if i < j and sum(a0 != b0 for a0, b0 in zip(left, right)) == 1:
                assembled_hessian[i, i] += lam * v**2
                assembled_hessian[j, j] += lam * v**2
                assembled_hessian[i, j] -= lam * v**2
                assembled_hessian[j, i] -= lam * v**2
    assembled_hessian = assembled_hessian.subs(v**2, v2).applyfunc(sp.factor)
    hessian_residual = (assembled_hessian - ordered_hessian).applyfunc(sp.simplify)
    audit.check("differentiated full ordered Hessian", hessian_residual == sp.zeros(8), hessian_residual, sp.zeros(8), "Hessian")
    species = [sp.factor(-2 * r + 2 * s * lam * v2) for s in range(4)]
    expected_species = [sp.factor(-2 * r * (1 + s * lam / g)) for s in range(4)]
    audit.check("species stiffness formula", species == expected_species, species, expected_species, "Hessian")
    audit.check("lambda-zero species control", [value.subs(lam, 0) for value in species] == [-2 * r] * 4, [value.subs(lam, 0) for value in species], [-2 * r] * 4, "Hessian")
    audit.check("all ordered species strictly positive", all(value.is_positive is True for value in species), species, "all positive for rho>0,g>0,lambda>=0", "Hessian")
    for alpha in alphas:
        level = sum(alpha)
        vector = walsh(nodes, alpha)
        residual = sp.simplify(ordered_hessian * vector - species[level] * vector)
        audit.check(f"ordered Hessian Walsh branch {alpha}", residual == sp.zeros(8, 1), residual, sp.zeros(8, 1), "Hessian")
    fixture_subs = {rho: sp.Rational(1, 2), g: 1, lam: 3}
    fixture_species = [value.subs(fixture_subs) for value in species]
    audit.check("positive ordered fixture", fixture_species == [1, 4, 7, 10], fixture_species, [1, 4, 7, 10], "Hessian")

    a, chi, hbar, y, p = sp.symbols("a chi hbar y p", positive=True, real=True)
    Phi_can, P_can = sp.symbols("Phi_can P_can", real=True)
    weight = a / 8
    field_scale = sp.sqrt(a / 8)
    momentum_scale = sp.sqrt(8 / a)
    audit.check("canonical scale product", sp.simplify(field_scale * momentum_scale) == 1, sp.simplify(field_scale * momentum_scale), 1, "normalization")
    raw_mode_kinetic = sp.factor(p**2 / (2 * chi * weight))
    transformed_kinetic = sp.simplify(raw_mode_kinetic.subs(p, sp.sqrt(a / 8) * P_can))
    audit.check("mode mass is chi", transformed_kinetic == P_can**2 / (2 * chi), transformed_kinetic, P_can**2 / (2 * chi), "normalization")
    Omega2 = sp.symbols("Omega2", positive=True)
    raw_mode_potential = weight * Omega2 * y**2 / 2
    transformed_potential = sp.simplify(raw_mode_potential.subs(y, sp.sqrt(8 / a) * Phi_can))
    audit.check("mode potential normalization", transformed_potential == Omega2 * Phi_can**2 / 2, transformed_potential, Omega2 * Phi_can**2 / 2, "normalization")

    k = sp.symbols("k", real=True)
    khat2 = khat_squared(k, a)
    nu = sp.symbols("nu", positive=True)
    c = sp.symbols("c", positive=True)
    omega_a = sp.sqrt((nu + c * khat2) / chi)
    C_phi_a = sp.factor(hbar / (2 * chi * omega_a))
    C_p_a = sp.factor(hbar * chi * omega_a / 2)
    audit.check("Gaussian uncertainty product", sp.simplify(C_phi_a * C_p_a) == hbar**2 / 4, sp.simplify(C_phi_a * C_p_a), hbar**2 / 4, "Gaussian")
    audit.check("zero symmetrized cross covariance declared", "zero symmetrized cross covariance" in manifest["spectral_projective_state_family"]["state"], manifest["spectral_projective_state_family"]["state"], "contains zero cross covariance", "Gaussian")

    # Exact spectral-cutoff state restriction.  Each old mode retains the same
    # continuum-symbol covariance because it is independent of the cutoff K.
    spectral_parameters = {nu: 1, c: 1, chi: 1, hbar: 2}
    def spectral_covariances(cutoff: int) -> dict[tuple[int, int, str], sp.Expr]:
        values: dict[tuple[int, int, str], sp.Expr] = {}
        for mode in range(cutoff + 1):
            multiplicity = 1 if mode == 0 else 2
            frequency = sp.sqrt((nu + c * mode**2) / chi).subs(spectral_parameters)
            for quadrature in range(multiplicity):
                values[(mode, quadrature, "q")] = sp.factor(hbar / (2 * chi * frequency)).subs(spectral_parameters)
                values[(mode, quadrature, "p")] = sp.factor(hbar * chi * frequency / 2).subs(spectral_parameters)
        return values
    spectral_1 = spectral_covariances(1)
    spectral_3 = spectral_covariances(3)
    audit.check("spectral projective restriction", all(spectral_3[key] == value for key, value in spectral_1.items()), {str(key): spectral_3[key] for key in spectral_1}, spectral_1, "projective")
    audit.check("spectral inclusion adds modes", set(spectral_1) < set(spectral_3), len(spectral_3), "strictly more modes", "projective")

    # Exact centered coarse/fine witness away from the Nyquist mode.
    L = sp.Integer(6)
    M_coarse = sp.Integer(6)
    n_mode = sp.Integer(2)
    a_coarse = L / M_coarse
    a_fine = a_coarse / 2
    k_mode = 2 * sp.pi * n_mode / L
    coarse_symbol = sp.simplify(khat_squared(k_mode, a_coarse))
    fine_symbol = sp.simplify(khat_squared(k_mode, a_fine))
    audit.check("coarse symbol fixture", coarse_symbol == 3, coarse_symbol, 3, "centered-no-go")
    audit.check("fine symbol fixture", fine_symbol == 4, fine_symbol, 4, "centered-no-go")
    audit.check("fixture is non-Nyquist", 0 < n_mode < M_coarse / 2, n_mode, "0<n<M/2", "centered-no-go")
    x = sp.symbols("x", real=True)
    refinement_identity = sp.trigsimp(
        sp.expand_trig(16 * sp.sin(x / 2) ** 2 - 4 * sp.sin(x) ** 2 - 16 * sp.sin(x / 2) ** 4),
        method="fu",
    )
    audit.check("refinement identity", refinement_identity == 0, refinement_identity, 0, "centered-no-go")
    audit.check("strict centered frequency mismatch", fine_symbol > coarse_symbol, [coarse_symbol, fine_symbol], "fine>coarse", "centered-no-go")
    fixture_frequency_coarse = sp.sqrt(1 + coarse_symbol)
    fixture_frequency_fine = sp.sqrt(1 + fine_symbol)
    audit.check("field covariance strictly decreases", 1 / fixture_frequency_fine < 1 / fixture_frequency_coarse, [1 / fixture_frequency_coarse, 1 / fixture_frequency_fine], "fine<coarse", "centered-no-go")
    audit.check("momentum covariance strictly increases", fixture_frequency_fine > fixture_frequency_coarse, [fixture_frequency_coarse, fixture_frequency_fine], "fine>coarse", "centered-no-go")

    # Series and analytic bound bookkeeping for fixed modes.
    symbol_series = sp.series(khat2, a, 0, 7).removeO().expand()
    expected_series = k**2 - a**2 * k**4 / 12 + a**4 * k**6 / 360 - a**6 * k**8 / 20160
    audit.check("centered symbol series", sp.expand(symbol_series - expected_series) == 0, symbol_series, expected_series, "convergence")
    # Exact analytic certificate for 0 <= k^2-khat^2 <= a^2*k^4/12
    # on |k*a|<=pi.  By evenness put X=|k*a|/2 in [0,pi/2].
    # x-sin(x) has derivative 1-cos(x)>=0.  The lower Taylor residual
    # sin(x)-x+x^3/6 has third derivative 1-cos(x)>=0 and vanishing value,
    # first derivative, and second derivative at zero.  Thus
    # x-x^3/6 <= sin(x) <= x.  Squaring the nonnegative lower bound gives
    # the claimed symbol estimate.
    X = sp.symbols("X", nonnegative=True)
    upper_sine_residual = X - sp.sin(X)
    lower_sine_residual = sp.sin(X) - X + X**3 / 6
    audit.check("upper sine lemma derivative", sp.diff(upper_sine_residual, X) == 1 - sp.cos(X), sp.diff(upper_sine_residual, X), 1 - sp.cos(X), "convergence")
    audit.check("upper sine lemma base", upper_sine_residual.subs(X, 0) == 0, upper_sine_residual.subs(X, 0), 0, "convergence")
    audit.check("lower sine lemma third derivative", sp.diff(lower_sine_residual, X, 3) == 1 - sp.cos(X), sp.diff(lower_sine_residual, X, 3), 1 - sp.cos(X), "convergence")
    audit.check("lower sine lemma zero jet", [sp.diff(lower_sine_residual, X, order).subs(X, 0) for order in range(3)] == [0, 0, 0], [sp.diff(lower_sine_residual, X, order).subs(X, 0) for order in range(3)], [0, 0, 0], "convergence")
    polynomial_gap = sp.factor(X**2 / 3 - (1 - (1 - X**2 / 6) ** 2))
    audit.check("squared lower sine bound slack", polynomial_gap == X**4 / 36, polynomial_gap, X**4 / 36, "convergence")
    translated_symbol_bound = sp.simplify(k**2 * (k * a / 2) ** 2 / 3)
    audit.check("global centered symbol bound coefficient", translated_symbol_bound == a**2 * k**4 / 12, translated_symbol_bound, a**2 * k**4 / 12, "convergence")
    mu = sp.symbols("m", positive=True)
    Omega0 = sp.symbols("Omega0", positive=True)
    OmegaLat = sp.symbols("OmegaLat", positive=True)
    delta = Omega0**2 - OmegaLat**2
    rationalized = sp.simplify((1 / OmegaLat - 1 / Omega0) - delta / ((Omega0 + OmegaLat) * Omega0 * OmegaLat))
    audit.check("inverse-square-root rationalization", rationalized == 0, rationalized, 0, "convergence")
    audit.check("frequency rationalization", sp.simplify((Omega0 - OmegaLat) - delta / (Omega0 + OmegaLat)) == 0, sp.simplify((Omega0 - OmegaLat) - delta / (Omega0 + OmegaLat)), 0, "convergence")
    u0, u_lat = sp.symbols("u0 u_lat", nonnegative=True)
    frequency_denominator_excess = sp.expand((2 * mu + u0 + u_lat) - 2 * mu)
    inverse_denominator_excess = sp.expand(
        (2 * mu + u0 + u_lat) * (mu + u0) * (mu + u_lat) - 2 * mu**3
    )
    inverse_coefficients = sp.Poly(inverse_denominator_excess, u0, u_lat, mu).coeffs()
    audit.check("frequency denominator lower bound", frequency_denominator_excess == u0 + u_lat, frequency_denominator_excess, u0 + u_lat, "convergence")
    audit.check("inverse denominator lower bound", all(coefficient >= 0 for coefficient in inverse_coefficients), inverse_denominator_excess, "polynomial with nonnegative coefficients", "convergence")
    delta_frequency_square_bound = c * a**2 * k**4 / (12 * chi)
    frequency_bound = sp.factor(delta_frequency_square_bound / (2 * mu))
    field_covariance_bound = sp.factor(hbar * delta_frequency_square_bound / (4 * chi * mu**3))
    momentum_covariance_bound = sp.factor(hbar * chi * delta_frequency_square_bound / (4 * mu))
    audit.check("derived frequency bound", frequency_bound == c * a**2 * k**4 / (24 * chi * mu), frequency_bound, c * a**2 * k**4 / (24 * chi * mu), "convergence")
    audit.check("derived field covariance bound", field_covariance_bound == hbar * c * a**2 * k**4 / (48 * chi**2 * mu**3), field_covariance_bound, hbar * c * a**2 * k**4 / (48 * chi**2 * mu**3), "convergence")
    audit.check("derived momentum covariance bound", momentum_covariance_bound == hbar * c * a**2 * k**4 / (48 * mu), momentum_covariance_bound, hbar * c * a**2 * k**4 / (48 * mu), "convergence")

    # Reproducible numerical hostile check: both equal-time covariance and a
    # nonzero-time Wightman coefficient converge with the predicted a^2 rate.
    errors_q: list[float] = []
    errors_t: list[float] = []
    for M in (24, 48, 96, 192):
        spacing = 2 * math.pi / M
        physical_k = 3.0
        lattice_k = 2.0 * math.sin(physical_k * spacing / 2.0) / spacing
        continuum_frequency = math.sqrt(2.0 + physical_k**2)
        lattice_frequency = math.sqrt(2.0 + lattice_k**2)
        cq0 = 1.0 / (2.0 * continuum_frequency)
        cqa = 1.0 / (2.0 * lattice_frequency)
        errors_q.append(abs(cqa - cq0))
        w0 = cq0 * complex(math.cos(0.7 * continuum_frequency), -math.sin(0.7 * continuum_frequency))
        wa = cqa * complex(math.cos(0.7 * lattice_frequency), -math.sin(0.7 * lattice_frequency))
        errors_t.append(abs(wa - w0))
    ratios_q = [errors_q[i + 1] / errors_q[i] for i in range(len(errors_q) - 1)]
    ratios_t = [errors_t[i + 1] / errors_t[i] for i in range(len(errors_t) - 1)]
    audit.check("fixed-mode covariance converges", all(errors_q[i + 1] < errors_q[i] for i in range(3)), errors_q, "strict decrease", "convergence")
    audit.check("fixed-mode covariance a2 ratios", all(0.20 < ratio < 0.27 for ratio in ratios_q), ratios_q, "near one quarter", "convergence")
    audit.check("finite-time two-point converges", all(errors_t[i + 1] < errors_t[i] for i in range(3)), errors_t, "strict decrease", "convergence")
    audit.check("finite-time two-point a2 ratios", all(0.20 < ratio < 0.27 for ratio in ratios_t), ratios_t, "near one quarter", "convergence")

    # Critical scaling, speed, and the compact zero-mode obstruction.
    s = sp.symbols("s", integer=True, nonnegative=True)
    nu_critical = 2 * rho * (1 + s * lam / g)
    xi = sp.sqrt(c / nu_critical)
    gap = sp.sqrt(nu_critical / chi)
    correlation_power = sp.limit(sp.log(xi) / sp.log(rho), rho, 0, dir="+")
    gap_power = sp.limit(sp.log(gap) / sp.log(rho), rho, 0, dir="+")
    z_value = sp.simplify(-gap_power / correlation_power)
    audit.check("bare correlation exponent", correlation_power == -sp.Rational(1, 2), correlation_power, -sp.Rational(1, 2), "critical")
    audit.check("bare gap exponent", gap_power == sp.Rational(1, 2), gap_power, sp.Rational(1, 2), "critical")
    audit.check("bare dynamical exponent", z_value == 1, z_value, 1, "critical")
    gap_xi_squared = sp.factor((gap * xi) ** 2)
    audit.check("gap times correlation length squared", sp.simplify(gap_xi_squared - c / chi) == 0, gap_xi_squared, c / chi, "critical")
    positive_k = sp.symbols("k_pos", positive=True)
    critical_frequency = sp.sqrt(c / chi) * 2 * sp.sin(positive_k * a / 2) / a
    group_velocity = sp.simplify(sp.diff(critical_frequency, positive_k))
    audit.check("finite lattice group velocity", group_velocity == sp.sqrt(c / chi) * sp.cos(positive_k * a / 2), group_velocity, sp.sqrt(c / chi) * sp.cos(positive_k * a / 2), "critical")
    common_speed = sp.limit(group_velocity, a, 0, dir="+")
    audit.check("continuum common speed", common_speed == sp.sqrt(c / chi), common_speed, sp.sqrt(c / chi), "critical")
    critical_branch_factor = sp.symbols("A_critical", positive=True)
    zero_covariance = hbar / (2 * sp.sqrt(chi * 2 * rho * critical_branch_factor))
    audit.check("critical zero covariance diverges", sp.limit(zero_covariance, rho, 0, dir="+") == sp.oo, sp.limit(zero_covariance, rho, 0, dir="+"), sp.oo, "zero-mode")
    test_u = sp.symbols("u", positive=True)
    zero_characteristic = sp.exp(-test_u**2 * zero_covariance / (2 * hbar**2))
    audit.check("nonzero zero-mode characteristic collapses", sp.limit(zero_characteristic, rho, 0, dir="+") == 0, sp.limit(zero_characteristic, rho, 0, dir="+"), 0, "zero-mode")
    q = sp.symbols("q", real=True)
    A0, B0 = sp.symbols("A0 B0")
    free_zero_solution = A0 + B0 * q
    audit.check("free zero-energy solution", sp.diff(free_zero_solution, q, 2) == 0, sp.diff(free_zero_solution, q, 2), 0, "zero-mode")
    no_normal_ground = (
        sp.diff(free_zero_solution, q, 2) == 0
        and "no normalizable ground vector" in manifest["critical_zero_mode_no_go"]["conclusion"]
    )
    audit.check("no nonzero affine L2 solution declared", no_normal_ground, manifest["critical_zero_mode_no_go"]["conclusion"], "contains no normalizable ground vector", "zero-mode")

    audit.check("Hadamard theorem owner DOI", "10.1016/0003-4916(81)90098-1" in manifest["Hadamard_comparator"]["theorem_owner"], manifest["Hadamard_comparator"]["theorem_owner"], "contains DOI", "Hadamard")
    audit.check("massive direct-sum identification", "eight massive static Klein-Gordon ground states" in manifest["Hadamard_comparator"]["result"], manifest["Hadamard_comparator"]["result"], "contains eight massive states", "Hadamard")
    audit.check("Hadamard is comparator only", "comparator only" in manifest["Hadamard_comparator"]["scope_boundary"], manifest["Hadamard_comparator"]["scope_boundary"], "contains comparator only", "Hadamard")
    sqrt_spatial_metric = sp.sqrt(chi / c)
    field_rescaling_squared = sp.sqrt(chi * c)
    audit.check("effective metric time coefficient", sp.simplify(sqrt_spatial_metric * field_rescaling_squared) == chi, sp.simplify(sqrt_spatial_metric * field_rescaling_squared), chi, "Hadamard")
    audit.check("effective metric spatial coefficient", sp.simplify(field_rescaling_squared / sqrt_spatial_metric) == c, sp.simplify(field_rescaling_squared / sqrt_spatial_metric), c, "Hadamard")
    audit.check("effective metric mass coefficient", sp.simplify(sqrt_spatial_metric * field_rescaling_squared * (nu / chi)) == nu, sp.simplify(sqrt_spatial_metric * field_rescaling_squared * (nu / chi)), nu, "Hadamard")
    audit.check("two-point normalization denominator", sp.simplify(sqrt_spatial_metric * field_rescaling_squared) == chi, sp.simplify(sqrt_spatial_metric * field_rescaling_squared), chi, "Hadamard")
    audit.check("effective geometry metadata", "ds^2=-dt^2+(chi/c)dx^2" in manifest["Hadamard_comparator"]["effective_geometry"], manifest["Hadamard_comparator"]["effective_geometry"], "contains metric", "Hadamard")
    audit.check("smooth Cauchy extension metadata", "extend continuously" in manifest["Hadamard_comparator"]["full_Cauchy_extension"], manifest["Hadamard_comparator"]["full_Cauchy_extension"], "contains continuous extension", "Hadamard")
    audit.check("spacetime two-point restriction metadata", "exact finite-mode restriction" in manifest["Hadamard_comparator"]["spacetime_two_point"], manifest["Hadamard_comparator"]["spacetime_two_point"], "contains exact restriction", "Hadamard")

    true_scope = (
        "ordered_Q3_Hessian_spectrum",
        "canonical_a_over_8_mode_normalization",
        "massive_spectral_projective_Gaussian_family",
        "massive_ordered_tangent_Hadamard_comparator",
        "centered_fixed_mode_O_a2_convergence",
        "centered_finite_time_two_point_convergence",
        "bare_mean_field_nu_half_and_z_one",
        "bare_common_tangent_speed",
    )
    false_scope = (
        "natural_centered_exact_projectivity",
        "critical_compact_full_Gaussian_normal_ground",
        "loop_or_RG_speed_protection",
        "interacting_history_cut_state_family",
        "interacting_continuum_Hadamard_state",
        "original_3D_Q3LOCK_parent",
        "physical_light_speed_derived",
        "physical_phase_transition",
        "physical_state_or_vacuum",
        "below_empty_space_comparison",
        "hbar_origin_derived",
        "C0_closed",
        "N1_through_N5_closed",
        "C6_advanced",
        "CP1_complete",
        "Pre_A_complete",
    )
    for key in true_scope:
        audit.check(f"scope true: {key}", manifest["scope"].get(key) is True, manifest["scope"].get(key), True, "scope")
    for key in false_scope:
        audit.check(f"scope false: {key}", manifest["scope"].get(key) is False, manifest["scope"].get(key), False, "scope")
    audit.check("parent history-cut gate remains open", "PARENT OPEN" in manifest["gate_resolution"]["status"], manifest["gate_resolution"]["status"], "contains PARENT OPEN", "scope")
    audit.check("next gate is interacting", manifest["gate_resolution"]["next_gate"] == "PA-CP1-CL8-INTERACTING-REGULATOR-COMPATIBLE-HISTORY-CUT-STATE-FAMILY", manifest["gate_resolution"]["next_gate"], "PA-CP1-CL8-INTERACTING-REGULATOR-COMPATIBLE-HISTORY-CUT-STATE-FAMILY", "scope")

    derived = {
        "Q3_spectrum": {"eigenvalues": sorted(spectrum), "multiplicities": [spectrum[value] for value in sorted(spectrum)]},
        "species_stiffness": [str(value) for value in species],
        "ordered_fixture": fixture_species,
        "canonical_scaling": {"Phi": "sqrt(a/8)*y", "P": "sqrt(8/a)*p", "oscillator_mass": "chi"},
        "covariances": {"field": "hbar/(2*chi*omega)", "momentum": "hbar*chi*omega/2", "product": "hbar^2/4"},
        "centered_fixture": {"L": 6, "coarse_M": 6, "fine_M": 12, "n": 2, "coarse_symbol_squared": coarse_symbol, "fine_symbol_squared": fine_symbol},
        "symbol_series": symbol_series,
        "convergence_errors": {"field": errors_q, "finite_time": errors_t, "field_ratios": ratios_q, "finite_time_ratios": ratios_t},
        "bare_critical": {
            "nu_MF": -correlation_power,
            "z": z_value,
            "common_speed_squared_fixture_c7_chi3": gap_xi_squared.subs({c: 7, chi: 3}),
            "full_compact_Gaussian_ground": not no_normal_ground,
        },
        "negative_ids": list(NEGATIVE_IDS),
    }
    source_hashes = {"script": sha256(SCRIPT), "manifest": sha256(MANIFEST)}
    for path in PARENT_FILES:
        source_hashes[path] = sha256(REPO / path)
    return {
        "schema": SCHEMA,
        "candidate_id": CANDIDATE_ID,
        "parent_ids": manifest["parent_ids"],
        "result_id": RESULT_ID,
        "negative_ids": list(NEGATIVE_IDS),
        "task_id": "T-054",
        "claim_context": "C6-SPACETIME-SIGNATURE",
        "claim_bearing": False,
        "verdict": manifest["verdict"],
        "derived": derived,
        "source_sha256": source_hashes,
        "scope": manifest["scope"],
        "assertions": audit.rows,
        "assertion_summary": {"passed": len(audit.rows), "total": len(audit.rows)},
        "next_gate": manifest["gate_resolution"]["next_gate"],
        "no_overclaim": manifest["no_overclaim"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    payload = build_payload()
    if not args.self_test:
        atomic_json(args.output, payload)
    summary = payload["assertion_summary"]
    print(f"{CANDIDATE_ID}: {summary['passed']}/{summary['total']} PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

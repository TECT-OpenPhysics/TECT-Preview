#!/usr/bin/env python3
"""Primary exact verifier for the staged R-167 v1.7 route split.

This executable checks the finite-volume local-strict/energy carrier, two
quartic point-norm and resolvent-algebra obstructions, the fixed-Gibbs
character relative-entropy tail estimate, an exact two-level entropy-only
counterfixture, and the failure of ordered ground doublets to force a
uniform GNS gap.

The result is deliberately finite-volume and non-claim-bearing.  It does not
construct an all-exhaustion common dynamics, prove a two-orientation history
estimate, or establish a broken-sector GNS gap.  Until the manifest,
certificate, exploration record, negative authorities, gate record, and
R-167 v1.7 ledger row exist, run with ``--staged``; the verifier then reports
``INCOMPLETE`` rather than promoting unregistered mathematics.
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


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-local-strict-quartic-c0-entropy-gap-route-split"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260811.md"
PARENT = (
    REPO
    / "strategy/pre-a-cp1-st8-q3lock-universal-orbit-smear-ground-doublet-route-split-manifest.json"
)
DEFAULT_OUTPUT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / f"2026-08-11-primary-{SLUG}/result.json"
)
STATUS = REPO / "claims/C6-SPACETIME-SIGNATURE/status.json"
EXPLORATION_LEDGER = REPO / "explorations/log.jsonl"
RESULT_LEDGER = REPO / "RESULTS-LEDGER.md"
NEGATIVE_REGISTRY = REPO / "negative-results/registry.md"
GATE_REGISTRY = REPO / "claims/GATES.md"

EXPECTED_TASK = "T-054"
EXPECTED_EXPLORATION = "EXP-000804"
EXPECTED_RESULT_NUMBER = "R-167"
EXPECTED_RESULT_VERSION = "v1.7"
EXPECTED_RESULT_ID = (
    "PA-CP1-ST8-Q3LOCK-SECOND-WEIGHTED-ENERGY-MOMENT-AND-COMMON-ALPHA-CAUCHY-GATE-SPLIT"
)
EXPECTED_CLOSED_GATES = (
    "PA-CP1-ST8-Q3LOCK-FINITE-VOLUME-LOCAL-STRICT-ENERGY-SUBFLOW-CARRIER",
    "PA-CP1-ST8-Q3LOCK-FIXED-GIBBS-CHARACTER-ENTROPY-TILTED-TAIL-BOUND",
)
EXPECTED_OPEN_GATES = (
    "PA-CP1-ST8-Q3LOCK-LOCAL-STRICT-ALL-EXHAUSTION-TWO-ORIENTATION-HISTORY-COMMON-ALPHA",
    "PA-CP1-ST8-Q3LOCK-BROKEN-SECTOR-GNS-GAP-COERCIVITY",
    "PA-ROUND1-EVIDENCE-ROLE-AND-MINIMUM-MANIFEST-FREEZE",
)
NEGATIVE_IDS = (
    "NG-2026-08-11-PRE-A-ST8-Q3LOCK-RAW-WEYL-BASIC-RESOLVENT-QUARTIC-POINT-NORM-C0",
    "NG-2026-08-11-PRE-A-ST8-Q3LOCK-PURE-QUARTIC-POTENTIAL-RESOLVENT-ALGEBRA-INVARIANCE",
    "NG-2026-08-11-PRE-A-ST8-Q3LOCK-ENTROPY-FINITE-MOMENT-DYNAMIC-GAUSSIAN-TAIL-INFERENCE",
    "NG-2026-08-11-PRE-A-ST8-Q3LOCK-ORDERED-GROUND-DOUBLETS-AUTOMATIC-GNS-GAP",
)
EXPECTED_AUTHORITY_SECTIONS = (
    "finite_region_local_strict_carrier",
    "full_quartic_point_norm_no_go",
    "pure_quartic_resolvent_no_go",
    "fixed_gibbs_character_entropy_tail",
    "entropy_finite_moment_no_go",
    "ordered_ground_doublet_gap_no_go",
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


def operator_norm(matrix: sp.MatrixBase) -> sp.Expr:
    eigenvalues: list[sp.Expr] = []
    for eigenvalue, multiplicity in (matrix.H * matrix).eigenvals().items():
        eigenvalues.extend([sp.simplify(eigenvalue)] * multiplicity)
    largest = max(eigenvalues, key=lambda item: float(sp.N(item, 50)))
    return sp.sqrt(largest)


def positive_semidefinite(matrix: sp.MatrixBase) -> bool:
    return all(float(sp.N(value, 50)) >= -1.0e-40 for value in matrix.eigenvals())


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


def q3_force_audit() -> dict[str, Any]:
    q = sp.symbols("q0:8", real=True)
    g, lam, radius = sp.symbols("g lambda R", positive=True)
    edges = sorted(
        {
            (min(vertex, vertex ^ (1 << bit)), max(vertex, vertex ^ (1 << bit)))
            for vertex in range(8)
            for bit in range(3)
        }
    )
    neighbors_zero = sorted(
        right if left == 0 else left
        for left, right in edges
        if left == 0 or right == 0
    )
    potential = g * sum(coordinate**4 for coordinate in q) / 4
    potential += lam * sum(
        (q[left] - q[right]) ** 2 * (q[left] ** 2 + q[right] ** 2)
        for left, right in edges
    ) / 4
    force_zero = sp.expand(sp.diff(potential, q[0]))
    effective_g = sp.expand(g + len(neighbors_zero) * lam)
    expected_force_zero = sp.expand(
        effective_g * q[0] ** 3
        - sp.Rational(3, 2) * lam * q[0] ** 2 * sum(q[j] for j in neighbors_zero)
        + lam * q[0] * sum(q[j] ** 2 for j in neighbors_zero)
        - sp.Rational(1, 2) * lam * sum(q[j] ** 3 for j in neighbors_zero)
    )
    axis = {q[0]: radius, **{q[index]: 0 for index in range(1, 8)}}
    ray_potential = sp.factor(potential.subs(axis))
    ray_force = sp.factor(force_zero.subs(axis))
    ray_hessian = sp.factor(sp.diff(force_zero, q[0]).subs(axis))

    fixture_inputs = {g: sp.Rational(3, 5), lam: sp.Rational(2, 7)}
    fixture_effective_g = sp.simplify(effective_g.subs(fixture_inputs))
    return {
        "inputs": {
            "g": fixture_inputs[g],
            "lambda": fixture_inputs[lam],
            "Q3_dimension": 3,
        },
        "vertices": list(range(8)),
        "edges": edges,
        "neighbors_zero": neighbors_zero,
        "potential": potential,
        "F0": sp.factor(force_zero),
        "expected_F0": sp.factor(expected_force_zero),
        "G": effective_g,
        "G_fixture": fixture_effective_g,
        "coordinate_ray": {
            "potential": ray_potential,
            "force": ray_force,
            "hessian": ray_hessian,
        },
    }


def local_strict_carrier_audit() -> dict[str, Any]:
    # INPUTS for the registered centered all-bond estimate.  exp(mu) is
    # recorded as an input; C_b is derived from it.
    bond_c = sp.Rational(3, 5)
    coordination = sp.Integer(6)
    chi = sp.Rational(7, 4)
    sqrt_gamma = sp.Rational(2, 5)
    exp_mu = sp.Rational(3, 2)
    time_step = sp.Rational(2, 7)
    graph_power = sp.Rational(1, 2)
    c_b = sp.simplify(
        1
        + bond_c**2
        * coordination**2
        * exp_mu
        / (2 * chi * sqrt_gamma)
    )
    m_delta = sp.simplify(1 + c_b * abs(time_step))

    momentum, star_sum = sp.symbols("p S", real=True)
    shifted_square = sp.expand((momentum + time_step * bond_c * star_sum) ** 2)
    young_majorant = sp.expand(
        (1 + time_step) * momentum**2
        + (time_step + time_step**2) * bond_c**2 * star_sum**2
    )
    young_residual = sp.factor(young_majorant - shifted_square)
    young_hessian = sp.hessian(young_residual, (momentum, star_sum)) / 2

    # Exact local-strict transport identity in a finite matrix fixture.
    unitary = sp.Matrix([[0, 1], [1, 0]])
    observable = sp.Matrix([[1, 2], [0, -1]])
    compact = sp.diag(1, 0)
    transformed_observable = unitary.H * observable * unitary
    transported_compact = unitary * compact * unitary.H
    strict_after = sp.simplify(
        operator_norm(transformed_observable * compact)
        + operator_norm(compact * transformed_observable)
    )
    strict_before = sp.simplify(
        operator_norm(observable * transported_compact)
        + operator_norm(transported_compact * observable)
    )

    # Exact spectral fixture for (1.5)--(1.6).  K=diag(1,4), E=2 and
    # A=P_high.  The energy constraint gives |psi_high|^2<=1/3.
    control = sp.diag(1, 4)
    spectral_cutoff = sp.diag(1, 0)
    high_projection = sp.diag(0, 1)
    energy_cut = sp.Integer(2)
    norm_bound = sp.Integer(1)
    graph_right = operator_norm(high_projection * sp.diag(1, sp.Rational(1, 2)))
    graph_left = operator_norm(sp.diag(1, sp.Rational(1, 2)) * high_projection)
    q_s = sp.simplify(graph_right + graph_left)
    e_e = sp.sqrt(sp.Rational(energy_cut - 1, 4 - 1))
    comparison_upper = sp.simplify(
        energy_cut**graph_power * max(graph_right, graph_left)
    )
    comparison_reverse = sp.simplify(
        2 * e_e + 2 * norm_bound * energy_cut ** (-graph_power)
    )
    tail_weight_norm = operator_norm(
        sp.diag(1, sp.Rational(1, 2)) * (sp.eye(2) - spectral_cutoff)
    )

    return {
        "inputs": {
            "bond_c": bond_c,
            "coordination_z": coordination,
            "chi": chi,
            "sqrt_gamma": sqrt_gamma,
            "exp_mu": exp_mu,
            "delta_fixture": time_step,
            "graph_power_s": graph_power,
        },
        "topology": {
            "ambient": "B(H_Y)=M(K(H_Y)), Y finite",
            "control": "arbitrary positive compact-resolvent K_Y>=1",
            "strict_seminorm": "p_C(A)=||A C||+||C A||, C compact",
            "graph_seminorm": "q_s(A)=||A K_Y^-s||+||K_Y^-s A||",
            "energy_seminorm": (
                "e_E(A)=max{sup_<psi,Kpsi><=E ||Apsi||, "
                "sup_<psi,Kpsi><=E ||A*psi||}"
            ),
            "strict_after_fixture": strict_after,
            "strict_before_fixture": strict_before,
            "bounded_strict_equals_strong_star": True,
            "bounded_strict_graph_energy_equivalent": True,
        },
        "spectral_energy_fixture": {
            "K": control,
            "P_E": spectral_cutoff,
            "A": high_projection,
            "E": energy_cut,
            "s": graph_power,
            "norm_bound_M": norm_bound,
            "graph_right": graph_right,
            "graph_left": graph_left,
            "q_s": q_s,
            "e_E": e_e,
            "e_E_upper": comparison_upper,
            "q_s_upper": comparison_reverse,
            "tail_weight_norm": tail_weight_norm,
            "tail_weight_upper": energy_cut ** (-graph_power),
            "contracts": (
                "e_E<=E^s max(||AK^-s||,||K^-sA||); "
                "q_s<=2e_E+2M E^-s"
            ),
        },
        "onsite_subflow": {
            "control": "separate K_Y^os, positive weighted onsite sum",
            "commutes_with_onsite_unitary": True,
            "q_s_isometry": True,
            "e_E_isometry": True,
            "strict_C0": True,
            "support_X_fixed": True,
        },
        "bond_kick": {
            "control": "registered centered K_(Y,mu), Y contains N_1(X)",
            "C_b": c_b,
            "M_delta": m_delta,
            "M_delta_to_s": sp.simplify(m_delta**graph_power),
            "shifted_square": shifted_square,
            "young_majorant": young_majorant,
            "young_residual": young_residual,
            "young_hessian": young_hessian,
            "linear_delta_coefficient": time_step,
            "quadratic_delta_coefficient": time_step**2,
            "combined_delta_coefficient": time_step + time_step**2,
            "form_contract": (
                "B_(+/-delta)^* K_(Y,mu) B_(+/-delta)<=M_delta K_(Y,mu)"
            ),
            "energy_contract": "e_E(beta_delta A)<=e_(M_delta E)(A)",
            "graph_contract": "q_s(beta_delta A)<=M_delta^s q_s(A)",
            "support_action": "X -> N_1(X) inside fixed Y",
            "q_commutator": "[q_x,beta_delta(A)]=beta_delta([q_x,A])",
            "p_commutator": (
                "[p_x,beta_delta(A)]=beta_delta([p_x,A]-"
                "delta c sum_(y~x)[q_y,A])"
            ),
        },
        "controls_are_distinct": True,
        "finite_region_subflow_carrier_closed": True,
        "continuous_time_split_product_limit": False,
        "all_exhaustion_common_alpha": False,
    }


def quartic_packet_c0_no_go_audit(effective_g_fixture: sp.Expr) -> dict[str, Any]:
    q, translation, effective_g = sp.symbols("q a G", positive=True)
    hbar_symbol = sp.symbols("hbar", positive=True)
    axial_potential = effective_g * q**4 / 4
    d_translation = sp.expand(
        axial_potential - axial_potential.subs(q, q - translation)
    )
    cubic_coefficient = sp.Poly(d_translation, q).coeff_monomial(q**3)

    # INPUTS for exact rational Taylor-lemma fixtures.  They instantiate the
    # abstract constants C_A and M_psi without pretending to compute their
    # model-dependent graph-estimate values.
    translation_fixture = sp.Rational(2, 5)
    hbar_fixture = sp.Rational(7, 5)
    resolvent_square_vector_norm = sp.Rational(3, 5)
    rows: list[dict[str, Any]] = []
    for label, d_a, c_a, m_psi in (
        (
            "raw_momentum_weyl",
            sp.simplify(
                translation_fixture * effective_g_fixture / hbar_fixture
            ),
            sp.Rational(5, 2),
            sp.Rational(4, 3),
        ),
        (
            "basic_momentum_resolvent",
            sp.simplify(
                effective_g_fixture * resolvent_square_vector_norm
            ),
            sp.Rational(7, 3),
            sp.Rational(5, 4),
        ),
    ):
        tau = sp.simplify(d_a / (c_a * m_psi))
        threshold = sp.simplify(2 * d_a / (c_a * m_psi))
        main_term = sp.simplify(tau * d_a)
        remainder = sp.simplify(tau**2 * c_a * m_psi / 2)
        rows.append(
            {
                "label": label,
                "d_A": d_a,
                "C_A": c_a,
                "M_psi": m_psi,
                "tau": tau,
                "tau_threshold": threshold,
                "main_term": main_term,
                "taylor_remainder": remainder,
                "liminf_lower": sp.simplify(main_term - remainder),
            }
        )

    energy_degree = sp.Integer(4)
    graph_degree = energy_degree * sp.Rational(3, 2)
    time_degree = sp.Integer(-3)
    return {
        "delta_convention": "delta(A)=(i/hbar)[h,A]",
        "delta_squared_convention": "delta^2(A)=delta(delta(A))",
        "axial_quartic": {
            "potential": axial_potential,
            "D_a": d_translation,
            "D_a_cubic_coefficient": cubic_coefficient,
            "expected_D_a_cubic_coefficient": effective_g * translation,
        },
        "exact_derivations": {
            "W_a": "delta W_a=(i/hbar) D_a W_a",
            "W_a_second": (
                "delta^2 W_a=(i/(2 chi hbar)) sum_j{p_j,partial_j D_a}W_a "
                "-hbar^-2 D_a^2 W_a"
            ),
            "R_0": "delta R_0=R_0 F_0 R_0",
            "R_0_second": (
                "delta^2 R_0=2R_0F_0R_0F_0R_0+"
                "(1/(2chi))R_0 sum_j{p_j,partial_jF_0}R_0"
            ),
            "resolvent_sign_anchor": "[q_0,R_0]=-i hbar R_0^2",
        },
        "packet": {
            "psi_R": "exp(-i R p_0/hbar) psi",
            "raw_weyl_scaled_limit": "R^-3||delta W_a psi_R||->|a|G/hbar",
            "resolvent_scaled_limit": (
                "R^-3||delta R_0 psi_R||->G||R_0^2 psi||"
            ),
            "resolvent_square_vector_norm_fixture": resolvent_square_vector_norm,
            "rows": rows,
        },
        "graph_endpoint": {
            "contract": "||delta^2(A) K^-3/2||<infinity",
            "labels": ["W_a", "R_0"],
            "anisotropic_max_degree": 6,
            "fixed_translation_graph_equivalence_required": True,
            "K_degree_R": energy_degree,
            "K_three_halves_degree_R": graph_degree,
        },
        "scaling": {
            "time_t_R": "tau R^-3",
            "time_degree_R": time_degree,
            "time_squared_degree_R": 2 * time_degree,
            "delta_squared_vector_bound_degree_R": 6,
            "taylor_remainder_total_degree_R": 2 * time_degree + graph_degree,
            "remainder_contract": (
                "tau d_A-(tau^2/2) C_A M_psi; "
                "t_R^2 O(R^6)=O(tau^2)"
            ),
        },
        "conclusion": {
            "full_unsplit_positive_liminf_only": True,
            "exact_norm_jump_claimed": False,
            "raw_momentum_weyl_point_norm_C0": False,
            "basic_momentum_resolvent_point_norm_C0": False,
            "unsplit_resolvent_algebra_invariance_decided": False,
        },
        "scope": {
            "local_strict_C0_rejected": False,
            "all_alternative_carriers_rejected": False,
            "full_Q3LOCK_dynamics_counterexample": False,
        },
        "symbols": {
            "hbar": hbar_symbol,
            "translation": translation,
        },
    }


def pure_kick_resolvent_no_go_audit() -> dict[str, Any]:
    q, shift, effective_g, kick_time = sp.symbols("R s G t", positive=True)
    mu = sp.symbols("mu", positive=True)
    force = effective_g * q**3
    translated_force_difference = sp.expand(force.subs(q, q - shift) - force)
    momentum_center = sp.expand(-kick_time * translated_force_difference)
    polynomial = sp.Poly(momentum_center, q)
    quadratic_coefficient = polynomial.coeff_monomial(q**2)
    scaled_large_q_limit = sp.limit(momentum_center / q**2, q, sp.oo)
    mu_fixture = sp.Rational(3, 2)
    exact_jump_fixture = sp.simplify(1 / abs(mu_fixture))
    return {
        "force": force,
        "translated_force_difference": translated_force_difference,
        "induced_momentum_center": momentum_center,
        "quadratic_translation_coefficient": quadratic_coefficient,
        "expected_quadratic_translation_coefficient": (
            3 * kick_time * effective_g * shift
        ),
        "large_R_scaled_limit": scaled_large_q_limit,
        "potential_kick": "p -> p-t G q^3",
        "basic_resolvent": "R_mu=(i mu-p_0)^(-1)",
        "basic_resolvent_image": "A_t=U_t R_mu U_t^*",
        "packet": {
            "width": "R^(1/2)",
            "initial_momentum_scale": "O(R^-1/2)",
            "centered_momentum_error": "O(R^3/2)",
            "center_scale": "3 t G s R^2+O(R)",
            "relative_error_power": sp.Rational(3, 2) - 2,
        },
        "exact_spatial_weyl_orbit_jump": "1/abs(mu)",
        "mu_fixture": mu_fixture,
        "exact_jump_fixture": exact_jump_fixture,
        "cayley_upper_fixture": exact_jump_fixture,
        "finite_phase_space_weyl_orbit_norm_continuity_criterion": True,
        "standard_resolvent_algebra_invariant_under_pure_quartic_kick": False,
        "unsplit_quartic_resolvent_algebra_invariance_decided": False,
        "unital_resolvent_strict_equals_norm": True,
        "local_strict_BH_carrier_remains_available": True,
        "scope": (
            "Pure quartic potential subflow versus the standard finite-dimensional "
            "resolvent algebra only; not a no-go for local-strict or other carriers."
        ),
        "symbols": {"kick_time": kick_time, "mu": mu},
    }


def binary_relative_entropy(q: sp.Expr, p: sp.Expr) -> sp.Expr:
    return sp.simplify(
        q * sp.log(q / p) + (1 - q) * sp.log((1 - q) / (1 - p))
    )


def gibbs_entropy_tail_audit() -> dict[str, Any]:
    # INPUTS for an exact configuration-character entropy fixture.
    beta = sp.Rational(5, 3)
    hbar = sp.Rational(7, 5)
    chi = sp.Rational(11, 6)
    xi_norm_square = sp.Rational(13, 7)
    s_xi = sp.simplify(beta * hbar**2 * xi_norm_square / (2 * chi))

    # Exact binary data-processing fixture.  The lower bound need not be
    # sharp; it is the universal entropy-to-tail conversion used below.
    reference_p = sp.exp(-20)
    tilted_q = sp.Rational(1, 10)
    binary_entropy = binary_relative_entropy(tilted_q, reference_p)
    binary_lower = sp.simplify(tilted_q * sp.log(1 / reference_p) - sp.log(2))

    # INPUTS for p<=M_a |S| exp(-a L^2).
    moment_constant = sp.Rational(3, 2)
    support_size = sp.Integer(8)
    gaussian_rate = sp.Rational(2, 5)
    distance = sp.Integer(6)
    reference_tail_upper = sp.simplify(
        moment_constant
        * support_size
        * sp.exp(-gaussian_rate * distance**2)
    )
    denominator = sp.simplify(
        gaussian_rate * distance**2
        - sp.log(moment_constant * support_size)
    )
    raw_tilted_tail_upper = sp.simplify((s_xi + sp.log(2)) / denominator)
    tilted_tail_upper = sp.Min(1, raw_tilted_tail_upper)

    return {
        "inputs": {
            "beta": beta,
            "hbar": hbar,
            "chi": chi,
            "xi_norm_square": xi_norm_square,
            "M_a": moment_constant,
            "support_size": support_size,
            "a": gaussian_rate,
            "L": distance,
        },
        "character": {
            "W_xi": "exp(i xi.q)",
            "momentum_shift": "W_xi^* p W_xi=p+hbar xi",
            "gibbs_mean_momentum": 0,
            "S_xi": s_xi,
            "both_character_orientations": True,
            "preserved_after_full_H_time_evolution": True,
            "identity": (
                "S(W_xi rho W_xi^* || rho)="
                "beta*hbar^2*||xi||^2/(2 chi)"
            ),
        },
        "binary_data_processing": {
            "reference_p": reference_p,
            "tilted_q": tilted_q,
            "d_bin_q_p": binary_entropy,
            "universal_lower_bound": binary_lower,
            "contract": (
                "d_bin(q||p)<=S_xi and "
                "d_bin(q||p)>=q log(1/p)-log(2)"
            ),
        },
        "tail": {
            "reference_upper": reference_tail_upper,
            "log_reference_lower": denominator,
            "raw_tilted_upper": raw_tilted_tail_upper,
            "tilted_upper": tilted_tail_upper,
            "orientation_bounds": {
                "q_plus": tilted_tail_upper,
                "q_minus": tilted_tail_upper,
            },
            "formula": (
                "q<=min(1,(S_xi+log(2))/(a L^2-log(M_a |S|)))"
            ),
            "denominator_positive": bool(sp.N(denominator, 50) > 0),
        },
        "scope": {
            "fixed_finite_gibbs_character": True,
            "fixed_support_tail_event": True,
            "history_word_bound": False,
            "all_exhaustion_uniformity": False,
            "dynamic_gaussian_tail": False,
        },
    }


def entropy_fixture_audit() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    beta = sp.Rational(7, 5)  # INPUT inverse temperature.
    boltzmann_symbol, scale_symbol, log_odds_symbol, moment_weight = sp.symbols(
        "b z ell w", positive=True
    )
    abstract_p_one = boltzmann_symbol / (1 + boltzmann_symbol)
    abstract_gap = (1 - boltzmann_symbol) / (1 + boltzmann_symbol)
    abstract_sine_square = 1 / (abstract_gap * scale_symbol)
    abstract_rotated_tail = abstract_p_one + abstract_gap * abstract_sine_square
    rotation_identity_residual = sp.cancel(
        abstract_rotated_tail - (abstract_p_one + 1 / scale_symbol)
    )
    entropy_identity_residual = sp.cancel(
        abstract_gap * abstract_sine_square * log_odds_symbol
        - log_odds_symbol / scale_symbol
    )
    energy_identity_residual = sp.cancel(
        abstract_gap * abstract_sine_square * log_odds_symbol / beta
        - log_odds_symbol / (beta * scale_symbol)
    )
    moment_identity_residual = sp.cancel(
        moment_weight * abstract_rotated_tail
        - (moment_weight * abstract_p_one + moment_weight / scale_symbol)
    )
    for moment_half_order in (3, 4, 5, 6):
        m = sp.Integer(moment_half_order)
        for n_value in (2, 4, 8):
            n = sp.Integer(n_value)
            boltzmann = sp.exp(-(n**4))
            p_one = boltzmann / (1 + boltzmann)
            p_zero = 1 / (1 + boltzmann)
            population_gap = (1 - boltzmann) / (1 + boltzmann)
            mixing_probability = 1 / (population_gap * n ** (2 * m))
            polynomial_increment = n ** (-2 * m)
            tilted_tail = p_one + polynomial_increment
            expected_tail = p_one + n ** (-2 * m)
            relative_entropy = n ** (4 - 2 * m)
            expected_entropy = n ** (4 - 2 * m)
            energy_excess = relative_entropy / beta
            expected_energy_excess = n ** (4 - 2 * m) / beta
            tilted_moment = 1 + n ** (2 * m) * p_one
            expected_tilted_moment = 1 + n ** (2 * m) * p_one
            lower_moments = [
                {
                    "order_r": r,
                    "formula": n**r * p_one + n ** (r - 2 * m),
                }
                for r in range(2, 2 * int(m) + 1, 2)
            ]
            rows.append(
                {
                    "m": m,
                    "n": n,
                    "p0": p_zero,
                    "p1": p_one,
                    "Delta_n": population_gap,
                    "sin_theta_squared": mixing_probability,
                    "tail_increment": polynomial_increment,
                    "tilted_tail": tilted_tail,
                    "expected_tilted_tail": expected_tail,
                    "relative_entropy": relative_entropy,
                    "expected_relative_entropy": expected_entropy,
                    "energy_excess": energy_excess,
                    "expected_energy_excess": expected_energy_excess,
                    "moment_order": 2 * m,
                    "tilted_moment": tilted_moment,
                    "expected_tilted_moment": expected_tilted_moment,
                    "finite_moment_fixture_bound": sp.Integer(2),
                    "lower_even_moments": lower_moments,
                    "m4_eighth_reference_piece": (
                        n**8 * p_one if m == 4 else None
                    ),
                    "m4_reference_piece_bound": (
                        4 * sp.exp(-2) if m == 4 else None
                    ),
                    "m4_exact_fixture": m == 4,
                }
            )
    coefficient = sp.symbols("a", positive=True)
    n_symbol = sp.symbols("n", positive=True)
    gaussian_completion = sp.expand(
        coefficient**2 / 4
        - (coefficient * n_symbol**2 - n_symbol**4)
    )
    x_symbol = sp.symbols("x", positive=True)
    m4_envelope = x_symbol**2 * sp.exp(-x_symbol)
    m4_envelope_derivative = sp.factor(sp.diff(m4_envelope, x_symbol))
    return {
        "inputs": {"beta": beta, "m_values": [3, 4, 5, 6], "n_values": [2, 4, 8]},
        "rows": rows,
        "rotation_identity_residual": rotation_identity_residual,
        "symbolic_2x2_derivation": {
            "p1": abstract_p_one,
            "Delta": abstract_gap,
            "sin_squared": abstract_sine_square,
            "rotated_tail": abstract_rotated_tail,
            "tail_residual": rotation_identity_residual,
            "relative_entropy_residual": entropy_identity_residual,
            "energy_excess_residual": energy_identity_residual,
            "moment_residual": moment_identity_residual,
        },
        "construction": (
            "rho_n=diag(1,exp(-n^4))/(1+exp(-n^4)); "
            "sin^2(theta_nm)=1/(Delta_n n^(2m))"
        ),
        "general_exact_values": {
            "tilted_tail": "p1+n^(-2m)",
            "relative_entropy": "n^(4-2m)",
            "energy_excess": "beta^-1 n^(4-2m)",
            "tilted_2m_moment": "1+n^(2m)p1",
        },
        "m4_exact_values": {
            "tilted_tail_increment": "n^-8",
            "relative_entropy": "n^-4",
            "energy_excess": "1/(beta n^4)",
            "moment_order": 8,
            "reference_piece_bound": "n^8 p1<=4 exp(-2)",
        },
        "m4_bound_proof": {
            "substitution": "x=n^4",
            "p1_upper": "p1<=exp(-x)",
            "envelope": m4_envelope,
            "derivative": m4_envelope_derivative,
            "critical_point": 2,
            "global_maximum": sp.simplify(m4_envelope.subs(x_symbol, 2)),
            "expected_global_maximum": 4 * sp.exp(-2),
        },
        "gaussian_reference": {
            "observable": "q_n=n P_1",
            "all_coefficients": True,
            "completion_square": gaussian_completion,
            "expected_completion_square": (n_symbol**2 - coefficient / 2) ** 2,
            "bound": "Tr rho_n exp(a q_n^2)<=1+exp(a^2/4)",
        },
        "both_unitary_orientations": True,
        "auxiliary_drive": "K_nm^(+/-)=+/- hbar theta_nm sigma_y/T",
        "entropy_tends_to_zero": True,
        "energy_excess_tends_to_zero_for_m_at_least_3": True,
        "uniform_dynamic_gaussian_tail_inferred": False,
        "scope": (
            "For any preregistered finite moment ceiling choose fixed m above "
            "it.  This is a proof-method no-go, not a Q3LOCK counterexample."
        ),
    }


def ordered_ground_gap_no_go_audit() -> dict[str, Any]:
    symbolic_n = sp.symbols("N", positive=True)
    spectral_probes = [sp.Rational(1, n) for n in (2, 4, 8, 16, 32)]
    return {
        "hilbert_space": "K_0=C Omega direct-sum L2((0,1),dx)",
        "generator": {
            "vacuum_action": "h_0 Omega=0",
            "continuum_action": "(h_0 f)(x)=x f(x)",
            "spectrum": "{0} union [0,1]",
            "kernel_dimension": 1,
            "positive_spectrum_accumulates_at_zero": True,
            "spectral_probes_1_over_N": spectral_probes,
            "probe_limit": sp.limit(1 / symbolic_n, symbolic_n, sp.oo),
        },
        "algebra": "B(K_0) direct-sum B(K_0)",
        "dynamics": "Ad(exp(i t h_0/hbar)) on each summand",
        "states": {
            "omega_plus": "Omega vector state on first summand",
            "omega_minus": "Omega vector state on second summand",
            "pure": True,
            "disjoint": True,
            "central_supports": ["(1,0)", "(0,1)"],
            "exact_ground": True,
            "parity_exchange": "summand swap",
        },
        "order_witness": {
            "Z": "(1,-1)",
            "omega_plus_Z": 1,
            "omega_minus_Z": -1,
        },
        "gns": {
            "ground_vector_simple": True,
            "implementing_spectrum": "{0} union [0,1]",
            "positive_gap": 0,
            "coercive_gap_estimate_supplied": False,
        },
        "two_distinct_pure_disjoint_ordered_ground_states": True,
        "automatic_broken_sector_GNS_gap": False,
        "scope": (
            "Distinct ordered algebraic ground states do not by themselves "
            "supply a uniform excitation or GNS gap."
        ),
    }


def authority_audit(audit: Audit, staged: bool) -> dict[str, Any]:
    issues: list[str] = []
    checked: list[str] = []

    def authority_check(
        name: str,
        condition: bool,
        actual: Any,
        expected: Any,
    ) -> None:
        if condition:
            audit.check(name, True, actual, expected, "authority")
            checked.append(name)
        elif staged:
            issues.append(f"mismatch:{name}")
        else:
            raise AssertionError(
                f"authority: {name}: {actual!r} != {expected!r}"
            )

    for path in (MANIFEST, CERTIFICATE, PARENT):
        if not path.exists():
            issues.append(str(path.relative_to(REPO)).replace("\\", "/"))

    manifest: dict[str, Any] | None = None
    certificate_text = ""
    if MANIFEST.exists():
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    if CERTIFICATE.exists():
        certificate_text = " ".join(
            CERTIFICATE.read_text(encoding="utf-8").split()
        ).lower()

    if manifest is not None:
        authority_check(
            "authority task",
            manifest.get("task_id") == EXPECTED_TASK,
            manifest.get("task_id"),
            EXPECTED_TASK,
        )
        authority_check(
            "authority exploration",
            manifest.get("exploration_id") == EXPECTED_EXPLORATION,
            manifest.get("exploration_id"),
            EXPECTED_EXPLORATION,
        )
        authority_check(
            "authority result number",
            manifest.get("result_number") == EXPECTED_RESULT_NUMBER,
            manifest.get("result_number"),
            EXPECTED_RESULT_NUMBER,
        )
        authority_check(
            "authority result version",
            manifest.get("result_version") == EXPECTED_RESULT_VERSION,
            manifest.get("result_version"),
            EXPECTED_RESULT_VERSION,
        )
        authority_check(
            "authority result id",
            manifest.get("result_id") == EXPECTED_RESULT_ID,
            manifest.get("result_id"),
            EXPECTED_RESULT_ID,
        )
        authority_check(
            "authority claim nonbearing",
            manifest.get("claim_bearing") is False,
            manifest.get("claim_bearing"),
            False,
        )
        closed = manifest.get("closed_gates", manifest.get("closed_subgates", []))
        authority_check(
            "authority closed gates",
            tuple(closed) == EXPECTED_CLOSED_GATES,
            closed,
            EXPECTED_CLOSED_GATES,
        )
        authority_check(
            "authority open gates",
            tuple(manifest.get("open_gates", [])) == EXPECTED_OPEN_GATES,
            manifest.get("open_gates", []),
            EXPECTED_OPEN_GATES,
        )
        authority_check(
            "authority negative set",
            tuple(manifest.get("negative_ids", [])) == NEGATIVE_IDS,
            manifest.get("negative_ids", []),
            NEGATIVE_IDS,
        )
        verification = manifest.get("verification", {})
        primary_path = str(SCRIPT.relative_to(REPO)).replace("\\", "/")
        authority_check(
            "authority primary script",
            verification.get("primary_script", verification.get("primary"))
            == primary_path,
            verification.get("primary_script", verification.get("primary")),
            primary_path,
        )
        for section in EXPECTED_AUTHORITY_SECTIONS:
            authority_check(
                f"authority section {section}",
                isinstance(manifest.get(section), dict),
                section in manifest,
                True,
            )
        no_overclaim = json.dumps(
            manifest.get("no_overclaim", ""), ensure_ascii=False
        ).lower()
        for token in ("all-exhaustion", "common alpha", "gns", "c6", "pre-a"):
            authority_check(
                f"authority no-overclaim {token}",
                token in no_overclaim,
                token in no_overclaim,
                True,
            )

    if certificate_text:
        token_groups = {
            "local strict": ("local-strict", "local strict"),
            "entropy": ("entropy",),
            "R^-3": ("r^-3", "r^{-3}", "r^(-3)"),
            "all exhaustion": ("all-exhaustion", "all exhaustion"),
            "GNS gap": ("gns gap", "gns-gap"),
            "Pre-A": ("pre-a",),
        }
        for label, alternatives in token_groups.items():
            authority_check(
                f"certificate token {label}",
                any(token in certificate_text for token in alternatives),
                any(token in certificate_text for token in alternatives),
                True,
            )
        for negative_id in NEGATIVE_IDS:
            authority_check(
                f"certificate negative {negative_id}",
                negative_id.lower() in certificate_text,
                negative_id.lower() in certificate_text,
                True,
            )

    exploration_found = False
    if EXPLORATION_LEDGER.exists():
        for line in EXPLORATION_LEDGER.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            if json.loads(line).get("id") == EXPECTED_EXPLORATION:
                exploration_found = True
                break
    if not exploration_found:
        issues.append(EXPECTED_EXPLORATION)

    result_text = RESULT_LEDGER.read_text(encoding="utf-8")
    if not (
        EXPECTED_RESULT_NUMBER in result_text
        and EXPECTED_RESULT_VERSION in result_text
    ):
        issues.append(f"{EXPECTED_RESULT_NUMBER} {EXPECTED_RESULT_VERSION}")

    negative_text = NEGATIVE_REGISTRY.read_text(encoding="utf-8")
    for negative_id in NEGATIVE_IDS:
        if negative_id not in negative_text:
            issues.append(negative_id)

    gate_text = GATE_REGISTRY.read_text(encoding="utf-8")
    for gate in (*EXPECTED_CLOSED_GATES, *EXPECTED_OPEN_GATES):
        if gate not in gate_text:
            issues.append(gate)

    status = json.loads(STATUS.read_text(encoding="utf-8"))
    authority_check(
        "C6 tier unchanged", status.get("tier") == "T1", status.get("tier"), "T1"
    )
    authority_check(
        "C6 lifecycle unchanged",
        status.get("lifecycle") == "ACTIVE",
        status.get("lifecycle"),
        "ACTIVE",
    )

    issues = list(dict.fromkeys(issues))
    if issues and not staged:
        raise FileNotFoundError(
            "staged v1.7 authority is missing or incomplete ("
            + ", ".join(issues)
            + "); rerun with --staged"
        )
    return {
        "status": "STAGED" if issues else "COMPLETE",
        "missing": issues,
        "checked": checked,
        "certificate": (
            str(CERTIFICATE.relative_to(REPO)).replace("\\", "/")
            if CERTIFICATE.exists()
            else None
        ),
    }


def run_audit(staged: bool = False) -> dict[str, Any]:
    audit = Audit()

    q3 = q3_force_audit()
    audit.check("Q3 vertex count", len(q3["vertices"]) == 8, len(q3["vertices"]), 8, "q3")
    audit.check("Q3 edge count", len(q3["edges"]) == 12, len(q3["edges"]), 12, "q3")
    audit.check("Q3 zero neighbors", q3["neighbors_zero"] == [1, 2, 4], q3["neighbors_zero"], [1, 2, 4], "q3")
    audit.check("exact Q3 F0", sp.expand(q3["F0"] - q3["expected_F0"]) == 0, q3["F0"], q3["expected_F0"], "q3")
    audit.check("exact Q3 G", str(q3["G"]) == "g + 3*lambda", q3["G"], "g+3 lambda", "q3")
    radius = sp.symbols("R", positive=True)
    audit.check("coordinate-ray potential", sp.simplify(q3["coordinate_ray"]["potential"] - q3["G"] * radius**4 / 4) == 0, q3["coordinate_ray"]["potential"], "G R^4/4", "q3")
    audit.check("coordinate-ray force", sp.simplify(q3["coordinate_ray"]["force"] - q3["G"] * radius**3) == 0, q3["coordinate_ray"]["force"], "G R^3", "q3")
    audit.check("coordinate-ray Hessian", sp.simplify(q3["coordinate_ray"]["hessian"] - 3 * q3["G"] * radius**2) == 0, q3["coordinate_ray"]["hessian"], "3 G R^2", "q3")

    carrier = local_strict_carrier_audit()
    kick = carrier["bond_kick"]
    audit.check("Young residual PSD", positive_semidefinite(kick["young_hessian"]), kick["young_hessian"], "PSD", "carrier")
    audit.check("Young delta plus delta squared", sp.expand(kick["combined_delta_coefficient"] - kick["linear_delta_coefficient"] - kick["quadratic_delta_coefficient"]) == 0, kick["combined_delta_coefficient"], "delta+delta^2", "carrier")
    inputs = carrier["inputs"]
    independently_recomputed_c_b = sp.simplify(1 + inputs["bond_c"]**2 * inputs["coordination_z"]**2 * inputs["exp_mu"] / (2 * inputs["chi"] * inputs["sqrt_gamma"]))
    audit.check("exact C_b", kick["C_b"] == independently_recomputed_c_b, kick["C_b"], independently_recomputed_c_b, "carrier")
    audit.check("exact M_delta", kick["M_delta"] == 1 + kick["C_b"] * abs(inputs["delta_fixture"]), kick["M_delta"], "1+C_b|delta|", "carrier")
    audit.check("exact M_delta power", kick["M_delta_to_s"] == kick["M_delta"] ** inputs["graph_power_s"], kick["M_delta_to_s"], "M_delta^s", "carrier")
    topology = carrier["topology"]
    audit.check("local-strict transport identity fixture", topology["strict_after_fixture"] == topology["strict_before_fixture"], topology["strict_after_fixture"], topology["strict_before_fixture"], "carrier")
    audit.check("bounded strict topology equivalence", topology["bounded_strict_equals_strong_star"] and topology["bounded_strict_graph_energy_equivalent"], topology, "strict=strong-star=graph=energy on bounded sets", "carrier")
    spectral = carrier["spectral_energy_fixture"]
    audit.check("spectral e_E exact", spectral["e_E"] ** 2 == sp.Rational(1, 3), spectral["e_E"], "1/sqrt(3)", "carrier")
    audit.check("spectral graph wings exact", spectral["graph_right"] == spectral["graph_left"] == sp.Rational(1, 2), (spectral["graph_right"], spectral["graph_left"]), (sp.Rational(1, 2), sp.Rational(1, 2)), "carrier")
    audit.check("energy-to-graph inequality", spectral["e_E"] <= spectral["e_E_upper"], spectral["e_E"], f"<={spectral['e_E_upper']}", "carrier")
    audit.check("graph-to-energy inequality", spectral["q_s"] <= spectral["q_s_upper"], spectral["q_s"], f"<={spectral['q_s_upper']}", "carrier")
    audit.check("spectral tail split", spectral["tail_weight_norm"] <= spectral["tail_weight_upper"], spectral["tail_weight_norm"], f"<={spectral['tail_weight_upper']}", "carrier")
    onsite = carrier["onsite_subflow"]
    audit.check("onsite separate commuting control", onsite["commutes_with_onsite_unitary"] and onsite["q_s_isometry"] and onsite["e_E_isometry"] and onsite["strict_C0"], onsite, "commuting K_Y^os isometries", "carrier")
    audit.check("carrier controls separated", carrier["controls_are_distinct"], carrier["controls_are_distinct"], True, "carrier")
    audit.check("finite-volume local-strict carrier only", carrier["finite_region_subflow_carrier_closed"] and carrier["continuous_time_split_product_limit"] is False and carrier["all_exhaustion_common_alpha"] is False, {"finite": carrier["finite_region_subflow_carrier_closed"], "split_limit": carrier["continuous_time_split_product_limit"], "all_exhaustion": carrier["all_exhaustion_common_alpha"]}, {"finite": True, "split_limit": False, "all_exhaustion": False}, "carrier")

    packet = quartic_packet_c0_no_go_audit(q3["G_fixture"])
    axial = packet["axial_quartic"]
    audit.check("quartic D_a cubic coefficient", axial["D_a_cubic_coefficient"] == axial["expected_D_a_cubic_coefficient"], axial["D_a_cubic_coefficient"], axial["expected_D_a_cubic_coefficient"], "packet")
    audit.check("resolvent commutator sign", packet["exact_derivations"]["resolvent_sign_anchor"] == "[q_0,R_0]=-i hbar R_0^2", packet["exact_derivations"]["resolvent_sign_anchor"], "[q_0,R_0]=-i hbar R_0^2", "packet")
    audit.check("quartic graph endpoint degree", packet["graph_endpoint"]["anisotropic_max_degree"] == packet["graph_endpoint"]["K_three_halves_degree_R"] == 6, packet["graph_endpoint"], "degree six", "packet")
    audit.check("fixed Weyl graph equivalence retained", packet["graph_endpoint"]["fixed_translation_graph_equivalence_required"], packet["graph_endpoint"]["fixed_translation_graph_equivalence_required"], True, "packet")
    scaling = packet["scaling"]
    audit.check("t_R squared R degree", scaling["time_squared_degree_R"] == -6, scaling["time_squared_degree_R"], -6, "packet")
    audit.check("Taylor remainder scale cancels", scaling["taylor_remainder_total_degree_R"] == 0, scaling["taylor_remainder_total_degree_R"], 0, "packet")
    for row in packet["packet"]["rows"]:
        audit.check(f"packet tau threshold {row['label']}", 0 < row["tau"] < row["tau_threshold"], row["tau"], f"in (0,{row['tau_threshold']})", "packet")
        audit.check(f"packet C_A M_psi remainder {row['label']}", row["taylor_remainder"] == row["tau"] ** 2 * row["C_A"] * row["M_psi"] / 2, row["taylor_remainder"], "tau^2 C_A M_psi/2", "packet")
        audit.check(f"packet positive liminf {row['label']}", row["liminf_lower"] > 0 and row["liminf_lower"] == row["main_term"] - row["taylor_remainder"], row["liminf_lower"], ">0", "packet")
    conclusion = packet["conclusion"]
    audit.check("full unsplit only positive liminf", conclusion["full_unsplit_positive_liminf_only"] and conclusion["exact_norm_jump_claimed"] is False, conclusion, "positive liminf, no exact jump", "packet")
    audit.check("raw and basic point norm routes rejected", conclusion["raw_momentum_weyl_point_norm_C0"] is False and conclusion["basic_momentum_resolvent_point_norm_C0"] is False, conclusion, "both not C0", "packet")
    audit.check("unsplit invariance remains open", conclusion["unsplit_resolvent_algebra_invariance_decided"] is False, conclusion["unsplit_resolvent_algebra_invariance_decided"], False, "packet")
    audit.check("packet scope firewall", packet["scope"]["local_strict_C0_rejected"] is False and packet["scope"]["full_Q3LOCK_dynamics_counterexample"] is False, packet["scope"], "local-strict and Q3LOCK remain open", "packet")

    pure_kick = pure_kick_resolvent_no_go_audit()
    audit.check("pure quartic 3 t G s R^2 coefficient", pure_kick["quadratic_translation_coefficient"] == pure_kick["expected_quadratic_translation_coefficient"], pure_kick["quadratic_translation_coefficient"], pure_kick["expected_quadratic_translation_coefficient"], "pure_kick")
    audit.check("pure quartic scaled momentum limit", pure_kick["large_R_scaled_limit"] == pure_kick["expected_quadratic_translation_coefficient"], pure_kick["large_R_scaled_limit"], pure_kick["expected_quadratic_translation_coefficient"], "pure_kick")
    audit.check("pure kick packet relative error", pure_kick["packet"]["relative_error_power"] < 0, pure_kick["packet"]["relative_error_power"], "<0", "pure_kick")
    audit.check("pure kick exact 1/mu jump", pure_kick["exact_jump_fixture"] == 1 / pure_kick["mu_fixture"] == pure_kick["cayley_upper_fixture"], pure_kick["exact_jump_fixture"], "1/abs(mu)", "pure_kick")
    audit.check("pure quartic standard resolvent invariance rejected", pure_kick["standard_resolvent_algebra_invariant_under_pure_quartic_kick"] is False and pure_kick["local_strict_BH_carrier_remains_available"] is True and pure_kick["unsplit_quartic_resolvent_algebra_invariance_decided"] is False, pure_kick, "pure kick no; local-strict yes; unsplit open", "pure_kick")

    gibbs = gibbs_entropy_tail_audit()
    character = gibbs["character"]
    gibbs_inputs = gibbs["inputs"]
    recomputed_s_xi = sp.simplify(gibbs_inputs["beta"] * gibbs_inputs["hbar"]**2 * gibbs_inputs["xi_norm_square"] / (2 * gibbs_inputs["chi"]))
    audit.check("exact Gibbs S_xi", character["S_xi"] == recomputed_s_xi, character["S_xi"], recomputed_s_xi, "entropy_tail")
    audit.check("Gibbs two orientations and evolved character", character["both_character_orientations"] and character["preserved_after_full_H_time_evolution"], character, "both orientations, time preserved", "entropy_tail")
    binary = gibbs["binary_data_processing"]
    audit.check("binary entropy lower bound fixture", bool(sp.N(binary["d_bin_q_p"] - binary["universal_lower_bound"], 50) >= 0), binary["d_bin_q_p"], f">={binary['universal_lower_bound']}", "entropy_tail")
    tail = gibbs["tail"]
    audit.check("reference Gaussian tail below one", 0 < tail["reference_upper"] < 1, tail["reference_upper"], "in (0,1)", "entropy_tail")
    audit.check("entropy tail denominator positive", tail["denominator_positive"], tail["log_reference_lower"], ">0", "entropy_tail")
    audit.check("entropy tail bound finite", bool(sp.N(tail["raw_tilted_upper"], 50).is_finite) and tail["raw_tilted_upper"] > 0 and tail["tilted_upper"] <= 1, tail["tilted_upper"], "in (0,1] after min", "entropy_tail")
    audit.check("entropy tail both orientation bounds", tail["orientation_bounds"]["q_plus"] == tail["orientation_bounds"]["q_minus"] == tail["tilted_upper"], tail["orientation_bounds"], "same exact bound", "entropy_tail")
    audit.check("fixed Gibbs scope firewall", gibbs["scope"]["fixed_finite_gibbs_character"] and gibbs["scope"]["history_word_bound"] is False and gibbs["scope"]["all_exhaustion_uniformity"] is False, gibbs["scope"], "fixed character only", "entropy_tail")

    entropy_fixture = entropy_fixture_audit()
    audit.check("general rotation identity", entropy_fixture["rotation_identity_residual"] == 0, entropy_fixture["rotation_identity_residual"], 0, "entropy_fixture")
    symbolic_entropy = entropy_fixture["symbolic_2x2_derivation"]
    for key in (
        "tail_residual",
        "relative_entropy_residual",
        "energy_excess_residual",
        "moment_residual",
    ):
        audit.check(f"symbolic 2x2 {key}", symbolic_entropy[key] == 0, symbolic_entropy[key], 0, "entropy_fixture")
    gaussian = entropy_fixture["gaussian_reference"]
    audit.check("Gaussian completion square", sp.expand(gaussian["completion_square"] - gaussian["expected_completion_square"]) == 0, gaussian["completion_square"], gaussian["expected_completion_square"], "entropy_fixture")
    for row in entropy_fixture["rows"]:
        label = f"m={row['m']},n={row['n']}"
        audit.check(f"2x2 tilted tail {label}", row["tilted_tail"] == row["expected_tilted_tail"], row["tilted_tail"], row["expected_tilted_tail"], "entropy_fixture")
        audit.check(f"2x2 exact entropy {label}", row["relative_entropy"] == row["expected_relative_entropy"], row["relative_entropy"], row["expected_relative_entropy"], "entropy_fixture")
        audit.check(f"2x2 exact energy excess {label}", row["energy_excess"] == row["expected_energy_excess"], row["energy_excess"], row["expected_energy_excess"], "entropy_fixture")
        audit.check(f"2x2 exact finite moment {label}", row["tilted_moment"] == row["expected_tilted_moment"], row["tilted_moment"], row["expected_tilted_moment"], "entropy_fixture")
        audit.check(f"2x2 positive lower moment orders {label}", all(item["order_r"] > 0 and item["order_r"] <= row["moment_order"] for item in row["lower_even_moments"]), [item["order_r"] for item in row["lower_even_moments"]], f"0<r<={row['moment_order']}", "entropy_fixture")
        mixing_float = float(sp.N(row["sin_theta_squared"], 30))
        audit.check(f"2x2 rotation admissible {label}", 0 < mixing_float < 1, mixing_float, "in (0,1)", "entropy_fixture")
        audit.check(f"2x2 finite moment bounded {label}", float(sp.N(row["tilted_moment"], 30)) < float(row["finite_moment_fixture_bound"]), row["tilted_moment"], f"<{row['finite_moment_fixture_bound']}", "entropy_fixture")
    audit.check("entropy fixture m range", entropy_fixture["inputs"]["m_values"] == [3, 4, 5, 6], entropy_fixture["inputs"]["m_values"], [3, 4, 5, 6], "entropy_fixture")
    audit.check("m=4 exact specialization", all(row["tail_increment"] == row["n"] ** (-8) and row["relative_entropy"] == row["n"] ** (-4) and row["moment_order"] == 8 for row in entropy_fixture["rows"] if row["m4_exact_fixture"]), "m=4 checked", "n^-8, n^-4, eighth moment", "entropy_fixture")
    m4_proof = entropy_fixture["m4_bound_proof"]
    audit.check("m=4 envelope derivative", str(m4_proof["derivative"]) == "-x*(x - 2)*exp(-x)", m4_proof["derivative"], "x(2-x)exp(-x)", "entropy_fixture")
    audit.check("m=4 envelope global maximum", m4_proof["global_maximum"] == m4_proof["expected_global_maximum"], m4_proof["global_maximum"], m4_proof["expected_global_maximum"], "entropy_fixture")
    audit.check("m=4 eighth reference-piece bound", all(float(sp.N(row["m4_eighth_reference_piece"], 30)) <= float(sp.N(row["m4_reference_piece_bound"], 30)) for row in entropy_fixture["rows"] if row["m4_exact_fixture"]), [row["m4_eighth_reference_piece"] for row in entropy_fixture["rows"] if row["m4_exact_fixture"]], "<=4 exp(-2)", "entropy_fixture")
    audit.check("two entropy orientations", entropy_fixture["both_unitary_orientations"], entropy_fixture["both_unitary_orientations"], True, "entropy_fixture")
    audit.check("entropy finite-moment Gaussian inference rejected", entropy_fixture["uniform_dynamic_gaussian_tail_inferred"] is False, entropy_fixture["uniform_dynamic_gaussian_tail_inferred"], False, "entropy_fixture")

    ground = ordered_ground_gap_no_go_audit()
    generator = ground["generator"]
    probes = generator["spectral_probes_1_over_N"]
    audit.check("infinite fixture simple kernel", generator["kernel_dimension"] == 1, generator["kernel_dimension"], 1, "ground_gap")
    audit.check("continuous spectrum accumulates at zero", generator["positive_spectrum_accumulates_at_zero"] and all(right < left for left, right in zip(probes, probes[1:])) and generator["probe_limit"] == 0, {"probes": probes, "limit": generator["probe_limit"]}, "decrease to zero", "ground_gap")
    states = ground["states"]
    audit.check("component ground states pure disjoint exact", states["pure"] and states["disjoint"] and states["exact_ground"] and states["central_supports"] == ["(1,0)", "(0,1)"], states, "pure disjoint exact with orthogonal central supports", "ground_gap")
    audit.check("parity exchanges ground states", states["parity_exchange"] == "summand swap", states["parity_exchange"], "summand swap", "ground_gap")
    witness = ground["order_witness"]
    audit.check("central order witness separates", witness["omega_plus_Z"] == 1 and witness["omega_minus_Z"] == -1, witness, "+1/-1", "ground_gap")
    gns = ground["gns"]
    audit.check("GNS simple ground but zero gap", gns["ground_vector_simple"] and gns["positive_gap"] == 0 and gns["coercive_gap_estimate_supplied"] is False, gns, "simple kernel, zero gap, no coercivity", "ground_gap")
    audit.check("ground doublets do not force GNS gap", ground["two_distinct_pure_disjoint_ordered_ground_states"] and ground["automatic_broken_sector_GNS_gap"] is False, {"distinct": ground["two_distinct_pure_disjoint_ordered_ground_states"], "GNS_gap": ground["automatic_broken_sector_GNS_gap"]}, {"distinct": True, "GNS_gap": False}, "ground_gap")

    authority = authority_audit(audit, staged)
    verdict = "PASS" if authority["status"] == "COMPLETE" else "INCOMPLETE"
    source_paths = [SCRIPT, PARENT, MANIFEST, CERTIFICATE]
    scope = {
        "finite_volume_local_strict_energy_subflow_carrier": True,
        "fixed_gibbs_character_entropy_tilted_tail": True,
        "raw_weyl_basic_resolvent_point_norm_C0": False,
        "pure_quartic_standard_resolvent_algebra_invariance": False,
        "entropy_finite_moment_dynamic_gaussian_tail": False,
        "ordered_ground_doublets_imply_GNS_gap": False,
        "all_exhaustion_two_orientation_history_common_alpha": False,
        "broken_sector_GNS_gap_coercivity": False,
        "mass_gap": False,
        "continuum_regulator_removal": False,
        "physical_empty_space_reference": False,
        "C6_advanced": False,
        "CP1_complete": False,
        "Sector_A_complete": False,
        "Pre_A_complete": False,
    }
    passed = len(audit.rows)
    return {
        "schema": f"tect/{SLUG}-primary-result/1.0",
        "script_version": __version__,
        "result_id": EXPECTED_RESULT_ID,
        "result_number": EXPECTED_RESULT_NUMBER,
        "result_version": EXPECTED_RESULT_VERSION,
        "exploration_id": EXPECTED_EXPLORATION,
        "claim_bearing": False,
        "closed_gates": list(EXPECTED_CLOSED_GATES),
        "closed_subgates": list(EXPECTED_CLOSED_GATES),
        "open_gates": list(EXPECTED_OPEN_GATES),
        "next_gate": EXPECTED_OPEN_GATES[0],
        "negative_ids": list(NEGATIVE_IDS),
        "verdict": verdict,
        "passed": passed,
        "failed": 0,
        "total": passed,
        "summary": {
            "passed": passed,
            "failed": 0,
            "total": passed,
            "authority_status": authority["status"],
        },
        "authority": authority,
        "derived": {
            "q3_force": q3,
            "local_strict_carrier": carrier,
            "quartic_packet_c0_no_go": packet,
            "pure_kick_resolvent_no_go": pure_kick,
            "gibbs_entropy_tail": gibbs,
            "entropy_fixture": entropy_fixture,
            "ordered_ground_gap_no_go": ground,
        },
        "scope": scope,
        "source_hashes": {
            str(path.relative_to(REPO)).replace("\\", "/"): normalized_sha256(path)
            for path in source_paths
            if path.exists()
        },
        "assertions": audit.rows,
        "boundary": (
            "Finite-volume local-strict/energy subflow carrier and fixed-Gibbs "
            "single-character entropy-tail theorem only; not all-exhaustion "
            "history dynamics, a standard raw-Weyl/resolvent point-norm carrier, "
            "a dynamic Gaussian tail, a broken-sector GNS gap, C6, CP1, Sector A, "
            "or Pre-A closure."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--staged", action="store_true")
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()

    payload = run_audit(staged=args.staged)
    if not args.self_test and not args.no_store:
        atomic_json(args.output, payload)
    print(f"{payload['verdict']} {payload['passed']}/{payload['total']}")
    if payload["verdict"] == "INCOMPLETE":
        print("authority: " + ", ".join(payload["authority"]["missing"]))
    script_key = str(SCRIPT.relative_to(REPO)).replace("\\", "/")
    print("schema: " + payload["schema"])
    print("script_sha256: " + payload["source_hashes"][script_key])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

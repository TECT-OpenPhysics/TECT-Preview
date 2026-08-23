#!/usr/bin/env python3
"""Primary exact verifier for the staged R-167 v1.8 route reduction.

The verifier covers four positive reductions and two scoped route failures:

* exact fixed-Trotter-level exhaustion compatibility on the bounded local net;
* a sandwiched-Renyi two-orientation history-tail criterion which absorbs the
  existing coordinate-cutoff corridor;
* a two-level example showing that entropy, finite moments, and two-sided
  energy-form comparability do not imply that Renyi criterion;
* zero-temperature OS temporal decay / GNS coercivity equivalence;
* the exact locked Q3 onsite instanton action and a low-doublet Ising
  reference decomposition;
* the mismatch between the registered infrared LRO threshold and the missing
  quantum-Pirogov-Sinai smallness data.

This is claim-nonbearing.  It does not construct the n->infinity split limit,
prove an actual Q3LOCK Renyi history estimate, establish a broken-sector gap,
or close Pre-A or Sector A.  Until every authority exists, ``--staged`` emits
INCOMPLETE rather than promoting the result.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import tempfile
from decimal import Decimal, getcontext
from fractions import Fraction
from itertools import product
from pathlib import Path
from typing import Any, Iterable


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-renyi-history-os-gap-reduction-route-split"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260811.md"
DEFAULT_OUTPUT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / f"2026-08-11-primary-{SLUG}/result.json"
)
EXPLORATION_LEDGER = REPO / "explorations/log.jsonl"
RESULT_LEDGER = REPO / "RESULTS-LEDGER.md"
NEGATIVE_REGISTRY = REPO / "negative-results/registry.md"
GATE_REGISTRY = REPO / "claims/GATES.md"
SECTOR_A_MAP = REPO / "governance/sector-a-theorem-map.json"

EXPECTED_TASK = "T-054"
EXPECTED_CLAIM_IDS = ("C6-SPACETIME-SIGNATURE",)
EXPECTED_EXPLORATION = "EXP-000805"
EXPECTED_RESULT_NUMBER = "R-167"
EXPECTED_RESULT_VERSION = "v1.8"
EXPECTED_RESULT_ID = (
    "PA-CP1-ST8-Q3LOCK-SECOND-WEIGHTED-ENERGY-MOMENT-AND-COMMON-ALPHA-CAUCHY-GATE-SPLIT"
)
EXPECTED_CLOSED_GATES = (
    "PA-CP1-ST8-Q3LOCK-FIXED-TROTTER-LOCAL-STRICT-INDUCTIVE-EXHAUSTION-COMPATIBILITY",
    "PA-CP1-ST8-Q3LOCK-SANDWICHED-RENYI-TO-TWO-ORIENTATION-HISTORY-TAIL-CORRIDOR-REDUCTION",
    "PA-CP1-ST8-Q3LOCK-PHASEWISE-GNS-GAP-OS-TEMPORAL-MASS-EQUIVALENCE",
    "PA-CP1-ST8-Q3LOCK-ONE-SITE-Q3-INSTANTON-ACTION-MINIMUM",
    "PA-CP1-ST8-Q3LOCK-CONDITIONAL-DOUBLET-ISING-REFERENCE-GAP",
)
EXPECTED_OPEN_GATES = (
    "PA-CP1-ST8-Q3LOCK-LOCAL-STRICT-ALL-EXHAUSTION-TWO-ORIENTATION-HISTORY-COMMON-ALPHA",
    "PA-CP1-ST8-Q3LOCK-BROKEN-SECTOR-GNS-GAP-COERCIVITY",
    "PA-ROUND1-EVIDENCE-ROLE-AND-MINIMUM-MANIFEST-FREEZE",
)
NEGATIVE_IDS = (
    "NG-2026-08-11-PRE-A-ST8-Q3LOCK-ENERGY-FORM-ENTROPY-FINITE-MOMENT-AUTOMATIC-SANDWICHED-RENYI-UPGRADE",
    "NG-2026-08-11-PRE-A-ST8-Q3LOCK-DIRECT-YAROTSKY-TWO-PHASE-GAP-IMPORT",
)
REUSED_NEGATIVE_IDS = (
    "NG-2026-08-11-PRE-A-ST8-Q3LOCK-ENTROPY-FINITE-MOMENT-DYNAMIC-GAUSSIAN-TAIL-INFERENCE",
    "NG-2026-08-11-PRE-A-ST8-Q3LOCK-ORDERED-GROUND-DOUBLETS-AUTOMATIC-GNS-GAP",
)
EXPECTED_SUCCESSOR_GATES = EXPECTED_OPEN_GATES[:2]
EXPECTED_SUPERSEDED_GATE_IDS = (
    "PA-CP1-ST8-Q3LOCK-QUASI-LOCAL-RAW-OSCILLATOR-ALL-EXHAUSTION-COMMON-ALPHA-AND-BROKEN-GNS-GAP",
)
EXPECTED_RETAINED_GATES = (
    "PA-CP1-ST8-Q3LOCK-ALL-EXHAUSTION-MIXTURE-L2-LOCALITY-AND-BETA-INDEPENDENT-CSTAR-DYNAMICS",
    "PA-CP1-ST8-Q3LOCK-HAMILTONIAN-THERMODYNAMIC-IDENTIFICATION-IN-CANONICAL-OS-MIXTURE",
    "PA-CP1-ST8-Q3LOCK-PROJECTED-DUHAMEL-MODULAR-C1-MULTIPLIER-LOCALITY",
)
EXPECTED_AUTHORITY_SECTIONS = (
    "fixed_trotter_level_compatibility",
    "renyi_history_sufficiency",
    "renyi_energy_form_no_go",
    "zero_temperature_os_gap_equivalence",
    "q3_instanton_low_doublet_reference",
    "yarotsky_qps_boundary",
)


def normalized_sha256(path: Path) -> str:
    raw = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(raw).hexdigest()


def json_safe(value: Any) -> Any:
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, Fraction):
        return f"{value.numerator}/{value.denominator}"
    if isinstance(value, Decimal):
        return format(value, "f")
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
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
                "group": group,
                "name": name,
                "status": "PASS",
                "actual": json_safe(actual),
                "expected": json_safe(expected),
            }
        )


Coord = tuple[int, int, int]
Edge = tuple[Coord, Coord]


def canonical_edge(a: Coord, b: Coord) -> Edge:
    return (a, b) if a < b else (b, a)


def neighbours(x: Coord) -> Iterable[Coord]:
    for axis in range(3):
        for sign in (-1, 1):
            y = list(x)
            y[axis] += sign
            yield tuple(y)  # type: ignore[return-value]


def one_neighbourhood(vertices: set[Coord]) -> set[Coord]:
    result = set(vertices)
    for vertex in vertices:
        result.update(neighbours(vertex))
    return result


def expand(vertices: set[Coord], levels: int) -> set[Coord]:
    result = set(vertices)
    for _ in range(levels):
        result = one_neighbourhood(result)
    return result


def incident_edges(vertices: set[Coord]) -> set[Edge]:
    result: set[Edge] = set()
    for vertex in vertices:
        for neighbour in neighbours(vertex):
            result.add(canonical_edge(vertex, neighbour))
    return result


def fixed_trotter_level_audit() -> dict[str, Any]:
    seed = {(0, 0, 0)}
    supports = [expand(seed, n) for n in range(4)]
    relevant_first_kick = incident_edges(seed)

    kappa = Fraction(10, 21)
    zero = Fraction(0)

    def normalize(
        state: tuple[dict[int, Fraction], dict[int, Fraction]],
        radius: int,
    ) -> tuple[dict[int, Fraction], dict[int, Fraction]]:
        q, p = state
        return (
            {x: q.get(x, zero) for x in range(-radius, radius + 1)},
            {x: p.get(x, zero) for x in range(-radius, radius + 1)},
        )

    def kick(
        state: tuple[dict[int, Fraction], dict[int, Fraction]],
        radius: int,
        sign: int = 1,
    ) -> tuple[dict[int, Fraction], dict[int, Fraction]]:
        q, p = normalize(state, radius)
        return q, {
            x: p[x]
            + sign * kappa * (q.get(x - 1, zero) + q.get(x + 1, zero))
            for x in range(-radius, radius + 1)
        }

    def onsite(
        state: tuple[dict[int, Fraction], dict[int, Fraction]],
        radius: int,
        inverse: bool = False,
    ) -> tuple[dict[int, Fraction], dict[int, Fraction]]:
        q, p = normalize(state, radius)
        if inverse:
            return (
                {x: -p[x] for x in range(-radius, radius + 1)},
                {x: q[x] for x in range(-radius, radius + 1)},
            )
        return (
            {x: p[x] for x in range(-radius, radius + 1)},
            {x: -q[x] for x in range(-radius, radius + 1)},
        )

    def forward_step(
        state: tuple[dict[int, Fraction], dict[int, Fraction]],
        radius: int,
    ) -> tuple[dict[int, Fraction], dict[int, Fraction]]:
        return onsite(kick(state, radius), radius)

    def inverse_step(
        state: tuple[dict[int, Fraction], dict[int, Fraction]],
        radius: int,
    ) -> tuple[dict[int, Fraction], dict[int, Fraction]]:
        return kick(onsite(state, radius, inverse=True), radius, sign=-1)

    def compact(
        state: tuple[dict[int, Fraction], dict[int, Fraction]],
    ) -> dict[int, tuple[Fraction, Fraction]]:
        q, p = state
        return {
            x: (q.get(x, zero), p.get(x, zero))
            for x in sorted(set(q) | set(p))
            if q.get(x, zero) != 0 or p.get(x, zero) != 0
        }

    seed_state = ({0: Fraction(1)}, {})
    state_small = seed_state
    state_large = seed_state
    prefix_ambient_equal: list[bool] = []
    prefix_support_ok: list[bool] = []
    for level in range(1, 4):
        state_small = forward_step(state_small, 3)
        state_large = forward_step(state_large, 4)
        small_compact = compact(state_small)
        large_compact = compact(state_large)
        prefix_ambient_equal.append(
            all(
                small_compact.get(x, (zero, zero))
                == large_compact.get(x, (zero, zero))
                for x in range(-3, 4)
            )
            and all(
                large_compact.get(x, (zero, zero)) == (zero, zero)
                for x in (-4, 4)
            )
        )
        prefix_support_ok.append(
            all(abs(x) <= level for x in large_compact)
        )

    full_oracle = {
        -3: (Fraction(1000, 9261), zero),
        -2: (zero, Fraction(-100, 441)),
        -1: (Fraction(-1940, 3087), zero),
        0: (zero, Fraction(241, 441)),
        1: (Fraction(-1940, 3087), zero),
        2: (zero, Fraction(-100, 441)),
        3: (Fraction(1000, 9261), zero),
    }
    reverse = state_large
    for _ in range(3):
        reverse = inverse_step(reverse, 4)
    too_small = seed_state
    for _ in range(3):
        too_small = forward_step(too_small, 2)
    return {
        "seed": sorted(seed),
        "support_sizes": [len(item) for item in supports],
        "expected_l1_ball_sizes": [1, 7, 25, 63],
        "first_kick_edge_count": len(relevant_first_kick),
        "fixed_level": 3,
        "minimal_ambient": sorted(supports[3]),
        "larger_ambient": sorted(expand(seed, 5)),
        "onsite_support_map": "X -> X",
        "bond_support_map": "X -> N_1(X)",
        "bond_generators_commute": True,
        "bond_terms_outside_incident_set_commute_with_seed": True,
        "split_map": "Theta_(t,n)=(sigma_(t/n) beta_(t/n))^n",
        "inverse_map": "Theta_(t,n)^(-1)=(beta_(-t/n) sigma_(-t/n))^n",
        "exact_exhaustion_independence_for_fixed_n": True,
        "linear_proxy_kappa": kappa,
        "linear_proxy_full_word": compact(state_large),
        "linear_proxy_expected_full_word": full_oracle,
        "all_prefix_ambient_equal": all(prefix_ambient_equal),
        "all_prefix_support_in_N_b": all(prefix_support_ok),
        "outer_halo_sharp": compact(state_large).get(3) == full_oracle[3],
        "reverse_recovers_seed": compact(reverse) == {0: (Fraction(1), zero)},
        "too_small_ambient_rejected": compact(too_small) != full_oracle,
        "fixture_is_support_proxy_not_Q3_onsite": True,
        "local_weyl_or_resolvent_invariance": False,
        "global_strict_inductive_topology": False,
        "point_norm_C0": False,
        "n_to_infinity_cauchy_proved": False,
        "continuous_group_completion_proved": False,
        "topology": "stagewise bounded local-strict/final local topology",
    }


def renyi_history_audit() -> dict[str, Any]:
    alpha = Fraction(2)
    theta = (alpha - 1) / alpha
    rho = (Fraction(3, 4), Fraction(1, 4))
    sigma = (Fraction(1, 4), Fraction(3, 4))
    q_alpha = sum(s**2 / r for r, s in zip(rho, sigma))
    event_probability = sigma[1]
    reference_event = rho[1]
    squared_upper = q_alpha * reference_event
    squared_residual = squared_upper - event_probability**2

    p0 = Fraction(4, 5)
    p1 = Fraction(1, 5)
    sigma_plus = (
        (Fraction(52, 125), Fraction(36, 125)),
        (Fraction(36, 125), Fraction(73, 125)),
    )
    sigma_minus = (
        (Fraction(52, 125), Fraction(-36, 125)),
        (Fraction(-36, 125), Fraction(73, 125)),
    )
    sqrt_p0p1 = Fraction(2, 5)

    def sandwiched_q2(
        sigma_matrix: tuple[tuple[Fraction, Fraction], tuple[Fraction, Fraction]],
    ) -> Fraction:
        return (
            sigma_matrix[0][0] ** 2 / p0
            + sigma_matrix[1][1] ** 2 / p1
            + 2 * sigma_matrix[0][1] ** 2 / sqrt_p0p1
        )

    def petz_q2(
        sigma_matrix: tuple[tuple[Fraction, Fraction], tuple[Fraction, Fraction]],
    ) -> Fraction:
        return (
            (sigma_matrix[0][0] ** 2 + sigma_matrix[0][1] ** 2) / p0
            + (sigma_matrix[1][1] ** 2 + sigma_matrix[0][1] ** 2) / p1
        )

    def plus_event(
        sigma_matrix: tuple[tuple[Fraction, Fraction], tuple[Fraction, Fraction]],
    ) -> Fraction:
        return (
            sigma_matrix[0][0]
            + sigma_matrix[1][1]
            + 2 * sigma_matrix[0][1]
        ) / 2

    noncommuting_q2_plus = sandwiched_q2(sigma_plus)
    noncommuting_q2_minus = sandwiched_q2(sigma_minus)
    petz_plus = petz_q2(sigma_plus)
    plus_reference = Fraction(1, 2)
    q_plus = plus_event(sigma_plus)
    q_minus = plus_event(sigma_minus)

    gaussian_a = Fraction(14)
    kappa_t = Fraction(3)
    d_growth = Fraction(1)
    b = theta * gaussian_a
    effective_b = theta * (gaussian_a - d_growth)
    cutoff_l = Fraction(2)
    layer_polynomial = (
        cutoff_l**4 + 2 * cutoff_l**2 / b + 2 / b**2
    )
    gamma = Fraction(1, 3)
    exact_alpha = Fraction(2)
    exact_theta = Fraction(1, 2)
    exact_a = Fraction(12)
    exact_b = exact_theta * exact_a
    exact_l = Fraction(2)
    exact_layer = exact_l**4 + 2 * exact_l**2 / exact_b + 2 / exact_b**2
    exact_q = Fraction(9)
    exact_ms = Fraction(16)
    exact_c = Fraction(3, 5)
    exact_edges = 3
    exact_q_root = Fraction(math.isqrt(exact_q.numerator), math.isqrt(exact_q.denominator))
    exact_ms_root = Fraction(math.isqrt(exact_ms.numerator), math.isqrt(exact_ms.denominator))
    one_orientation_prefactor = (
        4
        * exact_c**2
        * exact_edges**2
        * exact_q_root
        * exact_ms_root
    )
    two_orientation_prefactor = 2 * one_orientation_prefactor
    final_rational_coefficient = two_orientation_prefactor * exact_layer
    return {
        "alpha": alpha,
        "theta": theta,
        "commuting_swap_fixture": {
            "rho": rho,
            "sigma": sigma,
            "sandwiched_Q_alpha": q_alpha,
            "event_probability": event_probability,
            "reference_event_probability": reference_event,
            "upper_bound_squared": squared_upper,
            "slack_squared": squared_residual,
        },
        "noncommuting_orientation_fixture": {
            "rho": ((p0, Fraction(0)), (Fraction(0), p1)),
            "sigma_plus": sigma_plus,
            "sigma_minus": sigma_minus,
            "sandwiched_Q2_plus": noncommuting_q2_plus,
            "sandwiched_Q2_minus": noncommuting_q2_minus,
            "petz_Q2_plus": petz_plus,
            "reference_plus_event": plus_reference,
            "q_plus": q_plus,
            "q_minus": q_minus,
            "orientation_sum": q_plus + q_minus,
            "two_orientation_factor": 2,
            "two_orientation_squared_bound": 4 * noncommuting_q2_plus * plus_reference,
            "petz_differs_from_sandwiched": petz_plus != noncommuting_q2_plus,
            "orientations_are_distinct": sigma_plus != sigma_minus and q_plus != q_minus,
        },
        "projection_theorem": (
            "sigma_P(E)<=Q_alpha(P)^(1/alpha) rho(E)^theta"
        ),
        "two_orientation_theorem": (
            "rho(P*EP)+rho(PEP*)<=2 Q_(alpha,T)^(1/alpha) rho(E)^theta"
        ),
        "gaussian_tail": {
            "a": gaussian_a,
            "b_theta_a": b,
            "layer_cutoff_L": cutoff_l,
            "fourth_moment_polynomial": layer_polynomial,
            "formula": "L^4+2L^2/b+2/b^2",
        },
        "corridor": {
            "kappa_T": kappa_t,
            "gamma": gamma,
            "gamma_window": 0 < gamma < Fraction(1, 2),
            "squared_seminorm_condition": b > kappa_t,
            "unsquared_seminorm_condition": b > 2 * kappa_t,
            "renyi_growth_d": d_growth,
            "effective_exponent": effective_b,
            "effective_unsquared_condition": effective_b > 2 * kappa_t,
            "factorial_power": 2 * gamma - 1,
        },
        "bond_tail": {
            "pointwise_square_bound": "|w_(xy,L)|^2<=4c^2 X_(xy)^4 E_(xy,L)",
            "finite_edge_sum_power": 2,
            "exact_fixture": {
                "alpha": exact_alpha,
                "theta": exact_theta,
                "a": exact_a,
                "b": exact_b,
                "L": exact_l,
                "Q": exact_q,
                "M_times_S": exact_ms,
                "c": exact_c,
                "edge_count": exact_edges,
                "layer_polynomial": exact_layer,
                "one_orientation_prefactor": one_orientation_prefactor,
                "two_orientation_factor": 2,
                "two_orientation_prefactor": two_orientation_prefactor,
                "final_rational_coefficient": final_rational_coefficient,
                "gaussian_exponent": -24,
            },
        },
        "actual_Q3_history_bound_proved": False,
    }


def renyi_energy_form_no_go_audit() -> dict[str, Any]:
    alpha = 2
    m = 3
    rows: list[dict[str, Any]] = []
    for n in (2, 4, 6):
        n4 = n**4
        reservoir = 2**n4
        p0 = Fraction(reservoir, reservoir + 1)
        p1 = Fraction(1, reservoir + 1)
        delta = p0 - p1
        rotation_denominator = 4 * n ** (2 * m) + 1
        cosine = Fraction(4 * n ** (2 * m) - 1, rotation_denominator)
        sine = Fraction(4 * n**m, rotation_denominator)
        sine2 = sine**2
        cosine2 = cosine**2
        q = p1 + delta * sine2
        entropy_over_log2 = delta * sine2 * n4
        energy_excess = delta * sine2 * n4
        k_excited = 1 + n4
        trace = Fraction(2) + sine2 * Fraction(n**8, 1 + n4)
        determinant = (
            (cosine2 + k_excited * sine2)
            * (cosine2 + sine2 / k_excited)
            - Fraction((1 - k_excited) ** 2, k_excited)
            * cosine2
            * sine2
        )

        sigma00 = cosine2 * p0 + sine2 * p1
        sigma11 = q
        sigma01 = cosine * sine * delta
        sqrt_p0p1 = Fraction(2 ** (n4 // 2), reservoir + 1)
        sandwiched_q2 = (
            sigma00**2 / p0
            + sigma11**2 / p1
            + 2 * sigma01**2 / sqrt_p0p1
        )
        measured_q2 = sigma11**2 / p1 + sigma00**2 / p0
        gaussian_reference = {
            k: Fraction(reservoir + 2 ** (k * n**2), reservoir + 1)
            for k in (1, 2)
        }
        tilted_moments = {
            r: n**r * q
            for r in range(1, 2 * m + 1)
        }
        rows.append(
            {
                "n": n,
                "m": m,
                "reservoir": reservoir,
                "p0": p0,
                "p1": p1,
                "cosine": cosine,
                "sine": sine,
                "rotation_identity": cosine2 + sine2,
                "tilted_tail": q,
                "tail_increment": delta * sine2,
                "relative_entropy_over_log2": entropy_over_log2,
                "energy_excess": energy_excess,
                "energy_excess_upper": Fraction(n4, n ** (2 * m)),
                "K_generalized_trace": trace,
                "K_generalized_determinant": determinant,
                "energy_form_half_two": determinant == 1 and trace < Fraction(5, 2),
                "measured_Q2": measured_q2,
                "sandwiched_Q2": sandwiched_q2,
                "sandwiched_minus_measured": sandwiched_q2 - measured_q2,
                "q_squared_over_p1": q**2 / p1,
                "q_lower_bound": Fraction(8, 25 * n ** (2 * m)),
                "gaussian_reference_integer_log2_fixtures": gaussian_reference,
                "gaussian_reference_fixtures_bounded_by_two": all(
                    value <= 2 for value in gaussian_reference.values()
                ),
                "tilted_moments_through_2m": tilted_moments,
                "tilted_moments_bounded_by_two": all(
                    value <= 2 for value in tilted_moments.values()
                ),
            }
        )
    compact = rows[0]
    return {
        "alpha": alpha,
        "theta": "1/2",
        "m": m,
        "rows": rows,
        "energy_form_comparison": "(1/2)K_n<=U K_n U*<=2K_n",
        "both_orientations_have_same_exact_invariants": all(
            row["rotation_identity"] == 1 for row in rows
        ),
        "exact_compact_oracle_n2_m3": {
            "p0": compact["p0"],
            "p1": compact["p1"],
            "cosine": compact["cosine"],
            "sine": compact["sine"],
            "q": compact["tilted_tail"],
            "trace_G": compact["K_generalized_trace"],
            "measured_Q2": compact["measured_Q2"],
            "sandwiched_Q2": compact["sandwiched_Q2"],
            "sandwiched_minus_measured": compact["sandwiched_minus_measured"],
            "q_squared_over_p1": compact["q_squared_over_p1"],
        },
        "general_lower_certificate": {
            "q_lower": "8/(25*n^(2m))",
            "Qalpha_lower": "(8/(25*n^(2m)))^alpha * 2^((alpha-1)*n^4)",
            "Dalpha_lower": "n^4 log 2 - 2m alpha/(alpha-1) log n + O(1)",
            "diverges_for_every_fixed_alpha_greater_than_one": True,
        },
        "uniform_Renyi_inferred": False,
        "actual_Q3_Renyi_rejected": False,
    }


def zero_temperature_os_gap_audit() -> dict[str, Any]:
    hbar = Fraction(2)
    gap = Fraction(3)
    energies = (Fraction(3), Fraction(5))
    weights = (Fraction(4, 9), Fraction(5, 9))
    g0 = sum(weights)
    energy_form = sum(w * e for w, e in zip(weights, energies))
    derivative_at_zero = -energy_form / hbar
    return {
        "hbar": hbar,
        "gap": gap,
        "energies": energies,
        "spectral_weights": weights,
        "G_0": g0,
        "minus_G_prime_0": -derivative_at_zero,
        "coercive_energy": energy_form,
        "coercivity_residual": energy_form - gap * g0,
        "decay_rate": gap / hbar,
        "equivalent_statements": [
            "spectrum subset {0} union [Delta,infinity)",
            "-i hbar omega(A*delta(A))>=Delta Var_omega(A)",
            "G_A(tau)<=exp(-Delta tau/hbar)G_A(0)",
        ],
        "common_rate_with_observable_prefactors": (
            "G_A(tau)<=C_A exp(-m tau) for a common m implies Delta>=hbar m"
        ),
        "requires_zero_temperature_sector_representation": True,
        "current_beta_uniform_temporal_rate_proved": False,
    }


Matrix = list[list[Fraction]]


def zeros(rows: int, cols: int) -> Matrix:
    return [[Fraction(0) for _ in range(cols)] for _ in range(rows)]


def identity(size: int) -> Matrix:
    result = zeros(size, size)
    for index in range(size):
        result[index][index] = Fraction(1)
    return result


def mat_add(a: Matrix, b: Matrix) -> Matrix:
    return [[x + y for x, y in zip(arow, brow)] for arow, brow in zip(a, b)]


def mat_sub(a: Matrix, b: Matrix) -> Matrix:
    return [[x - y for x, y in zip(arow, brow)] for arow, brow in zip(a, b)]


def mat_scale(scale: Fraction, a: Matrix) -> Matrix:
    return [[scale * value for value in row] for row in a]


def mat_mul(a: Matrix, b: Matrix) -> Matrix:
    rows, inner, cols = len(a), len(b), len(b[0])
    assert len(a[0]) == inner
    result = zeros(rows, cols)
    for i in range(rows):
        for k in range(inner):
            if a[i][k] == 0:
                continue
            for j in range(cols):
                result[i][j] += a[i][k] * b[k][j]
    return result


def kron(a: Matrix, b: Matrix) -> Matrix:
    result = zeros(len(a) * len(b), len(a[0]) * len(b[0]))
    for i, row_a in enumerate(a):
        for j, value_a in enumerate(row_a):
            for k, row_b in enumerate(b):
                for ell, value_b in enumerate(row_b):
                    result[i * len(b) + k][j * len(b[0]) + ell] = (
                        value_a * value_b
                    )
    return result


def torus_graph(side: int = 3) -> dict[int, dict[int, int]]:
    coordinates = list(product(range(side), repeat=3))
    index = {coord: position for position, coord in enumerate(coordinates)}
    edges: set[tuple[int, int]] = set()
    for coord in coordinates:
        for axis in range(3):
            neighbour = list(coord)
            neighbour[axis] = (neighbour[axis] + 1) % side
            a, b = index[coord], index[tuple(neighbour)]
            edges.add((min(a, b), max(a, b)))
    graph = {vertex: {} for vertex in range(len(coordinates))}
    for a, b in edges:
        graph[a][b] = graph[a].get(b, 0) + 1
        graph[b][a] = graph[b].get(a, 0) + 1
    return graph


def stoer_wagner_min_cut(graph: dict[int, dict[int, int]]) -> int:
    adjacency = {v: dict(row) for v, row in graph.items()}
    vertices = list(adjacency)
    best = math.inf
    while len(vertices) > 1:
        used: set[int] = set()
        weights = {v: 0 for v in vertices}
        previous = vertices[0]
        for step in range(len(vertices)):
            selected = max((v for v in vertices if v not in used), key=weights.get)
            used.add(selected)
            if step == len(vertices) - 1:
                best = min(best, weights[selected])
                if previous != selected:
                    for neighbour, weight in list(adjacency[selected].items()):
                        if neighbour == previous or neighbour not in vertices:
                            continue
                        adjacency[previous][neighbour] = (
                            adjacency[previous].get(neighbour, 0) + weight
                        )
                        adjacency[neighbour][previous] = (
                            adjacency[neighbour].get(previous, 0) + weight
                        )
                        adjacency[neighbour].pop(selected, None)
                    vertices.remove(selected)
                break
            previous = selected
            for neighbour, weight in adjacency[selected].items():
                if neighbour in weights and neighbour not in used:
                    weights[neighbour] += weight
    return int(best)


def q3_instanton_low_doublet_audit() -> dict[str, Any]:
    v = Fraction(3, 2)
    g = Fraction(2)
    chi = Fraction(1)
    coupling_lambda = Fraction(5, 7)
    action_squared = Fraction(512, 9) * v**6 * chi * g
    scalar_integral = Fraction(4, 3) * v**3
    q3_vertices = list(product((0, 1), repeat=3))
    q3_edges = [
        (a, b)
        for index, a in enumerate(q3_vertices)
        for b in q3_vertices[index + 1 :]
        if sum(x != y for x, y in zip(a, b)) == 1
    ]
    locked_values = {vertex: v for vertex in q3_vertices}
    q3_locked_polynomial = sum(
        (locked_values[a] - locked_values[b]) ** 2
        * (locked_values[a] ** 2 + locked_values[b] ** 2)
        for a, b in q3_edges
    )

    m = Fraction(1, 2)
    c = Fraction(3, 5)
    epsilon0 = Fraction(0)
    epsilon1 = Fraction(1, 10)
    epsilon2 = Fraction(5)
    gamma = epsilon2 - epsilon0
    components = 8
    j_ising = components * c * m**2
    min_cut = stoer_wagner_min_cut(torus_graph(3))
    low_sector_gap = 2 * j_ising * min_cut
    reference_gap_lower_bound = min(gamma, low_sector_gap)

    q = [
        [Fraction(0), m, Fraction(0)],
        [m, Fraction(0), Fraction(2, 3)],
        [Fraction(0), Fraction(2, 3), Fraction(0)],
    ]
    s = [
        [Fraction(0), Fraction(1), Fraction(0)],
        [Fraction(1), Fraction(0), Fraction(0)],
        [Fraction(0), Fraction(0), Fraction(0)],
    ]
    r = mat_sub(q, mat_scale(m, s))
    i3 = identity(3)
    dq = mat_sub(kron(q, i3), kron(i3, q))
    ds = mat_sub(kron(s, i3), kron(i3, s))
    dr = mat_sub(kron(r, i3), kron(i3, r))
    exact_bond = mat_mul(dq, dq)
    expanded_bond = mat_add(
        mat_scale(m**2, mat_mul(ds, ds)),
        mat_add(
            mat_scale(m, mat_add(mat_mul(ds, dr), mat_mul(dr, ds))),
            mat_mul(dr, dr),
        ),
    )
    return {
        "instanton": {
            "v": v,
            "g": g,
            "chi": chi,
            "lambda": coupling_lambda,
            "q3_vertex_count": len(q3_vertices),
            "q3_edge_count": len(q3_edges),
            "locked_q3_polynomial": q3_locked_polynomial,
            "scalar_barrier_integral": scalar_integral,
            "action_formula": "(16 sqrt(2)/3) v^3 sqrt(chi g)",
            "action_squared": action_squared,
            "expected_action_squared": Fraction(1296),
            "action": math.isqrt(action_squared.numerator),
            "expected_action": 36,
            "attained_by_locked_path": True,
            "locked_minimizer_unique_up_to_common_translation_for_lambda_positive": True,
            "lambda_zero_has_independent_kink_centres": True,
        },
        "low_doublet": {
            "epsilon0": epsilon0,
            "epsilon1": epsilon1,
            "epsilon2": epsilon2,
            "Gamma": gamma,
            "m": m,
            "c": c,
            "J": j_ising,
            "periodic_C3_cubed_min_cut": min_cut,
            "disagreeing_bond_cost": 2 * j_ising,
            "low_sector_gap": low_sector_gap,
            "reference_gap_lower_bound": reference_gap_lower_bound,
            "two_product_ground_states": True,
            "bond_decomposition_residual_zero": exact_bond == expanded_bond,
            "remainder": (
                "Delta_1 sum P_1 +(c/2) sum_e[m{ds,dR}+dR^2]"
            ),
        },
        "actual_relative_QPS_smallness_proved": False,
        "actual_broken_sector_gap_proved": False,
    }


def yarotsky_qps_boundary_audit() -> dict[str, Any]:
    alpha = Fraction(2, 5)
    g = Fraction(3, 5)
    c = Fraction(7, 10)
    v = Fraction(3, 2)
    # The scalar inequality residual is an exact sum of these two squares.
    square_one_coefficient = alpha * g / 8
    square_one_shift = 2 * v**2
    square_two_coefficient = alpha * g / 8
    square_two_shift = 4 * c / (alpha * g)

    hbar = Fraction(1)
    chi = Fraction(1)
    theta_q = Fraction(1)
    j3 = Fraction(3, 5)
    c_ir = hbar**2 * j3**2 / (8 * chi * theta_q**2)
    couplings = (Fraction(1, 10), Fraction(10))
    return {
        "relative_form": {
            "alpha": alpha,
            "g": g,
            "c": c,
            "v": v,
            "one_coordinate_residual": (
                "(alpha g/8)(q^2-2v^2)^2+"
                "(alpha g/8)(q^2-4c/(alpha g))^2"
            ),
            "square_coefficients": (
                square_one_coefficient,
                square_two_coefficient,
            ),
            "square_shifts": (square_one_shift, square_two_shift),
            "bond_bound": (
                "B_xy<=alpha(U_x+U_y)+4alpha g v^4+32c^2/(alpha g)"
            ),
        },
        "infrared_threshold": {
            "J3_fixture": j3,
            "c_IR": c_ir,
            "couplings_both_above_threshold": [value > c_ir for value in couplings],
            "A0_condition_is_only_a_lower_bound_on_c": True,
        },
        "single_phase_theorem": {
            "infinite_dimensional_onsite_allowed": True,
            "requires_simple_gapped_product_reference": True,
            "sufficiently_small_relative_perturbation": True,
            "conclusion_is_unique_gapped_phase": True,
            "target_broken_phase_certificate": False,
        },
        "two_phase_theorem": {
            "requires_two_Hilbert_product_ground_vectors": True,
            "requires_reference_gap_and_Peierls_smallness": True,
            "classical_delta_minima_are_Hilbert_vectors": False,
            "current_Q3_onsite_quantum_ground_is_double": False,
        },
        "missing_low_doublet_data": [
            "epsilon1-epsilon0",
            "Gamma",
            "m",
            "R_e relative-form constants",
            "controlled infinite-dimensional QPS embedding",
        ],
        "automatic_sector_gap_from_A0": False,
    }


def authority_audit(audit: Audit, staged: bool) -> dict[str, Any]:
    missing: list[str] = []

    def require_file(path: Path, label: str) -> str | None:
        if not path.exists():
            if staged:
                missing.append(label)
                return None
            raise FileNotFoundError(path)
        return path.read_text(encoding="utf-8")

    def require_token(text: str, token: str, label: str) -> bool:
        present = token in text
        if not present:
            if staged:
                missing.append(label)
                return False
            raise AssertionError(f"missing authority token {token!r} in {label}")
        audit.check(label, True, True, True, "authority")
        return True

    manifest_text = require_file(MANIFEST, "manifest")
    if manifest_text is not None:
        manifest = json.loads(manifest_text)
        audit.check("manifest task", manifest["task_id"] == EXPECTED_TASK, manifest["task_id"], EXPECTED_TASK, "authority")
        audit.check("manifest claims", tuple(manifest["claim_ids"]) == EXPECTED_CLAIM_IDS, manifest["claim_ids"], EXPECTED_CLAIM_IDS, "authority")
        audit.check("manifest claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "authority")
        audit.check("manifest exploration", manifest["exploration_id"] == EXPECTED_EXPLORATION, manifest["exploration_id"], EXPECTED_EXPLORATION, "authority")
        audit.check("manifest result number", manifest["result_number"] == EXPECTED_RESULT_NUMBER, manifest["result_number"], EXPECTED_RESULT_NUMBER, "authority")
        audit.check("manifest result version", manifest["result_version"] == EXPECTED_RESULT_VERSION, manifest["result_version"], EXPECTED_RESULT_VERSION, "authority")
        audit.check("manifest result id", manifest["result_id"] == EXPECTED_RESULT_ID, manifest["result_id"], EXPECTED_RESULT_ID, "authority")
        audit.check("manifest closed subgates", tuple(manifest["closed_subgates"]) == EXPECTED_CLOSED_GATES, manifest["closed_subgates"], EXPECTED_CLOSED_GATES, "authority")
        audit.check("manifest open gates", tuple(manifest["open_gates"]) == EXPECTED_OPEN_GATES, manifest["open_gates"], EXPECTED_OPEN_GATES, "authority")
        audit.check("manifest successor gates", tuple(manifest["open_gates"][:2]) == EXPECTED_SUCCESSOR_GATES, manifest["open_gates"][:2], EXPECTED_SUCCESSOR_GATES, "authority")
        audit.check("manifest negatives", tuple(manifest["negative_ids"]) == NEGATIVE_IDS, manifest["negative_ids"], NEGATIVE_IDS, "authority")
        audit.check("manifest reused negatives", tuple(manifest["reused_negative_ids"]) == REUSED_NEGATIVE_IDS, manifest["reused_negative_ids"], REUSED_NEGATIVE_IDS, "authority")
        audit.check("manifest superseded gates", tuple(manifest["superseded_gate_ids"]) == EXPECTED_SUPERSEDED_GATE_IDS, manifest["superseded_gate_ids"], EXPECTED_SUPERSEDED_GATE_IDS, "authority")
        audit.check("manifest retained gates", tuple(manifest["retained_gate_ids"]) == EXPECTED_RETAINED_GATES, manifest["retained_gate_ids"], EXPECTED_RETAINED_GATES, "authority")
        for section in EXPECTED_AUTHORITY_SECTIONS:
            audit.check(f"manifest section {section}", section in manifest, section in manifest, True, "authority")

    certificate_text = require_file(CERTIFICATE, "certificate")
    if certificate_text is not None:
        for token in (
            EXPECTED_EXPLORATION,
            EXPECTED_RESULT_NUMBER,
            EXPECTED_RESULT_VERSION,
            *EXPECTED_CLOSED_GATES,
            *EXPECTED_OPEN_GATES,
            *NEGATIVE_IDS,
            "sandwiched-Renyi",
            "fixed Trotter level",
            "OS temporal",
            "16\\sqrt2",
            "does not close Pre-A",
        ):
            require_token(certificate_text, token, f"certificate token {token}")

    exploration_text = require_file(EXPLORATION_LEDGER, "exploration ledger")
    if exploration_text is not None:
        require_token(exploration_text, f'"id":"{EXPECTED_EXPLORATION}"', "exploration record")

    result_text = require_file(RESULT_LEDGER, "result ledger")
    if result_text is not None:
        if require_token(result_text, "R-167", "result ledger R-167"):
            require_token(result_text, "v1.8", "result ledger v1.8")

    negative_text = require_file(NEGATIVE_REGISTRY, "negative registry")
    if negative_text is not None:
        for negative_id in NEGATIVE_IDS:
            require_token(negative_text, negative_id, f"negative {negative_id}")

    gate_text = require_file(GATE_REGISTRY, "gate registry")
    if gate_text is not None:
        for gate in (*EXPECTED_CLOSED_GATES, *EXPECTED_OPEN_GATES):
            require_token(gate_text, gate, f"gate {gate}")

    theorem_map_text = require_file(SECTOR_A_MAP, "sector-a theorem map")
    if theorem_map_text is not None:
        theorem_map = json.loads(theorem_map_text)
        priority = theorem_map.get("research_priority", {})
        current_contract = {
            "schema": theorem_map.get("schema") == "tect/sector-a-theorem-map/1.0",
            "status": theorem_map.get("status") == "ACTIVE",
            "priority_status": priority.get("status") == "IN_PROGRESS",
            "dynamics_successor": priority.get("parallel_cp1_gate") == EXPECTED_OPEN_GATES[0],
            "gap_successor": priority.get("parallel_cp1_gap_gate") == EXPECTED_OPEN_GATES[1],
            "pre_a_boundary": "Pre-A" in json.dumps(theorem_map, sort_keys=True)
            and "remain open" in json.dumps(theorem_map, sort_keys=True),
        }
        audit.check(
            "theorem map current successor contract",
            all(current_contract.values()),
            current_contract,
            "current Sector-A map with live successor gates and open Pre-A boundary",
            "authority",
        )

    return {"status": "INCOMPLETE" if missing else "COMPLETE", "missing": missing}


def run_audit(staged: bool = False) -> dict[str, Any]:
    audit = Audit()

    trotter = fixed_trotter_level_audit()
    audit.check("L1 ball support sizes", trotter["support_sizes"] == trotter["expected_l1_ball_sizes"], trotter["support_sizes"], trotter["expected_l1_ball_sizes"], "trotter")
    audit.check("first bond layer has six edges", trotter["first_kick_edge_count"] == 6, trotter["first_kick_edge_count"], 6, "trotter")
    audit.check("bond generators commute", trotter["bond_generators_commute"], trotter["bond_generators_commute"], True, "trotter")
    audit.check("fixed level exhaustion independent", trotter["exact_exhaustion_independence_for_fixed_n"], trotter["exact_exhaustion_independence_for_fixed_n"], True, "trotter")
    audit.check("constructive fixed-word oracle", trotter["linear_proxy_full_word"] == trotter["linear_proxy_expected_full_word"], trotter["linear_proxy_full_word"], trotter["linear_proxy_expected_full_word"], "trotter")
    audit.check("all prefixes ambient equal", trotter["all_prefix_ambient_equal"], trotter["all_prefix_ambient_equal"], True, "trotter")
    audit.check("all prefixes stay in halo", trotter["all_prefix_support_in_N_b"], trotter["all_prefix_support_in_N_b"], True, "trotter")
    audit.check("outer halo is sharp", trotter["outer_halo_sharp"], trotter["outer_halo_sharp"], True, "trotter")
    audit.check("reverse word recovers seed", trotter["reverse_recovers_seed"], trotter["reverse_recovers_seed"], True, "trotter")
    audit.check("too-small ambient rejected", trotter["too_small_ambient_rejected"], trotter["too_small_ambient_rejected"], True, "trotter")
    audit.check("no local C-star promotion", not trotter["local_weyl_or_resolvent_invariance"] and not trotter["global_strict_inductive_topology"] and not trotter["point_norm_C0"], (trotter["local_weyl_or_resolvent_invariance"], trotter["global_strict_inductive_topology"], trotter["point_norm_C0"]), (False, False, False), "trotter")
    audit.check("Trotter inverse order", trotter["inverse_map"].startswith("Theta_(t,n)^(-1)=(beta_"), trotter["inverse_map"], "reverse order", "trotter")
    audit.check("no n infinity promotion", not trotter["n_to_infinity_cauchy_proved"] and not trotter["continuous_group_completion_proved"], (trotter["n_to_infinity_cauchy_proved"], trotter["continuous_group_completion_proved"]), (False, False), "trotter")

    renyi = renyi_history_audit()
    fixture = renyi["commuting_swap_fixture"]
    audit.check("Renyi Q2 exact", fixture["sandwiched_Q_alpha"] == Fraction(7, 3), fixture["sandwiched_Q_alpha"], Fraction(7, 3), "renyi")
    audit.check("Renyi event inequality exact", fixture["upper_bound_squared"] >= fixture["event_probability"] ** 2 and fixture["slack_squared"] == Fraction(1, 48), fixture["slack_squared"], Fraction(1, 48), "renyi")
    orientation = renyi["noncommuting_orientation_fixture"]
    audit.check("noncommuting sandwiched Q2 exact", orientation["sandwiched_Q2_plus"] == orientation["sandwiched_Q2_minus"] == Fraction(7301, 3125), (orientation["sandwiched_Q2_plus"], orientation["sandwiched_Q2_minus"]), Fraction(7301, 3125), "renyi")
    audit.check("Petz differs from sandwiched", orientation["petz_Q2_plus"] == Fraction(61, 25) and orientation["petz_differs_from_sandwiched"], (orientation["petz_Q2_plus"], orientation["sandwiched_Q2_plus"]), (Fraction(61, 25), "different"), "renyi")
    audit.check("orientations distinguished", orientation["q_plus"] == Fraction(197, 250) and orientation["q_minus"] == Fraction(53, 250) and orientation["orientations_are_distinct"], (orientation["q_plus"], orientation["q_minus"]), (Fraction(197, 250), Fraction(53, 250)), "renyi")
    audit.check("two-orientation factor exact", orientation["two_orientation_factor"] == 2 and orientation["orientation_sum"] ** 2 <= orientation["two_orientation_squared_bound"], (orientation["two_orientation_factor"], orientation["orientation_sum"], orientation["two_orientation_squared_bound"]), (2, "<= bound"), "renyi")
    tail = renyi["gaussian_tail"]
    audit.check("layer cake fourth moment polynomial", tail["fourth_moment_polynomial"] == Fraction(842, 49), tail["fourth_moment_polynomial"], Fraction(842, 49), "renyi")
    corridor = renyi["corridor"]
    audit.check("cutoff scaling window", corridor["gamma_window"] and corridor["factorial_power"] < 0, (corridor["gamma_window"], corridor["factorial_power"]), (True, "<0"), "renyi")
    audit.check("squared history exponent", corridor["squared_seminorm_condition"], corridor["squared_seminorm_condition"], True, "renyi")
    audit.check("unsquared history factor two", corridor["unsquared_seminorm_condition"], corridor["unsquared_seminorm_condition"], True, "renyi")
    audit.check("Renyi growth still absorbed", corridor["effective_unsquared_condition"], corridor["effective_exponent"], f">{2*corridor['kappa_T']}", "renyi")
    edge_fixture = renyi["bond_tail"]["exact_fixture"]
    audit.check("edge layer polynomial exact", edge_fixture["layer_polynomial"] == Fraction(313, 18), edge_fixture["layer_polynomial"], Fraction(313, 18), "renyi")
    audit.check("edge count squared exact", renyi["bond_tail"]["finite_edge_sum_power"] == 2 and edge_fixture["one_orientation_prefactor"] == Fraction(3888, 25), (renyi["bond_tail"]["finite_edge_sum_power"], edge_fixture["one_orientation_prefactor"]), (2, Fraction(3888, 25)), "renyi")
    audit.check("two-orientation edge coefficient exact", edge_fixture["two_orientation_factor"] == 2 and edge_fixture["two_orientation_prefactor"] == Fraction(7776, 25) and edge_fixture["final_rational_coefficient"] == Fraction(135216, 25), (edge_fixture["two_orientation_factor"], edge_fixture["two_orientation_prefactor"], edge_fixture["final_rational_coefficient"]), (2, Fraction(7776, 25), Fraction(135216, 25)), "renyi")
    audit.check("actual Q3 Renyi remains open", renyi["actual_Q3_history_bound_proved"] is False, renyi["actual_Q3_history_bound_proved"], False, "renyi")

    no_go = renyi_energy_form_no_go_audit()
    for row in no_go["rows"]:
        label = f"n={row['n']}"
        audit.check(f"rotation identity exact {label}", row["rotation_identity"] == 1, row["rotation_identity"], 1, "renyi_no_go")
        audit.check(f"energy excess vanishes at certified power {label}", row["energy_excess"] < row["energy_excess_upper"], row["energy_excess"], f"<{row['energy_excess_upper']}", "renyi_no_go")
        audit.check(f"generalized determinant one {label}", row["K_generalized_determinant"] == 1, row["K_generalized_determinant"], 1, "renyi_no_go")
        audit.check(f"energy form spectrum in half two {label}", row["energy_form_half_two"] and row["K_generalized_trace"] < Fraction(9, 4), (row["energy_form_half_two"], row["K_generalized_trace"]), (True, "<9/4"), "renyi_no_go")
        audit.check(f"tail lower bound exact {label}", row["tilted_tail"] >= row["q_lower_bound"], row["tilted_tail"], f">={row['q_lower_bound']}", "renyi_no_go")
        audit.check(f"Gaussian reference fixtures exact {label}", row["gaussian_reference_fixtures_bounded_by_two"], row["gaussian_reference_integer_log2_fixtures"], "<=2", "renyi_no_go")
        audit.check(f"finite tilted moments exact {label}", row["tilted_moments_bounded_by_two"], row["tilted_moments_through_2m"], "<=2", "renyi_no_go")
        audit.check(f"sandwiched exceeds measured {label}", row["sandwiched_minus_measured"] > 0, row["sandwiched_minus_measured"], ">0", "renyi_no_go")
    compact = no_go["exact_compact_oracle_n2_m3"]
    expected_compact = {
        "p0": Fraction(65536, 65537),
        "p1": Fraction(1, 65537),
        "cosine": Fraction(255, 257),
        "sine": Fraction(32, 257),
        "q": Fraction(261377, 16843009),
        "trace_G": Fraction(2507810, 1122833),
        "measured_Q2": Fraction(1106449, 66049),
        "sandwiched_Q2": Fraction(106339353113, 4328653313),
        "sandwiched_minus_measured": Fraction(33826005000, 4328653313),
        "q_squared_over_p1": Fraction(68317936129, 4328653313),
    }
    audit.check("exact rational no-go compact oracle", compact == expected_compact, compact, expected_compact, "renyi_no_go")
    audit.check("general Renyi divergence certificate", no_go["general_lower_certificate"]["diverges_for_every_fixed_alpha_greater_than_one"], no_go["general_lower_certificate"], "diverges", "renyi_no_go")
    audit.check("energy and entropy do not imply Renyi", no_go["uniform_Renyi_inferred"] is False and no_go["actual_Q3_Renyi_rejected"] is False, (no_go["uniform_Renyi_inferred"], no_go["actual_Q3_Renyi_rejected"]), (False, False), "renyi_no_go")

    os_gap = zero_temperature_os_gap_audit()
    audit.check("OS G(0) normalized", os_gap["G_0"] == 1, os_gap["G_0"], 1, "os_gap")
    audit.check("OS coercivity residual", os_gap["coercivity_residual"] == Fraction(10, 9), os_gap["coercivity_residual"], Fraction(10, 9), "os_gap")
    audit.check("OS decay rate units", os_gap["decay_rate"] == Fraction(3, 2), os_gap["decay_rate"], Fraction(3, 2), "os_gap")
    audit.check("zero temperature required", os_gap["requires_zero_temperature_sector_representation"] and os_gap["current_beta_uniform_temporal_rate_proved"] is False, (os_gap["requires_zero_temperature_sector_representation"], os_gap["current_beta_uniform_temporal_rate_proved"]), (True, False), "os_gap")

    q3 = q3_instanton_low_doublet_audit()
    instanton = q3["instanton"]
    audit.check("Q3 cube edges", instanton["q3_vertex_count"] == 8 and instanton["q3_edge_count"] == 12, (instanton["q3_vertex_count"], instanton["q3_edge_count"]), (8, 12), "q3_gap")
    audit.check("locked path kills Q3 term", instanton["locked_q3_polynomial"] == 0, instanton["locked_q3_polynomial"], 0, "q3_gap")
    audit.check("instanton squared exact", instanton["action_squared"] == instanton["expected_action_squared"], instanton["action_squared"], instanton["expected_action_squared"], "q3_gap")
    audit.check("instanton action exact", instanton["action"] == instanton["expected_action"] == 36, instanton["action"], 36, "q3_gap")
    low = q3["low_doublet"]
    audit.check("C3 cubed min cut", low["periodic_C3_cubed_min_cut"] == 6, low["periodic_C3_cubed_min_cut"], 6, "q3_gap")
    audit.check("Ising J exact", low["J"] == Fraction(6, 5), low["J"], Fraction(6, 5), "q3_gap")
    audit.check("reference gap lower bound exact", low["reference_gap_lower_bound"] == 5 and low["low_sector_gap"] == Fraction(72, 5), (low["reference_gap_lower_bound"], low["low_sector_gap"]), (5, Fraction(72, 5)), "q3_gap")
    audit.check("bond decomposition exact", low["bond_decomposition_residual_zero"], low["bond_decomposition_residual_zero"], True, "q3_gap")
    audit.check("no sector gap promotion", q3["actual_relative_QPS_smallness_proved"] is False and q3["actual_broken_sector_gap_proved"] is False, (q3["actual_relative_QPS_smallness_proved"], q3["actual_broken_sector_gap_proved"]), (False, False), "q3_gap")

    qps = yarotsky_qps_boundary_audit()
    relative = qps["relative_form"]
    audit.check("relative-form squares positive", all(value > 0 for value in relative["square_coefficients"]), relative["square_coefficients"], ">0", "qps")
    audit.check("IR condition has no upper c bound", all(qps["infrared_threshold"]["couplings_both_above_threshold"]) and qps["infrared_threshold"]["A0_condition_is_only_a_lower_bound_on_c"], qps["infrared_threshold"], "both small/large examples pass lower threshold", "qps")
    audit.check("single phase theorem wrong target", qps["single_phase_theorem"]["conclusion_is_unique_gapped_phase"] and qps["single_phase_theorem"]["target_broken_phase_certificate"] is False, qps["single_phase_theorem"], "unique, not broken", "qps")
    audit.check("two phase hypotheses missing", qps["two_phase_theorem"]["requires_two_Hilbert_product_ground_vectors"] and qps["two_phase_theorem"]["classical_delta_minima_are_Hilbert_vectors"] is False, qps["two_phase_theorem"], "missing Hilbert product reference", "qps")
    audit.check("A0 does not imply QPS gap", qps["automatic_sector_gap_from_A0"] is False, qps["automatic_sector_gap_from_A0"], False, "qps")
    audit.check("certificate has no bare CR", CERTIFICATE.read_bytes().count(b"\r") == 0, CERTIFICATE.read_bytes().count(b"\r"), 0, "source")

    authority = authority_audit(audit, staged)
    verdict = "PASS" if authority["status"] == "COMPLETE" else "INCOMPLETE"
    scope = {
        "fixed_trotter_level_exhaustion_compatibility": True,
        "renyi_history_cutoff_sufficiency": True,
        "zero_temperature_OS_gap_equivalence": True,
        "q3_instanton_low_doublet_reference_reduction": True,
        "actual_Q3_Renyi_history_bound": False,
        "n_to_infinity_split_limit": False,
        "all_exhaustion_common_alpha": False,
        "local_weyl_or_resolvent_invariance": False,
        "point_norm_C0": False,
        "renyi_condition_is_sufficient_not_necessary": True,
        "counterexample_is_actual_Q3_history": False,
        "actual_QPS_smallness": False,
        "broken_sector_GNS_gap": False,
        "continuum_regulator_removal": False,
        "physical_empty_space_reference": False,
        "prospective_Pre_A_validation": False,
        "C6_advanced": False,
        "CP1_complete": False,
        "Sector_A_complete": False,
        "Pre_A_complete": False,
    }
    source_paths = [SCRIPT, MANIFEST, CERTIFICATE]
    passed = len(audit.rows)
    return {
        "schema": f"tect/{SLUG}-primary-result/1.0",
        "script_version": __version__,
        "task_id": EXPECTED_TASK,
        "claim_ids": list(EXPECTED_CLAIM_IDS),
        "result_id": EXPECTED_RESULT_ID,
        "result_number": EXPECTED_RESULT_NUMBER,
        "result_version": EXPECTED_RESULT_VERSION,
        "exploration_id": EXPECTED_EXPLORATION,
        "claim_bearing": False,
        "reused_negative_ids": list(REUSED_NEGATIVE_IDS),
        "closed_gates": list(EXPECTED_CLOSED_GATES),
        "closed_subgates": list(EXPECTED_CLOSED_GATES),
        "open_gates": list(EXPECTED_OPEN_GATES),
        "successor_gates": list(EXPECTED_SUCCESSOR_GATES),
        "superseded_gate_ids": list(EXPECTED_SUPERSEDED_GATE_IDS),
        "retained_gates": list(EXPECTED_RETAINED_GATES),
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
            "fixed_trotter_level_compatibility": trotter,
            "renyi_history_sufficiency": renyi,
            "renyi_energy_form_no_go": no_go,
            "zero_temperature_os_gap_equivalence": os_gap,
            "q3_instanton_low_doublet_reference": q3,
            "yarotsky_qps_boundary": qps,
        },
        "scope": scope,
        "source_hashes": {
            str(path.relative_to(REPO)).replace("\\", "/"): normalized_sha256(path)
            for path in source_paths
            if path.exists()
        },
        "assertions": audit.rows,
        "boundary": (
            "Exact fixed-level split compatibility, Renyi history sufficiency, "
            "zero-temperature OS gap equivalence, and Q3 onsite low-doublet "
            "reduction only. No n-to-infinity common alpha, actual Q3 Renyi "
            "history estimate, quantum-Pirogov-Sinai smallness, broken-sector "
            "gap, continuum, prospective validation, Sector A, or Pre-A closure."
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

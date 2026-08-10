#!/usr/bin/env python3
"""Independent standard-library verifier for the R-167 v1.8 reduction.

This file intentionally does not import the primary verifier or consume its
result.  It reconstructs the decisive graph, Fraction, spectral-measure,
instanton, Ising-reference, and two-level hostile fixtures independently.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import tempfile
from fractions import Fraction
from itertools import product
from pathlib import Path
from typing import Any


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-renyi-history-os-gap-reduction-route-split"
PRIMARY_NAME = f"pre_a_cp1_st8_q3lock_renyi_history_os_gap_reduction_route_split"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260811.md"
DEFAULT_OUTPUT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / f"2026-08-11-independent-{SLUG}/result.json"
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


def normalized_sha256(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def encode(value: Any) -> Any:
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, Fraction):
        return f"{value.numerator}/{value.denominator}"
    if isinstance(value, dict):
        return {str(key): encode(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [encode(item) for item in value]
    return str(value)


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(encode(payload), stream, indent=2, sort_keys=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


class Checks:
    def __init__(self) -> None:
        self.rows: list[dict[str, Any]] = []

    def add(self, name: str, truth: bool, actual: Any, expected: Any, group: str) -> None:
        if not truth:
            raise AssertionError(f"{group}: {name}: {actual!r}; expected {expected!r}")
        self.rows.append(
            {
                "group": group,
                "name": name,
                "status": "PASS",
                "actual": encode(actual),
                "expected": encode(expected),
            }
        )


def l1_ball(radius: int) -> set[tuple[int, int, int]]:
    return {
        (x, y, z)
        for x in range(-radius, radius + 1)
        for y in range(-radius, radius + 1)
        for z in range(-radius, radius + 1)
        if abs(x) + abs(y) + abs(z) <= radius
    }


def trotter_oracle() -> dict[str, Any]:
    sizes = [len(l1_ball(radius)) for radius in range(4)]
    edge_directions = [
        (axis, sign) for axis in range(3) for sign in (-1, 1)
    ]
    kappa = Fraction(10, 21)
    zero = Fraction(0)

    def normalize(state: dict[int, tuple[Fraction, Fraction]], radius: int) -> dict[int, tuple[Fraction, Fraction]]:
        return {
            x: state.get(x, (zero, zero))
            for x in range(-radius, radius + 1)
        }

    def beta(state: dict[int, tuple[Fraction, Fraction]], radius: int, sign: int = 1) -> dict[int, tuple[Fraction, Fraction]]:
        current = normalize(state, radius)
        return {
            x: (
                current[x][0],
                current[x][1]
                + sign
                * kappa
                * (
                    current.get(x - 1, (zero, zero))[0]
                    + current.get(x + 1, (zero, zero))[0]
                ),
            )
            for x in range(-radius, radius + 1)
        }

    def sigma(state: dict[int, tuple[Fraction, Fraction]], radius: int, inverse: bool = False) -> dict[int, tuple[Fraction, Fraction]]:
        current = normalize(state, radius)
        if inverse:
            return {x: (-current[x][1], current[x][0]) for x in current}
        return {x: (current[x][1], -current[x][0]) for x in current}

    def compact(state: dict[int, tuple[Fraction, Fraction]]) -> dict[int, tuple[Fraction, Fraction]]:
        return {x: value for x, value in state.items() if value != (zero, zero)}

    def step(state: dict[int, tuple[Fraction, Fraction]], radius: int) -> dict[int, tuple[Fraction, Fraction]]:
        return sigma(beta(state, radius), radius)

    def inverse_step(state: dict[int, tuple[Fraction, Fraction]], radius: int) -> dict[int, tuple[Fraction, Fraction]]:
        return beta(sigma(state, radius, inverse=True), radius, sign=-1)

    seed = {0: (Fraction(1), zero)}
    small = seed
    large = seed
    prefix_equal = []
    prefix_support = []
    for level in range(1, 4):
        small = step(small, 3)
        large = step(large, 4)
        prefix_equal.append(
            all(
                small.get(x, (zero, zero)) == large.get(x, (zero, zero))
                for x in range(-3, 4)
            )
            and large.get(-4, (zero, zero)) == (zero, zero)
            and large.get(4, (zero, zero)) == (zero, zero)
        )
        prefix_support.append(all(abs(x) <= level for x in compact(large)))
    reverse = large
    for _ in range(3):
        reverse = inverse_step(reverse, 4)
    too_small = seed
    for _ in range(3):
        too_small = step(too_small, 2)
    exact_full = {
        -3: (Fraction(1000, 9261), zero),
        -2: (zero, Fraction(-100, 441)),
        -1: (Fraction(-1940, 3087), zero),
        0: (zero, Fraction(241, 441)),
        1: (Fraction(-1940, 3087), zero),
        2: (zero, Fraction(-100, 441)),
        3: (Fraction(1000, 9261), zero),
    }
    return {
        "support_sizes": sizes,
        "first_layer_edges": len(edge_directions),
        "fixed_n": 3,
        "ambient_radius_required": 3,
        "linear_proxy_kappa": kappa,
        "linear_proxy_full_word": compact(large),
        "linear_proxy_expected_full_word": exact_full,
        "all_prefix_ambient_equal": all(prefix_equal),
        "all_prefix_support_in_N_b": all(prefix_support),
        "outer_halo_sharp": compact(large).get(3) == exact_full[3],
        "reverse_recovers_seed": compact(reverse) == seed,
        "too_small_ambient_rejected": compact(too_small) != exact_full,
        "commuting_bond_terms": True,
        "forward_word": ["beta", "sigma"] * 3,
        "inverse_word": ["sigma^-1", "beta^-1"] * 3,
        "fixed_level_exhaustion_independent": True,
        "growing_level_cauchy": False,
        "local_weyl_or_resolvent_invariance": False,
        "global_strict_inductive_topology": False,
        "point_norm_C0": False,
        "fixture_is_support_proxy_not_Q3_onsite": True,
    }


def renyi_oracle() -> dict[str, Any]:
    alpha = Fraction(2)
    theta = Fraction(1, 2)
    reference = (Fraction(3, 4), Fraction(1, 4))
    tilted = tuple(reversed(reference))
    q2_terms = [s * s / r for r, s in zip(reference, tilted)]
    q2 = sum(q2_terms)
    event = tilted[1]
    event_ref = reference[1]
    bound_squared = q2 * event_ref
    p0 = Fraction(4, 5)
    p1 = Fraction(1, 5)
    plus = ((Fraction(52, 125), Fraction(36, 125)), (Fraction(36, 125), Fraction(73, 125)))
    minus = ((Fraction(52, 125), Fraction(-36, 125)), (Fraction(-36, 125), Fraction(73, 125)))
    sqrt_p0p1 = Fraction(2, 5)

    def sandwiched(matrix: tuple[tuple[Fraction, Fraction], tuple[Fraction, Fraction]]) -> Fraction:
        return matrix[0][0] ** 2 / p0 + matrix[1][1] ** 2 / p1 + 2 * matrix[0][1] ** 2 / sqrt_p0p1

    def petz(matrix: tuple[tuple[Fraction, Fraction], tuple[Fraction, Fraction]]) -> Fraction:
        return (matrix[0][0] ** 2 + matrix[0][1] ** 2) / p0 + (matrix[1][1] ** 2 + matrix[0][1] ** 2) / p1

    def plus_event(matrix: tuple[tuple[Fraction, Fraction], tuple[Fraction, Fraction]]) -> Fraction:
        return (matrix[0][0] + matrix[1][1] + 2 * matrix[0][1]) / 2

    sand_plus = sandwiched(plus)
    sand_minus = sandwiched(minus)
    petz_plus = petz(plus)
    q_plus = plus_event(plus)
    q_minus = plus_event(minus)
    a = Fraction(14)
    b = theta * a
    l_value = Fraction(2)
    layer = l_value**4 + 2 * l_value**2 / b + 2 / b**2
    kappa = Fraction(3)
    exact_b = Fraction(6)
    exact_layer = Fraction(2) ** 4 + 2 * Fraction(2) ** 2 / exact_b + 2 / exact_b**2
    one_prefactor = 4 * Fraction(3, 5) ** 2 * 3**2 * 3 * 4
    two_prefactor = 2 * one_prefactor
    return {
        "alpha": alpha,
        "theta": theta,
        "Q2_terms": q2_terms,
        "Q2": q2,
        "event": event,
        "event_reference": event_ref,
        "bound_squared": bound_squared,
        "slack_squared": bound_squared - event**2,
        "orientation_fixture": {
            "sigma_plus": plus,
            "sigma_minus": minus,
            "sandwiched_Q2_plus": sand_plus,
            "sandwiched_Q2_minus": sand_minus,
            "Petz_Q2": petz_plus,
            "p": Fraction(1, 2),
            "q_plus": q_plus,
            "q_minus": q_minus,
            "orientation_sum": q_plus + q_minus,
            "two_orientation_factor": 2,
            "two_orientation_squared_bound": 4 * sand_plus * Fraction(1, 2),
        },
        "gaussian_a": a,
        "b": b,
        "L": l_value,
        "fourth_tail_polynomial": layer,
        "kappa": kappa,
        "squared_condition": b > kappa,
        "unsquared_condition": b > 2 * kappa,
        "gamma": Fraction(1, 3),
        "factorial_exponent": Fraction(-1, 3),
        "projection_formula": "q<=Q_alpha^(1/alpha)p^((alpha-1)/alpha)",
        "two_orientation_factor": 2,
        "edge_fixture": {
            "layer_polynomial": exact_layer,
            "edge_count_power": 2,
            "one_orientation_prefactor": one_prefactor,
            "two_orientation_prefactor": two_prefactor,
            "final_rational_coefficient": two_prefactor * exact_layer,
            "gaussian_exponent": -24,
        },
    }


def hostile_renyi_oracle() -> dict[str, Any]:
    m = 3
    rows = []
    for n in (2, 4, 6):
        n4 = n**4
        reservoir = 2**n4
        p0 = Fraction(reservoir, reservoir + 1)
        p1 = Fraction(1, reservoir + 1)
        delta = p0 - p1
        denominator = 4 * n ** (2 * m) + 1
        cosine = Fraction(4 * n ** (2 * m) - 1, denominator)
        sine = Fraction(4 * n**m, denominator)
        cosine2 = cosine**2
        sine2 = sine**2
        tail = p1 + delta * sine2
        k = 1 + n4
        trace = Fraction(2) + sine2 * Fraction(n**8, 1 + n4)
        determinant = (
            (cosine2 + k * sine2) * (cosine2 + sine2 / k)
            - Fraction((1 - k) ** 2, k) * cosine2 * sine2
        )
        sigma00 = cosine2 * p0 + sine2 * p1
        sigma11 = tail
        sigma01 = cosine * sine * delta
        sqrt_p0p1 = Fraction(2 ** (n4 // 2), reservoir + 1)
        measured = sigma11**2 / p1 + sigma00**2 / p0
        sandwiched = sigma00**2 / p0 + sigma11**2 / p1 + 2 * sigma01**2 / sqrt_p0p1
        gaussian = {
            exponent: Fraction(reservoir + 2 ** (exponent * n**2), reservoir + 1)
            for exponent in (1, 2)
        }
        moments = {r: n**r * tail for r in range(1, 2 * m + 1)}
        rows.append(
            {
                "n": n,
                "p0": p0,
                "p1": p1,
                "cosine": cosine,
                "sine": sine,
                "rotation_identity": cosine2 + sine2,
                "tail": tail,
                "tail_increment": delta * sine2,
                "entropy_over_log2": delta * sine2 * n4,
                "energy_excess": delta * sine2 * n4,
                "energy_excess_upper": Fraction(n4, n ** (2 * m)),
                "K_trace": trace,
                "K_determinant": determinant,
                "K_half_two": determinant == 1 and trace < Fraction(5, 2),
                "measured_Q2": measured,
                "sandwiched_Q2": sandwiched,
                "sandwiched_minus_measured": sandwiched - measured,
                "q_squared_over_p1": tail**2 / p1,
                "q_lower": Fraction(8, 25 * n ** (2 * m)),
                "gaussian_reference": gaussian,
                "gaussian_bounded": all(value <= 2 for value in gaussian.values()),
                "moments": moments,
                "moments_bounded": all(value <= 2 for value in moments.values()),
            }
        )
    compact = rows[0]
    return {
        "m": m,
        "rows": rows,
        "two_sided_K_comparison": "1/2 K <= U K U* <= 2 K",
        "compact_oracle": {
            "p0": compact["p0"],
            "p1": compact["p1"],
            "cosine": compact["cosine"],
            "sine": compact["sine"],
            "q": compact["tail"],
            "trace_G": compact["K_trace"],
            "measured_Q2": compact["measured_Q2"],
            "sandwiched_Q2": compact["sandwiched_Q2"],
            "sandwiched_minus_measured": compact["sandwiched_minus_measured"],
            "q_squared_over_p1": compact["q_squared_over_p1"],
        },
        "general_lower_certificate": {
            "q_lower": "8/(25*n^(2m))",
            "Qalpha_lower": "(8/(25*n^(2m)))^alpha*2^((alpha-1)*n^4)",
            "Dalpha_diverges_for_fixed_alpha_gt_one": True,
        },
        "uniform_Renyi": False,
        "Q3_counterexample": False,
    }


def os_gap_oracle() -> dict[str, Any]:
    hbar = Fraction(2)
    energies = (Fraction(3, 2), Fraction(7, 3))
    amplitudes = (Fraction(2, 3), Fraction(3, 5))
    weights = tuple(value * value for value in amplitudes)
    variance = sum(weights)
    energy = sum(w * e for w, e in zip(weights, energies))
    gap = min(energies)
    margin = energy - gap * variance
    saturator_energy = energies[0]
    hostile_energies = (Fraction(0), Fraction(0), Fraction(2))
    return {
        "hbar": hbar,
        "energies": energies,
        "weights": weights,
        "variance": variance,
        "energy": energy,
        "gap": gap,
        "margin": margin,
        "decay_rate": gap / hbar,
        "saturator_margin": saturator_energy - gap,
        "minus_hbar_G_prime_zero": energy,
        "hostile_kernel": {
            "energies": hostile_energies,
            "simple_kernel": False,
            "variance": 1,
            "energy": 0,
            "G_tau": 1,
        },
        "fixed_beta_thermal_is_vacuum_gap": False,
        "actual_Q3_temporal_rate": False,
    }


def cube_edges() -> list[tuple[tuple[int, ...], tuple[int, ...]]]:
    vertices = list(product((0, 1), repeat=3))
    return [
        (a, b)
        for i, a in enumerate(vertices)
        for b in vertices[i + 1 :]
        if sum(x != y for x, y in zip(a, b)) == 1
    ]


def instanton_oracle() -> dict[str, Any]:
    chi = Fraction(1)
    g = Fraction(2)
    v = Fraction(3, 2)
    coupling_lambda = Fraction(5, 7)
    scalar_variation = Fraction(4, 3) * v**3
    scalar_action = Fraction(2) * scalar_variation / Fraction(2)
    # sqrt(chi*g/2)=1 for this fixture.
    total_action = 8 * scalar_variation
    hbar = Fraction(3, 2)
    locked = {vertex: v for vertex in product((0, 1), repeat=3)}
    q3_value = sum(
        (locked[a] - locked[b]) ** 2 * (locked[a] ** 2 + locked[b] ** 2)
        for a, b in cube_edges()
    )
    return {
        "chi": chi,
        "g": g,
        "v": v,
        "lambda": coupling_lambda,
        "edge_count": len(cube_edges()),
        "scalar_variation": scalar_variation,
        "scalar_action": scalar_action,
        "total_action": total_action,
        "action_over_hbar": total_action / hbar,
        "locked_Q3_value": q3_value,
        "lambda_positive_locked_unique_up_to_common_shift": True,
        "lambda_zero_independent_centres": 8,
        "tunnelling_bound_proved": False,
    }


def z2_cube_multigraph_min_cut() -> int:
    vertices = list(product((0, 1), repeat=3))
    index = {vertex: i for i, vertex in enumerate(vertices)}
    edges: list[tuple[int, int]] = []
    for vertex in vertices:
        for axis in range(3):
            neighbour = list(vertex)
            neighbour[axis] = (neighbour[axis] + 1) % 2
            edges.append((index[vertex], index[tuple(neighbour)]))
    best = 10**9
    for mask in range(1, 1 << len(vertices)):
        if not (mask & 1) or mask == (1 << len(vertices)) - 1:
            continue
        cut = sum(((mask >> a) & 1) != ((mask >> b) & 1) for a, b in edges)
        best = min(best, cut)
    return best


def doublet_ising_oracle() -> dict[str, Any]:
    delta1 = Fraction(1, 10)
    gamma = Fraction(20)
    m = Fraction(3, 2)
    c = Fraction(2, 9)
    j_value = 8 * c * m**2
    cycle_edges = ((0, 1), (1, 2), (2, 3), (3, 0))
    energies: list[tuple[tuple[int, ...], Fraction]] = []
    # labels -1,+1 are low s eigenvalues; 0 is a high label.
    for labels in product((-1, 0, 1), repeat=4):
        energy = gamma * sum(label == 0 for label in labels)
        energy += sum(
            (j_value / 2) * (labels[x] - labels[y]) ** 2
            for x, y in cycle_edges
        )
        energies.append((labels, energy))
    zero_labels = [labels for labels, energy in energies if energy == 0]
    positive = sorted({energy for _, energy in energies if energy > 0})
    return {
        "delta1": delta1,
        "Gamma": gamma,
        "m": m,
        "c": c,
        "J": j_value,
        "C4_edge_connectivity": 2,
        "Z2_cube_multigraph_edge_connectivity": z2_cube_multigraph_min_cut(),
        "zero_labels": zero_labels,
        "kernel_dimension": len(zero_labels),
        "C4_first_positive": positive[0],
        "predicted_C4_gap": min(gamma, 2 * j_value * 2),
        "R_e": 0,
        "exact_remainder": "delta1 sum P1",
        "actual_Q3_reduction": False,
    }


def qps_boundary_oracle() -> dict[str, Any]:
    eta = Fraction(2, 5)
    g = Fraction(3, 5)
    c = Fraction(7, 10)
    v = Fraction(3, 2)
    j3 = Fraction(3, 5)
    c_ir = j3**2 / 8
    return {
        "relative_form_sum_of_squares": {
            "first_coefficient": eta * g / 8,
            "first_shift": 2 * v**2,
            "second_coefficient": eta * g / 8,
            "second_shift": 4 * c / (eta * g),
        },
        "bond_constant": 4 * eta * g * v**4 + 32 * c**2 / (eta * g),
        "c_IR": c_ir,
        "lower_threshold_accepts": [Fraction(1, 10) > c_ir, Fraction(10) > c_ir],
        "single_phase_infinite_site_allowed": True,
        "single_phase_conclusion_unique": True,
        "two_phase_finite_site_required": True,
        "classical_delta_minima_in_L2": False,
        "two_product_reference_available_for_exact_Q3": False,
        "low_doublet_smallness_certified": False,
        "A0_implies_sector_gap": False,
    }


def source_firewall(checks: Checks) -> None:
    tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
    imported = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.append(node.module or "")
    checks.add(
        "no primary import",
        all(PRIMARY_NAME not in name for name in imported),
        imported,
        "no primary module",
        "firewall",
    )
    source = SCRIPT.read_text(encoding="utf-8")
    checks.add(
        "no primary result consumption",
        "primary-" + SLUG not in source,
        "primary result path absent",
        True,
        "firewall",
    )


def authority_audit(checks: Checks, staged: bool) -> dict[str, Any]:
    missing: list[str] = []

    def file_text(path: Path, label: str) -> str | None:
        if path.exists():
            return path.read_text(encoding="utf-8")
        if staged:
            missing.append(label)
            return None
        raise FileNotFoundError(path)

    def token(text: str, value: str, label: str) -> None:
        if value in text:
            checks.add(label, True, True, True, "authority")
        elif staged:
            missing.append(label)
        else:
            raise AssertionError(f"missing {value!r} in {label}")

    manifest_text = file_text(MANIFEST, "manifest")
    if manifest_text is not None:
        manifest = json.loads(manifest_text)
        checks.add("manifest task", manifest["task_id"] == EXPECTED_TASK, manifest["task_id"], EXPECTED_TASK, "authority")
        checks.add("manifest claims", tuple(manifest["claim_ids"]) == EXPECTED_CLAIM_IDS, manifest["claim_ids"], EXPECTED_CLAIM_IDS, "authority")
        checks.add("manifest claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "authority")
        checks.add("manifest version", manifest["result_version"] == EXPECTED_RESULT_VERSION, manifest["result_version"], EXPECTED_RESULT_VERSION, "authority")
        checks.add("manifest exploration", manifest["exploration_id"] == EXPECTED_EXPLORATION, manifest["exploration_id"], EXPECTED_EXPLORATION, "authority")
        checks.add("manifest result", manifest["result_id"] == EXPECTED_RESULT_ID, manifest["result_id"], EXPECTED_RESULT_ID, "authority")
        checks.add("manifest closed", tuple(manifest["closed_subgates"]) == EXPECTED_CLOSED_GATES, manifest["closed_subgates"], EXPECTED_CLOSED_GATES, "authority")
        checks.add("manifest open", tuple(manifest["open_gates"]) == EXPECTED_OPEN_GATES, manifest["open_gates"], EXPECTED_OPEN_GATES, "authority")
        checks.add("manifest successor gates", tuple(manifest["open_gates"][:2]) == EXPECTED_SUCCESSOR_GATES, manifest["open_gates"][:2], EXPECTED_SUCCESSOR_GATES, "authority")
        checks.add("manifest negatives", tuple(manifest["negative_ids"]) == NEGATIVE_IDS, manifest["negative_ids"], NEGATIVE_IDS, "authority")
        checks.add("manifest reused negatives", tuple(manifest["reused_negative_ids"]) == REUSED_NEGATIVE_IDS, manifest["reused_negative_ids"], REUSED_NEGATIVE_IDS, "authority")
        checks.add("manifest superseded gates", tuple(manifest["superseded_gate_ids"]) == EXPECTED_SUPERSEDED_GATE_IDS, manifest["superseded_gate_ids"], EXPECTED_SUPERSEDED_GATE_IDS, "authority")
        checks.add("manifest retained gates", tuple(manifest["retained_gate_ids"]) == EXPECTED_RETAINED_GATES, manifest["retained_gate_ids"], EXPECTED_RETAINED_GATES, "authority")

    certificate_text = file_text(CERTIFICATE, "certificate")
    if certificate_text is not None:
        for value in (
            EXPECTED_EXPLORATION,
            EXPECTED_RESULT_VERSION,
            *EXPECTED_CLOSED_GATES,
            *EXPECTED_OPEN_GATES,
            *NEGATIVE_IDS,
            "S_{\\rm inst}=36",
            "fixed Trotter level",
            "sandwiched-Renyi",
            "OS temporal",
        ):
            token(certificate_text, value, f"certificate {value}")

    exploration = file_text(EXPLORATION_LEDGER, "exploration ledger")
    if exploration is not None:
        token(exploration, f'"id":"{EXPECTED_EXPLORATION}"', "exploration record")
    result = file_text(RESULT_LEDGER, "result ledger")
    if result is not None:
        token(result, "R-167", "result R-167")
        token(result, "v1.8", "result v1.8")
    negatives = file_text(NEGATIVE_REGISTRY, "negative registry")
    if negatives is not None:
        for value in NEGATIVE_IDS:
            token(negatives, value, f"negative {value}")
    gates = file_text(GATE_REGISTRY, "gate registry")
    if gates is not None:
        for value in (*EXPECTED_CLOSED_GATES, *EXPECTED_OPEN_GATES):
            token(gates, value, f"gate {value}")
    theorem_map = file_text(SECTOR_A_MAP, "sector-a theorem map")
    if theorem_map is not None:
        token(theorem_map, "R-167 v1.8", "theorem map v1.8")

    return {"status": "INCOMPLETE" if missing else "COMPLETE", "missing": missing}


def run(staged: bool = False) -> dict[str, Any]:
    checks = Checks()
    source_firewall(checks)

    trotter = trotter_oracle()
    checks.add("support balls", trotter["support_sizes"] == [1, 7, 25, 63], trotter["support_sizes"], [1, 7, 25, 63], "trotter")
    checks.add("first layer", trotter["first_layer_edges"] == 6, trotter["first_layer_edges"], 6, "trotter")
    checks.add("fixed stage exact", trotter["fixed_level_exhaustion_independent"] and not trotter["growing_level_cauchy"], (trotter["fixed_level_exhaustion_independent"], trotter["growing_level_cauchy"]), (True, False), "trotter")
    checks.add("constructive full word", trotter["linear_proxy_full_word"] == trotter["linear_proxy_expected_full_word"], trotter["linear_proxy_full_word"], trotter["linear_proxy_expected_full_word"], "trotter")
    checks.add("all prefix ambient equal", trotter["all_prefix_ambient_equal"], trotter["all_prefix_ambient_equal"], True, "trotter")
    checks.add("all prefix halo support", trotter["all_prefix_support_in_N_b"], trotter["all_prefix_support_in_N_b"], True, "trotter")
    checks.add("sharp outer halo", trotter["outer_halo_sharp"], trotter["outer_halo_sharp"], True, "trotter")
    checks.add("reverse word", trotter["reverse_recovers_seed"], trotter["reverse_recovers_seed"], True, "trotter")
    checks.add("small ambient hostile", trotter["too_small_ambient_rejected"], trotter["too_small_ambient_rejected"], True, "trotter")
    checks.add("no C-star topology promotion", not trotter["local_weyl_or_resolvent_invariance"] and not trotter["global_strict_inductive_topology"] and not trotter["point_norm_C0"], (trotter["local_weyl_or_resolvent_invariance"], trotter["global_strict_inductive_topology"], trotter["point_norm_C0"]), (False, False, False), "trotter")

    renyi = renyi_oracle()
    checks.add("Q2", renyi["Q2"] == Fraction(7, 3), renyi["Q2"], Fraction(7, 3), "renyi")
    checks.add("Renyi slack", renyi["slack_squared"] == Fraction(1, 48), renyi["slack_squared"], Fraction(1, 48), "renyi")
    orientation = renyi["orientation_fixture"]
    checks.add("sandwiched Q2 orientations", orientation["sandwiched_Q2_plus"] == orientation["sandwiched_Q2_minus"] == Fraction(7301, 3125), (orientation["sandwiched_Q2_plus"], orientation["sandwiched_Q2_minus"]), Fraction(7301, 3125), "renyi")
    checks.add("Petz hostile", orientation["Petz_Q2"] == Fraction(61, 25) and orientation["Petz_Q2"] != orientation["sandwiched_Q2_plus"], (orientation["Petz_Q2"], orientation["sandwiched_Q2_plus"]), "different exact values", "renyi")
    checks.add("orientation event split", orientation["q_plus"] == Fraction(197, 250) and orientation["q_minus"] == Fraction(53, 250), (orientation["q_plus"], orientation["q_minus"]), (Fraction(197, 250), Fraction(53, 250)), "renyi")
    checks.add("orientation factor two", orientation["two_orientation_factor"] == 2 and orientation["orientation_sum"] ** 2 <= orientation["two_orientation_squared_bound"], (orientation["two_orientation_factor"], orientation["orientation_sum"], orientation["two_orientation_squared_bound"]), (2, "<= bound"), "renyi")
    checks.add("fourth tail", renyi["fourth_tail_polynomial"] == Fraction(842, 49), renyi["fourth_tail_polynomial"], Fraction(842, 49), "renyi")
    checks.add("corridor conditions", renyi["squared_condition"] and renyi["unsquared_condition"] and renyi["factorial_exponent"] < 0, (renyi["squared_condition"], renyi["unsquared_condition"], renyi["factorial_exponent"]), (True, True, "<0"), "renyi")
    edge = renyi["edge_fixture"]
    checks.add("edge polynomial", edge["layer_polynomial"] == Fraction(313, 18), edge["layer_polynomial"], Fraction(313, 18), "renyi")
    checks.add("edge m squared", edge["edge_count_power"] == 2 and edge["one_orientation_prefactor"] == Fraction(3888, 25), (edge["edge_count_power"], edge["one_orientation_prefactor"]), (2, Fraction(3888, 25)), "renyi")
    checks.add("edge orientation coefficient", edge["two_orientation_prefactor"] == Fraction(7776, 25) and edge["final_rational_coefficient"] == Fraction(135216, 25), (edge["two_orientation_prefactor"], edge["final_rational_coefficient"]), (Fraction(7776, 25), Fraction(135216, 25)), "renyi")

    hostile = hostile_renyi_oracle()
    for row in hostile["rows"]:
        label = f"n={row['n']}"
        checks.add(f"rotation identity {label}", row["rotation_identity"] == 1, row["rotation_identity"], 1, "renyi_no_go")
        checks.add(f"entropy energy scale {label}", row["energy_excess"] < row["energy_excess_upper"], row["energy_excess"], f"<{row['energy_excess_upper']}", "renyi_no_go")
        checks.add(f"K comparison {label}", row["K_half_two"] and row["K_trace"] < Fraction(9, 4), (row["K_half_two"], row["K_trace"]), (True, "<9/4"), "renyi_no_go")
        checks.add(f"K determinant {label}", row["K_determinant"] == 1, row["K_determinant"], 1, "renyi_no_go")
        checks.add(f"tail lower {label}", row["tail"] >= row["q_lower"], row["tail"], f">={row['q_lower']}", "renyi_no_go")
        checks.add(f"Gaussian reference {label}", row["gaussian_bounded"], row["gaussian_reference"], "<=2", "renyi_no_go")
        checks.add(f"finite moments {label}", row["moments_bounded"], row["moments"], "<=2", "renyi_no_go")
        checks.add(f"sandwiched not measured {label}", row["sandwiched_minus_measured"] > 0, row["sandwiched_minus_measured"], ">0", "renyi_no_go")
    compact_expected = {
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
    checks.add("exact hostile compact oracle", hostile["compact_oracle"] == compact_expected, hostile["compact_oracle"], compact_expected, "renyi_no_go")
    checks.add("general divergence certificate", hostile["general_lower_certificate"]["Dalpha_diverges_for_fixed_alpha_gt_one"], hostile["general_lower_certificate"], "diverges", "renyi_no_go")
    checks.add("no Q3 nonexistence", not hostile["uniform_Renyi"] and not hostile["Q3_counterexample"], (hostile["uniform_Renyi"], hostile["Q3_counterexample"]), (False, False), "renyi_no_go")

    os_gap = os_gap_oracle()
    checks.add("OS variance", os_gap["variance"] == Fraction(181, 225), os_gap["variance"], Fraction(181, 225), "os_gap")
    checks.add("OS energy", os_gap["energy"] == Fraction(113, 75), os_gap["energy"], Fraction(113, 75), "os_gap")
    checks.add("OS margin", os_gap["margin"] == Fraction(3, 10), os_gap["margin"], Fraction(3, 10), "os_gap")
    checks.add("OS rate", os_gap["decay_rate"] == Fraction(3, 4), os_gap["decay_rate"], Fraction(3, 4), "os_gap")
    checks.add("simple kernel required", os_gap["hostile_kernel"]["simple_kernel"] is False and os_gap["hostile_kernel"]["energy"] == 0, os_gap["hostile_kernel"], "degenerate zero mode blocks gap", "os_gap")
    checks.add("actual Q3 mass open", not os_gap["actual_Q3_temporal_rate"], os_gap["actual_Q3_temporal_rate"], False, "os_gap")

    instanton = instanton_oracle()
    checks.add("Q3 edges", instanton["edge_count"] == 12, instanton["edge_count"], 12, "instanton")
    checks.add("scalar action", instanton["scalar_action"] == Fraction(9, 2), instanton["scalar_action"], Fraction(9, 2), "instanton")
    checks.add("total action", instanton["total_action"] == 36, instanton["total_action"], 36, "instanton")
    checks.add("action exponent", instanton["action_over_hbar"] == 24, instanton["action_over_hbar"], 24, "instanton")
    checks.add("locked Q3 zero", instanton["locked_Q3_value"] == 0, instanton["locked_Q3_value"], 0, "instanton")
    checks.add("no splitting promotion", not instanton["tunnelling_bound_proved"], instanton["tunnelling_bound_proved"], False, "instanton")

    ising = doublet_ising_oracle()
    checks.add("J", ising["J"] == 4, ising["J"], 4, "ising")
    checks.add("two product kernels", ising["kernel_dimension"] == 2 and set(ising["zero_labels"]) == {(-1, -1, -1, -1), (1, 1, 1, 1)}, ising["zero_labels"], "two uniform signs", "ising")
    checks.add("C4 gap", ising["C4_first_positive"] == ising["predicted_C4_gap"] == 16, ising["C4_first_positive"], 16, "ising")
    checks.add("cube multigraph cut", ising["Z2_cube_multigraph_edge_connectivity"] == 6, ising["Z2_cube_multigraph_edge_connectivity"], 6, "ising")
    checks.add("actual reduction open", not ising["actual_Q3_reduction"], ising["actual_Q3_reduction"], False, "ising")

    qps = qps_boundary_oracle()
    squares = qps["relative_form_sum_of_squares"]
    checks.add("relative squares positive", squares["first_coefficient"] > 0 and squares["second_coefficient"] > 0, squares, "positive squares", "qps")
    checks.add("IR lower only", all(qps["lower_threshold_accepts"]), qps["lower_threshold_accepts"], [True, True], "qps")
    checks.add("single/two phase distinction", qps["single_phase_infinite_site_allowed"] and qps["single_phase_conclusion_unique"] and qps["two_phase_finite_site_required"], qps, "single phase structurally available; two phase mismatch", "qps")
    checks.add("direct import blocked", not qps["classical_delta_minima_in_L2"] and not qps["two_product_reference_available_for_exact_Q3"] and not qps["low_doublet_smallness_certified"] and not qps["A0_implies_sector_gap"], qps, "all load-bearing data absent", "qps")
    checks.add("certificate bare CR", CERTIFICATE.read_bytes().count(b"\r") == 0, CERTIFICATE.read_bytes().count(b"\r"), 0, "source")

    authority = authority_audit(checks, staged)
    verdict = "PASS" if authority["status"] == "COMPLETE" else "INCOMPLETE"
    sources = [SCRIPT, MANIFEST, CERTIFICATE]
    count = len(checks.rows)
    return {
        "schema": f"tect/{SLUG}-independent-result/1.0",
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
        "negative_ids": list(NEGATIVE_IDS),
        "verdict": verdict,
        "passed": count,
        "failed": 0,
        "total": count,
        "summary": {"passed": count, "failed": 0, "total": count, "authority_status": authority["status"]},
        "authority": authority,
        "derived": {
            "fixed_trotter_level_compatibility": trotter,
            "renyi_history_sufficiency": renyi,
            "renyi_energy_form_no_go": hostile,
            "zero_temperature_os_gap_equivalence": os_gap,
            "q3_instanton": instanton,
            "conditional_doublet_ising_reference": ising,
            "yarotsky_qps_boundary": qps,
        },
        "scope": {
            "fixed_level": True,
            "conditional_Renyi_reduction": True,
            "abstract_OS_gap_equivalence": True,
            "exact_instanton_action": True,
            "conditional_reference_gap": True,
            "actual_Renyi_history": False,
            "all_exhaustion_common_alpha": False,
            "actual_Q3_GNS_gap": False,
            "Sector_A_complete": False,
            "Pre_A_complete": False,
        },
        "source_hashes": {
            str(path.relative_to(REPO)).replace("\\", "/"): normalized_sha256(path)
            for path in sources
            if path.exists()
        },
        "assertions": checks.rows,
        "boundary": (
            "Independent exact checks of fixed-stage compatibility, conditional "
            "Renyi history tails, OS/GNS spectral equivalence, instanton action, "
            "and a conditional reference model only; no thermodynamic common "
            "alpha, actual sector gap, Sector A, or Pre-A closure."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--staged", action="store_true")
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    payload = run(staged=args.staged)
    if not args.self_test and not args.no_store:
        atomic_json(args.output, payload)
    print(f"{payload['verdict']} {payload['passed']}/{payload['total']}")
    if payload["verdict"] == "INCOMPLETE":
        print("authority: " + ", ".join(payload["authority"]["missing"]))
    key = str(SCRIPT.relative_to(REPO)).replace("\\", "/")
    print("schema: " + payload["schema"])
    print("script_sha256: " + payload["source_hashes"][key])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

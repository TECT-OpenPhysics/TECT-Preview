#!/usr/bin/env python3
"""Primary verifier for the CL8 time-local RP/Feynman--Kac bridge split."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from itertools import product
from pathlib import Path
from typing import Any, Callable

import sympy as sp


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
SLUG = "pre-a-cp1-cl8-time-local-rp-feynman-kac-bridge-route-split"
CANDIDATE_ID = "PA-CP1-CL8-TIME-LOCAL-RP-FEYNMAN-KAC-BRIDGE-ROUTE-SPLIT-v0"
RESULT_ID = "PA-CP1-CL8-FIXED-REGULATOR-EXACT-HEAT-TRANSFER-REFLECTION-POSITIVITY-FEYNMAN-KAC-AND-STRANG-LIMIT-WITH-EXACT-SLICE-AND-CONE-NOGOS"
NEGATIVE_IDS = (
    "NG-2026-08-04-PRE-A-CP1-CL8-STRANG-ONE-SLICE-EXACT-HAMILTONIAN-SEMIGROUP",
    "NG-2026-08-04-PRE-A-CP1-CL8-EUCLIDEAN-HEAT-SUPPORT-PHYSICAL-LIGHT-CONE",
)
EXPLORATION_ID = "EXP-000768"
PARENT_IDS = (
    "PA-CP1-CL8-FINITE-QUANTUM-STATE-BOUNDARY-FORK-v0",
    "PA-CP1-CL8-Q3-VECTOR-PHI2-CONSTRUCTIVE-COMPARATOR-ROUTE-SPLIT-v0",
    "PA-C0A-RPTM-FS-v0",
)
SCHEMA = f"tect/{SLUG}-primary/0.1"
SCRIPT = Path(__file__).resolve()
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260804.md"
PARENTS = (
    REPO / "strategy/pre-a-cp1-cl8-finite-quantum-state-boundary-fork-manifest.json",
    REPO / "strategy/pre-a-cp1-cl8-q3-vector-phi2-constructive-comparator-route-split-manifest.json",
    REPO / "strategy/pre-a-c0a-reflection-positive-transfer-manifest.json",
)
STATUS = REPO / "claims/C6-SPACETIME-SIGNATURE/status.json"
DEFAULT_OUTPUT = REPO / f"claims/C6-SPACETIME-SIGNATURE/runs/2026-08-04-primary-{SLUG}/result.json"

# Explicit self-test oracles, not production inputs.
TEST_ORACLE_SITE_NUMERATOR = sp.Rational(6143, 1024)
TEST_ORACLE_LINK_NUMERATOR = sp.Rational(3753, 1024)
TEST_ORACLE_RING_Z = sp.Rational(257, 256)
TEST_ORACLE_CORRELATOR_NUMERATOR = sp.Rational(1703, 1024)


def sha256(path: Path) -> str:
    data = path.read_bytes().replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(data).hexdigest()


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=path.name + ".", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(payload, stream, indent=2, sort_keys=True)
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
            raise AssertionError(f"{group}: {name}: {actual!r} != {expected!r}")
        self.rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})


def cube_edges() -> list[tuple[int, int]]:
    nodes = list(product((0, 1), repeat=3))
    index = {node: position for position, node in enumerate(nodes)}
    edges: list[tuple[int, int]] = []
    for node in nodes:
        for axis in range(3):
            if node[axis] == 0:
                other = list(node)
                other[axis] = 1
                edges.append((index[node], index[tuple(other)]))
    return edges


def exp_jet(operator: Callable[[sp.Expr], sp.Expr], seed: sp.Expr, order: int) -> list[sp.Expr]:
    result: list[sp.Expr] = []
    current = sp.expand(seed)
    for degree in range(order + 1):
        if degree:
            current = sp.expand(operator(current))
        result.append(sp.expand(current / sp.factorial(degree)))
    return result


def compose_jet(operator: Callable[[sp.Expr], sp.Expr], incoming: list[sp.Expr], order: int) -> list[sp.Expr]:
    result = [sp.Integer(0) for _ in range(order + 1)]
    for source_degree, polynomial in enumerate(incoming):
        current = sp.expand(polynomial)
        for added_degree in range(order - source_degree + 1):
            if added_degree:
                current = sp.expand(operator(current))
            result[source_degree + added_degree] += current / sp.factorial(added_degree)
    return [sp.expand(value) for value in result]


def matrix_ring_weight(matrix: sp.Matrix, path: tuple[int, ...]) -> sp.Expr:
    return sp.prod(matrix[path[index], path[(index + 1) % len(path)]] for index in range(len(path)))


def build_payload() -> dict[str, Any]:
    audit = Audit()
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    parents = [json.loads(path.read_text(encoding="utf-8")) for path in PARENTS]
    status = json.loads(STATUS.read_text(encoding="utf-8"))
    certificate = CERTIFICATE.read_text(encoding="utf-8")

    audit.check("manifest schema", manifest["schema"].endswith("/0.1"), manifest["schema"], "*/0.1", "identity")
    audit.check("candidate id", manifest["candidate_id"] == CANDIDATE_ID, manifest["candidate_id"], CANDIDATE_ID, "identity")
    audit.check("result id", manifest["result_id"] == RESULT_ID, manifest["result_id"], RESULT_ID, "identity")
    audit.check("negative ids", tuple(manifest["negative_ids"]) == NEGATIVE_IDS, manifest["negative_ids"], NEGATIVE_IDS, "identity")
    audit.check("exploration id", manifest["exploration_id"] == EXPLORATION_ID, manifest["exploration_id"], EXPLORATION_ID, "identity")
    audit.check("parent ids", tuple(manifest["parent_ids"]) == PARENT_IDS, manifest["parent_ids"], PARENT_IDS, "identity")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "identity")
    audit.check("task id", manifest["task_id"] == "T-054", manifest["task_id"], "T-054", "identity")
    for index, (parent, parent_id) in enumerate(zip(parents, PARENT_IDS), start=1):
        audit.check(f"parent {index} resolved", parent["candidate_id"] == parent_id, parent["candidate_id"], parent_id, "identity")

    a, chi, hbar, delta, g, dimension = sp.symbols("a chi hbar delta g d", positive=True)
    weight = a / 8
    mu = chi * weight
    kappa = sp.simplify(hbar**2 / (2 * mu))
    inverse_energy_step = delta / hbar
    audit.check("symplectic weight", weight == a / 8, weight, a / 8, "coefficients")
    audit.check("canonical mass", sp.simplify(mu - a * chi / 8) == 0, mu, a * chi / 8, "coefficients")
    audit.check("heat coefficient", sp.simplify(kappa - 4 * hbar**2 / (a * chi)) == 0, kappa, 4 * hbar**2 / (a * chi), "coefficients")
    audit.check("free denominator", sp.simplify(4 * kappa - 16 * hbar**2 / (a * chi)) == 0, 4 * kappa, 16 * hbar**2 / (a * chi), "coefficients")
    physical_link = sp.simplify(1 / (4 * kappa * inverse_energy_step))
    audit.check("physical link coefficient", sp.simplify(physical_link - a * chi / (16 * hbar * delta)) == 0, physical_link, a * chi / (16 * hbar * delta), "coefficients")
    audit.check("physical action coefficient", sp.simplify(physical_link - chi * weight / (2 * hbar * delta)) == 0, physical_link, chi * weight / (2 * hbar * delta), "coefficients")
    radial_quartic = sp.simplify(weight * g / (4 * dimension))
    audit.check("radial quartic coefficient", sp.simplify(radial_quartic - a * g / (32 * dimension)) == 0, radial_quartic, a * g / (32 * dimension), "coefficients")
    audit.check("manifest inverse-energy units", "inverse-energy" in manifest["exact_heat_transfer"]["parameter_units"], manifest["exact_heat_transfer"]["parameter_units"], "inverse-energy", "coefficients")
    audit.check("manifest physical-time conversion", "t=delta/hbar" in manifest["exact_heat_transfer"]["parameter_units"], manifest["exact_heat_transfer"]["parameter_units"], "t=delta/hbar", "coefficients")

    x, y, z = sp.symbols("x y z", real=True)
    k, s, t = sp.symbols("k s t", positive=True)
    gaussian_exponent = (x - z) ** 2 / (4 * k * s) + (z - y) ** 2 / (4 * k * t)
    gaussian_mean = (t * x + s * y) / (s + t)
    completed = (s + t) * (z - gaussian_mean) ** 2 / (4 * k * s * t) + (x - y) ** 2 / (4 * k * (s + t))
    audit.check("Gaussian square completion", sp.simplify(gaussian_exponent - completed) == 0, gaussian_exponent, completed, "Gaussian")
    prefactor = (4 * sp.pi * k * s) ** sp.Rational(-1, 2) * (4 * sp.pi * k * t) ** sp.Rational(-1, 2)
    integrated_prefactor = sp.simplify(prefactor * sp.sqrt(4 * sp.pi * k * s * t / (s + t)))
    target_prefactor = (4 * sp.pi * k * (s + t)) ** sp.Rational(-1, 2)
    audit.check("Gaussian convolution prefactor", sp.simplify(integrated_prefactor / target_prefactor) == 1, integrated_prefactor, target_prefactor, "Gaussian")
    u = sp.symbols("u", real=True)
    gaussian = sp.exp(-(u - x) ** 2 / (4 * k * s)) / sp.sqrt(4 * sp.pi * k * s)
    audit.check("Gaussian normalization", sp.integrate(gaussian, (u, -sp.oo, sp.oo)) == 1, sp.integrate(gaussian, (u, -sp.oo, sp.oo)), 1, "Gaussian")
    audit.check("Gaussian symmetry", sp.simplify((x - y) ** 2 - (y - x) ** 2) == 0, "symmetric", "symmetric", "Gaussian")
    audit.check("heat full-support ledger", "K_t(q,q')>0" in manifest["heat_support_cone_no_go"]["witness"], manifest["heat_support_cone_no_go"]["witness"], "strictly positive", "Gaussian")

    p0 = sp.Matrix([[1, 1], [1, 1]]) / 2
    p1 = sp.Matrix([[1, -1], [-1, 1]]) / 2
    half_transfer = p0 + p1 / 2
    transfer = p0 + p1 / 4
    audit.check("exact half-step square", half_transfer * half_transfer == transfer, half_transfer * half_transfer, transfer, "exact_RP")
    audit.check("exact transfer symmetric", transfer.T == transfer, transfer.T, transfer, "exact_RP")
    audit.check("exact transfer strictly entrywise positive", all(value > 0 for value in transfer), list(transfer), ">0", "exact_RP")
    audit.check("exact transfer spectrum", set(transfer.eigenvals()) == {sp.Integer(1), sp.Rational(1, 4)}, transfer.eigenvals(), "{1,1/4}", "exact_RP")
    paths4 = list(product(range(2), repeat=4))
    partition_path = sp.simplify(sum(matrix_ring_weight(transfer, path) for path in paths4))
    partition_trace = sp.trace(transfer**4)
    audit.check("periodic path normalizer", partition_path == partition_trace, partition_path, partition_trace, "exact_RP")
    audit.check("periodic trace oracle", partition_trace == TEST_ORACLE_RING_Z, partition_trace, TEST_ORACLE_RING_Z, "exact_RP")

    imaginary = sp.I

    def site_function(q0: int, q1: int, q2: int) -> sp.Expr:
        return 1 + q0 + 2 * q1 - q2 + imaginary * (q1 + q2)

    site_direct = sp.Integer(0)
    for q0, q1, q2, q3 in paths4:
        weight4 = transfer[q0, q1] * transfer[q1, q2] * transfer[q2, q3] * transfer[q3, q0]
        site_direct += weight4 * sp.conjugate(site_function(q0, q3, q2)) * site_function(q0, q1, q2)
    site_square = sp.Integer(0)
    for q0, q2 in product(range(2), repeat=2):
        amplitude = sum(transfer[q0, q1] * transfer[q1, q2] * site_function(q0, q1, q2) for q1 in range(2))
        site_square += sp.conjugate(amplitude) * amplitude
    site_direct = sp.simplify(site_direct)
    site_square = sp.simplify(site_square)
    audit.check("site reflected form square", site_direct == site_square, site_direct, site_square, "exact_RP")
    audit.check("site reflected form oracle", site_direct == TEST_ORACLE_SITE_NUMERATOR, site_direct, TEST_ORACLE_SITE_NUMERATOR, "exact_RP")
    audit.check("site reflected form positive", bool(site_direct > 0), site_direct, ">0", "exact_RP")

    def link_function(q0: int, q1: int) -> sp.Expr:
        return 1 + 2 * q0 - q1 + imaginary * (q0 + q1)

    link_direct = sp.Integer(0)
    for q0, q1, q2, q3 in paths4:
        weight4 = transfer[q0, q1] * transfer[q1, q2] * transfer[q2, q3] * transfer[q3, q0]
        link_direct += weight4 * sp.conjugate(link_function(q3, q2)) * link_function(q0, q1)
    link_square = sp.Integer(0)
    for z0, z1 in product(range(2), repeat=2):
        amplitude = sp.Integer(0)
        for q0, q1 in product(range(2), repeat=2):
            amplitude += half_transfer[z0, q0] * transfer[q0, q1] * half_transfer[q1, z1] * link_function(q0, q1)
        link_square += sp.conjugate(amplitude) * amplitude
    link_direct = sp.simplify(link_direct)
    link_square = sp.simplify(link_square)
    audit.check("link reflected form half-step square", link_direct == link_square, link_direct, link_square, "exact_RP")
    audit.check("link reflected form oracle", link_direct == TEST_ORACLE_LINK_NUMERATOR, link_direct, TEST_ORACLE_LINK_NUMERATOR, "exact_RP")
    audit.check("link reflected form positive", bool(link_direct > 0), link_direct, ">0", "exact_RP")

    d1 = sp.diag(2, -1)
    d2 = sp.diag(3, 4)
    correlator_path = sp.Integer(0)
    for q0, q1, q2, q3 in paths4:
        correlator_path += matrix_ring_weight(transfer, (q0, q1, q2, q3)) * d1[q1, q1] * d2[q3, q3]
    correlator_trace = sp.trace(transfer * d1 * transfer**2 * d2 * transfer)
    audit.check("bounded path correlator trace", correlator_path == correlator_trace, correlator_path, correlator_trace, "bridge")
    audit.check("bounded correlator oracle", correlator_trace == TEST_ORACLE_CORRELATOR_NUMERATOR, correlator_trace, TEST_ORACLE_CORRELATOR_NUMERATOR, "bridge")
    audit.check("normalized bounded correlator", sp.simplify(correlator_trace / partition_trace) == sp.Rational(1703, 1028), sp.simplify(correlator_trace / partition_trace), sp.Rational(1703, 1028), "bridge")
    audit.check("cyclic trace orientation", sp.trace(transfer * d1 * transfer**2 * d2 * transfer) == sp.trace(transfer * d2 * transfer**2 * d1 * transfer), "equal", "equal", "bridge")

    psi = sp.Matrix([1, 2])
    excited = sp.Matrix([2, -1])
    ground_transfer = psi * psi.T / 5 + excited * excited.T / 20
    diagonal = sp.diag(1, 2)
    markov = diagonal.inv() * ground_transfer * diagonal
    stationary = sp.Matrix([sp.Rational(1, 5), sp.Rational(4, 5)])
    audit.check("Doob ground eigenvector", ground_transfer * psi == psi, ground_transfer * psi, psi, "Doob")
    audit.check("Doob stationary measure normalized", sum(stationary) == 1, sum(stationary), 1, "Doob")
    audit.check("Doob Markov rows", markov * sp.ones(2, 1) == sp.ones(2, 1), markov * sp.ones(2, 1), sp.ones(2, 1), "Doob")
    audit.check("Doob stationary law", markov.T * stationary == stationary, markov.T * stationary, stationary, "Doob")
    detailed = sp.diag(*stationary) * markov
    audit.check("Doob detailed balance", detailed == detailed.T, detailed, detailed.T, "Doob")
    audit.check("Doob similarity", diagonal * markov * diagonal.inv() == ground_transfer, diagonal * markov * diagonal.inv(), ground_transfer, "Doob")
    audit.check("Doob spectrum reaches zero only in infinite model", "accumulating at zero" in manifest["ground_state_Doob_Markov_interface"]["unbounded_log_boundary"], manifest["ground_state_Doob_Markov_interface"]["unbounded_log_boundary"], "accumulating at zero", "Doob")
    audit.check("Doob bounded-log no-go linked", "NG-2026-08-03-PRE-A-C0A-FINITE-HILBERT-BOUNDED-LOG-LIFT" in manifest["ground_state_Doob_Markov_interface"]["unbounded_log_boundary"], manifest["ground_state_Doob_Markov_interface"]["unbounded_log_boundary"], "registered no-go", "Doob")

    endpoint = sp.diag(sp.Rational(1, 2), sp.Rational(1, 3))
    heat_half = sp.Matrix([[sp.Rational(3, 4), sp.Rational(1, 8)], [sp.Rational(1, 8), sp.Rational(2, 3)]])
    potential_half = endpoint * heat_half**2 * endpoint
    kinetic_half = heat_half * endpoint**2 * heat_half
    audit.check("Strang orderings differ", potential_half != kinetic_half, potential_half - kinetic_half, "nonzero", "slice")
    for power in range(1, 5):
        audit.check(f"cyclic ordering trace N={power}", sp.trace(potential_half**power) == sp.trace(kinetic_half**power), sp.trace(potential_half**power), sp.trace(kinetic_half**power), "slice")
    audit.check("Strang link Gram", potential_half == (heat_half * endpoint).T * (heat_half * endpoint), potential_half, "B^*B", "slice")
    gamma, epsilon = sp.symbols("gamma epsilon", positive=True)
    quartic_trace = (4 * sp.pi * k * epsilon) ** sp.Rational(-1, 2) * sp.gamma(sp.Rational(1, 4)) / (2 * (epsilon * gamma) ** sp.Rational(1, 4))
    quartic_integral = sp.integrate(sp.exp(-epsilon * gamma * x**4), (x, -sp.oo, sp.oo))
    audit.check("quartic trace integral", sp.simplify(quartic_integral - sp.gamma(sp.Rational(1, 4)) / (2 * (epsilon * gamma) ** sp.Rational(1, 4))) == 0, quartic_integral, quartic_trace, "slice")

    potential = gamma * x**4

    def left_half(polynomial: sp.Expr) -> sp.Expr:
        return sp.expand(-potential * polynomial / 2)

    def heat(polynomial: sp.Expr) -> sp.Expr:
        return sp.expand(k * sp.diff(polynomial, x, 2))

    def exact_generator(polynomial: sp.Expr) -> sp.Expr:
        return sp.expand(heat(polynomial) - potential * polynomial)

    seed = [sp.Integer(1), sp.Integer(0), sp.Integer(0), sp.Integer(0)]
    strang_jet = compose_jet(left_half, compose_jet(heat, compose_jet(left_half, seed, 3), 3), 3)
    exact_jet = exp_jet(exact_generator, sp.Integer(1), 3)
    for degree in range(3):
        audit.check(f"quartic jets agree epsilon^{degree}", sp.expand(strang_jet[degree] - exact_jet[degree]) == 0, strang_jet[degree], exact_jet[degree], "one_slice")
    jet_defect = sp.expand(strang_jet[3] - exact_jet[3])
    closed_defect = sp.expand(-k * sp.diff(potential, x) ** 2 / 12 - k**2 * sp.diff(potential, x, 4) / 12)
    audit.check("quartic epsilon-cubed defect", sp.expand(jet_defect - closed_defect) == 0, jet_defect, closed_defect, "one_slice")
    audit.check("quartic origin defect", jet_defect.subs(x, 0) == -2 * gamma * k**2, jet_defect.subs(x, 0), -2 * gamma * k**2, "one_slice")
    audit.check("quartic highest-degree sentinel", sp.Poly(jet_defect, x).coeff_monomial(x**6) == -sp.Rational(4, 3) * gamma**2 * k, sp.Poly(jet_defect, x), -sp.Rational(4, 3) * gamma**2 * k, "one_slice")

    q = sp.symbols("q0:8", real=True)
    lam = sp.symbols("lambda", nonnegative=True)
    edges = cube_edges()
    audit.check("Q3 edge count", len(edges) == 12, len(edges), 12, "actual_CL8")
    one_node_quartic = g * sum(value**4 for value in q) / 4
    one_node_quartic += lam * sum((q[left] - q[right]) ** 2 * (q[left] ** 2 + q[right] ** 2) for left, right in edges) / 4
    laplacian = sum(sp.diff(one_node_quartic, value, 2) for value in q)
    bilaplacian = sp.expand(sum(sp.diff(laplacian, value, 2) for value in q))
    zero = {value: 0 for value in q}
    per_node_bilaplacian = sp.expand(bilaplacian.subs(zero))
    audit.check("actual Q3 bi-Laplacian per node", per_node_bilaplacian == 48 * (g + 4 * lam), per_node_bilaplacian, 48 * (g + 4 * lam), "actual_CL8")
    nodes = sp.symbols("M", integer=True, positive=True)
    actual_bilaplacian = sp.expand(weight * nodes * per_node_bilaplacian)
    actual_defect = sp.expand(-kappa**2 * actual_bilaplacian / 12)
    actual_g_coefficient = sp.diff(per_node_bilaplacian, g)
    actual_lambda_coefficient = sp.diff(per_node_bilaplacian, lam)
    actual_defect_factor = sp.simplify(actual_defect / (kappa**2 * weight * nodes * (g + 4 * lam)))
    audit.check("actual CL8 bi-Laplacian", sp.simplify(actual_bilaplacian - 48 * weight * nodes * (g + 4 * lam)) == 0, actual_bilaplacian, 48 * weight * nodes * (g + 4 * lam), "actual_CL8")
    audit.check("actual CL8 one-slice defect", sp.expand(actual_defect + 4 * kappa**2 * weight * nodes * (g + 4 * lam)) == 0, actual_defect, -4 * kappa**2 * weight * nodes * (g + 4 * lam), "actual_CL8")
    audit.check("actual CL8 defect strict sign", bool(actual_defect.subs({a: 1, chi: 1, hbar: 1, nodes: 2, g: 1, lam: 0}) < 0), actual_defect, "<0", "actual_CL8")

    path_velocity = sp.simplify(2 * dimension * kappa / epsilon)
    audit.check("Brownian velocity divergence coefficient", sp.simplify(path_velocity - 8 * dimension * hbar**2 / (a * chi * epsilon)) == 0, path_velocity, 8 * dimension * hbar**2 / (a * chi * epsilon), "boundaries")
    audit.check("path momentum scope false", manifest["scope"]["canonical_momentum_from_path_variable"] is False, manifest["scope"]["canonical_momentum_from_path_variable"], False, "boundaries")
    entrywise_indefinite = sp.Matrix([[1, 2], [2, 1]])
    audit.check("pointwise-positive operator sentinel", (sp.Matrix([1, -1]).T * entrywise_indefinite * sp.Matrix([1, -1]))[0] < 0, entrywise_indefinite, "negative form", "boundaries")
    positive_not_cone = sp.Matrix([[2, -1], [-1, 2]])
    audit.check("operator-positive cone sentinel", min(positive_not_cone.eigenvals()) > 0 and any(value < 0 for value in positive_not_cone), positive_not_cone, "SPD with negative entries", "boundaries")

    gate = manifest["gate_resolution"]
    audit.check("gate status", gate["status"].startswith("FIXED-SPATIAL-REGULATOR SUBGATES CLOSED"), gate["status"], "fixed regulator only", "gate")
    audit.check("closed gate count", len(gate["closed_subgates"]) == 5, gate["closed_subgates"], 5, "gate")
    audit.check("refuted gate count", len(gate["refuted_subgates"]) == 2, gate["refuted_subgates"], 2, "gate")
    audit.check("open gate count", len(gate["open_subgates"]) == 7, gate["open_subgates"], 7, "gate")
    audit.check("next gate", gate["next_gate"] == "PA-CP1-CL8-REGULATOR-COMPATIBLE-RP-FEYNMAN-KAC-STATE-AND-WEYL-LIMIT", gate["next_gate"], "PA-CP1-CL8-REGULATOR-COMPATIBLE-RP-FEYNMAN-KAC-STATE-AND-WEYL-LIMIT", "gate")

    true_scope = {
        "fixed_regulator_exact_heat_transfer",
        "fixed_regulator_Feynman_Kac_kernel",
        "fixed_regulator_site_reflection_positive",
        "fixed_regulator_link_reflection_positive",
        "fixed_regulator_configuration_Gibbs_bridge",
        "fixed_regulator_symmetric_slice_reflection_positive",
        "fixed_regulator_symmetric_product_trace_norm_limit",
        "fixed_regulator_ground_state_Doob_Markov_interface",
    }
    for key, value in manifest["scope"].items():
        expected = key in true_scope
        audit.check(f"scope {key}", value is expected, value, expected, "scope")
    audit.check("all scope values boolean", all(isinstance(value, bool) for value in manifest["scope"].values()), manifest["scope"], "booleans", "scope")

    audit.check("C6 tier unchanged", status["tier"] == "T1", status["tier"], "T1", "claim_firewall")
    audit.check("C6 lifecycle unchanged", status["lifecycle"] == "ACTIVE", status["lifecycle"], "ACTIVE", "claim_firewall")
    audit.check("C6 evidence unchanged", status["evidence_grade"] == ["CONDITIONAL"], status["evidence_grade"], ["CONDITIONAL"], "claim_firewall")
    audit.check("C6 gate unchanged", status["open_gates"] == ["C6-BCC-PREMISE-BLOCKED"], status["open_gates"], ["C6-BCC-PREMISE-BLOCKED"], "claim_firewall")

    required_phrases = (
        "lattice-preserving dihedral reflection axis",
        "continuous-time periodic loop law",
        "NG-2026-08-03-PRE-A-C0A-FINITE-HILBERT-BOUNDED-LOG-LIFT",
        "B_\\epsilon^*B_\\epsilon",
        "O(N^(-1/2))",
        "Delta^2U_a(0)=6wgd+192w\\lambda M",
        "below-empty-space energy comparison",
    )
    for phrase in required_phrases:
        audit.check(f"certificate phrase {phrase[:30]}", phrase in certificate, phrase, "present", "source")
    audit.check("Simon source", "S0273-0979-1982-15041-8" in certificate, "Simon DOI", "present", "source")
    audit.check("DIT source", "05020359" in certificate, "DIT DOI", "present", "source")
    package_paths = (MANIFEST, CERTIFICATE, SCRIPT)
    audit.check("package ASCII", all(ord(character) < 128 for path in package_paths for character in path.read_text(encoding="utf-8")), "ASCII", "clean", "hygiene")

    return {
        "schema": SCHEMA,
        "candidate_id": CANDIDATE_ID,
        "result_id": RESULT_ID,
        "parent_ids": list(PARENT_IDS),
        "negative_ids": list(NEGATIVE_IDS),
        "exploration_id": EXPLORATION_ID,
        "claim_bearing": False,
        "verdict": gate["status"],
        "next_gate": gate["next_gate"],
        "script_version": __version__,
        "source_sha256": {
            "script": sha256(SCRIPT),
            "manifest": sha256(MANIFEST),
            "certificate": sha256(CERTIFICATE),
            **{f"parent_{index}": sha256(path) for index, path in enumerate(PARENTS, start=1)},
        },
        "derived": {
            "coefficient_ledger": {
                "w": str(weight),
                "mu": str(mu),
                "kappa": str(kappa),
                "physical_link": str(physical_link),
            },
            "Gaussian": {"mean": str(gaussian_mean), "completed": str(completed), "prefactor": str(integrated_prefactor)},
            "exact_RP": {
                "half_transfer": [[str(value) for value in half_transfer.row(row)] for row in range(2)],
                "transfer": [[str(value) for value in transfer.row(row)] for row in range(2)],
                "Z": str(partition_trace),
                "site_numerator": str(site_direct),
                "link_numerator": str(link_direct),
                "correlator_numerator": str(correlator_trace),
            },
            "Doob": {
                "transfer": [[str(value) for value in ground_transfer.row(row)] for row in range(2)],
                "P": [[str(value) for value in markov.row(row)] for row in range(2)],
                "pi": [str(value) for value in stationary],
            },
            "quartic_jet": {
                "strang": [str(value) for value in strang_jet],
                "exact": [str(value) for value in exact_jet],
                "defect": str(jet_defect),
                "actual_CL8_bilaplacian": str(actual_bilaplacian),
                "actual_CL8_defect": str(actual_defect),
                "actual_CL8_per_node_g_coefficient": str(actual_g_coefficient),
                "actual_CL8_per_node_lambda_coefficient": str(actual_lambda_coefficient),
                "actual_CL8_defect_factor": str(actual_defect_factor),
            },
        },
        "scope": manifest["scope"],
        "assertions": audit.rows,
        "assertion_summary": {"passed": len(audit.rows), "total": len(audit.rows)},
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    arguments = parser.parse_args()
    payload = build_payload()
    if not arguments.self_test:
        atomic_json(arguments.output, payload)
    print(f"{CANDIDATE_ID}: {payload['assertion_summary']['passed']}/{payload['assertion_summary']['total']} PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

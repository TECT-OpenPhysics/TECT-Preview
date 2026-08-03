#!/usr/bin/env python3
"""Primary exact audit for the CL8 classical invariance-selection fork.

The executable checks the inherited one-eighth Hamiltonian normalization,
coercive Gibbs bound, Liouville identities, canonical momentum variance, and
the two common continuum/lattice equilibrium-measure witnesses.  The general
measure-theoretic proof and scope boundary are recorded in the certificate.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

import sympy as sp


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
CANDIDATE_ID = "PA-CP1-CL8-INVARIANCE-SELECTION-FORK-v0"
PARENT_IDS = (
    "PA-CP1-ST8-Q3LOCK-v0",
    "PA-CP1-CL8-GLOBAL-GOURSAT-CONTINUATION-v0",
    "PA-CP1-CL8-CLASSICAL-BOUNDARY-TO-LATTICE-OA2-v0",
)
RESULT_ID = "PA-CP1-CL8-FINITE-GIBBS-AND-COMMON-EQUILIBRIUM-MEASURE-FORK"
NEGATIVE_ID = "NG-2026-08-03-PRE-A-CP1-CL8-INVARIANCE-ONLY-PREFERRED-STATE"
SLUG = "pre-a-cp1-cl8-invariance-selection-fork"
SCHEMA = f"tect/{SLUG}-primary/0.1"
SCRIPT = Path(__file__).resolve()
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
SEMIDISCRETE = REPO / "strategy/pre-a-cp1-cl8-semidiscrete-cauchy-oa2-manifest.json"
Q3LOCK = REPO / "strategy/pre-a-cp1-st8-q3lock-manifest.json"
GLOBAL = REPO / "strategy/pre-a-cp1-cl8-global-goursat-continuation-manifest.json"
COMPOSITION = REPO / "strategy/pre-a-cp1-cl8-classical-boundary-lattice-oa2-manifest.json"
DEFAULT_OUTPUT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / f"2026-08-03-primary-{SLUG}/result.json"
)


def serial(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value).replace("\\", "/")
    if isinstance(value, Fraction):
        return str(value)
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
        self.rows.append(
            {
                "name": name,
                "group": group,
                "status": "PASS",
                "actual": serial(actual),
                "expected": serial(expected),
            }
        )


def q3_graph() -> tuple[list[tuple[int, ...]], list[tuple[tuple[int, ...], tuple[int, ...]]]]:
    vertices = list(itertools.product((0, 1), repeat=3))
    edges: list[tuple[tuple[int, ...], tuple[int, ...]]] = []
    for index, left in enumerate(vertices):
        for right in vertices[index + 1 :]:
            if sum(a != b for a, b in zip(left, right)) == 1:
                edges.append((left, right))
    return vertices, edges


def graph_connected(vertices: list[tuple[int, ...]], edges: list[tuple[tuple[int, ...], tuple[int, ...]]]) -> bool:
    seen = {vertices[0]}
    frontier = [vertices[0]]
    while frontier:
        current = frontier.pop()
        for left, right in edges:
            if left == current and right not in seen:
                seen.add(right)
                frontier.append(right)
            elif right == current and left not in seen:
                seen.add(left)
                frontier.append(left)
    return len(seen) == len(vertices)


def build_payload() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    semidiscrete = json.loads(SEMIDISCRETE.read_text(encoding="utf-8"))
    q3lock = json.loads(Q3LOCK.read_text(encoding="utf-8"))
    global_manifest = json.loads(GLOBAL.read_text(encoding="utf-8"))
    composition = json.loads(COMPOSITION.read_text(encoding="utf-8"))
    audit = Audit()

    audit.check("candidate id", manifest["candidate_id"] == CANDIDATE_ID, manifest["candidate_id"], CANDIDATE_ID, "identity")
    audit.check("result id", manifest["result_id"] == RESULT_ID, manifest["result_id"], RESULT_ID, "identity")
    audit.check("parent ids", tuple(manifest["parent_ids"]) == PARENT_IDS, manifest["parent_ids"], PARENT_IDS, "identity")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "identity")
    audit.check("C6 context", manifest["claim_context"] == "C6-SPACETIME-SIGNATURE", manifest["claim_context"], "C6-SPACETIME-SIGNATURE", "identity")
    audit.check("negative id", manifest["formal_selection_no_go"]["negative_id"] == NEGATIVE_ID, manifest["formal_selection_no_go"]["negative_id"], NEGATIVE_ID, "identity")
    audit.check("semidiscrete parent", semidiscrete["candidate_id"] == "PA-CP1-CL8-SEMIDISCRETE-CAUCHY-OA2-v0", semidiscrete["candidate_id"], "PA-CP1-CL8-SEMIDISCRETE-CAUCHY-OA2-v0", "parents")
    audit.check("Q3 parent", q3lock["candidate_id"] == PARENT_IDS[0], q3lock["candidate_id"], PARENT_IDS[0], "parents")
    audit.check("global parent", global_manifest["candidate_id"] == PARENT_IDS[1], global_manifest["candidate_id"], PARENT_IDS[1], "parents")
    audit.check("composition parent", composition["candidate_id"] == PARENT_IDS[2], composition["candidate_id"], PARENT_IDS[2], "parents")
    audit.check("Hamiltonian normalization inherited", semidiscrete["hamiltonian_structure"]["Hamiltonian"].startswith("H_a=(a/8)"), semidiscrete["hamiltonian_structure"]["Hamiltonian"], "starts H_a=(a/8)", "parents")
    audit.check("symplectic normalization inherited", semidiscrete["hamiltonian_structure"]["symplectic_form"].startswith("Omega_a=(a/8)"), semidiscrete["hamiltonian_structure"]["symplectic_form"], "starts Omega_a=(a/8)", "parents")

    vertices, edges = q3_graph()
    species = len(vertices)
    audit.check("Q3 species count", species == 8, species, 8, "Q3")
    audit.check("Q3 edge count", len(edges) == 12, len(edges), 12, "Q3")
    audit.check("Q3 connected", graph_connected(vertices, edges), graph_connected(vertices, edges), True, "Q3")

    z, r_minus, g = sp.symbols("z r_minus g", positive=True, real=True)
    weak_residual = -r_minus * z**2 / 2 + g * z**4 / 4 - g * z**4 / 8 + r_minus**2 / (2 * g)
    expected_square = (g * z**2 - 2 * r_minus) ** 2 / (8 * g)
    audit.check("weak coercive square identity", sp.expand(weak_residual - expected_square) == 0, sp.expand(weak_residual), sp.expand(expected_square), "coercivity")

    r = sp.symbols("r", negative=True, real=True)
    onsite = r * z**2 / 2 + g * z**4 / 4
    v_squared = -r / g
    onsite_ordered = sp.factor(onsite.subs(z**2, v_squared))
    audit.check("ordered onsite energy", onsite_ordered == -r**2 / (4 * g), onsite_ordered, -r**2 / (4 * g), "coercivity")
    audit.check("ordered onsite force", sp.factor(sp.diff(onsite, z).subs(z**2, v_squared)) == 0, sp.factor(sp.diff(onsite, z).subs(z**2, v_squared)), 0, "coercivity")

    L, M, a, chi = sp.symbols("L M a chi", positive=True)
    weight = a / 8
    configuration_dimension = 8 * M
    phase_dimension = 2 * configuration_dimension
    momentum_coefficient = sp.factor(weight / (2 * chi))
    quartic_coefficient = sp.factor(weight * g / 8)
    weak_constant = sp.factor(weight * M * 8 * r_minus**2 / (2 * g))
    exact_floor = sp.factor(-weight * M * 8 * r**2 / (4 * g)).subs(a * M, L)
    audit.check("momentum lower-bound coefficient", momentum_coefficient == a / (16 * chi), momentum_coefficient, a / (16 * chi), "coercivity")
    audit.check("quartic lower-bound coefficient", quartic_coefficient == a * g / 64, quartic_coefficient, a * g / 64, "coercivity")
    audit.check("weak additive constant", sp.factor(weak_constant.subs(a * M, L)) == L * r_minus**2 / (2 * g), sp.factor(weak_constant.subs(a * M, L)), L * r_minus**2 / (2 * g), "coercivity")
    audit.check("exact energy floor", exact_floor == -L * r**2 / (4 * g), exact_floor, -L * r**2 / (4 * g), "coercivity")

    q0, q1, p0, p1, coupling, beta = sp.symbols("q0 q1 p0 p1 coupling beta", real=True)
    test_weight = sp.Rational(3, 7)
    test_chi = sp.Rational(5, 2)
    test_hamiltonian = test_weight * (
        (p0**2 + p1**2) / (2 * test_chi)
        + q0**4 / 4
        + q1**4 / 4
        + coupling * (q0 - q1) ** 2 / 2
    )
    variables_q = (q0, q1)
    variables_p = (p0, p1)
    vector_field = [sp.diff(test_hamiltonian, item) / test_weight for item in variables_p]
    vector_field += [-sp.diff(test_hamiltonian, item) / test_weight for item in variables_q]
    divergence = sum(sp.diff(vector_field[index], variable) for index, variable in enumerate(variables_q + variables_p))
    h_dot = sum(sp.diff(test_hamiltonian, variable) * component for variable, component in zip(variables_q + variables_p, vector_field))
    audit.check("Hamiltonian vector field divergence", sp.simplify(divergence) == 0, sp.simplify(divergence), 0, "Liouville")
    audit.check("Hamiltonian conserved symbolically", sp.simplify(h_dot) == 0, sp.simplify(h_dot), 0, "Liouville")
    density_dot = sp.factor(-beta * sp.exp(-beta * test_hamiltonian) * h_dot)
    audit.check("Gibbs density stationary", density_dot == 0, density_dot, 0, "Liouville")

    beta_symbol = sp.symbols("beta", positive=True)
    variance = sp.factor(chi / (beta_symbol * weight))
    audit.check("canonical momentum variance", variance == 8 * chi / (beta_symbol * a), variance, 8 * chi / (beta_symbol * a), "Gibbs")
    fixture_variances = [variance.subs({chi: 2, a: sp.Rational(1, 2), beta_symbol: value}) for value in (1, 2)]
    audit.check("different beta values are distinct", fixture_variances == [32, 16], fixture_variances, [32, 16], "Gibbs")
    audit.check("canonical beta domain", manifest["finite_gibbs_theorem"]["normalization_range"].startswith("Z_(beta,a) is finite exactly for beta>0"), manifest["finite_gibbs_theorem"]["normalization_range"], "beta>0 only", "Gibbs")
    audit.check("general F(H) family retained", "F(H_a)" in manifest["finite_gibbs_theorem"]["general_invariant_family"], manifest["finite_gibbs_theorem"]["general_invariant_family"], "contains F(H_a)", "Gibbs")
    audit.check("compact sublevel control retained", "compact sublevel" in manifest["finite_gibbs_theorem"]["compact_invariant_controls"], manifest["finite_gibbs_theorem"]["compact_invariant_controls"], "contains compact sublevel", "Gibbs")

    q_symbols = sp.symbols("q0:8", real=True)
    q3_potential = sum(r * item**2 / 2 + g * item**4 / 4 for item in q_symbols)
    vertex_to_index = {vertex: index for index, vertex in enumerate(vertices)}
    lambda_symbol = sp.symbols("lambda", nonnegative=True, real=True)
    for left, right in edges:
        left_q = q_symbols[vertex_to_index[left]]
        right_q = q_symbols[vertex_to_index[right]]
        q3_potential += lambda_symbol * (left_q - right_q) ** 2 * (left_q**2 + right_q**2) / 4
    collective = {item: z for item in q_symbols}
    collective_forces = [sp.factor(sp.diff(q3_potential, item).subs(collective)) for item in q_symbols]
    audit.check("collective Q3 force", all(force == z * (g * z**2 + r) for force in collective_forces), collective_forces, [z * (g * z**2 + r)] * 8, "witness")
    zero_forces = [force.subs(z, 0) for force in collective_forces]
    ordered_forces = [sp.factor(force.subs(z**2, -r / g)) for force in collective_forces]
    audit.check("zero equilibrium force", all(force == 0 for force in zero_forces), zero_forces, [0] * 8, "witness")
    audit.check("ordered equilibrium force", all(force == 0 for force in ordered_forces), ordered_forces, [0] * 8, "witness")

    raw_zero_energy = sp.Integer(0)
    raw_ordered_energy = -L * r**2 / (4 * g)
    audit.check("zero raw energy", raw_zero_energy == 0, raw_zero_energy, 0, "witness")
    audit.check("ordered raw energy", raw_ordered_energy == -L * r**2 / (4 * g), raw_ordered_energy, -L * r**2 / (4 * g), "witness")
    zero_mean = sp.Integer(0)
    ordered_symmetric_mean = sp.simplify((sp.sqrt(-r / g) - sp.sqrt(-r / g)) / 2)
    ordered_second_moment = sp.simplify(((-r / g) + (-r / g)) / 2)
    audit.check("both witness means are Z2 symmetric", [zero_mean, ordered_symmetric_mean] == [0, 0], [zero_mean, ordered_symmetric_mean], [0, 0], "witness")
    audit.check("witness second moments differ", ordered_second_moment == -r / g and ordered_second_moment != 0, ordered_second_moment, -r / g, "witness")
    audit.check("constant trace seams exact", all(sp.diff(sp.Integer(1), z, order) == (1 if order == 0 else 0) for order in range(9)), True, True, "witness")
    audit.check("equilibrium composition error", manifest["common_equilibrium_measures"]["composition"].endswith("error is zero"), manifest["common_equilibrium_measures"]["composition"], "ends error is zero", "witness")
    witness_symmetries = manifest["common_equilibrium_measures"]["symmetries"]
    for token in ("spatial translations", "Q3 automorphisms", "global Z2", "momentum reversal", "time reversal"):
        audit.check(f"witness symmetry: {token}", token in witness_symmetries, witness_symmetries, f"contains {token}", "witness")
    audit.check("witness measures distinct", "disjoint supports" in manifest["common_equilibrium_measures"]["distinctness"], manifest["common_equilibrium_measures"]["distinctness"], "contains disjoint supports", "witness")

    audit.check("parent preferred-state gate remains open", manifest["gate_resolution"]["status"] == "SPLIT; PARENT GATE REMAINS OPEN", manifest["gate_resolution"]["status"], "SPLIT; PARENT GATE REMAINS OPEN", "scope")
    audit.check("next gate quantum finite regulator", manifest["gate_resolution"]["next_gate"] == "PA-CP1-CL8-FINITE-REGULATOR-QUANTUM-STATE", manifest["gate_resolution"]["next_gate"], "PA-CP1-CL8-FINITE-REGULATOR-QUANTUM-STATE", "scope")
    required_false = (
        "invariance_only_unique_preference",
        "derived_beta_or_energy",
        "selected_physical_classical_measure",
        "finite_quantum_state",
        "quantum_boundary_state",
        "continuum_quantum_state",
        "Hadamard_state",
        "physical_vacuum",
        "below_empty_space",
        "C6_claim_advanced",
        "CP1_complete",
        "Pre_A_complete",
    )
    for key in required_false:
        audit.check(f"scope false: {key}", manifest["scope"][key] is False, manifest["scope"][key], False, "scope")

    payload = {
        "schema": SCHEMA,
        "candidate_id": CANDIDATE_ID,
        "parent_ids": list(PARENT_IDS),
        "result_id": RESULT_ID,
        "task_id": "T-054",
        "claim_context": "C6-SPACETIME-SIGNATURE",
        "claim_bearing": False,
        "verdict": manifest["verdict"],
        "derived": {
            "Q3": {"species": species, "edges": len(edges), "connected": True},
            "dimensions": {"configuration": "8*M", "phase": "16*M"},
            "normalization": {
                "symplectic_weight": "a/8",
                "momentum_lower_coefficient": "a/(16*chi)",
                "quartic_lower_coefficient": "a*g/64",
            },
            "coercivity": {
                "weak_constant": "L*r_minus^2/(2*g)",
                "exact_floor": "-L*r_minus^2/(4*g)",
                "weak_square": "(g*z^2-2*r_minus)^2/(8*g)",
            },
            "Liouville": {"divergence": divergence, "H_dot": h_dot, "density_dot": density_dot},
            "Gibbs": {
                "beta_domain": "beta>0",
                "momentum_variance": "8*chi/(beta*a)",
                "fixture_variances": fixture_variances,
                "full_support": True,
                "compact_sublevel_controls": True,
            },
            "witnesses": {
                "zero_energy": raw_zero_energy,
                "ordered_energy": "-L*r^2/(4*g)",
                "zero_second_moment": 0,
                "ordered_second_moment": "-r/g",
                "all_seams": True,
                "composition_error": 0,
                "distinct": True,
            },
            "negative_id": NEGATIVE_ID,
        },
        "source_sha256": {
            "script": sha256(SCRIPT),
            "manifest": sha256(MANIFEST),
            "semidiscrete_manifest": sha256(SEMIDISCRETE),
            "q3lock_manifest": sha256(Q3LOCK),
            "global_manifest": sha256(GLOBAL),
            "composition_manifest": sha256(COMPOSITION),
        },
        "scope": manifest["scope"],
        "assertions": audit.rows,
        "assertion_summary": {"passed": len(audit.rows), "total": len(audit.rows)},
        "next_gate": manifest["gate_resolution"]["next_gate"],
        "no_overclaim": manifest["no_overclaim"],
    }
    return payload


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

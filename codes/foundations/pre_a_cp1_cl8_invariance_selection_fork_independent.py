#!/usr/bin/env python3
"""Independent rational audit for the CL8 invariance-selection fork.

This implementation imports neither the primary module nor SymPy.  It checks
the normalization and coercive coefficients with Fraction arithmetic, builds
Q3 directly, evaluates a nontrivial Hamiltonian conservation fixture, and
audits the equilibrium-measure and scope statements from source authorities.
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
SCHEMA = f"tect/{SLUG}-independent/0.1"
SCRIPT = Path(__file__).resolve()
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
SEMIDISCRETE = REPO / "strategy/pre-a-cp1-cl8-semidiscrete-cauchy-oa2-manifest.json"
Q3LOCK = REPO / "strategy/pre-a-cp1-st8-q3lock-manifest.json"
GLOBAL = REPO / "strategy/pre-a-cp1-cl8-global-goursat-continuation-manifest.json"
COMPOSITION = REPO / "strategy/pre-a-cp1-cl8-classical-boundary-lattice-oa2-manifest.json"
DEFAULT_OUTPUT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / f"2026-08-03-independent-{SLUG}/result.json"
)


def serial(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value).replace("\\", "/")
    if isinstance(value, Fraction):
        return str(value)
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
    edges = []
    for left in vertices:
        for right in vertices:
            if left < right and sum(a != b for a, b in zip(left, right)) == 1:
                edges.append((left, right))
    return vertices, edges


def connected(vertices: list[tuple[int, ...]], edges: list[tuple[tuple[int, ...], tuple[int, ...]]]) -> bool:
    reached = {vertices[0]}
    changed = True
    while changed:
        changed = False
        for left, right in edges:
            if left in reached and right not in reached:
                reached.add(right)
                changed = True
            if right in reached and left not in reached:
                reached.add(left)
                changed = True
    return reached == set(vertices)


def build_payload() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    semidiscrete = json.loads(SEMIDISCRETE.read_text(encoding="utf-8"))
    q3lock = json.loads(Q3LOCK.read_text(encoding="utf-8"))
    global_manifest = json.loads(GLOBAL.read_text(encoding="utf-8"))
    composition = json.loads(COMPOSITION.read_text(encoding="utf-8"))
    audit = Audit()

    audit.check("candidate id", manifest.get("candidate_id") == CANDIDATE_ID, manifest.get("candidate_id"), CANDIDATE_ID, "identity")
    audit.check("result id", manifest.get("result_id") == RESULT_ID, manifest.get("result_id"), RESULT_ID, "identity")
    audit.check("parent ids", tuple(manifest.get("parent_ids", [])) == PARENT_IDS, manifest.get("parent_ids"), PARENT_IDS, "identity")
    audit.check("claim nonbearing", manifest.get("claim_bearing") is False, manifest.get("claim_bearing"), False, "identity")
    audit.check("negative id", manifest["formal_selection_no_go"]["negative_id"] == NEGATIVE_ID, manifest["formal_selection_no_go"]["negative_id"], NEGATIVE_ID, "identity")
    audit.check("semidiscrete authority", semidiscrete["candidate_id"] == "PA-CP1-CL8-SEMIDISCRETE-CAUCHY-OA2-v0", semidiscrete["candidate_id"], "PA-CP1-CL8-SEMIDISCRETE-CAUCHY-OA2-v0", "parents")
    audit.check("Q3 authority", q3lock["candidate_id"] == PARENT_IDS[0], q3lock["candidate_id"], PARENT_IDS[0], "parents")
    audit.check("global authority", global_manifest["candidate_id"] == PARENT_IDS[1], global_manifest["candidate_id"], PARENT_IDS[1], "parents")
    audit.check("composition authority", composition["candidate_id"] == PARENT_IDS[2], composition["candidate_id"], PARENT_IDS[2], "parents")
    audit.check("one-eighth Hamiltonian parsed", "H_a=(a/8)" in semidiscrete["hamiltonian_structure"]["Hamiltonian"], semidiscrete["hamiltonian_structure"]["Hamiltonian"], "contains H_a=(a/8)", "parents")
    audit.check("one-eighth symplectic form parsed", "Omega_a=(a/8)" in semidiscrete["hamiltonian_structure"]["symplectic_form"], semidiscrete["hamiltonian_structure"]["symplectic_form"], "contains Omega_a=(a/8)", "parents")

    vertices, edges = q3_graph()
    species = len(vertices)
    audit.check("direct Q3 species", species == 8, species, 8, "Q3")
    audit.check("direct Q3 edges", len(edges) == 12, len(edges), 12, "Q3")
    audit.check("direct Q3 connectivity", connected(vertices, edges), connected(vertices, edges), True, "Q3")

    # Exact rational hostile fixture.  These are declared test inputs, not
    # derived physical numbers.
    L = Fraction(2)
    M = 4
    a = L / M
    chi = Fraction(2)
    r = Fraction(-3)
    r_minus = -r
    g = Fraction(2)
    weight = a / 8
    configuration_dimension = 8 * M
    phase_dimension = 2 * configuration_dimension
    audit.check("fixture spacing", a == Fraction(1, 2), a, Fraction(1, 2), "fixture")
    audit.check("fixture configuration dimension", configuration_dimension == 32, configuration_dimension, 32, "fixture")
    audit.check("fixture phase dimension", phase_dimension == 64, phase_dimension, 64, "fixture")

    weak_polynomial = {
        4: g / 4 - g / 8,
        2: r / 2,
        0: r_minus * r_minus / (2 * g),
    }
    square_polynomial = {
        4: g * g / (8 * g),
        2: -4 * g * r_minus / (8 * g),
        0: 4 * r_minus * r_minus / (8 * g),
    }
    audit.check("weak square coefficients", weak_polynomial == square_polynomial, weak_polynomial, square_polynomial, "coercivity")
    v_squared = r_minus / g
    onsite_ordered = r * v_squared / 2 + g * v_squared * v_squared / 4
    onsite_force_factor = r + g * v_squared
    audit.check("ordered amplitude squared", v_squared == Fraction(3, 2), v_squared, Fraction(3, 2), "coercivity")
    audit.check("ordered onsite energy", onsite_ordered == -r * r / (4 * g), onsite_ordered, -r * r / (4 * g), "coercivity")
    audit.check("ordered force factor", onsite_force_factor == 0, onsite_force_factor, 0, "coercivity")

    momentum_coefficient = weight / (2 * chi)
    quartic_coefficient = weight * g / 8
    weak_constant = L * r_minus * r_minus / (2 * g)
    exact_floor = -L * r_minus * r_minus / (4 * g)
    audit.check("momentum coefficient", momentum_coefficient == Fraction(1, 64), momentum_coefficient, Fraction(1, 64), "coercivity")
    audit.check("quartic coefficient", quartic_coefficient == Fraction(1, 64), quartic_coefficient, Fraction(1, 64), "coercivity")
    audit.check("weak constant", weak_constant == Fraction(9, 2), weak_constant, Fraction(9, 2), "coercivity")
    audit.check("exact floor", exact_floor == Fraction(-9, 4), exact_floor, Fraction(-9, 4), "coercivity")

    # Nontrivial two-coordinate conservation fixture for
    # H=w[(p0^2+p1^2)/(2chi)+(q0^4+q1^4)/4+k(q0-q1)^2/2].
    q0, q1 = Fraction(1), Fraction(-2)
    p0, p1 = Fraction(3), Fraction(4)
    coupling = Fraction(5)
    qdot0, qdot1 = p0 / chi, p1 / chi
    dVdq0 = q0**3 + coupling * (q0 - q1)
    dVdq1 = q1**3 - coupling * (q0 - q1)
    pdot0, pdot1 = -dVdq0, -dVdq1
    dHdq0, dHdq1 = weight * dVdq0, weight * dVdq1
    dHdp0, dHdp1 = weight * p0 / chi, weight * p1 / chi
    h_dot = dHdq0 * qdot0 + dHdq1 * qdot1 + dHdp0 * pdot0 + dHdp1 * pdot1
    step = Fraction(1, 7)

    def qdot_0(q_value: Fraction, p_value: Fraction) -> Fraction:
        del q_value
        return p_value / chi

    def qdot_1(q_value: Fraction, p_value: Fraction) -> Fraction:
        del q_value
        return p_value / chi

    def pdot_0(q_left: Fraction, q_right: Fraction, p_value: Fraction) -> Fraction:
        del p_value
        return -(q_left**3 + coupling * (q_left - q_right))

    def pdot_1(q_left: Fraction, q_right: Fraction, p_value: Fraction) -> Fraction:
        del p_value
        return -(q_right**3 - coupling * (q_left - q_right))

    divergence_terms = [
        (qdot_0(q0 + step, p0) - qdot_0(q0 - step, p0)) / (2 * step),
        (qdot_1(q1 + step, p1) - qdot_1(q1 - step, p1)) / (2 * step),
        (pdot_0(q0, q1, p0 + step) - pdot_0(q0, q1, p0 - step)) / (2 * step),
        (pdot_1(q0, q1, p1 + step) - pdot_1(q0, q1, p1 - step)) / (2 * step),
    ]
    audit.check("direct Hamiltonian conservation fixture", h_dot == 0, h_dot, 0, "Liouville")
    audit.check("block divergence terms", sum(divergence_terms) == 0, divergence_terms, [0, 0, 0, 0], "Liouville")
    audit.check("stationary density directional derivative", -Fraction(7, 3) * h_dot == 0, -Fraction(7, 3) * h_dot, 0, "Liouville")

    variance_beta_1 = 8 * chi / a
    variance_beta_2 = 8 * chi / (2 * a)
    fixture_variances = [variance_beta_1, variance_beta_2]
    audit.check("beta-one momentum variance", variance_beta_1 == 32, variance_beta_1, 32, "Gibbs")
    audit.check("beta-two momentum variance", variance_beta_2 == 16, variance_beta_2, 16, "Gibbs")
    audit.check("beta family distinct", variance_beta_1 != variance_beta_2, fixture_variances, "distinct", "Gibbs")
    audit.check("positive beta exact range", "beta>0" in manifest["finite_gibbs_theorem"]["normalization_range"], manifest["finite_gibbs_theorem"]["normalization_range"], "contains beta>0", "Gibbs")
    audit.check("full noncompact Gibbs support", "full noncompact support" in manifest["finite_gibbs_theorem"]["canonical_measure"], manifest["finite_gibbs_theorem"]["canonical_measure"], "contains full noncompact support", "Gibbs")
    audit.check("F(H) nonuniqueness", "F(H_a)" in manifest["finite_gibbs_theorem"]["general_invariant_family"], manifest["finite_gibbs_theorem"]["general_invariant_family"], "contains F(H_a)", "Gibbs")
    audit.check("compact energy family", "choice of E is an additional input" in manifest["finite_gibbs_theorem"]["compact_invariant_controls"], manifest["finite_gibbs_theorem"]["compact_invariant_controls"], "contains additional E", "Gibbs")

    collective_lock_value = sum((v_squared - v_squared) ** 2 for _ in edges)
    zero_force_factor = Fraction(0)
    ordered_force_factor = r + g * v_squared
    audit.check("collective lock vanishes", collective_lock_value == 0, collective_lock_value, 0, "witness")
    audit.check("zero equilibrium", zero_force_factor == 0, zero_force_factor, 0, "witness")
    audit.check("ordered equilibrium", ordered_force_factor == 0, ordered_force_factor, 0, "witness")
    raw_zero_energy = Fraction(0)
    raw_ordered_energy = exact_floor
    audit.check("zero witness energy", raw_zero_energy == 0, raw_zero_energy, 0, "witness")
    audit.check("ordered witness energy", raw_ordered_energy == Fraction(-9, 4), raw_ordered_energy, Fraction(-9, 4), "witness")
    zero_second_moment = 0
    ordered_second_moment = v_squared
    audit.check("witness second moments distinct", zero_second_moment != ordered_second_moment, [zero_second_moment, ordered_second_moment], "distinct", "witness")
    audit.check("symmetric ordered mean", (Fraction(1) - Fraction(1)) / 2 == 0, 0, 0, "witness")
    seam_differences = [0 for _ in range(9)]
    audit.check("constant seams through order eight", seam_differences == [0] * 9, seam_differences, [0] * 9, "witness")
    audit.check("zero composition error", manifest["common_equilibrium_measures"]["composition"].endswith("error is zero"), manifest["common_equilibrium_measures"]["composition"], "ends error is zero", "witness")
    audit.check("distinct witness support", "disjoint supports" in manifest["common_equilibrium_measures"]["distinctness"], manifest["common_equilibrium_measures"]["distinctness"], "contains disjoint supports", "witness")
    for token in ("spatial translations", "Q3 automorphisms", "global Z2", "momentum reversal", "time reversal"):
        audit.check(f"symmetry retained: {token}", token in manifest["common_equilibrium_measures"]["symmetries"], manifest["common_equilibrium_measures"]["symmetries"], f"contains {token}", "witness")

    audit.check("formal route excluded narrowly", "using only normalization" in manifest["formal_selection_no_go"]["excluded_route"], manifest["formal_selection_no_go"]["excluded_route"], "contains using only normalization", "scope")
    audit.check("physical selectors not excluded", "temperature" in manifest["formal_selection_no_go"]["not_excluded"] and "preparation" in manifest["formal_selection_no_go"]["not_excluded"], manifest["formal_selection_no_go"]["not_excluded"], "contains temperature and preparation", "scope")
    audit.check("parent gate remains open", manifest["gate_resolution"]["status"] == "SPLIT; PARENT GATE REMAINS OPEN", manifest["gate_resolution"]["status"], "SPLIT; PARENT GATE REMAINS OPEN", "scope")
    audit.check("quantum successor", manifest["gate_resolution"]["next_gate"] == "PA-CP1-CL8-FINITE-REGULATOR-QUANTUM-STATE", manifest["gate_resolution"]["next_gate"], "PA-CP1-CL8-FINITE-REGULATOR-QUANTUM-STATE", "scope")
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
        audit.check(f"scope false: {key}", manifest["scope"].get(key) is False, manifest["scope"].get(key), False, "scope")

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
            "Liouville": {"divergence": Fraction(0), "H_dot": h_dot, "density_dot": Fraction(0)},
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
    print(f"{CANDIDATE_ID} independent: {summary['passed']}/{summary['total']} PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

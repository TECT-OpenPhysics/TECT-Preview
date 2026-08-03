#!/usr/bin/env python3
"""Primary exact audit for the finite CL8 quantum-state boundary fork."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any

import sympy as sp


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
CANDIDATE_ID = "PA-CP1-CL8-FINITE-QUANTUM-STATE-BOUNDARY-FORK-v0"
PARENT_IDS = (
    "PA-CP1-ST8-Q3LOCK-v0",
    "PA-CP1-CL8-SEMIDISCRETE-CAUCHY-OA2-v0",
    "PA-CP1-CL8-INVARIANCE-SELECTION-FORK-v0",
)
RESULT_ID = "PA-CP1-CL8-FINITE-QUANTUM-GROUND-THERMAL-STATE-AND-BOUNDARY-FORK"
NEGATIVE_ID = "NG-2026-08-03-PRE-A-CP1-CL8-STATIONARITY-ONLY-QUANTUM-STATE"
SLUG = "pre-a-cp1-cl8-finite-quantum-state-boundary-fork"
SCHEMA = f"tect/{SLUG}-primary/0.1"
SCRIPT = Path(__file__).resolve()
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
SEMIDISCRETE = REPO / "strategy/pre-a-cp1-cl8-semidiscrete-cauchy-oa2-manifest.json"
Q3LOCK = REPO / "strategy/pre-a-cp1-st8-q3lock-manifest.json"
CLASSICAL_FORK = REPO / "strategy/pre-a-cp1-cl8-invariance-selection-fork-manifest.json"
GLOBAL = REPO / "strategy/pre-a-cp1-cl8-global-goursat-continuation-manifest.json"
GAUSSIAN_CCR = REPO / "strategy/pre-a-c0a-gaussian-ccr-pah1-embedding-manifest.json"
PRIOR_ART = REPO / "strategy/pre-a-prior-art-novelty-matrix-260803.md"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-03-primary-{SLUG}/result.json"


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
        self.rows.append({"name": name, "group": group, "status": "PASS", "actual": serial(actual), "expected": serial(expected)})


def diagonal(values: list[sp.Expr]) -> sp.Matrix:
    return sp.diag(*values)


def build_payload() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    semidiscrete = json.loads(SEMIDISCRETE.read_text(encoding="utf-8"))
    q3lock = json.loads(Q3LOCK.read_text(encoding="utf-8"))
    classical_fork = json.loads(CLASSICAL_FORK.read_text(encoding="utf-8"))
    global_manifest = json.loads(GLOBAL.read_text(encoding="utf-8"))
    gaussian_ccr = json.loads(GAUSSIAN_CCR.read_text(encoding="utf-8"))
    audit = Audit()

    audit.check("candidate id", manifest["candidate_id"] == CANDIDATE_ID, manifest["candidate_id"], CANDIDATE_ID, "identity")
    audit.check("result id", manifest["result_id"] == RESULT_ID, manifest["result_id"], RESULT_ID, "identity")
    audit.check("parent ids", tuple(manifest["parent_ids"]) == PARENT_IDS, manifest["parent_ids"], PARENT_IDS, "identity")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "identity")
    audit.check("negative id", manifest["formal_selection_no_go"]["negative_id"] == NEGATIVE_ID, manifest["formal_selection_no_go"]["negative_id"], NEGATIVE_ID, "identity")
    audit.check("Q3 parent", q3lock["candidate_id"] == PARENT_IDS[0], q3lock["candidate_id"], PARENT_IDS[0], "parents")
    audit.check("semidiscrete parent", semidiscrete["candidate_id"] == PARENT_IDS[1], semidiscrete["candidate_id"], PARENT_IDS[1], "parents")
    audit.check("classical fork parent", classical_fork["candidate_id"] == PARENT_IDS[2], classical_fork["candidate_id"], PARENT_IDS[2], "parents")
    audit.check("global parent", global_manifest["candidate_id"] == "PA-CP1-CL8-GLOBAL-GOURSAT-CONTINUATION-v0", global_manifest["candidate_id"], "PA-CP1-CL8-GLOBAL-GOURSAT-CONTINUATION-v0", "parents")
    audit.check("Gaussian CCR comparator", gaussian_ccr["candidate_id"] == "PA-C0A-GAUSSIAN-CCR-PAH1-EMBEDDING-v0", gaussian_ccr["candidate_id"], "PA-C0A-GAUSSIAN-CCR-PAH1-EMBEDDING-v0", "parents")
    audit.check("Pre-A chain authority", manifest["authorities"]["Pre_A_chain_definition"] == "strategy/pre-a-prior-art-novelty-matrix-260803.md", manifest["authorities"]["Pre_A_chain_definition"], "strategy/pre-a-prior-art-novelty-matrix-260803.md", "parents")
    audit.check("classical Hamiltonian a/8", semidiscrete["hamiltonian_structure"]["Hamiltonian"].startswith("H_a=(a/8)"), semidiscrete["hamiltonian_structure"]["Hamiltonian"], "starts H_a=(a/8)", "parents")
    audit.check("classical symplectic a/8", semidiscrete["hamiltonian_structure"]["symplectic_form"].startswith("Omega_a=(a/8)"), semidiscrete["hamiltonian_structure"]["symplectic_form"], "starts Omega_a=(a/8)", "parents")

    a, chi, hbar, p, Pi = sp.symbols("a chi hbar p Pi", positive=True, real=True)
    weight = a / 8
    canonical_relation = sp.factor((weight * Pi).subs(Pi, p / weight))
    classical_kinetic = sp.factor(weight * Pi**2 / (2 * chi))
    canonical_kinetic = sp.factor(classical_kinetic.subs(Pi, p / weight))
    kappa = sp.factor(hbar**2 / (2 * chi * weight))
    audit.check("canonical momentum relation", canonical_relation == p, canonical_relation, p, "quantization")
    audit.check("canonical kinetic energy", canonical_kinetic == p**2 / (2 * chi * weight), canonical_kinetic, p**2 / (2 * chi * weight), "quantization")
    audit.check("quantum kinetic coefficient", kappa == 4 * hbar**2 / (a * chi), kappa, 4 * hbar**2 / (a * chi), "quantization")
    audit.check("hbar explicitly inserted", manifest["quantization"]["inserted_constant"] == "hbar>0", manifest["quantization"]["inserted_constant"], "hbar>0", "quantization")
    audit.check("CCR explicitly declared", "[q_i,p_k]" in manifest["quantization"]["CCR"], manifest["quantization"]["CCR"], "contains CCR", "quantization")

    L, M, g, r_minus, mu, s = sp.symbols("L M g r_minus mu s", positive=True, real=True)
    d = 8 * M
    A = sp.factor(a * g / (32 * d))
    B = sp.factor(a * r_minus / 16)
    C_mu = sp.factor((B + mu) ** 2 / (4 * A))
    completion = sp.factor(A * s**2 - B * s - mu * s + C_mu)
    expected_completion = sp.factor(A * (s - (B + mu) / (2 * A)) ** 2)
    audit.check("radial completion", sp.expand(completion - expected_completion) == 0, completion, expected_completion, "coercivity")
    scaling = sp.factor(A.subs(a, L / M))
    audit.check("radial coefficient scaling", scaling == L * g / (256 * M**2), scaling, L * g / (256 * M**2), "coercivity")

    fixture = {L: 2, M: 4, a: sp.Rational(1, 2), chi: 2, hbar: 3, g: 2, r_minus: 3, mu: sp.Rational(1, 32)}
    fixture_d = int(d.subs(fixture))
    fixture_weight = sp.factor(weight.subs(fixture))
    fixture_kappa = sp.factor(kappa.subs(fixture))
    fixture_A = sp.factor(A.subs(fixture))
    fixture_B = sp.factor(B.subs(fixture))
    fixture_C = sp.factor(C_mu.subs(fixture))
    fixture_s0 = sp.factor(((B + mu) / (2 * A)).subs(fixture))
    audit.check("fixture dimension", fixture_d == 32, fixture_d, 32, "fixture")
    audit.check("fixture symplectic weight", fixture_weight == sp.Rational(1, 16), fixture_weight, sp.Rational(1, 16), "fixture")
    audit.check("fixture kinetic coefficient", fixture_kappa == 36, fixture_kappa, 36, "fixture")
    audit.check("fixture radial quartic", fixture_A == sp.Rational(1, 1024), fixture_A, sp.Rational(1, 1024), "fixture")
    audit.check("fixture radial quadratic", fixture_B == sp.Rational(3, 32), fixture_B, sp.Rational(3, 32), "fixture")
    audit.check("fixture harmonic constant", fixture_C == 4, fixture_C, 4, "fixture")
    audit.check("fixture completion minimizer", fixture_s0 == 64, fixture_s0, 64, "fixture")
    audit.check("fixture completion zero", completion.subs(fixture).subs(s, fixture_s0) == 0, completion.subs(fixture).subs(s, fixture_s0), 0, "fixture")

    omega, beta = sp.symbols("omega beta", positive=True, real=True)
    y = sp.symbols("y", positive=True, real=True)
    oscillator_partial = sum(y ** (2 * n + 1) for n in range(6))
    oscillator_partial_closed = sp.factor(y * (1 - y**12) / (1 - y**2))
    audit.check("oscillator geometric partial sum", sp.expand(oscillator_partial - oscillator_partial_closed) == 0, oscillator_partial, oscillator_partial_closed, "heat-trace")
    oscillator_infinite = y / (1 - y**2)
    audit.check("oscillator trace positive fixture", oscillator_infinite.subs(y, sp.Rational(1, 2)) == sp.Rational(2, 3), oscillator_infinite.subs(y, sp.Rational(1, 2)), sp.Rational(2, 3), "heat-trace")
    audit.check("d-dimensional trace product fixture", oscillator_infinite.subs(y, sp.Rational(1, 2)) ** fixture_d == sp.Rational(2, 3) ** 32, oscillator_infinite.subs(y, sp.Rational(1, 2)) ** fixture_d, sp.Rational(2, 3) ** 32, "heat-trace")
    audit.check("heat bound contains shift", "exp(beta C_mu)" in manifest["thermal_state_theorem"]["heat_trace_bound"], manifest["thermal_state_theorem"]["heat_trace_bound"], "contains exp(beta C_mu)", "heat-trace")
    audit.check("compact resolvent not sole heat argument", "harmonic comparison" in manifest["hostile_boundaries"]["compact_resolvent_not_heat_trace"], manifest["hostile_boundaries"]["compact_resolvent_not_heat_trace"], "contains harmonic comparison", "heat-trace")

    energies = diagonal([0, 2, 4])
    ground = diagonal([1, 0, 0])
    boltzmann_ratio = sp.Rational(1, 2)
    raw_thermal = [boltzmann_ratio**level for level in range(3)]
    thermal_weights = [sp.factor(value / sum(raw_thermal)) for value in raw_thermal]
    colder_ratio = sp.Rational(1, 4)
    raw_colder = [colder_ratio**level for level in range(3)]
    colder_weights = [sp.factor(value / sum(raw_colder)) for value in raw_colder]
    thermal = diagonal(thermal_weights)
    thermal_colder = diagonal(colder_weights)
    parity = diagonal([1, 1, -1])
    # For spectral energies (0,2,4), t/hbar=pi/2 gives the exact unitary
    # phases (1,-1,1).  This is distinct from the parity fixture above.
    time_unitary = diagonal([1, -1, 1])
    observable = sp.Matrix([[1, 2, 0], [2, 0, 3], [0, 3, 4]])
    evolved_observable = time_unitary * observable * time_unitary
    audit.check("Gibbs weights derived from one Boltzmann ratio", thermal_weights == [sp.Rational(4, 7), sp.Rational(2, 7), sp.Rational(1, 7)], thermal_weights, [sp.Rational(4, 7), sp.Rational(2, 7), sp.Rational(1, 7)], "spectral")
    audit.check("ground stationary fixture", energies * ground - ground * energies == sp.zeros(3), energies * ground - ground * energies, sp.zeros(3), "spectral")
    audit.check("thermal stationary fixture", energies * thermal - thermal * energies == sp.zeros(3), energies * thermal - thermal * energies, sp.zeros(3), "spectral")
    audit.check("thermal trace one", sp.trace(thermal) == 1, sp.trace(thermal), 1, "spectral")
    audit.check("thermal faithful", all(thermal[i, i] > 0 for i in range(3)), [thermal[i, i] for i in range(3)], "all positive", "spectral")
    audit.check("ground pure", sp.trace(ground * ground) == 1, sp.trace(ground * ground), 1, "spectral")
    audit.check("thermal mixed", sp.trace(thermal * thermal) == sp.Rational(3, 7), sp.trace(thermal * thermal), sp.Rational(3, 7), "spectral")
    audit.check("ground and thermal distinct", ground != thermal, [ground, thermal], "distinct", "spectral")
    audit.check("different beta weights distinct", thermal != thermal_colder, [thermal, thermal_colder], "distinct", "spectral")
    audit.check("ground Z2 even fixture", parity * ground == ground, parity * ground, ground, "spectral")
    audit.check("thermal Z2 symmetric fixture", parity * thermal - thermal * parity == sp.zeros(3), parity * thermal - thermal * parity, sp.zeros(3), "spectral")
    audit.check("ground state invariant under nontrivial alpha fixture", sp.trace(ground * evolved_observable) == sp.trace(ground * observable), sp.trace(ground * evolved_observable), sp.trace(ground * observable), "spectral")
    audit.check("thermal state invariant under nontrivial alpha fixture", sp.trace(thermal * evolved_observable) == sp.trace(thermal * observable), sp.trace(thermal * evolved_observable), sp.trace(thermal * observable), "spectral")
    excited_masses = [sp.factor((x + x**2) / (1 + x + x**2)) for x in (sp.Rational(1, 2), sp.Rational(1, 4), sp.Rational(1, 16))]
    audit.check("zero-temperature excited mass decreases", excited_masses[0] > excited_masses[1] > excited_masses[2] > 0, excited_masses, "strictly decreases to zero", "spectral")
    zeta = sp.symbols("zeta", positive=True, real=True)
    excited_ratio = sp.factor((zeta + zeta**2) / (1 + zeta + zeta**2))
    bound_remainder = sp.factor(2 * zeta - excited_ratio)
    expected_remainder = zeta * (1 + zeta + 2 * zeta**2) / (1 + zeta + zeta**2)
    audit.check("zero-temperature analytic fixture bound", sp.simplify(bound_remainder - expected_remainder) == 0, bound_remainder, expected_remainder, "spectral")
    audit.check("zero-temperature analytic fixture limit", sp.limit(excited_ratio, zeta, 0, dir="+") == 0, sp.limit(excited_ratio, zeta, 0, dir="+"), 0, "spectral")
    audit.check("general trace-norm limit bound declared", "2R_beta/(1+R_beta)" in manifest["thermal_state_theorem"]["zero_temperature_limit"], manifest["thermal_state_theorem"]["zero_temperature_limit"], "contains exact trace-norm ratio", "spectral")

    C_star = sp.factor(2 * r_minus**2 / g)
    operator_shift = sp.factor(L * C_star / 8)
    fixture_shift = sp.factor(operator_shift.subs(fixture))
    raw_weights = [sp.Integer(4), sp.Integer(2), sp.Integer(1)]
    common_factor = sp.symbols("common_factor", positive=True)
    normalized = [sp.factor(value / sum(raw_weights)) for value in raw_weights]
    shifted_normalized = [sp.factor(common_factor * value / sum(common_factor * item for item in raw_weights)) for value in raw_weights]
    audit.check("Goursat operator shift", operator_shift == L * r_minus**2 / (4 * g), operator_shift, L * r_minus**2 / (4 * g), "shift")
    audit.check("fixture operator shift", fixture_shift == sp.Rational(9, 4), fixture_shift, sp.Rational(9, 4), "shift")
    audit.check("normalized Gibbs unchanged by shift", normalized == shifted_normalized, shifted_normalized, normalized, "shift")
    audit.check("ground eigenvectors unchanged by scalar shift", (energies + fixture_shift * sp.eye(3)) * ground - ground * (energies + fixture_shift * sp.eye(3)) == sp.zeros(3), 0, 0, "shift")

    audit.check("ground theorem explicitly conditional", "selection criterion and hbar are declared inputs" in manifest["conditional_ground_selection"]["inserted_status"], manifest["conditional_ground_selection"]["inserted_status"], "criterion and hbar inputs", "scope")
    audit.check("finite ground symmetry boundary", "does not select any one" in manifest["coercive_operator_theorem"]["finite_volume_boundary"], manifest["coercive_operator_theorem"]["finite_volume_boundary"], "does not select one well", "scope")
    audit.check("normal observable algebra declared", manifest["state_algebra"]["observable_algebra"].startswith("B(H_a)"), manifest["state_algebra"]["observable_algebra"], "starts B(H_a)", "scope")
    audit.check("Hilbert space not finite dimensional", "infinite-dimensional" in manifest["state_algebra"]["observable_algebra"], manifest["state_algebra"]["observable_algebra"], "contains infinite-dimensional", "scope")
    audit.check("regular Weyl restriction only", "restriction" in manifest["state_algebra"]["normal_state"], manifest["state_algebra"]["normal_state"], "contains restriction", "scope")
    audit.check("B(H) stationarity automorphism declared", "alpha_t(A)=" in manifest["state_algebra"]["stationarity"], manifest["state_algebra"]["stationarity"], "contains alpha_t", "scope")
    audit.check("Weyl dynamics preservation not claimed", "not proved" in manifest["state_algebra"]["dynamics_boundary"], manifest["state_algebra"]["dynamics_boundary"], "contains not proved", "scope")
    audit.check("coarse translation scope exact", "fine one-site ST8 translation is not claimed" in manifest["coercive_operator_theorem"]["symmetry"], manifest["coercive_operator_theorem"]["symmetry"], "fine translation not claimed", "scope")
    audit.check("parent preferred-state gate remains open", manifest["gate_resolution"]["status"] == "SPLIT; PARENT GATE REMAINS OPEN", manifest["gate_resolution"]["status"], "SPLIT; PARENT GATE REMAINS OPEN", "scope")
    audit.check("next quantum boundary gate", manifest["gate_resolution"]["next_gate"] == "PA-CP1-CL8-QUANTUM-BOUNDARY-ALGEBRA-INTERTWINER", manifest["gate_resolution"]["next_gate"], "PA-CP1-CL8-QUANTUM-BOUNDARY-ALGEBRA-INTERTWINER", "scope")
    required_false = (
        "hbar_origin_derived",
        "stationarity_only_unique_preference",
        "physical_state_criterion_derived",
        "pure_ordered_finite_phase",
        "quantum_boundary_algebra_map",
        "quantum_characteristic_state",
        "continuum_quantum_state",
        "Hadamard_state",
        "cutoff_uniform_trace_bound",
        "thermodynamic_limit",
        "physical_vacuum",
        "below_empty_space",
        "C6_claim_advanced",
        "CP1_complete",
        "Pre_A_complete",
    )
    for key in required_false:
        audit.check(f"scope false: {key}", manifest["scope"][key] is False, manifest["scope"][key], False, "scope")

    derived = {
        "dimensions": {"configuration": "8*M"},
        "quantization": {"weight": "a/8", "canonical_momentum": "p=(a/8)*Pi", "kappa": "4*hbar^2/(a*chi)"},
        "coercivity": {"A": "a*g/(32*d)", "B": "a*r_minus/16", "C_mu": "(B+mu)^2/(4*A)", "cutoff_scaling": "L*g/(256*M^2)"},
        "fixture": {"d": fixture_d, "weight": fixture_weight, "kappa": fixture_kappa, "A": fixture_A, "B": fixture_B, "C_mu": fixture_C, "s0": fixture_s0},
        "heat_trace": {"one_dimensional": "exp(-beta*omega)/(1-exp(-2*beta*omega))", "dimension": "d", "fixture_factor": sp.Rational(2, 3) ** 32},
        "spectral_fixture": {"ground_weights": [1, 0, 0], "thermal_weights": [sp.Rational(4, 7), sp.Rational(2, 7), sp.Rational(1, 7)], "thermal_purity": sp.Rational(3, 7), "stationary": True, "symmetric": True, "distinct": True},
        "shift": {"operator": "L*C_star/8=L*r_minus^2/(4*g)", "fixture": fixture_shift, "normalized_states_unchanged": True},
        "negative_id": NEGATIVE_ID,
    }
    return {
        "schema": SCHEMA,
        "candidate_id": CANDIDATE_ID,
        "parent_ids": list(PARENT_IDS),
        "result_id": RESULT_ID,
        "task_id": "T-054",
        "claim_context": "C6-SPACETIME-SIGNATURE",
        "claim_bearing": False,
        "verdict": manifest["verdict"],
        "derived": derived,
        "source_sha256": {
            "script": sha256(SCRIPT),
            "manifest": sha256(MANIFEST),
            "semidiscrete_manifest": sha256(SEMIDISCRETE),
            "q3lock_manifest": sha256(Q3LOCK),
            "classical_fork_manifest": sha256(CLASSICAL_FORK),
            "global_manifest": sha256(GLOBAL),
            "gaussian_ccr_manifest": sha256(GAUSSIAN_CCR),
            "prior_art_matrix": sha256(PRIOR_ART),
        },
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

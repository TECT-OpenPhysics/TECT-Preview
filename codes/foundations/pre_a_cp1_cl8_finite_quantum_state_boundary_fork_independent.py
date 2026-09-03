#!/usr/bin/env python3
"""Independent rational audit for the finite CL8 quantum-state fork."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


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
SCHEMA = f"tect/{SLUG}-independent/0.1"
SCRIPT = Path(__file__).resolve()
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
SEMIDISCRETE = REPO / "strategy/pre-a-cp1-cl8-semidiscrete-cauchy-oa2-manifest.json"
Q3LOCK = REPO / "strategy/pre-a-cp1-st8-q3lock-manifest.json"
CLASSICAL_FORK = REPO / "strategy/pre-a-cp1-cl8-invariance-selection-fork-manifest.json"
GLOBAL = REPO / "strategy/pre-a-cp1-cl8-global-goursat-continuation-manifest.json"
GAUSSIAN_CCR = REPO / "strategy/pre-a-c0a-gaussian-ccr-pah1-embedding-manifest.json"
PRIOR_ART = REPO / "strategy/pre-a-prior-art-novelty-matrix-260803.md"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-03-independent-{SLUG}/result.json"


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
        self.rows.append({"name": name, "group": group, "status": "PASS", "actual": serial(actual), "expected": serial(expected)})


def diagonal(values: list[Fraction]) -> list[list[Fraction]]:
    return [[value if i == j else Fraction(0) for j, _ in enumerate(values)] for i, value in enumerate(values)]


def matmul(left: list[list[Fraction]], right: list[list[Fraction]]) -> list[list[Fraction]]:
    size = len(left)
    return [[sum(left[i][k] * right[k][j] for k in range(size)) for j in range(size)] for i in range(size)]


def matsub(left: list[list[Fraction]], right: list[list[Fraction]]) -> list[list[Fraction]]:
    return [[a - b for a, b in zip(left_row, right_row)] for left_row, right_row in zip(left, right)]


def transpose(matrix: list[list[Fraction]]) -> list[list[Fraction]]:
    return [list(column) for column in zip(*matrix)]


def conjugate(orthogonal: list[list[Fraction]], diagonal_matrix: list[list[Fraction]]) -> list[list[Fraction]]:
    return matmul(matmul(orthogonal, diagonal_matrix), transpose(orthogonal))


def trace(matrix: list[list[Fraction]]) -> Fraction:
    return sum(matrix[i][i] for i in range(len(matrix)))


def build_payload() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    semidiscrete = json.loads(SEMIDISCRETE.read_text(encoding="utf-8"))
    q3lock = json.loads(Q3LOCK.read_text(encoding="utf-8"))
    classical_fork = json.loads(CLASSICAL_FORK.read_text(encoding="utf-8"))
    global_manifest = json.loads(GLOBAL.read_text(encoding="utf-8"))
    gaussian_ccr = json.loads(GAUSSIAN_CCR.read_text(encoding="utf-8"))
    audit = Audit()

    audit.check("candidate id", manifest.get("candidate_id") == CANDIDATE_ID, manifest.get("candidate_id"), CANDIDATE_ID, "identity")
    audit.check("result id", manifest.get("result_id") == RESULT_ID, manifest.get("result_id"), RESULT_ID, "identity")
    audit.check("parent ids", tuple(manifest.get("parent_ids", [])) == PARENT_IDS, manifest.get("parent_ids"), PARENT_IDS, "identity")
    audit.check("claim nonbearing", manifest.get("claim_bearing") is False, manifest.get("claim_bearing"), False, "identity")
    audit.check("negative id", manifest["formal_selection_no_go"]["negative_id"] == NEGATIVE_ID, manifest["formal_selection_no_go"]["negative_id"], NEGATIVE_ID, "identity")
    audit.check("Q3 parent", q3lock["candidate_id"] == PARENT_IDS[0], q3lock["candidate_id"], PARENT_IDS[0], "parents")
    audit.check("semidiscrete parent", semidiscrete["candidate_id"] == PARENT_IDS[1], semidiscrete["candidate_id"], PARENT_IDS[1], "parents")
    audit.check("classical fork parent", classical_fork["candidate_id"] == PARENT_IDS[2], classical_fork["candidate_id"], PARENT_IDS[2], "parents")
    audit.check("global parent", global_manifest["candidate_id"] == "PA-CP1-CL8-GLOBAL-GOURSAT-CONTINUATION-v0", global_manifest["candidate_id"], "PA-CP1-CL8-GLOBAL-GOURSAT-CONTINUATION-v0", "parents")
    audit.check("Gaussian CCR parent", gaussian_ccr["candidate_id"] == "PA-C0A-GAUSSIAN-CCR-PAH1-EMBEDDING-v0", gaussian_ccr["candidate_id"], "PA-C0A-GAUSSIAN-CCR-PAH1-EMBEDDING-v0", "parents")
    audit.check("Pre-A chain authority", manifest["authorities"]["Pre_A_chain_definition"] == "strategy/pre-a-prior-art-novelty-matrix-260803.md", manifest["authorities"]["Pre_A_chain_definition"], "strategy/pre-a-prior-art-novelty-matrix-260803.md", "parents")
    audit.check("Hamiltonian weight parsed", "H_a=(a/8)" in semidiscrete["hamiltonian_structure"]["Hamiltonian"], semidiscrete["hamiltonian_structure"]["Hamiltonian"], "contains H_a=(a/8)", "parents")
    audit.check("symplectic weight parsed", "Omega_a=(a/8)" in semidiscrete["hamiltonian_structure"]["symplectic_form"], semidiscrete["hamiltonian_structure"]["symplectic_form"], "contains Omega_a=(a/8)", "parents")

    # Declared rational regression inputs.
    L = Fraction(2)
    M = 4
    a = L / M
    d = 8 * M
    chi = Fraction(2)
    hbar = Fraction(3)
    g = Fraction(2)
    r_minus = Fraction(3)
    mu = Fraction(1, 32)
    weight = a / 8
    kappa_from_weight = hbar * hbar / (2 * chi * weight)
    kappa_from_a = 4 * hbar * hbar / (a * chi)
    audit.check("fixture spacing", a == Fraction(1, 2), a, Fraction(1, 2), "quantization")
    audit.check("fixture dimension", d == 32, d, 32, "quantization")
    audit.check("fixture weight", weight == Fraction(1, 16), weight, Fraction(1, 16), "quantization")
    audit.check("kinetic coefficient two routes", kappa_from_weight == kappa_from_a, [kappa_from_weight, kappa_from_a], "equal", "quantization")
    audit.check("fixture kinetic coefficient", kappa_from_a == 36, kappa_from_a, 36, "quantization")
    canonical_p = weight * Fraction(48)
    recovered_Pi = canonical_p / weight
    audit.check("canonical momentum invertible fixture", recovered_Pi == 48, recovered_Pi, 48, "quantization")
    classical_kinetic = weight * recovered_Pi * recovered_Pi / (2 * chi)
    canonical_kinetic = canonical_p * canonical_p / (2 * chi * weight)
    audit.check("classical and canonical kinetic fixtures", classical_kinetic == canonical_kinetic, [classical_kinetic, canonical_kinetic], "equal", "quantization")
    audit.check("hbar declared input", manifest["quantization"]["inserted_constant"] == "hbar>0", manifest["quantization"]["inserted_constant"], "hbar>0", "quantization")
    audit.check("CCR representation declared", "p_i=-i*hbar" in manifest["quantization"]["CCR"], manifest["quantization"]["CCR"], "contains p representation", "quantization")

    # Derive the radial constants independently from the original onsite
    # coefficients w*g/4 and -w*r_minus/2.
    onsite_quartic = weight * g / 4
    onsite_negative_quadratic = weight * r_minus / 2
    A = onsite_quartic / d
    B = onsite_negative_quadratic
    C_mu = (B + mu) * (B + mu) / (4 * A)
    s0 = (B + mu) / (2 * A)
    audit.check("fixture radial A", A == Fraction(1, 1024), A, Fraction(1, 1024), "coercivity")
    audit.check("fixture radial B", B == Fraction(3, 32), B, Fraction(3, 32), "coercivity")
    audit.check("fixture C_mu", C_mu == 4, C_mu, 4, "coercivity")
    audit.check("fixture radial minimizer", s0 == 64, s0, 64, "coercivity")
    completion_values = []
    for s in (Fraction(0), Fraction(1), s0, Fraction(100)):
        left = A * s * s - B * s - mu * s + C_mu
        right = A * (s - s0) * (s - s0)
        completion_values.append((s, left, right))
    audit.check("radial completion independent samples", all(left == right for _, left, right in completion_values), completion_values, "left=right", "coercivity")
    audit.check("radial completion nonnegative", all(left >= 0 for _, left, _ in completion_values), completion_values, "nonnegative", "coercivity")
    cutoff_scaling = L * g / (256 * M * M)
    audit.check("cutoff scaling equals A", cutoff_scaling == A, cutoff_scaling, A, "coercivity")

    y = Fraction(1, 2)
    partial_direct = sum(y ** (2 * n + 1) for n in range(6))
    partial_formula = y * (1 - y**12) / (1 - y**2)
    one_dimensional_trace = y / (1 - y**2)
    d_trace = one_dimensional_trace**d
    audit.check("oscillator partial geometric sum", partial_direct == partial_formula, partial_direct, partial_formula, "heat-trace")
    audit.check("one-dimensional heat fixture", one_dimensional_trace == Fraction(2, 3), one_dimensional_trace, Fraction(2, 3), "heat-trace")
    audit.check("d-dimensional heat fixture", d_trace == Fraction(2, 3) ** 32, d_trace, Fraction(2, 3) ** 32, "heat-trace")
    audit.check("heat trace beta positive", "for every beta>0" in manifest["thermal_state_theorem"]["heat_trace_bound"], manifest["thermal_state_theorem"]["heat_trace_bound"], "contains beta>0", "heat-trace")
    audit.check("harmonic comparison owner", "harmonic comparison" in manifest["hostile_boundaries"]["compact_resolvent_not_heat_trace"], manifest["hostile_boundaries"]["compact_resolvent_not_heat_trace"], "contains harmonic comparison", "heat-trace")

    # Independent non-diagonal spectral fixture: conjugate the spectral data by
    # an exact rational orthogonal matrix instead of reusing the primary
    # diagonal representation.
    orthogonal = [
        [Fraction(3, 5), Fraction(-4, 13), Fraction(48, 65)],
        [Fraction(4, 5), Fraction(3, 13), Fraction(-36, 65)],
        [Fraction(0), Fraction(12, 13), Fraction(5, 13)],
    ]
    identity = diagonal([Fraction(1), Fraction(1), Fraction(1)])
    audit.check("rational rotation orthogonal", matmul(orthogonal, transpose(orthogonal)) == identity, matmul(orthogonal, transpose(orthogonal)), identity, "spectral")
    energies = conjugate(orthogonal, diagonal([Fraction(0), Fraction(2), Fraction(4)]))
    ground = conjugate(orthogonal, diagonal([Fraction(1), Fraction(0), Fraction(0)]))
    boltzmann_ratio = Fraction(1, 2)
    raw = [boltzmann_ratio**level for level in range(3)]
    colder_ratio = Fraction(1, 4)
    raw_colder = [colder_ratio**level for level in range(3)]
    thermal_weights = [value / sum(raw) for value in raw]
    colder_weights = [value / sum(raw_colder) for value in raw_colder]
    thermal = conjugate(orthogonal, diagonal(thermal_weights))
    colder = conjugate(orthogonal, diagonal(colder_weights))
    parity = conjugate(orthogonal, diagonal([Fraction(1), Fraction(1), Fraction(-1)]))
    # For spectral energies (0,2,4), t/hbar=pi/2 gives the exact unitary
    # phases (1,-1,1), rationally conjugated into this non-diagonal basis.
    time_unitary = conjugate(orthogonal, diagonal([Fraction(1), Fraction(-1), Fraction(1)]))
    zero_matrix = diagonal([Fraction(0), Fraction(0), Fraction(0)])
    audit.check("rotated Hamiltonian genuinely non-diagonal", any(energies[i][j] != 0 for i in range(3) for j in range(3) if i != j), energies, "has nonzero off-diagonal entry", "spectral")
    audit.check("Gibbs weights independently derived", thermal_weights == [Fraction(4, 7), Fraction(2, 7), Fraction(1, 7)], thermal_weights, [Fraction(4, 7), Fraction(2, 7), Fraction(1, 7)], "spectral")
    audit.check("ground commutator", matsub(matmul(energies, ground), matmul(ground, energies)) == zero_matrix, matsub(matmul(energies, ground), matmul(ground, energies)), zero_matrix, "spectral")
    audit.check("thermal commutator", matsub(matmul(energies, thermal), matmul(thermal, energies)) == zero_matrix, matsub(matmul(energies, thermal), matmul(thermal, energies)), zero_matrix, "spectral")
    audit.check("thermal normalized", trace(thermal) == 1, trace(thermal), 1, "spectral")
    audit.check("thermal faithful", all(value > 0 for value in thermal_weights), thermal_weights, "all positive", "spectral")
    audit.check("ground purity", trace(matmul(ground, ground)) == 1, trace(matmul(ground, ground)), 1, "spectral")
    thermal_purity = trace(matmul(thermal, thermal))
    audit.check("thermal purity", thermal_purity == Fraction(3, 7), thermal_purity, Fraction(3, 7), "spectral")
    audit.check("ground thermal distinct", ground != thermal, [ground, thermal], "distinct", "spectral")
    audit.check("temperature weights distinct", thermal != colder, [thermal, colder], "distinct", "spectral")
    audit.check("ground parity evenness", matmul(parity, ground) == ground, matmul(parity, ground), ground, "spectral")
    audit.check("thermal parity commutator", matsub(matmul(parity, thermal), matmul(thermal, parity)) == zero_matrix, matsub(matmul(parity, thermal), matmul(thermal, parity)), zero_matrix, "spectral")
    observable = [
        [Fraction(1), Fraction(2), Fraction(0)],
        [Fraction(2), Fraction(0), Fraction(3)],
        [Fraction(0), Fraction(3), Fraction(4)],
    ]
    evolved_observable = matmul(matmul(time_unitary, observable), time_unitary)
    audit.check("ground normal state alpha invariance", trace(matmul(ground, evolved_observable)) == trace(matmul(ground, observable)), trace(matmul(ground, evolved_observable)), trace(matmul(ground, observable)), "spectral")
    audit.check("thermal normal state alpha invariance", trace(matmul(thermal, evolved_observable)) == trace(matmul(thermal, observable)), trace(matmul(thermal, evolved_observable)), trace(matmul(thermal, observable)), "spectral")
    excited_masses = []
    for x in (Fraction(1, 2), Fraction(1, 4), Fraction(1, 16)):
        excited_masses.append((x + x * x) / (1 + x + x * x))
    audit.check("zero-temperature control decreases", excited_masses[0] > excited_masses[1] > excited_masses[2] > 0, excited_masses, "strictly decreases", "spectral")
    bound_samples = []
    for x in (Fraction(1, 2), Fraction(1, 4), Fraction(1, 16)):
        ratio = (x + x * x) / (1 + x + x * x)
        left = 2 * x - ratio
        right = x * (1 + x + 2 * x * x) / (1 + x + x * x)
        bound_samples.append((x, left, right))
    audit.check("zero-temperature exact bound identity", all(left == right and left > 0 for _, left, right in bound_samples), bound_samples, "positive exact identity", "spectral")
    audit.check("general trace-norm limit bound parsed", "2R_beta/(1+R_beta)" in manifest["thermal_state_theorem"]["zero_temperature_limit"], manifest["thermal_state_theorem"]["zero_temperature_limit"], "contains exact trace-norm ratio", "spectral")

    C_star = 2 * r_minus * r_minus / g
    operator_shift = L * C_star / 8
    common_factor = Fraction(5)
    shifted_weights = [common_factor * value / sum(common_factor * item for item in raw) for value in raw]
    audit.check("fixture C_star", C_star == 9, C_star, 9, "shift")
    audit.check("fixture operator shift", operator_shift == Fraction(9, 4), operator_shift, Fraction(9, 4), "shift")
    audit.check("normalized thermal unchanged", shifted_weights == thermal_weights, shifted_weights, thermal_weights, "shift")
    shifted_energies = [
        [energies[i][j] + (operator_shift if i == j else 0) for j in range(3)]
        for i in range(3)
    ]
    audit.check("ground commutes after scalar shift", matsub(matmul(shifted_energies, ground), matmul(ground, shifted_energies)) == zero_matrix, matsub(matmul(shifted_energies, ground), matmul(ground, shifted_energies)), zero_matrix, "shift")

    audit.check("finite ground criterion is input", "declared inputs" in manifest["conditional_ground_selection"]["inserted_status"], manifest["conditional_ground_selection"]["inserted_status"], "contains declared inputs", "scope")
    audit.check("finite ground is Z2 even", "Z2 even" in manifest["conditional_ground_selection"]["ordered_phase_boundary"], manifest["conditional_ground_selection"]["ordered_phase_boundary"], "contains Z2 even", "scope")
    audit.check("normal observable algebra declared", manifest["state_algebra"]["observable_algebra"].startswith("B(H_a)"), manifest["state_algebra"]["observable_algebra"], "starts B(H_a)", "scope")
    audit.check("Hilbert space not finite dimensional", "infinite-dimensional" in manifest["state_algebra"]["observable_algebra"], manifest["state_algebra"]["observable_algebra"], "contains infinite-dimensional", "scope")
    audit.check("regular Weyl restriction only", "restriction" in manifest["state_algebra"]["normal_state"], manifest["state_algebra"]["normal_state"], "contains restriction", "scope")
    audit.check("B(H) stationarity automorphism declared", "alpha_t(A)=" in manifest["state_algebra"]["stationarity"], manifest["state_algebra"]["stationarity"], "contains alpha_t", "scope")
    audit.check("Weyl dynamics preservation not claimed", "not proved" in manifest["state_algebra"]["dynamics_boundary"], manifest["state_algebra"]["dynamics_boundary"], "contains not proved", "scope")
    audit.check("coarse translation scope exact", "fine one-site ST8 translation is not claimed" in manifest["coercive_operator_theorem"]["symmetry"], manifest["coercive_operator_theorem"]["symmetry"], "fine translation not claimed", "scope")
    audit.check("position marginal boundary", "not an invariant positive classical phase-space measure" in manifest["boundary_composition_fork"]["position_marginal_boundary"], manifest["boundary_composition_fork"]["position_marginal_boundary"], "not classical phase measure", "scope")
    audit.check("classical map not quantum star map", "not a quantum star-homomorphism" in manifest["boundary_composition_fork"]["classical_map_boundary"], manifest["boundary_composition_fork"]["classical_map_boundary"], "not star map", "scope")
    audit.check("cutoff nonuniformity explicit", "L*g/(256M^2)" in manifest["boundary_composition_fork"]["nonuniformity"], manifest["boundary_composition_fork"]["nonuniformity"], "contains cutoff scaling", "scope")
    audit.check("parent gate remains open", manifest["gate_resolution"]["status"] == "SPLIT; PARENT GATE REMAINS OPEN", manifest["gate_resolution"]["status"], "SPLIT; PARENT GATE REMAINS OPEN", "scope")
    audit.check("next gate boundary algebra", manifest["gate_resolution"]["next_gate"] == "PA-CP1-CL8-QUANTUM-BOUNDARY-ALGEBRA-INTERTWINER", manifest["gate_resolution"]["next_gate"], "PA-CP1-CL8-QUANTUM-BOUNDARY-ALGEBRA-INTERTWINER", "scope")
    required_true = (
        "finite_quantum_CCR_declared",
        "finite_quantum_self_adjoint_operator",
        "finite_quantum_compact_resolvent",
        "finite_quantum_unique_ground",
        "finite_quantum_thermal_Gibbs",
        "ground_selected_given_criterion",
    )
    for key in required_true:
        audit.check(f"scope true: {key}", manifest["scope"].get(key) is True, manifest["scope"].get(key), True, "scope")
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
        audit.check(f"scope false: {key}", manifest["scope"].get(key) is False, manifest["scope"].get(key), False, "scope")

    derived = {
        "dimensions": {"configuration": "8*M"},
        "quantization": {"weight": "a/8", "canonical_momentum": "p=(a/8)*Pi", "kappa": "4*hbar^2/(a*chi)"},
        "coercivity": {"A": "a*g/(32*d)", "B": "a*r_minus/16", "C_mu": "(B+mu)^2/(4*A)", "cutoff_scaling": "L*g/(256*M^2)"},
        "fixture": {"d": d, "weight": weight, "kappa": kappa_from_a, "A": A, "B": B, "C_mu": C_mu, "s0": s0},
        "heat_trace": {"one_dimensional": "exp(-beta*omega)/(1-exp(-2*beta*omega))", "dimension": "d", "fixture_factor": d_trace},
        "spectral_fixture": {"ground_weights": [1, 0, 0], "thermal_weights": thermal_weights, "thermal_purity": thermal_purity, "stationary": True, "symmetric": True, "distinct": True},
        "shift": {"operator": "L*C_star/8=L*r_minus^2/(4*g)", "fixture": operator_shift, "normalized_states_unchanged": True},
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
    print(f"{CANDIDATE_ID} independent: {summary['passed']}/{summary['total']} PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

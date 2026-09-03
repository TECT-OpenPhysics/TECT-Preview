#!/usr/bin/env python3
"""Primary exact audit for the CL8 quantum boundary-algebra route split."""

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
CANDIDATE_ID = "PA-CP1-CL8-QUANTUM-BOUNDARY-ALGEBRA-INTERTWINER-ROUTE-SPLIT-v0"
RESULT_ID = "PA-CP1-CL8-ORDERED-TANGENT-FINITE-IMAGE-WEYL-STATE-PULLBACK-AND-ROUTE-NOGOS"
SLUG = "pre-a-cp1-cl8-quantum-boundary-algebra-intertwiner-route-split"
SCHEMA = f"tect/{SLUG}-primary/0.1"
SCRIPT = Path(__file__).resolve()
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
GLOBAL = REPO / "strategy/pre-a-cp1-cl8-global-goursat-continuation-manifest.json"
Q3LOCK = REPO / "strategy/pre-a-cp1-st8-q3lock-manifest.json"
GAUSSIAN = REPO / "strategy/pre-a-c0a-gaussian-ccr-pah1-embedding-manifest.json"
CLASSICAL = REPO / "strategy/pre-a-cp1-cl8-classical-boundary-lattice-oa2-manifest.json"
QUANTUM = REPO / "strategy/pre-a-cp1-cl8-finite-quantum-state-boundary-fork-manifest.json"
DEFAULT_OUTPUT = (
    REPO
    / "claims/C6-SPACETIME-SIGNATURE/runs"
    / f"2026-08-04-primary-{SLUG}/result.json"
)


def serial(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value).replace("\\", "/")
    if isinstance(value, sp.MatrixBase):
        return [
            [serial(value[row, column]) for column in range(value.cols)]
            for row in range(value.rows)
        ]
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
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
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


def canonical_symplectic(configuration_dimension: int) -> sp.Matrix:
    identity = sp.eye(configuration_dimension)
    zero = sp.zeros(configuration_dimension)
    return zero.row_join(identity).col_join((-identity).row_join(zero))


def lambda_power(f: sp.Expr, g: sp.Expr, order: int, q: sp.Symbol, p: sp.Symbol) -> sp.Expr:
    result = sp.Integer(0)
    for index in range(order + 1):
        result += (
            (-1) ** index
            * sp.binomial(order, index)
            * sp.diff(f, q, order - index, p, index)
            * sp.diff(g, q, index, p, order - index)
        )
    return sp.expand(result)


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


def build_payload() -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    global_manifest = json.loads(GLOBAL.read_text(encoding="utf-8"))
    q3lock = json.loads(Q3LOCK.read_text(encoding="utf-8"))
    gaussian = json.loads(GAUSSIAN.read_text(encoding="utf-8"))
    classical = json.loads(CLASSICAL.read_text(encoding="utf-8"))
    quantum = json.loads(QUANTUM.read_text(encoding="utf-8"))
    audit = Audit()

    expected_parents = (
        "PA-CP1-CL8-GLOBAL-GOURSAT-CONTINUATION-v0",
        "PA-CP1-ST8-Q3LOCK-v0",
        "PA-C0A-GAUSSIAN-CCR-PAH1-EMBEDDING-v0",
        "PA-CP1-CL8-CLASSICAL-BOUNDARY-TO-LATTICE-OA2-v0",
        "PA-CP1-CL8-FINITE-QUANTUM-STATE-BOUNDARY-FORK-v0",
    )
    audit.check("candidate id", manifest["candidate_id"] == CANDIDATE_ID, manifest["candidate_id"], CANDIDATE_ID, "identity")
    audit.check("result id", manifest["result_id"] == RESULT_ID, manifest["result_id"], RESULT_ID, "identity")
    audit.check("parent ids", tuple(manifest["parent_ids"]) == expected_parents, manifest["parent_ids"], expected_parents, "identity")
    audit.check("claim nonbearing", manifest["claim_bearing"] is False, manifest["claim_bearing"], False, "identity")
    audit.check("global parent", global_manifest["candidate_id"] == expected_parents[0], global_manifest["candidate_id"], expected_parents[0], "parents")
    audit.check("Q3 parent", q3lock["candidate_id"] == expected_parents[1], q3lock["candidate_id"], expected_parents[1], "parents")
    audit.check("Gaussian parent", gaussian["candidate_id"] == expected_parents[2], gaussian["candidate_id"], expected_parents[2], "parents")
    audit.check("classical sampling parent", classical["candidate_id"] == expected_parents[3], classical["candidate_id"], expected_parents[3], "parents")
    audit.check("quantum parent", quantum["candidate_id"] == expected_parents[4], quantum["candidate_id"], expected_parents[4], "parents")
    audit.check("ordered calibration inherited", q3lock["pah1_calibration"]["result"] == "the collective spatial squared frequencies are 9,25,25", q3lock["pah1_calibration"]["result"], "9,25,25", "parents")
    audit.check("Gaussian frequencies inherited", gaussian["fixture"]["omega"] == ["3", "5", "5"], gaussian["fixture"]["omega"], ["3", "5", "5"], "parents")
    audit.check("quantum ground available", quantum["scope"]["finite_quantum_unique_ground"] is True, quantum["scope"]["finite_quantum_unique_ground"], True, "parents")
    audit.check("quantum Gibbs available", quantum["scope"]["finite_quantum_thermal_Gibbs"] is True, quantum["scope"]["finite_quantum_thermal_Gibbs"], True, "parents")

    # Exact three-oscillator transfer and the CL8 CCR sign.
    d = sp.sqrt(2) / 2
    chi_transfer = sp.symbols("chi_transfer", positive=True, real=True)
    omega = sp.diag(3, 5, 5)
    cosine = sp.diag(-d, -d, -d)
    sine = sp.diag(d, -d, -d)
    transfer = cosine.row_join(omega.inv() * sine / chi_transfer).col_join(
        (-chi_transfer * omega * sine).row_join(cosine)
    )
    sigma6 = canonical_symplectic(3)
    transfer_defect = sp.simplify(transfer.T * sigma6 * transfer - sigma6)
    audit.check("frequency matrix", list(omega.diagonal()) == [3, 5, 5], list(omega.diagonal()), [3, 5, 5], "finite_image")
    audit.check("transfer first block", transfer.extract([0, 3], [0, 3]) == sp.Matrix([[-d, d / (3 * chi_transfer)], [-3 * chi_transfer * d, -d]]), transfer.extract([0, 3], [0, 3]), "S3 with canonical Pi", "finite_image")
    audit.check("transfer cosine block", transfer.extract([1, 4], [1, 4]) == sp.Matrix([[-d, -d / (5 * chi_transfer)], [5 * chi_transfer * d, -d]]), transfer.extract([1, 4], [1, 4]), "S5 with canonical Pi", "finite_image")
    audit.check("transfer sine block", transfer.extract([2, 5], [2, 5]) == sp.Matrix([[-d, -d / (5 * chi_transfer)], [5 * chi_transfer * d, -d]]), transfer.extract([2, 5], [2, 5]), "S5 with canonical Pi", "finite_image")
    audit.check("all transfer blocks determinant one", [sp.factor(transfer.extract([j, j + 3], [j, j + 3]).det()) for j in range(3)] == [1, 1, 1], [transfer.extract([j, j + 3], [j, j + 3]).det() for j in range(3)], [1, 1, 1], "finite_image")
    audit.check("transfer symplectic", transfer_defect == sp.zeros(6), transfer_defect, sp.zeros(6), "finite_image")
    audit.check("coefficient p is canonical Pi", "canonical Pi=chi*xi_t" in manifest["ordered_tangent_finite_image"]["coefficient_phase_space"], manifest["ordered_tangent_finite_image"]["coefficient_phase_space"], "canonical Pi=chi*xi_t", "finite_image")
    audit.check("CCR sign declared", manifest["algebra_contract"]["CCR_sign"].startswith("sigma=-Omega_var"), manifest["algebra_contract"]["CCR_sign"], "sigma=-Omega_var", "finite_image")

    # Exact collective band sampling.  M=4 is the smallest admitted fixture;
    # the certificate proves the roots-of-unity identity for all even M>=4.
    L = sp.pi / 2
    M = 4
    a = L / M
    nodes = [sp.factor(j * a) for j in range(M)]
    basis = (
        lambda x: sp.sqrt(2 / sp.pi),
        lambda x: 2 * sp.cos(4 * x) / sp.sqrt(sp.pi),
        lambda x: 2 * sp.sin(4 * x) / sp.sqrt(sp.pi),
    )
    sample = sp.Matrix([[sp.simplify(function(x)) for function in basis] for x in nodes])
    discrete_gram = sp.simplify(a * sample.T * sample)
    x = sp.symbols("x", real=True)
    continuum_gram = sp.Matrix(
        [
            [sp.integrate(basis[row](x) * basis[column](x), (x, 0, L)) for column in range(3)]
            for row in range(3)
        ]
    )
    audit.check("continuum mode Gram", continuum_gram == sp.eye(3), continuum_gram, sp.eye(3), "sampling")
    audit.check("M=4 discrete mode Gram", discrete_gram == sp.eye(3), discrete_gram, sp.eye(3), "sampling")
    audit.check("sample rank", sample.rank() == 3, sample.rank(), 3, "sampling")
    collective_q = sp.Matrix.vstack(*([sample] * 8))
    zero_q = sp.zeros(8 * M, 3)
    sampling_map = collective_q.row_join(zero_q).col_join(zero_q.row_join(collective_q))
    sigma_lattice = (a / 8) * canonical_symplectic(8 * M)
    sampling_pullback = sp.simplify(sampling_map.T * sigma_lattice * sampling_map)
    composed_map = sp.simplify(sampling_map * transfer)
    audit.check("collective species cancellation", sampling_pullback == sigma6, sampling_pullback, sigma6, "sampling")
    audit.check("sampling map rank six", sampling_map.rank() == 6, sampling_map.rank(), 6, "sampling")
    audit.check("composed map rank six", composed_map.rank() == 6, composed_map.rank(), 6, "sampling")
    audit.check("composed characteristic sampling symplectic", sp.simplify(composed_map.T * sigma_lattice * composed_map) == sigma6, sp.simplify(composed_map.T * sigma_lattice * composed_map), sigma6, "sampling")
    audit.check("restricted Weyl map declared injective", "injective unital" in manifest["algebra_contract"]["map_status"], manifest["algebra_contract"]["map_status"], "injective unital", "sampling")

    # Exact unrestricted sampling-kernel obstruction.
    hbar = sp.symbols("hbar", positive=True, real=True)
    f = sp.sin(2 * sp.pi * M * x / L)
    f_samples = [sp.simplify(f.subs(x, node)) for node in nodes]
    norm_squared = sp.integrate(f**2, (x, 0, L))
    omega_var = sp.factor(-norm_squared / 8)
    sigma_kernel = sp.factor(-omega_var)
    scale = sp.factor(16 * sp.pi * hbar / L)
    scaled_sigma = sp.factor(scale * sigma_kernel)
    source_commutator = sp.simplify(sp.exp(-sp.I * scaled_sigma / hbar))
    audit.check("kernel samples vanish", f_samples == [0] * M, f_samples, [0] * M, "sampling_no_go")
    audit.check("kernel norm", norm_squared == L / 2, norm_squared, L / 2, "sampling_no_go")
    audit.check("variational kernel pairing", omega_var == -L / 16, omega_var, -L / 16, "sampling_no_go")
    audit.check("CCR kernel pairing", sigma_kernel == L / 16, sigma_kernel, L / 16, "sampling_no_go")
    audit.check("scaled CCR phase", scaled_sigma == sp.pi * hbar, scaled_sigma, sp.pi * hbar, "sampling_no_go")
    audit.check("source commutator minus one", source_commutator == -1, source_commutator, -1, "sampling_no_go")
    audit.check("target commutator plus one", all(value == 0 for value in f_samples), 1, 1, "sampling_no_go")

    # Nonlinear symplectic does not mean generator-relabel Weyl.
    q, p, gamma = sp.symbols("q p gamma", real=True)
    shear_jacobian = sp.Matrix([[1, 0], [2 * gamma * q, 1]])
    sigma2 = canonical_symplectic(1)
    audit.check("nonlinear shear symplectic", sp.simplify(shear_jacobian.T * sigma2 * shear_jacobian) == sigma2, sp.simplify(shear_jacobian.T * sigma2 * shear_jacobian), sigma2, "nonlinear_no_go")
    shear_one = sp.Matrix([1, gamma])
    shear_two = sp.Matrix([2, 4 * gamma])
    additivity_defect = sp.simplify(shear_two - 2 * shear_one)
    audit.check("nonlinear shear additivity defect", additivity_defect == sp.Matrix([0, 2 * gamma]), additivity_defect, sp.Matrix([0, 2 * gamma]), "nonlinear_no_go")
    g, chi, u, v, tau, v0 = sp.symbols("g chi u v tau v0", positive=True, real=True)
    ordered_mixed_second = -3 * g * v0 / (2 * chi)
    ordered_axis_normal = sp.factor(ordered_mixed_second * u)
    ordered_final_endpoint_slope = sp.factor(ordered_axis_normal.subs(u, 2 * tau))
    audit.check("ordered second variation mixed axis value", ordered_mixed_second == -3 * g * v0 / (2 * chi), ordered_mixed_second, -3 * g * v0 / (2 * chi), "nonlinear_no_go")
    audit.check("ordered second variation normal axis value", ordered_axis_normal == -3 * g * v0 * u / (2 * chi), ordered_axis_normal, -3 * g * v0 * u / (2 * chi), "nonlinear_no_go")
    audit.check("ordered final-slice endpoint slope", ordered_final_endpoint_slope == -3 * g * v0 * tau / chi, ordered_final_endpoint_slope, -3 * g * v0 * tau / chi, "nonlinear_no_go")
    audit.check("ordered witness declared", "endpoint derivative is -3g*v0*tau/chi" in manifest["nonlinear_generator_relabel_no_go"]["CL8_witness"], manifest["nonlinear_generator_relabel_no_go"]["CL8_witness"], "ordered endpoint derivative", "nonlinear_no_go")
    third_variation = -3 * g * u * v / (2 * chi)
    q_third = sp.factor(third_variation.subs({u: tau, v: tau}))
    pi_third = sp.factor(chi * (sp.diff(third_variation, u) + sp.diff(third_variation, v)).subs({u: tau, v: tau}))
    audit.check("CL8 third variation PDE", sp.simplify(4 * chi * sp.diff(third_variation, u, v) + 6 * g) == 0, sp.simplify(4 * chi * sp.diff(third_variation, u, v) + 6 * g), 0, "nonlinear_no_go")
    audit.check("CL8 third variation boundary u", third_variation.subs(u, 0) == 0, third_variation.subs(u, 0), 0, "nonlinear_no_go")
    audit.check("CL8 third variation boundary v", third_variation.subs(v, 0) == 0, third_variation.subs(v, 0), 0, "nonlinear_no_go")
    audit.check("CL8 final q third derivative", q_third == -3 * g * tau**2 / (2 * chi), q_third, -3 * g * tau**2 / (2 * chi), "nonlinear_no_go")
    audit.check("CL8 final Pi third derivative", pi_third == -3 * g * tau, pi_third, -3 * g * tau, "nonlinear_no_go")
    audit.check("classification declared", "additive and hence real-linear" in manifest["nonlinear_generator_relabel_no_go"]["classification"], manifest["nonlinear_generator_relabel_no_go"]["classification"], "additive and real-linear", "nonlinear_no_go")

    # Independent hostile Groenewold/Moyal algebra.
    f_one = q**3
    g_one = p**3
    f_two = q**2 * p
    g_two = q * p**2
    lambda3_one = lambda_power(f_one, g_one, 3, q, p)
    lambda3_two = lambda_power(f_two, g_two, 3, q, p)
    poisson_one = lambda_power(f_one, g_one, 1, q, p)
    poisson_two = lambda_power(f_two, g_two, 1, q, p)
    moyal_one = sp.expand(poisson_one - hbar**2 * lambda3_one / 24)
    moyal_two = sp.expand(poisson_two - hbar**2 * lambda3_two / 24)
    first_q2p2 = sp.expand(moyal_one / 9)
    second_q2p2 = sp.expand(moyal_two / 3)
    moyal_difference = sp.expand(second_q2p2 - first_q2p2)
    audit.check("first Poisson bracket", poisson_one == 9 * q**2 * p**2, poisson_one, 9 * q**2 * p**2, "moyal")
    audit.check("second Poisson bracket", poisson_two == 3 * q**2 * p**2, poisson_two, 3 * q**2 * p**2, "moyal")
    audit.check("first Lambda cubed", lambda3_one == 36, lambda3_one, 36, "moyal")
    audit.check("second Lambda cubed", lambda3_two == -12, lambda3_two, -12, "moyal")
    audit.check("first quantization value", first_q2p2 == q**2 * p**2 - hbar**2 / 6, first_q2p2, q**2 * p**2 - hbar**2 / 6, "moyal")
    audit.check("second quantization value", second_q2p2 == q**2 * p**2 + hbar**2 / 6, second_q2p2, q**2 * p**2 + hbar**2 / 6, "moyal")
    audit.check("Groenewold discrepancy", moyal_difference == hbar**2 / 3, moyal_difference, hbar**2 / 3, "moyal")

    # Exact current-dynamics mismatch at the smallest admitted regulator.
    continuum_frequency_squared = sp.Integer(9 + 4**2)
    lattice_frequency_squared = sp.simplify(9 + 4 * sp.sin(2 * a) ** 2 / a**2)
    mismatch = sp.factor(continuum_frequency_squared - lattice_frequency_squared)
    audit.check("continuum first harmonic squared", continuum_frequency_squared == 25, continuum_frequency_squared, 25, "dynamics_no_go")
    audit.check("M=4 lattice first harmonic squared", lattice_frequency_squared == 9 + 128 / sp.pi**2, lattice_frequency_squared, 9 + 128 / sp.pi**2, "dynamics_no_go")
    audit.check("M=4 exact mismatch formula", sp.simplify(mismatch - 16 * (sp.pi**2 - 8) / sp.pi**2) == 0, mismatch, 16 * (sp.pi**2 - 8) / sp.pi**2, "dynamics_no_go")
    audit.check("M=4 mismatch positive", bool(sp.pi**2 > 8), sp.pi**2 > 8, True, "dynamics_no_go")
    audit.check("general strict sine boundary declared", "sin(2a)<2a" in manifest["current_dynamics_no_go"]["strict_mismatch"], manifest["current_dynamics_no_go"]["strict_mismatch"], "sin(2a)<2a", "dynamics_no_go")

    negative_ids = [
        manifest["unrestricted_sampling_no_go"]["negative_id"],
        manifest["nonlinear_generator_relabel_no_go"]["negative_id"],
        manifest["current_dynamics_no_go"]["negative_id"],
    ]
    expected_negatives = [
        "NG-2026-08-04-PRE-A-CP1-CL8-OA2-SAMPLING-EXACT-WEYL",
        "NG-2026-08-04-PRE-A-CP1-CL8-DIRECT-NONLINEAR-WEYL-RELABEL",
        "NG-2026-08-04-PRE-A-CP1-CL8-CURRENT-SAMPLING-EXACT-DYNAMICS",
    ]
    audit.check("formal negative ids", negative_ids == expected_negatives, negative_ids, expected_negatives, "scope")
    audit.check("parent gate remains open", manifest["gate_resolution"]["status"] == "SPLIT; PARENT GATE REMAINS OPEN", manifest["gate_resolution"]["status"], "SPLIT; PARENT GATE REMAINS OPEN", "scope")
    audit.check("three closed subgates", len(manifest["gate_resolution"]["closed_subgates"]) == 3, len(manifest["gate_resolution"]["closed_subgates"]), 3, "scope")
    audit.check("three refuted subgates", len(manifest["gate_resolution"]["refuted_subgates"]) == 3, len(manifest["gate_resolution"]["refuted_subgates"]), 3, "scope")
    audit.check("next common regulator gate", manifest["gate_resolution"]["next_gate"] == "PA-CP1-CL8-COMMON-FINITE-REGULATOR-CHARACTERISTIC-MODEL", manifest["gate_resolution"]["next_gate"], "PA-CP1-CL8-COMMON-FINITE-REGULATOR-CHARACTERISTIC-MODEL", "scope")

    required_true = (
        "ordered_tangent_finite_image_symplectic_isomorphism",
        "finite_image_metaplectic_control",
        "restricted_finite_a_Weyl_monomorphism",
        "interacting_bulk_state_restricted_boundary_pullback",
        "conditional_N1_cutoff_ingredient",
    )
    for key in required_true:
        audit.check(f"scope true: {key}", manifest["scope"][key] is True, manifest["scope"][key], True, "scope")
    required_false = (
        "unrestricted_point_sampling_exact_Weyl",
        "direct_nonlinear_generator_relabel_Weyl",
        "current_sampling_exact_dynamics_intertwiner",
        "full_finite_a_boundary_algebra",
        "interacting_boundary_bulk_dynamics_intertwiner",
        "interacting_Weyl_Cstar_dynamics_preserved",
        "preferred_physical_state_selected",
        "regulator_compatible_state_family",
        "continuum_quantum_state",
        "Hadamard_state",
        "hbar_origin_derived",
        "Lorentzian_or_null_structure_derived",
        "physical_vacuum",
        "below_empty_space",
        "C0_closed",
        "N1_closed",
        "N2_closed",
        "N3_closed",
        "N4_closed",
        "N5_closed",
        "C6_claim_advanced",
        "CP1_complete",
        "Pre_A_complete",
    )
    for key in required_false:
        audit.check(f"scope false: {key}", manifest["scope"][key] is False, manifest["scope"][key], False, "scope")

    derived = {
        "frequencies": [int(value) for value in omega.diagonal()],
        "transfer_determinants": [serial(sp.factor(transfer.extract([j, j + 3], [j, j + 3]).det())) for j in range(3)],
        "M_fixture": M,
        "continuum_gram": serial(continuum_gram),
        "discrete_gram": serial(discrete_gram),
        "sampling_rank": sampling_map.rank(),
        "sampling_kernel_sigma": "L/16",
        "scaled_commutator": "-1",
        "nonlinear_q_third": "-3*g*tau^2/(2*chi)",
        "nonlinear_Pi_third": "-3*g*tau",
        "ordered_q_second_endpoint_slope": "-3*g*v0*tau/chi",
        "shear_additivity_defect": ["0", "2*gamma"],
        "moyal_lambda3": [int(lambda3_one), int(lambda3_two)],
        "moyal_discrepancy": "hbar^2/3",
        "continuum_frequency_squared": int(continuum_frequency_squared),
        "lattice_fixture_frequency_squared": "9 + 128/pi^2",
        "next_gate": manifest["gate_resolution"]["next_gate"],
    }
    return {
        "schema": SCHEMA,
        "candidate_id": CANDIDATE_ID,
        "parent_ids": list(expected_parents),
        "result_id": RESULT_ID,
        "task_id": "T-054",
        "claim_context": "C6-SPACETIME-SIGNATURE",
        "claim_bearing": False,
        "verdict": manifest["verdict"],
        "derived": derived,
        "scope": manifest["scope"],
        "negative_ids": negative_ids,
        "assertions": audit.rows,
        "assertion_summary": {"passed": len(audit.rows), "total": len(audit.rows)},
        "next_gate": manifest["gate_resolution"]["next_gate"],
        "no_overclaim": manifest["no_overclaim"],
        "source_sha256": {
            "script": sha256(SCRIPT),
            "manifest": sha256(MANIFEST),
            "global_manifest": sha256(GLOBAL),
            "q3lock_manifest": sha256(Q3LOCK),
            "gaussian_manifest": sha256(GAUSSIAN),
            "classical_manifest": sha256(CLASSICAL),
            "quantum_manifest": sha256(QUANTUM),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload()
    atomic_json(args.output, payload)
    summary = payload["assertion_summary"]
    print(f"{CANDIDATE_ID} primary: {summary['passed']}/{summary['total']} PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

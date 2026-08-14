#!/usr/bin/env python3
"""Verify the R-167 v4.1 categorical GNS Poincare reduction.

The declared inputs below are exact audit fixtures, not Q3 predictions. Every
reported constant is derived from them. The load-bearing formulas are the GNS
energy/Rayleigh identity and
``Delta_L^full <= 32 sqrt(B_a) h_L V/(r_w^2 rho_*)``.
"""

from __future__ import annotations

import argparse
import ast
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
SLUG = "pre-a-cp1-st8-q3lock-categorical-ground-bandlimited-gns-poincare-route-split"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260814.md"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-14-primary-{SLUG}/result.json"
FORMAL_PATHS = (
    REPO / "claims/GATES.md",
    REPO / "RESULTS-LEDGER.md",
    REPO / "negative-results/registry.md",
    REPO / "explorations/log.jsonl",
)

CLOSED = "PA-CP1-ST8-Q3LOCK-ZERO-SOURCE-CATEGORICAL-GROUND-BANDLIMITED-GNS-ENERGY-FORM-CORE-AND-PARITY-POINCARE-REDUCTION"
NEW_NEGATIVE = "NG-2026-08-14-PRE-A-ST8-Q3LOCK-MESOSCOPIC-SOURCE-FULL-FINITE-GAP-AUTOMATIC-UNIFORM-POINCARE-TRANSFER"
REUSED = "NG-2026-08-11-PRE-A-ST8-Q3LOCK-ORDERED-GROUND-DOUBLETS-AUTOMATIC-GNS-GAP"

# Labelled exact audit inputs. Derived outputs appear only in the oracle ledger.
RHO_STAR = sp.Integer(8)
HBAR = sp.Integer(2)
R_W = sp.Rational(1, 16)
WEIGHT_A = sp.Integer(1)
A_S = sp.Integer(3)
C_GAMMA = sp.Integer(5)
GAMMA = sp.Rational(1, 4)
G_COUPLING = sp.Integer(16)
H_STAR = sp.Integer(3)
SOURCE_POWER = sp.Rational(3, 2)

GNS_ENERGIES = (sp.Integer(0), sp.Integer(3), sp.Integer(7))
GNS_AMPLITUDES = (sp.Integer(0), sp.Rational(1, 2), sp.Rational(1, 3))
GROUND_AMPLITUDE = sp.Rational(2, 3)

BRANCH_A = sp.Rational(3, 5)
BRANCH_B = sp.Rational(4, 5)
SOURCE_STRENGTH = sp.Rational(1, 10)
REFERENCE_EXCITATION = sp.Integer(5)

# Explicit test oracles detect drift; theorem values are recomputed below.
TEST_ORACLE_CONSTANTS = {
    "B_a": "9",
    "C_S": "3",
    "d_squared": "1/128",
    "gap_coefficient": "3072",
    "canonical_coefficient": "9216",
    "gap_power": "-1/2",
}
TEST_ORACLE_GNS = {
    "variance": "13/36",
    "energy": "55/36",
    "rayleigh": "55/13",
    "cutoff_form_error": "8/9",
    "final_form_error": "0",
}
TEST_ORACLE_BRANCH = {
    "overlap": "24/25",
    "expectation_split": "14/25",
    "one_minus_overlap_squared": "49/625",
    "source_branch_energy": "49/125",
    "orthogonal_rayleigh": "5",
}


def normalized_sha256(path: Path) -> str:
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
        self.rows: list[dict[str, str]] = []

    def check(self, name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        self.rows.append(
            {"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)}
        )


def scalar(matrix: sp.Matrix) -> sp.Expr:
    if matrix.shape != (1, 1):
        raise AssertionError(f"expected scalar matrix, got {matrix.shape}")
    return sp.simplify(matrix[0, 0])


def exact_derivation() -> dict[str, Any]:
    b_a = sp.simplify(WEIGHT_A * (A_S + C_GAMMA) + 1 / (4 * WEIGHT_A * GAMMA))
    c_s = sp.sqrt(b_a)
    d_squared = sp.simplify(R_W**2 * RHO_STAR / 4)
    gap_coefficient = sp.simplify(32 * c_s / (R_W**2 * RHO_STAR))
    canonical_coefficient = sp.simplify(gap_coefficient * H_STAR)
    gap_power = sp.simplify(1 - SOURCE_POWER)

    h_plus = sp.diag(*GNS_ENERGIES)
    omega = sp.Matrix([1, 0, 0])
    excited = sp.Matrix(GNS_AMPLITUDES)
    observable_on_ground = GROUND_AMPLITUDE * omega + excited
    mean = scalar(omega.T * observable_on_ground)
    centered = sp.simplify(observable_on_ground - mean * omega)
    variance = scalar(centered.T * centered)
    energy = scalar(centered.T * h_plus * centered)
    rayleigh = sp.simplify(energy / variance)

    cutoff_three = sp.diag(1, 1, 0)
    cutoff_seven = sp.eye(3)
    tail_three = sp.simplify(centered - cutoff_three * centered)
    tail_seven = sp.simplify(centered - cutoff_seven * centered)
    form_error_three = sp.simplify(scalar(tail_three.T * tail_three) + scalar(tail_three.T * h_plus * tail_three))
    form_error_seven = sp.simplify(scalar(tail_seven.T * tail_seven) + scalar(tail_seven.T * h_plus * tail_seven))

    parity = sp.Matrix([[1, 0, 0], [0, 0, 1], [0, 1, 0]])
    h_minus = sp.simplify(parity * h_plus * parity)
    parity_centered = sp.simplify(parity * centered)
    parity_energy = scalar(parity_centered.T * h_minus * parity_centered)

    phi_plus = sp.Matrix([BRANCH_A, BRANCH_B])
    phi_minus = sp.Matrix([BRANCH_B, BRANCH_A])
    overlap = scalar(phi_plus.T * phi_minus)
    witness = sp.diag(-1, 1)
    witness_plus = scalar(phi_plus.T * witness * phi_plus)
    witness_minus = scalar(phi_minus.T * witness * phi_minus)
    split = sp.simplify(witness_plus - witness_minus)
    one_minus = sp.simplify(1 - overlap**2)

    zeta_plus = sp.Matrix([-BRANCH_B, BRANCH_A])
    h_source_plus = sp.simplify(REFERENCE_EXCITATION * zeta_plus * zeta_plus.T)
    source_branch_energy = scalar(phi_minus.T * h_source_plus * phi_minus)
    h_source_minus = sp.simplify(sp.Matrix([[0, 1], [1, 0]]) * h_source_plus * sp.Matrix([[0, 1], [1, 0]]))
    source_operator = sp.simplify((h_source_minus - h_source_plus) / (2 * SOURCE_STRENGTH))
    signed_order = scalar(phi_plus.T * source_operator * phi_plus)
    centered_branch = sp.simplify((phi_minus - overlap * phi_plus) / sp.sqrt(one_minus))
    orthogonal_rayleigh = scalar(centered_branch.T * h_source_plus * centered_branch)
    exact_source_identity = sp.simplify(source_branch_energy - 2 * SOURCE_STRENGTH * signed_order)

    return {
        "constants": {
            "gamma_below_g_over_32": bool(GAMMA < G_COUPLING / 32),
            "B_a": str(b_a),
            "C_S": str(c_s),
            "d_squared": str(d_squared),
            "gap_coefficient": str(gap_coefficient),
            "canonical_coefficient": str(canonical_coefficient),
            "gap_power": str(gap_power),
        },
        "gns": {
            "mean": str(mean),
            "variance": str(variance),
            "energy": str(energy),
            "rayleigh": str(rayleigh),
            "cutoff_form_error": str(form_error_three),
            "final_form_error": str(form_error_seven),
            "parity_energy": str(parity_energy),
            "parity_spectra_equal": set(h_plus.eigenvals()) == set(h_minus.eigenvals()),
        },
        "branch": {
            "overlap": str(overlap),
            "expectation_split": str(split),
            "one_minus_overlap_squared": str(one_minus),
            "trace_distance_squared": str(sp.simplify(4 * one_minus)),
            "split_saturates_trace_distance": bool(sp.simplify(split**2 - 4 * one_minus) == 0),
            "source_branch_energy": str(source_branch_energy),
            "signed_order": str(signed_order),
            "source_identity_residual": str(exact_source_identity),
            "orthogonal_rayleigh": str(orthogonal_rayleigh),
            "orthogonal_to_ground": str(scalar(phi_plus.T * centered_branch)),
        },
    }


def build_payload(formal: bool) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate = " ".join(CERTIFICATE.read_text(encoding="utf-8").split())
    derived = exact_derivation()
    audit = Audit()

    audit.check("manifest identity", manifest["package_id"] == SLUG and manifest["version"] == "R-167 v4.1" and manifest["date"] == "2026-08-14" and manifest["exploration_id"] == "EXP-000845" and manifest["prior_exploration_id"] == "EXP-000844" and manifest["claim_bearing"] is False, (manifest["package_id"], manifest["version"], manifest["exploration_id"]), (SLUG, "R-167 v4.1", "EXP-000845"), "identity")
    audit.check("manifest topology", manifest["closed_gate_ids"] == [CLOSED] and manifest["negative_ids"] == [NEW_NEGATIVE] and manifest["reused_negative_ids"] == [REUSED], (manifest["closed_gate_ids"], manifest["negative_ids"], manifest["reused_negative_ids"]), ([CLOSED], [NEW_NEGATIVE], [REUSED]), "topology")
    inherited = " ".join(str(value) for value in manifest["inherited_v4_0_inputs"].values())
    audit.check("v4.0 exact inheritance", all(token in inherited for token in ("A_H^0", "D_bl", "omega_-=omega_+ o gamma", "cal E_L^sigma", "R_L^sigma(A)->0", "d=r_w sqrt(rho_*)/2")), inherited, "categorical ground-pair inputs", "theorem")
    energy_text = " ".join(manifest["gns_energy_identity"].values())
    audit.check("GNS energy identity contract", all(token in energy_text for token in ("exp(i t H_sigma/hbar)", "H_sigma>=0", "-i hbar pi_sigma(delta_H A)", "||H_sigma^(1/2)", "neither faithfulness")), energy_text, "exact implementation energy", "theorem")
    core_text = " ".join(manifest["centered_bandlimited_form_core"].values())
    audit.check("centered bandlimited form core", all(token in core_text for token in ("C_c^infinity", "Schwartz g_R", "compact Fourier support", "bounded on the filtered range", "diagonalize in R,n", "even if ker")), core_text, "two-stage spectral core", "theorem")
    rayleigh_text = " ".join(manifest["rayleigh_and_parity_reduction"].values())
    audit.check("Rayleigh parity reduction", all(token in rayleigh_text for token in ("Delta_sigma^P=inf", "ker(H_sigma)=C Omega_sigma", "W_gamma", "W_gamma H_- W_gamma^*=H_+", "Delta_-^P=Delta_+^P", "parity-twisted")), rayleigh_text, "exact Rayleigh and parity", "theorem")
    gap_text = " ".join(manifest["finite_source_gap_collapse"].values())
    audit.check("finite source gap collapse", all(token in gap_text for token in ("1-c_L^2>=d^2/4", "2 h_L s_L^+/(1-c_L^2)", "32 sqrt(B_a)/(r_w^2 rho_*)", "h_L V->0", "not refute")), gap_text, "exact global branch-switch bound", "theorem")
    limit_text = " ".join(manifest["fixed_carrier_limit_coercivity"].values())
    audit.check("fixed-carrier limit equivalence", all(token in limit_text for token in ("cal E_L^sigma(A)->", "if and only if", "for every fixed A", "cannot be interchanged", "No uniform positive")), limit_text, "fixed A/common Delta", "theorem")
    scope = " ".join(manifest["nonduplication_and_scope"].values()) + " " + manifest["no_overclaim"]
    audit.check("nonduplication and scope", all(token in scope for token in ("O(1/V)", "v1.8", "v3.0", "v3.4", "v4.0", "global L-dependent", "remain OPEN")), scope, "exact historical split", "scope")

    constants = derived["constants"]
    audit.check("derived Q3 constants", constants["gamma_below_g_over_32"] and all(constants[key] == value for key, value in TEST_ORACLE_CONSTANTS.items()), constants, TEST_ORACLE_CONSTANTS, "derivation")
    gns = derived["gns"]
    audit.check("exact GNS Rayleigh fixture", all(gns[key] == value for key, value in TEST_ORACLE_GNS.items()), gns, TEST_ORACLE_GNS, "derivation")
    audit.check("exact parity fixture", gns["parity_energy"] == gns["energy"] and gns["parity_spectra_equal"], gns, "equal spectra and energy", "derivation")
    branch = derived["branch"]
    audit.check("exact overlap and source trial", all(branch[key] == value for key, value in TEST_ORACLE_BRANCH.items()) and branch["split_saturates_trace_distance"] and branch["source_identity_residual"] == "0" and branch["orthogonal_to_ground"] == "0", branch, TEST_ORACLE_BRANCH, "derivation")
    audit.check("certificate math tokens", all(token in certificate for token in (CLOSED, NEW_NEGATIVE, "hat g(nu)=int_R exp(+i nu t)g(t)dt", "-i hbar omega(A^*delta_H(A))", "closure_form(C_D)", "Delta_-^P=Delta_+^P", "32 sqrt(B_a)/(r_w^2 rho_*)", "No interchange is permitted", "No v4.1 PDF is issued")), "required tokens present", "required tokens present", "certificate")
    audit.check("certificate lifecycle firewalls", all(token in certificate for token in ("not a positive-gap theorem", "does not refute a positive phasewise GNS gap", "simple-kernel hypothesis", "global and `L`-dependent", "Both historical gates and all five active parent gates remain OPEN")), "scope tokens present", "scope tokens present", "scope")
    audit.check("source AST and format", ast.parse(SCRIPT.read_text(encoding="utf-8")) is not None and all(b"\r" not in path.read_bytes() and path.read_bytes().endswith(b"\n") and all(byte < 128 for byte in path.read_bytes()) for path in (MANIFEST, CERTIFICATE, SCRIPT)), "AST ASCII LF final-LF", "AST ASCII LF final-LF", "format")
    if formal:
        formal_text = "\n".join(path.read_text(encoding="utf-8") for path in FORMAL_PATHS)
        audit.check("formal authority links", all(token in formal_text for token in ("EXP-000845", CLOSED, NEW_NEGATIVE, REUSED, "R-167 v4.1")), "all formal tokens present", "all formal tokens present", "formal")

    return {
        "schema": "tect/pre-a-q3lock-categorical-ground-bandlimited-gns-poincare-run/1.0",
        "version": "R-167 v4.1",
        "mode": "formal" if formal else "staged",
        "assertions": audit.rows,
        "summary": {"status": "PASS", "passed": len(audit.rows), "failed": 0},
        "derived": derived,
        "source_hashes": {str(path.relative_to(REPO)).replace("\\", "/"): normalized_sha256(path) for path in (MANIFEST, CERTIFICATE, SCRIPT)},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--staged", action="store_true")
    parser.add_argument("--no-store", action="store_true")
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    payload = build_payload(formal=not args.staged)
    if not args.no_store:
        atomic_json(args.output, payload)
    print(f"PRIMARY PASS {payload['summary']['passed']}/{payload['summary']['passed']} mode={payload['mode']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

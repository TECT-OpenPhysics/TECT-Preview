#!/usr/bin/env python3
"""Independently verify the R-167 v4.1 categorical GNS reduction.

This lane uses only stdlib ``Fraction`` matrix arithmetic. It imports no SymPy,
uses no float or complex values, and derives the source-gap coefficient and
all finite spectral fixtures from the labelled exact inputs below.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import math
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-categorical-ground-bandlimited-gns-poincare-route-split"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260814.md"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-14-independent-{SLUG}/result.json"

CLOSED = "PA-CP1-ST8-Q3LOCK-ZERO-SOURCE-CATEGORICAL-GROUND-BANDLIMITED-GNS-ENERGY-FORM-CORE-AND-PARITY-POINCARE-REDUCTION"
NEW_NEGATIVE = "NG-2026-08-14-PRE-A-ST8-Q3LOCK-MESOSCOPIC-SOURCE-FULL-FINITE-GAP-AUTOMATIC-UNIFORM-POINCARE-TRANSFER"
REUSED = "NG-2026-08-11-PRE-A-ST8-Q3LOCK-ORDERED-GROUND-DOUBLETS-AUTOMATIC-GNS-GAP"

# Independent labelled inputs matching only the primary lane's declared data.
RHO_STAR = Fraction(8)
HBAR = Fraction(2)
R_W = Fraction(1, 16)
WEIGHT_A = Fraction(1)
A_S = Fraction(3)
C_GAMMA = Fraction(5)
GAMMA = Fraction(1, 4)
G_COUPLING = Fraction(16)
H_STAR = Fraction(3)
SOURCE_POWER = Fraction(3, 2)

GNS_ENERGIES = (Fraction(0), Fraction(3), Fraction(7))
GNS_AMPLITUDES = (Fraction(0), Fraction(1, 2), Fraction(1, 3))
GROUND_AMPLITUDE = Fraction(2, 3)

BRANCH_A = Fraction(3, 5)
BRANCH_B = Fraction(4, 5)
SOURCE_STRENGTH = Fraction(1, 10)
REFERENCE_EXCITATION = Fraction(5)

# Explicit drift-detection oracles; all entries are independently recomputed.
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


Vector = list[Fraction]
Matrix = list[list[Fraction]]


def exact_sqrt(value: Fraction) -> Fraction:
    numerator = math.isqrt(value.numerator)
    denominator = math.isqrt(value.denominator)
    if numerator * numerator != value.numerator or denominator * denominator != value.denominator:
        raise AssertionError(f"non-square exact input: {value}")
    return Fraction(numerator, denominator)


def dot(left: Vector, right: Vector) -> Fraction:
    if len(left) != len(right):
        raise AssertionError("vector size mismatch")
    return sum((a * b for a, b in zip(left, right)), Fraction(0))


def mat_vec(matrix: Matrix, vector: Vector) -> Vector:
    return [dot(row, vector) for row in matrix]


def transpose(matrix: Matrix) -> Matrix:
    return [list(column) for column in zip(*matrix)]


def mat_mul(left: Matrix, right: Matrix) -> Matrix:
    columns = transpose(right)
    return [[dot(row, column) for column in columns] for row in left]


def mat_add(left: Matrix, right: Matrix) -> Matrix:
    return [[a + b for a, b in zip(row_a, row_b)] for row_a, row_b in zip(left, right)]


def mat_scale(value: Fraction, matrix: Matrix) -> Matrix:
    return [[value * entry for entry in row] for row in matrix]


def outer(left: Vector, right: Vector) -> Matrix:
    return [[a * b for b in right] for a in left]


def diag(values: tuple[Fraction, ...]) -> Matrix:
    return [[value if i == j else Fraction(0) for j, value in enumerate(values)] for i in range(len(values))]


def vector_add(left: Vector, right: Vector) -> Vector:
    return [a + b for a, b in zip(left, right)]


def vector_scale(value: Fraction, vector: Vector) -> Vector:
    return [value * entry for entry in vector]


def quadratic(vector: Vector, matrix: Matrix) -> Fraction:
    return dot(vector, mat_vec(matrix, vector))


def ast_firewall(path: Path) -> dict[str, Any]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imports: set[str] = set()
    forbidden_calls: list[str] = []
    forbidden_complex_literals: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.add((node.module or "").split(".")[0])
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in {
            "float",
            "complex",
            "eval",
            "exec",
            "compile",
            "__import__",
        }:
            forbidden_calls.append(node.func.id)
        elif isinstance(node, ast.Constant) and isinstance(node.value, complex):
            forbidden_complex_literals.append(repr(node.value))
    return {
        "imports": sorted(imports),
        "forbidden_calls": forbidden_calls,
        "forbidden_complex_literals": forbidden_complex_literals,
    }


def exact_derivation() -> dict[str, Any]:
    b_a = WEIGHT_A * (A_S + C_GAMMA) + Fraction(1) / (4 * WEIGHT_A * GAMMA)
    c_s = exact_sqrt(b_a)
    d_squared = R_W**2 * RHO_STAR / 4
    gap_coefficient = 32 * c_s / (R_W**2 * RHO_STAR)
    canonical_coefficient = gap_coefficient * H_STAR
    gap_power = 1 - SOURCE_POWER

    h_plus = diag(GNS_ENERGIES)
    omega = [Fraction(1), Fraction(0), Fraction(0)]
    excited = list(GNS_AMPLITUDES)
    observable_on_ground = vector_add(vector_scale(GROUND_AMPLITUDE, omega), excited)
    mean = dot(omega, observable_on_ground)
    centered = vector_add(observable_on_ground, vector_scale(-mean, omega))
    variance = dot(centered, centered)
    energy = quadratic(centered, h_plus)
    rayleigh = energy / variance

    cutoff_three = diag((Fraction(1), Fraction(1), Fraction(0)))
    cutoff_seven = diag((Fraction(1), Fraction(1), Fraction(1)))
    tail_three = vector_add(centered, vector_scale(-1, mat_vec(cutoff_three, centered)))
    tail_seven = vector_add(centered, vector_scale(-1, mat_vec(cutoff_seven, centered)))
    form_error_three = dot(tail_three, tail_three) + quadratic(tail_three, h_plus)
    form_error_seven = dot(tail_seven, tail_seven) + quadratic(tail_seven, h_plus)

    parity = [
        [Fraction(1), Fraction(0), Fraction(0)],
        [Fraction(0), Fraction(0), Fraction(1)],
        [Fraction(0), Fraction(1), Fraction(0)],
    ]
    h_minus = mat_mul(mat_mul(parity, h_plus), parity)
    parity_centered = mat_vec(parity, centered)
    parity_energy = quadratic(parity_centered, h_minus)
    spectra_plus = sorted(GNS_ENERGIES)
    spectra_minus = sorted(h_minus[index][index] for index in range(len(h_minus)))

    phi_plus = [BRANCH_A, BRANCH_B]
    phi_minus = [BRANCH_B, BRANCH_A]
    overlap = dot(phi_plus, phi_minus)
    witness = diag((Fraction(-1), Fraction(1)))
    witness_plus = quadratic(phi_plus, witness)
    witness_minus = quadratic(phi_minus, witness)
    split = witness_plus - witness_minus
    one_minus = 1 - overlap**2

    zeta_plus = [-BRANCH_B, BRANCH_A]
    h_source_plus = mat_scale(REFERENCE_EXCITATION, outer(zeta_plus, zeta_plus))
    parity_two = [[Fraction(0), Fraction(1)], [Fraction(1), Fraction(0)]]
    h_source_minus = mat_mul(mat_mul(parity_two, h_source_plus), parity_two)
    source_operator = mat_scale(Fraction(1) / (2 * SOURCE_STRENGTH), mat_add(h_source_minus, mat_scale(-1, h_source_plus)))
    source_branch_energy = quadratic(phi_minus, h_source_plus)
    signed_order = quadratic(phi_plus, source_operator)
    normalization = exact_sqrt(one_minus)
    centered_branch = vector_scale(Fraction(1) / normalization, vector_add(phi_minus, vector_scale(-overlap, phi_plus)))
    orthogonal_rayleigh = quadratic(centered_branch, h_source_plus)
    exact_source_identity = source_branch_energy - 2 * SOURCE_STRENGTH * signed_order

    return {
        "constants": {
            "gamma_below_g_over_32": GAMMA < G_COUPLING / 32,
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
            "parity_spectra_equal": spectra_plus == spectra_minus,
        },
        "branch": {
            "overlap": str(overlap),
            "expectation_split": str(split),
            "one_minus_overlap_squared": str(one_minus),
            "trace_distance_squared": str(4 * one_minus),
            "split_saturates_trace_distance": split**2 == 4 * one_minus,
            "source_branch_energy": str(source_branch_energy),
            "signed_order": str(signed_order),
            "source_identity_residual": str(exact_source_identity),
            "orthogonal_rayleigh": str(orthogonal_rayleigh),
            "orthogonal_to_ground": str(dot(phi_plus, centered_branch)),
        },
    }


def build_payload(formal: bool) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate = " ".join(CERTIFICATE.read_text(encoding="utf-8").split())
    derived = exact_derivation()
    audit = Audit()

    audit.check("manifest exact identity", manifest["package_id"] == SLUG and manifest["version"] == "R-167 v4.1" and manifest["exploration_id"] == "EXP-000845" and manifest["prior_exploration_id"] == "EXP-000844" and manifest["claim_bearing"] is False, (manifest["package_id"], manifest["version"], manifest["exploration_id"]), (SLUG, "R-167 v4.1", "EXP-000845"), "identity")
    audit.check("manifest exact topology", manifest["closed_gate_ids"] == [CLOSED] and manifest["negative_ids"] == [NEW_NEGATIVE] and manifest["reused_negative_ids"] == [REUSED], (manifest["closed_gate_ids"], manifest["negative_ids"], manifest["reused_negative_ids"]), ([CLOSED], [NEW_NEGATIVE], [REUSED]), "topology")
    energy = " ".join(manifest["gns_energy_identity"].values())
    core = " ".join(manifest["centered_bandlimited_form_core"].values())
    audit.check("implementation and form-core contract", all(token in energy + " " + core for token in ("H_sigma>=0", "-i hbar", "C_c^infinity", "compact Fourier support", "form core", "even if ker")), energy + " " + core, "exact GNS core", "theorem")
    rayleigh = " ".join(manifest["rayleigh_and_parity_reduction"].values())
    audit.check("Rayleigh parity contract", all(token in rayleigh for token in ("Delta_sigma^P=inf", "ker(H_sigma)=C Omega_sigma", "W_gamma", "Delta_-^P=Delta_+^P", "parity-twisted")), rayleigh, "exact Rayleigh parity", "theorem")
    gap = " ".join(manifest["finite_source_gap_collapse"].values())
    audit.check("source collapse contract", all(token in gap for token in ("d^2/4", "2 h_L s_L^+", "32 sqrt(B_a)", "h_L V->0", "not refute")), gap, "global finite-source collapse", "theorem")
    limit = " ".join(manifest["fixed_carrier_limit_coercivity"].values())
    audit.check("fixed carrier quantifiers", all(token in limit for token in ("for every fixed A", "if and only if", "cannot be interchanged", "remains the load-bearing")), limit, "one common Delta after fixed-A limits", "scope")

    constants = derived["constants"]
    audit.check("independent derived constants", constants["gamma_below_g_over_32"] and all(constants[key] == value for key, value in TEST_ORACLE_CONSTANTS.items()), constants, TEST_ORACLE_CONSTANTS, "derivation")
    gns = derived["gns"]
    audit.check("independent GNS form fixture", all(gns[key] == value for key, value in TEST_ORACLE_GNS.items()) and gns["parity_energy"] == gns["energy"] and gns["parity_spectra_equal"], gns, TEST_ORACLE_GNS, "derivation")
    branch = derived["branch"]
    audit.check("independent overlap/source fixture", all(branch[key] == value for key, value in TEST_ORACLE_BRANCH.items()) and branch["split_saturates_trace_distance"] and branch["source_identity_residual"] == "0" and branch["orthogonal_to_ground"] == "0", branch, TEST_ORACLE_BRANCH, "derivation")
    firewall = ast_firewall(SCRIPT)
    allowed_imports = {"__future__", "argparse", "ast", "hashlib", "json", "math", "os", "tempfile", "fractions", "pathlib", "typing"}
    audit.check("stdlib exact AST firewall", set(firewall["imports"]) <= allowed_imports and not firewall["forbidden_calls"] and not firewall["forbidden_complex_literals"], firewall, "stdlib allowlist and no float/complex/dynamic execution", "independence")
    audit.check("certificate exact tokens", all(token in certificate for token in (CLOSED, NEW_NEGATIVE, "hat g_R(H/hbar)", "closure_form(C_D)", "Delta_-^P=Delta_+^P", "32 sqrt(B_a)/(r_w^2 rho_*)", "No interchange is permitted", "No v4.1 PDF is issued")), "required tokens present", "required tokens present", "certificate")
    audit.check("scope firewall", all(token in manifest["no_overclaim"] for token in ("no positive D_bl Poincare constant", "global L-dependent", "not a phasewise target-gap no-go", "remain OPEN")), manifest["no_overclaim"], "T0 route scope", "scope")
    audit.check("source AST and exact format", ast.parse(SCRIPT.read_text(encoding="utf-8")) is not None and all(b"\r" not in path.read_bytes() and path.read_bytes().endswith(b"\n") and all(byte < 128 for byte in path.read_bytes()) for path in (MANIFEST, CERTIFICATE, SCRIPT)), "AST ASCII LF final-LF", "AST ASCII LF final-LF", "format")
    if formal:
        formal_paths = (REPO / "claims/GATES.md", REPO / "RESULTS-LEDGER.md", REPO / "negative-results/registry.md", REPO / "explorations/log.jsonl")
        formal_text = "\n".join(path.read_text(encoding="utf-8") for path in formal_paths)
        audit.check("formal authority links", all(token in formal_text for token in ("EXP-000845", CLOSED, NEW_NEGATIVE, REUSED, "R-167 v4.1")), "all formal tokens present", "all formal tokens present", "formal")

    return {
        "schema": "tect/pre-a-q3lock-categorical-ground-bandlimited-gns-poincare-independent-run/1.0",
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
    print(f"INDEPENDENT PASS {payload['summary']['passed']}/{payload['summary']['passed']} mode={payload['mode']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

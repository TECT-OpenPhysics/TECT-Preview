#!/usr/bin/env python3
"""Non-importing stdlib verifier for the R-167 v3.0 route split."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import tempfile
from fractions import Fraction
from itertools import product
from math import isqrt
from pathlib import Path
from typing import Any


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-zero-source-star-bond-modulation-and-gns-gap-transfer-route-split"
PRIMARY = REPO / "codes/foundations/pre_a_cp1_st8_q3lock_zero_source_star_bond_modulation_and_gns_gap_transfer_route_split.py"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260813.md"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-13-independent-{SLUG}/result.json"
FORMAL_PATHS = (
    REPO / "claims/GATES.md",
    REPO / "RESULTS-LEDGER.md",
    REPO / "negative-results/registry.md",
    REPO / "explorations/log.jsonl",
)

# Independent labelled inputs. Reported claims are recomputed without SymPy.
STAR_INPUTS = (3, 6, 8, 96, 100, 1000)
RADIUS_INPUTS = (16, 8, 1, 1, 1, 10)
BOND_PHASE = -1
SHELL_INPUTS = (4, 2)
GNS_INPUTS = (3, 2, 5, 1)
NEGATIVE_INPUTS = (7, 1, 1)


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
        self.rows.append({"name": name, "group": group, "status": "PASS", "actual": str(actual), "expected": str(expected)})


Matrix = list[list[Fraction]]


def matrix_multiply(left: Matrix, right: Matrix) -> Matrix:
    rows = len(left)
    inner = len(right)
    columns = len(right[0])
    return [
        [sum((left[i][k] * right[k][j] for k in range(inner)), Fraction(0)) for j in range(columns)]
        for i in range(rows)
    ]


def matrix_transpose(matrix: Matrix) -> Matrix:
    return [list(row) for row in zip(*matrix)]


def matrix_subtract(left: Matrix, right: Matrix) -> Matrix:
    return [[left[i][j] - right[i][j] for j in range(len(left[0]))] for i in range(len(left))]


def matrix_commutator(left: Matrix, right: Matrix) -> Matrix:
    return matrix_subtract(matrix_multiply(left, right), matrix_multiply(right, left))


def matrix_trace(matrix: Matrix) -> Fraction:
    return sum((matrix[i][i] for i in range(len(matrix))), Fraction(0))


def scalar_identity_norm(matrix: Matrix) -> Fraction:
    gram = matrix_multiply(matrix_transpose(matrix), matrix)
    diagonal = gram[0][0]
    if any(gram[i][j] != (diagonal if i == j else 0) for i in range(len(gram)) for j in range(len(gram))):
        raise AssertionError(f"fixture Gram is not scalar: {gram}")
    numerator_root = isqrt(diagonal.numerator)
    denominator_root = isqrt(diagonal.denominator)
    if numerator_root**2 != diagonal.numerator or denominator_root**2 != diagonal.denominator:
        raise AssertionError(f"fixture norm is not rational: {diagonal}")
    return Fraction(numerator_root, denominator_root)


def diagonal_gram_norm(matrix: Matrix) -> Fraction:
    gram = matrix_multiply(matrix_transpose(matrix), matrix)
    if any(gram[i][j] != 0 for i in range(len(gram)) for j in range(len(gram)) if i != j):
        raise AssertionError(f"fixture Gram is not diagonal: {gram}")
    largest = max(gram[i][i] for i in range(len(gram)))
    numerator_root = isqrt(largest.numerator)
    denominator_root = isqrt(largest.denominator)
    if numerator_root**2 != largest.numerator or denominator_root**2 != largest.denominator:
        raise AssertionError(f"fixture norm is not rational: {largest}")
    return Fraction(numerator_root, denominator_root)


def star_fixture() -> dict[str, Any]:
    dimension, z, coupling_i, high_gap_i, alpha_den, beta_den = STAR_INPUTS
    coupling = Fraction(coupling_i)
    high_gap = Fraction(high_gap_i)
    labels = {"+": (Fraction(0), Fraction(1)), "-": (Fraction(0), Fraction(-1)), "h": (high_gap, Fraction(0))}

    def edge(a: str, b: str) -> Fraction:
        ka, sa = labels[a]
        kb, sb = labels[b]
        return (ka + kb) / z + coupling * (1 - sa * sb)

    energies: dict[tuple[str, ...], Fraction] = {}
    for configuration in product(labels, repeat=dimension + 1):
        energies[configuration] = sum((edge(configuration[0], configuration[i]) for i in range(1, dimension + 1)), Fraction(0))
    positives = sorted(value for value in energies.values() if value > 0)
    gap = positives[0]
    formula_gap = min(2 * coupling, high_gap / z + coupling)
    alpha = Fraction(1, alpha_den)
    beta = Fraction(1, beta_den)
    return {
        "z": z,
        "dimension": dimension,
        "J": coupling,
        "Gamma": high_gap,
        "kernel_dimension": sum(value == 0 for value in energies.values()),
        "low_disagreement": energies[("+", "-", "+", "+")],
        "high_neighbour": energies[("+", "h", "+", "+")],
        "high_centre": energies[("h", "+", "+", "+")],
        "gap": gap,
        "formula_gap": formula_gap,
        "alpha": alpha,
        "beta": beta,
        "normalized_beta": dimension * beta / gap,
    }


def integer_cube_root_floor(value: int) -> int:
    candidate = 0
    while (candidate + 1) ** 3 <= value:
        candidate += 1
    return candidate


def radius_fixture() -> dict[str, Any]:
    c_alpha, c_beta, a_2, b_2, g_0, n_1 = RADIUS_INPUTS
    square_floor = isqrt(c_alpha // a_2)
    cube_numerator = 3 * c_beta
    cube_denominator = g_0 * b_2
    cube_floor = integer_cube_root_floor(cube_numerator // cube_denominator)
    while (cube_floor + 1) ** 3 * cube_denominator <= cube_numerator:
        cube_floor += 1
    n_star = 1 + max(n_1, square_floor, cube_floor)
    alpha_at = Fraction(c_alpha, n_star**2)
    beta_at = Fraction(3 * c_beta, g_0 * n_star**3)
    return {
        "C_alpha": Fraction(c_alpha),
        "C_beta": Fraction(c_beta),
        "a_2": Fraction(a_2),
        "b_2": Fraction(b_2),
        "g_0": Fraction(g_0),
        "N_1": n_1,
        "N_star": n_star,
        "strict_alpha_at_N_star": alpha_at < a_2,
        "strict_beta_at_N_star": beta_at < b_2,
        "alpha_at_N_star": alpha_at,
        "beta_prime_at_N_star": beta_at,
    }


def bond_fixture() -> dict[str, Any]:
    phase = Fraction(BOND_PHASE)
    modulation = [[Fraction(1), Fraction(0)], [Fraction(0), phase]]
    offdiagonal = [[Fraction(0), Fraction(1)], [Fraction(1), Fraction(0)]]
    diagonal = [[Fraction(2), Fraction(0)], [Fraction(0), Fraction(-1)]]
    off_delta = matrix_subtract(matrix_multiply(matrix_multiply(modulation, offdiagonal), modulation), offdiagonal)
    diagonal_delta = matrix_subtract(matrix_multiply(matrix_multiply(modulation, diagonal), modulation), diagonal)
    off_distance = scalar_identity_norm(off_delta)
    diagonal_distance = scalar_identity_norm(diagonal_delta)
    return {
        "offdiagonal_modulation_distance": off_distance,
        "diagonal_modulation_distance": diagonal_distance,
        "nonzero_time_supremum": off_distance,
    }


def shell_fixture() -> dict[str, Any]:
    radius, denominator = SHELL_INPUTS
    base = Fraction(1, denominator)
    tail = base ** (radius + 1) / (1 - base)
    return {"radius": radius, "tail": tail, "cauchy_bound": tail}


def gns_fixture() -> dict[str, Any]:
    delta_gap_i, numerator, denominator, hbar_i = GNS_INPUTS
    delta_gap = Fraction(delta_gap_i)
    coefficient = Fraction(numerator, denominator)
    hbar = Fraction(hbar_i)
    density = [[Fraction(1), Fraction(0)], [Fraction(0), Fraction(0)]]
    observable = [[Fraction(0), Fraction(0)], [coefficient, Fraction(0)]]
    observable_star = matrix_transpose(observable)
    product_aa = matrix_multiply(observable_star, observable)
    variance = matrix_trace(matrix_multiply(density, product_aa))
    hamiltonian = [[Fraction(0), Fraction(0)], [Fraction(0), delta_gap]]
    commutator_without_i = matrix_commutator(hamiltonian, observable)
    energy = hbar * matrix_trace(matrix_multiply(density, matrix_multiply(observable_star, commutator_without_i))) / hbar
    return {"Delta": delta_gap, "coefficient": coefficient, "variance": variance, "energy": energy, "gap_ratio": energy / variance}


def negative_fixture() -> dict[str, Any]:
    sample_n_i, lower_i, hbar_i = NEGATIVE_INPUTS
    sample_n = Fraction(sample_n_i)
    lower = Fraction(lower_i)
    hbar = Fraction(hbar_i)
    density = [[Fraction(1), Fraction(0)], [Fraction(0), Fraction(0)]]
    limiting_density = [[Fraction(1), Fraction(0)], [Fraction(0), Fraction(0)]]
    state_distance = scalar_identity_norm(matrix_subtract(density, limiting_density))
    hamiltonian_levels = sorted((Fraction(0), sample_n))
    finite_gap = hamiltonian_levels[1] - hamiltonian_levels[0]
    observable = [[Fraction(0), Fraction(0)], [Fraction(1), Fraction(0)]]
    observable_star = matrix_transpose(observable)
    variance = matrix_trace(matrix_multiply(density, matrix_multiply(observable_star, observable)))
    hamiltonian = [[Fraction(0), Fraction(0)], [Fraction(0), sample_n]]
    commutator_without_i = matrix_commutator(hamiltonian, observable)
    energy = hbar * matrix_trace(matrix_multiply(density, matrix_multiply(observable_star, commutator_without_i))) / hbar
    generator_norm = diagonal_gram_norm(commutator_without_i)
    next_hamiltonian = [[Fraction(0), Fraction(0)], [Fraction(0), sample_n + 1]]
    next_commutator = matrix_commutator(next_hamiltonian, observable)
    next_distance = diagonal_gram_norm(matrix_subtract(next_commutator, commutator_without_i))
    return {
        "sample_n": sample_n_i,
        "finite_gap": finite_gap,
        "uniform_lower_gap": lower,
        "state_distance": state_distance,
        "generator_norm": generator_norm,
        "next_generator_distance": next_distance,
        "variance": variance,
        "energy": energy,
    }


def stringify(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: stringify(item) for key, item in value.items()}
    if isinstance(value, list):
        return [stringify(item) for item in value]
    if isinstance(value, bool) or value is None or isinstance(value, (int, str)):
        return value
    return str(value)


def independence_firewall() -> dict[str, Any]:
    tree = ast.parse(SCRIPT.read_text(encoding="utf-8"))
    allowed = {"__future__", "argparse", "ast", "hashlib", "json", "os", "tempfile", "fractions", "itertools", "math", "pathlib", "typing"}
    imported: list[str] = []
    dynamic: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.extend(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.append((node.module or "").split(".")[0])
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in {"__import__", "eval", "exec", "compile"}:
                dynamic.append(node.func.id)
            if isinstance(node.func, ast.Attribute) and node.func.attr in {"import_module", "exec_module", "load_module"}:
                dynamic.append(node.func.attr)
    roots = sorted(set(imported))
    return {
        "imports": roots,
        "unapproved": sorted(set(roots) - allowed),
        "dynamic": dynamic,
        "primary_imported": any(root.startswith("pre_a_cp1") for root in roots),
    }


def build_payload(staged: bool) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate = CERTIFICATE.read_text(encoding="utf-8")
    fixtures = {
        "star": star_fixture(),
        "radius": radius_fixture(),
        "bond": bond_fixture(),
        "shell": shell_fixture(),
        "gns": gns_fixture(),
        "negative": negative_fixture(),
    }
    firewall = independence_firewall()
    audit = Audit()

    audit.check("manifest identity", manifest["package_id"] == SLUG and manifest["exploration_id"] == "EXP-000834", (manifest["package_id"], manifest["exploration_id"]), (SLUG, "EXP-000834"), "identity")
    audit.check("three children and one negative", (len(manifest["closed_gate_ids"]), len(manifest["negative_ids"])) == (3, 1), (len(manifest["closed_gate_ids"]), len(manifest["negative_ids"])), (3, 1), "identity")
    audit.check("five OPEN parents", len(manifest["open_parent_gate_ids"]) == 5, manifest["open_parent_gate_ids"], "five", "identity")

    for group, derived in fixtures.items():
        oracle = manifest["exact_fixture"][group]
        for key, expected in oracle.items():
            audit.check(f"{group} {key}", key in derived and stringify(derived[key]) == expected, derived.get(key), expected, group)
    audit.check("star formula attained", fixtures["star"]["gap"] == fixtures["star"]["formula_gap"], fixtures["star"]["gap"], fixtures["star"]["formula_gap"], "star")
    audit.check("GNS equality", fixtures["gns"]["energy"] == fixtures["gns"]["Delta"] * fixtures["gns"]["variance"], fixtures["gns"]["energy"], fixtures["gns"]["Delta"] * fixtures["gns"]["variance"], "gns")
    audit.check("negative finite gap lower bound", fixtures["negative"]["finite_gap"] >= fixtures["negative"]["uniform_lower_gap"], fixtures["negative"]["finite_gap"], fixtures["negative"]["uniform_lower_gap"], "negative")
    audit.check("stdlib independence firewall", not firewall["unapproved"] and not firewall["dynamic"] and not firewall["primary_imported"], firewall, "stdlib only", "independence")
    audit.check("independent source distinct", normalized_sha256(SCRIPT) != normalized_sha256(PRIMARY), normalized_sha256(SCRIPT), "different from primary", "independence")

    normalized_certificate = " ".join(certificate.split())
    required = ("Pirogov--Sinai theory", "k_NP_N=P_Nk_N=0", "is attained", "applies directly to the exact infinite-dimensional", "assign every `j in J` an integer shell", "invariant under its `delta_n` dynamics", "All five active parent gates remain OPEN", "No v3.0 PDF is issued")
    manifest_star_setup = manifest["zero_source_forward_star"]["setup"]
    audit.check("certificate corrected scope", all(token in normalized_certificate for token in required) and "k_N P_N=P_N k_N=0" in manifest_star_setup, {"certificate_missing": [token for token in required if token not in normalized_certificate], "manifest_kernel_premise": "k_N P_N=P_N k_N=0" in manifest_star_setup}, {"certificate_missing": [], "manifest_kernel_premise": True}, "authority")
    audit.check("no PDF lifecycle", manifest["checkpoint_synthesis"]["pdf_issued"] is False and "--staged --no-store" in manifest["verification"]["staged_lifecycle"] and "cutoff-stable passage theorem" in manifest["no_overclaim"], manifest["verification"], "staged/no PDF and cutoff-passage firewall", "authority")

    if not staged:
        formal_text = "\n".join(path.read_text(encoding="utf-8") for path in FORMAL_PATHS)
        formal_tokens = ["EXP-000834", "R-167 v3.0", *manifest["closed_gate_ids"], *manifest["negative_ids"]]
        audit.check("formal authority landed", all(token in formal_text for token in formal_tokens), [token for token in formal_tokens if token not in formal_text], [], "formal")

    derived = {key: stringify(value) for key, value in fixtures.items()}
    derived["firewall"] = firewall
    return {
        "schema": "tect/verification-run/1.0",
        "script_version": __version__,
        "package_id": SLUG,
        "mode": "staged" if staged else "formal",
        "verdict": "PASS",
        "assertions": audit.rows,
        "summary": {"total": len(audit.rows), "passed": len(audit.rows), "failed": 0, "missing": 0},
        "derived": derived,
        "source_hashes": {
            str(path.relative_to(REPO)).replace("\\", "/"): normalized_sha256(path)
            for path in (SCRIPT, MANIFEST, CERTIFICATE)
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--staged", action="store_true")
    parser.add_argument("--no-store", action="store_true")
    args = parser.parse_args()
    payload = build_payload(args.staged)
    if not args.no_store:
        atomic_json(args.output, payload)
    total = payload["summary"]["total"]
    print(f"R-167 v3.0 INDEPENDENT PASS {total}/{total}")
    if args.no_store:
        print("NO-STORE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

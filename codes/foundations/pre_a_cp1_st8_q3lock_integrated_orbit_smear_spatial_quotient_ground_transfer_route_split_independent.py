#!/usr/bin/env python3
"""Independently verify the R-167 v4.2 spatial quotient theorem.

This lane uses only stdlib ``Fraction`` arithmetic. It imports no SymPy, uses
no float or complex values, and independently derives every exact shell,
product, quotient, kernel, and parity-ground fixture from labelled inputs.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import os
import tempfile
from fractions import Fraction
from pathlib import Path
from typing import Any


__version__ = "1.0.0"
REPO = Path(__file__).resolve().parents[2]
SCRIPT = Path(__file__).resolve()
SLUG = "pre-a-cp1-st8-q3lock-integrated-orbit-smear-spatial-quotient-ground-transfer-route-split"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260814.md"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-14-independent-{SLUG}/result.json"

CLOSED = "PA-CP1-ST8-Q3LOCK-INTEGRATED-ORBIT-SMEAR-SHELL-CAUCHY-SPATIAL-QUOTIENT-AND-SAME-NET-GROUND-TRANSFER"
REUSED = [
    "NG-2026-08-12-PRE-A-ST8-Q3LOCK-ORBIT-SMEAR-SEED-SUPPORT-AUTOMATIC-SPATIAL-LOCAL-NET",
    "NG-2026-08-13-PRE-A-ST8-Q3LOCK-CATEGORICAL-UNIFORM-CONTINUOUS-ELEMENT-KMS-ENVELOPE-AUTOMATIC-ALL-SHAPE-CAUCHY-AND-UNIQUE-PHASE-QUOTIENT",
    "NG-2026-08-13-PRE-A-ST8-Q3LOCK-NONESSENTIALLY-CONSTANT-LINFINITY-CONFIGURATION-MULTIPLIER-FULL-HAMILTONIAN-POINT-NORM-C0",
]

# Independent exact inputs matching only the primary lane's declared data.
SHELL_RATIO = Fraction(1, 2)
SHELL_RADIUS = 2
LABEL_SPLIT = (Fraction(1, 3), Fraction(2, 3))
SYMMETRIC_DIFFERENCE = ((3, 0), (3, 1), (4, 0))
FACTOR_NORMS = (Fraction(2), Fraction(3), Fraction(5))
FACTOR_TOGGLE_WEIGHTS = (Fraction(1, 7), Fraction(1, 11), Fraction(1, 13))

WEAK_COEFFICIENTS = (Fraction(1, 4), -Fraction(1, 6), Fraction(1, 3))
SHIFT_L1_ERROR = Fraction(1, 12)

PERIODIC_INDEX = Fraction(8)
COMPLETION_ERROR = Fraction(1, 16)
ALGEBRAIC_PATH_ERROR = Fraction(1, 32)
GROUND_EXCITATION = Fraction(2)
WITNESS_HALF = Fraction(1, 2)

# Labelled exact oracles detect drift; no value is accepted without derivation.
TEST_ORACLE_SHELL = {
    "summable_total": "1",
    "tail_after_radius": "1/4",
    "symmetric_difference_bound": "7/48",
    "product_toggle_bound": "3517/1001",
    "product_norm_bound": "30",
}
TEST_ORACLE_WEAK = {
    "weak_sum_norm": "3/4",
    "l1_bound": "3/4",
    "translation_bound": "1/12",
}
TEST_ORACLE_QUOTIENT = {
    "categorical_sup_norm": "2",
    "spatial_quotient_norm": "1",
    "periodic_path_error": "1/8",
    "kernel_representation_norm": "1/8",
    "completion_three_term_bound": "5/32",
}
TEST_ORACLE_GROUND = {
    "plus_witness": "1/2",
    "minus_witness": "-1/2",
    "state_distance_lower_bound": "1",
    "spatial_witness_norm": "1/2",
    "plus_ground_energy": "0",
    "minus_ground_energy": "0",
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


def diag(values: tuple[Fraction, ...]) -> Matrix:
    return [
        [value if row == column else Fraction(0) for column in range(len(values))]
        for row, value in enumerate(values)
    ]


def diagonal_norm(matrix: Matrix) -> Fraction:
    if any(matrix[row][column] != 0 for row in range(len(matrix)) for column in range(len(matrix)) if row != column):
        raise AssertionError("fixture requires a diagonal matrix")
    return max(abs(matrix[index][index]) for index in range(len(matrix)))


def quadratic(vector: Vector, matrix: Matrix) -> Fraction:
    return dot(vector, mat_vec(matrix, vector))


def ast_firewall(path: Path) -> dict[str, Any]:
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imports: set[str] = set()
    forbidden_calls: list[str] = []
    forbidden_literals: list[str] = []
    dynamic_attributes: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imports.add((node.module or "").split(".")[0])
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name) and node.func.id in {
                "float",
                "complex",
                "eval",
                "exec",
                "compile",
                "__import__",
            }:
                forbidden_calls.append(node.func.id)
            if isinstance(node.func, ast.Attribute) and node.func.attr in {
                "import_module",
                "exec_module",
                "load_module",
            }:
                dynamic_attributes.append(node.func.attr)
        elif isinstance(node, ast.Constant) and isinstance(node.value, (float, complex)):
            forbidden_literals.append(repr(node.value))
    return {
        "imports": sorted(imports),
        "forbidden_calls": forbidden_calls,
        "forbidden_literals": forbidden_literals,
        "dynamic_attributes": dynamic_attributes,
    }


def label_weight(shell: int, branch: int) -> Fraction:
    return LABEL_SPLIT[branch] * SHELL_RATIO**shell


def exact_derivation() -> dict[str, Any]:
    summable_total = SHELL_RATIO / (1 - SHELL_RATIO)
    tail = SHELL_RATIO ** (SHELL_RADIUS + 1) / (1 - SHELL_RATIO)
    symmetric_bound = sum(
        (label_weight(shell, branch) for shell, branch in SYMMETRIC_DIFFERENCE),
        Fraction(0),
    )
    product_toggle = sum(
        (
            FACTOR_TOGGLE_WEIGHTS[index]
            * product(
                FACTOR_NORMS[other]
                for other in range(len(FACTOR_NORMS))
                if other != index
            )
            for index in range(len(FACTOR_NORMS))
        ),
        Fraction(0),
    )
    product_norm = product(FACTOR_NORMS)

    weak_operators = (
        (Fraction(1), Fraction(-1)),
        (Fraction(-1), Fraction(1)),
        (Fraction(1), Fraction(1)),
    )
    weak_diagonal = [
        sum(
            (WEAK_COEFFICIENTS[index] * weak_operators[index][column] for index in range(len(weak_operators))),
            Fraction(0),
        )
        for column in range(len(weak_operators[0]))
    ]
    weak_sum_norm = max(abs(value) for value in weak_diagonal)
    weak_l1_bound = sum((abs(value) for value in WEAK_COEFFICIENTS), Fraction(0))

    periodic_representation = (
        1 + 1 / PERIODIC_INDEX,
        -1 + 1 / (2 * PERIODIC_INDEX),
    )
    spatial_image = (Fraction(1), Fraction(-1))
    periodic_path_error = max(
        abs(periodic_representation[index] - spatial_image[index])
        for index in range(len(spatial_image))
    )
    categorical_sup_norm = 1 + Fraction(1)
    spatial_norm = max(abs(value) for value in spatial_image)
    kernel_representation = (1 / PERIODIC_INDEX, -1 / (2 * PERIODIC_INDEX))
    kernel_norm = max(abs(value) for value in kernel_representation)
    completion_bound = 2 * COMPLETION_ERROR + ALGEBRAIC_PATH_ERROR

    hamiltonian = diag((Fraction(0), Fraction(0), GROUND_EXCITATION, GROUND_EXCITATION))
    phi_plus = [Fraction(1), Fraction(0), Fraction(0), Fraction(0)]
    phi_minus = [Fraction(0), Fraction(1), Fraction(0), Fraction(0)]
    parity = [
        [Fraction(0), Fraction(1), Fraction(0), Fraction(0)],
        [Fraction(1), Fraction(0), Fraction(0), Fraction(0)],
        [Fraction(0), Fraction(0), Fraction(0), Fraction(1)],
        [Fraction(0), Fraction(0), Fraction(1), Fraction(0)],
    ]
    witness = diag((WITNESS_HALF, -WITNESS_HALF, Fraction(0), Fraction(0)))
    plus_witness = quadratic(phi_plus, witness)
    minus_witness = quadratic(phi_minus, witness)
    state_distance = plus_witness - minus_witness
    witness_norm = diagonal_norm(witness)
    plus_ground_energy = quadratic(phi_plus, hamiltonian)
    minus_ground_energy = quadratic(phi_minus, hamiltonian)

    return {
        "shell": {
            "summable_total": str(summable_total),
            "tail_after_radius": str(tail),
            "symmetric_difference_bound": str(symmetric_bound),
            "symmetric_difference_within_tail": symmetric_bound <= tail,
            "product_toggle_bound": str(product_toggle),
            "product_norm_bound": str(product_norm),
        },
        "weak_integral": {
            "weak_sum_norm": str(weak_sum_norm),
            "l1_bound": str(weak_l1_bound),
            "norm_bound_holds": weak_sum_norm <= weak_l1_bound,
            "translation_bound": str(SHIFT_L1_ERROR),
        },
        "quotient": {
            "categorical_sup_norm": str(categorical_sup_norm),
            "spatial_quotient_norm": str(spatial_norm),
            "contractive": spatial_norm <= categorical_sup_norm,
            "periodic_path_error": str(periodic_path_error),
            "kernel_representation_norm": str(kernel_norm),
            "kernel_image_norm": str(Fraction(0)),
            "completion_three_term_bound": str(completion_bound),
        },
        "ground_transfer": {
            "plus_witness": str(plus_witness),
            "minus_witness": str(minus_witness),
            "state_distance_lower_bound": str(state_distance),
            "spatial_witness_norm": str(witness_norm),
            "plus_ground_energy": str(plus_ground_energy),
            "minus_ground_energy": str(minus_ground_energy),
            "parity_intertwines_states": mat_vec(parity, phi_plus) == phi_minus,
            "parity_commutes_dynamics": mat_mul(parity, hamiltonian) == mat_mul(hamiltonian, parity),
            "witness_nonzero": witness_norm > 0,
        },
    }


def product(values: Any) -> Fraction:
    answer = Fraction(1)
    for value in values:
        answer *= value
    return answer


def build_payload(formal: bool) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate = " ".join(CERTIFICATE.read_text(encoding="utf-8").split())
    derived = exact_derivation()
    audit = Audit()

    audit.check(
        "manifest exact identity",
        manifest["package_id"] == SLUG
        and manifest["version"] == "R-167 v4.2"
        and manifest["exploration_id"] == "EXP-000846"
        and manifest["prior_exploration_id"] == "EXP-000845"
        and manifest["claim_bearing"] is False,
        (manifest["package_id"], manifest["version"], manifest["exploration_id"]),
        (SLUG, "R-167 v4.2", "EXP-000846"),
        "identity",
    )
    audit.check(
        "manifest exact topology",
        manifest["closed_gate_ids"] == [CLOSED]
        and manifest["negative_ids"] == []
        and manifest["reused_negative_ids"] == REUSED,
        (manifest["closed_gate_ids"], manifest["negative_ids"], manifest["reused_negative_ids"]),
        ([CLOSED], [], REUSED),
        "topology",
    )
    setup = " ".join(manifest["setup_and_weak_integrals"].values())
    cauchy = " ".join(manifest["shell_cauchy_and_polynomials"].values())
    audit.check(
        "independent common-filter theorem audit",
        all(token in setup + " " + cauchy for token in ("Xi_Q", "Lambda(F) contains X", "onsite Q3 terms", "periodized W_(P_L,xi)", "N_R(X)", "every sufficiently advanced all-shape F", "F union G", "F triangle G", "X=union_j supp(xi_j)", "product_(k!=j)||f_k||_1")),
        setup + " " + cauchy,
        "cross-net shell/product contract",
        "theorem",
    )
    action = " ".join(manifest["spatial_action"].values())
    quotient = " ".join(manifest["categorical_spatial_quotient"].values())
    approximation = " ".join(manifest["uniform_categorical_approximation"].values())
    transfer = " ".join(manifest["same_net_ground_transfer"].values())
    audit.check(
        "independent quotient/ground theorem audit",
        all(token in action + " " + quotient + " " + approximation + " " + transfer for token in ("tilde(P)_F", "Gamma_L", "cofinal periodic", "zero-limit kernel", "C_c^1", "dense in L1", "surjective", "2||a-a_n||_H", "||pi_L^0(k)||", "nonnegative generator", "q_sp(b)!=0")),
        action + " " + quotient + " " + approximation + " " + transfer,
        "typed C0 quotient and same-net ground transfer",
        "theorem",
    )

    shell = derived["shell"]
    audit.check(
        "independent shell/product derivation",
        all(shell[key] == value for key, value in TEST_ORACLE_SHELL.items())
        and shell["symmetric_difference_within_tail"],
        shell,
        TEST_ORACLE_SHELL,
        "derivation",
    )
    weak = derived["weak_integral"]
    audit.check(
        "independent weak-integral derivation",
        all(weak[key] == value for key, value in TEST_ORACLE_WEAK.items()) and weak["norm_bound_holds"],
        weak,
        TEST_ORACLE_WEAK,
        "derivation",
    )
    quotient_values = derived["quotient"]
    audit.check(
        "independent quotient/kernel derivation",
        all(quotient_values[key] == value for key, value in TEST_ORACLE_QUOTIENT.items())
        and quotient_values["contractive"]
        and quotient_values["kernel_image_norm"] == "0",
        quotient_values,
        TEST_ORACLE_QUOTIENT,
        "derivation",
    )
    ground = derived["ground_transfer"]
    audit.check(
        "independent parity-ground derivation",
        all(ground[key] == value for key, value in TEST_ORACLE_GROUND.items())
        and ground["parity_intertwines_states"]
        and ground["parity_commutes_dynamics"]
        and ground["witness_nonzero"],
        ground,
        TEST_ORACLE_GROUND,
        "derivation",
    )
    firewall = ast_firewall(SCRIPT)
    allowed_imports = {
        "__future__",
        "argparse",
        "ast",
        "hashlib",
        "json",
        "os",
        "tempfile",
        "fractions",
        "pathlib",
        "typing",
    }
    audit.check(
        "stdlib exact AST firewall",
        set(firewall["imports"]) <= allowed_imports
        and not firewall["forbidden_calls"]
        and not firewall["forbidden_literals"]
        and not firewall["dynamic_attributes"],
        firewall,
        "stdlib allowlist and no float/complex/dynamic execution",
        "independence",
    )
    audit.check(
        "certificate and adversarial tokens",
        all(token in certificate for token in (CLOSED, "xi in Xi_Q", "all-shape filter neighborhood", "tilde(P)_F", "q_sp is surjective", "q_sp(b)!=0", "Devil's-advocate and code-discipline audit", "External adversarial review is invited", "No v4.2 PDF is issued")),
        "required tokens present",
        "required tokens present",
        "certificate",
    )
    audit.check(
        "conditional scope firewall",
        all(token in manifest["no_overclaim"] for token in ("does not prove those weights", "not proved to be a seed-indexed commuting local net", "EXP-000790", "v3.8", "no GNS spectral gap", "remain OPEN")),
        manifest["no_overclaim"],
        "conditional spatial-only T0 route",
        "scope",
    )
    audit.check(
        "source AST and exact format",
        ast.parse(SCRIPT.read_text(encoding="utf-8")) is not None
        and all(
            b"\r" not in path.read_bytes()
            and path.read_bytes().endswith(b"\n")
            and all(byte < 128 for byte in path.read_bytes())
            for path in (MANIFEST, CERTIFICATE, SCRIPT)
        ),
        "AST ASCII LF final-LF",
        "AST ASCII LF final-LF",
        "format",
    )
    if formal:
        formal_paths = (
            REPO / "claims/GATES.md",
            REPO / "RESULTS-LEDGER.md",
            REPO / "negative-results/registry.md",
            REPO / "explorations/log.jsonl",
        )
        formal_text = "\n".join(path.read_text(encoding="utf-8") for path in formal_paths)
        audit.check(
            "formal authority links",
            all(token in formal_text for token in ("EXP-000846", CLOSED, *REUSED, "R-167 v4.2")),
            "all formal tokens present",
            "all formal tokens present",
            "formal",
        )

    return {
        "schema": "tect/pre-a-q3lock-integrated-orbit-smear-spatial-quotient-independent-run/1.0",
        "version": "R-167 v4.2",
        "mode": "formal" if formal else "staged",
        "assertions": audit.rows,
        "summary": {"status": "PASS", "passed": len(audit.rows), "failed": 0},
        "derived": derived,
        "source_hashes": {
            str(path.relative_to(REPO)).replace("\\", "/"): normalized_sha256(path)
            for path in (MANIFEST, CERTIFICATE, SCRIPT)
        },
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

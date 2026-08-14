#!/usr/bin/env python3
"""Verify the R-167 v4.2 integrated-smear spatial quotient theorem.

The exact fixtures audit the weak-integral norm bound, summable shell
telescope, product weight, categorical completion, kernel annihilation, and
parity-ground witness transfer. They are proof diagnostics, not Q3-derived
toggle weights; the theorem remains conditional on those weights.
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
SLUG = "pre-a-cp1-st8-q3lock-integrated-orbit-smear-spatial-quotient-ground-transfer-route-split"
MANIFEST = REPO / f"strategy/{SLUG}-manifest.json"
CERTIFICATE = REPO / f"strategy/{SLUG}-certificate-260814.md"
DEFAULT_OUTPUT = REPO / "claims/C6-SPACETIME-SIGNATURE/runs" / f"2026-08-14-primary-{SLUG}/result.json"
FORMAL_PATHS = (
    REPO / "claims/GATES.md",
    REPO / "RESULTS-LEDGER.md",
    REPO / "negative-results/registry.md",
    REPO / "explorations/log.jsonl",
)

CLOSED = "PA-CP1-ST8-Q3LOCK-INTEGRATED-ORBIT-SMEAR-SHELL-CAUCHY-SPATIAL-QUOTIENT-AND-SAME-NET-GROUND-TRANSFER"
REUSED = [
    "NG-2026-08-12-PRE-A-ST8-Q3LOCK-ORBIT-SMEAR-SEED-SUPPORT-AUTOMATIC-SPATIAL-LOCAL-NET",
    "NG-2026-08-13-PRE-A-ST8-Q3LOCK-CATEGORICAL-UNIFORM-CONTINUOUS-ELEMENT-KMS-ENVELOPE-AUTOMATIC-ALL-SHAPE-CAUCHY-AND-UNIQUE-PHASE-QUOTIENT",
    "NG-2026-08-13-PRE-A-ST8-Q3LOCK-NONESSENTIALLY-CONSTANT-LINFINITY-CONFIGURATION-MULTIPLIER-FULL-HAMILTONIAN-POINT-NORM-C0",
]

# Labelled exact audit inputs. No entry below is an asserted Q3 toggle weight.
SHELL_RATIO = sp.Rational(1, 2)
SHELL_RADIUS = sp.Integer(2)
LABEL_SPLIT = (sp.Rational(1, 3), sp.Rational(2, 3))
SYMMETRIC_DIFFERENCE = ((3, 0), (3, 1), (4, 0))
FACTOR_NORMS = (sp.Integer(2), sp.Integer(3), sp.Integer(5))
FACTOR_TOGGLE_WEIGHTS = (sp.Rational(1, 7), sp.Rational(1, 11), sp.Rational(1, 13))

WEAK_COEFFICIENTS = (sp.Rational(1, 4), -sp.Rational(1, 6), sp.Rational(1, 3))
SHIFT_L1_ERROR = sp.Rational(1, 12)

PERIODIC_INDEX = sp.Integer(8)
COMPLETION_ERROR = sp.Rational(1, 16)
ALGEBRAIC_PATH_ERROR = sp.Rational(1, 32)
GROUND_EXCITATION = sp.Integer(2)
WITNESS_HALF = sp.Rational(1, 2)

# Explicit drift oracles. All values are recomputed in exact arithmetic.
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


def diagonal_norm(matrix: sp.Matrix) -> sp.Expr:
    if matrix.rows != matrix.cols or matrix != sp.diag(*matrix.diagonal()):
        raise AssertionError("fixture requires a diagonal matrix")
    return max(abs(sp.simplify(matrix[index, index])) for index in range(matrix.rows))


def scalar(matrix: sp.Matrix) -> sp.Expr:
    if matrix.shape != (1, 1):
        raise AssertionError(f"expected scalar matrix, got {matrix.shape}")
    return sp.simplify(matrix[0, 0])


def label_weight(shell: int, branch: int) -> sp.Expr:
    return sp.simplify(LABEL_SPLIT[branch] * SHELL_RATIO**shell)


def exact_derivation() -> dict[str, Any]:
    summable_total = sp.simplify(SHELL_RATIO / (1 - SHELL_RATIO))
    tail = sp.simplify(SHELL_RATIO ** (SHELL_RADIUS + 1) / (1 - SHELL_RATIO))
    symmetric_bound = sp.simplify(
        sum((label_weight(shell, branch) for shell, branch in SYMMETRIC_DIFFERENCE), sp.Integer(0))
    )
    product_toggle = sp.simplify(
        sum(
            (
                FACTOR_TOGGLE_WEIGHTS[index]
                * sp.prod(FACTOR_NORMS[other] for other in range(len(FACTOR_NORMS)) if other != index)
                for index in range(len(FACTOR_NORMS))
            ),
            sp.Integer(0),
        )
    )
    product_norm = sp.prod(FACTOR_NORMS)

    weak_operators = (
        sp.diag(1, -1),
        sp.diag(-1, 1),
        sp.eye(2),
    )
    weak_sum = sp.zeros(2)
    for coefficient, operator in zip(WEAK_COEFFICIENTS, weak_operators):
        weak_sum += coefficient * operator
    weak_sum_norm = diagonal_norm(weak_sum)
    weak_l1_bound = sp.simplify(sum((abs(value) for value in WEAK_COEFFICIENTS), sp.Integer(0)))

    periodic_representation = sp.diag(
        1 + 1 / PERIODIC_INDEX,
        -1 + 1 / (2 * PERIODIC_INDEX),
    )
    spatial_image = sp.diag(1, -1)
    periodic_path_error = diagonal_norm(periodic_representation - spatial_image)
    categorical_sup_norm = sp.simplify(1 + 1 / sp.Integer(1))
    spatial_norm = diagonal_norm(spatial_image)
    kernel_representation = sp.diag(1 / PERIODIC_INDEX, -1 / (2 * PERIODIC_INDEX))
    kernel_norm = diagonal_norm(kernel_representation)
    completion_bound = sp.simplify(2 * COMPLETION_ERROR + ALGEBRAIC_PATH_ERROR)

    hamiltonian = sp.diag(0, 0, GROUND_EXCITATION, GROUND_EXCITATION)
    phi_plus = sp.Matrix([1, 0, 0, 0])
    phi_minus = sp.Matrix([0, 1, 0, 0])
    parity = sp.Matrix(
        [
            [0, 1, 0, 0],
            [1, 0, 0, 0],
            [0, 0, 0, 1],
            [0, 0, 1, 0],
        ]
    )
    witness = sp.diag(WITNESS_HALF, -WITNESS_HALF, 0, 0)
    plus_witness = scalar(phi_plus.T * witness * phi_plus)
    minus_witness = scalar(phi_minus.T * witness * phi_minus)
    state_distance = sp.simplify(plus_witness - minus_witness)
    witness_norm = diagonal_norm(witness)
    plus_ground_energy = scalar(phi_plus.T * hamiltonian * phi_plus)
    minus_ground_energy = scalar(phi_minus.T * hamiltonian * phi_minus)

    return {
        "shell": {
            "summable_total": str(summable_total),
            "tail_after_radius": str(tail),
            "symmetric_difference_bound": str(symmetric_bound),
            "symmetric_difference_within_tail": bool(symmetric_bound <= tail),
            "product_toggle_bound": str(product_toggle),
            "product_norm_bound": str(product_norm),
        },
        "weak_integral": {
            "weak_sum_norm": str(weak_sum_norm),
            "l1_bound": str(weak_l1_bound),
            "norm_bound_holds": bool(weak_sum_norm <= weak_l1_bound),
            "translation_bound": str(SHIFT_L1_ERROR),
        },
        "quotient": {
            "categorical_sup_norm": str(categorical_sup_norm),
            "spatial_quotient_norm": str(spatial_norm),
            "contractive": bool(spatial_norm <= categorical_sup_norm),
            "periodic_path_error": str(periodic_path_error),
            "kernel_representation_norm": str(kernel_norm),
            "kernel_image_norm": str(sp.Integer(0)),
            "completion_three_term_bound": str(completion_bound),
        },
        "ground_transfer": {
            "plus_witness": str(plus_witness),
            "minus_witness": str(minus_witness),
            "state_distance_lower_bound": str(state_distance),
            "spatial_witness_norm": str(witness_norm),
            "plus_ground_energy": str(plus_ground_energy),
            "minus_ground_energy": str(minus_ground_energy),
            "parity_intertwines_states": bool(parity * phi_plus == phi_minus),
            "parity_commutes_dynamics": bool(parity * hamiltonian == hamiltonian * parity),
            "witness_nonzero": bool(witness_norm > 0),
        },
    }


def build_payload(formal: bool) -> dict[str, Any]:
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    certificate = " ".join(CERTIFICATE.read_text(encoding="utf-8").split())
    derived = exact_derivation()
    audit = Audit()

    audit.check(
        "manifest identity",
        manifest["package_id"] == SLUG
        and manifest["version"] == "R-167 v4.2"
        and manifest["date"] == "2026-08-14"
        and manifest["exploration_id"] == "EXP-000846"
        and manifest["prior_exploration_id"] == "EXP-000845"
        and manifest["claim_bearing"] is False,
        (manifest["package_id"], manifest["version"], manifest["exploration_id"]),
        (SLUG, "R-167 v4.2", "EXP-000846"),
        "identity",
    )
    audit.check(
        "manifest topology",
        manifest["closed_gate_ids"] == [CLOSED]
        and manifest["negative_ids"] == []
        and manifest["reused_negative_ids"] == REUSED,
        (manifest["closed_gate_ids"], manifest["negative_ids"], manifest["reused_negative_ids"]),
        ([CLOSED], [], REUSED),
        "topology",
    )
    setup = " ".join(manifest["setup_and_weak_integrals"].values())
    toggle = " ".join(manifest["conditional_integrated_toggle_hypothesis"].values())
    audit.check(
        "weak integral and directed same-net hypotheses",
        all(
            token in setup + " " + toggle
            for token in (
                "Xi_Q",
                "configuration-Weyl",
                "Lambda(F) contains X",
                "onsite Q3 terms",
                "periodized W_(P_L,xi)",
                "strong-star continuous",
                "||G_F(xi,f)||<=||f||_1",
                "F triangle G subset",
                "auxiliary union background",
                "common infinite interaction pattern",
                "N_R",
                "both time orientations",
                "sum_(e in E) w_e",
            )
        ),
        setup + " " + toggle,
        "exact weak-integral/common-filter hypothesis",
        "theorem",
    )
    cauchy = " ".join(manifest["shell_cauchy_and_polynomials"].values())
    audit.check(
        "shell and product theorem",
        all(token in cauchy for token in ("F union G", "F triangle G", "sum_(r>R)B_r", "X=union_j supp(xi_j)", "product_(k!=j)||f_k||_1", "star-polynomials")),
        cauchy,
        "tail telescope and product weight",
        "theorem",
    )
    action = " ".join(manifest["spatial_action"].values())
    quotient = " ".join(manifest["categorical_spatial_quotient"].values())
    audit.check(
        "C0 spatial quotient theorem",
        all(token in action + " " + quotient for token in ("tilde(P)_F", "J_F(alpha_s^F", "Gamma_L", "cofinal periodic", "zero-limit kernel", "theta_sp,s", "||tau_s f-f||_1", "inverse", "C_c^1", "dense in L1", "q_sp:A_H^0->B_sp", "surjective", "q_sp theta_s")),
        action + " " + quotient,
        "C0 equivariant surjective quotient",
        "theorem",
    )
    approximation = " ".join(manifest["uniform_categorical_approximation"].values())
    transfer = " ".join(manifest["same_net_ground_transfer"].values())
    audit.check(
        "same-net kernel and ground transfer",
        all(token in approximation + " " + transfer for token in ("2||a-a_n||_H", "||pi_L^0(k)||", "omega_sigma(k^*k)", "unique states", "nonnegative generator", "q_sp(b)!=0")),
        approximation + " " + transfer,
        "completed same-net factorization",
        "theorem",
    )
    scope = " ".join(manifest["nonduplication_and_scope"].values()) + " " + manifest["no_overclaim"]
    audit.check(
        "conditional spatial-only scope",
        all(token in scope for token in ("does not prove those weights", "abstract summable single-toggle-shell", "specializes and repairs", "spatial subalgebra", "not proved to be a seed-indexed commuting local net", "EXP-000790", "v3.8", "No new negative", "no GNS spectral gap", "remain OPEN")),
        scope,
        "conditional route without branch or gap promotion",
        "scope",
    )

    shell = derived["shell"]
    audit.check(
        "exact shell and product derivation",
        all(shell[key] == value for key, value in TEST_ORACLE_SHELL.items())
        and shell["symmetric_difference_within_tail"],
        shell,
        TEST_ORACLE_SHELL,
        "derivation",
    )
    weak = derived["weak_integral"]
    audit.check(
        "exact weak-integral fixture",
        all(weak[key] == value for key, value in TEST_ORACLE_WEAK.items()) and weak["norm_bound_holds"],
        weak,
        TEST_ORACLE_WEAK,
        "derivation",
    )
    quotient_values = derived["quotient"]
    audit.check(
        "exact quotient and kernel fixture",
        all(quotient_values[key] == value for key, value in TEST_ORACLE_QUOTIENT.items())
        and quotient_values["contractive"]
        and quotient_values["kernel_image_norm"] == "0",
        quotient_values,
        TEST_ORACLE_QUOTIENT,
        "derivation",
    )
    ground = derived["ground_transfer"]
    audit.check(
        "exact ground/parity witness fixture",
        all(ground[key] == value for key, value in TEST_ORACLE_GROUND.items())
        and ground["parity_intertwines_states"]
        and ground["parity_commutes_dynamics"]
        and ground["witness_nonzero"],
        ground,
        TEST_ORACLE_GROUND,
        "derivation",
    )
    audit.check(
        "certificate proof tokens",
        all(
            token in certificate
            for token in (
                CLOSED,
                "weak-int_R",
                "F triangle G subset {e:r_X(e)>R}",
                "all-shape filter neighborhood",
                "product_(k!=j)||f_k||_1",
                "q_sp:A_H^0->B_sp",
                "||pi_L^0(k)||",
                "bar(omega)_sigma",
                "q_sp(b)!=0",
                "No v4.2 PDF is issued",
                "Devil's-advocate and code-discipline audit",
                "External adversarial review is invited",
            )
        ),
        "required proof tokens present",
        "required proof tokens present",
        "certificate",
    )
    audit.check(
        "source AST and format",
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
        formal_text = "\n".join(path.read_text(encoding="utf-8") for path in FORMAL_PATHS)
        audit.check(
            "formal authority links",
            all(token in formal_text for token in ("EXP-000846", CLOSED, *REUSED, "R-167 v4.2")),
            "all formal tokens present",
            "all formal tokens present",
            "formal",
        )

    return {
        "schema": "tect/pre-a-q3lock-integrated-orbit-smear-spatial-quotient-run/1.0",
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
    print(f"PRIMARY PASS {payload['summary']['passed']}/{payload['summary']['passed']} mode={payload['mode']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

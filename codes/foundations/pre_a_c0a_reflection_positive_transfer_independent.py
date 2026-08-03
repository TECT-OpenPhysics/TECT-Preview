#!/usr/bin/env python3
"""Non-importing rational audit for PA-C0A-RPTM-FS-v0."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
from fractions import Fraction as F
from pathlib import Path
from typing import Any


__version__ = "0.1.0"
REPO = Path(__file__).resolve().parents[2]
CANDIDATE_ID = "PA-C0A-RPTM-FS-v0"
SLUG = "pre-a-c0a-reflection-positive-transfer"
SCHEMA = f"tect/{SLUG}-independent/0.1"
CLAIM_CONTEXT = "C6-SPACETIME-SIGNATURE"
DEFAULT_OUTPUT = (
    REPO
    / "claims"
    / CLAIM_CONTEXT
    / "runs"
    / f"2026-08-03-independent-{SLUG}"
    / "result.json"
)

Matrix = list[list[F]]


def encode(value: Any) -> Any:
    if isinstance(value, Path):
        return str(value).replace("\\", "/")
    if isinstance(value, F):
        return str(value)
    if isinstance(value, dict):
        return {str(key): encode(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [encode(item) for item in value]
    return value


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(
        prefix=path.name + ".", suffix=".tmp", dir=path.parent
    )
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            json.dump(encode(payload), stream, indent=2, sort_keys=True, ensure_ascii=True)
            stream.write("\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def zeros(rows: int, cols: int) -> Matrix:
    return [[F(0) for _ in range(cols)] for _ in range(rows)]


def identity(size: int) -> Matrix:
    return [[F(int(row == col)) for col in range(size)] for row in range(size)]


def transpose(matrix: Matrix) -> Matrix:
    return [list(row) for row in zip(*matrix)]


def add(left: Matrix, right: Matrix) -> Matrix:
    return [
        [left[row][col] + right[row][col] for col in range(len(left[0]))]
        for row in range(len(left))
    ]


def scale(matrix: Matrix, scalar: F) -> Matrix:
    return [[scalar * value for value in row] for row in matrix]


def multiply(left: Matrix, right: Matrix) -> Matrix:
    return [
        [
            sum(left[row][index] * right[index][col] for index in range(len(right)))
            for col in range(len(right[0]))
        ]
        for row in range(len(left))
    ]


def diagonal(values: list[F]) -> Matrix:
    return [
        [values[row] if row == col else F(0) for col in range(len(values))]
        for row in range(len(values))
    ]


def projector(pi: list[F]) -> Matrix:
    return [list(pi) for _ in pi]


def transfer(pi: list[F], alpha: F) -> Matrix:
    size = len(pi)
    return add(scale(identity(size), alpha), scale(projector(pi), 1 - alpha))


def determinant_2(matrix: Matrix) -> F:
    if len(matrix) != 2 or len(matrix[0]) != 2:
        raise ValueError("determinant_2 requires a 2x2 matrix")
    return matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]


def quadratic(vector: list[F], matrix: Matrix) -> F:
    column = [[value] for value in vector]
    return multiply([vector], multiply(matrix, column))[0][0]


def derive() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []

    def check(name: str, condition: bool, actual: Any, expected: Any, group: str) -> None:
        if not condition:
            raise AssertionError(f"{name}: actual={actual!r}, expected={expected!r}")
        rows.append(
            {
                "name": name,
                "status": "PASS",
                "actual": encode(actual),
                "expected": encode(expected),
                "group": group,
            }
        )

    pi = [F(1, 2), F(1, 3), F(1, 6)]
    size = len(pi)
    eye = identity(size)
    pi_projector = projector(pi)
    complement = add(eye, scale(pi_projector, F(-1)))
    weight = diagonal(pi)
    alpha = F(2, 3)
    matrix = transfer(pi, alpha)
    ones = [[F(1)] for _ in range(size)]
    pi_column = [[value] for value in pi]

    check(
        "independent probability normalization",
        sum(pi) == 1 and all(value > 0 for value in pi),
        (sum(pi), pi),
        "positive normalized probability",
        "transfer",
    )
    check(
        "independent stationary projector identity",
        multiply(pi_projector, pi_projector) == pi_projector,
        multiply(pi_projector, pi_projector),
        pi_projector,
        "transfer",
    )
    check(
        "independent complementary projector identity",
        multiply(complement, complement) == complement
        and multiply(pi_projector, complement) == zeros(size, size)
        and multiply(complement, pi_projector) == zeros(size, size),
        (
            multiply(complement, complement),
            multiply(pi_projector, complement),
            multiply(complement, pi_projector),
        ),
        (complement, zeros(size, size), zeros(size, size)),
        "transfer",
    )
    check(
        "independent stochastic transfer",
        multiply(matrix, ones) == ones and min(min(row) for row in matrix) >= 0,
        (multiply(matrix, ones), min(min(row) for row in matrix)),
        (ones, ">=0"),
        "transfer",
    )

    # Converse boundary: spectral/operator positivity does not imply
    # entrywise nonnegativity, hence it does not by itself define a Markov
    # transition kernel.
    contrast = [[F(1)], [F(1)], [F(-2)]]
    positive_non_markov = add(
        identity(size),
        scale(multiply(contrast, transpose(contrast)), F(-1, 10)),
    )
    check(
        "independent operator-positive control is not entrywise Markov",
        multiply(positive_non_markov, ones) == ones
        and multiply(positive_non_markov, [[F(1)], [F(-1)], [F(0)]])
        == [[F(1)], [F(-1)], [F(0)]]
        and multiply(positive_non_markov, contrast) == scale(contrast, F(2, 5))
        and min(min(row) for row in positive_non_markov) == F(-1, 10),
        (
            multiply(positive_non_markov, ones),
            multiply(positive_non_markov, contrast),
            min(min(row) for row in positive_non_markov),
        ),
        (ones, scale(contrast, F(2, 5)), F(-1, 10)),
        "transfer_boundary",
    )
    check(
        "independent detailed balance",
        multiply(weight, matrix) == multiply(transpose(matrix), weight),
        multiply(weight, matrix),
        multiply(transpose(matrix), weight),
        "transfer",
    )
    check(
        "independent stationary probability",
        multiply(transpose(matrix), pi_column) == pi_column,
        multiply(transpose(matrix), pi_column),
        pi_column,
        "transfer",
    )

    # The exact minimal polynomial pins the spectrum {1,alpha,alpha} without
    # using an eigensolver.
    matrix_minus_one = add(matrix, scale(eye, F(-1)))
    matrix_minus_alpha = add(matrix, scale(eye, -alpha))
    minimal_product = multiply(matrix_minus_one, matrix_minus_alpha)
    check(
        "independent transfer minimal polynomial",
        minimal_product == zeros(size, size),
        minimal_product,
        zeros(size, size),
        "transfer",
    )
    check(
        "independent complement is a doubly degenerate alpha eigenspace",
        multiply(matrix, complement) == scale(complement, alpha),
        multiply(matrix, complement),
        scale(complement, alpha),
        "transfer",
    )

    # D(I-Pi) is exactly the pair-difference variance matrix.
    variance_matrix = multiply(weight, complement)
    pair_matrix = zeros(size, size)
    for left in range(size):
        for right in range(left + 1, size):
            pair_weight = pi[left] * pi[right]
            pair_matrix[left][left] += pair_weight
            pair_matrix[right][right] += pair_weight
            pair_matrix[left][right] -= pair_weight
            pair_matrix[right][left] -= pair_weight
    check(
        "independent weighted generator form is the pair variance",
        variance_matrix == pair_matrix,
        variance_matrix,
        pair_matrix,
        "generator",
    )
    complement_minor = [row[:2] for row in complement[:2]]
    check(
        "independent complement kernel is exactly span of constants",
        multiply(complement, ones) == zeros(size, 1)
        and determinant_2(complement_minor) != 0,
        (multiply(complement, ones), determinant_2(complement_minor)),
        (zeros(size, 1), "nonzero rank-two minor"),
        "generator",
    )

    # The projector functional calculus is exact: any scalar function maps P
    # to f(1)Pi+f(alpha)(I-Pi).  These algebraic identities underwrite log and
    # exponential reconstruction without importing transcendental software.
    check(
        "independent transfer spectral decomposition",
        matrix == add(pi_projector, scale(complement, alpha)),
        matrix,
        add(pi_projector, scale(complement, alpha)),
        "generator",
    )
    check(
        "independent unitary projector algebra",
        multiply(pi_projector, complement) == zeros(size, size)
        and add(pi_projector, complement) == eye,
        (multiply(pi_projector, complement), add(pi_projector, complement)),
        (zeros(size, size), eye),
        "generator",
    )

    alpha_alt = F(1, 2)
    matrix_alt = transfer(pi, alpha_alt)
    check(
        "independent same static marginal has distinct positive transfers",
        matrix_alt != matrix
        and multiply(transpose(matrix_alt), pi_column) == pi_column
        and min(min(row) for row in matrix_alt) >= 0,
        (matrix_alt != matrix, multiply(transpose(matrix_alt), pi_column)),
        (True, pi_column),
        "static_boundary",
    )

    tests: Matrix = [
        [F(1), F(0)],
        [F(2), F(3)],
        [F(-1), F(2)],
    ]
    site_gram = multiply(transpose(tests), multiply(weight, tests))
    link_gram = multiply(transpose(tests), multiply(weight, multiply(matrix, tests)))
    check(
        "independent site-reflection Gram fixture",
        site_gram[0][0] > 0 and determinant_2(site_gram) > 0,
        (site_gram[0][0], determinant_2(site_gram)),
        "positive leading principal minors",
        "reflection_positivity",
    )
    check(
        "independent link-reflection Gram fixture",
        link_gram[0][0] > 0 and determinant_2(link_gram) > 0,
        (link_gram[0][0], determinant_2(link_gram)),
        "positive leading principal minors",
        "reflection_positivity",
    )

    alpha_bad = F(-1, 10)
    bad = transfer(pi, alpha_bad)
    bad_minimal = multiply(
        add(bad, scale(eye, F(-1))), add(bad, scale(eye, -alpha_bad))
    )
    zero_mean = [F(1), F(-3, 2), F(0)]
    zero_mean_value = sum(pi[index] * zero_mean[index] for index in range(size))
    bad_link_form = quadratic(zero_mean, multiply(weight, bad))
    zero_transfer = projector(pi)
    zero_link_form = quadratic(zero_mean, multiply(weight, zero_transfer))
    check(
        "independent zero-spectrum control is Markov and link-positive",
        multiply(zero_transfer, ones) == ones
        and min(min(row) for row in zero_transfer) >= 0
        and multiply(weight, zero_transfer)
        == multiply(transpose(zero_transfer), weight)
        and multiply(zero_transfer, complement) == zeros(size, size)
        and zero_link_form == 0,
        (
            multiply(zero_transfer, ones),
            multiply(zero_transfer, complement),
            zero_link_form,
        ),
        (ones, zeros(size, size), F(0)),
        "zero_spectrum_boundary",
    )
    check(
        "independent negative control remains stochastic and reversible",
        multiply(bad, ones) == ones
        and min(min(row) for row in bad) >= 0
        and multiply(weight, bad) == multiply(transpose(bad), weight),
        (multiply(bad, ones), min(min(row) for row in bad)),
        (ones, ">=0"),
        "negative_control",
    )
    check(
        "independent negative control has the pinned minimal polynomial",
        bad_minimal == zeros(size, size)
        and multiply(bad, complement) == scale(complement, alpha_bad),
        (bad_minimal, multiply(bad, complement)),
        (zeros(size, size), scale(complement, alpha_bad)),
        "negative_control",
    )
    check(
        "independent negative control violates link positivity",
        zero_mean_value == 0 and bad_link_form < 0,
        (zero_mean_value, bad_link_form),
        (F(0), "<0"),
        "negative_control",
    )

    source = Path(__file__).resolve()
    return {
        "schema": SCHEMA,
        "candidate_id": CANDIDATE_ID,
        "version": __version__,
        "issued": "2026-08-03",
        "authority": "independent rational audit of a T0 C0-A transfer benchmark",
        "shared_exact_results": {
            "probability": pi,
            "alpha": alpha,
            "positive_transfer_spectrum": [F(1), alpha, alpha],
            "positive_weighted_self_adjoint_transfer": True,
            "projector_log_generator": True,
            "one_dimensional_constant_ground_space": True,
            "site_reflection_positive_fixture": True,
            "link_reflection_positive_fixture": True,
            "same_static_marginal_distinct_positive_transfer": True,
            "negative_control_alpha": alpha_bad,
            "negative_control_link_form": bad_link_form,
            "zero_spectrum_markov_link_positive_boundary": True,
            "operator_positive_non_markov_boundary": True,
            "pre_a_complete": False,
        },
        "scope": {
            "c0_a_temporal_transfer_benchmark_instantiated": True,
            "c0_a_causal_structure_instantiated": False,
            "time_order_and_spacing_inserted": True,
            "markov_entrywise_nonnegative_input": True,
            "static_functional_selects_transfer": False,
            "positive_self_adjoint_generator_reconstructed": True,
            "unitary_group_reconstructed": True,
            "site_reflection_positive": True,
            "link_reflection_requires_positive_transfer": True,
            "reversibility_alone_implies_positive_generator": False,
            "spatial_locality_derived": False,
            "causal_cone_derived": False,
            "lorentzian_signature_derived": False,
            "physical_quantum_dynamics_selected": False,
            "preferred_hadamard_state_selected": False,
            "pa_h1_state_supplied": False,
            "pa_m2_composition": False,
            "tect_c0_branch_selected": False,
            "pre_a_complete": False,
        },
        "assertions": {"passed": len(rows), "total": len(rows), "rows": rows},
        "source": {"path": source.relative_to(REPO), "sha256": sha256(source)},
        "no_overclaim": (
            "This non-importing audit certifies exact rational projector, transfer, variance, reflection-Gram, "
            "and negative-control identities. It does not derive time, locality, a causal cone, Lorentzian "
            "signature, a physical quantum theory, a PA-H1 state, a PA-M2 composition, or Pre-A completion."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--self-test", action="store_true")
    arguments = parser.parse_args()
    payload = derive()
    if not arguments.self_test:
        atomic_json(arguments.output, payload)
    print(
        f"PASS {payload['assertions']['passed']}/{payload['assertions']['total']} | "
        f"independent {CANDIDATE_ID}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
